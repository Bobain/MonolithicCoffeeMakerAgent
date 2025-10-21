# GUIDELINE-003: Specification Review Process

**Author**: architect
**Status**: Active
**CFR**: CFR-010 - Continuous Spec Improvement
**Related**: US-049 - Continuous Spec Improvement Loop

---

## Overview

This guideline provides the architect with structured checklists for continuous review and improvement of technical specifications. The goal is to keep specs current, simple, and reusable.

**Key Principle**: Specs are living documents that evolve based on implementation learnings and architectural improvements, not one-and-done artifacts.

---

## Daily Spec Review Checklist (5-10 minutes)

**When**: Every morning before starting work
**Why**: Catch new priorities early, identify spec needs proactively

### Process

- [ ] Read full ROADMAP.md (focus on new/changed priorities since yesterday)
- [ ] Identify priorities missing technical specs
- [ ] Note dependencies between upcoming features
- [ ] Create specs for next 2-3 priorities (proactive planning)
- [ ] Update spec coverage status in metrics

### Questions to Ask

- Are there new priorities since yesterday?
- Do any planned priorities lack specs?
- Are there dependencies I should consider in design?
- Can I consolidate any upcoming features into shared specs?
- Are there related priorities that should reference each other?

### Output

- List of 2-3 priorities to create specs for this week
- Notes on any dependencies or consolidation opportunities
- Updated spec metrics with coverage status

---

## Weekly Deep Spec Review (1 hour)

**When**: Every Friday afternoon
**Why**: Identify improvement patterns, update based on implementation learnings, plan next week

### Process

- [ ] Re-read ALL existing specs (skim for big picture patterns)
- [ ] For each spec, ask simplification questions (see below)
- [ ] Update specs with improvements
- [ ] Identify and document reuse opportunities
- [ ] Generate weekly metrics report
- [ ] Plan next week's spec creation priorities

### Simplification Questions

For each spec, ask:

1. **Complexity**: Can this be simplified further?
   - Remove unnecessary features
   - Consolidate duplicate patterns
   - Break oversized specs into smaller pieces

2. **Reuse**: Does it share patterns with other specs?
   - Common error handling patterns
   - Shared data structures
   - Repeated workflows
   - CLI command patterns

3. **Reality**: Has implementation revealed issues?
   - Estimates vs actual time spent
   - Unexpected challenges
   - Design assumptions that proved wrong
   - Missing edge cases

4. **Consolidation**: Should this merge with another spec?
   - Related features that should be reviewed together
   - Shared dependencies
   - Common business domain

### Output

- Updated specs with simplifications
- List of identified reuse opportunities
- Weekly metrics report (generated automatically)
- Plan for consolidation if needed

---

## Post-Implementation Review (15 minutes)

**When**: After code_developer completes a priority
**Why**: Learn from implementation, improve future specs, update metrics

### Process

- [ ] Read code_developer's implementation (code review)
- [ ] Compare implementation to technical spec
- [ ] Note what was built differently (and why)
- [ ] Ask discovery questions (see below)
- [ ] Update spec with "Actual Implementation" section
- [ ] Record metrics (actual vs estimated time)

### Discovery Questions

When implementation diverges from spec:

1. **Was the spec unclear?**
   - Missing details?
   - Ambiguous requirements?
   - Poor examples?

2. **Was the spec too complex?**
   - Over-engineered?
   - Unnecessary features?
   - Predicted problems that didn't occur?

3. **Were there unexpected challenges?**
   - Integration issues not anticipated?
   - Performance problems?
   - Edge cases discovered during coding?

4. **What worked well?**
   - Did the architecture approach work?
   - Were the estimates accurate?
   - Did code reuse happen as expected?

### Update Spec

Add new section to spec:

```markdown
## Actual Implementation Notes

**Date**: [Implementation completion date]

### What Was Built
- [Summary of what code_developer actually built]

### Divergences from Spec
- [What was different from the spec and why]

### Lessons Learned
- [What we learned for future specs]

### Metrics
- Estimated effort: X days
- Actual effort: Y days
- Accuracy: Z%
```

---

## Metrics Tracking

### Key Metrics

Track the following for each spec review cycle:

1. **Complexity Reduction**
   - Lines of documentation removed
   - Features removed or simplified
   - Consolidations made

2. **Reuse Opportunities**
   - Shared patterns identified
   - Cross-spec dependencies noted
   - Potential shared components suggested

3. **Time Estimation Accuracy**
   - Compare estimated days to actual implementation days
   - Calculate percentage accuracy (actual/estimated * 100)
   - Track trends over time

4. **Spec Coverage**
   - Number of specs created
   - Percentage of priorities with specs
   - Distribution by complexity

### Recording Metrics

Metrics are recorded in `data/spec_metrics.json`:

```json
{
  "specs": {
    "SPEC-049": {
      "created": "2025-10-16",
      "complexity_score": 200,
      "estimated_days": 2,
      "actual_days": 1.5,
      "updates": [
        {
          "date": "2025-10-17",
          "changes": "Simplified git log parsing",
          "complexity_reduction": 50
        }
      ]
    }
  },
  "weekly_summaries": [
    {
      "week_start": "2025-10-14",
      "specs_created": 3,
      "specs_updated": 2,
      "total_complexity_reduction": 150,
      "reuse_opportunities": [
        "DailyReportGenerator pattern reused across specs"
      ]
    }
  ]
}
```

---

## Weekly Report Format

Each Friday, generate a report showing:

```markdown
# Weekly Spec Improvement Report

Week of: 2025-10-14 to 2025-10-20

## Summary
- Specs Created: 3
- Specs Updated: 2
- Complexity Reduced: 150 lines
- Reuse Opportunities: 2

## Specs Created This Week
1. SPEC-047: Architect-Only Spec Creation (2 days, 300 lines)
2. SPEC-048: Silent Background Agents (4-6 hours, 100 lines)
3. SPEC-049: Continuous Spec Improvement (1-2 days, 250 lines)

## Specs Improved This Week
1. SPEC-009: Enhanced Communication
   - Simplified git parsing (removed AI summaries)
   - Reduced from 250 → 200 lines (-50 lines)
   - Estimated 2 days → Actual 1.5 days (75% accurate)

## Complexity Reduction
- Total lines reduced: 150
- Average reduction per update: 30%
- Trend: Improving (vs last week: 100 lines)

## Reuse Opportunities Identified
1. DailyReportGenerator pattern
   - Used in SPEC-009
   - Could be reused in SPEC-010, SPEC-011
   - Suggests creating shared reporting component

## Next Week Goals
- Create specs for PRIORITY 11, 12, 13
- Review all specs for consolidation opportunities
- Target 20% complexity reduction across board
```

---

## Integration with Tools

### CLI Commands

Use the following commands to support your workflow:

```bash
# Show spec metrics and trends
project-manager spec-metrics

# Show which specs need review
project-manager spec-needs-review

# Compare spec to actual implementation
project-manager spec-diff "PRIORITY 9"

# Show spec review status
project-manager spec-status
```

### Git Integration

Track spec changes with git:

```bash
# See what changed in a spec
git diff docs/architecture/specs/SPEC-009-*.md

# See all spec changes this week
git log --since="7 days ago" -- docs/architecture/specs/

# See spec creation history
git log --pretty=format:"%h %s" -- docs/architecture/specs/ | head -20
```

---

## Best Practices

### Do's

- ✅ Keep daily reviews brief (5-10 minutes)
- ✅ Keep weekly reviews focused (1 hour, Friday afternoon)
- ✅ Review immediately after implementation completes
- ✅ Ask discovery questions when implementation diverges
- ✅ Share learnings with team (include in weekly report)
- ✅ Use metrics to measure improvement over time
- ✅ Be proactive creating specs for upcoming priorities

### Don'ts

- ❌ Skip reviews ("too busy")
- ❌ Review specs only when problems occur
- ❌ Wait weeks between reviews (information is stale)
- ❌ Blame code_developer if implementation diverges
- ❌ Dismiss reuse opportunities ("just do it manually")
- ❌ Ignore estimation accuracy trends
- ❌ Create overly complex specs anticipating unknown problems

---

## Example Workflow: One Week

**Monday 9am**: Daily Review
- Read ROADMAP
- Identify 2 priorities needing specs
- Create SPEC-050 (1 hour)
- Update metrics

**Tuesday-Thursday**: Business as usual
- Respond to code_developer questions
- Review PRs
- Design new features

**Friday 4pm**: Weekly Review (1 hour)
- Re-read all 8 existing specs
- Simplify SPEC-045 (removed AI analysis, kept templates)
- Identify reuse: DailyReportGenerator used in 3 specs
- Create SPEC-051 (1 hour)
- Generate weekly report

**Next Monday**: Post-Implementation Review
- code_developer completed SPEC-049 (1.5 days vs 2 estimated)
- Add "Actual Implementation" notes to SPEC-049
- Update metrics (accuracy: 75%)

---

## Measuring Success

### Goals

1. **Sustainability**: Reviews happen consistently (5+ per month)
2. **Impact**: Specs get simpler (complexity reduction > 10% per month)
3. **Reuse**: Patterns identified (2+ per week)
4. **Accuracy**: Estimation improves (trend toward 90%+)

### Metrics

- Average daily review time: < 10 minutes
- Average weekly review time: < 1 hour
- Average post-implementation review: < 15 minutes
- Specs created per month: 5-8
- Complexity reduction per month: 100+ lines
- Reuse opportunities identified: 8+ per month

---

## Getting Help

If reviews feel overwhelming:

1. **Too many specs to review?**
   - Focus on active specs (from past 2-3 months)
   - Use git to skip old, archived specs

2. **Too many reuse opportunities?**
   - Track as backlog for future consolidation
   - Prioritize by impact (affects most specs)

3. **Estimation accuracy low?**
   - Don't blame code_developer
   - Ask: Is spec too vague? Too complex? Missing details?
   - Improve spec quality, not the blame

4. **Metrics overwhelming?**
   - Start with just complexity reduction
   - Add other metrics gradually
   - Focus on trends, not absolute numbers

---

## Related Guidelines

- GUIDELINE-002: CLI Command Pattern (for spec-related commands)
- GUIDELINE-001: Error Handling (for spec_metrics.py)

## Related CFRs

- CFR-010: Continuous Spec Improvement (this is the implementation)
- CFR-003: Simplification ADR Pattern (use simplification questions)

---

**Status**: Active (2025-10-17)
**Last Review**: 2025-10-17
**Next Review**: 2025-10-24
