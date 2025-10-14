"""Tests for TraceManager."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.autonomous.ace.models import (
    ExecutionTrace,
)
from coffee_maker.autonomous.ace.trace_manager import TraceManager


@pytest.fixture
def temp_trace_dir():
    """Create temporary directory for traces."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_trace():
    """Create sample execution trace."""
    return ExecutionTrace(
        trace_id="test_trace_123",
        timestamp=datetime.now(),
        agent_identity={
            "target_agent": "code_developer",
            "agent_objective": "Test",
            "success_criteria": "Pass",
        },
        user_query="Test query",
        current_context="# Test context",
        executions=[],
        helpful_context_elements=[],
        problematic_context_elements=[],
        new_insights_surfaced=[],
    )


class TestTraceManager:
    """Tests for TraceManager class."""

    def test_init_creates_directory(self, temp_trace_dir):
        """Test that initialization creates base directory."""
        TraceManager(temp_trace_dir / "traces")
        assert (temp_trace_dir / "traces").exists()

    def test_write_trace(self, temp_trace_dir, sample_trace):
        """Test writing trace to file."""
        manager = TraceManager(temp_trace_dir)
        trace_path = manager.write_trace(sample_trace)

        assert trace_path.exists()
        assert trace_path.suffix == ".json"
        assert "test_trace_123" in trace_path.name

    def test_write_trace_creates_date_directory(self, temp_trace_dir, sample_trace):
        """Test that writing trace creates date-based directory."""
        manager = TraceManager(temp_trace_dir)
        trace_path = manager.write_trace(sample_trace)

        date_str = sample_trace.timestamp.strftime("%Y-%m-%d")
        assert (temp_trace_dir / date_str).exists()
        assert trace_path.parent.name == date_str

    def test_write_trace_creates_markdown(self, temp_trace_dir, sample_trace):
        """Test that markdown file is also created."""
        manager = TraceManager(temp_trace_dir)
        trace_path = manager.write_trace(sample_trace)

        md_path = trace_path.with_suffix(".md")
        assert md_path.exists()

    def test_read_trace(self, temp_trace_dir, sample_trace):
        """Test reading trace by ID."""
        manager = TraceManager(temp_trace_dir)
        manager.write_trace(sample_trace)

        loaded_trace = manager.read_trace("test_trace_123")
        assert loaded_trace.trace_id == sample_trace.trace_id
        assert loaded_trace.user_query == sample_trace.user_query

    def test_read_trace_with_date(self, temp_trace_dir, sample_trace):
        """Test reading trace with specific date."""
        manager = TraceManager(temp_trace_dir)
        manager.write_trace(sample_trace)

        date_str = sample_trace.timestamp.strftime("%Y-%m-%d")
        loaded_trace = manager.read_trace("test_trace_123", date=date_str)
        assert loaded_trace.trace_id == "test_trace_123"

    def test_read_nonexistent_trace(self, temp_trace_dir):
        """Test reading nonexistent trace raises error."""
        manager = TraceManager(temp_trace_dir)

        with pytest.raises(FileNotFoundError):
            manager.read_trace("nonexistent")

    def test_list_traces_empty(self, temp_trace_dir):
        """Test listing traces when none exist."""
        manager = TraceManager(temp_trace_dir)
        traces = manager.list_traces()
        assert traces == []

    def test_list_traces(self, temp_trace_dir):
        """Test listing all traces."""
        manager = TraceManager(temp_trace_dir)

        # Create multiple traces
        trace1 = ExecutionTrace(
            trace_id="trace_1",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Query 1",
            current_context="",
        )
        trace2 = ExecutionTrace(
            trace_id="trace_2",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Query 2",
            current_context="",
        )

        manager.write_trace(trace1)
        manager.write_trace(trace2)

        traces = manager.list_traces()
        assert len(traces) == 2

    def test_list_traces_by_date(self, temp_trace_dir, sample_trace):
        """Test listing traces filtered by date."""
        manager = TraceManager(temp_trace_dir)
        manager.write_trace(sample_trace)

        date_str = sample_trace.timestamp.strftime("%Y-%m-%d")
        traces = manager.list_traces(date=date_str)
        assert len(traces) == 1

    def test_list_traces_by_agent(self, temp_trace_dir):
        """Test listing traces filtered by agent."""
        manager = TraceManager(temp_trace_dir)

        trace1 = ExecutionTrace(
            trace_id="trace_1",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Query 1",
            current_context="",
        )
        trace2 = ExecutionTrace(
            trace_id="trace_2",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "assistant"},
            user_query="Query 2",
            current_context="",
        )

        manager.write_trace(trace1)
        manager.write_trace(trace2)

        traces = manager.list_traces(agent="code_developer")
        assert len(traces) == 1
        assert traces[0].agent_identity["target_agent"] == "code_developer"

    def test_get_latest_traces(self, temp_trace_dir):
        """Test getting N most recent traces."""
        manager = TraceManager(temp_trace_dir)

        # Create 5 traces
        for i in range(5):
            trace = ExecutionTrace(
                trace_id=f"trace_{i}",
                timestamp=datetime.now() + timedelta(seconds=i),
                agent_identity={"target_agent": "test"},
                user_query=f"Query {i}",
                current_context="",
            )
            manager.write_trace(trace)

        latest = manager.get_latest_traces(n=3)
        assert len(latest) == 3
        # Should be in descending order
        assert latest[0].trace_id == "trace_4"

    def test_get_traces_since(self, temp_trace_dir):
        """Test getting traces from last N hours."""
        manager = TraceManager(temp_trace_dir)

        # Create old trace
        old_trace = ExecutionTrace(
            trace_id="old_trace",
            timestamp=datetime.now() - timedelta(hours=48),
            agent_identity={"target_agent": "test"},
            user_query="Old query",
            current_context="",
        )

        # Create recent trace
        recent_trace = ExecutionTrace(
            trace_id="recent_trace",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "test"},
            user_query="Recent query",
            current_context="",
        )

        manager.write_trace(old_trace)
        manager.write_trace(recent_trace)

        # Get traces from last 24 hours
        recent_traces = manager.get_traces_since(hours=24)
        assert len(recent_traces) == 1
        assert recent_traces[0].trace_id == "recent_trace"

    def test_delete_old_traces(self, temp_trace_dir):
        """Test deleting traces older than N days."""
        manager = TraceManager(temp_trace_dir)

        # Create old trace (100 days ago)
        old_trace = ExecutionTrace(
            trace_id="old_trace",
            timestamp=datetime.now() - timedelta(days=100),
            agent_identity={"target_agent": "test"},
            user_query="Old",
            current_context="",
        )

        # Create recent trace
        recent_trace = ExecutionTrace(
            trace_id="recent_trace",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "test"},
            user_query="Recent",
            current_context="",
        )

        manager.write_trace(old_trace)
        manager.write_trace(recent_trace)

        # Delete traces older than 90 days
        manager.delete_old_traces(days=90)

        # Check that old trace is gone
        with pytest.raises(FileNotFoundError):
            manager.read_trace("old_trace")

        # Check that recent trace still exists
        loaded = manager.read_trace("recent_trace")
        assert loaded.trace_id == "recent_trace"

    def test_get_stats(self, temp_trace_dir):
        """Test getting trace statistics."""
        manager = TraceManager(temp_trace_dir)

        # Create some traces
        for i in range(3):
            trace = ExecutionTrace(
                trace_id=f"trace_{i}",
                timestamp=datetime.now(),
                agent_identity={"target_agent": "test"},
                user_query=f"Query {i}",
                current_context="",
            )
            manager.write_trace(trace)

        stats = manager.get_stats()
        assert stats["total_traces"] == 3
        assert "total_size_mb" in stats
        assert "date_range" in stats

    def test_get_stats_empty(self, temp_trace_dir):
        """Test getting stats with no traces."""
        manager = TraceManager(temp_trace_dir)
        stats = manager.get_stats()
        assert stats["total_traces"] == 0
