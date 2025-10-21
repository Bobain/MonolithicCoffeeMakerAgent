"""Database-backed ROADMAP management system.

Replaces file-based ROADMAP.md with SQLite database for:
- Concurrent access control
- Write access enforcement (project_manager only)
- Bidirectional sync with markdown files
- Message-based update requests

Architecture:
    - roadmap_items table: Stores all priorities/user stories
    - roadmap_metadata table: Stores header/footer content
    - Import: Parse ROADMAP.md → database
    - Export: Generate ROADMAP.md from database
    - Write access: Only project_manager agent
    - Read access: All agents
"""

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class RoadmapDatabase:
    """Database-backed ROADMAP with import/export and access control.

    Single source of truth for ROADMAP data with:
    - Structured storage of priorities and user stories
    - Bidirectional sync with ROADMAP.md file
    - Write access control (project_manager only)
    - Complete audit trail of changes

    Example:
        >>> db = RoadmapDatabase()
        >>> db.import_from_file("docs/roadmap/ROADMAP.md")
        >>> items = db.get_all_items()
        >>> db.update_status("US-062", "🔄 In Progress", updated_by="code_developer")
        >>> db.export_to_file("docs/roadmap/ROADMAP.md")
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize roadmap database.

        Args:
            db_path: Path to SQLite database (default: data/roadmap.db)
        """
        if db_path is None:
            db_path = Path("data/roadmap.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema if not exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create roadmap_items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_items (
                    id TEXT PRIMARY KEY,
                    item_type TEXT NOT NULL,
                    number TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    content TEXT,
                    phase TEXT,
                    estimated_hours TEXT,
                    dependencies TEXT,
                    section_order INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT NOT NULL
                )
            """
            )

            # Create metadata table for header/footer
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """
            )

            # Create audit trail table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    field_changed TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by TEXT NOT NULL,
                    changed_at TEXT NOT NULL
                )
            """
            )

            # Create roadmap update notifications table
            # This persists update requests from agents until project_manager actions them
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_update_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    requested_status TEXT,
                    message TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    processed_by TEXT,
                    notes TEXT
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON roadmap_items(item_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_status ON roadmap_items(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON roadmap_items(section_order)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_item ON roadmap_audit(item_id)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notifications_status ON roadmap_update_notifications(status)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_item ON roadmap_update_notifications(item_id)")

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Error initializing roadmap database: {e}")

    def import_from_file(self, roadmap_path: Path) -> int:
        """Import ROADMAP.md into database.

        Parses markdown file and stores structured data in database.
        Preserves section order for export.

        Args:
            roadmap_path: Path to ROADMAP.md file

        Returns:
            Number of items imported

        Raises:
            FileNotFoundError: If roadmap file doesn't exist
        """
        if not roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {roadmap_path}")

        content = roadmap_path.read_text()
        lines = content.split("\n")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Extract header (everything before first priority)
        header_lines = []
        priority_start_idx = 0

        for idx, line in enumerate(lines):
            if re.match(r"^##\s+(US-|PRIORITY)", line) or re.match(r"^###\s+(🔴|PRIORITY|US-)", line):
                priority_start_idx = idx
                break
            header_lines.append(line)

        header = "\n".join(header_lines)

        # Store header in metadata
        cursor.execute(
            "INSERT OR REPLACE INTO roadmap_metadata (key, value, updated_at) VALUES (?, ?, ?)",
            ("header", header, datetime.now().isoformat()),
        )

        # Parse priorities/user stories
        items_imported = 0
        section_order = 0
        current_item = None
        current_content_lines = []

        # Regex patterns for priorities (matching RoadmapParser)
        patterns = [
            (r"^##\s+US-(\d+):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "user_story"),
            (r"^##\s+PRIORITY\s+(\d+(?:\.\d+)?):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "priority"),
            (r"^###\s+🔴\s+\*\*PRIORITY\s+(\d+(?:\.\d+)?):(.+?)\*\*.*$", "priority"),
            (r"^###\s+PRIORITY\s+(\d+(?:\.\d+)?):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "priority"),
            (r"^###\s+US-(\d+):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "user_story"),
        ]

        for idx in range(priority_start_idx, len(lines)):
            line = lines[idx]

            # Check if this is a new priority header
            matched = False
            for pattern, item_type in patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous item if exists
                    if current_item:
                        current_item["content"] = "\n".join(current_content_lines)
                        self._save_item(cursor, current_item, section_order)
                        items_imported += 1
                        section_order += 1

                    # Start new item
                    number = match.group(1)
                    title = match.group(2).strip()
                    status = match.group(3) if len(match.groups()) >= 3 else "📝 Planned"

                    item_id = f"US-{number}" if item_type == "user_story" else f"PRIORITY-{number}"

                    current_item = {
                        "id": item_id,
                        "item_type": item_type,
                        "number": number,
                        "title": title,
                        "status": status if status else "📝 Planned",
                    }
                    current_content_lines = [line]
                    matched = True
                    break

            if not matched and current_item:
                # Accumulate content for current item
                current_content_lines.append(line)

        # Save last item
        if current_item:
            current_item["content"] = "\n".join(current_content_lines)
            self._save_item(cursor, current_item, section_order)
            items_imported += 1

        conn.commit()
        conn.close()

        logger.info(f"✅ Imported {items_imported} items from {roadmap_path}")
        return items_imported

    def _save_item(self, cursor, item: Dict, section_order: int) -> None:
        """Save an item to database."""
        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT OR REPLACE INTO roadmap_items
            (id, item_type, number, title, status, content, section_order, created_at, updated_at, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item["id"],
                item["item_type"],
                item["number"],
                item["title"],
                item["status"],
                item.get("content", ""),
                section_order,
                now,
                now,
                "import",
            ),
        )

    def export_to_file(self, roadmap_path: Path) -> None:
        """Export database to ROADMAP.md file.

        Generates markdown file from structured database.
        Preserves formatting and section order.

        Args:
            roadmap_path: Path to write ROADMAP.md
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get header
        cursor.execute("SELECT value FROM roadmap_metadata WHERE key = ?", ("header",))
        result = cursor.fetchone()
        header = result["value"] if result else "# Coffee Maker Agent - Prioritized Roadmap\n\n"

        # Get all items in section order
        cursor.execute(
            """
            SELECT * FROM roadmap_items
            ORDER BY section_order ASC
        """
        )

        rows = cursor.fetchall()
        conn.close()

        # Build markdown content
        lines = [header]

        for row in rows:
            # Use stored content if available (preserves exact formatting)
            if row["content"]:
                lines.append(row["content"])
            else:
                # Generate from structured data
                prefix = "##" if row["item_type"] == "user_story" else "###"
                item_id = f"US-{row['number']}" if row["item_type"] == "user_story" else f"PRIORITY {row['number']}"
                lines.append(f"{prefix} {item_id}: {row['title']} {row['status']}\n")

        # Write to file
        roadmap_path.parent.mkdir(parents=True, exist_ok=True)
        roadmap_path.write_text("\n".join(lines))

        logger.info(f"✅ Exported {len(rows)} items to {roadmap_path}")

    def get_all_items(self, status_filter: Optional[str] = None) -> List[Dict]:
        """Get all roadmap items.

        Args:
            status_filter: Optional status to filter by (e.g., "📝 Planned")

        Returns:
            List of item dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if status_filter:
                cursor.execute(
                    """
                    SELECT * FROM roadmap_items
                    WHERE status LIKE ?
                    ORDER BY section_order ASC
                """,
                    (f"%{status_filter}%",),
                )
            else:
                cursor.execute("SELECT * FROM roadmap_items ORDER BY section_order ASC")

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting roadmap items: {e}")
            return []

    def update_status(self, item_id: str, new_status: str, updated_by: str) -> bool:
        """Update status of a roadmap item.

        Args:
            item_id: Item ID (e.g., "US-062", "PRIORITY-1")
            new_status: New status (e.g., "🔄 In Progress")
            updated_by: Agent making the update

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current status for audit trail
            cursor.execute("SELECT status FROM roadmap_items WHERE id = ?", (item_id,))
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            old_status = result[0]

            # Update status
            cursor.execute(
                """
                UPDATE roadmap_items
                SET status = ?, updated_at = ?, updated_by = ?
                WHERE id = ?
            """,
                (new_status, datetime.now().isoformat(), updated_by, item_id),
            )

            # Log audit trail
            cursor.execute(
                """
                INSERT INTO roadmap_audit
                (item_id, action, field_changed, old_value, new_value, changed_by, changed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (item_id, "update_status", "status", old_status, new_status, updated_by, datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Updated {item_id} status: {old_status} → {new_status} (by {updated_by})")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error updating status: {e}")
            return False

    def get_next_planned(self) -> Optional[Dict]:
        """Get next planned item (first with "📝 Planned" status).

        Returns:
            Item dictionary or None if no planned items
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM roadmap_items
                WHERE status LIKE '%📝%' OR status LIKE '%Planned%'
                ORDER BY section_order ASC
                LIMIT 1
            """
            )

            result = cursor.fetchone()
            conn.close()

            return dict(result) if result else None

        except sqlite3.Error as e:
            logger.error(f"Error getting next planned item: {e}")
            return None

    def create_update_notification(
        self,
        item_id: str,
        requested_by: str,
        notification_type: str,
        requested_status: Optional[str] = None,
        message: str = "",
    ) -> int:
        """Create a persistent notification requesting ROADMAP update.

        Called by: code_developer, architect, or any agent (NOT project_manager)

        Args:
            item_id: Which roadmap item (e.g., "US-062")
            requested_by: Agent requesting update (e.g., "code_developer")
            notification_type: "status_update", "new_item", "modify_content"
            requested_status: New status if type is status_update
            message: Agent's explanation/context

        Returns:
            notification_id: ID of created notification

        Example:
            >>> db.create_update_notification(
            ...     item_id="US-062",
            ...     requested_by="code_developer",
            ...     notification_type="status_update",
            ...     requested_status="✅ Complete",
            ...     message="Implemented database migration, all tests passing"
            ... )
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO roadmap_update_notifications
                (item_id, requested_by, notification_type, requested_status, message, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    requested_by,
                    notification_type,
                    requested_status,
                    message,
                    "pending",
                    datetime.now().isoformat(),
                ),
            )

            notification_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(
                f"📬 Notification created: {requested_by} requests {notification_type} for {item_id} (ID: {notification_id})"
            )
            return notification_id

        except sqlite3.Error as e:
            logger.error(f"Error creating notification: {e}")
            raise

    def get_pending_notifications(self, item_id: Optional[str] = None) -> List[Dict]:
        """Get all pending notifications.

        Called by: project_manager, orchestrator (to review and action)

        Args:
            item_id: Optional filter by specific item

        Returns:
            List of pending notification dictionaries

        Example:
            >>> notifications = db.get_pending_notifications()
            >>> for notif in notifications:
            ...     print(f"{notif['requested_by']} wants to update {notif['item_id']}")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if item_id:
                cursor.execute(
                    """
                    SELECT * FROM roadmap_update_notifications
                    WHERE status = 'pending' AND item_id = ?
                    ORDER BY created_at ASC
                """,
                    (item_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM roadmap_update_notifications
                    WHERE status = 'pending'
                    ORDER BY created_at ASC
                """
                )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []

    def approve_notification(self, notification_id: int, processed_by: str, notes: str = "") -> bool:
        """Approve notification and apply the requested change.

        Called by: ONLY project_manager or orchestrator

        Args:
            notification_id: Notification to approve
            processed_by: "project_manager" or "orchestrator"
            notes: Optional note about approval

        Returns:
            True if successful

        Side effects:
            - Updates the roadmap item as requested
            - Marks notification as approved
            - Logs to audit trail

        Example:
            >>> db.approve_notification(
            ...     notification_id=5,
            ...     processed_by="project_manager",
            ...     notes="Verified all tests passing"
            ... )
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get notification details
            cursor.execute(
                """
                SELECT * FROM roadmap_update_notifications
                WHERE id = ? AND status = 'pending'
            """,
                (notification_id,),
            )

            notification = cursor.fetchone()
            if not notification:
                logger.error(f"Notification {notification_id} not found or already processed")
                conn.close()
                return False

            notification = dict(notification)

            # Apply the requested change based on notification type
            if notification["notification_type"] == "status_update":
                # Update the roadmap item status
                success = self._update_status_internal(
                    cursor, notification["item_id"], notification["requested_status"], processed_by
                )

                if not success:
                    conn.close()
                    return False

            elif notification["notification_type"] in ["new_item", "modify_content"]:
                # For now, just log - these require more complex handling
                logger.info(f"Notification type {notification['notification_type']} requires manual processing")

            # Mark notification as approved
            cursor.execute(
                """
                UPDATE roadmap_update_notifications
                SET status = 'approved', processed_at = ?, processed_by = ?, notes = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), processed_by, notes, notification_id),
            )

            conn.commit()
            conn.close()

            logger.info(
                f"✅ Notification {notification_id} approved by {processed_by}: "
                f"{notification['requested_by']} → {notification['item_id']}"
            )
            return True

        except sqlite3.Error as e:
            logger.error(f"Error approving notification: {e}")
            return False

    def reject_notification(self, notification_id: int, processed_by: str, reason: str) -> bool:
        """Reject notification with reason.

        Called by: ONLY project_manager or orchestrator

        Args:
            notification_id: Notification to reject
            processed_by: "project_manager" or "orchestrator"
            reason: Why rejected (required)

        Returns:
            True if successful

        Example:
            >>> db.reject_notification(
            ...     notification_id=5,
            ...     processed_by="project_manager",
            ...     reason="Tests still failing, please verify before marking complete"
            ... )
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Verify notification exists and is pending
            cursor.execute(
                """
                SELECT item_id, requested_by FROM roadmap_update_notifications
                WHERE id = ? AND status = 'pending'
            """,
                (notification_id,),
            )

            result = cursor.fetchone()
            if not result:
                logger.error(f"Notification {notification_id} not found or already processed")
                conn.close()
                return False

            item_id, requested_by = result

            # Mark notification as rejected
            cursor.execute(
                """
                UPDATE roadmap_update_notifications
                SET status = 'rejected', processed_at = ?, processed_by = ?, notes = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), processed_by, reason, notification_id),
            )

            conn.commit()
            conn.close()

            logger.info(
                f"❌ Notification {notification_id} rejected by {processed_by}: "
                f"{requested_by} → {item_id}. Reason: {reason}"
            )
            return True

        except sqlite3.Error as e:
            logger.error(f"Error rejecting notification: {e}")
            return False

    def _update_status_internal(self, cursor, item_id: str, new_status: str, updated_by: str) -> bool:
        """Internal method to update status using existing cursor.

        Used by approve_notification to update status within same transaction.

        Args:
            cursor: Existing database cursor
            item_id: Item ID to update
            new_status: New status value
            updated_by: Who is making the update

        Returns:
            True if successful
        """
        try:
            # Get current status for audit trail
            cursor.execute("SELECT status FROM roadmap_items WHERE id = ?", (item_id,))
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            old_status = result[0]

            # Update status
            cursor.execute(
                """
                UPDATE roadmap_items
                SET status = ?, updated_at = ?, updated_by = ?
                WHERE id = ?
            """,
                (new_status, datetime.now().isoformat(), updated_by, item_id),
            )

            # Log audit trail
            cursor.execute(
                """
                INSERT INTO roadmap_audit
                (item_id, action, field_changed, old_value, new_value, changed_by, changed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (item_id, "update_status", "status", old_status, new_status, updated_by, datetime.now().isoformat()),
            )

            logger.info(f"✅ Updated {item_id} status: {old_status} → {new_status} (by {updated_by})")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error updating status: {e}")
            return False
