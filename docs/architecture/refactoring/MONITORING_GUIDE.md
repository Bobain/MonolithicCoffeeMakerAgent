# Code Quality Monitoring Guide

**Owner**: architect agent

**Purpose**: Detailed guide for interpreting code quality metrics and making refactoring decisions.

**Related**: US-044, ARCHITECT_WORKFLOW.md

---

## Table of Contents

1. [Overview](#overview)
2. [Radon Metrics](#radon-metrics)
3. [Pylint Analysis](#pylint-analysis)
4. [Test Coverage](#test-coverage)
5. [Decision Matrix](#decision-matrix)
6. [Baseline Analysis](#baseline-analysis)

---

## Overview

### Monitoring Philosophy

**Proactive, not reactive**: Monitor weekly to catch issues early.

**Objective thresholds**: Use measurable criteria for decisions.

**Track trends**: Monitor improvement/degradation over time.

### Weekly Monitoring Routine

**Monday 9am:**
```bash
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent-wt044
./scripts/check_complexity.sh > docs/architecture/refactoring/weekly_$(date +%Y_%m_%d).txt
cat docs/architecture/refactoring/weekly_$(date +%Y_%m_%d).txt
```

---

## Radon Metrics

### Cyclomatic Complexity

**What it measures**: Number of independent paths through code.

**Formula**: `E = edges - nodes + 2*connected_components`

#### Interpreting Scores

| Score | Grade | Meaning | Action |
|-------|-------|---------|--------|
| 1-5 | A | Simple, easy to understand | ✅ Good |
| 6-10 | B | Acceptable complexity | ✅ OK |
| 11-20 | C | Complex, monitor | ⚠️ Watch |
| 21-30 | D | Very complex, hard to maintain | 🔴 Plan refactoring |
| 31-40 | E | Extremely complex, error-prone | 🔴 Refactor now |
| 41+ | F | Critical, unmaintainable | 🔴 Refactor immediately |

#### Example Output

```bash
$ radon cc coffee_maker/autonomous/daemon.py -a

coffee_maker/autonomous/daemon.py
    M 156:4 DevDaemon.run - E (47)
    M 244:4 DevDaemon._implement_priority - C (15)
    M 310:4 DevDaemon._create_spec - B (8)
    M 350:4 DevDaemon._update_status - A (3)

Average complexity: C (18.25)
```

**Interpretation:**
- `M` = Method (F = Function, C = Class)
- `156:4` = Line 156, indent level 4
- `E (47)` = Grade E, complexity 47
- **run()** method: CRITICAL - needs immediate refactoring
- **_implement_priority()**: Complex - plan refactoring this month
- **_create_spec()**: Acceptable
- **_update_status()**: Good

#### Decision Criteria

```
Complexity > 40: CRITICAL - Refactor this week
Complexity 30-40: HIGH - Refactor within 2 weeks
Complexity 20-30: MEDIUM - Refactor this month
Complexity 15-20: LOW - Monitor, refactor next quarter
Complexity < 15: Good - no action needed
```

#### Common Causes & Solutions

**Cause 1: Deep nesting**
```python
# Bad - complexity 15
def process(data):
    if data:
        if data.valid:
            if data.type == "A":
                if data.status:
                    # Process
                    pass
```

**Solution: Early returns**
```python
# Good - complexity 5
def process(data):
    if not data:
        return
    if not data.valid:
        return
    if data.type != "A":
        return
    if not data.status:
        return
    # Process
```

**Cause 2: Many conditions**
```python
# Bad - complexity 10
def validate(user):
    if user.age > 18 and user.country == "US" and user.verified and user.active and not user.banned:
        return True
```

**Solution: Extract to helper methods**
```python
# Good - complexity 2
def validate(user):
    return (
        is_adult(user) and
        is_us_user(user) and
        is_verified_active(user) and
        not is_banned(user)
    )
```

**Cause 3: Long switch/if-elif chains**
```python
# Bad - complexity 12
def handle(action):
    if action == "create":
        # ...
    elif action == "update":
        # ...
    elif action == "delete":
        # ...
    # ... 10 more elif blocks
```

**Solution: Strategy pattern or dispatch dict**
```python
# Good - complexity 2
HANDLERS = {
    "create": handle_create,
    "update": handle_update,
    "delete": handle_delete,
    # ...
}

def handle(action):
    handler = HANDLERS.get(action, handle_unknown)
    return handler()
```

---

### Maintainability Index

**What it measures**: Overall maintainability based on complexity, lines, and Halstead volume.

**Scale**: 0-100 (higher is better)

#### Interpreting Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 65-100 | Highly maintainable | ✅ Good |
| 20-64 | Moderately maintainable | ⚠️ Monitor |
| 0-19 | Difficult to maintain | 🔴 Refactor |

#### Example Output

```bash
$ radon mi coffee_maker/autonomous/daemon.py -s

coffee_maker/autonomous/daemon.py - A (72.34)
coffee_maker/autonomous/mixins/spec_manager.py - A (85.21)
coffee_maker/cli/chat.py - B (45.12)
coffee_maker/services/ai_client.py - C (18.67)
```

**Interpretation:**
- daemon.py: Good maintainability (72)
- spec_manager.py: Excellent maintainability (85)
- chat.py: Moderate maintainability (45) - monitor
- ai_client.py: Poor maintainability (18) - refactor

#### Decision Criteria

```
MI < 20: CRITICAL - Refactor this week
MI 20-40: MEDIUM - Plan refactoring this month
MI 40-65: OK - Monitor trends
MI > 65: Good - no action needed
```

---

### Halstead Metrics (Advanced)

**What it measures**: Program complexity based on operators and operands.

**Use case**: Deep analysis of algorithmic complexity.

```bash
$ radon hal coffee_maker/autonomous/daemon.py
```

**Key metrics:**
- **Volume**: Size and complexity
- **Difficulty**: How hard to understand
- **Effort**: Mental effort to understand
- **Bugs**: Estimated bugs (higher = more bugs)

**Typical thresholds:**
- Volume < 1000: Simple
- Difficulty < 30: Easy to understand
- Estimated bugs < 1.0: Low risk

---

## Pylint Analysis

### Overall Score

**Scale**: 0-10 (higher is better)

```bash
$ pylint coffee_maker/ --score=y

Your code has been rated at 7.85/10
```

#### Interpreting Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 9.0-10.0 | Excellent | ✅ Maintain |
| 8.0-8.9 | Good | ✅ OK |
| 7.0-7.9 | Acceptable | ⚠️ Improve |
| 5.0-6.9 | Poor | 🔴 Fix issues |
| 0-4.9 | Critical | 🔴 Major cleanup needed |

#### Decision Criteria

```
Pylint < 5.0: CRITICAL - Fix this week
Pylint 5.0-7.0: MEDIUM - Plan improvements
Pylint 7.0-8.0: OK - Monitor
Pylint > 8.0: Good - maintain
```

---

### Message Categories

Pylint reports 4 categories of issues:

#### C (Convention) - Style violations

**Examples:**
- Line too long
- Missing docstring
- Bad variable name
- Inconsistent formatting

**Priority**: LOW (unless many violations)

**Action**: Fix during refactoring, not urgent

#### R (Refactor) - Code smell suggestions

**Examples:**
- Too many branches
- Too many return statements
- Duplicate code
- Too many instance attributes

**Priority**: MEDIUM

**Action**: Consider during planning

#### W (Warning) - Potential bugs

**Examples:**
- Unused variable
- Undefined variable
- Dangerous default argument
- Attribute defined outside __init__

**Priority**: HIGH

**Action**: Fix soon, may cause bugs

#### E (Error) - Definite bugs

**Examples:**
- Import error
- Syntax error
- Undefined name
- Method missing

**Priority**: CRITICAL

**Action**: Fix immediately

---

### Filtering Pylint Output

**Show only errors and warnings:**
```bash
pylint coffee_maker/ --disable=C,R
```

**Show only high-priority issues:**
```bash
pylint coffee_maker/ --disable=all --enable=E,F
```

**Check specific file:**
```bash
pylint coffee_maker/autonomous/daemon.py
```

**Generate detailed report:**
```bash
pylint coffee_maker/ --output-format=json > pylint_report.json
```

---

## Test Coverage

### Coverage Percentage

**What it measures**: Percentage of code executed by tests.

```bash
$ pytest --cov=coffee_maker --cov-report=term

Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
coffee_maker/__init__.py                    5      0   100%
coffee_maker/autonomous/daemon.py         487     35    93%
coffee_maker/cli/chat.py                  312     94    70%
coffee_maker/services/ai_client.py        156     12    92%
-----------------------------------------------------------
TOTAL                                    2847    234    92%
```

#### Interpreting Coverage

| Coverage | Meaning | Action |
|----------|---------|--------|
| 95-100% | Excellent | ✅ Maintain |
| 90-94% | Good | ✅ OK |
| 80-89% | Acceptable | ⚠️ Improve |
| 70-79% | Poor | 🔴 Add tests |
| < 70% | Critical | 🔴 Major gaps |

#### Coverage by Component Type

Different components have different standards:

| Component | Target | Rationale |
|-----------|--------|-----------|
| Business logic | 100% | Critical paths must be tested |
| Data processing | 95%+ | Important algorithms |
| API/CLI | 80%+ | UI has manual testing too |
| Utils/helpers | 100% | Reused everywhere |
| Config/setup | 70%+ | Often simple, low risk |

---

### Missing Coverage Analysis

**Show uncovered lines:**
```bash
pytest --cov=coffee_maker --cov-report=term-missing
```

**Output:**
```
Name                                    Stmts   Miss  Cover   Missing
----------------------------------------------------------------------
coffee_maker/autonomous/daemon.py         487     35    93%   156-158, 234-245, 389
```

**Interpretation:**
- Lines 156-158: 3 consecutive lines (likely a block)
- Lines 234-245: 12 lines (likely an error handler or branch)
- Line 389: Single line (likely rare condition)

**Priority:**
1. Check what these lines do
2. If error handling: add error test cases
3. If rare condition: add edge case tests
4. If dead code: remove it

---

### HTML Coverage Report

**Generate interactive report:**
```bash
pytest --cov=coffee_maker --cov-report=html
open htmlcov/index.html
```

**Benefits:**
- Visual highlighting of covered/uncovered code
- Click through files to see exact lines
- Identify patterns (e.g., all error handlers uncovered)

---

## Decision Matrix

### Comprehensive Refactoring Decision

Consider all metrics together:

```python
def should_refactor(file_metrics):
    """Decision logic for refactoring."""

    # CRITICAL - refactor this week
    if (
        file_metrics.complexity > 40 or
        file_metrics.lines > 2000 or
        file_metrics.mi < 20 or
        file_metrics.pylint < 5.0 or
        file_metrics.coverage < 70
    ):
        return "CRITICAL", "Refactor this week"

    # HIGH - refactor within 2 weeks
    if (
        file_metrics.complexity > 30 or
        file_metrics.lines > 1500 or
        file_metrics.mi < 40 or
        file_metrics.pylint < 7.0 or
        file_metrics.coverage < 80
    ):
        return "HIGH", "Plan refactoring this month"

    # MEDIUM - refactor this quarter
    if (
        file_metrics.complexity > 20 or
        file_metrics.lines > 1000 or
        file_metrics.mi < 60 or
        file_metrics.pylint < 8.0 or
        file_metrics.coverage < 90
    ):
        return "MEDIUM", "Monitor, refactor next quarter"

    # Good - no action needed
    return "OK", "No action needed"
```

### Example Analysis

**File:** `coffee_maker/autonomous/daemon.py`

**Metrics:**
- Lines: 1592
- Complexity: 47
- MI: 45
- Pylint: 7.2
- Coverage: 92%

**Decision:**
```
Priority: CRITICAL
Reason: Complexity (47) > 40 AND Lines (1592) > 1500
Action: Create refactoring plan THIS WEEK
Approach: Extract mixins, simplify main loop
Estimated effort: 2-3 days
```

---

## Baseline Analysis

### Creating Baseline

When starting monitoring, create baseline:

```bash
# Full complexity baseline
./scripts/check_complexity.sh > docs/architecture/refactoring/baseline_complexity_$(date +%Y_%m_%d).txt

# Coverage baseline
pytest --cov=coffee_maker --cov-report=term > docs/architecture/refactoring/baseline_coverage_$(date +%Y_%m_%d).txt
```

### Tracking Trends

**Weekly comparison:**

```bash
# This week
./scripts/check_complexity.sh > /tmp/this_week.txt

# Last week
cat docs/architecture/refactoring/weekly_2025_10_14.txt > /tmp/last_week.txt

# Compare
diff /tmp/last_week.txt /tmp/this_week.txt
```

**Look for:**
- ✅ Complexity decreasing (good)
- ✅ MI increasing (good)
- ✅ Pylint score improving (good)
- ✅ Coverage increasing (good)
- 🔴 Any metric worsening (investigate)

### Example Trend Analysis

**Week 1:**
```
daemon.py - Complexity: 47, MI: 45, Pylint: 7.2, Coverage: 92%
```

**Week 2 (after refactoring):**
```
daemon.py - Complexity: 18, MI: 72, Pylint: 8.4, Coverage: 93%
```

**Analysis:**
- ✅ Complexity reduced by 62% (47 → 18)
- ✅ MI improved by 60% (45 → 72)
- ✅ Pylint improved by 17% (7.2 → 8.4)
- ✅ Coverage maintained (92% → 93%)
- **Conclusion**: Refactoring successful, all metrics improved

---

## Automated Monitoring

### Creating Weekly Reports

**Script:** `scripts/weekly_quality_check.sh`

```bash
#!/bin/bash
# Weekly code quality monitoring

REPORT_DIR="docs/architecture/refactoring"
DATE=$(date +%Y_%m_%d)
REPORT_FILE="$REPORT_DIR/weekly_$DATE.txt"

echo "=== Weekly Code Quality Report ===" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "=== Cyclomatic Complexity ===" >> $REPORT_FILE
radon cc coffee_maker/ -a -s >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "=== Maintainability Index ===" >> $REPORT_FILE
radon mi coffee_maker/ -s >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "=== Pylint Score ===" >> $REPORT_FILE
pylint coffee_maker/ --score=y >> $REPORT_FILE 2>&1

echo "" >> $REPORT_FILE
echo "=== Test Coverage ===" >> $REPORT_FILE
pytest --cov=coffee_maker --cov-report=term >> $REPORT_FILE 2>&1

echo "" >> $REPORT_FILE
echo "=== Files Over 1000 Lines ===" >> $REPORT_FILE
find coffee_maker -name "*.py" -exec wc -l {} + | sort -rn | head -10 >> $REPORT_FILE

echo "Report saved to: $REPORT_FILE"
```

---

## Quick Reference

### Threshold Summary

| Metric | Good | OK | Monitor | Refactor |
|--------|------|----|---------|---------
| Complexity | <10 | 10-15 | 15-20 | >20 |
| MI | >65 | 40-65 | 20-40 | <20 |
| Pylint | >8.0 | 7.0-8.0 | 5.0-7.0 | <5.0 |
| Coverage | >95% | 90-95% | 80-90% | <80% |
| Lines | <500 | 500-1000 | 1000-1500 | >1500 |

### Key Commands

```bash
# Weekly monitoring
./scripts/check_complexity.sh

# Complexity by file
radon cc coffee_maker/ -a -s

# Maintainability index
radon mi coffee_maker/ -s

# Pylint score
pylint coffee_maker/ --score=y

# Test coverage
pytest --cov=coffee_maker --cov-report=term-missing

# Coverage HTML report
pytest --cov=coffee_maker --cov-report=html
open htmlcov/index.html

# Find large files
find coffee_maker -name "*.py" -exec wc -l {} + | sort -rn | head -10

# Find complex functions
radon cc coffee_maker/ -a | grep -E " [D-F] \("
```

---

## Related Documents

- [ARCHITECT_WORKFLOW.md](./ARCHITECT_WORKFLOW.md) - Using metrics for decisions
- [CODE_DEVELOPER_WORKFLOW.md](./CODE_DEVELOPER_WORKFLOW.md) - Improving metrics
- [US-044](../../roadmap/ROADMAP.md#us-044) - Refactoring workflow

---

**Last Updated**: 2025-10-21
**Version**: 1.0
**Status**: Production ✅
