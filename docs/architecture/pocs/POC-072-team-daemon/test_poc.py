"""
POC-072: Tests

Tests proving POC concepts work correctly.

Usage:
    python test_poc.py
"""

import unittest
import time

from agent_process import AgentProcess
from message_queue import AgentType, Message, MessageQueue, MessageType
from team_daemon import TeamDaemon


class TestPOC(unittest.TestCase):
    """Tests for POC-072 components."""

    def test_message_queue(self):
        """Test message queue basics."""
        print("\n[TEST] Testing message queue...")

        queue = MessageQueue()

        # Send messages
        msg1 = Message(
            sender=AgentType.AGENT_1,
            recipient=AgentType.AGENT_2,
            type=MessageType.SIMPLE_MESSAGE,
            payload="Test message 1",
            priority=5,
        )
        msg2 = Message(
            sender=AgentType.AGENT_1,
            recipient=AgentType.AGENT_2,
            type=MessageType.SIMPLE_MESSAGE,
            payload="Test message 2",
            priority=1,  # Higher priority
        )

        queue.send(msg1)
        queue.send(msg2)

        # Should get higher priority message first
        received = queue.get(AgentType.AGENT_2)
        self.assertIsNotNone(received)
        self.assertEqual(received.priority, 1)
        self.assertEqual(received.payload, "Test message 2")

        # Should get lower priority message next
        received = queue.get(AgentType.AGENT_2)
        self.assertIsNotNone(received)
        self.assertEqual(received.priority, 5)
        self.assertEqual(received.payload, "Test message 1")

        # No more messages
        received = queue.get(AgentType.AGENT_2)
        self.assertIsNone(received)

        print("[TEST] ✅ Message queue test passed")

    def test_agent_process_lifecycle(self):
        """Test agent process start/stop."""
        print("\n[TEST] Testing agent process lifecycle...")

        queue = MessageQueue()
        agent = AgentProcess(AgentType.AGENT_1, queue)

        # Start agent
        agent.start()
        time.sleep(1)  # Give it time to start

        # Check it's alive
        self.assertTrue(agent.is_alive())
        self.assertIsNotNone(agent.pid)

        # Stop agent
        agent.stop(timeout=5)
        time.sleep(1)  # Give it time to stop

        # Check it's stopped
        self.assertFalse(agent.is_alive())

        print("[TEST] ✅ Agent process lifecycle test passed")

    def test_team_daemon_spawn(self):
        """Test team daemon spawns agents."""
        print("\n[TEST] Testing team daemon spawn...")

        # Simplified test - just verify we can create daemon and spawn agents
        MessageQueue()
        daemon = TeamDaemon()

        # Spawn agents directly (not in subprocess to avoid pickling issues)
        daemon._spawn_agent(AgentType.AGENT_1)
        daemon._spawn_agent(AgentType.AGENT_2)

        # Give them time to start
        time.sleep(1)

        # Check they're alive
        self.assertTrue(daemon.agents[AgentType.AGENT_1].is_alive())
        self.assertTrue(daemon.agents[AgentType.AGENT_2].is_alive())

        # Stop daemon
        daemon.stop()
        time.sleep(1)

        # Check they're stopped
        self.assertFalse(daemon.agents[AgentType.AGENT_1].is_alive())
        self.assertFalse(daemon.agents[AgentType.AGENT_2].is_alive())

        print("[TEST] ✅ Team daemon spawn test passed")

    def test_health_monitoring(self):
        """Test health monitoring detects crashes."""
        print("\n[TEST] Testing health monitoring...")

        queue = MessageQueue()
        agent = AgentProcess(AgentType.AGENT_1, queue)

        # Start agent
        agent.start()
        time.sleep(1)
        self.assertTrue(agent.is_alive())

        # Kill agent (simulate crash)
        agent.process.kill()
        time.sleep(1)

        # Health check should detect it's dead
        self.assertFalse(agent.is_alive())

        print("[TEST] ✅ Health monitoring test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("POC-072: Running Tests")
    print("=" * 60)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestPOC)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
        print("POC-072 core concepts are proven to work!")
    else:
        print("❌ SOME TESTS FAILED")
        print("Review failures above")
    print("=" * 60)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(main())
