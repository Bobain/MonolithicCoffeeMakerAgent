"""
Code Forensics Skill for code-searcher.
Trace code evolution, identify contributors, analyze patterns.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute code forensics analysis."""
    scope = context.get("scope", ".")
    time_range = context.get("time_range")

    print(f"Analyzing code forensics: {scope}")

    # Step 1: Analyze git history
    commits = analyze_git_history(scope, time_range)

    # Step 2: Identify contributors
    contributors = identify_contributors(commits)

    # Step 3: Detect hotspots
    hotspots = detect_hotspots(commits)

    # Step 4: Analyze patterns
    patterns = analyze_patterns(commits)

    # Step 5: Generate insights
    insights = generate_insights(contributors, hotspots, patterns)

    # Step 6: Create report
    report_path = create_forensics_report(scope, contributors, hotspots, patterns, insights)

    return {
        "contributors": contributors[:10],  # Top 10
        "hotspots": hotspots[:10],  # Top 10
        "patterns": patterns,
        "report_path": str(report_path),
    }


def analyze_git_history(scope: str, time_range: str) -> List[Dict[str, Any]]:
    """Analyze git history for scope."""
    cmd = ["git", "log", "--numstat", "--pretty=format:%H|%an|%ae|%ad|%s"]

    if time_range:
        cmd.append(f"--since={time_range}")

    if scope != ".":
        cmd.append("--")
        cmd.append(scope)

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse git log output
    commits = []
    current_commit = None

    for line in result.stdout.split("\n"):
        if "|" in line:
            # Commit header
            parts = line.split("|", 4)
            if len(parts) == 5:
                hash, author, email, date, subject = parts
                current_commit = {
                    "hash": hash,
                    "author": author,
                    "email": email,
                    "date": date,
                    "subject": subject,
                    "files": [],
                }
                commits.append(current_commit)
        elif line.strip() and current_commit:
            # File change (numstat)
            parts = line.split()
            if len(parts) >= 3:
                added, removed, file = parts[0], parts[1], parts[2]
                current_commit["files"].append(
                    {
                        "file": file,
                        "added": int(added) if added.isdigit() else 0,
                        "removed": int(removed) if removed.isdigit() else 0,
                    }
                )

    return commits


def identify_contributors(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify top contributors."""
    contributors = defaultdict(lambda: {"commits": 0, "lines_added": 0, "lines_removed": 0})

    for commit in commits:
        author = commit["author"]
        contributors[author]["commits"] += 1

        for file in commit["files"]:
            contributors[author]["lines_added"] += file["added"]
            contributors[author]["lines_removed"] += file["removed"]

    # Convert to list and sort by commits
    result = [{"name": name, **stats} for name, stats in contributors.items()]

    result.sort(key=lambda x: x["commits"], reverse=True)

    return result


def detect_hotspots(commits: List[Dict[str, Any]]) -> List[str]:
    """Detect code hotspots (files changed most frequently)."""
    file_changes = defaultdict(int)

    for commit in commits:
        for file in commit["files"]:
            file_changes[file["file"]] += 1

    # Sort by change frequency
    hotspots = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)

    return [file for file, count in hotspots]


def analyze_patterns(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze commit patterns (time of day, day of week)."""
    hour_distribution = defaultdict(int)
    day_distribution = defaultdict(int)

    for commit in commits:
        # Parse date (format: "Wed Oct 19 14:23:45 2025 +0200")
        date_str = commit["date"]
        try:
            dt = datetime.strptime(date_str.rsplit(" ", 1)[0], "%a %b %d %H:%M:%S %Y")
            hour_distribution[dt.hour] += 1
            day_distribution[dt.strftime("%A")] += 1
        except ValueError:
            pass

    return {
        "peak_hour": max(hour_distribution, key=hour_distribution.get) if hour_distribution else None,
        "peak_day": max(day_distribution, key=day_distribution.get) if day_distribution else None,
        "hour_distribution": dict(hour_distribution),
        "day_distribution": dict(day_distribution),
    }


def generate_insights(contributors: List[Dict[str, Any]], hotspots: List[str], patterns: Dict[str, Any]) -> List[str]:
    """Generate actionable insights."""
    insights = []

    # Top contributor
    if contributors:
        top = contributors[0]
        insights.append(
            f"Top contributor: {top['name']} ({top['commits']} commits, " f"{top['lines_added']} lines added)"
        )

    # Hotspots
    if hotspots:
        insights.append(f"Code hotspot: {hotspots[0]} (changed most frequently → refactor candidate)")

    # Patterns
    if patterns.get("peak_hour"):
        insights.append(f"Peak commit time: {patterns['peak_hour']}:00 (team most active)")

    return insights


def create_forensics_report(
    scope: str, contributors: List[Dict[str, Any]], hotspots: List[str], patterns: Dict[str, Any], insights: List[str]
) -> Path:
    """Create synthetic forensics report."""
    report = f"""# Code Forensics Report

**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Scope**: {scope}

## Top 5 Contributors

| Rank | Name | Commits | Lines Added | Lines Removed |
|------|------|---------|-------------|---------------|
"""

    for i, contributor in enumerate(contributors[:5], 1):
        report += f"| {i} | {contributor['name']} | {contributor['commits']} | {contributor['lines_added']} | {contributor['lines_removed']} |\n"

    report += f"""

## Top 5 Code Hotspots

(Files changed most frequently - potential refactor targets)

"""

    for i, hotspot in enumerate(hotspots[:5], 1):
        report += f"{i}. `{hotspot}`\n"

    report += f"""

## Commit Patterns

- **Peak Hour**: {patterns.get('peak_hour', 'N/A')}:00
- **Peak Day**: {patterns.get('peak_day', 'N/A')}

## Key Insights

"""

    for insight in insights:
        report += f"- {insight}\n"

    # Save report
    report_path = Path("evidence/code-forensics-report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)

    return report_path


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
