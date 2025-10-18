"""
POC-072: Agent Process Wrapper

Minimal wrapper for agent subprocess with health monitoring.
Each agent runs in isolated subprocess.
"""

import multiprocessing
import time
from datetime import datetime
from typing import Optional

from message_queue import AgentType, Message, MessageQueue, MessageType


class AgentProcess:
    """Wrapper for agent subprocess.

    Provides lifecycle management and inter-process communication.
    This is a MINIMAL implementation for POC purposes.
    """

    def __init__(
        self,
        agent_type: AgentType,
        message_queue: MessageQueue,
    ):
        self.agent_type = agent_type
        self.message_queue = message_queue
        self.process: Optional[multiprocessing.Process] = None
        self.restart_count = 0
        self.start_time: Optional[datetime] = None

    def start(self) -> None:
        """Start agent subprocess."""
        self.process = multiprocessing.Process(
            target=self._run_agent,
            name=f"agent-{self.agent_type.value}",
        )
        self.process.start()
        self.start_time = datetime.now()
        print(f"[AgentProcess] {self.agent_type.value} started (PID: {self.process.pid})")

    def _run_agent(self) -> None:
        """Agent main loop (runs in subprocess).

        This is a DUMMY implementation that just sends/receives messages.
        Production version would run actual agent logic.
        """
        print(f"[{self.agent_type.value}] Agent started in subprocess")

        # Determine other agent (for demo)
        other_agent = AgentType.AGENT_2 if self.agent_type == AgentType.AGENT_1 else AgentType.AGENT_1

        # Main loop
        iteration = 0
        while True:
            try:
                # Send a message every 2 seconds
                if iteration % 2 == 0:
                    message = Message(
                        sender=self.agent_type,
                        recipient=other_agent,
                        type=MessageType.SIMPLE_MESSAGE,
                        payload=f"Hello from {self.agent_type.value} (iter {iteration})",
                        priority=5,
                    )
                    self.message_queue.send(message)

                # Check for incoming messages
                msg = self.message_queue.get(self.agent_type, timeout=0.1)
                if msg:
                    print(f"[{self.agent_type.value}] Received message: {msg.payload}")

                # Sleep a bit
                time.sleep(1)
                iteration += 1

                # Stop after 10 iterations (for POC demo)
                if iteration >= 10:
                    print(f"[{self.agent_type.value}] Completed 10 iterations, exiting...")
                    break

            except KeyboardInterrupt:
                print(f"[{self.agent_type.value}] Received interrupt, exiting...")
                break
            except Exception as e:
                print(f"[{self.agent_type.value}] Error: {e}")
                break

        print(f"[{self.agent_type.value}] Agent subprocess exiting")

    def is_alive(self) -> bool:
        """Check if agent subprocess is alive."""
        return self.process is not None and self.process.is_alive()

    def stop(self, timeout: int = 5) -> None:
        """Stop agent subprocess gracefully.

        Args:
            timeout: Max seconds to wait for graceful exit
        """
        if self.process is not None:
            print(f"[AgentProcess] Stopping {self.agent_type.value}...")
            self.process.terminate()  # Send SIGTERM
            self.process.join(timeout=timeout)

            if self.process.is_alive():
                # Force kill if didn't exit gracefully
                print(f"[AgentProcess] Force killing {self.agent_type.value}...")
                self.process.kill()

    @property
    def pid(self) -> Optional[int]:
        """Get process ID."""
        return self.process.pid if self.process else None

    def uptime(self) -> float:
        """Get uptime in seconds."""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
