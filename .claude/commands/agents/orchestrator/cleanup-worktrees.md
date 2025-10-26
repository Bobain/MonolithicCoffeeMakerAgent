---
command: orchestrator.cleanup-worktrees
agent: orchestrator
action: cleanup_worktrees
description: Remove completed worktrees and branches
tables:
  read: [orchestrator_state]
  write: [orchestrator_state]
required_tools: [git, filesystem]
cfr_compliance:
  - CFR-013: Git worktree cleanup after merge
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.cleanup-worktrees

## Purpose

Clean up worktrees and branches after successful merge:
1. Verify worktree is merged to roadmap
2. Remove git worktree
3. Delete worktree branch
4. Free up disk space
5. Update database with cleanup status
6. Verify clean state

## Parameters

```python
parameters = {
    "TASK_ID": "TASK-31-1",
    "FORCE_CLEANUP": False,         # Skip verification if True
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "VERIFY_MERGE": True            # Verify merged before cleanup
}
```

## Cleanup Process

### Step 1: Verify Merge Status

```sql
SELECT
    task_id,
    status,
    worktree_path,
    branch_name,
    merged_at
FROM orchestrator_state
WHERE task_id = ? AND status = 'merged';
```

### Step 2: Remove Worktree

```bash
cd /path/to/project

# Remove worktree (safe deletion)
git worktree remove .worktrees/implementation_task-TASK-31-1

# Expected output:
# Removing worktrees/implementation_task-TASK-31-1
```

### Step 3: Delete Branch

```bash
# Delete worktree branch from main repo
git branch -d roadmap-implementation_task-TASK-31-1

# Alternative: Force delete if not fully merged
# git branch -D roadmap-implementation_task-TASK-31-1
```

### Step 4: Clean Reflog

```bash
# Clean reflog to prevent recovery of deleted branch
git reflog expire --expire-unreachable=now --all
git gc --prune=now
```

### Step 5: Verify Cleanup

```bash
# List remaining worktrees (should not include removed one)
git worktree list

# List branches (should not include removed one)
git branch | grep roadmap-implementation_task

# Verify disk space
du -sh .worktrees/
```

## Database Operations

### Update orchestrator_state

```sql
UPDATE orchestrator_state
SET status = 'cleaned',
    cleaned_at = CURRENT_TIMESTAMP,
    worktree_path = NULL
WHERE task_id = ?;
```

## Cleanup Operations

### Operation 1: Cleanup Specific Worktree

```python
invoke_command("cleanup-worktrees", {
    "TASK_ID": "TASK-31-1",
    "VERIFY_MERGE": True,
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "task_id": "TASK-31-1",
    "action": "cleanup",
    "worktree_path": "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.worktrees/implementation_task-TASK-31-1",
    "branch_name": "roadmap-implementation_task-TASK-31-1",
    "status": "cleaned",
    "disk_space_freed_mb": 125.4,
    "cleaned_at": "2025-10-26T10:50:00Z",
    "message": "Worktree cleaned successfully"
}
```

### Operation 2: Cleanup Multiple Worktrees

```python
invoke_command("cleanup-worktrees", {
    "ACTION": "cleanup_all",
    "STATUS_FILTER": "merged",  # Only cleanup merged worktrees
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "cleanup_all",
    "worktrees_cleaned": 3,
    "worktrees": [
        {
            "task_id": "TASK-31-1",
            "status": "cleaned",
            "disk_space_freed_mb": 125.4
        },
        {
            "task_id": "TASK-31-2",
            "status": "cleaned",
            "disk_space_freed_mb": 98.7
        },
        {
            "task_id": "TASK-32-1",
            "status": "cleaned",
            "disk_space_freed_mb": 112.3
        }
    ],
    "total_disk_space_freed_mb": 336.4,
    "cleaned_at": "2025-10-26T10:50:05Z"
}
```

### Operation 3: List Cleanup Candidates

```python
invoke_command("cleanup-worktrees", {
    "ACTION": "list_candidates",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "list_candidates",
    "candidates_count": 2,
    "candidates": [
        {
            "task_id": "TASK-31-1",
            "worktree_path": "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.worktrees/implementation_task-TASK-31-1",
            "branch_name": "roadmap-implementation_task-TASK-31-1",
            "status": "merged",
            "disk_space_mb": 125.4,
            "merged_at": "2025-10-26T10:45:00Z",
            "ready_for_cleanup": true
        },
        {
            "task_id": "TASK-32-1",
            "status": "running",
            "ready_for_cleanup": false,
            "reason": "Not yet merged"
        }
    ]
}
```

## Cleanup Safety Checks

| Check | Purpose | Action on Fail |
|-------|---------|----------------|
| Merge verified | Ensure work is merged | Skip cleanup |
| Branch exists | Ensure branch exists | Note and continue |
| Worktree exists | Ensure worktree exists | Skip removal |
| No uncommitted | Verify clean state | Abort cleanup |
| Disk space | Monitor cleanup progress | Report freed |

## Disk Space Management

```
Before cleanup:
  .worktrees/ = 500 MB (3 worktrees × ~167 MB)

After cleanup of 3 worktrees:
  .worktrees/ = 0 MB (reclaimed 500 MB)
```

## Success Criteria

1. Worktree status is 'merged'
2. Git worktree removed successfully
3. Git branch deleted successfully
4. Database updated with cleanup status
5. Disk space freed
6. No dangling branches remain

## Error Handling

```json
{
    "success": false,
    "error": "not_merged",
    "message": "Worktree not merged to roadmap, cannot cleanup",
    "task_id": "TASK-31-1",
    "status": "running",
    "solution": "Complete merge-completed-work first"
}
```

## Possible Errors

- `not_merged`: Worktree hasn't been merged yet
- `worktree_not_found`: Worktree directory doesn't exist
- `branch_not_found`: Branch doesn't exist
- `uncommitted_changes`: Worktree has dirty state
- `cleanup_failed`: Git command failed
- `still_in_use`: Worktree is checked out elsewhere

## Related Commands

- create-worktree.md (creates worktrees)
- merge-completed-work.md (merges before cleanup)
- orchestrator.py (calls cleanup after merge)
