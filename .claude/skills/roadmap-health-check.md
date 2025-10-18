# Skill: ROADMAP Health Check

**Name**: `roadmap-health-check`
**Owner**: project_manager agent
**Purpose**: Rapid ROADMAP analysis to identify blockers, stale priorities, and health metrics
**Priority**: HIGH - Enables proactive project management

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ Daily standup generation (automatic)
- ✅ Weekly status reports
- ✅ When user asks "/roadmap status" or "/health"
- ✅ Before starting new sprint planning
- ✅ When code_developer reports being blocked

**Example Trigger**:
```python
# In project_manager agent
daily_report = self._generate_daily_standup()
# Uses roadmap-health-check skill
```

---

## Skill Execution Steps

### Step 1: Parse ROADMAP Structure

**Inputs Needed**:
- `$ROADMAP_PATH`: Path to ROADMAP.md (default: docs/roadmap/ROADMAP.md)
- `$CURRENT_DATE`: Today's date for staleness calculation

**Actions**:
1. Read ROADMAP.md file
2. Extract all priorities with:
   - Priority number (e.g., "PRIORITY 10")
   - Status (📝 Planned, 🔄 In Progress, ✅ Complete, ⏸️ Blocked, etc.)
   - Title
   - Description
   - Dependencies (if mentioned)
   - Estimated effort
   - Last updated date (from git blame)

**Output**: Structured priority list

```python
priorities = [
    {
        "number": "10",
        "status": "🔄 In Progress",
        "title": "User Authentication",
        "description": "...",
        "dependencies": ["PRIORITY 9"],
        "estimated_effort": "2 days",
        "last_updated": "2025-10-15"
    }
]
```

### Step 2: Calculate Health Metrics

**Metrics to Calculate**:

1. **Velocity** - Priorities completed per week
   ```
   Recent completions: Last 7 days, last 30 days
   Average velocity: Completions / weeks
   ```

2. **Blockers** - Priorities marked as ⏸️ Blocked or stuck
   ```
   Total blocked: Count of ⏸️
   Blocked duration: Days since blocked
   ```

3. **Stale Priorities** - In Progress but no updates >7 days
   ```
   Stale: In Progress + no updates >7 days
   ```

4. **Dependency Issues** - Priorities waiting on incomplete dependencies
   ```
   For each planned priority:
       If depends on X and X not complete:
           Dependency blocker
   ```

5. **Backlog Health** - Ratio of planned vs in-progress vs complete
   ```
   Planned: Count of 📝
   In Progress: Count of 🔄
   Complete: Count of ✅
   Backlog ratio: Planned / Total
   ```

**Output**:
```python
health_metrics = {
    "velocity": {
        "last_7_days": 2,
        "last_30_days": 8,
        "average_per_week": 2.0
    },
    "blockers": {
        "count": 3,
        "longest_blocked_days": 12
    },
    "stale_priorities": {
        "count": 2,
        "average_stale_days": 9
    },
    "dependencies": {
        "blocked_by_deps": 5
    },
    "backlog": {
        "planned": 15,
        "in_progress": 3,
        "complete": 42,
        "backlog_ratio": 0.25
    }
}
```

### Step 3: Identify Issues and Risks

**Issue Detection Rules**:

**1. Critical Blockers** (Severity: CRITICAL)
- Priority marked ⏸️ Blocked for >7 days
- Action: Escalate to user, investigate blocker

**2. Stale Work** (Severity: HIGH)
- Priority 🔄 In Progress but no updates >7 days
- Action: Check with code_developer, may need help

**3. Dependency Chain Blocked** (Severity: HIGH)
- Planned priority waiting on blocked dependency
- Action: Consider re-prioritization

**4. Low Velocity** (Severity: MEDIUM)
- Velocity <50% of historical average
- Action: Identify bottlenecks

**5. Backlog Bloat** (Severity: LOW)
- Backlog ratio >0.5 (too many planned items)
- Action: Consider trimming backlog

**Output**:
```python
issues = [
    {
        "severity": "CRITICAL",
        "type": "critical_blocker",
        "priority": "PRIORITY 8",
        "description": "Blocked for 12 days - dependency on external API approval",
        "recommendation": "Escalate to user, find workaround"
    },
    {
        "severity": "HIGH",
        "type": "stale_work",
        "priority": "PRIORITY 10",
        "description": "In Progress for 9 days with no updates",
        "recommendation": "Check code_developer status, may need assistance"
    }
]
```

### Step 4: Generate Health Score

**Scoring Algorithm**:

```python
def calculate_health_score(metrics, issues):
    """Calculate overall ROADMAP health (0-100)."""
    base_score = 100

    # Deductions
    for issue in issues:
        if issue["severity"] == "CRITICAL":
            base_score -= 20
        elif issue["severity"] == "HIGH":
            base_score -= 10
        elif issue["severity"] == "MEDIUM":
            base_score -= 5
        elif issue["severity"] == "LOW":
            base_score -= 2

    # Bonuses for good health
    if metrics["velocity"]["last_7_days"] > 2:
        base_score += 5  # Good velocity

    if metrics["blockers"]["count"] == 0:
        base_score += 10  # No blockers

    if metrics["stale_priorities"]["count"] == 0:
        base_score += 5  # No stale work

    return max(0, min(100, base_score))  # Clamp to 0-100
```

**Score Interpretation**:
- 90-100: 🟢 Excellent - Project on track
- 70-89: 🟡 Good - Minor issues, manageable
- 50-69: 🟠 Fair - Needs attention
- 0-49: 🔴 Poor - Critical issues, urgent action needed

### Step 5: Generate Recommendations

**Recommendation Engine**:

For each issue, generate specific, actionable recommendations:

**Example Recommendations**:

```markdown
## Recommendations

### CRITICAL Issues

1. **PRIORITY 8: Blocked for 12 days**
   - **Action**: Escalate to user immediately
   - **Options**:
     a) Get external API approval (best)
     b) Implement with mock API (workaround)
     c) Defer PRIORITY 8, work on PRIORITY 11 instead
   - **Timeline**: Resolve within 48 hours to avoid further delays

### HIGH Issues

2. **PRIORITY 10: Stale for 9 days**
   - **Action**: Check code_developer status
   - **Diagnostic Questions**:
     - Is code_developer stuck on tests?
     - Is spec unclear?
     - Are dependencies missing?
   - **Timeline**: Investigate within 24 hours

### Optimization Opportunities

3. **Backlog pruning**
   - **Action**: Review 15 planned priorities
   - **Suggestion**: Move low-priority items to "Future Considerations"
   - **Benefit**: Better focus on high-value work
```

### Step 6: Generate Report

**Report Format**:

```markdown
# ROADMAP Health Check Report
**Generated**: $CURRENT_DATE
**Health Score**: X/100 🟢

## Executive Summary
- Velocity: 2 priorities/week (on track)
- Blockers: 1 CRITICAL (needs attention)
- Stale work: 0 (excellent)
- Overall health: GOOD

## Metrics

### Velocity
- Last 7 days: 2 priorities ✅
- Last 30 days: 8 priorities ✅
- Average: 2.0 per week
- Trend: Stable

### Current Status
- 📝 Planned: 15 priorities
- 🔄 In Progress: 3 priorities
- ✅ Complete: 42 priorities
- ⏸️ Blocked: 1 priority
- Backlog ratio: 25% (healthy)

### Issues Found: 2

#### CRITICAL (1)
1. **PRIORITY 8: External API Integration** - Blocked 12 days
   - Blocker: Waiting on external API approval
   - Impact: Blocking PRIORITY 9, 11
   - Recommendation: Escalate to user, consider workaround

#### HIGH (1)
2. **PRIORITY 10: User Authentication** - Stale 9 days
   - Status: In Progress, no updates
   - Impact: May delay other priorities
   - Recommendation: Check code_developer status

## Recommendations

### Immediate Actions (Next 24-48 hours)
1. Escalate PRIORITY 8 blocker to user
2. Check code_developer status on PRIORITY 10
3. Consider starting PRIORITY 11 while waiting for PRIORITY 8

### This Week
1. Review backlog, defer low-priority items
2. Monitor velocity, ensure 2+ completions/week
3. Weekly check-in with code_developer

### Next Sprint
1. Plan for PRIORITY 12-15
2. Review and update stale technical specs
3. Consider adding buffer time for blockers

## Risk Analysis

### High-Risk Priorities
- PRIORITY 8: High dependency risk (external blocker)
- PRIORITY 10: Medium risk (stale, may need help)

### Mitigation Strategies
- PRIORITY 8: Have workaround ready (mock API)
- PRIORITY 10: Architect review, additional support if needed

## Next Health Check
- Scheduled: $NEXT_DATE (in 7 days)
- Focus areas: Resolve blockers, maintain velocity
```

---

## Integration with project_manager Agent

### Daily Standup Generation

```python
# coffee_maker/autonomous/agents/project_manager_agent.py

def _generate_daily_standup(self) -> str:
    """Generate daily standup using roadmap-health-check skill."""
    from coffee_maker.autonomous.skill_loader import load_skill, SkillNames
    from datetime import datetime

    skill = load_skill(SkillNames.ROADMAP_HEALTH_CHECK, {
        "ROADMAP_PATH": "docs/roadmap/ROADMAP.md",
        "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d"),
    })

    # Execute with LLM
    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
    claude = ClaudeCLIInterface()
    result = claude.execute_prompt(skill)

    health_report = result.content if result and result.success else "Health check failed"

    # Save report
    report_path = Path(f"data/reports/roadmap_health_{datetime.now().strftime('%Y%m%d')}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(health_report, encoding="utf-8")

    # Send summary to user (if critical issues found)
    if "CRITICAL" in health_report:
        self._notify_user_critical_issues(health_report)

    return health_report
```

### Weekly Status Report

```python
def _generate_weekly_status_report(self) -> str:
    """Generate weekly status report."""
    # Use roadmap-health-check skill with extended analysis
    health_report = self._generate_daily_standup()

    # Add GitHub stats
    github_stats = self._get_github_stats()

    # Add code_developer progress
    developer_progress = self._get_developer_progress()

    # Combine into comprehensive weekly report
    weekly_report = f"""# Weekly Status Report

## ROADMAP Health
{health_report}

## GitHub Activity
{github_stats}

## Code Developer Progress
{developer_progress}
"""

    return weekly_report
```

---

## Skill Checklist (project_manager Must Complete)

Before generating reports:

- [ ] ✅ Load roadmap-health-check skill with current date
- [ ] ✅ Execute skill to get health analysis
- [ ] ✅ Review health score and issues
- [ ] ✅ If CRITICAL issues: Notify user immediately
- [ ] ✅ If HIGH issues: Add to follow-up queue
- [ ] ✅ Save report to data/reports/
- [ ] ✅ Update project dashboard with health metrics
- [ ] ✅ Track health trends over time
- [ ] ✅ Use recommendations to guide daily work

**Failure to check ROADMAP health = Missed blockers, delayed projects**

---

## Success Metrics

**Time Savings**:
- **Before**: 20-30 minutes manual ROADMAP analysis
- **After**: 2-3 minutes with skill-generated report
- **Savings**: 17-27 minutes per health check

**Quality Improvements**:
- **Faster blocker detection**: Identify blockers within 24 hours
- **Better prioritization**: Data-driven decisions
- **Proactive management**: Address issues before they escalate

**Measurement**:
- Track time from "blocker appears" to "blocker detected"
- Track time from "issue detected" to "issue resolved"
- Track project health trend (improving vs declining)

---

## Related Skills

- **proactive-refactoring-analysis**: Architect identifies technical debt
- **test-failure-analysis**: code_developer debugs test issues
- **architecture-reuse-check**: Architect ensures quality specs

---

**Remember**: Healthy ROADMAP = Predictable delivery = Happy users! 📊

**project_manager's Mantra**: "Daily health check = No surprises!"
