# poc

## Purpose
Manage POC lifecycle: create structure, track implementation, evaluate results, decide on integration or abandonment.

## Parameters
```yaml
spec_id: str  # Required if action="create", format: SPEC-NNN
action: str  # Required: "create" | "evaluate" | "integrate" | "abandon"
poc_id: str = None  # Required for evaluate/integrate/abandon
evaluation_criteria: dict = None  # Custom criteria for evaluation
```

## Workflow
1. Load spec and determine POC requirements
2. Execute action:
   - **create**: Generate POC structure in docs/architecture/pocs/
   - **evaluate**: Run tests, check criteria, generate report
   - **integrate**: Move POC code to main codebase
   - **abandon**: Archive POC with lessons learned
3. Update database with POC status
4. Return PocResult

## Database Operations
```sql
-- Insert POC record
INSERT INTO poc_tracker (
    poc_id, spec_id, title, status, created_at,
    evaluation_criteria, conclusion
) VALUES (?, ?, ?, 'in_progress', datetime('now'), ?, NULL)

-- Update POC status
UPDATE poc_tracker
SET status = ?, conclusion = ?, completed_at = datetime('now')
WHERE poc_id = ?

-- Link POC to spec
UPDATE technical_spec
SET poc_id = ?, poc_status = ?
WHERE spec_id = ?
```

## Result Object
```python
@dataclass
class PocResult:
    poc_id: str  # Format: POC-NNN
    action: str
    status: str  # "created" | "passed" | "failed" | "integrated" | "abandoned"
    poc_path: str  # docs/architecture/pocs/POC-NNN-{slug}/
    evaluation_score: int  # 0-100, None if action="create"
    recommendation: str  # "integrate" | "abandon" | "revise"
```

## POC Directory Structure
```
docs/architecture/pocs/POC-{number}-{slug}/
├── README.md           # Overview and goals
├── implementation/     # POC code
├── tests/             # POC tests
├── EVALUATION.md      # Results and metrics
└── LESSONS.md         # Learnings
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| SpecNotFound | Invalid spec_id | Verify spec exists |
| PocNotFound | Invalid poc_id | Check POC ID |
| EvaluationFailed | Tests broken | Review POC implementation |
| IntegrationConflict | Code conflicts | Resolve conflicts manually |

## Example
```python
result = poc(spec_id="SPEC-042", action="create")
# PocResult(
#   poc_id="POC-015",
#   action="created",
#   status="created",
#   poc_path="docs/architecture/pocs/POC-015-oauth2-flow/",
#   evaluation_score=None,
#   recommendation="test_and_evaluate"
# )
```

## Related Commands
- design() - Creates specs that may require POCs
- adr() - Document POC decisions

---
Estimated: 60 lines | Context: ~4% | Examples: poc_examples.md
