"""Slack message formatters using Block Kit.

This module provides formatters for converting event data into Slack Block Kit structures.
Each formatter creates rich, well-formatted messages for different notification types.

Block Kit Reference: https://api.slack.com/block-kit

Example:
    >>> from coffee_maker.integrations.slack.formatters import DaemonLifecycleFormatter
    >>> blocks = DaemonLifecycleFormatter.format_start()
    >>> # Returns Slack Block Kit blocks for daemon start notification
"""

from datetime import datetime
from typing import Dict, List, Optional


class DaemonLifecycleFormatter:
    """Format daemon lifecycle events (start, stop, error)."""

    @staticmethod
    def format_start(branch: str = "roadmap", next_priority: Optional[str] = None) -> List[Dict]:
        """Format daemon start notification.

        Args:
            branch: Current git branch
            next_priority: Next priority to implement

        Returns:
            Slack Block Kit blocks

        Example Output:
            🚀 Daemon Started
            ──────────────────
            Status: Running
            Time: 2025-10-15 14:30:00 UTC
            Branch: roadmap
            Next Priority: US-034
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🚀 Daemon Started"}},
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Status:*\nRunning"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{timestamp}"},
                    {"type": "mrkdwn", "text": f"*Branch:*\n`{branch}`"},
                ],
            },
        ]

        if next_priority:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Next Priority:* {next_priority}",
                    },
                }
            )

        return blocks

    @staticmethod
    def format_stop(runtime_hours: Optional[float] = None, priorities_completed: int = 0) -> List[Dict]:
        """Format daemon stop notification.

        Args:
            runtime_hours: Total runtime in hours
            priorities_completed: Number of priorities completed

        Returns:
            Slack Block Kit blocks

        Example Output:
            🛑 Daemon Stopped
            ──────────────────
            Status: Graceful shutdown
            Time: 2025-10-15 18:45:00 UTC
            Runtime: 4.25 hours
            Priorities Completed: 2
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        fields = [
            {"type": "mrkdwn", "text": "*Status:*\nGraceful shutdown"},
            {"type": "mrkdwn", "text": f"*Time:*\n{timestamp}"},
        ]

        if runtime_hours is not None:
            fields.append({"type": "mrkdwn", "text": f"*Runtime:*\n{runtime_hours:.2f} hours"})

        fields.append({"type": "mrkdwn", "text": f"*Priorities Completed:*\n{priorities_completed}"})

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🛑 Daemon Stopped"}},
            {"type": "divider"},
            {"type": "section", "fields": fields},
        ]

        return blocks

    @staticmethod
    def format_error(error: Exception, context: Optional[Dict] = None) -> List[Dict]:
        """Format daemon error notification.

        Args:
            error: Exception that occurred
            context: Additional context (priority, action, etc.)

        Returns:
            Slack Block Kit blocks

        Example Output:
            🚨 Daemon Error
            ────────────────
            Error: ConnectionError
            Message: Failed to connect to Claude API
            Time: 2025-10-15 16:22:00 UTC
            Context: Implementing US-034
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        error_type = type(error).__name__
        error_message = str(error)

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🚨 Daemon Error"}},
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Error:*\n`{error_type}`"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{timestamp}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Message:*\n```{error_message}```"},
            },
        ]

        if context:
            context_text = "\n".join([f"• *{k}:* {v}" for k, v in context.items()])
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Context:*\n{context_text}"},
                }
            )

        return blocks


class PriorityCompletionFormatter:
    """Format priority completion events."""

    @staticmethod
    def format(
        priority_name: str,
        summary: str,
        duration_hours: float,
        files_changed: int = 0,
        tests_added: int = 0,
        lines_added: int = 0,
        lines_deleted: int = 0,
    ) -> List[Dict]:
        """Format priority completion notification.

        Args:
            priority_name: Priority identifier (e.g., "US-034")
            summary: Brief summary of what was completed
            duration_hours: Time taken in hours
            files_changed: Number of files modified
            tests_added: Number of tests added
            lines_added: Lines of code added
            lines_deleted: Lines of code deleted

        Returns:
            Slack Block Kit blocks

        Example Output:
            ✅ Priority Completed: US-034
            ────────────────────────────
            Slack Integration for Notifications

            📊 Metrics:
            • Duration: 8.5 hours
            • Files Changed: 12
            • Tests Added: 25
            • Lines: +847 / -23

            Summary: Implemented Slack Bot integration...
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"✅ Priority Completed: {priority_name}",
                },
            },
            {"type": "divider"},
        ]

        # Metrics section
        metrics_text = (
            f"*📊 Metrics:*\n"
            f"• *Duration:* {duration_hours:.1f} hours\n"
            f"• *Files Changed:* {files_changed}\n"
            f"• *Tests Added:* {tests_added}\n"
            f"• *Lines:* +{lines_added} / -{lines_deleted}"
        )
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": metrics_text}})

        # Summary section
        if summary:
            summary_truncated = summary[:500] + "..." if len(summary) > 500 else summary
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{summary_truncated}",
                    },
                }
            )

        return blocks


class PRStatusFormatter:
    """Format PR status events (created, merged, CI failure)."""

    @staticmethod
    def format_created(
        pr_number: int,
        pr_url: str,
        title: str,
        branch: str,
    ) -> List[Dict]:
        """Format PR creation notification.

        Args:
            pr_number: PR number
            pr_url: Full PR URL
            title: PR title
            branch: Source branch name

        Returns:
            Slack Block Kit blocks

        Example Output:
            📝 PR Created: #142
            ───────────────────
            feat: Implement US-034 - Slack Integration

            Branch: feature/us-034-slack-integration
            Status: Awaiting review

            [View PR Button]
        """
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📝 PR Created: #{pr_number}"},
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Branch:*\n`{branch}`"},
                    {"type": "mrkdwn", "text": "*Status:*\nAwaiting review"},
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View PR"},
                        "url": pr_url,
                        "action_id": "view_pr",
                    }
                ],
            },
        ]

        return blocks

    @staticmethod
    def format_merged(pr_number: int, pr_url: str, title: str) -> List[Dict]:
        """Format PR merge notification.

        Args:
            pr_number: PR number
            pr_url: Full PR URL
            title: PR title

        Returns:
            Slack Block Kit blocks

        Example Output:
            ✅ PR Merged: #142
            ──────────────────
            feat: Implement US-034 - Slack Integration

            Time: 2025-10-15 17:30:00 UTC
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"✅ PR Merged: #{pr_number}"},
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Time:* {timestamp}"},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View PR"},
                        "url": pr_url,
                        "action_id": "view_pr",
                    }
                ],
            },
        ]

        return blocks

    @staticmethod
    def format_ci_failure(pr_number: int, pr_url: str, title: str, failure_details: str) -> List[Dict]:
        """Format CI failure notification.

        Args:
            pr_number: PR number
            pr_url: Full PR URL
            title: PR title
            failure_details: Details about failed tests/checks

        Returns:
            Slack Block Kit blocks

        Example Output:
            ❌ CI Failure: PR #142
            ───────────────────────
            feat: Implement US-034 - Slack Integration

            Failed Tests:
            • test_slack_client.py::test_post_message
            • test_slack_notifier.py::test_daemon_started

            [View Logs Button]
        """
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"❌ CI Failure: PR #{pr_number}"},
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Failed Tests/Checks:*\n```{failure_details}```",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Logs"},
                        "url": pr_url,
                        "action_id": "view_logs",
                        "style": "danger",
                    }
                ],
            },
        ]

        return blocks


class SystemAlertFormatter:
    """Format system alerts (warnings and errors)."""

    @staticmethod
    def format(
        level: str,
        title: str,
        message: str,
        context: Optional[Dict] = None,
    ) -> List[Dict]:
        """Format system alert notification.

        Args:
            level: Alert level ("warning" or "error")
            title: Alert title
            message: Alert message
            context: Additional context

        Returns:
            Slack Block Kit blocks

        Example Output:
            ⚠️ System Warning
            ──────────────────
            Title: Rate limit approaching
            Message: Slack API rate limit at 80% capacity
            Time: 2025-10-15 15:45:00 UTC
            Action: Throttling notifications
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        if level == "error":
            emoji = "🚨"
            header = "System Error"
        else:
            emoji = "⚠️"
            header = "System Warning"

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} {header}"}},
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Title:*\n{title}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{timestamp}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Message:*\n{message}"},
            },
        ]

        if context:
            context_text = "\n".join([f"• *{k}:* {v}" for k, v in context.items()])
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Context:*\n{context_text}"},
                }
            )

        return blocks


class DailySummaryFormatter:
    """Format daily progress summaries."""

    @staticmethod
    def format(
        date: str,
        priorities_completed: int,
        prs_created: int,
        prs_merged: int,
        velocity: float,
        blockers: List[str],
        system_health: str = "✅ Healthy",
    ) -> List[Dict]:
        """Format daily summary notification.

        Args:
            date: Date in YYYY-MM-DD format
            priorities_completed: Number of priorities completed
            prs_created: Number of PRs created
            prs_merged: Number of PRs merged
            velocity: Priorities per day
            blockers: List of current blockers
            system_health: Overall system health status

        Returns:
            Slack Block Kit blocks

        Example Output:
            📈 Daily Summary - October 15, 2025
            ───────────────────────────────────

            🎯 Priorities Completed: 2
            📝 PRs Created: 3
            ✅ PRs Merged: 1
            ⚡ Velocity: 1.8 priorities/day

            🚧 Blockers:
            • US-035: Waiting for API access
            • US-040: Needs architectural review

            📊 System Health: ✅ Healthy
        """
        # Parse date for better formatting
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except ValueError:
            formatted_date = date

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📈 Daily Summary - {formatted_date}"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"🎯 *Priorities Completed:*\n{priorities_completed}"},
                    {"type": "mrkdwn", "text": f"📝 *PRs Created:*\n{prs_created}"},
                    {"type": "mrkdwn", "text": f"✅ *PRs Merged:*\n{prs_merged}"},
                    {"type": "mrkdwn", "text": f"⚡ *Velocity:*\n{velocity:.1f} priorities/day"},
                ],
            },
        ]

        # Blockers section
        if blockers:
            blockers_text = "\n".join([f"• {blocker}" for blocker in blockers])
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🚧 Blockers ({len(blockers)}):*\n{blockers_text}",
                    },
                }
            )
        else:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*🚧 Blockers:* None"},
                }
            )

        # System health
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*📊 System Health:* {system_health}"},
            }
        )

        return blocks
