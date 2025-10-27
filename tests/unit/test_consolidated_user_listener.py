"""Unit tests for UserListenerCommands.

Tests all 3 consolidated commands:
1. understand - NLU for user requests (classify_intent, extract_entities, determine_agent)
2. route - Request routing (route_request, queue, handle_fallback)
3. conversation - Conversation management (track, update_context, manage_session)
"""

import unittest

from coffee_maker.commands.consolidated.user_listener_commands import (
    UserListenerCommands,
)


class TestUserListenerUnderstandCommand(unittest.TestCase):
    """Test understand command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.listener = UserListenerCommands()

    def test_understand_classify_intent_action(self):
        """Test understand classify_intent action."""
        result = self.listener.understand(
            action="classify_intent",
            user_input="I want to implement a new feature",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("intent", result)

    def test_understand_classify_intent_missing_user_input(self):
        """Test understand classify_intent without user_input raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.listener.understand(action="classify_intent")

        self.assertIn("user_input", str(context.exception))

    def test_understand_extract_entities_action(self):
        """Test understand extract_entities action."""
        result = self.listener.understand(
            action="extract_entities",
            user_input="Create a user authentication module",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("entities", result)

    def test_understand_determine_agent_action(self):
        """Test understand determine_agent action."""
        result = self.listener.understand(
            action="determine_agent",
            user_input="Design the UI for the dashboard",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("agent", result)


class TestUserListenerRouteCommand(unittest.TestCase):
    """Test route command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.listener = UserListenerCommands()

    def test_route_route_request_action(self):
        """Test route route_request action."""
        result = self.listener.route(
            action="route_request",
            request_text="Implement PRIORITY 5",
            target_agent="code_developer",
        )

        self.assertIsInstance(result, dict)

    def test_route_route_request_missing_target_agent(self):
        """Test route route_request without target_agent raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.listener.route(
                action="route_request",
                request_text="Implement PRIORITY 5",
            )

        self.assertIn("target_agent", str(context.exception))

    def test_route_queue_action(self):
        """Test route queue action."""
        result = self.listener.route(
            action="queue",
            request_text="Some request",
        )

        self.assertTrue(result)

    def test_route_queue_missing_request_text(self):
        """Test route queue without request_text raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.listener.route(action="queue")

        self.assertIn("request_text", str(context.exception))

    def test_route_handle_fallback_action(self):
        """Test route handle_fallback action."""
        result = self.listener.route(action="handle_fallback")

        self.assertIsInstance(result, dict)


class TestUserListenerConversationCommand(unittest.TestCase):
    """Test conversation command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.listener = UserListenerCommands()

    def test_conversation_track_action(self):
        """Test conversation track action."""
        result = self.listener.conversation(
            action="track",
            session_id="session_123",
        )

        self.assertIsInstance(result, dict)

    def test_conversation_track_missing_session_id(self):
        """Test conversation track without session_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.listener.conversation(action="track")

        self.assertIn("session_id", str(context.exception))

    def test_conversation_update_context_action(self):
        """Test conversation update_context action."""
        result = self.listener.conversation(
            action="update_context",
            session_id="session_123",
            context_data={"key": "value"},
        )

        self.assertTrue(result)

    def test_conversation_update_context_missing_context_data(self):
        """Test conversation update_context without context_data raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.listener.conversation(
                action="update_context",
                session_id="session_123",
            )

        self.assertIn("context_data", str(context.exception))

    def test_conversation_manage_session_action(self):
        """Test conversation manage_session action."""
        result = self.listener.conversation(action="manage_session")

        self.assertIsInstance(result, dict)


class TestUserListenerCommandInfo(unittest.TestCase):
    """Test command information for UserListenerCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.listener = UserListenerCommands()

    def test_get_command_info_understand(self):
        """Test getting info for understand command."""
        info = self.listener.get_command_info("understand")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("classify_intent", info["actions"])

    def test_list_commands_includes_all_three(self):
        """Test that all 3 commands are listed."""
        commands = self.listener.list_commands()

        expected = ["understand", "route", "conversation"]
        for cmd in expected:
            self.assertIn(cmd, commands)


if __name__ == "__main__":
    unittest.main()
