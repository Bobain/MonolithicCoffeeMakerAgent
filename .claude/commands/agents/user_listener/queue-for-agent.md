---
command: queue-for-agent
agent: user_listener
action: queue_request_for_busy_agent
tables: [ui_routing_log, agent_message]
tools: []
duration: 5m
---

## Purpose

Enqueue work when target agent is busy, with priority assignment and wait time estimation.

## Input Parameters

```yaml
TARGET_AGENT:
  type: string
  description: Agent name (currently busy)
  example: "code_developer"

REQUEST_DATA:
  type: object
  description: Complete request data

SESSION_ID:
  type: string
  description: Conversation session

PRIORITY:
  type: string
  optional: true
  enum: [low, normal, high, critical]
  default: normal
  description: Queue priority
```

## Database Operations

### INSERT agent_message

```sql
INSERT INTO agent_message (
    from_agent, to_agent, message_type, content, status, priority, created_at
) VALUES (?, ?, 'request', ?, 'queued', ?, datetime('now'))
```

### INSERT ui_routing_log

```sql
INSERT INTO ui_routing_log (
    session_id, source_agent, target_agent, request_type, routed_at, status
) VALUES (?, 'user_listener', ?, ?, datetime('now'), 'queued')
```

## Success Criteria

- Request queued in agent_message table
- Priority assigned
- Estimated wait time calculated
- User notified with position and ETA

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "target_agent": "code_developer",
  "queue_position": 3,
  "queue_size": 5,
  "estimated_wait_minutes": 12,
  "priority": "normal",
  "message": "Request queued for code_developer, position 3/5"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid priority | PRIORITY not in enum | Use 'normal' |
| Queue insert failed | Database error | Retry up to 3 times |

## Examples

### Example 1: Queue High Priority Request

```bash
/agents:user_listener:queue-for-agent \
  TARGET_AGENT="code_developer" \
  SESSION_ID="SESS-20251027-abc123" \
  PRIORITY="high" \
  REQUEST_DATA='{...}'
```

### Example 2: Queue Normal Request

```bash
/agents:user_listener:queue-for-agent \
  TARGET_AGENT="architect" \
  SESSION_ID="SESS-20251027-def456" \
  PRIORITY="normal" \
  REQUEST_DATA='{...}'
```

## Implementation Notes

- Queue priority: critical > high > normal > low
- Estimate wait time based on queue size and agent processing time
- Store in agent_message with status='queued'
- Update routing_log with queued status
- User receives queue position and ETA
- Agent processes queued messages in priority order
