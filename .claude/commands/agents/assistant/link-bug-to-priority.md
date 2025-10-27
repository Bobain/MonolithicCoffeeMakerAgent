---
command: link-bug-to-priority
agent: assistant
action: link_bug_to_priority
tables: [ui_bug_reports, roadmap_priority]
tools: []
duration: 5m
---

## Purpose

Associate bug with roadmap priority for tracking and impact analysis.

## Input Parameters

```yaml
BUG_ID:
  type: string
  description: Bug identifier
  example: "BUG-087"

PRIORITY_ID:
  type: string
  description: Roadmap priority identifier
  example: "PRIORITY-28"
```

## Database Operations

### UPDATE ui_bug_reports

```sql
UPDATE ui_bug_reports
SET priority_id = ?
WHERE bug_id = ?
```

### SELECT roadmap_priority

```sql
SELECT id, name FROM roadmap_priority WHERE id = ?
```

## Success Criteria

- Bug exists in database
- Priority exists in roadmap
- Link created successfully
- Audit trail created

## Output Format

```json
{
  "success": true,
  "bug_id": "BUG-087",
  "priority_id": "PRIORITY-28",
  "priority_name": "User Authentication",
  "message": "Bug successfully linked to priority"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Bug not found | Invalid BUG_ID | Return 404 |
| Priority not found | PRIORITY_ID doesn't exist | List valid priorities |
| Already linked | Bug already has priority_id | Return current link |

## Examples

### Example 1: Link to Priority

```bash
/agents:assistant:link-bug-to-priority \
  BUG_ID="BUG-087" \
  PRIORITY_ID="PRIORITY-28"
```

### Example 2: Verify Link

```bash
/agents:assistant:link-bug-to-priority \
  BUG_ID="BUG-087" \
  PRIORITY_ID="PRIORITY-28"
```

## Implementation Notes

- Validate both bug_id and priority_id exist before linking
- One bug can link to one priority
- Null priority_id is allowed (unlinked bugs)
- Create audit trail entry for the link
- Query roadmap_priority table to verify priority exists
