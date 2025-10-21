# Refactoring Workflow Integration Guide

**Purpose**: Complete end-to-end guide showing how refactoring workflow integrates with the autonomous agent system.

**Audience**: All agents (architect, code_developer, project_manager, orchestrator)

**Related**: US-044, CFR-005 (Ownership Includes Maintenance), CFR-011 (Code Quality Integration)

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Workflow](#complete-workflow)
3. [Agent Responsibilities](#agent-responsibilities)
4. [Integration Points](#integration-points)
5. [Real-World Example](#real-world-example)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What is the Refactoring Workflow?

The refactoring workflow is a **systematic, proactive approach** to technical debt reduction:

- **Weekly monitoring** by architect identifies code quality issues
- **Detailed planning** creates actionable refactoring tasks
- **Autonomous execution** by code_developer implements improvements
- **Review and verification** ensures quality improvements achieved
- **Continuous tracking** documents progress over time

### Why This Workflow Matters

**Before US-044**:
- ❌ Refactoring happened reactively (when things broke)
- ❌ Technical debt accumulated over time
- ❌ No systematic approach to code quality
- ❌ Code became harder to maintain

**After US-044**:
- ✅ Proactive weekly monitoring prevents debt accumulation
- ✅ Clear criteria trigger refactoring at right time
- ✅ Detailed plans guide code_developer execution
- ✅ Metrics track improvement over time
- ✅ Codebase stays clean and maintainable

### Key Workflow Components

```
┌─────────────────────────────────────────────────────────┐
│                  Weekly Monitoring                       │
│                   (architect)                            │
│  - Run complexity metrics                                │
│  - Check code quality thresholds                         │
│  - Identify refactoring opportunities                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Decision Making                          │
│                   (architect)                            │
│  - Evaluate priority vs. new features                    │
│  - Decide if refactoring needed now                      │
│  - Balance technical debt vs. delivery                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Create Refactoring Plan                     │
│                   (architect)                            │
│  - Document current state and problems                   │
│  - Define target state and goals                         │
│  - Break down into actionable tasks                      │
│  - Set acceptance criteria                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Add to ROADMAP                             │
│                (project_manager)                         │
│  - Create REFACTOR-XXX priority                          │
│  - Set priority level and estimate                       │
│  - Link to refactoring plan                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│             Execute Refactoring                          │
│                (code_developer)                          │
│  - Read refactoring plan                                 │
│  - Execute tasks incrementally                           │
│  - Test after each change                                │
│  - Report progress                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Review and Verify                           │
│                   (architect)                            │
│  - Run verification commands                             │
│  - Check acceptance criteria met                         │
│  - Review code quality                                   │
│  - Document results                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Complete                                │
│           (project_manager)                              │
│  - Update ROADMAP status to ✅ Complete                  │
│  - Archive refactoring plan                              │
│  - Track metrics improvement                             │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Workflow

### Phase 1: Weekly Monitoring (Monday 9am)

**Agent**: architect

**Schedule**: Every Monday 9:00 AM

**Actions**:

```bash
# 1. Run complexity analysis
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent
./scripts/check_complexity.sh > docs/architecture/refactoring/weekly_$(date +%Y_%m_%d).txt

# 2. Review the output
cat docs/architecture/refactoring/weekly_$(date +%Y_%m_%d).txt

# 3. Identify issues exceeding thresholds
radon cc coffee_maker/ -a -s | grep -E " [D-F] \("  # Complexity >20

# 4. Find large files
find coffee_maker -name "*.py" -exec wc -l {} + | sort -rn | head -10

# 5. Check test coverage
pytest --cov=coffee_maker --cov-report=term-missing | grep -E "[0-7][0-9]%"
```

**Decision Criteria**:

| Metric | Threshold | Action | Priority |
|--------|-----------|--------|----------|
| Complexity | >40 | Refactor immediately | CRITICAL |
| Complexity | 30-40 | Refactor this week | HIGH |
| Complexity | 20-30 | Refactor this month | MEDIUM |
| File lines | >2000 | Split file this week | HIGH |
| File lines | 1500-2000 | Plan file split | MEDIUM |
| Coverage | <80% | Add tests this week | HIGH |
| Duplication | >3 instances | Extract common code | MEDIUM |

**Output**: List of issues requiring refactoring

---

### Phase 2: Decision Making (Monday 10am)

**Agent**: architect

**Questions to Answer**:

1. **Is refactoring needed now?**
   - Critical issues (complexity >40, files >2000 lines) → YES
   - Medium issues + low upcoming feature load → YES
   - Minor issues + high feature pressure → Defer to next month

2. **Can this be automated?**
   - Simple renames, imports → Use automated tools
   - Complex logic changes → Manual refactoring

3. **Should user be notified?**
   - Estimate >1 week → Escalate to user for approval
   - Estimate <1 week → Proceed autonomously

4. **What's the priority?**
   - Blocking new features → CRITICAL
   - Architecture violations → HIGH
   - Quality improvements → MEDIUM
   - Nice-to-haves → LOW

**Output**: Decision on whether to create refactoring plan

---

### Phase 3: Create Refactoring Plan (Monday 11am - 2pm)

**Agent**: architect

**Steps**:

```bash
# 1. Copy template
cp docs/architecture/refactoring/templates/REFACTOR_TEMPLATE.md \
   docs/architecture/refactoring/active/REFACTOR_$(date +%Y_%m_%d)_brief_description.md

# 2. Edit plan
# Fill in all sections:
# - Why Refactor? (problem statement + metrics)
# - Current State (code snippets, specific issues)
# - Target State (desired structure, metrics goals)
# - Tasks for code_developer (6-10 actionable tasks)
# - Acceptance Criteria (measurable success metrics)
# - Verification (exact commands to run)

# 3. Estimate effort
# Count hours per task:
# - Simple extraction: 2-4 hours
# - Module split: 4-8 hours
# - Complex restructuring: 8-16 hours
# Total estimate = sum of task estimates
```

**Quality Checklist**:
- [ ] Problem clearly stated with metrics
- [ ] Current state code snippets included
- [ ] Target state code snippets show desired structure
- [ ] Each task is specific and actionable
- [ ] Estimates are realistic
- [ ] Acceptance criteria are measurable
- [ ] Verification commands are exact (copy-paste ready)

**Output**: Detailed refactoring plan in `docs/architecture/refactoring/active/`

---

### Phase 4: ROADMAP Integration (Monday 2pm)

**Agent**: architect → project_manager

**architect creates notification**:

```python
# architect notifies project_manager
from coffee_maker.database.notification_db import NotificationDB

NotificationDB.create_notification(
    agent_id="architect",
    title="New Refactoring Plan: Simplify DevDaemon Class",
    message="""
    Created refactoring plan: REFACTOR_2025_10_21_daemon_simplification.md

    Metrics:
    - Current complexity: 47 (Grade E - Extremely Complex)
    - Current lines: 1011
    - Priority: HIGH (blocking new features)
    - Estimated effort: 2 days (16 hours)

    Please add to ROADMAP as REFACTOR-001.

    See: docs/architecture/refactoring/active/REFACTOR_2025_10_21_daemon_simplification.md
    """,
    priority="high",
    sound=False,  # CFR-009: architect is background agent
)
```

**project_manager adds to ROADMAP**:

```markdown
### REFACTOR-001: Simplify DevDaemon Class

**Status**: 📝 PLANNED
**Type**: Refactoring / Technical Debt
**Priority**: HIGH
**Estimated**: 2 days (16 hours)
**Owner**: code_developer
**Reviewer**: architect
**Created**: 2025-10-21

**Problem**:
- DevDaemon complexity: 47 (Grade E - Extremely Complex)
- File size: 1011 lines
- Blocking: New feature development difficult

**Refactoring Plan**: `docs/architecture/refactoring/active/REFACTOR_2025_10_21_daemon_simplification.md`

**Metrics Goals**:
- Complexity: 47 → <20
- Lines: 1011 → <500
- Pylint score: 7.2 → >8.0

**Acceptance Criteria**:
- [ ] Complexity reduced to <20
- [ ] File size reduced to <500 lines
- [ ] All 247 tests passing
- [ ] Coverage maintained at >90%
- [ ] architect review approved
```

**Output**: REFACTOR priority added to ROADMAP

---

### Phase 5: Autonomous Execution (Tuesday - Thursday)

**Agent**: code_developer (autonomous daemon)

**How code_developer finds the task**:

```python
# code_developer daemon polls ROADMAP
# Finds next PLANNED priority: REFACTOR-001
# Reads refactoring plan from link
# Executes tasks sequentially
```

**Execution Loop**:

```
For each task in refactoring plan:
    1. Read task description
    2. Understand "before" and "after" state
    3. Make code changes incrementally
    4. Run tests after each change
    5. Verify tests pass
    6. Commit with clear message
    7. Update task status
    8. Move to next task
```

**Example Task Execution**:

```markdown
### Task 1: Extract SpecManagerMixin (4 hours)

code_developer reads:
- What: Move spec management logic to separate module
- How: Create new file, move methods, update imports
- Files: daemon.py, mixins/spec_manager.py (NEW)
- Tests: Add unit tests for SpecManagerMixin

code_developer executes:
1. Create coffee_maker/autonomous/mixins/spec_manager.py
2. Move _create_spec_if_needed() method
3. Move _validate_spec_exists() method
4. Move _get_spec_path() method
5. Create SpecManagerMixin class
6. Update DevDaemon to inherit from SpecManagerMixin
7. Run tests: pytest tests/unit/test_daemon.py
8. Verify: All tests pass ✅
9. Commit: "Extract SpecManagerMixin to separate module"
10. Mark task complete
```

**Progress Reporting**:

```python
# code_developer updates progress
NotificationDB.create_notification(
    agent_id="code_developer",
    title="Refactoring Progress: REFACTOR-001",
    message="Completed 2/6 tasks (33%). Next: Simplify main run() loop.",
    priority="normal",
    sound=False,
)
```

**Output**: Refactoring implemented, committed, tests passing

---

### Phase 6: Review and Verification (Friday 4pm)

**Agent**: architect

**Steps**:

```bash
# 1. Run verification commands from refactoring plan
radon cc coffee_maker/autonomous/daemon.py -a
# Expected: Complexity <20 ✅

wc -l coffee_maker/autonomous/daemon.py
# Expected: <500 lines ✅

pytest tests/unit/test_daemon.py -v
# Expected: All passing ✅

pytest --cov=coffee_maker/autonomous/daemon.py --cov-report=term
# Expected: >90% coverage ✅

# 2. Check acceptance criteria
# Go through each checkbox in refactoring plan

# 3. Review code quality
# - Follows style guide?
# - Type hints present?
# - Documentation updated?
# - No new technical debt?

# 4. Document results
# Add "Refactoring Results" section to plan

# 5. Move to completed
mv docs/architecture/refactoring/active/REFACTOR_2025_10_21_daemon_simplification.md \
   docs/architecture/refactoring/completed/REFACTOR_2025_10_21_daemon_simplification_COMPLETED.md
```

**Review Checklist**:
- [ ] All verification commands pass
- [ ] All acceptance criteria met
- [ ] Code follows style guide
- [ ] Tests comprehensive
- [ ] Documentation updated
- [ ] No regressions introduced
- [ ] Metrics improved as expected

**Output**: Approval or rejection with feedback

---

### Phase 7: Completion (Friday 5pm)

**Agent**: architect → project_manager

**architect notifies completion**:

```python
NotificationDB.create_notification(
    agent_id="architect",
    title="Refactoring Complete: REFACTOR-001",
    message="""
    ✅ REFACTOR-001 completed and approved

    Metrics Achieved:
    - Complexity: 47 → 18 ✅
    - Lines: 1011 → 487 ✅
    - Pylint: 7.2 → 8.4 ✅
    - Coverage: 92.1% → 93.2% ✅

    All acceptance criteria met. Ready to mark complete in ROADMAP.

    Plan archived to: docs/architecture/refactoring/completed/REFACTOR_2025_10_21_daemon_simplification_COMPLETED.md
    """,
    priority="normal",
    sound=False,
)
```

**project_manager updates ROADMAP**:

```markdown
### REFACTOR-001: Simplify DevDaemon Class ✅ COMPLETE

**Status**: ✅ COMPLETE (2025-10-25)
**Completed**: 2025-10-25
**Time Spent**: 14 hours (estimated 16 hours)

**Metrics Achieved**:
- Complexity: 47 → 18 ✅ (Target: <20)
- Lines: 1011 → 487 ✅ (Target: <500)
- Pylint: 7.2 → 8.4 ✅ (Target: >8.0)
- Coverage: 92.1% → 93.2% ✅ (Target: >90%)

**Plan**: `docs/architecture/refactoring/completed/REFACTOR_2025_10_21_daemon_simplification_COMPLETED.md`
```

**Output**: ROADMAP updated, metrics tracked, workflow complete

---

## Agent Responsibilities

### architect

**Proactive Monitoring** (Weekly):
- Run `./scripts/check_complexity.sh` every Monday
- Review metrics for threshold violations
- Identify 3-5 refactoring opportunities

**Decision Making**:
- Decide when refactoring is needed
- Balance technical debt vs. feature delivery
- Escalate to user if major refactoring (>1 week)

**Planning**:
- Create detailed refactoring plans
- Break down into actionable tasks
- Set measurable acceptance criteria
- Provide exact verification commands

**Review**:
- Verify code_developer completed work correctly
- Check all acceptance criteria met
- Review code quality improvements
- Document results and lessons learned

**Documents Owned**:
- `docs/architecture/refactoring/active/*.md`
- `docs/architecture/refactoring/completed/*.md`
- Weekly complexity reports

---

### code_developer

**Execution**:
- Read refactoring plans from ROADMAP
- Execute tasks exactly as specified
- Make changes incrementally
- Test after each change

**Progress Reporting**:
- Update task status
- Report blockers immediately
- Notify when complete

**Quality**:
- Follow style guide
- Maintain test coverage
- Run verification commands
- Ensure no regressions

**Autonomous Operation**:
- Works from ROADMAP priorities
- Executes refactoring like any other task
- No special handling required

---

### project_manager

**ROADMAP Management**:
- Add REFACTOR-XXX priorities
- Set priority levels and estimates
- Track progress
- Update status to ✅ Complete

**Coordination**:
- Receives notifications from architect
- Coordinates refactoring with feature work
- Balances priorities

**Metrics Tracking**:
- Track before/after metrics
- Document time spent vs. estimated
- Report on technical debt reduction

---

### orchestrator

**Work Distribution**:
- Includes refactoring in work queue
- Schedules refactoring at appropriate times
- Coordinates with other priorities

**Monitoring**:
- Tracks refactoring progress
- Alerts if refactoring blocked
- Ensures regular cadence

---

## Integration Points

### With ROADMAP.md

Refactoring tasks integrate seamlessly:

```markdown
## 🔴 TOP PRIORITY FOR code_developer

**CURRENT PRIORITY**: REFACTOR-001 - Simplify DevDaemon Class

**NEXT PRIORITIES**:
- US-045 - New Feature X
- REFACTOR-002 - Clean up API client
- US-046 - New Feature Y
```

code_developer daemon reads ROADMAP and executes refactoring just like features.

---

### With Notification System

Agents communicate via notifications:

```python
# architect creates refactoring plan
architect → NotificationDB → project_manager
"New refactoring plan ready for ROADMAP"

# code_developer reports progress
code_developer → NotificationDB → architect
"REFACTOR-001: 50% complete (3/6 tasks done)"

# architect approves completion
architect → NotificationDB → project_manager
"REFACTOR-001 approved, ready to mark complete"
```

---

### With Git Workflow (CFR-013)

All work happens on `roadmap` branch:

```bash
# code_developer commits refactoring work
git checkout roadmap  # Always on roadmap branch
git add coffee_maker/autonomous/mixins/spec_manager.py
git commit -m "refactor: Extract SpecManagerMixin to separate module

- Move spec management logic from DevDaemon to dedicated module
- Reduces DevDaemon complexity from 47 to 38
- Adds unit tests for SpecManagerMixin
- Part of REFACTOR-001

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### With CI/CD

Tests run automatically:

```yaml
# .github/workflows/tests.yml
on:
  push:
    branches: [roadmap, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: pytest

      - name: Check complexity
        run: radon cc coffee_maker/ -a -s

      - name: Coverage
        run: pytest --cov=coffee_maker
```

Refactoring commits trigger same CI as feature commits.

---

## Real-World Example

### Scenario: chat_interface.py Too Complex

**Monday 9am - architect Monitoring**:

```bash
./scripts/check_complexity.sh > weekly_2025_10_21.txt
cat weekly_2025_10_21.txt
```

**Output**:
```
coffee_maker/cli/chat_interface.py
    M 134:4 DeveloperStatusMonitor.get_formatted_status - D (22)
    File: 1612 lines
```

**architect Decision**: File >1500 lines AND complexity D (22) → Refactor this week

---

**Monday 11am - architect Creates Plan**:

```bash
cp templates/REFACTOR_TEMPLATE.md \
   active/REFACTOR_2025_10_21_chat_interface_simplification.md
```

**Plan Contents**:
```markdown
## Why Refactor?

chat_interface.py has grown to 1612 lines with complexity D (22).
- Too many responsibilities (monitoring, completers, session management)
- Hard to test components in isolation
- Blocking: Can't add new CLI features easily

## Current State

File: 1612 lines
- DeveloperStatusMonitor: 134 lines, complexity 22
- ProjectManagerCompleter: 100 lines
- ChatSession: 1100+ lines

## Target State

File: <800 lines
- Extract monitor to coffee_maker/monitoring/status_monitor.py
- Extract completer to coffee_maker/cli/completers.py
- Simplify ChatSession to core logic only
- Complexity: All methods <10

## Tasks for code_developer

### Task 1: Extract DeveloperStatusMonitor (4 hours)
[Details...]

### Task 2: Extract ProjectManagerCompleter (3 hours)
[Details...]

### Task 3: Simplify ChatSession (5 hours)
[Details...]

## Acceptance Criteria

- [ ] chat_interface.py <800 lines
- [ ] All methods complexity <10
- [ ] Extracted modules have >90% test coverage
- [ ] All existing tests pass
```

---

**Monday 2pm - project_manager Adds to ROADMAP**:

```markdown
### REFACTOR-001: Simplify chat_interface.py

**Status**: 📝 PLANNED
**Priority**: MEDIUM
**Estimated**: 1.5 days (12 hours)
**See**: docs/architecture/refactoring/active/REFACTOR_2025_10_21_chat_interface_simplification.md
```

---

**Tuesday - code_developer Execution**:

```bash
# code_developer daemon starts
poetry run code-developer --auto-approve

# Reads ROADMAP, finds REFACTOR-001
# Reads refactoring plan
# Executes Task 1: Extract DeveloperStatusMonitor

# 1. Create new file
touch coffee_maker/monitoring/status_monitor.py

# 2. Move class
# [code changes...]

# 3. Update imports
# [code changes...]

# 4. Run tests
pytest tests/unit/test_chat_interface.py

# 5. Commit
git add .
git commit -m "refactor: Extract DeveloperStatusMonitor to separate module"

# 6. Continue to Task 2...
```

---

**Friday 4pm - architect Review**:

```bash
# Verify metrics
wc -l coffee_maker/cli/chat_interface.py
# Result: 762 lines ✅ (target <800)

radon cc coffee_maker/cli/chat_interface.py -a
# Result: All methods <10 complexity ✅

pytest
# Result: All 380 tests passing ✅

# Approve!
```

---

**Friday 5pm - Completion**:

project_manager updates ROADMAP:
```markdown
### REFACTOR-001: Simplify chat_interface.py ✅ COMPLETE

**Metrics Achieved**:
- Lines: 1612 → 762 ✅
- Complexity: 22 → 8 ✅
- Tests: All passing ✅
```

---

## Troubleshooting

### Problem: Tests Fail After Refactoring

**Symptoms**:
```bash
pytest
FAILED tests/unit/test_daemon.py::test_spec_creation
```

**Solution**:
```bash
# 1. Revert the change that broke tests
git checkout HEAD -- coffee_maker/autonomous/daemon.py

# 2. Run tests again - should pass
pytest tests/unit/test_daemon.py

# 3. Re-apply change more carefully
# 4. Update tests if needed
# 5. Commit only when all tests pass
```

---

### Problem: Refactoring Taking Longer Than Estimated

**Symptoms**: Estimated 2 days, now on day 4

**Solution**:
```python
# code_developer notifies architect
NotificationDB.create_notification(
    agent_id="code_developer",
    title="REFACTOR-001: Estimate Exceeded",
    message="""
    Original estimate: 16 hours
    Time spent: 24 hours
    Progress: 4/6 tasks complete (67%)

    Blocker: Integration tests more complex than expected.
    Need additional 8 hours to complete remaining tasks.
    """,
    priority="high",
    sound=False,
)

# architect evaluates options:
# 1. Continue (approved)
# 2. Split remaining work to new refactoring
# 3. Defer remaining tasks
```

---

### Problem: Acceptance Criteria Not Met

**Symptoms**: Complexity reduced to 25, target was <20

**Solution**:

```markdown
## Review Results

Acceptance Criteria:
- [x] File size <500 lines ✅
- [ ] Complexity <20 ❌ (achieved 25)
- [x] Tests passing ✅

**Decision**: APPROVED with follow-up

Rationale:
- Complexity improved from 47 to 25 (47% improvement)
- File size target met
- Further simplification requires architectural changes
- Create REFACTOR-002 for remaining complexity reduction

Follow-up: REFACTOR-002 to reduce complexity 25 → <20
```

---

### Problem: Circular Dependencies After Refactoring

**Symptoms**:
```python
ImportError: cannot import name 'DevDaemon' from partially initialized module
```

**Solution**:

```python
# ❌ BEFORE: Circular dependency
# coffee_maker/autonomous/daemon.py
from coffee_maker.autonomous.spec_manager import SpecManager

# coffee_maker/autonomous/spec_manager.py
from coffee_maker/autonomous.daemon import DevDaemon  # CIRCULAR!

# ✅ AFTER: Break circular dependency
# Option 1: Use TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coffee_maker.autonomous.daemon import DevDaemon

# Option 2: Use protocol/interface
from typing import Protocol
class DaemonProtocol(Protocol):
    def get_spec_path(self) -> Path: ...

# Option 3: Restructure to remove dependency
```

---

## Quick Reference

### Weekly Schedule

**Monday**:
- 9am: architect runs complexity check
- 10am: architect reviews metrics
- 11am-2pm: architect creates refactoring plans
- 2pm: project_manager adds to ROADMAP

**Tuesday-Thursday**:
- code_developer executes refactoring tasks
- code_developer reports progress daily

**Friday**:
- 4pm: architect reviews completed refactoring
- 5pm: project_manager updates ROADMAP

---

### Key Commands

```bash
# Check complexity (architect)
./scripts/check_complexity.sh

# Find refactoring opportunities
radon cc coffee_maker/ -a -s | grep -E " [D-F] \("

# Run code_developer daemon
poetry run code-developer --auto-approve

# Check refactoring progress
poetry run project-manager /roadmap | grep REFACTOR

# Review completed work
pytest && radon cc coffee_maker/ -a
```

---

### File Locations

```
docs/architecture/refactoring/
├── templates/
│   └── REFACTOR_TEMPLATE.md          # Template for new plans
├── active/
│   └── REFACTOR_YYYY_MM_DD_name.md   # Active refactoring plans
├── completed/
│   └── REFACTOR_YYYY_MM_DD_name_COMPLETED.md  # Archived plans
├── ARCHITECT_WORKFLOW.md              # Detailed architect guide
├── CODE_DEVELOPER_WORKFLOW.md         # Detailed developer guide
├── MONITORING_GUIDE.md                # Metrics interpretation
├── REFACTORING_BEST_PRACTICES.md      # Patterns and examples
└── REFACTORING_WORKFLOW_INTEGRATION.md  # This document
```

---

## Related Documents

- [ARCHITECT_WORKFLOW.md](./ARCHITECT_WORKFLOW.md) - How architect creates plans
- [CODE_DEVELOPER_WORKFLOW.md](./CODE_DEVELOPER_WORKFLOW.md) - How code_developer executes
- [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) - Metrics and thresholds
- [REFACTORING_BEST_PRACTICES.md](./REFACTORING_BEST_PRACTICES.md) - Patterns and examples
- [US-044](../../roadmap/ROADMAP.md#us-044) - Original user story
- [CFR-005](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md) - Ownership includes maintenance
- [WORKFLOWS.md](../../WORKFLOWS.md) - All project workflows

---

**Last Updated**: 2025-10-21
**Version**: 1.0
**Status**: Production ✅
