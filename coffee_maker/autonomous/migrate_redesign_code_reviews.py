#!/usr/bin/env python3
"""Migration: Redesign code review system to review complete implementations.

OLD DESIGN (commit-level):
- Review every single commit
- Too granular, too noisy
- No context about overall feature

NEW DESIGN (roadmap-item-level):
- Track commits per roadmap_item during implementation
- Review ALL commits for a roadmap_item together (before marking complete)
- Generate comprehensive review summary
- Architect reviews the summary
- Delete commit records after review (cleanup)

Tables:
1. implementation_commits - Track commits during implementation (temporary)
2. code_reviews - Store final review summaries (permanent)

Author: architect
Date: 2025-10-24
Related: User request for implementation-level reviews
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def redesign_code_reviews(db_path: Path) -> bool:
    """Redesign code review system for implementation-level reviews.

    Args:
        db_path: Path to database file

    Returns:
        True if successful
    """
    logger.info("=" * 70)
    logger.info("Migration: Redesign Code Review System")
    logger.info("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: Drop old review tables if they exist
        logger.info("\n1. Dropping old review tables...")

        old_tables = ["commit_reviews", "review_reports", "review_comments"]
        for table in old_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            logger.info(f"   Dropped {table} (old design)")

        conn.commit()

        # Step 2: Create implementation_commits table (temporary tracking)
        logger.info("\n2. Creating implementation_commits table...")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS implementation_commits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadmap_item_id TEXT NOT NULL,
                commit_hash TEXT NOT NULL,
                commit_message TEXT NOT NULL,
                commit_author TEXT NOT NULL,
                commit_date TEXT NOT NULL,
                files_changed TEXT NOT NULL,      -- JSON array of file paths
                insertions INTEGER NOT NULL,
                deletions INTEGER NOT NULL,
                created_at TEXT NOT NULL,

                FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id) ON DELETE CASCADE
            )
        """
        )
        logger.info("✅ Created implementation_commits table")

        # Step 3: Create code_reviews table (permanent summaries)
        logger.info("\n3. Creating code_reviews table...")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS code_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadmap_item_id TEXT NOT NULL UNIQUE,
                spec_id TEXT,                      -- Link to technical spec

                -- Review metadata
                review_date TEXT NOT NULL,
                reviewer TEXT NOT NULL,            -- Always "code_reviewer"
                commits_reviewed INTEGER NOT NULL, -- How many commits reviewed

                -- Review summary
                summary TEXT NOT NULL,             -- Overall assessment
                quality_score INTEGER,             -- 1-10 score

                -- Issues found
                critical_issues TEXT,              -- JSON array of critical issues
                warnings TEXT,                     -- JSON array of warnings
                suggestions TEXT,                  -- JSON array of suggestions

                -- Compliance
                follows_spec BOOLEAN NOT NULL,     -- Does implementation follow spec?
                test_coverage_ok BOOLEAN NOT NULL, -- Adequate test coverage?
                style_compliant BOOLEAN NOT NULL,  -- Follows style guide?

                -- Architect review
                architect_reviewed BOOLEAN DEFAULT FALSE,
                architect_reviewed_at TEXT,
                architect_comments TEXT,

                -- Metadata
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id) ON DELETE CASCADE,
                FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
            )
        """
        )
        logger.info("✅ Created code_reviews table")

        # Step 4: Create indexes
        logger.info("\n4. Creating indexes...")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_impl_commits_roadmap ON implementation_commits(roadmap_item_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_impl_commits_hash ON implementation_commits(commit_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_code_reviews_roadmap ON code_reviews(roadmap_item_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_code_reviews_architect ON code_reviews(architect_reviewed)")

        logger.info("✅ Created indexes")

        conn.commit()

        # Step 5: Verify
        logger.info("\n5. Verifying migration...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        if "implementation_commits" in tables:
            logger.info("✅ implementation_commits table exists")
        if "code_reviews" in tables:
            logger.info("✅ code_reviews table exists")

        logger.info("\n" + "=" * 70)
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("New design:")
        logger.info("  1. code_developer tracks commits in implementation_commits")
        logger.info("  2. code_reviewer reviews ALL commits for roadmap_item")
        logger.info("  3. code_reviewer generates summary in code_reviews")
        logger.info("  4. architect reviews the summary")
        logger.info("  5. code_reviewer deletes implementation_commits after review")
        logger.info("")
        logger.info("Tables:")
        logger.info("  implementation_commits - Temporary commit tracking")
        logger.info("  code_reviews - Permanent review summaries")

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

    success = redesign_code_reviews(db_path)

    if success:
        logger.info("\n🎉 Migration completed successfully!")
        logger.info("\nNew workflow:")
        logger.info(
            """
1. code_developer commits code:
   - Tracks each commit in implementation_commits table
   - Links to roadmap_item_id

2. When roadmap_item implementation complete:
   - code_reviewer triggered
   - Reads ALL commits for that roadmap_item
   - Reads technical spec
   - Generates comprehensive review

3. code_reviewer stores review:
   - Creates entry in code_reviews table
   - Deletes commits from implementation_commits (cleanup)

4. architect reviews summary:
   - Reads code_reviews where architect_reviewed = FALSE
   - Marks as reviewed after reading
"""
        )
        exit(0)
    else:
        logger.error("\n❌ Migration failed")
        exit(1)
