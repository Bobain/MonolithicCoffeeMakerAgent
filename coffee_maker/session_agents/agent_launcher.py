"""Agent Launcher - Spawns autonomous agents as long-running Claude Code sessions.

This module implements the architecture where agents ARE Claude Code sessions,
not Python processes that call Claude.

Architecture:
    Each agent runs as a persistent Claude Code session with:
    - Full tool access (Read, Write, Edit, Bash)
    - Continuous loop logic in the prompt
    - Auto-restart on failure
    - Heartbeat monitoring

Usage:
    python -m coffee_maker.session_agents.agent_launcher --agent code-developer

    # Or launch all agents
    python -m coffee_maker.session_agents.agent_launcher --all
"""

import json
import logging
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from threading import Thread

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AgentSessionLauncher:
    """Launches and monitors autonomous agents as Claude Code sessions.

    Each agent runs as a persistent Claude session that:
    1. Loads its prompt from .claude/agents/{agent_type}.md
    2. Executes a continuous work loop
    3. Uses tools (Read, Write, Edit, Bash) directly
    4. Manages its own state via files
    5. Auto-restarts on failure

    Example:
        >>> launcher = AgentSessionLauncher()
        >>> launcher.launch_agent("code-developer")
        🚀 Starting code-developer as Claude Code session...
        💬 Reading roadmap...
        🔧 Using tool: Read
        ...
    """

    def __init__(
        self,
        claude_path: str = "/opt/homebrew/bin/claude",
        heartbeat_dir: Path = Path("data/heartbeats"),
        restart_on_exit: bool = True,
        restart_delay: int = 10,
    ):
        """Initialize agent launcher.

        Args:
            claude_path: Path to claude CLI
            heartbeat_dir: Directory for agent heartbeat files
            restart_on_exit: Auto-restart agents when they exit
            restart_delay: Seconds to wait before restart
        """
        self.claude_path = Path(claude_path)
        self.heartbeat_dir = heartbeat_dir
        self.restart_on_exit = restart_on_exit
        self.restart_delay = restart_delay

        # Create directories
        self.heartbeat_dir.mkdir(parents=True, exist_ok=True)

        # Track running sessions
        self.running_sessions = {}

        # Shutdown flag
        self.shutdown = False

        if not self.claude_path.exists():
            raise RuntimeError(f"Claude CLI not found at {claude_path}")

        logger.info("✅ AgentSessionLauncher initialized")

    def launch_agent(self, agent_type: str):
        """Launch an agent as a long-running Claude Code session.

        The agent runs continuously until stopped or crashed.
        If restart_on_exit=True, will restart automatically.

        Args:
            agent_type: Agent to launch (code-developer, architect, etc.)
        """
        logger.info(f"🚀 Launching {agent_type} as Claude Code session...")

        # Build continuous loop prompt
        prompt = self._build_continuous_prompt(agent_type)

        # Launch loop (with auto-restart)
        restart_count = 0

        while not self.shutdown:
            try:
                session_start = time.time()

                logger.info(f"📍 Starting {agent_type} session (restart #{restart_count})")

                # Start Claude process
                proc = subprocess.Popen(
                    [
                        str(self.claude_path),
                        "--print",
                        "--output-format",
                        "stream-json",
                        "--permission-mode",
                        "acceptEdits",
                        prompt,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                # Track session
                self.running_sessions[agent_type] = {
                    "pid": proc.pid,
                    "started_at": datetime.utcnow().isoformat(),
                    "restart_count": restart_count,
                }

                # Monitor output
                for line in proc.stdout:
                    if not line.strip():
                        continue

                    try:
                        msg = json.loads(line)
                        self._handle_session_message(agent_type, msg)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse: {line[:100]}")

                # Process ended
                proc.wait()
                exit_code = proc.returncode

                session_duration = time.time() - session_start
                logger.warning(
                    f"⚠️  {agent_type} session ended (exit_code={exit_code}, " f"duration={session_duration:.0f}s)"
                )

                # Check if should restart
                if not self.restart_on_exit or self.shutdown:
                    logger.info(f"🛑 Not restarting {agent_type} (restart_on_exit=False or shutdown)")
                    break

                # Restart with delay
                restart_count += 1
                logger.info(f"🔄 Restarting {agent_type} in {self.restart_delay}s...")
                time.sleep(self.restart_delay)

            except Exception as e:
                logger.error(f"❌ {agent_type} session crashed: {e}", exc_info=True)

                if not self.restart_on_exit or self.shutdown:
                    break

                restart_count += 1
                logger.info(f"🔄 Restarting {agent_type} in {self.restart_delay * 2}s after crash...")
                time.sleep(self.restart_delay * 2)

        # Cleanup
        if agent_type in self.running_sessions:
            del self.running_sessions[agent_type]

        logger.info(f"✅ {agent_type} session terminated")

    def _build_continuous_prompt(self, agent_type: str) -> str:
        """Build prompt that makes Claude run continuously as an agent.

        Args:
            agent_type: Agent type

        Returns:
            Prompt string with continuous loop logic
        """
        # Load base agent prompt from .claude/agents/
        agent_prompt_file = Path(f".claude/agents/{agent_type}.md")

        if agent_prompt_file.exists():
            base_prompt = agent_prompt_file.read_text()
        else:
            logger.warning(f"No agent file found: {agent_prompt_file}, using minimal prompt")
            base_prompt = f"You are the {agent_type} agent."

        # Add continuous loop instructions
        continuous_prompt = f"""{base_prompt}

---

## CONTINUOUS OPERATION MODE

You are running as an autonomous agent in continuous mode. This means:

1. **You control your own loop** - After completing work, immediately check for more
2. **Never exit** - Keep running until explicitly stopped
3. **Use tools directly** - You have Read, Write, Edit, Bash tools
4. **Manage state via files** - Use data/agent_status/{agent_type}_state.json
5. **Write heartbeats** - Update data/heartbeats/{agent_type}.json every iteration

## Main Loop

Execute this loop continuously:

### Step 1: Update Heartbeat
```
Use Write tool to create/update: data/heartbeats/{agent_type}.json
Content: {{"agent": "{agent_type}", "timestamp": "<current_time>", "status": "running"}}
```

### Step 2: Check for Work
- For code-developer: Read docs/roadmap/ROADMAP.md, find next "📝 Planned" priority
- For architect: Check data/messages/ for spec_request_*.json files
- For project-manager: Check roadmap health, GitHub PRs, notifications

### Step 3: Do the Work
Use appropriate tools:
- Read: Read files
- Write: Create new files
- Edit: Modify existing files
- Bash: Run commands (pytest, git, etc.)

### Step 4: Report Progress
Output progress messages:
- "PROGRESS: <what you're doing>"
- "TOOL_USE: <tool_name>"
- "COMPLETE: <what you completed>"

### Step 5: Sleep Briefly
After completing work:
- Output: "LOOP_COMPLETE: Waiting for next iteration"
- Immediately continue to Step 1 (you can't actually sleep, just continue the loop)

## Critical Rules

1. **NEVER EXIT**: Keep looping forever
2. **TOOL USAGE**: Always use tools (Read/Write/Edit/Bash), never just describe
3. **ERROR HANDLING**: If something fails, log it and continue to next iteration
4. **STATE PERSISTENCE**: Save your state before each iteration
5. **HEARTBEAT**: Update heartbeat every loop so monitor knows you're alive

## Start Now

Begin your continuous loop. Start with Step 1 (update heartbeat), then check for work.
"""

        return continuous_prompt

    def _handle_session_message(self, agent_type: str, msg: dict):
        """Handle streaming message from agent session.

        Args:
            agent_type: Agent type
            msg: Streaming message dict
        """
        msg_type = msg.get("type", "unknown")

        if msg_type == "init":
            logger.info(f"🎬 {agent_type}: Session initialized")

        elif msg_type == "message":
            content = msg.get("content", "")
            # Log agent messages
            logger.info(f"💬 {agent_type}: {content[:200]}")

            # Check for special markers
            if "PROGRESS:" in content:
                logger.info(f"📊 {agent_type}: {content}")
            elif "ERROR:" in content:
                logger.error(f"❌ {agent_type}: {content}")
            elif "COMPLETE:" in content:
                logger.info(f"✅ {agent_type}: {content}")

        elif msg_type == "tool_use":
            tool_name = msg.get("name", "unknown")
            logger.info(f"🔧 {agent_type}: Using tool: {tool_name}")

        elif msg_type == "tool_result":
            pass  # Too verbose, skip

        elif msg_type == "result":
            logger.info(f"🏁 {agent_type}: Session result received")
            tokens_in = msg.get("input_tokens", 0)
            tokens_out = msg.get("output_tokens", 0)
            cost = msg.get("total_cost_usd", 0)
            logger.info(f"📊 {agent_type}: Tokens: {tokens_in} in, {tokens_out} out, ${cost:.4f}")

    def launch_all_agents(self):
        """Launch all agents in parallel threads."""
        agents = ["code-developer", "architect", "project-manager"]

        threads = []
        for agent in agents:
            logger.info(f"🚀 Starting {agent} in background thread...")
            thread = Thread(target=self.launch_agent, args=(agent,), daemon=True)
            thread.start()
            threads.append(thread)
            time.sleep(2)  # Stagger starts

        logger.info(f"✅ All {len(agents)} agents started")

        # Wait for all threads
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested...")
            self.shutdown = True
            # Give threads time to clean up
            time.sleep(5)

    def stop_agent(self, agent_type: str):
        """Stop a running agent session.

        Args:
            agent_type: Agent to stop
        """
        if agent_type not in self.running_sessions:
            logger.warning(f"{agent_type} not running")
            return

        session = self.running_sessions[agent_type]
        pid = session["pid"]

        logger.info(f"🛑 Stopping {agent_type} (PID {pid})...")

        try:
            import os

            os.kill(pid, signal.SIGTERM)
            logger.info(f"✅ Sent SIGTERM to {agent_type}")
        except Exception as e:
            logger.error(f"Failed to stop {agent_type}: {e}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Launch autonomous agents as Claude Code sessions")
    parser.add_argument("--agent", type=str, help="Agent to launch (code-developer, architect, etc.)")
    parser.add_argument("--all", action="store_true", help="Launch all agents")
    parser.add_argument("--no-restart", action="store_true", help="Don't auto-restart on exit")

    args = parser.parse_args()

    launcher = AgentSessionLauncher(restart_on_exit=not args.no_restart)

    if args.all:
        launcher.launch_all_agents()
    elif args.agent:
        launcher.launch_agent(args.agent)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
