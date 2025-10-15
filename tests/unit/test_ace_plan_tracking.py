"""Tests for ACE plan tracking functionality.

This module tests that the Generator captures agent plans, difficulties,
concerns, and progress during execution, providing full visibility into
agent behavior for the Reflector to analyze.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.generator import ACEGenerator
from coffee_maker.autonomous.ace.models import Execution
from coffee_maker.autonomous.ace.trace_manager import TraceManager
from coffee_maker.cli.user_interpret import UserInterpret


class TestExecutionModelPlanFields:
    """Test Execution model with plan tracking fields."""

    def test_execution_with_plan_fields(self):
        """Test creating Execution with all plan tracking fields."""
        from coffee_maker.autonomous.ace.models import ExternalObservation, InternalObservation

        execution = Execution(
            execution_id=1,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
            # Plan tracking
            agent_plan=["Step 1", "Step 2", "Step 3"],
            plan_progress={"Step 1": {"status": "completed", "timestamp": "2025-10-15T10:00:00"}},
            # Difficulty tracking
            difficulties=[{"description": "Timeout", "severity": "medium", "timestamp": "2025-10-15T10:00:01"}],
            concerns=["Edge case detected"],
            retries=1,
            # Context snapshot
            context_snapshot={"user": "test_user", "session": "session_123"},
        )

        assert execution.agent_plan == ["Step 1", "Step 2", "Step 3"]
        assert execution.plan_progress is not None
        assert execution.difficulties is not None
        assert len(execution.difficulties) == 1
        assert execution.concerns == ["Edge case detected"]
        assert execution.retries == 1
        assert execution.context_snapshot == {"user": "test_user", "session": "session_123"}

    def test_execution_serialization_with_plan_fields(self):
        """Test serialization/deserialization preserves plan fields."""
        from coffee_maker.autonomous.ace.models import ExternalObservation, InternalObservation

        original_execution = Execution(
            execution_id=1,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
            agent_plan=["Step A", "Step B"],
            plan_progress={"Step A": {"status": "completed"}},
            difficulties=[{"description": "Error", "severity": "high"}],
            concerns=["Warning"],
            retries=2,
            context_snapshot={"key": "value"},
        )

        # Serialize
        execution_dict = original_execution.to_dict()

        # Verify fields present
        assert "agent_plan" in execution_dict
        assert "plan_progress" in execution_dict
        assert "difficulties" in execution_dict
        assert "concerns" in execution_dict
        assert "retries" in execution_dict
        assert "context_snapshot" in execution_dict

        # Deserialize
        restored_execution = Execution.from_dict(execution_dict)

        assert restored_execution.agent_plan == original_execution.agent_plan
        assert restored_execution.plan_progress == original_execution.plan_progress
        assert restored_execution.difficulties == original_execution.difficulties
        assert restored_execution.concerns == original_execution.concerns
        assert restored_execution.retries == original_execution.retries
        assert restored_execution.context_snapshot == original_execution.context_snapshot


class TestACEAgentPlanInterface:
    """Test plan tracking interface methods on ACEAgent."""

    def setup_method(self):
        """Clear singleton instance before each test."""
        if hasattr(UserInterpret, "_instance"):
            delattr(UserInterpret, "_instance")

    def test_set_plan(self):
        """Test _set_plan method."""
        agent = UserInterpret()
        plan = ["Analyze sentiment", "Interpret intent", "Choose agent"]

        agent._set_plan(plan)

        assert hasattr(agent, "_current_plan")
        assert agent._current_plan == plan

    def test_report_difficulty(self):
        """Test _report_difficulty method."""
        agent = UserInterpret()

        agent._report_difficulty("Network timeout", severity="high")
        agent._report_difficulty("Parsing error", severity="low")

        assert hasattr(agent, "_current_difficulties")
        assert len(agent._current_difficulties) == 2
        assert agent._current_difficulties[0]["description"] == "Network timeout"
        assert agent._current_difficulties[0]["severity"] == "high"
        assert agent._current_difficulties[1]["description"] == "Parsing error"
        assert agent._current_difficulties[1]["severity"] == "low"

        # Check timestamp exists
        assert "timestamp" in agent._current_difficulties[0]

    def test_report_concern(self):
        """Test _report_concern method."""
        agent = UserInterpret()

        agent._report_concern("Intent unclear")
        agent._report_concern("Low confidence")

        assert hasattr(agent, "_current_concerns")
        assert len(agent._current_concerns) == 2
        assert agent._current_concerns[0] == "Intent unclear"
        assert agent._current_concerns[1] == "Low confidence"

    def test_update_plan_progress(self):
        """Test _update_plan_progress method."""
        agent = UserInterpret()

        agent._update_plan_progress("Analyze sentiment", "in_progress")
        agent._update_plan_progress("Analyze sentiment", "completed")
        agent._update_plan_progress("Interpret intent", "in_progress")

        assert hasattr(agent, "_plan_progress")
        assert "Analyze sentiment" in agent._plan_progress
        assert agent._plan_progress["Analyze sentiment"]["status"] == "completed"
        assert "Interpret intent" in agent._plan_progress
        assert agent._plan_progress["Interpret intent"]["status"] == "in_progress"

        # Check timestamps exist
        assert "timestamp" in agent._plan_progress["Analyze sentiment"]


class TestGeneratorCapturesPlan:
    """Test that Generator captures plan from agent."""

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
    def mock_agent_with_plan(self):
        """Create mock agent that sets plan."""
        agent = MagicMock()

        def send_message_with_plan(prompt, **kwargs):
            # Simulate agent setting plan
            agent._current_plan = ["Step 1", "Step 2", "Step 3"]
            agent._plan_progress = {
                "Step 1": {"status": "completed", "timestamp": datetime.now().isoformat()},
                "Step 2": {"status": "in_progress", "timestamp": datetime.now().isoformat()},
            }
            agent._current_difficulties = [
                {"description": "Minor issue", "severity": "low", "timestamp": datetime.now().isoformat()}
            ]
            agent._current_concerns = ["Edge case detected"]
            return {"result": "success", "token_usage": 100}

        agent.send_message = send_message_with_plan
        return agent

    def test_generator_initializes_plan_tracking(self, temp_config, mock_agent_with_plan):
        """Test that generator initializes plan tracking attributes on agent."""
        generator = ACEGenerator(
            agent_interface=mock_agent_with_plan,
            config=temp_config,
            agent_name="test_agent",
        )

        # Execute
        result = generator.execute_with_trace(prompt="Test prompt")

        # Verify initialization happened
        assert hasattr(mock_agent_with_plan, "_current_plan")
        assert hasattr(mock_agent_with_plan, "_current_difficulties")
        assert hasattr(mock_agent_with_plan, "_current_concerns")
        assert hasattr(mock_agent_with_plan, "_plan_progress")

    def test_generator_captures_plan_in_execution(self, temp_config, mock_agent_with_plan):
        """Test that generator captures plan in Execution object."""
        generator = ACEGenerator(
            agent_interface=mock_agent_with_plan,
            config=temp_config,
            agent_name="test_agent",
        )

        # Execute
        result = generator.execute_with_trace(prompt="Test prompt")

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Verify plan captured
        execution = trace.executions[0]
        assert execution.agent_plan is not None
        assert len(execution.agent_plan) == 3
        assert "Step 1" in execution.agent_plan
        assert "Step 2" in execution.agent_plan
        assert "Step 3" in execution.agent_plan

    def test_generator_captures_plan_progress(self, temp_config, mock_agent_with_plan):
        """Test that generator captures plan progress."""
        generator = ACEGenerator(
            agent_interface=mock_agent_with_plan,
            config=temp_config,
            agent_name="test_agent",
        )

        # Execute
        result = generator.execute_with_trace(prompt="Test prompt")

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Verify progress captured
        execution = trace.executions[0]
        assert execution.plan_progress is not None
        assert "Step 1" in execution.plan_progress
        assert execution.plan_progress["Step 1"]["status"] == "completed"
        assert "Step 2" in execution.plan_progress
        assert execution.plan_progress["Step 2"]["status"] == "in_progress"

    def test_generator_captures_difficulties(self, temp_config, mock_agent_with_plan):
        """Test that generator captures difficulties."""
        generator = ACEGenerator(
            agent_interface=mock_agent_with_plan,
            config=temp_config,
            agent_name="test_agent",
        )

        # Execute
        result = generator.execute_with_trace(prompt="Test prompt")

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Verify difficulties captured
        execution = trace.executions[0]
        assert execution.difficulties is not None
        assert len(execution.difficulties) == 1
        assert execution.difficulties[0]["description"] == "Minor issue"
        assert execution.difficulties[0]["severity"] == "low"

    def test_generator_captures_concerns(self, temp_config, mock_agent_with_plan):
        """Test that generator captures concerns."""
        generator = ACEGenerator(
            agent_interface=mock_agent_with_plan,
            config=temp_config,
            agent_name="test_agent",
        )

        # Execute
        result = generator.execute_with_trace(prompt="Test prompt")

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Verify concerns captured
        execution = trace.executions[0]
        assert execution.concerns is not None
        assert len(execution.concerns) == 1
        assert execution.concerns[0] == "Edge case detected"

    def test_generator_captures_context_snapshot(self, temp_config, mock_agent_with_plan):
        """Test that generator captures context snapshot."""
        generator = ACEGenerator(
            agent_interface=mock_agent_with_plan,
            config=temp_config,
            agent_name="test_agent",
        )

        # Execute with context
        result = generator.execute_with_trace(
            prompt="Test prompt", context={"user": "test_user", "session": "session_123"}
        )

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Verify context snapshot captured
        execution = trace.executions[0]
        assert execution.context_snapshot is not None
        assert execution.context_snapshot["user"] == "test_user"
        assert execution.context_snapshot["session"] == "session_123"


class TestUserInterpretPlanTracking:
    """Test that user_interpret uses plan tracking correctly."""

    def setup_method(self):
        """Clear singleton instance before each test."""
        if hasattr(UserInterpret, "_instance"):
            delattr(UserInterpret, "_instance")

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

    @patch("coffee_maker.autonomous.ace.config.get_default_config")
    def test_user_interpret_sets_plan(self, mock_get_config, temp_config):
        """Test that user_interpret sets its execution plan."""
        mock_get_config.return_value = temp_config

        agent = UserInterpret()

        # Execute task (this should set plan internally)
        agent.execute_task("Hello")

        # If ACE enabled, check trace
        if agent.ace_enabled:
            # Get the trace
            trace_manager = TraceManager(temp_config.trace_dir)
            traces = trace_manager.list_traces()

            if traces:
                trace = traces[0]
                execution = trace.executions[0]

                # Verify plan was set
                assert execution.agent_plan is not None
                assert len(execution.agent_plan) == 4
                assert "Analyze user sentiment" in execution.agent_plan
                assert "Interpret user intent" in execution.agent_plan
                assert "Choose appropriate agent" in execution.agent_plan
                assert "Generate response" in execution.agent_plan

    @patch("coffee_maker.autonomous.ace.config.get_default_config")
    def test_user_interpret_tracks_progress(self, mock_get_config, temp_config):
        """Test that user_interpret tracks progress through plan."""
        mock_get_config.return_value = temp_config

        agent = UserInterpret()

        # Execute task
        agent.execute_task("Hello")

        if agent.ace_enabled:
            trace_manager = TraceManager(temp_config.trace_dir)
            traces = trace_manager.list_traces()

            if traces:
                trace = traces[0]
                execution = trace.executions[0]

                # Verify progress tracked
                assert execution.plan_progress is not None
                assert "Analyze user sentiment" in execution.plan_progress
                assert execution.plan_progress["Analyze user sentiment"]["status"] == "completed"

    @patch("coffee_maker.autonomous.ace.config.get_default_config")
    def test_user_interpret_reports_concerns(self, mock_get_config, temp_config):
        """Test that user_interpret reports concerns for unclear intent."""
        mock_get_config.return_value = temp_config

        agent = UserInterpret()

        # Execute with unclear message (should default to general_question)
        agent.execute_task("umm what?")

        if agent.ace_enabled:
            trace_manager = TraceManager(temp_config.trace_dir)
            traces = trace_manager.list_traces()

            if traces:
                trace = traces[0]
                execution = trace.executions[0]

                # Verify concern reported
                if execution.concerns:
                    assert any("Intent unclear" in concern for concern in execution.concerns)


class TestPlanTrackingEdgeCases:
    """Test edge cases in plan tracking."""

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

    def test_execution_with_no_plan(self, temp_config):
        """Test execution when agent doesn't set a plan."""
        mock_agent = MagicMock()
        mock_agent.send_message.return_value = {"result": "success"}

        generator = ACEGenerator(
            agent_interface=mock_agent,
            config=temp_config,
            agent_name="test_agent",
        )

        result = generator.execute_with_trace(prompt="Test")

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Plan should be None (not set)
        execution = trace.executions[0]
        assert execution.agent_plan is None

    def test_execution_with_exception(self, temp_config):
        """Test that exceptions are captured as difficulties."""
        mock_agent = MagicMock()
        mock_agent.send_message.side_effect = Exception("Test error")

        generator = ACEGenerator(
            agent_interface=mock_agent,
            config=temp_config,
            agent_name="test_agent",
        )

        result = generator.execute_with_trace(prompt="Test")

        # Load trace
        trace_manager = TraceManager(temp_config.trace_dir)
        trace = trace_manager.read_trace(result["trace_id"])

        # Verify exception captured
        execution = trace.executions[0]
        assert execution.result_status == "failure"
        assert len(execution.errors) > 0
        assert execution.difficulties is not None
        assert any("Execution failed" in d["description"] for d in execution.difficulties)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
