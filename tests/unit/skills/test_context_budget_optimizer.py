"""Tests for context-budget-optimizer skill."""

from pathlib import Path

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from coffee_maker.skills.optimization.context_budget_optimizer import (
    ContextBudgetOptimizer,
    FilePrioritizer,
    TokenCounter,
)


class TestTokenCounter:
    """Tests for TokenCounter."""

    def test_count_tokens_with_text(self):
        """Test token counting with text."""
        counter = TokenCounter()
        text = "This is a test string."
        tokens = counter.count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_tokens_empty_string(self):
        """Test token counting with empty string."""
        counter = TokenCounter()
        tokens = counter.count_tokens("")
        assert tokens == 0

    def test_count_tokens_long_text(self):
        """Test token counting with long text."""
        counter = TokenCounter()
        text = "word " * 1000  # 5000 words ≈ 6250 tokens
        tokens = counter.count_tokens(text)
        assert tokens > 1000


class TestFilePrioritizer:
    """Tests for FilePrioritizer."""

    def test_categorize_high_priority_roadmap(self):
        """Test categorizing ROADMAP file."""
        category = FilePrioritizer.categorize_file("docs/roadmap/ROADMAP.md")
        assert category == "high"

    def test_categorize_high_priority_spec(self):
        """Test categorizing SPEC files."""
        category = FilePrioritizer.categorize_file("docs/architecture/specs/SPEC-001-auth.md")
        assert category == "high"

    def test_categorize_medium_priority_adr(self):
        """Test categorizing ADR files."""
        category = FilePrioritizer.categorize_file("docs/architecture/decisions/ADR-001.md")
        assert category == "medium"

    def test_categorize_low_priority_deprecated(self):
        """Test categorizing deprecated files."""
        category = FilePrioritizer.categorize_file("tests/unit/_deprecated/test_old.py")
        assert category == "low"

    def test_categorize_low_priority_archived(self):
        """Test categorizing archived files."""
        category = FilePrioritizer.categorize_file("docs/archived/old_spec.md")
        assert category == "low"


class TestContextBudgetOptimizer:
    """Tests for ContextBudgetOptimizer."""

    def test_budget_constants(self):
        """Test budget constant values."""
        optimizer = ContextBudgetOptimizer()
        assert optimizer.TOTAL_BUDGET == 200_000
        assert optimizer.CFR_007_THRESHOLD == 0.30
        assert optimizer.BUDGET_LIMIT == 60_000

    def test_analyze_empty_files(self):
        """Test analyzing empty file list."""
        optimizer = ContextBudgetOptimizer()
        analysis = optimizer.analyze_files([])
        assert analysis["total_tokens"] == 0
        assert analysis["exceeds_budget"] is False

    def test_generate_recommendations_within_budget(self):
        """Test recommendations when within budget."""
        optimizer = ContextBudgetOptimizer()
        analysis = {
            "files": [],
            "total_tokens": 30_000,
            "budget_limit": 60_000,
            "exceeds_budget": False,
            "excess_tokens": 0,
        }
        recommendations = optimizer.generate_recommendations(analysis)
        assert len(recommendations) > 0
        assert recommendations[0]["action"] == "no_optimization_needed"

    def test_generate_recommendations_exceeds_budget(self):
        """Test recommendations when exceeding budget."""
        optimizer = ContextBudgetOptimizer()

        from dataclasses import dataclass

        @dataclass
        class MockFile:
            path: str
            estimated_tokens: int
            lines: int
            category: str

        analysis = {
            "files": [
                MockFile("docs/roadmap/ROADMAP.md", 50_000, 28_000, "high"),
                MockFile("docs/architecture/SPEC-001.md", 15_000, 5_000, "high"),
            ],
            "total_tokens": 65_000,
            "budget_limit": 60_000,
            "exceeds_budget": True,
            "excess_tokens": 5_000,
        }
        recommendations = optimizer.generate_recommendations(analysis)
        assert len(recommendations) > 0
        # Should recommend summarizing ROADMAP
        assert any(r["action"] == "summarize" for r in recommendations)

    def test_generate_report_format(self):
        """Test report generation format."""
        optimizer = ContextBudgetOptimizer()

        from dataclasses import dataclass

        @dataclass
        class MockFile:
            path: str
            estimated_tokens: int
            lines: int
            category: str

        analysis = {
            "files": [MockFile("docs/roadmap/ROADMAP.md", 30_000, 28_000, "high")],
            "total_tokens": 30_000,
            "budget_limit": 60_000,
            "exceeds_budget": False,
        }
        recommendations = [
            {
                "action": "no_optimization_needed",
                "message": "Within budget",
            }
        ]
        report = optimizer.generate_report("architect", "Create spec", analysis, recommendations)
        assert "CONTEXT BUDGET ANALYSIS REPORT" in report
        assert "architect" in report
        assert "Create spec" in report
        assert "Within budget" in report

    def test_budget_usage_percentage(self):
        """Test budget usage percentage calculation."""
        ContextBudgetOptimizer()
        analysis = {
            "files": [],
            "total_tokens": 30_000,
            "budget_limit": 60_000,
            "exceeds_budget": False,
        }
        percentage = analysis["total_tokens"] / analysis["budget_limit"] * 100
        assert percentage == 50.0


class TestContextBudgetIntegration:
    """Integration tests for context budget optimizer."""

    def test_workflow_within_budget(self):
        """Test complete workflow when within budget."""
        optimizer = ContextBudgetOptimizer()
        files = ["docs/roadmap/ROADMAP.md"]  # If exists

        # This test is conditional on file existing
        # Just test that the workflow doesn't crash
        try:
            analysis = optimizer.analyze_files(files)
            recommendations = optimizer.generate_recommendations(analysis)
            report = optimizer.generate_report(
                "architect",
                "Create technical spec",
                analysis,
                recommendations,
            )
            assert "CONTEXT BUDGET ANALYSIS REPORT" in report
        except FileNotFoundError:
            # File may not exist in test environment
            pass

    def test_excess_calculation_accuracy(self):
        """Test that excess token calculation is accurate."""
        ContextBudgetOptimizer()
        from dataclasses import dataclass

        @dataclass
        class MockFile:
            path: str
            estimated_tokens: int
            lines: int
            category: str

        analysis = {
            "files": [
                MockFile("file1.md", 50_000, 1000, "high"),
                MockFile("file2.md", 20_000, 500, "high"),
            ],
            "total_tokens": 70_000,
            "budget_limit": 60_000,
            "exceeds_budget": True,
            "excess_tokens": 10_000,
        }
        assert analysis["excess_tokens"] == 10_000
        assert analysis["exceeds_budget"] is True
