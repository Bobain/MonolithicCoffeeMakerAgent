# Orchestrator Agent

**Role**: Multi-agent coordination, parallel execution, health monitoring
**Interaction**: Backend only (no UI)
**Owner**: orchestrator
**CFR Compliance**: CFR-000, CFR-013, CFR-014, CFR-018

---

## Purpose

The orchestrator agent coordinates multiple agents for parallel task execution. It:

- Monitors agent lifecycle (health, CPU/memory, heartbeats)
- Assigns tasks to available agents based on dependency graph
- Routes inter-agent messages via agent_message table
- Manages git worktrees for parallel task isolation (CFR-013)
- Enforces singleton agent policy (CFR-000)
- Detects deadlocks and stalled agents
- Generates activity summaries

**Key Principle**: Coordination without execution. Orchestrator manages agents but doesn't implement tasks.

**Lifecycle**: Agent executes ONE command, then terminates (CFR-018).

---

## Commands (4)

### agents
Monitor agent lifecycle: track health, detect stalls, auto-restart failed agents, enforce singleton policy (CFR-000), generate activity reports.
- **Input**: action (list/health/restart/kill), agent_id, agent_type filter
- **Output**: Active agents, health status, agents restarted/killed
- **Duration**: 2-10 seconds
- **Budget**: 180 (README) + 95 (command) + 160 (auto-skills) = 435 lines (27%) ✅

### assign
Assign tasks to agents for parallel execution: analyze dependencies, find available work, create orchestrator_task entries, notify agents.
- **Input**: priority_id, task_ids, max_parallel count
- **Output**: Tasks assigned, assignments list, blocked tasks count
- **Duration**: 5-15 seconds
- **Budget**: 180 (README) + 86 (command) + 160 (auto-skills) = 426 lines (27%) ✅

### route
Route messages between agents: read agent_message table, deliver to target agents, track delivery status, handle routing failures.
- **Input**: action (poll/send/acknowledge), message_id, target_agent
- **Output**: Messages processed, delivery status
- **Duration**: 1-3 seconds per action
- **Budget**: 180 (README) + 100 (command) + 160 (auto-skills) = 440 lines (28%) ✅

### worktrees
Manage git worktrees for parallel task execution (CFR-013): create isolated branches, track worktree usage, cleanup completed worktrees.
- **Input**: action (create/list/cleanup/merge), task_id, worktree_path
- **Output**: Worktree path, branch name, active worktrees, cleaned up count
- **Duration**: 5-20 seconds
- **Budget**: 180 (README) + 105 (command) + 160 (auto-skills) = 445 lines (28%) ✅

---

## Key Workflows

### Parallel Execution Workflow
```
1. assign(priority_id) → Find tasks with no blocking dependencies
2. For each available task:
   a. worktrees(action="create", task_id) → Create isolated branch
   b. Spawn code_developer agent in worktree
   c. Track in orchestrator_task table
3. Monitor agent health with agents(action="health")
4. When task completes: worktrees(action="merge") → Merge to roadmap
5. worktrees(action="cleanup") → Remove worktree and branch
```

### Agent Health Monitoring
```
1. agents(action="health") → Check all running agents
   - Heartbeat < 2 min: healthy
   - Heartbeat 2-5 min: warning
   - Heartbeat > 5 min: stalled
2. CPU/Memory checks:
   - CPU < 80%: healthy
   - CPU 80-95%: warning
   - CPU > 95%: critical
3. Enforce CFR-000: Only 1 instance per agent type
4. Auto-restart failed agents (exponential backoff)
```

### Message Routing Workflow
```
1. Agent A sends message: route(action="send", target="agent_B", content={...})
2. Insert into agent_message table (status="pending")
3. Agent B polls: route(action="poll", target="agent_B")
4. Deliver messages, update status="delivered"
5. Handle failures: Retry with backoff (max 3 attempts)
```

### CFR-013 Worktree Management
```
1. Create: git worktree add ../worktrees/task-{id} -b roadmap-implementation_task-{id}
2. Agent works in isolated worktree
3. Merge (architect only): git merge --no-ff roadmap-implementation_task-{id}
4. Cleanup: git worktree remove + git branch -d
```

---

## Database Tables

### Primary Tables
- **orchestrator_task**: Task assignments (task_id, agent_type, status, worktree_path)
- **agent_lifecycle**: Agent health (agent_id, type, status, pid, heartbeat, CPU, memory)
- **agent_message**: Inter-agent messaging (from, to, type, content, status)
- **git_worktree_tracker**: Worktree management (task_id, branch, path, status)

### Dependency Tables
- **specs_task_dependency**: Task dependencies (blocking_task_id, dependent_task_id)
- **agent_restart_log**: Restart tracking (agent_id, reason, attempt_number)

### Query Patterns
```sql
-- Find available tasks (no blocking dependencies)
SELECT st.task_id
FROM specs_task st
LEFT JOIN specs_task_dependency std ON st.task_id = std.dependent_task_id
LEFT JOIN specs_task dep ON std.blocking_task_id = dep.task_id
WHERE st.status = 'pending'
  AND (dep.status = 'completed' OR dep.task_id IS NULL)
GROUP BY st.task_id
HAVING COUNT(CASE WHEN dep.status != 'completed' THEN 1 END) = 0

-- Check agent health
SELECT agent_id, agent_type,
       ROUND((julianday('now') - julianday(last_heartbeat)) * 1440) as minutes_since_heartbeat
FROM agent_lifecycle
WHERE status = 'running'
```

---

## CFR Compliance

### CFR-000: Singleton Agent Enforcement
Uses AgentRegistry to ensure only 1 instance per agent type runs at any time.

### CFR-013: Git Worktree Workflow
- Branch naming: `roadmap-implementation_task-{task_id}`
- One worktree per task for isolation
- Sequential merge: architect merges after each task completion
- Parallel across groups: Different task groups work simultaneously

### CFR-014: Database Tracing
ALL orchestrator activities in SQLite database. No JSON files.

### CFR-018: Command Execution Context
All commands: `README (180) + command (86-105) + auto-skills (160) = 426-445 lines (27-28%)` ✅

---

## Error Handling

### Common Errors
- **AgentNotFound**: Invalid agent_id → Check active agents
- **SingletonViolation**: Multiple instances → Kill duplicates (CFR-000)
- **NoAvailableWork**: All tasks blocked → Wait for dependencies
- **WorktreeExists**: Duplicate worktree → Cleanup or use existing
- **DependencyCycle**: Circular dependencies → Fix dependency graph

---

## Related Documents

- **CFR-000**: Agent singleton architecture
- **CFR-013**: Git worktree workflow
- **CFR-014**: Database tracing requirements
- **Agent Registry**: `coffee_maker/autonomous/agent_registry.py`

---

**Version**: 1.0.0
**Last Updated**: 2025-10-28
**Lines**: 180
**Budget**: 11% (180/1,600 lines)
