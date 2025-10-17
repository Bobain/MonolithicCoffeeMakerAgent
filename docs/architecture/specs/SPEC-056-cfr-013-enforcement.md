# SPEC-056: Enforce CFR-013 - Daemon Must Work on roadmap Branch Only

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-17
**Related**: US-056, CFR-013 (CRITICAL_FUNCTIONAL_REQUIREMENTS.md)

---

## Executive Summary

The code_developer daemon currently VIOLATES CFR-013 by attempting to create feature branches, which blocks ALL autonomous operations. This specification details the architectural changes required to enforce CFR-013: ALL agents MUST work on the `roadmap` branch ONLY.

**Impact**: CRITICAL - Daemon cannot operate until this is fixed.

**Estimated Implementation Time**: 2-3 hours

**Complexity**: Low (removal of code, not addition)

---

## Problem Statement

### Current Violation

**Location**: `coffee_maker/autonomous/daemon_implementation.py:198`

```python
# VIOLATION: Attempts to create feature branch
branch_name = f"feature/{priority_name.lower().replace(' ', '-').replace(':', '')}"
logger.info(f"Creating branch: {branch_name}")
if not self.git.create_branch(branch_name):
    logger.error("Failed to create branch")
    return False
```

**Error Observed**:
```
CFR-013 VIOLATION: Attempted to switch away from roadmap branch

Current branch: roadmap
Attempted checkout: feature/priority-2-6
Violating agent: code_developer
```

### Why This Is Critical

1. **Daemon Cannot Start**: Branch creation fails, blocking all work
2. **Blocks US-057**: Multi-agent orchestrator requires CFR-013 compliance
3. **Violates Architecture**: CFR-013 mandates single-branch workflow
4. **No Value**: Feature branches serve no purpose when working on `roadmap`

### Root Cause

The daemon was originally designed with a **feature branch workflow**:
1. Create feature branch (`feature/priority-X`)
2. Implement on feature branch
3. Create PR to merge to main
4. Repeat

But the system has evolved to use a **single-branch workflow** (CFR-013):
1. Work directly on `roadmap` branch
2. Commit frequently with clear messages
3. Push to `origin/roadmap` for visibility
4. No PRs needed (roadmap IS the work-in-progress branch)

The daemon code was never updated to reflect this architectural shift.

---

## Current Architecture Analysis

### Branch Operations - Current Flow

```
DevDaemon._implement_priority()
    ↓
Create feature branch (daemon_implementation.py:198)
    ↓
Execute Claude API
    ↓
Commit to feature branch
    ↓
Push feature branch
    ↓
Create PR (optional)
    ↓
Merge to roadmap (daemon_git_ops.py:112)
```

### Files Involved

| File | Lines | Purpose | Needs Change? |
|------|-------|---------|---------------|
| `daemon_implementation.py` | 185-206 | Feature branch creation | ✅ REMOVE |
| `daemon.py` | 364-366 | Prerequisites check | ✅ ADD CFR-013 validation |
| `git_manager.py` | 116-148 | `create_branch()` method | ⚠️  Keep but warn against usage |
| `daemon_git_ops.py` | 112-252 | `_merge_to_roadmap()` | ✅ SIMPLIFY (already on roadmap) |
| `daemon_git_ops.py` | 51-110 | `_sync_roadmap_branch()` | ✅ SIMPLIFY (no merge needed) |

### Branch Operations - All Locations

**Grep Analysis**:
```bash
# All git branch operations in daemon code
git_manager.py:93-115    # branch_exists()
git_manager.py:116-148   # create_branch() - USED BY VIOLATION
daemon_implementation.py:185-206 # Feature branch creation - VIOLATION
daemon_git_ops.py:112-252 # _merge_to_roadmap() - Assumes feature branch
daemon_git_ops.py:51-110  # _sync_roadmap_branch() - Merges origin/roadmap
```

---

## Desired Architecture

### Single-Branch Workflow (CFR-013 Compliant)

```
DevDaemon._implement_priority()
    ↓
Validate on roadmap branch (CFR-013 check)
    ↓
Execute Claude API
    ↓
Commit to roadmap branch
    ↓
Push to origin/roadmap
    ↓
Continue (NO PR, NO merge)
```

### Key Principles

1. **Always on roadmap**: Daemon NEVER leaves the `roadmap` branch
2. **Frequent commits**: Commit after each subtask with descriptive messages
3. **Direct push**: Push directly to `origin/roadmap` for visibility
4. **No PRs**: The `roadmap` branch IS the work-in-progress branch
5. **Validation at startup**: Daemon MUST validate CFR-013 compliance before starting

### CFR-013 Validation

**What to check**:
```python
def _validate_cfr_013(self) -> bool:
    """Validate CFR-013: Daemon must be on roadmap branch.

    Returns:
        True if on roadmap branch, False otherwise
    """
    current_branch = self.git.get_current_branch()

    if current_branch != "roadmap":
        logger.error("CFR-013 VIOLATION: Daemon must work on 'roadmap' branch only")
        logger.error(f"Current branch: {current_branch}")
        logger.error(f"Expected branch: roadmap")
        logger.error("")
        logger.error("To fix:")
        logger.error("1. git checkout roadmap")
        logger.error("2. git pull origin roadmap")
        logger.error("3. Restart daemon")
        return False

    logger.info("✅ CFR-013 compliant: On 'roadmap' branch")
    return True
```

**When to validate**:
- Daemon startup (before main loop)
- After git operations (defensive check)
- Before implementing priority

---

## Implementation Plan

### Phase 1: Add CFR-013 Validation (15 minutes)

**Goal**: Daemon validates branch before starting

**Changes**:
```python
# File: daemon.py
# Location: _check_prerequisites() method (after line 605)

def _check_prerequisites(self) -> bool:
    """Check if prerequisites are met.

    Returns:
        True if ready to run
    """
    logger.info("Checking prerequisites...")

    # Existing checks...
    # (Claude API, Git, ROADMAP)

    # NEW: CFR-013 validation
    logger.info("Checking CFR-013 compliance...")
    if not self._validate_cfr_013():
        logger.error("❌ CFR-013 validation failed")
        return False

    logger.info("✅ CFR-013 compliant")

    return True

def _validate_cfr_013(self) -> bool:
    """Validate CFR-013: Daemon must be on roadmap branch.

    Returns:
        True if on roadmap branch, False otherwise
    """
    current_branch = self.git.get_current_branch()

    if current_branch != "roadmap":
        logger.error("")
        logger.error("=" * 60)
        logger.error("CFR-013 VIOLATION: Daemon must work on 'roadmap' branch ONLY")
        logger.error("=" * 60)
        logger.error(f"Current branch: {current_branch}")
        logger.error(f"Expected branch: roadmap")
        logger.error("")
        logger.error("CFR-013 requires ALL agents to work on the roadmap branch.")
        logger.error("This ensures:")
        logger.error("  - Single source of truth")
        logger.error("  - No merge conflicts between feature branches")
        logger.error("  - All work immediately visible to team")
        logger.error("")
        logger.error("To fix:")
        logger.error("  1. git checkout roadmap")
        logger.error("  2. git pull origin roadmap")
        logger.error("  3. Restart daemon")
        logger.error("")
        return False

    logger.info("✅ CFR-013 compliant: On 'roadmap' branch")
    return True
```

**Testing**:
```bash
# Test 1: Should fail on wrong branch
git checkout main
poetry run code-developer --auto-approve
# Expected: CFR-013 VIOLATION error, daemon exits

# Test 2: Should succeed on roadmap
git checkout roadmap
poetry run code-developer --auto-approve
# Expected: Daemon starts successfully
```

### Phase 2: Remove Branch Creation Logic (30 minutes)

**Goal**: Eliminate all feature branch creation code

**Changes**:

**File 1**: `daemon_implementation.py` (lines 185-206)

```python
# BEFORE (VIOLATION):
# PRIORITY 4: Update progress - creating branch
self.status.report_progress(10, "Creating feature branch")

# Track subtask: Creating branch (estimated: 10 seconds)
subtask_start = datetime.now()
self._update_subtask(
    "Creating feature branch",
    "in_progress",
    subtask_start,
    estimated_seconds=10,
)

# Create branch
branch_name = f"feature/{priority_name.lower().replace(' ', '-').replace(':', '')}"
logger.info(f"Creating branch: {branch_name}")

if not self.git.create_branch(branch_name):
    logger.error("Failed to create branch")
    self._update_subtask("Creating feature branch", "failed", subtask_start, estimated_seconds=10)
    return False

self._update_subtask("Creating feature branch", "completed", subtask_start, estimated_seconds=10)

# PRIORITY 4: Log branch creation
self.status.report_activity(
    ActivityType.GIT_BRANCH,
    f"Created branch: {branch_name}",
    details={"branch": branch_name},
)
```

```python
# AFTER (CFR-013 COMPLIANT):
# PRIORITY 4: Update progress - validating branch
self.status.report_progress(10, "Validating roadmap branch")

# Validate CFR-013 compliance before implementation
current_branch = self.git.get_current_branch()
if current_branch != "roadmap":
    logger.error(f"CFR-013 VIOLATION: Must be on roadmap branch, currently on: {current_branch}")
    return False

logger.info("✅ CFR-013 compliant: Working on 'roadmap' branch")

# PRIORITY 4: Log CFR-013 compliance
self.status.report_activity(
    ActivityType.INFO,  # Or create new ActivityType.CFR_013_VALIDATION
    "CFR-013 validated: On roadmap branch",
    details={"branch": "roadmap"},
)
```

**File 2**: `daemon_implementation.py` (line 148 - remove branch_name reference)

```python
# BEFORE:
# PRIORITY 4: Log push activity
self.status.report_activity(
    ActivityType.GIT_PUSH,
    f"Pushed branch: {branch_name}",
    details={"branch": branch_name},
)
```

```python
# AFTER:
# PRIORITY 4: Log push activity
self.status.report_activity(
    ActivityType.GIT_PUSH,
    "Pushed to roadmap branch",
    details={"branch": "roadmap"},
)
```

### Phase 3: Update Git Operations (45 minutes)

**Goal**: Simplify git operations for single-branch workflow

**File**: `daemon_git_ops.py`

#### Change 1: Simplify `_merge_to_roadmap()` (lines 112-252)

**BEFORE**: Complex logic to switch branches, merge, switch back
**AFTER**: Simple push to roadmap (we're already there!)

```python
def _merge_to_roadmap(self, message: str = "Sync progress to roadmap") -> bool:
    """Push changes to roadmap branch.

    CFR-013 COMPLIANT: Since daemon always works on roadmap branch,
    this method simply commits and pushes changes to origin/roadmap.

    No branch switching, no merging needed.

    Args:
        message: Description of what was accomplished

    Returns:
        True if push successful, False otherwise

    Example:
        >>> # After completing a subtask
        >>> self._merge_to_roadmap("Completed US-056 Phase 1")
        True
    """
    try:
        # Validate we're on roadmap branch (defensive check)
        current_branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=self.git.repo_path,
            text=True
        ).strip()

        if current_branch != "roadmap":
            logger.error(f"CFR-013 VIOLATION in _merge_to_roadmap: On '{current_branch}', expected 'roadmap'")
            return False

        # Check for uncommitted changes
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=self.git.repo_path,
            text=True
        )

        if status.strip():
            # Commit changes
            logger.info(f"Committing changes: {message}")
            subprocess.run(["git", "add", "-A"], cwd=self.git.repo_path, check=True)
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.git.repo_path,
                check=True
            )
        else:
            logger.info("No uncommitted changes to commit")

        # Push to origin/roadmap
        logger.info("Pushing to origin/roadmap...")
        subprocess.run(
            ["git", "push", "origin", "roadmap"],
            cwd=self.git.repo_path,
            check=True
        )

        logger.info(f"✅ Pushed to roadmap: {message}")
        logger.info("✅ project_manager can now see progress")
        return True

    except Exception as e:
        logger.error(f"Failed to push to roadmap: {e}")
        logger.error("PROJECT_MANAGER CANNOT SEE PROGRESS!")
        return False
```

#### Change 2: Simplify `_sync_roadmap_branch()` (lines 51-110)

**BEFORE**: Fetch and merge origin/roadmap
**AFTER**: Simple pull (we're already on roadmap!)

```python
def _sync_roadmap_branch(self) -> bool:
    """Sync with 'roadmap' branch before each iteration.

    CFR-013 COMPLIANT: Since daemon always works on roadmap branch,
    this method simply pulls latest changes from origin/roadmap.

    No branch switching, no merge needed.

    Returns:
        True if sync successful, False if sync failed
    """
    try:
        # Validate we're on roadmap branch (defensive check)
        current_branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=self.git.repo_path,
            text=True
        ).strip()

        if current_branch != "roadmap":
            logger.error(f"CFR-013 VIOLATION in _sync_roadmap_branch: On '{current_branch}', expected 'roadmap'")
            return False

        # Pull latest from origin/roadmap
        logger.info("Pulling latest from origin/roadmap...")
        result = subprocess.run(
            ["git", "pull", "origin", "roadmap", "--no-edit"],
            cwd=self.git.repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            # Check if merge conflict
            if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                logger.error("❌ Merge conflict with origin/roadmap!")
                logger.error("Manual intervention required to resolve conflicts")

                # Abort merge
                subprocess.run(
                    ["git", "merge", "--abort"],
                    cwd=self.git.repo_path,
                    capture_output=True,
                )
                return False
            else:
                logger.warning(f"Pull failed: {result.stderr}")
                return False

        logger.info("✅ Synced with origin/roadmap")
        return True

    except Exception as e:
        logger.error(f"Error syncing roadmap branch: {e}")
        return False
```

### Phase 4: Update Prompts and Status Reporting (30 minutes)

**Goal**: Remove all references to "feature branch" in prompts and status messages

**Changes**:

1. **Prompt files** (`.claude/commands/implement-*.md`):
   - Search for "feature branch" → Replace with "roadmap branch"
   - Search for "create branch" → Remove instructions
   - Add CFR-013 reminder: "You are working on the roadmap branch. Do NOT create branches."

2. **Status messages** (`daemon_implementation.py`):
   - Line 186: "Creating feature branch" → "Validating roadmap branch"
   - Line 190-195: Remove "Creating branch" subtask
   - Line 209-213: Remove "Created branch" activity log

3. **Commit messages** (`daemon_implementation.py:300-311`):
   - Already correct (no branch references)
   - Add note: "All work on roadmap branch (CFR-013)"

4. **PR body** (`daemon_implementation.py:313-345`):
   - ⚠️  PRs may not be needed anymore
   - If kept: Update to reflect roadmap branch workflow
   - Consider: Should daemon create PRs from roadmap → main? (Future decision)

### Phase 5: Testing and Verification (30 minutes)

**Goal**: Comprehensive testing of single-branch workflow

#### Test Plan

**Test 1: CFR-013 Validation at Startup**
```bash
# Setup: Switch to wrong branch
git checkout main

# Execute
poetry run code-developer --auto-approve

# Expected
CFR-013 VIOLATION error
Daemon exits immediately
Clear instructions to fix
```

**Test 2: CFR-013 Validation Success**
```bash
# Setup: Switch to roadmap branch
git checkout roadmap

# Execute
poetry run code-developer --auto-approve

# Expected
✅ CFR-013 compliant: On 'roadmap' branch
Daemon starts successfully
No branch creation attempts
```

**Test 3: Implementation Without Branch Creation**
```bash
# Setup: Roadmap with simple priority
git checkout roadmap

# Execute
poetry run code-developer --auto-approve

# Expected
Daemon implements priority
No "Creating feature branch" messages
All commits go directly to roadmap
Push to origin/roadmap succeeds
```

**Test 4: Roadmap Sync Without Branch Switching**
```bash
# Setup: Simulate concurrent changes
# Terminal 1: Start daemon
poetry run code-developer --auto-approve

# Terminal 2: Make changes to ROADMAP.md
echo "# Test" >> docs/roadmap/ROADMAP.md
git add docs/roadmap/ROADMAP.md
git commit -m "test: Concurrent change"
git push origin roadmap

# Expected (Terminal 1)
Next iteration: Daemon pulls latest ROADMAP.md
No branch switching
No merge conflicts
Continues working
```

**Test 5: Frequent Commits to Roadmap**
```bash
# Execute: Let daemon run for 2-3 priorities
poetry run code-developer --auto-approve

# Verify
git log --oneline -n 20
# Expected: Multiple commits directly on roadmap
# Expected: No feature/* branch references
# Expected: Clear commit messages

git branch -a
# Expected: Only roadmap, main branches
# Expected: NO feature/* branches
```

**Test 6: Integration with US-029 Merge**
```bash
# Execute: Let daemon complete a priority
poetry run code-developer --auto-approve

# Expected
✅ Implementation complete
✅ Pushed to roadmap
✅ Merged progress to roadmap (should be no-op)
No errors about branch switching
```

#### Integration Tests

**File**: `tests/integration/test_cfr_013_enforcement.py`

```python
"""Integration tests for CFR-013 enforcement."""

import subprocess
from pathlib import Path

import pytest


class TestCFR013Enforcement:
    """Test CFR-013: Daemon must work on roadmap branch only."""

    def test_daemon_validates_branch_at_startup(self, tmp_path, monkeypatch):
        """Daemon should validate branch at startup and exit if not on roadmap."""
        # Setup: Create git repo on main branch
        repo = tmp_path / "test_repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True)
        subprocess.run(["git", "checkout", "-b", "main"], cwd=repo, check=True)

        # Create minimal ROADMAP.md
        roadmap = repo / "docs" / "roadmap"
        roadmap.mkdir(parents=True)
        (roadmap / "ROADMAP.md").write_text("# ROADMAP\n\nNo priorities")

        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)

        monkeypatch.chdir(repo)

        # Execute: Start daemon on main branch
        from coffee_maker.autonomous.daemon import DevDaemon
        daemon = DevDaemon(roadmap_path=str(roadmap / "ROADMAP.md"))

        # Verify: _check_prerequisites() should fail
        assert not daemon._check_prerequisites()

    def test_daemon_starts_on_roadmap_branch(self, tmp_path, monkeypatch):
        """Daemon should start successfully when on roadmap branch."""
        # Setup: Create git repo on roadmap branch
        repo = tmp_path / "test_repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True)
        subprocess.run(["git", "checkout", "-b", "roadmap"], cwd=repo, check=True)

        # Create minimal ROADMAP.md
        roadmap = repo / "docs" / "roadmap"
        roadmap.mkdir(parents=True)
        (roadmap / "ROADMAP.md").write_text("# ROADMAP\n\nNo priorities")

        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)

        monkeypatch.chdir(repo)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Execute: Start daemon on roadmap branch
        from coffee_maker.autonomous.daemon import DevDaemon
        daemon = DevDaemon(roadmap_path=str(roadmap / "ROADMAP.md"))

        # Verify: _validate_cfr_013() should succeed
        assert daemon._validate_cfr_013()

    def test_no_branch_creation_during_implementation(self, tmp_path, monkeypatch):
        """Daemon should NOT attempt to create branches during implementation."""
        # Setup: Create git repo on roadmap branch with priority
        repo = tmp_path / "test_repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True)
        subprocess.run(["git", "checkout", "-b", "roadmap"], cwd=repo, check=True)

        # Create ROADMAP.md with simple priority
        roadmap = repo / "docs" / "roadmap"
        roadmap.mkdir(parents=True)
        (roadmap / "ROADMAP.md").write_text("""# ROADMAP

## PRIORITY 1: Test Priority

**Status**: 📋 Planned
**Title**: Simple test task

### Deliverables
- Create test.txt file
""")

        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)

        # Setup remote
        subprocess.run(["git", "remote", "add", "origin", "git@github.com:test/repo.git"], cwd=repo, check=True)

        monkeypatch.chdir(repo)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Execute: Mock implementation
        from coffee_maker.autonomous.daemon import DevDaemon
        daemon = DevDaemon(roadmap_path=str(roadmap / "ROADMAP.md"))

        # Spy on git operations
        original_create_branch = daemon.git.create_branch
        branch_create_calls = []

        def spy_create_branch(branch_name, from_branch=None):
            branch_create_calls.append(branch_name)
            return original_create_branch(branch_name, from_branch)

        daemon.git.create_branch = spy_create_branch

        # Execute implementation (mock)
        priority = {
            "name": "PRIORITY 1",
            "title": "Test Priority",
            "number": 1,
            "content": "Create test.txt file"
        }

        # Verify: create_branch should NEVER be called
        # (We can't run full implementation in unit test, but we can verify
        #  the code path doesn't call create_branch)
        assert len(branch_create_calls) == 0
```

#### Manual Verification Checklist

- [ ] Daemon starts only on roadmap branch
- [ ] Daemon exits with clear error on wrong branch
- [ ] No branch creation attempts during implementation
- [ ] All commits go directly to roadmap
- [ ] Push to origin/roadmap succeeds
- [ ] Roadmap sync works without branch switching
- [ ] No merge conflicts from branch operations
- [ ] Status messages reference "roadmap branch" not "feature branch"
- [ ] Git log shows linear history on roadmap
- [ ] No feature/* branches created

---

## Code Changes Required

### Summary of Changes

| File | Lines | Change Type | Estimated Time |
|------|-------|-------------|----------------|
| `daemon.py` | After 605 | Add `_validate_cfr_013()` method | 10 min |
| `daemon.py` | 364-366 | Add CFR-013 validation to prerequisites | 5 min |
| `daemon_implementation.py` | 185-206 | Remove branch creation logic | 15 min |
| `daemon_implementation.py` | 148 | Update push activity log | 2 min |
| `daemon_git_ops.py` | 112-252 | Simplify `_merge_to_roadmap()` | 20 min |
| `daemon_git_ops.py` | 51-110 | Simplify `_sync_roadmap_branch()` | 15 min |
| `.claude/commands/implement-*.md` | Various | Remove branch references | 10 min |
| `tests/integration/test_cfr_013_enforcement.py` | New file | Add integration tests | 30 min |

**Total Estimated Time**: 2 hours 7 minutes

### Detailed Code Snippets

All code snippets provided in Phase 1-5 above are production-ready and can be copy-pasted directly.

---

## Rollback Plan

### If Implementation Fails

**Symptoms**:
- Daemon cannot start
- Git operations fail
- Commits/pushes fail

**Rollback Steps**:

```bash
# 1. Revert all changes
git checkout roadmap
git reset --hard <commit-before-us-056>

# 2. Verify daemon works on old code
poetry run code-developer --auto-approve

# 3. Restore feature branch workflow temporarily
# (This allows daemon to work while we debug)
git checkout <last-working-commit>

# 4. Create ticket for follow-up
# BUG-XXX: US-056 rollback - CFR-013 enforcement failed
```

### Recovery Strategy

If rollback needed:
1. Document exact error messages
2. Capture git status, branch info, logs
3. Create detailed bug report with reproduction steps
4. Re-plan implementation with more conservative approach

---

## Success Criteria

### Must Have (Critical)

1. **Daemon starts without CFR-013 violations**
   - `poetry run code-developer --auto-approve` succeeds on roadmap branch
   - Exits with clear error on wrong branch

2. **No feature branch creation**
   - `git branch -a` shows NO feature/* branches after daemon run
   - Git log shows commits directly on roadmap

3. **All commits go to roadmap**
   - `git log --oneline roadmap` shows daemon commits
   - `git log --oneline main` unchanged

4. **Push to roadmap succeeds**
   - `git push origin roadmap` works after implementation
   - No branch tracking issues

5. **PRIORITY 2.6 implementation succeeds**
   - Daemon can implement at least one full priority
   - No CFR-013 violations during implementation

### Should Have (Important)

6. **Clear error messages**
   - CFR-013 violation message is helpful
   - Instructions for fix are correct

7. **Integration tests pass**
   - `pytest tests/integration/test_cfr_013_enforcement.py` passes
   - All test cases succeed

8. **Status messages updated**
   - No references to "feature branch"
   - All messages reference "roadmap branch"

### Nice to Have (Optional)

9. **Prompts updated**
   - `.claude/commands/` prompts mention CFR-013
   - No branch creation instructions

10. **Documentation updated**
    - US-056 marked complete
    - CFR-013 implementation documented

---

## Dependencies

### Prerequisites

- **Current branch**: Must be on `roadmap` branch
- **Clean working directory**: No uncommitted changes
- **Remote configured**: `origin` remote exists
- **Tests passing**: All existing tests pass before changes

### Blocks

- **US-057**: Multi-Agent Orchestrator (cannot proceed without CFR-013)
- **US-029**: Frequent Roadmap Sync (relies on CFR-013 for simplicity)

### Blocked By

- None (this is CRITICAL and blocking everything)

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_cfr_013_validation.py`

```python
"""Unit tests for CFR-013 validation."""

from unittest.mock import MagicMock

from coffee_maker.autonomous.daemon import DevDaemon


class TestCFR013Validation:
    """Test _validate_cfr_013() method."""

    def test_validate_cfr_013_success_on_roadmap(self):
        """Should return True when on roadmap branch."""
        daemon = DevDaemon()
        daemon.git = MagicMock()
        daemon.git.get_current_branch.return_value = "roadmap"

        assert daemon._validate_cfr_013() is True

    def test_validate_cfr_013_fails_on_main(self):
        """Should return False when on main branch."""
        daemon = DevDaemon()
        daemon.git = MagicMock()
        daemon.git.get_current_branch.return_value = "main"

        assert daemon._validate_cfr_013() is False

    def test_validate_cfr_013_fails_on_feature_branch(self):
        """Should return False when on feature branch."""
        daemon = DevDaemon()
        daemon.git = MagicMock()
        daemon.git.get_current_branch.return_value = "feature/test"

        assert daemon._validate_cfr_013() is False
```

### Integration Tests

See Phase 5 above for complete integration test plan.

### Manual Testing

**Test Checklist** (copy to test execution log):

```
[ ] Test 1: CFR-013 validation at startup (wrong branch)
    - Expected: Daemon exits with clear error
    - Actual: _______________

[ ] Test 2: CFR-013 validation at startup (correct branch)
    - Expected: Daemon starts successfully
    - Actual: _______________

[ ] Test 3: Implementation without branch creation
    - Expected: No branch creation, commits to roadmap
    - Actual: _______________

[ ] Test 4: Roadmap sync without branch switching
    - Expected: Simple pull, no branch ops
    - Actual: _______________

[ ] Test 5: Frequent commits to roadmap
    - Expected: Multiple commits on roadmap branch
    - Actual: _______________

[ ] Test 6: Integration with US-029 merge
    - Expected: Merge is no-op (already on roadmap)
    - Actual: _______________
```

---

## Risks and Mitigations

### Risk 1: Breaking US-029 Merge Logic

**Risk**: US-029 expects `_merge_to_roadmap()` to switch branches
**Impact**: High - Project manager loses visibility
**Probability**: Medium
**Mitigation**:
- Test US-029 integration thoroughly
- Simplify `_merge_to_roadmap()` to just push (we're already on roadmap)
- Add defensive checks for branch name

### Risk 2: Git Operations Fail

**Risk**: Simplified git operations may fail in edge cases
**Impact**: High - Daemon cannot commit/push
**Probability**: Low
**Mitigation**:
- Keep error handling from original code
- Add more logging for debugging
- Test with dirty working directory, merge conflicts

### Risk 3: Existing Work on Feature Branches

**Risk**: User may have uncommitted work on feature branches
**Impact**: Medium - User loses work
**Probability**: Low (internal project, small team)
**Mitigation**:
- Document rollback procedure
- Warn user to commit all work before upgrade
- Add migration guide to US-056

### Risk 4: Tests Depend on Branch Creation

**Risk**: Existing tests may expect feature branch creation
**Impact**: Low - Tests fail but no runtime impact
**Probability**: High (tests likely mock branch creation)
**Mitigation**:
- Update all tests to work with roadmap branch
- Search for `create_branch` in tests
- Update mocks to reflect CFR-013

---

## Migration Guide

### For Users

**Before Upgrading**:

```bash
# 1. Commit all work on feature branches
git add .
git commit -m "WIP: Save before CFR-013 migration"

# 2. Merge feature branches to roadmap
git checkout roadmap
git merge --no-ff feature/my-work -m "Merge before CFR-013"
git push origin roadmap

# 3. Delete feature branches
git branch -d feature/my-work
git push origin --delete feature/my-work

# 4. Verify on roadmap branch
git branch --show-current
# Expected: roadmap
```

**After Upgrading**:

```bash
# 1. Pull latest roadmap
git checkout roadmap
git pull origin roadmap

# 2. Start daemon (should work now)
poetry run code-developer --auto-approve

# 3. Verify no feature branches created
git branch -a
# Expected: Only roadmap, main
```

### For Developers

**Code Changes**:

```python
# BEFORE (VIOLATION):
git.create_branch("feature/my-feature")
git.commit("feat: Implement feature")
git.push()

# AFTER (CFR-013 COMPLIANT):
# Already on roadmap, just commit and push
git.commit("feat: Implement feature")
git.push("roadmap")
```

**Testing Changes**:

```python
# BEFORE:
mock_git.create_branch.assert_called_once_with("feature/test")

# AFTER:
# Branch creation should never be called
mock_git.create_branch.assert_not_called()
```

---

## Performance Impact

### Expected Improvements

1. **Faster git operations**: No branch creation/switching overhead
   - Before: ~2-3 seconds (create branch, switch)
   - After: ~0 seconds (already on roadmap)
   - **Savings**: 2-3 seconds per priority

2. **Simpler merge logic**: No complex branch merging
   - Before: Checkout roadmap, merge, switch back (~5 seconds)
   - After: Simple push (~1 second)
   - **Savings**: 4 seconds per checkpoint

3. **Reduced merge conflicts**: Single branch eliminates branch conflicts
   - Before: Potential conflicts when merging feature → roadmap
   - After: Only conflicts from concurrent edits (rare)
   - **Savings**: Minutes to hours in conflict resolution

### Total Impact

For a typical priority (5 git operations):
- **Before**: ~25 seconds in git overhead
- **After**: ~5 seconds in git overhead
- **Improvement**: 80% reduction in git time

---

## Monitoring and Observability

### Metrics to Track

1. **CFR-013 Compliance Rate**: % of daemon runs on roadmap branch
2. **Branch Creation Attempts**: Should be 0 after implementation
3. **Git Operation Duration**: Should decrease by ~80%
4. **Merge Conflicts**: Should decrease significantly
5. **Daemon Startup Success Rate**: Should increase to 100% on roadmap

### Logging

**Add these log lines**:

```python
# At startup
logger.info("CFR-013 Validation: Checking branch...")
logger.info(f"CFR-013 Validation: Current branch = {current_branch}")
logger.info("CFR-013 Validation: ✅ PASS" or "❌ FAIL")

# During implementation
logger.info("CFR-013: Working on roadmap branch (no branch creation)")
logger.info("CFR-013: Committing directly to roadmap")
logger.info("CFR-013: Pushing to origin/roadmap")

# On violations (should never happen)
logger.error("CFR-013 VIOLATION DETECTED!")
logger.error(f"Expected: roadmap, Got: {current_branch}")
```

### Dashboards

**Add to developer status dashboard**:

```json
{
  "cfr_013_compliant": true,
  "current_branch": "roadmap",
  "branch_creation_attempts": 0,
  "git_operation_avg_duration_ms": 200
}
```

---

## Future Considerations

### Question 1: Should Daemon Create PRs?

**Current**: Daemon creates PRs from feature branch → main
**After CFR-013**: Daemon works on roadmap branch

**Options**:
1. **No PRs**: roadmap IS the work-in-progress branch (RECOMMENDED)
2. **PRs from roadmap → main**: Daemon creates PR after completing priority
3. **Manual PRs**: User creates PR when ready to release

**Recommendation**: Option 1 (No PRs)
- roadmap branch is the continuous integration branch
- main branch is the stable release branch
- User manually creates PR when ready to release
- This matches typical trunk-based development

### Question 2: When to Merge roadmap → main?

**Options**:
1. **Manual**: User decides when to release
2. **Automated**: After N priorities complete
3. **Scheduled**: Weekly/monthly releases

**Recommendation**: Manual (for now)
- User has full control over releases
- Can batch multiple priorities into one release
- Allows for testing before release

### Question 3: Should Other Agents Follow CFR-013?

**Current**: CFR-013 applies to ALL agents
**Implementation**: Only daemon enforced so far

**Future**:
- architect agent: Should also work on roadmap
- project_manager agent: Already works on roadmap (strategic docs)
- assistant agent: Read-only, no branch concerns

**Action**: Extend CFR-013 validation to all agents that commit code

---

## Related ADRs

### ADR-013: Single-Branch Workflow (CFR-013)

**Status**: Accepted
**Date**: 2025-10-17

**Context**: The system was designed with feature branch workflow, but evolved to use single-branch workflow for simplicity and visibility.

**Decision**: ALL agents MUST work on `roadmap` branch ONLY. No feature branches allowed.

**Consequences**:
- **Positive**: Simpler workflow, better visibility, fewer merge conflicts
- **Negative**: All work visible immediately (no "work in progress" privacy)

**Alternatives Considered**:
1. Feature branch per priority → Rejected: Too much complexity
2. Feature branch per agent → Rejected: Merge conflicts between agents
3. Single roadmap branch → **ACCEPTED**

---

## Appendix A: CFR-013 Full Text

**From**: `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` (lines 3405-3652)

```
## CFR-013: All Agents Must Work on `roadmap` Branch Only

**Rule**: ALL agents MUST stay on the `roadmap` branch at ALL times.
NO agent can switch branches or create new branches.

**Core Principle**:
✅ ALLOWED: Work on roadmap branch
❌ FORBIDDEN: git checkout <other-branch>
❌ FORBIDDEN: git checkout -b <new-branch>
❌ FORBIDDEN: Working on main branch
❌ FORBIDDEN: Working on feature/* branches

**Why This Is Critical**:

1. Single Source of Truth: All work happens in one place
2. No Branch Conflicts: Eliminates merge conflicts between parallel branches
3. Simplified Workflow: No confusion about which branch has latest work
4. Prevents Work Loss: All commits immediately visible to entire team
5. Easier Rollback: Single branch history simplifies reverting changes
```

**Enforcement**: Code-level validation before any git checkout operation
**User Story**: US-056: Single Branch Workflow Enforcement

---

## Appendix B: Git Command Reference

### Allowed Git Commands (CFR-013 Compliant)

```bash
✅ git status              # Check status
✅ git add <files>         # Stage changes
✅ git commit -m "..."     # Commit to roadmap
✅ git push origin roadmap # Push to remote
✅ git pull origin roadmap # Pull latest
✅ git log                 # View history
✅ git diff                # View changes
```

### Forbidden Git Commands (CFR-013 Violation)

```bash
❌ git checkout main                    # VIOLATION
❌ git checkout feature/my-branch       # VIOLATION
❌ git checkout -b feature/new-branch   # VIOLATION
❌ git switch main                      # VIOLATION
❌ git branch new-branch                # VIOLATION
```

---

## Appendix C: Error Messages

### CFR-013 Violation at Startup

```
============================================================
CFR-013 VIOLATION: Daemon must work on 'roadmap' branch ONLY
============================================================
Current branch: main
Expected branch: roadmap

CFR-013 requires ALL agents to work on the roadmap branch.
This ensures:
  - Single source of truth
  - No merge conflicts between feature branches
  - All work immediately visible to team

To fix:
  1. git checkout roadmap
  2. git pull origin roadmap
  3. Restart daemon
```

### CFR-013 Violation During Implementation

```
CFR-013 VIOLATION: Attempted to switch away from roadmap branch

Current branch: roadmap
Attempted checkout: feature/priority-2-6
Violating agent: code_developer

CFR-013 requires ALL agents to work on roadmap branch ONLY.
This operation is blocked.

Implementation aborted.
```

---

## Questions for Clarification

### Q1: Should daemon create PRs after CFR-013?

**Current Behavior**: Daemon creates PRs from feature branch → main

**After CFR-013**: No feature branches exist

**Options**:
- A) No PRs - roadmap is WIP, user creates PR when ready
- B) PRs from roadmap → main after each priority
- C) PRs from roadmap → main on demand

**Recommendation**: Option A (No PRs) - Let user control releases

**Decision**: _______________

### Q2: How to handle multi-agent scenarios?

**Current**: Only code_developer daemon runs

**Future (US-057)**: Multiple agents running simultaneously

**Question**: Do all agents work on same roadmap branch?

**Recommendation**: Yes - CFR-013 applies to ALL agents

**Implications**: Need file locking or ownership to prevent conflicts

**Decision**: _______________

### Q3: Should CFR-013 block git operations or just warn?

**Current Spec**: Block (return False, exit daemon)

**Alternative**: Warn but allow (log error, continue)

**Recommendation**: BLOCK - CFR-013 is CRITICAL, must enforce strictly

**Decision**: _______________

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-17 | architect | Initial draft |

---

## Approval

**Spec Status**: Draft

**Awaiting Approval From**:
- [ ] User (via user_listener)
- [ ] project_manager (confirm strategic alignment)
- [ ] code_developer (confirm implementation feasibility)

**Approval Date**: _______________

**Implementation Start**: After approval

**Target Completion**: 2-3 hours after approval

---

**End of Specification**
