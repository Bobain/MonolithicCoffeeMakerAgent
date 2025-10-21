# SPEC-062: Orchestrator Agent Architecture

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: ACE Framework Phase 4 - Orchestrator Implementation

---

## Executive Summary

This specification defines the **Orchestrator Agent**, a new autonomous agent responsible for coordinating multi-agent workflows, measuring performance metrics (response times, queue wait times), detecting bottlenecks, and optimizing team efficiency.

**Key Capabilities**:
- **Message Bus Coordination**: Routes requests between agents using a pub/sub architecture
- **Performance Monitoring**: Tracks agent response times, queue depths, waiting times
- **Bottleneck Detection**: Identifies slow agents, queue congestion, circular dependencies
- **Workflow Optimization**: Suggests parallel execution opportunities, reordering strategies
- **Health Reporting**: Real-time dashboard of agent health and system throughput

**Integration**: Orchestrator sits between `user_listener` and all other agents, providing transparent coordination without breaking existing workflows.

**Impact**:
- **Faster Response Times**: Parallel execution of independent tasks (2-3x speedup)
- **Bottleneck Visibility**: Identify which agents are overloaded (e.g., architect creating specs)
- **Queue Management**: Prevent request pile-ups by load balancing or prioritization
- **Better UX**: Users see progress across multiple agents simultaneously

---

## Problem Statement

### Current Pain Points

**1. Sequential Execution Bottleneck**
```
Current Workflow (Sequential):
User → user_listener → architect (3 min)
                     → code_developer (20 min) ← BLOCKED waiting for architect
                     → project_manager (2 min) ← BLOCKED waiting for code_developer

Total Time: 3 + 20 + 2 = 25 minutes
```

**Problem**: Independent tasks run sequentially, wasting time when they could run in parallel.

**2. No Performance Visibility**
- User doesn't know which agent is slow
- Can't tell if architect is still working or stuck
- No way to measure improvement over time
- Queue depth invisible (how many tasks pending?)

**3. No Bottleneck Detection**
- If architect takes 10 minutes on a spec, user has no warning
- Queue pile-ups can occur (multiple requests waiting for same agent)
- Circular dependencies not detected (Agent A waits for B, B waits for A)

**4. Manual Coordination Required**
- user_listener must manually decide: "Can I run these in parallel?"
- No automatic detection of independence (e.g., "architect creating spec" and "project_manager checking GitHub" are independent)
- Human judgment required for optimization

### User Requirements

From ACE Framework Phase 4:
- **Multi-Agent Coordination**: Orchestrator manages workflows across all agents
- **Message Bus**: Pub/sub architecture for agent communication
- **Performance Tracking**: Response time, queue wait time, bottleneck analysis
- **Parallel Execution**: Automatically detect and execute independent tasks concurrently
- **Health Dashboard**: Real-time view of agent status and system throughput

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────────┐                                                │
│  │user_listener │  (PRIMARY UI - routes ALL user requests)      │
│  └──────┬───────┘                                                │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR AGENT ⭐ NEW                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Message Bus                               │ │
│  │  - Task Queue (FIFO + Priority)                            │ │
│  │  - Pub/Sub Topics (agent.architect, agent.code_developer) │ │
│  │  - Request Routing                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Performance Monitor                             │ │
│  │  - Response Time Tracker                                   │ │
│  │  - Queue Depth Analyzer                                    │ │
│  │  - Bottleneck Detector                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Workflow Optimizer                               │ │
│  │  - Dependency Analyzer (detect independence)               │ │
│  │  - Parallel Executor (run concurrent tasks)                │ │
│  │  - Priority Scheduler (critical-first execution)           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                                 │
│  ┌────────────┐ ┌────────────────┐ ┌───────────────────┐       │
│  │ architect  │ │ code_developer │ │ project_manager   │       │
│  └────────────┘ └────────────────┘ └───────────────────┘       │
│  ┌────────────┐ ┌────────────────┐ ┌───────────────────┐       │
│  │ assistant  │ │ reflector      │ │ curator           │       │
│  └────────────┘ └────────────────┘ └───────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Example

**Scenario**: User requests "Create spec for caching layer and check GitHub PRs"

**Before Orchestrator (Sequential)**:
```
user_listener → architect (create spec)      [3 minutes]
             → project_manager (check PRs)   [2 minutes]  ← BLOCKED
Total: 5 minutes
```

**After Orchestrator (Parallel)**:
```
user_listener → orchestrator
             → architect (create spec)       [3 minutes] ┐
             → project_manager (check PRs)   [2 minutes] ┴→ PARALLEL
Total: 3 minutes (faster of the two)
```

**Orchestrator Workflow**:
1. Receives 2 tasks from user_listener
2. Analyzes dependencies: Independent (spec creation doesn't need PR status)
3. Publishes to message bus:
   - Topic: `agent.architect`, Payload: {task: "create spec", priority: HIGH}
   - Topic: `agent.project_manager`, Payload: {task: "check PRs", priority: MEDIUM}
4. Both agents consume tasks in parallel
5. Orchestrator tracks progress:
   - architect: Started 10:00:00, ETA 3 min
   - project_manager: Started 10:00:00, ETA 2 min
6. Aggregates results when both complete
7. Returns to user_listener

---

## Component Design

### 1. Message Bus

**Purpose**: Asynchronous communication between orchestrator and agents

**Architecture**: In-memory pub/sub with SQLite persistence (for reliability)

**Components**:

```python
# coffee_maker/orchestrator/message_bus.py

from dataclasses import dataclass
from typing import Dict, List, Callable
from enum import Enum
import threading
import queue

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class Task:
    """A task to be executed by an agent."""
    id: str                     # Unique task ID (UUID)
    agent_type: str             # "architect", "code_developer", etc.
    payload: Dict               # Task-specific data
    priority: Priority          # Execution priority
    dependencies: List[str]     # Task IDs this task depends on
    created_at: float           # Timestamp
    timeout_seconds: int = 600  # Max execution time (10 minutes)

@dataclass
class TaskResult:
    """Result of a completed task."""
    task_id: str
    status: str                 # "success", "failure", "timeout"
    result: Dict                # Agent's response
    execution_time_seconds: float
    error: str = None           # Error message if failed

class MessageBus:
    """
    In-memory pub/sub message bus with persistence.

    Features:
    - Topic-based routing (agent.architect, agent.code_developer)
    - Priority queue (CRITICAL > HIGH > MEDIUM > LOW)
    - Task persistence (SQLite for crash recovery)
    - Dead letter queue (failed tasks)
    """

    def __init__(self, db_path: str = "data/orchestrator/message_bus.db"):
        self.topics: Dict[str, queue.PriorityQueue] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.pending_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.db_path = db_path
        self._lock = threading.Lock()
        self._initialize_db()

    def publish(self, topic: str, task: Task):
        """
        Publish a task to a topic.

        Args:
            topic: Topic name (e.g., "agent.architect")
            task: Task to execute
        """
        with self._lock:
            # Persist task to DB (crash recovery)
            self._persist_task(task)

            # Add to priority queue
            if topic not in self.topics:
                self.topics[topic] = queue.PriorityQueue()

            # Queue item: (priority_value, task)
            # Lower priority value = higher priority
            self.topics[topic].put((task.priority.value, task))

            # Track pending task
            self.pending_tasks[task.id] = task

            # Notify subscribers
            self._notify_subscribers(topic, task)

    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to a topic.

        Args:
            topic: Topic name
            callback: Function to call when task published
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    def consume(self, topic: str, timeout: float = 1.0) -> Task:
        """
        Consume next task from topic.

        Args:
            topic: Topic name
            timeout: Max wait time in seconds

        Returns:
            Task object or None if timeout
        """
        if topic not in self.topics:
            return None

        try:
            priority_value, task = self.topics[topic].get(timeout=timeout)
            return task
        except queue.Empty:
            return None

    def complete_task(self, task_id: str, result: TaskResult):
        """
        Mark task as completed.

        Args:
            task_id: Task ID
            result: Execution result
        """
        with self._lock:
            # Remove from pending
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]

            # Add to completed
            self.completed_tasks[task_id] = result

            # Persist result to DB
            self._persist_result(result)

    def get_queue_depth(self, topic: str) -> int:
        """Get number of pending tasks in topic queue."""
        if topic not in self.topics:
            return 0
        return self.topics[topic].qsize()

    def get_pending_tasks(self, agent_type: str = None) -> List[Task]:
        """Get all pending tasks (optionally filtered by agent)."""
        if agent_type:
            return [t for t in self.pending_tasks.values() if t.agent_type == agent_type]
        return list(self.pending_tasks.values())

    # ... (DB methods: _initialize_db, _persist_task, _persist_result)
```

**Why In-Memory + SQLite?**
- **In-Memory**: Fast for real-time operations
- **SQLite**: Crash recovery (tasks not lost if orchestrator restarts)
- **No External Dependency**: No Redis/RabbitMQ needed (simpler deployment)

### 2. Performance Monitor

**Purpose**: Track agent performance and identify bottlenecks

```python
# coffee_maker/orchestrator/performance_monitor.py

from dataclasses import dataclass
from typing import Dict, List
import time

@dataclass
class AgentMetrics:
    """Performance metrics for a single agent."""
    agent_type: str
    total_tasks: int                    # Total tasks executed
    completed_tasks: int                # Successfully completed
    failed_tasks: int                   # Failed tasks
    average_response_time: float        # Seconds
    p95_response_time: float            # 95th percentile (seconds)
    p99_response_time: float            # 99th percentile (seconds)
    queue_depth: int                    # Current pending tasks
    average_queue_wait_time: float      # Time tasks spend in queue
    last_task_completed_at: float       # Timestamp

@dataclass
class BottleneckReport:
    """Detected bottleneck analysis."""
    agent_type: str
    severity: str                       # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    reason: str                         # Human-readable explanation
    queue_depth: int
    average_wait_time: float
    suggested_actions: List[str]        # Mitigation recommendations

class PerformanceMonitor:
    """
    Tracks agent performance and detects bottlenecks.

    Metrics Tracked:
    - Response time (how long agent takes to complete task)
    - Queue wait time (how long task waits before agent starts)
    - Queue depth (how many tasks pending for agent)
    - Success/failure rates
    """

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.metrics: Dict[str, AgentMetrics] = {}
        self.response_times: Dict[str, List[float]] = {}  # For percentile calc
        self.queue_wait_times: Dict[str, List[float]] = {}

    def record_task_start(self, agent_type: str, task_id: str):
        """Record when agent starts executing task."""
        # Calculate queue wait time
        task = self.message_bus.pending_tasks.get(task_id)
        if task:
            wait_time = time.time() - task.created_at
            if agent_type not in self.queue_wait_times:
                self.queue_wait_times[agent_type] = []
            self.queue_wait_times[agent_type].append(wait_time)

    def record_task_complete(self, agent_type: str, result: TaskResult):
        """Record task completion and update metrics."""
        # Initialize metrics if needed
        if agent_type not in self.metrics:
            self.metrics[agent_type] = AgentMetrics(
                agent_type=agent_type,
                total_tasks=0,
                completed_tasks=0,
                failed_tasks=0,
                average_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                queue_depth=0,
                average_queue_wait_time=0.0,
                last_task_completed_at=0.0
            )

        metrics = self.metrics[agent_type]

        # Update counts
        metrics.total_tasks += 1
        if result.status == "success":
            metrics.completed_tasks += 1
        else:
            metrics.failed_tasks += 1

        # Update response times
        if agent_type not in self.response_times:
            self.response_times[agent_type] = []
        self.response_times[agent_type].append(result.execution_time_seconds)

        # Calculate percentiles
        sorted_times = sorted(self.response_times[agent_type])
        n = len(sorted_times)
        metrics.average_response_time = sum(sorted_times) / n
        metrics.p95_response_time = sorted_times[int(n * 0.95)] if n > 0 else 0
        metrics.p99_response_time = sorted_times[int(n * 0.99)] if n > 0 else 0

        # Update queue metrics
        metrics.queue_depth = self.message_bus.get_queue_depth(f"agent.{agent_type}")

        wait_times = self.queue_wait_times.get(agent_type, [])
        if wait_times:
            metrics.average_queue_wait_time = sum(wait_times) / len(wait_times)

        metrics.last_task_completed_at = time.time()

    def detect_bottlenecks(self) -> List[BottleneckReport]:
        """
        Analyze metrics and detect bottlenecks.

        Bottleneck Criteria:
        - HIGH: Queue depth > 5 AND average wait time > 5 minutes
        - MEDIUM: Queue depth > 3 AND average wait time > 3 minutes
        - LOW: Response time > 10 minutes (slow but not queued)
        """
        bottlenecks = []

        for agent_type, metrics in self.metrics.items():
            # Check queue depth bottleneck
            if metrics.queue_depth > 5 and metrics.average_queue_wait_time > 300:
                bottlenecks.append(BottleneckReport(
                    agent_type=agent_type,
                    severity="HIGH",
                    reason=f"Queue backed up: {metrics.queue_depth} tasks waiting {metrics.average_queue_wait_time:.0f}s avg",
                    queue_depth=metrics.queue_depth,
                    average_wait_time=metrics.average_queue_wait_time,
                    suggested_actions=[
                        "Consider parallel execution if tasks are independent",
                        "Prioritize critical tasks",
                        "Scale out agent instances (future enhancement)"
                    ]
                ))
            elif metrics.queue_depth > 3 and metrics.average_queue_wait_time > 180:
                bottlenecks.append(BottleneckReport(
                    agent_type=agent_type,
                    severity="MEDIUM",
                    reason=f"Queue growing: {metrics.queue_depth} tasks waiting {metrics.average_queue_wait_time:.0f}s avg",
                    queue_depth=metrics.queue_depth,
                    average_wait_time=metrics.average_queue_wait_time,
                    suggested_actions=[
                        "Monitor queue depth closely",
                        "Review task priorities"
                    ]
                ))

            # Check slow response time
            if metrics.p95_response_time > 600:  # 10 minutes
                bottlenecks.append(BottleneckReport(
                    agent_type=agent_type,
                    severity="LOW",
                    reason=f"Slow response: p95={metrics.p95_response_time:.0f}s",
                    queue_depth=metrics.queue_depth,
                    average_wait_time=metrics.average_queue_wait_time,
                    suggested_actions=[
                        "Profile agent performance",
                        "Check for hanging LLM calls",
                        "Review spec complexity (if architect)"
                    ]
                ))

        return sorted(bottlenecks, key=lambda b: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[b.severity])

    def get_dashboard_data(self) -> Dict:
        """Get real-time dashboard data."""
        return {
            "metrics": {agent: vars(metrics) for agent, metrics in self.metrics.items()},
            "bottlenecks": [vars(b) for b in self.detect_bottlenecks()],
            "queue_depths": {
                agent: self.message_bus.get_queue_depth(f"agent.{agent}")
                for agent in self.metrics.keys()
            },
            "timestamp": time.time()
        }
```

### 3. Workflow Optimizer

**Purpose**: Detect task independence and enable parallel execution

```python
# coffee_maker/orchestrator/workflow_optimizer.py

from dataclasses import dataclass
from typing import List, Set, Dict
import networkx as nx  # For dependency graph analysis

@dataclass
class WorkflowPlan:
    """Execution plan for a workflow."""
    sequential_batches: List[List[Task]]  # [[task1, task2], [task3]]
    execution_time_estimate: float        # Estimated total time (seconds)
    parallelism_factor: float             # Speedup vs sequential (1.0 = no speedup)

class WorkflowOptimizer:
    """
    Analyzes task dependencies and creates optimized execution plans.

    Key Capabilities:
    - Detect independent tasks (can run in parallel)
    - Identify dependency chains (must run sequentially)
    - Create batched execution plan (minimize total time)
    """

    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor

    def analyze_dependencies(self, tasks: List[Task]) -> nx.DiGraph:
        """
        Build dependency graph for tasks.

        Returns:
            Directed graph where edge (A, B) means "B depends on A"
        """
        graph = nx.DiGraph()

        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(task.id, task=task)

        # Add dependency edges
        for task in tasks:
            for dep_id in task.dependencies:
                # Edge: dependency → task
                graph.add_edge(dep_id, task.id)

        return graph

    def create_execution_plan(self, tasks: List[Task]) -> WorkflowPlan:
        """
        Create optimized execution plan.

        Algorithm:
        1. Build dependency graph
        2. Topological sort to get valid execution order
        3. Group independent tasks into parallel batches
        4. Estimate execution time for each batch
        """
        graph = self.analyze_dependencies(tasks)

        # Detect cycles (circular dependencies)
        if not nx.is_directed_acyclic_graph(graph):
            cycles = list(nx.simple_cycles(graph))
            raise ValueError(f"Circular dependencies detected: {cycles}")

        # Topological sort (valid execution order)
        execution_order = list(nx.topological_sort(graph))

        # Group into parallel batches
        batches = []
        remaining_tasks = {task.id: task for task in tasks}
        completed = set()

        while remaining_tasks:
            # Find tasks whose dependencies are all completed
            ready_tasks = [
                task for task_id, task in remaining_tasks.items()
                if all(dep in completed for dep in task.dependencies)
            ]

            if not ready_tasks:
                break  # Should not happen if graph is DAG

            # This batch can run in parallel
            batches.append(ready_tasks)

            # Mark as completed
            for task in ready_tasks:
                completed.add(task.id)
                del remaining_tasks[task.id]

        # Estimate execution time
        batch_times = []
        for batch in batches:
            # Batch time = max(task times in batch) since they run in parallel
            max_time = max(
                self._estimate_task_time(task)
                for task in batch
            )
            batch_times.append(max_time)

        total_time = sum(batch_times)

        # Calculate parallelism factor
        sequential_time = sum(self._estimate_task_time(task) for task in tasks)
        parallelism_factor = sequential_time / total_time if total_time > 0 else 1.0

        return WorkflowPlan(
            sequential_batches=batches,
            execution_time_estimate=total_time,
            parallelism_factor=parallelism_factor
        )

    def _estimate_task_time(self, task: Task) -> float:
        """
        Estimate task execution time based on historical metrics.

        Uses agent's average response time, or default if no history.
        """
        metrics = self.performance_monitor.metrics.get(task.agent_type)
        if metrics and metrics.average_response_time > 0:
            return metrics.average_response_time

        # Default estimates by agent type
        defaults = {
            "architect": 180.0,         # 3 minutes (spec creation)
            "code_developer": 600.0,    # 10 minutes (implementation)
            "project_manager": 60.0,    # 1 minute (status check)
            "assistant": 30.0,          # 30 seconds (quick query)
            "reflector": 120.0,         # 2 minutes (trace analysis)
            "curator": 90.0             # 1.5 minutes (playbook update)
        }

        return defaults.get(task.agent_type, 120.0)  # Default: 2 minutes
```

### 4. Orchestrator Agent

**Purpose**: Main orchestration logic that ties everything together

```python
# coffee_maker/orchestrator/orchestrator_agent.py

from coffee_maker.orchestrator.message_bus import MessageBus, Task, TaskResult, Priority
from coffee_maker.orchestrator.performance_monitor import PerformanceMonitor
from coffee_maker.orchestrator.workflow_optimizer import WorkflowOptimizer
from coffee_maker.langfuse_observe import observe
import threading
import time
import uuid

class OrchestratorAgent:
    """
    Orchestrator Agent: Coordinates multi-agent workflows.

    Responsibilities:
    - Route tasks to agents via message bus
    - Monitor performance and detect bottlenecks
    - Optimize workflows with parallel execution
    - Provide health dashboard
    """

    def __init__(self):
        self.message_bus = MessageBus()
        self.performance_monitor = PerformanceMonitor(self.message_bus)
        self.workflow_optimizer = WorkflowOptimizer(self.performance_monitor)
        self.running = False
        self._worker_thread = None

    @observe(name="orchestrator_submit_task")
    def submit_task(
        self,
        agent_type: str,
        payload: Dict,
        priority: Priority = Priority.MEDIUM,
        dependencies: List[str] = None
    ) -> str:
        """
        Submit a task to be executed by an agent.

        Args:
            agent_type: Agent to execute task (e.g., "architect")
            payload: Task-specific data
            priority: Execution priority
            dependencies: Task IDs this task depends on

        Returns:
            Task ID (UUID)
        """
        task = Task(
            id=str(uuid.uuid4()),
            agent_type=agent_type,
            payload=payload,
            priority=priority,
            dependencies=dependencies or [],
            created_at=time.time()
        )

        # Publish to message bus
        topic = f"agent.{agent_type}"
        self.message_bus.publish(topic, task)

        return task.id

    @observe(name="orchestrator_submit_workflow")
    def submit_workflow(self, tasks: List[Dict]) -> WorkflowPlan:
        """
        Submit multiple tasks with dependency optimization.

        Args:
            tasks: List of task definitions
                [
                    {
                        "agent_type": "architect",
                        "payload": {...},
                        "priority": "HIGH",
                        "dependencies": []
                    },
                    ...
                ]

        Returns:
            WorkflowPlan with optimized execution batches
        """
        # Create Task objects
        task_objects = []
        for task_def in tasks:
            task = Task(
                id=str(uuid.uuid4()),
                agent_type=task_def["agent_type"],
                payload=task_def["payload"],
                priority=Priority[task_def.get("priority", "MEDIUM")],
                dependencies=task_def.get("dependencies", []),
                created_at=time.time()
            )
            task_objects.append(task)

        # Create execution plan
        plan = self.workflow_optimizer.create_execution_plan(task_objects)

        # Submit tasks in optimized batches
        for batch in plan.sequential_batches:
            # Submit all tasks in batch (will execute in parallel)
            for task in batch:
                topic = f"agent.{task.agent_type}"
                self.message_bus.publish(topic, task)

        return plan

    def wait_for_task(self, task_id: str, timeout: float = 600.0) -> TaskResult:
        """
        Wait for a task to complete.

        Args:
            task_id: Task ID
            timeout: Max wait time in seconds

        Returns:
            TaskResult

        Raises:
            TimeoutError: If task doesn't complete in time
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if task completed
            if task_id in self.message_bus.completed_tasks:
                return self.message_bus.completed_tasks[task_id]

            # Sleep briefly
            time.sleep(0.1)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        return self.performance_monitor.get_dashboard_data()

    def detect_bottlenecks(self):
        """Detect and report bottlenecks."""
        return self.performance_monitor.detect_bottlenecks()

    def start(self):
        """Start orchestrator background worker."""
        self.running = True
        self._worker_thread = threading.Thread(target=self._background_worker, daemon=True)
        self._worker_thread.start()

    def stop(self):
        """Stop orchestrator background worker."""
        self.running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)

    def _background_worker(self):
        """
        Background worker that monitors queues and reports bottlenecks.

        Runs every 30 seconds:
        - Check queue depths
        - Detect bottlenecks
        - Log warnings if queues backing up
        """
        while self.running:
            time.sleep(30)  # Check every 30 seconds

            # Detect bottlenecks
            bottlenecks = self.detect_bottlenecks()

            if bottlenecks:
                for bottleneck in bottlenecks:
                    if bottleneck.severity in ["HIGH", "CRITICAL"]:
                        # Log warning
                        print(f"⚠️ BOTTLENECK DETECTED: {bottleneck.agent_type} ({bottleneck.severity})")
                        print(f"   Reason: {bottleneck.reason}")
                        print(f"   Suggestions: {', '.join(bottleneck.suggested_actions)}")
```

---

## Agent Integration

### How Agents Consume Tasks

Each agent needs to be updated to consume tasks from message bus:

```python
# Example: architect agent integration

from coffee_maker.orchestrator.orchestrator_agent import OrchestratorAgent

# In architect startup
orchestrator = OrchestratorAgent()

# Subscribe to architect topic
def handle_architect_task(task):
    """Handle task delegated to architect."""
    # Extract payload
    spec_type = task.payload.get("spec_type")  # e.g., "technical_spec"
    priority_name = task.payload.get("priority_name")

    # Execute task
    result = create_technical_spec(priority_name)

    # Report result
    orchestrator.message_bus.complete_task(
        task.id,
        TaskResult(
            task_id=task.id,
            status="success" if result else "failure",
            result={"spec_path": result},
            execution_time_seconds=time.time() - task.created_at
        )
    )

orchestrator.message_bus.subscribe("agent.architect", handle_architect_task)
```

### user_listener Integration

user_listener delegates work via orchestrator:

```python
# user_listener submits work to orchestrator

orchestrator = OrchestratorAgent()

# User request: "Create spec for caching and check PRs"
task_ids = []

# Submit architect task
task_ids.append(orchestrator.submit_task(
    agent_type="architect",
    payload={"spec_type": "caching_layer", "priority_name": "PRIORITY 11"},
    priority=Priority.HIGH
))

# Submit project_manager task (independent)
task_ids.append(orchestrator.submit_task(
    agent_type="project_manager",
    payload={"action": "check_prs"},
    priority=Priority.MEDIUM
))

# Wait for both (runs in parallel)
results = [orchestrator.wait_for_task(task_id) for task_id in task_ids]

# Return aggregated results to user
return f"Spec created: {results[0].result['spec_path']}\nPRs checked: {results[1].result}"
```

---

## Startup Skill

Location: `.claude/skills/orchestrator-startup.md`

```markdown
# Orchestrator Agent Startup Skill

**Purpose**: Initialize orchestrator agent with all required components.

## Initialization Steps

1. **Load Message Bus**
   - Initialize SQLite database (data/orchestrator/message_bus.db)
   - Recover pending tasks from previous session
   - Set up topic queues for all agents

2. **Start Performance Monitor**
   - Load historical metrics (if available)
   - Initialize metrics for each agent type
   - Set up bottleneck detection thresholds

3. **Initialize Workflow Optimizer**
   - Load dependency graph templates
   - Set up task time estimation models
   - Initialize parallel execution scheduler

4. **Start Background Worker**
   - Launch monitoring thread (checks every 30s)
   - Set up bottleneck alerting
   - Initialize health dashboard

5. **Register Agent Subscriptions**
   - Subscribe each agent to its topic
   - Set up callback handlers
   - Verify message routing

## Health Checks

- [ ] Message bus operational (can publish/consume)
- [ ] Performance monitor tracking metrics
- [ ] Workflow optimizer creating plans
- [ ] Background worker running
- [ ] All agents subscribed to topics

## Recovery from Crash

If orchestrator crashed:
1. Load pending tasks from SQLite
2. Republish to message bus
3. Resume monitoring
4. Alert user of recovery

## Success Criteria

- Orchestrator agent registered in AgentRegistry
- Message bus operational
- Performance dashboard accessible
- Bottleneck detection active
- All integration tests passing
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_orchestrator_message_bus.py

def test_message_bus_publish_consume():
    """Test basic pub/sub functionality."""
    bus = MessageBus()

    task = Task(
        id="task-1",
        agent_type="architect",
        payload={"action": "create_spec"},
        priority=Priority.HIGH,
        dependencies=[],
        created_at=time.time()
    )

    bus.publish("agent.architect", task)
    consumed_task = bus.consume("agent.architect")

    assert consumed_task.id == "task-1"
    assert consumed_task.priority == Priority.HIGH

def test_priority_ordering():
    """Test that CRITICAL tasks execute before MEDIUM."""
    bus = MessageBus()

    # Publish in reverse priority order
    bus.publish("agent.test", Task(id="medium", priority=Priority.MEDIUM, ...))
    bus.publish("agent.test", Task(id="critical", priority=Priority.CRITICAL, ...))

    # Consume should get CRITICAL first
    task1 = bus.consume("agent.test")
    assert task1.id == "critical"

    task2 = bus.consume("agent.test")
    assert task2.id == "medium"

def test_workflow_optimizer_parallel_detection():
    """Test detection of independent tasks."""
    optimizer = WorkflowOptimizer(mock_performance_monitor)

    tasks = [
        Task(id="task-1", dependencies=[], ...),  # Independent
        Task(id="task-2", dependencies=[], ...),  # Independent
        Task(id="task-3", dependencies=["task-1"], ...)  # Depends on task-1
    ]

    plan = optimizer.create_execution_plan(tasks)

    # Batch 1: task-1 and task-2 (parallel)
    # Batch 2: task-3 (after task-1)
    assert len(plan.sequential_batches) == 2
    assert len(plan.sequential_batches[0]) == 2  # 2 parallel tasks
    assert plan.parallelism_factor > 1.0  # Speedup detected
```

### Integration Tests

```python
# tests/integration/test_orchestrator_workflow.py

def test_parallel_workflow_execution():
    """Test end-to-end parallel workflow execution."""
    orchestrator = OrchestratorAgent()
    orchestrator.start()

    # Submit 2 independent tasks
    task_1 = orchestrator.submit_task("architect", {"action": "spec"})
    task_2 = orchestrator.submit_task("project_manager", {"action": "check_prs"})

    # Both should complete
    result_1 = orchestrator.wait_for_task(task_1, timeout=120)
    result_2 = orchestrator.wait_for_task(task_2, timeout=120)

    assert result_1.status == "success"
    assert result_2.status == "success"

    # Check metrics updated
    metrics = orchestrator.get_metrics()
    assert "architect" in metrics["metrics"]
    assert metrics["metrics"]["architect"]["total_tasks"] >= 1

    orchestrator.stop()
```

---

## Rollout Plan

### Phase 1: Infrastructure (Week 1)
- [ ] Implement MessageBus with SQLite persistence
- [ ] Implement PerformanceMonitor
- [ ] Implement WorkflowOptimizer
- [ ] Unit tests (>80% coverage)

### Phase 2: Orchestrator Agent (Week 2)
- [ ] Implement OrchestratorAgent class
- [ ] Create orchestrator-startup.md skill
- [ ] Integration tests
- [ ] Performance benchmarks

### Phase 3: Agent Integration (Week 3)
- [ ] Update architect to consume from message bus
- [ ] Update code_developer to consume from message bus
- [ ] Update project_manager to consume from message bus
- [ ] Update user_listener to submit via orchestrator

### Phase 4: Architect Code Review ⭐ MANDATORY
- [ ] architect reviews implementation:
  - **Architectural Compliance**: Message bus patterns, agent coordination, delegation model
  - **Code Quality**: Singleton enforcement (AgentRegistry), thread safety (locks, queues)
  - **Security**: Agent isolation, safe task routing, no data leakage between agents
  - **Performance**: Queue latency (<100ms), bottleneck detection accuracy, memory usage
  - **CFR Compliance**:
    - CFR-007: Orchestrator context budget (<30%)
    - CFR-008: Agent boundary enforcement (no direct agent-to-agent calls)
    - CFR-009: Proper error propagation and recovery
  - **Dependency Approval**: If new packages added (e.g., networkx for graph analysis)
- [ ] architect approves or requests changes
- [ ] code_developer addresses feedback (if any)
- [ ] architect gives final approval

### Phase 5: Dashboard & Monitoring (Week 4)
- [ ] Create health dashboard UI
- [ ] Add bottleneck alerts
- [ ] Performance visualization
- [ ] User documentation

---

## Success Metrics

| Metric | Baseline (Before) | Target (After) | Measurement |
|--------|-------------------|----------------|-------------|
| **Average Workflow Time** | 15-25 minutes (sequential) | 8-12 minutes (parallel) | 40-50% reduction |
| **Queue Wait Time** | Unknown (not tracked) | <1 minute (p95) | Real-time monitoring |
| **Bottleneck Detection** | Manual (user complaints) | Automatic (30s checks) | Proactive alerts |
| **Parallel Execution Rate** | 0% (all sequential) | 40-60% (independent tasks) | Workflow analysis |

---

## Risks & Mitigations

### Risk 1: Message Bus Complexity
**Impact**: Adds architectural complexity
**Mitigation**: Start simple (in-memory + SQLite), avoid external dependencies

### Risk 2: Performance Overhead
**Impact**: Orchestrator adds latency to task submission
**Mitigation**: Measure overhead (<100ms target), optimize hot paths

### Risk 3: Integration Burden
**Impact**: All agents need updates
**Mitigation**: Gradual rollout, backward compatibility with direct delegation

---

## Conclusion

The Orchestrator Agent provides the missing coordination layer for multi-agent workflows. By introducing a message bus, performance monitoring, and workflow optimization, we enable:

1. **Parallel Execution**: 40-50% faster workflows by running independent tasks concurrently
2. **Visibility**: Real-time metrics on agent health and queue depths
3. **Bottleneck Detection**: Automatic identification of slow agents or queue pile-ups
4. **Optimized Scheduling**: Priority-based execution and dependency analysis

This specification provides the foundation for Phase 4 of the ACE Framework implementation.

---

**Files to Create**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/message_bus.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/performance_monitor.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/workflow_optimizer.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/orchestrator_agent.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/orchestrator-startup.md`

**Next Steps**:
1. Review and approve this spec
2. Create ADR-011: Orchestrator Agent Addition
3. Assign implementation to code_developer
4. Begin Phase 1 (Infrastructure) implementation
