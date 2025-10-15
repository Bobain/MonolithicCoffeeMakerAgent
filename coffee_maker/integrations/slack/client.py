"""Slack API client with retry logic and rate limiting.

This module provides a low-level wrapper around the Slack API with:
- Rate limiting (1 message per second)
- Exponential backoff retry logic
- Connection validation
- Comprehensive error handling

Example:
    >>> from coffee_maker.integrations.slack.client import SlackClient
    >>> client = SlackClient(bot_token="xoxb-...", channel_id="C123456")
    >>> client.post_message(
    ...     text="Daemon started",
    ...     blocks=[{"type": "section", "text": {...}}]
    ... )
    True
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackClient:
    """Low-level Slack API client with retry logic and rate limiting.

    This class wraps the official Slack SDK with additional features:
    - Automatic rate limiting (1 message/second)
    - Exponential backoff retry (configurable attempts)
    - Connection testing
    - Error handling and logging

    Attributes:
        client: Slack WebClient instance
        channel_id: Default channel ID for messages
        rate_limit: Max messages per second
        max_retries: Max retry attempts for failed messages
        last_message_time: Timestamp of last message (for rate limiting)

    Example:
        >>> client = SlackClient(
        ...     bot_token="xoxb-1234567890-...",
        ...     channel_id="C123456789"
        ... )
        >>> success = client.post_message(
        ...     text="Test notification",
        ...     blocks=[...]
        ... )
    """

    def __init__(
        self,
        bot_token: str,
        channel_id: str,
        rate_limit: float = 1.0,
        max_retries: int = 3,
    ):
        """Initialize Slack client.

        Args:
            bot_token: Slack Bot User OAuth Token (xoxb-...)
            channel_id: Default channel ID (C123456789)
            rate_limit: Max messages per second (default: 1.0)
            max_retries: Max retry attempts (default: 3)
        """
        self.client = WebClient(token=bot_token)
        self.channel_id = channel_id
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.last_message_time = 0.0

        logger.debug(
            f"SlackClient initialized: channel={channel_id}, " f"rate_limit={rate_limit}, max_retries={max_retries}"
        )

    def post_message(
        self,
        text: str,
        blocks: Optional[List[Dict]] = None,
        channel: Optional[str] = None,
        thread_ts: Optional[str] = None,
    ) -> bool:
        """Post message to Slack with retry logic.

        This method:
        1. Enforces rate limiting
        2. Posts message to Slack
        3. Retries with exponential backoff if failed

        Args:
            text: Plain text fallback message
            blocks: Slack Block Kit blocks for rich formatting
            channel: Override default channel (optional)
            thread_ts: Thread timestamp for reply (optional)

        Returns:
            True if message sent successfully, False otherwise

        Example:
            >>> client.post_message(
            ...     text="Daemon started",
            ...     blocks=[{
            ...         "type": "header",
            ...         "text": {"type": "plain_text", "text": "🚀 Daemon Started"}
            ...     }]
            ... )
            True
        """
        target_channel = channel or self.channel_id

        # Enforce rate limiting
        self._check_rate_limit()

        def _send():
            """Inner function for retry wrapper."""
            response = self.client.chat_postMessage(
                channel=target_channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts,
            )
            return response

        try:
            response = self._retry_with_backoff(_send)

            if response.get("ok"):
                logger.info(f"Sent Slack message to #{target_channel}: {text[:50]}...")
                return True
            else:
                logger.error(f"Slack API returned ok=False: {response.get('error', 'unknown error')}")
                return False

        except SlackApiError as e:
            logger.error(f"Slack API error after {self.max_retries} attempts: " f"{e.response['error']} - {text[:50]}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error posting to Slack: {e} - {text[:50]}")
            return False

    def _check_rate_limit(self):
        """Enforce rate limiting (1 message per second by default).

        This method tracks the time since the last message and sleeps
        if necessary to avoid exceeding the rate limit.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_message_time

        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        self.last_message_time = time.time()

    def _retry_with_backoff(self, func: Callable, max_attempts: Optional[int] = None) -> Any:
        """Retry function with exponential backoff.

        Backoff strategy:
            Attempt 1: Immediate
            Attempt 2: Wait 2 seconds
            Attempt 3: Wait 4 seconds
            ...

        Args:
            func: Function to retry
            max_attempts: Override max_retries (optional)

        Returns:
            Function result if successful

        Raises:
            SlackApiError: If all attempts fail
        """
        attempts = max_attempts or self.max_retries

        for attempt in range(attempts):
            try:
                return func()

            except SlackApiError as e:
                error_code = e.response.get("error", "unknown")

                # Calculate wait time
                if error_code == "rate_limited":
                    # Rate limited - wait longer
                    wait_time = 2 ** (attempt + 2)  # 4, 8, 16 seconds
                else:
                    # Other errors - exponential backoff
                    wait_time = 2**attempt if attempt > 0 else 0  # 0, 2, 4 seconds

                if attempt < attempts - 1:
                    logger.warning(
                        f"Slack API error (attempt {attempt + 1}/{attempts}): "
                        f"{error_code} - retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Slack API failed after {attempts} attempts: {error_code}")
                    raise

            except Exception as e:
                logger.error(f"Unexpected error during retry: {e}")
                raise

    def test_connection(self) -> bool:
        """Test Slack connection and permissions.

        This method:
        1. Tests authentication
        2. Attempts to post a test message
        3. Returns success/failure status

        Returns:
            True if connection successful, False otherwise

        Example:
            >>> if client.test_connection():
            ...     print("Slack connection verified")
        """
        try:
            # Test authentication
            auth_response = self.client.auth_test()
            logger.info(f"Slack auth successful: {auth_response.get('user', 'unknown')}")

            # Test posting to channel
            test_message = "✅ Slack integration test successful"
            test_blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *Connection verified*\nSlack integration is working correctly.",
                    },
                }
            ]

            success = self.post_message(text=test_message, blocks=test_blocks)

            if success:
                logger.info(f"Slack connection test passed for channel: {self.channel_id}")
                return True
            else:
                logger.error("Slack connection test failed: could not post message")
                return False

        except SlackApiError as e:
            logger.error(f"Slack connection test failed: {e.response['error']}")
            return False

        except Exception as e:
            logger.error(f"Slack connection test failed with unexpected error: {e}")
            return False
