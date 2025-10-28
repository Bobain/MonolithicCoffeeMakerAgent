"""Database-backed message queue for inter-agent communication.

Replaces file-based message passing with SQLite database for better:
- Concurrency handling
- Message history/audit trail
- Query performance
- Reliability

Schema:
    agent_messages table stores all inter-agent messages
    Indexes on (to_agent, status) and (priority, created_at) for fast queries
"""

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class MessageType(Enum):
    """Types of messages that can be sent between agents."""

    USER_REQUEST = "user_request"
    TASK_REQUEST = "task_request"
    USER_RESPONSE = "user_response"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    SPEC_REQUEST = "spec_request"
    SPEC_RESPONSE = "spec_response"


# Import AgentType from agent_registry for backward compatibility
# This allows old code importing from message_queue to still work
try:
    from coffee_maker.autonomous.agent_registry import AgentType
except ImportError:
    # Fallback if agent_registry not available
    class AgentType(Enum):  # type: ignore
        """Fallback AgentType enum."""

        USER_LISTENER = "user_listener"
        ARCHITECT = "architect"
        CODE_DEVELOPER = "code_developer"
        PROJECT_MANAGER = "project_manager"
        CODE_REVIEWER = "code_reviewer"
        ASSISTANT = "assistant"
        ORCHESTRATOR = "orchestrator"
        UX_DESIGN_EXPERT = "ux_design_expert"


@dataclass
class Message:
    """Message for inter-agent communication.

    Attributes:
        sender: Agent that sent the message
        recipient: Target agent for the message
        type: Type of message (from MessageType enum)
        payload: Message content/data
        priority: Message priority (1=highest, 10=lowest)
        message_id: Unique message ID (auto-generated)
        timestamp: When message was created (auto-generated)
    """

    sender: str
    recipient: str
    type: str
    payload: Dict[str, Any]
    priority: int = 5
    message_id: Optional[str] = None
    timestamp: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())


class MessageQueue:
    """Database-backed message queue for inter-agent communication.

    Replaces file-based inbox/*.json system with SQLite database.
    Provides message persistence, history, and concurrent access.

    Example:
        >>> queue = MessageQueue()
        >>> queue.send_message(
        ...     from_agent="code_developer",
        ...     to_agent="architect",
        ...     message_type="spec_request",
        ...     content={"priority": "US-060"},
        ...     priority="urgent"
        ... )
        >>> messages = queue.get_pending_messages("architect", urgent_only=True)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize message queue.

        Args:
            db_path: Path to SQLite database (default: data/agent_messages.db)
        """
        if db_path is None:
            db_path = Path("data/agent_messages.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema if not exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create agent_messages table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_messages (
                    message_id TEXT PRIMARY KEY,
                    from_agent TEXT NOT NULL,
                    to_agent TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    content TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    error TEXT
                )
            """
            )

            # Create indexes for fast queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_to_status
                ON agent_messages(to_agent, status)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_priority
                ON agent_messages(priority, created_at)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_created
                ON agent_messages(created_at)
            """
            )

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Error initializing message queue database: {e}")

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: Dict,
        priority: str = "normal",
    ) -> str:
        """Send a message to another agent.

        Args:
            from_agent: Sending agent type
            to_agent: Recipient agent type
            message_type: Type of message (spec_request, demo_request, etc.)
            content: Message payload dict
            priority: "urgent" or "normal"

        Returns:
            Message ID

        Raises:
            sqlite3.Error: If database write fails
        """
        message_id = f"{message_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO agent_messages
                (message_id, from_agent, to_agent, message_type, priority, content, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    message_id,
                    from_agent,
                    to_agent,
                    message_type,
                    priority,
                    json.dumps(content),
                    "pending",
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"📨 Sent {priority} message to {to_agent}: {message_type}")
            return message_id

        except sqlite3.Error as e:
            logger.error(f"Error sending message: {e}")
            raise

    def get_pending_messages(self, to_agent: str, urgent_only: bool = False, limit: Optional[int] = None) -> List[Dict]:
        """Get pending messages for an agent.

        Args:
            to_agent: Agent type to get messages for
            urgent_only: If True, only return urgent messages
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if urgent_only:
                query = """
                    SELECT * FROM agent_messages
                    WHERE to_agent = ? AND status = 'pending' AND priority = 'urgent'
                    ORDER BY created_at ASC
                """
                params = [to_agent]
            else:
                query = """
                    SELECT * FROM agent_messages
                    WHERE to_agent = ? AND status = 'pending'
                    ORDER BY
                        CASE priority WHEN 'urgent' THEN 1 ELSE 2 END,
                        created_at ASC
                """
                params = [to_agent]

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            messages = []
            for row in rows:
                message = dict(row)
                message["content"] = json.loads(message["content"])
                messages.append(message)

            return messages

        except sqlite3.Error as e:
            logger.error(f"Error getting pending messages: {e}")
            return []

    def mark_message_processed(self, message_id: str, error: Optional[str] = None) -> None:
        """Mark a message as processed.

        Args:
            message_id: ID of message to mark
            error: Optional error message if processing failed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            status = "failed" if error else "completed"

            cursor.execute(
                """
                UPDATE agent_messages
                SET status = ?, processed_at = ?, error = ?
                WHERE message_id = ?
            """,
                (status, datetime.now().isoformat(), error, message_id),
            )

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Error marking message processed: {e}")

    def delete_old_messages(self, days: int = 30) -> int:
        """Delete messages older than specified days.

        Args:
            days: Delete messages older than this many days

        Returns:
            Number of messages deleted
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)

            cursor.execute(
                """
                DELETE FROM agent_messages
                WHERE created_at < ? AND status != 'pending'
            """,
                (cutoff_date.isoformat(),),
            )

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"🗑️  Deleted {deleted_count} messages older than {days} days")
            return deleted_count

        except sqlite3.Error as e:
            logger.error(f"Error deleting old messages: {e}")
            return 0

    def get_message_stats(self, agent: Optional[str] = None) -> Dict:
        """Get message statistics.

        Args:
            agent: Optional agent type to filter by

        Returns:
            Dict with message counts by status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if agent:
                cursor.execute(
                    """
                    SELECT status, COUNT(*) as count
                    FROM agent_messages
                    WHERE to_agent = ?
                    GROUP BY status
                """,
                    (agent,),
                )
            else:
                cursor.execute(
                    """
                    SELECT status, COUNT(*) as count
                    FROM agent_messages
                    GROUP BY status
                """
                )

            stats = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()

            return stats

        except sqlite3.Error as e:
            logger.error(f"Error getting message stats: {e}")
            return {}
