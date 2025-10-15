"""Autonomous development daemon - minimal MVP.

This module implements the core autonomous daemon that continuously reads
ROADMAP.md and autonomously implements features by invoking Claude API.

Architecture:
    DevDaemon: Main daemon loop
    ├── RoadmapParser: Reads and parses ROADMAP.md
    ├── ClaudeAPI/ClaudeCLI: Interfaces with Claude for implementation
    ├── GitManager: Handles git operations (branch, commit, push, PR)
    ├── DeveloperStatus: Real-time status tracking (PRIORITY 4)
    └── NotificationDB: Bidirectional communication with project-manager

Workflow:
    1. Parse ROADMAP.md for next planned priority
    2. Ensure technical specification exists (create if missing)
    3. Create feature branch
    4. Execute Claude API with implementation prompt
    5. Commit changes with proper message
    6. Push and create PR
    7. Update status and notify user
    8. Sleep and repeat

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WORKFLOW INTEGRATION: US-024 + US-027 (VISIBILITY LOOP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This daemon implements a dual workflow for real-time visibility between
code_developer (this daemon) and project_manager (user interface):

US-027: Roadmap Branch as Single Source of Truth (Developer Side)
──────────────────────────────────────────────────────────────────
The daemon ALWAYS syncs with 'roadmap' branch at the start of each iteration:

    def run():
        while True:
            # 1. SYNC FROM roadmap branch (US-027)
            _sync_roadmap_branch()  # Pull latest ROADMAP.md from origin/roadmap

            # 2. Read priorities
            next_priority = parser.get_next_planned_priority()

            # 3. Implement
            _implement_priority(next_priority)

            # 4. MERGE TO roadmap branch (US-024)
            # (Not yet implemented - see US-024.md)

            time.sleep(30)

Key principle: The 'roadmap' branch is the SINGLE SOURCE OF TRUTH.
All priority decisions, status updates, and planning changes MUST go
through the roadmap branch first.

US-024: Frequent Roadmap Sync (Developer → Manager Visibility)
───────────────────────────────────────────────────────────────
The daemon will merge to 'roadmap' branch frequently to show progress:

    Merge Triggers:
    - After completing sub-tasks
    - After updating ROADMAP.md
    - Before going idle/sleep
    - After creating tickets

    Implementation (planned):
        def _merge_to_roadmap(message: str):
            git checkout roadmap
            git merge --no-ff feature-branch -m message
            git push origin roadmap
            git checkout feature-branch

The Visibility Loop
───────────────────
Together, US-024 + US-027 create a continuous visibility loop:

    ┌─────────────────────────────────────────────────────────────┐
    │                  VISIBILITY LOOP                            │
    │                                                             │
    │   code_developer                    project_manager        │
    │   (this daemon)                     (user interface)        │
    │        │                                   │                │
    │        ├──[1. Work on feature]─────►      │                │
    │        │                                   │                │
    │        ├──[2. Merge to roadmap]────►  ┌───┴───┐            │
    │        │        (US-024)              │ See   │            │
    │        │                              │updates│            │
    │        │                              └───┬───┘            │
    │        │                                  │                │
    │        │   ┌──────────────────────────────┘                │
    │        │   │ [3. User provides feedback]                   │
    │        │   │    (updates ROADMAP.md on                     │
    │        │   │     roadmap branch)                           │
    │        │   │                                               │
    │   ┌────┴───▼────┐                                          │
    │   │ [4. Sync    │                                          │
    │   │  from       │                                          │
    │   │  roadmap]   │                                          │
    │   │  (US-027)   │                                          │
    │   └────┬────────┘                                          │
    │        │                                                   │
    │        └──[5. Continue with updated priorities]           │
    │                                                             │
    │   Result: Real-time visibility and early course            │
    │           correction without waiting for PR merge          │
    └─────────────────────────────────────────────────────────────┘

Benefits:
    For code_developer (daemon):
    - ✅ Always works on latest priorities
    - ✅ Never wastes time on obsolete tasks
    - ✅ Frequent checkpoints for recovery

    For project_manager (user):
    - ✅ Real-time visibility into progress
    - ✅ Can provide feedback early
    - ✅ No surprises at PR time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Features:
    - Crash Recovery: Automatic recovery from crashes (max 3 attempts)
    - Context Management: Periodic context refresh (every 10 iterations)
    - Status Tracking: Real-time status reporting via data/developer_status.json
    - Retry Logic: Smart retry with max attempts per priority
    - Notifications: Bidirectional communication with user
    - Auto-approval Mode: Fully autonomous operation
    - PR Creation: Automatic pull request generation
    - Roadmap Sync: Always syncs with origin/roadmap (US-027)

Prerequisites:
    - ANTHROPIC_API_KEY environment variable (for API mode)
    - Claude CLI installed (for CLI mode)
    - Git repository with remote
    - docs/roadmap/ROADMAP.md exists
    - Clean working directory
    - 'roadmap' branch exists and is up to date

Usage Examples:
    Basic usage (autonomous mode):
    >>> daemon = DevDaemon(auto_approve=True)
    >>> daemon.run()  # Runs until all priorities complete

    With user approval:
    >>> daemon = DevDaemon(auto_approve=False)
    >>> daemon.run()  # Asks for approval before each priority

    Using Claude CLI (subscription):
    >>> daemon = DevDaemon(use_claude_cli=True, claude_cli_path="/path/to/claude")
    >>> daemon.run()

    Custom crash recovery:
    >>> daemon = DevDaemon(max_crashes=5, crash_sleep_interval=120)
    >>> daemon.run()

Status Tracking:
    The daemon writes status to ~/.coffee_maker/daemon_status.json
    which project-manager reads to display current progress.

    Use `project-manager developer-status` to view daemon status.

Configuration:
    - roadmap_path: Path to ROADMAP.md (default: docs/roadmap/ROADMAP.md)
    - auto_approve: Auto-approve without confirmation (default: True)
    - create_prs: Create PRs automatically (default: True)
    - sleep_interval: Seconds between iterations (default: 30)
    - model: Claude model to use (default: sonnet)
    - max_crashes: Max crashes before stopping (default: 3)
    - compact_interval: Iterations between context resets (default: 10)
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from coffee_maker.autonomous.daemon_git_ops import GitOpsMixin
from coffee_maker.autonomous.daemon_implementation import ImplementationMixin
from coffee_maker.autonomous.daemon_spec_manager import SpecManagerMixin
from coffee_maker.autonomous.daemon_status import StatusMixin
from coffee_maker.autonomous.developer_status import (
    ActivityType,
    DeveloperState,
    DeveloperStatus,
)
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.task_metrics import TaskMetricsDB
from coffee_maker.cli.notifications import (
    NotificationDB,
)
from coffee_maker.integrations.slack import DailySummaryScheduler, SlackNotifier

# ACE Framework (optional, only loaded if enabled)
try:
    from coffee_maker.autonomous.ace import ACEGenerator
    from coffee_maker.autonomous.ace.config import get_default_config
    from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader

    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False
    logger.warning("ACE framework not available - continuing without it")

# Lazy imports for expensive modules (only loaded when needed)
if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class DevDaemon(GitOpsMixin, SpecManagerMixin, ImplementationMixin, StatusMixin):
    """Autonomous development daemon (minimal MVP).

    This daemon continuously reads ROADMAP.md and autonomously implements
    features by invoking Claude API. It follows a simple loop:

    1. Parse ROADMAP.md for next planned priority
    2. Create feature branch
    3. Execute Claude API with implementation prompt
    4. Commit changes with proper message
    5. Push and create PR
    6. Update ROADMAP status (via notification)
    7. Sleep and repeat

    Composed from mixins:
        - GitOpsMixin: Git synchronization and branch operations
        - SpecManagerMixin: Technical specification management
        - ImplementationMixin: Priority implementation orchestration
        - StatusMixin: Status tracking and notifications

    Attributes:
        roadmap_path: Path to ROADMAP.md
        auto_approve: Whether to auto-approve without user confirmation
        create_prs: Whether to create PRs automatically
        sleep_interval: Seconds to sleep between iterations

    Example:
        >>> daemon = DevDaemon(
        ...     roadmap_path="docs/roadmap/ROADMAP.md",
        ...     auto_approve=False,  # Ask user before starting
        ...     create_prs=True
        ... )
        >>> daemon.run()  # Runs until all priorities complete
    """

    def __init__(
        self,
        roadmap_path: str = "docs/roadmap/ROADMAP.md",
        auto_approve: bool = True,  # BUG FIX: Should be autonomous by default
        create_prs: bool = True,
        sleep_interval: int = 30,
        model: str = "sonnet",
        use_claude_cli: bool = False,
        claude_cli_path: str = "/opt/homebrew/bin/claude",
        # PRIORITY 2.7: Crash recovery parameters
        max_crashes: int = 3,
        crash_sleep_interval: int = 60,
        compact_interval: int = 10,
    ) -> None:
        """Initialize development daemon.

        CRITICAL: Only ONE code_developer (DevDaemon) can run at a time.
        This is enforced via AgentRegistry to prevent parallel implementations.

        Args:
            roadmap_path: Path to ROADMAP.md
            auto_approve: Auto-approve implementation (skip user confirmation)
            create_prs: Create pull requests automatically
            sleep_interval: Seconds between iterations (default: 30)
            model: Claude model to use (default: claude-sonnet-4)
            use_claude_cli: Use Claude CLI instead of Anthropic API (default: False)
            claude_cli_path: Path to claude CLI executable (default: /opt/homebrew/bin/claude)
            max_crashes: Maximum consecutive crashes before stopping (default: 3)
            crash_sleep_interval: Sleep duration after crash in seconds (default: 60)
            compact_interval: Iterations between context resets (default: 10)

        Raises:
            RuntimeError: If another code_developer is already running
        """
        # CRITICAL: Check if another code_developer is already running
        # We need to track this separately since AgentRegistry can't be used during __init__
        if hasattr(DevDaemon, "_daemon_instance_running"):
            raise RuntimeError(
                "❌ CRITICAL: Another code_developer is already running! "
                "Only ONE code_developer instance allowed at a time. "
                "Kill the other instance first (use 'ps aux | grep code-developer')."
            )

        # Mark that a daemon instance is now running
        DevDaemon._daemon_instance_running = True

        logger.info("✅ code_developer started (singleton confirmed)")

        self.roadmap_path = Path(roadmap_path)
        self.auto_approve = auto_approve
        self.create_prs = create_prs
        self.sleep_interval = sleep_interval
        self.model = model
        self.use_claude_cli = use_claude_cli

        # Initialize components
        self.parser = RoadmapParser(str(self.roadmap_path))
        self.git = GitManager()

        # Choose between CLI and API based on flag (lazy import)
        if use_claude_cli:
            # Lazy import: only load when using CLI mode
            from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

            self.claude = ClaudeCLIInterface(claude_path=claude_cli_path, model=model)
            logger.info("✅ Using Claude CLI mode (subscription)")
        else:
            # Lazy import: only load when using API mode
            from coffee_maker.autonomous.claude_api_interface import ClaudeAPI

            self.claude = ClaudeAPI(model=model)
            logger.info("✅ Using Claude API mode (requires credits)")

        self.notifications = NotificationDB()

        # PRIORITY 4: Developer status tracking
        self.status = DeveloperStatus()

        # Task metrics database for performance tracking
        self.metrics_db = TaskMetricsDB()

        # US-034: Slack integration (graceful degradation if not configured)
        self.slack = SlackNotifier()
        if self.slack.is_enabled():
            logger.info("✅ Slack notifications enabled")
        else:
            logger.debug("Slack notifications disabled (not configured or SLACK_ENABLED=false)")

        # US-034: Daily summary scheduler
        self.daily_summary_scheduler = DailySummaryScheduler(notifier=self.slack, roadmap_path=str(self.roadmap_path))
        logger.info(f"Daily summary scheduler initialized (time: {self.daily_summary_scheduler.summary_time})")

        # ACE Framework integration (optional)
        self.ace_enabled = self._init_ace_framework()

        # State
        self.running = False
        self.attempted_priorities = {}  # Track retry attempts: {priority_name: count}
        self.max_retries = 3  # Maximum attempts before skipping a priority

        # PRIORITY 2.8: Status reporting state
        self.start_time = None
        self.iteration_count = 0
        self.current_priority_start_time = None
        self.current_priority_info = None  # Store current priority for metrics recording

        # Subtask tracking for status bar display
        self.current_subtasks = []  # List of {name, status, duration_seconds, estimated_seconds}

        # PRIORITY 2.7: Crash recovery state
        self.max_crashes = max_crashes
        self.crash_sleep_interval = crash_sleep_interval
        self.crash_count = 0
        self.crash_history = []  # List of crash info dicts

        # PRIORITY 2.7: Context management state
        self.compact_interval = compact_interval
        self.iterations_since_compact = 0
        self.last_compact_time = None

        logger.info("DevDaemon initialized")
        logger.info(f"Roadmap: {self.roadmap_path}")
        logger.info(f"Auto-approve: {self.auto_approve}")
        logger.info(f"Create PRs: {self.create_prs}")
        logger.info(f"Max crashes: {self.max_crashes}")
        logger.info(f"Compact interval: {self.compact_interval} iterations")

    def run(self):
        """Run daemon main loop.

        This method runs continuously until:
        - All planned priorities are complete
        - User stops the daemon (Ctrl+C)
        - Fatal error occurs

        Example:
            >>> daemon = DevDaemon()
            >>> daemon.run()  # Runs until complete
        """
        self.running = True
        self.start_time = datetime.now()
        logger.info("🤖 DevDaemon starting...")

        # PRIORITY 4: Set initial status
        self.status.update_status(DeveloperState.IDLE, current_step="Starting daemon")

        # Check prerequisites
        if not self._check_prerequisites():
            logger.error("Prerequisites not met - cannot start")

            # US-034: Alert about prerequisite failure
            try:
                self.slack.notify_system_alert(
                    level="error",
                    title="Daemon failed to start",
                    message="Prerequisites check failed - daemon cannot start",
                    context={"action": "Check logs for details"},
                )
            except Exception as e:
                logger.warning(f"Failed to send Slack system_alert: {e}")

            return

        # PRIORITY 2.8: Write initial status
        self._write_status()

        # US-034: Start daily summary scheduler
        try:
            self.daily_summary_scheduler.start()
        except Exception as e:
            logger.warning(f"Failed to start daily summary scheduler: {e}")

        # US-034: Notify Slack about daemon start
        try:
            current_branch = self.git.get_current_branch()
            next_priority = self.parser.get_next_planned_priority()
            next_priority_name = next_priority.get("name") if next_priority else None
            self.slack.notify_daemon_started(branch=current_branch, next_priority=next_priority_name)
        except Exception as e:
            logger.warning(f"Failed to send Slack daemon_started notification: {e}")

        iteration = 0

        while self.running:
            iteration += 1
            self.iteration_count = iteration
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration} | Crashes: {self.crash_count}/{self.max_crashes}")
            logger.info(f"{'='*60}")

            # PRIORITY 2.8: Write status at start of iteration
            self._write_status()

            try:
                # PRIORITY 2.7: Crash recovery - reset context after crash
                if self.crash_count > 0:
                    logger.warning(f"🔄 Recovering from crash #{self.crash_count}")
                    if self._reset_claude_context():
                        logger.info("✅ Context reset successful")
                        # Reset crash count only after successful recovery
                        self.crash_count = 0
                    else:
                        logger.error("Failed to reset context - continuing anyway")

                # PRIORITY 2.7: Periodic context refresh
                if self.iterations_since_compact >= self.compact_interval:
                    logger.info(f"🔄 Periodic context refresh (every {self.compact_interval} iterations)")
                    if self._reset_claude_context():
                        self.iterations_since_compact = 0
                        logger.info("✅ Periodic refresh complete")

                # BUG FIX #2: Sync roadmap branch BEFORE reading priorities
                logger.info("🔄 Syncing with 'roadmap' branch...")
                if not self._sync_roadmap_branch():
                    logger.warning("⚠️  Roadmap sync failed - continuing with local version")

                    # US-034: Alert about sync failure (warning level)
                    try:
                        self.slack.notify_system_alert(
                            level="warning",
                            title="Roadmap sync failed",
                            message="Failed to sync with remote roadmap branch - using local version",
                            context={"action": "Continuing with local ROADMAP.md"},
                        )
                    except Exception as e:
                        logger.debug(f"Failed to send Slack system_alert: {e}")

                # Reload roadmap
                self.parser = RoadmapParser(str(self.roadmap_path))

                # PRIORITY 4: Update status - analyzing roadmap
                self.status.update_status(DeveloperState.THINKING, current_step="Analyzing ROADMAP.md")

                # Get next task
                next_priority = self.parser.get_next_planned_priority()

                if not next_priority:
                    logger.info("✅ No more planned priorities - all done!")
                    self._notify_completion()
                    # PRIORITY 4: Return to idle when done
                    self.status.update_status(DeveloperState.IDLE, current_step="All priorities complete")

                    # US-034: Notify Slack about completion
                    try:
                        runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
                        self.slack.notify_daemon_stopped(
                            runtime_hours=runtime_hours,
                            priorities_completed=self.iteration_count,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send Slack daemon_stopped notification: {e}")

                    break

                logger.info(f"📋 Next priority: {next_priority['name']} - {next_priority['title']}")

                # PRIORITY 2.8: Update status with current priority
                self.current_priority_start_time = datetime.now()
                self._write_status(priority=next_priority)

                # BUG FIX #3 & #4: Check for technical spec, create if missing
                if not self._ensure_technical_spec(next_priority):
                    logger.warning("⚠️  Could not ensure technical spec exists - skipping this priority")

                    # US-034: Alert about missing spec
                    try:
                        self.slack.notify_system_alert(
                            level="warning",
                            title=f"Missing technical spec for {next_priority['name']}",
                            message=f"Could not create or find technical spec - skipping priority",
                            context={
                                "priority": next_priority["name"],
                                "action": "Check logs and ROADMAP.md for details",
                            },
                        )
                    except Exception as e:
                        logger.debug(f"Failed to send Slack system_alert: {e}")

                    time.sleep(self.sleep_interval)
                    continue

                # Ask for approval if needed
                if not self.auto_approve:
                    # PRIORITY 4: Set blocked while waiting for approval
                    self.status.add_question(
                        question_id=f"approve_{next_priority['name']}",
                        question_type="implementation_approval",
                        message=f"Approve implementation of {next_priority['name']}?",
                        context=f"Priority: {next_priority['title']}",
                    )

                    if not self._request_approval(next_priority):
                        logger.info("User declined - waiting for next iteration")
                        # Remove question since it was answered (declined)
                        self.status.remove_question(f"approve_{next_priority['name']}")
                        time.sleep(self.sleep_interval)
                        continue

                    # Remove question since it was approved
                    self.status.remove_question(f"approve_{next_priority['name']}")

                # PRIORITY 4: Update status - working on implementation
                task_info = {
                    "priority": next_priority.get("number", 0),
                    "name": f"{next_priority['name']}: {next_priority['title']}",
                }
                self.status.update_status(
                    DeveloperState.WORKING,
                    task=task_info,
                    progress=0,
                    current_step="Starting implementation",
                )

                # Execute implementation
                success = self._implement_priority(next_priority)

                if success:
                    logger.info(f"✅ Successfully implemented {next_priority['name']}")
                    # PRIORITY 4: Mark task as completed
                    self.status.task_completed()
                    # PRIORITY 2.7: Increment iteration counter only on success
                    self.iterations_since_compact += 1
                    # PRIORITY 2.8: Write status after completion
                    self._write_status(priority=next_priority)

                    # US-034: Notify Slack about priority completion
                    try:
                        # Calculate metrics
                        if self.current_priority_start_time:
                            duration_hours = (datetime.now() - self.current_priority_start_time).total_seconds() / 3600
                        else:
                            duration_hours = 0.0

                        # Get git stats
                        try:
                            stats = self.git.get_stats()
                            files_changed = stats.get("files_changed", 0)
                            lines_added = stats.get("lines_added", 0)
                            lines_deleted = stats.get("lines_deleted", 0)
                        except Exception:
                            files_changed = 0
                            lines_added = 0
                            lines_deleted = 0

                        # Try to extract tests added (optional)
                        tests_added = 0
                        try:
                            # Count test files in diff
                            diff_output = self.git.run_command("git diff HEAD~1 --name-only | grep test_")
                            if diff_output:
                                tests_added = len(diff_output.strip().split("\n"))
                        except Exception:
                            pass

                        self.slack.notify_priority_completed(
                            priority_name=next_priority["name"],
                            summary=next_priority.get("title", "Implementation completed"),
                            duration_hours=round(duration_hours, 2),
                            files_changed=files_changed,
                            tests_added=tests_added,
                            lines_added=lines_added,
                            lines_deleted=lines_deleted,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send Slack priority_completed notification: {e}")

                    # US-029: CRITICAL - Merge to roadmap after successful implementation
                    logger.info(f"📤 Merging {next_priority['name']} to roadmap for project_manager visibility...")
                    self._merge_to_roadmap(f"Completed {next_priority['name']}")

                    # PRIORITY 4: Return to idle after task complete
                    self.status.update_status(
                        DeveloperState.IDLE,
                        current_step="Task completed, waiting for next",
                    )
                else:
                    logger.warning(f"⚠️  Implementation failed for {next_priority['name']}")
                    # PRIORITY 4: Log error activity
                    self.status.report_activity(
                        ActivityType.ERROR_ENCOUNTERED,
                        f"Implementation failed for {next_priority['name']}",
                        details={"priority": next_priority["name"]},
                    )

                # US-029: CRITICAL - Merge to roadmap before sleep so project_manager has visibility
                logger.info("📤 Merging progress to roadmap before sleep...")
                self._merge_to_roadmap("End of iteration checkpoint")

                # Sleep before next iteration
                logger.info(f"💤 Sleeping {self.sleep_interval}s before next iteration...")
                time.sleep(self.sleep_interval)

            except KeyboardInterrupt:
                logger.info("\n⏹️  Daemon stopped by user")
                self.running = False

                # US-034: Notify Slack about stop
                try:
                    runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
                    self.slack.notify_daemon_stopped(
                        runtime_hours=runtime_hours,
                        priorities_completed=self.iteration_count,
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Slack daemon_stopped notification: {e}")

                # CRITICAL: Release singleton lock
                if hasattr(DevDaemon, "_daemon_instance_running"):
                    delattr(DevDaemon, "_daemon_instance_running")
                    logger.info("✅ Singleton lock released")
                break

            except Exception as e:
                # PRIORITY 2.7: Enhanced crash recovery
                self.crash_count += 1
                crash_info = {
                    "timestamp": datetime.now().isoformat(),
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                    "priority": (
                        next_priority.get("name") if "next_priority" in locals() and next_priority else "Unknown"
                    ),
                    "iteration": iteration,
                }
                self.crash_history.append(crash_info)

                logger.error(f"❌ CRASH #{self.crash_count}/{self.max_crashes}: {e}")
                logger.error(f"Priority: {crash_info['priority']}")
                import traceback

                traceback.print_exc()

                # US-034: Notify Slack about error
                try:
                    self.slack.notify_daemon_error(
                        error=e,
                        context={
                            "priority": crash_info["priority"],
                            "crash_count": self.crash_count,
                            "max_crashes": self.max_crashes,
                            "iteration": iteration,
                        },
                    )
                except Exception as slack_err:
                    logger.warning(f"Failed to send Slack daemon_error notification: {slack_err}")

                # PRIORITY 4: Log crash as error activity
                self.status.report_activity(
                    ActivityType.ERROR_ENCOUNTERED,
                    f"Daemon crashed: {type(e).__name__}",
                    details={
                        "exception": str(e)[:200],
                        "crash_count": self.crash_count,
                    },
                )

                # PRIORITY 2.8: Write status after crash
                priority_context = next_priority if "next_priority" in locals() else None
                self._write_status(priority=priority_context)

                # Check if max crashes reached
                if self.crash_count >= self.max_crashes:
                    logger.critical(f"🚨 MAX CRASHES REACHED ({self.max_crashes}) - STOPPING DAEMON")
                    self._notify_persistent_failure(crash_info)
                    self.running = False
                    # CRITICAL: Release singleton lock
                    if hasattr(DevDaemon, "_daemon_instance_running"):
                        delattr(DevDaemon, "_daemon_instance_running")
                        logger.info("✅ Singleton lock released")
                    break

                # Sleep longer after crash
                logger.info(f"💤 Sleeping {self.crash_sleep_interval}s after crash before recovery...")
                time.sleep(self.crash_sleep_interval)

        logger.info("🛑 DevDaemon stopped")
        logger.info(f"Total crashes: {len(self.crash_history)}")

        # US-034: Stop daily summary scheduler
        try:
            self.daily_summary_scheduler.stop()
        except Exception as e:
            logger.warning(f"Failed to stop daily summary scheduler: {e}")

        # CRITICAL: Release singleton lock
        if hasattr(DevDaemon, "_daemon_instance_running"):
            delattr(DevDaemon, "_daemon_instance_running")
            logger.info("✅ Singleton lock released")

        # PRIORITY 2.8: Write final status on stop
        self._write_status()

    def _check_prerequisites(self) -> bool:
        """Check if prerequisites are met.

        Returns:
            True if ready to run

        Checks:
            - Claude API available
            - Git repository
            - ROADMAP.md exists
        """
        logger.info("Checking prerequisites...")

        # Check Claude API
        if not self.claude.check_available():
            logger.error("❌ Claude API not available")
            return False

        logger.info("✅ Claude API available")

        # Check Git
        if not self.git.has_remote():
            logger.warning("⚠️  No Git remote configured - PRs will fail")

        logger.info("✅ Git repository ready")

        # Check ROADMAP
        if not self.roadmap_path.exists():
            logger.error(f"❌ ROADMAP not found: {self.roadmap_path}")
            return False

        logger.info("✅ ROADMAP.md found")

        return True

    def _reset_claude_context(self) -> bool:
        """Reset Claude conversation context using /compact.

        This method resets the Claude CLI conversation context to prevent
        token bloat and stale context. It uses the /compact command which
        summarizes the current conversation and starts fresh.

        Returns:
            True if context reset successful, False otherwise

        Implementation:
            1. Check if using Claude CLI (API mode doesn't need reset)
            2. Call claude.reset_context() which executes /compact
            3. Log token savings and new context state
            4. Update last_compact_time timestamp

        Example:
            >>> daemon = DevDaemon(use_claude_cli=True)
            >>> daemon._reset_claude_context()
            True
        """
        # Only applicable for Claude CLI mode
        if not self.use_claude_cli:
            logger.debug("Context reset not needed for API mode")
            return True

        try:
            logger.info("🔄 Resetting Claude context via /compact...")

            # Call reset_context() on claude interface
            result = self.claude.reset_context()

            if result:
                self.last_compact_time = datetime.now()
                logger.info("✅ Context reset successful")
                logger.info(f"Context age: {self.iterations_since_compact} iterations")
                return True
            else:
                logger.error("❌ Context reset failed")
                return False

        except Exception as e:
            logger.error(f"Error resetting context: {e}")
            return False

    def _init_ace_framework(self) -> bool:
        """Initialize ACE framework if enabled.

        NOTE: ACE for code_developer is EXPERIMENTAL and not recommended.

        Reason: code_developer has:
        - Long operations (30min-4hr) → slow learning
        - Delayed feedback → hard to measure success
        - Low volume (5-10/day) → insufficient data

        Better ACE candidates:
        - user_listener: Fast (< 10s), high volume (50-100/day), immediate feedback ⭐ BEST
        - assistant: Fast (10-30s), good volume (20-50/day), quick feedback
        - code-searcher: Fast (5-30s), moderate volume (10-20/day), clear success

        Consider using ACE for those agents first, then code_developer later
        after the framework is proven and refined.

        Returns:
            True if ACE is enabled and initialized, False otherwise
        """
        if not ACE_AVAILABLE:
            logger.info("ACE framework not available")
            return False

        # Check if ACE is enabled via environment variable (agent-specific)
        ace_enabled = os.getenv("ACE_ENABLED_CODE_DEVELOPER", "false").lower() == "true"

        if not ace_enabled:
            logger.info("ACE framework disabled for code_developer " "(set ACE_ENABLED_CODE_DEVELOPER=true to enable)")
            logger.info("⚠️  NOTE: ACE for code_developer is EXPERIMENTAL - " "consider user_listener first")
            return False

        logger.warning("⚠️  Using ACE for code_developer (EXPERIMENTAL)")
        logger.warning("   This agent has slow feedback loops and low volume")
        logger.warning("   Consider using ACE for user_listener/assistant instead")

        try:
            # Initialize ACE components
            config = get_default_config()
            config.ensure_directories()

            self.ace_config = config
            self.ace_generator = ACEGenerator(
                agent_interface=self.claude,
                config=config,
                agent_name="code_developer",
                agent_objective="Implement features from ROADMAP autonomously",
                success_criteria="Code runs, tests pass, DoD verified, PR created",
            )

            # Load current playbook for context
            self.ace_loader = PlaybookLoader(agent_name="code_developer", config=config)

            logger.info("✅ ACE Framework enabled")
            logger.info(f"   Trace dir: {config.trace_dir}")
            logger.info(f"   Delta dir: {config.delta_dir}")
            logger.info(f"   Playbook dir: {config.playbook_dir}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize ACE framework: {e}")
            return False

    def _get_ace_context(self) -> str:
        """Get current ACE playbook as context.

        Returns:
            Playbook markdown if available, empty string otherwise
        """
        if not self.ace_enabled or not hasattr(self, "ace_loader"):
            return ""

        try:
            playbook = self.ace_loader.load()
            return self.ace_loader.to_markdown(playbook)
        except FileNotFoundError:
            logger.debug("No playbook found yet - will be created after first curation")
            return ""
        except Exception as e:
            logger.warning(f"Failed to load playbook: {e}")
            return ""

    def stop(self):
        """Stop the daemon gracefully."""
        logger.info("Stopping daemon...")
        self.running = False

        # CRITICAL: Release singleton lock so another daemon can start
        if hasattr(DevDaemon, "_daemon_instance_running"):
            delattr(DevDaemon, "_daemon_instance_running")
            logger.info("✅ Singleton lock released")
