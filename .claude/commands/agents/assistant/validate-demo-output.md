---
command: validate-demo-output
agent: assistant
action: validate_demo_results
tables: [ui_demo_sessions]
tools: [file_system]
duration: 10m
---

## Purpose

Verify demo results meet acceptance criteria and mark session as completed or failed.

## Input Parameters

```yaml
SESSION_ID:
  type: string
  description: Demo session identifier
  example: "DEMO-20251027-abc123"

CRITERIA:
  type: array
  description: Validation criteria to check
  items:
    type: object
    properties:
      check_type: string (screenshots_exist|steps_completed|no_errors|file_paths_valid)
      expected_count: integer
      required: boolean

MARK_COMPLETE:
  type: boolean
  optional: true
  default: true
  description: Update session status to completed if all criteria pass
```

## Database Operations

### UPDATE ui_demo_sessions

```sql
UPDATE ui_demo_sessions
SET status = ?, metadata = json_set(metadata, '$.validation_results', ?)
WHERE session_id = ?
```

## Success Criteria

- All criteria validated
- Status updated to "completed" or "failed"
- Validation report generated
- Files archived (if applicable)

## Output Format

```json
{
  "success": true,
  "session_id": "DEMO-20251027-abc123",
  "validation_results": [
    {"check": "screenshots_exist", "expected": 5, "actual": 5, "passed": true},
    {"check": "steps_completed", "expected": 5, "actual": 5, "passed": true},
    {"check": "no_errors", "passed": true},
    {"check": "file_paths_valid", "passed": true}
  ],
  "overall_status": "completed",
  "validation_report": "All criteria passed. Demo ready for review.",
  "demo_url": "http://localhost:8501/demos/DEMO-20251027-abc123"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Session not found | Invalid SESSION_ID | Return 404 |
| Invalid criteria | Unknown check_type | List valid types |
| Validation failed | Criteria not met | Log details, suggest fixes |
| File access error | Missing files | Check directory structure |

## Examples

### Example 1: Validate Roadmap Demo

```bash
/agents:assistant:validate-demo-output \
  SESSION_ID="DEMO-20251027-abc123" \
  CRITERIA='[
    {"check_type": "screenshots_exist", "expected_count": 5, "required": true},
    {"check_type": "steps_completed", "expected_count": 5, "required": true},
    {"check_type": "no_errors", "required": true}
  ]' \
  MARK_COMPLETE=true
```

## Implementation Notes

- Check types validate different aspects of demo
- screenshots_exist: Verify expected number of PNG files
- steps_completed: Verify metadata.steps array length
- no_errors: Check for exceptions in metadata
- file_paths_valid: Verify all paths are readable
- If all criteria pass and MARK_COMPLETE=true, set status='completed'
- If any required criterion fails, set status='failed'
- Archive demo data for long-term storage
