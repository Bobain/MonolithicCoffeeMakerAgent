# Claude Agent Invoker - Quick Start Guide

**5-Minute Setup**: Get started with programmatic Claude agent invocation

---

## Installation

Already installed! The invoker is part of your MonolithicCoffeeMakerAgent codebase.

---

## Quick Start

### 1. Basic Usage (30 seconds)

```python
from coffee_maker.claude_agent_invoker import get_invoker

# Get singleton invoker instance
invoker = get_invoker()

# Invoke an agent
result = invoker.invoke_agent(
    agent_type="architect",
    prompt="Create a technical spec for user authentication"
)

# Check result
if result.success:
    print("✅ Success!")
    print(f"Response: {result.content}")
    print(f"Tokens: {result.usage['output_tokens']}")
    print(f"Cost: ${result.cost_usd:.4f}")
else:
    print(f"❌ Error: {result.error}")
```

### 2. Streaming Progress (1 minute)

```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()

# Stream agent execution
for msg in invoker.invoke_agent_streaming(
    agent_type="code-developer",
    prompt="Implement US-042: Add OAuth2 authentication"
):
    # Real-time updates
    if msg.message_type == "message":
        print(f"💬 {msg.content}")
    elif msg.message_type == "tool_use":
        print(f"🔧 Using tool: {msg.metadata.get('name')}")
    elif msg.message_type == "result":
        print(f"🏁 Complete! Tokens: {msg.metadata.get('output_tokens')}")
```

### 3. Check History (30 seconds)

```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()

# Get recent invocations
history = invoker.get_history(agent_type="architect", limit=10)

for inv in history:
    print(f"📝 {inv['prompt'][:50]}...")
    print(f"   Status: {inv['status']}, Duration: {inv['duration_ms']}ms, Cost: ${inv['cost_usd']:.4f}")
```

### 4. Launch Dashboard (1 minute)

```bash
# From project root
streamlit run streamlit_apps/agent_invocation_monitor/app.py
```

Opens browser at http://localhost:8501 with full monitoring dashboard.

---

## Available Agents

Use these agent types with `invoke_agent()`:

| Agent Type | Description | Best For |
|------------|-------------|----------|
| `architect` | Technical design authority | Specs, ADRs, architecture |
| `code-developer` | Autonomous implementation | Feature implementation, bug fixes |
| `project-manager` | Project coordination | Roadmap, planning, status |
| `assistant` | Documentation expert | Docs, explanations, help |
| `ux-design-expert` | UI/UX design | Design, Tailwind, frontend |

---

## Common Patterns

### Pattern: Multi-Turn Conversation

```python
invoker = get_invoker()

# First message
result1 = invoker.invoke_agent("architect", "Design a caching layer")
session_id = result1.session_id

# Continue conversation with context
result2 = invoker.invoke_agent(
    "architect",
    "Add Redis support to the caching layer",
    session_id=session_id  # Maintains context
)
```

### Pattern: Execute Slash Command

```python
invoker = get_invoker()

result = invoker.invoke_slash_command(
    command_name="implement-feature",
    variables={
        "PRIORITY_NAME": "US-042",
        "PRIORITY_TITLE": "OAuth2 Authentication",
        "SPEC_CONTENT": open("docs/SPEC-042.md").read(),
        "PRIORITY_CONTENT": "Add OAuth2 support..."
    }
)
```

### Pattern: Debugging Failed Invocation

```python
invoker = get_invoker()

# Get failed invocations
history = invoker.get_history(limit=100)
failed = [h for h in history if h['status'] == 'error']

for inv in failed:
    print(f"❌ Invocation {inv['invocation_id']}")
    print(f"   Prompt: {inv['prompt'][:80]}")
    print(f"   Error: {inv['error']}")

    # Check streaming messages for details
    messages = invoker.get_stream_messages(inv['invocation_id'])
    print(f"   Total messages: {len(messages)}")
```

---

## Database Queries

Direct SQL access to `data/claude_invocations.db`:

```bash
sqlite3 data/claude_invocations.db
```

### Useful Queries

```sql
-- Recent invocations
SELECT invocation_id, agent_type, status, duration_ms, cost_usd
FROM claude_invocations
ORDER BY invoked_at DESC
LIMIT 10;

-- Cost by agent type
SELECT agent_type,
       COUNT(*) as invocations,
       SUM(output_tokens) as total_tokens,
       SUM(cost_usd) as total_cost
FROM claude_invocations
GROUP BY agent_type
ORDER BY total_cost DESC;

-- Success rate
SELECT status, COUNT(*) as count
FROM claude_invocations
GROUP BY status;

-- Streaming messages for invocation #42
SELECT sequence, message_type, content
FROM claude_stream_messages
WHERE invocation_id = 42
ORDER BY sequence;
```

---

## Tips & Tricks

### Tip 1: Use Streaming for Long Tasks
Anything >10 seconds should use streaming for progress visibility:
```python
# ✅ Good - see progress
for msg in invoker.invoke_agent_streaming("code-developer", long_task):
    update_ui(msg.content)

# ❌ Bad - no visibility until complete
result = invoker.invoke_agent("code-developer", long_task)
```

### Tip 2: Set Timeouts
Prevent hanging on stuck invocations:
```python
result = invoker.invoke_agent(
    "architect",
    "Complex design task",
    timeout=300  # 5 minutes max
)
```

### Tip 3: Check History Before Retrying
Avoid duplicate work:
```python
# Check if already invoked
history = invoker.get_history(agent_type="architect", limit=50)
similar = [h for h in history if "OAuth2" in h['prompt']]

if similar:
    print(f"Found {len(similar)} similar invocations")
    print("Reuse result?", similar[0]['content'][:100])
```

### Tip 4: Monitor Costs
Track spending:
```python
history = invoker.get_history(limit=1000)
total_cost = sum(h.get('cost_usd', 0) for h in history)
print(f"Total spent: ${total_cost:.2f}")

# Set budget alerts
if total_cost > 10.0:
    print("⚠️ Warning: Cost exceeds $10")
```

---

## Troubleshooting

### Problem: "Claude CLI not found"

**Solution:**
```bash
# Check Claude CLI path
which claude

# Update invoker initialization if needed
from coffee_maker.claude_agent_invoker import ClaudeAgentInvoker
invoker = ClaudeAgentInvoker(claude_path="/your/path/to/claude")
```

### Problem: Database locked

**Solution:**
```python
# Close other connections first
import sqlite3
conn = sqlite3.connect("data/claude_invocations.db")
conn.close()

# Then use invoker
invoker = get_invoker()
```

### Problem: Streaming messages not appearing

**Solution:**
Check that you're using `invoke_agent_streaming()` not `invoke_agent()`:
```python
# ❌ Wrong - not streaming
result = invoker.invoke_agent("architect", "task")

# ✅ Correct - streaming
for msg in invoker.invoke_agent_streaming("architect", "task"):
    print(msg)
```

---

## Next Steps

1. **Try it out**: Run the examples above
2. **Launch dashboard**: `streamlit run streamlit_apps/agent_invocation_monitor/app.py`
3. **Read migration guide**: `docs/CLAUDE_INVOKER_MIGRATION_GUIDE.md`
4. **Explore tests**: `tests/unit/test_claude_agent_invoker.py`

---

## Reference

- **Implementation**: `coffee_maker/claude_agent_invoker.py`
- **Migration Guide**: `docs/CLAUDE_INVOKER_MIGRATION_GUIDE.md`
- **Full Summary**: `docs/CLAUDE_INVOKER_IMPLEMENTATION_SUMMARY.md`
- **Tests**: `tests/unit/test_claude_agent_invoker.py`
- **Dashboard**: `streamlit_apps/agent_invocation_monitor/app.py`

---

**Questions?** Check the docs above or inspect the implementation directly!
