---
command: determine-agent
agent: user_listener
action: determine_target_agent
tables: [agent_lifecycle]
tools: []
duration: 5m
---

## Purpose

Map classified intent to appropriate agent based on routing rules and availability.

## Input Parameters

```yaml
INTENT:
  type: string
  description: Classified intent from classify-intent
  example: "command"

EXTRACTED_ENTITIES:
  type: object
  description: Entities from extract-entities
  properties:
    target_type: string
    action: string

PRIORITY:
  type: string
  optional: true
  enum: [low, normal, high, critical]
  default: normal
```

## Database Operations

### SELECT agent_lifecycle

```sql
SELECT agent_name, status FROM agent_lifecycle
WHERE agent_name IN (?) AND status = 'available'
ORDER BY last_activity DESC
```

## Success Criteria

- Agent selected based on intent
- Availability verified
- Fallback agent identified
- Confidence score returned

## Output Format

```json
{
  "success": true,
  "intent": "command",
  "primary_agent": "architect",
  "primary_availability": "available",
  "fallback_agent": "assistant",
  "fallback_availability": "available",
  "confidence": 0.98,
  "message": "Architect agent selected for spec creation"
}
```

## Agent Selection Rules

| Intent | Target Type | Primary Agent | Fallback |
|--------|------------|---------------|----------|
| command | spec | architect | assistant |
| command | code | code_developer | architect |
| command | design | ux_design_expert | architect |
| question | any | assistant | user_listener |
| request | any | orchestrator | code_developer |

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| No agent found | No match for intent | Default to assistant |
| All agents busy | No available agents | Return busy status |

## Examples

### Example 1: Spec Creation Command

```bash
/agents:user_listener:determine-agent \
  INTENT="command" \
  EXTRACTED_ENTITIES='{"target_type": "spec", "action": "create"}'
```

**Response**:
```json
{
  "primary_agent": "architect",
  "primary_availability": "available"
}
```

### Example 2: Code Implementation

```bash
/agents:user_listener:determine-agent \
  INTENT="command" \
  EXTRACTED_ENTITIES='{"target_type": "code", "action": "implement"}'
```

## Implementation Notes

- Check agent_lifecycle table for agent availability
- Use routing rules to select primary agent
- Identify fallback agent in case primary is unavailable
- Return both primary and fallback options
- Track confidence in agent selection
