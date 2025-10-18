# Daily Standup Quick Start Guide

**Get started with code_developer daily standup reports in 5 minutes!**

## What You'll Learn

- How to view yesterday's work in 1 command
- How to get automatic standups in chat
- How to check current daemon status
- How activity tracking works behind the scenes

---

## 1. View Yesterday's Work (30 seconds)

**Command**:
```bash
poetry run project-manager dev-report
```

**What You'll See**:
```
╭──────────────────────────── 📊 DEVELOPER REPORT ─────────────────────────────╮
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃               🤖 code_developer Daily Report - 2025-10-18                ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                                                              │
│ ============================================================                 │
│                                                                              │
│                       📊 Yesterday's Work (2025-10-17)                       │
│                                                                              │
│                    ✅ PRIORITY 9: Communication System                       │
│                                                                              │
│  • Implemented activity tracking database                                    │
│  • Created standup generator with AI summaries                               │
│  • Integrated with chat interface                                            │
│    Commits: 5 Files: 12 modified Lines: +850 / -45                           │
│                                                                              │
│                               📈 Overall Stats                               │
│                                                                              │
│  • Total Commits: 5                                                          │
│  • Files Modified: 12                                                        │
│  • Lines Added: +850                                                         │
│  • Lines Removed: -45                                                        │
│                                                                              │
│                               🔄 Today's Focus                               │
│                                                                              │
│  • PRIORITY 9: Documentation                                                 │
│    Progress: 80%                                                             │
│                                                                              │
│                                 ✅ Blockers                                  │
│                                                                              │
│ None                                                                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**That's it!** You now see exactly what `code_developer` accomplished yesterday.

---

## 2. Start Your Day with Automatic Standup (1 minute)

**Command**:
```bash
poetry run project-manager chat
```

**What Happens**:

1. **First chat of the day** (>12 hours since last chat):
   ```
   Generating daily standup report...

   🤖 code_developer Daily Report - 2025-10-18
   ============================================================

   [Full standup report shows here automatically]

   Now, how can I help you today?

   > _
   ```

2. **Subsequent chats** (same day):
   ```
   Now, how can I help you today?

   > _
   ```
   (Standup skipped - you already saw it this morning!)

**Why This Is Awesome**:
- No need to remember to check standup
- Natural conversation flow
- Context-aware: shows standup when you need it, skips when you don't

---

## 3. Check What's Happening Right Now (30 seconds)

**Command**:
```bash
poetry run project-manager developer-status
```

**What You'll See**:
```
╭────────────────────────── 🤖 DEVELOPER STATUS ──────────────────────────────╮
│ Current Priority: PRIORITY 9                                                 │
│ Status: working                                                              │
│ Progress: 80%                                                                │
│ Last Activity: 2025-10-18 17:30:00                                           │
│ Current Step: Creating documentation                                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**Use Case**: Quick check on what the daemon is doing without interrupting it.

---

## 4. Review Last Week's Progress (1 minute)

**Command**:
```bash
poetry run project-manager dev-report --days 7
```

**What You'll See**:
- All commits from the past 7 days
- Aggregated statistics
- Multiple priorities if worked on several
- Total lines added/removed across the week

**Use Case**: Weekly sprint reviews, progress tracking, velocity metrics.

---

## 5. How It Works Behind the Scenes

### Activity Tracking

Every time `code_developer` daemon does something, it logs an activity:

```python
# Example: Daemon creates a commit
db.log_activity(
    activity_type="commit",
    title="feat: Implement authentication system",
    priority_number="2.5",
    priority_name="Security Enhancements",
    metadata={
        "commit_hash": "abc123",
        "files_changed": 5,
        "lines_added": 120,
        "lines_removed": 30
    }
)
```

### AI-Powered Summaries

The system uses Claude API to generate intelligent summaries:

```
Raw Activities (database)
    ↓
StandupGenerator (Claude API)
    ↓
Professional Markdown Report
    ↓
CLI Display / Chat
```

**Benefits**:
- Human-readable narratives (not just raw data)
- Highlights business value
- Focuses on impact
- Professional formatting

### Database Storage

All activities stored in SQLite:
- **Location**: `data/activity_tracking.db`
- **Tables**: `activities`, `daily_summaries`, `activity_stats`
- **Concurrent access**: WAL mode enabled
- **Fast queries**: Indexed by date, type, priority

---

## 6. Common Usage Patterns

### Morning Routine
```bash
# Option 1: Explicit standup check
poetry run project-manager dev-report

# Option 2: Chat (automatic standup)
poetry run project-manager chat
```

### Quick Status Check
```bash
# What's the daemon working on right now?
poetry run project-manager developer-status
```

### Weekly Review (Friday afternoon)
```bash
# See the whole week's progress
poetry run project-manager dev-report --days 7
```

### Monthly Review
```bash
# See the whole month's progress
poetry run project-manager dev-report --days 30
```

---

## 7. Real Example: Typical Day

**8:00 AM** - Start your day:
```bash
$ poetry run project-manager chat
```
```
Generating daily standup report...

🤖 code_developer Daily Report - 2025-10-18
============================================================

📊 Yesterday's Work (2025-10-17)

✅ PRIORITY 7: Multi-Model Code Review Agent
  • Implemented core reviewer system
  • Added perspective-based analysis
  • Created markdown report generator
  Commits: 8 Files: 24 modified Lines: +1250 / -120

✅ Bug Fixes
  • Fixed rate limiting in API calls
  Commits: 1 Files: 2 modified Lines: +15 / -8

📈 Overall Stats
  • Total Commits: 9
  • Files Modified: 26
  • Lines Added: +1265
  • Lines Removed: -128

🔄 Today's Focus
  • PRIORITY 7: Testing and documentation
    Progress: 60%

✅ Blockers
None

────────────────────────────────────────────────────────────

Now, how can I help you today?

>
```

You type:
```
> What tests are missing for the code review agent?
```

AI responds with detailed analysis...

**12:00 PM** - Quick check:
```bash
$ poetry run project-manager developer-status
```
```
Current Priority: PRIORITY 7
Status: working
Progress: 75%
Last Activity: 2025-10-18 11:45:00
Current Step: Writing integration tests
```

**5:00 PM** - End of day review:
```bash
$ poetry run project-manager chat
```
```
Now, how can I help you today?

> Give me a summary of what you accomplished today
```

(Chat skips standup since you already saw it this morning, but you can ask for current status anytime!)

---

## 8. Troubleshooting

### No Activities Shown

**Problem**: Report shows "No activities recorded"

**Solution**:
```bash
# Check if daemon is running
poetry run project-manager status

# Start daemon if not running
poetry run code-developer --auto-approve
```

### Standup Not Generated

**Problem**: Chat doesn't show standup

**Possible Causes**:
1. **Already shown today** (expected behavior)
2. **Anthropic API key not set**

**Solution**:
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Set if missing
export ANTHROPIC_API_KEY="sk-ant-..."

# Or use explicit command
poetry run project-manager dev-report
```

### Database Errors

**Problem**: "Database is locked" errors

**Solution**:
- System has automatic retry protection
- If persists, check for zombie processes:
  ```bash
  ps aux | grep code-developer
  kill <PID if needed>
  ```

---

## 9. What Gets Tracked

| Activity Type | What It Captures |
|---------------|------------------|
| **Commits** | Hash, files changed, lines added/removed |
| **PRs Created** | PR number, URL, branch name |
| **Tests Run** | Tests passed/failed, coverage % |
| **Priority Started** | Priority number, name, timestamp |
| **Priority Completed** | Priority number, name, duration |
| **Errors** | Error type, message, stack trace |
| **Documentation** | Files updated, sections added |
| **Dependencies** | Package name, version |

---

## 10. Next Steps

Now that you know the basics:

1. **Read the Full Guide**: [CODE_DEVELOPER_COMMUNICATION.md](./CODE_DEVELOPER_COMMUNICATION.md)
2. **Explore Activity Tracking**: [ACTIVITY_TRACKING_QUICKSTART.md](./ACTIVITY_TRACKING_QUICKSTART.md)
3. **Check the ROADMAP**: [ROADMAP.md](../roadmap/ROADMAP.md) - See PRIORITY 9 details
4. **Review Implementation**: Check `coffee_maker/autonomous/standup_generator.py`

---

## Quick Reference

```bash
# Daily standup
poetry run project-manager dev-report

# Chat with auto-standup
poetry run project-manager chat

# Current status
poetry run project-manager developer-status

# Weekly review
poetry run project-manager dev-report --days 7

# Monthly review
poetry run project-manager dev-report --days 30
```

---

**That's all you need to get started!** 🎉

The system is designed to be **zero-configuration** and **automatic**. Just run the daemon, and it will track everything for you. Check the standup each morning to see what got done!

---

**Last Updated**: 2025-10-18
**Related**: CODE_DEVELOPER_COMMUNICATION.md, ACTIVITY_TRACKING_QUICKSTART.md
