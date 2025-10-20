# US-038: File Ownership Enforcement - Practical Guide

**Quick Reference for Developers and Agents**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [File Ownership Matrix](#file-ownership-matrix)
3. [How It Works](#how-it-works)
4. [Common Scenarios](#common-scenarios)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Quick Start

### For Agents

```python
from coffee_maker.autonomous.ace.file_tools import WriteTool, ReadTool
from coffee_maker.autonomous.agent_registry import AgentType

# 1. Create tools for your agent
write_tool = WriteTool(AgentType.CODE_DEVELOPER)
read_tool = ReadTool(AgentType.CODE_DEVELOPER)

# 2. Read any file (always allowed)
content = read_tool.read_file(".claude/CLAUDE.md")

# 3. Write to owned file
write_tool.write_file("coffee_maker/test.py", "# code")  # ✅ Allowed

# 4. Write to non-owned file (auto-delegated)
write_tool.write_file("docs/roadmap/ROADMAP.md", "# roadmap")  # ⚠️ Delegated to project_manager
```

### Key Concepts

1. **Read Operations**: Always allowed for all agents (no restrictions)
2. **Write Operations**: Only allowed for file owner (auto-delegated if violated)
3. **Automatic Delegation**: Generator handles violations transparently
4. **No Manual Checking**: Agents don't need to check ownership manually

---

## File Ownership Matrix

### Complete Reference

| Files/Directories | Owner | Purpose |
|-------------------|-------|---------|
| `.claude/**` | `code_developer` | All Claude Code configurations |
| `.claude/CLAUDE.md` | `code_developer` | Technical setup guide |
| `.claude/agents/**` | `code_developer` | Agent definitions |
| `.claude/commands/**` | `code_developer` | Centralized prompts |
| `.claude/mcp/**` | `code_developer` | MCP server configurations |
| `coffee_maker/**` | `code_developer` | All implementation code |
| `tests/**` | `code_developer` | All test code |
| `scripts/**` | `code_developer` | Utility scripts |
| `.pre-commit-config.yaml` | `code_developer` | Pre-commit hooks |
| `docs/*.md` | `project_manager` | Top-level docs (README, etc.) |
| `docs/roadmap/**` | `project_manager` | ROADMAP and strategic planning |
| `docs/templates/**` | `project_manager` | Documentation templates |
| `docs/tutorials/**` | `project_manager` | Tutorial content |
| `docs/code-searcher/**` | `project_manager` | Code analysis documentation |
| `docs/user_interpret/**` | `project_manager` | user_interpret meta-docs |
| `docs/code_developer/**` | `project_manager` | code_developer meta-docs |
| `docs/architecture/**` | `architect` | Technical specs, ADRs, guidelines |
| `docs/architecture/specs/**` | `architect` | Technical specifications |
| `docs/architecture/decisions/**` | `architect` | Architectural Decision Records |
| `docs/architecture/guidelines/**` | `architect` | Implementation guidelines |
| `docs/architecture/pocs/**` | `architect` | Proof of Concepts |
| `pyproject.toml` | `architect` | Dependency management |
| `poetry.lock` | `architect` | Dependency lock file |
| `docs/generator/**` | `generator` | Execution traces |
| `docs/reflector/**` | `reflector` | Insights and delta items |
| `docs/curator/**` | `curator` | Playbooks and curation |
| `data/user_interpret/**` | `user_listener` | Operational data |

### Visual Ownership Map

```
MonolithicCoffeeMakerAgent/
├── .claude/                         → code_developer
│   ├── CLAUDE.md                    → code_developer
│   ├── agents/                      → code_developer
│   ├── commands/                    → code_developer
│   └── mcp/                         → code_developer
├── coffee_maker/                    → code_developer
│   ├── cli/                         → code_developer
│   ├── autonomous/                  → code_developer
│   └── ...                          → code_developer
├── tests/                           → code_developer
├── scripts/                         → code_developer
├── docs/
│   ├── README.md                    → project_manager
│   ├── WORKFLOWS.md                 → project_manager
│   ├── roadmap/                     → project_manager
│   │   ├── ROADMAP.md               → project_manager
│   │   └── TEAM_COLLABORATION.md    → project_manager
│   ├── architecture/                → architect
│   │   ├── specs/                   → architect
│   │   ├── decisions/               → architect
│   │   ├── guidelines/              → architect
│   │   └── pocs/                    → architect
│   ├── generator/                   → generator
│   ├── reflector/                   → reflector
│   └── curator/                     → curator
├── pyproject.toml                   → architect
├── poetry.lock                      → architect
└── .pre-commit-config.yaml          → code_developer
```

---

## How It Works

### 1. Agent Attempts File Operation

```python
# assistant tries to write to code_developer's file
write_tool = WriteTool(AgentType.ASSISTANT)
write_tool.write_file("coffee_maker/cli/test.py", "# code")
```

### 2. WriteTool Intercepts Operation

```python
# WriteTool calls generator.intercept_file_operation()
result = self.generator.intercept_file_operation(
    agent_type=AgentType.ASSISTANT,
    file_path="coffee_maker/cli/test.py",
    operation="write",
    content="# code"
)
```

### 3. Generator Checks Ownership

```python
# Generator queries FileOwnership registry
owner = FileOwnership.get_owner("coffee_maker/cli/test.py")
# Returns: AgentType.CODE_DEVELOPER

# Compare: ASSISTANT ≠ CODE_DEVELOPER
# → Ownership violation detected!
```

### 4. Generator Auto-Delegates

```python
# Generator creates delegation trace
trace = DelegationTrace(
    requesting_agent=AgentType.ASSISTANT,
    owner_agent=AgentType.CODE_DEVELOPER,
    file_path="coffee_maker/cli/test.py",
    operation=FileOperationType.WRITE,
    ...
)

# Logs to database
generator._log_trace_to_database(...)

# Returns result with delegation info
return OperationResult(
    success=True,
    delegated=True,
    delegated_to=AgentType.CODE_DEVELOPER,
    trace_id="delegation_20251020_123456"
)
```

### 5. WriteTool Returns Result

```python
# WriteTool logs delegation and returns success
if result.delegated:
    logger.info(f"Write delegated to {result.delegated_to.value}")

return result.success  # True
```

### 6. Operation Completes Transparently

```python
# assistant receives success result
# Doesn't need to know delegation occurred
# File operation handled by correct owner
```

---

## Common Scenarios

### Scenario 1: Code Developer Modifying Implementation

```python
# ✅ ALLOWED - code_developer owns coffee_maker/**
write_tool = WriteTool(AgentType.CODE_DEVELOPER)
write_tool.write_file(
    "coffee_maker/cli/roadmap_cli.py",
    "from coffee_maker.cli.console_ui import *\n..."
)
# Result: Direct write (no delegation)
```

### Scenario 2: Project Manager Updating ROADMAP

```python
# ✅ ALLOWED - project_manager owns docs/roadmap/**
write_tool = WriteTool(AgentType.PROJECT_MANAGER)
write_tool.write_file(
    "docs/roadmap/ROADMAP.md",
    "## US-039: Next Priority\n..."
)
# Result: Direct write (no delegation)
```

### Scenario 3: Architect Managing Dependencies

```python
# ✅ ALLOWED - architect owns pyproject.toml
write_tool = WriteTool(AgentType.ARCHITECT)
write_tool.write_file(
    "pyproject.toml",
    "[tool.poetry]\nname = 'coffee_maker'\n..."
)
# Result: Direct write (no delegation)
```

### Scenario 4: Assistant Writing to Code Developer File

```python
# ⚠️ DELEGATED - assistant does NOT own coffee_maker/**
write_tool = WriteTool(AgentType.ASSISTANT)
write_tool.write_file(
    "coffee_maker/autonomous/test.py",
    "# test code"
)
# Result: Delegated to code_developer
# Log: "Write delegated: coffee_maker/autonomous/test.py → code_developer"
```

### Scenario 5: Project Manager Writing to Architect File

```python
# ⚠️ DELEGATED - project_manager does NOT own docs/architecture/**
write_tool = WriteTool(AgentType.PROJECT_MANAGER)
write_tool.write_file(
    "docs/architecture/specs/SPEC-042-new-feature.md",
    "# Technical Specification\n..."
)
# Result: Delegated to architect
# Log: "Write delegated: docs/architecture/specs/SPEC-042-new-feature.md → architect"
```

### Scenario 6: Any Agent Reading Any File

```python
# ✅ ALWAYS ALLOWED - read operations unrestricted
read_tool = ReadTool(AgentType.ASSISTANT)

# Can read code_developer files
content = read_tool.read_file("coffee_maker/cli/roadmap_cli.py")

# Can read architect files
content = read_tool.read_file("pyproject.toml")

# Can read project_manager files
content = read_tool.read_file("docs/roadmap/ROADMAP.md")

# All allowed - no ownership check for reads
```

### Scenario 7: Checking Ownership Before Writing

```python
# Check if agent owns file before attempting write
write_tool = WriteTool(AgentType.ASSISTANT)

if write_tool.can_write("docs/roadmap/ROADMAP.md"):
    # Won't execute - assistant doesn't own it
    write_tool.write_file("docs/roadmap/ROADMAP.md", "# Updated")
else:
    print("⚠️ Cannot write - will be delegated to project_manager")
    # Or: Delegate explicitly to project_manager
```

### Scenario 8: Getting Allowed Paths for Agent

```python
# Get list of files/directories agent can write to
write_tool = WriteTool(AgentType.CODE_DEVELOPER)
allowed = write_tool.get_allowed_paths()

print("code_developer can write to:")
for path in allowed:
    print(f"  ✅ {path}")

# Output:
#   ✅ .claude/**
#   ✅ coffee_maker/**
#   ✅ tests/**
#   ✅ scripts/**
#   ✅ .pre-commit-config.yaml
```

---

## API Reference

### WriteTool

```python
from coffee_maker.autonomous.ace.file_tools import WriteTool

# Initialize for agent
write_tool = WriteTool(AgentType.CODE_DEVELOPER)
```

#### Methods

**`write_file(file_path: str, content: str, raise_on_violation: bool = False) -> bool`**

Write content to a file with ownership enforcement.

```python
# Normal usage (auto-delegate on violation)
success = write_tool.write_file("coffee_maker/test.py", "# code")

# Raise exception on violation (instead of delegating)
try:
    write_tool.write_file(
        "docs/roadmap/ROADMAP.md",
        "# roadmap",
        raise_on_violation=True
    )
except OwnershipViolationError as e:
    print(f"Violation: {e.agent.value} → {e.owner.value}")
```

**`edit_file(file_path: str, old_content: str, new_content: str, raise_on_violation: bool = False) -> bool`**

Edit content in a file with ownership enforcement.

```python
success = write_tool.edit_file(
    "coffee_maker/test.py",
    old_content="# old code",
    new_content="# new code"
)
```

**`delete_file(file_path: str, raise_on_violation: bool = False) -> bool`**

Delete a file with ownership enforcement.

```python
success = write_tool.delete_file("coffee_maker/old_file.py")
```

**`can_write(file_path: str) -> bool`**

Check if agent can write to file without delegation.

```python
if write_tool.can_write("coffee_maker/test.py"):
    write_tool.write_file("coffee_maker/test.py", "# code")
```

**`get_allowed_paths() -> List[str]`**

Get list of path patterns agent can write to.

```python
allowed = write_tool.get_allowed_paths()
print(f"Can write to: {allowed}")
```

---

### ReadTool

```python
from coffee_maker.autonomous.ace.file_tools import ReadTool

# Initialize for agent
read_tool = ReadTool(AgentType.ASSISTANT)
```

#### Methods

**`read_file(file_path: str) -> Optional[str]`**

Read content from a file (always allowed).

```python
content = read_tool.read_file(".claude/CLAUDE.md")
if content:
    print(content)
```

**`file_exists(file_path: str) -> bool`**

Check if a file exists.

```python
if read_tool.file_exists("coffee_maker/test.py"):
    content = read_tool.read_file("coffee_maker/test.py")
```

**`list_files(directory: str, pattern: str = "*") -> List[str]`**

List files in a directory matching pattern.

```python
# List all Python files in coffee_maker/
files = read_tool.list_files("coffee_maker", "*.py")
for file in files:
    print(file)
```

---

### FileOwnership (Advanced)

```python
from coffee_maker.autonomous.ace.file_ownership import FileOwnership

# Get owner of a file
owner = FileOwnership.get_owner("coffee_maker/test.py")
print(f"Owner: {owner.value}")  # "code_developer"

# Check if agent owns file
owns = FileOwnership.check_ownership(
    agent=AgentType.CODE_DEVELOPER,
    file_path="coffee_maker/test.py"
)
print(f"Owns: {owns}")  # True

# Get allowed paths for agent
paths = FileOwnership.get_allowed_paths(AgentType.CODE_DEVELOPER)
print(f"Allowed: {paths}")

# Clear ownership cache (testing)
FileOwnership.clear_cache()

# Validate ownership rules (no conflicts)
valid = FileOwnership.validate_rules()
print(f"Rules valid: {valid}")  # True
```

---

### Generator (Advanced)

```python
from coffee_maker.autonomous.ace.generator import Generator, get_generator

# Get singleton instance
generator = get_generator()

# Intercept file operation
result = generator.intercept_file_operation(
    agent_type=AgentType.ASSISTANT,
    file_path="coffee_maker/test.py",
    operation="write",
    content="# code"
)

print(f"Success: {result.success}")
print(f"Delegated: {result.delegated}")
if result.delegated:
    print(f"Delegated to: {result.delegated_to.value}")

# Get delegation statistics
stats = generator.get_delegation_stats()
print(f"Total delegations: {stats['total_delegations']}")
print(f"By agent: {stats['delegations_by_requesting_agent']}")

# Get delegation traces
traces = generator.get_delegation_traces(
    agent=AgentType.ASSISTANT,
    hours=24
)
for trace in traces:
    print(f"{trace.timestamp}: {trace.file_path} → {trace.owner_agent.value}")
```

---

## Troubleshooting

### Issue: OwnershipUnclearError

**Symptom**: Exception raised when trying to determine file owner

```python
OwnershipUnclearError: Cannot determine owner for: my_new_file.txt
```

**Cause**: File not covered by ownership rules in `file_ownership.py`

**Solution**: Add ownership rule to `OWNERSHIP_RULES`

```python
# In coffee_maker/autonomous/ace/file_ownership.py
OWNERSHIP_RULES = {
    # ... existing rules ...
    "my_new_directory/**": AgentType.CODE_DEVELOPER,
}
```

---

### Issue: Unexpected Delegation

**Symptom**: File operation delegated when you expected direct write

```python
# Expected: Direct write
# Actual: Delegated to code_developer
write_tool.write_file("scripts/test.sh", "#!/bin/bash")
```

**Diagnosis**: Check ownership

```python
owner = FileOwnership.get_owner("scripts/test.sh")
print(f"Owner: {owner.value}")  # "code_developer"

# Check what patterns agent owns
allowed = write_tool.get_allowed_paths()
print(f"Allowed patterns: {allowed}")
```

**Solution**: Either:
1. Use correct agent (code_developer for scripts/)
2. Or: Accept delegation (automatic)

---

### Issue: Delegation Not Working

**Symptom**: Write succeeds without delegation when violation expected

**Diagnosis**: Check if ownership check performed

```python
# Verify ownership enforcement active
generator = get_generator()
result = generator.intercept_file_operation(
    agent_type=AgentType.ASSISTANT,
    file_path="coffee_maker/test.py",
    operation="write",
    content="# code"
)

print(f"Delegated: {result.delegated}")  # Should be True
```

**Possible Causes**:
1. Read operation (no ownership check)
2. Ownership unclear (fail-open policy)
3. Agent actually owns file

---

### Issue: Performance Slow

**Symptom**: File operations take longer than expected

**Diagnosis**: Check if caching working

```python
# Clear cache and time lookups
FileOwnership.clear_cache()

import time

# Cold cache
start = time.perf_counter()
FileOwnership.get_owner("coffee_maker/test.py")
cold = time.perf_counter() - start

# Warm cache
start = time.perf_counter()
FileOwnership.get_owner("coffee_maker/test.py")
warm = time.perf_counter() - start

print(f"Cold: {cold*1000:.2f}ms, Warm: {warm*1000:.2f}ms")
# Expected: Cold ~1-2ms, Warm ~0.01ms
```

**Solution**: Ensure ownership cache not being cleared unnecessarily

---

## Best Practices

### 1. Use Appropriate Agent for File

**❌ Don't**: Try to write to files your agent doesn't own

```python
# assistant writing to code_developer file
write_tool = WriteTool(AgentType.ASSISTANT)
write_tool.write_file("coffee_maker/test.py", "# code")  # Delegated
```

**✅ Do**: Use correct agent for file

```python
# code_developer writing to own file
write_tool = WriteTool(AgentType.CODE_DEVELOPER)
write_tool.write_file("coffee_maker/test.py", "# code")  # Direct
```

---

### 2. Check Ownership Before Batch Operations

**❌ Don't**: Blindly write to many files

```python
for file in files:
    write_tool.write_file(file, content)  # May delegate many times
```

**✅ Do**: Check ownership first

```python
# Group files by owner
by_owner = {}
for file in files:
    owner = FileOwnership.get_owner(file)
    by_owner.setdefault(owner, []).append(file)

# Process each group with appropriate agent
for owner, owner_files in by_owner.items():
    write_tool = WriteTool(owner)
    for file in owner_files:
        write_tool.write_file(file, content)
```

---

### 3. Read Operations Don't Need Ownership Check

**❌ Don't**: Check ownership before reading

```python
# Unnecessary
if write_tool.can_write(file_path):
    content = read_tool.read_file(file_path)
```

**✅ Do**: Just read (always allowed)

```python
# All agents can read any file
content = read_tool.read_file(file_path)
```

---

### 4. Use `raise_on_violation` for Error Handling

**❌ Don't**: Rely on delegation when you need explicit control

```python
write_tool.write_file(file_path, content)  # Silently delegated
```

**✅ Do**: Raise exception if delegation not acceptable

```python
try:
    write_tool.write_file(file_path, content, raise_on_violation=True)
except OwnershipViolationError as e:
    logger.error(f"Cannot write to {file_path}: owned by {e.owner.value}")
    # Handle error explicitly
```

---

### 5. Monitor Delegation Patterns

**✅ Periodically check delegation statistics**:

```python
# Get delegation statistics
generator = get_generator()
stats = generator.get_delegation_stats()

# Alert if high delegation rate
for agent, count in stats['delegations_by_requesting_agent'].items():
    if count > 50:
        logger.warning(
            f"⚠️ {agent} has {count} ownership violations - "
            f"consider reviewing agent design"
        )
```

---

### 6. Clear Ownership Cache After Rule Changes

**✅ After modifying OWNERSHIP_RULES**:

```python
# After changing file_ownership.py
FileOwnership.clear_cache()

# Verify rules still valid
assert FileOwnership.validate_rules(), "Ownership rules have conflicts!"
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════════════╗
║                    FILE OWNERSHIP QUICK REFERENCE                 ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  READ OPERATIONS:  Always allowed (all agents)                    ║
║  WRITE OPERATIONS: Only allowed for owner (auto-delegated)        ║
║                                                                   ║
║  KEY OWNERS:                                                      ║
║    .claude/**           → code_developer                          ║
║    coffee_maker/**      → code_developer                          ║
║    tests/**             → code_developer                          ║
║    docs/roadmap/**      → project_manager                         ║
║    docs/architecture/** → architect                               ║
║    pyproject.toml       → architect                               ║
║                                                                   ║
║  TOOLS:                                                           ║
║    WriteTool(agent)     - Write with enforcement                  ║
║    ReadTool(agent)      - Read (unrestricted)                     ║
║                                                                   ║
║  METHODS:                                                         ║
║    write_file(path, content)                                      ║
║    edit_file(path, old, new)                                      ║
║    delete_file(path)                                              ║
║    read_file(path)                                                ║
║    can_write(path)                                                ║
║    get_allowed_paths()                                            ║
║                                                                   ║
║  DELEGATION:                                                      ║
║    Automatic - Generator handles transparently                    ║
║    Logged - All delegations traced for analysis                   ║
║    Transparent - Requesting agent sees success                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Related Documentation

- [US_038_TECHNICAL_SPEC.md](architecture/user_stories/US_038_TECHNICAL_SPEC.md) - Complete technical specification
- [US_038_DELEGATION_PROTOCOL.md](US_038_DELEGATION_PROTOCOL.md) - Delegation mechanism details
- [AGENT_OWNERSHIP.md](AGENT_OWNERSHIP.md) - Agent boundaries and ownership matrix
- [CRITICAL_FUNCTIONAL_REQUIREMENTS.md](roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md) - CFR-001: Document Ownership
- [ROADMAP.md](roadmap/ROADMAP.md) - US-038 user story

---

*Last Updated: 2025-10-20*
*Implementation: coffee_maker/autonomous/ace/*
*Status: ✅ Production Ready*
