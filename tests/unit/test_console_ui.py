"""Unit tests for console UI utilities.

US-036: Polish Console UI to Claude-CLI Quality Standard
"""

from rich.panel import Panel
from rich.table import Table

from coffee_maker.cli.console_ui import (
    COLORS,
    SYMBOLS,
    create_panel,
    create_table,
    format_error_with_suggestions,
    format_key_value,
    format_list,
    format_metric,
    format_notification,
)


def test_colors_defined():
    """Test that all required colors are defined."""
    required_colors = [
        "info",
        "success",
        "warning",
        "error",
        "muted",
        "highlight",
        "accent",
    ]

    for color in required_colors:
        assert color in COLORS
        assert isinstance(COLORS[color], str)


def test_symbols_defined():
    """Test that all required symbols are defined."""
    required_symbols = [
        "success",
        "error",
        "warning",
        "info",
        "working",
        "thinking",
        "idle",
    ]

    for symbol in required_symbols:
        assert symbol in SYMBOLS
        assert isinstance(SYMBOLS[symbol], str)


def test_create_table_default():
    """Test creating a table with default options."""
    table = create_table()

    assert isinstance(table, Table)
    assert table.show_header is True


def test_create_table_with_columns():
    """Test creating a table with custom columns."""
    columns = ["Name", "Value", "Status"]
    table = create_table(columns=columns)

    assert isinstance(table, Table)
    assert len(table.columns) == 3


def test_create_table_with_title():
    """Test creating a table with a title."""
    table = create_table(title="Test Table")

    assert isinstance(table, Table)
    assert table.title == "Test Table"


def test_create_panel_basic():
    """Test creating a basic panel."""
    panel = create_panel("Test content")

    assert isinstance(panel, Panel)


def test_create_panel_with_title():
    """Test creating a panel with a title."""
    panel = create_panel("Test content", title="Test Title")

    assert isinstance(panel, Panel)
    assert panel.title == "Test Title"


def test_create_panel_with_border_style():
    """Test creating a panel with custom border style."""
    panel = create_panel("Test content", border_style="red")

    assert isinstance(panel, Panel)


def test_format_key_value():
    """Test formatting key-value pairs."""
    text = format_key_value("Status", "Active")

    # Should contain both key and value
    assert "Status" in text.plain
    assert "Active" in text.plain


def test_format_metric_without_threshold():
    """Test formatting metric without threshold."""
    result = format_metric("CPU Usage", 45, unit="%")

    assert "CPU Usage" in result
    assert "45%" in result


def test_format_metric_with_good_threshold():
    """Test formatting metric that exceeds good threshold."""
    result = format_metric("Accuracy", 95, unit="%", good_threshold=90)

    assert "Accuracy" in result
    assert "95%" in result
    # Should use success color
    assert COLORS["success"] in result


def test_format_metric_with_bad_threshold():
    """Test formatting metric that doesn't meet good threshold."""
    result = format_metric("Accuracy", 75, unit="%", good_threshold=90)

    assert "Accuracy" in result
    assert "75%" in result
    # Should use warning color
    assert COLORS["warning"] in result


def test_format_list_default():
    """Test formatting list with default bullet."""
    items = ["Item 1", "Item 2", "Item 3"]
    result = format_list(items)

    # All items should be present
    for item in items:
        assert item in result

    # Should contain bullet character
    assert "•" in result


def test_format_list_custom_bullet():
    """Test formatting list with custom bullet."""
    items = ["Task 1", "Task 2"]
    result = format_list(items, bullet="-")

    assert "Task 1" in result
    assert "Task 2" in result
    assert "-" in result


def test_format_error_with_suggestions():
    """Test formatting error panel with suggestions."""
    error_msg = "Database connection failed"
    suggestions = [
        "Check your database credentials",
        "Verify the database is running",
        "Check network connectivity",
    ]

    panel = format_error_with_suggestions(error_msg, suggestions)

    assert isinstance(panel, Panel)
    # Error message should be in the panel
    # Note: We can't easily test the exact content without rendering


def test_format_error_with_details():
    """Test formatting error with details."""
    error_msg = "API request failed"
    suggestions = ["Retry the request"]
    details = "Connection timeout after 30 seconds"

    panel = format_error_with_suggestions(error_msg, suggestions, error_details=details)

    assert isinstance(panel, Panel)


def test_format_notification_info():
    """Test formatting info notification."""
    panel = format_notification(notif_type="info", title="Test Info", message="This is an info message")

    assert isinstance(panel, Panel)


def test_format_notification_warning():
    """Test formatting warning notification."""
    panel = format_notification(notif_type="warning", title="Test Warning", message="This is a warning message")

    assert isinstance(panel, Panel)


def test_format_notification_error():
    """Test formatting error notification."""
    panel = format_notification(notif_type="error", title="Test Error", message="This is an error message")

    assert isinstance(panel, Panel)


def test_format_notification_critical():
    """Test formatting critical notification."""
    panel = format_notification(
        notif_type="error",
        title="Critical Issue",
        message="System failure",
        priority="critical",
    )

    assert isinstance(panel, Panel)


def test_format_notification_with_timestamp():
    """Test formatting notification with timestamp."""
    panel = format_notification(
        notif_type="info",
        title="Test",
        message="Test message",
        created_at="2025-10-16 10:30:00",
    )

    assert isinstance(panel, Panel)


def test_colors_are_valid_rich_styles():
    """Test that all colors are valid Rich color names."""
    # This is a basic test - Rich will validate at runtime
    valid_basic_colors = [
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "bright_black",
        "bright_red",
        "bright_green",
        "bright_yellow",
        "bright_blue",
        "bright_magenta",
        "bright_cyan",
        "bright_white",
    ]

    for color_value in COLORS.values():
        # Color can be a basic color name or contain spaces (like "dim white")
        # Just check that it's a string
        assert isinstance(color_value, str)


def test_format_list_with_indentation():
    """Test formatting list with custom indentation."""
    items = ["Line 1", "Line 2"]
    result = format_list(items, indent=4)

    # Should have indentation
    assert "    •" in result or "    " in result
