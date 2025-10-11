"""
Utility modules for Analytics Dashboard.

This package provides utility functions for data processing, formatting, and exports.
"""

from .data_processing import aggregate_by_period, fill_missing_dates, validate_dataframe
from .export_utils import create_download_button, generate_csv_export, generate_pdf_report
from .format_utils import format_currency, format_datetime, format_number, format_percentage

__all__ = [
    # Data processing
    "validate_dataframe",
    "fill_missing_dates",
    "aggregate_by_period",
    # Formatting
    "format_currency",
    "format_number",
    "format_percentage",
    "format_datetime",
    # Exports
    "generate_csv_export",
    "generate_pdf_report",
    "create_download_button",
]
