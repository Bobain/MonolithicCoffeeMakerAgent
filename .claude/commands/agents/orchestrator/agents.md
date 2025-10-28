# agents

## Purpose
Monitor agent lifecycle: track health, detect stalls, auto-restart failed agents, enforce singleton policy (CFR-000), generate activity reports.

## Parameters
```yaml
action: str  # Required: "list" | "health" | "restart" | "kill"
agent_id: str = None  # Required for restart/kill actions
agent_type: str = None  # Filter by type for list/health
auto_restart: bool = true  # Enable auto-restart on failure
```

## Workflow
1. Query agent_lifecycle table for current agents
2. Execute action:
   - **list**: Return all active agents
   - **health**: Check heartbeats, CPU/memory usage
   - **restart**: Terminate and relaunch agent
   - **kill**: Force terminate agent
3. Enforce CFR-000 singleton policy
4. Update agent_lifecycle records
5. Return AgentsResult

## Database Operations
```sql
-- Get active agents
SELECT agent_id, agent_type, status, pid, created_at,
       last_heartbeat, cpu_percent, memory_mb
FROM agent_lifecycle
WHERE status IN ('running', 'idle')
ORDER BY created_at DESC

-- Update heartbeat
UPDATE agent_lifecycle
SET last_heartbeat = datetime('now'),
    cpu_percent = ?, memory_mb = ?
WHERE agent_id = ?

-- Mark agent as failed
UPDATE agent_lifecycle
SET status = 'failed', exit_code = ?, terminated_at = datetime('now')
WHERE agent_id = ?

-- Restart tracking
INSERT INTO agent_restart_log (
    restart_id, agent_id, reason, attempt_number, timestamp
) VALUES (?, ?, ?, ?, datetime('now'))
```

## Result Object
```python
@dataclass
class AgentsResult:
    action: str
    agents: List[dict]  # [{agent_id, type, status, pid, uptime}]
    health_status: str  # "healthy" | "degraded" | "critical"
    agents_restarted: int
    agents_killed: int
    status: str  # "success" | "failed"
```

## Health Check Criteria
- **Heartbeat**: < 2 minutes = healthy, 2-5 min = warning, >5 min = stalled
- **CPU**: < 80% = healthy, 80-95% = warning, >95% = critical
- **Memory**: < 1GB = healthy, 1-2GB = warning, >2GB = critical
- **Singleton**: Only 1 instance per agent_type

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| AgentNotFound | Invalid agent_id | Check active agents |
| SingletonViolation | Multiple instances | Kill duplicates, keep oldest |
| RestartFailed | Agent won't start | Log error, notify admin |
| KillTimeout | Process won't die | Force kill with SIGKILL |

## Example
```python
result = agents(action="health", agent_type="code_developer")
# AgentsResult(
#   action="health",
#   agents=[{"agent_id": "cd-123", "type": "code_developer", "status": "running"}],
#   health_status="healthy",
#   agents_restarted=0,
#   agents_killed=0,
#   status="success"
# )
```

## Related Commands
- assign() - Assigns tasks to healthy agents
- route() - Routes messages to active agents

---
Estimated: 70 lines | Context: ~4.5% | Examples: agents_examples.md
