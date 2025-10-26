---
command: orchestrator.monitor-agent-lifecycle
agent: orchestrator
action: monitor_agent_lifecycle
description: Track agent health and status in agent_lifecycle table
tables:
  read: [agent_lifecycle, orchestrator_task]
  write: [agent_lifecycle]
required_tools: [psutil, database, subprocess]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.monitor-agent-lifecycle

## Purpose

Continuously monitor agent health by:
1. Checking process status (alive/dead)
2. Monitoring resource usage (CPU, memory)
3. Detecting heartbeat timeouts (stalled agents)
4. Recording agent events in agent_lifecycle
5. Detecting early failures

## Parameters

```python
parameters = {
    "CHECK_INTERVAL_SECONDS": 30,
    "HEARTBEAT_TIMEOUT_SECONDS": 120,
    "CPU_THRESHOLD_PERCENT": 0.1,    # Minimum CPU usage (0.1%)
    "MEMORY_THRESHOLD_MB": 50,       # Minimum memory usage
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
}
```

## Health Monitoring

### Process Status Check

```python
import psutil

def check_agent_health(pid: int, agent_id: str) -> dict:
    try:
        process = psutil.Process(pid)
        status = {
            "process_alive": process.is_running(),
            "cpu_percent": process.cpu_percent(interval=1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "num_threads": process.num_threads(),
            "status": process.status()
        }
        return status
    except psutil.NoSuchProcess:
        return {"process_alive": False, "error": "process_not_found"}
```

### Heartbeat Monitoring

Track last heartbeat from agent:

```sql
SELECT
    agent_id,
    status,
    last_heartbeat,
    CURRENT_TIMESTAMP - last_heartbeat as seconds_since_heartbeat
FROM agent_lifecycle
WHERE agent_type IN ('code_developer', 'architect', 'project_manager')
ORDER BY seconds_since_heartbeat DESC;
```

## Monitoring Operations

### Operation 1: Check All Agents

```python
invoke_command("monitor-agent-lifecycle", {
    "ACTION": "check_all",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "agents_checked": 3,
    "agents_healthy": 2,
    "agents_stalled": 1,
    "agents_dead": 0,
    "agents": [
        {
            "agent_id": "code-developer-20251026-001",
            "agent_type": "code_developer",
            "task_id": "TASK-31-1",
            "status": "running",
            "pid": 12345,
            "process_alive": true,
            "cpu_percent": 45.2,
            "memory_mb": 285.5,
            "seconds_since_heartbeat": 5,
            "health_status": "healthy"
        },
        {
            "agent_id": "architect-20251026-001",
            "agent_type": "architect",
            "status": "running",
            "pid": 12346,
            "process_alive": true,
            "cpu_percent": 0.0,
            "memory_mb": 120.3,
            "seconds_since_heartbeat": 95,
            "health_status": "stalled"
        },
        {
            "agent_id": "project-manager-20251026-001",
            "agent_type": "project_manager",
            "status": "completed",
            "pid": null,
            "health_status": "completed"
        }
    ],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 2: Check Specific Agent

```python
invoke_command("monitor-agent-lifecycle", {
    "ACTION": "check_agent",
    "AGENT_ID": "code-developer-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "agent_id": "code-developer-20251026-001",
    "status": "running",
    "health_status": "healthy",
    "pid": 12345,
    "process_alive": true,
    "cpu_percent": 45.2,
    "memory_mb": 285.5,
    "seconds_since_heartbeat": 5,
    "task_id": "TASK-31-1",
    "uptime_seconds": 125,
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 3: Update Heartbeat

Agent calls this periodically to signal liveliness:

```python
invoke_command("monitor-agent-lifecycle", {
    "ACTION": "heartbeat",
    "AGENT_ID": "code-developer-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "agent_id": "code-developer-20251026-001",
    "last_heartbeat": "2025-10-26T10:35:00Z",
    "next_heartbeat_due": "2025-10-26T10:36:00Z"
}
```

## Health Status Classification

| Status | Meaning | Action |
|--------|---------|--------|
| healthy | Process running, CPU/memory OK, recent heartbeat | Continue monitoring |
| stalled | Process running but no heartbeat for >120s | Mark stalled, may kill/restart |
| dead | Process not running | Update status, clean up |
| completed | Task finished successfully | Archive records |
| failed | Task failed with error | Log error, investigate |

## Database Updates

### Update agent_lifecycle on Status Change

```sql
UPDATE agent_lifecycle
SET status = ?,
    last_heartbeat = CURRENT_TIMESTAMP,
    error_message = ?
WHERE agent_id = ?;
```

### Record Health Events

Create health check records for audit trail:

```sql
INSERT INTO agent_lifecycle_events (
    agent_id,
    event_type,
    health_status,
    cpu_percent,
    memory_mb,
    recorded_at
) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
```

## Success Criteria

1. All agent processes checked within CHECK_INTERVAL
2. Heartbeat timeout correctly detected
3. Resource usage accurately measured
4. Status updates atomic and logged
5. No missed stalled agents
6. Monitoring completes within 5 seconds

## Error Handling

```json
{
    "success": false,
    "error": "monitoring_error",
    "message": "Failed to check process health",
    "agent_id": "code-developer-20251026-001",
    "pid": 12345
}
```

## Related Commands

- spawn-agent-session.md (creates agents to monitor)
- kill-stalled-agent.md (terminates detected stalled agents)
- auto-restart-agent.md (restarts dead agents)
