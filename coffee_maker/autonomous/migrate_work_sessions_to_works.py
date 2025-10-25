"""Migration: Rename work_sessions → works and add related_works_id + priority_order.

This migration transforms the incorrect work_sessions model to the correct works model:

BEFORE (work_sessions):
- Designed for pre-split subtasks
- No grouping mechanism
- No ordering enforcement

AFTER (works):
- related_works_id: Groups sequential works (e.g., "GROUP-31" for 4 phases)
- priority_order: Enforces sequential execution within group (1, 2, 3, 4)
- priority_number: Links to ROADMAP PRIORITY number

Author: code_developer
Date: 2025-10-23
Related: PRIORITY 31, CFR-000
"""

import sqlite3
import sys
from pathlib import Path


def migrate_work_sessions_to_works(db_path: str) -> None:
    """Migrate work_sessions table to works table.

    Steps:
    1. Create new works table with correct schema
    2. Migrate existing data (if any) from work_sessions
    3. Drop old work_sessions table
    4. Create indexes

    Args:
        db_path: Path to SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Starting migration: work_sessions → works...")

        # Check if work_sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_sessions'")
        work_sessions_exists = cursor.fetchone() is not None

        # Check if works table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='works'")
        works_exists = cursor.fetchone() is not None

        if works_exists:
            print("✅ works table already exists - skipping migration")
            return

        # 1. CREATE NEW WORKS TABLE
        print("📝 Creating works table...")
        cursor.execute(
            """
            CREATE TABLE works (
                work_id TEXT PRIMARY KEY,
                priority_number INTEGER NOT NULL,
                related_works_id TEXT NOT NULL,
                priority_order INTEGER NOT NULL,
                spec_id TEXT NOT NULL,
                scope_description TEXT NOT NULL,
                assigned_files TEXT NOT NULL,
                status TEXT NOT NULL,
                claimed_by TEXT,
                claimed_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                commit_sha TEXT,
                created_at TEXT NOT NULL,

                UNIQUE(related_works_id, priority_order)
            )
        """
        )
        print("✅ works table created")

        # 2. MIGRATE EXISTING DATA (if work_sessions exists)
        if work_sessions_exists:
            print("🔄 Migrating data from work_sessions...")

            # Read all work_sessions
            cursor.execute("SELECT * FROM work_sessions")
            work_sessions = cursor.fetchall()

            if work_sessions:
                # Get column names
                cursor.execute("PRAGMA table_info(work_sessions)")
                columns = [col[1] for col in cursor.fetchall()]

                migrated_count = 0

                for row in work_sessions:
                    work_session = dict(zip(columns, row))

                    # Extract priority_number from work_id (e.g., "WORK-31-1" → 31)
                    work_id = work_session["work_id"]
                    try:
                        priority_number = int(work_id.split("-")[1])
                    except (IndexError, ValueError):
                        priority_number = 0  # Default for malformed IDs

                    # Generate related_works_id from priority_number
                    related_works_id = f"GROUP-{priority_number}"

                    # Extract priority_order from work_id (e.g., "WORK-31-1" → 1)
                    try:
                        priority_order = int(work_id.split("-")[2])
                    except (IndexError, ValueError):
                        priority_order = 1  # Default

                    # Insert into works table
                    cursor.execute(
                        """
                        INSERT INTO works (
                            work_id, priority_number, related_works_id, priority_order,
                            spec_id, scope_description, assigned_files, status,
                            claimed_by, claimed_at, started_at, completed_at, commit_sha, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            work_session["work_id"],
                            priority_number,
                            related_works_id,
                            priority_order,
                            work_session["spec_id"],
                            work_session["scope_description"],
                            work_session["assigned_files"],
                            work_session["status"],
                            work_session.get("claimed_by"),
                            work_session.get("claimed_at"),
                            work_session.get("started_at"),
                            work_session.get("completed_at"),
                            work_session.get("commit_sha"),
                            work_session["created_at"],
                        ),
                    )
                    migrated_count += 1

                print(f"✅ Migrated {migrated_count} work_sessions → works")
            else:
                print("ℹ️  No work_sessions to migrate (empty table)")

            # 3. DROP OLD TABLE
            print("🗑️  Dropping work_sessions table...")
            cursor.execute("DROP TABLE work_sessions")
            print("✅ work_sessions table dropped")
        else:
            print("ℹ️  work_sessions table doesn't exist - clean migration")

        # 4. CREATE INDEXES
        print("📇 Creating indexes...")
        cursor.execute("CREATE INDEX idx_works_priority_number ON works(priority_number)")
        cursor.execute("CREATE INDEX idx_works_related_works_id ON works(related_works_id)")
        cursor.execute("CREATE INDEX idx_works_status ON works(status)")
        cursor.execute("CREATE INDEX idx_works_claimed_by ON works(claimed_by)")
        print("✅ Indexes created")

        conn.commit()
        print("=" * 60)
        print("✅ Migration complete: work_sessions → works")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


def main():
    """Run migration on unified database."""
    # Default database path
    db_path = "coffee_maker.db"

    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("   Run this script from project root directory")
        sys.exit(1)

    print(f"📦 Database: {db_path}")
    migrate_work_sessions_to_works(db_path)


if __name__ == "__main__":
    main()
