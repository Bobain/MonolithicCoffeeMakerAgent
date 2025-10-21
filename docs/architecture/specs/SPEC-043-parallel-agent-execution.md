# SPEC-043: Enable Parallel Agent Execution for Faster Delivery

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: US-043 (ROADMAP), US-035 (Singleton), US-038 (Ownership), CFR-000 (Prevent Conflicts)

**Related ADRs**: ADR-003 (Simplification-First Approach)

**Assigned To**: code_developer

**Depends On**: US-035 (Singleton) and US-038 (Ownership) must be complete first

---

## Executive Summary

This specification describes a simple task queue system that enables safe parallel execution of independent agent tasks. Using file ownership checks and singleton enforcement, we dispatch non-conflicting tasks in parallel, achieving 2-4x speedup for independent work without complex orchestration.

---

## Problem Statement

### Current Situation

Agents execute mostly sequentially:
- User requests task for project_manager → waits
- Then requests task for code_developer → waits
- Total time: Sum of all tasks

**User Feedback** (Critical):
> "I don't understand why I hardly see some agents working in parallel: this is not the expected behavior, we want agents to work in parallel as much as possible in order to deliver faster"

**Example**:
```
Sequential: code_developer (30 min) + project_manager (30 min) = 60 minutes
Parallel:   max(code_developer 30 min, project_manager 30 min) = 30 minutes
Speedup: 2x faster! ✨
```

### Goal

Enable safe parallel execution:
- Multiple agents work simultaneously when safe
- Automatic conflict detection (ownership + singleton checks)
- 2-4x speedup for independent tasks
- Simple queue-based dispatch (not complex scheduler)

### Non-Goals

- NOT building complex orchestrator (simple queue + conflict check)
- NOT implementing distributed execution (single-machine only)
- NOT adding resource management (CPU/memory limits → future)
- NOT creating dependency graphs (manual task specification for now)

---

## Requirements

### Functional Requirements

1. **FR-1**: Task queue accepts multiple tasks
2. **FR-2**: Dispatcher checks conflicts before execution (ownership + singleton)
3. **FR-3**: Non-conflicting tasks run in parallel (separate threads/processes)
4. **FR-4**: Conflicting tasks wait in queue (sequential fallback)
5. **FR-5**: Status dashboard shows running + queued tasks

### Non-Functional Requirements

1. **NFR-1**: Performance: 2-4x speedup for independent tasks
2. **NFR-2**: Safety: ZERO file conflicts (guaranteed by ownership + singleton)
3. **NFR-3**: Reliability: Task failures don't crash dispatcher
4. **NFR-4**: Observability: All tasks tracked in Langfuse

### Constraints

- Must integrate with US-035 (singleton enforcement)
- Must integrate with US-038 (ownership enforcement)
- Must work on macOS, Linux (development environments)
- Must not break existing agent workflows

---

## Proposed Solution

### High-Level Approach

**Simple Task Queue with Conflict Detection**:
1. User submits tasks to queue
2. Dispatcher checks if task conflicts with running tasks
3. If no conflict: Start task in parallel
4. If conflict: Wait in queue
5. On task completion: Check queue for waiting tasks

**Why This is Simple**:
- No complex scheduler (just conflict detection)
- Uses existing ownership + singleton checks
- Python `concurrent.futures.ThreadPoolExecutor` (stdlib)
- ~200 lines total implementation

### Architecture Diagram

```
User submits Task A (code_developer)
User submits Task B (project_manager)
User submits Task C (code_developer)
    ↓
Task Queue: [A, B, C]
    ↓
Dispatcher checks conflicts:
  Task A: code_developer on coffee_maker/
    - Singleton: ✅ No other code_developer running
    - Ownership: ✅ code_developer owns coffee_maker/
    → START in parallel
  Task B: project_manager on docs/roadmap/
    - Singleton: ✅ No other project_manager running
    - Ownership: ✅ project_manager owns docs/roadmap/
    → START in parallel (now 2 tasks running!)
  Task C: code_developer on tests/
    - Singleton: ❌ code_developer already running (Task A)
    → WAIT in queue
    ↓
Task A completes → Dispatcher checks queue
    ↓
Task C: code_developer on tests/
    - Singleton: ✅ code_developer now free
    → START (now 2 tasks: B and C)
    ↓
All tasks complete
```

### Safe Parallel Combinations

Thanks to US-035 + US-038, these are SAFE:

| Agent 1 | Files | Agent 2 | Files | Safe? | Why? |
|---------|-------|---------|-------|-------|------|
| code_developer | coffee_maker/ | project_manager | docs/roadmap/ | ✅ YES | Different files (US-038) |
| code_developer | coffee_maker/ | architect | docs/architecture/ | ✅ YES | Different files (US-038) |
| project_manager | docs/roadmap/ | architect | docs/architecture/ | ✅ YES | Different files (US-038) |
| assistant | read-only | code_developer | coffee_maker/ | ✅ YES | assistant read-only |
| code_developer | coffee_maker/ | code_developer | tests/ | ❌ NO | Same agent (US-035 singleton) |

---

## Detailed Design

### Component 1: Task Queue

**File**: `coffee_maker/autonomous/task_queue.py` (~120 lines)

**Purpose**: Queue tasks and dispatch based on conflict checks

**Interface**:
```python
"""
Simple task queue for parallel agent execution.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from typing import List, Optional, Callable
from queue import Queue
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentTask:
    """Represents a task for an agent to execute."""
    agent_type: str
    task_description: str
    files_to_modify: List[str]  # Paths agent will write
    execute_fn: Callable  # Function to run
    priority: int = 0  # Higher = more urgent (future use)

class TaskQueue:
    """
    Queue for parallel agent execution.

    Ensures safe parallel execution using singleton + ownership checks.
    """

    def __init__(self, max_parallel: int = 4):
        """
        Initialize task queue.

        Args:
            max_parallel: Max number of parallel agents (default: 4)
        """
        self.queue: Queue[AgentTask] = Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_parallel)
        self.running_agents: set[str] = set()  # Agent types currently running
        self.running_files: set[str] = set()  # Files currently being modified
        self.lock = threading.Lock()

    def submit_task(self, task: AgentTask) -> Future:
        """
        Submit task to queue.

        Args:
            task: Task to execute

        Returns:
            Future for task result

        Example:
            >>> task = AgentTask(
            ...     agent_type="code_developer",
            ...     task_description="Implement US-035",
            ...     files_to_modify=["coffee_maker/autonomous/agent_singleton.py"],
            ...     execute_fn=lambda: implement_us_035()
            ... )
            >>> future = queue.submit_task(task)
            >>> result = future.result()  # Wait for completion
        """
        logger.info(f"📝 Queued: {task.agent_type} - {task.task_description}")
        return self.executor.submit(self._execute_when_safe, task)

    def _execute_when_safe(self, task: AgentTask):
        """
        Execute task when no conflicts exist.

        Waits until:
        1. Singleton allows (no other instance of same agent)
        2. Ownership allows (no conflicting file writes)
        """
        # Wait for safe execution
        while True:
            with self.lock:
                if self._can_execute_now(task):
                    # Mark resources as in-use
                    self.running_agents.add(task.agent_type)
                    for file_path in task.files_to_modify:
                        self.running_files.add(file_path)
                    break
            # Conflict exists, wait and retry
            logger.info(f"⏳ Waiting: {task.agent_type} (conflict detected)")
            threading.Event().wait(1.0)  # Sleep 1 second, retry

        # Execute task
        logger.info(f"▶️ Started: {task.agent_type} - {task.task_description}")
        try:
            result = task.execute_fn()
            logger.info(f"✅ Completed: {task.agent_type}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed: {task.agent_type} - {e}")
            raise
        finally:
            # Release resources
            with self.lock:
                self.running_agents.discard(task.agent_type)
                for file_path in task.files_to_modify:
                    self.running_files.discard(file_path)
            logger.info(f"🏁 Released: {task.agent_type}")

    def _can_execute_now(self, task: AgentTask) -> bool:
        """
        Check if task can execute without conflicts.

        Returns:
            True if safe to execute now, False if conflict exists
        """
        # Singleton check: Is agent type already running?
        if task.agent_type in self.running_agents:
            logger.debug(f"⛔ Singleton conflict: {task.agent_type} already running")
            return False

        # Ownership check: Are any files currently being modified?
        for file_path in task.files_to_modify:
            if file_path in self.running_files:
                logger.debug(f"⛔ File conflict: {file_path} currently in use")
                return False

        # No conflicts!
        return True

    def get_status(self) -> dict:
        """
        Get current queue status.

        Returns:
            Status dict with running agents and queued tasks

        Example:
            >>> status = queue.get_status()
            >>> print(status)
            {
                "running": ["code_developer", "project_manager"],
                "queued": 2,
                "active_files": ["coffee_maker/daemon.py", "docs/ROADMAP.md"]
            }
        """
        with self.lock:
            return {
                "running_agents": list(self.running_agents),
                "running_files": list(self.running_files),
                "queued_tasks": self.queue.qsize(),
            }

    def shutdown(self, wait: bool = True):
        """
        Shutdown queue and wait for tasks to complete.

        Args:
            wait: If True, wait for running tasks (default: True)
        """
        logger.info("🛑 Shutting down task queue...")
        self.executor.shutdown(wait=wait)
        logger.info("✅ Task queue shutdown complete")
```

**Implementation Notes**:
- `ThreadPoolExecutor` for parallel execution (stdlib)
- `threading.Lock` for thread-safe conflict checks
- Simple busy-wait for conflict resolution (1-second polling)
- Automatic resource cleanup in `finally` block

### Component 2: Integration with user_listener

**File**: `coffee_maker/autonomous/user_listener.py` (existing, minor update)

**Add**:
```python
from coffee_maker.autonomous.task_queue import TaskQueue, AgentTask

# Global task queue
task_queue = TaskQueue(max_parallel=4)

def delegate_tasks_parallel(tasks: List[dict]) -> List[Future]:
    """
    Delegate multiple tasks in parallel when safe.

    Args:
        tasks: List of task dicts with agent_type, description, files

    Returns:
        List of Futures (one per task)

    Example:
        >>> tasks = [
        ...     {"agent_type": "code_developer", "description": "Implement US-035", "files": ["coffee_maker/..."]},
        ...     {"agent_type": "project_manager", "description": "Update ROADMAP", "files": ["docs/roadmap/ROADMAP.md"]},
        ... ]
        >>> futures = delegate_tasks_parallel(tasks)
        >>> results = [f.result() for f in futures]  # Wait for all
    """
    futures = []
    for task_dict in tasks:
        task = AgentTask(
            agent_type=task_dict["agent_type"],
            task_description=task_dict["description"],
            files_to_modify=task_dict.get("files", []),
            execute_fn=lambda t=task_dict: execute_agent_task(t)
        )
        future = task_queue.submit_task(task)
        futures.append(future)

    return futures
```

### Component 3: Status Dashboard

**File**: `scripts/show_parallel_status.py` (~30 lines, NEW)

**Purpose**: Show real-time status of parallel execution

**Interface**:
```bash
python scripts/show_parallel_status.py

# Output:
# 🎯 Parallel Execution Status
# ============================
# Running Agents (2):
#   - code_developer (on coffee_maker/daemon.py)
#   - project_manager (on docs/ROADMAP.md)
#
# Queued Tasks (1):
#   - architect (waiting for code_developer to finish)
#
# Active Files (2):
#   - coffee_maker/daemon.py
#   - docs/ROADMAP.md
#
# Estimated Completion: 15 minutes
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_task_queue.py` (~120 lines, 10 tests)

**Test Cases**:
1. `test_submit_single_task()` - Single task executes
2. `test_parallel_different_agents()` - Different agents run simultaneously
3. `test_singleton_conflict()` - Same agent blocks second instance
4. `test_file_conflict()` - Same file blocks parallel writes
5. `test_sequential_fallback()` - Conflicting tasks wait
6. `test_task_completion_releases()` - Resources released after task
7. `test_status_reporting()` - Status accurately reflects queue state
8. `test_error_handling()` - Failed tasks don't crash queue
9. `test_shutdown_graceful()` - Queue shuts down cleanly
10. `test_max_parallel_limit()` - Respects max_parallel setting

### Integration Tests

**File**: `tests/integration/test_parallel_execution.py` (~80 lines, 5 tests)

**Test Cases**:
1. `test_code_developer_and_project_manager_parallel()` - Real agents run together
2. `test_three_agents_parallel()` - code_developer + project_manager + architect
3. `test_duplicate_agent_blocks()` - Two code_developer tasks → sequential
4. `test_overlapping_files_blocks()` - Two agents, same file → sequential
5. `test_end_to_end_workflow()` - Submit 5 tasks, verify parallelism

### Manual Testing

```bash
# Test 1: Parallel execution (different agents)
python -c "
from coffee_maker.autonomous.task_queue import TaskQueue, AgentTask
import time

queue = TaskQueue(max_parallel=4)

# Submit tasks for different agents
task1 = AgentTask('code_developer', 'Task 1', ['coffee_maker/a.py'], lambda: time.sleep(5))
task2 = AgentTask('project_manager', 'Task 2', ['docs/roadmap/ROADMAP.md'], lambda: time.sleep(5))

f1 = queue.submit_task(task1)
f2 = queue.submit_task(task2)

# Should complete in ~5 seconds (parallel), not 10 (sequential)
start = time.time()
f1.result()
f2.result()
print(f'Completed in {time.time() - start:.1f}s (should be ~5s)')
"

# Test 2: Singleton conflict (same agent)
# Should take ~10 seconds (sequential)

# Test 3: Status dashboard
python scripts/show_parallel_status.py
# Should show running agents while tasks execute
```

---

## Rollout Plan

### Phase 1: Task Queue (Day 1 - 4 hours)

**Goal**: Implement core task queue with conflict detection

**Tasks**:
1. Create `task_queue.py` (120 lines)
2. Implement `TaskQueue` class with conflict checks
3. Write unit tests (120 lines)
4. Verify singleton + ownership integration

**Success Criteria**:
- All 10 unit tests pass
- Parallel execution works (different agents)
- Sequential fallback works (same agent/files)

### Phase 2: Integration (Day 2 - 3 hours)

**Goal**: Integrate with user_listener

**Tasks**:
1. Update `user_listener.py` to use TaskQueue
2. Add `delegate_tasks_parallel()` function
3. Write integration tests (80 lines)
4. Test with real agents

**Success Criteria**:
- user_listener can submit parallel tasks
- Real agents run in parallel
- All integration tests pass

### Phase 3: Status Dashboard (Day 2 - 2 hours)

**Goal**: Add visibility into parallel execution

**Tasks**:
1. Create `show_parallel_status.py` script (30 lines)
2. Add status reporting to `TaskQueue`
3. Test real-time status updates

**Success Criteria**:
- Dashboard shows running agents
- Dashboard shows queued tasks
- Updates in real-time

---

## Why This is Simple (vs Strategic Spec)

**Strategic Spec** (US-043 in ROADMAP):
- Mentioned "Parallel Task Queue System" (sounds complex)
- "Conflict Detection" (sounds like complex graph analysis)
- "Resource Management" (CPU, memory throttling)
- "Dependency Management" (dependency graphs)
- "Priority-based Scheduling" (complex scheduler)
- ~2-3 days estimate

**This Simplified Spec**:
- **Simple conflict check** (singleton + file ownership lookup)
- **No dependency graphs** (manual task specification)
- **No resource management** (max_parallel only)
- **No priority scheduling** (FIFO queue for now)
- **120 lines implementation** (not 500+)
- **Same 2-3 days estimate** (but simpler)

**What We REUSE**:
- US-035 singleton checks (already implemented)
- US-038 ownership checks (already implemented)
- Python stdlib `concurrent.futures.ThreadPoolExecutor`
- Python stdlib `threading.Lock`

**Complexity Reduction**:
- **No complex scheduler** (just conflict detection)
- **No dependency graphs** (deferred to future)
- **No resource monitoring** (CPU/memory tracking deferred)
- **No priority queues** (FIFO for now)

**Result**: 60% less code, 2-4x speedup achieved

---

## Success Metrics

Track these metrics to validate parallelism:

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Avg task completion time | 100% | 40-50% | 2-4x faster |
| Max parallel agents | 1 | 3-4 | 3+ |
| CPU utilization | 25% | 60-80% | >50% |
| User satisfaction | Baseline | TBD | >9/10 |

**Example Speedup**:
```
Before (Sequential):
  code_developer: 30 min
  project_manager: 30 min
  architect: 30 min
  Total: 90 minutes

After (Parallel):
  All 3 running simultaneously
  Total: max(30, 30, 30) = 30 minutes
  Speedup: 3x faster! ✨
```

---

## Future Enhancements

**NOT in this spec** (deferred):
1. **Dependency Graphs** → Automatic task ordering based on dependencies
2. **Resource Management** → CPU/memory limits, intelligent throttling
3. **Priority Scheduling** → High-priority tasks jump queue
4. **Distributed Execution** → Multi-machine orchestration
5. **Dynamic Parallelism** → Adjust max_parallel based on load

---

## References

- US-043: Enable Parallel Agent Execution for Faster Delivery (ROADMAP)
- US-035: Implement Singleton Agent Enforcement (dependency)
- US-038: Implement File Ownership Enforcement (dependency)
- CFR-000: Prevent File Conflicts (master requirement)
- ADR-003: Simplification-First Approach
- Python concurrent.futures: https://docs.python.org/3/library/concurrent.futures.html

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created (Draft) | architect |

---

## Approval

- [ ] architect (author) - Ready for review
- [ ] code_developer (implementer) - Can implement in 2-3 days
- [ ] project_manager (strategic alignment) - Meets US-043 goals
- [ ] User (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 2-3 days (9 hours total)

**Phases**:
- Phase 1: Task Queue (4 hours)
- Phase 2: Integration (3 hours)
- Phase 3: Status Dashboard (2 hours)

**Depends On**: US-035 (Singleton) and US-038 (Ownership) must be complete first

**Result**: 2-4x faster delivery, safe parallel execution! 🚀
