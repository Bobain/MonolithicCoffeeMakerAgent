"""Unit tests for AssistantCommands.

Tests all 4 consolidated commands:
1. demo - Demo creation and management (create, record, validate)
2. bug - Bug reporting and tracking (report, track_status, link_to_priority)
3. delegate - Intelligent request routing (classify, route, monitor)
4. docs - Documentation generation (generate, update_readme)
"""

import unittest

from coffee_maker.commands.consolidated.assistant_commands import (
    AssistantCommands,
)


class TestAssistantDemoCommand(unittest.TestCase):
    """Test demo command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.assistant = AssistantCommands()

    def test_demo_create_action(self):
        """Test demo create action."""
        result = self.assistant.demo(
            action="create",
            feature_name="User Authentication",
        )

        self.assertIsInstance(result, str)

    def test_demo_create_missing_feature_name(self):
        """Test demo create without feature_name raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.demo(action="create")

        self.assertIn("feature_name", str(context.exception))

    def test_demo_record_action(self):
        """Test demo record action."""
        result = self.assistant.demo(
            action="record",
            recording_path="/path/to/recording.mp4",
        )

        self.assertTrue(result)

    def test_demo_record_missing_recording_path(self):
        """Test demo record without recording_path raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.demo(action="record")

        self.assertIn("recording_path", str(context.exception))

    def test_demo_validate_action(self):
        """Test demo validate action."""
        result = self.assistant.demo(action="validate")

        self.assertIsInstance(result, bool)


class TestAssistantBugCommand(unittest.TestCase):
    """Test bug command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.assistant = AssistantCommands()

    def test_bug_report_action(self):
        """Test bug report action."""
        result = self.assistant.bug(
            action="report",
            title="Login feature broken",
            description="Users cannot login after password reset",
        )

        self.assertIsInstance(result, (dict, int))

    def test_bug_report_missing_title(self):
        """Test bug report without title raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.bug(
                action="report",
                description="Bug description",
            )

        self.assertIn("title", str(context.exception))

    def test_bug_track_status_action(self):
        """Test bug track_status action."""
        result = self.assistant.bug(
            action="track_status",
            bug_id=123,
        )

        self.assertIsInstance(result, dict)

    def test_bug_track_status_missing_bug_id(self):
        """Test bug track_status without bug_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.bug(action="track_status")

        self.assertIn("bug_id", str(context.exception))

    def test_bug_link_to_priority_action(self):
        """Test bug link_to_priority action."""
        result = self.assistant.bug(
            action="link_to_priority",
            bug_id=123,
            priority_id="PRIORITY-5",
        )

        self.assertTrue(result)

    def test_bug_link_to_priority_missing_priority_id(self):
        """Test bug link_to_priority without priority_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.bug(
                action="link_to_priority",
                bug_id=123,
            )

        self.assertIn("priority_id", str(context.exception))


class TestAssistantDelegateCommand(unittest.TestCase):
    """Test delegate command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.assistant = AssistantCommands()

    def test_delegate_classify_action(self):
        """Test delegate classify action."""
        request = "I need to implement feature X"

        result = self.assistant.delegate(
            action="classify",
            request=request,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("category", result)

    def test_delegate_classify_missing_request(self):
        """Test delegate classify without request raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.delegate(action="classify")

        self.assertIn("request", str(context.exception))

    def test_delegate_route_action(self):
        """Test delegate route action."""
        result = self.assistant.delegate(
            action="route",
            request="Create database schema",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("agent", result)

    def test_delegate_route_missing_request(self):
        """Test delegate route without request raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.delegate(action="route")

        self.assertIn("request", str(context.exception))

    def test_delegate_monitor_action(self):
        """Test delegate monitor action."""
        result = self.assistant.delegate(action="monitor")

        self.assertIsInstance(result, dict)


class TestAssistantDocsCommand(unittest.TestCase):
    """Test docs command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.assistant = AssistantCommands()

    def test_docs_generate_action(self):
        """Test docs generate action."""
        result = self.assistant.docs(
            action="generate",
            feature_name="User Authentication",
        )

        self.assertIsInstance(result, str)

    def test_docs_generate_missing_feature_name(self):
        """Test docs generate without feature_name raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.assistant.docs(action="generate")

        self.assertIn("feature_name", str(context.exception))

    def test_docs_update_readme_action(self):
        """Test docs update_readme action."""
        result = self.assistant.docs(action="update_readme")

        self.assertTrue(result)


class TestAssistantCommandInfo(unittest.TestCase):
    """Test command information for AssistantCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.assistant = AssistantCommands()

    def test_get_command_info_demo(self):
        """Test getting info for demo command."""
        info = self.assistant.get_command_info("demo")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("create", info["actions"])

    def test_get_command_info_bug(self):
        """Test getting info for bug command."""
        info = self.assistant.get_command_info("bug")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("report", info["actions"])

    def test_list_commands_includes_all_four(self):
        """Test that all 4 commands are listed."""
        commands = self.assistant.list_commands()

        expected = ["demo", "bug", "delegate", "docs"]
        for cmd in expected:
            self.assertIn(cmd, commands)


if __name__ == "__main__":
    unittest.main()
