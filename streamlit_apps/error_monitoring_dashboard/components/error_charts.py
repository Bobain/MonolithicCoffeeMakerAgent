"""
Plotly chart creation functions for the Error Monitoring Dashboard.

This module provides reusable chart creation functions for visualizing
error data including timelines, distributions, patterns, and breakdowns.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_error_timeline(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a line chart showing error counts over time.

    Args:
        df: DataFrame with columns:
            - hour (datetime): Timestamp (hourly aggregation)
            - error_count (int): Number of errors in that hour
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with line chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'hour': pd.date_range('2024-01-01', periods=24, freq='H'),
        ...     'error_count': [5, 8, 6, 10, 7, 9, 12, 8, 6, 5, 7, 9,
        ...                     11, 8, 6, 7, 9, 10, 8, 7, 6, 5, 4, 3]
        ... })
        >>> fig = create_error_timeline(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No error data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    # Ensure hour column is datetime
    df = df.copy()
    df["hour"] = pd.to_datetime(df["hour"])

    fig = px.line(
        df,
        x="hour",
        y="error_count",
        title="Error Timeline",
        markers=True,
        color_discrete_sequence=["#dc3545"],  # Red for errors
    )

    fig.update_traces(
        mode="lines+markers",
        marker=dict(size=8),
        line=dict(width=2),
        hovertemplate="<b>Time: %{x|%Y-%m-%d %H:%M}</b><br>" + "Errors: %{y}<extra></extra>",
    )

    fig.update_layout(
        height=height,
        xaxis_title="Time",
        yaxis_title="Error Count",
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_severity_pie_chart(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a pie chart showing error distribution by severity level.

    Args:
        df: DataFrame with columns:
            - severity (str): Severity level (CRITICAL, HIGH, MEDIUM, LOW)
            - count (int): Number of errors at that severity
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with pie chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'severity': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        ...     'count': [23, 45, 67, 12]
        ... })
        >>> fig = create_severity_pie_chart(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No severity data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    # Create color mapping based on severity
    color_map = {
        "CRITICAL": "#dc3545",  # Red
        "HIGH": "#fd7e14",  # Orange
        "MEDIUM": "#ffc107",  # Yellow
        "LOW": "#28a745",  # Green
        "UNKNOWN": "#6c757d",  # Gray
    }

    colors = [color_map.get(sev, "#6c757d") for sev in df["severity"]]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["severity"],
                values=df["count"],
                marker=dict(colors=colors),
                hole=0.3,
                textposition="inside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>" + "Count: %{value}<br>" + "Percentage: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Error Distribution by Severity",
        height=height,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
    )

    return fig


def create_error_type_bar_chart(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a horizontal bar chart showing top error types.

    Args:
        df: DataFrame with columns:
            - error_type (str): Type of error
            - count (int): Number of occurrences
            - severity (str): Severity level
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with horizontal bar chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'error_type': ['RateLimitError', 'TimeoutError', 'APIConnectionError'],
        ...     'count': [45, 32, 23],
        ...     'severity': ['HIGH', 'HIGH', 'CRITICAL']
        ... })
        >>> fig = create_error_type_bar_chart(df)
    """
    if df.empty or "error_type" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No error type data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    # Sort by count
    df = df.sort_values("count", ascending=True)

    # Create color mapping based on severity
    color_map = {"CRITICAL": "#dc3545", "HIGH": "#fd7e14", "MEDIUM": "#ffc107", "LOW": "#28a745", "UNKNOWN": "#6c757d"}

    colors = [color_map.get(sev, "#6c757d") for sev in df["severity"]]

    fig = go.Figure(
        data=[
            go.Bar(
                x=df["count"],
                y=df["error_type"],
                orientation="h",
                marker=dict(color=colors),
                hovertemplate="<b>%{y}</b><br>" + "Count: %{x}<br>" + "<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Top Error Types",
        xaxis_title="Error Count",
        yaxis_title="Error Type",
        height=height,
        showlegend=False,
        yaxis=dict(tickangle=0),
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_model_error_comparison(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a bar chart comparing error counts across models.

    Args:
        df: DataFrame with columns:
            - model (str): Model name
            - error_count (int): Number of errors
            - error_percentage (float): Percentage of errors
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with bar chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'model': ['gpt-4', 'gpt-3.5-turbo', 'claude-3'],
        ...     'error_count': [45, 78, 32],
        ...     'error_percentage': [2.3, 3.1, 1.8]
        ... })
        >>> fig = create_model_error_comparison(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No model error data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    fig = px.bar(
        df,
        x="model",
        y="error_count",
        title="Error Count by Model",
        color="model",
        color_discrete_sequence=px.colors.qualitative.Bold,
        text="error_count",
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>" + "Errors: %{y}<br>" + "<extra></extra>",
    )

    fig.update_layout(
        height=height,
        xaxis_title="Model",
        yaxis_title="Error Count",
        showlegend=False,
        xaxis=dict(tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_failure_rate_chart(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a bar chart showing failure rates by model.

    Args:
        df: DataFrame with columns:
            - model (str): Model name
            - failure_rate (float): Failure rate as percentage
            - error_count (int): Number of errors
            - total_count (int): Total requests
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with bar chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'model': ['gpt-4', 'gpt-3.5-turbo'],
        ...     'failure_rate': [2.3, 3.1],
        ...     'error_count': [45, 78],
        ...     'total_count': [1956, 2516]
        ... })
        >>> fig = create_failure_rate_chart(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No failure rate data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    # Sort by failure rate
    df = df.sort_values("failure_rate", ascending=False)

    fig = px.bar(
        df,
        x="model",
        y="failure_rate",
        title="Model Failure Rates",
        color="failure_rate",
        color_continuous_scale=["#28a745", "#ffc107", "#fd7e14", "#dc3545"],
        text="failure_rate",
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>" + "Failure Rate: %{y:.2f}%<br>" + "<extra></extra>",
    )

    fig.update_layout(
        height=height,
        xaxis_title="Model",
        yaxis_title="Failure Rate (%)",
        showlegend=False,
        xaxis=dict(tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_error_heatmap(df: pd.DataFrame, height: int = 500) -> go.Figure:
    """
    Create a heatmap showing error patterns by hour and day of week.

    Args:
        df: DataFrame with columns:
            - hour (int): Hour of day (0-23)
            - day_of_week (int): Day of week (0-6, where 0=Sunday)
            - error_count (int): Number of errors

    Returns:
        Plotly Figure object with heatmap

    Examples:
        >>> df = pd.DataFrame({
        ...     'hour': [9, 10, 11, 9, 10, 11],
        ...     'day_of_week': [1, 1, 1, 2, 2, 2],
        ...     'error_count': [5, 8, 6, 7, 9, 5]
        ... })
        >>> fig = create_error_heatmap(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No pattern data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    # Map day numbers to names
    day_map = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

    df = df.copy()
    df["day_name"] = df["day_of_week"].map(day_map)

    # Pivot for heatmap
    pivot_df = df.pivot_table(index="day_name", columns="hour", values="error_count", fill_value=0)

    # Reorder days (Monday first)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot_df = pivot_df.reindex([d for d in day_order if d in pivot_df.index])

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale="Reds",
            hovertemplate="<b>%{y}</b><br>" + "Hour: %{x}:00<br>" + "Errors: %{z}<extra></extra>",
            colorbar=dict(title="Error Count"),
        )
    )

    fig.update_layout(
        title="Error Heatmap by Hour and Day of Week",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=height,
        xaxis=dict(tickmode="linear", tick0=0, dtick=1, side="bottom"),
        yaxis=dict(autorange="reversed"),
    )

    return fig


def create_category_pie_chart(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a pie chart showing error distribution by category.

    Args:
        df: DataFrame with columns:
            - category (str): Error category
            - count (int): Number of errors in that category
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with pie chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'category': ['API Limits', 'Network', 'Input Validation'],
        ...     'count': [45, 32, 23]
        ... })
        >>> fig = create_category_pie_chart(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No category data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    fig = px.pie(
        df,
        values="count",
        names="category",
        title="Error Distribution by Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.3,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>" + "Count: %{value}<br>" + "Percentage: %{percent}<extra></extra>",
    )

    fig.update_layout(
        height=height, showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )

    return fig


def create_stacked_severity_timeline(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a stacked area chart showing error severity over time.

    Args:
        df: DataFrame with columns:
            - timestamp (datetime): Time of error
            - severity (str): Severity level
            - count (int): Number of errors (aggregated)
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with stacked area chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'timestamp': pd.date_range('2024-01-01', periods=24, freq='H').repeat(3),
        ...     'severity': ['CRITICAL', 'HIGH', 'MEDIUM'] * 24,
        ...     'count': [2, 5, 8] * 24
        ... })
        >>> fig = create_stacked_severity_timeline(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No timeline data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Color mapping
    color_map = {
        "CRITICAL": "#dc3545",
        "HIGH": "#fd7e14",
        "MEDIUM": "#ffc107",
        "LOW": "#28a745",
    }

    fig = go.Figure()

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        severity_df = df[df["severity"] == severity]
        if not severity_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=severity_df["timestamp"],
                    y=severity_df["count"],
                    mode="lines",
                    name=severity,
                    stackgroup="one",
                    line=dict(width=0.5, color=color_map.get(severity, "#6c757d")),
                    fillcolor=color_map.get(severity, "#6c757d"),
                    hovertemplate="<b>%{fullData.name}</b><br>"
                    + "Time: %{x|%Y-%m-%d %H:%M}<br>"
                    + "Count: %{y}<extra></extra>",
                )
            )

    fig.update_layout(
        title="Error Severity Timeline (Stacked)",
        xaxis_title="Time",
        yaxis_title="Error Count",
        height=height,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig
