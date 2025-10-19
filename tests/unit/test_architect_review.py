"""Unit tests for architect continuous spec improvement loop (US-049).

Tests cover:
- ReviewTrigger: Daily and weekly review trigger detection
- ArchitectMetrics: Simplification and reuse tracking
- WeeklyReportGenerator: Report generation and content
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from coffee_maker.autonomous.architect_metrics import ArchitectMetrics
from coffee_maker.autonomous.architect_report_generator import WeeklyReportGenerator
from coffee_maker.autonomous.architect_review_triggers import ReviewTrigger


class TestReviewTrigger:
    """Tests for ReviewTrigger class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def temp_roadmap(self, temp_dir):
        """Create temporary ROADMAP.md file."""
        roadmap_dir = temp_dir / "docs" / "roadmap"
        roadmap_dir.mkdir(parents=True)
        roadmap_file = roadmap_dir / "ROADMAP.md"
        roadmap_file.write_text("# ROADMAP\nTest content")
        return roadmap_file

    @pytest.fixture
    def trigger(self, temp_dir):
        """Create ReviewTrigger instance with temp dir."""
        return ReviewTrigger(data_dir=temp_dir)

    def test_daily_review_triggered_on_roadmap_change(self, trigger, temp_roadmap, monkeypatch):
        """Test that daily review triggers when ROADMAP.md is modified."""
        # Change to temp directory so ROADMAP.md is found
        monkeypatch.chdir(temp_roadmap.parent.parent.parent)

        # Mark a review as completed 1 hour ago
        old_time = datetime.now() - timedelta(hours=1)
        reviews = {"daily": old_time.isoformat()}
        trigger._save_reviews(reviews)

        # Modify ROADMAP.md (update mtime to now)
        temp_roadmap.touch()

        # Should trigger because ROADMAP mtime > last review time
        assert trigger.should_run_daily_review() is True

    def test_daily_review_triggered_after_24h(self, trigger):
        """Test that daily review triggers after 24 hours elapsed."""
        # Mark a review as completed 25 hours ago
        old_time = datetime.now() - timedelta(hours=25)
        reviews = {"daily": old_time.isoformat()}
        trigger._save_reviews(reviews)

        # Should trigger because >24 hours elapsed
        assert trigger.should_run_daily_review() is True

    def test_no_trigger_when_roadmap_unchanged(self, trigger, temp_roadmap, monkeypatch):
        """Test that daily review doesn't trigger when ROADMAP unchanged and <24h."""
        # Change to temp directory
        monkeypatch.chdir(temp_roadmap.parent.parent.parent)

        # Mark a review as completed 1 hour ago
        old_time = datetime.now() - timedelta(hours=1)
        reviews = {"daily": old_time.isoformat()}
        trigger._save_reviews(reviews)

        # Touch ROADMAP to set mtime to 2 hours ago (before last review)
        import os

        two_hours_ago = (datetime.now() - timedelta(hours=2)).timestamp()
        os.utime(temp_roadmap, (two_hours_ago, two_hours_ago))

        # Should NOT trigger (ROADMAP unchanged, <24h elapsed)
        assert trigger.should_run_daily_review() is False

    def test_weekly_review_triggered_after_7_days(self, trigger):
        """Test that weekly review triggers after 7 days elapsed."""
        # Mark a review as completed 8 days ago
        old_time = datetime.now() - timedelta(days=8)
        reviews = {"weekly": old_time.isoformat()}
        trigger._save_reviews(reviews)

        # Should trigger because >7 days elapsed
        assert trigger.should_run_weekly_review() is True

    def test_weekly_review_not_triggered_within_7_days(self, trigger):
        """Test that weekly review doesn't trigger within 7 days."""
        # Mark a review as completed 5 days ago
        old_time = datetime.now() - timedelta(days=5)
        reviews = {"weekly": old_time.isoformat()}
        trigger._save_reviews(reviews)

        # Should NOT trigger because <7 days elapsed
        assert trigger.should_run_weekly_review() is False

    def test_first_run_triggers_reviews(self, trigger, temp_roadmap, monkeypatch):
        """Test that first run (no review history) triggers both reviews."""
        # Change to temp directory
        monkeypatch.chdir(temp_roadmap.parent.parent.parent)

        # No review history - should trigger both
        assert trigger.should_run_daily_review() is True
        assert trigger.should_run_weekly_review() is True

    def test_mark_review_completed(self, trigger):
        """Test that marking review completed updates timestamps."""
        # Mark daily review completed
        trigger.mark_review_completed("daily")

        # Should have recorded timestamp
        last_review = trigger._get_last_review_time("daily")
        assert last_review is not None
        assert isinstance(last_review, datetime)

        # Should be very recent (within 1 second)
        time_diff = (datetime.now() - last_review).total_seconds()
        assert time_diff < 1.0

    def test_mark_weekly_review_completed(self, trigger):
        """Test that marking weekly review completed updates timestamps."""
        # Mark weekly review completed
        trigger.mark_review_completed("weekly")

        # Should have recorded timestamp
        last_review = trigger._get_last_review_time("weekly")
        assert last_review is not None
        assert isinstance(last_review, datetime)

        # Should be very recent (within 1 second)
        time_diff = (datetime.now() - last_review).total_seconds()
        assert time_diff < 1.0


class TestArchitectMetrics:
    """Tests for ArchitectMetrics class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def metrics(self, temp_dir):
        """Create ArchitectMetrics instance with temp file."""
        metrics_file = temp_dir / "architect_metrics.json"
        return ArchitectMetrics(metrics_file=metrics_file)

    def test_record_simplification(self, metrics):
        """Test that simplification is recorded correctly."""
        metrics.record_simplification(
            spec_id="SPEC-009",
            original_hours=80.0,
            simplified_hours=16.0,
            description="Reused DeveloperStatus infrastructure",
        )

        # Load metrics and verify
        data = metrics._load_metrics()
        assert "simplifications" in data
        assert len(data["simplifications"]) == 1

        simp = data["simplifications"][0]
        assert simp["spec_id"] == "SPEC-009"
        assert simp["original_hours"] == 80.0
        assert simp["simplified_hours"] == 16.0
        assert simp["effort_saved"] == 64.0
        assert simp["reduction_percent"] == 80.0
        assert simp["description"] == "Reused DeveloperStatus infrastructure"
        assert "date" in simp

    def test_record_reuse(self, metrics):
        """Test that component reuse is recorded correctly."""
        metrics.record_reuse(
            spec_id="SPEC-010",
            reused_components=["NotificationDB", "DeveloperStatus"],
            description="Leveraged existing notification system",
        )

        # Load metrics and verify
        data = metrics._load_metrics()
        assert "reuse" in data
        assert len(data["reuse"]) == 1

        reuse = data["reuse"][0]
        assert reuse["spec_id"] == "SPEC-010"
        assert reuse["components"] == ["NotificationDB", "DeveloperStatus"]
        assert reuse["count"] == 2
        assert reuse["description"] == "Leveraged existing notification system"
        assert "date" in reuse

    def test_get_summary(self, metrics):
        """Test that summary metrics are calculated correctly."""
        # Record some simplifications
        metrics.record_simplification("SPEC-009", 80.0, 16.0, "Test 1")
        metrics.record_simplification("SPEC-010", 24.0, 12.0, "Test 2")

        # Record some reuse
        metrics.record_reuse("SPEC-011", ["CompA", "CompB"], "Test reuse 1")
        metrics.record_reuse("SPEC-012", ["CompC"], "Test reuse 2")

        # Get summary
        summary = metrics.get_summary()

        assert summary["total_simplifications"] == 2
        assert summary["total_effort_saved"] == 76.0  # 64 + 12
        assert summary["avg_reduction_percent"] == 65.0  # (80 + 50) / 2
        assert summary["total_reuse_opportunities"] == 2
        assert summary["specs_reviewed"] == 4  # SPEC-009, 010, 011, 012

    def test_multiple_simplifications(self, temp_dir):
        """Test that multiple simplifications are tracked correctly."""
        # Create fresh metrics instance (don't reuse fixture)
        metrics_file = temp_dir / "test_multiple.json"
        metrics = ArchitectMetrics(metrics_file=metrics_file)

        # Record 3 simplifications
        metrics.record_simplification("SPEC-001", 40.0, 10.0, "Test 1")
        metrics.record_simplification("SPEC-002", 60.0, 20.0, "Test 2")
        metrics.record_simplification("SPEC-003", 100.0, 25.0, "Test 3")

        # Verify all recorded
        data = metrics._load_metrics()
        assert len(data["simplifications"]) == 3

        # Verify summary
        summary = metrics.get_summary()
        assert summary["total_simplifications"] == 3
        assert summary["total_effort_saved"] == 145.0  # 30 + 40 + 75

    def test_empty_metrics(self, metrics):
        """Test that empty metrics file is handled correctly."""
        # Get summary with no data
        summary = metrics.get_summary()

        assert summary["total_simplifications"] == 0
        assert summary["total_effort_saved"] == 0.0
        assert summary["avg_reduction_percent"] == 0.0
        assert summary["total_reuse_opportunities"] == 0
        assert summary["specs_reviewed"] == 0


class TestWeeklyReportGenerator:
    """Tests for WeeklyReportGenerator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def metrics(self, temp_dir):
        """Create ArchitectMetrics instance with test data."""
        metrics_file = temp_dir / "architect_metrics.json"
        metrics = ArchitectMetrics(metrics_file=metrics_file)

        # Add some test data
        metrics.record_simplification("SPEC-009", 80.0, 16.0, "Reused infrastructure")
        metrics.record_reuse("SPEC-010", ["NotificationDB"], "Leveraged notifications")

        return metrics

    @pytest.fixture
    def generator(self, metrics, temp_dir):
        """Create WeeklyReportGenerator instance."""
        output_dir = temp_dir / "reports"
        return WeeklyReportGenerator(metrics=metrics, output_dir=output_dir)

    def test_generate_report(self, generator, temp_dir):
        """Test that report file is created."""
        findings = {
            "specs_reviewed": ["SPEC-009", "SPEC-010"],
            "simplifications_made": [
                {
                    "spec_id": "SPEC-009",
                    "title": "Test Spec",
                    "reduction_percent": 80.0,
                    "original_hours": 80.0,
                    "simplified_hours": 16.0,
                    "effort_saved": 64.0,
                    "description": "Test simplification",
                }
            ],
            "reuse_opportunities": [{"spec_id": "SPEC-010", "components": ["NotificationDB"]}],
            "recommendations": ["Recommendation 1", "Recommendation 2"],
        }

        report_path = generator.generate_report(findings)

        # Verify file created
        assert report_path.exists()
        assert report_path.suffix == ".md"
        assert "WEEKLY_SPEC_REVIEW" in report_path.name

    def test_report_content_structure(self, generator):
        """Test that report has valid markdown structure."""
        findings = {
            "specs_reviewed": ["SPEC-009"],
            "simplifications_made": [],
            "reuse_opportunities": [],
            "recommendations": [],
        }

        report_path = generator.generate_report(findings)
        content = report_path.read_text()

        # Check for required sections
        assert "# Weekly Spec Review" in content
        assert "## Summary" in content
        assert "## Metrics" in content
        assert "## Next Week Focus" in content
        assert "**Generated by**: architect agent" in content

    def test_report_includes_metrics(self, generator):
        """Test that report includes metrics from ArchitectMetrics."""
        findings = {
            "specs_reviewed": ["SPEC-009", "SPEC-010"],
            "simplifications_made": [
                {
                    "spec_id": "SPEC-009",
                    "title": "Test Spec",
                    "reduction_percent": 80.0,
                    "original_hours": 80.0,
                    "simplified_hours": 16.0,
                    "effort_saved": 64.0,
                    "description": "Test",
                }
            ],
            "reuse_opportunities": [],
            "recommendations": [],
        }

        report_path = generator.generate_report(findings)
        content = report_path.read_text()

        # Check for metrics
        assert "80.0%" in content  # Simplification rate
        assert "64.0 hours" in content  # Effort saved

    def test_report_recommendations(self, generator):
        """Test that recommendations section is populated correctly."""
        findings = {
            "specs_reviewed": ["SPEC-009"],
            "simplifications_made": [],
            "reuse_opportunities": [],
            "recommendations": [
                "Create shared utility module",
                "Extract validation logic",
                "Add shared testing utilities",
            ],
        }

        report_path = generator.generate_report(findings)
        content = report_path.read_text()

        # Check for recommendations section
        assert "## Recommendations" in content
        assert "1. Create shared utility module" in content
        assert "2. Extract validation logic" in content
        assert "3. Add shared testing utilities" in content
