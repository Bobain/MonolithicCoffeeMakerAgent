# PRIORITY 4: Developer Status Dashboard - Technical Specification

**Version**: 1.0
**Created**: 2025-10-11
**Status**: Draft
**Dependencies**: PRIORITY 1 (Daemon), PRIORITY 2 (PM CLI), PRIORITY 3 (Package & Binaries)

---

## 1. Overview

### 1.1 Goal

Enhance `project-manager` CLI to display real-time status of the `code-developer` daemon, including:
- Current state (WORKING, BLOCKED, TESTING, etc.)
- Progress percentage (0-100%)
- Recent activity log
- Pending questions waiting for user response
- ETA for current task

### 1.2 User Stories

**US-1**: As a user, I want to see what the developer is doing RIGHT NOW
**US-2**: As a user, I want to know if the developer is stuck or blocked
**US-3**: As a user, I want to see progress percentage and ETA
**US-4**: As a user, I want to see recent activities (commits, tests, file changes)
**US-5**: As a user, I want to see pending questions immediately

### 1.3 Success Metrics

- User can check developer status in < 2 seconds
- Status accuracy: 100% (always reflects daemon's actual state)
- Status freshness: < 60 seconds (updates every minute or on state change)
- User satisfaction: Remove "black box" feeling

---

## 2. Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  code-developer daemon                                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  DeveloperStatus Class                           │  │
│  │  • update_status(status, task, progress)         │  │
│  │  • report_activity(type, description)            │  │
│  │  • report_progress(progress, current_step)       │  │
│  └──────────────────────────────────────────────────┘  │
│                       ↓                                 │
│              Writes to status file                      │
│                       ↓                                 │
└───────────────────────┼─────────────────────────────────┘
                        │
                        ↓
        ┌───────────────────────────────────┐
        │  data/developer_status.json       │
        │  (Shared file system)             │
        └───────────────────────────────────┘
                        ↓
                        │
┌───────────────────────┼─────────────────────────────────┐
│                       ↓                                 │
│  project-manager CLI                                    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  DeveloperStatusDisplay Class                    │  │
│  │  • show_status()                                 │  │
│  │  • show_activity_log()                           │  │
│  │  • show_questions()                              │  │
│  │  • watch_mode()                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Components

#### 2.2.1 Daemon Side (Writer)

**File**: `coffee_maker/autonomous/developer_status.py` (NEW)

**Responsibilities**:
- Maintain current state (WORKING, BLOCKED, etc.)
- Track progress percentage
- Log activities
- Calculate ETA
- Write status to JSON file

#### 2.2.2 CLI Side (Reader)

**File**: `coffee_maker/cli/developer_status_display.py` (NEW)

**Responsibilities**:
- Read status JSON file
- Format status for terminal display
- Render progress bars
- Show activity log
- Display pending questions
- Support watch mode (continuous updates)

#### 2.2.3 Integration Points

**File**: `coffee_maker/autonomous/daemon.py` (MODIFY)
- Initialize DeveloperStatus on daemon start
- Call status updates at key points in workflow

**File**: `coffee_maker/cli/roadmap_cli.py` (MODIFY)
- Add `developer-status` command
- Add `developer-status --watch` option

---

## 3. Data Structures

### 3.1 Status File Schema

**File**: `data/developer_status.json`

```json
{
  "status": "working",
  "current_task": {
    "priority": 4,
    "name": "Developer Status Dashboard",
    "started_at": "2025-10-11T10:30:00Z",
    "progress": 60,
    "eta_seconds": 3600,
    "current_step": "Writing status dashboard UI"
  },
  "last_activity": {
    "timestamp": "2025-10-11T11:30:00Z",
    "type": "git_commit",
    "description": "Committed status display logic",
    "details": {
      "files_modified": 3,
      "lines_added": 145,
      "lines_deleted": 12,
      "commit_hash": "abc1234"
    }
  },
  "activity_log": [
    {
      "timestamp": "2025-10-11T10:45:00Z",
      "type": "file_created",
      "description": "Created status.py module"
    },
    {
      "timestamp": "2025-10-11T10:52:00Z",
      "type": "code_change",
      "description": "Implemented real-time status tracking"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "dependency_approval",
      "message": "May I install 'pandas>=2.0.0'?",
      "context": "Required for CSV export with advanced filtering",
      "created_at": "2025-10-11T11:15:00Z",
      "status": "pending"
    }
  ],
  "metrics": {
    "tasks_completed_today": 0,
    "total_commits_today": 4,
    "tests_passed_today": 12,
    "tests_failed_today": 0
  },
  "daemon_info": {
    "pid": 12345,
    "started_at": "2025-10-11T08:00:00Z",
    "version": "1.0.0"
  }
}
```

### 3.2 Developer States

```python
class DeveloperState(str, Enum):
    WORKING = "working"      # 🟢 Actively implementing
    TESTING = "testing"      # 🟡 Running tests
    BLOCKED = "blocked"      # 🔴 Waiting for user response
    IDLE = "idle"            # ⚪ Between tasks
    THINKING = "thinking"    # 🔵 Analyzing codebase
    REVIEWING = "reviewing"  # 🟣 Creating PR/docs
    STOPPED = "stopped"      # ⚫ Daemon not running
```

### 3.3 Activity Types

```python
class ActivityType(str, Enum):
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    CODE_CHANGE = "code_change"
    GIT_COMMIT = "git_commit"
    GIT_PUSH = "git_push"
    GIT_BRANCH = "git_branch"
    TEST_RUN = "test_run"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"
    QUESTION_ASKED = "question_asked"
    DEPENDENCY_REQUESTED = "dependency_requested"
    ERROR_ENCOUNTERED = "error_encountered"
    STATUS_UPDATE = "status_update"
```

---

## 4. Component Design

### 4.1 DeveloperStatus Class (Daemon Side)

**File**: `coffee_maker/autonomous/developer_status.py`

```python
"""Developer status tracking for daemon."""

import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class DeveloperState(str, Enum):
    """Developer status states."""
    WORKING = "working"
    TESTING = "testing"
    BLOCKED = "blocked"
    IDLE = "idle"
    THINKING = "thinking"
    REVIEWING = "reviewing"
    STOPPED = "stopped"


class ActivityType(str, Enum):
    """Activity log types."""
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    GIT_COMMIT = "git_commit"
    TEST_RUN = "test_run"
    QUESTION_ASKED = "question_asked"
    STATUS_UPDATE = "status_update"


class DeveloperStatus:
    """Track and report developer status."""

    def __init__(self, status_file: Path = None):
        """Initialize status tracker.

        Args:
            status_file: Path to status JSON file (default: data/developer_status.json)
        """
        if status_file is None:
            status_file = Path("data/developer_status.json")
        self.status_file = status_file
        self.current_state = DeveloperState.IDLE
        self.current_task = None
        self.activity_log = []
        self.questions = []

        # Ensure data directory exists
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    def update_status(
        self,
        status: DeveloperState,
        task: Optional[Dict] = None,
        progress: int = 0,
        current_step: str = ""
    ):
        """Update current developer status.

        Args:
            status: Current state
            task: Current task details (priority, name, etc.)
            progress: Progress percentage (0-100)
            current_step: Description of current step
        """
        self.current_state = status

        if task:
            self.current_task = {
                "priority": task.get("priority", 0),
                "name": task.get("name", "Unknown"),
                "started_at": task.get("started_at", datetime.utcnow().isoformat() + "Z"),
                "progress": progress,
                "current_step": current_step,
                "eta_seconds": self._calculate_eta(task, progress)
            }

        self._write_status()

    def report_activity(
        self,
        activity_type: ActivityType,
        description: str,
        details: Optional[Dict] = None
    ):
        """Log an activity.

        Args:
            activity_type: Type of activity
            description: Human-readable description
            details: Additional details (optional)
        """
        activity = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": activity_type.value,
            "description": description
        }

        if details:
            activity["details"] = details

        self.activity_log.append(activity)

        # Keep only last 50 activities
        self.activity_log = self.activity_log[-50:]

        self._write_status()

    def report_progress(self, progress: int, current_step: str):
        """Update progress percentage.

        Args:
            progress: Progress percentage (0-100)
            current_step: Description of current step
        """
        if self.current_task:
            self.current_task["progress"] = progress
            self.current_task["current_step"] = current_step
            self.current_task["eta_seconds"] = self._calculate_eta(
                self.current_task, progress
            )

        self._write_status()

    def add_question(
        self,
        question_id: str,
        question_type: str,
        message: str,
        context: str = ""
    ):
        """Add a pending question.

        Args:
            question_id: Unique question ID
            question_type: Type of question (dependency_approval, design_decision, etc.)
            message: Question message
            context: Additional context
        """
        question = {
            "id": question_id,
            "type": question_type,
            "message": message,
            "context": context,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "pending"
        }

        self.questions.append(question)
        self._write_status()

        # Update state to BLOCKED
        self.update_status(DeveloperState.BLOCKED)

    def remove_question(self, question_id: str):
        """Remove a question (after it's answered).

        Args:
            question_id: Question ID to remove
        """
        self.questions = [q for q in self.questions if q["id"] != question_id]
        self._write_status()

        # If no more questions, return to previous state
        if not self.questions and self.current_state == DeveloperState.BLOCKED:
            self.update_status(DeveloperState.WORKING)

    def _calculate_eta(self, task: Dict, progress: int) -> int:
        """Calculate estimated time remaining.

        Args:
            task: Task details
            progress: Current progress (0-100)

        Returns:
            Estimated seconds remaining
        """
        if progress <= 0:
            return 0

        # Parse started_at
        started_at = datetime.fromisoformat(task["started_at"].replace("Z", ""))
        elapsed = datetime.utcnow() - started_at

        # Calculate total estimated time
        total_estimated = elapsed.total_seconds() * (100 / progress)

        # Calculate remaining
        remaining = total_estimated - elapsed.total_seconds()

        return max(0, int(remaining))

    def _write_status(self):
        """Write current status to JSON file."""
        import os

        status_data = {
            "status": self.current_state.value,
            "current_task": self.current_task,
            "last_activity": self.activity_log[-1] if self.activity_log else None,
            "activity_log": self.activity_log[-20:],  # Last 20 activities
            "questions": self.questions,
            "metrics": {
                "tasks_completed_today": 0,  # TODO: Track this
                "total_commits_today": 0,    # TODO: Track this
                "tests_passed_today": 0,     # TODO: Track this
                "tests_failed_today": 0      # TODO: Track this
            },
            "daemon_info": {
                "pid": os.getpid(),
                "started_at": datetime.utcnow().isoformat() + "Z",
                "version": "1.0.0"
            }
        }

        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
```

### 4.2 DeveloperStatusDisplay Class (CLI Side)

**File**: `coffee_maker/cli/developer_status_display.py`

```python
"""Developer status display for project-manager CLI."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.text import Text


class DeveloperStatusDisplay:
    """Display developer status in terminal."""

    def __init__(self, status_file: Path = None):
        """Initialize status display.

        Args:
            status_file: Path to status JSON file
        """
        if status_file is None:
            status_file = Path("data/developer_status.json")
        self.status_file = status_file
        self.console = Console()

    def show_status(self, watch: bool = False):
        """Display developer status.

        Args:
            watch: If True, continuously update display
        """
        if watch:
            self._watch_mode()
        else:
            self._show_once()

    def _show_once(self):
        """Display status once."""
        status = self._load_status()

        if not status:
            self.console.print("[red]Developer not running or status file not found[/red]")
            return

        # Render status panel
        self.console.print(self._render_status_panel(status))

        # Render activity log
        if status.get("activity_log"):
            self.console.print(self._render_activity_log(status["activity_log"]))

        # Render questions
        if status.get("questions"):
            self.console.print(self._render_questions(status["questions"]))

    def _watch_mode(self):
        """Continuously update status display."""
        with Live(console=self.console, refresh_per_second=1) as live:
            try:
                while True:
                    status = self._load_status()
                    if status:
                        live.update(self._render_status_panel(status))
                    time.sleep(2)
            except KeyboardInterrupt:
                pass

    def _render_status_panel(self, status: Dict) -> Panel:
        """Render status panel.

        Args:
            status: Status data

        Returns:
            Rich Panel
        """
        # Status emoji
        status_emoji = {
            "working": "🟢",
            "testing": "🟡",
            "blocked": "🔴",
            "idle": "⚪",
            "thinking": "🔵",
            "reviewing": "🟣",
            "stopped": "⚫"
        }

        state = status.get("status", "stopped")
        emoji = status_emoji.get(state, "⚫")

        # Build panel content
        content = []
        content.append(f"Status: {emoji} {state.upper()}")

        # Current task
        if status.get("current_task"):
            task = status["current_task"]
            content.append(f"Current Task: PRIORITY {task['priority']} - {task['name']}")

            # Progress bar
            progress = task.get("progress", 0)
            bar = self._render_progress_bar(progress)
            content.append(f"Progress: {bar} {progress}% complete")

            # Time info
            started_at = datetime.fromisoformat(task["started_at"].replace("Z", ""))
            elapsed = datetime.utcnow() - started_at
            content.append(f"Started: {started_at.strftime('%Y-%m-%d %H:%M:%S')} ({self._format_duration(elapsed)} ago)")

            # ETA
            eta_seconds = task.get("eta_seconds", 0)
            if eta_seconds > 0:
                eta = timedelta(seconds=eta_seconds)
                content.append(f"ETA: ~{self._format_duration(eta)} remaining")

            # Current step
            if task.get("current_step"):
                content.append(f"Current Step: {task['current_step']}")

        # Last activity
        if status.get("last_activity"):
            activity = status["last_activity"]
            timestamp = datetime.fromisoformat(activity["timestamp"].replace("Z", ""))
            elapsed = datetime.utcnow() - timestamp
            content.append(f"Last Activity: {self._format_duration(elapsed)} ago - {activity['description']}")

        # Questions and notifications
        num_questions = len(status.get("questions", []))
        content.append(f"Questions Waiting for Response: {num_questions}")

        return Panel(
            "\n".join(content),
            title="🤖 CODE DEVELOPER STATUS",
            border_style="blue"
        )

    def _render_activity_log(self, activities: list) -> Table:
        """Render activity log table.

        Args:
            activities: List of activities

        Returns:
            Rich Table
        """
        table = Table(title="Recent Activity (last 30 min)")
        table.add_column("Time", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="white")

        # Show last 10 activities
        for activity in activities[-10:]:
            timestamp = datetime.fromisoformat(activity["timestamp"].replace("Z", ""))
            time_str = timestamp.strftime("%H:%M")
            table.add_row(time_str, activity["type"], activity["description"])

        return table

    def _render_questions(self, questions: list) -> Panel:
        """Render questions panel.

        Args:
            questions: List of pending questions

        Returns:
            Rich Panel
        """
        content = []
        for i, question in enumerate(questions, 1):
            content.append(f"[Q{i}] {question['type'].upper()} - WAITING")
            content.append(f"  {question['message']}")
            if question.get("context"):
                content.append(f"  Context: {question['context']}")
            content.append(f"  Command: project-manager respond {question['id']} <answer>")
            content.append("")

        content.append(f"Total waiting: {len(questions)} questions")
        content.append("Developer is BLOCKED until you respond!")

        return Panel(
            "\n".join(content),
            title="❓ QUESTIONS WAITING FOR RESPONSE",
            border_style="red"
        )

    def _render_progress_bar(self, progress: int) -> str:
        """Render progress bar as ASCII.

        Args:
            progress: Progress percentage (0-100)

        Returns:
            ASCII progress bar
        """
        width = 20
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return bar

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration as human-readable string.

        Args:
            duration: Time delta

        Returns:
            Formatted string (e.g., "2h 15m")
        """
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"

    def _load_status(self) -> Optional[Dict]:
        """Load status from JSON file.

        Returns:
            Status data or None if file doesn't exist
        """
        if not self.status_file.exists():
            return None

        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.console.print(f"[red]Error loading status: {e}[/red]")
            return None
```

---

## 5. Integration

### 5.1 Daemon Integration

**File**: `coffee_maker/autonomous/daemon.py` (MODIFY)

Add status reporting at key points:

```python
from coffee_maker.autonomous.developer_status import DeveloperStatus, DeveloperState, ActivityType


class DevDaemon:
    def __init__(self, ...):
        # ... existing init ...
        self.status = DeveloperStatus()

    def run(self):
        """Main daemon loop."""
        self.status.update_status(DeveloperState.IDLE)

        while True:
            # Get next priority
            priority = self._get_next_priority()

            if not priority:
                self.status.update_status(DeveloperState.IDLE)
                time.sleep(60)
                continue

            # Start working on priority
            self.status.update_status(
                DeveloperState.THINKING,
                task={
                    "priority": priority["priority"],
                    "name": priority["name"],
                    "started_at": datetime.utcnow().isoformat() + "Z"
                },
                progress=0
            )

            # Implement priority
            self._implement_priority(priority)

    def _implement_priority(self, priority):
        """Implement a priority."""
        # Report progress at key milestones
        self.status.report_progress(10, "Read requirements")

        # Read spec
        spec = self._read_technical_spec(priority)
        self.status.report_progress(20, "Analyzed technical spec")

        # Implement
        self.status.update_status(DeveloperState.WORKING)
        self.status.report_progress(40, "Implementing core logic")

        # ... implementation code ...

        self.status.report_activity(
            ActivityType.FILE_MODIFIED,
            f"Modified {filename}",
            details={"lines_added": 145, "lines_deleted": 12}
        )

        # Run tests
        self.status.update_status(DeveloperState.TESTING)
        self.status.report_progress(70, "Running tests")

        # ... test code ...

        self.status.report_activity(
            ActivityType.TEST_RUN,
            "Tests passed",
            details={"passed": 12, "failed": 0}
        )

        # Create PR
        self.status.update_status(DeveloperState.REVIEWING)
        self.status.report_progress(95, "Creating PR")

        # ... PR code ...

        self.status.report_progress(100, "Task complete")
```

### 5.2 CLI Integration

**File**: `coffee_maker/cli/roadmap_cli.py` (MODIFY)

Add command:

```python
from coffee_maker.cli.developer_status_display import DeveloperStatusDisplay


def cmd_developer_status(args):
    """Show developer status.

    Usage:
        project-manager developer-status
        project-manager developer-status --watch
    """
    display = DeveloperStatusDisplay()
    display.show_status(watch=args.watch)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # ... existing commands ...

    # developer-status command
    status_parser = subparsers.add_parser("developer-status", help="Show developer status")
    status_parser.add_argument("--watch", action="store_true", help="Continuously update display")

    args = parser.parse_args()

    if args.command == "developer-status":
        cmd_developer_status(args)
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**File**: `tests/test_developer_status.py`

```python
def test_status_update():
    """Test status update."""
    status = DeveloperStatus(Path("test_status.json"))
    status.update_status(
        DeveloperState.WORKING,
        task={"priority": 4, "name": "Test Task"},
        progress=50
    )

    # Verify file was written
    assert Path("test_status.json").exists()

    # Verify content
    with open("test_status.json") as f:
        data = json.load(f)
    assert data["status"] == "working"
    assert data["current_task"]["progress"] == 50


def test_activity_log():
    """Test activity logging."""
    status = DeveloperStatus()
    status.report_activity(ActivityType.GIT_COMMIT, "Test commit")

    assert len(status.activity_log) == 1
    assert status.activity_log[0]["type"] == "git_commit"


def test_eta_calculation():
    """Test ETA calculation."""
    task = {
        "started_at": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
    }
    status = DeveloperStatus()
    eta = status._calculate_eta(task, 50)

    # At 50% after 1 hour, ETA should be ~1 hour
    assert 3000 < eta < 4000  # Allow some variance
```

### 6.2 Integration Tests

**File**: `tests/integration/test_status_integration.py`

```python
def test_daemon_status_reporting(daemon_process):
    """Test daemon reports status correctly."""
    # Start daemon
    daemon_process.start()

    # Wait for status file
    time.sleep(5)

    # Load status
    status_file = Path("data/developer_status.json")
    assert status_file.exists()

    with open(status_file) as f:
        data = json.load(f)

    assert data["status"] in ["idle", "thinking", "working"]


def test_cli_status_display():
    """Test CLI displays status."""
    # Create mock status file
    status_data = {
        "status": "working",
        "current_task": {"priority": 4, "name": "Test", "progress": 60}
    }

    with open("data/developer_status.json", 'w') as f:
        json.dump(status_data, f)

    # Run CLI command
    result = subprocess.run(
        ["poetry", "run", "project-manager", "developer-status"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "CODE DEVELOPER STATUS" in result.stdout
    assert "WORKING" in result.stdout
```

---

## 7. Acceptance Criteria

- [ ] `project-manager developer-status` command displays current status
- [ ] Status shows state emoji (🟢 WORKING, 🔴 BLOCKED, etc.)
- [ ] Status shows progress percentage (0-100%)
- [ ] Status shows ETA (estimated time remaining)
- [ ] Status shows recent activities (last 30 min)
- [ ] Status shows pending questions with response commands
- [ ] Status updates within 60 seconds of state change
- [ ] `--watch` mode continuously updates display
- [ ] Daemon reports status at key milestones (0%, 10%, 20%, ..., 100%)
- [ ] Activity log tracks commits, tests, file changes
- [ ] Status file survives daemon crashes (persisted to disk)

---

## 8. Implementation Timeline

**Day 1** (4-6 hours):
- [x] Create technical spec (this document)
- [ ] Implement DeveloperStatus class (developer_status.py)
- [ ] Add status reporting to daemon.py
- [ ] Write unit tests

**Day 2** (2-4 hours):
- [ ] Implement DeveloperStatusDisplay class
- [ ] Add CLI command (developer-status)
- [ ] Test full workflow
- [ ] Update documentation

**Total Estimate**: 6-10 hours

---

## 9. Future Enhancements

- Web UI instead of terminal
- Push notifications (desktop/mobile)
- Historical tracking (graphs over time)
- Multi-developer support
- Slack/Discord integration

---

**Status**: Ready for implementation

**Next Steps**:
1. Review and approve this spec
2. Implement DeveloperStatus class
3. Integrate with daemon
4. Test and iterate
