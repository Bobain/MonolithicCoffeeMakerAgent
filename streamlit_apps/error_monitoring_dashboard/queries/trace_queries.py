"""Trace detail queries for the error monitoring dashboard.

This module provides query functions for retrieving detailed trace information
from the Langfuse database, including full context for error investigation.

Example:
    >>> trace = get_trace_details("llm_metrics.db", "trace-abc123")
    >>> print(trace['error_message'])
"""

import json
import sqlite3
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_trace_details(db_path: str, trace_id: str) -> Optional[Dict]:
    """Get full details for a specific trace.

    Args:
        db_path: Path to SQLite database
        trace_id: Trace ID to retrieve

    Returns:
        Dictionary with full trace details or None if not found

    Example:
        >>> trace = get_trace_details("llm_metrics.db", "trace-123")
        >>> print(trace['timestamp'])
    """
    conn = sqlite3.connect(db_path)

    # Get trace details
    trace_query = """
        SELECT
            t.id,
            t.name,
            t.timestamp,
            t.metadata,
            t.status_message,
            t.input,
            t.output
        FROM traces t
        WHERE t.id = ?
    """

    trace_df = pd.read_sql_query(trace_query, conn, params=[trace_id])

    if trace_df.empty:
        conn.close()
        return None

    trace = trace_df.iloc[0].to_dict()

    # Parse JSON fields
    if trace.get("metadata"):
        try:
            trace["metadata"] = (
                json.loads(trace["metadata"]) if isinstance(trace["metadata"], str) else trace["metadata"]
            )
        except:
            pass

    # Get related events
    events_query = """
        SELECT
            id,
            timestamp,
            level,
            message,
            body
        FROM events
        WHERE trace_id = ?
        ORDER BY timestamp ASC
    """

    events_df = pd.read_sql_query(events_query, conn, params=[trace_id])
    trace["events"] = events_df.to_dict("records")

    # Parse event bodies
    for event in trace["events"]:
        if event.get("body"):
            try:
                event["body"] = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
            except:
                pass

    # Get related generations
    gen_query = """
        SELECT
            id,
            model,
            model_parameters,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            total_cost,
            latency_ms,
            created_at
        FROM generations
        WHERE trace_id = ?
    """

    gen_df = pd.read_sql_query(gen_query, conn, params=[trace_id])
    if not gen_df.empty:
        trace["generation"] = gen_df.iloc[0].to_dict()

        # Parse model parameters
        if trace["generation"].get("model_parameters"):
            try:
                trace["generation"]["model_parameters"] = (
                    json.loads(trace["generation"]["model_parameters"])
                    if isinstance(trace["generation"]["model_parameters"], str)
                    else trace["generation"]["model_parameters"]
                )
            except:
                pass
    else:
        trace["generation"] = None

    conn.close()

    return trace


@st.cache_data(ttl=300)
def search_traces(
    db_path: str,
    search_query: str = "",
    date_range: Optional[tuple] = None,
    model: Optional[str] = None,
    limit: int = 50,
) -> pd.DataFrame:
    """Search traces by various criteria.

    Args:
        db_path: Path to SQLite database
        search_query: Text search query (searches in name and error messages)
        date_range: Optional (start_date, end_date) tuple
        model: Optional model filter
        limit: Maximum number of results

    Returns:
        DataFrame with matching traces

    Example:
        >>> df = search_traces("llm_metrics.db", search_query="rate limit")
        >>> print(df[["id", "name", "timestamp"]])
    """
    conn = sqlite3.connect(db_path)

    where_clauses = ["(e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)"]
    params = []

    if search_query:
        where_clauses.append("(t.name LIKE ? OR t.status_message LIKE ? OR e.message LIKE ?)")
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if date_range:
        where_clauses.append("t.timestamp BETWEEN ? AND ?")
        params.extend([date_range[0], date_range[1]])

    if model and model != "All":
        where_clauses.append("g.model = ?")
        params.append(model)

    where_clause = " AND ".join(where_clauses)

    query = f"""
        SELECT DISTINCT
            t.id,
            t.name,
            t.timestamp,
            t.status_message,
            g.model,
            e.level,
            e.message as event_message
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

    # Convert timestamp
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


@st.cache_data(ttl=300)
def get_trace_events(db_path: str, trace_id: str) -> pd.DataFrame:
    """Get all events for a specific trace.

    Args:
        db_path: Path to SQLite database
        trace_id: Trace ID

    Returns:
        DataFrame with trace events

    Example:
        >>> df = get_trace_events("llm_metrics.db", "trace-123")
        >>> print(df[["timestamp", "level", "message"]])
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            id,
            timestamp,
            level,
            message,
            body
        FROM events
        WHERE trace_id = ?
        ORDER BY timestamp ASC
    """

    df = pd.read_sql_query(query, conn, params=[trace_id])
    conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


@st.cache_data(ttl=300)
def get_trace_generation(db_path: str, trace_id: str) -> Optional[Dict]:
    """Get generation details for a specific trace.

    Args:
        db_path: Path to SQLite database
        trace_id: Trace ID

    Returns:
        Dictionary with generation details or None

    Example:
        >>> gen = get_trace_generation("llm_metrics.db", "trace-123")
        >>> print(gen['model'])
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            id,
            model,
            model_parameters,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            total_cost,
            latency_ms,
            created_at
        FROM generations
        WHERE trace_id = ?
    """

    df = pd.read_sql_query(query, conn, params=[trace_id])
    conn.close()

    if df.empty:
        return None

    generation = df.iloc[0].to_dict()

    # Parse model parameters
    if generation.get("model_parameters"):
        try:
            generation["model_parameters"] = (
                json.loads(generation["model_parameters"])
                if isinstance(generation["model_parameters"], str)
                else generation["model_parameters"]
            )
        except:
            pass

    return generation


@st.cache_data(ttl=300)
def get_related_traces(db_path: str, trace_id: str, limit: int = 5) -> pd.DataFrame:
    """Get traces related to the given trace (same name/agent).

    Args:
        db_path: Path to SQLite database
        trace_id: Reference trace ID
        limit: Maximum number of related traces

    Returns:
        DataFrame with related traces

    Example:
        >>> df = get_related_traces("llm_metrics.db", "trace-123")
        >>> print(df)
    """
    conn = sqlite3.connect(db_path)

    # First, get the trace name
    name_query = "SELECT name FROM traces WHERE id = ?"
    name_df = pd.read_sql_query(name_query, conn, params=[trace_id])

    if name_df.empty:
        conn.close()
        return pd.DataFrame()

    trace_name = name_df.iloc[0]["name"]

    # Find related traces with same name
    query = """
        SELECT
            t.id,
            t.name,
            t.timestamp,
            t.status_message,
            g.model
        FROM traces t
        LEFT JOIN generations g ON t.id = g.trace_id
        WHERE t.name = ? AND t.id != ?
        ORDER BY t.timestamp DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=[trace_name, trace_id, limit])
    conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


@st.cache_data(ttl=300)
def get_trace_statistics(db_path: str, trace_id: str) -> Dict:
    """Get statistical summary for a trace.

    Args:
        db_path: Path to SQLite database
        trace_id: Trace ID

    Returns:
        Dictionary with trace statistics

    Example:
        >>> stats = get_trace_statistics("llm_metrics.db", "trace-123")
        >>> print(stats['event_count'])
    """
    conn = sqlite3.connect(db_path)

    # Count events
    event_count_query = "SELECT COUNT(*) as count FROM events WHERE trace_id = ?"
    event_df = pd.read_sql_query(event_count_query, conn, params=[trace_id])
    event_count = int(event_df.iloc[0]["count"])

    # Count error events
    error_count_query = """
        SELECT COUNT(*) as count FROM events
        WHERE trace_id = ? AND level IN ('ERROR', 'WARNING')
    """
    error_df = pd.read_sql_query(error_count_query, conn, params=[trace_id])
    error_count = int(error_df.iloc[0]["count"])

    # Get generation stats
    gen_query = """
        SELECT
            total_tokens,
            total_cost,
            latency_ms
        FROM generations
        WHERE trace_id = ?
    """
    gen_df = pd.read_sql_query(gen_query, conn, params=[trace_id])

    conn.close()

    stats = {
        "event_count": event_count,
        "error_event_count": error_count,
        "has_generation": not gen_df.empty,
    }

    if not gen_df.empty:
        stats.update(
            {
                "total_tokens": int(gen_df.iloc[0]["total_tokens"] or 0),
                "total_cost": float(gen_df.iloc[0]["total_cost"] or 0.0),
                "latency_ms": float(gen_df.iloc[0]["latency_ms"] or 0.0),
            }
        )

    return stats


@st.cache_data(ttl=300)
def get_all_trace_ids(db_path: str, limit: int = 1000) -> List[str]:
    """Get list of all error trace IDs.

    Args:
        db_path: Path to SQLite database
        limit: Maximum number of trace IDs

    Returns:
        List of trace IDs

    Example:
        >>> ids = get_all_trace_ids("llm_metrics.db")
        >>> print(len(ids))
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT DISTINCT t.id
        FROM traces t
        LEFT JOIN events e ON t.id = e.trace_id
        WHERE (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
        ORDER BY t.timestamp DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=[limit])
    conn.close()

    return df["id"].tolist()
