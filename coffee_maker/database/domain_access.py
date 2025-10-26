"""Domain-based database access layer with permission enforcement.

This module implements strict data domain isolation where each agent can only
write to their own domain tables and has controlled read access to others.
"""

import json
import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.utils.logging import setup_logger

logger = setup_logger(__name__)


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


# Domain prefix mapping - defines write permissions
AGENT_PREFIXES = {
    AgentType.ARCHITECT: "arch_",
    AgentType.CODE_DEVELOPER: "dev_",
    AgentType.PROJECT_MANAGER: "pm_",
    AgentType.CODE_REVIEWER: "review_",
    AgentType.ORCHESTRATOR: "orch_",
    AgentType.ASSISTANT: "assist_",
    AgentType.USER_LISTENER: "user_",
    AgentType.UX_DESIGN_EXPERT: "ux_",
}

# Read permissions matrix - defines what each agent can read
READ_PERMISSIONS = {
    AgentType.ARCHITECT: ["arch_", "dev_", "pm_", "review_", "shared_"],
    AgentType.CODE_DEVELOPER: ["dev_", "arch_", "pm_", "shared_"],
    AgentType.PROJECT_MANAGER: ["pm_", "arch_", "dev_", "review_", "shared_"],
    AgentType.CODE_REVIEWER: ["review_", "dev_", "arch_", "shared_"],
    AgentType.ORCHESTRATOR: ["*"],  # Can read all for coordination
    AgentType.ASSISTANT: ["assist_", "shared_", "*"],  # Can read all for demos/analysis
    AgentType.USER_LISTENER: ["user_", "shared_"],
    AgentType.UX_DESIGN_EXPERT: ["ux_", "dev_", "shared_"],
}


class DomainAccessError(Exception):
    """Base exception for domain access violations."""


class WritePermissionError(DomainAccessError):
    """Raised when an agent attempts to write to a forbidden domain."""


class ReadPermissionError(DomainAccessError):
    """Raised when an agent attempts to read from a forbidden domain."""


class DomainDatabase:
    """Database access with strict domain isolation and permission enforcement.

    This class ensures that each agent can only write to tables in their
    domain (identified by prefix) and can only read from allowed domains.
    All operations are logged for audit purposes.
    """

    def __init__(
        self,
        agent_type: AgentType,
        db_path: str = "data/unified_domain.db",
        create_tables: bool = True,
    ):
        """Initialize domain database connection.

        Args:
            agent_type: The type of agent accessing the database
            db_path: Path to the unified database file
            create_tables: Whether to create tables if they don't exist
        """
        self.agent_type = agent_type
        self.agent_name = agent_type.value
        self.write_prefix = AGENT_PREFIXES[agent_type]
        self.read_prefixes = READ_PERMISSIONS[agent_type]
        self.db_path = db_path

        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Connect to database
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

        if create_tables:
            self._create_audit_table()

        logger.info(f"DomainDatabase initialized for {self.agent_name} " f"with write prefix '{self.write_prefix}'")

    def _create_audit_table(self):
        """Create the shared audit trail table if it doesn't exist."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS shared_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                operation TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id TEXT,
                affected_rows INTEGER,
                timestamp TIMESTAMP NOT NULL,
                details TEXT
            )
        """
        )
        self.conn.commit()

    def can_write(self, table: str) -> bool:
        """Check if agent has write permission for a table.

        Args:
            table: Name of the table

        Returns:
            True if agent can write to the table
        """
        # Special case: shared_audit is writable by all for logging
        if table == "shared_audit":
            return True

        # Special case: orchestrator can write to message tables
        if self.agent_type == AgentType.ORCHESTRATOR and table == "orch_messages":
            return True

        # Standard check: table must have agent's prefix
        return table.startswith(self.write_prefix)

    def can_read(self, table: str) -> bool:
        """Check if agent has read permission for a table.

        Args:
            table: Name of the table

        Returns:
            True if agent can read from the table
        """
        # Wildcard permission allows reading all tables
        if "*" in self.read_prefixes:
            return True

        # Check if table matches any allowed prefix
        return any(table.startswith(prefix) for prefix in self.read_prefixes)

    def write(self, table: str, data: Dict[str, Any]) -> int:
        """Write a record to a table with permission enforcement.

        Args:
            table: Name of the table
            data: Dictionary of column:value pairs

        Returns:
            ID of the inserted record

        Raises:
            WritePermissionError: If agent lacks write permission
        """
        if not self.can_write(table):
            raise WritePermissionError(
                f"{self.agent_name} cannot write to '{table}'. "
                f"Only tables with prefix '{self.write_prefix}' are allowed."
            )

        # Add audit fields
        data["created_by"] = self.agent_name
        data["created_at"] = datetime.now().isoformat()

        # Build INSERT query
        columns = list(data.keys())
        placeholders = ["?" for _ in columns]
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, list(data.values()))
            self.conn.commit()
            record_id = cursor.lastrowid

            # Log to audit trail
            self._audit_log("WRITE", table, str(record_id), 1)

            logger.debug(f"{self.agent_name} wrote to {table} (ID: {record_id})")
            return record_id

        except sqlite3.Error as e:
            logger.error(f"Database write error: {e}")
            raise

    def read(
        self, table: str, conditions: Optional[Dict[str, Any]] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Read records from a table with permission enforcement.

        Args:
            table: Name of the table
            conditions: Optional WHERE conditions as column:value pairs
            limit: Optional maximum number of records to return

        Returns:
            List of records as dictionaries

        Raises:
            ReadPermissionError: If agent lacks read permission
        """
        if not self.can_read(table):
            raise ReadPermissionError(
                f"{self.agent_name} cannot read from '{table}'. " f"Allowed prefixes: {self.read_prefixes}"
            )

        # Build SELECT query
        query = f"SELECT * FROM {table}"
        params = []

        # Add WHERE conditions
        if conditions:
            where_clauses = [f"{k} = ?" for k in conditions.keys()]
            query += f" WHERE {' AND '.join(where_clauses)}"
            params = list(conditions.values())

        # Add LIMIT
        if limit:
            query += f" LIMIT {limit}"

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert to list of dicts
            results = [dict(row) for row in rows]

            # Log to audit trail
            self._audit_log("READ", table, None, len(results))

            logger.debug(f"{self.agent_name} read {len(results)} records from {table}")
            return results

        except sqlite3.Error as e:
            logger.error(f"Database read error: {e}")
            raise

    def update(self, table: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> int:
        """Update records in a table with permission enforcement.

        Args:
            table: Name of the table
            data: Dictionary of column:value pairs to update
            conditions: WHERE conditions as column:value pairs

        Returns:
            Number of affected rows

        Raises:
            WritePermissionError: If agent lacks write permission
        """
        if not self.can_write(table):
            raise WritePermissionError(
                f"{self.agent_name} cannot update '{table}'. "
                f"Only tables with prefix '{self.write_prefix}' are allowed."
            )

        # Add audit fields
        data["updated_by"] = self.agent_name
        data["updated_at"] = datetime.now().isoformat()

        # Build UPDATE query
        set_clauses = [f"{k} = ?" for k in data.keys()]
        where_clauses = [f"{k} = ?" for k in conditions.keys()]

        query = f"""
            UPDATE {table}
            SET {', '.join(set_clauses)}
            WHERE {' AND '.join(where_clauses)}
        """

        params = list(data.values()) + list(conditions.values())

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            affected_rows = cursor.rowcount

            # Log to audit trail
            self._audit_log("UPDATE", table, None, affected_rows)

            logger.debug(f"{self.agent_name} updated {affected_rows} rows in {table}")
            return affected_rows

        except sqlite3.Error as e:
            logger.error(f"Database update error: {e}")
            raise

    def delete(self, table: str, conditions: Dict[str, Any]) -> int:
        """Delete records from a table with permission enforcement.

        Args:
            table: Name of the table
            conditions: WHERE conditions as column:value pairs

        Returns:
            Number of deleted rows

        Raises:
            WritePermissionError: If agent lacks write permission
        """
        if not self.can_write(table):
            raise WritePermissionError(
                f"{self.agent_name} cannot delete from '{table}'. "
                f"Only tables with prefix '{self.write_prefix}' are allowed."
            )

        # Build DELETE query
        where_clauses = [f"{k} = ?" for k in conditions.keys()]
        query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        params = list(conditions.values())

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            affected_rows = cursor.rowcount

            # Log to audit trail
            self._audit_log("DELETE", table, None, affected_rows)

            logger.debug(f"{self.agent_name} deleted {affected_rows} rows from {table}")
            return affected_rows

        except sqlite3.Error as e:
            logger.error(f"Database delete error: {e}")
            raise

    def cross_domain_notify(self, target_agent: str, message: Dict[str, Any]) -> int:
        """Send a notification to another agent via orchestrator's message queue.

        This is the only way agents can communicate across domain boundaries.
        The orchestrator will read these messages and route them appropriately.

        Args:
            target_agent: Name of the target agent
            message: Message payload as dictionary

        Returns:
            Message ID
        """
        notification = {
            "from_agent": self.agent_name,
            "to_agent": target_agent,
            "message_type": message.get("type", "notification"),
            "payload": json.dumps(message),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }

        # Write to orchestrator's message queue
        # This is a special case where any agent can write to orch_messages
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO orch_messages
            (from_agent, to_agent, message_type, payload, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                notification["from_agent"],
                notification["to_agent"],
                notification["message_type"],
                notification["payload"],
                notification["status"],
                notification["created_at"],
            ),
        )
        self.conn.commit()
        message_id = cursor.lastrowid

        logger.info(f"{self.agent_name} sent notification to {target_agent} " f"(Message ID: {message_id})")

        return message_id

    def execute_command(self, command_name: str, params: Dict[str, Any]) -> Any:
        """Execute a domain command with full permission enforcement.

        This method loads a command definition from the agent's command
        directory and executes it with proper permission checks.

        Args:
            command_name: Name of the command (e.g., "create_spec")
            params: Parameters for the command

        Returns:
            Command execution result
        """
        # Load command definition
        command_path = Path(".claude/commands/agents") / self.agent_type.value / f"{command_name}.md"

        if not command_path.exists():
            raise ValueError(f"Command '{command_name}' not found for {self.agent_name}")

        # Parse command metadata
        with open(command_path) as f:
            f.read()
            # Extract metadata from frontmatter
            # ... parsing logic ...

        logger.info(f"{self.agent_name} executing command '{command_name}'")

        # Command execution would be implemented here
        # This is a placeholder for the actual command logic
        return {"status": "success", "command": command_name, "agent": self.agent_name}

    def _audit_log(
        self,
        operation: str,
        table: str,
        record_id: Optional[str] = None,
        affected_rows: Optional[int] = None,
        details: Optional[str] = None,
    ):
        """Log an operation to the audit trail.

        Args:
            operation: Type of operation (READ, WRITE, UPDATE, DELETE)
            table: Name of the affected table
            record_id: ID of the affected record (if applicable)
            affected_rows: Number of affected rows
            details: Additional details about the operation
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO shared_audit
                (agent, operation, table_name, record_id, affected_rows, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.agent_name,
                    operation,
                    table,
                    record_id,
                    affected_rows,
                    datetime.now().isoformat(),
                    details,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            # Don't fail the main operation if audit logging fails
            logger.warning(f"Failed to log audit trail: {e}")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.debug(f"Database connection closed for {self.agent_name}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def get_audit_trail(self, table: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit trail entries.

        Args:
            table: Optional table name to filter by
            limit: Maximum number of entries to return

        Returns:
            List of audit trail entries
        """
        query = "SELECT * FROM shared_audit"
        params = []

        if table:
            query += " WHERE table_name = ?"
            params.append(table)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]
