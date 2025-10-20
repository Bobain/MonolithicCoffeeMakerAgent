"""Continuous Work Loop for Orchestrator Agent.

This module implements the main work loop that enables 24/7 autonomous operation
where code_developer and architect continuously work on ROADMAP priorities without
human intervention.

Architecture:
    - Infinite work loop that polls ROADMAP every 30 seconds
    - Maintains 2-3 specs ahead of code_developer (spec backlog)
    - Delegates spec creation to architect proactively
    - Delegates implementation to code_developer when specs ready
    - Monitors task progress and handles errors
    - Graceful shutdown on SIGINT (Ctrl+C)
    - State preservation for crash recovery

CFR Compliance:
    - CFR-009: Sound notifications disabled (sound=False, agent_id="orchestrator")
    - CFR-013: All work happens on roadmap branch only

Related:
    SPEC-104: Technical specification
    US-104: Strategic requirement (PRIORITY 20)
"""

import json
import logging
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.cli.notifications import NotificationDB
from coffee_maker.orchestrator.architect_coordinator import ArchitectCoordinator

logger = logging.getLogger(__name__)

# Import orchestrator agent management skill
agent_mgmt_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "orchestrator-agent-management"
sys.path.insert(0, str(agent_mgmt_dir))
from agent_management import OrchestratorAgentManagementSkill

sys.path.pop(0)

# Import roadmap management skill (SINGLE SOURCE OF TRUTH for ROADMAP operations)
roadmap_mgmt_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "roadmap-management"
sys.path.insert(0, str(roadmap_mgmt_dir))
from roadmap_management import RoadmapManagementSkill

sys.path.pop(0)


@dataclass
class WorkLoopConfig:
    """Configuration for continuous work loop."""

    poll_interval_seconds: int = 30  # How often to check ROADMAP
    spec_backlog_target: int = 3  # Keep 3 specs ahead of code_developer
    max_retry_attempts: int = 3  # Retry failed tasks up to 3 times
    task_timeout_seconds: int = 7200  # 2 hours max per task
    state_file_path: str = "data/orchestrator/work_loop_state.json"
    enable_sound_notifications: bool = False  # CFR-009: Only user_listener uses sound


class ContinuousWorkLoop:
    """
    Continuous work loop for orchestrator agent.

    Responsibilities:
    - Poll ROADMAP every 30 seconds for new priorities
    - Maintain 2-3 specs ahead of code_developer (spec backlog)
    - Delegate spec creation to architect proactively
    - Delegate implementation to code_developer when specs ready
    - Monitor task progress and handle errors
    - Graceful shutdown on SIGINT (Ctrl+C)
    - State preservation for crash recovery

    CFR Compliance:
    - CFR-009: Sound notifications disabled (sound=False, agent_id="orchestrator")
    - CFR-013: All work happens on roadmap branch only
    """

    def __init__(self, config: Optional[WorkLoopConfig] = None):
        """
        Initialize continuous work loop.

        Args:
            config: Configuration for work loop (optional, uses defaults)
        """
        self.config = config or WorkLoopConfig()
        self.notifications = NotificationDB()
        self.running = False
        self.current_state: Dict = {}
        self.last_roadmap_update = 0.0
        self.repo_root = Path.cwd()  # Repository root directory

        # Initialize agent management skill
        self.agent_mgmt = OrchestratorAgentManagementSkill()

        # Initialize roadmap management skill (SINGLE SOURCE OF TRUTH)
        self.roadmap_skill = RoadmapManagementSkill()

        # Initialize architect coordinator (spec backlog + worktree merging)
        self.architect_coordinator = ArchitectCoordinator(spec_backlog_target=self.config.spec_backlog_target)

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # Load previous state if exists (crash recovery)
        self._load_state()

    def start(self):
        """
        Start continuous work loop (runs forever until interrupted).

        Returns:
            None (blocks until graceful shutdown)
        """
        logger.info("🚀 Starting Orchestrator Continuous Work Loop")
        self.running = True

        self.notifications.create_notification(
            type="info",
            title="Orchestrator Started",
            message="Continuous work loop is now running. Agents will work 24/7 on ROADMAP priorities.",
            priority="normal",
            sound=False,  # CFR-009: Background agent, no sound
            agent_id="orchestrator",
        )

        try:
            while self.running:
                loop_start = time.time()

                # Main work loop cycle
                try:
                    self._work_cycle()
                except Exception as e:
                    logger.error(f"Error in work cycle: {e}", exc_info=True)
                    self._handle_cycle_error(e)

                # Sleep for poll interval (minus cycle time)
                cycle_duration = time.time() - loop_start
                sleep_time = max(0, self.config.poll_interval_seconds - cycle_duration)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self._shutdown()

    def _work_cycle(self):
        """
        Single iteration of work loop.

        Steps:
        1. Poll ROADMAP for changes
        2. Coordinate architect (proactive spec creation)
        3. Coordinate code_developer (implementation)
        4. Monitor task progress
        5. Handle errors and retries
        6. Save state
        """
        # Step 1: Poll ROADMAP
        roadmap_updated = self._poll_roadmap()
        if roadmap_updated:
            logger.info("ROADMAP updated, recalculating work distribution")

        # Step 2: Architect coordination (proactive spec creation)
        self._coordinate_architect()

        # Step 2.5: Architect refactoring analysis (weekly)
        self._coordinate_refactoring_analysis()

        # Step 2.6: project_manager auto-planning (weekly)
        self._coordinate_planning()

        # Step 2.7: Check for completed worktrees and notify architect for merge
        self._check_worktree_merges()

        # Step 3: code_developer coordination (implementation)
        self._coordinate_code_developer()

        # Step 4: Monitor task progress
        self._monitor_tasks()

        # Step 5: Save state
        self._save_state()

    def _poll_roadmap(self) -> bool:
        """
        Poll ROADMAP.md for changes.

        NOTE: With roadmap-management skill, we don't cache - skill reads file directly.
        This method only checks if file changed to log updates.

        Returns:
            True if ROADMAP was updated since last check, False otherwise
        """
        roadmap_path = Path("docs/roadmap/ROADMAP.md")

        if not roadmap_path.exists():
            logger.warning("ROADMAP.md not found!")
            return False

        # Check file modification time
        current_mtime = roadmap_path.stat().st_mtime

        if current_mtime > self.last_roadmap_update:
            # ROADMAP was modified
            logger.info(f"ROADMAP.md updated (mtime: {current_mtime})")
            self.last_roadmap_update = current_mtime
            return True

        return False

    def _coordinate_architect(self):
        """
        Coordinate architect to maintain spec backlog.

        Logic:
        1. Use RoadmapParser to get ALL priorities (handles all ROADMAP formats)
        2. Use ArchitectCoordinator to identify missing specs
        3. Spawn architect instances for first N missing specs (parallel execution)
        4. Target: Always have 2-3 specs ahead of code_developer
        """
        # Load all priorities from ROADMAP using skill (SINGLE SOURCE OF TRUTH)
        result = self.roadmap_skill.execute(operation="get_all_priorities")

        if result.get("error"):
            logger.error(f"Failed to get priorities: {result['error']}")
            return

        priorities = result.get("result", [])

        if not priorities:
            logger.debug("No priorities found in ROADMAP")
            return

        # Use ArchitectCoordinator to get all missing specs
        missing_specs = self.architect_coordinator.get_missing_specs(priorities)

        if not missing_specs:
            logger.debug("No missing specs, architect idle")
            return

        # Log how many specs are missing
        logger.info(f"📋 Found {len(missing_specs)} priorities without specs")

        # Prioritize: Create specs for first N missing (spec backlog target)
        for priority in missing_specs[: self.config.spec_backlog_target]:
            # Check if already creating this spec
            if self._is_spec_in_progress(priority["number"]):
                # Construct name from us_id or number for logging
                priority_name = priority.get("us_id") or f"PRIORITY {priority['number']}"
                logger.debug(f"Spec for {priority_name} already in progress")
                continue

            # Spawn architect to create spec
            # Skill returns: us_id (e.g., "US-059") and number (e.g., "59")
            priority_name = priority.get("us_id") or f"PRIORITY {priority['number']}"
            priority_number = priority["number"]  # e.g., "59" or "1.5"
            logger.info(f"🏗️  Spawning architect for {priority_name} spec creation")

            result = self.agent_mgmt.execute(
                action="spawn_architect",
                priority_number=priority_number,
                priority_name=priority_name,
                task_type="create_spec",
                auto_approve=True,
            )

            if result["error"]:
                logger.error(f"Failed to spawn architect for {priority_name}: {result['error']}")
                continue

            # Track that we're working on this spec
            agent_info = result["result"]
            self._track_spec_task(priority_number, agent_info["task_id"], agent_info["pid"])
            logger.info(
                f"✅ Architect spawned for {priority_name} (PID: {agent_info['pid']}, task: {agent_info['task_id']})"
            )

    def _coordinate_refactoring_analysis(self):
        """
        Coordinate architect for weekly refactoring analysis.

        Logic:
        1. Check if 7 days since last analysis
        2. If yes: spawn architect for proactive-refactoring-analysis
        3. Architect analyzes codebase and code-review history
        4. Reports refactoring opportunities to project_manager
        """
        # Check last refactoring analysis time
        last_analysis = self.current_state.get("last_refactoring_analysis", 0)
        days_since_analysis = (time.time() - last_analysis) / 86400  # seconds to days

        if days_since_analysis < 7:
            # Not time yet
            logger.debug(f"Refactoring analysis not needed (last run {days_since_analysis:.1f} days ago)")
            return

        logger.info("🔍 Spawning architect for weekly refactoring analysis")

        result = self.agent_mgmt.execute(
            action="spawn_architect",
            task_type="refactoring_analysis",
            auto_approve=True,
        )

        if result["error"]:
            logger.error(f"Failed to spawn architect for refactoring analysis: {result['error']}")
            return

        # Update last analysis time
        self.current_state["last_refactoring_analysis"] = time.time()
        logger.info(f"✅ Architect spawned for refactoring analysis (PID: {result['result']['pid']})")

    def _coordinate_planning(self):
        """
        Coordinate project_manager for weekly auto-planning.

        Logic:
        1. Check ROADMAP health
        2. If health < 80: spawn project_manager for planning
        3. If 7 days since last planning: spawn for weekly review
        4. project_manager analyzes gaps, creates new priorities
        """
        # Check last planning time
        last_planning = self.current_state.get("last_planning", 0)
        days_since_planning = (time.time() - last_planning) / 86400

        # Weekly planning OR low health
        needs_planning = days_since_planning >= 7

        if not needs_planning:
            logger.debug(f"Auto-planning not needed (last run {days_since_planning:.1f} days ago)")
            return

        logger.info("📋 Spawning project_manager for auto-planning")

        result = self.agent_mgmt.execute(
            action="spawn_project_manager",
            task_type="auto_planning",
            auto_approve=True,
        )

        if result["error"]:
            logger.error(f"Failed to spawn project_manager for planning: {result['error']}")
            return

        # Update last planning time
        self.current_state["last_planning"] = time.time()
        logger.info(f"✅ project_manager spawned for planning (PID: {result['result']['pid']})")

    def _check_worktree_merges(self):
        """
        Check for completed worktrees and notify architect when merges are needed.

        Logic:
        1. Detect all roadmap-* branches with completed work (commits ahead of roadmap)
        2. For each completed worktree:
           a. Extract US number from commit message
           b. Create high-priority notification for architect
           c. Include merge command in notification
        3. Architect receives notification and uses merge-worktree-branches skill
        4. After merge, architect notifies orchestrator
        5. Orchestrator can then clean up worktree
        """
        # Use ArchitectCoordinator to check and notify
        notifications_sent = self.architect_coordinator.check_and_notify_merges()

        if notifications_sent > 0:
            logger.info(f"📬 Sent {notifications_sent} merge notification(s) to architect")

    def _coordinate_code_developer(self):
        """
        Coordinate code_developer to implement next priority.

        NEW: Attempts parallel execution when possible!

        Logic:
        1. Get next 2-3 PLANNED priorities with specs
        2. Check task-separator skill for independence
        3. If independent: spawn parallel code_developers in worktrees
        4. If not independent: fall back to sequential execution
        """
        # Use roadmap-management skill (SINGLE SOURCE OF TRUTH)
        result = self.roadmap_skill.execute(operation="get_all_priorities")

        if result.get("error"):
            logger.error(f"Failed to get priorities: {result['error']}")
            return

        priorities = result.get("result", [])

        if not priorities:
            return

        # Filter for planned priorities with specs
        # NOTE: Skill returns: status="Planned" (not emoji), us_id="US-059", number="59"
        planned_priorities = []
        for p in priorities:
            # Check if planned (skill returns status="Planned" without emoji)
            if p.get("status") != "Planned":
                continue

            # Check if spec exists
            # Use US number for spec lookup (e.g., "US-104" -> "SPEC-104-*.md")
            # Skill returns: number="20" (PRIORITY number), us_id="US-104"
            # Specs are named with US number, not PRIORITY number
            us_id = p.get("us_id")
            spec_number = None

            if us_id:
                # Extract number from us_id (e.g., "US-104" -> "104")
                spec_number = us_id.replace("US-", "")
            else:
                # Fallback to priority number if no us_id
                spec_number = p.get("number")

            if spec_number:
                spec_pattern = f"SPEC-{spec_number}-*.md"
                spec_dir = Path("docs/architecture/specs")
                spec_files = list(spec_dir.glob(spec_pattern))
                if len(spec_files) > 0:
                    p["has_spec"] = True
                    p["spec_path"] = str(spec_files[0])
                    planned_priorities.append(p)

        if not planned_priorities:
            logger.info("No planned priorities with specs, code_developer idle")
            return

        # Check if any work already in progress
        active_impl_count = sum(1 for key in self.current_state.get("active_tasks", {}) if key.startswith("impl_"))

        if active_impl_count > 0:
            logger.debug(f"{active_impl_count} implementations already in progress")
            return

        # Try parallel execution (2-3 priorities)
        max_parallel = min(3, len(planned_priorities))

        if max_parallel >= 2:
            # Attempt parallel execution
            candidate_priorities = planned_priorities[:max_parallel]
            candidate_ids = [p["number"] for p in candidate_priorities]

            logger.info(f"🔍 Checking if {len(candidate_ids)} priorities can run in parallel...")

            # Call task-separator skill
            parallel_result = self._check_parallel_viability(candidate_ids)

            if parallel_result["valid"] and len(parallel_result["independent_pairs"]) > 0:
                # Parallel execution possible!
                logger.info(f"✅ Found {len(parallel_result['independent_pairs'])} independent pairs!")
                logger.info(f"🚀 Spawning parallel code_developers in worktrees...")

                # Use ParallelExecutionCoordinator
                self._spawn_parallel_execution(candidate_ids)
                return

            else:
                logger.info(f"❌ Cannot parallelize: {parallel_result.get('reason', 'file conflicts')}")
                logger.info("📝 Falling back to sequential execution...")

        # Fall back to sequential execution (original behavior)
        next_priority = planned_priorities[0]

        # Check if already implementing
        if self._is_implementation_in_progress(next_priority["number"]):
            logger.debug(f"Implementation for PRIORITY {next_priority['number']} already in progress")
            return

        # For now, just log that we would delegate
        logger.info(f"⚙️  Would delegate implementation to code_developer: PRIORITY {next_priority['number']}")

        # Track that we're working on this implementation
        self._track_implementation_task(next_priority["number"], f"impl-{next_priority['number']}")

    def _monitor_tasks(self):
        """
        Monitor in-progress tasks and handle timeouts/failures.

        Checks:
        - Task completion (move from in_progress to completed)
        - Timeouts (task running > 2 hours)
        - Failures (task failed, retry or escalate)
        """
        # Get active tasks from state
        active_tasks = self.current_state.get("active_tasks", {})

        for task_key, task_info in list(active_tasks.items()):
            task_age = time.time() - task_info["started_at"]

            # Check timeout
            if task_age > self.config.task_timeout_seconds:
                logger.warning(f"⚠️  Task timeout: {task_key} ({task_age:.0f}s)")

                self.notifications.create_notification(
                    type="warning",
                    title="Task Timeout Detected",
                    message=f"Task {task_key} running for {task_age / 3600:.1f} hours",
                    priority="high",
                    sound=False,  # CFR-009
                    agent_id="orchestrator",
                )

    def _is_spec_in_progress(self, priority_number: int) -> bool:
        """Check if spec creation is already in progress for priority."""
        return f"spec_{priority_number}" in self.current_state.get("active_tasks", {})

    def _is_implementation_in_progress(self, priority_number: int) -> bool:
        """Check if implementation is already in progress for priority."""
        return f"impl_{priority_number}" in self.current_state.get("active_tasks", {})

    def _track_spec_task(self, priority_number: int, task_id: str, pid: Optional[int] = None):
        """Track spec creation task."""
        if "active_tasks" not in self.current_state:
            self.current_state["active_tasks"] = {}

        self.current_state["active_tasks"][f"spec_{priority_number}"] = {
            "task_id": task_id,
            "pid": pid,
            "started_at": time.time(),
            "type": "spec_creation",
        }

    def _track_implementation_task(self, priority_number: int, task_id: str):
        """Track implementation task."""
        if "active_tasks" not in self.current_state:
            self.current_state["active_tasks"] = {}

        self.current_state["active_tasks"][f"impl_{priority_number}"] = {
            "task_id": task_id,
            "started_at": time.time(),
            "type": "implementation",
        }

    def _check_parallel_viability(self, priority_ids: List[int]) -> Dict[str, Any]:
        """Check if priorities can run in parallel using task-separator skill.

        Args:
            priority_ids: List of PRIORITY numbers to check

        Returns:
            Dict with validation result from task-separator skill
        """
        try:
            # Import and execute task-separator skill
            import importlib.util

            skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task-separator.py"

            if not skill_path.exists():
                return {"valid": False, "reason": f"task-separator skill not found: {skill_path}"}

            spec = importlib.util.spec_from_file_location("task_separator", skill_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Call skill
            result = module.main({"priority_ids": priority_ids})
            return result

        except Exception as e:
            logger.error(f"Error running task-separator skill: {e}", exc_info=True)
            return {"valid": False, "reason": f"Error: {e}"}

    def _spawn_parallel_execution(self, priority_ids: List[int]):
        """Spawn parallel code_developer instances in worktrees.

        Args:
            priority_ids: List of PRIORITY numbers to execute in parallel
        """
        try:
            from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator

            logger.info(f"🚀 Launching ParallelExecutionCoordinator for {len(priority_ids)} priorities")

            # Create coordinator
            coordinator = ParallelExecutionCoordinator(
                repo_root=self.repo_root, max_instances=min(len(priority_ids), 3), auto_merge=True
            )

            # Execute parallel batch
            result = coordinator.execute_parallel_batch(priority_ids, auto_approve=True)

            if result["success"]:
                logger.info(f"✅ Parallel execution completed!")
                logger.info(f"   Priorities executed: {result['priorities_executed']}")
                logger.info(f"   Duration: {result['duration_seconds']:.1f}s")
                logger.info(f"   Merge results: {result['merge_results']}")

                # Track completed implementations
                for priority_id in result["priorities_executed"]:
                    task_key = f"impl_{priority_id}"
                    if task_key in self.current_state.get("active_tasks", {}):
                        del self.current_state["active_tasks"][task_key]

            else:
                logger.error(f"❌ Parallel execution failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"Error spawning parallel execution: {e}", exc_info=True)

    def _handle_cycle_error(self, error: Exception):
        """
        Handle errors during work cycle.

        Args:
            error: Exception that occurred
        """
        logger.error(f"Work cycle error: {error}", exc_info=True)

        # Log to error recovery file
        error_log_path = Path("data/orchestrator/error_recovery.log")
        error_log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(error_log_path, "a") as f:
            f.write(f"{time.time()}: {error}\n")

        # Notify user for critical errors
        if isinstance(error, (IOError, PermissionError)):
            self.notifications.create_notification(
                type="error",
                title="Orchestrator Error",
                message=f"Critical error: {error}. Work loop may need manual restart.",
                priority="critical",
                sound=False,  # CFR-009
                agent_id="orchestrator",
            )

    def _handle_shutdown(self, signum, frame):
        """
        Handle shutdown signals (SIGINT, SIGTERM).

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.running = False

    def _shutdown(self):
        """Graceful shutdown: save state and stop orchestrator."""
        logger.info("🛑 Shutting down Orchestrator Work Loop")

        # Save final state
        self._save_state()

        self.notifications.create_notification(
            type="info",
            title="Orchestrator Stopped",
            message="Continuous work loop has been stopped. State saved for recovery.",
            priority="normal",
            sound=False,  # CFR-009
            agent_id="orchestrator",
        )

        logger.info("✅ Graceful shutdown complete")

    def _save_state(self):
        """Save current state to disk (for crash recovery)."""
        state_path = Path(self.config.state_file_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state_data = {
            "last_update": time.time(),
            "active_tasks": self.current_state.get("active_tasks", {}),
            "last_roadmap_update": self.last_roadmap_update,
        }

        with open(state_path, "w") as f:
            json.dump(state_data, f, indent=2)

    def _load_state(self):
        """Load previous state from disk (crash recovery)."""
        state_path = Path(self.config.state_file_path)

        if not state_path.exists():
            logger.info("No previous state found, starting fresh")
            return

        try:
            with open(state_path, "r") as f:
                state_data = json.load(f)

            self.current_state = state_data
            self.last_roadmap_update = state_data.get("last_roadmap_update", 0.0)

            logger.info(f"Loaded previous state (last update: {state_data['last_update']})")

        except Exception as e:
            logger.error(f"Failed to load state: {e}", exc_info=True)
