---
command: orchestrator.handle-agent-errors
agent: orchestrator
action: handle_agent_errors
description: Handle and recover from agent errors
tables:
  read: [agent_lifecycle, orchestrator_task]
  write: [agent_lifecycle, orchestrator_task, agent_message]
required_tools: [database, notification]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.handle-agent-errors

## Purpose

Handle and recover from agent errors through:
1. Detect agent errors from agent_lifecycle
2. Classify error severity
3. Log detailed error information
4. Attempt recovery (retry, alternative strategy)
5. Escalate if necessary
6. Notify affected parties

## Error Types

| Error Type | Severity | Retryable | Recovery |
|-----------|----------|-----------|----------|
| Process died | Medium | Yes | Restart agent |
| Task timeout | Medium | Yes | Increase timeout, restart |
| Git conflict | High | No | Manual intervention |
| Syntax error | High | No | Code review needed |
| Resource exhausted | Medium | Yes | Wait, retry |
| Deadlock detected | High | No | Resolve dependencies |
| Network timeout | Low | Yes | Exponential backoff |

## Parameters

```python
parameters = {
    "ACTION": "detect",          # "detect", "handle", "recover", "escalate"
    "ERROR_THRESHOLD": 3,        # Max errors before escalation
    "RETRY_MAX": 3,
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
}
```

## Error Detection and Classification

### Detect Errors

```sql
SELECT
    al.agent_id,
    al.agent_type,
    al.task_id,
    al.status,
    al.error_message,
    al.completed_at,
    ot.priority,
    ot.estimated_hours
FROM agent_lifecycle al
LEFT JOIN orchestrator_task ot ON al.task_id = ot.task_id
WHERE al.status IN ('failed', 'killed', 'timeout')
AND al.error_message IS NOT NULL
ORDER BY al.completed_at DESC;
```

### Classify Severity

```python
def classify_error_severity(error_message: str, agent_type: str) -> dict:
    """Classify error severity and retryability."""

    # Map error keywords to severity
    severity_keywords = {
        "critical": ["corruption", "data_loss", "authentication_failed"],
        "high": ["syntax_error", "merge_conflict", "spec_not_found"],
        "medium": ["process_died", "resource_exhaustion", "timeout"],
        "low": ["network_timeout", "temporary_error", "rate_limited"]
    }

    retryable_errors = [
        "timeout", "network_", "resource_", "temporary_",
        "database_lock", "rate_limited"
    ]

    # Find matching severity
    for severity, keywords in severity_keywords.items():
        if any(kw in error_message.lower() for kw in keywords):
            return {
                "severity": severity,
                "retryable": any(e in error_message for e in retryable_errors),
                "recommended_action": get_recommended_action(severity)
            }

    return {
        "severity": "medium",
        "retryable": False,
        "recommended_action": "manual_review"
    }
```

## Error Handling Operations

### Operation 1: Detect All Errors

```python
invoke_command("handle-agent-errors", {
    "ACTION": "detect",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "detect",
    "errors_found": 3,
    "errors": [
        {
            "error_id": "err-001",
            "agent_id": "code-developer-20251026-001",
            "task_id": "TASK-31-1",
            "error_message": "Process died unexpectedly",
            "severity": "medium",
            "retryable": true,
            "timestamp": "2025-10-26T10:30:00Z"
        },
        {
            "error_id": "err-002",
            "agent_id": "code-developer-20251026-002",
            "task_id": "TASK-31-2",
            "error_message": "Merge conflict in coffee_maker/models/database.py",
            "severity": "high",
            "retryable": false,
            "timestamp": "2025-10-26T10:32:00Z"
        },
        {
            "error_id": "err-003",
            "agent_id": "architect-20251026-001",
            "task_id": "TASK-32-1",
            "error_message": "Task timeout after 3600 seconds",
            "severity": "medium",
            "retryable": true,
            "timestamp": "2025-10-26T10:34:00Z"
        }
    ]
}
```

### Operation 2: Handle Specific Error

```python
invoke_command("handle-agent-errors", {
    "ACTION": "handle",
    "ERROR_ID": "err-001",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "handle",
    "error_id": "err-001",
    "error_message": "Process died unexpectedly",
    "severity": "medium",
    "recovery_action": "auto_restart",
    "details": {
        "agent_id": "code-developer-20251026-001",
        "task_id": "TASK-31-1",
        "retry_attempt": 1,
        "max_retries": 3,
        "message_sent": true,
        "timestamp": "2025-10-26T10:35:00Z"
    }
}
```

### Operation 3: Recover from Error

```python
invoke_command("handle-agent-errors", {
    "ACTION": "recover",
    "TASK_ID": "TASK-31-1",
    "RECOVERY_STRATEGY": "restart"
})
```

**Output**:
```json
{
    "success": true,
    "action": "recover",
    "task_id": "TASK-31-1",
    "recovery_strategy": "restart",
    "new_agent_id": "code-developer-20251026-003",
    "recovery_timestamp": "2025-10-26T10:35:00Z",
    "message": "Agent restarted to recover from error"
}
```

### Operation 4: Escalate Error

```python
invoke_command("handle-agent-errors", {
    "ACTION": "escalate",
    "ERROR_ID": "err-002",
    "ESCALATION_LEVEL": "architect"
})
```

**Output**:
```json
{
    "success": true,
    "action": "escalate",
    "error_id": "err-002",
    "escalation_level": "architect",
    "escalation_message": "Merge conflict in TASK-31-2 requires manual resolution",
    "details": {
        "agent_id": "code-developer-20251026-002",
        "task_id": "TASK-31-2",
        "severity": "high",
        "files_affected": ["coffee_maker/models/database.py"],
        "message_sent": true,
        "timestamp": "2025-10-26T10:35:00Z"
    }
}
```

## Recovery Strategies

### Strategy 1: Automatic Retry

For low-severity, retryable errors:

```python
# Restart agent with same task
# Increase timeout if timeout error
# Clear cache if corruption detected
```

### Strategy 2: Manual Intervention

For high-severity, non-retryable errors:

```python
# Escalate to architect/project_manager
# Create notification with error details
# Require manual approval to proceed
```

### Strategy 3: Fallback Path

For critical errors:

```python
# Mark task as failed
# Notify project manager
# Update ROADMAP status
# Suggest alternative approach
```

## Error Logging

### Database Schema

```sql
CREATE TABLE error_events (
    error_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    task_id TEXT,
    error_message TEXT,
    severity TEXT,
    stack_trace TEXT,
    recovery_action TEXT,
    recovered BOOLEAN,
    created_at TIMESTAMP,
    resolved_at TIMESTAMP
);
```

## Notification Types

| Severity | Recipients | Action |
|----------|-----------|--------|
| Critical | project_manager, architect | Immediate notification |
| High | architect, code_developer | Notification + log |
| Medium | code_developer | Log + auto-recovery attempt |
| Low | orchestrator logs only | Logged only |

## Success Criteria

1. All errors correctly detected
2. Severity accurately classified
3. Recovery actions appropriate
4. Escalations routed correctly
5. Notifications sent to right parties
6. Error history tracked

## Error Handling Example

```
Error: Process died unexpectedly (code_developer-20251026-001)
  ↓
Severity: Medium
Retryable: Yes
  ↓
Action: Auto-restart agent
  ↓
Result: Agent restarted successfully
  ↓
Outcome: Task resumed (retry 1 of 3)
```

## Related Commands

- auto-restart-agent.md (implements restart recovery)
- monitor-agent-lifecycle.md (detects failures)
- route-inter-agent-messages.md (sends escalation messages)
