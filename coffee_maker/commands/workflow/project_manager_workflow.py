"""Project Manager Workflow Command - Ultra-Consolidated.

Single workflow command that handles all project management operations:
roadmap management, progress tracking, planning, and reporting.

Replaces 5 consolidated commands with 1 workflow command.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from coffee_maker.commands.consolidated.project_manager_commands import (
    ProjectManagerCommands,
)
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class ManageAction(Enum):
    """Available project management actions."""

    ROADMAP = "roadmap"  # Update/view/validate roadmap
    TRACK = "track"  # Track progress and send notifications
    PLAN = "plan"  # Create new priorities and tasks
    REPORT = "report"  # Generate status reports


@dataclass
class ManageResult:
    """Result of manage() execution.

    Attributes:
        action: The action that was performed
        status: Success/failure status
        data: Action-specific result data
        notifications_sent: Number of notifications sent
        tasks_updated: Number of tasks updated
        duration_seconds: Execution time
        metadata: Additional workflow metadata
    """

    action: str
    status: str = "success"
    data: Any = None
    notifications_sent: int = 0
    tasks_updated: int = 0
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectManagerWorkflow:
    """Ultra-consolidated workflow command for project management.

    Single command that handles all project management workflows:
        - Roadmap: Load → Update → Validate → Notify → Commit
        - Track: Query → Identify blockers → Notify → Update
        - Plan: Analyze → Create priorities/tasks → Update roadmap
        - Report: Gather data → Generate report → Distribute

    Example:
        >>> workflow = ProjectManagerWorkflow()
        >>> result = workflow.manage(action="track")
        >>> print(result.notifications_sent)
        3

    Replaces:
        - roadmap(action="update|view|validate")
        - tasks(action="create|update|track")
        - specs(action="load|create")
        - notifications(action="send|list")
        - git(action="commit|tag")
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize workflow with consolidated commands."""
        self.commands = ProjectManagerCommands(db_path)
        self.logger = logger

    def manage(
        self,
        action: str,
        priority_id: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None,
        notify: bool = True,
        auto_commit: bool = False,
        verbose: bool = False,
    ) -> ManageResult:
        """Execute complete project management workflow.

        Args:
            action: Management action - "roadmap"|"track"|"plan"|"report"
            priority_id: Priority ID for plan action (optional)
            updates: Updates to apply for roadmap action (optional)
            notify: Send notifications (default: True)
            auto_commit: Auto-commit changes (default: False)
            verbose: Enable verbose logging (default: False)

        Returns:
            ManageResult with execution details

        Raises:
            ValueError: If action is invalid

        Example:
            # Track progress across all tasks
            result = workflow.manage(action="track")

            # Update roadmap
            result = workflow.manage(
                action="roadmap",
                updates={"PRIORITY-5": {"status": "in_progress"}}
            )

            # Create new plan
            result = workflow.manage(
                action="plan",
                priority_id="PRIORITY-6"
            )
        """
        start_time = datetime.now()

        try:
            # Validate action
            try:
                manage_action = ManageAction(action)
            except ValueError:
                raise ValueError(
                    f"Invalid action '{action}'. " f"Must be one of: {', '.join(a.value for a in ManageAction)}"
                )

            self.logger.info(f"Starting manage workflow: {action}")

            # Execute workflow based on action
            if manage_action == ManageAction.ROADMAP:
                result = self._execute_roadmap_workflow(
                    updates=updates,
                    notify=notify,
                    auto_commit=auto_commit,
                    verbose=verbose,
                )
            elif manage_action == ManageAction.TRACK:
                result = self._execute_track_workflow(notify=notify, verbose=verbose)
            elif manage_action == ManageAction.PLAN:
                result = self._execute_plan_workflow(
                    priority_id=priority_id,
                    notify=notify,
                    auto_commit=auto_commit,
                    verbose=verbose,
                )
            elif manage_action == ManageAction.REPORT:
                result = self._execute_report_workflow(verbose=verbose)
            else:
                raise ValueError(f"Unknown action: {action}")

            # Calculate duration
            result.duration_seconds = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"Manage workflow completed: {result.status} ({result.duration_seconds:.1f}s)")
            return result

        except Exception as e:
            result = ManageResult(action=action, status="failed", data=str(e))
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Manage workflow failed: {e}")
            return result

    def _execute_roadmap_workflow(
        self,
        updates: Optional[Dict[str, Any]],
        notify: bool,
        auto_commit: bool,
        verbose: bool,
    ) -> ManageResult:
        """Execute roadmap management workflow.

        Steps:
            1. Load current roadmap
            2. Apply updates
            3. Validate consistency
            4. Notify affected agents
            5. Commit changes (if auto_commit)
        """
        result = ManageResult(action="roadmap")

        try:
            # Step 1: Load roadmap
            if verbose:
                self.logger.info("[1/5] Loading current roadmap")
            roadmap_data = self.commands.roadmap(action="view")
            result.metadata["original_roadmap"] = roadmap_data

            # Step 2: Apply updates
            if updates:
                if verbose:
                    self.logger.info(f"[2/5] Applying {len(updates)} updates")
                update_result = self.commands.roadmap(action="update", updates=updates)
                result.tasks_updated = len(updates)
                result.data = update_result
            else:
                if verbose:
                    self.logger.info("[2/5] No updates to apply")
                result.data = roadmap_data

            # Step 3: Validate
            if verbose:
                self.logger.info("[3/5] Validating roadmap consistency")
            validation = self.commands.roadmap(action="validate")
            result.metadata["validation"] = validation

            # Step 4: Notify
            if notify and result.tasks_updated > 0:
                if verbose:
                    self.logger.info("[4/5] Sending notifications")
                notification_result = self.commands.notifications(
                    action="send", message=f"Roadmap updated: {result.tasks_updated} changes"
                )
                if isinstance(notification_result, dict):
                    result.notifications_sent = notification_result.get("sent", 0)
            else:
                if verbose:
                    self.logger.info("[4/5] Skipping notifications")

            # Step 5: Commit
            if auto_commit and result.tasks_updated > 0:
                if verbose:
                    self.logger.info("[5/5] Committing roadmap changes")
                commit_sha = self.commands.git(
                    action="commit",
                    message=f"chore: Update roadmap ({result.tasks_updated} changes)",
                )
                result.metadata["commit_sha"] = commit_sha
            else:
                if verbose:
                    self.logger.info("[5/5] Skipping commit")

            result.status = "success"
            return result

        except Exception as e:
            result.status = "failed"
            result.data = str(e)
            return result

    def _execute_track_workflow(self, notify: bool, verbose: bool) -> ManageResult:
        """Execute progress tracking workflow.

        Steps:
            1. Query all task statuses
            2. Identify blockers
            3. Send notifications for blockers
            4. Update roadmap status
        """
        result = ManageResult(action="track")

        try:
            # Step 1: Query task statuses
            if verbose:
                self.logger.info("[1/4] Querying task statuses")
            task_data = self.commands.tasks(action="track")
            result.data = task_data

            # Step 2: Identify blockers
            if verbose:
                self.logger.info("[2/4] Identifying blockers")
            blockers = []
            if isinstance(task_data, dict):
                tasks = task_data.get("tasks", [])
                blockers = [t for t in tasks if t.get("status") == "blocked"]
            result.metadata["blockers"] = blockers

            # Step 3: Notify about blockers
            if notify and blockers:
                if verbose:
                    self.logger.info(f"[3/4] Notifying about {len(blockers)} blockers")
                notification_result = self.commands.notifications(
                    action="send", message=f"{len(blockers)} tasks blocked, need attention"
                )
                if isinstance(notification_result, dict):
                    result.notifications_sent = notification_result.get("sent", 0)
            else:
                if verbose:
                    self.logger.info("[3/4] No blockers to notify")

            # Step 4: Update roadmap
            if verbose:
                self.logger.info("[4/4] Updating roadmap status")
            if isinstance(task_data, dict):
                result.tasks_updated = task_data.get("total", 0)

            result.status = "success"
            return result

        except Exception as e:
            result.status = "failed"
            result.data = str(e)
            return result

    def _execute_plan_workflow(
        self,
        priority_id: Optional[str],
        notify: bool,
        auto_commit: bool,
        verbose: bool,
    ) -> ManageResult:
        """Execute planning workflow.

        Steps:
            1. Analyze priority requirements
            2. Create new priorities/tasks
            3. Update roadmap
            4. Notify team
        """
        result = ManageResult(action="plan")

        try:
            if not priority_id:
                raise ValueError("priority_id required for plan action")

            # Step 1: Analyze requirements
            if verbose:
                self.logger.info(f"[1/4] Analyzing {priority_id}")
            # Load priority details
            priority_data = self.commands.roadmap(action="view", priority_id=priority_id)
            result.metadata["priority"] = priority_data

            # Step 2: Create tasks
            if verbose:
                self.logger.info("[2/4] Creating tasks")
            task_result = self.commands.tasks(action="create", priority_id=priority_id)
            result.data = task_result
            if isinstance(task_result, dict):
                result.tasks_updated = task_result.get("created", 0)

            # Step 3: Update roadmap
            if verbose:
                self.logger.info("[3/4] Updating roadmap")
            self.commands.roadmap(action="update", updates={priority_id: {"status": "planned"}})

            # Step 4: Notify
            if notify:
                if verbose:
                    self.logger.info("[4/4] Notifying team")
                notification_result = self.commands.notifications(
                    action="send",
                    message=f"New plan created: {priority_id} ({result.tasks_updated} tasks)",
                )
                if isinstance(notification_result, dict):
                    result.notifications_sent = notification_result.get("sent", 0)

            result.status = "success"
            return result

        except Exception as e:
            result.status = "failed"
            result.data = str(e)
            return result

    def _execute_report_workflow(self, verbose: bool) -> ManageResult:
        """Execute status reporting workflow.

        Steps:
            1. Gather all project data
            2. Generate comprehensive report
            3. Format for distribution
        """
        result = ManageResult(action="report")

        try:
            # Step 1: Gather data
            if verbose:
                self.logger.info("[1/3] Gathering project data")

            roadmap_data = self.commands.roadmap(action="view")
            task_data = self.commands.tasks(action="track")
            notification_data = self.commands.notifications(action="list")

            # Step 2: Generate report
            if verbose:
                self.logger.info("[2/3] Generating report")

            report = {
                "timestamp": datetime.now().isoformat(),
                "roadmap": roadmap_data,
                "tasks": task_data,
                "notifications": notification_data,
                "summary": self._generate_summary(roadmap_data, task_data),
            }

            # Step 3: Format
            if verbose:
                self.logger.info("[3/3] Formatting report")

            result.data = report
            result.status = "success"
            return result

        except Exception as e:
            result.status = "failed"
            result.data = str(e)
            return result

    def _generate_summary(self, roadmap_data: Any, task_data: Any) -> Dict[str, Any]:
        """Generate summary statistics.

        Args:
            roadmap_data: Roadmap information
            task_data: Task tracking information

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            "total_priorities": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "in_progress_tasks": 0,
            "blocked_tasks": 0,
        }

        if isinstance(roadmap_data, dict):
            summary["total_priorities"] = len(roadmap_data.get("priorities", []))

        if isinstance(task_data, dict):
            tasks = task_data.get("tasks", [])
            summary["total_tasks"] = len(tasks)
            summary["completed_tasks"] = len([t for t in tasks if t.get("status") == "completed"])
            summary["in_progress_tasks"] = len([t for t in tasks if t.get("status") == "in_progress"])
            summary["blocked_tasks"] = len([t for t in tasks if t.get("status") == "blocked"])

        return summary
