---
command: track-conversation
agent: user_listener
action: maintain_conversation_history
tables: [ui_conversation_context]
tools: []
duration: 5m
---

## Purpose

Maintain conversation state and history in database for context across sessions.

## Input Parameters

```yaml
SESSION_ID:
  type: string
  description: Conversation session identifier

USER_INPUT:
  type: string
  description: Latest user message

AGENT_RESPONSE:
  type: string
  description: Agent's response (if available)

TURN_NUMBER:
  type: integer
  optional: true
  description: Auto-increment if not provided
```

## Database Operations

### INSERT ui_conversation_context

```sql
INSERT INTO ui_conversation_context (
    session_id, turn_number, user_input, agent_response, created_at
) VALUES (?, ?, ?, ?, datetime('now'))
```

## Success Criteria

- Turn number incremented
- Full context stored
- Database transaction committed
- Context window managed

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "turn_number": 5,
  "messages_in_session": 5,
  "tokens_used": 2340,
  "context_window_percent": 45,
  "message": "Conversation tracked successfully"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Session not found | Invalid SESSION_ID | Create new session |
| Insert failed | Database error | Retry up to 3 times |
| Turn mismatch | TURN_NUMBER doesn't match | Auto-increment instead |

## Examples

### Example 1: Track User Input

```bash
/agents:user_listener:track-conversation \
  SESSION_ID="SESS-20251027-abc123" \
  USER_INPUT="Create a database schema for user authentication" \
  TURN_NUMBER=1
```

### Example 2: Track Full Turn

```bash
/agents:user_listener:track-conversation \
  SESSION_ID="SESS-20251027-abc123" \
  USER_INPUT="What are the authentication requirements?" \
  AGENT_RESPONSE="Authentication should support email, password hashing with bcrypt, and JWT tokens for API access..." \
  TURN_NUMBER=5
```

## Implementation Notes

- Turn numbers auto-increment per session
- Store both user_input and agent_response
- created_at timestamp auto-set
- Calculate tokens used for context window tracking
- Trigger context pruning if >80% of context window used
- Keep last 50 turns per session for long conversations
- Archive old turns to separate table if needed
