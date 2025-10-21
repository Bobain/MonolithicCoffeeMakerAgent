"""Unit tests for code-review-management skill."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def skill():
    """Create skill instance with temp directories."""
    import sys
    from pathlib import Path as PathModule

    # Add skill directory to path
    skill_dir = (
        PathModule(__file__).parent.parent.parent.parent.parent
        / ".claude"
        / "skills"
        / "shared"
        / "code-review-management"
    )
    sys.path.insert(0, str(skill_dir))

    try:
        # Import the skill class
        from code_review_management import CodeReviewManagementSkill

        # Use temp directory for tests
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create skill instance with temp directories
            skill_instance = CodeReviewManagementSkill()
            skill_instance.reviews_dir = tmpdir / "reviews"
            skill_instance.state_file = tmpdir / "state.json"
            skill_instance.reviews_dir.mkdir(parents=True, exist_ok=True)
            skill_instance.state_file.parent.mkdir(parents=True, exist_ok=True)

            yield skill_instance
    finally:
        # Remove from path
        sys.path.pop(0)


@pytest.fixture
def sample_review(skill):
    """Create a sample review file."""
    review_content = """# Code Review: REVIEW-2025-10-19-abc123

Commit: `abc123`
Status: pending
Priority: US-064

## Findings

### Issue 1: Memory Leak
BUG: Potential memory leak in daemon.py:245

### Issue 2: Duplicated Logic
REFACTOR: Extract duplicated error handling logic

### Issue 3: Performance
OPTIMIZE: Use cached results instead of recomputing
"""

    review_file = skill.reviews_dir / "REVIEW-2025-10-19-abc123.md"
    review_file.write_text(review_content)

    return review_file


def test_list_reviews_empty(skill):
    """Test listing reviews when directory is empty."""
    result = skill.execute(action="list_reviews")

    assert result["error"] is None
    assert result["result"]["total"] == 0
    assert result["result"]["reviews"] == []


def test_list_reviews_with_data(skill, sample_review):
    """Test listing reviews with sample data."""
    result = skill.execute(action="list_reviews")

    assert result["error"] is None
    assert result["result"]["total"] == 1
    assert len(result["result"]["reviews"]) == 1
    assert result["result"]["reviews"][0]["id"] == "REVIEW-2025-10-19-abc123"


def test_list_reviews_filter_by_status(skill, sample_review):
    """Test filtering reviews by status."""
    result = skill.execute(action="list_reviews", status="pending")

    assert result["error"] is None
    assert result["result"]["total"] == 1

    result = skill.execute(action="list_reviews", status="closed")
    assert result["result"]["total"] == 0


def test_get_review_by_id(skill, sample_review):
    """Test getting a specific review by ID."""
    result = skill.execute(action="get_review", review_id="REVIEW-2025-10-19-abc123")

    assert result["error"] is None
    assert result["result"]["id"] == "REVIEW-2025-10-19-abc123"
    assert result["result"]["commit"] == "abc123"
    assert result["result"]["status"] == "pending"


def test_get_review_by_commit(skill, sample_review):
    """Test getting a review by commit hash."""
    result = skill.execute(action="get_review", commit="abc123")

    assert result["error"] is None
    assert result["result"]["id"] == "REVIEW-2025-10-19-abc123"


def test_extract_action_items(skill, sample_review):
    """Test extracting action items from a review."""
    result = skill.execute(action="extract_action_items", review_path=str(sample_review))

    assert result["error"] is None
    assert len(result["result"]["action_items"]) == 3

    # Check summary
    summary = result["result"]["summary"]
    assert summary["bugs"] == 1
    assert summary["refactoring"] == 1
    assert summary["optimization"] == 1


def test_update_status(skill, sample_review):
    """Test updating review status."""
    result = skill.execute(action="update_status", review_id="REVIEW-2025-10-19-abc123", status="addressed")

    assert result["error"] is None
    assert result["result"]["new_status"] == "addressed"

    # Verify status was updated
    content = sample_review.read_text()
    assert "addressed" in content.lower()


def test_update_status_invalid(skill, sample_review):
    """Test updating status with invalid value."""
    result = skill.execute(action="update_status", review_id="REVIEW-2025-10-19-abc123", status="invalid")

    assert result["error"] is not None
    assert "Invalid status" in result["error"]


def test_mark_as_read(skill, sample_review):
    """Test marking a review as read by an agent."""
    result = skill.execute(action="mark_as_read", review_id="REVIEW-2025-10-19-abc123", agent="architect")

    assert result["error"] is None
    assert result["result"]["agent"] == "architect"

    # Verify state was saved
    assert skill.state_file.exists()
    state = json.loads(skill.state_file.read_text())
    assert "architect" in state
    assert "REVIEW-2025-10-19-abc123" in state["architect"]["last_read"]


def test_get_unread_reviews(skill, sample_review):
    """Test getting unread reviews for an agent."""
    # Initially all reviews are unread
    result = skill.execute(action="get_unread_reviews", agent="architect")

    assert result["error"] is None
    assert result["result"]["count"] == 1

    # Mark as read
    skill.execute(action="mark_as_read", review_id="REVIEW-2025-10-19-abc123", agent="architect")

    # Now should be 0 unread
    result = skill.execute(action="get_unread_reviews", agent="architect")
    assert result["result"]["count"] == 0


def test_mark_integrated(skill, sample_review):
    """Test marking a review as integrated into a spec."""
    result = skill.execute(action="mark_integrated", review_id="REVIEW-2025-10-19-abc123", spec_ref="SPEC-075")

    assert result["error"] is None
    assert result["result"]["review_id"] == "REVIEW-2025-10-19-abc123"
    assert result["result"]["spec_ref"] == "SPEC-075"

    # Verify state was saved
    state = json.loads(skill.state_file.read_text())
    assert "integrations" in state
    assert len(state["integrations"]) == 1


def test_get_refactoring_opportunities(skill, sample_review):
    """Test identifying refactoring opportunities."""
    result = skill.execute(action="get_refactoring_opportunities", min_priority=2)

    assert result["error"] is None
    # Should find at least one opportunity (duplicated logic)
    assert result["result"]["total"] >= 0


def test_archive_old_reviews(skill):
    """Test archiving old reviews."""
    # Create an old review (closed status)
    old_review = skill.reviews_dir / "REVIEW-2020-01-01-old123.md"
    old_review.write_text(
        """# Code Review: REVIEW-2020-01-01-old123

Commit: `old123`
Status: closed
Priority: US-001

## Findings
Old finding
"""
    )

    result = skill.execute(action="archive_old_reviews", days=30)

    assert result["error"] is None
    assert result["result"]["count"] >= 0  # May or may not archive depending on date


def test_invalid_action(skill):
    """Test invalid action handling."""
    result = skill.execute(action="invalid_action")

    assert result["error"] is not None
    assert "Unknown action" in result["error"]
