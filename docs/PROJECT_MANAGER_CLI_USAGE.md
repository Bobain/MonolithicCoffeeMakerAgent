# Project Manager CLI - Usage Guide

The **project-manager** CLI is the primary interface for interacting with the Coffee Maker Agent's autonomous development system. Use it to view your roadmap, communicate with the daemon, and manage notifications.

## 🎯 Overview

```
User → project-manager CLI → NotificationDB → DevDaemon → Implementation
         ↓
     ROADMAP.md
```

**What it does**:
- View project roadmap (full or specific priorities)
- List pending notifications from the daemon
- Respond to daemon questions (approve/decline)
- Monitor daemon status (coming in Phase 2)
- Sync roadmap with daemon environment (coming in Phase 2)

**MVP Phase 1** (Current):
- ✅ View roadmap (read-only)
- ✅ List notifications grouped by priority
- ✅ Respond to notifications
- ⏳ Daemon status (placeholder)
- ⏳ Sync (placeholder)

**Phase 2** (Future):
- Claude AI integration for interactive roadmap chat
- Rich terminal UI with colors and formatting
- Roadmap editing capabilities
- Slack integration for notifications

## 🚀 Quick Start

### 1. Installation

The CLI is installed automatically with the Coffee Maker Agent:

```bash
poetry install
```

The `project-manager` command is available via Poetry's scripts.

### 2. Basic Commands

**View full roadmap**:
```bash
project-manager view
```

**View specific priority**:
```bash
project-manager view 2
project-manager view PRIORITY-3
```

**Check notifications**:
```bash
project-manager notifications
```

**Respond to notification**:
```bash
project-manager respond 5 approve
project-manager respond 10 "no, use option 2"
```

**Check daemon status**:
```bash
project-manager status
```

### 3. Typical Workflow

While the daemon runs in one terminal:

**Terminal 1** (Daemon):
```bash
python run_daemon.py
```

**Terminal 2** (You):
```bash
# Check for new notifications
project-manager notifications

# View details of a priority
project-manager view PRIORITY-4

# Approve daemon's proposed implementation
project-manager respond 12 approve

# Watch for updates
watch -n 5 project-manager notifications
```

---

## 📖 Command Reference

### `project-manager view`

View the project roadmap.

**Usage**:
```bash
project-manager view [PRIORITY]
```

**Arguments**:
- `PRIORITY` (optional): Specific priority to view
  - Can be number: `1`, `2`, `3`
  - Or full name: `PRIORITY-1`, `PRIORITY-3`

**Examples**:

**View full roadmap** (first 100 lines):
```bash
project-manager view
```

Output:
```
================================================================================
Coffee Maker Agent - ROADMAP
================================================================================

# Coffee Maker Agent - Project Roadmap

**Current Status**: PRIORITY 2 (85%) & PRIORITY 3 (90%)
**Branch**: feature/priority-1.5
...
... (95 more lines)

Tip: Use 'project-manager view <priority>' to see specific priority
```

**View specific priority**:
```bash
project-manager view 2
```

Output:
```
================================================================================
Coffee Maker Agent - ROADMAP
================================================================================

### 🔴 **PRIORITY 2: Roadmap Management CLI** ⚡ MVP ⚡ NEW 🎯 85% COMPLETE

**Status**: 🔄 In Progress
**Target**: MVP Phase 1 (Basic CLI with text output)
**Deliverables**:
- ✅ NotificationDB (SQLite + WAL mode)
- ✅ CLI commands (view, notifications, respond, status, sync)
- ✅ Unit tests (24 tests)
- ⏳ Documentation (final step for MVP Phase 1)
...
```

**View by full name**:
```bash
project-manager view PRIORITY-1.5
```

---

### `project-manager notifications`

List all pending notifications from the daemon.

**Usage**:
```bash
project-manager notifications
```

**Output Format**:

Notifications are grouped by priority:

```
================================================================================
Pending Notifications
================================================================================

🚨 CRITICAL:
  [3] Security vulnerability detected
      CVE-2024-1234 found in dependency X
      Type: INFO | Created: 2025-10-09 14:30:00

⚠️  HIGH:
  [5] Implement PRIORITY 4?
      The daemon wants to implement:
      Streamlit Analytics Dashboard

      Approve?
      Type: QUESTION | Created: 2025-10-09 14:35:00

📋 NORMAL:
  [7] Tests completed successfully
      All 159 tests passing
      Type: INFO | Created: 2025-10-09 14:40:00

Total: 3 pending notification(s)

Tip: Use 'project-manager respond <id> <response>' to respond
```

**No notifications**:
```bash
$ project-manager notifications
```

Output:
```
================================================================================
Pending Notifications
================================================================================

✅ No pending notifications
```

---

### `project-manager respond`

Respond to a pending notification.

**Usage**:
```bash
project-manager respond <ID> <RESPONSE>
```

**Arguments**:
- `ID`: Notification ID (number shown in brackets)
- `RESPONSE`: Your response text
  - Common responses: `approve`, `decline`, `skip`, `yes`, `no`
  - Can be any text: `"use option 2 instead"`

**Examples**:

**Approve a task**:
```bash
project-manager respond 5 approve
```

Output:
```
✅ Responded to notification 5: approve

Original question: Implement PRIORITY 4?
Your response: approve
```

**Decline with reason**:
```bash
project-manager respond 10 "no, implement PRIORITY 5 first"
```

**Quick approve**:
```bash
project-manager respond 12 yes
```

**Error Cases**:

**Notification not found**:
```bash
$ project-manager respond 999 approve
```

Output:
```
❌ Notification 999 not found
```

**Notification already responded to**:
```bash
$ project-manager respond 5 approve
```

Output:
```
⚠️  Notification 5 is not pending (status: completed)
```

---

### `project-manager status`

Show daemon status.

**Usage**:
```bash
project-manager status
```

**Current Output** (MVP Phase 1):
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

**Future Output** (Phase 2):
```
================================================================================
Daemon Status
================================================================================

Status: 🟢 Running
Current Task: Implementing PRIORITY 4 (Streamlit Dashboard)
Progress: 45% (2/4 deliverables complete)
Last Activity: 2 minutes ago

Recent Actions:
  ✅ Created feature branch: feature/priority-4
  ✅ Implemented dashboard layout
  🔄 Adding analytics charts...
  ⏳ Tests pending

Uptime: 3 hours 24 minutes
Total Implementations: 3 (all successful)
```

---

### `project-manager sync`

Sync roadmap with daemon environment.

**Usage**:
```bash
project-manager sync
```

**Current Output** (MVP Phase 1):
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

**Future Behavior** (Phase 2):
- Ensures daemon has latest ROADMAP.md
- Syncs notification database between processes
- Validates data consistency
- Resolves conflicts if any

---

## 🔄 Workflow Examples

### Basic Daemon Interaction

**Scenario**: Daemon asks to implement PRIORITY 4

**Terminal 1** (Daemon):
```bash
$ python run_daemon.py

[INFO] DevDaemon started
[INFO] Found planned priority: PRIORITY 4 (Streamlit Dashboard)
[INFO] Created notification 15 - waiting for response
[INFO] Check notifications with: project-manager notifications
[INFO] Approve with: project-manager respond 15 approve
```

**Terminal 2** (You):
```bash
# 1. Check notification
$ project-manager notifications

⚠️  HIGH:
  [15] Implement PRIORITY 4?
       The daemon wants to implement:
       Streamlit Analytics Dashboard

       Approve?

# 2. Review priority details
$ project-manager view PRIORITY-4

### 🔴 **PRIORITY 4: Streamlit Analytics Dashboard**
...
**Deliverables**:
- Interactive dashboard with usage metrics
- Real-time charts and graphs
- Export functionality
...

# 3. Approve
$ project-manager respond 15 approve

✅ Responded to notification 15: approve
```

**Terminal 1** (Daemon continues):
```bash
[INFO] User approved - starting implementation
[INFO] Creating branch: feature/priority-4
[INFO] Executing Claude CLI...
[INFO] Implementation complete
[INFO] PR created: https://github.com/user/repo/pull/123
```

---

### Monitoring Long-Running Tasks

**Use `watch` to auto-refresh**:

```bash
# Check notifications every 5 seconds
watch -n 5 project-manager notifications
```

Output (auto-refreshes):
```
Every 5.0s: project-manager notifications

================================================================================
Pending Notifications
================================================================================

⚠️  HIGH:
  [20] Implementation progress update
       PRIORITY 4: 60% complete (3/5 deliverables done)
       Type: INFO | Created: 2025-10-09 15:10:23
```

---

### Viewing Multiple Priorities

**Check next 3 priorities**:

```bash
for i in 4 5 6; do
  echo "=== PRIORITY $i ==="
  project-manager view $i | head -20
  echo
done
```

---

### Responding to Multiple Notifications

**Approve all pending**:

```bash
# List all pending notification IDs
project-manager notifications | grep '^\[' | sed 's/\[//;s/\].*//' | while read id; do
  project-manager respond $id approve
done
```

⚠️ **Caution**: Only use this if you've reviewed all notifications!

---

## ⚙️ Configuration

### Database Location

The CLI uses the shared notification database at:

```
{DATA_DIR}/notifications.db
```

Where `DATA_DIR` defaults to:
- `data/` in the project root

Configure via environment variable:
```bash
export DATA_DIR=/custom/path/to/data
project-manager notifications
```

### Roadmap Location

The CLI reads the roadmap from:

```
docs/ROADMAP.md
```

This is hardcoded in `coffee_maker/config.py` as `ROADMAP_PATH`.

To use a different roadmap (advanced):
```python
# In coffee_maker/config.py
ROADMAP_PATH = Path("/custom/path/to/roadmap.md")
```

---

## 📊 Notification System

### Notification Types

| Type | Icon | Description | Requires Response |
|------|------|-------------|-------------------|
| `INFO` | 📋 | Informational message | No |
| `QUESTION` | ❓ | Requires user decision | Yes |
| `WARNING` | ⚠️ | Non-critical issue | No |
| `ERROR` | ❌ | Critical error | No |

### Priority Levels

| Priority | Icon | Description | Response Time |
|----------|------|-------------|---------------|
| `CRITICAL` | 🚨 | Urgent, needs immediate attention | < 5 minutes |
| `HIGH` | ⚠️ | Important, respond soon | < 30 minutes |
| `NORMAL` | 📋 | Standard priority | < 1 hour |
| `LOW` | 💬 | Informational, no rush | Anytime |

### Notification Lifecycle

```
┌──────────┐
│ PENDING  │ ← Created by daemon
└────┬─────┘
     │
     ├─→ User responds → COMPLETED (with response)
     │
     ├─→ Timeout (5 min) → EXPIRED
     │
     └─→ User declines → COMPLETED (declined)
```

---

## 🐛 Troubleshooting

### "ROADMAP not found" Error

**Symptom**:
```bash
$ project-manager view
❌ ROADMAP not found: /path/to/docs/ROADMAP.md
```

**Solutions**:
1. Ensure you're in the project root directory
2. Check ROADMAP.md exists: `ls docs/ROADMAP.md`
3. Verify `ROADMAP_PATH` in `coffee_maker/config.py`

---

### "No pending notifications" (but daemon says it created one)

**Symptom**:
- Daemon says: "Created notification 15"
- CLI says: "No pending notifications"

**Causes & Solutions**:

1. **Different database files**:
   ```bash
   # Check DATA_DIR matches
   echo $DATA_DIR

   # Verify database exists
   ls -lh data/notifications.db
   ```

2. **Permission issues**:
   ```bash
   # Fix permissions
   chmod 644 data/notifications.db
   ```

3. **Database locked**:
   ```bash
   # Check for lock
   lsof data/notifications.db

   # Wait a moment and retry
   sleep 2 && project-manager notifications
   ```

---

### "Notification X not found" When Responding

**Symptom**:
```bash
$ project-manager respond 15 approve
❌ Notification 15 not found
```

**Solutions**:
1. **Check ID is correct**:
   ```bash
   project-manager notifications
   ```

2. **Notification may have expired**:
   - Questions expire after 5 minutes if unanswered
   - INFO notifications don't expire

3. **Already responded**:
   - Can only respond to PENDING notifications once

---

### Python Module Import Errors

**Symptom**:
```bash
$ project-manager view
ModuleNotFoundError: No module named 'coffee_maker'
```

**Solutions**:
1. **Install the package**:
   ```bash
   poetry install
   ```

2. **Use Poetry to run**:
   ```bash
   poetry run project-manager view
   ```

3. **Activate virtual environment**:
   ```bash
   poetry shell
   project-manager view
   ```

---

### Command Not Found

**Symptom**:
```bash
$ project-manager view
command not found: project-manager
```

**Solutions**:
1. **Ensure installed**:
   ```bash
   poetry install
   ```

2. **Check Poetry scripts**:
   ```bash
   poetry run project-manager view
   ```

3. **Add to PATH** (if using global install):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

---

## 🎯 Best Practices

### 1. Monitor Regularly

Set up automatic monitoring:

**Option A: Terminal multiplexer** (tmux/screen)
```bash
# Split screen: left=daemon, right=notifications
tmux new-session \; \
  split-window -h \; \
  send-keys 'python run_daemon.py' C-m \; \
  select-pane -t 1 \; \
  send-keys 'watch -n 5 project-manager notifications' C-m
```

**Option B: Desktop notification** (macOS)
```bash
# Add to cron: check every 5 minutes
*/5 * * * * cd /path/to/project && project-manager notifications | grep -q "pending" && osascript -e 'display notification "New daemon notifications" with title "Coffee Maker Agent"'
```

---

### 2. Respond Promptly

The daemon waits for:
- **QUESTION notifications**: 5 minutes before timing out
- **INFO notifications**: Indefinitely (no timeout)

Quick response = faster development cycle!

---

### 3. Use Specific Priority Views

Don't read the full 9,000-line roadmap every time:

```bash
# Quick priority check
project-manager view 4 | head -30

# Save to file for detailed review
project-manager view PRIORITY-5 > /tmp/priority-5.txt
vim /tmp/priority-5.txt
```

---

### 4. Meaningful Responses

When declining or suggesting changes, provide context:

❌ **Bad**:
```bash
project-manager respond 20 no
```

✅ **Good**:
```bash
project-manager respond 20 "no, implement PRIORITY 5 first - it's a dependency"
```

The daemon reads your response and may act on it!

---

### 5. Keep Notifications Clean

Regularly check and respond to notifications:

```bash
# Daily routine
project-manager notifications   # Check pending
# Respond to each...
project-manager notifications   # Verify all clear
```

Don't let them pile up - it confuses the workflow.

---

### 6. Integrate with Your Workflow

**Git aliases**:
```bash
# Add to ~/.gitconfig
[alias]
    pm-view = !project-manager view
    pm-notif = !project-manager notifications
    pm-approve = !project-manager respond
```

Usage:
```bash
git pm-notif
git pm-approve 15 approve
```

**Shell aliases**:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias pmv='project-manager view'
alias pmn='project-manager notifications'
alias pmr='project-manager respond'
```

Usage:
```bash
pmn              # List notifications
pmv PRIORITY-4   # View priority
pmr 15 approve   # Respond
```

---

## 🔮 Advanced Usage

### Scripting with project-manager

**Check if notifications exist** (for automation):

```bash
#!/bin/bash
# notify-if-pending.sh

COUNT=$(project-manager notifications 2>/dev/null | grep -c "^\[")

if [ $COUNT -gt 0 ]; then
    echo "You have $COUNT pending notification(s)!"
    project-manager notifications

    # Send desktop notification
    notify-send "Coffee Maker Agent" "$COUNT pending notifications"
fi
```

---

### Parsing Notification Output

**Extract notification IDs**:

```bash
project-manager notifications | \
  grep '^\[' | \
  sed 's/\[\([0-9]*\)\].*/\1/' | \
  while read id; do
    echo "Notification ID: $id"
  done
```

**Count by priority**:

```bash
project-manager notifications | awk '
  /CRITICAL:/ { critical++ }
  /HIGH:/ { high++ }
  /NORMAL:/ { normal++ }
  END {
    print "Critical:", critical
    print "High:", high
    print "Normal:", normal
  }
'
```

---

### Custom Notification Queries

Use the database directly for advanced queries:

```bash
# View all notifications (including completed)
sqlite3 data/notifications.db "
  SELECT id, type, title, status, created_at
  FROM notifications
  ORDER BY created_at DESC
  LIMIT 10;
"
```

```bash
# Count notifications by status
sqlite3 data/notifications.db "
  SELECT status, COUNT(*)
  FROM notifications
  GROUP BY status;
"
```

**Example output**:
```
pending|3
completed|15
expired|2
```

---

### Integration with CI/CD

**GitHub Actions workflow** to auto-respond:

```yaml
# .github/workflows/auto-approve.yml
name: Auto-Approve Low-Priority Tasks

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes

jobs:
  auto-approve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check and approve LOW priority notifications
        run: |
          # Get all LOW priority notification IDs
          poetry run project-manager notifications | \
            awk '/NORMAL:/{flag=1; next} /^$/{flag=0} flag && /^\[/ {print $1}' | \
            tr -d '[]' | \
            while read id; do
              poetry run project-manager respond $id "auto-approved (CI)"
            done
```

---

## 📚 Related Documentation

- [ROADMAP.md](ROADMAP.md) - Complete project roadmap
- [DAEMON_USAGE.md](DAEMON_USAGE.md) - Autonomous daemon guide
- [ADR_001](ADR_001_DATABASE_SYNC_STRATEGY.md) - Database sync architecture
- [PRIORITY 2 Details](ROADMAP.md#priority-2) - CLI implementation details

---

## 🤝 Getting Help

### Test the CLI

Verify your installation:

```bash
# Test view command
project-manager view | head -10

# Test notifications (should work even if empty)
project-manager notifications

# Test database connection
python -c "from coffee_maker.cli.notifications import NotificationDB; db = NotificationDB(); print('✅ Database OK')"

# Run CLI tests
pytest tests/unit/test_roadmap_cli.py -v
```

### Debug Mode

Enable verbose logging:

```python
# In coffee_maker/cli/roadmap_cli.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",
)
```

### Common Issues

1. **Database locked**: Wait a few seconds, WAL mode handles concurrent access
2. **Permission denied**: Check file permissions on `data/notifications.db`
3. **Module not found**: Run `poetry install` and use `poetry run project-manager`

### Run Integration Tests

Test the full notification workflow:

```bash
pytest tests/integration/test_daemon_integration.py::test_notification_flow -v
```

---

## 📊 Quick Reference Card

```
╔════════════════════════════════════════════════════════════════╗
║                   PROJECT-MANAGER CLI                          ║
║                     Quick Reference                            ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  VIEW ROADMAP                                                  ║
║    project-manager view              # Full roadmap           ║
║    project-manager view 2            # Specific priority      ║
║    project-manager view PRIORITY-3   # By name               ║
║                                                                ║
║  NOTIFICATIONS                                                 ║
║    project-manager notifications     # List pending           ║
║    project-manager respond 5 approve # Approve task           ║
║    project-manager respond 10 no     # Decline task           ║
║                                                                ║
║  DAEMON STATUS                                                 ║
║    project-manager status            # Check daemon           ║
║    project-manager sync              # Sync roadmap           ║
║                                                                ║
║  TIPS                                                          ║
║    - Respond to CRITICAL within 5 minutes                     ║
║    - Use watch for auto-refresh: watch -n 5 project-manager notifications ║
║    - View specific priorities instead of full roadmap         ║
║    - Provide context when declining: "no, do X first"         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🎓 Training: Your First Week

**Day 1**: Learn the basics
```bash
project-manager view              # Explore roadmap
project-manager view PRIORITY-1   # Focus on one priority
```

**Day 2**: Start monitoring
```bash
python run_daemon.py              # Terminal 1: Start daemon
project-manager notifications     # Terminal 2: Watch notifications
```

**Day 3**: First approval
```bash
project-manager notifications     # Check pending
project-manager respond <id> approve
# Watch daemon implement!
```

**Day 4**: Advanced viewing
```bash
for i in 1 2 3; do project-manager view $i | head -20; done
project-manager view PRIORITY-4 > /tmp/review.txt
```

**Day 5**: Automation
```bash
watch -n 5 project-manager notifications
alias pmn='project-manager notifications'
```

**Week 2+**: Full autonomous workflow!

---

**Ready to manage your autonomous development! 🎯**
