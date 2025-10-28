# track

## Purpose
Update priority/task status, calculate progress percentage, send notifications to relevant agents.

## Parameters
```yaml
priority_id: str  # Required, format: PRIORITY-N
updates: dict  # Required, {status: str, progress: int, metadata: dict}
notify: bool = true  # Send agent notifications
auto_milestone: bool = true  # Auto-notify at 25%, 50%, 75%, 100%
```

## Workflow
1. Load priority from database
2. Calculate previous progress state
3. Apply updates (status, progress, metadata)
4. Calculate new progress from task completion
5. Detect milestone achievements (25%, 50%, 75%, 100%)
6. Send notifications if enabled
7. Return TrackResult with notification count

## Database Operations
```sql
-- Update priority
UPDATE roadmap_priority
SET
    status = ?,
    progress = ?,
    metadata = json_patch(metadata, ?),
    updated_at = datetime('now')
WHERE priority_id = ?

-- Calculate progress from tasks
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed
FROM specs_task
WHERE priority_id = ?

-- Send notification
INSERT INTO agent_notification (
    notification_id, agent_type, priority, message, metadata, created_at, status
) VALUES (?, ?, 'medium', ?, ?, datetime('now'), 'pending')
```

## Result Object
```python
@dataclass
class TrackResult:
    priority_id: str
    previous_progress: int
    current_progress: int
    status: str  # Priority status
    notifications_sent: int
    milestones_achieved: List[int]  # [25, 50] if crossed
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| PriorityNotFound | Invalid priority_id | Verify priority exists |
| InvalidProgress | Progress < 0 or > 100 | Check progress value |
| NotificationFailed | Agent unavailable | Log warning, continue |
| DatabaseError | Update failed | Retry with backoff |

## Example
```python
result = track(
    priority_id="PRIORITY-5",
    updates={"status": "in_progress", "progress": 50},
    notify=True
)
# TrackResult(
#   priority_id="PRIORITY-5",
#   previous_progress=30,
#   current_progress=50,
#   status="in_progress",
#   notifications_sent=2,
#   milestones_achieved=[50],
#   status="success"
# )
```

## Related Commands
- roadmap() - Sync ROADMAP.md
- plan() - Create priorities

---
Estimated: 65 lines | Context: ~4% | Examples: track_examples.md
