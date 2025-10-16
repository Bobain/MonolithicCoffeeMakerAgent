# New User Journey - Project Manager CLI

This document maps the complete user journey for Coffee Maker's Project Manager CLI, from discovery through power user workflows.

---

## Discovery Phase (0-5 minutes)

### How Users Find Project Manager

**Primary Paths:**
1. **GitHub README** → Sees "AI-Powered Project Manager" feature → Clicks documentation link
2. **ROADMAP.md** → References to `project-manager` command → Searches for docs
3. **CLI Help** → Runs `project-manager --help` after installation
4. **Search** → "autonomous code development" / "AI project manager CLI"

### First Impression

**What does this tool do?**
> "Project Manager is a CLI that helps you manage development roadmaps and communicate with an autonomous AI developer. It acts as your AI project manager, tracking progress, handling notifications, and coordinating between you and the autonomous code daemon."

**Value Proposition - Why should I use this?**

✅ **For Solo Developers:**
- Automate repetitive development tasks
- Keep roadmap organized without manual updates
- Get notified when AI needs input
- Review and approve changes before merging

✅ **For Small Teams:**
- Central source of truth for project priorities
- Async communication with AI developer
- Track progress without constant check-ins
- Reduce context switching

✅ **For Open Source:**
- Autonomous contributor that follows your roadmap
- Handles documentation and boilerplate
- Creates well-documented PRs
- Frees you to focus on architecture

**Unique Selling Points:**
1. **Autonomous**: AI implements features while you sleep
2. **Safe**: All changes tracked in git, reviewed before merge
3. **Interactive**: Ask questions, provide feedback, guide direction
4. **Transparent**: Full visibility into what AI is doing

---

## Setup Phase (5-15 minutes)

### Prerequisites Check

**What you need:**
- ✅ Python 3.11+ (`python --version`)
- ✅ Poetry installed (`poetry --version`)
- ✅ Git repository (`git status`)
- ✅ Anthropic API key ([get one here](https://console.anthropic.com/))
- ⚠️  ROADMAP.md file (will be created if missing)

**First-Time Experience - Installation**

```bash
# Step 1: Clone (development setup)
git clone https://github.com/Bobain/MonolithicCoffeeMakerAgent.git
cd MonolithicCoffeeMakerAgent

# Step 2: Install dependencies
poetry install
# ⏱️  Takes ~2-3 minutes

# Step 3: Activate environment
poetry shell

# Step 4: Verify installation
project-manager --help
# ✅ Success! You see the help menu
```

**Common Setup Issues:**

| Issue | Solution |
|-------|----------|
| `poetry: command not found` | Install Poetry: `curl -sSL https://install.python-poetry.org \| python3 -` |
| `Python version not supported` | Use pyenv to install Python 3.11+: `pyenv install 3.11` |
| `project-manager: command not found` | Run `poetry shell` first |
| Slow installation | Poetry is installing heavy dependencies (langchain, etc.) - be patient |

### Configuration

**Required: Anthropic API Key**

```bash
# Option 1: .env file (recommended)
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env

# Option 2: Environment variable
export ANTHROPIC_API_KEY='sk-ant-...'

# Verify (daemon only)
python run_daemon.py --help  # Should not error about missing key
```

**Optional: Slack Integration**

See [SLACK_SETUP_GUIDE.md](SLACK_SETUP_GUIDE.md) for Slack notification setup (15 minutes).

### First Run Experience

**Test Drive - View the Roadmap**

```bash
$ project-manager view

================================================================================
Coffee Maker Agent - ROADMAP
================================================================================

# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-09
**Status**: PRIORITY 2-6 ✅ 100% COMPLETE

## 🔴 TOP PRIORITY FOR code_developer (START HERE)
...
```

**What just happened?**
- ✅ Project Manager read `docs/roadmap/ROADMAP.md`
- ✅ Formatted it for terminal display
- ✅ Showed first 100 lines (tip shown for full view)

**Check Notifications (None Yet)**

```bash
$ project-manager notifications

================================================================================
Pending Notifications
================================================================================

✅ No pending notifications
```

**What this means:**
- Notification database initialized (`data/notifications.db`)
- No daemon running yet, so no notifications
- Ready to receive notifications when daemon starts

---

## Daily Usage Phase (Ongoing)

### Morning Routine (5 minutes)

**1. Check What Happened Overnight**

```bash
# View recent git commits
git log --oneline -10

# Check notifications from daemon
project-manager notifications

# Review roadmap progress
project-manager view
```

**Typical Morning Scenario:**
```
You wake up to find:
- 3 new commits from the daemon
- 2 PRs created for review
- 1 notification asking about dependency choice
```

**2. Respond to Daemon Questions**

```bash
# List notifications
$ project-manager notifications

⚠️  HIGH:
  [12] PRIORITY 3: Implementation Question
      Should I use FastAPI or Flask for the REST API?

      Context:
      - FastAPI has better async support
      - Flask is more familiar to the team

      Please respond with your preference.

# Respond
$ project-manager respond 12 "Use FastAPI for better async support"

✅ Responded to notification 12: Use FastAPI for better async support
```

**3. Review and Merge PRs**

```bash
# Check PRs on GitHub
gh pr list

# Review locally
gh pr checkout 123
pytest
git diff main

# Merge if good
gh pr merge 123
```

### Core Workflows

#### Workflow 1: Track Ongoing Work

```bash
# Quick status check
project-manager view | grep "🔄"

# See full details of in-progress priority
project-manager view PRIORITY-2.5

# Check recent activity
git log --since="24 hours ago" --oneline
```

#### Workflow 2: Add New Priority

**Manual (Current):**
```bash
# 1. Edit ROADMAP.md
vim docs/roadmap/ROADMAP.md

# 2. Add new priority section
### PRIORITY 10: New Feature
**Status**: 📝 Planned
**Description**: ...

# 3. Commit
git add docs/roadmap/ROADMAP.md
git commit -m "Add PRIORITY 10: New Feature"

# 4. Daemon will pick it up automatically
```

**Future (Phase 2 - Interactive Chat):**
```bash
$ project-manager chat

> Add a new priority: CSV export feature

✅ Added PRIORITY 10: CSV Export Feature
📋 Deliverables:
   - Export all user data to CSV
   - Add download button in settings
   - Handle large datasets with streaming

Should I start implementing now? [y/N]
```

#### Workflow 3: Handle Daemon Failures

**Scenario: Daemon can't implement vague priority**

```bash
$ project-manager notifications

🚨 CRITICAL:
  [15] PRIORITY 2.5: Max Retries Reached
      The daemon has attempted to implement this priority 3 times but no files were changed.

      This priority requires manual implementation:

      Priority: PRIORITY 2.5
      Title: New User Experience & Documentation
      Status: Skipped after 3 attempts

      Action Required:
      1. Manually implement this priority, OR
      2. Mark as "Manual Only" in ROADMAP.md, OR
      3. Clarify the deliverables to make them more concrete

# Fix: Edit ROADMAP to add concrete deliverables
vim docs/roadmap/ROADMAP.md

# Add specific files to create:
#### Deliverables
1. docs/QUICKSTART.md
2. docs/USER_JOURNEY.md
...

# Daemon will retry on next iteration
```

### Common Commands and Outputs

| Command | Purpose | Output |
|---------|---------|--------|
| `project-manager view` | See full roadmap | First 100 lines of ROADMAP.md |
| `project-manager view 2` | See specific priority | Complete PRIORITY 2 section |
| `project-manager notifications` | Check pending items | List of notifications by priority |
| `project-manager respond <id> <msg>` | Answer daemon question | Confirmation message |
| `project-manager status` | Daemon status | Placeholder (Phase 2) |

### Error Handling and Recovery

**Common Errors:**

**1. Notification Database Locked**
```bash
Error: database is locked

Solution:
# Stop any running daemon processes
pkill -f run_daemon.py

# Database will auto-recover
```

**2. ROADMAP.md Not Found**
```bash
❌ ROADMAP not found: /path/to/docs/roadmap/ROADMAP.md

Solution:
# Make sure you're in project root
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent

# Or specify custom path (future)
project-manager view --roadmap=/custom/path/ROADMAP.md
```

**3. Permission Denied**
```bash
PermissionError: [Errno 13] Permission denied: 'data/notifications.db'

Solution:
# Fix permissions
chmod 755 data/
chmod 644 data/notifications.db
```

---

## Power User Phase (Advanced)

### Advanced Features (Current)

**1. Custom Notification Workflows**

Create scripts to automatically respond to specific notification types:

```bash
# auto_respond.sh
#!/bin/bash

# Get all high-priority notifications
project-manager notifications | grep "HIGH" | while read line; do
    id=$(echo $line | grep -oP '\[\K[0-9]+')

    # Auto-approve documentation tasks
    if [[ "$line" == *"Documentation"* ]]; then
        project-manager respond $id "approve"
    fi
done
```

**2. Roadmap Parsing**

Extract specific sections programmatically:

```python
from coffee_maker.autonomous.roadmap_parser import RoadmapParser

parser = RoadmapParser("docs/roadmap/ROADMAP.md")
next_priority = parser.get_next_planned_priority()
print(f"Next task: {next_priority['name']}")
```

**3. Daemon Control**

Run daemon with custom settings:

```bash
# Custom model
python run_daemon.py --model claude-opus-4

# Custom sleep interval
python run_daemon.py --sleep 60 --auto-approve

# No PRs (commit only)
python run_daemon.py --no-pr --auto-approve

# Verbose logging
python run_daemon.py -v --auto-approve
```

### Customization Options

**1. Custom ROADMAP Location**

```bash
# Set in environment
export ROADMAP_PATH=/custom/path/ROADMAP.md

# Or in code (config.py)
```

**2. Notification Preferences**

Edit `coffee_maker/cli/notifications.py` to customize:
- Notification storage location
- Retention policy (auto-delete old notifications)
- Priority levels

**3. Output Formatting**

Future: Phase 2 will add Rich terminal UI with:
- Color themes
- Progress bars
- Interactive tables
- Streaming output

### Integration with Other Tools

**GitHub CLI (gh)**
```bash
# List PRs created by daemon
gh pr list --author "Claude" --label "autonomous"

# Auto-merge approved PRs
gh pr merge --auto --squash
```

**Git Hooks**
```bash
# Pre-commit: Check for daemon-approved changes
# .git/hooks/pre-commit
if git log -1 --format=%B | grep "Co-Authored-By: Claude"; then
    # Run extra validation for daemon commits
    pytest tests/integration/
fi
```

**CI/CD Integration**
```yaml
# .github/workflows/daemon-pr.yml
name: Validate Daemon PRs

on:
  pull_request:
    branches: [ main ]

jobs:
  validate:
    if: contains(github.event.pull_request.user.login, 'claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run full test suite
        run: pytest --strict
```

---

## Metrics & Success Indicators

### After 1 Day
- ✅ Installed and ran first command
- ✅ Viewed roadmap successfully
- ✅ Set up API key

### After 1 Week
- ✅ Daemon created first PR
- ✅ Reviewed and merged autonomous change
- ✅ Responded to 3+ notifications
- ✅ Comfortable with daily workflow

### After 1 Month
- ✅ 10+ priorities completed autonomously
- ✅ Custom automation scripts
- ✅ Slack integration (if applicable)
- ✅ Contributing back to project

---

## Future Enhancements (Phase 2)

**Interactive Chat Mode:**
```bash
$ project-manager chat

> What's the status of PRIORITY 3?

Claude: PRIORITY 3 is currently 🔄 In Progress (60% complete).
The daemon has implemented the FastAPI endpoints and tests,
but still needs to add documentation.

Estimated completion: 2-3 hours

> Can you add a new priority for mobile app support?

Claude: Got it! I'll add that to the roadmap. A few questions:
- Which platforms? (iOS, Android, both?)
- Native or cross-platform (React Native, Flutter)?
- Priority level relative to existing items?
```

**Rich Terminal UI:**
- Progress bars for priorities
- Real-time daemon status
- Colorized output
- Interactive menus

See ROADMAP.md lines 5044-5330 for complete Phase 2 specification.

---

## Getting Help

- **Documentation**: Browse `docs/` folder
- **Issues**: Report bugs at https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- **Discussions**: Ask questions in GitHub Discussions
- **Roadmap**: Check planned features in `docs/roadmap/ROADMAP.md`

## Feedback

Help us improve! We want to know:
- What was confusing during setup?
- Which features do you use most?
- What would make your workflow smoother?
- Any friction points we should address?

Please open an issue or discussion on GitHub with your feedback.

---

**Last Updated**: 2025-10-09
**Version**: MVP Phase 1
