"""Slack configuration management.

This module handles Slack integration configuration from environment variables.

Environment Variables:
    SLACK_BOT_TOKEN: Bot User OAuth Token (xoxb-...)
    SLACK_CHANNEL_ID: Channel ID (C123456789)
    SLACK_ENABLED: Enable/disable integration (default: false)
    SLACK_DAILY_SUMMARY_TIME: Daily summary time HH:MM (default: 18:00)
    SLACK_RATE_LIMIT: Rate limit in messages/second (default: 1.0)
    SLACK_MAX_RETRIES: Max retry attempts (default: 3)

Example:
    >>> config = SlackConfig.from_env()
    >>> if config.enabled and config.is_configured():
    ...     print(f"Slack enabled for channel: {config.channel_id}")
"""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SlackConfig:
    """Slack integration configuration.

    Attributes:
        bot_token: Slack Bot User OAuth Token (xoxb-...)
        channel_id: Slack Channel ID (C123456789)
        enabled: Whether Slack integration is enabled
        daily_summary_time: Time for daily summary in HH:MM format
        rate_limit: Max messages per second (default: 1.0)
        max_retries: Max retry attempts for failed messages (default: 3)
    """

    bot_token: str = ""
    channel_id: str = ""
    enabled: bool = False
    daily_summary_time: str = "18:00"
    rate_limit: float = 1.0
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "SlackConfig":
        """Load configuration from environment variables.

        Returns:
            SlackConfig instance with values from environment

        Example:
            >>> config = SlackConfig.from_env()
            >>> print(f"Enabled: {config.enabled}")
        """
        enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"
        bot_token = os.getenv("SLACK_BOT_TOKEN", "")
        channel_id = os.getenv("SLACK_CHANNEL_ID", "")
        daily_summary_time = os.getenv("SLACK_DAILY_SUMMARY_TIME", "18:00")

        # Parse numeric values with defaults
        try:
            rate_limit = float(os.getenv("SLACK_RATE_LIMIT", "1.0"))
        except ValueError:
            logger.warning("Invalid SLACK_RATE_LIMIT, using default: 1.0")
            rate_limit = 1.0

        try:
            max_retries = int(os.getenv("SLACK_MAX_RETRIES", "3"))
        except ValueError:
            logger.warning("Invalid SLACK_MAX_RETRIES, using default: 3")
            max_retries = 3

        config = cls(
            bot_token=bot_token,
            channel_id=channel_id,
            enabled=enabled,
            daily_summary_time=daily_summary_time,
            rate_limit=rate_limit,
            max_retries=max_retries,
        )

        logger.debug(f"Loaded Slack config: enabled={enabled}, channel={channel_id}")

        return config

    def validate(self):
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid

        Example:
            >>> config = SlackConfig.from_env()
            >>> config.validate()  # Raises ValueError if invalid
        """
        if self.enabled:
            if not self.bot_token:
                raise ValueError("SLACK_BOT_TOKEN is required when SLACK_ENABLED=true")

            if not self.bot_token.startswith("xoxb-"):
                raise ValueError("SLACK_BOT_TOKEN must start with 'xoxb-'")

            if not self.channel_id:
                raise ValueError("SLACK_CHANNEL_ID is required when SLACK_ENABLED=true")

            if not self.channel_id.startswith("C"):
                raise ValueError("SLACK_CHANNEL_ID must start with 'C' (e.g., C123456789)")

            # Validate daily summary time format (HH:MM)
            try:
                hours, minutes = self.daily_summary_time.split(":")
                h = int(hours)
                m = int(minutes)
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    raise ValueError
            except (ValueError, AttributeError):
                raise ValueError(f"SLACK_DAILY_SUMMARY_TIME must be in HH:MM format (got: {self.daily_summary_time})")

            # Validate rate limit
            if self.rate_limit <= 0:
                raise ValueError(f"SLACK_RATE_LIMIT must be > 0 (got: {self.rate_limit})")

            # Validate max retries
            if self.max_retries < 0:
                raise ValueError(f"SLACK_MAX_RETRIES must be >= 0 (got: {self.max_retries})")

        logger.info("Slack configuration validated successfully")

    def is_configured(self) -> bool:
        """Check if Slack is properly configured.

        Returns:
            True if bot_token and channel_id are set, False otherwise

        Example:
            >>> config = SlackConfig.from_env()
            >>> if config.is_configured():
            ...     print("Ready to send notifications")
        """
        return bool(self.bot_token and self.channel_id)
