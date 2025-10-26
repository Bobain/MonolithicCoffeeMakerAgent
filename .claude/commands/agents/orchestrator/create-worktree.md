---
command: orchestrator.create-worktree
agent: orchestrator
action: create_worktree
description: Create git worktree for task isolation (CFR-013)
tables:
  read: [orchestrator_task, roadmap_priority]
  write: [orchestrator_state]
required_tools: [git, database]
cfr_compliance:
  - CFR-013: Git worktree workflow (roadmap-implementation_task-{task_id} branches)
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.create-worktree

## Purpose

Create isolated git worktrees for each task to enable parallel execution without branch conflicts. Per CFR-013:
1. Create worktree with naming: `roadmap-implementation_task-{task_id}`
2. Isolate each task's work to separate directory
3. Track worktree status in database
4. Enable parallel task execution
5. Support sequential merging after completion

## Parameters

```python
parameters = {
    "TASK_ID": "TASK-31-1",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "BASE_BRANCH": "roadmap",
    "WORKTREE_ROOT": "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.worktrees"
}
```

## Git Worktree Workflow (CFR-013)

### Branch Naming Convention

```
Base:    main
Primary: roadmap
Worktree: roadmap-implementation_task-TASK-31-1
Worktree: roadmap-implementation_task-TASK-31-2
Worktree: roadmap-implementation_task-TASK-32-1
```

### Directory Structure

```
project_root/
├── .git/
├── .worktrees/
│   ├── implementation_task-TASK-31-1/   # Worktree for TASK-31-1
│   ├── implementation_task-TASK-31-2/   # Worktree for TASK-31-2
│   └── implementation_task-TASK-32-1/   # Worktree for TASK-32-1
└── coffee_maker/
```

## Worktree Creation Process

### Step 1: Create Branch

```bash
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent

# Create new branch from roadmap
git branch roadmap-implementation_task-TASK-31-1 roadmap
```

### Step 2: Create Worktree

```bash
# Create worktree with new branch
git worktree add \
    .worktrees/implementation_task-TASK-31-1 \
    roadmap-implementation_task-TASK-31-1
```

### Step 3: Verify Worktree

```bash
# List all worktrees
git worktree list

# Expected output:
# /path/to/project                          (bare)
# /path/to/project/.worktrees/implementation_task-TASK-31-1  roadmap-implementation_task-TASK-31-1
```

## Database Operations

### Record Worktree in orchestrator_state

```sql
INSERT INTO orchestrator_state (
    task_id,
    worktree_path,
    branch_name,
    status,
    created_at,
    git_commit_ref,
    orchestrator_instance_id
) VALUES (?, ?, ?, 'created', CURRENT_TIMESTAMP, ?, ?);
```

## Creation Operations

### Operation 1: Create Worktree for Task

```python
invoke_command("create-worktree", {
    "TASK_ID": "TASK-31-1",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "BASE_BRANCH": "roadmap"
})
```

**Output**:
```json
{
    "success": true,
    "task_id": "TASK-31-1",
    "worktree_path": "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.worktrees/implementation_task-TASK-31-1",
    "branch_name": "roadmap-implementation_task-TASK-31-1",
    "status": "created",
    "created_at": "2025-10-26T10:30:00Z",
    "git_commit_ref": "abc123def456",
    "message": "Worktree created successfully"
}
```

### Operation 2: Create Multiple Worktrees

```python
invoke_command("create-worktree", {
    "ACTION": "create_multiple",
    "TASKS": ["TASK-31-1", "TASK-31-2", "TASK-32-1"],
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "create_multiple",
    "worktrees_created": 3,
    "worktrees": [
        {
            "task_id": "TASK-31-1",
            "worktree_path": "/path/to/.worktrees/implementation_task-TASK-31-1",
            "branch_name": "roadmap-implementation_task-TASK-31-1",
            "status": "created"
        },
        {
            "task_id": "TASK-31-2",
            "worktree_path": "/path/to/.worktrees/implementation_task-TASK-31-2",
            "branch_name": "roadmap-implementation_task-TASK-31-2",
            "status": "created"
        },
        {
            "task_id": "TASK-32-1",
            "worktree_path": "/path/to/.worktrees/implementation_task-TASK-32-1",
            "branch_name": "roadmap-implementation_task-TASK-32-1",
            "status": "created"
        }
    ],
    "timestamp": "2025-10-26T10:30:05Z"
}
```

## Worktree Isolation Benefits

| Aspect | Single Repo | With Worktrees |
|--------|-----------|-----------------|
| Parallel work | Conflicts | Safe |
| Branch switches | Frequent | Avoided |
| Merge conflicts | Common | Reduced |
| CI/CD runs | Blocked | Parallel |
| Development speed | Sequential | Parallel |

## Success Criteria

1. Branch created from correct base (roadmap)
2. Worktree created at correct path
3. Working directory initialized
4. Database record created
5. Worktree is usable (verified with git status)
6. Naming follows CFR-013 convention

## Error Handling

```json
{
    "success": false,
    "error": "branch_exists",
    "message": "Branch roadmap-implementation_task-TASK-31-1 already exists",
    "task_id": "TASK-31-1",
    "solution": "Use merge-completed-work to clean up old worktree first"
}
```

## Possible Errors

- `branch_exists`: Branch name already taken (orphaned from previous run)
- `worktree_exists`: Worktree path already exists
- `git_error`: Git command failed (permission, corruption)
- `disk_full`: Insufficient disk space
- `invalid_base_branch`: Base branch doesn't exist

## Related Commands

- merge-completed-work.md (merges and cleans up)
- cleanup-worktrees.md (removes completed worktrees)
- spawn-agent-session.md (agents work in worktrees)
