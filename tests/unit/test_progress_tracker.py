"""Tests for progress tracker UI component.

Tests the ProgressTracker class for displaying step-by-step progress
in the user_listener console UI.
"""

import pytest
from io import StringIO
from rich.console import Console
from coffee_maker.cli.progress_tracker import ProgressTracker, StepStatus


@pytest.fixture
def console():
    """Create a Rich console with string output for testing."""
    return Console(file=StringIO(), width=100)


@pytest.fixture
def progress_tracker(console):
    """Create a ProgressTracker instance."""
    return ProgressTracker(console, use_live=False)


def test_progress_tracker_initialization(progress_tracker):
    """Test progress tracker initializes correctly."""
    assert progress_tracker.current_request is None
    assert progress_tracker.steps == []
    assert progress_tracker.active_step == 0
    assert progress_tracker.live is None


def test_progress_tracker_start(progress_tracker):
    """Test starting a new progress tracking session."""
    request = "Implement authentication"
    steps = ["Step 1", "Step 2", "Step 3"]

    progress_tracker.start(request, steps)

    assert progress_tracker.current_request == request
    assert len(progress_tracker.steps) == 3
    assert all(s["status"] == StepStatus.WAITING for s in progress_tracker.steps)
    assert progress_tracker.steps[0]["name"] == "Step 1"
    assert progress_tracker.steps[1]["name"] == "Step 2"
    assert progress_tracker.steps[2]["name"] == "Step 3"


def test_progress_tracker_update_step(progress_tracker):
    """Test updating step status."""
    progress_tracker.start("Test request", ["Step 1", "Step 2", "Step 3"])

    # Update first step to active
    progress_tracker.update_step(0, StepStatus.ACTIVE)
    assert progress_tracker.steps[0]["status"] == StepStatus.ACTIVE
    assert progress_tracker.active_step == 0

    # Update first step to complete
    progress_tracker.update_step(0, StepStatus.COMPLETE)
    assert progress_tracker.steps[0]["status"] == StepStatus.COMPLETE

    # Update second step to active
    progress_tracker.update_step(1, StepStatus.ACTIVE)
    assert progress_tracker.steps[1]["status"] == StepStatus.ACTIVE
    assert progress_tracker.active_step == 1


def test_progress_tracker_complete(progress_tracker):
    """Test marking all steps as complete."""
    progress_tracker.start("Test request", ["Step 1", "Step 2", "Step 3"])

    # Set some steps to active
    progress_tracker.update_step(0, StepStatus.ACTIVE)
    progress_tracker.update_step(1, StepStatus.ACTIVE)

    # Complete all
    progress_tracker.complete()

    assert all(s["status"] == StepStatus.COMPLETE for s in progress_tracker.steps)


def test_progress_tracker_error(progress_tracker):
    """Test marking a step as error."""
    progress_tracker.start("Test request", ["Step 1", "Step 2", "Step 3"])

    error_message = "Something went wrong"
    progress_tracker.error(1, error_message)

    assert progress_tracker.steps[1]["status"] == StepStatus.ERROR
    assert progress_tracker.steps[1]["error"] == error_message


def test_progress_tracker_invalid_step_index(progress_tracker):
    """Test updating invalid step index is handled gracefully."""
    progress_tracker.start("Test request", ["Step 1", "Step 2"])

    # Try to update non-existent step
    progress_tracker.update_step(10, StepStatus.ACTIVE)
    # Should not crash, steps remain unchanged
    assert progress_tracker.steps[0]["status"] == StepStatus.WAITING
    assert progress_tracker.steps[1]["status"] == StepStatus.WAITING


def test_progress_tracker_error_does_not_affect_complete(progress_tracker):
    """Test that error steps are not changed by complete()."""
    progress_tracker.start("Test request", ["Step 1", "Step 2", "Step 3"])

    # Mark step 1 as error
    progress_tracker.error(1, "Error occurred")

    # Complete all
    progress_tracker.complete()

    # Error step should remain error
    assert progress_tracker.steps[1]["status"] == StepStatus.ERROR
    # Others should be complete
    assert progress_tracker.steps[0]["status"] == StepStatus.COMPLETE
    assert progress_tracker.steps[2]["status"] == StepStatus.COMPLETE


def test_progress_tracker_create_panel(progress_tracker):
    """Test panel creation contains expected elements."""
    progress_tracker.start("Implement feature X", ["Interpret", "Delegate", "Process", "Summarize"])

    panel = progress_tracker._create_panel()

    # Panel should have title
    assert panel.title is not None
    assert "Working on" in panel.title
    assert "Implement feature X" in panel.title


def test_progress_tracker_long_request_truncation(progress_tracker):
    """Test long request text is truncated in display."""
    long_request = "A" * 100  # Very long request
    progress_tracker.start(long_request, ["Step 1"])

    panel = progress_tracker._create_panel()

    # Title should contain truncated request
    assert "..." in panel.title
    # Title should not contain full request
    assert "A" * 100 not in panel.title


def test_step_status_enum():
    """Test StepStatus enum values."""
    assert StepStatus.WAITING.value == "waiting"
    assert StepStatus.ACTIVE.value == "active"
    assert StepStatus.COMPLETE.value == "complete"
    assert StepStatus.ERROR.value == "error"


def test_progress_tracker_workflow_sequence(progress_tracker):
    """Test a complete workflow sequence."""
    # Start tracking
    progress_tracker.start(
        "Implement authentication",
        ["Interpret request", "Delegate to agent", "Process", "Summarize"],
    )

    # Step 1: Interpret
    progress_tracker.update_step(0, StepStatus.ACTIVE)
    assert progress_tracker.steps[0]["status"] == StepStatus.ACTIVE

    progress_tracker.update_step(0, StepStatus.COMPLETE)
    assert progress_tracker.steps[0]["status"] == StepStatus.COMPLETE

    # Step 2: Delegate
    progress_tracker.update_step(1, StepStatus.ACTIVE)
    assert progress_tracker.steps[1]["status"] == StepStatus.ACTIVE

    progress_tracker.update_step(1, StepStatus.COMPLETE)
    assert progress_tracker.steps[1]["status"] == StepStatus.COMPLETE

    # Step 3: Process
    progress_tracker.update_step(2, StepStatus.ACTIVE)
    progress_tracker.update_step(2, StepStatus.COMPLETE)

    # Step 4: Summarize
    progress_tracker.update_step(3, StepStatus.ACTIVE)
    progress_tracker.update_step(3, StepStatus.COMPLETE)

    # All should be complete
    assert all(s["status"] == StepStatus.COMPLETE for s in progress_tracker.steps)


def test_progress_tracker_stop(progress_tracker):
    """Test stopping live display."""
    # Start without live
    progress_tracker.start("Test", ["Step 1"])
    progress_tracker.stop()
    assert progress_tracker.live is None

    # Start with live
    progress_tracker_live = ProgressTracker(progress_tracker.console, use_live=True)
    progress_tracker_live.start("Test", ["Step 1"])
    assert progress_tracker_live.live is not None

    progress_tracker_live.stop()
    assert progress_tracker_live.live is None
