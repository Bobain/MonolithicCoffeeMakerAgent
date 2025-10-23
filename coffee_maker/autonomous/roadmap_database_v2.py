"""Database-backed ROADMAP management system (Version 2).

This is the ONLY authorized way to access the ROADMAP.
Direct file access to ROADMAP.md is FORBIDDEN.

Key Changes in v2:
- Simplified schema (removed created_at from items)
- Enforced database-only access
- id field is PRIMARY KEY (guaranteed unique)
- All agents MUST use this interface

Architecture:
    - roadmap_items table: Stores all priorities/user stories
    - roadmap_metadata table: Stores header/footer content
    - Write access: project_manager only
    - Read access: All agents
    - Direct file access: FORBIDDEN
"""

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RoadmapDatabaseV2:
    """Database-backed ROADMAP with enforced access control.

    This is the ONLY authorized way to interact with the ROADMAP.
    Direct file manipulation of ROADMAP.md is FORBIDDEN.

    Access Control:
        - Write operations: project_manager ONLY
        - Read operations: All agents
        - File operations: FORBIDDEN (use export_to_file only for backups)

    Example:
        >>> db = RoadmapDatabaseV2()
        >>> items = db.get_all_items()  # Read allowed for all
        >>> db.update_status("US-062", "Complete", "project_manager")  # Write requires PM
    """

    def __init__(self, db_path: Optional[Path] = None, agent_name: str = "unknown"):
        """Initialize roadmap database.

        Args:
            db_path: Path to SQLite database (default: data/roadmap.db)
            agent_name: Name of agent accessing the database
        """
        if db_path is None:
            db_path = Path("data/roadmap.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.agent_name = agent_name
        self.can_write = agent_name == "project_manager"

        self._init_database()

        if not self.can_write and agent_name != "unknown":
            logger.info(f"Agent {agent_name} has read-only access to roadmap database")

    def _init_database(self) -> None:
        """Initialize database schema (simplified)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create simplified roadmap_items table
            # PRIMARY KEY ensures id uniqueness
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_items (
                    id TEXT PRIMARY KEY,            -- UNIQUE by definition
                    item_type TEXT NOT NULL,        -- 'user_story' or 'priority'
                    number TEXT NOT NULL,           -- "062", "1", "1.5"
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,           -- "📝 Planned", "🔄 In Progress", etc.
                    spec_id TEXT,                   -- Foreign key to technical_specs.id
                    content TEXT,                   -- Full markdown content
                    phase TEXT,                     -- Optional phase grouping
                    estimated_hours TEXT,           -- Time estimation
                    dependencies TEXT,              -- Dependency information
                    section_order INTEGER NOT NULL, -- Preserve ROADMAP.md ordering
                    updated_at TEXT NOT NULL,       -- ISO timestamp
                    updated_by TEXT NOT NULL,       -- Agent who updated
                    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
                )
            """
            )

            # Create metadata table
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

            # Create update notifications table
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

            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON roadmap_items(item_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_status ON roadmap_items(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON roadmap_items(section_order)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_number ON roadmap_items(number)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_spec ON roadmap_items(spec_id)"
            )  # Index for spec lookups
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_items_id ON roadmap_items(id)")  # Enforce uniqueness
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_item ON roadmap_audit(item_id)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notifications_status ON roadmap_update_notifications(status)"
            )

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Error initializing roadmap database: {e}")
            raise

    def create_item(
        self,
        item_id: str,
        item_type: str,
        number: str,
        title: str,
        status: str = "📝 Planned",
        content: str = "",
        phase: Optional[str] = None,
        estimated_hours: Optional[str] = None,
        dependencies: Optional[str] = None,
        section_order: int = 999,
    ) -> bool:
        """Create a new roadmap item.

        Args:
            item_id: Unique ID (e.g., "US-062", "PRIORITY-1")
            item_type: "user_story" or "priority"
            number: Item number (e.g., "062", "1")
            title: Item title
            status: Status emoji and text
            content: Full markdown content
            phase: Optional phase grouping
            estimated_hours: Time estimate
            dependencies: Dependencies info
            section_order: Order in roadmap

        Returns:
            True if successful

        Raises:
            PermissionError: If agent is not project_manager
            sqlite3.IntegrityError: If id already exists
        """
        if not self.can_write:
            raise PermissionError(f"Only project_manager can create items, not {self.agent_name}")

        now = datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO roadmap_items (
                    id, item_type, number, title, status, content,
                    phase, estimated_hours, dependencies, section_order,
                    updated_at, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    item_type,
                    number,
                    title,
                    status,
                    content,
                    phase,
                    estimated_hours,
                    dependencies,
                    section_order,
                    now,
                    self.agent_name,
                ),
            )

            # Log to audit
            cursor.execute(
                """
                INSERT INTO roadmap_audit (
                    item_id, action, changed_by, changed_at
                ) VALUES (?, ?, ?, ?)
            """,
                (item_id, "create", self.agent_name, now),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Created roadmap item: {item_id}")
            return True

        except sqlite3.IntegrityError:
            logger.error(f"Item {item_id} already exists!")
            raise
        except sqlite3.Error as e:
            logger.error(f"Error creating item: {e}")
            return False

    def get_all_items(self, status_filter: Optional[str] = None) -> List[Dict]:
        """Get all roadmap items (READ operation - all agents allowed).

        Args:
            status_filter: Optional status to filter by

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

    def get_item(self, item_id: str) -> Optional[Dict]:
        """Get a specific roadmap item (READ operation - all agents allowed).

        Args:
            item_id: Item ID (e.g., "US-062")

        Returns:
            Item dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM roadmap_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            conn.close()

            return dict(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Error getting item: {e}")
            return None

    def update_status(self, item_id: str, new_status: str, updated_by: str) -> bool:
        """Update status of a roadmap item.

        Args:
            item_id: Item ID (e.g., "US-062")
            new_status: New status (e.g., "✅ Complete")
            updated_by: Agent making the update

        Returns:
            True if successful

        Raises:
            PermissionError: If agent is not project_manager
        """
        if updated_by != "project_manager":
            raise PermissionError(f"Only project_manager can update status, not {updated_by}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current status
            cursor.execute("SELECT status FROM roadmap_items WHERE id = ?", (item_id,))
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            old_status = result[0]
            now = datetime.now().isoformat()

            # Update status
            cursor.execute(
                """
                UPDATE roadmap_items
                SET status = ?, updated_at = ?, updated_by = ?
                WHERE id = ?
            """,
                (new_status, now, updated_by, item_id),
            )

            # Log audit trail
            cursor.execute(
                """
                INSERT INTO roadmap_audit (
                    item_id, action, field_changed, old_value, new_value,
                    changed_by, changed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (item_id, "update_status", "status", old_status, new_status, updated_by, now),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Updated {item_id} status: {old_status} → {new_status}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error updating status: {e}")
            return False

    def get_next_planned(self) -> Optional[Dict]:
        """Get next planned item (READ operation - all agents allowed).

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
        """Create notification requesting ROADMAP update (non-PM agents use this).

        This is how agents OTHER than project_manager request changes.

        Args:
            item_id: Which roadmap item
            requested_by: Agent requesting update
            notification_type: "status_update", "new_item", "modify_content"
            requested_status: New status if applicable
            message: Explanation/context

        Returns:
            notification_id
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO roadmap_update_notifications (
                    item_id, requested_by, notification_type, requested_status,
                    message, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
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

            logger.info(f"📬 {requested_by} requested {notification_type} for {item_id}")
            return notification_id

        except sqlite3.Error as e:
            logger.error(f"Error creating notification: {e}")
            raise

    def get_pending_notifications(self) -> List[Dict]:
        """Get pending update requests (project_manager reviews these).

        Returns:
            List of pending notifications
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

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
            logger.error(f"Error getting notifications: {e}")
            return []

    def approve_notification(self, notification_id: int, processed_by: str) -> bool:
        """Approve and apply a notification (project_manager only).

        Args:
            notification_id: ID to approve
            processed_by: Must be "project_manager"

        Returns:
            True if successful

        Raises:
            PermissionError: If not project_manager
        """
        if processed_by != "project_manager":
            raise PermissionError("Only project_manager can approve notifications")

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get notification
            cursor.execute(
                """
                SELECT * FROM roadmap_update_notifications
                WHERE id = ? AND status = 'pending'
            """,
                (notification_id,),
            )

            notification = cursor.fetchone()
            if not notification:
                return False

            notification = dict(notification)

            # Apply the requested change
            if notification["notification_type"] == "status_update":
                # Update the item status
                cursor.execute(
                    """
                    UPDATE roadmap_items
                    SET status = ?, updated_at = ?, updated_by = ?
                    WHERE id = ?
                """,
                    (
                        notification["requested_status"],
                        datetime.now().isoformat(),
                        processed_by,
                        notification["item_id"],
                    ),
                )

            # Mark notification as approved
            cursor.execute(
                """
                UPDATE roadmap_update_notifications
                SET status = 'approved', processed_at = ?, processed_by = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), processed_by, notification_id),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Approved notification {notification_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error approving notification: {e}")
            return False

    def export_to_file(self, roadmap_path: Path) -> None:
        """Export database to ROADMAP.md file (BACKUP ONLY - DO NOT USE FOR NORMAL OPS).

        This should ONLY be used for backups or emergency recovery.
        Normal operations should NEVER read/write ROADMAP.md directly.

        Args:
            roadmap_path: Path to write ROADMAP.md

        Raises:
            PermissionError: If not project_manager
        """
        if not self.can_write:
            raise PermissionError("Only project_manager can export roadmap")

        logger.warning("⚠️  Exporting to file - this should only be used for backups!")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get header
        cursor.execute("SELECT value FROM roadmap_metadata WHERE key = ?", ("header",))
        result = cursor.fetchone()
        header = result["value"] if result else "# ROADMAP\n\n"

        # Get all items
        cursor.execute("SELECT * FROM roadmap_items ORDER BY section_order ASC")
        rows = cursor.fetchall()
        conn.close()

        # Build markdown
        lines = [header]
        for row in rows:
            if row["content"]:
                lines.append(row["content"])
            else:
                prefix = "##" if row["item_type"] == "user_story" else "###"
                item_id = f"US-{row['number']}" if row["item_type"] == "user_story" else f"PRIORITY {row['number']}"
                lines.append(f"{prefix} {item_id}: {row['title']} {row['status']}\n")

        roadmap_path.parent.mkdir(parents=True, exist_ok=True)
        roadmap_path.write_text("\n".join(lines))

        logger.info(f"✅ Exported {len(rows)} items to {roadmap_path} (backup only)")

    def import_from_file(self, roadmap_path: Path) -> int:
        """Import ROADMAP.md into database (ONE-TIME MIGRATION ONLY).

        This should ONLY be used for initial migration.
        After migration, NEVER read ROADMAP.md directly.

        Args:
            roadmap_path: Path to ROADMAP.md file

        Returns:
            Number of items imported

        Raises:
            PermissionError: If not project_manager
        """
        if not self.can_write:
            raise PermissionError("Only project_manager can import roadmap")

        logger.warning("⚠️  Importing from file - this should only be done ONCE for migration!")

        if not roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {roadmap_path}")

        content = roadmap_path.read_text()
        lines = content.split("\n")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Store header
        header_lines = []
        priority_start_idx = 0

        for idx, line in enumerate(lines):
            if re.match(r"^##\s+(US-|PRIORITY)", line) or re.match(r"^###\s+(🔴|PRIORITY|US-)", line):
                priority_start_idx = idx
                break
            header_lines.append(line)

        header = "\n".join(header_lines)
        cursor.execute(
            "INSERT OR REPLACE INTO roadmap_metadata (key, value, updated_at) VALUES (?, ?, ?)",
            ("header", header, datetime.now().isoformat()),
        )

        # Parse items
        items_imported = 0
        section_order = 0
        current_item = None
        current_content_lines = []

        patterns = [
            (r"^##\s+US-(\d+):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "user_story"),
            (r"^##\s+PRIORITY\s+(\d+(?:\.\d+)?):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "priority"),
            (r"^###\s+🔴\s+\*\*PRIORITY\s+(\d+(?:\.\d+)?):(.+?)\*\*.*$", "priority"),
            (r"^###\s+PRIORITY\s+(\d+(?:\.\d+)?):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "priority"),
            (r"^###\s+US-(\d+):(.+?)(?:\s+(📝|🔄|✅|⏸️|🚧).*)?$", "user_story"),
        ]

        for idx in range(priority_start_idx, len(lines)):
            line = lines[idx]
            matched = False

            for pattern, item_type in patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous item
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
        """Save an item during import."""
        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT OR REPLACE INTO roadmap_items (
                id, item_type, number, title, status, content, section_order,
                updated_at, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                "import",
            ),
        )

    def get_stats(self) -> Dict:
        """Get roadmap statistics (READ operation - all agents allowed).

        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total items
            cursor.execute("SELECT COUNT(*) FROM roadmap_items")
            total = cursor.fetchone()[0]

            # By status
            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN status LIKE '%📝%' OR status LIKE '%Planned%' THEN 1 ELSE 0 END) as planned,
                    SUM(CASE WHEN status LIKE '%🔄%' OR status LIKE '%Progress%' THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN status LIKE '%✅%' OR status LIKE '%Complete%' THEN 1 ELSE 0 END) as complete
                FROM roadmap_items
            """
            )

            row = cursor.fetchone()
            conn.close()

            return {
                "total": total,
                "planned": row[0] or 0,
                "in_progress": row[1] or 0,
                "complete": row[2] or 0,
                "completion_percentage": ((row[2] or 0) / total * 100) if total > 0 else 0,
            }

        except sqlite3.Error as e:
            logger.error(f"Error getting stats: {e}")
            return {}
