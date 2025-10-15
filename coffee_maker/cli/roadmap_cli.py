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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WORKFLOW INTEGRATION: US-027 (ROADMAP BRANCH AS SOURCE OF TRUTH)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT: The 'roadmap' branch is the SINGLE SOURCE OF TRUTH for ROADMAP.md

When viewing the roadmap with project-manager, you should ALWAYS be on the
'roadmap' branch to see the latest priorities and status updates.

US-027 Workflow (Manager Side):
────────────────────────────────
1. project_manager MUST view roadmap from 'roadmap' branch
2. code_developer daemon syncs FROM 'roadmap' branch each iteration
3. Updates to priorities happen ON 'roadmap' branch
4. Feature branches merge TO 'roadmap' frequently (US-024)

Why This Matters:
─────────────────
    ❌ WRONG: Viewing roadmap from feature branch
       → Shows stale priorities
       → User provides feedback on obsolete tasks
       → Daemon wastes time on wrong work

    ✅ CORRECT: Always viewing roadmap from 'roadmap' branch
       → Shows current priorities
       → User provides feedback on actual work
       → Daemon implements correct priorities

Branch Warning System:
──────────────────────
The `cmd_view` function checks your current branch and warns if you're not
on 'roadmap':

    $ git checkout feature/something
    $ project-manager view

    ⚠️  ══════════════════════════════════════════════════════════════
    ⚠️  WARNING: You are NOT on the roadmap branch!
    ⚠️  ══════════════════════════════════════════════════════════════

       Current branch: feature/something
       Roadmap branch is the SINGLE SOURCE OF TRUTH

       To view latest priorities:
       $ git checkout roadmap && git pull

Best Practice:
──────────────
Always start your session with:

    $ git checkout roadmap
    $ git pull origin roadmap
    $ project-manager view

This ensures you're looking at the daemon's current priorities, not stale
feature branch versions.

The Complete Visibility Loop:
─────────────────────────────

    code_developer              project_manager
    (daemon)                    (this CLI)
         │                            │
         ├─[1. Work]────►             │
         │                            │
         ├─[2. Merge to roadmap]──►  │
         │      (US-024)              │
         │                       ┌────┴────┐
         │                       │ View on │
         │                       │ roadmap │
         │                       │ branch  │
         │                       └────┬────┘
         │                            │
         │    ┌───────────────────────┘
         │    │ [3. User updates ROADMAP.md
         │    │     on roadmap branch]
         │    │
    ┌────┴────▼───┐
    │ [4. Sync    │
    │  from       │
    │  roadmap]   │
    │  (US-027)   │
    └────┬────────┘
         │
         └─[5. Continue with updated priorities]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commands:
    project-manager view [priority]      View roadmap (or specific priority)
    project-manager status                Show daemon status
    project-manager notifications        List pending notifications
    project-manager respond <id> <msg>   Respond to notification
    project-manager sync                  Sync with daemon environment

Example:
    # ALWAYS start by ensuring you're on roadmap branch
    $ git checkout roadmap && git pull

    # View full roadmap (from roadmap branch)
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
from coffee_maker.config import ROADMAP_PATH, ConfigManager

# Configure logging BEFORE imports that might fail
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Import chat components for Phase 2
try:
    from coffee_maker.cli.ai_service import AIService
    from coffee_maker.cli.assistant_manager import AssistantManager
    from coffee_maker.cli.chat_interface import ChatSession
    from coffee_maker.cli.roadmap_editor import RoadmapEditor

    # Import all command handlers to register them
    from coffee_maker.cli.commands import all_commands  # noqa: F401

    CHAT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chat features not available: {e}")
    CHAT_AVAILABLE = False


def cmd_view(args: argparse.Namespace) -> int:
    """View roadmap or specific priority.

    Args:
        args: Parsed command-line arguments with priority field

    Returns:
        0 on success, 1 on error
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


def cmd_status(args: argparse.Namespace) -> int:
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
    from datetime import datetime
    from pathlib import Path

    from coffee_maker.utils.file_io import read_json_file, FileOperationError

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
        status = read_json_file(status_file)

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

    except FileOperationError as e:
        print("❌ Status file is corrupted")
        print(f"\nFile: {status_file}")
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error reading status: {e}")
        return 1


def cmd_developer_status(args: argparse.Namespace) -> int:
    """Show developer status dashboard.

    PRIORITY 4: Developer Status Dashboard

    Displays real-time developer status including current task, progress,
    activities, and metrics.

    Args:
        args: Parsed command-line arguments with optional --watch flag

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager developer-status
        $ project-manager developer-status --watch
    """
    from coffee_maker.cli.developer_status_display import DeveloperStatusDisplay

    display = DeveloperStatusDisplay()

    if hasattr(args, "watch") and args.watch:
        # Continuous watch mode
        display.watch(interval=args.interval if hasattr(args, "interval") else 5)
    else:
        # One-time display
        if not display.show():
            return 1

    return 0


def cmd_notifications(args: argparse.Namespace) -> int:
    """List pending notifications from daemon.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success
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


def cmd_respond(args: argparse.Namespace) -> int:
    """Respond to a notification.

    Args:
        args: Parsed arguments with notif_id and response

    Returns:
        0 on success, 1 on error
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


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync roadmap with daemon environment.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 (always successful for MVP placeholder)
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


def cmd_spec(args: argparse.Namespace) -> int:
    """Generate technical specification for a user story.

    US-016 Phase 5: Interactive Spec Generation Workflow

    This command:
    1. Generates technical spec from user story
    2. Shows delivery estimate with buffer
    3. Prompts for review (approve/reject)
    4. Updates ROADMAP.md on approval

    Args:
        args: Parsed command-line arguments with user_story, feature_type, complexity, etc.

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager spec "Email notifications for completed tasks" --type integration --complexity medium
    """
    if not CHAT_AVAILABLE:
        print("❌ Spec generation not available")
        print("\nMissing dependencies. Install with: poetry install")
        return 1

    try:
        from coffee_maker.cli.spec_workflow import SpecWorkflow

        print("\n" + "=" * 80)
        print("Technical Specification Generation (US-016 Phase 5)")
        print("=" * 80 + "\n")

        # Initialize AI service and workflow
        ai_service = AIService()
        workflow = SpecWorkflow(ai_service)

        # Get parameters
        user_story = args.user_story
        feature_type = args.type if hasattr(args, "type") else "general"
        complexity = args.complexity if hasattr(args, "complexity") else "medium"
        user_story_id = args.id if hasattr(args, "id") else None

        print(f"Generating specification...")
        print(f"  User Story: {user_story[:60]}...")
        print(f"  Type: {feature_type}")
        print(f"  Complexity: {complexity}")
        print()

        # Generate spec
        result = workflow.generate_and_review_spec(
            user_story=user_story, feature_type=feature_type, complexity=complexity, user_story_id=user_story_id
        )

        # Show summary
        print(workflow.format_spec_summary(result))
        print()

        # Prompt for review
        response = input("Review the spec? [y/n]: ").strip().lower()

        if response == "y":
            # Show spec file location
            print(f"\nSpec saved to: {result.spec_path}")
            print("\nPlease review the technical specification.")
            print()

            # Show what will be updated in ROADMAP
            if user_story_id:
                print(workflow.format_roadmap_update_example(result, user_story_id))
                print()

            # Approval workflow
            approve_response = input("Approve this specification? [y/n]: ").strip().lower()

            if approve_response == "y":
                # Approve and update ROADMAP
                if user_story_id:
                    workflow.approve_spec(result, user_story_id)
                    print(f"\n✅ Specification approved!")
                    print(f"   ROADMAP.md updated for {user_story_id}")
                    print(f"   Estimated delivery: {result.delivery_estimate['delivery_date']}")
                else:
                    print("\n⚠️  No user story ID provided, cannot update ROADMAP")
                    print("   Spec saved but ROADMAP not updated")

                return 0

            else:
                # Rejected
                reason = input("Reason for rejection (optional): ").strip()
                workflow.reject_spec(result, reason or "User rejected")
                print(f"\n❌ Specification rejected: {reason}")
                print(f"   Spec kept at {result.spec_path} for reference")

                return 0

        else:
            print(f"\nSpec saved to: {result.spec_path}")
            print("   Review later and use 'project-manager spec' to approve")
            return 0

    except Exception as e:
        logger.error(f"Spec generation failed: {e}")
        print(f"\n❌ Error generating spec: {e}")
        return 1


def cmd_assistant_status(args):
    """Show assistant status and knowledge state.

    PRIORITY 5: Assistant Auto-Refresh & Always-On Availability

    Displays:
    - Assistant online/offline status
    - Last documentation refresh time
    - Next scheduled refresh
    - Documentation files loaded
    - Git commit history loaded
    - Available tools

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager assistant-status
    """
    if not CHAT_AVAILABLE:
        print("❌ Assistant feature not available")
        print("\nMissing dependencies. Install with: poetry install")
        return 1

    try:
        from datetime import datetime

        # Get assistant manager from global context (will be set in main())
        if not hasattr(cmd_assistant_status, "manager"):
            print("❌ Assistant manager not initialized")
            print("\nThe assistant is not running.")
            return 1

        manager = cmd_assistant_status.manager
        status = manager.get_status()

        print("\n" + "=" * 80)
        print("🤖 ASSISTANT STATUS")
        print("=" * 80 + "\n")

        # Online status
        if status["online"]:
            print("Status: 🟢 ONLINE")
        else:
            print("Status: 🔴 OFFLINE")

        # Assistant availability
        if status["assistant_available"]:
            print("Assistant: ✅ Available")
        else:
            print("Assistant: ❌ Not available (no LLM configured)")

        # Refresh info
        if status["last_refresh"]:
            from dateutil.parser import isoparse

            last_refresh = isoparse(status["last_refresh"])
            elapsed = datetime.now() - last_refresh
            minutes = int(elapsed.total_seconds() // 60)

            print(f"\nLast Documentation Refresh: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')} ({minutes} minutes ago)")
        else:
            print("\nLast Documentation Refresh: Never")

        if status["next_refresh"]:
            print(f"Next Refresh: {status['next_refresh']}")

        # Documentation knowledge
        print(f"\nDocumentation Knowledge:")
        print(f"  📚 {status['docs_loaded']} document(s) loaded")

        for doc_info in status["docs_info"]:
            print(f"  ✅ {doc_info['path']}")
            print(f"     Modified: {doc_info['modified']}, Lines: {doc_info['line_count']}")

        # Git history
        if status["git_commits_loaded"] > 0:
            print(f"\n  📝 Git History: {status['git_commits_loaded']} recent commits loaded")

        # Tools (from assistant_bridge.py - hardcoded for now)
        print("\nTools Available:")
        tool_names = [
            "read_file",
            "search_code",
            "list_files",
            "git_log",
            "git_diff",
            "execute_bash",
        ]
        for tool in tool_names:
            print(f"  ✅ {tool}")

        print("\n✨ Ready to answer questions! 🚀")
        print("\nUse 'project-manager chat' to ask questions")
        print("Use 'project-manager assistant-refresh' to manually refresh documentation")
        print()

        return 0

    except Exception as e:
        logger.error(f"Failed to get assistant status: {e}", exc_info=True)
        print(f"❌ Error getting assistant status: {e}")
        return 1


def cmd_assistant_refresh(args):
    """Manually refresh assistant documentation.

    PRIORITY 5: Assistant Auto-Refresh & Always-On Availability

    Triggers an immediate refresh of:
    - ROADMAP.md
    - COLLABORATION_METHODOLOGY.md
    - DOCUMENTATION_INDEX.md
    - TUTORIALS.md
    - Recent git commits (last 10)

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager assistant-refresh
    """
    if not CHAT_AVAILABLE:
        print("❌ Assistant feature not available")
        print("\nMissing dependencies. Install with: poetry install")
        return 1

    try:
        # Get assistant manager from global context
        if not hasattr(cmd_assistant_refresh, "manager"):
            print("❌ Assistant manager not initialized")
            return 1

        manager = cmd_assistant_refresh.manager

        print("\n🔄 Refreshing assistant documentation...")
        print()

        # Trigger manual refresh
        result = manager.manual_refresh()

        if result["success"]:
            print("Reading ROADMAP.md... ✅")
            print("Reading COLLABORATION_METHODOLOGY.md... ✅")
            print("Reading DOCUMENTATION_INDEX.md... ✅")
            print("Reading TUTORIALS.md... ✅")
            print("Reading git history... ✅")
            print()
            print(f"✅ Assistant knowledge refreshed successfully!")
            print(f"   {result['docs_refreshed']} document(s) updated")
            print(f"   Timestamp: {result['timestamp']}")
            print()
        else:
            print(f"❌ Refresh failed: {result['message']}")
            return 1

        return 0

    except Exception as e:
        logger.error(f"Manual refresh failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1


def cmd_chat(args):
    """Start interactive chat session with AI (Phase 2).

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
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
        has_api_key = ConfigManager.has_anthropic_api_key()

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


def main() -> int:
    """Main CLI entry point.

    Returns:
        0 on success, 1 on error
    """
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

    # Developer status command (PRIORITY 4)
    dev_status_parser = subparsers.add_parser("developer-status", help="Show developer status dashboard")
    dev_status_parser.add_argument("--watch", action="store_true", help="Continuous watch mode")
    dev_status_parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval in seconds (default: 5)",
    )

    # Notifications command
    subparsers.add_parser("notifications", help="List pending notifications")

    # Respond command
    respond_parser = subparsers.add_parser("respond", help="Respond to notification")
    respond_parser.add_argument("notif_id", type=int, help="Notification ID")
    respond_parser.add_argument("response", help="Your response")

    # Sync command
    subparsers.add_parser("sync", help="Sync with daemon environment")

    # Spec command (US-016 Phase 5)
    spec_parser = subparsers.add_parser("spec", help="Generate technical specification (US-016 Phase 5)")
    spec_parser.add_argument("user_story", help="User story description")
    spec_parser.add_argument(
        "--type", default="general", help="Feature type (crud, integration, ui, infrastructure, analytics, security)"
    )
    spec_parser.add_argument("--complexity", default="medium", help="Complexity (low, medium, high)")
    spec_parser.add_argument("--id", help="User story ID (e.g., US-016) for ROADMAP update")

    # Chat command (Phase 2)
    subparsers.add_parser("chat", help="Start interactive AI chat session (Phase 2)")

    # Assistant commands (PRIORITY 5)
    subparsers.add_parser("assistant-status", help="Show assistant status and knowledge state")
    subparsers.add_parser("assistant-refresh", help="Manually refresh assistant documentation")

    args = parser.parse_args()

    # US-030: Default to chat when no command provided
    if not args.command:
        logger.info("No command provided - defaulting to chat interface (US-030)")
        args.command = "chat"

    # PRIORITY 5: Initialize and start AssistantManager if chat features available
    if CHAT_AVAILABLE:
        try:
            assistant_manager = AssistantManager()
            assistant_manager.start_auto_refresh()

            # Make manager available to command handlers via function attributes
            cmd_assistant_status.manager = assistant_manager
            cmd_assistant_refresh.manager = assistant_manager

            logger.info("Assistant manager initialized and auto-refresh started")
        except Exception as e:
            logger.warning(f"Failed to initialize assistant manager: {e}")

    # Route to command handler
    commands = {
        "view": cmd_view,
        "status": cmd_status,
        "developer-status": cmd_developer_status,  # PRIORITY 4
        "notifications": cmd_notifications,
        "respond": cmd_respond,
        "sync": cmd_sync,
        "spec": cmd_spec,  # US-016 Phase 5
        "chat": cmd_chat,  # Phase 2
        "assistant-status": cmd_assistant_status,  # PRIORITY 5
        "assistant-refresh": cmd_assistant_refresh,  # PRIORITY 5
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
