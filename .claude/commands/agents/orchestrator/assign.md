# assign

## Purpose
Assign tasks to agents for parallel execution: analyze dependencies, find available work, create orchestrator_task entries, notify agents.

## Parameters
```yaml
priority_id: str = None  # Assign all tasks for priority
task_ids: List[str] = None  # Specific tasks to assign
max_parallel: int = 3  # Max concurrent tasks
force: bool = false  # Override dependency checks
```

## Workflow
1. Load specs_task entries (filtered by priority or task_ids)
2. Analyze specs_task_dependency graph
3. Find tasks with no unmet dependencies
4. Check agent availability (agent_lifecycle)
5. Create orchestrator_task entries
6. Notify assigned agents via agent_notification
7. Return AssignResult with assignment counts

## Database Operations
```sql
-- Find available tasks (no blocking dependencies)
SELECT st.task_id, st.spec_id, st.priority_id, st.description,
       st.estimated_hours, st.assigned_agent
FROM specs_task st
LEFT JOIN specs_task_dependency std ON st.task_id = std.dependent_task_id
LEFT JOIN specs_task dep ON std.blocking_task_id = dep.task_id
WHERE st.status = 'pending'
  AND (dep.status = 'completed' OR dep.task_id IS NULL)
  AND st.priority_id = COALESCE(?, st.priority_id)
GROUP BY st.task_id
HAVING COUNT(CASE WHEN dep.status != 'completed' THEN 1 END) = 0

-- Create orchestrator task
INSERT INTO orchestrator_task (
    orchestrator_task_id, task_id, agent_type, status,
    assigned_at, metadata
) VALUES (?, ?, ?, 'assigned', datetime('now'), ?)

-- Notify agent
INSERT INTO agent_notification (
    notification_id, agent_type, priority, message, metadata, created_at
) VALUES (?, ?, 'high', ?, ?, datetime('now'))
```

## Result Object
```python
@dataclass
class AssignResult:
    tasks_assigned: int
    assignments: List[dict]  # [{task_id, agent_type, orchestrator_task_id}]
    blocked_tasks: int
    status: str  # "success" | "partial" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| NoAvailableWork | All tasks blocked | Wait for dependencies |
| NoHealthyAgents | No agents available | Start agents first |
| DependencyCycle | Circular dependencies | Fix dependency graph |
| AssignmentFailed | Database error | Retry with backoff |

## Example
```python
result = assign(priority_id="PRIORITY-8", max_parallel=3)
# AssignResult(
#   tasks_assigned=3,
#   assignments=[
#     {"task_id": "TASK-8-1", "agent_type": "code_developer", "orchestrator_task_id": "ot-001"},
#     {"task_id": "TASK-8-2", "agent_type": "code_developer", "orchestrator_task_id": "ot-002"}
#   ],
#   blocked_tasks=2,
#   status="success"
# )
```

## Related Commands
- agents() - Check agent availability
- worktrees() - Create isolated work environments

---
Estimated: 60 lines | Context: ~4% | Examples: assign_examples.md
