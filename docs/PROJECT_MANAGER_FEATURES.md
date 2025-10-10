# Project Manager - Complete Feature Reference

A comprehensive guide to all Project Manager CLI commands, options, and features.

---

## Table of Contents

- [Core Commands](#core-commands)
  - [view](#view) - View roadmap
  - [notifications](#notifications) - List notifications
  - [respond](#respond) - Respond to notifications
  - [status](#status) - Daemon status (Phase 2)
  - [sync](#sync) - Sync roadmap (Phase 2)
- [Global Options](#global-options)
- [Exit Codes](#exit-codes)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Use Cases & Examples](#use-cases--examples)

---

## Core Commands

### `view`

**Purpose**: View the project roadmap or a specific priority.

**Syntax**:
```bash
project-manager view [PRIORITY]
```

**Arguments**:
- `PRIORITY` (optional): Priority number or name to view
  - Can be just the number: `1`, `2`, `3`
  - Or full name: `PRIORITY-1`, `PRIORITY-2.5`
  - Case-insensitive

**Behavior**:
- Without argument: Shows first 100 lines of ROADMAP.md
- With argument: Shows complete section for that priority
- Reads from `docs/ROADMAP.md` by default (configurable via `ROADMAP_PATH`)

**Output Format**:
```
================================================================================
Coffee Maker Agent - ROADMAP
================================================================================

[Content from ROADMAP.md]

... (N more lines)

Tip: Use 'project-manager view <priority>' to see specific priority
```

**Examples**:
```bash
# View full roadmap (first 100 lines)
project-manager view

# View PRIORITY 1
project-manager view 1

# View PRIORITY 2.5 (decimal notation)
project-manager view 2.5

# View using full name
project-manager view PRIORITY-3
```

**Exit Codes**:
- `0`: Success
- `1`: ROADMAP not found or priority not found

**Related Commands**:
- `status` - Check what daemon is working on
- `notifications` - See pending items

---

### `notifications`

**Purpose**: List all pending notifications from the autonomous daemon.

**Syntax**:
```bash
project-manager notifications
```

**Arguments**: None

**Behavior**:
- Queries `data/notifications.db` for pending notifications
- Groups notifications by priority level:
  - 🚨 **CRITICAL**: Daemon crashed, max retries reached, etc.
  - ⚠️  **HIGH**: Needs manual review, implementation questions
  - 📋 **NORMAL**: Progress updates, informational
- Shows newest first

**Output Format**:
```
================================================================================
Pending Notifications
================================================================================

🚨 CRITICAL:
  [ID] Title
      Message body
      Type: type | Created: timestamp

⚠️  HIGH:
  [ID] Title
      Message body
      Type: type | Created: timestamp

📋 NORMAL:
  [ID] Title
      Message body
      Type: type | Created: timestamp

Total: N pending notification(s)

Tip: Use 'project-manager respond <id> <response>' to respond
```

**Notification Types**:
- `info`: Informational message
- `warning`: Warning or concern
- `error`: Error condition
- `question`: Requires user response

**Examples**:
```bash
# List all pending notifications
project-manager notifications

# No pending notifications
✅ No pending notifications
```

**Exit Codes**:
- `0`: Success (even if no notifications)
- `1`: Database error

**Related Commands**:
- `respond` - Respond to a notification
- `status` - Check daemon status

---

### `respond`

**Purpose**: Respond to a notification from the daemon.

**Syntax**:
```bash
project-manager respond <ID> <RESPONSE>
```

**Arguments**:
- `ID` (required): Notification ID from `notifications` command
- `RESPONSE` (required): Your response message
  - Can be quoted for multi-word responses
  - Common responses: `approve`, `skip`, `reject`, `"use option 2"`

**Behavior**:
- Updates notification status to `responded`
- Records your response in database
- Daemon will check responses on next iteration
- Response is case-insensitive for common keywords (`approve`, `yes`, `no`)

**Output Format**:
```
✅ Responded to notification ID: RESPONSE

Original question: TITLE
Your response: RESPONSE
```

**Examples**:
```bash
# Simple approval
project-manager respond 5 approve

# Custom response
project-manager respond 10 "use FastAPI instead"

# Reject
project-manager respond 15 skip

# Multi-word response (quoted)
project-manager respond 20 "no, this needs manual implementation"
```

**Exit Codes**:
- `0`: Response recorded successfully
- `1`: Notification not found or not pending

**Common Responses**:

| Response | Meaning |
|----------|---------|
| `approve` / `yes` | Approve daemon's suggestion |
| `reject` / `no` | Decline daemon's suggestion |
| `skip` | Skip this priority, move to next |
| `"option N"` | Choose specific option (custom) |

**Related Commands**:
- `notifications` - List pending notifications

---

### `status`

**Purpose**: Show current daemon status (active, idle, working on).

**Syntax**:
```bash
project-manager status
```

**Status**: ⏳ **Not Implemented** (MVP Phase 1)

**Planned Behavior** (Phase 2):
- Show daemon running/stopped state
- Display current priority being implemented
- Show progress percentage
- Last activity timestamp
- Estimated completion time

**Placeholder Output** (Current):
```
================================================================================
Daemon Status
================================================================================

Status: Not implemented yet (MVP Phase 1)

Daemon status will be available in Phase 2:
  - Running/Stopped status
  - Current task
  - Progress
  - Last activity
```

**Planned Output** (Phase 2):
```
================================================================================
Daemon Status
================================================================================

🟢 Running
Current Task: PRIORITY 2.5 - New User Experience & Documentation
Progress: 60% (3/5 deliverables complete)
Last Activity: 2 minutes ago
Estimated Completion: 15 minutes

Recent Activity:
  ✅ Created docs/QUICKSTART_PROJECT_MANAGER.md (2 min ago)
  ✅ Created docs/USER_JOURNEY_PROJECT_MANAGER.md (5 min ago)
  🔄 Creating docs/PROJECT_MANAGER_FEATURES.md (in progress)

Next Up: PRIORITY 2.6 - Testing Infrastructure
```

**Exit Codes**:
- `0`: Success
- `1`: Cannot connect to daemon

---

### `sync`

**Purpose**: Sync ROADMAP.md changes with daemon environment.

**Syntax**:
```bash
project-manager sync
```

**Status**: ⏳ **Not Implemented** (MVP Phase 1)

**Planned Behavior** (Phase 2):
- Copy local ROADMAP.md to daemon environment
- Sync notification database
- Verify consistency between local and daemon
- Trigger daemon to reload configuration

**Placeholder Output** (Current):
```
================================================================================
Sync with Daemon Environment
================================================================================

Sync: Not implemented yet (MVP Phase 1)

Sync functionality will be available in Phase 2:
  - Copy ROADMAP.md to daemon environment
  - Sync database changes
  - Verify consistency
```

**Planned Output** (Phase 2):
```
================================================================================
Sync with Daemon Environment
================================================================================

Syncing ROADMAP.md...
  ✅ Copied to daemon environment
  ✅ Daemon reloaded configuration

Syncing notification database...
  ✅ 3 new notifications received
  ✅ 1 response sent to daemon

Verification:
  ✅ Roadmap version matches
  ✅ Database schema matches
  ✅ Daemon acknowledged sync

Sync complete!
```

**Use Cases**:
- After editing ROADMAP.md manually
- After daemon crash/restart
- When daemon environment is out of sync

**Exit Codes**:
- `0`: Sync successful
- `1`: Sync failed (files/database mismatch)

---

## Global Options

**Get Help**:
```bash
project-manager --help              # Show all commands
project-manager view --help         # Command-specific help
project-manager -h                  # Short form
```

**Version**:
```bash
# Not yet implemented (Phase 2)
project-manager --version
project-manager -v
```

**Verbose Output**:
```bash
# Not yet implemented (Phase 2)
project-manager --verbose view
project-manager -vvv notifications  # Very verbose
```

**Custom Roadmap Path**:
```bash
# Not yet implemented (Phase 2)
project-manager --roadmap=/custom/ROADMAP.md view
```

---

## Exit Codes

All commands follow standard Unix exit code conventions:

| Code | Meaning | Example |
|------|---------|---------|
| `0` | Success | Command completed successfully |
| `1` | General error | File not found, invalid argument |
| `2` | Misuse of command | Missing required argument |
| `130` | Interrupted (Ctrl+C) | User cancelled operation |

**Checking Exit Codes**:
```bash
# In shell scripts
if project-manager notifications; then
    echo "Notifications retrieved successfully"
else
    echo "Error getting notifications" >&2
    exit 1
fi

# Get last exit code
project-manager view
echo $?  # 0 = success, non-zero = error
```

---

## Configuration

### Environment Variables

**ROADMAP_PATH**: Custom roadmap location
```bash
export ROADMAP_PATH=/path/to/custom/ROADMAP.md
project-manager view
```

**ANTHROPIC_API_KEY**: Required for daemon
```bash
# Recommended: Set in .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env

# Or export in shell
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Configuration Files

**config.py** (`coffee_maker/config.py`):
```python
# Default roadmap path
ROADMAP_PATH = Path("docs/ROADMAP.md")

# Database location
DB_PATH = Path("data/notifications.db")

# Customizable in future versions
```

**.env** (Project root):
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C123456

# Optional: Custom paths
ROADMAP_PATH=/custom/path/ROADMAP.md
```

---

## Database Schema

**Notifications Database** (`data/notifications.db`):

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,              -- 'info', 'warning', 'error', 'question'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    priority INTEGER DEFAULT 2,       -- 1=critical, 2=high, 3=normal
    status TEXT DEFAULT 'pending',    -- 'pending', 'responded', 'resolved'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    user_response TEXT,
    context TEXT                      -- JSON metadata
);

CREATE INDEX idx_status_priority ON notifications(status, priority);
CREATE INDEX idx_created_at ON notifications(created_at);
```

**Direct Database Access** (Advanced):
```bash
# View database
sqlite3 data/notifications.db "SELECT * FROM notifications;"

# Count pending
sqlite3 data/notifications.db "SELECT COUNT(*) FROM notifications WHERE status='pending';"

# Clear old notifications (90 days)
sqlite3 data/notifications.db "DELETE FROM notifications WHERE created_at < datetime('now', '-90 days');"
```

---

## Use Cases & Examples

### Use Case 1: Daily Stand-Up

**Goal**: Quick status check before starting work

```bash
#!/bin/bash
# daily_standup.sh

echo "📊 Daily Stand-Up Report"
echo "========================"

# 1. Show recent activity
echo "\n🔄 Recent Activity:"
git log --since="24 hours ago" --oneline | head -5

# 2. Check notifications
echo "\n🔔 Pending Notifications:"
project-manager notifications | grep -E "CRITICAL|HIGH" || echo "None"

# 3. Current priority
echo "\n🎯 Current Priority:"
project-manager view | grep "🔄 In Progress" || echo "None"

echo "\n✅ Stand-up complete!"
```

### Use Case 2: Auto-Respond Script

**Goal**: Automatically approve documentation tasks

```bash
#!/bin/bash
# auto_approve_docs.sh

# Get all pending HIGH notifications about documentation
project-manager notifications | grep "HIGH" | while IFS= read -r line; do
    # Extract ID
    id=$(echo "$line" | grep -oP '\[\K[0-9]+(?=\])')

    # Auto-approve if it's about documentation
    if echo "$line" | grep -qi "documentation\|docs\|guide"; then
        echo "Auto-approving documentation task: $id"
        project-manager respond "$id" "approve"
    fi
done
```

### Use Case 3: CI/CD Integration

**Goal**: Check for high-priority notifications in CI

```yaml
# .github/workflows/check-notifications.yml
name: Check Daemon Notifications

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Check for CRITICAL notifications
        run: |
          # Fail if any CRITICAL notifications
          if poetry run project-manager notifications | grep -q "CRITICAL"; then
            echo "::error::Critical notifications found"
            poetry run project-manager notifications
            exit 1
          fi
```

### Use Case 4: Slack Bot Integration

**Goal**: Forward notifications to Slack

```python
# slack_notifier.py
from coffee_maker.cli.notifications import NotificationDB
import requests
import time

def send_to_slack(notification):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

    color = {
        1: "danger",   # Critical
        2: "warning",  # High
        3: "good"      # Normal
    }.get(notification['priority'], "good")

    payload = {
        "attachments": [{
            "color": color,
            "title": notification['title'],
            "text": notification['message'],
            "footer": f"Project Manager | ID: {notification['id']}",
            "ts": notification['created_at']
        }]
    }

    requests.post(webhook_url, json=payload)

# Poll for new notifications
db = NotificationDB()
last_id = 0

while True:
    notifications = db.get_pending_notifications()
    for notif in notifications:
        if notif['id'] > last_id:
            send_to_slack(notif)
            last_id = notif['id']

    time.sleep(60)  # Check every minute
```

---

## Future Features (Phase 2)

See [ROADMAP.md](../ROADMAP.md) lines 5044-5330 for complete Phase 2 specification.

**Planned Features:**
- 🎨 **Rich Terminal UI** - Colors, progress bars, interactive tables
- 💬 **Interactive Chat Mode** - `project-manager chat` with Claude AI
- ✏️  **Roadmap Editing** - Add/edit priorities from CLI
- 📊 **Analytics** - Velocity tracking, time estimates
- 🔌 **Plugin System** - Custom commands and integrations
- 🔄 **Real-time Updates** - Live daemon status streaming
- 📱 **Slack Integration** - Native Slack notifications
- 🌐 **Web Dashboard** - Browser-based roadmap view

---

## Troubleshooting

### Command Not Found

**Problem**: `bash: project-manager: command not found`

**Solutions**:
```bash
# 1. Activate poetry shell
poetry shell

# 2. Verify installation
poetry show coffee-maker

# 3. Reinstall
poetry install

# 4. Use via poetry run
poetry run project-manager view
```

### Database Locked

**Problem**: `database is locked`

**Solutions**:
```bash
# 1. Stop daemon
pkill -f run_daemon.py

# 2. Wait for database to unlock (auto-recovers)

# 3. If stuck, remove write-ahead log
rm data/notifications.db-wal
```

### ROADMAP Not Found

**Problem**: `❌ ROADMAP not found: docs/ROADMAP.md`

**Solutions**:
```bash
# 1. Check current directory
pwd

# 2. Change to project root
cd /path/to/MonolithicCoffeeMakerAgent

# 3. Verify file exists
ls docs/ROADMAP.md

# 4. Set custom path (future)
export ROADMAP_PATH=/custom/path/ROADMAP.md
```

---

## Getting Help

- **Documentation**: See `docs/` folder
- **Quick Start**: [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md)
- **User Journey**: [USER_JOURNEY_PROJECT_MANAGER.md](USER_JOURNEY_PROJECT_MANAGER.md)
- **Issues**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- **Discussions**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions

---

**Last Updated**: 2025-10-09
**Version**: MVP Phase 1
**Status**: ✅ Current Features Documented
