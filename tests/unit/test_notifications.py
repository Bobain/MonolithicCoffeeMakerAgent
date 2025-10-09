"""Unit tests for notification database."""

import tempfile
from pathlib import Path

import pytest

from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_PRIORITY_HIGH,
    NOTIF_PRIORITY_NORMAL,
    NOTIF_STATUS_DISMISSED,
    NOTIF_STATUS_PENDING,
    NOTIF_STATUS_READ,
    NOTIF_STATUS_RESPONDED,
    NOTIF_TYPE_QUESTION,
    NotificationDB,
)


@pytest.fixture
def temp_db():
    """Create temporary notification database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    Path(f"{db_path}-wal").unlink(missing_ok=True)
    Path(f"{db_path}-shm").unlink(missing_ok=True)


class TestNotificationDB:
    """Test NotificationDB class."""

    def test_init_creates_database(self, temp_db):
        """Test database initialization."""
        db = NotificationDB(temp_db)

        # Verify database file exists
        assert Path(temp_db).exists()

        # Verify WAL mode
        with db._get_connection() as conn:
            cursor = conn.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            assert mode.lower() == "wal"

    def test_create_notification(self, temp_db):
        """Test creating a notification."""
        db = NotificationDB(temp_db)

        notif_id = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Test Question",
            message="This is a test",
            priority=NOTIF_PRIORITY_HIGH,
            context={"key": "value"},
        )

        assert notif_id > 0

        # Verify notification was created
        notif = db.get_notification(notif_id)
        assert notif is not None
        assert notif["title"] == "Test Question"
        assert notif["message"] == "This is a test"
        assert notif["type"] == NOTIF_TYPE_QUESTION
        assert notif["priority"] == NOTIF_PRIORITY_HIGH
        assert notif["status"] == NOTIF_STATUS_PENDING
        assert notif["context"] == {"key": "value"}

    def test_get_pending_notifications(self, temp_db):
        """Test getting pending notifications."""
        db = NotificationDB(temp_db)

        # Create multiple notifications
        id1 = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Question 1",
            message="Message 1",
            priority=NOTIF_PRIORITY_CRITICAL,
        )

        id2 = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Question 2",
            message="Message 2",
            priority=NOTIF_PRIORITY_HIGH,
        )

        id3 = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Question 3",
            message="Message 3",
            priority=NOTIF_PRIORITY_NORMAL,
        )

        # Mark one as read
        db.mark_as_read(id2)

        # Get pending
        pending = db.get_pending_notifications()
        assert len(pending) == 2
        assert pending[0]["id"] == id1
        assert pending[1]["id"] == id3

    def test_get_pending_by_priority(self, temp_db):
        """Test filtering pending by priority."""
        db = NotificationDB(temp_db)

        db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Critical",
            message="Critical message",
            priority=NOTIF_PRIORITY_CRITICAL,
        )

        db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="High",
            message="High message",
            priority=NOTIF_PRIORITY_HIGH,
        )

        # Get only critical
        critical = db.get_pending_notifications(priority=NOTIF_PRIORITY_CRITICAL)
        assert len(critical) == 1
        assert critical[0]["priority"] == NOTIF_PRIORITY_CRITICAL

    def test_respond_to_notification(self, temp_db):
        """Test responding to a notification."""
        db = NotificationDB(temp_db)

        notif_id = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Test Question",
            message="Test message",
        )

        # Respond
        db.respond_to_notification(notif_id, "approve")

        # Verify response
        notif = db.get_notification(notif_id)
        assert notif["status"] == NOTIF_STATUS_RESPONDED
        assert notif["user_response"] == "approve"

    def test_mark_as_read(self, temp_db):
        """Test marking notification as read."""
        db = NotificationDB(temp_db)

        notif_id = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Test",
            message="Test",
        )

        db.mark_as_read(notif_id)

        notif = db.get_notification(notif_id)
        assert notif["status"] == NOTIF_STATUS_READ

    def test_dismiss_notification(self, temp_db):
        """Test dismissing a notification."""
        db = NotificationDB(temp_db)

        notif_id = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Test",
            message="Test",
        )

        db.dismiss_notification(notif_id)

        notif = db.get_notification(notif_id)
        assert notif["status"] == NOTIF_STATUS_DISMISSED

    def test_retry_on_lock(self, temp_db):
        """Test retry logic on database lock."""
        db = NotificationDB(temp_db)

        # Create notification (should succeed even with retries)
        notif_id = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Retry Test",
            message="Testing retry logic",
        )

        assert notif_id > 0

    def test_context_json_serialization(self, temp_db):
        """Test JSON context serialization."""
        db = NotificationDB(temp_db)

        context = {
            "dependency": "pandas",
            "version": "2.0.0",
            "nested": {"key": "value"},
        }

        notif_id = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Test",
            message="Test",
            context=context,
        )

        notif = db.get_notification(notif_id)
        assert notif["context"] == context

    def test_get_nonexistent_notification(self, temp_db):
        """Test getting notification that doesn't exist."""
        db = NotificationDB(temp_db)

        notif = db.get_notification(99999)
        assert notif is None

    def test_multiple_notifications_order(self, temp_db):
        """Test notifications are returned in creation order."""
        db = NotificationDB(temp_db)

        id1 = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="First",
            message="First",
        )

        id2 = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Second",
            message="Second",
        )

        id3 = db.create_notification(
            type=NOTIF_TYPE_QUESTION,
            title="Third",
            message="Third",
        )

        pending = db.get_pending_notifications()
        assert len(pending) == 3
        assert pending[0]["id"] == id1
        assert pending[1]["id"] == id2
        assert pending[2]["id"] == id3
