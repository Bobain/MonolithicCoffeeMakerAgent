# code_developer Refactoring Workflow

**Owner**: code_developer agent

**Purpose**: This document describes how code_developer executes refactoring tasks created by architect, ensuring quality and maintaining all functionality.

**Related**: US-044, ARCHITECT_WORKFLOW.md

---

## Table of Contents

1. [Overview](#overview)
2. [Finding Refactoring Tasks](#finding-refactoring-tasks)
3. [Executing Refactoring](#executing-refactoring)
4. [Testing Strategy](#testing-strategy)
5. [Progress Reporting](#progress-reporting)
6. [Complete Example](#complete-example)

---

## Overview

### code_developer's Role

code_developer executes refactoring plans created by architect:

- **Follow**: Execute tasks exactly as specified in refactoring plan
- **Implement**: Make code changes incrementally and safely
- **Test**: Verify no functionality broken at each step
- **Report**: Update task status and communicate blockers
- **Verify**: Run all verification commands before completion

### Key Principles

1. **Safety first**: Never break existing functionality
2. **Incremental**: Make small, testable changes
3. **Test continuously**: Run tests after each major change
4. **Communicate**: Report blockers immediately
5. **Verify**: Always run verification commands from plan

---

## Finding Refactoring Tasks

### Location

Refactoring plans are in: `docs/architecture/refactoring/active/`

```bash
# List active refactoring plans
ls -la docs/architecture/refactoring/active/

# Example output:
# REFACTOR_2025_10_16_daemon_simplification.md
# REFACTOR_2025_10_18_api_client_cleanup.md
```

### ROADMAP Integration

Refactoring tasks also appear in ROADMAP:

```bash
# Check ROADMAP for refactoring priorities
poetry run project-manager /roadmap | grep REFACTOR
```

Example ROADMAP entry:

```markdown
### REFACTOR-001: Simplify DevDaemon Class

**Status**: 📝 PLANNED
**Priority**: HIGH
**Estimated**: 2 days
**See**: docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md
```

### Reading a Refactoring Plan

Each plan has:

1. **Why Refactor?** - Understanding the problem
2. **Current State** - Code before refactoring
3. **Target State** - Goal after refactoring
4. **Tasks for code_developer** - Specific tasks to execute
5. **Acceptance Criteria** - Success metrics
6. **Verification** - Commands to run

**Always read the entire plan before starting!**

---

## Executing Refactoring

### Step 1: Understand the Goal

Read the refactoring plan carefully:

```bash
# Open the refactoring plan
cat docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md
```

Understand:
- **Why** this refactoring is needed
- **What** the target state looks like
- **How** each task contributes to the goal

### Step 2: Set Up Development Environment

```bash
# Ensure on roadmap branch
git checkout roadmap

# Pull latest changes
git pull origin roadmap

# Verify tests pass before starting
pytest

# Create baseline metrics
./scripts/check_complexity.sh > /tmp/before_refactoring.txt
```

### Step 3: Execute Tasks Incrementally

**IMPORTANT**: Execute one task at a time, test after each task.

#### Example Task from Plan:

```markdown
### Task 1: Extract SpecManagerMixin to separate module (4 hours)

**What**: Move spec management logic from DevDaemon to dedicated module

**How**:
1. Create `coffee_maker/autonomous/mixins/spec_manager.py`
2. Move these methods from DevDaemon:
   - `_create_spec_if_needed()`
   - `_validate_spec_exists()`
   - `_get_spec_path()`
3. Create SpecManagerMixin class with these methods
4. Update DevDaemon to inherit from SpecManagerMixin
5. Update imports in DevDaemon

**Files to modify**:
- `coffee_maker/autonomous/daemon.py`
- `coffee_maker/autonomous/mixins/spec_manager.py` (NEW)
- `coffee_maker/autonomous/mixins/__init__.py`

**Tests**:
- Add `tests/unit/mixins/test_spec_manager.py`
- Update `tests/unit/test_daemon.py`
- Run integration tests
```

#### Execution Steps:

**Step 3.1: Create new file structure**

```bash
# Create new mixin file
touch coffee_maker/autonomous/mixins/spec_manager.py
```

**Step 3.2: Implement the mixin**

```python
# coffee_maker/autonomous/mixins/spec_manager.py
"""Spec management mixin for DevDaemon."""

from pathlib import Path
from typing import Optional


class SpecManagerMixin:
    """Handles spec creation and validation for priorities."""

    def _create_spec_if_needed(self, priority_id: str) -> Path:
        """Create spec for priority if it doesn't exist.

        Args:
            priority_id: Priority identifier (e.g., "US-044")

        Returns:
            Path to spec file
        """
        # Implementation moved from DevDaemon
        pass

    def _validate_spec_exists(self, spec_path: Path) -> bool:
        """Validate that spec file exists and is valid.

        Args:
            spec_path: Path to spec file

        Returns:
            True if spec exists and is valid
        """
        # Implementation moved from DevDaemon
        pass

    def _get_spec_path(self, priority_id: str) -> Path:
        """Get path to spec file for priority.

        Args:
            priority_id: Priority identifier

        Returns:
            Path to spec file
        """
        # Implementation moved from DevDaemon
        pass
```

**Step 3.3: Update imports**

```python
# coffee_maker/autonomous/mixins/__init__.py
"""Mixins for DevDaemon."""

from .spec_manager import SpecManagerMixin

__all__ = ["SpecManagerMixin"]
```

**Step 3.4: Update DevDaemon**

```python
# coffee_maker/autonomous/daemon.py
from coffee_maker.autonomous.mixins import SpecManagerMixin


class DevDaemon(SpecManagerMixin):
    """Autonomous development daemon."""

    # Remove the three methods that are now in SpecManagerMixin
    # They're inherited automatically
```

**Step 3.5: Run tests**

```bash
# Run unit tests for the mixin
pytest tests/unit/mixins/test_spec_manager.py -v

# Run daemon tests
pytest tests/unit/test_daemon.py -v

# Run integration tests
pytest tests/integration/ -v

# If all pass, commit this task
git add .
git commit -m "refactor: Extract SpecManagerMixin from DevDaemon

- Created coffee_maker/autonomous/mixins/spec_manager.py
- Moved _create_spec_if_needed, _validate_spec_exists, _get_spec_path
- DevDaemon now inherits from SpecManagerMixin
- All tests passing

Part of REFACTOR-001 (Task 1/6)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Step 3.6: Move to next task**

Repeat steps 3.1-3.5 for each remaining task.

### Step 4: Handle Blockers

If you encounter issues:

#### Blocker Types

**1. Technical Blocker** (can't complete task as written)

Example: Task says to extract method, but method is tightly coupled.

**Action:**
```markdown
## Task 2 Blocker Report

**Task**: Extract ImplementationMixin
**Issue**: _run_implementation() method tightly coupled to 4 other methods
**Impact**: Cannot extract cleanly without breaking functionality

**Options**:
1. Extract all 5 methods together (more work, 8h instead of 4h)
2. Refactor coupling first, then extract (safer, 6h total)
3. Skip this extraction, document coupling as tech debt

**Recommendation**: Option 2 - refactor coupling first

**Request**: architect guidance on approach
```

**2. Test Failure** (existing tests break)

**Action:**
```bash
# Document the failure
pytest tests/unit/test_daemon.py::test_implementation_flow -v > /tmp/test_failure.txt

# Analyze the root cause
# Fix the test or the code
# Re-run tests

# If can't fix: report to architect
```

**3. Unclear Requirement** (task not specific enough)

**Action:**
Ask architect for clarification:
```markdown
## Task 3 Clarification Needed

**Task**: "Simplify main run() loop"
**Question**: Should I extract just the iteration logic, or also the error handling?
**Context**: Error handling is 15 lines and has 2 nested try/except blocks

**Request**: Please clarify scope of simplification
```

### Step 5: Run Verification Commands

After completing ALL tasks, run verification commands from plan:

```bash
# Example verification commands from plan:

# Check complexity improved
radon cc coffee_maker/autonomous/daemon.py -a
# Expected output: Complexity <20, Grade A or B

# Check line count reduced
wc -l coffee_maker/autonomous/daemon.py
# Expected output: <500 lines

# Run unit tests
pytest tests/unit/test_daemon.py -v
# Expected output: All passing

# Run integration tests
pytest tests/integration/test_daemon_workflow.py -v
# Expected output: All passing

# Check coverage maintained
pytest --cov=coffee_maker/autonomous/daemon.py --cov-report=term
# Expected output: >90%

# Full test suite
pytest
# Expected output: All passing, no regressions
```

**Document results:**

```markdown
## Verification Results (2025-10-21)

### Complexity Check
```
$ radon cc coffee_maker/autonomous/daemon.py -a
coffee_maker/autonomous/daemon.py
    M 156:4 DevDaemon.run - B (18)
Average complexity: B (8.2)
```
✅ Target achieved: <20

### Line Count
```
$ wc -l coffee_maker/autonomous/daemon.py
487 coffee_maker/autonomous/daemon.py
```
✅ Target achieved: <500

### Tests
```
$ pytest tests/unit/test_daemon.py -v
===== 47 passed in 3.21s =====
```
✅ All unit tests passing

[... etc for all verification commands]
```

---

## Testing Strategy

### Test Continuously

**After each task:**
```bash
# Quick smoke test
pytest tests/unit/test_daemon.py -v

# If that passes, run related tests
pytest tests/unit/mixins/ -v
pytest tests/integration/ -v
```

### Test Coverage

**Maintain or improve coverage:**

```bash
# Check coverage before refactoring
pytest --cov=coffee_maker/autonomous/daemon.py --cov-report=term > /tmp/coverage_before.txt

# Check coverage after refactoring
pytest --cov=coffee_maker/autonomous/daemon.py --cov-report=term > /tmp/coverage_after.txt

# Compare
diff /tmp/coverage_before.txt /tmp/coverage_after.txt
```

**Coverage should not decrease!**

### Add Tests for Extracted Code

When extracting methods to new modules:

```bash
# Create test file for new mixin
touch tests/unit/mixins/test_spec_manager.py
```

```python
# tests/unit/mixins/test_spec_manager.py
"""Tests for SpecManagerMixin."""

import pytest
from pathlib import Path
from coffee_maker.autonomous.mixins import SpecManagerMixin


class TestSpecManagerMixin:
    """Test SpecManagerMixin functionality."""

    def test_create_spec_if_needed(self):
        """Test spec creation when spec doesn't exist."""
        # Implementation
        pass

    def test_validate_spec_exists(self):
        """Test spec validation."""
        # Implementation
        pass

    def test_get_spec_path(self):
        """Test spec path retrieval."""
        # Implementation
        pass
```

### Integration Testing

**Critical**: Verify entire workflow still works:

```bash
# Run the daemon for 1 iteration in test mode
poetry run code-developer --auto-approve --max-iterations 1

# Verify it completes successfully
# Verify it produces expected output
# Verify no errors in logs
```

---

## Progress Reporting

### Update Task Status in Plan

As you complete tasks, update the refactoring plan:

```markdown
## Tasks Progress

- [x] Task 1: Extract SpecManagerMixin (4h) - COMPLETE 2025-10-21
- [x] Task 2: Extract ImplementationMixin (4h) - COMPLETE 2025-10-21
- [ ] Task 3: Simplify main run() loop (3h) - IN PROGRESS
- [ ] Task 4: Update tests (5h) - PENDING
- [ ] Task 5: Update documentation (2h) - PENDING
```

### Commit Frequency

**Commit after each task:**

```bash
# Good commit message format
git commit -m "refactor: [Brief description]

[Detailed explanation of what changed]

Part of REFACTOR-001 (Task 2/6)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Time Tracking

**Report actual vs estimated time:**

```markdown
## Time Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| Task 1 | 4h | 3.5h | Smoother than expected |
| Task 2 | 4h | 6h | Found coupling issue, needed extra work |
| Task 3 | 3h | 2h | Straightforward extraction |
| Task 4 | 5h | ... | In progress |
```

This helps architect improve future estimates.

---

## Complete Example

### Scenario: Execute REFACTOR-001 (DevDaemon Simplification)

**Morning: Preparation**

```bash
# Step 1: Find the task
ls docs/architecture/refactoring/active/
# See: REFACTOR_2025_10_16_daemon_simplification.md

# Step 2: Read the plan
cat docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md
# Understand: 6 tasks, ~16 hours total

# Step 3: Setup
git checkout roadmap
git pull origin roadmap

# Step 4: Baseline
pytest  # Ensure all tests pass
./scripts/check_complexity.sh > /tmp/baseline_metrics.txt

# Ready to start!
```

---

**Task 1: Extract SpecManagerMixin (4 hours)**

```bash
# Create new file
touch coffee_maker/autonomous/mixins/spec_manager.py

# Implement mixin (copy methods from DevDaemon)
# Update DevDaemon to inherit from mixin
# Update imports

# Test
pytest tests/unit/mixins/test_spec_manager.py -v
pytest tests/unit/test_daemon.py -v

# Commit
git add .
git commit -m "refactor: Extract SpecManagerMixin from DevDaemon

- Created coffee_maker/autonomous/mixins/spec_manager.py
- Moved spec management methods
- DevDaemon inherits from SpecManagerMixin
- Added comprehensive unit tests

Part of REFACTOR-001 (Task 1/6)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Update plan progress
# Task 1: ✅ COMPLETE
```

---

**Task 2: Extract ImplementationMixin (4 hours)**

```bash
# Create file
touch coffee_maker/autonomous/mixins/implementation_manager.py

# Implement mixin
# Update DevDaemon
# Update imports

# Test
pytest tests/unit/mixins/test_implementation_manager.py -v
pytest tests/unit/test_daemon.py -v

# Commit
git add .
git commit -m "refactor: Extract ImplementationMixin from DevDaemon

- Created coffee_maker/autonomous/mixins/implementation_manager.py
- Moved implementation methods
- DevDaemon inherits from ImplementationMixin
- Added unit tests

Part of REFACTOR-001 (Task 2/6)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Update plan progress
# Task 2: ✅ COMPLETE
```

---

**Task 3: Simplify main run() loop (3 hours)**

```bash
# Extract helper methods
# Reduce nesting
# Add inline documentation

# Test
pytest tests/unit/test_daemon.py::test_run -v
pytest tests/integration/ -v

# Commit
git add .
git commit -m "refactor: Simplify DevDaemon.run() main loop

- Extracted _run_iteration() helper method
- Reduced nesting from 4 to 2 levels
- Added inline documentation
- Complexity reduced from 47 to 18

Part of REFACTOR-001 (Task 3/6)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Update plan progress
# Task 3: ✅ COMPLETE
```

---

**Task 4-6: Continue same pattern**

Execute remaining tasks following same approach:
1. Implement change
2. Test thoroughly
3. Commit with descriptive message
4. Update plan progress

---

**Final: Verification**

```bash
# Run ALL verification commands from plan

# 1. Complexity check
radon cc coffee_maker/autonomous/daemon.py -a
# Result: Complexity 18, Grade B ✅

# 2. Line count
wc -l coffee_maker/autonomous/daemon.py
# Result: 487 lines ✅

# 3. Unit tests
pytest tests/unit/test_daemon.py -v
# Result: 47 passed ✅

# 4. Integration tests
pytest tests/integration/test_daemon_workflow.py -v
# Result: 12 passed ✅

# 5. Coverage
pytest --cov=coffee_maker/autonomous/daemon.py --cov-report=term
# Result: 93.2% coverage ✅

# 6. Full test suite
pytest
# Result: 261 passed ✅

# All verification passed! Ready for architect review.
```

---

**Update Refactoring Plan**

Add completion section to plan:

```markdown
## code_developer Execution Report

**Completed**: 2025-10-21
**Time spent**: 14 hours (estimated 16 hours)
**Commits**: 6 (one per task)

### Tasks Completed

- [x] Task 1: Extract SpecManagerMixin (3.5h)
- [x] Task 2: Extract ImplementationMixin (4h)
- [x] Task 3: Simplify main run() loop (2h)
- [x] Task 4: Extract error handling (1.5h)
- [x] Task 5: Update tests (2h)
- [x] Task 6: Update documentation (1h)

### Verification Results

All acceptance criteria met:
✅ DevDaemon.py: 487 lines (target <500)
✅ Complexity: 18 (target <20)
✅ All 261 tests passing
✅ Coverage: 93.2% (target >90%)
✅ Pylint: 8.4 (target >8.0)

### Blockers Encountered

None - all tasks completed as planned

**Status**: ✅ READY FOR ARCHITECT REVIEW
```

---

## Quick Reference

### code_developer Checklist

**Before starting:**
- [ ] Read entire refactoring plan
- [ ] Understand goal and target state
- [ ] Ensure on `roadmap` branch
- [ ] Baseline: all tests passing
- [ ] Save baseline metrics

**For each task:**
- [ ] Implement change incrementally
- [ ] Add/update tests
- [ ] Run tests (unit + integration)
- [ ] Check coverage maintained
- [ ] Commit with descriptive message
- [ ] Update plan progress

**After all tasks:**
- [ ] Run ALL verification commands
- [ ] Document results in plan
- [ ] Update time tracking
- [ ] Mark ready for review
- [ ] Notify architect

### Key Commands

```bash
# Find refactoring tasks
ls docs/architecture/refactoring/active/

# Read refactoring plan
cat docs/architecture/refactoring/active/REFACTOR_*.md

# Run tests after each change
pytest tests/unit/test_daemon.py -v

# Check coverage
pytest --cov=coffee_maker --cov-report=term

# Check complexity
radon cc coffee_maker/autonomous/daemon.py -a

# Full verification
pytest && radon cc coffee_maker/ -a && pylint coffee_maker/ --score=y
```

### Commit Message Template

```
refactor: [Brief description in imperative mood]

[Detailed explanation]
- Bullet point 1
- Bullet point 2

Part of REFACTOR-XXX (Task Y/Z)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Related Documents

- [ARCHITECT_WORKFLOW.md](./ARCHITECT_WORKFLOW.md) - How architect creates refactoring plans
- [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) - Understanding metrics
- [templates/REFACTOR_TEMPLATE.md](./templates/REFACTOR_TEMPLATE.md) - Plan template
- [US-044](../../roadmap/ROADMAP.md#us-044) - User story

---

**Last Updated**: 2025-10-21
**Version**: 1.0
**Status**: Production ✅
