# CLI UX Improvements - Design Specifications
**Date**: October 17, 2025
**Component**: Terminal CLI Interface
**Status**: Design Phase
**Priority**: High

---

## 1. Enhanced Error Message System

### 1.1 Design Principle
**Every error should:**
1. Clearly state what went wrong
2. Suggest concrete fixes
3. Show related commands
4. Provide debug information

### 1.2 Error Message Format

#### Visual Structure
```
╔════════════════════════════════════════════════════════════════════════════╗
║ ERROR CATEGORY                                                             ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║ ✗ Error: Concise description of what went wrong                          ║
║                                                                            ║
║ 💡 Suggestions:                                                            ║
║   • Specific action 1 to resolve this                                     ║
║   • Specific action 2 to resolve this                                     ║
║   • Check the following: detail about what to verify                      ║
║                                                                            ║
║ 🔗 Related Commands:                                                       ║
║   • project-manager related-command - Description of how it helps         ║
║   • project-manager another-command - Another related option              ║
║                                                                            ║
║ 📝 Details: [technical error details]                                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

#### Color Coding
- **Title**: Red (bold) for errors, Yellow for warnings
- **Symbol**: Matching color (✗ for error, ⚠ for warning)
- **Message**: White
- **Suggestions**: Blue (💡 symbol)
- **Commands**: Cyan (🔗 symbol)
- **Details**: Dim white for technical info

### 1.3 Error Types & Responses

#### Type 1: File Not Found
```python
# Error: ROADMAP.md not found
error(
    "ROADMAP.md not found",
    suggestions=[
        "Ensure you're on the 'roadmap' branch: git checkout roadmap",
        "Verify the file exists: ls -la ROADMAP.md",
        "Check your working directory: pwd"
    ],
    related_commands=[
        ("git status", "Check current git status"),
        ("git branch", "List available branches")
    ]
)
```

#### Type 2: Configuration Error
```python
# Error: Claude not available
error(
    "No Claude access available",
    suggestions=[
        "Option 1: Install Claude CLI from https://claude.ai/",
        "Option 2: Set ANTHROPIC_API_KEY environment variable",
        "Option 3: Run in a different environment with Claude CLI installed"
    ],
    related_commands=[
        ("claude --version", "Check if Claude CLI is installed"),
        ("echo $ANTHROPIC_API_KEY", "Check if API key is set")
    ]
)
```

#### Type 3: Daemon Issues
```python
# Error: Daemon not running
error(
    "Daemon is not running",
    suggestions=[
        "Start the daemon: poetry run code-developer",
        "Check daemon status: project-manager status",
        "View recent daemon errors: project-manager dev-report"
    ],
    related_commands=[
        ("project-manager dev-report", "See what daemon was doing"),
        ("project-manager developer-status", "Check detailed status")
    ]
)
```

### 1.4 Implementation

New functions in `console_ui.py`:

```python
def error_block(
    title: str,
    message: str,
    suggestions: Optional[List[str]] = None,
    related_commands: Optional[List[Tuple[str, str]]] = None,
    details: Optional[str] = None
) -> None:
    """Display comprehensive error message with suggestions and related commands.

    Args:
        title: Error category (e.g., "Configuration Error")
        message: Main error message
        suggestions: List of actionable suggestions
        related_commands: List of (command, description) tuples
        details: Optional technical details
    """
    content = []

    # Error message
    content.append(f"[bold red]✗ Error:[/bold red] [white]{message}[/white]")
    content.append("")

    # Suggestions
    if suggestions:
        content.append(f"[bold blue]💡 Suggestions:[/bold blue]")
        for suggestion in suggestions:
            content.append(f"  • {suggestion}")
        content.append("")

    # Related commands
    if related_commands:
        content.append(f"[bold cyan]🔗 Related Commands:[/bold cyan]")
        for cmd, desc in related_commands:
            content.append(f"  • [cyan]{cmd}[/cyan] - {desc}")
        content.append("")

    # Details
    if details:
        content.append(f"[dim]📝 Details: {details}[/dim]")

    # Create panel
    panel = Panel(
        "\n".join(content),
        title=f"[bold red]{title}[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(panel)


def warning_block(
    title: str,
    message: str,
    suggestions: Optional[List[str]] = None
) -> None:
    """Display warning message with suggestions."""
    content = []
    content.append(f"[bold yellow]⚠ Warning:[/bold yellow] [white]{message}[/white]")

    if suggestions:
        content.append("")
        content.append(f"[bold blue]💡 Suggestions:[/bold blue]")
        for suggestion in suggestions:
            content.append(f"  • {suggestion}")

    panel = Panel(
        "\n".join(content),
        title=f"[bold yellow]{title}[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    )
    console.print(panel)
```

---

## 2. Progress Indicators for Long Operations

### 2.1 Design Principle
**Show progress through:**
1. Visual progress bar (0-100%)
2. Current step being executed
3. Time elapsed
4. Estimated time remaining
5. Success/failure at each step

### 2.2 Progress Bar Styles

#### Style 1: Simple Linear Progress
```
Generating specification...
  Reading template...                    [████░░░░░░░░░░░░░░░░░░░] 20%
```

#### Style 2: Multi-Step Progress (Recommended)
```
Generating specification...

  ✓ Reading template                          (0.3s)
  ✓ Analyzing requirements                    (1.2s)
  ⧖ Generating implementation plan            (in progress...)
  ○ Estimating effort                         (pending)
  ○ Creating final document                   (pending)

Progress: 60%  |  Elapsed: 1.5s  |  ETA: 1.0s remaining
```

#### Style 3: Task Queue (For multiple operations)
```
Processing 5 items...

[1/5] ✓ PRIORITY-1 - User authentication        (completed in 2m 30s)
[2/5] ✓ PRIORITY-2 - Dashboard                  (completed in 1m 45s)
[3/5] ⧖ PRIORITY-3 - API integration            (in progress - 45% done)
[4/5] ○ PRIORITY-4 - Testing                    (waiting)
[5/5] ○ PRIORITY-5 - Documentation              (waiting)

Overall: 3/5 complete (60%)  |  Current task ETA: 45s
```

### 2.3 Implementation Pattern

```python
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

def generate_spec_with_progress(spec_request):
    """Generate spec with multi-step progress display."""

    steps = [
        ("Reading template", read_template),
        ("Analyzing requirements", analyze_requirements),
        ("Generating plan", generate_plan),
        ("Estimating effort", estimate_effort),
        ("Creating document", create_document),
    ]

    completed_steps = []

    for step_name, step_func in steps:
        console.print(f"\n⧖ {step_name}...", style="yellow")

        start_time = time.time()
        try:
            result = step_func(spec_request)
            elapsed = time.time() - start_time
            completed_steps.append((step_name, "success", elapsed))
            console.print(f"✓ {step_name} completed in {elapsed:.1f}s", style="green")
        except Exception as e:
            elapsed = time.time() - start_time
            completed_steps.append((step_name, "failed", elapsed))
            console.print(f"✗ {step_name} failed after {elapsed:.1f}s", style="red")
            console.print(f"  Error: {e}")
            raise

    # Summary
    console.print("\n" + "=" * 70)
    total_time = sum(t[2] for t in completed_steps)
    console.print(f"✓ Specification generated in {total_time:.1f}s")
    console.print("=" * 70)
```

---

## 3. Status Display Hierarchy

### 3.1 Three-Tier Display System

#### Tier 1: Quick Status (15 characters)
```
🟢 Working | 80% | 2h
```
**Use case**: Terminal width < 80 chars, daemon watch mode

#### Tier 2: Status Summary (40-50 lines)
```
╔══════════════════════════════════════════════════════════════════════════╗
║  DAEMON STATUS                                              ⏰ 14:32    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  State: 🟢 Working                    Uptime: 2h 45m                    ║
║  Current: PRIORITY 3.2 - Daemon Status Reporting                         ║
║  Progress: ████████░░ 80%             ETA: 2h 15m                       ║
║                                                                          ║
║  PENDING QUESTIONS (2)                 BLOCKERS (0)                      ║
║  • Approve pandas dependency?          (none)                            ║
║  • Review spec PRIORITY-3?                                              ║
║                                                                          ║
║  METRICS (TODAY)                                                         ║
║  Tasks: 3 complete | Commits: 8 | Tests: 24 pass / 0 fail              ║
╚══════════════════════════════════════════════════════════════════════════╝
```
**Use case**: `project-manager dashboard` (new command)

#### Tier 3: Full Status (80+ lines)
```
[Complete developer_status_display format with all fields]
```
**Use case**: `project-manager developer-status` (existing)

### 3.2 Visual Hierarchy Rules

1. **State** (top-left, emoji + text)
   - Most important: Is the daemon working?
   - Uses colored emoji (🟢🟡🔴⚫)

2. **Current Task** (second row)
   - What is it doing right now?
   - Shows priority/task name

3. **Progress** (third row)
   - How much is done?
   - Visual bar + percentage + ETA

4. **Urgent Info** (middle section)
   - Questions pending
   - Blockers
   - Errors

5. **Context** (lower section)
   - Metrics
   - History
   - Advanced details

---

## 4. New Commands

### 4.1 Quick Status

**Command**: `project-manager status-quick`

**Output**:
```
🟢 Working | PRIORITY 3.2 (80%, 2h 15m ETA) | 2 pending questions
```

**Implementation** (10 lines):
```python
def cmd_status_quick(args):
    """Show one-line daemon status."""
    status = read_developer_status()

    state_emoji = _get_state_emoji(status['state'])
    task = status.get('current_task', {})
    task_name = task.get('name', 'Idle')
    progress = task.get('progress', 0)
    eta = task.get('eta_seconds', 0)
    eta_str = format_duration(eta)
    questions = len(status.get('questions', []))

    one_liner = f"{state_emoji} {status['state'].title()} | {task_name} ({progress}%, {eta_str}) | {questions} pending"
    console.print(one_liner)
```

### 4.2 Dashboard

**Command**: `project-manager dashboard`

**Shows executive summary with:**
- Daemon state + uptime
- Current task + progress
- Pending questions (max 3)
- Blockers (if any)
- Daily metrics summary

**Implementation**: Combine data from multiple sources

### 4.3 Help/Discovery

**Command**: `project-manager help`

**Shows**:
```
╔════════════════════════════════════════════════════════════════════════════╗
║  COFFEE MAKER AGENT · Help                                                ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  MOST COMMON COMMANDS                                                      ║
║  ─────────────────────────────────────────────────────────────────────────  ║
║                                                                            ║
║  📋 View ROADMAP                                                           ║
║     project-manager view                 Show current priorities            ║
║     project-manager view 1               Show specific priority             ║
║                                                                            ║
║  🟢 Check Daemon Status                                                    ║
║     project-manager status-quick         One-line status                   ║
║     project-manager dashboard            Executive summary                 ║
║     project-manager developer-status     Full detailed status              ║
║                                                                            ║
║  ❓ Manage Notifications                                                    ║
║     project-manager notifications        List pending items                ║
║     project-manager respond 1 yes        Respond to notification           ║
║                                                                            ║
║  💬 Chat Interface                                                         ║
║     project-manager chat                 Start AI chat session             ║
║     project-manager guide setup          Show setup guide                  ║
║                                                                            ║
║  📊 Reports & Metrics                                                      ║
║     project-manager summary              Recent deliveries                 ║
║     project-manager metrics              Velocity and accuracy             ║
║     project-manager calendar             Upcoming deliverables             ║
║                                                                            ║
║  For complete list: project-manager --help                                ║
║  For specific command: project-manager <command> --help                   ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## 5. Notification Management Enhancements

### 5.1 Enhanced Display

**Current State**:
```
[NOTIFICATION PANEL]
```

**Improved State**:
```
╔════════════════════════════════════════════════════════════════════════════╗
║ QUESTION [ID: 5]                                              Waiting 12m ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║ ❓ Approve Installation: Approve pandas dependency?                        ║
║                                                                            ║
║ Context:                                                                   ║
║   • Required for data processing in PRIORITY 3.2                          ║
║   • Version: 2.0.0 (latest stable)                                        ║
║   • Installation time: ~30 seconds                                        ║
║                                                                            ║
║ Suggested Responses:                                                       ║
║   • approve       Accept installation                                     ║
║   • reject        Decline installation                                    ║
║   • ask-alternative  Suggest alternative solution                         ║
║                                                                            ║
║ Respond with: project-manager respond 5 approve                           ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### 5.2 Batch Response Command

**Command**: `project-manager respond-all <response>`

**Usage**:
```bash
# Respond to all normal/high priority questions
project-manager respond-all approve

# Requires confirmation
project-manager respond-all approve --confirm
```

**Implementation**:
```python
def cmd_respond_all(args):
    """Respond to all pending notifications."""
    db = NotificationDB()
    pending = db.get_pending_notifications()

    if not pending:
        console.print("✓ No pending notifications")
        return 0

    # Show what will happen
    console.print(f"[yellow]Will respond to {len(pending)} notification(s):[/yellow]")
    for n in pending:
        console.print(f"  • [{n['id']}] {n['title']}")

    if not args.confirm:
        response = console.input("\nConfirm [y/N]: ")
        if response.lower() != 'y':
            console.print("Cancelled")
            return 0

    for n in pending:
        db.respond_to_notification(n['id'], args.response)

    console.print(f"\n✓ Responded to {len(pending)} notification(s)")
    return 0
```

---

## 6. Consistent Terminal UI Toolkit

### 6.1 Component Expansion

Add to `console_ui.py`:

#### Header Component
```python
def section_title(title: str, subtitle: Optional[str] = None) -> None:
    """Display section title with visual hierarchy."""
```

#### Status Component
```python
def status_item(label: str, status: str, emoji: str = "⚪") -> None:
    """Display status item with emoji and label."""
```

#### Info Box Component
```python
def info_box(items: List[Tuple[str, str]]) -> None:
    """Display key-value items in formatted box."""
```

#### Tree Component (for hierarchical info)
```python
def tree_item(label: str, children: List[str], expanded: bool = False) -> None:
    """Display tree-like structure."""
```

---

## 7. Terminal-Safe Responsive Design

### 7.1 Width Detection

```python
def get_terminal_width() -> int:
    """Get terminal width, default to 80."""
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except:
        return 80

def format_for_width(content: str, target_width: int) -> str:
    """Format content for terminal width."""
    # Detect terminal width
    width = get_terminal_width()

    if width < 60:
        # Mobile/narrow: Stack vertically, reduce info
        return format_compact(content)
    elif width < 100:
        # Normal: Current formatting
        return format_normal(content)
    else:
        # Wide: Use full layout
        return format_wide(content)
```

### 7.2 Responsive Components

**Narrow** (< 60):
```
State: 🟢 Working
Task: PRIORITY 3
Progress: 80%
ETA: 2h
```

**Normal** (60-100):
```
State: 🟢 Working
Task: PRIORITY 3 - Status Reporting
Progress: ████░░░░░░ 80% (2h remaining)
Questions: 2 pending
```

**Wide** (> 100):
```
State: 🟢 Working | Task: PRIORITY 3 - Status Reporting | Progress: 80% (2h)
Context: Iteration 45 | Uptime: 2h 45m | Commits: 8 | Questions: 2
```

---

## 8. Migration Path

### Phase 1: Enhanced Error System (2-3 hours)
1. Implement `error_block()`, `warning_block()` in console_ui.py
2. Update critical error paths in roadmap_cli.py
3. Test error scenarios

### Phase 2: Progress Indicators (2-3 hours)
1. Add progress utilities to console_ui.py
2. Update spec_generation to use progress
3. Add to daemon spec manager

### Phase 3: New Commands (2 hours)
1. `status-quick` command
2. `dashboard` command
3. `help` command

### Phase 4: Notification Improvements (1-2 hours)
1. Enhanced display format
2. Batch response command
3. Better suggestions

### Phase 5: Polish & Testing (1-2 hours)
1. Responsive design testing
2. Cross-terminal testing
3. User feedback iteration

---

## 9. Accessibility Considerations

### 9.1 Color Blindness
- Use emojis in addition to colors
- Never rely on color alone
- Include text symbols (✓ for success, ✗ for error)

### 9.2 Screen Readers
- Add meaningful labels to panels
- Use semantic structure in output
- Avoid pure visual formatting tricks

### 9.3 Terminal Compatibility
- Test on:
  - macOS Terminal.app
  - iTerm2
  - VS Code Terminal
  - GitHub Codespaces
  - Linux terminals

---

## 10. Success Criteria

### UX Improvements
- [ ] Error messages include suggestions (100% coverage)
- [ ] Long operations show progress (all operations > 2s)
- [ ] New commands discovered easily (`help` command works)
- [ ] Status checkable in < 5s (`status-quick` command)
- [ ] Notifications manageable in batch (`respond-all` works)

### Performance
- [ ] Dashboard loads in < 1 second
- [ ] No performance regression on existing commands
- [ ] Memory usage stable during watch mode

### User Satisfaction
- [ ] 80% of users find improvements helpful (survey)
- [ ] 30% reduction in support requests
- [ ] New user onboarding time < 10 minutes

---

**End of Design Specifications**
