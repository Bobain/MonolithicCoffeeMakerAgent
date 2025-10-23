"""Unified Database for Roadmap and Technical Specifications.

This module provides a single database containing both roadmap items and technical specs,
enabling efficient JOIN operations and maintaining referential integrity.

Per CFR-015: Database stored in data/unified_roadmap_specs.db

Features:
    - Single database for roadmap and specs (easier JOINs)
    - Foreign key constraints enforced
    - Hierarchical spec content support (JSON)
    - Efficient indexes for JOIN operations
    - Audit trail for all changes

Access Control:
    - Roadmap write: project_manager only
    - Spec write: architect only
    - Read: All agents

Migration:
    This database consolidates:
    - data/roadmap.db → unified database
    - data/specs.db → unified database
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class UnifiedDatabase:
    """Unified database for roadmap and technical specifications.

    Provides single source of truth for both roadmap items and technical specs,
    enabling efficient JOIN operations and maintaining data integrity.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize unified database.

        Args:
            db_path: Path to SQLite database (default: data/unified_roadmap_specs.db)
        """
        if db_path is None:
            db_path = Path("data/unified_roadmap_specs.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_database()
        logger.info(f"UnifiedDatabase initialized at {self.db_path}")

    def _init_database(self) -> None:
        """Initialize database schema with both roadmap and spec tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")

            # Technical specifications table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS technical_specs (
                    id TEXT PRIMARY KEY,                -- e.g., "SPEC-115"
                    spec_number INTEGER NOT NULL UNIQUE, -- e.g., 115
                    title TEXT NOT NULL,
                    roadmap_item_id TEXT,               -- e.g., "US-062", "PRIORITY-26"
                    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'in_progress', 'complete', 'approved'
                    spec_type TEXT DEFAULT 'monolithic',  -- 'monolithic' or 'hierarchical'
                    phase TEXT,                         -- Phase grouping (moved from roadmap_items)
                    file_path TEXT,                     -- Path to backup file (reference only)
                    content TEXT,                       -- Full content (JSON for hierarchical)
                    dependencies TEXT,                  -- JSON array of spec IDs
                    estimated_hours REAL,
                    actual_hours REAL,
                    started_at TEXT,                    -- When spec work started (for stale detection)
                    updated_at TEXT NOT NULL,
                    updated_by TEXT NOT NULL
                )
            """
            )

            # Roadmap items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_items (
                    id TEXT PRIMARY KEY,                -- e.g., "US-062", "PRIORITY-26"
                    item_type TEXT NOT NULL,            -- 'user_story' or 'priority'
                    number TEXT NOT NULL,               -- "062", "26"
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,               -- "📝 Planned", "🔄 In Progress", etc.
                    spec_id TEXT,                       -- Foreign key to technical_specs
                    content TEXT,                       -- Full markdown content
                    estimated_hours TEXT,
                    dependencies TEXT,
                    section_order INTEGER NOT NULL,
                    implementation_started_at TEXT,     -- When code_developer started work (for stale detection)
                    updated_at TEXT NOT NULL,
                    updated_by TEXT NOT NULL,
                    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
                )
            """
            )

            # Roadmap metadata table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roadmap_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """
            )

            # Audit trail table (combined for both)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,           -- 'roadmap_items' or 'technical_specs'
                    item_id TEXT NOT NULL,
                    action TEXT NOT NULL,               -- 'create', 'update', 'delete'
                    field_changed TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by TEXT NOT NULL,
                    changed_at TEXT NOT NULL
                )
            """
            )

            # Notification table for inter-agent communication
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_agent TEXT NOT NULL,         -- Who should handle this
                    source_agent TEXT NOT NULL,         -- Who sent this
                    notification_type TEXT NOT NULL,    -- 'status_update', 'spec_complete', etc.
                    item_id TEXT,                       -- Related item
                    message TEXT,
                    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'processed', 'ignored'
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    processed_by TEXT,
                    notes TEXT
                )
            """
            )

            # Work sessions table for parallel development tracking
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS work_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_id TEXT NOT NULL UNIQUE,           -- e.g., "WORK-42"
                    spec_id TEXT NOT NULL,                  -- Links to technical_specs.id
                    roadmap_item_id TEXT,                   -- Links to roadmap_items.id
                    scope TEXT NOT NULL,                    -- "phase", "section", "module"
                    scope_description TEXT,                 -- Human-readable scope description
                    assigned_files TEXT,                    -- JSON array of file paths this work touches
                    branch_name TEXT NOT NULL UNIQUE,       -- e.g., "roadmap-work-42"
                    worktree_path TEXT,                     -- Path to git worktree
                    status TEXT NOT NULL DEFAULT 'pending', -- "pending", "in_progress", "completed", "failed"
                    claimed_by TEXT,                        -- "code_developer"
                    claimed_at TEXT,                        -- When work was claimed
                    started_at TEXT,                        -- When work actually started
                    completed_at TEXT,                      -- When work finished
                    commit_sha TEXT,                        -- Final commit SHA
                    merged_at TEXT,                         -- When merged to roadmap branch
                    created_by TEXT NOT NULL DEFAULT 'architect', -- Who created this work session
                    created_at TEXT NOT NULL,               -- When work session was created

                    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE CASCADE,
                    FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id) ON DELETE SET NULL
                )
            """
            )

            # Code review reports table (replaces file-based reviews)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS review_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_review_id INTEGER NOT NULL,       -- Links to commit_reviews
                    commit_sha TEXT NOT NULL,
                    spec_id TEXT,                            -- Links to technical_specs

                    -- Report metadata
                    date TEXT NOT NULL,
                    reviewer TEXT NOT NULL DEFAULT 'code_reviewer',
                    review_duration_seconds REAL,

                    -- Metrics
                    files_changed INTEGER,
                    lines_added INTEGER,
                    lines_deleted INTEGER,
                    quality_score INTEGER NOT NULL,          -- 0-100
                    approved BOOLEAN NOT NULL,

                    -- Issues (JSON)
                    issues TEXT,                             -- JSON array of Issue objects
                    style_compliance TEXT,                   -- JSON dict
                    architecture_compliance TEXT,            -- JSON dict

                    -- Content
                    overall_assessment TEXT NOT NULL,
                    full_report_markdown TEXT,               -- Full markdown content

                    -- Architect follow-up
                    needs_architect_review BOOLEAN DEFAULT 0,
                    architect_reviewed_at TEXT,
                    architect_notes TEXT,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY (commit_review_id) REFERENCES commit_reviews(id) ON DELETE CASCADE,
                    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
                )
            """
            )

            # Create indexes for performance
            # Specs indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_specs_roadmap ON technical_specs(roadmap_item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_specs_status ON technical_specs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_specs_number ON technical_specs(spec_number)")

            # Roadmap indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_roadmap_spec ON roadmap_items(spec_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_roadmap_status ON roadmap_items(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_roadmap_order ON roadmap_items(section_order)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_roadmap_type ON roadmap_items(item_type)")

            # Review reports indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reports_score ON review_reports(quality_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reports_spec ON review_reports(spec_id)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_review_reports_needs_review ON review_reports(needs_architect_review)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reports_approved ON review_reports(approved)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reports_commit ON review_reports(commit_review_id)")

            # Audit/notification indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_item ON audit_trail(item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_table ON audit_trail(table_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_target ON notifications(target_agent)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status)")

            # Work sessions indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_status ON work_sessions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_spec ON work_sessions(spec_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_roadmap ON work_sessions(roadmap_item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_branch ON work_sessions(branch_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_claimed_at ON work_sessions(claimed_at)")

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Error initializing unified database: {e}")
            raise

    # ==================== JOIN QUERIES ====================

    def get_next_implementation_task(self) -> Optional[Dict]:
        """Get next roadmap item with complete spec ready for implementation.

        This performs an efficient JOIN between roadmap_items and technical_specs.

        Returns:
            Dict with complete roadmap + spec information, or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    r.id as roadmap_id,
                    r.title as roadmap_title,
                    r.content as roadmap_content,
                    r.status as roadmap_status,
                    r.item_type,
                    r.number as item_number,
                    r.estimated_hours as roadmap_hours,
                    s.id as spec_id,
                    s.title as spec_title,
                    s.spec_type,
                    s.content as spec_content,
                    s.estimated_hours as spec_hours,
                    s.dependencies
                FROM roadmap_items r
                INNER JOIN technical_specs s ON r.spec_id = s.id
                WHERE
                    (r.status LIKE '%📝%' OR r.status LIKE '%Planned%')
                    AND s.status IN ('complete', 'approved')
                ORDER BY r.section_order ASC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                result = dict(row)
                # Parse JSON fields
                if result.get("dependencies"):
                    result["dependencies"] = json.loads(result["dependencies"])
                return result

            return None

        except sqlite3.Error as e:
            logger.error(f"Error getting next implementation task: {e}")
            return None

    def get_items_with_specs(self) -> List[Dict]:
        """Get all roadmap items that have associated specs.

        Returns:
            List of dicts with roadmap + spec information
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
                FROM roadmap_items r
                INNER JOIN technical_specs s ON r.spec_id = s.id
                ORDER BY r.section_order ASC
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
            List of roadmap items missing specs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM roadmap_items
                WHERE
                    spec_id IS NULL
                    AND status NOT LIKE '%✅%'
                    AND status NOT LIKE '%Complete%'
                ORDER BY section_order ASC
            """
            )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting items needing specs: {e}")
            return []

    # ==================== MIGRATION HELPERS ====================

    def migrate_from_separate_databases(
        self, roadmap_db_path: Optional[Path] = None, specs_db_path: Optional[Path] = None
    ) -> Tuple[int, int]:
        """Migrate data from separate roadmap and specs databases.

        Args:
            roadmap_db_path: Path to old roadmap.db
            specs_db_path: Path to old specs.db

        Returns:
            Tuple of (roadmap_items_migrated, specs_migrated)
        """
        roadmap_migrated = 0
        specs_migrated = 0

        # Default paths
        if roadmap_db_path is None:
            roadmap_db_path = Path("data/roadmap.db")
        if specs_db_path is None:
            specs_db_path = Path("data/specs.db")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Migrate specs first (no foreign key dependencies)
            if specs_db_path.exists():
                cursor.execute(f"ATTACH DATABASE '{specs_db_path}' AS old_specs")
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO technical_specs
                    SELECT * FROM old_specs.technical_specs
                """
                )
                specs_migrated = cursor.rowcount
                cursor.execute("DETACH DATABASE old_specs")

            # Migrate roadmap items
            if roadmap_db_path.exists():
                cursor.execute(f"ATTACH DATABASE '{roadmap_db_path}' AS old_roadmap")

                # Check if the old schema has spec_id column
                cursor.execute("PRAGMA old_roadmap.table_info(roadmap_items)")
                columns = [col[1] for col in cursor.fetchall()]

                if "spec_id" in columns:
                    # Direct migration with spec_id
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO roadmap_items
                        SELECT * FROM old_roadmap.roadmap_items
                    """
                    )
                else:
                    # Migration without spec_id (add NULL for that column)
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO roadmap_items (
                            id, item_type, number, title, status,
                            spec_id, content, phase, estimated_hours,
                            dependencies, section_order, updated_at, updated_by
                        )
                        SELECT
                            id, item_type, number, title, status,
                            NULL, content, phase, estimated_hours,
                            dependencies, section_order, updated_at, updated_by
                        FROM old_roadmap.roadmap_items
                    """
                    )

                roadmap_migrated = cursor.rowcount

                # Also migrate metadata
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO roadmap_metadata
                    SELECT * FROM old_roadmap.roadmap_metadata
                """
                )

                cursor.execute("DETACH DATABASE old_roadmap")

            conn.commit()
            conn.close()

            logger.info(f"✅ Migrated {roadmap_migrated} roadmap items and {specs_migrated} specs")
            return roadmap_migrated, specs_migrated

        except sqlite3.Error as e:
            logger.error(f"Error during migration: {e}")
            raise

    def link_spec_to_roadmap(self, roadmap_id: str, spec_id: str) -> bool:
        """Link a technical spec to a roadmap item.

        Args:
            roadmap_id: Roadmap item ID (e.g., "PRIORITY-26")
            spec_id: Spec ID (e.g., "SPEC-115")

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update roadmap item with spec_id
            cursor.execute(
                """
                UPDATE roadmap_items
                SET spec_id = ?, updated_at = ?, updated_by = ?
                WHERE id = ?
            """,
                (spec_id, datetime.now().isoformat(), "system", roadmap_id),
            )

            success = cursor.rowcount > 0

            # Also update spec with roadmap_item_id
            cursor.execute(
                """
                UPDATE technical_specs
                SET roadmap_item_id = ?, updated_at = ?, updated_by = ?
                WHERE id = ?
            """,
                (roadmap_id, datetime.now().isoformat(), "system", spec_id),
            )

            conn.commit()
            conn.close()

            if success:
                logger.info(f"✅ Linked {spec_id} to {roadmap_id}")

            return success

        except sqlite3.Error as e:
            logger.error(f"Error linking spec to roadmap: {e}")
            return False

    def get_database_stats(self) -> Dict:
        """Get statistics about the unified database.

        Returns:
            Dict with counts and statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats = {}

            # Roadmap stats
            cursor.execute("SELECT COUNT(*) FROM roadmap_items")
            stats["total_roadmap_items"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM roadmap_items WHERE spec_id IS NOT NULL")
            stats["roadmap_items_with_specs"] = cursor.fetchone()[0]

            # Spec stats
            cursor.execute("SELECT COUNT(*) FROM technical_specs")
            stats["total_specs"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM technical_specs WHERE status = 'complete'")
            stats["complete_specs"] = cursor.fetchone()[0]

            # JOIN stats
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM roadmap_items r
                INNER JOIN technical_specs s ON r.spec_id = s.id
                WHERE s.status IN ('complete', 'approved')
                AND (r.status LIKE '%📝%' OR r.status LIKE '%Planned%')
            """
            )
            stats["items_ready_for_implementation"] = cursor.fetchone()[0]

            conn.close()
            return stats

        except sqlite3.Error as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Singleton instance for shared access
_unified_db: Optional[UnifiedDatabase] = None


def get_unified_database() -> UnifiedDatabase:
    """Get singleton instance of unified database.

    Returns:
        UnifiedDatabase instance
    """
    global _unified_db
    if _unified_db is None:
        _unified_db = UnifiedDatabase()
    return _unified_db
