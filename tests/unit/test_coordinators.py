"""Unit tests for Architect and CodeDeveloper coordinators.

Tests cover:
- ArchitectCoordinator: spec backlog management
- CodeDeveloperCoordinator: implementation delegation
"""

from unittest.mock import patch


from coffee_maker.orchestrator.architect_coordinator import ArchitectCoordinator
from coffee_maker.orchestrator.code_developer_coordinator import CodeDeveloperCoordinator


class TestArchitectCoordinator:
    """Test ArchitectCoordinator functionality."""

    def test_initialization(self):
        """Test coordinator initializes with correct defaults."""
        coordinator = ArchitectCoordinator()
        assert coordinator.spec_backlog_target == 3

    def test_initialization_custom_backlog(self):
        """Test coordinator accepts custom backlog target."""
        coordinator = ArchitectCoordinator(spec_backlog_target=5)
        assert coordinator.spec_backlog_target == 5

    def test_get_missing_specs(self):
        """Test identifying priorities that need specs."""
        coordinator = ArchitectCoordinator()

        # Mock _has_spec to use has_spec field from priority
        def mock_has_spec(priority):
            return priority.get("has_spec", False)

        with patch.object(coordinator, "_has_spec", side_effect=mock_has_spec):
            priorities = [
                {"number": 20, "us_number": "US-104", "has_spec": False},
                {"number": 21, "us_number": "US-105", "has_spec": True},
                {"number": 22, "us_number": "US-106", "has_spec": False},
            ]

            missing = coordinator.get_missing_specs(priorities)

            assert len(missing) == 2
            assert missing[0]["number"] == 20
            assert missing[1]["number"] == 22

    def test_get_missing_specs_sorted(self):
        """Test missing specs are returned in priority order."""
        coordinator = ArchitectCoordinator()

        priorities = [
            {"number": 30, "us_number": "US-130", "has_spec": False},
            {"number": 10, "us_number": "US-110", "has_spec": False},
            {"number": 20, "us_number": "US-120", "has_spec": False},
        ]

        missing = coordinator.get_missing_specs(priorities)

        # Should be sorted by priority number
        assert missing[0]["number"] == 10
        assert missing[1]["number"] == 20
        assert missing[2]["number"] == 30

    def test_has_spec_checks_filesystem(self, tmp_path):
        """Test _has_spec correctly checks for spec files."""
        coordinator = ArchitectCoordinator()

        # Create spec directory and file
        spec_dir = tmp_path / "docs" / "architecture" / "specs"
        spec_dir.mkdir(parents=True)
        (spec_dir / "SPEC-104-test.md").write_text("# Test spec")

        priority = {"number": 20, "us_number": "US-104", "has_spec": False}

        with patch("coffee_maker.orchestrator.architect_coordinator.Path") as mock_path:
            mock_path.return_value.glob.return_value = [spec_dir / "SPEC-104-test.md"]

            result = coordinator._has_spec(priority)
            assert result is True

    def test_has_spec_returns_false_when_missing(self, tmp_path):
        """Test _has_spec returns False when spec doesn't exist."""
        coordinator = ArchitectCoordinator()

        priority = {"number": 20, "us_number": "US-104", "has_spec": False}

        with patch("coffee_maker.orchestrator.architect_coordinator.Path") as mock_path:
            mock_path.return_value.glob.return_value = []

            result = coordinator._has_spec(priority)
            assert result is False

    def test_create_spec_backlog_respects_target(self):
        """Test create_spec_backlog only creates up to backlog_target."""
        coordinator = ArchitectCoordinator(spec_backlog_target=2)

        priorities = [
            {"number": 20, "us_number": "US-104", "has_spec": False},
            {"number": 21, "us_number": "US-105", "has_spec": False},
            {"number": 22, "us_number": "US-106", "has_spec": False},
        ]

        with patch.object(coordinator, "get_missing_specs", return_value=priorities):
            task_ids = coordinator.create_spec_backlog(priorities)

        # Should only create 2 (backlog_target=2)
        assert len(task_ids) == 2
        assert task_ids[0] == "spec-20"
        assert task_ids[1] == "spec-21"

    def test_create_spec_backlog_returns_task_ids(self):
        """Test create_spec_backlog returns correct task IDs."""
        coordinator = ArchitectCoordinator()

        priorities = [{"number": 20, "us_number": "US-104", "has_spec": False}]

        with patch.object(coordinator, "get_missing_specs", return_value=priorities):
            task_ids = coordinator.create_spec_backlog(priorities)

        assert len(task_ids) == 1
        assert task_ids[0] == "spec-20"


class TestCodeDeveloperCoordinator:
    """Test CodeDeveloperCoordinator functionality."""

    def test_initialization(self):
        """Test coordinator initializes correctly."""
        coordinator = CodeDeveloperCoordinator()
        assert coordinator is not None

    def test_get_next_implementable_priority_finds_first_with_spec(self):
        """Test finding next priority with spec."""
        coordinator = CodeDeveloperCoordinator()

        priorities = [
            {"number": 20, "name": "US-104", "status": "📝", "has_spec": False},
            {"number": 21, "name": "US-105", "status": "📝", "has_spec": True},
            {"number": 22, "name": "US-106", "status": "📝", "has_spec": True},
        ]

        next_priority = coordinator.get_next_implementable_priority(priorities)

        assert next_priority is not None
        assert next_priority["number"] == 21  # First with spec

    def test_get_next_implementable_priority_returns_none_when_no_specs(self):
        """Test returns None when no priorities have specs."""
        coordinator = CodeDeveloperCoordinator()

        priorities = [
            {"number": 20, "name": "US-104", "status": "📝", "has_spec": False},
            {"number": 21, "name": "US-105", "status": "📝", "has_spec": False},
        ]

        next_priority = coordinator.get_next_implementable_priority(priorities)

        assert next_priority is None

    def test_get_next_implementable_priority_ignores_completed(self):
        """Test ignores completed priorities."""
        coordinator = CodeDeveloperCoordinator()

        priorities = [
            {"number": 20, "name": "US-104", "status": "✅", "has_spec": True},  # Completed
            {"number": 21, "name": "US-105", "status": "📝", "has_spec": True},  # Planned
        ]

        next_priority = coordinator.get_next_implementable_priority(priorities)

        assert next_priority is not None
        assert next_priority["number"] == 21  # Skip completed

    def test_get_next_implementable_priority_ignores_in_progress(self):
        """Test ignores in-progress priorities."""
        coordinator = CodeDeveloperCoordinator()

        priorities = [
            {"number": 20, "name": "US-104", "status": "🔄", "has_spec": True},  # In Progress
            {"number": 21, "name": "US-105", "status": "📝", "has_spec": True},  # Planned
        ]

        next_priority = coordinator.get_next_implementable_priority(priorities)

        assert next_priority is not None
        assert next_priority["number"] == 21  # Skip in-progress

    def test_submit_implementation_task_returns_task_id(self):
        """Test submitting implementation task returns task ID."""
        coordinator = CodeDeveloperCoordinator()

        priority = {"number": 20, "name": "US-104 - Test"}

        task_id = coordinator.submit_implementation_task(priority)

        assert task_id == "impl-20"

    def test_submit_implementation_task_logs_submission(self):
        """Test submitting task logs correctly."""
        coordinator = CodeDeveloperCoordinator()

        priority = {"number": 20, "name": "US-104 - Test"}

        with patch("coffee_maker.orchestrator.code_developer_coordinator.logger") as mock_logger:
            coordinator.submit_implementation_task(priority)

            # Verify logging
            mock_logger.info.assert_called_once()
            assert "Queued implementation" in mock_logger.info.call_args[0][0]
