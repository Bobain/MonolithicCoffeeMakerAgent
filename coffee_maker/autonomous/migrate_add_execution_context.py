#!/usr/bin/env python3
"""Migration: Add execution context fields to implementation_tasks.

This migration replaces the useless claimed_by field with useful execution context:
- claimed_by → process_id (PID of code_developer process)
- Add worktree_path (path to git worktree for parallel execution)
- Add branch_name (git branch for implementation task, e.g., "roadmap-implementation_task-TASK-31-1")

Rationale:
- claimed_by was always "code_developer" (useless)
- process_id enables monitoring which process is working on which task
- worktree_path + branch_name enable parallel execution with git worktrees
- Essential for orchestrator to manage parallel code_developer instances

Author: code_developer
Date: 2025-10-24
Related: PRIORITY 32, SPEC-132, CFR-000
"""

import sqlite3
import sys
from pathlib import Path


def migrate_add_execution_context(db_path: str) -> None:
    """Add execution context fields to implementation_tasks table.

    Args:
        db_path: Path to database file
    """
    print(f"\n🔧 Migration: Add execution context to implementation_tasks")
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
        cursor.execute("SELECT * FROM implementation_tasks")
        rows = cursor.fetchall()
        print(f"   Found {len(rows)} existing tasks")

        # Get column names
        cursor.execute("PRAGMA table_info(implementation_tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current columns: {', '.join(columns)}")

        print("\n2. Creating new table with execution context fields...")
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

                -- Execution Context (NEW/CHANGED)
                process_id INTEGER,                  -- PID of code_developer process
                worktree_path TEXT,                  -- Path to git worktree
                branch_name TEXT,                    -- Git branch (e.g., "roadmap-implementation_task-TASK-31-1")

                -- Timestamps
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
        print("✅ New table created")

        print("\n3. Migrating data to new table...")
        if rows:
            # Map old columns to new columns
            # claimed_by → NULL (was useless, will use process_id instead)
            # Add new columns: process_id, worktree_path, branch_name

            for row in rows:
                old_data = dict(zip(columns, row))

                cursor.execute(
                    """
                    INSERT INTO implementation_tasks_new (
                        task_id, priority_number, task_group_id, priority_order,
                        spec_id, scope_description, assigned_files, spec_sections,
                        status, process_id, worktree_path, branch_name,
                        claimed_at, started_at, completed_at, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        old_data["task_id"],
                        old_data["priority_number"],
                        old_data["task_group_id"],
                        old_data["priority_order"],
                        old_data["spec_id"],
                        old_data["scope_description"],
                        old_data["assigned_files"],
                        old_data.get("spec_sections"),
                        old_data["status"],
                        None,  # process_id (new)
                        None,  # worktree_path (new)
                        None,  # branch_name (new)
                        old_data.get("claimed_at"),
                        old_data.get("started_at"),
                        old_data.get("completed_at"),
                        old_data["created_at"],
                    ),
                )

            print(f"✅ Migrated {len(rows)} tasks")
        else:
            print("   No data to migrate")

        print("\n4. Recreating indexes...")
        # Drop old indexes
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_priority_number")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_task_group_id")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_status")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_claimed_by")
        cursor.execute("DROP INDEX IF EXISTS idx_implementation_tasks_spec_id")

        # Create new indexes
        cursor.execute(
            "CREATE INDEX idx_implementation_tasks_priority_number ON implementation_tasks_new(priority_number)"
        )
        cursor.execute("CREATE INDEX idx_implementation_tasks_task_group_id ON implementation_tasks_new(task_group_id)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_status ON implementation_tasks_new(status)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_process_id ON implementation_tasks_new(process_id)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_spec_id ON implementation_tasks_new(spec_id)")
        cursor.execute("CREATE INDEX idx_implementation_tasks_branch_name ON implementation_tasks_new(branch_name)")
        print("✅ Indexes recreated (replaced claimed_by → process_id, added branch_name)")

        print("\n5. Swapping tables...")
        cursor.execute("DROP TABLE implementation_tasks")
        cursor.execute("ALTER TABLE implementation_tasks_new RENAME TO implementation_tasks")
        print("✅ Tables swapped")

        conn.commit()
        print(f"\n✅ Migration complete!")
        print(f"   - Removed: claimed_by (always 'code_developer')")
        print(f"   - Added: process_id (PID of code_developer process)")
        print(f"   - Added: worktree_path (git worktree path)")
        print(f"   - Added: branch_name (git branch for parallel execution)")

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

    # Check schema
    cursor.execute("PRAGMA table_info(implementation_tasks)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    # Check old column is gone
    if "claimed_by" in columns:
        print("❌ Old 'claimed_by' column still exists!")
    else:
        print("✅ Old 'claimed_by' column removed")

    # Check new columns exist
    expected_new_columns = ["process_id", "worktree_path", "branch_name"]
    for col in expected_new_columns:
        if col in columns:
            print(f"✅ New column '{col}' exists ({columns[col]})")
        else:
            print(f"❌ New column '{col}' missing!")

    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='implementation_tasks'")
    indexes = [row[0] for row in cursor.fetchall()]

    if "idx_implementation_tasks_claimed_by" in indexes:
        print("❌ Old index 'idx_implementation_tasks_claimed_by' still exists!")
    else:
        print("✅ Old index 'idx_implementation_tasks_claimed_by' removed")

    if "idx_implementation_tasks_process_id" in indexes:
        print("✅ New index 'idx_implementation_tasks_process_id' exists")
    else:
        print("❌ New index 'idx_implementation_tasks_process_id' missing!")

    if "idx_implementation_tasks_branch_name" in indexes:
        print("✅ New index 'idx_implementation_tasks_branch_name' exists")
    else:
        print("❌ New index 'idx_implementation_tasks_branch_name' missing!")

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

    migrate_add_execution_context(str(db_path))
    verify_migration(str(db_path))

    print("\n✅ Migration complete and verified!")
