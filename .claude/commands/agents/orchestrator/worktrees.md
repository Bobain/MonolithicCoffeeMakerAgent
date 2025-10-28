# worktrees

## Purpose
Manage git worktrees for parallel task execution (CFR-013): create isolated branches, track worktree usage, cleanup completed worktrees.

## Parameters
```yaml
action: str  # Required: "create" | "list" | "cleanup" | "merge"
task_id: str = None  # Required for create/merge
worktree_path: str = None  # Required for cleanup
force_cleanup: bool = false  # Remove even if uncommitted changes
```

## Workflow
1. Execute action:
   - **create**: Create `roadmap-implementation_task-{task_id}` branch + worktree
   - **list**: Show all active worktrees
   - **cleanup**: Remove worktree and branch after merge
   - **merge**: Merge task branch → roadmap (architect only)
2. Update orchestrator_task with worktree info
3. Track in git_worktree_tracker table
4. Return WorktreesResult

## Database Operations
```sql
-- Track worktree creation
INSERT INTO git_worktree_tracker (
    worktree_id, task_id, branch_name, worktree_path,
    created_at, status
) VALUES (?, ?, ?, ?, datetime('now'), 'active')

-- Update worktree status
UPDATE git_worktree_tracker
SET status = ?, completed_at = datetime('now')
WHERE worktree_id = ?

-- Link to orchestrator task
UPDATE orchestrator_task
SET worktree_path = ?, branch_name = ?
WHERE task_id = ?
```

## Git Commands
```bash
# Create worktree
git worktree add ../worktrees/task-{task_id} -b roadmap-implementation_task-{task_id} roadmap

# List worktrees
git worktree list

# Merge to roadmap (architect only)
git checkout roadmap
git merge --no-ff roadmap-implementation_task-{task_id} -m "merge: Complete {task_id}"

# Cleanup worktree
git worktree remove ../worktrees/task-{task_id}
git branch -d roadmap-implementation_task-{task_id}
```

## Result Object
```python
@dataclass
class WorktreesResult:
    action: str
    worktree_path: str  # For create action
    branch_name: str  # For create action
    active_worktrees: List[dict]  # For list action
    cleaned_up: int  # For cleanup action
    status: str  # "success" | "failed"
```

## CFR-013 Compliance
- **Branch naming**: `roadmap-implementation_task-{task_id}`
- **One worktree per task**: Isolated environments
- **Sequential merge**: architect merges after each task completion
- **Parallel across groups**: Different task groups can work simultaneously
- **Cleanup required**: Remove worktree + branch after merge

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| WorktreeExists | Duplicate worktree | Use existing or cleanup first |
| BranchExists | Duplicate branch | Delete old branch or use new name |
| MergeConflict | Code conflicts | Resolve manually |
| CleanupFailed | Uncommitted changes | Use force_cleanup=true |

## Example
```python
result = worktrees(action="create", task_id="TASK-8-1")
# WorktreesResult(
#   action="create",
#   worktree_path="../worktrees/task-TASK-8-1",
#   branch_name="roadmap-implementation_task-TASK-8-1",
#   active_worktrees=[],
#   cleaned_up=0,
#   status="success"
# )
```

## Related Commands
- assign() - Creates tasks that need worktrees
- agents() - Monitors agents working in worktrees

---
Estimated: 65 lines | Context: ~4% | Examples: worktrees_examples.md
