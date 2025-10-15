"""Tests for ACE API layer."""

import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from coffee_maker.autonomous.ace.api import ACEApi
from coffee_maker.autonomous.ace.models import (
    ExecutionTrace,
    Execution,
    ExternalObservation,
    InternalObservation,
    Playbook,
    PlaybookBullet,
)


@pytest.fixture
def mock_config():
    """Mock ACE config."""
    config = Mock()
    config.trace_dir = Path("/tmp/traces")
    config.delta_dir = Path("/tmp/deltas")
    config.playbook_dir = Path("/tmp/playbooks")
    return config


@pytest.fixture
def sample_trace():
    """Sample execution trace."""
    return ExecutionTrace(
        trace_id="trace_123",
        timestamp=datetime.now(),
        agent_identity={
            "target_agent": "user_interpret",
            "agent_objective": "Test objective",
            "success_criteria": "Test criteria",
        },
        user_query="Test query",
        current_context="Test context",
        executions=[
            Execution(
                execution_id=1,
                external_observation=ExternalObservation(),
                internal_observation=InternalObservation(),
                result_status="success",
                duration_seconds=1.5,
                token_usage=100,
            )
        ],
    )


@pytest.fixture
def sample_playbook():
    """Sample playbook."""
    return Playbook(
        playbook_version="1.0",
        agent_name="user_interpret",
        agent_objective="Test objective",
        success_criteria="Test criteria",
        last_updated=datetime.now(),
        total_bullets=5,
        effectiveness_score=0.85,
        categories={
            "category1": [
                PlaybookBullet(
                    bullet_id="bullet_1",
                    type="success_pattern",
                    content="Test bullet",
                    helpful_count=10,
                    confidence=0.9,
                    priority=5,
                )
            ]
        },
    )


class TestACEApi:
    """Tests for ACEApi class."""

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_init(self, mock_env_manager, mock_trace_manager, mock_config):
        """Test API initialization."""
        api = ACEApi(config=mock_config)
        assert api.config == mock_config
        mock_trace_manager.assert_called_once_with(mock_config.trace_dir)

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    @patch("coffee_maker.autonomous.ace.api.PlaybookLoader")
    def test_get_agent_status(
        self,
        mock_playbook_loader,
        mock_env_manager,
        mock_trace_manager,
        mock_config,
        sample_playbook,
    ):
        """Test getting agent status."""
        # Mock dependencies
        api = ACEApi(config=mock_config)

        # Mock env manager
        api.env_manager.get_agent_ace_status = Mock(return_value=True)

        # Mock trace manager
        api.trace_manager.list_traces = Mock(return_value=[])

        # Mock playbook loader
        mock_loader_instance = Mock()
        mock_loader_instance.load = Mock(return_value=sample_playbook)
        mock_playbook_loader.return_value = mock_loader_instance

        # Get status
        statuses = api.get_agent_status()

        # Verify
        assert isinstance(statuses, dict)
        assert "user_interpret" in statuses
        assert statuses["user_interpret"]["ace_enabled"] is True
        assert statuses["user_interpret"]["playbook_size"] == 5

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_enable_agent(self, mock_env_manager, mock_trace_manager, mock_config):
        """Test enabling ACE for an agent."""
        api = ACEApi(config=mock_config)
        api.env_manager.set_agent_ace_status = Mock(return_value=True)

        result = api.enable_agent("user_interpret")

        assert result is True
        api.env_manager.set_agent_ace_status.assert_called_once_with("user_interpret", True)

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_disable_agent(self, mock_env_manager, mock_trace_manager, mock_config):
        """Test disabling ACE for an agent."""
        api = ACEApi(config=mock_config)
        api.env_manager.set_agent_ace_status = Mock(return_value=True)

        result = api.disable_agent("user_interpret")

        assert result is True
        api.env_manager.set_agent_ace_status.assert_called_once_with("user_interpret", False)

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_get_traces(self, mock_env_manager, mock_trace_manager, mock_config, sample_trace):
        """Test getting traces."""
        api = ACEApi(config=mock_config)
        api.trace_manager.list_traces = Mock(return_value=[sample_trace])

        traces = api.get_traces(agent="user_interpret")

        assert isinstance(traces, list)
        assert len(traces) == 1
        assert traces[0]["trace_id"] == "trace_123"
        api.trace_manager.list_traces.assert_called_once_with(agent="user_interpret")

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_get_traces_with_hours_filter(self, mock_env_manager, mock_trace_manager, mock_config, sample_trace):
        """Test getting traces with hours filter."""
        api = ACEApi(config=mock_config)
        api.trace_manager.get_traces_since = Mock(return_value=[sample_trace])

        traces = api.get_traces(hours=24)

        assert isinstance(traces, list)
        assert len(traces) == 1
        api.trace_manager.get_traces_since.assert_called_once_with(hours=24, agent=None)

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_get_trace_by_id(self, mock_env_manager, mock_trace_manager, mock_config, sample_trace):
        """Test getting trace by ID."""
        api = ACEApi(config=mock_config)
        api.trace_manager.read_trace = Mock(return_value=sample_trace)

        trace = api.get_trace_by_id("trace_123")

        assert trace is not None
        assert trace["trace_id"] == "trace_123"
        api.trace_manager.read_trace.assert_called_once_with("trace_123", date=None)

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_get_trace_by_id_not_found(self, mock_env_manager, mock_trace_manager, mock_config):
        """Test getting non-existent trace."""
        api = ACEApi(config=mock_config)
        api.trace_manager.read_trace = Mock(side_effect=FileNotFoundError("Not found"))

        trace = api.get_trace_by_id("trace_999")

        assert trace is None

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    @patch("coffee_maker.autonomous.ace.api.PlaybookLoader")
    def test_get_playbook(
        self,
        mock_playbook_loader,
        mock_env_manager,
        mock_trace_manager,
        mock_config,
        sample_playbook,
    ):
        """Test getting playbook."""
        api = ACEApi(config=mock_config)

        # Mock playbook loader
        mock_loader_instance = Mock()
        mock_loader_instance.load = Mock(return_value=sample_playbook)
        mock_playbook_loader.return_value = mock_loader_instance

        playbook = api.get_playbook("user_interpret")

        assert playbook is not None
        assert playbook["agent_name"] == "user_interpret"
        assert playbook["total_bullets"] == 5

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_get_metrics(self, mock_env_manager, mock_trace_manager, mock_config, sample_trace):
        """Test getting metrics."""
        # Create multiple traces
        traces = [sample_trace] * 10

        api = ACEApi(config=mock_config)
        api.trace_manager.list_traces = Mock(return_value=traces)

        metrics = api.get_metrics(days=7)

        assert metrics["total_traces"] == 10
        assert metrics["success_count"] == 10
        assert metrics["failure_count"] == 0
        assert metrics["success_rate"] == 100.0
        assert "agent_metrics" in metrics
        assert "user_interpret" in metrics["agent_metrics"]

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_get_reflection_status(self, mock_env_manager, mock_trace_manager, mock_config, tmp_path):
        """Test getting reflection status."""
        # Create temp delta directory with file
        delta_dir = tmp_path / "deltas"
        delta_dir.mkdir()

        delta_file = delta_dir / "delta_123.json"
        delta_file.write_text(json.dumps({"deltas": [{"delta_id": "1"}, {"delta_id": "2"}]}))

        # Update config
        mock_config.delta_dir = delta_dir

        api = ACEApi(config=mock_config)
        api.trace_manager.list_traces = Mock(return_value=[])

        status = api.get_reflection_status()

        assert "last_run" in status
        assert status["delta_items_generated"] == 2
        assert status["pending_traces"] == 0

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_is_success_all_success(self, mock_env_manager, mock_trace_manager, mock_config, sample_trace):
        """Test _is_success with all successful executions."""
        api = ACEApi(config=mock_config)
        assert api._is_success(sample_trace) is True

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_is_success_with_failure(self, mock_env_manager, mock_trace_manager, mock_config, sample_trace):
        """Test _is_success with failed execution."""
        sample_trace.executions[0].result_status = "failure"
        api = ACEApi(config=mock_config)
        assert api._is_success(sample_trace) is False

    @patch("coffee_maker.autonomous.ace.api.TraceManager")
    @patch("coffee_maker.autonomous.ace.api.EnvManager")
    def test_is_success_no_executions(self, mock_env_manager, mock_trace_manager, mock_config, sample_trace):
        """Test _is_success with no executions."""
        sample_trace.executions = []
        api = ACEApi(config=mock_config)
        assert api._is_success(sample_trace) is False
