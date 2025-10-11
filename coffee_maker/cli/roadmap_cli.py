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

    Args:
        args: Parsed command-line arguments
    """
    print("\n" + "=" * 80)
    print("Daemon Status")
    print("=" * 80 + "\n")

    # For MVP, this is a placeholder
    # In Phase 2, this will query daemon's actual status
    print("Status: Not implemented yet (MVP Phase 1)")
    print("\nDaemon status will be available in Phase 2:")
    print("  - Running/Stopped status")
    print("  - Current task")
    print("  - Progress")
    print("  - Last activity")

    return 0


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
        # Initialize components
        editor = RoadmapEditor(ROADMAP_PATH)
        ai_service = AIService()

        # Check AI service availability
        if not ai_service.check_available():
            print("❌ AI service not available")
            print("\nPlease check:")
            print("  - ANTHROPIC_API_KEY is valid")
            print("  - Internet connection is active")
            return 1

        # Start chat session
        session = ChatSession(ai_service, editor)
        session.start()

        return 0

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set ANTHROPIC_API_KEY in your .env file")
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
