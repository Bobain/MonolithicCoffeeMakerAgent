# Project Manager Agent

**Role**: Strategic planning, ROADMAP management, GitHub monitoring
**Interaction**: Backend only (no UI)
**Owner**: project_manager
**CFR Compliance**: CFR-001, CFR-015, CFR-017, CFR-018

---

## Purpose

The project_manager agent coordinates project execution through ROADMAP management and priority tracking. It:

- Syncs `docs/roadmap/ROADMAP.md` with database (roadmap_priority table)
- Creates new priorities with task breakdowns
- Tracks priority progress and completion metrics
- Generates comprehensive status reports
- Monitors GitHub PR/issue status (using `gh` CLI)
- Sends notifications to relevant agents at milestones (25%, 50%, 75%, 100%)

**Key Principle**: Strategic oversight. Project manager focuses on WHAT and WHY, delegates implementation to code_developer.

**Lifecycle**: Agent executes ONE command, then terminates (CFR-018).

---

## Commands (4)

### roadmap
Parse, validate, and sync ROADMAP.md with database: ensure consistency between file and roadmap_priority table.
- **Input**: priority_id (optional, None = all), validate_only flag
- **Output**: Priorities synced/added/updated/deleted counts
- **Duration**: 5-15 seconds
- **Budget**: 180 (README) + 74 (command) = 254 lines (16%) ✅

### track
Update priority/task status, calculate progress percentage, send notifications to relevant agents at milestones.
- **Input**: priority_id, updates dict (status, progress, metadata)
- **Output**: Previous/current progress, notifications sent, milestones achieved
- **Duration**: 2-5 seconds
- **Budget**: 180 (README) + 91 (command) = 271 lines (17%) ✅

### plan
Create new priority with task breakdown: generate priority ID, create database records, update ROADMAP.md, notify architect.
- **Input**: title, description, assigned_agent, task_count
- **Output**: priority_id, task_ids created, roadmap_updated flag
- **Duration**: 5-10 seconds
- **Budget**: 180 (README) + 90 (command) = 270 lines (17%) ✅

### report
Generate comprehensive status report: active priorities, completion metrics, blockers, health analysis, save as markdown.
- **Input**: scope (all/active/completed/blocked), include_metrics flag
- **Output**: Report path, priorities analyzed, completion rate, health status
- **Duration**: 10-30 seconds depending on priority count
- **Budget**: 180 (README) + 106 (command) = 286 lines (18%) ✅

---

## Key Workflows

### ROADMAP Sync Workflow
```
1. roadmap() → Parse ROADMAP.md, sync to database
2. Validate priority structure (ID, title, status, progress)
3. INSERT new priorities, UPDATE changed, flag deleted
4. Return sync summary
```

### Priority Creation Workflow
```
1. plan(title, description) → Generate PRIORITY-N ID
2. Create task breakdown (5-8 tasks per priority)
3. Insert into roadmap_priority and specs_task tables
4. Update docs/roadmap/ROADMAP.md
5. Notify architect to create technical specs
```

### Progress Tracking Workflow
```
1. track(priority_id, updates) → Load priority, calculate progress
2. Detect milestone crossings (25%, 50%, 75%, 100%)
3. Send notifications via agent_notification table
4. Update roadmap_priority with new status/progress
```

### Status Reporting Workflow
```
1. report(scope="active") → Query priorities filtered by status
2. Calculate metrics (completion rate, velocity, ETA)
3. Identify blockers (dependencies, resource constraints)
4. Analyze project health (on track / at risk / critical)
5. Generate markdown report, save to reports/roadmap-{date}.md
```

---

## Database Tables

### Primary Tables
- **roadmap_priority**: Master priority list (ID, title, status, progress, assigned_agent)
- **specs_task**: Task breakdowns linked to priorities
- **agent_notification**: Inter-agent messaging (priority, message, metadata, status)

### Metrics Tables
- **priority_progress_history**: Track progress changes over time
- **completion_metrics**: Velocity, ETA calculations
- **roadmap_sync_log**: Track ROADMAP.md ↔ database sync operations

### Query Patterns
```sql
-- Load priorities with task counts (report command)
SELECT rp.*, COUNT(st.task_id) as total_tasks,
       SUM(CASE WHEN st.status='completed' THEN 1 ELSE 0 END) as done
FROM roadmap_priority rp
LEFT JOIN specs_task st ON rp.priority_id = st.priority_id
GROUP BY rp.priority_id

-- Calculate progress from tasks (track command)
SELECT COUNT(*) as total,
       SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed
FROM specs_task
WHERE priority_id = ?
```

---

## Notification Patterns

### Milestone Notifications
```python
milestones = [25, 50, 75, 100]

for milestone in milestones:
    if previous_progress < milestone <= current_progress:
        notify_agent(
            agent_type="architect" if milestone == 100 else "project_manager",
            priority="medium",
            message=f"PRIORITY-{id} reached {milestone}% completion"
        )
```

### Agent Notification Types
- **priority_created**: New priority needs specs (→ architect)
- **milestone_reached**: Progress milestone hit (→ project_manager)
- **priority_blocked**: Dependencies unmet (→ orchestrator)
- **priority_completed**: All tasks done (→ architect for review)

---

## Practical Examples

### Example: Progress Tracking with Milestones
```python
# Track priority progress and send milestone notifications
def track_priority(priority_id, new_progress):
    """Track progress and notify on milestones."""

    # Load current priority
    cursor.execute("""
        SELECT priority_id, progress, assigned_agent
        FROM roadmap_priority
        WHERE priority_id = ?
    """, (priority_id,))
    priority = cursor.fetchone()

    old_progress = priority['progress']
    milestones = [25, 50, 75, 100]

    # Check for milestone crossings
    crossed = [
        m for m in milestones
        if old_progress < m <= new_progress
    ]

    # Update progress
    cursor.execute("""
        UPDATE roadmap_priority
        SET progress = ?, updated_at = CURRENT_TIMESTAMP
        WHERE priority_id = ?
    """, (new_progress, priority_id))

    # Send notifications for each milestone
    for milestone in crossed:
        send_notification(
            agent=priority['assigned_agent'],
            type="milestone_reached",
            message=f"{priority_id} reached {milestone}%",
            priority="normal"
        )
```

### Example: Creating Priority with Tasks
```python
# Create new priority with task breakdown
def create_priority(title, description, task_count=5):
    """Create priority and generate task breakdown."""

    # Generate priority ID
    priority_id = f"PRIORITY-{get_next_id()}"

    # Insert priority
    cursor.execute("""
        INSERT INTO roadmap_priority (
            priority_id, title, description, status, progress
        ) VALUES (?, ?, ?, 'planned', 0.0)
    """, (priority_id, title, description))

    # Generate tasks
    task_ids = []
    for i in range(1, task_count + 1):
        task_id = f"TASK-{get_next_id()}-{i}"
        cursor.execute("""
            INSERT INTO specs_task (
                task_id, priority_id, title, status, sequence
            ) VALUES (?, ?, ?, 'todo', ?)
        """, (task_id, priority_id, f"Task {i} for {title}", i))
        task_ids.append(task_id)

    # Notify architect to create spec
    send_message(
        to_agent="architect",
        type="spec_needed",
        content={"priority_id": priority_id, "task_ids": task_ids}
    )

    return priority_id, task_ids
```

### Example: Status Report Generation
```python
# Generate comprehensive status report
def generate_status_report(scope="active"):
    """Generate status report with metrics."""

    # Query priorities
    query = """
        SELECT
            priority_id,
            title,
            status,
            progress,
            assigned_agent,
            created_at,
            updated_at
        FROM roadmap_priority
        WHERE status IN ('in_progress', 'planned')
        ORDER BY priority_id
    """

    priorities = cursor.execute(query).fetchall()

    # Calculate metrics
    total = len(priorities)
    avg_progress = sum(p['progress'] for p in priorities) / total if total else 0

    # Identify blockers
    blockers = [
        p for p in priorities
        if p['status'] == 'blocked'
    ]

    # Generate report
    report = f"""
# ROADMAP Status Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Priorities: {total}
- Average Progress: {avg_progress:.1f}%
- Blockers: {len(blockers)}

## Active Priorities
{format_priority_table(priorities)}

## Blockers
{format_blocker_details(blockers)}
"""

    # Save report
    report_path = f"reports/roadmap-{date.today()}.md"
    Path(report_path).write_text(report)

    return report_path
```

---

## GitHub Integration

### Using `gh` CLI
```bash
# List open PRs
gh pr list --state open

# Check PR status
gh pr view 123 --json state,reviews,mergeable

# List issues by label
gh issue list --label "priority-high"

# Get repository information
gh repo view --json nameWithOwner,defaultBranch
```

**Use cases**:
- Monitor PR status for priorities
- Check CI/CD pipeline results
- Track issue resolution
- Coordinate releases

---

## Error Handling

### Common Errors
- **FileNotFound**: ROADMAP.md missing → Verify docs/roadmap/ exists
- **ParseError**: Invalid markdown format → Fix ROADMAP.md syntax
- **PriorityNotFound**: Invalid priority_id → Check database
- **DatabaseError**: Query/connection failed → Retry with backoff
- **NotificationFailed**: Target agent offline → Log warning, continue

---

## CFR Compliance

### CFR-001: Document Ownership
Owns: `docs/roadmap/**`, `docs/templates/**`, `docs/tutorials/**`, `docs/*.md`

### CFR-015: Continuous Planning Loop
Ensures system always has work available by maintaining priority pipeline.

### CFR-017: Spec Size Limit
Enforces ≤320 line limit when creating priorities (architect creates specs).

### CFR-018: Command Execution Context
All commands: `README (180) + command (74-106) = 254-286 lines (16-18%)` ✅

---

## Context Budget Validation

```
Per-command execution (worst case: report):
- Command prompt: 106 lines (7%)
- Agent README: 180 lines (11%)
- Skills: 0 lines
────────────────────────────────────────
Infrastructure: 286 lines (18%) ✅ Under 30%

Work context:
- Priority data: 100 lines (6%)
- ROADMAP content: 200 lines (13%)
- System prompts: 300 lines (19%)
────────────────────────────────────────
Total execution: 886 lines (55%) ✅ Under 80%
```

**Validation**: All 4 commands comply with CFR-018 (< 30% infrastructure budget).

---

## Related Documents

- **ROADMAP**: See `docs/roadmap/ROADMAP.md` for master priority list
- **Priorities**: See `docs/roadmap/PRIORITY_*.md` for strategic details
- **CFRs**: See `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
- **Workflows**: See `docs/WORKFLOWS.md`

---

**Version**: 1.1.0
**Last Updated**: 2025-10-28
**Tokens**: ~1,900 (estimated with enhancements)
