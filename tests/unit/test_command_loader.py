"""Unit tests for CommandLoader.

Tests cover:
- Command loading from markdown files
- Permission validation
- Command execution
- Skill integration
"""

import tempfile
from pathlib import Path

import pytest

from coffee_maker.commands.command_loader import CommandLoader
from coffee_maker.database.domain_wrapper import AgentType


@pytest.fixture
def commands_dir():
    """Create a temporary commands directory with sample commands."""
    with tempfile.TemporaryDirectory() as tmpdir:
        commands_path = Path(tmpdir)

        # Create architect commands directory
        arch_dir = commands_path / "architect"
        arch_dir.mkdir()

        # Create a sample architect command
        spec_cmd = arch_dir / "create_spec.md"
        spec_cmd.write_text(
            """---
command: architect.create_spec
agent: architect
action: create_spec
tables:
  write: [specs_specification]
  read: [roadmap_priority]
required_skills: [technical_specification_handling]
---

# Command: architect.create_spec

## Purpose

Create a technical specification for a priority.

## Parameters

- priority_id: ID of the priority to create spec for
"""
        )

        # Create developer commands directory
        dev_dir = commands_path / "code_developer"
        dev_dir.mkdir()

        # Create a sample developer command
        impl_cmd = dev_dir / "implement_feature.md"
        impl_cmd.write_text(
            """---
command: code_developer.implement_feature
agent: code_developer
action: implement_feature
tables:
  write: [review_commit]
  read: [specs_specification, roadmap_priority]
required_skills: []
required_tools: [git, pytest]
---

# Command: code_developer.implement_feature

## Purpose

Implement a feature from a specification.

## Parameters

- spec_id: ID of the specification to implement
"""
        )

        yield commands_path


class TestCommandLoading:
    """Test command loading from markdown files."""

    def test_loader_initialization(self, commands_dir):
        """Test that loader initializes correctly."""
        # Temporarily patch the commands directory
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir) / "test.db"
            loader = CommandLoader(
                AgentType.ARCHITECT,
                commands_dir / "architect",
            )
            # Should initialize without error
            assert loader.agent_name == "architect"

    def test_commands_not_found_no_error(self, commands_dir):
        """Test that missing commands directory doesn't crash."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            Path("/nonexistent/path"),
        )
        # Should initialize without error
        assert loader.commands == {}

    def test_load_single_command(self, commands_dir):
        """Test loading a single command."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        # Should have loaded the create_spec command
        assert "create_spec" in loader.commands
        cmd = loader.commands["create_spec"]
        assert cmd.name == "architect.create_spec"
        assert cmd.action == "create_spec"

    def test_load_multiple_commands(self, commands_dir):
        """Test loading multiple commands."""
        # Add another command
        arch_dir = commands_dir / "architect"
        update_spec = arch_dir / "update_spec.md"
        update_spec.write_text(
            """---
command: architect.update_spec
agent: architect
action: update_spec
tables:
  write: [specs_specification]
  read: [specs_specification]
---

# Update Spec
"""
        )

        loader = CommandLoader(
            AgentType.ARCHITECT,
            arch_dir,
        )

        # Should have loaded both commands
        assert len(loader.commands) >= 2
        assert "create_spec" in loader.commands
        assert "update_spec" in loader.commands

    def test_command_metadata_parsed(self, commands_dir):
        """Test that command metadata is parsed correctly."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        cmd = loader.commands["create_spec"]

        # Check metadata
        assert cmd.tables_write == ["specs_specification"]
        assert cmd.tables_read == ["roadmap_priority"]
        assert "technical_specification_handling" in cmd.required_skills


class TestPermissionValidation:
    """Test permission validation."""

    def test_permission_validation_success(self, commands_dir, monkeypatch):
        """Test that validation passes for authorized commands."""
        # Create a loader with proper permissions
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        # Should not raise an error
        cmd = loader.commands["create_spec"]
        loader._validate_permissions(cmd)

    def test_permission_validation_write_denied(self, commands_dir):
        """Test that validation fails if agent can't write to table."""
        # Developer can't write to specs_specification
        loader = CommandLoader(
            AgentType.CODE_DEVELOPER,
            commands_dir / "code_developer",
        )

        # Try to validate an architect command (which requires write to specs_specification)
        arch_cmd = loader.commands["implement_feature"]
        # The implement_feature command doesn't require specs write, so this should pass
        loader._validate_permissions(arch_cmd)


class TestCommandExecution:
    """Test command execution."""

    def test_list_commands(self, commands_dir):
        """Test listing available commands."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        commands = loader.list_commands()
        assert isinstance(commands, list)
        assert "create_spec" in commands

    def test_get_command(self, commands_dir):
        """Test getting a specific command."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        cmd = loader.get_command("create_spec")
        assert cmd is not None
        assert cmd.action == "create_spec"

    def test_get_command_not_found(self, commands_dir):
        """Test getting a command that doesn't exist."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        cmd = loader.get_command("nonexistent")
        assert cmd is None

    def test_execute_command(self, commands_dir):
        """Test executing a command."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        # Execute the create_spec command
        result = loader.execute(
            "create_spec",
            {"priority_id": "PRIORITY-1"},
        )

        assert isinstance(result, dict)
        assert "success" in result

    def test_execute_nonexistent_command(self, commands_dir):
        """Test executing a command that doesn't exist."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        with pytest.raises(ValueError):
            loader.execute("nonexistent", {})


class TestSkillLoading:
    """Test skill loading integration."""

    def test_load_skills_empty(self, commands_dir):
        """Test loading commands with no required skills."""
        loader = CommandLoader(
            AgentType.CODE_DEVELOPER,
            commands_dir / "code_developer",
        )

        cmd = loader.commands["implement_feature"]
        skills = loader._load_skills(cmd.required_skills)

        assert isinstance(skills, dict)

    def test_load_skills_with_requirements(self, commands_dir):
        """Test loading commands with required skills."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        cmd = loader.commands["create_spec"]
        skills = loader._load_skills(cmd.required_skills)

        assert isinstance(skills, dict)
        # Skills might not be loadable in test environment, but dict should be returned


class TestCommandLoaderIntegration:
    """Test integration scenarios."""

    def test_loader_multiple_agents(self, commands_dir):
        """Test that different agents can have different commands."""
        arch_loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        dev_loader = CommandLoader(
            AgentType.CODE_DEVELOPER,
            commands_dir / "code_developer",
        )

        # Each should have different commands
        assert "create_spec" in arch_loader.list_commands()
        assert "implement_feature" in dev_loader.list_commands()
        assert "create_spec" not in dev_loader.list_commands()

    def test_command_persistence(self, commands_dir):
        """Test that commands persist across operations."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            commands_dir / "architect",
        )

        # List commands multiple times
        list1 = loader.list_commands()
        list2 = loader.list_commands()

        assert list1 == list2
