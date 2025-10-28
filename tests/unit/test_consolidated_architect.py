"""Unit tests for ArchitectCommands.

Tests all 5 consolidated commands:
1. spec - Technical specifications (create, update, approve, deprecate, link)
2. tasks - Task management (decompose, update_order, merge_branch)
3. documentation - ADRs and guidelines (create_adr, update_guidelines, update_styleguide)
4. review - Architecture validation (validate_architecture, design_api)
5. dependencies - Dependency management (check, add, evaluate)
"""

import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from coffee_maker.commands.consolidated.architect_commands import (
    ArchitectCommands,
)


class TestArchitectSpecCommand(unittest.TestCase):
    """Test spec command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_spec_create_action(self):
        """Test spec create action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchone.return_value = (5,)  # Max spec_number

            result = self.arch.spec(
                action="create",
                title="New Specification",
                content="Specification content here",
            )

            self.assertEqual(result, "SPEC-6")
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()

    def test_spec_create_missing_title(self):
        """Test spec create without title raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.spec(
                action="create",
                content="Specification content here",
            )

        self.assertIn("title", str(context.exception))

    def test_spec_create_missing_content(self):
        """Test spec create without content raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.spec(
                action="create",
                title="New Specification",
            )

        self.assertIn("content", str(context.exception))

    def test_spec_update_action(self):
        """Test spec update action."""
        result = self.arch.spec(
            action="update",
            spec_id="SPEC-1",
            content="Updated content",
        )

        self.assertTrue(result)

    def test_spec_update_missing_spec_id(self):
        """Test spec update without spec_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.spec(action="update", content="Updated content")

        self.assertIn("spec_id", str(context.exception))

    def test_spec_approve_action(self):
        """Test spec approve action."""
        result = self.arch.spec(action="approve", spec_id="SPEC-1")

        self.assertTrue(result)

    def test_spec_approve_missing_spec_id(self):
        """Test spec approve without spec_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.spec(action="approve")

        self.assertIn("spec_id", str(context.exception))

    def test_spec_deprecate_action(self):
        """Test spec deprecate action."""
        result = self.arch.spec(action="deprecate", spec_id="SPEC-1")

        self.assertTrue(result)

    def test_spec_link_action(self):
        """Test spec link action."""
        result = self.arch.spec(
            action="link",
            spec_id="SPEC-1",
            roadmap_item_id="PRIORITY-5",
        )

        self.assertTrue(result)

    def test_spec_link_missing_roadmap_item_id(self):
        """Test spec link without roadmap_item_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.spec(action="link", spec_id="SPEC-1")

        self.assertIn("roadmap_item_id", str(context.exception))

    def test_spec_invalid_action(self):
        """Test spec with invalid action raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.arch.spec(action="invalid_action")

        self.assertIn("Unknown action", str(context.exception))


class TestArchitectTasksCommand(unittest.TestCase):
    """Test tasks command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_tasks_decompose_action(self):
        """Test tasks decompose action."""
        result = self.arch.tasks(action="decompose", spec_id="SPEC-1")

        self.assertIsInstance(result, list)

    def test_tasks_decompose_missing_spec_id(self):
        """Test tasks decompose without spec_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.tasks(action="decompose")

        self.assertIn("spec_id", str(context.exception))

    def test_tasks_update_order_action(self):
        """Test tasks update_order action."""
        tasks = [
            {"id": "TASK-1", "order": 1},
            {"id": "TASK-2", "order": 2},
        ]

        result = self.arch.tasks(action="update_order", tasks=tasks)

        self.assertTrue(result)

    def test_tasks_update_order_missing_tasks(self):
        """Test tasks update_order without tasks raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.tasks(action="update_order")

        self.assertIn("tasks", str(context.exception))

    def test_tasks_merge_branch_action(self):
        """Test tasks merge_branch action."""
        result = self.arch.tasks(action="merge_branch")

        self.assertTrue(result)


class TestArchitectDocumentationCommand(unittest.TestCase):
    """Test documentation command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_documentation_create_adr_action(self):
        """Test documentation create_adr action."""
        result = self.arch.documentation(
            action="create_adr",
            title="ADR: Use SQLite for Database",
            content="Decision Record content...",
        )

        self.assertEqual(result, "ADR-001")

    def test_documentation_create_adr_missing_title(self):
        """Test documentation create_adr without title raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.documentation(
                action="create_adr",
                content="ADR content",
            )

        self.assertIn("title", str(context.exception))

    def test_documentation_update_guidelines_action(self):
        """Test documentation update_guidelines action."""
        result = self.arch.documentation(
            action="update_guidelines",
            section="error-handling",
            content="Updated guidelines...",
        )

        self.assertTrue(result)

    def test_documentation_update_guidelines_missing_section(self):
        """Test documentation update_guidelines without section raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.documentation(
                action="update_guidelines",
                content="Updated guidelines",
            )

        self.assertIn("section", str(context.exception))

    def test_documentation_update_styleguide_action(self):
        """Test documentation update_styleguide action."""
        result = self.arch.documentation(
            action="update_styleguide",
            section="naming",
            content="Updated style guide...",
        )

        self.assertTrue(result)

    def test_documentation_update_styleguide_missing_content(self):
        """Test documentation update_styleguide without content raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.documentation(
                action="update_styleguide",
                section="naming",
            )

        self.assertIn("content", str(context.exception))


class TestArchitectReviewCommand(unittest.TestCase):
    """Test review command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_review_validate_architecture_action(self):
        """Test review validate_architecture action."""
        result = self.arch.review(
            action="validate_architecture",
            spec_id="SPEC-1",
        )

        self.assertIn("spec_id", result)
        self.assertIn("valid", result)
        self.assertIn("issues", result)

    def test_review_validate_architecture_missing_spec_id(self):
        """Test review validate_architecture without spec_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.review(action="validate_architecture")

        self.assertIn("spec_id", str(context.exception))

    def test_review_design_api_action(self):
        """Test review design_api action."""
        design_doc = """
        API Endpoints:
        - GET /users
        - POST /users
        """

        result = self.arch.review(
            action="design_api",
            design_document=design_doc,
        )

        self.assertIn("endpoints", result)
        self.assertIn("authentication", result)

    def test_review_design_api_missing_design_document(self):
        """Test review design_api without design_document raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.review(action="design_api")

        self.assertIn("design_document", str(context.exception))


class TestArchitectDependenciesCommand(unittest.TestCase):
    """Test dependencies command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_dependencies_check_action(self):
        """Test dependencies check action."""
        result = self.arch.dependencies(action="check", package="numpy")

        self.assertIn("package", result)
        self.assertIn("approved", result)
        self.assertIn("tier", result)

    def test_dependencies_check_missing_package(self):
        """Test dependencies check without package raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.dependencies(action="check")

        self.assertIn("package", str(context.exception))

    def test_dependencies_add_action(self):
        """Test dependencies add action."""
        result = self.arch.dependencies(
            action="add",
            package="numpy",
            version="1.24.0",
            reason="Scientific computing",
        )

        self.assertTrue(result)

    def test_dependencies_add_missing_version(self):
        """Test dependencies add without version raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.dependencies(
                action="add",
                package="numpy",
            )

        self.assertIn("version", str(context.exception))

    def test_dependencies_evaluate_action(self):
        """Test dependencies evaluate action."""
        result = self.arch.dependencies(
            action="evaluate",
            package="numpy",
            version="1.24.0",
        )

        self.assertIn("package", result)
        self.assertIn("impact", result)
        self.assertIn("recommendation", result)

    def test_dependencies_evaluate_missing_package(self):
        """Test dependencies evaluate without package raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.arch.dependencies(
                action="evaluate",
                version="1.24.0",
            )

        self.assertIn("package", str(context.exception))


class TestArchitectErrorHandling(unittest.TestCase):
    """Test error handling in ArchitectCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_database_error_handling_spec_create(self):
        """Test database error is propagated for spec create."""
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database connection failed")

            with self.assertRaises(sqlite3.Error):
                self.arch.spec(
                    action="create",
                    title="Test",
                    content="Content",
                )


class TestArchitectCommandInfo(unittest.TestCase):
    """Test command information for ArchitectCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_get_command_info_spec(self):
        """Test getting info for spec command."""
        info = self.arch.get_command_info("spec")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("create", info["actions"])
        self.assertIn("approve", info["actions"])

    def test_list_commands_includes_all_five(self):
        """Test that all 5 commands are listed."""
        commands = self.arch.list_commands()

        expected = ["spec", "tasks", "documentation", "review", "dependencies"]
        for cmd in expected:
            self.assertIn(cmd, commands)

    def test_commands_have_descriptions(self):
        """Test that all commands have descriptions."""
        commands = self.arch.list_commands()

        for cmd_name, cmd_info in commands.items():
            self.assertIn("description", cmd_info)
            self.assertTrue(len(cmd_info["description"]) > 0)


class TestArchitectCommandParameterValidation(unittest.TestCase):
    """Test parameter validation in ArchitectCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.arch = ArchitectCommands()

    def test_spec_create_requires_both_title_and_content(self):
        """Test that spec create requires both title and content."""
        # Missing both
        with self.assertRaises(TypeError):
            self.arch.spec(action="create")

        # Missing title
        with self.assertRaises(TypeError):
            self.arch.spec(action="create", content="Content")

        # Missing content
        with self.assertRaises(TypeError):
            self.arch.spec(action="create", title="Title")

    def test_tasks_decompose_requires_spec_id(self):
        """Test that tasks decompose requires spec_id."""
        with self.assertRaises(TypeError):
            self.arch.tasks(action="decompose")

    def test_documentation_methods_require_content(self):
        """Test that documentation methods require content."""
        # create_adr requires both title and content
        with self.assertRaises(TypeError):
            self.arch.documentation(action="create_adr")

        with self.assertRaises(TypeError):
            self.arch.documentation(action="create_adr", title="Title")

        # update_guidelines requires both section and content
        with self.assertRaises(TypeError):
            self.arch.documentation(action="update_guidelines")

        with self.assertRaises(TypeError):
            self.arch.documentation(action="update_guidelines", section="test")


if __name__ == "__main__":
    unittest.main()
