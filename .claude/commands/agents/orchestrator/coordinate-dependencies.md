---
command: orchestrator.coordinate-dependencies
agent: orchestrator
action: coordinate_dependencies
description: Manage specs_task_dependency graph for task coordination
tables:
  read: [specs_task, specs_task_dependency]
  write: [specs_task_dependency]
required_tools: [sqlite3, database]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
  - CFR-015: Centralized database storage (data/ directory)
---

# Command: orchestrator.coordinate-dependencies

## Purpose

Manage and coordinate the task dependency graph by:
1. Tracking task dependencies (specs_task_dependency)
2. Updating dependency status as tasks complete
3. Detecting circular dependencies (deadlocks)
4. Unblocking dependent tasks when dependencies complete
5. Validating dependency constraints

## Parameters

```python
parameters = {
    "ACTION": "update_status",  # "update_status", "check_deadlocks", "validate_graph"
    "TASK_ID": "TASK-31-1",
    "NEW_STATUS": "completed",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
}
```

## Database Schema

### specs_task_dependency Table

```sql
CREATE TABLE specs_task_dependency (
    dependency_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    dependency_id_ref TEXT NOT NULL,
    dependency_type TEXT,           -- 'hard' (blocking) or 'soft' (advisory)
    dependency_status TEXT,         -- 'pending', 'blocked', 'completed'
    created_at TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES specs_task(task_id),
    FOREIGN KEY (dependency_id_ref) REFERENCES specs_task(task_id)
);
```

## Core Operations

### 1. Update Dependency Status

When a task completes, update its dependencies:

```sql
UPDATE specs_task_dependency
SET dependency_status = 'completed',
    resolved_at = CURRENT_TIMESTAMP
WHERE dependency_id_ref = ? AND dependency_type = 'hard';
```

### 2. Unblock Dependent Tasks

When all dependencies for a task are resolved:

```sql
UPDATE specs_task
SET status = 'ready'
WHERE task_id IN (
    SELECT task_id FROM specs_task_dependency
    WHERE dependency_id_ref = ?
    AND dependency_status = 'completed'
    AND (SELECT COUNT(*) FROM specs_task_dependency std2
         WHERE std2.task_id = specs_task.task_id
         AND std2.dependency_status != 'completed') = 0
);
```

### 3. Detect Circular Dependencies

Check for cycles in dependency graph:

```sql
WITH RECURSIVE dependency_chain AS (
    SELECT task_id, dependency_id_ref, 1 as depth
    FROM specs_task_dependency
    WHERE dependency_type = 'hard'

    UNION ALL

    SELECT dc.task_id, std.dependency_id_ref, dc.depth + 1
    FROM dependency_chain dc
    JOIN specs_task_dependency std ON dc.dependency_id_ref = std.task_id
    WHERE dc.depth < 10
)
SELECT DISTINCT task_id
FROM dependency_chain
WHERE dependency_id_ref IN (
    SELECT task_id FROM dependency_chain dc2
    WHERE dc2.dependency_id_ref = dependency_chain.task_id
);
```

## Operations

### Operation 1: Update Dependency Status

```python
# When task completes
invoke_command("coordinate-dependencies", {
    "ACTION": "update_status",
    "TASK_ID": "TASK-31-1",
    "NEW_STATUS": "completed"
})
```

**Output**:
```json
{
    "success": true,
    "action": "update_status",
    "task_id": "TASK-31-1",
    "dependencies_resolved": 2,
    "dependent_tasks_unblocked": [
        "TASK-31-2",
        "TASK-32-1"
    ],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 2: Detect Deadlocks

```python
invoke_command("coordinate-dependencies", {
    "ACTION": "check_deadlocks",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "check_deadlocks",
    "deadlocks_detected": 0,
    "circular_dependencies": [],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 3: Validate Graph

```python
invoke_command("coordinate-dependencies", {
    "ACTION": "validate_graph"
})
```

**Output**:
```json
{
    "success": true,
    "action": "validate_graph",
    "total_tasks": 12,
    "total_dependencies": 18,
    "valid": true,
    "issues": [],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

## Dependency Types

- **hard**: Task cannot start until dependency completes (blocking)
- **soft**: Task is advisory only (informational)

## Success Criteria

1. Dependency status updates atomic and correct
2. Circular dependencies detected before execution
3. Dependent tasks correctly unblocked
4. No orphaned dependencies
5. Dependency graph remains acyclic
6. All updates logged with timestamp

## Deadlock Detection Algorithm

1. Start with any unresolved task
2. Follow hard dependencies recursively
3. If we reach a task we started with, circle detected
4. Report all circular task chains
5. Halt execution until resolved

## Error Handling

```json
{
    "success": false,
    "error": "circular_dependency_detected",
    "message": "Deadlock detected in dependency graph",
    "circular_chain": ["TASK-31-1", "TASK-31-2", "TASK-31-1"],
    "affected_tasks": ["TASK-31-1", "TASK-31-2"]
}
```

## Related Commands

- find-available-work.md (uses dependency status)
- create-parallel-tasks.md (respects dependencies)
- detect-deadlocks.md (focused deadlock detection)
