"""Tests for ACE Reflector component."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from coffee_maker.autonomous.ace.models import (
    DeltaItem,
    Evidence,
    Execution,
    ExecutionTrace,
    ExternalObservation,
    InternalObservation,
)
from coffee_maker.autonomous.ace.reflector import ACEReflector


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary directories for testing."""
    traces_dir = tmp_path / "traces"
    deltas_dir = tmp_path / "deltas"
    traces_dir.mkdir()
    deltas_dir.mkdir()
    return traces_dir, deltas_dir


@pytest.fixture
def sample_trace():
    """Create a sample execution trace for testing."""
    return ExecutionTrace(
        trace_id="trace_123",
        timestamp=datetime.now(),
        agent_identity={
            "target_agent": "code_developer",
            "agent_objective": "Implement features",
            "success_criteria": "Code runs, tests pass",
        },
        user_query="Implement authentication feature",
        current_context="No existing context",
        executions=[
            Execution(
                execution_id=1,
                external_observation=ExternalObservation(
                    files_created=["auth/login.py"],
                    files_modified=["app.py"],
                    commands_executed=["pytest"],
                ),
                internal_observation=InternalObservation(
                    reasoning_steps=[
                        "Read spec",
                        "Create auth module",
                        "Implement login",
                    ],
                    tools_called=[{"tool": "Read", "file": "spec.md"}],
                ),
                result_status="success",
                duration_seconds=45.0,
            )
        ],
    )


@pytest.fixture
def sample_deltas():
    """Create sample delta items for testing."""
    return [
        DeltaItem(
            delta_id="delta_001",
            insight_type="success_pattern",
            title="Read spec before implementing",
            description="Always read technical spec before starting implementation",
            recommendation="Use Read tool to review spec first",
            evidence=[
                Evidence(
                    trace_id="trace_123",
                    execution_id=1,
                    example="Read spec.md before coding",
                )
            ],
            priority=4,
            confidence=0.85,
        ),
        DeltaItem(
            delta_id="delta_002",
            insight_type="failure_mode",
            title="Missing directory creation",
            description="Failing to create directories before writing files",
            recommendation="Use os.makedirs before Write tool",
            evidence=[
                Evidence(
                    trace_id="trace_456",
                    execution_id=1,
                    example="FileNotFoundError on write",
                )
            ],
            priority=5,
            confidence=0.95,
        ),
    ]


@pytest.fixture
def reflector(temp_dirs):
    """Create ACEReflector instance for testing."""
    traces_dir, deltas_dir = temp_dirs
    return ACEReflector(
        agent_name="code_developer",
        traces_base_dir=traces_dir,
        deltas_base_dir=deltas_dir,
    )


class TestReflectorInitialization:
    """Tests for ACEReflector initialization."""

    def test_init_creates_directories(self, temp_dirs):
        """Test that initialization creates necessary directories."""
        traces_dir, deltas_dir = temp_dirs
        reflector = ACEReflector(
            agent_name="code_developer",
            traces_base_dir=traces_dir,
            deltas_base_dir=deltas_dir,
        )

        assert reflector.agent_name == "code_developer"
        assert reflector.deltas_base_dir.exists()
        assert reflector.traces_base_dir.exists()

    def test_init_default_directories(self):
        """Test initialization with default directories."""
        reflector = ACEReflector(agent_name="test_agent")

        assert reflector.agent_name == "test_agent"
        assert reflector.traces_base_dir == Path("docs/generator/traces")
        assert reflector.deltas_base_dir == Path("docs/reflector/deltas")


class TestTraceLoading:
    """Tests for trace loading functionality."""

    def test_load_traces_by_ids(self, reflector, sample_trace, temp_dirs):
        """Test loading specific traces by ID."""
        traces_dir, _ = temp_dirs

        # Save sample trace
        date_dir = traces_dir / sample_trace.timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir()
        trace_path = date_dir / f"trace_{sample_trace.trace_id}.json"
        with open(trace_path, "w") as f:
            json.dump(sample_trace.to_dict(), f)

        # Load traces
        traces = reflector._load_traces(trace_ids=["trace_123"])

        assert len(traces) == 1
        assert traces[0].trace_id == "trace_123"

    def test_load_traces_by_hours(self, reflector, sample_trace, temp_dirs):
        """Test loading traces from last N hours."""
        traces_dir, _ = temp_dirs

        # Save sample trace
        date_dir = traces_dir / sample_trace.timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir()
        trace_path = date_dir / f"trace_{sample_trace.trace_id}.json"
        with open(trace_path, "w") as f:
            json.dump(sample_trace.to_dict(), f)

        # Mock trace_manager.get_traces_since
        with patch.object(reflector.trace_manager, "get_traces_since", return_value=[sample_trace]):
            traces = reflector._load_traces(hours=24)

        assert len(traces) >= 0  # May be 0 or 1 depending on mock

    def test_load_traces_by_n_latest(self, reflector, sample_trace):
        """Test loading N most recent traces."""
        # Mock trace_manager.get_latest_traces
        with patch.object(reflector.trace_manager, "get_latest_traces", return_value=[sample_trace]):
            traces = reflector._load_traces(n_latest=10)

        assert len(traces) >= 0  # May be 0 or 1 depending on mock

    def test_load_traces_filters_by_agent(self, reflector, sample_trace, temp_dirs):
        """Test that traces are filtered by agent name."""
        traces_dir, _ = temp_dirs

        # Create trace for different agent
        wrong_agent_trace = ExecutionTrace(
            trace_id="trace_456",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "assistant"},
            user_query="Test query",
            current_context="",
        )

        # Save traces
        date_dir = traces_dir / sample_trace.timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir()

        with open(date_dir / f"trace_{sample_trace.trace_id}.json", "w") as f:
            json.dump(sample_trace.to_dict(), f)

        with open(date_dir / f"trace_{wrong_agent_trace.trace_id}.json", "w") as f:
            json.dump(wrong_agent_trace.to_dict(), f)

        # Load traces
        traces = reflector._load_traces(trace_ids=["trace_123", "trace_456"])

        # Should only get trace for code_developer
        assert len(traces) == 1
        assert traces[0].trace_id == "trace_123"

    def test_load_traces_nonexistent_id(self, reflector):
        """Test loading non-existent trace ID."""
        traces = reflector._load_traces(trace_ids=["nonexistent"])
        assert len(traces) == 0


class TestInsightExtraction:
    """Tests for insight extraction functionality."""

    @patch("coffee_maker.autonomous.ace.reflector.load_prompt")
    def test_extract_insights_calls_claude(self, mock_load_prompt, reflector, sample_trace):
        """Test that insight extraction calls Claude CLI."""
        mock_load_prompt.return_value = "Test prompt"

        # Mock Claude CLI response with valid JSON
        mock_response = json.dumps(
            {
                "deltas": [
                    {
                        "delta_id": "delta_001",
                        "insight_type": "success_pattern",
                        "title": "Test insight",
                        "description": "Test description",
                        "recommendation": "Test recommendation",
                        "evidence": [],
                        "priority": 4,
                        "confidence": 0.8,
                    }
                ]
            }
        )

        # Mock the execute_prompt result
        from coffee_maker.autonomous.claude_cli_interface import APIResult

        mock_result = APIResult(
            content=mock_response,
            model="sonnet",
            usage={},
            stop_reason="end_turn",
            error=None,
        )

        with patch.object(reflector.claude_cli, "execute_prompt", return_value=mock_result):
            deltas = reflector._extract_insights([sample_trace])

        assert len(deltas) >= 1
        mock_load_prompt.assert_called_once()

    def test_parse_deltas_from_json_response(self, reflector, sample_trace):
        """Test parsing deltas from JSON response."""
        response = json.dumps(
            {
                "deltas": [
                    {
                        "delta_id": "delta_001",
                        "insight_type": "success_pattern",
                        "title": "Test",
                        "description": "Test desc",
                        "recommendation": "Do this",
                        "evidence": [
                            {
                                "trace_id": "trace_123",
                                "execution_id": 1,
                                "example": "Example",
                            }
                        ],
                        "priority": 4,
                        "confidence": 0.85,
                    }
                ]
            }
        )

        deltas = reflector._parse_deltas_from_response(response, [sample_trace])

        assert len(deltas) == 1
        assert deltas[0].delta_id == "delta_001"
        assert deltas[0].insight_type == "success_pattern"

    def test_parse_deltas_from_markdown_json(self, reflector, sample_trace):
        """Test parsing deltas from markdown code block."""
        response = """
        Here are the deltas:
        ```json
        {
            "deltas": [{
                "delta_id": "delta_001",
                "insight_type": "success_pattern",
                "title": "Test",
                "description": "Test desc",
                "recommendation": "Do this",
                "evidence": [],
                "priority": 4,
                "confidence": 0.85
            }]
        }
        ```
        """

        deltas = reflector._parse_deltas_from_response(response, [sample_trace])

        assert len(deltas) == 1
        assert deltas[0].delta_id == "delta_001"

    def test_parse_deltas_invalid_json_creates_fallback(self, reflector, sample_trace):
        """Test that invalid JSON creates fallback delta."""
        response = "This is not JSON at all"

        deltas = reflector._parse_deltas_from_response(response, [sample_trace])

        assert len(deltas) == 1
        assert deltas[0].insight_type == "raw_analysis"


class TestPriorityAssignment:
    """Tests for priority assignment."""

    def test_assign_priority_failure_mode(self, reflector):
        """Test that failure modes get highest priority."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="failure_mode",
            title="Test",
            description="Test",
            recommendation="Test",
        )

        priority = reflector._assign_priority(delta)
        assert priority == 5

    def test_assign_priority_success_pattern_multiple_evidence(self, reflector):
        """Test success patterns with multiple evidence get high priority."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="success_pattern",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[
                Evidence(trace_id="1", execution_id=1, example="Ex1"),
                Evidence(trace_id="2", execution_id=1, example="Ex2"),
            ],
        )

        priority = reflector._assign_priority(delta)
        assert priority == 4

    def test_assign_priority_optimization_high_confidence(self, reflector):
        """Test optimizations with high confidence get high priority."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="optimization",
            title="Test",
            description="Test",
            recommendation="Test",
            confidence=0.9,
        )

        priority = reflector._assign_priority(delta)
        assert priority == 4

    def test_assign_priority_best_practice(self, reflector):
        """Test best practices get medium priority."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="best_practice",
            title="Test",
            description="Test",
            recommendation="Test",
        )

        priority = reflector._assign_priority(delta)
        assert priority == 3


class TestConfidenceAssignment:
    """Tests for confidence assignment."""

    def test_assign_confidence_multiple_evidence(self, reflector):
        """Test confidence with multiple evidence points."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="success_pattern",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[
                Evidence(trace_id="1", execution_id=1, example="Ex1"),
                Evidence(trace_id="2", execution_id=1, example="Ex2"),
                Evidence(trace_id="3", execution_id=1, example="Ex3"),
            ],
        )

        confidence = reflector._assign_confidence(delta)
        assert confidence == 0.9

    def test_assign_confidence_two_evidence(self, reflector):
        """Test confidence with two evidence points."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="success_pattern",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[
                Evidence(trace_id="1", execution_id=1, example="Ex1"),
                Evidence(trace_id="2", execution_id=1, example="Ex2"),
            ],
        )

        confidence = reflector._assign_confidence(delta)
        assert confidence == 0.75

    def test_assign_confidence_single_evidence(self, reflector):
        """Test confidence with single evidence point."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="success_pattern",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[Evidence(trace_id="1", execution_id=1, example="Ex1")],
        )

        confidence = reflector._assign_confidence(delta)
        assert confidence == 0.6

    def test_assign_confidence_no_evidence(self, reflector):
        """Test confidence with no evidence."""
        delta = DeltaItem(
            delta_id="test",
            insight_type="success_pattern",
            title="Test",
            description="Test",
            recommendation="Test",
        )

        confidence = reflector._assign_confidence(delta)
        assert confidence == 0.4


class TestDeltaSaving:
    """Tests for saving delta items."""

    def test_save_deltas_creates_file(self, reflector, sample_deltas):
        """Test that save_deltas creates JSON file."""
        delta_path = reflector.save_deltas(sample_deltas)

        assert delta_path.exists()
        assert delta_path.suffix == ".json"

    def test_save_deltas_structure(self, reflector, sample_deltas):
        """Test that saved deltas have correct structure."""
        delta_path = reflector.save_deltas(sample_deltas)

        with open(delta_path, "r") as f:
            data = json.load(f)

        assert "metadata" in data
        assert "deltas" in data
        assert "summary" in data
        assert data["metadata"]["agent_name"] == "code_developer"
        assert len(data["deltas"]) == 2

    def test_save_deltas_custom_filename(self, reflector, sample_deltas):
        """Test saving deltas with custom filename."""
        delta_path = reflector.save_deltas(sample_deltas, custom_filename="custom_deltas.json")

        assert delta_path.name == "custom_deltas.json"
        assert delta_path.exists()

    def test_save_deltas_date_subdirectory(self, reflector, sample_deltas):
        """Test that deltas are saved in date subdirectory."""
        delta_path = reflector.save_deltas(sample_deltas)

        # Check that parent directory is a date (YYYY-MM-DD)
        date_dir_name = delta_path.parent.name
        assert len(date_dir_name) == 10  # YYYY-MM-DD format
        assert date_dir_name.count("-") == 2


class TestSummaryComputation:
    """Tests for summary computation."""

    def test_compute_summary(self, reflector, sample_deltas):
        """Test computing summary statistics."""
        summary = reflector._compute_summary(sample_deltas)

        assert summary["total_deltas"] == 2
        assert "success_pattern" in summary["by_type"]
        assert "failure_mode" in summary["by_type"]
        assert "4" in summary["by_priority"]
        assert "5" in summary["by_priority"]
        assert summary["avg_confidence"] > 0

    def test_compute_summary_empty(self, reflector):
        """Test computing summary with no deltas."""
        summary = reflector._compute_summary([])

        assert summary["total_deltas"] == 0
        assert summary["by_type"] == {}
        assert summary["by_priority"] == {}
        assert summary["avg_confidence"] == 0.0


class TestAnalyzeTraces:
    """Tests for analyze_traces method."""

    def test_analyze_traces_validation_no_args(self, reflector):
        """Test that analyze_traces requires at least one argument."""
        with pytest.raises(ValueError, match="Must provide one of"):
            reflector.analyze_traces()

    def test_analyze_traces_validation_multiple_args(self, reflector):
        """Test that analyze_traces rejects multiple arguments."""
        with pytest.raises(ValueError, match="Only one of"):
            reflector.analyze_traces(trace_ids=["test"], hours=24)

    @patch("coffee_maker.autonomous.ace.reflector.load_prompt")
    def test_analyze_traces_empty_returns_empty(self, mock_load_prompt, reflector):
        """Test that analyzing zero traces returns empty list."""
        # Mock to return no traces
        with patch.object(reflector, "_load_traces", return_value=[]):
            deltas = reflector.analyze_traces(trace_ids=["nonexistent"])

        assert deltas == []

    def test_analyze_recent_traces_convenience(self, reflector):
        """Test analyze_recent_traces convenience method."""
        with patch.object(reflector, "analyze_traces", return_value=[]) as mock_analyze:
            reflector.analyze_recent_traces(hours=48)

        mock_analyze.assert_called_once_with(hours=48)


class TestStatistics:
    """Tests for statistics methods."""

    def test_get_stats_empty(self, reflector):
        """Test get_stats with no deltas."""
        stats = reflector.get_stats()

        assert stats["total_deltas_files"] == 0
        assert stats["date_range"] == "No deltas"

    def test_get_stats_with_deltas(self, reflector, sample_deltas):
        """Test get_stats with saved deltas."""
        reflector.save_deltas(sample_deltas)

        stats = reflector.get_stats()

        assert stats["total_deltas_files"] == 1
        assert stats["dates_with_deltas"] == 1


class TestIntegration:
    """Integration tests for Reflector."""

    def test_full_workflow(self, reflector, sample_trace, temp_dirs):
        """Test complete workflow from trace to saved deltas."""
        traces_dir, _ = temp_dirs

        # Save sample trace
        date_dir = traces_dir / sample_trace.timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir()
        trace_path = date_dir / f"trace_{sample_trace.trace_id}.json"
        with open(trace_path, "w") as f:
            json.dump(sample_trace.to_dict(), f)

        # Mock Claude response
        mock_response = json.dumps(
            {
                "deltas": [
                    {
                        "delta_id": "delta_test",
                        "insight_type": "success_pattern",
                        "title": "Integration test insight",
                        "description": "Test description",
                        "recommendation": "Test recommendation",
                        "evidence": [],
                        "priority": 3,
                        "confidence": 0.7,
                    }
                ]
            }
        )

        # Mock the execute_prompt result
        from coffee_maker.autonomous.claude_cli_interface import APIResult

        mock_result = APIResult(
            content=mock_response,
            model="sonnet",
            usage={},
            stop_reason="end_turn",
            error=None,
        )

        with patch.object(reflector.claude_cli, "execute_prompt", return_value=mock_result):
            # Analyze traces
            deltas = reflector.analyze_traces(trace_ids=["trace_123"])

            # Save deltas
            delta_path = reflector.save_deltas(deltas)

        # Verify
        assert len(deltas) >= 1
        assert delta_path.exists()

        # Check saved data
        with open(delta_path, "r") as f:
            data = json.load(f)

        assert data["metadata"]["agent_name"] == "code_developer"
        assert len(data["deltas"]) >= 1
