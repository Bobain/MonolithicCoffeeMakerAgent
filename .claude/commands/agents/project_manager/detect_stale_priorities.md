---
command: project_manager.detect_stale_priorities
agent: project_manager
action: detect_stale_priorities
data_domain: roadmap
write_tables: [system_audit]
read_tables: [roadmap_priority]
required_skills: [roadmap_database_handling]
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.detect_stale_priorities

## Purpose

Find priorities that are stuck (no progress for N days). Identifies blocked work, forgotten priorities, and items needing attention.

## Input Parameters

```yaml
stale_threshold_days: integer  # Optional - Days without update (default: 14)
statuses: list                 # Optional - Statuses to check (default: ["🏗️ In Progress", "📝 Planned"])
include_completed: boolean     # Optional - Include completed priorities (default: false)
```

## Database Operations

### READ Operations

```sql
SELECT id, title, status, updated_at, started_at, completed_at,
       spec_id, assigned_to, last_activity
FROM roadmap_priority
WHERE status IN (?, ?)
ORDER BY updated_at ASC;
```

### WRITE Operations

```sql
-- Create audit log entry
INSERT INTO system_audit (
    table_name, item_id, action, field_changed, new_value,
    changed_by, changed_at
) VALUES ('stale_detection', ?, 'detect', 'stale_status', ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify stale_threshold_days is positive integer
   - Verify statuses are valid

2. **Calculate Cutoff Date**
   - cutoff = now - stale_threshold_days

3. **Query Priorities**
   - Get all priorities in specified statuses
   - Filter by updated_at < cutoff_date

4. **Analyze Each Stale Priority**
   - Calculate days stale
   - Check if assigned to developer
   - Check if has spec
   - Check last activity
   - Determine root cause

5. **Categorize Staleness**
   - **Blocked**: No progress due to external factors
   - **Forgotten**: No activity, no known blockers
   - **Low Priority**: Deliberately postponed
   - **In Progress**: Developer assigned but inactive

6. **Generate Recommendations**
   - For each stale priority: suggest next action
   - Recommend escalation if needed

7. **Create Audit Log Entry**

8. **Return Results**

## Output

```json
{
  "success": true,
  "stale_threshold_days": 14,
  "stale_priorities": 3,
  "by_category": {
    "blocked": 1,
    "forgotten": 1,
    "low_priority": 1
  },
  "priorities": [
    {
      "priority_id": "PRIORITY-20",
      "title": "Feature X",
      "status": "🏗️ In Progress",
      "days_stale": 21,
      "last_updated": "2025-10-05T14:30:00Z",
      "stale_category": "blocked",
      "assigned_to": "code_developer",
      "has_spec": true,
      "last_activity": "2025-10-05T14:30:00Z",
      "recommendations": [
        "Check with code_developer on status",
        "Verify if spec is complete",
        "Consider re-prioritizing if blocked"
      ]
    },
    {
      "priority_id": "PRIORITY-15",
      "title": "Enhancement Y",
      "status": "📝 Planned",
      "days_stale": 28,
      "last_updated": "2025-09-28T10:00:00Z",
      "stale_category": "forgotten",
      "assigned_to": null,
      "has_spec": false,
      "last_activity": "2025-09-28T10:00:00Z",
      "recommendations": [
        "No assignment - unblock by assigning developer or deferring",
        "Missing spec - request from architect",
        "Consider removing if no longer needed"
      ]
    }
  ],
  "analysis_timestamp": "2025-10-26T13:00:00Z"
}
```

## Implementation Pattern

```python
def detect_stale_priorities(db: DomainWrapper, params: dict):
    """Find priorities with no progress for N days."""
    from datetime import datetime, timedelta

    threshold_days = params.get("stale_threshold_days", 14)
    statuses = params.get("statuses", ["🏗️ In Progress", "📝 Planned"])
    include_completed = params.get("include_completed", False)

    # 1. Validate input
    if threshold_days <= 0:
        raise ValueError("stale_threshold_days must be positive")

    # 2. Calculate cutoff date
    now = datetime.now()
    cutoff_date = now - timedelta(days=threshold_days)

    # 3. Query priorities
    priorities = db.read("roadmap_priority")

    # Filter by status
    filtered = [p for p in priorities if p.get("status") in statuses]

    # Filter by staleness
    stale = []
    for p in filtered:
        updated_at_str = p.get("updated_at")
        if updated_at_str:
            try:
                updated_at = datetime.fromisoformat(updated_at_str)
                if updated_at < cutoff_date:
                    stale.append(p)
            except (ValueError, TypeError):
                pass

    # 4. Analyze each stale priority
    stale_results = []
    category_counts = {"blocked": 0, "forgotten": 0, "low_priority": 0, "in_progress": 0}

    for p in stale:
        priority_id = p["id"]
        status = p.get("status")
        updated_at = datetime.fromisoformat(p.get("updated_at", now.isoformat()))
        days_stale = (now - updated_at).days

        # Determine category
        assigned_to = p.get("assigned_to")
        has_spec = bool(p.get("spec_id"))

        if status == "🏗️ In Progress":
            if assigned_to:
                category = "in_progress"
                category_counts["in_progress"] += 1
            else:
                category = "blocked"
                category_counts["blocked"] += 1
        elif status == "📝 Planned":
            if not assigned_to and not has_spec:
                category = "forgotten"
                category_counts["forgotten"] += 1
            elif not assigned_to:
                category = "blocked"
                category_counts["blocked"] += 1
            else:
                category = "low_priority"
                category_counts["low_priority"] += 1
        else:
            category = "low_priority"
            category_counts["low_priority"] += 1

        # Generate recommendations
        recommendations = []

        if category == "blocked":
            recommendations.append("Check on assignment and spec status")
            if not has_spec:
                recommendations.append("Missing spec - request from architect")
            if not assigned_to:
                recommendations.append("No developer assigned - assign or defer")

        elif category == "forgotten":
            recommendations.append("No assignment - unblock by assigning developer or deferring")
            recommendations.append("Missing spec - request from architect")
            recommendations.append("Consider removing if no longer needed")

        elif category == "in_progress":
            recommendations.append("Check with code_developer on status")
            if has_spec:
                recommendations.append("Verify if spec is complete and up to date")
            recommendations.append("Identify and remove blockers")

        elif category == "low_priority":
            recommendations.append("Re-prioritize or defer if needed")
            recommendations.append("Communicate decision to assigned developer")

        # Build result
        result = {
            "priority_id": priority_id,
            "title": p.get("title", "Unknown"),
            "status": status,
            "days_stale": days_stale,
            "last_updated": p.get("updated_at"),
            "stale_category": category,
            "assigned_to": assigned_to,
            "has_spec": has_spec,
            "last_activity": p.get("last_activity", p.get("updated_at")),
            "recommendations": recommendations
        }

        stale_results.append(result)

    # 5. Create audit log entry
    db.write("system_audit", {
        "table_name": "stale_detection",
        "item_id": f"stale_check_{now.isoformat()}",
        "action": "detect",
        "field_changed": "stale_status",
        "new_value": json.dumps({
            "stale_count": len(stale_results),
            "by_category": category_counts,
            "timestamp": now.isoformat()
        }),
        "changed_by": "project_manager",
        "changed_at": now.isoformat()
    }, action="create")

    # 6. Return results
    return {
        "success": True,
        "stale_threshold_days": threshold_days,
        "stale_priorities": len(stale_results),
        "by_category": category_counts,
        "priorities": stale_results,
        "analysis_timestamp": now.isoformat()
    }
```

## Staleness Categories

### Blocked
- **In Progress** priority with no assignment → developer needed
- **Planned** priority without spec → architect action needed
- **Any** priority with unresolved dependencies

### Forgotten
- **Planned** priority with no assignment and no spec
- No activity for threshold period
- Nobody working on it

### Low Priority
- **Planned** priority assigned but not started
- Deliberately postponed
- Waiting for other priorities to complete

### In Progress
- **In Progress** priority that's stalled
- Developer assigned but no activity
- Possible blocker or resource issue

## Recommendations by Category

| Category | Primary Recommendation | Secondary |
|----------|------------------------|-----------|
| Blocked | Check blockers, request spec | Unblock or defer |
| Forgotten | Assign developer or defer | Remove if obsolete |
| Low Priority | Re-prioritize or close | Communicate decision |
| In Progress | Check developer status | Identify blockers |

## Success Criteria

- ✅ Stale priorities identified
- ✅ Days stale calculated correctly
- ✅ Categories assigned (blocked, forgotten, etc.)
- ✅ Recommendations provided
- ✅ Audit log created
- ✅ Accurate staleness detection

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| InvalidThresholdError | threshold <= 0 | Use positive integer |
| InvalidStatusError | Invalid status in list | Use valid status values |
| DateParseError | Invalid date format | Use ISO format timestamps |

## CFR Compliance

- **CFR-009**: No sound notifications
- **CFR-015**: Database-only detection, no file modifications
- **CFR-007**: Efficient staleness detection with minimal overhead

## Related Commands

- `project_manager.analyze_project_health` - Health analysis
- `project_manager.update_priority_status` - Update priority status
- `project_manager.send_agent_notification` - Send notifications
