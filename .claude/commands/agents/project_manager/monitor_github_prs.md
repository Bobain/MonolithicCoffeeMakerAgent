---
command: project_manager.monitor_github_prs
agent: project_manager
action: monitor_github_prs
data_domain: github
write_tables: [system_audit]
read_tables: [roadmap_priority]
required_skills: [pr_monitoring_analysis]
required_tools: [gh]
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.monitor_github_prs

## Purpose

Monitor GitHub pull requests and detect blockers (failing CI, merge conflicts, stale PRs). Provides recommendations for unblocking work.

## Input Parameters

```yaml
repository: string       # Optional - GitHub repository (default: current repo)
state: string            # Optional - "open", "closed", "all" (default: "open")
check_blockers: boolean  # Optional - Detect blocking issues (default: true)
check_stale: boolean     # Optional - Check for stale PRs (default: true)
stale_days: integer      # Optional - Days to consider stale (default: 7)
```

## Database Operations

### READ Operations

```sql
SELECT id, title, status
FROM roadmap_priority
WHERE status = '🏗️ In Progress' OR status = '✅ Complete';
```

### WRITE Operations

```sql
-- Create audit log entry
INSERT INTO system_audit (
    table_name, item_id, action, field_changed, new_value,
    changed_by, changed_at
) VALUES ('github_prs', ?, 'monitor', 'pr_status', ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify state is valid ("open", "closed", "all")
   - Verify stale_days is positive integer

2. **Query GitHub PRs**
   - Use `gh pr list` command with specified state
   - Request fields: number, title, state, statusCheckRollup, mergeable, updatedAt, author
   - Parse JSON output

3. **Analyze Each PR**
   - Check CI status (statusCheckRollup)
   - Check mergeable status
   - Check age (for stale detection)
   - Extract priority ID from PR title/labels if present

4. **Detect Blockers**
   - Failing CI checks → blocked
   - Merge conflicts → blocked
   - Blocked by dependencies → blocked

5. **Detect Stale PRs**
   - If last update > stale_days ago → stale
   - No activity for extended period

6. **Correlate with Roadmap**
   - Try to link PRs to roadmap priorities
   - Check for unlinked PRs

7. **Generate Recommendations**
   - For blocked PRs: suggest fix actions
   - For stale PRs: suggest review/merge actions
   - For unlinked PRs: suggest priority mapping

8. **Create Audit Log Entry**
   - Log monitoring activity
   - Include summary statistics

9. **Return Results**

## Output

```json
{
  "success": true,
  "prs_found": 5,
  "blocking_prs": 1,
  "stale_prs": 2,
  "prs": [
    {
      "number": 123,
      "title": "feat: Implement PRIORITY-25 - User Authentication",
      "state": "open",
      "blocked": true,
      "blocker_reason": "Failing CI checks",
      "blocker_details": "Unit tests failing (3 failures)",
      "url": "https://github.com/Bobain/MonolithicCoffeeMakerAgent/pull/123",
      "author": "code_developer",
      "stale": false
    },
    {
      "number": 124,
      "title": "feat: PRIORITY-30 - Database Schema",
      "state": "open",
      "blocked": false,
      "stale": true,
      "days_since_update": 9,
      "url": "https://github.com/Bobain/MonolithicCoffeeMakerAgent/pull/124"
    }
  ],
  "recommendations": [
    "PR #123 needs attention - CI failing. Check unit test output.",
    "PR #124 is stale (9 days). Review and merge or close."
  ],
  "monitoring_timestamp": "2025-10-26T11:00:00Z"
}
```

## Implementation Pattern

```python
def monitor_github_prs(db: DomainWrapper, params: dict):
    """Monitor GitHub PRs and detect blockers."""
    import subprocess
    import json
    from datetime import datetime, timedelta

    state = params.get("state", "open").lower()
    check_blockers = params.get("check_blockers", True)
    check_stale = params.get("check_stale", True)
    stale_days = params.get("stale_days", 7)

    # 1. Validate input
    if state not in ["open", "closed", "all"]:
        raise ValueError(f"Invalid state: {state}. Must be 'open', 'closed', or 'all'")

    if stale_days <= 0:
        raise ValueError("stale_days must be positive")

    # 2. Query GitHub PRs using gh CLI
    try:
        result = subprocess.run(
            [
                "gh", "pr", "list",
                "--state", state,
                "--json", "number,title,state,statusCheckRollup,mergeable,updatedAt,author"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(f"GitHub CLI error: {result.stderr}")

        prs = json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise RuntimeError("GitHub CLI request timed out")
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse GitHub response")

    # 3. Get roadmap priorities for correlation
    roadmap_priorities = db.read("roadmap_priority")
    priority_map = {p["id"]: p for p in roadmap_priorities}

    # 4. Analyze each PR
    blocking_prs = []
    stale_prs = []
    pr_results = []
    recommendations = []

    now = datetime.now()
    stale_threshold = now - timedelta(days=stale_days)

    for pr in prs:
        pr_result = {
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"],
            "url": f"https://github.com/Bobain/MonolithicCoffeeMakerAgent/pull/{pr['number']}",
            "author": pr.get("author", {}).get("login", "unknown") if pr.get("author") else "unknown",
            "blocked": False,
            "stale": False
        }

        # Check for blockers
        if check_blockers:
            # Check CI status
            if pr.get("statusCheckRollup"):
                checks = pr["statusCheckRollup"]
                for check in checks:
                    if check.get("conclusion") == "FAILURE":
                        pr_result["blocked"] = True
                        pr_result["blocker_reason"] = "Failing CI checks"
                        pr_result["blocker_details"] = f"{check.get('name')} failed"
                        blocking_prs.append(pr_result)
                        recommendations.append(
                            f"PR #{pr['number']} needs attention - CI failing. Check {check.get('name')}."
                        )
                        break

            # Check mergeable status
            if not pr_result["blocked"] and pr.get("mergeable") == "CONFLICTING":
                pr_result["blocked"] = True
                pr_result["blocker_reason"] = "Merge conflicts"
                blocking_prs.append(pr_result)
                recommendations.append(f"PR #{pr['number']} has merge conflicts. Resolve conflicts.")

        # Check for staleness
        if check_stale:
            updated_at = pr.get("updatedAt")
            if updated_at:
                try:
                    updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    if updated < stale_threshold:
                        pr_result["stale"] = True
                        days_since = (now - updated).days
                        pr_result["days_since_update"] = days_since
                        stale_prs.append(pr_result)
                        recommendations.append(
                            f"PR #{pr['number']} is stale ({days_since} days). Review and merge or close."
                        )
                except (ValueError, AttributeError):
                    pass  # Skip if date parsing fails

        pr_results.append(pr_result)

    # 5. Create audit log entry
    db.write("system_audit", {
        "table_name": "github_prs",
        "item_id": "github_monitor",
        "action": "monitor",
        "field_changed": "pr_status",
        "new_value": json.dumps({
            "total_prs": len(prs),
            "blocking": len(blocking_prs),
            "stale": len(stale_prs),
            "timestamp": datetime.now().isoformat()
        }),
        "changed_by": "project_manager",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    # 6. Return results
    return {
        "success": True,
        "prs_found": len(prs),
        "blocking_prs": len(blocking_prs),
        "stale_prs": len(stale_prs),
        "prs": pr_results,
        "recommendations": recommendations,
        "monitoring_timestamp": datetime.now().isoformat()
    }
```

## Success Criteria

- ✅ GitHub PRs queried via `gh` CLI
- ✅ Blockers detected (failing checks, conflicts, stale)
- ✅ Recommendations generated
- ✅ Audit log created
- ✅ All blocking PRs identified

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
- **CFR-007**: Efficient PR monitoring with minimal overhead

## Related Commands

- `project_manager.monitor_github_issues` - Monitor issues
- `project_manager.analyze_project_health` - Health analysis
- `project_manager.detect_stale_priorities` - Find stuck priorities
