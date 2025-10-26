# Orchestrator-Agent Communication Architecture

**Date**: 2025-10-26
**Status**: Implemented ✅
**Related**: Final architecture where agents ARE Claude Code sessions

---

## Overview

In the final architecture, **ALL agents run as Claude Code sessions**, not Python processes. The orchestrator is the only persistent Python process that spawns these sessions as needed.

This document explains how orchestrator and agents communicate.

---

## Communication Channels

### 1. Orchestrator → Agent (Task Assignment)

**Method**: Via the initial prompt when spawning

```python
# Orchestrator spawns agent with task
prompt = f"""Implement priority {priority_number}.

## Task
1. Use Read tool to read docs/roadmap/ROADMAP.md
2. Find priority {priority_number}
3. Read the spec
4. Implement the feature
5. Report "COMPLETE: Priority {priority_number} implemented"

Start now. When done, exit."""

invoker.invoke_agent_streaming("code-developer", prompt, timeout=3600)
```

**What gets communicated:**
- Task type and parameters
- Instructions and constraints
- Expected deliverables
- Timeout limits

**Limitations:**
- ❌ One-way only (orchestrator → agent)
- ❌ No dynamic instructions after spawn
- ✅ Clear, complete task definition upfront

---

### 2. Agent → Orchestrator (Real-Time Progress)

**Method**: Streaming JSON messages via `ClaudeAgentInvoker`

```python
# Orchestrator receives real-time updates
for msg in invoker.invoke_agent_streaming("architect", prompt, timeout=1800):
    if msg.message_type == "message":
        # Agent text output
        logger.info(f"💬 {msg.content}")

    elif msg.message_type == "tool_use":
        # Agent using a tool (Read, Write, Edit, Bash)
        tool_name = msg.metadata.get("name")
        logger.info(f"🔧 Agent using: {tool_name}")

    elif msg.message_type == "result":
        # Session completed
        success = msg.metadata.get("stop_reason") != "error"
        logger.info(f"🏁 Session complete (success={success})")
```

**What gets communicated:**
- Agent thoughts and plans
- Tool invocations (Read, Write, Edit, Bash)
- Progress updates
- Error messages
- Final result and exit status

**Benefits:**
- ✅ Real-time visibility into agent actions
- ✅ Can detect when agent is stuck
- ✅ Can log all tool usage
- ✅ Can trigger orchestrator actions based on agent progress

---

### 3. Agent → Database (Persistent State)

**Method**: Automatic tracking by `ClaudeAgentInvoker`

**Database: `data/claude_invocations.db`**

```sql
-- All invocations stored
CREATE TABLE claude_invocations (
    invocation_id INTEGER PRIMARY KEY,
    agent_type TEXT NOT NULL,           -- code-developer, architect, etc.
    prompt TEXT NOT NULL,               -- Task given to agent
    content TEXT,                       -- Aggregated agent output
    final_result TEXT,                  -- Final exit message
    status TEXT NOT NULL,               -- completed, failed, running
    duration_ms INTEGER,
    cost_usd REAL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    invoked_at TEXT NOT NULL,
    completed_at TEXT,
    ...
);

-- All streaming messages stored
CREATE TABLE claude_stream_messages (
    id INTEGER PRIMARY KEY,
    invocation_id INTEGER,
    message_type TEXT,                  -- message, tool_use, result
    sequence INTEGER,
    timestamp TEXT,
    content TEXT,
    metadata TEXT,                      -- JSON with tool details, etc.
    ...
);
```

**What gets communicated:**
- Complete invocation history
- All streaming messages
- Token usage and costs
- Performance metrics
- Success/failure status

**Benefits:**
- ✅ Full audit trail
- ✅ Cost tracking
- ✅ Performance analysis
- ✅ Debugging and replay
- ✅ Dashboard visualization

---

### 4. Agent → Files (Deliverables)

**Method**: Agents use Write/Edit tools directly

**Examples:**
- Architect writes: `docs/architecture/specs/SPEC-123-feature.md`
- Code developer writes: `coffee_maker/new_feature.py`
- Project manager edits: `docs/roadmap/ROADMAP.md`
- Code reviewer writes: `evidence/code-review-{commit}.md`

**What gets communicated:**
- Specifications
- Implementation code
- Test files
- Reports and analysis
- Roadmap updates

**Benefits:**
- ✅ Persistent deliverables
- ✅ Standard file formats
- ✅ Git-trackable
- ✅ Human-readable

---

### 5. Agent ← → Orchestrator (Database Coordination)

**Method**: Orchestrator tracks agent lifecycle in `data/orchestrator.db`

**Database: `data/orchestrator.db`**

```sql
CREATE TABLE agent_lifecycle (
    pid INTEGER PRIMARY KEY,            -- Thread ID (pseudo-PID)
    agent_type TEXT NOT NULL,           -- code_developer, architect, etc.
    task_id TEXT NOT NULL,              -- impl-42, spec-059, etc.
    task_type TEXT NOT NULL,            -- implementation, create_spec, etc.
    priority_number INTEGER,
    spawned_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    status TEXT NOT NULL,               -- spawned, running, completed, failed
    exit_code INTEGER,
    command TEXT,
    worktree_path TEXT,
    ...
);
```

**What gets communicated:**
- Agent spawn events
- Agent status changes (spawned → running → completed)
- Agent exit codes
- Task assignments

**Orchestrator uses this to:**
- ✅ Track active agents
- ✅ Detect hung agents
- ✅ Coordinate parallel execution
- ✅ Cleanup completed agents
- ✅ Restart failed agents

---

## Communication Patterns

### Pattern 1: Fire-and-Forget

```python
# Orchestrator spawns agent in background
thread = Thread(target=run_architect_session, args=(priority_id,))
thread.start()  # Doesn't wait

# Agent runs independently
# Orchestrator continues with other work
```

**Use case**: Parallel execution, long-running tasks

---

### Pattern 2: Monitor and React

```python
# Orchestrator monitors streaming messages
for msg in invoker.invoke_agent_streaming("code-developer", prompt):
    if msg.message_type == "tool_use":
        tool = msg.metadata.get("name")

        # React to specific tools
        if tool == "Bash" and "git commit" in msg.metadata.get("input", ""):
            logger.info("🎉 Agent committed changes!")
            # Could trigger code_reviewer here
```

**Use case**: Triggering follow-up actions based on agent behavior

---

### Pattern 3: Check and Wait

```python
# Orchestrator checks if agent is done
while True:
    conn = sqlite3.connect("data/orchestrator.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM agent_lifecycle WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()

    if row and row[0] == "completed":
        logger.info("Agent finished!")
        break

    time.sleep(5)  # Check every 5 seconds
```

**Use case**: Waiting for prerequisite tasks before proceeding

---

## Agent-to-Agent Communication

**Important**: Agents do NOT communicate directly with each other.

### Indirect Communication via Files

Agents can leave messages for each other by writing files:

```python
# Architect writes spec
Write("docs/architecture/specs/SPEC-042-feature.md", spec_content)

# Code developer reads spec later
spec_content = Read("docs/architecture/specs/SPEC-042-feature.md")
```

### Indirect Communication via Database

Orchestrator coordinates handoffs:

```python
# 1. Orchestrator spawns architect
spawn_architect(priority=42)

# 2. Wait for architect to complete
wait_for_task_completion("spec-42")

# 3. Orchestrator spawns code_developer
spawn_code_developer(priority=42)
```

---

## Observability

### Real-Time Monitoring

```python
# Orchestrator logs all agent activity
for msg in invoker.invoke_agent_streaming("architect", prompt):
    logger.info(f"[architect/spec-42] {msg.message_type}: {msg.content[:100]}")
```

**Output:**
```
[architect/spec-42] message: Let me read the roadmap to find priority 42...
[architect/spec-42] tool_use: Read
[architect/spec-42] message: I found priority 42. Now I'll read existing architecture...
[architect/spec-42] tool_use: Read
[architect/spec-42] message: Creating specification...
[architect/spec-42] tool_use: Write
[architect/spec-42] result: Session complete (success=True)
```

### Dashboard Visualization

```bash
# View all agent activity in Streamlit dashboard
streamlit run streamlit_apps/agent_invocation_monitor/app.py
```

**Features:**
- Live agent status
- Streaming message timeline
- Token usage and costs
- Performance metrics

---

## Error Handling

### Agent Crashes

```python
# Orchestrator detects crash via exception
try:
    for msg in invoker.invoke_agent_streaming("code-developer", prompt):
        process_message(msg)
except Exception as e:
    logger.error(f"Agent crashed: {e}")
    # Mark as failed in database
    update_agent_status(task_id, status="failed")
```

### Agent Timeouts

```python
# Timeout specified when spawning
for msg in invoker.invoke_agent_streaming("architect", prompt, timeout=1800):
    # If 30 minutes pass, TimeoutError raised
    process_message(msg)
```

### Orchestrator Reactions

When agent fails:
1. ✅ Update status in database
2. ✅ Log error details
3. ✅ Optionally retry with different approach
4. ✅ Notify user/dashboard

---

## Limitations and Future Enhancements

### Current Limitations

1. **No Dynamic Task Modification**: Once spawned, agent's task can't be changed
2. **No Agent Interruption**: Can't send new instructions mid-execution
3. **No Agent-to-Agent Direct Communication**: Must go through files or orchestrator

### Potential Enhancements

1. **Message Queue**: Add `data/messages/` directory for agent-to-agent messages
   ```python
   # Agent leaves message
   Write("data/messages/to-code_developer-priority-42.json", message)

   # Code developer checks for messages
   messages = Glob("data/messages/to-code_developer-*.json")
   ```

2. **Agent Pause/Resume**: Store agent state in database, kill, restart later
   ```python
   # Save state
   Write("data/agent_state/code_developer_42.json", state)

   # Kill agent
   kill_agent(task_id="impl-42")

   # Resume later with state
   spawn_code_developer(priority=42, resume_from_state=True)
   ```

3. **Bidirectional Control Channel**: Use subprocess.stdin for dynamic instructions
   ```python
   # Send instruction to running agent
   agent_process.stdin.write("PAUSE\n")
   agent_process.stdin.write("CHECK_ROADMAP\n")
   agent_process.stdin.write("RESUME\n")
   ```

---

## Summary

### Communication Flow

```
Orchestrator (Python)
    │
    ├─> Spawns Claude session with prompt (one-way)
    │
    ├─< Receives streaming messages (real-time)
    │   ├─ Agent thoughts
    │   ├─ Tool usage
    │   └─ Final result
    │
    ├─< Reads agent deliverables from files
    │   ├─ Specs (architect)
    │   ├─ Code (code_developer)
    │   └─ Reports (project_manager)
    │
    └─< Queries databases for status
        ├─ claude_invocations.db (invocation history)
        └─ orchestrator.db (agent lifecycle)
```

### Key Takeaways

- ✅ **Orchestrator → Agent**: Via initial prompt (one-way)
- ✅ **Agent → Orchestrator**: Via streaming messages (real-time)
- ✅ **Agent → Database**: Automatic tracking by invoker
- ✅ **Agent → Files**: Direct tool usage (Write, Edit)
- ✅ **Agent ← → Orchestrator**: Via lifecycle database
- ❌ **Agent ← → Agent**: No direct communication (must go through orchestrator or files)

---

**Result**: Full observability, clear coordination, persistent tracking - all without agents being Python processes!

**Status**: ✅ Implemented in `.claude/skills/shared/orchestrator_agent_management/agent_management.py`
**Last Updated**: 2025-10-26
