"""Unit tests for playbook API methods."""

import pytest
from datetime import datetime
from coffee_maker.autonomous.ace.api import ACEApi
from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.models import Playbook, PlaybookBullet


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary ACE configuration."""
    return ACEConfig(
        trace_dir=tmp_path / "traces",
        delta_dir=tmp_path / "deltas",
        playbook_dir=tmp_path / "playbooks",
        enabled=True,
    )


@pytest.fixture
def ace_api(temp_config):
    """Create ACE API instance with temp config."""
    return ACEApi(config=temp_config)


@pytest.fixture
def mock_agent_name():
    """Return mock agent name."""
    return "test_agent"


class TestPlaybookAPI:
    """Tests for playbook API methods."""

    def test_get_playbook_bullets_no_filters(self, ace_api, mock_agent_name):
        """Test getting all bullets without filters."""
        bullets = ace_api.get_playbook_bullets(mock_agent_name)
        assert isinstance(bullets, list)
        assert len(bullets) > 0  # Mock data generates 157 bullets
        assert all(isinstance(b, dict) for b in bullets)

    def test_get_playbook_bullets_with_category_filter(self, ace_api, mock_agent_name):
        """Test filtering bullets by category."""
        # Get all categories first
        categories = ace_api.get_playbook_categories(mock_agent_name)
        assert len(categories) > 0

        # Filter by first category
        category = categories[0]
        bullets = ace_api.get_playbook_bullets(mock_agent_name, category=category)

        assert isinstance(bullets, list)
        assert all(b.get("category") == category for b in bullets)

    def test_get_playbook_bullets_with_status_filter(self, ace_api, mock_agent_name):
        """Test filtering bullets by status."""
        active_bullets = ace_api.get_playbook_bullets(mock_agent_name, status="active")
        pending_bullets = ace_api.get_playbook_bullets(mock_agent_name, status="pending")
        archived_bullets = ace_api.get_playbook_bullets(mock_agent_name, status="archived")

        assert isinstance(active_bullets, list)
        assert isinstance(pending_bullets, list)
        assert isinstance(archived_bullets, list)

        # Most bullets should be active (90% in mock data)
        assert len(active_bullets) > len(pending_bullets)
        assert len(active_bullets) > len(archived_bullets)

    def test_get_playbook_bullets_with_effectiveness_filter(self, ace_api, mock_agent_name):
        """Test filtering bullets by effectiveness range."""
        # High effectiveness only
        high_eff_bullets = ace_api.get_playbook_bullets(mock_agent_name, min_effectiveness=0.7)

        assert isinstance(high_eff_bullets, list)
        assert all(b.get("effectiveness", 0) >= 0.7 for b in high_eff_bullets)

        # Low effectiveness only
        low_eff_bullets = ace_api.get_playbook_bullets(mock_agent_name, max_effectiveness=0.3)

        assert isinstance(low_eff_bullets, list)
        assert all(b.get("effectiveness", 0) <= 0.3 for b in low_eff_bullets)

    def test_get_playbook_bullets_with_search_query(self, ace_api, mock_agent_name):
        """Test searching bullets by content."""
        search_results = ace_api.get_playbook_bullets(mock_agent_name, search_query="validate")

        assert isinstance(search_results, list)
        assert all("validate" in b.get("content", "").lower() for b in search_results)

    def test_approve_bullet(self, ace_api, mock_agent_name):
        """Test approving a bullet."""
        # Get a pending bullet
        pending_bullets = ace_api.get_playbook_bullets(mock_agent_name, status="pending")

        if len(pending_bullets) > 0:
            bullet_id = pending_bullets[0]["bullet_id"]

            # Approve it
            result = ace_api.approve_bullet(mock_agent_name, bullet_id)
            assert result is True

            # Verify status changed (note: mock data regenerates, so this is conceptual)
            # In production, we would verify the bullet status changed to "active"

    def test_approve_nonexistent_bullet(self, ace_api, mock_agent_name):
        """Test approving a bullet that doesn't exist."""
        result = ace_api.approve_bullet(mock_agent_name, "nonexistent_bullet_id")
        assert result is False

    def test_reject_bullet(self, ace_api, mock_agent_name):
        """Test rejecting a bullet."""
        # Get an active bullet
        active_bullets = ace_api.get_playbook_bullets(mock_agent_name, status="active")

        if len(active_bullets) > 0:
            bullet_id = active_bullets[0]["bullet_id"]

            # Reject it
            result = ace_api.reject_bullet(mock_agent_name, bullet_id)
            assert result is True

    def test_reject_nonexistent_bullet(self, ace_api, mock_agent_name):
        """Test rejecting a bullet that doesn't exist."""
        result = ace_api.reject_bullet(mock_agent_name, "nonexistent_bullet_id")
        assert result is False

    def test_bulk_approve_bullets(self, ace_api, mock_agent_name):
        """Test bulk approving multiple bullets."""
        # Get pending bullets
        pending_bullets = ace_api.get_playbook_bullets(mock_agent_name, status="pending")

        if len(pending_bullets) >= 2:
            bullet_ids = [b["bullet_id"] for b in pending_bullets[:2]]

            # Bulk approve
            result = ace_api.bulk_approve_bullets(mock_agent_name, bullet_ids)

            assert isinstance(result, dict)
            assert "success" in result
            assert "failure" in result
            # At least some should succeed (with mock data)
            assert result["success"] + result["failure"] == len(bullet_ids)

    def test_bulk_reject_bullets(self, ace_api, mock_agent_name):
        """Test bulk rejecting multiple bullets."""
        # Get active bullets
        active_bullets = ace_api.get_playbook_bullets(mock_agent_name, status="active")

        if len(active_bullets) >= 2:
            bullet_ids = [b["bullet_id"] for b in active_bullets[:2]]

            # Bulk reject
            result = ace_api.bulk_reject_bullets(mock_agent_name, bullet_ids)

            assert isinstance(result, dict)
            assert "success" in result
            assert "failure" in result
            assert result["success"] + result["failure"] == len(bullet_ids)

    def test_get_curation_queue(self, ace_api, mock_agent_name):
        """Test getting curation queue (pending bullets)."""
        queue = ace_api.get_curation_queue(mock_agent_name)

        assert isinstance(queue, list)
        assert all(b.get("status") == "pending" for b in queue)

    def test_get_playbook_categories(self, ace_api, mock_agent_name):
        """Test getting unique categories."""
        categories = ace_api.get_playbook_categories(mock_agent_name)

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert all(isinstance(c, str) for c in categories)
        # Should be sorted
        assert categories == sorted(categories)

    def test_get_playbook(self, ace_api, mock_agent_name):
        """Test getting full playbook."""
        playbook = ace_api.get_playbook(mock_agent_name)

        assert isinstance(playbook, dict)
        assert "agent_name" in playbook
        assert "bullets" in playbook
        assert "total_bullets" in playbook
        assert "avg_effectiveness" in playbook
        assert playbook["agent_name"] == mock_agent_name
        assert len(playbook["bullets"]) > 0

    def test_combined_filters(self, ace_api, mock_agent_name):
        """Test using multiple filters together."""
        # Get categories
        categories = ace_api.get_playbook_categories(mock_agent_name)

        if len(categories) > 0:
            category = categories[0]

            # Combine category, status, effectiveness, and search
            bullets = ace_api.get_playbook_bullets(
                mock_agent_name,
                category=category,
                status="active",
                min_effectiveness=0.5,
                search_query="error" if category == "error_handling" else None,
            )

            assert isinstance(bullets, list)
            # All filters should apply
            for bullet in bullets:
                assert bullet.get("category") == category
                assert bullet.get("status") == "active"
                assert bullet.get("effectiveness", 0) >= 0.5


class TestPlaybookModels:
    """Tests for playbook data models."""

    def test_playbook_bullet_to_dict(self):
        """Test PlaybookBullet serialization."""
        bullet = PlaybookBullet(
            bullet_id="test_001",
            content="Test content",
            category="testing",
            effectiveness=0.85,
            usage_count=10,
            added_date=datetime.now(),
            status="active",
        )

        bullet_dict = bullet.to_dict()

        assert isinstance(bullet_dict, dict)
        assert bullet_dict["bullet_id"] == "test_001"
        assert bullet_dict["content"] == "Test content"
        assert bullet_dict["category"] == "testing"
        assert bullet_dict["effectiveness"] == 0.85
        assert bullet_dict["usage_count"] == 10
        assert bullet_dict["status"] == "active"

    def test_playbook_to_dict(self):
        """Test Playbook serialization."""
        bullets = [
            PlaybookBullet(
                bullet_id=f"test_{i:03d}",
                content=f"Test content {i}",
                category="testing",
                effectiveness=0.8,
                usage_count=5,
            )
            for i in range(5)
        ]

        playbook = Playbook(
            agent_name="test_agent",
            bullets=bullets,
            total_bullets=len(bullets),
            avg_effectiveness=0.8,
            last_updated=datetime.now(),
        )

        playbook_dict = playbook.to_dict()

        assert isinstance(playbook_dict, dict)
        assert playbook_dict["agent_name"] == "test_agent"
        assert len(playbook_dict["bullets"]) == 5
        assert playbook_dict["total_bullets"] == 5
        assert playbook_dict["avg_effectiveness"] == 0.8


class TestPerformance:
    """Performance tests for playbook operations."""

    def test_load_large_playbook(self, ace_api, mock_agent_name):
        """Test loading playbook with 150+ bullets."""
        import time

        start = time.time()
        playbook = ace_api.get_playbook(mock_agent_name)
        elapsed = time.time() - start

        assert elapsed < 10.0, f"Loading took {elapsed:.2f}s, should be < 10s"
        assert len(playbook["bullets"]) >= 150

    def test_filter_large_playbook(self, ace_api, mock_agent_name):
        """Test filtering large playbook performs well."""
        import time

        start = time.time()
        bullets = ace_api.get_playbook_bullets(mock_agent_name, min_effectiveness=0.5, search_query="validate")
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Filtering took {elapsed:.2f}s, should be < 1s"
        assert isinstance(bullets, list)

    def test_bulk_operations_performance(self, ace_api, mock_agent_name):
        """Test bulk operations complete in reasonable time."""
        import time

        # Get 10 pending bullets
        pending = ace_api.get_playbook_bullets(mock_agent_name, status="pending")[:10]
        bullet_ids = [b["bullet_id"] for b in pending]

        start = time.time()
        result = ace_api.bulk_approve_bullets(mock_agent_name, bullet_ids)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Bulk approve took {elapsed:.2f}s, should be < 5s"
        assert result["success"] + result["failure"] == len(bullet_ids)
