---
command: orchestrator.find-available-work
agent: orchestrator
action: find_available_work
description: Query specs_task table for parallelizable tasks that can be executed
tables:
  read: [specs_task, specs_specification, roadmap_priority]
  write: []
required_tools: [sqlite3, database]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
  - CFR-015: Centralized database storage (data/ directory)
---

# Command: orchestrator.find-available-work

## Purpose

Find tasks from the specs_task table that are ready for execution, considering:
- Task status (pending, ready, blocked)
- Dependency graph (no unresolved dependencies)
- Resource requirements
- Parallelizability constraints
- Current workload

## Database Query

Query the specs_task and specs_task_dependency tables to identify tasks that:
1. Have status = 'ready' or 'pending'
2. Have all dependencies completed (resolved in specs_task_dependency)
3. Are not currently assigned to an active agent
4. Meet resource requirements

## Parameters

```python
parameters = {
    "MAX_PARALLEL": 4,           # Maximum parallel tasks to return
    "PRIORITY_FILTER": "all",    # "high", "medium", "low", or "all"
    "EXCLUDE_BLOCKED": True,     # Exclude tasks with unresolved dependencies
    "RESOURCE_CHECK": True       # Check resource requirements
}
```

## SQL Query Pattern

```sql
SELECT
    st.task_id,
    st.spec_id,
    ss.title as spec_title,
    st.status,
    st.priority,
    st.estimated_hours,
    COUNT(DISTINCT std.dependency_id) as dependency_count
FROM specs_task st
JOIN specs_specification ss ON st.spec_id = ss.id
LEFT JOIN specs_task_dependency std ON st.task_id = std.task_id
WHERE
    st.status IN ('ready', 'pending')
    AND st.task_id NOT IN (
        SELECT task_id FROM orchestrator_task
        WHERE status IN ('running', 'spawned')
    )
    AND (SELECT COUNT(*) FROM specs_task_dependency std2
         WHERE std2.task_id = st.task_id
         AND std2.dependency_status != 'completed') = 0
GROUP BY st.task_id
ORDER BY st.priority DESC, st.estimated_hours ASC
LIMIT ?;
```

## Output Format

```json
{
    "success": true,
    "available_tasks": [
        {
            "task_id": "TASK-31-1",
            "spec_id": "SPEC-031",
            "spec_title": "Database Schema Phase 1",
            "status": "ready",
            "priority": "high",
            "estimated_hours": 8,
            "dependencies": {
                "total": 2,
                "completed": 2,
                "blocked": 0
            },
            "can_parallelize": true,
            "assigned_agent": null
        },
        {
            "task_id": "TASK-31-2",
            "spec_id": "SPEC-031",
            "spec_title": "Database Schema Phase 2",
            "status": "pending",
            "priority": "high",
            "estimated_hours": 6,
            "dependencies": {
                "total": 1,
                "completed": 1,
                "blocked": 0
            },
            "can_parallelize": false,
            "assigned_agent": null
        }
    ],
    "total_available": 2,
    "resource_available": true,
    "next_check_in_seconds": 30
}
```

## Success Criteria

1. Returns correct task count (up to MAX_PARALLEL)
2. All returned tasks have status 'ready' or 'pending'
3. No tasks with unresolved dependencies returned
4. Tasks ordered by priority and estimated hours
5. Database transaction is read-only
6. Query completes in <1 second

## Error Handling

```python
{
    "success": false,
    "error": "no_available_tasks",
    "message": "No tasks ready for execution",
    "next_check_in_seconds": 60
}
```

## Dependencies

- SQLite3 database connection
- specs_task table
- specs_specification table
- specs_task_dependency table

## Related Commands

- create-parallel-tasks.md (creates orchestrator_task entries)
- coordinate-dependencies.md (manages dependency graph)
