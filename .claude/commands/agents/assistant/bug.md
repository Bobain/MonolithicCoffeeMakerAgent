# bug

## Purpose
Report bugs and link to priorities: create bug records, analyze severity, link to existing priorities/specs, notify relevant agents.

## Parameters
```yaml
title: str  # Required, bug title
description: str  # Required, detailed description
severity: str = "medium"  # "low" | "medium" | "high" | "critical"
steps_to_reproduce: List[str]  # Required, reproduction steps
priority_id: str = None  # Link to existing priority
auto_create_priority: bool = false  # Create new priority for bug
notify_architect: bool = true  # Notify for high/critical bugs
```

## Workflow
1. Create bug record in database
2. Analyze severity and impact
3. Link to existing priority if provided
4. Create new priority if auto_create_priority=True
5. Notify architect for high/critical bugs
6. Generate bug report
7. Return BugResult

## Database Operations
```sql
-- Create bug record
INSERT INTO bug_tracker (
    bug_id, title, description, severity, status,
    steps_to_reproduce, created_at, priority_id
) VALUES (?, ?, ?, ?, 'open', ?, datetime('now'), ?)

-- Link to priority
UPDATE bug_tracker
SET priority_id = ?, linked_spec_id = ?
WHERE bug_id = ?

-- Create priority for bug
INSERT INTO roadmap_priority (
    priority_id, title, description, status, bug_id, created_at
) VALUES (?, ?, ?, 'pending', ?, datetime('now'))

-- Notify architect
INSERT INTO agent_notification (
    notification_id, agent_type, priority, message, metadata, created_at
) VALUES (?, 'architect', 'high', ?, ?, datetime('now'))
```

## Result Object
```python
@dataclass
class BugResult:
    bug_id: str  # Format: BUG-NNN
    severity: str
    priority_id: str  # None if not linked
    priority_created: bool
    architect_notified: bool
    status: str  # "success" | "failed"
```

## Severity Assessment
- **Critical**: System down, data loss, security breach
- **High**: Major feature broken, performance severely degraded
- **Medium**: Feature partially broken, workaround available
- **Low**: Minor issue, cosmetic problem

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| DuplicateBug | Similar bug exists | Link to existing bug |
| PriorityNotFound | Invalid priority_id | Verify priority exists |
| NotificationFailed | Architect unavailable | Log warning, continue |
| ValidationError | Missing required fields | Check all parameters |

## Example
```python
result = bug(
    title="User login fails with OAuth2",
    description="OAuth2 login redirects to 404 page",
    severity="high",
    steps_to_reproduce=[
        "Navigate to /login",
        "Click 'Sign in with OAuth2'",
        "Observe 404 error"
    ],
    auto_create_priority=True
)
# BugResult(
#   bug_id="BUG-042",
#   severity="high",
#   priority_id="PRIORITY-23",
#   priority_created=True,
#   architect_notified=True,
#   status="success"
# )
```

## Related Commands
- demo() - Bugs found during demos
- delegate() - Route bug fix requests

---
Estimated: 60 lines | Context: ~4% | Examples: bug_examples.md
