# Claude Invoker Migration Guide

**Date**: 2025-10-26
**Purpose**: Replace all direct Claude API/CLI calls with unified `ClaudeAgentInvoker`
**Status**: Migration in progress

---

## Overview

We are migrating from direct `ClaudeAPI` and `ClaudeCLIInterface` usage to a unified `ClaudeAgentInvoker` interface.

### Benefits

1. **Streaming support** with real-time progress tracking
2. **Database persistence** of all agent interactions for debugging
3. **Unified interface** - one way to invoke Claude across the entire codebase
4. **Session management** for multi-turn conversations
5. **Cost tracking** and token usage monitoring
6. **CFR-014 compliance** - all invocations tracked in database

### Database Schema

All invocations stored in `data/claude_invocations.db`:

```sql
-- Main invocations table
claude_invocations (
    invocation_id,
    session_id,
    agent_type,
    prompt,
    system_prompt,
    content,              -- Aggregated response
    final_result,         -- Final exit message (for streaming)
    model,
    input_tokens,
    output_tokens,
    cost_usd,
    duration_ms,
    status,
    stop_reason,
    error,
    invoked_at,
    completed_at,
    working_dir,
    streaming,
    metadata
)

-- Streaming messages table
claude_stream_messages (
    id,
    invocation_id,
    message_type,         -- init, message, tool_use, tool_result, result
    sequence,
    timestamp,
    content,
    metadata
)
```

---

## Migration Patterns

### Pattern 1: Simple API Call

**Before:**
```python
from coffee_maker.autonomous.claude_api_interface import ClaudeAPI

api = ClaudeAPI()
result = api.execute_prompt("Create a spec for OAuth2")
print(result.content)
```

**After:**
```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()
result = invoker.invoke_agent("architect", "Create a spec for OAuth2")
print(result.content)
```

### Pattern 2: CLI Interface Call

**Before:**
```python
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

cli = ClaudeCLIInterface()
result = cli.execute_prompt(
    "Implement feature X",
    system_prompt="You are a code developer",
    working_dir="/path/to/project"
)
```

**After:**
```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()
result = invoker.invoke_agent(
    "code-developer",
    "Implement feature X",
    system_prompt="You are a code developer",
    working_dir="/path/to/project"
)
```

### Pattern 3: Streaming Invocation (NEW!)

**Before:** Not available

**After:**
```python
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()
for msg in invoker.invoke_agent_streaming("code-developer", "Implement US-042"):
    print(f"[{msg.message_type}] {msg.content}")

    # Update dashboard, database, or UI in real-time
    if msg.message_type == "tool_use":
        update_progress(f"Tool: {msg.metadata.get('name')}")
```

### Pattern 4: Multi-Turn Conversations

**Before:**
```python
api = ClaudeAPI()
result1 = api.execute_prompt("Create a spec")
# No built-in session management
```

**After:**
```python
invoker = get_invoker()
result1 = invoker.invoke_agent("architect", "Create a spec")
session_id = result1.session_id

# Continue conversation with context
result2 = invoker.invoke_agent(
    "architect",
    "Add authentication section",
    session_id=session_id
)
```

### Pattern 5: Slash Command Execution

**Before:** Manual template loading and substitution

**After:**
```python
invoker = get_invoker()
result = invoker.invoke_slash_command("implement-feature", {
    "PRIORITY_NAME": "US-042",
    "PRIORITY_TITLE": "Add OAuth2",
    "SPEC_CONTENT": spec_text,
    "PRIORITY_CONTENT": priority_text
})
```

---

## Files Requiring Migration

### High Priority (Core Agent Files)

1. **`coffee_maker/autonomous/agents/code_developer_agent.py`** (line 51, 110, 525, 527)
   - Replace `ClaudeCLIInterface()` with `get_invoker()`
   - Update `self.claude` initialization
   - Migrate all `execute_prompt()` calls

2. **`coffee_maker/autonomous/agents/architect_agent.py`** (line 398, 400)
   - Replace architect's Claude invocations
   - Use `invoke_agent("architect", ...)`

3. **`coffee_maker/autonomous/agents/architect_skills_mixin.py`** (lines 235, 237, 400, 402, 562, 564)
   - Migrate all skill-based Claude calls
   - Use unified invoker for consistency

4. **`coffee_maker/autonomous/daemon.py`** (lines 179, 300, 303, 308, 311)
   - Core daemon initialization
   - Replace `self.claude = ClaudeAPI()` pattern

5. **`coffee_maker/cli/ai_service.py`** (lines 54, 155)
   - CLI service layer
   - Replace with invoker for consistency

6. **`coffee_maker/ai_providers/providers/claude_provider.py`** (lines 74, 76)
   - Provider abstraction layer
   - Migrate to use invoker

### Medium Priority (Test Files)

These can be migrated gradually:
- `manual_tests/test_daemon_*.py` - All test files
- `tests/ci_tests/conftest.py` - Test fixtures

### Low Priority (Documentation)

Example code in docstrings:
- `coffee_maker/autonomous/claude_api_interface.py` - Update examples
- `coffee_maker/autonomous/claude_cli_interface.py` - Update examples

---

## Step-by-Step Migration Process

### Step 1: Import Change

**Replace:**
```python
from coffee_maker.autonomous.claude_api_interface import ClaudeAPI
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
```

**With:**
```python
from coffee_maker.claude_agent_invoker import get_invoker
```

### Step 2: Instance Creation

**Replace:**
```python
self.claude = ClaudeAPI(model="sonnet")
# OR
self.claude = ClaudeCLIInterface(model="sonnet")
```

**With:**
```python
self.invoker = get_invoker()  # Singleton, auto-configured
```

### Step 3: Method Calls

**Replace:**
```python
result = self.claude.execute_prompt(prompt, system_prompt, working_dir)
```

**With:**
```python
result = self.invoker.invoke_agent(
    agent_type="architect",  # or "code-developer", "project-manager"
    prompt=prompt,
    system_prompt=system_prompt,
    working_dir=working_dir
)
```

### Step 4: Enable Streaming (Optional but Recommended)

For long-running tasks, use streaming:

```python
# Before: No progress visibility
result = self.claude.execute_prompt(long_task)

# After: Real-time progress
for msg in self.invoker.invoke_agent_streaming("code-developer", long_task):
    if msg.message_type == "message":
        self.update_status(msg.content)
    elif msg.message_type == "tool_use":
        self.log_tool_use(msg.metadata["name"])
```

---

## Dashboard Integration

### Streaming Progress Widget

Add to your dashboard to show real-time agent progress:

```python
import streamlit as st
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()

# Show recent invocations
st.header("Recent Agent Invocations")
history = invoker.get_history(limit=20)
for inv in history:
    with st.expander(f"{inv['agent_type']}: {inv['prompt'][:50]}..."):
        st.write(f"Status: {inv['status']}")
        st.write(f"Duration: {inv['duration_ms']}ms")
        st.write(f"Tokens: {inv['input_tokens']} in, {inv['output_tokens']} out")
        st.write(f"Cost: ${inv['cost_usd']:.4f}")

        # Show streaming messages if available
        messages = invoker.get_stream_messages(inv['invocation_id'])
        if messages:
            st.subheader("Stream Timeline")
            for msg in messages:
                st.text(f"[{msg['sequence']}] {msg['message_type']}: {msg['content'][:100]}")
```

### Live Progress Bar

```python
import streamlit as st
from coffee_maker.claude_agent_invoker import get_invoker

invoker = get_invoker()

progress_bar = st.progress(0)
status_text = st.empty()

message_count = 0
for msg in invoker.invoke_agent_streaming("code-developer", "Implement US-042"):
    message_count += 1
    progress_bar.progress(min(message_count * 10, 100))
    status_text.text(f"[{msg.message_type}] {msg.content[:80]}...")

    if msg.message_type == "result":
        status_text.success("✅ Complete!")
        break
```

---

## Testing Strategy

### Unit Tests

Update existing tests to use invoker:

```python
def test_invoke_agent(mock_claude_cli):
    """Test agent invocation."""
    from coffee_maker.claude_agent_invoker import ClaudeAgentInvoker

    # Mock subprocess.run
    mock_claude_cli.return_value = Mock(
        returncode=0,
        stdout=json.dumps({
            "result": "Spec created",
            "session_id": "abc",
            "model": "sonnet",
            "input_tokens": 100,
            "output_tokens": 200,
            "total_cost_usd": 0.03,
            "duration_ms": 2000,
            "stop_reason": "end_turn"
        })
    )

    invoker = ClaudeAgentInvoker(db_path=":memory:")
    result = invoker.invoke_agent("architect", "Create spec")

    assert result.success
    assert result.content == "Spec created"
```

### Integration Tests

Test streaming in real scenarios:

```python
def test_streaming_integration():
    """Test streaming with real Claude CLI."""
    invoker = get_invoker()

    messages = []
    for msg in invoker.invoke_agent_streaming("architect", "Quick design question"):
        messages.append(msg)

    # Verify we got init, messages, and result
    assert any(m.message_type == "init" for m in messages)
    assert any(m.message_type == "result" for m in messages)

    # Verify database persistence
    invocation_id = messages[0].invocation_id
    stored_messages = invoker.get_stream_messages(invocation_id)
    assert len(stored_messages) == len(messages)
```

---

## Rollback Plan

If migration causes issues:

1. **Keep old interfaces** - Don't delete `claude_api_interface.py` or `claude_cli_interface.py` yet
2. **Feature flag** - Add config option to use old vs new invoker
3. **Gradual rollout** - Migrate one agent at a time, test thoroughly
4. **Database backups** - Back up `data/claude_invocations.db` before major migrations

---

## Success Metrics

Track these metrics to verify migration success:

1. **Code Coverage**: All Claude calls go through invoker
2. **Database Growth**: `claude_invocations` table populating correctly
3. **Streaming Usage**: Percentage of calls using streaming
4. **Error Rate**: Should not increase post-migration
5. **Performance**: Latency should be similar or better

---

## Next Steps

1. ✅ Create `claude_agent_invoker.py` module
2. ✅ Create database schema
3. ✅ Add streaming support
4. ✅ Add tests
5. ⏳ **Migrate high-priority files** (code_developer_agent.py, daemon.py)
6. ⏳ **Add dashboard streaming widgets**
7. ⏳ Migrate medium-priority files
8. ⏳ Update documentation
9. ⏳ Deprecate old interfaces
10. ⏳ Remove old interfaces after verification period

---

## Questions?

See:
- `coffee_maker/claude_agent_invoker.py` - Full implementation
- `tests/unit/test_claude_agent_invoker.py` - Usage examples
- This document - Migration patterns

**Contact**: architect agent for architecture questions, code_developer for implementation help
