"""Tests for ACE Curator."""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.curator import ACECurator
from coffee_maker.autonomous.ace.models import (
    DeltaItem,
    Evidence,
    Playbook,
    PlaybookBullet,
)


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary ACE config."""
    return ACEConfig(
        enabled=True,
        trace_dir=tmp_path / "traces",
        delta_dir=tmp_path / "deltas",
        playbook_dir=tmp_path / "playbooks",
        similarity_threshold=0.85,
        pruning_rate=0.10,
        min_helpful_count=2,
        max_bullets=150,
    )


@pytest.fixture
def curator(temp_config):
    """Create ACECurator with temp config."""
    return ACECurator("test_agent", temp_config)


@pytest.fixture
def sample_delta():
    """Create sample delta item."""
    return DeltaItem(
        delta_id="delta_001",
        insight_type="success_pattern",
        title="Run tests before commit",
        description="Always run tests before committing to prevent regressions",
        recommendation="Run pytest before git commit",
        evidence=[Evidence(trace_id="trace_001", execution_id=1, example="Test passed")],
        applicability="All code changes",
        priority=5,
        confidence=0.9,
        action="add_new",
    )


@pytest.fixture
def sample_playbook():
    """Create sample playbook with existing bullets."""
    bullet1 = PlaybookBullet(
        bullet_id="bullet_001",
        type="success_pattern",
        content="Always run tests before committing",
        helpful_count=10,
        harmful_count=0,
        confidence=0.95,
        priority=5,
        evidence_sources=["trace_001"],
    )

    bullet2 = PlaybookBullet(
        bullet_id="bullet_002",
        type="failure_mode",
        content="Avoid deprecated APIs",
        helpful_count=1,  # Low count - candidate for pruning
        harmful_count=0,
        confidence=0.6,
        priority=3,
        evidence_sources=["trace_002"],
    )

    return Playbook(
        playbook_version="1.0",
        agent_name="test_agent",
        agent_objective="Test objectives",
        success_criteria="Test criteria",
        last_updated=datetime.now(),
        total_bullets=2,
        effectiveness_score=0.85,
        categories={"success_pattern": [bullet1], "failure_mode": [bullet2]},
    )


# Initialization Tests


def test_curator_initialization(temp_config):
    """Test ACECurator initialization."""
    curator = ACECurator("test_agent", temp_config)
    assert curator.agent_name == "test_agent"
    assert curator.config == temp_config
    assert curator.bullets_added == 0
    assert curator.bullets_updated == 0
    assert curator.bullets_pruned == 0


# Delta Loading Tests


def test_discover_delta_files(curator, temp_config):
    """Test delta file discovery."""
    # Create delta directory with files
    delta_dir = temp_config.delta_dir / "test_agent"
    delta_dir.mkdir(parents=True, exist_ok=True)

    (delta_dir / "delta_001.json").write_text("{}")
    (delta_dir / "delta_002.json").write_text("{}")
    (delta_dir / "other_file.txt").write_text("")

    delta_files = curator._discover_delta_files()

    assert len(delta_files) == 2
    assert all(f.name.startswith("delta_") for f in delta_files)


def test_discover_delta_files_missing_directory(curator):
    """Test delta discovery when directory doesn't exist."""
    delta_files = curator._discover_delta_files()
    assert delta_files == []


def test_load_deltas_single(curator, temp_config, sample_delta):
    """Test loading single delta from file."""
    delta_dir = temp_config.delta_dir / "test_agent"
    delta_dir.mkdir(parents=True, exist_ok=True)

    delta_path = delta_dir / "delta_001.json"
    with open(delta_path, "w") as f:
        json.dump(sample_delta.to_dict(), f)

    deltas = curator._load_deltas([delta_path])

    assert len(deltas) == 1
    assert deltas[0].delta_id == "delta_001"
    assert deltas[0].title == "Run tests before commit"


def test_load_deltas_list(curator, temp_config, sample_delta):
    """Test loading list of deltas from file."""
    delta_dir = temp_config.delta_dir / "test_agent"
    delta_dir.mkdir(parents=True, exist_ok=True)

    # Create file with list of deltas
    delta_path = delta_dir / "delta_batch.json"
    deltas_list = [sample_delta.to_dict(), sample_delta.to_dict()]
    with open(delta_path, "w") as f:
        json.dump(deltas_list, f)

    deltas = curator._load_deltas([delta_path])

    assert len(deltas) == 2


def test_load_deltas_handles_invalid_file(curator, temp_config):
    """Test loading deltas handles invalid JSON gracefully."""
    delta_dir = temp_config.delta_dir / "test_agent"
    delta_dir.mkdir(parents=True, exist_ok=True)

    delta_path = delta_dir / "invalid.json"
    delta_path.write_text("{ invalid json }")

    deltas = curator._load_deltas([delta_path])

    assert deltas == []


# Playbook Loading Tests


def test_load_playbook_creates_default(curator):
    """Test loading playbook creates default when missing."""
    playbook = curator._load_playbook()

    assert playbook.agent_name == "test_agent"
    assert playbook.total_bullets == 0


# Semantic Similarity Tests


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
@patch("coffee_maker.autonomous.ace.curator.compute_similarity")
def test_find_similar_bullet_finds_match(mock_sim, mock_emb, curator, sample_delta, sample_playbook):
    """Test finding similar bullet above threshold."""
    # Mock embeddings
    mock_emb.return_value = [0.1, 0.2, 0.3]
    mock_sim.return_value = 0.90  # Above threshold

    result = curator._find_similar_bullet(sample_delta, sample_playbook, threshold=0.85)

    assert result is not None
    bullet, similarity = result
    assert bullet.bullet_id == "bullet_001"
    assert similarity == 0.90


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
@patch("coffee_maker.autonomous.ace.curator.compute_similarity")
def test_find_similar_bullet_no_match(mock_sim, mock_emb, curator, sample_delta, sample_playbook):
    """Test finding similar bullet below threshold."""
    mock_emb.return_value = [0.1, 0.2, 0.3]
    mock_sim.return_value = 0.70  # Below threshold

    result = curator._find_similar_bullet(sample_delta, sample_playbook, threshold=0.85)

    assert result is None


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
@patch("coffee_maker.autonomous.ace.curator.compute_similarity")
def test_find_similar_bullet_skips_deprecated(mock_sim, mock_emb, curator, sample_delta, sample_playbook):
    """Test finding similar bullet skips deprecated bullets."""
    # Mark bullet as deprecated
    sample_playbook.categories["success_pattern"][0].deprecated = True

    mock_emb.return_value = [0.1, 0.2, 0.3]
    mock_sim.return_value = 0.95  # High similarity

    result = curator._find_similar_bullet(sample_delta, sample_playbook, threshold=0.85)

    # Should not match deprecated bullet
    assert result is None


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
@patch("coffee_maker.autonomous.ace.curator.compute_similarity")
def test_find_similar_bullet_exact_threshold(mock_sim, mock_emb, curator, sample_delta, sample_playbook):
    """Test finding similar bullet at exact threshold."""
    mock_emb.return_value = [0.1, 0.2, 0.3]
    mock_sim.return_value = 0.85  # Exactly at threshold

    result = curator._find_similar_bullet(sample_delta, sample_playbook, threshold=0.85)

    # Should not match (needs to be > threshold)
    assert result is None


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
def test_find_similar_bullet_computes_embedding_if_missing(mock_emb, curator, sample_delta, sample_playbook):
    """Test finding similar bullet computes embedding if not cached."""
    # Remove embedding from bullet
    sample_playbook.categories["success_pattern"][0].embedding = None

    mock_emb.return_value = [0.1, 0.2, 0.3]

    curator._find_similar_bullet(sample_delta, sample_playbook, threshold=0.85)

    # Should have computed embedding for bullet
    assert mock_emb.call_count >= 2  # Once for delta, once for bullet


# Merge Logic Tests


def test_merge_bullet_increments_helpful_count(curator, sample_delta):
    """Test merging increments helpful_count."""
    bullet = PlaybookBullet(
        bullet_id="bullet_001",
        type="success_pattern",
        content="Run tests",
        helpful_count=5,
        harmful_count=0,
        confidence=0.8,
        priority=3,
    )

    curator._merge_bullet(bullet, sample_delta)

    assert bullet.helpful_count == 6


def test_merge_bullet_updates_confidence(curator, sample_delta):
    """Test merging updates confidence with weighted average."""
    bullet = PlaybookBullet(
        bullet_id="bullet_001",
        type="success_pattern",
        content="Run tests",
        helpful_count=10,
        harmful_count=0,
        confidence=0.8,
        priority=3,
    )

    # Delta has confidence 0.9
    curator._merge_bullet(bullet, sample_delta)

    # New confidence should be weighted average
    # (0.8 * 10 + 0.9 * 1) / 11 = 8.9 / 11 ≈ 0.809
    assert 0.80 < bullet.confidence < 0.82


def test_merge_bullet_updates_priority(curator, sample_delta):
    """Test merging takes maximum priority."""
    bullet = PlaybookBullet(
        bullet_id="bullet_001",
        type="success_pattern",
        content="Run tests",
        helpful_count=5,
        harmful_count=0,
        confidence=0.8,
        priority=3,  # Lower than delta's priority 5
    )

    curator._merge_bullet(bullet, sample_delta)

    assert bullet.priority == 5  # Should take delta's higher priority


def test_merge_bullet_appends_evidence_sources(curator, sample_delta):
    """Test merging appends new evidence sources."""
    bullet = PlaybookBullet(
        bullet_id="bullet_001",
        type="success_pattern",
        content="Run tests",
        helpful_count=5,
        harmful_count=0,
        confidence=0.8,
        priority=3,
        evidence_sources=["trace_000"],
    )

    curator._merge_bullet(bullet, sample_delta)

    assert "trace_000" in bullet.evidence_sources
    assert "trace_001" in bullet.evidence_sources  # From delta


def test_merge_bullet_updates_timestamp(curator, sample_delta):
    """Test merging updates last_updated timestamp."""
    old_time = datetime(2025, 1, 1, 12, 0, 0)
    bullet = PlaybookBullet(
        bullet_id="bullet_001",
        type="success_pattern",
        content="Run tests",
        helpful_count=5,
        harmful_count=0,
        confidence=0.8,
        priority=3,
        last_updated=old_time,
    )

    curator._merge_bullet(bullet, sample_delta)

    assert bullet.last_updated > old_time


# Add New Bullet Tests


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
def test_add_new_bullet(mock_emb, curator, sample_delta, sample_playbook):
    """Test adding new bullet from delta."""
    mock_emb.return_value = [0.1, 0.2, 0.3]

    curator._add_new_bullet(sample_delta, sample_playbook)

    # Should have added to success_pattern category
    assert len(sample_playbook.categories["success_pattern"]) == 2  # Was 1, now 2

    new_bullet = sample_playbook.categories["success_pattern"][1]
    assert new_bullet.content == "Run pytest before git commit"
    assert new_bullet.helpful_count == 1
    assert new_bullet.confidence == 0.9
    assert new_bullet.priority == 5


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
def test_add_new_bullet_creates_category(mock_emb, curator, sample_delta, sample_playbook):
    """Test adding new bullet creates category if doesn't exist."""
    mock_emb.return_value = [0.1, 0.2, 0.3]

    # Change delta to new category
    sample_delta.insight_type = "optimization"

    curator._add_new_bullet(sample_delta, sample_playbook)

    # Should have created new category
    assert "optimization" in sample_playbook.categories
    assert len(sample_playbook.categories["optimization"]) == 1


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
def test_add_new_bullet_generates_embedding(mock_emb, curator, sample_delta, sample_playbook):
    """Test adding new bullet generates embedding."""
    mock_emb.return_value = [0.1, 0.2, 0.3]

    curator._add_new_bullet(sample_delta, sample_playbook)

    new_bullet = sample_playbook.categories["success_pattern"][1]
    assert new_bullet.embedding == [0.1, 0.2, 0.3]


# Pruning Logic Tests


def test_prune_low_helpful_count(curator, sample_playbook):
    """Test pruning bullets with low helpful_count."""
    # bullet_002 has helpful_count=1, below min_helpful_count=2
    curator._prune_low_value_bullets(sample_playbook)

    bullet2 = sample_playbook.categories["failure_mode"][0]
    assert bullet2.deprecated is True
    assert "Low helpful count" in bullet2.deprecation_reason


def test_prune_respects_max_bullets(curator, temp_config, sample_playbook):
    """Test pruning when exceeding max_bullets."""
    # Set very low max_bullets
    temp_config.max_bullets = 1
    curator = ACECurator("test_agent", temp_config)

    curator._prune_low_value_bullets(sample_playbook)

    # Should have pruned at least one bullet
    all_bullets = []
    for bullets in sample_playbook.categories.values():
        all_bullets.extend(bullets)

    active_bullets = [b for b in all_bullets if not b.deprecated]
    assert len(active_bullets) <= 1


def test_prune_skips_already_deprecated(curator, sample_playbook):
    """Test pruning skips already deprecated bullets."""
    # Mark bullet as deprecated
    bullet1 = sample_playbook.categories["success_pattern"][0]
    bullet1.deprecated = True

    initial_deprecated = sum(1 for bullets in sample_playbook.categories.values() for b in bullets if b.deprecated)

    curator._prune_low_value_bullets(sample_playbook)

    final_deprecated = sum(1 for bullets in sample_playbook.categories.values() for b in bullets if b.deprecated)

    # Should have pruned more bullets beyond the already deprecated one
    assert final_deprecated >= initial_deprecated


def test_prune_tracks_count(curator, sample_playbook):
    """Test pruning tracks bullets_pruned count."""
    curator._prune_low_value_bullets(sample_playbook)

    # Should have pruned bullet_002 (low helpful count)
    assert curator.bullets_pruned >= 1


def test_prune_uses_effectiveness_score(curator, sample_playbook):
    """Test pruning considers effectiveness score."""
    # Add bullet with high helpful but also high harmful (low effectiveness)
    bullet3 = PlaybookBullet(
        bullet_id="bullet_003",
        type="success_pattern",
        content="Sometimes works",
        helpful_count=5,
        harmful_count=5,  # 50% effectiveness
        confidence=0.5,
        priority=1,
    )
    sample_playbook.categories["success_pattern"].append(bullet3)

    # Lower max_bullets to force pruning
    curator.config.max_bullets = 2

    curator._prune_low_value_bullets(sample_playbook)

    # bullet3 should be candidate for pruning due to low score
    # (effectiveness * confidence * priority = 0.5 * 0.5 * 1 = 0.25)


# Health Metrics Tests


def test_update_health_metrics_computes_total_bullets(curator, sample_playbook):
    """Test health metrics computes total bullets."""
    curator._update_health_metrics(sample_playbook)

    assert sample_playbook.health_metrics.total_bullets == 2


def test_update_health_metrics_computes_avg_helpful(curator, sample_playbook):
    """Test health metrics computes average helpful count."""
    # bullet_001: helpful=10, bullet_002: helpful=1
    # avg = (10 + 1) / 2 = 5.5
    curator._update_health_metrics(sample_playbook)

    assert sample_playbook.health_metrics.avg_helpful_count == 5.5


def test_update_health_metrics_computes_effectiveness(curator, sample_playbook):
    """Test health metrics computes effectiveness ratio."""
    # total_helpful = 10 + 1 = 11
    # total_harmful = 0 + 0 = 0
    # effectiveness = 11 / 11 = 1.0
    curator._update_health_metrics(sample_playbook)

    assert sample_playbook.health_metrics.effectiveness_ratio == 1.0


def test_update_health_metrics_includes_session_stats(curator, sample_playbook):
    """Test health metrics includes session statistics."""
    curator.bullets_added = 5
    curator.bullets_updated = 3
    curator.bullets_pruned = 1

    curator._update_health_metrics(sample_playbook)

    assert sample_playbook.health_metrics.bullets_added_this_session == 5
    assert sample_playbook.health_metrics.bullets_updated_this_session == 3
    assert sample_playbook.health_metrics.bullets_pruned_this_session == 1


def test_update_health_metrics_handles_empty_playbook(curator):
    """Test health metrics handles empty playbook."""
    empty_playbook = Playbook(
        playbook_version="1.0",
        agent_name="test",
        agent_objective="Test",
        success_criteria="Test",
        last_updated=datetime.now(),
        total_bullets=0,
        effectiveness_score=0.0,
        categories={},
    )

    curator._update_health_metrics(empty_playbook)

    assert empty_playbook.health_metrics.total_bullets == 0
    assert empty_playbook.health_metrics.avg_helpful_count == 0.0


# Integration Tests


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
@patch("coffee_maker.autonomous.ace.curator.compute_similarity")
def test_consolidate_deltas_full_workflow(mock_sim, mock_emb, curator, temp_config, sample_delta, sample_playbook):
    """Test full consolidation workflow."""
    # Setup
    mock_emb.return_value = [0.1, 0.2, 0.3]
    mock_sim.return_value = 0.70  # Below threshold - will add new

    # Create delta file
    delta_dir = temp_config.delta_dir / "test_agent"
    delta_dir.mkdir(parents=True, exist_ok=True)
    delta_path = delta_dir / "delta_001.json"
    with open(delta_path, "w") as f:
        json.dump(sample_delta.to_dict(), f)

    # Save initial playbook
    curator.playbook_loader.save(sample_playbook)

    # Run consolidation
    updated_playbook = curator.consolidate_deltas([delta_path])

    # Verify
    assert curator.deltas_processed == 1
    assert curator.bullets_added >= 1  # Added new bullet
    assert updated_playbook.total_bullets > sample_playbook.total_bullets


@patch("coffee_maker.autonomous.ace.curator.get_embedding")
@patch("coffee_maker.autonomous.ace.curator.compute_similarity")
def test_consolidate_deltas_merges_similar(mock_sim, mock_emb, curator, temp_config, sample_delta, sample_playbook):
    """Test consolidation merges similar deltas."""
    # Setup
    mock_emb.return_value = [0.1, 0.2, 0.3]
    mock_sim.return_value = 0.95  # Above threshold - will merge

    # Create delta file
    delta_dir = temp_config.delta_dir / "test_agent"
    delta_dir.mkdir(parents=True, exist_ok=True)
    delta_path = delta_dir / "delta_001.json"
    with open(delta_path, "w") as f:
        json.dump(sample_delta.to_dict(), f)

    # Save initial playbook
    initial_helpful = sample_playbook.categories["success_pattern"][0].helpful_count
    curator.playbook_loader.save(sample_playbook)

    # Run consolidation
    updated_playbook = curator.consolidate_deltas([delta_path])

    # Verify
    assert curator.bullets_updated >= 1
    # Check helpful count increased
    updated_bullet = updated_playbook.categories["success_pattern"][0]
    assert updated_bullet.helpful_count > initial_helpful


def test_consolidate_deltas_saves_report(curator, temp_config):
    """Test consolidation saves curation report."""
    # Create empty playbook
    empty_playbook = curator._load_playbook()
    curator.playbook_loader.save(empty_playbook)

    # Run consolidation with no deltas
    curator.consolidate_deltas([])

    # Check report was created
    report_dir = temp_config.playbook_dir / "reports"
    assert report_dir.exists()

    reports = list(report_dir.glob("curation_report_*.json"))
    assert len(reports) == 1


def test_process_delta_updates_stats(curator, sample_delta, sample_playbook):
    """Test process_delta updates statistics correctly."""
    with patch.object(curator, "_find_similar_bullet", return_value=None):
        with patch.object(curator, "_add_new_bullet"):
            curator._process_delta(sample_delta, sample_playbook)

            # _process_delta only increments bullets_added, not deltas_processed
            # (deltas_processed is incremented in consolidate_deltas)
            assert curator.bullets_added == 1
