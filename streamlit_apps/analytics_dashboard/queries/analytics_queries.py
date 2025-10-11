"""Core analytics queries for the dashboard.

This module provides query functions for retrieving and analyzing LLM metrics
from the Langfuse export database (SQLite or PostgreSQL).

All query functions return pandas DataFrames and are cached using Streamlit's
@st.cache_data decorator for optimal performance.

Example:
    >>> import streamlit as st
    >>> stats = get_quick_stats("llm_metrics.db")
    >>> st.metric("Total Cost", f"${stats['total_cost']:.2f}")
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_quick_stats(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, float]:
    """Get quick overview statistics.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        Dictionary with total_cost, total_tokens, total_requests, avg_latency

    Example:
        >>> stats = get_quick_stats("llm_metrics.db")
        >>> print(f"Total cost: ${stats['total_cost']:.2f}")
        Total cost: $42.50
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            COALESCE(SUM(total_cost), 0) as total_cost,
            COALESCE(SUM(total_tokens), 0) as total_tokens,
            COUNT(*) as total_requests,
            COALESCE(AVG(latency_ms), 0) as avg_latency
        FROM generations
        {where_clause}
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return {
        "total_cost": float(df.iloc[0]["total_cost"]),
        "total_tokens": int(df.iloc[0]["total_tokens"]),
        "total_requests": int(df.iloc[0]["total_requests"]),
        "avg_latency": float(df.iloc[0]["avg_latency"]),
    }


@st.cache_data(ttl=300)
def get_recent_generations(
    db_path: str, limit: int = 10, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get recent LLM generations.

    Args:
        db_path: Path to SQLite database
        limit: Number of recent generations to return
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: created_at, model, total_tokens, total_cost, latency_ms

    Example:
        >>> df = get_recent_generations("llm_metrics.db", limit=5)
        >>> print(df[["model", "total_cost"]])
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            created_at,
            model,
            total_tokens,
            total_cost,
            latency_ms,
            input_tokens,
            output_tokens
        FROM generations
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert created_at to datetime
    df["created_at"] = pd.to_datetime(df["created_at"])

    return df


@st.cache_data(ttl=300)
def get_cost_by_model(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """Get total cost breakdown by model.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: model, total_cost, request_count, avg_cost_per_request

    Example:
        >>> df = get_cost_by_model("llm_metrics.db")
        >>> print(df.sort_values("total_cost", ascending=False))
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            model,
            COALESCE(SUM(total_cost), 0) as total_cost,
            COUNT(*) as request_count,
            COALESCE(AVG(total_cost), 0) as avg_cost_per_request,
            COALESCE(SUM(total_tokens), 0) as total_tokens
        FROM generations
        {where_clause}
        GROUP BY model
        ORDER BY total_cost DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


@st.cache_data(ttl=300)
def get_daily_cost_trend(
    db_path: str, days: int = 30, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get daily cost trend over time.

    Args:
        db_path: Path to SQLite database
        days: Number of days to look back (ignored if date_range provided)
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: date, total_cost, request_count, total_tokens

    Example:
        >>> df = get_daily_cost_trend("llm_metrics.db", days=7)
        >>> print(df.tail())
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]
    else:
        cutoff_date = datetime.now() - timedelta(days=days)
        where_clause = "WHERE created_at >= ?"
        params = [cutoff_date]

    query = f"""
        SELECT
            DATE(created_at) as date,
            COALESCE(SUM(total_cost), 0) as total_cost,
            COUNT(*) as request_count,
            COALESCE(SUM(total_tokens), 0) as total_tokens
        FROM generations
        {where_clause}
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])

    return df


@st.cache_data(ttl=300)
def get_model_performance_comparison(
    db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get model performance comparison (latency, cost, token efficiency).

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: model, avg_latency_ms, median_latency_ms,
                                total_cost, cost_per_1k_tokens, request_count

    Example:
        >>> df = get_model_performance_comparison("llm_metrics.db")
        >>> print(df.sort_values("avg_latency_ms"))
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            model,
            COALESCE(AVG(latency_ms), 0) as avg_latency_ms,
            COALESCE(SUM(total_cost), 0) as total_cost,
            COALESCE(SUM(total_tokens), 0) as total_tokens,
            COUNT(*) as request_count,
            COALESCE(AVG(total_cost), 0) as avg_cost_per_request,
            CASE
                WHEN SUM(total_tokens) > 0 THEN (SUM(total_cost) * 1000.0 / SUM(total_tokens))
                ELSE 0
            END as cost_per_1k_tokens
        FROM generations
        {where_clause}
        GROUP BY model
        ORDER BY request_count DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


@st.cache_data(ttl=300)
def get_agent_analysis(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """Get cost and usage analysis by agent (extracted from trace metadata).

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: agent_name, total_cost, request_count, total_tokens

    Example:
        >>> df = get_agent_analysis("llm_metrics.db")
        >>> print(df.head())
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "AND g.created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    # Extract agent name from trace name or metadata
    query = f"""
        SELECT
            COALESCE(t.name, 'Unknown') as agent_name,
            COALESCE(SUM(g.total_cost), 0) as total_cost,
            COUNT(g.id) as request_count,
            COALESCE(SUM(g.total_tokens), 0) as total_tokens,
            COALESCE(AVG(g.latency_ms), 0) as avg_latency_ms
        FROM generations g
        LEFT JOIN traces t ON g.trace_id = t.id
        WHERE 1=1 {where_clause}
        GROUP BY t.name
        ORDER BY total_cost DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


@st.cache_data(ttl=300)
def parse_date_range(range_option: str) -> Tuple[datetime, datetime]:
    """Parse date range option into (start_date, end_date).

    Args:
        range_option: One of "Last 24 hours", "Last 7 days", "Last 30 days", "Last 90 days"

    Returns:
        Tuple of (start_date, end_date)

    Example:
        >>> start, end = parse_date_range("Last 7 days")
        >>> print(f"From {start} to {end}")
    """
    end_date = datetime.now()

    if range_option == "Last 24 hours":
        start_date = end_date - timedelta(hours=24)
    elif range_option == "Last 7 days":
        start_date = end_date - timedelta(days=7)
    elif range_option == "Last 30 days":
        start_date = end_date - timedelta(days=30)
    elif range_option == "Last 90 days":
        start_date = end_date - timedelta(days=90)
    else:
        # Default to last 30 days
        start_date = end_date - timedelta(days=30)

    return start_date, end_date


@st.cache_data(ttl=300)
def get_available_models(db_path: str) -> List[str]:
    """Get list of available models in the database.

    Args:
        db_path: Path to SQLite database

    Returns:
        List of model names

    Example:
        >>> models = get_available_models("llm_metrics.db")
        >>> print(models)
        ['openai/gpt-4o-mini', 'openai/gpt-4o', 'anthropic/claude-3-5-sonnet-20241022']
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT DISTINCT model
        FROM generations
        WHERE model IS NOT NULL
        ORDER BY model
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df["model"].tolist()


@st.cache_data(ttl=300)
def get_available_agents(db_path: str) -> List[str]:
    """Get list of available agents (from trace names).

    Args:
        db_path: Path to SQLite database

    Returns:
        List of agent names

    Example:
        >>> agents = get_available_agents("llm_metrics.db")
        >>> print(agents)
        ['code-developer', 'project-manager', 'coffee-maker']
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT DISTINCT name as agent_name
        FROM traces
        WHERE name IS NOT NULL
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df["agent_name"].tolist()


@st.cache_data(ttl=300)
def get_hourly_usage_pattern(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """Get hourly usage pattern for heatmap visualization.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: hour, day_of_week, request_count, total_cost

    Example:
        >>> df = get_hourly_usage_pattern("llm_metrics.db")
        >>> # Use for heatmap showing usage by hour and day of week
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            CAST(strftime('%H', created_at) AS INTEGER) as hour,
            CAST(strftime('%w', created_at) AS INTEGER) as day_of_week,
            COUNT(*) as request_count,
            COALESCE(SUM(total_cost), 0) as total_cost
        FROM generations
        {where_clause}
        GROUP BY hour, day_of_week
        ORDER BY day_of_week, hour
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


@st.cache_data(ttl=300)
def get_cost_by_day_and_model(
    db_path: str, days: int = 30, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get daily cost breakdown by model for stacked area chart.

    Args:
        db_path: Path to SQLite database
        days: Number of days to look back
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: date, model, total_cost, request_count

    Example:
        >>> df = get_cost_by_day_and_model("llm_metrics.db", days=7)
        >>> # Pivot for stacked area chart
        >>> pivot = df.pivot(index='date', columns='model', values='total_cost')
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]
    else:
        cutoff_date = datetime.now() - timedelta(days=days)
        where_clause = "WHERE created_at >= ?"
        params = [cutoff_date]

    query = f"""
        SELECT
            DATE(created_at) as date,
            model,
            COALESCE(SUM(total_cost), 0) as total_cost,
            COUNT(*) as request_count
        FROM generations
        {where_clause}
        GROUP BY DATE(created_at), model
        ORDER BY date ASC, model
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])

    return df


@st.cache_data(ttl=300)
def get_token_usage_breakdown(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """Get token usage breakdown (input vs output) by model.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: model, input_tokens, output_tokens, total_tokens

    Example:
        >>> df = get_token_usage_breakdown("llm_metrics.db")
        >>> # Use for stacked bar chart
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            model,
            COALESCE(SUM(input_tokens), 0) as input_tokens,
            COALESCE(SUM(output_tokens), 0) as output_tokens,
            COALESCE(SUM(total_tokens), 0) as total_tokens,
            COUNT(*) as request_count
        FROM generations
        {where_clause}
        GROUP BY model
        ORDER BY total_tokens DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df
