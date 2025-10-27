---
command: monitor-delegation
agent: assistant
action: monitor_delegation_outcome
tables: [ui_delegation_log]
tools: []
duration: 5m
---

## Purpose

Track delegation outcomes and identify patterns in success rates and agent performance.

## Input Parameters

```yaml
SESSION_ID:
  type: string
  description: Delegation session identifier
  example: "SESS-20251027-abc123"

OUTCOME:
  type: string
  enum: [success, failed, timeout]
  description: Delegation outcome

NOTES:
  type: string
  optional: true
  description: Notes about outcome

COMPLETION_TIME_SECONDS:
  type: integer
  optional: true
  description: Time from delegation to completion
```

## Database Operations

### UPDATE ui_delegation_log

```sql
UPDATE ui_delegation_log
SET outcome = ?, completed_at = datetime('now'), notes = ?
WHERE session_id = ?
```

## Success Criteria

- Outcome recorded
- Timestamp updated
- Metrics calculated
- Patterns identified

## Output Format

```json
{
  "success": true,
  "session_id": "SESS-20251027-abc123",
  "outcome": "success",
  "completion_time": 120,
  "target_agent": "code_developer",
  "agent_success_rate": 0.95,
  "message": "Delegation monitored and metrics updated"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Session not found | Invalid SESSION_ID | Return 404 |
| Invalid outcome | OUTCOME not in enum | List valid values |

## Examples

### Example 1: Successful Delegation

```bash
/agents:assistant:monitor-delegation \
  SESSION_ID="SESS-20251027-abc123" \
  OUTCOME="success" \
  COMPLETION_TIME_SECONDS=120 \
  NOTES="Task completed within SLA"
```

### Example 2: Failed Delegation

```bash
/agents:assistant:monitor-delegation \
  SESSION_ID="SESS-20251027-def456" \
  OUTCOME="failed" \
  NOTES="Agent returned error: file not found"
```

## Implementation Notes

- Outcome must match one of: success, failed, timeout
- completed_at timestamp set to current time
- Calculate success rate per agent
- Track average completion time
- Identify trends (e.g., code_developer success rate dropping)
- Store all notes for analysis
