"""Unit tests for StoryMetricsDB - US-015 Estimation Metrics & Velocity Tracking.

Tests cover:
- Database initialization
- Story lifecycle (start, complete)
- Metrics calculation (error, accuracy)
- Velocity tracking
- Accuracy trends
- Category-specific metrics
- Spec vs no-spec comparison
- Suggested estimates
"""

import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.autonomous.story_metrics import StoryMetricsDB


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def metrics_db(temp_db):
    """Create a StoryMetricsDB instance with temporary database."""
    return StoryMetricsDB(db_path=temp_db)


class TestDatabaseInitialization:
    """Test database schema creation and initialization."""

    def test_database_file_created(self, metrics_db, temp_db):
        """Test that database file is created."""
        assert temp_db.exists()
        assert temp_db.stat().st_size > 0

    def test_story_metrics_table_exists(self, metrics_db, temp_db):
        """Test that story_metrics table is created."""
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='story_metrics'
        """
        )

        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "story_metrics"

    def test_velocity_snapshots_table_exists(self, metrics_db, temp_db):
        """Test that velocity_snapshots table is created."""
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='velocity_snapshots'
        """
        )

        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "velocity_snapshots"

    def test_indexes_created(self, metrics_db, temp_db):
        """Test that indexes are created for performance."""
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        """
        )

        indexes = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Check for expected indexes
        assert "idx_story_id" in indexes
        assert "idx_completed_at" in indexes
        assert "idx_category" in indexes
        assert "idx_has_technical_spec" in indexes
        assert "idx_velocity_period_start" in indexes

    def test_wal_mode_enabled(self, metrics_db, temp_db):
        """Test that WAL mode is enabled for multi-process safety."""
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute("PRAGMA journal_mode")
        result = cursor.fetchone()
        conn.close()

        assert result[0].lower() == "wal"


class TestStoryLifecycle:
    """Test story start and completion workflow."""

    def test_start_story_basic(self, metrics_db):
        """Test starting a story with basic information."""
        record_id = metrics_db.start_story(
            story_id="US-001",
            story_title="Test Story",
            estimated_min_days=2.0,
            estimated_max_days=3.0,
        )

        assert record_id > 0

        # Verify record in database
        metrics = metrics_db.get_story_metrics("US-001")
        assert metrics is not None
        assert metrics["story_id"] == "US-001"
        assert metrics["story_title"] == "Test Story"
        assert metrics["estimated_min_days"] == 2.0
        assert metrics["estimated_max_days"] == 3.0
        assert metrics["started_at"] is not None
        assert metrics["completed_at"] is None

    def test_start_story_with_all_fields(self, metrics_db):
        """Test starting a story with all optional fields."""
        record_id = metrics_db.start_story(
            story_id="US-002",
            story_title="Full Story",
            estimated_min_days=3.0,
            estimated_max_days=5.0,
            complexity="high",
            category="feature",
            story_points=8,
            has_technical_spec=True,
            technical_spec_path="docs/US-002_SPEC.md",
        )

        assert record_id > 0

        metrics = metrics_db.get_story_metrics("US-002")
        assert metrics["complexity"] == "high"
        assert metrics["category"] == "feature"
        assert metrics["story_points"] == 8
        assert metrics["has_technical_spec"] == 1
        assert metrics["technical_spec_path"] == "docs/US-002_SPEC.md"

    def test_complete_story_with_actual_days(self, metrics_db):
        """Test completing a story with explicit actual days."""
        metrics_db.start_story(
            story_id="US-003",
            story_title="Completed Story",
            estimated_min_days=2.0,
            estimated_max_days=3.0,
        )

        metrics_db.complete_story(story_id="US-003", actual_days=2.5)

        metrics = metrics_db.get_story_metrics("US-003")
        assert metrics["actual_days"] == 2.5
        assert metrics["completed_at"] is not None
        assert metrics["estimation_error"] is not None
        assert metrics["estimation_accuracy_pct"] is not None

    def test_complete_story_with_spec_phase_metrics(self, metrics_db):
        """Test completing a story with phase-level metrics."""
        metrics_db.start_story(
            story_id="US-004",
            story_title="Story with Phases",
            estimated_min_days=4.0,
            estimated_max_days=5.0,
            has_technical_spec=True,
        )

        phase_metrics = [
            {"phase": "Phase 1", "estimated_hours": 8, "actual_hours": 10},
            {"phase": "Phase 2", "estimated_hours": 6, "actual_hours": 5},
        ]

        metrics_db.complete_story(story_id="US-004", actual_days=4.5, spec_phase_metrics=phase_metrics)

        metrics = metrics_db.get_story_metrics("US-004")
        assert metrics["spec_phase_metrics"] is not None
        assert len(metrics["spec_phase_metrics"]) == 2
        assert metrics["spec_phase_metrics"][0]["phase"] == "Phase 1"


class TestMetricsCalculation:
    """Test accuracy metrics calculation."""

    def test_estimation_error_calculation(self, metrics_db):
        """Test calculation of estimation error."""
        metrics_db.start_story(
            story_id="US-010",
            story_title="Error Test",
            estimated_min_days=2.0,
            estimated_max_days=4.0,  # avg = 3.0
        )

        metrics_db.complete_story(story_id="US-010", actual_days=3.5)

        metrics = metrics_db.get_story_metrics("US-010")

        # Error = actual - avg(estimated) = 3.5 - 3.0 = 0.5
        assert abs(metrics["estimation_error"] - 0.5) < 0.01

    def test_estimation_accuracy_calculation(self, metrics_db):
        """Test calculation of estimation accuracy percentage."""
        metrics_db.start_story(
            story_id="US-011",
            story_title="Accuracy Test",
            estimated_min_days=2.0,
            estimated_max_days=4.0,  # avg = 3.0
        )

        metrics_db.complete_story(story_id="US-011", actual_days=3.3)

        metrics = metrics_db.get_story_metrics("US-011")

        # Error = 3.3 - 3.0 = 0.3
        # Accuracy = 100 - |0.3/3.0 * 100| = 100 - 10 = 90%
        assert abs(metrics["estimation_accuracy_pct"] - 90.0) < 0.1

    def test_perfect_estimation(self, metrics_db):
        """Test metrics when estimation is perfect."""
        metrics_db.start_story(
            story_id="US-012",
            story_title="Perfect",
            estimated_min_days=2.5,
            estimated_max_days=3.5,  # avg = 3.0
        )

        metrics_db.complete_story(story_id="US-012", actual_days=3.0)

        metrics = metrics_db.get_story_metrics("US-012")

        assert abs(metrics["estimation_error"]) < 0.01
        assert metrics["estimation_accuracy_pct"] == 100.0


class TestVelocityTracking:
    """Test velocity calculation and tracking."""

    def test_current_velocity_no_data(self, metrics_db):
        """Test velocity calculation with no completed stories."""
        velocity = metrics_db.get_current_velocity(period_days=7)

        assert velocity["stories_per_week"] == 0
        assert velocity["points_per_week"] == 0
        assert velocity["avg_days_per_story"] == 0
        assert velocity["avg_accuracy_pct"] == 0

    def test_current_velocity_single_story(self, metrics_db):
        """Test velocity with single completed story."""
        metrics_db.start_story(
            story_id="US-020",
            story_title="Single Story",
            estimated_min_days=2.0,
            estimated_max_days=3.0,
            story_points=5,
        )

        metrics_db.complete_story(story_id="US-020", actual_days=2.5)

        velocity = metrics_db.get_current_velocity(period_days=7)

        assert velocity["stories_per_week"] == 1.0
        assert velocity["points_per_week"] == 5.0
        assert velocity["avg_days_per_story"] == 2.5

    def test_current_velocity_multiple_stories(self, metrics_db):
        """Test velocity with multiple stories."""
        # Create 3 stories
        for i in range(3):
            metrics_db.start_story(
                story_id=f"US-02{i}",
                story_title=f"Story {i}",
                estimated_min_days=2.0,
                estimated_max_days=3.0,
                story_points=3,
            )
            metrics_db.complete_story(story_id=f"US-02{i}", actual_days=2.5)

        velocity = metrics_db.get_current_velocity(period_days=7)

        assert velocity["stories_per_week"] == 3.0
        assert velocity["points_per_week"] == 9.0
        assert velocity["avg_days_per_story"] == 2.5

    def test_velocity_snapshot_creation(self, metrics_db):
        """Test creating a velocity snapshot."""
        # Complete some stories
        metrics_db.start_story(
            story_id="US-030",
            story_title="Snapshot Test",
            estimated_min_days=2.0,
            estimated_max_days=3.0,
            story_points=5,
        )
        metrics_db.complete_story(story_id="US-030", actual_days=2.5)

        # Create snapshot
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()

        snapshot_id = metrics_db.create_velocity_snapshot(period_start, period_end)

        assert snapshot_id > 0


class TestAccuracyTrends:
    """Test accuracy trend analysis."""

    def test_accuracy_trends_empty(self, metrics_db):
        """Test accuracy trends with no data."""
        trends = metrics_db.get_accuracy_trends(limit=10)

        assert trends == []

    def test_accuracy_trends_ordering(self, metrics_db):
        """Test that trends are ordered by completion date (most recent first)."""
        # Create stories with different completion times
        for i in range(3):
            metrics_db.start_story(
                story_id=f"US-04{i}",
                story_title=f"Trend {i}",
                estimated_min_days=2.0,
                estimated_max_days=3.0,
            )
            metrics_db.complete_story(story_id=f"US-04{i}", actual_days=2.5)

        trends = metrics_db.get_accuracy_trends(limit=10)

        assert len(trends) == 3
        # Most recent should be first
        assert trends[0]["story_id"] == "US-042"
        assert trends[1]["story_id"] == "US-041"
        assert trends[2]["story_id"] == "US-040"

    def test_accuracy_trends_limit(self, metrics_db):
        """Test that limit parameter works correctly."""
        # Create 5 stories
        for i in range(5):
            metrics_db.start_story(
                story_id=f"US-05{i}",
                story_title=f"Limit Test {i}",
                estimated_min_days=2.0,
                estimated_max_days=3.0,
            )
            metrics_db.complete_story(story_id=f"US-05{i}", actual_days=2.5)

        trends = metrics_db.get_accuracy_trends(limit=3)

        assert len(trends) == 3


class TestCategoryAccuracy:
    """Test category-specific accuracy metrics."""

    def test_category_accuracy_empty(self, metrics_db):
        """Test category accuracy with no data."""
        category_stats = metrics_db.get_category_accuracy()

        assert category_stats == []

    def test_category_accuracy_multiple_categories(self, metrics_db):
        """Test accuracy grouped by category."""
        # Feature stories (more accurate)
        for i in range(2):
            metrics_db.start_story(
                story_id=f"US-F0{i}",
                story_title=f"Feature {i}",
                estimated_min_days=2.0,
                estimated_max_days=3.0,
                category="feature",
            )
            metrics_db.complete_story(story_id=f"US-F0{i}", actual_days=2.5)

        # Bug stories (less accurate)
        for i in range(2):
            metrics_db.start_story(
                story_id=f"US-B0{i}",
                story_title=f"Bug {i}",
                estimated_min_days=1.0,
                estimated_max_days=2.0,
                category="bug",
            )
            metrics_db.complete_story(story_id=f"US-B0{i}", actual_days=2.5)

        category_stats = metrics_db.get_category_accuracy()

        assert len(category_stats) == 2

        # Find feature and bug categories
        feature_stat = next((s for s in category_stats if s["category"] == "feature"), None)
        bug_stat = next((s for s in category_stats if s["category"] == "bug"), None)

        assert feature_stat is not None
        assert bug_stat is not None

        assert feature_stat["story_count"] == 2
        assert bug_stat["story_count"] == 2

        # Feature estimates should be more accurate
        assert feature_stat["avg_accuracy_pct"] > bug_stat["avg_accuracy_pct"]


class TestSpecComparison:
    """Test comparison of stories with vs without technical specs."""

    def test_spec_comparison_no_data(self, metrics_db):
        """Test spec comparison with no data."""
        comparison = metrics_db.get_spec_comparison()

        assert comparison["with_spec"]["count"] == 0
        assert comparison["without_spec"]["count"] == 0

    def test_spec_comparison_with_data(self, metrics_db):
        """Test spec comparison with mixed data."""
        # Stories with specs
        for i in range(2):
            metrics_db.start_story(
                story_id=f"US-W0{i}",
                story_title=f"With Spec {i}",
                estimated_min_days=3.0,
                estimated_max_days=5.0,
                has_technical_spec=True,
            )
            metrics_db.complete_story(story_id=f"US-W0{i}", actual_days=4.0)

        # Stories without specs
        for i in range(3):
            metrics_db.start_story(
                story_id=f"US-N0{i}",
                story_title=f"No Spec {i}",
                estimated_min_days=2.0,
                estimated_max_days=4.0,
                has_technical_spec=False,
            )
            metrics_db.complete_story(story_id=f"US-N0{i}", actual_days=4.0)

        comparison = metrics_db.get_spec_comparison()

        assert comparison["with_spec"]["count"] == 2
        assert comparison["without_spec"]["count"] == 3

        # Stories with specs should be more accurate
        assert comparison["with_spec"]["avg_accuracy_pct"] > comparison["without_spec"]["avg_accuracy_pct"]


class TestSuggestedEstimates:
    """Test suggested estimate generation based on historical data."""

    def test_suggested_estimate_no_data(self, metrics_db):
        """Test suggested estimate with no historical data."""
        suggestion = metrics_db.get_suggested_estimate(
            category="feature", complexity="medium", has_technical_spec=False
        )

        assert suggestion is None

    def test_suggested_estimate_with_data(self, metrics_db):
        """Test suggested estimate with historical data."""
        # Create historical data
        for i in range(5):
            metrics_db.start_story(
                story_id=f"US-S0{i}",
                story_title=f"Historical {i}",
                estimated_min_days=2.0,
                estimated_max_days=3.0,
                category="feature",
                complexity="medium",
                has_technical_spec=False,
            )
            metrics_db.complete_story(story_id=f"US-S0{i}", actual_days=2.5)

        suggestion = metrics_db.get_suggested_estimate(
            category="feature", complexity="medium", has_technical_spec=False
        )

        assert suggestion is not None
        assert suggestion["suggested_min_days"] == pytest.approx(2.0, abs=0.1)
        assert suggestion["suggested_max_days"] == pytest.approx(3.0, abs=0.1)
        assert suggestion["based_on_samples"] == 5
        assert suggestion["historical_avg"] == 2.5

    def test_suggested_estimate_different_complexity(self, metrics_db):
        """Test that complexity affects suggested estimates."""
        # High complexity stories
        for i in range(3):
            metrics_db.start_story(
                story_id=f"US-H0{i}",
                story_title=f"High {i}",
                estimated_min_days=4.0,
                estimated_max_days=6.0,
                category="feature",
                complexity="high",
            )
            metrics_db.complete_story(story_id=f"US-H0{i}", actual_days=5.0)

        # Low complexity stories
        for i in range(3):
            metrics_db.start_story(
                story_id=f"US-L0{i}",
                story_title=f"Low {i}",
                estimated_min_days=1.0,
                estimated_max_days=2.0,
                category="feature",
                complexity="low",
            )
            metrics_db.complete_story(story_id=f"US-L0{i}", actual_days=1.5)

        high_suggestion = metrics_db.get_suggested_estimate(
            category="feature", complexity="high", has_technical_spec=False
        )

        low_suggestion = metrics_db.get_suggested_estimate(
            category="feature", complexity="low", has_technical_spec=False
        )

        assert high_suggestion["suggested_max_days"] > low_suggestion["suggested_max_days"]
