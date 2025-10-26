# How To Spawn Claude Code Sub-Agents From Your System

**Tested**: ✅ Working as of 2025-10-26
**Use Case**: Make your autonomous agents delegate work to Claude Code's built-in sub-agents

---

## Quick Answer

Yes! Your system **can spawn Claude Code sub-agents programmatically**. Here's how:

```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()

# Spawn architect to create spec
result = invoker.invoke_agent(
    "architect",
    "Create technical spec for OAuth2 authentication"
)

# Spawn code-developer to implement
for msg in invoker.invoke_agent_streaming(
    "code-developer",
    "Implement US-042: OAuth2 authentication"
):
    print(f"[{msg.message_type}] {msg.content}")
```

**What happens:**
1. Invokes Claude CLI with `--print --output-format json`
2. References `.claude/agents/architect.md` (or `code_developer.md`)
3. Agent has full tool access (Read, Write, Edit, Bash, etc.)
4. Works on roadmap branch (CFR-013 compliant)
5. All activity tracked in `data/claude_invocations.db`

---

## Practical Integration Examples

### Example 1: code_developer_agent.py Spawning Claude Code's code-developer

Your autonomous `code_developer_agent.py` can delegate to Claude Code's sub-agent:

```python
class CodeDeveloperAgent(BaseAgent):
    def __init__(self, ...):
        super().__init__(...)
        self.invoker = get_invoker()  # ✅ NEW

    def _implement_priority(self, priority: Dict, spec_file: Path) -> bool:
        """Implement priority by spawning Claude Code's code-developer."""

        # Build prompt for Claude's code-developer sub-agent
        spec_content = spec_file.read_text()

        prompt = f"""
Implement {priority['id']}: {priority['title']}

## Technical Specification

{spec_content}

## Instructions

1. Read the spec above carefully
2. Implement following the spec exactly
3. Add tests as specified
4. Run tests (pytest)
5. Commit: "feat: Implement {priority['id']}"

You have full tool access. Use Read, Write, Edit, Bash as needed.
"""

        # Spawn Claude Code's code-developer with streaming
        print(f"🚀 Spawning code-developer for {priority['id']}")

        for msg in self.invoker.invoke_agent_streaming(
            "code-developer",
            prompt,
            timeout=1800  # 30 min for implementation
        ):
            # Track progress
            if msg.message_type == "message":
                self.update_status(msg.content)
            elif msg.message_type == "tool_use":
                self.log(f"Tool: {msg.metadata.get('name')}")

        return True  # Implementation delegated to sub-agent
```

**Benefits:**
- ✅ Your agent becomes a **coordinator** instead of implementer
- ✅ Leverages Claude Code's full system prompt and tool capabilities
- ✅ Real-time progress tracking via streaming
- ✅ Database history for debugging

### Example 2: Orchestrator Spawning Multiple Agents in Parallel

Your orchestrator can spawn agents for parallel task execution:

```python
from coffee_maker.claude_agent_invoker import get_invoker
from concurrent.futures import ThreadPoolExecutor

invoker = get_invoker()

def spawn_agent_for_task(task_id: str, agent_type: str, prompt: str):
    """Spawn sub-agent for a task."""
    result = invoker.invoke_agent(agent_type, prompt, timeout=1800)
    return {
        'task_id': task_id,
        'success': result.success,
        'cost': result.cost_usd,
        'invocation_id': result.invocation_id
    }

# Spawn multiple agents in parallel
tasks = [
    ('task-1', 'architect', 'Create spec for caching'),
    ('task-2', 'code-developer', 'Implement US-042'),
    ('task-3', 'project-manager', 'Update roadmap status'),
]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(spawn_agent_for_task, task_id, agent, prompt)
        for task_id, agent, prompt in tasks
    ]

    results = [f.result() for f in futures]

print(f"Completed {len(results)} tasks in parallel")
```

### Example 3: architect_agent.py Delegating Spec Creation

Your architect agent can delegate to Claude Code's architect:

```python
class ArchitectAgent(BaseAgent):
    def __init__(self, ...):
        super().__init__(...)
        self.invoker = get_invoker()

    def create_spec_for_priority(self, priority: Dict) -> Path:
        """Delegate spec creation to Claude Code's architect sub-agent."""

        prompt = f"""
Create technical specification for {priority['id']}: {priority['title']}

## Priority Details
{priority.get('description', '')}

## Requirements
Create comprehensive spec following SPEC-XXX format:
1. Problem statement
2. Proposed solution
3. Implementation steps
4. Testing strategy
5. Definition of Done

Save to: docs/architecture/specs/SPEC-{priority['number']}-{priority['id'].lower()}.md

Use Write tool to create the file.
"""

        print(f"🏗️  Delegating spec creation to architect sub-agent")

        # Non-streaming for specs (simpler)
        result = self.invoker.invoke_agent(
            "architect",
            prompt,
            timeout=600  # 10 min for spec
        )

        if result.success:
            # Find the created spec file
            spec_file = self._find_created_spec(priority)
            return spec_file
        else:
            raise Exception(f"Spec creation failed: {result.error}")
```

---

## Using Slash Commands

Invoke your `.claude/commands/*.md` slash commands programmatically:

```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()

# Execute /implement-feature command
result = invoker.invoke_slash_command(
    command_name="implement-feature",
    variables={
        "PRIORITY_NAME": "US-042",
        "PRIORITY_TITLE": "OAuth2 Authentication",
        "SPEC_CONTENT": open("docs/specs/SPEC-042.md").read(),
        "PRIORITY_CONTENT": "Add OAuth2 support..."
    },
    timeout=1800
)

if result.success:
    print("✅ Feature implemented via slash command")
```

**Available Commands:**
- `implement-feature` - Full implementation workflow
- `create-technical-spec` - Spec creation
- `verify-dod-puppeteer` - DoD verification with Puppeteer
- Any custom commands in `.claude/commands/`

---

## Monitoring & Debugging

### Real-Time Progress (Dashboard)

```bash
streamlit run streamlit_apps/agent_invocation_monitor/app.py
```

Shows:
- All agent invocations
- Streaming message timeline
- Token usage and costs
- Performance metrics

### Query Database Directly

```bash
sqlite3 data/claude_invocations.db
```

```sql
-- Recent invocations
SELECT * FROM claude_invocations
ORDER BY invoked_at DESC LIMIT 10;

-- Streaming messages for invocation #42
SELECT sequence, message_type, content
FROM claude_stream_messages
WHERE invocation_id = 42
ORDER BY sequence;

-- Cost by agent type
SELECT agent_type, SUM(cost_usd) as total_cost
FROM claude_invocations
GROUP BY agent_type;
```

### Python API

```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()

# Get history
history = invoker.get_history(agent_type="code-developer", limit=20)

for inv in history:
    print(f"{inv['invocation_id']}: {inv['prompt'][:50]}...")
    print(f"  Status: {inv['status']}, Cost: ${inv['cost_usd']:.4f}")

# Get streaming details
messages = invoker.get_stream_messages(invocation_id=42)
for msg in messages:
    print(f"[{msg['sequence']}] {msg['message_type']}: {msg['content'][:80]}")
```

---

## Testing

Tested and working:

```bash
# Run basic tests
pytest tests/unit/test_claude_agent_invoker.py -v

# Test actual invocation
python examples/claude_agent_spawning/spawn_code_developer.py

# Interactive demo
python examples/claude_agent_spawning/spawn_code_developer.py
# Then choose option 1, 2, or 3
```

**Verified:**
- ✅ Database schema creation
- ✅ Non-streaming invocation
- ✅ Streaming invocation
- ✅ Session management
- ✅ Error handling
- ✅ Slash command execution
- ✅ Actual Claude CLI integration (tested with simple prompt)

---

## Architecture

```
Your Autonomous Agent
  │
  ├─> ClaudeAgentInvoker.invoke_agent()
  │     │
  │     ├─> Executes: claude --print --output-format json
  │     ├─> References: .claude/agents/{agent_type}.md
  │     ├─> Full tool access: Read, Write, Edit, Bash, etc.
  │     └─> Returns: AgentInvocationResult
  │
  └─> Database persistence
        ├─> data/claude_invocations.db
        │     ├─> claude_invocations (main records)
        │     └─> claude_stream_messages (streaming history)
        │
        └─> Dashboard visualization
```

---

## Benefits of This Approach

### 1. Separation of Concerns
- **Your agents**: Coordinators, workflow managers
- **Claude Code agents**: Actual implementation with full tool access

### 2. Leverage Claude Code's Prompts
Your `.claude/agents/*.md` files already have:
- Comprehensive system prompts
- Tool usage guidelines
- Best practices
- CFR compliance instructions

### 3. Database Tracking
Every invocation tracked for:
- Debugging failed implementations
- Cost analysis
- Performance monitoring
- Compliance verification

### 4. Real-Time Visibility
Streaming lets you:
- Show progress in dashboards
- Update status in real-time
- Intervene if needed
- Track tool usage

---

## Common Patterns

### Pattern: Request → Validate → Delegate → Verify

```python
def implement_priority(priority: Dict):
    """Standard implementation workflow with sub-agent delegation."""

    # 1. Validate
    if not find_spec(priority):
        raise Exception("Spec required first")

    # 2. Delegate to sub-agent
    invoker = get_invoker()
    result = invoker.invoke_agent(
        "code-developer",
        f"Implement {priority['id']}",
        timeout=1800
    )

    # 3. Verify
    if result.success:
        # Check tests passed, files changed, etc.
        verify_implementation(priority)
    else:
        handle_failure(result.error)
```

### Pattern: Streaming Progress Updates

```python
def implement_with_progress(priority: Dict):
    """Implementation with live progress updates."""

    invoker = get_invoker()
    progress = 0

    for msg in invoker.invoke_agent_streaming("code-developer", prompt):
        # Update progress bar
        if msg.message_type == "tool_use":
            progress += 10
            update_dashboard(f"Progress: {progress}%")

        # Log tool usage
        if msg.message_type == "tool_result":
            log_to_database(msg.metadata)
```

### Pattern: Parallel Agent Execution

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_implementation(priorities: List[Dict]):
    """Implement multiple priorities in parallel."""

    invoker = get_invoker()

    def implement_one(p):
        return invoker.invoke_agent("code-developer", f"Implement {p['id']}")

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(implement_one, priorities))

    return results
```

---

## Next Steps

1. **Try the example**: `python examples/claude_agent_spawning/spawn_code_developer.py`
2. **Launch dashboard**: `streamlit run streamlit_apps/agent_invocation_monitor/app.py`
3. **Migrate your agents**: See `docs/CLAUDE_INVOKER_MIGRATION_GUIDE.md`
4. **Read quick start**: `docs/CLAUDE_INVOKER_QUICK_START.md`

---

## References

- **Invoker Implementation**: `coffee_maker/claude_agent_invoker.py`
- **Migration Guide**: `docs/CLAUDE_INVOKER_MIGRATION_GUIDE.md`
- **Quick Start**: `docs/CLAUDE_INVOKER_QUICK_START.md`
- **Tests**: `tests/unit/test_claude_agent_invoker.py`
- **Example**: `examples/claude_agent_spawning/spawn_code_developer.py`

---

**Status**: ✅ Tested and working
**Last Updated**: 2025-10-26
