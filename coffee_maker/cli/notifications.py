"""Notification database for daemon-user communication.

This module provides a notification system for communication between the
autonomous daemon and the user. Uses SQLite with WAL mode for multi-process safety.

Database Schema:
    notifications table:
        - id: Unique notification ID
        - type: Notification type (question, info, warning, error, completion)
        - priority: Priority level (critical, high, normal, low)
        - title: Short title
        - message: Full message
        - context: JSON context data
        - status: pending, read, responded, dismissed
        - user_response: User's response (if any)
        - created_at: Creation timestamp
        - updated_at: Last update timestamp

Features:
    - WAL mode enabled (multi-process safe)
    - Retry logic for database operations
    - Timeout configuration
    - JSON context support

Example:
    Create notification:
    >>> from coffee_maker.cli.notifications import NotificationDB
    >>>
    >>> db = NotificationDB()
    >>> notif_id = db.create_notification(
    ...     type="question",
    ...     title="Dependency Approval",
    ...     message="Install pandas for data processing?",
    ...     context={"dependency": "pandas", "version": "2.0.0"}
    ... )

    Get pending notifications:
    >>> pending = db.get_pending_notifications()
    >>> for notif in pending:
    ...     print(f"{notif['title']}: {notif['message']}")

    Respond to notification:
    >>> db.respond_to_notification(notif_id, "approve")
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.config import DATABASE_PATHS
from coffee_maker.langchain_observe.retry import with_retry

logger = logging.getLogger(__name__)

# Default timeout for database operations (30 seconds)
DB_TIMEOUT = 30.0

# Notification types
NOTIF_TYPE_QUESTION = "question"
NOTIF_TYPE_INFO = "info"
NOTIF_TYPE_WARNING = "warning"
NOTIF_TYPE_ERROR = "error"
NOTIF_TYPE_COMPLETION = "completion"

# Notification priorities
NOTIF_PRIORITY_CRITICAL = "critical"
NOTIF_PRIORITY_HIGH = "high"
NOTIF_PRIORITY_NORMAL = "normal"
NOTIF_PRIORITY_LOW = "low"

# Notification statuses
NOTIF_STATUS_PENDING = "pending"
NOTIF_STATUS_READ = "read"
NOTIF_STATUS_RESPONDED = "responded"
NOTIF_STATUS_DISMISSED = "dismissed"


CREATE_NOTIFICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal',
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    user_response TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
"""


class NotificationDB:
    """Notification database for daemon-user communication.

    This class provides a simple, robust notification system using SQLite
    with WAL mode and retry logic for reliability.

    Attributes:
        db_path: Path to SQLite database
        conn: SQLite connection

    Example:
        >>> db = NotificationDB()
        >>> notif_id = db.create_notification(
        ...     type="question",
        ...     title="Install dependency?",
        ...     message="The daemon needs to install pytest. Approve?"
        ... )
        >>> response = db.wait_for_response(notif_id, timeout=300)
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize notification database.

        Args:
            db_path: Path to database file (defaults to DATABASE_PATHS['notifications'])
        """
        if db_path is None:
            db_path = str(DATABASE_PATHS["notifications"])

        self.db_path = db_path

        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.debug(f"NotificationDB initialized: {db_path}")

    def _init_database(self):
        """Initialize database schema and enable WAL mode."""
        conn = sqlite3.connect(self.db_path, timeout=DB_TIMEOUT)

        # Enable WAL mode for multi-process safety
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")  # 30 second busy timeout

        # Create schema
        conn.executescript(CREATE_NOTIFICATIONS_TABLE)
        conn.commit()
        conn.close()

        logger.debug("Notification database schema initialized with WAL mode")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration.

        Returns:
            Configured SQLite connection
        """
        conn = sqlite3.connect(self.db_path, timeout=DB_TIMEOUT)
        conn.row_factory = sqlite3.Row  # Dict-like row access
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def create_notification(
        self,
        type: str,
        title: str,
        message: str,
        priority: str = NOTIF_PRIORITY_NORMAL,
        context: Optional[Dict] = None,
    ) -> int:
        """Create a new notification.

        Args:
            type: Notification type (question, info, warning, error, completion)
            title: Short title
            message: Full message
            priority: Priority level (critical, high, normal, low)
            context: Optional context data (will be JSON serialized)

        Returns:
            Notification ID

        Example:
            >>> db = NotificationDB()
            >>> notif_id = db.create_notification(
            ...     type="question",
            ...     title="Dependency Approval",
            ...     message="Install pandas?",
            ...     priority="high",
            ...     context={"dependency": "pandas"}
            ... )
        """
        now = datetime.utcnow().isoformat()
        context_json = json.dumps(context) if context else None

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO notifications
                (type, priority, title, message, context, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (type, priority, title, message, context_json, NOTIF_STATUS_PENDING, now, now),
            )
            conn.commit()
            notif_id = cursor.lastrowid

        logger.info(f"Created notification {notif_id}: {title}")
        return notif_id

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_pending_notifications(self, priority: Optional[str] = None) -> List[Dict]:
        """Get all pending notifications.

        Args:
            priority: Optional filter by priority

        Returns:
            List of notification dicts

        Example:
            >>> db = NotificationDB()
            >>> pending = db.get_pending_notifications(priority="high")
            >>> for notif in pending:
            ...     print(f"{notif['title']}: {notif['message']}")
        """
        query = "SELECT * FROM notifications WHERE status = ?"
        params = [NOTIF_STATUS_PENDING]

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_at ASC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            notifications = [self._row_to_dict(row) for row in cursor.fetchall()]

        return notifications

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def respond_to_notification(self, notif_id: int, response: str):
        """Respond to a notification.

        Args:
            notif_id: Notification ID
            response: User's response

        Example:
            >>> db = NotificationDB()
            >>> db.respond_to_notification(1, "approve")
        """
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE notifications
                SET status = ?, user_response = ?, updated_at = ?
                WHERE id = ?
                """,
                (NOTIF_STATUS_RESPONDED, response, now, notif_id),
            )
            conn.commit()

        logger.info(f"Notification {notif_id} responded: {response}")

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def mark_as_read(self, notif_id: int):
        """Mark notification as read.

        Args:
            notif_id: Notification ID
        """
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE notifications SET status = ?, updated_at = ? WHERE id = ?",
                (NOTIF_STATUS_READ, now, notif_id),
            )
            conn.commit()

        logger.info(f"Notification {notif_id} marked as read")

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def dismiss_notification(self, notif_id: int):
        """Dismiss a notification.

        Args:
            notif_id: Notification ID
        """
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE notifications SET status = ?, updated_at = ? WHERE id = ?",
                (NOTIF_STATUS_DISMISSED, now, notif_id),
            )
            conn.commit()

        logger.info(f"Notification {notif_id} dismissed")

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_notification(self, notif_id: int) -> Optional[Dict]:
        """Get a specific notification by ID.

        Args:
            notif_id: Notification ID

        Returns:
            Notification dict or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM notifications WHERE id = ?", (notif_id,))
            row = cursor.fetchone()

        return self._row_to_dict(row) if row else None

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert database row to dictionary.

        Args:
            row: SQLite row

        Returns:
            Dictionary with notification data
        """
        notif = dict(row)

        # Parse JSON context if present
        if notif.get("context"):
            try:
                notif["context"] = json.loads(notif["context"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse context JSON: {notif['context']}")
                notif["context"] = {}

        return notif

    def close(self):
        """Close database connection."""
        # Connection is opened per-operation, nothing to close
        logger.info("NotificationDB closed")
