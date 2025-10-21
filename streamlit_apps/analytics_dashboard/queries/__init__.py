"""
Query modules for Analytics Dashboard.

This package provides query functions for analyzing LLM metrics from SQLite database.
"""

from .cost_queries import get_hourly_cost_breakdown, get_budget_tracking, get_cost_forecast, get_most_expensive_requests

from .performance_queries import (
    get_latency_percentiles,
    get_hourly_usage_heatmap,
    get_error_rate_by_model,
    get_token_efficiency_by_model,
    get_throughput_over_time,
)

__all__ = [
    # Cost queries
    "get_hourly_cost_breakdown",
    "get_budget_tracking",
    "get_cost_forecast",
    "get_most_expensive_requests",
    # Performance queries
    "get_latency_percentiles",
    "get_hourly_usage_heatmap",
    "get_error_rate_by_model",
    "get_token_efficiency_by_model",
    "get_throughput_over_time",
]
