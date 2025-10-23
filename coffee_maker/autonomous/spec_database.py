"""Technical Specification Database Management.

This module provides database-backed technical specification management for the architect agent.
Replaces file-only spec storage with structured database tracking while maintaining backward
compatibility with existing markdown files.

Per CFR-015: Database stored in data/specs.db

Features:
    - Track spec metadata and status in database
    - Maintain links to markdown files
    - Provide structured queries for specs
    - Track implementation progress
    - Calculate effort estimates and actuals

Access Control:
    - Write access: architect agent only
    - Read access: All agents
    - Updates logged for audit trail

Example:
    >>> from coffee_maker.autonomous.spec_database import SpecDatabase
    >>> db = SpecDatabase()
    >>>
    >>> # Create new spec entry
    >>> spec_id = db.create_spec(
    ...     spec_number="112",
    ...     title="Codebase Quality Audit",
    ...     roadmap_item_id="PRIORITY-26",
    ...     estimated_hours=4.0
    ... )
    >>>
    >>> # Update spec status
    >>> db.update_status(spec_id, "in_progress", updated_by="architect")
    >>>
    >>> # Query specs
    >>> specs = db.get_specs_by_status("draft")
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SpecDatabase:
    """Database for technical specification tracking.

    Provides structured storage for spec metadata while maintaining
    compatibility with existing markdown file system.

    Attributes:
        db_path: Path to SQLite database (default: data/specs.db)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize spec database.

        Args:
            db_path: Path to SQLite database (default: data/specs.db per CFR-015)
        """
        if db_path is None:
            db_path = Path("data/specs.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_database()
        logger.info(f"SpecDatabase initialized at {self.db_path}")

    def _init_database(self) -> None:
        """Initialize database schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Main technical_specs table (simplified per user request)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS technical_specs (
                    id TEXT PRIMARY KEY,           -- e.g., "SPEC-112"
                    spec_number INTEGER NOT NULL,   -- e.g., 112
                    title TEXT NOT NULL,           -- Spec title
                    roadmap_item_id TEXT,          -- e.g., "US-062", "PRIORITY-26"
                    status TEXT NOT NULL DEFAULT 'draft',  -- 'draft', 'in_progress', 'complete', 'approved'
                    spec_type TEXT DEFAULT 'monolithic',   -- 'monolithic' or 'hierarchical'
                    file_path TEXT,                -- Path to markdown file(s)
                    content TEXT,                  -- Optional: full markdown content
                    dependencies TEXT,             -- JSON array of other spec IDs
                    estimated_hours REAL,          -- Total estimated effort
                    actual_hours REAL,             -- Actual time spent (when complete)
                    updated_at TEXT NOT NULL,      -- ISO timestamp of last update
                    updated_by TEXT NOT NULL       -- Agent that made the update
                )
            """
            )

            # Audit trail table for all changes
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS spec_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spec_id TEXT NOT NULL,
                    action TEXT NOT NULL,          -- 'create', 'update_status', 'update_content'
                    field_changed TEXT,            -- Which field was modified
                    old_value TEXT,                -- Previous value
                    new_value TEXT,                -- New value
                    changed_by TEXT NOT NULL,      -- Agent making change
                    changed_at TEXT NOT NULL,      -- ISO timestamp
                    notes TEXT                     -- Optional notes about change
                )
            """
            )

            # Indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_specs_status ON technical_specs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_specs_roadmap ON technical_specs(roadmap_item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_specs_number ON technical_specs(spec_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_spec ON spec_audit(spec_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_changed_at ON spec_audit(changed_at)")

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Error initializing spec database: {e}")
            raise

    def create_spec(
        self,
        spec_number: int,
        title: str,
        roadmap_item_id: Optional[str] = None,
        spec_type: str = "monolithic",
        file_path: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        estimated_hours: Optional[float] = None,
        created_by: str = "architect",
    ) -> str:
        """Create a new technical specification entry.

        Args:
            spec_number: Spec number (e.g., 112)
            title: Spec title
            roadmap_item_id: Related roadmap item (e.g., "US-062")
            spec_type: "monolithic" or "hierarchical"
            file_path: Path to markdown file(s)
            dependencies: List of spec IDs this depends on
            estimated_hours: Total effort estimate
            created_by: Agent creating the spec

        Returns:
            spec_id: Generated spec ID (e.g., "SPEC-112")

        Raises:
            PermissionError: If created_by is not "architect"
            sqlite3.IntegrityError: If spec already exists
        """
        if created_by != "architect":
            raise PermissionError(f"Only architect can create specs, not {created_by}")

        spec_id = f"SPEC-{spec_number}"
        now = datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert spec
            cursor.execute(
                """
                INSERT INTO technical_specs (
                    id, spec_number, title, roadmap_item_id, status, spec_type,
                    file_path, dependencies, estimated_hours, updated_at, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    spec_id,
                    spec_number,
                    title,
                    roadmap_item_id,
                    "draft",
                    spec_type,
                    file_path,
                    json.dumps(dependencies) if dependencies else None,
                    estimated_hours,
                    now,
                    created_by,
                ),
            )

            # Log to audit trail
            cursor.execute(
                """
                INSERT INTO spec_audit (
                    spec_id, action, changed_by, changed_at, notes
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    spec_id,
                    "create",
                    created_by,
                    now,
                    f"Created spec for {roadmap_item_id}" if roadmap_item_id else "Created spec",
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Created {spec_id}: {title}")
            return spec_id

        except sqlite3.IntegrityError:
            logger.error(f"Spec {spec_id} already exists")
            raise
        except sqlite3.Error as e:
            logger.error(f"Error creating spec: {e}")
            raise

    def update_status(
        self, spec_id: str, new_status: str, updated_by: str, actual_hours: Optional[float] = None
    ) -> bool:
        """Update the status of a technical specification.

        Args:
            spec_id: Spec ID (e.g., "SPEC-112")
            new_status: New status ('draft', 'in_progress', 'complete', 'approved')
            updated_by: Agent making the update
            actual_hours: Actual effort (when marking complete)

        Returns:
            True if successful

        Raises:
            PermissionError: If updated_by is not "architect"
        """
        if updated_by != "architect":
            raise PermissionError(f"Only architect can update specs, not {updated_by}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current status
            cursor.execute("SELECT status FROM technical_specs WHERE id = ?", (spec_id,))
            result = cursor.fetchone()

            if not result:
                logger.error(f"Spec {spec_id} not found")
                return False

            old_status = result[0]
            now = datetime.now().isoformat()

            # Update spec
            if actual_hours is not None:
                cursor.execute(
                    """
                    UPDATE technical_specs
                    SET status = ?, actual_hours = ?, updated_at = ?, updated_by = ?
                    WHERE id = ?
                """,
                    (new_status, actual_hours, now, updated_by, spec_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE technical_specs
                    SET status = ?, updated_at = ?, updated_by = ?
                    WHERE id = ?
                """,
                    (new_status, now, updated_by, spec_id),
                )

            # Log to audit trail
            cursor.execute(
                """
                INSERT INTO spec_audit (
                    spec_id, action, field_changed, old_value, new_value,
                    changed_by, changed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (spec_id, "update_status", "status", old_status, new_status, updated_by, now),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Updated {spec_id} status: {old_status} → {new_status}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error updating status: {e}")
            return False

    def get_spec(self, spec_id: str) -> Optional[Dict]:
        """Get a specific technical specification.

        Args:
            spec_id: Spec ID (e.g., "SPEC-112")

        Returns:
            Spec dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM technical_specs WHERE id = ?", (spec_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                spec = dict(row)
                # Parse JSON fields
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                return spec

            return None

        except sqlite3.Error as e:
            logger.error(f"Error getting spec: {e}")
            return None

    def get_specs_by_status(self, status: str) -> List[Dict]:
        """Get all specs with a specific status.

        Args:
            status: Status to filter by ('draft', 'in_progress', 'complete', 'approved')

        Returns:
            List of spec dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM technical_specs
                WHERE status = ?
                ORDER BY spec_number ASC
            """,
                (status,),
            )

            rows = cursor.fetchall()
            conn.close()

            specs = []
            for row in rows:
                spec = dict(row)
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                specs.append(spec)

            return specs

        except sqlite3.Error as e:
            logger.error(f"Error getting specs by status: {e}")
            return []

    def get_specs_for_roadmap_item(self, roadmap_item_id: str) -> List[Dict]:
        """Get all specs for a specific roadmap item.

        Args:
            roadmap_item_id: Roadmap item ID (e.g., "US-062", "PRIORITY-26")

        Returns:
            List of spec dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM technical_specs
                WHERE roadmap_item_id = ?
                ORDER BY spec_number ASC
            """,
                (roadmap_item_id,),
            )

            rows = cursor.fetchall()
            conn.close()

            specs = []
            for row in rows:
                spec = dict(row)
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                specs.append(spec)

            return specs

        except sqlite3.Error as e:
            logger.error(f"Error getting specs for roadmap item: {e}")
            return []

    def find_spec_by_number(self, spec_number: int) -> Optional[Dict]:
        """Find a spec by its number.

        Args:
            spec_number: Spec number (e.g., 112)

        Returns:
            Spec dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM technical_specs
                WHERE spec_number = ?
            """,
                (spec_number,),
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                spec = dict(row)
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                return spec

            return None

        except sqlite3.Error as e:
            logger.error(f"Error finding spec by number: {e}")
            return None

    def find_spec_by_id(self, spec_id: str) -> Optional[Dict]:
        """Find a spec by its ID.

        Args:
            spec_id: Spec ID (e.g., "SPEC-112")

        Returns:
            Spec dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM technical_specs
                WHERE id = ?
            """,
                (spec_id,),
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                spec = dict(row)
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                return spec

            return None

        except sqlite3.Error as e:
            logger.error(f"Error finding spec by ID: {e}")
            return None

    def get_all_specs(self) -> List[Dict]:
        """Get all technical specifications.

        Returns:
            List of all spec dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM technical_specs
                ORDER BY spec_number ASC
            """
            )

            rows = cursor.fetchall()
            conn.close()

            specs = []
            for row in rows:
                spec = dict(row)
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                specs.append(spec)

            return specs

        except sqlite3.Error as e:
            logger.error(f"Error getting all specs: {e}")
            return []

    def get_spec_stats(self) -> Dict:
        """Get statistics about technical specifications.

        Returns:
            Dictionary with stats (counts by status, effort metrics)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count by status
            cursor.execute(
                """
                SELECT status, COUNT(*) as count
                FROM technical_specs
                GROUP BY status
            """
            )
            status_counts = dict(cursor.fetchall())

            # Effort statistics
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_specs,
                    SUM(estimated_hours) as total_estimated,
                    SUM(actual_hours) as total_actual,
                    AVG(estimated_hours) as avg_estimated,
                    AVG(actual_hours) as avg_actual
                FROM technical_specs
            """
            )

            effort_stats = cursor.fetchone()
            conn.close()

            return {
                "status_counts": status_counts,
                "total_specs": effort_stats[0] or 0,
                "total_estimated_hours": effort_stats[1] or 0.0,
                "total_actual_hours": effort_stats[2] or 0.0,
                "avg_estimated_hours": effort_stats[3] or 0.0,
                "avg_actual_hours": effort_stats[4] or 0.0,
            }

        except sqlite3.Error as e:
            logger.error(f"Error getting spec stats: {e}")
            return {}

    def get_audit_trail(self, spec_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get audit trail for specs.

        Args:
            spec_id: Optional spec ID to filter by
            limit: Maximum number of records to return

        Returns:
            List of audit records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if spec_id:
                cursor.execute(
                    """
                    SELECT * FROM spec_audit
                    WHERE spec_id = ?
                    ORDER BY changed_at DESC
                    LIMIT ?
                """,
                    (spec_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM spec_audit
                    ORDER BY changed_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting audit trail: {e}")
            return []

    def import_existing_specs(self) -> Tuple[int, int]:
        """Import existing spec files from filesystem into database.

        Scans docs/architecture/specs/ for existing spec files and imports
        their metadata into the database.

        Returns:
            Tuple of (imported_count, skipped_count)
        """
        specs_dir = Path("docs/architecture/specs")
        imported = 0
        skipped = 0

        if not specs_dir.exists():
            logger.warning(f"Specs directory not found: {specs_dir}")
            return (0, 0)

        # Find all spec files and directories
        for path in specs_dir.iterdir():
            try:
                # Extract spec number from name
                if path.name.startswith("SPEC-"):
                    parts = path.name.split("-", 2)
                    if len(parts) >= 2:
                        spec_number = int(parts[1].split(".")[0])  # Remove .md if present

                        # Check if already exists
                        if self.find_spec_by_number(spec_number):
                            logger.debug(f"Skipping existing spec: {path.name}")
                            skipped += 1
                            continue

                        # Determine spec type
                        spec_type = "hierarchical" if path.is_dir() else "monolithic"

                        # Extract title from filename
                        title = (
                            parts[2].replace(".md", "").replace("-", " ").title()
                            if len(parts) > 2
                            else f"Spec {spec_number}"
                        )

                        # Create database entry
                        self.create_spec(
                            spec_number=spec_number,
                            title=title,
                            spec_type=spec_type,
                            file_path=str(path),  # Just use the path as-is
                            created_by="architect",  # Import as architect
                        )
                        imported += 1

            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse spec from {path.name}: {e}")
                skipped += 1
            except Exception as e:
                logger.error(f"Error importing {path.name}: {e}")
                skipped += 1

        logger.info(f"✅ Import complete: {imported} imported, {skipped} skipped")
        return (imported, skipped)
