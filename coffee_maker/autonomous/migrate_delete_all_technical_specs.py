#!/usr/bin/env python3
"""Migration: Delete all existing technical specifications.

REASON: Legacy specs cannot be migrated to new workflow without significant effort.
Starting fresh with new hierarchical spec system and progressive architect workflow.

OLD SPECS:
- Created before roadmap-level planning
- No plan_and_summary tracking
- No hierarchical structure
- Incompatible with new architect workflow

NEW APPROACH:
- architect creates specs with progressive workflow
- plan_and_summary tracked at roadmap_items level
- Hierarchical spec structure
- Reusability tracking

This migration:
1. Deletes all rows from technical_specs table
2. Resets spec counter to 1
3. Keeps table structure intact
4. Ready for new specs to be created

Author: architect
Date: 2025-10-24
Related: User request to start fresh with technical specs
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def delete_all_technical_specs(db_path: Path) -> bool:
    """Delete all existing technical specifications.

    Args:
        db_path: Path to database file

    Returns:
        True if successful
    """
    logger.info("=" * 70)
    logger.info("Migration: Delete All Technical Specifications")
    logger.info("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: Count existing specs
        logger.info("\n1. Checking existing specs...")
        cursor.execute("SELECT COUNT(*) FROM technical_specs")
        count = cursor.fetchone()[0]
        logger.info(f"   Found {count} existing technical specs")

        if count == 0:
            logger.info("   No specs to delete - table already empty")
            return True

        # Step 2: Get list of spec IDs (for logging)
        cursor.execute("SELECT id, title FROM technical_specs ORDER BY spec_number")
        specs = cursor.fetchall()

        logger.info(f"\n2. Specs to be deleted ({len(specs)}):")
        for spec_id, title in specs[:10]:  # Show first 10
            logger.info(f"   - {spec_id}: {title}")
        if len(specs) > 10:
            logger.info(f"   ... and {len(specs) - 10} more")

        # Step 3: Delete all specs
        logger.info("\n3. Deleting all technical specs...")
        cursor.execute("DELETE FROM technical_specs")
        deleted_count = cursor.rowcount
        logger.info(f"   Deleted {deleted_count} specs")

        conn.commit()

        # Step 4: Verify deletion
        logger.info("\n4. Verifying deletion...")
        cursor.execute("SELECT COUNT(*) FROM technical_specs")
        remaining = cursor.fetchone()[0]

        if remaining == 0:
            logger.info("   ✅ All specs deleted successfully")
        else:
            logger.warning(f"   ⚠️  {remaining} specs still remain!")

        # Step 5: Check table structure is intact
        logger.info("\n5. Verifying table structure...")
        cursor.execute("PRAGMA table_info(technical_specs)")
        columns = cursor.fetchall()
        logger.info(f"   Table has {len(columns)} columns:")
        for col in columns:
            logger.info(f"     - {col[1]} ({col[2]})")

        logger.info("\n" + "=" * 70)
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Database ready for new technical specs:")
        logger.info("  - Table structure intact")
        logger.info("  - All old specs removed")
        logger.info("  - Ready for architect to create new specs")
        logger.info("  - New specs will use progressive workflow")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. architect creates specs with plan_and_summary")
        logger.info("  2. Use hierarchical spec structure")
        logger.info("  3. Track reusable components")
        logger.info("  4. Follow progressive workflow in ARCHITECT_PROGRESSIVE_WORKFLOW.md")

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

    # Confirm before proceeding
    logger.warning("")
    logger.warning("⚠️  WARNING: This will DELETE ALL existing technical specifications!")
    logger.warning("⚠️  This action cannot be undone!")
    logger.warning("")
    logger.warning("Reason: Legacy specs incompatible with new progressive workflow")
    logger.warning("")

    response = input("Type 'DELETE ALL SPECS' to confirm: ")

    if response != "DELETE ALL SPECS":
        logger.info("Migration cancelled - no changes made")
        exit(0)

    success = delete_all_technical_specs(db_path)

    if success:
        logger.info("\n🎉 Migration completed successfully!")
        logger.info("\nDatabase is ready for new technical specs using:")
        logger.info("  - Progressive architect workflow")
        logger.info("  - Hierarchical spec structure")
        logger.info("  - Reusability tracking")
        logger.info("  - plan_and_summary at roadmap_items level")
        exit(0)
    else:
        logger.error("\n❌ Migration failed")
        exit(1)
