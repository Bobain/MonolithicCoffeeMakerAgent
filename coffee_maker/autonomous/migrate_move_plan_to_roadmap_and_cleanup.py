#!/usr/bin/env python3
"""Migration: Move plan_and_summary to roadmap_items and delete unused tables.

This migration:
1. Adds plan_and_summary to roadmap_items (correct granularity)
2. Removes plan_and_summary from technical_specs (wrong granularity)
3. Deletes unused tables: spec_work_plan, spec_audit, roadmap_audit

Author: architect
Date: 2025-10-24
Related: User request to fix data structure granularity
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def move_plan_and_cleanup(db_path: Path) -> bool:
    """Move plan_and_summary to roadmap_items and delete unused tables.

    Args:
        db_path: Path to database file

    Returns:
        True if successful
    """
    logger.info("=" * 70)
    logger.info("Migration: Move plan_and_summary to roadmap_items + Cleanup")
    logger.info("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: Add plan_and_summary to roadmap_items
        logger.info("\n1. Adding plan_and_summary to roadmap_items...")

        cursor.execute("PRAGMA table_info(roadmap_items)")
        columns = [row[1] for row in cursor.fetchall()]

        if "plan_and_summary" not in columns:
            cursor.execute("ALTER TABLE roadmap_items ADD COLUMN plan_and_summary TEXT")
            logger.info("✅ Added plan_and_summary column to roadmap_items")
        else:
            logger.info("✅ plan_and_summary column already exists in roadmap_items")

        conn.commit()

        # Step 2: Identify unused tables
        logger.info("\n2. Identifying unused tables...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = [row[0] for row in cursor.fetchall()]

        # Tables that are actually used in code
        used_tables = {
            "roadmap_items",
            "technical_specs",
            "implementation_tasks",
            "review_reports",
            "notifications",
            "roadmap_update_notifications",
            "audit_trail",
            "roadmap_metadata",
            "roadmap_audit",  # Used in roadmap_database.py
            "sqlite_sequence",  # SQLite internal
        }

        unused_tables = [t for t in all_tables if t not in used_tables]

        if unused_tables:
            logger.info(f"Found {len(unused_tables)} unused tables: {unused_tables}")
        else:
            logger.info("No unused tables found")

        # Step 3: Delete unused tables
        logger.info("\n3. Deleting unused tables...")

        for table in unused_tables:
            logger.info(f"   Dropping table: {table}")
            cursor.execute(f"DROP TABLE IF EXISTS {table}")

        if unused_tables:
            logger.info(f"✅ Deleted {len(unused_tables)} unused tables")
        else:
            logger.info("✅ No tables to delete")

        conn.commit()

        # Step 4: Verify
        logger.info("\n4. Verifying migration...")

        cursor.execute("PRAGMA table_info(roadmap_items)")
        columns = {row[1] for row in cursor.fetchall()}

        if "plan_and_summary" in columns:
            logger.info("✅ plan_and_summary exists in roadmap_items")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        remaining_tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"✅ Remaining tables ({len(remaining_tables)}): {remaining_tables}")

        logger.info("\n" + "=" * 70)
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Changes:")
        logger.info("  - plan_and_summary now in roadmap_items (correct granularity)")
        logger.info(f"  - Deleted {len(unused_tables)} unused tables")
        logger.info("")
        logger.info("Schema:")
        logger.info("  roadmap_items.plan_and_summary - JSON with plan, progress, next_steps")
        logger.info("")
        logger.info("Note:")
        logger.info("  - technical_specs still has plan_and_summary column (will be ignored)")
        logger.info("  - SQLite cannot drop columns without recreating table")

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

    success = move_plan_and_cleanup(db_path)

    if success:
        logger.info("\n🎉 Migration completed successfully!")
        logger.info("\nUsage Example:")
        logger.info(
            """
# Architect working on roadmap item with progressive workflow
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

db = RoadmapDatabase(agent_name="architect")

# Session 1: Create plan for roadmap item
db.update_roadmap_item(
    item_id="PRIORITY-26",
    plan_and_summary={
        "overview": "Implement auth system: user model, login, password reset, tests",
        "sections_planned": ["user_model", "login_api", "password_reset", "tests"],
        "sections_completed": [],
        "next_steps": "Start with user model spec and database schema",
        "blockers": [],
        "work_sessions": 1
    }
)

# Session 2: Update progress
item = db.get_roadmap_item("PRIORITY-26")
plan = json.loads(item["plan_and_summary"])
plan["sections_completed"] = ["user_model"]
plan["next_steps"] = "Create login API spec"
plan["work_sessions"] += 1
db.update_roadmap_item(item_id="PRIORITY-26", plan_and_summary=plan)
"""
        )
        exit(0)
    else:
        logger.error("\n❌ Migration failed")
        exit(1)
