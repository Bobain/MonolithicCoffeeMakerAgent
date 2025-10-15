"""Tests for singleton agent pattern.

This module tests that agents using the ACEAgent base class and AgentRegistry
follow the singleton pattern correctly, ensuring only one instance exists
and remains running throughout the application lifecycle.
"""

import os
from unittest.mock import patch

import pytest

from coffee_maker.autonomous.ace.agent_registry import AgentRegistry
from coffee_maker.cli.user_interpret import UserInterpret


class TestAgentRegistry:
    """Test AgentRegistry functionality."""

    def setup_method(self):
        """Clear registry before each test."""
        AgentRegistry.clear_registry()

    def test_get_agent_creates_singleton(self):
        """Test that get_agent creates a singleton instance."""
        agent1 = AgentRegistry.get_agent(UserInterpret)
        agent2 = AgentRegistry.get_agent(UserInterpret)

        # Should be the exact same instance
        assert agent1 is agent2
        assert id(agent1) == id(agent2)

    def test_has_agent_before_and_after_creation(self):
        """Test has_agent correctly reports existence."""
        # Before creation
        assert not AgentRegistry.has_agent(UserInterpret)

        # After creation
        AgentRegistry.get_agent(UserInterpret)
        assert AgentRegistry.has_agent(UserInterpret)

    def test_clear_registry_removes_all_agents(self):
        """Test that clear_registry removes all instances."""
        agent1 = AgentRegistry.get_agent(UserInterpret)
        assert AgentRegistry.has_agent(UserInterpret)

        AgentRegistry.clear_registry()
        assert not AgentRegistry.has_agent(UserInterpret)

        # Next call should create new instance
        agent2 = AgentRegistry.get_agent(UserInterpret)
        assert agent1 is not agent2  # Different instance

    def test_get_all_agents(self):
        """Test get_all_agents returns all registered instances."""
        agent1 = AgentRegistry.get_agent(UserInterpret)

        all_agents = AgentRegistry.get_all_agents()
        assert "UserInterpret" in all_agents
        assert all_agents["UserInterpret"] is agent1


class TestACEAgentSingleton:
    """Test singleton pattern in ACEAgent base class."""

    def setup_method(self):
        """Clear any existing instances before each test."""
        # Clear the singleton instance
        if hasattr(UserInterpret, "_instance"):
            delattr(UserInterpret, "_instance")

    def test_aceagent_creates_singleton(self):
        """Test that ACEAgent subclasses are singletons."""
        agent1 = UserInterpret()
        agent2 = UserInterpret()

        # Should be the exact same instance
        assert agent1 is agent2
        assert id(agent1) == id(agent2)

    def test_singleton_initialization_only_once(self):
        """Test that __init__ only runs once even with multiple instantiations."""
        agent1 = UserInterpret()
        agent1.conversation_history.copy()

        # Add something to history
        agent1.conversation_history.append("test message")

        # Create "new" instance (should be same instance)
        agent2 = UserInterpret()

        # Should have the modified history from agent1
        assert agent2.conversation_history == agent1.conversation_history
        assert "test message" in agent2.conversation_history

    def test_singleton_state_preserved(self):
        """Test that singleton state is preserved across references."""
        agent1 = UserInterpret()
        agent1.conversation_history = ["message 1", "message 2"]

        # Get "new" instance
        agent2 = UserInterpret()

        # Should have same conversation history
        assert agent2.conversation_history == ["message 1", "message 2"]

        # Modify via agent2
        agent2.conversation_history.append("message 3")

        # Should reflect in agent1
        assert agent1.conversation_history == ["message 1", "message 2", "message 3"]


class TestSingletonWithACE:
    """Test singleton pattern works correctly with ACE enabled/disabled."""

    def setup_method(self):
        """Clear instances before each test."""
        if hasattr(UserInterpret, "_instance"):
            delattr(UserInterpret, "_instance")

    def test_singleton_with_ace_enabled(self):
        """Test singleton works when ACE is enabled."""
        with patch.dict(os.environ, {"ACE_ENABLED_USER_INTERPRET": "true"}):
            agent1 = UserInterpret()
            agent2 = UserInterpret()

            assert agent1 is agent2
            assert agent1.ace_enabled
            assert agent2.ace_enabled

    def test_singleton_with_ace_disabled(self):
        """Test singleton works when ACE is disabled."""
        with patch.dict(os.environ, {"ACE_ENABLED_USER_INTERPRET": "false"}):
            agent1 = UserInterpret()
            agent2 = UserInterpret()

            assert agent1 is agent2
            assert not agent1.ace_enabled
            assert not agent2.ace_enabled


class TestSingletonTraceCorrelation:
    """Test that singleton pattern improves trace correlation."""

    def setup_method(self):
        """Clear instances before each test."""
        if hasattr(UserInterpret, "_instance"):
            delattr(UserInterpret, "_instance")

    def test_multiple_calls_use_same_generator(self):
        """Test that multiple executions use the same generator instance."""
        with patch.dict(os.environ, {"ACE_ENABLED_USER_INTERPRET": "true"}):
            agent1 = UserInterpret()
            generator1 = agent1.generator

            # Get agent again
            agent2 = UserInterpret()
            generator2 = agent2.generator

            # Should be the same generator instance
            assert generator1 is generator2

    def test_conversation_history_persists(self):
        """Test that conversation history persists across instantiations."""
        agent1 = UserInterpret()

        # Execute a task (this adds to conversation history)
        agent1.interpret("Hello")

        # Get agent again
        agent2 = UserInterpret()

        # Should have conversation history from agent1
        # Note: ACE may execute twice, so we check that "Hello" is in history
        assert "Hello" in agent2.conversation_history
        assert len(agent2.conversation_history) > 0


class TestConcurrentSingletonAccess:
    """Test singleton pattern with concurrent access patterns."""

    def setup_method(self):
        """Clear instances before each test."""
        if hasattr(UserInterpret, "_instance"):
            delattr(UserInterpret, "_instance")
        AgentRegistry.clear_registry()

    def test_registry_and_direct_instantiation_same_instance(self):
        """Test that AgentRegistry and direct instantiation return same instance."""
        # Create via direct instantiation
        agent1 = UserInterpret()

        # Get via registry
        agent2 = AgentRegistry.get_agent(UserInterpret)

        # Should be the same instance (both use singleton pattern)
        assert agent1 is agent2

    def test_multiple_registry_calls_same_instance(self):
        """Test that multiple registry calls return same instance."""
        agent1 = AgentRegistry.get_agent(UserInterpret)
        agent2 = AgentRegistry.get_agent(UserInterpret)
        agent3 = UserInterpret()

        # All should be the same instance
        assert agent1 is agent2
        assert agent2 is agent3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
