"""
Metrics rendering components for the Analytics Dashboard.

This module provides functions to render various metric visualizations
including metric cards, delta metrics, and progress bars.
"""

import streamlit as st
from typing import Dict, Any, Optional, Literal


def render_metric_cards(stats_dict: Dict[str, Any]) -> None:
    """
    Render four metric cards in columns displaying key statistics.

    Args:
        stats_dict: Dictionary containing the following keys:
            - total_cost (float): Total cost in dollars
            - total_tokens (int): Total number of tokens used
            - total_requests (int): Total number of API requests
            - avg_latency (float): Average latency in milliseconds

    Example:
        >>> stats = {
        ...     "total_cost": 45.67,
        ...     "total_tokens": 1234567,
        ...     "total_requests": 890,
        ...     "avg_latency": 234.56
        ... }
        >>> render_metric_cards(stats)
        # Renders 4 columns with formatted metrics

    Notes:
        - Cost is formatted with $ symbol and 2 decimal places
        - Tokens are formatted with K/M suffixes for readability
        - Requests are formatted with commas for thousands
        - Latency is formatted with 1 decimal place and 'ms' suffix
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cost = stats_dict.get("total_cost", 0.0)
        st.metric(label="Total Cost", value=f"${cost:,.2f}")

    with col2:
        tokens = stats_dict.get("total_tokens", 0)
        formatted_tokens = _format_large_number(tokens)
        st.metric(label="Total Tokens", value=formatted_tokens)

    with col3:
        requests = stats_dict.get("total_requests", 0)
        st.metric(label="Total Requests", value=f"{requests:,}")

    with col4:
        latency = stats_dict.get("avg_latency", 0.0)
        st.metric(label="Avg Latency", value=f"{latency:.1f} ms")


def render_delta_metric(
    label: str, value: Any, delta: Optional[Any] = None, delta_color: Literal["normal", "inverse", "off"] = "normal"
) -> None:
    """
    Render a single metric card with an optional delta indicator.

    Args:
        label: The label/title for the metric
        value: The current value to display
        delta: The change value to show (can be numeric or string)
        delta_color: How to color the delta indicator:
            - "normal": green for positive, red for negative
            - "inverse": red for positive, green for negative
            - "off": no color applied

    Example:
        >>> render_delta_metric(
        ...     label="API Success Rate",
        ...     value="98.5%",
        ...     delta="+2.1%",
        ...     delta_color="normal"
        ... )
        # Renders a metric card showing 98.5% with green +2.1% indicator

        >>> render_delta_metric(
        ...     label="Error Rate",
        ...     value="1.5%",
        ...     delta="-0.3%",
        ...     delta_color="inverse"
        ... )
        # Renders error rate with green -0.3% (lower is better)

    Notes:
        - Delta can be numeric or string with formatting
        - Use delta_color="inverse" for metrics where lower is better
        - Use delta_color="off" to display delta without color
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def render_progress_bar(
    label: str, current: float, total: float, format_as: Literal["percentage", "fraction", "both"] = "percentage"
) -> None:
    """
    Render a progress bar with label and formatted display.

    Args:
        label: The label to display above the progress bar
        current: The current value (numerator)
        total: The total/maximum value (denominator)
        format_as: How to display the progress:
            - "percentage": Show as percentage (e.g., "75%")
            - "fraction": Show as fraction (e.g., "75 / 100")
            - "both": Show both formats (e.g., "75 / 100 (75%)")

    Example:
        >>> render_progress_bar(
        ...     label="API Quota Usage",
        ...     current=7500,
        ...     total=10000,
        ...     format_as="both"
        ... )
        # Renders: "API Quota Usage"
        #          [███████████████░░░░░] 7,500 / 10,000 (75%)

        >>> render_progress_bar(
        ...     label="Task Completion",
        ...     current=45,
        ...     total=60,
        ...     format_as="percentage"
        ... )
        # Renders: "Task Completion"
        #          [███████████████░░░░░] 75%

    Notes:
        - Progress is clamped between 0 and 1
        - Handles division by zero gracefully
        - Numbers in "fraction" and "both" modes are formatted with commas
    """
    # Calculate progress (0 to 1)
    if total == 0:
        progress = 0.0
        percentage = 0.0
    else:
        progress = min(max(current / total, 0.0), 1.0)
        percentage = progress * 100

    # Format display text
    if format_as == "percentage":
        display_text = f"{percentage:.1f}%"
    elif format_as == "fraction":
        display_text = f"{current:,.0f} / {total:,.0f}"
    else:  # both
        display_text = f"{current:,.0f} / {total:,.0f} ({percentage:.1f}%)"

    # Render label and progress bar
    st.text(label)
    st.progress(progress, text=display_text)


def _format_large_number(num: int) -> str:
    """
    Format large numbers with K/M/B suffixes for readability.

    Args:
        num: The number to format

    Returns:
        Formatted string with appropriate suffix

    Example:
        >>> _format_large_number(1234)
        '1.2K'
        >>> _format_large_number(1234567)
        '1.2M'
        >>> _format_large_number(1234567890)
        '1.2B'
        >>> _format_large_number(123)
        '123'
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)
