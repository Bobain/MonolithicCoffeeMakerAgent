---
command: orchestrator.monitor-resource-usage
agent: orchestrator
action: monitor_resource_usage
description: Track CPU/memory usage with psutil
tables:
  read: [agent_lifecycle]
  write: [metrics]
required_tools: [psutil, database]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
  - CFR-015: Centralized database storage (metrics in data/ directory)
---

# Command: orchestrator.monitor-resource-usage

## Purpose

Monitor system resource usage during parallel execution:
1. Track CPU usage per agent
2. Monitor memory consumption
3. Detect resource exhaustion
4. Throttle new task spawning if needed
5. Alert on resource constraints
6. Record metrics for analysis

## Parameters

```python
parameters = {
    "CHECK_INTERVAL_SECONDS": 30,
    "CPU_WARNING_THRESHOLD": 80,    # Percent
    "CPU_CRITICAL_THRESHOLD": 95,   # Percent
    "MEMORY_WARNING_THRESHOLD": 75,  # Percent
    "MEMORY_CRITICAL_THRESHOLD": 90, # Percent
    "DISK_WARNING_THRESHOLD": 80,    # Percent
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
}
```

## Resource Metrics

### CPU Monitoring

```python
import psutil

def check_cpu_usage() -> dict:
    """Check overall and per-core CPU usage."""
    return {
        "overall_percent": psutil.cpu_percent(interval=1),
        "per_core": psutil.cpu_percent(interval=1, percpu=True),
        "count": psutil.cpu_count(),
        "load_average": os.getloadavg()  # (1min, 5min, 15min)
    }
```

### Memory Monitoring

```python
def check_memory_usage() -> dict:
    """Check system and agent memory usage."""
    virtual_memory = psutil.virtual_memory()
    swap_memory = psutil.swap_memory()

    return {
        "virtual": {
            "total_mb": virtual_memory.total / 1024 / 1024,
            "available_mb": virtual_memory.available / 1024 / 1024,
            "used_mb": virtual_memory.used / 1024 / 1024,
            "percent": virtual_memory.percent
        },
        "swap": {
            "total_mb": swap_memory.total / 1024 / 1024,
            "used_mb": swap_memory.used / 1024 / 1024,
            "percent": swap_memory.percent
        }
    }
```

### Disk Monitoring

```python
def check_disk_usage(path: str) -> dict:
    """Check disk usage for project directory."""
    usage = psutil.disk_usage(path)

    return {
        "total_gb": usage.total / 1024 / 1024 / 1024,
        "used_gb": usage.used / 1024 / 1024 / 1024,
        "free_gb": usage.free / 1024 / 1024 / 1024,
        "percent": usage.percent
    }
```

## Monitoring Operations

### Operation 1: Check Current Resource Usage

```python
invoke_command("monitor-resource-usage", {
    "ACTION": "check",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "check",
    "timestamp": "2025-10-26T10:35:00Z",
    "cpu": {
        "overall_percent": 45.2,
        "per_core": [42.1, 48.3, 45.0, 46.1],
        "load_average": [3.2, 2.8, 2.1],
        "status": "normal"
    },
    "memory": {
        "virtual": {
            "total_mb": 16384,
            "available_mb": 6144,
            "used_mb": 10240,
            "percent": 62.5,
            "status": "normal"
        },
        "swap": {
            "total_mb": 4096,
            "used_mb": 512,
            "percent": 12.5,
            "status": "normal"
        }
    },
    "disk": {
        "total_gb": 500,
        "used_gb": 250,
        "free_gb": 250,
        "percent": 50.0,
        "status": "normal"
    },
    "can_spawn_agents": true
}
```

### Operation 2: Monitor Per-Agent Usage

```python
invoke_command("monitor-resource-usage", {
    "ACTION": "per_agent",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "per_agent",
    "agents": [
        {
            "agent_id": "code-developer-20251026-001",
            "agent_type": "code_developer",
            "pid": 12345,
            "cpu_percent": 85.3,
            "memory_mb": 450.2,
            "threads": 5,
            "status": "warning"
        },
        {
            "agent_id": "architect-20251026-001",
            "agent_type": "architect",
            "pid": 12346,
            "cpu_percent": 5.2,
            "memory_mb": 120.5,
            "threads": 3,
            "status": "normal"
        },
        {
            "agent_id": "project-manager-20251026-001",
            "agent_type": "project_manager",
            "pid": 12347,
            "cpu_percent": 2.1,
            "memory_mb": 85.3,
            "threads": 2,
            "status": "normal"
        }
    ],
    "total_cpu_percent": 92.6,
    "total_memory_mb": 655.0,
    "status": "critical"
}
```

### Operation 3: Get Historical Metrics

```python
invoke_command("monitor-resource-usage", {
    "ACTION": "history",
    "TIME_RANGE_MINUTES": 60,
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001"
})
```

**Output**:
```json
{
    "success": true,
    "action": "history",
    "time_range": "last 60 minutes",
    "metrics": [
        {
            "timestamp": "2025-10-26T09:35:00Z",
            "cpu_percent": 32.1,
            "memory_percent": 58.2,
            "disk_percent": 45.0,
            "active_agents": 2
        },
        {
            "timestamp": "2025-10-26T10:05:00Z",
            "cpu_percent": 65.3,
            "memory_percent": 72.1,
            "disk_percent": 48.0,
            "active_agents": 3
        },
        {
            "timestamp": "2025-10-26T10:35:00Z",
            "cpu_percent": 92.6,
            "memory_percent": 62.5,
            "disk_percent": 50.0,
            "active_agents": 3
        }
    ],
    "trends": {
        "cpu_trend": "increasing",
        "memory_trend": "stable",
        "disk_trend": "increasing"
    }
}
```

## Metrics Storage

Store metrics in metrics.db:

```sql
CREATE TABLE metrics (
    metric_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP,
    metric_type TEXT,      -- "cpu", "memory", "disk"
    value FLOAT,
    unit TEXT,             -- "percent", "mb", "gb"
    agent_id TEXT,
    orchestrator_instance_id TEXT
);
```

## Resource Constraints

| Resource | Warning | Critical | Action |
|----------|---------|----------|--------|
| CPU | >80% | >95% | Throttle new tasks |
| Memory | >75% | >90% | Stop new tasks |
| Disk | >80% | >95% | Alert, cleanup |
| Swap | >50% | >75% | Alert, investigate |

## Spawn Decision Logic

```python
def can_spawn_new_agent(thresholds: dict) -> bool:
    """Determine if system has capacity for new agent."""
    cpu = check_cpu_usage()["overall_percent"]
    memory = check_memory_usage()["virtual"]["percent"]
    disk = check_disk_usage(".")["percent"]

    if cpu > thresholds["CPU_CRITICAL_THRESHOLD"]:
        return False
    if memory > thresholds["MEMORY_CRITICAL_THRESHOLD"]:
        return False
    if disk > thresholds["DISK_CRITICAL_THRESHOLD"]:
        return False

    return True
```

## Success Criteria

1. All resource metrics collected accurately
2. Thresholds evaluated correctly
3. Metrics stored in database
4. Alerts triggered appropriately
5. Historical data preserved
6. Per-agent tracking accurate

## Error Handling

```json
{
    "success": false,
    "error": "resource_critical",
    "message": "System resources critically low",
    "cpu_percent": 98.5,
    "memory_percent": 92.1,
    "action_taken": "Throttled new task spawning"
}
```

## Alert Levels

| Level | Threshold | Response |
|-------|-----------|----------|
| Normal | <70% | Continue normally |
| Warning | 70-80% | Monitor closely |
| Critical | 80-95% | Throttle new tasks |
| Severe | >95% | Stop new tasks |

## Related Commands

- spawn-agent-session.md (checks resources before spawn)
- monitor-agent-lifecycle.md (tracks agent resource usage)
- generate-activity-summary.md (includes resource metrics)
