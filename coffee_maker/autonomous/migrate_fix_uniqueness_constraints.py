#!/usr/bin/env python3
"""Migration: Fix uniqueness constraints on implementation_tasks.

This migration updates the UNIQUE constraints to properly enforce:
1. Unique (priority_number, priority_order) - One order per priority
2. Unique (spec_id, priority_order) - One order per spec
3. Unique (task_group_id, priority_order) - One order per group
4. Unique (spec_id, scope_description, spec_sections) - No duplicate tasks for same spec scope

Rationale:
- priority_number x priority_order: Ensures sequential order within a ROADMAP priority
- spec_id x priority_order: Ensures sequential order within a technical spec
- task_group_id x priority_order: Maintains grouping for related tasks
- spec_id x scope_description x spec_sections: Prevents duplicate tasks for same work scope
  (e.g., can't have two "Phase 1: Database Schema" tasks with same sections for SPEC-131)

Author: code_developer
Date: 2025-10-24
Related: PRIORITY 32, SPEC-132
"""

import sqlite3
import sys
from pathlib import Path


def migrate_fix_uniqueness_constraints(db_path: str) -> None:
    """Fix UNIQUE constraints on implementation_tasks table.

    Args:
        db_path: Path to database file
    """
    print(f"\n🔧 Migration: Fix uniqueness constraints on implementation_tasks")
    print(f"Database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implementation_tasks'")
        if not cursor.fetchone():
            print("⚠️  implementation_tasks table does not exist, skipping migration")
            conn.close()
            return

        print("\n1. Reading current table schema and data...")
        # Get current data
        cursor.execute("SELECT * FROM implementation_tasks")
        rows = cursor.fetchall()
        print(f"   Found {len(rows)} existing tasks")

        # Get column names
        cursor.execute("PRAGMA table_info(implementation_tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"   Columns: {', '.join(columns)}")

        print("\n2. Creating new table with updated constraints...")
        cursor.execute(
            """
            CREATE TABLE implementation_tasks_new (
                task_id TEXT PRIMARY KEY,
                priority_number INTEGER NOT NULL,
                task_group_id TEXT NOT NULL,
                priority_order INTEGER NOT NULL,
                spec_id TEXT NOT NULL,
                scope_description TEXT NOT NULL,
                assigned_files TEXT NOT NULL,
                spec_sections TEXT,
                status TEXT NOT NULL,
                claimed_by TEXT,
                claimed_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                created_at TEXT NOT NULL,

                UNIQUE(priority_number, priority_order),
                UNIQUE(spec_id, priority_order),
                UNIQUE(task_group_id, priority_order),
                UNIQUE(spec_id, scope_description, spec_sections)
            )
        """
        )
        print("✅ New table created with correct constraints")

        print("\n3. Migrating data to new table...")
        if rows:
            placeholders = ",".join(["?"] * len(columns))
            cursor.executemany(
                f"INSERT INTO implementation_tasks_new ({','.join(columns)}) VALUES ({placeholders})",
                rows,
            )
            print(f"✅ Migrated {len(rows)} tasks")
        else:
            print("   No data to migrate")

        print("\n4. Recreating indexes...")
        # Drop all old indexes
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_priority_number")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_task_group_id")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_status")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_claimed_by")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_spec_id")

        # Create indexes on new table
        cursor.execute(
            "CREATE INDEX idx_implementation_tasks_priority_number ON implementation_tasks_new(priority_number)"
        )
        cursor.execute("CREATE INDEX idx_implementation_tasks_task_group_id ON implementation_tasks_new(task_group_id)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_status ON implementation_tasks_new(status)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_claimed_by ON implementation_tasks_new(claimed_by)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_spec_id ON implementation_tasks_new(spec_id)")
        print("✅ Indexes recreated (including spec_id index)")

        print("\n5. Swapping tables...")
        cursor.execute("DROP TABLE implementation_tasks")
        cursor.execute("ALTER TABLE implementation_tasks_new RENAME TO implementation_tasks")
        print("✅ Tables swapped")

        conn.commit()
        print(f"\n✅ Migration complete!")
        print(f"   - Added UNIQUE(priority_number, priority_order)")
        print(f"   - Added UNIQUE(spec_id, priority_order)")
        print(f"   - Kept UNIQUE(task_group_id, priority_order)")
        print(f"   - Added UNIQUE(spec_id, scope_description, spec_sections)")
        print(f"   - Added index on spec_id")

    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_migration(db_path: str) -> None:
    """Verify migration was successful.

    Args:
        db_path: Path to database file
    """
    print("\n🔍 Verifying migration...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implementation_tasks'")
    if not cursor.fetchone():
        print("❌ implementation_tasks table not found!")
        conn.close()
        return

    print("✅ implementation_tasks table exists")

    # Check constraints by examining schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='implementation_tasks'")
    schema = cursor.fetchone()[0]

    if "UNIQUE(priority_number, priority_order)" in schema:
        print("✅ UNIQUE(priority_number, priority_order) constraint present")
    else:
        print("❌ UNIQUE(priority_number, priority_order) constraint missing!")

    if "UNIQUE(spec_id, priority_order)" in schema:
        print("✅ UNIQUE(spec_id, priority_order) constraint present")
    else:
        print("❌ UNIQUE(spec_id, priority_order) constraint missing!")

    if "UNIQUE(task_group_id, priority_order)" in schema:
        print("✅ UNIQUE(task_group_id, priority_order) constraint present")
    else:
        print("❌ UNIQUE(task_group_id, priority_order) constraint missing!")

    if "UNIQUE(spec_id, scope_description, spec_sections)" in schema:
        print("✅ UNIQUE(spec_id, scope_description, spec_sections) constraint present")
    else:
        print("❌ UNIQUE(spec_id, scope_description, spec_sections) constraint missing!")

    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='implementation_tasks'")
    indexes = [row[0] for row in cursor.fetchall()]
    print(f"\n📋 Indexes: {', '.join(indexes)}")

    # Check data
    cursor.execute("SELECT COUNT(*) FROM implementation_tasks")
    count = cursor.fetchone()[0]
    print(f"\n📊 Total tasks: {count}")

    conn.close()


if __name__ == "__main__":
    # Default to production database
    db_path = Path(__file__).parent.parent.parent / "coffee_maker.db"

    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    migrate_fix_uniqueness_constraints(str(db_path))
    verify_migration(str(db_path))

    print("\n✅ Migration complete and verified!")
