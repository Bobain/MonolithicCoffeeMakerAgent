"""Tests for Code Complexity Analyzer."""

from pathlib import Path
from textwrap import dedent


from coffee_maker.skills.refactoring_analysis.proactive_refactoring_analysis import (
    CodeComplexityAnalyzer,
)


class TestCodeComplexityAnalyzer:
    """Test code complexity analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path("/tmp/test_complexity_analysis")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = CodeComplexityAnalyzer(self.test_dir)

    def teardown_method(self):
        """Clean up test files."""
        for file in self.test_dir.rglob("*.py"):
            file.unlink()
        if self.test_dir.exists():
            self.test_dir.rmdir()

    def test_analyze_empty_codebase(self):
        """Test analyzing empty codebase."""
        metrics = self.analyzer.analyze()

        assert metrics["files_over_500_loc"] == []
        assert metrics["files_over_1000_loc"] == []
        assert metrics["complex_functions"] == []
        assert metrics["average_complexity"] == 0.0
        assert metrics["maintainability_index"] == 0.0

    def test_analyze_detects_large_file(self):
        """Test detection of file >500 LOC."""
        # Create file with 600 lines
        large_file = self.test_dir / "large.py"
        content = "\n".join([f"# Line {i}" for i in range(600)])
        large_file.write_text(content)

        metrics = self.analyzer.analyze()

        assert len(metrics["files_over_500_loc"]) == 1
        assert metrics["files_over_500_loc"][0]["loc"] == 600

    def test_analyze_detects_very_large_file(self):
        """Test detection of file >1000 LOC."""
        # Create file with 1200 lines
        huge_file = self.test_dir / "huge.py"
        content = "\n".join([f"# Line {i}" for i in range(1200)])
        huge_file.write_text(content)

        metrics = self.analyzer.analyze()

        assert len(metrics["files_over_1000_loc"]) == 1
        assert metrics["files_over_1000_loc"][0]["loc"] == 1200

    def test_analyze_detects_complex_function(self):
        """Test detection of complex function (cyclomatic complexity >10)."""
        complex_file = self.test_dir / "complex.py"
        content = dedent(
            """
            def complex_function(x):
                if x == 1:
                    return 1
                elif x == 2:
                    return 2
                elif x == 3:
                    return 3
                elif x == 4:
                    return 4
                elif x == 5:
                    return 5
                elif x == 6:
                    return 6
                elif x == 7:
                    return 7
                elif x == 8:
                    return 8
                elif x == 9:
                    return 9
                elif x == 10:
                    return 10
                else:
                    return 0
            """
        )
        complex_file.write_text(content)

        metrics = self.analyzer.analyze()

        assert len(metrics["complex_functions"]) >= 1
        complex_func = metrics["complex_functions"][0]
        assert complex_func["function"] == "complex_function"
        assert complex_func["complexity"] > 10

    def test_analyze_calculates_average_complexity(self):
        """Test average complexity calculation."""
        simple_file = self.test_dir / "simple.py"
        content = dedent(
            """
            def func1(x):
                if x > 0:
                    return x
                return 0

            def func2(x):
                return x * 2

            def func3(x):
                if x > 0:
                    if x < 10:
                        return x
                return 0
            """
        )
        simple_file.write_text(content)

        metrics = self.analyzer.analyze()

        assert metrics["average_complexity"] > 0
        assert isinstance(metrics["average_complexity"], float)

    def test_analyze_handles_syntax_errors(self):
        """Test analyzer handles files with syntax errors."""
        bad_file = self.test_dir / "bad.py"
        bad_file.write_text("def broken(:\n    pass")

        # Should not raise exception
        metrics = self.analyzer.analyze()

        assert metrics is not None

    def test_analyze_handles_unicode_errors(self):
        """Test analyzer handles unicode decode errors."""
        binary_file = self.test_dir / "binary.py"
        binary_file.write_bytes(b"\xff\xfe\x00\x00")

        # Should not raise exception
        metrics = self.analyzer.analyze()

        assert metrics is not None
