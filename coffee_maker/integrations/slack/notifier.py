"""High-level Slack notification dispatcher.

This module provides the main interface for sending Slack notifications.
All daemon and system events should use the SlackNotifier class.

Features:
- Auto-formatting based on notification type
- Graceful degradation if Slack unavailable
- Fallback to NotificationDB
- Configuration-driven (SLACK_ENABLED)

Example:
    >>> from coffee_maker.integrations.slack import SlackNotifier
    >>> notifier = SlackNotifier()
    >>> notifier.notify_daemon_started()
    >>> notifier.notify_priority_completed(
    ...     priority_name="US-034",
    ...     summary="Slack integration implemented",
    ...     duration_hours=8.5
    ... )
"""

import logging
from typing import Dict, List, Optional

from coffee_maker.integrations.slack.client import SlackClient
from coffee_maker.integrations.slack.config import SlackConfig
from coffee_maker.integrations.slack.formatters import (
    DaemonLifecycleFormatter,
    DailySummaryFormatter,
    PRStatusFormatter,
    PriorityCompletionFormatter,
    SystemAlertFormatter,
)

logger = logging.getLogger(__name__)


class SlackNotifier:
    """High-level notification dispatcher for Slack.

    This is the primary interface for sending Slack notifications.
    All daemon and system events should use this class.

    The notifier handles:
    - Configuration validation
    - Message formatting
    - Sending via SlackClient
    - Graceful degradation if Slack unavailable
    - Fallback to NotificationDB

    Attributes:
        config: Slack configuration
        client: Slack API client (None if disabled)

    Example:
        >>> notifier = SlackNotifier()
        >>> if notifier.is_enabled():
        ...     notifier.notify_daemon_started()
    """

    def __init__(self, config: Optional[SlackConfig] = None):
        """Initialize Slack notifier.

        Args:
            config: Slack configuration (defaults to env vars)
        """
        self.config = config or SlackConfig.from_env()
        self.client: Optional[SlackClient] = None

        # Initialize client if Slack is enabled and configured
        if self.config.enabled and self.config.is_configured():
            try:
                self.config.validate()
                self.client = SlackClient(
                    bot_token=self.config.bot_token,
                    channel_id=self.config.channel_id,
                    rate_limit=self.config.rate_limit,
                    max_retries=self.config.max_retries,
                )
                logger.info("SlackNotifier initialized and enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Slack client: {e} - disabling")
                self.config.enabled = False
        else:
            logger.debug("SlackNotifier initialized but disabled")

    def is_enabled(self) -> bool:
        """Check if Slack notifications are enabled.

        Returns:
            True if enabled and configured, False otherwise
        """
        return self.config.enabled and self.client is not None

    # =========================================================================
    # Daemon Lifecycle Notifications
    # =========================================================================

    def notify_daemon_started(self, branch: str = "roadmap", next_priority: Optional[str] = None) -> bool:
        """Notify that daemon has started.

        Args:
            branch: Current git branch
            next_priority: Next priority to implement

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_daemon_started(
            ...     branch="roadmap",
            ...     next_priority="US-034"
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping daemon_started notification")
            return False

        try:
            blocks = DaemonLifecycleFormatter.format_start(branch=branch, next_priority=next_priority)
            return self._send_message(text="🚀 Daemon Started", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send daemon_started notification: {e}")
            self._fallback_to_db(
                type="info",
                title="Daemon Started",
                message=f"Branch: {branch}, Next: {next_priority}",
            )
            return False

    def notify_daemon_stopped(self, runtime_hours: Optional[float] = None, priorities_completed: int = 0) -> bool:
        """Notify that daemon has stopped gracefully.

        Args:
            runtime_hours: Total runtime in hours
            priorities_completed: Number of priorities completed

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_daemon_stopped(
            ...     runtime_hours=4.25,
            ...     priorities_completed=2
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping daemon_stopped notification")
            return False

        try:
            blocks = DaemonLifecycleFormatter.format_stop(
                runtime_hours=runtime_hours, priorities_completed=priorities_completed
            )
            return self._send_message(text="🛑 Daemon Stopped", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send daemon_stopped notification: {e}")
            self._fallback_to_db(
                type="info",
                title="Daemon Stopped",
                message=f"Runtime: {runtime_hours}h, Completed: {priorities_completed}",
            )
            return False

    def notify_daemon_error(self, error: Exception, context: Optional[Dict] = None) -> bool:
        """Notify about daemon error or crash.

        Args:
            error: Exception that occurred
            context: Additional context (priority, action, etc.)

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_daemon_error(
            ...     error=ConnectionError("API timeout"),
            ...     context={"priority": "US-034", "action": "implementing"}
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping daemon_error notification")
            return False

        try:
            blocks = DaemonLifecycleFormatter.format_error(error=error, context=context)
            return self._send_message(text=f"🚨 Daemon Error: {type(error).__name__}", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send daemon_error notification: {e}")
            self._fallback_to_db(
                type="error",
                title="Daemon Error",
                message=f"{type(error).__name__}: {str(error)}",
            )
            return False

    # =========================================================================
    # Priority Completion Notifications
    # =========================================================================

    def notify_priority_completed(
        self,
        priority_name: str,
        summary: str,
        duration_hours: float,
        files_changed: int = 0,
        tests_added: int = 0,
        lines_added: int = 0,
        lines_deleted: int = 0,
    ) -> bool:
        """Notify about completed priority.

        Args:
            priority_name: Priority identifier (e.g., "US-034")
            summary: Brief summary of what was completed
            duration_hours: Time taken in hours
            files_changed: Number of files modified
            tests_added: Number of tests added
            lines_added: Lines of code added
            lines_deleted: Lines of code deleted

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_priority_completed(
            ...     priority_name="US-034",
            ...     summary="Implemented Slack Bot integration...",
            ...     duration_hours=8.5,
            ...     files_changed=12,
            ...     tests_added=25,
            ...     lines_added=847,
            ...     lines_deleted=23
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping priority_completed notification")
            return False

        try:
            blocks = PriorityCompletionFormatter.format(
                priority_name=priority_name,
                summary=summary,
                duration_hours=duration_hours,
                files_changed=files_changed,
                tests_added=tests_added,
                lines_added=lines_added,
                lines_deleted=lines_deleted,
            )
            return self._send_message(text=f"✅ Priority Completed: {priority_name}", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send priority_completed notification: {e}")
            self._fallback_to_db(
                type="completion",
                title=f"Priority Completed: {priority_name}",
                message=summary,
            )
            return False

    # =========================================================================
    # PR Status Notifications
    # =========================================================================

    def notify_pr_created(self, pr_number: int, pr_url: str, title: str, branch: str) -> bool:
        """Notify about new PR creation.

        Args:
            pr_number: PR number
            pr_url: Full PR URL
            title: PR title
            branch: Source branch name

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_pr_created(
            ...     pr_number=142,
            ...     pr_url="https://github.com/user/repo/pull/142",
            ...     title="feat: Implement US-034 - Slack Integration",
            ...     branch="feature/us-034-slack-integration"
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping pr_created notification")
            return False

        try:
            blocks = PRStatusFormatter.format_created(pr_number=pr_number, pr_url=pr_url, title=title, branch=branch)
            return self._send_message(text=f"📝 PR Created: #{pr_number}", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send pr_created notification: {e}")
            self._fallback_to_db(
                type="info",
                title=f"PR Created: #{pr_number}",
                message=f"{title}\nBranch: {branch}\nURL: {pr_url}",
            )
            return False

    def notify_pr_merged(self, pr_number: int, pr_url: str, title: str) -> bool:
        """Notify about PR merge.

        Args:
            pr_number: PR number
            pr_url: Full PR URL
            title: PR title

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_pr_merged(
            ...     pr_number=142,
            ...     pr_url="https://github.com/user/repo/pull/142",
            ...     title="feat: Implement US-034 - Slack Integration"
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping pr_merged notification")
            return False

        try:
            blocks = PRStatusFormatter.format_merged(pr_number=pr_number, pr_url=pr_url, title=title)
            return self._send_message(text=f"✅ PR Merged: #{pr_number}", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send pr_merged notification: {e}")
            self._fallback_to_db(
                type="info",
                title=f"PR Merged: #{pr_number}",
                message=f"{title}\nURL: {pr_url}",
            )
            return False

    def notify_ci_failure(self, pr_number: int, pr_url: str, title: str, failure_details: str) -> bool:
        """Notify about CI/CD failure.

        Args:
            pr_number: PR number
            pr_url: Full PR URL
            title: PR title
            failure_details: Details about failed tests/checks

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_ci_failure(
            ...     pr_number=142,
            ...     pr_url="https://github.com/user/repo/pull/142",
            ...     title="feat: Implement US-034 - Slack Integration",
            ...     failure_details="test_slack_client.py::test_post_message FAILED"
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping ci_failure notification")
            return False

        try:
            blocks = PRStatusFormatter.format_ci_failure(
                pr_number=pr_number,
                pr_url=pr_url,
                title=title,
                failure_details=failure_details,
            )
            return self._send_message(text=f"❌ CI Failure: PR #{pr_number}", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send ci_failure notification: {e}")
            self._fallback_to_db(
                type="error",
                title=f"CI Failure: PR #{pr_number}",
                message=f"{title}\n\nDetails:\n{failure_details}",
            )
            return False

    # =========================================================================
    # System Alerts
    # =========================================================================

    def notify_system_alert(self, level: str, title: str, message: str, context: Optional[Dict] = None) -> bool:
        """Notify about system alerts.

        Args:
            level: Alert level ("warning" or "error")
            title: Alert title
            message: Alert message
            context: Additional context

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.notify_system_alert(
            ...     level="warning",
            ...     title="Rate limit approaching",
            ...     message="Slack API rate limit at 80% capacity",
            ...     context={"action": "Throttling notifications"}
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping system_alert notification")
            return False

        try:
            blocks = SystemAlertFormatter.format(level=level, title=title, message=message, context=context)
            emoji = "🚨" if level == "error" else "⚠️"
            return self._send_message(text=f"{emoji} System {level.title()}: {title}", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send system_alert notification: {e}")
            self._fallback_to_db(
                type=level,
                title=f"System {level.title()}: {title}",
                message=message,
            )
            return False

    # =========================================================================
    # Daily Summary
    # =========================================================================

    def send_daily_summary(
        self,
        date: str,
        priorities_completed: int,
        prs_created: int,
        prs_merged: int,
        velocity: float,
        blockers: List[str],
        system_health: str = "✅ Healthy",
    ) -> bool:
        """Send daily progress summary.

        Args:
            date: Date in YYYY-MM-DD format
            priorities_completed: Number of priorities completed
            prs_created: Number of PRs created
            prs_merged: Number of PRs merged
            velocity: Priorities per day
            blockers: List of current blockers
            system_health: Overall system health status

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> notifier.send_daily_summary(
            ...     date="2025-10-15",
            ...     priorities_completed=2,
            ...     prs_created=3,
            ...     prs_merged=1,
            ...     velocity=1.8,
            ...     blockers=["US-035: Waiting for API access"],
            ...     system_health="✅ Healthy"
            ... )
            True
        """
        if not self.is_enabled():
            logger.debug("Slack disabled - skipping daily_summary notification")
            return False

        try:
            blocks = DailySummaryFormatter.format(
                date=date,
                priorities_completed=priorities_completed,
                prs_created=prs_created,
                prs_merged=prs_merged,
                velocity=velocity,
                blockers=blockers,
                system_health=system_health,
            )
            return self._send_message(text=f"📈 Daily Summary - {date}", blocks=blocks)
        except Exception as e:
            logger.error(f"Failed to send daily_summary notification: {e}")
            self._fallback_to_db(
                type="info",
                title=f"Daily Summary - {date}",
                message=f"Completed: {priorities_completed}, PRs: {prs_created}/{prs_merged}, Velocity: {velocity}",
            )
            return False

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _send_message(self, text: str, blocks: List[Dict]) -> bool:
        """Internal method to send message via SlackClient.

        Args:
            text: Plain text fallback
            blocks: Slack Block Kit blocks

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            logger.warning("Slack client not initialized")
            return False

        try:
            success = self.client.post_message(text=text, blocks=blocks)

            if success:
                logger.info(f"Sent Slack notification: {text[:50]}")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {text[:50]}")
                return False

        except Exception as e:
            logger.error(f"Exception sending Slack notification: {e}")
            return False

    def _fallback_to_db(self, type: str, title: str, message: str):
        """Fallback to NotificationDB if Slack fails.

        Args:
            type: Notification type
            title: Notification title
            message: Notification message
        """
        try:
            from coffee_maker.cli.notifications import NotificationDB

            db = NotificationDB()
            db.create_notification(
                type=type,
                title=f"[Slack Failed] {title}",
                message=message,
                priority="normal",
                play_sound=False,  # Already attempted via Slack
            )
            logger.info(f"Fallback notification created in DB: {title}")
        except Exception as e:
            logger.error(f"Failed to create fallback notification in DB: {e}")
