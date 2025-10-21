# Architect Refactoring Workflow

**Owner**: architect agent

**Purpose**: This document describes the complete workflow for architect to monitor code quality, identify technical debt, create refactoring plans, and oversee refactoring execution.

**Related**: US-044, CFR-005 (Ownership Includes Maintenance Responsibility), CFR-011 (Code Quality Integration)

---

## Table of Contents

1. [Overview](#overview)
2. [Weekly Monitoring Schedule](#weekly-monitoring-schedule)
3. [Code Quality Metrics](#code-quality-metrics)
4. [Identifying Refactoring Opportunities](#identifying-refactoring-opportunities)
5. [Creating Refactoring Plans](#creating-refactoring-plans)
6. [ROADMAP Integration](#roadmap-integration)
7. [Review Process](#review-process)
8. [Complete Example](#complete-example)

---

## Overview

### architect's Role

architect is responsible for **proactive code quality management**:

- **Monitor**: Weekly review of code complexity and quality metrics
- **Decide**: When refactoring is needed based on clear criteria
- **Plan**: Create detailed refactoring plans for code_developer
- **Review**: Verify refactoring quality after code_developer completes work
- **Track**: Document improvements and lessons learned

### Key Principles

1. **Proactive, not reactive**: Don't wait for things to break
2. **Regular cadence**: Weekly monitoring ensures early detection
3. **Clear criteria**: Objective thresholds for refactoring decisions
4. **Detailed plans**: code_developer needs specific, actionable tasks
5. **Verify success**: Always check metrics improved after refactoring

---

## Weekly Monitoring Schedule

### Monday 9am: Run Code Quality Analysis

```bash
# Navigate to project root
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt044

# Run comprehensive complexity check
./scripts/check_complexity.sh > docs/architecture/refactoring/weekly_$(date +%Y_%m_%d).txt

# Review the output
cat docs/architecture/refactoring/weekly_$(date +%Y_%m_%d).txt
```

### What to Look For

**🔴 Critical Issues** (Fix immediately):
- Cyclomatic complexity >20
- Files >2000 lines
- Pylint score <5.0
- Architecture violations

**🟡 Medium Issues** (Plan for this week):
- Complexity >15
- Files >1500 lines
- Pylint score <7.0
- Code duplication (>3 instances)

**🟢 Minor Issues** (Track for next month):
- Complexity >10
- Files >1000 lines
- Pylint score <8.0
- Test coverage <90%

---

## Code Quality Metrics

### Tools Available

#### 1. Radon - Complexity Analysis

```bash
# Cyclomatic complexity (per function)
radon cc coffee_maker/ -a -s

# Maintainability index (per file)
radon mi coffee_maker/ -s

# Halstead metrics (optional, for deep analysis)
radon hal coffee_maker/
```

**Interpreting Radon Output:**

```
coffee_maker/autonomous/daemon.py
    M 156:4 DevDaemon.run - E (47)
```

- `M` = Method
- `156:4` = Line 156, indent level 4
- `E` = Complexity grade (A-F scale)
- `47` = Cyclomatic complexity score

**Complexity Grades:**
- A (1-5): Simple
- B (6-10): Acceptable
- C (11-20): Complex - monitor
- D (21-30): Very complex - refactor soon
- E (31-40): Extremely complex - refactor now
- F (>40): Critical - refactor immediately

#### 2. Pylint - Code Quality

```bash
# Full report with score
pylint coffee_maker/ --score=y

# Focus on specific categories
pylint coffee_maker/ --disable=C,R --score=y  # Only errors and warnings

# Check specific file
pylint coffee_maker/autonomous/daemon.py
```

**Key Pylint Checks:**
- Import errors
- Undefined variables
- Unused imports
- Convention violations
- Refactoring suggestions

#### 3. Test Coverage

```bash
# Run tests with coverage
pytest --cov=coffee_maker --cov-report=term-missing

# Generate HTML report for detailed analysis
pytest --cov=coffee_maker --cov-report=html
open htmlcov/index.html
```

**Coverage Targets:**
- Critical paths: 100%
- Business logic: >95%
- Overall: >90%
- UI/CLI: >80%

#### 4. Code Duplication

```bash
# Find duplicate code blocks
# Note: Install with `pip install pylint`
pylint --disable=all --enable=duplicate-code coffee_maker/
```

### Automated Check Script

The project includes `/scripts/check_complexity.sh`:

```bash
#!/bin/bash
# Check code complexity metrics

echo "=== Code Complexity Report ==="
echo ""

echo "Cyclomatic Complexity (should be <10 per function):"
radon cc coffee_maker/ -a -s

echo ""
echo "Maintainability Index (should be >20):"
radon mi coffee_maker/ -s

echo ""
echo "Pylint Score (should be >8.0):"
pylint coffee_maker/ --score=y || true
```

---

## Identifying Refactoring Opportunities

### Decision Criteria

Use these objective thresholds to identify refactoring needs:

| Metric | Threshold | Action |
|--------|-----------|--------|
| File size | >2000 lines | Split into modules |
| Function complexity | >20 | Extract methods, simplify logic |
| Duplication | >3 instances | Extract common code |
| Test coverage | <80% | Add tests |
| Pylint score | <7.0 | Fix quality issues |
| Architecture violation | Any | Fix immediately |
| Nested depth | >4 levels | Flatten control flow |

### Common Refactoring Patterns

#### 1. Large Class/File

**Detection:**
```bash
# Find files >1000 lines
find coffee_maker -name "*.py" -exec wc -l {} + | sort -rn | head -10
```

**Refactoring approach:**
- Extract mixins for separate concerns
- Split into module with multiple files
- Extract utility functions to separate module

**Example:** `DevDaemon` (1592 lines) → Split into daemon.py + mixins

#### 2. Complex Function

**Detection:**
```bash
# Find functions with complexity >15
radon cc coffee_maker/ -a -s | grep -E " [D-F] \("
```

**Refactoring approach:**
- Extract helper methods
- Reduce nesting with early returns
- Split into multiple smaller functions
- Use strategy pattern for complex conditionals

**Example:** `DevDaemon.run()` (complexity 47) → Extract iteration logic

#### 3. Code Duplication

**Detection:**
```bash
# Find duplicate code
pylint --disable=all --enable=duplicate-code coffee_maker/
```

**Refactoring approach:**
- Extract common code to utility function
- Create base class for shared behavior
- Use composition over inheritance
- Create reusable helper module

#### 4. Poor Test Coverage

**Detection:**
```bash
# Find files with <80% coverage
pytest --cov=coffee_maker --cov-report=term-missing | grep -E "[0-7][0-9]%"
```

**Refactoring approach:**
- Add unit tests for uncovered code
- Add integration tests for workflows
- Mock external dependencies
- Test error paths

---

## Creating Refactoring Plans

### Step 1: Use the Template

Start with the template:

```bash
cp docs/architecture/refactoring/templates/REFACTOR_TEMPLATE.md \
   docs/architecture/refactoring/active/REFACTOR_$(date +%Y_%m_%d)_brief_description.md
```

### Step 2: Document Current State

**Required sections:**

1. **Why Refactor?**
   - Clear problem statement
   - Objective metrics (complexity, lines, coverage)
   - Pain points from code review

2. **Current State**
   - Code snippet showing the problem
   - Specific issues list
   - Metrics baseline

3. **Target State**
   - Code snippet showing desired structure
   - Expected improvements
   - Metrics targets

### Step 3: Create Actionable Tasks

Each task must include:

- **Title**: Brief, descriptive (e.g., "Extract SpecManagerMixin")
- **Estimate**: Hours required (be realistic)
- **What**: Clear description of the change
- **How**: Step-by-step approach
- **Files to modify**: Exact file paths
- **Tests**: Testing requirements

**Good Task Example:**

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
- `coffee_maker/autonomous/daemon.py` - Remove methods, add mixin
- `coffee_maker/autonomous/mixins/spec_manager.py` - NEW FILE
- `coffee_maker/autonomous/mixins/__init__.py` - Export SpecManagerMixin

**Tests**:
- Add `tests/unit/mixins/test_spec_manager.py` with unit tests
- Update `tests/unit/test_daemon.py` to verify mixin integration
- Run integration tests to verify spec workflow unchanged
```

**Bad Task Example** (too vague):

```markdown
### Task 1: Improve DevDaemon

Make DevDaemon better by refactoring it.
```

### Step 4: Define Acceptance Criteria

Must be **objective and measurable**:

✅ Good:
```markdown
- [ ] DevDaemon.py reduced from 1592 lines to <500 lines
- [ ] Complexity score reduced from 47 to <20
- [ ] All 247 existing tests passing
- [ ] Test coverage maintained at >92%
- [ ] Pylint score improved from 7.2 to >8.0
```

❌ Bad:
```markdown
- [ ] Code is better
- [ ] Everything works
- [ ] Tests pass
```

### Step 5: Add Verification Commands

Provide **exact commands** code_developer can run:

```markdown
## Verification

```bash
# Check complexity improved
radon cc coffee_maker/autonomous/daemon.py -a
# Expected: Complexity <20, Grade A or B

# Check line count reduced
wc -l coffee_maker/autonomous/daemon.py
# Expected: <500 lines

# Run unit tests
pytest tests/unit/test_daemon.py -v
# Expected: All passing

# Run integration tests
pytest tests/integration/test_daemon_workflow.py -v
# Expected: All passing

# Check coverage maintained
pytest --cov=coffee_maker/autonomous/daemon.py --cov-report=term
# Expected: >90%

# Full test suite
pytest
# Expected: All passing, no regressions
```
```

---

## ROADMAP Integration

### Adding Refactoring Priority

After creating refactoring plan, architect should notify project_manager to add to ROADMAP:

**Format:**

```markdown
### REFACTOR-001: Simplify DevDaemon Class

**Status**: 📝 PLANNED
**Type**: Refactoring / Technical Debt
**Priority**: HIGH
**Estimated**: 2 days
**Owner**: code_developer
**Reviewer**: architect

**See**: docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md

**Metrics**:
- Current complexity: 47 → Target: <20
- Current lines: 1592 → Target: <500
- Impact: Improves maintainability, enables faster feature development

**Acceptance Criteria**:
- [ ] Refactoring plan completed
- [ ] All metrics targets achieved
- [ ] All tests passing
- [ ] architect review approved
```

### Priority Levels

**HIGH** (Do this week):
- Complexity >30
- Files >2000 lines
- Architecture violations
- Blocking new features

**MEDIUM** (Do this month):
- Complexity 20-30
- Files 1500-2000 lines
- Code duplication
- Test coverage <80%

**LOW** (Nice to have):
- Complexity 15-20
- Files 1000-1500 lines
- Code style improvements
- Documentation gaps

---

## Review Process

### After code_developer Completes Refactoring

#### Step 1: Run Verification Commands

Run the exact commands from the refactoring plan:

```bash
# Example verification
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt044

# Check complexity improved
radon cc coffee_maker/autonomous/daemon.py -a

# Check line count
wc -l coffee_maker/autonomous/daemon.py

# Run tests
pytest tests/unit/test_daemon.py -v
pytest tests/integration/ -v

# Check coverage
pytest --cov=coffee_maker --cov-report=term-missing
```

#### Step 2: Verify Acceptance Criteria

Go through each checkbox in the refactoring plan:

```markdown
## Acceptance Criteria Review

- [x] DevDaemon.py reduced from 1592 to 487 lines ✅
- [x] Complexity reduced from 47 to 18 ✅
- [x] All 247 tests passing ✅
- [x] Coverage maintained at 93.2% ✅
- [x] Pylint score 8.4 ✅
```

#### Step 3: Code Quality Check

Review the actual code changes:

**Check for:**
- ✅ Code follows style guide (.gemini/styleguide.md)
- ✅ Type hints present
- ✅ Documentation updated
- ✅ No functionality broken
- ✅ Error handling maintained
- ✅ No new technical debt introduced

#### Step 4: Document Results

Add results section to refactoring plan:

```markdown
## Refactoring Results

**Completed**: 2025-10-21
**Reviewed by**: architect
**Time spent**: 14 hours (estimated 16 hours)

### Metrics Achieved

| Metric | Before | After | Target | Status |
|--------|--------|-------|--------|--------|
| Lines | 1592 | 487 | <500 | ✅ |
| Complexity | 47 | 18 | <20 | ✅ |
| Tests | 247 | 261 | 247+ | ✅ |
| Coverage | 92.1% | 93.2% | >90% | ✅ |
| Pylint | 7.2 | 8.4 | >8.0 | ✅ |

### Benefits Realized

1. **Maintainability**: Code much easier to understand and modify
2. **Testability**: Extracted methods easier to unit test
3. **Performance**: 15% faster startup (bonus improvement)
4. **Developer Experience**: New developers can understand flow

### Lessons Learned

1. Mixin pattern worked well for separating concerns
2. Integration tests caught 2 edge cases during refactoring
3. Time estimate was accurate (14h vs 16h estimated)
4. Should have created POC for mixin extraction approach

**Status**: ✅ APPROVED
```

#### Step 5: Move to Completed

```bash
# Move to completed directory
mv docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md \
   docs/architecture/refactoring/completed/REFACTOR_2025_10_16_daemon_simplification_COMPLETED.md
```

#### Step 6: Update ROADMAP

Notify project_manager to update ROADMAP status to ✅ COMPLETE.

---

## Complete Example

### Scenario: DevDaemon is too complex

**Monday 9am: Monitoring**

```bash
# Run weekly complexity check
./scripts/check_complexity.sh > docs/architecture/refactoring/weekly_2025_10_16.txt

# Review output
cat docs/architecture/refactoring/weekly_2025_10_16.txt
```

**Output shows:**
```
coffee_maker/autonomous/daemon.py
    M 156:4 DevDaemon.run - E (47)
```

**Decision:** Complexity 47 is CRITICAL (grade E). Must refactor this week.

---

**Monday 11am: Create Refactoring Plan**

```bash
# Copy template
cp docs/architecture/refactoring/templates/REFACTOR_TEMPLATE.md \
   docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md

# Edit plan with specific tasks
```

Fill in:
- Current state: 1592 lines, complexity 47
- Target state: <500 lines, complexity <20
- 6 specific tasks for code_developer
- Acceptance criteria with measurable targets
- Verification commands

---

**Monday 2pm: Notify project_manager**

Create ROADMAP entry:

```markdown
### REFACTOR-001: Simplify DevDaemon Class

**Status**: 📝 PLANNED
**Priority**: HIGH
**Estimated**: 2 days
**See**: docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md
```

---

**Tuesday-Thursday: code_developer works**

code_developer executes the 6 tasks in the refactoring plan.

---

**Friday 4pm: architect Review**

```bash
# Run verification commands
radon cc coffee_maker/autonomous/daemon.py -a
# Result: Complexity 18 ✅

wc -l coffee_maker/autonomous/daemon.py
# Result: 487 lines ✅

pytest
# Result: All 261 tests passing ✅

pytest --cov=coffee_maker --cov-report=term
# Result: 93.2% coverage ✅
```

**Review code changes:**
- Extracted 3 mixins properly
- All methods have type hints ✅
- Tests comprehensive ✅
- Documentation updated ✅

**Approve refactoring:**

```bash
# Add results to plan
# Move to completed
mv docs/architecture/refactoring/active/REFACTOR_2025_10_16_daemon_simplification.md \
   docs/architecture/refactoring/completed/REFACTOR_2025_10_16_daemon_simplification_COMPLETED.md

# Update ROADMAP
# REFACTOR-001 status: ✅ COMPLETE
```

---

## Quick Reference

### architect Weekly Checklist

**Monday:**
- [ ] Run `./scripts/check_complexity.sh`
- [ ] Review metrics for thresholds exceeded
- [ ] Identify 3-5 refactoring opportunities
- [ ] Create refactoring plan if critical issues found
- [ ] Notify project_manager to add to ROADMAP

**Friday:**
- [ ] Review completed refactorings
- [ ] Run verification commands
- [ ] Check acceptance criteria met
- [ ] Document results and lessons learned
- [ ] Move completed plans to `completed/` directory
- [ ] Update ROADMAP status

### Decision Matrix

| Complexity | Lines | Priority | Timeline |
|------------|-------|----------|----------|
| >40 | >2000 | CRITICAL | This week |
| 30-40 | 1500-2000 | HIGH | This week |
| 20-30 | 1000-1500 | MEDIUM | This month |
| 15-20 | 500-1000 | LOW | Next quarter |

### Key Commands

```bash
# Weekly complexity check
./scripts/check_complexity.sh > docs/architecture/refactoring/weekly_$(date +%Y_%m_%d).txt

# Find complex functions
radon cc coffee_maker/ -a -s | grep -E " [D-F] \("

# Find large files
find coffee_maker -name "*.py" -exec wc -l {} + | sort -rn | head -10

# Check test coverage
pytest --cov=coffee_maker --cov-report=term-missing

# Create new refactoring plan
cp docs/architecture/refactoring/templates/REFACTOR_TEMPLATE.md \
   docs/architecture/refactoring/active/REFACTOR_$(date +%Y_%m_%d)_description.md
```

---

## Related Documents

- [CODE_DEVELOPER_WORKFLOW.md](./CODE_DEVELOPER_WORKFLOW.md) - How code_developer executes refactoring
- [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) - Detailed metrics interpretation
- [REFACTOR_TEMPLATE.md](./templates/REFACTOR_TEMPLATE.md) - Template for new plans
- [US-044](../../roadmap/ROADMAP.md#us-044) - User story for this workflow
- [CFR-005](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md) - Ownership includes maintenance
- [CFR-011](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md) - Code quality integration

---

**Last Updated**: 2025-10-21
**Version**: 1.0
**Status**: Production ✅
