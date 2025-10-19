"""
ROADMAP Health Skill for project_manager.

Automated health monitoring: parse → github → blockers → report.

Author: code_developer (implementing architect's spec)
Date: 2025-10-19
Related: SPEC-056, US-056
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ROADMAP health monitoring.

    Args:
        context: Context data containing optional 'generate_report' field

    Returns:
        Dict with health status, blockers, github status, and report path
    """
    generate_report = context.get("generate_report", True)

    print("Analyzing ROADMAP health...")

    # Step 1: Parse ROADMAP
    priorities = parse_roadmap()
    print(f"  Found {len(priorities)} priorities")

    # Step 2: Check GitHub status
    github_status = check_github_status()
    print(f"  GitHub: {github_status['open_prs']} open PRs, {github_status['failed_ci']} failed CI")

    # Step 3: Identify blockers
    blockers = identify_blockers(priorities, github_status)
    print(f"  Identified {len(blockers)} blockers")

    # Step 4: Analyze trends
    trends = analyze_trends(priorities)

    # Step 5: Determine overall health
    health = determine_health(blockers, github_status)
    print(f"  Overall health: {health}")

    # Step 6: Generate report
    report_path = None
    if generate_report:
        report_path = generate_health_report(health, priorities, blockers, github_status, trends)
        print(f"  Report generated: {report_path}")

    # Step 7: Send notification if critical
    if health == "CRITICAL":
        send_notification(blockers)

    return {
        "health_status": health,
        "blockers": blockers,
        "github_status": github_status,
        "report_path": str(report_path) if report_path else None,
    }


def parse_roadmap() -> List[Dict[str, Any]]:
    """Parse ROADMAP.md and extract priorities.

    Returns:
        List of priority dictionaries with number, title, status, effort
    """
    roadmap_path = Path("docs/roadmap/ROADMAP.md")
    if not roadmap_path.exists():
        return []

    roadmap_text = roadmap_path.read_text()
    priorities = []

    # Pattern: ### PRIORITY X: Title Status
    pattern = r"^### PRIORITY (\d+(?:\.\d+)?):?\s+(.+?)\s+(📝|🔄|✅|⏸️|🚧)"
    matches = re.finditer(pattern, roadmap_text, re.MULTILINE)

    for match in matches:
        priority_num = match.group(1)
        title = match.group(2)
        status_emoji = match.group(3)

        # Map emoji to status
        status_map = {"📝": "Planned", "🔄": "In Progress", "✅": "Complete", "⏸️": "Blocked", "🚧": "Manual Review"}
        status = status_map.get(status_emoji, "Unknown")

        priorities.append(
            {
                "number": priority_num,
                "title": title,
                "status": status,
                "emoji": status_emoji,
            }
        )

    return priorities


def check_github_status() -> Dict[str, Any]:
    """Check GitHub status using gh CLI.

    Returns:
        Dict with open_prs, failed_ci, prs, and runs
    """
    try:
        # Check for open PRs
        open_prs_result = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "number,title,state"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        prs = json.loads(open_prs_result.stdout) if open_prs_result.returncode == 0 else []

        # Check for CI runs
        ci_runs_result = subprocess.run(
            ["gh", "run", "list", "--limit", "10", "--json", "status,conclusion"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        runs = json.loads(ci_runs_result.stdout) if ci_runs_result.returncode == 0 else []

        failed_ci = sum(1 for r in runs if r.get("conclusion") == "failure")

        return {
            "open_prs": len(prs),
            "failed_ci": failed_ci,
            "prs": prs[:5],  # Limit to 5 for report brevity
            "runs": runs[:5],  # Limit to 5 for report brevity
        }

    except Exception as e:
        print(f"  Warning: Could not check GitHub status: {e}")
        return {"open_prs": 0, "failed_ci": 0, "prs": [], "runs": []}


def identify_blockers(priorities: List[Dict[str, Any]], github_status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify blockers (stuck priorities, failed CI, etc.).

    Args:
        priorities: List of priority dictionaries
        github_status: GitHub status dictionary

    Returns:
        List of blocker dictionaries with priority, blocker, severity, action
    """
    blockers = []

    # Check for blocked priorities
    for priority in priorities:
        if priority["status"] == "Blocked":
            blockers.append(
                {
                    "priority": f"PRIORITY {priority['number']}: {priority['title']}",
                    "blocker": "Priority explicitly marked as blocked",
                    "severity": "HIGH",
                    "action": "Review priority and remove blocker",
                }
            )

    # Check for stuck in-progress priorities (simplified - just flag all in progress)
    in_progress_count = sum(1 for p in priorities if p["status"] == "In Progress")
    if in_progress_count > 3:
        blockers.append(
            {
                "priority": "Multiple priorities",
                "blocker": f"{in_progress_count} priorities in progress (possible context switching)",
                "severity": "MEDIUM",
                "action": "Focus on completing one priority before starting another",
            }
        )

    # Check for failed CI
    if github_status.get("failed_ci", 0) > 0:
        blockers.append(
            {
                "priority": "CI/CD Pipeline",
                "blocker": f"{github_status['failed_ci']} recent CI failures",
                "severity": "HIGH" if github_status["failed_ci"] > 3 else "MEDIUM",
                "action": "Review and fix failing CI runs",
            }
        )

    # Check for stale PRs
    if github_status.get("open_prs", 0) > 5:
        blockers.append(
            {
                "priority": "Pull Requests",
                "blocker": f"{github_status['open_prs']} open PRs (possible review backlog)",
                "severity": "LOW",
                "action": "Review and merge or close stale PRs",
            }
        )

    return blockers


def analyze_trends(priorities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze trends (compare vs last week).

    Args:
        priorities: List of priority dictionaries

    Returns:
        Dict with completion_rate_change, velocity_trend, patterns
    """
    # Simplified: just count completed vs total
    total = len(priorities)
    completed = sum(1 for p in priorities if p["status"] == "Complete")

    completion_rate = (completed / total * 100) if total > 0 else 0

    return {
        "completion_rate": completion_rate,
        "completion_rate_change": 0.0,  # Would need historical data
        "velocity_trend": "stable",  # Would need historical data
        "patterns": [],
    }


def determine_health(blockers: List[Dict[str, Any]], github_status: Dict[str, Any]) -> str:
    """Determine overall health status.

    Args:
        blockers: List of blocker dictionaries
        github_status: GitHub status dictionary

    Returns:
        Health status string (HEALTHY, WARNING, CRITICAL)
    """
    critical_blockers = [b for b in blockers if b["severity"] == "CRITICAL"]
    high_blockers = [b for b in blockers if b["severity"] == "HIGH"]
    failed_ci = github_status.get("failed_ci", 0)

    if critical_blockers or failed_ci > 3:
        return "CRITICAL"
    elif high_blockers or len(blockers) > 3 or failed_ci > 0:
        return "WARNING"
    else:
        return "HEALTHY"


def generate_health_report(
    health: str,
    priorities: List[Dict[str, Any]],
    blockers: List[Dict[str, Any]],
    github_status: Dict[str, Any],
    trends: Dict[str, Any],
) -> Path:
    """Generate synthetic health report (1-2 pages max).

    Args:
        health: Overall health status
        priorities: List of priority dictionaries
        blockers: List of blocker dictionaries
        github_status: GitHub status dictionary
        trends: Trends dictionary

    Returns:
        Path to generated report
    """
    health_emoji = "🔴" if health == "CRITICAL" else "🟡" if health == "WARNING" else "🟢"

    in_progress = sum(1 for p in priorities if p["status"] == "In Progress")
    completed = sum(1 for p in priorities if p["status"] == "Complete")
    planned = sum(1 for p in priorities if p["status"] == "Planned")
    blocked = sum(1 for p in priorities if p["status"] == "Blocked")

    report = f"""# ROADMAP Health Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Health Status**: {health} {health_emoji}

## Summary

- **Total Priorities**: {len(priorities)}
- **Completed**: {completed} ({trends['completion_rate']:.1f}%)
- **In Progress**: {in_progress}
- **Planned**: {planned}
- **Blocked**: {blocked}
- **Open PRs**: {github_status['open_prs']}
- **Failed CI**: {github_status['failed_ci']}

## Top Blockers

"""

    if not blockers:
        report += "_No blockers identified. All systems healthy!_ ✅\n\n"
    else:
        # Show top 3 most critical blockers
        for i, blocker in enumerate(
            sorted(blockers, key=lambda b: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(b["severity"], 4))[:3],
            1,
        ):
            report += f"""### {i}. {blocker['priority']} ({blocker['severity']})

**Blocker**: {blocker['blocker']}
**Action**: {blocker['action']}

"""

    report += f"""## Trends

- **Completion Rate**: {trends['completion_rate']:.1f}%
- **Velocity**: {trends['velocity_trend']}

## Recommended Actions

"""

    # Generate 3-5 actionable recommendations based on blockers
    if health == "CRITICAL":
        report += """1. **URGENT**: Address critical blockers immediately
2. **URGENT**: Fix failing CI/CD pipeline
3. Review blocked priorities and remove impediments
4. Reduce work-in-progress to improve focus
"""
    elif health == "WARNING":
        report += """1. Review and resolve high-priority blockers
2. Monitor CI/CD health and fix failures
3. Consider reducing parallel work streams
4. Review stale PRs for merge or closure
"""
    else:
        report += """1. Continue current pace - project is healthy
2. Maintain focus on one priority at a time
3. Keep CI/CD green and PRs flowing
4. Consider starting next planned priority
"""

    # Save report
    evidence_dir = Path("evidence")
    evidence_dir.mkdir(exist_ok=True)

    report_path = evidence_dir / f"roadmap-health-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    report_path.write_text(report)

    return report_path


def send_notification(blockers: List[Dict[str, Any]]):
    """Send notification if critical blockers.

    Args:
        blockers: List of blocker dictionaries
    """
    # Placeholder - would integrate with notification system
    critical = [b for b in blockers if b["severity"] == "CRITICAL"]
    if critical:
        print(f"\n⚠️  CRITICAL ALERT: {len(critical)} critical blockers found!")
        for blocker in critical:
            print(f"  - {blocker['priority']}: {blocker['blocker']}")


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
