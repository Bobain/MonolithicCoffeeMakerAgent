# Architect Daily Routine Guide (CFR-011)

**Last Updated**: 2025-10-19
**Status**: Active
**Related**: CFR-011, US-054

---

## Overview

This guide describes the architect agent's daily integration workflow for code-searcher findings and weekly codebase analysis, as required by CFR-011.

**Key Principle**: architect MUST integrate code-searcher findings daily and analyze the codebase weekly BEFORE creating new technical specifications.

---

## CFR-011 Requirements

### Daily Integration (Every Day)
1. **Read ALL code-searcher reports** in `docs/code-searcher/*.md`
2. **Extract action items** from each report
3. **Update tracking file** to mark reports as read

### Weekly Analysis (Every 7 Days)
1. **Analyze codebase** using radon, pytest, and manual review
2. **Generate analysis report** in `docs/architecture/CODEBASE_ANALYSIS_*.md`
3. **Update tracking file** to mark analysis complete

### Enforcement
- **Spec creation BLOCKED** if violations detected
- **Violations raised** as `CFR011ViolationError`
- **User notified** via notification system

---

## Daily Workflow

### Step 1: Check Compliance Status

```bash
$ poetry run architect cfr-011-status
```

**Output**:
```
=== CFR-011 Compliance Status

============================================================
 COMPLIANT - No violations detected

Last code-searcher read: 2025-10-18
Last codebase analysis: 2025-10-18
Next analysis due: 2025-10-25

Metrics:
  Reports read: 12
  Refactoring specs created: 4
  Specs updated: 6
```

### Step 2: Daily Integration (if needed)

If there are unread reports:

```bash
$ poetry run architect daily-integration
```

**What this does**:
1. Finds all unread code-searcher reports
2. Displays each report for review
3. Asks: "Have you read this report and extracted action items?"
4. Marks reports as read in tracking file

**Example Session**:
```
=== Found 2 unread code-searcher report(s):

  1. CODE_QUALITY_ANALYSIS_2025-10-17.md
  2. SECURITY_AUDIT_2025-10-18.md

=== Please read all reports now:

============================================================
Reading: CODE_QUALITY_ANALYSIS_2025-10-17.md
============================================================
[report content displayed]

============================================================

Have you read this report and extracted action items? [y/N]: y
 Marked CODE_QUALITY_ANALYSIS_2025-10-17.md as read

[... repeat for next report ...]

 Daily integration complete!
```

### Step 3: Extract Action Items

For each report, extract:
1. **Refactoring opportunities** (e.g., "Simplify X by reusing Y")
2. **Technical debt** (e.g., "Address TODO comments in Z")
3. **Security issues** (e.g., "Fix vulnerability in W")
4. **Spec updates needed** (e.g., "Update SPEC-009 to use pattern P")

Document action items in:
- Spec updates: Update existing specs in `docs/architecture/specs/`
- New specs: Create refactoring specs for major changes
- ADRs: Document architectural decisions

---

## Weekly Workflow

### Step 1: Check if Analysis Due

```bash
$ poetry run architect cfr-011-status
```

Look for:
```
   Weekly codebase analysis is OVERDUE
```

### Step 2: Run Codebase Analysis

```bash
$ poetry run architect analyze-codebase
```

**What this does**:
1. Runs radon complexity analysis
2. Detects large files (>500 LOC)
3. Runs pytest coverage analysis
4. Extracts TODO/FIXME comments
5. Generates synthetic report in `docs/architecture/CODEBASE_ANALYSIS_*.md`

**Example Output**:
```
=
 Starting weekly codebase analysis...

=== Analyzing codebase for:
  - Complexity metrics (radon --average)
  - Large files (>500 LOC)
  - Test coverage (pytest --cov)
  - TODO/FIXME comments

(This may take 5-10 minutes...)

=== Report saved: docs/architecture/CODEBASE_ANALYSIS_2025-10-19.md

 Codebase analysis complete!
   Next analysis due: 2025-10-26
```

### Step 3: Review Analysis Report

Open `docs/architecture/CODEBASE_ANALYSIS_*.md` and review:
1. **Complexity metrics**: Identify complex files for refactoring
2. **Large files**: Consider splitting files >500 LOC
3. **Test coverage**: Ensure coverage >80%
4. **TODO/FIXME**: Prioritize technical debt

### Step 4: Create Action Plan

Based on analysis, create:
1. **Refactoring specs** for complex files
2. **Spec updates** for existing features
3. **New priorities** in ROADMAP.md for critical issues

---

## Violation Scenarios

### Scenario 1: Unread Reports Block Spec Creation

**Violation**:
```
L CFR-011 violation detected!

Unread code-searcher reports: SECURITY_AUDIT_2025-10-18.md

Actions required:
  1. Run: architect daily-integration
  2. Run: architect analyze-codebase (if due)
```

**Resolution**:
```bash
$ poetry run architect daily-integration
# Read reports and extract action items
```

### Scenario 2: Overdue Analysis Blocks Spec Creation

**Violation**:
```
L CFR-011 violation detected!

Weekly codebase analysis overdue (last: 2025-10-10)

Actions required:
  1. Run: architect analyze-codebase
```

**Resolution**:
```bash
$ poetry run architect analyze-codebase
# Review report and create action plan
```

---

## Integration with Spec Creation

### Automatic Enforcement

When architect creates a spec, CFR-011 enforcement happens **automatically**:

```python
# In architect_agent.py

def _create_spec_for_priority(self, priority: Dict):
    # CFR-011: Enforce daily integration before creating specs
    from coffee_maker.autonomous.architect_daily_routine import (
        ArchitectDailyRoutine,
        CFR011ViolationError
    )

    try:
        routine = ArchitectDailyRoutine()
        routine.enforce_cfr_011()  # Raises CFR011ViolationError if violations
    except CFR011ViolationError as e:
        # Block spec creation - return early
        return

    # Continue with spec creation...
```

**Result**:
- Spec creation **BLOCKED** if violations exist
- User **notified** via notification system
- architect must complete daily integration before resuming

---

## Tracking File

**Location**: `data/architect_integration_status.json`

**Format**:
```json
{
  "last_code_searcher_read": "2025-10-19",
  "last_codebase_analysis": "2025-10-18",
  "reports_read": [
    "CODE_QUALITY_ANALYSIS_2025-10-17.md",
    "SECURITY_AUDIT_2025-10-18.md"
  ],
  "refactoring_specs_created": 4,
  "specs_updated": 6,
  "next_analysis_due": "2025-10-25"
}
```

**Fields**:
- `last_code_searcher_read`: Last date reports were read (YYYY-MM-DD)
- `last_codebase_analysis`: Last date codebase was analyzed (YYYY-MM-DD)
- `reports_read`: List of report filenames marked as read
- `refactoring_specs_created`: Count of refactoring specs created
- `specs_updated`: Count of specs updated with findings
- `next_analysis_due`: Next date when analysis is due (YYYY-MM-DD)

---

## Best Practices

### Daily Integration
1. **Do it early**: Check for reports first thing in the morning
2. **Extract thoroughly**: Don't just skim - identify concrete action items
3. **Document immediately**: Update specs while findings are fresh
4. **Track metrics**: Increment `refactoring_specs_created` and `specs_updated`

### Weekly Analysis
1. **Schedule it**: Pick a consistent day (e.g., Monday mornings)
2. **Review deeply**: Don't just run the command - analyze the results
3. **Create specs proactively**: Address issues before they become blockers
4. **Monitor trends**: Compare weekly reports to track improvements

### Spec Creation
1. **Check compliance first**: Run `architect cfr-011-status` before creating specs
2. **Integrate findings**: Use code-searcher insights to improve spec quality
3. **Avoid rework**: Don't create specs that ignore known refactoring opportunities
4. **Update metrics**: Increment counters when creating/updating specs

---

## Troubleshooting

### "I ran daily-integration but still getting violations"

Check:
1. Did you answer "y" to all reports?
2. Did you mark reports as read in the tracking file?
3. Is the tracking file in `data/architect_integration_status.json`?

### "Codebase analysis is taking too long"

- Normal duration: 5-10 minutes
- If >15 minutes: Check pytest timeout settings
- If stuck: Ctrl+C and retry with `--no-cov` flag

### "I want to skip a report"

- Not recommended - CFR-011 requires ALL reports to be read
- If you must skip: Answer "N" and it will remain unread
- You'll need to read it later before creating specs

---

## CLI Reference

### `architect daily-integration`

Guided workflow for reading code-searcher reports.

**Usage**:
```bash
$ poetry run architect daily-integration
```

**Flags**: None

**Output**: Interactive report review with confirmation prompts

---

### `architect analyze-codebase`

Perform weekly codebase analysis.

**Usage**:
```bash
$ poetry run architect analyze-codebase
```

**Flags**: None (prompts for confirmation if not due)

**Output**: Synthetic report saved to `docs/architecture/CODEBASE_ANALYSIS_*.md`

**Analysis Includes**:
- Radon complexity metrics (cyclomatic complexity average)
- Large file detection (>500 LOC)
- Test coverage analysis (pytest --cov)
- TODO/FIXME comment extraction

---

### `architect cfr-011-status`

Check CFR-011 compliance status.

**Usage**:
```bash
$ poetry run architect cfr-011-status
```

**Flags**: None

**Output**: Compliance status, metrics, and actions required

---

## Success Metrics

Track your CFR-011 compliance with these metrics:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Reports read** | 100% daily | `architect cfr-011-status` |
| **Analysis frequency** | Every 7 days | Check `next_analysis_due` |
| **Refactoring specs created** | 1-2 per week | Track `refactoring_specs_created` |
| **Specs updated** | 2-3 per week | Track `specs_updated` |
| **Violation rate** | 0% | Monitor notifications |

---

## Related Documentation

- [CFR-011 Definition](../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-011)
- [SPEC-054: Technical Specification](specs/SPEC-054-architect-code-searcher-daily-integration.md)
- [code-searcher Documentation](.claude/agents/code-searcher.md)
- [Architect Agent Implementation](../../coffee_maker/autonomous/agents/architect_agent.py)

---

**Remember**: CFR-011 is not optional. Daily integration and weekly analysis ensure that technical specifications are always informed by the latest codebase insights, preventing rework and improving overall code quality.
