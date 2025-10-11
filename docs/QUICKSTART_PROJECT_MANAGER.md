# Project Manager - Quick Start Guide (5 minutes)

Get up and running with Coffee Maker's Project Manager CLI in just a few minutes.

## What is Project Manager?

**Project Manager** is a command-line tool that helps you manage your development roadmap, track progress, and communicate with the autonomous code developer daemon. Think of it as your AI project manager that keeps everything organized.

**Key Features:**
- 📋 View and manage your ROADMAP.md
- 🔔 Handle notifications from the autonomous daemon
- ✅ Approve/respond to implementation questions
- 📊 Track development progress

## Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)
- Git repository with a ROADMAP.md file

## Installation

### Option 1: Development Setup (Recommended for Contributors)

```bash
# Clone the repository
git clone https://github.com/Bobain/MonolithicCoffeeMakerAgent.git
cd MonolithicCoffeeMakerAgent

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell

# Verify installation
project-manager --help
```

### Option 2: Direct Installation (Future - PyPI)

```bash
# Once published to PyPI (PRIORITY 3)
pip install coffee-maker

# Verify installation
project-manager --help
```

## Your First Command: View the Roadmap

Let's start by viewing your project roadmap:

```bash
# View the full roadmap (first 100 lines)
project-manager view
```

**Expected Output:**
```
================================================================================
Coffee Maker Agent - ROADMAP
================================================================================

# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-09
**Current Branch**: `feature/priority-2.5`
**Status**: PRIORITY 2-6 ✅ 100% COMPLETE
...
```

### View a Specific Priority

```bash
# View just PRIORITY 1
project-manager view 1

# Or use the full name
project-manager view PRIORITY-2
```

## Check for Notifications

The autonomous daemon may ask questions or send updates. Check for notifications:

```bash
# List all pending notifications
project-manager notifications
```

**If you have notifications:**
```
================================================================================
Pending Notifications
================================================================================

⚠️  HIGH:
  [5] PRIORITY 2.5: Needs Manual Review
      Claude API completed successfully but made no file changes.

      Possible actions:
      1. Review priority description - is it concrete enough?
      2. Manually implement this priority
      3. Mark as "Manual Only" in ROADMAP
      4. Skip and move to next priority

      Type: info | Created: 2025-10-09 19:08:30

Total: 1 pending notification(s)

Tip: Use 'project-manager respond <id> <response>' to respond
```

### Respond to a Notification

```bash
# Respond with approval
project-manager respond 5 approve

# Respond with custom message
project-manager respond 5 "Skip this priority and move to the next one"
```

## Run the Autonomous Daemon

Want the AI to implement features autonomously? Start the daemon:

```bash
# Set your Anthropic API key (required)
export ANTHROPIC_API_KEY='your-api-key-here'

# Start the daemon in autonomous mode
python run_daemon.py --auto-approve
```

**The daemon will:**
1. Read ROADMAP.md to find the next planned priority
2. Use the Anthropic API to implement it
3. Create/modify files as needed
4. Commit changes to git
5. Create pull requests
6. Send you notifications for review

## ✨ NEW: Interactive Chat with Daemon Control (US-009)

**The project-manager now includes an interactive chat interface with full daemon control!**

### Start Chat Mode

```bash
poetry run project-manager chat
```

**You'll see**:
```
🤖 Welcome to Coffee Maker - AI Project Manager

✨ New Features:
  • Streaming responses - Text appears progressively
  • ↑/↓ - Navigate input history
  • Tab - Auto-complete commands and priorities
  • Shift+Enter - Multi-line input

📊 Status: 🟢 Daemon: Active - Working on PRIORITY 5
         Use /status for detailed info, /start to launch daemon

You: _
```

### Daemon Control Commands (NEW!)

**Check Daemon Status**:
```
/status
```

Shows:
- PID, uptime, CPU, memory
- Current task
- Whether daemon is running/idle/stopped

**Start Daemon**:
```
/start
```

Launches the daemon in the background. No need for separate terminal!

**Stop Daemon**:
```
/stop
```

Gracefully shuts down the daemon.

**Restart Daemon**:
```
/restart
```

### Talk to the Daemon (NEW!)

**Natural Language Communication**:
```
You: Ask daemon to implement PRIORITY 5

✅ Command Sent to Daemon (Notification #42)

Your message has been delivered to code_developer.

⏰ Response Time: He may take 12+ hours to respond.
   Like a human developer, he needs focus time and rest periods.
```

**Check for Daemon Questions**:

The chat automatically shows daemon questions every 10 messages:
```
📋 Daemon Has Questions:

  #41: Dependency Approval
  Should I install pytest for testing?

Use /notifications to view and respond
```

**Respond to Daemon**:
```
You: /respond 41 "Yes, use pytest"
```

### Chat Features

**Multi-line Input** (Shift+Enter):
```
You: Add a new priority:
     - Create authentication
     - Add tests
     - Update docs
     [Press Enter to send]
```

**History Navigation** (↑/↓):
Press ↑ to recall previous commands

**Auto-completion** (Tab):
Type `/sta` then press Tab → `/status`

**Syntax Highlighting**:
Code blocks in responses are automatically highlighted

### Example Chat Session

```
You: /status
Claude: 🟢 Daemon Status: RUNNING
        - PID: 12345
        - Status: WORKING
        - Current Task: PRIORITY 5: Authentication
        - Uptime: 2 hours
        - CPU: 15.2%
        - Memory: 45.3 MB

You: What is the daemon working on?
Claude: The daemon is currently implementing PRIORITY 5:
        User Authentication with email/password and OAuth...

You: Ask daemon to add tests for authentication
Claude: ✅ Command sent to daemon (Notification #43)

You: /exit
Claude: Thank you for using Coffee Maker!
```

## Common Workflows

### Daily Check-In (Updated!)

**Option A: Using Chat (Recommended)**
```bash
poetry run project-manager chat

# Then in chat:
/status                  # Check daemon status
/notifications           # See daemon questions
Ask daemon to...         # Send commands
/exit                    # When done
```

**Option B: Using CLI Commands**
```bash
# 1. Check notifications
project-manager notifications

# 2. View roadmap to see progress
project-manager view

# 3. Respond to any pending questions
project-manager respond <id> <your-response>
```

### Review Daemon Progress

```bash
# Check what the daemon is working on
project-manager view

# Look for priorities marked "🔄 In Progress"
# Check git for recent commits
git log --oneline -10
```

### Troubleshooting

**Problem: "Command not found: project-manager"**
```bash
# Make sure you're in the poetry shell
poetry shell

# Verify installation
which project-manager
```

**Problem: "ROADMAP not found"**
```bash
# Make sure you're in the project root directory
cd /path/to/MonolithicCoffeeMakerAgent

# Verify ROADMAP.md exists
ls docs/ROADMAP.md
```

**Problem: "ANTHROPIC_API_KEY not set" (daemon)**
```bash
# Set the key in .env file (recommended)
echo "ANTHROPIC_API_KEY=your-key-here" >> .env

# Or export it in your shell
export ANTHROPIC_API_KEY='your-key-here'
```

**Problem: "project-manager chat" forces API mode when running inside Claude Code**

When you run `project-manager chat` from within Claude Code (the Claude CLI interface), it automatically detects CLI nesting and switches to API mode to prevent issues.

**What's happening:**
- Claude Code is running on Claude CLI
- Running `project-manager chat` would try to call Claude CLI again (nesting)
- The system detects this and uses API mode instead

**Solutions:**

Option 1: Run from regular terminal (Recommended - Free)
```bash
# Open a new terminal (not Claude Code)
cd /path/to/MonolithicCoffeeMakerAgent
poetry run project-manager chat
```
This will use Claude CLI mode and is free with your subscription.

Option 2: Use API mode with credits
```bash
# Add API key to your .env file
echo "ANTHROPIC_API_KEY=your-key-here" >> .env

# Then run from Claude Code
poetry run project-manager chat
```
This will use API mode with your API credits.

**Why this matters:**
- CLI nesting (Claude CLI calling Claude CLI) can cause unexpected behavior
- The system automatically prevents this by detecting when you're already inside Claude Code
- You'll see a clear message explaining the situation and your options

## Next Steps

Now that you have the basics:

1. **📖 Read the Full Documentation**
   - [User Journey Guide](USER_JOURNEY_PROJECT_MANAGER.md) - Understand the complete workflow
   - [Feature Reference](PROJECT_MANAGER_FEATURES.md) - All commands and options
   - [Slack Setup Guide](SLACK_SETUP_GUIDE.md) - Get notifications in Slack

2. **🎯 Customize Your Roadmap**
   - Edit `docs/ROADMAP.md` to add your priorities
   - Follow the format in existing priorities
   - Be specific about deliverables to help the daemon

3. **🤖 Let the Daemon Work**
   - Run `python run_daemon.py --auto-approve`
   - Check notifications with `project-manager notifications`
   - Review PRs before merging

4. **🔧 Advanced Configuration**
   - See ROADMAP.md lines 5044-5330 for Phase 2 features
   - Customize notification preferences
   - Set up Slack integration

## Quick Reference Card

```bash
# View roadmap
project-manager view                  # Full roadmap
project-manager view 2                # Specific priority

# Notifications
project-manager notifications         # List pending
project-manager respond <id> <msg>    # Respond

# Daemon (future)
project-manager status                # Daemon status
project-manager sync                  # Sync roadmap

# Get help
project-manager --help                # Show all commands
project-manager view --help           # Command-specific help
```

## Getting Help

- **Documentation**: See `docs/` folder for detailed guides
- **Issues**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- **Roadmap**: Check `docs/ROADMAP.md` for planned features

---

**Time to Complete**: ⏱️  5 minutes

**Ready for More?** Check out the [User Journey Guide](USER_JOURNEY_PROJECT_MANAGER.md) for a deeper understanding of how Project Manager fits into your workflow.
