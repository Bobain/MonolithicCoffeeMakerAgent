---
command: architect.update_spec
agent: architect
action: update_spec
data_domain: arch_specs
write_tables: [arch_specs, arch_spec_sections, system_audit]
read_tables: [arch_specs, arch_spec_sections]
required_skills: [technical_specification_handling]
---

# Command: architect.update_spec

## Purpose
Modify an existing specification (add sections, update content, change status, bump version).

## Input Parameters
- **spec_id**: string (required) - Specification to update (e.g., "SPEC-131")
- **updates**: object (required) - Fields to update
  - `status`: string - New status (draft|in_progress|approved|deprecated)
  - `content`: object - New content for specific section
  - `estimated_days`: number - Update effort estimate
  - `section_name`: string - Section to update (problem_statement|proposed_solution|etc)
  - `section_content`: string - New section content
- **reason**: string (optional) - Reason for update
- **version**: string (optional) - Version to bump (e.g., "1.1.0")

## Database Operations

### READ Operations
```sql
-- Get specification
SELECT * FROM arch_specs WHERE id = :spec_id;

-- Get current sections
SELECT section_name, content, section_order
FROM arch_spec_sections
WHERE spec_id = :spec_id
ORDER BY section_order;

-- Get current version info
SELECT version FROM arch_specs WHERE id = :spec_id;
```

### WRITE Operations
```sql
-- Update main spec record
UPDATE arch_specs
SET status = :new_status,
    estimated_days = :estimated_days,
    version = :new_version,
    updated_at = :timestamp,
    updated_by = 'architect'
WHERE id = :spec_id;

-- Update or insert section
UPDATE arch_spec_sections
SET content = :new_content,
    updated_at = :timestamp
WHERE spec_id = :spec_id AND section_name = :section_name;

-- Create audit trail
INSERT INTO system_audit (
    table_name, item_id, action, field_changed,
    old_value, new_value, changed_by, changed_at
) VALUES (
    'arch_specs', :spec_id, 'update', :field_name,
    :old_value, :new_value, 'architect', :timestamp
);
```

## Required Skills

### technical_specification_handling
- Validates updated specification structure
- Ensures consistency across sections
- Manages version increments

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to arch_specs domain

2. **Load Required Skills**
   ```python
   spec_skill = load_skill(SkillNames.TECHNICAL_SPECIFICATION_HANDLING)
   ```

3. **Fetch Current Specification**
   - Query arch_specs for spec_id
   - If not found, return SpecNotFoundError
   - Retrieve current version

4. **Validate Status Transition** (if updating status)
   - draft → in_progress (valid)
   - in_progress → approved (valid)
   - approved → deprecated (valid)
   - Other transitions may be invalid

5. **Validate Content Updates** (if updating section)
   - Check section_name is valid
   - Check new content is not empty
   - Validate markdown format

6. **Determine Version Bump**
   - If version parameter provided, use it
   - Else if content changed, increment minor version (1.0.0 → 1.1.0)
   - Else if status changed, increment patch version (1.0.0 → 1.0.1)

7. **Update Specification**
   - Update arch_specs table with new values
   - If section_content provided, update arch_spec_sections
   - Set updated_at timestamp
   - Set updated_by to 'architect'

8. **Create Audit Trail Entries**
   - Create entry for each field changed
   - Record old_value and new_value
   - Record reason if provided

9. **Send Notifications** (if status changed)
   ```python
   if old_status != new_status:
       if new_status == 'approved':
           notify_code_developer(f'{spec_id} approved and ready for implementation')
       elif new_status == 'deprecated':
           notify_architect(f'{spec_id} deprecated')
   ```

10. **Return Update Results**
    - List all fields updated
    - Return old and new version
    - Confirm audit entry created

## Error Handling

### SpecNotFoundError
- **Cause**: Specification doesn't exist
- **Response**: Return error with spec_id
- **Recovery**: Verify spec_id is correct

### InvalidStatusTransition
- **Cause**: Cannot transition from current status to requested status
- **Response**: Return error with current and requested status
- **Recovery**: Check spec status and plan transition

### InvalidSectionName
- **Cause**: Section name is not recognized
- **Response**: Return list of valid section names
- **Recovery**: Use valid section name

### ValidationError
- **Cause**: New content fails validation
- **Response**: Return specific validation error
- **Recovery**: Fix content and retry

## Success Criteria
- [ ] Spec updated in database
- [ ] Audit trail created for each change
- [ ] Version incremented if content changed
- [ ] Status transitions valid
- [ ] Notifications sent if status changed
- [ ] All field updates successful

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Update spec content
result = db.execute_command('architect.update_spec', {
    'spec_id': 'SPEC-131',
    'updates': {
        'section_name': 'testing_strategy',
        'section_content': 'Implement unit tests for all API endpoints...',
        'status': 'in_progress'
    },
    'reason': 'Added comprehensive testing strategy',
    'version': '1.1.0'
})

# Returns
{
    'success': True,
    'spec_id': 'SPEC-131',
    'updated_fields': ['testing_strategy', 'status'],
    'old_version': '1.0.0',
    'new_version': '1.1.0',
    'audit_entry_created': True
}
```

## Output Format

```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "updated_fields": [
    "section_content",
    "status"
  ],
  "old_version": "1.0.0",
  "new_version": "1.1.0",
  "old_status": "draft",
  "new_status": "in_progress",
  "audit_entry_created": true,
  "updated_at": "2025-10-26T12:34:56Z"
}
```

## Version Numbering

Follows Semantic Versioning (MAJOR.MINOR.PATCH):
- MAJOR: Never incremented (specs are spec-specific)
- MINOR: Increment when content/structure changes
- PATCH: Increment when status changes, metadata updates

## Related Commands
- `architect.create_spec` - Create new specification
- `architect.validate_spec_completeness` - Check spec quality
- `architect.link_spec_to_priority` - Link spec to priority
