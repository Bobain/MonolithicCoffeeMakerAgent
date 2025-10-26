---
command: orchestrator.kill-stalled-agent
agent: orchestrator
action: kill_stalled_agent
description: Terminate unresponsive agents and clean up resources
tables:
  read: [agent_lifecycle]
  write: [agent_lifecycle]
required_tools: [subprocess, psutil, database]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.kill-stalled-agent

## Purpose

Terminate unresponsive agents by:
1. Detecting stalled agents (no heartbeat >120s)
2. Sending graceful SIGTERM signal
3. Waiting for graceful shutdown (10 seconds)
4. Force killing with SIGKILL if needed
5. Cleaning up resources and updating database
6. Recording kill event for debugging

## Parameters

```python
parameters = {
    "AGENT_ID": "code-developer-20251026-001",
    "GRACE_PERIOD_SECONDS": 10,
    "FORCE_KILL": False,  # True to skip graceful shutdown
    "CLEANUP": True       # Clean up worktrees and resources
}
```

## Kill Process

### Step 1: Validate Agent

```sql
SELECT agent_id, pid, status, task_id
FROM agent_lifecycle
WHERE agent_id = ?;
```

### Step 2: Send SIGTERM (Graceful)

```python
import subprocess
import signal

def kill_agent_gracefully(pid: int, grace_period: int) -> bool:
    try:
        os.kill(pid, signal.SIGTERM)
        # Wait for graceful shutdown
        start_time = time.time()
        while time.time() - start_time < grace_period:
            try:
                process = psutil.Process(pid)
                if not process.is_running():
                    return True  # Graceful shutdown succeeded
            except psutil.NoSuchProcess:
                return True
            time.sleep(1)
        return False  # Timeout, need force kill
    except ProcessLookupError:
        return True  # Already dead
```

### Step 3: Force Kill (SIGKILL)

```python
import signal

def force_kill_agent(pid: int) -> bool:
    try:
        os.kill(pid, signal.SIGKILL)
        time.sleep(1)
        # Verify process is dead
        try:
            process = psutil.Process(pid)
            return not process.is_running()
        except psutil.NoSuchProcess:
            return True
    except ProcessLookupError:
        return True  # Already dead
```

## Kill Operations

### Operation 1: Kill Specific Agent

```python
invoke_command("kill-stalled-agent", {
    "AGENT_ID": "code-developer-20251026-001",
    "GRACE_PERIOD_SECONDS": 10,
    "FORCE_KILL": False,
    "CLEANUP": True
})
```

**Output**:
```json
{
    "success": true,
    "agent_id": "code-developer-20251026-001",
    "action": "graceful_kill",
    "pid": 12345,
    "kill_signal": "SIGTERM",
    "task_id": "TASK-31-1",
    "killed_at": "2025-10-26T10:35:00Z",
    "grace_period_seconds": 10,
    "killed_gracefully": true,
    "message": "Agent terminated gracefully"
}
```

### Operation 2: Force Kill Agent

```python
invoke_command("kill-stalled-agent", {
    "AGENT_ID": "architect-20251026-001",
    "FORCE_KILL": True,
    "GRACE_PERIOD_SECONDS": 0,
    "CLEANUP": True
})
```

**Output**:
```json
{
    "success": true,
    "agent_id": "architect-20251026-001",
    "action": "force_kill",
    "pid": 12346,
    "kill_signal": "SIGKILL",
    "task_id": "TASK-32-1",
    "killed_at": "2025-10-26T10:35:02Z",
    "killed_gracefully": false,
    "message": "Agent force killed"
}
```

### Operation 3: Kill All Stalled Agents

```python
invoke_command("kill-stalled-agent", {
    "ACTION": "kill_stalled",
    "HEARTBEAT_TIMEOUT_SECONDS": 120,
    "CLEANUP": True
})
```

**Output**:
```json
{
    "success": true,
    "action": "kill_stalled",
    "agents_killed": 1,
    "killed_agents": [
        {
            "agent_id": "architect-20251026-001",
            "pid": 12346,
            "seconds_since_heartbeat": 250,
            "killed_gracefully": false,
            "task_id": "TASK-32-1"
        }
    ],
    "timestamp": "2025-10-26T10:35:02Z"
}
```

## Database Updates

### Update agent_lifecycle

```sql
UPDATE agent_lifecycle
SET status = 'killed',
    completed_at = CURRENT_TIMESTAMP,
    error_message = ?
WHERE agent_id = ?;
```

### Update orchestrator_task

```sql
UPDATE orchestrator_task
SET status = 'failed',
    error_message = 'Agent killed: ' || ?
WHERE task_id = (
    SELECT task_id FROM agent_lifecycle
    WHERE agent_id = ?
);
```

## Resource Cleanup

After killing an agent:

1. **Close file handles** - Ensure no open files remain
2. **Clean temporary directories** - Remove temp session dirs
3. **Release database connections** - Close SQLite connections
4. **Cleanup worktrees** - If task has associated worktree
5. **Update task status** - Mark task as failed or ready for retry

## Graceful vs Force Kill

| Aspect | Graceful | Force |
|--------|----------|-------|
| Signal | SIGTERM | SIGKILL |
| Grace period | 10s | 0s |
| Resource cleanup | Agent handles | OS cleans up |
| Data integrity | Better | Risky |
| Use case | Normal shutdown | Unresponsive |

## Success Criteria

1. Target agent process terminated
2. agent_lifecycle record updated
3. orchestrator_task status updated appropriately
4. Resources cleaned up
5. All related records logged
6. No orphaned processes remain

## Error Handling

```json
{
    "success": false,
    "error": "agent_not_found",
    "message": "Agent ID not found in database",
    "agent_id": "code-developer-20251026-001"
}
```

## Possible Errors

- `agent_not_found`: Agent doesn't exist in agent_lifecycle
- `process_not_found`: PID doesn't correspond to running process
- `kill_failed`: Failed to send signal to process
- `cleanup_failed`: Failed to clean up resources

## Related Commands

- monitor-agent-lifecycle.md (detects stalled agents)
- auto-restart-agent.md (restarts killed agents)
- spawn-agent-session.md (launches agents)
