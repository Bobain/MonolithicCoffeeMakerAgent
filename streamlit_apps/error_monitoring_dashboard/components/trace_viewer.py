"""
Trace viewer component for the Error Monitoring Dashboard.

This module provides components for displaying full trace details in an
organized, readable format with expandable sections and syntax highlighting.
"""

import json
import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

from streamlit_apps.error_monitoring_dashboard.utils.error_classifier import ErrorClassifier


def render_trace_details(trace_data: Dict[str, Any]) -> None:
    """
    Render full trace details in an organized, expandable format.

    Args:
        trace_data: Dictionary containing trace information with keys:
            - trace_id (str): Unique trace identifier
            - trace_name (str): Name of the trace
            - timestamp (datetime): When the error occurred
            - error_message (str): Error message
            - error_type (str): Classified error type
            - severity (str): Error severity
            - category (str): Error category
            - recommendation (str): Recommended action
            - model (str): Model used
            - latency_ms (float): Request latency
            - total_cost (float): Request cost
            - prompt_tokens (int): Input tokens
            - completion_tokens (int): Output tokens
            - metadata (str): JSON metadata
            - model_parameters (str): JSON model parameters

    Example:
        >>> trace = {
        ...     "trace_id": "trace_123",
        ...     "trace_name": "ChatCompletion",
        ...     "timestamp": "2024-01-15 10:30:00",
        ...     "error_message": "Rate limit exceeded",
        ...     "error_type": "RateLimitError",
        ...     "severity": "HIGH",
        ...     "model": "gpt-4"
        ... }
        >>> render_trace_details(trace)

    Notes:
        - Uses expandable sections for better organization
        - Includes syntax highlighting for JSON data
        - Shows severity with color-coded badges
    """
    # Header with trace ID and severity
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"Trace: {trace_data.get('trace_id', 'Unknown')}")
        st.caption(f"**{trace_data.get('trace_name', 'Unknown')}** at {trace_data.get('timestamp', 'Unknown')}")

    with col2:
        severity = trace_data.get("severity", "UNKNOWN")
        emoji = ErrorClassifier.get_severity_emoji(severity)
        color = ErrorClassifier.get_severity_color(severity)
        st.markdown(
            f"<div style='text-align: right; font-size: 20px;'>"
            f"{emoji} <span style='color: {color};'>{severity}</span></div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Error Information Section
    with st.expander("Error Information", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Error Type:**")
            st.code(trace_data.get("error_type", "Unknown"), language=None)

            st.markdown("**Category:**")
            st.info(trace_data.get("category", "Unknown"))

        with col2:
            st.markdown("**Severity:**")
            st.code(trace_data.get("severity", "Unknown"), language=None)

            st.markdown("**Recommendation:**")
            st.warning(trace_data.get("recommendation", "No recommendation available"))

        st.markdown("**Error Message:**")
        error_msg = trace_data.get("error_message") or trace_data.get("combined_error", "No error message")
        st.code(error_msg, language=None)

    # Model & Performance Section
    with st.expander("Model & Performance", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="Model", value=trace_data.get("model", "Unknown"))

        with col2:
            latency = trace_data.get("latency_ms")
            if latency is not None:
                st.metric(label="Latency", value=f"{latency:.0f} ms")
            else:
                st.metric(label="Latency", value="N/A")

        with col3:
            cost = trace_data.get("total_cost")
            if cost is not None:
                st.metric(label="Cost", value=f"${cost:.4f}")
            else:
                st.metric(label="Cost", value="N/A")

        # Token usage
        col1, col2, col3 = st.columns(3)

        with col1:
            prompt_tokens = trace_data.get("prompt_tokens")
            if prompt_tokens is not None:
                st.metric(label="Prompt Tokens", value=f"{prompt_tokens:,}")
            else:
                st.metric(label="Prompt Tokens", value="N/A")

        with col2:
            completion_tokens = trace_data.get("completion_tokens")
            if completion_tokens is not None:
                st.metric(label="Completion Tokens", value=f"{completion_tokens:,}")
            else:
                st.metric(label="Completion Tokens", value="N/A")

        with col3:
            total_tokens = trace_data.get("total_tokens")
            if total_tokens is not None:
                st.metric(label="Total Tokens", value=f"{total_tokens:,}")
            else:
                st.metric(label="Total Tokens", value="N/A")

    # Model Parameters Section
    with st.expander("Model Parameters", expanded=False):
        model_params = trace_data.get("model_parameters")
        if model_params:
            try:
                if isinstance(model_params, str):
                    params_dict = json.loads(model_params)
                else:
                    params_dict = model_params
                st.json(params_dict)
            except (json.JSONDecodeError, TypeError):
                st.code(str(model_params), language=None)
        else:
            st.info("No model parameters available")

    # Metadata Section
    with st.expander("Trace Metadata", expanded=False):
        metadata = trace_data.get("metadata")
        if metadata:
            try:
                if isinstance(metadata, str):
                    metadata_dict = json.loads(metadata)
                else:
                    metadata_dict = metadata
                st.json(metadata_dict)
            except (json.JSONDecodeError, TypeError):
                st.code(str(metadata), language=None)
        else:
            st.info("No metadata available")


def render_trace_list(traces_df: pd.DataFrame, max_display: int = 10) -> Optional[str]:
    """
    Render a list of traces with selection capability.

    Args:
        traces_df: DataFrame containing trace information
        max_display: Maximum number of traces to display (default: 10)

    Returns:
        Selected trace_id or None if no selection

    Example:
        >>> df = pd.DataFrame({
        ...     'trace_id': ['trace_1', 'trace_2'],
        ...     'timestamp': ['2024-01-15 10:30', '2024-01-15 10:35'],
        ...     'error_type': ['RateLimitError', 'TimeoutError'],
        ...     'severity': ['HIGH', 'HIGH'],
        ...     'model': ['gpt-4', 'gpt-3.5-turbo']
        ... })
        >>> selected = render_trace_list(df)

    Notes:
        - Displays traces in a table with key information
        - Uses color coding for severity
        - Provides click-to-select functionality
    """
    if traces_df.empty:
        st.info("No traces available")
        return None

    # Limit display
    display_df = traces_df.head(max_display).copy()

    # Format timestamp
    if "timestamp" in display_df.columns:
        display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Select columns to display
    display_columns = ["trace_id", "timestamp", "error_type", "severity", "model"]
    available_columns = [col for col in display_columns if col in display_df.columns]

    if not available_columns:
        st.warning("No displayable columns found in traces data")
        return None

    # Display table with selection
    st.markdown(f"**Showing {len(display_df)} of {len(traces_df)} traces**")

    # Create clickable trace list
    selected_trace = None
    for idx, row in display_df.iterrows():
        trace_id = row.get("trace_id", "Unknown")
        timestamp = row.get("timestamp", "Unknown")
        error_type = row.get("error_type", "Unknown")
        severity = row.get("severity", "UNKNOWN")
        model = row.get("model", "Unknown")

        emoji = ErrorClassifier.get_severity_emoji(severity)

        # Create a button for each trace
        col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 2, 2])

        with col1:
            st.markdown(f"**{emoji}**")
        with col2:
            st.text(timestamp)
        with col3:
            st.code(error_type, language=None)
        with col4:
            st.text(model)
        with col5:
            if st.button("View", key=f"view_{trace_id}"):
                selected_trace = trace_id

        st.divider()

    return selected_trace


def render_trace_comparison(trace1: Dict[str, Any], trace2: Dict[str, Any]) -> None:
    """
    Render a side-by-side comparison of two traces.

    Args:
        trace1: First trace data dictionary
        trace2: Second trace data dictionary

    Example:
        >>> trace1 = {"trace_id": "1", "error_type": "RateLimitError", "severity": "HIGH"}
        >>> trace2 = {"trace_id": "2", "error_type": "TimeoutError", "severity": "MEDIUM"}
        >>> render_trace_comparison(trace1, trace2)

    Notes:
        - Displays key metrics side by side
        - Highlights differences between traces
        - Useful for pattern analysis
    """
    st.subheader("Trace Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Trace 1")
        st.markdown(f"**ID:** {trace1.get('trace_id', 'Unknown')}")
        st.markdown(f"**Type:** {trace1.get('error_type', 'Unknown')}")
        st.markdown(f"**Severity:** {trace1.get('severity', 'Unknown')}")
        st.markdown(f"**Model:** {trace1.get('model', 'Unknown')}")

        latency1 = trace1.get("latency_ms")
        if latency1:
            st.metric("Latency", f"{latency1:.0f} ms")

    with col2:
        st.markdown("### Trace 2")
        st.markdown(f"**ID:** {trace2.get('trace_id', 'Unknown')}")
        st.markdown(f"**Type:** {trace2.get('error_type', 'Unknown')}")
        st.markdown(f"**Severity:** {trace2.get('severity', 'Unknown')}")
        st.markdown(f"**Model:** {trace2.get('model', 'Unknown')}")

        latency2 = trace2.get("latency_ms")
        if latency2:
            st.metric("Latency", f"{latency2:.0f} ms")

    # Highlight differences
    st.markdown("### Key Differences")

    differences = []

    if trace1.get("error_type") != trace2.get("error_type"):
        differences.append(f"Error Type: {trace1.get('error_type')} vs {trace2.get('error_type')}")

    if trace1.get("severity") != trace2.get("severity"):
        differences.append(f"Severity: {trace1.get('severity')} vs {trace2.get('severity')}")

    if trace1.get("model") != trace2.get("model"):
        differences.append(f"Model: {trace1.get('model')} vs {trace2.get('model')}")

    if differences:
        for diff in differences:
            st.warning(diff)
    else:
        st.info("No significant differences found")


def render_compact_trace(trace_data: Dict[str, Any]) -> None:
    """
    Render a compact, single-line trace summary.

    Args:
        trace_data: Dictionary containing trace information

    Example:
        >>> trace = {
        ...     "timestamp": "2024-01-15 10:30:00",
        ...     "error_type": "RateLimitError",
        ...     "severity": "HIGH",
        ...     "model": "gpt-4",
        ...     "combined_error": "Rate limit exceeded"
        ... }
        >>> render_compact_trace(trace)

    Notes:
        - Displays trace in a single row with key info
        - Uses emoji for severity indication
        - Suitable for lists and quick scanning
    """
    severity = trace_data.get("severity", "UNKNOWN")
    emoji = ErrorClassifier.get_severity_emoji(severity)

    col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 2, 4])

    with col1:
        st.markdown(f"**{emoji}**")

    with col2:
        timestamp = trace_data.get("timestamp", "Unknown")
        st.text(str(timestamp)[:19])  # Trim to datetime without microseconds

    with col3:
        error_type = trace_data.get("error_type", "Unknown")
        st.code(error_type, language=None)

    with col4:
        model = trace_data.get("model", "Unknown")
        st.text(model)

    with col5:
        error_msg = trace_data.get("combined_error", "No message")
        # Truncate long messages
        if len(error_msg) > 50:
            error_msg = error_msg[:47] + "..."
        st.caption(error_msg)


def render_trace_table(traces_df: pd.DataFrame) -> None:
    """
    Render traces in a sortable, filterable data table.

    Args:
        traces_df: DataFrame containing trace information

    Example:
        >>> df = pd.DataFrame({
        ...     'trace_id': ['trace_1', 'trace_2'],
        ...     'timestamp': ['2024-01-15 10:30', '2024-01-15 10:35'],
        ...     'error_type': ['RateLimitError', 'TimeoutError'],
        ...     'severity': ['HIGH', 'HIGH']
        ... })
        >>> render_trace_table(df)

    Notes:
        - Provides interactive table with sorting and filtering
        - Shows all available columns
        - Useful for detailed analysis
    """
    if traces_df.empty:
        st.info("No traces available")
        return

    # Select relevant columns for display
    display_columns = [
        "trace_id",
        "timestamp",
        "error_type",
        "severity",
        "category",
        "model",
        "latency_ms",
        "total_cost",
    ]

    available_columns = [col for col in display_columns if col in traces_df.columns]

    if not available_columns:
        # Show all columns if none of the preferred ones exist
        available_columns = traces_df.columns.tolist()

    display_df = traces_df[available_columns].copy()

    # Format timestamp
    if "timestamp" in display_df.columns:
        display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Format numeric columns
    if "latency_ms" in display_df.columns:
        display_df["latency_ms"] = display_df["latency_ms"].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "N/A")

    if "total_cost" in display_df.columns:
        display_df["total_cost"] = display_df["total_cost"].apply(lambda x: f"${x:.4f}" if pd.notna(x) else "N/A")

    # Display as dataframe with column config
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

    # Display count
    st.caption(f"Showing {len(display_df)} traces")
