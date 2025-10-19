# GUIDELINE-006: Architect Review Process

**Status**: Active

**Author**: code_developer (implementing US-049)

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-049 (ROADMAP), CFR-010 (Continuous Spec Improvement), ADR-003 (Simplification-First Approach)

---

## Purpose

This guideline defines the architect agent's continuous review process for maintaining and improving technical specifications over time. Through regular reviews (daily and weekly), architect ensures:

- **Complexity reduction**: Identify simplification opportunities across all specs
- **Component reuse**: Spot shared patterns and reusable infrastructure
- **Architectural consistency**: Maintain design coherence across priorities
- **Quality improvement**: Feed implementation lessons back into specs

## Scope

This guideline applies to:
- architect agent (primary responsibility)
- All technical specifications in `docs/architecture/specs/`
- ROADMAP.md monitoring
- Metrics tracking and reporting

## Review Types

### Daily Quick Review (5-10 minutes)

**Triggers**:
- ROADMAP.md modified since last review
- OR 24+ hours elapsed since last daily review

**Process**:
1. Open ROADMAP.md
2. Scan for new or changed priorities (last 24h)
3. Quick mental check:
   - Can this reuse existing components?
   - Similar to past specs?
   - Obvious simplification opportunities?
4. Add notes to weekly review backlog if needed
5. Mark daily review complete

**Example**:
```bash
# architect agent performs daily review
cd /path/to/MonolithicCoffeeMakerAgent

# 1. Check ROADMAP changes
git log --since="24 hours ago" -- docs/roadmap/ROADMAP.md

# 2. Scan for new priorities
cat docs/roadmap/ROADMAP.md | grep "📝 Planned" | head -5

# 3. Quick assessment (mental check)
# - PRIORITY 15: Needs spec... can reuse NotificationDB?
# - PRIORITY 16: Similar to PRIORITY 10... check for patterns

# 4. Add backlog notes (if needed)
echo "Review PRIORITY 15 for NotificationDB reuse" >> notes/weekly_backlog.md

# 5. Mark complete
# (ReviewTrigger.mark_review_completed("daily") called by daemon)
```

### Weekly Deep Review (1-2 hours)

**Triggers**:
- 7+ days elapsed since last weekly review

**Process**:
1. List all specs: `ls docs/architecture/specs/`
2. Read each spec (skim for architecture, components)
3. Analyze for patterns:
   - **Shared components** across specs
   - **Duplicate logic** that could be extracted
   - **Overly complex designs** that could be simplified
4. Record simplifications in metrics (if improvements made)
5. Record reuse opportunities
6. Update specs if improvements found
7. Generate weekly report
8. Mark weekly review complete

**Example**:
```python
# architect agent performs weekly review

from coffee_maker.autonomous.architect_metrics import ArchitectMetrics
from coffee_maker.autonomous.architect_report_generator import WeeklyReportGenerator
from pathlib import Path

# 1. Load metrics
metrics = ArchitectMetrics()

# 2. Review all specs (manual process - architect reads each spec)
specs = list(Path("docs/architecture/specs").glob("SPEC-*.md"))
print(f"Reviewing {len(specs)} specs...")

# For each spec, architect analyzes:
# - Can this be simplified?
# - Does it reuse existing components?
# - Are there shared patterns with other specs?

# 3. Record findings (example)
metrics.record_simplification(
    spec_id="SPEC-009",
    original_hours=80,
    simplified_hours=16,
    description="Reused DeveloperStatus, removed 6 modules"
)

metrics.record_reuse(
    spec_id="SPEC-010",
    reused_components=["NotificationDB", "DeveloperStatus"],
    description="Leveraged existing notification system"
)

# 4. Generate report
findings = {
    "specs_reviewed": [s.stem for s in specs],
    "simplifications_made": [
        {
            "spec_id": "SPEC-009",
            "title": "Enhanced Communication",
            "reduction_percent": 80.0,
            "original_hours": 80,
            "simplified_hours": 16,
            "effort_saved": 64.0,
            "description": "Reused DeveloperStatus infrastructure"
        }
    ],
    "reuse_opportunities": [
        {
            "spec_id": "SPEC-010",
            "components": ["NotificationDB", "DeveloperStatus"]
        }
    ],
    "recommendations": [
        "Create shared JSON file utility (used in 6 specs)",
        "Extract validation logic into reusable module",
        "Consider shared testing utilities for daemon"
    ]
}

report_gen = WeeklyReportGenerator(metrics)
report_path = report_gen.generate_report(findings)
print(f"Report generated: {report_path}")

# 5. Mark weekly review complete
# (ReviewTrigger.mark_review_completed("weekly") called by daemon)
```

## Metrics Tracked

### Simplification Metrics

For each spec simplification, record:
- **spec_id**: Spec identifier (e.g., "SPEC-009")
- **original_hours**: Original estimated effort
- **simplified_hours**: Simplified estimated effort
- **effort_saved**: Hours saved (original - simplified)
- **reduction_percent**: Percentage reduction
- **description**: Brief description of changes
- **date**: When simplification was identified

**Example**:
```python
metrics.record_simplification(
    spec_id="SPEC-009",
    original_hours=80.0,  # 2 weeks
    simplified_hours=16.0,  # 2 days
    description="Reused DeveloperStatus infrastructure instead of building new metrics system"
)
# Result: 64 hours saved (80% reduction)
```

### Reuse Metrics

For each component reuse opportunity, record:
- **spec_id**: Spec identifier
- **reused_components**: List of component names
- **count**: Number of components reused
- **description**: Brief description
- **date**: When reuse was identified

**Example**:
```python
metrics.record_reuse(
    spec_id="SPEC-010",
    reused_components=["NotificationDB", "DeveloperStatus", "AgentRegistry"],
    description="Leveraged existing infrastructure for user listener UI"
)
# Result: 3 components reused
```

### Summary Metrics

Cumulative metrics across all reviews:
- **total_simplifications**: Count of simplifications
- **total_effort_saved**: Total hours saved (cumulative)
- **avg_reduction_percent**: Average complexity reduction
- **total_reuse_opportunities**: Count of reuse instances
- **specs_reviewed**: Unique specs reviewed

## Weekly Report Format

Reports are generated in `docs/architecture/WEEKLY_SPEC_REVIEW_YYYY-MM-DD.md`:

```markdown
# Weekly Spec Review - 2025-10-19

## Summary

Reviewed 8 specs, identified 3 reuse opportunities, simplified 2 implementations.

## Metrics

- **Simplification Rate**: 65.5% average complexity reduction
- **Reuse Rate**: 12 components reused across specs
- **Effort Saved**: 76.5 hours (cumulative)
- **Specs Reviewed**: 15 total

## Improvements Made This Week

### SPEC-009: Enhanced Communication

**Reduction**: 80.0% (80h → 16h)

**Changes**: Reused DeveloperStatus infrastructure, removed 6 modules

**Impact**: Saved 64.0 hours implementation time

## Reuse Opportunities Identified

- **SPEC-011**: Reuses NotificationDB, AgentRegistry
- **SPEC-012**: Reuses DeveloperStatus, PromptLoader

## Recommendations

1. Create shared JSON file utility (used in 6 specs)
2. Extract validation logic into reusable module
3. Consider shared testing utilities for daemon tests

## Next Week Focus

- Review new priorities added to ROADMAP
- Continue identifying shared patterns
- Update older specs with new best practices
- Monitor implementation feedback for spec improvements

---

**Generated by**: architect agent (continuous improvement loop)
**Next Review**: 2025-10-26
```

## Automation

The review process is **semi-automated**:

### Automated (code_developer daemon)
- **Trigger detection**: Daemon checks if reviews are needed
- **Notification creation**: Alerts architect when review due
- **Metrics persistence**: JSON file storage
- **Report generation**: Markdown file creation

### Manual (architect agent)
- **Spec reading**: Architect reads and analyzes specs
- **Pattern identification**: Architect spots reuse opportunities
- **Simplification design**: Architect designs improvements
- **Spec updates**: Architect modifies specs if needed

## CFR-010 Compliance

This guideline enforces CFR-010 (Continuous Spec Improvement):

> **CFR-010**: architect MUST continuously review and improve all technical specifications on a regular basis (daily quick reviews, weekly deep reviews) to reduce implementation complexity, increase code reuse, and maintain architectural quality.

**Compliance Check**:
- ✅ Daily reviews triggered automatically (ROADMAP changes or 24h elapsed)
- ✅ Weekly reviews triggered automatically (7 days elapsed)
- ✅ Metrics tracked (simplification rate, reuse rate, effort saved)
- ✅ Reports generated (weekly improvement reports)
- ✅ architect notified (daemon creates notifications)

**Non-Compliance Consequences**:
- Complexity accumulates (each new spec designed in isolation)
- Missed reuse opportunities (shared patterns not identified)
- Architectural drift (patterns diverge over time)
- No feedback loop (lessons from implementation don't improve specs)

## Best Practices

### For architect Agent

1. **Be Proactive**: Don't wait for reviews - if you see a simplification opportunity during spec creation, apply it immediately
2. **Document Reasoning**: When simplifying, explain WHY in the spec (helps future reviews)
3. **Quantify Impact**: Always estimate effort saved (hours, percentage reduction)
4. **Cross-Reference**: Link related specs together (e.g., "See SPEC-009 for similar pattern")
5. **Update ADRs**: If simplification reveals architectural pattern, create ADR

### For code_developer

1. **Trust the Process**: Follow the simplified spec, even if it seems "too simple"
2. **Provide Feedback**: If spec was unclear or missing details, tell architect
3. **Report Complexity**: If implementation is harder than estimated, notify architect
4. **Suggest Improvements**: If you find a better approach during implementation, propose it

## Tools & Infrastructure

### Review Trigger System

**File**: `coffee_maker/autonomous/architect_review_triggers.py`

**Usage**:
```python
from coffee_maker.autonomous.architect_review_triggers import ReviewTrigger

trigger = ReviewTrigger()

# Check if reviews needed
if trigger.should_run_daily_review():
    # Perform daily review
    trigger.mark_review_completed("daily")

if trigger.should_run_weekly_review():
    # Perform weekly review
    trigger.mark_review_completed("weekly")
```

### Metrics Tracker

**File**: `coffee_maker/autonomous/architect_metrics.py`

**Usage**:
```python
from coffee_maker.autonomous.architect_metrics import ArchitectMetrics

metrics = ArchitectMetrics()

# Record simplification
metrics.record_simplification(
    spec_id="SPEC-009",
    original_hours=80.0,
    simplified_hours=16.0,
    description="Reused infrastructure"
)

# Record reuse
metrics.record_reuse(
    spec_id="SPEC-010",
    reused_components=["NotificationDB"],
    description="Leveraged existing system"
)

# Get summary
summary = metrics.get_summary()
print(f"Total effort saved: {summary['total_effort_saved']} hours")
```

### Report Generator

**File**: `coffee_maker/autonomous/architect_report_generator.py`

**Usage**:
```python
from coffee_maker.autonomous.architect_report_generator import WeeklyReportGenerator

generator = WeeklyReportGenerator(metrics)

findings = {
    "specs_reviewed": ["SPEC-009", "SPEC-010"],
    "simplifications_made": [...],
    "reuse_opportunities": [...],
    "recommendations": [...]
}

report_path = generator.generate_report(findings)
```

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-19 | Created GUIDELINE-006 | code_developer (US-049) |

---

## References

- [US-049: Architect Continuous Spec Improvement Loop](../../roadmap/ROADMAP.md#us-049-architect-continuous-spec-improvement-loop-cfr-010)
- [CFR-010: Continuous Spec Improvement](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-010-continuous-spec-improvement)
- [ADR-003: Simplification-First Architectural Approach](../decisions/ADR-003-simplification-first-approach.md)
- [SPEC-049: Architect Continuous Spec Improvement Loop](../specs/SPEC-049-architect-continuous-spec-improvement-loop.md)
