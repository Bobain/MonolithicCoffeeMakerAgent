#!/usr/bin/env python3
"""Add hierarchical spec support columns to technical_specs table.

This migration adds columns needed for hierarchical specification architecture:
- total_phases: Number of phases in hierarchical spec
- phase_files: JSON array of phase file names
- current_phase_status: Status of current phase (in_progress, completed)

Usage:
    python coffee_maker/autonomous/migrate_add_hierarchical_spec_columns.py

Author: architect
Date: 2025-10-24
Related: PRIORITY 25 Phase 4, CFR-016
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate():
    """Add hierarchical spec columns to technical_specs table."""
    db_path = Path("data/roadmap.db")

    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("Starting migration: Add hierarchical spec columns")

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(technical_specs)")
        columns = {row[1] for row in cursor.fetchall()}

        # Add total_phases column
        if "total_phases" not in columns:
            logger.info("Adding column: total_phases INTEGER")
            cursor.execute("ALTER TABLE technical_specs ADD COLUMN total_phases INTEGER")
        else:
            logger.info("Column total_phases already exists, skipping")

        # Add phase_files column (JSON array)
        if "phase_files" not in columns:
            logger.info("Adding column: phase_files TEXT (JSON)")
            cursor.execute("ALTER TABLE technical_specs ADD COLUMN phase_files TEXT")
        else:
            logger.info("Column phase_files already exists, skipping")

        # Add current_phase_status column
        if "current_phase_status" not in columns:
            logger.info("Adding column: current_phase_status TEXT")
            cursor.execute("ALTER TABLE technical_specs ADD COLUMN current_phase_status TEXT")
        else:
            logger.info("Column current_phase_status already exists, skipping")

        conn.commit()

        # Verify changes
        cursor.execute("PRAGMA table_info(technical_specs)")
        columns_after = {row[1]: row[2] for row in cursor.fetchall()}

        logger.info("\nTechnical specs table columns:")
        for col_name, col_type in sorted(columns_after.items()):
            marker = "✅ NEW" if col_name in ["total_phases", "phase_files", "current_phase_status"] else ""
            logger.info(f"  - {col_name} ({col_type}) {marker}")

        conn.close()

        logger.info("\n✅ Migration complete!")
        logger.info("Hierarchical spec columns added to technical_specs table")
        return True

    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
