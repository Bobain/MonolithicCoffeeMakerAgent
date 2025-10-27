---
command: handle-fallback
agent: user_listener
action: handle_unclassifiable_requests
tables: [ui_conversation_context, notifications]
tools: [llm, notification_system]
duration: 10m
---

## Purpose

Manage unclassifiable or failed requests with helpful clarification prompts.

## Input Parameters

```yaml
SESSION_ID:
  type: string
  description: Conversation session identifier

FAILURE_REASON:
  type: string
  enum: [low_confidence, no_match, agent_unavailable, parse_error]
  description: Why primary routing failed

ORIGINAL_INPUT:
  type: string
  description: Original user input
```

## Database Operations

### UPDATE ui_conversation_context

```sql
UPDATE ui_conversation_context
SET routed_to_agent = 'fallback_handler'
WHERE session_id = ?
```

### INSERT notifications

```sql
INSERT INTO notifications (user_id, title, message, level)
VALUES (?, ?, ?, 'warning')
```

## External Tools

### LLM Clarification

Generate helpful clarification prompt using Claude API.

### Notification System

Send user notification with clarification needed.

## Success Criteria

- Clarification prompt generated
- User notified with request for clarification
- Session updated to reflect fallback handling
- Helpful examples provided

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "failure_reason": "low_confidence",
  "clarification_prompt": "I'm not entirely sure what you're asking. Could you clarify if you want to create, modify, or delete the database schema?",
  "suggested_clarifications": [
    "Do you want to CREATE, READ, UPDATE, or DELETE?",
    "Which component? (authentication, authorization, logging, etc.)",
    "Should this be for a specific priority?"
  ],
  "message": "Clarification requested from user"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid reason | FAILURE_REASON not recognized | Use 'parse_error' |
| LLM error | API call failed | Use generic prompt |

## Failure Reasons

| Reason | Description | Recovery |
|--------|-------------|----------|
| low_confidence | Classification confidence <0.7 | Ask for clarification |
| no_match | No agent found for intent | Suggest available options |
| agent_unavailable | All agents busy | Offer queueing |
| parse_error | Entity extraction failed | Ask for structured format |

## Examples

### Example 1: Low Confidence

```bash
/agents:user_listener:handle-fallback \
  SESSION_ID="SESS-20251027-abc123" \
  FAILURE_REASON="low_confidence" \
  ORIGINAL_INPUT="Something about the database"
```

**Response**:
```json
{
  "clarification_prompt": "I'm not entirely sure what you're asking about the database. Could you clarify if you want to create a new schema, modify an existing one, or troubleshoot an issue?"
}
```

### Example 2: No Matching Agent

```bash
/agents:user_listener:handle-fallback \
  SESSION_ID="SESS-20251027-def456" \
  FAILURE_REASON="no_match" \
  ORIGINAL_INPUT="I want to reorganize the project structure"
```

## Implementation Notes

- Generate personalized clarification prompts using LLM
- Provide multiple clarification options as bullet points
- Suggest available actions/agents
- Keep conversation natural and helpful
- Store fallback event in conversation context
- Log failure reason for analysis
