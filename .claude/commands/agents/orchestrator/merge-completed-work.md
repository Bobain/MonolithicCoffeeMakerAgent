---
command: orchestrator.merge-completed-work
agent: orchestrator
action: merge_completed_work
description: Merge task branch to roadmap sequentially (CFR-013)
tables:
  read: [orchestrator_state, orchestrator_task]
  write: [orchestrator_state]
required_tools: [git, database]
cfr_compliance:
  - CFR-013: Git worktree workflow (sequential merge, roadmap branch only)
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.merge-completed-work

## Purpose

Merge completed task branches back to roadmap sequentially to ensure clean integration:
1. Verify task is completed
2. Test merge compatibility
3. Perform merge into roadmap (sequential, not parallel)
4. Resolve any conflicts
5. Update database with merge status
6. Clean up worktree (prepare for cleanup-worktrees)

Per CFR-013: Merge is SEQUENTIAL. Each task must complete merge before next task starts.

## Parameters

```python
parameters = {
    "TASK_ID": "TASK-31-1",
    "MERGE_STRATEGY": "recursive",  # "recursive" or "ours"
    "RESOLVE_CONFLICTS": True,      # Auto-resolve if possible
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "FORCE_MERGE": False            # Force merge even if conflicts
}
```

## Merge Process

### Step 1: Verify Task Completion

```sql
SELECT
    task_id,
    status,
    assigned_agent,
    completed_at
FROM orchestrator_task
WHERE task_id = ? AND status = 'completed';
```

### Step 2: Get Worktree Info

```sql
SELECT
    worktree_path,
    branch_name,
    git_commit_ref
FROM orchestrator_state
WHERE task_id = ?;
```

### Step 3: Test Merge (Dry Run)

```bash
cd /path/to/project

# Check if merge would succeed
git merge --no-commit --no-ff roadmap-implementation_task-TASK-31-1 --dry-run

# Abort dry run
git merge --abort
```

### Step 4: Perform Merge

```bash
# Switch to roadmap (main branch)
git checkout roadmap

# Merge from worktree branch
git merge --no-ff \
    -m "Merge TASK-31-1 from roadmap-implementation_task-TASK-31-1" \
    roadmap-implementation_task-TASK-31-1

# If conflicts occur, resolve them
# git add <resolved_files>
# git commit
```

### Step 5: Verify Merge

```bash
# Verify merge was successful
git log --oneline -n 5

# Check that all files are committed
git status
```

## Database Updates

### Record Merge in orchestrator_state

```sql
UPDATE orchestrator_state
SET status = 'merged',
    merged_at = CURRENT_TIMESTAMP,
    merge_commit_ref = ?
WHERE task_id = ?;
```

### Update orchestrator_task

```sql
UPDATE orchestrator_task
SET status = 'merged',
    completed_at = CURRENT_TIMESTAMP
WHERE task_id = ?;
```

## Merge Operations

### Operation 1: Merge Specific Task

```python
invoke_command("merge-completed-work", {
    "TASK_ID": "TASK-31-1",
    "MERGE_STRATEGY": "recursive",
    "RESOLVE_CONFLICTS": True,
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output (Successful)**:
```json
{
    "success": true,
    "task_id": "TASK-31-1",
    "action": "merge",
    "branch_name": "roadmap-implementation_task-TASK-31-1",
    "merge_strategy": "recursive",
    "conflicts": 0,
    "files_changed": 23,
    "insertions": 1456,
    "deletions": 89,
    "merge_commit": "merge123abc",
    "merged_at": "2025-10-26T10:45:00Z",
    "message": "Merge completed successfully"
}
```

**Output (Conflicts)**:
```json
{
    "success": false,
    "error": "merge_conflicts",
    "task_id": "TASK-31-1",
    "branch_name": "roadmap-implementation_task-TASK-31-1",
    "conflicts_count": 3,
    "conflicted_files": [
        "coffee_maker/models/database.py",
        "tests/test_database.py",
        "docs/ROADMAP.md"
    ],
    "message": "Merge has conflicts, manual resolution required"
}
```

### Operation 2: Merge with Conflict Resolution

```python
invoke_command("merge-completed-work", {
    "TASK_ID": "TASK-31-1",
    "ACTION": "resolve_conflicts",
    "CONFLICT_STRATEGY": "ours",  # Accept our changes
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "task_id": "TASK-31-1",
    "action": "resolve_conflicts",
    "conflicts_resolved": 3,
    "strategy": "ours",
    "files_resolved": [
        "coffee_maker/models/database.py",
        "tests/test_database.py",
        "docs/ROADMAP.md"
    ],
    "merge_commit": "merge123abc",
    "message": "Conflicts resolved using 'ours' strategy"
}
```

### Operation 3: Merge Queue Status

```python
invoke_command("merge-completed-work", {
    "ACTION": "status",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "status",
    "merge_queue": [
        {
            "task_id": "TASK-31-1",
            "status": "merged",
            "merge_commit": "merge123abc",
            "position": 1
        },
        {
            "task_id": "TASK-31-2",
            "status": "completed_awaiting_merge",
            "position": 2
        },
        {
            "task_id": "TASK-32-1",
            "status": "completed_awaiting_merge",
            "position": 3
        }
    ],
    "total_in_queue": 3,
    "next_to_merge": "TASK-31-2"
}
```

## Conflict Resolution Strategies

| Strategy | Use Case | Behavior |
|----------|----------|----------|
| recursive | Default | Git's smart merge |
| ours | Our changes are correct | Keep our version |
| theirs | Their changes are correct | Accept their version |
| abort | Conflicts are severe | Stop, require manual fix |

## Merge Sequencing (CFR-013)

```
TASK-31-1 merges to roadmap (SEQUENTIAL)
    ↓
TASK-31-2 can merge (after TASK-31-1 completes)
    ↓
TASK-32-1 can merge (after TASK-31-2 completes)

NOT PARALLEL: Only one merge at a time
```

## Success Criteria

1. Task status is 'completed'
2. Dry run succeeds (or conflicts are solvable)
3. Merge commits to roadmap
4. orchestrator_state updated with merge status
5. No uncommitted changes remain
6. Merge commit message is clear

## Error Handling

```json
{
    "success": false,
    "error": "task_not_completed",
    "message": "Task TASK-31-1 is not completed, cannot merge",
    "task_id": "TASK-31-1",
    "current_status": "running"
}
```

## Possible Errors

- `task_not_completed`: Task still in progress
- `merge_conflicts`: Unresolvable conflicts
- `branch_not_found`: Worktree branch deleted
- `git_error`: Git command failed
- `dirty_working_directory`: Uncommitted changes exist
- `merge_already_done`: Already merged

## Related Commands

- create-worktree.md (creates branches to merge)
- cleanup-worktrees.md (removes merged worktrees)
- spawn-agent-session.md (agents create commits to merge)
