# Console UI Guide - MonolithicCoffeeMakerAgent

**Related**: US-036: Polish Console UI to Claude-CLI Quality
**Status**: ✅ Complete
**Last Updated**: 2025-10-20

## Overview

MonolithicCoffeeMakerAgent features a polished, professional console UI that rivals claude-cli in quality and user experience. This guide documents the UI features, implementation, and best practices.

## Table of Contents

1. [Key Features](#key-features)
2. [Color Scheme & Visual Language](#color-scheme--visual-language)
3. [Interactive Features](#interactive-features)
4. [Usage Examples](#usage-examples)
5. [Developer Guide](#developer-guide)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)

---

## Key Features

### 1. Rich Text Formatting

The UI uses the `rich` library for professional terminal output:

- **Color-coded messages**: Info (blue), Success (green), Warning (yellow), Error (red)
- **Status symbols**: ✓ ✗ ⚠ ℹ ⚙ 🧠 💤
- **Tables and panels**: Structured data display
- **Progress indicators**: Spinners and progress bars
- **Markdown rendering**: Rich text responses

### 2. Advanced Input Handling

Using `prompt_toolkit` for sophisticated input:

- **Command history**: Navigate with ↑/↓ arrows
- **Auto-suggestions**: Based on command history
- **TAB completion**: Command and argument completion
- **Multi-line input**: For complex prompts
- **Keyboard shortcuts**: Ctrl+C, Ctrl+D, Ctrl+L, Ctrl+R

### 3. Real-time Status Monitoring

Background status monitor displays:

- Current task and priority
- Iteration count
- Time elapsed and ETA
- Progress visualization

---

## Color Scheme & Visual Language

### Color Palette

```python
COLORS = {
    "info": "blue",        # Informational messages
    "success": "green",    # Successful operations
    "warning": "yellow",   # Warnings and cautions
    "error": "red",        # Errors and failures
    "muted": "dim white",  # Secondary information
    "highlight": "cyan",   # Highlighted text
    "accent": "magenta",   # Accent elements
}
```

### Status Symbols

```python
SYMBOLS = {
    "success": "✓",      # Successful completion
    "error": "✗",        # Errors
    "warning": "⚠",      # Warnings
    "info": "ℹ",         # Information
    "working": "⚙",      # In progress
    "thinking": "🧠",    # Processing
    "idle": "💤",        # Waiting/idle
}
```

### Visual Hierarchy

1. **Section Headers**: Bold cyan with horizontal rules
2. **Primary Content**: Normal weight, high contrast
3. **Secondary Content**: Muted (dim white)
4. **Status Messages**: Color-coded with symbols
5. **Error Messages**: Red with suggestions in blue

---

## Interactive Features

### Command History

History is persisted to `.project_manager_history`:

```bash
# Navigate history
↑   # Previous command
↓   # Next command

# Search history
Ctrl+R  # Reverse search through history
```

**Example**:
```
> /roadmap
> /status
> chat What's the current priority?

# Press ↑ to get: chat What's the current priority?
# Press ↑ again to get: /status
```

### Auto-completion

TAB completion for commands and arguments:

```bash
# Type /ro and press TAB
> /ro<TAB>
> /roadmap

# Available commands:
/roadmap, /status, /notifications, /verify-dod,
/github-status, /help, /exit, /standup
```

### Multi-line Input

For long prompts, use natural line breaks:

```
> chat Please analyze the current roadmap
... and identify the top 3 priorities
... that we should focus on this week

# Lines continue until you press Enter twice
```

---

## Usage Examples

### 1. Starting a Chat Session

```bash
$ poetry run project-manager chat

╭─────────────────────────────────────────────────╮
│    MonolithicCoffeeMakerAgent Project Manager  │
│                                                 │
│    Type /help for commands                     │
│    Type 'exit' or press Ctrl+D to quit        │
╰─────────────────────────────────────────────────╯

⚫ code_developer: Not running

>
```

### 1b. Available Commands (Real Examples)

```bash
# View roadmap
$ poetry run project-manager view

# Show daemon status
$ poetry run project-manager status

# Show developer status dashboard
$ poetry run project-manager developer-status

# Check notifications
$ poetry run project-manager notifications

# Respond to notification
$ poetry run project-manager respond 5 approve

# Generate technical specification
$ poetry run project-manager spec PRIORITY-2.8

# Show spec metrics
$ poetry run project-manager spec-metrics

# Start interactive AI chat
$ poetry run project-manager chat
```

### 2. Success Message Example

```python
from coffee_maker.cli.console_ui import success

success("Priority PRIORITY-2.6 completed!",
        details="All tests passed, documentation updated")
```

**Output**:
```
✓ Priority PRIORITY-2.6 completed!
   All tests passed, documentation updated
```

### 3. Error Message with Suggestions

```python
from coffee_maker.cli.console_ui import error

error("Failed to read ROADMAP.md",
      suggestion="Check that the file exists in docs/roadmap/",
      details="FileNotFoundError: No such file or directory")
```

**Output**:
```
✗ Error: Failed to read ROADMAP.md
   💡 Suggestion: Check that the file exists in docs/roadmap/
   Details: FileNotFoundError: No such file or directory
```

### 4. Progress Indicator

```python
from coffee_maker.cli.console_ui import progress_context

with progress_context("Analyzing roadmap...") as progress:
    task = progress.add_task("Processing", total=100)
    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

**Output**:
```
⠋ Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  45% 0:00:12
```

### 5. Formatted Table

```python
from coffee_maker.cli.console_ui import create_table, console

table = create_table(
    title="Current Priorities",
    columns=["ID", "Title", "Status", "Effort"]
)
table.add_row("PRIORITY-2.6", "ACE Framework", "✅ Complete", "3 days")
table.add_row("PRIORITY-2.7", "UI Polish", "🔄 In Progress", "2 days")
console.print(table)
```

**Output**:
```
         Current Priorities
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┓
┃ ID          ┃ Title       ┃ Status      ┃ Effort┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━┩
│ PRIORITY-2.6│ ACE Framework│ ✅ Complete│ 3 days│
│ PRIORITY-2.7│ UI Polish   │ 🔄 In Progress│ 2 days│
└─────────────┴─────────────┴─────────────┴───────┘
```

### 6. Notification Display

```python
from coffee_maker.cli.console_ui import format_notification, console

panel = format_notification(
    notif_type="question",
    title="Approval Required",
    message="Ready to implement PRIORITY-2.8?",
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
│ Ready to implement PRIORITY-2.8?                 │
│                                                  │
│ Created: 2025-10-20 14:30:00                    │
╰──────────────────────────────────────────────────╯
```

---

## Developer Guide

### Using Console UI in Your Code

Import the centralized console UI utilities:

```python
from coffee_maker.cli.console_ui import (
    console,           # Shared console instance
    success,           # Success messages
    error,             # Error messages
    warning,           # Warning messages
    info,              # Info messages
    section_header,    # Section headers
    create_table,      # Create tables
    create_panel,      # Create panels
    progress_context,  # Progress indicators
)
```

### Best Practices

#### 1. Consistent Messaging

```python
# ✅ Good: Use helper functions
success("Task completed successfully!")

# ❌ Bad: Direct console.print with manual styling
console.print("[green]✓[/green] Task completed successfully!")
```

#### 2. Helpful Error Messages

```python
# ✅ Good: Include suggestions
error("Database connection failed",
      suggestion="Check DATABASE_URL in .env file",
      details=str(e))

# ❌ Bad: Generic error
console.print(f"[red]Error: {e}[/red]")
```

#### 3. Visual Hierarchy

```python
# ✅ Good: Use section headers
section_header("Roadmap Analysis", "Analyzing current priorities")
# ... content ...

# ❌ Bad: No visual separation
console.print("Roadmap Analysis")
# ... content ...
```

#### 4. Progress Feedback

```python
# ✅ Good: Show progress for long operations
with progress_context("Analyzing roadmap...") as progress:
    task = progress.add_task("Processing", total=len(items))
    for item in items:
        # Process item
        progress.update(task, advance=1)

# ❌ Bad: No feedback during long operations
for item in items:
    # Process item (user sees nothing)
    pass
```

### Architecture

**Location**: `coffee_maker/cli/console_ui.py:1`

**Dependencies**:
- `rich>=13.0.0`: Rich text formatting
- `prompt_toolkit>=3.0.47`: Advanced input handling

**Key Components**:

1. **Shared Console Instance** (`console`): Single console for consistent output
2. **Helper Functions**: `success()`, `error()`, `warning()`, `info()`
3. **Formatting Functions**: `create_table()`, `create_panel()`, `format_list()`
4. **Progress Utilities**: `progress_context()`
5. **Color Scheme**: Consistent color palette across all commands

---

## Keyboard Shortcuts

### Input Navigation

| Shortcut | Action |
|----------|--------|
| `↑` | Previous command in history |
| `↓` | Next command in history |
| `Ctrl+A` | Move cursor to beginning of line |
| `Ctrl+E` | Move cursor to end of line |
| `Ctrl+K` | Delete from cursor to end of line |
| `Ctrl+U` | Delete from cursor to beginning of line |
| `Ctrl+W` | Delete word before cursor |
| `Alt+B` | Move cursor back one word |
| `Alt+F` | Move cursor forward one word |

### Command Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Graceful exit (with confirmation) |
| `Ctrl+D` | Exit (standard Unix convention) |
| `Ctrl+L` | Clear screen |
| `Ctrl+R` | Reverse search through history |
| `TAB` | Command/argument autocomplete |

### Multi-line Input

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit single-line input |
| `Shift+Enter` | Continue to next line (multi-line mode) |
| `Enter` twice | Submit multi-line input |

---

## Troubleshooting

### Issue: Colors Not Displaying

**Symptoms**: Text appears without colors, formatting looks broken

**Causes**:
- Terminal doesn't support colors
- `NO_COLOR` environment variable is set
- Output is piped/redirected

**Solutions**:
```bash
# Check terminal capabilities
echo $TERM
# Should show: xterm-256color, screen-256color, etc.

# Unset NO_COLOR if set
unset NO_COLOR

# Use a modern terminal emulator
# Recommended: iTerm2 (macOS), Windows Terminal, GNOME Terminal
```

### Issue: Command History Not Working

**Symptoms**: ↑/↓ arrows don't navigate history

**Causes**:
- History file not writable
- `prompt_toolkit` not installed correctly

**Solutions**:
```bash
# Check history file permissions
ls -la ~/.coffee_maker/.project_manager_history
chmod 644 ~/.coffee_maker/.project_manager_history

# Reinstall prompt_toolkit
poetry install --sync
```

### Issue: Unicode Symbols Not Displaying

**Symptoms**: Status symbols show as `?` or boxes

**Causes**:
- Terminal encoding not set to UTF-8
- Font doesn't support Unicode

**Solutions**:
```bash
# Check encoding
locale
# Should show: LANG=en_US.UTF-8

# Set UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Use a font with Unicode support
# Recommended: Fira Code, JetBrains Mono, Cascadia Code
```

### Issue: Terminal Resize Breaks Formatting

**Symptoms**: Tables and panels don't resize correctly

**Causes**:
- Rich library needs to detect resize
- Terminal emulator doesn't send SIGWINCH

**Solutions**:
```bash
# Restart the chat session
# The console will recalculate dimensions on startup

# If persistent, try a different terminal emulator
```

### Issue: Autocomplete Not Working

**Symptoms**: TAB key inserts tab character instead of completing

**Causes**:
- `prompt_toolkit` completer not configured
- Terminal in raw mode

**Solutions**:
```bash
# Restart the application
poetry run project-manager chat

# If persistent, check for conflicting readline configuration
# Remove or rename ~/.inputrc
```

---

## Performance Considerations

### Memory Usage

The console UI is designed to be lightweight:

- **Shared console instance**: Single instance across all commands
- **Lazy rendering**: Tables and panels only rendered when printed
- **Stream processing**: Large outputs streamed, not buffered

### Terminal Compatibility

Tested on:
- ✅ iTerm2 (macOS)
- ✅ Terminal.app (macOS)
- ✅ VS Code integrated terminal
- ✅ Windows Terminal
- ✅ GNOME Terminal (Linux)
- ✅ Konsole (KDE)
- ⚠️ Basic terminals (limited color support)

### Responsive Design

The UI adapts to terminal size:

- **Minimum size**: 80x24 (standard terminal)
- **Recommended size**: 120x40 or larger
- **Automatic wrapping**: Long lines wrap gracefully
- **Table overflow**: Tables adapt to available width

---

## Related Documentation

- **Technical Specification**: `docs/architecture/specs/SPEC-036-console-ui-polish.md`
- **Implementation**: `coffee_maker/cli/console_ui.py:1`
- **Chat Interface**: `coffee_maker/cli/chat_interface.py:1`
- **ROADMAP Entry**: `docs/roadmap/ROADMAP.md:23698` (US-036)

---

## Future Enhancements

1. **Custom Themes**: User-configurable color schemes
2. **Plugin System**: Extend UI with custom components
3. **Voice Input**: Optional voice command support
4. **Keyboard Macros**: Record and replay command sequences
5. **Split Panes**: Show status in sidebar while chatting
6. **Search**: Search through conversation history
7. **Export**: Export conversations to markdown/HTML

---

## Changelog

### 2025-10-20 - Initial Release (US-036)
- ✅ Professional console UI matching claude-cli quality
- ✅ Rich text formatting with consistent color scheme
- ✅ Advanced input handling with history and autocomplete
- ✅ Real-time status monitoring
- ✅ Progress indicators and loading spinners
- ✅ Helpful error messages with suggestions
- ✅ Comprehensive keyboard shortcuts
- ✅ Terminal resize handling
- ✅ Multi-line input support

---

**Last Updated**: 2025-10-20
**Maintained By**: MonolithicCoffeeMakerAgent Team
**Status**: Production Ready ✅
