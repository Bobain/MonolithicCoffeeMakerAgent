"""Tests for ACE agent migrations.

This module validates that all agents have been properly migrated to use
the ACEAgent base class for automatic ACE integration.

Migration Status:
    ✅ user_interpret - Migrated to ACEAgent base class
    ⏸️  DevDaemon (code_developer) - Has custom ACE integration (not using base class)
    ⏸️  assistant - Not yet implemented (assistant_ace.py is just a helper)
    ⏸️  project_manager - CLI tool, not a Python agent class
    ⏸️  code-searcher - Not yet implemented

Test Coverage:
    - user_interpret inherits from ACEAgent
    - user_interpret has required properties
    - user_interpret works with ACE enabled
    - user_interpret works with ACE disabled
    - user_interpret maintains backward compatibility
"""

import os
import pytest
from unittest.mock import patch

from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent
from coffee_maker.cli.user_interpret import UserInterpret


class TestUserInterpretMigration:
    """Tests for user_interpret migration to ACEAgent."""

    def test_inherits_from_ace_agent(self):
        """Verify user_interpret inherits from ACEAgent."""
        assert issubclass(UserInterpret, ACEAgent)

    def test_has_required_properties(self):
        """Verify user_interpret implements required ACE properties."""
        agent = UserInterpret()

        # Test agent_name property
        assert hasattr(agent, "agent_name")
        assert agent.agent_name == "user_interpret"

        # Test agent_objective property
        assert hasattr(agent, "agent_objective")
        assert isinstance(agent.agent_objective, str)
        assert len(agent.agent_objective) > 0

        # Test success_criteria property
        assert hasattr(agent, "success_criteria")
        assert isinstance(agent.success_criteria, str)
        assert len(agent.success_criteria) > 0

    def test_has_execute_task_method(self):
        """Verify user_interpret has execute_task method."""
        agent = UserInterpret()
        assert hasattr(agent, "execute_task")
        assert callable(agent.execute_task)

    def test_has_send_message_method(self):
        """Verify user_interpret has send_message method for ACE generator."""
        agent = UserInterpret()
        assert hasattr(agent, "send_message")
        assert callable(agent.send_message)

    def test_has_execute_implementation_method(self):
        """Verify user_interpret has _execute_implementation method."""
        agent = UserInterpret()
        assert hasattr(agent, "_execute_implementation")
        assert callable(agent._execute_implementation)

    @patch.dict(os.environ, {"ACE_ENABLED_USER_INTERPRET": "false"})
    def test_ace_disabled(self):
        """Test user_interpret works with ACE disabled."""
        agent = UserInterpret()

        # ACE should be disabled
        assert agent.ace_enabled is False
        assert agent.generator is None

        # Agent should still work
        result = agent.interpret("add a login feature")

        # Verify result structure
        assert isinstance(result, dict)
        assert "intent" in result
        assert "delegated_to" in result
        assert "message_to_user" in result
        assert "confidence" in result

    @patch.dict(os.environ, {"ACE_ENABLED_USER_INTERPRET": "true"})
    def test_ace_enabled(self):
        """Test user_interpret initializes with ACE enabled."""
        agent = UserInterpret()

        # ACE should be enabled
        assert agent.ace_enabled is True
        assert agent.generator is not None

        # Generator should have correct agent name
        assert agent.generator.agent_name == "user_interpret"

    def test_backward_compatibility(self):
        """Test that interpret() method still works (backward compatibility)."""
        agent = UserInterpret()

        # Old interface: interpret() method
        result = agent.interpret("show me the roadmap")

        # Should work and return expected structure
        assert isinstance(result, dict)
        assert "intent" in result
        assert result["intent"] == "view_roadmap"

    def test_intent_interpretation(self):
        """Test that intent interpretation still works correctly."""
        agent = UserInterpret()

        test_cases = [
            ("implement a login feature", "add_feature"),
            ("the code is broken", "report_bug"),
            ("show me the roadmap", "view_roadmap"),
            ("how do I use this?", "request_tutorial"),  # Fixed: "how do I" triggers tutorial
            ("what's the project status?", "check_status"),
            ("how does this work?", "ask_how_to"),  # Added: "how does" triggers ask_how_to
        ]

        for message, expected_intent in test_cases:
            result = agent.interpret(message)
            assert result["intent"] == expected_intent, f"Failed for: {message}"

    def test_agent_delegation(self):
        """Test that agent delegation works correctly."""
        agent = UserInterpret()

        test_cases = [
            ("add_feature", "code_developer"),
            ("report_bug", "code_developer"),
            ("view_roadmap", "project_manager"),
            ("ask_how_to", "assistant"),
        ]

        for intent_msg, expected_agent in test_cases:
            # Create messages that trigger specific intents
            messages = {
                "add_feature": "implement a new feature",
                "report_bug": "there's a bug in the code",
                "view_roadmap": "show me the roadmap",
                "ask_how_to": "how do I use this?",
            }

            result = agent.interpret(messages[intent_msg])
            assert result["delegated_to"] == expected_agent, f"Wrong delegation for {intent_msg}"


class TestMigrationCompleteness:
    """Tests to verify migration is complete."""

    def test_no_manual_wrapper_files_exist(self):
        """Verify manual wrapper files have been deleted."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        cli_dir = project_root / "coffee_maker" / "cli"

        # user_interpret_ace.py should NOT exist (was deleted)
        user_interpret_ace = cli_dir / "user_interpret_ace.py"
        assert not user_interpret_ace.exists(), "user_interpret_ace.py should be deleted"

        # user_interpret_v2.py should NOT exist (was merged)
        user_interpret_v2 = cli_dir / "user_interpret_v2.py"
        assert not user_interpret_v2.exists(), "user_interpret_v2.py should be deleted"

        # assistant_ace.py SHOULD exist (different pattern - helper class)
        assistant_ace = cli_dir / "assistant_ace.py"
        assert assistant_ace.exists(), "assistant_ace.py should exist (helper pattern)"

        # user_listener_ace.py SHOULD exist (different pattern - helper class)
        user_listener_ace = cli_dir / "user_listener_ace.py"
        assert user_listener_ace.exists(), "user_listener_ace.py should exist (helper pattern)"

    def test_user_interpret_is_primary_import(self):
        """Verify user_interpret can be imported from primary location."""
        # Should import without error
        from coffee_maker.cli.user_interpret import UserInterpret

        # Should be the migrated version (ACEAgent subclass)
        assert issubclass(UserInterpret, ACEAgent)


class TestACEIntegrationValidation:
    """Tests to validate ACE integration works correctly."""

    @patch.dict(os.environ, {"ACE_ENABLED_USER_INTERPRET": "true"})
    def test_ace_generator_initialization(self):
        """Test ACE generator initializes with correct parameters."""
        agent = UserInterpret()

        assert agent.ace_enabled is True
        assert agent.generator is not None

        # Verify generator has correct configuration
        assert agent.generator.agent_name == "user_interpret"
        assert (
            agent.generator.agent_objective
            == "Interpret user intent, analyze sentiment, and delegate to appropriate agents"
        )
        assert "Correct intent interpretation" in agent.generator.success_criteria

    @patch.dict(os.environ, {"ACE_ENABLED_USER_INTERPRET": "false"})
    def test_ace_disabled_direct_execution(self):
        """Test that ACE disabled mode calls _execute_implementation directly."""
        agent = UserInterpret()

        # Execute task
        result = agent.execute_task("test message")

        # Should return interpretation result
        assert isinstance(result, dict)
        assert "intent" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
