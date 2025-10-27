"""Unit tests for ProjectManagerCommands.

Tests all 5 consolidated commands:
1. roadmap - ROADMAP operations (list, details, update, status)
2. status - Developer status and notifications (developer, notifications, read)
3. dependencies - Dependency management (check, add, list)
4. github - GitHub integration (monitor_pr, track_issue, sync)
5. stats - Project statistics (roadmap, feature, spec, audit)
"""

import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from coffee_maker.commands.consolidated.project_manager_commands import (
    ProjectManagerCommands,
)


class TestProjectManagerRoadmapCommand(unittest.TestCase):
    """Test roadmap command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.pm = ProjectManagerCommands()

    def test_roadmap_list_action(self):
        """Test roadmap list action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = [
                {"id": "PRIORITY-1", "status": "completed"},
                {"id": "PRIORITY-2", "status": "in-progress"},
            ]

            result = self.pm.roadmap(action="list")

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["id"], "PRIORITY-1")
            mock_cursor.execute.assert_called()

    def test_roadmap_list_with_status_filter(self):
        """Test roadmap list action with status filter."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = [{"id": "PRIORITY-1", "status": "completed"}]

            result = self.pm.roadmap(action="list", status="completed")

            self.assertEqual(len(result), 1)
            # Verify SQL includes status filter
            call_args = mock_cursor.execute.call_args
            self.assertIn("status = ?", call_args[0][0])

    def test_roadmap_details_action(self):
        """Test roadmap details action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchone.return_value = {
                "id": "PRIORITY-1",
                "title": "Test Priority",
                "status": "completed",
            }

            result = self.pm.roadmap(action="details", priority_id="PRIORITY-1")

            self.assertEqual(result["id"], "PRIORITY-1")
            self.assertEqual(result["title"], "Test Priority")

    def test_roadmap_details_missing_priority_id(self):
        """Test roadmap details action without priority_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.roadmap(action="details")

        self.assertIn("priority_id", str(context.exception))

    def test_roadmap_details_priority_not_found(self):
        """Test roadmap details action when priority not found."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None

            with self.assertRaises(ValueError) as context:
                self.pm.roadmap(action="details", priority_id="NONEXISTENT")

            self.assertIn("not found", str(context.exception))

    def test_roadmap_update_action(self):
        """Test roadmap update action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {"id": "PRIORITY-1"}

            result = self.pm.roadmap(
                action="update",
                priority_id="PRIORITY-1",
                metadata={"status": "completed"},
            )

            self.assertTrue(result)
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()

    def test_roadmap_update_missing_metadata(self):
        """Test roadmap update without metadata raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.roadmap(action="update", priority_id="PRIORITY-1")

        self.assertIn("metadata", str(context.exception))

    def test_roadmap_update_metadata_wrong_type(self):
        """Test roadmap update with wrong metadata type raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.roadmap(
                action="update",
                priority_id="PRIORITY-1",
                metadata="not a dict",
            )

        self.assertIn("dict", str(context.exception))

    def test_roadmap_status_action(self):
        """Test roadmap status action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchone.return_value = {
                "status": "in-progress",
                "dependencies": "[]",
            }

            result = self.pm.roadmap(action="status", priority_id="PRIORITY-1")

            self.assertEqual(result["priority_id"], "PRIORITY-1")
            self.assertEqual(result["status"], "in-progress")

    def test_roadmap_invalid_action(self):
        """Test roadmap with invalid action raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.pm.roadmap(action="invalid_action")

        self.assertIn("Unknown action", str(context.exception))


class TestProjectManagerStatusCommand(unittest.TestCase):
    """Test status command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.pm = ProjectManagerCommands()

    def test_status_developer_action(self):
        """Test status developer action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # First query for status counts
            mock_cursor.fetchall.return_value = [
                {"status": "completed", "count": 5},
                {"status": "in-progress", "count": 2},
            ]
            # Second query for in-progress count
            mock_cursor.fetchone.return_value = {"count": 2}

            result = self.pm.status(action="developer")

            self.assertEqual(result["in_progress"], 2)
            self.assertEqual(result["total"], 7)
            self.assertIn("status_breakdown", result)

    def test_status_notifications_action(self):
        """Test status notifications action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = [
                {"id": 1, "title": "Notification 1"},
                {"id": 2, "title": "Notification 2"},
            ]

            result = self.pm.status(action="notifications")

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["id"], 1)

    def test_status_notifications_with_level_filter(self):
        """Test status notifications with level filter."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = [{"id": 1, "title": "Error Notification"}]

            result = self.pm.status(action="notifications", level="error")

            self.assertEqual(len(result), 1)
            # Verify filter is applied
            call_args = mock_cursor.execute.call_args
            self.assertIn("notification_type = ?", call_args[0][0])

    def test_status_read_action(self):
        """Test status read action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            result = self.pm.status(action="read", notification_id=1)

            self.assertTrue(result)
            mock_conn.commit.assert_called_once()

    def test_status_read_missing_notification_id(self):
        """Test status read without notification_id raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.status(action="read")

        self.assertIn("notification_id", str(context.exception))


class TestProjectManagerDependenciesCommand(unittest.TestCase):
    """Test dependencies command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.pm = ProjectManagerCommands()

    def test_dependencies_check_action(self):
        """Test dependencies check action."""
        result = self.pm.dependencies(action="check", package="pytest")

        self.assertIn("package", result)
        self.assertEqual(result["package"], "pytest")
        self.assertIn("approved", result)

    def test_dependencies_check_missing_package(self):
        """Test dependencies check without package raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.dependencies(action="check")

        self.assertIn("package", str(context.exception))

    def test_dependencies_add_action(self):
        """Test dependencies add action."""
        result = self.pm.dependencies(action="add", package="pytest", version="7.0.0")

        self.assertTrue(result)

    def test_dependencies_add_missing_version(self):
        """Test dependencies add without version raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.dependencies(action="add", package="pytest")

        self.assertIn("version", str(context.exception))

    def test_dependencies_list_action(self):
        """Test dependencies list action."""
        result = self.pm.dependencies(action="list")

        self.assertIsInstance(result, list)


class TestProjectManagerGitHubCommand(unittest.TestCase):
    """Test github command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.pm = ProjectManagerCommands()

    def test_github_monitor_pr_action(self):
        """Test github monitor_pr action."""
        result = self.pm.github(action="monitor_pr", pr_number=123)

        self.assertEqual(result["pr_number"], 123)
        self.assertIn("status", result)
        self.assertIn("checks", result)

    def test_github_monitor_pr_missing_pr_number(self):
        """Test github monitor_pr without pr_number raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.github(action="monitor_pr")

        self.assertIn("pr_number", str(context.exception))

    def test_github_track_issue_action(self):
        """Test github track_issue action."""
        result = self.pm.github(action="track_issue", issue_number=456)

        self.assertEqual(result["issue_number"], 456)
        self.assertIn("status", result)

    def test_github_track_issue_missing_issue_number(self):
        """Test github track_issue without issue_number raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.pm.github(action="track_issue")

        self.assertIn("issue_number", str(context.exception))

    def test_github_sync_action(self):
        """Test github sync action."""
        result = self.pm.github(action="sync")

        self.assertTrue(result)


class TestProjectManagerStatsCommand(unittest.TestCase):
    """Test stats command with all actions."""

    def setUp(self):
        """Set up test fixtures."""
        self.pm = ProjectManagerCommands()

    def test_stats_roadmap_action(self):
        """Test stats roadmap action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = [
                {"status": "completed", "count": 8},
                {"status": "in-progress", "count": 2},
            ]

            result = self.pm.stats(action="roadmap")

            self.assertEqual(result["total"], 10)
            self.assertEqual(result["completed"], 8)
            self.assertEqual(result["percentage"], 80.0)
            self.assertIn("breakdown", result)

    def test_stats_roadmap_empty(self):
        """Test stats roadmap when no priorities exist."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = []

            result = self.pm.stats(action="roadmap")

            self.assertEqual(result["total"], 0)
            self.assertEqual(result["percentage"], 0)

    def test_stats_feature_action(self):
        """Test stats feature action."""
        result = self.pm.stats(action="feature")

        self.assertIn("total_features", result)
        self.assertIn("implemented", result)

    def test_stats_spec_action(self):
        """Test stats spec action."""
        result = self.pm.stats(action="spec")

        self.assertIn("total_specs", result)
        self.assertIn("approved", result)

    def test_stats_audit_action(self):
        """Test stats audit action."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = [
                {"id": 1, "action": "created"},
                {"id": 2, "action": "updated"},
            ]

            result = self.pm.stats(action="audit")

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)

    def test_stats_audit_with_days_filter(self):
        """Test stats audit with days parameter."""
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = []

            result = self.pm.stats(action="audit", days=30)

            # Verify days parameter is used
            call_args = mock_cursor.execute.call_args
            self.assertIn("LIMIT", call_args[0][0])


class TestProjectManagerErrorHandling(unittest.TestCase):
    """Test error handling in ProjectManagerCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.pm = ProjectManagerCommands()

    def test_database_error_handling_roadmap_list(self):
        """Test database error is propagated for roadmap list."""
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database connection failed")

            with self.assertRaises(sqlite3.Error):
                self.pm.roadmap(action="list")

    def test_database_error_handling_stats(self):
        """Test database error is propagated for stats."""
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database error")

            with self.assertRaises(sqlite3.Error):
                self.pm.stats(action="roadmap")


class TestProjectManagerCommandInfo(unittest.TestCase):
    """Test command information for ProjectManagerCommands."""

    def setUp(self):
        """Set up test fixtures."""
        self.pm = ProjectManagerCommands()

    def test_get_command_info_roadmap(self):
        """Test getting info for roadmap command."""
        info = self.pm.get_command_info("roadmap")

        self.assertIn("description", info)
        self.assertIn("actions", info)
        self.assertIn("list", info["actions"])

    def test_list_commands_includes_all_five(self):
        """Test that all 5 commands are listed."""
        commands = self.pm.list_commands()

        expected = ["roadmap", "status", "dependencies", "github", "stats"]
        for cmd in expected:
            self.assertIn(cmd, commands)

    def test_commands_have_replaces_info(self):
        """Test that commands document which legacy commands they replace."""
        info = self.pm.get_command_info("roadmap")

        self.assertIn("replaces", info)
        self.assertIsInstance(info["replaces"], list)
        self.assertTrue(len(info["replaces"]) > 0)


if __name__ == "__main__":
    unittest.main()
