"""
Formatting utilities for Streamlit Analytics Dashboard.

This module provides functions for formatting numbers, currencies, percentages,
and datetime objects in a human-readable format suitable for display in dashboards.
"""

from datetime import datetime
from typing import Optional, Union


def format_currency(value: Optional[Union[int, float]]) -> str:
    """
    Format a numeric value as US currency (USD).

    Converts a numeric value to a currency string with dollar sign and two
    decimal places. Handles negative values, None, and edge cases.

    Args:
        value: The numeric value to format. Can be int, float, or None.

    Returns:
        Formatted currency string (e.g., "$1,234.56", "-$50.00", "$0.00").
        Returns "$0.00" if value is None.

    Examples:
        >>> format_currency(1234.567)
        '$1,234.57'

        >>> format_currency(-50)
        '-$50.00'

        >>> format_currency(None)
        '$0.00'

        >>> format_currency(0)
        '$0.00'

        >>> format_currency(1000000)
        '$1,000,000.00'

    Note:
        - Uses thousands separator (comma)
        - Always shows 2 decimal places
        - Negative values have minus sign before dollar sign
        - None values default to $0.00
    """
    if value is None:
        return "$0.00"

    try:
        # Convert to float to handle both int and float
        num_value = float(value)

        # Handle negative values
        if num_value < 0:
            return f"-${abs(num_value):,.2f}"

        return f"${num_value:,.2f}"

    except (ValueError, TypeError):
        return "$0.00"


def format_number(value: Optional[Union[int, float]]) -> str:
    """
    Format a numeric value with K/M/B suffixes for large numbers.

    Converts large numbers to a compact representation using suffixes:
    - K for thousands (1,000+)
    - M for millions (1,000,000+)
    - B for billions (1,000,000,000+)

    Args:
        value: The numeric value to format. Can be int, float, or None.

    Returns:
        Formatted number string with suffix (e.g., "1.5K", "2.3M", "1.2B").
        Returns "0" if value is None.

    Examples:
        >>> format_number(1500)
        '1.5K'

        >>> format_number(2300000)
        '2.3M'

        >>> format_number(1234567890)
        '1.2B'

        >>> format_number(999)
        '999'

        >>> format_number(None)
        '0'

        >>> format_number(-5000)
        '-5.0K'

        >>> format_number(0)
        '0'

    Note:
        - Numbers under 1,000 display without suffix
        - Shows one decimal place for suffixed numbers
        - Handles negative values with minus sign prefix
        - None values default to "0"
    """
    if value is None:
        return "0"

    try:
        # Convert to float to handle both int and float
        num_value = float(value)

        # Handle negative values
        is_negative = num_value < 0
        abs_value = abs(num_value)

        # Format based on magnitude
        if abs_value >= 1_000_000_000:
            formatted = f"{abs_value / 1_000_000_000:.1f}B"
        elif abs_value >= 1_000_000:
            formatted = f"{abs_value / 1_000_000:.1f}M"
        elif abs_value >= 1_000:
            formatted = f"{abs_value / 1_000:.1f}K"
        else:
            # For numbers less than 1000, remove decimal if it's a whole number
            if abs_value == int(abs_value):
                formatted = str(int(abs_value))
            else:
                formatted = f"{abs_value:.1f}"

        return f"-{formatted}" if is_negative else formatted

    except (ValueError, TypeError):
        return "0"


def format_percentage(value: Optional[Union[int, float]]) -> str:
    """
    Format a numeric value as a percentage.

    Converts a numeric value to a percentage string with one decimal place.
    Assumes the input value is already in percentage form (e.g., 25 = 25%,
    not 0.25 = 25%).

    Args:
        value: The numeric value to format as percentage. Can be int, float, or None.

    Returns:
        Formatted percentage string (e.g., "25.5%", "-10.0%", "0.0%").
        Returns "0.0%" if value is None.

    Examples:
        >>> format_percentage(25.5)
        '25.5%'

        >>> format_percentage(-10)
        '-10.0%'

        >>> format_percentage(None)
        '0.0%'

        >>> format_percentage(0)
        '0.0%'

        >>> format_percentage(99.99)
        '100.0%'

        >>> format_percentage(0.123)
        '0.1%'

    Note:
        - Shows one decimal place
        - Handles negative values
        - None values default to 0.0%
        - Input should be in percentage form (25, not 0.25)
        - For decimal inputs (0-1 range), multiply by 100 before passing
    """
    if value is None:
        return "0.0%"

    try:
        # Convert to float to handle both int and float
        num_value = float(value)
        return f"{num_value:.1f}%"

    except (ValueError, TypeError):
        return "0.0%"


def format_datetime(dt: Optional[Union[datetime, str]]) -> str:
    """
    Format a datetime object or ISO string in a human-readable format.

    Converts datetime objects or ISO format strings to a readable format:
    "YYYY-MM-DD HH:MM:SS" (24-hour format).

    Args:
        dt: The datetime to format. Can be datetime object, ISO string, or None.

    Returns:
        Formatted datetime string (e.g., "2025-10-11 14:30:00").
        Returns "N/A" if dt is None or invalid.

    Examples:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 10, 11, 14, 30, 0)
        >>> format_datetime(dt)
        '2025-10-11 14:30:00'

        >>> format_datetime("2025-10-11T14:30:00")
        '2025-10-11 14:30:00'

        >>> format_datetime(None)
        'N/A'

        >>> format_datetime("invalid")
        'N/A'

    Note:
        - Uses 24-hour time format
        - Accepts datetime objects or ISO 8601 strings
        - Returns "N/A" for None or invalid inputs
        - Zero-pads single-digit values
        - Handles various ISO format variations (with/without timezone)
    """
    if dt is None:
        return "N/A"

    try:
        # If it's already a datetime object
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        # If it's a string, try to parse it
        if isinstance(dt, str):
            # Try common ISO formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%d",
            ]:
                try:
                    parsed_dt = datetime.strptime(dt.split("+")[0].split("Z")[0], fmt)
                    return parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue

        return "N/A"

    except (ValueError, TypeError, AttributeError):
        return "N/A"
