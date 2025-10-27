---
command: manage-session
agent: user_listener
action: create_close_pause_sessions
tables: [ui_conversation_context]
tools: []
duration: 5m
---

## Purpose

Create, close, or pause conversation sessions with state management.

## Input Parameters

```yaml
ACTION:
  type: string
  enum: [create, close, pause, resume]
  description: Session action

SESSION_ID:
  type: string
  optional: true
  description: Required for close/pause/resume actions

USER_ID:
  type: string
  optional: true
  description: User identifier (for create)
```

## Database Operations

### INSERT ui_conversation_context (for CREATE)

```sql
INSERT INTO ui_conversation_context (
    session_id, turn_number, created_at
) VALUES (?, 0, datetime('now'))
```

### UPDATE ui_conversation_context (for CLOSE/PAUSE/RESUME)

```sql
UPDATE ui_conversation_context
SET status = ?
WHERE session_id = ?
```

## Success Criteria

- Session created with unique ID (if ACTION=create)
- Session marked closed/paused/resumed
- Session data archived (if old)
- Database transaction committed

## Output Format

```json
{
  "success": true,
  "action": "create",
  "session_id": "SESS-20251027-xyz789",
  "user_id": "user@example.com",
  "status": "active",
  "created_at": "2025-10-27T10:30:00Z",
  "message": "Session created and ready for use"
}
```

## Session Statuses

| Status | Description | Can Resume |
|--------|-------------|-----------|
| active | Current conversation | N/A |
| paused | Temporarily paused | Yes |
| closed | Completed conversation | No |
| archived | Old session (>30 days) | No |

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Session not found | Invalid SESSION_ID | List recent sessions |
| Invalid action | ACTION not in enum | List valid actions |
| Invalid transition | Can't close paused session | Require resume first |

## Examples

### Example 1: Create New Session

```bash
/agents:user_listener:manage-session \
  ACTION="create" \
  USER_ID="user@example.com"
```

**Response**:
```json
{
  "action": "create",
  "session_id": "SESS-20251027-xyz789",
  "status": "active"
}
```

### Example 2: Close Session

```bash
/agents:user_listener:manage-session \
  ACTION="close" \
  SESSION_ID="SESS-20251027-abc123"
```

### Example 3: Pause Session

```bash
/agents:user_listener:manage-session \
  ACTION="pause" \
  SESSION_ID="SESS-20251027-abc123"
```

## Implementation Notes

- Session IDs use format: `SESS-{YYYYMMDD-HHMM}-{6-char-random}`
- Create inserts initial row with turn_number=0
- Pause allows resumption later
- Close prevents resumption
- Archive sessions older than 30 days
- Maintain conversation history even after closing
- Generate session summaries on close
