# Agent Management Scripts

Scripts for managing autonomous agents (code_developer, project_manager).

## Quick Reference

```bash
# Start agents
./scripts/start_agents.sh

# Check health
./scripts/agent_health_check.sh

# Stop agents
./scripts/stop_agents.sh

# Install auto-start (run once)
./scripts/install_autostart.sh
```

## Scripts

### `start_agents.sh`
Starts the code_developer daemon in the background.

**Usage**:
```bash
./scripts/start_agents.sh

# Output:
# ✓ code_developer daemon started (PID: 12345)
# ✓ project_manager: Available in Claude CLI
```

**What it does**:
- Checks if daemon already running
- Starts `poetry run code-developer --auto-approve`
- Logs to `daemon.log`
- Shows status dashboard

### `stop_agents.sh`
Stops the code_developer daemon.

**Usage**:
```bash
./scripts/stop_agents.sh

# Output:
# ✓ code_developer daemon stopped
```

**What it does**:
- Finds daemon process
- Sends kill signal
- Force kills if needed

### `agent_health_check.sh`
Checks if agents are running and healthy.

**Usage**:
```bash
./scripts/agent_health_check.sh

# Exit codes:
#   0 = All healthy
#   1 = Some agents down
```

**Output**:
```
=== Agent Health Check ===
✓ code_developer daemon: RUNNING
  PID: 12345
  Uptime: 2:15:30

╭─────────────── Developer Status ───────────────╮
│ State:  🟢 WORKING                            │
│  Task:  PRIORITY 5: Analytics Dashboard        │
│  Progress: ████████░░░░░░░░░░░░░░ 30%        │
╰────────────────────────────────────────────────╯

=== Health Summary ===
✓ All agents healthy
```

### `install_autostart.sh`
Installs system service to auto-start agents on boot.

**Usage**:
```bash
./scripts/install_autostart.sh
```

**Platforms**:
- **macOS**: Creates launchd plist in `~/Library/LaunchAgents/`
- **Linux**: Creates systemd service in `~/.config/systemd/user/`

**Commands after install**:

**macOS**:
```bash
# Start
launchctl start com.coffeemaker.agents

# Stop
launchctl stop com.coffeemaker.agents

# Uninstall
launchctl unload ~/Library/LaunchAgents/com.coffemaker.agents.plist
rm ~/Library/LaunchAgents/com.coffemaker.agents.plist
```

**Linux**:
```bash
# Start
systemctl --user start coffeemaker-agents

# Stop
systemctl --user stop coffeemaker-agents

# Status
systemctl --user status coffeemaker-agents

# Logs
journalctl --user -u coffeemaker-agents -f

# Uninstall
systemctl --user disable coffeemaker-agents
rm ~/.config/systemd/user/coffeemaker-agents.service
```

## Testing Scripts

### `test_sound_notifications.py`
Tests the sound notification system.

**Usage**:
```bash
poetry run python scripts/test_sound_notifications.py
```

**What it tests**:
- Normal priority sounds
- High priority sounds
- Critical priority sounds
- Silent notifications

### `test_project_manager_warnings.py`
Tests the project_manager warning system.

**Usage**:
```bash
poetry run python scripts/test_project_manager_warnings.py
```

**What it tests**:
- Critical blocker warnings
- High priority warnings
- Normal warnings
- Low priority suggestions

## Integration with Other Tools

### With Poetry

All scripts use Poetry for Python execution:

```bash
# Daemon uses this internally:
poetry run code-developer --auto-approve

# Status checks use:
poetry run project-manager developer-status
```

### With Git

Agents auto-commit and create PRs:

```bash
# View daemon's commits
git log --author="Claude"

# Check daemon's branches
git branch | grep "feature/priority"
```

### With Claude CLI

The project_manager agent is always available in Claude CLI:

```bash
# Explicit invocation
claude
> /agent-project-manager
> What's the project health?

# Or automatic delegation
claude --message "Analyze ROADMAP health"
```

## Logs

### Daemon Logs

```bash
# Main log (daemon output)
tail -f daemon.log

# Agent startup log (if using auto-start)
tail -f ~/.coffee_maker/agents.log

# Agent errors (if using auto-start)
tail -f ~/.coffee_maker/agents.error.log
```

### Notification Logs

```bash
# View all notifications
poetry run project-manager notifications

# Database location
ls ~/.coffee_maker/notifications.db
```

### Status Files

```bash
# Current daemon status (JSON)
cat ~/.coffee_maker/daemon_status.json | jq

# Daemon PID file
cat ~/.coffee_maker/daemon.pid
```

## Troubleshooting

### "Daemon already running"

```bash
# Find existing process
pgrep -f code-developer

# Kill it
pkill -f code-developer

# Start fresh
./scripts/start_agents.sh
```

### "Permission denied"

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### "Poetry not found"

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or use pip
pip install poetry
```

### Auto-start not working (macOS)

```bash
# Check if loaded
launchctl list | grep coffeemaker

# Check logs
cat ~/.coffee_maker/agents.log

# Reload
launchctl unload ~/Library/LaunchAgents/com.coffemaker.agents.plist
launchctl load ~/Library/LaunchAgents/com.coffemaker.agents.plist
```

### Auto-start not working (Linux)

```bash
# Check status
systemctl --user status coffeemaker-agents

# Check logs
journalctl --user -u coffeemaker-agents --no-pager

# Restart
systemctl --user restart coffeemaker-agents
```

## Advanced Usage

### Custom Health Checks in CI/CD

```yaml
# .github/workflows/health-check.yml
name: Agent Health

on:
  schedule:
    - cron: '0 */6 * * *'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Health check
        run: ./scripts/agent_health_check.sh
```

### Monitoring with cron

```bash
# Add to crontab
crontab -e

# Check health every hour and log
0 * * * * cd /path/to/project && ./scripts/agent_health_check.sh >> ~/.coffee_maker/health.log 2>&1
```

### Email Alerts

```bash
# Create wrapper script: scripts/health_check_with_alert.sh
#!/bin/bash
if ! ./scripts/agent_health_check.sh; then
    echo "Agents down!" | mail -s "Agent Alert" you@example.com
fi
```

## Related Documentation

- **Agent Management Guide**: `docs/AGENT_MANAGEMENT.md`
- **Agent Definitions**: `.claude/agents/*.md`
- **Project Instructions**: `.claude/CLAUDE.md`
- **ROADMAP**: `docs/ROADMAP.md`

---

**Version**: 1.0
**Last Updated**: 2025-10-12
