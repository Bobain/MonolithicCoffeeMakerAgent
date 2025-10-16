"""Unit tests for UpdateScheduler.

Tests for US-017 Phase 4: Automatic Updates & Smart Detection
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.reports.update_scheduler import (
    EstimateChange,
    UpdateScheduler,
    UpdateState,
)


@pytest.fixture
def temp_roadmap(tmp_path):
    """Create a temporary ROADMAP.md file for testing."""
    roadmap_file = tmp_path / "ROADMAP.md"
    roadmap_content = """# Coffee Maker Roadmap

## User Stories

### 🎯 [US-017] Summary & Calendar

**Status**: ✅ Complete

**Estimated Effort**: 5-7 days

**I want**: Proactive delivery summaries and calendar

**So that**: Better visibility, reduced status questions

### 🎯 [US-018] Future Feature

**Status**: 📝 Planned

**Estimated Effort**: 10-12 days

**I want**: Some future feature

**So that**: Improved system

### 🎯 [US-019] Another Feature

**Status**: 📝 Planned

**Estimated Effort**: 3-4 days

**I want**: Another feature

**So that**: More improvements
"""
    roadmap_file.write_text(roadmap_content)
    return roadmap_file


@pytest.fixture
def temp_coffee_maker_dir(tmp_path, monkeypatch):
    """Create temporary .coffee_maker directory."""
    coffee_dir = tmp_path / ".coffee_maker"
    coffee_dir.mkdir()

    # Mock Path.home() to return tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    return coffee_dir


@pytest.fixture
def scheduler(temp_roadmap, temp_coffee_maker_dir):
    """Create UpdateScheduler instance for testing."""
    return UpdateScheduler(roadmap_path=str(temp_roadmap), update_interval_days=3, estimate_change_threshold=1.0)


# ==================== TEST UPDATE STATE ====================


def test_update_state_creation():
    """Test UpdateState creation."""
    now = datetime.now()
    state = UpdateState(last_update=now, update_count=5, last_manual_update=now)

    assert state.last_update == now
    assert state.update_count == 5
    assert state.last_manual_update == now


def test_update_state_without_manual():
    """Test UpdateState creation without manual update."""
    now = datetime.now()
    state = UpdateState(last_update=now, update_count=3)

    assert state.last_update == now
    assert state.update_count == 3
    assert state.last_manual_update is None


# ==================== TEST ESTIMATE CHANGE ====================


def test_estimate_change_creation():
    """Test EstimateChange creation."""
    change = EstimateChange(
        story_id="US-017",
        old_min_days=5.0,
        old_max_days=7.0,
        new_min_days=8.0,
        new_max_days=10.0,
        delta=3.0,
    )

    assert change.story_id == "US-017"
    assert change.old_min_days == 5.0
    assert change.old_max_days == 7.0
    assert change.new_min_days == 8.0
    assert change.new_max_days == 10.0
    assert change.delta == 3.0


# ==================== TEST SCHEDULER INITIALIZATION ====================


def test_scheduler_initialization(scheduler):
    """Test UpdateScheduler initialization."""
    assert scheduler.update_interval_days == 3
    assert scheduler.estimate_change_threshold == 1.0
    assert scheduler.state_file.name == "last_summary_update.json"
    assert scheduler.estimates_file.name == "previous_estimates.json"


def test_scheduler_initialization_missing_roadmap(tmp_path):
    """Test UpdateScheduler with missing ROADMAP.md."""
    with pytest.raises(FileNotFoundError, match="ROADMAP not found"):
        UpdateScheduler(roadmap_path=str(tmp_path / "missing.md"))


# ==================== TEST TIME-BASED UPDATES ====================


def test_should_update_no_previous_state(scheduler):
    """Test should_update returns True when no previous state exists."""
    assert scheduler.should_update() is True


def test_should_update_time_elapsed(scheduler):
    """Test should_update returns True when interval elapsed."""
    # Create state file with old timestamp
    old_time = datetime.now() - timedelta(days=4)
    state = UpdateState(last_update=old_time, update_count=1)
    scheduler._save_state(state)

    assert scheduler.should_update() is True


def test_should_update_time_not_elapsed(scheduler):
    """Test should_update returns False when interval not elapsed."""
    # Create state file with recent timestamp
    recent_time = datetime.now() - timedelta(days=1)
    state = UpdateState(last_update=recent_time, update_count=1)
    scheduler._save_state(state)

    # Also save empty estimates to avoid estimate change trigger
    scheduler._save_estimates({})

    assert scheduler.should_update() is False


def test_should_update_force(scheduler):
    """Test should_update returns True when forced."""
    # Create state file with recent timestamp
    recent_time = datetime.now() - timedelta(hours=1)
    state = UpdateState(last_update=recent_time, update_count=1)
    scheduler._save_state(state)

    assert scheduler.should_update(force=True) is True


# ==================== TEST TIME SINCE LAST UPDATE ====================


def test_get_time_since_last_update_no_state(scheduler):
    """Test get_time_since_last_update with no previous state."""
    assert scheduler.get_time_since_last_update() is None


def test_get_time_since_last_update_with_state(scheduler):
    """Test get_time_since_last_update with previous state."""
    # Create state 2 days ago
    old_time = datetime.now() - timedelta(days=2, hours=3)
    state = UpdateState(last_update=old_time, update_count=1)
    scheduler._save_state(state)

    time_since = scheduler.get_time_since_last_update()

    assert time_since is not None
    assert time_since.days == 2


# ==================== TEST ESTIMATE CHANGES ====================


def test_check_estimate_changes_no_previous(scheduler):
    """Test check_estimate_changes with no previous estimates."""
    # No previous estimates file
    changes = scheduler.check_estimate_changes()

    # Should return empty list (no baseline to compare against)
    assert changes == []


def test_check_estimate_changes_no_changes(scheduler):
    """Test check_estimate_changes with no significant changes."""
    # Save current estimates as previous
    current_estimates = scheduler._get_current_estimates()
    scheduler._save_estimates(current_estimates)

    changes = scheduler.check_estimate_changes()

    assert changes == []


def test_check_estimate_changes_significant_change(scheduler, temp_roadmap):
    """Test check_estimate_changes with significant estimate change."""
    # Save initial estimates
    initial_estimates = {
        "US-018": {"min_days": 10.0, "max_days": 12.0},
        "US-019": {"min_days": 3.0, "max_days": 4.0},
    }
    scheduler._save_estimates(initial_estimates)

    # Modify ROADMAP to change US-018 estimate (10-12 → 15-17 days = +5.5 delta)
    content = temp_roadmap.read_text()
    content = content.replace("**Estimated Effort**: 10-12 days", "**Estimated Effort**: 15-17 days")
    temp_roadmap.write_text(content)

    # Recreate scheduler to pick up changes
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap), update_interval_days=3, estimate_change_threshold=1.0)
    scheduler._save_estimates(initial_estimates)  # Restore previous estimates

    changes = scheduler.check_estimate_changes()

    assert len(changes) == 1
    assert changes[0].story_id == "US-018"
    assert changes[0].old_min_days == 10.0
    assert changes[0].old_max_days == 12.0
    assert changes[0].new_min_days == 15.0
    assert changes[0].new_max_days == 17.0
    assert changes[0].delta == pytest.approx(5.0, abs=0.1)


def test_check_estimate_changes_below_threshold(scheduler, temp_roadmap):
    """Test check_estimate_changes with change below threshold."""
    # Save initial estimates
    initial_estimates = {
        "US-019": {"min_days": 3.0, "max_days": 4.0},
    }
    scheduler._save_estimates(initial_estimates)

    # Modify ROADMAP to change US-019 estimate slightly (3-4 → 3-5 days = +0.5 delta)
    content = temp_roadmap.read_text()
    content = content.replace("**Estimated Effort**: 3-4 days", "**Estimated Effort**: 3-5 days")
    temp_roadmap.write_text(content)

    # Recreate scheduler
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap), update_interval_days=3, estimate_change_threshold=1.0)
    scheduler._save_estimates(initial_estimates)

    changes = scheduler.check_estimate_changes()

    # Change is 0.5 days, below 1.0 threshold
    assert len(changes) == 0


# ==================== TEST RECORD UPDATE ====================


def test_record_update_new_state(scheduler):
    """Test record_update creates new state when none exists."""
    scheduler.record_update(manual=False)

    state = scheduler._load_state()

    assert state is not None
    assert state.update_count == 1
    assert state.last_manual_update is None
    assert (datetime.now() - state.last_update).total_seconds() < 5


def test_record_update_increments_count(scheduler):
    """Test record_update increments count."""
    # Create initial state
    old_time = datetime.now() - timedelta(days=1)
    state = UpdateState(last_update=old_time, update_count=5)
    scheduler._save_state(state)

    # Record update
    scheduler.record_update(manual=False)

    # Load updated state
    new_state = scheduler._load_state()

    assert new_state.update_count == 6


def test_record_update_manual(scheduler):
    """Test record_update sets manual update timestamp."""
    scheduler.record_update(manual=True)

    state = scheduler._load_state()

    assert state.last_manual_update is not None
    assert (datetime.now() - state.last_manual_update).total_seconds() < 5


def test_record_update_saves_estimates(scheduler):
    """Test record_update saves current estimates."""
    scheduler.record_update()

    # Check estimates file was created
    assert scheduler.estimates_file.exists()

    estimates = scheduler._load_estimates()

    # Should have estimates from ROADMAP
    assert "US-018" in estimates
    assert "US-019" in estimates


# ==================== TEST GET UPDATE SUMMARY ====================


def test_get_update_summary_no_state(scheduler):
    """Test get_update_summary with no previous state."""
    summary = scheduler.get_update_summary()

    assert summary["last_update"] is None
    assert summary["update_count"] == 0
    assert summary["last_manual_update"] is None
    assert summary["time_since_update"] is None


def test_get_update_summary_with_state(scheduler):
    """Test get_update_summary with previous state."""
    # Create state
    last_update = datetime.now() - timedelta(days=2)
    state = UpdateState(last_update=last_update, update_count=10, last_manual_update=last_update)
    scheduler._save_state(state)

    summary = scheduler.get_update_summary()

    assert summary["update_count"] == 10
    assert summary["last_update"] is not None
    assert summary["last_manual_update"] is not None


# ==================== TEST STATE PERSISTENCE ====================


def test_state_save_and_load(scheduler):
    """Test saving and loading state."""
    now = datetime.now()
    state = UpdateState(last_update=now, update_count=7, last_manual_update=now)

    scheduler._save_state(state)

    loaded_state = scheduler._load_state()

    assert loaded_state is not None
    assert loaded_state.update_count == 7
    assert abs((loaded_state.last_update - now).total_seconds()) < 1
    assert abs((loaded_state.last_manual_update - now).total_seconds()) < 1


def test_state_load_corrupted(scheduler):
    """Test loading corrupted state file."""
    # Write invalid JSON
    scheduler.state_file.write_text("invalid json{")

    state = scheduler._load_state()

    assert state is None


# ==================== TEST ESTIMATES PERSISTENCE ====================


def test_estimates_save_and_load(scheduler):
    """Test saving and loading estimates."""
    estimates = {
        "US-018": {"min_days": 10.0, "max_days": 12.0},
        "US-019": {"min_days": 3.0, "max_days": 4.0},
    }

    scheduler._save_estimates(estimates)

    loaded_estimates = scheduler._load_estimates()

    assert loaded_estimates == estimates


def test_estimates_load_missing(scheduler):
    """Test loading estimates when file doesn't exist."""
    estimates = scheduler._load_estimates()

    assert estimates == {}


def test_estimates_load_corrupted(scheduler):
    """Test loading corrupted estimates file."""
    # Write invalid JSON
    scheduler.estimates_file.write_text("corrupted[")

    estimates = scheduler._load_estimates()

    assert estimates == {}


# ==================== TEST EXTRACT CURRENT ESTIMATES ====================


def test_get_current_estimates(scheduler):
    """Test extracting current estimates from ROADMAP."""
    estimates = scheduler._get_current_estimates()

    # Should extract US-018 and US-019
    assert "US-018" in estimates
    assert estimates["US-018"]["min_days"] == 10.0
    assert estimates["US-018"]["max_days"] == 12.0

    assert "US-019" in estimates
    assert estimates["US-019"]["min_days"] == 3.0
    assert estimates["US-019"]["max_days"] == 4.0

    # US-017 is complete, should still be extracted
    assert "US-017" in estimates


# ==================== INTEGRATION TESTS ====================


def test_full_update_cycle(scheduler):
    """Test full update cycle: check -> record -> check again."""
    # First check - should update (no previous state)
    assert scheduler.should_update() is True

    # Record update
    scheduler.record_update()

    # Save current estimates
    current_estimates = scheduler._get_current_estimates()
    scheduler._save_estimates(current_estimates)

    # Second check - should not update (too soon)
    assert scheduler.should_update() is False

    # Force update
    assert scheduler.should_update(force=True) is True


def test_estimate_change_triggers_update(scheduler, temp_roadmap):
    """Test that estimate change triggers update even within interval."""
    # Record initial update
    scheduler.record_update()

    # Save initial estimates
    initial_estimates = scheduler._get_current_estimates()
    scheduler._save_estimates(initial_estimates)

    # Verify no update needed yet (within interval)
    assert scheduler.should_update() is False

    # Change estimate significantly
    content = temp_roadmap.read_text()
    content = content.replace("**Estimated Effort**: 10-12 days", "**Estimated Effort**: 20-25 days")
    temp_roadmap.write_text(content)

    # Recreate scheduler to pick up changes
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap), update_interval_days=3, estimate_change_threshold=1.0)

    # Save initial estimates again (before change)
    scheduler._save_estimates({"US-018": {"min_days": 10.0, "max_days": 12.0}})

    # Now update should be needed due to estimate change
    assert scheduler.should_update() is True


def test_summary_state_after_multiple_updates(scheduler):
    """Test summary state after multiple updates."""
    # Record 3 updates
    scheduler.record_update(manual=False)
    scheduler.record_update(manual=True)
    scheduler.record_update(manual=False)

    summary = scheduler.get_update_summary()

    assert summary["update_count"] == 3
    assert summary["last_manual_update"] is not None
