# Parallel Execution Quick Reference

**Quick access guide for parallel agent execution capabilities**

---

## Overview

MonolithicCoffeeMakerAgent has **two parallel execution systems**:

| System | Purpose | Max Speedup | Use When |
|--------|---------|-------------|----------|
| **US-043: Task Queue** | Different agents in parallel | 2-4x | architect + code_developer + project_manager simultaneously |
| **US-108: Git Worktree** | Same agent in parallel | 2-3x | Multiple code_developer instances on independent tasks |

---

## US-043: Simple Task Queue

### Quick Start

```python
from coffee_maker.autonomous.task_queue import TaskQueue, AgentTask

queue = TaskQueue(max_parallel=4)

# Submit tasks for different agents
task1 = AgentTask("code_developer", "Task 1", ["coffee_maker/a.py"], lambda: work())
task2 = AgentTask("architect", "Task 2", ["docs/architecture/spec.md"], lambda: work())

f1 = queue.submit_task(task1)
f2 = queue.submit_task(task2)

# Both run in parallel!
results = [f1.result(), f2.result()]
```

### Safe Combinations

| ✅ SAFE (Parallel) | ❌ UNSAFE (Sequential) |
|-------------------|----------------------|
| code_developer + architect | code_developer + code_developer |
| code_developer + project_manager | architect + architect |
| architect + project_manager | project_manager + project_manager |
| assistant + any agent (read-only) | Any 2 agents touching same file |

### Check Status

```python
status = queue.get_status()
print(f"Running: {status['running_agents']}")
print(f"Queued: {status['queued_tasks']}")
```

### Documentation

→ Full Guide: [docs/US-043_PARALLEL_TASK_QUEUE_GUIDE.md](US-043_PARALLEL_TASK_QUEUE_GUIDE.md)

---

## US-108: Git Worktree Parallel Execution

### Quick Start

```python
from coffee_maker.orchestrator.parallel_execution_coordinator import (
    ParallelExecutionCoordinator
)

# Run 2 code_developer instances in parallel
coordinator = ParallelExecutionCoordinator(max_instances=2, auto_merge=True)

result = coordinator.execute_parallel_batch(
    priority_ids=[20, 21, 22],  # PRIORITY numbers
    auto_approve=True
)

print(f"Completed: {result['monitoring_result']['completed']}")
print(f"Duration: {result['duration_seconds']}s")
```

### Prerequisites

1. **Technical Specs Required**: Each PRIORITY must have `SPEC-{id}-*.md`
2. **File Lists in Specs**: Specs must include `**File**: path/to/file.py` markers
3. **Independent Tasks**: Priorities must have zero file overlap

### Workflow

```
1. architect validates task separation (task-separator skill)
   ↓
2. coordinator creates git worktrees
   ↓
3. code_developer instances spawn in each worktree
   ↓
4. Monitor progress (10s polling)
   ↓
5. Auto-merge to roadmap branch
   ↓
6. Cleanup worktrees
```

### Documentation

→ Full Guide: [docs/PARALLEL_EXECUTION_GUIDE.md](PARALLEL_EXECUTION_GUIDE.md)

---

## Comparison Matrix

| Feature | US-043 Task Queue | US-108 Git Worktree |
|---------|------------------|---------------------|
| **Max Speedup** | 2-4x (4-6 different agents) | 2-3x (2-3 same agent) |
| **Setup Required** | None (instant) | Technical specs required |
| **Agent Types** | Different agents only | Same agent allowed |
| **Isolation** | Thread-based | Full git worktree (separate directory) |
| **Complexity** | Simple (~200 lines) | Complex (~600 lines) |
| **Resource Usage** | Low | Higher (multiple directories) |
| **Merge Required** | No | Yes (auto or manual) |

---

## Decision Tree: Which System to Use?

```
Do you need SAME agent type to run multiple instances?
   YES → Use US-108 Git Worktree
   NO → Use US-043 Task Queue
          ↓
Are all agents working on different files?
   YES → Safe to run in parallel (3-4x speedup!)
   NO → Sequential execution (file conflict)
```

---

## Common Use Cases

### Case 1: Different Agents, Different Files

**Scenario**: architect creating spec + code_developer implementing + project_manager updating ROADMAP

**System**: US-043 Task Queue

**Speedup**: 3x (all run simultaneously)

```python
queue = TaskQueue(max_parallel=4)

tasks = [
    AgentTask("architect", "Create SPEC-046", ["docs/architecture/specs/SPEC-046.md"], create_spec),
    AgentTask("code_developer", "Implement US-038", ["coffee_maker/daemon.py"], implement),
    AgentTask("project_manager", "Update ROADMAP", ["docs/roadmap/ROADMAP.md"], update_roadmap),
]

futures = [queue.submit_task(t) for t in tasks]
results = [f.result() for f in futures]  # All run in parallel!
```

### Case 2: Multiple code_developer Instances

**Scenario**: 3 independent priorities to implement

**System**: US-108 Git Worktree

**Speedup**: 2x (2-3 instances in parallel)

```python
coordinator = ParallelExecutionCoordinator(max_instances=2, auto_merge=True)

# PRIORITY 20, 21, 22 all have technical specs and zero file overlap
result = coordinator.execute_parallel_batch(
    priority_ids=[20, 21, 22],
    auto_approve=True
)
```

### Case 3: Combined (Maximum Speedup)

**Scenario**: 2x code_developer + architect + project_manager

**System**: US-108 + US-043 combined

**Speedup**: 4x (all run simultaneously)

```python
# Start 2 code_developer instances with US-108
coordinator = ParallelExecutionCoordinator(max_instances=2)
dev_result = coordinator.execute_parallel_batch(priority_ids=[20, 21], auto_approve=True)

# Meanwhile, run architect + project_manager with US-043
queue = TaskQueue(max_parallel=4)
arch_task = AgentTask("architect", "Create spec", ["docs/architecture/specs/SPEC-046.md"], create_spec)
pm_task = AgentTask("project_manager", "Update ROADMAP", ["docs/roadmap/ROADMAP.md"], update_roadmap)

queue.submit_task(arch_task)
queue.submit_task(pm_task)

# All 4 agents working simultaneously!
```

---

## Conflict Detection Rules

### Singleton Enforcement (US-035)

**Rule**: Only ONE instance of each agent type can run at a time (unless using US-108 worktrees)

**Implementation**: `AgentRegistry` checks running agents

**Example**:
```python
# ❌ BLOCKED: Same agent type
task1 = AgentTask("code_developer", "Task 1", ["file1.py"], work1)
task2 = AgentTask("code_developer", "Task 2", ["file2.py"], work2)  # WAITS for task1

# ✅ ALLOWED: Different agent types
task1 = AgentTask("code_developer", "Task 1", ["file1.py"], work1)
task2 = AgentTask("architect", "Task 2", ["file2.py"], work2)  # Runs in parallel
```

### File Ownership (US-038)

**Rule**: Only the file owner can modify files

**Implementation**: `FileOwnership` registry maps files to agents

**Example**:
```python
# ❌ BLOCKED: Same file
task1 = AgentTask("code_developer", "Task 1", ["coffee_maker/a.py"], work1)
task2 = AgentTask("architect", "Task 2", ["coffee_maker/a.py"], work2)  # WAITS (file conflict)

# ✅ ALLOWED: Different files
task1 = AgentTask("code_developer", "Task 1", ["coffee_maker/a.py"], work1)
task2 = AgentTask("architect", "Task 2", ["docs/architecture/spec.md"], work2)  # Parallel
```

### Resource Limits

**Rule**: Maximum 4-6 agents in parallel (configurable)

**Implementation**: `max_parallel` parameter in TaskQueue

**Example**:
```python
queue = TaskQueue(max_parallel=4)

# 1st-4th tasks: Run immediately
# 5th+ tasks: Wait in queue until slot opens
```

---

## Performance Expectations

### US-043 Task Queue

| Agents | Sequential Time | Parallel Time | Speedup |
|--------|----------------|---------------|---------|
| 2 (different) | 60 min | 30 min | **2x** |
| 3 (different) | 90 min | 30 min | **3x** |
| 4 (different) | 120 min | 30 min | **4x** |

### US-108 Git Worktree

| Instances | Sequential Time | Parallel Time | Speedup |
|-----------|----------------|---------------|---------|
| 2 (code_developer) | 60 min | 30 min | **2x** |
| 3 (code_developer) | 90 min | 30 min | **3x** |

### Combined

| Total Agents | Sequential Time | Parallel Time | Speedup |
|--------------|----------------|---------------|---------|
| 2x code_developer + architect + PM | 120 min | 30 min | **4x** |

---

## CLI Commands

### US-043 Task Queue

```bash
# Check queue status
python scripts/show_parallel_status.py

# Delegate multiple tasks (future)
poetry run project-manager delegate-multiple \
    "code_developer: implement US-038" \
    "architect: create SPEC-046" \
    "project_manager: update ROADMAP"
```

### US-108 Git Worktree

```bash
# Execute priorities in parallel (via Python)
python -c "
from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator
coordinator = ParallelExecutionCoordinator(max_instances=2, auto_merge=True)
result = coordinator.execute_parallel_batch(priority_ids=[20, 21], auto_approve=True)
print(f'Completed: {result[\"monitoring_result\"][\"completed\"]}')
"

# Check status
python -c "
from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator
coordinator = ParallelExecutionCoordinator()
status = coordinator.get_status()
print(f'Active worktrees: {status[\"active_worktrees\"]}')
"
```

---

## Troubleshooting

### Tasks Run Sequentially (Not Parallel)

**Symptoms**: Total time = sum of task times

**Causes**:
1. Same agent type (singleton conflict)
2. Overlapping files (ownership conflict)
3. Resource limit hit (max_parallel exceeded)

**Debug**:
```python
status = queue.get_status()
print(f"Running: {status['running_agents']}")
print(f"Active files: {status['running_files']}")
print(f"Queued: {status['queued_tasks']}")

# Check for conflicts
task1_files = set(task1.files_to_modify)
task2_files = set(task2.files_to_modify)
if task1_files & task2_files:
    print(f"File conflict: {task1_files & task2_files}")
```

### "No independent priority pairs found"

**Symptom**: Git worktree coordinator fails to find parallelizable tasks

**Cause**: All priorities modify overlapping files

**Solution**: Review technical specs, ensure tasks touch different files

```bash
# Use task-separator skill to check
python -c "
import sys
sys.path.insert(0, '.claude/skills/architect/task-separator')
import task_separator
result = task_separator.main({'priority_ids': [20, 21, 22]})
print(f'Independent pairs: {result[\"independent_pairs\"]}')
print(f'Conflicts: {result[\"conflicts\"]}')
"
```

### Worktree Creation Fails

**Symptom**: `git worktree add` errors

**Cause**: Worktree directory already exists

**Solution**:
```bash
# Remove stale worktrees
git worktree remove --force ../MonolithicCoffeeMakerAgent-wt20
git worktree remove --force ../MonolithicCoffeeMakerAgent-wt21

# Prune stale references
git worktree prune
```

---

## Best Practices

### 1. Start Small, Scale Up

```python
# Start with 2 agents
queue = TaskQueue(max_parallel=2)
# Verify stability, then scale to 4
queue = TaskQueue(max_parallel=4)
```

### 2. Specify Files Accurately

```python
# ✅ GOOD: Complete file list
files = [
    "coffee_maker/module_a.py",
    "coffee_maker/module_b.py",
    "tests/unit/test_module_a.py"
]

# ❌ BAD: Incomplete (may miss conflicts)
files = ["coffee_maker/module_a.py"]
```

### 3. Monitor Resources

```python
import psutil

cpu = psutil.cpu_percent(interval=1.0)
mem = psutil.virtual_memory().percent

if cpu < 70 and mem < 70:
    queue.submit_task(task)  # System has capacity
else:
    print("System under load, waiting...")
```

### 4. Handle Failures Gracefully

```python
try:
    result = future.result(timeout=300)  # 5 min timeout
except TimeoutError:
    print("Task timed out")
except Exception as e:
    print(f"Task failed: {e}")
```

---

## Key Files

### US-043 Implementation

- `coffee_maker/autonomous/task_queue.py` - Task queue class (to be implemented)
- `coffee_maker/autonomous/agent_registry.py` - Singleton enforcement (US-035)
- `coffee_maker/autonomous/ace/file_ownership.py` - Ownership enforcement (US-038)

### US-108 Implementation

- `coffee_maker/orchestrator/parallel_execution_coordinator.py` - Worktree coordinator
- `.claude/skills/architect/task-separator/task_separator.py` - Task separation validator

### Documentation

- `docs/US-043_PARALLEL_TASK_QUEUE_GUIDE.md` - US-043 full guide
- `docs/PARALLEL_EXECUTION_GUIDE.md` - US-108 full guide
- `docs/architecture/specs/SPEC-043-parallel-agent-execution.md` - US-043 technical spec
- `docs/architecture/specs/SPEC-108-parallel-agent-execution-with-git-worktree.md` - US-108 technical spec

---

## Related CFRs

- **CFR-000**: Prevent File Conflicts (master requirement)
- **CFR-013**: Git Workflow (roadmap branch only)
- **US-035**: Singleton Agent Enforcement
- **US-038**: File Ownership Enforcement

---

**Last Updated**: 2025-10-21
**Version**: 1.0.0

For detailed information, see:
- [US-043 Full Guide](US-043_PARALLEL_TASK_QUEUE_GUIDE.md)
- [US-108 Full Guide](PARALLEL_EXECUTION_GUIDE.md)
