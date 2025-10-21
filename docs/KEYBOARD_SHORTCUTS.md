# Keyboard Shortcuts Reference

**Related**: US-036: Polish Console UI to Claude-CLI Quality
**Status**: ✅ Complete
**Last Updated**: 2025-10-20

## Overview

This document provides a complete reference of all keyboard shortcuts available in the project-manager chat interface. The shortcuts are designed to match claude-cli conventions and provide professional keyboard-driven workflow.

---

## Quick Reference Card

### Most Common Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `↑` / `↓` | Navigate history | Input prompt |
| `Tab` | Autocomplete | Input prompt |
| `Ctrl+R` | Search history | Input prompt |
| `Alt+Enter` | Multi-line input | Input prompt |
| `Enter` | Submit | Input prompt |
| `/exit` | Exit chat | Anywhere |
| `/help` | Show help | Anywhere |

**Print this section for quick reference!**

---

## Complete Shortcut List

### Input Navigation & Editing

#### Cursor Movement

| Shortcut | Action | Example |
|----------|--------|---------|
| `←` / `→` | Move cursor left/right by character | Navigate within line |
| `Ctrl+A` | Move to beginning of line | Jump to start |
| `Ctrl+E` | Move to end of line | Jump to end |
| `Alt+B` | Move backward one word | `poetry run` → `poetry│run` |
| `Alt+F` | Move forward one word | `poetry│run` → `poetry run│` |
| `Home` | Move to beginning (alternative) | Same as Ctrl+A |
| `End` | Move to end (alternative) | Same as Ctrl+E |

#### Text Deletion

| Shortcut | Action | Example |
|----------|--------|---------|
| `Backspace` | Delete character before cursor | Standard delete |
| `Delete` | Delete character after cursor | Forward delete |
| `Ctrl+H` | Delete character before cursor | Alternative to Backspace |
| `Ctrl+D` | Delete character after cursor (or EOF) | Alternative to Delete |
| `Ctrl+K` | Delete from cursor to end of line | `hello│world` → `hello` |
| `Ctrl+U` | Delete from cursor to start of line | `hello│world` → `world` |
| `Ctrl+W` | Delete word before cursor | `poetry run│code` → `poetry │code` |
| `Alt+D` | Delete word after cursor | `poetry│run code` → `poetry│code` |

---

## Session Control

### Exit Commands

| Shortcut | Action | Behavior |
|----------|--------|----------|
| `/exit` | Exit gracefully | Saves session, shows goodbye |
| `/quit` | Exit gracefully (alias) | Same as `/exit` |
| `Ctrl+D` | EOF signal / Exit | Exit if line is empty |
| `Ctrl+C` | Interrupt | Shows "Type /exit to quit" |

**Ctrl+D Behavior**:
- **Empty line**: Exits chat
- **Non-empty line**: Deletes character after cursor

**Ctrl+C Behavior**:
- **During input**: Clears current line
- **During response**: Shows interruption message
- **Repeated**: Does NOT force quit (use `/exit`)

---

## Command History

### History Navigation

| Shortcut | Action | Usage |
|----------|--------|-------|
| `↑` | Previous command | Step backwards in history |
| `↓` | Next command | Step forwards in history |
| `Ctrl+P` | Previous command (alternative) | Same as `↑` |
| `Ctrl+N` | Next command (alternative) | Same as `↓` |
| `Ctrl+R` | Reverse search | Type to search history |

### History Search (Ctrl+R)

When you press `Ctrl+R`, you enter reverse search mode:

**How to use**:
1. Press `Ctrl+R`
2. Start typing search term
3. Press `Ctrl+R` again to find next match
4. Press `Enter` to execute found command
5. Press `Ctrl+G` or `Ctrl+C` to cancel

**Example**:
```
(reverse-i-search)`status': /status
```

---

## Autocompletion

### Tab Completion

| Shortcut | Action | Completes |
|----------|--------|-----------|
| `Tab` | Show completions | Commands, priority names |
| `Tab` `Tab` | Show all completions | Full list of matches |

**Example**:
```
You
› /vie<Tab>
› /view

You
› /view PRIOR<Tab>
› /view PRIORITY
```

---

## Multi-line Input

### Creating Multi-line Input

| Shortcut | Action | Mode |
|----------|--------|------|
| `Alt+Enter` | Insert newline | Multi-line mode |
| `Enter` | Submit input | Single-line mode |

**Example Multi-line**:
```
You
› Implement authentication system<Alt+Enter>
... Requirements:<Alt+Enter>
... - JWT tokens<Alt+Enter>
... - Password hashing<Enter>
```

---

## Related Documentation

- [Console UI Guide](CONSOLE_UI_GUIDE.md) - Complete UI documentation
- [UI Customization](UI_CUSTOMIZATION.md) - Customize appearance
- [Project Manager CLI Usage](PROJECT_MANAGER_CLI_USAGE.md) - CLI commands

---

**Last Updated**: 2025-10-20
**Status**: Production Ready ✅
