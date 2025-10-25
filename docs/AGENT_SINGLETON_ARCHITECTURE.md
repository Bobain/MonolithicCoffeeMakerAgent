# Agent Singleton Architecture

**Document Type**: Architecture Documentation
**Status**: Implemented
**Created**: 2025-10-20
**Implements**: US-035 (Singleton Agent Enforcement)
**Related**: CFR-000 (Prevent File Conflicts)

---

## Overview

The **Agent Singleton Architecture** ensures that only ONE instance of each agent type can run at a time within the MonolithicCoffeeMakerAgent system. This fundamental architectural requirement prevents resource conflicts, duplicate work, race conditions, and file corruption.

### Key Principle

> "Each agent type MUST have exactly ONE running instance. Multiple instances of the same agent type attempting to run simultaneously will be prevented with clear error messages."

---

## Why Singleton Enforcement is Critical

### File Corruption Prevention

Multiple instances of file-owning agents writing to the same files simultaneously can cause:
- Corrupted file contents (interleaved writes)
- Lost updates (one instance overwrites another's changes)
- Inconsistent state across the codebase
- Git merge conflicts that are difficult to resolve

**Example Scenario Without Singleton**:
```python
# BAD: Two code_developer instances running
developer_1 = CodeDeveloper()  # Writes to coffee_maker/utils/helper.py
developer_2 = CodeDeveloper()  # Also writes to coffee_maker/utils/helper.py

# Result: File corruption, race conditions, lost changes
```

### Resource Efficiency

Running duplicate agents wastes:
- CPU and memory resources
- AI API credits (duplicate LLM calls)
- Developer time (confusion from duplicate work)
- Database connections and file handles

### State Consistency

Agents maintain internal state. Multiple instances create:
- Conflicting ROADMAP status updates
- Duplicate notifications
- Race conditions in database writes
- Confusion about which instance is authoritative

---

## Architecture Components

### 1. AgentRegistry Singleton

**Location**: `coffee_maker/autonomous/agent_registry.py:101`

The `AgentRegistry` is itself a singleton class that tracks all running agent instances.

**Key Features**:
- Thread-safe singleton pattern with double-checked locking
- Tracks agent type, PID, and start time
- Raises clear errors on duplicate registration attempts
- Provides context manager for automatic cleanup
- Thread-safe with `threading.Lock`

**Example**:
```python
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

# Get the singleton registry instance
registry = AgentRegistry()

# Register an agent
registry.register_agent(AgentType.CODE_DEVELOPER)

# Check if registered
if registry.is_registered(AgentType.CODE_DEVELOPER):
    print("Code developer is running!")

# Unregister when done
registry.unregister_agent(AgentType.CODE_DEVELOPER)
```

### 2. AgentType Enum

**Location**: `coffee_maker/autonomous/agent_registry.py:46`

Defines all valid agent types in the system.

**Autonomous Agents** (8 total):
1. `ORCHESTRATOR` - Coordinates all other 7 agents
2. `ARCHITECT` - Creates technical specifications
3. `CODE_DEVELOPER` - Implements priorities from ROADMAP
4. `PROJECT_MANAGER` - Monitors GitHub, verifies DoD
5. `ASSISTANT` - Creates demos, reports bugs
6. `ASSISTANT` - Deep code analysis
7. `UX_DESIGN_EXPERT` - Design guidance
8. `CODE_REVIEWER` - Quality assurance and code review

**Infrastructure Agents**:
- `USER_LISTENER` - Primary user interface
- `GENERATOR` - ACE framework (observes executions)
- `REFLECTOR` - ACE framework (extracts insights)
- `CURATOR` - ACE framework (maintains playbooks)

### 3. AgentAlreadyRunningError Exception

**Location**: `coffee_maker/autonomous/agent_registry.py:83`

Custom exception raised when duplicate agent registration is attempted.

**Error Message Format**:
```
Agent 'code_developer' is already running!
  PID: 12345
  Started at: 2025-10-20T14:30:00

Only ONE instance of each agent type can run at a time.
Please stop the existing agent before starting a new one.
```

---

## Singleton Enforcement Rules

### File-Owning Agents (MUST be singleton)

These agents write to specific directories and MUST be singletons:

| Agent | Owned Directories | Why Singleton |
|-------|------------------|---------------|
| `code_developer` | `.claude/`, `coffee_maker/`, `tests/` | Prevents code conflicts |
| `project_manager` | `docs/roadmap/` | Prevents ROADMAP conflicts |
| `architect` | `docs/architecture/` | Prevents spec conflicts |
| `generator` | `docs/generator/` | Prevents playbook conflicts |
| `reflector` | `docs/reflector/` | Prevents insight conflicts |
| `curator` | `docs/curator/` | Prevents curation conflicts |

### Non-File-Owning Agents (Multiple instances allowed)

These agents are READ-ONLY or delegation-only and can have multiple instances:

| Agent | Why Multiple Instances OK |
|-------|--------------------------|
| `assistant` | READ-ONLY, only reads and delegates |
| `user_listener` | Delegation-only, no writes |
| `assistant (with code analysis skills)` | READ-ONLY, only analyzes code |
| `ux-design-expert` | Provides specs, doesn't write files |

**Note**: While multiple instances are technically safe for these agents, the current implementation enforces singleton for ALL agents for consistency and simplicity.

---

## Usage Patterns

### Pattern 1: Context Manager (Recommended)

The context manager automatically registers and unregisters the agent:

```python
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

# Automatic registration and cleanup
with AgentRegistry.register(AgentType.CODE_DEVELOPER):
    # Agent work here
    print("Code developer is running!")
    # Automatically unregistered on exit (even if exception occurs)
```

**Benefits**:
- Automatic cleanup (even on exceptions)
- Clear scope of agent lifetime
- No risk of forgetting to unregister
- Recommended for all agent implementations

### Pattern 2: Manual Registration

Manual control over registration lifecycle:

```python
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

registry = AgentRegistry()

try:
    # Register agent
    registry.register_agent(AgentType.CODE_DEVELOPER)

    # Agent work here
    print("Code developer is running!")

finally:
    # Always unregister in finally block
    registry.unregister_agent(AgentType.CODE_DEVELOPER)
```

**Use Cases**:
- When you need custom cleanup logic
- When agent lifetime doesn't map to a code block
- For testing and debugging

### Pattern 3: Querying Registry State

Check current agent status:

```python
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

registry = AgentRegistry()

# Check if specific agent is running
if registry.is_registered(AgentType.CODE_DEVELOPER):
    print("Code developer is already running!")

# Get agent info
info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
if info:
    print(f"PID: {info['pid']}")
    print(f"Started: {info['started_at']}")

# Get all running agents
all_agents = registry.get_all_registered_agents()
for agent_type, agent_info in all_agents.items():
    print(f"{agent_type.value}: PID {agent_info['pid']}")
```

---

## Thread Safety

### Concurrent Registration Protection

The registry uses thread-safe locking to prevent race conditions:

```python
import threading
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

registry = AgentRegistry()

def try_start_agent():
    try:
        registry.register_agent(AgentType.CODE_DEVELOPER)
        print("Agent started successfully!")
    except AgentAlreadyRunningError:
        print("Agent already running, skipping...")

# Try to start from 10 threads simultaneously
threads = [threading.Thread(target=try_start_agent) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Result: Exactly ONE thread succeeds, others get AgentAlreadyRunningError
```

### Locking Strategy

**Class-level Lock** (`_lock`):
- Protects singleton instance creation
- Ensures only one `AgentRegistry` instance exists

**Instance-level Lock** (`_agent_lock`):
- Protects agent registration operations
- Prevents race conditions in `register_agent()`, `unregister_agent()`
- Ensures atomic read-modify-write operations

---

## Error Handling

### Duplicate Agent Detection

**Scenario**: Attempting to start an agent that's already running

```python
from coffee_maker.autonomous.agent_registry import (
    AgentRegistry,
    AgentType,
    AgentAlreadyRunningError
)

registry = AgentRegistry()

# First instance succeeds
registry.register_agent(AgentType.CODE_DEVELOPER)

# Second instance fails with clear error
try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
except AgentAlreadyRunningError as e:
    print(f"Error: {e}")
    print(f"Agent type: {e.agent_type}")
    print(f"Existing PID: {e.existing_pid}")
    print(f"Started at: {e.existing_started_at}")
```

**Output**:
```
Error: Agent 'code_developer' is already running!
  PID: 12345
  Started at: 2025-10-20T14:30:00

Only ONE instance of each agent type can run at a time.
Please stop the existing agent before starting a new one.

Agent type: AgentType.CODE_DEVELOPER
Existing PID: 12345
Started at: 2025-10-20T14:30:00
```

### Recovery Strategies

**Strategy 1: Wait and Retry**
```python
import time
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

registry = AgentRegistry()
max_retries = 5

for attempt in range(max_retries):
    try:
        registry.register_agent(AgentType.CODE_DEVELOPER)
        break  # Success
    except AgentAlreadyRunningError:
        if attempt < max_retries - 1:
            print(f"Waiting for agent to finish (attempt {attempt+1}/{max_retries})...")
            time.sleep(10)
        else:
            raise  # Max retries exceeded
```

**Strategy 2: Kill and Replace**
```python
import os
import signal
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

registry = AgentRegistry()

try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
except AgentAlreadyRunningError as e:
    # Get PID of running agent
    existing_pid = e.existing_pid

    # Confirm with user before killing
    response = input(f"Kill existing agent (PID {existing_pid})? [y/N]: ")
    if response.lower() == 'y':
        os.kill(existing_pid, signal.SIGTERM)
        time.sleep(2)  # Wait for cleanup
        registry.unregister_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.CODE_DEVELOPER)
```

**Strategy 3: Graceful Handoff**
```python
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

registry = AgentRegistry()

# Signal existing agent to shut down gracefully
# (implementation depends on agent's shutdown mechanism)
if registry.is_registered(AgentType.CODE_DEVELOPER):
    # Send shutdown signal via notification system
    # Wait for clean shutdown
    pass

# Register new instance
registry.register_agent(AgentType.CODE_DEVELOPER)
```

---

## Testing

### Unit Tests

**Location**: `tests/unit/test_agent_registry.py:1`

**Test Coverage** (30+ tests):
- Singleton pattern enforcement
- Agent registration/unregistration
- Duplicate detection
- Thread safety
- Context manager behavior
- Error messages
- Edge cases (stale agents, null instances)

**Example Test**:
```python
def test_duplicate_registration_raises_error(self):
    """Test that registering same agent twice raises error."""
    registry = AgentRegistry()
    registry.register_agent(AgentType.CODE_DEVELOPER)

    with pytest.raises(AgentAlreadyRunningError) as exc_info:
        registry.register_agent(AgentType.CODE_DEVELOPER)

    assert "already running" in str(exc_info.value)
    assert "code_developer" in str(exc_info.value).lower()
```

### Integration Testing

**Test Scenarios**:
1. Start agent daemon → verify singleton registration
2. Attempt duplicate start → verify error
3. Agent crash → verify cleanup
4. Agent restart → verify re-registration succeeds

**Manual Testing Steps**:
```bash
# Terminal 1: Start code_developer
poetry run code-developer --verbose

# Terminal 2: Attempt duplicate start (should fail)
poetry run code-developer --verbose
# Expected: AgentAlreadyRunningError with PID and timestamp

# Terminal 1: Stop agent (Ctrl+C)

# Terminal 2: Retry (should succeed now)
poetry run code-developer --verbose
```

---

## Monitoring and Debugging

### CLI Commands

**View Running Agents**:
```python
from coffee_maker.autonomous.agent_registry import AgentRegistry

registry = AgentRegistry()
all_agents = registry.get_all_registered_agents()

print("Currently Running Agents:")
print("-" * 60)
for agent_type, info in all_agents.items():
    print(f"{agent_type.value:20} PID: {info['pid']:6}  Started: {info['started_at']}")
```

**Expected Output**:
```
Currently Running Agents:
------------------------------------------------------------
code_developer       PID: 12345  Started: 2025-10-20T14:30:00
project_manager      PID: 12346  Started: 2025-10-20T14:31:00
architect            PID: 12347  Started: 2025-10-20T14:32:00
```

### Logging

The registry logs all registration events:

```python
import logging

logger = logging.getLogger("coffee_maker.autonomous.agent_registry")
logger.setLevel(logging.INFO)

# Log output:
# INFO: AgentRegistry initialized (singleton)
# INFO: Agent registered: code_developer (PID: 12345)
# INFO: Agent unregistered: code_developer (PID: 12345)
```

---

## Common Issues and Solutions

### Issue 1: "Agent already running" Error

**Symptom**:
```
AgentAlreadyRunningError: Agent 'code_developer' is already running!
  PID: 12345
  Started at: 2025-10-20T14:30:00
```

**Possible Causes**:
1. Another instance is actually running
2. Previous instance crashed without cleanup
3. Stale registration from system restart

**Solutions**:
```bash
# Check if process is running
ps aux | grep 12345

# If not running, clean up registry:
# (Registry reset typically happens automatically, but manual cleanup available)

# If running, stop it first:
kill 12345

# Or use graceful shutdown via CLI
```

### Issue 2: Stale Registrations After Crash

**Symptom**: Agent crashed but registry still shows it as running

**Solution**: The registry is in-memory only, so restarting the parent process (or system) clears all registrations. For production systems, consider implementing persistent registry with heartbeat checks.

**Future Enhancement**:
```python
# Potential cleanup mechanism
registry.cleanup_stale_agents(max_age_minutes=60)
```

### Issue 3: Thread Safety in Multi-Threaded Environments

**Symptom**: Race conditions when multiple threads try to register agents

**Solution**: Already handled by `AgentRegistry` using `threading.Lock`. All operations are atomic and thread-safe.

---

## Best Practices

### 1. Always Use Context Manager

```python
# GOOD: Automatic cleanup
with AgentRegistry.register(AgentType.CODE_DEVELOPER):
    agent.do_work()

# BAD: Manual cleanup (error-prone)
registry.register_agent(AgentType.CODE_DEVELOPER)
agent.do_work()
registry.unregister_agent(AgentType.CODE_DEVELOPER)  # Might not execute on exception
```

### 2. Check Before Registering

```python
# GOOD: Check first, provide helpful message
registry = AgentRegistry()
if registry.is_registered(AgentType.CODE_DEVELOPER):
    print("Code developer is already running. Waiting for it to finish...")
    # Implement wait logic or exit gracefully
else:
    registry.register_agent(AgentType.CODE_DEVELOPER)
```

### 3. Handle Errors Gracefully

```python
# GOOD: Catch and handle specific errors
try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
except AgentAlreadyRunningError as e:
    logger.error(f"Cannot start agent: {e}")
    # Provide user-friendly error message
    # Suggest alternatives (wait, kill, etc.)
```

### 4. Clean Shutdown

```python
# GOOD: Ensure cleanup in signal handlers
import signal
import sys

def signal_handler(sig, frame):
    registry.unregister_agent(AgentType.CODE_DEVELOPER)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

---

## Future Enhancements

### 1. Persistent Registry

**Current**: In-memory registry (clears on process restart)
**Future**: SQLite-backed registry for persistence across restarts

**Benefits**:
- Detect stale registrations from crashes
- Survive system restarts
- Historical tracking of agent runs

### 2. Heartbeat Mechanism

**Current**: No liveness detection
**Future**: Agents send periodic heartbeats

**Benefits**:
- Auto-cleanup of crashed agents
- Detect hung agents
- More robust stale agent detection

### 3. Resource Quotas

**Future**: Limit concurrent agents by resource usage

**Example**:
```python
# Only allow 3 total autonomous agents at once
registry.set_max_total_agents(3)
```

### 4. Agent Priority Queue

**Future**: Queue agents waiting to run

**Benefits**:
- Graceful handling of duplicate starts
- Automatic retry when slot available
- Priority-based agent scheduling

---

## Related Documentation

- **Implementation**: `coffee_maker/autonomous/agent_registry.py`
- **Tests**: `tests/unit/test_agent_registry.py`
- **User Story**: `docs/roadmap/ROADMAP.md` (US-035)
- **CFR**: `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` (CFR-000)
- **Agent Ownership**: `docs/AGENT_OWNERSHIP.md`
- **Project Instructions**: `.claude/CLAUDE.md`

---

## Summary

The Agent Singleton Architecture is a critical safety mechanism that:

✅ Prevents file corruption from concurrent writes
✅ Eliminates duplicate work and resource waste
✅ Ensures consistent state across the system
✅ Provides clear error messages for troubleshooting
✅ Uses thread-safe implementation with proper locking
✅ Offers both context manager and manual registration patterns
✅ Is fully tested with 30+ unit tests

**Key Takeaway**: Always use the context manager pattern for automatic cleanup and error safety. The singleton enforcement is a fundamental architectural requirement that MUST be respected by all agents.

---

**Document Status**: Complete
**Last Updated**: 2025-10-20
**Maintained By**: Architect
