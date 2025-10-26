---
command: code_developer.request_code_review
agent: code_developer
action: request_code_review
tables:
  write: [notifications, system_audit]
  read: [review_commit, specs_task]
required_skills: []
required_tools: [database]
---

# Command: code_developer.request_code_review

## Purpose
Explicitly trigger code review process for a task and all associated commits.

## Input Parameters

```yaml
task_id: string          # Required - Task to review
priority: string         # "low", "medium", "high", "urgent" (default: "high")
focus_areas: array       # Optional - Specific concerns ["security", "performance", "testing"]
```

## Database Operations

### 1. Get Task and Commits
```python
from datetime import datetime
import json

def request_code_review(db: DomainWrapper, params: dict):
    task_id = params["task_id"]
    priority = params.get("priority", "high")

    # Get task
    tasks = db.read("specs_task", {"id": task_id})
    if not tasks:
        return {"success": False, "error": f"Task {task_id} not found"}

    task = tasks[0]

    # Get all commits for this task
    commits = db.read("review_commit", {"task_id": task_id})
    if not commits:
        commits = []
```

### 2. Validate Priority
```python
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        return {
            "success": False,
            "error": f"Invalid priority: {priority}",
            "valid_priorities": valid_priorities
        }
```

### 3. Create Review Request
```python
    # Create review request record
    review_request = {
        "task_id": task_id,
        "priority": priority,
        "focus_areas": json.dumps(params.get("focus_areas", [])),
        "requested_by": "code_developer",
        "requested_at": datetime.now().isoformat(),
        "status": "pending",
        "commits_count": len(commits)
    }

    review_request_id = db.write(
        "code_review_requests",  # If table exists
        review_request,
        action="create"
    ) if "code_review_requests" in db.list_tables() else f"review-{task_id}"
```

### 4. Notify Code Reviewer
```python
    # Build notification message with focus areas
    focus_areas_str = ""
    if params.get("focus_areas"):
        focus_areas_str = f"\n\nFocus areas:\n" + "\n".join(
            f"- {area}" for area in params["focus_areas"]
        )

    db.send_notification("code_reviewer", {
        "type": "code_review_requested",
        "review_request_id": review_request_id,
        "task_id": task_id,
        "priority": priority,
        "commits_to_review": len(commits),
        "focus_areas": params.get("focus_areas", []),
        "message": f"Code review requested for {task_id} ({priority} priority)",
        "details": f"Task: {task_id}\nCommits: {len(commits)}{focus_areas_str}",
        "priority": priority
    })
```

### 5. Audit Trail
```python
    db.write("system_audit", {
        "table_name": "specs_task",
        "item_id": task_id,
        "action": "review_requested",
        "field_changed": "review_status",
        "new_value": "pending_review",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": True,
        "task_id": task_id,
        "review_request_id": review_request_id,
        "commits_queued": len(commits),
        "priority": priority,
        "notification_sent": True
    }
```

## Output

```json
{
  "success": true,
  "task_id": "TASK-31-1",
  "review_request_id": "review-12345",
  "commits_queued": 5,
  "priority": "high",
  "notification_sent": true
}
```

## Success Criteria

- ✅ Review request created
- ✅ All commits for task queued
- ✅ code_reviewer notified with priority
- ✅ Focus areas communicated
- ✅ Audit trail created

## Priority Levels

| Priority | Use Case | Response Time |
|----------|----------|---------------|
| low | Documentation, minor fixes | 24+ hours |
| medium | Standard feature | 8-12 hours |
| high | Important feature, bug fix | 2-4 hours |
| urgent | Critical bug, blocker | 30 minutes |

## Focus Areas

Code_developer can specify focus areas to guide code_reviewer:

- **security** - Review security implications, vulnerabilities
- **performance** - Check for performance issues, optimizations
- **testing** - Verify test coverage, test quality
- **architecture** - Validate design patterns, structure
- **documentation** - Check docs, comments, API docs
- **compatibility** - Check backward compatibility, migrations

## Example: Request Review with Focus Areas

```python
request_code_review(db, {
    "task_id": "TASK-31-1",
    "priority": "high",
    "focus_areas": ["security", "performance", "testing"]
})
# Notifies code_reviewer to focus on these areas
```

## Code Review Workflow

```
1. code_developer completes implementation
2. code_developer calls request_code_review
3. code_reviewer receives notification with priority
4. code_reviewer reviews all commits for task
5. code_reviewer provides feedback or approves
6. code_developer makes changes if needed
7. architect merges when approved
```

## Integration with Code Reviewer

After receiving notification:
- code_reviewer retrieves all `review_commit` records for task
- code_reviewer analyzes code against spec requirements
- code_reviewer checks focus areas specified
- code_reviewer provides feedback or approval
- code_reviewer updates commit status

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| TaskNotFoundError | Task doesn't exist | Verify task ID |
| InvalidPriorityError | Unknown priority | Use valid priority |
| NotificationError | Failed to notify | Check notification system |
