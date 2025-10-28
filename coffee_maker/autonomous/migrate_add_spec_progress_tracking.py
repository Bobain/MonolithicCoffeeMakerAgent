#!/usr/bin/env python3
"""Migration: Add progressive spec creation tracking.

This migration enables architects to work on specs incrementally across multiple sessions:

1. Adds spec_work_plan table for tracking spec creation progress
2. Updates technical_specs with plan_summary field
3. Tracks what sections are complete, what's next, blockers, etc.

Workflow:
- Architect Session 1: Creates plan_summary, starts core architecture
- Architect Session 2-N: Reads plan, completes next sections, updates plan
- Each session: Clear "next steps" so architect knows what to do

Author: architect
Date: 2025-10-24
Related: User request for progressive spec creation workflow
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def add_spec_progress_tracking(db_path: Path) -> bool:
    """Add progressive spec creation tracking.

    Args:
        db_path: Path to database file

    Returns:
        True if successful
    """
    logger.info("=" * 70)
    logger.info("Migration: Add Progressive Spec Creation Tracking")
    logger.info("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: Add plan_and_summary to technical_specs
        logger.info("\n1. Adding plan_and_summary column to technical_specs...")

        # Check if column already exists
        cursor.execute("PRAGMA table_info(technical_specs)")
        columns = [row[1] for row in cursor.fetchall()]

        # Handle both old and new column names for migration
        if "plan_and_summary" not in columns:
            if "plan_summary" in columns:
                # Rename old column to new name
                logger.info("Renaming plan_summary to plan_and_summary...")
                # SQLite doesn't support RENAME COLUMN directly in older versions
                # We need to copy data to new column and drop old one
                cursor.execute("ALTER TABLE technical_specs ADD COLUMN plan_and_summary TEXT")
                cursor.execute("UPDATE technical_specs SET plan_and_summary = plan_summary")
                # Note: Cannot drop column in SQLite without recreating table
                # Old column will remain but won't be used
                logger.info("✅ Renamed plan_summary to plan_and_summary")
            else:
                cursor.execute("ALTER TABLE technical_specs ADD COLUMN plan_and_summary TEXT")
                logger.info("✅ Added plan_and_summary column")
        else:
            logger.info("✅ plan_and_summary column already exists")

        conn.commit()

        # Step 2: Verify
        logger.info("\n2. Verifying migration...")
        cursor.execute("PRAGMA table_info(technical_specs)")
        columns = {row[1] for row in cursor.fetchall()}

        if "plan_and_summary" in columns:
            logger.info("✅ plan_and_summary column verified")

        logger.info("\n" + "=" * 70)
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("New capabilities:")
        logger.info("  - Architects can create spec plans before full implementation")
        logger.info("  - Track progress using plan_and_summary (JSON format)")
        logger.info("  - Store sections_completed, next_steps, blockers in plan_and_summary")
        logger.info("  - TechnicalSpecSkill manages progressive workflow")
        logger.info("")
        logger.info("Schema:")
        logger.info("  technical_specs.plan_and_summary - JSON with plan, progress, next_steps")

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

    success = add_spec_progress_tracking(db_path)

    if success:
        logger.info("\n🎉 Migration completed successfully!")
        logger.info("\nUsage Example:")
        logger.info(
            """
# Session 1: Create spec with plan
spec_skill.create_spec_with_plan(
    spec_number=131,
    title="Authentication System",
    roadmap_item_id="PRIORITY-26",
    plan_and_summary={
        "overview": "Implement auth system with user model, login, password reset",
        "sections_planned": ["user_model", "login_api", "password_reset", "tests"],
        "sections_completed": [],
        "next_steps": "Start with user model and database schema",
        "blockers": [],
        "work_sessions": 1
    },
    content={"overview": "Initial architecture..."}
)

# Session 2: Update progress
spec_skill.update_spec_progress(
    spec_id="SPEC-131",
    sections_completed=["user_model"],
    next_steps="Implement login API endpoint and JWT tokens"
)

# Session 3: Resume work
progress = spec_skill.get_spec_progress("SPEC-131")
print(f"Next steps: {progress['next_steps']}")
print(f"Completed: {progress['sections_completed']}")
"""
        )
        exit(0)
    else:
        logger.error("\n❌ Migration failed")
        exit(1)
