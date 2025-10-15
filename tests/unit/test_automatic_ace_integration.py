"""Tests for automatic ACE integration via ACEAgent base class.

This test suite validates that:
1. ACEAgent base class provides automatic ACE integration
2. New agents automatically get ACE supervision
3. No manual wrapper creation needed
4. Consistent behavior across all agents
"""

import pytest
from unittest.mock import Mock, patch
from coffee_maker.cli.user_interpret import UserInterpret


class TestAutomaticACEIntegration:
    """Test automatic ACE integration for all agents."""

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config")
    def test_agent_automatically_enables_ace_from_env(self, mock_config, mock_generator_class, mock_getenv):
        """Verify agent automatically checks ACE_ENABLED_{AGENT_NAME} env var."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_USER_INTERPRET":
                return "true"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_config.return_value = {}
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Create agent (should automatically enable ACE)
        agent = UserInterpret()

        # Verify ACE enabled
        assert agent.ace_enabled is True
        assert agent.generator is not None

        # Verify generator initialized with correct params
        call_args = mock_generator_class.call_args
        assert call_args[1]["agent_name"] == "user_interpret"
        assert "Interpret user intent" in call_args[1]["agent_objective"]
        assert "Correct intent interpretation" in call_args[1]["success_criteria"]

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_agent_enabled_by_default_when_no_env_var(self, mock_getenv):
        """Verify ACE is ENABLED BY DEFAULT when no env var set."""

        def getenv_side_effect(key, default=""):
            # Return default (which is "true" for ACE_ENABLED_*)
            return default

        mock_getenv.side_effect = getenv_side_effect

        # Note: We need to mock the ACEGenerator to avoid real initialization
        with patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator") as mock_gen:
            with patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config") as mock_config:
                mock_config.return_value = {}
                mock_gen.return_value = Mock()

                # Create agent (should automatically ENABLE ACE by default)
                agent = UserInterpret()

                # Verify ACE enabled by default
                assert agent.ace_enabled is True
                assert agent.generator is not None

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_agent_can_opt_out_with_false(self, mock_getenv):
        """Verify user can opt-out of ACE by setting env var to false."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_USER_INTERPRET":
                return "false"  # User explicitly opts out
            return default

        mock_getenv.side_effect = getenv_side_effect

        # Create agent (should disable ACE due to opt-out)
        agent = UserInterpret()

        # Verify ACE disabled (user opt-out)
        assert agent.ace_enabled is False
        assert agent.generator is None

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config")
    def test_execute_task_routes_through_generator_when_enabled(self, mock_config, mock_generator_class, mock_getenv):
        """Verify execute_task automatically routes through generator."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_USER_INTERPRET":
                return "true"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_config.return_value = {}
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Create agent
        agent = UserInterpret()

        # Mock generator to call send_message
        def mock_execute_with_trace(prompt, priority_context, **kwargs):
            result = agent.send_message(prompt, **kwargs)
            return {
                "agent_result": result,
                "result": "success",
                "trace_id": "test_trace",
                "duration": 1.0,
                "errors": [],
            }

        mock_generator.execute_with_trace.side_effect = mock_execute_with_trace

        # Execute task
        result = agent.execute_task("test message")

        # Verify generator was called
        mock_generator.execute_with_trace.assert_called_once()

        # Verify result has expected structure
        assert "intent" in result
        assert "delegated_to" in result

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_execute_task_direct_when_disabled(self, mock_getenv):
        """Verify execute_task calls implementation directly when ACE disabled."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_USER_INTERPRET":
                return "false"
            return default

        mock_getenv.side_effect = getenv_side_effect

        # Create agent
        agent = UserInterpret()

        # Execute task
        result = agent.execute_task("how do I run tests?")

        # Verify result returned (no exception)
        assert "intent" in result
        assert "delegated_to" in result

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config")
    def test_single_execution_through_automatic_integration(self, mock_config, mock_generator_class, mock_getenv):
        """Verify automatic integration ensures single execution."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_USER_INTERPRET":
                return "true"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_config.return_value = {}
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Create agent
        agent = UserInterpret()

        # Track calls to _execute_implementation
        original_impl = agent._execute_implementation
        call_count = {"count": 0}

        def counting_impl(*args, **kwargs):
            call_count["count"] += 1
            return original_impl(*args, **kwargs)

        agent._execute_implementation = counting_impl

        # Mock generator to call send_message
        def mock_execute_with_trace(prompt, priority_context, **kwargs):
            result = agent.send_message(prompt, **kwargs)
            return {
                "agent_result": result,
                "result": "success",
                "trace_id": "test_trace",
                "duration": 1.0,
                "errors": [],
            }

        mock_generator.execute_with_trace.side_effect = mock_execute_with_trace

        # Execute
        agent.execute_task("test message")

        # Verify single execution
        assert call_count["count"] == 1, "Should execute exactly once"

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config")
    def test_backward_compatibility_interpret_method(self, mock_config, mock_generator_class, mock_getenv):
        """Verify interpret() method still works (backward compatibility)."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_USER_INTERPRET":
                return "true"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_config.return_value = {}
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Create agent
        agent = UserInterpret()

        # Mock generator to call send_message
        def mock_execute_with_trace(prompt, priority_context, **kwargs):
            result = agent.send_message(prompt, **kwargs)
            return {
                "agent_result": result,
                "result": "success",
                "trace_id": "test_trace",
                "duration": 1.0,
                "errors": [],
            }

        mock_generator.execute_with_trace.side_effect = mock_execute_with_trace

        # Call interpret() (old method)
        result = agent.interpret("test message")

        # Verify it works
        assert "intent" in result
        assert "delegated_to" in result

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_no_manual_wrapper_needed(self, mock_getenv):
        """Verify no manual *_ace.py wrapper file needed.

        This is the KEY benefit: just inherit from ACEAgent and you're done!
        """

        def getenv_side_effect(key, default=""):
            # Test both enabled and disabled
            return "false"  # Doesn't matter for this test

        mock_getenv.side_effect = getenv_side_effect

        # Just create the agent - no wrapper!
        agent = UserInterpret()

        # Verify agent has all necessary methods
        assert hasattr(agent, "execute_task"), "Should have execute_task method"
        assert hasattr(agent, "send_message"), "Should have send_message method"
        assert hasattr(agent, "agent_name"), "Should have agent_name property"
        assert hasattr(agent, "agent_objective"), "Should have agent_objective property"
        assert hasattr(agent, "success_criteria"), "Should have success_criteria property"
        assert hasattr(agent, "ace_enabled"), "Should have ace_enabled flag"

        # Execute task should work
        result = agent.execute_task("test")
        assert result is not None


class TestAutomaticACEForNewAgents:
    """Demonstrate how easy it is to add ACE to new agents."""

    def test_new_agent_pattern_example(self):
        """Show the pattern for any new agent."""
        from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

        # This is ALL you need for a new agent with automatic ACE!
        class MyNewAgent(ACEAgent):
            @property
            def agent_name(self) -> str:
                return "my_new_agent"

            @property
            def agent_objective(self) -> str:
                return "Do something useful"

            @property
            def success_criteria(self) -> str:
                return "Task completed successfully"

            def _execute_implementation(self, task: str, **kwargs):
                return {"result": f"Completed: {task}"}

        # That's it! ACE is automatic
        with patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv") as mock_env:
            mock_env.return_value = "false"
            agent = MyNewAgent()

            result = agent.execute_task("test task")
            assert result["result"] == "Completed: test task"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
