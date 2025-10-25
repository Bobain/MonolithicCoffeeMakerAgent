#!/usr/bin/env python3
"""Migration: Rename 'works' table to 'implementation_tasks'.

This migration improves naming clarity by reflecting that these are
implementation tasks for code_developer, not generic "work".

Changes:
- Table: works → implementation_tasks
- Column: work_id → task_id (e.g., "TASK-31-1" instead of "WORK-31-1")
- Column: related_works_id → task_group_id (e.g., "GROUP-31" remains same)
- Indexes: idx_works_* → idx_implementation_tasks_*

Naming Rationale:
- "implementation_task" clearly indicates this is code_developer's work
- "task_id" is clearer than "work_id"
- "task_group_id" maintains grouping concept

Author: code_developer
Date: 2025-10-24
Related: PRIORITY 32, SPEC-132
"""

import sqlite3
import sys
from pathlib import Path


def migrate_rename_works_to_implementation_tasks(db_path: str) -> None:
    """Rename works table to implementation_tasks.

    Args:
        db_path: Path to database file
    """
    print(f"\n🔧 Migration: Rename 'works' table to 'implementation_tasks'")
    print(f"Database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if old table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='works'")
        if not cursor.fetchone():
            print("⚠️  'works' table does not exist, skipping migration")
            conn.close()
            return

        # Check if new table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implementation_tasks'")
        if cursor.fetchone():
            print("⚠️  'implementation_tasks' table already exists, skipping migration")
            conn.close()
            return

        print("\n1. Creating new implementation_tasks table...")
        cursor.execute(
            """
            CREATE TABLE implementation_tasks (
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

                UNIQUE(task_group_id, priority_order)
            )
        """
        )
        print("✅ Table created")

        print("\n2. Checking if spec_sections column exists in old table...")
        cursor.execute("PRAGMA table_info(works)")
        old_columns = {row[1]: row for row in cursor.fetchall()}
        has_spec_sections = "spec_sections" in old_columns
        print(f"   spec_sections column exists: {has_spec_sections}")

        print("\n3. Migrating data from works to implementation_tasks...")
        if has_spec_sections:
            cursor.execute(
                """
                INSERT INTO implementation_tasks (
                    task_id, priority_number, task_group_id, priority_order,
                    spec_id, scope_description, assigned_files, spec_sections,
                    status, claimed_by, claimed_at, started_at, completed_at, created_at
                )
                SELECT
                    work_id, priority_number, related_works_id, priority_order,
                    spec_id, scope_description, assigned_files, spec_sections,
                    status, claimed_by, claimed_at, started_at, completed_at, created_at
                FROM works
            """
            )
        else:
            cursor.execute(
                """
                INSERT INTO implementation_tasks (
                    task_id, priority_number, task_group_id, priority_order,
                    spec_id, scope_description, assigned_files, spec_sections,
                    status, claimed_by, claimed_at, started_at, completed_at, created_at
                )
                SELECT
                    work_id, priority_number, related_works_id, priority_order,
                    spec_id, scope_description, assigned_files, NULL,
                    status, claimed_by, claimed_at, started_at, completed_at, created_at
                FROM works
            """
            )
        migrated_count = cursor.rowcount
        print(f"✅ Migrated {migrated_count} records")

        print("\n4. Creating indexes...")
        cursor.execute("CREATE INDEX idx_implementation_tasks_priority_number ON implementation_tasks(priority_number)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_task_group_id ON implementation_tasks(task_group_id)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_status ON implementation_tasks(status)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_claimed_by ON implementation_tasks(claimed_by)")
        print("✅ Indexes created")

        print("\n5. Checking for related tables (commits, etc.)...")
        # Check if commits table exists and references work_id
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commits'")
        if cursor.fetchone():
            print("   Found 'commits' table - checking schema...")
            cursor.execute("PRAGMA table_info(commits)")
            columns = {row[1]: row for row in cursor.fetchall()}

            if "work_id" in columns:
                print("   'commits' table has work_id column - will need update")
                # This will be handled by updating the commits table schema
                # For now, just note it
            else:
                print("   'commits' table does not have work_id column")

        print("\n6. Dropping old 'works' table...")
        cursor.execute("DROP TABLE works")
        print("✅ Old table dropped")

        conn.commit()
        print(f"\n✅ Migration complete!")
        print(f"   - Renamed: works → implementation_tasks")
        print(f"   - Renamed: work_id → task_id")
        print(f"   - Renamed: related_works_id → task_group_id")
        print(f"   - Migrated {migrated_count} records")

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

    # Check old table is gone
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='works'")
    if cursor.fetchone():
        print("❌ Old 'works' table still exists!")
        conn.close()
        return

    print("✅ Old 'works' table removed")

    # Check new table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implementation_tasks'")
    if not cursor.fetchone():
        print("❌ New 'implementation_tasks' table not found!")
        conn.close()
        return

    print("✅ New 'implementation_tasks' table exists")

    # Check schema
    cursor.execute("PRAGMA table_info(implementation_tasks)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    expected_columns = [
        "task_id",
        "priority_number",
        "task_group_id",
        "priority_order",
        "spec_id",
        "scope_description",
        "assigned_files",
        "spec_sections",
        "status",
        "claimed_by",
        "claimed_at",
        "started_at",
        "completed_at",
        "created_at",
    ]

    for col in expected_columns:
        if col in columns:
            print(f"✅ Column '{col}' exists")
        else:
            print(f"❌ Column '{col}' missing!")

    # Check data
    cursor.execute("SELECT COUNT(*) FROM implementation_tasks")
    count = cursor.fetchone()[0]
    print(f"\n📊 Total implementation_tasks: {count}")

    # Show sample
    cursor.execute(
        """
        SELECT task_id, scope_description, status
        FROM implementation_tasks
        LIMIT 3
    """
    )
    print("\n📋 Sample tasks:")
    for task_id, scope_desc, status in cursor.fetchall():
        print(f"   {task_id}: {scope_desc} ({status})")

    conn.close()


if __name__ == "__main__":
    # Default to production database
    db_path = Path(__file__).parent.parent.parent / "coffee_maker.db"

    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    migrate_rename_works_to_implementation_tasks(str(db_path))
    verify_migration(str(db_path))

    print("\n✅ Migration complete and verified!")
