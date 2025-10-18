# SPEC-072: Multi-Agent Orchestration Daemon

**Status**: Draft

**Created**: 2025-10-18

**Author**: architect agent

**Estimated Effort**: 3-4 days (24-32 hours)

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

### Message Queue Architecture (Redis-Based)

**Decision**: Use **Redis** for production message queue (pre-approved per ADR-013)

**Benefits**:
- ✅ Persistent message storage (survives daemon crashes)
- ✅ Built-in duration tracking (Redis Hashes + Sorted Sets)
- ✅ Real-time bottleneck analysis (O(log N) queries)
- ✅ Pub/Sub for live observability (no polling)
- ✅ Battle-tested reliability (100K+ ops/sec)
- ✅ Zero user approval needed (pre-approved dependency)

```
┌─────────────────────────────────────────────────────────────────┐
│                    REDIS MESSAGE QUEUE                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Task Queues (Redis Lists - LPUSH/RPOP)               │    │
│  │  - queue:architect (create_spec tasks)                 │    │
│  │  - queue:code_developer (implement tasks)              │    │
│  │  - queue:assistant (demo tasks)                        │    │
│  │  - queue:project_manager (verification tasks)          │    │
│  │                                                        │    │
│  │  Priority: Multi-list approach                        │    │
│  │  - queue:high (p1-3): Check first                     │    │
│  │  - queue:normal (p4-6): Check second                  │    │
│  │  - queue:low (p7-10): Check last                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Event Stream (Redis Pub/Sub)                         │    │
│  │  Channel: events:orchestrator                         │    │
│  │  - spec_created {spec_id, agent, timestamp}           │    │
│  │  - implementation_complete {priority, pr, duration}    │    │
│  │  - bug_detected {severity, title, agent}              │    │
│  │  - agent_started {agent, pid}                         │    │
│  │  - agent_crashed {agent, retry_count}                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Task Metadata (Redis Hashes)                         │    │
│  │  key: task:{task_id}                                  │    │
│  │  - start_time: timestamp                              │    │
│  │  - duration: milliseconds (updated on completion)     │    │
│  │  - agent: AgentType                                   │    │
│  │  - status: queued|running|complete|failed             │    │
│  │  - priority: 1-10                                     │    │
│  │  - payload: JSON                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Bottleneck Analysis (Redis Sorted Sets)              │    │
│  │  zset: tasks:by_duration                              │    │
│  │  - {task_id: duration_ms} (sorted by duration)        │    │
│  │                                                        │    │
│  │  Query slowest 10 tasks: ZREVRANGE 0 9 WITHSCORES    │    │
│  │  Query 95th percentile: ZREVRANGE 0 <5% of total>    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Agent Status (Redis Hashes)                          │    │
│  │  key: agent:{agent_type}                              │    │
│  │  - pid: process ID                                    │    │
│  │  - status: running|crashed|stopped                    │    │
│  │  - current_task: task_id or null                      │    │
│  │  - last_heartbeat: timestamp                          │    │
│  │  - tasks_completed: counter                           │    │
│  │  - tasks_failed: counter                              │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
   Subscribers:       Subscribers:          Subscribers:
   - code_developer   - project_manager     - Langfuse exporter
   - project_manager  - architect           - Orchestrator dashboard
   - assistant        - assistant           - All agents (coordination)
```

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

### 3. Message Queue (Redis-Based)

**File**: `coffee_maker/autonomous/message_queue.py`

**Implementation**: **Redis** (production) with fallback to in-memory (development/testing)

**Dependencies**: `redis` (✅ pre-approved per ADR-013), `hiredis` (✅ pre-approved, faster parser)

**API**:

```python
class Message:
    """Inter-agent message."""
    sender: AgentType
    recipient: AgentType
    type: MessageType  # TASK_DELEGATE, STATUS_UPDATE, BUG_REPORT, etc.
    payload: dict
    priority: int  # 1=highest, 10=lowest
    timestamp: datetime
    task_id: str  # Unique task identifier (UUID)

class MessageQueue:
    """Redis-based inter-agent communication queue.

    Provides reliable, persistent message passing between agents.
    Supports priority queuing, broadcast messages, and duration tracking.

    Features:
    - Persistent storage (survives daemon crashes)
    - Priority queuing (3 priority levels: high/normal/low)
    - Duration tracking (start time → completion time)
    - Bottleneck analysis (slowest tasks via Redis Sorted Sets)
    - Real-time observability (Redis Pub/Sub)
    - Langfuse integration (automatic metrics export)

    Example:
        >>> queue = MessageQueue(redis_url="redis://localhost:6379/0")
        >>> queue.send(Message(
        ...     sender=AgentType.ARCHITECT,
        ...     recipient=AgentType.CODE_DEVELOPER,
        ...     type=MessageType.TASK_DELEGATE,
        ...     payload={"spec_id": "SPEC-071"},
        ...     priority=2,  # High priority
        ... ))
        >>>
        >>> # Get next task for code_developer
        >>> message = queue.get(AgentType.CODE_DEVELOPER)
        >>> queue.mark_started(message.task_id, agent=AgentType.CODE_DEVELOPER)
        >>> # ... do work ...
        >>> queue.mark_completed(message.task_id, duration_ms=1500)
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis-based message queue.

        Args:
            redis_url: Redis connection URL (default: localhost)
        """
        import redis
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("events:orchestrator")

    def send(self, message: Message) -> None:
        """Send message to recipient's queue with priority.

        Args:
            message: Message to send

        Implementation:
            1. Generate unique task_id (UUID)
            2. Store task metadata in Redis Hash (task:{task_id})
            3. Push task_id to recipient's priority queue (LPUSH)
            4. Publish event to Pub/Sub channel
        """
        import uuid
        task_id = str(uuid.uuid4())

        # Store task metadata
        self.redis.hset(f"task:{task_id}", mapping={
            "sender": message.sender.value,
            "recipient": message.recipient.value,
            "type": message.type.value,
            "payload": json.dumps(message.payload),
            "priority": message.priority,
            "timestamp": message.timestamp.isoformat(),
            "status": "queued",
        })

        # Push to appropriate priority queue
        priority_level = self._get_priority_level(message.priority)
        self.redis.lpush(f"queue:{priority_level}:{message.recipient.value}", task_id)

        # Publish event
        self.redis.publish("events:orchestrator", json.dumps({
            "event": "task_queued",
            "task_id": task_id,
            "recipient": message.recipient.value,
            "priority": message.priority,
        }))

    def get(self, recipient: AgentType, timeout: float = 1.0) -> Optional[Message]:
        """Get next message for recipient (highest priority first).

        Args:
            recipient: Agent to get messages for
            timeout: Timeout in seconds (default: 1.0)

        Returns:
            Next message or None if no messages available

        Implementation:
            1. Check high priority queue first (RPOP queue:high:{agent})
            2. If empty, check normal priority queue
            3. If empty, check low priority queue
            4. If task found, load metadata from Redis Hash
            5. Return Message object
        """
        # Check queues in priority order
        for priority_level in ["high", "normal", "low"]:
            task_id = self.redis.rpop(f"queue:{priority_level}:{recipient.value}")
            if task_id:
                # Load task metadata
                task_data = self.redis.hgetall(f"task:{task_id}")
                return Message(
                    sender=AgentType(task_data["sender"]),
                    recipient=AgentType(task_data["recipient"]),
                    type=MessageType(task_data["type"]),
                    payload=json.loads(task_data["payload"]),
                    priority=int(task_data["priority"]),
                    timestamp=datetime.fromisoformat(task_data["timestamp"]),
                    task_id=task_id,
                )
        return None

    def mark_started(self, task_id: str, agent: AgentType) -> None:
        """Mark task as started, record start time.

        Args:
            task_id: Task identifier
            agent: Agent starting the task
        """
        self.redis.hset(f"task:{task_id}", mapping={
            "status": "running",
            "start_time": datetime.now().isoformat(),
        })
        self.redis.publish("events:orchestrator", json.dumps({
            "event": "task_started",
            "task_id": task_id,
            "agent": agent.value,
        }))

    def mark_completed(self, task_id: str, duration_ms: int) -> None:
        """Mark task as completed, record duration, update bottleneck metrics.

        Args:
            task_id: Task identifier
            duration_ms: Task duration in milliseconds
        """
        self.redis.hset(f"task:{task_id}", mapping={
            "status": "complete",
            "duration": duration_ms,
            "completed_at": datetime.now().isoformat(),
        })

        # Update bottleneck analysis (sorted set by duration)
        self.redis.zadd("tasks:by_duration", {task_id: duration_ms})

        # Publish completion event
        task_data = self.redis.hgetall(f"task:{task_id}")
        self.redis.publish("events:orchestrator", json.dumps({
            "event": "task_completed",
            "task_id": task_id,
            "agent": task_data["recipient"],
            "duration_ms": duration_ms,
        }))

    def get_slowest_tasks(self, limit: int = 10) -> List[dict]:
        """Get slowest tasks for bottleneck analysis.

        Args:
            limit: Number of slowest tasks to return

        Returns:
            List of task metadata sorted by duration (slowest first)
        """
        # Get task IDs sorted by duration (descending)
        task_ids = self.redis.zrevrange("tasks:by_duration", 0, limit - 1, withscores=True)

        results = []
        for task_id, duration_ms in task_ids:
            task_data = self.redis.hgetall(f"task:{task_id}")
            results.append({
                "task_id": task_id,
                "duration_ms": duration_ms,
                "agent": task_data["recipient"],
                "type": task_data["type"],
                "timestamp": task_data["timestamp"],
            })
        return results

    def broadcast(self, message: Message) -> None:
        """Broadcast message to all agents via Pub/Sub.

        Args:
            message: Message to broadcast
        """
        self.redis.publish("events:orchestrator", json.dumps({
            "event": "broadcast",
            "sender": message.sender.value,
            "type": message.type.value,
            "payload": message.payload,
        }))

    def _get_priority_level(self, priority: int) -> str:
        """Map priority (1-10) to priority level (high/normal/low).

        Args:
            priority: Priority value (1=highest, 10=lowest)

        Returns:
            Priority level: "high" (1-3), "normal" (4-6), "low" (7-10)
        """
        if priority <= 3:
            return "high"
        elif priority <= 6:
            return "normal"
        else:
            return "low"
```

**Redis Data Structures**:

```
# Task Metadata (Hash)
task:{uuid}
├── sender: "architect"
├── recipient: "code_developer"
├── type: "TASK_DELEGATE"
├── payload: '{"spec_id": "SPEC-071"}'
├── priority: 2
├── timestamp: "2025-10-18T10:30:00"
├── status: "queued" | "running" | "complete" | "failed"
├── start_time: "2025-10-18T10:30:05" (when started)
├── duration: 1500 (milliseconds, when completed)
└── completed_at: "2025-10-18T10:30:06.5"

# Priority Queues (Lists)
queue:high:code_developer → [task_id_1, task_id_2, ...]
queue:normal:code_developer → [task_id_3, task_id_4, ...]
queue:low:code_developer → [task_id_5, task_id_6, ...]

# Bottleneck Analysis (Sorted Set)
tasks:by_duration
├── task_id_1: 3500 (ms)
├── task_id_2: 2800 (ms)
└── task_id_3: 1500 (ms)

# Pub/Sub Channel
events:orchestrator
└── {event: "task_completed", task_id: "...", duration_ms: 1500}
```

**Migration from POC-072**:

POC-072 uses in-memory `multiprocessing.Queue`. Migration to Redis requires:

1. **Install dependencies** (✅ pre-approved):
   ```bash
   poetry add redis hiredis
   ```

2. **Start Redis** (development):
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   # Or: brew install redis && redis-server
   ```

3. **Update TeamDaemon** to use Redis-based MessageQueue:
   ```python
   # Before (POC-072):
   self.message_queue = MessageQueue()  # In-memory

   # After (Production):
   self.message_queue = MessageQueue(
       redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0")
   )
   ```

4. **Zero changes to agent code** - `MessageQueue` API remains identical

5. **Fallback for testing** - Use FakeRedis for unit tests (no Redis server required)

**Performance**:
- Redis throughput: 100K+ ops/sec (far exceeds orchestrator needs ~10-50 msg/min)
- Latency: <1ms for `LPUSH`/`RPOP` operations
- Memory: ~1KB per task (10K tasks = 10MB)
- Persistence: AOF (Append-Only File) ensures durability

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

### Phase 1: Core Infrastructure (Week 1, 18-22 hours)

**Day 1-2: Team Daemon Framework** (8-10 hours)
- Create `TeamDaemon` class
- Implement agent process management
- Add health monitoring
- Implement graceful shutdown

**Day 3: Redis-Based Message Queue** (6-7 hours) ⭐ UPDATED
- Install Redis dependencies (`poetry add redis hiredis`) ✅ Pre-approved
- Implement `MessageQueue` class with Redis backend
  - Task queuing (LPUSH/RPOP with priority levels)
  - Task metadata storage (Redis Hashes)
  - Duration tracking (`mark_started`, `mark_completed`)
  - Bottleneck analysis (Redis Sorted Sets)
  - Pub/Sub for real-time events
- Add FakeRedis fallback for testing (no server required)
- Create `RedisConfig` dataclass for connection settings

**Day 4: Testing & Integration** (4-5 hours)
- Unit tests for TeamDaemon (with FakeRedis)
- Integration tests for agent spawning
- Health check tests
- Redis message queue tests (priority ordering, persistence)

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

**Implementation**: Redis Sorted Sets + Pub/Sub

```python
# In TeamDaemon._coordination_loop()
def _check_bottlenecks(self) -> None:
    """Check for performance bottlenecks every 5 minutes."""
    slowest_tasks = self.message_queue.get_slowest_tasks(limit=10)

    for task in slowest_tasks:
        if task["duration_ms"] > 30000:  # >30 seconds
            logger.warning(
                f"BOTTLENECK: {task['agent']} task {task['task_id']} "
                f"took {task['duration_ms']}ms (type: {task['type']})"
            )

            # Send notification to project_manager
            self._notify_bottleneck(task)

    # Calculate percentiles
    p50, p95, p99 = self._get_percentiles()
    logger.info(f"Task durations: p50={p50}ms, p95={p95}ms, p99={p99}ms")
```

### Bottleneck Metrics Dashboard

**Query Examples**:

```python
# Get slowest 10 tasks
slowest = queue.get_slowest_tasks(limit=10)
# → [{task_id, duration_ms, agent, type, timestamp}, ...]

# Get average duration per agent
for agent_type in AgentType:
    tasks = redis.keys(f"task:*")
    agent_tasks = [
        redis.hget(task, "duration")
        for task in tasks
        if redis.hget(task, "recipient") == agent_type.value
    ]
    avg_duration = sum(agent_tasks) / len(agent_tasks) if agent_tasks else 0
    print(f"{agent_type.value}: avg={avg_duration}ms")

# Get 95th percentile duration
total_tasks = redis.zcard("tasks:by_duration")
p95_index = int(total_tasks * 0.05)  # Top 5%
p95_tasks = redis.zrevrange("tasks:by_duration", 0, p95_index, withscores=True)
p95_duration = p95_tasks[-1][1] if p95_tasks else 0
print(f"95th percentile: {p95_duration}ms")
```

### Langfuse Integration for Observability

**Redis Pub/Sub → Langfuse Exporter**:

```python
class LangfuseExporter:
    """Export Redis events to Langfuse for observability."""

    def __init__(self, redis_url: str, langfuse_client):
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("events:orchestrator")
        self.langfuse = langfuse_client

    def run(self):
        """Listen to Redis events and export to Langfuse."""
        for message in self.pubsub.listen():
            if message["type"] == "message":
                event = json.loads(message["data"])

                if event["event"] == "task_completed":
                    # Export to Langfuse
                    self.langfuse.trace(
                        name=f"task_{event['task_id']}",
                        metadata={
                            "agent": event["agent"],
                            "duration_ms": event["duration_ms"],
                            "timestamp": datetime.now().isoformat(),
                        },
                    )

# Start in background thread
exporter = LangfuseExporter(redis_url, langfuse_client)
threading.Thread(target=exporter.run, daemon=True).start()
```

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

**Implementation**:

```python
def _check_alerts(self):
    """Check alerting rules and send notifications."""
    # Check slow tasks
    for task in self.message_queue.get_slowest_tasks(limit=100):
        if task["duration_ms"] > self.config.slow_task_threshold:
            self._send_alert(
                severity="warning",
                title=f"Slow task detected: {task['task_id']}",
                details=f"Duration: {task['duration_ms']}ms (threshold: {self.config.slow_task_threshold}ms)",
            )

    # Check p95
    p95 = self._get_p95_duration()
    if p95 > self.config.p95_threshold:
        self._send_alert(
            severity="warning",
            title=f"High p95 duration: {p95}ms",
            details=f"Threshold: {self.config.p95_threshold}ms",
        )

    # Check queue depth
    queue_depth = sum([
        self.redis.llen(f"queue:high:{agent.value}") +
        self.redis.llen(f"queue:normal:{agent.value}") +
        self.redis.llen(f"queue:low:{agent.value}")
        for agent in AgentType
    ])
    if queue_depth > self.config.max_queue_depth:
        self._send_alert(
            severity="critical",
            title=f"Queue depth critical: {queue_depth} tasks",
            details=f"Threshold: {self.config.max_queue_depth}",
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

# View real-time Redis events ⭐ NEW
poetry run team-daemon events --follow
# Output (streaming):
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
| **Inter-Agent Latency** | <1 second | Message queue latency (Redis LPUSH/RPOP) |
| **Message Persistence** ⭐ NEW | 100% | Messages survive daemon crashes (Redis AOF) |
| **Bottleneck Detection** ⭐ NEW | <5 min | Time to identify slow tasks (p95 > 30s) |
| **Task Duration Tracking** ⭐ NEW | 100% | All tasks have start/completion timestamps |
| **Observability** ⭐ NEW | Real-time | Live event stream via Redis Pub/Sub |

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
    backend: redis  # Production: redis, Development: memory, Testing: fakeredis
    redis_url: redis://localhost:6379/0  # Or use REDIS_URL env var
    # Connection pooling
    max_connections: 50
    socket_timeout: 5  # seconds
    socket_connect_timeout: 5  # seconds
    # Persistence
    aof_enabled: true  # Append-Only File for durability
    # Retention
    task_ttl: 604800  # 7 days (tasks expire after 7 days)
    max_tasks: 10000  # Max tasks in bottleneck analysis

  health_check:
    interval: 30  # seconds
    timeout: 5    # seconds

  resource_limits:
    max_memory_mb: 500
    max_cpu_percent: 50

  observability:
    langfuse:
      enabled: true
      # Subscribe to Redis Pub/Sub for real-time metrics
      pubsub_channel: events:orchestrator
      # Export metrics every N seconds
      export_interval: 60
```

**Environment Variables**:

```bash
# Redis connection (overrides config)
export REDIS_URL="redis://localhost:6379/0"

# For production (managed Redis):
export REDIS_URL="redis://user:password@redis.example.com:6379/0"

# For development (local Redis):
export REDIS_URL="redis://localhost:6379/0"

# For testing (FakeRedis, no server required):
export REDIS_BACKEND="fakeredis"
```

---

**Created**: 2025-10-18
**Author**: architect agent
**Version**: 1.0
**Status**: Draft (Pending Review)
