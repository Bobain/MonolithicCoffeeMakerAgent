---
command: code_developer.track_metrics
agent: code_developer
action: track_metrics
tables:
  write: [metrics_subtask]
  read: []
required_skills: []
required_tools: [database]
---

# Command: code_developer.track_metrics

## Purpose
Record implementation metrics (velocity, complexity, time, effort) for trend analysis and resource planning.

## Input Parameters

```yaml
task_id: string          # Required - Task being measured
metric_type: string      # Required - "velocity", "complexity", "time", "lines_of_code", "effort"
value: float             # Required - Metric value
unit: string             # Required - "hours", "lines", "points", "days"
notes: string            # Optional - Additional context
```

## Database Operations

### 1. Prepare Metric Record
```python
from datetime import datetime
import json

def track_metrics(db: DomainWrapper, params: dict):
    task_id = params["task_id"]
    metric_type = params["metric_type"]
    value = params["value"]
    unit = params["unit"]

    # Validate metric type
    valid_types = ["velocity", "complexity", "time", "lines_of_code", "effort"]
    if metric_type not in valid_types:
        return {
            "success": False,
            "error": f"Invalid metric type: {metric_type}",
            "valid_types": valid_types
        }

    # Validate unit matches metric type
    valid_units = {
        "velocity": ["points/hour", "tasks/day", "features/sprint"],
        "complexity": ["points", "score"],
        "time": ["hours", "days", "minutes"],
        "lines_of_code": ["lines", "files"],
        "effort": ["hours", "days", "story_points"]
    }

    if unit not in valid_units.get(metric_type, []):
        return {
            "success": False,
            "error": f"Invalid unit '{unit}' for metric type '{metric_type}'",
            "valid_units": valid_units[metric_type]
        }
```

### 2. Create Metric Record
```python
    # Create metric record
    metric_data = {
        "task_id": task_id,
        "metric_type": metric_type,
        "value": value,
        "unit": unit,
        "notes": params.get("notes", ""),
        "recorded_by": "code_developer",
        "recorded_at": datetime.now().isoformat()
    }

    # Store metric
    metric_id = db.write("metrics_subtask", metric_data, action="create")
    if not metric_id:
        return {
            "success": False,
            "error": "Failed to record metric"
        }
```

### 3. Calculate Derived Metrics
```python
    # Calculate productivity metrics based on type
    derived_metrics = {}

    if metric_type == "time":
        # Calculate velocity: tasks/hour
        derived_metrics["productivity"] = 1.0 / (value / 1.0) if value > 0 else 0

    elif metric_type == "lines_of_code":
        # Calculate code density
        derived_metrics["code_density"] = value  # lines added

    elif metric_type == "complexity":
        # Complexity score (lower is better)
        derived_metrics["complexity_score"] = value
```

### 4. Update Aggregate Metrics
```python
    # Get all metrics for this task to calculate averages
    all_metrics = db.read("metrics_subtask", {"task_id": task_id})

    if all_metrics:
        # Calculate average time spent
        time_metrics = [m for m in all_metrics if m["metric_type"] == "time"]
        if time_metrics:
            avg_time = sum(m["value"] for m in time_metrics) / len(time_metrics)

        # Calculate total code changed
        loc_metrics = [m for m in all_metrics if m["metric_type"] == "lines_of_code"]
        if loc_metrics:
            total_lines = sum(m["value"] for m in loc_metrics)

        # Store aggregate
        db.write("metrics_subtask", {
            "task_id": task_id,
            "metric_type": "aggregate",
            "value": json.dumps({
                "average_time_hours": round(avg_time, 2) if 'avg_time' in locals() else 0,
                "total_lines_changed": total_lines if 'total_lines' in locals() else 0
            }),
            "unit": "computed",
            "recorded_by": "code_developer",
            "recorded_at": datetime.now().isoformat()
        }, action="create")
```

### 5. Create Audit Record
```python
    db.write("system_audit", {
        "table_name": "metrics_subtask",
        "item_id": metric_id,
        "action": "created",
        "field_changed": "metric",
        "new_value": f"{metric_type}={value}{unit}",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": True,
        "metric_id": metric_id,
        "task_id": task_id,
        "metric_type": metric_type,
        "value": value,
        "unit": unit
    }
```

## Output

```json
{
  "success": true,
  "metric_id": "metric-12345",
  "task_id": "TASK-31-1",
  "metric_type": "velocity",
  "value": 8.5,
  "unit": "hours"
}
```

## Success Criteria

- ✅ Metric recorded in database
- ✅ Linked to task
- ✅ Timestamp captured
- ✅ Available for analysis
- ✅ Audit trail created

## Metric Types and Units

### Velocity (Productivity)
Measures tasks completed per time unit

```python
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "velocity",
    "value": 2.5,
    "unit": "tasks/day",
    "notes": "Completed 2.5 tasks per day on average"
})
```

### Complexity (Difficulty)
Measures code/feature complexity (1-10 scale or custom)

```python
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "complexity",
    "value": 7,
    "unit": "points",
    "notes": "Complex authentication feature, estimated 7 complexity points"
})
```

### Time (Duration)
Measures actual time spent

```python
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "time",
    "value": 6.5,
    "unit": "hours",
    "notes": "6.5 hours of implementation and testing"
})
```

### Lines of Code
Measures code size

```python
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "lines_of_code",
    "value": 450,
    "unit": "lines",
    "notes": "Added 450 lines of production code"
})
```

### Effort (Story Points)
Measures story point consumption

```python
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "effort",
    "value": 13,
    "unit": "story_points",
    "notes": "Consumed 13 story points"
})
```

## Metrics Dashboard Data

Track these per task for comprehensive metrics:

| Metric | Type | Unit | Purpose |
|--------|------|------|---------|
| Time | time | hours | Resource planning |
| Complexity | complexity | points | Risk assessment |
| Code Volume | lines_of_code | lines | Code review effort |
| Velocity | velocity | tasks/day | Team capacity |
| Effort | effort | story_points | Sprint planning |

## Usage Examples

### Track Time Spent
```python
# Morning session: 3 hours
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "time",
    "value": 3.0,
    "unit": "hours",
    "notes": "Morning development session"
})

# Afternoon session: 2.5 hours
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "time",
    "value": 2.5,
    "unit": "hours",
    "notes": "Afternoon testing and debugging"
})

# Total tracked: 5.5 hours
```

### Track Code Changes
```python
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "lines_of_code",
    "value": 250,
    "unit": "lines",
    "notes": "Production code additions"
})

track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "lines_of_code",
    "value": 180,
    "unit": "lines",
    "notes": "Test code additions"
})
```

### Track Complexity Assessment
```python
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "complexity",
    "value": 6,
    "unit": "points",
    "notes": "Medium-high complexity - required database schema changes"
})
```

## Trend Analysis

After collecting metrics, data can be analyzed for:

1. **Velocity Trends**: Are developers getting faster?
2. **Complexity Impact**: Do complex tasks take proportionally longer?
3. **Code Quality**: Is there correlation between complexity and test coverage?
4. **Team Capacity**: How many story points per sprint?
5. **Risk Indicators**: Which task types have highest variance?

## Integration with Other Commands

### After Complete Implementation
```python
# Record completion time
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "time",
    "value": 5.5,
    "unit": "hours",
    "notes": "Total time from start to completion"
})

# Record effort consumed
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "effort",
    "value": 8,
    "unit": "story_points",
    "notes": "Estimated 13 points, consumed 8"
})
```

### After Running Tests
```python
# Record code volume
track_metrics(db, {
    "task_id": "TASK-31-1",
    "metric_type": "lines_of_code",
    "value": 450,
    "unit": "lines",
    "notes": "Production code + tests"
})
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| InvalidMetricType | Unknown metric type | Use valid type |
| InvalidUnit | Unit doesn't match type | Use valid unit |
| InvalidValue | Value invalid (negative when positive required) | Check value |
| DatabaseError | Write failed | Check database |

## Queries for Analysis

After collecting metrics:

```sql
-- Average time per task type
SELECT task_type, AVG(value) as avg_hours
FROM metrics_subtask
WHERE metric_type = 'time'
GROUP BY task_type;

-- Velocity trend
SELECT recorded_at, value
FROM metrics_subtask
WHERE metric_type = 'velocity'
ORDER BY recorded_at;

-- Complexity vs Time correlation
SELECT m1.value as complexity, m2.value as time
FROM metrics_subtask m1
JOIN metrics_subtask m2 ON m1.task_id = m2.task_id
WHERE m1.metric_type = 'complexity'
AND m2.metric_type = 'time';
```
