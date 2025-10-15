# Daily Standup Guide - code_developer Communication

**PRIORITY 9: Enhanced code_developer Communication & Daily Standup**

This guide explains how to use the daily standup and communication features of the `code_developer` autonomous agent.

---

## Table of Contents

1. [Overview](#overview)
2. [Daily Standup Reports](#daily-standup-reports)
3. [CLI Commands](#cli-commands)
4. [Report Format](#report-format)
5. [Accessing Historical Reports](#accessing-historical-reports)
6. [Integration with project_manager](#integration-with-project_manager)
7. [Configuration](#configuration)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The daily standup system provides **automated, professional status updates** from the `code_developer` daemon, just like a human developer would provide in an agile team.

### Key Features

- **Automatic Generation**: Daily standup reports generated at 9 AM (configurable)
- **Yesterday's Accomplishments**: Complete summary of work done
- **Today's Plan**: What the daemon will work on
- **Metrics**: Commits, PRs, lines of code, test coverage
- **Blockers**: Any issues needing attention
- **Professional Format**: Clear, actionable markdown reports

### Why Daily Standups Matter

1. **Trust Building**: See exactly what the AI accomplished each day
2. **Progress Tracking**: Understand momentum and velocity
3. **Early Warning**: Identify blockers before they become problems
4. **Team Integration**: AI acts like a professional team member
5. **Historical Record**: Track accomplishments over time

---

## Daily Standup Reports

### What's Included

Each daily standup report contains:

1. **📊 Yesterday's Accomplishments**
   - Priorities completed
   - Features implemented
   - Bugs fixed
   - Documentation created
   - Commits and file changes

2. **📈 Metrics**
   - Total commits
   - Pull requests created
   - Lines of code (added/deleted)
   - Build status
   - Test coverage change

3. **🔄 Today's Plan**
   - Next priorities to work on
   - Estimated tasks
   - Goals for the day

4. **⚠️ Blockers & Needs**
   - Issues requiring manual intervention
   - Questions for the user
   - Dependencies needed

5. **💬 Notes**
   - Additional context
   - Observations
   - Recommendations

### When Reports Are Generated

By default, reports are generated:
- **Time**: 9:00 AM (local time, configurable)
- **Frequency**: Daily (Monday-Friday by default)
- **Location**: `reports/daily/standup-YYYY-MM-DD.md`

---

## CLI Commands

### View Developer Status (Real-Time)

```bash
# One-time status check
poetry run project-manager developer-status

# Watch mode (updates every 5 seconds)
poetry run project-manager developer-status --watch

# Custom refresh interval
poetry run project-manager developer-status --watch --interval 10
```

**Example Output:**
```
┌─────────────────── Developer Status Dashboard ────────────────────┐
│         State: 🟢 WORKING                                          │
│          Task: PRIORITY 9 - Enhanced Communication                 │
│      Progress: ██████████████░░░░░░ 60%                           │
│          Step: Creating daily standup generator                    │
│           ETA: 2h 15m                                              │
│    Last Event: 2025-10-12 18:42:35                                │
│                Created file: daily_standup.py                      │
├────────────────────────────────────────────────────────────────────┤
│ Recent Activity (last 30 minutes):                                │
│   18:42:35  file_created      Created: daily_standup.py           │
│   18:35:20  test_run          Running: pytest tests/communication │
│   18:30:15  git_commit        Committed: "feat: Add standup gen"  │
├────────────────────────────────────────────────────────────────────┤
│ Today's Metrics:                                                   │
│   Tasks Completed: 0     Tests Passed: 24                          │
│   Total Commits: 3       Tests Failed: 0                           │
└────────────────────────────────────────────────────────────────────┘
```

### View Daily Standup Report

```bash
# View today's standup
poetry run project-manager dev report daily

# View specific date
poetry run project-manager dev report daily 2025-10-11

# View yesterday
poetry run project-manager dev report daily yesterday
```

### View Weekly Summary

```bash
# View current week's summary
poetry run project-manager dev report weekly

# View specific week (ISO week number)
poetry run project-manager dev report weekly 2025-W41
```

### View Sprint Review

```bash
# View current sprint
poetry run project-manager dev report sprint

# View specific sprint
poetry run project-manager dev report sprint 2025-10
```

### Historical Reports

```bash
# List all available reports
poetry run project-manager dev history

# Search reports by date range
poetry run project-manager dev history --since 2025-10-01 --until 2025-10-12

# Search reports by keyword
poetry run project-manager dev history --keyword "GCP deployment"
```

---

## Report Format

### Daily Standup Template

```markdown
🤖 code_developer Daily Standup - 2025-10-12
================================================

📊 Yesterday's Accomplishments (2025-10-11):
✅ Completed PRIORITY 6.5 - GCP Deployment Documentation
   - Created docs/GCP_DEPLOYMENT_GUIDE.md (860 lines)
   - Created docs/GCP_SETUP.md (767 lines)
   - Created docs/OPERATIONS_RUNBOOK.md (1074 lines)
   - Created docs/TROUBLESHOOTING_GCP.md (1007 lines)
   - Commits: 1 | Files changed: 5 | Lines added: 3,735

✅ Fixed agent scope overlaps (Issue: tighten-scopes)
   - Updated .claude/CLAUDE.md with tool ownership matrix
   - Updated 3 agent configuration files
   - Commits: 1 | Tests: All passing

📈 Metrics:
   - Total commits: 2
   - Total PRs created: 0
   - Lines of code: +3,906 / -72
   - Build status: ✅ Passing
   - Test coverage: 87% (+0%)

🔄 Today's Plan (2025-10-12):
1. Start PRIORITY 9 - Enhanced Communication & Daily Standup
2. Create technical specification document
3. Design communication module architecture
4. Implement daily standup generator

⚠️ Blockers & Needs:
   - None currently

💬 Notes:
   - Documentation priorities completed successfully
   - Ready to start implementing communication features

---
Report generated: 2025-10-12 09:00:00
Total active days: 45 | Sprint: Week 7
```

---

## Accessing Historical Reports

### Report Storage

Reports are stored in:
- **Daily Reports**: `reports/daily/standup-YYYY-MM-DD.md`
- **Weekly Reports**: `reports/weekly/summary-YYYY-WNN.md`
- **Sprint Reports**: `reports/sprint/review-YYYY-MM.md`

### Retention Policy

- **Daily Reports**: 90 days (configurable)
- **Weekly Reports**: 1 year (configurable)
- **Sprint Reports**: Indefinite

### Exporting Reports

```bash
# Export all reports to PDF
poetry run project-manager dev export --format pdf --output reports.pdf

# Export specific date range to CSV
poetry run project-manager dev export --since 2025-10-01 --format csv

# Export to JSON for analysis
poetry run project-manager dev export --format json --output metrics.json
```

---

## Integration with project_manager

### Morning Greeting with Daily Update

When you start a new day with `user-listener`, the system automatically detects it's a new day and presents the daily standup **before** starting the conversation:

```bash
$ poetry run user-listener

🤖 project-manager: Good morning! Before we start, here's what
   code_developer accomplished yesterday:

📊 Daily Update - 2025-10-11:
✅ Completed PRIORITY 6.5 - GCP Deployment Documentation
   - Created 4 comprehensive documentation files
   - Added 3,735 lines of documentation
   - All tests passing | Coverage: 87%
   - Commits: 2 | PRs: 0

🔄 Current Status:
   - Working on PRIORITY 9 - Enhanced Communication (60% complete)
   - ETA: 2-3 hours remaining

⚠️ Needs Your Attention:
   - None currently

Now, how can I help you today?

>
```

### Smart Detection

The project manager detects when it's a "new day":
- First interaction after midnight
- More than 12 hours since last chat
- Explicit request: `user-listener --daily-update`

### Disable Auto-Updates

If you don't want automatic daily updates:

```bash
# Disable in config
poetry run project-manager dev config set daily_update.auto false

# Or use flag
poetry run user-listener --no-daily-update
```

---

## Configuration

### Config File Location

`~/.config/coffee-maker/communication.yaml`

### Example Configuration

```yaml
communication:
  daily_standup:
    enabled: true
    time: "09:00"              # Local time (24-hour format)
    timezone: "America/New_York"
    days:                      # Days to generate reports
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
    channels:
      - terminal               # Display in terminal
      - file                   # Save to file
      # Optional channels:
      # - slack: "webhook_url"
      # - email: "your@email.com"

  weekly_summary:
    enabled: true
    day: "friday"
    time: "17:00"

  realtime_updates:
    enabled: true
    milestones: true           # Notify on major milestones
    blockers: true             # Notify immediately on blockers
    questions: true            # Ask for user input when needed
    quiet_hours:
      start: "22:00"
      end: "08:00"

  report_retention:
    daily_days: 90             # Keep 90 days of daily reports
    weekly_days: 365           # Keep 1 year of weekly reports
    sprint_days: -1            # Keep all sprint reports

  verbosity: "normal"          # minimal | normal | verbose

# Output paths
paths:
  reports_dir: "reports/"
  daily_dir: "reports/daily/"
  weekly_dir: "reports/weekly/"
  sprint_dir: "reports/sprint/"
```

### CLI Configuration

```bash
# Set standup time
poetry run project-manager dev config set daily_standup.time "08:30"

# Set timezone
poetry run project-manager dev config set daily_standup.timezone "America/Los_Angeles"

# Enable Slack notifications
poetry run project-manager dev config set daily_standup.channels.slack "https://hooks.slack.com/..."

# Set verbosity
poetry run project-manager dev config set verbosity "verbose"

# View current config
poetry run project-manager dev config show
```

---

## Examples

### Example 1: Morning Routine

```bash
# Start your day
$ poetry run user-listener

# System automatically shows daily standup
# You see what was accomplished yesterday
# You understand today's plan
# You're ready to engage with the project
```

### Example 2: Check Status During Day

```bash
# See what's happening right now
$ poetry run project-manager developer-status

# Output shows current task, progress, recent activities
# You understand exactly where the daemon is in its work
```

### Example 3: Weekly Review on Friday

```bash
# Friday afternoon - check weekly summary
$ poetry run project-manager dev report weekly

# See full week's accomplishments
# Review velocity and metrics
# Understand next week's goals
```

### Example 4: Historical Analysis

```bash
# How much progress in October?
$ poetry run project-manager dev history --since 2025-10-01 --until 2025-10-31

# Export to CSV for analysis
$ poetry run project-manager dev export --since 2025-10-01 --format csv --output october.csv

# Analyze in spreadsheet or Python
# Track trends, velocity, productivity
```

---

## Troubleshooting

### Problem: No Daily Report Generated

**Symptoms**: Expected daily report at 9 AM, but none appeared

**Solutions**:

1. Check daemon is running:
   ```bash
   poetry run project-manager status
   ```

2. Check configuration:
   ```bash
   poetry run project-manager dev config show
   ```

3. Manually generate report:
   ```bash
   poetry run project-manager dev report daily --force
   ```

4. Check logs:
   ```bash
   tail -f data/logs/daemon.log
   ```

### Problem: Metrics Seem Inaccurate

**Symptoms**: Commit count or lines changed don't match reality

**Solutions**:

1. Verify git history:
   ```bash
   git log --since="yesterday" --author="Claude" --oneline
   ```

2. Check daemon's git configuration:
   ```bash
   git config user.name
   git config user.email
   ```

3. Regenerate metrics:
   ```bash
   poetry run project-manager dev report daily --recalculate
   ```

### Problem: Reports Are Too Verbose

**Symptoms**: Daily standup is too long or detailed

**Solutions**:

1. Set minimal verbosity:
   ```bash
   poetry run project-manager dev config set verbosity "minimal"
   ```

2. Use summary view:
   ```bash
   poetry run project-manager dev report daily --summary-only
   ```

3. Customize template (advanced):
   ```bash
   # Edit template in:
   coffee_maker/autonomous/communication/report_templates.py
   ```

### Problem: Daemon Status Shows "STOPPED"

**Symptoms**: `developer-status` shows daemon not running

**Solutions**:

1. Start daemon:
   ```bash
   poetry run code-developer --auto-approve
   ```

2. Check for errors:
   ```bash
   poetry run code-developer --verbose
   ```

3. Check system resources:
   ```bash
   # Check if daemon crashed
   poetry run project-manager notifications
   # Look for crash notifications
   ```

---

## Integration with Workflow

### Daily Workflow

**Morning (9:00 AM)**:
1. Daemon generates daily standup
2. Report saved to `reports/daily/`
3. Optional: Slack notification sent

**When You Check In**:
1. Run `user-listener`
2. See automatic daily update
3. Understand status immediately
4. Engage with project

**During Day**:
1. Run `developer-status --watch` in separate terminal
2. Monitor real-time progress
3. See milestones as they happen

**End of Day**:
1. Daemon logs final activities
2. Metrics calculated and stored
3. Ready for tomorrow's standup

### Weekly Workflow

**Friday (5:00 PM)**:
1. Daemon generates weekly summary
2. Review week's accomplishments
3. Understand velocity and trends
4. Plan next week

### Sprint Workflow

**End of Sprint**:
1. Daemon generates sprint review
2. Comprehensive metrics for sprint
3. Compare to previous sprints
4. Identify improvements

---

## Advanced Features

### Custom Report Queries

```bash
# Find all days with >10 commits
poetry run project-manager dev history --filter "commits > 10"

# Find blockers in last month
poetry run project-manager dev history --since 30d --filter "blockers.count > 0"

# Find high-velocity weeks
poetry run project-manager dev history --weekly --filter "velocity > 20"
```

### API Access

```python
from coffee_maker.autonomous.communication import DailyStandupGenerator

# Generate report programmatically
generator = DailyStandupGenerator()
report = generator.generate_report(date="2025-10-12")

print(report.accomplishments)
print(report.metrics)
print(report.blockers)
```

### Notification Customization

```yaml
# Custom Slack template
notifications:
  slack:
    template: |
      :robot: *Daily Update - {date}*

      *Yesterday's Wins:*
      {accomplishments}

      *Today's Plan:*
      {todays_plan}

      *Status:* {status_emoji}
    webhook_url: "https://hooks.slack.com/..."
```

---

## Best Practices

### 1. Review Daily Standups Regularly

Make it part of your morning routine:
```bash
# Add to your shell startup (~/.zshrc or ~/.bashrc)
alias morning="poetry run user-listener"
```

### 2. Use Watch Mode During Active Development

Keep a terminal open with:
```bash
poetry run project-manager developer-status --watch
```

### 3. Weekly Reviews

Every Friday, review the weekly summary:
```bash
poetry run project-manager dev report weekly
```

### 4. Track Trends

Export historical data monthly:
```bash
poetry run project-manager dev export --since 30d --format csv --output $(date +%Y-%m).csv
```

### 5. Share Reports

Share daily standups with team:
- Enable Slack integration
- Email reports to stakeholders
- Include in sprint reviews

---

## Related Documentation

- [PRIORITY_9_TECHNICAL_SPEC.md](PRIORITY_9_TECHNICAL_SPEC.md) - Technical specification
- [PRIORITY_9_COMMUNICATION_GUIDE.md](PRIORITY_9_COMMUNICATION_GUIDE.md) - Complete guide
- [COMMUNICATION_CONFIG_GUIDE.md](COMMUNICATION_CONFIG_GUIDE.md) - Configuration reference
- [STANDUP_EXAMPLES.md](STANDUP_EXAMPLES.md) - Real-world examples

---

## Support

For issues or questions:

1. **Documentation**: Check [ROADMAP.md](ROADMAP.md) PRIORITY 9 section
2. **GitHub Issues**: Report bugs at https://github.com/your-repo/issues
3. **Community**: Join discussions in GitHub Discussions
4. **Direct Help**: Run `poetry run user-listener` and ask!

---

**Version**: 1.0
**Last Updated**: 2025-10-12
**Status**: ✅ Complete - Ready to use
