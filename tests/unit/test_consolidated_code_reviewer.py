"""Unit tests for CodeReviewerCommands.

Tests all 4 consolidated commands:
1. review - Complete review operations (generate_report, score, validate_dod)
2. analyze - Code analysis types (style, security, complexity, coverage, types, architecture, docs)
3. monitor - Commit and issue tracking (detect_commits, track_issues)
4. notify - Agent notifications (architect, code_developer)
"""

import unittest

from coffee_maker.commands.consolidated.code_reviewer_commands import (
    CodeReviewerCommands,
)


class TestCodeReviewerReviewCommand(unittest.TestCase):
    """Test review command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.reviewer = CodeReviewerCommands()

    def test_review_generate_report_action(self):
        """Test review generate_report action."""
        result = self.reviewer.review(
            action="generate_report",
            commit_sha="abc123def456",
            spec_id="SPEC-105",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("commit", result)  # Implementation uses 'commit' not 'commit_sha'
        self.assertIn("spec_id", result)

    def test_review_generate_report_missing_commit_sha(self):
        """Test review generate_report without commit_sha raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.reviewer.review(action="generate_report")

        self.assertIn("commit_sha", str(context.exception))

    def test_review_score_action(self):
        """Test review score action."""
        result = self.reviewer.review(
            action="score",
            commit_sha="abc123def456",
        )

        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)

    def test_review_validate_dod_action(self):
        """Test review validate_dod action."""
        result = self.reviewer.review(
            action="validate_dod",
            priority_id="PRIORITY-5",
            spec_id="SPEC-105",
        )

        self.assertIsInstance(result, bool)

    def test_review_validate_dod_missing_priority_id(self):
        """Test review validate_dod without priority_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.reviewer.review(action="validate_dod")

        self.assertIn("priority_id", str(context.exception))


class TestCodeReviewerAnalyzeCommand(unittest.TestCase):
    """Test analyze command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.reviewer = CodeReviewerCommands()

    def test_analyze_style_action(self):
        """Test analyze style action."""
        result = self.reviewer.analyze(
            action="style",
            file_path="coffee_maker/feature.py",
        )

        self.assertIsInstance(result, dict)

    def test_analyze_style_missing_file_path(self):
        """Test analyze style without file_path still works (optional)."""
        # file_path is optional for style analysis
        result = self.reviewer.analyze(action="style")
        self.assertIsInstance(result, dict)

    def test_analyze_security_action(self):
        """Test analyze security action."""
        result = self.reviewer.analyze(
            action="security",
            code_content="def function(): pass",
        )

        self.assertIsInstance(result, dict)

    def test_analyze_complexity_action(self):
        """Test analyze complexity action."""
        result = self.reviewer.analyze(
            action="complexity",
            code_content="def function(): pass",
        )

        self.assertIsInstance(result, dict)

    def test_analyze_coverage_action(self):
        """Test analyze coverage action."""
        result = self.reviewer.analyze(action="coverage")

        self.assertIsInstance(result, dict)

    def test_analyze_types_action(self):
        """Test analyze types action."""
        result = self.reviewer.analyze(
            action="types",
            file_path="coffee_maker/feature.py",
        )

        self.assertIsInstance(result, dict)

    def test_analyze_architecture_action(self):
        """Test analyze architecture action."""
        result = self.reviewer.analyze(
            action="architecture",
            code_content="class FeatureClass: pass",
        )

        self.assertIsInstance(result, dict)

    def test_analyze_docs_action(self):
        """Test analyze docs action."""
        result = self.reviewer.analyze(
            action="docs",
            code_content='"""Module docstring."""',
        )

        self.assertIsInstance(result, dict)

    def test_analyze_invalid_action(self):
        """Test analyze with invalid action raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.reviewer.analyze(action="invalid_action")

        self.assertIn("Unknown action", str(context.exception))


class TestCodeReviewerMonitorCommand(unittest.TestCase):
    """Test monitor command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.reviewer = CodeReviewerCommands()

    def test_monitor_detect_commits_action(self):
        """Test monitor detect_commits action."""
        result = self.reviewer.monitor(action="detect_commits")

        self.assertIsInstance(result, (list, dict))

    def test_monitor_track_issues_action(self):
        """Test monitor track_issues action."""
        result = self.reviewer.monitor(
            action="track_issues",
            issue_id=123,  # Implementation expects issue_id not issue_number
        )

        self.assertIsInstance(result, dict)

    def test_monitor_track_issues_missing_issue_number(self):
        """Test monitor track_issues without issue_id still works (optional)."""
        # issue_id is optional for track_issues
        result = self.reviewer.monitor(action="track_issues")
        self.assertIsInstance(result, dict)


class TestCodeReviewerNotifyCommand(unittest.TestCase):
    """Test notify command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.reviewer = CodeReviewerCommands()

    def test_notify_architect_action(self):
        """Test notify architect action."""
        result = self.reviewer.notify(
            action="architect",
            message="Architecture review needed",
        )

        self.assertTrue(result)

    def test_notify_architect_missing_message(self):
        """Test notify architect without message raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.reviewer.notify(action="architect")

        self.assertIn("message", str(context.exception))

    def test_notify_code_developer_action(self):
        """Test notify code_developer action."""
        result = self.reviewer.notify(
            action="code_developer",
            message="Review complete, changes requested",
        )

        self.assertTrue(result)

    def test_notify_code_developer_missing_message(self):
        """Test notify code_developer without message raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.reviewer.notify(action="code_developer")

        self.assertIn("message", str(context.exception))


class TestCodeReviewerCommandInfo(unittest.TestCase):
    """Test command information for CodeReviewerCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.reviewer = CodeReviewerCommands()

    def test_get_command_info_review(self):
        """Test getting info for review command."""
        info = self.reviewer.get_command_info("review")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("generate_report", info["actions"])
        self.assertIn("validate_dod", info["actions"])

    def test_get_command_info_analyze(self):
        """Test getting info for analyze command."""
        info = self.reviewer.get_command_info("analyze")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        expected_actions = ["style", "security", "complexity", "coverage", "types"]
        for action in expected_actions:
            self.assertIn(action, info["actions"])

    def test_list_commands_includes_all_four(self):
        """Test that all 4 commands are listed."""
        commands = self.reviewer.list_commands()

        expected = ["review", "analyze", "monitor", "notify"]
        for cmd in expected:
            self.assertIn(cmd, commands)

    def test_analyze_has_multiple_actions(self):
        """Test that analyze command has multiple analysis type actions."""
        info = self.reviewer.get_command_info("analyze")

        self.assertGreaterEqual(len(info["actions"]), 7)


if __name__ == "__main__":
    unittest.main()
