# Architecture: Autonomous Agents AS Claude Code Sessions

**Concept**: Instead of Python agents that call Claude, the agents **ARE** Claude Code sessions running continuously.

---

## Current Architecture (What We Just Built)

```
Python Agent (code_developer_agent.py)
  └─> Spawns Claude Code sub-agent
      └─> Claude has tools (Read, Write, Edit, Bash)
```

**Problem**: Python agent is still the coordinator. You want the agent **to BE** Claude.

---

## New Architecture (What You Want)

```
claude --print (running as daemon)
  ├─> Loads .claude/agents/code_developer.md
  ├─> Has full tool access (Read, Write, Edit, Bash)
  ├─> Runs continuous loop
  └─> Never exits
```

**Result**: The agent **IS** a Claude Code session. No Python wrapper.

---

## Implementation Strategy

### Option 1: Long-Running Claude Sessions

Spawn Claude Code with a prompt that runs forever:

```bash
# Start code-developer agent
claude --print \
  --agents '{"code-developer": {"description": "Continuous implementation agent"}}' \
  "You are the code-developer agent. Run continuously:

1. Read docs/roadmap/ROADMAP.md
2. Find next planned priority
3. Check if spec exists (in docs/architecture/specs/)
4. If no spec: STOP and report 'Waiting for spec'
5. If spec exists: Implement the priority
6. Run tests (pytest)
7. Commit changes
8. LOOP back to step 1

IMPORTANT: This is a continuous loop. After completing a priority, immediately check for the next one. Never exit.

Start now."
```

**Benefits**:
- ✅ Agent **IS** Claude Code
- ✅ Full tool access natively
- ✅ No Python wrapper needed
- ✅ True autonomous operation

**Challenges**:
- ❌ How to keep session alive indefinitely?
- ❌ How to handle Claude timeouts?
- ❌ How to restart on failure?

### Option 2: Orchestrator That Spawns Long-Running Sessions

A lightweight Python orchestrator that launches and monitors Claude sessions:

```python
# coffee_maker/claude_session_manager.py

class ClaudeSessionManager:
    """Manages long-running Claude Code sessions as agents."""

    def spawn_agent(self, agent_type: str):
        """Spawn a Claude Code session that runs as an autonomous agent.

        The session runs the agent's .claude/agents/{agent_type}.md prompt
        in a continuous loop.
        """
        prompt = self._build_continuous_loop_prompt(agent_type)

        # Start Claude in background with continuous prompt
        proc = subprocess.Popen(
            [
                "claude",
                "--print",
                "--output-format", "stream-json",
                prompt
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Monitor output
        for line in proc.stdout:
            msg = json.loads(line)
            self._handle_agent_message(agent_type, msg)

    def _build_continuous_loop_prompt(self, agent_type: str):
        """Build prompt that makes Claude run continuously."""
        return f"""
You are the {agent_type} agent running continuously.

AGENT LOOP:
1. Check for work (read ROADMAP.md)
2. If work exists: Do the work
3. If no work: Sleep 5 minutes
4. GOTO step 1

CRITICAL: You must loop forever. After completing a task, immediately check for the next one.

Tools available:
- Read: Read any file
- Write: Create new files
- Edit: Modify existing files
- Bash: Run commands

Start the loop now.
"""
```

### Option 3: Session-Based Agent Framework (Recommended)

Create a framework where agents are Claude Code sessions:

```
coffee_maker/
├── session_agents/
│   ├── agent_launcher.py          # Spawns Claude sessions
│   ├── agent_monitor.py           # Monitors session health
│   ├── session_prompts/
│   │   ├── code_developer_loop.md # Continuous loop prompt
│   │   ├── architect_loop.md      # Continuous loop prompt
│   │   └── project_manager_loop.md
│   └── session_config.json        # Agent session configs
```

**Agent Launcher**:
```python
class AgentLauncher:
    def launch_code_developer(self):
        """Launch code-developer as Claude Code session."""
        session_prompt = Path("session_prompts/code_developer_loop.md").read_text()

        # Start session
        self.start_claude_session(
            agent_type="code-developer",
            prompt=session_prompt,
            check_interval=300,  # 5 minutes
            restart_on_exit=True
        )

    def start_claude_session(self, agent_type, prompt, check_interval, restart_on_exit):
        """Start a Claude Code session in daemon mode."""
        while True:
            try:
                # Spawn Claude
                proc = subprocess.Popen(
                    ["claude", "--print", "--output-format", "stream-json", prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # Monitor
                for line in proc.stdout:
                    self.log_message(agent_type, line)

                # If we get here, session ended
                if not restart_on_exit:
                    break

                logger.warning(f"{agent_type} session ended, restarting in 10s...")
                time.sleep(10)

            except Exception as e:
                logger.error(f"{agent_type} crashed: {e}")
                time.sleep(30)
```

**Session Prompt Template** (code_developer_loop.md):
```markdown
# Code Developer Agent - Continuous Loop

You are the autonomous code-developer agent. Run this loop continuously:

## Main Loop

1. **Read Roadmap**
   - Use Read tool: `Read docs/roadmap/ROADMAP.md`
   - Parse for next "📝 Planned" priority

2. **Check Spec Exists**
   - Use Glob tool: `Glob docs/architecture/specs/SPEC-{priority_number}-*.md`
   - If no spec found: STOP and output "WAITING_FOR_SPEC: {priority_id}"
   - If spec exists: Continue

3. **Implement Priority**
   - Read spec file
   - Use Write/Edit tools to implement
   - Use Bash to run tests: `pytest`
   - If tests fail: Fix and retry
   - If tests pass: Continue

4. **Commit Changes**
   - Use Bash: `git add .`
   - Use Bash: `git commit -m "feat: Implement {priority_id}"`
   - Use Bash: `git push`

5. **Update Roadmap**
   - Use Edit tool to mark priority as "✅ Complete"
   - Save changes

6. **Sleep**
   - Output: "LOOP_COMPLETE: Sleeping 5 minutes"
   - Wait 5 minutes (you can't actually sleep, so just say you're ready for next iteration)

7. **REPEAT FROM STEP 1**

## Critical Rules

- NEVER exit this loop
- Always use tools (Read, Write, Edit, Bash)
- If stuck: Output "ERROR: {description}" and continue to next priority
- Track progress by outputting "PROGRESS: {step}"

## Start Now

Begin the loop. Read the roadmap and find the first planned priority.
```

---

## Comparison

### Python Agents (Current)
```python
# code_developer_agent.py runs as Python process
class CodeDeveloperAgent:
    def _do_background_work(self):
        priority = self.roadmap.get_next_planned()
        result = self.invoker.invoke_agent("code-developer", prompt)
        # Python controls the loop
```

### Claude Session Agents (New)
```bash
# Claude Code runs directly as the agent
claude --print "You are code-developer agent. Loop:
1. Read roadmap
2. Implement priority
3. Commit
4. Repeat forever"

# Claude controls its own loop
```

---

## Advantages of Claude-As-Agent

1. **Native Tool Access**
   - Claude uses Read/Write/Edit/Bash directly
   - No API wrapper overhead
   - Full Claude Code capabilities

2. **True Autonomy**
   - Claude decides when to loop
   - Claude manages its own state
   - No Python orchestration

3. **Simpler Architecture**
   - No Python agent classes needed
   - Just session prompts + launcher
   - Easier to understand

4. **Better Prompts**
   - Use full `.claude/agents/*.md` prompts
   - More natural for Claude
   - Leverage Claude Code's design

---

## Challenges to Solve

### 1. Session Persistence
**Problem**: Claude sessions eventually timeout or exit.

**Solution**: Launcher restarts sessions automatically:
```python
def keep_alive(agent_type):
    while True:
        start_session(agent_type)
        logger.warning(f"{agent_type} session ended, restarting...")
```

### 2. State Management
**Problem**: How does Claude remember what it was doing?

**Solution**: Claude reads state from files:
```markdown
# In session prompt
"Check data/agent_status/code_developer_state.json for your last state.
If file exists, resume from there. Otherwise, start fresh."
```

### 3. Inter-Agent Communication
**Problem**: How do agents talk to each other?

**Solution**: File-based message passing:
```markdown
# Architect session
"When spec is ready, write: data/messages/spec_ready_{priority_id}.json"

# Code-developer session
"Check data/messages/ for spec_ready_*.json files"
```

### 4. Monitoring
**Problem**: How to know if agent is healthy?

**Solution**: Heartbeat files:
```markdown
# In session prompt
"Every 5 minutes, update data/heartbeats/code_developer.json with current timestamp"
```

---

## Recommended Implementation

### Phase 1: Single Agent Prototype

Create a launcher for just code-developer:

```python
# launch_code_developer_session.py

from coffee_maker.claude_agent_invoker import get_invoker
from pathlib import Path

def launch_code_developer_as_session():
    """Launch code-developer as a persistent Claude Code session."""

    # Load the continuous loop prompt
    loop_prompt = Path("session_prompts/code_developer_loop.md").read_text()

    invoker = get_invoker()

    print("🚀 Starting code-developer agent as Claude Code session...")

    # Use streaming to monitor the agent
    for msg in invoker.invoke_agent_streaming(
        agent_type="code-developer",
        prompt=loop_prompt,
        timeout=86400  # 24 hours
    ):
        # Log all agent activity
        if msg.message_type == "message":
            print(f"💬 {msg.content}")
        elif msg.message_type == "tool_use":
            print(f"🔧 Using: {msg.metadata.get('name')}")
        elif msg.message_type == "result":
            print(f"⚠️  Session ended - should restart")
            break
```

### Phase 2: Full Multi-Agent System

Create launchers for all agents with restart logic:

```python
# coffee_maker/session_agents/multi_agent_launcher.py

class MultiAgentLauncher:
    def start_all_agents(self):
        """Start all agents as Claude Code sessions."""
        agents = [
            "code-developer",
            "architect",
            "project-manager"
        ]

        # Start each in separate thread
        for agent in agents:
            thread = Thread(target=self.launch_agent, args=(agent,))
            thread.daemon = True
            thread.start()

    def launch_agent(self, agent_type):
        """Launch and monitor single agent session."""
        while True:  # Restart loop
            try:
                self._run_agent_session(agent_type)
            except Exception as e:
                logger.error(f"{agent_type} crashed: {e}")
                time.sleep(30)
```

---

## Next Steps

Would you like me to:

1. **Create the session launcher** that runs agents as Claude Code sessions?
2. **Write the continuous loop prompts** for each agent type?
3. **Build the monitoring/restart system** to keep sessions alive?
4. **Implement file-based state management** for session persistence?

Let me know which approach you prefer and I'll implement it!
