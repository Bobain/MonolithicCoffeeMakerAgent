---
command: architect.update_task_status
agent: architect
action: update_task_status
data_domain: dev_implementations
write_tables: [dev_implementation_tasks, system_audit]
read_tables: [dev_implementation_tasks]
required_skills: []
---

# Command: architect.update_task_status

## Purpose
Update task status (pending → in_progress → completed → blocked) for monitoring and orchestration.

## Input Parameters
- **task_id**: string (required) - Task to update (e.g., "TASK-31-1")
- **new_status**: string (required) - New status: "pending", "in_progress", "completed", "blocked"
- **notes**: string (optional) - Status change notes
- **completed_at**: string (optional) - Completion timestamp (if status=completed)

## Database Operations

### READ Operations
```sql
-- Get task
SELECT * FROM dev_implementation_tasks WHERE id = :task_id;

-- Get task's task group
SELECT * FROM dev_implementations
WHERE task_group_id = (
    SELECT task_group_id FROM dev_implementation_tasks WHERE id = :task_id
);
```

### WRITE Operations
```sql
-- Update task status
UPDATE dev_implementation_tasks
SET status = :new_status,
    completed_at = :completed_at,
    notes = :notes,
    updated_at = :timestamp,
    updated_by = 'architect'
WHERE id = :task_id;

-- Create audit trail
INSERT INTO system_audit (
    table_name, item_id, action, field_changed,
    old_value, new_value, changed_by, changed_at, notes
) VALUES (
    'dev_implementation_tasks', :task_id, 'update', 'status',
    :old_status, :new_status, 'architect', :timestamp, :notes
);

-- Update task group status if all tasks complete
UPDATE dev_implementations
SET status = 'completed',
    completed_at = :timestamp
WHERE task_group_id = :task_group_id
  AND status != 'completed'
  AND (SELECT COUNT(*) FROM dev_implementation_tasks
       WHERE task_group_id = :task_group_id
       AND status != 'completed') = 0;
```

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to dev_implementations domain

2. **Fetch Task**
   - Query dev_implementation_tasks for task_id
   - If not found, return TaskNotFoundError
   - Get current status and task_group_id

3. **Validate Status Transition**
   - Check current status
   - Validate transition to new_status
   - Allowed transitions:
     - pending → in_progress ✓
     - pending → blocked ✓
     - in_progress → completed ✓
     - in_progress → blocked ✓
     - blocked → pending ✓
     - blocked → in_progress ✓
   - All other transitions invalid

4. **Set Completion Timestamp** (if status=completed)
   - If completed_at not provided, set to now()
   - Record completion time

5. **Update Task Record**
   - Update dev_implementation_tasks table
   - Set new status
   - Set completed_at if applicable
   - Set notes if provided
   - Set updated_at = now()
   - Set updated_by = 'architect'

6. **Create Audit Trail**
   - Record old_status and new_status
   - Record notes explaining change
   - Timestamp the change

7. **Check Task Group Completion**
   - Get task_group_id for this task
   - Query all tasks in group
   - If all tasks completed, mark task group completed
   - Update dev_implementations.status = 'completed'
   - Set completed_at on task group

8. **Send Notifications** (if status changed to completed)
   ```python
   if new_status == 'completed':
       notify_orchestrator({
           'type': 'task_completed',
           'task_id': task_id,
           'task_group_id': task_group_id,
           'message': f'{task_id} completed and ready for merge'
       })
   ```

9. **Return Update Results**
   - Confirm status updated
   - Return old and new status
   - Confirm audit entry created

## Error Handling

### TaskNotFoundError
- **Cause**: Task doesn't exist
- **Response**: Return error with task_id
- **Recovery**: Verify task_id is correct

### InvalidStatusTransition
- **Cause**: Cannot transition from current to requested status
- **Response**: Return error with allowed transitions
- **Recovery**: Check current status and choose valid transition

### ValidationError
- **Cause**: Missing required fields for status (e.g., completed_at for completed)
- **Response**: Return error with missing fields
- **Recovery**: Provide required fields

## Success Criteria
- [ ] Task status updated
- [ ] Audit trail created
- [ ] orchestrator notified if task completed
- [ ] Task group status updated if all tasks complete
- [ ] Status transition valid

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Mark task as in progress
result = db.execute_command('architect.update_task_status', {
    'task_id': 'TASK-31-1',
    'new_status': 'in_progress',
    'notes': 'code_developer claimed this task'
})

# Mark task as completed
result = db.execute_command('architect.update_task_status', {
    'task_id': 'TASK-31-1',
    'new_status': 'completed',
    'notes': 'All tests passing, ready for merge'
})

# Block task due to dependency
result = db.execute_command('architect.update_task_status', {
    'task_id': 'TASK-31-2',
    'new_status': 'blocked',
    'notes': 'Waiting for TASK-31-1 to complete'
})

# Returns
{
    'success': True,
    'task_id': 'TASK-31-1',
    'old_status': 'pending',
    'new_status': 'in_progress',
    'audit_entry_created': True
}
```

## Output Format

```json
{
  "success": true,
  "task_id": "TASK-31-1",
  "old_status": "pending",
  "new_status": "in_progress",
  "task_group_id": "GROUP-31",
  "task_group_status": "in_progress",
  "audit_entry_created": true,
  "updated_at": "2025-10-26T12:34:56Z"
}
```

## Status Lifecycle

```
pending
  ├─> in_progress (developer claims and starts)
  │     ├─> completed (implementation done)
  │     └─> blocked (waiting for dependency)
  └─> blocked (dependency not met)
      ├─> pending (dependency resolved, reset)
      └─> in_progress (when dependencies met)

completed (final state)
blocked (intermediate state)
```

## Task Group Status Rules

Task group status is:
- **pending**: All tasks pending
- **in_progress**: At least one task in_progress
- **completed**: All tasks completed
- **blocked**: At least one task blocked, others not completed

Task group automatically moves to **completed** when:
- ALL tasks are in status "completed"

## Task Status Monitoring

The orchestrator will monitor:
1. Task progress via status changes
2. Blocked tasks (may need intervention)
3. Completion of task groups
4. Timing of transitions
5. Failure patterns (repeated blocks)

## Related Commands
- `architect.create_implementation_tasks` - Create tasks
- `architect.define_task_dependencies` - Set task dependencies
- `code_developer.claim_work` - Developer claims task
