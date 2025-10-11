"""
Data processing utilities for Streamlit Analytics Dashboard.

This module provides functions for validating, cleaning, and transforming
DataFrames for use in analytics dashboards, including time series operations.
"""

import pandas as pd
from typing import List, Optional


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validate that a DataFrame contains all required columns.

    Checks if a DataFrame is valid and contains all specified required columns.
    Returns a tuple with validation status and an optional error message.

    Args:
        df: The pandas DataFrame to validate. Can be None.
        required_columns: List of column names that must be present in the DataFrame.

    Returns:
        Tuple of (is_valid, error_message):
        - is_valid: True if validation passes, False otherwise
        - error_message: None if valid, descriptive error string if invalid

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> validate_dataframe(df, ['A', 'B'])
        (True, None)

        >>> validate_dataframe(df, ['A', 'C'])
        (False, "Missing required columns: C")

        >>> validate_dataframe(None, ['A'])
        (False, "DataFrame is None or invalid")

        >>> empty_df = pd.DataFrame()
        >>> validate_dataframe(empty_df, ['A'])
        (False, "DataFrame is empty")

        >>> validate_dataframe(df, [])
        (True, None)

    Note:
        - Returns False if DataFrame is None
        - Returns False if DataFrame is empty (has no rows)
        - Empty required_columns list always passes validation
        - Error messages list all missing columns
    """
    # Check if DataFrame is None or invalid
    if df is None or not isinstance(df, pd.DataFrame):
        return False, "DataFrame is None or invalid"

    # Check if DataFrame is empty
    if df.empty:
        return False, "DataFrame is empty"

    # If no required columns specified, validation passes
    if not required_columns:
        return True, None

    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        error_msg = f"Missing required columns: {', '.join(missing_columns)}"
        return False, error_msg

    return True, None


def fill_missing_dates(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """
    Fill missing dates in a time series DataFrame.

    Takes a DataFrame with a date column and fills in any missing dates
    in the range, inserting rows with NaN values for other columns.
    Useful for ensuring continuous time series data.

    Args:
        df: The pandas DataFrame containing time series data. Can be empty or None.
        date_column: Name of the column containing date/datetime values.
                     Defaults to 'date'.

    Returns:
        New DataFrame with all dates filled in the range [min_date, max_date].
        Returns empty DataFrame if input is None or empty.
        Returns original DataFrame if date_column doesn't exist.

    Examples:
        >>> import pandas as pd
        >>> from datetime import datetime
        >>> df = pd.DataFrame({
        ...     'date': [datetime(2025, 1, 1), datetime(2025, 1, 3)],
        ...     'value': [10, 20]
        ... })
        >>> result = fill_missing_dates(df, 'date')
        >>> len(result)
        3
        >>> result['date'].tolist()
        [datetime(2025, 1, 1), datetime(2025, 1, 2), datetime(2025, 1, 3)]

        >>> # Handle empty DataFrame
        >>> empty_df = pd.DataFrame()
        >>> fill_missing_dates(empty_df, 'date')
        Empty DataFrame

        >>> # Handle missing column
        >>> df2 = pd.DataFrame({'other': [1, 2]})
        >>> result = fill_missing_dates(df2, 'date')
        >>> result.equals(df2)
        True

    Note:
        - Converts date_column to datetime if not already
        - Preserves all existing columns
        - New rows have NaN for non-date columns
        - Sorts result by date
        - Handles date and datetime types
        - Returns copy of original if date_column missing
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        return pd.DataFrame()

    # Check if date column exists
    if date_column not in df.columns:
        return df.copy()

    # Create a copy to avoid modifying original
    result_df = df.copy()

    try:
        # Convert date column to datetime if not already
        result_df[date_column] = pd.to_datetime(result_df[date_column])

        # Get the min and max dates
        min_date = result_df[date_column].min()
        max_date = result_df[date_column].max()

        # Handle case where min_date == max_date (single date)
        if min_date == max_date:
            return result_df

        # Create a complete date range
        date_range = pd.date_range(start=min_date, end=max_date, freq="D")

        # Create a DataFrame with the complete date range
        complete_dates = pd.DataFrame({date_column: date_range})

        # Merge with original data, keeping all dates
        result_df = complete_dates.merge(result_df, on=date_column, how="left")

        # Sort by date
        result_df = result_df.sort_values(by=date_column).reset_index(drop=True)

        return result_df

    except (ValueError, TypeError, KeyError):
        # If any error occurs during processing, return original DataFrame
        return df.copy()


def aggregate_by_period(
    df: pd.DataFrame, period: str = "day", date_column: str = "date", agg_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Aggregate DataFrame data by time period.

    Groups data by specified time period (day, week, month, quarter, year)
    and aggregates numeric columns using sum. Non-numeric columns are excluded.

    Args:
        df: The pandas DataFrame containing time series data. Can be empty or None.
        period: Time period for aggregation. Options:
                'day' (default), 'week', 'month', 'quarter', 'year'.
        date_column: Name of the column containing date/datetime values.
                     Defaults to 'date'.
        agg_columns: Optional list of specific columns to aggregate.
                    If None, aggregates all numeric columns.

    Returns:
        New DataFrame aggregated by the specified period with date as index.
        Returns empty DataFrame if input is None or empty.
        Returns original DataFrame if date_column doesn't exist.

    Examples:
        >>> import pandas as pd
        >>> from datetime import datetime
        >>> df = pd.DataFrame({
        ...     'date': [datetime(2025, 1, 1), datetime(2025, 1, 2),
        ...              datetime(2025, 1, 8), datetime(2025, 1, 9)],
        ...     'value': [10, 20, 30, 40],
        ...     'count': [1, 2, 3, 4]
        ... })
        >>> result = aggregate_by_period(df, period='week', date_column='date')
        >>> len(result)
        2

        >>> # Aggregate by month
        >>> result = aggregate_by_period(df, period='month')
        >>> len(result)
        1

        >>> # Aggregate specific columns
        >>> result = aggregate_by_period(df, period='day', agg_columns=['value'])
        >>> 'count' not in result.columns
        True

        >>> # Handle empty DataFrame
        >>> empty_df = pd.DataFrame()
        >>> aggregate_by_period(empty_df, period='day')
        Empty DataFrame

    Note:
        - Converts date_column to datetime if not already
        - Aggregates using sum() for numeric columns
        - Period options map to pandas resample frequencies:
          * 'day' -> 'D', 'week' -> 'W', 'month' -> 'M',
          * 'quarter' -> 'Q', 'year' -> 'Y'
        - Returns DataFrame with date as index
        - Invalid period defaults to 'day'
        - Non-numeric columns are automatically excluded
    """
    # Handle None or empty DataFrame
    if df is None or df.empty:
        return pd.DataFrame()

    # Check if date column exists
    if date_column not in df.columns:
        return df.copy()

    # Create a copy to avoid modifying original
    result_df = df.copy()

    try:
        # Convert date column to datetime if not already
        result_df[date_column] = pd.to_datetime(result_df[date_column])

        # Set date column as index for resampling
        result_df = result_df.set_index(date_column)

        # Map period to pandas frequency
        period_map = {"day": "D", "week": "W", "month": "M", "quarter": "Q", "year": "Y"}

        # Get frequency, default to day if invalid
        freq = period_map.get(period.lower(), "D")

        # Determine columns to aggregate
        if agg_columns is not None:
            # Use specified columns (filter out non-existent ones)
            cols_to_agg = [col for col in agg_columns if col in result_df.columns]
        else:
            # Use all numeric columns
            cols_to_agg = result_df.select_dtypes(include=["number"]).columns.tolist()

        # If no columns to aggregate, return empty DataFrame with date index
        if not cols_to_agg:
            return pd.DataFrame(index=result_df.resample(freq).asfreq().index)

        # Select only columns to aggregate
        result_df = result_df[cols_to_agg]

        # Resample and aggregate
        aggregated = result_df.resample(freq).sum()

        # Reset index to make date a column again
        aggregated = aggregated.reset_index()

        return aggregated

    except (ValueError, TypeError, KeyError):
        # If any error occurs during processing, return original DataFrame
        return df.copy()
