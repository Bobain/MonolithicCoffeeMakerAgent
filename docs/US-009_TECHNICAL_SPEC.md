# US-009 Technical Specification: Process Management & Status Monitoring

**Status**: 🔄 In Progress
**Created**: 2025-10-10
**Estimated Duration**: 5 working days (1 week)
**Complexity**: Medium
**Impact**: High (Enables v0.2.0 release)

---

## 1. Overview

### User Story
> "As a project_manager user, I want to know if the code_developer process is up so that I can watch the current progress, ask him to do something, ask him to answer a question, answer a question he asked me, etc. The code_developer can delay his answers for more than 12 hours, as he needs to focus or rest, and have other activities."

### Business Context
The current system treats code_developer and project_manager as completely separate processes with no integrated management. This creates a fragmented experience requiring manual terminal management and no visibility into daemon status.

The key insight is that code_developer should be treated like a **human developer colleague**:
- May not respond immediately (needs focus time)
- Takes breaks and has other activities
- Will get back to you when ready (async communication)
- You should be able to check their status without interrupting them

### Goals
1. **Status Awareness**: Always know if code_developer is running and what it's doing
2. **Process Control**: Start/stop daemon from project_manager chat
3. **Bidirectional Communication**: Send commands and receive responses asynchronously
4. **Unified Experience**: Single interface for all daemon interactions
5. **Graceful Async**: Handle delayed responses (12+ hours) naturally

### Non-Goals
- Real-time streaming of daemon logs (too noisy)
- Forcing immediate daemon responses (respect focus time)
- Complex daemon clustering or load balancing (future)
- Web-based dashboard (future, separate from chat)

---

## 2. Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│           project_manager (Chat Interface)              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  ChatInterface                                    │  │
│  │  - Shows daemon status in header                 │  │
│  │  - Handles /status, /start, /stop commands       │  │
│  │  - Natural language command detection            │  │
│  └───────────┬───────────────────────────────────────┘  │
│              │ uses                                      │
│  ┌───────────▼───────────────────────────────────────┐  │
│  │  ProcessManager                                   │  │
│  │  - is_daemon_running() → bool                     │  │
│  │  - get_daemon_status() → Dict                     │  │
│  │  - start_daemon() → bool                          │  │
│  │  - stop_daemon() → bool                           │  │
│  └───────────┬───────────────────────────────────────┘  │
└──────────────┼───────────────────────────────────────────┘
               │
               │ reads/writes PID file
               │ checks process via psutil
               ▼
    ~/.coffee_maker/daemon.pid
    ~/.coffee_maker/daemon_status.json
               │
               │ monitors
               ▼
┌──────────────────────────────────────────────────────────┐
│           code_developer (Daemon Process)                │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Daemon Main Loop                                  │  │
│  │  - Writes PID file on startup                     │  │
│  │  - Updates status file with current task          │  │
│  │  - Checks notifications for commands               │  │
│  │  - Responds to questions asynchronously            │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
               │
               │ communicates via
               ▼
    data/notifications.db (SQLite)
    - Commands from PM to daemon
    - Questions from daemon to PM
    - Async responses (12+ hour delays OK)
```

### Component Breakdown

#### 1. ProcessManager (`coffee_maker/process_manager.py`)
**Responsibility**: Detect, start, stop, and monitor the code_developer daemon process

**Key Methods**:
- `is_daemon_running() -> bool`: Check if process exists and is actually code_developer
- `get_daemon_status() -> Dict`: Get detailed status (PID, uptime, CPU, memory, current task)
- `start_daemon(background: bool = True) -> bool`: Launch daemon process
- `stop_daemon(timeout: int = 10) -> bool`: Gracefully terminate daemon
- `_get_current_task() -> Optional[str]`: Extract current task from status file or ROADMAP
- `_read_pid_file() -> Optional[int]`: Read PID from file
- `_write_pid_file(pid: int)`: Write PID to file
- `_clean_stale_pid()`: Remove invalid PID files

**Dependencies**:
- `psutil`: Cross-platform process management
- `pathlib`: File path handling
- `subprocess`: Process spawning
- `signal`: Graceful shutdown signals

#### 2. ChatInterface Updates (`coffee_maker/cli/chat_interface.py`)
**Responsibility**: Integrate daemon status display and control commands

**New Methods**:
- `_update_status_display()`: Refresh daemon status
- `_cmd_daemon_status()`: Handle `/status` command
- `_cmd_daemon_start()`: Handle `/start` command
- `_cmd_daemon_stop()`: Handle `/stop` command
- `_send_command_to_daemon(command: str)`: Send command via notifications
- `_check_daemon_questions()`: Check for pending daemon questions

**Updated Methods**:
- `__init__()`: Initialize ProcessManager
- `_show_welcome()`: Display daemon status in welcome message
- `_handle_command()`: Add new commands (/status, /start, /stop)
- `_handle_natural_language_stream()`: Detect daemon-related natural language

#### 3. Daemon CLI Updates (`coffee_maker/autonomous/daemon_cli.py`)
**Responsibility**: Write PID file on startup, update status file during work

**New Features**:
- Write PID file immediately after startup
- Update status file with current task when starting work
- Clean PID file on graceful shutdown
- Handle SIGTERM for graceful shutdown

---

## 3. Implementation Plan

### Phase 1: Process Detection (Days 1-2)

#### Task 1.1: Create ProcessManager Class
**File**: `coffee_maker/process_manager.py`

```python
"""Process management for code_developer daemon."""

import logging
import psutil
from pathlib import Path
from typing import Optional, Dict
import json

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages code_developer daemon process lifecycle."""

    def __init__(self):
        """Initialize process manager."""
        self.config_dir = Path.home() / ".coffee_maker"
        self.config_dir.mkdir(exist_ok=True)

        self.pid_file = self.config_dir / "daemon.pid"
        self.status_file = self.config_dir / "daemon_status.json"

        logger.info("ProcessManager initialized")

    def is_daemon_running(self) -> bool:
        """Check if code_developer daemon is running.

        Returns:
            True if daemon is running, False otherwise
        """
        pid = self._read_pid_file()
        if pid is None:
            return False

        try:
            # Check if process exists
            process = psutil.Process(pid)

            # Verify it's actually the daemon (not a recycled PID)
            cmdline = " ".join(process.cmdline())
            is_daemon = (
                "code-developer" in cmdline or
                "daemon_cli.py" in cmdline or
                "coffee_maker.autonomous.daemon_cli" in cmdline
            )

            if not is_daemon:
                logger.warning(f"PID {pid} exists but is not code_developer daemon")
                self._clean_stale_pid()
                return False

            return True

        except psutil.NoSuchProcess:
            logger.debug(f"PID {pid} no longer exists")
            self._clean_stale_pid()
            return False
        except Exception as e:
            logger.error(f"Error checking daemon status: {e}")
            return False

    def get_daemon_status(self) -> Dict:
        """Get detailed daemon status information.

        Returns:
            Dict with keys: running, pid, status, current_task, uptime,
            cpu_percent, memory_mb
        """
        if not self.is_daemon_running():
            return {
                "running": False,
                "status": "stopped",
                "current_task": None,
                "uptime": None,
                "pid": None,
                "cpu_percent": 0.0,
                "memory_mb": 0.0
            }

        pid = self._read_pid_file()

        try:
            process = psutil.Process(pid)

            # Get current task
            current_task = self._get_current_task()

            return {
                "running": True,
                "pid": pid,
                "status": "working" if current_task else "idle",
                "current_task": current_task,
                "uptime": process.create_time(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error getting daemon status: {e}")
            return {
                "running": False,
                "status": "error",
                "current_task": None,
                "uptime": None,
                "pid": pid,
                "cpu_percent": 0.0,
                "memory_mb": 0.0
            }

    def _get_current_task(self) -> Optional[str]:
        """Get current task daemon is working on.

        Returns:
            Task name or None if idle
        """
        # Try status file first (most accurate)
        if self.status_file.exists():
            try:
                with open(self.status_file) as f:
                    data = json.load(f)
                    task = data.get("current_task")
                    if task:
                        return task
            except Exception as e:
                logger.warning(f"Failed to read status file: {e}")

        # Fallback: Check ROADMAP for in-progress priorities
        try:
            from coffee_maker.cli.roadmap_editor import RoadmapEditor

            editor = RoadmapEditor("docs/roadmap/ROADMAP.md")
            priorities = editor.list_priorities()

            for p in priorities:
                status = p.get("status", "")
                if "🔄" in status or "In Progress" in status:
                    return p.get("name", "Unknown priority")
        except Exception as e:
            logger.warning(f"Failed to check ROADMAP: {e}")

        return None

    def _read_pid_file(self) -> Optional[int]:
        """Read PID from file.

        Returns:
            PID as integer or None if file doesn't exist/is invalid
        """
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file) as f:
                pid_str = f.read().strip()
                return int(pid_str)
        except (ValueError, IOError) as e:
            logger.warning(f"Invalid PID file: {e}")
            return None

    def _write_pid_file(self, pid: int):
        """Write PID to file.

        Args:
            pid: Process ID to write
        """
        try:
            with open(self.pid_file, "w") as f:
                f.write(str(pid))
            logger.info(f"Wrote PID {pid} to {self.pid_file}")
        except IOError as e:
            logger.error(f"Failed to write PID file: {e}")

    def _clean_stale_pid(self):
        """Remove stale PID file."""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
                logger.info("Cleaned stale PID file")
            except Exception as e:
                logger.warning(f"Failed to remove stale PID file: {e}")
```

**Testing**:
```python
# Manual test
from coffee_maker.process_manager import ProcessManager

pm = ProcessManager()
print(f"Daemon running: {pm.is_daemon_running()}")
print(f"Status: {pm.get_daemon_status()}")
```

#### Task 1.2: Add PID File Writing to Daemon
**File**: `coffee_maker/autonomous/daemon_cli.py`

**Changes**:
1. Import ProcessManager
2. Write PID file on startup
3. Clean PID file on shutdown
4. Handle SIGTERM for graceful shutdown

```python
# Add at top of file
import signal
import sys
from coffee_maker.process_manager import ProcessManager

# In main() function, after initialization
def main():
    # ... existing setup ...

    # Write PID file
    process_manager = ProcessManager()
    process_manager._write_pid_file(os.getpid())

    # Register signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        process_manager._clean_stale_pid()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # ... existing daemon loop ...
        pass
    finally:
        # Clean up on exit
        process_manager._clean_stale_pid()
        logger.info("Daemon shutdown complete")
```

**Deliverable**: ProcessManager can accurately detect if daemon is running

---

### Phase 2: Process Control (Days 2-3)

#### Task 2.1: Add Start/Stop Methods to ProcessManager

```python
# Add to ProcessManager class

import subprocess
import time

def start_daemon(self, background: bool = True) -> bool:
    """Start the code_developer daemon.

    Args:
        background: If True, start in background. If False, run in foreground.

    Returns:
        True if daemon started successfully, False otherwise
    """
    if self.is_daemon_running():
        logger.info("Daemon is already running")
        return True

    logger.info("Starting code_developer daemon...")

    # Build command
    cmd = ["poetry", "run", "code-developer"]

    try:
        if background:
            # Start in background (detached from parent)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # Detach from terminal
                cwd=Path.cwd()  # Use current working directory
            )

            # PID will be written by daemon itself
            logger.info(f"Daemon started with PID {process.pid}")

            # Wait briefly to ensure it started
            time.sleep(2)

            # Verify it's running
            if self.is_daemon_running():
                logger.info("Daemon started successfully")
                return True
            else:
                logger.error("Daemon failed to start")
                return False
        else:
            # Run in foreground (for debugging)
            subprocess.run(cmd)
            return True

    except Exception as e:
        logger.error(f"Failed to start daemon: {e}")
        return False

def stop_daemon(self, timeout: int = 10) -> bool:
    """Stop the daemon gracefully.

    Args:
        timeout: Seconds to wait for graceful shutdown before force kill

    Returns:
        True if daemon stopped successfully, False otherwise
    """
    if not self.is_daemon_running():
        logger.info("Daemon is not running")
        return True

    pid = self._read_pid_file()

    logger.info(f"Stopping daemon (PID {pid})...")

    try:
        process = psutil.Process(pid)

        # Send SIGTERM for graceful shutdown
        logger.info("Sending SIGTERM for graceful shutdown...")
        process.terminate()

        # Wait for graceful exit
        try:
            process.wait(timeout=timeout)
            logger.info("Daemon stopped gracefully")
        except psutil.TimeoutExpired:
            # Force kill if timeout exceeded
            logger.warning("Graceful shutdown timed out, force killing...")
            process.kill()
            logger.info("Daemon force killed")

        # Clean up PID file
        self._clean_stale_pid()
        return True

    except psutil.NoSuchProcess:
        logger.info("Process already stopped")
        self._clean_stale_pid()
        return True
    except Exception as e:
        logger.error(f"Error stopping daemon: {e}")
        return False
```

**Testing**:
```python
pm = ProcessManager()

# Start daemon
assert pm.start_daemon() == True
time.sleep(3)
assert pm.is_daemon_running() == True

# Stop daemon
assert pm.stop_daemon() == True
time.sleep(2)
assert pm.is_daemon_running() == False
```

**Deliverable**: Can reliably start and stop daemon from code

---

### Phase 3: Status Display in Chat (Days 3-4)

#### Task 3.1: Integrate ProcessManager into ChatInterface

**File**: `coffee_maker/cli/chat_interface.py`

```python
# Add import at top
from coffee_maker.process_manager import ProcessManager

# In __init__
def __init__(self, editor: RoadmapEditor, console: Console, ai_service: AIService, notif_service: NotificationService):
    # ... existing init ...

    # Add process manager
    self.process_manager = ProcessManager()
    self.daemon_status_text = ""

    # Update status on init
    self._update_status_display()

def _update_status_display(self):
    """Update daemon status text for display."""
    status = self.process_manager.get_daemon_status()

    if status["running"]:
        if status["current_task"]:
            emoji = "🟢"
            text = f"Daemon: Active - Working on {status['current_task']}"
        else:
            emoji = "🟡"
            text = "Daemon: Idle - Waiting for tasks"
    else:
        emoji = "🔴"
        text = "Daemon: Stopped"

    self.daemon_status_text = f"{emoji} {text}"
    logger.debug(f"Status updated: {self.daemon_status_text}")

def _show_welcome(self):
    """Show welcome message with daemon status."""
    self.console.print("\n[bold cyan]Welcome to Coffee Maker Project Manager![/] 🤖")
    self.console.print("[dim]Type 'help' for commands, or just chat naturally.[/]\n")

    # Show daemon status
    self.console.print(f"[cyan]{self.daemon_status_text}[/]")
    self.console.print("[dim]Use /status for detailed info, /start to launch daemon[/]\n")
```

#### Task 3.2: Add Control Commands

```python
def _handle_command(self, text: str):
    """Handle slash commands."""
    # ... existing commands ...

    if text == "/status":
        return self._cmd_daemon_status()
    elif text == "/start":
        return self._cmd_daemon_start()
    elif text == "/stop":
        return self._cmd_daemon_stop()
    elif text == "/restart":
        return self._cmd_daemon_restart()

    # ... rest of existing code ...

def _cmd_daemon_status(self) -> str:
    """Show detailed daemon status."""
    self._update_status_display()
    status = self.process_manager.get_daemon_status()

    if not status["running"]:
        return """
❌ **Daemon Status: STOPPED**

The code_developer daemon is not currently running.

Use `/start` to launch it.
        """.strip()

    # Calculate uptime
    from datetime import datetime, timedelta
    uptime_seconds = datetime.now().timestamp() - status["uptime"]
    uptime = str(timedelta(seconds=int(uptime_seconds)))

    # Format current task
    task = status["current_task"] or "None (Idle)"

    return f"""
🟢 **Daemon Status: RUNNING**

- **PID**: {status['pid']}
- **Status**: {status['status'].upper()}
- **Current Task**: {task}
- **Uptime**: {uptime}
- **CPU**: {status['cpu_percent']:.1f}%
- **Memory**: {status['memory_mb']:.1f} MB

💡 **Tip**: code_developer may take time to respond (12+ hours is normal).
   He needs focus time and rest, just like a human developer!

Use `/stop` to shut down the daemon gracefully.
    """.strip()

def _cmd_daemon_start(self) -> str:
    """Start the daemon."""
    if self.process_manager.is_daemon_running():
        self._update_status_display()
        return "✅ Daemon is already running!"

    self.console.print("[cyan]Starting code_developer daemon...[/]")

    success = self.process_manager.start_daemon(background=True)

    if success:
        self._update_status_display()
        return """
✅ **Daemon Started Successfully!**

The code_developer daemon is now running in the background.

He'll start working on priorities from the roadmap and will
respond to your messages when he has time (might take 12+ hours).

Use `/status` to check what he's working on.
        """.strip()
    else:
        return """
❌ **Failed to Start Daemon**

Could not start the code_developer daemon.

**Troubleshooting**:
- Check that you have a valid ANTHROPIC_API_KEY in .env
- Ensure no other daemon is running
- Check logs for errors

Try running manually: `poetry run code-developer`
        """.strip()

def _cmd_daemon_stop(self) -> str:
    """Stop the daemon."""
    if not self.process_manager.is_daemon_running():
        self._update_status_display()
        return "⚠️  Daemon is not running."

    self.console.print("[cyan]Stopping daemon gracefully...[/]")

    success = self.process_manager.stop_daemon(timeout=10)

    if success:
        self._update_status_display()
        return """
✅ **Daemon Stopped Successfully**

The code_developer daemon has been shut down gracefully.

Use `/start` to launch it again when needed.
        """.strip()
    else:
        return """
❌ **Failed to Stop Daemon**

Could not stop the daemon gracefully.

You may need to kill the process manually:
1. Run `/status` to get the PID
2. Run `kill <PID>` in terminal

        """.strip()

def _cmd_daemon_restart(self) -> str:
    """Restart the daemon."""
    self.console.print("[cyan]Restarting daemon...[/]")

    # Stop if running
    if self.process_manager.is_daemon_running():
        self.console.print("[cyan]Stopping current daemon...[/]")
        self.process_manager.stop_daemon()
        time.sleep(2)

    # Start fresh
    self.console.print("[cyan]Starting daemon...[/]")
    success = self.process_manager.start_daemon()

    self._update_status_display()

    if success:
        return "✅ Daemon restarted successfully!"
    else:
        return "❌ Failed to restart daemon. Check logs."
```

**Deliverable**: Chat interface shows daemon status and provides control commands

---

### Phase 4: Bidirectional Communication (Days 4-5)

#### Task 4.1: Natural Language Command Detection

```python
def _handle_natural_language_stream(self, text: str, context: Dict) -> str:
    """Handle natural language with daemon awareness."""

    # Detect daemon-related commands
    daemon_keywords = [
        "ask daemon", "tell daemon", "daemon implement",
        "daemon work on", "daemon start working", "daemon please",
        "ask code_developer", "tell code_developer"
    ]

    if any(keyword in text.lower() for keyword in daemon_keywords):
        return self._send_command_to_daemon(text)

    # Detect status queries
    status_keywords = [
        "daemon status", "what is daemon doing", "is daemon working",
        "daemon progress", "what's daemon working on", "code_developer status"
    ]

    if any(keyword in text.lower() for keyword in status_keywords):
        return self._cmd_daemon_status()

    # Normal AI-powered response
    return self._stream_ai_response(text, context)

def _send_command_to_daemon(self, command: str) -> str:
    """Send command to daemon via notifications.

    Args:
        command: Natural language command for daemon

    Returns:
        Confirmation message
    """
    # Check if daemon is running
    if not self.process_manager.is_daemon_running():
        return """
⚠️  **Daemon Not Running**

I can't send commands to the daemon because it's not running.

Would you like me to start it? Use `/start` to launch the daemon.
        """.strip()

    # Create notification for daemon
    notif_id = self.notif_service.create_notification(
        type="command",
        title="Command from project-manager",
        message=command,
        priority="high",
        context={"timestamp": datetime.now().isoformat()}
    )

    return f"""
✅ **Command Sent to Daemon** (Notification #{notif_id})

Your message has been delivered to code_developer.

⏰ **Response Time**: He may take 12+ hours to respond.
   Like a human developer, he needs focus time and rest periods.

💡 **Tip**: Use `/notifications` to check for his response later.
    """.strip()

def _check_daemon_questions(self):
    """Check for pending questions from daemon and display them."""
    questions = self.notif_service.get_pending_notifications(
        type="question"
    )

    if questions:
        self.console.print("\n[yellow]📋 Daemon Has Questions:[/]\n")

        for q in questions[:5]:  # Show top 5
            created = q.get("created_at", "Unknown time")
            self.console.print(f"  [bold]#{q['id']}[/]: {q['title']}")
            self.console.print(f"  [dim]{created}[/]")
            self.console.print(f"  {q['message'][:100]}...")
            self.console.print()

        if len(questions) > 5:
            self.console.print(f"[dim]  ...and {len(questions) - 5} more[/]\n")

        self.console.print("[dim]Use /notifications to view and respond[/]\n")
```

#### Task 4.2: Periodic Status Updates

```python
# In chat loop
def chat_loop(self):
    """Main chat loop with periodic status updates."""

    # Check for daemon questions on startup
    self._check_daemon_questions()

    message_count = 0

    while True:
        try:
            # Get user input
            user_input = self.prompt_session.prompt(
                "[You] ",
                # ... prompt settings ...
            )

            # Update status every 10 messages
            message_count += 1
            if message_count % 10 == 0:
                old_status = self.daemon_status_text
                self._update_status_display()

                # Alert if status changed
                if old_status != self.daemon_status_text:
                    self.console.print(f"\n[cyan]Status Update: {self.daemon_status_text}[/]\n")

            # Check for new daemon questions every 10 messages
            if message_count % 10 == 0:
                self._check_daemon_questions()

            # ... handle user input ...

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Use 'exit' or 'quit' to leave[/]")
        except EOFError:
            break
```

**Deliverable**: Full bidirectional communication with async support

---

## 4. Testing Strategy

### Unit Tests

```python
# tests/test_process_manager.py

import pytest
from coffee_maker.process_manager import ProcessManager

def test_is_daemon_running_when_stopped():
    pm = ProcessManager()
    assert pm.is_daemon_running() == False

def test_start_daemon():
    pm = ProcessManager()
    assert pm.start_daemon() == True
    assert pm.is_daemon_running() == True

def test_stop_daemon():
    pm = ProcessManager()
    pm.start_daemon()
    assert pm.stop_daemon() == True
    assert pm.is_daemon_running() == False

def test_get_status_when_running():
    pm = ProcessManager()
    pm.start_daemon()

    status = pm.get_daemon_status()
    assert status["running"] == True
    assert status["pid"] is not None
    assert status["status"] in ["idle", "working"]

def test_stale_pid_cleanup():
    pm = ProcessManager()

    # Write fake PID
    pm._write_pid_file(99999)

    # Should clean stale PID
    assert pm.is_daemon_running() == False
    assert not pm.pid_file.exists()
```

### Integration Tests

```bash
# Manual integration test script

# 1. Start project-manager chat
poetry run project-manager chat

# 2. Check status (daemon should be stopped)
/status
# Expected: "Daemon Status: STOPPED"

# 3. Start daemon
/start
# Expected: "Daemon Started Successfully!"
# Wait 3 seconds

# 4. Check status again
/status
# Expected: "Daemon Status: RUNNING" with details

# 5. Send command
Ask the daemon to check the roadmap

# Expected: "Command Sent to Daemon"

# 6. Check notifications
/notifications
# Should see command in list

# 7. Stop daemon
/stop
# Expected: "Daemon Stopped Successfully"

# 8. Verify stopped
/status
# Expected: "Daemon Status: STOPPED"
```

### Edge Cases to Test

1. **Stale PID file**: Daemon crashed but PID file remains
2. **Multiple starts**: Calling /start when daemon already running
3. **Multiple stops**: Calling /stop when daemon not running
4. **PID reuse**: System assigns same PID to different process
5. **Permission errors**: Can't write PID file
6. **Daemon crash**: Process dies unexpectedly
7. **Network issues**: Can't communicate with daemon
8. **Long-running tasks**: Daemon busy for hours

---

## 5. Success Criteria

### Functional Requirements
- [ ] `/status` command shows accurate daemon information
- [ ] `/start` command launches daemon in background
- [ ] `/stop` command gracefully shuts down daemon
- [ ] Chat header shows real-time daemon status
- [ ] Natural language commands reach daemon via notifications
- [ ] Daemon questions appear in chat interface
- [ ] System handles 12+ hour response delays gracefully

### Non-Functional Requirements
- [ ] Status check completes in <1 second
- [ ] Daemon starts within 3 seconds
- [ ] Graceful shutdown completes within 10 seconds
- [ ] Zero orphaned daemon processes
- [ ] Works cross-platform (Mac, Linux, Windows)
- [ ] Clear error messages for all failure modes

### User Experience
- [ ] User always knows if daemon is running
- [ ] User can control daemon without leaving chat
- [ ] Async communication feels natural
- [ ] Status changes are visible without polling
- [ ] Commands to daemon are acknowledged immediately

---

## 6. Deployment

### Prerequisites
- psutil already installed (pyproject.toml: psutil = "^7.0.0")
- No new dependencies needed

### Configuration Files
```bash
# ~/.coffee_maker/daemon.pid
# Contains daemon process ID (single line)
12345

# ~/.coffee_maker/daemon_status.json
# Contains current daemon state
{
  "current_task": "PRIORITY 2.6 - CI Testing",
  "started_at": "2025-10-10T14:30:00",
  "last_updated": "2025-10-10T15:45:00"
}
```

### Migration
No breaking changes. Existing installations will work immediately after update.

### Rollback Plan
If issues occur:
1. Revert `coffee_maker/cli/chat_interface.py` changes
2. Remove `coffee_maker/process_manager.py`
3. Revert `coffee_maker/autonomous/daemon_cli.py` changes
4. Users can still launch daemon manually as before

---

## 7. Future Enhancements

### Post-MVP Features
- **Status persistence**: Track daemon uptime history
- **Performance metrics**: Tasks completed per hour
- **Email notifications**: Alert on daemon crashes
- **Web dashboard**: Visual monitoring interface
- **Cluster management**: Multiple daemons in parallel
- **Auto-restart**: Daemon restarts after crashes
- **Health checks**: Periodic daemon health monitoring

### Related Stories
- US-007: IDE completion needs daemon status
- US-008: User assistant needs daemon coordination
- PRIORITY 2.7: Crash recovery builds on this

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| PID file corruption | Medium | Low | Validate PID format, clean stale files |
| Process detection fails | High | Low | Verify cmdline, fallback to status file |
| Cross-platform issues | High | Medium | Use psutil for all OS operations |
| Daemon doesn't write PID | High | Low | Write PID early, log failures |
| Graceful shutdown fails | Medium | Medium | Force kill after timeout |
| Multiple PMs start daemon | Medium | Low | File locking (future) |

---

## 9. Completion Checklist

### Phase 1: Process Detection
- [ ] ProcessManager class created
- [ ] PID file read/write working
- [ ] is_daemon_running() accurate
- [ ] get_daemon_status() returns correct info
- [ ] Daemon writes PID on startup
- [ ] Unit tests passing

### Phase 2: Process Control
- [ ] start_daemon() launches process
- [ ] stop_daemon() gracefully shuts down
- [ ] Background mode working
- [ ] Signal handlers registered
- [ ] PID cleanup on exit

### Phase 3: Status Display
- [ ] ChatInterface integrated
- [ ] Status shown in header
- [ ] /status command working
- [ ] /start command working
- [ ] /stop command working
- [ ] Status updates periodically

### Phase 4: Communication
- [ ] Natural language detection
- [ ] Commands sent via notifications
- [ ] Daemon questions displayed
- [ ] Async messaging working
- [ ] 12+ hour delays handled gracefully

### Documentation & Testing
- [ ] Technical spec complete (this document)
- [ ] Unit tests written and passing
- [ ] Integration tests performed
- [ ] Documentation updated
- [ ] Commit messages clear
- [ ] ROADMAP updated

---

**Status**: Ready for implementation
**Next Step**: Begin Phase 1 - Create ProcessManager class
