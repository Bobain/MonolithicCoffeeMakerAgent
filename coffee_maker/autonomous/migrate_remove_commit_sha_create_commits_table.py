"""Migration: Remove commit_sha from works, create commits table.

A work can have multiple commits (code_developer may commit multiple times).
The commits table enables code_developer ↔ code_reviewer synchronization.

BEFORE:
- works.commit_sha (single commit per work - WRONG)

AFTER:
- commits table tracks ALL commits for a work
- code_reviewer reads from commits table to review all commits

Author: code_developer
Date: 2025-10-23
Related: PRIORITY 31, CFR-000
"""

import sqlite3
import sys
from pathlib import Path


def migrate_create_commits_table(db_path: str) -> None:
    """Remove commit_sha from works and create commits table.

    Steps:
    1. Create commits table
    2. Migrate existing commit_sha data (if any) to commits table
    3. Remove commit_sha column from works table

    Args:
        db_path: Path to SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Starting migration: Remove commit_sha, create commits table...")

        # Check if commits table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commits'")
        commits_exists = cursor.fetchone() is not None

        if commits_exists:
            print("✅ commits table already exists - skipping migration")
            return

        # 1. CREATE COMMITS TABLE
        print("📝 Creating commits table...")
        cursor.execute(
            """
            CREATE TABLE commits (
                commit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id TEXT NOT NULL,
                commit_sha TEXT NOT NULL,
                commit_message TEXT,
                committed_at TEXT NOT NULL,
                reviewed_by TEXT,
                review_status TEXT,
                review_notes TEXT,

                FOREIGN KEY (work_id) REFERENCES works(work_id)
            )
        """
        )
        print("✅ commits table created")

        # 2. MIGRATE EXISTING COMMIT_SHA DATA
        print("🔄 Migrating existing commit_sha data to commits table...")

        # Check if works table has commit_sha column
        cursor.execute("PRAGMA table_info(works)")
        columns = [col[1] for col in cursor.fetchall()]

        if "commit_sha" in columns:
            # Read all works with commit_sha
            cursor.execute("SELECT work_id, commit_sha, completed_at FROM works WHERE commit_sha IS NOT NULL")
            works_with_commits = cursor.fetchall()

            migrated_count = 0

            for work_id, commit_sha, completed_at in works_with_commits:
                # Insert into commits table
                cursor.execute(
                    """
                    INSERT INTO commits (work_id, commit_sha, committed_at)
                    VALUES (?, ?, ?)
                """,
                    (work_id, commit_sha, completed_at or "unknown"),
                )
                migrated_count += 1

            if migrated_count > 0:
                print(f"✅ Migrated {migrated_count} commit_sha records to commits table")
            else:
                print("ℹ️  No commit_sha data to migrate")

            # 3. REMOVE COMMIT_SHA COLUMN FROM WORKS TABLE
            print("🗑️  Removing commit_sha column from works table...")

            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            # Create temporary table without commit_sha
            cursor.execute(
                """
                CREATE TABLE works_new (
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
                    created_at TEXT NOT NULL,

                    UNIQUE(related_works_id, priority_order)
                )
            """
            )

            # Copy data from old table to new table
            cursor.execute(
                """
                INSERT INTO works_new (
                    work_id, priority_number, related_works_id, priority_order,
                    spec_id, scope_description, assigned_files, status,
                    claimed_by, claimed_at, started_at, completed_at, created_at
                )
                SELECT
                    work_id, priority_number, related_works_id, priority_order,
                    spec_id, scope_description, assigned_files, status,
                    claimed_by, claimed_at, started_at, completed_at, created_at
                FROM works
            """
            )

            # Drop old table
            cursor.execute("DROP TABLE works")

            # Rename new table
            cursor.execute("ALTER TABLE works_new RENAME TO works")

            # Recreate indexes
            cursor.execute("CREATE INDEX idx_works_priority_number ON works(priority_number)")
            cursor.execute("CREATE INDEX idx_works_related_works_id ON works(related_works_id)")
            cursor.execute("CREATE INDEX idx_works_status ON works(status)")
            cursor.execute("CREATE INDEX idx_works_claimed_by ON works(claimed_by)")

            print("✅ commit_sha column removed from works table")
        else:
            print("ℹ️  works table doesn't have commit_sha column - skipping removal")

        # 4. CREATE INDEXES FOR COMMITS TABLE
        print("📇 Creating indexes on commits table...")
        cursor.execute("CREATE INDEX idx_commits_work_id ON commits(work_id)")
        cursor.execute("CREATE INDEX idx_commits_review_status ON commits(review_status)")
        print("✅ Indexes created")

        conn.commit()
        print("=" * 60)
        print("✅ Migration complete: commit_sha removed, commits table created")
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
    migrate_create_commits_table(db_path)


if __name__ == "__main__":
    main()
