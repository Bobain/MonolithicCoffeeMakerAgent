# Summary & Calendar Tutorial - US-017

**Complete Guide to Proactive Status Updates and Delivery Calendars**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Multi-Channel Delivery](#multi-channel-delivery)
7. [API Reference](#api-reference)
8. [FAQ](#faq)

---

## Overview

US-017 provides proactive status reporting with two main features:

1. **Executive Summary** - Recent completions (last N days) with business value
2. **Delivery Calendar** - Upcoming priorities with estimated completion dates

### Key Benefits

- **Reduce status questions** - Stakeholders get updates automatically
- **Better visibility** - See what's been delivered and what's coming
- **Multi-channel delivery** - Console, Slack, email (stub)
- **Auto-maintained** - Updates automatically from ROADMAP.md

### Components

```
ROADMAP.md
    ↓
StatusReportGenerator (parse & format)
    ↓
NotificationDispatcher (multi-channel delivery)
    ↓
[Console] [Slack] [Email]
```

---

## Quick Start

### 1. Generate Summary (Console)

```python
from coffee_maker.reports.status_report_generator import StatusReportGenerator

# Initialize generator
generator = StatusReportGenerator("docs/ROADMAP.md")

# Get recent completions
completions = generator.get_recent_completions(days=14)

# Format as executive summary
summary = generator.format_delivery_summary(completions)
print(summary)
```

**Output**:
```
# Recent Deliveries Summary

Period: Last 14 days
Total Deliveries: 3

---

## US-016: Technical Spec Generation

**Completed**: 2025-10-15

**Business Value**: Accurate delivery estimates before coding starts

**Key Features**:
- AI-assisted task breakdown
- 100 tests passing
- Integration with ROADMAP

---
```

### 2. Generate Calendar (Console)

```python
# Get upcoming deliverables
upcoming = generator.get_upcoming_deliverables(limit=5)

# Format as calendar report
calendar = generator.format_calendar_report(upcoming)
print(calendar)
```

**Output**:
```
# Upcoming Deliverables Calendar

Next 5 Priorities

---

## 1. US-017: Summary & Calendar

**Estimated**: 5-7 days (completing by 2025-10-27)

**What**: Proactive delivery summaries and calendar

**Impact**: Better visibility, reduced status questions

---
```

### 3. Auto-Update STATUS_TRACKING.md

```python
from coffee_maker.reports.status_tracking_updater import update_status_tracking

# Update document automatically
success = update_status_tracking(
    roadmap_path="docs/ROADMAP.md",
    output_path="docs/STATUS_TRACKING.md",
    days=14,
    upcoming_count=5
)

print(f"Update {'succeeded' if success else 'failed'}")
```

---

## Features

### 1. Executive Summary (Recent Completions)

**What it shows**:
- Story ID and title
- Completion date
- Business value delivered
- Key features delivered
- Estimation accuracy (if available)

**Example**:
```python
completions = generator.get_recent_completions(days=14)

for completion in completions:
    print(f"{completion.story_id}: {completion.title}")
    print(f"  Completed: {completion.completion_date}")
    print(f"  Business Value: {completion.business_value}")
    print(f"  Features: {', '.join(completion.key_features[:3])}")

    if completion.estimated_days and completion.actual_days:
        accuracy = 100 - abs(completion.actual_days - completion.estimated_days) / completion.estimated_days * 100
        print(f"  Accuracy: {accuracy:.1f}%")
```

### 2. Delivery Calendar (Upcoming Work)

**What it shows**:
- Priority order (1, 2, 3...)
- Estimated time range (min-max days)
- Estimated completion date
- What description (user story)
- Impact statement

**Example**:
```python
upcoming = generator.get_upcoming_deliverables(limit=5)

for idx, story in enumerate(upcoming, 1):
    print(f"{idx}. {story.story_id}: {story.title}")
    print(f"   Estimated: {story.estimated_min_days}-{story.estimated_max_days} days")
    print(f"   Completion: {story.estimated_completion_date.strftime('%Y-%m-%d')}")
    print(f"   What: {story.what_description}")
    print(f"   Impact: {story.impact_statement}")
```

### 3. Auto-Maintained STATUS_TRACKING.md

**Features**:
- Auto-generated from ROADMAP.md
- Recent completions (last N days)
- Current work in progress
- Next up priorities
- Velocity & accuracy metrics

**Update Triggers**:
- Story starts (status → In Progress)
- Story completes (status → Complete)
- Progress updates
- Manual update requested

**Example**:
```python
# Hook: Called when story completes
from coffee_maker.reports.status_tracking_updater import on_story_completed

on_story_completed("US-017")
```

### 4. Automatic Updates (Scheduled)

**Smart scheduling**:
- Updates every 3 days (configurable)
- Updates on significant estimate changes (>1 day)
- Tracks update history

**Example**:
```python
from coffee_maker.reports.status_tracking_updater import check_and_update_if_needed

result = check_and_update_if_needed()

if result['updated']:
    print(f"Updated: {result['reason']}")
else:
    print(f"Skipped: {result['reason']}")
```

---

## Configuration

### Notification Preferences

Configuration file: `~/.coffee_maker/notification_preferences.json`

**Default Configuration**:
```json
{
  "channels": ["console"],
  "slack_enabled": false,
  "email_enabled": false,
  "auto_update_enabled": true,
  "update_interval_days": 3,
  "slack_webhook_url": null,
  "email_recipients": []
}
```

### Enable Slack Notifications

```python
from coffee_maker.reports.notification_dispatcher import NotificationDispatcher

dispatcher = NotificationDispatcher()

# Configure Slack
dispatcher.update_config(
    slack_enabled=True,
    slack_webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    channels=["console", "slack"]
)

# Test connection
results = dispatcher.test_channels()
print(f"Slack: {'✓' if results['slack'] else '✗'}")
```

### Configure Update Interval

```python
dispatcher.update_config(
    auto_update_enabled=True,
    update_interval_days=7  # Update weekly instead of every 3 days
)
```

---

## Usage Examples

### Example 1: Manual Summary Report

```python
from coffee_maker.reports.status_report_generator import StatusReportGenerator

# Generate summary for last 30 days
generator = StatusReportGenerator("docs/ROADMAP.md")
completions = generator.get_recent_completions(days=30)

print(f"✅ {len(completions)} stories completed in last 30 days")
for completion in completions:
    print(f"  - {completion.story_id}: {completion.title}")
```

### Example 2: Send Summary to Slack

```python
from coffee_maker.reports.notification_dispatcher import NotificationDispatcher
from coffee_maker.reports.status_report_generator import StatusReportGenerator

# Generate data
generator = StatusReportGenerator("docs/ROADMAP.md")
completions = generator.get_recent_completions(days=14)

# Dispatch to Slack
dispatcher = NotificationDispatcher()
results = dispatcher.dispatch_summary(completions, period_days=14)

print(f"Slack: {'✓' if results.get('slack') else '✗'}")
```

### Example 3: Full Workflow with Notifications

```python
from coffee_maker.reports.status_tracking_updater import update_status_tracking
from coffee_maker.reports.notification_dispatcher import NotificationDispatcher

# Configure dispatcher
dispatcher = NotificationDispatcher()
dispatcher.update_config(
    slack_enabled=True,
    slack_webhook_url="https://hooks.slack.com/...",
    channels=["console", "slack"]
)

# Update with notifications
success = update_status_tracking(
    roadmap_path="docs/ROADMAP.md",
    output_path="docs/STATUS_TRACKING.md",
    days=14,
    upcoming_count=5,
    send_notifications=True,
    dispatcher=dispatcher
)

print(f"Update: {'✓' if success else '✗'}")
```

### Example 4: Check Update Status

```python
from coffee_maker.reports.update_scheduler import UpdateScheduler

scheduler = UpdateScheduler(roadmap_path="docs/ROADMAP.md")

# Check if update needed
should_update = scheduler.should_update()
print(f"Update needed: {should_update}")

# Get time since last update
time_since = scheduler.get_time_since_last_update()
if time_since:
    print(f"Last updated: {time_since.days} days ago")
```

### Example 5: Velocity Metrics

```python
from coffee_maker.reports.status_report_generator import StatusReportGenerator

generator = StatusReportGenerator("docs/ROADMAP.md")
completions = generator.get_recent_completions(days=30)

# Calculate metrics
metrics = generator._calculate_velocity_metrics(completions)

print(f"Stories completed: {metrics['stories_completed']}")
print(f"Average velocity: {metrics['avg_velocity']:.1f} stories/week")

if metrics['avg_accuracy']:
    print(f"Average accuracy: {metrics['avg_accuracy']:.0f}%")
    print(f"Trend: {metrics['trend']}")
```

---

## Multi-Channel Delivery

### Supported Channels

1. **Console** (always enabled)
   - Prints formatted output to stdout
   - Uses emoji and formatting
   - 80-character width

2. **Slack** (configurable)
   - Rich Block Kit formatting
   - Clickable links
   - Channel override support
   - Webhook-based (no app required)

3. **Email** (stub - not yet implemented)
   - Placeholder for future implementation
   - Returns False (not available)

### Channel Selection

```python
from coffee_maker.reports.notification_dispatcher import NotificationDispatcher

dispatcher = NotificationDispatcher()

# Enable specific channels
dispatcher.update_config(
    channels=["console", "slack"],  # Only console and Slack
    slack_enabled=True,
    email_enabled=False
)

# Dispatch to all enabled channels
completions = generator.get_recent_completions(days=14)
results = dispatcher.dispatch_summary(completions, period_days=14)

# Check results
for channel, success in results.items():
    print(f"{channel}: {'✓' if success else '✗'}")
```

### Graceful Fallback

If a channel fails, other channels continue:

```python
# Even if Slack fails, console still works
results = dispatcher.dispatch_summary(completions, period_days=14)

# Results: {'console': True, 'slack': False}
# Console output is still generated!
```

### Slack Block Format

**Summary Message**:
```
┌─────────────────────────────────────┐
│ 📊 Summary - Last 14 Days           │
├─────────────────────────────────────┤
│ 3 stories completed | 12.5 days    │
├─────────────────────────────────────┤
│ US-016: Technical Spec Generation   │
│ • 2025-10-15                        │
│ Accurate delivery estimates...      │
├─────────────────────────────────────┤
│ Generated: 2025-10-16 02:00         │
└─────────────────────────────────────┘
```

**Calendar Message**:
```
┌─────────────────────────────────────┐
│ 📅 Upcoming Deliverables - Next 5   │
├─────────────────────────────────────┤
│ 5 upcoming stories | 25.0 days      │
├─────────────────────────────────────┤
│ 📝 1. US-017: Summary & Calendar    │
│ Estimate: 5.0d                      │
├─────────────────────────────────────┤
│ Generated: 2025-10-16 02:00         │
└─────────────────────────────────────┘
```

---

## API Reference

### StatusReportGenerator

**Initialization**:
```python
generator = StatusReportGenerator(
    roadmap_path="docs/ROADMAP.md",
    velocity_days_per_story=3.5  # Average days per story
)
```

**Methods**:

- `get_recent_completions(days=14)` → `List[StoryCompletion]`
  - Returns completions in last N days
  - Sorted by completion date (newest first)

- `get_upcoming_deliverables(limit=3)` → `List[UpcomingStory]`
  - Returns top N upcoming stories with estimates
  - Excludes completed stories

- `format_delivery_summary(completions)` → `str`
  - Formats completions as executive summary
  - Markdown format

- `format_calendar_report(deliverables)` → `str`
  - Formats upcoming work as calendar
  - Markdown format

- `generate_status_tracking_document(days=14, upcoming_count=5)` → `str`
  - Full STATUS_TRACKING.md content
  - Includes metrics and velocity

### NotificationDispatcher

**Initialization**:
```python
dispatcher = NotificationDispatcher(
    config_path="~/.coffee_maker/notification_preferences.json"
)
```

**Methods**:

- `dispatch_summary(completions, period_days=14)` → `Dict[str, bool]`
  - Sends summary to all enabled channels
  - Returns success status per channel

- `dispatch_calendar(deliverables, limit=5)` → `Dict[str, bool]`
  - Sends calendar to all enabled channels
  - Returns success status per channel

- `dispatch_update(summary_data, calendar_data)` → `Dict`
  - Sends both summary and calendar
  - Convenience method

- `update_config(**kwargs)` → `None`
  - Updates configuration
  - Saves to file

- `get_config()` → `Dict`
  - Returns current configuration
  - Read-only copy

- `test_channels()` → `Dict[str, bool]`
  - Tests all enabled channels
  - Returns test results

### SlackNotifier

**Initialization**:
```python
notifier = SlackNotifier(
    webhook_url="https://hooks.slack.com/..."
)
```

**Methods**:

- `send_summary_to_slack(completions, period_days=14, channel_override=None)` → `bool`
  - Sends summary to Slack
  - Rich Block Kit formatting

- `send_calendar_to_slack(deliverables, limit=5, channel_override=None)` → `bool`
  - Sends calendar to Slack
  - Rich Block Kit formatting

- `test_connection()` → `bool`
  - Tests webhook connection
  - Sends test message

### Data Classes

**StoryCompletion**:
```python
@dataclass
class StoryCompletion:
    story_id: str
    title: str
    completion_date: datetime
    business_value: str
    key_features: List[str]
    estimated_days: Optional[float] = None
    actual_days: Optional[float] = None
```

**UpcomingStory**:
```python
@dataclass
class UpcomingStory:
    story_id: str
    title: str
    estimated_min_days: float
    estimated_max_days: float
    estimated_completion_date: datetime
    what_description: str
    impact_statement: str
```

---

## FAQ

### Q1: How often does STATUS_TRACKING.md update?

**A**: By default, every 3 days or when significant changes occur (>1 day estimate change). You can configure the interval:

```python
dispatcher.update_config(update_interval_days=7)  # Weekly
```

### Q2: Can I send notifications to multiple Slack channels?

**A**: Yes, use `channel_override` parameter:

```python
notifier.send_summary_to_slack(
    completions,
    period_days=14,
    channel_override="#status-updates"
)
```

### Q3: How do I disable auto-updates?

**A**: Set `auto_update_enabled` to `false`:

```python
dispatcher.update_config(auto_update_enabled=False)
```

### Q4: What if my ROADMAP format is different?

**A**: The parser looks for specific patterns:
- `### 🎯 [US-XXX] Title` for user stories
- `## PRIORITY X:` or `## 📝 PLANNED:` for priorities
- `✅ COMPLETE` or `**Status**: Complete` for completions
- `**Completed**: YYYY-MM-DD` for dates

Ensure your ROADMAP follows these patterns.

### Q5: Can I customize the Slack message format?

**A**: Yes, modify `SlackNotifier._build_summary_blocks()` or `_build_calendar_blocks()` methods to change formatting.

### Q6: How do I get email notifications?

**A**: Email is currently a stub. To implement:
1. Choose email provider (SMTP, SendGrid, etc.)
2. Update `NotificationDispatcher._send_summary_email()`
3. Add email configuration to config file

### Q7: What if a story has no estimate?

**A**: Stories without estimates are excluded from the calendar. Only stories with `**Estimated Effort**: X-Y days` are included.

### Q8: How accurate are the estimated completion dates?

**A**: Completion dates are calculated using:
- Average of min/max estimate
- Days from today
- Does NOT account for weekends or holidays (yet)

Future: Will use US-015 velocity metrics for better accuracy.

### Q9: Can I run updates manually?

**A**: Yes:

```python
from coffee_maker.reports.status_tracking_updater import update_status_tracking

update_status_tracking(force=True)  # Force immediate update
```

### Q10: How do I see the notification history?

**A**: Notifications are logged. Check logs:

```python
import logging
logging.getLogger('coffee_maker.reports').setLevel(logging.INFO)
```

---

## Next Steps

1. **Configure Slack** - Set up webhook and test notifications
2. **Customize Intervals** - Adjust update frequency to your needs
3. **Integrate with Daemon** - Have code_developer trigger updates automatically
4. **Add Email** - Implement email notifications for your team

**See Also**:
- `docs/US-017_TECHNICAL_SPEC.md` - Technical specification
- `docs/ROADMAP.md` - Project roadmap
- `coffee_maker/reports/` - Source code

---

**US-017 Complete** ✅

Generated: 2025-10-16
Version: 1.0
