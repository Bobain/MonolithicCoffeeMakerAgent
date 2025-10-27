"""Unit tests for CodeDeveloperCommands.

Tests all 6 consolidated commands:
1. implement - Implementation lifecycle (claim, load, update_status, record_commit, complete)
2. test - Testing operations (run, fix, coverage)
3. git - Git operations (commit, create_pr)
4. review - Code review (request, track)
5. quality - Code quality (pre_commit, metrics, lint)
6. config - Configuration management (update_claude, update_config)
"""

import unittest

from coffee_maker.commands.consolidated.code_developer_commands import (
    CodeDeveloperCommands,
)


class TestCodeDeveloperImplementCommand(unittest.TestCase):
    """Test implement command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.dev = CodeDeveloperCommands()

    def test_implement_claim_action(self):
        """Test implement claim action."""
        result = self.dev.implement(action="claim", priority_id="PRIORITY-5")

        self.assertIsInstance(result, dict)

    def test_implement_claim_missing_priority_id(self):
        """Test implement claim without priority_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.dev.implement(action="claim")

        self.assertIn("priority_id", str(context.exception))

    def test_implement_load_action(self):
        """Test implement load action."""
        result = self.dev.implement(
            action="load",
            task_id="TASK-31-1",
            spec_id="SPEC-105",
        )

        self.assertIsInstance(result, dict)

    def test_implement_load_missing_task_id(self):
        """Test implement load without task_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.dev.implement(action="load", spec_id="SPEC-105")

        self.assertIn("task_id", str(context.exception))

    def test_implement_update_status_action(self):
        """Test implement update_status action."""
        result = self.dev.implement(
            action="update_status",
            task_id="TASK-31-1",
            status="in-progress",
        )

        self.assertTrue(result)

    def test_implement_record_commit_action(self):
        """Test implement record_commit action."""
        result = self.dev.implement(
            action="record_commit",
            commit_sha="abc123def456",
            commit_message="feat: Implement PRIORITY 5",
        )

        self.assertTrue(result)

    def test_implement_record_commit_missing_message(self):
        """Test implement record_commit without message raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.dev.implement(
                action="record_commit",
                commit_sha="abc123",
            )

        self.assertIn("commit_message", str(context.exception))

    def test_implement_complete_action(self):
        """Test implement complete action."""
        result = self.dev.implement(
            action="complete",
            task_id="TASK-31-1",
        )

        self.assertTrue(result)

    def test_implement_invalid_action(self):
        """Test implement with invalid action raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.dev.implement(action="invalid_action")

        self.assertIn("Unknown action", str(context.exception))


class TestCodeDeveloperTestCommand(unittest.TestCase):
    """Test test command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.dev = CodeDeveloperCommands()

    def test_test_run_action(self):
        """Test test run action."""
        result = self.dev.test(action="run", test_path="tests/unit")

        self.assertIsInstance(result, dict)

    def test_test_run_without_path(self):
        """Test test run without test_path still works."""
        result = self.dev.test(action="run")

        self.assertIsInstance(result, dict)

    def test_test_fix_action(self):
        """Test test fix action."""
        result = self.dev.test(action="fix")

        self.assertIsInstance(result, dict)

    def test_test_coverage_action(self):
        """Test test coverage action."""
        result = self.dev.test(
            action="coverage",
            output_format="html",
        )

        self.assertIsInstance(result, dict)


class TestCodeDeveloperGitCommand(unittest.TestCase):
    """Test git command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.dev = CodeDeveloperCommands()

    def test_git_commit_action(self):
        """Test git commit action."""
        result = self.dev.git(
            action="commit",
            message="feat: Add new feature",
            files=["coffee_maker/feature.py", "tests/test_feature.py"],
        )

        self.assertIsInstance(result, dict)

    def test_git_commit_missing_message(self):
        """Test git commit without message raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.dev.git(action="commit")

        self.assertIn("message", str(context.exception))

    def test_git_create_pr_action(self):
        """Test git create_pr action."""
        result = self.dev.git(
            action="create_pr",
            title="Implement PRIORITY 5",
            body="This PR implements PRIORITY 5 features",
        )

        self.assertIsInstance(result, dict)

    def test_git_create_pr_missing_title(self):
        """Test git create_pr without title raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.dev.git(
                action="create_pr",
                body="Description",
            )

        self.assertIn("title", str(context.exception))


class TestCodeDeveloperReviewCommand(unittest.TestCase):
    """Test review command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.dev = CodeDeveloperCommands()

    def test_review_request_action(self):
        """Test review request action."""
        result = self.dev.review(
            action="request",
            commit_sha="abc123def456",
            spec_id="SPEC-105",
            description="Code review for SPEC-105 implementation",
        )

        self.assertIsInstance(result, (dict, int))

    def test_review_request_missing_commit_sha(self):
        """Test review request without commit_sha raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.dev.review(
                action="request",
                spec_id="SPEC-105",
            )

        self.assertIn("commit_sha", str(context.exception))

    def test_review_track_action(self):
        """Test review track action."""
        result = self.dev.review(
            action="track",
            review_id=1,
        )

        self.assertIsInstance(result, dict)

    def test_review_track_missing_review_id(self):
        """Test review track without review_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.dev.review(action="track")

        self.assertIn("review_id", str(context.exception))


class TestCodeDeveloperQualityCommand(unittest.TestCase):
    """Test quality command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.dev = CodeDeveloperCommands()

    def test_quality_pre_commit_action(self):
        """Test quality pre_commit action."""
        result = self.dev.quality(action="pre_commit")

        self.assertIsInstance(result, dict)

    def test_quality_metrics_action(self):
        """Test quality metrics action."""
        result = self.dev.quality(action="metrics")

        self.assertIsInstance(result, dict)

    def test_quality_lint_action(self):
        """Test quality lint action."""
        result = self.dev.quality(
            action="lint",
            file_path="coffee_maker/feature.py",
        )

        self.assertIsInstance(result, dict)

    def test_quality_lint_missing_file_path(self):
        """Test quality lint without file_path still works."""
        result = self.dev.quality(action="lint")

        self.assertIsInstance(result, dict)


class TestCodeDeveloperConfigCommand(unittest.TestCase):
    """Test config command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.dev = CodeDeveloperCommands()

    def test_config_update_claude_action(self):
        """Test config update_claude action."""
        result = self.dev.config(action="update_claude")

        self.assertTrue(result)

    def test_config_update_config_action(self):
        """Test config update_config action."""
        result = self.dev.config(action="update_config")

        self.assertTrue(result)


class TestCodeDeveloperCommandInfo(unittest.TestCase):
    """Test command information for CodeDeveloperCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.dev = CodeDeveloperCommands()

    def test_get_command_info_implement(self):
        """Test getting info for implement command."""
        info = self.dev.get_command_info("implement")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("claim", info["actions"])
        self.assertIn("complete", info["actions"])

    def test_list_commands_includes_all_six(self):
        """Test that all 6 commands are listed."""
        commands = self.dev.list_commands()

        expected = ["implement", "test", "git", "review", "quality", "config"]
        for cmd in expected:
            self.assertIn(cmd, commands)


if __name__ == "__main__":
    unittest.main()
