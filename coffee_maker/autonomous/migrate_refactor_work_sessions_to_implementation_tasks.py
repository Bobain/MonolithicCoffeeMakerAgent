#!/usr/bin/env python3
"""Migration: Refactor work_sessions to implementation_tasks with proper normalization.

This migration:
1. Renames work_sessions → implementation_tasks (clearer naming)
2. Removes redundant roadmap_item_id column (normalization)
3. Creates implementation_tasks_view with roadmap_item_id (denormalized for performance)

Rationale:
- "implementation_tasks" is much clearer than "work_sessions"
- roadmap_item_id is redundant (can be derived via spec_id → technical_specs.roadmap_item_id)
- View provides performance benefit without data redundancy
- Single source of truth maintained

Author: architect
Date: 2025-10-24
Related: User feedback on schema design and naming clarity
"""

import logging
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate_work_sessions_to_implementation_tasks(db_path: Path) -> bool:
    """Refactor work_sessions to implementation_tasks with normalized schema.

    Args:
        db_path: Path to database file

    Returns:
        True if successful
    """
    logger.info("=" * 70)
    logger.info("Migration: work_sessions → implementation_tasks")
    logger.info("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: Check if work_sessions exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_sessions'")
        if not cursor.fetchone():
            logger.info("⚠️  work_sessions table does not exist, skipping migration")
            conn.close()
            return True

        logger.info("\n1. Checking current work_sessions data...")
        cursor.execute("SELECT COUNT(*) FROM work_sessions")
        row_count = cursor.fetchone()[0]
        logger.info(f"   Found {row_count} existing work sessions")

        if row_count > 0:
            # Show existing data
            cursor.execute("SELECT work_id, spec_id, roadmap_item_id FROM work_sessions LIMIT 5")
            logger.info("   Sample data:")
            for row in cursor.fetchall():
                logger.info(f"     {row[0]}: spec={row[1]}, roadmap={row[2]}")

        # Step 2: Create new implementation_tasks table (normalized - no roadmap_item_id)
        logger.info("\n2. Creating implementation_tasks table (normalized schema)...")
        cursor.execute(
            """
            CREATE TABLE implementation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL UNIQUE,
                spec_id TEXT NOT NULL,
                scope TEXT NOT NULL,
                scope_description TEXT,
                assigned_files TEXT,
                branch_name TEXT NOT NULL UNIQUE,
                worktree_path TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                claimed_by TEXT,
                claimed_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                commit_sha TEXT,
                merged_at TEXT,
                created_by TEXT NOT NULL DEFAULT 'architect',
                created_at TEXT NOT NULL,
                FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE CASCADE
            )
        """
        )
        logger.info("✅ Created implementation_tasks table")

        # Step 3: Create indexes
        logger.info("\n3. Creating indexes...")
        cursor.execute("CREATE INDEX idx_implementation_tasks_status ON implementation_tasks(status)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_spec ON implementation_tasks(spec_id)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_branch ON implementation_tasks(branch_name)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_claimed_at ON implementation_tasks(claimed_at)")
        logger.info("✅ Created 4 indexes")

        # Step 4: Migrate data from work_sessions to implementation_tasks
        if row_count > 0:
            logger.info(f"\n4. Migrating {row_count} work sessions to implementation_tasks...")
            cursor.execute(
                """
                INSERT INTO implementation_tasks (
                    task_id, spec_id, scope, scope_description, assigned_files,
                    branch_name, worktree_path, status, claimed_by, claimed_at,
                    started_at, completed_at, commit_sha, merged_at,
                    created_by, created_at
                )
                SELECT
                    work_id, spec_id, scope, scope_description, assigned_files,
                    branch_name, worktree_path, status, claimed_by, claimed_at,
                    started_at, completed_at, commit_sha, merged_at,
                    created_by, created_at
                FROM work_sessions
            """
            )
            migrated = cursor.rowcount
            logger.info(f"✅ Migrated {migrated} rows")
        else:
            logger.info("\n4. No data to migrate (table is empty)")

        # Step 5: Create denormalized VIEW with roadmap_item_id
        logger.info("\n5. Creating implementation_tasks_view (with roadmap_item_id)...")
        cursor.execute(
            """
            CREATE VIEW implementation_tasks_view AS
            SELECT
                t.id,
                t.task_id,
                t.spec_id,
                s.roadmap_item_id,  -- Derived from spec
                t.scope,
                t.scope_description,
                t.assigned_files,
                t.branch_name,
                t.worktree_path,
                t.status,
                t.claimed_by,
                t.claimed_at,
                t.started_at,
                t.completed_at,
                t.commit_sha,
                t.merged_at,
                t.created_by,
                t.created_at
            FROM implementation_tasks t
            JOIN technical_specs s ON t.spec_id = s.id
        """
        )
        logger.info("✅ Created implementation_tasks_view")

        # Step 6: Drop old work_sessions table
        logger.info("\n6. Dropping old work_sessions table...")
        cursor.execute("DROP TABLE work_sessions")
        logger.info("✅ Dropped work_sessions")

        conn.commit()

        # Step 7: Verify migration
        logger.info("\n7. Verifying migration...")
        cursor.execute("SELECT COUNT(*) FROM implementation_tasks")
        new_count = cursor.fetchone()[0]
        logger.info(f"✅ implementation_tasks has {new_count} rows")

        # Check view works
        cursor.execute("SELECT COUNT(*) FROM implementation_tasks_view")
        view_count = cursor.fetchone()[0]
        logger.info(f"✅ implementation_tasks_view has {view_count} rows")

        # Show sample from view
        if view_count > 0:
            cursor.execute(
                """
                SELECT task_id, spec_id, roadmap_item_id
                FROM implementation_tasks_view
                LIMIT 3
            """
            )
            logger.info("\n   Sample from view:")
            for row in cursor.fetchall():
                logger.info(f"     {row[0]}: spec={row[1]}, roadmap={row[2]}")

        logger.info("\n" + "=" * 70)
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Changes:")
        logger.info("  - Renamed: work_sessions → implementation_tasks")
        logger.info("  - Removed: redundant roadmap_item_id column")
        logger.info("  - Created: implementation_tasks_view (with roadmap_item_id)")
        logger.info("  - Migrated: {} rows".format(new_count))
        logger.info("")
        logger.info("Schema:")
        logger.info("  Table: implementation_tasks (normalized)")
        logger.info("    ├── task_id (renamed from work_id)")
        logger.info("    ├── spec_id (FK → technical_specs.id)")
        logger.info("    └── roadmap_item_id REMOVED ✅")
        logger.info("")
        logger.info("  View: implementation_tasks_view (denormalized)")
        logger.info("    ├── All fields from implementation_tasks")
        logger.info("    └── roadmap_item_id (derived from spec)")
        logger.info("")
        logger.info("Usage:")
        logger.info("  - Use implementation_tasks table for writes")
        logger.info("  - Use implementation_tasks_view for reads (includes roadmap_item_id)")

        return True

    except sqlite3.Error as e:
        logger.error(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def verify_migration(db_path: Path) -> None:
    """Verify migration was successful.

    Args:
        db_path: Path to database file
    """
    logger.info("\n🔍 Verifying migration...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check old table is gone
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_sessions'")
    if cursor.fetchone():
        logger.error("❌ Old work_sessions table still exists!")
    else:
        logger.info("✅ Old work_sessions table removed")

    # Check new table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implementation_tasks'")
    if cursor.fetchone():
        logger.info("✅ New implementation_tasks table exists")
    else:
        logger.error("❌ New implementation_tasks table missing!")

    # Check view exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='implementation_tasks_view'")
    if cursor.fetchone():
        logger.info("✅ implementation_tasks_view exists")
    else:
        logger.error("❌ implementation_tasks_view missing!")

    # Check schema
    cursor.execute("PRAGMA table_info(implementation_tasks)")
    columns = {row[1] for row in cursor.fetchall()}

    if "task_id" in columns:
        logger.info("✅ Column renamed: work_id → task_id")
    else:
        logger.error("❌ task_id column missing!")

    if "roadmap_item_id" not in columns:
        logger.info("✅ Redundant roadmap_item_id column removed")
    else:
        logger.error("❌ roadmap_item_id column still exists in table!")

    # Check view has roadmap_item_id
    cursor.execute("SELECT * FROM implementation_tasks_view LIMIT 0")
    view_columns = {desc[0] for desc in cursor.description}

    if "roadmap_item_id" in view_columns:
        logger.info("✅ View includes roadmap_item_id (derived)")
    else:
        logger.error("❌ View missing roadmap_item_id!")

    conn.close()


if __name__ == "__main__":
    db_path = Path("data/roadmap.db")

    if not db_path.exists():
        logger.error(f"❌ Database not found: {db_path}")
        sys.exit(1)

    logger.info(f"📁 Database: {db_path}")
    logger.info("")

    # Run migration
    success = migrate_work_sessions_to_implementation_tasks(db_path)

    if success:
        # Verify
        verify_migration(db_path)

        logger.info("\n🎉 Migration completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Update code to use implementation_tasks table")
        logger.info("2. Use implementation_tasks_view when roadmap_item_id is needed")
        logger.info("3. Update ImplementationTaskManager to use new names")
        sys.exit(0)
    else:
        logger.error("\n❌ Migration failed")
        sys.exit(1)
