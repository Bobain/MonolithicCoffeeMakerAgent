# Orchestrator Commands Index

**SPEC-106: Orchestrator Commands**

All orchestrator commands for managing parallel execution, agent lifecycle, worktree operations, and system monitoring.

## Categories

### 1. Work Distribution (3 commands)

Find available work and coordinate parallel task execution.

| Command | Action | Purpose |
|---------|--------|---------|
| [find-available-work.md](find-available-work.md) | find_available_work | Query specs_task for parallelizable tasks |
| [create-parallel-tasks.md](create-parallel-tasks.md) | create_parallel_tasks | Create orchestrator_task entries for parallel execution |
| [coordinate-dependencies.md](coordinate-dependencies.md) | coordinate_dependencies | Manage specs_task_dependency graph |

### 2. Agent Lifecycle (5 commands)

Manage agent spawning, monitoring, health, and recovery.

| Command | Action | Purpose |
|---------|--------|---------|
| [spawn-agent-session.md](spawn-agent-session.md) | spawn_agent_session | Launch agent using claude command |
| [monitor-agent-lifecycle.md](monitor-agent-lifecycle.md) | monitor_agent_lifecycle | Track agent health and status |
| [kill-stalled-agent.md](kill-stalled-agent.md) | kill_stalled_agent | Terminate unresponsive agents |
| [auto-restart-agent.md](auto-restart-agent.md) | auto_restart_agent | Restart failed agents with backoff |
| [detect-deadlocks.md](detect-deadlocks.md) | detect_deadlocks | Detect circular dependencies |

### 3. Worktree Management (3 commands)

Create, merge, and cleanup git worktrees for parallel development.

| Command | Action | Purpose |
|---------|--------|---------|
| [create-worktree.md](create-worktree.md) | create_worktree | Create git worktree for task isolation |
| [merge-completed-work.md](merge-completed-work.md) | merge_completed_work | Merge task branch to roadmap sequentially |
| [cleanup-worktrees.md](cleanup-worktrees.md) | cleanup_worktrees | Remove completed worktrees |

### 4. System Monitoring (4 commands)

Monitor system resources, inter-agent communication, and overall health.

| Command | Action | Purpose |
|---------|--------|---------|
| [route-inter-agent-messages.md](route-inter-agent-messages.md) | route_inter_agent_messages | Route agent_message entries |
| [monitor-resource-usage.md](monitor-resource-usage.md) | monitor_resource_usage | Track CPU/memory with psutil |
| [generate-activity-summary.md](generate-activity-summary.md) | generate_activity_summary | Create activity reports |
| [handle-agent-errors.md](handle-agent-errors.md) | handle_agent_errors | Handle and recover from errors |

## Quick Reference

### Parallel Execution Flow

```
find-available-work
    ↓
create-parallel-tasks (up to 4 parallel)
    ↓
create-worktree (isolated for each task)
    ↓
spawn-agent-session (launch agent)
    ↓
monitor-agent-lifecycle (track health)
    ↓
Agent completes task
    ↓
merge-completed-work (sequential)
    ↓
cleanup-worktrees
```

### Database Tables

**Written By Commands:**
- agent_lifecycle
- orchestrator_task
- orchestrator_state
- agent_message
- metrics

**Read By Commands:**
- roadmap_priority
- specs_specification
- specs_task
- specs_task_dependency

## CFR Compliance

- **CFR-000**: Singleton agent enforcement (spawn-agent-session)
- **CFR-013**: Git worktree workflow (create-worktree, merge-completed-work, cleanup-worktrees)
- **CFR-014**: Database tracing (all commands)
- **CFR-015**: Centralized database storage (data/ directory)

## Invocation Pattern

All commands follow consistent invocation pattern:

```python
from coffee_maker.claude_agent_invoker import ClaudeAgentInvoker

invoker = ClaudeAgentInvoker(agent_name="orchestrator")

# Invoke any command
result = invoker.invoke_command(
    command_name="find-available-work",
    parameters={"MAX_PARALLEL": "4"}
)
```

## Command Template

All commands include:
- YAML metadata (command, agent, action, tables, cfr_compliance)
- Purpose statement
- Parameters specification
- Database operations (SQL queries)
- Multiple operation examples
- JSON/Markdown output examples
- Success criteria
- Error handling with examples
- Related commands cross-references

## Testing

Comprehensive test suite: `tests/test_orchestrator_commands.py`
- 21 tests covering all commands
- 100% passing (21/21)
- Validates metadata, structure, and CFR compliance

## See Also

- SPEC-106: Full specification
- SPEC-106-IMPLEMENTATION-SUMMARY.md: Complete implementation guide
- CFR-013: Git Worktree Workflow
- CFR-014: Database Tracing
- CFR-000: Singleton Agent Enforcement

---

**Status**: Production Ready
**Last Updated**: 2025-10-26
**Total Commands**: 15
**Test Coverage**: 100%
