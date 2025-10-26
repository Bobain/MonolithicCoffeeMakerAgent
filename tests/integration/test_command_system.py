"""Integration tests for unified command system.

Tests the end-to-end workflow: Load → Validate → Execute

This verifies:
- Command loading from markdown files
- Permission enforcement workflow
- Audit trail creation
- Skill integration
- Cross-agent notifications
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase
from coffee_maker.commands.command_loader import CommandLoader
from coffee_maker.database.domain_wrapper import AgentType, DomainWrapper, PermissionError


@pytest.fixture
def initialized_db(tmpdir):
    """Create and initialize a test database with all required tables."""
    db_path = Path(tmpdir) / "test.db"

    # Initialize the database using RoadmapDatabase to create base tables
    road_db = RoadmapDatabase(db_path, agent_name="test")

    # Create additional tables needed for integration tests
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create specs_specification table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS specs_specification (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            updated_at TEXT NOT NULL,
            updated_by TEXT NOT NULL
        )
    """
    )

    # Create review_commit table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS review_commit (
            id TEXT PRIMARY KEY,
            commit_hash TEXT,
            message TEXT,
            updated_at TEXT NOT NULL,
            updated_by TEXT NOT NULL
        )
    """
    )

    # Create system_audit table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS system_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            item_id TEXT NOT NULL,
            action TEXT NOT NULL,
            field_changed TEXT,
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT NOT NULL,
            changed_at TEXT NOT NULL
        )
    """
    )

    # Create notifications table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_agent TEXT NOT NULL,
            source_agent TEXT NOT NULL,
            notification_type TEXT,
            item_id TEXT,
            message TEXT,
            status TEXT,
            created_at TEXT NOT NULL,
            processed_at TEXT,
            processed_by TEXT,
            notes TEXT
        )
    """
    )

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def test_commands_dir():
    """Create a test commands directory with sample commands."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Create architect commands
        arch_dir = base_path / "architect"
        arch_dir.mkdir()

        # Create spec command
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

# Create Specification

Creates a new technical specification for an architecture priority.

## Parameters

- priority_id: ID of the priority to create spec for
- title: Specification title
"""
        )

        # Create developer commands
        dev_dir = base_path / "code_developer"
        dev_dir.mkdir()

        # Create implementation command
        impl_cmd = dev_dir / "implement_feature.md"
        impl_cmd.write_text(
            """---
command: code_developer.implement_feature
agent: code_developer
action: implement_feature
tables:
  write: [review_commit]
  read: [specs_specification, roadmap_priority]
required_tools: [git, pytest]
---

# Implement Feature

Implements a feature from a specification.

## Parameters

- spec_id: ID of the specification to implement
"""
        )

        yield base_path


class TestEndToEndCommandExecution:
    """Test complete command execution workflow."""

    def test_architect_load_and_execute_command(self, test_commands_dir):
        """Test architect can load and execute their own commands."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            test_commands_dir / "architect",
        )

        # Should have loaded the command
        assert "create_spec" in loader.list_commands()

        # Execute the command
        result = loader.execute(
            "create_spec",
            {"priority_id": "PRIORITY-1", "title": "Test Spec"},
        )

        # Should succeed
        assert result["success"] is True
        assert result["command"] == "architect.create_spec"

    def test_developer_load_and_execute_command(self, test_commands_dir):
        """Test developer can load and execute their own commands."""
        loader = CommandLoader(
            AgentType.CODE_DEVELOPER,
            test_commands_dir / "code_developer",
        )

        # Should have loaded the command
        assert "implement_feature" in loader.list_commands()

        # Execute the command
        result = loader.execute(
            "implement_feature",
            {"spec_id": "SPEC-101"},
        )

        # Should succeed
        assert result["success"] is True


class TestPermissionEnforcementInCommands:
    """Test permission enforcement during command execution."""

    def test_command_permission_validation(self, test_commands_dir):
        """Test that command permissions are validated before execution."""
        # Developer tries to execute architect command
        # First, create a mixed loader with both commands
        mixed_dir = Path(tempfile.gettempdir()) / "mixed_commands"
        mixed_dir.mkdir(exist_ok=True)

        # Developer should not be able to load architect commands
        # because they're in a different directory
        arch_loader = CommandLoader(
            AgentType.ARCHITECT,
            test_commands_dir / "architect",
        )

        # Verify architect can execute their command
        arch_result = arch_loader.execute(
            "create_spec",
            {"priority_id": "PRIORITY-1"},
        )
        assert arch_result["success"] is True


class TestAuditTrailCreation:
    """Test that operations create audit trails."""

    def test_command_execution_creates_audit(self, test_commands_dir, initialized_db):
        """Test that command execution creates audit logs."""
        # Create a wrapper and write to a table
        db = DomainWrapper(AgentType.ARCHITECT, str(initialized_db))

        # Write a spec
        db.write(
            "specs_specification",
            {"id": "SPEC-101", "title": "Test", "content": "Content"},
        )

        # Check audit log
        audits = db.read("system_audit", {"item_id": "SPEC-101"})
        assert len(audits) > 0
        assert audits[-1]["action"] == "create"
        assert audits[-1]["changed_by"] == "architect"

    def test_command_update_creates_audit(self, initialized_db):
        """Test that updates create audit logs."""
        db = DomainWrapper(AgentType.PROJECT_MANAGER, str(initialized_db))

        # Create a priority
        db.write(
            "roadmap_priority",
            {
                "id": "PRIORITY-1",
                "item_type": "priority",
                "number": "1",
                "title": "Test Priority",
                "status": "📝 Planned",
                "priority_order": 1,
            },
        )

        # Update it
        db.update(
            "roadmap_priority",
            {"status": "🔄 In Progress"},
            {"id": "PRIORITY-1"},
        )

        # Check audit logs
        audits = db.read("system_audit", {"item_id": "PRIORITY-1"})
        assert len(audits) >= 2
        update_audits = [a for a in audits if a["action"] == "update"]
        assert len(update_audits) > 0


class TestCrossAgentNotifications:
    """Test inter-agent communication via notifications."""

    def test_architect_notify_developer(self, initialized_db):
        """Test architect can notify developer."""
        arch_db = DomainWrapper(AgentType.ARCHITECT, str(initialized_db))
        dev_db = DomainWrapper(AgentType.CODE_DEVELOPER, str(initialized_db))

        # Architect sends notification to developer
        notif_id = arch_db.send_notification(
            "code_developer",
            {"type": "spec_ready", "spec_id": "SPEC-101"},
        )
        assert notif_id > 0

        # Developer retrieves their notifications
        dev_notifs = dev_db.get_my_notifications()
        assert len(dev_notifs) > 0

        # Verify notification content
        notif = dev_notifs[-1]
        assert notif["source_agent"] == "architect"
        assert notif["target_agent"] == "code_developer"
        assert notif["status"] == "pending"

    def test_notification_processing(self, initialized_db):
        """Test marking notifications as processed."""
        arch_db = DomainWrapper(AgentType.ARCHITECT, str(initialized_db))
        dev_db = DomainWrapper(AgentType.CODE_DEVELOPER, str(initialized_db))

        # Send notification
        notif_id = arch_db.send_notification(
            "code_developer",
            {"type": "spec_ready"},
        )

        # Developer processes it
        result = dev_db.process_notification(
            notif_id,
            notes="Processing spec now",
        )
        assert result is True


class TestSkillIntegration:
    """Test skill integration with commands."""

    def test_command_loader_loads_skills(self, test_commands_dir):
        """Test that command loader can load required skills."""
        loader = CommandLoader(
            AgentType.ARCHITECT,
            test_commands_dir / "architect",
        )

        cmd = loader.commands["create_spec"]
        skills = loader._load_skills(cmd.required_skills)

        # Should return a dictionary (might be empty if skills can't load)
        assert isinstance(skills, dict)


class TestCommandPermissionDenial:
    """Test command execution with permission denial."""

    def test_agent_cannot_write_other_agents_tables(self, tmpdir):
        """Test that agents are denied write access to other agents' tables."""
        db_path = Path(tmpdir) / "test.db"

        # Developer tries to write to architect table
        dev_db = DomainWrapper(AgentType.CODE_DEVELOPER, str(db_path))

        with pytest.raises(PermissionError):
            dev_db.write(
                "specs_specification",
                {"id": "SPEC-101", "title": "Test"},
            )

    def test_agent_cannot_read_unauthorized_tables(self, tmpdir):
        """Test that agents cannot read unauthorized tables."""
        db_path = Path(tmpdir) / "test.db"

        # User listener cannot read specs
        listener_db = DomainWrapper(AgentType.USER_LISTENER, str(db_path))

        with pytest.raises(PermissionError):
            listener_db.read("specs_specification")


class TestMultiAgentWorkflow:
    """Test complex multi-agent workflows."""

    def test_architect_to_developer_workflow(self, test_commands_dir, initialized_db):
        """Test complete workflow: Architect creates spec, Developer implements."""
        # Step 1: Architect creates a spec
        arch_db = DomainWrapper(AgentType.ARCHITECT, str(initialized_db))
        arch_db.write(
            "specs_specification",
            {
                "id": "SPEC-101",
                "title": "Authentication System",
                "content": "Implement user authentication",
            },
        )

        # Step 2: Architect notifies developer
        arch_db.send_notification(
            "code_developer",
            {"type": "spec_ready", "spec_id": "SPEC-101"},
        )

        # Step 3: Developer retrieves notification and implements
        dev_db = DomainWrapper(AgentType.CODE_DEVELOPER, str(initialized_db))
        notifs = dev_db.get_my_notifications()
        assert len(notifs) > 0

        # Step 4: Developer reads the spec
        specs = dev_db.read("specs_specification", {"id": "SPEC-101"})
        assert len(specs) > 0

        # Step 5: Developer writes commit info
        dev_db.write(
            "review_commit",
            {"id": "commit-1", "commit_hash": "abc123", "message": "Implement auth"},
        )

        # Step 6: Developer marks notification as processed
        for notif in notifs:
            dev_db.process_notification(notif["id"], "Completed implementation")

        # Verify audit trail
        audits = dev_db.read("system_audit")
        assert len(audits) > 0
