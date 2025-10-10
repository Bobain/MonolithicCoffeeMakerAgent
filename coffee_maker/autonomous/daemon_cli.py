"""Code Developer Daemon CLI.

This module provides the command-line interface for the code-developer daemon.

Usage:
    code-developer                      # Interactive mode (asks for approval)
    code-developer --auto-approve       # Auto-approve mode (autonomous)
    code-developer --help               # Show help
"""

import argparse
import logging
import os
import sys

from coffee_maker.autonomous.daemon import DevDaemon


def check_claude_session():
    """Check if running inside a Claude Code session and warn user.

    Returns:
        bool: True if running inside Claude Code terminal session
    """
    # Check for ACTUAL Claude Code environment variables
    # These are set when running inside a Claude Code terminal session
    claude_env_vars = [
        "CLAUDECODE",  # Set to "1" when inside Claude Code
        "CLAUDE_CODE_ENTRYPOINT",  # Set to "cli" when using Claude Code CLI
    ]

    for var in claude_env_vars:
        if os.environ.get(var):
            return True

    # NOTE: We do NOT check for running processes with pgrep
    # because that's too broad - it matches any Claude process anywhere,
    # not just the terminal session we're running in.
    # Only environment variables reliably indicate we're INSIDE a session.

    return False


def main():
    """Run the code-developer daemon."""
    parser = argparse.ArgumentParser(
        description="Code Developer Daemon - Autonomous development agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  code-developer                      # Interactive mode
  code-developer --auto-approve       # Autonomous mode
  code-developer --no-pr              # Skip PR creation

The daemon reads your ROADMAP.md file and autonomously implements features
using the Anthropic API (Claude).
        """,
    )

    parser.add_argument("--roadmap", default="docs/ROADMAP.md", help="Path to ROADMAP.md (default: docs/ROADMAP.md)")

    parser.add_argument(
        "--auto-approve", action="store_true", help="Auto-approve implementation without asking (autonomous mode)"
    )

    parser.add_argument("--no-pr", action="store_true", help="Skip creating pull requests")

    parser.add_argument("--sleep", type=int, default=30, help="Seconds to sleep between iterations (default: 30)")

    parser.add_argument("--model", default="claude-sonnet-4", help="Claude model to use (default: claude-sonnet-4)")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging output")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Check for required environment variables
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("=" * 70)
        print("❌ ERROR: ANTHROPIC_API_KEY not set!")
        print("=" * 70)
        print("\nThe daemon requires an Anthropic API key to function.")
        print("\n🔧 SOLUTION:")
        print("  1. Get your API key from: https://console.anthropic.com/")
        print("  2. Set the environment variable:")
        print("     export ANTHROPIC_API_KEY='your-api-key-here'")
        print("  3. Run the daemon again")
        print("\n" + "=" * 70 + "\n")
        sys.exit(1)

    # Check if running inside Claude session (warning only, not blocking)
    if check_claude_session():
        print("=" * 70)
        print("⚠️  INFO: Running inside Claude Code session")
        print("=" * 70)
        print("\nYou're running the daemon from within Claude Code.")
        print("This works fine now (we use the Anthropic SDK directly),")
        print("but running from a separate terminal provides better isolation.")
        print("\n💡 TIP: For better debugging, run from a separate terminal.")
        print("=" * 70 + "\n")

    # Create and run daemon
    print("=" * 70)
    print("🤖 Code Developer Daemon")
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
