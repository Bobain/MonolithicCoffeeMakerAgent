"""Tests for ACE delegation chain tracking.

This module tests the delegation chain propagation feature which ensures
user satisfaction signals flow from delegating agents (user_listener) to
delegated agents (code_developer) through the trace chain.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.generator import ACEGenerator
from coffee_maker.autonomous.ace.models import (
    ExecutionTrace,
)
from coffee_maker.autonomous.ace.reflector import ACEReflector
from coffee_maker.autonomous.ace.trace_manager import TraceManager
from coffee_maker.cli.user_listener_ace import UserListenerACE


class TestExecutionTraceModel:
    """Test ExecutionTrace model with delegation chain fields."""

    def test_trace_with_delegation_chain(self):
        """Test creating trace with delegation chain."""
        trace = ExecutionTrace(
            trace_id="trace_123",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "code_developer",
                "agent_objective": "Implement features",
                "success_criteria": "Tests pass",
            },
            user_query="Implement authentication",
            current_context="# Playbook",
            parent_trace_id="trace_122",
            delegation_chain=[
                {
                    "agent": "user_listener",
                    "trace_id": "trace_122",
                    "timestamp": "2025-10-15T10:00:00",
                },
                {
                    "agent": "code_developer",
                    "trace_id": "trace_123",
                    "timestamp": "2025-10-15T10:00:01",
                },
            ],
        )

        assert trace.parent_trace_id == "trace_122"
        assert len(trace.delegation_chain) == 2
        assert trace.delegation_chain[0]["agent"] == "user_listener"
        assert trace.delegation_chain[1]["agent"] == "code_developer"

    def test_trace_serialization_with_delegation_chain(self):
        """Test serialization/deserialization preserves delegation chain."""
        original_trace = ExecutionTrace(
            trace_id="trace_123",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "code_developer",
                "agent_objective": "Implement features",
                "success_criteria": "Tests pass",
            },
            user_query="Implement authentication",
            current_context="# Playbook",
            parent_trace_id="trace_122",
            delegation_chain=[
                {
                    "agent": "user_listener",
                    "trace_id": "trace_122",
                    "timestamp": "2025-10-15T10:00:00",
                }
            ],
        )

        # Serialize to dict
        trace_dict = original_trace.to_dict()

        # Verify delegation fields present
        assert "parent_trace_id" in trace_dict
        assert "delegation_chain" in trace_dict
        assert trace_dict["parent_trace_id"] == "trace_122"
        assert len(trace_dict["delegation_chain"]) == 1

        # Deserialize back
        restored_trace = ExecutionTrace.from_dict(trace_dict)

        assert restored_trace.parent_trace_id == original_trace.parent_trace_id
        assert restored_trace.delegation_chain == original_trace.delegation_chain

    def test_trace_markdown_shows_delegation_chain(self):
        """Test markdown representation includes delegation chain."""
        trace = ExecutionTrace(
            trace_id="trace_123",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "code_developer",
                "agent_objective": "Implement features",
                "success_criteria": "Tests pass",
            },
            user_query="Implement authentication",
            current_context="# Playbook",
            parent_trace_id="trace_122",
            delegation_chain=[
                {
                    "agent": "user_listener",
                    "trace_id": "trace_122",
                    "timestamp": "2025-10-15T10:00:00",
                },
                {
                    "agent": "code_developer",
                    "trace_id": "trace_123",
                    "timestamp": "2025-10-15T10:00:01",
                },
            ],
        )

        markdown = trace.to_markdown()

        # Verify delegation chain appears in markdown
        assert "## Delegation Chain" in markdown
        assert "user_listener" in markdown
        assert "trace_122" in markdown
        assert "code_developer" in markdown
        assert "trace_123" in markdown
        assert "**Parent Trace**: trace_122" in markdown


class TestACEGeneratorDelegationChain:
    """Test ACEGenerator delegation chain tracking."""

    @pytest.fixture
    def temp_config(self):
        """Create temporary ACE config for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ACEConfig(
                trace_dir=Path(tmpdir) / "traces",
                delta_dir=Path(tmpdir) / "deltas",
                playbook_dir=Path(tmpdir) / "playbooks",
            )
            config.ensure_directories()
            yield config

    @pytest.fixture
    def mock_agent_interface(self):
        """Create mock agent interface."""
        interface = MagicMock()
        interface.send_message.return_value = {
            "result": "success",
            "token_usage": 100,
        }
        return interface

    def test_generator_accepts_delegation_chain(self, temp_config, mock_agent_interface):
        """Test generator accepts parent_trace_id and delegation_chain."""
        generator = ACEGenerator(
            agent_interface=mock_agent_interface,
            config=temp_config,
            agent_name="code_developer",
        )

        # Execute with delegation chain
        result = generator.execute_with_trace(
            prompt="Implement feature X",
            parent_trace_id="trace_122",
            delegation_chain=[
                {
                    "agent": "user_listener",
                    "trace_id": "trace_122",
                    "timestamp": "2025-10-15T10:00:00",
                }
            ],
        )

        assert "trace_id" in result

        # Load saved trace and verify chain
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        assert trace.parent_trace_id == "trace_122"
        assert len(trace.delegation_chain) == 2  # user_listener + code_developer
        assert trace.delegation_chain[0]["agent"] == "user_listener"
        assert trace.delegation_chain[1]["agent"] == "code_developer"

    def test_generator_creates_chain_from_none(self, temp_config, mock_agent_interface):
        """Test generator creates new chain if none provided."""
        generator = ACEGenerator(
            agent_interface=mock_agent_interface,
            config=temp_config,
            agent_name="code_developer",
        )

        # Execute without delegation chain
        result = generator.execute_with_trace(prompt="Implement feature X")

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Should have chain with just current agent
        assert trace.parent_trace_id is None
        assert len(trace.delegation_chain) == 1
        assert trace.delegation_chain[0]["agent"] == "code_developer"


class TestUserListenerACEDelegation:
    """Test UserListenerACE delegation observation."""

    @pytest.fixture
    def temp_config(self):
        """Create temporary ACE config for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ACEConfig(
                trace_dir=Path(tmpdir) / "traces",
                delta_dir=Path(tmpdir) / "deltas",
                playbook_dir=Path(tmpdir) / "playbooks",
            )
            config.ensure_directories()
            yield config

    @patch("coffee_maker.cli.user_listener_ace.get_default_config")
    def test_observe_delegation_creates_trace(self, mock_get_config, temp_config):
        """Test observe_delegation creates and returns trace_id."""
        mock_get_config.return_value = temp_config

        ace = UserListenerACE(enabled=True)

        # Observe delegation
        trace_id = ace.observe_delegation(
            user_query="Implement authentication",
            intent="code_implementation",
            delegated_to="code_developer",
            success=True,
            duration_seconds=5.0,
        )

        assert trace_id is not None

        # Verify trace was created
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(trace_id)

        assert trace.agent_identity["target_agent"] == "user_listener"
        assert trace.parent_trace_id is None  # Top of chain
        assert len(trace.delegation_chain) == 1
        assert trace.delegation_chain[0]["agent"] == "user_listener"

    @patch("coffee_maker.cli.user_listener_ace.get_default_config")
    def test_observe_delegation_disabled(self, mock_get_config, temp_config):
        """Test observe_delegation returns None when ACE disabled."""
        mock_get_config.return_value = temp_config

        ace = UserListenerACE(enabled=False)

        # Observe delegation
        trace_id = ace.observe_delegation(
            user_query="Implement authentication",
            intent="code_implementation",
            delegated_to="code_developer",
            success=True,
            duration_seconds=5.0,
        )

        assert trace_id is None


class TestReflectorSatisfactionPropagation:
    """Test ACEReflector satisfaction propagation."""

    @pytest.fixture
    def temp_config(self):
        """Create temporary ACE config for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ACEConfig(
                trace_dir=Path(tmpdir) / "traces",
                delta_dir=Path(tmpdir) / "deltas",
                playbook_dir=Path(tmpdir) / "playbooks",
            )
            config.ensure_directories()
            yield config

    def test_propagate_satisfaction_to_child(self, temp_config):
        """Test satisfaction propagates from parent to child trace."""
        trace_manager = TraceManager(temp_config.trace_dir)

        # Create parent trace (user_listener) with satisfaction
        parent_trace = ExecutionTrace(
            trace_id="trace_122",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "user_listener",
                "agent_objective": "Delegate user requests",
                "success_criteria": "Correct delegation",
            },
            user_query="Implement authentication",
            current_context="",
            user_satisfaction={
                "score": 5,
                "positive_feedback": "Perfect implementation!",
                "timestamp": "2025-10-15T10:00:00",
            },
        )
        trace_manager.write_trace(parent_trace)

        # Create child trace (code_developer) without satisfaction
        child_trace = ExecutionTrace(
            trace_id="trace_123",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "code_developer",
                "agent_objective": "Implement features",
                "success_criteria": "Tests pass",
            },
            user_query="Implement authentication",
            current_context="",
            parent_trace_id="trace_122",
            delegation_chain=[
                {"agent": "user_listener", "trace_id": "trace_122"},
                {"agent": "code_developer", "trace_id": "trace_123"},
            ],
        )
        trace_manager.write_trace(child_trace)

        # Propagate satisfaction
        reflector = ACEReflector(
            agent_name="user_listener",
            traces_base_dir=temp_config.trace_dir,
            deltas_base_dir=temp_config.delta_dir,
        )

        num_propagated = reflector.propagate_satisfaction("trace_122")

        assert num_propagated == 1

        # Verify child trace now has satisfaction
        updated_child = trace_manager.read_trace("trace_123")
        assert updated_child.user_satisfaction is not None
        assert updated_child.user_satisfaction["score"] == 5
        assert "propagated_from" in updated_child.user_satisfaction
        assert updated_child.user_satisfaction["propagated_from"] == "trace_122"

    def test_propagate_satisfaction_multi_level(self, temp_config):
        """Test satisfaction propagates through multi-level delegation chain."""
        trace_manager = TraceManager(temp_config.trace_dir)

        # Create 3-level chain: user_listener → assistant → code_developer
        traces = [
            ExecutionTrace(
                trace_id="trace_1",
                timestamp=datetime.now(),
                agent_identity={
                    "target_agent": "user_listener",
                    "agent_objective": "Delegate",
                    "success_criteria": "Correct",
                },
                user_query="Fix bug",
                current_context="",
                user_satisfaction={
                    "score": 4,
                    "positive_feedback": "Good work",
                    "timestamp": "2025-10-15T10:00:00",
                },
            ),
            ExecutionTrace(
                trace_id="trace_2",
                timestamp=datetime.now(),
                agent_identity={
                    "target_agent": "assistant",
                    "agent_objective": "Triage",
                    "success_criteria": "Correct",
                },
                user_query="Fix bug",
                current_context="",
                parent_trace_id="trace_1",
            ),
            ExecutionTrace(
                trace_id="trace_3",
                timestamp=datetime.now(),
                agent_identity={
                    "target_agent": "code_developer",
                    "agent_objective": "Implement",
                    "success_criteria": "Tests pass",
                },
                user_query="Fix bug",
                current_context="",
                parent_trace_id="trace_2",
            ),
        ]

        for trace in traces:
            trace_manager.write_trace(trace)

        # Propagate from top
        reflector = ACEReflector(
            agent_name="user_listener",
            traces_base_dir=temp_config.trace_dir,
            deltas_base_dir=temp_config.delta_dir,
        )

        num_propagated = reflector.propagate_satisfaction("trace_1")

        # Should propagate to both children (assistant and code_developer)
        assert num_propagated == 2

        # Verify both children have satisfaction
        trace_2 = trace_manager.read_trace("trace_2")
        trace_3 = trace_manager.read_trace("trace_3")

        assert trace_2.user_satisfaction is not None
        assert trace_2.user_satisfaction["score"] == 4
        assert trace_2.user_satisfaction["propagated_from"] == "trace_1"

        assert trace_3.user_satisfaction is not None
        assert trace_3.user_satisfaction["score"] == 4
        # Grandchild should be propagated from parent (trace_2)
        assert trace_3.user_satisfaction["propagated_from"] == "trace_2"

    def test_propagate_satisfaction_no_children(self, temp_config):
        """Test propagation with no child traces."""
        trace_manager = TraceManager(temp_config.trace_dir)

        # Create parent trace with satisfaction but no children
        parent_trace = ExecutionTrace(
            trace_id="trace_100",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "user_listener",
                "agent_objective": "Delegate",
                "success_criteria": "Correct",
            },
            user_query="Test",
            current_context="",
            user_satisfaction={
                "score": 3,
                "timestamp": "2025-10-15T10:00:00",
            },
        )
        trace_manager.write_trace(parent_trace)

        # Propagate
        reflector = ACEReflector(
            agent_name="user_listener",
            traces_base_dir=temp_config.trace_dir,
            deltas_base_dir=temp_config.delta_dir,
        )

        num_propagated = reflector.propagate_satisfaction("trace_100")

        # No children, so nothing propagated
        assert num_propagated == 0

    def test_propagate_satisfaction_no_satisfaction_data(self, temp_config):
        """Test propagation when parent has no satisfaction data."""
        trace_manager = TraceManager(temp_config.trace_dir)

        # Create parent trace WITHOUT satisfaction
        parent_trace = ExecutionTrace(
            trace_id="trace_200",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "user_listener",
                "agent_objective": "Delegate",
                "success_criteria": "Correct",
            },
            user_query="Test",
            current_context="",
        )
        trace_manager.write_trace(parent_trace)

        # Create child
        child_trace = ExecutionTrace(
            trace_id="trace_201",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "code_developer",
                "agent_objective": "Implement",
                "success_criteria": "Tests pass",
            },
            user_query="Test",
            current_context="",
            parent_trace_id="trace_200",
        )
        trace_manager.write_trace(child_trace)

        # Propagate
        reflector = ACEReflector(
            agent_name="user_listener",
            traces_base_dir=temp_config.trace_dir,
            deltas_base_dir=temp_config.delta_dir,
        )

        num_propagated = reflector.propagate_satisfaction("trace_200")

        # No satisfaction to propagate
        assert num_propagated == 0


class TestEndToEndDelegationChain:
    """End-to-end integration tests for delegation chain."""

    @pytest.fixture
    def temp_config(self):
        """Create temporary ACE config for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ACEConfig(
                trace_dir=Path(tmpdir) / "traces",
                delta_dir=Path(tmpdir) / "deltas",
                playbook_dir=Path(tmpdir) / "playbooks",
            )
            config.ensure_directories()
            yield config

    @patch("coffee_maker.cli.user_listener_ace.get_default_config")
    def test_full_delegation_workflow(self, mock_get_config, temp_config):
        """Test complete workflow: user_listener → code_developer → satisfaction."""
        mock_get_config.return_value = temp_config

        # 1. User asks user_listener
        user_listener_ace = UserListenerACE(enabled=True)
        parent_trace_id = user_listener_ace.observe_delegation(
            user_query="Implement authentication",
            intent="code_implementation",
            delegated_to="code_developer",
            success=True,
            duration_seconds=2.0,
        )

        assert parent_trace_id is not None

        # 2. code_developer executes (simulate)
        mock_interface = MagicMock()
        mock_interface.send_message.return_value = {"result": "success"}

        code_dev_generator = ACEGenerator(
            agent_interface=mock_interface,
            config=temp_config,
            agent_name="code_developer",
        )

        # Get delegation chain from parent trace
        trace_manager = TraceManager(temp_config.trace_dir)
        parent_trace = trace_manager.read_trace(parent_trace_id)

        result = code_dev_generator.execute_with_trace(
            prompt="Implement authentication feature",
            parent_trace_id=parent_trace_id,
            delegation_chain=parent_trace.delegation_chain,
        )

        child_trace_id = result["trace_id"]

        # Verify child trace has parent_trace_id set correctly
        child_trace = trace_manager.read_trace(child_trace_id)
        assert child_trace.parent_trace_id == parent_trace_id, (
            f"Child trace parent_trace_id={child_trace.parent_trace_id}, " f"expected={parent_trace_id}"
        )

        # 3. User provides satisfaction to user_listener
        parent_trace.user_satisfaction = {
            "score": 5,
            "positive_feedback": "Perfect!",
            "timestamp": datetime.now().isoformat(),
        }
        trace_manager.write_trace(parent_trace)

        # 4. Propagate satisfaction
        reflector = ACEReflector(
            agent_name="user_listener",
            traces_base_dir=temp_config.trace_dir,
            deltas_base_dir=temp_config.delta_dir,
        )

        num_propagated = reflector.propagate_satisfaction(parent_trace_id)

        # Debug: List all traces to see what's available
        all_traces = trace_manager.list_traces()
        print(f"\n=== All traces: {len(all_traces)} ===")
        for trace in all_traces:
            print(
                f"  - {trace.trace_id}: agent={trace.agent_identity.get('target_agent')}, parent={trace.parent_trace_id}"
            )

        assert num_propagated == 1, (
            f"Expected 1 propagation, got {num_propagated}. " f"Parent: {parent_trace_id}, Child: {child_trace_id}"
        )

        # 5. Verify code_developer trace has satisfaction
        child_trace = trace_manager.read_trace(child_trace_id)
        assert child_trace.user_satisfaction is not None
        assert child_trace.user_satisfaction["score"] == 5
        assert child_trace.user_satisfaction["propagated_from"] == parent_trace_id

        # 6. Verify delegation chain in child trace
        assert len(child_trace.delegation_chain) == 2
        assert child_trace.delegation_chain[0]["agent"] == "user_listener"
        assert child_trace.delegation_chain[1]["agent"] == "code_developer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
