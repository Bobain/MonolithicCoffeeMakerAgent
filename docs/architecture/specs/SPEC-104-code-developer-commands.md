# SPEC-104: Code Developer Commands

**Status**: Draft
**Created**: 2025-10-26
**Author**: architect
**Parent Spec**: SPEC-100
**Related Specs**: SPEC-101 (Foundation), SPEC-102 (Project Manager), SPEC-103 (Architect)
**Related CFRs**: CFR-007 (Context Budget), CFR-013 (Git Workflow), CFR-014 (Database Tracing)
**Dependencies**: SPEC-101 (Foundation), SPEC-102 (Project Manager), SPEC-103 (Architect)

## Executive Summary

Implement 14 commands for the code_developer agent, covering work management, code operations, and quality assurance. These commands enable autonomous implementation from the database while enforcing code quality standards and proper workflow tracking.

### Key Objectives

1. **Work Management** - Claim priorities, load specs, update status (3 commands)
2. **Code Operations** - Record commits, complete work, create PRs (4 commands)
3. **Quality Assurance** - Testing, pre-commit, bug fixes, metrics (7 commands)

### Design Principles

- **Database-First**: ALL work items and status from database
- **Progressive Disclosure**: Load only needed spec sections (CFR-007)
- **Autonomous Execution**: code_developer works independently from ROADMAP
- **Quality Gates**: Tests, coverage, pre-commit hooks enforced
- **Traceability**: Every commit, test run, metric tracked

---

## Architecture Overview

### Command Groups

```
Code Developer (14 commands)
├── Work Management (3 commands)
│   ├── claim_priority              - Claim roadmap item for implementation
│   ├── load_spec                   - Load spec content (progressive)
│   └── update_implementation_status - Update work status
│
├── Code Operations (4 commands)
│   ├── record_commit               - Record commit to review queue
│   ├── complete_implementation     - Mark implementation complete
│   ├── request_code_review         - Trigger code_reviewer analysis
│   └── create_pull_request         - Create GitHub PR
│
└── Quality Assurance (7 commands)
    ├── run_test_suite              - Execute pytest with coverage
    ├── fix_failing_tests           - Analyze and fix test failures
    ├── run_pre_commit_hooks        - Execute pre-commit checks
    ├── implement_bug_fix           - Fix bugs from bug tracking
    ├── track_metrics               - Record implementation metrics
    ├── generate_coverage_report    - Generate test coverage report
    └── update_claude_config        - Update .claude/ configuration
```

### Database Domain

**Tables Owned (Write Access)**:
- `review_commit` - Commits for code review
- `metrics_subtask` - Implementation metrics

**Tables Read**:
- `roadmap_priority` - Work items to implement
- `specs_specification` - Technical specifications
- `specs_task` - Implementation tasks
- `specs_task_dependency` - Task ordering
- `notifications` - Work assignments, feedback

---

## Command Group 1: Work Management (3 Commands)

### Command: code_developer.claim_priority

**Purpose**: Claim a roadmap priority for implementation (prevent concurrent work)

**Tables**:
- Write: `roadmap_priority`, `system_audit`
- Read: `roadmap_priority`, `specs_task`, `specs_task_dependency`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
priority_id: string      # Required - Priority to claim (e.g., "PRIORITY-28")
force_claim: boolean     # Override existing claim (default: false)
estimated_start: string  # ISO date when starting work
```

**Output**:
```json
{
  "success": true,
  "priority_id": "PRIORITY-28",
  "claimed_by": "code_developer",
  "claimed_at": "2025-10-26T10:00:00Z",
  "spec_id": "SPEC-131",
  "tasks_available": 3,
  "dependencies_satisfied": true
}
```

**Success Criteria**:
- ✅ Priority claimed atomically (prevents race conditions)
- ✅ Dependencies verified (prerequisites complete)
- ✅ Spec exists and is approved
- ✅ Tasks created and ready
- ✅ Audit trail created

**Database Operations**:

```python
def claim_priority(db: DomainWrapper, params: dict):
    priority_id = params["priority_id"]

    # Get priority
    priorities = db.read("roadmap_priority", {"id": priority_id})
    if not priorities:
        return {"success": False, "error": f"Priority {priority_id} not found"}

    priority = priorities[0]

    # Check if already claimed
    if priority.get("claimed_by") and not params.get("force_claim", False):
        return {
            "success": False,
            "error": f"Priority already claimed by {priority['claimed_by']}",
            "claimed_by": priority["claimed_by"],
            "claimed_at": priority.get("claimed_at")
        }

    # Verify spec exists
    if not priority.get("spec_id"):
        return {
            "success": False,
            "error": "No technical spec available",
            "recommendation": "architect should create spec first"
        }

    # Check dependencies
    tasks = db.read("specs_task", {"roadmap_item_id": priority_id})
    if tasks:
        task_group_id = tasks[0]["task_group_id"]
        dependencies = db.read("specs_task_dependency", {"task_group_id": task_group_id})

        for dep in dependencies:
            if dep["dependency_type"] == "hard":
                # Check if prerequisite is complete
                prereq_tasks = db.read("specs_task", {"task_group_id": dep["depends_on_group_id"]})
                if not all(t["status"] == "completed" for t in prereq_tasks):
                    return {
                        "success": False,
                        "error": f"Dependency {dep['depends_on_group_id']} not complete",
                        "blocked_by": dep["depends_on_group_id"]
                    }

    # Claim priority
    db.write("roadmap_priority", {
        "id": priority_id,
        "claimed_by": "code_developer",
        "claimed_at": datetime.now().isoformat(),
        "status": "🏗️ In Progress",
        "started_at": params.get("estimated_start", datetime.now().isoformat())
    }, action="update")

    return {
        "success": True,
        "priority_id": priority_id,
        "claimed_by": "code_developer",
        "claimed_at": datetime.now().isoformat(),
        "spec_id": priority.get("spec_id"),
        "tasks_available": len(tasks),
        "dependencies_satisfied": True
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| AlreadyClaimedError | Priority claimed by another agent | Wait or force claim |
| NoSpecError | Technical spec missing | architect creates spec |
| DependencyBlockedError | Prerequisites not complete | Wait for dependencies |
| NotFoundError | Priority doesn't exist | Verify priority ID |

**Downstream Effects**:
- Status changes to "In Progress"
- orchestrator sees work started
- Dashboard shows claimed work
- Audit trail enables tracking

---

### Command: code_developer.load_spec

**Purpose**: Load specification content for current implementation phase (progressive disclosure)

**Tables**:
- Read: `specs_specification`, `specs_task`

**Required Skills**: `technical_specification_handling`

**Input Parameters**:
```yaml
spec_id: string          # Required - Spec to load (e.g., "SPEC-131")
task_id: string          # Optional - Specific task (loads only needed sections)
phase: string            # Optional - Specific phase (for hierarchical specs)
full_content: boolean    # Load entire spec (default: false, CFR-007)
```

**Output**:
```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "spec_type": "hierarchical",
  "loaded_sections": ["overview", "implementation", "phase_1"],
  "content": {
    "overview": "...",
    "implementation": "...",
    "phase_1": "..."
  },
  "context_tokens": 2500,
  "estimated_hours": 8.0,
  "reuse_components": [
    {
      "component": "ConfigManager",
      "location": "SPEC-120",
      "fitness": 85
    }
  ]
}
```

**Success Criteria**:
- ✅ Only needed sections loaded (CFR-007)
- ✅ Context budget <30%
- ✅ Hierarchical specs load progressively
- ✅ Reuse components highlighted
- ✅ Dependencies documented

**Database Operations**:

```python
def load_spec(db: DomainWrapper, params: dict):
    spec_id = params["spec_id"]

    # Get spec from database
    specs = db.read("specs_specification", {"id": spec_id})
    if not specs:
        return {"success": False, "error": f"Spec {spec_id} not found"}

    spec = specs[0]
    content_json = json.loads(spec["content"])

    # Determine what to load
    if params.get("full_content", False):
        # Load everything (use sparingly)
        loaded_sections = list(content_json.keys())
        content = content_json
    elif params.get("task_id"):
        # Load sections needed for specific task
        task = db.read("specs_task", {"id": params["task_id"]})[0]
        spec_sections = json.loads(task["spec_sections"])

        loaded_sections = ["overview"] + spec_sections
        content = {k: content_json[k] for k in loaded_sections if k in content_json}
    elif params.get("phase"):
        # Load specific phase (hierarchical specs)
        if spec["spec_type"] == "hierarchical":
            phases = content_json.get("phases", [])
            phase_data = next((p for p in phases if p["name"] == params["phase"]), None)

            loaded_sections = ["overview", "architecture", params["phase"]]
            content = {
                "overview": content_json["overview"],
                "architecture": content_json.get("architecture", ""),
                "phase_content": phase_data["content"] if phase_data else ""
            }
        else:
            return {"success": False, "error": "Phase loading only for hierarchical specs"}
    else:
        # Load overview + first phase (default)
        loaded_sections = ["overview"]
        content = {"overview": content_json.get("overview", "")}

    # Calculate context tokens (rough estimate)
    content_str = json.dumps(content)
    context_tokens = len(content_str) // 4  # Rough estimate

    return {
        "success": True,
        "spec_id": spec_id,
        "spec_type": spec["spec_type"],
        "loaded_sections": loaded_sections,
        "content": content,
        "context_tokens": context_tokens,
        "estimated_hours": spec.get("estimated_hours", 0),
        "reuse_components": content_json.get("reuse_components", [])
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| SpecNotFoundError | Spec doesn't exist | Verify spec ID |
| InvalidPhaseError | Phase doesn't exist | Check phase names |
| TaskNotFoundError | Task ID invalid | Verify task ID |

---

### Command: code_developer.update_implementation_status

**Purpose**: Update implementation status (Planned → In Progress → Complete)

**Tables**:
- Write: `specs_task`, `system_audit`
- Read: `specs_task`

**Required Skills**: None

**Input Parameters**:
```yaml
task_id: string          # Required - Task to update
new_status: string       # Required - "pending", "in_progress", "completed", "blocked"
notes: string            # Optional - Status update notes
files_modified: array    # Optional - Files changed
commits: array           # Optional - Commit hashes
```

**Output**:
```json
{
  "success": true,
  "task_id": "TASK-31-1",
  "old_status": "pending",
  "new_status": "in_progress",
  "updated_at": "2025-10-26T10:15:00Z",
  "notification_sent": false
}
```

**Success Criteria**:
- ✅ Status updated in database
- ✅ Audit trail created
- ✅ Notifications sent if status=completed
- ✅ Files tracked
- ✅ Commits linked

**Database Operations**:

```python
def update_implementation_status(db: DomainWrapper, params: dict):
    task_id = params["task_id"]
    new_status = params["new_status"]

    # Get current task
    tasks = db.read("specs_task", {"id": task_id})
    if not tasks:
        return {"success": False, "error": f"Task {task_id} not found"}

    task = tasks[0]
    old_status = task["status"]

    # Update status
    update_data = {
        "id": task_id,
        "status": new_status,
        "updated_at": datetime.now().isoformat()
    }

    if params.get("notes"):
        update_data["notes"] = params["notes"]

    if params.get("files_modified"):
        update_data["files_modified"] = json.dumps(params["files_modified"])

    if params.get("commits"):
        update_data["commits"] = json.dumps(params["commits"])

    if new_status == "completed":
        update_data["completed_at"] = datetime.now().isoformat()

    db.write("specs_task", update_data, action="update")

    # Notify architect if completed (for merge)
    notification_sent = False
    if new_status == "completed":
        db.send_notification("architect", {
            "type": "task_complete",
            "task_id": task_id,
            "message": f"Task {task_id} completed, ready for merge"
        })
        notification_sent = True

    return {
        "success": True,
        "task_id": task_id,
        "old_status": old_status,
        "new_status": new_status,
        "updated_at": datetime.now().isoformat(),
        "notification_sent": notification_sent
    }
```

---

## Command Group 2: Code Operations (4 Commands)

### Command: code_developer.record_commit

**Purpose**: Record a commit to the review queue for code_reviewer analysis

**Tables**:
- Write: `review_commit`, `system_audit`
- Read: `specs_task`

**Required Skills**: None

**Input Parameters**:
```yaml
commit_hash: string      # Required - Git commit hash
task_id: string          # Required - Associated task
message: string          # Required - Commit message
files_changed: array     # Required - Files modified
additions: integer       # Lines added
deletions: integer       # Lines deleted
timestamp: string        # ISO timestamp
```

**Output**:
```json
{
  "success": true,
  "commit_id": "commit-12345",
  "commit_hash": "abc123def",
  "task_id": "TASK-31-1",
  "queued_for_review": true,
  "review_notification_sent": true
}
```

**Success Criteria**:
- ✅ Commit recorded in database
- ✅ Linked to task
- ✅ Queued for code_reviewer
- ✅ Notification sent to code_reviewer
- ✅ Audit trail created

**Database Operations**:

```python
def record_commit(db: DomainWrapper, params: dict):
    commit_data = {
        "commit_hash": params["commit_hash"],
        "task_id": params["task_id"],
        "message": params["message"],
        "files_changed": json.dumps(params["files_changed"]),
        "additions": params.get("additions", 0),
        "deletions": params.get("deletions", 0),
        "timestamp": params.get("timestamp", datetime.now().isoformat()),
        "status": "pending_review",
        "created_by": "code_developer",
        "created_at": datetime.now().isoformat()
    }

    commit_id = db.write("review_commit", commit_data, action="create")

    # Notify code_reviewer
    db.send_notification("code_reviewer", {
        "type": "commit_ready_for_review",
        "commit_id": commit_id,
        "commit_hash": params["commit_hash"],
        "task_id": params["task_id"],
        "message": f"New commit ready for review: {params['commit_hash'][:7]}"
    })

    return {
        "success": True,
        "commit_id": commit_id,
        "commit_hash": params["commit_hash"],
        "task_id": params["task_id"],
        "queued_for_review": True,
        "review_notification_sent": True
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| DuplicateCommitError | Commit already recorded | Skip or update |
| TaskNotFoundError | Invalid task ID | Verify task exists |
| ValidationError | Missing required fields | Provide all params |

**Downstream Effects**:
- code_reviewer detects new commit
- Review queue populated
- Commit linked to task for traceability
- architect can see commit in review summaries

---

### Command: code_developer.complete_implementation

**Purpose**: Mark implementation complete and trigger verification

**Tables**:
- Write: `specs_task`, `roadmap_priority`, `system_audit`
- Read: `specs_task`, `roadmap_priority`

**Required Skills**: `roadmap_database_handling`

**Input Parameters**:
```yaml
task_id: string          # Required - Task completed
priority_id: string      # Required - Associated priority
run_tests: boolean       # Run tests before marking complete (default: true)
request_review: boolean  # Trigger code review (default: true)
```

**Output**:
```json
{
  "success": true,
  "task_id": "TASK-31-1",
  "priority_id": "PRIORITY-28",
  "tests_passed": true,
  "coverage": 92,
  "review_requested": true,
  "notification_sent": true
}
```

**Success Criteria**:
- ✅ Task marked completed
- ✅ Tests run and pass
- ✅ Coverage >90%
- ✅ Code review triggered
- ✅ Notifications sent (architect, project_manager)

**Database Operations**:

```python
def complete_implementation(db: DomainWrapper, params: dict):
    task_id = params["task_id"]
    priority_id = params["priority_id"]

    # Run tests if requested
    tests_passed = True
    coverage = 0

    if params.get("run_tests", True):
        test_result = subprocess.run(
            ["pytest", "--cov=coffee_maker", "--cov-report=json"],
            capture_output=True, text=True
        )
        tests_passed = test_result.returncode == 0

        if tests_passed:
            # Read coverage report
            with open("coverage.json") as f:
                cov_data = json.load(f)
                coverage = cov_data["totals"]["percent_covered"]

        if not tests_passed:
            return {
                "success": False,
                "error": "Tests failed",
                "test_output": test_result.stderr
            }

        if coverage < 90:
            return {
                "success": False,
                "error": f"Coverage too low: {coverage}% (need 90%)",
                "coverage": coverage
            }

    # Mark task complete
    db.write("specs_task", {
        "id": task_id,
        "status": "completed",
        "completed_at": datetime.now().isoformat()
    }, action="update")

    # Request code review if enabled
    review_requested = False
    if params.get("request_review", True):
        db.send_notification("code_reviewer", {
            "type": "implementation_complete",
            "task_id": task_id,
            "priority_id": priority_id,
            "message": f"Implementation complete for {task_id}, please review"
        })
        review_requested = True

    # Notify architect (for merge)
    db.send_notification("architect", {
        "type": "task_complete",
        "task_id": task_id,
        "priority_id": priority_id,
        "tests_passed": tests_passed,
        "coverage": coverage,
        "message": f"Task {task_id} complete with {coverage}% coverage"
    })

    return {
        "success": True,
        "task_id": task_id,
        "priority_id": priority_id,
        "tests_passed": tests_passed,
        "coverage": coverage,
        "review_requested": review_requested,
        "notification_sent": True
    }
```

---

### Command: code_developer.request_code_review

**Purpose**: Explicitly trigger code review process

**Tables**:
- Write: `notifications`
- Read: `review_commit`, `specs_task`

**Required Skills**: None

**Input Parameters**:
```yaml
task_id: string          # Required - Task to review
priority: string         # "low", "medium", "high", "urgent"
focus_areas: array       # Optional - Specific concerns ["security", "performance"]
```

**Output**:
```json
{
  "success": true,
  "task_id": "TASK-31-1",
  "commits_queued": 5,
  "review_request_id": "review-12345",
  "notification_sent": true
}
```

**Success Criteria**:
- ✅ Review request created
- ✅ All commits for task queued
- ✅ code_reviewer notified
- ✅ Priority set

---

### Command: code_developer.create_pull_request

**Purpose**: Create GitHub pull request using gh CLI

**Tables**:
- Write: `system_audit`
- Read: `roadmap_priority`, `specs_specification`

**Required Skills**: None

**Required Tools**: `gh` (GitHub CLI)

**Input Parameters**:
```yaml
priority_id: string      # Required - Priority implemented
branch: string           # Required - Source branch
base_branch: string      # Target branch (default: "main")
title: string            # PR title (auto-generated if not provided)
body: string             # PR description (auto-generated if not provided)
draft: boolean           # Create as draft PR (default: false)
```

**Output**:
```json
{
  "success": true,
  "pr_number": 123,
  "pr_url": "https://github.com/.../pull/123",
  "title": "Implement PRIORITY-28: Feature X",
  "status": "open"
}
```

**Success Criteria**:
- ✅ PR created on GitHub
- ✅ Title and description auto-generated from spec
- ✅ Linked to priority and spec
- ✅ CI checks triggered
- ✅ Audit trail created

**External Tool Usage**:

```bash
# Create PR
gh pr create \
  --title "Implement PRIORITY-28: Feature X" \
  --body "$(cat <<'EOF'
## Summary
- Implemented authentication system
- Added user model and session management
- Tests pass with 92% coverage

## Related
- Priority: PRIORITY-28
- Spec: SPEC-131
- Tasks: TASK-31-1, TASK-31-2, TASK-31-3

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main \
  --head roadmap
```

**Database Operations**:

```python
def create_pull_request(db: DomainWrapper, params: dict):
    priority_id = params["priority_id"]
    branch = params["branch"]
    base_branch = params.get("base_branch", "main")

    # Get priority and spec for context
    priority = db.read("roadmap_priority", {"id": priority_id})[0]
    spec = None
    if priority.get("spec_id"):
        spec = db.read("specs_specification", {"id": priority["spec_id"]})[0]

    # Auto-generate title and body if not provided
    title = params.get("title", f"Implement {priority_id}: {priority['title']}")

    if not params.get("body"):
        # Generate PR description from spec
        body_parts = [
            "## Summary",
            f"- {priority['description']}",
            "",
            "## Related",
            f"- Priority: {priority_id}",
        ]

        if spec:
            body_parts.extend([
                f"- Spec: {spec['id']}",
                f"- Estimated Hours: {spec['estimated_hours']}"
            ])

        body_parts.append("\n🤖 Generated with [Claude Code](https://claude.com/claude-code)")
        body = "\n".join(body_parts)
    else:
        body = params["body"]

    # Create PR using gh CLI
    cmd = [
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--base", base_branch,
        "--head", branch
    ]

    if params.get("draft", False):
        cmd.append("--draft")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "success": False,
            "error": f"Failed to create PR: {result.stderr}"
        }

    # Parse PR URL from output
    pr_url = result.stdout.strip()
    pr_number = int(pr_url.split("/")[-1])

    # Audit log
    db.write("system_audit", {
        "table_name": "github_prs",
        "item_id": f"PR-{pr_number}",
        "action": "create",
        "field_changed": "pr_url",
        "new_value": pr_url,
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": True,
        "pr_number": pr_number,
        "pr_url": pr_url,
        "title": title,
        "status": "open"
    }
```

**Error Handling**:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| GitHubAPIError | Rate limit, auth | Wait, check token |
| BranchNotFoundError | Branch doesn't exist | Verify branch name |
| CLINotFoundError | gh not installed | Install GitHub CLI |

---

## Command Group 3: Quality Assurance (7 Commands)

### Command: code_developer.run_test_suite

**Purpose**: Execute pytest with coverage reporting

**Tables**:
- Write: `metrics_subtask`, `system_audit`

**Required Skills**: None

**Required Tools**: `pytest`

**Input Parameters**:
```yaml
test_path: string        # Optional - Specific test file/directory
coverage_threshold: integer # Minimum coverage (default: 90)
markers: array           # Optional - pytest markers to run
fail_fast: boolean       # Stop on first failure (default: false)
```

**Output**:
```json
{
  "success": true,
  "tests_run": 156,
  "tests_passed": 155,
  "tests_failed": 1,
  "tests_skipped": 0,
  "coverage": 92,
  "duration_seconds": 12.5,
  "failed_tests": [
    {
      "test_name": "test_authentication",
      "error": "AssertionError: Expected 200, got 401"
    }
  ]
}
```

**Success Criteria**:
- ✅ Tests executed
- ✅ Coverage calculated
- ✅ Results recorded in database
- ✅ Failed tests identified
- ✅ Metrics tracked

**External Tool Usage**:

```bash
# Run tests with coverage
pytest --cov=coffee_maker --cov-report=json --cov-report=term -v

# Run specific markers
pytest -m "not slow" --cov=coffee_maker

# Fail fast
pytest -x --cov=coffee_maker
```

**Database Operations**:

```python
def run_test_suite(db: DomainWrapper, params: dict):
    test_path = params.get("test_path", "tests/")
    coverage_threshold = params.get("coverage_threshold", 90)

    # Build pytest command
    cmd = [
        "pytest",
        test_path,
        "--cov=coffee_maker",
        "--cov-report=json",
        "--cov-report=term",
        "-v"
    ]

    if params.get("markers"):
        cmd.extend(["-m", " and ".join(params["markers"])])

    if params.get("fail_fast", False):
        cmd.append("-x")

    # Run tests
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time

    # Parse results
    tests_passed = result.returncode == 0

    # Read coverage
    coverage = 0
    if os.path.exists("coverage.json"):
        with open("coverage.json") as f:
            cov_data = json.load(f)
            coverage = cov_data["totals"]["percent_covered"]

    # Parse test counts from output
    # (simplified - real implementation would parse pytest output)
    tests_run = 156
    tests_failed = 0 if tests_passed else 1
    tests_passed_count = tests_run - tests_failed

    # Record metrics
    db.write("metrics_subtask", {
        "metric_type": "test_run",
        "tests_run": tests_run,
        "tests_passed": tests_passed_count,
        "tests_failed": tests_failed,
        "coverage": coverage,
        "duration_seconds": duration,
        "recorded_by": "code_developer",
        "recorded_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": tests_passed and coverage >= coverage_threshold,
        "tests_run": tests_run,
        "tests_passed": tests_passed_count,
        "tests_failed": tests_failed,
        "tests_skipped": 0,
        "coverage": coverage,
        "duration_seconds": duration,
        "failed_tests": [] if tests_passed else [{"test_name": "unknown", "error": result.stderr}]
    }
```

---

### Command: code_developer.fix_failing_tests

**Purpose**: Analyze and fix failing tests

**Tables**:
- Read: `metrics_subtask`
- Write: `system_audit`

**Required Skills**: `code_forensics`

**Input Parameters**:
```yaml
test_name: string        # Optional - Specific test to fix
auto_fix: boolean        # Attempt automatic fix (default: false)
analyze_only: boolean    # Only analyze, don't fix (default: false)
```

**Output**:
```json
{
  "success": true,
  "tests_analyzed": 3,
  "issues_found": [
    {
      "test_name": "test_authentication",
      "error_type": "AssertionError",
      "root_cause": "Missing token validation",
      "suggested_fix": "Add token validation in auth middleware",
      "auto_fixed": false
    }
  ],
  "fixes_applied": 0
}
```

**Success Criteria**:
- ✅ Failing tests identified
- ✅ Root causes analyzed
- ✅ Fixes suggested
- ✅ Auto-fix applied (if enabled)

---

### Command: code_developer.run_pre_commit_hooks

**Purpose**: Execute pre-commit hooks (black, flake8, mypy, etc.)

**Tables**:
- Write: `system_audit`

**Required Skills**: None

**Required Tools**: `pre-commit`

**Input Parameters**:
```yaml
hooks: array             # Optional - Specific hooks to run
all_files: boolean       # Run on all files (default: false)
show_diff: boolean       # Show diff of changes (default: true)
```

**Output**:
```json
{
  "success": true,
  "hooks_run": 5,
  "hooks_passed": 5,
  "hooks_failed": 0,
  "files_modified": ["coffee_maker/models/user.py"],
  "details": [
    {
      "hook": "black",
      "status": "passed",
      "files_changed": 1
    }
  ]
}
```

**Success Criteria**:
- ✅ All hooks executed
- ✅ Code formatted
- ✅ Linting passed
- ✅ Type checking passed
- ✅ Files modified tracked

**External Tool Usage**:

```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Show diff
pre-commit run --show-diff-on-failure
```

---

### Command: code_developer.implement_bug_fix

**Purpose**: Implement bug fix from bug tracking system

**Tables**:
- Read: `bug_reports` (if exists)
- Write: `review_commit`, `system_audit`

**Required Skills**: `code_forensics`, `bug_tracking_helper`

**Input Parameters**:
```yaml
bug_id: string           # Required - Bug ID to fix
create_test: boolean     # Create regression test (default: true)
priority: string         # "low", "medium", "high", "critical"
```

**Output**:
```json
{
  "success": true,
  "bug_id": "BUG-042",
  "fix_applied": true,
  "test_created": true,
  "commit_hash": "abc123def",
  "files_modified": ["coffee_maker/auth.py", "tests/test_auth.py"]
}
```

**Success Criteria**:
- ✅ Bug identified and analyzed
- ✅ Fix implemented
- ✅ Regression test created
- ✅ Commit recorded
- ✅ Bug status updated

---

### Command: code_developer.track_metrics

**Purpose**: Record implementation metrics (velocity, complexity, time)

**Tables**:
- Write: `metrics_subtask`

**Required Skills**: None

**Input Parameters**:
```yaml
task_id: string          # Required - Task being measured
metric_type: string      # "velocity", "complexity", "time", "lines_of_code"
value: float             # Metric value
unit: string             # "hours", "lines", "points"
notes: string            # Optional - Additional context
```

**Output**:
```json
{
  "success": true,
  "metric_id": "metric-12345",
  "task_id": "TASK-31-1",
  "metric_type": "velocity",
  "value": 8.5,
  "unit": "hours"
}
```

**Success Criteria**:
- ✅ Metric recorded
- ✅ Linked to task
- ✅ Timestamp captured
- ✅ Available for analysis

---

### Command: code_developer.generate_coverage_report

**Purpose**: Generate detailed test coverage report

**Tables**:
- Write: `system_audit`

**Required Skills**: None

**Required Tools**: `pytest`, `coverage`

**Input Parameters**:
```yaml
output_format: string    # "html", "json", "xml", "term" (default: "html")
output_path: string      # Output directory (default: "htmlcov/")
show_missing: boolean    # Show uncovered lines (default: true)
```

**Output**:
```json
{
  "success": true,
  "coverage": 92,
  "output_format": "html",
  "output_path": "htmlcov/index.html",
  "uncovered_lines": 145,
  "modules_analyzed": 42,
  "modules_below_threshold": 2
}
```

**Success Criteria**:
- ✅ Coverage report generated
- ✅ Missing lines identified
- ✅ Report accessible
- ✅ Threshold violations flagged

**External Tool Usage**:

```bash
# Generate HTML report
pytest --cov=coffee_maker --cov-report=html

# Generate JSON report
pytest --cov=coffee_maker --cov-report=json

# Show missing lines
pytest --cov=coffee_maker --cov-report=term-missing
```

---

### Command: code_developer.update_claude_config

**Purpose**: Update .claude/ configuration files (agent definitions, commands, skills)

**Tables**:
- Write: `system_audit`

**Files**:
- Write: `.claude/agents/*.md`, `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`

**Required Skills**: None

**Input Parameters**:
```yaml
config_type: string      # "agent", "command", "skill"
config_name: string      # Name of config to update
updates: object          # Fields to update
backup: boolean          # Create backup before update (default: true)
```

**Output**:
```json
{
  "success": true,
  "config_type": "agent",
  "config_name": "code_developer",
  "file_updated": ".claude/agents/code_developer.md",
  "backup_created": ".claude/agents/code_developer.md.backup"
}
```

**Success Criteria**:
- ✅ Config file updated
- ✅ Backup created
- ✅ Syntax valid
- ✅ Audit trail created

---

## Implementation Tasks

### Task Breakdown (CFR-007 Compliant: <30% context each)

#### TASK-104-1: Work Management Commands (6 hours)

**Scope**:
- Implement `claim_priority` command
- Implement `load_spec` command
- Implement `update_implementation_status` command

**Files**:
- Create: `.claude/commands/agents/code_developer/claim_priority.md`
- Create: `.claude/commands/agents/code_developer/load_spec.md`
- Create: `.claude/commands/agents/code_developer/update_implementation_status.md`
- Create: `coffee_maker/commands/code_developer/work_management.py`

**Tests**:
- Create: `tests/unit/test_code_developer_work_management.py`
- Test priority claiming (atomicity, race conditions)
- Test spec loading (progressive disclosure)
- Test status updates

**Context Size**: ~22% (3 commands + database operations + tests)

**Success Criteria**:
- ✅ Priority claiming prevents concurrent work
- ✅ Spec loading respects context budget
- ✅ Status updates tracked properly

---

#### TASK-104-2: Code Operations Commands (10 hours)

**Scope**:
- Implement `record_commit` command
- Implement `complete_implementation` command
- Implement `request_code_review` command
- Implement `create_pull_request` command

**Files**:
- Create: `.claude/commands/agents/code_developer/record_commit.md`
- Create: `.claude/commands/agents/code_developer/complete_implementation.md`
- Create: `.claude/commands/agents/code_developer/request_code_review.md`
- Create: `.claude/commands/agents/code_developer/create_pull_request.md`
- Create: `coffee_maker/commands/code_developer/code_operations.py`

**Tests**:
- Create: `tests/unit/test_code_developer_code_operations.py`
- Test commit recording
- Test completion workflow (tests, coverage)
- Test review requests
- Test PR creation (mock gh CLI)

**Context Size**: ~28% (4 commands + git/gh integration + tests)

**Success Criteria**:
- ✅ Commits tracked for review
- ✅ Completion requires tests passing
- ✅ PRs auto-generated with context
- ✅ GitHub CLI integration works

---

#### TASK-104-3: Quality Assurance Commands (12 hours)

**Scope**:
- Implement `run_test_suite` command
- Implement `fix_failing_tests` command
- Implement `run_pre_commit_hooks` command
- Implement `implement_bug_fix` command
- Implement `track_metrics` command
- Implement `generate_coverage_report` command
- Implement `update_claude_config` command

**Files**:
- Create: `.claude/commands/agents/code_developer/run_test_suite.md`
- Create: `.claude/commands/agents/code_developer/fix_failing_tests.md`
- Create: `.claude/commands/agents/code_developer/run_pre_commit_hooks.md`
- Create: `.claude/commands/agents/code_developer/implement_bug_fix.md`
- Create: `.claude/commands/agents/code_developer/track_metrics.md`
- Create: `.claude/commands/agents/code_developer/generate_coverage_report.md`
- Create: `.claude/commands/agents/code_developer/update_claude_config.md`
- Create: `coffee_maker/commands/code_developer/quality_assurance.py`

**Tests**:
- Create: `tests/unit/test_code_developer_quality_assurance.py`
- Test test execution and coverage
- Test pre-commit hooks
- Test bug fix workflow
- Test metrics tracking
- Test config updates

**Context Size**: ~29% (7 commands + testing/tooling integration + tests)

**Success Criteria**:
- ✅ Test suite execution reliable
- ✅ Coverage tracking accurate
- ✅ Pre-commit hooks enforced
- ✅ Metrics captured correctly

---

## Total Effort Estimate

| Task | Hours | Complexity | Context % |
|------|-------|------------|-----------|
| TASK-104-1: Work Management | 6 | Medium | 22% |
| TASK-104-2: Code Operations | 10 | High | 28% |
| TASK-104-3: Quality Assurance | 12 | High | 29% |
| **TOTAL** | **28** | **High** | **<30% each** ✅ |

---

## Success Criteria

### Functional
- ✅ All 14 commands implemented
- ✅ Autonomous work execution from database
- ✅ Progressive spec loading (CFR-007)
- ✅ Tests run before completion
- ✅ PRs auto-generated
- ✅ Quality gates enforced

### Technical
- ✅ All unit tests pass (>90% coverage)
- ✅ Context budget <30% per task
- ✅ CFR-013 enforced (git workflow)
- ✅ CFR-014 enforced (database tracing)
- ✅ External tools (pytest, gh, pre-commit) integrated

### Integration
- ✅ Commands load via CommandLoader
- ✅ Permissions enforced (write to review_commit, metrics_subtask)
- ✅ Skills integrate correctly
- ✅ Notifications flow to other agents

---

## Dependencies

### Python Packages
- `pytest` - Test execution (Tier 1 approved)
- `coverage` - Coverage reporting (Tier 1 approved)
- `pre-commit` - Code quality hooks (Tier 1 approved)
- Existing: `sqlite3`, `subprocess`, `json`

### External Tools
- `gh` (GitHub CLI) - Already configured
- `pytest` - Already installed
- `pre-commit` - Already configured

### Existing Infrastructure
- RoadmapDatabase - Work items
- TechnicalSpecSkill - Spec loading
- ImplementationTaskCreator - Task decomposition
- NotificationDatabase - Inter-agent communication

---

## Related Documents

- [SPEC-100: Unified Agent Commands Architecture (Master)](SPEC-100-unified-agent-commands-architecture.md)
- [SPEC-101: Foundation Infrastructure](SPEC-101-foundation-infrastructure.md)
- [SPEC-102: Project Manager Commands](SPEC-102-project-manager-commands.md)
- [SPEC-103: Architect Commands](SPEC-103-architect-commands.md)
- [.claude/agents/code_developer.md](../../../.claude/agents/code_developer.md)
- [CFR-007: Context Budget](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-007)
- [CFR-013: Git Workflow](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-013)
- [CFR-014: Database Tracing](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-014)

---

**Specification Status**: Draft - Ready for Review
**Estimated Effort**: 28 hours
**Complexity**: High
**Context Budget**: All tasks <30% ✅
**Dependencies**: SPEC-101, SPEC-102, SPEC-103
