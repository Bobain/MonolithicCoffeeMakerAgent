# route

## Purpose
Route messages between agents: read agent_message table, deliver to target agents, track delivery status, handle routing failures.

## Parameters
```yaml
action: str  # Required: "poll" | "send" | "acknowledge"
message_id: str = None  # Required for send/acknowledge
target_agent: str = None  # Required for send
message_content: dict = None  # Required for send
poll_interval: int = 5  # Seconds between polls
```

## Workflow
1. Execute action:
   - **poll**: Check agent_message for pending messages
   - **send**: Create new message in agent_message table
   - **acknowledge**: Mark message as delivered
2. Update delivery status
3. Handle routing failures (retry with backoff)
4. Return RouteResult

## Database Operations
```sql
-- Poll for pending messages
SELECT message_id, from_agent, to_agent, message_type,
       content, priority, created_at, retry_count
FROM agent_message
WHERE to_agent = ? AND status = 'pending'
ORDER BY priority DESC, created_at ASC
LIMIT 10

-- Send message
INSERT INTO agent_message (
    message_id, from_agent, to_agent, message_type,
    content, priority, status, created_at
) VALUES (?, ?, ?, ?, ?, ?, 'pending', datetime('now'))

-- Acknowledge delivery
UPDATE agent_message
SET status = 'delivered', delivered_at = datetime('now')
WHERE message_id = ?

-- Mark as failed
UPDATE agent_message
SET status = 'failed', retry_count = retry_count + 1,
    last_retry_at = datetime('now')
WHERE message_id = ? AND retry_count < 3
```

## Result Object
```python
@dataclass
class RouteResult:
    action: str
    messages_processed: int
    messages: List[dict]  # For poll action
    delivery_status: str  # "delivered" | "pending" | "failed"
    status: str  # "success" | "failed"
```

## Message Types
- **task_assignment**: New task assigned
- **status_update**: Task progress update
- **dependency_ready**: Blocking dependency completed
- **error_notification**: Task execution error
- **quality_report**: Code review results
- **spec_ready**: New spec available

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| AgentOffline | Target agent not running | Queue message, retry later |
| MessageExpired | Created > 24h ago | Mark as failed, notify sender |
| DatabaseError | Query failed | Retry with exponential backoff |
| InvalidMessage | Malformed content | Log error, mark as failed |

## Example
```python
result = route(action="send", target_agent="code_developer", message_content={
    "message_type": "task_assignment",
    "task_id": "TASK-8-1",
    "priority": "high"
})
# RouteResult(
#   action="send",
#   messages_processed=1,
#   messages=[],
#   delivery_status="pending",
#   status="success"
# )
```

## Related Commands
- agents() - Check agent availability
- assign() - Creates assignment messages

---
Estimated: 55 lines | Context: ~3.5% | Examples: route_examples.md
