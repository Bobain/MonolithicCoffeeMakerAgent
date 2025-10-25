# Merge Worktree Branches

**Agent**: architect

**Purpose**: Efficiently manage merging parallel work from roadmap-* worktree branches back to the main roadmap branch.

**Time Savings**: 15-20 minutes → 3-5 minutes (75-80% reduction)

---

## What This Skill Does

Automates and streamlines the process of merging parallel work from git worktrees:

1. **List Worktree Branches**: Identify all roadmap-* branches that need merging
2. **Check Merge Status**: Determine if branches are ready for merge (tests passing, no conflicts)
3. **Perform Merge**: Execute merge with proper commit message and validation
4. **Resolve Conflicts**: Guide conflict resolution with intelligent suggestions
5. **Validate Results**: Run tests and check ROADMAP.md consistency
6. **Notify Orchestrator**: Signal when worktree can be cleaned up

---

## When To Use

architect should use this skill **when orchestrator notifies of completed work**:

- **After Completion**: When code_developer completes work in a worktree
- **Periodic Check**: Daily check for completed worktrees that need merging
- **Before Cleanup**: Orchestrator asks architect to verify merge before cleanup
- **Conflict Detection**: When git reports merge conflicts

---

## Usage

```bash
# List all roadmap-* branches that need merging
architect merge-worktree-branches --list

# Check if specific branch is ready for merge
architect merge-worktree-branches --check roadmap-wt1

# Perform merge (with validation)
architect merge-worktree-branches --merge roadmap-wt1 --us-number 048

# Dry-run merge (preview conflicts without committing)
architect merge-worktree-branches --dry-run roadmap-wt1

# Interactive conflict resolution
architect merge-worktree-branches --merge roadmap-wt1 --interactive

# Notify orchestrator after successful merge
architect merge-worktree-branches --notify-complete roadmap-wt1
```

---

## Output Format

### List Worktree Branches

```markdown
# Worktree Branches Status

**Total Branches**: 3
**Ready for Merge**: 2
**Not Ready**: 1

---

## Ready for Merge ✅

### roadmap-wt1 (US-048)
- **Status**: ✅ Ready for merge
- **Tests**: ✅ All passing (156 tests)
- **Commits**: 3 commits ahead of roadmap
- **Last Activity**: 2025-10-19 14:30:00
- **Conflicts**: None detected
- **Action**: `architect merge-worktree-branches --merge roadmap-wt1 --us-number 048`

### roadmap-wt2 (US-050)
- **Status**: ✅ Ready for merge
- **Tests**: ✅ All passing (158 tests)
- **Commits**: 5 commits ahead of roadmap
- **Last Activity**: 2025-10-19 15:00:00
- **Conflicts**: None detected
- **Action**: `architect merge-worktree-branches --merge roadmap-wt2 --us-number 050`

---

## Not Ready ⚠️

### roadmap-wt3 (US-052)
- **Status**: ⚠️ Not ready
- **Tests**: ❌ 2 tests failing
- **Commits**: 2 commits ahead of roadmap
- **Last Activity**: 2025-10-19 16:00:00
- **Issues**:
  - tests/unit/test_orchestrator.py::test_spawn_parallel - FAILED
  - tests/integration/test_worktree.py::test_cleanup - FAILED
- **Action**: Wait for code_developer to fix tests
```

---

### Merge Execution Report

```markdown
# Merge Report: roadmap-wt1 → roadmap

**Branch**: roadmap-wt1
**User Story**: US-048 - Enforce CFR-009
**Status**: ✅ Merge Successful

---

## Pre-Merge Validation

✅ Tests passing (156 tests)
✅ No merge conflicts detected
✅ ROADMAP.md consistent
✅ Working directory clean

---

## Merge Details

**Commits Merged**: 3
**Files Changed**: 5 files (+120, -30)
**Merge Commit**: 820b563

```
git merge roadmap-wt1 --no-ff -m "Merge parallel work from roadmap-wt1: US-048 - Enforce CFR-009

Features:
- CFR-009 enforcement in NotificationDB
- Comprehensive test coverage (17 tests)
- Background agent validation

Tests: All passing (156 tests total)
Status: Ready for production

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Post-Merge Validation

✅ Tests still passing (156 tests)
✅ ROADMAP.md no duplicates
✅ Git status clean
✅ Pushed to remote

---

## Next Steps

1. ✅ Merge complete
2. ✅ Notified orchestrator
3. ⏳ Waiting for orchestrator to cleanup worktree

**Cleanup Command** (orchestrator will run):
```bash
git worktree remove /path/to/worktree --force
```
```

---

### Conflict Resolution Report

```markdown
# Merge Conflicts Detected: roadmap-wt1 → roadmap

**Branch**: roadmap-wt1
**User Story**: US-048
**Conflicts**: 2 files

---

## Conflicts

### 1. docs/roadmap/ROADMAP.md

**Type**: Content conflict (duplicate entries)

**Conflict Block**:
```diff
<<<<<<< HEAD
- [ ] US-047: Architect-only spec creation (In Progress)
=======
- [x] US-048: Enforce CFR-009 (Complete)
>>>>>>> roadmap-wt1
```

**Resolution Strategy**: Keep BOTH entries
```markdown
- [ ] US-047: Architect-only spec creation (In Progress)
- [x] US-048: Enforce CFR-009 (Complete)
```

**Rationale**: No duplicate US numbers, both are valid work items

---

### 2. coffee_maker/autonomous/daemon.py

**Type**: Code conflict (same function modified)

**Conflict Block**:
```diff
<<<<<<< HEAD
def _validate_cfr_013(self):
    """Validate CFR-013: Daemon must be on roadmap branch."""
    current_branch = self.git.get_current_branch()
    if current_branch != "roadmap":
        return False
=======
def _validate_cfr_013(self):
    """Validate CFR-013: Daemon must be on roadmap or roadmap-* branch."""
    current_branch = self.git.get_current_branch()
    if current_branch != "roadmap" and not current_branch.startswith("roadmap-"):
        return False
>>>>>>> roadmap-wt1
```

**Resolution Strategy**: Keep roadmap-wt1 version (more complete)

**Rationale**: roadmap-wt1 version supports parallel execution with roadmap-* branches

---

## Recommended Actions

1. **ROADMAP.md**: Merge both entries manually
2. **daemon.py**: Accept roadmap-wt1 version (has parallel execution support)
3. **Run tests**: `pytest` after resolution
4. **Commit resolution**: `git add . && git commit`

**Resolution Commands**:
```bash
# Resolve ROADMAP.md manually
vim docs/roadmap/ROADMAP.md

# Accept roadmap-wt1 version for daemon.py
git checkout roadmap-wt1 -- coffee_maker/autonomous/daemon.py

# Stage resolved files
git add docs/roadmap/ROADMAP.md coffee_maker/autonomous/daemon.py

# Run tests
pytest

# Commit resolution
git commit
```
```

---

## How It Works

1. **Discovery**: Scans git for all roadmap-* branches
   ```bash
   git branch -a | grep "roadmap-"
   ```

2. **Status Check**: For each branch:
   - Check if tests passing (look for pytest output in worktree)
   - Check if ahead of roadmap (commits to merge)
   - Check for potential conflicts (git merge --no-commit --no-ff)

3. **Merge Execution**:
   ```bash
   git checkout roadmap
   git pull origin roadmap
   git merge roadmap-wt1 --no-ff -m "[generated message]"
   ```

4. **Validation**:
   - Run tests: `pytest`
   - Check ROADMAP.md for duplicates
   - Verify git status clean

5. **Notification**:
   - Send notification to orchestrator via NotificationDB
   - Include branch name and US number
   - Signal ready for cleanup

---

## Configuration

Create `.claude/skills/architect/merge-worktree-branches/config.json`:

```json
{
  "auto_merge_on_success": false,
  "run_tests_before_merge": true,
  "run_tests_after_merge": true,
  "validate_roadmap_consistency": true,
  "auto_notify_orchestrator": true,
  "conflict_resolution_strategy": "interactive",
  "dry_run_first": true
}
```

**Options**:
- `auto_merge_on_success`: Automatically merge if all validations pass
- `run_tests_before_merge`: Run pytest before attempting merge
- `run_tests_after_merge`: Run pytest after merge completes
- `validate_roadmap_consistency`: Check ROADMAP.md for duplicates
- `auto_notify_orchestrator`: Automatically send notification after successful merge
- `conflict_resolution_strategy`: `interactive` (manual) or `automatic` (use predefined rules)
- `dry_run_first`: Always do dry-run before actual merge

---

## Error Handling

| Error | Resolution |
|-------|-----------|
| Tests failing before merge | Wait for code_developer to fix, do not merge |
| Merge conflicts | Use interactive conflict resolution, escalate to user if complex |
| ROADMAP.md duplicates | Manually edit to remove duplicates |
| Push rejected | Pull latest changes, rebase, retry push |
| Worktree branch missing | Notify orchestrator, investigate |
| Tests failing after merge | Revert merge: `git reset --hard HEAD~1`, investigate |

---

## Integration with Orchestrator

### Notification Protocol

**Orchestrator → Architect** (work complete):
```json
{
  "type": "worktree_complete",
  "branch": "roadmap-wt1",
  "us_number": "048",
  "worktree_path": "/tmp/worktrees/wt1",
  "tests_status": "passing",
  "timestamp": "2025-10-19T14:30:00Z"
}
```

**Architect → Orchestrator** (merge complete):
```json
{
  "type": "merge_complete",
  "branch": "roadmap-wt1",
  "us_number": "048",
  "worktree_path": "/tmp/worktrees/wt1",
  "merge_commit": "820b563",
  "ready_for_cleanup": true,
  "timestamp": "2025-10-19T14:35:00Z"
}
```

---

## Benefits

- ✅ **Faster merges**: Automated validation and execution (75-80% time reduction)
- ✅ **Safer merges**: Always run tests before and after
- ✅ **Conflict detection**: Preview conflicts before committing
- ✅ **Consistency**: ROADMAP.md validated for duplicates
- ✅ **Traceability**: Complete merge reports for audit trail
- ✅ **Orchestrator integration**: Seamless coordination for cleanup

---

## Example Workflow

```bash
# 1. Orchestrator notifies architect of completed work
#    (architect receives notification: roadmap-wt1 complete, US-048)

# 2. Architect lists all branches needing merge
architect merge-worktree-branches --list

# Output:
# roadmap-wt1: ✅ Ready (US-048)
# roadmap-wt2: ⚠️ Tests failing (US-050)

# 3. Architect checks specific branch
architect merge-worktree-branches --check roadmap-wt1

# Output:
# ✅ Tests passing (156 tests)
# ✅ No conflicts detected
# ✅ Ready for merge

# 4. Architect performs merge (with validation)
architect merge-worktree-branches --merge roadmap-wt1 --us-number 048

# Output:
# ✅ Merge successful
# ✅ Tests still passing
# ✅ Pushed to remote
# ✅ Notified orchestrator

# 5. Orchestrator cleans up worktree
#    (automatically triggered by architect's notification)
```

---

## Time Savings Calculation

**Manual Process** (15-20 minutes):
1. Check git branches (2 min)
2. Verify tests passing (3 min)
3. Attempt merge (2 min)
4. Resolve conflicts (5-10 min if conflicts)
5. Run tests after merge (3 min)
6. Push to remote (1 min)
7. Notify orchestrator (1 min)

**With Skill** (3-5 minutes):
1. List branches (30 sec - automated)
2. Check status (1 min - automated)
3. Execute merge (1 min - automated validation)
4. Review report (1 min)
5. Confirm notification (30 sec)

**Time Saved**: 12-15 minutes per merge (75-80% reduction)

**Monthly Impact** (assuming 10 merges/month):
- Manual: 150-200 minutes (2.5-3.3 hours)
- With skill: 30-50 minutes (0.5-0.8 hours)
- **Saved: 2-2.5 hours per month**

---

## Reference

See `.claude/agents/architect.md` Workflow 7 for complete merge workflow details.

See `docs/architecture/SPEC-108-parallel-agent-execution-with-git-worktree.md` for parallel execution architecture.

---

**Version**: 1.0
**Created**: 2025-10-19
**Author**: architect + code_developer
**Status**: Active
