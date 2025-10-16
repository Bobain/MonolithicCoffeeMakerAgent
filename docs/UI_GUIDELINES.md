# Console UI Guidelines

**US-036: Polish Console UI to Claude-CLI Quality Standard**

This document provides guidelines for creating consistent, professional console output across all CLI commands in the MonolithicCoffeeMakerAgent project.

## Overview

The project uses the `rich` library for terminal formatting, providing a Claude-CLI quality user experience with:
- Consistent color scheme
- Professional formatting (panels, tables, progress indicators)
- Helpful error messages with suggestions
- Clear visual separation between sections
- Real-time status indicators

## Core Module

All UI utilities are centralized in `coffee_maker/cli/console_ui.py`.

## Color Scheme

The project uses a consistent color scheme defined in `COLORS`:

```python
COLORS = {
    "info": "blue",          # Information messages
    "success": "green",      # Success messages
    "warning": "yellow",     # Warning messages
    "error": "red",          # Error messages
    "muted": "dim white",    # Secondary text
    "highlight": "cyan",     # Highlighted text
    "accent": "magenta",     # Accent colors
}
```

## Status Symbols

Consistent symbols for different message types:

```python
SYMBOLS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "working": "⚙",
    "thinking": "🧠",
    "idle": "💤",
}
```

## Usage Guidelines

### 1. Success Messages

Use `success()` for positive outcomes:

```python
from coffee_maker.cli.console_ui import success

success("Task completed successfully!")
success("File saved", details="Saved to /path/to/file")
```

**Output:**
```
✓ Task completed successfully!
✓ File saved
   Saved to /path/to/file
```

### 2. Error Messages

Use `error()` with helpful suggestions:

```python
from coffee_maker.cli.console_ui import error

error(
    "Database connection failed",
    suggestion="Check your database credentials in .env",
    details="Connection timeout after 30 seconds"
)
```

**Output:**
```
✗ Error: Database connection failed
   💡 Suggestion: Check your database credentials in .env
   Details: Connection timeout after 30 seconds
```

### 3. Warning Messages

Use `warning()` for non-critical issues:

```python
from coffee_maker.cli.console_ui import warning

warning(
    "No cache found, will build from scratch",
    suggestion="Run with --cache to speed up future builds"
)
```

### 4. Info Messages

Use `info()` for informational output:

```python
from coffee_maker.cli.console_ui import info

info("Processing 150 files...")
info("Daemon started", details="PID: 12345")
```

### 5. Section Headers

Use `section_header()` to separate major sections:

```python
from coffee_maker.cli.console_ui import section_header

section_header("Configuration", "System settings and options")
```

**Output:**
```
────────────────────── Configuration ──────────────────────
System settings and options
```

### 6. Tables

Use `create_table()` for structured data:

```python
from coffee_maker.cli.console_ui import console, create_table

table = create_table(
    title="Build Results",
    columns=["File", "Status", "Time"]
)

table.add_row("main.py", "✓ Success", "0.5s")
table.add_row("test.py", "✓ Success", "1.2s")
table.add_row("app.py", "✗ Failed", "0.3s")

console.print(table)
```

### 7. Panels

Use `create_panel()` for highlighted content:

```python
from coffee_maker.cli.console_ui import console, create_panel

panel = create_panel(
    "This is important information",
    title="Notice",
    border_style="yellow"
)

console.print(panel)
```

### 8. Progress Indicators

Use `progress_context()` for long operations:

```python
from coffee_maker.cli.console_ui import progress_context

with progress_context("Loading data...") as progress:
    task = progress.add_task("Processing", total=100)

    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

### 9. Notifications

Use `format_notification()` for daemon notifications:

```python
from coffee_maker.cli.console_ui import console, format_notification

panel = format_notification(
    notif_type="question",
    title="Dependency Approval",
    message="Install pandas for data processing?",
    priority="high",
    created_at="2025-10-16 10:30:00"
)

console.print(panel)
```

### 10. Error Panels with Suggestions

Use `format_error_with_suggestions()` for comprehensive error display:

```python
from coffee_maker.cli.console_ui import console, format_error_with_suggestions

panel = format_error_with_suggestions(
    error_message="Failed to start daemon",
    suggestions=[
        "Check if another instance is already running",
        "Verify ANTHROPIC_API_KEY is set",
        "Ensure Claude CLI is installed"
    ],
    error_details="Port 8000 already in use"
)

console.print(panel)
```

## Best Practices

### DO ✓

1. **Be Consistent**: Use the same color/symbol for the same type of message across all commands
2. **Provide Context**: Include helpful suggestions with errors
3. **Use Visual Hierarchy**: Section headers → Panels → Tables → Text
4. **Show Progress**: Use progress indicators for operations > 1 second
5. **Give Feedback**: Confirm user actions (saved, deleted, etc.)
6. **Format Data**: Use tables for structured data, not plain text
7. **Color Code**: Use colors to indicate status (green=good, red=bad, yellow=warning)

### DON'T ✗

1. **Don't Mix Styles**: Don't use plain `print()` mixed with rich formatting
2. **Don't Overuse Color**: Too much color is distracting
3. **Don't Hide Errors**: Always show what went wrong and how to fix it
4. **Don't Abbreviate**: Write full words, not "db" or "cfg"
5. **Don't Skip Whitespace**: Use blank lines to separate sections
6. **Don't Use Emojis Excessively**: Use symbols from SYMBOLS dict
7. **Don't Hardcode Colors**: Use COLORS constants

## Examples

### Before (Plain):

```python
print("Starting daemon...")
print("Error: API key not set")
print("Priority 1: Analytics")
print("Priority 2: Dashboard")
```

### After (Polished):

```python
from coffee_maker.cli.console_ui import (
    section_header,
    error,
    create_table,
    console
)

section_header("Code Developer Daemon", "Autonomous development agent")

error(
    "API key not set",
    suggestion="Set ANTHROPIC_API_KEY in .env file"
)

table = create_table(title="Priorities", columns=["ID", "Title", "Status"])
table.add_row("1", "Analytics", "[green]✓ Complete[/green]")
table.add_row("2", "Dashboard", "[yellow]⚙ In Progress[/yellow]")

console.print(table)
```

## Testing UI Components

All UI utilities have comprehensive unit tests in `tests/unit/test_console_ui.py`.

Run tests:

```bash
poetry run pytest tests/unit/test_console_ui.py -v
```

## Integration Checklist

When adding new CLI commands or updating existing ones:

- [ ] Import console_ui utilities
- [ ] Replace plain `print()` with appropriate UI functions
- [ ] Add section headers for major sections
- [ ] Use tables for structured data
- [ ] Add helpful error messages with suggestions
- [ ] Include progress indicators for long operations
- [ ] Use consistent color scheme
- [ ] Add visual separation (blank lines, rules)
- [ ] Write tests for new formatting logic
- [ ] Test output visually in terminal

## Further Reading

- [Rich Documentation](https://rich.readthedocs.io/)
- [Claude CLI](https://claude.ai/) - Quality standard to match
- `coffee_maker/cli/console_ui.py` - Source implementation
- `tests/unit/test_console_ui.py` - Unit tests

---

**Version**: 1.0
**Last Updated**: 2025-10-16
**US**: US-036
