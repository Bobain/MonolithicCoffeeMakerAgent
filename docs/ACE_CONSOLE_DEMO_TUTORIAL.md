# ACE Console Demo Tutorial

**Last Updated**: 2025-10-20
**Status**: ✅ Complete
**Time to Complete**: 30 minutes
**Target Audience**: Developers, AI assistants, new users learning the ACE system

---

## 📚 Table of Contents

1. [Introduction to ACE Framework](#1-introduction-to-ace-framework)
2. [Prerequisites & Setup](#2-prerequisites--setup)
3. [Tutorial 1: Understanding the Generator](#3-tutorial-1-understanding-the-generator)
4. [Tutorial 2: File Ownership Enforcement](#4-tutorial-2-file-ownership-enforcement)
5. [Tutorial 3: Delegation Traces & Monitoring](#5-tutorial-3-delegation-traces--monitoring)
6. [Tutorial 4: Context-Upfront Pattern](#6-tutorial-4-context-upfront-pattern)
7. [Tutorial 5: Search Monitoring](#7-tutorial-5-search-monitoring)
8. [Real-World Scenarios](#8-real-world-scenarios)
9. [Troubleshooting Common Issues](#9-troubleshooting-common-issues)
10. [FAQ](#10-faq)
11. [Advanced Tips & Tricks](#11-advanced-tips--tricks)
12. [Next Steps](#12-next-steps)

---

## 1. Introduction to ACE Framework

### What is ACE?

**ACE (Agentic Context Engineering)** is a framework built into the MonolithicCoffeeMakerAgent system that manages how autonomous agents interact with files and enforce architectural boundaries.

### Core Components

The ACE framework consists of one primary agent:

| Component | Purpose | Primary Responsibility |
|-----------|---------|------------------------|
| **Generator** | File operation interceptor | Intercepts all file operations, enforces ownership rules (CFR-001), auto-delegates to correct owners, logs traces for analysis |

### Why Use ACE?

**Problem Without ACE:**
- Agents step on each other's toes
- `project_manager` overwrites `code_developer` files
- `assistant` modifies files they don't own
- Chaos, conflicts, merge nightmares

**Solution With ACE:**
- ✅ Automatic ownership enforcement (CFR-001)
- ✅ Zero-configuration delegation
- ✅ Transparent to requesting agents
- ✅ Complete observability via traces
- ✅ No file conflicts between agents

### When to Use Each Feature

| Feature | When to Use |
|---------|-------------|
| **Generator Interception** | Every time an agent writes/edits/deletes a file |
| **Context-Upfront** | Loading required files for agent execution |
| **Search Monitoring** | Tracking when agents search for files (detecting insufficient context) |
| **Delegation Traces** | Analyzing ownership violation patterns |

---

## 2. Prerequisites & Setup

### Required Installations

```bash
# Clone the repository
git clone https://github.com/Bobain/MonolithicCoffeeMakerAgent.git
cd MonolithicCoffeeMakerAgent

# Install dependencies
poetry install

# Activate environment
poetry shell

# Verify installation
python -c "from coffee_maker.autonomous.ace.generator import Generator; print('✅ ACE Generator installed')"
```

**Expected Output:**
```
✅ ACE Generator installed
```

### Environment Variables

The ACE Generator requires access to the orchestrator database:

```bash
# Verify database exists
ls -la data/orchestrator.db
```

**Expected Output:**
```
-rw-r--r--  1 user  staff  245760 Oct 20 10:30 data/orchestrator.db
```

If missing, initialize it:

```bash
# Run database migration
python coffee_maker/orchestrator/migrate_add_generator_traces.py
```

### First-Time Configuration

The Generator is automatically initialized when agents start. No manual configuration required!

### Verification Steps

```bash
# Start Python shell
python

# Import and test Generator
>>> from coffee_maker.autonomous.ace.generator import get_generator
>>> generator = get_generator()
>>> print(f"Generator ready: {generator is not None}")
```

**Expected Output:**
```python
Generator ready: True
```

---

## 3. Tutorial 1: Understanding the Generator

### What Generator Does

The **Generator** is the guardian of file ownership. It:

1. **Intercepts** every file write/edit/delete operation
2. **Checks** ownership using the FileOwnership registry
3. **Delegates** to the correct owner if violation detected
4. **Logs** delegation traces for analysis
5. **Returns** results transparently to the requesting agent

### How to Invoke Generator

The Generator is **automatic**. You don't invoke it directly - it intercepts operations transparently.

### Example: Capture Trace from code_developer

Let's see the Generator in action when `project_manager` tries to write to a file owned by `code_developer`:

```python
from coffee_maker.autonomous.ace.generator import Generator
from coffee_maker.autonomous.agent_registry import AgentType

# Initialize Generator
generator = Generator()

# Simulate project_manager trying to write to code_developer's file
result = generator.intercept_file_operation(
    agent_type=AgentType.PROJECT_MANAGER,
    file_path="coffee_maker/cli/test.py",
    operation="write",
    content="# Test code"
)

# Check results
print(f"Success: {result.success}")
print(f"Delegated: {result.delegated}")
print(f"Delegated to: {result.delegated_to.value if result.delegated else 'None'}")
print(f"Trace ID: {result.trace_id}")
```

**Expected Output:**
```
Success: True
Delegated: True
Delegated to: code_developer
Trace ID: delegation_20251020_103045_123456
```

### Interpreting the Trace Output

| Field | Meaning |
|-------|---------|
| `success: True` | Operation completed successfully |
| `delegated: True` | Operation was delegated to another agent |
| `delegated_to: code_developer` | The agent that actually performed the operation |
| `trace_id: delegation_...` | Unique ID for retrieving full trace details |

### Where Traces Are Stored

Traces are stored in **two locations**:

1. **In-Memory** (during session):
   ```python
   generator.delegation_traces  # List of DelegationTrace objects
   ```

2. **SQLite Database** (persistent):
   ```bash
   sqlite3 data/orchestrator.db "SELECT * FROM generator_traces LIMIT 5;"
   ```

---

## 4. Tutorial 2: File Ownership Enforcement

### What is File Ownership?

Every file in the project is "owned" by one agent. Ownership is defined in `coffee_maker/autonomous/ace/file_ownership.py`:

```python
from coffee_maker.autonomous.ace.file_ownership import FileOwnership
from coffee_maker.autonomous.agent_registry import AgentType

# Check who owns a file
owner = FileOwnership.get_owner("docs/roadmap/ROADMAP.md")
print(f"Owner: {owner.value}")  # project_manager

owner = FileOwnership.get_owner("coffee_maker/cli/user_listener.py")
print(f"Owner: {owner.value}")  # code_developer

owner = FileOwnership.get_owner(".claude/agents/architect.md")
print(f"Owner: {owner.value}")  # architect
```

### Ownership Rules (CFR-001)

**Read Operations**: Always allowed (no ownership check)

**Write/Edit/Delete Operations**: Checked against ownership

| Agent | Owns |
|-------|------|
| `code_developer` | `coffee_maker/**/*.py`, `tests/**/*.py` |
| `project_manager` | `docs/roadmap/**/*.md` |
| `architect` | `docs/architecture/**/*.md`, `.claude/agents/*.md` |
| `assistant` | `.claude/commands/**/*.md` |

### Example: Delegation When Owner Mismatch

```python
from coffee_maker.autonomous.ace.generator import Generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = Generator()

# ❌ assistant tries to write to architect's file
result = generator.intercept_file_operation(
    agent_type=AgentType.ASSISTANT,
    file_path=".claude/agents/architect.md",
    operation="write",
    content="# Updated architect definition"
)

print(f"Delegated: {result.delegated}")  # True
print(f"Owner: {result.delegated_to.value}")  # architect
```

**Console Output:**
```
INFO: Ownership violation detected: assistant tried to write .claude/agents/architect.md (owner: architect). Auto-delegating...
INFO: Delegation trace logged: delegation_20251020_104512_789012
```

### Understanding Delta Items

**Delta items** are the changes detected between agents' expected ownership and actual operations.

Get delegation statistics:

```python
stats = generator.get_delegation_stats()
print(f"Total delegations: {stats['total_delegations']}")
print(f"By requester: {stats['delegations_by_requesting_agent']}")
print(f"By owner: {stats['delegations_by_owner']}")
print(f"Most common violations: {stats['most_common_violations']}")
```

**Example Output:**
```python
Total delegations: 23
By requester: {'assistant': 12, 'project_manager': 8, 'user_listener': 3}
By owner: {'code_developer': 15, 'architect': 5, 'project_manager': 3}
Most common violations: [
    {'pattern': 'assistant → code_developer', 'count': 10},
    {'pattern': 'project_manager → code_developer', 'count': 5}
]
```

This tells us:
- `assistant` frequently tries to write code (should delegate to `code_developer`)
- May need to update `assistant` agent definition to not attempt code writing

---

## 5. Tutorial 3: Delegation Traces & Monitoring

### Viewing Delegation Traces

Get all delegations from a specific agent:

```python
from coffee_maker.autonomous.ace.generator import get_generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = get_generator()

# Get delegations from assistant in last 24 hours
traces = generator.get_delegation_traces(
    agent=AgentType.ASSISTANT,
    hours=24
)

for trace in traces:
    print(f"[{trace.timestamp}] {trace.requesting_agent.value} → {trace.owner_agent.value}")
    print(f"  File: {trace.file_path}")
    print(f"  Operation: {trace.operation.value}")
    print(f"  Reason: {trace.reason}")
    print()
```

**Example Output:**
```
[2025-10-20 10:45:12] assistant → code_developer
  File: coffee_maker/cli/new_feature.py
  Operation: write
  Reason: Ownership violation: assistant tried to access code_developer's file

[2025-10-20 11:22:45] assistant → architect
  File: .claude/agents/new_agent.md
  Operation: edit
  Reason: Ownership violation: assistant tried to access architect's file
```

### Complete ACE Workflow

**Workflow: Implementing a Feature with Automatic Delegation**

```python
from coffee_maker.autonomous.ace.generator import Generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = Generator()

# Step 1: Load context for code_developer
context = generator.load_agent_context(AgentType.CODE_DEVELOPER)
print(f"Loaded {len(context)} context files")

# Step 2: Format for prompt
formatted = generator.format_context_for_prompt(context, max_chars_per_file=5000)

# Step 3: Simulate code_developer writing to owned file (ALLOWED)
result1 = generator.intercept_file_operation(
    agent_type=AgentType.CODE_DEVELOPER,
    file_path="coffee_maker/new_module.py",
    operation="write",
    content="# New module"
)
print(f"Write allowed: {not result1.delegated}")  # True (owns the file)

# Step 4: Update ROADMAP (delegated to project_manager)
result2 = generator.intercept_file_operation(
    agent_type=AgentType.CODE_DEVELOPER,
    file_path="docs/roadmap/ROADMAP.md",
    operation="edit",
    content="Updated status"
)
print(f"Delegated: {result2.delegated}")  # True
print(f"Owner: {result2.delegated_to.value}")  # project_manager

# Step 5: View delegation stats
stats = generator.get_delegation_stats()
print(f"Total delegations: {stats['total_delegations']}")
```

### Feedback Loop Demonstration

The ACE system creates a feedback loop:

```
1. Agent tries operation → 2. Generator intercepts → 3. Checks ownership
                ↑                                              ↓
        7. Agent improves  ← 6. Patterns identified ← 4. Logs trace
                ↑                                              ↓
        Analysis reveals patterns                    5. Database stores
```

This loop helps identify:
- Agents that need better ownership awareness
- Files with unclear ownership
- Opportunities to improve agent design

---

## 6. Tutorial 4: Context-Upfront Pattern

### What is Context-Upfront?

Instead of agents **searching** for files (Glob/Grep), they receive **required files upfront** in their initial context.

**Old Pattern (Slow):**
```python
# Agent searches for ROADMAP
files = glob("docs/**/*.md")
for f in files:
    if "ROADMAP" in f:
        content = read(f)
```

**New Pattern (Fast):**
```python
# Generator provides ROADMAP upfront
context = generator.load_agent_context(AgentType.PROJECT_MANAGER)
roadmap = context["docs/roadmap/ROADMAP.md"]  # Already loaded!
```

### Loading Context for an Agent

```python
from coffee_maker.autonomous.ace.generator import Generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = Generator()

# Load context for project_manager
context = generator.load_agent_context(AgentType.PROJECT_MANAGER)

print("Files provided upfront:")
for file_path in context.keys():
    size = len(context[file_path])
    print(f"  - {file_path} ({size:,} chars)")
```

**Example Output:**
```
Files provided upfront:
  - docs/roadmap/ROADMAP.md (1,234,567 chars)
  - docs/roadmap/TEAM_COLLABORATION.md (45,678 chars)
  - docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md (23,456 chars)
  - .claude/CLAUDE.md (12,345 chars)
  - .claude/agents/project_manager.md (8,901 chars)
```

### Formatting Context for Prompts

```python
formatted = generator.format_context_for_prompt(context, max_chars_per_file=5000)
print(formatted[:500])
```

**Output:**
```
=== CONTEXT FILES PROVIDED UPFRONT ===

--- docs/roadmap/ROADMAP.md ---
# MonolithicCoffeeMakerAgent - Master Roadmap

**Last Updated**: 2025-10-20
...

--- docs/roadmap/TEAM_COLLABORATION.md ---
# Team Collaboration Methodology
...

=== END CONTEXT FILES ===

You have all required context above. Use Read tool for specific line ranges if needed, but do NOT search with Glob/Grep for these known files.
```

### Benefits of Context-Upfront

| Before | After |
|--------|-------|
| 5+ file searches per task | 0 searches (files provided) |
| 30-60 seconds searching | Instant access |
| Higher token usage | Lower token usage |
| Agent wastes time | Agent focuses on work |

---

## 7. Tutorial 5: Search Monitoring

### Monitoring File Searches

The Generator tracks when agents use Glob/Grep, which may indicate insufficient context:

```python
from coffee_maker.autonomous.ace.generator import Generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = Generator()

# Simulate code_developer searching for test files
generator.monitor_file_search(
    agent_type=AgentType.CODE_DEVELOPER,
    operation="glob",
    file_pattern="tests/**/*test*.py",
    context_provided=True  # Context WAS provided upfront
)

# Get search statistics
stats = generator.get_search_stats()
print(f"Total searches: {stats['total_searches']}")
print(f"Unexpected searches: {stats['unexpected_searches']}")
print(f"By agent: {stats['searches_by_agent']}")
```

**Console Output:**
```
WARNING: Unexpected file search: code_developer used glob for 'tests/**/*test*.py'. Consider adding to required context files in agent definition.

Total searches: 1
Unexpected searches: 1
By agent: {'code_developer': 1}
```

### Interpreting Search Logs

| Severity | Meaning | Action |
|----------|---------|--------|
| **INFO** | Expected search (assistant (using code analysis skills) or architect analysis) | None needed |
| **WARNING** | Unexpected search (context was provided) | Add file to agent's required context |

### Improving Agent Context

If you see repeated unexpected searches, update the agent's required files:

**Before** (in `generator.py`):
```python
AgentType.CODE_DEVELOPER: [
    "docs/roadmap/ROADMAP.md",
    ".claude/CLAUDE.md",
    ".claude/agents/code_developer.md",
]
```

**After** (add frequently searched file):
```python
AgentType.CODE_DEVELOPER: [
    "docs/roadmap/ROADMAP.md",
    ".claude/CLAUDE.md",
    ".claude/agents/code_developer.md",
    "tests/conftest.py",  # ← Added based on search logs
]
```

---

## 8. Real-World Scenarios

### Scenario A: Debugging Ownership Violations

**Problem**: `assistant` keeps trying to write code, causing delegations.

**Solution**:

```python
from coffee_maker.autonomous.ace.generator import get_generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = get_generator()

# Get all delegations from assistant
traces = generator.get_delegation_traces(agent=AgentType.ASSISTANT)

# Find patterns
violation_counts = {}
for trace in traces:
    key = f"{trace.file_path} ({trace.operation.value})"
    violation_counts[key] = violation_counts.get(key, 0) + 1

# Print most common violations
print("Top violations by assistant:")
for file_op, count in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {count}x: {file_op}")
```

**Output:**
```
Top violations by assistant:
  12x: coffee_maker/cli/helper.py (write)
  8x: tests/test_helper.py (write)
  5x: .claude/agents/assistant.md (edit)
```

**Action**: Update `assistant` agent definition to clarify it should NOT write code directly.

---

### Scenario B: Monitoring Agent Context Efficiency

**Problem**: Want to know if agents are using provided context or searching unnecessarily.

**Solution**:

```python
generator = get_generator()

# Run a task simulation
# ... (agents perform work) ...

# Get search statistics
stats = generator.get_search_stats()

print(f"Context Efficiency Report:")
print(f"  Total file searches: {stats['total_searches']}")
print(f"  Unexpected searches: {stats['unexpected_searches']}")
print(f"  Efficiency: {100 * (1 - stats['unexpected_searches']/max(stats['total_searches'], 1)):.1f}%")

print(f"\nMost searched patterns:")
for pattern_info in stats['most_common_patterns'][:3]:
    print(f"  {pattern_info['count']}x: {pattern_info['pattern']}")
```

**Output:**
```
Context Efficiency Report:
  Total file searches: 25
  Unexpected searches: 3
  Efficiency: 88.0%

Most searched patterns:
  5x: glob:**/*.py
  3x: grep:TODO
  2x: glob:tests/**/*
```

---

### Scenario C: Implementing Cross-Agent Feature

**Problem**: Need to implement a feature that touches multiple agent boundaries (code + docs + specs).

**Workflow**:

```python
from coffee_maker.autonomous.ace.generator import Generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = Generator()

# Step 1: code_developer writes implementation
code_result = generator.intercept_file_operation(
    agent_type=AgentType.CODE_DEVELOPER,
    file_path="coffee_maker/new_feature.py",
    operation="write",
    content="# New feature implementation"
)
print(f"Code: {code_result.success}, delegated={code_result.delegated}")

# Step 2: code_developer tries to update ROADMAP (delegated)
roadmap_result = generator.intercept_file_operation(
    agent_type=AgentType.CODE_DEVELOPER,
    file_path="docs/roadmap/ROADMAP.md",
    operation="edit",
    content="Status: Complete"
)
print(f"ROADMAP: delegated to {roadmap_result.delegated_to.value}")

# Step 3: architect creates technical spec
spec_result = generator.intercept_file_operation(
    agent_type=AgentType.ARCHITECT,
    file_path="docs/architecture/specs/SPEC-999.md",
    operation="write",
    content="# Technical Specification"
)
print(f"Spec: {spec_result.success}, delegated={spec_result.delegated}")

# View all traces for this feature
traces = generator.get_delegation_traces(hours=1)
print(f"\nTotal operations: {len(traces)}")
```

---

### Scenario D: Database Query for Observability

**Problem**: Need to analyze all Generator activity across all agents.

**Solution**:

```bash
# Connect to database
sqlite3 data/orchestrator.db

# Query delegation patterns
SELECT
    agent_type,
    delegated_to,
    COUNT(*) as delegation_count,
    AVG(duration_ms) as avg_duration_ms
FROM generator_traces
WHERE delegated = 1
  AND started_at > datetime('now', '-7 days')
GROUP BY agent_type, delegated_to
ORDER BY delegation_count DESC
LIMIT 10;
```

**Output:**
```
agent_type       delegated_to       delegation_count  avg_duration_ms
---------------  -----------------  ----------------  ---------------
assistant        code_developer     45                23.4
project_manager  code_developer     28                18.7
code_developer   project_manager    15                12.3
assistant        architect          8                 31.2
```

---

### Scenario E: Automated Trace Cleanup

**Problem**: Database getting large with old traces.

**Solution**:

```python
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

db_path = Path("data/orchestrator.db")

# Delete traces older than 30 days
cutoff = (datetime.now() - timedelta(days=30)).isoformat()

with sqlite3.connect(str(db_path)) as conn:
    cursor = conn.cursor()

    # Count before
    cursor.execute("SELECT COUNT(*) FROM generator_traces WHERE started_at < ?", (cutoff,))
    count_before = cursor.fetchone()[0]

    # Delete
    cursor.execute("DELETE FROM generator_traces WHERE started_at < ?", (cutoff,))
    conn.commit()

    print(f"Deleted {count_before} old traces (>30 days)")

    # Vacuum to reclaim space
    cursor.execute("VACUUM")
    conn.commit()

    print("Database optimized")
```

---

## 9. Troubleshooting Common Issues

### Issue 1: Generator Not Intercepting Operations

**Symptoms**:
```python
result = generator.intercept_file_operation(...)
# result shows no delegation even though ownership violated
```

**Solution**:

```python
# Check FileOwnership registry
from coffee_maker.autonomous.ace.file_ownership import FileOwnership

try:
    owner = FileOwnership.get_owner("your/file/path.py")
    print(f"Owner: {owner.value}")
except Exception as e:
    print(f"Ownership unclear: {e}")
    # File ownership not defined - Generator fails open (allows operation)
```

**Fix**: Add file pattern to `FileOwnership` class in `coffee_maker/autonomous/ace/file_ownership.py`.

---

### Issue 2: Database Logging Not Working

**Symptoms**:
```
WARNING: Database not found at data/orchestrator.db, database logging disabled
```

**Solution**:

```bash
# Run migration to create generator_traces table
python coffee_maker/orchestrator/migrate_add_generator_traces.py

# Verify table exists
sqlite3 data/orchestrator.db "SELECT name FROM sqlite_master WHERE type='table' AND name='generator_traces';"
```

**Expected Output:**
```
generator_traces
```

---

### Issue 3: Traces Not Appearing

**Symptoms**: `get_delegation_traces()` returns empty list even though delegations occurred.

**Solution**:

```python
# Check if traces are in database but not in-memory
import sqlite3

with sqlite3.connect("data/orchestrator.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM generator_traces WHERE delegated = 1")
    db_count = cursor.fetchone()[0]
    print(f"Traces in database: {db_count}")

# In-memory traces are session-only
# Use database queries for historical analysis
```

---

### Issue 4: Too Many Delegations

**Symptoms**: High delegation count indicating agents don't understand their boundaries.

**Solution**:

```python
# Analyze delegation patterns
stats = generator.get_delegation_stats()
print("Most common violations:")
for violation in stats['most_common_violations']:
    print(f"  {violation['pattern']}: {violation['count']} times")

# Update agent definitions to clarify ownership
# Add to agent prompt: "You do NOT own files in X directory"
```

---

### Issue 5: OwnershipUnclearError

**Symptoms**:
```python
OwnershipUnclearError: Multiple potential owners for path: shared_file.py
```

**Solution**:

```python
# Check ownership registry
from coffee_maker.autonomous.ace.file_ownership import FileOwnership

# Option 1: Make ownership explicit in FileOwnership class
# Add pattern to specific agent's ownership

# Option 2: Fail open (Generator allows operation with warning)
# No action needed - Generator logs warning and allows
```

---

## 10. FAQ

### Q1: Does every file operation go through Generator?

**A:** Not automatically. The Generator provides `intercept_file_operation()` method that should be called by agent wrapper code. Currently implemented for demonstration - full integration planned.

### Q2: How do I view all Generator traces?

**A:** Two ways:

```python
# In-memory (current session)
generator = get_generator()
traces = generator.get_delegation_traces()

# Database (persistent, historical)
import sqlite3
with sqlite3.connect("data/orchestrator.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM generator_traces ORDER BY started_at DESC LIMIT 100")
    rows = cursor.fetchall()
```

### Q3: Can I manually trigger a delegation?

**A:** Yes, call `intercept_file_operation()` directly:

```python
result = generator.intercept_file_operation(
    agent_type=AgentType.ASSISTANT,
    file_path="coffee_maker/code.py",
    operation="write",
    content="# Code"
)
```

### Q4: How do I delete bad traces?

**A:** Traces are append-only for audit purposes. To clean up old data:

```python
# Clear in-memory traces (testing only)
generator.clear_traces()

# Delete from database (be careful!)
import sqlite3
with sqlite3.connect("data/orchestrator.db") as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM generator_traces WHERE trace_id = ?", (trace_id,))
    conn.commit()
```

### Q5: How do delegation traces improve the system?

**A:** By analyzing traces, you can:
- Identify agents that frequently violate ownership
- Find files with unclear ownership
- Optimize agent definitions
- Improve context-upfront file lists
- Detect architectural issues early

### Q6: Can multiple agents share ownership of a file?

**A:** Currently no. Each file has one owner. If ownership is unclear, `FileOwnership.get_owner()` raises `OwnershipUnclearError` and Generator fails open (allows operation).

### Q7: How do I backup/restore traces?

**A:** Traces are in SQLite database:

```bash
# Backup
cp data/orchestrator.db data/orchestrator.db.backup

# Restore
cp data/orchestrator.db.backup data/orchestrator.db

# Export to JSON
sqlite3 data/orchestrator.db <<EOF
.mode json
.output traces_backup.json
SELECT * FROM generator_traces;
.quit
EOF
```

### Q8: What's the storage footprint?

**A:** Approximately:
- 500 bytes per delegation trace (in-memory)
- 1 KB per trace record (database with indexes)
- For 10,000 traces: ~10 MB

Cleanup old traces periodically (see Scenario E).

### Q9: How do I integrate Generator with my agent?

**A:** Wrap file operations:

```python
from coffee_maker.autonomous.ace.generator import get_generator
from coffee_maker.autonomous.agent_registry import AgentType

class MyAgent:
    def __init__(self):
        self.generator = get_generator()
        self.agent_type = AgentType.MY_AGENT

    def write_file(self, path, content):
        result = self.generator.intercept_file_operation(
            agent_type=self.agent_type,
            file_path=path,
            operation="write",
            content=content
        )

        if result.delegated:
            # Operation delegated to owner
            print(f"Delegated to {result.delegated_to.value}")
        else:
            # Perform actual write
            Path(path).write_text(content)
```

### Q10: Can I use ACE with other AI providers?

**A:** Yes! The ACE Generator is provider-agnostic. It works with any agent system that performs file operations.

---

## 11. Advanced Tips & Tricks

### Tip 1: Query Delegation Patterns

```python
# Find which agents delegate most to code_developer
stats = generator.get_delegation_stats()
for agent, count in stats['delegations_by_requesting_agent'].items():
    if agent in ['assistant', 'project_manager']:
        print(f"{agent} delegated {count} times - consider updating agent definition")
```

### Tip 2: Monitor Real-Time Delegations

```python
import time

last_count = 0
while True:
    stats = generator.get_delegation_stats()
    new_count = stats['total_delegations']

    if new_count > last_count:
        print(f"[{time.strftime('%H:%M:%S')}] New delegation detected! Total: {new_count}")
        # Get latest trace
        recent = generator.get_delegation_traces(hours=1)
        latest = recent[-1]
        print(f"  {latest.requesting_agent.value} → {latest.owner_agent.value}: {latest.file_path}")

    last_count = new_count
    time.sleep(5)
```

### Tip 3: Export Delegation Report

```python
import json
from datetime import datetime

def export_delegation_report(hours=24):
    generator = get_generator()
    traces = generator.get_delegation_traces(hours=hours)

    report = {
        "generated_at": datetime.now().isoformat(),
        "time_window_hours": hours,
        "total_delegations": len(traces),
        "traces": [trace.to_dict() for trace in traces]
    }

    report_path = f"delegation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report exported: {report_path}")

export_delegation_report(hours=168)  # Last 7 days
```

### Tip 4: Context Optimization

```python
# Find which files are frequently read but not in context
def analyze_missing_context():
    stats = generator.get_search_stats()

    # Extract searched file patterns
    patterns = [p['pattern'] for p in stats['most_common_patterns']]

    print("Consider adding these to agent context:")
    for pattern in patterns:
        if "glob:" in pattern or "grep:" in pattern:
            print(f"  - {pattern}")

analyze_missing_context()
```

### Tip 5: Automated Delegation Alerts

```python
import smtplib
from email.message import EmailMessage

def check_delegation_threshold(max_delegations=50):
    stats = generator.get_delegation_stats()

    if stats['total_delegations'] > max_delegations:
        # Send alert
        msg = EmailMessage()
        msg['Subject'] = '⚠️ High Delegation Count Alert'
        msg['From'] = 'generator@example.com'
        msg['To'] = 'admin@example.com'
        msg.set_content(f"Delegation count exceeded threshold: {stats['total_delegations']}")

        # Send email (configure SMTP)
        # smtp.send_message(msg)

        print(f"Alert: {stats['total_delegations']} delegations detected!")

# Run periodically
check_delegation_threshold()
```

### Tip 6: Database Performance Optimization

```sql
-- Add indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_generator_traces_agent ON generator_traces(agent_type);
CREATE INDEX IF NOT EXISTS idx_generator_traces_delegated ON generator_traces(delegated);
CREATE INDEX IF NOT EXISTS idx_generator_traces_time ON generator_traces(started_at);

-- Query with index
SELECT agent_type, COUNT(*)
FROM generator_traces
WHERE delegated = 1 AND started_at > datetime('now', '-7 days')
GROUP BY agent_type;
```

### Tip 7: Integration with Observability Tools

```python
# Export to Langfuse (observability platform used in this project)
from langfuse import Langfuse

langfuse = Langfuse()

def log_delegation_to_langfuse(trace):
    langfuse.trace(
        name="file_operation_delegation",
        input={
            "requesting_agent": trace.requesting_agent.value,
            "file_path": trace.file_path,
            "operation": trace.operation.value
        },
        output={
            "delegated_to": trace.owner_agent.value,
            "success": trace.success
        },
        metadata={
            "trace_id": trace.trace_id,
            "reason": trace.reason
        }
    )

# Use after each delegation
for trace in generator.get_delegation_traces(hours=1):
    log_delegation_to_langfuse(trace)
```

---

## 12. Next Steps

### Recommended Learning Path

1. **✅ Complete this tutorial** - You're here!
2. **Practice**: Run the examples in a Python shell
3. **Explore**: Read `coffee_maker/autonomous/ace/generator.py` source code
4. **Implement**: Add Generator to your own agent
5. **Analyze**: Use database queries to understand delegation patterns
6. **Optimize**: Update agent definitions based on insights

### Advanced Documentation

- **Technical Spec**: [SPEC-038 - ACE Generator](../architecture/specs/SPEC-038-ace-generator.md) (if exists)
- **File Ownership**: [FileOwnership Registry](../../coffee_maker/autonomous/ace/file_ownership.py:1)
- **Agent Singleton**: [AGENT_SINGLETON_ARCHITECTURE.md](../AGENT_SINGLETON_ARCHITECTURE.md)
- **Database Schema**: [generator_traces table](../../coffee_maker/orchestrator/migrate_add_generator_traces.py:1)

### Related Tutorials

- [TUTORIALS.md](TUTORIALS.md) - General system tutorials
- [QUICKSTART_PROJECT_MANAGER.md](QUICKSTART_PROJECT_MANAGER.md) - Project manager quickstart
- [WORKFLOWS.md](WORKFLOWS.md) - Common workflows

### Community & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues)
- **Discussions**: [Ask questions](https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions)
- **Pull Requests**: Contribute improvements

### Integration with Other Systems

The ACE Generator is designed to integrate with:

- **Langfuse**: Observability and tracing
- **Streamlit Dashboards**: Visualize delegation patterns
- **CI/CD Pipelines**: Enforce ownership in automation
- **GitHub Actions**: Validate ownership before merge

---

## 🎯 Summary

You've learned:

- ✅ What ACE Generator is and why it exists
- ✅ How to use Generator for file ownership enforcement
- ✅ How to monitor delegations and analyze patterns
- ✅ How to implement context-upfront pattern
- ✅ How to troubleshoot common issues
- ✅ Advanced tips for optimization and integration

**The ACE Generator ensures architectural boundaries are respected automatically, making multi-agent systems reliable and maintainable.**

---

**Happy Building!** 🚀

---

**Last Updated**: 2025-10-20
**Author**: MonolithicCoffeeMakerAgent Documentation Team
**License**: Apache 2.0
