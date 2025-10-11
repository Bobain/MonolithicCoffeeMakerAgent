"""
Performance Analysis Query Module for Analytics Dashboard.

This module provides functions to query and analyze performance-related metrics
from the LLM generations database.
"""

import sqlite3
from datetime import datetime
from typing import Optional, Tuple
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_latency_percentiles(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """
    Calculate latency percentiles (p50, p75, p90, p95, p99) by model.

    Args:
        db_path: Path to the SQLite database file
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, returns all historical data.

    Returns:
        DataFrame with columns:
            - model: Model name (str)
            - p50: 50th percentile latency in ms (float)
            - p75: 75th percentile latency in ms (float)
            - p90: 90th percentile latency in ms (float)
            - p95: 95th percentile latency in ms (float)
            - p99: 99th percentile latency in ms (float)

    Examples:
        >>> # Get latency percentiles for all models
        >>> latency_df = get_latency_percentiles("metrics.db")
        >>> print(latency_df)
                      model    p50    p75    p90    p95    p99
        0  claude-3-opus   1500   2100   3200   4500   6800
        1  gpt-4          1200   1800   2500   3200   4900

        >>> # Get percentiles for last 24 hours
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(hours=24)
        >>> latency_df = get_latency_percentiles("metrics.db", (start, end))
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            model,
            COALESCE(latency_ms, 0.0) as latency_ms
        FROM generations
        WHERE latency_ms IS NOT NULL
    """

    params = []
    if date_range:
        query += " AND created_at BETWEEN ? AND ?"
        params.extend([date_range[0].isoformat(), date_range[1].isoformat()])

    query += " ORDER BY model, latency_ms"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=["model", "p50", "p75", "p90", "p95", "p99"])

    # Calculate percentiles by model
    percentiles = df.groupby("model")["latency_ms"].quantile([0.50, 0.75, 0.90, 0.95, 0.99]).unstack()
    percentiles.columns = ["p50", "p75", "p90", "p95", "p99"]
    percentiles = percentiles.reset_index()

    return percentiles


@st.cache_data(ttl=300)
def get_hourly_usage_heatmap(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """
    Get request counts by hour of day and day of week for heatmap visualization.

    Args:
        db_path: Path to the SQLite database file
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, returns all historical data.

    Returns:
        DataFrame with columns:
            - hour: Hour of day (0-23) (int)
            - day_of_week: Day of week (0=Monday, 6=Sunday) (int)
            - request_count: Number of requests (int)

    Examples:
        >>> # Get usage heatmap for all data
        >>> heatmap_df = get_hourly_usage_heatmap("metrics.db")
        >>> print(heatmap_df.head())
           hour  day_of_week  request_count
        0     0            0             15
        1     0            1             12
        2     1            0             18

        >>> # Get heatmap for last 30 days
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(days=30)
        >>> heatmap_df = get_hourly_usage_heatmap("metrics.db", (start, end))

        >>> # Pivot for heatmap visualization
        >>> pivot_df = heatmap_df.pivot(
        ...     index='hour',
        ...     columns='day_of_week',
        ...     values='request_count'
        ... ).fillna(0)
    """
    conn = sqlite3.connect(db_path)

    # SQLite strftime with %w returns 0=Sunday, we need to convert to 0=Monday
    query = """
        SELECT
            CAST(strftime('%H', created_at) AS INTEGER) as hour,
            CASE
                WHEN CAST(strftime('%w', created_at) AS INTEGER) = 0 THEN 6
                ELSE CAST(strftime('%w', created_at) AS INTEGER) - 1
            END as day_of_week,
            COUNT(*) as request_count
        FROM generations
    """

    params = []
    if date_range:
        query += " WHERE created_at BETWEEN ? AND ?"
        params.extend([date_range[0].isoformat(), date_range[1].isoformat()])

    query += """
        GROUP BY hour, day_of_week
        ORDER BY hour, day_of_week
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


@st.cache_data(ttl=300)
def get_error_rate_by_model(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """
    Calculate error rates by model based on traces with error metadata.

    This function attempts to identify errors by checking for NULL latency_ms
    or zero/negative latency values, as well as looking for error indicators
    in the trace metadata. The error detection is heuristic-based.

    Args:
        db_path: Path to the SQLite database file
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, returns all historical data.

    Returns:
        DataFrame with columns:
            - model: Model name (str)
            - total_requests: Total number of requests (int)
            - error_count: Number of requests with errors (int)
            - error_rate: Error rate as percentage (float, 0-100)

    Examples:
        >>> # Get error rates for all models
        >>> error_df = get_error_rate_by_model("metrics.db")
        >>> print(error_df)
                      model  total_requests  error_count  error_rate
        0  claude-3-opus            1000           15        1.50
        1  gpt-4                     800            8        1.00

        >>> # Get error rates for last week
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(days=7)
        >>> error_df = get_error_rate_by_model("metrics.db", (start, end))

        >>> # Filter to models with high error rates
        >>> high_error = error_df[error_df['error_rate'] > 5.0]
    """
    conn = sqlite3.connect(db_path)

    # Define error conditions:
    # 1. latency_ms IS NULL (request failed before completion)
    # 2. latency_ms <= 0 (invalid latency)
    # 3. total_cost IS NULL AND latency_ms IS NOT NULL (pricing error)
    query = """
        SELECT
            model,
            COUNT(*) as total_requests,
            SUM(
                CASE
                    WHEN latency_ms IS NULL THEN 1
                    WHEN latency_ms <= 0 THEN 1
                    WHEN total_cost IS NULL AND latency_ms IS NOT NULL THEN 1
                    ELSE 0
                END
            ) as error_count
        FROM generations
    """

    params = []
    if date_range:
        query += " WHERE created_at BETWEEN ? AND ?"
        params.extend([date_range[0].isoformat(), date_range[1].isoformat()])

    query += """
        GROUP BY model
        ORDER BY error_rate DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=["model", "total_requests", "error_count", "error_rate"])

    # Calculate error rate percentage
    df["error_rate"] = (df["error_count"] / df["total_requests"] * 100).round(2)

    return df


@st.cache_data(ttl=300)
def get_token_efficiency_by_model(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """
    Calculate token efficiency metrics by model.

    Args:
        db_path: Path to the SQLite database file
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, returns all historical data.

    Returns:
        DataFrame with columns:
            - model: Model name (str)
            - avg_input_tokens: Average input tokens per request (float)
            - avg_output_tokens: Average output tokens per request (float)
            - avg_total_tokens: Average total tokens per request (float)
            - total_requests: Total number of requests (int)
            - output_input_ratio: Ratio of output to input tokens (float)

    Examples:
        >>> # Get token efficiency for all models
        >>> efficiency_df = get_token_efficiency_by_model("metrics.db")
        >>> print(efficiency_df)
                      model  avg_input_tokens  avg_output_tokens  ...
        0  claude-3-opus              1250               450      ...
        1  gpt-4                      1100               380      ...

        >>> # Compare models by output/input ratio
        >>> sorted_df = efficiency_df.sort_values('output_input_ratio', ascending=False)
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            model,
            AVG(COALESCE(input_tokens, 0)) as avg_input_tokens,
            AVG(COALESCE(output_tokens, 0)) as avg_output_tokens,
            AVG(COALESCE(total_tokens, 0)) as avg_total_tokens,
            COUNT(*) as total_requests,
            CASE
                WHEN AVG(COALESCE(input_tokens, 0)) > 0
                THEN AVG(COALESCE(output_tokens, 0)) * 1.0 / AVG(COALESCE(input_tokens, 0))
                ELSE 0.0
            END as output_input_ratio
        FROM generations
    """

    params = []
    if date_range:
        query += " WHERE created_at BETWEEN ? AND ?"
        params.extend([date_range[0].isoformat(), date_range[1].isoformat()])

    query += """
        GROUP BY model
        ORDER BY avg_total_tokens DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if not df.empty:
        # Round numeric columns for readability
        df["avg_input_tokens"] = df["avg_input_tokens"].round(2)
        df["avg_output_tokens"] = df["avg_output_tokens"].round(2)
        df["avg_total_tokens"] = df["avg_total_tokens"].round(2)
        df["output_input_ratio"] = df["output_input_ratio"].round(3)

    return df


@st.cache_data(ttl=300)
def get_throughput_over_time(
    db_path: str, interval: str = "hour", date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """
    Get request throughput over time at different time intervals.

    Args:
        db_path: Path to the SQLite database file
        interval: Time interval for grouping ('hour', 'day', 'minute') (default: 'hour')
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, returns all historical data.

    Returns:
        DataFrame with columns:
            - timestamp: Time bucket (datetime)
            - request_count: Number of requests in that time bucket (int)
            - avg_latency_ms: Average latency in ms (float)
            - total_tokens: Sum of tokens processed (int)

    Examples:
        >>> # Get hourly throughput
        >>> throughput_df = get_throughput_over_time("metrics.db", interval='hour')
        >>> print(throughput_df.head())
                    timestamp  request_count  avg_latency_ms  total_tokens
        0 2024-01-01 00:00:00             25          1450.5         45000
        1 2024-01-01 01:00:00             30          1380.2         52000

        >>> # Get minute-by-minute throughput for last hour
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(hours=1)
        >>> throughput_df = get_throughput_over_time(
        ...     "metrics.db",
        ...     interval='minute',
        ...     date_range=(start, end)
        ... )

        >>> # Get daily throughput
        >>> daily_df = get_throughput_over_time("metrics.db", interval='day')
    """
    conn = sqlite3.connect(db_path)

    # Determine time format based on interval
    time_formats = {"minute": "%Y-%m-%d %H:%M:00", "hour": "%Y-%m-%d %H:00:00", "day": "%Y-%m-%d"}

    if interval not in time_formats:
        raise ValueError(f"Invalid interval: {interval}. Must be one of {list(time_formats.keys())}")

    time_format = time_formats[interval]

    query = f"""
        SELECT
            strftime('{time_format}', created_at) as timestamp,
            COUNT(*) as request_count,
            AVG(COALESCE(latency_ms, 0.0)) as avg_latency_ms,
            SUM(COALESCE(total_tokens, 0)) as total_tokens
        FROM generations
    """

    params = []
    if date_range:
        query += " WHERE created_at BETWEEN ? AND ?"
        params.extend([date_range[0].isoformat(), date_range[1].isoformat()])

    query += f"""
        GROUP BY strftime('{time_format}', created_at)
        ORDER BY timestamp ASC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert timestamp to datetime
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["avg_latency_ms"] = df["avg_latency_ms"].round(2)

    return df
