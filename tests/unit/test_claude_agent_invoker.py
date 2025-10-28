"""Tests for ClaudeAgentInvoker module.

This module tests the unified Claude agent invocation interface.

Test Coverage:
    - Database schema creation
    - Non-streaming invocation
    - Streaming invocation
    - Slash command execution
    - Session management
    - Error handling
    - Database persistence
"""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from coffee_maker.claude_agent_invoker import (
    ClaudeAgentInvoker,
    ClaudeInvocationDB,
    get_invoker,
)


class TestClaudeInvocationDB:
    """Test database persistence layer."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        Path(db_path).unlink(missing_ok=True)

    def test_schema_creation(self, temp_db):
        """Test database schema is created correctly."""
        ClaudeInvocationDB(temp_db)

        with sqlite3.connect(temp_db) as conn:
            # Check tables exist
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN ('claude_invocations', 'claude_stream_messages')
            """
            )
            tables = {row[0] for row in cursor.fetchall()}
            assert "claude_invocations" in tables
            assert "claude_stream_messages" in tables

            # Check indexes exist
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master WHERE type='index'
            """
            )
            indexes = {row[0] for row in cursor.fetchall()}
            assert "idx_invocations_agent_type" in indexes
            assert "idx_invocations_session" in indexes
            assert "idx_stream_messages_invocation" in indexes

    def test_create_invocation(self, temp_db):
        """Test creating invocation record."""
        db = ClaudeInvocationDB(temp_db)
        invocation_id = db.create_invocation(
            agent_type="architect", prompt="Create spec", system_prompt="You are architect", working_dir="/tmp"
        )

        assert invocation_id > 0

        # Verify record
        with sqlite3.connect(temp_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM claude_invocations WHERE invocation_id = ?", (invocation_id,))
            row = dict(cursor.fetchone())

            assert row["agent_type"] == "architect"
            assert row["prompt"] == "Create spec"
            assert row["system_prompt"] == "You are architect"
            assert row["working_dir"] == "/tmp"
            assert row["status"] == "running"

    def test_complete_invocation(self, temp_db):
        """Test completing invocation."""
        db = ClaudeInvocationDB(temp_db)
        invocation_id = db.create_invocation("architect", "Create spec")

        db.complete_invocation(
            invocation_id=invocation_id,
            content="Spec created",
            model="sonnet",
            usage={"input_tokens": 100, "output_tokens": 200},
            stop_reason="end_turn",
            duration_ms=5000,
            cost_usd=0.05,
            session_id="session-123",
        )

        # Verify
        with sqlite3.connect(temp_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM claude_invocations WHERE invocation_id = ?", (invocation_id,))
            row = dict(cursor.fetchone())

            assert row["content"] == "Spec created"
            assert row["model"] == "sonnet"
            assert row["input_tokens"] == 100
            assert row["output_tokens"] == 200
            assert row["cost_usd"] == 0.05
            assert row["duration_ms"] == 5000
            assert row["session_id"] == "session-123"
            assert row["status"] == "success"
            assert row["stop_reason"] == "end_turn"

    def test_add_stream_message(self, temp_db):
        """Test adding stream messages."""
        db = ClaudeInvocationDB(temp_db)
        invocation_id = db.create_invocation("code-developer", "Implement feature")

        # Add stream messages
        db.add_stream_message(invocation_id, "init", 0, "Starting", {"model": "sonnet"})
        db.add_stream_message(invocation_id, "message", 1, "Implementing...", {"tool": "Write"})
        db.add_stream_message(invocation_id, "result", 2, "Done", {"tokens": 500})

        # Verify
        messages = db.get_stream_messages(invocation_id)
        assert len(messages) == 3
        assert messages[0]["message_type"] == "init"
        assert messages[1]["message_type"] == "message"
        assert messages[2]["message_type"] == "result"
        assert json.loads(messages[1]["metadata"])["tool"] == "Write"

    def test_get_invocation_history(self, temp_db):
        """Test retrieving invocation history."""
        db = ClaudeInvocationDB(temp_db)

        # Create multiple invocations
        db.create_invocation("architect", "Spec 1")
        db.create_invocation("code-developer", "Implement 1")
        db.create_invocation("architect", "Spec 2")

        # Get all history
        history = db.get_invocation_history(limit=10)
        assert len(history) == 3

        # Get filtered history
        architect_history = db.get_invocation_history(agent_type="architect", limit=10)
        assert len(architect_history) == 2
        assert all(row["agent_type"] == "architect" for row in architect_history)


class TestClaudeAgentInvoker:
    """Test agent invocation logic."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def mock_claude_cli(self):
        """Mock Claude CLI command."""
        with patch("subprocess.run") as mock_run:
            yield mock_run

    def test_invoke_agent_success(self, temp_db, mock_claude_cli):
        """Test successful agent invocation."""
        # Mock successful response
        mock_response = {
            "result": "Spec created successfully",
            "session_id": "session-abc",
            "model": "claude-sonnet-4",
            "input_tokens": 150,
            "output_tokens": 300,
            "total_cost_usd": 0.045,
            "duration_ms": 3000,
            "stop_reason": "end_turn",
        }

        mock_claude_cli.return_value = Mock(returncode=0, stdout=json.dumps(mock_response), stderr="")

        # Invoke agent
        invoker = ClaudeAgentInvoker(db_path=temp_db)
        result = invoker.invoke_agent("architect", "Create spec for OAuth2")

        # Verify result
        assert result.success
        assert result.content == "Spec created successfully"
        assert result.session_id == "session-abc"
        assert result.model == "claude-sonnet-4"
        assert result.usage["input_tokens"] == 150
        assert result.usage["output_tokens"] == 300
        assert result.cost_usd == 0.045

        # Verify database persistence
        history = invoker.get_history()
        assert len(history) == 1
        assert history[0]["agent_type"] == "architect"
        assert history[0]["status"] == "success"

    def test_invoke_agent_error(self, temp_db, mock_claude_cli):
        """Test agent invocation error handling."""
        # Mock error response
        mock_claude_cli.return_value = Mock(returncode=1, stdout="", stderr="API rate limit exceeded")

        invoker = ClaudeAgentInvoker(db_path=temp_db)
        result = invoker.invoke_agent("architect", "Create spec")

        # Verify error handling
        assert not result.success
        assert result.error == "API rate limit exceeded"
        assert result.content == ""

        # Verify database persistence
        history = invoker.get_history()
        assert len(history) == 1
        assert history[0]["status"] == "error"
        assert history[0]["error"] == "API rate limit exceeded"

    def test_invoke_agent_timeout(self, temp_db, mock_claude_cli):
        """Test timeout handling."""
        import subprocess

        mock_claude_cli.side_effect = subprocess.TimeoutExpired("claude", 10)

        invoker = ClaudeAgentInvoker(db_path=temp_db)
        result = invoker.invoke_agent("code-developer", "Implement feature", timeout=10)

        assert not result.success
        assert "Timeout" in result.error
        assert result.stop_reason == "timeout"

    def test_invoke_slash_command(self, temp_db, mock_claude_cli):
        """Test slash command invocation."""
        # Create temporary command file
        with tempfile.TemporaryDirectory() as tmpdir:
            command_dir = Path(tmpdir) / ".claude" / "commands"
            command_dir.mkdir(parents=True)

            command_file = command_dir / "test-command.md"
            command_file.write_text(
                """
# Test Command

Priority: $PRIORITY_NAME
Title: $PRIORITY_TITLE

Do something with this priority.
"""
            )

            # Mock response
            mock_claude_cli.return_value = Mock(
                returncode=0,
                stdout=json.dumps(
                    {
                        "result": "Command executed",
                        "session_id": "",
                        "model": "sonnet",
                        "input_tokens": 50,
                        "output_tokens": 100,
                        "total_cost_usd": 0.01,
                        "duration_ms": 1000,
                        "stop_reason": "end_turn",
                    }
                ),
            )

            # Patch command path lookup
            with patch("pathlib.Path.exists", return_value=True), patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = command_file.read_text()

                invoker = ClaudeAgentInvoker(db_path=temp_db)
                result = invoker.invoke_slash_command(
                    "test-command", {"PRIORITY_NAME": "US-042", "PRIORITY_TITLE": "Add OAuth2"}
                )

                assert result.success

    def test_streaming_invocation(self, temp_db):
        """Test streaming invocation."""
        # Mock Popen for streaming
        mock_proc = MagicMock()
        mock_proc.stdout = [
            json.dumps({"type": "init", "session_id": "session-123"}),
            json.dumps({"type": "message", "content": "Starting implementation"}),
            json.dumps({"type": "tool_use", "name": "Write", "content": "Creating file"}),
            json.dumps(
                {
                    "type": "result",
                    "input_tokens": 100,
                    "output_tokens": 200,
                    "model": "sonnet",
                    "stop_reason": "end_turn",
                }
            ),
        ]
        mock_proc.wait.return_value = 0

        with patch("subprocess.Popen", return_value=mock_proc):
            invoker = ClaudeAgentInvoker(db_path=temp_db)
            messages = list(invoker.invoke_agent_streaming("code-developer", "Implement US-042"))

            # Verify messages
            assert len(messages) == 4
            assert messages[0].message_type == "init"
            assert messages[1].message_type == "message"
            assert messages[2].message_type == "tool_use"
            assert messages[3].message_type == "result"

            # Verify database persistence
            invocation_id = messages[0].invocation_id
            stream_messages = invoker.get_stream_messages(invocation_id)
            assert len(stream_messages) == 4


def test_get_invoker_singleton():
    """Test singleton pattern for get_invoker()."""
    invoker1 = get_invoker()
    invoker2 = get_invoker()

    # Should be same instance
    assert invoker1 is invoker2
