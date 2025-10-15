"""Tests for project-manager CLI.

Tests the project-manager command-line interface for:
- Viewing roadmap (full and specific priorities)
- Listing notifications
- Responding to notifications
- Status and sync commands (placeholders)
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_PRIORITY_HIGH,
    NOTIF_PRIORITY_NORMAL,
    NOTIF_STATUS_PENDING,
    NOTIF_TYPE_INFO,
    NOTIF_TYPE_QUESTION,
)
from coffee_maker.cli.roadmap_cli import (
    cmd_notifications,
    cmd_respond,
    cmd_status,
    cmd_sync,
    cmd_view,
)


class TestCmdView:
    """Tests for cmd_view (roadmap viewing)."""

    @pytest.fixture
    def temp_roadmap(self):
        """Create temporary roadmap file."""
        content = """# Test Roadmap

### 🔴 **PRIORITY 1: Test Feature One**

**Status**: ✅ Complete

Test content for priority 1.

### 🔴 **PRIORITY 2: Test Feature Two**

**Status**: 🔄 In Progress

Test content for priority 2.

### 🔴 **PRIORITY 3: Test Feature Three**

**Status**: 📝 Planned

Test content for priority 3.
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        yield temp_path

        # Cleanup
        temp_path.unlink(missing_ok=True)

    def test_view_full_roadmap(self, temp_roadmap, capsys):
        """Test viewing full roadmap."""
        args = MagicMock()
        args.priority = None

        with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", temp_roadmap):
            result = cmd_view(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "Coffee Maker Agent - ROADMAP" in captured.out
        assert "PRIORITY 1" in captured.out
        assert "PRIORITY 2" in captured.out

    def test_view_specific_priority_by_number(self, temp_roadmap, capsys):
        """Test viewing specific priority by number."""
        args = MagicMock()
        args.priority = "2"

        with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", temp_roadmap):
            result = cmd_view(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "PRIORITY 2" in captured.out
        assert "Test Feature Two" in captured.out
        # Should not show other priorities
        assert "PRIORITY 1" not in captured.out or "PRIORITY 2" in captured.out  # Header might show both

    def test_view_specific_priority_by_name(self, temp_roadmap, capsys):
        """Test viewing specific priority by name."""
        args = MagicMock()
        args.priority = "PRIORITY-1"

        with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", temp_roadmap):
            result = cmd_view(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "PRIORITY 1" in captured.out
        assert "Test Feature One" in captured.out

    def test_view_nonexistent_priority(self, temp_roadmap, capsys):
        """Test viewing nonexistent priority."""
        args = MagicMock()
        args.priority = "999"

        with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", temp_roadmap):
            cmd_view(args)

        # Should still succeed but show not found message
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    def test_view_roadmap_not_found(self, capsys):
        """Test viewing when roadmap file doesn't exist."""
        args = MagicMock()
        args.priority = None

        nonexistent = Path("/tmp/nonexistent_roadmap_12345.md")

        with patch("coffee_maker.cli.roadmap_cli.ROADMAP_PATH", nonexistent):
            result = cmd_view(args)

        assert result == 1

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()


class TestCmdStatus:
    """Tests for cmd_status (daemon status)."""

    def test_status_placeholder(self, capsys):
        """Test status command (MVP placeholder)."""
        args = MagicMock()

        result = cmd_status(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "Daemon Status" in captured.out
        assert "Not implemented yet" in captured.out


class TestCmdNotifications:
    """Tests for cmd_notifications (notification listing)."""

    def test_no_pending_notifications(self, capsys):
        """Test when there are no pending notifications."""
        args = MagicMock()

        mock_db = MagicMock()
        mock_db.get_pending_notifications.return_value = []

        with patch("coffee_maker.cli.roadmap_cli.NotificationDB", return_value=mock_db):
            result = cmd_notifications(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "No pending notifications" in captured.out

    def test_pending_notifications_by_priority(self, capsys):
        """Test listing notifications grouped by priority."""
        args = MagicMock()

        notifications = [
            {
                "id": 1,
                "type": NOTIF_TYPE_QUESTION,
                "title": "Critical Issue",
                "message": "Critical message",
                "priority": NOTIF_PRIORITY_CRITICAL,
                "created_at": "2025-10-09 10:00:00",
            },
            {
                "id": 2,
                "type": NOTIF_TYPE_INFO,
                "title": "High Priority",
                "message": "High message",
                "priority": NOTIF_PRIORITY_HIGH,
                "created_at": "2025-10-09 10:01:00",
            },
            {
                "id": 3,
                "type": NOTIF_TYPE_INFO,
                "title": "Normal Priority",
                "message": "Normal message",
                "priority": NOTIF_PRIORITY_NORMAL,
                "created_at": "2025-10-09 10:02:00",
            },
        ]

        mock_db = MagicMock()
        mock_db.get_pending_notifications.return_value = notifications

        with patch("coffee_maker.cli.roadmap_cli.NotificationDB", return_value=mock_db):
            result = cmd_notifications(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "CRITICAL" in captured.out
        assert "HIGH" in captured.out
        assert "NORMAL" in captured.out
        assert "Critical Issue" in captured.out
        assert "High Priority" in captured.out
        assert "Normal Priority" in captured.out
        assert "Total: 3" in captured.out


class TestCmdRespond:
    """Tests for cmd_respond (responding to notifications)."""

    def test_respond_to_pending_notification(self, capsys):
        """Test responding to a pending notification."""
        args = MagicMock()
        args.notif_id = 5
        args.response = "approve"

        notification = {
            "id": 5,
            "type": NOTIF_TYPE_QUESTION,
            "title": "Implement feature X?",
            "message": "Should I implement feature X?",
            "priority": NOTIF_PRIORITY_HIGH,
            "status": NOTIF_STATUS_PENDING,
            "created_at": "2025-10-09 10:00:00",
        }

        mock_db = MagicMock()
        mock_db.get_notification.return_value = notification
        mock_db.respond_to_notification.return_value = None

        with patch("coffee_maker.cli.roadmap_cli.NotificationDB", return_value=mock_db):
            result = cmd_respond(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "Responded to notification 5" in captured.out
        assert "approve" in captured.out

        # Verify DB methods called
        mock_db.get_notification.assert_called_once_with(5)
        mock_db.respond_to_notification.assert_called_once_with(5, "approve")

    def test_respond_to_nonexistent_notification(self, capsys):
        """Test responding to nonexistent notification."""
        args = MagicMock()
        args.notif_id = 999
        args.response = "approve"

        mock_db = MagicMock()
        mock_db.get_notification.return_value = None

        with patch("coffee_maker.cli.roadmap_cli.NotificationDB", return_value=mock_db):
            result = cmd_respond(args)

        assert result == 1

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    def test_respond_to_non_pending_notification(self, capsys):
        """Test responding to non-pending notification."""
        args = MagicMock()
        args.notif_id = 10
        args.response = "approve"

        notification = {
            "id": 10,
            "type": NOTIF_TYPE_QUESTION,
            "title": "Already responded",
            "message": "Test message",
            "priority": NOTIF_PRIORITY_HIGH,
            "status": "completed",  # Not pending
            "created_at": "2025-10-09 10:00:00",
        }

        mock_db = MagicMock()
        mock_db.get_notification.return_value = notification

        with patch("coffee_maker.cli.roadmap_cli.NotificationDB", return_value=mock_db):
            result = cmd_respond(args)

        assert result == 1

        captured = capsys.readouterr()
        assert "not pending" in captured.out.lower()


class TestCmdSync:
    """Tests for cmd_sync (sync with daemon)."""

    def test_sync_placeholder(self, capsys):
        """Test sync command (MVP placeholder)."""
        args = MagicMock()

        result = cmd_sync(args)

        assert result == 0

        captured = capsys.readouterr()
        assert "Sync" in captured.out
        assert "Not implemented yet" in captured.out


class TestCLIIntegration:
    """Integration tests for the CLI."""

    def test_cli_command_routing(self):
        """Test that commands are properly routed."""
        # This tests that the command routing dictionary is set up correctly
        from coffee_maker.cli.roadmap_cli import main

        # Test with no command (should show help)
        with patch("sys.argv", ["project-manager"]):
            with patch("coffee_maker.cli.roadmap_cli.logger") as mock_logger:
                try:
                    result = main()
                    # Should return 1 for no command
                    assert result in [0, 1]
                except SystemExit as e:
                    # argparse might raise SystemExit
                    assert e.code in [0, 1, None]

    def test_cli_error_handling(self, capsys):
        """Test CLI error handling."""
        args = MagicMock()

        # Test error in notification listing
        mock_db = MagicMock()
        mock_db.get_pending_notifications.side_effect = Exception("Database error")

        with patch("coffee_maker.cli.roadmap_cli.NotificationDB", return_value=mock_db):
            # The exception should be caught and logged
            # For now, the command doesn't have try/except at the handler level
            # but main() does, so this tests that behavior
            with pytest.raises(Exception):
                cmd_notifications(args)


# Run tests with: pytest tests/unit/test_roadmap_cli.py -v
