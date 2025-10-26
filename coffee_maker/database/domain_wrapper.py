"""Domain-based access wrappers for existing database tables.

This module provides domain-enforced wrappers around existing database
classes to ensure agents only access their authorized tables.

Features:
    - Permission enforcement (table ownership, read/write controls)
    - Audit trail logging for all operations
    - Inter-agent notifications
    - Transparent wrapping of existing database classes
"""

import json
import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase
from coffee_maker.utils.logging import get_logger

logger = get_logger(__name__)


class PermissionError(Exception):
    """Raised when agent attempts unauthorized database operation."""


class AgentType(Enum):
    """Enumeration of all agent types in the system."""

    ARCHITECT = "architect"
    CODE_DEVELOPER = "code_developer"
    PROJECT_MANAGER = "project_manager"
    CODE_REVIEWER = "code_reviewer"
    ORCHESTRATOR = "orchestrator"
    ASSISTANT = "assistant"
    USER_LISTENER = "user_listener"
    UX_DESIGN_EXPERT = "ux_design_expert"


# Map existing tables to their owner agents (who can write)
TABLE_OWNERSHIP = {
    # Project Manager owns roadmap tables
    "roadmap_priority": AgentType.PROJECT_MANAGER,
    "roadmap_metadata": AgentType.PROJECT_MANAGER,
    "roadmap_audit": AgentType.PROJECT_MANAGER,
    "roadmap_notification": AgentType.PROJECT_MANAGER,
    # Architect owns specification tables
    "specs_specification": AgentType.ARCHITECT,
    "specs_task": AgentType.ARCHITECT,
    "specs_task_dependency": AgentType.ARCHITECT,
    # Code Developer owns implementation tracking
    "review_commit": AgentType.CODE_DEVELOPER,  # Tracks commits
    "metrics_subtask": AgentType.CODE_DEVELOPER,  # Tracks work
    # Code Reviewer owns review tables
    "review_code_review": AgentType.CODE_REVIEWER,
    # Orchestrator owns agent coordination
    "agent_lifecycle": AgentType.ORCHESTRATOR,
    "orchestrator_state": AgentType.ORCHESTRATOR,
    "orchestrator_task": AgentType.ORCHESTRATOR,
    "orchestrator_bug": AgentType.ORCHESTRATOR,
    "agent_message": AgentType.ORCHESTRATOR,
    # Shared tables - multiple agents can write
    "notifications": "shared",  # All agents can send notifications
    "system_audit": "shared",  # All agents can audit
    "notification_user": "shared",  # User notifications
    "notification_system_state": "shared",
}

# Read permissions - which tables each agent can read
READ_PERMISSIONS = {
    AgentType.ARCHITECT: [
        "roadmap_priority",
        "specs_specification",
        "specs_task",
        "specs_task_dependency",
        "review_code_review",
        "notifications",
        "system_audit",
    ],
    AgentType.CODE_DEVELOPER: [
        "roadmap_priority",
        "specs_specification",
        "specs_task",
        "review_commit",
        "metrics_subtask",
        "notifications",
        "system_audit",
    ],
    AgentType.PROJECT_MANAGER: [
        # Can read everything for monitoring
        "*"
    ],
    AgentType.CODE_REVIEWER: [
        "specs_specification",
        "review_commit",
        "review_code_review",
        "roadmap_priority",
        "notifications",
        "system_audit",
    ],
    AgentType.ORCHESTRATOR: [
        # Can read everything for coordination
        "*"
    ],
    AgentType.ASSISTANT: [
        # Can read everything for demos and analysis
        "*"
    ],
    AgentType.USER_LISTENER: ["roadmap_priority", "notifications", "notification_user"],
    AgentType.UX_DESIGN_EXPERT: ["roadmap_priority", "specs_specification"],
}


class DomainWrapper:
    """Wrapper that enforces domain-based access control over existing database classes.

    This wrapper doesn't create new tables - it enforces permissions on existing ones.
    It provides permission enforcement, audit logging, and inter-agent communication.

    Example:
        >>> db = DomainWrapper(AgentType.ARCHITECT)
        >>> db.write("specs_specification", {"id": "SPEC-101", "title": "..."})
        >>> items = db.read("roadmap_priority", {"status": "📝 Planned"})
        >>> db.send_notification("code_developer", {"type": "spec_ready", "spec_id": "SPEC-101"})
    """

    def __init__(self, agent_type: AgentType, db_path: str = "data/roadmap.db"):
        """Initialize domain wrapper.

        Args:
            agent_type: The type of agent accessing the database
            db_path: Path to the database file
        """
        self.agent_type = agent_type
        self.agent_name = agent_type.value
        self.db_path = Path(db_path)

        # Use existing RoadmapDatabase which already has the connection
        self.db = RoadmapDatabase(self.db_path, agent_name=self.agent_name)

        # Get our permissions
        self.read_tables = READ_PERMISSIONS.get(agent_type, [])

        logger.info(f"DomainWrapper initialized for {self.agent_name}")

    def can_write(self, table: str) -> bool:
        """Check if agent can write to a table.

        Args:
            table: Name of the table

        Returns:
            True if agent owns the table or it's shared
        """
        ownership = TABLE_OWNERSHIP.get(table)

        # Shared tables can be written by anyone
        if ownership == "shared":
            return True

        # Check if agent owns the table
        return ownership == self.agent_type

    def can_read(self, table: str) -> bool:
        """Check if agent can read from a table.

        Args:
            table: Name of the table

        Returns:
            True if agent has read permission
        """
        # Wildcard permission
        if "*" in self.read_tables:
            return True

        # Check specific permission
        return table in self.read_tables

    def _audit_log(
        self,
        action: str,
        table: str,
        item_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log operation to audit trail.

        Args:
            action: Action performed ('create', 'update', 'delete', 'read')
            table: Table affected
            item_id: ID of item affected
            details: Additional details (field_changed, old_value, new_value)
        """
        if details is None:
            details = {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO system_audit (
                    table_name, item_id, action, field_changed,
                    old_value, new_value, changed_by, changed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    table,
                    item_id,
                    action,
                    details.get("field_changed"),
                    details.get("old_value"),
                    details.get("new_value"),
                    self.agent_name,
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            logger.debug(f"Audit logged: {self.agent_name} {action} on {table}:{item_id}")
        except Exception as e:
            logger.error(f"Failed to audit log operation: {e}")

    def write(self, table: str, data: Dict[str, Any]) -> Any:
        """Write to a table with permission check and audit logging.

        Args:
            table: Table name
            data: Data to write

        Returns:
            Result from underlying database

        Raises:
            PermissionError: If agent lacks write permission
        """
        if not self.can_write(table):
            raise PermissionError(
                f"{self.agent_name} cannot write to '{table}'. "
                f"This table is owned by {TABLE_OWNERSHIP.get(table, 'unknown')}"
            )

        # Add agent tracking and timestamp
        data["updated_by"] = self.agent_name
        if "updated_at" not in data:
            data["updated_at"] = datetime.now().isoformat()
        item_id = data.get("id", "unknown")

        # Use the appropriate method based on table
        try:
            if table == "roadmap_priority":
                # Special handling for roadmap items
                if self.agent_type != AgentType.PROJECT_MANAGER:
                    raise PermissionError("Only project_manager can write to roadmap_priority")

                result = self.db.create_item(
                    item_id=item_id,
                    item_type=data.get("item_type", "priority"),
                    number=data["number"],
                    title=data["title"],
                    status=data.get("status", "📝 Planned"),
                    content=data.get("content", ""),
                    estimated_hours=data.get("estimated_hours"),
                    dependencies=data.get("dependencies"),
                    priority_order=data.get("priority_order"),
                )

                # Audit log
                self._audit_log(
                    action="create",
                    table=table,
                    item_id=item_id,
                    details={
                        "field_changed": "all",
                        "new_value": json.dumps(data)[:200],
                    },
                )

                return result

            else:
                # Generic write for other tables using direct SQL
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                columns = list(data.keys())
                placeholders = ["?" for _ in columns]
                query = f"""
                    INSERT INTO {table} ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                """

                cursor.execute(query, list(data.values()))
                conn.commit()
                result = cursor.lastrowid
                conn.close()

                # Audit log
                self._audit_log(
                    action="create",
                    table=table,
                    item_id=item_id,
                    details={
                        "field_changed": "all",
                        "new_value": json.dumps(data)[:200],
                    },
                )

                return result

        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Error writing to {table}: {e}")
            raise

    def read(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Read from a table with permission check.

        Args:
            table: Table name
            conditions: Optional WHERE conditions

        Returns:
            List of records

        Raises:
            PermissionError: If agent lacks read permission
        """
        if not self.can_read(table):
            raise PermissionError(
                f"{self.agent_name} cannot read from '{table}'. " f"Allowed tables: {self.read_tables}"
            )

        try:
            # Special handling for roadmap_priority
            if table == "roadmap_priority":
                if conditions and "status" in conditions:
                    # Use existing method with status filter
                    items = self.db.get_all_items(status_filter=conditions["status"])
                    return items
                else:
                    return self.db.get_all_items()

            # Generic read for other tables
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = f"SELECT * FROM {table}"
            params = []

            if conditions:
                where_clauses = [f"{k} = ?" for k in conditions.keys()]
                query += f" WHERE {' AND '.join(where_clauses)}"
                params = list(conditions.values())

            cursor.execute(query, params)
            [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            conn.close()

            # Convert to list of dicts
            return [dict(row) for row in rows] if rows else []

        except Exception as e:
            logger.error(f"Error reading from {table}: {e}")
            raise

    def update(self, table: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> int:
        """Update records with permission check and audit logging.

        Args:
            table: Table name
            data: Fields to update
            conditions: WHERE conditions

        Returns:
            Number of affected rows

        Raises:
            PermissionError: If agent lacks write permission
        """
        if not self.can_write(table):
            raise PermissionError(
                f"{self.agent_name} cannot update '{table}'. "
                f"This table is owned by {TABLE_OWNERSHIP.get(table, 'unknown')}"
            )

        # Add tracking
        data["updated_by"] = self.agent_name
        item_id = conditions.get("id", "unknown")

        try:
            # Special handling for roadmap_priority
            if table == "roadmap_priority" and "status" in data:
                if self.agent_type != AgentType.PROJECT_MANAGER:
                    raise PermissionError("Only project_manager can update roadmap status")

                if item_id != "unknown":
                    result = self.db.update_status(
                        item_id=item_id,
                        new_status=data["status"],
                        updated_by=self.agent_name,
                    )

                    # Audit log
                    self._audit_log(
                        action="update",
                        table=table,
                        item_id=item_id,
                        details={
                            "field_changed": "status",
                            "new_value": data["status"],
                        },
                    )

                    return 1 if result else 0

            # Generic update
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            set_clauses = [f"{k} = ?" for k in data.keys()]
            where_clauses = [f"{k} = ?" for k in conditions.keys()]

            query = f"""
                UPDATE {table}
                SET {', '.join(set_clauses)}
                WHERE {' AND '.join(where_clauses)}
            """

            params = list(data.values()) + list(conditions.values())
            cursor.execute(query, params)
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            # Audit log
            if rowcount > 0:
                self._audit_log(
                    action="update",
                    table=table,
                    item_id=item_id,
                    details={
                        "field_changed": ", ".join(data.keys()),
                        "new_value": json.dumps(data)[:200],
                    },
                )

            return rowcount

        except Exception as e:
            logger.error(f"Error updating {table}: {e}")
            raise

    def send_notification(self, target_agent: str, message: Dict[str, Any]) -> int:
        """Send a notification to another agent.

        This is how agents communicate across domain boundaries.

        Args:
            target_agent: Target agent name
            message: Message payload

        Returns:
            Notification ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO notifications
                (target_agent, source_agent, notification_type, item_id, message, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'pending', datetime('now'))
                """,
                (
                    target_agent,
                    self.agent_name,
                    message.get("type", "notification"),
                    message.get("item_id"),
                    json.dumps(message),
                ),
            )
            conn.commit()

            notification_id = cursor.lastrowid
            conn.close()

            logger.info(f"{self.agent_name} sent notification to {target_agent} (ID: {notification_id})")

            return notification_id
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise

    def get_my_notifications(self, status: str = "pending") -> List[Dict]:
        """Get notifications for this agent.

        Args:
            status: Filter by status (pending, processed, ignored)

        Returns:
            List of notifications
        """
        if not self.can_read("notifications"):
            return []

        return self.read("notifications", {"target_agent": self.agent_name, "status": status})

    def process_notification(self, notification_id: int, notes: Optional[str] = None) -> bool:
        """Mark a notification as processed.

        Args:
            notification_id: ID of notification
            notes: Optional processing notes

        Returns:
            True if notification was successfully processed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE notifications
                SET status = 'processed',
                    processed_at = datetime('now'),
                    processed_by = ?,
                    notes = ?
                WHERE id = ?
                """,
                (self.agent_name, notes, notification_id),
            )
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()

            return success
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            return False


# Convenience functions for each agent type
def get_architect_db(db_path: str = "data/roadmap.db") -> DomainWrapper:
    """Get database wrapper for architect agent."""
    return DomainWrapper(AgentType.ARCHITECT, db_path)


def get_developer_db(db_path: str = "data/roadmap.db") -> DomainWrapper:
    """Get database wrapper for code_developer agent."""
    return DomainWrapper(AgentType.CODE_DEVELOPER, db_path)


def get_project_manager_db(db_path: str = "data/roadmap.db") -> DomainWrapper:
    """Get database wrapper for project_manager agent."""
    return DomainWrapper(AgentType.PROJECT_MANAGER, db_path)


def get_reviewer_db(db_path: str = "data/roadmap.db") -> DomainWrapper:
    """Get database wrapper for code_reviewer agent."""
    return DomainWrapper(AgentType.CODE_REVIEWER, db_path)


def get_orchestrator_db(db_path: str = "data/roadmap.db") -> DomainWrapper:
    """Get database wrapper for orchestrator agent."""
    return DomainWrapper(AgentType.ORCHESTRATOR, db_path)
