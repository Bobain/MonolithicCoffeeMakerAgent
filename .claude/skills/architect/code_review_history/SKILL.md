# Code Review History Navigator

**Agent**: architect

**Purpose**: Navigate, analyze, and extract insights from code-review history to improve specs and identify recurring quality issues.

**Time Savings**: 30-45 minutes → 2-3 minutes (85-93% reduction)

---

## What This Skill Does

Analyzes the complete history of code reviews in `docs/code-reviews/` to:

1. **Track Quality Trends**: See if quality scores are improving or declining over time
2. **Identify Recurring Issues**: Find patterns in issues across multiple reviews
3. **Measure Improvement**: Compare before/after quality on same modules
4. **Extract Insights**: Generate actionable recommendations for spec updates
5. **Review Summary**: Get quick overview of recent reviews and their status

---

## When To Use

architect should use this skill **frequently**:

- **Daily**: Quick check of recent reviews (last 3-5 commits)
- **Weekly**: Full trend analysis to identify patterns
- **Before Spec Updates**: Review relevant module history before creating/updating specs
- **After code_developer completes priority**: Check review to see if spec was clear enough
- **When notified**: After code-reviewer sends high-priority notification

---

## Usage

```bash
# Analyze recent reviews (last 7 days)
architect code-review-history --recent

# Analyze specific module/file
architect code-review-history --module coffee_maker/autonomous/daemon.py

# Full trend analysis (all reviews)
architect code-review-history --trends

# Find recurring issues
architect code-review-history --recurring-issues

# Compare quality over time
architect code-review-history --quality-trend
```

---

## Output Format

### Recent Reviews Summary

```markdown
# Code Review History - Recent Reviews

**Period**: Last 7 days (2025-10-12 to 2025-10-19)
**Total Reviews**: 15
**Average Quality Score**: 82/100
**Trend**: ⬆️ Improving (+5 points from last week)

---

## Reviews

### ✅ 2025-10-19 - commit abc123d (Score: 95/100)
- **Files**: 3 files (+50, -20)
- **Status**: APPROVED - Excellent quality
- **Issues**: 1 low (documentation)
- **Report**: [REVIEW-2025-10-19-abc123d.md](../../../docs/code-reviews/REVIEW-2025-10-19-abc123d.md)

### ⚠️ 2025-10-18 - commit def456a (Score: 75/100)
- **Files**: 5 files (+120, -45)
- **Status**: APPROVED WITH NOTES
- **Issues**: 2 medium (architecture, test coverage)
- **Report**: [REVIEW-2025-10-18-def456a.md](../../../docs/code-reviews/REVIEW-2025-10-18-def456a.md)

### ❌ 2025-10-17 - commit ghi789b (Score: 55/100)
- **Files**: 2 files (+80, -10)
- **Status**: REQUEST CHANGES
- **Issues**: 1 high (security), 2 medium (performance, style)
- **Report**: [REVIEW-2025-10-17-ghi789b.md](../../../docs/code-reviews/REVIEW-2025-10-17-ghi789b.md)
```

---

### Recurring Issues Analysis

```markdown
# Recurring Issues Analysis

**Period**: Last 30 reviews

---

## Top Recurring Issues (by frequency)

### 1. Test Coverage Below 80% (12 occurrences)
- **Severity**: MEDIUM
- **Files Most Affected**:
  - coffee_maker/autonomous/daemon.py (5 times)
  - coffee_maker/cli/roadmap_cli.py (4 times)
  - coffee_maker/autonomous/orchestrator.py (3 times)
- **Recommendation**:
  - Update SPEC-* to require >80% coverage
  - Add test coverage requirements to DoD
  - Create guideline for test patterns

### 2. Missing Type Hints (8 occurrences)
- **Severity**: LOW
- **Files Most Affected**:
  - Various utility modules
- **Recommendation**:
  - Update .gemini/styleguide.md to emphasize type hints
  - Add mypy pre-commit hook with stricter settings

### 3. High Cyclomatic Complexity (6 occurrences)
- **Severity**: MEDIUM
- **Modules**: daemon.py, orchestrator.py
- **Recommendation**:
  - Create refactoring guideline for complex functions
  - Add complexity limits to coding standards
```

---

### Quality Trend Analysis

```markdown
# Quality Trend Analysis

**Period**: Last 60 days
**Total Reviews**: 45

---

## Overall Trends

**Average Quality Score**: 78/100
- Week 1 (Oct 1-7): 72/100 ⬇️
- Week 2 (Oct 8-14): 75/100 ⬆️
- Week 3 (Oct 15-21): 81/100 ⬆️
- Week 4 (Oct 22-28): 85/100 ⬆️

**Trend**: ⬆️ Improving steadily (+13 points over 4 weeks)

---

## Issues Breakdown

| Severity | Week 1 | Week 2 | Week 3 | Week 4 | Trend |
|----------|--------|--------|--------|--------|-------|
| Critical | 2      | 1      | 0      | 0      | ✅ Eliminated |
| High     | 5      | 4      | 2      | 1      | ⬆️ Improving |
| Medium   | 12     | 10     | 8      | 6      | ⬆️ Improving |
| Low      | 8      | 9      | 7      | 5      | ⬆️ Improving |

---

## Insights

1. **Critical Issues Eliminated**: No critical issues in last 2 weeks
2. **Code Quality Improving**: Average score up 18% in 4 weeks
3. **Test Coverage Improving**: More tests being written
4. **Style Compliance Better**: Fewer style violations
```

---

## Implementation

The skill should:

1. **Read all review files** from `docs/code-reviews/`
2. **Parse markdown reports** to extract:
   - Commit SHA, date, quality score
   - Issues (severity, category, file, description)
   - Overall status (approved, changes requested, etc.)
3. **Aggregate data** across reviews
4. **Identify patterns**:
   - Same issue appearing in multiple reviews
   - Same file having repeated issues
   - Quality trends over time
5. **Generate insights**:
   - What specs need updating
   - What guidelines should be created
   - What refactoring is needed

---

## Benefits for architect

1. **Data-Driven Spec Updates**: See exactly what issues keep appearing → update specs to prevent
2. **Quality Monitoring**: Track if code quality is improving over time
3. **Proactive Refactoring**: Identify modules that need architectural attention
4. **Refactoring Planning**: Extract insights to inform refactoring priorities and design
5. **Continuous Improvement**: Use review history to improve development process
6. **Time Savings**: 30-45 min manual review → 2-3 min automated analysis

---

## Integration with Refactoring Plans

architect can use code-review insights to enhance refactoring planning:

### 1. Identify Refactoring Candidates

```bash
# Find modules with recurring quality issues
architect code-review-history --refactoring-candidates

# Output:
# Refactoring Priority List (based on review history)
#
# 1. coffee_maker/autonomous/daemon.py
#    - Quality Score: 65/100 (average over 10 reviews)
#    - Recurring Issues: High complexity (8x), Low test coverage (6x)
#    - Recommendation: URGENT - Extract mixins, add tests
#    - Estimated Effort: 2-3 days
#    - Business Value: HIGH (core daemon reliability)
#
# 2. coffee_maker/cli/roadmap_cli.py
#    - Quality Score: 72/100 (average over 7 reviews)
#    - Recurring Issues: Test coverage (5x), Type hints missing (4x)
#    - Recommendation: Medium priority - Add tests, type hints
#    - Estimated Effort: 1-2 days
#    - Business Value: MEDIUM (CLI usability)
```

### 2. Enrich Refactoring Specs with Review Insights

When architect creates refactoring specs, include review history:

```markdown
# SPEC-XXX: Refactor daemon.py Complexity

## Motivation (Evidence-Based)

**Code Review History Analysis**:
- 10 reviews of daemon.py in last 30 days
- Average quality score: 65/100 (below 80% target)
- Recurring issues:
  - High cyclomatic complexity: 8 occurrences
    - Functions with complexity >15: _execute_priority(), _handle_errors()
  - Low test coverage: 6 occurrences
    - Current coverage: 62% (target: >80%)
  - Architecture violations: 3 occurrences
    - Missing singleton enforcement in 2 places

**Quality Trend**: ⬇️ Declining (-10 points over 3 weeks)

**Root Cause** (from review recommendations):
- Monolithic functions doing too much
- Insufficient test coverage for error paths
- Missing abstraction layers

## Refactoring Goals

Based on review insights:
1. Reduce complexity to <10 per function (currently: 15-20)
2. Increase test coverage to >80% (currently: 62%)
3. Extract error handling to mixin pattern
4. Add missing singleton enforcement

## Success Criteria

code-reviewer should report:
- ✅ Quality score >85/100 (currently: 65/100)
- ✅ Zero high-complexity warnings (currently: 8)
- ✅ Test coverage >80% (currently: 62%)
- ✅ Zero architecture violations (currently: 3)
```

### 3. Track Refactoring Success

After refactoring, verify improvement:

```bash
# Compare before/after quality for refactored module
architect code-review-history --compare daemon.py --before 2025-10-01 --after 2025-10-19

# Output:
# daemon.py Quality Comparison
#
# BEFORE Refactoring (Oct 1-14):
# - Average Score: 65/100
# - Issues: 23 total (8 high complexity, 6 low coverage, 9 other)
# - Test Coverage: 62%
# - Complexity: 15-20 per function
#
# AFTER Refactoring (Oct 15-19):
# - Average Score: 88/100 ⬆️ (+23 points)
# - Issues: 5 total (0 high complexity, 2 low, 3 style)
# - Test Coverage: 85% ⬆️ (+23%)
# - Complexity: 5-8 per function ⬆️ (50% reduction)
#
# ✅ REFACTORING SUCCESSFUL! Quality improved by 35%
```

### 4. Prioritize Refactoring Work

Generate refactoring priority matrix based on:
- **Impact**: Quality score × Number of reviews (how often touched)
- **Urgency**: Severity of recurring issues
- **Effort**: Estimated refactoring time (from complexity metrics)

```bash
architect code-review-history --refactoring-matrix

# Output:
# Refactoring Priority Matrix
#
# HIGH IMPACT + HIGH URGENCY (DO FIRST):
# 1. daemon.py - Impact: 95, Urgency: 90, Effort: 3 days
# 2. orchestrator.py - Impact: 88, Urgency: 75, Effort: 2 days
#
# HIGH IMPACT + LOW URGENCY (PLAN NEXT):
# 3. roadmap_cli.py - Impact: 80, Urgency: 50, Effort: 1 day
#
# LOW IMPACT + HIGH URGENCY (QUICK WINS):
# 4. utils.py - Impact: 40, Urgency: 85, Effort: 4 hours
```

### 5. Generate Refactoring Insights Document

Create comprehensive refactoring plan:

```bash
architect code-review-history --refactoring-insights > docs/architecture/REFACTORING_INSIGHTS_2025-10-19.md

# Generates:
# - Summary of all modules needing refactoring
# - Evidence from code reviews
# - Recommended refactoring patterns
# - Effort estimates
# - Success criteria
# - Before/after quality targets
```

---

## Integration with code-reviewer

1. **code-reviewer** creates review reports in `docs/code-reviews/`
2. **code-reviewer** notifies architect of high-priority issues
3. **architect** uses this skill to analyze history
4. **architect** updates specs based on insights
5. **code_developer** implements better code following updated specs
6. **code-reviewer** verifies improvement in next review

**Quality Feedback Loop Complete!** 🔄

---

## Example Workflow

```bash
# Morning routine: architect checks recent reviews
architect code-review-history --recent

# Output shows 2 medium issues in daemon.py
# architect investigates:
architect code-review-history --module coffee_maker/autonomous/daemon.py

# Output shows daemon.py has low test coverage in 5 reviews
# architect decides to update SPEC-072 with test coverage requirements

# architect also runs trend analysis weekly
architect code-review-history --trends

# Output shows quality improving steadily
# architect generates weekly report for user
```

---

## Success Metrics

- **architect reads reviews**: Daily (recent) + Weekly (trends)
- **Spec updates based on insights**: 2-3 per week
- **Recurring issues reduced**: Track month-over-month
- **Quality score trending up**: +5-10 points per month
- **Time saved**: 3-4 hours/week on manual review analysis

---

## Version

**Created**: 2025-10-19
**Status**: Active
**Priority**: HIGH (architect daily routine)
**Agent**: architect
**Time Savings**: 85-93%
