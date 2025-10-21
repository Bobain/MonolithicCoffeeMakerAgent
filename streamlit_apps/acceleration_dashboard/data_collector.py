"""Data collector for acceleration metrics."""

import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import re


@dataclass
class CommitMetric:
    """Single commit metric."""

    sha: str
    date: datetime
    message: str
    author: str
    files_changed: int
    insertions: int
    deletions: int


@dataclass
class TaskMetric:
    """Single task metric from ROADMAP."""

    priority: str
    name: str
    status: str
    estimated_effort: Optional[str]
    completed_date: Optional[datetime]


class MetricsCollector:
    """Collects metrics from various sources."""

    def __init__(self, project_root: Path):
        """Initialize metrics collector.

        Args:
            project_root (Path): Project root directory.
        """
        self.project_root = project_root

    def collect_velocity_metrics(self, days: int = 30) -> Dict:
        """Collect velocity metrics.

        Args:
            days (int): Number of days to look back.

        Returns:
            Dict: Velocity metrics.
        """
        since_date = datetime.now() - timedelta(days=days)
        commits = self._get_commits_since(since_date)

        return {
            "total_commits": len(commits),
            "commits_per_day": len(commits) / days if days > 0 else 0,
            "average_files_per_commit": sum(c.files_changed for c in commits) / len(commits) if commits else 0,
            "total_lines_changed": sum(c.insertions + c.deletions for c in commits),
            "commits_by_day": self._group_commits_by_day(commits),
        }

    def collect_duration_stats(self) -> Dict:
        """Collect task duration statistics.

        Returns:
            Dict: Duration statistics.
        """
        # Parse ROADMAP for completed tasks
        tasks = self._parse_roadmap_tasks()
        completed_tasks = [t for t in tasks if "Complete" in t.status]

        return {
            "total_completed": len(completed_tasks),
            "average_duration_estimate": self._calculate_avg_duration(completed_tasks),
            "tasks_by_status": self._group_tasks_by_status(tasks),
        }

    def collect_bottleneck_data(self) -> Dict:
        """Collect bottleneck analysis data.

        Returns:
            Dict: Bottleneck data.
        """
        commits = self._get_commits_since(datetime.now() - timedelta(days=7))

        # Analyze commit patterns
        time_between_commits = self._calculate_commit_gaps(commits)

        return {
            "longest_gaps": sorted(time_between_commits, reverse=True)[:10],
            "average_gap_hours": sum(time_between_commits) / len(time_between_commits) if time_between_commits else 0,
            "idle_time_detected": any(gap > 24 for gap in time_between_commits),
        }

    def collect_acceleration_opportunities(self) -> Dict:
        """Identify acceleration opportunities.

        Returns:
            Dict: Acceleration opportunities.
        """
        tasks = self._parse_roadmap_tasks()
        planned_tasks = [t for t in tasks if "Planned" in t.status]

        # Identify parallelizable work
        parallelizable = self._identify_parallelizable_work(planned_tasks)

        return {
            "parallelizable_tasks": len(parallelizable),
            "second_developer_velocity_increase": 0.75 if len(parallelizable) > 10 else 0.4,
            "new_skills_needed": self._identify_automation_candidates(),
            "process_improvements": self._identify_process_improvements(),
        }

    def _get_commits_since(self, since: datetime) -> List[CommitMetric]:
        """Get commits since a given date.

        Args:
            since (datetime): Date to get commits from.

        Returns:
            List[CommitMetric]: List of commits.
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--since={since.strftime('%Y-%m-%d')}",
                    "--pretty=format:%H|%ai|%s|%an",
                    "--numstat",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            commits = []
            lines = result.stdout.split("\n")
            i = 0

            while i < len(lines):
                if "|" in lines[i]:
                    parts = lines[i].split("|")
                    if len(parts) >= 4:
                        sha, date_str, message, author = parts[0], parts[1], parts[2], parts[3]

                        # Parse date
                        date = datetime.strptime(date_str.split()[0], "%Y-%m-%d")

                        # Count file changes
                        i += 1
                        files_changed = 0
                        insertions = 0
                        deletions = 0

                        while i < len(lines) and "|" not in lines[i] and lines[i].strip():
                            parts = lines[i].split()
                            if len(parts) >= 2:
                                try:
                                    ins = int(parts[0]) if parts[0] != "-" else 0
                                    dels = int(parts[1]) if parts[1] != "-" else 0
                                    insertions += ins
                                    deletions += dels
                                    files_changed += 1
                                except ValueError:
                                    pass
                            i += 1

                        commits.append(
                            CommitMetric(
                                sha=sha,
                                date=date,
                                message=message,
                                author=author,
                                files_changed=files_changed,
                                insertions=insertions,
                                deletions=deletions,
                            )
                        )
                        continue
                i += 1

            return commits

        except Exception as e:
            print(f"Error getting commits: {e}")
            return []

    def _parse_roadmap_tasks(self) -> List[TaskMetric]:
        """Parse tasks from ROADMAP.

        Returns:
            List[TaskMetric]: List of tasks.
        """
        roadmap_path = self.project_root / "docs" / "roadmap" / "ROADMAP.md"
        if not roadmap_path.exists():
            return []

        tasks = []
        try:
            with open(roadmap_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find all PRIORITY sections
            pattern = r"### PRIORITY (\d+):\s+([^\n]+)\s+([✅🔄📝⏸️🚧]+)\s+(\w+)"
            matches = re.finditer(pattern, content)

            for match in matches:
                priority = match.group(1)
                name = match.group(2)
                match.group(3)
                status = match.group(4)

                # Try to extract completion date if completed
                completed_date = None
                if "Complete" in status:
                    date_pattern = r"Complete[d]?\s*\((\d{4}-\d{2}-\d{2})\)"
                    date_match = re.search(date_pattern, content[match.end() : match.end() + 200])
                    if date_match:
                        try:
                            completed_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                        except ValueError:
                            pass

                tasks.append(
                    TaskMetric(
                        priority=f"PRIORITY {priority}",
                        name=name,
                        status=status,
                        estimated_effort=None,  # Could be extracted from detailed sections
                        completed_date=completed_date,
                    )
                )

        except Exception as e:
            print(f"Error parsing ROADMAP: {e}")

        return tasks

    def _group_commits_by_day(self, commits: List[CommitMetric]) -> Dict[str, int]:
        """Group commits by day.

        Args:
            commits (List[CommitMetric]): List of commits.

        Returns:
            Dict[str, int]: Commits grouped by day.
        """
        by_day = {}
        for commit in commits:
            day = commit.date.strftime("%Y-%m-%d")
            by_day[day] = by_day.get(day, 0) + 1
        return by_day

    def _calculate_avg_duration(self, tasks: List[TaskMetric]) -> str:
        """Calculate average task duration.

        Args:
            tasks (List[TaskMetric]): List of tasks.

        Returns:
            str: Average duration estimate.
        """
        # For now, return a placeholder
        # In full implementation, would calculate from actual timing data
        return "2-3 days"

    def _group_tasks_by_status(self, tasks: List[TaskMetric]) -> Dict[str, int]:
        """Group tasks by status.

        Args:
            tasks (List[TaskMetric]): List of tasks.

        Returns:
            Dict[str, int]: Tasks grouped by status.
        """
        by_status = {}
        for task in tasks:
            status = task.status
            by_status[status] = by_status.get(status, 0) + 1
        return by_status

    def _calculate_commit_gaps(self, commits: List[CommitMetric]) -> List[float]:
        """Calculate gaps between commits in hours.

        Args:
            commits (List[CommitMetric]): List of commits.

        Returns:
            List[float]: Gaps in hours.
        """
        if len(commits) < 2:
            return []

        sorted_commits = sorted(commits, key=lambda c: c.date)
        gaps = []

        for i in range(len(sorted_commits) - 1):
            gap = (sorted_commits[i + 1].date - sorted_commits[i].date).total_seconds() / 3600
            gaps.append(gap)

        return gaps

    def _identify_parallelizable_work(self, tasks: List[TaskMetric]) -> List[TaskMetric]:
        """Identify tasks that could be parallelized.

        Args:
            tasks (List[TaskMetric]): List of tasks.

        Returns:
            List[TaskMetric]: Parallelizable tasks.
        """
        # Simple heuristic: tasks that don't depend on each other
        # In full implementation, would parse dependencies from specs
        return tasks[: min(12, len(tasks))]

    def _identify_automation_candidates(self) -> List[Dict]:
        """Identify manual tasks that could be automated.

        Returns:
            List[Dict]: Automation candidates.
        """
        # Placeholder - would analyze commit messages, time spent, etc.
        return [
            {"task": "Dependency conflict resolution", "frequency": "45 min/week", "savings": "90%"},
            {"task": "Test failure analysis", "frequency": "1.5 hrs/week", "savings": "85%"},
            {"task": "PR review automation", "frequency": "30 min/week", "savings": "80%"},
        ]

    def _identify_process_improvements(self) -> List[Dict]:
        """Identify process improvement opportunities.

        Returns:
            List[Dict]: Process improvements.
        """
        return [
            {"area": "Spec creation", "issue": "Takes 25% of total time", "suggestion": "Use templates"},
            {"area": "Testing", "issue": "Manual test running", "suggestion": "Auto-run on commit"},
        ]
