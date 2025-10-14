# PRIORITY 9: Enhanced code_developer Communication & Daily Standup - Complete Guide

## Overview

The Enhanced Communication System transforms `code_developer` from a silent background process into a **communicative team member** that provides daily status updates, progress reports, and real-time activity tracking. Just like a professional human developer on an agile team, the AI developer now provides standups, reports accomplishments, and keeps you informed about its work.

**Status**: ✅ Complete (Technical Spec Available)
**Impact**: ⭐⭐⭐⭐⭐ (Critical for trust and visibility)
**Strategic Goal**: Build trust and engagement through professional communication

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [What's New](#whats-new)
3. [Daily Standup Reports](#daily-standup-reports)
4. [Real-Time Developer Status](#real-time-developer-status)
5. [Activity Tracking](#activity-tracking)
6. [Communication Patterns](#communication-patterns)
7. [CLI Commands](#cli-commands)
8. [Configuration](#configuration)
9. [Integration with Workflow](#integration-with-workflow)
10. [Troubleshooting](#troubleshooting)
11. [Technical Reference](#technical-reference)

---

## Quick Start

### 1. Check Developer Status

See what the `code_developer` daemon is currently doing:

```bash
# One-time status check
poetry run project-manager developer-status

# Watch status in real-time (updates every 5 seconds)
poetry run project-manager developer-status --watch
```

**Example Output:**
```
┌─────────────────── Developer Status Dashboard ────────────────────┐
│         State: 🟢 WORKING                                          │
│          Task: PRIORITY 2.6 - CI Testing & Build Automation       │
│      Progress: ██████████████░░░░░░░░░░░░░░░░ 50%                │
│          Step: Creating GitHub Actions workflow                   │
│           ETA: 2h 30m                                              │
│       Elapsed: 1h 45m                                              │
│ Last Activity: Committed "ci: Add pytest configuration" (2m ago)  │
│                                                                    │
│         Today: Tasks: 1 | Commits: 3 | Tests: 47/0               │
│                                                                    │
│    Daemon PID: 12345                                              │
│        Uptime: 5h 23m                                             │
└────────────────────────────────────────────────────────────────────┘
```

### 2. Get Daily Summary (Morning Standup)

When you start your day with `project-manager chat`, you'll automatically see a daily summary:

```bash
poetry run project-manager chat
```

**Example Morning Greeting:**
```
┌──────────────── 🤖 code_developer Daily Update ────────────────────┐
│                                                                     │
│ 📊 Yesterday's Accomplishments (2025-10-10):                       │
│ ✅ Completed PRIORITY 2.5 - CI Testing & Build Automation          │
│    - Implemented pytest configuration with parallel execution      │
│    - Added GitHub Actions CI workflow                              │
│    - Fixed 3 failing tests in authentication module                │
│    - All 47 tests now passing | Coverage: 87% (+5%)               │
│    - Commits: 4 | Files changed: 12 | Lines added: 320            │
│                                                                     │
│ 🔄 Current Status:                                                  │
│    - Working on PRIORITY 2.6 - Documentation Enhancement          │
│    - ETA: 2-3 hours remaining                                      │
│                                                                     │
│ 📈 Metrics:                                                        │
│    - Commits: 4                                                    │
│    - Tests Passed: 47/47 (100%)                                   │
│    - Files Modified: 12                                            │
│                                                                     │
│ 🎯 Next Steps:                                                     │
│    - Complete PRIORITY 2.6 documentation                           │
│    - Create pull request for review                                │
│                                                                     │
│ Have a productive day! 🚀                                          │
└─────────────────────────────────────────────────────────────────────┘

Now, how can I help you today?
> _
```

### 3. Manual Daily Report (Optional)

If you want to see the standup report without starting a chat:

```bash
# View yesterday's standup
poetry run project-manager dev report daily

# View specific date's standup
poetry run project-manager dev report daily --date 2025-10-10
```

---

## What's New

### Before PRIORITY 9 (Old Behavior)
- ❌ Daemon worked silently in the background
- ❌ No visibility into what it accomplished
- ❌ Had to manually check git logs to see progress
- ❌ No proactive communication
- ❌ Felt like a "black box" process

### After PRIORITY 9 (New Behavior)
- ✅ **Automatic daily standups** every morning
- ✅ **Real-time status dashboard** shows current activity
- ✅ **Comprehensive activity tracking** logs all work
- ✅ **Proactive communication** through project manager
- ✅ **Professional reporting** like a real team member
- ✅ **Trust and transparency** - always know what's happening

---

## Daily Standup Reports

### What is a Daily Standup?

Every morning when you interact with `project-manager chat`, you automatically receive a **daily standup report** summarizing what `code_developer` accomplished yesterday, what it's working on today, and any blockers.

### Standup Format

Daily standups include:

1. **📊 Yesterday's Accomplishments**
   - Completed priorities with details
   - Bug fixes and improvements
   - Documentation and maintenance

2. **🔄 Current Status**
   - What's currently in progress
   - Progress percentage and ETA
   - Current focus area

3. **⚠️ Blockers & Needs**
   - Items requiring your attention
   - Questions pending your input
   - Manual review requests

4. **📈 Metrics**
   - Commits, tests, files changed
   - Lines of code added/removed
   - Pull requests created

5. **🎯 Next Steps**
   - What will be worked on next
   - Planned priorities

### When Standups Appear

Standups are shown automatically when:
- ✅ It's a new day (first interaction after midnight)
- ✅ More than 12 hours since last chat
- ✅ There are activities from yesterday

Standups are **NOT** shown:
- ❌ Multiple times in the same day
- ❌ If no development activity yesterday
- ❌ If daemon hasn't been running

### Standup Report Example (Real Format)

```markdown
🤖 code_developer Daily Standup - 2025-10-10
================================================

📊 Yesterday's Accomplishments:
✅ Completed PRIORITY 2.5 - CI Testing & Build Automation
   - Implemented pytest configuration with parallel execution
   - Added GitHub Actions CI workflow
   - Fixed 3 failing tests in authentication module
   - All 47 tests now passing | Coverage: 87% (+5%)
   - Commits: 4 | Files changed: 12 | Lines added: 320

✅ Resolved critical bug in notification system (Issue #42)
   - Fixed race condition in SQLite WAL mode
   - Added retry logic for database locks
   - Validated fix with stress test (100 concurrent writes)

🔄 Current Status:
   - Working on PRIORITY 2.6 - Documentation Enhancement (45% complete)
   - ETA: 2-3 hours remaining
   - Writing comprehensive API documentation for autonomous module

⚠️ Blockers/Issues:
   - None at this time

📈 Metrics:
   - Commits: 4
   - Tests Passed: 47/47 (100%)
   - Files Modified: 12
   - Lines Added: 320 | Removed: 85
   - Pull Requests: 1 created (#45 - "Add CI Testing")

🎯 Next Steps:
   - Complete PRIORITY 2.6 documentation
   - Create pull request for review
   - Begin PRIORITY 3 - Analytics Dashboard (if 2.6 approved)

Have a productive day! 🚀
```

---

## Real-Time Developer Status

### Developer Status Dashboard

The developer status dashboard shows the **current** state of the `code_developer` daemon in real-time.

### Access Developer Status

```bash
# One-time check
poetry run project-manager developer-status

# Continuous monitoring (updates every 5 seconds)
poetry run project-manager developer-status --watch

# Stop watching with Ctrl+C
```

### Developer States

The daemon can be in one of seven states:

| State | Emoji | Description | What It Means |
|-------|-------|-------------|---------------|
| **WORKING** | 🟢 | Actively implementing | Writing code, making changes |
| **TESTING** | 🟡 | Running tests | Executing pytest, validating changes |
| **BLOCKED** | 🔴 | Waiting for user | Needs your approval or input |
| **IDLE** | ⚪ | Between tasks | Finished task, deciding what's next |
| **THINKING** | 🔵 | Analyzing codebase | Reading files, planning approach |
| **REVIEWING** | 🟣 | Creating PR/docs | Finalizing work, writing docs |
| **STOPPED** | ⚫ | Daemon not running | Process has stopped |

### Status Dashboard Fields

**State Information:**
- **State**: Current developer state with emoji
- **Task**: Name of current priority being worked on
- **Progress**: Visual progress bar (0-100%)
- **Step**: Detailed description of current activity
- **ETA**: Estimated time to completion
- **Elapsed**: Time spent on current task

**Recent Activity:**
- **Last Activity**: Most recent action with timestamp
  - Examples: "Committed changes", "Tests passed", "Created file"

**Pending Items:**
- **Pending Questions**: Questions waiting for your response
  - Shows up to 3 most recent questions

**Daily Metrics:**
- **Today**: Summary of today's work
  - Tasks completed
  - Commits made
  - Tests passed/failed

**Daemon Information:**
- **Daemon PID**: Process ID (for debugging)
- **Uptime**: How long daemon has been running

### Example Status Output

```
┌──────────────── Developer Status Dashboard ─────────────────┐
│       State: 🟢 WORKING                                      │
│        Task: PRIORITY 2.6 - CI Testing                      │
│    Progress: ██████████████░░░░░░░░░░░░░░░░ 50%            │
│        Step: Creating GitHub Actions workflow               │
│         ETA: 2h 30m                                          │
│     Elapsed: 1h 45m                                          │
│                                                              │
│ Last Activity: Committed "ci: Add pytest config" (2m ago)   │
│                                                              │
│       Today: Tasks: 1 | Commits: 3 | Tests: 47/0           │
│                                                              │
│  Daemon PID: 12345                                          │
│      Uptime: 5h 23m                                         │
└──────────────────────────────────────────────────────────────┘
```

### Watch Mode (Real-Time Updates)

Watch mode continuously updates the status dashboard:

```bash
poetry run project-manager developer-status --watch
```

**What you'll see:**
- Status updates every 5 seconds
- Progress bar advancing as work continues
- Last activity changing in real-time
- ETA adjusting based on progress

**When to use watch mode:**
- Monitoring long-running tasks
- Debugging daemon behavior
- Demonstrating to stakeholders
- Understanding workflow progress

**Stop watching:**
- Press `Ctrl+C` to exit

---

## Activity Tracking

### What is Activity Tracking?

The daemon now logs **every** action it takes to a persistent database (`data/activity.db`). This creates a comprehensive record of all development work.

### Activity Types Tracked

| Activity Type | Description | When It's Logged |
|---------------|-------------|------------------|
| **PRIORITY_STARTED** | Started working on priority | Beginning of new task |
| **PRIORITY_COMPLETED** | Finished priority | Task successfully done |
| **GIT_COMMIT** | Created git commit | After committing changes |
| **GIT_PUSH** | Pushed to remote | After pushing to GitHub |
| **GIT_BRANCH** | Created branch | When starting feature branch |
| **FILE_CREATED** | Created new file | New file added |
| **FILE_MODIFIED** | Modified existing file | File changed |
| **FILE_DELETED** | Deleted file | File removed |
| **TEST_RUN** | Executed tests | Running pytest |
| **TEST_PASSED** | Tests passed | All tests succeeded |
| **TEST_FAILED** | Tests failed | Some tests failed |
| **PR_CREATED** | Created pull request | PR opened on GitHub |
| **ERROR_ENCOUNTERED** | Hit an error | Exception or failure |
| **QUESTION_ASKED** | Asked for user input | Needs approval/decision |
| **DEPENDENCY_INSTALLED** | Installed package | pip/poetry install |
| **DOCUMENTATION_UPDATED** | Updated docs | Modified markdown/docstrings |

### Activity Structure

Each activity includes:

```python
{
    "id": 12345,                      # Unique ID
    "activity_type": "commit",        # Type (see table above)
    "title": "Add pytest configuration",  # Short description
    "description": "Full commit message...",  # Details
    "priority_number": "2.5",         # Which priority
    "priority_name": "CI Testing",    # Priority name
    "metadata": {                      # Type-specific data
        "files_changed": 3,
        "lines_added": 120,
        "lines_removed": 45,
        "commit_hash": "abc123..."
    },
    "outcome": "success",              # success/failure/partial/blocked
    "created_at": "2025-10-10T14:30:00Z",  # ISO timestamp
    "session_id": "uuid-..."          # Groups related activities
}
```

### Viewing Activity History

**Via CLI:**
```bash
# View recent activities (coming in future update)
poetry run project-manager dev history

# View activities for specific priority
poetry run project-manager dev history --priority 2.5

# View activities for date range
poetry run project-manager dev history --since 2025-10-01
```

**Via Database:**
```bash
# Direct database query
sqlite3 data/activity.db "SELECT * FROM activities ORDER BY created_at DESC LIMIT 10;"
```

### Activity Database Location

- **Path**: `data/activity.db`
- **Format**: SQLite database
- **Size**: ~1-2 MB per month
- **Retention**: 30 days (configurable)

---

## Communication Patterns

### Pattern 1: Morning Check-In

**User Workflow:**
```bash
# User starts their day
$ poetry run project-manager chat

# System automatically shows daily standup
[Daily standup appears - see example above]

# User continues with normal chat
> What should I work on today?
```

**When it happens:**
- First `project-manager chat` of the day
- After midnight or >12 hours since last chat

**What you get:**
- Summary of yesterday's accomplishments
- Current status and progress
- Any blockers or questions
- Plan for today

### Pattern 2: Continuous Monitoring

**User Workflow:**
```bash
# User opens a dedicated terminal for monitoring
$ poetry run project-manager developer-status --watch

# Dashboard updates in real-time
# User keeps this running in the background while working
```

**When to use:**
- During long-running daemon sessions
- When demonstrating to stakeholders
- When debugging issues
- When you want constant awareness

**What you see:**
- Real-time status updates
- Progress advancing
- Activities as they happen
- ETA adjustments

### Pattern 3: Periodic Check-Ins

**User Workflow:**
```bash
# User checks status occasionally during the day
$ poetry run project-manager developer-status

# Quick status check
[Status dashboard appears]

# Continue working
```

**When to use:**
- Quick progress checks
- Before meetings
- When switching contexts
- To verify daemon is still running

### Pattern 4: Historical Review

**User Workflow:**
```bash
# User wants to see what happened yesterday
$ poetry run project-manager dev report daily --date 2025-10-09

# Or review this week
$ poetry run project-manager dev report weekly

# Or see full activity log
$ poetry run project-manager dev history
```

**When to use:**
- End-of-week reviews
- Sprint retrospectives
- Progress reporting to stakeholders
- Understanding what was accomplished

---

## CLI Commands

### Core Commands

#### 1. `developer-status` - Real-Time Status

Show current developer state and activity.

```bash
# Basic usage
poetry run project-manager developer-status

# Watch mode (real-time updates)
poetry run project-manager developer-status --watch

# Specify update interval (seconds)
poetry run project-manager developer-status --watch --interval 10
```

**Options:**
- `--watch` - Continuous updates (default: 5 seconds)
- `--interval N` - Update every N seconds

**Exit codes:**
- `0` - Status displayed successfully
- `1` - Daemon not running or status unavailable

#### 2. `chat` - Interactive Session with Standup

Start interactive chat with automatic morning standup.

```bash
# Start chat (shows standup if new day)
poetry run project-manager chat

# Skip standup (force no standup)
poetry run project-manager chat --no-standup

# Force show standup (even if already shown today)
poetry run project-manager chat --force-standup
```

**Behavior:**
- Shows standup on first chat of day
- Then continues with normal AI chat
- Smart detection (new day, >12h gap)

#### 3. `dev report` - Historical Reports (Future)

Generate reports for past activities.

```bash
# Daily report (yesterday by default)
poetry run project-manager dev report daily

# Specific date
poetry run project-manager dev report daily --date 2025-10-10

# Weekly report (this week)
poetry run project-manager dev report weekly

# Sprint/monthly report
poetry run project-manager dev report sprint

# Custom date range
poetry run project-manager dev report --from 2025-10-01 --to 2025-10-10
```

**Report formats:**
- `daily` - Single day summary
- `weekly` - 7-day summary
- `sprint` - Monthly/sprint summary
- Custom - Date range query

#### 4. `dev history` - Activity Log (Future)

View detailed activity history.

```bash
# Recent activities (last 20)
poetry run project-manager dev history

# Filter by priority
poetry run project-manager dev history --priority 2.5

# Filter by activity type
poetry run project-manager dev history --type commit

# Filter by date range
poetry run project-manager dev history --since 2025-10-01

# Show more details
poetry run project-manager dev history --verbose

# Export to JSON
poetry run project-manager dev history --format json > activities.json
```

**Filters:**
- `--priority N` - Filter by priority number
- `--type TYPE` - Filter by activity type
- `--since DATE` - Activities since date
- `--until DATE` - Activities until date
- `--outcome STATUS` - Filter by success/failure

### Quick Reference

```bash
# What is the daemon doing RIGHT NOW?
poetry run project-manager developer-status

# What did it accomplish YESTERDAY?
poetry run project-manager chat  # Shows standup automatically

# Monitor it CONTINUOUSLY?
poetry run project-manager developer-status --watch

# See DETAILED HISTORY?
poetry run project-manager dev history

# Generate WEEKLY REPORT?
poetry run project-manager dev report weekly
```

---

## Configuration

### Communication Settings (Future)

Configure how the daemon communicates with you.

**Configuration File**: `~/.config/coffee-maker/communication.yaml`

```yaml
communication:
  # Daily standup settings
  daily_standup:
    enabled: true
    time: "09:00"                    # Local time for standup
    channels:
      - terminal                      # Display in terminal
      - notification                  # System notification (macOS/Linux)
      - file: "logs/standup.md"      # Save to file
      # - slack: "webhook_url"        # Optional: Send to Slack

  # Weekly summary settings
  weekly_summary:
    enabled: true
    day: "friday"                     # Day of week
    time: "17:00"                     # End of day

  # Real-time updates
  realtime_updates:
    enabled: true
    milestones: true                  # Notify on major milestones
    blockers: true                    # Notify immediately on blockers
    questions: true                   # Ask for input when needed
    quiet_hours:
      start: "22:00"                  # Don't notify during quiet hours
      end: "08:00"

  # Communication style
  verbosity: "normal"                 # minimal | normal | verbose
  timezone: "America/New_York"        # Your timezone
  emoji: true                         # Use emojis in reports

  # Data retention
  activity_retention_days: 30         # Keep activities for 30 days
  summary_cache_days: 365            # Keep summaries for 1 year
```

### Status File Location

The daemon writes its current status to:

**Path**: `data/developer_status.json`

**Format**:
```json
{
  "status": "working",
  "current_task": {
    "priority": 2.6,
    "name": "CI Testing",
    "progress": 50,
    "current_step": "Creating GitHub Actions workflow",
    "started_at": "2025-10-10T12:00:00Z",
    "eta_seconds": 9000
  },
  "last_activity": {
    "timestamp": "2025-10-10T14:28:00Z",
    "type": "git_commit",
    "description": "ci: Add pytest configuration"
  },
  "activity_log": [
    // Last 20 activities
  ],
  "questions": [],
  "metrics": {
    "tasks_completed_today": 1,
    "total_commits_today": 3,
    "tests_passed_today": 47,
    "tests_failed_today": 0
  },
  "daemon_info": {
    "pid": 12345,
    "started_at": "2025-10-10T08:00:00Z",
    "version": "1.0.0"
  }
}
```

**Access programmatically:**
```python
import json
from pathlib import Path

status_file = Path("data/developer_status.json")
with open(status_file) as f:
    status = json.load(f)

print(f"Daemon is: {status['status']}")
print(f"Working on: {status['current_task']['name']}")
print(f"Progress: {status['current_task']['progress']}%")
```

---

## Integration with Workflow

### Daily Workflow Example

**Morning:**
```bash
# 1. Start your day
$ poetry run project-manager chat

# 2. Automatic standup appears
[Shows yesterday's accomplishments]

# 3. Review and decide priorities
> Show me the roadmap
> Should we continue with PRIORITY 2.6?
```

**During the Day:**
```bash
# Dedicated monitoring terminal
$ poetry run project-manager developer-status --watch

# Or periodic checks
$ poetry run project-manager developer-status
```

**Afternoon:**
```bash
# Check in with project manager
$ poetry run project-manager chat

> How's the progress on PRIORITY 2.6?
> Any blockers?
```

**End of Day:**
```bash
# Review today's work
$ poetry run project-manager dev report daily

# Or just check status
$ poetry run project-manager developer-status
```

### Integration with Team Workflows

#### Standup Meetings

Use daily standups for team sync:

```bash
# Before standup meeting, get AI developer's report
$ poetry run project-manager dev report daily

# Share in meeting:
# "Our AI developer completed PRIORITY 2.5 yesterday with 4 commits..."
```

#### Sprint Planning

Use weekly/sprint reports for planning:

```bash
# Generate sprint report
$ poetry run project-manager dev report sprint

# Review velocity and achievements
# Plan next sprint priorities
```

#### Stakeholder Updates

Export reports for stakeholders:

```bash
# Generate professional report
$ poetry run project-manager dev report weekly --format markdown > weekly_report.md

# Share via email or Slack
```

### Integration with Notifications

The daemon already uses the notification system for questions and approvals. Communication enhances this:

```bash
# Check notifications (existing)
$ poetry run project-manager notifications

# Example notification with context
[Notification #12] code_developer is blocked
  - Waiting for approval on dependency: pytest-cov
  - See details: project-manager developer-status

# Respond
$ poetry run project-manager respond 12 approve
```

---

## Troubleshooting

### Issue: No Daily Standup Appearing

**Symptoms:**
- `project-manager chat` doesn't show standup
- Expected morning update but didn't see it

**Possible Causes:**
1. Already saw standup today (only shows once per day)
2. No development activity yesterday
3. Daemon hasn't been running
4. Less than 12 hours since last chat

**Solutions:**
```bash
# Force show standup
poetry run project-manager chat --force-standup

# Check if daemon has been running
poetry run project-manager developer-status

# Manually view daily report
poetry run project-manager dev report daily
```

### Issue: Developer Status Shows "Not Available"

**Symptoms:**
```
⚠️  Developer status not available
The code_developer daemon may not be running.
```

**Possible Causes:**
1. Daemon is not running
2. Status file doesn't exist
3. Status file is corrupted

**Solutions:**
```bash
# 1. Check if daemon is running
ps aux | grep code-developer

# 2. Start daemon if not running
poetry run code-developer

# 3. Check status file
ls -la data/developer_status.json

# 4. If corrupted, restart daemon
# (daemon will recreate status file)
```

### Issue: Watch Mode Not Updating

**Symptoms:**
- `developer-status --watch` stuck on same screen
- No updates happening

**Possible Causes:**
1. Daemon is idle (no activity)
2. Status file not being updated
3. Terminal refresh issue

**Solutions:**
```bash
# 1. Check daemon is actually working
poetry run project-manager developer-status  # One-time check

# 2. Increase update interval (slower refresh)
poetry run project-manager developer-status --watch --interval 10

# 3. Restart watch mode
# Ctrl+C, then rerun command
```

### Issue: Activity History Missing

**Symptoms:**
- No activities in reports
- Database seems empty

**Possible Causes:**
1. Daemon hasn't logged activities yet (new installation)
2. Activity database doesn't exist
3. Database file corrupted

**Solutions:**
```bash
# 1. Check if database exists
ls -la data/activity.db

# 2. Check if daemon is logging activities
# (Wait for daemon to complete one task)

# 3. Query database directly
sqlite3 data/activity.db "SELECT COUNT(*) FROM activities;"

# 4. If corrupted, delete and let daemon recreate
rm data/activity.db
# Daemon will create new database on next activity
```

### Issue: Standup Quality Issues

**Symptoms:**
- Standup reports are too verbose
- Missing important details
- Format looks wrong

**Possible Causes:**
1. Claude API issues
2. Not enough activity data
3. Prompt needs tuning

**Solutions:**
```bash
# 1. Check if using fallback mode (no Claude API)
# Look for "AI summary unavailable" in standup

# 2. Verify ANTHROPIC_API_KEY is set
echo $ANTHROPIC_API_KEY

# 3. Force regenerate standup
poetry run project-manager dev report daily --force-regenerate

# 4. Report issue for prompt improvements
# (See GitHub issues)
```

### Issue: ETA is Inaccurate

**Symptoms:**
- Estimated time remaining seems way off
- ETA jumping around

**Possible Causes:**
1. Progress tracking is imprecise
2. Task complexity varies
3. ETA calculation based on limited data

**Explanation:**
- ETA is calculated from elapsed time and progress
- Formula: `remaining = (elapsed / progress) * (100 - progress)`
- Early estimates are less accurate
- Improves as task progresses

**No action needed** - this is expected behavior. ETA becomes more accurate as progress increases.

### Common Error Messages

#### Error: "Failed to generate daily standup"

**Cause**: Claude API failure or rate limit

**Solution**:
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Wait a few minutes and try again
# System will use fallback summary with metrics
```

#### Error: "Database locked"

**Cause**: Multiple processes trying to write simultaneously

**Solution**:
- No action needed - daemon uses automatic retry logic
- If persistent, check for zombie processes:
  ```bash
  ps aux | grep code-developer
  kill -9 <PID>  # If zombie process found
  ```

#### Error: "Status file not found"

**Cause**: Daemon not started yet

**Solution**:
```bash
# Start daemon
poetry run code-developer
```

---

## Technical Reference

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│                                                          │
│  Terminal: project-manager chat / developer-status      │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  PROJECT MANAGER CLI                     │
│                                                          │
│  • Detects "new day" interactions                       │
│  • Queries ActivityTracker for daily summary            │
│  • Displays developer status dashboard                  │
│  • Formats standup reports                              │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│               ACTIVITY TRACKING SYSTEM                   │
│                                                          │
│  • ActivityDB: SQLite database (data/activity.db)       │
│  • ActivityLogger: High-level logging interface         │
│  • StandupGenerator: Creates daily summaries            │
│  • DeveloperStatus: Real-time status tracking           │
└─────────────────────────────────────────────────────────┘
                          ▲
┌─────────────────────────────────────────────────────────┐
│                CODE DEVELOPER DAEMON                     │
│                                                          │
│  • Logs all activities via ActivityLogger               │
│  • Updates developer_status.json continuously           │
│  • Reports progress, state changes, errors              │
│  • Creates notifications for user input                 │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. ActivityDB (`coffee_maker/autonomous/activity_db.py`)

**Purpose**: Persistent storage for all developer activities

**Database Schema**:
- `activities` table - Main activity log
- `daily_summaries` table - Cached standup reports
- `activity_stats` table - Aggregated metrics

**Key Methods**:
- `log_activity()` - Record an activity
- `get_activities()` - Query activities with filters
- `get_daily_metrics()` - Calculate day's metrics

#### 2. ActivityLogger (`coffee_maker/autonomous/activity_logger.py`)

**Purpose**: Convenience interface for logging from daemon

**Key Methods**:
- `start_priority()` - Log priority start
- `complete_priority()` - Log priority completion
- `log_commit()` - Log git commit
- `log_test_run()` - Log test execution
- `log_pr_created()` - Log PR creation

#### 3. StandupGenerator (`coffee_maker/autonomous/standup_generator.py`)

**Purpose**: Generate daily standup reports using Claude API

**Key Methods**:
- `generate_daily_standup()` - Create standup for date
- `_generate_with_claude()` - Use AI to format summary
- `_calculate_metrics()` - Compute statistics
- `_cache_summary()` - Save for fast retrieval

#### 4. DeveloperStatus (`coffee_maker/autonomous/developer_status.py`)

**Purpose**: Real-time status tracking for daemon

**File**: `data/developer_status.json`

**Key Methods**:
- `update_status()` - Change state (working, testing, etc.)
- `report_activity()` - Log recent action
- `report_progress()` - Update progress percentage
- `add_question()` - Ask user for input

#### 5. DeveloperStatusDisplay (`coffee_maker/cli/developer_status_display.py`)

**Purpose**: Format status for terminal display

**Key Methods**:
- `show()` - Display status once
- `watch()` - Continuous monitoring
- `_format_status()` - Create Rich UI panel

### Data Flow

#### Daily Standup Generation:
1. User runs `project-manager chat`
2. ChatInterface detects new day (>12h or after midnight)
3. StandupGenerator queries ActivityDB for yesterday's activities
4. Calculates metrics (commits, tests, files changed)
5. Calls Claude API to generate formatted summary
6. Caches summary in database
7. Displays in terminal with Rich formatting
8. Continues with normal chat

#### Real-Time Status Updates:
1. Daemon executes work (e.g., commits code)
2. Calls `ActivityLogger.log_commit()`
3. ActivityLogger writes to ActivityDB
4. Daemon updates `developer_status.json`
5. User runs `project-manager developer-status`
6. DeveloperStatusDisplay reads status file
7. Formats and displays in terminal

### Database Schema

**Activities Table:**
```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    priority_number TEXT,
    priority_name TEXT,
    title TEXT NOT NULL,
    description TEXT,
    metadata TEXT,  -- JSON
    outcome TEXT NOT NULL DEFAULT 'success',
    created_at TEXT NOT NULL,  -- ISO 8601
    session_id TEXT
);
```

**Indexes:**
```sql
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_date ON activities(created_at);
CREATE INDEX idx_activities_priority ON activities(priority_number);
```

### API Reference

See `docs/PRIORITY_9_TECHNICAL_SPEC.md` for complete API reference including:
- Full method signatures
- Parameter descriptions
- Return types
- Example usage
- Error handling

### File Locations

| File | Purpose | Format |
|------|---------|--------|
| `data/developer_status.json` | Current daemon state | JSON |
| `data/activity.db` | Activity history | SQLite |
| `data/last_chat_time.txt` | Last chat timestamp | Plain text |
| `logs/standup.md` | Standup archive | Markdown |

### Performance Characteristics

| Operation | Expected Time |
|-----------|---------------|
| Log activity | <10ms |
| Query activities (1 day) | <50ms |
| Generate standup (cached) | <100ms |
| Generate standup (uncached) | <3s |
| Display status | <500ms |
| Watch mode update | <100ms |

---

## Examples

### Example 1: Morning Workflow

```bash
# Day starts at 9:00 AM
$ poetry run project-manager chat

🤖 project-manager: Good morning! Before we start, here's what
   code_developer accomplished yesterday:

[Daily standup appears - see full example above]

Now, how can I help you today?
> What's on the roadmap for this week?

🤖 project-manager: Let me show you the roadmap...
[Continues with normal chat]
```

### Example 2: Monitoring Long Task

**Terminal 1 - Daemon:**
```bash
$ poetry run code-developer
Starting autonomous development daemon...
✓ Loaded roadmap
✓ Found next priority: PRIORITY 2.6
✓ Created branch: feature/priority-2.6
Working on PRIORITY 2.6...
```

**Terminal 2 - Monitor:**
```bash
$ poetry run project-manager developer-status --watch

# Updates every 5 seconds:
# 14:00:00 - Progress: 10% - Reading existing tests
# 14:05:30 - Progress: 25% - Creating test fixtures
# 14:12:15 - Progress: 40% - Writing unit tests
# 14:20:00 - Progress: 60% - Running test suite
# ...
```

### Example 3: Weekly Review Meeting

```bash
# Before weekly team meeting
$ poetry run project-manager dev report weekly

🤖 code_developer Weekly Summary - Week of 2025-10-03
======================================================

🎯 This Week's Achievements:

✅ Completed Priorities:
   1. PRIORITY 2.5 - CI Testing (2 days)
   2. PRIORITY 2.6 - Documentation (1 day)

🚀 Features Delivered:
   - GitHub Actions CI workflow
   - Comprehensive test suite (47 tests)
   - API documentation (12 modules)

📊 Statistics:
   - Commits: 18
   - Pull Requests: 3 (all merged)
   - Lines of code: +2,450 / -320
   - Tests added: 24
   - Test coverage: 87% (↗️ +5%)

🔄 In Progress:
   - PRIORITY 3 - Analytics Dashboard (20% complete)

📈 Velocity:
   - Velocity this week: 13 story points
   - Trend: ↗️ Increasing

🎯 Next Week's Goals:
   1. Complete PRIORITY 3
   2. Start PRIORITY 4 - Agent UI
   3. Address technical debt in parser module
```

### Example 4: Debugging Daemon Issue

```bash
# Something seems wrong, daemon appears stuck
$ poetry run project-manager developer-status

┌──────────────── Developer Status Dashboard ─────────────────┐
│       State: 🔴 BLOCKED                                      │
│        Task: PRIORITY 2.7 - Database Migration              │
│    Progress: ████████░░░░░░░░░░░░░░░░░░░░░░░ 30%           │
│        Step: Waiting for user approval                       │
│                                                              │
│ Pending Questions: 1 question(s)                            │
│   Q1: Should I use Alembic or raw SQL for migration?       │
└──────────────────────────────────────────────────────────────┘

# Ah! Daemon is blocked waiting for my response
$ poetry run project-manager notifications

[Notification #15] Dependency Approval Required
  - Question: Should I use Alembic or raw SQL for migration?
  - Priority: 2.7 - Database Migration
  - Created: 30 minutes ago

$ poetry run project-manager respond 15 "Use Alembic"

✓ Response recorded
✓ Daemon will continue with your decision

# Check status again
$ poetry run project-manager developer-status

┌──────────────── Developer Status Dashboard ─────────────────┐
│       State: 🟢 WORKING                                      │
│        Task: PRIORITY 2.7 - Database Migration              │
│    Progress: ██████████░░░░░░░░░░░░░░░░░░░ 35%             │
│        Step: Installing Alembic dependency                   │
│         ETA: 1h 30m                                          │
└──────────────────────────────────────────────────────────────┘

# Great! It's unblocked and continuing
```

---

## What's Next

### Implemented in PRIORITY 9 ✅

- ✅ Real-time developer status dashboard
- ✅ Comprehensive activity tracking database
- ✅ Daily standup report generation (technical foundation)
- ✅ Project manager integration (status display)
- ✅ Rich terminal UI components

### Coming Soon 🚀

**Phase 2 Features:**
- Weekly summary reports
- Sprint/milestone summaries
- Historical activity queries (`dev history` command)
- Custom date range reports
- Export to multiple formats (JSON, CSV, PDF)

**Phase 3 Features:**
- Slack integration (send standups to Slack)
- Email integration (morning standup emails)
- Webhook support (trigger on milestones)
- Custom notification channels

**Phase 4 Features:**
- AI-generated insights and trends
- Predictive ETA using machine learning
- Performance comparison metrics
- Burndown charts and visualizations
- Team dashboard (multi-developer support)

### Feedback

We'd love to hear your feedback on the communication system!

**What's working well:**
- Are the standups helpful?
- Is the status dashboard informative?
- Are you using watch mode?

**What needs improvement:**
- Standup format too verbose/brief?
- Missing information in reports?
- Want different metrics?
- Need different communication channels?

**Submit feedback:**
- GitHub Issues: `anthropics/coffee-maker/issues`
- In-app: `project-manager chat` > "I have feedback on the standup system"

---

## Conclusion

The Enhanced Communication System (PRIORITY 9) transforms `code_developer` from a silent background process into a **professional, communicative team member**. With daily standups, real-time status dashboards, and comprehensive activity tracking, you now have full visibility into what your AI developer is doing.

**Key Takeaways:**
- ✅ **Automatic daily standups** - Know what happened yesterday
- ✅ **Real-time status** - See current activity and progress
- ✅ **Activity tracking** - Complete history of all work
- ✅ **Professional communication** - Like a real developer on your team
- ✅ **Trust and transparency** - Always know what's happening

**Get Started:**
```bash
# Try it now!
poetry run project-manager chat            # See daily standup
poetry run project-manager developer-status  # Check current status
```

**Learn More:**
- Technical Spec: `docs/PRIORITY_9_TECHNICAL_SPEC.md`
- Implementation: `coffee_maker/autonomous/developer_status.py`
- Roadmap: `docs/roadmap/ROADMAP.md` (PRIORITY 9 section)

---

**Version**: 1.0
**Last Updated**: 2025-10-11
**Status**: ✅ Complete (Technical Foundation) | 🚀 Enhancements Coming Soon
