---
command: report-bug
agent: assistant
action: create_bug_report
tables: [ui_bug_reports]
tools: [notification_system]
duration: 5m
---

## Purpose

Create structured bug report in database and notify project_manager.

## Input Parameters

```yaml
TITLE:
  type: string
  description: Short bug description
  example: "Login timeout after 5 minutes"

DESCRIPTION:
  type: string
  description: Detailed bug information including steps to reproduce

SEVERITY:
  type: string
  enum: [critical, high, medium, low]
  description: Bug severity level

PRIORITY_ID:
  type: string
  optional: true
  description: Link to affected roadmap priority
  example: "PRIORITY-28"

AFFECTED_COMPONENT:
  type: string
  optional: true
  description: Affected component or area
```

## Database Operations

### INSERT ui_bug_reports

```sql
INSERT INTO ui_bug_reports (
    bug_id, title, description, severity, priority_id,
    reported_by, reported_at, status
) VALUES (?, ?, ?, ?, ?, 'assistant', datetime('now'), 'open')
```

## External Tools

### Notification System

Send notification to project_manager about new bug report.

## Success Criteria

- Bug ID generated in BUG-XXX format
- Database record created
- Severity level valid
- Notification sent to project_manager
- Priority link validated (if provided)

## Output Format

```json
{
  "success": true,
  "bug_id": "BUG-087",
  "title": "Login timeout after 5 minutes",
  "severity": "high",
  "priority_id": "PRIORITY-28",
  "status": "open",
  "created_at": "2025-10-27T10:30:00Z",
  "reported_by": "assistant",
  "message": "Bug report created and notified to project_manager"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid severity | SEVERITY not in enum | Reject and list valid values |
| Priority not found | PRIORITY_ID doesn't exist | Warn but continue |
| Notification failed | System error | Log error, bug still created |

## Examples

### Example 1: High Severity Bug

```bash
/agents:assistant:report-bug \
  TITLE="Login timeout after 5 minutes" \
  DESCRIPTION="Users are automatically logged out after 5 minutes of inactivity. Expected behavior: session should persist for 24 hours." \
  SEVERITY="high" \
  PRIORITY_ID="PRIORITY-28" \
  AFFECTED_COMPONENT="Authentication"
```

### Example 2: Critical Bug

```bash
/agents:assistant:report-bug \
  TITLE="Database connection failing on startup" \
  DESCRIPTION="When starting the daemon, database connection fails with 'too many connections' error. Affects all agents." \
  SEVERITY="critical"
```

## Implementation Notes

- Bug IDs use format: `BUG-{sequential-number}`
- Auto-increment BUG ID counter in database
- Always validate PRIORITY_ID exists in roadmap_priority table
- Notification includes bug_id, title, severity, and link to full report
- Severity enum strictly enforced
- Initial status always 'open'
- reported_by always 'assistant'
- reported_at always current timestamp
