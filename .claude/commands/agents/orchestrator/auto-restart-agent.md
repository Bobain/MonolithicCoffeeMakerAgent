---
command: orchestrator.auto-restart-agent
agent: orchestrator
action: auto_restart_agent
description: Restart failed agents with exponential backoff
tables:
  read: [agent_lifecycle, orchestrator_task]
  write: [agent_lifecycle]
required_tools: [subprocess, database]
cfr_compliance:
  - CFR-000: Singleton agent enforcement
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.auto-restart-agent

## Purpose

Automatically restart failed agents with intelligent backoff strategy:
1. Detect agent failure (process died, task failed)
2. Analyze failure reason
3. Calculate backoff delay (exponential: 2^n seconds)
4. Spawn new agent instance
5. Track retry attempts
6. Give up after max retries

## Parameters

```python
parameters = {
    "AGENT_ID": "code-developer-20251026-001",
    "MAX_RETRIES": 3,
    "INITIAL_BACKOFF_SECONDS": 2,
    "MAX_BACKOFF_SECONDS": 120,
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
}
```

## Failure Detection

### Check Agent Status

```sql
SELECT
    agent_id,
    agent_type,
    status,
    task_id,
    pid,
    error_message,
    retry_count,
    CURRENT_TIMESTAMP - completed_at as seconds_since_failure
FROM agent_lifecycle
WHERE status IN ('killed', 'failed', 'timeout')
AND retry_count < ?
ORDER BY completed_at DESC;
```

### Analyze Failure Reason

```python
def analyze_failure(error_message: str, agent_type: str) -> dict:
    """Determine if failure is retryable."""
    retryable_errors = [
        "network_timeout",
        "database_lock",
        "resource_exhaustion",
        "temporary_error"
    ]

    permanent_errors = [
        "git_conflict",
        "syntax_error",
        "spec_not_found",
        "invalid_configuration"
    ]

    return {
        "retryable": any(e in error_message for e in retryable_errors),
        "reason": error_message,
        "agent_type": agent_type
    }
```

## Restart Operations

### Operation 1: Restart Specific Agent

```python
invoke_command("auto-restart-agent", {
    "AGENT_ID": "code-developer-20251026-001",
    "MAX_RETRIES": 3,
    "INITIAL_BACKOFF_SECONDS": 2
})
```

**Output**:
```json
{
    "success": true,
    "agent_id": "code-developer-20251026-001",
    "action": "restart",
    "old_agent_id": "code-developer-20251026-001",
    "new_agent_id": "code-developer-20251026-002",
    "task_id": "TASK-31-1",
    "retry_count": 1,
    "backoff_seconds": 2,
    "restarting_in_seconds": 2,
    "max_retries": 3,
    "message": "Agent scheduled for restart"
}
```

### Operation 2: Auto-restart All Failed Agents

```python
invoke_command("auto-restart-agent", {
    "ACTION": "restart_all_failed",
    "MAX_RETRIES": 3,
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "restart_all_failed",
    "agents_scheduled": 2,
    "agents": [
        {
            "agent_id": "code-developer-20251026-001",
            "task_id": "TASK-31-1",
            "retry_count": 1,
            "backoff_seconds": 2,
            "reason": "process_died"
        },
        {
            "agent_id": "architect-20251026-001",
            "task_id": "TASK-32-1",
            "retry_count": 1,
            "backoff_seconds": 2,
            "reason": "task_timeout"
        }
    ],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 3: Check Restart Status

```python
invoke_command("auto-restart-agent", {
    "ACTION": "check_status",
    "AGENT_ID": "code-developer-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "agent_id": "code-developer-20251026-001",
    "task_id": "TASK-31-1",
    "retry_count": 1,
    "max_retries": 3,
    "last_failure": "2025-10-26T10:34:00Z",
    "can_retry": true,
    "reason": "process_died",
    "message": "Agent can be restarted"
}
```

## Backoff Strategy

```
Retry 1: 2^1 = 2 seconds
Retry 2: 2^2 = 4 seconds
Retry 3: 2^3 = 8 seconds
Retry 4: min(2^4, 120) = 16 seconds
...
Retry n: min(2^n, 120) seconds (capped at 120s)
```

## Database Updates

### Update agent_lifecycle

```sql
UPDATE agent_lifecycle
SET retry_count = retry_count + 1,
    status = 'pending_restart',
    error_message = error_message || ' (Retry ' || retry_count + 1 || ')'
WHERE agent_id = ?;

INSERT INTO agent_lifecycle (
    agent_id,
    agent_type,
    status,
    task_id,
    created_at,
    retry_count,
    error_message
) VALUES (?, ?, 'spawned', ?, CURRENT_TIMESTAMP, ?, ?);
```

## Failure Classification

| Error Type | Retryable | Max Retries | Strategy |
|-----------|-----------|-------------|----------|
| Network timeout | Yes | 3 | Exponential backoff |
| Database lock | Yes | 3 | Exponential backoff |
| Resource exhaustion | Yes | 2 | Longer backoff |
| Syntax error | No | 0 | Fail immediately |
| Git conflict | No | 0 | Manual intervention |
| Task timeout | Yes | 2 | Increase timeout |

## Success Criteria

1. Failure correctly detected
2. Retryability determined correctly
3. Backoff delay calculated properly
4. New agent spawned successfully
5. Retry count incremented
6. Old agent_lifecycle preserved for debugging
7. Max retries enforced

## Error Handling

```json
{
    "success": false,
    "error": "max_retries_exceeded",
    "message": "Agent has been restarted 3 times, giving up",
    "agent_id": "code-developer-20251026-001",
    "retry_count": 3,
    "max_retries": 3
}
```

## Possible Errors

- `max_retries_exceeded`: Too many restart attempts
- `non_retryable_error`: Permanent failure, cannot restart
- `agent_not_found`: Agent doesn't exist in database
- `spawn_failed`: Cannot spawn new agent (resource exhaustion)

## Related Commands

- kill-stalled-agent.md (detects failures to restart)
- spawn-agent-session.md (launches new agent instances)
- monitor-agent-lifecycle.md (tracks failures)
