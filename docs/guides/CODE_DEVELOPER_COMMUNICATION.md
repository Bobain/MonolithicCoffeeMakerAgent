# code_developer Communication & Daily Standup Guide

**PRIORITY 9: Enhanced code_developer Communication & Daily Standup** ✅

This guide explains how the `code_developer` daemon communicates like a professional team member with daily status updates, progress tracking, and proactive notifications.

## Table of Contents

- [Overview](#overview)
- [Daily Standup Reports](#daily-standup-reports)
- [CLI Commands](#cli-commands)
- [Activity Tracking](#activity-tracking)
- [Chat Integration](#chat-integration)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

The `code_developer` daemon now provides professional communication features:

1. **Daily Standup Reports** - AI-generated summaries of work accomplished
2. **Activity Tracking** - Comprehensive logging of all development activities
3. **Chat Integration** - Automatic standup display on first chat of the day
4. **Real-time Status** - Current progress and blockers
5. **Professional Format** - Clean, readable reports with metrics

### Business Value

- ✅ **Trust Building**: Users see exactly what the AI accomplished each day
- ✅ **Progress Tracking**: Daily summaries help track momentum and identify blockers
- ✅ **Team Integration**: AI developer provides standups just like human developers
- ✅ **Accountability**: Clear reporting builds confidence in the system
- ✅ **Context Awareness**: Summaries help users understand project status

---

## Daily Standup Reports

### What Gets Tracked

The system automatically tracks all `code_developer` activities:

- **Commits**: Git commits with file counts and line changes
- **PRs Created**: Pull requests opened
- **Tests Run**: Test execution and results
- **Priorities**: Work started and completed
- **Errors**: Issues encountered
- **Documentation**: Docs updated
- **Dependencies**: Packages installed

### Report Format

Daily standup reports include:

```markdown
🤖 code_developer Daily Report - YYYY-MM-DD
============================================================

📊 Yesterday's Work (YYYY-MM-DD)

✅ PRIORITY X: [Priority Name]
  • [List of commits and work done]
  • Commits: N Files: M modified Lines: +X / -Y

✅ Other
  • [Additional work]

📈 Overall Stats
  • Total Commits: N
  • Files Modified: M
  • Lines Added: +X
  • Lines Removed: -Y

🔄 Today's Focus
  • PRIORITY Z: [Current priority]
    Progress: N%

✅ Blockers
None (or list of blockers)

────────────────────────────────────────────────────────────
Report generated: YYYY-MM-DD HH:MM:SS
```

### AI-Generated Summaries

The system uses Claude API to generate intelligent, human-readable summaries that:

- Highlight business value of work done
- Include specific metrics and numbers
- Focus on impact, not just activity
- Use professional but friendly tone
- Automatically categorize work by priority

---

## CLI Commands

### View Yesterday's Report

```bash
# Show yesterday's work (default)
poetry run project-manager dev-report

# Or explicitly
poetry run project-manager dev-report --days 1
```

**Output**: Professional daily standup report with all activities from yesterday.

### View Last N Days

```bash
# Last 7 days
poetry run project-manager dev-report --days 7

# Last 30 days
poetry run project-manager dev-report --days 30
```

**Output**: Aggregated report showing work from the specified time period.

### Developer Status Dashboard

```bash
# Show current daemon status
poetry run project-manager developer-status
```

**Output**: Real-time view of what `code_developer` is currently working on.

### Interactive Chat with Standup

```bash
# Start interactive chat
poetry run project-manager chat
```

**Behavior**:
- First chat of the day (>12 hours since last chat) automatically shows daily standup
- Subsequent chats skip the standup unless forced
- Natural conversation flow with project context

---

## Activity Tracking

### Automatic Activity Logging

All `code_developer` daemon activities are automatically logged to SQLite database:

**Database Location**: `data/activity_tracking.db`

**Schema**:
- `activities` table: Individual activities with metadata
- `daily_summaries` table: Cached AI-generated summaries
- `activity_stats` table: Aggregated statistics by day and type

### Activity Types

| Type | Description | Metadata Captured |
|------|-------------|-------------------|
| `commit` | Git commits | `commit_hash`, `files_changed`, `lines_added`, `lines_removed` |
| `pr_created` | Pull requests | `pr_number`, `pr_url`, `branch_name` |
| `test_run` | Test execution | `tests_passed`, `tests_failed`, `coverage_percent` |
| `priority_started` | Started working on priority | `priority_number`, `priority_name` |
| `priority_completed` | Completed priority | `priority_number`, `priority_name`, `duration_hours` |
| `error_encountered` | Errors/failures | `error_type`, `error_message`, `stack_trace` |
| `documentation_updated` | Docs modified | `files_updated`, `sections_added` |
| `dependency_installed` | Packages added | `package_name`, `version` |

### Querying Activities Programmatically

```python
from coffee_maker.autonomous.activity_db import ActivityDB
from datetime import date, timedelta

# Initialize database
db = ActivityDB()

# Get activities for yesterday
yesterday = date.today() - timedelta(days=1)
activities = db.get_activities(
    start_date=yesterday,
    end_date=yesterday,
    limit=100
)

# Get daily metrics
metrics = db.get_daily_metrics(yesterday)

print(f"Commits: {metrics['commits']}")
print(f"Tests run: {metrics['test_runs']}")
print(f"PRs created: {metrics['prs_created']}")
```

---

## Chat Integration

### Automatic Standup Display

When you start a chat session with `project-manager chat`:

1. **First Chat of Day** (>12 hours since last chat):
   - System automatically generates and displays daily standup
   - Shows what `code_developer` accomplished yesterday
   - Provides context before conversation starts

2. **Subsequent Chats**:
   - Standup is skipped (already shown today)
   - Can force display with manual `dev-report` command

### Example Chat Flow

```bash
$ poetry run project-manager chat

Generating daily standup report...

🤖 code_developer Daily Report - 2025-10-18
============================================================

📊 Yesterday's Work (2025-10-17)

✅ PRIORITY 9: Enhanced code_developer Communication & Daily Standup
  • Implemented activity tracking database
  • Created standup generator with AI summaries
  • Integrated with chat interface
  Commits: 5 Files: 12 modified Lines: +850 / -45

📈 Overall Stats
  • Total Commits: 5
  • Files Modified: 12
  • Lines Added: +850
  • Lines Removed: -45

🔄 Today's Focus
  • PRIORITY 9: Documentation
    Progress: 80%

✅ Blockers
None

────────────────────────────────────────────────────────────

Now, how can I help you today?

> _
```

### Smart Detection

The system detects "new day" by checking:
- Time since last chat session
- If >12 hours, show standup
- If <12 hours, skip standup

This creates a natural flow where you get a morning update when you start work.

---

## Configuration

### AI Model Selection

The standup generator uses Claude API. Configuration in `coffee_maker/autonomous/standup_generator.py`:

```python
# Claude model for summary generation
model="claude-3-5-sonnet-20241022"
max_tokens=2000
temperature=0.7
```

### API Key Setup

Ensure Anthropic API key is configured:

```bash
# Set in environment
export ANTHROPIC_API_KEY="sk-ant-..."

# Or in config file
# ~/.config/coffee-maker/config.yaml
```

### Customizing Report Format

To customize report templates, modify `STANDUP_PROMPT_TEMPLATE` in:
`coffee_maker/autonomous/standup_generator.py`

**Current sections**:
- 📊 Yesterday's Accomplishments
- 🔄 Current Status
- ⚠️ Blockers/Issues
- 📈 Metrics
- 🎯 Next Steps

### Database Configuration

Activity tracking database settings:

```python
# Default location
database_path = "data/activity_tracking.db"

# WAL mode enabled for concurrent access
# Automatic indexing for fast queries
# Retry protection for transient failures
```

---

## Examples

### Example 1: Morning Standup

**Command**:
```bash
poetry run project-manager dev-report
```

**Output**:
```
🤖 code_developer Daily Report - 2025-10-18
============================================================

📊 Yesterday's Work (2025-10-17)

✅ PRIORITY 7: Multi-Model Code Review Agent
  • Implemented core reviewer with perspective system
  • Added report generation with markdown export
  • Integrated with Git for automatic PR reviews
  Commits: 8 Files: 24 modified Lines: +1250 / -120

✅ Bug Fixes
  • Fixed rate limiting in API calls
  • Resolved circular import in command registry
  Commits: 2 Files: 5 modified Lines: +45 / -30

📈 Overall Stats
  • Total Commits: 10
  • Files Modified: 29
  • Lines Added: +1295
  • Lines Removed: -150

🔄 Today's Focus
  • PRIORITY 7: Testing and documentation
    Progress: 60%

✅ Blockers
None
```

### Example 2: Weekly Review

**Command**:
```bash
poetry run project-manager dev-report --days 7
```

**Output**: Aggregated report showing all work from the past week with summary statistics.

### Example 3: Chat with Automatic Standup

**Command**:
```bash
poetry run project-manager chat
```

**Flow**:
1. System detects first chat of the day
2. Generates standup report automatically
3. Displays report before starting conversation
4. User can then ask questions with full context

---

## Troubleshooting

### Issue: No Activities Shown

**Cause**: `code_developer` daemon hasn't logged any activities yet

**Solution**:
```bash
# Check daemon status
poetry run project-manager developer-status

# Ensure daemon is running
poetry run code-developer --auto-approve
```

### Issue: AI Summary Generation Fails

**Cause**: Anthropic API key not configured or rate limit reached

**Solution**:
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Set if missing
export ANTHROPIC_API_KEY="sk-ant-..."

# System will fall back to template-based summary if AI fails
```

**Fallback Behavior**: If Claude API fails, system generates basic metrics summary without AI narrative.

### Issue: Database Lock Errors

**Cause**: Multiple processes accessing database concurrently

**Solution**:
- Database uses WAL mode for concurrent access
- Retry protection built-in (automatic retries on lock errors)
- If persists, check for zombie processes:

```bash
# Find code_developer processes
ps aux | grep code-developer

# Kill zombie processes if needed
kill <PID>
```

### Issue: Old Summaries Shown

**Cause**: Cached summaries not regenerating

**Solution**:
```bash
# Force regeneration (future enhancement)
# Currently, summaries are generated on-demand each time

# Clear cache manually if needed
rm data/activity_tracking.db
# Database will be recreated automatically
```

### Issue: Standup Not Shown in Chat

**Cause**: Chat session within 12 hours of previous session

**Solution**:
- This is expected behavior (prevents duplicate standups)
- Use explicit command instead:
  ```bash
  poetry run project-manager dev-report
  ```

---

## Architecture & Implementation

### Components

**Activity Tracking**:
- `activity_db.py`: SQLite database with activity logging
- `activity_logger.py`: Logging utilities for daemon

**Report Generation**:
- `standup_generator.py`: AI-powered daily standup generation
- Claude API integration for intelligent summaries

**CLI Integration**:
- `roadmap_cli.py`: `dev-report` command implementation
- `chat_interface.py`: Automatic standup display in chat

**Database Schema**:
```sql
-- Activities table
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    activity_type TEXT NOT NULL,
    priority_number TEXT,
    title TEXT NOT NULL,
    description TEXT,
    metadata TEXT,
    outcome TEXT DEFAULT 'success',
    created_at TEXT NOT NULL
);

-- Daily summaries cache
CREATE TABLE daily_summaries (
    id INTEGER PRIMARY KEY,
    date TEXT UNIQUE,
    summary_text TEXT,
    metrics TEXT,
    generated_at TEXT
);
```

### Data Flow

```
code_developer daemon
    ↓ logs activities
ActivityDB (SQLite)
    ↓ queries
StandupGenerator
    ↓ generates with Claude
Daily Standup Report
    ↓ displays
CLI / Chat Interface
    ↓ shows to
User
```

---

## Best Practices

### For Users

1. **Check Standup Daily**: Start your day with `project-manager chat` or `dev-report`
2. **Monitor Progress**: Use weekly reports (`--days 7`) for sprint reviews
3. **Review Blockers**: Pay attention to blockers section - address issues promptly
4. **Track Metrics**: Monitor commit counts, test coverage, and velocity

### For Developers Extending This System

1. **Log All Activities**: Use `ActivityDB.log_activity()` for new activity types
2. **Include Metadata**: Capture relevant metrics in metadata field
3. **Handle Failures**: Use retry protection for database operations
4. **Test AI Summaries**: Ensure fallback works when API unavailable
5. **Keep Templates Updated**: Update `STANDUP_PROMPT_TEMPLATE` as format evolves

---

## Future Enhancements

**Planned Features** (Post-PRIORITY 9):

- [ ] **Weekly Summary Reports**: Automated weekly summaries every Friday
- [ ] **Sprint Reviews**: Monthly sprint completion reports
- [ ] **Slack Integration**: Send standups to Slack channels
- [ ] **Email Reports**: Daily/weekly email summaries
- [ ] **Configurable Schedules**: User-defined report timing
- [ ] **Trend Analysis**: Velocity tracking and prediction
- [ ] **Custom Templates**: User-defined report formats
- [ ] **Voice Reports**: Text-to-speech daily summaries

---

## References

### Code Files

- `coffee_maker/autonomous/standup_generator.py`: Core standup generation
- `coffee_maker/autonomous/activity_db.py`: Activity tracking database
- `coffee_maker/autonomous/activity_logger.py`: Logging utilities
- `coffee_maker/cli/roadmap_cli.py`: CLI commands
- `coffee_maker/cli/chat_interface.py`: Chat integration

### Documentation

- [Activity Tracking Quickstart](./ACTIVITY_TRACKING_QUICKSTART.md)
- [ROADMAP.md](../roadmap/ROADMAP.md) - PRIORITY 9 details
- [CLAUDE.md](../../.claude/CLAUDE.md) - Project overview

### Related Priorities

- **PRIORITY 3**: Autonomous Development Daemon (foundation)
- **PRIORITY 2**: Project Manager CLI (status commands)
- **PRIORITY 1**: Analytics & Observability (metrics tracking)

---

## Quick Reference Card

```bash
# Daily Commands
poetry run project-manager dev-report              # Yesterday's work
poetry run project-manager chat                    # Chat with auto-standup
poetry run project-manager developer-status        # Current status

# Weekly/Historical
poetry run project-manager dev-report --days 7     # Last week
poetry run project-manager dev-report --days 30    # Last month

# Daemon Management
poetry run code-developer --auto-approve           # Start daemon
poetry run project-manager status                  # Check daemon status
```

---

**Last Updated**: 2025-10-18
**Status**: ✅ Complete
**Version**: 1.0
