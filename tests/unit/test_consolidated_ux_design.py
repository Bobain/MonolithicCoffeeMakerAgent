"""Unit tests for UXDesignExpertCommands.

Tests all 4 consolidated commands:
1. design - UI/component specifications (generate_ui_spec, create_component_spec)
2. components - Component library (manage_library, tailwind_config, design_tokens, chart_theme)
3. review - UI review and accessibility (review_implementation, suggest_improvements, validate_accessibility)
4. debt - Design debt management (track, prioritize, remediate)
"""

import unittest

from coffee_maker.commands.consolidated.ux_design_expert_commands import (
    UXDesignExpertCommands,
)


class TestUXDesignDesignCommand(unittest.TestCase):
    """Test design command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.ux = UXDesignExpertCommands()

    def test_design_generate_ui_spec_action(self):
        """Test design generate_ui_spec action."""
        result = self.ux.design(
            action="generate_ui_spec",
            feature_name="User Dashboard",
        )

        self.assertIsInstance(result, (dict, str))

    def test_design_generate_ui_spec_missing_feature_name(self):
        """Test design generate_ui_spec without feature_name raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.design(action="generate_ui_spec")

        self.assertIn("feature_name", str(context.exception))

    def test_design_create_component_spec_action(self):
        """Test design create_component_spec action."""
        result = self.ux.design(
            action="create_component_spec",
            wireframe="Component wireframe...",
        )

        self.assertIsInstance(result, (dict, str))

    def test_design_create_component_spec_missing_wireframe(self):
        """Test design create_component_spec without wireframe raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.design(action="create_component_spec")

        self.assertIn("wireframe", str(context.exception))


class TestUXDesignComponentsCommand(unittest.TestCase):
    """Test components command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.ux = UXDesignExpertCommands()

    def test_components_manage_library_action(self):
        """Test components manage_library action."""
        result = self.ux.components(
            action="manage_library",
            component_id="button-primary",
        )

        self.assertIsInstance(result, dict)

    def test_components_manage_library_missing_component_id(self):
        """Test components manage_library without component_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.components(action="manage_library")

        self.assertIn("component_id", str(context.exception))

    def test_components_tailwind_config_action(self):
        """Test components tailwind_config action."""
        result = self.ux.components(
            action="tailwind_config",
            config_data={"theme": {"colors": {"primary": "#000"}}},
        )

        self.assertIsInstance(result, dict)

    def test_components_tailwind_config_missing_config_data(self):
        """Test components tailwind_config without config_data raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.components(action="tailwind_config")

        self.assertIn("config_data", str(context.exception))

    def test_components_design_tokens_action(self):
        """Test components design_tokens action."""
        result = self.ux.components(
            action="design_tokens",
            config_data={"colors": {"primary": "#000"}},
        )

        self.assertIsInstance(result, dict)

    def test_components_chart_theme_action(self):
        """Test components chart_theme action."""
        result = self.ux.components(
            action="chart_theme",
            config_data={"theme": "light"},
        )

        self.assertIsInstance(result, dict)


class TestUXDesignReviewCommand(unittest.TestCase):
    """Test review command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.ux = UXDesignExpertCommands()

    def test_review_review_implementation_action(self):
        """Test review review_implementation action."""
        result = self.ux.review(
            action="review_implementation",
            component_id="button-primary",
        )

        self.assertIsInstance(result, dict)

    def test_review_review_implementation_missing_component_id(self):
        """Test review review_implementation without component_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.review(action="review_implementation")

        self.assertIn("component_id", str(context.exception))

    def test_review_suggest_improvements_action(self):
        """Test review suggest_improvements action."""
        result = self.ux.review(
            action="suggest_improvements",
            design_content="Current design...",
        )

        self.assertIsInstance(result, list)

    def test_review_suggest_improvements_missing_design_content(self):
        """Test review suggest_improvements without design_content raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.review(action="suggest_improvements")

        self.assertIn("design_content", str(context.exception))

    def test_review_validate_accessibility_action(self):
        """Test review validate_accessibility action."""
        result = self.ux.review(
            action="validate_accessibility",
            component_id="button-primary",
        )

        self.assertIsInstance(result, bool)

    def test_review_validate_accessibility_missing_component_id(self):
        """Test review validate_accessibility without component_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.review(action="validate_accessibility")

        self.assertIn("component_id", str(context.exception))


class TestUXDesignDebtCommand(unittest.TestCase):
    """Test debt command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.ux = UXDesignExpertCommands()

    def test_debt_track_action(self):
        """Test debt track action."""
        result = self.ux.debt(
            action="track",
            item_description="Old button style used in 5 places",
        )

        self.assertIsInstance(result, (dict, int))

    def test_debt_track_missing_item_description(self):
        """Test debt track without item_description raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.debt(action="track")

        self.assertIn("item_description", str(context.exception))

    def test_debt_prioritize_action(self):
        """Test debt prioritize action."""
        result = self.ux.debt(action="prioritize")

        self.assertIsInstance(result, list)

    def test_debt_remediate_action(self):
        """Test debt remediate action."""
        result = self.ux.debt(
            action="remediate",
            item_id=1,
        )

        self.assertTrue(result)

    def test_debt_remediate_missing_item_id(self):
        """Test debt remediate without item_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.ux.debt(action="remediate")

        self.assertIn("item_id", str(context.exception))


class TestUXDesignCommandInfo(unittest.TestCase):
    """Test command information for UXDesignExpertCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.ux = UXDesignExpertCommands()

    def test_get_command_info_design(self):
        """Test getting info for design command."""
        info = self.ux.get_command_info("design")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("generate_ui_spec", info["actions"])

    def test_get_command_info_components(self):
        """Test getting info for components command."""
        info = self.ux.get_command_info("components")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        expected = ["manage_library", "tailwind_config", "design_tokens"]
        for action in expected:
            self.assertIn(action, info["actions"])

    def test_list_commands_includes_all_four(self):
        """Test that all 4 commands are listed."""
        commands = self.ux.list_commands()

        expected = ["design", "components", "review", "debt"]
        for cmd in expected:
            self.assertIn(cmd, commands)


if __name__ == "__main__":
    unittest.main()
