"""Integration tests for proactive refactoring analysis skill."""

from pathlib import Path

import pytest

from claude.skills.refactoring_analysis.proactive_refactoring_analysis import (
    WeeklyReportGenerator,
    main,
)


class TestProactiveRefactoringIntegration:
    """Integration tests for full refactoring analysis workflow."""

    def test_generate_report_for_real_codebase(self):
        """Test generating report for actual MonolithicCoffeeMakerAgent codebase."""
        # Get project root
        codebase_path = Path(__file__).parents[4]
        assert (codebase_path / "coffee_maker").exists()

        generator = WeeklyReportGenerator(codebase_path)
        report = generator.generate_report()

        # Verify report structure
        assert "# Proactive Refactoring Analysis Report" in report
        assert "Executive Summary" in report
        assert "Top Recommendations" in report
        assert "Detailed Metrics" in report
        assert "Next Steps" in report

        # Verify metrics are present
        assert "Code Health Score" in report
        assert "Average Complexity" in report
        assert "Test Coverage" in report
        assert "Code Duplication" in report

    def test_main_saves_report_to_evidence(self):
        """Test main() function saves report to evidence directory."""
        codebase_path = Path(__file__).parents[4]

        # Run analysis
        main(codebase_path)

        # Check report was saved
        evidence_dir = codebase_path / "evidence"
        assert evidence_dir.exists()

        # Find most recent report
        reports = list(evidence_dir.glob("refactoring-analysis-*.md"))
        assert len(reports) > 0

        # Verify report content
        latest_report = max(reports, key=lambda p: p.stat().st_mtime)
        report_content = latest_report.read_text()

        assert "# Proactive Refactoring Analysis Report" in report_content
        assert len(report_content) > 500  # Should be substantial

    def test_analysis_completes_in_time(self):
        """Test analysis completes within 5 minute target."""
        import time

        codebase_path = Path(__file__).parents[4]

        start_time = time.time()
        main(codebase_path)
        end_time = time.time()

        elapsed = end_time - start_time

        # Should complete in <5 minutes (300 seconds)
        assert elapsed < 300, f"Analysis took {elapsed:.1f}s (target: <300s)"
        print(f"\n✅ Analysis completed in {elapsed:.1f} seconds")

    def test_recommendations_have_roi(self):
        """Test all recommendations include ROI calculations."""
        codebase_path = Path(__file__).parents[4]

        generator = WeeklyReportGenerator(codebase_path)
        report = generator.generate_report()

        # Check for ROI indicators
        if "Top Recommendations" in report:
            # If recommendations exist, verify ROI fields
            assert "ROI:" in report or "No recommendations" in report
            assert "Effort:" in report or "No recommendations" in report
            assert "Time Saved:" in report or "No recommendations" in report

    def test_report_includes_health_score(self):
        """Test report includes overall health score."""
        codebase_path = Path(__file__).parents[4]

        generator = WeeklyReportGenerator(codebase_path)
        report = generator.generate_report()

        # Check for health score
        assert "Code Health Score:" in report

        # Extract and verify health score is valid
        import re

        match = re.search(r"Code Health Score:\*\* (\d+)/100", report)
        if match:
            health_score = int(match.group(1))
            assert 0 <= health_score <= 100

    def test_report_tracks_multiple_metrics(self):
        """Test report includes all required metric categories."""
        codebase_path = Path(__file__).parents[4]

        generator = WeeklyReportGenerator(codebase_path)
        report = generator.generate_report()

        # Verify all metric categories are present
        required_sections = [
            "Code Complexity",
            "Code Duplication",
            "Test Coverage",
            "Dependencies",
        ]

        for section in required_sections:
            assert section in report, f"Missing section: {section}"

    @pytest.mark.slow
    def test_trend_tracking_across_runs(self):
        """Test trend tracking accumulates data across multiple runs."""
        from claude.skills.refactoring_analysis.proactive_refactoring_analysis import (
            TrendTracker,
        )

        codebase_path = Path(__file__).parents[4]
        tracker = TrendTracker(codebase_path)

        # Record multiple metrics
        metrics1 = {"health_score": 85, "coverage": 78.5, "complexity": 4.2}
        metrics2 = {"health_score": 87, "coverage": 80.0, "complexity": 4.0}

        tracker.record_metrics(metrics1)
        tracker.record_metrics(metrics2)

        # Get trends
        trends = tracker.get_trends()

        assert len(trends["timestamps"]) >= 2
        assert len(trends["health_scores"]) >= 2
        assert len(trends["coverage"]) >= 2

    def test_report_prioritizes_by_roi(self):
        """Test recommendations are sorted by ROI."""
        codebase_path = Path(__file__).parents[4]

        generator = WeeklyReportGenerator(codebase_path)
        report = generator.generate_report()

        # Extract ROI percentages
        import re

        roi_matches = re.findall(r"ROI:\*\* ([\d.]+)%", report)

        if len(roi_matches) > 1:
            # Convert to floats and check descending order
            roi_values = [float(roi) for roi in roi_matches]

            # Check if sorted in descending order
            assert roi_values == sorted(roi_values, reverse=True), "ROI values should be sorted in descending order"
