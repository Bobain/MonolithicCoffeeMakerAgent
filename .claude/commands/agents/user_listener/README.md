# User Listener Agent Commands

9 commands for intent classification, entity extraction, routing, and conversation management.

## Commands

### Intent Classification (3 commands)

- **classify-intent** - Identify user intent from natural language
  - Input: USER_INPUT, SESSION_ID, TURN_NUMBER (optional), CONTEXT (optional)
  - Output: classified_intent, confidence, requires_clarification, next_step
  - Use case: LLM-based classification (question|command|request|clarification)

- **extract-entities** - Parse parameters, file paths, agent names
  - Input: USER_INPUT, INTENT, EXPECTED_ENTITIES (optional), SESSION_ID (optional)
  - Output: extracted_entities (JSON), confidence, ambiguities
  - Use case: Extract structured data (agent_names, file_paths, priority_ids)

- **determine-agent** - Map intent to appropriate agent
  - Input: INTENT, EXTRACTED_ENTITIES, PRIORITY (optional)
  - Output: primary_agent, fallback_agent, availability, confidence
  - Use case: Select best agent for the request

### Routing (3 commands)

- **route-request** - Forward classified request to target agent
  - Input: TARGET_AGENT, REQUEST_DATA, SESSION_ID
  - Output: message_id, status=pending, notification_sent
  - Use case: Send request to appropriate agent via agent_message table

- **queue-for-agent** - Enqueue work when agent is busy
  - Input: TARGET_AGENT, REQUEST_DATA, SESSION_ID, PRIORITY (optional)
  - Output: queue_position, queue_size, estimated_wait_minutes
  - Use case: Queue requests for busy agents with priority

- **handle-fallback** - Manage unclassifiable or failed requests
  - Input: SESSION_ID, FAILURE_REASON, ORIGINAL_INPUT
  - Output: clarification_prompt, suggested_clarifications
  - Use case: Ask user for clarification when classification fails

### Conversation Management (3 commands)

- **track-conversation** - Maintain conversation state in database
  - Input: SESSION_ID, USER_INPUT, AGENT_RESPONSE (optional), TURN_NUMBER (optional)
  - Output: turn_number, messages_in_session, tokens_used, context_window_percent
  - Use case: Store conversation history for context

- **update-context** - Add context to ongoing conversation
  - Input: SESSION_ID, CONTEXT_TYPE, CONTEXT_DATA, TURN_NUMBER (optional)
  - Output: context_tokens, session_total_tokens, tokens_remaining, pruning_triggered
  - Use case: Enrich conversation with specs, files, roadmap data

- **manage-session** - Create/close/pause conversation sessions
  - Input: ACTION (create|close|pause|resume), SESSION_ID (for close/pause), USER_ID (for create)
  - Output: session_id, status, created_at
  - Use case: Session lifecycle management (create new, pause, resume, close)

## Implementation

Located in: `coffee_maker/commands/user_listener_commands.py`

### Usage Example

```python
from coffee_maker.commands.user_listener_commands import UserListenerCommands

listener = UserListenerCommands()

# Create session
session = listener.manage_session(action="create", user_id="user@example.com")
session_id = session["session_id"]

# Classify intent
intent_result = listener.classify_intent(
    user_input="Create a spec for authentication",
    session_id=session_id
)

# Extract entities
entities_result = listener.extract_entities(
    user_input=intent_result["user_input"],
    intent=intent_result["classified_intent"],
    session_id=session_id
)

# Determine target agent
agent_result = listener.determine_agent(
    intent=intent_result["classified_intent"],
    extracted_entities=entities_result["extracted_entities"]
)

# Route to agent
routing_result = listener.route_request(
    target_agent=agent_result["primary_agent"],
    request_data={
        "user_input": intent_result["user_input"],
        "classified_intent": intent_result["classified_intent"],
        "extracted_entities": entities_result["extracted_entities"]
    },
    session_id=session_id
)

# Track conversation
listener.track_conversation(
    session_id=session_id,
    user_input=intent_result["user_input"],
    agent_response="Processing your request..."
)

# Close session
listener.manage_session(action="close", session_id=session_id)
```

## Database Tables

- `ui_conversation_context` - Conversation state and history
- `ui_intent_classification` - Classification results and confidence scores
- `ui_routing_log` - Routing decisions and patterns

## Agent Routing Map

| Intent | Primary Agent | Fallback |
|--------|---------------|----------|
| command | architect | assistant |
| question | assistant | user_listener |
| request | orchestrator | code_developer |

## Testing

Run tests with:
```bash
pytest tests/unit/test_spec114_commands.py::TestUserListenerCommands -v
```

Test coverage includes:
- Intent classification (command, question, request)
- Entity extraction (agent_names, file_paths, priority_ids)
- Agent determination with availability
- Request routing to agents
- Queueing for busy agents
- Fallback handling (low confidence, no match, unavailable)
- Conversation tracking
- Context addition with token budgeting
- Session management (create, pause, resume, close)

## Performance

- Intent classification: <1s (LLM call)
- Entity extraction: <500ms
- Agent determination: <100ms
- Request routing: <100ms
- Queueing: <100ms
- Conversation tracking: <50ms
- Context update: <100ms

## Context Window Management (CFR-007)

- Max context per session: 200K tokens
- Auto-prune when >80% used
- Track tokens_used and tokens_remaining
- Respect CFR-007 (context budget <30%)

## Intent Types

| Type | Example | Routing |
|------|---------|---------|
| question | "How do I create a spec?" | assistant |
| command | "Create a spec for auth" | architect |
| request | "Add authentication feature" | orchestrator |
| clarification | "What do you mean by schema?" | user_listener |

## Error Handling

All commands return:
```json
{
  "success": true/false,
  "error": "error message if failed",
  "...": "command-specific results"
}
```

Common errors:
- Invalid action (manage-session)
- Session not found
- Low confidence classification (<0.7)
- Agent unavailable (no agents match intent)
- Invalid priority value
