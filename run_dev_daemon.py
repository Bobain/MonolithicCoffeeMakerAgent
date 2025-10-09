#!/usr/bin/env python3
"""Launcher script for the autonomous development daemon.

This script starts the DevDaemon which continuously:
1. Reads ROADMAP.md for next planned priority
2. Requests user approval (if not auto-approved)
3. Executes Claude CLI to implement the priority
4. Commits, pushes, and creates PR
5. Updates ROADMAP.md status
6. Repeats until all priorities complete

Usage:
    python run_dev_daemon.py              # Manual approval mode
    python run_dev_daemon.py --auto       # Auto-approve mode (dangerous!)
    python run_dev_daemon.py --no-pr      # Skip PR creation
    python run_dev_daemon.py --sleep 60   # Set sleep interval to 60s

Example:
    # Start daemon in safe mode (asks for approval)
    python run_dev_daemon.py

    # Monitor notifications in another terminal
    project-manager notifications

    # Approve a task when prompted
    project-manager respond <notif_id> approve
"""

import argparse
import logging
import sys
from pathlib import Path

from coffee_maker.autonomous.daemon import DevDaemon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("dev_daemon.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Run the autonomous development daemon."""
    parser = argparse.ArgumentParser(
        description="Autonomous Development Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Start daemon (manual approval)
  %(prog)s --auto             Start daemon (auto-approve - use with caution!)
  %(prog)s --no-pr            Skip PR creation
  %(prog)s --sleep 60         Sleep 60s between iterations
  %(prog)s --model sonnet-4   Use specific Claude model

Safety:
  By default, the daemon will ask for approval before implementing each priority.
  You can monitor and respond to approval requests using:
    project-manager notifications
    project-manager respond <notif_id> approve

  Use --auto mode only if you trust the daemon to make all decisions autonomously.
        """,
    )

    parser.add_argument(
        "--roadmap",
        default="docs/ROADMAP.md",
        help="Path to ROADMAP.md (default: docs/ROADMAP.md)",
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-approve implementations (DANGEROUS - skips user confirmation)",
    )

    parser.add_argument(
        "--no-pr",
        action="store_true",
        help="Skip PR creation (only commit and push)",
    )

    parser.add_argument(
        "--sleep",
        type=int,
        default=30,
        help="Seconds to sleep between iterations (default: 30)",
    )

    parser.add_argument(
        "--model",
        default="claude-sonnet-4",
        help="Claude model to use (default: claude-sonnet-4)",
    )

    args = parser.parse_args()

    # Validate roadmap exists
    roadmap_path = Path(args.roadmap)
    if not roadmap_path.exists():
        logger.error(f"ROADMAP not found: {args.roadmap}")
        sys.exit(1)

    # Warn if auto-approve enabled
    if args.auto:
        logger.warning("⚠️  AUTO-APPROVE MODE ENABLED!")
        logger.warning("⚠️  The daemon will implement priorities WITHOUT asking for approval!")
        logger.warning("⚠️  Press Ctrl+C within 5 seconds to cancel...")
        import time

        time.sleep(5)

    # Create and start daemon
    logger.info("Starting DevDaemon...")
    logger.info(f"Roadmap: {args.roadmap}")
    logger.info(f"Auto-approve: {args.auto}")
    logger.info(f"Create PRs: {not args.no_pr}")
    logger.info(f"Sleep interval: {args.sleep}s")
    logger.info(f"Model: {args.model}")

    daemon = DevDaemon(
        roadmap_path=args.roadmap,
        auto_approve=args.auto,
        create_prs=not args.no_pr,
        sleep_interval=args.sleep,
        model=args.model,
    )

    try:
        daemon.run()
    except KeyboardInterrupt:
        logger.info("\n⏹️  Daemon stopped by user (Ctrl+C)")
    except Exception as e:
        logger.exception(f"❌ Fatal error in daemon: {e}")
        sys.exit(1)

    logger.info("👋 Daemon exited cleanly")


if __name__ == "__main__":
    main()
