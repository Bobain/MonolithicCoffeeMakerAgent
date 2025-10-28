# plan

## Purpose
Create new priority with task breakdown: generate priority ID, create database records, update ROADMAP.md, notify architect.

## Parameters
```yaml
title: str  # Required, priority title
description: str  # Required, detailed description
assigned_agent: str = "code_developer"  # Agent assignment
task_count: int = None  # Auto-generate if None
notify_architect: bool = true  # Request spec creation
```

## Workflow
1. Generate next priority ID (PRIORITY-N)
2. Create task breakdown (auto-generate or use task_count)
3. Insert priority into database
4. Generate task IDs (TASK-N-1, TASK-N-2, ...)
5. Insert tasks into specs_task table
6. Update docs/roadmap/ROADMAP.md
7. Notify architect to create specs
8. Return PlanResult

## Database Operations
```sql
-- Get next priority ID
SELECT MAX(CAST(SUBSTR(priority_id, 10) AS INTEGER)) + 1
FROM roadmap_priority

-- Insert priority
INSERT INTO roadmap_priority (
    priority_id, title, description, status, progress,
    assigned_agent, created_at
) VALUES (?, ?, ?, 'pending', 0, ?, datetime('now'))

-- Insert tasks
INSERT INTO specs_task (
    task_id, priority_id, description, status, created_at
) VALUES (?, ?, ?, 'pending', datetime('now'))

-- Notify architect
INSERT INTO agent_notification (
    notification_id, agent_type, priority, message, metadata, created_at
) VALUES (?, 'architect', 'high', ?, ?, datetime('now'))
```

## Result Object
```python
@dataclass
class PlanResult:
    priority_id: str
    task_ids: List[str]
    tasks_created: int
    roadmap_updated: bool
    architect_notified: bool
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| DuplicatePriority | ID already exists | Regenerate ID |
| InvalidAgent | Unknown assigned_agent | Check valid agents |
| FileWriteError | Can't update ROADMAP.md | Check file permissions |
| NotificationFailed | Architect unavailable | Log warning, continue |

## Example
```python
result = plan(
    title="Implement OAuth2 Support",
    description="Add OAuth2 authentication flow",
    task_count=5
)
# PlanResult(
#   priority_id="PRIORITY-8",
#   task_ids=["TASK-8-1", "TASK-8-2", "TASK-8-3", "TASK-8-4", "TASK-8-5"],
#   tasks_created=5,
#   roadmap_updated=True,
#   architect_notified=True,
#   status="success"
# )
```

## Related Commands
- roadmap() - Sync after creation
- track() - Update created priority

---
Estimated: 65 lines | Context: ~4% | Examples: plan_examples.md
