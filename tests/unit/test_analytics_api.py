"""Unit tests for ACE analytics API methods.

Tests cost analytics, effectiveness analytics, performance analytics,
and executive summary generation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from coffee_maker.autonomous.ace.api import ACEApi
from coffee_maker.autonomous.ace.models import ExecutionTrace, Execution


@pytest.fixture
def mock_traces():
    """Create mock execution traces for testing."""
    traces = []
    base_time = datetime.now() - timedelta(days=15)

    # Create 20 mock traces across different agents
    agents = ["user_interpret", "assistant", "code_developer", "project_manager"]

    for i in range(20):
        agent = agents[i % len(agents)]
        success = i % 3 != 0  # 2/3 success rate

        trace = ExecutionTrace(
            trace_id=f"trace_{i:03d}",
            timestamp=base_time + timedelta(days=i % 30),
            agent_identity={"target_agent": agent},
            user_query=f"Test query {i}",
            executions=[
                Execution(
                    execution_id=f"exec_{i}_1",
                    prompt=f"Test prompt {i}" * 50,  # ~100 tokens
                    input_data={"test": "data"},
                    output=f"Test output {i}",
                    result_status="success" if success else "failure",
                    duration_seconds=5.0 + (i % 10),
                    metadata={"tokens": 100 + (i * 10)},
                )
            ],
        )
        traces.append(trace)

    return traces


@pytest.fixture
def api_with_mock_traces(mock_traces):
    """Create ACEApi instance with mocked trace manager."""
    api = ACEApi()
    api.trace_manager.list_traces = Mock(return_value=mock_traces)
    return api


def test_get_cost_analytics_basic(api_with_mock_traces):
    """Test basic cost analytics aggregation."""
    result = api_with_mock_traces.get_cost_analytics(days=30)

    assert "total_cost" in result
    assert "cost_by_agent" in result
    assert "cost_by_day" in result
    assert "avg_cost_per_trace" in result
    assert "most_expensive_agent" in result
    assert "trend" in result

    assert result["total_cost"] >= 0
    assert isinstance(result["cost_by_agent"], dict)
    assert isinstance(result["cost_by_day"], list)
    assert result["avg_cost_per_trace"] >= 0


def test_get_cost_analytics_by_agent(api_with_mock_traces):
    """Test cost analytics filtered by agent."""
    result = api_with_mock_traces.get_cost_analytics(agent="user_interpret", days=30)

    assert result["total_cost"] >= 0
    # Should only have one agent in breakdown when filtered
    if result["cost_by_agent"]:
        assert "user_interpret" in result["cost_by_agent"]


def test_get_cost_analytics_trend_calculation(api_with_mock_traces):
    """Test cost trend calculation logic."""
    result = api_with_mock_traces.get_cost_analytics(days=30)

    assert result["trend"] in ["increasing", "decreasing", "stable"]


def test_get_cost_analytics_empty_traces():
    """Test cost analytics with no traces."""
    api = ACEApi()
    api.trace_manager.list_traces = Mock(return_value=[])

    result = api.get_cost_analytics(days=30)

    assert result["total_cost"] == 0.0
    assert result["cost_by_agent"] == {}
    assert result["cost_by_day"] == []
    assert result["avg_cost_per_trace"] == 0.0
    assert result["most_expensive_agent"] == "N/A"


def test_get_effectiveness_analytics_basic(api_with_mock_traces):
    """Test basic effectiveness analytics."""
    result = api_with_mock_traces.get_effectiveness_analytics(days=30)

    assert "success_rate" in result
    assert "error_rate" in result
    assert "avg_effectiveness" in result
    assert "effectiveness_by_agent" in result
    assert "effectiveness_trend" in result
    assert "problem_areas" in result

    assert 0 <= result["success_rate"] <= 1
    assert 0 <= result["error_rate"] <= 1
    assert 0 <= result["avg_effectiveness"] <= 1
    assert isinstance(result["effectiveness_by_agent"], dict)
    assert isinstance(result["effectiveness_trend"], list)


def test_get_effectiveness_analytics_success_rate(api_with_mock_traces):
    """Test success rate calculation."""
    result = api_with_mock_traces.get_effectiveness_analytics(days=30)

    # With our mock data (2/3 success rate)
    assert result["success_rate"] > 0.5
    assert result["success_rate"] < 0.8
    assert abs(result["success_rate"] + result["error_rate"] - 1.0) < 0.01


def test_get_effectiveness_analytics_problem_areas(api_with_mock_traces):
    """Test problem area identification."""
    result = api_with_mock_traces.get_effectiveness_analytics(days=30)

    # Problem areas are agents with effectiveness < 0.7
    problem_areas = result.get("problem_areas", [])
    assert isinstance(problem_areas, list)


def test_get_effectiveness_analytics_by_agent(api_with_mock_traces):
    """Test effectiveness analytics filtered by agent."""
    result = api_with_mock_traces.get_effectiveness_analytics(agent="assistant", days=30)

    assert result["success_rate"] >= 0
    if result["effectiveness_by_agent"]:
        assert "assistant" in result["effectiveness_by_agent"]


def test_get_effectiveness_analytics_empty_traces():
    """Test effectiveness analytics with no traces."""
    api = ACEApi()
    api.trace_manager.list_traces = Mock(return_value=[])

    result = api.get_effectiveness_analytics(days=30)

    assert result["success_rate"] == 0.0
    assert result["error_rate"] == 0.0
    assert result["avg_effectiveness"] == 0.0
    assert result["effectiveness_by_agent"] == {}
    assert result["effectiveness_trend"] == []


def test_get_performance_analytics_basic(api_with_mock_traces):
    """Test basic performance analytics."""
    result = api_with_mock_traces.get_performance_analytics(days=30)

    assert "avg_duration" in result
    assert "avg_tokens" in result
    assert "duration_by_agent" in result
    assert "tokens_by_agent" in result
    assert "slowest_operations" in result
    assert "optimization_opportunities" in result

    assert result["avg_duration"] >= 0
    assert result["avg_tokens"] >= 0
    assert isinstance(result["duration_by_agent"], dict)
    assert isinstance(result["tokens_by_agent"], dict)
    assert isinstance(result["slowest_operations"], list)


def test_get_performance_analytics_averages(api_with_mock_traces):
    """Test average calculation in performance analytics."""
    result = api_with_mock_traces.get_performance_analytics(days=30)

    # With our mock data, duration should be between 5-15s
    assert 5 <= result["avg_duration"] <= 15
    assert result["avg_tokens"] >= 100


def test_get_performance_analytics_slowest_operations(api_with_mock_traces):
    """Test slowest operations tracking."""
    result = api_with_mock_traces.get_performance_analytics(days=30)

    slowest = result.get("slowest_operations", [])
    assert isinstance(slowest, list)
    assert len(slowest) <= 10  # Should limit to top 10

    # Each operation should have required fields
    for op in slowest:
        assert "agent" in op
        assert "task" in op
        assert "duration" in op
        assert "trace_id" in op


def test_get_performance_analytics_optimization_opportunities(api_with_mock_traces):
    """Test optimization opportunity generation."""
    result = api_with_mock_traces.get_performance_analytics(days=30)

    opportunities = result.get("optimization_opportunities", [])
    assert isinstance(opportunities, list)


def test_get_performance_analytics_empty_traces():
    """Test performance analytics with no traces."""
    api = ACEApi()
    api.trace_manager.list_traces = Mock(return_value=[])

    result = api.get_performance_analytics(days=30)

    assert result["avg_duration"] == 0.0
    assert result["avg_tokens"] == 0
    assert result["duration_by_agent"] == {}
    assert result["slowest_operations"] == []


def test_get_executive_summary_basic(api_with_mock_traces):
    """Test executive summary generation."""
    # Mock insights module
    with patch("coffee_maker.autonomous.ace.insights.generate_insights") as mock_insights:
        with patch("coffee_maker.autonomous.ace.insights.generate_recommendations") as mock_recs:
            mock_insights.return_value = ["Test insight 1", "Test insight 2"]
            mock_recs.return_value = ["Test recommendation 1"]

            result = api_with_mock_traces.get_executive_summary(days=30)

            assert "total_traces" in result
            assert "total_cost" in result
            assert "avg_effectiveness" in result
            assert "top_performing_agent" in result
            assert "biggest_cost_driver" in result
            assert "key_insights" in result
            assert "recommendations" in result

            assert result["total_traces"] >= 0
            assert result["total_cost"] >= 0
            assert isinstance(result["key_insights"], list)
            assert isinstance(result["recommendations"], list)


def test_get_executive_summary_top_performer(api_with_mock_traces):
    """Test top performing agent identification."""
    with patch("coffee_maker.autonomous.ace.insights.generate_insights") as mock_insights:
        with patch("coffee_maker.autonomous.ace.insights.generate_recommendations") as mock_recs:
            mock_insights.return_value = []
            mock_recs.return_value = []

            result = api_with_mock_traces.get_executive_summary(days=30)

            # Should identify an agent as top performer
            assert result["top_performing_agent"] != "N/A"


def test_get_executive_summary_empty_traces():
    """Test executive summary with no traces."""
    api = ACEApi()
    api.trace_manager.list_traces = Mock(return_value=[])

    with patch("coffee_maker.autonomous.ace.insights.generate_insights") as mock_insights:
        with patch("coffee_maker.autonomous.ace.insights.generate_recommendations") as mock_recs:
            mock_insights.return_value = []
            mock_recs.return_value = []

            result = api.get_executive_summary(days=30)

            assert result["total_traces"] == 0
            assert result["total_cost"] == 0.0
            assert result["top_performing_agent"] == "N/A"


def test_analytics_performance(api_with_mock_traces):
    """Test that analytics methods complete in reasonable time."""
    import time

    # Cost analytics should be fast
    start = time.time()
    api_with_mock_traces.get_cost_analytics(days=30)
    duration = time.time() - start
    assert duration < 1.0  # Should complete in <1s

    # Effectiveness analytics should be fast
    start = time.time()
    api_with_mock_traces.get_effectiveness_analytics(days=30)
    duration = time.time() - start
    assert duration < 1.0

    # Performance analytics should be fast
    start = time.time()
    api_with_mock_traces.get_performance_analytics(days=30)
    duration = time.time() - start
    assert duration < 1.0


def test_analytics_with_different_time_ranges(api_with_mock_traces):
    """Test analytics with various time ranges."""
    for days in [7, 30, 90]:
        cost = api_with_mock_traces.get_cost_analytics(days=days)
        effectiveness = api_with_mock_traces.get_effectiveness_analytics(days=days)
        performance = api_with_mock_traces.get_performance_analytics(days=days)

        # All should return valid data structures
        assert isinstance(cost, dict)
        assert isinstance(effectiveness, dict)
        assert isinstance(performance, dict)


def test_analytics_data_consistency(api_with_mock_traces):
    """Test that analytics data is consistent across methods."""
    cost = api_with_mock_traces.get_cost_analytics(days=30)
    effectiveness = api_with_mock_traces.get_effectiveness_analytics(days=30)
    performance = api_with_mock_traces.get_performance_analytics(days=30)

    # Agents should be consistent across analytics
    cost_agents = set(cost["cost_by_agent"].keys())
    eff_agents = set(effectiveness["effectiveness_by_agent"].keys())
    perf_agents = set(performance["duration_by_agent"].keys())

    # All should have overlapping agents
    assert cost_agents & eff_agents, "Cost and effectiveness should share agents"
    assert cost_agents & perf_agents, "Cost and performance should share agents"


def test_analytics_error_handling():
    """Test analytics error handling with corrupted data."""
    api = ACEApi()

    # Mock trace manager to raise exception
    api.trace_manager.list_traces = Mock(side_effect=Exception("Test error"))

    # Should not raise, but return default values
    cost = api.get_cost_analytics(days=30)
    assert cost["total_cost"] == 0.0

    effectiveness = api.get_effectiveness_analytics(days=30)
    assert effectiveness["success_rate"] == 0.0

    performance = api.get_performance_analytics(days=30)
    assert performance["avg_duration"] == 0.0
