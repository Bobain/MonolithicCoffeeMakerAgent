---
command: code_reviewer.detect_new_commits
agent: code_reviewer
action: detect_new_commits
tables:
  write: [review_code_review]
  read: [review_commit, roadmap_priority]
required_tools: []
estimated_duration_seconds: 10
---

# Command: code_reviewer.detect_new_commits

## Purpose

Poll the review_commit table for unreviewed commits and identify which are ready for immediate review. This command runs periodically to detect new work from code_developer that needs quality assurance.

## Input Parameters

```yaml
max_age_minutes: integer        # Only consider commits <X minutes old (default: 60)
priority_filter: string         # Optional - review only commits for this priority
batch_size: integer             # Max commits to return per run (default: 5)
skip_draft_commits: boolean     # Skip commits marked as WIP (default: true)
```

## Database Operations

**Query 1: Find unreviewed commits**
```sql
SELECT rc.*, rp.title as priority_title, rp.scope_description
FROM review_commit rc
LEFT JOIN roadmap_priority rp ON rc.priority_id = rp.id
WHERE rc.reviewed_at IS NULL
  AND rc.created_at > datetime('now', '-' || ? || ' minutes')
  AND (? IS NULL OR rc.priority_id = ?)
  AND (? = FALSE OR rc.commit_message NOT LIKE 'WIP:%')
ORDER BY rc.created_at DESC
LIMIT ?;
```

**Query 2: Check for blocking reviews**
```sql
SELECT COUNT(*) as block_count
FROM review_code_review rcr
WHERE rcr.commit_sha = ?
  AND rcr.status IN ('reviewing', 'needs_changes', 'pending')
  AND rcr.completed_at IS NULL;
```

**Query 3: Create review tracking entry**
```sql
INSERT INTO review_code_review (
    id, commit_sha, review_date, status, started_at
) VALUES (
    ?, ?, datetime('now'), 'pending', datetime('now')
);
```

## External Tools

No external tools required. This is a pure database polling operation.

## Success Criteria

- ✅ Finds all unreviewed commits created within max_age_minutes
- ✅ Filters by priority if priority_filter provided
- ✅ Skips commits with blocking reviews
- ✅ Creates review_code_review entry for each ready commit
- ✅ Returns batch-sized result set (default 5)
- ✅ Provides skip reasons for filtered commits
- ✅ Completes in <10 seconds even with 100+ commits

## Output Format

```json
{
  "status": "success",
  "commits_found": 3,
  "commits_ready": 2,
  "commits_skipped": 1,
  "batch_size": 5,
  "skip_reasons": [
    {
      "commit_sha": "abc123def456",
      "reason": "Blocked by review REV-123 (reviewing)"
    }
  ],
  "ready_commits": [
    {
      "commit_sha": "def456ghi789",
      "created_at": "2025-10-26T10:30:45Z",
      "priority_id": "US-104",
      "message": "feat: Add authentication",
      "author": "code_developer",
      "files_changed": 5
    }
  ],
  "timestamp": "2025-10-26T10:35:22Z"
}
```

## Error Handling

**Database Connection Error**:
```json
{
  "status": "error",
  "error_type": "DATABASE_CONNECTION_FAILED",
  "message": "Cannot connect to review_commit table",
  "recovery": "Retry in 30 seconds"
}
```

**Invalid Parameters**:
```json
{
  "status": "error",
  "error_type": "INVALID_PARAMETER",
  "message": "max_age_minutes must be positive integer",
  "provided_value": -5
}
```

## Examples

### Example 1: Poll for any new commits

```bash
code_reviewer.detect_new_commits(
  max_age_minutes=60,
  batch_size=5
)
```

**Response**:
```json
{
  "status": "success",
  "commits_found": 2,
  "commits_ready": 2,
  "commits_skipped": 0
}
```

### Example 2: Poll with priority filter

```bash
code_reviewer.detect_new_commits(
  max_age_minutes=120,
  priority_filter="US-104",
  batch_size=3
)
```

### Example 3: Skip WIP commits

```bash
code_reviewer.detect_new_commits(
  max_age_minutes=60,
  skip_draft_commits=true,
  batch_size=10
)
```

## Implementation Notes

- Run this command every 5 minutes during development
- Respects CFR-013 (git workflow) - works with roadmap branch
- IDs should be generated as `REV-{timestamp}-{commit_sha[:8]}`
- Check commit age to avoid reviewing stale commits
- Blocking reviews prevent duplicate analysis

## Related Commands

- `code_reviewer.generate_review_report` - Analyze the commit
- `code_reviewer.notify_architect` - Escalate findings

---

**Version**: 1.0
**Last Updated**: 2025-10-26
