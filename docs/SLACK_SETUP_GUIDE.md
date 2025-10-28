# Slack Integration - Setup Guide

Get daemon notifications delivered directly to your Slack workspace. This guide walks you through setting up Slack integration for Coffee Maker's Project Manager.

---

## Status

⚠️  **Slack integration is planned for Phase 2** (see ROADMAP.md)

This guide documents the planned implementation to help you prepare. Basic notification functionality will be available soon.

---

## Prerequisites

Before setting up Slack integration:

✅ **Technical Requirements:**
- Project Manager CLI installed and working
- Slack workspace where you have admin access (or know who to ask)
- Ability to create Slack apps in your workspace
- Python 3.11+ environment

✅ **Permissions Needed:**
- `chat:write` - Send messages to channels
- `chat:write.public` - Send messages to public channels
- `incoming-webhook` - Post messages via webhook (simpler alternative)
- `commands` - Slash commands (future: `/roadmap status`)
- `interactivity` - Interactive buttons (future: approve/reject actions)

**Estimated Setup Time**: 15-20 minutes

---

## Architecture Overview

```
┌─────────────────┐
│ Daemon          │
│  run_code_developer.py  │
└────────┬────────┘
         │
         │ Creates notifications
         ↓
┌─────────────────┐
│ Notification DB │
│  notifications  │
│  .db            │
└────────┬────────┘
         │
         │ Polls for new
         ↓
┌─────────────────┐
│ Slack Notifier  │
│  (Future)       │
└────────┬────────┘
         │
         │ Sends via Webhook/Bot
         ↓
┌─────────────────┐
│ Slack Channel   │
│  #dev-updates   │
└─────────────────┘
```

---

## Setup Steps

### Step 1: Create Slack App (5 minutes)

1. **Go to Slack App Dashboard**
   - Visit: https://api.slack.com/apps
   - Click **"Create New App"**
   - Select **"From scratch"**

2. **Configure App Details**
   ```
   App Name: Coffee Maker Project Manager
   Workspace: [Your Workspace]
   ```

3. **Add App Icon** (Optional)
   - Upload a coffee cup icon or robot emoji
   - Helps identify bot messages

**Result**: You should see your app in the dashboard

---

### Step 2: Configure Bot Permissions (5 minutes)

1. **Navigate to OAuth & Permissions**
   - Sidebar → Features → OAuth & Permissions

2. **Add Bot Token Scopes**

   Click **"Add an OAuth Scope"** under "Bot Token Scopes":

   **Required Scopes:**
   - `chat:write` - Send messages as the bot
   - `chat:write.public` - Post to public channels without joining

   **Optional (Future Features):**
   - `commands` - For slash commands like `/roadmap`
   - `interactivity` - For interactive buttons

3. **Save Changes**

**Result**: Scopes should be listed under "Bot Token Scopes"

---

### Step 3: Install App to Workspace (2 minutes)

1. **Install App**
   - Still in OAuth & Permissions
   - Click **"Install to Workspace"** (top of page)
   - Review permissions
   - Click **"Allow"**

2. **Copy Bot Token**
   ```
   Token format: xoxb-[numbers]-[numbers]-[random-string]
   Example: xoxb-XXXXXXXXXXXX-XXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXX
   ```

   **⚠️  IMPORTANT**: This token is a secret! Never commit it to git.

3. **Store Token Securely**
   ```bash
   # Add to .env file (recommended)
   echo "SLACK_BOT_TOKEN=xoxb-..." >> .env

   # Verify .env is in .gitignore
   grep ".env" .gitignore
   ```

**Result**: Bot is now installed in your workspace

---

### Step 4: Get Channel ID (3 minutes)

1. **Find Your Target Channel**
   - Open Slack
   - Go to the channel where you want notifications (e.g., `#dev-updates`)

2. **Get Channel ID**

   **Method 1 - From Channel Details:**
   - Right-click channel name → View channel details
   - Scroll to bottom
   - Channel ID shown as: `C01234ABCDE`

   **Method 2 - From URL:**
   - Click on channel
   - Look at URL: `https://yourworkspace.slack.com/archives/C01234ABCDE`
   - ID is the part after `/archives/`

3. **Store Channel ID**
   ```bash
   # Add to .env
   echo "SLACK_CHANNEL_ID=C01234ABCDE" >> .env
   ```

**Result**: You have both bot token and channel ID

---

### Step 5: Configure Project Manager (3 minutes)

1. **Update .env File**

   Your `.env` should now contain:
   ```bash
   # Anthropic API (for daemon)
   ANTHROPIC_API_KEY=sk-ant-...

   # Slack Integration
   SLACK_BOT_TOKEN=xoxb-...
   SLACK_CHANNEL_ID=C01234ABCDE
   ```

2. **Verify Configuration**
   ```bash
   # Check .env is loaded
   cat .env | grep SLACK

   # Verify not in git
   git status .env  # Should be ignored
   ```

3. **Test Connection** (Future - Once implemented)
   ```bash
   # This command doesn't exist yet (Phase 2)
   project-manager slack test
   ```

**Result**: Configuration complete

---

### Step 6: Test Notification (5 minutes)

**Manual Test** (Until automatic integration is ready):

```python
# test_slack.py
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
channel_id = os.environ["SLACK_CHANNEL_ID"]

try:
    # Send test message
    response = client.chat_postMessage(
        channel=channel_id,
        text="🤖 Project Manager Slack integration test",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Coffee Maker Project Manager*\n✅ Slack integration is working!"
                }
            }
        ]
    )
    print("✅ Message sent successfully!")
    print(f"Message timestamp: {response['ts']}")

except SlackApiError as e:
    print(f"❌ Error sending message: {e.response['error']}")
```

```bash
# Install Slack SDK (if not already)
pip install slack-sdk

# Run test
python test_slack.py
```

**Expected Output:**
```
✅ Message sent successfully!
Message timestamp: 1234567890.123456
```

**Check Slack**: You should see the test message in your channel!

---

## What You'll Receive

Once Slack integration is fully implemented, you'll receive notifications for:

### 🚨 Critical Notifications

**Example:**
```
🚨 CRITICAL: Daemon Crashed Multiple Times

The daemon has crashed 3 times and has stopped.

Check logs for details:
  • Last error: Connection timeout
  • Crashed at: 2025-10-09 14:32:15

Actions:
  • View logs: project-manager logs
  • Restart: python run_code_developer.py --auto-approve
```

### ⚠️ High Priority Notifications

**Example:**
```
⚠️ HIGH: PRIORITY 2.5 Needs Manual Review

Claude API completed successfully but made no file changes.

Possible actions:
  1. Review priority description
  2. Manually implement this priority
  3. Mark as "Manual Only" in ROADMAP

Respond:
  • project-manager respond 15 approve
  • project-manager respond 15 skip
```

### ✅ Success Notifications

**Example:**
```
✅ PRIORITY 3 Complete!

Implementation complete!

PR: https://github.com/user/repo/pull/123

Files changed:
  • coffee_maker/api/endpoints.py (new)
  • tests/test_api.py (new)
  • docs/API.md (new)

Please review and merge.
```

### 📊 Progress Updates

**Example:**
```
📊 Daily Summary

Yesterday's activity:
  • 3 priorities completed
  • 5 PRs created
  • 12 files modified
  • 0 critical issues

Current: PRIORITY 4 (60% complete)
Next: PRIORITY 5 (scheduled)
```

---

## Interactive Features (Future)

### Slash Commands

Once implemented, you'll be able to use:

```
/roadmap status           → Show current daemon status
/roadmap view 3           → View PRIORITY 3 details
/roadmap notifications    → List pending notifications
/roadmap respond 15 ok    → Respond to notification
```

### Interactive Buttons

Notifications will include action buttons:

```
⚠️ HIGH: Implementation Question

Should I use FastAPI or Flask for the REST API?

Context:
  • FastAPI has better async support
  • Flask is more familiar to the team

[Choose FastAPI]  [Choose Flask]  [Skip]
```

Clicking a button responds automatically!

---

## Customization

### Notification Preferences (Future)

```python
# coffee_maker/config.py

SLACK_CONFIG = {
    # Which notifications to send
    "notification_levels": ["critical", "high"],  # Skip "normal"

    # Quiet hours (no non-critical notifications)
    "quiet_hours": {
        "enabled": True,
        "start": "22:00",  # 10 PM
        "end": "08:00"     # 8 AM
    },

    # Rate limiting
    "max_per_hour": 10,  # Max 10 notifications/hour

    # Message format
    "use_blocks": True,   # Rich formatting
    "include_links": True # Add GitHub/docs links
}
```

### Channel Routing (Future)

Send different types to different channels:

```python
SLACK_CHANNELS = {
    "critical": "C-ONCALL",        # #on-call for critical
    "high": "C-DEV-UPDATES",       # #dev-updates for high
    "normal": "C-BOT-SPAM",        # #bot-spam for normal
    "summary": "C-DAILY-STANDUP"   # #daily-standup for summaries
}
```

---

## Troubleshooting

### "Not in Channel" Error

**Problem:**
```
Error: not_in_channel
```

**Solution:**
```bash
# Option 1: Invite bot to channel (in Slack)
/invite @Coffee Maker Project Manager

# Option 2: Use chat:write.public scope (set in Step 2)
# This allows posting without joining
```

### "Invalid Token" Error

**Problem:**
```
Error: invalid_auth
```

**Solutions:**
1. **Check token format**: Should start with `xoxb-`
2. **Regenerate token**:
   - Slack App Dashboard → OAuth & Permissions
   - Click "Reinstall App"
   - Copy new token
3. **Update .env file** with new token

### Messages Not Appearing

**Checklist:**
- [ ] Bot is installed in workspace
- [ ] Channel ID is correct (starts with `C`)
- [ ] Bot has `chat:write` permission
- [ ] Token is in .env and loaded correctly
- [ ] No typos in channel ID

**Debug:**
```bash
# Check environment variables
env | grep SLACK

# Test connection manually (see Step 6)
python test_slack.py
```

### Rate Limiting

**Problem:**
```
Error: rate_limited
```

**Cause**: Sending too many messages too quickly

**Solution:**
```python
# Add rate limiting (future implementation)
import time

def send_notification(message):
    # Wait between sends
    time.sleep(1)
    client.chat_postMessage(...)
```

---

## Security Best Practices

### 🔐 Token Security

**DO:**
- ✅ Store tokens in `.env` file
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables in production
- ✅ Rotate tokens periodically (every 90 days)
- ✅ Use Slack's token rotation feature

**DON'T:**
- ❌ Commit tokens to git
- ❌ Share tokens in Slack/email
- ❌ Use tokens in client-side code
- ❌ Log tokens in application logs

### 🔒 Access Control

**Principle of Least Privilege:**
- Only grant necessary scopes
- Review permissions quarterly
- Remove unused scopes
- Document why each scope is needed

**Workspace Security:**
- Limit who can create apps
- Review installed apps regularly
- Monitor bot activity logs
- Set up audit logging

---

## Webhook Alternative (Simpler Setup)

If you don't need interactive features, use Incoming Webhooks:

### Pros:
- ✅ Simpler setup (no OAuth)
- ✅ No token management
- ✅ Just one URL to configure

### Cons:
- ❌ No interactive buttons
- ❌ No slash commands
- ❌ Can't update/delete messages
- ❌ Limited to one channel per webhook

### Setup:

1. **Enable Incoming Webhooks**
   - Slack App Dashboard → Features → Incoming Webhooks
   - Toggle **On**

2. **Add Webhook to Channel**
   - Click **"Add New Webhook to Workspace"**
   - Select channel
   - Copy webhook URL

3. **Configure**
   ```bash
   # .env
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
   ```

4. **Send Message**
   ```python
   import requests

   webhook_url = os.environ["SLACK_WEBHOOK_URL"]
   requests.post(webhook_url, json={"text": "Hello from Project Manager!"})
   ```

---

## Migration Path

**Phase 1 (Now)**:
- ✅ Manual Slack SDK script
- ✅ Test connection
- ✅ Webhook alternative

**Phase 2 (Next Release)**:
- 🔄 Automatic notification forwarding
- 🔄 `project-manager slack` command
- 🔄 Configuration via CLI

**Phase 3 (Future)**:
- 📅 Interactive buttons
- 📅 Slash commands
- 📅 Rich formatting
- 📅 Thread replies

---

## Getting Help

**Slack API Documentation:**
- https://api.slack.com/docs
- https://api.slack.com/messaging/webhooks

**Coffee Maker Docs:**
- [Quick Start](QUICKSTART_PROJECT_MANAGER.md)
- [User Journey](USER_JOURNEY_PROJECT_MANAGER.md)
- [Features](PROJECT_MANAGER_FEATURES.md)

**Support:**
- GitHub Issues: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- Discussions: https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions

---

**Last Updated**: 2025-10-09
**Version**: Planned for Phase 2
**Status**: 📝 Documentation Only (Implementation Pending)

**Note**: This guide documents the planned implementation. Actual Slack integration will be available in a future release. In the meantime, you can use the manual test script from Step 6 to forward notifications.
