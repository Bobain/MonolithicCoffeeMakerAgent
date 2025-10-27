"""Unit tests for BaseCommand class and action routing mechanism.

Tests the core ConsolidatedCommand class that provides the foundation for
all consolidated command handlers, including:
- Action routing and validation
- Parameter validation (required, type, one_of)
- Error handling and logging
- Deprecation wrapper creation
- Command information retrieval
"""

import unittest
import warnings
from unittest.mock import MagicMock, patch

from coffee_maker.commands.consolidated.base_command import ConsolidatedCommand


class TestConsolidatedCommandActionRouting(unittest.TestCase):
    """Test action routing mechanism of ConsolidatedCommand."""

    def setUp(self):
        """Set up test fixtures."""
        self.command = ConsolidatedCommand()

    def test_route_action_valid(self):
        """Test routing to valid action handler."""
        handler = MagicMock(return_value="success")
        actions = {"valid": handler}

        result = self.command._route_action("valid", actions, param1="value1")

        handler.assert_called_once_with(param1="value1")
        self.assertEqual(result, "success")

    def test_route_action_invalid_action(self):
        """Test routing to invalid action raises ValueError."""
        actions = {"valid": MagicMock()}

        with self.assertRaises(ValueError) as context:
            self.command._route_action("invalid", actions)

        self.assertIn("Unknown action", str(context.exception))
        self.assertIn("valid", str(context.exception))

    def test_route_action_missing_parameters(self):
        """Test routing with missing required parameters raises TypeError."""

        def handler(required_param):
            return required_param

        actions = {"action": handler}

        with self.assertRaises(TypeError) as context:
            self.command._route_action("action", actions)

        self.assertIn("missing or invalid", str(context.exception))

    def test_route_action_handler_exception_propagates(self):
        """Test that exceptions from handler are propagated."""

        def failing_handler(**kwargs):
            raise RuntimeError("Handler failed")

        actions = {"action": failing_handler}

        with self.assertRaises(RuntimeError):
            self.command._route_action("action", actions)

    def test_route_action_multiple_actions(self):
        """Test routing with multiple available actions."""
        handler1 = MagicMock(return_value="result1")
        handler2 = MagicMock(return_value="result2")
        actions = {"action1": handler1, "action2": handler2}

        result1 = self.command._route_action("action1", actions)
        result2 = self.command._route_action("action2", actions)

        self.assertEqual(result1, "result1")
        self.assertEqual(result2, "result2")
        handler1.assert_called_once()
        handler2.assert_called_once()

    def test_route_action_passes_all_kwargs(self):
        """Test that all kwargs are passed to handler."""
        handler = MagicMock(return_value="success")
        actions = {"action": handler}

        self.command._route_action(
            "action",
            actions,
            param1="value1",
            param2="value2",
            param3=123,
        )

        handler.assert_called_once_with(param1="value1", param2="value2", param3=123)

    def test_route_action_logging(self):
        """Test that routing is logged."""
        handler = MagicMock(return_value="success")
        actions = {"action": handler}

        with patch.object(self.command.logger, "debug") as mock_debug:
            self.command._route_action("action", actions, param="value")

            # Should log routing and completion
            self.assertEqual(mock_debug.call_count, 2)
            calls = [call[0][0] for call in mock_debug.call_args_list]
            self.assertIn("Routing action", calls[0])
            self.assertIn("completed successfully", calls[1])


class TestConsolidatedCommandValidation(unittest.TestCase):
    """Test parameter validation methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.command = ConsolidatedCommand()

    def test_validate_required_params_all_present(self):
        """Test validation passes when all required params are present."""
        params = {"param1": "value1", "param2": "value2"}

        # Should not raise
        self.command.validate_required_params(params, ["param1", "param2"])

    def test_validate_required_params_missing_one(self):
        """Test validation fails when one required param is missing."""
        params = {"param1": "value1"}

        with self.assertRaises(TypeError) as context:
            self.command.validate_required_params(params, ["param1", "param2"])

        self.assertIn("param2", str(context.exception))
        self.assertIn("Missing required parameters", str(context.exception))

    def test_validate_required_params_missing_multiple(self):
        """Test validation fails when multiple required params are missing."""
        params = {"param1": "value1"}

        with self.assertRaises(TypeError) as context:
            self.command.validate_required_params(params, ["param1", "param2", "param3"])

        error_msg = str(context.exception)
        self.assertIn("param2", error_msg)
        self.assertIn("param3", error_msg)

    def test_validate_required_params_none_value(self):
        """Test validation fails when required param has None value."""
        params = {"param1": None, "param2": "value2"}

        with self.assertRaises(TypeError) as context:
            self.command.validate_required_params(params, ["param1", "param2"])

        self.assertIn("param1", str(context.exception))

    def test_validate_required_params_empty_list(self):
        """Test validation passes with empty required list."""
        params = {"param1": "value1"}

        # Should not raise
        self.command.validate_required_params(params, [])

    def test_validate_param_type_correct_type(self):
        """Test validation passes for correct type."""
        # Should not raise
        self.command.validate_param_type("name", "value", str)
        self.command.validate_param_type("count", 42, int)
        self.command.validate_param_type("data", {"key": "value"}, dict)
        self.command.validate_param_type("items", [1, 2, 3], list)

    def test_validate_param_type_wrong_type(self):
        """Test validation fails for wrong type."""
        with self.assertRaises(TypeError) as context:
            self.command.validate_param_type("name", 123, str)

        error_msg = str(context.exception)
        self.assertIn("name", error_msg)
        self.assertIn("str", error_msg)
        self.assertIn("int", error_msg)

    def test_validate_param_type_multiple_wrong_types(self):
        """Test validation works for multiple params with wrong types."""
        with self.assertRaises(TypeError):
            self.command.validate_param_type("param1", "string", int)

        with self.assertRaises(TypeError):
            self.command.validate_param_type("param2", 123, dict)

        with self.assertRaises(TypeError):
            self.command.validate_param_type("param3", ["list"], str)

    def test_validate_one_of_valid_value(self):
        """Test validation passes for valid value in list."""
        # Should not raise
        self.command.validate_one_of("status", "active", ["active", "inactive"])
        self.command.validate_one_of("priority", "high", ["low", "medium", "high"])

    def test_validate_one_of_invalid_value(self):
        """Test validation fails for value not in list."""
        with self.assertRaises(ValueError) as context:
            self.command.validate_one_of("status", "unknown", ["active", "inactive"])

        error_msg = str(context.exception)
        self.assertIn("status", error_msg)
        self.assertIn("unknown", error_msg)
        self.assertIn("active", error_msg)
        self.assertIn("inactive", error_msg)

    def test_validate_one_of_case_sensitive(self):
        """Test validation is case-sensitive."""
        with self.assertRaises(ValueError):
            self.command.validate_one_of("status", "Active", ["active", "inactive"])

    def test_validate_one_of_empty_list(self):
        """Test validation with empty allowed values."""
        with self.assertRaises(ValueError):
            self.command.validate_one_of("status", "active", [])


class TestConsolidatedCommandDeprecation(unittest.TestCase):
    """Test deprecation wrapper creation."""

    def setUp(self):
        """Set up test fixtures."""
        self.command = ConsolidatedCommand()

    def test_deprecated_command_wrapper_calls_new_method(self):
        """Test that deprecated command wrapper calls new method."""
        # Add a real method to test against
        self.command.new_command = MagicMock(return_value="new_result")

        wrapper = self.command.deprecated_command("old_command", "new_command", "new_action")
        result = wrapper(param1="value1")

        self.command.new_command.assert_called_once_with(action="new_action", param1="value1")
        self.assertEqual(result, "new_result")

    def test_deprecated_command_issues_warning(self):
        """Test that deprecated command issues DeprecationWarning."""
        self.command.new_command = MagicMock(return_value="result")

        wrapper = self.command.deprecated_command("old_command", "new_command", "new_action")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            wrapper()

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("old_command", str(w[0].message))
            self.assertIn("new_command", str(w[0].message))

    def test_deprecated_command_logs_usage(self):
        """Test that deprecated command usage is logged."""
        self.command.new_command = MagicMock(return_value="result")

        wrapper = self.command.deprecated_command("old_command", "new_command", "new_action")

        with patch.object(self.command.logger, "warning") as mock_warning:
            wrapper()

            mock_warning.assert_called_once()
            log_msg = mock_warning.call_args[0][0]
            self.assertIn("old_command", log_msg)
            self.assertIn("new_action", log_msg)

    def test_deprecated_command_passes_parameters(self):
        """Test that deprecated wrapper passes all parameters."""
        self.command.new_command = MagicMock(return_value="result")

        wrapper = self.command.deprecated_command("old_command", "new_command", "new_action")

        wrapper(param1="value1", param2="value2", param3=123)

        self.command.new_command.assert_called_once_with(
            action="new_action", param1="value1", param2="value2", param3=123
        )


class TestConsolidatedCommandInfo(unittest.TestCase):
    """Test command information retrieval."""

    def setUp(self):
        """Set up test fixtures."""

        class TestCommand(ConsolidatedCommand):
            COMMANDS_INFO = {
                "command1": {
                    "description": "First command",
                    "actions": ["action1", "action2"],
                },
                "command2": {
                    "description": "Second command",
                    "actions": ["action3"],
                },
            }

        self.command = TestCommand()

    def test_get_command_info_existing(self):
        """Test getting info for existing command."""
        info = self.command.get_command_info("command1")

        self.assertEqual(info["description"], "First command")
        self.assertEqual(info["actions"], ["action1", "action2"])

    def test_get_command_info_nonexisting(self):
        """Test getting info for non-existing command returns empty dict."""
        info = self.command.get_command_info("nonexistent")

        self.assertEqual(info, {})

    def test_list_commands(self):
        """Test listing all commands."""
        commands = self.command.list_commands()

        self.assertIn("command1", commands)
        self.assertIn("command2", commands)
        self.assertEqual(len(commands), 2)

    def test_list_commands_returns_copy(self):
        """Test that list_commands returns a copy, not reference."""
        commands = self.command.list_commands()
        commands["new_command"] = {"description": "New"}

        # Original should not be modified
        info = self.command.get_command_info("new_command")
        self.assertEqual(info, {})

    def test_list_commands_all_have_descriptions(self):
        """Test that all commands have descriptions."""
        commands = self.command.list_commands()

        for cmd_name, cmd_info in commands.items():
            self.assertIn("description", cmd_info)
            self.assertTrue(len(cmd_info["description"]) > 0)

    def test_list_commands_all_have_actions(self):
        """Test that all commands have actions list."""
        commands = self.command.list_commands()

        for cmd_name, cmd_info in commands.items():
            self.assertIn("actions", cmd_info)
            self.assertIsInstance(cmd_info["actions"], list)
            self.assertTrue(len(cmd_info["actions"]) > 0)


class TestConsolidatedCommandInitialization(unittest.TestCase):
    """Test ConsolidatedCommand initialization."""

    def test_init_default_db_path(self):
        """Test initialization with default db_path."""
        command = ConsolidatedCommand()

        self.assertEqual(command.db_path, "data/roadmap.db")

    def test_init_custom_db_path(self):
        """Test initialization with custom db_path."""
        command = ConsolidatedCommand(db_path="/custom/path.db")

        self.assertEqual(command.db_path, "/custom/path.db")

    def test_init_sets_logger(self):
        """Test that initialization sets up logger."""
        command = ConsolidatedCommand()

        self.assertIsNotNone(command.logger)

    def test_init_multiple_instances(self):
        """Test creating multiple instances with different db paths."""
        cmd1 = ConsolidatedCommand(db_path="/path1.db")
        cmd2 = ConsolidatedCommand(db_path="/path2.db")

        self.assertEqual(cmd1.db_path, "/path1.db")
        self.assertEqual(cmd2.db_path, "/path2.db")


if __name__ == "__main__":
    unittest.main()
