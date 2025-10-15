"""Slack integration for MonolithicCoffeeMakerAgent.

This package provides real-time Slack notifications for:
- Daemon lifecycle events (start, stop, errors)
- Priority completion notifications
- PR status updates
- System alerts
- Daily progress summaries

Usage:
    >>> from coffee_maker.integrations.slack import SlackNotifier
    >>> notifier = SlackNotifier()
    >>> notifier.notify_daemon_started()

Configuration:
    Set environment variables:
    - SLACK_ENABLED=true
    - SLACK_BOT_TOKEN=xoxb-...
    - SLACK_CHANNEL_ID=C123456789

Reference:
    - Technical Spec: docs/US_034_SLACK_INTEGRATION_TECHNICAL_SPEC.md
    - Setup Guide: See README.md
"""

from coffee_maker.integrations.slack.config import SlackConfig
from coffee_maker.integrations.slack.notifier import SlackNotifier
from coffee_maker.integrations.slack.scheduler import (
    DailySummaryScheduler,
    trigger_daily_summary_now,
)

__all__ = [
    "SlackConfig",
    "SlackNotifier",
    "DailySummaryScheduler",
    "trigger_daily_summary_now",
]
