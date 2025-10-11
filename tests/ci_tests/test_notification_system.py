"""Tests for notification system.

These tests verify the NotificationDB correctly handles
daemon-user communication via notifications.
"""

import pytest
import tempfile
from pathlib import Path
from coffee_maker.cli.notifications import (
    NotificationDB,
    NOTIF_TYPE_INFO,
    NOTIF_TYPE_QUESTION,
    NOTIF_PRIORITY_HIGH,
    NOTIF_PRIORITY_NORMAL,
    NOTIF_STATUS_PENDING,
    NOTIF_STATUS_RESPONDED,
)


class TestNotificationSystem:
    """Test notification system functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        db = NotificationDB(db_path=db_path)
        yield db

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_notification_db_initializes(self, temp_db):
        """Verify NotificationDB initializes correctly."""
        assert temp_db is not None
        assert temp_db.db_path is not None

    def test_create_notification(self, temp_db):
        """Verify notification creation."""
        notif_id = temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Test Notification",
            message="This is a test",
            priority=NOTIF_PRIORITY_NORMAL,
        )

        assert notif_id is not None
        assert notif_id > 0

    def test_get_pending_notifications(self, temp_db):
        """Verify getting pending notifications."""
        # Create test notifications
        temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Test 1",
            message="Message 1",
        )
        temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Test 2",
            message="Message 2",
        )

        pending = temp_db.get_pending_notifications()

        assert len(pending) >= 2
        assert all(n["status"] == NOTIF_STATUS_PENDING for n in pending)

    def test_get_pending_notifications_by_priority(self, temp_db):
        """Verify filtering notifications by priority."""
        # Create high priority notification
        temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="High Priority",
            message="Important",
            priority=NOTIF_PRIORITY_HIGH,
        )

        # Create normal priority notification
        temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Normal Priority",
            message="Not urgent",
            priority=NOTIF_PRIORITY_NORMAL,
        )

        high_priority = temp_db.get_pending_notifications(priority=NOTIF_PRIORITY_HIGH)

        assert len(high_priority) >= 1
        assert all(n["priority"] == NOTIF_PRIORITY_HIGH for n in high_priority)

    def test_respond_to_notification(self, temp_db):
        """Verify responding to notifications."""
        notif_id = temp_db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Approval Required",
            message="Please approve",
        )

        # Respond
        temp_db.respond_to_notification(notif_id, "approve")

        # Verify response recorded
        notif = temp_db.get_notification(notif_id)
        assert notif["status"] == NOTIF_STATUS_RESPONDED
        assert notif["user_response"] == "approve"

    def test_mark_as_read(self, temp_db):
        """Verify marking notifications as read."""
        notif_id = temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Info",
            message="Some info",
        )

        temp_db.mark_as_read(notif_id)

        notif = temp_db.get_notification(notif_id)
        assert notif["status"] == "read"

    def test_dismiss_notification(self, temp_db):
        """Verify dismissing notifications."""
        notif_id = temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Info",
            message="Some info",
        )

        temp_db.dismiss_notification(notif_id)

        notif = temp_db.get_notification(notif_id)
        assert notif["status"] == "dismissed"

    def test_get_notification(self, temp_db):
        """Verify getting specific notification."""
        notif_id = temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Test",
            message="Test message",
            context={"key": "value"},
        )

        notif = temp_db.get_notification(notif_id)

        assert notif is not None
        assert notif["id"] == notif_id
        assert notif["title"] == "Test"
        assert notif["message"] == "Test message"
        assert notif["context"]["key"] == "value"

    def test_notification_with_context(self, temp_db):
        """Verify notifications with JSON context."""
        context = {
            "priority_name": "PRIORITY 2.6",
            "attempt": 3,
            "reason": "max_retries",
        }

        notif_id = temp_db.create_notification(
            type=NOTIF_TYPE_INFO,
            title="Context Test",
            message="Testing context",
            context=context,
        )

        notif = temp_db.get_notification(notif_id)

        assert notif["context"] == context
        assert notif["context"]["priority_name"] == "PRIORITY 2.6"
        assert notif["context"]["attempt"] == 3
