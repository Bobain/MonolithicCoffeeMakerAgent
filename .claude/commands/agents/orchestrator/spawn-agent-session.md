---
command: orchestrator.spawn-agent-session
agent: orchestrator
action: spawn_agent_session
description: Launch agent using claude command for assigned task
tables:
  read: [orchestrator_task, roadmap_priority]
  write: [agent_lifecycle]
required_tools: [claude, subprocess, database]
cfr_compliance:
  - CFR-000: Singleton agent enforcement (AgentRegistry)
  - CFR-014: Database tracing (all orchestrator activities in SQLite)
---

# Command: orchestrator.spawn-agent-session

## Purpose

Spawn a new agent session using Claude Code to execute an assigned task. This command:
1. Validates task readiness
2. Checks agent singleton status (CFR-000)
3. Launches agent via `claude` CLI command
4. Records agent lifecycle in agent_lifecycle table
5. Tracks session status and health

## Parameters

```python
parameters = {
    "AGENT_TYPE": "code_developer",      # "code_developer", "architect", etc.
    "TASK_ID": "TASK-31-1",
    "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
    "TIMEOUT_SECONDS": 3600,
    "AUTO_RESTART": True
}
```

## Agent Invocation Pattern

### Option 1: Claude Code Command (Preferred)

```bash
claude run orchestrator/spawn-agent-session \
    --agent-type code_developer \
    --task-id TASK-31-1 \
    --orchestrator-id orch-20251026-001
```

### Option 2: Direct Python Invocation

```python
from coffee_maker.claude_agent_invoker import ClaudeAgentInvoker

invoker = ClaudeAgentInvoker(agent_name="orchestrator")

result = invoker.invoke_command(
    command_name="spawn-agent-session",
    parameters={
        "AGENT_TYPE": "code_developer",
        "TASK_ID": "TASK-31-1",
        "ORCHESTRATOR_INSTANCE_ID": "orch-20251026-001",
        "TIMEOUT_SECONDS": 3600
    }
)
```

## Database Operations

### Create agent_lifecycle Record

```sql
INSERT INTO agent_lifecycle (
    agent_id,
    agent_type,
    status,
    task_id,
    pid,
    created_at,
    started_at,
    completed_at,
    error_message,
    last_heartbeat
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

### Update orchestrator_task

```sql
UPDATE orchestrator_task
SET status = 'running',
    assigned_agent = ?,
    started_at = CURRENT_TIMESTAMP
WHERE task_id = ?;
```

## Pre-spawn Validation

1. **Singleton Check (CFR-000)**
   - Verify no other agent of same type is running
   - Check AgentRegistry for active instances
   - Fail if singleton constraint violated

2. **Task Validation**
   - Verify task exists in orchestrator_task
   - Verify task status is 'spawned'
   - Verify all dependencies completed

3. **Resource Check**
   - Verify CPU available (>20% free)
   - Verify memory available (>500MB free)
   - Verify no resource exhaustion

## Spawn Process

1. Create temporary agent session directory
2. Set environment variables (TASK_ID, ORCHESTRATOR_ID, etc.)
3. Launch agent process via CLI
4. Wait for agent to confirm startup
5. Record PID and startup time
6. Begin health monitoring

## Output Format

```json
{
    "success": true,
    "agent_id": "code-developer-20251026-001",
    "agent_type": "code_developer",
    "task_id": "TASK-31-1",
    "status": "running",
    "pid": 12345,
    "created_at": "2025-10-26T10:30:00Z",
    "started_at": "2025-10-26T10:30:05Z",
    "expected_completion": "2025-10-26T18:30:05Z",
    "timeout_seconds": 3600
}
```

## Timeout and Auto-restart

- **Timeout**: If agent doesn't heartbeat for 60 seconds, mark as stalled
- **Auto-restart**: If enabled, restart stalled agent with backoff
- **Max retries**: 3 attempts before failure
- **Backoff**: 2^n seconds (2s, 4s, 8s)

## Success Criteria

1. Agent process spawned successfully
2. agent_lifecycle record created
3. orchestrator_task updated to 'running'
4. PID recorded for process tracking
5. Agent confirms startup within 10 seconds
6. Singleton constraint enforced

## Error Handling

```json
{
    "success": false,
    "error": "singleton_violation",
    "message": "code_developer already running (PID: 11999)",
    "agent_type": "code_developer",
    "existing_agent_id": "code-developer-20251026-000"
}
```

## Possible Errors

- `singleton_violation`: Another agent of same type running
- `task_not_found`: Task doesn't exist in orchestrator_task
- `resource_exhaustion`: Insufficient CPU or memory
- `spawn_failed`: Agent process failed to start
- `startup_timeout`: Agent didn't confirm startup

## Related Commands

- monitor-agent-lifecycle.md (tracks agent health)
- kill-stalled-agent.md (terminates unresponsive agents)
- auto-restart-agent.md (restarts failed agents)
