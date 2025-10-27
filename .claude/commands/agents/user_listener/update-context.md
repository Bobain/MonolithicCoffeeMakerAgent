---
command: update-context
agent: user_listener
action: add_context_to_conversation
tables: [ui_conversation_context]
tools: []
duration: 5m
---

## Purpose

Add relevant context to ongoing conversation for improved agent responses.

## Input Parameters

```yaml
SESSION_ID:
  type: string
  description: Conversation session identifier

CONTEXT_TYPE:
  type: string
  enum: [file, spec, roadmap, priority, previous_response]
  description: Type of context to add

CONTEXT_DATA:
  type: string
  description: Context content to add

TURN_NUMBER:
  type: integer
  optional: true
  description: Associated turn number
```

## Database Operations

### UPDATE ui_conversation_context

```sql
UPDATE ui_conversation_context
SET extracted_entities = json_set(
    extracted_entities,
    '$.context.' || ?,
    json(?)
)
WHERE session_id = ?
```

## Success Criteria

- Context added to session
- Token budget checked
- Old context pruned if needed
- Database committed

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "context_type": "spec",
  "context_tokens": 450,
  "session_total_tokens": 2890,
  "tokens_remaining": 187110,
  "pruning_triggered": false,
  "message": "Context added to conversation"
}
```

## Context Types

| Type | Example | Max Tokens |
|------|---------|-----------|
| file | File content | 1000 |
| spec | Technical spec | 2000 |
| roadmap | Priority from roadmap | 500 |
| priority | Roadmap priority details | 1000 |
| previous_response | Previous agent response | 500 |

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Session not found | Invalid SESSION_ID | Return 404 |
| Context too large | Exceeds max tokens | Truncate or summarize |
| Invalid type | CONTEXT_TYPE not recognized | List valid types |

## Examples

### Example 1: Add Spec Context

```bash
/agents:user_listener:update-context \
  SESSION_ID="SESS-20251027-abc123" \
  CONTEXT_TYPE="spec" \
  CONTEXT_DATA="SPEC-114 defines 30 commands for UI agents..."
```

### Example 2: Add Priority Context

```bash
/agents:user_listener:update-context \
  SESSION_ID="SESS-20251027-abc123" \
  CONTEXT_TYPE="priority" \
  CONTEXT_DATA="PRIORITY-28: User Authentication - status: in_progress"
```

## Implementation Notes

- Check context window before adding (CFR-007 compliance)
- Max total context per session: 200K tokens
- Prune oldest context if limit exceeded
- Store context as JSON in extracted_entities
- Tag context with source and timestamp
- Allow override for high-priority context (critical, high severity)
