# Keyboard Shortcuts Reference - Project Manager Console

**Related**: US-036: Polish Console UI to Claude-CLI Quality
**Quick Reference Card**
**Last Updated**: 2025-10-20

---

## Essential Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+C` | **Graceful Exit** | Exit with confirmation prompt |
| `Ctrl+D` | **Quick Exit** | Exit immediately (Unix standard) |
| `Ctrl+L` | **Clear Screen** | Clear terminal display |
| `TAB` | **Autocomplete** | Complete command or argument |
| `↑` / `↓` | **Navigate History** | Browse previous commands |
| `Ctrl+R` | **Search History** | Reverse search through history |

---

## Input Navigation

### Cursor Movement

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Move to **start** of line |
| `Ctrl+E` | Move to **end** of line |
| `Alt+B` | Move back one **word** |
| `Alt+F` | Move forward one **word** |
| `Home` | Move to start of line (alternative) |
| `End` | Move to end of line (alternative) |

### Text Editing

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Delete from cursor to **end** of line |
| `Ctrl+U` | Delete from cursor to **start** of line |
| `Ctrl+W` | Delete **word** before cursor |
| `Alt+D` | Delete **word** after cursor |
| `Ctrl+Y` | Paste (yank) deleted text |
| `Backspace` | Delete character before cursor |
| `Delete` | Delete character after cursor |

---

## History Management

| Shortcut | Action | Details |
|----------|--------|---------|
| `↑` | Previous command | Navigate backward in history |
| `↓` | Next command | Navigate forward in history |
| `Ctrl+R` | Reverse search | Type to search history, Enter to use |
| `Ctrl+S` | Forward search | Search forward (if enabled) |
| `Ctrl+G` | Cancel search | Exit search mode |

### History File

- **Location**: `~/.coffee_maker/.project_manager_history`
- **Format**: Plain text, one command per line
- **Size limit**: Last 1000 commands
- **Persistence**: Saved on exit, loaded on start

---

## Multi-line Input

| Action | How To |
|--------|--------|
| **Start multi-line** | Type normally, press `Shift+Enter` to continue |
| **Add new line** | `Shift+Enter` |
| **Submit** | Press `Enter` without Shift |
| **Cancel** | `Ctrl+C` |

**Example**:
```
> chat Please analyze the roadmap<Shift+Enter>
... and identify priorities that:<Shift+Enter>
... 1. Need architectural review<Shift+Enter>
... 2. Are blocked<Enter>
```

---

## Command Autocomplete

### How It Works

1. Type the beginning of a command: `/ro`
2. Press `TAB`
3. Command completes to: `/roadmap`

### Available Commands

```
/roadmap              View ROADMAP
/status               Developer status
/notifications        View notifications
/verify-dod          Verify Definition of Done
/github-status       GitHub PR/issue status
/standup             Daily standup report
/help                Show help
/exit                Exit chat
```

### Autocomplete Features

- **Case insensitive**: `/RO<TAB>` → `/roadmap`
- **Partial match**: `/not<TAB>` → `/notifications`
- **Cycling**: Press `TAB` multiple times to cycle through matches
- **Arguments**: Some commands autocomplete arguments too

---

## Terminal Control

| Shortcut | Action | Notes |
|----------|--------|-------|
| `Ctrl+C` | Interrupt | Shows confirmation: "Exit? (y/n)" |
| `Ctrl+D` | EOF Signal | Exits immediately |
| `Ctrl+Z` | Suspend | Sends to background (resume with `fg`) |
| `Ctrl+L` | Clear Screen | Clears display, keeps history |
| `Ctrl+S` | Pause Output | Freezes display (Unix terminals) |
| `Ctrl+Q` | Resume Output | Resumes display after Ctrl+S |

---

## Advanced Features

### Reverse Search (Ctrl+R)

1. Press `Ctrl+R`
2. Type search term: `roadmap`
3. See matching command: `/roadmap`
4. Press `Enter` to execute
5. Or press `Ctrl+R` again for next match

**Example**:
```
> <Ctrl+R>
(reverse-i-search)`road': /roadmap
```

### Prefix Search (↑/↓)

1. Type prefix: `/not`
2. Press `↑`
3. Shows last command starting with `/not`: `/notifications`

### Word Jumping

Navigate by word instead of character:

- `Alt+B`: Jump back one word
- `Alt+F`: Jump forward one word

**Example** (cursor position shown as `|`):
```
chat analyze the |roadmap and identify priorities
<Alt+B>
chat analyze the| roadmap and identify priorities
<Alt+B>
chat analyze |the roadmap and identify priorities
```

---

## Copy and Paste

### From Terminal

| Action | Shortcut (macOS) | Shortcut (Linux/Windows) |
|--------|------------------|--------------------------|
| **Copy** | `Cmd+C` | `Ctrl+Shift+C` |
| **Paste** | `Cmd+V` | `Ctrl+Shift+V` |
| **Select All** | `Cmd+A` | `Ctrl+Shift+A` |

### Within Input Line

| Action | Shortcut |
|--------|----------|
| **Copy line** | `Ctrl+K` then `Ctrl+Y` (kill and yank) |
| **Paste** | `Ctrl+Y` (yank) |

---

## Tips and Tricks

### 1. Quick Command Recall

Instead of typing `/roadmap` every time:
1. Type `/ro`
2. Press `TAB` → completes to `/roadmap`
3. Press `Enter`

### 2. Repeat Last Command

1. Press `↑` once
2. Press `Enter`

### 3. Edit Previous Command

1. Press `↑` to recall
2. Edit with navigation keys
3. Press `Enter`

### 4. Search Command History

For frequently used complex commands:
1. Press `Ctrl+R`
2. Type a keyword from the command
3. Press `Enter` when found

### 5. Clear Screen Without Losing History

- Press `Ctrl+L` to clear display
- History remains accessible with `↑`

### 6. Multi-line Chat Prompts

For detailed questions:
```
> chat Please analyze<Shift+Enter>
... the current priorities<Shift+Enter>
... and identify blockers<Enter>
```

### 7. Graceful Exit

- `Ctrl+C` → Confirmation prompt → Type `y` → Exits
- `Ctrl+D` → Exits immediately

---

## Troubleshooting

### Shortcuts Not Working

**Problem**: Keyboard shortcuts don't respond

**Solutions**:
1. Check if `prompt_toolkit` is installed: `poetry show | grep prompt-toolkit`
2. Verify terminal supports key codes: Try in different terminal
3. Check for conflicting `~/.inputrc` configuration
4. Restart the application: `poetry run project-manager chat`

### History Not Saving

**Problem**: Command history doesn't persist between sessions

**Solutions**:
1. Check history file exists: `ls -la ~/.coffee_maker/.project_manager_history`
2. Check file permissions: `chmod 644 ~/.coffee_maker/.project_manager_history`
3. Ensure directory is writable: `chmod 755 ~/.coffee_maker/`

### Autocomplete Not Working

**Problem**: TAB key inserts tab character instead of completing

**Solutions**:
1. Verify you're using the interactive chat mode: `poetry run project-manager chat`
2. Check for conflicting readline configuration
3. Try in a fresh terminal session

### Unicode Symbols Missing

**Problem**: Symbols (✓ ✗ ⚠) show as `?` or boxes

**Solutions**:
1. Set UTF-8 encoding: `export LANG=en_US.UTF-8`
2. Use a font with Unicode support (Fira Code, JetBrains Mono)
3. Check terminal locale: `locale`

---

## Platform-Specific Notes

### macOS

- **Terminal.app**: Full support, all shortcuts work
- **iTerm2**: Full support, recommended terminal
- **VS Code**: Full support in integrated terminal
- **Copy/Paste**: Use `Cmd+C` / `Cmd+V`

### Linux

- **GNOME Terminal**: Full support
- **Konsole (KDE)**: Full support
- **Terminator**: Full support
- **Copy/Paste**: Usually `Ctrl+Shift+C` / `Ctrl+Shift+V`

### Windows

- **Windows Terminal**: Full support, recommended
- **PowerShell**: Partial support (some keys differ)
- **WSL**: Full support in Linux terminals
- **Copy/Paste**: `Ctrl+Shift+C` / `Ctrl+Shift+V`

---

## Quick Reference Card (Printable)

```
┌─────────────────────────────────────────────────────────────┐
│        PROJECT MANAGER - KEYBOARD SHORTCUTS                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ESSENTIAL                                                  │
│    Ctrl+C     Graceful exit (with confirmation)            │
│    Ctrl+D     Quick exit (immediate)                       │
│    Ctrl+L     Clear screen                                 │
│    TAB        Autocomplete command                         │
│    ↑ / ↓      Navigate command history                     │
│    Ctrl+R     Search command history                       │
│                                                             │
│  NAVIGATION                                                 │
│    Ctrl+A     Start of line                                │
│    Ctrl+E     End of line                                  │
│    Alt+B      Back one word                                │
│    Alt+F      Forward one word                             │
│                                                             │
│  EDITING                                                    │
│    Ctrl+K     Delete to end of line                        │
│    Ctrl+U     Delete to start of line                      │
│    Ctrl+W     Delete word before cursor                    │
│    Ctrl+Y     Paste deleted text                           │
│                                                             │
│  MULTI-LINE                                                 │
│    Shift+Enter    Add new line                             │
│    Enter          Submit input                             │
│                                                             │
│  COMMANDS                                                   │
│    /roadmap       View ROADMAP                             │
│    /status        Developer status                         │
│    /notifications View notifications                       │
│    /verify-dod    Verify Definition of Done                │
│    /help          Show help                                │
│    /exit          Exit application                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Learning Path

### Beginner (Week 1)

Start with these essential shortcuts:
- `↑` / `↓` for command history
- `TAB` for autocomplete
- `Ctrl+C` to exit
- `Ctrl+L` to clear screen

### Intermediate (Week 2-3)

Add these to your workflow:
- `Ctrl+R` for history search
- `Ctrl+A` / `Ctrl+E` for line navigation
- `Shift+Enter` for multi-line input
- `Alt+B` / `Alt+F` for word navigation

### Advanced (Week 4+)

Master these for efficiency:
- `Ctrl+K` / `Ctrl+U` for line editing
- `Ctrl+W` for word deletion
- `Ctrl+Y` for paste
- Custom keyboard macros (if terminal supports)

---

## Related Documentation

- **Console UI Guide**: `docs/CONSOLE_UI_GUIDE.md`
- **Console UI Examples**: `docs/CONSOLE_UI_EXAMPLES.md`
- **Implementation**: `coffee_maker/cli/console_ui.py:1`
- **Chat Interface**: `coffee_maker/cli/chat_interface.py:1`
- **ROADMAP**: `docs/roadmap/ROADMAP.md:23698` (US-036)

---

**Print this page and keep it handy for quick reference!**

**Last Updated**: 2025-10-20
**Status**: Production Ready ✅
**US-036**: Console UI Polish - Complete
