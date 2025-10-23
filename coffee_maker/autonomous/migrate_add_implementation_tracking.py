#!/usr/bin/env python3
"""Migration script to add implementation tracking to roadmap_items table.

This migration adds fields for tracking code_developer work sessions to detect
stale implementations (>24 hours with no progress).

Usage:
    python coffee_maker/autonomous/migrate_add_implementation_tracking.py
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate_database():
    """Add implementation tracking fields to roadmap_items table."""
    db_path = Path("data/roadmap.db")

    if not db_path.exists():
        logger.warning("Database does not exist yet - will be created with new schema")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(roadmap_items)")
        columns = [col[1] for col in cursor.fetchall()]

        needs_migration = False
        fields_to_add = []

        if "implementation_started_at" not in columns:
            fields_to_add.append(("implementation_started_at", "TEXT", "When code_developer started work"))
            needs_migration = True

        if "implementation_started_by" not in columns:
            fields_to_add.append(("implementation_started_by", "TEXT", "Which code_developer claimed this"))
            needs_migration = True

        if not needs_migration:
            logger.info("Migration not needed - fields already exist")
            conn.close()
            return True

        logger.info(f"Adding {len(fields_to_add)} fields to roadmap_items table...")

        for field_name, field_type, description in fields_to_add:
            logger.info(f"  Adding field: {field_name} ({description})")
            cursor.execute(f"ALTER TABLE roadmap_items ADD COLUMN {field_name} {field_type}")

        conn.commit()
        logger.info("✅ Successfully added implementation tracking fields")

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
