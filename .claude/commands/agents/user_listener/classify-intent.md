---
command: classify-intent
agent: user_listener
action: classify_user_intent
tables: [ui_conversation_context, ui_intent_classification]
tools: [llm]
duration: 10m
---

## Purpose

Identify user intent from natural language input and store classification results.

## Input Parameters

```yaml
USER_INPUT:
  type: string
  description: Natural language user input
  example: "Create a database schema for users"

SESSION_ID:
  type: string
  description: Conversation session identifier
  example: "SESS-20251027-abc123"

TURN_NUMBER:
  type: integer
  optional: true
  description: Current turn in conversation

CONTEXT:
  type: string
  optional: true
  description: Conversation history for context
```

## Database Operations

### INSERT ui_conversation_context

```sql
INSERT INTO ui_conversation_context (
    session_id, turn_number, user_input, classified_intent, created_at
) VALUES (?, ?, ?, ?, datetime('now'))
```

### INSERT ui_intent_classification

```sql
INSERT INTO ui_intent_classification (
    session_id, turn_number, user_input, classified_intent, confidence, created_at
) VALUES (?, ?, ?, ?, ?, datetime('now'))
```

## Success Criteria

- Intent classified (question, command, request, clarification)
- Confidence score >0.7
- Classification stored in database
- Context updated

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "turn_number": 1,
  "user_input": "Create a database schema for users",
  "classified_intent": "command",
  "confidence": 0.95,
  "requires_clarification": false,
  "next_step": "extract_entities",
  "message": "Intent classified as command with high confidence"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| LLM error | API call failed | Retry up to 3 times |
| Low confidence | Classification uncertain (<0.7) | Return multiple candidates |
| Empty input | USER_INPUT is empty | Reject and ask for clarification |

## Intent Types

| Intent | Description | Example |
|--------|-------------|---------|
| question | User asking for information | "How do I create a user?" |
| command | User requesting action | "Create a database schema" |
| request | User requesting feature | "Add authentication to the app" |
| clarification | User asking for clarification | "What do you mean by schema?" |

## Examples

### Example 1: Command Intent

```bash
/agents:user_listener:classify-intent \
  USER_INPUT="Create a database schema for users" \
  SESSION_ID="SESS-20251027-abc123" \
  TURN_NUMBER=1
```

**Response**:
```json
{
  "classified_intent": "command",
  "confidence": 0.95
}
```

### Example 2: Question Intent

```bash
/agents:user_listener:classify-intent \
  USER_INPUT="How do I add authentication to the application?" \
  SESSION_ID="SESS-20251027-abc123" \
  TURN_NUMBER=2
```

## Implementation Notes

- Use Claude API with intent classification prompt
- Intent types: question, command, request, clarification
- Confidence threshold: 0.7 (reject lower)
- Store classification in database for audit trail
- Include conversation context for better classification
- Track classification model version
