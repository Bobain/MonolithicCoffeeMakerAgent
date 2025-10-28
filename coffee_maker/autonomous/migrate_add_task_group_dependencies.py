#!/usr/bin/env python3
"""Migration: Add task_group_dependencies table for managing dependencies between task groups.

This migration creates a new table to track dependencies between implementation task groups,
enabling architect to define which groups must be completed before others can start.

Use Cases:
1. Shared prerequisites: GROUP-A (common utilities) must complete before GROUP-B and GROUP-C
2. Sequential implementation: GROUP-M depends on GROUP-K (database setup before API)
3. Cross-spec dependencies: Multiple specs share common infrastructure

Example:
    SPEC-131 needs database schema (GROUP-K)
    SPEC-132 also needs same database schema (GROUP-K)
    → architect creates GROUP-K first, then GROUP-M and GROUP-N depend on GROUP-K

Author: code_developer
Date: 2025-10-24
Related: PRIORITY 32, SPEC-132, CFR-000
"""

import sqlite3
import sys
from pathlib import Path


def migrate_add_task_group_dependencies(db_path: str) -> None:
    """Add task_group_dependencies table for managing task group dependencies.

    Args:
        db_path: Path to database file
    """
    print(f"\n🔧 Migration: Add task_group_dependencies table")
    print(f"Database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_group_dependencies'")
        if cursor.fetchone():
            print("⚠️  task_group_dependencies table already exists, skipping migration")
            conn.close()
            return

        print("\n1. Creating task_group_dependencies table...")
        cursor.execute(
            """
            CREATE TABLE task_group_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_group_id TEXT NOT NULL,           -- Group that has dependency (e.g., "GROUP-31")
                depends_on_group_id TEXT NOT NULL,     -- Group that must complete first (e.g., "GROUP-30")
                dependency_type TEXT NOT NULL,         -- "hard" (blocking) or "soft" (preferred)
                reason TEXT,                           -- Why this dependency exists
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,              -- Agent that created this (typically "architect")

                -- Constraints
                UNIQUE(task_group_id, depends_on_group_id),
                CHECK(task_group_id != depends_on_group_id),  -- Cannot depend on self
                CHECK(dependency_type IN ('hard', 'soft'))
            )
        """
        )
        print("✅ task_group_dependencies table created")

        print("\n2. Creating indexes...")
        cursor.execute("CREATE INDEX idx_task_group_dependencies_group ON task_group_dependencies(task_group_id)")
        cursor.execute(
            "CREATE INDEX idx_task_group_dependencies_depends_on ON task_group_dependencies(depends_on_group_id)"
        )
        cursor.execute("CREATE INDEX idx_task_group_dependencies_type ON task_group_dependencies(dependency_type)")
        print("✅ Indexes created")

        conn.commit()
        print(f"\n✅ Migration complete!")
        print(f"   - Added: task_group_dependencies table")
        print(f"   - Supports: hard (blocking) and soft (preferred) dependencies")
        print(f"   - Enables: Architect to define prerequisite task groups")
        print(f"   - Use case: GROUP-M and GROUP-N depend on GROUP-K")

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
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_group_dependencies'")
    if not cursor.fetchone():
        print("❌ task_group_dependencies table not found!")
        conn.close()
        return

    print("✅ task_group_dependencies table exists")

    # Check schema
    cursor.execute("PRAGMA table_info(task_group_dependencies)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    expected_columns = [
        "id",
        "task_group_id",
        "depends_on_group_id",
        "dependency_type",
        "reason",
        "created_at",
        "created_by",
    ]
    for col in expected_columns:
        if col in columns:
            print(f"✅ Column '{col}' exists ({columns[col]})")
        else:
            print(f"❌ Column '{col}' missing!")

    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='task_group_dependencies'")
    indexes = [row[0] for row in cursor.fetchall()]

    if "idx_task_group_dependencies_group" in indexes:
        print("✅ Index 'idx_task_group_dependencies_group' exists")
    else:
        print("❌ Index 'idx_task_group_dependencies_group' missing!")

    if "idx_task_group_dependencies_depends_on" in indexes:
        print("✅ Index 'idx_task_group_dependencies_depends_on' exists")
    else:
        print("❌ Index 'idx_task_group_dependencies_depends_on' missing!")

    conn.close()


if __name__ == "__main__":
    # Default to production database
    db_path = Path(__file__).parent.parent.parent / "coffee_maker.db"

    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    migrate_add_task_group_dependencies(str(db_path))
    verify_migration(str(db_path))

    print("\n✅ Migration complete and verified!")
