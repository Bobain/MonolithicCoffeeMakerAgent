#!/usr/bin/env python3
"""Migration script to move phase field from roadmap_items to technical_specs.

Architectural reasoning:
One roadmap item may require multiple phases, each with its own technical spec.
Therefore, phase should be associated with the spec, not the roadmap item.

This migration:
1. Adds phase column to technical_specs table
2. Migrates existing phase data from roadmap_items to linked specs
3. Removes phase column from roadmap_items table

Usage:
    python coffee_maker/autonomous/migrate_move_phase_to_specs.py
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate_unified_database():
    """Move phase field from roadmap_items to technical_specs in unified database."""
    db_path = Path("data/unified_roadmap_specs.db")

    if not db_path.exists():
        logger.warning("Unified database does not exist yet - will be created with new schema")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if technical_specs already has phase column
        cursor.execute("PRAGMA table_info(technical_specs)")
        specs_columns = [col[1] for col in cursor.fetchall()]

        if "phase" in specs_columns:
            logger.info("technical_specs already has phase column")
        else:
            logger.info("Adding phase column to technical_specs table...")
            cursor.execute("ALTER TABLE technical_specs ADD COLUMN phase TEXT")
            logger.info("✅ Added phase column to technical_specs")

        # Migrate phase data from roadmap_items to technical_specs
        logger.info("Migrating phase data from roadmap_items to linked specs...")
        cursor.execute(
            """
            SELECT r.id, r.phase, r.spec_id
            FROM roadmap_items r
            WHERE r.phase IS NOT NULL AND r.spec_id IS NOT NULL
        """
        )
        items_to_migrate = cursor.fetchall()

        migrated = 0
        for item_id, phase, spec_id in items_to_migrate:
            cursor.execute(
                "UPDATE technical_specs SET phase = ? WHERE id = ?",
                (phase, spec_id),
            )
            if cursor.rowcount > 0:
                migrated += 1
                logger.info(f"  Migrated phase '{phase}' from {item_id} to {spec_id}")

        logger.info(f"✅ Migrated phase data for {migrated} specs")

        # Remove phase column from roadmap_items (SQLite requires table recreation)
        logger.info("Removing phase column from roadmap_items table...")

        # Create new table without phase column
        cursor.execute(
            """
            CREATE TABLE roadmap_items_new (
                id TEXT PRIMARY KEY,
                item_type TEXT NOT NULL,
                number TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                spec_id TEXT,
                content TEXT,
                estimated_hours TEXT,
                dependencies TEXT,
                priority_order INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                updated_by TEXT NOT NULL,
                implementation_started_at TEXT,
                implementation_started_by TEXT,
                FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
            )
        """
        )

        # Copy data (excluding phase column)
        cursor.execute(
            """
            INSERT INTO roadmap_items_new (
                id, item_type, number, title, status, spec_id, content,
                estimated_hours, dependencies, priority_order, updated_at, updated_by,
                implementation_started_at, implementation_started_by
            )
            SELECT
                id, item_type, number, title, status, spec_id, content,
                estimated_hours, dependencies, priority_order, updated_at, updated_by,
                implementation_started_at, implementation_started_by
            FROM roadmap_items
        """
        )

        # Drop old table and rename new one
        cursor.execute("DROP TABLE roadmap_items")
        cursor.execute("ALTER TABLE roadmap_items_new RENAME TO roadmap_items")

        # Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON roadmap_items(item_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_status ON roadmap_items(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON roadmap_items(priority_order)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_number ON roadmap_items(number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_spec ON roadmap_items(spec_id)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_items_id ON roadmap_items(id)")

        logger.info("✅ Removed phase column from roadmap_items")

        conn.commit()
        conn.close()

        logger.info("✅ Migration completed successfully")
        return True

    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        return False


def migrate_roadmap_database():
    """Move phase field from roadmap_items in standalone roadmap database."""
    db_path = Path("data/roadmap.db")

    if not db_path.exists():
        logger.info("Standalone roadmap.db does not exist - skipping")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("Removing phase column from roadmap_items in standalone database...")

        # Check if phase column exists
        cursor.execute("PRAGMA table_info(roadmap_items)")
        columns = [col[1] for col in cursor.fetchall()]

        if "phase" not in columns:
            logger.info("Phase column already removed from standalone database")
            conn.close()
            return True

        # Create new table without phase column
        cursor.execute(
            """
            CREATE TABLE roadmap_items_new (
                id TEXT PRIMARY KEY,
                item_type TEXT NOT NULL,
                number TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                spec_id TEXT,
                content TEXT,
                estimated_hours TEXT,
                dependencies TEXT,
                priority_order INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                updated_by TEXT NOT NULL,
                implementation_started_at TEXT,
                implementation_started_by TEXT,
                FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
            )
        """
        )

        # Copy data (excluding phase column)
        cursor.execute(
            """
            INSERT INTO roadmap_items_new (
                id, item_type, number, title, status, spec_id, content,
                estimated_hours, dependencies, priority_order, updated_at, updated_by,
                implementation_started_at, implementation_started_by
            )
            SELECT
                id, item_type, number, title, status, spec_id, content,
                estimated_hours, dependencies, priority_order, updated_at, updated_by,
                implementation_started_at, implementation_started_by
            FROM roadmap_items
        """
        )

        # Drop old table and rename new one
        cursor.execute("DROP TABLE roadmap_items")
        cursor.execute("ALTER TABLE roadmap_items_new RENAME TO roadmap_items")

        # Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON roadmap_items(item_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_status ON roadmap_items(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON roadmap_items(priority_order)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_number ON roadmap_items(number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_spec ON roadmap_items(spec_id)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_items_id ON roadmap_items(id)")

        conn.commit()
        conn.close()

        logger.info("✅ Removed phase from standalone roadmap.db")
        return True

    except sqlite3.Error as e:
        logger.error(f"Migration failed for standalone database: {e}")
        return False


if __name__ == "__main__":
    success = True

    # Migrate unified database (primary)
    if not migrate_unified_database():
        success = False

    # Migrate standalone roadmap database (if exists)
    if not migrate_roadmap_database():
        success = False

    if success:
        logger.info("🎉 All migrations completed successfully")
    else:
        logger.error("❌ Some migrations failed")
        exit(1)
