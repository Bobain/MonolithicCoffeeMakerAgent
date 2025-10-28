"""Database-backed ROADMAP management system.

This is the ONLY authorized way to access the ROADMAP.
Direct file access to ROADMAP.md is FORBIDDEN.

Architecture:
    - roadmap_priority table: Stores all priorities/user stories
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


class RoadmapDatabase:
    """Database-backed ROADMAP with enforced access control.

    This is the ONLY authorized way to interact with the ROADMAP.
    Direct file manipulation of ROADMAP.md is FORBIDDEN.

    Access Control:
        - Write operations: project_manager ONLY
        - Read operations: All agents
        - File operations: FORBIDDEN (use export_to_file only for backups)

    Example:
        >>> db = RoadmapDatabase()
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

            # Create simplified roadmap_priority table
            # PRIMARY KEY ensures id uniqueness
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_priority (
                    id TEXT PRIMARY KEY,            -- UNIQUE by definition
                    item_type TEXT NOT NULL,        -- 'user_story' or 'priority'
                    number TEXT NOT NULL,           -- "062", "1", "1.5"
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,           -- "📝 Planned", "🔄 In Progress", etc.
                    spec_id TEXT,                   -- Foreign key to specs_specification.id
                    content TEXT,                   -- Full markdown content
                    estimated_hours TEXT,           -- Time estimation
                    dependencies TEXT,              -- Dependency information
                    priority_order INTEGER NOT NULL UNIQUE, -- Priority ordering from ROADMAP.md
                    implementation_started_at TEXT, -- When code_developer started work (for stale detection)
                    updated_at TEXT NOT NULL,       -- ISO timestamp
                    updated_by TEXT NOT NULL,       -- Agent who updated
                    FOREIGN KEY (spec_id) REFERENCES specs_specification(id) ON DELETE SET NULL
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
                CREATE TABLE IF NOT EXISTS roadmap_notification (
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON roadmap_priority(item_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_status ON roadmap_priority(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_priority_order ON roadmap_priority(priority_order)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_number ON roadmap_priority(number)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_spec ON roadmap_priority(spec_id)"
            )  # Index for spec lookups
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_items_id ON roadmap_priority(id)"
            )  # Enforce uniqueness
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_item ON roadmap_audit(item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_status ON roadmap_notification(status)")

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
        estimated_hours: Optional[str] = None,
        dependencies: Optional[str] = None,
        priority_order: Optional[int] = None,
    ) -> bool:
        """Create a new roadmap item.

        Args:
            item_id: Unique ID (e.g., "US-062", "PRIORITY-1")
            item_type: "user_story" or "priority"
            number: Item number (e.g., "062", "1")
            title: Item title
            status: Status emoji and text
            content: Full markdown content
            estimated_hours: Time estimate
            dependencies: Dependencies info
            priority_order: Order in roadmap (defaults to max+1 if not specified)

        Returns:
            True if successful

        Raises:
            PermissionError: If agent is not project_manager
            sqlite3.IntegrityError: If id already exists

        Note:
            Phase field has been moved to specs_specification table.
            Each spec can have its own phase, allowing one roadmap item
            to have multiple phases across different specs.
        """
        if not self.can_write:
            raise PermissionError(f"Only project_manager can create items, not {self.agent_name}")

        now = datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # If priority_order not specified, default to max+1
            if priority_order is None:
                cursor.execute("SELECT MAX(priority_order) FROM roadmap_priority")
                max_order = cursor.fetchone()[0]
                priority_order = (max_order + 1) if max_order is not None else 1
                logger.info(f"Auto-assigned priority_order={priority_order} for {item_id}")

            cursor.execute(
                """
                INSERT INTO roadmap_priority (
                    id, item_type, number, title, status, content,
                    estimated_hours, dependencies, priority_order,
                    updated_at, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    item_type,
                    number,
                    title,
                    status,
                    content,
                    estimated_hours,
                    dependencies,
                    priority_order,
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
                    SELECT * FROM roadmap_priority
                    WHERE status LIKE ?
                    ORDER BY priority_order ASC
                """,
                    (f"%{status_filter}%",),
                )
            else:
                cursor.execute("SELECT * FROM roadmap_priority ORDER BY priority_order ASC")

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

            cursor.execute("SELECT * FROM roadmap_priority WHERE id = ?", (item_id,))
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
            cursor.execute("SELECT status FROM roadmap_priority WHERE id = ?", (item_id,))
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            old_status = result[0]
            now = datetime.now().isoformat()

            # Update status
            cursor.execute(
                """
                UPDATE roadmap_priority
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
                SELECT * FROM roadmap_priority
                WHERE status LIKE '📝%' OR status LIKE 'Planned%'
                ORDER BY priority_order ASC
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
                INSERT INTO roadmap_notification (
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
                SELECT * FROM roadmap_notification
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
                SELECT * FROM roadmap_notification
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
                    UPDATE roadmap_priority
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
                UPDATE roadmap_notification
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
        cursor.execute("SELECT * FROM roadmap_priority ORDER BY priority_order ASC")
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
        priority_order = 0
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
                        self._save_item(cursor, current_item, priority_order)
                        items_imported += 1
                        priority_order += 1

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
            self._save_item(cursor, current_item, priority_order)
            items_imported += 1

        conn.commit()
        conn.close()

        logger.info(f"✅ Imported {items_imported} items from {roadmap_path}")
        return items_imported

    def _save_item(self, cursor, item: Dict, priority_order: int) -> None:
        """Save an item during import."""
        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT OR REPLACE INTO roadmap_priority (
                id, item_type, number, title, status, content, priority_order,
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
                priority_order,
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
            cursor.execute("SELECT COUNT(*) FROM roadmap_priority")
            total = cursor.fetchone()[0]

            # By status
            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN status LIKE '%📝%' OR status LIKE '%Planned%' THEN 1 ELSE 0 END) as planned,
                    SUM(CASE WHEN status LIKE '%🔄%' OR status LIKE '%Progress%' THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN status LIKE '%✅%' OR status LIKE '%Complete%' THEN 1 ELSE 0 END) as complete
                FROM roadmap_priority
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

    def claim_spec_work(self, item_id: str) -> bool:
        """Claim a roadmap item for spec writing (prevents concurrent architects).

        This marks an item as being actively worked on by an architect.
        Prevents multiple architects from working on the same roadmap item simultaneously.

        Args:
            item_id: Item to claim (e.g., "PRIORITY-26")

        Returns:
            True if successfully claimed, False if already claimed or not found

        Note:
            With AgentRegistry singleton enforcement, there's only ONE architect instance,
            but this prevents the same architect from being invoked multiple times on
            the same item (e.g., by user or orchestrator).
        """
        if self.agent_name != "architect":
            raise PermissionError(f"Only architect can claim spec work, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if item exists and is not already claimed
            cursor.execute(
                "SELECT spec_work_started_at FROM roadmap_priority WHERE id = ?",
                (item_id,),
            )
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            started_at = result[0]

            if started_at:
                logger.warning(f"❌ Item {item_id} spec work already claimed at {started_at}")
                logger.warning("   Another architect is already working on this item's specs")
                return False

            # Claim the item
            now = datetime.now().isoformat()
            cursor.execute(
                """
                UPDATE roadmap_priority
                SET spec_work_started_at = ?
                WHERE id = ?
            """,
                (now, item_id),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ architect claimed spec work for {item_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error claiming spec work: {e}")
            return False

    def release_spec_work(self, item_id: str) -> bool:
        """Release claim on spec work (called when spec work is complete or aborted).

        Clears spec work tracking timestamp so item can be claimed again if needed.

        Args:
            item_id: Item to release (e.g., "PRIORITY-26")

        Returns:
            True if successfully released
        """
        if self.agent_name != "architect":
            raise PermissionError(f"Only architect can release spec work, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if item exists
            cursor.execute(
                "SELECT spec_work_started_at FROM roadmap_priority WHERE id = ?",
                (item_id,),
            )
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            # Release the item
            cursor.execute(
                """
                UPDATE roadmap_priority
                SET spec_work_started_at = NULL
                WHERE id = ?
            """,
                (item_id,),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Released spec work claim for {item_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error releasing spec work: {e}")
            return False

    def reset_stale_spec_work(self, stale_hours: int = 24) -> int:
        """Find and reset stale spec work sessions (>24h with no progress).

        This should be called periodically (e.g., by orchestrator or maintenance task)
        to recover from interrupted architect sessions.

        Args:
            stale_hours: Number of hours before considering spec work stale (default: 24)

        Returns:
            Number of stale spec work sessions reset
        """
        try:
            from datetime import timedelta

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calculate stale threshold
            threshold = (datetime.now() - timedelta(hours=stale_hours)).isoformat()

            # Find stale spec work
            cursor.execute(
                """
                SELECT id, spec_work_started_at
                FROM roadmap_priority
                WHERE spec_work_started_at IS NOT NULL
                AND spec_work_started_at < ?
            """,
                (threshold,),
            )

            stale_items = cursor.fetchall()

            if not stale_items:
                logger.info("No stale spec work sessions found")
                return 0

            # Reset each stale item
            count = 0
            for item_id, started_at in stale_items:
                cursor.execute(
                    """
                    UPDATE roadmap_priority
                    SET spec_work_started_at = NULL
                    WHERE id = ?
                """,
                    (item_id,),
                )
                count += 1
                logger.warning(f"Reset stale spec work for {item_id} (started {started_at})")

            conn.commit()
            conn.close()

            logger.info(f"✅ Reset {count} stale spec work sessions")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error resetting stale spec work: {e}")
            return 0

    def claim_implementation(self, item_id: str, developer: str = "code_developer") -> bool:
        """Claim a roadmap item for implementation (tracks start time for stale detection).

        This marks an item as being actively worked on by code_developer.
        Used for stale work detection (>24 hours with no progress).

        Args:
            item_id: Item to claim (e.g., "PRIORITY-27")
            developer: Ignored (kept for API compatibility, uses singleton code_developer)

        Returns:
            True if successfully claimed, False if already claimed or not found

        Note:
            With singleton agent enforcement (CFR-000), there's only ever ONE code_developer,
            so we only track when work started, not who started it.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if item exists and is not already claimed
            cursor.execute(
                "SELECT implementation_started_at FROM roadmap_priority WHERE id = ?",
                (item_id,),
            )
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            started_at = result[0]

            if started_at:
                logger.warning(f"Item {item_id} already claimed at {started_at}")
                return False

            # Claim the item
            now = datetime.now().isoformat()
            cursor.execute(
                """
                UPDATE roadmap_priority
                SET implementation_started_at = ?
                WHERE id = ?
            """,
                (now, item_id),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ code_developer claimed {item_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error claiming implementation: {e}")
            return False

    def release_implementation(self, item_id: str, developer: str = "code_developer") -> bool:
        """Release claim on a roadmap item (called on completion or abort).

        Clears implementation tracking timestamp so item can be claimed again if needed.

        Args:
            item_id: Item to release (e.g., "PRIORITY-27")
            developer: Ignored (kept for API compatibility)

        Returns:
            True if successfully released
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if item exists
            cursor.execute(
                "SELECT id FROM roadmap_priority WHERE id = ?",
                (item_id,),
            )
            result = cursor.fetchone()

            if not result:
                logger.error(f"Item not found: {item_id}")
                return False

            # Release the item
            cursor.execute(
                """
                UPDATE roadmap_priority
                SET implementation_started_at = NULL
                WHERE id = ?
            """,
                (item_id,),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Released {item_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error releasing implementation: {e}")
            return False

    def reset_stale_implementations(self, stale_hours: int = 24) -> int:
        """Find and reset stale implementations (>24h with no progress).

        This should be called periodically (e.g., by orchestrator or maintenance task)
        to recover from interrupted code_developer sessions.

        Args:
            stale_hours: Number of hours before considering implementation stale (default: 24)

        Returns:
            Number of stale implementations reset
        """
        try:
            from datetime import timedelta

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calculate stale threshold
            threshold = (datetime.now() - timedelta(hours=stale_hours)).isoformat()

            # Find stale implementations
            cursor.execute(
                """
                SELECT id, implementation_started_at
                FROM roadmap_priority
                WHERE implementation_started_at IS NOT NULL
                AND implementation_started_at < ?
                AND (status LIKE '%🔄%' OR status LIKE '%Progress%')
            """,
                (threshold,),
            )

            stale_items = cursor.fetchall()

            if not stale_items:
                logger.info("No stale implementations found")
                return 0

            # Reset each stale item
            count = 0
            for item_id, started_at in stale_items:
                cursor.execute(
                    """
                    UPDATE roadmap_priority
                    SET implementation_started_at = NULL
                    WHERE id = ?
                """,
                    (item_id,),
                )

                logger.warning(f"⚠️ Reset stale implementation: {item_id} " f"(claimed at {started_at}, no progress)")
                count += 1

            conn.commit()
            conn.close()

            logger.info(f"✅ Reset {count} stale implementations")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error resetting stale implementations: {e}")
            return 0

    def get_items_with_specs(self) -> List[Dict]:
        """Get all roadmap items that have associated specs.

        Useful for finding items ready for implementation.

        Returns:
            List of dicts with roadmap + spec information (JOINed data)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    r.*,
                    s.title as spec_title,
                    s.status as spec_status,
                    s.spec_type,
                    s.estimated_hours as spec_hours
                FROM roadmap_priority r
                INNER JOIN specs_specification s ON r.spec_id = s.id
                ORDER BY r.priority_order ASC
            """
            )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting items with specs: {e}")
            return []

    def get_items_needing_specs(self) -> List[Dict]:
        """Get roadmap items without technical specs.

        Useful for architect to identify what needs design work.

        Returns:
            List of roadmap items missing specs (planned items only)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM roadmap_priority
                WHERE spec_id IS NULL
                AND status LIKE '%Planned%'
                ORDER BY priority_order ASC
            """
            )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting items needing specs: {e}")
            return []

    def update_plan_and_summary(self, item_id: str, plan_and_summary: Dict | str) -> bool:
        """Update plan_and_summary for a roadmap item (architect only).

        This enables progressive work across multiple architect sessions.

        Args:
            item_id: Roadmap item ID (e.g., "PRIORITY-26")
            plan_and_summary: Plan dict or JSON string with:
                {
                    "overview": "High-level description",
                    "sections_planned": ["section1", ...],
                    "sections_completed": [...],
                    "next_steps": "What to do next",
                    "blockers": [...],
                    "work_sessions": N
                }

        Returns:
            True if successful

        Raises:
            PermissionError: If not architect
        """
        if self.agent_name != "architect":
            raise PermissionError(f"Only architect can update plan_and_summary, not {self.agent_name}")

        import json

        # Convert dict to JSON if needed
        if isinstance(plan_and_summary, dict):
            plan_json = json.dumps(plan_and_summary, indent=2)
        else:
            plan_json = plan_and_summary

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE roadmap_priority
                SET plan_and_summary = ?, updated_at = ?
                WHERE id = ?
            """,
                (plan_json, datetime.now().isoformat(), item_id),
            )

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if success:
                logger.info(f"✅ Updated plan_and_summary for {item_id}")
            else:
                logger.warning(f"Item {item_id} not found")

            return success

        except sqlite3.Error as e:
            logger.error(f"Error updating plan_and_summary: {e}")
            return False

    def get_plan_and_summary(self, item_id: str) -> Optional[Dict]:
        """Get plan_and_summary for a roadmap item (all agents can read).

        Args:
            item_id: Roadmap item ID

        Returns:
            Plan dict or None if not found
        """
        item = self.get_item(item_id)
        if not item or not item.get("plan_and_summary"):
            return None

        import json

        try:
            return json.loads(item["plan_and_summary"])
        except (json.JSONDecodeError, TypeError):
            logger.error(f"Invalid plan_and_summary JSON for {item_id}")
            return None

    def find_reusable_components(self, search_terms: Optional[List[str]] = None) -> List[Dict]:
        """Find reusable components from completed roadmap items (all agents can read).

        This helps architect identify existing components when working on new specs.

        Args:
            search_terms: Optional list of keywords to filter components
                         (e.g., ["JWT", "email", "validation"])

        Returns:
            List of reusable components with source info:
            [
                {
                    "component_name": "JWT token generator",
                    "source_item_id": "PRIORITY-26",
                    "source_item_title": "Authentication System",
                    "location": "SPEC-132 /implementation section",
                    "use_cases": ["API auth", "Session management"],
                    "architecture_overview": "Complete auth system..."
                },
                ...
            ]
        """

        all_items = self.get_all_items()
        reusable_components = []

        for item in all_items:
            plan = self.get_plan_and_summary(item["id"])

            # Only consider items with completed tech specs
            if not plan or not plan.get("tech_specs_complete"):
                continue

            components = plan.get("reusable_components", [])
            architecture_summary = plan.get("architecture_summary", {})

            for component in components:
                # Filter by search terms if provided
                if search_terms:
                    component_text = (
                        f"{component.get('name', '')} " f"{' '.join(component.get('use_cases', []))}"
                    ).lower()

                    if not any(term.lower() in component_text for term in search_terms):
                        continue

                reusable_components.append(
                    {
                        "component_name": component.get("name"),
                        "source_item_id": item["id"],
                        "source_item_title": item.get("title", "Unknown"),
                        "location": component.get("location"),
                        "use_cases": component.get("use_cases", []),
                        "architecture_overview": architecture_summary.get("overview", ""),
                    }
                )

        logger.info(f"Found {len(reusable_components)} reusable components")
        return reusable_components

    # ==================== CODE REVIEW SYSTEM ====================

    def track_commit(
        self,
        roadmap_item_id: str,
        commit_hash: str,
        commit_message: str,
        commit_author: str,
        commit_date: str,
        files_changed: list[str],
        insertions: int,
        deletions: int,
    ) -> bool:
        """Track a commit for later review (code_developer only).

        Args:
            roadmap_item_id: Roadmap item being implemented
            commit_hash: Git commit hash
            commit_message: Commit message
            commit_author: Commit author
            commit_date: ISO timestamp
            files_changed: List of file paths
            insertions: Lines added
            deletions: Lines removed

        Returns:
            True if successful
        """
        if self.agent_name != "code_developer":
            raise PermissionError(f"Only code_developer can track commits, not {self.agent_name}")

        import json

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO review_commit (
                    roadmap_item_id, commit_hash, commit_message, commit_author,
                    commit_date, files_changed, insertions, deletions, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    roadmap_item_id,
                    commit_hash,
                    commit_message,
                    commit_author,
                    commit_date,
                    json.dumps(files_changed),
                    insertions,
                    deletions,
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Tracked commit {commit_hash[:7]} for {roadmap_item_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error tracking commit: {e}")
            return False

    def get_commits_for_review(self, roadmap_item_id: str) -> list[Dict]:
        """Get all commits for a roadmap item (for review).

        Args:
            roadmap_item_id: Roadmap item ID

        Returns:
            List of commit dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM review_commit
                WHERE roadmap_item_id = ?
                ORDER BY commit_date ASC
            """,
                (roadmap_item_id,),
            )

            commits = [dict(row) for row in cursor.fetchall()]
            conn.close()

            # Parse JSON fields
            import json

            for commit in commits:
                commit["files_changed"] = json.loads(commit["files_changed"])

            return commits

        except sqlite3.Error as e:
            logger.error(f"Error getting commits: {e}")
            return []

    def create_code_review(
        self,
        roadmap_item_id: str,
        spec_id: str,
        summary: str,
        quality_score: int,
        critical_issues: list[str],
        warnings: list[str],
        suggestions: list[str],
        follows_spec: bool,
        test_coverage_ok: bool,
        style_compliant: bool,
        commits_reviewed: int,
    ) -> bool:
        """Create code review summary (code_reviewer only).

        Args:
            roadmap_item_id: Roadmap item reviewed
            spec_id: Technical spec ID
            summary: Overall review summary
            quality_score: 1-10 score
            critical_issues: List of critical issues
            warnings: List of warnings
            suggestions: List of suggestions
            follows_spec: Implementation follows spec?
            test_coverage_ok: Adequate test coverage?
            style_compliant: Follows style guide?
            commits_reviewed: Number of commits reviewed

        Returns:
            True if successful
        """
        if self.agent_name != "code_reviewer":
            raise PermissionError(f"Only code_reviewer can create reviews, not {self.agent_name}")

        import json

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute(
                """
                INSERT OR REPLACE INTO review_code_review (
                    roadmap_item_id, spec_id, review_date, reviewer,
                    commits_reviewed, summary, quality_score,
                    critical_issues, warnings, suggestions,
                    follows_spec, test_coverage_ok, style_compliant,
                    architect_reviewed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    roadmap_item_id,
                    spec_id,
                    now,
                    "code_reviewer",
                    commits_reviewed,
                    summary,
                    quality_score,
                    json.dumps(critical_issues),
                    json.dumps(warnings),
                    json.dumps(suggestions),
                    follows_spec,
                    test_coverage_ok,
                    style_compliant,
                    False,  # architect_reviewed
                    now,
                    now,
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Created code review for {roadmap_item_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error creating code review: {e}")
            return False

    def delete_reviewed_commits(self, roadmap_item_id: str) -> int:
        """Delete commits after review is complete (code_reviewer only).

        Args:
            roadmap_item_id: Roadmap item ID

        Returns:
            Number of commits deleted
        """
        if self.agent_name != "code_reviewer":
            raise PermissionError(f"Only code_reviewer can delete commits, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM review_commit WHERE roadmap_item_id = ?", (roadmap_item_id,))

            count = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"✅ Deleted {count} reviewed commits for {roadmap_item_id}")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error deleting commits: {e}")
            return 0

    def get_unreviewed_review_code_review(self) -> list[Dict]:
        """Get code reviews not yet reviewed by architect (all agents can read).

        Returns:
            List of code review dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM review_code_review
                WHERE architect_reviewed = FALSE
                ORDER BY review_date DESC
            """
            )

            reviews = [dict(row) for row in cursor.fetchall()]
            conn.close()

            # Parse JSON fields
            import json

            for review in reviews:
                review["critical_issues"] = json.loads(review["critical_issues"])
                review["warnings"] = json.loads(review["warnings"])
                review["suggestions"] = json.loads(review["suggestions"])

            return reviews

        except sqlite3.Error as e:
            logger.error(f"Error getting unreviewed code reviews: {e}")
            return []

    def mark_review_as_read(self, roadmap_item_id: str, architect_comments: str = None) -> bool:
        """Mark code review as read by architect (architect only).

        Args:
            roadmap_item_id: Roadmap item ID
            architect_comments: Optional comments from architect

        Returns:
            True if successful
        """
        if self.agent_name != "architect":
            raise PermissionError(f"Only architect can mark reviews as read, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE review_code_review
                SET architect_reviewed = TRUE,
                    architect_reviewed_at = ?,
                    architect_comments = ?,
                    updated_at = ?
                WHERE roadmap_item_id = ?
            """,
                (datetime.now().isoformat(), architect_comments, datetime.now().isoformat(), roadmap_item_id),
            )

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if success:
                logger.info(f"✅ Marked review as read for {roadmap_item_id}")

            return success

        except sqlite3.Error as e:
            logger.error(f"Error marking review as read: {e}")
            return False

    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics.

        Returns:
            Dict with counts for roadmap items, specs, linkage, etc.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get roadmap item count
            cursor.execute("SELECT COUNT(*) FROM roadmap_priority")
            total_items = cursor.fetchone()[0]

            # Get items with specs
            cursor.execute("SELECT COUNT(*) FROM roadmap_priority WHERE spec_id IS NOT NULL")
            items_with_specs = cursor.fetchone()[0]

            # Get total specs (check if table exists)
            try:
                cursor.execute("SELECT COUNT(*) FROM specs_specification")
                total_specs = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM specs_specification WHERE status = 'complete'")
                complete_specs = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                # specs_specification table doesn't exist
                total_specs = 0
                complete_specs = 0

            # Get items ready for implementation (has spec, is planned)
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM roadmap_priority r
                WHERE r.spec_id IS NOT NULL
                AND r.status LIKE '%Planned%'
            """
            )
            ready_for_impl = cursor.fetchone()[0]

            conn.close()

            return {
                "total_roadmap_priority": total_items,
                "roadmap_priority_with_specs": items_with_specs,
                "total_specs": total_specs,
                "complete_specs": complete_specs,
                "items_ready_for_implementation": ready_for_impl,
            }

        except sqlite3.Error as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    # ========================================================================
    # Technical Specifications (Hierarchical Spec Support)
    # ========================================================================

    def create_technical_spec(
        self,
        spec_number: int,
        title: str,
        roadmap_item_id: str,
        spec_type: str = "monolithic",
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        estimated_hours: Optional[float] = None,
        dependencies: Optional[str] = None,
        total_phases: Optional[int] = None,
        phase_files: Optional[List[str]] = None,
    ) -> str:
        """Create a technical specification entry in the database.

        This method is ONLY callable by architect agent. It creates a new
        technical spec record and optionally links it to a roadmap item.

        Args:
            spec_number: Unique spec number (e.g., 104 for SPEC-104)
            title: Spec title (e.g., "Orchestrator Continuous Work Loop")
            roadmap_item_id: Roadmap item this spec implements (e.g., "US-104")
            spec_type: "monolithic" or "hierarchical" (default: "monolithic")
            file_path: Path to spec file or directory
            content: Full spec content (for monolithic) or README content (for hierarchical)
            estimated_hours: Total estimated implementation time
            dependencies: JSON string of spec dependencies
            total_phases: Number of phases (for hierarchical specs)
            phase_files: List of phase file names (for hierarchical specs)

        Returns:
            spec_id: The created spec ID (e.g., "SPEC-104")

        Raises:
            PermissionError: If agent is not architect
            ValueError: If spec_number already exists
        """
        if not self.can_write:
            raise PermissionError(f"Only architect can create specs, not {self.agent_name}")

        spec_id = f"SPEC-{spec_number:03d}"
        now = datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if spec_number already exists
            cursor.execute("SELECT id FROM specs_specification WHERE spec_number = ?", (spec_number,))
            if cursor.fetchone():
                conn.close()
                raise ValueError(f"Spec number {spec_number} already exists")

            # Prepare phase_files JSON
            phase_files_json = None
            if phase_files:
                import json

                phase_files_json = json.dumps(phase_files)

            # Insert spec
            cursor.execute(
                """
                INSERT INTO specs_specification (
                    id, spec_number, title, roadmap_item_id,
                    status, spec_type, file_path, content,
                    dependencies, estimated_hours,
                    updated_at, updated_by,
                    total_phases, phase_files
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    spec_id,
                    spec_number,
                    title,
                    roadmap_item_id,
                    "draft",
                    spec_type,
                    file_path,
                    content,
                    dependencies,
                    estimated_hours,
                    now,
                    self.agent_name,
                    total_phases,
                    phase_files_json,
                ),
            )

            # Update roadmap item to link spec (if roadmap_item_id provided)
            if roadmap_item_id:
                cursor.execute(
                    """
                    UPDATE roadmap_priority
                    SET spec_id = ?, updated_at = ?, updated_by = ?
                    WHERE id = ?
                """,
                    (spec_id, now, self.agent_name, roadmap_item_id),
                )

            conn.commit()
            conn.close()

            logger.info(f"Created {spec_type} spec: {spec_id} for {roadmap_item_id}")
            return spec_id

        except sqlite3.Error as e:
            logger.error(f"Error creating technical spec: {e}")
            raise

    def update_technical_spec(
        self,
        spec_id: str,
        status: Optional[str] = None,
        content: Optional[str] = None,
        current_phase: Optional[int] = None,
        phase_status: Optional[str] = None,
        actual_hours: Optional[float] = None,
        **kwargs,
    ) -> bool:
        """Update an existing technical specification.

        Args:
            spec_id: Spec ID to update (e.g., "SPEC-104")
            status: New status ("draft", "approved", "complete", "deprecated")
            content: Updated content
            current_phase: Current phase number (for hierarchical specs)
            phase_status: Status of current phase ("in_progress", "completed")
            actual_hours: Actual implementation time
            **kwargs: Other fields to update

        Returns:
            bool: True if updated successfully

        Raises:
            PermissionError: If agent is not architect
        """
        if not self.can_write:
            raise PermissionError(f"Only architect can update specs, not {self.agent_name}")

        now = datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build dynamic UPDATE query
            updates = []
            values = []

            if status is not None:
                updates.append("status = ?")
                values.append(status)

            if content is not None:
                updates.append("content = ?")
                values.append(content)

            if current_phase is not None:
                updates.append("phase = ?")
                values.append(str(current_phase))

            if phase_status is not None:
                updates.append("current_phase_status = ?")
                values.append(phase_status)

            if actual_hours is not None:
                updates.append("actual_hours = ?")
                values.append(actual_hours)

            # Add any extra kwargs
            for key, value in kwargs.items():
                updates.append(f"{key} = ?")
                values.append(value)

            # Always update metadata
            updates.extend(["updated_at = ?", "updated_by = ?"])
            values.extend([now, self.agent_name])

            # Add spec_id to WHERE clause
            values.append(spec_id)

            query = f"""
                UPDATE specs_specification
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, values)
            rows_affected = cursor.rowcount

            conn.commit()
            conn.close()

            if rows_affected > 0:
                logger.info(f"Updated spec {spec_id}")
                return True
            else:
                logger.warning(f"Spec {spec_id} not found")
                return False

        except sqlite3.Error as e:
            logger.error(f"Error updating technical spec: {e}")
            return False

    def get_technical_spec(
        self, spec_id: Optional[str] = None, roadmap_item_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Get technical specification by ID or roadmap item.

        Args:
            spec_id: Spec ID (e.g., "SPEC-104")
            roadmap_item_id: Roadmap item ID (e.g., "US-104")

        Returns:
            Dict with spec information, or None if not found
        """
        if not spec_id and not roadmap_item_id:
            raise ValueError("Must provide either spec_id or roadmap_item_id")

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if spec_id:
                cursor.execute("SELECT * FROM specs_specification WHERE id = ?", (spec_id,))
            else:
                cursor.execute("SELECT * FROM specs_specification WHERE roadmap_item_id = ?", (roadmap_item_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                spec = dict(row)
                # Parse phase_files JSON if present
                if spec.get("phase_files"):
                    import json

                    try:
                        spec["phase_files"] = json.loads(spec["phase_files"])
                    except json.JSONDecodeError:
                        spec["phase_files"] = []
                return spec
            return None

        except sqlite3.Error as e:
            logger.error(f"Error getting technical spec: {e}")
            return None

    def get_all_specs_specification(self, status: Optional[str] = None, spec_type: Optional[str] = None) -> List[Dict]:
        """Get all technical specifications with optional filtering.

        Args:
            status: Filter by status ("draft", "approved", "complete", "deprecated")
            spec_type: Filter by type ("monolithic", "hierarchical")

        Returns:
            List of spec dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM specs_specification WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)

            if spec_type:
                query += " AND spec_type = ?"
                params.append(spec_type)

            query += " ORDER BY spec_number ASC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            specs = []
            for row in rows:
                spec = dict(row)
                # Parse phase_files JSON
                if spec.get("phase_files"):
                    import json

                    try:
                        spec["phase_files"] = json.loads(spec["phase_files"])
                    except json.JSONDecodeError:
                        spec["phase_files"] = []
                specs.append(spec)

            return specs

        except sqlite3.Error as e:
            logger.error(f"Error getting all technical specs: {e}")
            return []
