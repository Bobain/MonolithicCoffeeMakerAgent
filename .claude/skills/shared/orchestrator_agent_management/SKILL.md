# orchestrator-agent-management Skill

**Agent**: orchestrator
**Purpose**: Spawn, monitor, and manage architect and code_developer instances for autonomous work

## Overview

This skill enables the orchestrator to:
- **Spawn agents**: Start architect/code_developer with specific tasks
- **Monitor progress**: Track PIDs, check completion status, read output
- **Manage resources**: Track active tasks, worktrees, agent instances
- **Health monitoring**: Detect hung processes, restart failed agents
- **Cleanup**: Kill processes, remove worktrees, free resources

## Capabilities

### 1. Agent Spawning
- **spawn_architect**: Create architect instance for spec generation
- **spawn_code_developer**: Create code_developer instance for implementation
- **spawn_in_worktree**: Create agent in separate git worktree (for parallel work)

### 2. Progress Monitoring
- **check_status**: Get agent status (running/completed/failed/timeout)
- **get_output**: Read stdout/stderr from agent process
- **get_exit_code**: Get agent exit code after completion
- **estimate_completion**: Estimate time remaining based on task type

### 3. Resource Management
- **list_active_agents**: Get all running agents with PIDs
- **get_agent_info**: Get detailed info about specific agent (PID, task, start time)
- **track_resources**: Monitor CPU/memory usage of agents
- **enforce_limits**: Kill agents exceeding resource limits

### 4. Health & Cleanup
- **detect_hung_agents**: Find agents stuck/not progressing
- **restart_failed_agent**: Retry agent after failure
- **kill_agent**: Force terminate agent
- **cleanup_all**: Clean up all resources for completed/failed agents

## Usage Examples

### orchestrator: Spawn architect for spec creation
```python
from coffee_maker.autonomous.skill_loader import load_skill

skill = load_skill("orchestrator-agent-management")

# Spawn architect to create spec for PRIORITY 10
result = skill.execute(
    action="spawn_architect",
    priority_number=10,
    task_type="create_spec",
    auto_approve=True
)

# Returns:
# {
#   "pid": 12345,
#   "task_id": "spec-10",
#   "agent_type": "architect",
#   "status": "spawned"
# }
```

### orchestrator: Monitor agent progress
```python
# Check if architect completed spec
result = skill.execute(
    action="check_status",
    pid=12345
)

# Returns:
# {
#   "pid": 12345,
#   "status": "completed",  # or "running", "failed", "timeout"
#   "exit_code": 0,
#   "duration": 120.5,  # seconds
#   "task_completed": true
# }
```

### orchestrator: Get agent output
```python
# Read what architect did
result = skill.execute(
    action="get_output",
    pid=12345,
    last_n_lines=50  # Get last 50 lines
)

# Returns:
# {
#   "stdout": "✅ Created SPEC-010-feature-name.md\n...",
#   "stderr": "",
#   "lines": 50
# }
```

### orchestrator: Spawn parallel code_developers
```python
# Spawn 2 code_developers in worktrees
result = skill.execute(
    action="spawn_parallel_developers",
    priorities=[10, 12],
    worktree_base="/tmp/worktrees"
)

# Returns:
# {
#   "spawned": [
#     {"priority": 10, "pid": 12346, "worktree": "/tmp/worktrees/wt10"},
#     {"priority": 12, "pid": 12347, "worktree": "/tmp/worktrees/wt12"}
#   ]
# }
```

### orchestrator: Cleanup after completion
```python
# Clean up architect resources
result = skill.execute(
    action="cleanup_agent",
    pid=12345,
    remove_worktree=False  # Architect doesn't use worktrees
)

# Clean up code_developer with worktree
result = skill.execute(
    action="cleanup_agent",
    pid=12346,
    remove_worktree=True,
    worktree_path="/tmp/worktrees/wt10"
)
```

## Output Format

### spawn_architect / spawn_code_developer
```json
{
  "pid": 12345,
  "task_id": "spec-10",
  "agent_type": "architect",
  "command": "poetry run architect create-spec --priority=10 --auto-approve",
  "status": "spawned",
  "started_at": "2025-10-19T19:40:00Z"
}
```

### check_status
```json
{
  "pid": 12345,
  "status": "completed",
  "exit_code": 0,
  "duration": 120.5,
  "task_completed": true,
  "task_id": "spec-10"
}
```

### list_active_agents
```json
{
  "active_agents": [
    {
      "pid": 12345,
      "agent_type": "architect",
      "task_id": "spec-10",
      "status": "running",
      "started_at": "2025-10-19T19:40:00Z",
      "duration": 45.2
    },
    {
      "pid": 12346,
      "agent_type": "code_developer",
      "task_id": "impl-12",
      "status": "running",
      "started_at": "2025-10-19T19:40:10Z",
      "duration": 35.2
    }
  ],
  "total": 2
}
```

### detect_hung_agents
```json
{
  "hung_agents": [
    {
      "pid": 12347,
      "agent_type": "code_developer",
      "task_id": "impl-15",
      "duration": 3600.0,
      "timeout_threshold": 1800.0,
      "recommended_action": "kill"
    }
  ],
  "total": 1
}
```

## Integration with Orchestrator

```python
# In continuous_work_loop.py

from coffee_maker.autonomous.skill_loader import load_skill

class ContinuousWorkLoop:
    def __init__(self):
        self.agent_mgmt = load_skill("orchestrator-agent-management")

    def _coordinate_architect(self):
        """Spawn architect for spec creation."""
        missing_specs = self._get_missing_specs()

        for priority in missing_specs[:3]:
            # Spawn architect
            result = self.agent_mgmt.execute(
                action="spawn_architect",
                priority_number=priority["number"],
                task_type="create_spec",
                auto_approve=True
            )

            # Track task
            self._track_task(result["task_id"], result["pid"])

    def _monitor_agents(self):
        """Check status of all active agents."""
        active = self.agent_mgmt.execute(action="list_active_agents")

        for agent in active["active_agents"]:
            status = self.agent_mgmt.execute(
                action="check_status",
                pid=agent["pid"]
            )

            if status["status"] == "completed":
                self._handle_completion(agent, status)
            elif status["status"] == "failed":
                self._handle_failure(agent, status)
```

## Performance Targets

- Spawn agent: <500ms
- Check status: <50ms
- Get output: <100ms
- List active agents: <100ms
- Cleanup: <200ms

## Error Handling

- Returns `{"error": "message"}` on failure
- Graceful handling of missing PIDs
- Validates agent types (architect, code_developer)
- Logs all operations for debugging

## Dependencies

- `subprocess` - Process management
- `psutil` - Process monitoring (CPU/memory)
- `pathlib` - Path handling
- `time` - Duration tracking
