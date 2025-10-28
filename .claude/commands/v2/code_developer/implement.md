# implement

## Purpose
Implement a task from technical specification: load spec from database, generate/modify code files, track all changes.

## Parameters
```yaml
task_id: str  # Required, format: TASK-N-M
auto_test: bool = true  # Run tests after implementation
verbose: bool = false  # Enable detailed logging
```

## Workflow
1. Load task and linked spec from database
2. Analyze spec requirements and complexity
3. Generate or modify code files
4. Track all file changes (create, update, delete)
5. Return ImplementResult with status and metadata

## Database Query
```sql
-- Load task with spec
SELECT
    st.task_id, st.spec_id, st.description, st.status,
    ts.title as spec_title, ts.dependencies, ts.complexity_score,
    ts.file_path as spec_file, ts.metadata as spec_metadata
FROM specs_task st
JOIN technical_spec ts ON st.spec_id = ts.spec_id
WHERE st.task_id = ?
```

## Result Object
```python
@dataclass
class ImplementResult:
    files_changed: List[str]  # Files created/modified
    spec_id: str  # Linked specification
    task_id: str
    status: str  # "success" | "partial" | "failed"
    metadata: dict  # {complexity, lines_added, lines_removed}
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| TaskNotFound | Invalid task_id | Verify task exists in specs_task table |
| SpecNotFound | Spec missing for task | Check spec_id link, notify architect |
| CodeGenError | Unable to generate code | Review spec clarity, check dependencies |
| FileWriteError | Permission/path issue | Check file permissions, verify paths |

## Example
```python
result = implement(task_id="TASK-42-1")
# ImplementResult(
#   files_changed=["coffee_maker/auth.py", "tests/unit/test_auth.py"],
#   spec_id="SPEC-100",
#   task_id="TASK-42-1",
#   status="success",
#   metadata={"complexity": 6, "lines_added": 145, "lines_removed": 0}
# )
```

## Database Connection
Use connection pooling: `with get_connection() as conn:`

## Related Commands
- test() - Validate implementation with pytest
- finalize() - Quality checks and commit

---
Estimated: 60 lines | Context: ~4% | Examples: implement_examples.md
