---
command: project_manager.strategic_planning
agent: project_manager
action: strategic_planning
data_domain: roadmap
write_tables: [roadmap_priority, system_audit]
read_tables: [roadmap_priority, specs_specification, agent_lifecycle]
required_skills: [roadmap_database_handling]
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.strategic_planning

## Purpose

Plan next priorities based on dependencies, resources, and goals. Recommends which priorities to start next given available capacity and constraints.

## Input Parameters

```yaml
planning_horizon_days: integer  # Optional - Days to plan ahead (default: 30)
max_priorities: integer         # Optional - Max priorities to plan (default: 10)
consider_dependencies: boolean  # Optional - Check dependencies (default: true)
resource_constraints: object    # Optional - Available resources {"code_developer": 1, "architect": 0.5}
```

## Database Operations

### READ Operations

```sql
SELECT id, title, status, spec_id, estimated_hours, dependencies,
       created_at, priority_number
FROM roadmap_priority
ORDER BY priority_number;

SELECT id, priority_id, status
FROM specs_specification;

SELECT agent_name, status, workload, available_capacity
FROM agent_lifecycle;
```

### WRITE Operations

```sql
-- Create audit log entry
INSERT INTO system_audit (
    table_name, item_id, action, field_changed, new_value,
    changed_by, changed_at
) VALUES ('strategic_planning', ?, 'plan', 'next_priorities', ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify planning_horizon_days is positive
   - Verify max_priorities is positive
   - Verify resource_constraints are valid

2. **Fetch Data**
   - Query all priorities
   - Query specifications
   - Query agent lifecycle/capacity

3. **Calculate Available Capacity**
   - For each agent: check current workload
   - Calculate available capacity in planning_horizon
   - Account for existing in-progress work

4. **Identify Ready Priorities**
   - Planned priorities that can start next
   - Check if spec exists (or can be created)
   - Check if dependencies satisfied

5. **Calculate Priority Score**
   - Based on: priority_number, estimated_hours, dependencies
   - Higher score = should start sooner
   - Adjust for resource availability

6. **Select Next Priorities**
   - Sort by score (highest first)
   - Limit to max_priorities
   - Check total estimated_hours vs available capacity
   - Flag if exceeds capacity

7. **Generate Recommendations**
   - For priorities without specs: recommend creating spec
   - For high-priority items: recommend starting immediately
   - For items exceeding capacity: recommend deferring

8. **Create Audit Log Entry**

9. **Return Results**

## Output

```json
{
  "success": true,
  "planning_horizon_days": 30,
  "priorities_planned": 5,
  "total_estimated_hours": 85,
  "available_capacity_hours": 160,
  "capacity_utilization_percent": 53,
  "capacity_status": "good",
  "planned_priorities": [
    {
      "priority_id": "PRIORITY-30",
      "title": "Feature Y",
      "priority_number": 10,
      "estimated_hours": 20,
      "spec_status": "complete",
      "has_dependencies": false,
      "estimated_start": "2025-10-27",
      "estimated_completion": "2025-11-06",
      "recommendation": "Ready to start immediately"
    },
    {
      "priority_id": "PRIORITY-31",
      "title": "Feature Z",
      "priority_number": 11,
      "estimated_hours": 30,
      "spec_status": "needed",
      "has_dependencies": true,
      "dependencies": ["PRIORITY-30"],
      "estimated_start": "2025-11-07",
      "estimated_completion": "2025-11-17",
      "recommendation": "Create spec for PRIORITY-30 first, then unblock this"
    }
  ],
  "recommendations": [
    "Create spec for PRIORITY-31 (architect action)",
    "code_developer can start PRIORITY-30 immediately",
    "Plan for PRIORITY-32 if PRIORITY-30 completes early",
    "Consider increasing architect capacity - 3 specs needed"
  ],
  "agent_capacity": {
    "code_developer": {
      "current_workload_hours": 40,
      "available_capacity_hours": 160,
      "utilization_percent": 25
    },
    "architect": {
      "current_workload_hours": 20,
      "available_capacity_hours": 40,
      "utilization_percent": 50
    }
  }
}
```

## Implementation Pattern

```python
def strategic_planning(db: DomainWrapper, params: dict):
    """Plan next priorities based on capacity and dependencies."""
    from datetime import datetime, timedelta
    import json

    planning_horizon = params.get("planning_horizon_days", 30)
    max_priorities = params.get("max_priorities", 10)
    consider_dependencies = params.get("consider_dependencies", True)
    resource_constraints = params.get("resource_constraints", {})

    # 1. Validate input
    if planning_horizon <= 0:
        raise ValueError("planning_horizon_days must be positive")

    if max_priorities <= 0:
        raise ValueError("max_priorities must be positive")

    # 2. Fetch data
    priorities = db.read("roadmap_priority")
    specs = db.read("specs_specification")
    agents = db.read("agent_lifecycle")

    # 3. Calculate available capacity
    agent_capacity = calculate_agent_capacity(agents, planning_horizon, resource_constraints)

    # 4. Identify ready priorities
    planned_priorities = [p for p in priorities if p.get("status") == "📝 Planned"]

    # Build spec map for quick lookup
    spec_map = {s.get("priority_id"): s for s in specs}

    # 5. Score and filter priorities
    scored_priorities = []

    for p in planned_priorities:
        # Check if dependencies are satisfied
        dependencies = p.get("dependencies", [])
        dependencies_met = True

        if consider_dependencies:
            for dep_id in dependencies:
                dep = next((x for x in priorities if x["id"] == dep_id), None)
                if dep and dep.get("status") != "✅ Complete":
                    dependencies_met = False
                    break

        if not dependencies_met:
            continue  # Skip if dependencies not met

        # Check spec status
        spec_status = "complete" if p.get("spec_id") else "needed"
        spec = spec_map.get(p["id"])
        if spec and spec.get("status") == "complete":
            spec_status = "complete"

        # Calculate score
        score = calculate_priority_score(p, spec_status)

        scored_priorities.append({
            "priority_id": p["id"],
            "title": p.get("title", "Unknown"),
            "priority_number": p.get("priority_number", 999),
            "estimated_hours": p.get("estimated_hours", 20),
            "spec_status": spec_status,
            "has_dependencies": len(dependencies) > 0,
            "dependencies": dependencies,
            "score": score
        })

    # 6. Select next priorities
    scored_priorities.sort(key=lambda x: x["score"], reverse=True)

    total_hours = 0
    planned = []

    for p in scored_priorities[:max_priorities]:
        estimated_hours = p["estimated_hours"]

        # Check if adding this would exceed capacity
        if total_hours + estimated_hours > agent_capacity["available_hours"]:
            break  # Stop if exceeds capacity

        # Calculate estimated dates
        days_from_now = total_hours / 8  # Assuming 8-hour days
        start_date = datetime.now() + timedelta(days=days_from_now)
        end_date = start_date + timedelta(hours=estimated_hours)

        # Generate recommendation
        recommendation = generate_priority_recommendation(
            p, spec_status=p["spec_status"], has_deps=p["has_dependencies"]
        )

        planned.append({
            **p,
            "estimated_start": start_date.strftime("%Y-%m-%d"),
            "estimated_completion": end_date.strftime("%Y-%m-%d"),
            "recommendation": recommendation
        })

        total_hours += estimated_hours

    # 7. Generate recommendations
    recommendations = []

    # Check for spec needs
    specs_needed = sum(1 for p in planned if p["spec_status"] == "needed")
    if specs_needed > 0:
        recommendations.append(
            f"Create {specs_needed} spec(s) for planned priorities (architect action)"
        )

    # Check capacity
    capacity_percent = (total_hours / agent_capacity["available_hours"]) * 100
    if capacity_percent > 80:
        recommendations.append("Capacity near limit - plan conservatively")
    elif capacity_percent < 50:
        recommendations.append("Significant capacity available - consider more priorities")

    # Check agent utilization
    for agent_name, capacity_info in agent_capacity.get("by_agent", {}).items():
        if capacity_info.get("utilization_percent", 0) > 80:
            recommendations.append(f"Consider increasing {agent_name} capacity")

    # 8. Create audit log entry
    db.write("system_audit", {
        "table_name": "strategic_planning",
        "item_id": f"plan_{datetime.now().isoformat()}",
        "action": "plan",
        "field_changed": "next_priorities",
        "new_value": json.dumps({
            "priorities_planned": len(planned),
            "total_hours": total_hours,
            "horizon_days": planning_horizon,
            "timestamp": datetime.now().isoformat()
        }),
        "changed_by": "project_manager",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    # 9. Return results
    return {
        "success": True,
        "planning_horizon_days": planning_horizon,
        "priorities_planned": len(planned),
        "total_estimated_hours": total_hours,
        "available_capacity_hours": agent_capacity.get("available_hours", 0),
        "capacity_utilization_percent": round(
            (total_hours / agent_capacity.get("available_hours", 1)) * 100, 1
        ),
        "capacity_status": "good" if capacity_percent < 80 else "tight",
        "planned_priorities": planned,
        "recommendations": recommendations,
        "agent_capacity": agent_capacity.get("by_agent", {})
    }

def calculate_agent_capacity(agents: list, horizon_days: int, constraints: dict) -> dict:
    """Calculate available agent capacity."""
    # Default: 40 hours/week per agent
    hours_per_week = 40
    weeks_in_horizon = horizon_days / 7

    total_available = 0
    by_agent = {}

    for agent in agents:
        agent_name = agent.get("agent_name")

        # Check if constrained
        if agent_name in constraints:
            capacity_multiplier = constraints[agent_name]
        else:
            capacity_multiplier = 1.0 if agent.get("status") == "online" else 0

        available = hours_per_week * weeks_in_horizon * capacity_multiplier
        total_available += available
        by_agent[agent_name] = {
            "available_capacity_hours": round(available, 1),
            "utilization_percent": agent.get("utilization_percent", 0)
        }

    return {
        "available_hours": total_available,
        "by_agent": by_agent
    }

def calculate_priority_score(priority: dict, spec_status: str) -> float:
    """Calculate score for priority ranking."""
    score = priority.get("priority_number", 100)

    # Boost if spec is ready
    if spec_status == "complete":
        score += 20

    # Adjust for estimated hours (prefer smaller items)
    estimated_hours = priority.get("estimated_hours", 20)
    if estimated_hours < 20:
        score += 10
    elif estimated_hours > 40:
        score -= 10

    return score

def generate_priority_recommendation(priority: dict, spec_status: str, has_deps: bool) -> str:
    """Generate recommendation for priority."""
    if spec_status == "needed":
        return "Create spec first (architect), then ready to start"

    if has_deps:
        return "Unblock dependencies, then start"

    return "Ready to start immediately"
```

## Capacity Calculation

```
Available Hours = (Hours per Week) * (Weeks in Horizon) * (Capacity Multiplier)

Default: 40 hours/week * 4.3 weeks/month = ~170 hours/month
Constrained: 40 * 4.3 * 0.5 = ~85 hours/month (50% capacity)
Offline: 40 * 4.3 * 0 = 0 hours/month
```

## Success Criteria

- ✅ Available capacity calculated
- ✅ Dependencies checked
- ✅ Priorities scored and ranked
- ✅ Next priorities identified
- ✅ Capacity status determined
- ✅ Recommendations provided
- ✅ Audit log created

## CFR Compliance

- **CFR-009**: No sound notifications
- **CFR-015**: Database-only planning storage
- **CFR-007**: Efficient planning with minimal overhead

## Related Commands

- `project_manager.analyze_project_health` - Health analysis
- `project_manager.detect_stale_priorities` - Find stuck work
- `project_manager.update_priority_status` - Update status
