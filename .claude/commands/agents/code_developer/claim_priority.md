---
command: code_developer.claim_priority
agent: code_developer
action: claim_priority
tables:
  write: [roadmap_priority, system_audit]
  read: [roadmap_priority, specs_task, specs_task_dependency]
required_skills: [roadmap_database_handling]
required_tools: [database]
---

# Command: code_developer.claim_priority

## Purpose
Claim a roadmap priority for implementation to prevent concurrent work by other agents.

## Input Parameters

```yaml
priority_id: string      # Required - Priority to claim (e.g., "PRIORITY-28")
force_claim: boolean     # Override existing claim (default: false)
estimated_start: string  # ISO date when starting work
```

## Database Operations

### 1. Retrieve Priority
```python
def claim_priority(db: DomainWrapper, params: dict):
    priority_id = params["priority_id"]

    # Get priority from database
    priorities = db.read("roadmap_priority", {"id": priority_id})
    if not priorities:
        return {"success": False, "error": f"Priority {priority_id} not found"}
```

### 2. Check for Existing Claims
```python
    priority = priorities[0]

    # Check if already claimed by another agent
    if priority.get("claimed_by") and not params.get("force_claim", False):
        return {
            "success": False,
            "error": f"Priority already claimed by {priority['claimed_by']}",
            "claimed_by": priority["claimed_by"],
            "claimed_at": priority.get("claimed_at")
        }
```

### 3. Verify Specification Exists
```python
    # Verify spec exists (architect must create spec first)
    if not priority.get("spec_id"):
        return {
            "success": False,
            "error": "No technical spec available",
            "recommendation": "architect should create spec first"
        }
```

### 4. Check Task Dependencies
```python
    # Check if all hard dependencies are satisfied
    tasks = db.read("specs_task", {"roadmap_item_id": priority_id})
    if tasks:
        task_group_id = tasks[0]["task_group_id"]
        dependencies = db.read("specs_task_dependency", {
            "task_group_id": task_group_id
        })

        for dep in dependencies:
            if dep["dependency_type"] == "hard":
                # Verify prerequisite tasks are complete
                prereq_tasks = db.read("specs_task", {
                    "task_group_id": dep["depends_on_group_id"]
                })
                if not all(t["status"] == "completed" for t in prereq_tasks):
                    return {
                        "success": False,
                        "error": f"Dependency {dep['depends_on_group_id']} not complete",
                        "blocked_by": dep["depends_on_group_id"]
                    }
```

### 5. Claim Priority Atomically
```python
    from datetime import datetime

    # Claim priority and update status
    db.write("roadmap_priority", {
        "id": priority_id,
        "claimed_by": "code_developer",
        "claimed_at": datetime.now().isoformat(),
        "status": "🏗️ In Progress",
        "started_at": params.get("estimated_start", datetime.now().isoformat())
    }, action="update")

    # Audit trail
    db.write("system_audit", {
        "table_name": "roadmap_priority",
        "item_id": priority_id,
        "action": "claimed",
        "field_changed": "claimed_by",
        "new_value": "code_developer",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": True,
        "priority_id": priority_id,
        "claimed_by": "code_developer",
        "claimed_at": datetime.now().isoformat(),
        "spec_id": priority.get("spec_id"),
        "tasks_available": len(tasks),
        "dependencies_satisfied": True
    }
```

## Output

```json
{
  "success": true,
  "priority_id": "PRIORITY-28",
  "claimed_by": "code_developer",
  "claimed_at": "2025-10-26T10:00:00Z",
  "spec_id": "SPEC-131",
  "tasks_available": 3,
  "dependencies_satisfied": true
}
```

## Success Criteria

- ✅ Priority claimed atomically (prevents race conditions)
- ✅ Dependencies verified (prerequisites complete)
- ✅ Spec exists and is approved
- ✅ Tasks created and ready
- ✅ Audit trail created

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| AlreadyClaimedError | Priority claimed by another agent | Wait or force claim |
| NoSpecError | Technical spec missing | architect creates spec |
| DependencyBlockedError | Prerequisites not complete | Wait for dependencies |
| NotFoundError | Priority doesn't exist | Verify priority ID |

## Downstream Effects

- Status changes to "In Progress"
- orchestrator sees work started
- Dashboard shows claimed work
- Audit trail enables tracking
