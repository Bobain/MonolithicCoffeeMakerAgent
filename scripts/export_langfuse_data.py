#!/usr/bin/env python3
"""Export Langfuse traces to local database.

This script exports traces from Langfuse cloud to a local SQLite or PostgreSQL
database for offline analysis, reporting, and visualization.

Usage:
    # Export last 24 hours to SQLite (default)
    python scripts/export_langfuse_data.py

    # Export last 7 days
    python scripts/export_langfuse_data.py --lookback-hours 168

    # Export to PostgreSQL
    export DB_TYPE=postgresql
    export POSTGRES_USER=llm_user
    export POSTGRES_PASSWORD=secret
    python scripts/export_langfuse_data.py

    # Continuous export every 30 minutes
    python scripts/export_langfuse_data.py --continuous --interval 30

Example:
    >>> python scripts/export_langfuse_data.py --lookback-hours 24
    Exporting traces from 2025-01-08 to 2025-01-09...
    ✅ Exported 150 traces with 450 generations
    ✅ Total cost: $12.34
    ✅ Average latency: 1234ms
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.langchain_observe.analytics.config import ExportConfig
from coffee_maker.langchain_observe.analytics.exporter_sqlite import LangfuseExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Run Langfuse data export."""
    parser = argparse.ArgumentParser(
        description="Export Langfuse traces to local database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export last 24 hours (default)
  python scripts/export_langfuse_data.py

  # Export last 7 days
  python scripts/export_langfuse_data.py --lookback-hours 168

  # Continuous export every 30 minutes
  python scripts/export_langfuse_data.py --continuous --interval 30

  # Use PostgreSQL
  export DB_TYPE=postgresql
  export POSTGRES_USER=llm_user
  export POSTGRES_PASSWORD=secret
  python scripts/export_langfuse_data.py

Environment Variables:
  LANGFUSE_PUBLIC_KEY    Langfuse public API key (required)
  LANGFUSE_SECRET_KEY    Langfuse secret API key (required)
  LANGFUSE_HOST          Langfuse host URL (default: https://cloud.langfuse.com)
  DB_TYPE                Database type: sqlite or postgresql (default: sqlite)
  SQLITE_PATH            SQLite database path (default: llm_metrics.db)
  POSTGRES_HOST          PostgreSQL host
  POSTGRES_PORT          PostgreSQL port
  POSTGRES_DATABASE      PostgreSQL database name
  POSTGRES_USER          PostgreSQL username
  POSTGRES_PASSWORD      PostgreSQL password
        """,
    )

    parser.add_argument(
        "--lookback-hours",
        type=int,
        help="Hours to look back for traces (default: 24)",
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuous export in daemon mode",
    )

    parser.add_argument(
        "--interval",
        type=int,
        help="Export interval in minutes for continuous mode (default: 30)",
    )

    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Setup database schema before exporting",
    )

    args = parser.parse_args()

    try:
        # Load configuration from environment
        logger.info("Loading configuration from environment...")
        config = ExportConfig.from_env()

        # Override lookback hours if provided
        if args.lookback_hours:
            config.lookback_hours = args.lookback_hours

        # Override interval if provided
        if args.interval:
            config.export_interval_minutes = args.interval

        logger.info(f"Database: {config.db_url}")
        logger.info(f"Langfuse host: {config.langfuse_host}")

        # Create exporter
        exporter = LangfuseExporter(config)

        # Setup database if requested
        if args.setup_db:
            logger.info("Setting up database schema...")
            exporter.setup_database()
            logger.info("✅ Database schema ready")

        # Run export
        if args.continuous:
            logger.info(f"Starting continuous export (interval: {config.export_interval_minutes} minutes)")
            logger.info("Press Ctrl+C to stop")
            exporter.start_continuous_export()
        else:
            logger.info(f"Exporting traces (lookback: {config.lookback_hours} hours)...")
            stats = exporter.export_traces()

            # Print results
            print("\n" + "=" * 60)
            print("✅ Export Complete")
            print("=" * 60)
            print(f"\nTraces exported: {stats['traces']}")
            print(f"Generations exported: {stats['generations']}")
            print(f"Spans exported: {stats['spans']}")
            if stats["errors"] > 0:
                print(f"⚠️  Errors encountered: {stats['errors']}")
            print("\nNext steps:")
            print("  - Analyze performance: python scripts/analyze_performance.py")
            print(f"  - Query database: sqlite3 {config.sqlite_path if config.db_type == 'sqlite' else 'llm_metrics'}")
            print("  - View dashboard: python scripts/run_metrics_dashboard.py")

    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("\nMake sure you have set the required environment variables:")
        logger.error("  LANGFUSE_PUBLIC_KEY")
        logger.error("  LANGFUSE_SECRET_KEY")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n✅ Export stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
