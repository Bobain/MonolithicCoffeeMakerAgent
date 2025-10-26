---
command: code_developer.update_implementation_status
agent: code_developer
action: update_implementation_status
tables:
  write: [specs_task, system_audit]
  read: [specs_task]
required_skills: []
required_tools: [database]
---

# Command: code_developer.update_implementation_status

## Purpose
Update implementation status as work progresses (Planned → In Progress → Complete → Blocked).

## Input Parameters

```yaml
task_id: string          # Required - Task to update
new_status: string       # Required - "pending", "in_progress", "completed", "blocked"
notes: string            # Optional - Status update notes
files_modified: array    # Optional - Files changed
commits: array           # Optional - Commit hashes
```

## Database Operations

### 1. Get Current Task
```python
from datetime import datetime
import json

def update_implementation_status(db: DomainWrapper, params: dict):
    task_id = params["task_id"]
    new_status = params["new_status"]

    # Get current task
    tasks = db.read("specs_task", {"id": task_id})
    if not tasks:
        return {"success": False, "error": f"Task {task_id} not found"}

    task = tasks[0]
    old_status = task.get("status", "unknown")
```

### 2. Validate Status Transition
```python
    # Validate status transitions
    valid_statuses = ["pending", "in_progress", "completed", "blocked"]
    if new_status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status: {new_status}",
            "valid_statuses": valid_statuses
        }

    # Prevent invalid transitions
    if old_status == "completed" and new_status != "blocked":
        return {
            "success": False,
            "error": "Cannot change status of completed task"
        }
```

### 3. Update Task Status
```python
    update_data = {
        "id": task_id,
        "status": new_status,
        "updated_at": datetime.now().isoformat()
    }

    # Add optional fields
    if params.get("notes"):
        update_data["notes"] = params["notes"]

    if params.get("files_modified"):
        update_data["files_modified"] = json.dumps(params["files_modified"])

    if params.get("commits"):
        update_data["commits"] = json.dumps(params["commits"])

    # Set completion timestamp
    if new_status == "completed":
        update_data["completed_at"] = datetime.now().isoformat()

    db.write("specs_task", update_data, action="update")
```

### 4. Create Audit Trail
```python
    db.write("system_audit", {
        "table_name": "specs_task",
        "item_id": task_id,
        "action": "status_update",
        "field_changed": "status",
        "old_value": old_status,
        "new_value": new_status,
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")
```

### 5. Send Notifications
```python
    # Notify architect if completed (for merge)
    notification_sent = False
    if new_status == "completed":
        db.send_notification("architect", {
            "type": "task_complete",
            "task_id": task_id,
            "message": f"Task {task_id} completed, ready for merge",
            "notes": params.get("notes", "")
        })
        notification_sent = True

    # Notify orchestrator if blocked
    if new_status == "blocked":
        db.send_notification("orchestrator", {
            "type": "task_blocked",
            "task_id": task_id,
            "message": f"Task {task_id} is blocked",
            "notes": params.get("notes", "")
        })

    return {
        "success": True,
        "task_id": task_id,
        "old_status": old_status,
        "new_status": new_status,
        "updated_at": datetime.now().isoformat(),
        "notification_sent": notification_sent
    }
```

## Output

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

## Success Criteria

- ✅ Status updated in database
- ✅ Audit trail created
- ✅ Notifications sent if status=completed
- ✅ Files tracked
- ✅ Commits linked

## Status Workflow

```
pending → in_progress → completed
          ↓
          blocked (can return to in_progress)
```

## Valid Statuses

| Status | Meaning | Notifications |
|--------|---------|---------------|
| pending | Task not started | None |
| in_progress | Currently implementing | None |
| completed | Implementation finished | architect (merge) |
| blocked | Task blocked, needs help | orchestrator (escalation) |

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| TaskNotFoundError | Task doesn't exist | Verify task ID |
| InvalidStatusError | Unknown status | Use valid status |
| InvalidTransitionError | Can't transition from current status | Contact architect |
