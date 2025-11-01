"""Tests for Trend Tracker."""

from datetime import datetime
from pathlib import Path


from claude.skills.refactoring_analysis.proactive_refactoring_analysis import (
    TrendTracker,
)


class TestTrendTracker:
    """Test trend tracking functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path("/tmp/test_refactoring_analysis")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.tracker = TrendTracker(self.test_dir)

    def teardown_method(self):
        """Clean up test files."""
        if self.tracker.trends_file.exists():
            self.tracker.trends_file.unlink()

    def test_record_metrics_creates_file(self):
        """Test recording metrics creates trends file."""
        metrics = {
            "health_score": 85,
            "coverage": 78.5,
            "complexity": 4.2,
        }

        self.tracker.record_metrics(metrics)

        assert self.tracker.trends_file.exists()

    def test_record_metrics_appends_data(self):
        """Test recording metrics appends to existing data."""
        metrics1 = {"health_score": 85, "coverage": 78.5}
        metrics2 = {"health_score": 90, "coverage": 82.0}

        self.tracker.record_metrics(metrics1)
        self.tracker.record_metrics(metrics2)

        trends = self.tracker._load_trends()
        assert len(trends) == 2
        assert trends[0]["metrics"]["health_score"] == 85
        assert trends[1]["metrics"]["health_score"] == 90

    def test_record_metrics_keeps_last_12_weeks(self):
        """Test trend history limited to 12 weeks."""
        # Record 15 weeks of data
        for i in range(15):
            metrics = {"health_score": 70 + i}
            self.tracker.record_metrics(metrics)

        trends = self.tracker._load_trends()

        # Should only keep last 12
        assert len(trends) == 12
        assert trends[0]["metrics"]["health_score"] == 73  # Week 3 (oldest kept)
        assert trends[-1]["metrics"]["health_score"] == 84  # Week 14 (newest)

    def test_get_trends_empty(self):
        """Test getting trends when no data exists."""
        trends = self.tracker.get_trends()

        assert trends == {}

    def test_get_trends_returns_time_series(self):
        """Test get_trends returns time series data."""
        metrics1 = {"health_score": 85, "coverage": 78.5, "complexity": 4.2}
        metrics2 = {"health_score": 90, "coverage": 82.0, "complexity": 4.0}

        self.tracker.record_metrics(metrics1)
        self.tracker.record_metrics(metrics2)

        trends = self.tracker.get_trends()

        assert len(trends["timestamps"]) == 2
        assert trends["health_scores"] == [85, 90]
        assert trends["coverage"] == [78.5, 82.0]
        assert trends["complexity"] == [4.2, 4.0]

    def test_load_trends_handles_missing_file(self):
        """Test loading trends when file doesn't exist."""
        trends = self.tracker._load_trends()

        assert trends == []

    def test_load_trends_handles_corrupt_file(self):
        """Test loading trends with corrupt JSON."""
        self.tracker.trends_file.parent.mkdir(parents=True, exist_ok=True)
        self.tracker.trends_file.write_text("not valid json")

        trends = self.tracker._load_trends()

        assert trends == []

    def test_save_trends_creates_directory(self):
        """Test saving trends creates data directory."""
        if self.tracker.trends_file.exists():
            self.tracker.trends_file.unlink()
        if self.tracker.trends_file.parent.exists():
            self.tracker.trends_file.parent.rmdir()

        trends = [{"timestamp": datetime.now().isoformat(), "metrics": {}}]
        self.tracker._save_trends(trends)

        assert self.tracker.trends_file.parent.exists()
        assert self.tracker.trends_file.exists()
