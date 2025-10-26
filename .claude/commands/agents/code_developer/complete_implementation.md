---
command: code_developer.complete_implementation
agent: code_developer
action: complete_implementation
tables:
  write: [specs_task, roadmap_priority, system_audit, notifications]
  read: [specs_task, roadmap_priority]
required_skills: [roadmap_database_handling]
required_tools: [database, pytest]
---

# Command: code_developer.complete_implementation

## Purpose
Mark implementation complete and trigger verification (tests, coverage, review).

## Input Parameters

```yaml
task_id: string          # Required - Task completed
priority_id: string      # Required - Associated priority
run_tests: boolean       # Run tests before marking complete (default: true)
request_review: boolean  # Trigger code review (default: true)
```

## Database Operations

### 1. Run Tests (Optional)
```python
from datetime import datetime
import json
import subprocess

def complete_implementation(db: DomainWrapper, params: dict):
    task_id = params["task_id"]
    priority_id = params["priority_id"]

    # Run tests if requested
    tests_passed = True
    coverage = 0
    test_output = ""

    if params.get("run_tests", True):
        # Execute pytest with coverage
        result = subprocess.run(
            ["pytest", "--cov=coffee_maker", "--cov-report=json", "-v"],
            capture_output=True,
            text=True
        )
        tests_passed = result.returncode == 0
        test_output = result.stderr + result.stdout

        # Parse coverage from JSON report
        try:
            import os
            if os.path.exists("coverage.json"):
                with open("coverage.json") as f:
                    cov_data = json.load(f)
                    coverage = round(cov_data["totals"]["percent_covered"], 2)
        except Exception as e:
            coverage = 0
            test_output += f"\nFailed to parse coverage: {e}"

        # Check if tests passed
        if not tests_passed:
            return {
                "success": False,
                "error": "Tests failed",
                "test_output": test_output[:1000],  # Truncate for DB
                "coverage": coverage
            }

        # Check coverage threshold (90%)
        if coverage < 90:
            return {
                "success": False,
                "error": f"Coverage too low: {coverage}% (need 90%)",
                "coverage": coverage,
                "test_output": test_output[:1000]
            }
```

### 2. Mark Task Complete
```python
    # Mark task as completed
    db.write("specs_task", {
        "id": task_id,
        "status": "completed",
        "completed_at": datetime.now().isoformat()
    }, action="update")
```

### 3. Update Priority Status
```python
    # Update priority to complete
    db.write("roadmap_priority", {
        "id": priority_id,
        "status": "✅ Complete",
        "completed_at": datetime.now().isoformat()
    }, action="update")
```

### 4. Audit Trail
```python
    # Create audit records
    db.write("system_audit", {
        "table_name": "specs_task",
        "item_id": task_id,
        "action": "completed",
        "field_changed": "status",
        "new_value": "completed",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    db.write("system_audit", {
        "table_name": "roadmap_priority",
        "item_id": priority_id,
        "action": "completed",
        "field_changed": "status",
        "new_value": "✅ Complete",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")
```

### 5. Request Code Review
```python
    # Request code review if enabled
    review_requested = False
    if params.get("request_review", True):
        db.send_notification("code_reviewer", {
            "type": "implementation_complete",
            "task_id": task_id,
            "priority_id": priority_id,
            "tests_passed": tests_passed,
            "coverage": coverage,
            "message": f"Implementation complete for {task_id}, please review",
            "priority": "high"
        })
        review_requested = True
```

### 6. Notify Architect
```python
    # Notify architect for merge decision
    db.send_notification("architect", {
        "type": "task_complete",
        "task_id": task_id,
        "priority_id": priority_id,
        "tests_passed": tests_passed,
        "coverage": coverage,
        "message": f"Task {task_id} complete with {coverage}% coverage, ready for merge",
        "priority": "high"
    })

    return {
        "success": True,
        "task_id": task_id,
        "priority_id": priority_id,
        "tests_passed": tests_passed,
        "coverage": coverage,
        "review_requested": review_requested,
        "notification_sent": True
    }
```

## Output

```json
{
  "success": true,
  "task_id": "TASK-31-1",
  "priority_id": "PRIORITY-28",
  "tests_passed": true,
  "coverage": 92,
  "review_requested": true,
  "notification_sent": true
}
```

## Success Criteria

- ✅ Task marked completed
- ✅ Tests run and pass
- ✅ Coverage ≥90%
- ✅ Code review triggered
- ✅ Notifications sent (architect, code_reviewer)
- ✅ Priority marked complete
- ✅ Audit trails created

## Quality Gates

| Gate | Requirement | Action If Failed |
|------|-------------|-----------------|
| Tests | All tests must pass | Return error, don't mark complete |
| Coverage | ≥90% coverage required | Return error, don't mark complete |
| Review | Code review requested | Notify code_reviewer and architect |

## Completion Workflow

```
1. Run tests (if enabled)
   ├─ All tests pass? → Continue
   └─ Tests fail? → Return error
2. Check coverage (if tests enabled)
   ├─ Coverage ≥90%? → Continue
   └─ Coverage <90%? → Return error
3. Mark task complete in database
4. Update priority to "✅ Complete"
5. Request code review (if enabled)
6. Notify architect
7. Return success
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| TestFailureError | Tests failed | Fix tests, try again |
| LowCoverageError | Coverage <90% | Add more tests |
| TaskNotFoundError | Task doesn't exist | Verify task ID |
| DatabaseError | Write failed | Check database |

## Integration with Other Agents

After `complete_implementation`:
- **code_reviewer** detects implementation_complete notification
- **code_reviewer** analyzes all commits for the task
- **architect** receives notification for merge decision
- **orchestrator** sees task complete and moves to next task

## Skipping Tests (Not Recommended)

```python
# Only skip tests for debugging/emergency fixes
complete_implementation(db, {
    "task_id": "TASK-31-1",
    "priority_id": "PRIORITY-28",
    "run_tests": False  # Not recommended!
})
```

WARNING: Skipping tests bypasses quality gates and should only be used in exceptional circumstances.
