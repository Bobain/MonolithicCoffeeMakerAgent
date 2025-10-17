"""Tests for user_listener CLI.

SPEC-010: User-Listener UI Command

Tests verify:
- Singleton enforcement (only one instance at a time)
- Cleanup on exit
- AgentRegistry integration
"""

import pytest

from coffee_maker.autonomous.agent_registry import (
    AgentAlreadyRunningError,
    AgentRegistry,
    AgentType,
)


def test_singleton_enforcement():
    """Test that only one user_listener can run at a time.

    From SPEC-010 Testing Strategy: Unit Tests

    Verifies:
    - First registration succeeds
    - Second registration fails with AgentAlreadyRunningError
    - Error message contains "user_listener" and "already running"
    """
    # Register first instance
    with AgentRegistry.register(AgentType.USER_LISTENER):
        # Try to register another instance - should fail
        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            AgentRegistry().register_agent(AgentType.USER_LISTENER)

        assert "user_listener" in str(exc_info.value).lower()
        assert "already running" in str(exc_info.value).lower()


def test_cleanup_on_exit():
    """Test that singleton is cleaned up on exit.

    From SPEC-010 Testing Strategy: Unit Tests

    Verifies:
    - First registration and exit succeeds
    - Second registration succeeds after cleanup
    - No lingering state after context manager exit
    """
    # Register and exit
    with AgentRegistry.register(AgentType.USER_LISTENER):
        pass  # Automatically cleaned up

    # Should be able to register again
    with AgentRegistry.register(AgentType.USER_LISTENER):
        pass  # Should succeed without error


def test_multiple_sequential_instances():
    """Test that multiple sequential instances can run.

    Verifies:
    - Can create, run, and exit multiple instances in sequence
    - Registry properly tracks each instance
    - No state pollution between instances
    """
    # First instance
    with AgentRegistry.register(AgentType.USER_LISTENER):
        # Verify we're registered
        registry = AgentRegistry()
        assert registry.is_registered(AgentType.USER_LISTENER)

    # Second instance (after cleanup)
    with AgentRegistry.register(AgentType.USER_LISTENER):
        # Verify we're registered
        registry = AgentRegistry()
        assert registry.is_registered(AgentType.USER_LISTENER)
