# GUIDELINE-008: Git Worktree Best Practices

**Category**: Best Practice

**Applies To**: Parallel agent execution, git workflow, orchestrator operations

**Author**: architect agent

**Date Created**: 2025-10-20

**Last Updated**: 2025-10-20

**Status**: Active

**Related ADRs**: None

**Related Specs**: [SPEC-108: Parallel Agent Execution](../specs/SPEC-108-parallel-agent-execution.md)

---

## Overview

This guideline describes best practices for using git worktrees in the MonolithicCoffeeMakerAgent project, specifically for parallel agent execution. Git worktrees enable multiple code_developer instances to work simultaneously in separate working directories while sharing the same git repository.

---

## When to Use

Use git worktrees when:
- Running multiple code_developer instances in parallel
- Working on independent tasks that don't share files
- Need isolated working directories for testing
- Want to check out multiple branches simultaneously

**Example Use Case**:
```bash
# Main workspace working on US-065
cd /path/to/MonolithicCoffeeMakerAgent

# Create worktree for parallel US-066 work
git worktree add ../MonolithicCoffeeMakerAgent-wt66 -b feature/us-066 roadmap
```

---

## When NOT to Use

Avoid git worktrees when:
- Tasks have file conflicts (use task-separator skill to validate first)
- Only one task available (no parallelization benefit)
- System resources constrained (CPU >80%, Memory >80%)
- Working on quick fixes or hotfixes (use regular branching)

---

## The Pattern

### Core Concepts

**What is a Git Worktree?**

A git worktree is a separate working directory linked to the same git repository. It allows multiple branches to be checked out simultaneously in different directories.

**Key Benefits**:
1. **Isolation**: Each worktree has its own working directory
2. **Shared Repository**: All worktrees share the same .git database
3. **Independent Branches**: Each worktree can be on a different branch
4. **Parallel Work**: Multiple agents can work simultaneously

**Visual Representation**:
```
Repository:
.git/                           # Shared git database
  ├── worktrees/
  │   ├── MonolithicCoffeeMakerAgent-wt65/
  │   └── MonolithicCoffeeMakerAgent-wt66/

Working Directories:
MonolithicCoffeeMakerAgent/     # Main workspace (branch: roadmap)
MonolithicCoffeeMakerAgent-wt65/  # Worktree 1 (branch: feature/us-065)
MonolithicCoffeeMakerAgent-wt66/  # Worktree 2 (branch: feature/us-066)
```

### Principles

1. **One Branch Per Worktree**: Each worktree must be on a different branch
2. **Validation First**: Always validate task independence before creating worktrees
3. **Clean Branches**: Create worktrees from clean base branch (roadmap)
4. **Cleanup After Use**: Remove worktrees when work is complete
5. **Monitor Resources**: Limit concurrent worktrees to prevent resource exhaustion

---

## Best Practices

### Creating Worktrees

**DO ✅**:

1. **Use descriptive naming convention**:
```bash
# Good: {repo-name}-wt{priority-number}
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap

# Bad: Vague names
git worktree add ../temp -b my-branch
```

2. **Always create from roadmap branch**:
```bash
# ✅ Create from roadmap branch
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap

# ❌ Don't create from unknown state
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065
```

3. **Validate independence first**:
```python
# ✅ Ask architect to validate
from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator

coordinator = ParallelExecutionCoordinator()
result = coordinator._validate_task_separation([65, 66])

if result["valid"]:
    # Safe to create worktrees
    coordinator._create_worktrees([65, 66])
```

4. **Check for existing worktrees**:
```bash
# ✅ List existing worktrees first
git worktree list

# ✅ Remove if already exists
if [ -d "../MonolithicCoffeeMakerAgent-wt65" ]; then
    git worktree remove ../MonolithicCoffeeMakerAgent-wt65
fi
```

**DON'T ❌**:

1. **Don't reuse branch names**:
```bash
# ❌ Error: branch 'feature/us-065' is already checked out
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap
# (when feature/us-065 already checked out elsewhere)
```

2. **Don't create worktrees without validation**:
```bash
# ❌ Skip validation → potential merge conflicts
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap
git worktree add ../MonolithicCoffeeMakerAgent-wt66 -b feature/us-066 roadmap
# (if US-065 and US-066 share files)
```

3. **Don't use absolute paths unnecessarily**:
```bash
# ✅ Good: Relative path (portable)
git worktree add ../MonolithicCoffeeMakerAgent-wt65

# ⚠️  Avoid: Absolute path (not portable)
git worktree add /Users/bobain/Projects/MonolithicCoffeeMakerAgent-wt65
```

### Working in Worktrees

**DO ✅**:

1. **Treat each worktree as independent**:
```bash
# ✅ Each worktree has its own working directory
cd ../MonolithicCoffeeMakerAgent-wt65
git status  # Shows status for this worktree only
git commit  # Commits only affect this worktree's branch
```

2. **Run complete workflows in each worktree**:
```bash
cd ../MonolithicCoffeeMakerAgent-wt65

# Install dependencies
poetry install

# Run tests
pytest

# Make changes
git add .
git commit -m "Implement US-065"
```

3. **Monitor progress independently**:
```python
# ✅ Each worktree has its own agent instance
# Worktree 1: code_developer working on US-065
# Worktree 2: code_developer working on US-066
# Both can be monitored separately
```

**DON'T ❌**:

1. **Don't modify .git directly**:
```bash
# ❌ Never edit .git in worktrees
# All worktrees share the same .git database
```

2. **Don't switch branches in worktrees**:
```bash
# ❌ Defeats purpose of worktrees
cd ../MonolithicCoffeeMakerAgent-wt65
git checkout feature/us-066  # Don't do this!
```

3. **Don't forget where you are**:
```bash
# ⚠️  Always check current directory
pwd  # Am I in main workspace or worktree?
git branch --show-current  # Which branch am I on?
```

### Merging from Worktrees

**DO ✅**:

1. **Merge from main workspace**:
```bash
# ✅ Switch to main workspace first
cd /path/to/MonolithicCoffeeMakerAgent
git checkout roadmap

# ✅ Merge feature branch
git merge --no-ff feature/us-065 -m "Merge US-065 from parallel execution"
```

2. **Verify merge success**:
```bash
# ✅ Check merge status
git status

# ✅ Run tests after merge
pytest

# ✅ Verify no conflicts
git diff
```

3. **Auto-merge only if clean**:
```python
# ✅ Auto-merge if no conflicts
result = subprocess.run([
    "git", "merge", "--no-ff", branch_name
], capture_output=True)

if result.returncode == 0:
    print("✅ Clean merge")
else:
    print("❌ Conflicts detected, manual resolution required")
```

**DON'T ❌**:

1. **Don't merge from worktree directory**:
```bash
# ❌ Don't merge while in worktree
cd ../MonolithicCoffeeMakerAgent-wt65
git checkout roadmap  # Error: roadmap checked out in main workspace
git merge feature/us-065  # Wrong!
```

2. **Don't force merge conflicts**:
```bash
# ❌ Never force merge
git merge -X theirs feature/us-065  # Dangerous!
```

3. **Don't skip conflict resolution**:
```bash
# ❌ Always resolve conflicts properly
git merge feature/us-065
# CONFLICT detected
git commit  # ❌ Don't commit unresolved conflicts
```

### Cleaning Up Worktrees

**DO ✅**:

1. **Remove worktrees after completion**:
```bash
# ✅ Proper cleanup sequence
git worktree remove ../MonolithicCoffeeMakerAgent-wt65
git branch -D feature/us-065
git worktree prune
```

2. **Verify removal**:
```bash
# ✅ Check worktrees removed
git worktree list
# Should not show wt65 anymore

# ✅ Check branch deleted
git branch -a | grep feature/us-065
# Should be empty
```

3. **Handle stale worktrees**:
```bash
# ✅ If worktree directory manually deleted
git worktree prune  # Cleans up stale references
```

**DON'T ❌**:

1. **Don't manually delete worktree directories**:
```bash
# ❌ Don't use rm -rf
rm -rf ../MonolithicCoffeeMakerAgent-wt65  # Leaves stale git references

# ✅ Use git worktree remove
git worktree remove ../MonolithicCoffeeMakerAgent-wt65
```

2. **Don't leave stale worktrees**:
```bash
# ❌ Accumulating stale worktrees wastes disk space
git worktree list
# /path/to/wt1  abc123 [feature/us-001]  # Complete 2 weeks ago
# /path/to/wt2  def456 [feature/us-002]  # Complete 1 week ago
# Clean these up!
```

3. **Don't delete branches before removing worktrees**:
```bash
# ❌ Wrong order
git branch -D feature/us-065  # Deletes branch
git worktree remove ../MonolithicCoffeeMakerAgent-wt65  # Error!

# ✅ Correct order
git worktree remove ../MonolithicCoffeeMakerAgent-wt65  # Remove worktree first
git branch -D feature/us-065  # Then delete branch
```

---

## Resource Management

### Limit Concurrent Worktrees

**Recommended Limits**:
- **Default**: 2 worktrees (main + 1 parallel)
- **Maximum**: 3 worktrees (main + 2 parallel)
- **Minimum**: 1 worktree (just main workspace)

**Rationale**:
```
1 worktree (main only):  Baseline (no parallelization)
2 worktrees (main + 1):  75% faster (good balance)
3 worktrees (main + 2):  150% faster (diminishing returns)
4+ worktrees:            Resource exhaustion risk
```

**Implementation**:
```python
class ParallelExecutionCoordinator:
    def __init__(self, max_instances: int = 3):
        # Hard limit: 3 instances
        self.max_instances = min(max_instances, 3)
```

### Monitor System Resources

**CPU and Memory Thresholds**:
```python
# Check before creating new worktree
import psutil

cpu_percent = psutil.cpu_percent(interval=1.0)
memory_percent = psutil.virtual_memory().percent

if cpu_percent > 80 or memory_percent > 80:
    print("⚠️  System resources constrained, skipping parallel execution")
else:
    print("✅ Resources available, safe to create worktree")
```

**Disk Space**:
```bash
# Each worktree requires disk space (~100-200MB)
df -h  # Check available disk space
# Ensure >1GB free before creating worktrees
```

---

## Common Patterns

### Pattern 1: Orchestrator Parallel Execution

**Use Case**: orchestrator spawns 2 code_developer instances for independent tasks

**Implementation**:
```python
from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator

# Step 1: Validate task independence
coordinator = ParallelExecutionCoordinator(max_instances=2)
validation = coordinator._validate_task_separation([65, 66])

if not validation["valid"]:
    print(f"Cannot parallelize: {validation['reason']}")
    exit(1)

# Step 2: Create worktrees
worktrees = coordinator._create_worktrees([65, 66])
# Creates:
#  - MonolithicCoffeeMakerAgent-wt65 (branch: feature/us-065)
#  - MonolithicCoffeeMakerAgent-wt66 (branch: feature/us-066)

# Step 3: Spawn instances
coordinator._spawn_instances(worktrees, auto_approve=False)

# Step 4: Monitor until complete
monitoring_result = coordinator._monitor_instances(worktrees)

# Step 5: Merge completed work
merge_results = coordinator._merge_completed_work(worktrees)

# Step 6: Cleanup
coordinator._cleanup_worktrees(worktrees)
```

**Expected Result**:
- 2 tasks completed in ~3-4 hours (instead of 6+ hours sequentially)
- 75% velocity increase
- Clean merges to roadmap branch

### Pattern 2: Manual Worktree for Testing

**Use Case**: Developer wants to test a feature in isolation

**Implementation**:
```bash
# Create test worktree
git worktree add ../test-feature -b test/recipe-validation roadmap

# Switch to worktree
cd ../test-feature

# Make changes
vim coffee_maker/recipes.py

# Test
pytest tests/test_recipes.py

# If successful, merge
cd /path/to/MonolithicCoffeeMakerAgent
git merge test/recipe-validation

# Cleanup
git worktree remove ../test-feature
git branch -D test/recipe-validation
```

### Pattern 3: Emergency Hotfix

**Use Case**: Critical bug fix needed while working on feature

**Implementation**:
```bash
# Main workspace: Working on US-065
cd /path/to/MonolithicCoffeeMakerAgent
# Branch: feature/us-065

# Create hotfix worktree from roadmap
git worktree add ../hotfix-critical -b hotfix/database-crash roadmap

# Switch to hotfix worktree
cd ../hotfix-critical

# Fix bug
vim coffee_maker/database.py
pytest tests/test_database.py

# Commit and merge immediately
git add .
git commit -m "fix: Database crash on null input"

cd /path/to/MonolithicCoffeeMakerAgent
git checkout roadmap
git merge --no-ff hotfix/database-crash
git push

# Cleanup hotfix worktree
git worktree remove ../hotfix-critical
git branch -D hotfix/database-crash

# Resume feature work
git checkout feature/us-065
```

---

## Troubleshooting

### Issue: "Branch already checked out"

**Error**:
```bash
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap
# fatal: 'feature/us-065' is already checked out at '/path/to/existing/worktree'
```

**Solution**:
```bash
# Option 1: Remove existing worktree
git worktree list  # Find where feature/us-065 is checked out
git worktree remove /path/to/existing/worktree

# Option 2: Use different branch name
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065-v2 roadmap
```

### Issue: "Worktree already exists"

**Error**:
```bash
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap
# fatal: '../MonolithicCoffeeMakerAgent-wt65' already exists
```

**Solution**:
```bash
# Remove existing worktree first
git worktree remove --force ../MonolithicCoffeeMakerAgent-wt65

# Then create new one
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap
```

### Issue: "Cannot merge - conflicts detected"

**Error**:
```bash
git merge feature/us-065
# CONFLICT (content): Merge conflict in coffee_maker/database.py
```

**Solution**:
```bash
# Manual conflict resolution required
git status  # Shows conflicted files

# Open file and resolve conflicts
vim coffee_maker/database.py
# Look for <<<<<<< HEAD, =======, >>>>>>> markers
# Edit to resolve

# Stage resolved files
git add coffee_maker/database.py

# Complete merge
git commit
```

### Issue: "Stale worktree references"

**Error**:
```bash
# Worktree directory manually deleted
git worktree list
# /path/to/wt65  abc123 [feature/us-065]  # But directory doesn't exist!
```

**Solution**:
```bash
# Prune stale references
git worktree prune

# Verify cleanup
git worktree list  # Should not show wt65 anymore
```

---

## Anti-Patterns

### Anti-Pattern 1: Creating Too Many Worktrees

**Problem**:
```bash
# Creating 5+ worktrees
git worktree add ../wt1 -b feature/us-001 roadmap
git worktree add ../wt2 -b feature/us-002 roadmap
git worktree add ../wt3 -b feature/us-003 roadmap
git worktree add ../wt4 -b feature/us-004 roadmap
git worktree add ../wt5 -b feature/us-005 roadmap
# Result: System resource exhaustion, slow performance
```

**Solution**:
```python
# Limit to 2-3 worktrees maximum
coordinator = ParallelExecutionCoordinator(max_instances=3)
# Hard limit enforced
```

### Anti-Pattern 2: Forgetting Cleanup

**Problem**:
```bash
# Create worktree
git worktree add ../wt65 -b feature/us-065 roadmap

# Work complete, merge
git merge feature/us-065

# ❌ Forget cleanup
# Worktree still exists, wastes disk space
```

**Solution**:
```python
# Always cleanup in finally block
try:
    worktree = create_worktree()
    spawn_instance(worktree)
    merge_work(worktree)
finally:
    cleanup_worktree(worktree)  # Guaranteed cleanup
```

### Anti-Pattern 3: Mixing Manual and Automated Worktrees

**Problem**:
```bash
# Manual worktree creation
git worktree add ../my-test -b test/something roadmap

# orchestrator creates worktree with same path
# Conflict!
```

**Solution**:
```bash
# Use consistent naming convention
# Manual: test/* branches
# Automated: feature/us-* branches

# Manual
git worktree add ../test-something -b test/something roadmap

# Automated (orchestrator)
git worktree add ../MonolithicCoffeeMakerAgent-wt65 -b feature/us-065 roadmap
# No conflict!
```

---

## Examples

### Example 1: Successful Parallel Execution

```bash
# Step 1: Validate (orchestrator calls architect)
$ coordinator._validate_task_separation([65, 66])
✅ Independent pairs: [(65, 66)]
Confidence: 100%

# Step 2: Create worktrees
$ git worktree list
/path/to/MonolithicCoffeeMakerAgent      abc123 [roadmap]
/path/to/MonolithicCoffeeMakerAgent-wt65 def456 [feature/us-065]
/path/to/MonolithicCoffeeMakerAgent-wt66 ghi789 [feature/us-066]

# Step 3: Work proceeds in parallel
# Worktree 1: code_developer implements US-065
# Worktree 2: code_developer implements US-066

# Step 4: Both complete
$ git merge --no-ff feature/us-065
Merge made by the 'ort' strategy.
 coffee_maker/recipes.py | 45 +++++++++++++++++++++++++++++++++++
 tests/test_recipes.py   | 23 ++++++++++++++++++
 2 files changed, 68 insertions(+)

$ git merge --no-ff feature/us-066
Merge made by the 'ort' strategy.
 coffee_maker/notifications.py | 38 ++++++++++++++++++++++++++++++++
 tests/test_notifications.py   | 19 +++++++++++++++
 2 files changed, 57 insertions(+)

# Step 5: Cleanup
$ git worktree remove ../MonolithicCoffeeMakerAgent-wt65
$ git worktree remove ../MonolithicCoffeeMakerAgent-wt66
$ git branch -D feature/us-065 feature/us-066

✅ Result: 2 tasks completed in 3 hours (75% faster)
```

### Example 2: Merge Conflict (Manual Resolution)

```bash
# orchestrator detects conflict during merge
$ git merge feature/us-065
Auto-merging coffee_maker/database.py
CONFLICT (content): Merge conflict in coffee_maker/database.py
Automatic merge failed; fix conflicts and then commit the result.

# Manual resolution required
$ cat coffee_maker/database.py
<<<<<<< HEAD
def connect():
    return Database(host="localhost")
=======
def connect():
    return Database(host="127.0.0.1")
>>>>>>> feature/us-065

# Resolve conflict
$ vim coffee_maker/database.py
# Choose "localhost"

$ git add coffee_maker/database.py
$ git commit

✅ Conflict resolved manually
```

---

## Related Documentation

- **[SPEC-108: Parallel Agent Execution](../specs/SPEC-108-parallel-agent-execution.md)** - Full technical specification
- **[Parallel Execution Skill](../../.claude/skills/orchestrator/parallel-execution/SKILL.md)** - orchestrator skill documentation
- **[Task Separator Skill](../../.claude/skills/architect/task-separator/SKILL.md)** - architect skill documentation
- **[Git Worktree Official Docs](https://git-scm.com/docs/git-worktree)** - Git documentation
- **[CFR-013: Git Workflow](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-013)** - Git branching rules

---

## Version History

**v1.0** (2025-10-20):
- Initial guideline
- Best practices for parallel execution
- Troubleshooting guide
- Common patterns and anti-patterns

---

**Guideline Version**: 1.0
**Last Review**: 2025-10-20
**Status**: Active
