---
command: project_manager.update_roadmap
agent: project_manager
action: update_roadmap
data_domain: pm_roadmap
write_tables: [pm_roadmap, pm_priorities, pm_notifications]
read_tables: [arch_specs, dev_implementations, review_reports, shared_config]
required_skills: [roadmap_database_handling, github_integration]
---

# Command: project_manager.update_roadmap

## Purpose
Update the roadmap with new priorities, status changes, and strategic adjustments.

## Input Parameters
- **action_type**: string (required) - Type of update (add_priority|update_status|reorder|remove)
- **priority_id**: string (required for updates) - Priority ID to update
- **priority_data**: object (required for adds) - New priority information
- **new_status**: string (required for status update) - New status value
- **reason**: string (optional) - Reason for the change
- **notify_agents**: boolean (optional) - Send notifications (default: true)

## Database Operations

### READ Operations
```sql
-- Check current roadmap state
SELECT * FROM pm_roadmap
ORDER BY priority_order;

-- Check for related specs
SELECT * FROM arch_specs
WHERE priority_id = :priority_id;

-- Check implementation status
SELECT * FROM dev_implementations
WHERE priority_id = :priority_id;

-- Check review status
SELECT * FROM review_reports
WHERE priority_id = :priority_id;
```

### WRITE Operations
```sql
-- Add new priority
INSERT INTO pm_priorities (
    id,
    title,
    description,
    status,
    priority_order,
    estimated_days,
    assigned_to,
    created_at,
    created_by
) VALUES (
    :priority_id,
    :title,
    :description,
    'planned',
    :order,
    :estimated_days,
    :assigned_to,
    :timestamp,
    'project_manager'
);

-- Update priority status
UPDATE pm_roadmap
SET
    status = :new_status,
    updated_at = :timestamp,
    updated_by = 'project_manager'
WHERE id = :priority_id;

-- Create notification for agents
INSERT INTO pm_notifications (
    id,
    type,
    target_agent,
    priority,
    payload,
    status,
    created_at
) VALUES (
    :notif_id,
    :notif_type,
    :target_agent,
    :priority_level,
    :payload_json,
    'pending',
    :timestamp
);
```

## Required Skills

### roadmap_database_handling
- Manage roadmap database operations
- Ensure data consistency
- Handle complex queries

### github_integration
- Check GitHub PR/Issue status
- Link roadmap items to GitHub
- Monitor CI/CD status

## Execution Steps

1. **Validate Permissions**
   - Verify agent is project_manager
   - Check write access to pm_* tables

2. **Load Required Skills**
   ```python
   roadmap_skill = load_skill(SkillNames.ROADMAP_DATABASE_HANDLING)
   github_skill = load_skill(SkillNames.GITHUB_INTEGRATION)
   ```

3. **Read Current Roadmap State**
   - Query all priorities
   - Build current state snapshot
   - Identify dependencies

4. **Validate Request**
   - Check priority exists (for updates)
   - Validate new status is valid
   - Check for conflicts

5. **Perform Action**

   ### Add Priority
   ```python
   if action_type == 'add_priority':
       # Generate priority ID
       priority_id = f"PRIORITY-{get_next_id()}"

       # Determine order
       max_order = get_max_priority_order()

       # Insert new priority
       db.write('pm_priorities', {
           'id': priority_id,
           'title': priority_data['title'],
           'description': priority_data['description'],
           'status': 'planned',
           'priority_order': max_order + 1
       })
   ```

   ### Update Status
   ```python
   elif action_type == 'update_status':
       # Validate transition
       current = get_priority_status(priority_id)
       if not is_valid_transition(current, new_status):
           raise InvalidTransitionError()

       # Update status
       db.update('pm_roadmap',
           {'status': new_status},
           {'id': priority_id}
       )
   ```

   ### Reorder Priorities
   ```python
   elif action_type == 'reorder':
       # Update priority orders
       for idx, pid in enumerate(priority_data['new_order']):
           db.update('pm_roadmap',
               {'priority_order': idx + 1},
               {'id': pid}
           )
   ```

6. **Check GitHub Status** (if applicable)
   ```bash
   gh pr list --search "priority:${priority_id}"
   gh issue list --search "priority:${priority_id}"
   ```

7. **Send Notifications**
   ```python
   # Notify relevant agents based on action
   if action_type == 'add_priority' and priority_is_ready:
       # Notify architect to create spec
       db.cross_domain_notify('architect', {
           'type': 'spec_requested',
           'priority_id': priority_id,
           'priority_data': priority_data
       })

   elif new_status == 'ready_for_implementation':
       # Notify code_developer
       db.cross_domain_notify('code_developer', {
           'type': 'implementation_ready',
           'priority_id': priority_id,
           'spec_id': spec_id
       })
   ```

8. **Update Metrics**
   ```python
   # Track roadmap health metrics
   db.write('pm_health_metrics', {
       'metric_type': 'priority_added',
       'priority_id': priority_id,
       'timestamp': datetime.now()
   })
   ```

## Error Handling

### InvalidTransitionError
- **Cause**: Invalid status transition
- **Response**: List valid transitions
- **Recovery**: Suggest valid next status

### PriorityNotFoundError
- **Cause**: Priority doesn't exist
- **Response**: List available priorities
- **Recovery**: Create new priority if needed

### ConflictError
- **Cause**: Priority being modified elsewhere
- **Response**: Wait and retry
- **Recovery**: Use optimistic locking

### GitHubConnectionError
- **Cause**: Can't connect to GitHub
- **Response**: Continue without GitHub data
- **Recovery**: Queue for later sync

## Success Criteria
- [ ] Roadmap updated successfully
- [ ] All affected priorities updated
- [ ] Notifications sent to relevant agents
- [ ] GitHub status checked (if applicable)
- [ ] Metrics updated
- [ ] Audit trail created

## Status Transitions
```
planned → ready_for_spec
ready_for_spec → spec_in_progress
spec_in_progress → ready_for_implementation
ready_for_implementation → in_progress
in_progress → testing
testing → complete
any → blocked
blocked → (previous status)
```

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType
import subprocess
import json

# Initialize database for project_manager
db = DomainDatabase(AgentType.PROJECT_MANAGER)

# Add new priority
new_priority = {
    'title': 'Implement OAuth Authentication',
    'description': 'Add OAuth2 support for GitHub and Google',
    'estimated_days': 5,
    'assigned_to': 'code_developer'
}

priority_id = f"PRIORITY-{get_next_id()}"
db.write('pm_priorities', {
    'id': priority_id,
    **new_priority,
    'status': 'planned'
})

# Update status when spec is ready
db.update('pm_roadmap',
    {'status': 'ready_for_implementation'},
    {'id': priority_id}
)

# Check GitHub for related work
result = subprocess.run(
    ['gh', 'pr', 'list', '--json', 'number,title,state'],
    capture_output=True,
    text=True
)
prs = json.loads(result.stdout)

# Notify code_developer
db.cross_domain_notify('code_developer', {
    'type': 'implementation_ready',
    'priority_id': priority_id,
    'spec_id': 'SPEC-001',
    'github_prs': prs
})

# Update metrics
db.write('pm_health_metrics', {
    'metric_type': 'status_changed',
    'priority_id': priority_id,
    'old_status': 'spec_in_progress',
    'new_status': 'ready_for_implementation',
    'timestamp': datetime.now().isoformat()
})
```

## Metrics & Monitoring
- **Priority velocity**: Priorities completed per week
- **Cycle time**: Time from planned to complete
- **Blocked rate**: Percentage of priorities blocked
- **Spec coverage**: Percentage with specs
- **GitHub linkage**: Priorities with PRs/Issues

## Related Commands
- `project_manager.analyze_health` - Analyze project health
- `project_manager.verify_dod` - Verify Definition of Done
- `project_manager.monitor_github` - Check GitHub status
- `project_manager.send_notification` - Send agent notifications
