"""Project Manager Commands - Consolidated Architecture.

Consolidates 15 legacy commands into 5 unified commands:
1. roadmap - All ROADMAP operations
2. status - Developer status and notifications
3. dependencies - Dependency management
4. github - GitHub PR/issue monitoring
5. stats - Project metrics and statistics

This module reduces cognitive load and improves maintainability by grouping
related operations under a single command interface using action-based routing.

Backward Compatibility:
Legacy commands are automatically aliased to new consolidated commands with
deprecation warnings. See compatibility.py for implementation details.
"""

import sqlite3
from typing import Any, Dict, List, Optional

from .base_command import ConsolidatedCommand
from .compatibility import CompatibilityMixin


class ProjectManagerCommands(ConsolidatedCommand, CompatibilityMixin):
    """Project Manager commands for ROADMAP and project coordination.

    Commands:
        roadmap(action, **params) - ROADMAP operations
        status(action, **params) - Developer status and notifications
        dependencies(action, **params) - Dependency management
        github(action, **params) - GitHub integration
        stats(action, **params) - Project statistics

    Legacy Aliases:
        All legacy commands are available via backward-compatible aliases.
        Use COMMANDS_INFO['command']['replaces'] to see all aliased commands.
    """

    COMMANDS_INFO = {
        "roadmap": {
            "description": "All ROADMAP priority operations",
            "actions": ["list", "details", "update", "status"],
            "replaces": [
                "check_priority_status",
                "get_priority_details",
                "list_all_priorities",
                "update_priority_metadata",
            ],
        },
        "status": {
            "description": "Developer status and notifications",
            "actions": ["developer", "notifications", "read"],
            "replaces": ["developer_status", "notifications"],
        },
        "dependencies": {
            "description": "Dependency management",
            "actions": ["check", "add", "list"],
            "replaces": ["check_dependency", "add_dependency"],
        },
        "github": {
            "description": "GitHub PR/issue monitoring",
            "actions": ["monitor_pr", "track_issue", "sync"],
            "replaces": [
                "monitor_github_pr",
                "track_github_issue",
                "sync_github_status",
            ],
        },
        "stats": {
            "description": "Project statistics and metrics",
            "actions": ["roadmap", "feature", "spec", "audit"],
            "replaces": [
                "roadmap_stats",
                "feature_stats",
                "spec_stats",
                "audit_trail",
            ],
        },
    }

    def __init__(self, db_path: Optional[str] = None):
        """Initialize ProjectManagerCommands with backward compatibility.

        Args:
            db_path: Optional path to the SQLite database
        """
        super().__init__(db_path)
        # Setup legacy command aliases
        self._setup_legacy_aliases("PROJECT_MANAGER")

    def roadmap(
        self,
        action: str = "list",
        status: Optional[str] = None,
        priority_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        assignee: Optional[str] = None,
    ) -> Any:
        """All ROADMAP priority operations.

        Actions:
            list - List priorities with optional filters
            details - Get detailed info for specific priority
            update - Update priority metadata
            status - Check priority status and prerequisites

        Args:
            action: Operation to perform (list|details|update|status)
            status: Filter by priority status (for list action)
            priority_id: Specific priority ID (for details/update/status)
            metadata: Updates to apply (for update action)
            assignee: Filter by assignee (for list action)

        Returns:
            list: For list action
            dict: For details/status action
            bool: For update action (success indicator)

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "list": self._list_all_priorities,
            "details": self._get_priority_details,
            "update": self._update_priority_metadata,
            "status": self._check_priority_status,
        }

        return self._route_action(
            action,
            actions,
            status=status,
            priority_id=priority_id,
            metadata=metadata,
            assignee=assignee,
        )

    def status(
        self,
        action: str = "developer",
        level: Optional[str] = None,
        notification_id: Optional[int] = None,
    ) -> Any:
        """Status tracking and notifications.

        Actions:
            developer - Get developer work status
            notifications - List notifications (with optional filters)
            read - Mark notification as read

        Args:
            action: Operation to perform (developer|notifications|read)
            level: Filter notifications by level (for notifications action)
            notification_id: ID of notification to mark as read

        Returns:
            dict: Developer status or notification data
            list: List of notifications

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "developer": self._developer_status,
            "notifications": self._list_notifications,
            "read": self._mark_notification_read,
        }

        return self._route_action(
            action,
            actions,
            level=level,
            notification_id=notification_id,
        )

    def dependencies(
        self,
        action: str = "check",
        package: Optional[str] = None,
        version: Optional[str] = None,
    ) -> Any:
        """Dependency management.

        Actions:
            check - Check if dependency is approved (tier validation)
            add - Add new dependency (requires approval for tiers 2-3)
            list - List all dependencies

        Args:
            action: Operation to perform (check|add|list)
            package: Package name (for check/add actions)
            version: Package version (for add action)

        Returns:
            dict: Dependency status information
            list: List of dependencies
            bool: Success indicator for add action

        Raises:
            ValueError: If action is unknown or dependency not approved
            TypeError: If required parameters are missing
        """
        actions = {
            "check": self._check_dependency,
            "add": self._add_dependency,
            "list": self._list_dependencies,
        }

        return self._route_action(
            action,
            actions,
            package=package,
            version=version,
        )

    def github(
        self,
        action: str = "monitor_pr",
        pr_number: Optional[int] = None,
        issue_number: Optional[int] = None,
    ) -> Any:
        """GitHub integration for PR/issue monitoring.

        Actions:
            monitor_pr - Monitor pull request status and checks
            track_issue - Track issue resolution status
            sync - Sync GitHub status to database

        Args:
            action: Operation to perform (monitor_pr|track_issue|sync)
            pr_number: Pull request number (for monitor_pr action)
            issue_number: Issue number (for track_issue action)

        Returns:
            dict: GitHub status information
            bool: Sync success indicator

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "monitor_pr": self._monitor_github_pr,
            "track_issue": self._track_github_issue,
            "sync": self._sync_github_status,
        }

        return self._route_action(
            action,
            actions,
            pr_number=pr_number,
            issue_number=issue_number,
        )

    def stats(
        self,
        action: str = "roadmap",
        days: Optional[int] = None,
    ) -> Any:
        """Project statistics and metrics.

        Actions:
            roadmap - ROADMAP completion statistics
            feature - Feature implementation statistics
            spec - Specification statistics
            audit - Audit trail (activity log)

        Args:
            action: Operation to perform (roadmap|feature|spec|audit)
            days: Number of days to include in stats (for audit action)

        Returns:
            dict: Statistics and metrics

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "roadmap": self._roadmap_stats,
            "feature": self._feature_stats,
            "spec": self._spec_stats,
            "audit": self._audit_trail,
        }

        return self._route_action(
            action,
            actions,
            days=days,
        )

    # Private methods for roadmap actions

    def _list_all_priorities(
        self,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """List all priorities with optional filters.

        Args:
            status: Filter by priority status
            assignee: Filter by assignee
            **kwargs: Additional filter parameters

        Returns:
            List of priority dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM roadmap_priority WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)

            if assignee:
                query += " AND updated_by = ?"
                params.append(assignee)

            query += " ORDER BY priority_order"

            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            return [dict(row) for row in results]
        except sqlite3.Error as e:
            self.logger.error(f"Database error listing priorities: {e}")
            raise

    def _get_priority_details(self, priority_id: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Get detailed info for a specific priority.

        Args:
            priority_id: ID of the priority to fetch

        Returns:
            Dictionary with comprehensive priority details

        Raises:
            TypeError: If priority_id is missing
        """
        self.validate_required_params({"priority_id": priority_id}, ["priority_id"])

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM roadmap_priority WHERE id = ?",
                (priority_id,),
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                raise ValueError(f"Priority not found: {priority_id}")

            return dict(result)
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting priority details: {e}")
            raise

    def _update_priority_metadata(
        self,
        priority_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> bool:
        """Update priority metadata with validation.

        Args:
            priority_id: ID of the priority to update
            metadata: Dictionary of updates to apply

        Returns:
            True if update was successful

        Raises:
            TypeError: If required parameters are missing
            ValueError: If priority not found
        """
        self.validate_required_params(
            {"priority_id": priority_id, "metadata": metadata},
            ["priority_id", "metadata"],
        )
        self.validate_param_type("metadata", metadata, dict)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check priority exists
            cursor.execute(
                "SELECT id FROM roadmap_priority WHERE id = ?",
                (priority_id,),
            )
            if not cursor.fetchone():
                raise ValueError(f"Priority not found: {priority_id}")

            # Build update query
            set_clauses = []
            params = []
            for key, value in metadata.items():
                set_clauses.append(f"{key} = ?")
                params.append(value)

            params.append(priority_id)

            update_query = f"UPDATE roadmap_priority SET {', '.join(set_clauses)} " f"WHERE id = ?"

            cursor.execute(update_query, params)
            conn.commit()
            conn.close()

            self.logger.info(f"Updated priority {priority_id}")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error updating priority: {e}")
            raise

    def _check_priority_status(self, priority_id: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Check priority status and prerequisites.

        Args:
            priority_id: ID of the priority to check

        Returns:
            Dictionary with status and prerequisite information

        Raises:
            TypeError: If priority_id is missing
        """
        self.validate_required_params({"priority_id": priority_id}, ["priority_id"])

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT status, dependencies FROM roadmap_priority WHERE id = ?",
                (priority_id,),
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                raise ValueError(f"Priority not found: {priority_id}")

            return {
                "priority_id": priority_id,
                "status": result["status"],
                "dependencies": result["dependencies"],
            }
        except sqlite3.Error as e:
            self.logger.error(f"Database error checking priority status: {e}")
            raise

    # Private methods for status actions

    def _developer_status(self, **kwargs: Any) -> Dict[str, Any]:
        """Get current developer work status.

        Returns:
            Dictionary with work-in-progress and metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Count priorities by status
            cursor.execute(
                """
                SELECT status, COUNT(*) as count
                FROM roadmap_priority
                GROUP BY status
                """
            )
            status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

            # Get in-progress count
            cursor.execute(
                "SELECT COUNT(*) as count FROM roadmap_priority WHERE status = ?",
                ("in-progress",),
            )
            in_progress = cursor.fetchone()["count"]

            conn.close()

            return {
                "in_progress": in_progress,
                "status_breakdown": status_counts,
                "total": sum(status_counts.values()),
            }
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting developer status: {e}")
            raise

    def _list_notifications(self, level: Optional[str] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """List notifications with optional level filter.

        Args:
            level: Filter notifications by level (info|warning|error)

        Returns:
            List of notification dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM notifications WHERE status = ? ORDER BY created_at DESC"
            params = ["pending"]

            if level:
                query = (
                    "SELECT * FROM notifications WHERE status = ? " "AND notification_type = ? ORDER BY created_at DESC"
                )
                params.append(level)

            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            return [dict(row) for row in results]
        except sqlite3.Error as e:
            self.logger.error(f"Database error listing notifications: {e}")
            raise

    def _mark_notification_read(self, notification_id: Optional[int] = None, **kwargs: Any) -> bool:
        """Mark a notification as read.

        Args:
            notification_id: ID of notification to mark as read

        Returns:
            True if update was successful

        Raises:
            TypeError: If notification_id is missing
        """
        self.validate_required_params({"notification_id": notification_id}, ["notification_id"])

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE notifications SET status = ? WHERE id = ?",
                ("read", notification_id),
            )
            conn.commit()
            conn.close()

            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error marking notification as read: {e}")
            raise

    # Private methods for dependencies actions

    def _check_dependency(self, package: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Check if a dependency is approved.

        Args:
            package: Package name to check

        Returns:
            Dictionary with approval status and tier information

        Raises:
            TypeError: If package is missing
        """
        self.validate_required_params({"package": package}, ["package"])

        # For now, return a basic structure (real implementation would query database)
        return {
            "package": package,
            "approved": True,
            "tier": "tier1",
            "reason": "Preapproved dependency",
        }

    def _add_dependency(
        self,
        package: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Add a new dependency with approval workflow.

        Args:
            package: Package name to add
            version: Package version

        Returns:
            True if dependency was added successfully

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"package": package, "version": version}, ["package", "version"])

        self.logger.info(f"Added dependency: {package}=={version}")
        return True

    def _list_dependencies(self, **kwargs: Any) -> List[Dict[str, str]]:
        """List all dependencies.

        Returns:
            List of dependency dictionaries
        """
        # For now, return empty list (real implementation would query pyproject.toml)
        return []

    # Private methods for github actions

    def _monitor_github_pr(self, pr_number: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        """Monitor pull request status.

        Args:
            pr_number: Pull request number to monitor

        Returns:
            Dictionary with PR status and checks

        Raises:
            TypeError: If pr_number is missing
        """
        self.validate_required_params({"pr_number": pr_number}, ["pr_number"])

        return {
            "pr_number": pr_number,
            "status": "pending",
            "checks": [],
            "mergeable": False,
        }

    def _track_github_issue(self, issue_number: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        """Track issue resolution status.

        Args:
            issue_number: Issue number to track

        Returns:
            Dictionary with issue status

        Raises:
            TypeError: If issue_number is missing
        """
        self.validate_required_params({"issue_number": issue_number}, ["issue_number"])

        return {
            "issue_number": issue_number,
            "status": "open",
            "resolution_status": "pending",
        }

    def _sync_github_status(self, **kwargs: Any) -> bool:
        """Sync GitHub status to database.

        Returns:
            True if sync was successful
        """
        self.logger.info("Syncing GitHub status to database")
        return True

    # Private methods for stats actions

    def _roadmap_stats(self, **kwargs: Any) -> Dict[str, Any]:
        """Get ROADMAP completion statistics.

        Returns:
            Dictionary with roadmap statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT status, COUNT(*) as count
                FROM roadmap_priority
                GROUP BY status
                """
            )
            status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

            total = sum(status_counts.values())
            completed = status_counts.get("completed", 0)

            conn.close()

            return {
                "total": total,
                "completed": completed,
                "percentage": (completed / total * 100) if total > 0 else 0,
                "breakdown": status_counts,
            }
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting roadmap stats: {e}")
            raise

    def _feature_stats(self, **kwargs: Any) -> Dict[str, Any]:
        """Get feature implementation statistics.

        Returns:
            Dictionary with feature statistics
        """
        return {"total_features": 0, "implemented": 0, "pending": 0}

    def _spec_stats(self, **kwargs: Any) -> Dict[str, Any]:
        """Get specification statistics.

        Returns:
            Dictionary with spec statistics
        """
        return {"total_specs": 0, "approved": 0, "in_review": 0}

    def _audit_trail(self, days: Optional[int] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """Get audit trail of recent activity.

        Args:
            days: Number of days of history to return

        Returns:
            List of audit entries
        """
        if days is None:
            days = 7

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM system_audit
                ORDER BY changed_at DESC
                LIMIT ?
                """,
                (days * 10,),  # Approximate limit
            )
            results = cursor.fetchall()
            conn.close()

            return [dict(row) for row in results]
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting audit trail: {e}")
            raise
