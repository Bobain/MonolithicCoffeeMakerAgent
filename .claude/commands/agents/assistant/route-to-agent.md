---
command: route-to-agent
agent: assistant
action: route_to_agent
tables: [ui_delegation_log, agent_lifecycle]
tools: []
duration: 10m
---

## Purpose

Select appropriate agent for task based on request type and check availability.

## Input Parameters

```yaml
REQUEST_TYPE:
  type: string
  enum: [implementation, question, bug, design, deployment, refactoring, documentation]
  description: Request type from classify-request

REQUEST_TEXT:
  type: string
  description: Original request for routing decision

PRIORITY:
  type: string
  optional: true
  enum: [low, normal, high, critical]
  default: normal
  description: Request priority level
```

## Database Operations

### INSERT ui_delegation_log

```sql
INSERT INTO ui_delegation_log (
    session_id, request_text, request_type, classified_by,
    target_agent, delegated_at
) VALUES (?, ?, ?, 'assistant', ?, datetime('now'))
```

### SELECT agent_lifecycle

```sql
SELECT agent_name, status FROM agent_lifecycle WHERE agent_name = ? LIMIT 1
```

## Success Criteria

- Agent selected based on request type
- Agent availability checked
- Delegation logged
- Fallback agent identified
- Session ID generated

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "request_type": "implementation",
  "target_agent": "code_developer",
  "target_agent_status": "available",
  "fallback_agent": "architect",
  "routing_confidence": 0.95,
  "message": "Request routed to code_developer"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid request type | REQUEST_TYPE not in enum | List valid types |
| No agent found | No agent handles request_type | Route to assistant |
| All agents busy | All agents have status=busy | Queue in agent_message |

## Agent Routing Map

| Request Type | Primary Agent | Fallback Agent |
|--------------|---------------|----------------|
| implementation | code_developer | architect |
| question | assistant | user_listener |
| bug | project_manager | code_developer |
| design | ux_design_expert | architect |
| deployment | orchestrator | project_manager |
| refactoring | code_developer | architect |
| documentation | assistant | code_developer |

## Examples

### Example 1: Route Implementation

```bash
/agents:assistant:route-to-agent \
  REQUEST_TYPE="implementation" \
  REQUEST_TEXT="Create user authentication module"
```

### Example 2: Route Design

```bash
/agents:assistant:route-to-agent \
  REQUEST_TYPE="design" \
  REQUEST_TEXT="Design responsive dashboard layout" \
  PRIORITY="high"
```

## Implementation Notes

- Use routing map to select primary agent
- Check agent_lifecycle table for availability
- Generate session ID: `SESS-{YYYYMMDD-HHMM}-{6-char-random}`
- Log all routing decisions for audit trail
- Track routing confidence based on request_type match
- Fallback agent used if primary agent unavailable
- Queue message in agent_message table if routing to busy agent
