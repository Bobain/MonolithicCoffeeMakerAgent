---
command: orchestrator.generate-activity-summary
agent: orchestrator
action: generate_activity_summary
description: Create activity reports from execution traces
tables:
  read: [agent_lifecycle, orchestrator_task, metrics]
  write: []
required_tools: [database, markdown]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.generate-activity-summary

## Purpose

Generate comprehensive activity reports to understand execution progress:
1. Summarize task completion status
2. Report agent activity and uptime
3. Calculate performance metrics (throughput, efficiency)
4. Identify bottlenecks
5. Track resource utilization
6. Generate markdown reports

## Parameters

```python
parameters = {
    "TIME_RANGE": "last_24h",  # "last_1h", "last_24h", "last_7d", "all"
    "DETAIL_LEVEL": "summary",  # "summary", "detailed", "comprehensive"
    "OUTPUT_FORMAT": "markdown", # "markdown", "json"
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
}
```

## Summary Metrics

### Task Progress

```sql
SELECT
    COUNT(*) as total_tasks,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
    AVG(
        JULIANDAY(completed_at) - JULIANDAY(created_at)
    ) * 24 as avg_hours_to_complete
FROM orchestrator_task;
```

### Agent Statistics

```sql
SELECT
    agent_type,
    COUNT(*) as total_agents,
    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as active,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    AVG(
        CASE WHEN completed_at IS NOT NULL
        THEN JULIANDAY(completed_at) - JULIANDAY(started_at)
        ELSE NULL
        END
    ) * 24 as avg_hours_active
FROM agent_lifecycle
GROUP BY agent_type;
```

## Report Operations

### Operation 1: Generate Activity Summary

```python
invoke_command("generate-activity-summary", {
    "TIME_RANGE": "last_24h",
    "DETAIL_LEVEL": "summary",
    "OUTPUT_FORMAT": "markdown"
})
```

**Output** (Markdown):
```markdown
# Activity Summary - Last 24 Hours

## Executive Summary

- **Period**: 2025-10-25 10:35 to 2025-10-26 10:35
- **Total Tasks**: 12
- **Completed**: 8 (67%)
- **Running**: 2 (17%)
- **Failed**: 1 (8%)
- **Pending**: 1 (8%)

## Task Performance

### Completion Statistics
- **Average time to complete**: 4.2 hours
- **Fastest task**: TASK-31-1 (2.1 hours)
- **Slowest task**: TASK-32-1 (7.5 hours)
- **Success rate**: 88.9% (8/9 completed)

### Task Status Breakdown

| Task ID | Spec | Status | Duration | Agent |
|---------|------|--------|----------|-------|
| TASK-31-1 | SPEC-031 | Completed | 2.1h | code-developer |
| TASK-31-2 | SPEC-031 | Completed | 3.0h | code-developer |
| TASK-32-1 | SPEC-032 | Running | 6.2h | code-developer |
| TASK-33-1 | SPEC-033 | Pending | - | - |
| ... | | | | |

## Agent Activity

### Agent Status
- **code_developer**: 1 active, 4 completed, 1 failed
- **architect**: 0 active, 2 completed, 0 failed
- **project_manager**: 0 active, 1 completed, 0 failed

### Agent Efficiency
- **code_developer average uptime**: 4.3 hours per task
- **architect average uptime**: 1.2 hours per task
- **project_manager average uptime**: 0.5 hours per task

## Resource Utilization

### CPU Usage
- **Average**: 45.2%
- **Peak**: 92.6%
- **Idle**: 7.4%

### Memory Usage
- **Average**: 62.5%
- **Peak**: 72.1%
- **Available**: 37.9%

### Disk Usage
- **Used**: 250 GB / 500 GB (50%)
- **Trend**: Increasing 1.2 GB/hour
- **Estimated full**: 200+ hours

## Performance Bottlenecks

### Identified Issues
1. **Code discovery overhead**: 15-30 min per task (44% of implementation time)
2. **Test failures**: TASK-31-3 restarted 2 times (6.5 hours)
3. **Dependency blocking**: TASK-32-2 blocked for 2.1 hours waiting for TASK-31-2

### Recommendations
- Implement code index caching to reduce discovery time
- Add pre-flight test validation before agent spawn
- Parallelize TASK-32 specs (currently sequential)

## Errors and Failures

### Failed Tasks
- **TASK-31-3**: Git merge conflict (manual resolution needed)
  - Duration: 4.2 hours
  - Cause: Conflicting database migrations
  - Resolution: Manual merge by architect

### Retry Attempts
- **TASK-32-1**: Restarted 2 times (initial timeout, then test failure)
- **TASK-33-1**: Awaiting spec completion (blocked on TASK-32-1)

## Recent Activity Timeline

```
2025-10-25 10:35  TASK-31-1 started (code_developer)
2025-10-25 12:40  TASK-31-1 completed
2025-10-25 12:45  TASK-31-2 started
2025-10-25 15:45  TASK-31-2 completed, TASK-31-3 started
2025-10-25 20:00  TASK-31-3 failed (merge conflict)
2025-10-26 02:15  TASK-31-3 restarted, completed
2025-10-26 04:20  TASK-32-1 started
2025-10-26 10:35  TASK-32-1 still running (6.2 hours)
```

## Next Steps

1. Resolve merge conflict in TASK-31-3
2. Monitor TASK-32-1 progress (approaching 7 hour timeout)
3. Review dependency blocking pattern
4. Implement code caching optimization

---

*Report generated at 2025-10-26 10:35:00 UTC*
```

### Operation 2: Generate Detailed Report

```python
invoke_command("generate-activity-summary", {
    "TIME_RANGE": "last_7d",
    "DETAIL_LEVEL": "detailed",
    "OUTPUT_FORMAT": "json"
})
```

**Output** (JSON):
```json
{
    "success": true,
    "report_type": "activity_summary",
    "time_range": "last 7 days",
    "detail_level": "detailed",
    "generated_at": "2025-10-26T10:35:00Z",
    "summary": {
        "total_tasks": 42,
        "completed": 35,
        "running": 3,
        "failed": 2,
        "pending": 2,
        "success_rate": 0.944
    },
    "performance": {
        "avg_hours_per_task": 4.2,
        "total_hours": 147.0,
        "tasks_per_hour": 0.286
    },
    "agents": [
        {
            "agent_type": "code_developer",
            "total": 28,
            "completed": 24,
            "active": 2,
            "failed": 2,
            "avg_hours_per_task": 4.5
        },
        {
            "agent_type": "architect",
            "total": 10,
            "completed": 9,
            "active": 1,
            "failed": 0,
            "avg_hours_per_task": 1.2
        },
        {
            "agent_type": "project_manager",
            "total": 4,
            "completed": 4,
            "active": 0,
            "failed": 0,
            "avg_hours_per_task": 0.5
        }
    ],
    "resources": {
        "cpu_avg_percent": 45.2,
        "memory_avg_percent": 62.5,
        "disk_usage_percent": 50.0
    },
    "bottlenecks": [
        {
            "issue": "Code discovery overhead",
            "impact": "44% of implementation time",
            "affected_tasks": 28,
            "severity": "high",
            "recommendation": "Implement code caching"
        }
    ]
}
```

### Operation 3: Export Activity Report

```python
invoke_command("generate-activity-summary", {
    "TIME_RANGE": "last_24h",
    "OUTPUT_FORMAT": "markdown",
    "EXPORT_PATH": "/path/to/reports/activity-20251026.md"
})
```

**Output**:
```json
{
    "success": true,
    "action": "export",
    "report_path": "/path/to/reports/activity-20251026.md",
    "file_size_kb": 45.2,
    "message": "Report exported successfully"
}
```

## Report Sections

| Section | Content | Use Case |
|---------|---------|----------|
| Executive Summary | High-level metrics | Management briefing |
| Task Performance | Completion stats | Project tracking |
| Agent Activity | Per-agent metrics | Resource allocation |
| Resource Usage | CPU, memory, disk | System health |
| Bottlenecks | Issues and recommendations | Performance tuning |
| Error Report | Failed tasks | Debugging |
| Timeline | Execution history | Audit trail |

## Success Criteria

1. All metrics calculated accurately
2. Report generated in requested format
3. Time ranges honored
4. Markdown/JSON well-formatted
5. All required sections included
6. Bottlenecks correctly identified

## Performance Metrics

```
Throughput = Total_Tasks_Completed / Total_Time_Hours
Efficiency = Tasks_Completed / (Tasks_Completed + Tasks_Failed)
Utilization = Average_CPU_Percent / 100
Velocity = Hours_Per_Task
```

## Related Commands

- monitor-agent-lifecycle.md (provides agent metrics)
- monitor-resource-usage.md (provides resource data)
- handle-agent-errors.md (provides error data)
