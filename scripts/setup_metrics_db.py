#!/usr/bin/env python3
"""Setup LLM metrics database.

This script creates the database schema for storing LLM analytics data.
Supports both SQLite (default) and PostgreSQL.

Usage:
    # Setup SQLite database (default)
    python scripts/setup_metrics_db.py

    # Setup with custom SQLite path
    python scripts/setup_metrics_db.py --db-path my_metrics.db

    # Setup PostgreSQL database
    export DB_TYPE=postgresql
    export POSTGRES_USER=llm_user
    export POSTGRES_PASSWORD=secret
    python scripts/setup_metrics_db.py

Example:
    >>> python scripts/setup_metrics_db.py
    Creating database schema...
    Database type: sqlite
    Database path: llm_metrics.db
    ✅ Created table: llm_generations
    ✅ Created table: llm_traces
    ✅ Created table: llm_events
    ✅ Created table: rate_limit_counters
    ✅ Created table: scheduled_requests
    ✅ Created table: agent_task_results
    ✅ Created table: prompt_variants
    ✅ Created table: prompt_executions
    ✅ Created table: export_metadata
    ✅ SQLite WAL mode enabled
    ✅ Database setup complete!
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, inspect

from coffee_maker.langchain_observe.analytics.db_schema import (
    Base,
    enable_sqlite_wal,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def get_database_url(args) -> tuple[str, str]:
    """Get database URL from args or environment.

    Args:
        args: Parsed command-line arguments

    Returns:
        Tuple of (db_type, db_url)
    """
    db_type = os.getenv("DB_TYPE", "sqlite")

    if db_type == "sqlite":
        db_path = args.db_path or os.getenv("SQLITE_PATH", "llm_metrics.db")
        db_url = f"sqlite:///{db_path}"
        return "sqlite", db_url

    elif db_type == "postgresql":
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DATABASE", "llm_metrics")

        if not user or not password:
            raise ValueError("POSTGRES_USER and POSTGRES_PASSWORD must be set for PostgreSQL")

        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        return "postgresql", db_url

    else:
        raise ValueError(f"Unsupported DB_TYPE: {db_type}")


def setup_database(db_url: str, db_type: str, enable_wal: bool = True):
    """Create database schema.

    Args:
        db_url: SQLAlchemy database URL
        db_type: Database type ("sqlite" or "postgresql")
        enable_wal: Whether to enable WAL mode for SQLite (default: True)
    """
    logger.info("Creating database schema...")
    logger.info(f"Database type: {db_type}")
    logger.info(f"Database URL: {db_url.split('@')[0]}...")  # Hide password

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    logger.info(f"Created {len(tables)} tables:")
    for table in tables:
        logger.info(f"  ✅ {table}")

    # Enable SQLite WAL mode for better concurrency
    if db_type == "sqlite" and enable_wal:
        logger.info("Enabling SQLite WAL mode...")
        enable_sqlite_wal(engine)
        logger.info("  ✅ WAL mode enabled (multi-process safe)")

    logger.info("✅ Database setup complete!")

    return engine


def verify_database(engine):
    """Verify database is accessible and has correct schema.

    Args:
        engine: SQLAlchemy engine instance
    """
    logger.info("Verifying database...")

    inspector = inspect(engine)
    expected_tables = {
        "llm_generations",
        "llm_traces",
        "llm_events",
        "rate_limit_counters",
        "scheduled_requests",
        "agent_task_results",
        "prompt_variants",
        "prompt_executions",
        "export_metadata",
    }

    actual_tables = set(inspector.get_table_names())

    missing = expected_tables - actual_tables
    if missing:
        logger.warning(f"⚠️  Missing tables: {missing}")
        return False

    logger.info("✅ All expected tables present")

    # Verify key tables have correct columns
    for table in ["llm_generations", "llm_traces", "rate_limit_counters"]:
        columns = {col["name"] for col in inspector.get_columns(table)}
        logger.info(f"  ✅ {table}: {len(columns)} columns")

    return True


def main():
    """Run database setup."""
    parser = argparse.ArgumentParser(
        description="Setup LLM metrics database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup SQLite database (default)
  python scripts/setup_metrics_db.py

  # Custom SQLite path
  python scripts/setup_metrics_db.py --db-path /tmp/metrics.db

  # PostgreSQL
  export DB_TYPE=postgresql
  export POSTGRES_USER=llm_user
  export POSTGRES_PASSWORD=secret
  python scripts/setup_metrics_db.py

  # Disable WAL mode
  python scripts/setup_metrics_db.py --no-wal
        """,
    )

    parser.add_argument(
        "--db-path",
        type=str,
        help="SQLite database path (default: llm_metrics.db)",
    )

    parser.add_argument(
        "--no-wal",
        action="store_true",
        help="Disable WAL mode for SQLite",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify database schema after creation",
    )

    args = parser.parse_args()

    try:
        # Get database URL
        db_type, db_url = get_database_url(args)

        # Setup database
        engine = setup_database(db_url, db_type, enable_wal=not args.no_wal)

        # Verify if requested
        if args.verify:
            verify_database(engine)

        # Print summary
        print("\n" + "=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        if db_type == "sqlite":
            db_path = args.db_path or "llm_metrics.db"
            print(f"\nDatabase location: {Path(db_path).absolute()}")
            print("\nYou can now:")
            print(f"  - View data: sqlite3 {db_path}")
            print("  - Export Langfuse data: python scripts/export_langfuse_data.py")
            print("  - Run queries: See docs/langfuse_to_postgresql_export_plan.md")
        else:
            print("\nPostgreSQL database ready")
            print("You can now:")
            print("  - Export Langfuse data: python scripts/export_langfuse_data.py")
            print("  - Connect with: psql -h localhost -U $POSTGRES_USER -d llm_metrics")

    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
