"""Unit tests for Command base class.

Tests cover:
- Command initialization
- Metadata access
- Execute method
"""

from pathlib import Path

import pytest

from coffee_maker.commands.command import Command
from coffee_maker.database.domain_wrapper import DomainWrapper, AgentType


@pytest.fixture
def sample_command():
    """Create a sample command for testing."""
    return Command(
        name="test.sample_command",
        agent="architect",
        action="sample_command",
        tables_write=["specs_specification"],
        tables_read=["roadmap_priority"],
        required_skills=["test_skill"],
        required_tools=["git"],
        content="# Sample Command\n\nThis is a test command.",
        source_file="/test/path/command.md",
    )


class TestCommandInitialization:
    """Test command initialization."""

    def test_command_creation(self, sample_command):
        """Test that commands can be created with all metadata."""
        assert sample_command.name == "test.sample_command"
        assert sample_command.agent == "architect"
        assert sample_command.action == "sample_command"

    def test_command_with_defaults(self):
        """Test that commands work with minimal metadata."""
        cmd = Command(
            name="minimal.command",
            agent="developer",
            action="minimal",
        )
        assert cmd.tables_write == []
        assert cmd.tables_read == []
        assert cmd.required_skills == []
        assert cmd.required_tools == []
        assert cmd.content == ""
        assert cmd.source_file == ""


class TestCommandMetadata:
    """Test command metadata access."""

    def test_tables_write_access(self, sample_command):
        """Test accessing write tables."""
        assert "specs_specification" in sample_command.tables_write

    def test_tables_read_access(self, sample_command):
        """Test accessing read tables."""
        assert "roadmap_priority" in sample_command.tables_read

    def test_required_skills_access(self, sample_command):
        """Test accessing required skills."""
        assert "test_skill" in sample_command.required_skills

    def test_required_tools_access(self, sample_command):
        """Test accessing required tools."""
        assert "git" in sample_command.required_tools

    def test_content_access(self, sample_command):
        """Test accessing command content."""
        assert "Sample Command" in sample_command.content

    def test_source_file_access(self, sample_command):
        """Test accessing source file path."""
        assert "command.md" in sample_command.source_file


class TestCommandExecution:
    """Test command execution."""

    def test_execute_returns_result(self, sample_command, tmpdir):
        """Test that execute returns a result dictionary."""
        db_path = Path(tmpdir) / "test.db"
        db = DomainWrapper(AgentType.ARCHITECT, str(db_path))

        result = sample_command.execute(db, {"test_param": "value"})

        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True

    def test_execute_includes_params(self, sample_command, tmpdir):
        """Test that execute includes parameters in result."""
        db_path = Path(tmpdir) / "test.db"
        db = DomainWrapper(AgentType.ARCHITECT, str(db_path))

        params = {"priority_id": "PRIORITY-1"}
        result = sample_command.execute(db, params)

        assert result["params"] == params

    def test_execute_includes_command_name(self, sample_command, tmpdir):
        """Test that execute includes command name in result."""
        db_path = Path(tmpdir) / "test.db"
        db = DomainWrapper(AgentType.ARCHITECT, str(db_path))

        result = sample_command.execute(db, {})

        assert result["command"] == sample_command.name


class TestCommandRepresentation:
    """Test command string representations."""

    def test_repr(self, sample_command):
        """Test __repr__ method."""
        repr_str = repr(sample_command)
        assert "test.sample_command" in repr_str
        assert "architect" in repr_str
        assert "sample_command" in repr_str

    def test_str(self, sample_command):
        """Test __str__ method."""
        str_repr = str(sample_command)
        assert "test.sample_command" in str_repr
        assert "architect" in str_repr


class TestCommandEdgeCases:
    """Test edge cases."""

    def test_command_with_empty_lists(self):
        """Test command with empty permission lists."""
        cmd = Command(
            name="test.empty",
            agent="test",
            action="empty",
            tables_write=[],
            tables_read=[],
        )
        assert cmd.tables_write == []
        assert cmd.tables_read == []

    def test_command_with_multiple_tables(self):
        """Test command with multiple table permissions."""
        cmd = Command(
            name="test.multi",
            agent="test",
            action="multi",
            tables_write=["table1", "table2", "table3"],
            tables_read=["table4", "table5"],
        )
        assert len(cmd.tables_write) == 3
        assert len(cmd.tables_read) == 2
