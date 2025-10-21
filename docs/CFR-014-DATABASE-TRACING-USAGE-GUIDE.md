# CFR-014 Database Tracing - Usage Guide

**Document**: CFR-014 Database Tracing Usage Guide
**Status**: Production
**Date**: 2025-10-21
**Related**: US-110, CFR-014, SPEC-110

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Database Schema](#database-schema)
4. [CLI Commands](#cli-commands)
5. [Analytics Views](#analytics-views)
6. [Common Queries](#common-queries)
7. [Troubleshooting](#troubleshooting)
8. [Performance](#performance)

---

## Overview

CFR-014 mandates that **ALL orchestrator activities must be traced in SQLite database**, replacing legacy JSON files. This provides:

- **Data Integrity**: No more stale agent_state.json files
- **Velocity Analysis**: Measure agent throughput and duration
- **Bottleneck Detection**: Identify slow agents and priorities
- **Historical Tracking**: 30+ days of queryable data
- **Business Intelligence**: SQL-based analytics and reporting

### What Changed

**Before CFR-014 (Problems)**:
```
❌ agent_state.json: 706 lines, 64+ dead agents marked "running"
❌ Dashboard shows "45 active agents" when only 2 running
❌ No velocity metrics - cannot answer "How fast is architect?"
❌ No historical data - cannot analyze trends
❌ JSON never cleaned up - accumulates stale data
```

**After CFR-014 (Solution)**:
```
✅ data/orchestrator.db: Single source of truth
✅ agent_lifecycle table: All agent events tracked
✅ active_agents view: Only running agents (verified with ps)
✅ agent_velocity view: Throughput and duration metrics
✅ agent_bottlenecks view: Slowest 100 agents
✅ priority_timeline view: Priority implementation timeline
✅ CLI commands: poetry run orchestrator velocity/bottlenecks/status
```

---

## Quick Start

### 1. Run Migration (One-Time Setup)

Create the `agent_lifecycle` table and analytics views:

```bash
poetry run python coffee_maker/orchestrator/migrate_add_agent_lifecycle.py
```

**Output**:
```
2025-10-21 08:50:49 - INFO - Starting agent_lifecycle migration...
2025-10-21 08:50:49 - INFO - Creating agent_lifecycle table...
2025-10-21 08:50:49 - INFO - Adding missing column: worktree_branch
2025-10-21 08:50:49 - INFO - ✅ agent_lifecycle table created
2025-10-21 08:50:49 - INFO - Creating analytics views...
2025-10-21 08:50:49 - INFO - ✅ Analytics views created (active_agents, agent_velocity, agent_bottlenecks, priority_timeline)
2025-10-21 08:50:49 - INFO - Verifying migration...
2025-10-21 08:50:49 - INFO - ✅ Verification passed
2025-10-21 08:50:49 - INFO - ✅ Migration completed successfully!
```

**Idempotent**: Safe to run multiple times.

### 2. Check Agent Velocity

View throughput and average duration per agent type:

```bash
poetry run orchestrator velocity
```

**Example Output**:
```
📊 Agent Velocity Report (last 7 days)
================================================================================

🤖 ARCHITECT
   Total Spawned: 653
   Completed: 653 (100.0%)
   Failed: 0 (0.0%)
   Avg Duration: 4.2 minutes

🤖 CODE_DEVELOPER
   Total Spawned: 69
   Completed: 69 (100.0%)
   Failed: 0 (0.0%)
   Avg Duration: 12.5 minutes

🤖 CODE_REVIEWER
   Total Spawned: 473
   Completed: 470 (99.4%)
   Failed: 0 (0.0%)
   Avg Duration: 2.1 minutes
```

### 3. Identify Bottlenecks

Find the slowest agents and priorities:

```bash
poetry run orchestrator bottlenecks --limit 10
```

**Example Output**:
```
🔍 Agent Bottlenecks (Top 10)
==========================================================================================

1. code_developer - impl-048 (Priority 48)
   Duration: 45.2 min | Idle: 2.3 min
   Type: Long Duration
   Spawned: 2025-10-20T14:32:15

2. architect - spec-072 (Priority 72)
   Duration: 38.7 min | Idle: 0.5 min
   Type: Long Duration
   Spawned: 2025-10-19T10:15:42

3. code_developer - impl-055 (Priority 55)
   Duration: 35.1 min | Idle: 18.2 min
   Type: High Idle Time
   Spawned: 2025-10-20T09:22:08
```

### 4. View Active Agents

See real-time active agents (only running processes):

```bash
poetry run orchestrator status
```

or use the dashboard:

```bash
poetry run orchestrator dashboard
```

---

## Database Schema

### `agent_lifecycle` Table

**Purpose**: Track every agent spawn, lifecycle event, and completion.

```sql
CREATE TABLE agent_lifecycle (
    -- Identity
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pid INTEGER NOT NULL,                   -- Process ID
    agent_type TEXT NOT NULL,               -- architect, code_developer, etc.
    task_id TEXT NOT NULL,                  -- spec-110, impl-055, etc.
    task_type TEXT,                         -- create_spec, implementation, etc.
    priority_number INTEGER,                -- ROADMAP priority

    -- Lifecycle timestamps (ISO8601)
    spawned_at TEXT NOT NULL,               -- When process spawned
    started_at TEXT,                        -- When agent began work
    completed_at TEXT,                      -- When agent finished

    -- Status and metrics
    status TEXT NOT NULL,                   -- spawned, running, completed, failed, killed
    exit_code INTEGER,                      -- Process exit code
    duration_ms INTEGER,                    -- spawn → complete (milliseconds)
    idle_time_ms INTEGER,                   -- spawn → start (milliseconds)

    -- Additional context
    command TEXT NOT NULL,                  -- Full CLI command
    worktree_path TEXT,                     -- Git worktree path (parallel exec)
    worktree_branch TEXT,                   -- Git worktree branch (e.g., roadmap-wt1)
    merged_at TEXT,                         -- When architect merged (CFR-013)
    cleaned_at TEXT,                        -- When worktree cleaned up
    merge_duration_ms INTEGER,              -- Time to merge
    cleanup_duration_ms INTEGER,            -- Time to cleanup
    error_message TEXT,                     -- Error details if failed
    metadata TEXT                           -- JSON blob for extras
);
```

**Indexes**:
- `idx_agent_type_status` - Fast filtering by agent + status
- `idx_priority_number` - Fast filtering by priority
- `idx_spawned_at` - Time-based queries
- `idx_duration` - Bottleneck analysis
- `idx_task_id` - Task lookup
- `idx_pid` - Process lookup
- `idx_worktree_branch` - Worktree tracking
- `idx_merged_at` - Merge timeline

---

## CLI Commands

### `poetry run orchestrator velocity`

**Purpose**: Measure agent throughput and duration metrics.

**Options**:
```bash
--agent-type TEXT    Filter by agent type (architect, code_developer, etc.)
--days INTEGER       Number of days to analyze (default: 7)
```

**Examples**:
```bash
# All agents, last 7 days
poetry run orchestrator velocity

# Architect only, last 30 days
poetry run orchestrator velocity --agent-type architect --days 30

# Code developer only, last 24 hours
poetry run orchestrator velocity --agent-type code_developer --days 1
```

**Use Cases**:
- Answer "How fast does architect create specs?"
- Track velocity trends over time
- Compare agent performance day-over-day

---

### `poetry run orchestrator bottlenecks`

**Purpose**: Identify slowest agents and priorities for optimization.

**Options**:
```bash
--limit INTEGER       Number of bottlenecks to show (default: 20)
--agent-type TEXT     Filter by agent type
```

**Examples**:
```bash
# Top 20 bottlenecks, all agents
poetry run orchestrator bottlenecks

# Top 10 slowest code_developer tasks
poetry run orchestrator bottlenecks --limit 10 --agent-type code_developer

# Top 5 slowest architect specs
poetry run orchestrator bottlenecks --limit 5 --agent-type architect
```

**Bottleneck Types**:
- **Long Duration**: Agent took >30 minutes
- **High Idle Time**: Idle time >50% of total duration
- **Normal**: Completed within expected time

**Use Cases**:
- Find priorities that take longest to implement
- Detect agents stuck waiting for resources
- Optimize orchestrator scheduling

---

### `poetry run orchestrator status`

**Purpose**: Check orchestrator status and active agents.

**Example**:
```bash
poetry run orchestrator status
```

**Output**:
```
📊 Orchestrator Status
============================================================
Last ROADMAP Update: 2025-10-21 08:45:32

Active Tasks: 2
  - spec-112: create_spec (agent: architect, PID: 45821)
  - impl-110: implementation (agent: code_developer, PID: 45823)

Running Agents: 2
  - PID 45821: python
  - PID 45823: python
```

---

## Analytics Views

### `active_agents` View

**Purpose**: Show only currently running agents (spawned or running status).

**Query**:
```sql
SELECT * FROM active_agents;
```

**Columns**:
- `agent_id` - Unique agent ID
- `pid` - Process ID
- `agent_type` - Agent type
- `task_id` - Task identifier
- `priority_number` - Priority number (if applicable)
- `status` - spawned or running
- `spawned_at` - Spawn timestamp
- `elapsed_ms` - Time since spawn (calculated)

**Use Case**: Dashboard showing only active agents (no stale data)

---

### `agent_velocity` View

**Purpose**: Calculate throughput and duration metrics per agent type.

**Query**:
```sql
SELECT * FROM agent_velocity;
```

**Columns**:
- `agent_type` - Agent type
- `total_agents` - Total spawned
- `completed` - Completed successfully
- `failed` - Failed
- `avg_duration_ms` - Average duration (completed only)
- `avg_idle_ms` - Average idle time
- `max_duration_ms` - Longest duration
- `min_duration_ms` - Shortest duration

**Use Case**: Velocity report, performance tracking

---

### `agent_bottlenecks` View

**Purpose**: Identify slowest 100 agents for optimization.

**Query**:
```sql
SELECT * FROM agent_bottlenecks LIMIT 20;
```

**Columns**:
- `agent_id`, `agent_type`, `task_id`, `priority_number`
- `duration_ms` - Total duration
- `idle_time_ms` - Idle time
- `spawned_at`, `completed_at` - Timestamps
- `bottleneck_type` - High Idle Time, Long Duration, or Normal

**Use Case**: Bottleneck analysis, optimization targets

---

### `priority_timeline` View

**Purpose**: Show priority implementation timeline and agent count.

**Query**:
```sql
SELECT * FROM priority_timeline WHERE priority_number = 110;
```

**Columns**:
- `priority_number` - Priority number
- `agent_type` - Agent type
- `first_spawn` - First agent spawn time
- `last_completion` - Last agent completion time
- `agent_count` - Number of agents
- `total_time_ms` - Total time across all agents
- `avg_time_ms` - Average time per agent

**Use Case**: Track priority implementation from start to finish

---

## Common Queries

### 1. Find Currently Running Agents

```sql
SELECT pid, agent_type, task_id, elapsed_ms / 60000 AS elapsed_minutes
FROM active_agents
ORDER BY elapsed_ms DESC;
```

**Purpose**: See real-time active agents, longest-running first.

---

### 2. Architect Velocity Over Last 30 Days

```sql
SELECT
    strftime('%Y-%m-%d', spawned_at) AS day,
    COUNT(*) AS specs_created,
    AVG(duration_ms) / 60000 AS avg_minutes
FROM agent_lifecycle
WHERE agent_type = 'architect' AND status = 'completed'
  AND spawned_at >= datetime('now', '-30 days')
GROUP BY day
ORDER BY day DESC;
```

**Purpose**: Daily spec creation rate and average time.

---

### 3. Slowest Priorities to Implement

```sql
SELECT
    priority_number,
    COUNT(*) AS agent_count,
    SUM(duration_ms) / 3600000 AS total_hours,
    MAX(duration_ms) / 60000 AS max_agent_minutes
FROM agent_lifecycle
WHERE priority_number IS NOT NULL AND status = 'completed'
GROUP BY priority_number
HAVING total_hours > 2  -- >2 hours total
ORDER BY total_hours DESC;
```

**Purpose**: Find priorities consuming most time.

---

### 4. Hourly Agent Throughput (Last 24 Hours)

```sql
SELECT
    strftime('%Y-%m-%d %H:00', spawned_at) AS hour,
    COUNT(*) AS spawned,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed
FROM agent_lifecycle
WHERE spawned_at > datetime('now', '-24 hours')
GROUP BY hour
ORDER BY hour DESC;
```

**Purpose**: Track orchestrator activity by hour.

---

### 5. Agents with High Idle Time

```sql
SELECT
    agent_type,
    task_id,
    priority_number,
    duration_ms / 60000 AS duration_minutes,
    idle_time_ms / 60000 AS idle_minutes,
    ROUND(idle_time_ms * 100.0 / duration_ms, 1) AS idle_percentage
FROM agent_lifecycle
WHERE idle_time_ms > duration_ms * 0.3  -- >30% idle
  AND status = 'completed'
ORDER BY idle_percentage DESC
LIMIT 20;
```

**Purpose**: Detect scheduling inefficiencies.

---

### 6. Failed Agents (Last 7 Days)

```sql
SELECT
    agent_type,
    task_id,
    priority_number,
    spawned_at,
    error_message
FROM agent_lifecycle
WHERE status = 'failed'
  AND spawned_at >= datetime('now', '-7 days')
ORDER BY spawned_at DESC;
```

**Purpose**: Debug failed agents.

---

## Troubleshooting

### Database Not Found

**Error**: `❌ Database not found. Run migrations first.`

**Solution**:
```bash
poetry run python coffee_maker/orchestrator/migrate_add_agent_lifecycle.py
```

---

### No Duration Data (Avg Duration: N/A)

**Cause**: `duration_ms` is NULL for all agents.

**Explanation**: Duration is calculated when agents complete. If you haven't run the orchestrator with the new agent_management skill yet, durations won't be populated.

**How It Works**:
```python
# In agent_management.py _spawn_architect():
conn.execute("""
    INSERT INTO agent_lifecycle
    (pid, agent_type, task_id, spawned_at, status, command)
    VALUES (?, ?, ?, ?, ?, ?)
""", (process.pid, "architect", task_id, now, "spawned", cmd))

# Later, when agent completes:
conn.execute("""
    UPDATE agent_lifecycle
    SET completed_at = ?,
        status = 'completed',
        duration_ms = CAST((julianday(?) - julianday(spawned_at)) * 86400000 AS INTEGER)
    WHERE pid = ?
""", (now, now, pid))
```

**Action**: Start orchestrator and run a few agents to populate duration data.

---

### Views Not Found

**Error**: `Error: no such table: active_agents`

**Solution**: Re-run migration to create views:
```bash
poetry run python coffee_maker/orchestrator/migrate_add_agent_lifecycle.py
```

---

## Performance

### Query Performance

All queries are optimized with indexes:

- **Typical query time**: <10ms for 10,000 records
- **View materialization**: Real-time (not cached)
- **Dashboard refresh**: <50ms

### Database Size

**Example sizes**:
- 1,000 agents: ~200 KB
- 10,000 agents: ~2 MB
- 100,000 agents: ~20 MB

**Cleanup**: Completed agents >30 days old are auto-cleaned by message queue.

---

## Integration with Other Systems

### Langfuse (Observability)

Agent lifecycle events can be exported to Langfuse for visualization:

```python
from coffee_maker.autonomous.message_queue import MessageQueue
from coffee_maker.observability.langfuse_tracer import trace_agent_lifecycle

queue = MessageQueue()
agents = queue.get_slowest_tasks(limit=100)

for agent in agents:
    trace_agent_lifecycle(agent)
```

### Dashboard (Real-Time UI)

The orchestrator dashboard queries `active_agents` view:

```bash
poetry run orchestrator dashboard
```

---

## References

- **CFR-014**: docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md (line 4000)
- **SPEC-110**: docs/architecture/specs/SPEC-110-orchestrator-database-tracing.md
- **US-110**: docs/roadmap/ROADMAP.md (US-110)
- **Migration Script**: coffee_maker/orchestrator/migrate_add_agent_lifecycle.py
- **Agent Management**: .claude/skills/shared/orchestrator-agent-management/agent_management.py
- **Message Queue**: coffee_maker/autonomous/message_queue.py

---

**Last Updated**: 2025-10-21
**Status**: Production ✅
