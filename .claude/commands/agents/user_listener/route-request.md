---
command: route-request
agent: user_listener
action: route_classified_request
tables: [ui_routing_log, agent_message]
tools: [notification_system]
duration: 10m
---

## Purpose

Forward classified request to target agent via agent_message table and notify target.

## Input Parameters

```yaml
TARGET_AGENT:
  type: string
  description: Agent to receive request
  example: "architect"

REQUEST_DATA:
  type: object
  description: Structured request containing classified_intent, extracted_entities
  properties:
    user_input: string
    classified_intent: string
    extracted_entities: object
    session_id: string

SESSION_ID:
  type: string
  description: Conversation session identifier
```

## Database Operations

### INSERT agent_message

```sql
INSERT INTO agent_message (
    from_agent, to_agent, message_type, content, status, created_at
) VALUES (?, ?, 'request', ?, 'pending', datetime('now'))
```

### INSERT ui_routing_log

```sql
INSERT INTO ui_routing_log (
    session_id, source_agent, target_agent, request_type, routed_at, status
) VALUES (?, 'user_listener', ?, ?, datetime('now'), 'in_progress')
```

## External Tools

### Notification System

Send notification to target agent about incoming request.

## Success Criteria

- Message created in agent_message table
- Target agent notified
- Routing logged
- Session linked to message

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "target_agent": "architect",
  "message_id": 42,
  "status": "pending",
  "notification_sent": true,
  "message": "Request routed to architect and notification sent"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid agent | TARGET_AGENT unknown | List valid agents |
| Message insert failed | Database error | Retry with exponential backoff |
| Notification failed | System error | Log error, message still created |

## Examples

### Example 1: Route to Architect

```bash
/agents:user_listener:route-request \
  TARGET_AGENT="architect" \
  SESSION_ID="SESS-20251027-abc123" \
  REQUEST_DATA='{
    "user_input": "Create a spec for user authentication",
    "classified_intent": "command",
    "extracted_entities": {"target_type": "spec", "action": "create"}
  }'
```

### Example 2: Route to Code Developer

```bash
/agents:user_listener:route-request \
  TARGET_AGENT="code_developer" \
  SESSION_ID="SESS-20251027-def456" \
  REQUEST_DATA='{
    "user_input": "Implement user authentication module",
    "classified_intent": "command",
    "extracted_entities": {"target_type": "code", "action": "implement"}
  }'
```

## Implementation Notes

- Use agent_message table for inter-agent communication
- Store complete REQUEST_DATA as JSON in message
- Mark message status as 'pending' initially
- Create routing log entry for audit trail
- Notify target agent via notification_system
- Link back to conversation session for context
