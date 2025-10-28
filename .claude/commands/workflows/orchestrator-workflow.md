---
command: orchestrator-workflow
workflow: coordinate
agent: orchestrator
purpose: Multi-agent coordination workflow
tables: [orchestrator_task, agent_lifecycle, agent_message, execution_trace]
tools: [git, file_system]
duration: 1-30m
---

## Purpose

Execute multi-agent coordination workflow: manage agent lifecycle, assign work, route messages, and manage worktrees. This is the PRIMARY workflow command for the orchestrator agent, enabling parallel execution across multiple agents.

## Workflow Overview

```
coordinate(action) → AGENTS | WORK | MESSAGES | WORKTREES → CoordinateResult
```

**Key Features**:
- **4 coordination actions**: AGENTS (lifecycle), WORK (task assignment), MESSAGES (routing), WORKTREES (git isolation)
- **Parallel execution**: Manages multiple agents working simultaneously
- **Worktree isolation**: CFR-013 compliant git worktree management
- **Health monitoring**: Tracks agent health and auto-restart
- **Message routing**: Routes inter-agent communication

## Input Parameters

```yaml
ACTION:
  type: string
  required: true
  enum: [agents, work, messages, worktrees]
  description: |
    - agents: Manage agent lifecycle (spawn, monitor, kill)
    - work: Assign tasks to agents
    - messages: Route inter-agent messages
    - worktrees: Manage git worktrees for parallel work

**params:
  type: dict
  description: Action-specific parameters
```

## Workflow Execution

### AGENTS Action

Manage agent lifecycle:

```python
1. Query agent_lifecycle table
2. Check agent health status
3. Spawn new agents if needed
4. Kill stalled agents
5. Monitor resource usage
6. Return agent status
```

### WORK Action

Assign tasks to available agents:

```python
1. Query specs_task for parallelizable work
2. Check task dependencies
3. Find available agents
4. Assign tasks to agents
5. Create orchestrator_task records
6. Return assignment summary
```

### MESSAGES Action

Route inter-agent communication:

```python
1. Query agent_message table
2. Route messages to target agents
3. Handle responses
4. Log message history
5. Return routing summary
```

### WORKTREES Action

Manage git worktrees (CFR-013):

```python
1. Create worktree for task
2. Create branch: roadmap-implementation_task-{task_id}
3. Track worktree in database
4. Clean up completed worktrees
5. Merge completed branches
6. Return worktree status
```

## Result Object

```python
@dataclass
class CoordinateResult:
    action: str  # agents | work | messages | worktrees
    status: str  # success | partial | failed
    agents_managed: int
    tasks_assigned: int
    duration_seconds: float
    metadata: Dict[str, Any]
```

## Database Operations

### Query: Agent Status

```sql
SELECT
    agent_id, agent_type, status, pid,
    started_at, last_heartbeat, resource_usage
FROM agent_lifecycle
WHERE status = 'running'
```

### Insert: Orchestrator Task

```sql
INSERT INTO orchestrator_task (
    task_id, assigned_agent, worktree_path,
    branch_name, status, created_at
) VALUES (?, ?, ?, ?, 'assigned', datetime('now'))
```

### Update: Agent Heartbeat

```sql
UPDATE agent_lifecycle
SET
    last_heartbeat = datetime('now'),
    resource_usage = ?
WHERE agent_id = ?
```

### Query: Available Work

```sql
SELECT st.task_id, st.spec_id, st.status
FROM specs_task st
WHERE st.status = 'pending'
  AND NOT EXISTS (
    SELECT 1 FROM task_dependency td
    WHERE td.from_task_id = st.task_id
    AND td.to_task_id IN (
      SELECT task_id FROM specs_task WHERE status != 'completed'
    )
  )
```

## Examples

### Example 1: Spawn Agents

```python
result = workflow.coordinate(
    action="agents",
    operation="spawn",
    agent_types=["code_developer", "code_reviewer"]
)
```

**Result**:
```python
CoordinateResult(
    action="agents",
    status="success",
    agents_managed=2,
    tasks_assigned=0,
    duration_seconds=5.0,
    metadata={
        "spawned": ["code_developer-1", "code_reviewer-1"],
        "pids": [12345, 12346]
    }
)
```

### Example 2: Assign Work

```python
result = workflow.coordinate(
    action="work",
    max_parallel=3
)
```

**Result**:
```python
CoordinateResult(
    action="work",
    status="success",
    agents_managed=1,
    tasks_assigned=3,
    duration_seconds=2.0,
    metadata={
        "assignments": [
            {"task_id": "TASK-31-1", "agent": "code_developer-1", "worktree": "wt-31-1"},
            {"task_id": "TASK-32-1", "agent": "code_developer-2", "worktree": "wt-32-1"},
            {"task_id": "TASK-33-1", "agent": "code_developer-3", "worktree": "wt-33-1"}
        ]
    }
)
```

### Example 3: Route Messages

```python
result = workflow.coordinate(
    action="messages",
    pending_only=True
)
```

**Result**:
```python
CoordinateResult(
    action="messages",
    status="success",
    agents_managed=4,
    tasks_assigned=0,
    duration_seconds=1.5,
    metadata={
        "messages_routed": 7,
        "routes": {
            "architect → code_developer": 3,
            "code_reviewer → architect": 2,
            "project_manager → all": 2
        }
    }
)
```

### Example 4: Manage Worktrees

```python
result = workflow.coordinate(
    action="worktrees",
    operation="cleanup"
)
```

**Result**:
```python
CoordinateResult(
    action="worktrees",
    status="success",
    agents_managed=0,
    tasks_assigned=0,
    duration_seconds=8.0,
    metadata={
        "cleaned": 5,
        "worktrees_removed": [
            ".worktrees/roadmap-implementation_task-31-1",
            ".worktrees/roadmap-implementation_task-31-2",
            ".worktrees/roadmap-implementation_task-32-1"
        ],
        "branches_deleted": [
            "roadmap-implementation_task-31-1",
            "roadmap-implementation_task-31-2"
        ]
    }
)
```

## Worktree Management (CFR-013)

### Create Worktree

```bash
# Create worktree for task
git worktree add .worktrees/roadmap-implementation_task-{task_id} \
  -b roadmap-implementation_task-{task_id} roadmap

# Example:
git worktree add .worktrees/roadmap-implementation_task-31-1 \
  -b roadmap-implementation_task-31-1 roadmap
```

### Cleanup Worktree

```bash
# Remove worktree
git worktree remove .worktrees/roadmap-implementation_task-{task_id}

# Delete branch
git branch -D roadmap-implementation_task-{task_id}
```

### Merge Workflow

```bash
# Switch to roadmap
git checkout roadmap

# Merge completed work
git merge roadmap-implementation_task-{task_id} --no-ff

# Cleanup
git branch -d roadmap-implementation_task-{task_id}
```

## Agent Health Monitoring

### Health Check

```python
def check_agent_health(agent_id):
    agent = query_agent(agent_id)

    # Check heartbeat (should be < 60 seconds ago)
    last_heartbeat = agent.last_heartbeat
    if (now() - last_heartbeat).seconds > 60:
        return "stalled"

    # Check resource usage
    if agent.resource_usage.cpu > 90:
        return "overloaded"

    if agent.resource_usage.memory > 80:
        return "memory_pressure"

    return "healthy"
```

### Auto-Restart

```python
def auto_restart_agent(agent_id):
    # Kill stalled agent
    kill_agent(agent_id)

    # Wait for cleanup
    time.sleep(5)

    # Spawn replacement
    spawn_agent(agent.agent_type)

    # Reassign tasks
    reassign_tasks(old_agent_id, new_agent_id)
```

## Performance Expectations

| Action | Duration | Agents Affected | Tasks Typical |
|--------|----------|-----------------|---------------|
| agents | 1-10s | 1-5 agents | N/A |
| work | 2-5s | 1-3 agents | 1-5 tasks |
| messages | 1-3s | All agents | 5-20 messages |
| worktrees | 5-15s | N/A | 3-8 worktrees |

## Best Practices

1. **Use agents action** for monitoring and health checks
2. **Use work action** to enable parallel execution
3. **Use messages action** for inter-agent communication
4. **Use worktrees action** to manage git isolation (CFR-013)
5. **Monitor agent health** regularly (every 60 seconds)
6. **Clean up worktrees** after task completion
7. **Limit parallel work** to system capacity (3-5 tasks)

## Related Commands

- `developer.work()` - Execute work assigned by orchestrator
- `project_manager.manage()` - Track orchestrated work
- `architect.spec()` - Create specs for orchestrated tasks

---

**Workflow Reduction**: This single `coordinate()` command replaces:
1. `spawn_agent()`
2. `assign_work()`
3. `route_messages()`
4. `manage_worktrees()`

**Context Savings**: ~200 lines vs ~1,200 lines (4 commands)
