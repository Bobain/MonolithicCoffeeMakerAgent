"""Unit tests for OrchestratorCommands.

Tests all 5 consolidated commands:
1. agents - Agent lifecycle (spawn, kill, restart, monitor_lifecycle, handle_errors)
2. orchestrate - Work coordination (coordinate_deps, find_work, create_tasks, detect_deadlocks)
3. worktree - Git worktree operations (create, cleanup, merge)
4. messages - Inter-agent communication (route, send, receive)
5. monitor - Resource monitoring (resources, activity_summary)
"""

import unittest

from coffee_maker.commands.consolidated.orchestrator_commands import (
    OrchestratorCommands,
)


class TestOrchestratorAgentsCommand(unittest.TestCase):
    """Test agents command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.orch = OrchestratorCommands()

    def test_agents_spawn_action(self):
        """Test agents spawn action."""
        result = self.orch.agents(
            action="spawn",
            agent_type="code_developer",
            task_id="TASK-31-1",
        )

        self.assertIsInstance(result, (dict, int))

    def test_agents_spawn_missing_agent_type(self):
        """Test agents spawn without agent_type raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.orch.agents(action="spawn", task_id="TASK-31-1")

        self.assertIn("agent_type", str(context.exception))

    def test_agents_kill_action(self):
        """Test agents kill action."""
        result = self.orch.agents(
            action="kill",
            agent_id=1,
        )

        self.assertTrue(result)

    def test_agents_kill_missing_agent_id(self):
        """Test agents kill without agent_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.orch.agents(action="kill")

        self.assertIn("agent_id", str(context.exception))

    def test_agents_restart_action(self):
        """Test agents restart action."""
        result = self.orch.agents(
            action="restart",
            agent_id=1,
        )

        self.assertTrue(result)

    def test_agents_monitor_lifecycle_action(self):
        """Test agents monitor_lifecycle action."""
        result = self.orch.agents(
            action="monitor_lifecycle",
            agent_id=1,
        )

        self.assertIsInstance(result, dict)

    def test_agents_handle_errors_action(self):
        """Test agents handle_errors action."""
        result = self.orch.agents(
            action="handle_errors",
            agent_id=1,
        )

        self.assertTrue(result)


class TestOrchestratorOrchestrateCommand(unittest.TestCase):
    """Test orchestrate command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.orch = OrchestratorCommands()

    def test_orchestrate_coordinate_deps_action(self):
        """Test orchestrate coordinate_deps action."""
        result = self.orch.orchestrate(
            action="coordinate_deps",
            spec_id="SPEC-105",
        )

        self.assertIsInstance(result, dict)

    def test_orchestrate_find_work_action(self):
        """Test orchestrate find_work action."""
        result = self.orch.orchestrate(action="find_work")

        self.assertIsInstance(result, (list, dict))

    def test_orchestrate_create_tasks_action(self):
        """Test orchestrate create_tasks action."""
        result = self.orch.orchestrate(action="create_tasks")

        self.assertTrue(result)

    def test_orchestrate_detect_deadlocks_action(self):
        """Test orchestrate detect_deadlocks action."""
        result = self.orch.orchestrate(action="detect_deadlocks")

        self.assertIsInstance(result, dict)


class TestOrchestratorWorktreeCommand(unittest.TestCase):
    """Test worktree command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.orch = OrchestratorCommands()

    def test_worktree_create_action(self):
        """Test worktree create action."""
        result = self.orch.worktree(
            action="create",
            task_id="TASK-31-1",
            branch_name="roadmap-implementation_task-TASK-31-1",
        )

        self.assertIsInstance(result, dict)

    def test_worktree_create_missing_task_id(self):
        """Test worktree create without task_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.orch.worktree(action="create")

        self.assertIn("task_id", str(context.exception))

    def test_worktree_cleanup_action(self):
        """Test worktree cleanup action."""
        result = self.orch.worktree(
            action="cleanup",
            task_id="TASK-31-1",
        )

        self.assertTrue(result)

    def test_worktree_merge_action(self):
        """Test worktree merge action."""
        result = self.orch.worktree(
            action="merge",
            task_id="TASK-31-1",
        )

        self.assertTrue(result)


class TestOrchestratorMessagesCommand(unittest.TestCase):
    """Test messages command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.orch = OrchestratorCommands()

    def test_messages_route_action(self):
        """Test messages route action."""
        result = self.orch.messages(action="route")

        self.assertTrue(result)

    def test_messages_send_action(self):
        """Test messages send action."""
        result = self.orch.messages(
            action="send",
            to_agent="code_developer",
            message="Test message",
        )

        self.assertTrue(result)

    def test_messages_send_missing_to_agent(self):
        """Test messages send without to_agent raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.orch.messages(action="send", message="Test")

        self.assertIn("to_agent", str(context.exception))

    def test_messages_receive_action(self):
        """Test messages receive action."""
        result = self.orch.messages(
            action="receive",
            from_agent="code_developer",
        )

        self.assertIsInstance(result, (list, dict))

    def test_messages_receive_missing_from_agent(self):
        """Test messages receive without from_agent raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.orch.messages(action="receive")

        self.assertIn("from_agent", str(context.exception))


class TestOrchestratorMonitorCommand(unittest.TestCase):
    """Test monitor command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.orch = OrchestratorCommands()

    def test_monitor_resources_action(self):
        """Test monitor resources action."""
        result = self.orch.monitor(action="resources")

        self.assertIsInstance(result, dict)
        self.assertIn("cpu", result)
        self.assertIn("memory", result)

    def test_monitor_activity_summary_action(self):
        """Test monitor activity_summary action."""
        result = self.orch.monitor(action="activity_summary")

        self.assertIsInstance(result, (dict, str))


class TestOrchestratorCommandInfo(unittest.TestCase):
    """Test command information for OrchestratorCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.orch = OrchestratorCommands()

    def test_get_command_info_agents(self):
        """Test getting info for agents command."""
        info = self.orch.get_command_info("agents")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("spawn", info["actions"])

    def test_list_commands_includes_all_five(self):
        """Test that all 5 commands are listed."""
        commands = self.orch.list_commands()

        expected = ["agents", "orchestrate", "worktree", "messages", "monitor"]
        for cmd in expected:
            self.assertIn(cmd, commands)

    def test_agents_has_multiple_lifecycle_actions(self):
        """Test that agents command has lifecycle management actions."""
        info = self.orch.get_command_info("agents")

        expected_actions = ["spawn", "kill", "restart", "monitor_lifecycle"]
        for action in expected_actions:
            self.assertIn(action, info["actions"])


if __name__ == "__main__":
    unittest.main()
