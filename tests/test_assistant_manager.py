"""Unit tests for AssistantManager.

PRIORITY 5: Assistant Auto-Refresh & Always-On Availability

Tests for the assistant manager's auto-refresh and status reporting features.
"""

import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from coffee_maker.cli.assistant_manager import AssistantManager


class TestAssistantManager(unittest.TestCase):
    """Test AssistantManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock AssistantBridge
        self.mock_assistant = Mock()
        self.mock_assistant.is_available.return_value = True

    def test_initialization(self):
        """Test basic initialization."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant, refresh_interval=10)

        self.assertEqual(manager.refresh_interval, 10)
        self.assertIsNone(manager.last_refresh)
        self.assertFalse(manager.is_running)
        self.assertIsNotNone(manager.assistant)

    def test_refresh_interval_default(self):
        """Test default refresh interval is 30 minutes."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant)

        self.assertEqual(manager.refresh_interval, 1800)  # 30 minutes in seconds

    @patch("coffee_maker.cli.assistant_manager.Path.exists")
    @patch("builtins.open", create=True)
    def test_refresh_documentation_reads_files(self, mock_open, mock_exists):
        """Test that refresh_documentation reads configured files."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "Test content"

        manager = AssistantManager(assistant_bridge=self.mock_assistant)
        manager._refresh_documentation()

        # Should have called docs_cache for each doc
        self.assertEqual(len(manager.docs_cache), 5)  # 4 docs + git history

        # Verify each doc was cached
        self.assertIn("docs/ROADMAP.md", manager.docs_cache)
        self.assertIn("docs/COLLABORATION_METHODOLOGY.md", manager.docs_cache)
        self.assertIn("docs/DOCUMENTATION_INDEX.md", manager.docs_cache)
        self.assertIn("docs/TUTORIALS.md", manager.docs_cache)

    @patch("coffee_maker.cli.assistant_manager.subprocess.run")
    def test_refresh_git_history(self, mock_run):
        """Test git history refresh."""
        # Mock successful git log
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123 Commit 1\ndef456 Commit 2\n"
        mock_run.return_value = mock_result

        manager = AssistantManager(assistant_bridge=self.mock_assistant)
        manager._refresh_git_history()

        # Should have cached git history
        self.assertIn("_git_history", manager.docs_cache)
        self.assertEqual(manager.docs_cache["_git_history"]["count"], 2)

    def test_start_auto_refresh(self):
        """Test starting auto-refresh starts background thread."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant, refresh_interval=1)

        # Mock _refresh_documentation to avoid file I/O
        manager._refresh_documentation = Mock()

        manager.start_auto_refresh()

        self.assertTrue(manager.is_running)
        self.assertIsNotNone(manager.refresh_thread)
        self.assertTrue(manager.refresh_thread.is_alive())
        self.assertIsNotNone(manager.last_refresh)

        # Stop thread
        manager.stop_auto_refresh()

    def test_stop_auto_refresh(self):
        """Test stopping auto-refresh."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant, refresh_interval=1)

        # Mock _refresh_documentation
        manager._refresh_documentation = Mock()

        manager.start_auto_refresh()
        self.assertTrue(manager.is_running)

        manager.stop_auto_refresh()
        self.assertFalse(manager.is_running)

    def test_manual_refresh_success(self):
        """Test successful manual refresh."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant)

        # Mock _refresh_documentation
        manager._refresh_documentation = Mock()
        manager.docs_cache = {
            "docs/ROADMAP.md": {"size": 1000},
            "docs/TUTORIALS.md": {"size": 500},
        }

        result = manager.manual_refresh()

        self.assertTrue(result["success"])
        self.assertEqual(result["docs_refreshed"], 2)
        self.assertIsNotNone(result["timestamp"])

    def test_manual_refresh_failure(self):
        """Test manual refresh failure handling."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant)

        # Mock _refresh_documentation to raise exception
        manager._refresh_documentation = Mock(side_effect=Exception("Test error"))

        result = manager.manual_refresh()

        self.assertFalse(result["success"])
        self.assertIn("Test error", result["message"])
        self.assertEqual(result["docs_refreshed"], 0)

    def test_get_status_offline(self):
        """Test status when offline."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant)

        status = manager.get_status()

        self.assertFalse(status["online"])
        self.assertIsNone(status["last_refresh"])
        self.assertIsNone(status["next_refresh"])

    def test_get_status_online(self):
        """Test status when online."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant, refresh_interval=1800)

        # Mock refresh
        manager.last_refresh = datetime.now() - timedelta(minutes=10)
        manager.is_running = True
        manager.docs_cache = {
            "docs/ROADMAP.md": {"size": 1000, "modified": datetime.now(), "line_count": 100},
            "_git_history": {"count": 5},
        }

        status = manager.get_status()

        self.assertTrue(status["online"])
        self.assertIsNotNone(status["last_refresh"])
        self.assertIsNotNone(status["next_refresh"])
        self.assertEqual(status["docs_loaded"], 1)  # Only non-internal docs
        self.assertEqual(status["git_commits_loaded"], 5)

    def test_invoke_passthrough(self):
        """Test that invoke passes through to assistant bridge."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant)

        # Mock assistant invoke
        expected_result = {"success": True, "answer": "Test answer"}
        manager.assistant.invoke = Mock(return_value=expected_result)

        result = manager.invoke("test question")

        self.assertEqual(result, expected_result)
        manager.assistant.invoke.assert_called_once_with("test question", None)

    def test_is_assistant_available(self):
        """Test assistant availability check."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant)

        self.assertTrue(manager.is_assistant_available())

        # Test unavailable
        manager.assistant.is_available.return_value = False
        self.assertFalse(manager.is_assistant_available())

    def test_auto_refresh_loop_runs(self):
        """Test that auto-refresh loop refreshes periodically."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant, refresh_interval=1)

        # Mock _refresh_documentation
        manager._refresh_documentation = Mock()

        # Start auto-refresh
        manager.start_auto_refresh()

        # Initial refresh happens immediately
        self.assertTrue(manager._refresh_documentation.called)

        # Wait a bit for next refresh
        time.sleep(1.5)

        # Should have refreshed again
        self.assertGreater(manager._refresh_documentation.call_count, 1)

        # Stop thread
        manager.stop_auto_refresh()

    @patch("coffee_maker.cli.assistant_manager.Path.exists")
    def test_refresh_handles_missing_files(self, mock_exists):
        """Test that refresh handles missing documentation files gracefully."""
        mock_exists.return_value = False

        manager = AssistantManager(assistant_bridge=self.mock_assistant)
        manager._refresh_documentation()

        # Should not crash, just log warnings
        # No docs should be cached (except git history)
        non_git_docs = [k for k in manager.docs_cache.keys() if not k.startswith("_")]
        self.assertEqual(len(non_git_docs), 0)

    def test_refresh_updates_timestamp(self):
        """Test that refresh updates last_refresh timestamp."""
        manager = AssistantManager(assistant_bridge=self.mock_assistant)

        # Mock _refresh_documentation
        manager._refresh_documentation = Mock()

        self.assertIsNone(manager.last_refresh)

        manager.manual_refresh()

        self.assertIsNotNone(manager.last_refresh)
        self.assertIsInstance(manager.last_refresh, datetime)


class TestAssistantManagerIntegration(unittest.TestCase):
    """Integration tests for AssistantManager."""

    @patch("coffee_maker.cli.assistant_manager.Path.exists")
    @patch("builtins.open", create=True)
    @patch("coffee_maker.cli.assistant_manager.subprocess.run")
    def test_full_refresh_cycle(self, mock_run, mock_open, mock_exists):
        """Test a full refresh cycle with mocked file I/O."""
        # Setup mocks
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "Test content for documentation"

        mock_git_result = Mock()
        mock_git_result.returncode = 0
        mock_git_result.stdout = "abc123 First commit\ndef456 Second commit\n"
        mock_run.return_value = mock_git_result

        # Create manager with mock assistant
        mock_assistant = Mock()
        mock_assistant.is_available.return_value = True

        manager = AssistantManager(assistant_bridge=mock_assistant)

        # Trigger refresh
        result = manager.manual_refresh()

        # Verify success
        self.assertTrue(result["success"])
        self.assertEqual(result["docs_refreshed"], 4)  # 4 documentation files

        # Verify cache populated
        self.assertEqual(len(manager.docs_cache), 5)  # 4 docs + git history

        # Verify git history
        self.assertIn("_git_history", manager.docs_cache)
        self.assertEqual(manager.docs_cache["_git_history"]["count"], 2)

        # Verify status
        status = manager.get_status()
        self.assertEqual(status["docs_loaded"], 4)
        self.assertEqual(status["git_commits_loaded"], 2)


if __name__ == "__main__":
    unittest.main()
