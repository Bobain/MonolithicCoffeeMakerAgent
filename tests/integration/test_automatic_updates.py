"""Integration tests for automatic updates.

Tests for US-017 Phase 4: Automatic Updates workflow
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.reports.status_tracking_updater import (
    check_and_update_if_needed,
    update_status_tracking,
)
from coffee_maker.reports.update_scheduler import UpdateScheduler


@pytest.fixture
def temp_roadmap_with_completions(tmp_path):
    """Create temporary ROADMAP.md with completed stories."""
    roadmap_file = tmp_path / "ROADMAP.md"
    roadmap_content = """# Coffee Maker Roadmap

## User Stories

### 🎯 [US-016] Technical Spec Generation

**Status**: ✅ Complete
**Completed**: 2025-10-12

**Estimated Effort**: 4-5 days
**Actual Effort**: 3.75 days

**Business Value**: Accurate delivery estimates before coding starts

**Key Features**:
- AI-assisted task breakdown
- 100 tests passing
- Interactive workflow

### 🎯 [US-017] Summary & Calendar

**Status**: 🔄 In Progress
**Started**: 2025-10-13

**Estimated Effort**: 5-7 days

**I want**: Proactive delivery summaries and calendar

**So that**: Better visibility, reduced status questions

### 🎯 [US-018] Future Feature

**Status**: 📝 Planned

**Estimated Effort**: 10-12 days

**I want**: Some future feature

**So that**: Improved system
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


# ==================== TEST AUTO-UPDATE WORKFLOW ====================


def test_first_run_auto_update(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test auto-update triggers on first run (no previous state)."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    result = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result["updated"] is True
    assert "3-day interval elapsed" in result["reason"] or "No update needed" not in result["reason"]
    assert output_file.exists()


def test_no_update_within_interval(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test no auto-update within 3-day interval."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    # First update
    result1 = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result1["updated"] is True

    # Second update immediately (within interval)
    result2 = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result2["updated"] is False
    assert "No update needed" in result2["reason"]


def test_auto_update_after_interval(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test auto-update triggers after 3-day interval."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    # Create scheduler and manually set old timestamp
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap_with_completions))

    # Simulate state from 4 days ago
    old_time = datetime.now() - timedelta(days=4)
    state_data = {
        "last_update": old_time.isoformat(),
        "update_count": 5,
        "last_manual_update": None,
    }

    with open(scheduler.state_file, "w") as f:
        json.dump(state_data, f)

    # Save empty estimates to avoid estimate change trigger
    with open(scheduler.estimates_file, "w") as f:
        json.dump({}, f)

    # Auto-update should trigger
    result = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result["updated"] is True
    assert "3-day interval elapsed" in result["reason"]


# ==================== TEST ESTIMATE CHANGE DETECTION ====================


def test_auto_update_on_estimate_change(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test auto-update triggers when estimate changes significantly."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    # Create scheduler
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap_with_completions))

    # Record initial update with estimates
    scheduler.record_update()

    # Modify estimate in ROADMAP (10-12 → 20-25 days)
    content = temp_roadmap_with_completions.read_text()
    content = content.replace("**Estimated Effort**: 10-12 days", "**Estimated Effort**: 20-25 days")
    temp_roadmap_with_completions.write_text(content)

    # Auto-update should trigger due to estimate change
    result = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result["updated"] is True
    assert "estimate change" in result["reason"].lower()


def test_no_update_on_small_estimate_change(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test no auto-update when estimate change is below threshold."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    # Create scheduler
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap_with_completions))

    # Record initial update with estimates
    scheduler.record_update()

    # Modify estimate slightly (10-12 → 10-13 days, delta = 0.5)
    content = temp_roadmap_with_completions.read_text()
    content = content.replace("**Estimated Effort**: 10-12 days", "**Estimated Effort**: 10-13 days")
    temp_roadmap_with_completions.write_text(content)

    # Auto-update should NOT trigger (change < 1.0 day threshold)
    result = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result["updated"] is False


# ==================== TEST MANUAL UPDATE ====================


def test_manual_update_force(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test manual update with force flag."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    # First update
    result1 = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result1["updated"] is True

    # Manual update immediately (force=True)
    result2 = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=True
    )

    assert result2["updated"] is True
    assert "Manual update" in result2["reason"]


# ==================== TEST STATUS_TRACKING.md GENERATION ====================


def test_status_tracking_document_created(temp_roadmap_with_completions, tmp_path):
    """Test STATUS_TRACKING.md is created with correct content."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    success = update_status_tracking(roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file))

    assert success is True
    assert output_file.exists()

    content = output_file.read_text()

    # Check document structure
    assert "STATUS TRACKING" in content
    assert "Auto-Generated Internal Document" in content
    assert "Recent Completions" in content
    assert "Current Work" in content
    assert "Next Up" in content
    assert "Velocity & Accuracy Metrics" in content

    # Check completed story appears
    assert "US-016" in content
    assert "Technical Spec Generation" in content

    # Check in-progress story appears
    assert "US-017" in content
    assert "Summary & Calendar" in content


# ==================== TEST UPDATE NOTIFICATIONS ====================


def test_update_summary_accurate(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test update summary reflects accurate state."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    # Perform multiple updates
    check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=True
    )

    check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=True
    )

    # Get summary
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap_with_completions))
    summary = scheduler.get_update_summary()

    assert summary["update_count"] >= 2
    assert summary["last_update"] is not None


# ==================== TEST ERROR HANDLING ====================


def test_update_with_missing_roadmap(tmp_path):
    """Test update gracefully handles missing ROADMAP."""
    output_file = tmp_path / "STATUS_TRACKING.md"

    result = check_and_update_if_needed(
        roadmap_path=str(tmp_path / "missing.md"), output_path=str(output_file), force=False
    )

    assert result["updated"] is False
    assert "Error" in result["reason"]


# ==================== TEST FULL WORKFLOW ====================


def test_complete_auto_update_workflow(temp_roadmap_with_completions, temp_coffee_maker_dir, tmp_path):
    """Test complete auto-update workflow over time."""
    output_file = tmp_path / "STATUS_TRACKING.md"
    scheduler = UpdateScheduler(roadmap_path=str(temp_roadmap_with_completions))

    # Day 0: First update
    result1 = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result1["updated"] is True
    assert output_file.exists()

    # Day 1: No update (within interval)
    result2 = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result2["updated"] is False

    # Simulate Day 4 (interval elapsed)
    old_time = datetime.now() - timedelta(days=4)
    state_data = {
        "last_update": old_time.isoformat(),
        "update_count": 1,
        "last_manual_update": None,
    }

    with open(scheduler.state_file, "w") as f:
        json.dump(state_data, f)

    # Day 4: Auto-update triggers
    result3 = check_and_update_if_needed(
        roadmap_path=str(temp_roadmap_with_completions), output_path=str(output_file), force=False
    )

    assert result3["updated"] is True
    assert "3-day interval elapsed" in result3["reason"]

    # Verify state updated
    summary = scheduler.get_update_summary()
    assert summary["update_count"] >= 2
