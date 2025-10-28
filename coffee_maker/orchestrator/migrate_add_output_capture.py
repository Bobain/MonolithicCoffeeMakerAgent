"""Migration script to add stdout_output and stderr_output columns to agent_lifecycle table.

This migration enables proper output capture for spawned agents, allowing
the orchestrator to debug failures and track agent behavior.

Usage:
    poetry run python coffee_maker/orchestrator/migrate_add_output_capture.py

Author: claude-code
Date: 2025-10-21
Related: architect/code_reviewer failure debugging
"""

import logging
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class OutputCaptureMigration:
    """Add output capture columns to agent_lifecycle table."""

    def __init__(self, db_path: str = "data/orchestrator.db"):
        """
        Initialize migration.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)

        # Ensure database exists
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}. " f"Run migrate_add_agent_lifecycle.py first."
            )

    def run(self) -> bool:
        """
        Run migration.

        Returns:
            True if successful
        """
        try:
            logger.info("Starting output capture migration...")

            # Add columns
            self._add_output_columns()

            # Verify migration
            self._verify_migration()

            logger.info("✅ Migration completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}", exc_info=True)
            return False

    def _add_output_columns(self):
        """Add stdout_output and stderr_output columns."""
        logger.info("Adding output capture columns...")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check existing columns
            cursor.execute("PRAGMA table_info(agent_lifecycle)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            columns_to_add = [
                ("stdout_output", "TEXT"),
                ("stderr_output", "TEXT"),
            ]

            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    logger.info(f"Adding column: {col_name} ({col_type})")
                    cursor.execute(f"ALTER TABLE agent_lifecycle ADD COLUMN {col_name} {col_type}")
                else:
                    logger.info(f"Column {col_name} already exists, skipping")

            conn.commit()

        logger.info("✅ Output capture columns added")

    def _verify_migration(self):
        """Verify migration was successful."""
        logger.info("Verifying migration...")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check columns exist
            cursor.execute("PRAGMA table_info(agent_lifecycle)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            required_columns = ["stdout_output", "stderr_output"]
            for col_name in required_columns:
                if col_name not in existing_columns:
                    raise RuntimeError(f"Column {col_name} not found!")

            logger.info(f"✅ Verification passed:")
            logger.info(f"   - stdout_output column: EXISTS")
            logger.info(f"   - stderr_output column: EXISTS")


def main():
    """Main entry point."""
    migration = OutputCaptureMigration()
    success = migration.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
