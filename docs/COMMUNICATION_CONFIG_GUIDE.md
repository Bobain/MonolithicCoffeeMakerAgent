# Communication Configuration Guide

**PRIORITY 9: Enhanced code_developer Communication & Daily Standup**

Complete guide to configuring the communication and reporting system for the `code_developer` autonomous agent.

---

## Table of Contents

1. [Overview](#overview)
2. [Configuration File Location](#configuration-file-location)
3. [Configuration Structure](#configuration-structure)
4. [Daily Standup Configuration](#daily-standup-configuration)
5. [Weekly Summary Configuration](#weekly-summary-configuration)
6. [Real-Time Updates Configuration](#real-time-updates-configuration)
7. [Notification Channels](#notification-channels)
8. [Report Retention](#report-retention)
9. [CLI Configuration Commands](#cli-configuration-commands)
10. [Examples](#examples)
11. [Advanced Configuration](#advanced-configuration)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The communication system is highly configurable to match your workflow and preferences. You can configure:

- **When** reports are generated (time, days, frequency)
- **What** is included (verbosity, sections, metrics)
- **Where** reports are sent (terminal, file, Slack, email)
- **How long** reports are retained (retention policies)

### Configuration Methods

1. **YAML File**: `~/.config/coffee-maker/communication.yaml` (recommended)
2. **CLI Commands**: `project-manager dev config` commands
3. **Environment Variables**: For temporary overrides
4. **Code**: Programmatic configuration (advanced)

---

## Configuration File Location

### Default Location

```
~/.config/coffee-maker/communication.yaml
```

### Alternative Locations

```
# Project-specific config (takes precedence)
./.coffee-maker/communication.yaml

# System-wide config
/etc/coffee-maker/communication.yaml

# Custom path via environment variable
export COFFEE_MAKER_CONFIG="/path/to/config.yaml"
```

### Creating Config File

```bash
# Create config directory
mkdir -p ~/.config/coffee-maker

# Create default config
poetry run project-manager dev config init

# Or manually create
cat > ~/.config/coffee-maker/communication.yaml << 'YAML'
communication:
  daily_standup:
    enabled: true
    time: "09:00"
YAML
```

---

## Configuration Structure

### Complete Configuration Schema

```yaml
communication:
  # Daily standup reports
  daily_standup:
    enabled: true
    time: "09:00"
    timezone: "America/New_York"
    days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    channels:
      - terminal
      - file
    format: "markdown"  # markdown | json | html
    sections:
      - accomplishments
      - metrics
      - todays_plan
      - blockers
      - notes
    verbosity: "normal"  # minimal | normal | verbose

  # Weekly summary reports
  weekly_summary:
    enabled: true
    day: "friday"
    time: "17:00"
    channels:
      - terminal
      - file
    include_velocity: true
    compare_previous_weeks: 4  # Compare to last 4 weeks

  # Sprint/milestone reviews
  sprint_review:
    enabled: true
    frequency: "monthly"  # weekly | biweekly | monthly
    day: "last_friday"  # last_friday | first_monday | etc.
    include_retrospective: true

  # Real-time updates
  realtime_updates:
    enabled: true
    milestones: true
    blockers: true
    questions: true
    progress_threshold: 25  # Notify every 25% progress
    quiet_hours:
      start: "22:00"
      end: "08:00"

  # Report retention
  retention:
    daily_days: 90
    weekly_days: 365
    sprint_days: -1  # -1 = keep forever

  # Global settings
  verbosity: "normal"
  timezone: "America/New_York"

# Notification channels
channels:
  terminal:
    enabled: true
    use_colors: true
    use_emojis: true

  file:
    enabled: true
    base_dir: "reports/"
    daily_dir: "reports/daily/"
    weekly_dir: "reports/weekly/"
    sprint_dir: "reports/sprint/"

  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    channel: "#code-developer-updates"
    username: "code_developer"
    icon_emoji: ":robot_face:"

  email:
    enabled: false
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    smtp_user: "your@email.com"
    smtp_password: "${EMAIL_PASSWORD}"  # Use env var
    from_email: "code-developer@yourdomain.com"
    to_emails:
      - "team@yourdomain.com"
      - "manager@yourdomain.com"

# Metrics collection
metrics:
  git:
    enabled: true
    author_filter: ["Claude", "code-developer"]
    exclude_merge_commits: true

  tests:
    enabled: true
    command: "pytest --cov"
    coverage_threshold: 80

  roadmap:
    enabled: true
    roadmap_file: "docs/ROADMAP.md"
    velocity_tracking: true

# Advanced settings
advanced:
  cache_metrics: true
  cache_ttl_seconds: 300  # 5 minutes
  parallel_processing: true
  max_workers: 4
```

---

## Daily Standup Configuration

### Basic Configuration

```yaml
communication:
  daily_standup:
    enabled: true
    time: "09:00"
    timezone: "America/New_York"
```

### Schedule Configuration

```yaml
communication:
  daily_standup:
    time: "09:00"  # 24-hour format
    timezone: "America/New_York"  # See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

    # Days to generate reports
    days:
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
      # Optional: saturday, sunday
```

### Content Configuration

```yaml
communication:
  daily_standup:
    # Control what's included
    sections:
      - accomplishments  # Required
      - metrics         # Required
      - todays_plan     # Optional
      - blockers        # Optional
      - notes           # Optional
      - recommendations # Optional

    # Detail level
    verbosity: "normal"
    # - minimal: Brief summary only
    # - normal: Standard detail
    # - verbose: All details including git diffs
```

### Format Configuration

```yaml
communication:
  daily_standup:
    format: "markdown"  # markdown | json | html

    # For markdown
    markdown:
      use_emojis: true
      use_tables: true
      use_progress_bars: true

    # For JSON
    json:
      indent: 2
      include_metadata: true

    # For HTML
    html:
      template: "templates/standup.html"
      css_file: "templates/styles.css"
```

---

## Weekly Summary Configuration

### Basic Configuration

```yaml
communication:
  weekly_summary:
    enabled: true
    day: "friday"  # monday, tuesday, etc.
    time: "17:00"
```

### Advanced Configuration

```yaml
communication:
  weekly_summary:
    day: "friday"
    time: "17:00"

    # Velocity tracking
    include_velocity: true
    velocity_unit: "story_points"  # story_points | tasks | hours

    # Comparison
    compare_previous_weeks: 4  # Compare to last 4 weeks
    show_trends: true

    # Statistics
    include_statistics:
      - commit_count
      - pr_count
      - lines_changed
      - test_coverage
      - velocity
      - completion_rate

    # Charts (requires plotly/matplotlib)
    generate_charts: true
    chart_types:
      - velocity_chart
      - commit_timeline
      - coverage_trend
```

---

## Real-Time Updates Configuration

### Basic Configuration

```yaml
communication:
  realtime_updates:
    enabled: true
    milestones: true
    blockers: true
    questions: true
```

### Detailed Configuration

```yaml
communication:
  realtime_updates:
    enabled: true

    # When to notify
    milestones: true  # Major accomplishments
    blockers: true    # Immediately when blocked
    questions: true   # When user input needed
    errors: true      # On errors/failures

    # Progress notifications
    progress_notifications: true
    progress_threshold: 25  # Notify every 25%
    # Sends notifications at: 25%, 50%, 75%, 100%

    # Quiet hours (no notifications)
    quiet_hours:
      enabled: true
      start: "22:00"
      end: "08:00"
      timezone: "America/New_York"
      exceptions:
        - "critical_errors"  # Still notify for critical errors
        - "security_issues"

    # Rate limiting (prevent spam)
    rate_limit:
      enabled: true
      max_per_hour: 10
      max_per_day: 50
```

---

## Notification Channels

### Terminal

```yaml
channels:
  terminal:
    enabled: true
    use_colors: true
    use_emojis: true
    width: 80  # Terminal width
    pager: false  # Use less/more for long output
```

### File

```yaml
channels:
  file:
    enabled: true
    base_dir: "reports/"

    # Directory structure
    daily_dir: "reports/daily/"
    weekly_dir: "reports/weekly/"
    sprint_dir: "reports/sprint/"

    # File naming
    daily_pattern: "standup-{date}.md"  # standup-2025-10-12.md
    weekly_pattern: "summary-{year}-W{week}.md"  # summary-2025-W41.md
    sprint_pattern: "review-{year}-{month}.md"  # review-2025-10.md

    # File permissions
    file_mode: 0o644  # rw-r--r--
    dir_mode: 0o755   # rwxr-xr-x
```

### Slack

```yaml
channels:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    channel: "#code-developer-updates"
    username: "code_developer"
    icon_emoji: ":robot_face:"

    # Message formatting
    format: "blocks"  # blocks | text
    mention_on_blockers: "@here"
    mention_on_completion: "@channel"

    # Rate limiting
    rate_limit:
      max_per_hour: 5
      max_per_day: 20
```

### Email

```yaml
channels:
  email:
    enabled: false

    # SMTP settings
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    smtp_tls: true
    smtp_user: "your@email.com"
    smtp_password: "${EMAIL_PASSWORD}"  # Use environment variable

    # Email settings
    from_email: "code-developer@yourdomain.com"
    from_name: "Code Developer AI"
    to_emails:
      - "team@yourdomain.com"
      - "manager@yourdomain.com"

    # Email formatting
    format: "html"  # html | text
    template: "templates/email.html"
    include_attachments: true  # Attach full report

    # When to send
    send_daily: true
    send_weekly: true
    send_on_blockers: true
```

---

## Report Retention

### Basic Retention

```yaml
communication:
  retention:
    daily_days: 90      # Keep 90 days of daily reports
    weekly_days: 365    # Keep 1 year of weekly reports
    sprint_days: -1     # -1 = keep forever
```

### Advanced Retention

```yaml
communication:
  retention:
    daily_days: 90
    weekly_days: 365
    sprint_days: -1

    # Archive old reports
    archive:
      enabled: true
      compress: true  # gzip old reports
      archive_dir: "reports/archive/"
      archive_after_days: 30

    # Cleanup
    cleanup:
      enabled: true
      schedule: "0 3 * * 0"  # 3 AM every Sunday (cron format)
      dry_run: false  # Set true to test without deleting
```

---

## CLI Configuration Commands

### View Configuration

```bash
# View entire configuration
poetry run project-manager dev config show

# View specific section
poetry run project-manager dev config show daily_standup

# View as JSON
poetry run project-manager dev config show --format json
```

### Set Configuration

```bash
# Set simple values
poetry run project-manager dev config set daily_standup.time "08:30"
poetry run project-manager dev config set daily_standup.timezone "America/Los_Angeles"

# Set boolean
poetry run project-manager dev config set daily_standup.enabled true

# Set list
poetry run project-manager dev config set daily_standup.days "monday,tuesday,wednesday"

# Set nested values
poetry run project-manager dev config set channels.slack.webhook_url "https://..."
```

### Initialize Configuration

```bash
# Create default config
poetry run project-manager dev config init

# Create config with template
poetry run project-manager dev config init --template minimal
poetry run project-manager dev config init --template full

# Interactive config creator
poetry run project-manager dev config wizard
```

### Validate Configuration

```bash
# Validate syntax
poetry run project-manager dev config validate

# Test configuration
poetry run project-manager dev config test

# Test specific channel
poetry run project-manager dev config test slack
```

---

## Examples

### Example 1: Minimal Configuration

For users who just want basic daily updates:

```yaml
communication:
  daily_standup:
    enabled: true
    time: "09:00"
    timezone: "America/New_York"
```

### Example 2: Workday Reports Only

Monday-Friday reports, no weekends:

```yaml
communication:
  daily_standup:
    enabled: true
    time: "09:00"
    days:
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
```

### Example 3: Slack Integration

Send daily updates to Slack:

```yaml
communication:
  daily_standup:
    enabled: true
    time: "09:00"
    channels:
      - terminal
      - file
      - slack

channels:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    channel: "#dev-updates"
    username: "code_developer"
```

### Example 4: Quiet Hours

No notifications between 10 PM and 8 AM:

```yaml
communication:
  realtime_updates:
    enabled: true
    quiet_hours:
      enabled: true
      start: "22:00"
      end: "08:00"
```

### Example 5: Minimal Verbosity

Brief summaries only:

```yaml
communication:
  daily_standup:
    verbosity: "minimal"
    sections:
      - accomplishments
      - blockers
```

### Example 6: Archive Old Reports

Keep last 30 days, archive the rest:

```yaml
communication:
  retention:
    daily_days: 30
    archive:
      enabled: true
      compress: true
      archive_dir: "reports/archive/"
```

---

## Advanced Configuration

### Custom Templates

```yaml
advanced:
  templates:
    daily_standup: "templates/custom_standup.md"
    weekly_summary: "templates/custom_weekly.md"

    # Template variables available:
    # - {date}, {day}, {week}, {month}, {year}
    # - {accomplishments}, {metrics}, {blockers}
    # - {commits}, {prs}, {lines_added}, {lines_deleted}
    # - {coverage}, {tests_passed}, {tests_failed}
```

### Metrics Customization

```yaml
metrics:
  git:
    enabled: true
    author_filter: ["Claude", "code-developer", "CI Bot"]
    exclude_merge_commits: true
    exclude_patterns:
      - "^WIP:"
      - "^temp:"

  custom_metrics:
    - name: "api_calls"
      query: "SELECT COUNT(*) FROM llm_metrics WHERE date = '{date}'"
      label: "API Calls"

    - name: "cost"
      query: "SELECT SUM(cost) FROM llm_metrics WHERE date = '{date}'"
      label: "Total Cost"
      format: "${:.2f}"
```

### Conditional Notifications

```yaml
communication:
  conditional_notifications:
    - condition: "commits > 10"
      action: "notify"
      channel: "slack"
      message: "High productivity day! 🚀 {commits} commits"

    - condition: "blockers.count > 0"
      action: "notify"
      channel: "email"
      priority: "high"
      message: "Blockers need attention: {blockers.summary}"

    - condition: "coverage < 80"
      action: "warn"
      message: "Test coverage dropped to {coverage}%"
```

---

## Troubleshooting

### Problem: Config Not Loading

**Symptoms**: Changes to config file don't take effect

**Solutions**:

1. Check config file location:
   ```bash
   poetry run project-manager dev config show --path
   ```

2. Validate config syntax:
   ```bash
   poetry run project-manager dev config validate
   ```

3. Check YAML syntax:
   ```bash
   yamllint ~/.config/coffee-maker/communication.yaml
   ```

4. Check file permissions:
   ```bash
   ls -la ~/.config/coffee-maker/communication.yaml
   chmod 644 ~/.config/coffee-maker/communication.yaml
   ```

### Problem: Slack Notifications Not Working

**Symptoms**: Slack webhook returns errors

**Solutions**:

1. Test webhook URL:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test from code_developer"}' \
     YOUR_WEBHOOK_URL
   ```

2. Verify webhook in Slack settings

3. Check rate limits:
   ```bash
   poetry run project-manager dev config show channels.slack.rate_limit
   ```

4. Test from CLI:
   ```bash
   poetry run project-manager dev config test slack
   ```

### Problem: Reports Not Generated at Scheduled Time

**Symptoms**: Daily report not generated at configured time

**Solutions**:

1. Check daemon is running:
   ```bash
   poetry run project-manager status
   ```

2. Check scheduler logs:
   ```bash
   tail -f data/logs/scheduler.log
   ```

3. Verify timezone:
   ```bash
   poetry run project-manager dev config show daily_standup.timezone
   ```

4. Manual generation:
   ```bash
   poetry run project-manager dev report daily --force
   ```

---

## Environment Variables

Override configuration with environment variables:

```bash
# Override standup time
export COFFEE_MAKER_DAILY_TIME="08:00"

# Override timezone
export COFFEE_MAKER_TIMEZONE="America/Los_Angeles"

# Override Slack webhook
export COFFEE_MAKER_SLACK_WEBHOOK="https://hooks.slack.com/..."

# Override verbosity
export COFFEE_MAKER_VERBOSITY="verbose"

# Custom config path
export COFFEE_MAKER_CONFIG="/path/to/config.yaml"
```

---

## Related Documentation

- [DAILY_STANDUP_GUIDE.md](DAILY_STANDUP_GUIDE.md) - Usage guide
- [PRIORITY_9_TECHNICAL_SPEC.md](PRIORITY_9_TECHNICAL_SPEC.md) - Technical details
- [STANDUP_EXAMPLES.md](STANDUP_EXAMPLES.md) - Real-world examples

---

**Version**: 1.0
**Last Updated**: 2025-10-12
**Status**: ✅ Complete - Ready to use
