#!/usr/bin/env python3
"""Migration script to add started_at column to technical_specs table.

This migration adds the started_at field for tracking when specs enter
'in_progress' status, enabling stale spec recovery.

Usage:
    python coffee_maker/autonomous/migrate_add_started_at.py
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate_database():
    """Add started_at column to technical_specs table if it doesn't exist."""
    db_path = Path("data/unified_roadmap_specs.db")

    if not db_path.exists():
        logger.warning("Database does not exist yet - will be created with new schema")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(technical_specs)")
        columns = [col[1] for col in cursor.fetchall()]

        if "started_at" not in columns:
            logger.info("Adding started_at column to technical_specs table...")

            # Add the column
            cursor.execute(
                """
                ALTER TABLE technical_specs
                ADD COLUMN started_at TEXT
            """
            )

            conn.commit()
            logger.info("✅ Successfully added started_at column")
        else:
            logger.info("Column started_at already exists - no migration needed")

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
