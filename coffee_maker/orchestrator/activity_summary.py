"""Activity and Progress Summary Generator.

This module implements the activity-summary skill for the orchestrator.
It generates comprehensive reports of development activity, progress, and agent status.

Related:
    .claude/skills/orchestrator/activity-summary/SKILL.md - Skill documentation
"""

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.cli.notifications import NotificationDB


def get_recent_commits(hours: int = 6) -> List[Dict]:
    """Get commits from last N hours.

    Args:
        hours: Number of hours to look back

    Returns:
        List of commit dictionaries with hash, date, subject, priority
    """
    since = datetime.now() - timedelta(hours=hours)
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")

    cmd = f'git log --since="{since_str}" --pretty=format:"%h|%ai|%s" --no-merges'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    commits = []
    for line in result.stdout.split("\n"):
        if not line:
            continue

        parts = line.split("|", 2)
        if len(parts) < 3:
            continue

        hash_val, date, subject = parts

        # Extract US/PRIORITY from commit
        us_match = re.search(r"(US-\d+|PRIORITY \d+)", subject)

        commits.append(
            {
                "hash": hash_val,
                "date": date,
                "subject": subject,
                "priority": us_match.group(1) if us_match else None,
            }
        )

    return commits


def group_commits_by_priority(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """Group commits by their priority.

    Args:
        commits: List of commit dictionaries

    Returns:
        Dictionary mapping priority -> list of commits
    """
    by_priority = defaultdict(list)

    for commit in commits:
        priority = commit["priority"] or "Other"
        by_priority[priority].append(commit)

    return dict(by_priority)


def find_completed_priorities(commits: List[Dict]) -> List[str]:
    """Find priorities that were marked complete in commits.

    Args:
        commits: List of commit dictionaries

    Returns:
        List of priority names that were completed
    """
    completed = []

    for commit in commits:
        # Look for completion patterns
        if re.search(r"(complete|implement|feat).*US-\d+", commit["subject"], re.I):
            if commit["priority"]:
                completed.append(commit["priority"])

    return list(set(completed))


def get_running_agents() -> List[Dict]:
    """Get all currently running agents.

    Returns:
        List of agent dictionaries with type, pid, priority, command
    """
    agents = []

    cmd = 'ps aux | grep -E "(code_developer|architect|code-reviewer|project_manager|orchestrator)" | grep python | grep -v grep'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    for line in result.stdout.split("\n"):
        if not line:
            continue

        parts = line.split()
        if len(parts) < 11:
            continue

        pid = int(parts[1])
        cmd_line = " ".join(parts[10:])

        agent_type = None
        priority = None

        if "code_developer" in cmd_line or "daemon" in cmd_line:
            agent_type = "code_developer"
            priority_match = re.search(r"--priority[= ](\d+)", cmd_line)
            if priority_match:
                priority = priority_match.group(1)
        elif "architect" in cmd_line:
            agent_type = "architect"
        elif "code-reviewer" in cmd_line:
            agent_type = "code-reviewer"
        elif "project_manager" in cmd_line:
            agent_type = "project_manager"
        elif "orchestrator" in cmd_line:
            agent_type = "orchestrator"

        if agent_type:
            agents.append({"type": agent_type, "pid": pid, "priority": priority, "command": cmd_line})

    return agents


def get_agent_status_from_files() -> Dict[str, Dict]:
    """Read agent status from status files.

    Filters out stale status files by checking if the PID is still running.

    Returns:
        Dictionary mapping agent_type -> status dictionary (only active agents)
    """
    status_dir = Path("data/agent_status")
    statuses = {}

    if not status_dir.exists():
        return statuses

    for status_file in status_dir.glob("*.json"):
        try:
            status = json.loads(status_file.read_text())
            agent_type = status.get("agent_type", status_file.stem)

            # Check if PID is still running
            pid = status.get("pid")
            if pid:
                # Check if process exists
                try:
                    import os

                    os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
                    # If we get here, process exists
                    statuses[agent_type] = status
                except (OSError, ProcessLookupError):
                    # Process doesn't exist - skip this stale status file
                    continue
            else:
                # No PID in status - include it anyway (might be old format)
                statuses[agent_type] = status

        except Exception:
            continue

    return statuses


def get_active_worktrees() -> List[Dict]:
    """Get all active git worktrees.

    Returns:
        List of worktree dictionaries with path, branch, commit
    """
    cmd = "git worktree list --porcelain"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    worktrees = []
    current_wt = {}

    for line in result.stdout.split("\n"):
        if line.startswith("worktree "):
            if current_wt:
                worktrees.append(current_wt)
            current_wt = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current_wt["branch"] = line.split(" ", 1)[1]
        elif line.startswith("HEAD "):
            current_wt["commit"] = line.split(" ", 1)[1]

    if current_wt:
        worktrees.append(current_wt)

    # Filter out main worktree
    return [wt for wt in worktrees if "-wt" in wt.get("path", "")]


def get_planned_priorities(roadmap_path: Path, limit: int = 5) -> List[Dict]:
    """Get next N planned priorities from ROADMAP.

    Args:
        roadmap_path: Path to ROADMAP.md
        limit: Maximum number of priorities to return

    Returns:
        List of priority dictionaries with name, title, status
    """
    if not roadmap_path.exists():
        return []

    content = roadmap_path.read_text()
    planned = []

    priority_pattern = r"##\s+(US-\d+|PRIORITY \d+):\s+(.+?)$"
    status_pattern = r"\*\*Status\*\*:\s*(.+?)$"

    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        priority_match = re.match(priority_pattern, line)
        if priority_match:
            priority_name = priority_match.group(1)
            priority_title = priority_match.group(2)

            # Look ahead for status
            for j in range(i + 1, min(i + 10, len(lines))):
                status_match = re.match(status_pattern, lines[j])
                if status_match:
                    status = status_match.group(1)

                    if "PLANNED" in status.upper() or "📝" in status:
                        planned.append({"name": priority_name, "title": priority_title, "status": status})

                        if len(planned) >= limit:
                            return planned
                    break

        i += 1

    return planned


def generate_summary_report(
    completed_work: Dict, current_work: Dict, upcoming_work: List[Dict], time_window: int = 6
) -> str:
    """Generate human-readable summary report.

    Args:
        completed_work: Dictionary with completed priorities and commits
        current_work: Dictionary with running agents, statuses, worktrees
        upcoming_work: List of upcoming planned priorities
        time_window: Hours covered by this report

    Returns:
        Formatted markdown report
    """
    report = f"""# Development Activity Report
**Period**: Last {time_window} hours
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## ✅ Completed Work

"""

    # Completed priorities
    if completed_work.get("completed_priorities"):
        report += "### Priorities Completed:\n"
        for priority in completed_work["completed_priorities"]:
            commits = completed_work["commits_by_priority"].get(priority, [])
            report += f"- **{priority}**: {len(commits)} commit(s)\n"
            for commit in commits[:3]:  # Show first 3 commits
                report += f"  - `{commit['hash']}` {commit['subject']}\n"
        report += "\n"
    else:
        report += "_No priorities completed in this period_\n\n"

    # All commits
    total_commits = len(completed_work.get("all_commits", []))
    report += f"**Total Commits**: {total_commits}\n\n"

    if total_commits > 0:
        report += "### Recent Commits:\n"
        for commit in completed_work["all_commits"][:10]:
            report += f"- `{commit['hash']}` {commit['subject']} _{commit['date']}_\n"
        report += "\n"

    report += "---\n\n"

    # Current work
    report += "## 🚀 Current Work in Progress\n\n"

    running_agents = current_work.get("running_agents", [])
    if running_agents:
        report += f"**Active Agents**: {len(running_agents)}\n\n"

        # Group by type
        by_type = defaultdict(list)
        for agent in running_agents:
            by_type[agent["type"]].append(agent)

        for agent_type, agents in by_type.items():
            report += f"### {agent_type.replace('_', ' ').title()} ({len(agents)})\n"
            for agent in agents:
                priority_str = f" - Priority {agent['priority']}" if agent["priority"] else ""
                report += f"- PID {agent['pid']}{priority_str}\n"
            report += "\n"
    else:
        report += "_No agents currently running_\n\n"

    # Worktrees
    worktrees = current_work.get("worktrees", [])
    if worktrees:
        report += f"**Active Worktrees**: {len(worktrees)}\n\n"
        for wt in worktrees:
            branch = wt.get("branch", "unknown")
            path = wt.get("path", "")
            priority = re.search(r"wt(\d+)", path)
            priority_num = priority.group(1) if priority else "?"
            report += f"- Priority {priority_num}: `{branch}` at `{path}`\n"
        report += "\n"

    # Agent status details
    agent_statuses = current_work.get("agent_statuses", {})
    if agent_statuses:
        report += "### Agent Status Details:\n\n"
        for agent_type, status in agent_statuses.items():
            state = status.get("state", "unknown")
            task = status.get("current_task", {})
            health = status.get("health", "unknown")

            report += f"**{agent_type}**: {state} ({health})\n"
            if task:
                task_type = task.get("type", "unknown")
                task_priority = task.get("priority", task.get("title", ""))
                report += f"  - Task: {task_type}"
                if task_priority:
                    report += f" ({task_priority})"
                report += "\n"
            report += "\n"

    report += "---\n\n"

    # Upcoming work
    report += "## 📋 Upcoming Work\n\n"

    if upcoming_work:
        report += f"**Next {len(upcoming_work)} Priorities**:\n\n"
        for i, priority in enumerate(upcoming_work, 1):
            report += f"{i}. **{priority['name']}**: {priority['title']}\n"
            report += f"   Status: {priority['status']}\n"
        report += "\n"
    else:
        report += "_No planned priorities found_\n\n"

    report += "---\n\n"

    # Summary statistics
    report += "## 📊 Summary Statistics\n\n"
    report += f"- Commits in period: {total_commits}\n"
    report += f"- Active agents: {len(running_agents)}\n"
    report += f"- Parallel worktrees: {len(worktrees)}\n"
    report += f"- Completed priorities: {len(completed_work.get('completed_priorities', []))}\n"
    report += f"- Upcoming priorities: {len(upcoming_work)}\n"

    return report


def save_report(report: str, timestamp: Optional[datetime] = None) -> Path:
    """Save report to evidence directory.

    Args:
        report: Report content (markdown)
        timestamp: Timestamp for filename (default: now)

    Returns:
        Path where report was saved
    """
    if timestamp is None:
        timestamp = datetime.now()

    evidence_dir = Path("evidence")
    evidence_dir.mkdir(exist_ok=True)

    filename = f"activity-summary-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"
    report_path = evidence_dir / filename
    report_path.write_text(report)

    return report_path


def create_summary_notification(report: str, report_path: Path):
    """Create notification with summary.

    Args:
        report: Full report content
        report_path: Path where report was saved
    """
    # Extract key stats for notification
    stats_match = re.search(r"- Commits in period: (\d+)", report)
    commits = stats_match.group(1) if stats_match else "0"

    agents_match = re.search(r"- Active agents: (\d+)", report)
    agents = agents_match.group(1) if agents_match else "0"

    completed_match = re.search(r"- Completed priorities: (\d+)", report)
    completed = completed_match.group(1) if completed_match else "0"

    worktrees_match = re.search(r"- Parallel worktrees: (\d+)", report)
    worktrees = worktrees_match.group(1) if worktrees_match else "0"

    # Create concise notification
    title = "Development Activity Summary"
    message = f"""Activity report generated:

✅ Completed: {completed} priorities
🚀 Active: {agents} agents running
🌿 Worktrees: {worktrees} parallel executions
📝 Commits: {commits}

Full report: {report_path}"""

    notifications = NotificationDB()
    notifications.create_notification(
        type="activity_summary",
        title=title,
        message=message.strip(),
        priority="normal",
        sound=False,  # CFR-009: No sound for background reports
        agent_id="orchestrator",
    )


def generate_activity_summary(time_window: int = 6, save_to_file: bool = True) -> str:
    """Generate complete activity summary.

    This is the main entry point for the activity-summary skill.

    Args:
        time_window: Hours to look back
        save_to_file: Whether to save report to evidence/ directory

    Returns:
        Formatted summary report
    """
    # Step 1: Collect data
    commits = get_recent_commits(hours=time_window)
    running_agents = get_running_agents()
    agent_statuses = get_agent_status_from_files()
    worktrees = get_active_worktrees()

    # Step 2: Analyze completed work
    commits_by_priority = group_commits_by_priority(commits)
    completed_priorities = find_completed_priorities(commits)

    completed_work = {
        "all_commits": commits,
        "commits_by_priority": commits_by_priority,
        "completed_priorities": completed_priorities,
    }

    # Step 3: Analyze current work
    current_work = {"running_agents": running_agents, "agent_statuses": agent_statuses, "worktrees": worktrees}

    # Step 4: Get upcoming work
    roadmap_path = Path("docs/roadmap/ROADMAP.md")
    upcoming_work = get_planned_priorities(roadmap_path, limit=5)

    # Step 5: Generate report
    report = generate_summary_report(
        completed_work=completed_work, current_work=current_work, upcoming_work=upcoming_work, time_window=time_window
    )

    # Step 6: Save and notify
    if save_to_file:
        timestamp = datetime.now()
        report_path = save_report(report, timestamp)
        create_summary_notification(report, report_path)

    return report
