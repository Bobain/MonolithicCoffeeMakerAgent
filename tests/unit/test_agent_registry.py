"""Unit tests for AgentRegistry singleton."""

import os
import threading
import time

import pytest

from coffee_maker.autonomous.agent_registry import (
    AgentAlreadyRunningError,
    AgentRegistry,
    AgentType,
    get_agent_registry,
)


class TestAgentRegistry:
    """Test suite for AgentRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        registry = AgentRegistry()
        registry.reset()

    def teardown_method(self):
        """Clean up registry after each test."""
        registry = AgentRegistry()
        registry.reset()

    def test_singleton_instance(self):
        """Test that AgentRegistry is a singleton."""
        registry1 = AgentRegistry()
        registry2 = AgentRegistry()
        assert registry1 is registry2

    def test_get_agent_registry(self):
        """Test convenience function returns singleton."""
        registry1 = get_agent_registry()
        registry2 = get_agent_registry()
        assert registry1 is registry2

    def test_register_agent(self):
        """Test successful agent registration."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER)

        assert registry.is_registered(AgentType.CODE_DEVELOPER)
        assert not registry.is_registered(AgentType.PROJECT_MANAGER)

    def test_register_agent_with_custom_pid(self):
        """Test registration with custom PID."""
        registry = AgentRegistry()
        custom_pid = 12345

        registry.register_agent(AgentType.CODE_DEVELOPER, pid=custom_pid)

        info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
        assert info is not None
        assert info["pid"] == custom_pid

    def test_register_agent_with_default_pid(self):
        """Test registration uses current process PID by default."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER)

        info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
        assert info is not None
        assert info["pid"] == os.getpid()

    def test_duplicate_registration_raises_error(self):
        """Test that registering same agent twice raises error."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.CODE_DEVELOPER)

        assert "already running" in str(exc_info.value)
        assert "code_developer" in str(exc_info.value).lower()

    def test_register_different_agents(self):
        """Test registering different agent types."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.PROJECT_MANAGER)
        registry.register_agent(AgentType.ARCHITECT)

        assert registry.is_registered(AgentType.CODE_DEVELOPER)
        assert registry.is_registered(AgentType.PROJECT_MANAGER)
        assert registry.is_registered(AgentType.ARCHITECT)

    def test_unregister_agent(self):
        """Test agent unregistration."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER)

        assert registry.is_registered(AgentType.CODE_DEVELOPER)

        registry.unregister_agent(AgentType.CODE_DEVELOPER)

        assert not registry.is_registered(AgentType.CODE_DEVELOPER)

    def test_unregister_non_registered_agent(self):
        """Test unregistering non-registered agent (should not error)."""
        registry = AgentRegistry()

        # Should not raise error
        registry.unregister_agent(AgentType.CODE_DEVELOPER)

    def test_re_register_after_unregister(self):
        """Test can re-register agent after unregistering."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.unregister_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.CODE_DEVELOPER)  # Should succeed

        assert registry.is_registered(AgentType.CODE_DEVELOPER)

    def test_get_agent_info(self):
        """Test getting agent information."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER)

        info = registry.get_agent_info(AgentType.CODE_DEVELOPER)

        assert info is not None
        assert "pid" in info
        assert "started_at" in info
        assert isinstance(info["pid"], int)
        assert isinstance(info["started_at"], str)

    def test_get_agent_info_not_registered(self):
        """Test getting info for non-registered agent returns None."""
        registry = AgentRegistry()

        info = registry.get_agent_info(AgentType.CODE_DEVELOPER)

        assert info is None

    def test_get_all_registered_agents(self):
        """Test getting all registered agents."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.PROJECT_MANAGER)

        all_agents = registry.get_all_registered_agents()

        assert len(all_agents) == 2
        assert AgentType.CODE_DEVELOPER in all_agents
        assert AgentType.PROJECT_MANAGER in all_agents
        assert AgentType.ARCHITECT not in all_agents

    def test_get_all_registered_agents_returns_copy(self):
        """Test that get_all_registered_agents returns a copy."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER)

        all_agents = registry.get_all_registered_agents()
        all_agents[AgentType.ARCHITECT] = {"pid": 999, "started_at": "test"}

        # Original should not be modified
        assert not registry.is_registered(AgentType.ARCHITECT)

    def test_reset(self):
        """Test registry reset clears all agents."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.PROJECT_MANAGER)

        assert len(registry.get_all_registered_agents()) == 2

        registry.reset()

        assert len(registry.get_all_registered_agents()) == 0

    def test_context_manager_registration(self):
        """Test context manager auto-registers and unregisters."""
        registry = AgentRegistry()

        assert not registry.is_registered(AgentType.CODE_DEVELOPER)

        with AgentRegistry.register(AgentType.CODE_DEVELOPER):
            assert registry.is_registered(AgentType.CODE_DEVELOPER)

        # Should be unregistered after context exit
        assert not registry.is_registered(AgentType.CODE_DEVELOPER)

    def test_context_manager_unregisters_on_exception(self):
        """Test context manager unregisters even if exception occurs."""
        registry = AgentRegistry()

        try:
            with AgentRegistry.register(AgentType.CODE_DEVELOPER):
                assert registry.is_registered(AgentType.CODE_DEVELOPER)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Should still be unregistered
        assert not registry.is_registered(AgentType.CODE_DEVELOPER)

    def test_context_manager_raises_on_duplicate(self):
        """Test context manager raises error for duplicate registration."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER)

        with pytest.raises(AgentAlreadyRunningError):
            with AgentRegistry.register(AgentType.CODE_DEVELOPER):
                pass

    def test_invalid_agent_type_raises_error(self):
        """Test that invalid agent type raises ValueError."""
        registry = AgentRegistry()

        with pytest.raises(ValueError) as exc_info:
            registry.register_agent("invalid_type")  # noqa

        assert "Invalid agent_type" in str(exc_info.value)

    def test_thread_safety_concurrent_registration(self):
        """Test thread-safe concurrent registration attempts."""
        registry = AgentRegistry()
        results = []
        errors = []

        def try_register():
            try:
                registry.register_agent(AgentType.CODE_DEVELOPER)
                results.append("success")
            except AgentAlreadyRunningError:
                errors.append("duplicate")

        # Try to register from 10 threads simultaneously
        threads = [threading.Thread(target=try_register) for _ in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Exactly one should succeed, rest should fail
        assert results.count("success") == 1
        assert len(errors) == 9

        # Clean up
        registry.unregister_agent(AgentType.CODE_DEVELOPER)

    def test_thread_safety_concurrent_different_agents(self):
        """Test thread-safe registration of different agent types."""
        registry = AgentRegistry()
        agent_types = [
            AgentType.CODE_DEVELOPER,
            AgentType.PROJECT_MANAGER,
            AgentType.ARCHITECT,
            AgentType.ASSISTANT,
        ]

        def register_agent(agent_type):
            registry.register_agent(agent_type)
            time.sleep(0.01)  # Small delay to test concurrency

        threads = [threading.Thread(target=register_agent, args=(at,)) for at in agent_types]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All should be registered
        for agent_type in agent_types:
            assert registry.is_registered(agent_type)

    def test_agent_type_enum_values(self):
        """Test that all expected agent types are defined."""
        expected_types = [
            "code_developer",
            "project_manager",
            "assistant",
            "code-searcher",
            "ux-design-expert",
            "architect",
            "user_listener",
            "generator",
            "reflector",
            "curator",
        ]

        for expected in expected_types:
            # Check that enum value exists
            matching = [at for at in AgentType if at.value == expected]
            assert len(matching) == 1, f"Missing or duplicate agent type: {expected}"

    def test_error_message_includes_pid_and_timestamp(self):
        """Test that error message includes helpful debugging info."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.CODE_DEVELOPER, pid=12345)

        try:
            registry.register_agent(AgentType.CODE_DEVELOPER)
            pytest.fail("Should have raised AgentAlreadyRunningError")
        except AgentAlreadyRunningError as e:
            error_msg = str(e)
            assert "12345" in error_msg  # PID
            assert "Started at:" in error_msg  # Timestamp
            assert "CODE_DEVELOPER" in error_msg or "code_developer" in error_msg

    def test_reset_idempotent(self):
        """Test that reset can be called multiple times safely."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.reset()
        registry.reset()  # Should not error
        registry.reset()  # Should not error

        assert len(registry.get_all_registered_agents()) == 0


class TestAgentAlreadyRunningError:
    """Test suite for AgentAlreadyRunningError exception."""

    def test_error_attributes(self):
        """Test that error has correct attributes."""
        error = AgentAlreadyRunningError(
            agent_type=AgentType.CODE_DEVELOPER, existing_pid=12345, existing_started_at="2025-01-01T10:00:00"
        )

        assert error.agent_type == AgentType.CODE_DEVELOPER
        assert error.existing_pid == 12345
        assert error.existing_started_at == "2025-01-01T10:00:00"

    def test_error_message_format(self):
        """Test error message format."""
        error = AgentAlreadyRunningError(
            agent_type=AgentType.CODE_DEVELOPER, existing_pid=12345, existing_started_at="2025-01-01T10:00:00"
        )

        message = str(error)
        assert "already running" in message.lower()
        assert "12345" in message
        assert "2025-01-01T10:00:00" in message
