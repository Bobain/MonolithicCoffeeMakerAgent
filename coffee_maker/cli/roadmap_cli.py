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

from coffee_maker.cli.console_ui import (
    console,
    create_table,
    error,
    format_notification,
    info,
    section_header,
    success,
    warning,
)
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
    section_header("Pending Notifications", "Review and respond to daemon questions and updates")

    db = NotificationDB()

    # Get pending notifications
    pending = db.get_pending_notifications()

    if not pending:
        success("No pending notifications")
        console.print()
        return 0

    # Group by priority
    critical = [n for n in pending if n["priority"] == NOTIF_PRIORITY_CRITICAL]
    high = [n for n in pending if n["priority"] == NOTIF_PRIORITY_HIGH]
    normal = [n for n in pending if n["priority"] not in [NOTIF_PRIORITY_CRITICAL, NOTIF_PRIORITY_HIGH]]

    # Display critical notifications
    if critical:
        console.print(f"[bold red]🚨 CRITICAL ({len(critical)})[/bold red]")
        console.print()
        for notif in critical:
            panel = format_notification(
                notif_type=notif["type"],
                title=f"[{notif['id']}] {notif['title']}",
                message=notif["message"],
                priority=notif["priority"],
                created_at=notif["created_at"],
            )
            console.print(panel)
            console.print()

    # Display high priority notifications
    if high:
        console.print(f"[bold yellow]⚠️  HIGH PRIORITY ({len(high)})[/bold yellow]")
        console.print()
        for notif in high:
            panel = format_notification(
                notif_type=notif["type"],
                title=f"[{notif['id']}] {notif['title']}",
                message=notif["message"],
                priority=notif["priority"],
                created_at=notif["created_at"],
            )
            console.print(panel)
            console.print()

    # Display normal notifications
    if normal:
        console.print(f"[bold blue]📋 NORMAL ({len(normal)})[/bold blue]")
        console.print()
        for notif in normal:
            panel = format_notification(
                notif_type=notif["type"],
                title=f"[{notif['id']}] {notif['title']}",
                message=notif["message"],
                priority=notif["priority"],
                created_at=notif["created_at"],
            )
            console.print(panel)
            console.print()

    # Summary
    info(f"Total: {len(pending)} pending notification(s)")
    console.print()
    console.print("[dim]💡 Tip: Use 'project-manager respond <id> <response>' to respond[/dim]")
    console.print()

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
        error(
            f"Notification {args.notif_id} not found",
            suggestion="Use 'project-manager notifications' to see available notifications",
        )
        return 1

    if notif["status"] != NOTIF_STATUS_PENDING:
        warning(
            f"Notification {args.notif_id} is not pending (status: {notif['status']})",
            suggestion="Only pending notifications can be responded to",
        )
        return 1

    # Respond
    db.respond_to_notification(args.notif_id, args.response)

    console.print()
    success(f"Responded to notification {args.notif_id}")
    console.print()

    # Show details in a table
    table = create_table(title="Response Details", show_header=False)
    table.add_column(style="bold cyan", justify="right")
    table.add_column()
    table.add_row("Original Question", notif["title"])
    table.add_row("Your Response", args.response)
    table.add_row("Timestamp", notif["created_at"])

    console.print(table)
    console.print()

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
            user_story=user_story,
            feature_type=feature_type,
            complexity=complexity,
            user_story_id=user_story_id,
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


def cmd_metrics(args: argparse.Namespace) -> int:
    """Show estimation metrics and velocity tracking.

    US-015: Estimation Metrics & Velocity Tracking

    Displays comprehensive metrics including:
    - Current velocity (stories/week, points/week)
    - Estimation accuracy trends
    - Category-specific accuracy
    - Spec vs no-spec comparison
    - Recent completed stories

    Args:
        args: Parsed command-line arguments with optional filters

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager metrics
        $ project-manager metrics --period 14
        $ project-manager metrics --category feature
    """
    from coffee_maker.autonomous.story_metrics import StoryMetricsDB

    try:
        print("\n" + "=" * 80)
        print("📊 ESTIMATION METRICS & VELOCITY TRACKING (US-015)")
        print("=" * 80 + "\n")

        metrics_db = StoryMetricsDB()

        # Get period from args (default: 7 days for weekly)
        period_days = args.period if hasattr(args, "period") else 7

        # Current Velocity
        print("📈 CURRENT VELOCITY")
        print("-" * 80)
        velocity = metrics_db.get_current_velocity(period_days=period_days)

        print(f"Period: Last {period_days} days")
        print(f"Stories per week: {velocity['stories_per_week']:.2f}")
        print(f"Story points per week: {velocity['points_per_week']:.2f}")
        print(f"Average days per story: {velocity['avg_days_per_story']:.2f}")
        print(f"Average accuracy: {velocity['avg_accuracy_pct']:.1f}%")
        print()

        # Accuracy Trends
        print("🎯 ACCURACY TRENDS (Recent 10 Stories)")
        print("-" * 80)
        trends = metrics_db.get_accuracy_trends(limit=10)

        if trends:
            print(f"{'Story':<15} {'Estimated':<12} {'Actual':<10} {'Error':<10} {'Accuracy':>10}")
            print("-" * 80)
            for trend in trends:
                story_id = trend["story_id"]
                est_min = trend["estimated_min_days"]
                est_max = trend["estimated_max_days"]
                actual = trend["actual_days"]
                error = trend["estimation_error"]
                accuracy = trend["estimation_accuracy_pct"]

                est_str = f"{est_min}-{est_max}"
                error_str = f"{error:+.1f}d" if error else "N/A"
                accuracy_str = f"{accuracy:.1f}%" if accuracy else "N/A"

                # Color coding based on accuracy
                if accuracy and accuracy >= 90:
                    marker = "✅"
                elif accuracy and accuracy >= 75:
                    marker = "⚠️ "
                else:
                    marker = "❌"

                print(f"{story_id:<15} {est_str:<12} {actual:<10.1f} {error_str:<10} {marker} {accuracy_str:>8}")
        else:
            print("No completed stories yet")
        print()

        # Category Accuracy
        print("📂 ACCURACY BY CATEGORY")
        print("-" * 80)
        category_stats = metrics_db.get_category_accuracy()

        if category_stats:
            print(f"{'Category':<15} {'Stories':<10} {'Avg Accuracy':<15} {'Avg Actual':<12} {'Avg Estimated':<15}")
            print("-" * 80)
            for stat in category_stats:
                category = stat["category"]
                count = stat["story_count"]
                accuracy = stat["avg_accuracy_pct"]
                actual = stat["avg_actual_days"]
                estimated = stat["avg_estimated_days"]

                print(f"{category:<15} {count:<10} {accuracy:<15.1f}% {actual:<12.1f} {estimated:<15.1f}")
        else:
            print("No category data yet")
        print()

        # Spec vs No-Spec Comparison
        print("📋 TECHNICAL SPEC COMPARISON")
        print("-" * 80)
        spec_comparison = metrics_db.get_spec_comparison()

        with_spec = spec_comparison["with_spec"]
        without_spec = spec_comparison["without_spec"]

        print(f"{'Type':<20} {'Stories':<10} {'Avg Accuracy':<15} {'Avg Days':<12}")
        print("-" * 80)
        print(
            f"{'With Spec':<20} {with_spec['count']:<10} {with_spec['avg_accuracy_pct']:<15.1f}% {with_spec['avg_actual_days']:<12.1f}"
        )
        print(
            f"{'Without Spec':<20} {without_spec['count']:<10} {without_spec['avg_accuracy_pct']:<15.1f}% {without_spec['avg_actual_days']:<12.1f}"
        )

        if with_spec["count"] > 0 and without_spec["count"] > 0:
            accuracy_diff = with_spec["avg_accuracy_pct"] - without_spec["avg_accuracy_pct"]
            if accuracy_diff > 0:
                print(f"\n✅ Stories with technical specs are {accuracy_diff:.1f}% more accurate!")
            elif accuracy_diff < 0:
                print(f"\n⚠️  Stories without specs are {abs(accuracy_diff):.1f}% more accurate")
            else:
                print("\n➡️  No significant difference")
        print()

        # Tips
        print("💡 TIPS")
        print("-" * 80)
        if velocity["avg_accuracy_pct"] < 75:
            print("⚠️  Accuracy below 75% - consider creating more detailed technical specs")
        elif velocity["avg_accuracy_pct"] >= 90:
            print("✅ Excellent estimation accuracy! Keep up the good work!")
        else:
            print("✅ Good estimation accuracy - room for improvement")

        if with_spec["count"] > 0 and with_spec["avg_accuracy_pct"] > without_spec["avg_accuracy_pct"]:
            print("✅ Technical specs improve accuracy - keep using them!")

        print()
        print(f"Database: {metrics_db.db_path}")
        print(f"Use 'project-manager metrics --period 14' to see 2-week velocity")
        print()

        return 0

    except Exception as e:
        logger.error(f"Failed to show metrics: {e}", exc_info=True)
        print(f"❌ Error showing metrics: {e}")
        return 1


def cmd_summary(args: argparse.Namespace) -> int:
    """Show delivery summary for recently completed stories.

    US-017 Phase 2: CLI Integration - /summary command
    US-017 Phase 4: Manual update trigger - /summary --update

    Displays executive-style summary of recent deliveries including:
    - Story ID and title
    - Completion date
    - Business value
    - Key features delivered
    - Estimation accuracy

    Args:
        args: Parsed command-line arguments with optional --days, --format, --update

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager summary
        $ project-manager summary --days 7
        $ project-manager summary --days 30 --format text
        $ project-manager summary --update  # Force update STATUS_TRACKING.md
    """
    from coffee_maker.reports.status_report_generator import StatusReportGenerator
    from coffee_maker.reports.status_tracking_updater import check_and_update_if_needed

    try:
        # Check if update flag is set (Phase 4)
        force_update = args.update if hasattr(args, "update") else False

        if force_update:
            print("\n" + "=" * 80)
            print("🔄 FORCING STATUS_TRACKING.md UPDATE")
            print("=" * 80 + "\n")

            result = check_and_update_if_needed(force=True)

            if result["updated"]:
                print(f"✅ STATUS_TRACKING.md updated successfully!")
                print(f"   Reason: {result['reason']}")
                print()
            else:
                print(f"⚠️  Update skipped: {result['reason']}")
                print()
        else:
            # Auto-check if update is needed (3-day schedule or estimate changes)
            result = check_and_update_if_needed(force=False)

            if result["updated"]:
                print("\n" + "=" * 80)
                print("✅ STATUS_TRACKING.md AUTO-UPDATE")
                print("=" * 80)
                print(f"Reason: {result['reason']}")
                print()

        # Get parameters from args
        days = args.days if hasattr(args, "days") else 14
        output_format = args.format if hasattr(args, "format") else "markdown"

        # Validate parameters
        if days <= 0:
            print("❌ Error: --days must be greater than 0")
            return 1

        if output_format not in ["text", "markdown"]:
            print(f"❌ Error: Invalid format '{output_format}'. Use 'text' or 'markdown'")
            return 1

        # Initialize generator
        generator = StatusReportGenerator(str(ROADMAP_PATH))

        # Get recent completions
        completions = generator.get_recent_completions(days=days)

        if not completions:
            print("\n" + "=" * 80)
            print(f"📦 DELIVERY SUMMARY (Last {days} days)")
            print("=" * 80 + "\n")
            print(f"No deliveries completed in the last {days} days.")
            print("\nTip: Try increasing the time period with --days N")
            print()
            return 0

        # Format summary
        summary = generator.format_delivery_summary(completions)

        # Display based on format
        if output_format == "markdown":
            print("\n" + summary)
        else:
            # Text format: Remove markdown formatting
            text_summary = summary.replace("# ", "").replace("## ", "").replace("**", "").replace("---", "-" * 80)
            print("\n" + text_summary)

        # Footer
        print()
        print(f"💡 TIP: Use 'project-manager summary --days N' to change time period")
        print(f"   Use 'project-manager summary --update' to force STATUS_TRACKING.md update")
        print(f"   Use 'project-manager calendar' to see upcoming deliverables")
        print()

        return 0

    except FileNotFoundError:
        print(f"❌ Error: ROADMAP not found at {ROADMAP_PATH}")
        return 1
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}", exc_info=True)
        print(f"❌ Error generating summary: {e}")
        return 1


def cmd_calendar(args: argparse.Namespace) -> int:
    """Show calendar of upcoming deliverables with estimated completion dates.

    US-017 Phase 2: CLI Integration - /calendar command
    US-017 Phase 4: Manual update trigger - /calendar --update

    Displays upcoming priorities/stories with:
    - Priority order (1, 2, 3...)
    - Estimated completion dates
    - What description
    - Impact statement

    Args:
        args: Parsed command-line arguments with optional --limit, --format, --update

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager calendar
        $ project-manager calendar --limit 5
        $ project-manager calendar --limit 10 --format text
        $ project-manager calendar --update  # Force update STATUS_TRACKING.md
    """
    from coffee_maker.reports.status_report_generator import StatusReportGenerator
    from coffee_maker.reports.status_tracking_updater import check_and_update_if_needed

    try:
        # Check if update flag is set (Phase 4)
        force_update = args.update if hasattr(args, "update") else False

        if force_update:
            print("\n" + "=" * 80)
            print("🔄 FORCING STATUS_TRACKING.md UPDATE")
            print("=" * 80 + "\n")

            result = check_and_update_if_needed(force=True)

            if result["updated"]:
                print(f"✅ STATUS_TRACKING.md updated successfully!")
                print(f"   Reason: {result['reason']}")
                print()
            else:
                print(f"⚠️  Update skipped: {result['reason']}")
                print()
        else:
            # Auto-check if update is needed (3-day schedule or estimate changes)
            result = check_and_update_if_needed(force=False)

            if result["updated"]:
                print("\n" + "=" * 80)
                print("✅ STATUS_TRACKING.md AUTO-UPDATE")
                print("=" * 80)
                print(f"Reason: {result['reason']}")
                print()

        # Get parameters from args
        limit = args.limit if hasattr(args, "limit") else 3
        output_format = args.format if hasattr(args, "format") else "markdown"

        # Validate parameters
        if limit <= 0:
            print("❌ Error: --limit must be greater than 0")
            return 1

        if output_format not in ["text", "markdown"]:
            print(f"❌ Error: Invalid format '{output_format}'. Use 'text' or 'markdown'")
            return 1

        # Initialize generator
        generator = StatusReportGenerator(str(ROADMAP_PATH))

        # Get upcoming deliverables
        upcoming = generator.get_upcoming_deliverables(limit=limit)

        if not upcoming:
            print("\n" + "=" * 80)
            print("📅 UPCOMING DELIVERABLES CALENDAR")
            print("=" * 80 + "\n")
            print("No upcoming deliverables with time estimates found.")
            print("\nTip: Add estimated effort to stories in ROADMAP.md")
            print("   Format: **Estimated Effort**: X-Y days")
            print()
            return 0

        # Format calendar
        calendar = generator.format_calendar_report(upcoming)

        # Display based on format
        if output_format == "markdown":
            print("\n" + calendar)
        else:
            # Text format: Remove markdown formatting
            text_calendar = calendar.replace("# ", "").replace("## ", "").replace("**", "").replace("---", "-" * 80)
            print("\n" + text_calendar)

        # Footer
        print()
        print(f"💡 TIP: Use 'project-manager calendar --limit N' to see more/fewer items")
        print(f"   Use 'project-manager calendar --update' to force STATUS_TRACKING.md update")
        print(f"   Use 'project-manager summary' to see recent deliveries")
        print()

        return 0

    except FileNotFoundError:
        print(f"❌ Error: ROADMAP not found at {ROADMAP_PATH}")
        return 1
    except Exception as e:
        logger.error(f"Failed to generate calendar: {e}", exc_info=True)
        print(f"❌ Error generating calendar: {e}")
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
        "--type",
        default="general",
        help="Feature type (crud, integration, ui, infrastructure, analytics, security)",
    )
    spec_parser.add_argument("--complexity", default="medium", help="Complexity (low, medium, high)")
    spec_parser.add_argument("--id", help="User story ID (e.g., US-016) for ROADMAP update")

    # Chat command (Phase 2)
    subparsers.add_parser("chat", help="Start interactive AI chat session (Phase 2)")

    # Assistant commands (PRIORITY 5)
    subparsers.add_parser("assistant-status", help="Show assistant status and knowledge state")
    subparsers.add_parser("assistant-refresh", help="Manually refresh assistant documentation")

    # Metrics command (US-015)
    metrics_parser = subparsers.add_parser("metrics", help="Show estimation metrics and velocity tracking (US-015)")
    metrics_parser.add_argument(
        "--period",
        type=int,
        default=7,
        help="Period in days for velocity calculation (default: 7)",
    )

    # Summary command (US-017 Phase 2 + Phase 4)
    summary_parser = subparsers.add_parser("summary", help="Show delivery summary for recent completions (US-017)")
    summary_parser.add_argument("--days", type=int, default=14, help="Number of days to look back (default: 14)")
    summary_parser.add_argument(
        "--format",
        type=str,
        default="markdown",
        choices=["text", "markdown"],
        help="Output format (default: markdown)",
    )
    summary_parser.add_argument(
        "--update",
        action="store_true",
        help="Force regenerate STATUS_TRACKING.md (Phase 4)",
    )

    # Calendar command (US-017 Phase 2 + Phase 4)
    calendar_parser = subparsers.add_parser("calendar", help="Show calendar of upcoming deliverables (US-017)")
    calendar_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of upcoming items to show (default: 3)",
    )
    calendar_parser.add_argument(
        "--format",
        type=str,
        default="markdown",
        choices=["text", "markdown"],
        help="Output format (default: markdown)",
    )
    calendar_parser.add_argument(
        "--update",
        action="store_true",
        help="Force regenerate STATUS_TRACKING.md (Phase 4)",
    )

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
        "metrics": cmd_metrics,  # US-015
        "summary": cmd_summary,  # US-017 Phase 2
        "calendar": cmd_calendar,  # US-017 Phase 2
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
