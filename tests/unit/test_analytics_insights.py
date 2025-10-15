"""Unit tests for ACE insights generation engine."""

import pytest
from coffee_maker.autonomous.ace.insights import (
    generate_insights,
    generate_recommendations,
    categorize_insights,
    prioritize_recommendations,
)


@pytest.fixture
def sample_cost_data():
    """Sample cost analytics data."""
    return {
        "total_cost": 127.45,
        "cost_by_agent": {
            "user_interpret": 45.20,
            "code_developer": 60.15,
            "assistant": 22.10,
        },
        "cost_by_day": [
            {"date": "2025-01-01", "cost": 5.0},
            {"date": "2025-01-02", "cost": 6.5},
        ],
        "avg_cost_per_trace": 0.0045,
        "most_expensive_agent": "code_developer",
        "trend": "increasing",
    }


@pytest.fixture
def sample_effectiveness_data():
    """Sample effectiveness analytics data."""
    return {
        "success_rate": 0.75,
        "error_rate": 0.25,
        "avg_effectiveness": 0.75,
        "effectiveness_by_agent": {
            "user_interpret": 0.85,
            "code_developer": 0.65,
            "assistant": 0.95,
        },
        "effectiveness_trend": [
            {"date": "2025-01-01", "effectiveness": 0.8},
            {"date": "2025-01-02", "effectiveness": 0.7},
        ],
        "problem_areas": ["code_developer (65%)"],
    }


@pytest.fixture
def sample_performance_data():
    """Sample performance analytics data."""
    return {
        "avg_duration": 12.5,
        "avg_tokens": 2500,
        "duration_by_agent": {
            "user_interpret": 8.0,
            "code_developer": 25.0,
            "assistant": 5.0,
        },
        "tokens_by_agent": {
            "user_interpret": 2000,
            "code_developer": 4000,
            "assistant": 1500,
        },
        "slowest_operations": [
            {"agent": "code_developer", "task": "Implement feature", "duration": 45.0},
        ],
        "optimization_opportunities": ["Optimize code_developer: 25.0s avg (system avg: 12.5s)"],
    }


def test_generate_insights_cost_increasing(sample_cost_data, sample_effectiveness_data, sample_performance_data):
    """Test insight generation for increasing costs."""
    insights = generate_insights(sample_cost_data, sample_effectiveness_data, sample_performance_data)

    assert isinstance(insights, list)
    assert len(insights) > 0

    # Should mention cost increase
    cost_insights = [i for i in insights if "cost" in i.lower() and "increasing" in i.lower()]
    assert len(cost_insights) > 0


def test_generate_insights_low_success_rate(sample_cost_data, sample_effectiveness_data, sample_performance_data):
    """Test insight generation for low success rate."""
    insights = generate_insights(sample_cost_data, sample_effectiveness_data, sample_performance_data)

    # Should mention success rate issue
    success_insights = [i for i in insights if "success rate" in i.lower()]
    assert len(success_insights) > 0


def test_generate_insights_problem_areas(sample_cost_data, sample_effectiveness_data, sample_performance_data):
    """Test insight generation for problem areas."""
    insights = generate_insights(sample_cost_data, sample_effectiveness_data, sample_performance_data)

    # Should mention problem areas
    problem_insights = [i for i in insights if "problem areas" in i.lower()]
    assert len(problem_insights) > 0


def test_generate_insights_slow_agents(sample_cost_data, sample_effectiveness_data, sample_performance_data):
    """Test insight generation for slow agents."""
    insights = generate_insights(sample_cost_data, sample_effectiveness_data, sample_performance_data)

    # Should mention slow agents
    slow_insights = [i for i in insights if "slower than average" in i.lower()]
    assert len(slow_insights) > 0


def test_generate_insights_cost_concentration(sample_cost_data, sample_effectiveness_data, sample_performance_data):
    """Test insight generation for cost concentration."""
    insights = generate_insights(sample_cost_data, sample_effectiveness_data, sample_performance_data)

    # Should mention cost concentration if one agent dominates
    concentration_insights = [i for i in insights if "accounts for" in i.lower()]
    assert len(concentration_insights) > 0


def test_generate_insights_empty_data():
    """Test insight generation with minimal data."""
    empty_cost = {
        "total_cost": 0.0,
        "cost_by_agent": {},
        "cost_by_day": [],
        "avg_cost_per_trace": 0.0,
        "most_expensive_agent": "N/A",
        "trend": "stable",
    }
    empty_eff = {
        "success_rate": 0.0,
        "error_rate": 0.0,
        "avg_effectiveness": 0.0,
        "effectiveness_by_agent": {},
        "effectiveness_trend": [],
        "problem_areas": [],
    }
    empty_perf = {
        "avg_duration": 0.0,
        "avg_tokens": 0,
        "duration_by_agent": {},
        "tokens_by_agent": {},
        "slowest_operations": [],
        "optimization_opportunities": [],
    }

    insights = generate_insights(empty_cost, empty_eff, empty_perf)

    assert isinstance(insights, list)
    # Should have at least one default insight
    assert len(insights) > 0


def test_generate_insights_excellent_performance():
    """Test insight generation with excellent metrics."""
    excellent_cost = {
        "total_cost": 5.0,
        "cost_by_agent": {"agent1": 5.0},
        "cost_by_day": [],
        "avg_cost_per_trace": 0.001,
        "most_expensive_agent": "agent1",
        "trend": "decreasing",
    }
    excellent_eff = {
        "success_rate": 0.98,
        "error_rate": 0.02,
        "avg_effectiveness": 0.98,
        "effectiveness_by_agent": {"agent1": 0.98},
        "effectiveness_trend": [],
        "problem_areas": [],
    }
    excellent_perf = {
        "avg_duration": 3.0,
        "avg_tokens": 500,
        "duration_by_agent": {"agent1": 3.0},
        "tokens_by_agent": {"agent1": 500},
        "slowest_operations": [],
        "optimization_opportunities": [],
    }

    insights = generate_insights(excellent_cost, excellent_eff, excellent_perf)

    # Should have positive insights
    positive_keywords = ["excellent", "decreasing", "good", "well"]
    positive_insights = [i for i in insights if any(kw in i.lower() for kw in positive_keywords)]
    assert len(positive_insights) > 0


def test_generate_recommendations_from_insights():
    """Test recommendation generation from insights."""
    insights = [
        "Cost is increasing. Consider optimizing code_developer",
        "Success rate is 75%, below target",
        "Agents code_developer are significantly slower than average",
        "High token usage detected (10000 tokens/trace)",
    ]

    recommendations = generate_recommendations(insights)

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    # Should generate relevant recommendations
    rec_text = " ".join(recommendations).lower()
    assert "optimi" in rec_text or "improv" in rec_text


def test_generate_recommendations_cost_related():
    """Test cost-related recommendations."""
    insights = ["Cost is increasing. Consider optimizing expensive agents"]

    recommendations = generate_recommendations(insights)

    rec_text = " ".join(recommendations).lower()
    assert "cost" in rec_text or "cach" in rec_text or "optimi" in rec_text


def test_generate_recommendations_effectiveness_related():
    """Test effectiveness-related recommendations."""
    insights = ["Success rate is 65%, below target"]

    recommendations = generate_recommendations(insights)

    rec_text = " ".join(recommendations).lower()
    assert "error" in rec_text or "retry" in rec_text or "validat" in rec_text


def test_generate_recommendations_performance_related():
    """Test performance-related recommendations."""
    insights = ["Agents code_developer are significantly slower than average"]

    recommendations = generate_recommendations(insights)

    rec_text = " ".join(recommendations).lower()
    assert "slow" in rec_text or "optimi" in rec_text or "bottleneck" in rec_text


def test_generate_recommendations_empty_insights():
    """Test recommendation generation with no insights."""
    insights = []

    recommendations = generate_recommendations(insights)

    assert isinstance(recommendations, list)
    # Should have at least some default recommendations
    assert len(recommendations) > 0


def test_generate_recommendations_limit():
    """Test that recommendations are limited to reasonable number."""
    insights = [
        "Cost increasing",
        "Success rate low",
        "Performance slow",
        "Token usage high",
        "Error rate high",
        "Problem areas detected",
    ]

    recommendations = generate_recommendations(insights)

    # Should not return too many recommendations
    assert len(recommendations) <= 8


def test_categorize_insights():
    """Test insight categorization."""
    insights = [
        "Cost is increasing by 20%",
        "Success rate is 85%",
        "Average duration is 15 seconds",
        "System is operating normally",
    ]

    categorized = categorize_insights(insights)

    assert isinstance(categorized, dict)
    assert "cost" in categorized
    assert "effectiveness" in categorized
    assert "performance" in categorized

    # Check correct categorization
    assert len(categorized["cost"]) > 0
    assert len(categorized["effectiveness"]) > 0
    assert len(categorized["performance"]) > 0


def test_categorize_insights_empty():
    """Test categorization with empty insights."""
    insights = []

    categorized = categorize_insights(insights)

    assert isinstance(categorized, dict)
    # Should return empty dict for empty insights
    assert len(categorized) == 0


def test_categorize_insights_mixed():
    """Test categorization with mixed insights."""
    insights = [
        "Cost and effectiveness are both improving",
        "Performance metrics show optimization needed",
    ]

    categorized = categorize_insights(insights)

    # First insight should be in both cost and effectiveness
    # (categorization picks first matching keyword)
    assert isinstance(categorized, dict)


def test_prioritize_recommendations():
    """Test recommendation prioritization."""
    recommendations = [
        "Implement error handling and retry logic",  # High priority
        "Consider optimizing slow operations",  # Medium priority
        "Continue monitoring trends",  # Low priority
        "Review failed traces",  # High priority
    ]

    prioritized = prioritize_recommendations(recommendations)

    assert isinstance(prioritized, list)
    assert len(prioritized) == len(recommendations)

    # Each item should have required fields
    for item in prioritized:
        assert "text" in item
        assert "priority" in item
        assert "score" in item
        assert item["priority"] in ["high", "medium", "low"]
        assert isinstance(item["score"], int)

    # Should be sorted by score (descending)
    scores = [item["score"] for item in prioritized]
    assert scores == sorted(scores, reverse=True)


def test_prioritize_recommendations_high_priority():
    """Test that high-priority keywords are detected."""
    recommendations = ["Critical error handling needed", "Significant failure rate"]

    prioritized = prioritize_recommendations(recommendations)

    # Both should be high priority
    high_priority_count = sum(1 for item in prioritized if item["priority"] == "high")
    assert high_priority_count == 2


def test_prioritize_recommendations_medium_priority():
    """Test that medium-priority keywords are detected."""
    recommendations = ["Optimize performance", "Consider improving efficiency"]

    prioritized = prioritize_recommendations(recommendations)

    # Should be medium priority
    medium_priority_count = sum(1 for item in prioritized if item["priority"] == "medium")
    assert medium_priority_count >= 1


def test_prioritize_recommendations_low_priority():
    """Test that low-priority keywords are detected."""
    recommendations = ["Continue monitoring", "Document best practices"]

    prioritized = prioritize_recommendations(recommendations)

    # Should be low priority
    low_priority_count = sum(1 for item in prioritized if item["priority"] == "low")
    assert low_priority_count >= 1


def test_prioritize_recommendations_empty():
    """Test prioritization with empty list."""
    recommendations = []

    prioritized = prioritize_recommendations(recommendations)

    assert isinstance(prioritized, list)
    assert len(prioritized) == 0
