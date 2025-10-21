"""Integration tests for multi-channel delivery system.

US-017 Phase 5: Multi-Channel Delivery

Tests cover:
- NotificationDispatcher initialization and configuration
- Slack notifications (summary and calendar)
- Email notifications (stub)
- Console output
- Multi-channel dispatch
- Graceful fallback on errors
- Configuration management
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coffee_maker.reports.notification_dispatcher import NotificationDispatcher, DEFAULT_CONFIG
from coffee_maker.reports.slack_notifier import SlackNotifier
from coffee_maker.reports.status_report_generator import StoryCompletion, UpcomingStory


@pytest.fixture
def temp_config_file():
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(DEFAULT_CONFIG, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_completions():
    """Sample story completions for testing."""
    from datetime import datetime

    return [
        StoryCompletion(
            story_id="US-001",
            title="Feature A",
            business_value="Improve user experience",
            completion_date=datetime(2025, 10, 1),
            key_features=["Feature 1", "Feature 2"],
            estimated_days=5.0,
            actual_days=4.5,
        ),
        StoryCompletion(
            story_id="US-002",
            title="Feature B",
            business_value="Increase performance",
            completion_date=datetime(2025, 10, 5),
            key_features=["Performance boost"],
            estimated_days=3.0,
            actual_days=3.2,
        ),
    ]


@pytest.fixture
def sample_deliverables():
    """Sample upcoming deliverables for testing."""
    from datetime import datetime, timedelta

    return [
        UpcomingStory(
            story_id="US-003",
            title="Feature C",
            estimated_min_days=4.0,
            estimated_max_days=6.0,
            estimated_completion_date=datetime.now() + timedelta(days=5),
            what_description="New feature C",
            impact_statement="Improved functionality",
        ),
        UpcomingStory(
            story_id="US-004",
            title="Feature D",
            estimated_min_days=2.0,
            estimated_max_days=4.0,
            estimated_completion_date=datetime.now() + timedelta(days=3),
            what_description="New feature D",
            impact_statement="Better user experience",
        ),
    ]


class TestNotificationDispatcherInitialization:
    """Test NotificationDispatcher initialization and configuration."""

    def test_default_initialization(self):
        """Test initialization with default config."""
        dispatcher = NotificationDispatcher()

        assert dispatcher.config is not None
        assert "channels" in dispatcher.config
        assert dispatcher.slack_notifier is None  # Slack disabled by default

    def test_initialization_with_custom_config(self, temp_config_file):
        """Test initialization with custom config file."""
        # Create custom config
        custom_config = {
            "channels": ["console", "slack"],
            "slack_enabled": True,
            "slack_webhook_url": "https://hooks.slack.com/test",
            "email_enabled": False,
        }

        with open(temp_config_file, "w") as f:
            json.dump(custom_config, f)

        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        assert dispatcher.config["slack_enabled"] is True
        assert dispatcher.config["slack_webhook_url"] == "https://hooks.slack.com/test"
        assert dispatcher.slack_notifier is not None

    def test_config_file_creation(self):
        """Test automatic config file creation if not exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "notification_preferences.json"

            dispatcher = NotificationDispatcher(config_path=str(config_path))

            assert config_path.exists()
            assert dispatcher.config == DEFAULT_CONFIG

    def test_config_update(self, temp_config_file):
        """Test configuration update."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        dispatcher.update_config(slack_enabled=True, slack_webhook_url="https://hooks.slack.com/new")

        assert dispatcher.config["slack_enabled"] is True
        assert dispatcher.config["slack_webhook_url"] == "https://hooks.slack.com/new"
        assert dispatcher.slack_notifier is not None


class TestSlackNotifier:
    """Test SlackNotifier functionality."""

    def test_slack_notifier_disabled_without_webhook(self):
        """Test Slack notifier is disabled when no webhook configured."""
        notifier = SlackNotifier()

        assert notifier.enabled is False
        assert notifier.webhook_url is None

    def test_slack_notifier_enabled_with_webhook(self):
        """Test Slack notifier is enabled when webhook configured."""
        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")

        assert notifier.enabled is True
        assert notifier.webhook_url == "https://hooks.slack.com/test"

    @patch("requests.post")
    def test_send_summary_to_slack(self, mock_post, sample_completions):
        """Test sending summary to Slack."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")
        result = notifier.send_summary_to_slack(sample_completions, period_days=14)

        assert result is True
        mock_post.assert_called_once()

        # Check payload structure
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "blocks" in payload
        assert len(payload["blocks"]) > 0

    @patch("requests.post")
    def test_send_calendar_to_slack(self, mock_post, sample_deliverables):
        """Test sending calendar to Slack."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")
        result = notifier.send_calendar_to_slack(sample_deliverables, limit=5)

        assert result is True
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_slack_api_error_handling(self, mock_post, sample_completions):
        """Test handling of Slack API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")
        result = notifier.send_summary_to_slack(sample_completions, period_days=14)

        assert result is False

    def test_slack_disabled_returns_false(self, sample_completions):
        """Test that disabled Slack returns False."""
        notifier = SlackNotifier()  # No webhook

        result = notifier.send_summary_to_slack(sample_completions, period_days=14)

        assert result is False


class TestMultiChannelDispatch:
    """Test multi-channel dispatch functionality."""

    def test_console_only_dispatch(self, temp_config_file, sample_completions, sample_deliverables, capsys):
        """Test dispatch to console only."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        # Ensure only console is enabled
        dispatcher.update_config(channels=["console"], slack_enabled=False, email_enabled=False)

        # Dispatch summary
        summary_results = dispatcher.dispatch_summary(sample_completions, period_days=14)

        assert summary_results["console"] is True
        assert "slack" not in summary_results
        assert "email" not in summary_results

        # Check console output
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out
        assert "US-001" in captured.out

    @patch("requests.post")
    def test_multi_channel_dispatch(self, mock_post, temp_config_file, sample_completions, capsys):
        """Test dispatch to multiple channels."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Configure dispatcher with Slack enabled
        custom_config = {
            "channels": ["console", "slack"],
            "slack_enabled": True,
            "slack_webhook_url": "https://hooks.slack.com/test",
            "email_enabled": False,
        }

        with open(temp_config_file, "w") as f:
            json.dump(custom_config, f)

        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        # Dispatch summary
        summary_results = dispatcher.dispatch_summary(sample_completions, period_days=14)

        assert summary_results["console"] is True
        assert summary_results["slack"] is True

        # Check console output
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out

    @patch("requests.post")
    def test_graceful_fallback_on_slack_failure(self, mock_post, temp_config_file, sample_completions, capsys):
        """Test graceful fallback when Slack fails."""
        # Simulate Slack failure
        mock_post.side_effect = Exception("Network error")

        # Configure dispatcher with Slack enabled
        custom_config = {
            "channels": ["console", "slack"],
            "slack_enabled": True,
            "slack_webhook_url": "https://hooks.slack.com/test",
            "email_enabled": False,
        }

        with open(temp_config_file, "w") as f:
            json.dump(custom_config, f)

        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        # Dispatch summary
        summary_results = dispatcher.dispatch_summary(sample_completions, period_days=14)

        # Console should still work
        assert summary_results["console"] is True
        # Slack should fail gracefully
        assert summary_results["slack"] is False

        # Console output should still be present
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out

    def test_email_stub_always_fails(self, temp_config_file, sample_completions):
        """Test that email stub returns False (not implemented)."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)
        dispatcher.update_config(email_enabled=True)

        summary_results = dispatcher.dispatch_summary(sample_completions, period_days=14)

        assert summary_results["email"] is False


class TestDispatchUpdate:
    """Test dispatch_update convenience method."""

    @patch("requests.post")
    def test_dispatch_update_both_reports(
        self, mock_post, temp_config_file, sample_completions, sample_deliverables, capsys
    ):
        """Test dispatching both summary and calendar."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        summary_data = {"completions": sample_completions, "period_days": 14}
        calendar_data = {"deliverables": sample_deliverables, "limit": 5}

        results = dispatcher.dispatch_update(summary_data, calendar_data)

        assert "summary" in results
        assert "calendar" in results
        assert results["summary"]["console"] is True
        assert results["calendar"]["console"] is True

        # Check console output for both
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out
        assert "UPCOMING DELIVERABLES" in captured.out


class TestConfigurationManagement:
    """Test configuration file management."""

    def test_get_config(self, temp_config_file):
        """Test getting current configuration."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        config = dispatcher.get_config()

        assert isinstance(config, dict)
        assert "channels" in config
        assert "slack_enabled" in config

    def test_test_channels(self, temp_config_file):
        """Test channel testing functionality."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        results = dispatcher.test_channels()

        assert "console" in results
        assert results["console"] is True  # Console always works


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_completions_list(self, temp_config_file, capsys):
        """Test dispatch with empty completions list."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        results = dispatcher.dispatch_summary([], period_days=14)

        assert results["console"] is True

        captured = capsys.readouterr()
        assert "0 stories completed" in captured.out

    def test_empty_deliverables_list(self, temp_config_file, capsys):
        """Test dispatch with empty deliverables list."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        results = dispatcher.dispatch_calendar([], limit=5)

        assert results["console"] is True

        captured = capsys.readouterr()
        assert "0 upcoming stories" in captured.out

    def test_invalid_config_file_uses_defaults(self):
        """Test that invalid config file falls back to defaults."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name

        try:
            dispatcher = NotificationDispatcher(config_path=temp_path)

            # Should use default config
            assert dispatcher.config == DEFAULT_CONFIG

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
