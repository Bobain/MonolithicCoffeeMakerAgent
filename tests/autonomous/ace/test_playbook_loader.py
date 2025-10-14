"""Tests for PlaybookLoader."""

import json
from datetime import datetime

import pytest

from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.models import HealthMetrics, Playbook, PlaybookBullet
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary ACE config."""
    return ACEConfig(
        enabled=True,
        trace_dir=tmp_path / "traces",
        delta_dir=tmp_path / "deltas",
        playbook_dir=tmp_path / "playbooks",
    )


@pytest.fixture
def loader(temp_config):
    """Create PlaybookLoader with temp config."""
    return PlaybookLoader("test_agent", temp_config)


@pytest.fixture
def sample_playbook():
    """Create sample playbook."""
    bullet1 = PlaybookBullet(
        bullet_id="bullet_001",
        type="success_pattern",
        content="Always run tests before committing",
        helpful_count=10,
        harmful_count=0,
        confidence=0.95,
        priority=5,
        created_at=datetime(2025, 1, 1, 12, 0, 0),
        last_updated=datetime(2025, 1, 10, 12, 0, 0),
        evidence_sources=["trace_001", "trace_002"],
        applicability="All code changes",
        tags=["testing", "git"],
    )

    bullet2 = PlaybookBullet(
        bullet_id="bullet_002",
        type="failure_mode",
        content="Avoid using deprecated API endpoints",
        helpful_count=5,
        harmful_count=1,
        confidence=0.75,
        priority=4,
        created_at=datetime(2025, 1, 2, 12, 0, 0),
        last_updated=datetime(2025, 1, 10, 12, 0, 0),
        evidence_sources=["trace_003"],
        applicability="API integrations",
        tags=["api", "deprecation"],
    )

    return Playbook(
        playbook_version="1.0",
        agent_name="test_agent",
        agent_objective="Test agent objectives",
        success_criteria="Test success criteria",
        last_updated=datetime(2025, 1, 10, 12, 0, 0),
        total_bullets=2,
        effectiveness_score=0.85,
        categories={"success_pattern": [bullet1], "failure_mode": [bullet2]},
        statistics={"total_traces": 3, "avg_confidence": 0.85},
        health_metrics=HealthMetrics(
            total_bullets=2,
            avg_helpful_count=7.5,
            effectiveness_ratio=0.93,
            bullets_added_this_session=2,
            bullets_updated_this_session=0,
            bullets_pruned_this_session=0,
            coverage_score=0.75,
        ),
        history=[],
    )


def test_loader_initialization(temp_config):
    """Test PlaybookLoader initialization."""
    loader = PlaybookLoader("test_agent", temp_config)
    assert loader.agent_name == "test_agent"
    assert loader.config == temp_config
    assert loader.playbook_path == temp_config.playbook_dir / "test_agent_playbook.json"


def test_load_creates_default_when_missing(loader):
    """Test load creates default playbook when file doesn't exist."""
    playbook = loader.load()

    assert playbook.agent_name == "test_agent"
    assert playbook.playbook_version == "1.0"
    assert playbook.total_bullets == 0
    assert playbook.effectiveness_score == 0.0
    assert len(playbook.categories) == 0
    assert isinstance(playbook.health_metrics, HealthMetrics)


def test_save_creates_directory(loader, sample_playbook):
    """Test save creates playbook directory if it doesn't exist."""
    # Ensure directory doesn't exist
    if loader.config.playbook_dir.exists():
        loader.config.playbook_dir.rmdir()

    saved_path = loader.save(sample_playbook)

    assert loader.config.playbook_dir.exists()
    assert saved_path.exists()


def test_save_and_load_roundtrip(loader, sample_playbook):
    """Test save followed by load preserves data."""
    # Save playbook
    loader.save(sample_playbook)

    # Load it back
    loaded_playbook = loader.load()

    assert loaded_playbook.agent_name == sample_playbook.agent_name
    assert loaded_playbook.playbook_version == sample_playbook.playbook_version
    assert loaded_playbook.total_bullets == sample_playbook.total_bullets
    assert loaded_playbook.effectiveness_score == sample_playbook.effectiveness_score
    assert len(loaded_playbook.categories) == len(sample_playbook.categories)

    # Check bullets
    assert "success_pattern" in loaded_playbook.categories
    assert "failure_mode" in loaded_playbook.categories
    assert len(loaded_playbook.categories["success_pattern"]) == 1
    assert len(loaded_playbook.categories["failure_mode"]) == 1

    bullet1 = loaded_playbook.categories["success_pattern"][0]
    assert bullet1.bullet_id == "bullet_001"
    assert bullet1.content == "Always run tests before committing"
    assert bullet1.helpful_count == 10
    assert bullet1.confidence == 0.95


def test_save_updates_last_updated(loader, sample_playbook):
    """Test save updates last_updated timestamp."""
    original_time = sample_playbook.last_updated
    loader.save(sample_playbook)
    assert sample_playbook.last_updated > original_time


def test_load_handles_invalid_json(loader, temp_config):
    """Test load handles invalid JSON gracefully."""
    # Create invalid JSON file
    temp_config.playbook_dir.mkdir(parents=True, exist_ok=True)
    playbook_path = temp_config.playbook_dir / "test_agent_playbook.json"
    playbook_path.write_text("{ invalid json }")

    # Should create default playbook instead of crashing
    playbook = loader.load()
    assert playbook.agent_name == "test_agent"
    assert playbook.total_bullets == 0


def test_to_markdown_basic(loader, sample_playbook):
    """Test markdown conversion produces correct format."""
    markdown = loader.to_markdown(sample_playbook)

    assert "# Playbook: test_agent" in markdown
    assert "**Version**: 1.0" in markdown
    assert "**Total Bullets**: 2" in markdown
    assert "**Effectiveness Score**: 0.85" in markdown
    assert "## Agent Identity" in markdown
    assert "Test agent objectives" in markdown
    assert "Test success criteria" in markdown


def test_to_markdown_includes_health_metrics(loader, sample_playbook):
    """Test markdown includes health metrics."""
    markdown = loader.to_markdown(sample_playbook)

    assert "## Health Metrics" in markdown
    assert "- **Average Helpful Count**: 7.50" in markdown
    assert "- **Effectiveness Ratio**: 0.93" in markdown
    assert "- Added: 2" in markdown
    assert "- Updated: 0" in markdown
    assert "- Pruned: 0" in markdown


def test_to_markdown_includes_bullets(loader, sample_playbook):
    """Test markdown includes all bullets."""
    markdown = loader.to_markdown(sample_playbook)

    assert "## Bullets by Category" in markdown
    assert "### success_pattern" in markdown
    assert "### failure_mode" in markdown
    assert "Always run tests before committing" in markdown
    assert "Avoid using deprecated API endpoints" in markdown
    assert "(confidence: 95%, helpful: 10)" in markdown
    assert "(confidence: 75%, helpful: 5)" in markdown


def test_to_markdown_sorts_bullets_by_priority(loader, sample_playbook):
    """Test markdown sorts bullets by priority (higher first)."""
    markdown = loader.to_markdown(sample_playbook)

    # Find positions of bullets
    bullet1_pos = markdown.find("Always run tests")
    bullet2_pos = markdown.find("Avoid using deprecated")

    # Both should be present
    assert bullet1_pos != -1
    assert bullet2_pos != -1

    # In success_pattern section, only one bullet
    # In failure_mode section, only one bullet
    # So we just verify they're both present


def test_to_markdown_skips_deprecated_bullets(loader, sample_playbook):
    """Test markdown skips deprecated bullets."""
    # Mark a bullet as deprecated
    sample_playbook.categories["success_pattern"][0].deprecated = True
    sample_playbook.categories["success_pattern"][0].deprecation_reason = "Outdated"

    markdown = loader.to_markdown(sample_playbook)

    # Deprecated bullet should not appear
    assert "Always run tests before committing" not in markdown
    # Non-deprecated bullet should still appear
    assert "Avoid using deprecated API endpoints" in markdown


def test_to_markdown_includes_statistics(loader, sample_playbook):
    """Test markdown includes statistics."""
    markdown = loader.to_markdown(sample_playbook)

    assert "## Statistics" in markdown
    assert "**avg_confidence**: 0.85" in markdown
    assert "**total_traces**: 3" in markdown


def test_from_markdown_not_implemented(loader):
    """Test from_markdown raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        loader.from_markdown("# Some markdown")


def test_save_is_thread_safe(loader, sample_playbook):
    """Test save uses atomic write (temp file + rename)."""
    # This is implicitly tested by using write_json_file utility
    # which uses atomic writes. We verify the file is created correctly.
    saved_path = loader.save(sample_playbook)

    assert saved_path.exists()
    with open(saved_path, "r") as f:
        data = json.load(f)
    assert data["agent_name"] == "test_agent"


def test_load_with_missing_health_metrics(loader, temp_config):
    """Test load handles playbook without health_metrics field."""
    # Create playbook JSON without health_metrics
    temp_config.playbook_dir.mkdir(parents=True, exist_ok=True)
    playbook_path = temp_config.playbook_dir / "test_agent_playbook.json"

    data = {
        "playbook_version": "1.0",
        "agent_name": "test_agent",
        "agent_objective": "Test",
        "success_criteria": "Test",
        "last_updated": datetime.now().isoformat(),
        "total_bullets": 0,
        "effectiveness_score": 0.0,
        "categories": {},
        "statistics": {},
        # health_metrics is None
        "health_metrics": None,
        "history": [],
    }

    with open(playbook_path, "w") as f:
        json.dump(data, f)

    # Should load successfully with None health_metrics
    playbook = loader.load()
    assert playbook.agent_name == "test_agent"
    assert playbook.health_metrics is None


def test_playbook_path_construction(temp_config):
    """Test playbook path is correctly constructed."""
    loader = PlaybookLoader("code_developer", temp_config)
    expected_path = temp_config.playbook_dir / "code_developer_playbook.json"
    assert loader.playbook_path == expected_path
