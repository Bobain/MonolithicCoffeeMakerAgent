# Final Architecture: All Agents ARE Claude Code Sub-Agents

**Principle**: There is no difference between an "autonomous agent" and a "sub-agent". They are all Claude Code sessions. Only the orchestrator stays running.

---

## Architecture

```
Orchestrator (Python - stays running)
  │
  ├─> Spawns: code-developer (Claude Code session)
  │     └─> Uses: Read, Write, Edit, Bash
  │     └─> Implements priority
  │     └─> Exits when done
  │
  ├─> Spawns: architect (Claude Code session)
  │     └─> Uses: Read, Write, Edit
  │     └─> Creates spec
  │     └─> Exits when done
  │
  └─> Spawns: project-manager (Claude Code session)
        └─> Uses: Read, Bash (gh)
        └─> Updates roadmap
        └─> Exits when done
```

**Key Points**:
- ✅ All agents are Claude Code sessions (no Python agent classes)
- ✅ Agents use tools directly (Read, Write, Edit, Bash)
- ✅ Agents exit when done
- ✅ Orchestrator spawns agents as needed
- ✅ Orchestrator is the only persistent process

---

## Implementation

### What We Already Have ✅

1. **`ClaudeAgentInvoker`** - Can spawn Claude Code sessions
2. **`.claude/agents/*.md`** - Agent prompts already defined
3. **Database tracking** - All invocations tracked

### What Changes

**Before** (What we just built):
```python
# code_developer_agent.py - Python class that calls Claude
class CodeDeveloperAgent(BaseAgent):
    def _implement_priority(self, priority):
        result = self.invoker.invoke_agent("code-developer", prompt)
```

**After** (Final architecture):
```python
# No code_developer_agent.py!
# Orchestrator spawns Claude directly:

orchestrator.spawn_agent(
    agent_type="code-developer",
    task={
        "type": "implement_priority",
        "priority_id": "US-042"
    }
)

# Claude Code session runs, uses tools, exits
```

---

## Orchestrator Responsibilities

The orchestrator is the **only Python process** that stays running. It:

1. **Monitors Work Queue**
   - Checks `docs/roadmap/ROADMAP.md` for planned priorities
   - Checks `data/messages/` for inter-agent messages
   - Checks GitHub for PR status

2. **Spawns Agents as Needed**
   - Priority needs spec → Spawn architect
   - Spec ready → Spawn code-developer
   - Implementation done → Spawn project-manager for verification

3. **Tracks Agent Execution**
   - Database: `data/claude_invocations.db`
   - Logs: Real-time streaming
   - Status: `data/agent_status/`

4. **Handles Failures**
   - Agent crashes → Retry with different approach
   - Agent stuck → Timeout and move to next task
   - Dependencies missing → Spawn dependency agent first

---

## Example: Implementing a Priority

### Old Way (Python Agents):
```python
# code_developer_agent.py runs continuously
while True:
    priority = get_next_planned()
    if not find_spec(priority):
        send_message_to_architect()
        continue

    # Call Claude
    result = self.invoker.invoke_agent("code-developer", prompt)

    commit_changes()
    sleep(300)
```

### New Way (Orchestrator + Claude Sessions):
```python
# orchestrator.py - stays running
while True:
    priority = get_next_planned()

    # Check if spec exists
    if not spec_exists(priority):
        # Spawn architect as Claude session
        spawn_agent(
            agent_type="architect",
            task={"type": "create_spec", "priority": priority}
        )
        # Architect session runs, creates spec, exits
        wait_for_agent_completion()

    # Spawn code-developer as Claude session
    spawn_agent(
        agent_type="code-developer",
        task={"type": "implement", "priority": priority}
    )
    # Code-developer session runs, implements, commits, exits
    wait_for_agent_completion()

    sleep(60)
```

---

## Orchestrator Implementation

```python
# coffee_maker/orchestrator/claude_orchestrator.py

from coffee_maker.claude_agent_invoker import get_invoker
from pathlib import Path

class ClaudeOrchestrator:
    """Orchestrator that spawns Claude Code sub-agents as needed.

    This is the ONLY persistent process. All work is done by
    Claude Code sessions that are spawned and exit.
    """

    def __init__(self):
        self.invoker = get_invoker()
        self.roadmap_db = RoadmapDatabase("orchestrator")

    def run_continuous(self):
        """Main orchestrator loop."""
        logger.info("🎯 Orchestrator starting...")

        while True:
            try:
                # Check for work
                work = self.find_work()

                if not work:
                    logger.info("😴 No work found, sleeping...")
                    time.sleep(60)
                    continue

                # Dispatch work to appropriate agent
                self.dispatch_work(work)

            except KeyboardInterrupt:
                logger.info("🛑 Shutting down...")
                break
            except Exception as e:
                logger.error(f"❌ Orchestrator error: {e}")
                time.sleep(30)

    def find_work(self) -> Optional[Dict]:
        """Find next work item."""
        # Check roadmap for planned priorities
        next_priority = self.roadmap_db.get_next_planned()

        if next_priority:
            return {
                "type": "implement_priority",
                "priority": next_priority
            }

        # Check for spec requests
        spec_requests = self.check_spec_requests()
        if spec_requests:
            return {
                "type": "create_spec",
                "request": spec_requests[0]
            }

        return None

    def dispatch_work(self, work: Dict):
        """Dispatch work to appropriate Claude Code sub-agent."""
        work_type = work["type"]

        if work_type == "implement_priority":
            self.spawn_code_developer(work["priority"])

        elif work_type == "create_spec":
            self.spawn_architect(work["request"])

    def spawn_code_developer(self, priority: Dict):
        """Spawn code-developer Claude Code session to implement priority.

        The session will:
        1. Read the spec
        2. Implement the feature
        3. Run tests
        4. Commit changes
        5. Exit
        """
        priority_id = priority["id"]
        logger.info(f"🚀 Spawning code-developer for {priority_id}")

        # Find spec
        spec_file = self.find_spec(priority)
        if not spec_file:
            logger.error(f"No spec for {priority_id}, spawning architect first...")
            self.spawn_architect(priority)
            return

        spec_content = spec_file.read_text()

        # Build prompt
        prompt = f\"\"\"
Implement {priority_id}: {priority.get('title', '')}

## Spec

{spec_content}

## Task

1. Use Read tool to understand existing code
2. Use Write/Edit tools to implement the feature
3. Use Bash tool to run: pytest
4. If tests pass: Use Bash to commit: git add . && git commit -m "feat: {priority_id}"
5. Report "COMPLETE: {priority_id} implemented"

Start now. When done, exit.
\"\"\"

        # Spawn Claude session
        for msg in self.invoker.invoke_agent_streaming(
            agent_type="code-developer",
            prompt=prompt,
            timeout=3600
        ):
            self.log_agent_message("code-developer", msg)

        logger.info(f"✅ code-developer completed {priority_id}")

    def spawn_architect(self, priority: Dict):
        """Spawn architect Claude Code session to create spec."""
        priority_id = priority["id"]
        logger.info(f"🏗️  Spawning architect for spec: {priority_id}")

        prompt = f\"\"\"
Create technical specification for {priority_id}: {priority.get('title', '')}

## Priority Description

{priority.get('description', '')}

## Task

1. Use Read tool to understand existing architecture
2. Design the solution
3. Use Write tool to create: docs/architecture/specs/SPEC-XXX-{priority_id}.md
4. Include: problem statement, solution, implementation steps, testing, DoD
5. Report "COMPLETE: Spec created"

Start now. When done, exit.
\"\"\"

        for msg in self.invoker.invoke_agent_streaming(
            agent_type="architect",
            prompt=prompt,
            timeout=600
        ):
            self.log_agent_message("architect", msg)

        logger.info(f"✅ architect completed spec for {priority_id}")
```

---

## Migration Path

### Step 1: Keep Orchestrator, Remove Agent Classes

```bash
# Delete Python agent classes (they're now Claude sessions)
git rm coffee_maker/autonomous/agents/code_developer_agent.py
git rm coffee_maker/autonomous/agents/architect_agent.py

# Keep orchestrator (the only Python code that stays running)
# Orchestrator now uses ClaudeAgentInvoker to spawn Claude sessions
```

### Step 2: Update Orchestrator to Spawn Claude Sessions

```python
# coffee_maker/orchestrator/continuous_work_loop.py

class ContinuousWorkLoop:
    def __init__(self):
        self.invoker = get_invoker()  # Spawns Claude sessions

    def run(self):
        while True:
            priority = self.get_next_priority()

            # Spawn Claude session (not Python agent!)
            self.invoker.invoke_agent_streaming(
                "code-developer",
                f"Implement {priority['id']}"
            )
```

---

## Benefits

### 1. Simplicity
- ❌ No more Python agent classes
- ❌ No more BaseAgent inheritance
- ❌ No more agent mixins
- ✅ Just: Orchestrator + Claude sessions

### 2. Power
- ✅ Agents have full Claude Code capabilities
- ✅ Native tool access (Read, Write, Edit, Bash)
- ✅ Better prompts (use full `.claude/agents/*.md`)
- ✅ Claude manages its own logic

### 3. Debugging
- ✅ All invocations in database
- ✅ Streaming messages preserved
- ✅ Dashboard shows all agent activity
- ✅ Easy to replay/analyze

---

## Summary

### Before (Complex):
```
Python Agents (code_developer_agent.py, etc.)
  └─> Call Claude via invoker
      └─> Claude does work
          └─> Returns to Python
              └─> Python commits, loops, etc.
```

### After (Simple):
```
Orchestrator (Python - stays running)
  └─> Spawns Claude session
      └─> Claude does ALL the work (tools, commits, everything)
          └─> Exits when done
              └─> Orchestrator spawns next agent
```

**Result**: Agents ARE Claude Code sessions. No Python wrappers. Orchestrator just coordinates.

---

## Next Steps

Shall I:
1. **Update orchestrator** to spawn Claude sessions instead of Python agents?
2. **Remove Python agent classes** (code_developer_agent.py, etc.)?
3. **Test with a simple priority** to verify it works end-to-end?

This is the true "agents as Claude sessions" architecture!
