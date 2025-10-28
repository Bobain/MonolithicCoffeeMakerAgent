# SPEC-102: Project Manager Commands

**Status**: Draft
**Created**: 2025-10-26
**Author**: architect
**Parent Spec**: SPEC-100
**Related Specs**: SPEC-101 (Foundation Infrastructure)
**Related CFRs**: CFR-007 (Context Budget), CFR-009 (Sound Notifications), CFR-015 (Centralized Database)
**Dependencies**: SPEC-101 (Foundation)

## Executive Summary

Implement 14 commands for the project_manager agent, covering roadmap parsing, inter-agent communication, GitHub monitoring, and verification workflows. These commands enforce the project_manager's exclusive write access to the `roadmap` schema while enabling comprehensive project oversight.

### Key Objectives

1. **Roadmap Management** - Parse and sync ROADMAP.md to database (4 commands)
2. **Inter-Agent Communication** - Create and process notifications (3 commands)
3. **Project Monitoring** - GitHub PRs/issues, health analysis (4 commands)
4. **Verification** - DoD validation, strategic planning, reporting (3 commands)

### Design Principles

- **Database-First**: ALL operations use database, NEVER read ROADMAP.md directly (CFR-015)
- **Exclusive Write Access**: ONLY project_manager writes to `roadmap_*` tables
- **Notification-Driven**: Other agents request changes via notifications
- **Audit Trail**: Every operation logged to `system_audit`

---

## Architecture Overview

### Command Groups

```
Project Manager (14 commands)
├── Roadmap Parsing (4 commands)
│   ├── parse_roadmap         - Parse ROADMAP.md → database
│   ├── update_priority_status - Change priority status
│   ├── update_metadata       - Update ROADMAP header/footer
│   └── create_roadmap_audit  - Manual audit log entry
│
├── Communication (3 commands)
│   ├── create_notification   - Send notification to agent
│   ├── process_notifications - Handle incoming notifications
│   └── send_agent_notification - Agent-specific message
│
├── Monitoring (4 commands)
│   ├── monitor_github_prs    - Check PR status
│   ├── monitor_github_issues - Check issue status
│   ├── analyze_project_health - Generate health report
│   └── detect_stale_priorities - Find stuck work
│
└── Verification (3 commands)
    ├── verify_dod_puppeteer  - DoD verification with browser
    ├── strategic_planning    - Plan next priorities
    └── create_roadmap_report - Generate status report
```

### Database Domain

**Tables Owned (Write Access)**:
- `roadmap_priority` - Priorities and user stories
- `roadmap_metadata` - ROADMAP header/footer
- `roadmap_audit` - Audit trail for roadmap changes
- `roadmap_notification` - Notification queue

**Tables Read**:
- `specs_specification` - Technical specs (architect's domain)
- `review_code_review` - Code reviews (code_reviewer's domain)
- `agent_lifecycle` - Agent status (orchestrator's domain)
- `notifications` - Shared notification system

---

## Command Group 1: Roadmap Parsing (4 Commands)

### Command: project_manager.parse_roadmap

**Purpose**: Parse ROADMAP.md file and sync all priorities to database

**Tables**:
- Write: `roadmap_priority`, `roadmap_audit`
- Read: `roadmap_priority` (for diff detection)

**Files**:
- Read: `docs/roadmap/ROADMAP.md`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
roadmap_file: string     # Path to ROADMAP.md (default: "docs/roadmap/ROADMAP.md")
force_sync: boolean      # Force full resync (default: false)
dry_run: boolean         # Preview changes without writing (default: false)
```

**Output**:
```json
{
  "success": true,
  "priorities_added": 3,
  "priorities_updated": 5,
  "priorities_removed": 1,
  "spec_notifications_sent": 2,
  "audit_entries_created": 9
}
```

**Success Criteria**:
- ✅ All priorities from ROADMAP.md synced to database
- ✅ Diff detection identifies changes (added/updated/removed)
- ✅ Audit trail created for all changes
- ✅ Notifications sent for priorities needing specs
- ✅ Priority order preserved

**Database Operations**:

```python
# Implementation pattern
def parse_roadmap(db: DomainWrapper, params: dict):
    # Read file
    with open(params["roadmap_file"]) as f:
        content = f.read()

    # Parse priorities from markdown
    priorities = parse_markdown_priorities(content)

    # Get current database state
    current_items = db.read("roadmap_priority")
    current_ids = {item["id"] for item in current_items}

    # Identify changes
    new_ids = {p["id"] for p in priorities}
    added = new_ids - current_ids
    removed = current_ids - new_ids
    updated = new_ids & current_ids

    # Apply changes
    for priority in priorities:
        if priority["id"] in added:
            db.write("roadmap_priority", priority, action="create")
        elif priority["id"] in updated:
            # Only update if fields changed
            current = next(i for i in current_items if i["id"] == priority["id"])
            if has_changes(current, priority):
                db.write("roadmap_priority", priority, action="update")

    # Send notifications for specs needed
    for priority in priorities:
        if priority["status"] == "📝 Planned" and not priority.get("spec_id"):
            db.send_notification("architect", {
                "type": "spec_needed",
                "priority_id": priority["id"],
                "title": priority["title"]
            })

    return {
        "success": True,
        "priorities_added": len(added),
        "priorities_updated": len([p for p in priorities if p["id"] in updated]),
        "priorities_removed": len(removed)
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| FileNotFoundError | ROADMAP.md missing | Check file path, create template |
| ParseError | Malformed markdown | Fix markdown syntax, validate format |
| DuplicateIDError | Multiple priorities with same ID | Consolidate duplicates, update IDs |
| PermissionError | Cannot write to database | Verify agent is project_manager |

**Downstream Effects**:
- Notifications sent to architect for priorities needing specs
- orchestrator detects new work available
- Dashboard UI shows updated priorities
- Audit trail enables rollback if needed

---

### Command: project_manager.update_priority_status

**Purpose**: Update the status of a priority (e.g., Planned → In Progress → Complete)

**Tables**:
- Write: `roadmap_priority`, `roadmap_audit`
- Read: `roadmap_priority`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
priority_id: string      # Required - Priority identifier (e.g., "PRIORITY-25")
new_status: string       # Required - New status value ("📝 Planned", "🏗️ In Progress", "✅ Complete")
reason: string           # Optional - Reason for status change
verify_dod: boolean      # Optional - Run DoD verification before marking complete (default: true)
```

**Output**:
```json
{
  "success": true,
  "priority_id": "PRIORITY-25",
  "old_status": "🏗️ In Progress",
  "new_status": "✅ Complete",
  "dod_verified": true,
  "audit_entry_id": "audit-12345"
}
```

**Success Criteria**:
- ✅ Status updated in database
- ✅ Audit trail created with old/new values
- ✅ DoD verification passed (if marking complete)
- ✅ Notifications sent to relevant agents

**Database Operations**:

```python
def update_priority_status(db: DomainWrapper, params: dict):
    # Get current priority
    items = db.read("roadmap_priority", {"id": params["priority_id"]})
    if not items:
        raise ValueError(f"Priority {params['priority_id']} not found")

    current = items[0]
    old_status = current["status"]
    new_status = params["new_status"]

    # Verify DoD if marking complete
    if new_status == "✅ Complete" and params.get("verify_dod", True):
        dod_result = verify_dod(params["priority_id"])
        if not dod_result["passed"]:
            return {
                "success": False,
                "error": "DoD verification failed",
                "dod_result": dod_result
            }

    # Update status
    db.write("roadmap_priority", {
        "id": params["priority_id"],
        "status": new_status,
        "completed_at": datetime.now().isoformat() if new_status == "✅ Complete" else None
    }, action="update")

    # Send notifications based on status change
    if new_status == "✅ Complete":
        # Notify orchestrator to plan next work
        db.send_notification("orchestrator", {
            "type": "priority_complete",
            "priority_id": params["priority_id"]
        })

    return {
        "success": True,
        "priority_id": params["priority_id"],
        "old_status": old_status,
        "new_status": new_status
    }
```

**Valid Status Transitions**:

```
📝 Planned → 🏗️ In Progress → ✅ Complete
     ↓            ↓                ↓
    ❌ Rejected  🔴 Blocked      🔄 Reopened
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| NotFoundError | Priority doesn't exist | Verify priority ID |
| InvalidTransitionError | Invalid status change | Check valid transitions |
| DoDFailedError | DoD verification failed | Fix implementation, re-verify |
| PermissionError | Not project_manager | Only project_manager can update status |

**Downstream Effects**:
- orchestrator detects work completion, plans next task
- Dashboard UI shows updated status
- Metrics updated (velocity, completion rate)
- Audit trail enables status history

---

### Command: project_manager.update_metadata

**Purpose**: Update ROADMAP.md header/footer metadata (project description, goals, metrics)

**Tables**:
- Write: `roadmap_metadata`, `roadmap_audit`
- Read: `roadmap_metadata`

**Required Skills**: None

**Input Parameters**:
```yaml
metadata_type: string    # "header" or "footer"
content: string          # New content for section
section: string          # Specific section to update (optional)
```

**Output**:
```json
{
  "success": true,
  "metadata_type": "header",
  "updated_at": "2025-10-26T10:30:00Z",
  "audit_entry_id": "audit-12346"
}
```

**Success Criteria**:
- ✅ Metadata updated in database
- ✅ Audit trail created
- ✅ File export triggered (if configured)

**Database Operations**:

```python
def update_metadata(db: DomainWrapper, params: dict):
    # Update metadata in database
    metadata_id = f"{params['metadata_type']}_metadata"

    db.write("roadmap_metadata", {
        "id": metadata_id,
        "type": params["metadata_type"],
        "content": params["content"],
        "section": params.get("section"),
        "updated_at": datetime.now().isoformat()
    }, action="update")

    return {
        "success": True,
        "metadata_type": params["metadata_type"]
    }
```

---

### Command: project_manager.create_roadmap_audit

**Purpose**: Manually create an audit log entry for roadmap changes (for external modifications)

**Tables**:
- Write: `roadmap_audit`

**Required Skills**: None

**Input Parameters**:
```yaml
priority_id: string      # Priority affected
action: string           # "create", "update", "delete", "status_change"
description: string      # Human-readable description
old_value: string        # Optional - Previous value
new_value: string        # Optional - New value
```

**Output**:
```json
{
  "success": true,
  "audit_entry_id": "audit-12347",
  "created_at": "2025-10-26T10:35:00Z"
}
```

**Success Criteria**:
- ✅ Audit entry created
- ✅ Timestamp recorded
- ✅ agent_name set to "project_manager"

---

## Command Group 2: Communication (3 Commands)

### Command: project_manager.create_notification

**Purpose**: Send a notification to another agent

**Tables**:
- Write: `notifications`

**Required Skills**: None

**Input Parameters**:
```yaml
target_agent: string     # Agent to notify ("architect", "code_developer", etc.)
notification_type: string # Type of notification
item_id: string          # Optional - Related item ID
message: string          # Notification message
priority: string         # "low", "medium", "high", "urgent"
sound: boolean           # Play sound (MUST be false per CFR-009)
```

**Output**:
```json
{
  "success": true,
  "notification_id": "notif-12348",
  "target_agent": "architect",
  "created_at": "2025-10-26T10:40:00Z"
}
```

**Success Criteria**:
- ✅ Notification created in database
- ✅ CFR-009 enforced (sound=false for background agents)
- ✅ Target agent specified
- ✅ Priority level set

**Database Operations**:

```python
def create_notification(db: DomainWrapper, params: dict):
    # CFR-009: Enforce silent notifications for background agents
    if params.get("sound", False):
        raise ValueError("CFR-009 violation: project_manager cannot use sound=True")

    notification_data = {
        "target_agent": params["target_agent"],
        "source_agent": "project_manager",
        "notification_type": params["notification_type"],
        "item_id": params.get("item_id"),
        "message": params["message"],
        "priority": params.get("priority", "medium"),
        "status": "pending",
        "sound": False,  # CFR-009
        "created_at": datetime.now().isoformat()
    }

    notification_id = db.write("notifications", notification_data, action="create")

    return {
        "success": True,
        "notification_id": notification_id,
        "target_agent": params["target_agent"]
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| CFR009ViolationError | sound=True | Use sound=False |
| InvalidAgentError | Unknown target agent | Check agent name |
| ValidationError | Missing required fields | Provide all required params |

---

### Command: project_manager.process_notifications

**Purpose**: Process incoming notifications from other agents (status change requests, etc.)

**Tables**:
- Read: `notifications`
- Write: `notifications`, `roadmap_priority`, `roadmap_audit`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
batch_size: integer      # Number of notifications to process (default: 10)
auto_approve: boolean    # Auto-approve safe changes (default: false)
```

**Output**:
```json
{
  "success": true,
  "processed": 3,
  "approved": 2,
  "rejected": 1,
  "notifications": [
    {
      "notification_id": "notif-123",
      "action": "approved",
      "reason": "DoD verified"
    }
  ]
}
```

**Success Criteria**:
- ✅ Pending notifications retrieved
- ✅ Each notification reviewed
- ✅ Status change applied if approved
- ✅ Rejection reason recorded if rejected

**Database Operations**:

```python
def process_notifications(db: DomainWrapper, params: dict):
    # Get pending notifications for project_manager
    notifications = db.read("notifications", {
        "target_agent": "project_manager",
        "status": "pending"
    })

    batch_size = params.get("batch_size", 10)
    auto_approve = params.get("auto_approve", False)

    results = []
    for notif in notifications[:batch_size]:
        # Review notification
        if notif["notification_type"] == "status_change_request":
            # Check if DoD verified
            dod_verified = check_dod_status(notif["item_id"])

            if dod_verified or auto_approve:
                # Approve and apply change
                db.write("roadmap_priority", {
                    "id": notif["item_id"],
                    "status": notif["requested_status"]
                }, action="update")

                # Mark notification as processed
                db.write("notifications", {
                    "id": notif["id"],
                    "status": "approved"
                }, action="update")

                results.append({
                    "notification_id": notif["id"],
                    "action": "approved"
                })
            else:
                # Reject (needs DoD verification)
                db.write("notifications", {
                    "id": notif["id"],
                    "status": "rejected",
                    "rejection_reason": "DoD verification required"
                }, action="update")

                results.append({
                    "notification_id": notif["id"],
                    "action": "rejected",
                    "reason": "DoD verification required"
                })

    return {
        "success": True,
        "processed": len(results),
        "approved": len([r for r in results if r["action"] == "approved"]),
        "rejected": len([r for r in results if r["action"] == "rejected"]),
        "notifications": results
    }
```

---

### Command: project_manager.send_agent_notification

**Purpose**: Send agent-specific message (wrapper for common notification patterns)

**Tables**:
- Write: `notifications`

**Required Skills**: None

**Input Parameters**:
```yaml
target_agent: string     # Agent to notify
message_type: string     # "spec_needed", "review_complete", "work_available", etc.
priority_id: string      # Related priority ID
additional_data: object  # Optional - Additional context
```

**Output**:
```json
{
  "success": true,
  "notification_id": "notif-12349",
  "target_agent": "architect"
}
```

**Success Criteria**:
- ✅ Notification sent with correct format
- ✅ Message type mapped to agent expectations
- ✅ CFR-009 enforced (sound=false)

---

## Command Group 3: Monitoring (4 Commands)

### Command: project_manager.monitor_github_prs

**Purpose**: Monitor GitHub pull requests and detect blockers

**Tables**:
- Write: `system_audit`
- Read: `roadmap_priority`

**Required Skills**: `pr_monitoring_analysis`

**Required Tools**: `gh` (GitHub CLI)

**Input Parameters**:
```yaml
repository: string       # GitHub repository (default: current repo)
state: string            # "open", "closed", "all" (default: "open")
check_blockers: boolean  # Detect blocking issues (default: true)
```

**Output**:
```json
{
  "success": true,
  "prs_found": 5,
  "blocking_prs": 1,
  "prs": [
    {
      "number": 123,
      "title": "Implement feature X",
      "state": "open",
      "blocked": true,
      "blocker_reason": "Failing CI checks",
      "url": "https://github.com/..."
    }
  ],
  "recommendations": [
    "PR #123 needs attention - CI failing"
  ]
}
```

**Success Criteria**:
- ✅ GitHub PRs queried via `gh` CLI
- ✅ Blockers detected (failing checks, conflicts, stale)
- ✅ Recommendations generated
- ✅ Audit log created

**External Tool Usage**:

```bash
# Query GitHub PRs
gh pr list --state open --json number,title,state,statusCheckRollup

# Check PR details
gh pr view 123 --json statusCheckRollup,mergeable,reviews
```

**Database Operations**:

```python
def monitor_github_prs(db: DomainWrapper, params: dict):
    # Use gh CLI to query PRs
    result = subprocess.run(
        ["gh", "pr", "list", "--state", params.get("state", "open"),
         "--json", "number,title,state,statusCheckRollup,mergeable"],
        capture_output=True, text=True
    )

    prs = json.loads(result.stdout)

    blocking_prs = []
    recommendations = []

    for pr in prs:
        # Check for blockers
        blocked = False
        blocker_reason = None

        # Check CI status
        if pr.get("statusCheckRollup"):
            checks = pr["statusCheckRollup"]
            if any(c["conclusion"] == "failure" for c in checks):
                blocked = True
                blocker_reason = "Failing CI checks"

        # Check merge conflicts
        if pr.get("mergeable") == "CONFLICTING":
            blocked = True
            blocker_reason = "Merge conflicts"

        if blocked:
            blocking_prs.append({
                "number": pr["number"],
                "title": pr["title"],
                "blocked": True,
                "blocker_reason": blocker_reason
            })
            recommendations.append(f"PR #{pr['number']} needs attention - {blocker_reason}")

    # Audit log
    db.write("system_audit", {
        "table_name": "github_prs",
        "action": "monitor",
        "item_id": "github_monitor",
        "field_changed": "pr_status",
        "new_value": json.dumps({"total": len(prs), "blocked": len(blocking_prs)}),
        "changed_by": "project_manager",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": True,
        "prs_found": len(prs),
        "blocking_prs": len(blocking_prs),
        "prs": prs,
        "recommendations": recommendations
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| GitHubAPIError | Rate limit, authentication | Wait, check token |
| CLINotFoundError | `gh` not installed | Install GitHub CLI |
| NetworkError | Network connectivity | Retry, check connection |

---

### Command: project_manager.monitor_github_issues

**Purpose**: Monitor GitHub issues and track bug reports

**Tables**:
- Write: `system_audit`
- Read: `roadmap_priority`

**Required Skills**: None

**Required Tools**: `gh` (GitHub CLI)

**Input Parameters**:
```yaml
repository: string       # GitHub repository (default: current repo)
label: string            # Filter by label (optional)
state: string            # "open", "closed", "all" (default: "open")
```

**Output**:
```json
{
  "success": true,
  "issues_found": 10,
  "critical_issues": 2,
  "issues": [
    {
      "number": 456,
      "title": "Critical bug in parser",
      "labels": ["bug", "critical"],
      "state": "open",
      "url": "https://github.com/..."
    }
  ]
}
```

**Success Criteria**:
- ✅ GitHub issues queried
- ✅ Critical issues flagged
- ✅ Audit log created

**External Tool Usage**:

```bash
# Query GitHub issues
gh issue list --state open --json number,title,labels,state

# Filter by label
gh issue list --label "bug" --json number,title,state
```

---

### Command: project_manager.analyze_project_health

**Purpose**: Generate comprehensive project health report (velocity, blockers, risks)

**Tables**:
- Read: `roadmap_priority`, `specs_specification`, `review_code_review`, `agent_lifecycle`
- Write: `system_audit`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
time_window: integer     # Days to analyze (default: 30)
include_metrics: boolean # Include detailed metrics (default: true)
include_risks: boolean   # Include risk analysis (default: true)
```

**Output**:
```json
{
  "success": true,
  "health_score": 85,
  "velocity": {
    "avg_completion_time_days": 3.5,
    "completed_last_30_days": 12,
    "in_progress": 5
  },
  "blockers": [
    {
      "priority_id": "PRIORITY-25",
      "blocked_reason": "Waiting for architect spec",
      "days_blocked": 7
    }
  ],
  "risks": [
    {
      "type": "low_velocity",
      "severity": "medium",
      "description": "Completion rate down 20% from last month"
    }
  ],
  "recommendations": [
    "Unblock PRIORITY-25 by creating spec",
    "Increase architect bandwidth for spec creation"
  ]
}
```

**Success Criteria**:
- ✅ Health score calculated (0-100)
- ✅ Velocity metrics computed
- ✅ Blockers identified
- ✅ Risks flagged
- ✅ Actionable recommendations provided

**Database Operations**:

```python
def analyze_project_health(db: DomainWrapper, params: dict):
    time_window = params.get("time_window", 30)
    cutoff_date = datetime.now() - timedelta(days=time_window)

    # Get all priorities
    priorities = db.read("roadmap_priority")

    # Calculate velocity
    completed = [p for p in priorities
                 if p["status"] == "✅ Complete"
                 and p.get("completed_at")
                 and datetime.fromisoformat(p["completed_at"]) > cutoff_date]

    in_progress = [p for p in priorities if p["status"] == "🏗️ In Progress"]
    planned = [p for p in priorities if p["status"] == "📝 Planned"]

    # Calculate avg completion time
    completion_times = []
    for p in completed:
        if p.get("started_at") and p.get("completed_at"):
            start = datetime.fromisoformat(p["started_at"])
            end = datetime.fromisoformat(p["completed_at"])
            days = (end - start).days
            completion_times.append(days)

    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

    # Detect blockers
    blockers = []
    for p in in_progress:
        if not p.get("spec_id"):
            blockers.append({
                "priority_id": p["id"],
                "blocked_reason": "Waiting for architect spec",
                "days_blocked": calculate_days_since(p.get("updated_at"))
            })

    # Calculate health score
    health_score = calculate_health_score(
        completed_count=len(completed),
        in_progress_count=len(in_progress),
        blocker_count=len(blockers),
        avg_completion_time=avg_completion_time
    )

    # Generate recommendations
    recommendations = []
    if len(blockers) > 0:
        recommendations.append(f"Unblock {len(blockers)} priorities by creating specs")
    if avg_completion_time > 5:
        recommendations.append("Completion time above target - investigate delays")

    return {
        "success": True,
        "health_score": health_score,
        "velocity": {
            "avg_completion_time_days": avg_completion_time,
            "completed_last_30_days": len(completed),
            "in_progress": len(in_progress)
        },
        "blockers": blockers,
        "recommendations": recommendations
    }
```

---

### Command: project_manager.detect_stale_priorities

**Purpose**: Find priorities that are stuck (no progress for N days)

**Tables**:
- Read: `roadmap_priority`
- Write: `system_audit`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
stale_threshold_days: integer  # Days without update (default: 14)
statuses: list                 # Statuses to check (default: ["🏗️ In Progress"])
```

**Output**:
```json
{
  "success": true,
  "stale_priorities": 3,
  "priorities": [
    {
      "priority_id": "PRIORITY-20",
      "title": "Feature X",
      "status": "🏗️ In Progress",
      "days_stale": 21,
      "last_updated": "2025-10-05",
      "recommendations": ["Check with code_developer", "Consider re-planning"]
    }
  ]
}
```

**Success Criteria**:
- ✅ Stale priorities identified
- ✅ Days stale calculated
- ✅ Recommendations provided
- ✅ Audit log created

**Database Operations**:

```python
def detect_stale_priorities(db: DomainWrapper, params: dict):
    threshold_days = params.get("stale_threshold_days", 14)
    statuses = params.get("statuses", ["🏗️ In Progress"])
    cutoff_date = datetime.now() - timedelta(days=threshold_days)

    # Get priorities in specified statuses
    priorities = db.read("roadmap_priority", {"status": statuses})

    stale = []
    for p in priorities:
        updated_at = datetime.fromisoformat(p["updated_at"])
        if updated_at < cutoff_date:
            days_stale = (datetime.now() - updated_at).days
            stale.append({
                "priority_id": p["id"],
                "title": p["title"],
                "status": p["status"],
                "days_stale": days_stale,
                "last_updated": p["updated_at"],
                "recommendations": generate_stale_recommendations(p, days_stale)
            })

    return {
        "success": True,
        "stale_priorities": len(stale),
        "priorities": stale
    }
```

---

## Command Group 4: Verification (3 Commands)

### Command: project_manager.verify_dod_puppeteer

**Purpose**: Verify Definition of Done using Puppeteer browser automation

**Tables**:
- Read: `roadmap_priority`, `specs_specification`
- Write: `system_audit`

**Required Skills**: `dod_verification`

**Required Tools**: `puppeteer` (via MCP)

**Input Parameters**:
```yaml
priority_id: string      # Priority to verify
test_url: string         # Optional - URL to test
acceptance_criteria: list # Optional - Specific criteria to check
```

**Output**:
```json
{
  "success": true,
  "priority_id": "PRIORITY-25",
  "dod_passed": true,
  "criteria_checked": 5,
  "criteria_passed": 5,
  "screenshots": ["screenshot1.png", "screenshot2.png"],
  "details": [
    {
      "criterion": "User can login",
      "passed": true,
      "evidence": "screenshot1.png"
    }
  ]
}
```

**Success Criteria**:
- ✅ Browser automation executed
- ✅ Acceptance criteria verified
- ✅ Screenshots captured
- ✅ DoD status recorded
- ✅ Audit log created

**External Tool Usage**:

```typescript
// Puppeteer MCP usage
await puppeteer_navigate({ url: "http://localhost:3000" });
await puppeteer_click({ selector: "#login-button" });
await puppeteer_fill({ selector: "#username", value: "test" });
await puppeteer_screenshot({ name: "login-test" });
```

**Database Operations**:

```python
def verify_dod_puppeteer(db: DomainWrapper, params: dict):
    # Get priority and spec
    priority = db.read("roadmap_priority", {"id": params["priority_id"]})[0]
    spec = db.read("specs_specification", {"id": priority.get("spec_id")})[0] if priority.get("spec_id") else None

    # Get acceptance criteria
    criteria = params.get("acceptance_criteria")
    if not criteria and spec:
        criteria = extract_acceptance_criteria(spec)

    # Execute verification with Puppeteer (via MCP)
    results = []
    screenshots = []

    for criterion in criteria:
        # Run test
        result = execute_dod_test(criterion, params.get("test_url"))
        results.append({
            "criterion": criterion["description"],
            "passed": result["passed"],
            "evidence": result["screenshot"]
        })
        screenshots.append(result["screenshot"])

    passed_count = sum(1 for r in results if r["passed"])
    dod_passed = passed_count == len(criteria)

    # Update DoD status
    db.write("roadmap_priority", {
        "id": params["priority_id"],
        "dod_verified": dod_passed,
        "dod_verified_at": datetime.now().isoformat()
    }, action="update")

    return {
        "success": True,
        "priority_id": params["priority_id"],
        "dod_passed": dod_passed,
        "criteria_checked": len(criteria),
        "criteria_passed": passed_count,
        "screenshots": screenshots,
        "details": results
    }
```

---

### Command: project_manager.strategic_planning

**Purpose**: Plan next priorities based on dependencies, resources, and goals

**Tables**:
- Read: `roadmap_priority`, `specs_specification`, `agent_lifecycle`
- Write: `roadmap_priority`, `system_audit`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
planning_horizon_days: integer  # Days to plan ahead (default: 30)
max_priorities: integer         # Max priorities to plan (default: 10)
consider_dependencies: boolean  # Check dependencies (default: true)
```

**Output**:
```json
{
  "success": true,
  "priorities_planned": 5,
  "planning_horizon_days": 30,
  "planned_priorities": [
    {
      "priority_id": "PRIORITY-30",
      "title": "Feature Y",
      "estimated_start": "2025-11-01",
      "estimated_completion": "2025-11-05",
      "dependencies": ["PRIORITY-25"]
    }
  ],
  "recommendations": [
    "architect should create specs for PRIORITY-30, PRIORITY-31",
    "code_developer has capacity for 2 more priorities"
  ]
}
```

**Success Criteria**:
- ✅ Available capacity calculated
- ✅ Dependencies checked
- ✅ Priorities scheduled
- ✅ Recommendations provided

---

### Command: project_manager.create_roadmap_report

**Purpose**: Generate comprehensive roadmap status report

**Tables**:
- Read: `roadmap_priority`, `specs_specification`, `review_code_review`
- Write: `system_audit`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
report_type: string      # "summary", "detailed", "executive"
output_format: string    # "markdown", "json", "html"
include_charts: boolean  # Include visualization data (default: true)
```

**Output**:
```json
{
  "success": true,
  "report_type": "summary",
  "generated_at": "2025-10-26T11:00:00Z",
  "report_url": "reports/roadmap-summary-2025-10-26.md",
  "summary": {
    "total_priorities": 50,
    "completed": 30,
    "in_progress": 10,
    "planned": 10,
    "completion_rate": 60
  }
}
```

**Success Criteria**:
- ✅ Report generated in requested format
- ✅ All metrics included
- ✅ Charts generated (if requested)
- ✅ Report saved to file

---

## Implementation Tasks

### Task Breakdown (CFR-007 Compliant: <30% context each)

#### TASK-102-1: Roadmap Parsing Commands (8 hours)

**Scope**:
- Implement `parse_roadmap` command
- Implement `update_priority_status` command
- Implement `update_metadata` command
- Implement `create_roadmap_audit` command

**Files**:
- Create: `.claude/commands/agents/project_manager/parse_roadmap.md`
- Create: `.claude/commands/agents/project_manager/update_priority_status.md`
- Create: `.claude/commands/agents/project_manager/update_metadata.md`
- Create: `.claude/commands/agents/project_manager/create_roadmap_audit.md`
- Create: `coffee_maker/commands/project_manager/roadmap_parsing.py` (implementation)

**Tests**:
- Create: `tests/unit/test_project_manager_roadmap_parsing.py`
- Test parse_roadmap with sample ROADMAP.md
- Test update_priority_status with valid/invalid transitions
- Test metadata updates
- Test audit trail creation

**Context Size**: ~25% (4 commands + implementation + tests)

**Success Criteria**:
- ✅ All 4 commands load correctly
- ✅ ROADMAP.md parsing works
- ✅ Status updates enforce valid transitions
- ✅ Audit trail complete

---

#### TASK-102-2: Communication Commands (6 hours)

**Scope**:
- Implement `create_notification` command
- Implement `process_notifications` command
- Implement `send_agent_notification` command

**Files**:
- Create: `.claude/commands/agents/project_manager/create_notification.md`
- Create: `.claude/commands/agents/project_manager/process_notifications.md`
- Create: `.claude/commands/agents/project_manager/send_agent_notification.md`
- Create: `coffee_maker/commands/project_manager/communication.py`

**Tests**:
- Create: `tests/unit/test_project_manager_communication.py`
- Test notification creation (CFR-009 enforcement)
- Test notification processing
- Test agent-specific messages

**Context Size**: ~20% (3 commands + implementation + tests)

**Success Criteria**:
- ✅ CFR-009 enforced (sound=false)
- ✅ Notifications sent and received correctly
- ✅ Batch processing works

---

#### TASK-102-3: Monitoring Commands (10 hours)

**Scope**:
- Implement `monitor_github_prs` command
- Implement `monitor_github_issues` command
- Implement `analyze_project_health` command
- Implement `detect_stale_priorities` command

**Files**:
- Create: `.claude/commands/agents/project_manager/monitor_github_prs.md`
- Create: `.claude/commands/agents/project_manager/monitor_github_issues.md`
- Create: `.claude/commands/agents/project_manager/analyze_project_health.md`
- Create: `.claude/commands/agents/project_manager/detect_stale_priorities.md`
- Create: `coffee_maker/commands/project_manager/monitoring.py`

**Tests**:
- Create: `tests/unit/test_project_manager_monitoring.py`
- Mock GitHub CLI responses
- Test health analysis logic
- Test stale detection

**Context Size**: ~28% (4 commands + GitHub integration + tests)

**Success Criteria**:
- ✅ GitHub CLI integration works
- ✅ Health score calculated correctly
- ✅ Blockers detected
- ✅ Stale priorities identified

---

#### TASK-102-4: Verification Commands (8 hours)

**Scope**:
- Implement `verify_dod_puppeteer` command
- Implement `strategic_planning` command
- Implement `create_roadmap_report` command

**Files**:
- Create: `.claude/commands/agents/project_manager/verify_dod_puppeteer.md`
- Create: `.claude/commands/agents/project_manager/strategic_planning.md`
- Create: `.claude/commands/agents/project_manager/create_roadmap_report.md`
- Create: `coffee_maker/commands/project_manager/verification.py`

**Tests**:
- Create: `tests/unit/test_project_manager_verification.py`
- Mock Puppeteer MCP
- Test DoD verification logic
- Test strategic planning
- Test report generation

**Context Size**: ~27% (3 commands + Puppeteer + tests)

**Success Criteria**:
- ✅ Puppeteer integration works
- ✅ DoD verification accurate
- ✅ Planning considers dependencies
- ✅ Reports generated correctly

---

## Total Effort Estimate

| Task | Hours | Complexity | Context % |
|------|-------|------------|-----------|
| TASK-102-1: Roadmap Parsing | 8 | Medium | 25% |
| TASK-102-2: Communication | 6 | Low | 20% |
| TASK-102-3: Monitoring | 10 | High | 28% |
| TASK-102-4: Verification | 8 | High | 27% |
| **TOTAL** | **32** | **Medium-High** | **<30% each** ✅ |

---

## Success Criteria

### Functional
- ✅ All 14 commands implemented
- ✅ ROADMAP.md parsing and sync works
- ✅ Notifications system functional
- ✅ GitHub monitoring operational
- ✅ DoD verification with Puppeteer works

### Technical
- ✅ All unit tests pass (>90% coverage)
- ✅ CFR-009 enforced (sound=false)
- ✅ CFR-015 enforced (database-only, no file access)
- ✅ Audit trails complete
- ✅ Context budget <30% per task

### Integration
- ✅ Commands load via CommandLoader
- ✅ Permissions enforced (write access to roadmap_*)
- ✅ Skills integrate correctly
- ✅ External tools (gh, puppeteer) work

---

## Dependencies

### Python Packages
- `frontmatter` - Markdown parsing (Tier 1 approved)
- Existing: `sqlite3`, `datetime`, `json`

### External Tools
- `gh` (GitHub CLI) - Already configured
- `puppeteer` (via MCP) - Already configured

### Existing Infrastructure
- RoadmapDatabase - Wrapped by DomainWrapper
- NotificationDatabase - Used for notifications
- SkillLoader - For roadmap_database_handling, dod_verification

---

## Related Documents

- [SPEC-100: Unified Agent Commands Architecture (Master)](SPEC-100-unified-agent-commands-architecture.md)
- [SPEC-101: Foundation Infrastructure](SPEC-101-foundation-infrastructure.md)
- [docs/UNIFIED_AGENT_COMMANDS_COMPLETE_PLAN.md](../../UNIFIED_AGENT_COMMANDS_COMPLETE_PLAN.md)
- [.claude/agents/project_manager.md](../../../.claude/agents/project_manager.md)
- [CFR-009: Sound Notifications](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-009)
- [CFR-015: Centralized Database Storage](../../CFR-015-CENTRALIZED-DATABASE-STORAGE.md)

---

**Specification Status**: Draft - Ready for Review
**Estimated Effort**: 32 hours
**Complexity**: Medium-High
**Context Budget**: All tasks <30% ✅
**Dependencies**: SPEC-101 (Foundation Infrastructure)
