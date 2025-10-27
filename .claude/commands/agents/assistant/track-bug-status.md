---
command: track-bug-status
agent: assistant
action: update_bug_status
tables: [ui_bug_reports]
tools: [notification_system]
duration: 5m
---

## Purpose

Monitor bug lifecycle and resolution with status transitions and notifications.

## Input Parameters

```yaml
BUG_ID:
  type: string
  description: Bug identifier
  example: "BUG-087"

STATUS:
  type: string
  enum: [open, in_progress, resolved, closed]
  description: New bug status

RESOLUTION_NOTES:
  type: string
  optional: true
  description: Notes about resolution (required if STATUS=resolved)

NOTIFY_REPORTER:
  type: boolean
  optional: true
  default: true
  description: Send notification about status change
```

## Database Operations

### UPDATE ui_bug_reports

```sql
UPDATE ui_bug_reports
SET status = ?, resolved_at = datetime('now'), resolution_notes = ?
WHERE bug_id = ?
```

## External Tools

### Notification System

Send notification when status changes, especially for resolution.

## Success Criteria

- Status transition valid
- Timestamp updated
- Resolution notes stored (if provided)
- Notification sent (if enabled)
- Audit trail created

## Output Format

```json
{
  "success": true,
  "bug_id": "BUG-087",
  "previous_status": "in_progress",
  "new_status": "resolved",
  "resolved_at": "2025-10-27T14:30:00Z",
  "resolution_notes": "Fixed session timeout to 24 hours in auth module",
  "message": "Bug status updated and notified to team"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Bug not found | Invalid BUG_ID | Return 404 |
| Invalid status | STATUS not in enum | Reject and list valid values |
| Invalid transition | Status change not allowed | List valid transitions |
| Missing notes | STATUS=resolved but no notes | Reject, require notes |

## Examples

### Example 1: Mark as In Progress

```bash
/agents:assistant:track-bug-status \
  BUG_ID="BUG-087" \
  STATUS="in_progress"
```

### Example 2: Mark as Resolved

```bash
/agents:assistant:track-bug-status \
  BUG_ID="BUG-087" \
  STATUS="resolved" \
  RESOLUTION_NOTES="Fixed session timeout to 24 hours in auth module" \
  NOTIFY_REPORTER=true
```

## Implementation Notes

- Valid status transitions:
  - open → in_progress
  - open → closed
  - in_progress → resolved
  - in_progress → closed
  - resolved → closed
  - Any → open (reopen)
- Resolved status requires resolution_notes
- resolved_at timestamp set to current time
- Keep audit trail of all status changes
- Notification includes bug_id, new_status, and resolution_notes (if applicable)
