#!/usr/bin/env python3
"""Migration script to add work_sessions table for parallel development tracking.

This table tracks code_developer work sessions in separate git worktrees,
enabling controlled parallelization (2-3 concurrent instances).

Usage:
    python coffee_maker/autonomous/migrate_add_work_sessions.py
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def migrate_database():
    """Add work_sessions table to unified database."""
    db_path = Path("data/unified_roadmap_specs.db")

    if not db_path.exists():
        logger.warning("Database does not exist yet - will be created with new schema")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_sessions'")
        exists = cursor.fetchone()

        if exists:
            logger.info("work_sessions table already exists - no migration needed")
            conn.close()
            return True

        logger.info("Creating work_sessions table...")

        # Create work_sessions table
        cursor.execute(
            """
            CREATE TABLE work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id TEXT NOT NULL UNIQUE,           -- e.g., "WORK-42"
                spec_id TEXT NOT NULL,                  -- Links to technical_specs.id
                roadmap_item_id TEXT,                   -- Links to roadmap_items.id
                scope TEXT NOT NULL,                    -- "phase", "section", "module"
                scope_description TEXT,                 -- Human-readable scope description
                assigned_files TEXT,                    -- JSON array of file paths this work touches
                branch_name TEXT NOT NULL UNIQUE,       -- e.g., "roadmap-work-42"
                worktree_path TEXT,                     -- Path to git worktree
                status TEXT NOT NULL DEFAULT 'pending', -- "pending", "in_progress", "completed", "failed"
                claimed_by TEXT,                        -- "code_developer"
                claimed_at TEXT,                        -- When work was claimed
                started_at TEXT,                        -- When work actually started
                completed_at TEXT,                      -- When work finished
                commit_sha TEXT,                        -- Final commit SHA
                merged_at TEXT,                         -- When merged to roadmap branch
                created_by TEXT NOT NULL DEFAULT 'architect', -- Who created this work session
                created_at TEXT NOT NULL,               -- When work session was created

                FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE CASCADE,
                FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id) ON DELETE SET NULL
            )
        """
        )

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_status ON work_sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_spec ON work_sessions(spec_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_roadmap ON work_sessions(roadmap_item_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_branch ON work_sessions(branch_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_work_sessions_claimed_at ON work_sessions(claimed_at)")

        conn.commit()
        logger.info("✅ Successfully created work_sessions table with indexes")

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
