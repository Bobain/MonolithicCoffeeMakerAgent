---
command: orchestrator.create-parallel-tasks
agent: orchestrator
action: create_parallel_tasks
description: Create orchestrator_task entries for available work to enable parallel execution
tables:
  read: [specs_task, specs_specification]
  write: [orchestrator_task]
required_tools: [sqlite3, database]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
  - CFR-015: Centralized database storage (data/ directory)
---

# Command: orchestrator.create-parallel-tasks

## Purpose

Create entries in the orchestrator_task table to represent parallel work distribution. This command:
1. Takes available tasks from find-available-work
2. Creates orchestrator_task records
3. Assigns unique task IDs
4. Sets initial status to 'spawned'
5. Records resource requirements
6. Enables parallel execution tracking

## Parameters

```python
parameters = {
    "TASKS": [
        {
            "task_id": "TASK-31-1",
            "spec_id": "SPEC-031",
            "priority": "high",
            "estimated_hours": 8
        },
        {
            "task_id": "TASK-31-2",
            "spec_id": "SPEC-031",
            "priority": "high",
            "estimated_hours": 6
        }
    ],
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "MAX_PARALLEL": 4
}
```

## Database Operations

### Insert orchestrator_task Records

```sql
INSERT INTO orchestrator_task (
    task_id,
    spec_id,
    status,
    priority,
    estimated_hours,
    assigned_agent,
    created_at,
    started_at,
    completed_at,
    orchestrator_instance_id,
    retry_count,
    error_message
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

### Update specs_task Status

```sql
UPDATE specs_task
SET status = 'assigned'
WHERE task_id = ?;
```

## Input Validation

1. Verify all tasks have valid task_id format (TASK-\d+-\d+)
2. Verify spec_id exists in specs_specification table
3. Verify priority is valid (high, medium, low)
4. Verify estimated_hours is positive integer
5. Ensure total parallel tasks <= MAX_PARALLEL

## Output Format

```json
{
    "success": true,
    "created_tasks": [
        {
            "task_id": "TASK-31-1",
            "status": "spawned",
            "created_at": "2025-10-26T10:30:45Z",
            "orchestrator_id": "orch-20251026-001",
            "retry_count": 0
        },
        {
            "task_id": "TASK-31-2",
            "status": "spawned",
            "created_at": "2025-10-26T10:30:46Z",
            "orchestrator_id": "orch-20251026-001",
            "retry_count": 0
        }
    ],
    "total_created": 2,
    "timestamp": "2025-10-26T10:30:46Z"
}
```

## Task Status Lifecycle

```
pending (specs_task)
    ↓
ready (specs_task)
    ↓
spawned (orchestrator_task created)
    ↓
running (agent spawned)
    ↓
completed (task finished)
```

## Parallel Execution Constraints

- Maximum 4 tasks can run in parallel
- Tasks with hard dependencies must run sequentially
- Tasks from different spec groups can run in parallel
- Monitor total resource consumption

## Success Criteria

1. All orchestrator_task records created successfully
2. specs_task status updated to 'assigned'
3. No duplicate task_ids in orchestrator_task
4. Timestamp recorded for audit trail
5. Database transaction committed atomically

## Error Handling

```python
{
    "success": false,
    "error": "validation_failed",
    "message": "Invalid task format: TASK-31",
    "failed_tasks": ["TASK-31"],
    "created_count": 1
}
```

## Rollback on Failure

If any insert fails, rollback all created records:
- Delete inserted orchestrator_task records
- Revert specs_task status to previous state
- Log error for investigation

## Related Commands

- find-available-work.md (identifies tasks to parallelize)
- spawn-agent-session.md (launches agents for created tasks)
- coordinate-dependencies.md (manages task graph)
