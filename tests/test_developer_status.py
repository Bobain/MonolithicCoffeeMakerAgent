"""Unit tests for DeveloperStatus class.

Tests status tracking, activity logging, progress reporting, and JSON file writing.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.autonomous.developer_status import (
    ActivityType,
    DeveloperState,
    DeveloperStatus,
)
from coffee_maker.utils.file_io import read_json_file


@pytest.fixture
def temp_status_file():
    """Create temporary status file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def status(temp_status_file):
    """Create DeveloperStatus instance with temp file."""
    return DeveloperStatus(status_file=temp_status_file)


def test_initialization(status, temp_status_file):
    """Test DeveloperStatus initialization."""
    assert status.current_state == DeveloperState.IDLE
    assert status.current_task is None
    assert status.activity_log == []
    assert status.questions == []
    assert status.status_file == temp_status_file


def test_update_status_new_task(status, temp_status_file):
    """Test updating status with a new task."""
    task = {"priority": 4, "name": "Test Task"}

    status.update_status(DeveloperState.WORKING, task=task, progress=10, current_step="Starting")

    assert status.current_state == DeveloperState.WORKING
    assert status.current_task is not None
    assert status.current_task["priority"] == 4
    assert status.current_task["name"] == "Test Task"
    assert status.current_task["progress"] == 10
    assert status.current_task["current_step"] == "Starting"

    # Verify file was written
    assert temp_status_file.exists()

    # Verify file contents
    data = read_json_file(temp_status_file)

    assert data["status"] == "working"
    assert data["current_task"]["priority"] == 4
    assert data["current_task"]["name"] == "Test Task"


def test_update_status_without_task(status):
    """Test updating status without task changes progress."""
    # First set a task
    task = {"priority": 4, "name": "Test Task"}
    status.update_status(DeveloperState.WORKING, task=task, progress=10)

    # Then update without task (should update existing task)
    status.update_status(DeveloperState.WORKING, progress=50, current_step="Half done")

    assert status.current_task["progress"] == 50
    assert status.current_task["current_step"] == "Half done"


def test_report_activity(status, temp_status_file):
    """Test activity logging."""
    status.report_activity(ActivityType.GIT_COMMIT, "Test commit", details={"files": 3})

    assert len(status.activity_log) == 1
    activity = status.activity_log[0]

    assert activity["type"] == "git_commit"
    assert activity["description"] == "Test commit"
    assert activity["details"]["files"] == 3
    assert "timestamp" in activity

    # Verify metrics updated
    assert status.metrics["total_commits_today"] == 1


def test_activity_log_limit(status):
    """Test activity log keeps only last 50 entries."""
    # Add 60 activities
    for i in range(60):
        status.report_activity(ActivityType.CODE_CHANGE, f"Change {i}")

    # Should keep only last 50
    assert len(status.activity_log) == 50

    # First activity should be "Change 10" (60 - 50 = 10)
    assert "Change 10" in status.activity_log[0]["description"]


def test_report_progress(status):
    """Test progress reporting."""
    # Set initial task
    task = {"priority": 4, "name": "Test Task"}
    status.update_status(DeveloperState.WORKING, task=task, progress=0)

    # Update progress
    status.report_progress(50, "Half done")

    assert status.current_task["progress"] == 50
    assert status.current_task["current_step"] == "Half done"

    # Should log activity
    assert len(status.activity_log) > 0
    assert any("Progress: 50%" in act["description"] for act in status.activity_log)


def test_add_question(status):
    """Test adding pending questions."""
    status.add_question("q1", "dependency_approval", "Install pandas?", "Needed for CSV export")

    assert len(status.questions) == 1
    question = status.questions[0]

    assert question["id"] == "q1"
    assert question["type"] == "dependency_approval"
    assert question["message"] == "Install pandas?"
    assert question["context"] == "Needed for CSV export"
    assert question["status"] == "pending"

    # Should change state to BLOCKED
    assert status.current_state == DeveloperState.BLOCKED


def test_remove_question(status):
    """Test removing answered questions."""
    # Set initial state
    task = {"priority": 4, "name": "Test Task"}
    status.update_status(DeveloperState.WORKING, task=task)

    # Add question (changes state to BLOCKED)
    status.add_question("q1", "dependency_approval", "Install pandas?")
    assert status.current_state == DeveloperState.BLOCKED
    assert len(status.questions) == 1

    # Remove question
    status.remove_question("q1")

    assert len(status.questions) == 0
    # Should return to WORKING
    assert status.current_state == DeveloperState.WORKING


def test_remove_question_keeps_blocked_if_more_questions(status):
    """Test removing one question keeps BLOCKED state if others remain."""
    status.add_question("q1", "dependency_approval", "Install pandas?")
    status.add_question("q2", "design_decision", "Use REST or GraphQL?")

    assert len(status.questions) == 2
    assert status.current_state == DeveloperState.BLOCKED

    # Remove one question
    status.remove_question("q1")

    # Still blocked because q2 remains
    assert len(status.questions) == 1
    assert status.current_state == DeveloperState.BLOCKED


def test_task_completed(status):
    """Test marking task as completed."""
    # Set task
    task = {"priority": 4, "name": "Test Task"}
    status.update_status(DeveloperState.WORKING, task=task, progress=50)

    initial_completed = status.metrics["tasks_completed_today"]

    # Mark completed
    status.task_completed()

    assert status.current_task["progress"] == 100
    assert status.current_task["current_step"] == "Task complete"
    assert status.metrics["tasks_completed_today"] == initial_completed + 1


def test_eta_calculation_zero_progress(status):
    """Test ETA calculation with zero progress."""
    task = {"priority": 4, "name": "Test", "started_at": datetime.utcnow().isoformat() + "Z"}

    eta = status._calculate_eta(task, 0)

    # Should return 0 when no progress made
    assert eta == 0


def test_eta_calculation_with_progress(status):
    """Test ETA calculation with actual progress."""
    # Task started 1 hour ago
    started_at = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
    task = {"priority": 4, "name": "Test", "started_at": started_at}

    # 50% progress after 1 hour → ETA should be ~1 hour
    eta = status._calculate_eta(task, 50)

    # Allow some variance (3000-4000 seconds = 50-67 minutes)
    assert 3000 < eta < 4000


def test_eta_calculation_with_invalid_started_at(status):
    """Test ETA calculation handles invalid started_at."""
    task = {"priority": 4, "name": "Test"}  # No started_at

    eta = status._calculate_eta(task, 50)

    # Should return 0 for invalid data
    assert eta == 0


def test_metrics_tracking(status):
    """Test metrics are tracked correctly."""
    # Initial metrics
    assert status.metrics["tasks_completed_today"] == 0
    assert status.metrics["total_commits_today"] == 0
    assert status.metrics["tests_passed_today"] == 0
    assert status.metrics["tests_failed_today"] == 0

    # Report activities
    status.report_activity(ActivityType.GIT_COMMIT, "Commit 1")
    status.report_activity(ActivityType.GIT_COMMIT, "Commit 2")
    status.report_activity(ActivityType.TEST_PASSED, "Test passed")
    status.report_activity(ActivityType.TEST_FAILED, "Test failed")

    assert status.metrics["total_commits_today"] == 2
    assert status.metrics["tests_passed_today"] == 1
    assert status.metrics["tests_failed_today"] == 1


def test_status_file_format(status, temp_status_file):
    """Test status file has correct format."""
    task = {"priority": 4, "name": "Test Task"}
    status.update_status(DeveloperState.WORKING, task=task, progress=50)
    status.report_activity(ActivityType.GIT_COMMIT, "Test commit")

    # Read file
    data = read_json_file(temp_status_file)

    # Verify structure
    assert "status" in data
    assert "current_task" in data
    assert "last_activity" in data
    assert "activity_log" in data
    assert "questions" in data
    assert "metrics" in data
    assert "daemon_info" in data

    # Verify daemon_info
    assert "pid" in data["daemon_info"]
    assert "started_at" in data["daemon_info"]
    assert "version" in data["daemon_info"]


def test_atomic_write(status, temp_status_file):
    """Test status file is written atomically."""
    task = {"priority": 4, "name": "Test Task"}
    status.update_status(DeveloperState.WORKING, task=task)

    # File should exist
    assert temp_status_file.exists()

    # Temp file should NOT exist (atomic write completed)
    temp_file = temp_status_file.with_suffix(".tmp")
    assert not temp_file.exists()


def test_activity_log_in_file_limited_to_20(status, temp_status_file):
    """Test status file contains only last 20 activities."""
    # Add 30 activities
    for i in range(30):
        status.report_activity(ActivityType.CODE_CHANGE, f"Change {i}")

    # Read file
    data = read_json_file(temp_status_file)

    # File should contain only last 20
    assert len(data["activity_log"]) == 20

    # Memory should contain last 50
    assert len(status.activity_log) == 30


def test_developer_states_enum():
    """Test DeveloperState enum values."""
    assert DeveloperState.WORKING == "working"
    assert DeveloperState.TESTING == "testing"
    assert DeveloperState.BLOCKED == "blocked"
    assert DeveloperState.IDLE == "idle"
    assert DeveloperState.THINKING == "thinking"
    assert DeveloperState.REVIEWING == "reviewing"
    assert DeveloperState.STOPPED == "stopped"


def test_activity_types_enum():
    """Test ActivityType enum values."""
    assert ActivityType.FILE_CREATED == "file_created"
    assert ActivityType.GIT_COMMIT == "git_commit"
    assert ActivityType.TEST_RUN == "test_run"
    assert ActivityType.QUESTION_ASKED == "question_asked"
    assert ActivityType.STATUS_UPDATE == "status_update"


def test_status_survives_exception_in_write(status, temp_status_file, monkeypatch):
    """Test status update doesn't crash if file write fails."""

    # Make file write fail
    def mock_open(*args, **kwargs):
        raise PermissionError("Mock permission error")

    monkeypatch.setattr("builtins.open", mock_open)

    # Should not raise exception
    task = {"priority": 4, "name": "Test Task"}
    status.update_status(DeveloperState.WORKING, task=task)

    # Status should still be updated in memory
    assert status.current_state == DeveloperState.WORKING
    assert status.current_task["name"] == "Test Task"
