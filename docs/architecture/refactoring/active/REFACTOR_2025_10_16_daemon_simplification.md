# Refactoring Plan: Simplify DevDaemon Main Loop

**Created By**: architect
**Date**: 2025-10-16
**Priority**: MEDIUM
**Estimated Effort**: 4-6 hours
**Status**: PLANNED

## Why Refactor?

The `DevDaemon.run()` method has become complex with nested conditionals and multiple responsibilities.

**Current Metrics**:
- Complexity: 15 (should be <10)
- Lines in run(): 87
- Nested depth: 4 levels
- Responsibilities: 6 different concerns

## Current State

```python
def run(self):
    while True:
        try:
            # Priority fetching (10 lines)
            # Spec checking (15 lines)
            # Implementation (20 lines)
            # Error handling (15 lines)
            # Status updates (12 lines)
            # Sleep logic (15 lines)
        except Exception as e:
            # Error handling (10 lines)
```

**Issues**:
- Too many responsibilities in one method
- Hard to test individual concerns
- Difficult to understand flow
- Nested error handling

## Target State

```python
def run(self):
    while True:
        try:
            self._run_iteration()
        except Exception as e:
            self._handle_error(e)

def _run_iteration(self):
    priority = self._fetch_next_priority()
    spec = self._ensure_spec(priority)
    result = self._implement_priority(priority, spec)
    self._update_status(result)
    self._sleep_between_iterations()
```

**Improvements**:
- Single Responsibility Principle
- Easier to test each method independently
- Clearer flow
- Reduced nesting

## Tasks for code_developer

### Task 1: Extract Priority Fetching (1 hour)

**What**: Move priority fetching logic to separate method

**How**:
1. Create `_fetch_next_priority()` method
2. Move priority fetching code
3. Return priority or None
4. Update run() to call new method

**Files to modify**:
- `coffee_maker/autonomous/daemon.py`

**Tests**:
- Add `test_fetch_next_priority()` unit test

### Task 2: Extract Spec Handling (1 hour)

**What**: Move spec checking/creation to separate method

**How**:
1. Create `_ensure_spec(priority)` method
2. Move spec checking logic
3. Return spec path
4. Update run() to call new method

**Files to modify**:
- `coffee_maker/autonomous/daemon.py`

**Tests**:
- Add `test_ensure_spec()` unit test

### Task 3: Extract Implementation Logic (1.5 hours)

**What**: Move implementation execution to separate method

**How**:
1. Create `_implement_priority(priority, spec)` method
2. Move implementation logic
3. Return result
4. Update run() to call new method

**Files to modify**:
- `coffee_maker/autonomous/daemon.py`

**Tests**:
- Add `test_implement_priority()` unit test

### Task 4: Extract Status Updates (30 min)

**What**: Move status update logic to separate method

**How**:
1. Create `_update_status(result)` method
2. Move status update code
3. Update run() to call new method

**Files to modify**:
- `coffee_maker/autonomous/daemon.py`

**Tests**:
- Add `test_update_status()` unit test

### Task 5: Simplify Error Handling (1 hour)

**What**: Create dedicated error handling method

**How**:
1. Create `_handle_error(exception)` method
2. Consolidate error handling logic
3. Update run() to call new method

**Files to modify**:
- `coffee_maker/autonomous/daemon.py`

**Tests**:
- Add `test_handle_error()` unit test

### Task 6: Update Integration Tests (1 hour)

**What**: Ensure integration tests still pass

**How**:
1. Run full test suite
2. Fix any broken tests
3. Verify no regressions

## Acceptance Criteria

- [ ] DevDaemon.run() method <30 lines
- [ ] Complexity score <10
- [ ] All tests passing (existing + new)
- [ ] No functionality broken
- [ ] Code coverage maintained (>90%)
- [ ] Each extracted method has unit test

## Verification

```bash
# Run tests
pytest tests/unit/test_daemon.py -v

# Check complexity
radon cc coffee_maker/autonomous/daemon.py -a

# Full test suite
pytest
```

## Rollback Plan

If refactoring causes issues:
1. Revert commit: `git revert <commit-hash>`
2. Run tests to verify: `pytest`
3. Report issue to architect

## Notes

This is a low-risk refactoring that improves maintainability without changing functionality. All behavior should remain identical.
