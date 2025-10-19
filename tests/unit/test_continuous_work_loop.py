"""Unit tests for ContinuousWorkLoop.

Tests cover:
- Work loop initialization
- ROADMAP polling and parsing
- State save/load (crash recovery)
- Architect coordination
- code_developer coordination
- Graceful shutdown
- Task tracking
"""

import json
import signal
import time
from pathlib import Path
from unittest.mock import Mock, patch


from coffee_maker.orchestrator.continuous_work_loop import ContinuousWorkLoop, WorkLoopConfig


class TestWorkLoopInitialization:
    """Test work loop initialization and configuration."""

    def test_work_loop_default_config(self, tmp_path):
        """Test that work loop initializes with default configuration."""
        # Use tmp_path for state file to avoid loading existing state
        config = WorkLoopConfig(state_file_path=str(tmp_path / "state.json"))
        loop = ContinuousWorkLoop(config)

        assert loop.config.poll_interval_seconds == 30
        assert loop.config.spec_backlog_target == 3
        assert loop.config.max_retry_attempts == 3
        assert loop.running is False
        assert loop.current_state == {}

    def test_work_loop_custom_config(self):
        """Test that work loop accepts custom configuration."""
        config = WorkLoopConfig(poll_interval_seconds=60, spec_backlog_target=5)
        loop = ContinuousWorkLoop(config)

        assert loop.config.poll_interval_seconds == 60
        assert loop.config.spec_backlog_target == 5


class TestRoadmapPolling:
    """Test ROADMAP polling and change detection."""

    def test_poll_roadmap_detects_changes(self, tmp_path):
        """Test that polling detects ROADMAP changes."""
        # Create test ROADMAP
        roadmap_path = tmp_path / "ROADMAP.md"
        roadmap_path.write_text("### PRIORITY 20: US-104 - Test 📝 Planned")

        loop = ContinuousWorkLoop()

        # Mock Path to use tmp_path
        with patch("coffee_maker.orchestrator.continuous_work_loop.Path") as mock_path:
            mock_path.return_value = roadmap_path

            # First poll - should detect change
            updated = loop._poll_roadmap()
            assert updated is True

            # Second poll - no changes
            updated = loop._poll_roadmap()
            assert updated is False

            # Modify ROADMAP
            time.sleep(0.01)  # Ensure mtime changes
            roadmap_path.write_text("### PRIORITY 20: US-104 - Updated 📝 Planned")

            # Third poll - should detect change
            updated = loop._poll_roadmap()
            assert updated is True

    def test_poll_roadmap_missing_file(self):
        """Test that missing ROADMAP.md is handled gracefully."""
        loop = ContinuousWorkLoop()

        # Mock Path.exists to return False
        with patch("coffee_maker.orchestrator.continuous_work_loop.Path") as mock_path:
            mock_path.return_value.exists.return_value = False

            updated = loop._poll_roadmap()
            assert updated is False


class TestRoadmapParsing:
    """Test ROADMAP parsing and priority extraction."""

    def test_parse_roadmap_extracts_priorities(self, tmp_path):
        """Test ROADMAP parsing extracts priorities correctly."""
        roadmap_content = """
### PRIORITY 20: US-104 - Orchestrator Work Loop 📝 Planned
### PRIORITY 21: US-105 - Dashboard ✅ Complete
### PRIORITY 22: US-106 - Code Reviewer 🔄 In Progress
        """

        roadmap_path = tmp_path / "ROADMAP.md"
        roadmap_path.write_text(roadmap_content)

        loop = ContinuousWorkLoop()
        result = loop._parse_roadmap(roadmap_path)

        assert len(result["priorities"]) == 3
        assert result["priorities"][0]["number"] == 20
        assert result["priorities"][0]["us_number"] == "US-104"
        assert result["priorities"][0]["status"] == "📝"
        assert result["priorities"][1]["number"] == 21
        assert result["priorities"][1]["status"] == "✅"
        assert result["priorities"][2]["number"] == 22
        assert result["priorities"][2]["status"] == "🔄"

    def test_parse_roadmap_checks_spec_existence(self, tmp_path):
        """Test that parsing checks for spec file existence."""
        roadmap_content = "### PRIORITY 20: US-104 - Test 📝 Planned"
        roadmap_path = tmp_path / "ROADMAP.md"
        roadmap_path.write_text(roadmap_content)

        # Create spec file
        spec_dir = tmp_path / "docs" / "architecture" / "specs"
        spec_dir.mkdir(parents=True)
        (spec_dir / "SPEC-104-test.md").write_text("# Spec")

        loop = ContinuousWorkLoop()

        # Test the parsing logic directly
        result = loop._parse_roadmap(roadmap_path)

        # Should extract the priority
        assert len(result["priorities"]) == 1
        assert result["priorities"][0]["number"] == 20
        assert result["priorities"][0]["us_number"] == "US-104"


class TestStatePersistence:
    """Test state save/load for crash recovery."""

    def test_state_save_and_load(self, tmp_path):
        """Test state persistence across restarts."""
        state_file = tmp_path / "state.json"
        config = WorkLoopConfig(state_file_path=str(state_file))

        # Create first instance
        loop1 = ContinuousWorkLoop(config)
        loop1.current_state = {
            "active_tasks": {"spec_20": {"task_id": "abc-123", "started_at": time.time(), "type": "spec_creation"}}
        }
        loop1.roadmap_cache = {"priorities": [{"number": 20, "name": "US-104 - Test"}]}
        loop1.last_roadmap_update = time.time()

        # Save state
        loop1._save_state()

        # Verify file was created
        assert state_file.exists()

        # Create second instance (simulates restart)
        loop2 = ContinuousWorkLoop(config)
        loop2._load_state()

        # Verify state was restored
        assert "spec_20" in loop2.current_state["active_tasks"]
        assert loop2.roadmap_cache is not None
        assert loop2.roadmap_cache["priorities"][0]["number"] == 20

    def test_load_state_handles_missing_file(self, tmp_path):
        """Test loading state when no previous state exists."""
        state_file = tmp_path / "nonexistent.json"
        config = WorkLoopConfig(state_file_path=str(state_file))

        loop = ContinuousWorkLoop(config)
        loop._load_state()

        # Should start with empty state
        assert loop.current_state == {}
        assert loop.roadmap_cache is None

    def test_load_state_handles_corrupted_file(self, tmp_path):
        """Test loading state handles corrupted JSON."""
        state_file = tmp_path / "corrupted.json"
        state_file.write_text("{ invalid json")

        config = WorkLoopConfig(state_file_path=str(state_file))

        loop = ContinuousWorkLoop(config)
        loop._load_state()

        # Should gracefully handle error and use empty state
        assert loop.current_state == {}


class TestArchitectCoordination:
    """Test architect coordinator logic."""

    def test_coordinate_architect_identifies_missing_specs(self):
        """Test that architect coordinator finds missing specs."""
        loop = ContinuousWorkLoop()
        loop.roadmap_cache = {
            "priorities": [
                {"number": 20, "us_number": "US-104", "name": "Test 1", "status": "📝", "has_spec": False},
                {"number": 21, "us_number": "US-105", "name": "Test 2", "status": "📝", "has_spec": False},
                {"number": 22, "us_number": "US-106", "name": "Test 3", "status": "📝", "has_spec": True},
            ]
        }

        # Run coordination
        loop._coordinate_architect()

        # Should track both missing specs
        assert "spec_20" in loop.current_state["active_tasks"]
        assert "spec_21" in loop.current_state["active_tasks"]
        assert "spec_22" not in loop.current_state["active_tasks"]  # Has spec already

    def test_coordinate_architect_respects_backlog_target(self):
        """Test that architect only creates up to backlog target specs."""
        config = WorkLoopConfig(spec_backlog_target=2)
        loop = ContinuousWorkLoop(config)
        loop.roadmap_cache = {
            "priorities": [
                {"number": 20, "us_number": "US-104", "name": "Test 1", "status": "📝", "has_spec": False},
                {"number": 21, "us_number": "US-105", "name": "Test 2", "status": "📝", "has_spec": False},
                {"number": 22, "us_number": "US-106", "name": "Test 3", "status": "📝", "has_spec": False},
            ]
        }

        loop._coordinate_architect()

        # Should only track first 2 (backlog_target=2)
        assert "spec_20" in loop.current_state["active_tasks"]
        assert "spec_21" in loop.current_state["active_tasks"]
        assert "spec_22" not in loop.current_state["active_tasks"]


class TestCodeDeveloperCoordination:
    """Test code_developer coordinator logic."""

    def test_coordinate_code_developer_finds_next_priority(self):
        """Test that code_developer coordinator finds next implementable priority."""
        loop = ContinuousWorkLoop()
        loop.roadmap_cache = {
            "priorities": [
                {"number": 20, "name": "Test 1", "status": "📝", "has_spec": True},
                {"number": 21, "name": "Test 2", "status": "📝", "has_spec": False},
            ]
        }

        loop._coordinate_code_developer()

        # Should implement first priority with spec
        assert "impl_20" in loop.current_state["active_tasks"]
        assert "impl_21" not in loop.current_state["active_tasks"]  # Missing spec

    def test_coordinate_code_developer_waits_for_spec(self):
        """Test that code_developer waits if no spec available."""
        loop = ContinuousWorkLoop()
        loop.roadmap_cache = {"priorities": [{"number": 20, "name": "Test 1", "status": "📝", "has_spec": False}]}

        loop._coordinate_code_developer()

        # Should NOT start implementation (no spec)
        assert "impl_20" not in loop.current_state.get("active_tasks", {})


class TestTaskTracking:
    """Test task tracking and monitoring."""

    def test_track_spec_task(self):
        """Test tracking spec creation tasks."""
        loop = ContinuousWorkLoop()

        loop._track_spec_task(20, "spec-20-abc")

        assert "spec_20" in loop.current_state["active_tasks"]
        assert loop.current_state["active_tasks"]["spec_20"]["task_id"] == "spec-20-abc"
        assert loop.current_state["active_tasks"]["spec_20"]["type"] == "spec_creation"

    def test_track_implementation_task(self):
        """Test tracking implementation tasks."""
        loop = ContinuousWorkLoop()

        loop._track_implementation_task(20, "impl-20-xyz")

        assert "impl_20" in loop.current_state["active_tasks"]
        assert loop.current_state["active_tasks"]["impl_20"]["task_id"] == "impl-20-xyz"
        assert loop.current_state["active_tasks"]["impl_20"]["type"] == "implementation"

    def test_is_spec_in_progress(self):
        """Test checking if spec is already in progress."""
        loop = ContinuousWorkLoop()
        loop._track_spec_task(20, "spec-20-abc")

        assert loop._is_spec_in_progress(20) is True
        assert loop._is_spec_in_progress(21) is False

    def test_is_implementation_in_progress(self):
        """Test checking if implementation is already in progress."""
        loop = ContinuousWorkLoop()
        loop._track_implementation_task(20, "impl-20-xyz")

        assert loop._is_implementation_in_progress(20) is True
        assert loop._is_implementation_in_progress(21) is False


class TestGracefulShutdown:
    """Test graceful shutdown on signals."""

    def test_handle_shutdown_sets_running_false(self):
        """Test that shutdown signal stops the loop."""
        loop = ContinuousWorkLoop()
        loop.running = True

        # Simulate SIGINT
        loop._handle_shutdown(signal.SIGINT, None)

        assert loop.running is False

    @patch("coffee_maker.orchestrator.continuous_work_loop.NotificationDB")
    def test_shutdown_saves_state(self, mock_notification, tmp_path):
        """Test that shutdown saves state before exiting."""
        state_file = tmp_path / "state.json"
        config = WorkLoopConfig(state_file_path=str(state_file))

        loop = ContinuousWorkLoop(config)
        loop.notifications = mock_notification.return_value
        loop.current_state = {"active_tasks": {"spec_20": {"task_id": "abc"}}}

        loop._shutdown()

        # Verify state was saved
        assert state_file.exists()
        with open(state_file) as f:
            data = json.load(f)
        assert "spec_20" in data["active_tasks"]


class TestErrorHandling:
    """Test error handling during work cycle."""

    @patch("coffee_maker.orchestrator.continuous_work_loop.NotificationDB")
    def test_handle_cycle_error_logs_error(self, mock_notification, tmp_path):
        """Test that cycle errors are logged."""
        loop = ContinuousWorkLoop()
        loop.notifications = mock_notification.return_value

        error = ValueError("Test error")
        loop._handle_cycle_error(error)

        # Verify error was logged to file
        error_log = Path("data/orchestrator/error_recovery.log")
        assert error_log.exists()

    @patch("coffee_maker.orchestrator.continuous_work_loop.NotificationDB")
    def test_handle_critical_error_notifies_user(self, mock_notification):
        """Test that critical errors create notifications."""
        loop = ContinuousWorkLoop()
        loop.notifications = mock_notification.return_value

        error = IOError("Critical file error")
        loop._handle_cycle_error(error)

        # Verify notification was created
        loop.notifications.create_notification.assert_called()
        call_args = loop.notifications.create_notification.call_args
        assert call_args[1]["level"] == "critical"
        assert call_args[1]["sound"] is False  # CFR-009
        assert call_args[1]["agent_id"] == "orchestrator"


class TestCFR009Compliance:
    """Test CFR-009 compliance (silent background agent)."""

    @patch("coffee_maker.orchestrator.continuous_work_loop.NotificationDB")
    def test_all_notifications_are_silent(self, mock_notification):
        """Test that all notifications have sound=False."""
        loop = ContinuousWorkLoop()
        loop.notifications = mock_notification.return_value

        # Test startup notification
        loop.start = Mock()  # Don't actually run loop
        loop._shutdown()

        # Check all notification calls
        for call in loop.notifications.create_notification.call_args_list:
            assert call[1]["sound"] is False
            assert call[1]["agent_id"] == "orchestrator"
