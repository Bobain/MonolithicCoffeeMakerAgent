#!/usr/bin/env python3
"""Quick-start script for running the code-developer daemon.

⚠️  IMPORTANT: Run this daemon from a SEPARATE TERMINAL, NOT from within Claude Code!

The daemon spawns Claude CLI sessions to implement features. Running it from
within an existing Claude Code session will cause it to hang due to nested
session conflicts.

CORRECT USAGE:
1. Open a NEW terminal (separate from Claude Code)
2. Activate the poetry environment
3. Run this script

WRONG USAGE:
❌ Running from within Claude Code terminal
❌ Running while Claude Code is using the same working directory

This is a temporary convenience script until PRIORITY 3 (PyPI Package & Binaries)
is complete and the proper `code-developer` CLI command is available.

Usage:
    python run_daemon.py                    # Interactive mode (asks for approval)
    python run_daemon.py --auto-approve     # Auto-approve mode (autonomous)
    python run_daemon.py --help             # Show help
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from coffee_maker.autonomous.daemon import DevDaemon


def check_claude_session():
    """Check if running inside a Claude Code session and warn user.

    Returns:
        bool: True if likely running inside Claude session
    """
    import os
    import subprocess

    # Check for Claude-specific environment variables
    claude_env_vars = [
        "CLAUDE_SESSION_ID",
        "CLAUDE_CLI_SESSION",
    ]

    for var in claude_env_vars:
        if os.environ.get(var):
            return True

    # Check if 'claude' process is running
    try:
        result = subprocess.run(["pgrep", "-f", "claude"], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except:
        pass

    return False


def main():
    """Run the code-developer daemon."""
    parser = argparse.ArgumentParser(
        description="Code Developer Daemon - Autonomous development agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_daemon.py                    # Interactive mode
  python run_daemon.py --auto-approve     # Autonomous mode
  python run_daemon.py --no-pr            # Skip PR creation

Note: This is a temporary script. After PRIORITY 3 is complete,
      use the `code-developer` command instead.
        """,
    )

    parser.add_argument(
        "--roadmap",
        default="docs/ROADMAP.md",
        help="Path to ROADMAP.md (default: docs/ROADMAP.md)",
    )

    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Auto-approve implementation without asking (autonomous mode)",
    )

    parser.add_argument(
        "--no-pr",
        action="store_true",
        help="Skip creating pull requests",
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

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose logging output",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Check if running inside Claude session
    if check_claude_session():
        print("=" * 70)
        print("⚠️  WARNING: Claude Code session detected!")
        print("=" * 70)
        print("\n⚠️  Running the daemon from within Claude Code will cause it to HANG!")
        print("\nThe daemon needs to spawn Claude CLI sessions, which conflicts with")
        print("running inside an existing Claude Code session.")
        print("\n🔧 SOLUTION:")
        print("  1. Exit this Claude Code session (type 'exit' or press Ctrl+D)")
        print("  2. Open a NEW terminal (completely separate)")
        print("  3. Activate poetry environment:")
        print("     source /Users/bobain/Library/Caches/pypoetry/virtualenvs/coffee-maker-efk4LJvC-py3.11/bin/activate")
        print("  4. Run daemon again from the new terminal")
        print("\n" + "=" * 70)

        response = input("\n⚠️  Continue anyway? (NOT recommended) [y/N]: ").strip().lower()
        if response not in ["y", "yes"]:
            print("\n✅ Good choice! Exiting safely.")
            print("Please run this daemon from a separate terminal.\n")
            sys.exit(0)
        else:
            print("\n⚠️  Proceeding... (expect the daemon to hang)\n")

    # Create and run daemon
    print("=" * 70)
    print("🤖 Code Developer Daemon - Quick Start")
    print("=" * 70)
    print(f"Roadmap: {args.roadmap}")
    print(f"Mode: {'Autonomous (auto-approve)' if args.auto_approve else 'Interactive (requires approval)'}")
    print(f"PRs: {'Disabled' if args.no_pr else 'Enabled'}")
    print(f"Model: {args.model}")
    print("=" * 70)
    print("\nStarting daemon... (Press Ctrl+C to stop)\n")

    try:
        daemon = DevDaemon(
            roadmap_path=args.roadmap,
            auto_approve=args.auto_approve,
            create_prs=not args.no_pr,
            sleep_interval=args.sleep,
            model=args.model,
        )

        daemon.run()

    except KeyboardInterrupt:
        print("\n\n⏹️  Daemon stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
