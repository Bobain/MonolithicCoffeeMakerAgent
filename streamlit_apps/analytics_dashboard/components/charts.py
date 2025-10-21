"""
Plotly chart creation functions for the Analytics Dashboard.

This module provides reusable chart creation functions for visualizing
API analytics data including costs, token usage, latency, and temporal patterns.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_cost_breakdown_pie(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a pie chart showing cost distribution across models.

    Args:
        df: DataFrame with columns:
            - model (str): Model name
            - total_cost (float): Total cost for the model
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with pie chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'model': ['gpt-4', 'gpt-3.5-turbo'],
        ...     'total_cost': [150.25, 45.80]
        ... })
        >>> fig = create_cost_breakdown_pie(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
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
        values="total_cost",
        names="model",
        title="Cost Breakdown by Model",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.3,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>" + "Cost: $%{value:.2f}<br>" + "Percentage: %{percent}<extra></extra>",
    )

    fig.update_layout(
        height=height, showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )

    return fig


def create_cost_trend_line(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a line chart showing cost trends over time.

    Args:
        df: DataFrame with columns:
            - date (datetime): Date of the cost
            - total_cost (float): Total cost for the date
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with line chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'date': pd.date_range('2024-01-01', periods=7),
        ...     'total_cost': [10.5, 12.3, 11.8, 15.2, 14.5, 16.1, 13.9]
        ... })
        >>> fig = create_cost_trend_line(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    # Ensure date column is datetime
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    fig = px.line(
        df, x="date", y="total_cost", title="Cost Trend Over Time", markers=True, color_discrete_sequence=["#1f77b4"]
    )

    fig.update_traces(
        mode="lines+markers",
        marker=dict(size=8),
        line=dict(width=2),
        hovertemplate="<b>Date: %{x|%Y-%m-%d}</b><br>" + "Cost: $%{y:.2f}<extra></extra>",
    )

    fig.update_layout(
        height=height,
        xaxis_title="Date",
        yaxis_title="Total Cost ($)",
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_model_comparison_bar(
    df: pd.DataFrame, metric_column: str = "total_cost", metric_label: str = "Total Cost ($)", height: int = 400
) -> go.Figure:
    """
    Create a bar chart comparing models across a metric.

    Args:
        df: DataFrame with columns:
            - model (str): Model name
            - metric_column (str): Column name for the metric to compare
        metric_column: Name of the column to use for comparison (default: 'total_cost')
        metric_label: Label for the metric axis (default: 'Total Cost ($)')
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with bar chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'model': ['gpt-4', 'gpt-3.5-turbo', 'claude-3'],
        ...     'total_cost': [150.25, 45.80, 89.50],
        ...     'request_count': [1200, 3500, 2100]
        ... })
        >>> fig = create_model_comparison_bar(df, 'request_count', 'Requests')
    """
    if df.empty or metric_column not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
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
        y=metric_column,
        title=f"Model Comparison: {metric_label}",
        color="model",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>" + f"{metric_label}: %{{y:,.2f}}<extra></extra>")

    fig.update_layout(
        height=height,
        xaxis_title="Model",
        yaxis_title=metric_label,
        showlegend=False,
        xaxis=dict(tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_token_usage_stacked_bar(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a stacked bar chart showing input and output token usage by model.

    Args:
        df: DataFrame with columns:
            - model (str): Model name
            - input_tokens (int): Number of input tokens
            - output_tokens (int): Number of output tokens
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with stacked bar chart

    Examples:
        >>> df = pd.DataFrame({
        ...     'model': ['gpt-4', 'gpt-3.5-turbo'],
        ...     'input_tokens': [50000, 120000],
        ...     'output_tokens': [30000, 80000]
        ... })
        >>> fig = create_token_usage_stacked_bar(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Input Tokens",
            x=df["model"],
            y=df["input_tokens"],
            marker_color="#3498db",
            hovertemplate="<b>%{x}</b><br>" + "Input Tokens: %{y:,}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Output Tokens",
            x=df["model"],
            y=df["output_tokens"],
            marker_color="#e74c3c",
            hovertemplate="<b>%{x}</b><br>" + "Output Tokens: %{y:,}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="stack",
        title="Token Usage by Model (Input vs Output)",
        xaxis_title="Model",
        yaxis_title="Token Count",
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_latency_distribution_box(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a box plot showing latency distribution across models.

    Args:
        df: DataFrame with columns:
            - model (str): Model name
            - latency_ms (float): Latency in milliseconds
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with box plot

    Examples:
        >>> df = pd.DataFrame({
        ...     'model': ['gpt-4'] * 10 + ['gpt-3.5-turbo'] * 10,
        ...     'latency_ms': [100, 120, 110, 115, 125, 105, 130, 108, 122, 118,
        ...                    80, 85, 75, 90, 82, 88, 78, 84, 86, 81]
        ... })
        >>> fig = create_latency_distribution_box(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    fig = px.box(
        df,
        x="model",
        y="latency_ms",
        title="Latency Distribution by Model",
        color="model",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        points="outliers",
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>" + "Latency: %{y:.2f} ms<br>" + "<extra></extra>")

    fig.update_layout(
        height=height,
        xaxis_title="Model",
        yaxis_title="Latency (ms)",
        showlegend=False,
        xaxis=dict(tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
    )

    return fig


def create_heatmap_hourly_usage(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create a heatmap showing request patterns by hour and day of week.

    Args:
        df: DataFrame with columns:
            - hour (int): Hour of day (0-23)
            - day_of_week (str or int): Day of week (Monday-Sunday or 0-6)
            - request_count (int): Number of requests
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with heatmap

    Examples:
        >>> df = pd.DataFrame({
        ...     'hour': [9, 10, 11, 9, 10, 11],
        ...     'day_of_week': ['Monday', 'Monday', 'Monday',
        ...                     'Tuesday', 'Tuesday', 'Tuesday'],
        ...     'request_count': [50, 75, 60, 55, 80, 65]
        ... })
        >>> fig = create_heatmap_hourly_usage(df)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=height)
        return fig

    # Convert day_of_week to consistent format
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    df = df.copy()

    # If day_of_week is numeric, convert to day names
    if df["day_of_week"].dtype in ["int64", "int32"]:
        day_map = {i: day_order[i] for i in range(7)}
        df["day_of_week"] = df["day_of_week"].map(day_map)

    # Pivot the data for heatmap
    pivot_df = df.pivot_table(index="day_of_week", columns="hour", values="request_count", fill_value=0)

    # Reorder rows by day of week
    pivot_df = pivot_df.reindex([d for d in day_order if d in pivot_df.index])

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale="YlOrRd",
            hovertemplate="<b>%{y}</b><br>" + "Hour: %{x}:00<br>" + "Requests: %{z:,}<extra></extra>",
            colorbar=dict(title="Request Count"),
        )
    )

    fig.update_layout(
        title="Request Heatmap by Hour and Day of Week",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=height,
        xaxis=dict(tickmode="linear", tick0=0, dtick=1, side="bottom"),
        yaxis=dict(autorange="reversed"),
    )

    return fig
