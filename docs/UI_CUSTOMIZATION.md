# UI Customization Guide

**Related**: US-036: Polish Console UI to Claude-CLI Quality
**Status**: ✅ Complete
**Last Updated**: 2025-10-20

## Overview

This guide explains how to customize the project-manager console UI to match your preferences and terminal environment. While the UI is designed to work beautifully out-of-the-box, these customization options let you fine-tune the experience.

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Terminal Configuration](#terminal-configuration)
3. [Color Schemes](#color-schemes)
4. [Font Recommendations](#font-recommendations)
5. [Performance Tuning](#performance-tuning)
6. [Advanced Customization](#advanced-customization)

---

## Environment Variables

### Disable Streaming Responses

If streaming is too fast, too slow, or causing display issues:

```bash
export PROJECT_MANAGER_NO_STREAMING=1
poetry run project-manager
```

**When to use**:
- Debugging response generation
- Slow network connections
- Terminal display issues
- Preference for instant responses

**Default**: Streaming enabled

### Adjust Status Monitor Refresh Rate

Currently hardcoded to 2 seconds, but can be modified in code:

```python
# In chat_interface.py:393
self.status_monitor = DeveloperStatusMonitor(poll_interval=2.0)

# Change to 5 seconds for less frequent updates:
self.status_monitor = DeveloperStatusMonitor(poll_interval=5.0)

# Or 1 second for more responsive updates:
self.status_monitor = DeveloperStatusMonitor(poll_interval=1.0)
```

**Recommended**: 2-5 seconds (balance between responsiveness and CPU usage)

### Debug Logging

Enable detailed logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG
poetry run project-manager 2> debug.log
```

**Output**:
- Session initialization
- Command routing
- AI service calls
- Status updates
- Error details

---

## Terminal Configuration

### macOS Terminal.app

**Recommended Settings**:

1. **Appearance**:
   - Theme: Solarized Dark or Solarized Light
   - Font: Monaco 14pt or SF Mono 14pt
   - Window Size: 120 columns × 40 rows

2. **Keyboard**:
   - ☑ Use Option as Meta key
   - Enables Alt+Enter, Alt+F, Alt+B shortcuts

3. **Terminal**:
   - Scrollback: 10000 lines
   - Character Encoding: UTF-8

**Steps**:
```
Terminal → Preferences → Profiles
→ Select your profile
→ Text tab: Set font and colors
→ Keyboard tab: Enable "Use Option as Meta key"
→ Window tab: Set size to 120×40
```

### iTerm2 (macOS)

**Recommended Settings**:

1. **Appearance**:
   - Color Preset: Solarized Dark, Dracula, or Nord
   - Font: JetBrains Mono 14pt or Fira Code 14pt
   - Window Size: 120×40 or larger

2. **Keyboard**:
   - Left Option Key: Esc+
   - Right Option Key: Normal (for special characters)

3. **Terminal**:
   - Scrollback Lines: Unlimited
   - Terminal Type: xterm-256color

**Steps**:
```
iTerm2 → Preferences → Profiles
→ Colors: Choose color preset
→ Text: Set font
→ Window: Set columns=120, rows=40
→ Keys → General: Set Left Option Key to "Esc+"
```

### VS Code Terminal

**Recommended Settings** (settings.json):

```json
{
  "terminal.integrated.fontSize": 14,
  "terminal.integrated.fontFamily": "JetBrains Mono, Fira Code, monospace",
  "terminal.integrated.lineHeight": 1.2,
  "terminal.integrated.scrollback": 10000,
  "terminal.integrated.cursorBlinking": true,
  "terminal.integrated.cursorStyle": "line"
}
```

**Steps**:
```
Code → Preferences → Settings
→ Search: "terminal.integrated"
→ Configure as above
```

### GNOME Terminal (Linux)

**Recommended Settings**:

1. **Appearance**:
   - Color Scheme: Tango Dark or Solarized Dark
   - Font: DejaVu Sans Mono 12pt or Ubuntu Mono 13pt
   - Window Size: 120×40

2. **Keyboard**:
   - Alt key typically works by default
   - Verify: Alt+F, Alt+B work in shell

3. **Terminal**:
   - Scrollback: 10000 lines
   - Encoding: UTF-8

**Steps**:
```
Edit → Preferences → Profiles
→ Colors: Select scheme
→ Text: Set font
→ Scrolling: Set scrollback limit
```

### Windows Terminal

**Recommended Settings** (settings.json):

```json
{
  "profiles": {
    "defaults": {
      "fontSize": 12,
      "fontFace": "Cascadia Code, Consolas",
      "colorScheme": "One Half Dark",
      "historySize": 10000,
      "cursorShape": "bar"
    }
  }
}
```

**Steps**:
```
Settings (Ctrl+,)
→ Profiles → Defaults
→ Appearance: Set font and color scheme
→ Advanced: Set history size
```

---

## Color Schemes

### Built-in Themes

The UI adapts to your terminal's color scheme. Popular themes:

**Dark Themes**:
- Solarized Dark (recommended)
- Dracula
- Nord
- One Dark
- Monokai
- Tomorrow Night

**Light Themes**:
- Solarized Light (recommended)
- GitHub Light
- Tomorrow
- One Light

### Color Customization

The UI uses semantic colors that adapt to your theme:

| UI Element | Color | Falls back to |
|------------|-------|---------------|
| Info | Blue | Terminal blue |
| Success | Green | Terminal green |
| Warning | Yellow | Terminal yellow |
| Error | Red | Terminal red |
| Muted | Dim white | Terminal dim |
| Highlight | Cyan | Terminal cyan |

**Testing Colors**:
```bash
# Run this to see your terminal's color palette
poetry run project-manager
/help
# Observe colors in the help table
```

### Syntax Highlighting

Code blocks use Pygments with Monokai theme:

```python
# In chat_interface.py:1257
syntax = Syntax(
    code,
    language,
    theme="monokai",  # Change theme here
    line_numbers=True,
    word_wrap=False,
)
```

**Available themes** (Pygments):
- `monokai` (default, dark)
- `solarized-dark`
- `solarized-light`
- `github-dark`
- `nord`
- `dracula`
- `one-dark`
- `zenburn`

**Example customization**:
```python
# For Solarized Dark terminal:
theme="solarized-dark"

# For GitHub Light terminal:
theme="github-light"
```

---

## Font Recommendations

### Monospace Fonts with Ligatures

**macOS**:
- JetBrains Mono (excellent ligatures)
- Fira Code (popular, good ligatures)
- SF Mono (Apple default, no ligatures)
- Monaco (classic, no ligatures)

**Linux**:
- JetBrains Mono
- Fira Code
- Ubuntu Mono
- DejaVu Sans Mono
- Source Code Pro

**Windows**:
- Cascadia Code (Microsoft, ligatures)
- JetBrains Mono
- Fira Code
- Consolas (default, no ligatures)

### Font Size

**Recommended sizes**:
- **Laptop (13-15")**: 12-14pt
- **Desktop (24"+)**: 14-16pt
- **4K Display**: 16-20pt
- **Accessibility**: 16-20pt

**Test readability**:
```bash
poetry run project-manager
/help
# Can you comfortably read the table?
```

### Unicode Support

**Required for UI icons**:
- ✅ ✓ ✗ ⚠ ℹ ⚙ 🧠 💤 🟢 🟡 🔴 ⚫
- ━ ┃ ┏ ┓ ┗ ┛ ├ ┤ ┬ ┴ ┼
- ▸ ► ▹ ▻ ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ░

**Fonts with excellent Unicode**:
- JetBrains Mono ⭐
- Fira Code ⭐
- Cascadia Code ⭐
- DejaVu Sans Mono

**Test Unicode**:
```bash
echo "✅ ✓ ✗ ⚠ ℹ 🟢 🟡 🔴"
# All symbols should display correctly
```

---

## Performance Tuning

### Reduce Memory Usage

**Session History**:
```bash
# Clear conversation history
rm ~/.project_manager/sessions/default.json

# Limit history size (manually edit after save)
# Keep only last 50 messages instead of all
```

**Command History**:
```bash
# Clear command history
rm ~/.project_manager/chat_history.txt

# Or limit size
tail -1000 ~/.project_manager/chat_history.txt > temp
mv temp ~/.project_manager/chat_history.txt
```

### Reduce CPU Usage

**Disable Status Monitor** (code change):
```python
# In chat_interface.py:393
# Comment out status monitor initialization
# self.status_monitor = DeveloperStatusMonitor(poll_interval=2.0)
```

**Increase Refresh Interval**:
```python
# From 2 seconds to 5 seconds
self.status_monitor = DeveloperStatusMonitor(poll_interval=5.0)
```

### Optimize Terminal

**macOS/Linux**:
```bash
# Disable unused terminal features
# ~/.bashrc or ~/.zshrc
unset PROMPT_COMMAND  # If not needed
```

**Windows**:
- Use Windows Terminal (more efficient than cmd.exe)
- Disable transparency/blur effects
- Limit scrollback to 5000-10000 lines

---

## Advanced Customization

### Modify Welcome Screen

**Location**: `coffee_maker/cli/chat_interface.py:1147`

```python
def _display_welcome(self):
    """Display welcome message with clean, claude-cli inspired formatting."""
    # Customize welcome message here
    self.console.print()
    self.console.print("[bold]Coffee Maker[/] [dim]·[/] AI Project Manager")
    self.console.print("[dim]Powered by Claude AI[/]")

    # Add custom branding:
    # self.console.print("[cyan]Your Company Name[/]")

    self.console.print()
```

### Customize Prompt

**Location**: `coffee_maker/cli/chat_interface.py:807-811`

```python
# Change prompt style
self.console.print("\n[bold]You[/]")  # Current

# Options:
# self.console.print("\n[bold cyan]You[/]")  # Cyan
# self.console.print("\n[bold]>[/]")  # Simple
# self.console.print("\n[bold]→[/]")  # Arrow
```

### Change Response Header

**Location**: `coffee_maker/cli/chat_interface.py:1196`

```python
# Change AI response header
self.console.print("\n[bold]Claude[/]")  # Current

# Options:
# self.console.print("\n[bold cyan]Assistant[/]")
# self.console.print("\n[bold magenta]AI[/]")
# self.console.print("\n[bold]▸ Response[/]")
```

### Custom Color Scheme

**Location**: Create `coffee_maker/cli/ui_config.py`:

```python
"""UI configuration and theme settings."""

THEME = {
    "info": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "muted": "dim white",
    "highlight": "cyan",
    "accent": "magenta",
}

# Use in code:
from coffee_maker.cli.ui_config import THEME
self.console.print(f"[{THEME['success']}]✓ Success![/]")
```

### Modify Status Bar Format

**Location**: `coffee_maker/cli/chat_interface.py:134-260`

```python
def get_formatted_status(self) -> str:
    """Customize status bar format here."""
    # Current: Multi-line with subtasks
    # Modify to single-line if preferred:

    return f"🟢 {priority_title} | {priority_name} | {elapsed_str} elapsed"
```

### Add Custom Commands

**Location**: Create new command handler in `coffee_maker/cli/commands/`

```python
# coffee_maker/cli/commands/custom_command.py
from coffee_maker.cli.commands.base import Command

class CustomCommand(Command):
    """Your custom command."""

    name = "custom"
    description = "Does something custom"

    def execute(self, args, editor):
        return "✅ Custom command executed!"
```

**Register** in `coffee_maker/cli/commands/__init__.py`:
```python
from coffee_maker.cli.commands.custom_command import CustomCommand

COMMANDS = {
    "custom": CustomCommand(),
    # ... other commands
}
```

---

## Troubleshooting Customization

### Colors Look Wrong

**Issue**: Colors don't match terminal theme

**Fix**:
1. Verify terminal supports 256 colors:
   ```bash
   echo $TERM
   # Should contain "256color"
   ```

2. Set correct TERM:
   ```bash
   export TERM=xterm-256color
   ```

3. Test colors:
   ```bash
   curl -s https://gist.githubusercontent.com/HaleTom/89ffe32783f89f403bba96bd7bcd1263/raw/ | bash
   ```

### Fonts Look Broken

**Issue**: Unicode symbols display as boxes

**Fix**:
1. Install font with Unicode support:
   ```bash
   # macOS
   brew tap homebrew/cask-fonts
   brew install --cask font-jetbrains-mono

   # Linux
   sudo apt install fonts-jetbrains-mono
   ```

2. Configure terminal to use new font

3. Verify:
   ```bash
   echo "✅ 🟢 ▸ █"
   ```

### Status Bar Not Visible

**Issue**: Bottom toolbar not showing

**Fix**:
1. Ensure terminal height ≥ 24 rows
2. Check prompt_toolkit version:
   ```bash
   poetry show prompt-toolkit
   # Should be >= 3.0.47
   ```

3. Restart project-manager

### Performance Issues

**Issue**: UI sluggish or laggy

**Fix**:
1. Disable streaming:
   ```bash
   export PROJECT_MANAGER_NO_STREAMING=1
   ```

2. Increase status refresh interval (see Performance Tuning)

3. Clear session history:
   ```bash
   rm ~/.project_manager/sessions/default.json
   ```

4. Use lighter terminal emulator

---

## Configuration File Locations

### User Data

```bash
~/.project_manager/
├── chat_history.txt          # Command history (readline)
└── sessions/
    └── default.json           # Conversation history
```

### Daemon Data

```bash
~/.coffee_maker/
└── daemon_status.json         # Daemon status (for status bar)
```

### Project Data

```bash
/path/to/MonolithicCoffeeMakerAgent/
├── .env                       # API keys and config
├── pyproject.toml             # Dependencies
└── coffee_maker/
    └── cli/
        ├── chat_interface.py  # Main chat UI
        └── console_ui.py      # UI components (if exists)
```

---

## Presets

### Minimal UI

For focus and minimal distraction:

```bash
# Disable status monitor (code change required)
# In chat_interface.py:776, comment out:
# self.status_monitor.start()

# Disable streaming
export PROJECT_MANAGER_NO_STREAMING=1

# Run
poetry run project-manager
```

### Maximum Information

For power users who want all the details:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Increase status refresh (code change)
# In chat_interface.py:393:
# self.status_monitor = DeveloperStatusMonitor(poll_interval=1.0)

# Run
poetry run project-manager 2> pm.log
```

### Accessibility

For better readability:

1. Large font: 18-20pt
2. High contrast theme: Solarized Light or GitHub Light
3. Disable animations:
   ```bash
   export PROJECT_MANAGER_NO_STREAMING=1
   ```
4. Increase terminal size: 100×50

---

## Related Documentation

- [Console UI Guide](CONSOLE_UI_GUIDE.md) - Complete UI features
- [Keyboard Shortcuts](KEYBOARD_SHORTCUTS.md) - All shortcuts
- [Project Manager CLI Usage](PROJECT_MANAGER_CLI_USAGE.md) - CLI commands
- [Workflows](WORKFLOWS.md) - Common workflows

---

## Feedback

Have ideas for new customization options?

**Submit Feature Requests**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues

**Popular Requests**:
- [ ] Configuration file for UI settings
- [ ] Multiple color themes
- [ ] Custom prompt formats
- [ ] Configurable shortcuts
- [ ] Plugin system

---

**Last Updated**: 2025-10-20
**Maintained By**: MonolithicCoffeeMakerAgent Team
**Status**: Production Ready ✅
