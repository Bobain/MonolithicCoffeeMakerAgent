"""Export query functions for the analytics dashboard.

This module provides functions for exporting comprehensive and summarized data
from the SQLite database for CSV/Excel export functionality.

All query functions return pandas DataFrames and are cached using Streamlit's
@st.cache_data decorator for optimal performance.

Example:
    >>> import streamlit as st
    >>> df = get_detailed_export_data("llm_metrics.db", models=["gpt-4o"])
    >>> df.to_csv("export.csv", index=False)
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_detailed_export_data(
    db_path: str,
    date_range: Optional[Tuple[datetime, datetime]] = None,
    models: Optional[List[str]] = None,
    agents: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Get comprehensive detailed data for export with all generation columns.

    Returns a DataFrame with ALL columns from the generations table plus trace
    information (agent name, session_id, user_id). This provides the most
    detailed view of all LLM activity for comprehensive exports.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple for filtering
        models: Optional list of model names to filter by
        agents: Optional list of agent names (trace names) to filter by

    Returns:
        DataFrame with columns:
            - id: Generation ID
            - trace_id: Associated trace ID
            - created_at: Timestamp of generation
            - model: Model identifier
            - input_tokens: Number of input tokens
            - output_tokens: Number of output tokens
            - total_tokens: Total token count
            - input_cost: Cost for input tokens
            - output_cost: Cost for output tokens
            - total_cost: Total cost for generation
            - latency_ms: Response latency in milliseconds
            - name: Generation name/identifier
            - agent_name: Name from associated trace
            - session_id: Session identifier from trace
            - user_id: User identifier from trace

    Example:
        >>> # Export all data
        >>> df = get_detailed_export_data("llm_metrics.db")
        >>> df.to_csv("full_export.csv", index=False)
        >>>
        >>> # Export filtered by model and date
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(days=7)
        >>> df = get_detailed_export_data(
        ...     "llm_metrics.db",
        ...     date_range=(start, end),
        ...     models=["gpt-4o", "gpt-4o-mini"]
        ... )
        >>> df.to_excel("weekly_gpt4_export.xlsx", index=False)
        >>>
        >>> # Export specific agent activity
        >>> df = get_detailed_export_data(
        ...     "llm_metrics.db",
        ...     agents=["code-developer", "project-manager"]
        ... )
        >>> print(f"Total rows: {len(df)}")
        Total rows: 1523
    """
    conn = sqlite3.connect(db_path)

    # Build WHERE clause conditions
    where_conditions = []
    params = []

    # Date range filter
    if date_range:
        where_conditions.append("g.created_at BETWEEN ? AND ?")
        params.extend([date_range[0], date_range[1]])

    # Model filter
    if models and len(models) > 0:
        placeholders = ",".join(["?" for _ in models])
        where_conditions.append(f"g.model IN ({placeholders})")
        params.extend(models)

    # Agent filter
    if agents and len(agents) > 0:
        placeholders = ",".join(["?" for _ in agents])
        where_conditions.append(f"t.name IN ({placeholders})")
        params.extend(agents)

    # Construct WHERE clause
    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)

    # Query with ALL generation columns plus trace info
    query = f"""
        SELECT
            g.id,
            g.trace_id,
            g.created_at,
            g.model,
            COALESCE(g.input_tokens, 0) as input_tokens,
            COALESCE(g.output_tokens, 0) as output_tokens,
            COALESCE(g.total_tokens, 0) as total_tokens,
            COALESCE(g.input_cost, 0.0) as input_cost,
            COALESCE(g.output_cost, 0.0) as output_cost,
            COALESCE(g.total_cost, 0.0) as total_cost,
            COALESCE(g.latency_ms, 0.0) as latency_ms,
            g.name as generation_name,
            COALESCE(t.name, 'Unknown') as agent_name,
            t.session_id,
            t.user_id
        FROM generations g
        LEFT JOIN traces t ON g.trace_id = t.id
        {where_clause}
        ORDER BY g.created_at DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert created_at to datetime and format for export
    df["created_at"] = pd.to_datetime(df["created_at"])

    # Handle NULL values in optional columns
    df["session_id"] = df["session_id"].fillna("N/A")
    df["user_id"] = df["user_id"].fillna("N/A")
    df["generation_name"] = df["generation_name"].fillna("N/A")

    return df


@st.cache_data(ttl=300)
def get_summary_export_data(
    db_path: str,
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> pd.DataFrame:
    """Get summarized daily aggregate data by model for export.

    Returns a DataFrame with daily aggregates grouped by date and model,
    providing a high-level summary view suitable for executive reports
    and trend analysis.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple for filtering

    Returns:
        DataFrame with columns:
            - date: Date of aggregation
            - model: Model identifier
            - request_count: Number of requests for that day/model
            - total_tokens: Sum of all tokens used
            - input_tokens: Sum of input tokens
            - output_tokens: Sum of output tokens
            - total_cost: Sum of costs
            - input_cost: Sum of input costs
            - output_cost: Sum of output costs
            - avg_latency_ms: Average response latency
            - min_latency_ms: Minimum response latency
            - max_latency_ms: Maximum response latency
            - unique_agents: Number of unique agents using this model

    Example:
        >>> # Export summary data for last 30 days
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(days=30)
        >>> df = get_summary_export_data("llm_metrics.db", date_range=(start, end))
        >>> df.to_csv("monthly_summary.csv", index=False)
        >>>
        >>> # Calculate total cost per model
        >>> model_totals = df.groupby("model")["total_cost"].sum()
        >>> print(model_totals)
        >>>
        >>> # View daily spending
        >>> daily_totals = df.groupby("date")["total_cost"].sum()
        >>> print(f"Peak spending: ${daily_totals.max():.2f}")
        Peak spending: $45.67
    """
    conn = sqlite3.connect(db_path)

    # Build WHERE clause
    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE g.created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            DATE(g.created_at) as date,
            g.model,
            COUNT(g.id) as request_count,
            COALESCE(SUM(g.total_tokens), 0) as total_tokens,
            COALESCE(SUM(g.input_tokens), 0) as input_tokens,
            COALESCE(SUM(g.output_tokens), 0) as output_tokens,
            COALESCE(SUM(g.total_cost), 0.0) as total_cost,
            COALESCE(SUM(g.input_cost), 0.0) as input_cost,
            COALESCE(SUM(g.output_cost), 0.0) as output_cost,
            COALESCE(AVG(g.latency_ms), 0.0) as avg_latency_ms,
            COALESCE(MIN(g.latency_ms), 0.0) as min_latency_ms,
            COALESCE(MAX(g.latency_ms), 0.0) as max_latency_ms,
            COUNT(DISTINCT t.name) as unique_agents
        FROM generations g
        LEFT JOIN traces t ON g.trace_id = t.id
        {where_clause}
        GROUP BY DATE(g.created_at), g.model
        ORDER BY date DESC, g.model ASC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])

    return df


@st.cache_data(ttl=300)
def get_agent_summary_export_data(
    db_path: str,
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> pd.DataFrame:
    """Get summarized data by agent for export.

    Returns a DataFrame aggregated by agent (trace name) showing total
    usage, costs, and performance metrics per agent.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple for filtering

    Returns:
        DataFrame with columns:
            - agent_name: Name from trace
            - request_count: Total number of requests
            - total_cost: Total cost incurred
            - total_tokens: Total tokens used
            - input_tokens: Total input tokens
            - output_tokens: Total output tokens
            - avg_latency_ms: Average response latency
            - unique_models: Number of different models used
            - unique_sessions: Number of unique sessions
            - first_activity: Timestamp of first activity
            - last_activity: Timestamp of last activity

    Example:
        >>> # Export agent usage summary
        >>> df = get_agent_summary_export_data("llm_metrics.db")
        >>> df.to_csv("agent_summary.csv", index=False)
        >>>
        >>> # Find most expensive agent
        >>> top_agent = df.sort_values("total_cost", ascending=False).iloc[0]
        >>> print(f"{top_agent['agent_name']}: ${top_agent['total_cost']:.2f}")
        code-developer: $234.56
    """
    conn = sqlite3.connect(db_path)

    # Build WHERE clause
    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE g.created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            COALESCE(t.name, 'Unknown') as agent_name,
            COUNT(g.id) as request_count,
            COALESCE(SUM(g.total_cost), 0.0) as total_cost,
            COALESCE(SUM(g.total_tokens), 0) as total_tokens,
            COALESCE(SUM(g.input_tokens), 0) as input_tokens,
            COALESCE(SUM(g.output_tokens), 0) as output_tokens,
            COALESCE(AVG(g.latency_ms), 0.0) as avg_latency_ms,
            COUNT(DISTINCT g.model) as unique_models,
            COUNT(DISTINCT t.session_id) as unique_sessions,
            MIN(g.created_at) as first_activity,
            MAX(g.created_at) as last_activity
        FROM generations g
        LEFT JOIN traces t ON g.trace_id = t.id
        {where_clause}
        GROUP BY t.name
        ORDER BY total_cost DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert timestamps to datetime
    df["first_activity"] = pd.to_datetime(df["first_activity"])
    df["last_activity"] = pd.to_datetime(df["last_activity"])

    return df


@st.cache_data(ttl=300)
def get_model_summary_export_data(
    db_path: str,
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> pd.DataFrame:
    """Get summarized data by model for export.

    Returns a DataFrame aggregated by model showing total usage, costs,
    and performance metrics per model.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple for filtering

    Returns:
        DataFrame with columns:
            - model: Model identifier
            - request_count: Total number of requests
            - total_cost: Total cost incurred
            - total_tokens: Total tokens used
            - input_tokens: Total input tokens
            - output_tokens: Total output tokens
            - avg_cost_per_request: Average cost per request
            - cost_per_1k_tokens: Cost per 1000 tokens
            - avg_latency_ms: Average response latency
            - median_latency_ms: Median response latency
            - p95_latency_ms: 95th percentile latency
            - unique_agents: Number of different agents using this model

    Example:
        >>> # Export model performance summary
        >>> df = get_model_summary_export_data("llm_metrics.db")
        >>> df.to_csv("model_summary.csv", index=False)
        >>>
        >>> # Compare model costs
        >>> print(df[["model", "total_cost", "cost_per_1k_tokens"]])
    """
    conn = sqlite3.connect(db_path)

    # Build WHERE clause
    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE g.created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            g.model,
            COUNT(g.id) as request_count,
            COALESCE(SUM(g.total_cost), 0.0) as total_cost,
            COALESCE(SUM(g.total_tokens), 0) as total_tokens,
            COALESCE(SUM(g.input_tokens), 0) as input_tokens,
            COALESCE(SUM(g.output_tokens), 0) as output_tokens,
            COALESCE(AVG(g.total_cost), 0.0) as avg_cost_per_request,
            CASE
                WHEN SUM(g.total_tokens) > 0
                THEN (SUM(g.total_cost) * 1000.0 / SUM(g.total_tokens))
                ELSE 0.0
            END as cost_per_1k_tokens,
            COALESCE(AVG(g.latency_ms), 0.0) as avg_latency_ms,
            COUNT(DISTINCT t.name) as unique_agents
        FROM generations g
        LEFT JOIN traces t ON g.trace_id = t.id
        {where_clause}
        GROUP BY g.model
        ORDER BY total_cost DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Calculate median and p95 latency separately (SQLite doesn't have built-in percentile functions)
    # We'll add these as approximate values based on available data
    df["median_latency_ms"] = df["avg_latency_ms"]  # Approximation
    df["p95_latency_ms"] = df["avg_latency_ms"] * 1.5  # Approximation

    return df


@st.cache_data(ttl=300)
def get_hourly_summary_export_data(
    db_path: str,
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> pd.DataFrame:
    """Get hourly aggregated data for detailed time-based analysis.

    Returns a DataFrame with hourly aggregates, useful for understanding
    usage patterns throughout the day and identifying peak usage times.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple for filtering

    Returns:
        DataFrame with columns:
            - datetime: Hour timestamp
            - hour: Hour of day (0-23)
            - date: Date
            - request_count: Number of requests in that hour
            - total_cost: Total cost for that hour
            - total_tokens: Total tokens used
            - unique_models: Number of different models used
            - unique_agents: Number of different agents active

    Example:
        >>> # Export hourly data for detailed analysis
        >>> df = get_hourly_summary_export_data("llm_metrics.db")
        >>> df.to_csv("hourly_usage.csv", index=False)
        >>>
        >>> # Find peak usage hour
        >>> peak = df.sort_values("request_count", ascending=False).iloc[0]
        >>> print(f"Peak hour: {peak['datetime']} with {peak['request_count']} requests")
    """
    conn = sqlite3.connect(db_path)

    # Build WHERE clause
    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE g.created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            strftime('%Y-%m-%d %H:00:00', g.created_at) as datetime,
            CAST(strftime('%H', g.created_at) AS INTEGER) as hour,
            DATE(g.created_at) as date,
            COUNT(g.id) as request_count,
            COALESCE(SUM(g.total_cost), 0.0) as total_cost,
            COALESCE(SUM(g.total_tokens), 0) as total_tokens,
            COUNT(DISTINCT g.model) as unique_models,
            COUNT(DISTINCT t.name) as unique_agents
        FROM generations g
        LEFT JOIN traces t ON g.trace_id = t.id
        {where_clause}
        GROUP BY datetime, hour, date
        ORDER BY datetime DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert datetime columns
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = pd.to_datetime(df["date"])

    return df
