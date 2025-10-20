# ACE Quick Reference Card

**One-page reference for the ACE (Agentic Context Engineering) Generator system**

---

## 🚀 Quick Start

```python
from coffee_maker.autonomous.ace.generator import get_generator
from coffee_maker.autonomous.agent_registry import AgentType

# Get singleton Generator instance
generator = get_generator()

# Intercept file operation
result = generator.intercept_file_operation(
    agent_type=AgentType.PROJECT_MANAGER,
    file_path="coffee_maker/code.py",
    operation="write",
    content="# Code"
)

print(f"Delegated: {result.delegated}")  # True (code_developer owns .py files)
print(f"Owner: {result.delegated_to.value}")  # code_developer
```

---

## 📋 Core Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| **Intercept** | Check ownership and delegate if needed | `generator.intercept_file_operation(...)` |
| **Load Context** | Get required files for agent | `generator.load_agent_context(AgentType.CODE_DEVELOPER)` |
| **Monitor Search** | Track file searches | `generator.monitor_file_search(agent, "glob", "*.py")` |
| **Get Traces** | Retrieve delegation history | `generator.get_delegation_traces(agent=AgentType.ASSISTANT, hours=24)` |
| **Get Stats** | Delegation statistics | `generator.get_delegation_stats()` |

---

## 🗂️ File Ownership (CFR-001)

| Agent | Owns |
|-------|------|
| `code_developer` | `coffee_maker/**/*.py`, `tests/**/*.py` |
| `project_manager` | `docs/roadmap/**/*.md` |
| `architect` | `docs/architecture/**/*.md`, `.claude/agents/*.md`, `pyproject.toml` |
| `assistant` | `.claude/commands/**/*.md` |
| `code_reviewer` | `docs/code-reviews/**/*.md` |

**Rule**: Read = always allowed. Write/Edit/Delete = checked.

---

## 🔍 Common Commands

### Check File Owner

```python
from coffee_maker.autonomous.ace.file_ownership import FileOwnership

owner = FileOwnership.get_owner("docs/roadmap/ROADMAP.md")
print(owner.value)  # project_manager
```

### Get Delegation History

```python
# Last 24 hours, all agents
traces = generator.get_delegation_traces(hours=24)

# Specific agent only
traces = generator.get_delegation_traces(
    agent=AgentType.ASSISTANT,
    hours=24
)

# Print traces
for trace in traces:
    print(f"{trace.requesting_agent.value} → {trace.owner_agent.value}")
    print(f"  File: {trace.file_path}")
```

### Get Statistics

```python
stats = generator.get_delegation_stats()

print(f"Total: {stats['total_delegations']}")
print(f"By agent: {stats['delegations_by_requesting_agent']}")
print(f"Common violations: {stats['most_common_violations']}")
```

### Load Agent Context

```python
# Get required files for agent
context = generator.load_agent_context(AgentType.CODE_DEVELOPER)

# Format for prompt
formatted = generator.format_context_for_prompt(context)
```

### Monitor File Searches

```python
# Track when agent searches for files
generator.monitor_file_search(
    agent_type=AgentType.CODE_DEVELOPER,
    operation="glob",
    file_pattern="**/*.py",
    context_provided=True
)

# Get search stats
stats = generator.get_search_stats()
print(f"Unexpected searches: {stats['unexpected_searches']}")
```

---

## 📊 Database Queries

```sql
-- Connect
sqlite3 data/orchestrator.db

-- Count delegations by agent
SELECT agent_type, COUNT(*) as count
FROM generator_traces
WHERE delegated = 1
GROUP BY agent_type
ORDER BY count DESC;

-- Recent delegations
SELECT agent_type, delegated_to, file_path, started_at
FROM generator_traces
WHERE delegated = 1
ORDER BY started_at DESC
LIMIT 20;

-- Average duration by operation
SELECT operation_name, AVG(duration_ms) as avg_ms
FROM generator_traces
GROUP BY operation_name;

-- Delegations in last 24 hours
SELECT COUNT(*)
FROM generator_traces
WHERE delegated = 1
  AND started_at > datetime('now', '-24 hours');
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| **Database not found** | Run `python coffee_maker/orchestrator/migrate_add_generator_traces.py` |
| **No delegations logged** | Check in-memory: `generator.delegation_traces` <br> Check DB: `SELECT COUNT(*) FROM generator_traces` |
| **Ownership unclear** | Add pattern to `FileOwnership` class in `file_ownership.py` |
| **Too many delegations** | Analyze patterns with `get_delegation_stats()`, update agent definitions |

---

## 🎯 Operation Results

```python
@dataclass
class OperationResult:
    success: bool              # Operation succeeded?
    delegated: bool            # Was it delegated?
    delegated_to: AgentType    # Owner agent (if delegated)
    error_message: str         # Error details (if failed)
    trace_id: str              # Trace ID for lookup
```

**Examples:**

```python
# Allowed (agent owns file)
OperationResult(success=True, delegated=False)

# Delegated (ownership violation)
OperationResult(success=True, delegated=True,
                delegated_to=AgentType.CODE_DEVELOPER,
                trace_id="delegation_20251020_103045_123456")

# Error (invalid operation)
OperationResult(success=False, error_message="Invalid operation type")
```

---

## 📈 Key Metrics

```python
# Delegation statistics
stats = generator.get_delegation_stats()

# {
#   'total_delegations': 23,
#   'delegations_by_requesting_agent': {
#     'assistant': 12,
#     'project_manager': 8
#   },
#   'delegations_by_owner': {
#     'code_developer': 15,
#     'architect': 5
#   },
#   'most_common_violations': [
#     {'pattern': 'assistant → code_developer', 'count': 10},
#     {'pattern': 'project_manager → code_developer', 'count': 5}
#   ]
# }

# Search statistics
search_stats = generator.get_search_stats()

# {
#   'total_searches': 25,
#   'unexpected_searches': 3,
#   'searches_by_agent': {'code_developer': 15, 'assistant': 10},
#   'most_common_patterns': [
#     {'pattern': 'glob:**/*.py', 'count': 5}
#   ]
# }
```

---

## 🔗 File Locations

| File | Path |
|------|------|
| **Generator** | `coffee_maker/autonomous/ace/generator.py` |
| **File Ownership** | `coffee_maker/autonomous/ace/file_ownership.py` |
| **Database** | `data/orchestrator.db` |
| **Migration** | `coffee_maker/orchestrator/migrate_add_generator_traces.py` |
| **Tests** | `tests/unit/test_ace_api.py` |

---

## ⚡ Common Patterns

### Pattern 1: Safe File Write

```python
def safe_write(agent_type, file_path, content):
    result = generator.intercept_file_operation(
        agent_type=agent_type,
        file_path=file_path,
        operation="write",
        content=content
    )

    if result.delegated:
        print(f"Delegated to {result.delegated_to.value}")
        # Actual write happens via delegation
    else:
        # Agent owns file, perform write
        Path(file_path).write_text(content)

    return result.success
```

### Pattern 2: Context-Upfront

```python
# Load all required files upfront
context = generator.load_agent_context(AgentType.PROJECT_MANAGER)

# Access files directly (no searching)
roadmap = context["docs/roadmap/ROADMAP.md"]
claude_md = context[".claude/CLAUDE.md"]

# No Glob/Grep needed!
```

### Pattern 3: Delegation Analysis

```python
# Analyze recent delegations
traces = generator.get_delegation_traces(hours=24)

# Group by pattern
from collections import Counter
patterns = Counter(
    f"{t.requesting_agent.value} → {t.owner_agent.value}"
    for t in traces
)

# Print top violations
for pattern, count in patterns.most_common(5):
    print(f"{count}x: {pattern}")
```

### Pattern 4: Cleanup Old Traces

```python
import sqlite3
from datetime import datetime, timedelta

cutoff = (datetime.now() - timedelta(days=30)).isoformat()

with sqlite3.connect("data/orchestrator.db") as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM generator_traces WHERE started_at < ?", (cutoff,))
    deleted = cursor.rowcount
    conn.commit()
    print(f"Deleted {deleted} traces older than 30 days")
```

---

## 🔐 Security Notes

- **Read operations**: Always allowed (no security check)
- **Write/Edit/Delete**: Ownership-checked
- **Database**: Local SQLite, no authentication required
- **Traces**: Contain file paths and operation details (no file contents)

---

## 📚 Related Docs

- **Full Tutorial**: [ACE_CONSOLE_DEMO_TUTORIAL.md](ACE_CONSOLE_DEMO_TUTORIAL.md)
- **Workflows**: [WORKFLOWS.md](WORKFLOWS.md)
- **Agent Ownership**: [AGENT_OWNERSHIP.md](AGENT_OWNERSHIP.md)
- **CFR-001**: [CRITICAL_FUNCTIONAL_REQUIREMENTS.md](roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)

---

**Version**: 1.0 | **Last Updated**: 2025-10-20 | **License**: Apache 2.0
