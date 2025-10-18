"""
POC-072: Message Queue (In-Memory Implementation)

Minimal message queue for inter-agent communication.
Uses multiprocessing.Queue for simplicity (production would use SQLite/Redis).
"""

import multiprocessing
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import heapq


class AgentType(Enum):
    """Agent types."""

    AGENT_1 = "agent_1"
    AGENT_2 = "agent_2"


class MessageType(Enum):
    """Message types."""

    SIMPLE_MESSAGE = "simple_message"


@dataclass
class Message:
    """Inter-agent message."""

    sender: AgentType
    recipient: AgentType
    type: MessageType
    payload: str
    priority: int = 5  # 1=highest, 10=lowest
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def __lt__(self, other):
        """For priority queue ordering (lower priority value = higher priority)."""
        return self.priority < other.priority


class MessageQueue:
    """In-memory message queue using multiprocessing.Queue.

    This is a MINIMAL implementation for POC purposes.
    Production version would use SQLite or Redis for persistence.
    """

    def __init__(self):
        # Use multiprocessing.Queue for inter-process communication
        self._queue = multiprocessing.Queue()
        # Use heap for priority ordering
        self._heap = []

    def send(self, message: Message) -> None:
        """Send message to queue.

        Args:
            message: Message to send
        """
        # Add to priority heap
        heapq.heappush(self._heap, (message.priority, message))
        print(f"[MessageQueue] Message sent: {message.sender.value} → {message.recipient.value}")

    def get(self, recipient: AgentType, timeout: float = 1.0) -> Optional[Message]:
        """Get next message for recipient (highest priority first).

        Args:
            recipient: Agent to get messages for
            timeout: Timeout in seconds

        Returns:
            Next message or None if no messages available
        """
        # Look for messages for this recipient
        found_messages = []
        remaining_messages = []

        while self._heap:
            priority, msg = heapq.heappop(self._heap)
            if msg.recipient == recipient:
                found_messages.append((priority, msg))
            else:
                remaining_messages.append((priority, msg))

        # Put back messages not for this recipient
        for item in remaining_messages:
            heapq.heappush(self._heap, item)

        # Return highest priority message for this recipient
        if found_messages:
            _, message = min(found_messages, key=lambda x: x[0])
            # Put back other messages for this recipient
            for item in found_messages:
                if item[1] != message:
                    heapq.heappush(self._heap, item)
            return message

        return None

    def has_messages(self) -> bool:
        """Check if queue has messages."""
        return len(self._heap) > 0

    def size(self) -> int:
        """Get queue size."""
        return len(self._heap)

    def stop(self) -> None:
        """Stop message queue (cleanup)."""
        print("[MessageQueue] Stopping...")
        self._heap.clear()
