#!/usr/bin/env python3
"""Migration script to add implementation tracking to unified database roadmap_items table.

This migration adds fields for tracking code_developer work sessions to detect
stale implementations (>24 hours with no progress) in the unified database.

Usage:
    python coffee_maker/autonomous/migrate_unified_impl_tracking.py
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate_database():
    """Add implementation tracking field to roadmap_items table in unified database."""
    db_path = Path("data/unified_roadmap_specs.db")

    if not db_path.exists():
        logger.warning("Database does not exist yet - will be created with new schema")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(roadmap_items)")
        columns = [col[1] for col in cursor.fetchall()]

        if "implementation_started_at" in columns:
            logger.info("Migration not needed - field already exists")

            # Remove implementation_started_by if it exists (legacy field)
            if "implementation_started_by" in columns:
                logger.info("Removing legacy implementation_started_by field...")
                # SQLite requires table recreation to drop column
                cursor.execute("PRAGMA foreign_keys=off")
                cursor.execute("BEGIN TRANSACTION")

                # Get all columns except implementation_started_by
                all_cols = [col for col in columns if col != "implementation_started_by"]
                cols_str = ", ".join(all_cols)

                cursor.execute(f"CREATE TABLE roadmap_items_temp AS SELECT {cols_str} FROM roadmap_items")
                cursor.execute("DROP TABLE roadmap_items")
                cursor.execute("ALTER TABLE roadmap_items_temp RENAME TO roadmap_items")
                cursor.execute("COMMIT")
                cursor.execute("PRAGMA foreign_keys=on")
                logger.info("✅ Removed legacy implementation_started_by field")

            conn.close()
            return True

        logger.info("Adding implementation_started_at field to roadmap_items table in unified database...")
        cursor.execute("ALTER TABLE roadmap_items ADD COLUMN implementation_started_at TEXT")
        conn.commit()
        logger.info("✅ Successfully added implementation tracking field to unified database")

        conn.close()
        return True

    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    if migrate_database():
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
        exit(1)
