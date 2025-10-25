#!/usr/bin/env python3
"""Migration: Add spec work locking to prevent concurrent architect work.

This migration adds the ability to track when an architect is actively working
on specs for a roadmap item, preventing multiple architects from working on
the same item simultaneously.

Prevents:
- Two architects writing conflicting specs
- Race conditions in plan_and_summary updates
- Duplicate work
- Data corruption

Author: architect
Date: 2025-10-24
Related: User request for concurrent architect prevention
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def add_spec_work_locking(db_path: Path) -> bool:
    """Add spec work locking to roadmap_items table.

    Args:
        db_path: Path to database file

    Returns:
        True if successful
    """
    logger.info("=" * 70)
    logger.info("Migration: Add Spec Work Locking")
    logger.info("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: Add spec_work_started_at column
        logger.info("\n1. Adding spec_work_started_at column to roadmap_items...")

        cursor.execute("PRAGMA table_info(roadmap_items)")
        columns = [row[1] for row in cursor.fetchall()]

        if "spec_work_started_at" not in columns:
            cursor.execute("ALTER TABLE roadmap_items ADD COLUMN spec_work_started_at TEXT")
            logger.info("✅ Added spec_work_started_at column")
        else:
            logger.info("✅ spec_work_started_at column already exists")

        conn.commit()

        # Step 2: Create index for faster queries
        logger.info("\n2. Creating index...")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_roadmap_spec_work ON roadmap_items(spec_work_started_at)")
        logger.info("✅ Created index on spec_work_started_at")

        conn.commit()

        # Step 3: Verify
        logger.info("\n3. Verifying migration...")

        cursor.execute("PRAGMA table_info(roadmap_items)")
        columns = {row[1] for row in cursor.fetchall()}

        if "spec_work_started_at" in columns:
            logger.info("✅ spec_work_started_at column verified")

        logger.info("\n" + "=" * 70)
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("New capabilities:")
        logger.info("  - Prevent concurrent architects working on same roadmap item")
        logger.info("  - Track when spec work started")
        logger.info("  - Detect stale spec work sessions (>24 hours)")
        logger.info("")
        logger.info("Schema:")
        logger.info("  roadmap_items.spec_work_started_at - ISO timestamp when architect claimed item")
        logger.info("")
        logger.info("Methods:")
        logger.info("  roadmap_db.claim_spec_work(item_id) - Claim item for spec writing")
        logger.info("  roadmap_db.release_spec_work(item_id) - Release claim")
        logger.info("  roadmap_db.reset_stale_spec_work() - Reset stale claims")

        return True

    except sqlite3.Error as e:
        logger.error(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    db_path = Path("data/roadmap.db")

    if not db_path.exists():
        logger.error(f"❌ Database not found: {db_path}")
        exit(1)

    success = add_spec_work_locking(db_path)

    if success:
        logger.info("\n🎉 Migration completed successfully!")
        logger.info("\nUsage Example:")
        logger.info(
            """
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

roadmap_db = RoadmapDatabase(agent_name="architect")

# Before working on specs
if roadmap_db.claim_spec_work("PRIORITY-26"):
    print("✅ Claimed PRIORITY-26 for spec work")

    # Work on specs...
    plan = roadmap_db.get_plan_and_summary("PRIORITY-26")
    # ... create specs ...

    # Release when done
    roadmap_db.release_spec_work("PRIORITY-26")
else:
    print("❌ Another architect is already working on PRIORITY-26")
"""
        )
        exit(0)
    else:
        logger.error("\n❌ Migration failed")
        exit(1)
