# Agent Management Guide

Guide for managing autonomous agents in the MonolithicCoffeeMakerAgent project.

## Available Agents

### 1. code_developer (Background Daemon)
**Type**: Autonomous background process
**Purpose**: Continuously implements ROADMAP priorities
**Mode**: Runs 24/7 in background

### 2. project_manager (Interactive Agent)
**Type**: Interactive AI assistant
**Purpose**: ROADMAP management, strategic planning, warnings
**Mode**: Available in Claude CLI sessions

## Quick Start

### Start All Agents

```bash
# Start code_developer daemon
./scripts/start_agents.sh

# Check status
./scripts/agent_health_check.sh
```

### Stop All Agents

```bash
./scripts/stop_agents.sh
```

## Auto-Start on Boot

### Install (Run Once)

```bash
# macOS or Linux
./scripts/install_autostart.sh
```

This installs:
- **macOS**: launchd service
- **Linux**: systemd user service

### Verify Auto-Start

```bash
# macOS
launchctl list | grep coffeemaker

# Linux
systemctl --user status coffeemaker-agents
```

## Daily Usage

### code_developer Daemon

```bash
# Check what it's working on
poetry run project-manager developer-status

# View live logs
tail -f daemon.log

# Stop daemon
./scripts/stop_agents.sh

# Restart daemon
./scripts/stop_agents.sh && ./scripts/start_agents.sh
```

### project_manager Agent

```bash
# In Claude CLI interactive mode:
/agent-project-manager

# Or automatic delegation:
claude --message "What's the project status?"
# (Claude will auto-select project_manager agent)
```

## Monitoring

### Health Check

```bash
# Quick status check
./scripts/agent_health_check.sh

# Returns:
#   0 = All healthy
#   1 = Some agents down
#   2 = All agents down
```

### Daemon Status

```bash
# Detailed daemon status (one-time)
poetry run project-manager developer-status

# Output:
# ╭─────────────── Developer Status Dashboard ───────────────╮
# │ State:  🟢 WORKING                                       │
# │  Task:  PRIORITY 5: Analytics Dashboard                  │
# │  Progress: ██████░░░░░░░░░░░░░░░░░░░░░░ 20%            │
# ╰──────────────────────────────────────────────────────────╯

# Live monitoring (auto-refresh every minute)
./scripts/monitor_code_developer.sh

# Custom interval (e.g., every 30 seconds)
./scripts/monitor_code_developer.sh 30
```

### View Notifications

```bash
# See warnings from project_manager
poetry run project-manager notifications

# Will show blockers, warnings, completions
```

## Integration with Claude CLI

### Always-Available project_manager

The project_manager agent is automatically available in Claude CLI:

**Option 1: Explicit Invocation**
```bash
claude
> /agent-project-manager
> What's blocking us?
```

**Option 2: Automatic Selection**
```bash
# Claude automatically selects project_manager for:
claude --message "Analyze the ROADMAP health"
claude --message "What should we prioritize next?"
claude --message "Is US-032 complete?"
```

### Agent Delegation

Agents can call other agents:

```
project_manager
  ↓ (uses Task tool)
  ↓ (finds code)
project_manager
  ↓ (warns user with findings)
```

Example:
```python
# project_manager detects issue
# → Delegates to assistant (with code analysis skills)
# → Warns user with evidence

service.warn_user(
    title="🚨 BLOCKER: US-021 stalled",
    message=f"Code analysis shows: {findings}",
    priority="critical"
)
```

## Configuration

### Project Settings

File: `.claude/settings.local.json`

```json
{
  "agents": {
    "auto_load": ["project_manager", "code_developer"],
    "default_agent": "project_manager"
  },
  "hooks": {
    "on_start": ["scripts/agent_health_check.sh"]
  },
  "notifications": {
    "sound_enabled": true
  }
}
```

### Daemon Configuration

File: `coffee_maker/autonomous/daemon.py`

```python
daemon = DevDaemon(
    roadmap_path="docs/roadmap/ROADMAP.md",
    auto_approve=True,          # Autonomous mode
    create_prs=True,            # Auto-create PRs
    sleep_interval=30,          # Seconds between checks
    model="sonnet",             # Claude model
    max_crashes=3,              # Max crashes before stop
    compact_interval=10         # Context refresh interval
)
```

## Troubleshooting

### Daemon Won't Start

```bash
# Check if already running
pgrep -f code-developer

# Kill existing process
pkill -f code-developer

# Check logs
tail -f daemon.log

# Start fresh
./scripts/start_agents.sh
```

### Daemon Stuck

```bash
# Check status
poetry run project-manager developer-status

# If stalled >3 days, restart:
./scripts/stop_agents.sh
./scripts/start_agents.sh
```

### No Sound Notifications

```bash
# Check sound system (macOS)
which afplay  # Should return path

# Test sound
poetry run python scripts/test_sound_notifications.py

# Check config
cat ~/.coffee_maker/daemon_status.json | grep sound
```

### Auto-Start Not Working

**macOS**:
```bash
# Check if loaded
launchctl list | grep coffeemaker

# View logs
cat ~/.coffee_maker/agents.log

# Reload
launchctl unload ~/Library/LaunchAgents/com.coffemaker.agents.plist
launchctl load ~/Library/LaunchAgents/com.coffemaker.agents.plist
```

**Linux**:
```bash
# Check status
systemctl --user status coffeemaker-agents

# View logs
journalctl --user -u coffeemaker-agents -f

# Restart
systemctl --user restart coffeemaker-agents
```

## Best Practices

### 1. Monitor Regularly

```bash
# Daily check
./scripts/agent_health_check.sh

# Weekly review
poetry run project-manager developer-status
poetry run project-manager notifications
```

### 2. Keep Agents Updated

When updating the codebase:
```bash
# Pull latest changes
git pull

# Restart daemon to pick up changes
./scripts/stop_agents.sh
./scripts/start_agents.sh
```

### 3. Review Warnings

The project_manager agent proactively warns you:
```bash
# Check for warnings
poetry run project-manager notifications

# Respond to critical warnings immediately:
# 🚨 BLOCKER = Act now
# ⚠️ WARNING = Act soon
# 📊 INFO = Be aware
```

### 4. Use Logs

```bash
# Daemon activity
tail -f daemon.log

# Agent health
tail -f ~/.coffee_maker/agents.log

# Errors
tail -f ~/.coffee_maker/agents.error.log
```

## Advanced Usage

### Custom Agent Workflows

Create custom scripts in `scripts/`:

```bash
# Example: Weekly report
./scripts/weekly_agent_report.sh

# Example: Emergency stop all
./scripts/emergency_stop_all.sh
```

### Integration with CI/CD

```yaml
# .github/workflows/agents.yml
name: Agent Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check agent health
        run: ./scripts/agent_health_check.sh
```

## Related Documentation

- **Agent Definitions**: `.claude/agents/*.md`
- **Prompt System**: `.claude/commands/PROMPTS_INDEX.md`
- **Project Instructions**: `.claude/CLAUDE.md`
- **ROADMAP**: `docs/roadmap/ROADMAP.md`

---

**Version**: 1.0
**Last Updated**: 2025-10-12
**Status**: Active - All agents operational
