# Scheduled Activity Reports Setup

This guide explains how to set up automated activity reports at 2AM, 4AM, and 6AM.

---

## Quick Setup (Using Cron)

### 1. Edit Your Crontab

```bash
crontab -e
```

### 2. Add These Lines

**Replace `/path/to/MonolithicCoffeeMakerAgent` with your actual project path**:

```cron
# Activity reports at 2AM, 4AM, 6AM
0 2 * * * cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent && /Users/bobain/Library/Caches/pypoetry/virtualenvs/coffee-maker-efk4LJvC-py3.11/bin/python scripts/scheduled_activity_report.py >> logs/scheduled_reports.log 2>&1
0 4 * * * cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent && /Users/bobain/Library/Caches/pypoetry/virtualenvs/coffee-maker-efk4LJvC-py3.11/bin/python scripts/scheduled_activity_report.py >> logs/scheduled_reports.log 2>&1
0 6 * * * cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent && /Users/bobain/Library/Caches/pypoetry/virtualenvs/coffee-maker-efk4LJvC-py3.11/bin/python scripts/scheduled_activity_report.py >> logs/scheduled_reports.log 2>&1
```

### 3. Save and Exit

- In vim: Press `Esc`, then type `:wq` and press `Enter`
- In nano: Press `Ctrl+O`, then `Enter`, then `Ctrl+X`

### 4. Verify Cron Jobs

```bash
crontab -l
```

You should see the three lines you just added.

---

## What Happens

**Every 2 hours (2AM, 4AM, 6AM)**:
1. Script runs automatically
2. Generates activity report for last 2 hours
3. Saves report to `evidence/activity-summary-YYYYMMDD-HHMMSS.md`
4. Creates notification in database
5. Logs output to `logs/scheduled_reports.log`

---

## Manual Test

**Test the script manually**:

```bash
# Make sure you're in the project directory
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent

# Run the script
poetry run python scripts/scheduled_activity_report.py
```

**Expected output**:
```
[2025-10-20 23:45:00] Generating scheduled activity report...
[2025-10-20 23:45:01] ✅ Activity report generated successfully
[2025-10-20 23:45:01] Report saved to evidence/
[2025-10-20 23:45:01] Notification created for user
```

---

## View Generated Reports

**Check evidence directory**:

```bash
ls -la evidence/activity-summary-*.md
```

**View latest report**:

```bash
cat evidence/activity-summary-*.md | tail -100
```

---

## View Notifications

**Check notifications database**:

```bash
poetry run project-manager notifications
```

---

## Disable Scheduled Reports

**Remove cron jobs**:

```bash
# Edit crontab
crontab -e

# Delete the three lines or comment them out with #
# Save and exit
```

---

## Troubleshooting

### Reports Not Generating

**Check cron log**:
```bash
cat logs/scheduled_reports.log
```

**Check if cron is running**:
```bash
ps aux | grep cron
```

**Verify Python path**:
```bash
poetry env info --path
# Use this path in your cron command
```

### Permission Errors

**Make script executable**:
```bash
chmod +x scripts/scheduled_activity_report.py
```

### Database Locked

If you see "database is locked" errors, it means another process is using the database. This is normal - cron will retry on the next schedule.

---

## Alternative: systemd Timer (Linux)

If you're on Linux and prefer systemd timers over cron:

### 1. Create service file

**File: `~/.config/systemd/user/activity-report.service`**

```ini
[Unit]
Description=MonolithicCoffeeMaker Activity Report

[Service]
Type=oneshot
WorkingDirectory=/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent
ExecStart=/Users/bobain/Library/Caches/pypoetry/virtualenvs/coffee-maker-efk4LJvC-py3.11/bin/python scripts/scheduled_activity_report.py
```

### 2. Create timer file

**File: `~/.config/systemd/user/activity-report.timer`**

```ini
[Unit]
Description=Run activity report at 2AM, 4AM, 6AM

[Timer]
OnCalendar=*-*-* 02:00:00
OnCalendar=*-*-* 04:00:00
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### 3. Enable and start timer

```bash
systemctl --user enable activity-report.timer
systemctl --user start activity-report.timer
```

### 4. Check status

```bash
systemctl --user status activity-report.timer
```

---

## CLI Command (On Demand)

**Generate report manually anytime**:

```bash
# Generate for last 6 hours
poetry run orchestrator activity-summary

# Generate for last 2 hours
poetry run orchestrator activity-summary --hours 2

# Save to file + create notification
poetry run orchestrator activity-summary --save
```

---

**Related Documentation**:
- `.claude/skills/orchestrator/activity-summary/SKILL.md` - Skill documentation
- `coffee_maker/orchestrator/activity_summary.py` - Implementation

---

**Last Updated**: 2025-10-20
