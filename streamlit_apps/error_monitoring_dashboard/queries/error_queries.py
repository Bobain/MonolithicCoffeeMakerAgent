"""Error extraction queries for the error monitoring dashboard.

This module provides query functions for retrieving error data from Langfuse traces
stored in the SQLite database. All query functions return pandas DataFrames and are
cached using Streamlit's @st.cache_data decorator for optimal performance.

Example:
    >>> import streamlit as st
    >>> errors = get_error_summary("llm_metrics.db")
    >>> st.metric("Total Errors", f"{errors['total_errors']:,}")
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from streamlit_apps.error_monitoring_dashboard.utils.error_classifier import ErrorClassifier


@st.cache_data(ttl=300)
def get_error_summary(db_path: str, hours: int = 24) -> Dict[str, any]:
    """Get error summary statistics for the last N hours.

    Args:
        db_path: Path to SQLite database
        hours: Number of hours to look back (default: 24)

    Returns:
        Dictionary with total_errors, error_rate, critical_errors

    Example:
        >>> stats = get_error_summary("llm_metrics.db", hours=24)
        >>> print(f"Total errors: {stats['total_errors']}")
    """
    conn = sqlite3.connect(db_path)
    cutoff_time = datetime.now() - timedelta(hours=hours)

    # Count errors
    error_query = """
        SELECT COUNT(DISTINCT t.id) as error_count
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        WHERE (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
          AND t.timestamp >= ?
    """

    # Count total traces
    total_query = """
        SELECT COUNT(*) as total_count
        FROM traces
        WHERE timestamp >= ?
    """

    error_df = pd.read_sql_query(error_query, conn, params=[cutoff_time])
    total_df = pd.read_sql_query(total_query, conn, params=[cutoff_time])

    conn.close()

    total_errors = int(error_df.iloc[0]["error_count"])
    total_traces = int(total_df.iloc[0]["total_count"])
    error_rate = total_errors / total_traces if total_traces > 0 else 0.0

    # Estimate critical errors (would need severity classification in DB for accuracy)
    critical_errors = int(total_errors * 0.15)  # Rough estimate

    return {
        "total_errors": total_errors,
        "total_traces": total_traces,
        "error_rate": error_rate,
        "critical_errors": critical_errors,
    }


@st.cache_data(ttl=300)
def get_error_traces(
    db_path: str,
    limit: int = 100,
    date_range: Optional[Tuple[datetime, datetime]] = None,
    error_type: Optional[str] = None,
    model: Optional[str] = None,
) -> pd.DataFrame:
    """Get error traces with full context.

    Args:
        db_path: Path to SQLite database
        limit: Maximum number of traces to return
        date_range: Optional (start_date, end_date) tuple
        error_type: Optional error type filter
        model: Optional model filter

    Returns:
        DataFrame with error trace details

    Example:
        >>> df = get_error_traces("llm_metrics.db", limit=50)
        >>> print(df.columns)
    """
    conn = sqlite3.connect(db_path)

    where_clauses = ["(e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)"]
    params = []

    if date_range:
        where_clauses.append("t.timestamp BETWEEN ? AND ?")
        params.extend([date_range[0], date_range[1]])

    if model:
        where_clauses.append("g.model = ?")
        params.append(model)

    where_clause = " AND ".join(where_clauses)

    query = f"""
        SELECT
            t.id as trace_id,
            t.name as trace_name,
            t.timestamp,
            t.metadata,
            t.status_message as error_message,
            e.level as event_level,
            e.message as event_message,
            e.body as event_body,
            g.model,
            g.model_parameters,
            g.prompt_tokens,
            g.completion_tokens,
            g.total_tokens,
            g.total_cost,
            g.latency_ms
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        LEFT JOIN generations g ON t.id = g.trace_id
        WHERE {where_clause}
        ORDER BY t.timestamp DESC
        LIMIT ?
    """
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Combine error messages
    df["combined_error"] = df.apply(
        lambda row: (
            row["error_message"]
            if pd.notna(row["error_message"])
            else (row["event_message"] if pd.notna(row["event_message"]) else "Unknown error")
        ),
        axis=1,
    )

    # Classify errors
    if not df.empty:
        classifications = df["combined_error"].apply(ErrorClassifier.classify)
        df["error_type"] = classifications.apply(lambda x: x["type"])
        df["severity"] = classifications.apply(lambda x: x["severity"])
        df["category"] = classifications.apply(lambda x: x["category"])
        df["recommendation"] = classifications.apply(lambda x: x["recommendation"])

        # Filter by error type if specified
        if error_type and error_type != "All":
            df = df[df["error_type"] == error_type]

    return df


@st.cache_data(ttl=300)
def get_error_timeline(
    db_path: str, hours: int = 24, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get error timeline for visualization.

    Args:
        db_path: Path to SQLite database
        hours: Number of hours to look back (default: 24)
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with hourly error counts

    Example:
        >>> df = get_error_timeline("llm_metrics.db", hours=48)
        >>> print(df.head())
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "AND t.timestamp BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]
    else:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        where_clause = "AND t.timestamp >= ?"
        params = [cutoff_time]

    query = f"""
        SELECT
            strftime('%Y-%m-%d %H:00:00', t.timestamp) as hour,
            COUNT(DISTINCT t.id) as error_count
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        WHERE (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
          {where_clause}
        GROUP BY strftime('%Y-%m-%d %H:00:00', t.timestamp)
        ORDER BY hour ASC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert hour to datetime
    df["hour"] = pd.to_datetime(df["hour"])

    return df


@st.cache_data(ttl=300)
def get_error_by_model(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """Get error counts by model.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with error counts by model

    Example:
        >>> df = get_error_by_model("llm_metrics.db")
        >>> print(df.sort_values("error_count", ascending=False))
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "AND t.timestamp BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            COALESCE(g.model, 'Unknown') as model,
            COUNT(DISTINCT t.id) as error_count,
            COUNT(DISTINCT t.id) * 100.0 / (
                SELECT COUNT(DISTINCT id)
                FROM traces
                WHERE 1=1 {where_clause.replace('t.timestamp', 'timestamp')}
            ) as error_percentage
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        LEFT JOIN generations g ON t.id = g.trace_id
        WHERE (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
          {where_clause}
        GROUP BY g.model
        ORDER BY error_count DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


@st.cache_data(ttl=300)
def get_error_by_type(
    db_path: str, limit: int = 10, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get top error types with counts.

    Args:
        db_path: Path to SQLite database
        limit: Maximum number of error types to return
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with error types and counts

    Example:
        >>> df = get_error_by_type("llm_metrics.db", limit=5)
        >>> print(df)
    """
    # Get all error traces
    error_traces = get_error_traces(db_path, limit=1000, date_range=date_range)

    if error_traces.empty:
        return pd.DataFrame(columns=["error_type", "count", "severity"])

    # Count by error type
    error_counts = error_traces.groupby(["error_type", "severity"]).size().reset_index(name="count")
    error_counts = error_counts.sort_values("count", ascending=False).head(limit)

    return error_counts


@st.cache_data(ttl=300)
def get_error_severity_distribution(
    db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get error distribution by severity.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with severity distribution

    Example:
        >>> df = get_error_severity_distribution("llm_metrics.db")
        >>> print(df)
    """
    # Get all error traces
    error_traces = get_error_traces(db_path, limit=10000, date_range=date_range)

    if error_traces.empty:
        return pd.DataFrame(columns=["severity", "count"])

    # Count by severity
    severity_counts = error_traces.groupby("severity").size().reset_index(name="count")

    # Sort by severity order
    severity_counts["order"] = severity_counts["severity"].apply(ErrorClassifier.get_severity_order)
    severity_counts = severity_counts.sort_values("order").drop(columns=["order"])

    return severity_counts


@st.cache_data(ttl=300)
def get_recent_errors(
    db_path: str, limit: int = 10, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """Get most recent errors for quick display.

    Args:
        db_path: Path to SQLite database
        limit: Maximum number of errors to return
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with recent errors

    Example:
        >>> df = get_recent_errors("llm_metrics.db", limit=5)
        >>> print(df[["timestamp", "error_type", "model"]])
    """
    error_traces = get_error_traces(db_path, limit=limit, date_range=date_range)

    if error_traces.empty:
        return pd.DataFrame()

    # Select relevant columns
    recent = error_traces[["timestamp", "error_type", "severity", "model", "trace_id", "combined_error"]].copy()

    return recent


@st.cache_data(ttl=300)
def get_available_models_with_errors(db_path: str) -> List[str]:
    """Get list of models that have errors.

    Args:
        db_path: Path to SQLite database

    Returns:
        List of model names

    Example:
        >>> models = get_available_models_with_errors("llm_metrics.db")
        >>> print(models)
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT DISTINCT g.model
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        LEFT JOIN generations g ON t.id = g.trace_id
        WHERE (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
          AND g.model IS NOT NULL
        ORDER BY g.model
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return ["All"] + df["model"].tolist()


@st.cache_data(ttl=300)
def get_hourly_error_pattern(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """Get hourly error pattern for heatmap visualization.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with columns: hour, day_of_week, error_count

    Example:
        >>> df = get_hourly_error_pattern("llm_metrics.db")
        >>> # Use for heatmap showing errors by hour and day of week
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "AND t.timestamp BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            CAST(strftime('%H', t.timestamp) AS INTEGER) as hour,
            CAST(strftime('%w', t.timestamp) AS INTEGER) as day_of_week,
            COUNT(DISTINCT t.id) as error_count
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        WHERE (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
          {where_clause}
        GROUP BY hour, day_of_week
        ORDER BY day_of_week, hour
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


@st.cache_data(ttl=300)
def get_model_failure_rates(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """Get model failure rates (errors / total requests).

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple

    Returns:
        DataFrame with model failure rates

    Example:
        >>> df = get_model_failure_rates("llm_metrics.db")
        >>> print(df.sort_values("failure_rate", ascending=False))
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE timestamp BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            g.model,
            COUNT(DISTINCT CASE WHEN (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
                  THEN t.id END) as error_count,
            COUNT(DISTINCT t.id) as total_count,
            (COUNT(DISTINCT CASE WHEN (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
                  THEN t.id END) * 100.0 / COUNT(DISTINCT t.id)) as failure_rate
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        LEFT JOIN generations g ON t.id = g.trace_id
        {where_clause}
        GROUP BY g.model
        HAVING COUNT(DISTINCT t.id) > 0
        ORDER BY failure_rate DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df
