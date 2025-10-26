---
command: orchestrator.route-inter-agent-messages
agent: orchestrator
action: route_inter_agent_messages
description: Route agent_message table entries between agents
tables:
  read: [agent_message]
  write: [agent_message]
required_tools: [database, message_queue]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.route-inter-agent-messages

## Purpose

Route messages between agents via database:
1. Poll agent_message table for new messages
2. Filter by recipient agent type
3. Deliver messages to agents
4. Track delivery status
5. Handle delivery failures
6. Clean up old messages

## Message Types

| Type | From | To | Purpose |
|------|------|-----|---------|
| task_assignment | orchestrator | code_developer | Assign task to implement |
| task_complete | code_developer | orchestrator | Report task completion |
| spec_ready | architect | code_developer | Spec ready for implementation |
| error_report | code_developer | orchestrator | Report task failure |
| dependency_unblocked | orchestrator | code_developer | Task dependencies met |

## Parameters

```python
parameters = {
    "ACTION": "poll",             # "poll", "deliver", "clear"
    "RECIPIENT": "code_developer", # "code_developer", "architect", "project_manager"
    "BATCH_SIZE": 10,
    "DELIVERY_TIMEOUT_SECONDS": 300,
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
}
```

## Message Schema

```sql
CREATE TABLE agent_message (
    message_id TEXT PRIMARY KEY,
    sender TEXT NOT NULL,           -- "orchestrator", "code_developer", etc.
    recipient TEXT NOT NULL,        -- Target agent type
    message_type TEXT,              -- "task_assignment", "error_report", etc.
    payload JSON,                   -- Message content
    status TEXT,                    -- "pending", "delivered", "failed"
    created_at TIMESTAMP,
    delivered_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT
);
```

## Message Delivery Process

### Step 1: Poll Messages

```sql
SELECT
    message_id,
    sender,
    recipient,
    message_type,
    payload,
    retry_count
FROM agent_message
WHERE recipient = ?
AND status IN ('pending', 'retry')
ORDER BY created_at ASC
LIMIT ?;
```

### Step 2: Deliver Message

For each message, deliver to target agent:

```python
def deliver_message(agent_type: str, message: dict) -> bool:
    """Deliver message to agent (via database or IPC)."""
    try:
        # Method 1: Database notification
        # Agent polls agent_message table periodically
        agent_inbox = f"{agent_type}_inbox"
        db.execute(
            f"INSERT INTO {agent_inbox} (message_id, payload) VALUES (?, ?)",
            (message['message_id'], message['payload'])
        )

        # Method 2: File-based notification (fallback)
        inbox_file = f"/tmp/{agent_type}.inbox"
        with open(inbox_file, 'a') as f:
            f.write(json.dumps(message) + '\n')

        return True
    except Exception as e:
        logger.error(f"Failed to deliver message: {e}")
        return False
```

### Step 3: Update Status

```sql
UPDATE agent_message
SET status = 'delivered',
    delivered_at = CURRENT_TIMESTAMP
WHERE message_id = ?;
```

## Message Operations

### Operation 1: Poll Messages for Agent

```python
invoke_command("route-inter-agent-messages", {
    "ACTION": "poll",
    "RECIPIENT": "code_developer",
    "BATCH_SIZE": 10
})
```

**Output**:
```json
{
    "success": true,
    "action": "poll",
    "recipient": "code_developer",
    "messages_pending": 2,
    "messages": [
        {
            "message_id": "msg-001",
            "sender": "orchestrator",
            "message_type": "task_assignment",
            "payload": {
                "task_id": "TASK-31-1",
                "spec_id": "SPEC-031",
                "priority": "high"
            },
            "created_at": "2025-10-26T10:30:00Z"
        },
        {
            "message_id": "msg-002",
            "sender": "orchestrator",
            "message_type": "dependency_unblocked",
            "payload": {
                "task_id": "TASK-31-2",
                "unblocked_by": "TASK-31-1"
            },
            "created_at": "2025-10-26T10:32:00Z"
        }
    ],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 2: Deliver All Pending Messages

```python
invoke_command("route-inter-agent-messages", {
    "ACTION": "deliver_all",
    "DELIVERY_TIMEOUT_SECONDS": 300
})
```

**Output**:
```json
{
    "success": true,
    "action": "deliver_all",
    "messages_delivered": 5,
    "messages_failed": 1,
    "delivery_summary": [
        {
            "recipient": "code_developer",
            "delivered": 3,
            "failed": 0
        },
        {
            "recipient": "architect",
            "delivered": 2,
            "failed": 0
        },
        {
            "recipient": "project_manager",
            "delivered": 0,
            "failed": 1
        }
    ],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 3: Send Message

```python
invoke_command("route-inter-agent-messages", {
    "ACTION": "send",
    "SENDER": "orchestrator",
    "RECIPIENT": "code_developer",
    "MESSAGE_TYPE": "task_assignment",
    "PAYLOAD": {
        "task_id": "TASK-31-1",
        "spec_id": "SPEC-031",
        "priority": "high"
    }
})
```

**Output**:
```json
{
    "success": true,
    "action": "send",
    "message_id": "msg-003",
    "sender": "orchestrator",
    "recipient": "code_developer",
    "message_type": "task_assignment",
    "status": "pending",
    "created_at": "2025-10-26T10:35:00Z"
}
```

### Operation 4: Clear Old Messages

```python
invoke_command("route-inter-agent-messages", {
    "ACTION": "clear_old",
    "OLDER_THAN_DAYS": 7
})
```

**Output**:
```json
{
    "success": true,
    "action": "clear_old",
    "messages_deleted": 12,
    "disk_space_freed_mb": 0.5,
    "deleted_statuses": {
        "delivered": 10,
        "failed": 2
    }
}
```

## Retry Strategy

```
Attempt 1: Immediate
Attempt 2: After 30 seconds
Attempt 3: After 60 seconds
Attempt 4: After 120 seconds
Give up: After 4 attempts
```

## Success Criteria

1. All pending messages identified
2. Messages delivered to correct agents
3. Status updates atomic and logged
4. No duplicate messages delivered
5. Failures tracked for analysis
6. Old messages cleaned up

## Error Handling

```json
{
    "success": false,
    "error": "delivery_timeout",
    "message": "Failed to deliver message after 3 attempts",
    "message_id": "msg-001",
    "recipient": "code_developer",
    "retry_count": 3
}
```

## Message Persistence

| Status | Lifetime | Action |
|--------|----------|--------|
| pending | 5 minutes | Retry |
| delivered | 7 days | Archive |
| failed | 7 days | Log then delete |
| expired | >7 days | Delete |

## Related Commands

- spawn-agent-session.md (agents check for messages)
- handle-agent-errors.md (sends error messages)
