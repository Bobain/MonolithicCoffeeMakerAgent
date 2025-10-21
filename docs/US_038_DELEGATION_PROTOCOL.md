# US-038: Delegation Protocol - Technical Documentation

**How Generator Auto-Delegates File Operations to Correct Owner**

---

## Table of Contents

1. [Overview](#overview)
2. [Delegation Workflow](#delegation-workflow)
3. [DelegationTrace Model](#delegationtrace-model)
4. [Database Schema](#database-schema)
5. [Delegation Statistics](#delegation-statistics)
6. [Monitoring and Analysis](#monitoring-and-analysis)
7. [Future: Actual Delegation Execution](#future-actual-delegation-execution)
8. [Examples](#examples)

---

## Overview

The **Delegation Protocol** defines how the Generator agent automatically routes file operations to the correct owner when ownership violations are detected.

### Key Principles

1. **Transparent**: Requesting agent doesn't need to know delegation occurred
2. **Automatic**: No manual ownership checking required
3. **Logged**: All delegations traced for analysis
4. **Non-blocking**: Delegation doesn't fail the operation
5. **Observable**: Full visibility into delegation patterns

### Delegation Decision Tree

```
File Operation Requested
        │
        ▼
    Read Operation?
    ┌───Yes───► Allow (no ownership check)
    │
    No
    │
    ▼
Get File Owner from Registry
        │
        ▼
  Agent == Owner?
    ┌───Yes───► Allow (direct execution)
    │
    No (Ownership Violation!)
    │
    ▼
Create DelegationTrace
        │
        ▼
Log to Database
        │
        ▼
Execute via Owner (future)
        │
        ▼
Return Result to Requester
```

---

## Delegation Workflow

### Phase 1: Interception

```python
# Agent requests file operation
write_tool = WriteTool(AgentType.ASSISTANT)
write_tool.write_file("coffee_maker/test.py", "# code")

# WriteTool intercepts and calls Generator
result = generator.intercept_file_operation(
    agent_type=AgentType.ASSISTANT,
    file_path="coffee_maker/test.py",
    operation="write",
    content="# code"
)
```

**Generator receives**:
- `agent_type`: Who's requesting (ASSISTANT)
- `file_path`: What file ("coffee_maker/test.py")
- `operation`: What action ("write")
- `content`: Operation data ("# code")

---

### Phase 2: Ownership Check

```python
# Generator checks ownership
owner = FileOwnership.get_owner("coffee_maker/test.py")
# Returns: AgentType.CODE_DEVELOPER

# Compare requesting agent vs. owner
if agent_type == owner:
    # Agent owns file - allow directly
    return OperationResult(success=True, delegated=False)
```

**Decision logic**:

| Requesting Agent | File Owner | Decision |
|------------------|------------|----------|
| CODE_DEVELOPER | CODE_DEVELOPER | ✅ Allow |
| ASSISTANT | CODE_DEVELOPER | ⚠️ Delegate |
| PROJECT_MANAGER | ARCHITECT | ⚠️ Delegate |

---

### Phase 3: Delegation Trace Creation

```python
# Ownership violation detected
# Create delegation trace for logging

trace = DelegationTrace(
    trace_id=f"delegation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
    timestamp=datetime.now(),
    requesting_agent=AgentType.ASSISTANT,
    owner_agent=AgentType.CODE_DEVELOPER,
    file_path="coffee_maker/test.py",
    operation=FileOperationType.WRITE,
    reason="Ownership violation: assistant tried to access code_developer's file",
    success=True  # Assumed for now
)
```

**Trace contains**:
- `trace_id`: Unique identifier for this delegation
- `timestamp`: When delegation occurred
- `requesting_agent`: Who requested the operation
- `owner_agent`: Who actually owns the file
- `file_path`: Which file was accessed
- `operation`: What operation (READ/WRITE/EDIT/DELETE)
- `reason`: Why delegation was needed
- `success`: Whether delegated operation succeeded

---

### Phase 4: Database Logging

```python
# Log delegation to SQLite database
db_trace_id = generator._log_trace_to_database(
    agent_type=AgentType.ASSISTANT,
    operation_type="file_operation",
    operation_name="write",
    parameters={"file_path": "coffee_maker/test.py", "content_length": 6},
    file_path="coffee_maker/test.py"
)

# Complete trace with delegation info
generator._complete_trace_in_database(
    trace_id=db_trace_id,
    exit_code=0,  # Success
    result={"delegated": True, "delegated_to": "code_developer"},
    delegated=True,
    delegated_to=AgentType.CODE_DEVELOPER
)
```

**Database record created**:
```sql
INSERT INTO generator_traces (
    trace_id, agent_type, operation_type, operation_name,
    file_path, started_at, status, delegated, delegated_to
) VALUES (
    42, 'assistant', 'file_operation', 'write',
    'coffee_maker/test.py', '2025-10-20T12:34:56', 'completed',
    1, 'code_developer'
);
```

---

### Phase 5: Result Return

```python
# Generator returns result to requesting agent
return OperationResult(
    success=True,              # Operation will succeed (delegated)
    delegated=True,            # Yes, delegation occurred
    delegated_to=AgentType.CODE_DEVELOPER,  # Delegated to owner
    trace_id="delegation_20251020_123456"   # Trace ID for lookup
)

# WriteTool receives result and logs
if result.delegated:
    logger.info(
        f"Write delegated: coffee_maker/test.py → {result.delegated_to.value}"
    )

# Return success to agent
return result.success  # True
```

**Agent receives**:
- Success (operation will complete)
- Doesn't need to handle delegation
- Transparent to requesting agent

---

## DelegationTrace Model

### Data Structure

```python
@dataclass
class DelegationTrace:
    """Trace record for delegated file operations.

    These traces are logged for reflector analysis to identify:
    - Common delegation patterns
    - Agents frequently violating ownership
    - Opportunities for improved agent design
    """

    trace_id: str                    # "delegation_20251020_123456"
    timestamp: datetime              # When delegation occurred
    requesting_agent: AgentType      # Who requested operation
    owner_agent: AgentType           # Who owns the file
    file_path: str                   # File being operated on
    operation: FileOperationType     # READ/WRITE/EDIT/DELETE
    reason: str                      # Why delegated
    success: bool                    # Whether succeeded

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "requesting_agent": self.requesting_agent.value,
            "owner_agent": self.owner_agent.value,
            "file_path": self.file_path,
            "operation": self.operation.value,
            "reason": self.reason,
            "success": self.success,
        }
```

### Example Trace

```json
{
    "trace_id": "delegation_20251020_123456_789012",
    "timestamp": "2025-10-20T12:34:56.789012",
    "requesting_agent": "assistant",
    "owner_agent": "code_developer",
    "file_path": "coffee_maker/cli/test.py",
    "operation": "write",
    "reason": "Ownership violation: assistant tried to access code_developer's file",
    "success": true
}
```

---

## Database Schema

### Table: generator_traces

```sql
CREATE TABLE generator_traces (
    trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type TEXT NOT NULL,           -- Requesting agent
    operation_type TEXT NOT NULL,       -- 'file_operation', 'tool', 'skill', 'command'
    operation_name TEXT NOT NULL,       -- 'write', 'read', 'edit', 'delete'
    file_path TEXT,                     -- File being operated on
    started_at TEXT NOT NULL,           -- ISO timestamp
    completed_at TEXT,                  -- ISO timestamp
    duration_ms INTEGER,                -- Operation duration
    status TEXT NOT NULL,               -- 'running', 'completed', 'failed'
    exit_code INTEGER,                  -- 0 = success, non-zero = error
    error_message TEXT,                 -- Error details if failed
    result TEXT,                        -- JSON result
    delegated INTEGER DEFAULT 0,        -- 0 = no, 1 = yes (boolean)
    delegated_to TEXT,                  -- Agent type delegated to
    parameters TEXT,                    -- JSON parameters
    task_id TEXT,                       -- Task ID for linking
    priority_number INTEGER             -- ROADMAP priority
);

-- Indexes for performance
CREATE INDEX idx_generator_traces_agent ON generator_traces(agent_type);
CREATE INDEX idx_generator_traces_delegated ON generator_traces(delegated);
CREATE INDEX idx_generator_traces_file_path ON generator_traces(file_path);
CREATE INDEX idx_generator_traces_started_at ON generator_traces(started_at);
```

### Sample Records

```sql
-- Direct write (no delegation)
INSERT INTO generator_traces VALUES (
    1, 'code_developer', 'file_operation', 'write',
    'coffee_maker/cli/test.py',
    '2025-10-20T12:00:00', '2025-10-20T12:00:00.100', 100,
    'completed', 0, NULL, NULL,
    0, NULL,  -- Not delegated
    '{"content_length": 100}', NULL, NULL
);

-- Delegated write
INSERT INTO generator_traces VALUES (
    2, 'assistant', 'file_operation', 'write',
    'coffee_maker/autonomous/test.py',
    '2025-10-20T12:01:00', '2025-10-20T12:01:00.050', 50,
    'completed', 0, NULL, '{"delegated": true, "delegated_to": "code_developer"}',
    1, 'code_developer',  -- Delegated!
    '{"content_length": 50}', NULL, NULL
);

-- Read operation (always allowed)
INSERT INTO generator_traces VALUES (
    3, 'assistant', 'file_operation', 'read',
    'coffee_maker/cli/roadmap_cli.py',
    '2025-10-20T12:02:00', '2025-10-20T12:02:00.010', 10,
    'completed', 0, NULL, NULL,
    0, NULL,  -- No delegation for reads
    '{}', NULL, NULL
);
```

---

## Delegation Statistics

### API: get_delegation_stats()

```python
from coffee_maker.autonomous.ace.generator import get_generator

generator = get_generator()
stats = generator.get_delegation_stats()
```

### Statistics Returned

```python
{
    "total_delegations": 42,

    "delegations_by_requesting_agent": {
        "assistant": 15,          # assistant had 15 delegations
        "project_manager": 12,    # project_manager had 12
        "architect": 10,          # architect had 10
        "user_listener": 5        # user_listener had 5
    },

    "delegations_by_owner": {
        "code_developer": 20,     # 20 operations delegated to code_developer
        "project_manager": 12,    # 12 to project_manager
        "architect": 10           # 10 to architect
    },

    "most_common_violations": [
        {
            "pattern": "assistant → code_developer",
            "count": 15
        },
        {
            "pattern": "project_manager → code_developer",
            "count": 12
        },
        {
            "pattern": "architect → code_developer",
            "count": 10
        },
        {
            "pattern": "assistant → project_manager",
            "count": 5
        }
    ]
}
```

### Interpretation

**High delegation rate** for an agent suggests:
1. Agent frequently accessing files it doesn't own
2. May indicate agent design issue
3. Or: Natural collaboration pattern

**Example analysis**:
```python
stats = generator.get_delegation_stats()

for agent, count in stats['delegations_by_requesting_agent'].items():
    total_ops = count  # Simplification
    delegation_rate = (count / total_ops) * 100

    if delegation_rate > 50:
        print(f"⚠️ {agent} has high delegation rate ({delegation_rate:.1f}%)")
        print(f"   Consider reviewing agent ownership boundaries")
```

---

## Monitoring and Analysis

### Query: Recent Delegations

```sql
-- Get all delegations in last 24 hours
SELECT
    started_at,
    agent_type,
    file_path,
    delegated_to
FROM generator_traces
WHERE delegated = 1
  AND started_at > datetime('now', '-1 day')
ORDER BY started_at DESC;
```

**Example output**:
```
2025-10-20 12:34:56 | assistant | coffee_maker/test.py | code_developer
2025-10-20 12:30:00 | project_manager | .claude/CLAUDE.md | code_developer
2025-10-20 12:15:00 | assistant | docs/roadmap/ROADMAP.md | project_manager
```

---

### Query: Delegation Rate by Agent

```sql
-- Calculate delegation rate per agent
SELECT
    agent_type,
    COUNT(*) as total_operations,
    SUM(delegated) as delegations,
    ROUND(100.0 * SUM(delegated) / COUNT(*), 2) as delegation_rate_pct
FROM generator_traces
WHERE operation_type = 'file_operation'
GROUP BY agent_type
ORDER BY delegation_rate_pct DESC;
```

**Example output**:
```
agent_type       | total_operations | delegations | delegation_rate_pct
-----------------|------------------|-------------|--------------------
assistant        | 100              | 50          | 50.00
project_manager  | 80               | 20          | 25.00
code_developer   | 200              | 5           | 2.50
architect        | 50               | 2           | 4.00
```

**Interpretation**:
- `assistant`: 50% delegation rate → Frequently accesses other agents' files
- `code_developer`: 2.5% delegation rate → Mostly writes to own files

---

### Query: Most Common Violation Patterns

```sql
-- Find most common agent → agent delegation patterns
SELECT
    agent_type || ' → ' || delegated_to as violation_pattern,
    COUNT(*) as count,
    GROUP_CONCAT(DISTINCT file_path) as example_files
FROM generator_traces
WHERE delegated = 1
GROUP BY violation_pattern
ORDER BY count DESC
LIMIT 10;
```

**Example output**:
```
violation_pattern              | count | example_files
-------------------------------|-------|----------------------------------
assistant → code_developer     | 150   | coffee_maker/test.py, .claude/CLAUDE.md
project_manager → code_developer | 50  | coffee_maker/cli/test.py
assistant → project_manager    | 30    | docs/roadmap/ROADMAP.md
architect → code_developer     | 20    | coffee_maker/autonomous/test.py
```

---

### Query: Delegation Hotspots (Files)

```sql
-- Find files most frequently involved in delegations
SELECT
    file_path,
    COUNT(*) as delegation_count,
    GROUP_CONCAT(DISTINCT agent_type) as requesting_agents,
    MAX(delegated_to) as owner
FROM generator_traces
WHERE delegated = 1
GROUP BY file_path
ORDER BY delegation_count DESC
LIMIT 10;
```

**Example output**:
```
file_path                    | delegation_count | requesting_agents      | owner
-----------------------------|------------------|------------------------|----------------
coffee_maker/cli/test.py     | 50               | assistant,architect    | code_developer
docs/roadmap/ROADMAP.md      | 30               | assistant,code_dev     | project_manager
.claude/CLAUDE.md            | 20               | project_manager        | code_developer
```

**Interpretation**:
- `coffee_maker/cli/test.py`: Frequently accessed by multiple agents
- May indicate central file or collaboration point

---

### Python API: Get Delegation Traces

```python
from coffee_maker.autonomous.ace.generator import get_generator
from coffee_maker.autonomous.agent_registry import AgentType

generator = get_generator()

# Get all delegations from assistant in last 24 hours
traces = generator.get_delegation_traces(
    agent=AgentType.ASSISTANT,
    hours=24
)

print(f"Found {len(traces)} delegations")

for trace in traces:
    print(f"{trace.timestamp}: {trace.file_path}")
    print(f"  {trace.requesting_agent.value} → {trace.owner_agent.value}")
    print(f"  Operation: {trace.operation.value}")
    print(f"  Reason: {trace.reason}")
    print()
```

**Example output**:
```
Found 15 delegations

2025-10-20 12:34:56: coffee_maker/test.py
  assistant → code_developer
  Operation: write
  Reason: Ownership violation: assistant tried to access code_developer's file

2025-10-20 12:30:00: docs/roadmap/ROADMAP.md
  assistant → project_manager
  Operation: write
  Reason: Ownership violation: assistant tried to access project_manager's file
```

---

## Future: Actual Delegation Execution

### Current State (Phase 1)

**What happens now**:
1. Generator detects ownership violation
2. Creates delegation trace
3. Logs to database
4. Returns success result
5. **Does NOT actually execute via owner** ⚠️

**Limitation**: Delegation is logged but not executed

---

### Future State (Phase 2)

**What will happen**:
1. Generator detects ownership violation
2. **Loads owner agent instance**
3. **Invokes owner agent to perform operation**
4. **Waits for owner agent to complete**
5. Returns actual result to requester

### Implementation Plan

```python
class Generator:
    def delegate_to_owner(
        self,
        owner_agent: AgentType,
        file_path: str,
        operation: str,
        content: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> OperationResult:
        """Actually execute operation via owner agent.

        Phase 2 Implementation:
        1. Load owner agent instance
        2. Create delegation context
        3. Execute operation via owner
        4. Return actual result
        """

        # 1. Load owner agent dynamically
        from coffee_maker.autonomous.agent_loader import AgentLoader

        owner = AgentLoader.load(owner_agent)

        # 2. Create delegation context
        delegation_context = DelegationContext(
            requesting_agent=context.get("requesting_agent"),
            file_path=file_path,
            operation=operation,
            content=content,
            timestamp=datetime.now(),
            trace_id=context.get("trace_id"),
        )

        # 3. Execute via owner
        try:
            result = owner.execute_file_operation(delegation_context)

            # 4. Log successful delegation
            logger.info(
                f"Delegation succeeded: {file_path} executed by {owner_agent.value}"
            )

            return OperationResult(
                success=True,
                delegated=True,
                delegated_to=owner_agent,
                result=result
            )

        except Exception as e:
            # 5. Log failed delegation
            logger.error(
                f"Delegation failed: {file_path} → {owner_agent.value}: {e}"
            )

            return OperationResult(
                success=False,
                delegated=True,
                delegated_to=owner_agent,
                error_message=str(e)
            )
```

### Agent Interface (Future)

```python
class Agent:
    """Base class for all agents."""

    def execute_file_operation(
        self,
        context: DelegationContext
    ) -> Any:
        """Execute a delegated file operation.

        Args:
            context: Delegation context with operation details

        Returns:
            Operation result

        Example:
            >>> context = DelegationContext(
            ...     requesting_agent=AgentType.ASSISTANT,
            ...     file_path="coffee_maker/test.py",
            ...     operation="write",
            ...     content="# code"
            ... )
            >>> result = agent.execute_file_operation(context)
        """

        # Log delegation
        logger.info(
            f"Executing delegated {context.operation} on {context.file_path} "
            f"(requested by {context.requesting_agent.value})"
        )

        # Execute operation based on type
        if context.operation == "write":
            return self._execute_write(context.file_path, context.content)
        elif context.operation == "edit":
            return self._execute_edit(context.file_path, context.old_content, context.new_content)
        elif context.operation == "delete":
            return self._execute_delete(context.file_path)
        else:
            raise ValueError(f"Unknown operation: {context.operation}")
```

### DelegationContext Model

```python
@dataclass
class DelegationContext:
    """Context passed to owner agent for delegated operations."""

    requesting_agent: AgentType      # Who requested
    file_path: str                   # What file
    operation: str                   # What operation
    content: Optional[str] = None    # Content for write
    old_content: Optional[str] = None  # Old content for edit
    new_content: Optional[str] = None  # New content for edit
    timestamp: datetime = field(default_factory=datetime.now)
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## Examples

### Example 1: Simple Delegation

```python
# assistant writes to code_developer file
write_tool = WriteTool(AgentType.ASSISTANT)
result = write_tool.write_file("coffee_maker/test.py", "# code")

# Delegation trace created:
{
    "trace_id": "delegation_20251020_120000",
    "timestamp": "2025-10-20T12:00:00",
    "requesting_agent": "assistant",
    "owner_agent": "code_developer",
    "file_path": "coffee_maker/test.py",
    "operation": "write",
    "reason": "Ownership violation: assistant tried to access code_developer's file",
    "success": true
}

# Database record created:
trace_id: 42
agent_type: assistant
file_path: coffee_maker/test.py
delegated: 1
delegated_to: code_developer
status: completed
```

---

### Example 2: Multiple Delegations

```python
# project_manager writes to multiple files
write_tool = WriteTool(AgentType.PROJECT_MANAGER)

# Owned file - no delegation
write_tool.write_file("docs/roadmap/ROADMAP.md", "# roadmap")
# delegation_count: 0

# code_developer file - delegated
write_tool.write_file("coffee_maker/test.py", "# code")
# delegation_count: 1

# architect file - delegated
write_tool.write_file("pyproject.toml", "[tool.poetry]...")
# delegation_count: 2

# Check statistics
stats = generator.get_delegation_stats()
print(stats['delegations_by_requesting_agent']['project_manager'])
# Output: 2
```

---

### Example 3: Delegation Pattern Analysis

```python
# Analyze delegation patterns for assistant
generator = get_generator()

# Get traces
traces = generator.get_delegation_traces(
    agent=AgentType.ASSISTANT,
    hours=168  # 1 week
)

# Group by owner
by_owner = {}
for trace in traces:
    owner = trace.owner_agent.value
    by_owner.setdefault(owner, []).append(trace)

# Print summary
print(f"assistant had {len(traces)} delegations in the last week:")
for owner, owner_traces in by_owner.items():
    print(f"  {owner}: {len(owner_traces)} delegations")
    # Show most common files
    files = {}
    for t in owner_traces:
        files[t.file_path] = files.get(t.file_path, 0) + 1
    top_files = sorted(files.items(), key=lambda x: x[1], reverse=True)[:3]
    for file, count in top_files:
        print(f"    - {file}: {count} times")
```

**Example output**:
```
assistant had 150 delegations in the last week:
  code_developer: 100 delegations
    - coffee_maker/cli/test.py: 30 times
    - .claude/commands/demo.md: 25 times
    - coffee_maker/autonomous/test.py: 20 times
  project_manager: 30 delegations
    - docs/roadmap/ROADMAP.md: 20 times
    - docs/templates/user_story.md: 10 times
  architect: 20 delegations
    - docs/architecture/specs/SPEC-042.md: 15 times
    - pyproject.toml: 5 times
```

---

## Related Documentation

- [US_038_TECHNICAL_SPEC.md](architecture/user_stories/US_038_TECHNICAL_SPEC.md) - Complete technical specification
- [US_038_FILE_OWNERSHIP_GUIDE.md](US_038_FILE_OWNERSHIP_GUIDE.md) - Practical usage guide
- [generator.py](../coffee_maker/autonomous/ace/generator.py) - Generator implementation
- [file_ownership.py](../coffee_maker/autonomous/ace/file_ownership.py) - Ownership registry
- [ROADMAP.md](roadmap/ROADMAP.md) - US-038 user story

---

*Last Updated: 2025-10-20*
*Implementation: coffee_maker/autonomous/ace/generator.py*
*Status: ✅ Phase 1 Complete (Logging), Phase 2 Planned (Execution)*
