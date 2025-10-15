# US-034: Slack Integration for Notifications and Status Updates

## Technical Specification

**Status**: 📝 In Development
**Priority**: 🔴 MUST-HAVE (User-requested)
**Estimated Duration**: 8-12 hours
**Created**: 2025-10-15

---

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Architecture](#architecture)
4. [Component Specifications](#component-specifications)
5. [Notification Types](#notification-types)
6. [Slack App Setup](#slack-app-setup)
7. [Configuration](#configuration)
8. [Integration Points](#integration-points)
9. [Error Handling & Resilience](#error-handling--resilience)
10. [Testing Strategy](#testing-strategy)
11. [Implementation Plan](#implementation-plan)
12. [Success Criteria](#success-criteria)

---

## Overview

### Business Value

Integrate Slack to provide **real-time visibility** into the autonomous development system, enabling remote monitoring and team collaboration. This is critical for users who want to:

- Monitor daemon lifecycle without polling the terminal
- Get instant notifications when PRs are created or completed
- Receive daily progress summaries with velocity metrics
- Stay informed about system errors and blockers

### Scope

**In Scope**:
- Slack Bot Token authentication
- Real-time notification delivery to configured channel
- Daemon lifecycle events (started, stopped, errors, crashes)
- Priority completion notifications with summaries
- PR status updates (created, merged, CI failures)
- System alerts (errors, warnings, blockers)
- Daily progress summaries (sent at configured time)
- Rich message formatting with Slack Block Kit
- Asynchronous, non-blocking notification delivery
- Graceful degradation if Slack unavailable

**Out of Scope** (Future Enhancements):
- Interactive Slack commands (e.g., `/code-dev status`)
- Thread-based conversations
- Multiple channel support
- User-specific DM notifications
- Slack OAuth (using Bot Token instead)
- Message editing/updating (always send new messages)

---

## Requirements

### Functional Requirements

1. **FR-01**: Send notification to Slack when daemon starts
2. **FR-02**: Send notification to Slack when daemon stops gracefully
3. **FR-03**: Send alert to Slack when daemon crashes or encounters errors
4. **FR-04**: Send notification when a priority is completed with summary
5. **FR-05**: Send notification when a PR is created
6. **FR-06**: Send alert when CI/CD tests fail
7. **FR-07**: Send daily progress summary at configured time (default: 18:00)
8. **FR-08**: Support rich message formatting with Slack Block Kit
9. **FR-09**: Include context-aware details (priority name, PR link, error details)
10. **FR-10**: Gracefully handle Slack API failures without crashing daemon

### Non-Functional Requirements

1. **NFR-01**: Notification delivery must be asynchronous (non-blocking)
2. **NFR-02**: System must respect Slack rate limits (1 message/second)
3. **NFR-03**: Failed notifications must be retried with exponential backoff (max 3 attempts)
4. **NFR-04**: If Slack is unavailable, fall back to existing notification system (NotificationDB)
5. **NFR-05**: Configuration must be environment-based (SLACK_BOT_TOKEN, etc.)
6. **NFR-06**: Slack integration must be opt-in (disabled by default via SLACK_ENABLED=false)
7. **NFR-07**: All Slack operations must have comprehensive logging
8. **NFR-08**: Test coverage target: 80%+ for Slack integration code

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MonolithicCoffeeMakerAgent                       │
│                                                                     │
│  ┌──────────────┐                          ┌──────────────────┐   │
│  │   Daemon     │                          │  NotificationDB  │   │
│  │   Events     │                          │   (Existing)     │   │
│  └──────┬───────┘                          └────────┬─────────┘   │
│         │                                            │             │
│         │  Lifecycle Events                          │ DB Events   │
│         │  (start, stop, error)                      │             │
│         │                                            │             │
│         ▼                                            ▼             │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              SlackNotifier (New)                            │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │ Notification Dispatcher                               │  │  │
│  │  │ - Formats messages                                    │  │  │
│  │  │ - Determines notification type                        │  │  │
│  │  │ - Delegates to formatters                             │  │  │
│  │  └────────────────────┬──────────────────────────────────┘  │  │
│  │                       │                                     │  │
│  │                       ▼                                     │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │ Message Formatters                                    │  │  │
│  │  │ - DaemonLifecycleFormatter                           │  │  │
│  │  │ - PriorityCompletionFormatter                        │  │  │
│  │  │ - PRStatusFormatter                                  │  │  │
│  │  │ - SystemAlertFormatter                               │  │  │
│  │  │ - DailySummaryFormatter                              │  │  │
│  │  └────────────────────┬──────────────────────────────────┘  │  │
│  │                       │                                     │  │
│  │                       ▼                                     │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │ SlackClient (API Wrapper)                             │  │  │
│  │  │ - Async message posting                               │  │  │
│  │  │ - Rate limiting (1 msg/sec)                           │  │  │
│  │  │ - Retry logic (exponential backoff)                   │  │  │
│  │  │ - Error handling                                      │  │  │
│  │  └────────────────────┬──────────────────────────────────┘  │  │
│  └───────────────────────┼─────────────────────────────────────┘  │
│                          │                                         │
│                          │ HTTPS POST (Bot Token Auth)             │
│                          ▼                                         │
│                  ┌─────────────────┐                               │
│                  │  Slack API      │                               │
│                  │  chat.postMessage│                              │
│                  └─────────────────┘                               │
│                          │                                         │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Slack Channel  │
                  │  #code-developer│
                  └─────────────────┘
```

### Component Interaction Flow

```
1. Event occurs (e.g., daemon starts)
   ├─► daemon.py calls: notifier.notify_daemon_started()
   │
2. SlackNotifier receives event
   ├─► Checks if Slack enabled (SLACK_ENABLED=true)
   ├─► Checks if bot token configured
   ├─► If disabled: log debug message, return
   │
3. Format message
   ├─► notifier.notify_daemon_started() → DaemonLifecycleFormatter.format_start()
   ├─► Returns Slack Block Kit JSON structure
   │
4. Send to Slack (async)
   ├─► SlackClient.post_message(blocks, channel)
   ├─► Rate limiting check (throttle if needed)
   ├─► POST to Slack API with Bot Token
   │   ├─► Success: Log confirmation, return
   │   └─► Failure: Retry with exponential backoff (max 3 attempts)
   │       ├─► Still failing: Log error, fallback to NotificationDB
   │       └─► Return
   │
5. Confirmation
   └─► Log: "Sent Slack notification: daemon_started to #code-developer"
```

---

## Component Specifications

### 1. SlackClient (`coffee_maker/integrations/slack/client.py`)

**Purpose**: Low-level Slack API wrapper with retry logic and rate limiting.

**Responsibilities**:
- Authenticate with Slack using Bot Token
- Post messages to configured channel
- Handle rate limiting (1 message/second)
- Implement retry logic with exponential backoff
- Manage connection errors gracefully

**Class Interface**:

```python
class SlackClient:
    """Low-level Slack API client with retry logic and rate limiting.

    Features:
        - Async message posting
        - Rate limiting (1 message/second)
        - Exponential backoff retry (max 3 attempts)
        - Comprehensive error handling

    Example:
        >>> client = SlackClient(bot_token="xoxb-...", channel_id="C123456")
        >>> client.post_message(
        ...     text="Daemon started",
        ...     blocks=[{...}]  # Slack Block Kit
        ... )
    """

    def __init__(
        self,
        bot_token: str,
        channel_id: str,
        rate_limit: float = 1.0  # messages per second
    ):
        """Initialize Slack client.

        Args:
            bot_token: Slack Bot Token (xoxb-...)
            channel_id: Default channel ID (C123456789)
            rate_limit: Max messages per second (default: 1.0)
        """
        pass

    def post_message(
        self,
        text: str,
        blocks: Optional[List[Dict]] = None,
        channel: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> bool:
        """Post message to Slack with retry logic.

        Args:
            text: Plain text fallback message
            blocks: Slack Block Kit blocks (rich formatting)
            channel: Override default channel (optional)
            thread_ts: Thread timestamp for replies (optional)

        Returns:
            True if message sent successfully, False otherwise
        """
        pass

    def _check_rate_limit(self):
        """Enforce rate limiting (1 message/second)."""
        pass

    def _retry_with_backoff(
        self,
        func: Callable,
        max_attempts: int = 3
    ) -> Any:
        """Retry function with exponential backoff.

        Backoff strategy:
            Attempt 1: Immediate
            Attempt 2: Wait 2 seconds
            Attempt 3: Wait 4 seconds
        """
        pass

    def test_connection(self) -> bool:
        """Test Slack connection and permissions.

        Returns:
            True if connection successful, False otherwise
        """
        pass
```

### 2. SlackNotifier (`coffee_maker/integrations/slack/notifier.py`)

**Purpose**: High-level notification dispatcher that formats and sends notifications.

**Responsibilities**:
- Determine notification type from event
- Delegate to appropriate formatter
- Call SlackClient to send message
- Handle configuration (SLACK_ENABLED, etc.)
- Fallback to NotificationDB if Slack fails

**Class Interface**:

```python
class SlackNotifier:
    """High-level notification dispatcher for Slack.

    This is the primary interface for sending Slack notifications.
    All daemon and system events should use this class.

    Features:
        - Auto-formatting based on notification type
        - Graceful degradation if Slack unavailable
        - Fallback to NotificationDB
        - Configuration-driven (SLACK_ENABLED)

    Example:
        >>> notifier = SlackNotifier()
        >>> notifier.notify_daemon_started()
        >>> notifier.notify_priority_completed(
        ...     priority_name="US-034",
        ...     summary="Slack integration implemented",
        ...     duration_hours=8.5
        ... )
    """

    def __init__(self, config: Optional[SlackConfig] = None):
        """Initialize Slack notifier.

        Args:
            config: Slack configuration (defaults to env vars)
        """
        pass

    # Daemon Lifecycle
    def notify_daemon_started(self):
        """Notify that daemon has started."""
        pass

    def notify_daemon_stopped(self):
        """Notify that daemon has stopped gracefully."""
        pass

    def notify_daemon_error(self, error: Exception, context: Dict):
        """Notify about daemon error/crash."""
        pass

    # Priority Completion
    def notify_priority_completed(
        self,
        priority_name: str,
        summary: str,
        duration_hours: float,
        files_changed: int,
        tests_added: int
    ):
        """Notify about completed priority."""
        pass

    # PR Status
    def notify_pr_created(
        self,
        pr_number: int,
        pr_url: str,
        title: str,
        branch: str
    ):
        """Notify about new PR creation."""
        pass

    def notify_pr_merged(self, pr_number: int, pr_url: str):
        """Notify about PR merge."""
        pass

    def notify_ci_failure(
        self,
        pr_number: int,
        pr_url: str,
        failure_details: str
    ):
        """Notify about CI/CD failure."""
        pass

    # System Alerts
    def notify_system_alert(
        self,
        level: str,  # "warning" or "error"
        title: str,
        message: str,
        context: Optional[Dict] = None
    ):
        """Notify about system alerts."""
        pass

    # Daily Summary
    def send_daily_summary(
        self,
        date: str,
        priorities_completed: int,
        prs_created: int,
        prs_merged: int,
        velocity: float,
        blockers: List[str]
    ):
        """Send daily progress summary."""
        pass

    def _send_message(
        self,
        text: str,
        blocks: List[Dict]
    ) -> bool:
        """Internal method to send message via SlackClient."""
        pass

    def _fallback_to_db(
        self,
        type: str,
        title: str,
        message: str
    ):
        """Fallback to NotificationDB if Slack fails."""
        pass
```

### 3. Message Formatters (`coffee_maker/integrations/slack/formatters.py`)

**Purpose**: Format notification data into Slack Block Kit structures.

**Responsibilities**:
- Convert event data to Slack Block Kit JSON
- Provide rich formatting (headers, sections, dividers, emojis)
- Maintain consistent styling across notification types
- Handle optional fields gracefully

**Module Structure**:

```python
"""Slack message formatters using Block Kit.

Each formatter converts event data into Slack Block Kit blocks.

Reference: https://api.slack.com/block-kit

Example Block Kit Structure:
    [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🚀 Daemon Started"}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Status:* Running"}
        },
        {
            "type": "divider"
        }
    ]
"""

class DaemonLifecycleFormatter:
    """Format daemon lifecycle events."""

    @staticmethod
    def format_start() -> List[Dict]:
        """Format daemon start notification.

        Returns:
            Slack Block Kit blocks

        Example Output:
            🚀 Daemon Started
            ──────────────────
            Status: Running
            Time: 2025-10-15 14:30:00 UTC
            Branch: roadmap
            Next Priority: US-034
        """
        pass

    @staticmethod
    def format_stop() -> List[Dict]:
        """Format daemon stop notification."""
        pass

    @staticmethod
    def format_error(error: Exception, context: Dict) -> List[Dict]:
        """Format daemon error notification."""
        pass


class PriorityCompletionFormatter:
    """Format priority completion events."""

    @staticmethod
    def format(
        priority_name: str,
        summary: str,
        duration_hours: float,
        files_changed: int,
        tests_added: int
    ) -> List[Dict]:
        """Format priority completion notification.

        Example Output:
            ✅ Priority Completed: US-034
            ────────────────────────────
            Slack Integration for Notifications

            📊 Metrics:
            • Duration: 8.5 hours
            • Files Changed: 12
            • Tests Added: 25

            Summary: Implemented Slack Bot integration...
        """
        pass


class PRStatusFormatter:
    """Format PR status events."""

    @staticmethod
    def format_created(
        pr_number: int,
        pr_url: str,
        title: str,
        branch: str
    ) -> List[Dict]:
        """Format PR creation notification."""
        pass

    @staticmethod
    def format_merged(pr_number: int, pr_url: str) -> List[Dict]:
        """Format PR merge notification."""
        pass

    @staticmethod
    def format_ci_failure(
        pr_number: int,
        pr_url: str,
        failure_details: str
    ) -> List[Dict]:
        """Format CI failure notification."""
        pass


class SystemAlertFormatter:
    """Format system alerts."""

    @staticmethod
    def format(
        level: str,
        title: str,
        message: str,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """Format system alert notification."""
        pass


class DailySummaryFormatter:
    """Format daily progress summaries."""

    @staticmethod
    def format(
        date: str,
        priorities_completed: int,
        prs_created: int,
        prs_merged: int,
        velocity: float,
        blockers: List[str]
    ) -> List[Dict]:
        """Format daily summary notification.

        Example Output:
            📈 Daily Summary - October 15, 2025
            ───────────────────────────────────

            🎯 Priorities Completed: 2
            📝 PRs Created: 3
            ✅ PRs Merged: 1
            ⚡ Velocity: 1.8 priorities/day

            🚧 Blockers:
            • US-035: Waiting for API access
            • US-040: Needs architectural review
        """
        pass
```

### 4. Configuration (`coffee_maker/integrations/slack/config.py`)

**Purpose**: Manage Slack configuration from environment variables.

**Responsibilities**:
- Load configuration from environment
- Validate required settings
- Provide defaults
- Handle missing configuration gracefully

**Class Interface**:

```python
@dataclass
class SlackConfig:
    """Slack integration configuration.

    Loaded from environment variables:
        SLACK_BOT_TOKEN: Bot Token (xoxb-...)
        SLACK_CHANNEL_ID: Channel ID (C123456789)
        SLACK_ENABLED: Enable/disable (default: false)
        SLACK_DAILY_SUMMARY_TIME: Daily summary time (HH:MM, default: 18:00)
        SLACK_RATE_LIMIT: Rate limit (default: 1.0 msg/sec)
        SLACK_MAX_RETRIES: Max retry attempts (default: 3)
    """

    bot_token: str
    channel_id: str
    enabled: bool = False
    daily_summary_time: str = "18:00"
    rate_limit: float = 1.0
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "SlackConfig":
        """Load configuration from environment variables.

        Returns:
            SlackConfig instance

        Raises:
            ValueError: If required settings missing and enabled=true
        """
        pass

    def validate(self):
        """Validate configuration.

        Raises:
            ValueError: If configuration invalid
        """
        pass

    def is_configured(self) -> bool:
        """Check if Slack is properly configured.

        Returns:
            True if bot_token and channel_id set, False otherwise
        """
        pass
```

---

## Notification Types

### 1. Daemon Lifecycle Events

**Trigger**: Daemon starts, stops, or encounters errors

**Example Messages**:

```
🚀 Daemon Started
──────────────────
Status: Running
Time: 2025-10-15 14:30:00 UTC
Branch: roadmap
Next Priority: US-034

───

🛑 Daemon Stopped
──────────────────
Status: Graceful shutdown
Time: 2025-10-15 18:45:00 UTC
Runtime: 4 hours 15 minutes
Priorities Completed: 2

───

🚨 Daemon Error
────────────────
Error: ConnectionError
Message: Failed to connect to Claude API
Time: 2025-10-15 16:22:00 UTC
Context: Implementing US-034
Action: Retrying in 5 minutes...
```

### 2. Priority Completion

**Trigger**: Priority marked as complete in ROADMAP.md

**Example Message**:

```
✅ Priority Completed: US-034
────────────────────────────
Slack Integration for Notifications

📊 Metrics:
• Duration: 8.5 hours
• Files Changed: 12
• Tests Added: 25
• Lines Added: 847
• Lines Deleted: 23

Summary:
Implemented Slack Bot integration with support for daemon lifecycle events,
priority completion notifications, PR status updates, and daily summaries.
```

### 3. PR Status Updates

**Trigger**: PR created, merged, or CI fails

**Example Messages**:

```
📝 PR Created: #142
───────────────────
feat: Implement US-034 - Slack Integration

Branch: feature/us-034-slack-integration
→ Link: https://github.com/user/repo/pull/142
Status: Awaiting review

───

✅ PR Merged: #142
──────────────────
feat: Implement US-034 - Slack Integration

Merged by: code_developer
Time: 2025-10-15 17:30:00 UTC

───

❌ CI Failure: PR #142
───────────────────────
feat: Implement US-034 - Slack Integration

Failed Tests:
• test_slack_client.py::test_post_message
• test_slack_notifier.py::test_daemon_started

→ View logs: https://github.com/user/repo/actions/runs/12345
```

### 4. System Alerts

**Trigger**: Warnings, errors, blockers

**Example Message**:

```
⚠️ System Warning
──────────────────
Title: Rate limit approaching
Message: Slack API rate limit at 80% capacity
Time: 2025-10-15 15:45:00 UTC
Action: Throttling notifications

───

🚨 System Error
────────────────
Title: Database connection lost
Message: Cannot connect to NotificationDB
Time: 2025-10-15 16:10:00 UTC
Action: Attempting reconnection...
```

### 5. Daily Summary

**Trigger**: Scheduled at configured time (default: 18:00)

**Example Message**:

```
📈 Daily Summary - October 15, 2025
───────────────────────────────────

🎯 Priorities Completed: 2
   • US-034: Slack Integration
   • US-035: Webhook Support

📝 PRs Created: 3
✅ PRs Merged: 1
⚡ Velocity: 1.8 priorities/day

🚧 Blockers (2):
• US-036: Waiting for API access
• US-040: Needs architectural review

📊 System Health: ✅ Healthy
```

---

## Slack App Setup

### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name: "Code Developer Bot"
5. Workspace: Select your workspace

### Step 2: Configure Bot Permissions

Navigate to **OAuth & Permissions** and add these Bot Token Scopes:

**Required Scopes**:
- `chat:write` - Post messages to channels
- `chat:write.public` - Post to public channels without joining
- `channels:read` - View basic channel info

**Optional Scopes** (Future):
- `chat:write.customize` - Custom username/icon
- `users:read` - Read user info
- `reactions:write` - Add emoji reactions

### Step 3: Install App to Workspace

1. Click "Install to Workspace"
2. Authorize the app
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### Step 4: Get Channel ID

**Method 1: From Slack UI**
1. Right-click channel name
2. Click "Copy link"
3. Extract ID from URL: `https://workspace.slack.com/archives/C123456789`
   - Channel ID: `C123456789`

**Method 2: From API**
```bash
curl -H "Authorization: Bearer xoxb-..." \
  https://slack.com/api/conversations.list
```

### Step 5: Configure MonolithicCoffeeMakerAgent

Add to `.env`:

```bash
# Slack Integration
SLACK_ENABLED=true
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=C123456789
SLACK_DAILY_SUMMARY_TIME=18:00
```

### Step 6: Test Connection

```bash
poetry run python -m coffee_maker.integrations.slack.client --test
```

Expected output:
```
✅ Slack connection successful
✅ Bot can post to #code-developer
✅ Rate limiting working
🎉 Ready to send notifications!
```

---

## Configuration

### Environment Variables

Add to `.env.example` and `.env`:

```bash
# ============================================================================
# Slack Integration (US-034)
# ============================================================================
# Real-time notifications for daemon events, PR updates, and daily summaries
#
# Setup:
# 1. Create Slack app at https://api.slack.com/apps
# 2. Add bot token scopes: chat:write, chat:write.public, channels:read
# 3. Install app to workspace
# 4. Copy Bot User OAuth Token (starts with xoxb-)
# 5. Get channel ID from Slack (right-click channel → Copy link → extract ID)
# ============================================================================

# Enable/disable Slack notifications (default: false)
export SLACK_ENABLED="false"

# Slack Bot User OAuth Token (REQUIRED if enabled)
# Get from: https://api.slack.com/apps → Your App → OAuth & Permissions
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"

# Slack Channel ID (REQUIRED if enabled)
# Format: C123456789
# Get from: Right-click channel → Copy link → Extract ID
export SLACK_CHANNEL_ID="C123456789"

# Daily summary time (24-hour format HH:MM, default: 18:00)
export SLACK_DAILY_SUMMARY_TIME="18:00"

# Rate limit (messages per second, default: 1.0)
export SLACK_RATE_LIMIT="1.0"

# Max retry attempts for failed messages (default: 3)
export SLACK_MAX_RETRIES="3"
```

### Configuration Validation

```python
# In daemon startup, validate Slack configuration:
from coffee_maker.integrations.slack.config import SlackConfig

try:
    config = SlackConfig.from_env()
    if config.enabled:
        config.validate()
        logger.info("Slack integration enabled")
        # Test connection
        client = SlackClient(config.bot_token, config.channel_id)
        if client.test_connection():
            logger.info("Slack connection verified")
        else:
            logger.warning("Slack connection failed - disabling")
            config.enabled = False
except Exception as e:
    logger.warning(f"Slack configuration error: {e} - disabling")
    config.enabled = False
```

---

## Integration Points

### 1. Daemon Lifecycle (`coffee_maker/autonomous/daemon.py`)

**Integration Points**:

```python
from coffee_maker.integrations.slack.notifier import SlackNotifier

class DevDaemon:
    def __init__(self, ...):
        # Existing initialization
        self.notifier = NotificationDB()

        # NEW: Slack integration
        self.slack_notifier = SlackNotifier()

    def run(self):
        """Main daemon loop."""
        try:
            # NEW: Notify daemon started
            self.slack_notifier.notify_daemon_started()

            while True:
                # Existing logic
                ...

        except KeyboardInterrupt:
            # NEW: Notify graceful shutdown
            self.slack_notifier.notify_daemon_stopped()

        except Exception as e:
            # NEW: Notify error
            self.slack_notifier.notify_daemon_error(e, context={...})
            raise

    def _implement_priority(self, priority):
        """Implement a priority."""
        # Existing implementation...

        # NEW: Notify completion
        self.slack_notifier.notify_priority_completed(
            priority_name=priority['name'],
            summary=priority['summary'],
            duration_hours=...,
            files_changed=...,
            tests_added=...
        )
```

### 2. PR Creation Hook (`coffee_maker/autonomous/daemon.py`)

**Integration Point**:

```python
def _create_pull_request(self, branch, priority_name):
    """Create PR after implementation."""
    # Existing PR creation with gh CLI
    result = subprocess.run([
        "gh", "pr", "create",
        "--title", f"feat: Implement {priority_name}",
        "--body", pr_body
    ], capture_output=True, text=True)

    if result.returncode == 0:
        # Parse PR URL and number
        pr_url = result.stdout.strip()
        pr_number = int(pr_url.split('/')[-1])

        # NEW: Notify PR created
        self.slack_notifier.notify_pr_created(
            pr_number=pr_number,
            pr_url=pr_url,
            title=f"feat: Implement {priority_name}",
            branch=branch
        )
```

### 3. Existing NotificationDB Integration

**Fallback Strategy**:

```python
# In SlackNotifier._send_message():
def _send_message(self, text: str, blocks: List[Dict]) -> bool:
    try:
        success = self.client.post_message(text, blocks)
        if success:
            return True
    except Exception as e:
        logger.error(f"Slack notification failed: {e}")

    # Fallback to existing NotificationDB
    logger.info("Falling back to NotificationDB")
    self._fallback_to_db(
        type="info",
        title=text,
        message=text
    )
    return False

def _fallback_to_db(self, type: str, title: str, message: str):
    """Fallback to existing notification system."""
    from coffee_maker.cli.notifications import NotificationDB
    db = NotificationDB()
    db.create_notification(
        type=type,
        title=f"[Slack Failed] {title}",
        message=message,
        priority="normal",
        play_sound=False  # Already tried via Slack
    )
```

### 4. Daily Summary Scheduler

**New Component**: Background scheduler for daily summaries

```python
# In daemon.py or separate scheduler module:
import schedule
import time
from threading import Thread

class DailySummaryScheduler:
    """Schedule daily summary notifications."""

    def __init__(self, slack_notifier: SlackNotifier, config: SlackConfig):
        self.slack_notifier = slack_notifier
        self.config = config

        # Schedule daily summary
        schedule.every().day.at(config.daily_summary_time).do(
            self._send_daily_summary
        )

    def _send_daily_summary(self):
        """Collect metrics and send daily summary."""
        # Query ROADMAP.md for completed priorities
        # Query git for PRs created/merged
        # Calculate velocity
        # Identify blockers

        self.slack_notifier.send_daily_summary(
            date=datetime.now().strftime("%Y-%m-%d"),
            priorities_completed=...,
            prs_created=...,
            prs_merged=...,
            velocity=...,
            blockers=[...]
        )

    def start(self):
        """Start scheduler in background thread."""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        thread = Thread(target=run_scheduler, daemon=True)
        thread.start()
```

---

## Error Handling & Resilience

### 1. Graceful Degradation

**Principle**: Slack failures should NEVER crash the daemon.

```python
# All Slack operations wrapped in try-except:
try:
    slack_notifier.notify_priority_completed(...)
except Exception as e:
    logger.error(f"Slack notification failed: {e}")
    # Continue daemon operation
```

### 2. Retry Logic

**Exponential Backoff**:

```python
def _retry_with_backoff(self, func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except SlackApiError as e:
            if e.response['error'] == 'rate_limited':
                # Rate limited - wait longer
                wait_time = 2 ** (attempt + 2)  # 4, 8, 16 seconds
            else:
                # Other errors - exponential backoff
                wait_time = 2 ** attempt  # 1, 2, 4 seconds

            if attempt < max_attempts - 1:
                logger.warning(f"Slack API error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Slack API failed after {max_attempts} attempts")
                raise
```

### 3. Rate Limiting

**Throttling**:

```python
class SlackClient:
    def __init__(self, ...):
        self.last_message_time = 0
        self.rate_limit = 1.0  # 1 message per second

    def _check_rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_message_time

        if time_since_last < self.rate_limit:
            wait_time = self.rate_limit - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        self.last_message_time = time.time()
```

### 4. Connection Validation

**Test on Startup**:

```python
def test_connection(self) -> bool:
    """Test Slack connection and permissions."""
    try:
        response = self.client.auth_test()
        logger.info(f"Slack auth successful: {response['user']}")

        # Test posting to channel
        self.post_message(
            text="✅ Slack integration test successful",
            blocks=[{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✅ Connection verified"
                }
            }]
        )
        return True

    except SlackApiError as e:
        logger.error(f"Slack connection test failed: {e}")
        return False
```

### 5. Logging

**Comprehensive Logging**:

```python
# Success
logger.info(f"Sent Slack notification: {event_type} to #{channel}")

# Warning (non-critical)
logger.warning(f"Slack rate limit approaching: {current_rate}/{max_rate}")

# Error (with fallback)
logger.error(f"Slack notification failed: {error} - falling back to DB")

# Debug (for development)
logger.debug(f"Slack message blocks: {json.dumps(blocks, indent=2)}")
```

---

## Testing Strategy

### 1. Unit Tests (`tests/unit/test_slack_integration.py`)

**Coverage**:

```python
# SlackClient Tests
def test_slack_client_initialization()
def test_slack_client_post_message_success()
def test_slack_client_post_message_failure()
def test_slack_client_rate_limiting()
def test_slack_client_retry_logic()
def test_slack_client_connection_test()

# SlackNotifier Tests
def test_slack_notifier_daemon_started()
def test_slack_notifier_daemon_stopped()
def test_slack_notifier_daemon_error()
def test_slack_notifier_priority_completed()
def test_slack_notifier_pr_created()
def test_slack_notifier_daily_summary()
def test_slack_notifier_fallback_to_db()
def test_slack_notifier_disabled()

# Formatter Tests
def test_daemon_lifecycle_formatter_start()
def test_daemon_lifecycle_formatter_stop()
def test_daemon_lifecycle_formatter_error()
def test_priority_completion_formatter()
def test_pr_status_formatter_created()
def test_pr_status_formatter_merged()
def test_pr_status_formatter_ci_failure()
def test_system_alert_formatter()
def test_daily_summary_formatter()

# Config Tests
def test_slack_config_from_env()
def test_slack_config_validation()
def test_slack_config_is_configured()
def test_slack_config_defaults()
```

**Mocking Strategy**:

```python
import pytest
from unittest.mock import Mock, patch
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

@pytest.fixture
def mock_slack_client():
    with patch('slack_sdk.WebClient') as mock:
        yield mock

def test_slack_client_post_message_success(mock_slack_client):
    # Mock successful API response
    mock_slack_client.return_value.chat_postMessage.return_value = {
        'ok': True,
        'ts': '1234567890.123456'
    }

    client = SlackClient(bot_token="xoxb-test", channel_id="C123")
    result = client.post_message(text="Test", blocks=[])

    assert result is True
    mock_slack_client.return_value.chat_postMessage.assert_called_once()
```

### 2. Integration Tests (`tests/integration/test_slack_e2e.py`)

**Coverage**:

```python
# End-to-End Tests (requires real Slack workspace)
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("SLACK_ENABLED"), reason="Slack not configured")
def test_e2e_daemon_started_notification():
    """Test actual Slack notification delivery."""
    notifier = SlackNotifier()
    result = notifier.notify_daemon_started()
    assert result is True

    # Verify message visible in Slack
    # (Manual verification or use Slack API to check recent messages)

@pytest.mark.integration
def test_e2e_fallback_to_db():
    """Test fallback when Slack unavailable."""
    # Configure with invalid token
    config = SlackConfig(
        bot_token="xoxb-invalid",
        channel_id="C123",
        enabled=True
    )
    notifier = SlackNotifier(config)

    # Should fail and fallback to DB
    result = notifier.notify_daemon_started()
    assert result is False

    # Verify notification created in DB
    db = NotificationDB()
    pending = db.get_pending_notifications()
    assert len(pending) > 0
    assert "[Slack Failed]" in pending[0]['title']
```

### 3. Manual Testing Checklist

**Before PR**:

- [ ] Test daemon start notification
- [ ] Test daemon stop notification
- [ ] Test daemon error notification
- [ ] Test priority completion notification
- [ ] Test PR creation notification
- [ ] Test daily summary (change time to current+1 min)
- [ ] Test with SLACK_ENABLED=false (should be no-op)
- [ ] Test with invalid bot token (should fallback to DB)
- [ ] Test rate limiting (send 10 messages rapidly)
- [ ] Test retry logic (temporarily break network)

---

## Implementation Plan

### Phase 1: Core Infrastructure (3 hours)

**Tasks**:
1. Create package structure:
   - `coffee_maker/integrations/slack/__init__.py`
   - `coffee_maker/integrations/slack/client.py`
   - `coffee_maker/integrations/slack/notifier.py`
   - `coffee_maker/integrations/slack/formatters.py`
   - `coffee_maker/integrations/slack/config.py`

2. Install `slack-sdk` dependency:
   ```bash
   poetry add slack-sdk
   ```

3. Implement `SlackConfig`:
   - Load from environment
   - Validate configuration
   - Provide defaults

4. Implement `SlackClient`:
   - Initialize Slack WebClient
   - Implement `post_message()` with retry logic
   - Implement rate limiting
   - Implement `test_connection()`

**Deliverables**:
- [ ] Package structure created
- [ ] slack-sdk installed
- [ ] SlackConfig implemented
- [ ] SlackClient implemented
- [ ] Basic unit tests passing

### Phase 2: Message Formatting (2 hours)

**Tasks**:
1. Implement all formatters in `formatters.py`:
   - `DaemonLifecycleFormatter`
   - `PriorityCompletionFormatter`
   - `PRStatusFormatter`
   - `SystemAlertFormatter`
   - `DailySummaryFormatter`

2. Use Slack Block Kit for rich formatting

3. Add comprehensive docstrings with example outputs

**Deliverables**:
- [ ] All formatters implemented
- [ ] Block Kit structures validated
- [ ] Formatter unit tests passing

### Phase 3: High-Level Notifier (2 hours)

**Tasks**:
1. Implement `SlackNotifier`:
   - All notify_* methods
   - Fallback to NotificationDB
   - Configuration handling

2. Implement graceful degradation

3. Add comprehensive logging

**Deliverables**:
- [ ] SlackNotifier implemented
- [ ] Fallback logic working
- [ ] Unit tests passing

### Phase 4: Daemon Integration (1.5 hours)

**Tasks**:
1. Integrate into `daemon.py`:
   - Initialize SlackNotifier
   - Add hooks for lifecycle events
   - Add hooks for priority completion
   - Add hooks for PR creation

2. Implement daily summary scheduler

3. Test with daemon in dev mode

**Deliverables**:
- [ ] Daemon integration complete
- [ ] All hooks working
- [ ] Daily scheduler functional

### Phase 5: Configuration & Documentation (1 hour)

**Tasks**:
1. Update `.env.example`:
   - Add Slack configuration variables
   - Add setup instructions

2. Create setup guide in README.md

3. Test configuration validation

**Deliverables**:
- [ ] .env.example updated
- [ ] README.md updated
- [ ] Configuration validation working

### Phase 6: Testing & Validation (2.5 hours)

**Tasks**:
1. Write comprehensive unit tests (target: 80%+ coverage)

2. Write integration tests

3. Manual testing checklist

4. Fix any bugs found

**Deliverables**:
- [ ] 20+ unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing checklist complete
- [ ] All bugs fixed

### Phase 7: PR & Documentation (1 hour)

**Tasks**:
1. Run full test suite

2. Create PR with detailed description

3. Update ROADMAP.md status

4. Add implementation notes

**Deliverables**:
- [ ] PR created
- [ ] ROADMAP.md updated
- [ ] Implementation documented

**Total Estimated Time**: 13 hours (vs. original estimate: 8-12 hours)

---

## Success Criteria

### Functional Criteria

- [ ] **FC-01**: Daemon start/stop/error notifications sent to Slack
- [ ] **FC-02**: Priority completion notifications include summary and metrics
- [ ] **FC-03**: PR creation notifications include PR link and branch
- [ ] **FC-04**: Daily summaries sent at configured time
- [ ] **FC-05**: All messages use rich Slack Block Kit formatting
- [ ] **FC-06**: Graceful fallback to NotificationDB when Slack fails
- [ ] **FC-07**: SLACK_ENABLED=false disables all Slack notifications

### Technical Criteria

- [ ] **TC-01**: Test coverage ≥ 80% for Slack integration code
- [ ] **TC-02**: All unit tests passing
- [ ] **TC-03**: All integration tests passing
- [ ] **TC-04**: Manual testing checklist complete
- [ ] **TC-05**: Rate limiting enforced (1 message/second)
- [ ] **TC-06**: Retry logic implemented with exponential backoff
- [ ] **TC-07**: Comprehensive logging for all operations
- [ ] **TC-08**: No daemon crashes from Slack failures

### Documentation Criteria

- [ ] **DC-01**: .env.example updated with Slack configuration
- [ ] **DC-02**: README.md includes Slack setup guide
- [ ] **DC-03**: All classes/methods have comprehensive docstrings
- [ ] **DC-04**: Block Kit examples documented in formatters.py
- [ ] **DC-05**: Troubleshooting guide for common issues

### Acceptance Criteria

- [ ] **AC-01**: User can configure Slack integration via .env
- [ ] **AC-02**: User receives real-time notifications for daemon events
- [ ] **AC-03**: User receives daily progress summaries
- [ ] **AC-04**: User can disable Slack without affecting daemon
- [ ] **AC-05**: System degrades gracefully if Slack unavailable
- [ ] **AC-06**: PR approved and merged to main branch
- [ ] **AC-07**: ROADMAP.md status updated to ✅ Complete

---

## Appendix

### A. Slack API References

- **Slack Block Kit Builder**: https://api.slack.com/block-kit/building
- **slack-sdk Python Library**: https://slack.dev/python-slack-sdk/
- **Slack API Methods**: https://api.slack.com/methods
- **Rate Limits**: https://api.slack.com/docs/rate-limits
- **Error Handling**: https://api.slack.com/docs/error-handling

### B. Example Block Kit Messages

See `coffee_maker/integrations/slack/formatters.py` for full examples.

### C. Troubleshooting

**Problem**: "invalid_auth" error

**Solution**: Verify bot token starts with `xoxb-` and is valid

---

**Problem**: "channel_not_found" error

**Solution**: Verify channel ID format (C123456789) and bot has access

---

**Problem**: "rate_limited" error

**Solution**: Check SLACK_RATE_LIMIT, reduce notification frequency

---

**Problem**: Messages not appearing in Slack

**Solution**: Check bot permissions (chat:write, chat:write.public)

---

## Conclusion

This specification provides a comprehensive blueprint for implementing Slack integration in MonolithicCoffeeMakerAgent. The system will provide real-time visibility into autonomous development operations, enabling remote monitoring and team collaboration.

**Next Steps**:
1. Review and approve this specification
2. Proceed with Phase 1 implementation
3. Test incrementally after each phase
4. Create PR when all success criteria met

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Author**: code_developer (autonomous agent)
**Status**: ✅ Ready for Implementation
