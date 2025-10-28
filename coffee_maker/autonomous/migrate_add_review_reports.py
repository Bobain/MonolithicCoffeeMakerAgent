#!/usr/bin/env python3
"""Migration script to add review_reports table to unified database.

This migration adds the review_reports table for storing code review reports
in the database instead of files, fixing the CFR-015 violation.

Usage:
    python coffee_maker/autonomous/migrate_add_review_reports.py
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate_database():
    """Add review_reports table to unified database if it doesn't exist."""
    db_path = Path("data/unified_roadmap_specs.db")

    if not db_path.exists():
        logger.warning("Database does not exist yet - will be created with new schema")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='review_reports'")
        exists = cursor.fetchone()

        if not exists:
            logger.info("Creating review_reports table...")

            # Create the table
            cursor.execute(
                """
                CREATE TABLE review_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_review_id INTEGER NOT NULL,
                    commit_sha TEXT NOT NULL,
                    spec_id TEXT,

                    -- Report metadata
                    date TEXT NOT NULL,
                    reviewer TEXT NOT NULL DEFAULT 'code_reviewer',
                    review_duration_seconds REAL,

                    -- Metrics
                    files_changed INTEGER,
                    lines_added INTEGER,
                    lines_deleted INTEGER,
                    quality_score INTEGER NOT NULL,
                    approved BOOLEAN NOT NULL,

                    -- Issues (JSON)
                    issues TEXT,
                    style_compliance TEXT,
                    architecture_compliance TEXT,

                    -- Content
                    overall_assessment TEXT NOT NULL,
                    full_report_markdown TEXT,

                    -- Architect follow-up
                    needs_architect_review BOOLEAN DEFAULT 0,
                    architect_reviewed_at TEXT,
                    architect_notes TEXT,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY (commit_review_id) REFERENCES commit_reviews(id) ON DELETE CASCADE,
                    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX idx_review_reports_score ON review_reports(quality_score)")
            cursor.execute("CREATE INDEX idx_review_reports_spec ON review_reports(spec_id)")
            cursor.execute("CREATE INDEX idx_review_reports_needs_review ON review_reports(needs_architect_review)")
            cursor.execute("CREATE INDEX idx_review_reports_approved ON review_reports(approved)")
            cursor.execute("CREATE INDEX idx_review_reports_commit ON review_reports(commit_review_id)")

            conn.commit()
            logger.info("✅ Successfully created review_reports table with indexes")
        else:
            logger.info("Table review_reports already exists - no migration needed")

        conn.close()
        return True

    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    if migrate_database():
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
        exit(1)
