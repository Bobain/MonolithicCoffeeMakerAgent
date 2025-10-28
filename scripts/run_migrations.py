#!/usr/bin/env python3
"""Run database migrations.

Usage:
    poetry run python scripts/run_migrations.py
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / "data" / "migrations"
DB_PATH = PROJECT_ROOT / "data" / "development.db"


def run_migrations():
    """Run all pending migrations."""
    # Ensure database exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create migrations table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()

    # Get list of applied migrations
    cursor.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}

    # Get all migration files
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        logger.info("No migration files found")
        return

    # Apply pending migrations
    pending_count = 0
    for migration_file in migration_files:
        if migration_file.name in applied:
            logger.debug(f"✓ {migration_file.name} (already applied)")
            continue

        logger.info(f"Applying migration: {migration_file.name}")

        # Read and execute migration
        with open(migration_file, "r") as f:
            sql = f.read()

        try:
            cursor.executescript(sql)
            conn.commit()

            # Record migration
            cursor.execute("INSERT INTO migrations (name) VALUES (?)", (migration_file.name,))
            conn.commit()

            logger.info(f"✅ {migration_file.name} applied successfully")
            pending_count += 1

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to apply {migration_file.name}: {e}")
            conn.rollback()
            raise

    conn.close()

    if pending_count == 0:
        logger.info("✅ All migrations up to date")
    else:
        logger.info(f"✅ Applied {pending_count} migration(s)")


if __name__ == "__main__":
    run_migrations()
