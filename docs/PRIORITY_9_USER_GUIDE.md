# PRIORITY 9: Enhanced code_developer Communication & Daily Standup - User Guide

**Status**: ✅ Complete
**Impact**: ⭐⭐⭐⭐⭐ Critical for trust and visibility
**Documentation Created**: 2025-10-18

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Daily Standup Reports](#daily-standup-reports)
4. [Developer Status](#developer-status)
5. [Command Reference](#command-reference)
6. [Architecture](#architecture)
7. [Data Sources](#data-sources)
8. [Troubleshooting](#troubleshooting)

---

## Overview

PRIORITY 9 makes `code_developer` communicate like a **real team member** with daily status updates. Instead of working silently in the background, the AI developer now provides:

- **📊 Daily Standup Reports** - Automatic morning summaries of yesterday's work
- **🔄 Real-Time Status** - Current task, progress, and next steps
- **⚠️ Proactive Notifications** - Blockers, questions, and milestones
- **📈 Metrics Tracking** - Commits, tests, files changed, and more

### Key Benefits

1. **Trust Building** - See what the AI accomplished each day
2. **Progress Tracking** - Daily summaries help track momentum
3. **Team Integration** - Professional standups like a human developer
4. **Accountability** - Clear record of work accomplished
5. **Context Awareness** - Always know where the project stands

---

## Quick Start

### 1. Start the Daemon

```bash
# Start code_developer in autonomous mode
poetry run code-developer --auto-approve
```

The daemon will:
- Pick priorities from ROADMAP.md
- Implement features autonomously
- Track all activities in the database
- Update status in real-time

### 2. Check Daily Standup (First Interaction of the Day)

```bash
# Start project-manager chat or any command
poetry run project-manager chat
```

**On your first interaction each day**, you'll automatically see:

```
╭──────────────────── 📊 DAILY STANDUP ─────────────────────╮
│                                                             │
│  # 🤖 code_developer Daily Report - 2025-10-17             │
│  ============================================================│
│                                                             │
│  ## 📊 Yesterday's Work (2025-10-17)                       │
│                                                             │
│  ### ✅ PRIORITY 9                                          │
│                                                             │
│  - feat: Implement daily standup infrastructure            │
│  - fix: Update status tracking for activities              │
│  - docs: Add user guide for communication features         │
│                                                             │
│    **Commits**: 3                                          │
│    **Files**: 8 modified                                   │
│    **Lines**: +450 / -25                                   │
│                                                             │
│  ## 📈 Overall Stats                                       │
│                                                             │
│  - **Total Commits**: 3                                    │
│  - **Files Modified**: 8                                   │
│  - **Lines Added**: +450                                   │
│  - **Lines Removed**: -25                                  │
│                                                             │
│  ## 🔄 Today's Focus                                       │
│                                                             │
│  - PRIORITY 10: Advanced Testing Framework                 │
│    Progress: 30%                                           │
│                                                             │
│  ## ✅ Blockers                                            │
│                                                             │
│  None                                                      │
│                                                             │
│  ────────────────────────────────────────────────────────  │
│  Report generated: 2025-10-18 09:15:30                     │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### 3. Check Developer Status Anytime

```bash
# View current developer status
poetry run project-manager developer-status
```

**Output Example**:

```
🤖 code_developer Status - Live
================================

Current Task: Implementing PRIORITY 10
Progress: ████████░░░░░░░░░░░░ 30% (Step 2 of 6)
Status: ✅ Active (running 1h 25m)

Recent Activities (last 30 min):
  10:15 | Created file: tests/test_advanced_framework.py
  10:05 | Running tests: pytest tests/
  10:00 | Committed: "feat: Add testing framework core"

Metrics Today:
  - Tasks completed: 0
  - Commits: 1
  - Tests passed: 15
  - Tests failed: 0

Last updated: 2 minutes ago
```

---

## Daily Standup Reports

### Automatic Display

Daily standup reports are shown **automatically** on your **first interaction of each new day**. This happens when you:

- Run `poetry run project-manager chat`
- Run any `project-manager` command after midnight
- First interaction >12 hours after last report

### Manual Display

You can also generate a report manually:

```bash
# Generate standup for yesterday
poetry run project-manager standup

# Generate standup for a specific date range
poetry run project-manager standup --since 2025-10-15 --until 2025-10-17
```

### Report Contents

Each daily standup includes:

1. **📊 Yesterday's Work**
   - Commits grouped by priority
   - File changes per priority
   - Lines added/removed

2. **📈 Overall Stats**
   - Total commits
   - Files modified
   - Code changes summary

3. **🔄 Today's Focus**
   - Current task
   - Progress percentage
   - Expected completion time

4. **⚠️ Blockers**
   - Questions awaiting user response
   - Issues blocking progress
   - Dependencies needed

### Data Tracking

Standup reports are generated from:

- **Git commits** - All work is tracked via git log
- **developer_status.json** - Current task and metrics
- **activity.db** - Activity logging database
- **notifications.db** - Blockers and questions

**No manual logging required!** Just work normally and the daemon tracks everything.

---

## Developer Status

### Real-Time Status Tracking

The `code_developer` daemon continuously updates its status in `data/developer_status.json`. You can query it anytime:

```bash
poetry run project-manager developer-status
```

### Status States

The developer can be in one of these states:

| State | Icon | Description |
|-------|------|-------------|
| `working` | 🟢 | Actively implementing code |
| `testing` | 🟡 | Running tests |
| `blocked` | 🔴 | Waiting for user response |
| `idle` | ⚪ | Between tasks |
| `thinking` | 🔵 | Analyzing codebase |
| `reviewing` | 🟣 | Creating PR/docs |
| `stopped` | ⚫ | Daemon not running |

### Metrics Tracked

Daily metrics include:

- **Tasks completed today** - Number of priorities finished
- **Total commits today** - Git commits made
- **Tests passed today** - Successful test runs
- **Tests failed today** - Failed test runs
- **Files created** - New files added
- **Files modified** - Existing files changed

### Activity Log

The last 20 activities are shown in the status output:

```json
{
  "timestamp": "2025-10-18T10:15:30Z",
  "type": "file_created",
  "description": "Created tests/test_advanced_framework.py"
}
```

Activity types:
- `file_created`, `file_modified`, `file_deleted`
- `git_commit`, `git_push`, `git_branch`
- `test_run`, `test_passed`, `test_failed`
- `question_asked`, `dependency_requested`
- `error_encountered`, `status_update`

---

## Command Reference

### Main Commands

#### `project-manager chat`

Start interactive AI chat with project_manager. Shows daily standup on first interaction of the day.

```bash
poetry run project-manager chat
```

**Use cases**:
- Ask about project status
- Get ROADMAP updates
- Delegate to specialized agents
- See daily standup automatically

#### `project-manager developer-status`

Show current code_developer status, progress, and recent activities.

```bash
poetry run project-manager developer-status
```

**Output includes**:
- Current task and progress
- Recent activities (last 30 min)
- Today's metrics
- Next steps
- ETA for current task

#### `project-manager standup`

Generate daily standup report for yesterday's work.

```bash
# Yesterday's standup
poetry run project-manager standup

# Custom date range
poetry run project-manager standup --since 2025-10-15

# Specific day
poetry run project-manager standup --since 2025-10-17 --until 2025-10-17
```

#### `project-manager notifications`

View pending notifications from code_developer (blockers, questions, approvals).

```bash
poetry run project-manager notifications
```

#### `project-manager respond`

Respond to code_developer questions or approve requests.

```bash
# Approve a notification
poetry run project-manager respond 5 approve

# Provide custom response
poetry run project-manager respond 10 "Use approach 2 with error handling"
```

### Status File Locations

All status data is stored in the `data/` directory:

```
data/
├── developer_status.json      # Real-time status
├── activity.db                # Activity logging database
├── notifications.db           # Notifications and blockers
└── last_interaction.json      # Last report timestamp
```

---

## Architecture

### Communication System Design

```
┌─────────────────────────────────────────────────────────┐
│  code_developer Daemon (Autonomous)                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 1. Work on priorities                             │  │
│  │ 2. Log activities (commits, tests, files)         │  │
│  │ 3. Update developer_status.json                   │  │
│  │ 4. Track metrics in activity.db                   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           │ Writes to
                           ↓
┌─────────────────────────────────────────────────────────┐
│  Data Layer                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ developer_   │ │ activity.db  │ │notifications │    │
│  │ status.json  │ │              │ │     .db      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
└─────────────────────────────────────────────────────────┘
                           │
                           │ Reads from
                           ↓
┌─────────────────────────────────────────────────────────┐
│  project_manager CLI (User Interface)                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Daily Report Generator                            │  │
│  │ - Collects git commits                            │  │
│  │ - Reads developer_status.json                     │  │
│  │ - Queries activity.db                             │  │
│  │ - Formats as markdown                             │  │
│  │ - Displays with rich.Console                      │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Developer Status Display                          │  │
│  │ - Reads developer_status.json                     │  │
│  │ - Shows current task, progress, metrics           │  │
│  │ - Displays recent activities                      │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           │ Shows to
                           ↓
┌─────────────────────────────────────────────────────────┐
│  User (You!)                                             │
│  - Sees daily standup automatically                      │
│  - Checks status anytime                                 │
│  - Stays informed of progress                            │
└─────────────────────────────────────────────────────────┘
```

### Key Components

1. **DeveloperStatus** (`coffee_maker/autonomous/developer_status.py`)
   - Tracks real-time daemon state
   - Updates `data/developer_status.json`
   - Logs activities (last 50)
   - Calculates ETA for tasks

2. **ActivityLogger** (`coffee_maker/autonomous/activity_logger.py`)
   - High-level activity logging interface
   - Writes to `activity.db`
   - Tracks commits, tests, PRs, errors
   - Session management per priority

3. **ActivityDB** (`coffee_maker/autonomous/activity_db.py`)
   - SQLite database for activities
   - Indexes for fast queries
   - WAL mode for concurrent access
   - Retention: unlimited (all history)

4. **DailyReportGenerator** (`coffee_maker/cli/daily_report_generator.py`)
   - Generates markdown standup reports
   - Reads git log, status file, database
   - Groups commits by priority
   - Calculates statistics

5. **StandupGenerator** (`coffee_maker/autonomous/standup_generator.py`)
   - AI-powered standup generation (optional)
   - Uses Claude API for narrative summaries
   - Caches summaries for performance
   - Fallback to template-based reports

### Data Flow

```
┌──────────────┐
│ code_developer│
│    daemon    │
└──────────────┘
       │
       │ 1. Commits code
       ├──────────────────────────────────────┐
       │                                       │
       ↓                                       ↓
┌──────────────┐                        ┌──────────────┐
│  Git log     │                        │developer_    │
│              │                        │status.json   │
└──────────────┘                        └──────────────┘
       │                                       │
       │                                       │
       │ 2. Logs activities                    │
       │                                       │
       ↓                                       ↓
┌──────────────┐                        ┌──────────────┐
│ activity.db  │                        │ Real-time    │
│              │                        │ metrics      │
└──────────────┘                        └──────────────┘
       │                                       │
       └───────────────┬───────────────────────┘
                       │
                       │ 3. User runs command
                       │
                       ↓
              ┌──────────────┐
              │Daily Report  │
              │  Generator   │
              └──────────────┘
                       │
                       │ 4. Formats markdown
                       │
                       ↓
              ┌──────────────┐
              │  Rich Panel  │
              │  (Terminal)  │
              └──────────────┘
```

---

## Data Sources

PRIORITY 9 uses **existing infrastructure** - no new complex systems needed!

### 1. Git Commits

**Source**: Git repository
**Access**: `git log` command
**Data tracked**:
- Commit hash
- Author
- Date/time
- Message
- Files changed
- Lines added/removed

**Example**:
```bash
git log --since="2025-10-17" --pretty=format:"%H|%an|%ai|%s" --numstat
```

### 2. Developer Status File

**Source**: `data/developer_status.json`
**Updated by**: DeveloperStatus class
**Contents**:
```json
{
  "status": "working",
  "current_task": {
    "priority": 10,
    "name": "Advanced Testing Framework",
    "started_at": "2025-10-18T09:00:00Z",
    "progress": 30,
    "current_step": "Implementing core test utilities",
    "eta_seconds": 7200
  },
  "last_activity": {
    "timestamp": "2025-10-18T10:15:30Z",
    "type": "git_commit",
    "description": "feat: Add testing framework core"
  },
  "activity_log": [...],
  "questions": [],
  "metrics": {
    "tasks_completed_today": 0,
    "total_commits_today": 1,
    "tests_passed_today": 15,
    "tests_failed_today": 0
  },
  "daemon_info": {
    "pid": 12345,
    "started_at": "2025-10-18T08:00:00Z",
    "version": "1.0.0"
  }
}
```

### 3. Activity Database

**Source**: `data/activity.db` (SQLite)
**Schema**: Activities table with indexes
**Activity types**:
- Commits
- File changes
- Test runs
- PRs created
- Branches created
- Priority started/completed
- Errors encountered
- Dependencies installed
- Documentation updated

**Example query**:
```sql
SELECT * FROM activities
WHERE date(created_at) = '2025-10-17'
  AND activity_type = 'commit'
ORDER BY created_at DESC;
```

### 4. Notifications Database

**Source**: `data/notifications.db`
**Used for**: Blockers and questions
**Example notification**:
```json
{
  "id": 5,
  "type": "dependency_approval",
  "message": "Need approval to install pytest-timeout",
  "status": "pending",
  "created_at": "2025-10-18T09:30:00Z"
}
```

---

## Troubleshooting

### Issue: Daily standup not showing

**Cause**: Report already shown today
**Solution**: Delete `data/last_interaction.json` to force re-display

```bash
rm data/last_interaction.json
poetry run project-manager chat
```

### Issue: Developer status shows "stopped"

**Cause**: Daemon not running
**Solution**: Start the daemon

```bash
poetry run code-developer --auto-approve
```

### Issue: No commits in standup report

**Cause**: No commits made yesterday
**Solution**: This is expected! Work happens at the daemon's pace

### Issue: Activity database locked

**Cause**: Concurrent access issue
**Solution**: WAL mode should handle this automatically. If persistent:

```bash
# Check for stale locks
cd data/
sqlite3 activity.db "PRAGMA journal_mode=WAL"
```

### Issue: Status file not updating

**Cause**: Daemon crashed or permissions issue
**Solution**:

```bash
# Check daemon is running
ps aux | grep code-developer

# Check file permissions
ls -la data/developer_status.json

# Restart daemon
pkill -f code-developer
poetry run code-developer --auto-approve
```

### Issue: Want to see older standups

**Cause**: Only yesterday's standup shown by default
**Solution**: Use date range flags

```bash
# Last week
poetry run project-manager standup --since 2025-10-11

# Specific day
poetry run project-manager standup --since 2025-10-15 --until 2025-10-15
```

---

## Advanced Usage

### Integration with Workflows

#### Morning Routine

```bash
# 1. Check daily standup
poetry run project-manager chat

# 2. Review current status
poetry run project-manager developer-status

# 3. Check for blockers
poetry run project-manager notifications
```

#### Afternoon Check-In

```bash
# Quick status check
poetry run project-manager developer-status
```

#### End of Day

```bash
# Review today's work
poetry run project-manager standup --since today

# Approve any pending requests
poetry run project-manager notifications
poetry run project-manager respond <id> approve
```

### Custom Reporting

You can query the activity database directly for custom reports:

```bash
sqlite3 data/activity.db "
  SELECT
    date(created_at) as date,
    COUNT(*) as commits,
    SUM(json_extract(metadata, '$.lines_added')) as lines_added
  FROM activities
  WHERE activity_type = 'commit'
    AND created_at >= date('now', '-7 days')
  GROUP BY date(created_at)
  ORDER BY date DESC;
"
```

---

## FAQ

**Q: How often does the daemon update status?**
A: After every significant action (commit, test run, file change).

**Q: Can I configure standup frequency?**
A: Currently daily (automatic on first interaction). Weekly/monthly coming in future.

**Q: Where is the data stored?**
A: All data is in the `data/` directory (git-ignored).

**Q: Can I export standup reports?**
A: Yes! Save to markdown:
```bash
poetry run project-manager standup > standup_2025-10-17.md
```

**Q: Does this work with multiple developers?**
A: Currently single developer. Multi-developer support in future PRIORITYs.

**Q: Can I disable daily standups?**
A: Not yet. Feature flagging coming in future update.

**Q: How long is activity data retained?**
A: Indefinitely. Database grows ~10MB per year of active development.

---

## Next Steps

- ✅ **PRIORITY 9 Complete** - Daily communication implemented
- 🔄 **PRIORITY 10** - Weekly summaries and sprint reviews
- 🔄 **PRIORITY 11** - Real-time progress streaming
- 🔄 **PRIORITY 12** - Slack/email integration
- 🔄 **PRIORITY 13** - AI-powered insights and recommendations

---

## Support

For issues or questions:
- Check ROADMAP.md for status
- Review CLAUDE.md for architecture
- Create issue in GitHub
- Ask in project-manager chat: `poetry run project-manager chat`

---

**Last Updated**: 2025-10-18
**Version**: 1.0.0
**Status**: Production Ready ✅
