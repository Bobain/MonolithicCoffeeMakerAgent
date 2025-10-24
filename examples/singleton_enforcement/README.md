# Singleton Enforcement Examples

This directory contains practical examples demonstrating the Agent Singleton Enforcement architecture implemented in MonolithicCoffeeMakerAgent.

## Overview

The Agent Singleton Architecture ensures that only ONE instance of each agent type can run at a time, preventing:
- File corruption from concurrent writes
- Resource waste (CPU, memory, API credits)
- Race conditions and duplicate work
- Inconsistent state and lost updates

## Examples

### 01_basic_usage.py

**Basic singleton enforcement patterns and usage**

Demonstrates:
- Successful agent registration
- Duplicate agent detection
- Multiple different agent types running simultaneously
- Context manager pattern (recommended)
- Error recovery strategies
- Querying agent status

Run:
```bash
poetry run python examples/singleton_enforcement/01_basic_usage.py
```

**Key Takeaways**:
- Use context manager (`with AgentRegistry.register()`) for automatic cleanup
- Only ONE instance of each agent type allowed
- Clear error messages with PID and timestamp
- Thread-safe registry with proper locking

### 02_thread_safety.py

**Thread-safe concurrent agent registration**

Demonstrates:
- Multiple threads trying to register the same agent (only 1 succeeds)
- Concurrent registration of different agent types (all succeed)
- Concurrent register/unregister operations
- Context managers with concurrency
- Stress test with 100 concurrent threads

Run:
```bash
poetry run python examples/singleton_enforcement/02_thread_safety.py
```

**Key Findings**:
- Registry maintains consistency under high load
- Exactly ONE thread succeeds when registering same agent type
- No deadlocks or race conditions
- Context managers cleanup properly even with concurrency

### 03_real_world_scenarios.py

**Real-world problems prevented by singleton enforcement**

Demonstrates:
- **Scenario 1**: File corruption prevention (duplicate code_developer)
- **Scenario 2**: ROADMAP conflict prevention (duplicate project_manager)
- **Scenario 3**: Resource waste prevention (duplicate architect)
- **Scenario 4**: Daemon startup race condition prevention
- **Scenario 5**: Crash recovery and restart
- **Scenario 6**: Monitoring dashboard with accurate agent counts

Run:
```bash
poetry run python examples/singleton_enforcement/03_real_world_scenarios.py
```

**Problems Prevented**:
- ✅ File corruption from interleaved writes
- ✅ Lost updates and conflicting changes
- ✅ Wasted CPU, memory, and API credits
- ✅ Duplicate work and race conditions
- ✅ Inconsistent monitoring and status tracking

## Quick Start

Run all examples in sequence:

```bash
# 1. Basic usage patterns
poetry run python examples/singleton_enforcement/01_basic_usage.py

# 2. Thread safety verification
poetry run python examples/singleton_enforcement/02_thread_safety.py

# 3. Real-world scenarios
poetry run python examples/singleton_enforcement/03_real_world_scenarios.py
```

## Key Concepts

### AgentRegistry

**Location**: `coffee_maker/autonomous/agent_registry.py:101`

The singleton registry that tracks all running agent instances.

**Features**:
- Thread-safe with `threading.Lock`
- Tracks agent type, PID, start time
- Raises `AgentAlreadyRunningError` on duplicates
- Context manager for automatic cleanup

### AgentType Enum

**Location**: `coffee_maker/autonomous/agent_registry.py:46`

Defines all valid agent types:
- `CODE_DEVELOPER` - Implements features
- `PROJECT_MANAGER` - Monitors ROADMAP
- `ARCHITECT` - Creates specs
- `ASSISTANT` - Creates demos
- `ASSISTANT` - Analyzes code
- `UX_DESIGN_EXPERT` - Design guidance
- `CODE_REVIEWER` - QA and reviews
- And more...

### Usage Patterns

**Pattern 1: Context Manager (Recommended)**
```python
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

with AgentRegistry.register(AgentType.CODE_DEVELOPER):
    # Agent work here
    # Automatically unregistered on exit
```

**Pattern 2: Manual Registration**
```python
registry = AgentRegistry()
try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
    # Agent work here
finally:
    registry.unregister_agent(AgentType.CODE_DEVELOPER)
```

**Pattern 3: Error Handling**
```python
from coffee_maker.autonomous.agent_registry import (
    AgentRegistry,
    AgentType,
    AgentAlreadyRunningError
)

try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
except AgentAlreadyRunningError as e:
    print(f"Agent already running!")
    print(f"PID: {e.existing_pid}")
    print(f"Started: {e.existing_started_at}")
```

## Testing

All examples include comprehensive testing:
- ✅ Singleton pattern enforcement
- ✅ Thread safety verification
- ✅ Error message validation
- ✅ Context manager cleanup
- ✅ Concurrent operations

## Related Documentation

- **Architecture**: `docs/AGENT_SINGLETON_ARCHITECTURE.md`
- **Implementation**: `coffee_maker/autonomous/agent_registry.py`
- **Tests**: `tests/unit/test_agent_registry.py` (30+ tests)
- **User Story**: `docs/roadmap/ROADMAP.md` (US-035)
- **Project Guide**: `.claude/CLAUDE.md`

## Expected Output

When you run the examples, you should see:
- ✅ Clear success/failure indicators
- 📊 Agent registration details (PID, timestamp)
- ⚠️  Error messages for duplicate attempts
- 💡 Key insights and takeaways

## Common Use Cases

### Starting a Daemon

```python
# In daemon startup code
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

registry = AgentRegistry()

# Check if already running
if registry.is_registered(AgentType.CODE_DEVELOPER):
    info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
    print(f"Daemon already running (PID: {info['pid']})")
    exit(1)

# Register and start
with AgentRegistry.register(AgentType.CODE_DEVELOPER):
    # Daemon main loop
    run_daemon()
```

### Monitoring Running Agents

```python
# In monitoring dashboard
from coffee_maker.autonomous.agent_registry import AgentRegistry

registry = AgentRegistry()
all_agents = registry.get_all_registered_agents()

print("Currently Running Agents:")
for agent_type, info in all_agents.items():
    print(f"  • {agent_type.value}: PID {info['pid']}")
```

### Graceful Restart

```python
# In restart logic
from coffee_maker.autonomous.agent_registry import (
    AgentRegistry,
    AgentType,
    AgentAlreadyRunningError
)

registry = AgentRegistry()

try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
except AgentAlreadyRunningError as e:
    # Signal existing agent to shutdown
    send_shutdown_signal(e.existing_pid)

    # Wait for cleanup
    time.sleep(5)

    # Retry registration
    registry.register_agent(AgentType.CODE_DEVELOPER)
```

## Troubleshooting

### "Agent already running" Error

**Check if process exists**:
```bash
ps aux | grep <PID>
```

**If stale registration** (process not running):
- Registry is in-memory, so restart parent process clears it
- For persistent registry, implement cleanup mechanism

### Concurrency Issues

All operations are thread-safe. If you see race conditions:
- Verify you're using the singleton `AgentRegistry` instance
- Check that you're not bypassing the registry

### Memory Leaks

Always unregister agents when done:
- Use context manager pattern (automatic cleanup)
- Or ensure `unregister_agent()` in `finally` block

## Performance

**Registry Operations**:
- Register: O(1) - Hash table lookup
- Unregister: O(1) - Hash table delete
- Check registered: O(1) - Hash table lookup
- Thread-safe: Uses `threading.Lock` (minimal overhead)

**Stress Test Results** (from 02_thread_safety.py):
- ✅ 100 concurrent threads handled correctly
- ✅ No deadlocks or race conditions
- ✅ All operations completed successfully
- ✅ Registry maintained consistency

## Best Practices

1. **Always use context manager** for automatic cleanup
2. **Check before registering** to provide helpful messages
3. **Handle errors gracefully** with clear user feedback
4. **Implement clean shutdown** to unregister agents properly
5. **Monitor agent status** for operational visibility

## Summary

The singleton enforcement examples demonstrate that:

✅ Only ONE instance of each agent type can run
✅ Registry is thread-safe and handles concurrency
✅ Clear error messages aid troubleshooting
✅ Context managers ensure proper cleanup
✅ Prevents real-world problems (corruption, waste, races)
✅ Essential for system stability and data integrity

**Key Insight**: Singleton enforcement is a CRITICAL architectural requirement, not just a nice-to-have feature!
