"""Integration tests for US-035 - Singleton Agent Enforcement across all agents.

This test suite verifies that:
1. All agent entry points use AgentRegistry with context manager
2. Duplicate agent instances are prevented
3. Error handling works correctly with helpful messages
4. Thread safety is maintained across all agent types
"""

import threading

import pytest

from coffee_maker.autonomous.agent_registry import (
    AgentAlreadyRunningError,
    AgentRegistry,
    AgentType,
)


class TestSingletonEnforcementAcrossAgents:
    """Test singleton enforcement for all agent types."""

    def setup_method(self):
        """Reset registry before each test."""
        registry = AgentRegistry()
        registry.reset()

    def teardown_method(self):
        """Clean up registry after each test."""
        registry = AgentRegistry()
        registry.reset()

    def test_all_agent_types_defined(self):
        """Test that all required agent types are defined."""
        required_agents = [
            AgentType.CODE_DEVELOPER,
            AgentType.PROJECT_MANAGER,
            AgentType.ARCHITECT,
            AgentType.ASSISTANT,
            AgentType.ASSISTANT,
            AgentType.UX_DESIGN_EXPERT,
            AgentType.USER_LISTENER,
        ]

        for agent_type in required_agents:
            assert agent_type in AgentType
            assert agent_type.value is not None

    def test_code_developer_singleton_enforcement(self):
        """Test code_developer cannot run in parallel."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.CODE_DEVELOPER)

        assert "code_developer" in str(exc_info.value).lower()

    def test_project_manager_singleton_enforcement(self):
        """Test project_manager cannot run in parallel."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.PROJECT_MANAGER)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.PROJECT_MANAGER)

        assert "project_manager" in str(exc_info.value).lower()

    def test_architect_singleton_enforcement(self):
        """Test architect cannot run in parallel."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.ARCHITECT)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.ARCHITECT)

        assert "architect" in str(exc_info.value).lower()

    def test_assistant_singleton_enforcement(self):
        """Test assistant cannot run in parallel."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.ASSISTANT)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.ASSISTANT)

        assert "assistant" in str(exc_info.value).lower()

    def test_code_searcher_singleton_enforcement(self):
        """Test assistant (with code analysis skills) cannot run in parallel."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.ASSISTANT)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.ASSISTANT)

        assert "assistant" in str(exc_info.value).lower()

    def test_ux_design_expert_singleton_enforcement(self):
        """Test ux-design-expert cannot run in parallel."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.UX_DESIGN_EXPERT)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.UX_DESIGN_EXPERT)

        assert "ux-design-expert" in str(exc_info.value).lower()

    def test_user_listener_singleton_enforcement(self):
        """Test user_listener cannot run in parallel."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.USER_LISTENER)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.USER_LISTENER)

        assert "user_listener" in str(exc_info.value).lower()

    def test_different_agents_can_run_simultaneously(self):
        """Test different agent types CAN run at the same time."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.PROJECT_MANAGER)
        registry.register_agent(AgentType.ASSISTANT)

        assert registry.is_registered(AgentType.CODE_DEVELOPER)
        assert registry.is_registered(AgentType.PROJECT_MANAGER)
        assert registry.is_registered(AgentType.ASSISTANT)

    def test_context_manager_singleton_enforcement_for_code_developer(self):
        """Test context manager prevents duplicate code_developer."""
        registry = AgentRegistry()

        with AgentRegistry.register(AgentType.CODE_DEVELOPER):
            assert registry.is_registered(AgentType.CODE_DEVELOPER)

            with pytest.raises(AgentAlreadyRunningError):
                with AgentRegistry.register(AgentType.CODE_DEVELOPER):
                    pass

    def test_context_manager_singleton_enforcement_for_project_manager(self):
        """Test context manager prevents duplicate project_manager."""
        registry = AgentRegistry()

        with AgentRegistry.register(AgentType.PROJECT_MANAGER):
            assert registry.is_registered(AgentType.PROJECT_MANAGER)

            with pytest.raises(AgentAlreadyRunningError):
                with AgentRegistry.register(AgentType.PROJECT_MANAGER):
                    pass

    def test_context_manager_singleton_enforcement_for_all_agents(self):
        """Test context manager prevents duplicates for all agent types."""
        agent_types = [
            AgentType.CODE_DEVELOPER,
            AgentType.PROJECT_MANAGER,
            AgentType.ARCHITECT,
            AgentType.ASSISTANT,
            AgentType.ASSISTANT,
            AgentType.UX_DESIGN_EXPERT,
            AgentType.USER_LISTENER,
        ]

        for agent_type in agent_types:
            registry = AgentRegistry()

            with AgentRegistry.register(agent_type):
                assert registry.is_registered(agent_type)

                with pytest.raises(AgentAlreadyRunningError):
                    with AgentRegistry.register(agent_type):
                        pass

            registry.reset()

    def test_singleton_enforced_across_daemon_lifecycle(self):
        """Test singleton is maintained across typical daemon operations."""
        registry = AgentRegistry()

        # Register
        registry.register_agent(AgentType.CODE_DEVELOPER)
        assert registry.is_registered(AgentType.CODE_DEVELOPER)

        # Try to register again - should fail
        with pytest.raises(AgentAlreadyRunningError):
            registry.register_agent(AgentType.CODE_DEVELOPER)

        # Unregister
        registry.unregister_agent(AgentType.CODE_DEVELOPER)
        assert not registry.is_registered(AgentType.CODE_DEVELOPER)

        # Re-register should work
        registry.register_agent(AgentType.CODE_DEVELOPER)
        assert registry.is_registered(AgentType.CODE_DEVELOPER)

    def test_error_message_contains_helpful_debugging_info(self):
        """Test that error message contains PID and timestamp."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER, pid=99999)

        try:
            registry.register_agent(AgentType.CODE_DEVELOPER)
            pytest.fail("Should have raised AgentAlreadyRunningError")
        except AgentAlreadyRunningError as e:
            error_msg = str(e)

            # Should contain debugging info
            assert "99999" in error_msg  # PID
            assert "Started at:" in error_msg  # Timestamp indicator
            assert "already running" in error_msg.lower()

    def test_concurrent_registration_single_agent_only_one_succeeds(self):
        """Test concurrent registration attempts for same agent - only one succeeds."""
        registry = AgentRegistry()
        results = {"success": 0, "duplicate": 0, "errors": 0}
        lock = threading.Lock()

        def attempt_register():
            try:
                registry.register_agent(AgentType.CODE_DEVELOPER)
                with lock:
                    results["success"] += 1
            except AgentAlreadyRunningError:
                with lock:
                    results["duplicate"] += 1
            except Exception:
                with lock:
                    results["errors"] += 1

        threads = [threading.Thread(target=attempt_register) for _ in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Exactly one should succeed, rest should fail with duplicate error
        assert results["success"] == 1, f"Expected 1 success, got {results['success']}"
        assert results["duplicate"] == 9, f"Expected 9 duplicates, got {results['duplicate']}"
        assert results["errors"] == 0, f"Unexpected errors: {results['errors']}"

        registry.unregister_agent(AgentType.CODE_DEVELOPER)

    def test_concurrent_different_agents_all_succeed(self):
        """Test concurrent registration of different agents - all should succeed."""
        registry = AgentRegistry()
        agent_types = [
            AgentType.CODE_DEVELOPER,
            AgentType.PROJECT_MANAGER,
            AgentType.ARCHITECT,
            AgentType.ASSISTANT,
        ]
        results = {"success": 0, "errors": 0}
        lock = threading.Lock()

        def attempt_register(agent_type):
            try:
                registry.register_agent(agent_type)
                with lock:
                    results["success"] += 1
            except Exception:
                with lock:
                    results["errors"] += 1

        threads = [threading.Thread(target=attempt_register, args=(at,)) for at in agent_types]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All should succeed
        assert results["success"] == 4, f"Expected 4 successes, got {results['success']}"
        assert results["errors"] == 0, f"Unexpected errors: {results['errors']}"

        # All should be registered
        for agent_type in agent_types:
            assert registry.is_registered(agent_type)

    def test_cleanup_on_exception_with_context_manager(self):
        """Test cleanup happens even with exceptions (all agents)."""
        agent_types = [
            AgentType.CODE_DEVELOPER,
            AgentType.PROJECT_MANAGER,
            AgentType.ARCHITECT,
            AgentType.ASSISTANT,
        ]

        for agent_type in agent_types:
            registry = AgentRegistry()

            try:
                with AgentRegistry.register(agent_type):
                    assert registry.is_registered(agent_type)
                    raise ValueError("Test exception")
            except ValueError:
                pass

            # Should be cleaned up even though exception occurred
            assert not registry.is_registered(agent_type)

            registry.reset()

    def test_get_agent_info_for_registered_agent(self):
        """Test retrieving info about registered agents."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER, pid=12345)
        info = registry.get_agent_info(AgentType.CODE_DEVELOPER)

        assert info is not None
        assert info["pid"] == 12345
        assert "started_at" in info

    def test_get_all_registered_agents_shows_multiple_types(self):
        """Test getting all registered agents when multiple are running."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.PROJECT_MANAGER)
        registry.register_agent(AgentType.ASSISTANT)

        all_agents = registry.get_all_registered_agents()

        assert len(all_agents) == 3
        assert AgentType.CODE_DEVELOPER in all_agents
        assert AgentType.PROJECT_MANAGER in all_agents
        assert AgentType.ASSISTANT in all_agents

    def test_sequential_agent_execution_pattern(self):
        """Test typical sequential agent execution pattern."""
        registry = AgentRegistry()

        # Agent 1 runs
        with AgentRegistry.register(AgentType.CODE_DEVELOPER):
            assert registry.is_registered(AgentType.CODE_DEVELOPER)
            assert not registry.is_registered(AgentType.PROJECT_MANAGER)

        # After unregister, Agent 2 can run
        with AgentRegistry.register(AgentType.PROJECT_MANAGER):
            assert not registry.is_registered(AgentType.CODE_DEVELOPER)
            assert registry.is_registered(AgentType.PROJECT_MANAGER)

        # Both are now unregistered
        assert not registry.is_registered(AgentType.CODE_DEVELOPER)
        assert not registry.is_registered(AgentType.PROJECT_MANAGER)

    def test_registry_reset_clears_all_agents(self):
        """Test reset clears all registered agents."""
        registry = AgentRegistry()

        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.PROJECT_MANAGER)
        registry.register_agent(AgentType.ASSISTANT)

        assert len(registry.get_all_registered_agents()) == 3

        registry.reset()

        assert len(registry.get_all_registered_agents()) == 0
        assert not registry.is_registered(AgentType.CODE_DEVELOPER)
        assert not registry.is_registered(AgentType.PROJECT_MANAGER)
        assert not registry.is_registered(AgentType.ASSISTANT)
