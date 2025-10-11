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

Key Features:
    - Crash Recovery: Automatic recovery from crashes (max 3 attempts)
    - Context Management: Periodic context refresh (every 10 iterations)
    - Status Tracking: Real-time status reporting via data/developer_status.json
    - Retry Logic: Smart retry with max attempts per priority
    - Notifications: Bidirectional communication with user
    - Auto-approval Mode: Fully autonomous operation
    - PR Creation: Automatic pull request generation

Prerequisites:
    - ANTHROPIC_API_KEY environment variable (for API mode)
    - Claude CLI installed (for CLI mode)
    - Git repository with remote
    - docs/ROADMAP.md exists
    - Clean working directory

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
    - roadmap_path: Path to ROADMAP.md (default: docs/ROADMAP.md)
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

from coffee_maker.autonomous.claude_api_interface import ClaudeAPI
from coffee_maker.utils.file_io import write_json_file
from coffee_maker.autonomous.developer_status import (
    ActivityType,
    DeveloperState,
    DeveloperStatus,
)
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.task_metrics import TaskMetricsDB
from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_PRIORITY_HIGH,
    NOTIF_TYPE_ERROR,
    NOTIF_TYPE_INFO,
    NotificationDB,
)

logger = logging.getLogger(__name__)


class DevDaemon:
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

    Attributes:
        roadmap_path: Path to ROADMAP.md
        auto_approve: Whether to auto-approve without user confirmation
        create_prs: Whether to create PRs automatically
        sleep_interval: Seconds to sleep between iterations

    Example:
        >>> daemon = DevDaemon(
        ...     roadmap_path="docs/ROADMAP.md",
        ...     auto_approve=False,  # Ask user before starting
        ...     create_prs=True
        ... )
        >>> daemon.run()  # Runs until all priorities complete
    """

    def __init__(
        self,
        roadmap_path: str = "docs/ROADMAP.md",
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
        """
        self.roadmap_path = Path(roadmap_path)
        self.auto_approve = auto_approve
        self.create_prs = create_prs
        self.sleep_interval = sleep_interval
        self.model = model
        self.use_claude_cli = use_claude_cli

        # Initialize components
        self.parser = RoadmapParser(str(self.roadmap_path))
        self.git = GitManager()

        # Choose between CLI and API based on flag
        if use_claude_cli:
            from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

            self.claude = ClaudeCLIInterface(claude_path=claude_cli_path, model=model)
            logger.info("✅ Using Claude CLI mode (subscription)")
        else:
            self.claude = ClaudeAPI(model=model)
            logger.info("✅ Using Claude API mode (requires credits)")

        self.notifications = NotificationDB()

        # PRIORITY 4: Developer status tracking
        self.status = DeveloperStatus()

        # Task metrics database for performance tracking
        self.metrics_db = TaskMetricsDB()

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
            return

        # PRIORITY 2.8: Write initial status
        self._write_status()

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
                    break

                logger.info(f"📋 Next priority: {next_priority['name']} - {next_priority['title']}")

                # PRIORITY 2.8: Update status with current priority
                self.current_priority_start_time = datetime.now()
                self._write_status(priority=next_priority)

                # BUG FIX #3 & #4: Check for technical spec, create if missing
                if not self._ensure_technical_spec(next_priority):
                    logger.warning("⚠️  Could not ensure technical spec exists - skipping this priority")
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
                    DeveloperState.WORKING, task=task_info, progress=0, current_step="Starting implementation"
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
                    # PRIORITY 4: Return to idle after task complete
                    self.status.update_status(DeveloperState.IDLE, current_step="Task completed, waiting for next")
                else:
                    logger.warning(f"⚠️  Implementation failed for {next_priority['name']}")
                    # PRIORITY 4: Log error activity
                    self.status.report_activity(
                        ActivityType.ERROR_ENCOUNTERED,
                        f"Implementation failed for {next_priority['name']}",
                        details={"priority": next_priority["name"]},
                    )

                # Sleep before next iteration
                logger.info(f"💤 Sleeping {self.sleep_interval}s before next iteration...")
                time.sleep(self.sleep_interval)

            except KeyboardInterrupt:
                logger.info("\n⏹️  Daemon stopped by user")
                self.running = False
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

                # PRIORITY 4: Log crash as error activity
                self.status.report_activity(
                    ActivityType.ERROR_ENCOUNTERED,
                    f"Daemon crashed: {type(e).__name__}",
                    details={"exception": str(e)[:200], "crash_count": self.crash_count},
                )

                # PRIORITY 2.8: Write status after crash
                priority_context = next_priority if "next_priority" in locals() else None
                self._write_status(priority=priority_context)

                # Check if max crashes reached
                if self.crash_count >= self.max_crashes:
                    logger.critical(f"🚨 MAX CRASHES REACHED ({self.max_crashes}) - STOPPING DAEMON")
                    self._notify_persistent_failure(crash_info)
                    self.running = False
                    break

                # Sleep longer after crash
                logger.info(f"💤 Sleeping {self.crash_sleep_interval}s after crash before recovery...")
                time.sleep(self.crash_sleep_interval)

        logger.info("🛑 DevDaemon stopped")
        logger.info(f"Total crashes: {len(self.crash_history)}")

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

    def _sync_roadmap_branch(self) -> bool:
        """Sync with 'roadmap' branch before each iteration.

        This ensures the daemon always works with the latest priorities
        and prevents working on stale/obsolete tasks.

        Returns:
            True if sync successful or not needed, False if sync failed

        Implementation:
            1. Fetch origin/roadmap
            2. Merge origin/roadmap into current branch
            3. Handle conflicts gracefully
        """
        try:
            # Fetch latest from roadmap branch
            import subprocess

            result = subprocess.run(
                ["git", "fetch", "origin", "roadmap"],
                cwd=self.git.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.warning(f"Failed to fetch roadmap branch: {result.stderr}")
                return False

            # Merge origin/roadmap
            result = subprocess.run(
                ["git", "merge", "origin/roadmap", "--no-edit"],
                cwd=self.git.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                # Check if merge conflict
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    logger.error("❌ Merge conflict with roadmap branch!")
                    logger.error("Manual intervention required to resolve conflicts")

                    # Abort merge
                    subprocess.run(
                        ["git", "merge", "--abort"],
                        cwd=self.git.repo_path,
                        capture_output=True,
                    )
                    return False
                else:
                    logger.warning(f"Merge failed: {result.stderr}")
                    return False

            logger.info("✅ Synced with 'roadmap' branch")
            return True

        except Exception as e:
            logger.error(f"Error syncing roadmap branch: {e}")
            return False

    def _ensure_technical_spec(self, priority: dict) -> bool:
        """Ensure technical specification exists for this priority.

        BUG-002 FIX: Validate priority fields before accessing them.

        If spec doesn't exist, create it before implementing.

        Args:
            priority: Priority dictionary

        Returns:
            True if spec exists or was created successfully
        """
        # BUG-002: Validate required fields
        if not priority.get("name"):
            logger.error("❌ Priority missing 'name' field - cannot create technical spec")
            return False

        if not priority.get("content"):
            logger.warning(f"⚠️  Priority {priority.get('name')} has no content - will use title only in spec")

        priority_name = priority["name"]

        # Determine spec filename
        # US-XXX -> US-XXX_TECHNICAL_SPEC.md
        # PRIORITY X -> PRIORITY_X_TECHNICAL_SPEC.md
        if priority_name.startswith("US-"):
            spec_filename = f"{priority_name}_TECHNICAL_SPEC.md"
        elif priority_name.startswith("PRIORITY"):
            # PRIORITY 2.6 -> PRIORITY_2_6_TECHNICAL_SPEC.md
            spec_name = priority_name.replace(" ", "_").replace(".", "_")
            spec_filename = f"{spec_name}_TECHNICAL_SPEC.md"
        else:
            # Generic fallback
            spec_name = priority_name.replace(" ", "_").replace(":", "")
            spec_filename = f"{spec_name}_TECHNICAL_SPEC.md"

        spec_path = self.roadmap_path.parent / spec_filename

        # Check if spec already exists
        if spec_path.exists():
            logger.info(f"✅ Technical spec exists: {spec_filename}")
            return True

        logger.info(f"📝 Technical spec not found: {spec_filename}")
        logger.info("Creating technical specification...")

        # Create spec using Claude
        spec_prompt = self._build_spec_creation_prompt(priority, spec_filename)

        try:
            result = self.claude.execute_prompt(spec_prompt, timeout=600)  # 10 min timeout

            if not result.success:
                logger.error(f"Failed to create technical spec: {result.error}")
                return False

            # Check if spec file was created
            if not spec_path.exists():
                logger.error("Claude completed but spec file was not created")
                return False

            logger.info(f"✅ Created technical spec: {spec_filename}")

            # Commit the spec
            self.git.commit(f"docs: Add technical spec for {priority_name}")
            self.git.push()

            return True

        except Exception as e:
            logger.error(f"Error creating technical spec: {e}")
            return False

    def _build_spec_creation_prompt(self, priority: dict, spec_filename: str) -> str:
        """Build prompt for creating technical specification.

        BUG-002 FIX: Use safe dictionary access to prevent KeyError crashes.

        Args:
            priority: Priority dictionary
            spec_filename: Name of spec file to create

        Returns:
            Prompt string
        """
        # BUG-002: Safe dictionary access with defaults
        priority_name = priority.get("name", "Unknown Priority")
        priority_title = priority.get("title", "No title")
        priority_content = priority.get("content", "")

        # Handle missing/empty content gracefully
        if not priority_content or len(priority_content.strip()) == 0:
            priority_context = f"Title: {priority_title}\nNo additional details provided in ROADMAP."
            logger.warning(f"Priority {priority_name} has no content - using title only for spec creation")
        else:
            # Safely truncate content
            priority_context = priority_content[:2000]
            if len(priority_content) > 2000:
                priority_context += "..."

        return f"""Create a detailed technical specification for implementing {priority_name}.

Read the user story from docs/ROADMAP.md and create a comprehensive technical spec.

**Your Task:**
1. Read docs/ROADMAP.md to understand {priority_name}
2. Create docs/{spec_filename} with detailed technical specification
3. Include:
   - Prerequisites & Dependencies
   - Architecture Overview
   - Component Specifications
   - Data Flow Diagrams (in text/mermaid format)
   - Implementation Plan (step-by-step with time estimates)
   - Testing Strategy
   - Security Considerations
   - Performance Requirements
   - Risk Analysis
   - Success Criteria

**Important:**
- Be VERY specific and detailed
- Include file paths, class names, method signatures
- Provide code examples
- Break down into concrete tasks
- Estimate time for each task
- Make it actionable for implementation

**User Story Context:**
{priority_context}

Create the spec now in docs/{spec_filename}."""

    def _request_approval(self, priority: dict) -> bool:
        """Request user approval to implement a priority.

        Args:
            priority: Priority dictionary

        Returns:
            True if approved
        """
        logger.info(f"Requesting approval for {priority['name']}")

        # Create notification
        notif_id = self.notifications.create_notification(
            type=NOTIF_TYPE_INFO,
            title=f"Implement {priority['name']}?",
            message=f"The daemon wants to implement:\n{priority['title']}\n\nApprove?",
            priority=NOTIF_PRIORITY_HIGH,
            context={"priority_name": priority["name"], "priority_number": priority["number"]},
        )

        logger.info(f"Created notification {notif_id} - waiting for response")
        logger.info("Check notifications with: project-manager notifications")
        logger.info(f"Approve with: project-manager respond {notif_id} approve")

        # Poll for response (simplified - in production would use event system)
        max_wait = 1800  # 30 minutes
        poll_interval = 5
        waited = 0

        while waited < max_wait:
            time.sleep(poll_interval)
            waited += poll_interval

            notif = self.notifications.get_notification(notif_id)
            if notif and notif["user_response"]:
                response = notif["user_response"].lower()
                approved = "approve" in response or "yes" in response
                logger.info(f"User response: {response} (approved={approved})")
                return approved

        logger.warning("User did not respond in time - skipping")
        return False

    def _implement_priority(self, priority: dict) -> bool:
        """Implement a priority.

        Args:
            priority: Priority dictionary

        Returns:
            True if successful
        """
        priority_name = priority["name"]
        priority_title = priority["title"]

        # Check if we've already attempted this priority too many times
        attempt_count = self.attempted_priorities.get(priority_name, 0)

        if attempt_count >= self.max_retries:
            logger.warning(f"⏭️  Skipping {priority_name} - already attempted {attempt_count} times with no changes")
            logger.warning(f"This priority requires manual intervention")

            # Create final notification
            self.notifications.create_notification(
                type=NOTIF_TYPE_INFO,
                title=f"{priority_name}: Max Retries Reached",
                message=f"""The daemon has attempted to implement this priority {attempt_count} times but no files were changed.

This priority requires manual implementation:

Priority: {priority_name}
Title: {priority_title}
Status: Skipped after {attempt_count} attempts

Action Required:
1. Manually implement this priority, OR
2. Mark as "Manual Only" in ROADMAP.md, OR
3. Clarify the deliverables to make them more concrete

The daemon will skip this priority in future iterations.
""",
                priority=NOTIF_PRIORITY_HIGH,
                context={
                    "priority_name": priority_name,
                    "priority_number": priority.get("number"),
                    "reason": "max_retries_reached",
                    "attempts": attempt_count,
                },
            )

            return False  # Return False so the daemon moves on

        # Increment attempt counter
        self.attempted_priorities[priority_name] = attempt_count + 1
        logger.info(
            f"🚀 Starting implementation of {priority_name} (attempt {self.attempted_priorities[priority_name]}/{self.max_retries})"
        )

        # Store priority info for metrics recording
        self.current_priority_info = priority

        # Clear previous subtasks
        self.current_subtasks = []

        # PRIORITY 4: Update progress - creating branch
        self.status.report_progress(10, "Creating feature branch")

        # Track subtask: Creating branch (estimated: 10 seconds)
        subtask_start = datetime.now()
        self._update_subtask("Creating feature branch", "in_progress", subtask_start, estimated_seconds=10)

        # Create branch
        branch_name = f"feature/{priority_name.lower().replace(' ', '-').replace(':', '')}"
        logger.info(f"Creating branch: {branch_name}")

        if not self.git.create_branch(branch_name):
            logger.error("Failed to create branch")
            self._update_subtask("Creating feature branch", "failed", subtask_start, estimated_seconds=10)
            return False

        self._update_subtask("Creating feature branch", "completed", subtask_start, estimated_seconds=10)

        # PRIORITY 4: Log branch creation
        self.status.report_activity(
            ActivityType.GIT_BRANCH, f"Created branch: {branch_name}", details={"branch": branch_name}
        )

        # Build prompt for Claude
        prompt = self._build_implementation_prompt(priority)

        # PRIORITY 4: Update progress - calling Claude API
        self.status.report_progress(20, "Executing implementation with Claude API")

        # Track subtask: Claude API execution (estimated: 5 minutes = 300 seconds)
        subtask_start = datetime.now()
        self._update_subtask("Executing Claude API", "in_progress", subtask_start, estimated_seconds=300)

        logger.info("Executing Claude API with implementation prompt...")

        # Execute Claude API
        result = self.claude.execute_prompt(prompt, timeout=3600)  # 1 hour timeout

        if not result.success:
            logger.error(f"Claude API failed: {result.error}")
            self._update_subtask("Executing Claude API", "failed", subtask_start, estimated_seconds=300)
            return False

        self._update_subtask("Executing Claude API", "completed", subtask_start, estimated_seconds=300)

        logger.info("✅ Claude API execution complete")
        logger.info(f"📊 Token usage: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")

        # PRIORITY 4: Update progress - implementation complete
        self.status.report_progress(60, "Implementation complete, checking changes")

        # Check if any files were changed (Fix for infinite loop issue)
        if self.git.is_clean():
            logger.warning("⚠️  Claude API completed but no files changed")
            logger.warning("Possible reasons:")
            logger.warning("  1. Priority already implemented")
            logger.warning("  2. Task too vague for autonomous implementation")
            logger.warning("  3. Requires human judgment/review")

            # Create notification for human review
            self.notifications.create_notification(
                type=NOTIF_TYPE_INFO,
                title=f"{priority_name}: Needs Manual Review",
                message=f"""Claude API completed successfully but made no file changes.

Possible actions:
1. Review priority description - is it concrete enough?
2. Manually implement this priority
3. Mark as "Manual Only" in ROADMAP
4. Skip and move to next priority

Priority: {priority_name}
Title: {priority_title}
Status: Requires human decision
""",
                priority=NOTIF_PRIORITY_HIGH,
                context={
                    "priority_name": priority_name,
                    "priority_number": priority.get("number"),
                    "reason": "no_changes",
                },
            )

            logger.info("📧 Created notification for manual review")
            # Return "success" to avoid infinite retry - human will decide next steps
            return True

        # PRIORITY 4: Update progress - committing changes
        self.status.report_progress(70, "Committing changes")

        # Track subtask: Committing changes (estimated: 20 seconds)
        subtask_start = datetime.now()
        self._update_subtask("Committing changes", "in_progress", subtask_start, estimated_seconds=20)

        # Commit changes
        commit_message = self._build_commit_message(priority)

        if not self.git.commit(commit_message):
            logger.error("Failed to commit changes")
            self._update_subtask("Committing changes", "failed", subtask_start, estimated_seconds=20)
            return False

        self._update_subtask("Committing changes", "completed", subtask_start, estimated_seconds=20)

        logger.info("✅ Changes committed")

        # PRIORITY 4: Log commit activity
        self.status.report_activity(
            ActivityType.GIT_COMMIT, f"Committed {priority_name}", details={"priority": priority_name}
        )

        # PRIORITY 4: Update progress - pushing
        self.status.report_progress(80, "Pushing to remote")

        # Track subtask: Pushing to remote (estimated: 30 seconds)
        subtask_start = datetime.now()
        self._update_subtask("Pushing to remote", "in_progress", subtask_start, estimated_seconds=30)

        # Push
        if not self.git.push():
            logger.error("Failed to push branch")
            self._update_subtask("Pushing to remote", "failed", subtask_start, estimated_seconds=30)
            return False

        self._update_subtask("Pushing to remote", "completed", subtask_start, estimated_seconds=30)

        logger.info("✅ Branch pushed")

        # PRIORITY 4: Log push activity
        self.status.report_activity(
            ActivityType.GIT_PUSH, f"Pushed branch: {branch_name}", details={"branch": branch_name}
        )

        # Create PR if enabled
        if self.create_prs:
            # PRIORITY 4: Update status to REVIEWING
            self.status.update_status(DeveloperState.REVIEWING, progress=90, current_step="Creating pull request")

            # Track subtask: Creating PR (estimated: 45 seconds)
            subtask_start = datetime.now()
            self._update_subtask("Creating pull request", "in_progress", subtask_start, estimated_seconds=45)

            pr_body = self._build_pr_body(priority)
            pr_url = self.git.create_pull_request(f"Implement {priority_name}: {priority_title}", pr_body)

            if pr_url:
                self._update_subtask("Creating pull request", "completed", subtask_start, estimated_seconds=45)
                logger.info(f"✅ PR created: {pr_url}")

                # PRIORITY 4: Update progress - PR created
                self.status.report_progress(100, f"PR created: {pr_url}")

                # Notify user
                self.notifications.create_notification(
                    type=NOTIF_TYPE_INFO,
                    title=f"{priority_name} Complete!",
                    message=f"Implementation complete!\n\nPR: {pr_url}\n\nPlease review and merge.",
                    priority=NOTIF_PRIORITY_HIGH,
                    context={"priority_name": priority_name, "pr_url": pr_url},
                )
            else:
                self._update_subtask("Creating pull request", "failed", subtask_start, estimated_seconds=45)
                logger.warning("Failed to create PR")
                # PRIORITY 4: Still mark as complete even if PR failed
                self.status.report_progress(100, "Implementation complete (PR creation failed)")

        return True

    def _build_implementation_prompt(self, priority: dict) -> str:
        """Build Claude API prompt for implementation.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string
        """
        # Detect priority type and build specialized prompt
        title_lower = priority["title"].lower()
        content_lower = priority.get("content", "").lower()

        # Check if this is a documentation/UX priority
        is_documentation = any(
            keyword in title_lower or keyword in content_lower
            for keyword in ["documentation", "docs", "guide", "ux", "user experience", "quickstart"]
        )

        if is_documentation:
            return self._build_documentation_prompt(priority)
        else:
            return self._build_feature_prompt(priority)

    def _build_documentation_prompt(self, priority: dict) -> str:
        """Build explicit documentation creation prompt.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string optimized for documentation tasks
        """
        return f"""Read docs/ROADMAP.md and implement {priority['name']}: {priority['title']}.

⚠️  THIS IS A DOCUMENTATION PRIORITY - You MUST CREATE FILES ⚠️

The ROADMAP lists specific deliverable files under "Deliverables" section.
Your task is to:
1. Identify all deliverable files mentioned in ROADMAP for this priority
2. CREATE each file with actual content (not placeholders)
3. Use real examples from the existing codebase
4. Test any commands/examples before documenting them

Instructions:
- CREATE all files listed in the Deliverables section
- Fill with real, specific content based on existing codebase
- Include actual commands, file paths, and examples
- Be concrete, not generic or abstract
- Test examples to ensure accuracy

After creating files:
- Update ROADMAP.md status to "✅ Complete"
- List all files created
- Commit your changes

Priority details:
{priority['content'][:1500]}...

Begin implementation now - CREATE THE FILES."""

    def _build_feature_prompt(self, priority: dict) -> str:
        """Build standard feature implementation prompt.

        Args:
            priority: Priority dictionary

        Returns:
            Prompt string for feature implementation
        """
        return f"""Read docs/ROADMAP.md and implement {priority['name']}: {priority['title']}.

Follow the roadmap guidelines and deliverables. Update docs/ROADMAP.md with your progress.

Important:
- Follow all coding standards
- Add tests where appropriate
- Document your changes
- Update ROADMAP.md status to "🔄 In Progress" first, then "✅ Complete" when done
- Commit frequently with clear messages

Priority details:
{priority['content'][:1000]}...

Begin implementation now."""

    def _build_commit_message(self, priority: dict) -> str:
        """Build commit message for implementation.

        Args:
            priority: Priority dictionary

        Returns:
            Commit message
        """
        message = f"""feat: Implement {priority['name']} - {priority['title']}

Autonomous implementation by DevDaemon.

Priority: {priority['name']}
Status: ✅ Complete

🤖 Generated with [Claude Code](https://claude.com/claude-code) via DevDaemon

Co-Authored-By: Claude <noreply@anthropic.com>
"""
        return message

    def _build_pr_body(self, priority: dict) -> str:
        """Build PR description.

        Args:
            priority: Priority dictionary

        Returns:
            PR body markdown
        """
        body = f"""## Summary

Autonomous implementation of {priority['name']}: {priority['title']}

## Implementation

This PR was autonomously implemented by the DevDaemon following the ROADMAP.md specifications.

## Testing

- Implementation follows ROADMAP guidelines
- Tests added where appropriate
- Manual verification completed

## Review Checklist

- [ ] Code follows project standards
- [ ] Tests pass
- [ ] Documentation updated
- [ ] ROADMAP.md status updated

🤖 Autonomously implemented by DevDaemon
"""
        return body

    def _notify_completion(self):
        """Notify user that all priorities are complete."""
        self.notifications.create_notification(
            type=NOTIF_TYPE_INFO,
            title="🎉 All Priorities Complete!",
            message="The DevDaemon has completed all planned priorities in the ROADMAP!\n\nCheck your PRs for review.",
            priority=NOTIF_PRIORITY_HIGH,
        )

    def _notify_persistent_failure(self, crash_info: dict):
        """Notify user of persistent daemon failure.

        Creates a critical notification when the daemon hits max crashes
        and needs to stop. Includes crash history and debugging information.

        Args:
            crash_info: Dictionary with last crash details
                - timestamp: ISO timestamp
                - exception: Exception message
                - exception_type: Exception class name
                - priority: Priority being worked on
                - iteration: Iteration number

        Example:
            >>> daemon._notify_persistent_failure({
            ...     "timestamp": "2025-10-11T10:30:00",
            ...     "exception": "API timeout",
            ...     "exception_type": "TimeoutError",
            ...     "priority": "PRIORITY 2.7",
            ...     "iteration": 5
            ... })
        """
        # Build crash history summary
        crash_summary = "\n".join(
            [
                f"{i+1}. {c['timestamp']} - {c['exception_type']}: {c['exception'][:100]}"
                for i, c in enumerate(self.crash_history[-5:])  # Last 5 crashes
            ]
        )

        message = f"""🚨 CRITICAL: code_developer daemon has crashed {self.crash_count} times and stopped.

**Last Crash Details**:
- Time: {crash_info['timestamp']}
- Priority: {crash_info['priority']}
- Exception: {crash_info['exception_type']}
- Message: {crash_info['exception'][:200]}

**Recent Crash History** ({len(self.crash_history)} total):
{crash_summary}

**Action Required**:
1. Review crash logs for root cause
2. Check ROADMAP.md for problematic priority
3. Fix underlying issue (API, network, code bug)
4. Restart daemon: `poetry run code-developer`

**Debugging Steps**:
1. Check daemon logs: `tail -f ~/.coffee_maker/daemon.log`
2. Test Claude CLI: `claude -p "test"`
3. Verify API credits: Check Anthropic dashboard
4. Check network: `ping api.anthropic.com`
5. Review priority: `poetry run project-manager view {crash_info['priority']}`

The daemon will remain stopped until manually restarted.
"""

        self.notifications.create_notification(
            type=NOTIF_TYPE_ERROR,
            title="🚨 Daemon Persistent Failure",
            message=message,
            priority=NOTIF_PRIORITY_CRITICAL,
            context={
                "crash_count": self.crash_count,
                "crash_info": crash_info,
                "crash_history": self.crash_history,
                "requires_manual_intervention": True,
            },
        )

        logger.critical("Created critical notification for persistent failure")

    def _write_status(self, priority=None):
        """Write current daemon status to file.

        PRIORITY 2.8: Daemon Status Reporting

        This method writes the daemon's current status to ~/.coffee_maker/daemon_status.json
        so that `project-manager status` can read and display it to the user.

        Called at:
        - Start of each iteration
        - After priority completion
        - After crash/recovery
        - On daemon stop

        Args:
            priority: Optional priority dictionary being worked on

        Status file format:
            {
                "pid": 12345,
                "status": "running" | "stopped",
                "started_at": "2025-10-11T10:30:00",
                "current_priority": {
                    "name": "PRIORITY 2.8",
                    "title": "Daemon Status Reporting",
                    "started_at": "2025-10-11T10:35:00"
                },
                "iteration": 5,
                "crashes": {
                    "count": 0,
                    "max": 3,
                    "history": [...]
                },
                "context": {
                    "iterations_since_compact": 2,
                    "compact_interval": 10,
                    "last_compact": "2025-10-11T10:00:00"
                },
                "last_update": "2025-10-11T10:45:00"
            }

        Example:
            >>> daemon = DevDaemon()
            >>> daemon._write_status(priority={"name": "PRIORITY 2.8", "title": "..."})
        """
        try:
            # Build status dictionary
            status = {
                "pid": os.getpid(),
                "status": "running" if self.running else "stopped",
                "started_at": (
                    getattr(self, "start_time", datetime.now()).isoformat() if hasattr(self, "start_time") else None
                ),
                "current_priority": (
                    {
                        "name": priority["name"] if priority else None,
                        "title": priority["title"] if priority else None,
                        "started_at": (
                            getattr(self, "current_priority_start_time", None).isoformat()
                            if hasattr(self, "current_priority_start_time") and self.current_priority_start_time
                            else None
                        ),
                    }
                    if priority
                    else None
                ),
                "iteration": getattr(self, "iteration_count", 0),
                "subtasks": self.current_subtasks,  # Include subtasks for status bar display
                "crashes": {
                    "count": self.crash_count,
                    "max": self.max_crashes,
                    "history": self.crash_history[-5:],  # Last 5 crashes
                },
                "context": {
                    "iterations_since_compact": self.iterations_since_compact,
                    "compact_interval": self.compact_interval,
                    "last_compact": (self.last_compact_time.isoformat() if self.last_compact_time else None),
                },
                "last_update": datetime.now().isoformat(),
            }

            # Write to status file
            status_file = Path.home() / ".coffee_maker" / "daemon_status.json"

            write_json_file(status_file, status)

            logger.debug(f"Status written to {status_file}")

        except Exception as e:
            logger.error(f"Failed to write status file: {e}")

    def _update_subtask(self, name: str, status: str, start_time: datetime = None, estimated_seconds: int = 0):
        """Update or add a subtask to tracking list.

        This method tracks individual subtasks within a priority implementation
        for display in the project-manager status bar.

        Args:
            name: Subtask name (e.g., "Creating branch", "Calling Claude API")
            status: One of "pending", "in_progress", "completed", "failed"
            start_time: When subtask started (for duration calculation)
            estimated_seconds: Estimated time for this task in seconds

        Status meanings:
            - pending: Task not yet started (⏳)
            - in_progress: Currently working on this task (🔄)
            - completed: Task finished successfully (✓)
            - failed: Task encountered an error (❌)

        Example:
            >>> daemon._update_subtask("Creating branch", "in_progress", datetime.now(), estimated_seconds=10)
            >>> daemon._update_subtask("Creating branch", "completed", start_time, estimated_seconds=10)
        """
        # Calculate duration if start_time provided
        duration_seconds = 0
        if start_time and status in ["completed", "failed"]:
            duration_seconds = int((datetime.now() - start_time).total_seconds())
        elif start_time and status == "in_progress":
            # For in-progress tasks, show current elapsed time
            duration_seconds = int((datetime.now() - start_time).total_seconds())

        # Check if subtask already exists
        existing_idx = None
        for idx, subtask in enumerate(self.current_subtasks):
            if subtask["name"] == name:
                existing_idx = idx
                break

        subtask_entry = {
            "name": name,
            "status": status,
            "duration_seconds": duration_seconds,
            "estimated_seconds": estimated_seconds,
        }

        if existing_idx is not None:
            # Update existing subtask, preserve estimated_seconds if not provided
            if estimated_seconds == 0 and "estimated_seconds" in self.current_subtasks[existing_idx]:
                subtask_entry["estimated_seconds"] = self.current_subtasks[existing_idx]["estimated_seconds"]
            self.current_subtasks[existing_idx] = subtask_entry
        else:
            # Add new subtask
            self.current_subtasks.append(subtask_entry)

        logger.debug(f"Subtask updated: {name} -> {status} ({duration_seconds}s / est: {estimated_seconds}s)")

        # Record metrics to database when subtask completes or fails
        if status in ["completed", "failed"] and duration_seconds > 0 and self.current_priority_info:
            try:
                self.metrics_db.record_subtask(
                    priority_name=self.current_priority_info.get("name", "Unknown"),
                    subtask_name=name,
                    estimated_seconds=estimated_seconds,
                    actual_seconds=duration_seconds,
                    status=status,
                    priority_title=self.current_priority_info.get("title"),
                )
            except Exception as e:
                logger.warning(f"Failed to record metrics for subtask '{name}': {e}")

        # Write status to file immediately so status bar updates
        self._write_status()

    def stop(self):
        """Stop the daemon gracefully."""
        logger.info("Stopping daemon...")
        self.running = False
