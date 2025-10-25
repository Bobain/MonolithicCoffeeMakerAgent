---
name: orchestrator-health-monitor
version: 1.0.0
agent: orchestrator
scope: shared
description: Real-time health monitoring, crash detection, auto-respawn, and bug reporting for orchestrator agents
triggers:
  - continuous_work_loop
  - agent_spawn
  - agent_crash
requires:
  - psutil
  - sqlite3
---

# Orchestrator Health Monitor Skill

**Purpose**: Detect agent crashes, orchestrator freezes, and automatically report bugs for immediate fixing

**Auto-Actions**:
- Respawn crashed agents (max 3 retries)
- Report bugs via bug-tracking skill
- Alert on orchestrator loop freeze
- Clean up zombie processes

---

## Quick Start

```python
from orchestrator_health_monitor import OrchestratorHealthMonitor

monitor = OrchestratorHealthMonitor()

# Run health check
status = monitor.check_health()

# Auto-fix issues
monitor.auto_fix_issues()

# Report bugs
monitor.report_bugs_if_any()
```

---

## Core Features

### 1. Agent Crash Detection

Monitors spawned agents and detects crashes by:
- **PID health checks** (every 30s)
- **Log parsing** for ERROR/exception patterns
- **Exit code inspection**

### 2. Orchestrator Loop Freeze Detection

Detects when orchestrator stops polling by:
- **Heartbeat monitoring** (expects log every 30s)
- **State file staleness** (work_loop_state.json)
- **Process responsiveness**

### 3. Auto-Respawn

When agent crashes:
- Record crash in database
- Parse error logs for root cause
- **Respawn agent** (max 3 retries per task)
- **Report bug** if persistent failure

### 4. Bug Auto-Reporting

Creates bug tickets via bug-tracking skill for:
- Agents crashing >3 times on same task
- ImportError/ModuleNotFoundError
- Orchestrator loop freezes
- Zombie processes detected

---

## Health Check Results

```python
{
    "status": "healthy" | "degraded" | "critical",
    "issues": [
        {
            "type": "agent_crash",
            "agent_pid": 2194,
            "agent_type": "architect",
            "error": "ImportError: cannot import...",
            "action_taken": "respawned",
            "bug_reported": True,
            "bug_number": 3
        }
    ],
    "metrics": {
        "active_agents": 2,
        "crashed_agents_last_hour": 4,
        "respawn_success_rate": 0.5,
        "orchestrator_last_poll": 3600  # seconds ago
    }
}
```

---

## Auto-Fix Actions

### Level 1: Respawn (Non-Invasive)
- Agent crashed → respawn same command
- Log error for analysis

### Level 2: Bug Reporting (Proactive)
- 3+ crashes on same task → create bug ticket
- Assign to code_developer with high priority
- Include error logs and stack traces

### Level 3: Orchestrator Restart (Emergency)
- Loop frozen >5 minutes → restart orchestrator
- Create CRITICAL bug ticket
- Notify user

---

## Bug Report Format

When creating bugs via bug-tracking skill:

```python
{
    "title": "Agent crashes with ImportError on skill loading",
    "description": "architect agent crashes immediately after spawn with ImportError...",
    "priority": "High",  # Critical if >10 crashes
    "category": "crash",
    "reproduction_steps": [
        "Start orchestrator",
        "Spawn architect for spec creation",
        "Observe immediate crash"
    ],
    "root_cause": "Missing SkillNames export in skill_loader.py",
    "related_files": ["coffee_maker/autonomous/skill_loader.py"],
    "error_logs": "...",
    "assigned_to": "code_developer"
}
```

---

## Usage in Orchestrator

### Integration Point

Add to `continuous_work_loop.py`:

```python
from orchestrator_health_monitor import OrchestratorHealthMonitor

def _run_work_loop(self):
    monitor = OrchestratorHealthMonitor()

    while self.running:
        # Normal work loop
        self._poll_roadmap()
        self._spawn_agents()

        # Health check every iteration
        status = monitor.check_health()

        if status["status"] != "healthy":
            monitor.auto_fix_issues()
            monitor.report_bugs_if_any()

        time.sleep(self.poll_interval)
```

---

## Monitoring Metrics

Tracked in `data/orchestrator.db`:

### health_checks table
```sql
CREATE TABLE health_checks (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,  -- healthy, degraded, critical
    active_agents INTEGER,
    crashed_agents INTEGER,
    zombie_processes INTEGER,
    orchestrator_responsive BOOLEAN,
    last_poll_age_seconds INTEGER,
    actions_taken TEXT,  -- JSON array
    bugs_reported TEXT   -- JSON array of bug numbers
);
```

### agent_crashes table
```sql
CREATE TABLE agent_crashes (
    crash_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_pid INTEGER NOT NULL,
    agent_type TEXT NOT NULL,
    task_id TEXT,
    crashed_at TEXT NOT NULL,
    error_type TEXT,  -- ImportError, RuntimeError, etc.
    error_message TEXT,
    stack_trace TEXT,
    respawned BOOLEAN,
    bug_reported BOOLEAN,
    bug_number INTEGER
);
```

---

## Example Scenarios

### Scenario 1: ImportError Crash
```
1. Agent spawns (PID 2194, architect)
2. Crashes with ImportError after 2s
3. Monitor detects crash within 30s
4. Parses logs → root cause: "Missing SkillNames"
5. Respawns agent (attempt 1/3)
6. Still crashes
7. After 3rd crash → Creates BUG-003
8. Assigns to code_developer with stack trace
```

### Scenario 2: Orchestrator Freeze
```
1. Last poll: 13:00:46
2. Current time: 14:30:00 (89 minutes later)
3. Monitor detects: last_poll_age > 5 minutes
4. Creates CRITICAL BUG-004: "Orchestrator loop frozen"
5. Attempts graceful restart
6. If restart fails → Alerts user
```

### Scenario 3: Zombie Processes
```
1. Detects 15 completed agents still in agent_state.json
2. Checks PIDs → all dead
3. Cleans up JSON file
4. Reports issue as Low priority bug
```

---

## Configuration

```python
config = {
    "health_check_interval": 30,  # seconds
    "max_respawn_attempts": 3,
    "orchestrator_freeze_threshold": 300,  # 5 minutes
    "crash_threshold_for_bug": 3,  # crashes before creating bug
    "bug_priority_mapping": {
        "ImportError": "High",
        "RuntimeError": "Medium",
        "TimeoutError": "Low"
    }
}
```

---

## Best Practices

1. **Run health checks in background thread** (don't block work loop)
2. **Rate limit bug creation** (max 1 bug per issue type per hour)
3. **Clean up old crashes** (remove from DB after 7 days)
4. **Alert on critical issues** (orchestrator freeze, >10 crashes/hour)

---

## Testing

```bash
# Manual test
pytest tests/unit/test_orchestrator_health_monitor.py

# Simulate agent crash
poetry run orchestrator-health-monitor simulate-crash --agent=architect

# Check health
poetry run orchestrator-health-monitor check

# View crash history
poetry run orchestrator-health-monitor crashes --last=24h
```

---

## References

- **SPEC-111**: Bug Tracking Database and Skill
- **SPEC-110**: Orchestrator Database Tracing
- **CFR-014**: Database Tracing Requirement
- **CFR-009**: Sound Notifications (use sound=False)

---

**Last Updated**: 2025-10-20
**Status**: Ready for Implementation
**Maintainer**: orchestrator
