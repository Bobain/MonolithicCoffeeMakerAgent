"""End-to-end workflow tests for US-017 complete feature.

US-017 Phase 6: End-to-End Testing

Tests complete workflow:
- Auto-update detection
- Report generation
- Multi-channel delivery
- Error recovery
- Configuration persistence
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coffee_maker.reports.notification_dispatcher import NotificationDispatcher
from coffee_maker.reports.status_report_generator import StatusReportGenerator
from coffee_maker.reports.status_tracking_updater import update_status_tracking
from coffee_maker.reports.update_scheduler import UpdateScheduler


@pytest.fixture
def sample_roadmap():
    """Create a sample ROADMAP.md for testing."""
    content = """# Project Roadmap

## US-001 - Feature A ✅ COMPLETE
**Completed**: 2025-10-01
**Story Points**: 5
**Business Value**: Improved user experience with better UX

## US-002 - Feature B ✅ COMPLETE
**Completed**: 2025-10-05
**Story Points**: 3
**Business Value**: Performance improvements for faster loading

## US-003 - Feature C 📝 PLANNED
**Estimate**: 5 days
**Priority**: High
**Business Value**: New analytics dashboard

## US-004 - Feature D 🔄 IN PROGRESS
**Estimate**: 3 days
**Started**: 2025-10-10
**Business Value**: User authentication system
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_config_file():
    """Create temporary config file."""
    config = {
        "channels": ["console"],
        "slack_enabled": False,
        "email_enabled": False,
        "auto_update_enabled": True,
        "update_interval_days": 3,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""

    def test_full_workflow_without_notifications(self, sample_roadmap, temp_output_dir):
        """Test complete workflow: parse → generate → update (no notifications)."""
        output_path = Path(temp_output_dir) / "STATUS_TRACKING.md"

        # Run update
        success = update_status_tracking(
            roadmap_path=sample_roadmap,
            output_path=str(output_path),
            days=14,
            upcoming_count=5,
            send_notifications=False,
        )

        assert success is True
        assert output_path.exists()

        # Check content
        content = output_path.read_text()
        assert "STATUS_TRACKING.md" in content
        assert "US-001" in content
        assert "US-003" in content

    def test_full_workflow_with_console_notifications(self, sample_roadmap, temp_output_dir, temp_config_file, capsys):
        """Test complete workflow with console notifications."""
        output_path = Path(temp_output_dir) / "STATUS_TRACKING.md"

        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        # Run update with notifications
        success = update_status_tracking(
            roadmap_path=sample_roadmap,
            output_path=str(output_path),
            days=14,
            upcoming_count=5,
            send_notifications=True,
            dispatcher=dispatcher,
        )

        assert success is True
        assert output_path.exists()

        # Check console output
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out
        assert "UPCOMING DELIVERABLES" in captured.out
        assert "US-001" in captured.out

    @patch("requests.post")
    def test_full_workflow_with_slack_notifications(self, mock_post, sample_roadmap, temp_output_dir, temp_config_file):
        """Test complete workflow with Slack notifications."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        output_path = Path(temp_output_dir) / "STATUS_TRACKING.md"

        # Enable Slack
        dispatcher = NotificationDispatcher(config_path=temp_config_file)
        dispatcher.update_config(
            slack_enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            channels=["console", "slack"],
        )

        # Run update with Slack
        success = update_status_tracking(
            roadmap_path=sample_roadmap,
            output_path=str(output_path),
            days=14,
            upcoming_count=5,
            send_notifications=True,
            dispatcher=dispatcher,
        )

        assert success is True
        assert output_path.exists()

        # Check Slack was called (2 calls: summary + calendar)
        assert mock_post.call_count == 2

    def test_workflow_continues_on_notification_failure(self, sample_roadmap, temp_output_dir, temp_config_file):
        """Test that workflow continues even if notifications fail."""
        output_path = Path(temp_output_dir) / "STATUS_TRACKING.md"

        # Configure Slack but don't mock requests (will fail)
        dispatcher = NotificationDispatcher(config_path=temp_config_file)
        dispatcher.update_config(
            slack_enabled=True, slack_webhook_url="https://invalid.url", channels=["console", "slack"]
        )

        # Run update - should succeed despite Slack failure
        success = update_status_tracking(
            roadmap_path=sample_roadmap,
            output_path=str(output_path),
            days=14,
            upcoming_count=5,
            send_notifications=True,
            dispatcher=dispatcher,
        )

        # Update should still succeed
        assert success is True
        assert output_path.exists()


class TestAutoUpdateScheduling:
    """Test automatic update scheduling."""

    def test_scheduler_detects_interval_elapsed(self, sample_roadmap, temp_output_dir):
        """Test scheduler detects when update interval has elapsed."""
        scheduler = UpdateScheduler(roadmap_path=sample_roadmap)

        # First check should trigger update (no history)
        should_update = scheduler.should_update()
        assert should_update is True

    def test_scheduler_skips_recent_updates(self, sample_roadmap, temp_output_dir):
        """Test scheduler skips updates when interval hasn't elapsed."""
        scheduler = UpdateScheduler(roadmap_path=sample_roadmap)

        # Record an update
        scheduler.record_update(manual=False)

        # Immediate check should skip
        should_update = scheduler.should_update(force=False)
        assert should_update is False

    def test_force_update_bypasses_interval(self, sample_roadmap, temp_output_dir):
        """Test force flag bypasses interval check."""
        scheduler = UpdateScheduler(roadmap_path=sample_roadmap)

        # Record an update
        scheduler.record_update(manual=False)

        # Force should still trigger
        should_update = scheduler.should_update(force=True)
        assert should_update is True


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    def test_missing_roadmap_returns_false(self, temp_output_dir):
        """Test graceful handling of missing ROADMAP."""
        output_path = Path(temp_output_dir) / "STATUS_TRACKING.md"

        success = update_status_tracking(
            roadmap_path="/nonexistent/roadmap.md", output_path=str(output_path), send_notifications=False
        )

        assert success is False
        assert not output_path.exists()

    def test_invalid_roadmap_content_handles_gracefully(self, temp_output_dir):
        """Test handling of invalid ROADMAP content."""
        # Create invalid ROADMAP
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("This is not a valid ROADMAP")
            invalid_roadmap = f.name

        try:
            output_path = Path(temp_output_dir) / "STATUS_TRACKING.md"

            # Should not crash, but may return False or handle gracefully
            try:
                success = update_status_tracking(
                    roadmap_path=invalid_roadmap, output_path=str(output_path), send_notifications=False
                )
                # Either succeeds with empty data or fails gracefully
                assert isinstance(success, bool)
            except Exception:
                pytest.fail("Should handle invalid ROADMAP gracefully")

        finally:
            if os.path.exists(invalid_roadmap):
                os.unlink(invalid_roadmap)

    def test_partial_notification_failure_continues(self, sample_roadmap, temp_output_dir, temp_config_file, capsys):
        """Test that partial notification failure doesn't stop workflow."""
        output_path = Path(temp_output_dir) / "STATUS_TRACKING.md"

        # Configure Slack (will fail) and console (will work)
        dispatcher = NotificationDispatcher(config_path=temp_config_file)
        dispatcher.update_config(
            slack_enabled=True, slack_webhook_url="https://invalid.url", channels=["console", "slack"]
        )

        # Should succeed with console, fail with Slack, but overall succeed
        success = update_status_tracking(
            roadmap_path=sample_roadmap,
            output_path=str(output_path),
            send_notifications=True,
            dispatcher=dispatcher,
        )

        assert success is True
        assert output_path.exists()

        # Console should have output
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out


class TestConfigurationPersistence:
    """Test configuration persistence across sessions."""

    def test_config_persists_across_instances(self, temp_config_file):
        """Test configuration persists when creating new instances."""
        # First instance - update config
        dispatcher1 = NotificationDispatcher(config_path=temp_config_file)
        dispatcher1.update_config(slack_enabled=True, slack_webhook_url="https://hooks.slack.com/test")

        # Second instance - should load persisted config
        dispatcher2 = NotificationDispatcher(config_path=temp_config_file)

        assert dispatcher2.config["slack_enabled"] is True
        assert dispatcher2.config["slack_webhook_url"] == "https://hooks.slack.com/test"
        assert dispatcher2.slack_notifier is not None

    def test_config_update_creates_backup(self, temp_config_file):
        """Test that config updates are saved immediately."""
        dispatcher = NotificationDispatcher(config_path=temp_config_file)

        # Update config
        dispatcher.update_config(update_interval_days=7)

        # Read file directly
        with open(temp_config_file, "r") as f:
            saved_config = json.load(f)

        assert saved_config["update_interval_days"] == 7


class TestIntegrationWithReportGenerator:
    """Test integration with StatusReportGenerator."""

    def test_generator_provides_correct_data_format(self, sample_roadmap):
        """Test that generator output is compatible with dispatcher."""
        generator = StatusReportGenerator(sample_roadmap)

        completions = generator.get_recent_completions(days=14)
        deliverables = generator.get_upcoming_deliverables(limit=5)

        # Check data format is compatible
        assert isinstance(completions, list)
        assert isinstance(deliverables, list)

        if completions:
            assert hasattr(completions[0], "story_id")
            assert hasattr(completions[0], "title")

        if deliverables:
            assert hasattr(deliverables[0], "story_id")
            assert hasattr(deliverables[0], "title")

    def test_end_to_end_data_flow(self, sample_roadmap, temp_config_file, capsys):
        """Test complete data flow from ROADMAP to notifications."""
        # Parse ROADMAP
        generator = StatusReportGenerator(sample_roadmap)
        completions = generator.get_recent_completions(days=14)
        deliverables = generator.get_upcoming_deliverables(limit=5)

        # Dispatch notifications
        dispatcher = NotificationDispatcher(config_path=temp_config_file)
        summary_results = dispatcher.dispatch_summary(completions, period_days=14)
        calendar_results = dispatcher.dispatch_calendar(deliverables, limit=5)

        # Verify success
        assert summary_results["console"] is True
        assert calendar_results["console"] is True

        # Verify output contains expected data
        captured = capsys.readouterr()
        assert "US-001" in captured.out or "US-002" in captured.out
        assert "US-003" in captured.out or "US-004" in captured.out
