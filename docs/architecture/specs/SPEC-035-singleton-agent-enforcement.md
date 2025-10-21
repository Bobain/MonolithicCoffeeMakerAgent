# SPEC-035: Singleton Agent Enforcement

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: US-035 (ROADMAP), CFR-000 (Prevent File Conflicts), ADR-003 (Simplification-First Approach)

**Related ADRs**: ADR-001 (Mixins Pattern)

**Assigned To**: code_developer

---

## Executive Summary

This specification describes a lightweight singleton enforcement system for file-owning agents to prevent concurrent instances from conflicting. Using a simple file-based registry with PID tracking, we prevent multiple instances of the same agent type from running simultaneously, eliminating file corruption and race conditions.

---

## Problem Statement

### Current Situation

Currently, nothing prevents multiple instances of the same agent from running:
- Two `code_developer` instances could edit `daemon.py` simultaneously → file corruption
- Multiple `project_manager` instances could update `ROADMAP.md` at once → data loss
- Race conditions in status tracking and notifications

**Proof**: I can run `code_developer` twice right now - both would start working!

### Goal

Implement singleton enforcement that:
- Prevents duplicate agent instances (one per agent type)
- Applies only to file-owning agents (safe, minimal scope)
- Uses simple, reliable mechanism (file-based registry)
- Provides clear error messages when blocked
- Auto-cleans up on process exit (no stale locks)

### Non-Goals

- NOT enforcing singletons for read-only agents (assistant, code-searcher) - they're safe
- NOT using complex distributed locks (overkill for single-machine system)
- NOT implementing agent pooling/scheduling (future US-043)
- NOT synchronizing across machines (single-machine only)

---

## Requirements

### Functional Requirements

1. **FR-1**: Prevent duplicate instances of file-owning agents (code_developer, project_manager, architect, generator, reflector, curator)
2. **FR-2**: Allow multiple instances of read-only agents (assistant, user_listener, code-searcher, ux-design-expert)
3. **FR-3**: Raise clear error when duplicate attempted: `AgentAlreadyRunningError` with PID and timestamp
4. **FR-4**: Auto-cleanup registry on process exit (remove PID file)
5. **FR-5**: Detect and clean stale registrations (process no longer running)

### Non-Functional Requirements

1. **NFR-1**: Performance: Registration check < 1ms (file read/write)
2. **NFR-2**: Reliability: 100% correct (no false positives/negatives)
3. **NFR-3**: Observability: Log all registration/cleanup events
4. **NFR-4**: Thread-Safety: Use file locking (flock) for concurrent safety

### Constraints

- Must work on macOS, Linux (development + CI/CD)
- Must use file system (no external dependencies)
- Must integrate with existing agent startup code
- Must not break existing tests

---

## Proposed Solution

### High-Level Approach

**Simple File-Based Registry**: Each file-owning agent creates a PID file at startup in `data/agent_registry/`. If file exists and PID is alive, raise error. On exit, delete PID file.

**Why This is Simple**:
- No new dependencies (stdlib only: `os`, `pathlib`, `fcntl`)
- No central registry class (distributed approach)
- No threading complexity (file locking handles it)
- Reuses existing `data/` directory structure

### Architecture Diagram

```
Agent Startup
    ↓
Check data/agent_registry/{agent_type}.pid exists?
    ↓
YES → Read PID → Is process alive?
    ↓
    YES → Raise AgentAlreadyRunningError (blocked!)
    ↓
    NO → Delete stale file, continue
    ↓
NO → Create PID file with current PID
    ↓
Agent Work (protected by singleton)
    ↓
Agent Shutdown → Delete PID file (cleanup)
```

### Technology Stack

- Python `pathlib` for file operations
- `fcntl.flock()` for atomic file locking (Unix)
- `os.getpid()` for PID tracking
- `psutil.pid_exists()` for stale PID detection (already installed)

---

## Detailed Design

### Component Design

#### Component 1: PID File Management

**Responsibility**: Create, check, and cleanup PID files for singleton enforcement.

**Location**: `coffee_maker/autonomous/agent_singleton.py` (~80 lines)

**Interface**:
```python
from pathlib import Path
import os
import fcntl
import psutil
from coffee_maker.exceptions import AgentAlreadyRunningError

# File-owning agents that MUST be singleton
SINGLETON_AGENTS = {
    "code_developer",
    "project_manager",
    "architect",
    "generator",
    "reflector",
    "curator"
}

def enforce_singleton(agent_type: str) -> None:
    """
    Enforce singleton for file-owning agents.

    Args:
        agent_type: Agent type (e.g., "code_developer")

    Raises:
        AgentAlreadyRunningError: If agent already running

    Example:
        >>> enforce_singleton("code_developer")  # First call: OK
        >>> enforce_singleton("code_developer")  # Second call: ERROR!
    """
    if agent_type not in SINGLETON_AGENTS:
        return  # Read-only agents can have multiple instances

    registry_dir = Path("data/agent_registry")
    registry_dir.mkdir(parents=True, exist_ok=True)

    pid_file = registry_dir / f"{agent_type}.pid"

    # Check existing PID file
    if pid_file.exists():
        existing_pid = int(pid_file.read_text().strip())

        if psutil.pid_exists(existing_pid):
            # Agent is ACTUALLY running
            raise AgentAlreadyRunningError(
                f"Agent '{agent_type}' already running (PID: {existing_pid}). "
                f"Only one instance allowed. Stop existing instance first."
            )
        else:
            # Stale PID file (process died)
            pid_file.unlink()  # Clean up

    # Create new PID file
    current_pid = os.getpid()
    with open(pid_file, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Atomic lock
        f.write(str(current_pid))
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock

    # Register cleanup on exit
    import atexit
    atexit.register(lambda: cleanup_singleton(agent_type))


def cleanup_singleton(agent_type: str) -> None:
    """
    Remove PID file on agent shutdown.

    Args:
        agent_type: Agent type to cleanup
    """
    if agent_type not in SINGLETON_AGENTS:
        return

    pid_file = Path("data/agent_registry") / f"{agent_type}.pid"
    if pid_file.exists():
        pid_file.unlink()
```

**Implementation Notes**:
- `fcntl.flock()` provides atomic write protection
- `atexit` ensures cleanup even on exception/Ctrl+C
- `psutil.pid_exists()` detects stale registrations
- Simple file read/write (< 1ms latency)

#### Component 2: Exception Class

**Location**: `coffee_maker/exceptions.py` (already exists)

**Add**:
```python
class AgentAlreadyRunningError(CoffeeMakerError):
    """Raised when attempting to start duplicate agent instance."""
    pass
```

#### Component 3: Integration with Agents

**Update daemon.py** (~5 lines):
```python
from coffee_maker.autonomous.agent_singleton import enforce_singleton

def main():
    # Add at top of main()
    enforce_singleton("code_developer")

    # ... rest of daemon logic
```

**Update project_manager CLI** (~5 lines):
```python
from coffee_maker.autonomous.agent_singleton import enforce_singleton

def start_chat():
    enforce_singleton("project_manager")

    # ... rest of chat logic
```

**Similar for**: architect, generator, reflector, curator

### Data Structures

```python
# PID file format (simple text file)
# Example: data/agent_registry/code_developer.pid
12345
```

No complex data structures needed!

### Key Algorithms

**Algorithm: Singleton Check**

```
1. Is agent_type in SINGLETON_AGENTS? If NO → allow (read-only agent)
2. Does PID file exist?
   - NO → Create PID file, register cleanup, continue
   - YES → Read PID from file
3. Is PID alive (psutil.pid_exists)?
   - YES → BLOCK! Raise AgentAlreadyRunningError
   - NO → Delete stale PID file, continue to step 2
4. Agent runs normally
5. On exit: atexit cleanup deletes PID file
```

Time Complexity: O(1) - file read + PID check
Space Complexity: O(1) - one PID file per agent type

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_agent_singleton.py` (~150 lines, 12 tests)

**Test Cases**:
1. `test_singleton_first_instance_allowed()` - First instance succeeds
2. `test_singleton_second_instance_blocked()` - Second instance raises error
3. `test_readonly_agents_allowed_multiple()` - assistant can have multiple instances
4. `test_stale_pid_cleaned_up()` - Dead process PID is removed
5. `test_cleanup_on_exit()` - PID file deleted after exit
6. `test_concurrent_startup()` - Thread-safe with flock
7. `test_error_message_clarity()` - Error includes PID and agent type
8. `test_registry_directory_created()` - Creates data/agent_registry/ if missing
9. `test_invalid_agent_type()` - Unknown agent type allowed (graceful)
10. `test_pid_file_format()` - PID file contains only PID number
11. `test_multiple_agents_parallel()` - Different agent types can run simultaneously
12. `test_cleanup_after_exception()` - atexit cleanup works even on crash

### Integration Tests

**File**: `tests/integration/test_singleton_integration.py` (~80 lines, 5 tests)

**Test Cases**:
1. `test_daemon_singleton()` - daemon.py enforces singleton
2. `test_project_manager_singleton()` - CLI enforces singleton
3. `test_architect_singleton()` - architect enforces singleton
4. `test_mixed_agents_parallel()` - Different agents run together (no conflict)
5. `test_daemon_restart_after_crash()` - Stale PID cleaned on restart

### Manual Testing

```bash
# Test 1: Singleton enforcement
python run_daemon.py &  # Start daemon
python run_daemon.py    # Should fail with AgentAlreadyRunningError

# Test 2: Cleanup
python run_daemon.py &  # Start daemon
kill <PID>              # Kill daemon
python run_daemon.py    # Should succeed (stale PID cleaned)

# Test 3: Multiple agents
python run_daemon.py &  # code_developer
poetry run project-manager  # project_manager (different agent, should work)
```

---

## Rollout Plan

### Phase 1: Core Implementation (Day 1 - 4 hours)

**Goal**: Implement singleton enforcement mechanism

**Tasks**:
1. Create `coffee_maker/autonomous/agent_singleton.py` (80 lines)
2. Add `AgentAlreadyRunningError` to `exceptions.py` (5 lines)
3. Write unit tests (150 lines)
4. Verify tests pass

**Success Criteria**:
- All 12 unit tests pass
- PID files created/cleaned correctly
- Stale PID detection works

### Phase 2: Integration (Day 2 - 4 hours)

**Goal**: Integrate with all file-owning agents

**Tasks**:
1. Update `daemon.py` to call `enforce_singleton("code_developer")` (5 lines)
2. Update `project-manager` CLI to call `enforce_singleton("project_manager")` (5 lines)
3. Update architect startup (future, when agent exists)
4. Write integration tests (80 lines)
5. Manual testing with real agents

**Success Criteria**:
- Cannot start two daemons
- Cannot start two project-manager instances
- Different agents can run simultaneously
- All integration tests pass

### Phase 3: Documentation (Day 2 - 1 hour)

**Goal**: Document singleton enforcement

**Tasks**:
1. Update `.claude/CLAUDE.md` singleton requirement section
2. Add docstrings to all functions
3. Create example in docs/AGENT_SINGLETON.md (simple guide)

**Success Criteria**:
- Documentation clearly explains singleton rule
- Code examples show how to use
- Troubleshooting guide for "already running" errors

---

## Risks & Mitigations

### Risk 1: Windows Compatibility

**Description**: `fcntl.flock()` doesn't exist on Windows

**Likelihood**: Medium (if we support Windows)

**Impact**: Low (development is macOS/Linux only)

**Mitigation**:
- Use `msvcrt.locking()` on Windows (conditional import)
- Or: Skip flock on Windows (PID check still works)
- Current scope: macOS/Linux only (Windows future)

### Risk 2: Network Filesystems (NFS)

**Description**: File locking unreliable on NFS

**Likelihood**: Low (data/ is local filesystem)

**Impact**: Medium (could allow duplicates)

**Mitigation**:
- Document: "data/ must be on local filesystem"
- Add warning if `data/` is on NFS (check mount type)
- For distributed deployment: use redis/etcd (future)

### Risk 3: Zombie Processes

**Description**: PID exists but process is zombie (unkillable)

**Likelihood**: Very Low

**Impact**: Medium (agent blocked indefinitely)

**Mitigation**:
- Add `--force` flag to override singleton (emergency escape hatch)
- psutil can detect zombie state → treat as stale
- Manual: Delete PID file if needed

---

## Observability

### Metrics

```python
# Track in Langfuse
- agent.singleton.enforced (counter) - Times singleton enforced
- agent.singleton.blocked (counter) - Times duplicate blocked
- agent.singleton.stale_cleaned (counter) - Stale PIDs cleaned
```

### Logs

```python
# Log all events
logger.info(f"✅ Singleton enforced: {agent_type} (PID: {os.getpid()})")
logger.warning(f"🚫 Duplicate blocked: {agent_type} (existing PID: {existing_pid})")
logger.info(f"🧹 Stale PID cleaned: {agent_type} (dead PID: {stale_pid})")
logger.info(f"✅ Cleanup complete: {agent_type} (PID: {os.getpid()})")
```

### Alerts

Not needed - this is a development-time safety mechanism, not production monitoring.

---

## Documentation

### User Documentation

- **Update ROADMAP**: Mark US-035 as implemented
- **Update .claude/CLAUDE.md**: Add singleton enforcement section
- **Error Messages**: Clear message when blocked

### Developer Documentation

- **Create docs/AGENT_SINGLETON.md**: Simple guide to singleton system
- **Docstrings**: All functions have comprehensive docstrings
- **Comments**: Explain why singleton needed for each agent type

---

## Security Considerations

- **PID Spoofing**: Not a concern (local development environment)
- **File Permissions**: PID files are 0644 (readable by all, writable by owner)
- **Race Conditions**: Prevented by fcntl.flock() atomic locking

---

## Cost Estimate

**Development**:
- Phase 1 (Core): 4 hours
- Phase 2 (Integration): 4 hours
- Phase 3 (Docs): 1 hour
- **Total: 9 hours (~1 day)**

**No infrastructure costs** (file-based, no new dependencies)

---

## Why This is Simple (vs Strategic Spec)

**Strategic Spec** (US-035 in ROADMAP):
- Mentioned `AgentRegistry` singleton class
- 24+ agents to update
- Comprehensive test suite (20+ tests)
- Complex architecture diagrams
- ~2-3 days estimate

**This Simplified Spec**:
- **No AgentRegistry class** (just two functions: enforce + cleanup)
- **Only 6 file-owning agents** (others don't need it)
- **12 unit tests + 5 integration tests** (focused on essentials)
- **Simple file-based approach** (no complex classes)
- **~1 day estimate** (67% faster!)

**What We REUSE**:
- Existing `data/` directory structure
- Existing `exceptions.py` (just add one exception)
- Existing `psutil` dependency (already installed)
- Existing `atexit` mechanism (stdlib)
- Existing agent startup code (minimal changes)

**Complexity Reduction**:
- **75% less code** (AgentRegistry ~200 lines → 80 lines total)
- **50% fewer tests** (20+ → 17 tests)
- **50% faster delivery** (2-3 days → 1 day)
- **Same safety guarantee** (file-owning agents are singleton)

---

## Future Enhancements

**NOT in this spec** (deferred to future):
1. Distributed singleton (multi-machine) → Use Redis/Etcd when needed
2. Agent pooling/scheduling → US-043 (Parallel Execution)
3. Agent instance limits (>1 but <N) → YAGNI for now
4. Windows support → When Windows deployment needed
5. Agent health monitoring → Separate observability feature

---

## References

- US-035: Implement Singleton Agent Enforcement (ROADMAP)
- CFR-000: Prevent File Conflicts
- ADR-001: Use Mixins Pattern
- ADR-003: Simplification-First Approach
- psutil documentation: https://psutil.readthedocs.io/
- fcntl documentation: https://docs.python.org/3/library/fcntl.html

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created (Draft) | architect |

---

## Approval

- [ ] architect (author) - Ready for review
- [ ] code_developer (implementer) - Can implement in 1 day
- [ ] project_manager (strategic alignment) - Meets US-035 goals
- [ ] User (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 1 day (9 hours) - Ready for code_developer!
