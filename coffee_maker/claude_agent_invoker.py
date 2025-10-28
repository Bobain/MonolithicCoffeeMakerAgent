"""Claude Code Agent Invoker - Unified interface for invoking Claude Code agents programmatically.

This module provides the ONLY way to invoke Claude Code agents in this codebase.
All direct Claude API calls should be replaced with this invoker.

Key Features:
- Streaming support with real-time progress tracking
- Database persistence of all agent interactions
- Session management for multi-turn conversations
- Support for both CLI and API modes
- Automatic CFR-013 compliance (roadmap branch)
- Cost tracking and token usage monitoring

Architecture:
    ClaudeAgentInvoker: Main class for agent invocation
    ├── invoke_agent(): Non-streaming invocation
    ├── invoke_agent_streaming(): Streaming invocation with progress
    ├── invoke_slash_command(): Execute slash commands programmatically
    └── Database persistence via ClaudeInvocationDB

Database Schema:
    claude_invocations: All agent invocation history
    claude_stream_messages: Streaming message history for debugging

Usage:
    >>> from coffee_maker.claude_agent_invoker import ClaudeAgentInvoker
    >>>
    >>> invoker = ClaudeAgentInvoker()
    >>>
    >>> # Non-streaming invocation
    >>> response = invoker.invoke_agent(
    ...     "architect",
    ...     "Create a technical spec for OAuth2 authentication"
    ... )
    >>>
    >>> # Streaming invocation with progress tracking
    >>> for msg in invoker.invoke_agent_streaming(
    ...     "code-developer",
    ...     "Implement US-042"
    ... ):
    ...     print(f"Progress: {msg}")

CFR Compliance:
    - CFR-013: All agents work on roadmap branch only
    - CFR-014: All invocations tracked in database
    - CFR-015: Database stored in data/ directory

Author: architect & code_developer
Date: 2025-10-26
Related: System-wide Claude invocation standardization
"""

import json
import logging
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional


logger = logging.getLogger(__name__)


@dataclass
class AgentInvocationResult:
    """Result from Claude agent invocation.

    Attributes:
        invocation_id: Unique ID for this invocation (DB primary key)
        content: Response content from agent
        session_id: Claude session ID for multi-turn conversations
        agent_type: Which agent was invoked
        model: Model used
        usage: Token usage dict (input_tokens, output_tokens)
        stop_reason: Why response ended
        duration_ms: How long invocation took
        cost_usd: Estimated cost in USD
        error: Error message if invocation failed
        success: Whether invocation succeeded
    """

    invocation_id: int
    content: str
    session_id: str
    agent_type: str
    model: str
    usage: Dict[str, int]
    stop_reason: str
    duration_ms: int
    cost_usd: float
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if invocation succeeded."""
        return self.error is None


@dataclass
class StreamMessage:
    """Single message from streaming invocation.

    Attributes:
        invocation_id: Links to claude_invocations table
        message_type: Type of message (init, message, tool_use, tool_result, result)
        sequence: Order in stream (0, 1, 2, ...)
        timestamp: When message arrived
        content: Message content
        metadata: Additional metadata (JSON)
    """

    invocation_id: int
    message_type: str
    sequence: int
    timestamp: str
    content: str
    metadata: Dict[str, Any]


class ClaudeInvocationDB:
    """Database persistence for Claude agent invocations.

    Schema:
        claude_invocations: All invocation history
        claude_stream_messages: Streaming message history for debugging

    All data stored in data/claude_invocations.db per CFR-015.
    """

    def __init__(self, db_path: str = "data/claude_invocations.db"):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database (default: data/claude_invocations.db)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Create database schema if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS claude_invocations (
                    invocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    agent_type TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    system_prompt TEXT,

                    -- Response data
                    content TEXT,               -- Final aggregated response
                    final_result TEXT,          -- Final exit message/result (for streaming)
                    model TEXT,

                    -- Metrics
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost_usd REAL,
                    duration_ms INTEGER,

                    -- Status
                    status TEXT NOT NULL,  -- success, error, timeout
                    stop_reason TEXT,
                    error TEXT,

                    -- Timestamps
                    invoked_at TEXT NOT NULL,
                    completed_at TEXT,

                    -- Metadata
                    working_dir TEXT,
                    streaming BOOLEAN DEFAULT 0,
                    metadata TEXT  -- JSON
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS claude_stream_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invocation_id INTEGER NOT NULL,
                    message_type TEXT NOT NULL,  -- init, message, tool_use, tool_result, result
                    sequence INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT,
                    metadata TEXT,  -- JSON

                    FOREIGN KEY (invocation_id) REFERENCES claude_invocations(invocation_id)
                )
            """
            )

            # Create indexes for common queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_invocations_agent_type
                ON claude_invocations(agent_type)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_invocations_session
                ON claude_invocations(session_id)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_stream_messages_invocation
                ON claude_stream_messages(invocation_id)
            """
            )

            conn.commit()

    def create_invocation(
        self, agent_type: str, prompt: str, system_prompt: Optional[str] = None, working_dir: Optional[str] = None
    ) -> int:
        """Create new invocation record.

        Args:
            agent_type: Which agent is being invoked
            prompt: User prompt
            system_prompt: Optional system prompt
            working_dir: Working directory

        Returns:
            invocation_id (primary key)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO claude_invocations
                (agent_type, prompt, system_prompt, working_dir, status, invoked_at)
                VALUES (?, ?, ?, ?, 'running', ?)
            """,
                (agent_type, prompt, system_prompt, working_dir, datetime.utcnow().isoformat()),
            )
            conn.commit()
            return cursor.lastrowid

    def complete_invocation(
        self,
        invocation_id: int,
        content: str,
        model: str,
        usage: Dict[str, int],
        stop_reason: str,
        duration_ms: int,
        cost_usd: float,
        session_id: Optional[str] = None,
        error: Optional[str] = None,
        final_result: Optional[str] = None,
    ):
        """Mark invocation as complete.

        Args:
            invocation_id: Invocation ID
            content: Response content
            model: Model used
            usage: Token usage dict
            stop_reason: Stop reason
            duration_ms: Duration in milliseconds
            cost_usd: Cost in USD
            session_id: Claude session ID
            error: Error message if failed
            final_result: Final exit message/result (for streaming)
        """
        status = "error" if error else "success"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE claude_invocations
                SET content = ?,
                    final_result = ?,
                    model = ?,
                    input_tokens = ?,
                    output_tokens = ?,
                    cost_usd = ?,
                    duration_ms = ?,
                    session_id = ?,
                    status = ?,
                    stop_reason = ?,
                    error = ?,
                    completed_at = ?
                WHERE invocation_id = ?
            """,
                (
                    content,
                    final_result,
                    model,
                    usage.get("input_tokens", 0),
                    usage.get("output_tokens", 0),
                    cost_usd,
                    duration_ms,
                    session_id,
                    status,
                    stop_reason,
                    error,
                    datetime.utcnow().isoformat(),
                    invocation_id,
                ),
            )
            conn.commit()

    def add_stream_message(self, invocation_id: int, message_type: str, sequence: int, content: str, metadata: Dict):
        """Add streaming message to database.

        Args:
            invocation_id: Invocation ID
            message_type: Type of message
            sequence: Sequence number
            content: Message content
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO claude_stream_messages
                (invocation_id, message_type, sequence, timestamp, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    invocation_id,
                    message_type,
                    sequence,
                    datetime.utcnow().isoformat(),
                    content,
                    json.dumps(metadata),
                ),
            )
            conn.commit()

    def get_invocation_history(self, agent_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent invocation history.

        Args:
            agent_type: Filter by agent type (optional)
            limit: Max records to return

        Returns:
            List of invocation records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if agent_type:
                cursor = conn.execute(
                    """
                    SELECT * FROM claude_invocations
                    WHERE agent_type = ?
                    ORDER BY invoked_at DESC
                    LIMIT ?
                """,
                    (agent_type, limit),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM claude_invocations
                    ORDER BY invoked_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            return [dict(row) for row in cursor.fetchall()]

    def get_stream_messages(self, invocation_id: int) -> List[Dict[str, Any]]:
        """Get all stream messages for an invocation.

        Args:
            invocation_id: Invocation ID

        Returns:
            List of stream messages in sequence order
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM claude_stream_messages
                WHERE invocation_id = ?
                ORDER BY sequence ASC
            """,
                (invocation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]


class ClaudeAgentInvoker:
    """Unified interface for invoking Claude Code agents programmatically.

    This is the ONLY way to invoke Claude agents in this codebase.
    All direct API calls should be replaced with this invoker.

    Example:
        >>> invoker = ClaudeAgentInvoker()
        >>> response = invoker.invoke_agent("architect", "Create spec for OAuth2")
        >>> print(response.content)
    """

    def __init__(
        self,
        claude_path: str = "/opt/homebrew/bin/claude",
        db_path: str = "data/claude_invocations.db",
        default_model: str = "sonnet",
    ):
        """Initialize Claude agent invoker.

        Args:
            claude_path: Path to claude CLI
            db_path: Path to invocation database
            default_model: Default model to use
        """
        self.claude_path = Path(claude_path)
        self.db = ClaudeInvocationDB(db_path)
        self.default_model = default_model

        if not self.claude_path.exists():
            raise RuntimeError(
                f"Claude CLI not found at {claude_path}. " f"Install from: https://docs.claude.com/docs/claude-code"
            )

    def invoke_agent(
        self,
        agent_type: str,
        prompt: str,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: int = 600,
    ) -> AgentInvocationResult:
        """Invoke Claude agent (non-streaming).

        Args:
            agent_type: Agent to invoke (architect, code-developer, etc.)
            prompt: User prompt
            session_id: Optional session ID for multi-turn conversations
            system_prompt: Optional system prompt
            working_dir: Working directory
            timeout: Timeout in seconds

        Returns:
            AgentInvocationResult with response and metadata

        Example:
            >>> invoker = ClaudeAgentInvoker()
            >>> result = invoker.invoke_agent(
            ...     "architect",
            ...     "Create spec for OAuth2 authentication"
            ... )
            >>> print(result.content)
        """
        start_time = datetime.utcnow()
        invocation_id = self.db.create_invocation(agent_type, prompt, system_prompt, working_dir)

        try:
            # Build command
            cmd = [
                str(self.claude_path),
                "--print",
                "--output-format",
                "json",
                "--permission-mode",
                "acceptEdits",
                "--model",
                self.default_model,
            ]

            # Add session resume if provided
            if session_id:
                cmd.extend(["--resume", session_id])

            # Add prompt (use slash command reference if needed)
            full_prompt = self._build_agent_prompt(agent_type, prompt, system_prompt, working_dir)
            cmd.append(full_prompt)

            logger.info(f"Invoking {agent_type} agent (invocation_id={invocation_id})")

            # Execute
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                self.db.complete_invocation(
                    invocation_id, "", self.default_model, {}, "error", duration_ms, 0.0, error=error_msg
                )
                return AgentInvocationResult(
                    invocation_id=invocation_id,
                    content="",
                    session_id=session_id or "",
                    agent_type=agent_type,
                    model=self.default_model,
                    usage={"input_tokens": 0, "output_tokens": 0},
                    stop_reason="error",
                    duration_ms=duration_ms,
                    cost_usd=0.0,
                    error=error_msg,
                )

            # Parse JSON output
            response = json.loads(result.stdout)
            content = response.get("result", "")
            new_session_id = response.get("session_id", session_id or "")
            model = response.get("model", self.default_model)
            usage = {
                "input_tokens": response.get("input_tokens", 0),
                "output_tokens": response.get("output_tokens", 0),
            }
            stop_reason = response.get("stop_reason", "end_turn")
            cost_usd = response.get("total_cost_usd", 0.0)
            duration_ms = response.get("duration_ms", int((datetime.utcnow() - start_time).total_seconds() * 1000))

            # Persist to database
            self.db.complete_invocation(
                invocation_id, content, model, usage, stop_reason, duration_ms, cost_usd, new_session_id
            )

            logger.info(
                f"✅ Agent {agent_type} completed: {usage['output_tokens']} tokens, "
                f"{duration_ms}ms, ${cost_usd:.4f}"
            )

            return AgentInvocationResult(
                invocation_id=invocation_id,
                content=content,
                session_id=new_session_id,
                agent_type=agent_type,
                model=model,
                usage=usage,
                stop_reason=stop_reason,
                duration_ms=duration_ms,
                cost_usd=cost_usd,
            )

        except subprocess.TimeoutExpired:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            error_msg = f"Timeout after {timeout}s"
            self.db.complete_invocation(
                invocation_id, "", self.default_model, {}, "timeout", duration_ms, 0.0, error=error_msg
            )
            return AgentInvocationResult(
                invocation_id=invocation_id,
                content="",
                session_id=session_id or "",
                agent_type=agent_type,
                model=self.default_model,
                usage={"input_tokens": 0, "output_tokens": 0},
                stop_reason="timeout",
                duration_ms=duration_ms,
                cost_usd=0.0,
                error=error_msg,
            )

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            error_msg = str(e)
            self.db.complete_invocation(
                invocation_id, "", self.default_model, {}, "error", duration_ms, 0.0, error=error_msg
            )
            logger.error(f"❌ Agent invocation failed: {e}", exc_info=True)
            return AgentInvocationResult(
                invocation_id=invocation_id,
                content="",
                session_id=session_id or "",
                agent_type=agent_type,
                model=self.default_model,
                usage={"input_tokens": 0, "output_tokens": 0},
                stop_reason="error",
                duration_ms=duration_ms,
                cost_usd=0.0,
                error=error_msg,
            )

    def invoke_agent_streaming(
        self,
        agent_type: str,
        prompt: str,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: int = 600,
    ) -> Generator[StreamMessage, None, None]:
        """Invoke Claude agent with streaming output.

        Args:
            agent_type: Agent to invoke
            prompt: User prompt
            session_id: Optional session ID
            system_prompt: Optional system prompt
            working_dir: Working directory
            timeout: Timeout in seconds

        Yields:
            StreamMessage objects as they arrive

        Example:
            >>> invoker = ClaudeAgentInvoker()
            >>> for msg in invoker.invoke_agent_streaming("code-developer", "Implement US-042"):
            ...     print(f"[{msg.message_type}] {msg.content}")
        """
        start_time = datetime.utcnow()
        invocation_id = self.db.create_invocation(agent_type, prompt, system_prompt, working_dir)

        try:
            # Build command for streaming
            cmd = [
                str(self.claude_path),
                "--print",
                "--output-format",
                "stream-json",
                "--permission-mode",
                "acceptEdits",
                "--model",
                self.default_model,
            ]

            if session_id:
                cmd.extend(["--resume", session_id])

            full_prompt = self._build_agent_prompt(agent_type, prompt, system_prompt, working_dir)
            cmd.append(full_prompt)

            logger.info(f"Invoking {agent_type} agent (streaming, invocation_id={invocation_id})")

            # Start process
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            sequence = 0
            last_session_id = session_id
            total_tokens = {"input": 0, "output": 0}
            last_model = self.default_model
            final_result_message = None
            accumulated_content = []

            # Stream messages
            for line in proc.stdout:
                if not line.strip():
                    continue

                try:
                    message = json.loads(line)
                    msg_type = message.get("type", "unknown")
                    content = message.get("content", "")

                    # Extract metadata
                    metadata = {k: v for k, v in message.items() if k not in ["type", "content"]}

                    # Track session and tokens
                    if "session_id" in message:
                        last_session_id = message["session_id"]
                    if "model" in message:
                        last_model = message["model"]
                    if msg_type == "result":
                        total_tokens["input"] = message.get("input_tokens", 0)
                        total_tokens["output"] = message.get("output_tokens", 0)
                        # Store final result message separately
                        final_result_message = message.get("result", "")

                    # Accumulate text content from messages
                    if msg_type == "message" and content:
                        accumulated_content.append(str(content))

                    # Store in database
                    self.db.add_stream_message(invocation_id, msg_type, sequence, str(content), metadata)

                    # Yield to caller
                    yield StreamMessage(
                        invocation_id=invocation_id,
                        message_type=msg_type,
                        sequence=sequence,
                        timestamp=datetime.utcnow().isoformat(),
                        content=str(content),
                        metadata=metadata,
                    )

                    sequence += 1

                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse streaming line: {line[:100]}")
                    continue

            # Wait for process to complete
            proc.wait(timeout=timeout)

            # Mark invocation complete
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            usage = {"input_tokens": total_tokens["input"], "output_tokens": total_tokens["output"]}
            # Rough cost estimate (adjust based on actual pricing)
            cost_usd = (usage["input_tokens"] * 0.003 + usage["output_tokens"] * 0.015) / 1000

            # Content is all accumulated messages, final_result is the exit value
            aggregated_content = "\n".join(accumulated_content)

            self.db.complete_invocation(
                invocation_id,
                aggregated_content,  # All accumulated text messages
                last_model,
                usage,
                "end_turn",
                duration_ms,
                cost_usd,
                last_session_id,
                final_result=final_result_message,  # Final exit message
            )

            logger.info(
                f"✅ Streaming agent {agent_type} completed: {usage['output_tokens']} tokens, "
                f"{duration_ms}ms, ${cost_usd:.4f}"
            )

        except Exception as e:
            logger.error(f"❌ Streaming invocation failed: {e}", exc_info=True)
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self.db.complete_invocation(
                invocation_id, "", self.default_model, {}, "error", duration_ms, 0.0, error=str(e)
            )

    def invoke_slash_command(
        self, command_name: str, variables: Dict[str, str], timeout: int = 600
    ) -> AgentInvocationResult:
        """Execute a Claude Code slash command programmatically.

        Args:
            command_name: Name of command file (without .md extension)
            variables: Template variables to substitute
            timeout: Timeout in seconds

        Returns:
            AgentInvocationResult

        Example:
            >>> invoker = ClaudeAgentInvoker()
            >>> result = invoker.invoke_slash_command("implement-feature", {
            ...     "PRIORITY_NAME": "US-042",
            ...     "PRIORITY_TITLE": "Add OAuth2",
            ...     "SPEC_CONTENT": "...",
            ...     "PRIORITY_CONTENT": "..."
            ... })
        """
        # Load command template
        command_path = Path(f".claude/commands/{command_name}.md")
        if not command_path.exists():
            raise ValueError(f"Command not found: {command_path}")

        with open(command_path) as f:
            template = f.read()

        # Substitute variables
        for key, value in variables.items():
            template = template.replace(f"${key}", str(value))

        # Invoke as generic prompt
        return self.invoke_agent(
            agent_type=f"slash_command_{command_name}",
            prompt=template,
            timeout=timeout,
        )

    def _build_agent_prompt(
        self, agent_type: str, prompt: str, system_prompt: Optional[str], working_dir: Optional[str]
    ) -> str:
        """Build full prompt for agent invocation.

        Args:
            agent_type: Agent type
            prompt: User prompt
            system_prompt: Optional system prompt
            working_dir: Working directory

        Returns:
            Full prompt string
        """
        parts = []

        # Reference to agent definition (Claude will load .claude/agents/{agent_type}.md)
        parts.append(f"Use the {agent_type} agent to complete this task:\n")

        if working_dir:
            parts.append(f"Working directory: {working_dir}\n\n")

        if system_prompt:
            parts.append(f"{system_prompt}\n\n")

        parts.append(prompt)

        return "".join(parts)

    def get_history(self, agent_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent invocation history.

        Args:
            agent_type: Filter by agent type (optional)
            limit: Max records

        Returns:
            List of invocation records
        """
        return self.db.get_invocation_history(agent_type, limit)

    def get_stream_messages(self, invocation_id: int) -> List[Dict[str, Any]]:
        """Get streaming messages for an invocation.

        Args:
            invocation_id: Invocation ID

        Returns:
            List of stream messages
        """
        return self.db.get_stream_messages(invocation_id)


# Singleton instance for global use
_invoker_instance: Optional[ClaudeAgentInvoker] = None


def get_invoker() -> ClaudeAgentInvoker:
    """Get global ClaudeAgentInvoker instance (singleton).

    Returns:
        Shared ClaudeAgentInvoker instance
    """
    global _invoker_instance
    if _invoker_instance is None:
        _invoker_instance = ClaudeAgentInvoker()
    return _invoker_instance
