# SPEC-053: Test Coverage Expansion

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CODE_QUALITY_ANALYSIS_2025-10-17.md (Finding #4)
**Priority**: MEDIUM
**Impact**: HIGH (Reliability)

---

## Problem Statement

### Current State
Test coverage is estimated at **60-70%**, leaving critical paths untested:
- **Daemon crash recovery** - Not fully tested
- **Context reset logic** - Edge cases missing
- **Git operation failures** - Partial coverage
- **Notification workflow** - Integration gaps
- **Error handling paths** - Many uncovered

### code-searcher Finding
> "Test Coverage Gaps
> Files: Several autonomous modules
> Observation: 90 test files exist, but critical paths may lack coverage
> Areas: Crash recovery, context reset, git edge cases, notification workflow
> Recommendation: Run coverage analysis, expand to 70-80%
> Effort: 3-5 hours initial setup
> Impact: Improved reliability"

### Why This Matters
- **Production Incidents**: Untested paths fail in production
- **Regression Risk**: Changes break untested functionality
- **Confidence**: Low confidence in autonomous operation
- **Debugging Time**: Harder to identify root cause without tests

**Goal**: Achieve **75%+ test coverage** with focus on critical paths

---

## Proposed Solution

### Simplified Approach (per ADR-003)

Expand test coverage in **3 phases**:
1. **Measure Current Coverage** (establish baseline)
2. **Target Critical Gaps** (daemon, git, notifications)
3. **Incremental Expansion** (add tests for uncovered paths)

### Architecture

```
tests/
├── unit/                           # Unit tests (isolated)
│   ├── autonomous/
│   │   ├── test_daemon_recovery.py      # NEW: Crash recovery
│   │   ├── test_context_reset.py        # NEW: Context edge cases
│   │   ├── test_git_failures.py         # NEW: Git error paths
│   │   └── test_notification_flow.py    # NEW: Notification workflow
│   └── ...
│
├── ci_tests/                       # Integration tests
│   ├── test_daemon_integration.py       # EXPAND: More scenarios
│   ├── test_git_integration.py          # EXPAND: Failure cases
│   └── test_notification_integration.py # EXPAND: Edge cases
│
└── coverage/                       # Coverage reports (NEW)
    ├── .coverage                   # Coverage data
    └── htmlcov/                    # HTML report
```

**Benefits**:
- **Visibility**: Know what's tested, what's not
- **Targeted**: Focus on high-impact areas first
- **Incremental**: Add tests over time (not all at once)
- **CI Integration**: Automated coverage checks

---

## Component Design

### 1. Coverage Measurement Setup

**Install Coverage Tool** (already in pyproject.toml):
```toml
[tool.pytest.ini_options]
addopts = "--cov=coffee_maker --cov-report=html --cov-report=term-missing"
```

**Run Coverage Analysis**:
```bash
# Generate coverage report
pytest --cov=coffee_maker --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html

# View terminal summary
pytest --cov=coffee_maker --cov-report=term-missing
```

### 2. Critical Coverage Gaps (Priority Targets)

Based on code-searcher findings:

#### Gap 1: Daemon Crash Recovery
**File**: `daemon.py`
**Missing Coverage**: Lines 150-180 (crash recovery logic)

**New Test**: `tests/unit/autonomous/test_daemon_recovery.py`
```python
import pytest
from coffee_maker.autonomous.daemon import DevDaemon


class TestDaemonCrashRecovery:
    def test_recovery_after_crash(self, tmp_path):
        """Test daemon recovers from unexpected crash."""
        daemon = DevDaemon()

        # Simulate crash (exception mid-execution)
        with pytest.raises(RuntimeError):
            daemon._simulate_crash()  # Test helper

        # Verify daemon can recover
        daemon.recover_from_crash()
        assert daemon.status == "recovered"

    def test_context_preserved_after_crash(self):
        """Test context is preserved across crashes."""
        daemon = DevDaemon()
        daemon.set_current_priority("PRIORITY 5")

        # Crash and recover
        daemon._simulate_crash()
        daemon.recover_from_crash()

        # Context should be preserved
        assert daemon.get_current_priority() == "PRIORITY 5"

    def test_cleanup_on_crash(self):
        """Test cleanup happens even on crash."""
        daemon = DevDaemon()

        try:
            daemon._simulate_crash()
        except:
            pass

        # Verify cleanup occurred
        assert not daemon._temp_files_exist()
```

#### Gap 2: Context Reset Logic
**File**: `daemon.py`
**Missing Coverage**: Lines 200-230 (context reset edge cases)

**New Test**: `tests/unit/autonomous/test_context_reset.py`
```python
class TestContextReset:
    def test_reset_with_active_priority(self):
        """Test context reset while priority is active."""
        daemon = DevDaemon()
        daemon.set_current_priority("PRIORITY 5")

        daemon.reset_context()

        assert daemon.get_current_priority() is None

    def test_reset_with_pending_notifications(self):
        """Test context reset clears pending notifications."""
        daemon = DevDaemon()
        daemon._add_pending_notification("test")

        daemon.reset_context()

        assert len(daemon._get_pending_notifications()) == 0

    def test_reset_preserves_config(self):
        """Test context reset doesn't clear configuration."""
        daemon = DevDaemon()
        original_config = daemon.config

        daemon.reset_context()

        assert daemon.config == original_config
```

#### Gap 3: Git Operation Failures
**File**: `daemon_git_ops.py`
**Missing Coverage**: Lines 80-120 (git error handling)

**New Test**: `tests/unit/autonomous/test_git_failures.py`
```python
class TestGitFailures:
    def test_branch_creation_fails_already_exists(self):
        """Test graceful handling when branch already exists."""
        git_ops = GitOpsMixin()

        # Create branch
        git_ops.create_branch("feature/test")

        # Try to create again (should handle gracefully)
        result = git_ops.create_branch("feature/test")
        assert result.success is False
        assert "already exists" in result.message

    def test_commit_fails_no_changes(self):
        """Test graceful handling when no changes to commit."""
        git_ops = GitOpsMixin()

        result = git_ops.commit_changes("No changes")
        assert result.success is False
        assert "nothing to commit" in result.message

    def test_push_fails_no_upstream(self):
        """Test graceful handling when no upstream configured."""
        git_ops = GitOpsMixin()

        result = git_ops.push_to_remote()
        assert result.success is False
        assert "no upstream" in result.message
```

#### Gap 4: Notification Workflow
**File**: `notifications.py`
**Missing Coverage**: Lines 100-150 (notification edge cases)

**New Test**: `tests/unit/autonomous/test_notification_flow.py`
```python
class TestNotificationWorkflow:
    def test_respond_to_nonexistent_notification(self):
        """Test responding to notification that doesn't exist."""
        notif_db = NotificationDB()

        result = notif_db.respond(999, "approve")
        assert result.success is False
        assert "not found" in result.message

    def test_respond_to_already_responded_notification(self):
        """Test responding to notification already responded to."""
        notif_db = NotificationDB()
        notif_id = notif_db.add("Test")

        # First response
        notif_db.respond(notif_id, "approve")

        # Second response (should fail)
        result = notif_db.respond(notif_id, "approve")
        assert result.success is False
        assert "already responded" in result.message

    def test_notification_expiration(self):
        """Test notifications expire after timeout."""
        notif_db = NotificationDB()
        notif_id = notif_db.add("Test", expires_in_hours=1)

        # Simulate time passing
        notif_db._advance_time(hours=2)

        # Should be expired
        assert notif_db.is_expired(notif_id) is True
```

### 3. Integration Test Expansion

**Expand**: `tests/ci_tests/test_daemon_integration.py`
```python
class TestDaemonIntegration:
    def test_full_priority_workflow_with_errors(self):
        """Test daemon handles errors during priority execution."""
        daemon = DevDaemon()

        # Priority that will cause error
        daemon.roadmap.add_priority({
            "name": "PRIORITY 99",
            "title": "Invalid priority",
            "content": "This will fail"
        })

        # Should handle gracefully
        result = daemon.execute_priority("PRIORITY 99")
        assert result.success is False
        assert daemon.status == "error_handled"

    def test_daemon_stops_on_user_interrupt(self):
        """Test daemon stops cleanly on Ctrl+C."""
        daemon = DevDaemon()

        # Simulate KeyboardInterrupt
        with pytest.raises(KeyboardInterrupt):
            daemon._simulate_interrupt()

        # Should clean up gracefully
        assert daemon.status == "stopped_by_user"
```

---

## Technical Details

### Coverage Measurement Commands

**Basic Coverage**:
```bash
pytest --cov=coffee_maker
```

**HTML Report** (recommended):
```bash
pytest --cov=coffee_maker --cov-report=html
open htmlcov/index.html
```

**Terminal Report with Missing Lines**:
```bash
pytest --cov=coffee_maker --cov-report=term-missing
```

**Coverage for Specific Module**:
```bash
pytest --cov=coffee_maker.autonomous tests/unit/autonomous/
```

**Coverage Diff** (compare with previous run):
```bash
pytest --cov=coffee_maker --cov-report=term:skip-covered
```

### Coverage Targets by Module

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| daemon.py | ~60% | 85% | HIGH |
| daemon_git_ops.py | ~55% | 80% | HIGH |
| notifications.py | ~65% | 80% | MEDIUM |
| daemon_implementation.py | ~70% | 85% | MEDIUM |
| daemon_spec_manager.py | ~75% | 85% | LOW |
| CLI commands | ~70% | 75% | LOW |

**Overall Target**: 75% → 85% over 3 sprints

### Test Categories

**Unit Tests** (isolated, fast):
- Mock external dependencies
- Test single functions/methods
- Edge cases and error paths
- Aim for >90% coverage

**Integration Tests** (realistic, slower):
- Real file system operations
- Actual git commands (in isolated repo)
- End-to-end workflows
- Aim for >70% coverage

**Manual Tests** (exploratory):
- User-facing features
- Performance under load
- Visual/UX validation

---

## Implementation Strategy

### Phase 1: Measure & Baseline (Week 1)

**Day 1: Setup Coverage Tools** (1 hour)
```bash
# Already in pyproject.toml, just verify
poetry run pytest --cov=coffee_maker --cov-report=html

# Add to .gitignore
echo "htmlcov/" >> .gitignore
echo ".coverage" >> .gitignore
```

**Day 1: Generate Baseline Report** (30 min)
```bash
# Run full test suite with coverage
pytest --cov=coffee_maker --cov-report=html --cov-report=term-missing > coverage_baseline.txt

# Identify gaps
# Look for lines with "!" (not covered)
```

**Day 2: Document Gaps** (1 hour)
- List all uncovered lines by module
- Prioritize by impact (daemon > CLI > utils)
- Create test plan (which tests to add)

### Phase 2: Target Critical Gaps (Week 2)

**Day 1: Daemon Tests** (3 hours)
- Create `test_daemon_recovery.py` (1 hour)
- Create `test_context_reset.py` (1 hour)
- Run tests, verify coverage increase (1 hour)

**Day 2: Git & Notification Tests** (3 hours)
- Create `test_git_failures.py` (1.5 hours)
- Create `test_notification_flow.py` (1.5 hours)

**Day 3: Integration Tests** (2 hours)
- Expand `test_daemon_integration.py` (1 hour)
- Expand `test_git_integration.py` (1 hour)

### Phase 3: Incremental Expansion (Ongoing)

**Week 3+: Add Tests as You Go**
- New feature → New tests
- Bug fix → Test for regression
- Refactoring → Maintain coverage

**Coverage Gate**: Don't merge PRs that decrease coverage

---

## Testing Strategy

### Coverage Gates (CI/CD)

**Add to `.github/workflows/test.yml`** (if using GitHub Actions):
```yaml
- name: Run tests with coverage
  run: |
    poetry run pytest --cov=coffee_maker --cov-report=term-missing --cov-fail-under=75
    # Fails if coverage < 75%
```

**Add to `pyproject.toml`**:
```toml
[tool.coverage.run]
source = ["coffee_maker"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    "raise AssertionError",
    "raise NotImplementedError",
]
fail_under = 75  # Fail if coverage < 75%
```

### Test Pyramid

```
      /\
     /  \    E2E Tests (5%)
    /----\   - Full system tests
   /      \  - Manual testing
  /--------\ Integration Tests (25%)
 /          \ - Multi-component
/------------\ - Real dependencies
/--------------\ Unit Tests (70%)
                - Fast, isolated
                - Edge cases
```

**Our Target**:
- 70% unit tests (fast feedback)
- 25% integration tests (realistic scenarios)
- 5% E2E tests (critical paths only)

---

## Rollout Plan

### Week 1: Setup & Baseline
- **Day 1**: Setup coverage tools, generate baseline (1.5 hours)
- **Day 2**: Document gaps, create test plan (1 hour)

### Week 2: Critical Tests
- **Day 1**: Daemon recovery & context tests (3 hours)
- **Day 2**: Git & notification tests (3 hours)
- **Day 3**: Integration tests (2 hours)

### Week 3: Validation
- **Day 1**: Run full coverage, validate 75%+ (1 hour)
- **Day 2**: Fix any remaining gaps (2 hours)
- **Day 3**: Document coverage strategy (1 hour)

**Total Timeline**: 3 weeks (14.5 hours actual work)

---

## Risks & Mitigations

### Risk 1: Coverage Doesn't Reach 75%
**Likelihood**: MEDIUM
**Impact**: MEDIUM (still better than 60%)
**Mitigation**:
- Focus on critical paths first (daemon, git)
- Accept 70-72% if high-value tests added
- Continue incremental expansion

### Risk 2: Tests Break Existing Functionality
**Likelihood**: LOW
**Impact**: MEDIUM
**Mitigation**:
- Isolate new tests (separate files)
- Use mocks for external dependencies
- Run full suite before commit

### Risk 3: Slow Test Suite
**Likelihood**: MEDIUM
**Impact**: LOW (CI takes longer)
**Mitigation**:
- Use pytest markers (`@pytest.mark.slow`)
- Run fast tests in development, all in CI
- Optimize slow integration tests

### Risk 4: Flaky Tests (Intermittent Failures)
**Likelihood**: MEDIUM
**Impact**: HIGH (CI unreliable)
**Mitigation**:
- Avoid time-dependent tests (use mocks)
- Seed random values (deterministic)
- Retry flaky tests (pytest-rerunfailures)

---

## Success Criteria

### Quantitative
- ✅ Overall coverage ≥75% (target: 80%)
- ✅ Daemon module coverage ≥85%
- ✅ Git operations coverage ≥80%
- ✅ Notification workflow coverage ≥80%
- ✅ All critical paths have tests
- ✅ CI fails if coverage drops below 75%

### Qualitative
- ✅ Developers confident in autonomous operation
- ✅ Bug fix rate decreases (fewer regressions)
- ✅ Easier to refactor (tests catch breaks)
- ✅ New contributors understand codebase via tests

---

## Coverage Report Example

**Before (60% coverage)**:
```
Name                          Stmts   Miss  Cover   Missing
---------------------------------------------------------
daemon.py                       200    80    60%   150-180, 200-230
daemon_git_ops.py               150    68    55%   80-120, 140-160
notifications.py                120    42    65%   100-150
---------------------------------------------------------
TOTAL                          1200   480    60%
```

**After (75% coverage)**:
```
Name                          Stmts   Miss  Cover   Missing
---------------------------------------------------------
daemon.py                       200    30    85%   195-200
daemon_git_ops.py               150    30    80%   145-150
notifications.py                120    24    80%   140-145
---------------------------------------------------------
TOTAL                          1200   300    75%
```

**Improvement**: +15% coverage, critical paths now tested

---

## Related Work

### Depends On
- None (independent testing improvement)

### Enables
- **SPEC-050**: CLI refactor (easier to test modular code)
- **SPEC-052**: Error handling (test all error paths)
- **Future**: Confident autonomous operation

### Related Specs
- All specs benefit from improved test coverage

---

## Future Enhancements

### After This Implementation
1. **Mutation Testing**: Verify tests actually catch bugs
2. **Property-Based Testing**: Use Hypothesis for edge cases
3. **Performance Tests**: Benchmark critical paths
4. **Snapshot Testing**: UI/output regression tests

---

## Appendix A: Coverage Commands Reference

### Generate Coverage

```bash
# Basic coverage report
pytest --cov=coffee_maker

# HTML report (interactive)
pytest --cov=coffee_maker --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=coffee_maker --cov-report=term-missing

# Only show uncovered (skip fully covered)
pytest --cov=coffee_maker --cov-report=term:skip-covered

# Coverage for specific directory
pytest --cov=coffee_maker.autonomous tests/unit/autonomous/

# Fail if coverage below threshold
pytest --cov=coffee_maker --cov-fail-under=75
```

### Coverage Diff

```bash
# Compare with previous run
pytest --cov=coffee_maker --cov-report=diff:previous_coverage.txt
```

### Coverage by File

```bash
# Sort by coverage %
pytest --cov=coffee_maker --cov-report=term | sort -k4 -n
```

---

## Appendix B: Test Organization

### Directory Structure

```
tests/
├── unit/                           # Unit tests (fast, isolated)
│   ├── autonomous/
│   │   ├── test_daemon.py
│   │   ├── test_daemon_recovery.py      # NEW
│   │   ├── test_context_reset.py        # NEW
│   │   ├── test_git_failures.py         # NEW
│   │   └── test_notification_flow.py    # NEW
│   ├── cli/
│   │   ├── test_roadmap_cli.py
│   │   └── test_error_handler.py        # From SPEC-052
│   └── utils/
│       └── test_prompt_builders.py      # From SPEC-051
│
├── ci_tests/                       # Integration tests (realistic)
│   ├── test_daemon_integration.py       # EXPAND
│   ├── test_git_integration.py          # EXPAND
│   └── test_notification_integration.py # EXPAND
│
└── coverage/                       # Coverage reports
    ├── .coverage
    └── htmlcov/
```

### Test Naming Convention

- `test_<module>.py` - Unit tests for module
- `test_<module>_integration.py` - Integration tests
- `test_<feature>_<scenario>.py` - Specific scenario tests

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 14.5 hours (over 3 weeks)
**Actual Effort**: TBD
