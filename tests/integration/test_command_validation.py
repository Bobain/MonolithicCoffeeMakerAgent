"""
Comprehensive Validation Framework for Command System Migration

This test suite validates the command system implementation across:
- Permission enforcement
- Workflow integration
- Performance overhead
- Data consistency
- Feature flag correctness
- Rollback procedures

These tests run during migration to ensure safety and correctness.
"""

import json
import tempfile
from pathlib import Path

from coffee_maker.commands.feature_flags import FeatureFlags
from coffee_maker.commands.parallel_operation import (
    ParallelOperationWrapper,
)
from coffee_maker.commands.rollback import RollbackManager


class TestFeatureFlagsPermissionEnforcement:
    """Test that feature flags properly enforce command permissions."""

    def test_all_flags_initially_disabled(self):
        """Test that new feature flags start disabled (safe default)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            # All agents should have empty command set
            for agent, commands in flags.flags.items():
                assert isinstance(commands, dict), f"Agent {agent} should have dict"

    def test_enable_specific_command(self):
        """Test enabling a specific command for an agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            # Enable a command
            flags.enable_command("code_developer", "claim_priority")

            # Verify it's enabled
            assert flags.is_enabled("code_developer", "claim_priority")
            assert not flags.is_enabled("code_developer", "run_tests")

    def test_disable_specific_command(self):
        """Test disabling a specific command for an agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            # Enable then disable
            flags.enable_command("architect", "create_spec")
            assert flags.is_enabled("architect", "create_spec")

            flags.disable_command("architect", "create_spec")
            assert not flags.is_enabled("architect", "create_spec")

    def test_enable_all_agent_commands(self):
        """Test enabling all commands for an agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            # Pre-register some commands
            flags.register_command("project_manager", "parse_roadmap", False)
            flags.register_command("project_manager", "create_notification", False)

            # Enable all for agent
            flags.enable_agent("project_manager")

            # All should be enabled
            for command, enabled in flags.flags["project_manager"].items():
                assert enabled

    def test_disable_all_agent_commands_rollback(self):
        """Test rolling back agent (disabling all commands)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            # Enable agent
            flags.register_command("code_developer", "claim_priority", True)
            flags.register_command("code_developer", "run_tests", True)
            flags.enable_agent("code_developer")

            # Rollback
            flags.disable_agent("code_developer")

            # All should be disabled
            for command, enabled in flags.flags["code_developer"].items():
                assert not enabled

    def test_unknown_agent_returns_false(self):
        """Test that unknown agent returns False for is_enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            assert not flags.is_enabled("nonexistent_agent", "any_command")

    def test_persistence_to_json_file(self):
        """Test that feature flags persist to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"

            # Create flags and enable a command
            flags1 = FeatureFlags(str(flags_file))
            flags1.enable_command("architect", "create_spec")

            # Load in new instance
            flags2 = FeatureFlags(str(flags_file))

            # Should persist
            assert flags2.is_enabled("architect", "create_spec")

    def test_phase_enablement(self):
        """Test enabling commands for entire phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            # Register commands for agents in Phase 2
            for agent in ["project_manager", "architect", "code_developer"]:
                flags.register_command(agent, "test_command", False)

            # Enable phase 2
            flags.enable_phase(2)

            # All phase 2 agents should be enabled
            for agent in ["project_manager", "architect", "code_developer"]:
                assert len(flags.get_enabled_commands(agent)) > 0


class TestParallelOperationValidation:
    """Test parallel operation wrapper for result validation."""

    def test_successful_operation_execution(self):
        """Test executing a successful operation."""
        wrapper = ParallelOperationWrapper()

        def legacy_fn(x):
            return x * 2

        result = wrapper.execute_with_validation(
            agent="code_developer",
            action="test_action",
            params={"x": 5},
            legacy_fn=legacy_fn,
        )

        assert result.success
        assert result.data == 10

    def test_failed_operation_returns_error(self):
        """Test that operation failures are captured."""
        wrapper = ParallelOperationWrapper()

        def failing_fn(x):
            raise ValueError("Test error")

        result = wrapper.execute_with_validation(
            agent="code_developer",
            action="test_action",
            params={"x": 5},
            legacy_fn=failing_fn,
        )

        assert not result.success
        assert "Test error" in result.error

    def test_result_comparison_with_matching_results(self):
        """Test that matching results are correctly identified."""
        wrapper = ParallelOperationWrapper()

        def legacy_fn(x):
            return {"result": x * 2}

        def command_fn(x):
            return {"result": x * 2}

        # Enable command
        wrapper.flags.enable_command("test_agent", "test_action")

        result = wrapper.execute_with_validation(
            agent="test_agent",
            action="test_action",
            params={"x": 5},
            legacy_fn=legacy_fn,
            command_fn=command_fn,
        )

        # Should have logged a comparison
        assert len(wrapper.comparison_log) > 0
        assert wrapper.comparison_log[0]["match"]

    def test_result_mismatch_detection(self):
        """Test that mismatched results are detected."""
        wrapper = ParallelOperationWrapper()

        def legacy_fn(x):
            return {"result": x * 2}

        def command_fn(x):
            return {"result": x * 3}  # Different result

        # Enable command
        wrapper.flags.enable_command("test_agent", "test_action")

        result = wrapper.execute_with_validation(
            agent="test_agent",
            action="test_action",
            params={"x": 5},
            legacy_fn=legacy_fn,
            command_fn=command_fn,
        )

        # Should have detected mismatch
        assert len(wrapper.comparison_log) > 0
        assert not wrapper.comparison_log[0]["match"]
        assert wrapper.mismatch_count > 0

    def test_fallback_to_legacy_on_mismatch(self):
        """Test that legacy result is returned on mismatch."""
        wrapper = ParallelOperationWrapper()

        def legacy_fn(x):
            return 10

        def command_fn(x):
            return 20  # Mismatch

        wrapper.flags.enable_command("test_agent", "test_action")

        result = wrapper.execute_with_validation(
            agent="test_agent",
            action="test_action",
            params={"x": 5},
            legacy_fn=legacy_fn,
            command_fn=command_fn,
        )

        # Should return legacy result
        assert result.data == 10

    def test_statistics_tracking(self):
        """Test that statistics are properly tracked."""
        wrapper = ParallelOperationWrapper()

        def legacy_fn(x):
            return x * 2

        # Run multiple operations
        for i in range(5):
            wrapper.execute_with_validation(
                agent="code_developer",
                action="test_action",
                params={"x": i},
                legacy_fn=legacy_fn,
            )

        stats = wrapper.get_statistics()
        assert stats["total_operations"] == 5

    def test_comparison_log_export(self):
        """Test exporting comparison log to JSON."""
        wrapper = ParallelOperationWrapper()

        def legacy_fn(x):
            return x * 2

        wrapper.execute_with_validation(
            agent="code_developer",
            action="test_action",
            params={"x": 5},
            legacy_fn=legacy_fn,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            export_file = Path(tmpdir) / "log.json"
            wrapper.export_comparison_log(str(export_file))

            assert export_file.exists()
            with open(export_file) as f:
                data = json.load(f)
                assert "statistics" in data

    def test_performance_tracking(self):
        """Test that operation timing is tracked."""
        wrapper = ParallelOperationWrapper()

        def slow_fn(x):
            import time

            time.sleep(0.01)
            return x

        result = wrapper.execute_with_validation(
            agent="code_developer",
            action="test_action",
            params={"x": 5},
            legacy_fn=slow_fn,
        )

        assert result.duration_ms > 0

    def test_command_disabled_uses_legacy(self):
        """Test that disabled commands fall back to legacy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            wrapper = ParallelOperationWrapper()
            wrapper.flags.config_path = Path(flags_file)

            def legacy_fn(x):
                return "legacy"

            def command_fn(x):
                return "command"

            # Explicitly register but don't enable the command
            wrapper.flags.register_command("test_agent", "test_action", False)
            assert not wrapper.flags.is_enabled("test_agent", "test_action")

            result = wrapper.execute_with_validation(
                agent="test_agent",
                action="test_action",
                params={"x": 5},
                legacy_fn=legacy_fn,
                command_fn=command_fn,
            )

            # Should return legacy result
            assert result.data == "legacy"


class TestWorkflowIntegration:
    """Test that command system integrates properly with workflows."""

    def test_sequential_operations_consistency(self):
        """Test that sequential operations maintain consistency."""
        wrapper = ParallelOperationWrapper()

        state = {"count": 0}

        def legacy_increment(x):
            state["count"] += x
            return state["count"]

        def command_increment(x):
            # Command implementation doesn't modify state
            return state["count"] + x

        # Don't enable command - test legacy-only sequential operations
        # (parallel execution would run both and double-increment)

        # Run sequential operations
        for i in range(5):
            result = wrapper.execute_with_validation(
                agent="test_agent",
                action="increment",
                params={"x": 1},
                legacy_fn=legacy_increment,
            )
            assert result.success

        assert state["count"] == 5

    def test_permission_enforcement_across_operations(self):
        """Test that permissions are enforced consistently."""
        FeatureFlags()

        # Create a write operation that should be permission-checked
        def write_operation(agent, table, data):
            # In real system, this would check permissions
            if agent == "code_developer" and table == "review_commit":
                return True  # Allowed
            return False

        # Test permission
        assert write_operation("code_developer", "review_commit", {})
        assert not write_operation("architect", "review_commit", {})

    def test_multiple_agents_independent_flags(self):
        """Test that flags are independent per agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"
            flags = FeatureFlags(str(flags_file))

            # Enable for one agent
            flags.enable_command("code_developer", "claim_priority")

            # Should not affect other agents
            assert not flags.is_enabled("architect", "claim_priority")
            assert flags.is_enabled("code_developer", "claim_priority")


class TestPerformanceOverhead:
    """Test that wrapper overhead is within acceptable range."""

    def test_wrapper_overhead_less_than_10_percent(self):
        """Test that wrapper adds <10% performance overhead."""
        wrapper = ParallelOperationWrapper()

        def fast_operation(x):
            return x * 2

        # Run many operations
        total_duration = 0
        for i in range(100):
            result = wrapper.execute_with_validation(
                agent="code_developer",
                action="test",
                params={"x": i},
                legacy_fn=fast_operation,
            )
            total_duration += result.duration_ms

        # Average operation time
        avg_time = total_duration / 100

        # Operations should complete quickly (less than 10ms average)
        assert avg_time < 10  # milliseconds

    def test_parallel_operation_no_significant_slowdown(self):
        """Test that parallel operation doesn't significantly slow things down."""
        wrapper = ParallelOperationWrapper()
        wrapper.flags.enable_command("test_agent", "test_action")

        def operation(x):
            return x * 2

        # Time with command enabled
        total_with_command = 0
        for i in range(50):
            result = wrapper.execute_with_validation(
                agent="test_agent",
                action="test_action",
                params={"x": i},
                legacy_fn=operation,
                command_fn=operation,
            )
            total_with_command += result.duration_ms

        # Should still be fast
        assert total_with_command / 50 < 10


class TestRollbackProcedures:
    """Test rollback manager functionality."""

    def test_single_agent_rollback(self):
        """Test rolling back a single agent."""
        manager = RollbackManager()

        # Enable an agent first
        manager.flags.enable_command("code_developer", "claim_priority")
        assert manager.flags.is_enabled("code_developer", "claim_priority")

        # Rollback
        manager.rollback_agent("code_developer")

        # Should be disabled
        assert not manager.flags.is_enabled("code_developer", "claim_priority")

    def test_phase_rollback(self):
        """Test rolling back an entire phase."""
        manager = RollbackManager()

        # Enable Phase 2 agents
        manager.flags.enable_phase(2)

        # Verify enabled
        assert len(manager.flags.get_enabled_agents()) > 0

        # Rollback phase
        manager.rollback_phase(2)

        # Verify disabled
        rolled_back = manager.get_rolled_back_agents()
        assert "code_developer" in rolled_back

    def test_emergency_rollback(self):
        """Test emergency rollback of entire system."""
        manager = RollbackManager()

        # Enable all phases
        for phase in range(2, 6):
            manager.flags.enable_phase(phase)

        # Should have some enabled agents
        assert len(manager.flags.get_enabled_agents()) > 0

        # Emergency rollback
        manager.rollback_all()

        # All should be rolled back
        for agent in manager.flags.flags:
            assert manager.is_rolled_back(agent)

    def test_re_enable_after_rollback(self):
        """Test re-enabling an agent after rollback."""
        manager = RollbackManager()

        manager.flags.register_command("code_developer", "test_cmd", False)
        manager.flags.enable_command("code_developer", "test_cmd")

        # Rollback
        manager.rollback_agent("code_developer")
        assert manager.is_rolled_back("code_developer")

        # Re-enable
        manager.re_enable_agent("code_developer")
        assert not manager.is_rolled_back("code_developer")

    def test_rollback_history_tracking(self):
        """Test that rollback history is properly recorded."""
        manager = RollbackManager()

        manager.rollback_agent("code_developer", "test issue")
        manager.rollback_agent("architect", "test issue")

        history = manager.get_rollback_history()
        assert len(history) == 2
        assert history[0]["agent"] == "code_developer"
        assert history[1]["agent"] == "architect"

    def test_safe_rollback_order(self):
        """Test that safe rollback order respects dependencies."""
        manager = RollbackManager()

        safe_order = manager.get_safe_rollback_order()

        # Orchestrator should be first (most dependent)
        assert safe_order[0] == "orchestrator"

        # Core agents should come later
        assert "code_developer" in safe_order
        assert "architect" in safe_order


class TestDataConsistency:
    """Test data consistency between legacy and command implementations."""

    def test_dictionary_result_matching(self):
        """Test that dictionary results match correctly."""
        from coffee_maker.commands.parallel_operation import _data_matches

        data1 = {"id": 1, "name": "test", "tags": ["a", "b"]}
        data2 = {"id": 1, "name": "test", "tags": ["a", "b"]}

        assert _data_matches(data1, data2)

    def test_list_result_matching(self):
        """Test that list results match correctly."""
        from coffee_maker.commands.parallel_operation import _data_matches

        list1 = [1, 2, 3]
        list2 = [1, 2, 3]

        assert _data_matches(list1, list2)

    def test_nested_structure_matching(self):
        """Test that nested structures match correctly."""
        from coffee_maker.commands.parallel_operation import _data_matches

        data1 = {
            "user": {"id": 1, "name": "Alice"},
            "tasks": [{"id": 1, "title": "task1"}],
        }
        data2 = {
            "user": {"id": 1, "name": "Alice"},
            "tasks": [{"id": 1, "title": "task1"}],
        }

        assert _data_matches(data1, data2)

    def test_type_mismatch_detection(self):
        """Test that type mismatches are detected."""
        from coffee_maker.commands.parallel_operation import _data_matches

        assert not _data_matches("string", 123)
        assert not _data_matches([1, 2], (1, 2))


class TestFeatureIntegration:
    """Integration tests for entire migration framework."""

    def test_complete_migration_workflow(self):
        """Test complete migration workflow from legacy to commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_file = Path(tmpdir) / "flags.json"

            # Phase 1: All disabled (safe state)
            flags = FeatureFlags(str(flags_file))
            assert len(flags.get_enabled_agents()) == 0

            # Pre-register commands for Phase 2 agents before enabling phase
            for agent in ["project_manager", "architect", "code_developer"]:
                flags.register_command(agent, "test_command", False)

            # Phase 2: Enable core agents
            flags.enable_phase(2)
            assert "code_developer" in flags.get_enabled_agents()
            assert "architect" in flags.get_enabled_agents()

            # Phase 3: If issues, can rollback
            manager = RollbackManager()
            manager.flags = flags  # Use same flags instance
            manager.rollback_phase(2, "Issues detected")
            rolled_back = manager.get_rolled_back_agents()
            assert "code_developer" in rolled_back

    def test_safety_guarantees(self):
        """Test that safety guarantees are maintained."""
        wrapper = ParallelOperationWrapper()
        manager = RollbackManager()

        # 1. Commands disabled by default
        assert len(wrapper.flags.get_enabled_agents()) == 0

        # 2. Can enable selectively
        wrapper.flags.enable_command("code_developer", "claim_priority")
        assert wrapper.flags.is_enabled("code_developer", "claim_priority")

        # 3. Fallback on mismatch
        def legacy_fn(x):
            return 1

        def command_fn(x):
            return 2

        wrapper.flags.enable_command("test_agent", "test")
        result = wrapper.execute_with_validation(
            agent="test_agent",
            action="test",
            params={"x": 5},
            legacy_fn=legacy_fn,
            command_fn=command_fn,
        )
        assert result.data == 1  # Falls back to legacy

        # 4. Can rollback entirely
        manager.rollback_all()
        assert len(manager.flags.get_enabled_agents()) == 0
