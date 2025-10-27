---
command: classify-request
agent: assistant
action: classify_request_type
tables: []
tools: [llm]
duration: 10m
---

## Purpose

Determine request type and complexity from natural language input using LLM classification.

## Input Parameters

```yaml
REQUEST_TEXT:
  type: string
  description: User's natural language request
  example: "Create a database schema for user authentication"

CONTEXT:
  type: string
  optional: true
  description: Additional context for classification

REQUEST_HISTORY:
  type: array
  optional: true
  description: Previous related requests for context
```

## Database Operations

None (pure classification, no database writes).

## External Tools

### LLM Classification

Use Claude API to classify request type and complexity:
- Request type: implementation, question, bug, design, deployment, refactoring
- Complexity: simple, medium, complex
- Confidence score: 0.0-1.0

## Success Criteria

- Request type identified
- Complexity assessed
- Confidence score >0.7
- Classification model version tracked

## Output Format

```json
{
  "success": true,
  "request_type": "implementation",
  "complexity": "complex",
  "confidence": 0.92,
  "key_intent": "Create database schema",
  "required_expertise": ["database", "sql", "architecture"],
  "estimated_effort": "6-8 hours",
  "message": "Complex implementation task requiring database expertise"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| LLM error | API call failed | Retry up to 3 times |
| Low confidence | Classification uncertain | Return multiple candidates |
| Empty input | REQUEST_TEXT is empty | Reject and ask for clarification |

## Examples

### Example 1: Implementation Request

```bash
/agents:assistant:classify-request \
  REQUEST_TEXT="Create a database schema for user authentication with role-based access control"
```

**Response**:
```json
{
  "request_type": "implementation",
  "complexity": "complex",
  "confidence": 0.92,
  "required_expertise": ["database", "sql", "architecture"]
}
```

### Example 2: Design Request

```bash
/agents:assistant:classify-request \
  REQUEST_TEXT="Design a responsive dashboard layout for the roadmap visualization"
```

**Response**:
```json
{
  "request_type": "design",
  "complexity": "medium",
  "confidence": 0.88,
  "required_expertise": ["ui", "ux", "responsive_design"]
}
```

## Implementation Notes

- Use Claude API with classification prompt
- Classification types: implementation, question, bug, design, deployment, refactoring, documentation
- Complexity levels: simple (1-2h), medium (3-6h), complex (>6h)
- Confidence threshold: 0.7 (reject lower confidence)
- Cache classification results for identical requests
- Track model version for audit trail
