---
command: project_manager.monitor_github_issues
agent: project_manager
action: monitor_github_issues
data_domain: github
write_tables: [system_audit]
read_tables: [roadmap_priority]
required_skills: []
required_tools: [gh]
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.monitor_github_issues

## Purpose

Monitor GitHub issues and track bug reports. Identifies critical issues and correlates them with roadmap priorities.

## Input Parameters

```yaml
repository: string       # Optional - GitHub repository (default: current repo)
label: string            # Optional - Filter by label (e.g., "bug", "critical")
state: string            # Optional - "open", "closed", "all" (default: "open")
sort_by: string          # Optional - "created", "updated", "comments" (default: "updated")
limit: integer           # Optional - Max issues to retrieve (default: 50)
```

## Database Operations

### READ Operations

```sql
SELECT id, title, status
FROM roadmap_priority;
```

### WRITE Operations

```sql
-- Create audit log entry
INSERT INTO system_audit (
    table_name, item_id, action, field_changed, new_value,
    changed_by, changed_at
) VALUES ('github_issues', ?, 'monitor', 'issue_status', ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify state is valid ("open", "closed", "all")
   - Verify sort_by is valid
   - Verify limit is positive

2. **Query GitHub Issues**
   - Use `gh issue list` command
   - Request fields: number, title, labels, state, createdAt, updatedAt, comments
   - Apply label filter if provided
   - Sort by specified field

3. **Categorize Issues**
   - Identify critical issues (by label or priority)
   - Group by label (bug, feature-request, enhancement, documentation)
   - Flag issues with high comment counts (ongoing discussion)

4. **Analyze Issue Status**
   - Check if linked to roadmap priority
   - Check if linked to PR
   - Calculate age (time since creation/last update)

5. **Generate Insights**
   - Count by label/type
   - Identify high-priority issues
   - Detect unresolved critical issues

6. **Create Audit Log Entry**
   - Log monitoring activity
   - Include summary statistics

7. **Return Results**

## Output

```json
{
  "success": true,
  "issues_found": 10,
  "critical_issues": 2,
  "by_label": {
    "bug": 5,
    "critical": 2,
    "enhancement": 3,
    "documentation": 1
  },
  "issues": [
    {
      "number": 456,
      "title": "Critical bug in parser - causes crash on invalid input",
      "labels": ["bug", "critical"],
      "state": "open",
      "created_at": "2025-10-20T10:30:00Z",
      "updated_at": "2025-10-26T09:15:00Z",
      "days_old": 6,
      "comments": 8,
      "url": "https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues/456",
      "priority": "critical"
    },
    {
      "number": 457,
      "title": "Documentation needs update for new API endpoint",
      "labels": ["documentation"],
      "state": "open",
      "created_at": "2025-10-25T14:00:00Z",
      "updated_at": "2025-10-25T14:00:00Z",
      "days_old": 1,
      "comments": 0,
      "url": "https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues/457",
      "priority": "low"
    }
  ],
  "recommendations": [
    "2 critical issues open - prioritize review and resolution",
    "5 bug reports - consider creating priority for bug fixes"
  ],
  "monitoring_timestamp": "2025-10-26T11:30:00Z"
}
```

## Implementation Pattern

```python
def monitor_github_issues(db: DomainWrapper, params: dict):
    """Monitor GitHub issues and track bug reports."""
    import subprocess
    import json
    from datetime import datetime, timedelta

    state = params.get("state", "open").lower()
    label = params.get("label")
    sort_by = params.get("sort_by", "updated").lower()
    limit = params.get("limit", 50)

    # 1. Validate input
    if state not in ["open", "closed", "all"]:
        raise ValueError(f"Invalid state: {state}. Must be 'open', 'closed', or 'all'")

    if sort_by not in ["created", "updated", "comments"]:
        raise ValueError(f"Invalid sort_by: {sort_by}")

    if limit <= 0:
        raise ValueError("limit must be positive")

    # 2. Build gh command
    cmd = [
        "gh", "issue", "list",
        "--state", state,
        "--json", "number,title,labels,state,createdAt,updatedAt,comments",
        "--limit", str(limit)
    ]

    if label:
        cmd.extend(["--label", label])

    # 3. Query GitHub issues
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(f"GitHub CLI error: {result.stderr}")

        issues = json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise RuntimeError("GitHub CLI request timed out")
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse GitHub response")

    # 4. Categorize and analyze issues
    issue_results = []
    label_counts = {}
    critical_count = 0

    now = datetime.now()

    for issue in issues:
        # Extract labels
        labels = [l.get("name") for l in issue.get("labels", [])] if issue.get("labels") else []

        # Count labels
        for lbl in labels:
            label_counts[lbl] = label_counts.get(lbl, 0) + 1

        # Determine priority
        priority = "low"
        if "critical" in labels or "security" in labels:
            priority = "critical"
            critical_count += 1
        elif "bug" in labels:
            priority = "medium"
            if issue.get("comments", 0) > 5:
                priority = "high"

        # Calculate age
        created_at = issue.get("createdAt")
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                days_old = (now - created).days
            except (ValueError, AttributeError):
                days_old = 0
        else:
            days_old = 0

        issue_result = {
            "number": issue["number"],
            "title": issue["title"],
            "labels": labels,
            "state": issue["state"],
            "created_at": created_at,
            "updated_at": issue.get("updatedAt"),
            "days_old": days_old,
            "comments": issue.get("comments", 0),
            "url": f"https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues/{issue['number']}",
            "priority": priority
        }

        issue_results.append(issue_result)

    # 5. Generate recommendations
    recommendations = []

    if critical_count > 0:
        recommendations.append(
            f"{critical_count} critical issue(s) open - prioritize review and resolution"
        )

    bug_count = label_counts.get("bug", 0)
    if bug_count >= 5:
        recommendations.append(
            f"{bug_count} bug reports - consider creating priority for bug fixes"
        )

    # 6. Create audit log entry
    db.write("system_audit", {
        "table_name": "github_issues",
        "item_id": "github_monitor",
        "action": "monitor",
        "field_changed": "issue_status",
        "new_value": json.dumps({
            "total_issues": len(issues),
            "critical": critical_count,
            "by_label": label_counts,
            "timestamp": datetime.now().isoformat()
        }),
        "changed_by": "project_manager",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    # 7. Return results
    return {
        "success": True,
        "issues_found": len(issues),
        "critical_issues": critical_count,
        "by_label": label_counts,
        "issues": issue_results,
        "recommendations": recommendations,
        "monitoring_timestamp": datetime.now().isoformat()
    }
```

## Issue Priority Classification

### Critical
- Security vulnerabilities
- Data loss bugs
- System crashes
- Label: "critical" or "security"

### High
- Blocking bugs (high impact)
- Performance issues affecting users
- Multiple reports of same bug
- Label: "bug" with 5+ comments

### Medium
- General bug reports
- Feature request with backing
- Label: "bug" or "enhancement"

### Low
- Documentation requests
- Minor improvements
- Label: "documentation"

## Success Criteria

- ✅ GitHub issues queried
- ✅ Critical issues flagged
- ✅ Issues categorized by label
- ✅ Audit log created
- ✅ Recommendations generated

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| GitHubAPIError | Rate limit, authentication | Wait, check GitHub token |
| CLINotFoundError | `gh` not installed | Install GitHub CLI |
| NetworkError | Network connectivity | Retry, check connection |
| InvalidStateError | Invalid state parameter | Use "open", "closed", or "all" |

## CFR Compliance

- **CFR-009**: No sound notifications
- **CFR-015**: Database-only storage via audit trail
- **CFR-007**: Efficient issue monitoring with minimal overhead

## Related Commands

- `project_manager.monitor_github_prs` - Monitor pull requests
- `project_manager.analyze_project_health` - Health analysis
- `project_manager.detect_stale_priorities` - Find stuck priorities
