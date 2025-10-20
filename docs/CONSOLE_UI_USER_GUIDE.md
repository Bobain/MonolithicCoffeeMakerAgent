# Console UI User Guide

**Project Manager CLI - Professional Console Interface**

**Version**: US-036 Enhanced UI
**Last Updated**: 2025-10-20
**Target Users**: Developers, Project Managers, DevOps Engineers

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Visual Elements](#visual-elements)
4. [Keyboard Shortcuts](#keyboard-shortcuts)
5. [Commands](#commands)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Tricks](#tips--tricks)

---

## Introduction

### What is the Console UI?

The Project Manager console UI is a professional, interactive command-line interface for managing your software development workflow. It provides:

- 🎨 **Beautiful, colored output** with rich formatting
- ⚡ **Streaming AI responses** for real-time feedback
- ⌨️ **Keyboard shortcuts** for efficient navigation
- 📝 **Command history** with autocomplete
- 🔍 **Smart search** through previous commands
- 📊 **Progress indicators** for long operations

### Why Use It?

- **Professional**: Polished UI matching industry-leading tools like claude-cli
- **Efficient**: Keyboard shortcuts and autocomplete save time
- **Intuitive**: Clear visual feedback and helpful error messages
- **Powerful**: Full access to project management and AI features

---

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry installed
- Project cloned and dependencies installed

### First Launch

```bash
# Start interactive chat
poetry run project-manager chat
```

**You'll see**:
```
╭─────────────────────────────────────────────────────╮
│              Project Manager - AI Assistant 🤖      │
│                                                     │
│  Version: 0.1.2                                    │
│  Mode: Interactive Chat                            │
│  Model: Claude Sonnet 4.5                          │
│                                                     │
│  Quick Commands                                    │
│  • /roadmap - View project roadmap                │
│  • /status - Check daemon status                  │
│  • /notifications - View pending notifications    │
│  • /help - Show all commands                      │
│  • Ctrl+D or exit - Exit chat                     │
│                                                     │
│  Ready to help! Ask me anything about the project. │
╰─────────────────────────────────────────────────────╯

❯ _
```

### Basic Interaction

```bash
# Ask a question
❯ What's the current status of the project?

# The AI responds with streaming text (character-by-character)
🧠 Let me check the current project status...

[Streaming response appears smoothly]

# Use commands
❯ /roadmap

# Exit
❯ exit
Goodbye! 👋
```

---

## Visual Elements

### Color Scheme

The UI uses a consistent, professional color scheme:

| Element | Color | Example |
|---------|-------|---------|
| **Info** | Blue (🔵) | `ℹ Information message` |
| **Success** | Green (🟢) | `✓ Task completed successfully!` |
| **Warning** | Yellow (🟡) | `⚠ Warning: Check this` |
| **Error** | Red (🔴) | `✗ Error occurred` |
| **Highlight** | Cyan | Command names, important text |
| **Muted** | Dim White | Details, timestamps |
| **Accent** | Magenta | Titles, headers |

### Status Symbols

| Symbol | Meaning | When You'll See It |
|--------|---------|-------------------|
| ✓ | Success | Task completed |
| ✗ | Error | Operation failed |
| ⚠ | Warning | Caution needed |
| ℹ | Info | General information |
| ⚙ | Working | Operation in progress |
| 🧠 | Thinking | AI processing |
| 💤 | Idle | Waiting for input |
| 🚨 | Critical | Urgent attention needed |
| ‼️ | High Priority | Important notification |

### Progress Indicators

**Spinner** (for unknown duration):
```
⚙ Processing your request...
```

**Progress Bar** (for known steps):
```
Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45% 0:00:23
```

**Status Messages**:
```
ℹ Fetching GitHub data...
✓ Data fetched successfully!
⚙ Processing 150 notifications...
✓ All notifications processed!
```

### Panels and Tables

**Information Panel**:
```
╭─────────────── Project Status ───────────────╮
│                                              │
│  Current Priority: PRIORITY 2                │
│  Status: In Progress                         │
│  Estimated Completion: 2 days                │
│                                              │
╰──────────────────────────────────────────────╯
```

**Data Table**:
```
┏━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID  ┃ Priority  ┃ Status  ┃ Assignee  ┃
┡━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ High      │ Active  │ Daemon    │
│ 2   │ Medium    │ Pending │ -         │
└─────┴───────────┴─────────┴───────────┘
```

---

## Keyboard Shortcuts

### Essential Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+D` | Exit | Quit the application (standard Unix) |
| `Ctrl+C` | Interrupt | Cancel current operation / Graceful exit |
| `Ctrl+L` | Clear | Clear the screen |
| `TAB` | Autocomplete | Complete commands and arguments |
| `↑` / `↓` | History | Navigate through command history |
| `Ctrl+R` | Search | Reverse search through history |

### History Navigation

```bash
# Press ↑ to see previous command
❯ /roadmap

# Press ↑ again
❯ /status  # (previous command)

# Press ↓ to go forward
❯ /roadmap  # (back to most recent)
```

### Autocomplete

```bash
# Type partial command and press TAB
❯ /roa<TAB>

# Automatically completes to:
❯ /roadmap

# Shows available completions if multiple matches:
❯ /st<TAB>
/status      (Check daemon status)
/statistics  (View statistics)
```

### Reverse Search (Ctrl+R)

```bash
# Press Ctrl+R
(reverse-i-search)`': _

# Type search term
(reverse-i-search)`road': /roadmap

# Press Enter to use the command
❯ /roadmap
```

### Clear Screen (Ctrl+L)

```bash
# Screen gets cluttered with output
❯ /roadmap
[... lots of output ...]

# Press Ctrl+L
ℹ Screen cleared. Press Enter to continue.

# Screen is now clean
❯ _
```

---

## Commands

### Slash Commands

All commands start with `/` for easy identification and autocomplete.

#### `/roadmap` - View Project Roadmap

**Usage**:
```bash
# View entire roadmap
❯ /roadmap

# View specific priority
❯ /roadmap 2
❯ /roadmap PRIORITY-3
```

**Output**:
```
════════════════ Project Roadmap ════════════════

🔴 PRIORITY 1: Foundation Setup
   Status: ✅ Complete
   Duration: 1 week

🟡 PRIORITY 2: Roadmap Management CLI
   Status: 🚧 In Progress
   Duration: 2-3 days
   Current Phase: Phase 2 Complete

🔵 PRIORITY 3: Autonomous Development Daemon
   Status: 📝 Planned
   Duration: 3-4 days

[... more priorities ...]
```

#### `/status` - Check Daemon Status

**Usage**:
```bash
❯ /status
```

**Output**:
```
╭───────────── Code Developer Status ─────────────╮
│                                                 │
│  Status: 🚧 Active                              │
│  Current Task: Implementing PRIORITY 2.6       │
│  Progress: 45% complete                        │
│  Estimated Time: 2 hours remaining             │
│                                                 │
│  Last Activity: 5 minutes ago                  │
│  Today's Commits: 3                            │
│  Lines Changed: +245 / -67                     │
│                                                 │
╰─────────────────────────────────────────────────╯
```

#### `/notifications` - View Notifications

**Usage**:
```bash
# View all pending notifications
❯ /notifications

# View specific notification
❯ /notifications 5
```

**Output**:
```
╭─────────────── Pending Notifications ───────────────╮
│                                                     │
│  🔴 [ID: 5] QUESTION - Priority 2.6 Design         │
│     Code developer needs design approval            │
│     Created: 2025-10-20 14:30                      │
│                                                     │
│  🟡 [ID: 6] WARNING - Low Disk Space               │
│     Only 2GB remaining on build server             │
│     Created: 2025-10-20 13:15                      │
│                                                     │
│  🔵 [ID: 7] INFO - Daily Report Available          │
│     View today's progress summary                  │
│     Created: 2025-10-20 09:00                      │
│                                                     │
╰─────────────────────────────────────────────────────╯

ℹ Use 'respond <id> <message>' to respond to questions
```

#### `/respond` - Respond to Notifications

**Usage**:
```bash
# Approve a question
❯ /respond 5 approve

# Provide custom response
❯ /respond 5 "use option 2 instead"

# Reject with reason
❯ /respond 5 "no, needs more testing first"
```

**Output**:
```
✓ Response sent successfully!
  Notification ID: 5
  Your response: "approve"
  Code developer will continue with approved design.
```

#### `/verify-dod` - Verify Definition of Done

**Usage**:
```bash
# Verify current priority
❯ /verify-dod

# Verify specific priority
❯ /verify-dod 2
❯ /verify-dod PRIORITY-3
```

**Output**:
```
╭─────── Definition of Done Verification ──────╮
│                                              │
│  Priority: PRIORITY 2                        │
│  Status: 🚧 In Progress                      │
│                                              │
│  Criteria:                                   │
│  ✓ Code implemented and tested              │
│  ✓ Documentation updated                    │
│  ✗ Code review completed                    │
│  ✗ Integration tests passing                │
│  ◯ Deployed to staging                      │
│                                              │
│  Progress: 2/5 criteria met (40%)           │
│                                              │
╰──────────────────────────────────────────────╯

⚠ Warning: Not ready for completion
  Missing: Code review, Integration tests
```

#### `/github-status` - Check GitHub Status

**Usage**:
```bash
❯ /github-status
```

**Output**:
```
╭──────────── GitHub Integration Status ─────────────╮
│                                                    │
│  📊 Open Pull Requests: 2                          │
│     • #47: US-036 Console UI Polish (In Review)   │
│     • #45: Fix notification bug (Approved)        │
│                                                    │
│  🐛 Open Issues: 5                                 │
│     • #52: Performance degradation (High)         │
│     • #51: Dark theme bugs (Medium)               │
│     • ... 3 more                                  │
│                                                    │
│  ✓ CI/CD: All checks passing                      │
│  ✓ Branch Status: Up to date with main           │
│                                                    │
╰────────────────────────────────────────────────────╯
```

#### `/help` - Show All Commands

**Usage**:
```bash
❯ /help
```

**Output**:
```
╭──────────── Available Commands ────────────╮
│                                            │
│  /roadmap [id]     - View project roadmap │
│  /status           - Check daemon status  │
│  /notifications    - View notifications   │
│  /respond <id>     - Respond to question  │
│  /verify-dod [id]  - Check DoD criteria   │
│  /github-status    - GitHub integration   │
│  /history          - View command history │
│  /clear            - Clear screen         │
│  /help             - Show this help       │
│  /exit             - Exit application     │
│                                            │
│  Keyboard Shortcuts:                      │
│  • TAB         - Autocomplete             │
│  • ↑/↓         - Navigate history         │
│  • Ctrl+R      - Search history           │
│  • Ctrl+L      - Clear screen             │
│  • Ctrl+D      - Exit                     │
│                                            │
╰────────────────────────────────────────────╯
```

#### `/exit` - Exit Application

**Usage**:
```bash
❯ /exit
# or
❯ exit
# or press Ctrl+D
```

**Output**:
```
Goodbye! 👋

Summary:
  • Commands executed: 12
  • Time active: 15 minutes
  • Last command: /status

See you next time!
```

### Natural Language Queries

You can also ask questions in natural language:

```bash
❯ What's the status of PRIORITY 2?

🧠 Let me check the status of PRIORITY 2...

[AI streams response with current status, progress, blockers]
```

```bash
❯ Show me recent commits

🧠 Fetching recent commit history...

[AI displays formatted commit list with details]
```

```bash
❯ What should I work on next?

🧠 Analyzing roadmap and priorities...

[AI provides recommendation based on current state]
```

---

## Advanced Features

### Streaming Responses

The AI provides real-time, streaming responses that appear character-by-character, just like claude-cli:

```bash
❯ Explain the architecture of this project

🧠 Analyzing project architecture...

[Text appears smoothly, word by word]
```

**Benefits**:
- **Immediate feedback**: See response start immediately
- **Natural feel**: Like talking to a person
- **Cancellable**: Press Ctrl+C to stop mid-stream

### Multi-line Input

For long prompts or complex queries:

```bash
❯ Explain how the autonomous daemon
... works and how it interacts with
... the notification system

[Multi-line input supported]
```

**How to Enable**:
- Just keep typing - newlines are handled automatically
- Or end line with `\` to explicitly continue

### Command History Persistence

Your command history is saved between sessions:

```bash
# Session 1
❯ /roadmap
❯ /status
❯ exit

# Session 2 (later)
❯ <Press ↑>
/status  # Previous command from earlier session!
```

**History File**: `.project_manager_history` (in project root)

### Smart Autocomplete

Autocomplete learns from your usage:

```bash
# First time
❯ /not<TAB>
/notifications

# After using it frequently, it appears first in suggestions
❯ /n<TAB>
/notifications  # (most used)
/notes          # (less used)
```

### Context-Aware Suggestions

The UI provides helpful suggestions based on context:

```bash
❯ /respond 5 approve

✗ Error: Notification 5 not found

💡 Suggestion: View pending notifications with '/notifications'
```

### Error Recovery

If something goes wrong, the UI guides you:

```bash
❯ /roadmap 99

✗ Error: Priority 99 does not exist

Details: Valid priorities are: 1-20, PRIORITY-1 to PRIORITY-20

💡 Suggestions:
  • View all priorities: /roadmap
  • Check a valid priority: /roadmap 2
  • See available priorities: /roadmap --list
```

---

## Troubleshooting

### Common Issues

#### Issue: Command Not Found

**Symptom**:
```bash
❯ /mycommand
✗ Error: Unknown command '/mycommand'
```

**Solution**:
- Check spelling
- Use `/help` to see available commands
- Try autocomplete with TAB

#### Issue: Slow Streaming Response

**Symptom**: Response appears in large chunks instead of smoothly

**Solution**:
1. Check network connection (for AI requests)
2. Check system load: `top` or `htop`
3. Try again - may be temporary API slowness

#### Issue: Terminal Formatting Broken

**Symptom**: Colors missing, boxes display incorrectly

**Solution**:
```bash
# Check terminal supports colors
echo $TERM  # Should be 'xterm-256color' or similar

# If not, set it:
export TERM=xterm-256color

# Or use a modern terminal:
# - iTerm2 (macOS)
# - Windows Terminal (Windows)
# - Alacritty (cross-platform)
```

#### Issue: History Not Working

**Symptom**: Arrow keys don't show previous commands

**Solution**:
1. Check history file exists: `ls -la .project_manager_history`
2. Check file permissions: `chmod 644 .project_manager_history`
3. If corrupted, delete and restart: `rm .project_manager_history`

#### Issue: Autocomplete Not Working

**Symptom**: TAB key doesn't complete commands

**Solution**:
1. Ensure `prompt_toolkit` is installed: `poetry show prompt-toolkit`
2. Check terminal compatibility
3. Try reinstalling dependencies: `poetry install`

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Run with debug output
poetry run project-manager chat --debug

# Or set environment variable
export PROJECT_MANAGER_DEBUG=1
poetry run project-manager chat
```

**Output**:
```
[DEBUG] Initializing console UI...
[DEBUG] Loading command history from .project_manager_history
[DEBUG] History file: 25 entries loaded
[DEBUG] Creating prompt session...
[DEBUG] Autocomplete initialized with 9 commands
[DEBUG] Ready for user input
```

### Getting Help

If you encounter issues:

1. **Check Documentation**: Read this guide thoroughly
2. **View Logs**: Check debug output
3. **Search Issues**: Look for similar problems in GitHub Issues
4. **Ask for Help**: Create a new GitHub Issue with:
   - Exact command you ran
   - Error message (if any)
   - Terminal type and version
   - OS version
   - Debug output

---

## Tips & Tricks

### Productivity Hacks

#### 1. Use Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Quick access to project manager
alias pm='poetry run project-manager'
alias pmc='poetry run project-manager chat'
alias pmr='poetry run project-manager /roadmap'
alias pms='poetry run project-manager status'
alias pmn='poetry run project-manager notifications'

# Now you can use:
$ pmc              # Start chat
$ pmr              # View roadmap
$ pms              # Check status
```

#### 2. Use Command Shortcuts

Instead of typing full commands, use prefixes:

```bash
# These all work
❯ /roadmap
❯ /road
❯ /ro

# Autocomplete fills in the rest
```

#### 3. Combine Commands

Ask compound questions:

```bash
❯ Show me the status of PRIORITY 2 and any related notifications

[AI provides comprehensive answer combining multiple data sources]
```

#### 4. Use History Search Efficiently

```bash
# Press Ctrl+R and type keyword
(reverse-i-search)`github': /github-status

# Much faster than scrolling with ↑
```

#### 5. Learn Common Patterns

```bash
# Daily workflow pattern
❯ /status            # Check what daemon is doing
❯ /notifications     # See if any questions
❯ /respond 5 approve # Respond if needed
❯ /roadmap           # Review progress
```

### Terminal Setup

#### Optimize Your Terminal

**Font**: Use a font with good emoji and symbol support
- Recommended: JetBrains Mono, Fira Code, SF Mono

**Color Scheme**: Use a scheme with good contrast
- Recommended: Dracula, Solarized Dark, Nord

**Terminal Emulator**: Use a modern, feature-rich terminal
- macOS: iTerm2
- Windows: Windows Terminal
- Linux: Alacritty, Kitty
- Cross-platform: Warp

#### Terminal Configuration

**iTerm2 Settings** (macOS):
1. Preferences → Profiles → Terminal
2. Set "Report Terminal Type" to `xterm-256color`
3. Enable "Use bright colors for bold text"
4. Set scrollback lines to 10,000+ for long sessions

**VS Code Terminal**:
1. Settings → Terminal › Integrated: Font Size → 14
2. Settings → Terminal › Integrated: Font Family → 'JetBrains Mono'
3. Settings → Terminal › Integrated: Line Height → 1.2

### Advanced Usage Patterns

#### Morning Checklist

```bash
# Start your day
❯ /status                    # What's the daemon working on?
❯ /notifications             # Any questions for me?
❯ /github-status             # Any PRs or issues?
❯ What should I focus on today?  # Ask AI for recommendations
```

#### Before Leaving Work

```bash
# End of day routine
❯ /status                    # Check progress
❯ Any blockers for the daemon?  # Proactive check
❯ /respond <id> <answer>     # Clear notifications
❯ /verify-dod <priority>     # Check if anything ready to ship
```

#### Debugging Workflow

```bash
# When something's wrong
❯ /status                    # Is daemon running?
❯ /notifications             # Any errors reported?
❯ Show me recent errors in the logs  # Ask AI to analyze
❯ /github-status             # Check if CI failing
```

### Customization

#### Environment Variables

```bash
# Customize behavior with environment variables
export PROJECT_MANAGER_THEME=light      # Use light theme
export PROJECT_MANAGER_TIMESTAMPS=true  # Show timestamps
export PROJECT_MANAGER_HISTORY_SIZE=500 # Increase history
export PROJECT_MANAGER_DEBUG=true       # Enable debug mode

poetry run project-manager chat
```

#### Configuration File

Create `~/.project_manager_config.yaml`:

```yaml
# UI Preferences
theme: dark
show_timestamps: false
animation_speed: normal  # slow, normal, fast

# Behavior
auto_update_roadmap: true
notification_check_interval: 300  # seconds
history_size: 1000

# AI Settings
stream_responses: true
model: claude-sonnet-4-5
temperature: 0.7
```

---

## Quick Reference Card

### Essential Commands

```
/roadmap [id]    - View roadmap
/status          - Daemon status
/notifications   - View notifications
/respond <id>    - Respond to notification
/help            - Show help
/exit            - Exit
```

### Essential Shortcuts

```
TAB        - Autocomplete
↑ / ↓      - Navigate history
Ctrl+R     - Search history
Ctrl+L     - Clear screen
Ctrl+D     - Exit
Ctrl+C     - Cancel/Exit
```

### Status Symbols

```
✓ Success    ✗ Error      ⚠ Warning
ℹ Info       ⚙ Working    🧠 Thinking
💤 Idle      🚨 Critical  ‼️  High Priority
```

---

## Next Steps

Now that you know how to use the console UI:

1. **Practice**: Use it daily to build muscle memory
2. **Explore**: Try different commands and see what's possible
3. **Customize**: Set up aliases and configuration for your workflow
4. **Provide Feedback**: Report bugs or suggest improvements

**Additional Resources**:
- Implementation Guide: `docs/US-036-CONSOLE_UI_POLISH_GUIDE.md`
- Testing Guide: `docs/US-036-CONSOLE_UI_TESTING_GUIDE.md`
- Main Documentation: `docs/roadmap/ROADMAP.md`

---

**Questions or Feedback?**

Create a GitHub Issue: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues

**Last Updated**: 2025-10-20
**Version**: US-036 Enhanced UI
