# report

## Purpose
Generate comprehensive status report: active priorities, completion metrics, blockers, health analysis, save as markdown.

## Parameters
```yaml
scope: str = "all"  # "all" | "active" | "completed" | "blocked"
include_metrics: bool = true  # Calculate detailed metrics
output_path: str = "reports/roadmap-{date}.md"  # Report file path
format: str = "markdown"  # "markdown" | "json"
```

## Workflow
1. Query priorities filtered by scope
2. Calculate completion metrics (rate, velocity, ETA)
3. Identify blockers and dependencies
4. Analyze project health (on track, at risk, delayed)
5. Generate markdown or JSON report
6. Save to output_path
7. Return ReportResult

## Database Query
```sql
-- Load priorities with tasks
SELECT
    rp.priority_id, rp.title, rp.status, rp.progress, rp.assigned_agent,
    rp.created_at, rp.updated_at,
    COUNT(st.task_id) as total_tasks,
    SUM(CASE WHEN st.status='completed' THEN 1 ELSE 0 END) as completed_tasks
FROM roadmap_priority rp
LEFT JOIN specs_task st ON rp.priority_id = st.priority_id
WHERE rp.status IN (?)  -- Filtered by scope
GROUP BY rp.priority_id
ORDER BY rp.created_at DESC
```

## Result Object
```python
@dataclass
class ReportResult:
    report_path: str
    priorities_analyzed: int
    completion_rate: float  # 0.0-1.0
    blockers_found: int
    health_status: str  # "healthy" | "at_risk" | "critical"
    status: str  # "success" | "failed"
    metadata: dict  # {velocity, eta_days, risks}
```

## Metrics Calculated
- Total priorities: All in scope
- Completion rate: Completed / Total
- Average progress: Mean of all progress %
- Velocity: Tasks completed per week
- ETA: Estimated days to completion
- Blockers: Tasks with unmet dependencies

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| NoData | No priorities found | Check scope filter |
| DatabaseError | Query failed | Retry connection |
| FileWriteError | Can't save report | Check output_path permissions |
| InvalidScope | Unknown scope value | Use: all, active, completed, blocked |

## Example
```python
result = report(scope="active", include_metrics=True)
# ReportResult(
#   report_path="reports/roadmap-20251028.md",
#   priorities_analyzed=12,
#   completion_rate=0.45,
#   blockers_found=2,
#   health_status="healthy",
#   status="success",
#   metadata={"velocity": 8.5, "eta_days": 14, "risks": []}
# )
```

## Report Format
```markdown
# Roadmap Status Report - 2025-10-28

## Summary
- Total Priorities: 12
- Completion Rate: 45%
- Health: Healthy
- ETA: 14 days

## Active Priorities (7)
### PRIORITY-5: Auth System (60% complete)
- Status: In Progress
- Tasks: 3/5 done
- Assigned: code_developer

## Blockers (2)
- TASK-8-2: Blocked by TASK-7-3
```

## Related Commands
- roadmap() - Source data
- track() - Update data

---
Estimated: 70 lines | Context: ~4.5% | Examples: report_examples.md
