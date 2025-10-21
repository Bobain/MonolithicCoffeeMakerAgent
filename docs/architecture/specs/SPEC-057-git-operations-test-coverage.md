# SPEC-057: Git Operations Test Coverage Expansion

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: code-searcher refactoring_priorities_2025-10-17.md (Priority 2.2)
**Priority**: HIGH
**Impact**: HIGH (Reliability)

---

## Problem Statement

### Current State

Git operations in `daemon_git_ops.py` have **basic tests** but are missing **critical edge cases**:

- **Merge conflicts**: Recovery behavior untested
- **Network errors**: Git fetch timeout, push failure handling
- **Concurrent operations**: Merge during fetch not tested
- **Branch state changes**: Detached HEAD, branch deletion
- **File conflicts**: Multiple conflict markers

### code-searcher Finding

> **Test Coverage Gaps: Git Operations**
> - Location: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon_git_ops.py`
> - Current Coverage: ~55%
> - Target Coverage: 80%+
> - Missing Scenarios: Merge conflicts, network errors, concurrent operations
> - Effort: 8 hours
> - Impact: HIGH (prevents production git failures)

### Why This Matters

- **Production Failures**: Untested merge conflicts crash daemon in production
- **Data Loss Risk**: Failed git operations can lose work
- **User Frustration**: Cryptic git error messages confuse users
- **Debugging Time**: Hard to reproduce git issues without tests

**Goal**: Achieve **80%+ test coverage** for git operations with focus on error paths

---

## Proposed Solution

### Related Guidelines

For implementation guidance on testing strategies and git workflows, see:
- [GUIDELINE-016: Testing Strategy](../../guidelines/GUIDELINE-016-testing-strategy.md) - Unit, integration, and E2E testing approaches
- [GUIDELINE-021: Git Workflow](../../guidelines/GUIDELINE-021-git-workflow.md) - Git commit and branch best practices

### Simplified Approach (per ADR-003)

Add **targeted test scenarios** for git edge cases:

1. **Merge Conflict Recovery**: Test conflict detection and resolution
2. **Network Error Handling**: Test fetch/push failures
3. **Concurrent Operation Safety**: Test race conditions
4. **Branch State Edge Cases**: Test detached HEAD, deleted branches
5. **File Conflict Scenarios**: Test multiple conflict markers

### Architecture

```
tests/unit/autonomous/
├── test_daemon_git_ops.py              # EXISTING: Basic tests
├── test_git_merge_conflicts.py         # NEW: Merge conflict scenarios
├── test_git_network_errors.py          # NEW: Network failure handling
├── test_git_concurrent_ops.py          # NEW: Concurrency tests
└── test_git_branch_states.py           # NEW: Branch edge cases

tests/ci_tests/
└── test_git_integration.py             # EXPAND: Real git operations
```

**Benefits**:
- **Confidence**: Know git operations work in edge cases
- **Faster Debugging**: Tests reproduce production issues
- **Better Error Messages**: Tests verify user-facing errors
- **Regression Prevention**: Tests catch git bugs early

---

## Component Design

### 1. Merge Conflict Recovery Tests

**File**: `tests/unit/autonomous/test_git_merge_conflicts.py`

```python
import pytest
from unittest.mock import Mock, patch
from coffee_maker.autonomous.daemon_git_ops import GitOpsMixin


class TestGitMergeConflicts:
    """Test merge conflict detection and recovery."""

    def test_merge_conflict_detection(self, mock_git_repo):
        """Test daemon detects merge conflicts."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate merge conflict
        mock_git_repo.merge.side_effect = GitCommandError("Merge conflict")

        result = git_ops._merge_to_roadmap()

        assert result.success is False
        assert "conflict" in result.message.lower()
        assert git_ops._has_merge_conflicts() is True

    def test_merge_conflict_recovery(self, mock_git_repo):
        """Test daemon can recover from merge conflicts."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate conflict
        git_ops._create_merge_conflict()

        # Attempt recovery
        result = git_ops._resolve_merge_conflicts()

        assert result.success is True
        assert git_ops._has_merge_conflicts() is False

    def test_merge_conflict_notification(self, mock_git_repo, mock_notif_db):
        """Test daemon notifies user of merge conflicts."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo
        git_ops.notification_db = mock_notif_db

        # Simulate conflict
        git_ops._merge_to_roadmap()  # Will fail with conflict

        # Verify notification created
        notifications = mock_notif_db.get_all()
        assert len(notifications) > 0
        assert "merge conflict" in notifications[0].message.lower()

    def test_multiple_conflict_markers(self, mock_git_repo):
        """Test handling of multiple conflict markers in same file."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate file with multiple conflicts
        conflicted_content = """
        <<<<<<< HEAD
        Line 1
        =======
        Different line 1
        >>>>>>> roadmap
        Normal line
        <<<<<<< HEAD
        Line 2
        =======
        Different line 2
        >>>>>>> roadmap
        """

        result = git_ops._count_conflict_markers(conflicted_content)

        assert result == 2  # Two distinct conflicts

    def test_abort_merge_on_conflict(self, mock_git_repo):
        """Test daemon can abort merge and return to clean state."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate conflict
        git_ops._create_merge_conflict()

        # Abort merge
        result = git_ops._abort_merge()

        assert result.success is True
        assert git_ops.git.is_dirty() is False
```

### 2. Network Error Handling Tests

**File**: `tests/unit/autonomous/test_git_network_errors.py`

```python
class TestGitNetworkErrors:
    """Test git network error handling."""

    def test_fetch_timeout(self, mock_git_repo):
        """Test git fetch timeout (30s limit)."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate timeout
        mock_git_repo.fetch.side_effect = subprocess.TimeoutExpired(
            cmd="git fetch", timeout=30
        )

        result = git_ops._sync_roadmap_branch()

        assert result.success is False
        assert "timeout" in result.message.lower()

    def test_push_failure_no_network(self, mock_git_repo):
        """Test push failure when network unavailable."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate network error
        mock_git_repo.push.side_effect = GitCommandError(
            "Could not resolve host"
        )

        result = git_ops._push_changes()

        assert result.success is False
        assert "network" in result.message.lower()

    def test_fetch_with_retry(self, mock_git_repo):
        """Test fetch retries on transient network errors."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # First call fails, second succeeds
        mock_git_repo.fetch.side_effect = [
            GitCommandError("Connection reset"),
            None  # Success
        ]

        result = git_ops._sync_roadmap_branch(retry=True)

        assert result.success is True
        assert mock_git_repo.fetch.call_count == 2

    def test_push_rejected_non_fast_forward(self, mock_git_repo):
        """Test push rejection (non-fast-forward)."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate rejected push
        mock_git_repo.push.side_effect = GitCommandError(
            "Updates were rejected because the tip of your current branch"
        )

        result = git_ops._push_changes()

        assert result.success is False
        assert "rejected" in result.message.lower()
        assert "pull first" in result.message.lower()  # User hint
```

### 3. Concurrent Operation Safety Tests

**File**: `tests/unit/autonomous/test_git_concurrent_ops.py`

```python
class TestGitConcurrentOperations:
    """Test concurrent git operation safety."""

    def test_merge_during_fetch(self, mock_git_repo):
        """Test merge attempt while fetch is in progress."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo
        git_ops._fetch_in_progress = True

        result = git_ops._merge_to_roadmap()

        assert result.success is False
        assert "fetch in progress" in result.message.lower()

    def test_push_during_merge(self, mock_git_repo):
        """Test push attempt while merge is in progress."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo
        git_ops._merge_in_progress = True

        result = git_ops._push_changes()

        assert result.success is False
        assert "merge in progress" in result.message.lower()

    def test_concurrent_branch_creation(self, mock_git_repo):
        """Test concurrent branch creation (race condition)."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Simulate race: branch created between check and create
        mock_git_repo.heads.__contains__.return_value = False  # Check: doesn't exist
        mock_git_repo.create_head.side_effect = GitCommandError(
            "branch already exists"  # Create: now exists!
        )

        result = git_ops._create_feature_branch("test")

        # Should handle gracefully
        assert result.success is True  # Not an error, just already exists
        assert "already exists" in result.message.lower()
```

### 4. Branch State Edge Cases Tests

**File**: `tests/unit/autonomous/test_git_branch_states.py`

```python
class TestGitBranchStates:
    """Test git branch state edge cases."""

    def test_detached_head_detection(self, mock_git_repo):
        """Test detection of detached HEAD state."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo
        mock_git_repo.head.is_detached = True

        result = git_ops._check_git_status()

        assert result.warnings.contains("detached HEAD")

    def test_merge_from_detached_head(self, mock_git_repo):
        """Test merge fails gracefully from detached HEAD."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo
        mock_git_repo.head.is_detached = True

        result = git_ops._merge_to_roadmap()

        assert result.success is False
        assert "detached HEAD" in result.message.lower()

    def test_branch_deletion_mid_operation(self, mock_git_repo):
        """Test handling of branch deleted during operation."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo

        # Branch exists during check
        mock_git_repo.heads.__contains__.return_value = True

        # Branch deleted before merge
        mock_git_repo.merge.side_effect = GitCommandError(
            "branch 'roadmap' not found"
        )

        result = git_ops._merge_to_roadmap()

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_uncommitted_changes_block_merge(self, mock_git_repo):
        """Test merge blocked by uncommitted changes."""
        git_ops = GitOpsMixin()
        git_ops.git = mock_git_repo
        mock_git_repo.is_dirty.return_value = True

        result = git_ops._merge_to_roadmap()

        assert result.success is False
        assert "uncommitted changes" in result.message.lower()
```

---

## Technical Details

### Test Infrastructure

**Mock Git Repository**:
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_git_repo():
    """Mock GitPython repo for testing."""
    repo = Mock()
    repo.is_dirty.return_value = False
    repo.head.is_detached = False
    repo.heads = Mock()
    repo.remotes = Mock()
    return repo
```

**Subprocess Mocking**:
```python
@patch('subprocess.run')
def test_git_command_timeout(mock_run):
    """Test git command timeout handling."""
    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd=["git", "fetch"], timeout=30
    )

    git_ops = GitOpsMixin()
    result = git_ops._sync_roadmap_branch()

    assert result.success is False
```

### Coverage Targets

| File | Current | Target | New Tests Needed |
|------|---------|--------|------------------|
| `daemon_git_ops.py` | ~55% | 80% | +15 tests |
| Merge operations | ~40% | 90% | +6 tests |
| Network handling | ~30% | 80% | +4 tests |
| Concurrent safety | ~20% | 70% | +3 tests |
| Branch states | ~50% | 80% | +4 tests |

**Total New Tests**: ~32 test functions

---

## Data Structures

### GitOperationResult

```python
@dataclass
class GitOperationResult:
    """Result of a git operation."""
    success: bool
    message: str
    warnings: list[str] = field(default_factory=list)
    details: Optional[dict] = None
```

---

## Testing Strategy

### Unit Tests (New: 32 tests)

**Coverage by Category**:
- Merge conflicts: 8 tests
- Network errors: 6 tests
- Concurrent operations: 5 tests
- Branch states: 7 tests
- File conflicts: 6 tests

### Integration Tests (Expand existing)

**`tests/ci_tests/test_git_integration.py`**:
```python
def test_real_merge_conflict_scenario(tmp_git_repo):
    """Test merge conflict with real git repo."""
    # Create two divergent branches
    # Attempt merge
    # Verify conflict detection
    # Verify recovery
    pass

def test_real_network_timeout(tmp_git_repo):
    """Test git fetch timeout with real repo."""
    # Configure remote with slow response
    # Attempt fetch with 5s timeout
    # Verify timeout handling
    pass
```

### Manual Testing

```bash
# Test merge conflict recovery
# 1. Create conflicting changes in roadmap branch
# 2. Run daemon
# 3. Verify notification created
# 4. Verify daemon doesn't crash

# Test network failure
# 1. Disconnect network
# 2. Run daemon
# 3. Verify graceful error handling
```

---

## Rollout Plan

### Week 1: Merge Conflict Tests (3 hours)
- **Day 1**: Write merge conflict tests (2 hours)
- **Day 1**: Integration test for real merge conflict (1 hour)

### Week 2: Network & Concurrency Tests (3 hours)
- **Day 1**: Write network error tests (1.5 hours)
- **Day 2**: Write concurrent operation tests (1.5 hours)

### Week 3: Branch State Tests (2 hours)
- **Day 1**: Write branch state edge case tests (2 hours)

**Total Timeline**: 3 weeks (8 hours actual work)

---

## Risks & Mitigations

### Risk 1: Flaky Tests (Git Timing)
**Likelihood**: MEDIUM
**Impact**: HIGH (CI unreliable)
**Mitigation**:
- Use mocks for unit tests (deterministic)
- Use controlled git repos for integration tests
- Add retries for flaky integration tests

### Risk 2: Test Complexity (Hard to Understand)
**Likelihood**: MEDIUM
**Impact**: MEDIUM
**Mitigation**:
- Clear docstrings for each test
- Helper functions for common setups
- Comments explaining git states

### Risk 3: Slow Integration Tests
**Likelihood**: MEDIUM
**Impact**: LOW (longer CI time)
**Mitigation**:
- Mark integration tests with `@pytest.mark.slow`
- Run only unit tests in development
- Optimize git repo creation (use templates)

---

## Success Criteria

### Quantitative
- ✅ `daemon_git_ops.py` coverage ≥80% (from ~55%)
- ✅ All merge conflict scenarios tested
- ✅ All network error scenarios tested
- ✅ Concurrent operation safety verified
- ✅ Branch state edge cases covered
- ✅ Zero new regressions in git operations

### Qualitative
- ✅ Developers confident in git error handling
- ✅ Production git failures reduced
- ✅ Easier to reproduce git bugs
- ✅ Better error messages for users

---

## Related Work

### Depends On
- None (independent testing improvement)

### Enables
- **Confident Autonomous Operation**: Daemon can handle git errors
- **Better User Experience**: Clear error messages for git issues
- **Faster Debugging**: Tests reproduce production issues

### Related Specs
- **SPEC-053**: Test coverage expansion (this is part of it)

---

## Future Enhancements

### After This Implementation
1. **Performance Tests**: Benchmark git operations
2. **Large Repo Tests**: Test with 1000+ commits
3. **Submodule Tests**: Handle git submodules
4. **LFS Tests**: Handle git LFS files

---

## Appendix A: Test Scenarios Matrix

### Merge Conflicts

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Single conflict | `test_merge_conflict_detection` | Detect and notify |
| Multiple conflicts | `test_multiple_conflict_markers` | Count all conflicts |
| Conflict recovery | `test_merge_conflict_recovery` | Resolve and continue |
| Abort merge | `test_abort_merge_on_conflict` | Clean state restored |

### Network Errors

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Fetch timeout | `test_fetch_timeout` | Graceful timeout handling |
| Push failure | `test_push_failure_no_network` | User-friendly error |
| Retry logic | `test_fetch_with_retry` | Automatic retry |
| Non-fast-forward | `test_push_rejected_non_fast_forward` | Suggest pull first |

### Concurrent Operations

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Merge during fetch | `test_merge_during_fetch` | Block and warn |
| Push during merge | `test_push_during_merge` | Block and warn |
| Concurrent branch creation | `test_concurrent_branch_creation` | Handle race gracefully |

### Branch States

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Detached HEAD | `test_detached_head_detection` | Warn user |
| Merge from detached | `test_merge_from_detached_head` | Fail gracefully |
| Branch deletion | `test_branch_deletion_mid_operation` | Handle gracefully |
| Uncommitted changes | `test_uncommitted_changes_block_merge` | Block merge |

---

## Appendix B: Coverage Report Example

**Before (55% coverage)**:
```
Name                          Stmts   Miss  Cover   Missing
---------------------------------------------------------
daemon_git_ops.py               150    68    55%   80-120, 140-160
  _merge_to_roadmap              30    18    40%   5-12, 20-28
  _sync_roadmap_branch           25    18    28%   8-20
  _push_changes                  20    12    40%   10-18
---------------------------------------------------------
TOTAL                           150    68    55%
```

**After (80% coverage)**:
```
Name                          Stmts   Miss  Cover   Missing
---------------------------------------------------------
daemon_git_ops.py               150    30    80%   145-150
  _merge_to_roadmap              30     3    90%   28-30
  _sync_roadmap_branch           25     5    80%   22-24
  _push_changes                  20     4    80%   18-19
---------------------------------------------------------
TOTAL                           150    30    80%
```

**Improvement**: +25% coverage, all critical paths tested

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 8 hours
**Actual Effort**: TBD (track during implementation)
