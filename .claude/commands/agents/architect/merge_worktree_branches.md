---
command: architect.merge_worktree_branches
agent: architect
action: merge_worktree_branches
data_domain: shared_governance
write_tables: [system_audit]
read_tables: [dev_implementation_tasks]
required_skills: [git_workflow_automation]
---

# Command: architect.merge_worktree_branches

## Purpose
Merge completed work from roadmap-implementation_task-* worktree branches back to the main roadmap branch (CFR-013 compliance).

## Input Parameters
- **worktree_branch**: string (required) - Worktree branch to merge (e.g., "roadmap-implementation_task-TASK-31-1")
- **task_id**: string (required) - Associated task ID for validation (e.g., "TASK-31-1")
- **run_tests**: boolean (optional, default: true) - Run tests before merge
- **resolve_conflicts**: boolean (optional, default: false) - Auto-resolve conflicts
- **force_merge**: boolean (optional, default: false) - Force merge even if tests fail

## External Tool Usage

```bash
# Validate branch exists
git branch -a | grep {worktree_branch}

# Switch to roadmap
git checkout roadmap

# Pull latest
git pull origin roadmap

# Merge with --no-ff (creates merge commit)
git merge {worktree_branch} --no-ff -m "{merge_message}"

# Run tests
pytest

# Push to remote
git push origin roadmap

# Get merge commit hash
git rev-parse HEAD
```

## Required Skills

### git_workflow_automation
- Safely merges branches
- Handles conflict resolution
- Validates test passing
- Creates proper merge commits

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to git repository

2. **Load Required Skills**
   ```python
   git_skill = load_skill(SkillNames.GIT_WORKFLOW_AUTOMATION)
   ```

3. **Validate Worktree Branch**
   - Verify branch exists in repository
   - Confirm branch matches pattern: roadmap-implementation_task-*
   - If not found, return BranchNotFoundError

4. **Validate Task**
   - Query dev_implementation_tasks for task_id
   - If not found, return TaskNotFoundError
   - Verify task.task_group_id matches worktree_branch
   - Check task status is "completed"
   - If not completed, return TaskNotCompleteError

5. **Switch to Roadmap Branch**
   ```bash
   git checkout roadmap
   git pull origin roadmap
   ```

6. **Check for Conflicts** (dry run)
   ```bash
   git merge --no-commit --no-ff {worktree_branch}
   git merge --abort
   ```

7. **Merge Branch**
   ```bash
   merge_msg = f"""Merge parallel work from {worktree_branch}: {task_id}

Features:
- {task.scope_description}

Task Status: Completed
Tests: {'Passed' if run_tests else 'Skipped'}
Ready for integration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
   """

   git merge {worktree_branch} --no-ff -m "{merge_msg}"
   ```

8. **Handle Merge Conflicts** (if any)
   - If resolve_conflicts=false:
     - Abort merge
     - Return error with list of conflicting files
   - If resolve_conflicts=true:
     - Auto-resolve safe conflicts (usually ROADMAP.md)
     - Add resolved files: git add .
     - Complete merge: git commit --no-edit

9. **Run Tests** (if run_tests=true)
   ```bash
   pytest
   ```
   - If tests fail and force_merge=false:
     - Abort merge: git merge --abort
     - Return error with test failures
   - If tests fail and force_merge=true:
     - Continue (force merge despite failures)
     - Log warning

10. **Push to Remote**
    ```bash
    git push origin roadmap
    ```

11. **Get Merge Commit**
    ```bash
    git rev-parse HEAD  # Gets merge commit hash
    ```

12. **Notify Orchestrator**
    ```python
    notify('orchestrator', {
        'type': 'merge_complete',
        'worktree_branch': worktree_branch,
        'task_id': task_id,
        'merge_commit': merge_commit,
        'message': f'Merge complete for {worktree_branch}, ready for cleanup'
    })
    ```

13. **Create Audit Trail**
    - Record merge in system_audit
    - Item: task_id
    - Action: merge
    - New value: merge commit hash
    - Notes: worktree branch, test results, conflict resolution

14. **Return Merge Results**
    - Confirm merge succeeded
    - Return merge commit hash
    - Return test status
    - Confirm notification sent

## Error Handling

### BranchNotFoundError
- **Cause**: Worktree branch doesn't exist
- **Response**: Return error with branch name
- **Recovery**: Verify branch name and existence

### TaskNotFoundError
- **Cause**: Task doesn't exist in database
- **Response**: Return error with task_id
- **Recovery**: Verify task_id is correct

### TaskNotCompleteError
- **Cause**: Task is not in "completed" status
- **Response**: Return error with current task status
- **Recovery**: Complete task first via architect.update_task_status

### MergeConflictError
- **Cause**: Conflicting changes when merging
- **Response**: Return error with conflicting files
- **Recovery**: Resolve manually and retry, or use resolve_conflicts=true

### TestFailureError
- **Cause**: Tests fail after merge
- **Response**: Return error with failed tests
- **Recovery**: Fix tests, abort merge, retry

### GitError
- **Cause**: Git operation failed
- **Response**: Return error with git error message
- **Recovery**: Check git status, fix issues, retry

## Success Criteria
- [ ] Merge executed successfully
- [ ] Tests pass (if run_tests=true)
- [ ] Conflicts resolved (manually or auto)
- [ ] Merge commit created
- [ ] Pushed to remote
- [ ] Notification sent to orchestrator
- [ ] Audit trail created

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Merge completed worktree branch
result = db.execute_command('architect.merge_worktree_branches', {
    'worktree_branch': 'roadmap-implementation_task-TASK-31-1',
    'task_id': 'TASK-31-1',
    'run_tests': True,
    'resolve_conflicts': True
})

# Returns
{
    'success': True,
    'worktree_branch': 'roadmap-implementation_task-TASK-31-1',
    'task_id': 'TASK-31-1',
    'merge_commit': 'abc123def456',
    'merge_commit_short': 'abc123d',
    'tests_passed': True,
    'conflicts_resolved': 2,
    'notification_sent': True
}
```

## Output Format

```json
{
  "success": true,
  "worktree_branch": "roadmap-implementation_task-TASK-31-1",
  "task_id": "TASK-31-1",
  "merge_commit": "abc123def456",
  "merge_commit_short": "abc123d",
  "tests_passed": true,
  "conflicts_resolved": 0,
  "notification_sent": true,
  "merged_at": "2025-10-26T12:34:56Z"
}
```

## CFR-013 Git Workflow Integration

This command implements part of CFR-013 (Git Worktree Workflow):

```
TASK-31-1 (in branch roadmap-implementation_task-TASK-31-1)
  ├─ code_developer develops
  ├─ Tests pass
  └─> architect.merge_worktree_branches
        └─> Merge to roadmap
            └─> orchestrator.cleanup_worktree
                └─> Remove worktree
                    └─> Sequential next: TASK-31-2
```

## Merge Conflict Resolution Strategy

Common merge conflicts:
- **ROADMAP.md**: Auto-resolve (keep both sections, order by task_id)
- **pyproject.toml**: Manual resolve (check dependencies)
- **Code files**: Manual resolve (architect reviews)

Auto-resolution only for safe files (configuration, documentation).

## Worktree Lifecycle (orchestrator cleanup)

After successful merge, orchestrator will:
1. Receive notification from architect
2. Wait for all tests on main branch to pass
3. Remove worktree: git worktree remove {path}
4. Delete branch: git branch -D {branch}
5. Update task status to "merged"
6. Start next task in group if dependencies met

## Sequential vs Parallel Execution

```
Sequential within GROUP (CFR-013):
TASK-31-1 → merge → TASK-31-2 → merge → TASK-31-3

Parallel across GROUPS:
TASK-31-1 (GROUP-31)  ╱  TASK-32-1 (GROUP-32)
TASK-31-2 (GROUP-31) │   TASK-32-2 (GROUP-32)
TASK-31-3 (GROUP-31) ╲  TASK-32-3 (GROUP-32)
```

## Related Commands
- `architect.create_implementation_tasks` - Create task groups
- `architect.update_task_status` - Mark task completed
- `orchestrator.cleanup_worktree` - Remove worktree after merge
