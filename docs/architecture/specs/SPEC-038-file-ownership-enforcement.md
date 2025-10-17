# SPEC-038: File Ownership Enforcement in generator Agent

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: US-038 (ROADMAP), CFR-000 (Prevent File Conflicts), US-035 (Singleton Enforcement)

**Related ADRs**: ADR-003 (Simplification-First Approach)

**Assigned To**: code_developer

**Depends On**: US-035 must be complete first

---

## Executive Summary

This specification describes a lightweight file ownership enforcement system that prevents agents from modifying files they don't own. Using a simple ownership registry and Read/Write/Edit tool wrappers in generator, we automatically delegate file operations to the correct owner agent, preventing conflicts while maintaining smooth collaboration.

---

## Problem Statement

### Current Situation

File ownership is documented but not enforced:
- Ownership rules in `.claude/CLAUDE.md` (honor system)
- Agents manually check ownership before writing
- Violations can slip through code review
- No automatic delegation when violations occur
- Risk of file conflicts if two agents write same file

**Proof**: Nothing prevents project_manager from editing `.claude/CLAUDE.md` (owned by code_developer)

### Goal

Enforce file ownership automatically:
- generator intercepts ALL file operations (Read, Write, Edit tools)
- Checks ownership before allowing write operations
- Auto-delegates to owner agent when violation detected
- Captures traces for learning (reflector can analyze patterns)
- ZERO ownership violations reach execution

### Non-Goals

- NOT preventing read operations (reading is always safe)
- NOT building complex permission system (simple owner-based model)
- NOT synchronizing across machines (single-machine enforcement)
- NOT implementing role-based access control (simple ownership matrix)

---

## Requirements

### Functional Requirements

1. **FR-1**: generator intercepts Read, Write, Edit tool calls before execution
2. **FR-2**: generator checks FileOwnership registry for write operations
3. **FR-3**: If agent owns file: Execute directly, capture trace
4. **FR-4**: If agent doesn't own file: Auto-delegate to owner, return result
5. **FR-5**: Delegation traces captured for reflector analysis

### Non-Functional Requirements

1. **NFR-1**: Performance: Ownership check < 1ms (file path lookup)
2. **NFR-2**: Reliability: 100% accurate ownership enforcement
3. **NFR-3**: Transparency: Clear logs when delegation occurs
4. **NFR-4**: Observability: All delegations tracked in Langfuse

### Constraints

- Must integrate with generator agent (ACE framework)
- Must use existing ownership matrix (CLAUDE.md)
- Must not break existing agent workflows
- Must work with SPEC-035 singleton enforcement

---

## Proposed Solution

### High-Level Approach

**Tool Interception in generator**: Before executing Read/Write/Edit, generator checks ownership. If violation, auto-delegate to owner.

**Why This is Simple**:
- Simple ownership lookup (path → owner mapping)
- No complex permission system
- Reuses generator's existing tool interception
- Minimal code (~120 lines total)

### Architecture Diagram

```
Agent calls Write("/path/to/file.md", content)
    ↓
generator intercepts tool call
    ↓
generator checks ownership:
  Is this a WRITE operation? (Read is always OK)
    ↓ YES
  Does calling agent OWN this file?
    ↓ NO (violation detected!)
  Look up owner: /path/to/file.md → owner: "code_developer"
    ↓
generator auto-delegates:
  "Delegating file write to code_developer (owns /path/to/)"
    ↓
generator invokes code_developer.write("/path/to/file.md", content)
    ↓
code_developer executes write
    ↓
generator captures delegation trace
    ↓
generator returns success to original agent
    ↓
Original agent continues (unaware of delegation)
```

### Ownership Matrix

**File Ownership** (from `.claude/CLAUDE.md`):

| Path | Owner | Write Access |
|------|-------|--------------|
| `.claude/` | code_developer | EXCLUSIVE |
| `coffee_maker/` | code_developer | EXCLUSIVE |
| `tests/` | code_developer | EXCLUSIVE |
| `scripts/` | code_developer | EXCLUSIVE |
| `docs/roadmap/` | project_manager | EXCLUSIVE |
| `docs/architecture/` | architect | EXCLUSIVE |
| `docs/generator/` | generator | EXCLUSIVE |
| `docs/reflector/` | reflector | EXCLUSIVE |
| `docs/curator/` | curator | EXCLUSIVE |
| `docs/*.md` (top-level) | project_manager | EXCLUSIVE |
| `pyproject.toml` | architect | EXCLUSIVE (requires user approval) |
| `poetry.lock` | architect | EXCLUSIVE |

**Read Access**: ALL agents can read ALL files (safe)

---

## Detailed Design

### Component 1: Ownership Registry

**File**: `coffee_maker/autonomous/ownership_registry.py` (~60 lines)

**Purpose**: Map file paths to owning agents

**Interface**:
```python
"""
File ownership registry for enforcement.
"""

from pathlib import Path
from typing import Optional

# Ownership mapping (directory-based)
FILE_OWNERSHIP = {
    ".claude": "code_developer",
    "coffee_maker": "code_developer",
    "tests": "code_developer",
    "scripts": "code_developer",
    "docs/roadmap": "project_manager",
    "docs/architecture": "architect",
    "docs/generator": "generator",
    "docs/reflector": "reflector",
    "docs/curator": "curator",
    "pyproject.toml": "architect",
    "poetry.lock": "architect",
}

def get_file_owner(file_path: str) -> Optional[str]:
    """
    Get owner of file based on path.

    Args:
        file_path: Path to file (absolute or relative)

    Returns:
        Owner agent type (e.g., "code_developer") or None if no specific owner

    Example:
        >>> get_file_owner(".claude/CLAUDE.md")
        'code_developer'
        >>> get_file_owner("docs/roadmap/ROADMAP.md")
        'project_manager'
        >>> get_file_owner("README.md")
        'project_manager'  # Top-level docs
    """
    path = Path(file_path)

    # Normalize path (handle absolute, relative, symlinks)
    try:
        normalized = path.resolve()
    except FileNotFoundError:
        # File doesn't exist yet (creation), use path as-is
        normalized = path

    # Convert to relative path from project root
    try:
        from coffee_maker.utils.project_root import get_project_root
        project_root = get_project_root()
        relative = normalized.relative_to(project_root)
    except (ValueError, FileNotFoundError):
        # Path outside project (shouldn't happen)
        relative = path

    relative_str = str(relative)

    # Check direct ownership (exact file match)
    if relative_str in FILE_OWNERSHIP:
        return FILE_OWNERSHIP[relative_str]

    # Check directory ownership (parent directory match)
    for owned_path, owner in FILE_OWNERSHIP.items():
        if relative_str.startswith(owned_path + "/"):
            return owner

    # Special case: Top-level .md files → project_manager
    if relative.parent == Path(".") and relative.suffix == ".md":
        return "project_manager"

    # No specific owner (shared files)
    return None


def check_ownership_violation(agent_type: str, file_path: str, operation: str) -> Optional[str]:
    """
    Check if agent can perform operation on file.

    Args:
        agent_type: Type of agent (e.g., "code_developer")
        file_path: Path to file
        operation: Operation type ("read", "write", "edit")

    Returns:
        None if allowed, or owner agent type if violation

    Example:
        >>> check_ownership_violation("project_manager", ".claude/CLAUDE.md", "write")
        'code_developer'  # Violation! project_manager can't write code_developer's files
        >>> check_ownership_violation("code_developer", ".claude/CLAUDE.md", "write")
        None  # OK, code_developer owns .claude/
    """
    # Read operations always allowed
    if operation == "read":
        return None

    # Write/Edit operations: Check ownership
    owner = get_file_owner(file_path)

    # No specific owner → anyone can write (shared files)
    if owner is None:
        return None

    # Agent owns file → allowed
    if agent_type == owner:
        return None

    # Violation: Agent doesn't own file
    return owner
```

**Implementation Notes**:
- Simple dictionary lookup (O(1) for exact paths)
- Directory prefix matching (O(n) where n = ownership rules, ~10)
- Handles absolute, relative, symlinks
- Special case for top-level .md files

### Component 2: Tool Interception in generator

**File**: `coffee_maker/autonomous/ace/generator_enforcement.py` (~60 lines, NEW)

**Purpose**: Intercept tool calls and enforce ownership

**Interface**:
```python
"""
Tool interception for ownership enforcement in generator.
"""

from coffee_maker.autonomous.ownership_registry import check_ownership_violation
from coffee_maker.langfuse_observe import observe
import logging

logger = logging.getLogger(__name__)

@observe(name="enforce_ownership")
def intercept_tool_call(agent_type: str, tool_name: str, tool_args: dict) -> dict:
    """
    Intercept tool call and enforce ownership.

    Args:
        agent_type: Type of calling agent
        tool_name: Tool being called ("Read", "Write", "Edit")
        tool_args: Tool arguments (contains file_path)

    Returns:
        Modified tool args if delegation needed, else original args

    Example:
        >>> args = intercept_tool_call("project_manager", "Write", {"file_path": ".claude/CLAUDE.md", "content": "..."})
        # Returns delegated args for code_developer
    """
    # Only intercept file operations
    if tool_name not in ["Read", "Write", "Edit"]:
        return tool_args

    file_path = tool_args.get("file_path")
    if not file_path:
        return tool_args

    # Determine operation type
    operation = "read" if tool_name == "Read" else "write"

    # Check for ownership violation
    owner = check_ownership_violation(agent_type, file_path, operation)

    if owner is None:
        # No violation → execute directly
        logger.info(f"✅ {agent_type} accessing {file_path} ({operation}) - ALLOWED")
        return tool_args

    # Violation detected → delegate to owner
    logger.warning(
        f"🚫 {agent_type} attempted {operation} on {file_path} "
        f"(owned by {owner}) - DELEGATING"
    )

    # Modify tool args to indicate delegation
    tool_args["_delegated_to"] = owner
    tool_args["_original_agent"] = agent_type

    return tool_args


def execute_with_delegation(tool_name: str, tool_args: dict):
    """
    Execute tool with delegation if needed.

    Args:
        tool_name: Tool to execute
        tool_args: Tool arguments (may contain _delegated_to)

    Returns:
        Tool result

    Example:
        >>> result = execute_with_delegation("Write", {"file_path": "...", "_delegated_to": "code_developer"})
    """
    delegated_to = tool_args.pop("_delegated_to", None)
    original_agent = tool_args.pop("_original_agent", None)

    if delegated_to:
        # Delegation needed
        logger.info(f"⚙️ Delegating {tool_name} to {delegated_to}")

        # Invoke owner agent
        from coffee_maker.autonomous.agent_delegation import delegate_tool_call
        result = delegate_tool_call(delegated_to, tool_name, tool_args)

        # Capture delegation trace
        from coffee_maker.autonomous.ace.generator import capture_delegation_trace
        capture_delegation_trace(
            original_agent=original_agent,
            delegated_to=delegated_to,
            tool=tool_name,
            file_path=tool_args["file_path"],
            result=result
        )

        return result
    else:
        # Direct execution
        from coffee_maker.tools import execute_tool
        return execute_tool(tool_name, tool_args)
```

**Implementation Notes**:
- Intercepts Read/Write/Edit before execution
- Checks ownership via registry
- Modifies tool args to indicate delegation
- Captures delegation traces for reflector

### Component 3: Integration with generator Agent

**File**: `.claude/agents/generator.md` (existing, add enforcement section)

**Add to generator's responsibilities**:
```markdown
## File Ownership Enforcement

Before executing any Read/Write/Edit tool call:

1. Intercept tool call
2. Check ownership: `check_ownership_violation(agent_type, file_path, operation)`
3. If violation: Auto-delegate to owner
4. Capture delegation trace (for reflector learning)
5. Return result to original agent

**Example Delegation**:
```
project_manager → Write(.claude/CLAUDE.md)
  ↓
generator detects violation (.claude/ owned by code_developer)
  ↓
generator delegates: code_developer.Write(.claude/CLAUDE.md)
  ↓
code_developer executes write
  ↓
generator returns success to project_manager
```

**Traces Captured**:
- Original agent type
- Delegated-to agent type
- File path
- Operation type
- Timestamp
- Result (success/failure)
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_ownership_registry.py` (~100 lines, 12 tests)

**Test Cases**:
1. `test_get_file_owner_code_developer()` - .claude/, coffee_maker/ owned
2. `test_get_file_owner_project_manager()` - docs/roadmap/ owned
3. `test_get_file_owner_architect()` - docs/architecture/, pyproject.toml owned
4. `test_get_file_owner_top_level_md()` - README.md → project_manager
5. `test_get_file_owner_no_owner()` - Shared files (data/) → None
6. `test_check_violation_read_always_ok()` - Read never violates
7. `test_check_violation_owner_writes_ok()` - Owner can write
8. `test_check_violation_non_owner_blocked()` - Non-owner blocked
9. `test_check_violation_no_owner_files()` - Anyone can write shared files
10. `test_path_normalization()` - Absolute, relative, symlinks work
11. `test_nonexistent_file_ownership()` - File creation uses path-based ownership
12. `test_nested_directory_ownership()` - .claude/agents/ → code_developer

### Integration Tests

**File**: `tests/integration/test_ownership_enforcement.py` (~80 lines, 6 tests)

**Test Cases**:
1. `test_generator_intercepts_write()` - generator intercepts Write tool
2. `test_delegation_to_code_developer()` - project_manager → code_developer delegation
3. `test_delegation_to_project_manager()` - code_developer → project_manager delegation
4. `test_delegation_to_architect()` - code_developer → architect delegation (pyproject.toml)
5. `test_no_delegation_when_owner()` - code_developer writes .claude/ (direct)
6. `test_read_never_delegates()` - Any agent can read any file

### Manual Testing

```bash
# Test 1: Direct write (owner)
# Start daemon (code_developer)
poetry run code-developer

# code_developer writes .claude/CLAUDE.md → Should succeed (owns .claude/)
# Check logs: "✅ code_developer accessing .claude/CLAUDE.md (write) - ALLOWED"

# Test 2: Delegated write (non-owner)
# project_manager tries to write .claude/CLAUDE.md → Should delegate to code_developer
# Check logs: "🚫 project_manager attempted write on .claude/CLAUDE.md (owned by code_developer) - DELEGATING"
# Check logs: "⚙️ Delegating Write to code_developer"

# Test 3: Read always works
# Any agent reads any file → Should always succeed (no delegation)
# Check logs: "✅ {agent} accessing {file} (read) - ALLOWED"

# Test 4: Shared files
# Any agent writes data/some_file.json → Should succeed (no owner)
# Check logs: "✅ {agent} accessing data/some_file.json (write) - ALLOWED"
```

---

## Rollout Plan

### Phase 1: Ownership Registry (Day 1 - 3 hours)

**Goal**: Create ownership lookup system

**Tasks**:
1. Create `ownership_registry.py` (60 lines)
2. Implement `get_file_owner()` and `check_ownership_violation()`
3. Write unit tests (100 lines)
4. Verify ownership matrix matches CLAUDE.md

**Success Criteria**:
- All 12 unit tests pass
- Ownership lookups correct
- Path normalization works

### Phase 2: generator Integration (Day 2 - 4 hours)

**Goal**: Intercept tool calls in generator

**Tasks**:
1. Create `generator_enforcement.py` (60 lines)
2. Implement `intercept_tool_call()` and `execute_with_delegation()`
3. Update generator agent to use interception
4. Write integration tests (80 lines)
5. Test with real agents

**Success Criteria**:
- generator intercepts Read/Write/Edit
- Ownership checks work
- Delegation succeeds
- All integration tests pass

### Phase 3: Trace Capture (Day 2 - 2 hours)

**Goal**: Capture delegation traces for reflector

**Tasks**:
1. Implement `capture_delegation_trace()` in generator
2. Save traces to `data/generator/traces/delegations/`
3. Test trace format (reflector can parse)
4. Verify traces contain all needed info

**Success Criteria**:
- Delegation traces saved
- Traces contain: original_agent, delegated_to, file_path, operation, timestamp
- reflector can parse traces

---

## Why This is Simple (vs Strategic Spec)

**Strategic Spec** (US-038 in ROADMAP):
- Mentioned "FileOwnership registry" (sounds like complex class)
- "Automatic delegation mechanism" (sounds like heavy infrastructure)
- Integration with all agents (sounds like widespread changes)
- ~2-3 days estimate

**This Simplified Spec**:
- **Simple dictionary lookup** (not complex registry class)
- **Tool interception in generator** (centralized, not per-agent)
- **~120 lines total** (not 500+ lines)
- **Minimal agent changes** (only generator intercepts, others unchanged)
- **Same 2-3 days estimate** (but simpler implementation)

**What We REUSE**:
- Existing generator tool interception (ACE framework)
- Existing ownership matrix (CLAUDE.md)
- Existing delegation mechanisms (if any)
- Existing trace capture (generator already does this)
- SPEC-035 singleton enforcement (builds on it)

**Complexity Reduction**:
- **No complex registry class** (simple dict + 2 functions)
- **No per-agent integration** (only generator intercepts)
- **No distributed locking** (single-machine enforcement)
- **No permission system** (simple owner-based model)

**Result**: 70% less code, same safety guarantee

---

## Integration with US-035 (Singleton)

**Together, US-035 + US-038 provide complete CFR-000 enforcement**:

| Conflict Type | Prevention Mechanism | Spec |
|---------------|---------------------|------|
| Same agent, multiple instances | Singleton enforcement | US-035 (SPEC-035) |
| Different agents, same file | Ownership enforcement | US-038 (this spec) |
| Read operations | Always allowed | This spec (reads are safe) |

**Example**:
```
Scenario 1: Two code_developer instances
→ BLOCKED by SPEC-035 (singleton prevents second instance)

Scenario 2: project_manager writes .claude/CLAUDE.md
→ DELEGATED by this spec (ownership enforcement)

Scenario 3: assistant reads any file
→ ALLOWED (reads are always safe)

Result: ZERO file conflicts possible! 🎉
```

---

## Future Enhancements

**NOT in this spec** (deferred):
1. **Role-based permissions** → When complex permission model needed
2. **Distributed enforcement** → When multi-machine deployment
3. **Temporary ownership transfer** → When agent collaboration workflows mature
4. **Ownership history** → When audit trail needed
5. **Permission override** → Emergency access (with user approval)

---

## References

- US-038: Implement File Ownership Enforcement in generator Agent (ROADMAP)
- US-035: Implement Singleton Agent Enforcement (dependency)
- CFR-000: Prevent File Conflicts (master requirement)
- ADR-003: Simplification-First Approach
- `.claude/CLAUDE.md` - File ownership matrix

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created (Draft) | architect |

---

## Approval

- [ ] architect (author) - Ready for review
- [ ] code_developer (implementer) - Can implement in 2-3 days
- [ ] project_manager (strategic alignment) - Meets US-038 goals
- [ ] User (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 2-3 days (9 hours total)

**Phases**:
- Phase 1: Ownership Registry (3 hours)
- Phase 2: generator Integration (4 hours)
- Phase 3: Trace Capture (2 hours)

**Depends On**: US-035 (Singleton Enforcement) must be complete first

**Result**: Zero file conflicts, automatic delegation, seamless collaboration! 🚀
