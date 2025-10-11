"""
Cost Analysis Query Module for Analytics Dashboard.

This module provides functions to query and analyze cost-related metrics
from the LLM generations database.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_hourly_cost_breakdown(db_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
    """
    Get hourly breakdown of total costs and request counts.

    Args:
        db_path: Path to the SQLite database file
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, returns all historical data.

    Returns:
        DataFrame with columns:
            - hour: Hour timestamp (datetime)
            - total_cost: Sum of costs for that hour (float)
            - request_count: Number of requests in that hour (int)

    Examples:
        >>> # Get all historical hourly costs
        >>> df = get_hourly_cost_breakdown("metrics.db")

        >>> # Get costs for last 7 days
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(days=7)
        >>> df = get_hourly_cost_breakdown("metrics.db", (start, end))
        >>> print(df.head())
                          hour  total_cost  request_count
        0  2024-01-01 00:00:00        0.15             10
        1  2024-01-01 01:00:00        0.23             15
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            strftime('%Y-%m-%d %H:00:00', created_at) as hour,
            COALESCE(SUM(total_cost), 0.0) as total_cost,
            COUNT(*) as request_count
        FROM generations
    """

    params = []
    if date_range:
        query += " WHERE created_at BETWEEN ? AND ?"
        params.extend([date_range[0].isoformat(), date_range[1].isoformat()])

    query += """
        GROUP BY strftime('%Y-%m-%d %H:00:00', created_at)
        ORDER BY hour ASC
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert hour to datetime
    if not df.empty:
        df["hour"] = pd.to_datetime(df["hour"])

    return df


@st.cache_data(ttl=300)
def get_budget_tracking(
    db_path: str, monthly_budget: float, date_range: Optional[Tuple[datetime, datetime]] = None
) -> Dict[str, float]:
    """
    Track spending against a monthly budget with projections.

    Args:
        db_path: Path to the SQLite database file
        monthly_budget: The monthly budget limit in dollars
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, uses current month-to-date.

    Returns:
        Dictionary with keys:
            - current_spend: Total spending in the period (float)
            - budget: The monthly budget limit (float)
            - percentage_used: Percentage of budget used (float, 0-100+)
            - days_remaining: Days remaining in the month (int)
            - projected_end_of_month: Projected total spend by end of month (float)

    Examples:
        >>> # Track current month spending against $100 budget
        >>> budget_info = get_budget_tracking("metrics.db", 100.0)
        >>> print(f"Used: ${budget_info['current_spend']:.2f}")
        >>> print(f"Projected: ${budget_info['projected_end_of_month']:.2f}")

        >>> # Track specific date range
        >>> from datetime import datetime
        >>> start = datetime(2024, 1, 1)
        >>> end = datetime(2024, 1, 31, 23, 59, 59)
        >>> budget_info = get_budget_tracking("metrics.db", 150.0, (start, end))
    """
    conn = sqlite3.connect(db_path)

    # Determine date range
    if date_range is None:
        # Use current month
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        # Calculate end of month
        if now.month == 12:
            end_of_month = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
        date_range = (start_of_month, end_of_month)

    start_date, end_date = date_range

    # Get current spending
    query = """
        SELECT COALESCE(SUM(total_cost), 0.0) as current_spend
        FROM generations
        WHERE created_at BETWEEN ? AND ?
    """

    result = pd.read_sql_query(query, conn, params=[start_date.isoformat(), datetime.now().isoformat()])
    current_spend = float(result["current_spend"].iloc[0])

    conn.close()

    # Calculate metrics
    percentage_used = (current_spend / monthly_budget * 100) if monthly_budget > 0 else 0

    # Calculate days
    now = datetime.now()
    days_elapsed = (now - start_date).days + 1
    days_in_period = (end_date - start_date).days + 1
    days_remaining = max(0, days_in_period - days_elapsed)

    # Project end of month spending (simple linear projection)
    if days_elapsed > 0:
        daily_average = current_spend / days_elapsed
        projected_end_of_month = daily_average * days_in_period
    else:
        projected_end_of_month = 0.0

    return {
        "current_spend": current_spend,
        "budget": monthly_budget,
        "percentage_used": percentage_used,
        "days_remaining": days_remaining,
        "projected_end_of_month": projected_end_of_month,
    }


@st.cache_data(ttl=300)
def get_cost_forecast(db_path: str, days_ahead: int = 7) -> pd.DataFrame:
    """
    Forecast future costs using simple linear regression on historical data.

    Args:
        db_path: Path to the SQLite database file
        days_ahead: Number of days to forecast into the future (default: 7)

    Returns:
        DataFrame with columns:
            - date: Date of prediction (datetime.date)
            - predicted_cost: Predicted cost for that day (float)

    Examples:
        >>> # Forecast next 7 days
        >>> forecast_df = get_cost_forecast("metrics.db")
        >>> print(forecast_df)
                 date  predicted_cost
        0  2024-01-15            5.23
        1  2024-01-16            5.45

        >>> # Forecast next 30 days
        >>> forecast_df = get_cost_forecast("metrics.db", days_ahead=30)
    """
    conn = sqlite3.connect(db_path)

    # Get daily historical costs
    query = """
        SELECT
            DATE(created_at) as date,
            COALESCE(SUM(total_cost), 0.0) as daily_cost
        FROM generations
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty or len(df) < 2:
        # Not enough data for forecasting, return empty DataFrame
        return pd.DataFrame(columns=["date", "predicted_cost"])

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Simple linear regression using numpy
    import numpy as np

    # Create numeric representation of dates (days since first record)
    df["days_since_start"] = (df["date"] - df["date"].min()).dt.days

    # Fit linear regression
    X = df["days_since_start"].values
    y = df["daily_cost"].values

    # Calculate slope and intercept
    A = np.vstack([X, np.ones(len(X))]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]

    # Generate forecast
    last_date = df["date"].max()
    forecast_dates = [last_date + timedelta(days=i + 1) for i in range(days_ahead)]
    last_days_since_start = df["days_since_start"].max()
    forecast_days = [last_days_since_start + i + 1 for i in range(days_ahead)]

    predicted_costs = [max(0, slope * day + intercept) for day in forecast_days]

    forecast_df = pd.DataFrame({"date": [d.date() for d in forecast_dates], "predicted_cost": predicted_costs})

    return forecast_df


@st.cache_data(ttl=300)
def get_most_expensive_requests(
    db_path: str, limit: int = 10, date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """
    Get the most expensive individual requests by total cost.

    Args:
        db_path: Path to the SQLite database file
        limit: Maximum number of requests to return (default: 10)
        date_range: Optional tuple of (start_datetime, end_datetime) to filter results.
                   If None, returns all historical data.

    Returns:
        DataFrame with columns:
            - id: Request ID (int)
            - trace_id: Trace identifier (str)
            - created_at: Timestamp of request (datetime)
            - model: Model name (str)
            - input_tokens: Number of input tokens (int)
            - output_tokens: Number of output tokens (int)
            - total_tokens: Total tokens (int)
            - total_cost: Total cost in dollars (float)
            - latency_ms: Request latency in milliseconds (float)

    Examples:
        >>> # Get top 10 most expensive requests
        >>> expensive_df = get_most_expensive_requests("metrics.db")
        >>> print(expensive_df[['model', 'total_tokens', 'total_cost']])

        >>> # Get top 20 from last 30 days
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(days=30)
        >>> expensive_df = get_most_expensive_requests(
        ...     "metrics.db",
        ...     limit=20,
        ...     date_range=(start, end)
        ... )
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            id,
            trace_id,
            created_at,
            model,
            COALESCE(input_tokens, 0) as input_tokens,
            COALESCE(output_tokens, 0) as output_tokens,
            COALESCE(total_tokens, 0) as total_tokens,
            COALESCE(total_cost, 0.0) as total_cost,
            COALESCE(latency_ms, 0.0) as latency_ms
        FROM generations
    """

    params = []
    if date_range:
        query += " WHERE created_at BETWEEN ? AND ?"
        params.extend([date_range[0].isoformat(), date_range[1].isoformat()])

    query += """
        ORDER BY total_cost DESC
        LIMIT ?
    """
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert created_at to datetime
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"])

    return df
