"""Unit tests for SQLite-based message queue.

Tests cover:
- Message persistence (survives restart)
- Priority ordering
- Task lifecycle (queued -> running -> completed/failed)
- Duration tracking
- Bottleneck analysis
- Agent performance metrics
- Queue depth tracking
"""

import sqlite3
import tempfile
import time
from pathlib import Path

import pytest

from coffee_maker.autonomous.message_queue import (
    AgentType,
    Message,
    MessageQueue,
    MessageType,
)


class TestMessageQueue:
    """Test suite for MessageQueue class."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
        Path(f"{db_path}-shm").unlink(missing_ok=True)
        Path(f"{db_path}-wal").unlink(missing_ok=True)

    @pytest.fixture
    def queue(self, temp_db):
        """Create message queue with temp database."""
        return MessageQueue(db_path=temp_db)

    def test_queue_initialization(self, temp_db):
        """Test queue initialization creates database and schema."""
        queue = MessageQueue(db_path=temp_db)
        assert Path(temp_db).exists()

        # Verify schema exists
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            assert cursor.fetchone() is not None

    def test_send_message(self, queue):
        """Test sending a message."""
        message = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type=MessageType.SPEC_CREATED.value,
            payload={"spec_id": "SPEC-072"},
            priority=2,
        )

        queue.send(message)

        # Verify message in database
        with sqlite3.connect(queue.db_path) as conn:
            cursor = conn.execute(
                "SELECT task_id, sender, recipient FROM tasks WHERE task_id = ?",
                (message.task_id,),
            )
            row = cursor.fetchone()
            assert row is not None
            assert row[1] == AgentType.ARCHITECT.value
            assert row[2] == AgentType.CODE_DEVELOPER.value

    def test_get_message(self, queue):
        """Test receiving a message."""
        original = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type=MessageType.SPEC_CREATED.value,
            payload={"spec_id": "SPEC-072"},
            priority=5,
        )

        queue.send(original)
        received = queue.get(AgentType.CODE_DEVELOPER.value)

        assert received is not None
        assert received.sender == original.sender
        assert received.recipient == original.recipient
        assert received.type == original.type
        assert received.payload == original.payload

    def test_message_persistence_survives_restart(self, temp_db):
        """Test messages persist across queue restarts."""
        # Send message with queue1
        queue1 = MessageQueue(db_path=temp_db)
        message = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type=MessageType.SPEC_CREATED.value,
            payload={"spec_id": "SPEC-072"},
            priority=3,
        )
        queue1.send(message)

        # Simulate daemon crash and restart
        queue2 = MessageQueue(db_path=temp_db)

        # Message should still be available
        received = queue2.get(AgentType.CODE_DEVELOPER.value)
        assert received is not None
        assert received.payload == {"spec_id": "SPEC-072"}

    def test_priority_ordering(self, queue):
        """Test messages returned in priority order (lowest number = highest priority)."""
        # Send messages in random order
        low_priority = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test_low",
            payload={},
            priority=8,
        )
        high_priority = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test_high",
            payload={},
            priority=2,
        )
        normal_priority = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test_normal",
            payload={},
            priority=5,
        )

        queue.send(low_priority)
        queue.send(high_priority)
        queue.send(normal_priority)

        # Get messages in order
        msg1 = queue.get(AgentType.CODE_DEVELOPER.value)
        assert msg1.type == "test_high"  # priority=2
        queue.mark_started(msg1.task_id, agent=AgentType.CODE_DEVELOPER.value)
        queue.mark_completed(msg1.task_id, duration_ms=100)

        msg2 = queue.get(AgentType.CODE_DEVELOPER.value)
        assert msg2.type == "test_normal"  # priority=5
        queue.mark_started(msg2.task_id, agent=AgentType.CODE_DEVELOPER.value)
        queue.mark_completed(msg2.task_id, duration_ms=100)

        msg3 = queue.get(AgentType.CODE_DEVELOPER.value)
        assert msg3.type == "test_low"  # priority=8

    def test_mark_started(self, queue):
        """Test marking task as started."""
        message = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test",
            payload={},
        )
        queue.send(message)

        queue.mark_started(message.task_id, agent=AgentType.CODE_DEVELOPER.value)

        with sqlite3.connect(queue.db_path) as conn:
            cursor = conn.execute(
                "SELECT status, started_at FROM tasks WHERE task_id = ?",
                (message.task_id,),
            )
            row = cursor.fetchone()
            assert row[0] == "running"
            assert row[1] is not None

    def test_mark_completed(self, queue):
        """Test marking task as completed."""
        message = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test",
            payload={},
        )
        queue.send(message)
        queue.mark_started(message.task_id, agent=AgentType.CODE_DEVELOPER.value)

        queue.mark_completed(message.task_id, duration_ms=1500)

        with sqlite3.connect(queue.db_path) as conn:
            cursor = conn.execute(
                "SELECT status, duration_ms FROM tasks WHERE task_id = ?",
                (message.task_id,),
            )
            row = cursor.fetchone()
            assert row[0] == "completed"
            assert row[1] == 1500

    def test_mark_failed(self, queue):
        """Test marking task as failed."""
        message = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test",
            payload={},
        )
        queue.send(message)
        queue.mark_started(message.task_id, agent=AgentType.CODE_DEVELOPER.value)

        queue.mark_failed(message.task_id, error_message="Task timed out")

        with sqlite3.connect(queue.db_path) as conn:
            cursor = conn.execute(
                "SELECT status, error_message FROM tasks WHERE task_id = ?",
                (message.task_id,),
            )
            row = cursor.fetchone()
            assert row[0] == "failed"
            assert row[1] == "Task timed out"

    def test_bottleneck_analysis(self, queue):
        """Test slowest tasks query."""
        # Create tasks with different durations
        durations = [1000, 5000, 2000, 10000, 3000, 15000, 500]

        for i, duration in enumerate(durations):
            msg = Message(
                sender=AgentType.ARCHITECT.value,
                recipient=AgentType.CODE_DEVELOPER.value,
                type=f"task_{i}",
                payload={},
            )
            queue.send(msg)
            queue.mark_started(msg.task_id, agent=AgentType.CODE_DEVELOPER.value)
            queue.mark_completed(msg.task_id, duration_ms=duration)

        # Get slowest tasks
        slowest = queue.get_slowest_tasks(limit=3)
        assert len(slowest) == 3
        assert slowest[0]["duration_ms"] == 15000  # Slowest
        assert slowest[1]["duration_ms"] == 10000
        assert slowest[2]["duration_ms"] == 5000

    def test_agent_performance_metrics(self, queue):
        """Test agent performance aggregation."""
        # Create tasks for different agents
        for i in range(5):
            msg = Message(
                sender=AgentType.ARCHITECT.value,
                recipient=AgentType.CODE_DEVELOPER.value,
                type=f"task_{i}",
                payload={},
            )
            queue.send(msg)
            queue.mark_started(msg.task_id, agent=AgentType.CODE_DEVELOPER.value)
            queue.mark_completed(msg.task_id, duration_ms=1000 + i * 100)

        # One failed task
        failed_msg = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="failed_task",
            payload={},
        )
        queue.send(failed_msg)
        queue.mark_started(failed_msg.task_id, agent=AgentType.CODE_DEVELOPER.value)
        queue.mark_failed(failed_msg.task_id, error_message="Error")

        performance = queue.get_agent_performance()
        assert len(performance) > 0

        code_dev_perf = next((p for p in performance if p["agent"] == AgentType.CODE_DEVELOPER.value), None)
        assert code_dev_perf is not None
        assert code_dev_perf["total_tasks"] == 6
        assert code_dev_perf["completed_tasks"] == 5
        assert code_dev_perf["failed_tasks"] == 1
        assert code_dev_perf["avg_duration_ms"] > 0

    def test_queue_depth_tracking(self, queue):
        """Test queue depth by agent and priority."""
        # Create queued tasks (not completed)
        for priority in [1, 2, 5, 8]:
            msg = Message(
                sender=AgentType.ARCHITECT.value,
                recipient=AgentType.CODE_DEVELOPER.value,
                type="queued",
                payload={},
                priority=priority,
            )
            queue.send(msg)

        depth = queue.get_queue_depth()
        assert len(depth) > 0

        code_dev_depth = next((d for d in depth if d["agent"] == AgentType.CODE_DEVELOPER.value), None)
        assert code_dev_depth is not None
        assert code_dev_depth["queued_tasks"] == 4
        assert code_dev_depth["high_priority"] == 2  # priorities 1, 2
        assert code_dev_depth["normal_priority"] == 1  # priority 5
        assert code_dev_depth["low_priority"] == 1  # priority 8

    def test_record_metric(self, queue):
        """Test recording agent metrics."""
        queue.record_metric(AgentType.CODE_DEVELOPER.value, "cpu_percent", 45.2)
        queue.record_metric(AgentType.CODE_DEVELOPER.value, "memory_mb", 128.5)

        with sqlite3.connect(queue.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM agent_metrics WHERE agent = ?",
                (AgentType.CODE_DEVELOPER.value,),
            )
            count = cursor.fetchone()[0]
            assert count == 2

    def test_get_task_metrics(self, queue):
        """Test overall task completion metrics."""
        # Create some tasks
        for i in range(3):
            msg = Message(
                sender=AgentType.ARCHITECT.value,
                recipient=AgentType.CODE_DEVELOPER.value,
                type="task",
                payload={},
            )
            queue.send(msg)
            queue.mark_started(msg.task_id, agent=AgentType.CODE_DEVELOPER.value)
            queue.mark_completed(msg.task_id, duration_ms=1000)

        # One queued, one failed
        queue.send(
            Message(
                sender=AgentType.ARCHITECT.value,
                recipient=AgentType.CODE_DEVELOPER.value,
                type="queued",
                payload={},
            )
        )

        metrics = queue.get_task_metrics()
        assert metrics["total_tasks"] == 4
        assert metrics["completed_tasks"] == 3
        assert metrics["queued_tasks"] == 1
        assert metrics["failed_tasks"] == 0

    def test_has_messages(self, queue):
        """Test checking for queued messages."""
        assert not queue.has_messages(AgentType.CODE_DEVELOPER.value)

        msg = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test",
            payload={},
        )
        queue.send(msg)

        assert queue.has_messages(AgentType.CODE_DEVELOPER.value)

    def test_queue_size(self, queue):
        """Test getting queue size."""
        assert queue.size(AgentType.CODE_DEVELOPER.value) == 0

        for i in range(5):
            queue.send(
                Message(
                    sender=AgentType.ARCHITECT.value,
                    recipient=AgentType.CODE_DEVELOPER.value,
                    type="test",
                    payload={},
                )
            )

        assert queue.size(AgentType.CODE_DEVELOPER.value) == 5

    def test_get_percentiles(self, queue):
        """Test duration percentile calculations."""
        # Create tasks with known durations
        durations = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

        for i, duration in enumerate(durations):
            msg = Message(
                sender=AgentType.ARCHITECT.value,
                recipient=AgentType.CODE_DEVELOPER.value,
                type=f"task_{i}",
                payload={},
            )
            queue.send(msg)
            queue.mark_started(msg.task_id, agent=AgentType.CODE_DEVELOPER.value)
            queue.mark_completed(msg.task_id, duration_ms=duration)

        percentiles = queue.get_percentiles([50, 95, 99])
        assert 50 in percentiles
        assert 95 in percentiles
        assert 99 in percentiles
        # Values should be in reasonable range
        assert percentiles[50] is not None

    def test_cleanup_old_tasks(self, queue):
        """Test cleanup of old completed tasks."""
        # Create completed task
        msg = Message(
            sender=AgentType.ARCHITECT.value,
            recipient=AgentType.CODE_DEVELOPER.value,
            type="test",
            payload={},
        )
        queue.send(msg)
        queue.mark_started(msg.task_id, agent=AgentType.CODE_DEVELOPER.value)
        queue.mark_completed(msg.task_id, duration_ms=1000)

        # Manually set completed_at to old date
        with sqlite3.connect(queue.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET completed_at = datetime('now', '-31 days') WHERE task_id = ?",
                (msg.task_id,),
            )
            conn.commit()

        # Cleanup
        deleted = queue.cleanup_old_tasks(days=30)
        assert deleted == 1

        # Verify task is gone
        assert queue.get(AgentType.CODE_DEVELOPER.value) is None

    def test_concurrent_send_receive(self, queue):
        """Test sending and receiving messages concurrently."""
        import threading

        messages_sent = []
        messages_received = []

        def send_messages():
            for i in range(10):
                msg = Message(
                    sender=AgentType.ARCHITECT.value,
                    recipient=AgentType.CODE_DEVELOPER.value,
                    type=f"task_{i}",
                    payload={"index": i},
                )
                queue.send(msg)
                messages_sent.append(msg)

        def receive_messages():
            for _ in range(10):
                msg = queue.get(AgentType.CODE_DEVELOPER.value)
                if msg:
                    messages_received.append(msg)

        sender = threading.Thread(target=send_messages)
        receiver = threading.Thread(target=receive_messages)

        sender.start()
        time.sleep(0.1)  # Let sender get ahead
        receiver.start()

        sender.join()
        receiver.join()

        assert len(messages_sent) == 10
        assert len(messages_received) == 10

    def test_queue_stop_cleanup(self, queue):
        """Test stop() method performs cleanup."""
        # Add some tasks
        for i in range(3):
            queue.send(
                Message(
                    sender=AgentType.ARCHITECT.value,
                    recipient=AgentType.CODE_DEVELOPER.value,
                    type="test",
                    payload={},
                )
            )

        # Should not raise
        queue.stop()

    def test_empty_queue_operations(self, queue):
        """Test operations on empty queue."""
        assert queue.get(AgentType.CODE_DEVELOPER.value) is None
        assert queue.size() == 0
        assert not queue.has_messages()
        assert queue.get_slowest_tasks() == []
