# Console UI Examples - Practical Demonstrations

**Related**: US-036: Polish Console UI to Claude-CLI Quality
**Status**: ✅ Complete
**Last Updated**: 2025-10-20

## Overview

This document provides practical, copy-paste examples demonstrating the polished console UI features. All examples use real code from the MonolithicCoffeeMakerAgent project.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Success and Error Messages](#success-and-error-messages)
3. [Progress Indicators](#progress-indicators)
4. [Tables and Data Display](#tables-and-data-display)
5. [Notifications and Panels](#notifications-and-panels)
6. [Interactive Features](#interactive-features)
7. [Real-World Scenarios](#real-world-scenarios)

---

## Basic Usage

### Import Console UI

```python
from coffee_maker.cli.console_ui import (
    console,           # Shared console instance
    success,           # Success messages
    error,             # Error messages
    warning,           # Warning messages
    info,              # Info messages
    status,            # Status updates
    section_header,    # Section headers
)
```

### Simple Messages

```python
# Info message
info("Starting roadmap analysis...")
# Output: ℹ Starting roadmap analysis...

# Success message
success("Analysis completed!")
# Output: ✓ Analysis completed!

# Warning message
warning("Priority PRIORITY-2.8 has no assigned developer")
# Output: ⚠ Warning: Priority PRIORITY-2.8 has no assigned developer

# Error message
error("Failed to parse ROADMAP.md")
# Output: ✗ Error: Failed to parse ROADMAP.md
```

### Messages with Details

```python
# Success with details
success(
    "Priority PRIORITY-2.6 completed!",
    details="All tests passed, documentation updated, PR merged"
)
# Output:
# ✓ Priority PRIORITY-2.6 completed!
#    All tests passed, documentation updated, PR merged

# Info with details
info(
    "Found 15 priorities in ROADMAP.md",
    details="5 completed, 3 in progress, 7 planned"
)
# Output:
# ℹ Found 15 priorities in ROADMAP.md
#    5 completed, 3 in progress, 7 planned
```

---

## Success and Error Messages

### Error with Suggestion

```python
error(
    "Database connection failed",
    suggestion="Check that DATABASE_URL is set in .env file",
    details="psycopg2.OperationalError: could not connect to server"
)
```

**Output**:
```
✗ Error: Database connection failed
   💡 Suggestion: Check that DATABASE_URL is set in .env file
   Details: psycopg2.OperationalError: could not connect to server
```

### Multiple Suggestions

```python
from coffee_maker.cli.console_ui import format_error_with_suggestions

suggestions = [
    "Verify the file exists: ls -la docs/roadmap/ROADMAP.md",
    "Check file permissions: chmod 644 docs/roadmap/ROADMAP.md",
    "Ensure you're in the project root directory"
]

error_msg = format_error_with_suggestions(
    "Failed to read ROADMAP.md",
    suggestions=suggestions,
    error_detail="FileNotFoundError: No such file or directory"
)
console.print(error_msg)
```

**Output**:
```
✗ Error: Failed to read ROADMAP.md

💡 Suggestions:
  1. Verify the file exists: ls -la docs/roadmap/ROADMAP.md
  2. Check file permissions: chmod 644 docs/roadmap/ROADMAP.md
  3. Ensure you're in the project root directory

Details: FileNotFoundError: No such file or directory
```

### Success Scenarios

```python
# Test passed
success("All 127 tests passed", details="Coverage: 87.3%")

# Feature completed
success(
    "US-036: Console UI Polish completed!",
    details="Implementation: ✅ | Tests: ✅ | Documentation: ✅"
)

# Deployment success
success(
    "Deployed to production",
    details="Version: v2.4.0 | Deployment time: 45s | Status: healthy"
)
```

---

## Progress Indicators

### Simple Progress Context

```python
from coffee_maker.cli.console_ui import progress_context

with progress_context("Analyzing codebase...") as progress:
    task = progress.add_task("Scanning files", total=100)

    for i in range(100):
        # Simulate work
        time.sleep(0.05)
        progress.update(task, advance=1)
```

**Output** (animated):
```
⠋ Scanning files ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  45% 0:00:03
```

### Multiple Progress Tasks

```python
from coffee_maker.cli.console_ui import progress_context

with progress_context("Building project...") as progress:
    # Task 1: Compile
    compile_task = progress.add_task("Compiling", total=50)
    for i in range(50):
        time.sleep(0.02)
        progress.update(compile_task, advance=1)

    # Task 2: Test
    test_task = progress.add_task("Running tests", total=30)
    for i in range(30):
        time.sleep(0.03)
        progress.update(test_task, advance=1)

    # Task 3: Package
    package_task = progress.add_task("Packaging", total=20)
    for i in range(20):
        time.sleep(0.04)
        progress.update(package_task, advance=1)
```

### Indeterminate Progress (Spinner)

```python
from coffee_maker.cli.console_ui import console
from rich.spinner import Spinner
from rich.live import Live

with Live(Spinner("dots", text="Waiting for API response..."), console=console):
    # Long-running operation without known duration
    response = api_client.fetch_data()
```

---

## Tables and Data Display

### Basic Table

```python
from coffee_maker.cli.console_ui import create_table, console

table = create_table(
    title="Current Priorities",
    columns=["ID", "Title", "Status", "Effort"]
)

table.add_row("PRIORITY-2.6", "ACE Framework", "✅ Complete", "3 days")
table.add_row("PRIORITY-2.7", "Multi-AI Providers", "✅ Complete", "2 days")
table.add_row("US-036", "Console UI Polish", "🔄 In Progress", "2 days")
table.add_row("US-037", "ACE Tutorial", "📝 Planned", "1 day")

console.print(table)
```

**Output**:
```
                    Current Priorities
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┓
┃ ID          ┃ Title             ┃ Status      ┃ Effort┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━┩
│ PRIORITY-2.6│ ACE Framework     │ ✅ Complete │ 3 days│
│ PRIORITY-2.7│ Multi-AI Providers│ ✅ Complete │ 2 days│
│ US-036      │ Console UI Polish │ 🔄 In Progress│ 2 days│
│ US-037      │ ACE Tutorial      │ 📝 Planned  │ 1 day │
└─────────────┴───────────────────┴─────────────┴───────┘
```

### Key-Value Display

```python
from coffee_maker.cli.console_ui import format_key_value

# System status
status_items = [
    ("Agent", "code_developer"),
    ("Status", "Running"),
    ("Current Task", "Implementing US-036"),
    ("Iteration", "3/10"),
    ("Uptime", "2h 34m"),
]

for key, value in status_items:
    console.print(format_key_value(key, value))
```

**Output**:
```
Agent:        code_developer
Status:       Running
Current Task: Implementing US-036
Iteration:    3/10
Uptime:       2h 34m
```

### Metrics Display

```python
from coffee_maker.cli.console_ui import format_metric

metrics = [
    ("Total Priorities", 47, "green"),
    ("Completed", 23, "green"),
    ("In Progress", 5, "yellow"),
    ("Planned", 19, "blue"),
    ("Blocked", 0, "red"),
]

section_header("ROADMAP Metrics")
for label, value, color in metrics:
    console.print(format_metric(label, value, color))
```

**Output**:
```
─────────────────── ROADMAP Metrics ───────────────────

Total Priorities: 47
Completed:        23
In Progress:      5
Planned:          19
Blocked:          0
```

### List Formatting

```python
from coffee_maker.cli.console_ui import format_list

completed_tasks = [
    "Implemented PolishedConsoleUI class",
    "Added streaming response support",
    "Integrated prompt_toolkit for input",
    "Created comprehensive test suite",
    "Wrote user documentation",
]

section_header("Completed Tasks", "US-036 Progress")
console.print(format_list(completed_tasks, style="success"))
```

**Output**:
```
─────────────────── Completed Tasks ───────────────────
US-036 Progress

  ✓ Implemented PolishedConsoleUI class
  ✓ Added streaming response support
  ✓ Integrated prompt_toolkit for input
  ✓ Created comprehensive test suite
  ✓ Wrote user documentation
```

---

## Notifications and Panels

### Notification Panel

```python
from coffee_maker.cli.console_ui import format_notification, console

# Question notification
panel = format_notification(
    notif_type="question",
    title="Approval Required",
    message="Ready to implement PRIORITY-2.8: Observability Dashboard?",
    priority="high",
    created_at="2025-10-20 14:30:00"
)
console.print(panel)
```

**Output**:
```
╭─ QUESTION ───────────────────────────────────────╮
│ ‼️  Approval Required                             │
│                                                  │
│ Ready to implement PRIORITY-2.8: Observability  │
│ Dashboard?                                       │
│                                                  │
│ Created: 2025-10-20 14:30:00                    │
╰──────────────────────────────────────────────────╯
```

### Info Panel

```python
from coffee_maker.cli.console_ui import create_panel, console

info_content = """
**System Status**

- Agent: code_developer
- Status: ✅ Running
- Current Priority: US-036
- Iteration: 5/10
- Last Activity: 2 minutes ago
"""

panel = create_panel(
    info_content,
    title="Developer Status",
    border_style="blue"
)
console.print(panel)
```

### Warning Panel

```python
from coffee_maker.cli.console_ui import create_panel, console

warning_content = """
⚠️  The following priorities are blocked:

1. PRIORITY-3.2: Waiting for API access
2. PRIORITY-4.1: Dependency on PRIORITY-3.2
3. PRIORITY-5.3: Awaiting design review

Action required: Resolve blockers before proceeding.
"""

panel = create_panel(
    warning_content,
    title="⚠️  Blocked Priorities",
    border_style="yellow"
)
console.print(panel)
```

---

## Interactive Features

### Command History

The console UI automatically saves command history to `.project_manager_history`:

```bash
# Start project-manager chat
poetry run project-manager chat

# Type some commands
> /roadmap
> /status
> chat What's the current priority?
> /notifications

# Navigate history with arrow keys
↑  # Shows: /notifications
↑  # Shows: chat What's the current priority?
↑  # Shows: /status
↑  # Shows: /roadmap
↓  # Shows: /status
```

### Auto-completion

TAB completion works for all commands:

```bash
> /ro<TAB>
> /roadmap

> /sta<TAB>
> /status

> /not<TAB>
> /notifications
```

**Available commands**:
- `/roadmap` - View ROADMAP
- `/status` - Developer status
- `/notifications` - View notifications
- `/verify-dod` - Verify Definition of Done
- `/github-status` - GitHub PR/issue status
- `/standup` - Daily standup report
- `/help` - Show help
- `/exit` - Exit chat

### Multi-line Input

For complex prompts, use Shift+Enter to continue:

```
> chat Please analyze the current roadmap<Shift+Enter>
... and identify any priorities that:<Shift+Enter>
... 1. Have dependencies on blocked priorities<Shift+Enter>
... 2. Are missing DoD criteria<Shift+Enter>
... 3. Need architectural review<Enter>

# Agent receives full multi-line prompt
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Graceful exit with confirmation |
| `Ctrl+D` | Exit (Unix standard) |
| `Ctrl+L` | Clear screen |
| `Ctrl+R` | Reverse search history |
| `Ctrl+A` | Move to start of line |
| `Ctrl+E` | Move to end of line |
| `Ctrl+K` | Delete to end of line |
| `Ctrl+U` | Delete to start of line |

---

## Real-World Scenarios

### Scenario 1: Checking Developer Status

```python
from coffee_maker.cli.console_ui import (
    section_header,
    create_table,
    format_key_value,
    success,
    warning,
    console,
)

section_header("Code Developer Status", "Real-time monitoring")

# Status overview
console.print(format_key_value("Agent", "code_developer"))
console.print(format_key_value("Status", "Running ✅"))
console.print(format_key_value("Current Priority", "US-036"))
console.print(format_key_value("Iteration", "5/10"))
console.print()

# Recent activity table
activity_table = create_table(
    title="Recent Activity",
    columns=["Time", "Event", "Status"]
)
activity_table.add_row("14:30", "Started US-036", "✅")
activity_table.add_row("14:45", "Created console_ui.py", "✅")
activity_table.add_row("15:00", "Ran tests (127 passed)", "✅")
activity_table.add_row("15:15", "Updated documentation", "🔄")

console.print(activity_table)

# Warnings (if any)
if blocked_items:
    warning("2 notifications pending approval")
else:
    success("No blockers detected")
```

### Scenario 2: Analyzing ROADMAP

```python
from coffee_maker.cli.console_ui import (
    section_header,
    create_table,
    format_metric,
    info,
    console,
)

section_header("ROADMAP Analysis", "Current status overview")

# Metrics
metrics = [
    ("Total Priorities", 47),
    ("Completed", 23),
    ("In Progress", 5),
    ("Planned", 19),
]

for label, value in metrics:
    console.print(format_metric(label, value, "blue"))

console.print()

# Priorities table
priorities_table = create_table(
    title="Active Priorities",
    columns=["ID", "Title", "Status", "Progress"]
)
priorities_table.add_row("US-036", "Console UI Polish", "🔄 In Progress", "80%")
priorities_table.add_row("US-037", "ACE Tutorial", "📝 Planned", "0%")
priorities_table.add_row("US-038", "Performance Opt", "📝 Planned", "0%")

console.print(priorities_table)

info("Analysis complete", details="3 priorities need attention")
```

### Scenario 3: Processing Notifications

```python
from coffee_maker.cli.console_ui import (
    section_header,
    format_notification,
    info,
    success,
    console,
)

section_header("Notifications", "Pending actions")

# Show notification count
info(f"Found 3 pending notifications")
console.print()

# Display each notification
notifications = [
    {
        "type": "question",
        "title": "Approval Required",
        "message": "Ready to implement US-037?",
        "priority": "high",
        "created_at": "2025-10-20 14:30:00",
    },
    {
        "type": "info",
        "title": "Test Results",
        "message": "All 127 tests passed with 87% coverage",
        "priority": "normal",
        "created_at": "2025-10-20 15:00:00",
    },
    {
        "type": "success",
        "title": "Priority Completed",
        "message": "PRIORITY-2.7 completed successfully",
        "priority": "normal",
        "created_at": "2025-10-20 15:30:00",
    },
]

for notif in notifications:
    panel = format_notification(**notif)
    console.print(panel)
    console.print()

success("All notifications processed")
```

### Scenario 4: Error Recovery

```python
from coffee_maker.cli.console_ui import (
    error,
    format_error_with_suggestions,
    console,
)

try:
    # Attempt operation
    result = parse_roadmap("docs/roadmap/ROADMAP.md")
except FileNotFoundError as e:
    suggestions = [
        "Check that you're in the project root: pwd",
        "Verify the file exists: ls -la docs/roadmap/ROADMAP.md",
        "Clone the repository if missing: git clone https://github.com/Bobain/MonolithicCoffeeMakerAgent",
    ]

    error_msg = format_error_with_suggestions(
        "Failed to read ROADMAP.md",
        suggestions=suggestions,
        error_detail=str(e)
    )
    console.print(error_msg)
except Exception as e:
    error(
        "Unexpected error during ROADMAP parsing",
        suggestion="Run with --debug for detailed traceback",
        details=str(e)
    )
```

### Scenario 5: Long-Running Task

```python
from coffee_maker.cli.console_ui import (
    section_header,
    progress_context,
    success,
    info,
)
import time

section_header("Building Project", "Compiling and testing")

with progress_context("Building...") as progress:
    # Compile
    compile_task = progress.add_task("Compiling source", total=100)
    for i in range(100):
        time.sleep(0.02)
        progress.update(compile_task, advance=1)

    info("Compilation complete")

    # Test
    test_task = progress.add_task("Running tests", total=127)
    for i in range(127):
        time.sleep(0.01)
        progress.update(test_task, advance=1)

    info("All tests passed")

    # Package
    package_task = progress.add_task("Creating package", total=50)
    for i in range(50):
        time.sleep(0.03)
        progress.update(package_task, advance=1)

success("Build complete!", details="Ready for deployment")
```

---

## Testing the Console UI

### Run Unit Tests

```bash
# Run all console UI tests
pytest tests/unit/test_console_ui.py -v

# Expected output:
# test_colors_defined ✓
# test_symbols_defined ✓
# test_create_table_default ✓
# test_create_table_with_columns ✓
# test_create_panel_basic ✓
# ... (15+ tests)
```

### Interactive Testing

```bash
# Start project-manager chat to test UI
poetry run project-manager chat

# Try these commands to see UI in action:
> /roadmap          # View roadmap with rich formatting
> /status           # See developer status with tables
> /notifications    # View notifications in panels
> /help             # See help with formatted commands
```

### Visual Testing Checklist

- [ ] Colors display correctly (info=blue, success=green, warning=yellow, error=red)
- [ ] Symbols render properly (✓ ✗ ⚠ ℹ)
- [ ] Tables format correctly with borders and alignment
- [ ] Panels have proper borders and titles
- [ ] Progress bars animate smoothly
- [ ] Multi-line input works with Shift+Enter
- [ ] Command history navigates with ↑/↓
- [ ] TAB completion suggests commands
- [ ] Ctrl+L clears screen
- [ ] Ctrl+C exits gracefully

---

## Related Documentation

- **User Guide**: `docs/CONSOLE_UI_GUIDE.md`
- **Technical Spec**: `docs/architecture/specs/SPEC-036-console-ui-polish.md` (if exists)
- **Implementation**: `coffee_maker/cli/console_ui.py:1`
- **Tests**: `tests/unit/test_console_ui.py:1`
- **ROADMAP**: `docs/roadmap/ROADMAP.md:23698` (US-036)

---

## Tips and Best Practices

### 1. Consistent Error Handling

Always provide helpful suggestions with errors:

```python
# ✅ Good
error("Database migration failed",
      suggestion="Run 'poetry run alembic upgrade head' to apply migrations",
      details=str(e))

# ❌ Bad
print(f"Error: {e}")
```

### 2. Progress Feedback

Show progress for operations > 2 seconds:

```python
# ✅ Good
with progress_context("Processing files...") as progress:
    task = progress.add_task("Processing", total=len(files))
    for file in files:
        process_file(file)
        progress.update(task, advance=1)

# ❌ Bad
for file in files:
    process_file(file)  # User sees nothing
```

### 3. Visual Hierarchy

Use section headers to organize output:

```python
# ✅ Good
section_header("ROADMAP Analysis")
# ... content ...
section_header("Recommendations")
# ... content ...

# ❌ Bad
print("ROADMAP Analysis")
# ... content ...
print("Recommendations")
# ... content ...
```

### 4. Color Coding

Use colors consistently:

- **Blue**: Informational messages
- **Green**: Success/completion
- **Yellow**: Warnings (non-blocking issues)
- **Red**: Errors (blocking issues)
- **Cyan**: Headers and highlights
- **Magenta**: Accent elements

---

**Last Updated**: 2025-10-20
**Status**: Production Ready ✅
**US-036**: Console UI Polish - Complete
