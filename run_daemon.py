#!/usr/bin/env python3
"""Quick-start script for running the code-developer daemon.

The daemon uses the Anthropic API to autonomously implement features from your
ROADMAP.md file.

REQUIREMENTS:
1. ANTHROPIC_API_KEY environment variable must be set
2. Poetry environment must be activated

RECOMMENDED:
- Run from a separate terminal (not from within Claude Code)
- This provides better isolation and debugging

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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, env vars must be set manually

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.config import ConfigManager


def check_claude_session():
    """Check if running inside a Claude Code session and warn user.

    Returns:
        bool: True if running inside Claude Code terminal session
    """
    import os

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
  python run_daemon.py                    # Interactive mode
  python run_daemon.py --auto-approve     # Autonomous mode
  python run_daemon.py --no-pr            # Skip PR creation

Note: This is a temporary script. After PRIORITY 3 is complete,
      use the `code-developer` command instead.
        """,
    )

    parser.add_argument(
        "--roadmap",
        default="docs/roadmap/ROADMAP.md",
        help="Path to ROADMAP.md (default: docs/roadmap/ROADMAP.md)",
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
        default="sonnet",
        help="Claude model to use (default: sonnet; options: sonnet, opus, haiku)",
    )

    parser.add_argument(
        "--use-cli",
        action="store_true",
        help="Force use of Claude CLI (default: auto-detect, prefers CLI)",
    )

    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Force use of Anthropic API (default: auto-detect, prefers CLI)",
    )

    parser.add_argument(
        "--claude-path",
        default="/opt/homebrew/bin/claude",
        help="Path to claude CLI executable (default: /opt/homebrew/bin/claude)",
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

    # Auto-detect mode: CLI vs API
    import os
    import shutil

    # Check for conflicting flags
    if args.use_cli and args.use_api:
        print("=" * 70)
        print("❌ ERROR: Cannot use both --use-cli and --use-api")
        print("=" * 70)
        print("\nPlease choose one:")
        print("  --use-cli   → Force Claude CLI mode")
        print("  --use-api   → Force Anthropic API mode")
        print("  (no flags)  → Auto-detect (prefers CLI)")
        print("=" * 70 + "\n")
        sys.exit(1)

    # Explicit flags take precedence
    if args.use_cli:
        use_claude_cli = True
    elif args.use_api:
        use_claude_cli = False
    else:
        # Auto-detect: PREFER CLI as default (it's free and subscription-based)
        # Only use API if explicitly configured (--use-api flag or CLI not available)
        has_cli = shutil.which("claude") or os.path.exists(args.claude_path)
        has_api_key = ConfigManager.has_anthropic_api_key()

        if has_cli:
            # CLI available - use it as default
            print("=" * 70)
            print("ℹ️  Auto-detected: Using Claude CLI (default)")
            print("=" * 70)
            print("💡 TIP: Claude CLI is free with your subscription!")
            print("    To use API mode instead: unset ANTHROPIC_API_KEY or use --use-api")
            print("=" * 70 + "\n")
            use_claude_cli = True
        elif has_api_key:
            # No CLI but has API key - use API
            print("=" * 70)
            print("ℹ️  Auto-detected: Using Anthropic API (no CLI found)")
            print("=" * 70)
            print("💡 TIP: Install Claude CLI for free usage!")
            print("    Get it from: https://claude.ai/")
            print("=" * 70 + "\n")
            use_claude_cli = False
        else:
            # Neither available - error
            print("=" * 70)
            print("❌ ERROR: No Claude access available!")
            print("=" * 70)
            print("\nThe daemon requires either:")
            print("  1. Claude CLI installed (recommended - free with subscription), OR")
            print("  2. Anthropic API key (requires credits)")
            print("\n🔧 SOLUTION 1 (CLI Mode - Recommended):")
            print("  1. Install Claude CLI from: https://claude.ai/")
            print("  2. Run: python run_daemon.py")
            print("\n🔧 SOLUTION 2 (API Mode):")
            print("  1. Get your API key from: https://console.anthropic.com/")
            print("  2. Set the environment variable:")
            print("     export ANTHROPIC_API_KEY='your-api-key-here'")
            print("  3. Run: python run_daemon.py")
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
    print("🤖 Code Developer Daemon - Quick Start")
    print("=" * 70)
    print(f"Roadmap: {args.roadmap}")
    print(f"Mode: {'Autonomous (auto-approve)' if args.auto_approve else 'Interactive (requires approval)'}")
    print(f"PRs: {'Disabled' if args.no_pr else 'Enabled'}")
    print(f"Model: {args.model}")
    print(f"Claude: {'CLI' if use_claude_cli else 'API'}")
    print("=" * 70)
    print("\nStarting daemon... (Press Ctrl+C to stop)\n")

    try:
        daemon = DevDaemon(
            roadmap_path=args.roadmap,
            auto_approve=args.auto_approve,
            create_prs=not args.no_pr,
            sleep_interval=args.sleep,
            model=args.model,
            use_claude_cli=use_claude_cli,
            claude_cli_path=args.claude_path,
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
