# Console UI Guide - Coffee Maker Project Manager

**Last Updated**: 2025-10-20
**Status**: Production Ready ✅
**US-036**: Polish Console UI to Claude-CLI Quality

---

## Table of Contents

1. [Overview](#overview)
2. [Color Scheme & Visual Language](#color-scheme--visual-language)
3. [Interactive Features](#interactive-features)
4. [Message Types](#message-types)
5. [Developer Guide](#developer-guide)
6. [Troubleshooting](#troubleshooting)
7. [Terminal Compatibility](#terminal-compatibility)

---

## Overview

The Coffee Maker console UI provides a professional, polished terminal interface matching claude-cli quality standards. Built with the `rich` library for advanced formatting and `prompt_toolkit` for interactive input, the UI delivers a smooth, responsive user experience.

### Key Features

- **Consistent Color Scheme**: Professional color palette across all outputs
- **Rich Formatting**: Tables, panels, progress bars, and syntax highlighting
- **Interactive Input**: Command history, auto-completion, multi-line support
- **Real-time Status**: Live daemon status monitoring in bottom toolbar
- **Keyboard Shortcuts**: Intuitive shortcuts for power users
- **Responsive Design**: Graceful handling of terminal resize and theme switching

### Design Philosophy

The UI follows these principles:
1. **Clarity**: Clear, scannable information hierarchy
2. **Consistency**: Unified visual language across all components
3. **Responsiveness**: Smooth streaming and real-time updates
4. **Accessibility**: Support for both light and dark themes
5. **Professional**: Clean, minimal design without clutter

---

## Color Scheme & Visual Language

### Primary Colors

The console UI uses a consistent color scheme defined in `coffee_maker/cli/console_ui.py:40`:

```python
COLORS = {
    "info": "blue",       # Informational messages
    "success": "green",   # Success states
    "warning": "yellow",  # Warning messages
    "error": "red",       # Error messages
    "muted": "dim white", # Secondary text
    "highlight": "cyan",  # Highlighted elements
    "accent": "magenta",  # Accent elements
}
```

### Status Symbols

Visual symbols provide quick status recognition (`coffee_maker/cli/console_ui.py:51`):

```python
SYMBOLS = {
    "success": "✓",    # Completed successfully
    "error": "✗",      # Failed or error
    "warning": "⚠",    # Warning or caution
    "info": "ℹ",       # Informational
    "working": "⚙",    # In progress
    "thinking": "🧠",  # AI processing
    "idle": "💤",      # Idle state
}
```

### Usage Examples

**Success Message**:
```
✓ Task completed successfully!
  Details: 3 files updated
```

**Error with Suggestion**:
```
✗ Error: Configuration file not found
  💡 Suggestion: Run `project-manager init` to create configuration
  Details: Missing .project_manager/config.json
```

**Warning**:
```
⚠ Warning: Large roadmap file detected (5MB)
  💡 Suggestion: Consider archiving completed priorities
```

---

## Interactive Features

### Command History

Navigate through previous commands using arrow keys:

- **↑ (Up Arrow)**: Previous command
- **↓ (Down Arrow)**: Next command
- **Ctrl+R**: Reverse search through history

History is persisted to `~/.project_manager/chat_history.txt` (configured in `coffee_maker/cli/chat_interface.py:418`).

### Auto-completion

Press **Tab** to trigger auto-completion for:

1. **Slash Commands**: `/help`, `/view`, `/status`, etc.
2. **Priority Names**: `PRIORITY 1`, `PRIORITY 2`, etc.
3. **Context-aware**: Suggests relevant completions based on input

Example:
```
You: /vi[TAB]
  → /view

You: view PRIO[TAB]
  → PRIORITY 1
  → PRIORITY 2
  → PRIORITY 3
```

Implementation in `coffee_maker/cli/chat_interface.py:263` (`ProjectManagerCompleter` class).

### Multi-line Input

Support for long prompts and formatted text:

- **Alt+Enter**: Insert newline (continue on next line)
- **Enter**: Submit input
- **Continuation prompt**: `... ` shows multi-line mode

Example:
```
You
› Can you help me with the following:
... 1. Review PRIORITY 3
... 2. Check daemon status
... 3. Generate standup report
```

Configured in `coffee_maker/cli/chat_interface.py:428` (escape + enter key binding).

### Real-time Status Bar

The bottom toolbar shows live daemon status (updates every 2 seconds):

```
🟢 Implement Authentication System
▸ PRIORITY 8 | Iteration 3 | Time: 2h 15m | ETA: ~4h 30m
▸ Tasks:
   ✓ Read specifications: 5m (est: 10m)
   🔄 Implement auth middleware: 1h 20m / 2h
   ⏳ Write tests (est: 1h)
   ⏳ Update documentation (est: 30m)
▸ Progress: [████████████░░░░░░░░] 60%
```

**Status Indicators**:
- 🟢 Active - Daemon working on task
- 🟡 Idle - Daemon waiting for tasks
- ⚫ Not running - Daemon stopped

Implementation in `coffee_maker/cli/chat_interface.py:56` (`DeveloperStatusMonitor` class).

---

## Message Types

### Success Messages

Used for completed actions and positive confirmations.

**API** (`coffee_maker/cli/console_ui.py:62`):
```python
from coffee_maker.cli.console_ui import success

success("Priority added successfully", details="PRIORITY 10: Authentication")
```

**Output**:
```
✓ Priority added successfully
  PRIORITY 10: Authentication
```

### Error Messages

Used for failures and errors with actionable suggestions.

**API** (`coffee_maker/cli/console_ui.py:75`):
```python
from coffee_maker.cli.console_ui import error

error(
    "Database connection failed",
    suggestion="Check that the daemon is running",
    details="Connection timeout after 30s"
)
```

**Output**:
```
✗ Error: Database connection failed
  💡 Suggestion: Check that the daemon is running
  Details: Connection timeout after 30s
```

### Warning Messages

Used for non-critical issues that need attention.

**API** (`coffee_maker/cli/console_ui.py:94`):
```python
from coffee_maker.cli.console_ui import warning

warning(
    "Context window nearing limit",
    suggestion="Consider compacting conversation history"
)
```

**Output**:
```
⚠ Warning: Context window nearing limit
  💡 Suggestion: Consider compacting conversation history
```

### Info Messages

Used for general information and status updates.

**API** (`coffee_maker/cli/console_ui.py:109`):
```python
from coffee_maker.cli.console_ui import info

info("Daemon started", details="PID: 12345")
```

**Output**:
```
ℹ Daemon started
  PID: 12345
```

### Notifications

Formatted panels for important messages from daemon.

**API** (`coffee_maker/cli/console_ui.py:319`):
```python
from coffee_maker.cli.console_ui import format_notification, console

panel = format_notification(
    notif_type="question",
    title="Approval Required",
    message="Should I proceed with implementation of PRIORITY 8?",
    priority="high",
    created_at="2025-10-20 14:30:00"
)
console.print(panel)
```

**Output**:
```
┌──────────── QUESTION ────────────┐
│ ‼️ Approval Required             │
│                                   │
│ Should I proceed with            │
│ implementation of PRIORITY 8?    │
│                                   │
│ Created: 2025-10-20 14:30:00     │
└───────────────────────────────────┘
```

### Tables

Structured data display with consistent formatting.

**API** (`coffee_maker/cli/console_ui.py:153`):
```python
from coffee_maker.cli.console_ui import create_table, console

table = create_table(
    title="Active Priorities",
    columns=["ID", "Title", "Status", "Progress"]
)
table.add_row("PRIORITY 8", "Authentication", "In Progress", "60%")
table.add_row("PRIORITY 9", "Email Notifications", "Planned", "0%")
console.print(table)
```

**Output**:
```
          Active Priorities
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID        ┃ Title              ┃ Status      ┃ Progress ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ PRIORITY 8│ Authentication     │ In Progress │ 60%      │
│ PRIORITY 9│ Email Notifications│ Planned     │ 0%       │
└───────────┴────────────────────┴─────────────┴──────────┘
```

### Progress Indicators

Visual feedback for long-running operations.

**Spinner** (`coffee_maker/cli/console_ui.py:203`):
```python
from coffee_maker.cli.console_ui import progress_context
import time

with progress_context("Loading priorities...") as progress:
    task = progress.add_task("Loading...", total=100)
    for i in range(100):
        time.sleep(0.01)
        progress.update(task, advance=1)
```

**Output** (animated):
```
⠋ Loading priorities... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45% 0:00:03
```

### Syntax Highlighting

Code blocks with automatic language detection and highlighting (implementation in `coffee_maker/cli/chat_interface.py:1211`).

**Automatic Detection**:
````
```python
def calculate_progress(completed, total):
    return (completed / total) * 100
```
````

**Output**:
```python
 1 │ def calculate_progress(completed, total):
 2 │     return (completed / total) * 100
```
(with syntax highlighting in Monokai theme)

---

## Developer Guide

### Using Console UI in Your Code

#### Import the Module

```python
from coffee_maker.cli.console_ui import (
    console,        # Shared Console instance
    success,        # Success messages
    error,          # Error messages
    warning,        # Warning messages
    info,           # Info messages
    create_table,   # Create formatted tables
    create_panel,   # Create formatted panels
    COLORS,         # Color constants
    SYMBOLS,        # Symbol constants
)
```

#### Best Practices

1. **Use Shared Console Instance**:
   ```python
   # Good
   from coffee_maker.cli.console_ui import console
   console.print("[bold]Hello[/]")

   # Bad - creates separate console instance
   from rich.console import Console
   Console().print("[bold]Hello[/]")
   ```

2. **Use Helper Functions**:
   ```python
   # Good - consistent formatting
   success("Task completed")

   # Bad - manual formatting
   console.print("[green]✓ Task completed[/]")
   ```

3. **Provide Actionable Suggestions**:
   ```python
   # Good - tells user what to do
   error(
       "Invalid priority ID",
       suggestion="Use /view to see available priorities"
   )

   # Bad - just the error
   error("Invalid priority ID")
   ```

4. **Use Appropriate Message Types**:
   ```python
   # Good - correct severity
   info("Loading roadmap...")      # Informational
   warning("Large file detected")  # Worth noting
   error("Database unavailable")   # Action required

   # Bad - wrong severity
   error("Loading roadmap...")     # Not an error!
   ```

#### Creating Custom Components

**Custom Panel** (using `coffee_maker/cli/console_ui.py:183`):
```python
from coffee_maker.cli.console_ui import create_panel, console

content = """
**Next Steps**:
1. Review the specification
2. Implement the feature
3. Write tests
"""

panel = create_panel(
    content,
    title="Action Items",
    border_style="cyan"
)
console.print(panel)
```

**Custom Table**:
```python
from coffee_maker.cli.console_ui import create_table, console

table = create_table(
    title="Daemon Statistics",
    columns=["Metric", "Value"]
)
table.add_row("Uptime", "12h 34m")
table.add_row("Tasks Completed", "8")
table.add_row("CPU Usage", "15%")
console.print(table)
```

**Error Panel with Suggestions** (`coffee_maker/cli/console_ui.py:282`):
```python
from coffee_maker.cli.console_ui import format_error_with_suggestions, console

panel = format_error_with_suggestions(
    error_message="Failed to parse ROADMAP.md",
    suggestions=[
        "Check for unclosed markdown blocks",
        "Verify file encoding is UTF-8",
        "Run: git diff docs/roadmap/ROADMAP.md"
    ],
    error_details="Line 1234: Unexpected end of file"
)
console.print(panel)
```

### Streaming Responses

For AI responses, use character-by-character streaming (`coffee_maker/cli/chat_interface.py:1327`):

```python
def stream_response(text_generator):
    """Stream AI response smoothly."""
    console.print("\n[bold]Claude[/]")

    for chunk in text_generator:
        console.print(chunk, end="")

    console.print()  # Final newline
```

### Markdown Rendering

Render markdown content with rich formatting:

```python
from rich.markdown import Markdown
from coffee_maker.cli.console_ui import console

markdown_text = """
# Heading

**Bold text** and *italic text*

- List item 1
- List item 2

```python
code_block()
```
"""

md = Markdown(markdown_text)
console.print(md)
```

---

## Troubleshooting

### Common Issues

#### Colors Not Showing

**Symptom**: Plain text without colors

**Solutions**:
1. Check terminal supports colors:
   ```bash
   echo $TERM  # Should be xterm-256color or similar
   ```

2. Force color output:
   ```bash
   export FORCE_COLOR=1
   poetry run project-manager
   ```

3. Update terminal emulator to modern version

#### Unicode Symbols Not Displaying

**Symptom**: Boxes or question marks instead of symbols

**Solutions**:
1. Use UTF-8 encoding:
   ```bash
   export LC_ALL=en_US.UTF-8
   export LANG=en_US.UTF-8
   ```

2. Install a font with good Unicode support:
   - macOS: SF Mono, Menlo
   - Linux: JetBrains Mono, Fira Code
   - Windows: Cascadia Code, Consolas

#### Progress Bar Flickering

**Symptom**: Status bar updates cause screen flicker

**Solutions**:
1. Disable status monitoring:
   ```bash
   export PROJECT_MANAGER_NO_STATUS=1
   poetry run project-manager
   ```

2. Increase refresh interval (edit `chat_interface.py:443`):
   ```python
   refresh_interval=5,  # Change from 2 to 5 seconds
   ```

#### Terminal Too Small

**Symptom**: Text wrapping or truncation

**Solutions**:
1. Resize terminal to minimum 80×24
2. Use full-screen mode (Cmd+Enter on macOS)
3. Reduce font size

#### Slow Rendering

**Symptom**: Lag when displaying large outputs

**Solutions**:
1. Limit table rows:
   ```python
   for priority in priorities[:20]:  # Limit to 20 rows
       table.add_row(...)
   ```

2. Disable streaming for large responses:
   ```bash
   export PROJECT_MANAGER_NO_STREAMING=1
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
export LOG_LEVEL=DEBUG
poetry run project-manager
```

Check logs in:
- `~/.coffee_maker/logs/project_manager.log`

---

## Terminal Compatibility

### Fully Supported

| Terminal | macOS | Linux | Windows | Notes |
|----------|-------|-------|---------|-------|
| iTerm2 | ✅ | - | - | Recommended on macOS |
| Terminal.app | ✅ | - | - | Default macOS terminal |
| Alacritty | ✅ | ✅ | ✅ | Fast, minimal |
| Kitty | ✅ | ✅ | - | Advanced features |
| GNOME Terminal | - | ✅ | - | Default on Ubuntu |
| Konsole | - | ✅ | - | KDE default |
| Windows Terminal | - | - | ✅ | Recommended on Windows |

### Partially Supported

| Terminal | Limitations |
|----------|-------------|
| tmux | Status bar may conflict with tmux status |
| screen | Limited Unicode support |
| SSH (slow connection) | Disable streaming for better performance |

### Not Supported

- Command Prompt (cmd.exe) - Use Windows Terminal or PowerShell
- Very old terminal emulators (pre-2015)

### Recommended Settings

**iTerm2** (macOS):
- Profile → Terminal → Report Terminal Type: `xterm-256color`
- Profile → Text → Font: SF Mono 12pt
- Profile → Colors → Color Presets: Solarized Dark/Light

**GNOME Terminal** (Linux):
- Preferences → Profiles → Colors → Built-in schemes: Tango Dark/Light
- Preferences → Profiles → Text → Custom font: JetBrains Mono 11pt

**Windows Terminal**:
- Settings → Profiles → Defaults → Appearance → Color scheme: One Half Dark
- Settings → Profiles → Defaults → Appearance → Font face: Cascadia Code

---

## Advanced Customization

See [UI_CUSTOMIZATION.md](./UI_CUSTOMIZATION.md) for detailed customization options including:

- Environment variables
- Custom color schemes
- Terminal-specific settings
- Performance tuning
- Font recommendations

---

## See Also

- [CONSOLE_UI_EXAMPLES.md](./CONSOLE_UI_EXAMPLES.md) - Code examples and recipes
- [KEYBOARD_SHORTCUTS_REFERENCE.md](./KEYBOARD_SHORTCUTS_REFERENCE.md) - Complete shortcut guide
- [US-036-CONSOLE_UI_POLISH_GUIDE.md](./US-036-CONSOLE_UI_POLISH_GUIDE.md) - Technical specification

---

**Last Updated**: 2025-10-20 | **Status**: Production ✅
