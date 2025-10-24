#!/usr/bin/env python3
"""Consolidate all databases into data/roadmap.db.

This migration consolidates:
- specs.db (64 technical_specs)
- unified_roadmap_specs.db (6 technical_specs + reviews + work_sessions)

Into a single unified database: data/roadmap.db

Migration Steps:
1. Add missing tables to roadmap.db (technical_specs, spec_audit, commit_reviews, etc.)
2. Import all technical specs (handle duplicates)
3. Import commit reviews and work sessions
4. Link roadmap items to technical specs (fix NULL spec_id values)
5. Verify data integrity

Author: architect
Date: 2025-10-24
Related: User request for database consolidation
"""

import logging
import sqlite3
import sys
from pathlib import Path
from typing import Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DatabaseConsolidator:
    """Consolidate multiple databases into data/roadmap.db."""

    def __init__(self):
        """Initialize consolidator."""
        self.roadmap_db = Path("data/roadmap.db")
        self.specs_db = Path("data/specs.db")
        self.unified_db = Path("data/unified_roadmap_specs.db")

        # Verify all databases exist
        if not self.roadmap_db.exists():
            raise FileNotFoundError(f"Target database not found: {self.roadmap_db}")
        if not self.specs_db.exists():
            logger.warning(f"Source database not found: {self.specs_db}")
        if not self.unified_db.exists():
            logger.warning(f"Source database not found: {self.unified_db}")

    def add_missing_tables(self) -> None:
        """Add missing tables to roadmap.db."""
        logger.info("=" * 70)
        logger.info("Step 1: Adding missing tables to roadmap.db")
        logger.info("=" * 70)

        conn = sqlite3.connect(self.roadmap_db)
        cursor = conn.cursor()

        try:
            # Check what tables already exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            logger.info(f"Existing tables: {', '.join(sorted(existing_tables))}")

            # Add technical_specs table (unified schema from unified_roadmap_specs.db)
            if "technical_specs" not in existing_tables:
                logger.info("Creating technical_specs table...")
                cursor.execute(
                    """
                    CREATE TABLE technical_specs (
                        id TEXT PRIMARY KEY,
                        spec_number INTEGER NOT NULL UNIQUE,
                        title TEXT NOT NULL,
                        roadmap_item_id TEXT,
                        status TEXT NOT NULL DEFAULT 'draft',
                        spec_type TEXT DEFAULT 'monolithic',
                        file_path TEXT,
                        content TEXT,
                        dependencies TEXT,
                        estimated_hours REAL,
                        actual_hours REAL,
                        updated_at TEXT NOT NULL,
                        updated_by TEXT NOT NULL,
                        started_at TEXT,
                        phase TEXT
                    )
                """
                )
                cursor.execute("CREATE INDEX idx_specs_roadmap ON technical_specs(roadmap_item_id)")
                cursor.execute("CREATE INDEX idx_specs_status ON technical_specs(status)")
                cursor.execute("CREATE INDEX idx_specs_number ON technical_specs(spec_number)")
                logger.info("✅ Created technical_specs table")
            else:
                logger.info("✅ technical_specs table already exists")

            # Add spec_audit table
            if "spec_audit" not in existing_tables:
                logger.info("Creating spec_audit table...")
                cursor.execute(
                    """
                    CREATE TABLE spec_audit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        spec_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        field_changed TEXT,
                        old_value TEXT,
                        new_value TEXT,
                        changed_by TEXT NOT NULL,
                        changed_at TEXT NOT NULL
                    )
                """
                )
                cursor.execute("CREATE INDEX idx_spec_audit_spec ON spec_audit(spec_id)")
                logger.info("✅ Created spec_audit table")
            else:
                logger.info("✅ spec_audit table already exists")

            # Add commit_reviews table
            if "commit_reviews" not in existing_tables:
                logger.info("Creating commit_reviews table...")
                cursor.execute(
                    """
                    CREATE TABLE commit_reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        commit_sha TEXT NOT NULL,
                        spec_id TEXT,
                        branch TEXT NOT NULL DEFAULT 'roadmap',
                        description TEXT,
                        files_changed TEXT,
                        requested_by TEXT NOT NULL,
                        requested_at TEXT NOT NULL,
                        review_status TEXT NOT NULL DEFAULT 'pending',
                        reviewer TEXT,
                        claimed_at TEXT,
                        reviewed_at TEXT,
                        review_feedback TEXT,
                        related_pr TEXT,
                        FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
                    )
                """
                )
                cursor.execute("CREATE INDEX idx_reviews_status ON commit_reviews(review_status)")
                cursor.execute("CREATE INDEX idx_reviews_spec ON commit_reviews(spec_id)")
                cursor.execute("CREATE INDEX idx_reviews_sha ON commit_reviews(commit_sha)")
                logger.info("✅ Created commit_reviews table")
            else:
                logger.info("✅ commit_reviews table already exists")

            # Add review_comments table (drop and recreate if needed for schema update)
            if "review_comments" in existing_tables:
                # Check if it has the old schema (severity column)
                cursor.execute("PRAGMA table_info(review_comments)")
                columns = {row[1] for row in cursor.fetchall()}
                if "severity" in columns:
                    logger.info("Dropping old review_comments table (schema update)...")
                    cursor.execute("DROP TABLE review_comments")
                    logger.info("Creating new review_comments table...")
                else:
                    logger.info("✅ review_comments table already has correct schema")
                    # Skip recreation
                    columns = None

            if "review_comments" not in existing_tables or ("severity" in columns if columns else False):
                logger.info("Creating review_comments table...")
                cursor.execute(
                    """
                    CREATE TABLE review_comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        review_id INTEGER NOT NULL,
                        file_path TEXT NOT NULL,
                        line_number INTEGER,
                        comment_type TEXT,
                        comment TEXT NOT NULL,
                        created_by TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        resolved BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (review_id) REFERENCES commit_reviews(id) ON DELETE CASCADE
                    )
                """
                )
                cursor.execute("CREATE INDEX idx_review_comments_review ON review_comments(review_id)")
                logger.info("✅ Created review_comments table")

            # Add review_reports table
            if "review_reports" not in existing_tables:
                logger.info("Creating review_reports table...")
                cursor.execute(
                    """
                    CREATE TABLE review_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        review_id INTEGER NOT NULL,
                        report_path TEXT NOT NULL,
                        report_format TEXT NOT NULL,
                        generated_at TEXT NOT NULL,
                        FOREIGN KEY (review_id) REFERENCES commit_reviews(id) ON DELETE CASCADE
                    )
                """
                )
                cursor.execute("CREATE INDEX idx_review_reports_review ON review_reports(review_id)")
                logger.info("✅ Created review_reports table")
            else:
                logger.info("✅ review_reports table already exists")

            # Add work_sessions table
            if "work_sessions" not in existing_tables:
                logger.info("Creating work_sessions table...")
                cursor.execute(
                    """
                    CREATE TABLE work_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        work_id TEXT NOT NULL UNIQUE,
                        spec_id TEXT NOT NULL,
                        roadmap_item_id TEXT,
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
                        FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE CASCADE,
                        FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id) ON DELETE SET NULL
                    )
                """
                )
                cursor.execute("CREATE INDEX idx_work_sessions_status ON work_sessions(status)")
                cursor.execute("CREATE INDEX idx_work_sessions_spec ON work_sessions(spec_id)")
                cursor.execute("CREATE INDEX idx_work_sessions_roadmap ON work_sessions(roadmap_item_id)")
                cursor.execute("CREATE INDEX idx_work_sessions_branch ON work_sessions(branch_name)")
                cursor.execute("CREATE INDEX idx_work_sessions_claimed_at ON work_sessions(claimed_at)")
                logger.info("✅ Created work_sessions table")
            else:
                logger.info("✅ work_sessions table already exists")

            conn.commit()
            logger.info("✅ All tables created successfully")

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to create tables: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def import_technical_specs(self) -> Tuple[int, int]:
        """Import technical specs from both source databases.

        Returns:
            Tuple of (specs_from_specs_db, specs_from_unified_db)
        """
        logger.info("=" * 70)
        logger.info("Step 2: Importing technical specs")
        logger.info("=" * 70)

        conn = sqlite3.connect(self.roadmap_db)
        cursor = conn.cursor()

        specs_db_count = 0
        unified_db_count = 0

        try:
            # Import from specs.db
            if self.specs_db.exists():
                logger.info(f"Importing specs from {self.specs_db}...")
                cursor.execute(f"ATTACH DATABASE '{self.specs_db}' AS specs_db")

                # Get count
                cursor.execute("SELECT COUNT(*) FROM specs_db.technical_specs")
                total_specs = cursor.fetchone()[0]
                logger.info(f"Found {total_specs} specs in specs.db")

                # Import specs (handle duplicates with INSERT OR IGNORE)
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO technical_specs (
                        id, spec_number, title, roadmap_item_id, status, spec_type,
                        file_path, content, dependencies, estimated_hours, actual_hours,
                        updated_at, updated_by
                    )
                    SELECT
                        id, spec_number, title, roadmap_item_id, status, spec_type,
                        file_path, content, dependencies, estimated_hours, actual_hours,
                        updated_at, updated_by
                    FROM specs_db.technical_specs
                """
                )
                specs_db_count = cursor.rowcount
                logger.info(f"✅ Imported {specs_db_count} specs from specs.db")

                # Import spec audit trail
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO spec_audit (
                        spec_id, action, field_changed, old_value, new_value,
                        changed_by, changed_at
                    )
                    SELECT
                        spec_id, action, field_changed, old_value, new_value,
                        changed_by, changed_at
                    FROM specs_db.spec_audit
                """
                )
                audit_count = cursor.rowcount
                logger.info(f"✅ Imported {audit_count} spec audit records")

                try:
                    cursor.execute("DETACH DATABASE specs_db")
                except sqlite3.Error:
                    pass  # Already detached

            # Import from unified_roadmap_specs.db
            if self.unified_db.exists():
                logger.info(f"Importing specs from {self.unified_db}...")
                try:
                    cursor.execute("DETACH DATABASE unified_db")
                except sqlite3.Error:
                    pass  # Not attached yet
                cursor.execute(f"ATTACH DATABASE '{self.unified_db}' AS unified_db")

                # Get count
                cursor.execute("SELECT COUNT(*) FROM unified_db.technical_specs")
                total_specs = cursor.fetchone()[0]
                logger.info(f"Found {total_specs} specs in unified_roadmap_specs.db")

                # Import specs (INSERT OR REPLACE to handle conflicts)
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO technical_specs (
                        id, spec_number, title, roadmap_item_id, status, spec_type,
                        file_path, content, dependencies, estimated_hours, actual_hours,
                        updated_at, updated_by, started_at, phase
                    )
                    SELECT
                        id, spec_number, title, roadmap_item_id, status, spec_type,
                        file_path, content, dependencies, estimated_hours, actual_hours,
                        updated_at, updated_by, started_at, phase
                    FROM unified_db.technical_specs
                """
                )
                unified_db_count = cursor.rowcount
                logger.info(f"✅ Imported {unified_db_count} specs from unified_roadmap_specs.db")

                try:
                    cursor.execute("DETACH DATABASE unified_db")
                except sqlite3.Error:
                    pass  # Already detached

            conn.commit()

            # Verify total count
            cursor.execute("SELECT COUNT(*) FROM technical_specs")
            total = cursor.fetchone()[0]
            logger.info(f"✅ Total technical_specs in roadmap.db: {total}")

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to import specs: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

        return specs_db_count, unified_db_count

    def import_reviews_and_sessions(self) -> Tuple[int, int, int]:
        """Import commit reviews, review comments, and work sessions.

        Returns:
            Tuple of (reviews_count, comments_count, sessions_count)
        """
        logger.info("=" * 70)
        logger.info("Step 3: Importing commit reviews and work sessions")
        logger.info("=" * 70)

        if not self.unified_db.exists():
            logger.warning("unified_roadmap_specs.db not found, skipping review/session import")
            return 0, 0, 0

        conn = sqlite3.connect(self.roadmap_db)
        cursor = conn.cursor()

        reviews_count = 0
        comments_count = 0
        sessions_count = 0

        try:
            try:
                cursor.execute("DETACH DATABASE unified_db")
            except sqlite3.Error:
                pass  # Not attached yet
            cursor.execute(f"ATTACH DATABASE '{self.unified_db}' AS unified_db")

            # Import commit_reviews
            logger.info("Importing commit_reviews...")
            cursor.execute("SELECT COUNT(*) FROM unified_db.commit_reviews")
            total_reviews = cursor.fetchone()[0]
            logger.info(f"Found {total_reviews} commit reviews")

            cursor.execute(
                """
                INSERT OR IGNORE INTO commit_reviews (
                    commit_sha, spec_id, branch, description, files_changed,
                    requested_by, requested_at, review_status, reviewer,
                    claimed_at, reviewed_at, review_feedback, related_pr
                )
                SELECT
                    commit_sha, spec_id, branch, description, files_changed,
                    requested_by, requested_at, review_status, reviewer,
                    claimed_at, reviewed_at, review_feedback, related_pr
                FROM unified_db.commit_reviews
            """
            )
            reviews_count = cursor.rowcount
            logger.info(f"✅ Imported {reviews_count} commit reviews")

            # Import review_comments
            logger.info("Importing review_comments...")
            cursor.execute("SELECT COUNT(*) FROM unified_db.review_comments")
            total_comments = cursor.fetchone()[0]
            logger.info(f"Found {total_comments} review comments")

            cursor.execute(
                """
                INSERT OR IGNORE INTO review_comments (
                    review_id, file_path, line_number, comment_type,
                    comment, created_by, created_at, resolved
                )
                SELECT
                    review_id, file_path, line_number, comment_type,
                    comment, created_by, created_at, resolved
                FROM unified_db.review_comments
            """
            )
            comments_count = cursor.rowcount
            logger.info(f"✅ Imported {comments_count} review comments")

            # Import work_sessions
            logger.info("Importing work_sessions...")
            cursor.execute("SELECT COUNT(*) FROM unified_db.work_sessions")
            total_sessions = cursor.fetchone()[0]
            logger.info(f"Found {total_sessions} work sessions")

            cursor.execute(
                """
                INSERT OR IGNORE INTO work_sessions (
                    work_id, spec_id, roadmap_item_id, scope, scope_description,
                    assigned_files, branch_name, worktree_path, status,
                    claimed_by, claimed_at, started_at, completed_at,
                    commit_sha, merged_at, created_by, created_at
                )
                SELECT
                    work_id, spec_id, roadmap_item_id, scope, scope_description,
                    assigned_files, branch_name, worktree_path, status,
                    claimed_by, claimed_at, started_at, completed_at,
                    commit_sha, merged_at, created_by, created_at
                FROM unified_db.work_sessions
            """
            )
            sessions_count = cursor.rowcount
            logger.info(f"✅ Imported {sessions_count} work sessions")

            try:
                cursor.execute("DETACH DATABASE unified_db")
            except sqlite3.Error:
                pass  # Already detached
            conn.commit()

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to import reviews/sessions: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

        return reviews_count, comments_count, sessions_count

    def link_roadmap_to_specs(self) -> int:
        """Link roadmap items to technical specs by matching IDs.

        Returns:
            Number of items linked
        """
        logger.info("=" * 70)
        logger.info("Step 4: Linking roadmap items to technical specs")
        logger.info("=" * 70)

        conn = sqlite3.connect(self.roadmap_db)
        cursor = conn.cursor()

        linked_count = 0

        try:
            # Check current linkage
            cursor.execute("SELECT COUNT(*) FROM roadmap_items WHERE spec_id IS NULL")
            null_count = cursor.fetchone()[0]
            logger.info(f"Found {null_count} roadmap items with NULL spec_id")

            # Link PRIORITY items to SPEC-XXX (e.g., PRIORITY-24 → SPEC-024)
            cursor.execute(
                """
                UPDATE roadmap_items
                SET spec_id = 'SPEC-' || printf('%03d', CAST(number AS INTEGER)),
                    updated_at = datetime('now'),
                    updated_by = 'migrate_consolidate_to_roadmap_db'
                WHERE item_type = 'PRIORITY'
                AND spec_id IS NULL
                AND EXISTS (
                    SELECT 1 FROM technical_specs
                    WHERE id = 'SPEC-' || printf('%03d', CAST(roadmap_items.number AS INTEGER))
                )
            """
            )
            priority_linked = cursor.rowcount
            logger.info(f"✅ Linked {priority_linked} PRIORITY items to specs")

            # Link US items (e.g., US-062 → SPEC-062)
            cursor.execute(
                """
                UPDATE roadmap_items
                SET spec_id = 'SPEC-' || number,
                    updated_at = datetime('now'),
                    updated_by = 'migrate_consolidate_to_roadmap_db'
                WHERE item_type = 'US'
                AND spec_id IS NULL
                AND EXISTS (
                    SELECT 1 FROM technical_specs
                    WHERE id = 'SPEC-' || roadmap_items.number
                )
            """
            )
            us_linked = cursor.rowcount
            logger.info(f"✅ Linked {us_linked} US items to specs")

            linked_count = priority_linked + us_linked

            # Report final status
            cursor.execute("SELECT COUNT(*) FROM roadmap_items WHERE spec_id IS NOT NULL")
            linked_total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM roadmap_items WHERE spec_id IS NULL")
            unlinked_total = cursor.fetchone()[0]

            logger.info(f"✅ Total items with specs: {linked_total}")
            logger.info(f"⚠️  Total items without specs: {unlinked_total}")

            conn.commit()

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to link roadmap items: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

        return linked_count

    def verify_integrity(self) -> bool:
        """Verify data integrity after migration.

        Returns:
            True if verification passed
        """
        logger.info("=" * 70)
        logger.info("Step 5: Verifying data integrity")
        logger.info("=" * 70)

        conn = sqlite3.connect(self.roadmap_db)
        cursor = conn.cursor()

        try:
            # Enable foreign key checking
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA foreign_key_check")
            fk_errors = cursor.fetchall()

            if fk_errors:
                logger.error(f"❌ Foreign key errors found: {fk_errors}")
                return False
            else:
                logger.info("✅ No foreign key errors")

            # Verify table counts
            tables = [
                "roadmap_items",
                "technical_specs",
                "commit_reviews",
                "work_sessions",
                "spec_audit",
            ]

            logger.info("\nTable row counts:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"  {table}: {count} rows")

            # Check spec linkage
            cursor.execute(
                """
                SELECT COUNT(*) FROM roadmap_items r
                WHERE r.spec_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM technical_specs s WHERE s.id = r.spec_id
                )
            """
            )
            orphaned = cursor.fetchone()[0]
            if orphaned > 0:
                logger.warning(f"⚠️  {orphaned} roadmap items have invalid spec_id references")
            else:
                logger.info("✅ All spec_id references are valid")

            logger.info("✅ Data integrity verification passed")
            return True

        except sqlite3.Error as e:
            logger.error(f"❌ Integrity check failed: {e}")
            return False
        finally:
            conn.close()

    def run(self) -> bool:
        """Run the complete consolidation process.

        Returns:
            True if successful
        """
        try:
            logger.info("🚀 Starting database consolidation to data/roadmap.db")
            logger.info("")

            # Step 1: Add missing tables
            self.add_missing_tables()

            # Step 2: Import technical specs
            specs_db_count, unified_db_count = self.import_technical_specs()

            # Step 3: Import reviews and sessions
            reviews, comments, sessions = self.import_reviews_and_sessions()

            # Step 4: Link roadmap items to specs
            linked = self.link_roadmap_to_specs()

            # Step 5: Verify integrity
            if not self.verify_integrity():
                logger.error("❌ Integrity verification failed")
                return False

            # Summary
            logger.info("")
            logger.info("=" * 70)
            logger.info("✅ CONSOLIDATION COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Technical specs imported: {specs_db_count + unified_db_count}")
            logger.info(f"  - From specs.db: {specs_db_count}")
            logger.info(f"  - From unified_roadmap_specs.db: {unified_db_count}")
            logger.info(f"Commit reviews imported: {reviews}")
            logger.info(f"Review comments imported: {comments}")
            logger.info(f"Work sessions imported: {sessions}")
            logger.info(f"Roadmap items linked to specs: {linked}")
            logger.info("")
            logger.info("✅ All data successfully consolidated into data/roadmap.db")

            return True

        except Exception as e:
            logger.error(f"❌ Consolidation failed: {e}")
            return False


if __name__ == "__main__":
    consolidator = DatabaseConsolidator()
    success = consolidator.run()

    if success:
        logger.info("\n🎉 Database consolidation completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update code paths to use data/roadmap.db")
        logger.info("2. Test all agents (project_manager, architect, code_developer, code_reviewer)")
        logger.info("3. Archive deprecated databases (specs.db, unified_roadmap_specs.db)")
        sys.exit(0)
    else:
        logger.error("\n❌ Database consolidation failed")
        logger.error("Check logs above for details")
        sys.exit(1)
