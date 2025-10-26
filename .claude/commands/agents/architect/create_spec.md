---
command: architect.create_spec
agent: architect
action: create_spec
data_domain: arch_specs
write_tables: [arch_specs, arch_spec_sections]
read_tables: [pm_roadmap, dev_implementations, shared_config]
required_skills: [technical_specification_handling, database_schema_guide]
---

# Command: architect.create_spec

## Purpose
Create a comprehensive technical specification for a priority from the roadmap.

## Input Parameters
- **priority_id**: string (required) - Roadmap priority ID (e.g., "PRIORITY-25")
- **priority_name**: string (required) - Human-readable priority name
- **requirements**: object (required) - Detailed requirements from roadmap
- **complexity**: string (optional) - Complexity level (simple|medium|complex)
- **estimated_days**: number (optional) - Estimated implementation days

## Database Operations

### READ Operations
```sql
-- Read priority details from project manager's domain
SELECT * FROM pm_roadmap WHERE id = :priority_id;

-- Check for existing specs
SELECT * FROM arch_specs WHERE priority_id = :priority_id;

-- Check existing implementations to understand context
SELECT * FROM dev_implementations
WHERE priority_id = :priority_id
ORDER BY created_at DESC;
```

### WRITE Operations
```sql
-- Create main specification record
INSERT INTO arch_specs (
    id,
    priority_id,
    title,
    overview,
    status,
    complexity,
    estimated_days,
    created_at,
    created_by
) VALUES (
    :spec_id,
    :priority_id,
    :title,
    :overview,
    'draft',
    :complexity,
    :estimated_days,
    :timestamp,
    'architect'
);

-- Create specification sections (hierarchical)
INSERT INTO arch_spec_sections (
    spec_id,
    section_name,
    section_order,
    content,
    created_at
) VALUES
    (:spec_id, 'problem_statement', 1, :problem_content, :timestamp),
    (:spec_id, 'proposed_solution', 2, :solution_content, :timestamp),
    (:spec_id, 'technical_design', 3, :design_content, :timestamp),
    (:spec_id, 'implementation_plan', 4, :plan_content, :timestamp),
    (:spec_id, 'testing_strategy', 5, :testing_content, :timestamp),
    (:spec_id, 'definition_of_done', 6, :dod_content, :timestamp);
```

## Required Skills

### technical_specification_handling
- Generates structured technical specifications
- Ensures consistency with existing specs
- Validates completeness of requirements

### database_schema_guide
- Understands data model relationships
- Ensures proper foreign key constraints
- Validates data integrity

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to arch_specs domain

2. **Load Required Skills**
   ```python
   spec_skill = load_skill(SkillNames.TECHNICAL_SPECIFICATION_HANDLING)
   db_skill = load_skill(SkillNames.DATABASE_SCHEMA_GUIDE)
   ```

3. **Read Priority Information**
   - Query pm_roadmap for priority details
   - Validate priority exists and is in "Ready for Spec" status

4. **Check for Existing Spec**
   - Query arch_specs for existing specification
   - If exists, return error or update existing

5. **Analyze Requirements**
   - Parse requirements object
   - Identify technical constraints
   - Determine complexity and scope

6. **Generate Specification**
   - Create problem statement
   - Design technical solution
   - Plan implementation phases
   - Define testing strategy
   - Specify Definition of Done

7. **Store in Database**
   - Insert main spec record
   - Insert hierarchical sections
   - Create audit trail entry

8. **Notify Project Manager**
   ```python
   db.cross_domain_notify('project_manager', {
       'type': 'spec_created',
       'spec_id': spec_id,
       'priority_id': priority_id,
       'title': spec_title
   })
   ```

## Error Handling

### PermissionError
- **Cause**: Agent is not architect
- **Response**: Log error and return permission denied
- **Recovery**: None - only architect can create specs

### DuplicateSpecError
- **Cause**: Spec already exists for priority
- **Response**: Return existing spec ID
- **Recovery**: Suggest updating existing spec

### InvalidPriorityError
- **Cause**: Priority doesn't exist in roadmap
- **Response**: Return error with details
- **Recovery**: Notify project_manager to create priority

### IncompleteRequirementsError
- **Cause**: Missing required information
- **Response**: List missing fields
- **Recovery**: Request complete requirements

## Success Criteria
- [ ] Spec created with unique ID
- [ ] All sections populated with content
- [ ] Spec linked to priority in roadmap
- [ ] Project manager notified
- [ ] Audit trail entry created
- [ ] Spec status set to 'draft'

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Prepare spec data
spec_data = {
    'id': f'SPEC-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
    'priority_id': 'PRIORITY-25',
    'title': 'Authentication System Implementation',
    'overview': 'Implement secure user authentication with JWT tokens',
    'complexity': 'complex',
    'estimated_days': 5
}

# Create specification
spec_id = db.write('arch_specs', spec_data)

# Create sections
sections = [
    {
        'spec_id': spec_id,
        'section_name': 'problem_statement',
        'content': 'Users need secure authentication...',
        'section_order': 1
    },
    # ... more sections
]

for section in sections:
    db.write('arch_spec_sections', section)

# Notify project manager
db.cross_domain_notify('project_manager', {
    'type': 'spec_created',
    'spec_id': spec_id,
    'priority_id': 'PRIORITY-25'
})
```

## Metrics & Monitoring
- **Average spec creation time**: Track time from request to completion
- **Spec approval rate**: Percentage of specs approved without revision
- **Spec completeness score**: Measure how complete specs are
- **Revision count**: Track how many times specs are updated

## Related Commands
- `architect.update_spec` - Update existing specification
- `architect.approve_spec` - Move spec from draft to approved
- `architect.create_adr` - Create architectural decision record
- `architect.breakdown_tasks` - Create implementation tasks from spec
