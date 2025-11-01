"""
Integration tests for proactive refactoring analysis with real codebase.

Tests the skill with the actual MonolithicCoffeeMakerAgent codebase.
"""

from pathlib import Path

import pytest

from claude.skills.architecture.proactive_refactoring_analyzer import (
    CodeHealthReport,
    analyze_codebase_health,
    generate_weekly_report,
)


class TestProactiveRefactoringAnalysisIntegration:
    """Integration tests with real codebase."""

    @pytest.fixture
    def codebase_root(self):
        """Get real codebase root."""
        # Assumes tests are run from project root
        return Path(__file__).parents[2]

    def test_analyze_real_codebase(self, codebase_root):
        """Test analyzing the real MonolithicCoffeeMakerAgent codebase."""
        report = analyze_codebase_health(codebase_root)

        # Verify report structure
        assert isinstance(report, CodeHealthReport)
        assert report.codebase_name == codebase_root.name

        # Verify codebase metrics
        assert report.total_loc > 10000  # Our codebase is substantial
        assert report.total_files > 50  # Many Python files

        # Verify opportunities found
        assert len(report.opportunities) > 0

        # Verify top priorities
        assert len(report.top_priorities) > 0
        assert len(report.top_priorities) <= 5

        # Verify health score is reasonable
        assert 0 <= report.overall_health_score <= 100

        # Verify execution time is reasonable (<5 minutes requirement)
        assert report.execution_time_seconds < 300

        # Verify metrics summary exists
        assert "total_loc" in report.metrics_summary
        assert "total_files" in report.metrics_summary
        assert "total_functions" in report.metrics_summary

    def test_generate_weekly_report_real_codebase(self, codebase_root):
        """Test generating weekly report for real codebase."""
        output_path = codebase_root / "evidence" / "refactoring_analysis_integration_test.md"

        # Generate report
        markdown = generate_weekly_report(codebase_root, output_path)

        # Verify markdown structure
        assert "# Refactoring Analysis Report" in markdown
        assert "## Executive Summary" in markdown
        assert "## Refactoring Opportunities" in markdown
        assert "## Metrics Summary" in markdown

        # Verify file was created
        assert output_path.exists()

        # Verify file content
        content = output_path.read_text(encoding="utf-8")
        assert content == markdown

        # Cleanup
        output_path.unlink()

    def test_opportunities_have_roi(self, codebase_root):
        """Test that all opportunities have valid ROI scores."""
        report = analyze_codebase_health(codebase_root)

        for opp in report.opportunities:
            # Verify ROI fields exist
            assert opp.estimated_effort_hours >= 0
            assert opp.time_saved_hours >= 0
            assert opp.roi_score >= 0

            # Verify ROI calculation
            if opp.estimated_effort_hours > 0:
                expected_roi = opp.time_saved_hours / opp.estimated_effort_hours
                assert abs(opp.roi_score - expected_roi) < 0.01

    def test_opportunities_sorted_by_priority(self, codebase_root):
        """Test that opportunities are sorted by priority."""
        report = analyze_codebase_health(codebase_root)

        priorities = [opp.priority for opp in report.opportunities]

        # Check descending order
        for i in range(len(priorities) - 1):
            assert priorities[i] >= priorities[i + 1]

    def test_top_priorities_are_highest_priority(self, codebase_root):
        """Test that top priorities are indeed the highest priority."""
        report = analyze_codebase_health(codebase_root)

        if len(report.opportunities) > 5:
            # Top 5 should have highest priorities
            top_priorities = report.top_priorities[:5]
            other_opportunities = report.opportunities[5:]

            min_top_priority = min(opp.priority for opp in top_priorities)
            max_other_priority = max(opp.priority for opp in other_opportunities)

            assert min_top_priority >= max_other_priority

    def test_metrics_summary_accuracy(self, codebase_root):
        """Test that metrics summary accurately reflects codebase."""
        report = analyze_codebase_health(codebase_root)
        summary = report.metrics_summary

        # Verify counts match report totals
        assert summary["total_files"] == report.total_files
        assert summary["total_loc"] == report.total_loc

        # Verify averages are reasonable
        assert summary["avg_loc_per_file"] > 0
        assert summary["avg_complexity"] > 0

        # Verify file counts
        assert summary["files_over_500_loc"] >= 0
        assert summary["files_over_1000_loc"] >= 0
        assert summary["files_over_1000_loc"] <= summary["files_over_500_loc"]

    def test_trend_tracking_works(self, codebase_root):
        """Test that trend tracking works over multiple analyses."""
        # First analysis
        analyze_codebase_health(codebase_root)

        # Second analysis (should record trend)
        analyze_codebase_health(codebase_root)

        # Verify trends file exists
        trends_file = codebase_root / "data" / "refactoring_analysis" / "trends.json"
        assert trends_file.exists()

        # Verify trends data
        from coffee_maker.utils.file_io import read_json_file

        trends = read_json_file(trends_file)
        assert len(trends) >= 2
        assert all("health_score" in t for t in trends)
        assert all("total_loc" in t for t in trends)

    def test_execution_time_meets_requirement(self, codebase_root):
        """Test that analysis completes within 5 minutes (acceptance criterion)."""
        report = analyze_codebase_health(codebase_root)

        # Acceptance criterion: <5 minutes (300 seconds)
        assert report.execution_time_seconds < 300

        # Target: <1 minute for good performance
        print(f"Execution time: {report.execution_time_seconds:.2f}s")

    def test_report_readability(self, codebase_root):
        """Test that generated report is readable and well-formatted."""
        markdown = generate_weekly_report(codebase_root)

        # Check for emojis (makes report more readable)
        emoji_indicators = ["🟢", "🟡", "🔴", "🏆", "🥈", "🥉"]
        assert any(emoji in markdown for emoji in emoji_indicators)

        # Check for tables
        assert "| Metric | Value |" in markdown or "| Metric |" in markdown

        # Check for section headers
        required_sections = [
            "# Refactoring Analysis Report",
            "## Executive Summary",
            "## Refactoring Opportunities",
            "## Metrics Summary",
            "## Next Steps",
        ]
        for section in required_sections:
            assert section in markdown, f"Missing section: {section}"

    def test_opportunities_have_actionable_recommendations(self, codebase_root):
        """Test that opportunities have actionable recommendations."""
        report = analyze_codebase_health(codebase_root)

        for opp in report.opportunities[:5]:  # Check top 5
            # Must have clear title
            assert len(opp.title) > 0

            # Must have current state
            assert len(opp.current_state) > 0

            # Must have proposed refactoring
            assert len(opp.proposed_refactoring) > 0

            # Must have benefits
            assert len(opp.benefits) > 0

            # Must have files affected
            assert len(opp.files_affected) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
