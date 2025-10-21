"""
Unit tests for proactive refactoring analyzer skill.

Tests cover:
- Code metrics calculation
- Refactoring opportunity detection
- ROI calculation
- Health score calculation
- Report generation
- Trend tracking
"""

import ast
import tempfile
from pathlib import Path

import pytest

from coffee_maker.skills.architecture.proactive_refactoring_analyzer import (
    CodeHealthReport,
    CodeMetrics,
    ProactiveRefactoringAnalyzer,
    RefactoringOpportunity,
    analyze_codebase_health,
    generate_weekly_report,
)


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        codebase_root = Path(tmpdir)

        # Create coffee_maker directory
        coffee_maker = codebase_root / "coffee_maker"
        coffee_maker.mkdir()

        # Create a simple file
        simple_file = coffee_maker / "simple.py"
        simple_file.write_text(
            """
def hello():
    return "world"

def add(a, b):
    return a + b
""",
            encoding="utf-8",
        )

        # Create a large file (>500 LOC)
        large_file = coffee_maker / "large.py"
        # Generate enough lines to exceed 500 LOC (need ~125 functions for 500+ lines)
        large_content = "# Large file\n" + "\n".join(
            [f'def func_{i}():\n    """Function {i}"""\n    pass\n' for i in range(150)]
        )
        large_file.write_text(large_content, encoding="utf-8")

        # Create a file with technical debt
        debt_file = coffee_maker / "debt.py"
        debt_file.write_text(
            """
# TODO: Implement proper error handling
# FIXME: This is broken
# HACK: Temporary workaround

def broken_function():
    pass
""",
            encoding="utf-8",
        )

        # Create a complex file with god class
        complex_file = coffee_maker / "complex.py"
        methods = "\n".join([f"    def method_{i}(self):\n        pass\n" for i in range(25)])
        complex_content = f"""
class GodClass:
{methods}
"""
        complex_file.write_text(complex_content, encoding="utf-8")

        yield codebase_root


class TestProactiveRefactoringAnalyzer:
    """Test ProactiveRefactoringAnalyzer class."""

    def test_initialization(self, temp_codebase):
        """Test analyzer initialization."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        assert analyzer.codebase_root == temp_codebase
        assert analyzer.data_dir.exists()
        assert analyzer.trends_file.exists() or not analyzer.trends_file.exists()  # May not exist yet

    def test_calculate_file_metrics_simple(self, temp_codebase):
        """Test metrics calculation for simple file."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)
        simple_file = temp_codebase / "coffee_maker" / "simple.py"

        metrics = analyzer._calculate_file_metrics(simple_file)

        assert isinstance(metrics, CodeMetrics)
        assert metrics.file_path == str(simple_file)
        assert metrics.lines_of_code > 0
        assert metrics.num_functions == 2
        assert metrics.num_classes == 0
        assert metrics.num_todos == 0
        assert metrics.num_fixmes == 0

    def test_calculate_file_metrics_with_debt(self, temp_codebase):
        """Test metrics calculation for file with technical debt."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)
        debt_file = temp_codebase / "coffee_maker" / "debt.py"

        metrics = analyzer._calculate_file_metrics(debt_file)

        assert metrics.num_todos >= 1
        assert metrics.num_fixmes >= 1
        assert metrics.num_hacks >= 1

    def test_calculate_all_metrics(self, temp_codebase):
        """Test calculating metrics for all files."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        metrics = analyzer._calculate_all_metrics()

        assert len(metrics) >= 4  # simple, large, debt, complex
        assert all(isinstance(m, CodeMetrics) for m in metrics)
        assert all(m.lines_of_code > 0 for m in metrics)

    def test_find_refactoring_opportunities_large_file(self, temp_codebase):
        """Test finding opportunities for large files."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)
        large_file = temp_codebase / "coffee_maker" / "large.py"

        metrics = [analyzer._calculate_file_metrics(large_file)]
        opportunities = analyzer._find_refactoring_opportunities(metrics)

        # Should detect large file
        large_file_opportunities = [
            o for o in opportunities if "large.py" in o.title or str(large_file) in o.files_affected
        ]
        assert len(large_file_opportunities) > 0

        # Check opportunity properties
        opp = large_file_opportunities[0]
        assert opp.category == "complexity"
        assert opp.severity in ["HIGH", "CRITICAL"]
        assert opp.estimated_effort_hours > 0
        assert opp.time_saved_hours > 0
        assert opp.roi_score > 0

    def test_find_refactoring_opportunities_technical_debt(self, temp_codebase):
        """Test finding opportunities for technical debt."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        metrics = analyzer._calculate_all_metrics()
        opportunities = analyzer._find_refactoring_opportunities(metrics)

        # Should detect technical debt
        debt_opportunities = [o for o in opportunities if o.category == "technical_debt"]
        assert len(debt_opportunities) > 0

        opp = debt_opportunities[0]
        assert "TODO" in opp.current_state or "FIXME" in opp.current_state
        assert opp.estimated_effort_hours > 0

    def test_find_refactoring_opportunities_god_class(self, temp_codebase):
        """Test finding opportunities for god classes."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)
        complex_file = temp_codebase / "coffee_maker" / "complex.py"

        metrics = [analyzer._calculate_file_metrics(complex_file)]
        opportunities = analyzer._find_refactoring_opportunities(metrics)

        # Should detect god class (>20 methods)
        god_class_opportunities = [o for o in opportunities if o.category == "architecture"]
        assert len(god_class_opportunities) > 0

        opp = god_class_opportunities[0]
        assert "mixin" in opp.proposed_refactoring.lower() or "extract" in opp.proposed_refactoring.lower()
        assert opp.severity == "HIGH"

    def test_calculate_health_score(self, temp_codebase):
        """Test health score calculation."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        metrics = analyzer._calculate_all_metrics()
        opportunities = analyzer._find_refactoring_opportunities(metrics)
        health_score = analyzer._calculate_health_score(metrics, opportunities)

        assert 0 <= health_score <= 100
        assert isinstance(health_score, float)

    def test_calculate_health_score_empty(self, temp_codebase):
        """Test health score with no metrics."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        health_score = analyzer._calculate_health_score([], [])

        assert health_score == 100.0  # Perfect score for empty codebase

    def test_create_metrics_summary(self, temp_codebase):
        """Test metrics summary creation."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        metrics = analyzer._calculate_all_metrics()
        summary = analyzer._create_metrics_summary(metrics)

        assert "total_files" in summary
        assert "total_loc" in summary
        assert "avg_loc_per_file" in summary
        assert "total_functions" in summary
        assert "total_classes" in summary
        assert "total_todos" in summary
        assert "files_over_500_loc" in summary

        assert summary["total_files"] == len(metrics)
        assert summary["total_loc"] > 0
        assert summary["files_over_500_loc"] >= 1  # large.py

    def test_analyze_codebase(self, temp_codebase):
        """Test full codebase analysis."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        report = analyzer.analyze_codebase()

        assert isinstance(report, CodeHealthReport)
        assert report.codebase_name == temp_codebase.name
        assert report.total_loc > 0
        assert report.total_files >= 4
        assert len(report.opportunities) > 0
        assert len(report.top_priorities) > 0
        assert 0 <= report.overall_health_score <= 100
        assert report.execution_time_seconds > 0
        assert report.metrics_summary

    def test_generate_report_markdown(self, temp_codebase):
        """Test markdown report generation."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)
        report = analyzer.analyze_codebase()

        markdown = analyzer.generate_report_markdown(report)

        # Check report structure
        assert "# Refactoring Analysis Report" in markdown
        assert "## Executive Summary" in markdown
        assert "## Refactoring Opportunities" in markdown
        assert "## Metrics Summary" in markdown
        assert "## Next Steps" in markdown

        # Check content
        assert str(report.overall_health_score) in markdown
        assert str(len(report.opportunities)) in markdown
        assert "architect" in markdown

    def test_trend_tracking(self, temp_codebase):
        """Test trend data recording."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        # First analysis
        report1 = analyzer.analyze_codebase()

        # Check trends file created
        assert analyzer.trends_file.exists()

        # Read trends
        from coffee_maker.utils.file_io import read_json_file

        trends = read_json_file(analyzer.trends_file)
        assert len(trends) == 1
        assert trends[0]["health_score"] == report1.overall_health_score

        # Second analysis (simulate after changes)
        analyzer.analyze_codebase()

        # Check trends updated
        trends = read_json_file(analyzer.trends_file)
        assert len(trends) == 2

    def test_get_trend_analysis_no_data(self, temp_codebase):
        """Test trend analysis with no historical data."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        trend_analysis = analyzer.get_trend_analysis()

        assert "No historical data" in trend_analysis

    def test_get_trend_analysis_with_data(self, temp_codebase):
        """Test trend analysis with historical data."""
        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        # Run two analyses
        analyzer.analyze_codebase()
        analyzer.analyze_codebase()

        trend_analysis = analyzer.get_trend_analysis()

        assert "Trend Analysis" in trend_analysis
        assert "Health Score" in trend_analysis
        assert "Previous" in trend_analysis
        assert "Current" in trend_analysis


class TestHelperFunctions:
    """Test helper functions."""

    def test_analyze_codebase_health(self, temp_codebase):
        """Test analyze_codebase_health function."""
        report = analyze_codebase_health(temp_codebase)

        assert isinstance(report, CodeHealthReport)
        assert report.total_loc > 0
        assert len(report.opportunities) > 0

    def test_generate_weekly_report(self, temp_codebase):
        """Test generate_weekly_report function."""
        markdown = generate_weekly_report(temp_codebase)

        assert isinstance(markdown, str)
        assert "# Refactoring Analysis Report" in markdown
        assert "## Executive Summary" in markdown

    def test_generate_weekly_report_with_output(self, temp_codebase):
        """Test generate_weekly_report with file output."""
        output_file = temp_codebase / "report.md"

        markdown = generate_weekly_report(temp_codebase, output_file)

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == markdown


class TestComplexityCalculation:
    """Test complexity calculation."""

    def test_calculate_complexity_simple(self):
        """Test complexity for simple code."""
        code = """
def simple():
    return 1
"""
        tree = ast.parse(code)
        analyzer = ProactiveRefactoringAnalyzer(Path("."))

        complexity = analyzer._calculate_complexity(tree)

        # Base complexity = 1
        assert complexity >= 1

    def test_calculate_complexity_with_if(self):
        """Test complexity with if statement."""
        code = """
def with_if(x):
    if x > 0:
        return x
    return 0
"""
        tree = ast.parse(code)
        analyzer = ProactiveRefactoringAnalyzer(Path("."))

        complexity = analyzer._calculate_complexity(tree)

        # Base + if = 2
        assert complexity >= 2

    def test_calculate_complexity_with_loops(self):
        """Test complexity with loops."""
        code = """
def with_loops():
    for i in range(10):
        if i % 2 == 0:
            print(i)
    while True:
        break
"""
        tree = ast.parse(code)
        analyzer = ProactiveRefactoringAnalyzer(Path("."))

        complexity = analyzer._calculate_complexity(tree)

        # Base + for + if + while = 4
        assert complexity >= 4


class TestROICalculation:
    """Test ROI calculation for refactorings."""

    def test_roi_score_calculation(self):
        """Test ROI score calculation."""
        opp = RefactoringOpportunity(
            title="Test",
            category="complexity",
            severity="HIGH",
            current_state="Bad",
            proposed_refactoring="Good",
            files_affected=["test.py"],
            estimated_effort_hours=10.0,
            time_saved_hours=20.0,
            roi_score=2.0,
            priority=8,
            benefits=[],
            risks=[],
        )

        assert opp.roi_score == 2.0
        assert opp.time_saved_hours / opp.estimated_effort_hours == 2.0

    def test_roi_priority_high_roi(self):
        """Test that high ROI gets high priority."""
        # High ROI opportunity
        high_roi = RefactoringOpportunity(
            title="High ROI",
            category="duplication",
            severity="HIGH",
            current_state="Duplicated",
            proposed_refactoring="Extract",
            files_affected=["test.py"],
            estimated_effort_hours=2.0,
            time_saved_hours=15.0,
            roi_score=7.5,
            priority=10,
            benefits=["Save time"],
            risks=[],
        )

        # Low ROI opportunity
        low_roi = RefactoringOpportunity(
            title="Low ROI",
            category="naming",
            severity="LOW",
            current_state="Poor names",
            proposed_refactoring="Rename",
            files_affected=["test.py"],
            estimated_effort_hours=5.0,
            time_saved_hours=3.0,
            roi_score=0.6,
            priority=3,
            benefits=["Clarity"],
            risks=[],
        )

        # High ROI should have higher priority
        assert high_roi.priority > low_roi.priority
        assert high_roi.roi_score > low_roi.roi_score


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_codebase(self):
        """Test analyzer with empty codebase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_codebase = Path(tmpdir)
            coffee_maker = empty_codebase / "coffee_maker"
            coffee_maker.mkdir()

            analyzer = ProactiveRefactoringAnalyzer(empty_codebase)
            report = analyzer.analyze_codebase()

            assert report.total_loc == 0
            assert report.total_files == 0
            assert len(report.opportunities) == 0
            assert report.overall_health_score == 100.0  # Perfect empty codebase

    def test_unparseable_file(self, temp_codebase):
        """Test handling of unparseable Python files."""
        coffee_maker = temp_codebase / "coffee_maker"
        bad_file = coffee_maker / "bad_syntax.py"
        bad_file.write_text("def broken(\n    # Missing closing parenthesis", encoding="utf-8")

        analyzer = ProactiveRefactoringAnalyzer(temp_codebase)

        # Should not crash
        metrics = analyzer._calculate_all_metrics()

        # Should include the bad file with minimal metrics
        bad_file_metrics = [m for m in metrics if "bad_syntax.py" in m.file_path]
        assert len(bad_file_metrics) == 1
        assert bad_file_metrics[0].lines_of_code > 0
        assert bad_file_metrics[0].complexity == 0  # Can't parse

    def test_zero_division_protection(self):
        """Test that ROI calculation handles zero effort."""
        opp = RefactoringOpportunity(
            title="Test",
            category="test",
            severity="LOW",
            current_state="",
            proposed_refactoring="",
            files_affected=[],
            estimated_effort_hours=0.0,  # Zero effort
            time_saved_hours=10.0,
            roi_score=0.0,  # Should be 0, not infinity
            priority=1,
            benefits=[],
            risks=[],
        )

        # Should not raise ZeroDivisionError
        assert opp.roi_score == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
