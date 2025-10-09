# PRIORITY 2: Minimal Notification UI

**Created**: 2025-10-09
**Status**: 📝 Planned
**Dependency**: PRIORITY 1 (Daemon needs this immediately)
**Duration**: 1 day (6-8 hours)
**Impact**: ⭐⭐⭐⭐⭐ **CRITICAL** - Daemon cannot ask questions without this

---

## Why This Is PRIORITY 2 (Before Database Sync)

**The Problem**: Daemon needs to communicate with user for:
1. ⚠️ **Dependency approval** (before installing packages)
2. ❓ **Design decisions** (e.g., "Use PostgreSQL or SQLite?")
3. 🚨 **Blocking errors** (e.g., "Tests failed, how to proceed?")
4. 📊 **Status updates** (e.g., "Completed PRIORITY 3")

**Without this UI**: Daemon is **deaf and mute** - cannot ask questions, cannot report status!

**Why before Project Manager CLI**: PM CLI is complex (AI, rich UI, slack). This is simple (terminal messages + responses).

---

## Core Requirements

### Must Have (Day 1)

1. **Show Pending Messages** 📬
   - Display all messages waiting for user response
   - Show daemon's current status
   - Show message type (question, approval, status)

2. **Respond to Messages** ✍️
   - Simple command: `coffee-notify respond <id> <answer>`
   - Save response to file (daemon polls for it)

3. **View Daemon Status** 📊
   - Current task (which PRIORITY)
   - Status (working, waiting, blocked)
   - Last activity timestamp

### Nice to Have (Future)

- ❌ Rich terminal UI (basic text is fine)
- ❌ Slack integration (later)
- ❌ Desktop notifications (later)
- ❌ Email notifications (later)

---

## Architecture

### Minimal File-Based Communication (No Database Yet!)

```
data/
├── notifications/
│   ├── pending/
│   │   ├── msg_001_dependency_approval.json
│   │   ├── msg_002_design_question.json
│   │   └── msg_003_error_occurred.json
│   ├── responses/
│   │   ├── msg_001_response.json
│   │   └── msg_002_response.json
│   └── daemon_status.json
```

**Why File-Based** (not database):
- ✅ No database sync issues (comes later in PRIORITY 3)
- ✅ Simple to implement (1 day)
- ✅ Easy to debug (just read JSON files)
- ✅ Works immediately (no schema setup)

---

## Message Format

### Notification (Daemon → User)

```json
{
  "id": "msg_001",
  "type": "dependency_approval",
  "priority": "PRIORITY 2",
  "message": "May I install 'psycopg2-binary>=2.9.9'?",
  "details": {
    "package": "psycopg2-binary>=2.9.9",
    "reason": "Required for PostgreSQL connection pooling",
    "license": "LGPL-3.0",
    "size": "~5MB"
  },
  "options": ["approve", "reject"],
  "timeout": 3600,
  "created_at": "2025-10-09T10:30:00Z",
  "status": "pending"
}
```

### Response (User → Daemon)

```json
{
  "message_id": "msg_001",
  "response": "reject",
  "reason": "We're using SQLite MVP, not PostgreSQL yet",
  "responded_at": "2025-10-09T10:35:00Z"
}
```

### Daemon Status

```json
{
  "status": "waiting_for_response",
  "current_task": "PRIORITY 2: Database Synchronization",
  "blocked_on": "msg_001",
  "last_activity": "2025-10-09T10:30:00Z",
  "uptime_seconds": 3600,
  "tasks_completed": 0,
  "tasks_pending": 3
}
```

---

## CLI Commands

### `coffee-notify` - Minimal Notification CLI

```bash
# View all pending messages
coffee-notify list

# View specific message
coffee-notify view msg_001

# Respond to message
coffee-notify respond msg_001 approve

# Respond with reason
coffee-notify respond msg_001 reject --reason "Use SQLite instead"

# View daemon status
coffee-notify status

# Clear old messages
coffee-notify clean --older-than 24h
```

---

## Implementation

### File: `coffee_maker/cli/notify_cli.py` (~200 LOC)

```python
"""Minimal notification CLI for daemon-user communication.

Simple file-based communication (no database yet).
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Notification directories
DATA_DIR = Path("data/notifications")
PENDING_DIR = DATA_DIR / "pending"
RESPONSES_DIR = DATA_DIR / "responses"
STATUS_FILE = DATA_DIR / "daemon_status.json"

# Ensure directories exist
PENDING_DIR.mkdir(parents=True, exist_ok=True)
RESPONSES_DIR.mkdir(parents=True, exist_ok=True)


class NotificationCLI:
    """Minimal CLI for viewing and responding to daemon notifications."""

    def list_pending(self) -> List[Dict]:
        """List all pending notifications."""
        messages = []
        for file in sorted(PENDING_DIR.glob("*.json")):
            with open(file) as f:
                msg = json.load(f)
                messages.append(msg)
        return messages

    def view_message(self, message_id: str) -> Optional[Dict]:
        """View specific message details."""
        file = PENDING_DIR / f"{message_id}.json"
        if not file.exists():
            return None

        with open(file) as f:
            return json.load(f)

    def respond(self, message_id: str, response: str, reason: str = None):
        """Respond to a pending message."""
        # Check if message exists
        msg_file = PENDING_DIR / f"{message_id}.json"
        if not msg_file.exists():
            print(f"❌ Message {message_id} not found")
            return

        # Create response
        response_data = {
            "message_id": message_id,
            "response": response,
            "reason": reason,
            "responded_at": datetime.utcnow().isoformat() + "Z"
        }

        # Save response
        response_file = RESPONSES_DIR / f"{message_id}_response.json"
        with open(response_file, 'w') as f:
            json.dump(response_data, f, indent=2)

        # Move message to responses (mark as handled)
        msg_file.unlink()

        print(f"✅ Responded to {message_id}: {response}")
        if reason:
            print(f"   Reason: {reason}")

    def get_daemon_status(self) -> Optional[Dict]:
        """Get current daemon status."""
        if not STATUS_FILE.exists():
            return None

        with open(STATUS_FILE) as f:
            return json.load(f)

    def display_list(self):
        """Display list of pending messages (user-friendly)."""
        messages = self.list_pending()

        if not messages:
            print("✅ No pending messages")
            return

        print(f"\n📬 Pending Messages ({len(messages)}):\n")

        for msg in messages:
            # Format based on type
            if msg['type'] == 'dependency_approval':
                icon = "📦"
            elif msg['type'] == 'design_question':
                icon = "❓"
            elif msg['type'] == 'error':
                icon = "🚨"
            else:
                icon = "📝"

            print(f"{icon} [{msg['id']}] {msg['type'].upper()}")
            print(f"   Priority: {msg.get('priority', 'N/A')}")
            print(f"   Message: {msg['message'][:80]}...")
            print(f"   Created: {msg['created_at']}")
            print()

    def display_status(self):
        """Display daemon status (user-friendly)."""
        status = self.get_daemon_status()

        if not status:
            print("❌ Daemon status not available (daemon not running?)")
            return

        print("\n🤖 Daemon Status:\n")
        print(f"Status: {status['status']}")
        print(f"Current Task: {status.get('current_task', 'N/A')}")

        if status.get('blocked_on'):
            print(f"⚠️  Blocked on: {status['blocked_on']}")

        print(f"Last Activity: {status['last_activity']}")
        print(f"Uptime: {status['uptime_seconds'] // 3600}h {(status['uptime_seconds'] % 3600) // 60}m")
        print(f"Completed: {status.get('tasks_completed', 0)} tasks")
        print(f"Pending: {status.get('tasks_pending', 0)} tasks")


def main():
    """CLI entry point."""
    cli = NotificationCLI()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  coffee-notify list")
        print("  coffee-notify view <message_id>")
        print("  coffee-notify respond <message_id> <response> [--reason \"...\"]")
        print("  coffee-notify status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        cli.display_list()

    elif command == "view":
        if len(sys.argv) < 3:
            print("Usage: coffee-notify view <message_id>")
            sys.exit(1)

        msg_id = sys.argv[2]
        msg = cli.view_message(msg_id)

        if not msg:
            print(f"❌ Message {msg_id} not found")
            sys.exit(1)

        print(json.dumps(msg, indent=2))

    elif command == "respond":
        if len(sys.argv) < 4:
            print("Usage: coffee-notify respond <message_id> <response> [--reason \"...\"]")
            sys.exit(1)

        msg_id = sys.argv[2]
        response = sys.argv[3]
        reason = None

        if len(sys.argv) > 4 and sys.argv[4] == "--reason":
            reason = sys.argv[5] if len(sys.argv) > 5 else None

        cli.respond(msg_id, response, reason)

    elif command == "status":
        cli.display_status()

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Daemon Integration

### File: `coffee_maker/autonomous/notifications.py` (~150 LOC)

```python
"""Daemon notification system - send messages and wait for responses."""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

PENDING_DIR = Path("data/notifications/pending")
RESPONSES_DIR = Path("data/notifications/responses")
STATUS_FILE = Path("data/notifications/daemon_status.json")


class DaemonNotifications:
    """Handle daemon notifications and user responses."""

    def __init__(self):
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    def send_notification(
        self,
        message_type: str,
        message: str,
        priority: str = None,
        details: Dict = None,
        options: list = None,
        timeout: int = 3600
    ) -> str:
        """Send notification to user and return message ID."""

        message_id = f"msg_{int(time.time())}"

        notification = {
            "id": message_id,
            "type": message_type,
            "priority": priority,
            "message": message,
            "details": details or {},
            "options": options or [],
            "timeout": timeout,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "pending"
        }

        # Write to pending directory
        file_path = PENDING_DIR / f"{message_id}.json"
        with open(file_path, 'w') as f:
            json.dump(notification, f, indent=2)

        print(f"📬 Sent notification: {message_id}")
        print(f"   Message: {message}")
        print(f"   Waiting for user response...")

        return message_id

    def wait_for_response(
        self,
        message_id: str,
        timeout: int = 3600,
        poll_interval: int = 5
    ) -> Optional[Dict]:
        """Wait for user response (polls response directory)."""

        response_file = RESPONSES_DIR / f"{message_id}_response.json"
        start_time = time.time()

        while time.time() - start_time < timeout:
            if response_file.exists():
                with open(response_file) as f:
                    response = json.load(f)

                # Clean up response file
                response_file.unlink()

                print(f"✅ Received response: {response['response']}")
                if response.get('reason'):
                    print(f"   Reason: {response['reason']}")

                return response

            time.sleep(poll_interval)

        print(f"⏰ Timeout waiting for response to {message_id}")
        return None

    def update_status(
        self,
        status: str,
        current_task: str = None,
        blocked_on: str = None,
        tasks_completed: int = 0,
        tasks_pending: int = 0
    ):
        """Update daemon status."""

        status_data = {
            "status": status,
            "current_task": current_task,
            "blocked_on": blocked_on,
            "last_activity": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(time.time() - self.start_time),
            "tasks_completed": tasks_completed,
            "tasks_pending": tasks_pending
        }

        with open(STATUS_FILE, 'w') as f:
            json.dump(status_data, f, indent=2)

    def request_dependency_approval(
        self,
        package: str,
        reason: str,
        license: str = "Unknown",
        size: str = "Unknown"
    ) -> bool:
        """Request approval for new dependency."""

        message_id = self.send_notification(
            message_type="dependency_approval",
            message=f"May I install '{package}'?",
            details={
                "package": package,
                "reason": reason,
                "license": license,
                "size": size
            },
            options=["approve", "reject"],
            timeout=3600
        )

        # Update status
        self.update_status(
            status="waiting_for_response",
            blocked_on=message_id
        )

        # Wait for response
        response = self.wait_for_response(message_id)

        if response and response['response'] == 'approve':
            return True
        else:
            return False
```

---

## Setup Script

### File: `scripts/setup_notifications.py`

```python
"""Setup notification directories and test files."""

from pathlib import Path

# Create directories
Path("data/notifications/pending").mkdir(parents=True, exist_ok=True)
Path("data/notifications/responses").mkdir(parents=True, exist_ok=True)

print("✅ Notification directories created:")
print("   - data/notifications/pending/")
print("   - data/notifications/responses/")
print("   - data/notifications/daemon_status.json")
print("\nReady to use coffee-notify CLI!")
```

---

## Testing

### Manual Test

```bash
# 1. Setup
python scripts/setup_notifications.py

# 2. Create test notification (simulating daemon)
python -c "
from coffee_maker.autonomous.notifications import DaemonNotifications
notif = DaemonNotifications()
notif.send_notification(
    message_type='test',
    message='Test notification from daemon',
    priority='TEST'
)
"

# 3. View pending messages
coffee-notify list

# 4. Respond to message
coffee-notify respond msg_XXXXX approve --reason "Test approved"

# 5. Check status
coffee-notify status
```

---

## Success Criteria

✅ **Day 1 Complete** if:
1. User can run `coffee-notify list` and see pending messages
2. User can run `coffee-notify respond <id> <answer>`
3. Daemon can send notifications via file system
4. Daemon can wait for and receive responses
5. Daemon status is visible via `coffee-notify status`

---

## Future Enhancements (After PRIORITY 3+)

- Database backend (replace file system)
- Rich terminal UI (colors, tables, progress bars)
- Slack integration (notifications to Slack channel)
- Desktop notifications (system tray)
- Email notifications (critical alerts)
- Web UI (browser-based notification center)

---

## Why This Enables Autonomous Development

**Without this**: Daemon is blind and mute
- Cannot ask for dependency approval → Blocked
- Cannot ask design questions → Makes wrong choices
- Cannot report errors → Silent failures
- User has no visibility into daemon activity

**With this**: Daemon can communicate
- ✅ Asks permission before installing packages
- ✅ Asks design questions when unsure
- ✅ Reports errors and waits for guidance
- ✅ User always knows daemon status

**This unlocks true autonomous development!** 🚀

---

**Status**: 📝 Ready to implement
**Estimated Time**: 6-8 hours (1 day)
**Next**: Implement after PRIORITY 1 (Daemon core) is complete
