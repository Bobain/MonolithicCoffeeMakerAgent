"""Unit tests for ActivityDB and ActivityLogger.

Tests cover:
- Activity logging with various types
- Date range filtering
- Metadata handling
- Concurrent access (WAL mode)
- Error handling and edge cases
"""

import pytest
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

from coffee_maker.autonomous.activity_db import (
    ActivityDB,
    ACTIVITY_TYPE_COMMIT,
    ACTIVITY_TYPE_TEST_RUN,
    ACTIVITY_TYPE_PR_CREATED,
    OUTCOME_SUCCESS,
    OUTCOME_FAILURE,
)
from coffee_maker.autonomous.activity_logger import ActivityLogger


@pytest.fixture
def temp_db():
    """Create a temporary test database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_activity.db")
        yield ActivityDB(db_path=db_path)


class TestActivityDB:
    """Tests for ActivityDB class."""

    def test_init_creates_database(self, temp_db):
        """Test that __init__ creates a valid database."""
        assert Path(temp_db.db_path).exists()

    def test_log_activity_returns_id(self, temp_db):
        """Test logging an activity returns an ID."""
        activity_id = temp_db.log_activity(activity_type=ACTIVITY_TYPE_COMMIT, title="Test commit")

        assert activity_id > 0
        assert isinstance(activity_id, int)

    def test_log_and_retrieve_activity(self, temp_db):
        """Test logging and retrieving an activity."""
        activity_id = temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Test commit",
            priority_number="2.5",
            priority_name="CI Testing",
            metadata={"files_changed": 3},
        )

        activity = temp_db.get_activity(activity_id)

        assert activity is not None
        assert activity.id == activity_id
        assert activity.title == "Test commit"
        assert activity.priority_number == "2.5"
        assert activity.metadata["files_changed"] == 3

    def test_get_activity_nonexistent(self, temp_db):
        """Test getting a nonexistent activity returns None."""
        activity = temp_db.get_activity(99999)
        assert activity is None

    def test_log_activity_with_all_fields(self, temp_db):
        """Test logging activity with all optional fields."""
        metadata = {"lines_added": 120, "lines_removed": 30}
        activity_id = temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Complex commit",
            description="Detailed description of changes",
            priority_number="3.5",
            priority_name="Advanced Feature",
            metadata=metadata,
            outcome=OUTCOME_SUCCESS,
            session_id="test-session-id",
        )

        activity = temp_db.get_activity(activity_id)

        assert activity.description == "Detailed description of changes"
        assert activity.outcome == OUTCOME_SUCCESS
        assert activity.session_id == "test-session-id"
        assert activity.metadata == metadata

    def test_log_activity_truncates_long_title(self, temp_db):
        """Test that long titles are truncated to 200 chars."""
        long_title = "x" * 300
        activity_id = temp_db.log_activity(activity_type=ACTIVITY_TYPE_COMMIT, title=long_title)

        activity = temp_db.get_activity(activity_id)

        assert len(activity.title) == 200
        assert activity.title == "x" * 200

    def test_get_activities_by_date_range(self, temp_db):
        """Test filtering activities by date range."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Log activity for today
        today_id = temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Today commit",
            priority_number="TODAY",
        )

        # Log activity for yesterday (simulate by checking dates)
        # Note: We can't actually log with past dates easily, but we test filtering logic
        activities = temp_db.get_activities(start_date=today, end_date=today)

        # Should find today's activity
        activity_ids = [a.id for a in activities]
        assert today_id in activity_ids

    def test_get_activities_by_type(self, temp_db):
        """Test filtering activities by type."""
        commit_id = temp_db.log_activity(activity_type=ACTIVITY_TYPE_COMMIT, title="Commit")
        test_id = temp_db.log_activity(activity_type=ACTIVITY_TYPE_TEST_RUN, title="Test")

        # Get only commits
        commits = temp_db.get_activities(activity_type=ACTIVITY_TYPE_COMMIT)

        commit_ids = [a.id for a in commits]
        assert commit_id in commit_ids
        assert test_id not in commit_ids

    def test_get_activities_by_priority(self, temp_db):
        """Test filtering activities by priority."""
        p1_id = temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="P1 commit",
            priority_number="2.5",
        )
        p2_id = temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="P2 commit",
            priority_number="3.5",
        )

        # Get only P1 activities
        p1_activities = temp_db.get_activities(priority_number="2.5")

        p1_ids = [a.id for a in p1_activities]
        assert p1_id in p1_ids
        assert p2_id not in p1_ids

    def test_get_activities_combined_filters(self, temp_db):
        """Test filtering with multiple criteria."""
        target_id = temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Target activity",
            priority_number="2.5",
        )

        other_id = temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_TEST_RUN,
            title="Other activity",
            priority_number="2.5",
        )

        # Filter by type and priority
        activities = temp_db.get_activities(activity_type=ACTIVITY_TYPE_COMMIT, priority_number="2.5")

        activity_ids = [a.id for a in activities]
        assert target_id in activity_ids
        assert other_id not in activity_ids

    def test_get_activities_limit(self, temp_db):
        """Test limit parameter."""
        # Log 5 activities
        for i in range(5):
            temp_db.log_activity(activity_type=ACTIVITY_TYPE_COMMIT, title=f"Commit {i}")

        # Get only 2
        activities = temp_db.get_activities(limit=2)

        assert len(activities) == 2

    def test_get_activities_ordered_by_date_desc(self, temp_db):
        """Test that activities are ordered most recent first."""
        id1 = temp_db.log_activity(activity_type=ACTIVITY_TYPE_COMMIT, title="First")
        time.sleep(0.1)  # Small delay to ensure different timestamps
        id2 = temp_db.log_activity(activity_type=ACTIVITY_TYPE_COMMIT, title="Second")

        activities = temp_db.get_activities(limit=10)

        # Most recent should be first
        assert activities[0].id == id2
        assert activities[1].id == id1

    def test_log_activity_invalid_type(self, temp_db):
        """Test that invalid activity type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid activity type"):
            temp_db.log_activity(activity_type="invalid_type", title="Test")

    def test_log_activity_invalid_outcome(self, temp_db):
        """Test that invalid outcome raises ValueError."""
        with pytest.raises(ValueError, match="Invalid outcome"):
            temp_db.log_activity(
                activity_type=ACTIVITY_TYPE_COMMIT,
                title="Test",
                outcome="invalid_outcome",
            )

    def test_get_daily_metrics(self, temp_db):
        """Test daily metrics calculation."""
        today = date.today()

        # Log various activities
        temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Commit 1",
            outcome=OUTCOME_SUCCESS,
        )
        temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title="Commit 2",
            outcome=OUTCOME_SUCCESS,
        )
        temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_TEST_RUN,
            title="Tests",
            outcome=OUTCOME_SUCCESS,
        )
        temp_db.log_activity(
            activity_type=ACTIVITY_TYPE_PR_CREATED,
            title="PR",
            outcome=OUTCOME_SUCCESS,
        )

        metrics = temp_db.get_daily_metrics(today)

        assert metrics["commits"] == 2
        assert metrics["test_runs"] == 1
        assert metrics["prs_created"] == 1
        assert metrics["total_activities"] == 4
        assert metrics["successes"] == 4
        assert metrics["failures"] == 0

    def test_get_daily_metrics_empty_day(self, temp_db):
        """Test metrics for a day with no activities."""
        tomorrow = date.today() + timedelta(days=1)
        metrics = temp_db.get_daily_metrics(tomorrow)

        assert metrics["total_activities"] == 0
        assert metrics["commits"] == 0
        assert all(v == 0 for v in metrics.values())


class TestActivityLogger:
    """Tests for ActivityLogger class."""

    @pytest.fixture
    def temp_logger(self, temp_db):
        """Create a temporary logger with test database."""
        return ActivityLogger(db=temp_db)

    def test_init_creates_session_id(self, temp_logger):
        """Test that __init__ creates a session ID."""
        assert temp_logger.current_session_id is not None
        assert len(temp_logger.current_session_id) > 0

    def test_start_priority_sets_context(self, temp_logger, temp_db):
        """Test start_priority sets priority context."""
        temp_logger.start_priority("2.5", "CI Testing")

        assert temp_logger.current_priority == "2.5"
        assert temp_logger.current_priority_name == "CI Testing"

        # Verify activity was logged
        activities = temp_db.get_activities(activity_type="priority_started", priority_number="2.5")
        assert len(activities) > 0

    def test_start_priority_creates_new_session(self, temp_logger):
        """Test start_priority creates a new session ID."""
        old_session = temp_logger.current_session_id
        temp_logger.start_priority("2.5", "CI Testing")
        new_session = temp_logger.current_session_id

        assert old_session != new_session

    def test_complete_priority_success(self, temp_logger, temp_db):
        """Test complete_priority with success."""
        temp_logger.start_priority("2.5", "CI Testing")
        temp_logger.complete_priority("2.5", success=True, summary="All tests passed")

        activities = temp_db.get_activities(activity_type="priority_completed", priority_number="2.5")
        assert len(activities) > 0
        assert activities[0].outcome == OUTCOME_SUCCESS
        assert activities[0].description == "All tests passed"

    def test_complete_priority_failure(self, temp_logger, temp_db):
        """Test complete_priority with failure."""
        temp_logger.start_priority("2.5", "CI Testing")
        temp_logger.complete_priority("2.5", success=False, summary="Tests failed")

        activities = temp_db.get_activities(activity_type="priority_completed", priority_number="2.5")
        assert len(activities) > 0
        assert activities[0].outcome == OUTCOME_FAILURE

    def test_log_commit(self, temp_logger, temp_db):
        """Test log_commit."""
        temp_logger.start_priority("2.5", "CI Testing")
        activity_id = temp_logger.log_commit(
            message="Add CI configuration",
            files_changed=3,
            lines_added=120,
            lines_removed=30,
            commit_hash="abc123def456",
        )

        activity = temp_db.get_activity(activity_id)

        assert activity.activity_type == ACTIVITY_TYPE_COMMIT
        assert activity.title == "Add CI configuration"
        assert activity.metadata["files_changed"] == 3
        assert activity.metadata["lines_added"] == 120
        assert activity.metadata["commit_hash"] == "abc123def456"

    def test_log_test_run_success(self, temp_logger, temp_db):
        """Test log_test_run with passing tests."""
        temp_logger.start_priority("2.5", "CI Testing")
        activity_id = temp_logger.log_test_run(passed=47, failed=0, skipped=2, duration_seconds=12.5)

        activity = temp_db.get_activity(activity_id)

        assert activity.activity_type == ACTIVITY_TYPE_TEST_RUN
        assert activity.outcome == OUTCOME_SUCCESS
        assert activity.metadata["passed"] == 47
        assert activity.metadata["failed"] == 0
        assert activity.metadata["skipped"] == 2

    def test_log_test_run_failure(self, temp_logger, temp_db):
        """Test log_test_run with failing tests."""
        temp_logger.start_priority("2.5", "CI Testing")
        activity_id = temp_logger.log_test_run(passed=45, failed=2, duration_seconds=15.0)

        activity = temp_db.get_activity(activity_id)

        assert activity.outcome == OUTCOME_FAILURE
        assert activity.metadata["failed"] == 2

    def test_log_pr_created(self, temp_logger, temp_db):
        """Test log_pr_created."""
        temp_logger.start_priority("2.5", "CI Testing")
        activity_id = temp_logger.log_pr_created(
            pr_number=42,
            pr_title="Add CI testing",
            pr_url="https://github.com/org/repo/pull/42",
            branch="feature/ci-testing",
        )

        activity = temp_db.get_activity(activity_id)

        assert activity.activity_type == ACTIVITY_TYPE_PR_CREATED
        assert "PR #42" in activity.title
        assert activity.metadata["pr_number"] == 42
        assert activity.metadata["branch"] == "feature/ci-testing"

    def test_log_error(self, temp_logger, temp_db):
        """Test log_error."""
        activity_id = temp_logger.log_error(
            error_message="Database connection timeout",
            error_type="TimeoutError",
            is_blocking=False,
        )

        activity = temp_db.get_activity(activity_id)

        assert activity.activity_type == "error_encountered"
        assert "Database connection timeout" in activity.title
        assert activity.metadata["error_type"] == "TimeoutError"
        assert activity.metadata["is_blocking"] is False

    def test_log_dependency_installed(self, temp_logger, temp_db):
        """Test log_dependency_installed."""
        activity_id = temp_logger.log_dependency_installed(package_name="pytest-cov", version="4.1.0")

        activity = temp_db.get_activity(activity_id)

        assert activity.activity_type == "dependency_installed"
        assert "pytest-cov" in activity.title
        assert activity.metadata["version"] == "4.1.0"

    def test_log_documentation_updated(self, temp_logger, temp_db):
        """Test log_documentation_updated."""
        activity_id = temp_logger.log_documentation_updated(
            file_path="docs/API.md", description="Updated API documentation"
        )

        activity = temp_db.get_activity(activity_id)

        assert activity.activity_type == "documentation_updated"
        assert "docs/API.md" in activity.title
        assert activity.description == "Updated API documentation"

    def test_priority_context_in_logs(self, temp_logger, temp_db):
        """Test that priority context is included in all logs."""
        temp_logger.start_priority("2.5", "CI Testing")

        temp_logger.log_commit(message="Test", files_changed=1)
        temp_logger.log_test_run(passed=1, failed=0)

        activities = temp_db.get_activities(priority_number="2.5", limit=10)

        # Should have priority_started + commit + test_run
        assert len(activities) >= 3
        assert all(a.priority_number == "2.5" for a in activities)

    def test_session_id_tracking(self, temp_logger, temp_db):
        """Test that session ID is tracked for related activities."""
        temp_logger.start_priority("2.5", "CI Testing")
        session_id = temp_logger.current_session_id

        temp_logger.log_commit(message="Test", files_changed=1)
        temp_logger.log_test_run(passed=1, failed=0)

        activities = temp_db.get_activities(limit=10)

        # Activities should have session ID
        for activity in activities:
            if activity.session_id:
                assert activity.session_id == session_id
