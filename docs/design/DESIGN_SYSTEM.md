# CLI Design System - MonolithicCoffeeMakerAgent
**Date**: October 17, 2025
**Version**: 1.0
**Status**: Design Reference

---

## 1. Design System Overview

### Mission
Create a **consistent, professional, accessible** terminal UI that:
- Reduces cognitive load
- Provides clear feedback
- Scales from mobile terminals to 4K displays
- Works for all user personas

### Principles
1. **Clarity First** - Information should be obvious
2. **Consistency** - Similar patterns across all commands
3. **Feedback** - Every action has clear response
4. **Accessibility** - Works for all users
5. **Efficiency** - Expert users can accomplish tasks quickly

---

## 2. Color Palette

### Primary Colors
```
Info      → Blue (#3B82F6)      - Questions, general information, links
Success   → Green (#10B981)     - Completed actions, approvals, checkmarks
Warning   → Yellow (#F59E0B)    - Cautions, pending actions, alerts
Error     → Red (#EF4444)       - Failures, blockers, critical issues
Muted     → Gray (#9CA3AF)      - Secondary info, timestamps, dividers
```

### Implementation in Rich
```python
COLORS = {
    "info": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "muted": "dim white",
    "highlight": "cyan",
    "accent": "magenta",
}
```

### Usage Guidelines

| Context | Color | Example |
|---------|-------|---------|
| Status running | Green | `🟢 Running` |
| Status waiting | Yellow | `🟡 Pending` |
| Status blocked | Red | `🔴 Blocked` |
| Status idle | Gray | `⚪ Idle` |
| Information | Blue | `ℹ️ Tip:` |
| Success | Green | `✓ Complete` |
| Warning | Yellow | `⚠️ Warning:` |
| Error | Red | `✗ Error:` |
| Metadata | Gray | `(created 2h ago)` |
| Highlight | Cyan | `important value` |

---

## 3. Typography & Hierarchy

### Font Styles (Terminal)
```
BOLD        - Section titles, key information
Normal      - Body text, main content
Dim         - Secondary info, hints, timestamps
Italic      - Emphasis, alternative terms
```

### Hierarchy Levels

#### H1 - Screen Title
```
════════════════════════════════════════════════════════════════════
Project Manager · Developer Status Dashboard
════════════════════════════════════════════════════════════════════
```
- 70-80 characters wide
- BOLD
- Centered or left-aligned
- Major separator above and below

#### H2 - Section Header
```
DAEMON STATUS
─────────────────────────────────────────────────────────────────
```
- ALL CAPS
- BOLD + Color (usually highlight/cyan)
- 40-60 characters wide
- Separator below (─ characters)

#### H3 - Subsection
```
Pending Questions
```
- Title Case
- BOLD + Color
- No separator
- Indented slightly

#### Body Text
```
State: 🟢 Running      Progress: 80%      ETA: 2h 15m
```
- Normal weight
- 70-80 character line limit
- Left-aligned within panels

#### Metadata
```
(last updated 5m ago)  (uptime 2h 45m)  (pid 12345)
```
- Dim/Gray color
- Parentheses for distinction
- Right-aligned when possible

---

## 4. Icons & Symbols

### Status Emojis (State Indicator)
```
🟢 Running/Working      🟡 Pending/Waiting      🔴 Blocked/Failed
🔵 Thinking             🟣 Reviewing            ⚫ Stopped/Offline
⚪ Idle/Unknown         🟠 Warning
```

### Action Symbols
```
✓  Success/Done         ✗  Failed/Error         ⧖  In Progress
○  Pending              ✔  Complete             ✘  Rejected
→  Next/Continue        ⚡ Quick action         💾 Save
↻  Retry/Refresh        ↕  Up/Down             ⏸  Paused
```

### Information Icons
```
ℹ️  Information          ❓ Question             💡 Tip/Suggestion
⚠️  Warning             🚨 Critical/Alert       🔧 Configuration
📋 Checklist            📊 Metrics              📈 Growth/Increase
🔗 Link/Related         📝 Note/Document       🎯 Target
```

### Contextual Icons
```
📍 Current location     ⏱️  Timer/Duration      🕐 Time/Schedule
🔑 Key/Important       📌 Pin/Bookmark        🏷️  Tag/Label
👤 User/Person         🔐 Security            🌐 Global/Network
```

---

## 5. Components

### 5.1 Panels & Borders

#### Full-Width Panel
```
╔════════════════════════════════════════════════════════════════════╗
║ TITLE                                                              ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Content here                                                      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

#### Info Panel (Compact)
```
┌─ Key Information ──────────────────────────────────────────────────┐
│ State: 🟢 Running                                                  │
│ Task: PRIORITY 3.2 - Daemon Status Reporting                      │
│ Progress: ████████░░ 80%                                          │
└────────────────────────────────────────────────────────────────────┘
```

#### Alert Panel (High Priority)
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CRITICAL ALERT                                                   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ ⚠️  Daemon has been working for 4+ hours without completing task! ┃
┃                                                                  ┃
┃ Action: Check status with 'project-manager developer-status'     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 5.2 Tables

#### Key-Value Table
```
Key                    Value
─────────────────────  ──────────────────────────
State                  🟢 Running
Current Task           PRIORITY 3.2 - Reporting
Progress               ████████░░ 80%
ETA                    2h 15m
Uptime                 2h 45m
```

#### Status Table
```
ID  Status    Title                              Progress  ETA
──  ────────  ───────────────────────────────  ─────────  ──────
1   ✓         PRIORITY 3.1 - User Auth         100%       Done
2   ⧖         PRIORITY 3.2 - Dashboard         80%        2h 15m
3   ○         PRIORITY 3.3 - API                0%        Pending
```

### 5.3 Lists

#### Bullet List
```
Items to review:
  • First item in the list
  • Second item in the list
  • Third item in the list
```

#### Numbered List
```
Steps to complete:
  1. First step description
  2. Second step description
  3. Third step description
```

#### Hierarchical List
```
Pending Items:
  Questions (2)
    • Approve pandas dependency?  (Waiting 12m)
    • Review spec PRIORITY-3?     (Waiting 45m)

  Blockers (1)
    • Git merge conflict in main  (Blocking 1h)
```

### 5.4 Progress Indicators

#### Simple Progress Bar
```
Progress: ████████░░░░░░░░░░░░░░░░░░░░░░ 25%
```

#### Detailed Progress Bar
```
[████████░░░░░░░░░░░░░░░░░░░░░░░░] 25% (15 seconds)
```

#### Step Progress
```
✓ Step 1: Configure environment
✓ Step 2: Install dependencies
⧖ Step 3: Building project...
○ Step 4: Running tests
○ Step 5: Deploying
```

#### Multi-Task Progress
```
[1/5] ✓ PRIORITY 1         completed in 2m 30s
[2/5] ✓ PRIORITY 2         completed in 1m 45s
[3/5] ⧖ PRIORITY 3         in progress (45%)
[4/5] ○ PRIORITY 4         waiting...
[5/5] ○ PRIORITY 5         waiting...
```

---

## 6. Layouts

### 6.1 Single-Column Layout
```
┌─ Header ──────────────────────────────────────────────┐
│ Title and basic info                                  │
└───────────────────────────────────────────────────────┘

┌─ Primary Info ────────────────────────────────────────┐
│ Main content and status                               │
└───────────────────────────────────────────────────────┘

┌─ Secondary Info ──────────────────────────────────────┐
│ Related information and context                       │
└───────────────────────────────────────────────────────┘

Footer: Help hints and related commands
```

### 6.2 Two-Column Layout (Wide Terminal)
```
┌─ Left Column ──────────────┬─ Right Column ────────────┐
│ State Information           │ Quick Metrics             │
│                             │                           │
│ Current Task                │ Pending Items             │
│ Progress Bar                │                           │
└─────────────────────────────┴───────────────────────────┘
```

### 6.3 Dashboard Layout (3+ Commands)
```
╔══════════════════════════════════════════════════════════════════╗
║  DAEMON STATUS                                   ⏰ 14:32:15     ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🟢 Working  |  PRIORITY 3.2 (80%, 2h 15m)  |  2 questions     ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  TODAY'S METRICS                                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Tasks: 3 complete | Commits: 8 | Tests: 24 pass | Specs: 2    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 7. Spacing & Whitespace

### Vertical Spacing
```
MAJOR SECTION
═════════════════════════════════════════════════════════════════

  [blank line]

  Content here

  [blank line]

SUB-SECTION
─────────────────────────────────────────────────────────────────

  Nested content
```

### Indentation
```
Level 0: No indentation
  Level 1: 2 spaces
    Level 2: 4 spaces
      Level 3: 6 spaces
```

### Line Length
- **Maximum**: 80 characters (terminal standard)
- **Comfortable**: 60-70 characters
- **Narrow mode**: 40-50 characters (mobile)

---

## 8. Interaction Patterns

### Confirmation Dialog
```
╔════════════════════════════════════════════════════════════════════╗
║ Confirm Action                                                   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║ This will respond to 3 pending notifications. Continue?            ║
║                                                                    ║
║   [Y]es   [N]o   [C]ancel                                          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

### Input Prompt
```
Please select an action:
  1. Approve installation
  2. Reject installation
  3. Ask for alternative
  4. Cancel

Your choice (1-4): █
```

### Progress Spinner
```
Generating specification...
  ⠋ Reading template...
```

---

## 9. Accessibility

### Color Blindness Considerations
- Always provide text/emoji alternatives to colors
- Use red + gray or green + gray (not red/green alone)
- Test with Deuteranopia and Protanopia simulators

### Screen Reader Considerations
- Use semantic panel titles
- Describe emojis with text
- Structure information hierarchically

### Motor Accessibility
- Keep key interactions simple (yes/no, not multi-step)
- Provide keyboard shortcuts
- Make clickable areas adequate (not tiny)

### Language Accessibility
- Keep text simple and clear
- Use active voice
- Avoid jargon where possible

---

## 10. Terminal Compatibility

### Tested On
```
✓ macOS Terminal.app (Monterey+)
✓ iTerm2 (3.4+)
✓ VS Code Integrated Terminal
✓ GitHub Codespaces
✓ Linux terminals (Ubuntu, Debian, CentOS)
✓ Windows Terminal (with WSL)
```

### Features by Terminal
```
Terminal        Unicode  256 Colors  True Color  Emoji
─────────────────────────────────────────────────────
macOS Terminal  ✓        ✓           ✓           ✓
iTerm2          ✓        ✓           ✓           ✓
VS Code         ✓        ✓           ✓           ✓
Linux GNOME     ✓        ✓           ✓           ✓
Windows PowerShell (older)  Limited  Limited      ✗
```

### Fallbacks
- If terminal width < 60: Use compact layouts
- If no color support: Use text-only mode with clear separators
- If no emoji support: Use ASCII alternatives (✓ ✗ -> [OK] [XX])

---

## 11. Typography Scale

### Font Sizes (by character count and position)

| Level | Style | Width | Example |
|-------|-------|-------|---------|
| H1 | BOLD + 70-80 chars | Full | `Daemon Status Dashboard` |
| H2 | BOLD + CAPS + 40-60 chars | ~75% | `PENDING QUESTIONS` |
| H3 | BOLD + Title Case | ~60% | `Current Task` |
| Body | Normal | 70-80 | Standard content |
| Meta | Dim | Variable | `(5m ago)` |
| Code | Monospace | Variable | Commands, paths |

---

## 12. Implementation Checklist

### Phase 1: Foundation
- [x] Define color palette
- [x] Define icons/symbols
- [x] Define typography hierarchy
- [x] Create component templates
- [ ] Implement in console_ui.py
- [ ] Create design token file

### Phase 2: Components
- [ ] Panel components
- [ ] Table components
- [ ] List components
- [ ] Progress components
- [ ] Confirmation dialogs

### Phase 3: Documentation
- [ ] Component gallery
- [ ] Usage examples
- [ ] Migration guide
- [ ] Best practices

### Phase 4: Testing
- [ ] Terminal compatibility testing
- [ ] Accessibility testing
- [ ] User testing
- [ ] Performance testing

---

## 13. Migration Guide

### For Existing Commands

#### Before (Inconsistent)
```python
# Command 1: Uses print()
print("Status: Running")
print("Task: PRIORITY 3")

# Command 2: Uses console_ui
info("Status: Running")
status("Current task: PRIORITY 3", state="working")

# Command 3: Uses Rich panels
console.print(Panel("Status: Running"))
```

#### After (Consistent)
```python
# All commands use unified system
from coffee_maker.cli.console_ui import status_item, progress_bar

status_item("State", "🟢 Running", label_style="bold cyan")
status_item("Task", "PRIORITY 3", label_style="bold cyan")
progress_bar("Progress", 80)
```

---

## 14. Brand Voice

### Terminal Output Style
- **Professional but approachable** - Not robotic or overly technical
- **Helpful** - Errors include suggestions, not just failures
- **Confident** - Clear direction, not wishy-washy
- **Concise** - Get to the point quickly
- **Honest** - Admit blockers and limitations

### Example Tones

#### Good
```
✓ Specification generated! Ready for review.
💡 Next: Use 'project-manager respond 1 approve' to proceed
```

#### Not Good
```
An action has potentially been completed pending verification status
```

---

## 15. Dark Mode & Light Mode

### Current Status
- Focus on **Dark Mode** (most terminal users)
- Provide fallback for light terminals

### Dark Mode (Default)
```
Background: Black / Very Dark Gray (#0F0F0F)
Text: White / Off-White (#E5E5E5)
Colors: Standard ANSI colors (bright)
```

### Light Mode (Fallback)
```
Background: White / Very Light Gray (#F8F8F8)
Text: Black / Dark Gray (#1F1F1F)
Colors: Darker ANSI colors (low contrast)
```

### Detection
```python
def detect_terminal_background() -> str:
    """Detect if terminal uses light or dark background."""
    # Default to dark mode
    return os.environ.get("COLORFGBG", "dark")
```

---

**End of Design System**
