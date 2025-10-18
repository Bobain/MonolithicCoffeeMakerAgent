"""
POC-072: Team Daemon (Minimal Implementation)

Master daemon that orchestrates multiple agent subprocesses.
This is a MINIMAL POC to prove core concepts work.

Usage:
    python team_daemon.py
"""

import signal
import time
from typing import Dict

from agent_process import AgentProcess
from message_queue import AgentType, MessageQueue


class TeamDaemon:
    """Master daemon that orchestrates all autonomous agents.

    This is a MINIMAL implementation for POC purposes.
    Production version would have much more sophisticated coordination.
    """

    def __init__(self):
        self.agents: Dict[AgentType, AgentProcess] = {}
        self.message_queue = MessageQueue()
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n🛑 Received shutdown signal, stopping...")
        self.stop()

    def start(self) -> None:
        """Start all agents and begin orchestration."""
        print("🚀 Starting team daemon POC...")

        # Spawn 2 dummy agents
        for agent_type in [AgentType.AGENT_1, AgentType.AGENT_2]:
            self._spawn_agent(agent_type)

        # Start coordination loop
        self.running = True
        print("✅ Team daemon started, agents running...")
        print("Press Ctrl+C to stop")
        self._coordination_loop()

    def _spawn_agent(self, agent_type: AgentType) -> None:
        """Spawn subprocess for specific agent."""
        print(f"Spawning {agent_type.value}...")

        process = AgentProcess(
            agent_type=agent_type,
            message_queue=self.message_queue,
        )
        process.start()
        self.agents[agent_type] = process

        print(f"✅ {agent_type.value} started (PID: {process.pid})")

    def _coordination_loop(self) -> None:
        """Main coordination loop (runs continuously)."""
        while self.running:
            try:
                # Check agent health every 2 seconds
                self._check_agent_health()

                # Sleep
                time.sleep(2)

            except KeyboardInterrupt:
                print("\nReceived Ctrl+C, shutting down...")
                self.stop()
                break
            except Exception as e:
                print(f"Error in coordination loop: {e}")
                # Continue running - don't crash master daemon

    def _check_agent_health(self) -> None:
        """Check health of all agent subprocesses."""
        for agent_type, process in self.agents.items():
            if not process.is_alive():
                print(f"❌ {agent_type.value} agent crashed!")

                # Auto-restart (max 3 retries)
                if process.restart_count < 3:
                    print(f"Auto-restarting {agent_type.value} (attempt {process.restart_count + 1}/3)...")
                    process.restart_count += 1
                    self._spawn_agent(agent_type)
                else:
                    print(f"Max retries reached for {agent_type.value}, giving up")
                    # In production, would notify user here

    def stop(self) -> None:
        """Gracefully stop all agents and shutdown."""
        print("🛑 Stopping team daemon...")

        self.running = False

        # Stop all agents
        for agent_type, process in self.agents.items():
            process.stop(timeout=5)

        # Stop message queue
        self.message_queue.stop()

        print("✅ Team daemon stopped successfully")

    def status(self) -> dict:
        """Get current status of all agents."""
        return {
            agent_type.value: {
                "pid": process.pid,
                "is_alive": process.is_alive(),
                "uptime": process.uptime(),
                "restart_count": process.restart_count,
            }
            for agent_type, process in self.agents.items()
        }


def main():
    """Main entry point."""
    daemon = TeamDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
