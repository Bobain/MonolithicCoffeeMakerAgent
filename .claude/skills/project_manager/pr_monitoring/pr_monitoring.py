"""
PR Monitoring & Analysis Skill for project_manager.

Automated PR monitoring: fetch → categorize → analyze blockers → report.

Author: code_developer (implementing US-071)
Date: 2025-10-19
Related: US-071
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute PR monitoring and analysis.

    Args:
        context: Context data containing optional 'repo_name' and 'current_date' fields

    Returns:
        Dict with pr_health_score, categorized_prs, issues, recommendations, and report_path
    """
    repo_name = context.get("repo_name", get_repo_name())
    current_date = context.get("current_date", datetime.now(timezone.utc))
    if isinstance(current_date, str):
        current_date = datetime.fromisoformat(current_date.replace("Z", "+00:00"))

    generate_report = context.get("generate_report", True)

    print(f"Analyzing PRs for {repo_name}...")

    # Step 1: Fetch all open PRs
    prs = fetch_open_prs()
    print(f"  Found {len(prs)} open PRs")

    # Step 2: Categorize PRs by status
    categorized_prs = categorize_prs(prs, current_date)
    print(
        f"  Categorized: {len(categorized_prs['ready_to_merge'])} ready, "
        f"{len(categorized_prs['failing_checks'])} failing, "
        f"{len(categorized_prs['waiting_for_review'])} waiting"
    )

    # Step 3: Analyze blockers and issues
    issues = detect_issues(categorized_prs, current_date)
    print(f"  Identified {len(issues)} issues")

    # Step 4: Calculate PR health score
    pr_health_score = calculate_pr_health_score(categorized_prs, issues)
    print(f"  PR Health Score: {pr_health_score}/100")

    # Step 5: Generate recommendations
    recommendations = generate_recommendations(categorized_prs, issues)
    print(f"  Generated {len(recommendations)} recommendations")

    # Step 6: Generate report
    report_path = None
    if generate_report:
        report_path = generate_pr_analysis_report(
            repo_name, current_date, pr_health_score, categorized_prs, issues, recommendations
        )
        print(f"  Report generated: {report_path}")

    # Step 7: Send notification if critical issues
    critical_issues = [i for i in issues if i["severity"] == "CRITICAL"]
    if critical_issues:
        send_notification(critical_issues)

    return {
        "pr_health_score": pr_health_score,
        "categorized_prs": {k: len(v) for k, v in categorized_prs.items()},
        "issues": issues,
        "recommendations": recommendations,
        "report_path": str(report_path) if report_path else None,
    }


def get_repo_name() -> str:
    """Get repository name from git config.

    Returns:
        Repository name (e.g., "user/repo") or "unknown"
    """
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("nameWithOwner", "unknown")

    except Exception as e:
        print(f"  Warning: Could not get repo name: {e}")

    return "unknown"


def fetch_open_prs() -> List[Dict[str, Any]]:
    """Fetch all open PRs using gh CLI.

    Returns:
        List of PR dictionaries with full metadata
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--state",
                "open",
                "--json",
                "number,title,author,createdAt,updatedAt,isDraft,labels,reviews,statusCheckRollup,mergeable",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"  Warning: gh pr list failed: {result.stderr}")
            return []

        prs_data = json.loads(result.stdout)

        # Parse and normalize PR data
        prs = []
        for pr in prs_data:
            prs.append(
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "author": pr["author"]["login"] if pr.get("author") else "unknown",
                    "created_at": datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00")),
                    "updated_at": datetime.fromisoformat(pr["updatedAt"].replace("Z", "+00:00")),
                    "is_draft": pr.get("isDraft", False),
                    "labels": [label["name"] for label in pr.get("labels", [])],
                    "reviews": pr.get("reviews", []),
                    "status_checks": pr.get("statusCheckRollup", []),
                    "mergeable": pr.get("mergeable", "UNKNOWN"),
                }
            )

        return prs

    except Exception as e:
        print(f"  Warning: Could not fetch PRs: {e}")
        return []


def categorize_prs(prs: List[Dict[str, Any]], current_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize PRs by status.

    Args:
        prs: List of PR dictionaries
        current_date: Current date for staleness calculation

    Returns:
        Dict mapping category name to list of PRs
    """
    categorized = {
        "ready_to_merge": [],
        "waiting_for_review": [],
        "changes_requested": [],
        "failing_checks": [],
        "merge_conflicts": [],
        "stale": [],
        "draft": [],
    }

    for pr in prs:
        category = categorize_pr(pr, current_date)
        categorized[category].append(pr)

    return categorized


def categorize_pr(pr: Dict[str, Any], current_date: datetime) -> str:
    """Categorize a single PR by status.

    Args:
        pr: PR dictionary
        current_date: Current date for staleness calculation

    Returns:
        Category string
    """
    # Draft
    if pr["is_draft"]:
        return "draft"

    # Stale (no updates in >7 days)
    days_since_update = (current_date - pr["updated_at"]).days
    if days_since_update > 7:
        return "stale"

    # Merge Conflicts
    if pr["mergeable"] == "CONFLICTING":
        return "merge_conflicts"

    # Failing Checks
    status_checks = pr.get("status_checks", [])
    if any(check.get("state") == "FAILURE" or check.get("conclusion") == "FAILURE" for check in status_checks):
        return "failing_checks"

    # Changes Requested
    reviews = pr.get("reviews", [])
    if any(review.get("state") == "CHANGES_REQUESTED" for review in reviews):
        return "changes_requested"

    # Ready to Merge
    has_approval = any(review.get("state") == "APPROVED" for review in reviews)
    checks_pass = (
        all(check.get("state") == "SUCCESS" or check.get("conclusion") == "SUCCESS" for check in status_checks)
        or not status_checks
    )
    no_conflicts = pr["mergeable"] != "CONFLICTING"

    if has_approval and checks_pass and no_conflicts:
        return "ready_to_merge"

    # Waiting for Review (default)
    return "waiting_for_review"


def detect_issues(categorized_prs: Dict[str, List[Dict[str, Any]]], current_date: datetime) -> List[Dict[str, Any]]:
    """Detect blockers and issues in PRs.

    Args:
        categorized_prs: Categorized PRs dictionary
        current_date: Current date for time-based issue detection

    Returns:
        List of issue dictionaries with severity, type, description, recommendation
    """
    issues = []

    # CRITICAL: Failing checks for >24 hours
    for pr in categorized_prs["failing_checks"]:
        hours_failing = (current_date - pr["updated_at"]).total_seconds() / 3600
        if hours_failing > 24:
            issues.append(
                {
                    "severity": "CRITICAL",
                    "pr_number": pr["number"],
                    "type": "failing_checks_too_long",
                    "description": f"PR #{pr['number']} has failing checks for {int(hours_failing)} hours",
                    "recommendation": "Fix failing checks immediately or close PR",
                }
            )

    # HIGH: Ready to merge but not merged for >2 days
    for pr in categorized_prs["ready_to_merge"]:
        days_ready = (current_date - pr["updated_at"]).days
        if days_ready > 2:
            issues.append(
                {
                    "severity": "HIGH",
                    "pr_number": pr["number"],
                    "type": "ready_but_not_merged",
                    "description": f"PR #{pr['number']} ready to merge for {days_ready} days",
                    "recommendation": "Merge immediately or investigate why delayed",
                }
            )

    # HIGH: Merge conflicts for >3 days
    for pr in categorized_prs["merge_conflicts"]:
        days_conflicting = (current_date - pr["updated_at"]).days
        if days_conflicting > 3:
            issues.append(
                {
                    "severity": "HIGH",
                    "pr_number": pr["number"],
                    "type": "merge_conflicts_too_long",
                    "description": f"PR #{pr['number']} has merge conflicts for {days_conflicting} days",
                    "recommendation": "Rebase and resolve conflicts within 24 hours",
                }
            )

    # HIGH: Changes requested for >5 days (no response)
    for pr in categorized_prs["changes_requested"]:
        days_since_request = (current_date - pr["updated_at"]).days
        if days_since_request > 5:
            issues.append(
                {
                    "severity": "HIGH",
                    "pr_number": pr["number"],
                    "type": "changes_requested_no_response",
                    "description": f"PR #{pr['number']} has requested changes for {days_since_request} days",
                    "recommendation": "Address review feedback or discuss with reviewers",
                }
            )

    # HIGH: Waiting for review for >3 days
    for pr in categorized_prs["waiting_for_review"]:
        days_waiting = (current_date - pr["created_at"]).days
        if days_waiting > 3:
            issues.append(
                {
                    "severity": "HIGH",
                    "pr_number": pr["number"],
                    "type": "waiting_for_review_too_long",
                    "description": f"PR #{pr['number']} waiting for review for {days_waiting} days",
                    "recommendation": "Assign reviewers or request review from team",
                }
            )

    # MEDIUM: Stale PRs (>7 days)
    for pr in categorized_prs["stale"]:
        days_stale = (current_date - pr["updated_at"]).days
        issues.append(
            {
                "severity": "MEDIUM",
                "pr_number": pr["number"],
                "type": "stale_pr",
                "description": f"PR #{pr['number']} stale for {days_stale} days (no updates)",
                "recommendation": "Review and decide: continue, pause, or close",
            }
        )

    # LOW: Draft PR for >14 days
    for pr in categorized_prs["draft"]:
        days_draft = (current_date - pr["created_at"]).days
        if days_draft > 14:
            issues.append(
                {
                    "severity": "LOW",
                    "pr_number": pr["number"],
                    "type": "draft_too_long",
                    "description": f"PR #{pr['number']} in draft for {days_draft} days",
                    "recommendation": "Complete work or close if abandoned",
                }
            )

    return issues


def calculate_pr_health_score(categorized_prs: Dict[str, List[Dict[str, Any]]], issues: List[Dict[str, Any]]) -> int:
    """Calculate overall PR health score (0-100).

    Scoring:
    - Base score: 100
    - Ready to merge ratio: +0 to -20 (penalty if few PRs ready)
    - Failing checks ratio: -30 per failing PR
    - Merge conflicts ratio: -20 per conflicting PR
    - Stale ratio: -15 per stale PR
    - Issues: -15 per CRITICAL, -10 per HIGH, -5 per MEDIUM, -2 per LOW

    Args:
        categorized_prs: Categorized PRs dictionary
        issues: List of issue dictionaries

    Returns:
        Health score (0-100)
    """
    base_score = 100

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
        severity = issue.get("severity", "LOW")
        if severity == "CRITICAL":
            base_score -= 15
        elif severity == "HIGH":
            base_score -= 10
        elif severity == "MEDIUM":
            base_score -= 5
        elif severity == "LOW":
            base_score -= 2

    return max(0, min(100, int(base_score)))  # Clamp to 0-100


def generate_recommendations(
    categorized_prs: Dict[str, List[Dict[str, Any]]], issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate actionable recommendations.

    Args:
        categorized_prs: Categorized PRs dictionary
        issues: List of issue dictionaries

    Returns:
        List of recommendation dictionaries with priority, action, details, prs, timeline
    """
    recommendations = []

    # Ready to merge PRs
    if categorized_prs["ready_to_merge"]:
        recommendations.append(
            {
                "priority": "HIGH",
                "action": "Merge ready PRs",
                "details": f"{len(categorized_prs['ready_to_merge'])} PR(s) ready to merge",
                "prs": [pr["number"] for pr in categorized_prs["ready_to_merge"]],
                "timeline": "Next 24 hours",
            }
        )

    # Failing checks
    if categorized_prs["failing_checks"]:
        recommendations.append(
            {
                "priority": "CRITICAL",
                "action": "Fix failing CI checks",
                "details": f"{len(categorized_prs['failing_checks'])} PR(s) with failing checks",
                "prs": [pr["number"] for pr in categorized_prs["failing_checks"]],
                "timeline": "Immediate",
            }
        )

    # Merge conflicts
    if categorized_prs["merge_conflicts"]:
        recommendations.append(
            {
                "priority": "HIGH",
                "action": "Resolve merge conflicts",
                "details": f"{len(categorized_prs['merge_conflicts'])} PR(s) with conflicts",
                "prs": [pr["number"] for pr in categorized_prs["merge_conflicts"]],
                "timeline": "Next 48 hours",
            }
        )

    # Changes requested
    if categorized_prs["changes_requested"]:
        recommendations.append(
            {
                "priority": "HIGH",
                "action": "Address review feedback",
                "details": f"{len(categorized_prs['changes_requested'])} PR(s) with changes requested",
                "prs": [pr["number"] for pr in categorized_prs["changes_requested"]],
                "timeline": "This week",
            }
        )

    # Waiting for review (only if >3 PRs)
    if len(categorized_prs["waiting_for_review"]) > 3:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "action": "Review pending PRs",
                "details": f"{len(categorized_prs['waiting_for_review'])} PR(s) waiting for review",
                "prs": [pr["number"] for pr in categorized_prs["waiting_for_review"]],
                "timeline": "This week",
            }
        )

    # Stale PRs
    if categorized_prs["stale"]:
        recommendations.append(
            {
                "priority": "LOW",
                "action": "Close or revive stale PRs",
                "details": f"{len(categorized_prs['stale'])} stale PR(s) (>7 days no update)",
                "prs": [pr["number"] for pr in categorized_prs["stale"]],
                "timeline": "This sprint",
            }
        )

    # Sort by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    return sorted(recommendations, key=lambda r: priority_order.get(r["priority"], 4))


def generate_pr_analysis_report(
    repo_name: str,
    current_date: datetime,
    pr_health_score: int,
    categorized_prs: Dict[str, List[Dict[str, Any]]],
    issues: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
) -> Path:
    """Generate PR analysis report.

    Args:
        repo_name: Repository name
        current_date: Current date
        pr_health_score: PR health score (0-100)
        categorized_prs: Categorized PRs dictionary
        issues: List of issue dictionaries
        recommendations: List of recommendation dictionaries

    Returns:
        Path to generated report
    """
    # Determine health status emoji
    if pr_health_score >= 90:
        health_emoji = "🟢"
        health_status = "EXCELLENT"
    elif pr_health_score >= 70:
        health_emoji = "🟡"
        health_status = "GOOD"
    elif pr_health_score >= 50:
        health_emoji = "🟠"
        health_status = "FAIR"
    else:
        health_emoji = "🔴"
        health_status = "POOR"

    total_prs = sum(len(prs) for prs in categorized_prs.values())

    report = f"""# Pull Request Monitoring & Analysis Report

**Generated**: {current_date.strftime("%Y-%m-%d %H:%M")}
**Repository**: {repo_name}
**Health Score**: {pr_health_score}/100 {health_emoji}

---

## Executive Summary

- Total Open PRs: {total_prs}
- Ready to Merge: {len(categorized_prs['ready_to_merge'])} ✅
- Waiting for Review: {len(categorized_prs['waiting_for_review'])} ⏳
- Changes Requested: {len(categorized_prs['changes_requested'])} 🔄
- Failing Checks: {len(categorized_prs['failing_checks'])} ❌
- Merge Conflicts: {len(categorized_prs['merge_conflicts'])} ⚠️
- Stale: {len(categorized_prs['stale'])} 🕐
- Draft: {len(categorized_prs['draft'])} 📝

**Overall Health**: {health_status} {health_emoji}

---

## PRs by Category

"""

    # Ready to Merge
    if categorized_prs["ready_to_merge"]:
        report += f"""### Ready to Merge ✅ ({len(categorized_prs['ready_to_merge'])} PR{"s" if len(categorized_prs['ready_to_merge']) > 1 else ""})

**HIGH PRIORITY**: These PRs should be merged ASAP!

"""
        for i, pr in enumerate(categorized_prs["ready_to_merge"], 1):
            report += f"""{i}. **PR #{pr['number']}**: {pr['title']}
   - Author: {pr['author']}
   - Created: {(current_date - pr['created_at']).days} days ago
   - **Action**: Merge immediately

"""

    # Waiting for Review
    if categorized_prs["waiting_for_review"]:
        report += f"""### Waiting for Review ⏳ ({len(categorized_prs['waiting_for_review'])} PR{"s" if len(categorized_prs['waiting_for_review']) > 1 else ""})

"""
        for pr in categorized_prs["waiting_for_review"]:
            report += f"""- **PR #{pr['number']}**: {pr['title']}
  - Author: {pr['author']}
  - Created: {(current_date - pr['created_at']).days} days ago
  - **Action**: Assign reviewer or request review

"""

    # Changes Requested
    if categorized_prs["changes_requested"]:
        report += f"""### Changes Requested 🔄 ({len(categorized_prs['changes_requested'])} PR{"s" if len(categorized_prs['changes_requested']) > 1 else ""})

"""
        for pr in categorized_prs["changes_requested"]:
            report += f"""- **PR #{pr['number']}**: {pr['title']}
  - Author: {pr['author']}
  - Updated: {(current_date - pr['updated_at']).days} days ago
  - **Action**: Address review feedback

"""

    # Failing Checks
    if categorized_prs["failing_checks"]:
        report += f"""### Failing Checks ❌ ({len(categorized_prs['failing_checks'])} PR{"s" if len(categorized_prs['failing_checks']) > 1 else ""})

**CRITICAL**: These PRs need immediate attention!

"""
        for pr in categorized_prs["failing_checks"]:
            failing_checks = [
                c
                for c in pr.get("status_checks", [])
                if c.get("state") == "FAILURE" or c.get("conclusion") == "FAILURE"
            ]
            report += f"""- **PR #{pr['number']}**: {pr['title']}
  - Author: {pr['author']}
  - Updated: {(current_date - pr['updated_at']).days} days ago
  - Failing checks: {len(failing_checks)}
  - **Action**: Fix failing tests/checks immediately

"""

    # Merge Conflicts
    if categorized_prs["merge_conflicts"]:
        report += f"""### Merge Conflicts ⚠️ ({len(categorized_prs['merge_conflicts'])} PR{"s" if len(categorized_prs['merge_conflicts']) > 1 else ""})

"""
        for pr in categorized_prs["merge_conflicts"]:
            report += f"""- **PR #{pr['number']}**: {pr['title']}
  - Author: {pr['author']}
  - Updated: {(current_date - pr['updated_at']).days} days ago
  - **Action**: Rebase on main and resolve conflicts

"""

    # Stale
    if categorized_prs["stale"]:
        report += f"""### Stale 🕐 ({len(categorized_prs['stale'])} PR{"s" if len(categorized_prs['stale']) > 1 else ""})

"""
        for pr in categorized_prs["stale"]:
            report += f"""- **PR #{pr['number']}**: {pr['title']}
  - Author: {pr['author']}
  - Last updated: {(current_date - pr['updated_at']).days} days ago
  - **Action**: Review and decide: continue, pause, or close

"""

    # Draft
    if categorized_prs["draft"]:
        report += f"""### Draft 📝 ({len(categorized_prs['draft'])} PR{"s" if len(categorized_prs['draft']) > 1 else ""})

"""
        for pr in categorized_prs["draft"]:
            report += f"""- **PR #{pr['number']}**: {pr['title']}
  - Author: {pr['author']}
  - Created: {(current_date - pr['created_at']).days} days ago
  - **Action**: Monitor progress

"""

    # Issues
    report += f"""---

## Issues Found: {len(issues)}

"""

    if not issues:
        report += "_No issues identified. All PRs healthy!_ ✅\n\n"
    else:
        # Group by severity
        critical = [i for i in issues if i["severity"] == "CRITICAL"]
        high = [i for i in issues if i["severity"] == "HIGH"]
        medium = [i for i in issues if i["severity"] == "MEDIUM"]
        low = [i for i in issues if i["severity"] == "LOW"]

        if critical:
            report += f"### CRITICAL Issues ({len(critical)})\n\n"
            for i, issue in enumerate(critical, 1):
                report += f"""{i}. **PR #{issue['pr_number']}: {issue['type']}**
   - Issue: {issue['description']}
   - Recommendation: {issue['recommendation']}

"""

        if high:
            report += f"### HIGH Issues ({len(high)})\n\n"
            for i, issue in enumerate(high, 1):
                report += f"""{i}. **PR #{issue['pr_number']}: {issue['type']}**
   - Issue: {issue['description']}
   - Recommendation: {issue['recommendation']}

"""

        if medium:
            report += f"### MEDIUM Issues ({len(medium)})\n\n"
            for issue in medium:
                report += f"""- **PR #{issue['pr_number']}**: {issue['description']}
  - Recommendation: {issue['recommendation']}

"""

        if low:
            report += f"### LOW Issues ({len(low)})\n\n"
            for issue in low:
                report += f"""- **PR #{issue['pr_number']}**: {issue['description']}

"""

    # Recommendations
    report += """---

## Recommendations

"""

    if not recommendations:
        report += "_No specific recommendations. Continue monitoring PRs regularly!_\n\n"
    else:
        # Group by timeline
        immediate = [r for r in recommendations if "Immediate" in r["timeline"]]
        next_24h = [r for r in recommendations if "24 hours" in r["timeline"]]
        next_48h = [r for r in recommendations if "48 hours" in r["timeline"]]
        this_week = [r for r in recommendations if "week" in r["timeline"]]
        this_sprint = [r for r in recommendations if "sprint" in r["timeline"]]

        if immediate or next_24h:
            report += "### Immediate Actions (Next 24 hours)\n\n"
            for rec in immediate + next_24h:
                prs_list = ", ".join(f"#{pr}" for pr in rec["prs"])
                report += f"""- **{rec['action']}** ({rec['priority']})
  - {rec['details']}
  - PRs: {prs_list}

"""

        if next_48h or this_week:
            report += "### This Week\n\n"
            for rec in next_48h + this_week:
                prs_list = ", ".join(f"#{pr}" for pr in rec["prs"])
                report += f"""- **{rec['action']}**
  - {rec['details']}
  - PRs: {prs_list}

"""

        if this_sprint:
            report += "### This Sprint\n\n"
            for rec in this_sprint:
                prs_list = ", ".join(f"#{pr}" for pr in rec["prs"])
                report += f"""- **{rec['action']}**
  - {rec['details']}
  - PRs: {prs_list}

"""

    report += f"""---

**Generated by**: project_manager agent (pr-monitoring-analysis skill)
**Next PR Health Check**: Recommended within 24 hours
"""

    # Save report
    evidence_dir = Path(".claude/skills/project-manager/pr-monitoring/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    report_path = evidence_dir / f"pr-monitoring-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    report_path.write_text(report)

    return report_path


def send_notification(critical_issues: List[Dict[str, Any]]):
    """Send notification for critical issues.

    Args:
        critical_issues: List of critical issue dictionaries
    """
    if critical_issues:
        print(f"\n⚠️  CRITICAL ALERT: {len(critical_issues)} critical PR issues found!")
        for issue in critical_issues:
            print(f"  - PR #{issue['pr_number']}: {issue['description']}")


if __name__ == "__main__":
    # Load context from stdin or use default
    try:
        if not sys.stdin.isatty():
            stdin_text = sys.stdin.read().strip()
            if stdin_text:
                context = json.loads(stdin_text)
            else:
                context = {"generate_report": True}
        else:
            # Default context for testing
            context = {"generate_report": True}
    except (json.JSONDecodeError, ValueError):
        # Fallback to default context
        context = {"generate_report": True}

    result = main(context)
    print("\nResult:")
    print(json.dumps(result, indent=2))
