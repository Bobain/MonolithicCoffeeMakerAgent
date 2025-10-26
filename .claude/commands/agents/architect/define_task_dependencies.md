---
command: architect.define_task_dependencies
agent: architect
action: define_task_dependencies
data_domain: dev_implementations
write_tables: [dev_task_dependencies]
read_tables: [dev_implementation_tasks]
required_skills: []
---

# Command: architect.define_task_dependencies

## Purpose
Define dependencies between task groups (hard/soft) to enforce execution order and manage parallel work.

## Input Parameters
- **task_group_id**: string (required) - Task group that depends on another (e.g., "GROUP-31")
- **depends_on_group_id**: string (required) - Prerequisite task group (e.g., "GROUP-30")
- **dependency_type**: string (required) - "hard" (blocking) or "soft" (recommended)
- **reason**: string (optional) - Explanation for dependency

## Database Operations

### READ Operations
```sql
-- Verify task group exists
SELECT * FROM dev_implementations WHERE task_group_id = :task_group_id;

-- Verify dependency target exists
SELECT * FROM dev_implementations WHERE task_group_id = :depends_on_group_id;

-- Check for circular dependencies
-- (Would need graph traversal - see error handling)
```

### WRITE Operations
```sql
-- Create dependency record
INSERT INTO dev_task_dependencies (
    id, task_group_id, depends_on_group_id,
    dependency_type, reason,
    created_by, created_at
) VALUES (
    :dep_id, :task_group_id, :depends_on_group_id,
    :dependency_type, :reason,
    'architect', :timestamp
);
```

## Execution Steps

1. **Validate Permissions**
   - Verify agent is architect
   - Check write access to dev_implementations domain

2. **Verify Task Groups Exist**
   - Query dev_implementations for task_group_id
   - If not found, return TaskGroupNotFoundError
   - Query dev_implementations for depends_on_group_id
   - If not found, return DependencyTargetNotFoundError

3. **Validate Dependency Type**
   - Ensure dependency_type is "hard" or "soft"
   - If invalid, return InvalidDependencyTypeError

4. **Check for Circular Dependencies**
   - Build dependency graph from existing dependencies
   - Traverse graph to check if adding this edge creates cycle
   - If cycle detected, return CircularDependencyError

5. **Check for Duplicate Dependencies**
   - Query dev_task_dependencies for existing link
   - If exact dependency already exists, return DuplicateDependencyError

6. **Create Dependency Record**
   - Insert into dev_task_dependencies table
   - Record task_group_id, depends_on_group_id, type, reason
   - Set created_by='architect', created_at=now()

7. **Generate Dependency ID**
   - Create unique dep_id for tracking
   - Example: dep-{timestamp}-{hash}

8. **Return Dependency Results**
   - Confirm creation
   - Return dependency ID
   - Return full dependency details

## Error Handling

### TaskGroupNotFoundError
- **Cause**: Task group doesn't exist
- **Response**: Return error with task_group_id
- **Recovery**: Verify task_group_id matches GROUP-{priority_number}

### DependencyTargetNotFoundError
- **Cause**: Dependency target group doesn't exist
- **Response**: Return error with depends_on_group_id
- **Recovery**: Create dependency target group first

### CircularDependencyError
- **Cause**: Adding this dependency would create cycle
- **Response**: Return error with cycle path
- **Recovery**: Re-order task groups or create separate chains

### DuplicateDependencyError
- **Cause**: Dependency already exists
- **Response**: Return existing dependency details
- **Recovery**: Use different dependency or update existing

### InvalidDependencyTypeError
- **Cause**: dependency_type is not "hard" or "soft"
- **Response**: Return error with valid options
- **Recovery**: Use "hard" for blocking or "soft" for recommended

## Success Criteria
- [ ] Dependency created in database
- [ ] Dependency type recorded
- [ ] Reason documented
- [ ] No circular dependencies created
- [ ] Dependency ID returned

## Example Usage

```python
from coffee_maker.database.domain_access import DomainDatabase, AgentType

# Initialize database for architect
db = DomainDatabase(AgentType.ARCHITECT)

# Define task dependency
result = db.execute_command('architect.define_task_dependencies', {
    'task_group_id': 'GROUP-31',
    'depends_on_group_id': 'GROUP-30',
    'dependency_type': 'hard',
    'reason': 'GROUP-31 requires database schema from GROUP-30'
})

# Returns
{
    'success': True,
    'task_group_id': 'GROUP-31',
    'depends_on_group_id': 'GROUP-30',
    'dependency_type': 'hard',
    'dependency_id': 'dep-20251026-abc123'
}
```

## Output Format

```json
{
  "success": true,
  "task_group_id": "GROUP-31",
  "depends_on_group_id": "GROUP-30",
  "dependency_type": "hard",
  "dependency_id": "dep-20251026-abc123",
  "created_at": "2025-10-26T12:34:56Z"
}
```

## Dependency Types

### Hard Dependencies
- **Semantics**: Task must complete before dependent starts
- **Blocking**: Yes - blocks dependent group
- **Use Case**: Database schema before API endpoints
- **Enforcement**: orchestrator will not start dependent group

### Soft Dependencies
- **Semantics**: Task should ideally complete first, but not required
- **Blocking**: No - dependent can start in parallel
- **Use Case**: Documentation before implementation
- **Enforcement**: orchestrator logs warning if not respected

## Dependency Management for orchestrator

The orchestrator will:
1. Load all task groups
2. Build dependency graph from dev_task_dependencies
3. For hard dependencies: enforce sequential execution
4. For soft dependencies: allow parallel execution with warnings
5. Detect cycles and fail early (prevent deadlock)

## Example Dependency Graph

```
GROUP-30 (Database)
  └─> GROUP-31 (API) [hard]
      └─> GROUP-32 (Frontend) [hard]
          └─> GROUP-33 (Integration Tests) [hard]

GROUP-34 (Documentation) [soft dependency on GROUP-32]
GROUP-35 (DevOps) [soft dependency on all above]
```

## Circular Dependency Detection Algorithm

```python
def has_cycle(graph, new_edge):
    """Check if adding new_edge creates cycle using DFS"""
    source, target = new_edge
    graph = graph + [new_edge]

    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    return dfs(source)
```

## Related Commands
- `architect.create_implementation_tasks` - Create task groups
- `architect.update_task_status` - Monitor task progress
- `orchestrator.execute_task_group` - Execute task respecting dependencies
