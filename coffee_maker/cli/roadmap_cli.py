"""Project Manager CLI - Roadmap management tool.

This module provides a command-line interface for managing ROADMAP.md
and viewing daemon status.

MVP Phase 1 (Current):
    - View roadmap
    - Check daemon status
    - View notifications
    - Respond to daemon questions
    - Basic text output

Phase 2 (Future):
    - Claude AI integration
    - Rich terminal UI
    - Roadmap editing
    - Slack integration

Commands:
    project-manager view [priority]      View roadmap (or specific priority)
    project-manager status                Show daemon status
    project-manager notifications        List pending notifications
    project-manager respond <id> <msg>   Respond to notification
    project-manager sync                  Sync with daemon environment

Example:
    # View full roadmap
    $ project-manager view

    # View specific priority
    $ project-manager view PRIORITY-1

    # Check notifications
    $ project-manager notifications

    # Respond to question
    $ project-manager respond 5 approve
"""

import argparse
import logging
import sys

from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_PRIORITY_HIGH,
    NOTIF_STATUS_PENDING,
    NotificationDB,
)
from coffee_maker.config import ROADMAP_PATH

# Configure logging BEFORE imports that might fail
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Import chat components for Phase 2
try:
    from coffee_maker.cli.ai_service import AIService
    from coffee_maker.cli.chat_interface import ChatSession
    from coffee_maker.cli.roadmap_editor import RoadmapEditor

    # Import all command handlers to register them
    from coffee_maker.cli.commands import all_commands  # noqa: F401

    CHAT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chat features not available: {e}")
    CHAT_AVAILABLE = False


def cmd_view(args):
    """View roadmap or specific priority.

    Args:
        args: Parsed command-line arguments with priority field
    """
    if not ROADMAP_PATH.exists():
        print(f"❌ ROADMAP not found: {ROADMAP_PATH}")
        return 1

    print("\n" + "=" * 80)
    print("Coffee Maker Agent - ROADMAP")
    print("=" * 80 + "\n")

    with open(ROADMAP_PATH, "r") as f:
        content = f.read()

    if args.priority:
        # Show specific priority
        priority_name = args.priority.upper()
        if not priority_name.startswith("PRIORITY"):
            priority_name = f"PRIORITY {priority_name}"

        lines = content.split("\n")
        in_priority = False
        priority_lines = []

        for line in lines:
            if priority_name in line and line.startswith("###"):
                in_priority = True
                priority_lines.append(line)
            elif in_priority:
                if line.startswith("###") and "PRIORITY" in line:
                    # Next priority section started
                    break
                priority_lines.append(line)

        if priority_lines:
            print("\n".join(priority_lines))
        else:
            print(f"❌ {priority_name} not found in ROADMAP")
            return 1

    else:
        # Show full roadmap (first 100 lines for MVP)
        lines = content.split("\n")
        print("\n".join(lines[:100]))

        if len(lines) > 100:
            print(f"\n... ({len(lines) - 100} more lines)")
            print("\nTip: Use 'project-manager view <priority>' to see specific priority")

    return 0


def cmd_status(args):
    """Show daemon status.

    PRIORITY 2.8: Daemon Status Reporting

    Reads ~/.coffee_maker/daemon_status.json and displays current daemon status.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager status

        Daemon Status: Running
        PID: 12345
        Started: 2025-10-11 10:30:00
        Current Priority: PRIORITY 2.8 - Daemon Status Reporting
        Iteration: 5
        Crashes: 0/3
    """
    import json
    from datetime import datetime
    from pathlib import Path

    print("\n" + "=" * 80)
    print("Code Developer Daemon Status")
    print("=" * 80 + "\n")

    # Read status file
    status_file = Path.home() / ".coffee_maker" / "daemon_status.json"

    if not status_file.exists():
        print("❌ Daemon status file not found")
        print("\nThe daemon is either:")
        print("  - Not running")
        print("  - Never been started")
        print("\n💡 Start the daemon with: poetry run code-developer")
        return 1

    try:
        with open(status_file, "r") as f:
            status = json.load(f)

        # Display daemon status
        daemon_status = status.get("status", "unknown")
        if daemon_status == "running":
            print("Status: 🟢 Running")
        elif daemon_status == "stopped":
            print("Status: 🔴 Stopped")
        else:
            print(f"Status: ⚪ {daemon_status}")

        # PID and process info
        pid = status.get("pid")
        if pid:
            print(f"PID: {pid}")

            # Check if process is actually running
            import psutil

            try:
                process = psutil.Process(pid)
                if process.is_running():
                    print(
                        f"Process: ✅ Running (CPU: {process.cpu_percent()}%, Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB)"
                    )
                else:
                    print("Process: ⚠️  Not running (stale status file)")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print("Process: ⚠️  Not found (stale status file)")

        # Start time
        started_at = status.get("started_at")
        if started_at:
            try:
                start_dt = datetime.fromisoformat(started_at)
                print(f"Started: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")

                # Calculate uptime
                uptime = datetime.now() - start_dt
                hours = int(uptime.total_seconds() // 3600)
                minutes = int((uptime.total_seconds() % 3600) // 60)
                print(f"Uptime: {hours}h {minutes}m")
            except ValueError:
                print(f"Started: {started_at}")

        # Current priority
        current_priority = status.get("current_priority")
        if current_priority:
            name = current_priority.get("name", "Unknown")
            title = current_priority.get("title", "")
            print(f"\nCurrent Priority: {name}")
            if title:
                print(f"  {title}")

            priority_started = current_priority.get("started_at")
            if priority_started:
                try:
                    priority_dt = datetime.fromisoformat(priority_started)
                    elapsed = datetime.now() - priority_dt
                    minutes = int(elapsed.total_seconds() // 60)
                    print(f"  Working on this for: {minutes} minutes")
                except ValueError:
                    pass
        else:
            print("\nCurrent Priority: None (idle)")

        # Iteration count
        iteration = status.get("iteration", 0)
        print(f"\nIteration: {iteration}")

        # Crash info
        crashes = status.get("crashes", {})
        crash_count = crashes.get("count", 0)
        max_crashes = crashes.get("max", 3)
        print(f"Crashes: {crash_count}/{max_crashes}")

        if crash_count > 0:
            print("⚠️  Recent crashes detected!")
            crash_history = crashes.get("history", [])
            if crash_history:
                print("\nRecent crash history:")
                for i, crash in enumerate(crash_history[-3:], 1):
                    timestamp = crash.get("timestamp", "Unknown")
                    exception_type = crash.get("exception_type", "Unknown")
                    print(f"  {i}. {timestamp} - {exception_type}")

        # Context management info
        context = status.get("context", {})
        iterations_since_compact = context.get("iterations_since_compact", 0)
        compact_interval = context.get("compact_interval", 10)
        last_compact = context.get("last_compact")

        print(f"\nContext Management:")
        print(f"  Iterations since last compact: {iterations_since_compact}/{compact_interval}")
        if last_compact:
            try:
                compact_dt = datetime.fromisoformat(last_compact)
                print(f"  Last compact: {compact_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except ValueError:
                print(f"  Last compact: {last_compact}")
        else:
            print("  Last compact: Never")

        # Last update time
        last_update = status.get("last_update")
        if last_update:
            try:
                update_dt = datetime.fromisoformat(last_update)
                time_since = datetime.now() - update_dt
                seconds = int(time_since.total_seconds())
                print(f"\nLast update: {seconds}s ago ({update_dt.strftime('%H:%M:%S')})")
            except ValueError:
                print(f"\nLast update: {last_update}")

        return 0

    except json.JSONDecodeError:
        print("❌ Status file is corrupted")
        print(f"\nFile: {status_file}")
        return 1
    except Exception as e:
        print(f"❌ Error reading status: {e}")
        return 1


def cmd_notifications(args):
    """List pending notifications from daemon.

    Args:
        args: Parsed command-line arguments
    """
    print("\n" + "=" * 80)
    print("Pending Notifications")
    print("=" * 80 + "\n")

    db = NotificationDB()

    # Get pending notifications
    pending = db.get_pending_notifications()

    if not pending:
        print("✅ No pending notifications")
        return 0

    # Group by priority
    critical = [n for n in pending if n["priority"] == NOTIF_PRIORITY_CRITICAL]
    high = [n for n in pending if n["priority"] == NOTIF_PRIORITY_HIGH]
    normal = [n for n in pending if n["priority"] not in [NOTIF_PRIORITY_CRITICAL, NOTIF_PRIORITY_HIGH]]

    if critical:
        print("🚨 CRITICAL:")
        for notif in critical:
            print(f"  [{notif['id']}] {notif['title']}")
            print(f"      {notif['message']}")
            print(f"      Type: {notif['type']} | Created: {notif['created_at']}")
            print()

    if high:
        print("⚠️  HIGH:")
        for notif in high:
            print(f"  [{notif['id']}] {notif['title']}")
            print(f"      {notif['message']}")
            print(f"      Type: {notif['type']} | Created: {notif['created_at']}")
            print()

    if normal:
        print("📋 NORMAL:")
        for notif in normal:
            print(f"  [{notif['id']}] {notif['title']}")
            print(f"      {notif['message']}")
            print(f"      Type: {notif['type']} | Created: {notif['created_at']}")
            print()

    print(f"\nTotal: {len(pending)} pending notification(s)")
    print("\nTip: Use 'project-manager respond <id> <response>' to respond")

    return 0


def cmd_respond(args):
    """Respond to a notification.

    Args:
        args: Parsed arguments with notif_id and response
    """
    db = NotificationDB()

    # Get notification
    notif = db.get_notification(args.notif_id)

    if not notif:
        print(f"❌ Notification {args.notif_id} not found")
        return 1

    if notif["status"] != NOTIF_STATUS_PENDING:
        print(f"⚠️  Notification {args.notif_id} is not pending (status: {notif['status']})")
        return 1

    # Respond
    db.respond_to_notification(args.notif_id, args.response)

    print(f"✅ Responded to notification {args.notif_id}: {args.response}")
    print(f"\nOriginal question: {notif['title']}")
    print(f"Your response: {args.response}")

    return 0


def cmd_sync(args):
    """Sync roadmap with daemon environment.

    Args:
        args: Parsed command-line arguments
    """
    print("\n" + "=" * 80)
    print("Sync with Daemon Environment")
    print("=" * 80 + "\n")

    # For MVP, this is a placeholder
    print("Sync: Not implemented yet (MVP Phase 1)")
    print("\nSync functionality will be available in Phase 2:")
    print("  - Copy ROADMAP.md to daemon environment")
    print("  - Sync database changes")
    print("  - Verify consistency")

    return 0


def cmd_chat(args):
    """Start interactive chat session with AI (Phase 2).

    Args:
        args: Parsed command-line arguments
    """
    if not CHAT_AVAILABLE:
        print("❌ Chat feature not available")
        print("\nMissing dependencies or ANTHROPIC_API_KEY not set.")
        print("\nPlease ensure:")
        print("  1. All dependencies are installed: poetry install")
        print("  2. ANTHROPIC_API_KEY is set in .env file")
        return 1

    try:
        import os
        import shutil

        # Check if we're ALREADY running inside Claude CLI (Claude Code)
        # If so, we MUST use API mode to avoid nesting
        inside_claude_cli = bool(os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"))

        if inside_claude_cli:
            logger.info("Detected running inside Claude Code - forcing API mode to avoid nesting")

        # Auto-detect mode: CLI vs API (same logic as daemon)
        claude_path = "/opt/homebrew/bin/claude"
        has_cli = shutil.which("claude") or os.path.exists(claude_path)
        has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))

        use_claude_cli = False

        if inside_claude_cli:
            # We're already in Claude CLI - MUST use API to avoid nesting
            if has_api_key:
                print("=" * 70)
                print("ℹ️  Detected: Running inside Claude Code")
                print("=" * 70)
                print("🔄 Using Anthropic API to avoid CLI nesting")
                print("💡 TIP: CLI nesting is not recommended")
                print("=" * 70 + "\n")
                use_claude_cli = False
            else:
                # No API key - can't proceed
                print("=" * 70)
                print("❌ ERROR: Running inside Claude Code without API key")
                print("=" * 70)
                print("\nYou're running project-manager chat from within Claude Code.")
                print("To avoid CLI nesting, we need to use API mode.")
                print("\n🔧 SOLUTION:")
                print("  1. Get your API key from: https://console.anthropic.com/")
                print("  2. Set the environment variable:")
                print("     export ANTHROPIC_API_KEY='your-api-key-here'")
                print("  3. Or add it to your .env file")
                print("\n💡 ALTERNATIVE: Run from a regular terminal (not Claude Code)")
                print("=" * 70 + "\n")
                return 1
        elif has_cli:
            # CLI available - use it as default (free with subscription!)
            print("=" * 70)
            print("ℹ️  Auto-detected: Using Claude CLI (default)")
            print("=" * 70)
            print("💡 TIP: Claude CLI is free with your subscription!")
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
            print("\nThe chat requires either:")
            print("  1. Claude CLI installed (recommended - free with subscription), OR")
            print("  2. Anthropic API key (requires credits)")
            print("\n🔧 SOLUTION 1 (CLI Mode - Recommended):")
            print("  1. Install Claude CLI from: https://claude.ai/")
            print("  2. Run: poetry run project-manager chat")
            print("\n🔧 SOLUTION 2 (API Mode):")
            print("  1. Get your API key from: https://console.anthropic.com/")
            print("  2. Set the environment variable:")
            print("     export ANTHROPIC_API_KEY='your-api-key-here'")
            print("  3. Run: poetry run project-manager chat")
            print("\n" + "=" * 70 + "\n")
            return 1

        # Initialize components
        editor = RoadmapEditor(ROADMAP_PATH)
        ai_service = AIService(use_claude_cli=use_claude_cli, claude_cli_path=claude_path)

        # Check AI service availability
        if not ai_service.check_available():
            print("❌ AI service not available")
            print("\nPlease check:")
            if use_claude_cli:
                print("  - Claude CLI is installed and working")
            else:
                print("  - ANTHROPIC_API_KEY is valid")
            print("  - Internet connection is active")
            return 1

        # Start chat session
        session = ChatSession(ai_service, editor)
        session.start()

        return 0

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        if "ANTHROPIC_API_KEY" in str(e):
            print("\n💡 TIP: Install Claude CLI for free usage (no API key needed)!")
            print("   Get it from: https://claude.ai/")
        return 1
    except Exception as e:
        logger.error(f"Chat session failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="project-manager",
        description="Coffee Maker Agent - Project Manager CLI with AI (Phase 2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive AI chat (Phase 2) ⭐ NEW
  project-manager chat

  # View full roadmap
  project-manager view

  # View specific priority
  project-manager view 1
  project-manager view PRIORITY-3

  # Check pending notifications
  project-manager notifications

  # Respond to notification
  project-manager respond 5 approve
  project-manager respond 10 "no, use option 2"

  # Check daemon status
  project-manager status

Phase 1 (Complete):
  ✅ View roadmap (read-only)
  ✅ List notifications
  ✅ Respond to notifications
  ✅ Basic CLI commands

Phase 2 (Current): ⭐ NEW
  ✅ Interactive AI chat session
  ✅ Natural language roadmap management
  ✅ Rich terminal UI
  ✅ Intelligent roadmap analysis
  ✅ Command handlers (/add, /update, /view, /analyze)

Use 'project-manager chat' for the best experience!
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # View command
    view_parser = subparsers.add_parser("view", help="View roadmap")
    view_parser.add_argument("priority", nargs="?", help="Specific priority to view (optional)")

    # Status command
    subparsers.add_parser("status", help="Show daemon status")

    # Notifications command
    subparsers.add_parser("notifications", help="List pending notifications")

    # Respond command
    respond_parser = subparsers.add_parser("respond", help="Respond to notification")
    respond_parser.add_argument("notif_id", type=int, help="Notification ID")
    respond_parser.add_argument("response", help="Your response")

    # Sync command
    subparsers.add_parser("sync", help="Sync with daemon environment")

    # Chat command (Phase 2)
    subparsers.add_parser("chat", help="Start interactive AI chat session (Phase 2)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handler
    commands = {
        "view": cmd_view,
        "status": cmd_status,
        "notifications": cmd_notifications,
        "respond": cmd_respond,
        "sync": cmd_sync,
        "chat": cmd_chat,  # Phase 2
    }

    handler = commands.get(args.command)
    if handler:
        try:
            return handler(args)
        except Exception as e:
            logger.error(f"Command failed: {e}")
            import traceback

            traceback.print_exc()
            return 1
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
