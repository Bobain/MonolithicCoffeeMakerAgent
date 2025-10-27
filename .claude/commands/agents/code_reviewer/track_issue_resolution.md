---
command: code_reviewer.track_issue_resolution
agent: code_reviewer
action: track_issue_resolution
tables:
  write: [review_issue]
  read: [review_code_review, review_issue, review_commit]
required_tools: [git]
estimated_duration_seconds: 15
---

# Command: code_reviewer.track_issue_resolution

## Purpose

Monitor and track whether issues found in previous reviews are actually fixed in subsequent commits. This command enables continuous improvement by identifying patterns of recurring issues.

## Input Parameters

```yaml
commit_sha: string              # Required - current commit to check
review_id: string               # Required - current review
check_previous_commits: integer # How many previous commits to scan (default: 10)
severity_filter: string         # Check: "ALL", "CRITICAL", "HIGH" (default: "HIGH")
auto_resolve_fixed: boolean     # Mark as resolved if fixed (default: true)
```

## Database Operations

**Query 1: Get previous issues**
```sql
SELECT ri.* FROM review_issue ri
JOIN review_code_review rcr ON ri.review_id = rcr.id
WHERE ri.file_path = ? AND ri.is_resolved = 0
ORDER BY rcr.commit_sha DESC
LIMIT 5;
```

**Query 2: Check if issue is fixed**
```sql
SELECT changes FROM review_commit
WHERE sha = ? AND files_changed LIKE '%' || ? || '%'
LIMIT 1;
```

**Query 3: Mark issue as resolved**
```sql
UPDATE review_issue
SET is_resolved = 1, resolved_in_commit = ?
WHERE id = ? AND review_id IN (
    SELECT id FROM review_code_review WHERE status = 'completed'
);
```

**Query 4: Insert tracking record**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, is_resolved, resolved_in_commit, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));
```

## External Tools

### Git Diff Analysis

```bash
# Get diff between previous and current commit
git diff HEAD~1..HEAD -- {file_path}

# Show detailed changes
git show --unified=3 {commit_sha} -- {file_path}

# Check if specific pattern was fixed
git diff HEAD~5..HEAD --  {file_path} | grep -i "pattern"
```

## Tracking Algorithm

```
For each previous issue:
  1. Check if file was modified in current commit
  2. Get git diff for that file
  3. Analyze diff to see if issue was addressed:
     - Code removed?
     - Code modified?
     - New test added for that case?
  4. Compare original issue line with current code
  5. Determine if issue is resolved
  6. Update tracking record
```

## Success Criteria

- ✅ Identifies all unresolved issues from previous reviews
- ✅ Checks if files containing issues were modified
- ✅ Analyzes diffs to detect fixes
- ✅ Tracks resolution time (commits between issue and fix)
- ✅ Identifies recurring issues (not fixed multiple times)
- ✅ Creates issue records for tracking
- ✅ Completes in <15 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "tracking_duration_seconds": 8.3,
  "previous_issues_tracked": 5,
  "issue_resolution_summary": {
    "resolved": 2,
    "unresolved": 2,
    "still_pending": 1,
    "resolution_rate": 40.0
  },
  "resolved_issues": [
    {
      "id": "ISS-5",
      "original_review": "REV-2025-10-24T14-32-xyz",
      "original_severity": "HIGH",
      "issue_type": "Security",
      "file_path": "coffee_maker/auth.py",
      "description": "SQL injection vulnerability",
      "resolved_in_commit": "abc123def456",
      "commits_to_fix": 2,
      "time_to_fix_days": 1.5,
      "resolution_method": "Refactored to use parameterized queries"
    }
  ],
  "unresolved_issues": [
    {
      "id": "ISS-3",
      "original_review": "REV-2025-10-23T09-15-abc",
      "original_severity": "MEDIUM",
      "issue_type": "Documentation",
      "file_path": "coffee_maker/utils.py",
      "description": "Missing function docstrings",
      "still_unresolved": true,
      "commits_since_issue": 3,
      "days_outstanding": 2.2,
      "status": "OVERDUE"
    }
  ],
  "recurring_issues": [
    {
      "issue_type": "Missing docstrings",
      "file_path": "coffee_maker/api.py",
      "occurrences": 3,
      "first_reported": "2025-10-18",
      "last_reported": "2025-10-26",
      "pattern": "Consistent pattern - new functions added without docs"
    }
  ],
  "trends": {
    "avg_resolution_time_commits": 1.8,
    "avg_resolution_time_days": 1.2,
    "resolution_rate_by_severity": {
      "CRITICAL": 100.0,
      "HIGH": 75.0,
      "MEDIUM": 50.0,
      "LOW": 25.0
    },
    "most_common_unresolved": "Documentation"
  }
}
```

## Issue Resolution Statuses

**RESOLVED**:
- Code was fixed
- Test was added
- Documentation was updated
- All changes confirmed in diff

**UNRESOLVED**:
- File not modified
- Issue still present in code
- Only cosmetic changes made
- Issue moved to different location

**PENDING**:
- Recently reported
- No follow-up commits yet
- Awaiting action

**OVERDUE**:
- Outstanding for >N days
- Multiple commits without fix
- Pattern indicates avoidance

## Error Handling

**No Previous Issues**:
```json
{
  "status": "success",
  "previous_issues_tracked": 0,
  "message": "No previous issues to track"
}
```

**All Issues Resolved**:
```json
{
  "status": "success",
  "issue_resolution_summary": {
    "resolved": 5,
    "unresolved": 0,
    "resolution_rate": 100.0
  },
  "message": "Excellent! All previous issues have been resolved"
}
```

**Git Access Error**:
```json
{
  "status": "error",
  "error_type": "GIT_ERROR",
  "message": "Cannot access git repository",
  "recovery": "Ensure git is available and repository is initialized"
}
```

## Examples

### Example 1: Full tracking

```bash
code_reviewer.track_issue_resolution(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_previous_commits=10,
  severity_filter="HIGH",
  auto_resolve_fixed=true
)
```

### Example 2: Recent issues only

```bash
code_reviewer.track_issue_resolution(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_previous_commits=5,
  severity_filter="CRITICAL"
)
```

## Implementation Notes

- Track resolution time for improvement metrics
- Identify recurring issues that need architectural fixes
- Consider automation of common fixes
- Monitor teams' responsiveness to critical issues
- Link resolved issues to specific code changes
- Archive old issues after confirmation of resolution

## Resolution Pattern Analysis

### Fast Resolutions (< 1 day)
- Typically: Simple bugs, easy fixes
- Examples: Typos, missing imports, obvious logic errors

### Slow Resolutions (> 5 days)
- Typically: Architectural changes, refactoring
- Examples: Complexity reduction, security overhauls, API changes

### Never Resolved (recurring)
- Typically: Missing practices, training issues
- Examples: Missing documentation, inconsistent style, incomplete tests

## Related Commands

- `code_reviewer.generate_review_report` - Main review creation
- `code_reviewer.notify_architect` - Escalate unresolved issues
- `code_reviewer.generate_quality_score` - Include resolution metrics

---

**Version**: 1.0
**Last Updated**: 2025-10-26
