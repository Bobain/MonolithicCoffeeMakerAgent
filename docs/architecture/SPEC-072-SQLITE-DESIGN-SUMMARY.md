# SPEC-072 SQLite Design Summary

**Date**: 2025-10-18
**Author**: architect agent
**Status**: Complete

---

## Executive Summary

**SPEC-072** has been successfully updated to use **SQLite** as the message queue and metrics database for the Multi-Agent Orchestration Daemon. This design leverages existing Python stdlib (no external dependencies) while providing **persistence**, **built-in analytics**, and **historical metrics** that the in-memory approach could not offer.

**Key Decision**: Replace in-memory queue (multiprocessing.Queue + heapq) with SQLite-based architecture.

**User Request**: "Can't we use SQLite to make a quick and easy message queue system for the orchestrator? We already have SQLite and the orchestrator could add metrics, analytics to the db."

---

## Architecture Change

### Before (In-Memory)

```
multiprocessing.Queue + heapq
├── Priority heap (in-memory)
├── Task metadata (dict)
└── Bottleneck tracking (heapq)

Trade-offs:
❌ No persistence (messages lost on crash)
❌ Manual bottleneck tracking (heapq)
❌ No historical metrics
```

### After (SQLite)

```
SQLite with WAL mode (data/orchestrator.db)
├── tasks table (message queue + history)
├── agent_metrics table (performance tracking)
├── bottlenecks view (top 100 slowest tasks)
├── agent_performance view (aggregated stats)
└── queue_depth view (current queue by agent/priority)

Benefits:
✅ Persistence (messages survive daemon crashes)
✅ Built-in analytics (SQL queries)
✅ Historical metrics (30-day retention)
✅ Thread-safe (WAL mode)
✅ Zero external dependencies (Python stdlib)
```

---

## Schema Design

### 1. Tasks Table (Message Queue + History)

```sql
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    type TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 5,  -- 1=highest, 10=lowest
    status TEXT NOT NULL DEFAULT 'queued',  -- queued, running, completed, failed
    payload TEXT NOT NULL,  -- JSON-encoded dict
    created_at TEXT NOT NULL,  -- ISO8601 timestamp
    started_at TEXT,  -- ISO8601 timestamp (nullable)
    completed_at TEXT,  -- ISO8601 timestamp (nullable)
    duration_ms INTEGER,  -- Duration in milliseconds (nullable)
    error_message TEXT  -- Error details if failed (nullable)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_duration ON tasks(duration_ms DESC);
CREATE INDEX IF NOT EXISTS idx_recipient_status ON tasks(recipient, status);
CREATE INDEX IF NOT EXISTS idx_status ON tasks(status);
```

**Purpose**:
- **Message Queue**: Stores queued tasks (status='queued')
- **Historical Data**: Stores completed/failed tasks for analytics
- **Duration Tracking**: Records start/completion timestamps and duration

**Query Examples**:
```sql
-- Get next task for code_developer (priority queue)
SELECT * FROM tasks
WHERE recipient = 'code_developer' AND status = 'queued'
ORDER BY priority ASC, created_at ASC
LIMIT 1;

-- Get slowest 10 tasks (bottleneck analysis)
SELECT * FROM tasks
WHERE status = 'completed' AND duration_ms IS NOT NULL
ORDER BY duration_ms DESC
LIMIT 10;
```

---

### 2. Agent Metrics Table (Performance Tracking)

```sql
CREATE TABLE IF NOT EXISTS agent_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT NOT NULL,
    metric_name TEXT NOT NULL,  -- tasks_completed, avg_duration, cpu_percent, memory_mb
    metric_value REAL NOT NULL,
    timestamp TEXT NOT NULL  -- ISO8601 timestamp
);

-- Index for metrics queries
CREATE INDEX IF NOT EXISTS idx_agent_metric ON agent_metrics(agent, metric_name, timestamp);
```

**Purpose**:
- Store agent performance metrics over time
- Enable trend analysis (week-over-week comparisons)
- Track CPU, memory, task completion rates

**Usage**:
```python
# Record metric
queue.record_metric("code_developer", "cpu_percent", 45.2)
queue.record_metric("code_developer", "memory_mb", 128.5)
```

**Query Examples**:
```sql
-- Get CPU usage trend for code_developer (last 24 hours)
SELECT timestamp, metric_value
FROM agent_metrics
WHERE agent = 'code_developer'
  AND metric_name = 'cpu_percent'
  AND timestamp >= datetime('now', '-1 day')
ORDER BY timestamp;
```

---

### 3. Bottlenecks View (Top 100 Slowest Tasks)

```sql
CREATE VIEW IF NOT EXISTS bottlenecks AS
SELECT task_id, recipient AS agent, type, duration_ms, created_at, started_at, completed_at
FROM tasks
WHERE status = 'completed' AND duration_ms IS NOT NULL
ORDER BY duration_ms DESC
LIMIT 100;
```

**Purpose**: Pre-computed view of slowest tasks for quick bottleneck analysis

**Usage**:
```python
slowest = queue.get_slowest_tasks(limit=10)
# → [{task_id, agent, type, duration_ms, created_at, started_at, completed_at}, ...]
```

---

### 4. Agent Performance View (Aggregated Stats)

```sql
CREATE VIEW IF NOT EXISTS agent_performance AS
SELECT
    recipient AS agent,
    COUNT(*) AS total_tasks,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_tasks,
    AVG(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS avg_duration_ms,
    MAX(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS max_duration_ms,
    MIN(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS min_duration_ms
FROM tasks
GROUP BY recipient;
```

**Purpose**: Aggregated performance metrics per agent

**Usage**:
```python
performance = queue.get_agent_performance()
# → [{
#   "agent": "code_developer",
#   "total_tasks": 156,
#   "completed_tasks": 153,
#   "failed_tasks": 3,
#   "avg_duration_ms": 2300,
#   "max_duration_ms": 45000,
#   "min_duration_ms": 120
# }, ...]
```

---

### 5. Queue Depth View (Current Queue by Agent/Priority)

```sql
CREATE VIEW IF NOT EXISTS queue_depth AS
SELECT
    recipient AS agent,
    COUNT(*) AS queued_tasks,
    SUM(CASE WHEN priority <= 2 THEN 1 ELSE 0 END) AS high_priority,
    SUM(CASE WHEN priority BETWEEN 3 AND 7 THEN 1 ELSE 0 END) AS normal_priority,
    SUM(CASE WHEN priority >= 8 THEN 1 ELSE 0 END) AS low_priority
FROM tasks
WHERE status = 'queued'
GROUP BY recipient;
```

**Purpose**: Real-time queue depth monitoring by agent and priority level

**Usage**:
```python
queue_depth = queue.get_queue_depth()
# → [{
#   "agent": "code_developer",
#   "queued_tasks": 5,
#   "high_priority": 2,
#   "normal_priority": 2,
#   "low_priority": 1
# }, ...]
```

---

## Python API

### MessageQueue Class

```python
class MessageQueue:
    """SQLite-based inter-agent communication queue with persistence and metrics."""

    def __init__(self, db_path: str = "data/orchestrator.db"):
        """Initialize SQLite message queue."""
        self.db_path = Path(db_path)
        self._init_schema()  # Create tables, indexes, views

    def send(self, message: Message) -> None:
        """Send message to recipient's queue with priority."""
        # INSERT INTO tasks (...) VALUES (...)

    def get(self, recipient: str, timeout: float = 1.0) -> Optional[Message]:
        """Get next message for recipient (highest priority first)."""
        # SELECT * FROM tasks WHERE recipient = ? AND status = 'queued'
        # ORDER BY priority ASC, created_at ASC LIMIT 1

    def mark_started(self, task_id: str, agent: str) -> None:
        """Mark task as started, record start time."""
        # UPDATE tasks SET status = 'running', started_at = ? WHERE task_id = ?

    def mark_completed(self, task_id: str, duration_ms: int) -> None:
        """Mark task as completed, record duration."""
        # UPDATE tasks SET status = 'completed', completed_at = ?, duration_ms = ?

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """Mark task as failed, record error message."""
        # UPDATE tasks SET status = 'failed', error_message = ? WHERE task_id = ?

    def get_slowest_tasks(self, limit: int = 10) -> List[dict]:
        """Get slowest tasks for bottleneck analysis."""
        # SELECT * FROM bottlenecks LIMIT ?

    def get_agent_performance(self) -> List[dict]:
        """Get aggregated performance metrics per agent."""
        # SELECT * FROM agent_performance

    def get_queue_depth(self) -> List[dict]:
        """Get current queue depth by agent and priority."""
        # SELECT * FROM queue_depth

    def record_metric(self, agent: str, metric_name: str, metric_value: float) -> None:
        """Record performance metric for agent."""
        # INSERT INTO agent_metrics (...) VALUES (...)

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """Clean up completed tasks older than N days."""
        # DELETE FROM tasks WHERE status IN ('completed', 'failed')
        # AND completed_at < datetime('now', '-{days} days')
```

---

## Benefits of SQLite Approach

### 1. Persistence (Crash Recovery)

**Problem**: In-memory queue loses messages on daemon crash
**Solution**: SQLite writes messages to disk immediately

```python
# Before daemon crash:
queue.send(Message(sender="architect", recipient="code_developer", ...))
# Daemon crashes...
# After daemon restart:
message = queue.get("code_developer")  # ✅ Message still there!
```

### 2. Built-in Analytics (SQL Queries)

**Problem**: In-memory approach requires manual heapq tracking
**Solution**: SQL queries on indexed columns

```python
# Get slowest tasks (no manual heapq tracking)
slowest = queue.get_slowest_tasks(limit=10)
# SQL: SELECT * FROM bottlenecks LIMIT 10

# Get average duration per agent
performance = queue.get_agent_performance()
# SQL: SELECT agent, AVG(duration_ms) FROM tasks GROUP BY agent
```

### 3. Historical Metrics (Trend Analysis)

**Problem**: In-memory approach loses history on restart
**Solution**: SQLite retains 30 days of task history

```sql
-- Compare this week vs. last week
SELECT
    DATE(created_at) AS date,
    AVG(duration_ms) AS avg_duration
FROM tasks
WHERE status = 'completed'
  AND created_at >= datetime('now', '-14 days')
GROUP BY DATE(created_at)
ORDER BY date;
```

### 4. Thread-Safe (WAL Mode)

**Problem**: In-memory approach requires complex locking
**Solution**: SQLite WAL mode enables concurrent reads/writes

```python
# WAL mode configuration
conn.execute("PRAGMA journal_mode = WAL")
conn.execute("PRAGMA synchronous = NORMAL")

# Multiple agents can read concurrently
# Writes don't block reads
```

### 5. Zero External Dependencies

**Problem**: Redis requires external server + package
**Solution**: SQLite is Python stdlib (no installation)

```python
import sqlite3  # ✅ Python 3.11 stdlib
# No poetry add, no server setup, no configuration
```

### 6. Simple Queries (No Manual Calculations)

**Problem**: In-memory approach requires manual percentile calculations
**Solution**: SQL queries with built-in sorting

```sql
-- 95th percentile duration (no manual sorting)
SELECT duration_ms
FROM tasks
WHERE status = 'completed' AND duration_ms IS NOT NULL
ORDER BY duration_ms
LIMIT 1 OFFSET (
    SELECT CAST(COUNT(*) * 0.95 AS INTEGER)
    FROM tasks
    WHERE status = 'completed' AND duration_ms IS NOT NULL
);
```

### 7. Aggregation (GROUP BY Queries)

**Problem**: In-memory approach requires manual aggregation loops
**Solution**: SQL GROUP BY with aggregate functions

```sql
-- Analyze bottlenecks by task type
SELECT
    type,
    COUNT(*) AS total,
    AVG(duration_ms) AS avg_duration,
    MAX(duration_ms) AS max_duration
FROM tasks
WHERE status = 'completed' AND duration_ms IS NOT NULL
GROUP BY type
ORDER BY avg_duration DESC;
```

---

## Trade-offs

### Accepted Trade-off 1: Disk I/O Overhead

**Impact**: ~1-2ms per operation (vs. <1ms for in-memory)
**Mitigation**: WAL mode minimizes disk writes (batches writes)
**Acceptable**: 1-2ms latency is negligible for inter-agent messaging

### Accepted Trade-off 2: Single-Machine Only

**Impact**: No distributed coordination (same as in-memory approach)
**Justification**: SPEC-072 targets single-machine orchestration only
**Future**: If distributed coordination needed, migrate to Redis/PostgreSQL

---

## CLI Commands

```bash
# View bottleneck analysis
poetry run team-daemon bottlenecks
# Output:
# Top 10 Slowest Tasks:
# 1. task_abc123 (code_developer): 45,000ms - implement_feature
# 2. task_def456 (architect): 32,000ms - create_spec
# ...

# View agent performance metrics
poetry run team-daemon metrics --agent code_developer
# Output:
# code_developer Performance:
# - Tasks completed: 156
# - Tasks failed: 3
# - Average duration: 2,300ms
# - p95 duration: 8,500ms
# - Current queue depth: 5 (high: 2, normal: 2, low: 1)

# View queue depth
poetry run team-daemon queue
# Output:
# Queue Depth by Agent:
# code_developer: 5 tasks (2 high, 2 normal, 1 low)
# architect: 2 tasks (1 high, 1 normal, 0 low)
# ...

# View task completion events (last 100)
poetry run team-daemon events --tail 100
```

---

## Implementation Effort

### Updated Estimate: 18-26 hours (increased from 16-24)

**Breakdown**:

**Phase 1: Core Infrastructure** (14-18 hours)
- Day 1-2: Team Daemon Framework (8-10 hours) - unchanged
- **Day 3: SQLite Message Queue (4-5 hours)** ⭐ NEW
  - Create SQLite schema (tasks, agent_metrics, views)
  - Implement MessageQueue class with SQLite backend
  - Add indexes for fast queries
  - Enable WAL mode for thread-safe concurrent access
- Day 4: Testing & Integration (2-3 hours) - reduced (no heapq tests needed)

**Phase 2: Agent Daemons** (12-16 hours) - unchanged

**Phase 3: Coordination & Polish** (8-12 hours) - unchanged

**Additional Time**:
- SQLite schema design: +1-2 hours
- Index optimization: +30 min
- WAL mode configuration: +30 min
- Testing persistence: +1 hour

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Message Persistence** ⭐ NEW | 100% | Messages survive daemon crashes (SQLite on disk) |
| **Inter-Agent Latency** | <5ms | Message queue latency (SQLite with WAL mode) |
| **Bottleneck Detection** | <5 min | Time to identify slow tasks (SQL query on duration_ms) |
| **Historical Metrics** ⭐ NEW | 30 days | Metrics retained in SQLite (configurable) |
| **Analytics** ⭐ NEW | Real-time | SQL queries for bottlenecks, trends, aggregates |

**Improvements over In-Memory**:
- ✅ 100% message persistence (vs. 0% with in-memory)
- ✅ 30 days historical metrics (vs. 0 with in-memory)
- ✅ Real-time analytics (vs. manual heapq tracking)

---

## Example Usage

### Sending a Task

```python
from coffee_maker.autonomous.message_queue import MessageQueue, Message

queue = MessageQueue(db_path="data/orchestrator.db")

# Architect sends task to code_developer
queue.send(Message(
    sender="architect",
    recipient="code_developer",
    type="task_delegate",
    payload={"spec_id": "SPEC-071", "priority_name": "US-048"},
    priority=2,  # High priority
))
```

### Receiving and Processing a Task

```python
# code_developer gets next task
message = queue.get("code_developer")
if message:
    # Mark started
    queue.mark_started(message.task_id, agent="code_developer")

    # Do work
    start_time = time.time()
    implement_spec(message.payload["spec_id"])
    duration_ms = int((time.time() - start_time) * 1000)

    # Mark completed
    queue.mark_completed(message.task_id, duration_ms=duration_ms)
```

### Analyzing Bottlenecks

```python
# Get slowest tasks
slowest = queue.get_slowest_tasks(limit=10)
for task in slowest:
    print(f"{task['agent']}: {task['duration_ms']}ms - {task['type']}")

# Get agent performance
performance = queue.get_agent_performance()
for agent_perf in performance:
    print(f"{agent_perf['agent']}: avg={agent_perf['avg_duration_ms']}ms, "
          f"failed={agent_perf['failed_tasks']}/{agent_perf['total_tasks']}")

# Get queue depth
queue_depth = queue.get_queue_depth()
for agent_queue in queue_depth:
    print(f"{agent_queue['agent']}: {agent_queue['queued_tasks']} tasks "
          f"(high: {agent_queue['high_priority']}, "
          f"normal: {agent_queue['normal_priority']}, "
          f"low: {agent_queue['low_priority']})")
```

### Recording Metrics

```python
# Record agent metrics periodically
import psutil

process = psutil.Process()
queue.record_metric("code_developer", "cpu_percent", process.cpu_percent())
queue.record_metric("code_developer", "memory_mb", process.memory_info().rss / 1024 / 1024)
```

---

## Testing Strategy

### Unit Tests

```python
def test_message_queue_persistence():
    """Test messages survive queue restart."""
    queue1 = MessageQueue(db_path="test_orchestrator.db")
    queue1.send(Message(sender="a", recipient="b", type="test", payload={}, priority=5))

    # Simulate daemon crash (create new queue instance)
    queue2 = MessageQueue(db_path="test_orchestrator.db")
    message = queue2.get("b")

    assert message is not None
    assert message.sender == "a"
    assert message.recipient == "b"

def test_priority_ordering():
    """Test messages returned in priority order."""
    queue = MessageQueue(db_path="test_orchestrator.db")
    queue.send(Message(sender="a", recipient="b", type="low", payload={}, priority=8))
    queue.send(Message(sender="a", recipient="b", type="high", payload={}, priority=2))
    queue.send(Message(sender="a", recipient="b", type="normal", payload={}, priority=5))

    msg1 = queue.get("b")
    assert msg1.type == "high"  # priority=2 (highest)

    msg2 = queue.get("b")
    assert msg2.type == "normal"  # priority=5

    msg3 = queue.get("b")
    assert msg3.type == "low"  # priority=8 (lowest)

def test_bottleneck_analysis():
    """Test slowest tasks query."""
    queue = MessageQueue(db_path="test_orchestrator.db")

    # Create tasks with different durations
    for i, duration in enumerate([1000, 5000, 2000, 10000, 3000]):
        msg = Message(sender="a", recipient="b", type=f"task_{i}", payload={}, priority=5)
        queue.send(msg)
        queue.mark_started(msg.task_id, agent="b")
        queue.mark_completed(msg.task_id, duration_ms=duration)

    # Get slowest tasks
    slowest = queue.get_slowest_tasks(limit=3)
    assert len(slowest) == 3
    assert slowest[0]["duration_ms"] == 10000  # Slowest
    assert slowest[1]["duration_ms"] == 5000
    assert slowest[2]["duration_ms"] == 3000
```

---

## Migration from In-Memory (POC-072)

**Good News**: API remains mostly compatible!

```python
# Before (POC-072 in-memory)
queue = MessageQueue()  # In-memory
queue.send(message)
message = queue.get(recipient)
queue.mark_completed(task_id, duration_ms)

# After (SPEC-072 SQLite)
queue = MessageQueue(db_path="data/orchestrator.db")  # ✅ SQLite
queue.send(message)  # ✅ Same API
message = queue.get(recipient)  # ✅ Same API
queue.mark_completed(task_id, duration_ms)  # ✅ Same API
```

**New Methods**:
```python
# New analytics methods (not in POC-072)
queue.get_slowest_tasks(limit=10)
queue.get_agent_performance()
queue.get_queue_depth()
queue.record_metric(agent, metric_name, metric_value)
queue.cleanup_old_tasks(days=30)
```

---

## Conclusion

**SPEC-072 SQLite Design** provides:

✅ **Persistence**: Messages survive daemon crashes (100% vs. 0% with in-memory)
✅ **Analytics**: SQL queries for bottlenecks (no manual heapq tracking)
✅ **Metrics**: Historical performance data (30-day retention)
✅ **Thread-Safe**: WAL mode enables concurrent reads/writes
✅ **Zero Dependencies**: SQLite is Python stdlib (no external packages)
✅ **Simple Queries**: Standard SQL (no complex data structures)
✅ **Aggregation**: GROUP BY queries (no manual loops)

**Estimated Effort**: 18-26 hours (slightly increased from 16-24 due to schema design)

**Next Steps**:
1. code_developer implements MessageQueue class (SQLite backend)
2. code_developer creates TeamDaemon (agent orchestration)
3. code_developer adds tests (persistence, priority, bottlenecks)
4. project_manager verifies DoD with Puppeteer testing

**Status**: ✅ SPEC-072 updated and committed to roadmap branch

---

**Created**: 2025-10-18
**Author**: architect agent
**Commit**: 8afedfb - spec: Update SPEC-072 to use SQLite for message queue + metrics
