---
command: code_reviewer.notify_architect
agent: code_reviewer
action: notify_architect
tables:
  write: [notifications]
  read: [review_code_review, review_issue]
required_tools: [git]
estimated_duration_seconds: 5
---

# Command: code_reviewer.notify_architect

## Purpose

Send critical findings from code reviews to the architect agent for architectural decision-making. This command escalates code quality issues that require architectural oversight or immediate action.

## Input Parameters

```yaml
review_id: string               # Required - review to report on
severity_threshold: string      # Notify on: "CRITICAL", "HIGH", "MEDIUM" (default: "HIGH")
include_evidence: boolean       # Attach code snippets (default: true)
include_recommendations: boolean # Include fix suggestions (default: true)
urgent: boolean                 # Mark as urgent/high-priority (default: false)
```

## Database Operations

**Query 1: Get review details**
```sql
SELECT id, commit_sha, quality_score, total_issues, critical_issues, status
FROM review_code_review
WHERE id = ?;
```

**Query 2: Get issues by severity**
```sql
SELECT id, severity, category, file_path, line_number, description, recommendation
FROM review_issue
WHERE review_id = ? AND severity IN (?, ?)
ORDER BY severity DESC;
```

**Query 3: Insert notification**
```sql
INSERT INTO notifications (
    id, agent_id, recipient, title, message, level, priority,
    related_commit, review_id, created_at, sound, acknowledged
) VALUES (
    ?, 'code_reviewer', 'architect', ?, ?, ?, ?,
    ?, ?, datetime('now'), 0, 0
);
```

## External Tools

### Get Commit Info

```bash
# Get commit metadata for notification context
git show --quiet --format="%an %ae %ai" {commit_sha}

# Get changed files
git show --name-only --pretty="" {commit_sha}
```

## Success Criteria

- ✅ Queries review_code_review and review_issue tables
- ✅ Filters issues by severity threshold
- ✅ Sends notification to architect (never with sound=True per CFR-009)
- ✅ Includes code snippets if requested
- ✅ Links to commit and review report
- ✅ Sets notification priority based on severity
- ✅ Completes in <5 seconds

## Notification Priority Mapping

```
CRITICAL issues → priority: "critical" (immediate action)
HIGH issues + score < 7 → priority: "high" (address soon)
HIGH issues + score >= 7 → priority: "medium" (consider in next review)
MEDIUM issues only → priority: "low" (informational)
```

## Output Format

```json
{
  "status": "success",
  "notification_sent": true,
  "notification_id": "NOTIF-2025-10-26T10-36-001",
  "recipient": "architect",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "commit_author": "code_developer",
  "commit_date": "2025-10-26T10:35:00Z",
  "issues_included": 3,
  "severity_breakdown": {
    "critical": 1,
    "high": 2,
    "medium": 0
  },
  "quality_score": 6,
  "priority": "high",
  "notification_level": "alert",
  "evidence_attached": true
}
```

## Notification Template

**Subject**: Code Review Alert: {commit_sha[:8]} - Quality Score {score}/10

**Body**:
```
Architect, a new commit requires your attention.

COMMIT INFORMATION
- SHA: {commit_sha}
- Author: {author}
- Date: {commit_date}
- Message: {commit_message}
- Files Changed: {file_count}

QUALITY ASSESSMENT
- Overall Score: {quality_score}/10
- Status: {approved ? "APPROVED" : "NEEDS REVIEW"}
- Total Issues: {total_issues}

CRITICAL FINDINGS ({critical_count})
{For each CRITICAL issue:
  - [{severity}] {category}: {file_path}:{line_number}
    Description: {description}
    Recommendation: {recommendation}
}

HIGH PRIORITY FINDINGS ({high_count})
{For each HIGH issue:
  - [{severity}] {category}: {file_path}:{line_number}
    Description: {description}
}

GITHUB LINK
https://github.com/Bobain/MonolithicCoffeeMakerAgent/commit/{commit_sha}

REVIEW REPORT
{review_report_url}

ACTION REQUIRED
{If critical: "Review and approve/request changes immediately"}
{If high: "Review findings and plan mitigation"}
{If medium: "Informational - no immediate action required"}
```

## Error Handling

**Review Not Found**:
```json
{
  "status": "error",
  "error_type": "REVIEW_NOT_FOUND",
  "message": "Review REV-123 not found in database",
  "review_id": "REV-123"
}
```

**No Issues Match Threshold**:
```json
{
  "status": "success",
  "notification_sent": false,
  "reason": "No issues meet severity threshold (HIGH)",
  "issues_found": 3,
  "matching_severity": 0
}
```

**Database Error**:
```json
{
  "status": "error",
  "error_type": "DATABASE_ERROR",
  "message": "Cannot insert notification record",
  "recovery": "Retry notification in 60 seconds"
}
```

## Examples

### Example 1: Notify on critical issues

```bash
code_reviewer.notify_architect(
  review_id="REV-2025-10-26T10-35-abc1",
  severity_threshold="CRITICAL",
  include_evidence=true
)
```

**Response**:
```json
{
  "status": "success",
  "notification_sent": true,
  "notification_id": "NOTIF-2025-10-26T10-36-001",
  "issues_included": 1,
  "priority": "critical"
}
```

### Example 2: Notify on high priority issues

```bash
code_reviewer.notify_architect(
  review_id="REV-2025-10-26T10-35-abc1",
  severity_threshold="HIGH",
  include_recommendations=true,
  urgent=false
)
```

### Example 3: Informational notification

```bash
code_reviewer.notify_architect(
  review_id="REV-2025-10-26T10-35-abc1",
  severity_threshold="MEDIUM",
  include_evidence=false
)
```

## Implementation Notes

- CRITICAL: Follow CFR-009 - ALWAYS use `sound=False` for notifications
- Agent ID: Always set to "code_reviewer" in notifications
- Recipient: Always "architect" (architect is responsible for architectural decisions)
- Link to GitHub commit directly with commit SHA
- Include file paths and line numbers for easy navigation
- Provide actionable recommendations for each issue
- Set priority based on severity and quality_score combination
- Skip notification if no issues match threshold

## Related Commands

- `code_reviewer.generate_review_report` - Create the review
- `code_reviewer.check_architecture_compliance` - Detect architecture issues
- `code_reviewer.run_security_scan` - Detect security issues

---

**Version**: 1.0
**Last Updated**: 2025-10-26
