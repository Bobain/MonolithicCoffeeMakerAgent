---
command: project_manager.analyze_project_health
agent: project_manager
action: analyze_project_health
data_domain: roadmap
write_tables: [system_audit]
read_tables: [roadmap_priority, specs_specification, review_code_review, agent_lifecycle]
required_skills: [roadmap_database_handling]
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.analyze_project_health

## Purpose

Generate comprehensive project health report including velocity metrics, blockers, risks, and actionable recommendations.

## Input Parameters

```yaml
time_window: integer     # Optional - Days to analyze (default: 30)
include_metrics: boolean # Optional - Include detailed metrics (default: true)
include_risks: boolean   # Optional - Include risk analysis (default: true)
include_blockers: boolean # Optional - Include blocker analysis (default: true)
```

## Database Operations

### READ Operations

```sql
-- Get all priorities
SELECT id, title, status, started_at, completed_at, updated_at,
       spec_id, dod_verified
FROM roadmap_priority
ORDER BY priority_number;

-- Get specs
SELECT id, priority_id, status, created_at, updated_at
FROM specs_specification;

-- Get code reviews
SELECT id, priority_id, status, passed, created_at
FROM review_code_review;

-- Get agent lifecycle
SELECT agent_name, status, last_activity
FROM agent_lifecycle;
```

### WRITE Operations

```sql
-- Create audit log entry
INSERT INTO system_audit (
    table_name, item_id, action, field_changed, new_value,
    changed_by, changed_at
) VALUES ('project_health', ?, 'analyze', 'health_report', ?, 'project_manager', ?);
```

## Execution Steps

1. **Fetch Data**
   - Query all priorities
   - Query all specs
   - Query code reviews
   - Query agent lifecycle

2. **Calculate Time Window**
   - Calculate cutoff_date = now - time_window days
   - Filter priorities by update dates within window

3. **Calculate Velocity Metrics**
   - Count completed priorities (status = "✅ Complete")
   - Count in_progress priorities
   - Count planned priorities
   - Calculate average completion time
   - Calculate completion rate

4. **Detect Blockers**
   - Priorities without specs
   - Priorities without assigned developers
   - Priorities with spec but no implementation started
   - Long-running in-progress priorities

5. **Identify Risks**
   - Low velocity trend
   - High blocker count
   - Agent availability issues
   - Spec coverage gaps

6. **Generate Recommendations**
   - For each blocker: suggest action
   - For each risk: suggest mitigation

7. **Calculate Health Score**
   - Base: 100
   - Deduct for blockers (-5 each)
   - Deduct for risks (-10 each)
   - Adjust for velocity

8. **Create Audit Log Entry**

9. **Return Results**

## Output

```json
{
  "success": true,
  "health_score": 78,
  "health_status": "Good",
  "analysis_period_days": 30,
  "analyzed_at": "2025-10-26T12:00:00Z",
  "velocity": {
    "avg_completion_time_days": 3.5,
    "completed_last_30_days": 12,
    "in_progress": 5,
    "planned": 8,
    "completion_rate": 60,
    "velocity_trend": "stable"
  },
  "blockers": [
    {
      "priority_id": "PRIORITY-25",
      "title": "User Authentication System",
      "blocked_reason": "Waiting for architect spec",
      "status": "🏗️ In Progress",
      "days_blocked": 7,
      "recommendation": "Request spec from architect, set deadline"
    },
    {
      "priority_id": "PRIORITY-20",
      "title": "Database Schema",
      "blocked_reason": "No developer assigned",
      "status": "📝 Planned",
      "days_blocked": 14,
      "recommendation": "Assign developer or defer priority"
    }
  ],
  "risks": [
    {
      "type": "low_velocity",
      "severity": "medium",
      "description": "Completion rate down from 70% to 60% (last 2 weeks)",
      "metrics": {
        "previous_rate": 0.70,
        "current_rate": 0.60,
        "change_percent": -14
      }
    },
    {
      "type": "spec_coverage",
      "severity": "high",
      "description": "3 in-progress priorities lack specs",
      "affected_priorities": ["PRIORITY-25", "PRIORITY-26"]
    },
    {
      "type": "agent_availability",
      "severity": "medium",
      "description": "code_developer offline for 2 days",
      "agent": "code_developer",
      "duration_hours": 48
    }
  ],
  "recommendations": [
    "Create spec for PRIORITY-25 (architect action)",
    "Assign developer to PRIORITY-20 or defer",
    "Investigate velocity decline - possible resource constraint",
    "Schedule architect/developer sync to align on specs"
  ]
}
```

## Implementation Pattern

```python
def analyze_project_health(db: DomainWrapper, params: dict):
    """Generate comprehensive project health report."""
    from datetime import datetime, timedelta
    import json

    time_window = params.get("time_window", 30)
    include_metrics = params.get("include_metrics", True)
    include_risks = params.get("include_risks", True)
    include_blockers = params.get("include_blockers", True)

    now = datetime.now()
    cutoff_date = now - timedelta(days=time_window)

    # 1. Fetch data
    priorities = db.read("roadmap_priority")
    specs = db.read("specs_specification")
    reviews = db.read("review_code_review")
    agents = db.read("agent_lifecycle")

    # 2. Filter by time window
    recent_priorities = [
        p for p in priorities
        if p.get("updated_at")
        and datetime.fromisoformat(p["updated_at"]) > cutoff_date
    ]

    # 3. Calculate velocity metrics
    completed = [p for p in recent_priorities if p["status"] == "✅ Complete"]
    in_progress = [p for p in recent_priorities if p["status"] == "🏗️ In Progress"]
    planned = [p for p in recent_priorities if p["status"] == "📝 Planned"]

    # Calculate average completion time
    completion_times = []
    for p in completed:
        if p.get("started_at") and p.get("completed_at"):
            try:
                start = datetime.fromisoformat(p["started_at"])
                end = datetime.fromisoformat(p["completed_at"])
                days = (end - start).days
                completion_times.append(days)
            except (ValueError, TypeError):
                pass

    avg_completion_time = (
        sum(completion_times) / len(completion_times) if completion_times else 0
    )
    completion_rate = (len(completed) / len(recent_priorities) * 100
                       if recent_priorities else 0)

    # 4. Detect blockers
    blockers = []

    for p in in_progress:
        if not p.get("spec_id"):
            days_in_progress = calculate_days_since(p.get("updated_at"))
            blockers.append({
                "priority_id": p["id"],
                "title": p.get("title", "Unknown"),
                "blocked_reason": "Waiting for architect spec",
                "status": p["status"],
                "days_blocked": days_in_progress,
                "recommendation": "Request spec from architect, set deadline"
            })

        # Check if long-running
        if p.get("started_at"):
            try:
                start = datetime.fromisoformat(p["started_at"])
                days_running = (now - start).days
                if days_running > 14:  # Arbitrary threshold
                    blockers.append({
                        "priority_id": p["id"],
                        "title": p.get("title", "Unknown"),
                        "blocked_reason": f"Long-running (>{days_running} days)",
                        "status": p["status"],
                        "days_blocked": days_running,
                        "recommendation": "Review progress, identify blockers, increase resources"
                    })
            except (ValueError, TypeError):
                pass

    # Planned priorities with no assignment
    for p in planned:
        if not p.get("assigned_to"):
            days_planned = calculate_days_since(p.get("updated_at"))
            if days_planned > 7:  # Arbitrary threshold
                blockers.append({
                    "priority_id": p["id"],
                    "title": p.get("title", "Unknown"),
                    "blocked_reason": "No developer assigned",
                    "status": p["status"],
                    "days_blocked": days_planned,
                    "recommendation": "Assign developer or defer priority"
                })

    # 5. Identify risks
    risks = []

    # Risk: Low velocity
    if completion_rate < 50:
        risks.append({
            "type": "low_velocity",
            "severity": "high",
            "description": f"Completion rate low ({completion_rate:.0f}%)",
            "metrics": {"completion_rate": completion_rate}
        })
    elif completion_rate < 60:
        risks.append({
            "type": "low_velocity",
            "severity": "medium",
            "description": f"Completion rate moderate ({completion_rate:.0f}%)",
            "metrics": {"completion_rate": completion_rate}
        })

    # Risk: Spec coverage
    specs_needed = sum(1 for p in in_progress if not p.get("spec_id"))
    if specs_needed > 0:
        risks.append({
            "type": "spec_coverage",
            "severity": "high" if specs_needed > 2 else "medium",
            "description": f"{specs_needed} in-progress priorities lack specs",
            "affected_count": specs_needed
        })

    # Risk: Agent availability
    for agent in agents:
        if agent.get("status") == "offline":
            last_activity = agent.get("last_activity")
            if last_activity:
                try:
                    last = datetime.fromisoformat(last_activity)
                    hours_offline = (now - last).total_seconds() / 3600
                    if hours_offline > 24:
                        risks.append({
                            "type": "agent_availability",
                            "severity": "medium",
                            "description": f"{agent['agent_name']} offline for {int(hours_offline)} hours",
                            "agent": agent["agent_name"],
                            "duration_hours": int(hours_offline)
                        })
                except (ValueError, TypeError):
                    pass

    # 6. Generate recommendations
    recommendations = []

    for blocker in blockers[:3]:  # Limit to top 3
        recommendations.append(blocker["recommendation"])

    if len(blockers) > 3:
        recommendations.append(f"... and {len(blockers) - 3} more blockers")

    for risk in risks:
        if risk["type"] == "spec_coverage":
            recommendations.append("Create specs for in-progress priorities (architect action)")
        elif risk["type"] == "low_velocity":
            recommendations.append("Investigate velocity decline - review resource allocation")
        elif risk["type"] == "agent_availability":
            recommendations.append(f"Check on {risk['agent']} - offline for {risk.get('duration_hours', '?')} hours")

    # 7. Calculate health score
    health_score = 100
    health_score -= min(len(blockers) * 5, 30)  # Max -30 for blockers
    health_score -= min(len(risks) * 10, 30)   # Max -30 for risks

    if completion_rate < 40:
        health_score -= 10
    elif completion_rate < 60:
        health_score -= 5

    health_score = max(0, min(100, health_score))

    # Determine health status
    if health_score >= 80:
        health_status = "Excellent"
    elif health_score >= 60:
        health_status = "Good"
    elif health_score >= 40:
        health_status = "Fair"
    else:
        health_status = "Poor"

    # 8. Create audit log entry
    db.write("system_audit", {
        "table_name": "project_health",
        "item_id": f"health_report_{now.isoformat()}",
        "action": "analyze",
        "field_changed": "health_report",
        "new_value": json.dumps({
            "health_score": health_score,
            "completion_rate": completion_rate,
            "blockers": len(blockers),
            "risks": len(risks)
        }),
        "changed_by": "project_manager",
        "changed_at": now.isoformat()
    }, action="create")

    # 9. Return results
    return {
        "success": True,
        "health_score": health_score,
        "health_status": health_status,
        "analysis_period_days": time_window,
        "analyzed_at": now.isoformat(),
        "velocity": {
            "avg_completion_time_days": round(avg_completion_time, 1),
            "completed_last_30_days": len(completed),
            "in_progress": len(in_progress),
            "planned": len(planned),
            "completion_rate": round(completion_rate, 1)
        } if include_metrics else {},
        "blockers": blockers if include_blockers else [],
        "risks": risks if include_risks else [],
        "recommendations": recommendations
    }

def calculate_days_since(iso_timestamp: str) -> int:
    """Calculate days since an ISO timestamp."""
    if not iso_timestamp:
        return 0
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        days = (datetime.now() - dt).days
        return max(0, days)
    except (ValueError, TypeError):
        return 0
```

## Health Score Calculation

```
Base: 100
- Blockers: -5 per blocker (max -30)
- Risks: -10 per risk (max -30)
- Low velocity: -10 if <40%, -5 if <60%

Score >= 80: Excellent (✅)
Score >= 60: Good (✅)
Score >= 40: Fair (⚠️)
Score < 40: Poor (❌)
```

## Success Criteria

- ✅ Health score calculated (0-100)
- ✅ Velocity metrics computed
- ✅ Blockers identified with recommendations
- ✅ Risks flagged with severity levels
- ✅ Actionable recommendations provided
- ✅ Audit log created

## CFR Compliance

- **CFR-009**: No sound notifications
- **CFR-015**: Database-only analysis storage
- **CFR-007**: Efficient health analysis with minimal overhead

## Related Commands

- `project_manager.detect_stale_priorities` - Find stuck priorities
- `project_manager.monitor_github_prs` - Monitor PRs
- `project_manager.monitor_github_issues` - Monitor issues
