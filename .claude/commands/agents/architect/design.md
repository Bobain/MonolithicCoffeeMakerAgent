# design

## Purpose
Create comprehensive technical specification from priority: analyze requirements, define architecture, identify dependencies, generate tasks.

## Parameters
```yaml
priority_id: str  # Required, format: PRIORITY-N
complexity: str = "auto"  # "auto" | "simple" | "moderate" | "complex"
require_poc: bool = false  # Force POC creation regardless of complexity
notify_project_manager: bool = true  # Notify when spec ready
```

## Workflow
1. Load priority from database
2. Analyze requirements and estimate complexity
3. Check dependency approval (SPEC-070)
4. Determine if POC required (>2 days OR high complexity)
5. Design architecture and data models
6. Generate task breakdown
7. Create technical spec document
8. Insert into database
9. Notify project_manager if enabled
10. Return DesignResult

## Database Operations
```sql
-- Get priority details
SELECT priority_id, title, description, metadata
FROM roadmap_priority
WHERE priority_id = ?

-- Insert technical spec
INSERT INTO technical_spec (
    spec_id, priority_id, title, complexity_score,
    architecture, dependencies, task_breakdown,
    requires_poc, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))

-- Generate tasks
INSERT INTO specs_task (
    task_id, spec_id, priority_id, description,
    estimated_hours, dependencies, status, created_at
) VALUES (?, ?, ?, ?, ?, ?, 'pending', datetime('now'))
```

## Result Object
```python
@dataclass
class DesignResult:
    spec_id: str  # Format: SPEC-NNN
    priority_id: str
    complexity_score: int  # 1-10
    tasks_generated: int
    requires_poc: bool
    dependencies_approved: bool
    status: str  # "success" | "blocked" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| PriorityNotFound | Invalid priority_id | Verify priority exists |
| DependencyNotApproved | Unapproved dependency | Run check-dependency CLI |
| SpecGenerationFailed | Requirements unclear | Request clarification |
| DatabaseError | Insert failed | Retry with backoff |

## Example
```python
result = design(priority_id="PRIORITY-8", complexity="auto")
# DesignResult(
#   spec_id="SPEC-042",
#   priority_id="PRIORITY-8",
#   complexity_score=7,
#   tasks_generated=5,
#   requires_poc=True,
#   dependencies_approved=True,
#   status="success"
# )
```

## Related Commands
- poc() - Create POC for complex specs
- adr() - Document architectural decisions

---
Estimated: 70 lines | Context: ~4.5% | Examples: design_examples.md
