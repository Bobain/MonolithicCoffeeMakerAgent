# Skill: Pull Request Monitoring & Analysis

**Name**: `pr-monitoring-analysis`
**Owner**: project_manager
**Purpose**: Monitor GitHub PRs, analyze status, detect blockers, and provide actionable insights
**Priority**: HIGH - Reduces PR monitoring from 15-20 minutes to 3-5 minutes

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ Daily standup generation
- ✅ Weekly status reports
- ✅ When user asks "what's the status of PR #X?"
- ✅ When user asks "are there any blocked PRs?"
- ✅ Automated hourly PR health checks (during work hours)

**Example Triggers**:
```python
# project_manager: Daily standup
daily_report = self._generate_daily_standup()
# Uses pr-monitoring-analysis skill

# project_manager: User query
if user_request == "PR status":
    pr_analysis = self._analyze_prs()
```

---

## Skill Execution Steps

### Step 1: Fetch All Open PRs

**Inputs Needed**:
- `$REPO_NAME`: Repository name (e.g., "user/MonolithicCoffeeMakerAgent")
- `$CURRENT_DATE`: Today's date for staleness calculation

**Actions**:

**1. Fetch PRs using gh CLI**:
```bash
# Get all open PRs
gh pr list --state open --json number,title,author,createdAt,updatedAt,isDraft,labels,reviews,statusCheckRollup,mergeable

# Example output:
[
  {
    "number": 42,
    "title": "Implement PRIORITY 10 - User Recipe Management",
    "author": {"login": "code_developer"},
    "createdAt": "2025-10-18T10:00:00Z",
    "updatedAt": "2025-10-18T14:30:00Z",
    "isDraft": false,
    "labels": ["feature", "priority-10"],
    "reviews": [
      {"state": "APPROVED", "author": {"login": "reviewer1"}},
      {"state": "CHANGES_REQUESTED", "author": {"login": "reviewer2"}}
    ],
    "statusCheckRollup": [
      {"context": "ci/tests", "state": "SUCCESS"},
      {"context": "ci/lint", "state": "FAILURE"}
    ],
    "mergeable": "CONFLICTING"
  }
]
```

**2. Parse PR data**:
```python
prs = [
    {
        "number": 42,
        "title": "Implement PRIORITY 10 - User Recipe Management",
        "author": "code_developer",
        "created_at": datetime.fromisoformat("2025-10-18T10:00:00Z"),
        "updated_at": datetime.fromisoformat("2025-10-18T14:30:00Z"),
        "is_draft": False,
        "labels": ["feature", "priority-10"],
        "reviews": [
            {"state": "APPROVED", "author": "reviewer1"},
            {"state": "CHANGES_REQUESTED", "author": "reviewer2"}
        ],
        "status_checks": [
            {"context": "ci/tests", "state": "SUCCESS"},
            {"context": "ci/lint", "state": "FAILURE"}
        ],
        "mergeable": "CONFLICTING"
    }
]
```

**Output**: List of open PRs with metadata

### Step 2: Categorize PRs by Status

**PR Status Categories**:

**1. Ready to Merge** ✅
- All status checks passed
- At least one approval
- No requested changes
- No merge conflicts
- Not a draft

**2. Waiting for Review** ⏳
- No reviews yet OR only comment reviews
- Status checks passing (or no checks)
- No merge conflicts

**3. Changes Requested** 🔴
- At least one reviewer requested changes
- Needs code_developer to address feedback

**4. Failing Checks** ❌
- CI/tests failing
- Linting/formatting failing
- Security checks failing

**5. Merge Conflicts** ⚠️
- Mergeable state is "CONFLICTING"
- Needs rebase/merge from base branch

**6. Stale** 🕐
- No updates in >7 days
- May need reminder or closure

**7. Draft** 📝
- Marked as draft (WIP)
- Not ready for review

**Categorization Logic**:
```python
def categorize_pr(pr):
    """Categorize PR by status."""

    # Draft
    if pr["is_draft"]:
        return "draft"

    # Stale
    days_since_update = (datetime.now() - pr["updated_at"]).days
    if days_since_update > 7:
        return "stale"

    # Merge Conflicts
    if pr["mergeable"] == "CONFLICTING":
        return "merge_conflicts"

    # Failing Checks
    if any(check["state"] == "FAILURE" for check in pr["status_checks"]):
        return "failing_checks"

    # Changes Requested
    if any(review["state"] == "CHANGES_REQUESTED" for review in pr["reviews"]):
        return "changes_requested"

    # Ready to Merge
    approved = any(review["state"] == "APPROVED" for review in pr["reviews"])
    checks_pass = all(check["state"] == "SUCCESS" for check in pr["status_checks"]) or not pr["status_checks"]
    no_conflicts = pr["mergeable"] != "CONFLICTING"

    if approved and checks_pass and no_conflicts:
        return "ready_to_merge"

    # Waiting for Review
    return "waiting_for_review"
```

**Output**: Categorized PRs
```python
categorized_prs = {
    "ready_to_merge": [pr_42],
    "waiting_for_review": [pr_43, pr_44],
    "changes_requested": [pr_45],
    "failing_checks": [pr_46],
    "merge_conflicts": [pr_47],
    "stale": [pr_48],
    "draft": [pr_49]
}
```

### Step 3: Analyze Blockers and Issues

**Issue Detection Rules**:

**1. Critical Blockers** (Severity: CRITICAL)
- PR with failing checks for >24 hours
- PR with merge conflicts for >3 days
- PR with changes requested for >5 days (no response)

**2. High Priority** (Severity: HIGH)
- PR ready to merge but not merged for >2 days
- PR waiting for review for >3 days

**3. Medium Priority** (Severity: MEDIUM)
- PR stale for >7 days (may need closure)
- PR with mixed reviews (some approve, some request changes)

**4. Low Priority** (Severity: LOW)
- Draft PR for >14 days (may be abandoned)

**Issue Detection**:
```python
def detect_issues(categorized_prs, current_date):
    """Detect blockers and issues."""
    issues = []

    # Ready to merge but not merged for >2 days
    for pr in categorized_prs["ready_to_merge"]:
        days_ready = (current_date - pr["updated_at"]).days
        if days_ready > 2:
            issues.append({
                "severity": "HIGH",
                "pr_number": pr["number"],
                "type": "ready_but_not_merged",
                "description": f"PR #{pr['number']} ready to merge for {days_ready} days",
                "recommendation": "Merge immediately or investigate why delayed"
            })

    # Failing checks for >24 hours
    for pr in categorized_prs["failing_checks"]:
        hours_failing = (current_date - pr["updated_at"]).total_seconds() / 3600
        if hours_failing > 24:
            issues.append({
                "severity": "CRITICAL",
                "pr_number": pr["number"],
                "type": "failing_checks_too_long",
                "description": f"PR #{pr['number']} has failing checks for {int(hours_failing)} hours",
                "recommendation": "Fix failing checks immediately or close PR"
            })

    # ... more detection rules ...

    return issues
```

**Output**: List of detected issues

### Step 4: Calculate PR Health Score

**Scoring Algorithm**:

```python
def calculate_pr_health_score(categorized_prs, issues):
    """Calculate overall PR health (0-100)."""
    base_score = 100

    # Count PRs in each category
    total_prs = sum(len(prs) for prs in categorized_prs.values())

    if total_prs == 0:
        return 100  # No PRs = perfect health

    # Deductions based on PR status
    ready_ratio = len(categorized_prs["ready_to_merge"]) / total_prs
    base_score -= (1 - ready_ratio) * 20  # Penalty if few PRs ready

    failing_ratio = len(categorized_prs["failing_checks"]) / total_prs
    base_score -= failing_ratio * 30  # Heavy penalty for failing checks

    conflicts_ratio = len(categorized_prs["merge_conflicts"]) / total_prs
    base_score -= conflicts_ratio * 20  # Penalty for conflicts

    stale_ratio = len(categorized_prs["stale"]) / total_prs
    base_score -= stale_ratio * 15  # Penalty for stale PRs

    # Deductions for issues
    for issue in issues:
        if issue["severity"] == "CRITICAL":
            base_score -= 15
        elif issue["severity"] == "HIGH":
            base_score -= 10
        elif issue["severity"] == "MEDIUM":
            base_score -= 5
        elif issue["severity"] == "LOW":
            base_score -= 2

    return max(0, min(100, base_score))  # Clamp to 0-100
```

**Score Interpretation**:
- 90-100: 🟢 Excellent - PRs healthy, merging regularly
- 70-89: 🟡 Good - Minor issues, mostly on track
- 50-69: 🟠 Fair - Needs attention, some blockers
- 0-49: 🔴 Poor - Critical issues, urgent action needed

### Step 5: Generate Recommendations

**Recommendation Engine**:

```python
def generate_recommendations(categorized_prs, issues):
    """Generate actionable recommendations."""
    recommendations = []

    # Ready to merge PRs
    if categorized_prs["ready_to_merge"]:
        recommendations.append({
            "priority": "HIGH",
            "action": "Merge ready PRs",
            "details": f"{len(categorized_prs['ready_to_merge'])} PR(s) ready to merge",
            "prs": [pr["number"] for pr in categorized_prs["ready_to_merge"]],
            "timeline": "Next 24 hours"
        })

    # Failing checks
    if categorized_prs["failing_checks"]:
        recommendations.append({
            "priority": "CRITICAL",
            "action": "Fix failing CI checks",
            "details": f"{len(categorized_prs['failing_checks'])} PR(s) with failing checks",
            "prs": [pr["number"] for pr in categorized_prs["failing_checks"]],
            "timeline": "Immediate"
        })

    # Merge conflicts
    if categorized_prs["merge_conflicts"]:
        recommendations.append({
            "priority": "HIGH",
            "action": "Resolve merge conflicts",
            "details": f"{len(categorized_prs['merge_conflicts'])} PR(s) with conflicts",
            "prs": [pr["number"] for pr in categorized_prs["merge_conflicts"]],
            "timeline": "Next 48 hours"
        })

    # Waiting for review
    if len(categorized_prs["waiting_for_review"]) > 3:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Review pending PRs",
            "details": f"{len(categorized_prs['waiting_for_review'])} PR(s) waiting for review",
            "prs": [pr["number"] for pr in categorized_prs["waiting_for_review"]],
            "timeline": "This week"
        })

    # Stale PRs
    if categorized_prs["stale"]:
        recommendations.append({
            "priority": "LOW",
            "action": "Close or revive stale PRs",
            "details": f"{len(categorized_prs['stale'])} stale PR(s) (>7 days no update)",
            "prs": [pr["number"] for pr in categorized_prs["stale"]],
            "timeline": "This sprint"
        })

    return sorted(recommendations, key=lambda r: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[r["priority"]])
```

### Step 6: Generate PR Analysis Report

**Report Format**:

```markdown
# Pull Request Monitoring & Analysis Report

**Generated**: $CURRENT_DATE
**Repository**: $REPO_NAME
**Health Score**: X/100 🟢

---

## Executive Summary

- Total Open PRs: 8
- Ready to Merge: 1 ✅
- Waiting for Review: 2 ⏳
- Failing Checks: 1 ❌
- Merge Conflicts: 1 ⚠️
- Stale: 2 🕐
- Draft: 1 📝

**Overall Health**: GOOD 🟡

---

## PRs by Category

### Ready to Merge ✅ (1 PR)

**HIGH PRIORITY**: These PRs should be merged ASAP!

1. **PR #42**: Implement PRIORITY 10 - User Recipe Management
   - Author: code_developer
   - Created: 2 days ago
   - Status checks: ✅ All passed
   - Reviews: ✅ Approved by reviewer1
   - Mergeable: ✅ No conflicts
   - **Action**: Merge immediately

### Waiting for Review ⏳ (2 PRs)

2. **PR #43**: Add recipe editing feature
   - Author: code_developer
   - Created: 1 day ago
   - Status checks: ✅ All passed
   - Reviews: 0 reviews
   - **Action**: Assign reviewer

3. **PR #44**: Fix recipe validation bug
   - Author: code_developer
   - Created: 3 hours ago
   - Status checks: ✅ All passed
   - Reviews: 0 reviews
   - **Action**: Request review from team

### Failing Checks ❌ (1 PR)

**CRITICAL**: These PRs need immediate attention!

4. **PR #46**: Refactor recipe storage
   - Author: code_developer
   - Created: 2 days ago
   - Status checks:
     - ❌ ci/tests - Test suite failing (3 tests)
     - ✅ ci/lint - Passed
   - **Action**: Fix failing tests immediately

### Merge Conflicts ⚠️ (1 PR)

5. **PR #47**: Update recipe UI
   - Author: code_developer
   - Created: 4 days ago
   - Mergeable: ❌ Has conflicts with main branch
   - **Action**: Rebase on main and resolve conflicts

### Stale ����� (2 PRs)

6. **PR #48**: Experimental caching feature
   - Author: code_developer
   - Created: 12 days ago
   - Last updated: 9 days ago
   - **Action**: Review and decide: continue, pause, or close

7. **PR #49**: Performance optimization POC
   - Author: code_developer
   - Created: 15 days ago
   - Last updated: 10 days ago
   - **Action**: Close if not relevant, or restart work

### Draft 📝 (1 PR)

8. **PR #50**: [WIP] Recipe sharing feature
   - Author: code_developer
   - Created: 1 day ago
   - Status: Draft (work in progress)
   - **Action**: Monitor progress

---

## Issues Found: 3

### CRITICAL Issues (1)

1. **PR #46: Failing checks for 48 hours**
   - Issue: Test suite failing for 2 days
   - Impact: Blocks other work, delays delivery
   - Recommendation: Fix tests immediately or revert changes

### HIGH Issues (1)

2. **PR #42: Ready to merge but not merged for 2 days**
   - Issue: All checks passed, approved, but not merged
   - Impact: Delays feature delivery
   - Recommendation: Merge immediately

### MEDIUM Issues (1)

3. **PR #47: Merge conflicts for 4 days**
   - Issue: Conflicts with main branch not resolved
   - Impact: May become harder to resolve over time
   - Recommendation: Rebase and resolve conflicts within 24 hours

---

## Recommendations

### Immediate Actions (Next 24 hours)

1. **Merge PR #42** (Ready to merge)
   - All criteria met, no blockers
   - Command: `gh pr merge 42 --squash`

2. **Fix failing tests in PR #46** (Critical)
   - 3 tests failing in ci/tests
   - Investigate and fix within 24 hours

3. **Resolve merge conflicts in PR #47** (High)
   - Rebase on main: `git pull --rebase origin main`
   - Resolve conflicts and push

### This Week

4. **Request reviews for PRs #43, #44**
   - Assign reviewers to waiting PRs
   - Target: Reviews within 48 hours

5. **Review stale PRs #48, #49**
   - Decide: continue, pause, or close
   - Update status or close within this sprint

### Next Sprint

6. **Monitor draft PR #50**
   - Check progress weekly
   - If stalled >14 days, discuss with code_developer

---

## PR Health Trends

### Current Sprint
- PRs opened: 5
- PRs merged: 3
- PRs closed: 1
- Average time to merge: 2.5 days
- Average time to first review: 1.2 days

### Comparison to Last Sprint
- PRs opened: +1 (was 4)
- PRs merged: +1 (was 2)
- Average time to merge: -0.5 days (improving ✅)
- Average time to first review: +0.2 days (slightly slower)

**Trend**: Merge velocity improving 📈

---

## Risk Analysis

### High-Risk PRs

1. **PR #46** - Failing for 2 days, may need significant rework
2. **PR #47** - Conflicts growing, harder to resolve over time

### Mitigation Strategies

- PR #46: Allocate code_developer time to fix tests (priority)
- PR #47: Rebase immediately before conflicts worsen

---

## Next PR Health Check

- Scheduled: Tomorrow at 10:00 AM
- Focus areas: Verify PR #42 merged, PR #46 tests fixed

---

**Generated by**: project_manager agent (pr-monitoring-analysis skill)
```

---

## Integration with project_manager Agent

### Daily Standup Generation

```python
# coffee_maker/autonomous/agents/project_manager_agent.py

def _generate_daily_standup(self) -> str:
    """Generate daily standup using PR monitoring skill."""
    from coffee_maker.autonomous.skill_loader import load_skill, SkillNames
    from datetime import datetime

    # Get repository name from git config
    repo_name = self._get_repo_name()

    skill = load_skill(SkillNames.PR_MONITORING_ANALYSIS, {
        "REPO_NAME": repo_name,
        "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d"),
    })

    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
    claude = ClaudeCLIInterface()
    result = claude.execute_prompt(skill)

    pr_report = result.content if result and result.success else "PR analysis failed"

    # Save report
    report_path = Path(f"data/reports/pr_health_{datetime.now().strftime('%Y%m%d')}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(pr_report, encoding="utf-8")

    # Notify user if CRITICAL issues found
    if "CRITICAL" in pr_report:
        self._notify_user_critical_pr_issues(pr_report)

    return pr_report
```

### User Query Handling

```python
def handle_pr_status_query(self, query: str) -> str:
    """Handle user queries about PR status."""

    if "PR #" in query:
        # Specific PR query
        pr_number = extract_pr_number(query)
        return self._get_pr_details(pr_number)

    elif "blocked" in query.lower():
        # Blocked PRs query
        return self._get_blocked_prs()

    else:
        # General PR status
        return self._generate_pr_analysis_report()
```

---

## Skill Checklist (project_manager Must Complete)

Before generating status reports:

- [ ] ✅ Load pr-monitoring-analysis skill
- [ ] ✅ Fetch all open PRs with `gh pr list`
- [ ] ✅ Categorize PRs by status
- [ ] ✅ Detect blockers and issues
- [ ] ✅ Calculate PR health score
- [ ] ✅ Generate actionable recommendations
- [ ] ✅ If CRITICAL issues: Notify user immediately
- [ ] ✅ Save report to data/reports/
- [ ] ✅ Track PR health trends over time

**Failure to monitor PRs = Delayed merges, frustrated team, delivery delays**

---

## Success Metrics

**Time Savings**:
- **Before**: 15-20 minutes manual PR monitoring (check each PR, categorize, analyze)
- **After**: 3-5 minutes with skill-generated report
- **Savings**: 12-15 minutes per health check

**Quality Improvements**:
- **Faster blocker detection**: Identify failing PRs within hours
- **Better merge velocity**: Track and improve time-to-merge
- **Proactive management**: Address issues before they escalate
- **Data-driven decisions**: Health scores guide priorities

**Measurement**:
- Track average time-to-merge (goal: <3 days)
- Track average time-to-first-review (goal: <24 hours)
- Track number of PRs blocked >3 days (goal: 0)

---

## Related Skills

- **roadmap-health-check**: Monitor ROADMAP progress
- **dod-verification**: Ensure PR quality before merge
- **git-workflow-automation**: Create PRs efficiently

---

**Remember**: Healthy PRs = Continuous delivery! 🚀

**project_manager's Mantra**: "Monitor PRs daily, merge confidently!"
