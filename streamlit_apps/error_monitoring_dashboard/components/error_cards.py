"""
Metric card components for the Error Monitoring Dashboard.

This module provides functions to render various error metric visualizations
including summary metric cards, delta metrics, and severity indicators.
"""

import streamlit as st
from typing import Dict, Any, Optional, Literal

from streamlit_apps.error_monitoring_dashboard.utils.error_classifier import ErrorClassifier


def render_error_summary_cards(stats_dict: Dict[str, Any]) -> None:
    """
    Render four metric cards in columns displaying key error statistics.

    Args:
        stats_dict: Dictionary containing the following keys:
            - total_errors (int): Total number of errors
            - error_rate (float): Error rate as decimal (e.g., 0.05 for 5%)
            - critical_errors (int): Number of critical severity errors
            - total_traces (int): Total number of traces processed

    Example:
        >>> stats = {
        ...     "total_errors": 145,
        ...     "error_rate": 0.0342,
        ...     "critical_errors": 23,
        ...     "total_traces": 4237
        ... }
        >>> render_error_summary_cards(stats)
        # Renders 4 columns with formatted error metrics

    Notes:
        - Error rate is formatted as percentage with 2 decimal places
        - All counts are formatted with commas for thousands
        - Uses red color scheme for critical metrics
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_errors = stats_dict.get("total_errors", 0)
        st.metric(label="Total Errors", value=f"{total_errors:,}")

    with col2:
        error_rate = stats_dict.get("error_rate", 0.0)
        st.metric(label="Error Rate", value=f"{error_rate * 100:.2f}%")

    with col3:
        critical_errors = stats_dict.get("critical_errors", 0)
        st.metric(label="Critical Errors", value=f"{critical_errors:,}")

    with col4:
        total_traces = stats_dict.get("total_traces", 0)
        st.metric(label="Total Traces", value=f"{total_traces:,}")


def render_severity_metric_cards(severity_counts: Dict[str, int]) -> None:
    """
    Render metric cards for each severity level with color-coded indicators.

    Args:
        severity_counts: Dictionary mapping severity levels to counts
            Example: {"CRITICAL": 23, "HIGH": 45, "MEDIUM": 67, "LOW": 12}

    Example:
        >>> counts = {"CRITICAL": 23, "HIGH": 45, "MEDIUM": 67, "LOW": 12}
        >>> render_severity_metric_cards(counts)
        # Renders 4 columns showing error counts by severity

    Notes:
        - Displays severity levels in order: CRITICAL, HIGH, MEDIUM, LOW
        - Each metric shows emoji indicator based on severity
        - Missing severities default to 0
    """
    # Define severity order
    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    cols = st.columns(4)

    for idx, severity in enumerate(severities):
        with cols[idx]:
            count = severity_counts.get(severity, 0)
            emoji = ErrorClassifier.get_severity_emoji(severity)
            st.metric(label=f"{emoji} {severity}", value=f"{count:,}")


def render_error_delta_metric(
    label: str, value: Any, delta: Optional[Any] = None, delta_color: Literal["normal", "inverse", "off"] = "inverse"
) -> None:
    """
    Render a single error metric card with an optional delta indicator.

    Args:
        label: The label/title for the metric
        value: The current value to display
        delta: The change value to show (can be numeric or string)
        delta_color: How to color the delta indicator:
            - "normal": green for positive, red for negative
            - "inverse": red for positive, green for negative (default for errors)
            - "off": no color applied

    Example:
        >>> render_error_delta_metric(
        ...     label="Error Rate",
        ...     value="3.4%",
        ...     delta="+0.5%",
        ...     delta_color="inverse"
        ... )
        # Renders an error rate metric with red +0.5% (higher is worse)

        >>> render_error_delta_metric(
        ...     label="Resolution Time",
        ...     value="2.3 hrs",
        ...     delta="-0.5 hrs",
        ...     delta_color="inverse"
        ... )
        # Renders resolution time with green -0.5 hrs (lower is better)

    Notes:
        - Delta can be numeric or string with formatting
        - Default is delta_color="inverse" since lower errors are better
        - Use delta_color="normal" for recovery/resolution metrics
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def render_model_error_cards(model_stats: Dict[str, Dict[str, Any]]) -> None:
    """
    Render error statistics cards for each model.

    Args:
        model_stats: Dictionary mapping model names to their error statistics
            Example: {
                "gpt-4": {"errors": 45, "failure_rate": 0.023},
                "gpt-3.5-turbo": {"errors": 78, "failure_rate": 0.031}
            }

    Example:
        >>> stats = {
        ...     "gpt-4": {"errors": 45, "failure_rate": 0.023},
        ...     "gpt-3.5-turbo": {"errors": 78, "failure_rate": 0.031}
        ... }
        >>> render_model_error_cards(stats)
        # Renders cards showing error stats per model

    Notes:
        - Creates columns dynamically based on number of models
        - Displays error count and failure rate for each model
        - Sorts models by error count (descending)
    """
    if not model_stats:
        st.info("No model error data available")
        return

    # Sort by error count
    sorted_models = sorted(model_stats.items(), key=lambda x: x[1].get("errors", 0), reverse=True)

    # Create columns for top models (up to 4)
    num_cols = min(len(sorted_models), 4)
    cols = st.columns(num_cols)

    for idx, (model, stats) in enumerate(sorted_models[:num_cols]):
        with cols[idx]:
            errors = stats.get("errors", 0)
            failure_rate = stats.get("failure_rate", 0.0)

            st.metric(
                label=model, value=f"{errors:,} errors", delta=f"{failure_rate * 100:.2f}% rate", delta_color="off"
            )


def render_category_breakdown(category_counts: Dict[str, int]) -> None:
    """
    Render a compact breakdown of errors by category.

    Args:
        category_counts: Dictionary mapping error categories to counts
            Example: {
                "API Limits": 45,
                "Network": 23,
                "Input Validation": 67
            }

    Example:
        >>> counts = {
        ...     "API Limits": 45,
        ...     "Network": 23,
        ...     "Input Validation": 67
        ... }
        >>> render_category_breakdown(counts)
        # Renders category breakdown with progress bars

    Notes:
        - Displays categories sorted by count (descending)
        - Shows count and percentage for each category
        - Uses progress bars for visual representation
    """
    if not category_counts:
        st.info("No category data available")
        return

    total = sum(category_counts.values())

    # Sort by count
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    st.markdown("**Error Categories**")

    for category, count in sorted_categories:
        percentage = (count / total * 100) if total > 0 else 0

        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(category)
            st.progress(count / total if total > 0 else 0)
        with col2:
            st.metric(label="", value=f"{count:,}")
            st.caption(f"{percentage:.1f}%")


def render_status_indicator(
    status: Literal["healthy", "warning", "critical", "unknown"], label: str = "System Status"
) -> None:
    """
    Render a status indicator with color-coded badge.

    Args:
        status: Current system status
        label: Label to display above status (default: "System Status")

    Example:
        >>> render_status_indicator("healthy", "API Health")
        # Renders: API Health [🟢 Healthy]

        >>> render_status_indicator("critical", "Error Rate")
        # Renders: Error Rate [🔴 Critical]

    Notes:
        - healthy: Green badge, low error rates
        - warning: Yellow badge, elevated error rates
        - critical: Red badge, high error rates
        - unknown: Gray badge, insufficient data
    """
    status_config = {
        "healthy": {"emoji": "🟢", "text": "Healthy", "color": "green"},
        "warning": {"emoji": "🟡", "text": "Warning", "color": "orange"},
        "critical": {"emoji": "🔴", "text": "Critical", "color": "red"},
        "unknown": {"emoji": "⚪", "text": "Unknown", "color": "gray"},
    }

    config = status_config.get(status, status_config["unknown"])

    st.markdown(f"**{label}**")
    st.markdown(
        f"<span style='font-size: 24px;'>{config['emoji']} "
        f"<span style='color: {config['color']};'>{config['text']}</span></span>",
        unsafe_allow_html=True,
    )


def render_time_since_last_error(minutes: Optional[int]) -> None:
    """
    Render a metric showing time since the last error occurred.

    Args:
        minutes: Minutes since last error, or None if no errors

    Example:
        >>> render_time_since_last_error(45)
        # Renders: "Last Error: 45 minutes ago"

        >>> render_time_since_last_error(None)
        # Renders: "Last Error: No errors recorded"

    Notes:
        - Formats as hours if > 60 minutes
        - Formats as days if > 24 hours
        - Shows "just now" if < 1 minute
    """
    if minutes is None:
        st.metric(label="Last Error", value="No errors")
        return

    if minutes < 1:
        time_str = "Just now"
    elif minutes < 60:
        time_str = f"{minutes} min ago"
    elif minutes < 1440:  # 24 hours
        hours = minutes / 60
        time_str = f"{hours:.1f} hrs ago"
    else:
        days = minutes / 1440
        time_str = f"{days:.1f} days ago"

    st.metric(label="Last Error", value=time_str)
