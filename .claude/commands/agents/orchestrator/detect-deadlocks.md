---
command: orchestrator.detect-deadlocks
agent: orchestrator
action: detect_deadlocks
description: Detect circular dependencies in task graph that cause deadlocks
tables:
  read: [specs_task, specs_task_dependency]
  write: []
required_tools: [database, graph_analysis]
cfr_compliance:
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.detect-deadlocks

## Purpose

Proactively detect deadlocks in the task dependency graph by:
1. Building complete dependency graph
2. Running cycle detection algorithms
3. Identifying circular task chains
4. Reporting all affected tasks
5. Suggesting resolution strategies
6. Preventing execution of deadlocked tasks

## Parameters

```python
parameters = {
    "ACTION": "detect",  # "detect" or "analyze"
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "REPORT_LEVEL": "detailed"  # "summary" or "detailed"
}
```

## Deadlock Detection Algorithm

### Algorithm 1: Depth-First Search (DFS)

```python
def find_cycles_dfs(graph: dict) -> list:
    """Find all cycles in directed graph using DFS."""
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(node: str, path: list) -> None:
        visited.add(node)
        recursion_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path[:])
            elif neighbor in recursion_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        recursion_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node, [])

    return cycles
```

### Algorithm 2: Tarjan's Strongly Connected Components

```python
def find_sccs(graph: dict) -> list:
    """Find strongly connected components (cycles) using Tarjan's algorithm."""
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = set()
    sccs = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)

        for successor in graph.get(node, []):
            if successor not in index:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in on_stack:
                lowlinks[node] = min(lowlinks[node], index[successor])

        if lowlinks[node] == index[node]:
            scc = []
            while True:
                successor = stack.pop()
                on_stack.remove(successor)
                scc.append(successor)
                if successor == node:
                    break
            if len(scc) > 1:  # Only report cycles (SCC size > 1)
                sccs.append(scc)

    for node in graph:
        if node not in index:
            strongconnect(node)

    return sccs
```

## Database Query

Build dependency graph from specs_task_dependency:

```sql
SELECT
    std.task_id,
    std.dependency_id_ref,
    std.dependency_type,
    st1.status as task_status,
    st2.status as dependency_status
FROM specs_task_dependency std
JOIN specs_task st1 ON std.task_id = st1.task_id
JOIN specs_task st2 ON std.dependency_id_ref = st2.task_id
WHERE std.dependency_type = 'hard'
ORDER BY std.task_id;
```

## Detection Operations

### Operation 1: Detect Deadlocks

```python
invoke_command("detect-deadlocks", {
    "ACTION": "detect",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "REPORT_LEVEL": "detailed"
})
```

**Output (No Deadlocks)**:
```json
{
    "success": true,
    "action": "detect",
    "deadlocks_found": 0,
    "total_tasks": 12,
    "total_dependencies": 18,
    "graph_acyclic": true,
    "message": "No circular dependencies detected",
    "timestamp": "2025-10-26T10:35:00Z"
}
```

**Output (Deadlock Found)**:
```json
{
    "success": true,
    "action": "detect",
    "deadlocks_found": 2,
    "total_tasks": 12,
    "total_dependencies": 18,
    "circular_chains": [
        {
            "chain": [
                "TASK-31-1",
                "TASK-31-2",
                "TASK-31-3",
                "TASK-31-1"
            ],
            "length": 3,
            "affected_tasks": ["TASK-31-1", "TASK-31-2", "TASK-31-3"],
            "severity": "high"
        },
        {
            "chain": [
                "TASK-32-1",
                "TASK-32-2",
                "TASK-32-1"
            ],
            "length": 2,
            "affected_tasks": ["TASK-32-1", "TASK-32-2"],
            "severity": "critical"
        }
    ],
    "resolution_suggestions": [
        "Review TASK-31-1 and TASK-31-3 dependencies",
        "Remove soft dependency from TASK-31-2 to TASK-31-1",
        "Break cycle: Make TASK-32-2 not depend on TASK-32-1"
    ],
    "timestamp": "2025-10-26T10:35:00Z"
}
```

### Operation 2: Analyze Specific Cycle

```python
invoke_command("detect-deadlocks", {
    "ACTION": "analyze",
    "CYCLE": ["TASK-31-1", "TASK-31-2", "TASK-31-3"],
    "REPORT_LEVEL": "detailed"
})
```

**Output**:
```json
{
    "success": true,
    "action": "analyze",
    "cycle": ["TASK-31-1", "TASK-31-2", "TASK-31-3"],
    "cycle_length": 3,
    "edges": [
        {
            "from": "TASK-31-1",
            "to": "TASK-31-2",
            "type": "hard",
            "reason": "TASK-31-2 requires output from TASK-31-1"
        },
        {
            "from": "TASK-31-2",
            "to": "TASK-31-3",
            "type": "hard",
            "reason": "TASK-31-3 requires database schema from TASK-31-2"
        },
        {
            "from": "TASK-31-3",
            "to": "TASK-31-1",
            "type": "soft",
            "reason": "TASK-31-1 depends on API spec from TASK-31-3"
        }
    ],
    "resolution_options": [
        {
            "option": 1,
            "action": "Remove soft dependency TASK-31-3 -> TASK-31-1",
            "impact": "TASK-31-1 can proceed without TASK-31-3 output"
        },
        {
            "option": 2,
            "action": "Parallelize TASK-31-1 and TASK-31-3",
            "impact": "Both tasks run simultaneously, breaking dependency"
        },
        {
            "option": 3,
            "action": "Change dependency order: TASK-31-1 -> TASK-31-3 -> TASK-31-2",
            "impact": "Sequential execution prevents deadlock"
        }
    ]
}
```

## Cycle Severity Levels

| Severity | Length | Impact | Action |
|----------|--------|--------|--------|
| Critical | 2 | Blocks execution | Prevent immediately |
| High | 3-4 | Significantly delays | Resolve ASAP |
| Medium | 5+ | Limits parallelism | Review dependencies |

## Resolution Strategies

1. **Remove soft dependencies** - Convert 'soft' edges to not required
2. **Parallelize tasks** - Execute independent tasks simultaneously
3. **Reorder dependencies** - Change execution sequence
4. **Split tasks** - Divide large task into smaller independent ones
5. **Add intermediate task** - Break cycle with new synchronization point

## Success Criteria

1. All cycles correctly identified
2. Affected tasks listed completely
3. Cycle severity assessed accurately
4. Resolution suggestions practical
5. Detection completes in <2 seconds
6. No false positives

## Performance Optimization

- Cache dependency graph in memory
- Run detection periodically (every 5 minutes)
- Alert immediately on new deadlock
- Log all detected cycles for audit trail

## Error Handling

```json
{
    "success": false,
    "error": "graph_analysis_failed",
    "message": "Failed to build dependency graph",
    "affected_count": 0
}
```

## Related Commands

- coordinate-dependencies.md (manages dependencies)
- find-available-work.md (considers deadlock status)
- handle-agent-errors.md (responds to deadlock-caused failures)
