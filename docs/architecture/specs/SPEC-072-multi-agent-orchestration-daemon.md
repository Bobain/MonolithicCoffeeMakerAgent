# SPEC-072: Multi-Agent Orchestration Daemon

**Status**: Draft (SQLite-Based Architecture)

**Created**: 2025-10-18

**Updated**: 2025-10-18 (Updated to SQLite-based message queue + metrics)

**Author**: architect agent

**Estimated Effort**: 2.5-3.5 days (18-26 hours) ⭐ ENHANCED (SQLite adds persistence + analytics)

**Priority**: CRITICAL - Foundation for autonomous team operation

---

## Executive Summary

Create a **master orchestration daemon** that runs ALL agents continuously in a coordinated, fault-tolerant manner. This daemon serves as the "operating system" for the autonomous development team, managing agent lifecycles, coordinating work, and ensuring the team operates 24/7 without human intervention.

**Key Capabilities**:
1. **Multi-Agent Execution**: Runs all agents concurrently (code_developer, project_manager, architect, assistant)
2. **Work Coordination**: Routes tasks to appropriate agents based on expertise
3. **Fault Tolerance**: Auto-restarts crashed agents, handles errors gracefully
4. **Health Monitoring**: Tracks agent status, performance, resource usage
5. **Priority Management**: Ensures high-priority work gets immediate attention
6. **Graceful Shutdown**: Clean cleanup of all agents on termination

**Architecture**:
- Master daemon process supervises all agent processes
- Each agent runs in isolated subprocess with its own event loop
- Shared message queue for inter-agent communication
- Centralized logging and monitoring
- Health checks every 30 seconds

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Architecture Overview](#architecture-overview)
3. [Component Specifications](#component-specifications)
4. [Agent Coordination](#agent-coordination)
5. [Implementation Plan](#implementation-plan)
6. [Testing Strategy](#testing-strategy)
7. [Rollout Plan](#rollout-plan)

---

## Problem Statement

### Current State (Fragmented)

```
# User must manually start each agent separately
poetry run code-developer --auto-approve      # Terminal 1
poetry run project-manager daemon             # Terminal 2
# architect: no daemon (manual invocation)
# assistant: no daemon (manual invocation)
```

**Pain Points**:
1. **Manual Coordination**: User must start/stop multiple processes manually
2. **No Fault Tolerance**: If one agent crashes, no automatic restart
3. **Fragmented Logging**: Each agent logs separately, hard to correlate events
4. **Resource Waste**: Agents may duplicate work or conflict
5. **No Priority Management**: All agents run independently, no coordination
6. **Limited Observability**: No single view of team health

### Desired State (Orchestrated)

```
# Single command starts entire autonomous team
poetry run team-daemon

# All agents run continuously:
# - code_developer: Implements ROADMAP priorities
# - project_manager: Monitors GitHub, sends notifications, updates ROADMAP
# - architect: Reviews ROADMAP weekly, creates specs proactively
# - assistant: Answers questions, creates demos, reports bugs

# Automatic coordination:
# - architect creates specs → code_developer implements
# - code_developer completes work → project_manager verifies DoD
# - assistant finds bugs → project_manager adds to ROADMAP
# - All agents collaborate seamlessly
```

**Benefits**:
1. **Single Command**: Start entire team with one command
2. **Automatic Coordination**: Agents communicate and delegate work
3. **Fault Tolerance**: Crashed agents auto-restart within 5 seconds
4. **Unified Logging**: All agent activity in one log stream
5. **Resource Optimization**: Shared connection pools, rate limiting
6. **Full Observability**: Real-time dashboard of team health

---

## Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATION DAEMON                  │
│                     (SupervisorProcess)                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │            Agent Process Manager                      │    │
│  │  - Spawns agent subprocesses                          │    │
│  │  - Monitors health (30s intervals)                    │    │
│  │  - Auto-restarts on crashes                           │    │
│  │  - Graceful shutdown on SIGTERM                       │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │            Message Queue (Inter-Agent Comm)           │    │
│  │  - Task delegation (architect → code_developer)       │    │
│  │  - Status updates (code_developer → project_manager)  │    │
│  │  - Bug reports (assistant → project_manager)          │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │            Shared Resources                           │    │
│  │  - HTTPConnectionPool (singleton)                     │    │
│  │  - GlobalRateTracker (singleton)                      │    │
│  │  - NotificationDB (shared)                            │    │
│  │  - AgentRegistry (singleton)                          │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↓               ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│code_developer│ │project_mgr   │ │ architect    │ │  assistant   │
│  Subprocess  │ │ Subprocess   │ │ Subprocess   │ │  Subprocess  │
│              │ │              │ │              │ │              │
│ - Implements │ │ - Monitors   │ │ - Creates    │ │ - Demos      │
│   ROADMAP    │ │   GitHub     │ │   specs      │ │ - Bug reports│
│ - Creates PRs│ │ - Sends      │ │ - Weekly     │ │ - Answers    │
│ - Runs tests │ │   notifs     │ │   reviews    │ │   questions  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### Process Hierarchy

```
team-daemon (PID 1000)
├── code_developer (PID 1001)
│   ├── Event Loop
│   ├── ROADMAP polling (every 60s)
│   └── Implementation cycle
│
├── project_manager (PID 1002)
│   ├── Event Loop
│   ├── GitHub polling (every 5 min)
│   └── Notification sending
│
├── architect (PID 1003)
│   ├── Event Loop
│   ├── ROADMAP review (weekly)
│   └── Spec creation
│
└── assistant (PID 1004)
    ├── Event Loop
    ├── Demo creation (on-demand)
    └── Bug detection
```

### Message Queue Architecture (SQLite-Based)

**Decision**: Use **SQLite** for message queue + metrics database - **Zero external dependencies**

**Rationale**: User preference for leveraging existing SQLite (already used by agents), with persistence and built-in analytics

**Benefits**:
- ✅ Zero external dependencies (SQLite is Python stdlib)
- ✅ **Persistence**: Messages survive daemon crashes
- ✅ **Built-in Analytics**: SQL queries for bottleneck analysis
- ✅ **Metrics Storage**: Historical data for performance tracking
- ✅ **Thread-Safe**: WAL mode enables concurrent reads/writes
- ✅ **Zero Configuration**: Just a file path (e.g., `data/orchestrator.db`)
- ✅ **Simple Queries**: `SELECT * FROM tasks ORDER BY duration_ms DESC LIMIT 10`
- ✅ **Aggregation**: `SELECT agent, AVG(duration_ms) FROM tasks GROUP BY agent`

**Trade-offs Accepted**:
- ⚠️ Single-machine only (no distributed coordination) - same as in-memory
- ⚠️ Disk I/O overhead (minimal with WAL mode, ~1-2ms per operation)

**Why SQLite > In-Memory**:
- ✅ Survives daemon crashes (messages not lost)
- ✅ Enables historical metrics (trend analysis over weeks)
- ✅ SQL queries for bottlenecks (no manual heapq tracking)
- ✅ Already available (Python 3.11 stdlib)

```
┌─────────────────────────────────────────────────────────────────┐
│                 SQLITE MESSAGE QUEUE + METRICS                  │
│                 (orchestrator.db with WAL mode)                 │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  TABLE: tasks (message queue + history)               │    │
│  │  - task_id (TEXT PRIMARY KEY)                          │    │
│  │  - sender (TEXT)                                       │    │
│  │  - recipient (TEXT)                                    │    │
│  │  - type (TEXT)                                         │    │
│  │  - priority (INTEGER, indexed for fast queries)       │    │
│  │  - status (TEXT) [queued, running, completed, failed]  │    │
│  │  - payload (TEXT, JSON)                                │    │
│  │  - created_at (TEXT, ISO8601)                          │    │
│  │  - started_at (TEXT, ISO8601, nullable)                │    │
│  │  - completed_at (TEXT, ISO8601, nullable)              │    │
│  │  - duration_ms (INTEGER, indexed for bottleneck query) │    │
│  │  - error_message (TEXT, nullable)                      │    │
│  │                                                        │    │
│  │  Indexes:                                              │    │
│  │  - idx_priority (priority, created_at) for fast dequeue│    │
│  │  - idx_duration (duration_ms DESC) for bottlenecks    │    │
│  │  - idx_recipient (recipient, status) for agent queries│    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  TABLE: agent_metrics (performance tracking)           │    │
│  │  - id (INTEGER PRIMARY KEY AUTOINCREMENT)              │    │
│  │  - agent (TEXT, indexed)                               │    │
│  │  - metric_name (TEXT) [tasks_completed, avg_duration,  │    │
│  │                        cpu_percent, memory_mb]         │    │
│  │  - metric_value (REAL)                                 │    │
│  │  - timestamp (TEXT, ISO8601)                           │    │
│  │                                                        │    │
│  │  Indexes:                                              │    │
│  │  - idx_agent_metric (agent, metric_name, timestamp)    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  VIEW: bottlenecks (materialized query)                │    │
│  │  SELECT * FROM tasks                                   │    │
│  │  WHERE status = 'completed'                            │    │
│  │  ORDER BY duration_ms DESC                             │    │
│  │  LIMIT 100;                                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  VIEW: agent_performance (aggregated stats)            │    │
│  │  SELECT recipient AS agent,                            │    │
│  │         COUNT(*) AS total_tasks,                       │    │
│  │         AVG(duration_ms) AS avg_duration,              │    │
│  │         MAX(duration_ms) AS max_duration,              │    │
│  │         SUM(CASE WHEN status='failed' THEN 1 END)      │    │
│  │           AS failed_tasks                              │    │
│  │  FROM tasks                                            │    │
│  │  WHERE status IN ('completed', 'failed')               │    │
│  │  GROUP BY recipient;                                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↓               ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│code_developer│ │project_mgr   │ │ architect    │ │  assistant   │
│  Subprocess  │ │ Subprocess   │ │ Subprocess   │ │  Subprocess  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**File Location**: `data/orchestrator.db` (persisted on disk)

**WAL Mode**: Write-Ahead Logging enables concurrent reads while writing (thread-safe)

---

## Component Specifications

### 1. Master Orchestration Daemon

**File**: `coffee_maker/autonomous/team_daemon.py`

**Class**: `TeamDaemon`

**Responsibilities**:
- Spawn and manage all agent subprocesses
- Monitor agent health (heartbeats every 30s)
- Auto-restart crashed agents (max 3 retries)
- Coordinate graceful shutdown
- Aggregate logging from all agents
- Provide status API endpoint

**API**:

```python
class TeamDaemon:
    """Master daemon that orchestrates all autonomous agents.

    This is the "operating system" for the autonomous development team.
    It manages agent lifecycles, coordinates work, and ensures fault tolerance.

    Example:
        >>> daemon = TeamDaemon()
        >>> daemon.start()  # Starts all agents
        >>> daemon.status()  # Get team health
        >>> daemon.stop()   # Graceful shutdown
    """

    def __init__(self, config: TeamConfig):
        """Initialize team daemon.

        Args:
            config: Configuration for all agents
        """
        self.config = config
        self.agents: Dict[AgentType, AgentProcess] = {}
        self.message_queue = MessageQueue()
        self.health_monitor = HealthMonitor()
        self.running = False

    def start(self) -> None:
        """Start all agents and begin orchestration.

        Spawns subprocesses for each agent, sets up message queue,
        starts health monitoring, and begins coordination loop.

        Raises:
            DaemonStartupError: If any agent fails to start
        """
        logger.info("🚀 Starting autonomous team daemon...")

        # 1. Start message queue
        self.message_queue.start()

        # 2. Spawn agent subprocesses
        for agent_type in [
            AgentType.CODE_DEVELOPER,
            AgentType.PROJECT_MANAGER,
            AgentType.ARCHITECT,
            AgentType.ASSISTANT,
        ]:
            self._spawn_agent(agent_type)

        # 3. Start health monitoring
        self.health_monitor.start()

        # 4. Begin coordination loop
        self.running = True
        self._coordination_loop()

    def _spawn_agent(self, agent_type: AgentType) -> None:
        """Spawn subprocess for specific agent.

        Args:
            agent_type: Type of agent to spawn

        Raises:
            AgentSpawnError: If subprocess fails to start
        """
        logger.info(f"Spawning {agent_type.value} agent...")

        # Create subprocess
        process = AgentProcess(
            agent_type=agent_type,
            message_queue=self.message_queue,
            config=self.config.get_agent_config(agent_type),
        )

        # Start subprocess
        process.start()

        # Register in agent registry
        self.agents[agent_type] = process

        logger.info(f"✅ {agent_type.value} agent started (PID: {process.pid})")

    def _coordination_loop(self) -> None:
        """Main coordination loop (runs continuously).

        Monitors agent health, processes messages, coordinates work.
        Runs until stop() is called or SIGTERM received.
        """
        while self.running:
            try:
                # 1. Check agent health
                self._check_agent_health()

                # 2. Process inter-agent messages
                self._process_messages()

                # 3. Coordinate work distribution
                self._coordinate_work()

                # 4. Sleep until next iteration
                time.sleep(5)  # Check every 5 seconds

            except KeyboardInterrupt:
                logger.info("Received Ctrl+C, shutting down...")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in coordination loop: {e}", exc_info=True)
                # Continue running - don't crash master daemon

    def _check_agent_health(self) -> None:
        """Check health of all agent subprocesses.

        Sends heartbeat requests, waits for responses.
        Auto-restarts agents that don't respond (max 3 retries).
        """
        for agent_type, process in self.agents.items():
            if not process.is_alive():
                logger.error(f"❌ {agent_type.value} agent crashed!")

                # Auto-restart (if retries remaining)
                if process.restart_count < 3:
                    logger.info(f"Auto-restarting {agent_type.value} (attempt {process.restart_count + 1}/3)...")
                    self._spawn_agent(agent_type)
                else:
                    logger.error(f"Max retries reached for {agent_type.value}, giving up")
                    # Send critical notification to user
                    self._notify_agent_failure(agent_type)

    def _process_messages(self) -> None:
        """Process inter-agent messages from queue.

        Routes messages to appropriate agents based on recipient.
        Handles task delegation, status updates, bug reports, etc.
        """
        while self.message_queue.has_messages():
            message = self.message_queue.get()

            # Route to recipient agent
            recipient_type = message.recipient
            if recipient_type in self.agents:
                self.agents[recipient_type].send_message(message)

    def _coordinate_work(self) -> None:
        """Coordinate work distribution across agents.

        Ensures high-priority work gets immediate attention.
        Prevents duplicate work across agents.
        Optimizes resource utilization.
        """
        # Example: If architect creates spec, notify code_developer
        # Example: If code_developer completes work, notify project_manager
        # Example: If assistant finds bug, notify project_manager
        pass

    def stop(self) -> None:
        """Gracefully stop all agents and shutdown.

        Sends SIGTERM to all subprocesses, waits for clean exit,
        stops message queue, saves state.
        """
        logger.info("🛑 Stopping autonomous team daemon...")

        self.running = False

        # 1. Stop health monitoring
        self.health_monitor.stop()

        # 2. Stop all agents (graceful)
        for agent_type, process in self.agents.items():
            logger.info(f"Stopping {agent_type.value} agent...")
            process.stop(timeout=30)  # Wait up to 30s for graceful exit

        # 3. Stop message queue
        self.message_queue.stop()

        logger.info("✅ Team daemon stopped successfully")

    def status(self) -> TeamStatus:
        """Get current status of all agents.

        Returns:
            TeamStatus with health, performance, and activity info
        """
        return TeamStatus(
            agents={
                agent_type: AgentStatus(
                    pid=process.pid,
                    is_alive=process.is_alive(),
                    uptime=process.uptime(),
                    cpu_percent=process.cpu_percent(),
                    memory_mb=process.memory_mb(),
                    current_task=process.current_task(),
                )
                for agent_type, process in self.agents.items()
            },
            message_queue_size=self.message_queue.size(),
            uptime=self._get_uptime(),
        )
```

---

### 2. Agent Process Wrapper

**File**: `coffee_maker/autonomous/agent_process.py`

**Class**: `AgentProcess`

**Purpose**: Wraps each agent in a managed subprocess with health monitoring

**API**:

```python
class AgentProcess:
    """Wrapper for agent subprocess with health monitoring.

    Each agent runs in an isolated subprocess with its own event loop.
    This class provides lifecycle management, health monitoring, and
    inter-process communication.

    Example:
        >>> process = AgentProcess(
        ...     agent_type=AgentType.CODE_DEVELOPER,
        ...     message_queue=queue,
        ...     config=config,
        ... )
        >>> process.start()
        >>> process.is_alive()
        True
        >>> process.stop()
    """

    def __init__(
        self,
        agent_type: AgentType,
        message_queue: MessageQueue,
        config: AgentConfig,
    ):
        self.agent_type = agent_type
        self.message_queue = message_queue
        self.config = config
        self.process: Optional[multiprocessing.Process] = None
        self.restart_count = 0
        self.start_time: Optional[datetime] = None

    def start(self) -> None:
        """Start agent subprocess."""
        self.process = multiprocessing.Process(
            target=self._run_agent,
            name=f"agent-{self.agent_type.value}",
        )
        self.process.start()
        self.start_time = datetime.now()

    def _run_agent(self) -> None:
        """Agent main loop (runs in subprocess).

        This is the entry point for the agent subprocess.
        Sets up agent, runs main loop, handles cleanup.
        """
        # Set process title (for `ps` visibility)
        setproctitle(f"team-daemon: {self.agent_type.value}")

        # Initialize agent based on type
        if self.agent_type == AgentType.CODE_DEVELOPER:
            from coffee_maker.autonomous.daemon import DevDaemon
            agent = DevDaemon(auto_approve=True)
        elif self.agent_type == AgentType.PROJECT_MANAGER:
            from coffee_maker.cli.roadmap_cli import ProjectManagerDaemon
            agent = ProjectManagerDaemon()
        elif self.agent_type == AgentType.ARCHITECT:
            from coffee_maker.autonomous.architect_daemon import ArchitectDaemon
            agent = ArchitectDaemon()
        elif self.agent_type == AgentType.ASSISTANT:
            from coffee_maker.autonomous.assistant_daemon import AssistantDaemon
            agent = AssistantDaemon()
        else:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        # Run agent
        agent.run()

    def is_alive(self) -> bool:
        """Check if agent subprocess is alive."""
        return self.process is not None and self.process.is_alive()

    def stop(self, timeout: int = 30) -> None:
        """Stop agent subprocess gracefully.

        Args:
            timeout: Max seconds to wait for graceful exit
        """
        if self.process is not None:
            self.process.terminate()  # Send SIGTERM
            self.process.join(timeout=timeout)

            if self.process.is_alive():
                # Force kill if didn't exit gracefully
                self.process.kill()

    def cpu_percent(self) -> float:
        """Get CPU usage percentage."""
        if self.process is not None:
            return psutil.Process(self.process.pid).cpu_percent()
        return 0.0

    def memory_mb(self) -> float:
        """Get memory usage in MB."""
        if self.process is not None:
            return psutil.Process(self.process.pid).memory_info().rss / 1024 / 1024
        return 0.0
```

---

### 3. Message Queue (SQLite-Based)

**File**: `coffee_maker/autonomous/message_queue.py`

**Implementation**: **SQLite with WAL mode** - **Zero external dependencies** (Python stdlib)

**Dependencies**: **None** (sqlite3, json, uuid, datetime are Python stdlib)

**Database**: `data/orchestrator.db` (persisted on disk)

**Schema Definition**:

```sql
-- Enable WAL mode (Write-Ahead Logging) for concurrent access
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;  -- Balance safety and performance

-- Tasks table (message queue + historical data)
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

-- Agent metrics table (performance tracking)
CREATE TABLE IF NOT EXISTS agent_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT NOT NULL,
    metric_name TEXT NOT NULL,  -- tasks_completed, avg_duration, cpu_percent, memory_mb
    metric_value REAL NOT NULL,
    timestamp TEXT NOT NULL  -- ISO8601 timestamp
);

-- Index for metrics queries
CREATE INDEX IF NOT EXISTS idx_agent_metric ON agent_metrics(agent, metric_name, timestamp);

-- View: Top 100 slowest tasks (bottleneck analysis)
CREATE VIEW IF NOT EXISTS bottlenecks AS
SELECT task_id, recipient AS agent, type, duration_ms, created_at, started_at, completed_at
FROM tasks
WHERE status = 'completed' AND duration_ms IS NOT NULL
ORDER BY duration_ms DESC
LIMIT 100;

-- View: Agent performance aggregates
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

-- View: Queue depth by agent (current queued tasks)
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

**Python API**:

```python
import sqlite3
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class Message:
    """Inter-agent message."""
    sender: str  # AgentType.value
    recipient: str  # AgentType.value
    type: str  # MessageType.value
    payload: dict
    priority: int = 5  # 1=highest, 10=lowest
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class MessageQueue:
    """SQLite-based inter-agent communication queue with persistence and metrics.

    Provides reliable message passing between agents with:
    - Priority queuing (SQL ORDER BY priority)
    - Persistence (survives daemon crashes)
    - Duration tracking (start/complete timestamps)
    - Bottleneck analysis (SQL queries on duration_ms)
    - Historical metrics (aggregated performance data)

    Features:
    - Zero external dependencies (sqlite3 is Python stdlib)
    - Thread-safe (WAL mode enables concurrent reads/writes)
    - SQL queries for analytics (e.g., SELECT * FROM bottlenecks)
    - Automatic cleanup (old completed tasks pruned periodically)

    Example:
        >>> queue = MessageQueue(db_path="data/orchestrator.db")
        >>> queue.send(Message(
        ...     sender="architect",
        ...     recipient="code_developer",
        ...     type="task_delegate",
        ...     payload={"spec_id": "SPEC-071"},
        ...     priority=2,
        ... ))
        >>>
        >>> # Get next task for code_developer
        >>> message = queue.get("code_developer")
        >>> queue.mark_started(message.task_id, agent="code_developer")
        >>> # ... do work ...
        >>> queue.mark_completed(message.task_id, duration_ms=1500)
    """

    def __init__(self, db_path: str = "data/orchestrator.db"):
        """Initialize SQLite message queue.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database and schema
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema with tables, indexes, and views."""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for concurrent access
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")

            # Create tables (see schema above)
            conn.executescript("""
                -- [Full schema from above would be inserted here]
            """)
            conn.commit()

    def send(self, message: Message) -> None:
        """Send message to recipient's queue with priority.

        Args:
            message: Message to send

        Implementation:
            INSERT INTO tasks (task_id, sender, recipient, type, priority,
                               payload, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'queued')
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tasks (task_id, sender, recipient, type, priority,
                                   payload, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'queued')
            """, (
                message.task_id,
                message.sender,
                message.recipient,
                message.type,
                message.priority,
                json.dumps(message.payload),
                message.timestamp,
            ))
            conn.commit()

    def get(self, recipient: str, timeout: float = 1.0) -> Optional[Message]:
        """Get next message for recipient (highest priority first).

        Args:
            recipient: Agent to get messages for
            timeout: Not used (kept for API compatibility)

        Returns:
            Next message or None if no messages available

        Implementation:
            SELECT * FROM tasks
            WHERE recipient = ? AND status = 'queued'
            ORDER BY priority ASC, created_at ASC
            LIMIT 1
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT task_id, sender, recipient, type, priority, payload, created_at
                FROM tasks
                WHERE recipient = ? AND status = 'queued'
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
            """, (recipient,))

            row = cursor.fetchone()
            if row:
                return Message(
                    task_id=row["task_id"],
                    sender=row["sender"],
                    recipient=row["recipient"],
                    type=row["type"],
                    priority=row["priority"],
                    payload=json.loads(row["payload"]),
                    timestamp=row["created_at"],
                )
            return None

    def mark_started(self, task_id: str, agent: str) -> None:
        """Mark task as started, record start time.

        Args:
            task_id: Task identifier
            agent: Agent starting the task

        Implementation:
            UPDATE tasks
            SET status = 'running', started_at = ?
            WHERE task_id = ?
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE tasks
                SET status = 'running', started_at = ?
                WHERE task_id = ?
            """, (datetime.now().isoformat(), task_id))
            conn.commit()

    def mark_completed(self, task_id: str, duration_ms: int) -> None:
        """Mark task as completed, record duration.

        Args:
            task_id: Task identifier
            duration_ms: Task duration in milliseconds

        Implementation:
            UPDATE tasks
            SET status = 'completed', completed_at = ?, duration_ms = ?
            WHERE task_id = ?
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE tasks
                SET status = 'completed', completed_at = ?, duration_ms = ?
                WHERE task_id = ?
            """, (datetime.now().isoformat(), duration_ms, task_id))
            conn.commit()

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """Mark task as failed, record error message.

        Args:
            task_id: Task identifier
            error_message: Error details
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE tasks
                SET status = 'failed', completed_at = ?, error_message = ?
                WHERE task_id = ?
            """, (datetime.now().isoformat(), error_message, task_id))
            conn.commit()

    def get_slowest_tasks(self, limit: int = 10) -> List[dict]:
        """Get slowest tasks for bottleneck analysis.

        Args:
            limit: Number of slowest tasks to return

        Returns:
            List of task metadata sorted by duration (slowest first)

        Implementation:
            SELECT * FROM bottlenecks LIMIT ?
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM bottlenecks LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_agent_performance(self) -> List[dict]:
        """Get aggregated performance metrics per agent.

        Returns:
            List of agent performance stats

        Implementation:
            SELECT * FROM agent_performance
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM agent_performance")
            return [dict(row) for row in cursor.fetchall()]

    def get_queue_depth(self) -> List[dict]:
        """Get current queue depth by agent and priority.

        Returns:
            List of queue depth stats by agent

        Implementation:
            SELECT * FROM queue_depth
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM queue_depth")
            return [dict(row) for row in cursor.fetchall()]

    def record_metric(self, agent: str, metric_name: str, metric_value: float) -> None:
        """Record performance metric for agent.

        Args:
            agent: Agent name
            metric_name: Metric name (e.g., "cpu_percent", "memory_mb")
            metric_value: Metric value

        Implementation:
            INSERT INTO agent_metrics (agent, metric_name, metric_value, timestamp)
            VALUES (?, ?, ?, ?)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO agent_metrics (agent, metric_name, metric_value, timestamp)
                VALUES (?, ?, ?, ?)
            """, (agent, metric_name, metric_value, datetime.now().isoformat()))
            conn.commit()

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """Clean up completed tasks older than N days.

        Args:
            days: Number of days to retain

        Returns:
            Number of tasks deleted

        Implementation:
            DELETE FROM tasks
            WHERE status IN ('completed', 'failed')
              AND completed_at < datetime('now', '-{days} days')
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"""
                DELETE FROM tasks
                WHERE status IN ('completed', 'failed')
                  AND completed_at < datetime('now', '-{days} days')
            """)
            conn.commit()
            return cursor.rowcount

    def has_messages(self, recipient: Optional[str] = None) -> bool:
        """Check if queue has messages.

        Args:
            recipient: Optional agent filter

        Returns:
            True if messages exist
        """
        with sqlite3.connect(self.db_path) as conn:
            if recipient:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM tasks WHERE recipient = ? AND status = 'queued'",
                    (recipient,)
                )
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'queued'")
            count = cursor.fetchone()[0]
            return count > 0

    def size(self, recipient: Optional[str] = None) -> int:
        """Get queue size.

        Args:
            recipient: Optional agent filter

        Returns:
            Number of queued messages
        """
        with sqlite3.connect(self.db_path) as conn:
            if recipient:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM tasks WHERE recipient = ? AND status = 'queued'",
                    (recipient,)
                )
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'queued'")
            return cursor.fetchone()[0]

    def stop(self) -> None:
        """Stop message queue (cleanup, vacuum database)."""
        with sqlite3.connect(self.db_path) as conn:
            # Clean up completed tasks older than 30 days
            self.cleanup_old_tasks(days=30)

            # Vacuum database to reclaim space
            conn.execute("VACUUM")
            conn.commit()
```

**Benefits of SQLite Approach**:

1. **Persistence**: Messages survive daemon crashes (written to disk)
2. **Analytics**: SQL queries for bottleneck analysis (no manual heapq tracking)
3. **Metrics**: Historical performance data (agent_metrics table)
4. **Thread-Safe**: WAL mode enables concurrent reads/writes
5. **Zero Dependencies**: SQLite is Python stdlib (no external packages)
6. **Simple Queries**: `SELECT * FROM bottlenecks LIMIT 10`
7. **Aggregation**: `SELECT agent, AVG(duration_ms) FROM tasks GROUP BY agent`

---

### 4. Individual Agent Daemons

Each agent needs a daemon implementation:

#### 4.1. code_developer (Already Exists)

**File**: `coffee_maker/autonomous/daemon.py`

**Status**: ✅ Already implemented

**Enhancements Needed**:
- Listen to message queue for spec_created events
- Send implementation_complete events
- Report status to team daemon

#### 4.2. project_manager Daemon (NEW)

**File**: `coffee_maker/cli/project_manager_daemon.py`

**Responsibilities**:
- Monitor GitHub (PRs, issues, CI) every 5 minutes
- Send notifications for important events
- Update ROADMAP status when work completes
- Verify DoD when requested

#### 4.3. architect Daemon (NEW)

**File**: `coffee_maker/autonomous/architect_daemon.py`

**Responsibilities**:
- Review ROADMAP weekly (every Monday)
- Create specs for all planned priorities
- Respond to spec creation requests
- Continuous spec improvement (CFR-010)

#### 4.4. assistant Daemon (NEW)

**File**: `coffee_maker/autonomous/assistant_daemon.py`

**Responsibilities**:
- Listen for demo creation requests
- Test features with Puppeteer
- Detect bugs and report to project_manager
- Answer questions from message queue

---

## Agent Coordination Examples

### Example 1: Spec Creation → Implementation Flow

```
1. architect daemon (Monday 9am):
   - Reviews ROADMAP
   - Finds US-048 (Planned)
   - Creates SPEC-048
   - Sends message:
     {
       sender: ARCHITECT,
       recipient: CODE_DEVELOPER,
       type: SPEC_CREATED,
       payload: {spec_id: "SPEC-048", priority: "US-048"}
     }

2. code_developer daemon (receives message):
   - Reads SPEC-048
   - Implements US-048
   - Runs tests
   - Creates PR
   - Sends message:
     {
       sender: CODE_DEVELOPER,
       recipient: PROJECT_MANAGER,
       type: IMPLEMENTATION_COMPLETE,
       payload: {priority: "US-048", pr_number: 123}
     }

3. project_manager daemon (receives message):
   - Verifies DoD with Puppeteer
   - Updates ROADMAP (US-048: Complete)
   - Sends notification to user
```

### Example 2: Bug Detection → Fix Flow

```
1. assistant daemon (testing feature):
   - Creates demo for US-047
   - Detects bug in notification system
   - Sends message:
     {
       sender: ASSISTANT,
       recipient: PROJECT_MANAGER,
       type: BUG_REPORT,
       payload: {
         title: "Notifications not playing sound",
         severity: "critical",
         reproduction_steps: "...",
         expected: "...",
         actual: "..."
       }
     }

2. project_manager daemon (receives message):
   - Creates new priority in ROADMAP (BUG-003)
   - Prioritizes based on severity (critical → top of queue)
   - Notifies user

3. architect daemon (next weekly review):
   - Sees BUG-003 in ROADMAP
   - Creates SPEC-073 for fix
   - Sends spec_created message

4. code_developer daemon:
   - Implements fix based on SPEC-073
   - Runs tests
   - Creates PR
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1, 14-18 hours)

**Day 1-2: Team Daemon Framework** (8-10 hours)
- Create `TeamDaemon` class (based on POC-072)
- Implement agent process management
- Add health monitoring
- Implement graceful shutdown

**Day 3: SQLite Message Queue** (4-5 hours) ⭐ ENHANCED
- Create SQLite schema (tasks, agent_metrics, views)
- Implement `MessageQueue` class with SQLite backend
  - Priority queuing (SQL ORDER BY priority)
  - Task lifecycle (queued → running → completed/failed)
  - Duration tracking (`mark_started`, `mark_completed`)
  - Bottleneck analysis (SQL queries on duration_ms)
  - Metrics recording (agent_metrics table)
- Add indexes for fast queries
- Enable WAL mode for thread-safe concurrent access
- **Zero dependencies** - sqlite3 is stdlib

**Day 4: Testing & Integration** (3-4 hours)
- Unit tests for TeamDaemon (based on POC-072 tests)
- Integration tests for agent spawning
- Health check tests
- Message queue tests (priority ordering, bottleneck tracking)

### Phase 2: Agent Daemons (Week 2, 12-16 hours)

**Day 5: project_manager Daemon** (4-5 hours)
- Implement GitHub monitoring loop
- Add notification sending
- Add message queue integration

**Day 6: architect Daemon** (4-5 hours)
- Implement weekly ROADMAP review
- Add proactive spec creation
- Add message queue integration

**Day 7: assistant Daemon** (4-6 hours)
- Implement demo creation loop
- Add bug detection
- Add message queue integration

### Phase 3: Coordination & Polish (Week 3, 8-12 hours)

**Day 8: Work Coordination** (4-6 hours)
- Implement coordination logic
- Add priority management
- Add resource optimization

**Day 9-10: Documentation & Rollout** (4-6 hours)
- Update CLAUDE.md
- Create user documentation
- Write operational runbook
- Deploy and monitor

---

## Bottleneck Analysis & Performance Monitoring

### Real-Time Bottleneck Detection

**Goal**: Identify slow tasks and agent performance bottlenecks automatically

**Implementation**: SQL queries on SQLite database

```python
# In TeamDaemon._coordination_loop()
def _check_bottlenecks(self) -> None:
    """Check for performance bottlenecks every 5 minutes."""
    # Query SQLite for slowest tasks
    slowest_tasks = self.message_queue.get_slowest_tasks(limit=10)
    # SQL: SELECT * FROM bottlenecks LIMIT 10

    for task in slowest_tasks:
        if task["duration_ms"] > 30000:  # >30 seconds
            logger.warning(
                f"BOTTLENECK: {task['agent']} task {task['task_id']} "
                f"took {task['duration_ms']}ms (type: {task['type']})"
            )

            # Send notification to project_manager
            self._notify_bottleneck(task)

    # Calculate percentiles (from SQLite)
    p50, p95, p99 = self._get_percentiles_from_sqlite()
    logger.info(f"Task durations: p50={p50}ms, p95={p95}ms, p99={p99}ms")

def _get_percentiles_from_sqlite(self) -> tuple:
    """Calculate p50, p95, p99 from SQLite."""
    with sqlite3.connect(self.message_queue.db_path) as conn:
        cursor = conn.execute("""
            SELECT
                (SELECT duration_ms FROM tasks
                 WHERE status = 'completed' AND duration_ms IS NOT NULL
                 ORDER BY duration_ms
                 LIMIT 1 OFFSET (SELECT COUNT(*) * 50 / 100 FROM tasks
                                  WHERE status = 'completed' AND duration_ms IS NOT NULL)) AS p50,
                (SELECT duration_ms FROM tasks
                 WHERE status = 'completed' AND duration_ms IS NOT NULL
                 ORDER BY duration_ms
                 LIMIT 1 OFFSET (SELECT COUNT(*) * 95 / 100 FROM tasks
                                  WHERE status = 'completed' AND duration_ms IS NOT NULL)) AS p95,
                (SELECT duration_ms FROM tasks
                 WHERE status = 'completed' AND duration_ms IS NOT NULL
                 ORDER BY duration_ms
                 LIMIT 1 OFFSET (SELECT COUNT(*) * 99 / 100 FROM tasks
                                  WHERE status = 'completed' AND duration_ms IS NOT NULL)) AS p99
        """)
        row = cursor.fetchone()
        return row[0] or 0, row[1] or 0, row[2] or 0
```

### Bottleneck Metrics Dashboard

**SQL Query Examples** (leveraging SQLite views):

```python
# Get slowest 10 tasks
slowest = queue.get_slowest_tasks(limit=10)
# SQL: SELECT * FROM bottlenecks LIMIT 10
# → [{task_id, agent, type, duration_ms, created_at, started_at, completed_at}, ...]

# Get agent performance stats
performance = queue.get_agent_performance()
# SQL: SELECT * FROM agent_performance
# → [{agent, total_tasks, completed_tasks, failed_tasks,
#      avg_duration_ms, max_duration_ms, min_duration_ms}, ...]

# Example output:
# [
#   {
#     "agent": "code_developer",
#     "total_tasks": 156,
#     "completed_tasks": 153,
#     "failed_tasks": 3,
#     "avg_duration_ms": 2300,
#     "max_duration_ms": 45000,
#     "min_duration_ms": 120
#   },
#   ...
# ]

# Get queue depth by agent
queue_depth = queue.get_queue_depth()
# SQL: SELECT * FROM queue_depth
# → [{agent, queued_tasks, high_priority, normal_priority, low_priority}, ...]

# Example output:
# [
#   {
#     "agent": "code_developer",
#     "queued_tasks": 5,
#     "high_priority": 2,
#     "normal_priority": 2,
#     "low_priority": 1
#   },
#   ...
# ]

# Get 95th percentile duration
with sqlite3.connect("data/orchestrator.db") as conn:
    cursor = conn.execute("""
        SELECT duration_ms
        FROM tasks
        WHERE status = 'completed' AND duration_ms IS NOT NULL
        ORDER BY duration_ms
        LIMIT 1 OFFSET (
            SELECT CAST(COUNT(*) * 0.95 AS INTEGER)
            FROM tasks
            WHERE status = 'completed' AND duration_ms IS NOT NULL
        )
    """)
    p95 = cursor.fetchone()[0]
    print(f"95th percentile: {p95}ms")

# Analyze bottlenecks by task type
with sqlite3.connect("data/orchestrator.db") as conn:
    cursor = conn.execute("""
        SELECT
            type,
            COUNT(*) AS total,
            AVG(duration_ms) AS avg_duration,
            MAX(duration_ms) AS max_duration
        FROM tasks
        WHERE status = 'completed' AND duration_ms IS NOT NULL
        GROUP BY type
        ORDER BY avg_duration DESC
    """)
    for row in cursor.fetchall():
        print(f"{row[0]}: avg={row[2]}ms, max={row[3]}ms ({row[1]} tasks)")
```

**Benefits of SQLite Approach**:

1. **Persistent Metrics**: Historical data survives daemon restarts
2. **Simple Queries**: Standard SQL (no manual heapq tracking)
3. **Flexible Analysis**: Ad-hoc queries for any time range
4. **Trend Analysis**: Compare performance week-over-week
5. **Views**: Pre-computed aggregates (bottlenecks, agent_performance, queue_depth)

### Langfuse Integration for Observability

**SQLite → Langfuse Exporter**:

```python
class LangfuseExporter:
    """Export task completion events from SQLite to Langfuse for observability."""

    def __init__(self, message_queue: MessageQueue, langfuse_client):
        self.queue = message_queue
        self.langfuse = langfuse_client
        self._last_export_timestamp = None

    def export_new_completions(self):
        """Export newly completed tasks to Langfuse.

        Queries SQLite for tasks completed since last export.
        """
        with sqlite3.connect(self.queue.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Query for newly completed tasks
            if self._last_export_timestamp:
                cursor = conn.execute("""
                    SELECT task_id, recipient, type, duration_ms, created_at, completed_at
                    FROM tasks
                    WHERE status = 'completed'
                      AND completed_at > ?
                    ORDER BY completed_at
                """, (self._last_export_timestamp,))
            else:
                cursor = conn.execute("""
                    SELECT task_id, recipient, type, duration_ms, created_at, completed_at
                    FROM tasks
                    WHERE status = 'completed'
                    ORDER BY completed_at DESC
                    LIMIT 100
                """)

            tasks = cursor.fetchall()

            # Export to Langfuse
            for task in tasks:
                self.langfuse.trace(
                    name=f"task_{task['task_id']}",
                    metadata={
                        "agent": task["recipient"],
                        "type": task["type"],
                        "duration_ms": task["duration_ms"],
                        "created_at": task["created_at"],
                        "completed_at": task["completed_at"],
                    },
                )

            # Update last export timestamp
            if tasks:
                self._last_export_timestamp = tasks[-1]["completed_at"]

# Run periodically in background thread
exporter = LangfuseExporter(message_queue, langfuse_client)
def export_loop():
    while True:
        exporter.export_new_completions()
        time.sleep(60)  # Export every 60 seconds
threading.Thread(target=export_loop, daemon=True).start()
```

**Benefits**:
- Queries SQLite for completed tasks (persistent, no lost data)
- Incremental export (only new completions since last export)
- Historical backfill (can re-export old tasks if needed)

### Alerting Rules

**Automatic alerts for bottlenecks**:

```yaml
bottleneck_alerts:
  # Alert if any task takes >60 seconds
  slow_task_threshold: 60000  # milliseconds

  # Alert if p95 duration exceeds threshold
  p95_threshold: 30000  # milliseconds

  # Alert if agent has >5 failed tasks in 1 hour
  max_failed_tasks: 5
  failure_window: 3600  # seconds

  # Alert if queue depth exceeds threshold
  max_queue_depth: 100  # tasks
```

**Implementation** (SQLite queries):

```python
def _check_alerts(self):
    """Check alerting rules and send notifications.

    Queries SQLite database for bottlenecks and performance issues.
    """
    # Check slow tasks (from bottlenecks view)
    slowest_tasks = self.message_queue.get_slowest_tasks(limit=100)
    for task in slowest_tasks:
        if task["duration_ms"] > self.config.slow_task_threshold:
            self._send_alert(
                severity="warning",
                title=f"Slow task detected: {task['task_id']}",
                details=f"Agent: {task['agent']}, Duration: {task['duration_ms']}ms (threshold: {self.config.slow_task_threshold}ms)",
            )

    # Check p95 (from SQLite query)
    p95 = self._get_p95_duration_from_sqlite()
    if p95 > self.config.p95_threshold:
        self._send_alert(
            severity="warning",
            title=f"High p95 duration: {p95}ms",
            details=f"Threshold: {self.config.p95_threshold}ms",
        )

    # Check queue depth per agent (from queue_depth view)
    queue_depths = self.message_queue.get_queue_depth()
    for agent_queue in queue_depths:
        if agent_queue["queued_tasks"] > self.config.max_queue_depth_per_agent:
            self._send_alert(
                severity="critical",
                title=f"Queue depth critical for {agent_queue['agent']}: {agent_queue['queued_tasks']} tasks",
                details=f"High priority: {agent_queue['high_priority']}, Normal: {agent_queue['normal_priority']}, Low: {agent_queue['low_priority']}",
            )

    # Check failed task rate (from agent_performance view)
    performance = self.message_queue.get_agent_performance()
    for agent_perf in performance:
        if agent_perf["total_tasks"] > 0:
            failure_rate = agent_perf["failed_tasks"] / agent_perf["total_tasks"]
            if failure_rate > self.config.max_failure_rate:
                self._send_alert(
                    severity="critical",
                    title=f"High failure rate for {agent_perf['agent']}: {failure_rate * 100:.1f}%",
                    details=f"Failed: {agent_perf['failed_tasks']}, Total: {agent_perf['total_tasks']}",
                )
```

---

## CLI Commands

### Start Team Daemon

```bash
# Start all agents
poetry run team-daemon

# Start with debug logging
poetry run team-daemon --debug

# Start specific agents only
poetry run team-daemon --agents code_developer,project_manager
```

### Monitor Team Status

```bash
# View team status dashboard
poetry run team-daemon status

# View specific agent status
poetry run team-daemon status --agent code_developer

# View message queue
poetry run team-daemon queue

# View bottleneck analysis ⭐ NEW
poetry run team-daemon bottlenecks
# Output:
# Top 10 Slowest Tasks:
# 1. task_abc123 (code_developer): 45,000ms - implement_feature
# 2. task_def456 (architect): 32,000ms - create_spec
# 3. task_ghi789 (assistant): 28,000ms - create_demo
# ...
# Performance Metrics:
# - p50: 1,200ms
# - p95: 15,000ms
# - p99: 32,000ms

# View agent performance metrics ⭐ NEW
poetry run team-daemon metrics --agent code_developer
# Output:
# code_developer Performance:
# - Tasks completed: 156
# - Tasks failed: 3
# - Average duration: 2,300ms
# - p95 duration: 8,500ms
# - Current queue depth: 5 (high: 2, normal: 2, low: 1)

# View task completion events (in-memory log)
poetry run team-daemon events --tail 100
# Output (last 100 completed tasks):
# [10:30:05] task_queued: architect.create_spec (priority=2)
# [10:30:10] task_started: architect.create_spec
# [10:32:45] task_completed: architect.create_spec (duration=155,000ms)
# [10:32:46] task_queued: code_developer.implement (priority=5)
```

### Stop Team Daemon

```bash
# Graceful shutdown (waits for agents to finish)
poetry run team-daemon stop

# Force shutdown (immediate)
poetry run team-daemon stop --force
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Uptime** | >99% | Agent crashes / total runtime |
| **Auto-Restart Time** | <5 seconds | Time from crash to restart |
| **Work Coordination** | >90% | Tasks routed to correct agent |
| **Resource Usage** | <500MB RAM | Total memory for all agents |
| **Inter-Agent Latency** | <5ms | Message queue latency (SQLite with WAL mode) |
| **Message Persistence** ⭐ NEW | 100% | Messages survive daemon crashes (SQLite on disk) |
| **Bottleneck Detection** ⭐ NEW | <5 min | Time to identify slow tasks (SQL query on duration_ms) |
| **Task Duration Tracking** ⭐ NEW | 100% | All tasks have start/completion timestamps (SQLite) |
| **Historical Metrics** ⭐ NEW | 30 days | Metrics retained in SQLite (configurable) |
| **Observability** ⭐ NEW | Periodic | Export to Langfuse every 60s (from SQLite) |
| **Analytics** ⭐ NEW | Real-time | SQL queries for bottlenecks, trends, aggregates |

---

## Risk Assessment

### Risk 1: Resource Exhaustion 🟠 MEDIUM

**Description**: All agents running simultaneously may exhaust system resources

**Mitigation**:
- Set memory limits per agent (100MB max)
- Throttle API calls (shared rate limiter)
- Monitor resource usage, kill agents if exceeded

### Risk 2: Agent Deadlock 🟡 LOW

**Description**: Agents waiting on each other create deadlock

**Mitigation**:
- Message queue with timeouts
- Deadlock detection (30s timeout)
- Auto-recovery (restart blocked agents)

### Risk 3: Message Queue Overflow 🟢 LOW

**Description**: Message queue grows unbounded

**Mitigation**:
- Queue size limit (1000 messages)
- Oldest messages dropped (FIFO)
- Monitoring and alerts

---

## Appendix

### A. Configuration

**File**: `team_daemon.yaml`

```yaml
team:
  agents:
    code_developer:
      enabled: true
      auto_approve: true
      sleep_interval: 60

    project_manager:
      enabled: true
      github_poll_interval: 300  # 5 minutes

    architect:
      enabled: true
      review_schedule: "0 9 * * 1"  # Every Monday 9am

    assistant:
      enabled: true

  message_queue:
    backend: sqlite  # SQLite (stdlib only, zero dependencies)
    db_path: data/orchestrator.db  # Database file location
    # Task retention (for observability)
    cleanup_interval_days: 30  # Delete completed tasks older than 30 days
    # WAL mode settings (for thread-safety)
    wal_enabled: true
    synchronous_mode: NORMAL  # Balance safety and performance

  health_check:
    interval: 30  # seconds
    timeout: 5    # seconds

  resource_limits:
    max_memory_mb: 500
    max_cpu_percent: 50

  observability:
    langfuse:
      enabled: true
      # Export completed tasks to Langfuse periodically
      export_interval: 60  # seconds
```

**Environment Variables**:

```bash
# SQLite database location (optional, defaults to data/orchestrator.db)
export ORCHESTRATOR_DB_PATH="data/orchestrator.db"

# Cleanup interval for old tasks (optional, defaults to 30 days)
export ORCHESTRATOR_CLEANUP_DAYS=30

# No external dependencies - SQLite is Python stdlib
# No Redis server, no external services needed
```

---

**Created**: 2025-10-18
**Author**: architect agent
**Version**: 1.0
**Status**: Draft (Pending Review)
