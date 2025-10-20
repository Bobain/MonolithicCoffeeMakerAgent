# SPEC-110: Orchestrator Database Tracing

**Status**: Draft
**Created**: 2025-10-20
**Author**: architect + code_developer
**Related**: CFR-015 (Orchestrator Database Tracing), US-072 (Multi-Agent Orchestration)

## Problem Statement

Currently, agent lifecycle events (spawning, running, completion) are tracked in JSON files (`data/orchestrator/agent_state.json`), which leads to:

1. **Stale data accumulation** - Completed agents never cleaned up (706 lines, 64+ dead processes)
2. **No velocity analysis** - Cannot measure implementation speed or identify bottlenecks
3. **Limited observability** - No historical tracking of agent performance
4. **No idle time tracking** - Cannot detect inefficiencies in orchestrator work loop
5. **Inconsistent storage** - Tasks use SQLite (`data/orchestrator.db`), agents use JSON

## Proposed Solution

### 1. Agent Lifecycle Table

Add `agent_lifecycle` table to existing `data/orchestrator.db` database:

```sql
CREATE TABLE agent_lifecycle (
    -- Primary identification
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pid INTEGER NOT NULL,
    agent_type TEXT NOT NULL,  -- architect, code_developer, project_manager
    task_id TEXT NOT NULL,     -- Links to tasks.task_id if applicable
    task_type TEXT,            -- create_spec, implementation, auto_planning
    priority_number INTEGER,   -- ROADMAP priority number (if applicable)

    -- Lifecycle timestamps (ISO8601 format)
    spawned_at TEXT NOT NULL,  -- When process was spawned
    started_at TEXT,           -- When agent began working (may differ from spawn)
    completed_at TEXT,         -- When agent finished (success or failure)

    -- Status and metrics
    status TEXT NOT NULL,      -- spawned, running, completed, failed, killed
    exit_code INTEGER,         -- Process exit code (NULL if still running)
    duration_ms INTEGER,       -- Total time from spawn to completion
    idle_time_ms INTEGER,      -- Time spent idle (spawned but not started)

    -- Additional context
    command TEXT NOT NULL,     -- Full CLI command executed
    worktree_path TEXT,        -- Git worktree path (for parallel execution)
    error_message TEXT,        -- Error details if failed
    metadata TEXT              -- JSON blob for additional context
);

-- Indexes for fast queries
CREATE INDEX idx_agent_type_status ON agent_lifecycle(agent_type, status);
CREATE INDEX idx_priority_number ON agent_lifecycle(priority_number);
CREATE INDEX idx_spawned_at ON agent_lifecycle(spawned_at);
CREATE INDEX idx_duration ON agent_lifecycle(duration_ms DESC);
CREATE INDEX idx_task_id ON agent_lifecycle(task_id);
```

### 2. Analytics Views

#### Agent Velocity View
```sql
CREATE VIEW agent_velocity AS
SELECT
    agent_type,
    COUNT(*) AS total_agents,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
    AVG(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS avg_duration_ms,
    AVG(CASE WHEN status = 'completed' THEN idle_time_ms ELSE NULL END) AS avg_idle_ms,
    MAX(duration_ms) AS max_duration_ms,
    MIN(duration_ms) AS min_duration_ms
FROM agent_lifecycle
GROUP BY agent_type;
```

#### Agent Bottlenecks View
```sql
CREATE VIEW agent_bottlenecks AS
SELECT
    agent_id,
    agent_type,
    task_id,
    priority_number,
    duration_ms,
    idle_time_ms,
    spawned_at,
    completed_at,
    CASE
        WHEN idle_time_ms > duration_ms * 0.5 THEN 'High Idle Time'
        WHEN duration_ms > 1800000 THEN 'Long Duration'  -- >30 minutes
        ELSE 'Normal'
    END AS bottleneck_type
FROM agent_lifecycle
WHERE status = 'completed' AND duration_ms IS NOT NULL
ORDER BY duration_ms DESC
LIMIT 100;
```

#### Priority Implementation Timeline View
```sql
CREATE VIEW priority_timeline AS
SELECT
    priority_number,
    agent_type,
    MIN(spawned_at) AS first_spawn,
    MAX(completed_at) AS last_completion,
    COUNT(*) AS agent_count,
    SUM(duration_ms) AS total_time_ms,
    AVG(duration_ms) AS avg_time_ms
FROM agent_lifecycle
WHERE priority_number IS NOT NULL
GROUP BY priority_number, agent_type
ORDER BY priority_number;
```

#### Current Active Agents View
```sql
CREATE VIEW active_agents AS
SELECT
    agent_id,
    pid,
    agent_type,
    task_id,
    priority_number,
    status,
    spawned_at,
    CAST((julianday('now') - julianday(spawned_at)) * 86400000 AS INTEGER) AS elapsed_ms
FROM agent_lifecycle
WHERE status IN ('spawned', 'running')
ORDER BY spawned_at;
```

## Implementation Plan

### Phase 1: Schema Migration (PRIORITY)
1. Add `agent_lifecycle` table to `data/orchestrator.db`
2. Create migration script to populate from existing `agent_state.json`
3. Add views for analytics

### Phase 2: Agent Management Integration
1. Update `agent_management.py` to write to SQLite on spawn
2. Update `_check_status()` to update lifecycle timestamps
3. Update `_list_active_agents()` to query from SQLite
4. Maintain JSON file for backward compatibility (read-only)

### Phase 3: Dashboard & Analytics
1. Update `dashboard.py` to use SQLite queries
2. Add velocity metrics panel to dashboard
3. Create CLI command for bottleneck analysis
4. Export functionality for Langfuse integration

### Phase 4: Cleanup & Deprecation
1. Remove JSON write operations from agent management
2. Archive historical `agent_state.json` data
3. Update documentation

## Benefits

1. **Velocity Analysis**: Track implementation speed per agent type, priority
2. **Bottleneck Detection**: Identify slow agents, excessive idle time
3. **Historical Tracking**: Retain 30+ days of agent performance data
4. **Consistent Storage**: All orchestrator data in single SQLite database
5. **Analytics**: SQL queries for business intelligence
6. **Scalability**: SQLite handles 10,000+ agent records efficiently

## Metrics to Track

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| **Agent Velocity** | Completed agents / hour | Measure throughput |
| **Avg Duration** | AVG(duration_ms) per agent_type | Baseline performance |
| **Idle Time** | spawned_at → started_at | Detect scheduling inefficiencies |
| **Success Rate** | completed / total | Quality metric |
| **Priority Throughput** | Priorities completed / day | User-facing metric |
| **Bottlenecks** | Agents with duration > 95th percentile | Optimization targets |

## Example Queries

### Find slow architect specs
```sql
SELECT priority_number, duration_ms / 60000 AS duration_minutes
FROM agent_lifecycle
WHERE agent_type = 'architect' AND status = 'completed'
ORDER BY duration_ms DESC
LIMIT 10;
```

### Calculate hourly velocity
```sql
SELECT
    strftime('%Y-%m-%d %H:00', spawned_at) AS hour,
    COUNT(*) AS spawned,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed
FROM agent_lifecycle
WHERE spawned_at > datetime('now', '-24 hours')
GROUP BY hour
ORDER BY hour;
```

### Find priorities with high idle time
```sql
SELECT priority_number, AVG(idle_time_ms) / 1000 AS avg_idle_seconds
FROM agent_lifecycle
WHERE priority_number IS NOT NULL AND idle_time_ms IS NOT NULL
GROUP BY priority_number
HAVING avg_idle_seconds > 60  -- >1 minute idle
ORDER BY avg_idle_seconds DESC;
```

## Acceptance Criteria

1. ✅ `agent_lifecycle` table created in `data/orchestrator.db`
2. ✅ All agent spawns write lifecycle event to SQLite
3. ✅ All status changes update lifecycle record
4. ✅ Dashboard shows only active agents from SQLite
5. ✅ Analytics views accessible via SQL queries
6. ✅ Historical JSON data migrated to SQLite
7. ✅ CLI command for velocity report (`orchestrator-velocity`)

## References

- Existing schema: `coffee_maker/autonomous/message_queue.py:167-238`
- Agent management: `.claude/skills/shared/orchestrator-agent-management/agent_management.py`
- Dashboard: `coffee_maker/orchestrator/dashboard.py`
- CFR-015: Orchestrator Database Tracing
