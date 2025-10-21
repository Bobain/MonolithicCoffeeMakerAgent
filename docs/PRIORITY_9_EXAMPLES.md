# PRIORITY 9: Communication & Daily Standup - Usage Examples

**Created**: 2025-10-18
**Status**: ✅ Complete
**Type**: Practical Usage Examples

---

## Table of Contents

1. [Basic Commands](#basic-commands)
2. [Daily Workflow](#daily-workflow)
3. [Real Output Examples](#real-output-examples)
4. [Advanced Usage](#advanced-usage)
5. [Troubleshooting Examples](#troubleshooting-examples)
6. [Integration Examples](#integration-examples)

---

## Basic Commands

### 1. Start the code_developer Daemon

```bash
# Start daemon in autonomous mode
poetry run code-developer --auto-approve

# Expected output:
# 🤖 code_developer starting in autonomous mode...
# ✅ Registered code_developer (PID: 12345)
# 📋 Loading ROADMAP from docs/roadmap/ROADMAP.md
# 🎯 Found 15 priorities (3 complete, 5 in progress, 7 planned)
# 🚀 Starting work on PRIORITY 10: Advanced Testing Framework
```

### 2. Check Developer Status (Anytime)

```bash
poetry run project-manager developer-status

# Expected output:
# 🤖 code_developer Status - Live
# ================================
#
# Current Task: Implementing PRIORITY 10
# Progress: ██████████░░░░░░░░░░ 50% (Step 3 of 6)
# Status: ✅ Active (running 2h 15m)
#
# Current Activity:
# ├─ Creating advanced test utilities
# │  ├─ ✅ Defined test framework structure
# │  ├─ ✅ Added pytest configuration
# │  ├─ 🔄 Implementing test fixtures
# │  └─ ⏳ Pending: Integration tests
#
# Recent Activities (last 30 min):
#   14:30 | Created file: tests/test_advanced.py
#   14:20 | Running tests: pytest tests/
#   14:15 | Committed: "feat: Add test framework core"
#
# Metrics Today:
#   - Tasks completed: 0
#   - Commits: 3
#   - Tests passed: 47
#   - Tests failed: 0
#
# Next Steps:
#   1. Complete fixture implementation
#   2. Write integration tests
#   3. Update documentation
#
# ETA: 2-3 hours
# Last updated: 1 minute ago
```

### 3. View Daily Standup (First Interaction of Day)

```bash
poetry run project-manager chat

# First shows daily standup automatically:
# ╭──────────────────── 📊 DAILY STANDUP ─────────────────────╮
# │                                                             │
# │  # 🤖 code_developer Daily Report - 2025-10-17             │
# │  ============================================================│
# │  [Full report shown here - see Real Output Examples below]  │
# │                                                             │
# ╰─────────────────────────────────────────────────────────────╯
#
# Then starts chat:
# 🤖 project-manager: Good morning! As you can see from the standup,
#    code_developer completed PRIORITY 9 yesterday. How can I help you today?
#
# >
```

### 4. Manual Standup Generation

```bash
# Generate standup for yesterday
poetry run project-manager standup
```

### 5. Check Notifications

```bash
poetry run project-manager notifications

# Expected output:
# 📬 Pending Notifications
# ========================
#
# ID  | Type              | Message                                  | Created
# ----+-------------------+------------------------------------------+---------
# 5   | dependency_approval| Need approval to install pytest-timeout  | 2h ago
# 7   | question          | Which testing framework should I use?     | 1h ago
#
# Use 'project-manager respond <id> <response>' to respond
```

### 6. Respond to Notifications

```bash
# Approve a request
poetry run project-manager respond 5 approve

# Expected output:
# ✅ Approved notification #5: dependency_approval
# 🤖 code_developer will continue with the approved action

# Or provide custom response
poetry run project-manager respond 7 "Use pytest with fixtures"

# Expected output:
# ✅ Responded to notification #7: question
# 💬 Your response: "Use pytest with fixtures"
# 🤖 code_developer will incorporate your feedback
```

---

## Daily Workflow

### Morning Routine (9:00 AM)

```bash
# Step 1: Open terminal and run project-manager
poetry run project-manager chat

# Automatic daily standup appears:
# ╭──────────────────── 📊 DAILY STANDUP ─────────────────────╮
# │  # 🤖 code_developer Daily Report - 2025-10-17             │
# │                                                             │
# │  ## 📊 Yesterday's Work                                    │
# │  ### ✅ PRIORITY 9                                          │
# │  - feat: Implement daily standup infrastructure            │
# │  - fix: Update status tracking                             │
# │  - docs: Add communication user guide                      │
# │    **Commits**: 5 | **Files**: 12 | **Lines**: +650/-45   │
# │                                                             │
# │  ## 📈 Overall Stats                                       │
# │  - **Total Commits**: 5                                    │
# │  - **Files Modified**: 12                                  │
# │  - **Lines Added**: +650                                   │
# │                                                             │
# │  ## 🔄 Today's Focus                                       │
# │  - PRIORITY 10: Advanced Testing Framework (30% complete)  │
# │                                                             │
# │  ## ✅ Blockers                                            │
# │  None                                                      │
# ╰─────────────────────────────────────────────────────────────╯

# Step 2: Check if any questions need answers
poetry run project-manager notifications

# Step 3: Start interactive chat if needed
# > What's the current status of PRIORITY 10?
# 🤖: code_developer is 30% through PRIORITY 10...
```

### Afternoon Check-In (2:00 PM)

```bash
# Quick status check
poetry run project-manager developer-status

# Example output:
# 🤖 code_developer Status - Live
# ================================
# Current Task: Implementing PRIORITY 10
# Progress: ███████████████░░░░░ 75% (Step 5 of 6)
# Status: ✅ Active (running 5h 45m)
#
# Recent Activities (last 30 min):
#   14:00 | Committed: "feat: Complete test fixtures"
#   13:50 | Running tests: pytest tests/ (47 passed, 0 failed)
#   13:40 | Created file: tests/integration/test_full_workflow.py
#
# ETA: 1-2 hours
```

### End of Day (5:00 PM)

```bash
# Check final status
poetry run project-manager developer-status

# Review notifications
poetry run project-manager notifications

# Approve any pending items for tomorrow
poetry run project-manager respond 12 approve
```

---

## Real Output Examples

### Example 1: Successful Day with Multiple Priorities

```markdown
# 🤖 code_developer Daily Report - 2025-10-17
============================================================

## 📊 Yesterday's Work (2025-10-17)

### ✅ PRIORITY 9

- feat: Implement DailyReportGenerator class
- feat: Add ActivityLogger integration
- feat: Create CLI commands for standup
- fix: Handle missing git commits gracefully
- docs: Write user guide and architecture docs

  **Commits**: 5
  **Files**: 12 modified
  **Lines**: +650 / -45

### ✅ PRIORITY 10

- feat: Start advanced testing framework
- feat: Add pytest configuration files
- test: Create initial test suite structure

  **Commits**: 3
  **Files**: 8 modified
  **Lines**: +320 / -10

## 📈 Overall Stats

- **Total Commits**: 8
- **Files Modified**: 20
- **Lines Added**: +970
- **Lines Removed**: -55

## 🔄 Today's Focus

- PRIORITY 10: Advanced Testing Framework
  Progress: 40%

## ✅ Blockers

None

────────────────────────────────────────────────────────────────
Report generated: 2025-10-18 09:00:15
```

### Example 2: Day with Blockers

```markdown
# 🤖 code_developer Daily Report - 2025-10-16
============================================================

## 📊 Yesterday's Work (2025-10-16)

### ✅ PRIORITY 8

- feat: Start multi-AI provider implementation
- feat: Create provider abstraction layer
- fix: Update dependency management

  **Commits**: 4
  **Files**: 10 modified
  **Lines**: +520 / -30

## 📈 Overall Stats

- **Total Commits**: 4
- **Files Modified**: 10
- **Lines Added**: +520
- **Lines Removed**: -30

## 🔄 Today's Focus

- PRIORITY 8: Multi-AI Provider Support
  Progress: 60%

## ⚠️ Blockers

- Need user approval for dependency: openai>=1.0.0
  (Notification #15, created 2 hours ago)

- Question about provider fallback strategy
  (Notification #16, created 1 hour ago)

────────────────────────────────────────────────────────────────
Report generated: 2025-10-17 09:00:22
```

### Example 3: Quiet Day (No Activity)

```markdown
# 🤖 code_developer Daily Report - 2025-10-14
============================================================

## 📊 Yesterday's Work (2025-10-14)

No activity yesterday.

## 📈 Overall Stats

- **Total Commits**: 0
- **Files Modified**: 0

## 🔄 Today's Focus

- PRIORITY 7: Documentation System
  Progress: 0% (not started)

## ✅ Blockers

None

────────────────────────────────────────────────────────────────
Report generated: 2025-10-15 09:00:05

Note: This is normal! Weekend or waiting for user input.
```

### Example 4: High Activity Day

```markdown
# 🤖 code_developer Daily Report - 2025-10-15
============================================================

## 📊 Yesterday's Work (2025-10-15)

### ✅ PRIORITY 9

- feat: Implement communication infrastructure
- feat: Add DeveloperStatus tracking
- feat: Create ActivityLogger with SQLite backend
- feat: Implement DailyReportGenerator
- feat: Add CLI commands for standup and status
- fix: Handle concurrent database access with WAL
- fix: Atomic writes for status file
- test: Add unit tests for all components
- test: Add integration tests
- docs: Create user guide
- docs: Create architecture documentation
- docs: Add usage examples

  **Commits**: 12
  **Files**: 25 modified
  **Lines**: +1,450 / -120

## 📈 Overall Stats

- **Total Commits**: 12
- **Files Modified**: 25
- **Lines Added**: +1,450
- **Lines Removed**: -120

## 🔄 Today's Focus

- PRIORITY 9: Enhanced Communication (Complete! ✅)
- Moving to PRIORITY 10: Advanced Testing Framework

## ✅ Blockers

None

────────────────────────────────────────────────────────────────
Report generated: 2025-10-16 09:00:18

🎉 Major milestone! PRIORITY 9 complete ahead of schedule!
```

---

## Advanced Usage

### Custom Date Ranges

```bash
# Last week's summary
poetry run project-manager standup --since 2025-10-11

# Specific day
poetry run project-manager standup --since 2025-10-15 --until 2025-10-15

# Last 3 days
poetry run project-manager standup --since $(date -d '3 days ago' +%Y-%m-%d)
```

### Query Activity Database Directly

```bash
# Connect to database
sqlite3 data/activity.db

# Get commit count by day
sqlite> SELECT
  ...>   date(created_at) as date,
  ...>   COUNT(*) as commits
  ...> FROM activities
  ...> WHERE activity_type = 'commit'
  ...> GROUP BY date(created_at)
  ...> ORDER BY date DESC
  ...> LIMIT 7;

# Example output:
# date         | commits
# -------------+---------
# 2025-10-17   | 5
# 2025-10-16   | 4
# 2025-10-15   | 12
# 2025-10-14   | 0
# 2025-10-13   | 3
# 2025-10-12   | 6
# 2025-10-11   | 2
```

### Export Standup to File

```bash
# Save to markdown file
poetry run project-manager standup > standup_2025-10-17.md

# Save with date in filename
poetry run project-manager standup > standup_$(date +%Y-%m-%d).md

# View later
cat standup_2025-10-17.md
```

### Monitor Developer Status in Real-Time

```bash
# Watch status every 10 seconds
watch -n 10 poetry run project-manager developer-status

# Or with a simple loop
while true; do
  clear
  poetry run project-manager developer-status
  sleep 10
done
```

---

## Troubleshooting Examples

### Problem: Daily standup not showing

```bash
# Check when last report was shown
cat data/last_interaction.json

# Example output:
# {
#   "last_check_in": "2025-10-18T09:15:30.123456",
#   "last_report_shown": "2025-10-18"
# }

# Force re-display by deleting timestamp
rm data/last_interaction.json

# Now run project-manager again
poetry run project-manager chat
# ✅ Standup will show again
```

### Problem: Developer status shows "stopped"

```bash
# Check if daemon is running
ps aux | grep code-developer

# Example output (not running):
# (no output or only grep process)

# Start daemon
poetry run code-developer --auto-approve

# Check status again
poetry run project-manager developer-status

# Example output:
# 🤖 code_developer Status - Live
# Status: ✅ Active (just started)
```

### Problem: No commits in standup

```bash
# Check git log directly
git log --since="yesterday" --oneline

# Example output (no commits):
# (empty)

# This is expected! code_developer works at its own pace
# Check developer status to see what it's working on
poetry run project-manager developer-status

# Example output:
# Current Task: Implementing PRIORITY 10
# Progress: ████░░░░░░░░░░░░░░░░ 20% (Step 1 of 6)
# Status: ✅ Active (working on tests)
```

### Problem: SQLite database locked

```bash
# Check WAL mode
sqlite3 data/activity.db "PRAGMA journal_mode;"

# Expected output:
# wal

# If not in WAL mode, fix it
sqlite3 data/activity.db "PRAGMA journal_mode=WAL;"

# Try command again
poetry run project-manager developer-status
```

### Problem: Status file corrupted

```bash
# Check if file is valid JSON
python3 -m json.tool data/developer_status.json

# If corrupted, delete it (daemon will recreate)
rm data/developer_status.json

# Restart daemon to recreate
pkill -f code-developer
poetry run code-developer --auto-approve
```

---

## Integration Examples

### Example 1: Morning Standup + Code Review Workflow

```bash
#!/bin/bash
# morning_routine.sh

echo "📊 Daily Standup"
echo "================"
poetry run project-manager chat

echo ""
echo "📬 Checking Notifications"
echo "========================="
poetry run project-manager notifications

echo ""
echo "🔍 Current Status"
echo "================="
poetry run project-manager developer-status

# If there are pending approvals, prompt user
if poetry run project-manager notifications | grep -q "pending"; then
  echo ""
  echo "⚠️  You have pending notifications. Please review and respond."
fi
```

**Usage**:
```bash
chmod +x morning_routine.sh
./morning_routine.sh
```

### Example 2: End-of-Day Summary Script

```bash
#!/bin/bash
# eod_summary.sh

# Generate today's summary
TODAY=$(date +%Y-%m-%d)
OUTPUT_FILE="summaries/standup_${TODAY}.md"

echo "📝 Generating end-of-day summary..."
poetry run project-manager standup --since $TODAY > $OUTPUT_FILE

echo "✅ Summary saved to: $OUTPUT_FILE"

# Display summary
cat $OUTPUT_FILE

# Commit summary to repo
git add $OUTPUT_FILE
git commit -m "docs: Add daily standup for $TODAY

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Example 3: Continuous Monitoring Dashboard

```bash
#!/bin/bash
# monitor_daemon.sh

while true; do
  clear
  echo "🤖 code_developer Monitoring Dashboard"
  echo "======================================"
  echo ""

  # Show status
  poetry run project-manager developer-status

  echo ""
  echo "Recent Git Activity:"
  echo "-------------------"
  git log --since="1 hour ago" --oneline | head -5

  echo ""
  echo "Notifications:"
  echo "-------------"
  poetry run project-manager notifications | head -10

  echo ""
  echo "Refreshing in 30 seconds... (Ctrl+C to exit)"
  sleep 30
done
```

### Example 4: Slack Integration (Conceptual)

```python
# slack_daily_standup.py
"""
Post daily standup to Slack channel.

Usage:
  python slack_daily_standup.py --channel #engineering
"""

import subprocess
from datetime import datetime
from slack_sdk import WebClient

def get_daily_standup():
    """Get standup report from project-manager."""
    result = subprocess.run(
        ["poetry", "run", "project-manager", "standup"],
        capture_output=True,
        text=True
    )
    return result.stdout

def post_to_slack(channel, message):
    """Post message to Slack channel."""
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    client.chat_postMessage(
        channel=channel,
        text=message,
        mrkdwn=True
    )

if __name__ == "__main__":
    standup = get_daily_standup()
    post_to_slack("#engineering", standup)
    print("✅ Standup posted to Slack!")
```

**Run daily with cron**:
```cron
# Post standup to Slack every morning at 9 AM
0 9 * * 1-5 cd /path/to/project && python slack_daily_standup.py
```

---

## Performance Examples

### Timing Commands

```bash
# Time standup generation
time poetry run project-manager standup

# Example output:
# real    0m1.245s
# user    0m0.892s
# sys     0m0.123s

# Time status check
time poetry run project-manager developer-status

# Example output:
# real    0m0.089s
# user    0m0.045s
# sys     0m0.022s
```

### Database Query Performance

```bash
# Count total activities
sqlite3 data/activity.db "SELECT COUNT(*) FROM activities;"

# Example output:
# 1247

# Get activities by type
sqlite3 data/activity.db "
  SELECT activity_type, COUNT(*) as count
  FROM activities
  GROUP BY activity_type
  ORDER BY count DESC;
"

# Example output:
# activity_type          | count
# -----------------------+-------
# commit                 | 450
# test_run               | 320
# file_changed           | 280
# status_update          | 150
# pr_created             | 25
# priority_completed     | 15
# error_encountered      | 7
```

---

## Comparison Examples

### Before PRIORITY 9 (Manual Tracking)

```bash
# Had to manually check git log
git log --since="yesterday" --oneline

# Had to manually check daemon status
ps aux | grep code-developer

# Had to manually query database
sqlite3 data/notifications.db "SELECT * FROM notifications WHERE status='pending';"

# No consolidated view
# No automatic reporting
# No metrics tracking
```

### After PRIORITY 9 (Automated Communication)

```bash
# Single command shows everything
poetry run project-manager chat

# Automatic daily standup
# Current status
# Pending notifications
# All metrics in one place
# Professional markdown formatting
# No manual work required!
```

---

## FAQ with Examples

**Q: How do I see last week's work?**

```bash
# Method 1: Multiple daily standups
for i in {7..1}; do
  date=$(date -d "$i days ago" +%Y-%m-%d)
  echo "=== $date ==="
  poetry run project-manager standup --since $date --until $date
  echo ""
done

# Method 2: Week range
poetry run project-manager standup --since $(date -d '7 days ago' +%Y-%m-%d)
```

**Q: How do I track multiple developers?**

```bash
# Currently: One daemon per machine
# Each developer has their own data/ directory

# Future: Multi-developer support coming in PRIORITY 11
```

**Q: Can I customize the standup format?**

```bash
# Currently: Fixed markdown format
# Future: Templates coming in Phase 2

# Workaround: Post-process with custom script
poetry run project-manager standup | python customize_format.py
```

**Q: How do I backup my activity data?**

```bash
# Backup all data files
tar -czf backup_$(date +%Y-%m-%d).tar.gz data/

# Backup just activity database
cp data/activity.db backups/activity_$(date +%Y-%m-%d).db

# Restore from backup
tar -xzf backup_2025-10-17.tar.gz
```

---

## Next Steps

**Explore More**:
- Read [User Guide](PRIORITY_9_USER_GUIDE.md) for full documentation
- Read [Architecture](PRIORITY_9_ARCHITECTURE.md) for technical details
- Check [ROADMAP.md](roadmap/ROADMAP.md) for upcoming features

**Get Help**:
- Ask in chat: `poetry run project-manager chat`
- Check issues: GitHub repository
- Review code: `coffee_maker/autonomous/` and `coffee_maker/cli/`

---

**Last Updated**: 2025-10-18
**Version**: 1.0.0
**Status**: Production Ready ✅
