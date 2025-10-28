# US-031: Quick Start Guide - Custom AI Development Environment

**Status**: Complete
**Created**: 2025-10-23
**Related**: US-031 - Custom AI Development Environment

## Get Started in 5 Minutes

This guide gets you up and running with the MonolithicCoffeeMakerAgent system quickly.

---

## Prerequisites

```bash
# 1. Python 3.11+
python --version  # Should be 3.11 or higher

# 2. Poetry installed
poetry --version

# 3. Git configured
git config user.name
git config user.email

# 4. API keys (at least one)
echo $ANTHROPIC_API_KEY  # For Claude
echo $OPENAI_API_KEY     # For OpenAI (optional)
echo $GOOGLE_API_KEY     # For Gemini (optional)
```

---

## Installation

```bash
# Clone repository
git checkout MonolithicCoffeeMakerAgent
cd MonolithicCoffeeMakerAgent

# Install dependencies
poetry install

# Verify installation
poetry run project-manager --help
poetry run code-developer --help
```

---

## Your First 3 Commands

### 1. View the ROADMAP (30 seconds)

```bash
poetry run project-manager view

# Output:
# ┌─────────────────────────────────────┐
# │         ROADMAP Overview            │
# ├─────────────────────────────────────┤
# │ Total Priorities: 50                │
# │ Completed: 30 ✅                    │
# │ In Progress: 2 🏗️                   │
# │ Planned: 18 📝                      │
# └─────────────────────────────────────┘
#
# ## PRIORITY 1: Feature X ✅ Complete
# ## PRIORITY 2: Feature Y 🏗️ In Progress
# ## PRIORITY 3: Feature Z 📝 Planned
```

**What this does**: Shows all priorities in your ROADMAP.md

---

### 2. Ask a Question (1 minute)

```bash
poetry run user-listener
```

```
You: What are the main agents in this system?

Agent: The system has 7 specialized agents:

1. user_listener - Primary UI for user interactions
2. code_developer - Autonomous feature implementation
3. project_manager - ROADMAP management
4. architect - Technical specs and ADRs
5. code-reviewer - Quality assurance
6. assistant (with code analysis skills) - Deep code analysis
7. orchestrator - Parallel execution

Each agent specializes in specific tasks. Would you like details on any?

You: /exit
```

**What this does**: Interactive chat with agent routing

---

### 3. Let the Daemon Implement a Feature (Autonomous!)

```bash
# Terminal 1: Start daemon
poetry run code-developer --auto-approve

# Output:
# 🤖 Code Developer Daemon Started
# 📖 Reading ROADMAP.md...
# ✅ Found next priority: PRIORITY 25
# 🏗️  Starting implementation...
# ⏱️  This will take 1-2 hours...

# Terminal 2: Monitor progress
poetry run project-manager developer-status

# Output:
# ┌─────────────────────────────────────┐
# │   Code Developer Status             │
# ├─────────────────────────────────────┤
# │ Status:    Running                  │
# │ Current:   PRIORITY 25              │
# │ Progress:  40% (2/5 criteria)       │
# │ Time:      23m 15s                  │
# │ CPU:       35%                      │
# │ Memory:    420 MB                   │
# └─────────────────────────────────────┘
```

**What this does**: Autonomously implements the next planned priority from ROADMAP.md

---

## The 5 Main Modes

### 1. CLI Mode - Ask Questions

```bash
poetry run user-listener
```

**Use for**:
- Quick questions about code
- Searching for specific functionality
- Interactive exploration

**Example**:
```
You: Find all singleton patterns
# Routes to assistant agent (with code analysis skills)
# Shows all singleton implementations

You: Create a spec for priority 25
# Routes to architect agent
# Generates technical specification
```

---

### 2. Project Manager - View Status

```bash
# View ROADMAP
poetry run project-manager view

# View specific priority
poetry run project-manager view 25

# Check developer status
poetry run project-manager developer-status

# List notifications
poetry run project-manager notifications

# Respond to notification
poetry run project-manager respond 5 approve

# AI chat for ROADMAP management
poetry run project-manager chat
```

**Use for**:
- ROADMAP management
- Status checking
- Notification handling
- Metrics and analytics

---

### 3. Daemon Mode - Autonomous Development

```bash
# Interactive (asks for approval)
poetry run code-developer

# Autonomous (no approval needed)
poetry run code-developer --auto-approve

# Work on specific priority
poetry run code-developer --priority 25

# Skip PR creation
poetry run code-developer --no-pr

# Verbose logging
poetry run code-developer --verbose
```

**Use for**:
- Hands-off feature implementation
- Overnight continuous development
- Autonomous operation

**What it does**:
1. Reads ROADMAP.md
2. Finds next 📝 Planned priority
3. Creates approval notification (unless --auto-approve)
4. Implements feature
5. Runs tests
6. Verifies DoD with Puppeteer (if web feature)
7. Creates commit + PR
8. Marks priority ✅ Complete
9. Sleeps 30s, then repeats

---

### 4. Architect Mode - Technical Design

```bash
# Create technical spec
poetry run architect create-spec 25

# Weekly codebase analysis (CFR-011)
poetry run architect analyze-codebase

# Daily integration workflow
poetry run architect daily-integration

# Check compliance
poetry run architect cfr-011-status
```

**Use for**:
- Creating technical specifications
- Writing ADRs
- Codebase analysis
- Architecture decisions

---

### 5. Orchestrator - Parallel Execution

```bash
# Run 3 priorities in parallel
poetry run orchestrator parallel-priorities 10 11 12

# Monitor status
poetry run orchestrator status

# Health check
poetry run orchestrator health-check
```

**Use for**:
- Speed up development with parallel work
- Run multiple priorities simultaneously
- Complex multi-priority workflows

**What it does**:
1. Creates git worktrees (roadmap-10, roadmap-11, roadmap-12)
2. Starts code_developer in each worktree
3. Tracks all in SQLite database (CFR-014)
4. Monitors progress
5. Merges when complete
6. Cleans up worktrees

---

## Common Workflows

### Workflow 1: View ROADMAP and Check Status

```bash
# 1. View full ROADMAP
poetry run project-manager view

# 2. View specific priority
poetry run project-manager view 25

# 3. Check if daemon is working on it
poetry run project-manager developer-status

# 4. Check notifications
poetry run project-manager notifications
```

---

### Workflow 2: Implement a Feature Autonomously

```bash
# Terminal 1: Start daemon
poetry run code-developer --auto-approve

# Terminal 2: Monitor progress
watch -n 5 'poetry run project-manager developer-status'

# Wait for completion notification
poetry run project-manager notifications

# View completed priority
poetry run project-manager view 25
```

---

### Workflow 3: Add a New Feature Request

```bash
# Option A: CLI with user story detection
poetry run user-listener

# User: "I want email notifications when builds fail"
# System: Detects user story, asks for confirmation
# System: Adds to ROADMAP as US-034

# Option B: Direct project manager chat
poetry run project-manager chat

# User: "Add user story: email notifications on build failure"
# System: Adds to ROADMAP as US-034
```

---

### Workflow 4: Create Technical Spec

```bash
# 1. Create spec for priority
poetry run architect create-spec 25

# 2. Review generated spec
cat docs/architecture/specs/SPEC-025-skill-loading.md

# 3. Edit if needed
vim docs/architecture/specs/SPEC-025-skill-loading.md

# 4. Commit
git add docs/architecture/specs/SPEC-025-skill-loading.md
git commit -m "docs: Add SPEC-025 for skill loading enhancement"
```

---

### Workflow 5: Parallel Development

```bash
# 1. Start orchestrator for 3 priorities
poetry run orchestrator parallel-priorities 10 11 12

# 2. Monitor in another terminal
poetry run orchestrator status

# Output:
# Worker 1: PRIORITY 10 - Running (45% complete)
# Worker 2: PRIORITY 11 - Running (60% complete)
# Worker 3: PRIORITY 12 - Complete ✅

# 3. Wait for all to complete
# Orchestrator automatically merges and cleans up
```

---

## Multi-AI Provider Support

### Configuration

**File**: `config/ai_providers.yaml`

```yaml
providers:
  claude:
    enabled: true
    model: "claude-sonnet-4-5"

  openai:
    enabled: true
    model: "gpt-4-turbo"

  gemini:
    enabled: true
    model: "gemini-2.0-flash-exp"

fallback_strategy:
  enabled: true
  order: ["claude", "openai", "gemini"]
```

### Usage

```bash
# Use specific provider
poetry run code-developer --provider claude
poetry run code-developer --provider openai
poetry run code-developer --provider gemini

# Automatic fallback (default)
poetry run code-developer --auto-approve
# If Claude rate limited → tries OpenAI
# If OpenAI rate limited → tries Gemini
```

---

## MCP Integration (Puppeteer)

### DoD Verification

When daemon implements web features, it automatically verifies Definition of Done using Puppeteer:

```bash
poetry run code-developer --auto-approve

# After implementing web priority:
# 1. ✅ Implementation complete
# 2. ✅ Tests passing
# 3. 🌐 Launching Puppeteer for DoD verification...
#    - Navigate to http://localhost:8501
#    - Test each acceptance criterion
#    - Take screenshots
#    - Check console for errors
# 4. ✅ DoD verification passed
# 5. 📦 Creating commit + PR
# 6. ✅ PRIORITY 25 complete!
```

**Configuration**: `.claude/mcp/puppeteer.json`

---

## Switching Between Modes

### Same Terminal

```bash
# Use CLI mode
poetry run user-listener
# ... ask questions ...
# /exit

# Then use project manager
poetry run project-manager view
```

### Multiple Terminals

**Recommended for daemon**:

```bash
# Terminal 1: Daemon (long-running)
poetry run code-developer --auto-approve

# Terminal 2: Monitor status
poetry run project-manager developer-status

# Terminal 3: Interactive work
poetry run user-listener
```

### tmux/screen for Multiple Sessions

```bash
# Create tmux session
tmux new -s coffee

# Window 0: Daemon
poetry run code-developer --auto-approve

# Window 1: Monitoring (Ctrl+b c for new window)
watch -n 5 'poetry run project-manager developer-status'

# Window 2: Interactive
poetry run user-listener

# Switch windows: Ctrl+b 0/1/2
# Detach: Ctrl+b d
# Reattach: tmux attach -t coffee
```

---

## Tips & Best Practices

### 1. Run Daemon in Background

```bash
# Use nohup for persistent background execution
nohup poetry run code-developer --auto-approve > daemon.log 2>&1 &

# Check log
tail -f daemon.log

# Monitor status
poetry run project-manager developer-status

# Stop daemon
pkill -f "code-developer"
```

### 2. Monitor Notifications

```bash
# Watch for new notifications
watch -n 10 'poetry run project-manager notifications'

# Or set up a cronjob
* * * * * poetry run project-manager notifications | mail -s "CM Notifications" you@example.com
```

### 3. Use Auto-Approve Carefully

```bash
# First time: Interactive mode
poetry run code-developer

# Once confident: Auto-approve
poetry run code-developer --auto-approve
```

### 4. Parallel Execution Strategy

```bash
# Start with small batch
poetry run orchestrator parallel-priorities 10 11

# Once stable, scale up
poetry run orchestrator parallel-priorities 10 11 12 13 14
```

### 5. Check Status Before Starting

```bash
# Always check first
poetry run project-manager developer-status

# If nothing running, safe to start
poetry run code-developer --auto-approve
```

---

## Troubleshooting

### Issue: "AgentAlreadyRunningError"

**Cause**: Another instance of code_developer is running

**Solution**:
```bash
# Check running agents
ps aux | grep code-developer

# Kill if needed
pkill -f "code-developer"

# Then retry
poetry run code-developer --auto-approve
```

### Issue: "Database is locked"

**Cause**: Multiple processes accessing SQLite simultaneously

**Solution**: Already handled by `@with_retry` decorator. If persists:
```bash
# Check WAL mode
sqlite3 data/notifications.db "PRAGMA journal_mode;"
# Should show: wal

# If not, enable
sqlite3 data/notifications.db "PRAGMA journal_mode=WAL;"
```

### Issue: "Claude CLI not found"

**Cause**: Claude CLI not installed or not in PATH

**Solution**:
```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-cli

# Or specify path
poetry run code-developer --claude-path /path/to/claude
```

### Issue: "Rate limit exceeded"

**Cause**: Too many API calls to Claude

**Solution**:
```bash
# Enable automatic fallback
# Edit config/ai_providers.yaml
fallback_strategy:
  enabled: true
  order: ["claude", "openai", "gemini"]

# Or use API mode with credits
poetry run code-developer --use-api
```

### Issue: "Priority not found"

**Cause**: ROADMAP.md format incorrect

**Solution**:
```bash
# Validate ROADMAP format
poetry run project-manager view

# Check specific priority
poetry run project-manager view 25

# If error, check ROADMAP.md format
# Must be: ## PRIORITY 25: Title
```

---

## Next Steps

Now that you've mastered the basics:

1. **Read the Implementation Guide** - [`US-031-IMPLEMENTATION_GUIDE.md`](US-031-IMPLEMENTATION_GUIDE.md)
   - Technical details
   - Architecture patterns
   - Database schema
   - Git workflow

2. **Read the Feature Comparison** - [`US-031-FEATURE_COMPARISON.md`](US-031-FEATURE_COMPARISON.md)
   - Compare with Claude CLI/Desktop
   - Understand custom enhancements
   - See what makes this system unique

3. **Read the Full User Guide** - [`US-031-USER_GUIDE.md`](US-031-USER_GUIDE.md)
   - Detailed mode explanations
   - Advanced workflows
   - Best practices

4. **Explore the ROADMAP** - `docs/roadmap/ROADMAP.md`
   - See all priorities
   - Understand project direction
   - Find areas to contribute

5. **Check Documentation** - `docs/`
   - `AGENT_OWNERSHIP.md` - Agent responsibilities
   - `WORKFLOWS.md` - Detailed workflows
   - `CLAUDE.md` - Project overview

---

## Summary

You now know how to:
- ✅ View the ROADMAP
- ✅ Ask questions in CLI mode
- ✅ Run autonomous daemon
- ✅ Monitor progress
- ✅ Manage notifications
- ✅ Create specs with architect
- ✅ Run parallel priorities
- ✅ Switch between modes

**Start experimenting!** The system is designed to be intuitive and helpful.

**Most Common Starting Point**:
```bash
poetry run code-developer --auto-approve
```

**Most Common Monitoring**:
```bash
poetry run project-manager developer-status
```

**Most Common Interactive Use**:
```bash
poetry run user-listener
```

---

**Status**: Documentation Complete ✅
**Last Updated**: 2025-10-23
