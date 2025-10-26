---
command: architect.create_implementation_tasks
agent: architect
action: create_implementation_tasks
data_domain: dev_implementations
write_tables: [dev_implementations, dev_implementation_tasks, dev_task_assignments]
read_tables: [arch_specs, arch_spec_sections]
required_skills: [technical_specification_handling]
---

# Command: architect.create_implementation_tasks

## Purpose
Break a technical specification into atomic implementation tasks with scope, assigned files, and dependencies.

## Input Parameters
- **spec_id**: string (required) - Specification to decompose (e.g., "SPEC-131")
- **priority_number**: integer (required) - Priority number for task group (e.g., 31)
- **granularity**: string (optional, default: "phase") - "phase", "section", or "module"
- **assign_files**: boolean (optional, default: true) - Auto-assign files to tasks

## Database Operations

### READ Operations
```sql
-- Get specification
SELECT * FROM arch_specs WHERE id = :spec_id;

-- Get specification sections
SELECT section_name, content, section_order
FROM arch_spec_sections
WHERE spec_id = :spec_id
ORDER BY section_order;

-- Check existing tasks for this spec
SELECT COUNT(*) FROM dev_implementation_tasks
WHERE spec_id = :spec_id;
```

### WRITE Operations
```sql
-- Create implementation group record
INSERT INTO dev_implementations (
    id, spec_id, priority_number, task_group_id,
    granularity, total_tasks, status, created_by, created_at
) VALUES (
    :impl_id, :spec_id, :priority_number, :task_group_id,
    :granularity, :total_tasks, 'pending', 'architect', :timestamp
);

-- Create implementation tasks
INSERT INTO dev_implementation_tasks (
    id, spec_id, task_group_id, scope_description,
    spec_sections, assigned_files, estimated_hours,
    priority_order, status, created_by, created_at
) VALUES (
    :task_id, :spec_id, :task_group_id, :scope,
    :sections_json, :files_json, :hours,
    :order, 'pending', 'architect', :timestamp
);

-- Create file assignments
INSERT INTO dev_task_assignments (
    task_id, file_path, purpose, conflict_checked, created_by
) VALUES (
    :task_id, :file_path, :purpose, true, 'architect'
);
```

## Required Skills

### technical_specification_handling
- Decomposes spec sections into tasks
- Determines file ownership per task
- Calculates task estimates from spec

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to dev_implementations domain

2. **Load Required Skills**
   ```python
   spec_skill = load_skill(SkillNames.TECHNICAL_SPECIFICATION_HANDLING)
   ```

3. **Fetch Specification**
   - Query arch_specs for spec_id
   - If not found, return SpecNotFoundError
   - Get estimated_days from spec

4. **Fetch Specification Sections**
   - Query arch_spec_sections for all sections
   - Organize by section_order

5. **Decompose into Tasks** (based on granularity)

   **phase granularity**: One task per major phase
   - Implementation tasks based on features/phases described in spec
   - Example: "Phase 1: Database Schema", "Phase 2: API Endpoints"

   **section granularity**: One task per spec section
   - problem_statement → TASK-31-1: Understand requirements
   - technical_design → TASK-31-2: Implement core design
   - implementation_plan → TASK-31-3: Implementation
   - testing_strategy → TASK-31-4: Testing

   **module granularity**: Fine-grained tasks per module
   - Identify modules in technical_design
   - Create task per module with dependencies

6. **Assign Files to Tasks** (if assign_files=true)
   - Parse implementation_plan for file references
   - Identify modules and their file locations
   - Assign files to tasks ensuring no conflicts
   - Check for file overlap (error if found)
   - Record assignment purpose (new|modify|test)

7. **Calculate Task Estimates**
   - Distribute spec.estimated_days across tasks
   - Base on complexity and scope_description
   - Each task gets estimated_hours value

8. **Create Task Group Record**
   - task_group_id = f"GROUP-{priority_number}"
   - Record total task count
   - Set status to pending

9. **Create Task Records**
   - Create dev_implementation_tasks entries
   - task_id = f"TASK-{priority_number}-{task_order}"
   - spec_sections = list of relevant section names (JSON)
   - assigned_files = list of file paths (JSON)
   - priority_order = task order within group

10. **Create File Assignments**
    - Create dev_task_assignments records
    - One per file per task
    - Record purpose (new, modify, test)
    - Mark conflict_checked=true

11. **Return Task Creation Results**
    - Total tasks created
    - Task group ID
    - List of task IDs with scope

## Error Handling

### SpecNotFoundError
- **Cause**: Specification doesn't exist
- **Response**: Return error with spec_id
- **Recovery**: Verify spec_id is correct

### FileConflictError
- **Cause**: Tasks would overlap on same files
- **Response**: Return error with conflicting files and tasks
- **Recovery**: Adjust granularity or split differently

### InvalidGranularityError
- **Cause**: Unknown granularity type
- **Response**: Return error with valid options
- **Recovery**: Use "phase", "section", or "module"

### TasksAlreadyExistError
- **Cause**: Tasks already created for this spec
- **Response**: Return error with existing task group
- **Recovery**: Delete existing tasks or use different spec

## Success Criteria
- [ ] Tasks created with unique IDs
- [ ] Task group assigned (GROUP-{priority_number})
- [ ] Spec sections mapped to tasks
- [ ] Files assigned without conflicts
- [ ] Priority order set correctly
- [ ] Estimated hours distributed

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Create implementation tasks
result = db.execute_command('architect.create_implementation_tasks', {
    'spec_id': 'SPEC-131',
    'priority_number': 31,
    'granularity': 'phase',
    'assign_files': True
})

# Returns
{
    'success': True,
    'spec_id': 'SPEC-131',
    'tasks_created': 3,
    'task_group_id': 'GROUP-31',
    'tasks': [
        {
            'task_id': 'TASK-31-1',
            'scope_description': 'Phase 1: Database Schema',
            'spec_sections': ['technical_design'],
            'assigned_files': ['coffee_maker/models/user.py'],
            'estimated_hours': 8.0
        },
        {
            'task_id': 'TASK-31-2',
            'scope_description': 'Phase 2: API Endpoints',
            'spec_sections': ['implementation_plan'],
            'assigned_files': ['coffee_maker/api/endpoints.py'],
            'estimated_hours': 10.0
        },
        {
            'task_id': 'TASK-31-3',
            'scope_description': 'Phase 3: Testing',
            'spec_sections': ['testing_strategy'],
            'assigned_files': ['tests/test_api.py'],
            'estimated_hours': 6.0
        }
    ]
}
```

## Output Format

```json
{
  "success": true,
  "spec_id": "SPEC-131",
  "tasks_created": 3,
  "task_group_id": "GROUP-31",
  "total_estimated_hours": 24.0,
  "granularity": "phase",
  "tasks": [
    {
      "task_id": "TASK-31-1",
      "scope_description": "Phase 1: Database Schema",
      "spec_sections": ["technical_design"],
      "assigned_files": ["coffee_maker/models/user.py"],
      "estimated_hours": 8.0,
      "priority_order": 1
    }
  ]
}
```

## Granularity Strategies

### Phase-Based (default)
- Best for: Specs with clear phases
- Example: Database → API → Frontend
- Pros: Large, meaningful units; easy to track progress
- Cons: Less parallelizable

### Section-Based
- Best for: Specs with clear sections
- Example: Per spec section (design, impl, testing)
- Pros: Natural breakpoints; good for code review
- Cons: May create dependent tasks

### Module-Based
- Best for: Complex specs with multiple modules
- Example: Auth module, User module, Admin module
- Pros: Maximum parallelization
- Cons: May create many tasks

## Related Commands
- `architect.define_task_dependencies` - Add dependencies between tasks
- `architect.update_task_status` - Update task progress
- `code_developer.claim_work` - Developer claims task
