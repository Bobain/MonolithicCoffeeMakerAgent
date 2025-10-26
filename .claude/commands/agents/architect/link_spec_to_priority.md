---
command: architect.link_spec_to_priority
agent: architect
action: link_spec_to_priority
data_domain: arch_specs
write_tables: [arch_specs, pm_roadmap]
read_tables: [arch_specs, pm_roadmap]
required_skills: [technical_specification_handling]
---

# Command: architect.link_spec_to_priority

## Purpose
Link an existing technical specification to a roadmap priority (bidirectional reference).

## Input Parameters
- **spec_id**: string (required) - Specification to link (e.g., "SPEC-131")
- **priority_id**: string (required) - Priority to link (e.g., "PRIORITY-28")
- **notify_project_manager**: boolean (optional, default: true) - Send notification to project_manager

## Database Operations

### READ Operations
```sql
-- Verify spec exists
SELECT * FROM arch_specs WHERE id = :spec_id;

-- Verify priority exists
SELECT * FROM pm_roadmap WHERE id = :priority_id;

-- Check if already linked
SELECT roadmap_item_id FROM arch_specs WHERE id = :spec_id;
```

### WRITE Operations
```sql
-- Link spec to priority (architect domain)
UPDATE arch_specs
SET roadmap_item_id = :priority_id,
    linked_at = :timestamp,
    linked_by = 'architect'
WHERE id = :spec_id;

-- Link priority to spec (project manager domain)
UPDATE pm_roadmap
SET spec_id = :spec_id,
    spec_linked_at = :timestamp
WHERE id = :priority_id;
```

## Required Skills

### technical_specification_handling
- Validates spec exists and is in valid state
- Ensures bidirectional consistency

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to arch_specs domain

2. **Load Required Skills**
   ```python
   spec_skill = load_skill(SkillNames.TECHNICAL_SPECIFICATION_HANDLING)
   ```

3. **Verify Spec Exists**
   - Query arch_specs for spec_id
   - If not found, return SpecNotFoundError
   - Check spec status (should be draft or in_progress)

4. **Verify Priority Exists**
   - Query pm_roadmap for priority_id
   - If not found, return PriorityNotFoundError
   - Check priority status

5. **Check for Existing Link**
   - If spec already linked to different priority, return error
   - If priority already linked to different spec, return error

6. **Create Bidirectional Link**
   - Update arch_specs.roadmap_item_id = priority_id
   - Update pm_roadmap.spec_id = spec_id
   - Set link timestamps and metadata

7. **Create Audit Trail Entry**
   - Record link operation in system_audit table

8. **Notify Project Manager** (if notify_project_manager=true)
   ```python
   db.cross_domain_notify('project_manager', {
       'type': 'spec_linked_to_priority',
       'spec_id': spec_id,
       'priority_id': priority_id,
       'message': f'Specification {spec_id} linked to {priority_id}'
   })
   ```

## Error Handling

### SpecNotFoundError
- **Cause**: Specification doesn't exist
- **Response**: Return error with spec_id
- **Recovery**: Verify spec_id is correct

### PriorityNotFoundError
- **Cause**: Priority doesn't exist in roadmap
- **Response**: Return error with priority_id
- **Recovery**: Create priority first via project_manager

### AlreadyLinkedError
- **Cause**: Spec or priority already linked to different item
- **Response**: Return error with existing link details
- **Recovery**: Unlink first or use different spec/priority

### PermissionError
- **Cause**: Agent is not architect
- **Response**: Return permission denied
- **Recovery**: None - only architect can link specs

## Success Criteria
- [ ] Spec updated with priority_id
- [ ] Priority updated with spec_id
- [ ] Audit trail created
- [ ] Project manager notified
- [ ] Bidirectional link established

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Link spec to priority
result = db.execute_command('architect.link_spec_to_priority', {
    'spec_id': 'SPEC-131',
    'priority_id': 'PRIORITY-28',
    'notify_project_manager': True
})

# Returns
{
    'success': True,
    'spec_id': 'SPEC-131',
    'priority_id': 'PRIORITY-28',
    'notification_sent': True
}
```

## Output Format

```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "priority_id": "PRIORITY-28",
  "notification_sent": true,
  "linked_at": "2025-10-26T12:34:56Z"
}
```

## Related Commands
- `architect.create_spec` - Create new specification
- `architect.update_spec` - Modify existing specification
- `project_manager.create_priority` - Create new roadmap priority
