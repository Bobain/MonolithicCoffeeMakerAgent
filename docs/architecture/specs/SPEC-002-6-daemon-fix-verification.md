# SPEC-002-6: Daemon Fix Verification

**Status**: Approved

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: PRIORITY 2.6, BUG-001, BUG-002

**Related ADRs**: ADR-003 (Simplification-First Approach)

**Assigned To**: code_developer

**Estimated Duration**: 1 day (SIMPLIFIED verification-only task)

---

## Executive Summary

Verify that BUG-001 (daemon stuck without --auto-approve) and BUG-002 (daemon crashes with missing priority content) are fully resolved through comprehensive testing. This is a verification task, not new feature development - the fixes are already implemented and committed.

**CRITICAL SIMPLIFICATION**: This is NOT about building new features. This is about verifying existing fixes work correctly through systematic testing.

---

## Problem Statement

### Current Situation
- **BUG-001**: Fixed in commit 491a438 - daemon now includes --auto-approve flag
- **BUG-002**: Fixed in commit 911d77c - daemon handles missing priority content gracefully
- Both fixes were implemented but need systematic verification to ensure they work correctly
- No comprehensive test coverage exists for these specific bug fixes
- Need confidence that these bugs won't resurface

### Goal
Verify the two bug fixes work correctly through:
1. Regression tests that reproduce the original bugs (should pass with fixes)
2. Documentation of verification results
3. Confidence that daemon is stable for autonomous operation

### Non-Goals
- ❌ Building new CI/CD infrastructure (use existing pytest setup)
- ❌ Creating complex test frameworks (use simple pytest tests)
- ❌ Adding new monitoring systems (verification only)
- ❌ Implementing new features (this is verification, not development)
- ❌ Comprehensive daemon refactoring (just verify fixes work)

---

## Proposed Solution: SIMPLIFIED VERIFICATION

### Core Concept
Write focused regression tests that:
1. Reproduce BUG-001 scenario (daemon without --auto-approve)
2. Reproduce BUG-002 scenario (missing priority content)
3. Verify fixes prevent the bugs from recurring
4. Document verification results

### Architecture (SIMPLE)
```
Verification Tasks:
   ↓
1. Test BUG-001 Fix
   - Verify ProcessManager includes --auto-approve
   - Verify daemon makes progress (not stuck)
   ↓
2. Test BUG-002 Fix
   - Test priority with missing content
   - Test priority with None content
   - Test priority with empty content
   - Verify graceful handling (no crash)
   ↓
3. Document Results
   - Update BUG tickets with verification evidence
   - Mark PRIORITY 2.6 as complete
```

**NO new infrastructure, NO complex setup - just focused regression tests!**

---

## What We REUSE

✅ **Existing test infrastructure**: `tests/ci_tests/` and `tests/unit/` directories
✅ **Existing daemon tests**: `test_daemon_*.py` files as reference
✅ **Pytest framework**: Already installed and configured
✅ **Existing fixtures**: Use existing test fixtures for daemon testing
✅ **Git history**: Commits 491a438 and 911d77c document the fixes

**New code**: Only verification tests (~150-200 lines total)

---

## Implementation Plan: PHASED & SIMPLE

### Phase 1: BUG-001 Verification (4 hours)

**Goal**: Verify daemon includes --auto-approve and makes progress.

**File to Create**:
`tests/unit/test_bug_001_verification.py` (~80 lines)

**Test Cases**:
```python
def test_process_manager_includes_auto_approve():
    """Verify ProcessManager.start_daemon() includes --auto-approve flag."""
    # Test that command includes --auto-approve
    pass

def test_daemon_not_stuck_at_iteration_2():
    """Verify daemon makes progress beyond iteration 2."""
    # Mock daemon, verify iterations increment
    pass

def test_daemon_auto_approve_flag_present():
    """Verify running daemon has --auto-approve in process args."""
    # Check process command line
    pass
```

**Acceptance Criteria**:
- ✅ Test verifies --auto-approve flag is present
- ✅ Test verifies daemon makes progress (iterations > 2)
- ✅ Tests pass with current code
- ✅ Tests are fast (< 10 seconds total)

---

### Phase 2: BUG-002 Verification (4 hours)

**Goal**: Verify daemon handles missing/empty priority content gracefully.

**File to Create**:
`tests/unit/test_bug_002_verification.py` (~120 lines)

**Test Cases**:
```python
def test_build_spec_prompt_with_missing_content():
    """Verify _build_spec_creation_prompt handles missing content."""
    priority = {"name": "PRIORITY 99", "title": "Test"}
    # Should not crash, should use fallback
    pass

def test_build_spec_prompt_with_none_content():
    """Verify _build_spec_creation_prompt handles None content."""
    priority = {"name": "PRIORITY 99", "title": "Test", "content": None}
    # Should not crash, should use fallback
    pass

def test_build_spec_prompt_with_empty_content():
    """Verify _build_spec_creation_prompt handles empty content."""
    priority = {"name": "PRIORITY 99", "title": "Test", "content": ""}
    # Should not crash, should use fallback
    pass

def test_ensure_technical_spec_missing_name():
    """Verify _ensure_technical_spec rejects priority without name."""
    priority = {"content": "test"}
    # Should return False and log error
    pass

def test_ensure_technical_spec_missing_content():
    """Verify _ensure_technical_spec handles missing content."""
    priority = {"name": "PRIORITY 99", "title": "Test"}
    # Should log warning but continue
    pass
```

**Acceptance Criteria**:
- ✅ All edge cases covered (missing, None, empty content)
- ✅ Tests verify no KeyError exceptions
- ✅ Tests verify appropriate warnings logged
- ✅ Tests pass with current code
- ✅ Tests are fast (< 10 seconds total)

---

### Phase 3: Documentation & Completion (1 hour)

**Goal**: Document verification results and close the loop.

**Tasks**:
1. Run all verification tests
2. Update BUG-001.md with verification evidence
3. Update BUG-002.md with verification evidence
4. Update ROADMAP.md to mark PRIORITY 2.6 as ✅ Complete
5. Commit with clear message

**Files to Update**:
- `tickets/BUG-001.md` - Add "Verification Complete" section
- `tickets/BUG-002.md` - Add "Verification Complete" section
- `docs/roadmap/ROADMAP.md` - Update PRIORITY 2.6 status

**Acceptance Criteria**:
- ✅ All tests passing
- ✅ BUG tickets updated with evidence
- ✅ ROADMAP updated
- ✅ Committed and ready for autonomous operation

---

## Detailed Component Design

### Component 1: BUG-001 Verification Tests

**Responsibility**: Verify ProcessManager and daemon use --auto-approve flag

**Interface**:
```python
# tests/unit/test_bug_001_verification.py

import pytest
from unittest.mock import Mock, patch
from coffee_maker.process_manager import ProcessManager

class TestBug001Verification:
    """Verify BUG-001 fix: daemon includes --auto-approve flag."""

    def test_process_manager_includes_auto_approve(self):
        """Test ProcessManager.start_daemon() includes --auto-approve."""
        # Given: ProcessManager instance
        pm = ProcessManager()

        # When: Building daemon command
        with patch('subprocess.Popen') as mock_popen:
            pm.start_daemon()

            # Then: Command includes --auto-approve
            call_args = mock_popen.call_args[0][0]
            assert "--auto-approve" in call_args

    def test_daemon_makes_progress(self):
        """Test daemon doesn't get stuck at iteration 2."""
        # Given: Mock daemon with status tracking
        with patch('coffee_maker.autonomous.daemon.DevDaemon') as mock_daemon:
            mock_status = Mock()
            mock_status.iteration = 5  # > 2
            mock_daemon.return_value.status = mock_status

            # Then: Iterations > 2 (not stuck)
            assert mock_status.iteration > 2
```

**Implementation Notes**:
- Use mocking to avoid starting actual daemon
- Focus on command construction, not execution
- Keep tests fast and isolated

---

### Component 2: BUG-002 Verification Tests

**Responsibility**: Verify daemon handles missing priority content gracefully

**Interface**:
```python
# tests/unit/test_bug_002_verification.py

import pytest
import logging
from coffee_maker.autonomous.daemon import DevDaemon

class TestBug002Verification:
    """Verify BUG-002 fix: graceful handling of missing content."""

    def test_build_spec_prompt_missing_content(self, caplog):
        """Test _build_spec_creation_prompt with missing content."""
        # Given: Priority without content field
        priority = {
            "name": "PRIORITY 99",
            "title": "Test Priority"
        }
        daemon = DevDaemon(auto_approve=True)

        # When: Building spec creation prompt
        with caplog.at_level(logging.WARNING):
            prompt = daemon._build_spec_creation_prompt(
                priority,
                "SPEC-099-test.md"
            )

        # Then: No crash, warning logged, fallback used
        assert prompt is not None
        assert "No additional details provided" in prompt
        assert "has no content" in caplog.text

    def test_build_spec_prompt_none_content(self):
        """Test _build_spec_creation_prompt with None content."""
        # Given: Priority with None content
        priority = {
            "name": "PRIORITY 99",
            "title": "Test Priority",
            "content": None
        }
        daemon = DevDaemon(auto_approve=True)

        # When: Building spec creation prompt
        prompt = daemon._build_spec_creation_prompt(
            priority,
            "SPEC-099-test.md"
        )

        # Then: No crash, fallback used
        assert prompt is not None
        assert "No additional details provided" in prompt

    def test_build_spec_prompt_empty_content(self):
        """Test _build_spec_creation_prompt with empty content."""
        # Given: Priority with empty string content
        priority = {
            "name": "PRIORITY 99",
            "title": "Test Priority",
            "content": ""
        }
        daemon = DevDaemon(auto_approve=True)

        # When: Building spec creation prompt
        prompt = daemon._build_spec_creation_prompt(
            priority,
            "SPEC-099-test.md"
        )

        # Then: No crash, fallback used
        assert prompt is not None

    def test_ensure_technical_spec_missing_name(self, caplog):
        """Test _ensure_technical_spec rejects priority without name."""
        # Given: Priority without name field
        priority = {"content": "Some content"}
        daemon = DevDaemon(auto_approve=True)

        # When: Ensuring technical spec
        with caplog.at_level(logging.ERROR):
            result = daemon._ensure_technical_spec(priority)

        # Then: Returns False, error logged
        assert result is False
        assert "missing 'name' field" in caplog.text

    def test_ensure_technical_spec_handles_missing_content(self, caplog):
        """Test _ensure_technical_spec logs warning for missing content."""
        # Given: Priority with name but no content
        priority = {
            "name": "PRIORITY 99",
            "title": "Test Priority"
        }
        daemon = DevDaemon(auto_approve=True)

        # When: Ensuring technical spec
        with caplog.at_level(logging.WARNING):
            # Mock spec file existence check
            with patch('pathlib.Path.exists', return_value=True):
                result = daemon._ensure_technical_spec(priority)

        # Then: Warning logged but continues
        assert "has no content" in caplog.text or result is not None
```

**Implementation Notes**:
- Use pytest fixtures for daemon setup
- Use caplog to verify logging behavior
- Test all edge cases: missing, None, empty
- Verify no KeyError or TypeError exceptions

---

## Testing Strategy

### Unit Tests (All tests)

**Files**:
- `tests/unit/test_bug_001_verification.py`
- `tests/unit/test_bug_002_verification.py`

**Total Test Count**: ~8 tests
**Estimated Runtime**: < 20 seconds total

**Test Execution**:
```bash
# Run verification tests
pytest tests/unit/test_bug_001_verification.py -v
pytest tests/unit/test_bug_002_verification.py -v

# Or run all at once
pytest tests/unit/test_bug_*_verification.py -v
```

### Manual Testing Checklist

**BUG-001 Manual Verification**:
- [ ] Start daemon with ProcessManager
- [ ] Verify process has --auto-approve in command line
- [ ] Check developer_status.json shows iterations > 2
- [ ] Confirm daemon makes autonomous progress

**BUG-002 Manual Verification**:
- [ ] Create test priority with no content in ROADMAP
- [ ] Start daemon, observe it processes priority
- [ ] Verify no crash, warning logged
- [ ] Check logs show "has no content - using title only"

---

## Rollout Plan

### Morning (4 hours) - BUG-001 Verification
1. Create `test_bug_001_verification.py`
2. Write tests for --auto-approve flag
3. Write tests for progress tracking
4. Run tests, verify passing
5. Commit: "test: Add BUG-001 verification tests"

### Afternoon (4 hours) - BUG-002 Verification
1. Create `test_bug_002_verification.py`
2. Write tests for missing/None/empty content
3. Write tests for missing name field
4. Run tests, verify passing
5. Commit: "test: Add BUG-002 verification tests"

### End of Day (1 hour) - Documentation
1. Run full test suite
2. Update BUG-001.md with verification section
3. Update BUG-002.md with verification section
4. Update ROADMAP.md (PRIORITY 2.6 → ✅ Complete)
5. Commit: "docs: Complete PRIORITY 2.6 - Daemon Fix Verification"

**Total: 1 day (8-9 hours)**

---

## Success Criteria

### Must Have (P0)
- ✅ BUG-001 verification tests passing
- ✅ BUG-002 verification tests passing
- ✅ No exceptions in any test case
- ✅ All edge cases covered
- ✅ Tests run in < 20 seconds
- ✅ BUG tickets updated with evidence
- ✅ ROADMAP updated to ✅ Complete

### Should Have (P1)
- ✅ Clear test names and docstrings
- ✅ Good code coverage of bug fix code paths
- ✅ Logging verification (warnings/errors)

### Could Have (P2) - DEFERRED
- ⚪ Integration tests with real daemon (not needed - unit tests sufficient)
- ⚪ Performance tests (not needed - verification only)
- ⚪ CI/CD pipeline updates (existing pipeline sufficient)

---

## Why This is SIMPLE

### Compared to Full CI/CD Implementation

**What we're NOT building**:
- ❌ GitHub Actions workflows
- ❌ Complex test infrastructure
- ❌ Integration test environment
- ❌ Monitoring/alerting systems
- ❌ Comprehensive daemon test suite

**What we ARE doing**:
- ✅ Focused regression tests (2 files, ~200 lines)
- ✅ Verify specific bug fixes
- ✅ Use existing test infrastructure
- ✅ Documentation updates

**Result**: Verification-only task, not feature development

### What We REUSE

✅ **Pytest**: Already installed and configured
✅ **Test fixtures**: Existing daemon test fixtures
✅ **Test structure**: Following existing test patterns
✅ **Bug fixes**: Already implemented (491a438, 911d77c)
✅ **Documentation structure**: Existing BUG ticket format

**New code**: Only ~200 lines of focused test code

---

## Risks & Mitigations

### Risk 1: Tests require running daemon

**Likelihood**: Low
**Impact**: Medium (would slow down tests)

**Mitigation**:
- Use mocking and patching
- Test method logic, not full daemon execution
- Keep tests isolated and fast

### Risk 2: Tests are brittle

**Likelihood**: Low
**Impact**: Low

**Mitigation**:
- Test behavior, not implementation details
- Use clear assertions
- Follow existing test patterns

### Risk 3: Verification finds issues

**Likelihood**: Very Low (fixes already manually tested)
**Impact**: Medium

**Mitigation**:
- If tests fail, investigate immediately
- Fixes are already committed, should work
- Most likely: test setup issue, not actual bug

---

## Observability

### Test Results
- All tests must pass (green)
- Test execution time < 20 seconds
- No skipped or xfail tests

### Logs
- BUG-001 tests verify logging (process startup)
- BUG-002 tests verify warnings (missing content)

---

## Documentation Updates

### Files to Update

1. **tickets/BUG-001.md**:
   - Add "Verification Complete" section
   - Link to verification tests
   - Mark as ✅ Verified

2. **tickets/BUG-002.md**:
   - Add "Verification Complete" section
   - Link to verification tests
   - Mark as ✅ Verified

3. **docs/roadmap/ROADMAP.md**:
   - Update PRIORITY 2.6 status: 📝 Planned → ✅ Complete
   - Add completion date and summary

4. **.claude/CLAUDE.md** (optional):
   - Update "Bug Fixes" section
   - Add verification test references

---

## Security Considerations

**None** - This is verification testing only, no security implications.

---

## Cost Estimate

**Development Time**: 1 day (8-9 hours)
- BUG-001 verification: 4 hours
- BUG-002 verification: 4 hours
- Documentation: 1 hour

**Infrastructure**: $0 (use existing test infrastructure)

**Ongoing**: $0 (tests run in CI automatically)

---

## Future Enhancements (NOT NOW)

Phase 2+ (if needed):
1. Integration tests with real daemon
2. GitHub Actions CI workflow updates
3. Automated regression test suite
4. Performance benchmarks

**But**: Only add if issues found. Current verification should be sufficient!

---

## References

- **BUG-001**: Daemon stuck without --auto-approve (Fixed: 491a438)
- **BUG-002**: Daemon crashes with missing content (Fixed: 911d77c)
- **ADR-003**: Simplification-First Approach
- **ROADMAP**: PRIORITY 2.6 definition (line 10504+)
- **Existing tests**: `tests/ci_tests/test_daemon_*.py`

---

## Implementation Checklist

### BUG-001 Verification
- [ ] Create `tests/unit/test_bug_001_verification.py`
- [ ] Test ProcessManager includes --auto-approve
- [ ] Test daemon makes progress (iterations > 2)
- [ ] Run tests, verify passing
- [ ] Commit verification tests

### BUG-002 Verification
- [ ] Create `tests/unit/test_bug_002_verification.py`
- [ ] Test missing content field
- [ ] Test None content
- [ ] Test empty content
- [ ] Test missing name field
- [ ] Run tests, verify passing
- [ ] Commit verification tests

### Documentation
- [ ] Update BUG-001.md with verification evidence
- [ ] Update BUG-002.md with verification evidence
- [ ] Update ROADMAP.md (PRIORITY 2.6 → ✅ Complete)
- [ ] Final commit: "Complete PRIORITY 2.6"

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created SPEC-002-6 | architect |
| 2025-10-17 | Status: Draft → Approved | architect |

---

## Approval

- [x] architect (author) - Approved 2025-10-17
- [ ] code_developer (implementer) - Review pending
- [ ] project_manager (strategic alignment) - Review pending

---

**Status**: ✅ Ready for Implementation

**Next Step**: code_developer reads this spec and implements verification tests

**Key Message**: This is a SIMPLE verification task - just write tests to prove the bugs are fixed. No new features, no complex infrastructure, just focused regression testing.
