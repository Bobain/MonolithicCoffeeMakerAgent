---
command: extract-entities
agent: user_listener
action: extract_parameters_and_entities
tables: [ui_conversation_context]
tools: [llm]
duration: 10m
---

## Purpose

Parse parameters, file paths, agent names from user input using entity extraction.

## Input Parameters

```yaml
USER_INPUT:
  type: string
  description: User text to parse
  example: "Create a spec for user authentication in coffee_maker/auth/"

INTENT:
  type: string
  description: Classified intent from previous step
  example: "command"

EXPECTED_ENTITIES:
  type: array
  optional: true
  description: Types of entities to extract
  items:
    type: string
    enum: [agent_name, file_path, priority_id, component_name]

SESSION_ID:
  type: string
  description: Conversation session
```

## Database Operations

### UPDATE ui_conversation_context

```sql
UPDATE ui_conversation_context
SET extracted_entities = ?
WHERE session_id = ? AND turn_number = ?
```

## Success Criteria

- Entities extracted as valid JSON
- Entity types validated
- Ambiguities flagged
- Results stored in database

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "extracted_entities": {
    "action": "create",
    "target_type": "spec",
    "target_name": "user authentication",
    "file_paths": ["coffee_maker/auth/"],
    "agent_names": [],
    "priority_ids": [],
    "ambiguities": []
  },
  "confidence": 0.92,
  "message": "Entities extracted successfully"
}
```

## Entity Types

| Type | Examples | Validation |
|------|----------|-----------|
| agent_name | architect, code_developer, user_listener | Must be valid agent |
| file_path | coffee_maker/auth/, tests/test_auth.py | Must be valid path |
| priority_id | PRIORITY-28, PRIORITY-30 | Must match PRIORITY-\d+ |
| component_name | Dashboard, Login, Roadmap | Free text |

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Extraction failed | Invalid format | Return partial results |
| Ambiguous entities | Multiple matches | Flag and ask for clarification |
| Empty input | USER_INPUT is empty | Return empty entities |

## Examples

### Example 1: Extract Implementation Details

```bash
/agents:user_listener:extract-entities \
  USER_INPUT="Create a spec for user authentication in coffee_maker/auth/" \
  INTENT="command" \
  SESSION_ID="SESS-20251027-abc123"
```

**Response**:
```json
{
  "extracted_entities": {
    "action": "create",
    "target_type": "spec",
    "target_name": "user authentication",
    "file_paths": ["coffee_maker/auth/"]
  }
}
```

### Example 2: Extract Agent Names

```bash
/agents:user_listener:extract-entities \
  USER_INPUT="Route this to the code_developer and architect for review" \
  INTENT="command" \
  SESSION_ID="SESS-20251027-abc123"
```

## Implementation Notes

- Use Claude API for entity extraction
- Validate extracted entities against known values
- Flag ambiguous entities and ask for clarification
- Store extracted entities in JSON format
- Entity confidence scores included
- Support partial matches with confidence scores
