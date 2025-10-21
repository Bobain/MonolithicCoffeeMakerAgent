# SPEC-044: Regular Refactoring Workflow

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: US-044 (ROADMAP), ADR-003 (Simplification-First Approach)

**Related ADRs**: None

**Assigned To**: architect (monitoring), code_developer (execution)

---

## Executive Summary

This specification describes a lightweight weekly refactoring workflow where architect proactively monitors code quality, identifies technical debt, and creates simple refactoring tasks for code_developer. Uses existing tools (radon, pylint) and a simple Markdown-based task format.

---

## Problem Statement

### Current Situation

Technical debt accumulates over time:
- No proactive code quality monitoring
- Refactoring happens reactively (when things break)
- No systematic approach to identifying debt
- Large files grow unchecked (daemon.py was 1592 lines!)
- Complexity increases silently

**Proof**: US-021 (massive refactoring effort) was reactive, took weeks

### Goal

Establish regular refactoring workflow where:
- architect monitors code quality **weekly**
- architect identifies debt **before it's critical**
- architect creates **small, specific tasks** for code_developer
- code_developer executes tasks **incrementally** (2-4 hours each)
- System quality improves **continuously**

### Non-Goals

- NOT automated refactoring (human judgment needed)
- NOT replacing US-021 style major refactorings (those still needed occasionally)
- NOT creating complex CI/CD pipelines (simple weekly check)
- NOT enforcing hard metrics (guidelines, not gates)

---

## Requirements

### Functional Requirements

1. **FR-1**: architect monitors code quality weekly (every Monday)
2. **FR-2**: architect identifies 3-5 refactoring opportunities per week
3. **FR-3**: architect creates refactoring task file (docs/architecture/refactoring/REFACTOR_YYYY_MM_DD.md)
4. **FR-4**: code_developer executes 1-2 tasks per week (2-4 hours total)
5. **FR-5**: architect reviews completed refactorings (quality check)

### Non-Functional Requirements

1. **NFR-1**: Low overhead: < 2 hours/week for architect
2. **NFR-2**: Incremental: Tasks take 1-2 hours each (not days)
3. **NFR-3**: Sustainable: Process doesn't burden team
4. **NFR-4**: Measurable: Track quality metrics over time

### Constraints

- Must use existing tools (radon, pylint already installed)
- Must not block feature development (refactoring is background work)
- Must integrate with ROADMAP (refactoring tasks added as priorities when urgent)

---

## Proposed Solution

### High-Level Approach

**Weekly Monitoring Ritual**:
1. **Monday 9am**: architect runs quality check script
2. **Monday 10am**: architect reviews results, creates 3-5 small tasks
3. **Week**: code_developer picks 1-2 tasks during downtime
4. **Friday 4pm**: architect reviews completed refactorings
5. **Next Monday**: Repeat cycle

**Why This is Simple**:
- Uses existing tools (no new infrastructure)
- Simple Markdown task format (no complex tracking system)
- Lightweight (2 hours/week total)
- Incremental (small tasks, continuous improvement)

### Workflow Diagram

```
MONDAY (architect):
  ┌─────────────────────────────────┐
  │ 1. Run quality check script     │
  │    python scripts/check_code_quality.py │
  └────────────┬────────────────────┘
               ├─> Radon (complexity)
               ├─> Pylint (style/errors)
               ├─> File size report
               └─> Duplication scan
  ┌─────────────────────────────────┐
  │ 2. Review results               │
  │    Identify 3-5 opportunities   │
  └────────────┬────────────────────┘
               v
  ┌─────────────────────────────────┐
  │ 3. Create refactoring task file │
  │    docs/architecture/refactoring/│
  │    REFACTOR_2025_10_21.md      │
  └────────────┬────────────────────┘
               v
  ┌─────────────────────────────────┐
  │ 4. Notify code_developer        │
  │    (comment in task file)       │
  └─────────────────────────────────┘

DURING WEEK (code_developer):
  ┌─────────────────────────────────┐
  │ 5. Pick 1-2 tasks during downtime│
  └────────────┬────────────────────┘
               v
  ┌─────────────────────────────────┐
  │ 6. Execute refactoring          │
  │    (1-2 hours per task)         │
  └────────────┬────────────────────┘
               v
  ┌─────────────────────────────────┐
  │ 7. Mark task complete           │
  │    (check box in task file)     │
  └─────────────────────────────────┘

FRIDAY (architect):
  ┌─────────────────────────────────┐
  │ 8. Review completed refactorings│
  │    (verify quality, run tests)  │
  └────────────┬────────────────────┘
               v
  ┌─────────────────────────────────┐
  │ 9. Update metrics tracker       │
  │    (record progress)            │
  └─────────────────────────────────┘
```

---

## Detailed Design

### Component 1: Quality Check Script

**File**: `scripts/check_code_quality.py` (~150 lines)

**Purpose**: Automated weekly code quality scan

**Interface**:
```python
"""
Weekly code quality check script.

Usage:
    python scripts/check_code_quality.py

Output:
    - Terminal report (colored, formatted)
    - JSON file: data/quality_reports/report_YYYY_MM_DD.json
"""

import radon.complexity as radon_cc
import radon.metrics as radon_mi
import subprocess
from pathlib import Path
import json

def check_complexity() -> dict:
    """Run radon complexity analysis."""
    # Find functions with complexity > 15
    # Return: {file: [(function, complexity), ...]}
    pass

def check_file_sizes() -> dict:
    """Find files > 1000 lines."""
    # Return: {file: line_count}
    pass

def check_duplication() -> dict:
    """Find duplicate code blocks (simple heuristic)."""
    # Use: difflib or similar
    # Return: {pattern: [file1, file2, ...]}
    pass

def check_test_coverage() -> float:
    """Get overall test coverage."""
    # Run: pytest --cov
    # Return: coverage percentage
    pass

def generate_report() -> dict:
    """Generate complete quality report."""
    return {
        "date": "2025-10-21",
        "complexity": check_complexity(),
        "file_sizes": check_file_sizes(),
        "duplication": check_duplication(),
        "test_coverage": check_test_coverage(),
        "recommendations": generate_recommendations()
    }

def generate_recommendations() -> list:
    """Suggest refactoring opportunities."""
    # Based on thresholds:
    # - Complexity > 15: Simplify function
    # - File > 1000 lines: Split file
    # - Duplication > 3: Extract common code
    # - Coverage < 80%: Add tests
    pass

if __name__ == "__main__":
    report = generate_report()

    # Save JSON
    Path("data/quality_reports").mkdir(exist_ok=True)
    with open(f"data/quality_reports/report_{report['date']}.json", 'w') as f:
        json.dump(report, f, indent=2)

    # Print terminal report
    print_report(report)
```

### Component 2: Refactoring Task Template

**File**: `docs/architecture/refactoring/REFACTOR_YYYY_MM_DD.md`

**Format**:
```markdown
# Refactoring Tasks - Week of YYYY-MM-DD

**Created**: YYYY-MM-DD by architect
**Status**: In Progress / Complete
**Completed**: X / 5 tasks

---

## Quality Metrics (Current)

- **Average Complexity**: 12.3 (target: < 10)
- **Files > 1000 lines**: 3 files (down from 5 last week ✅)
- **Test Coverage**: 78% (up from 76% last week ✅)
- **Duplicate Blocks**: 8 (target: < 5)

---

## Task 1: Simplify `daemon.py::_execute_priority()` (Complexity 18 → 10)

**Priority**: HIGH
**Estimated**: 1 hour
**Status**: [ ] Pending / [x] Complete

**Problem**:
```python
# daemon.py line 450
def _execute_priority(self, priority: dict) -> bool:
    # 18 complexity (too high!)
    # 80 lines with nested conditionals
```

**Solution**:
Extract helper functions:
- `_validate_priority()` (validation logic)
- `_prepare_context()` (context building)
- `_handle_failure()` (error handling)

**Acceptance Criteria**:
- Complexity reduced to < 10
- All tests pass
- No behavior changes

**Files to Modify**:
- `coffee_maker/autonomous/daemon.py`

---

## Task 2: Split `chat_interface.py` (1215 lines → 3 files × 400 lines)

**Priority**: MEDIUM
**Estimated**: 2 hours
**Status**: [ ] Pending

**Problem**:
`chat_interface.py` is 1215 lines (too large)

**Solution**:
Split into:
- `chat_ui.py` (UI components) ~400 lines
- `message_handler.py` (message processing) ~400 lines
- `session_manager.py` (session state) ~400 lines

**Acceptance Criteria**:
- 3 files created
- All imports updated
- Tests pass
- No duplicated code

**Files to Create**:
- `coffee_maker/cli/chat_ui.py`
- `coffee_maker/cli/message_handler.py`
- `coffee_maker/cli/session_manager.py`

**Files to Modify**:
- `coffee_maker/cli/chat_interface.py` (becomes stub importing from new files)

---

## Task 3: Extract duplicate JSON I/O pattern (10 occurrences → 1 utility)

**Priority**: MEDIUM
**Estimated**: 1 hour
**Status**: [ ] Pending

**Problem**:
10 files have duplicated JSON read/write logic

**Solution**:
Already have `coffee_maker/utils/file_io.py`, but some files don't use it.

**Migrate these files**:
- `coffee_maker/cli/roadmap_cli.py` (line 234)
- `coffee_maker/autonomous/developer_status.py` (line 89)
- `scripts/update_roadmap.py` (line 45)
- [... 7 more files]

**Acceptance Criteria**:
- All files use `file_io.read_json()` / `file_io.write_json()`
- No duplicated JSON I/O code
- Tests pass

---

## Task 4: Add missing docstrings (15 functions)

**Priority**: LOW
**Estimated**: 1 hour
**Status**: [ ] Pending

**Problem**:
15 public functions lack docstrings

**Solution**:
Add Google-style docstrings to:
- `coffee_maker/cli/notifications.py::send_notification()` (line 67)
- `coffee_maker/utils/time.py::format_duration()` (line 123)
- [... 13 more functions]

**Acceptance Criteria**:
- All public functions have docstrings
- Docstrings include: Args, Returns, Raises, Example

---

## Task 5: Increase test coverage for `daemon.py` (68% → 80%)

**Priority**: MEDIUM
**Estimated**: 2 hours
**Status**: [ ] Pending

**Problem**:
`daemon.py` coverage is 68% (below 80% target)

**Solution**:
Add tests for:
- Error recovery paths (not currently tested)
- Edge cases (empty priority, missing content)
- Cleanup logic (stale PID cleanup)

**Acceptance Criteria**:
- Coverage > 80%
- All new tests pass
- No flaky tests

**Files to Modify**:
- `tests/unit/test_daemon.py`

---

## Summary

**This Week's Focus**:
- Complexity reduction (Task 1)
- File splitting (Task 2)

**Deferred**:
- Duplication cleanup (Task 3) - next week
- Documentation (Task 4) - ongoing
- Testing (Task 5) - next week

**Metrics Goal**:
- Complete 2 tasks → Complexity down to 11.5, Files > 1000 down to 2

---

**architect Review Notes** (Friday):
[architect fills this in after reviewing completed work]

- Task 1: ✅ Complete, complexity now 9, tests passing
- Task 2: ⏸️ Deferred (blocked by X)
- Overall: Good progress, system improving incrementally
```

### Component 3: Metrics Tracker

**File**: `data/quality_metrics/metrics.json`

**Format**:
```json
{
  "metrics_history": [
    {
      "date": "2025-10-21",
      "avg_complexity": 12.3,
      "files_over_1000_lines": 3,
      "test_coverage": 78.0,
      "duplicate_blocks": 8,
      "tasks_completed": 2,
      "tasks_total": 5
    },
    {
      "date": "2025-10-14",
      "avg_complexity": 13.1,
      "files_over_1000_lines": 5,
      "test_coverage": 76.0,
      "duplicate_blocks": 10,
      "tasks_completed": 1,
      "tasks_total": 4
    }
  ],
  "trends": {
    "complexity": "IMPROVING (-0.8 in last week)",
    "file_sizes": "IMPROVING (-2 files in last week)",
    "test_coverage": "IMPROVING (+2% in last week)",
    "duplication": "IMPROVING (-2 blocks in last week)"
  }
}
```

---

## Testing Strategy

### Validation

**Week 1 Trial Run**:
1. architect runs `check_code_quality.py`
2. architect creates `REFACTOR_2025_10_21.md` with 5 tasks
3. code_developer executes 2 tasks
4. architect reviews Friday
5. Evaluate: Is process sustainable?

**Acceptance Criteria**:
- Quality check script works (< 5 minutes runtime)
- Tasks are clear and actionable
- code_developer completes 2 tasks in < 4 hours
- Quality metrics improve
- Process feels sustainable (not burdensome)

---

## Rollout Plan

### Phase 1: Setup (Day 1 - 3 hours)

**Goal**: Create automation and templates

**Tasks**:
1. Create `scripts/check_code_quality.py` (150 lines, 2 hours)
2. Create refactoring task template (30 minutes)
3. Create `data/quality_metrics/` directory
4. Test quality check script on current codebase

**Success Criteria**:
- Script runs successfully
- Report generated
- Recommendations make sense

### Phase 2: First Weekly Cycle (Week 1 - 6 hours total)

**Goal**: Validate workflow with real tasks

**Tasks**:
1. **Monday**: architect runs quality check, creates 5 tasks (1 hour)
2. **Week**: code_developer executes 2 tasks (4 hours)
3. **Friday**: architect reviews, updates metrics (1 hour)

**Success Criteria**:
- 2 tasks completed
- Quality metrics improved
- Process felt smooth (not burdensome)

### Phase 3: Iteration (Ongoing)

**Goal**: Refine based on experience

**Tasks**:
1. Adjust task complexity based on time taken
2. Tune quality thresholds (what triggers tasks)
3. Improve quality check script (add more checks)
4. Document lessons learned

**Success Criteria**:
- Process sustainable long-term
- Consistent quality improvement
- Low overhead (< 2 hours/week)

---

## Decision Criteria

### When to Create Refactoring Task

architect creates task when:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Function complexity | > 15 | Simplify function (extract helpers) |
| File size | > 1000 lines | Split file |
| Duplication | > 3 instances | Extract common code |
| Test coverage | < 80% | Add tests |
| Architecture violation | Any | Fix immediately |

### When to Escalate to ROADMAP

Some refactorings too big for weekly tasks → add to ROADMAP:

| Condition | Action |
|-----------|--------|
| Task > 1 day | Add to ROADMAP as priority |
| Multiple tasks related | Create epic in ROADMAP |
| User-visible impact | Get user approval first |
| Breaking changes | Plan carefully, add to ROADMAP |

**Example**: US-021 was too big for weekly workflow → full ROADMAP priority

---

## Risks & Mitigations

### Risk 1: Refactoring Slows Feature Development

**Likelihood**: Medium

**Impact**: Medium (features delayed)

**Mitigation**:
- Keep tasks small (1-2 hours each)
- code_developer does refactoring during downtime (not blocking features)
- If urgent features, skip week (refactoring is background work)

### Risk 2: Quality Check Script Becomes Slow

**Likelihood**: Low (current codebase ~25k LOC)

**Impact**: Low (annoying, not blocking)

**Mitigation**:
- Cache results where possible
- Parallelize checks
- Set timeout (max 5 minutes)

### Risk 3: Refactoring Introduces Bugs

**Likelihood**: Low (tests catch issues)

**Impact**: High (production bugs)

**Mitigation**:
- ALL refactorings must pass tests
- architect reviews all refactorings Friday
- Small, incremental changes (easier to debug)
- Revert quickly if issues found

---

## Why This is Simple (vs Strategic Spec)

**Strategic Spec** (US-044 in ROADMAP):
- Mentioned complex monitoring tools
- Continuous quality dashboards
- Automated refactoring suggestions
- Integration with CI/CD pipelines
- ~2-3 days estimate

**This Simplified Spec**:
- **Simple script** (150 lines Python, uses existing tools)
- **Markdown task files** (no complex tracking system)
- **Weekly ritual** (not continuous monitoring)
- **Manual decision-making** (architect reviews, not automated)
- **Same 2-3 days estimate** (but simpler implementation)

**What We REUSE**:
- Existing radon, pylint (already installed)
- Existing docs/ structure (new refactoring/ subdirectory)
- Existing quality tools (pytest --cov)
- Existing Markdown format (consistent with project)

**Complexity Reduction**:
- **No CI/CD integration** (weekly manual check)
- **No automated refactoring** (human judgment)
- **No complex dashboards** (simple JSON metrics)
- **Incremental tasks** (1-2 hours each, not days)

---

## Future Enhancements

**NOT in this spec** (deferred):
1. Automated refactoring suggestions (AI-powered) → When AI reliable
2. Real-time quality monitoring (CI/CD integration) → When CI/CD mature
3. Interactive quality dashboard (Streamlit) → When visualization needed
4. Complexity trends visualization (charts) → Nice-to-have
5. Multi-repo support → When we have multiple repos

---

## References

- US-044: Regular Refactoring Workflow (ROADMAP)
- US-021: Code Refactoring & Technical Debt Reduction (example of reactive refactoring)
- ADR-003: Simplification-First Approach
- Radon documentation: https://radon.readthedocs.io/
- Pylint documentation: https://pylint.readthedocs.io/

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created (Draft) | architect |

---

## Approval

- [ ] architect (author) - Ready for review
- [ ] code_developer (implementer) - Can implement in 2-3 days
- [ ] project_manager (strategic alignment) - Meets US-044 goals
- [ ] User (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 2-3 days (Setup: 3 hours, First cycle: 6 hours, Iteration: ongoing)

**Ongoing Effort**: ~2 hours/week (architect 1 hour, code_developer 4 hours/month)
