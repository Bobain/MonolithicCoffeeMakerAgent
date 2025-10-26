---
command: code_developer.record_commit
agent: code_developer
action: record_commit
tables:
  write: [review_commit, system_audit]
  read: [specs_task]
required_skills: []
required_tools: [database, git]
---

# Command: code_developer.record_commit

## Purpose
Record a commit to the review queue for code_reviewer analysis and tracking.

## Input Parameters

```yaml
commit_hash: string      # Required - Git commit hash (full or short)
task_id: string          # Required - Associated task
message: string          # Required - Commit message
files_changed: array     # Required - Files modified
additions: integer       # Lines added
deletions: integer       # Lines deleted
timestamp: string        # ISO timestamp (auto if not provided)
```

## Database Operations

### 1. Prepare Commit Record
```python
from datetime import datetime
import json

def record_commit(db: DomainWrapper, params: dict):
    commit_hash = params["commit_hash"]
    task_id = params["task_id"]

    # Prepare commit data
    commit_data = {
        "commit_hash": commit_hash,
        "task_id": task_id,
        "message": params["message"],
        "files_changed": json.dumps(params["files_changed"]),
        "additions": params.get("additions", 0),
        "deletions": params.get("deletions", 0),
        "timestamp": params.get("timestamp", datetime.now().isoformat()),
        "status": "pending_review",
        "created_by": "code_developer",
        "created_at": datetime.now().isoformat()
    }
```

### 2. Write to Review Queue
```python
    # Store commit for code_reviewer
    commit_id = db.write("review_commit", commit_data, action="create")
    if not commit_id:
        return {
            "success": False,
            "error": "Failed to create commit record"
        }
```

### 3. Audit Trail
```python
    # Create audit record
    db.write("system_audit", {
        "table_name": "review_commit",
        "item_id": commit_id,
        "action": "create",
        "field_changed": "status",
        "new_value": "pending_review",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")
```

### 4. Notify Code Reviewer
```python
    # Notify code_reviewer of new commit
    db.send_notification("code_reviewer", {
        "type": "commit_ready_for_review",
        "commit_id": commit_id,
        "commit_hash": commit_hash,
        "task_id": task_id,
        "message": f"New commit ready for review: {commit_hash[:7]}",
        "files_changed": len(params["files_changed"]),
        "additions": params.get("additions", 0),
        "deletions": params.get("deletions", 0)
    })

    return {
        "success": True,
        "commit_id": commit_id,
        "commit_hash": commit_hash,
        "task_id": task_id,
        "queued_for_review": True,
        "review_notification_sent": True
    }
```

## Output

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

## Success Criteria

- ✅ Commit recorded in database
- ✅ Linked to task
- ✅ Queued for code_reviewer
- ✅ Notification sent to code_reviewer
- ✅ Audit trail created

## Review Queue Workflow

1. code_developer commits code
2. code_developer records commit with `record_commit`
3. Commit stored in `review_commit` table with `pending_review` status
4. code_reviewer detects new commit
5. code_reviewer analyzes commit against spec
6. code_reviewer marks as `reviewed` with feedback
7. architect merges commit if approved

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| DuplicateCommitError | Commit already recorded | Skip or update |
| TaskNotFoundError | Invalid task ID | Verify task exists |
| ValidationError | Missing required fields | Provide all params |
| DatabaseError | Write failed | Check database connection |

## Downstream Effects

- code_reviewer detects new commit
- Review queue populated
- Commit linked to task for traceability
- architect can see commit in review summaries
- Metrics tracked from commit data

## Integration with Git

```bash
# After committing code
git log -1 --format="%H %s" > /tmp/last_commit.txt

# Parse output and call record_commit
commit_hash=$(git log -1 --format="%H")
commit_message=$(git log -1 --format="%s")
files_changed=$(git diff-tree --no-commit-id --name-only -r $commit_hash)

# Record in code_developer
record_commit(db, {
    "commit_hash": commit_hash,
    "task_id": "TASK-31-1",
    "message": commit_message,
    "files_changed": files_changed,
    "additions": additions,
    "deletions": deletions
})
```
