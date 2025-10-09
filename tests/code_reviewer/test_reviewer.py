"""Tests for MultiModelCodeReviewer."""

import tempfile
from pathlib import Path

import pytest

from coffee_maker.code_reviewer.models import ReviewReport
from coffee_maker.code_reviewer.reviewer import MultiModelCodeReviewer


class TestMultiModelCodeReviewer:
    """Test suite for MultiModelCodeReviewer."""

    def test_reviewer_initialization(self):
        """Test reviewer can be initialized."""
        reviewer = MultiModelCodeReviewer()
        assert reviewer is not None
        assert len(reviewer.perspectives) == 4  # All 4 perspectives

    def test_reviewer_with_selected_perspectives(self):
        """Test reviewer can be initialized with specific perspectives."""
        reviewer = MultiModelCodeReviewer(enable_perspectives=["bug_hunter"])
        assert len(reviewer.perspectives) == 1
        assert "bug_hunter" in reviewer.perspectives

    def test_review_file_with_issues(self):
        """Test reviewing a file that has issues."""
        # Create a temporary Python file with known issues
        test_code = (
            '''
# Test file with various issues

def problematic_function():
    # Bare except
    try:
        result = risky_operation()
    except:
        pass

    # File without context manager
    f = open("test.txt", "r")
    data = f.read()

    # String concatenation in loop
    result = ""
    for i in range(100):
        result += str(i)

    return result

class VeryLargeClass:
    """This class is intentionally large for testing."""
    '''
            + "\n    pass\n" * 350
        )  # Make it over 300 lines

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            reviewer = MultiModelCodeReviewer()
            report = reviewer.review_file(temp_path)

            # Verify report was created
            assert isinstance(report, ReviewReport)
            assert report.file_path == temp_path

            # Verify issues were found
            assert len(report.issues) > 0

            # Verify metrics were calculated
            assert "total_issues" in report.metrics
            assert report.metrics["total_issues"] > 0

            # Verify we found specific issues
            issue_titles = [issue.title for issue in report.issues]

            # Should find bare except
            assert any("except" in title.lower() for title in issue_titles)

        finally:
            Path(temp_path).unlink()

    def test_review_file_clean_code(self):
        """Test reviewing a file with no issues."""
        test_code = '''
"""Clean Python module."""

def well_written_function(param1: str, param2: int) -> str:
    """A well-written function with proper documentation.

    Args:
        param1: First parameter
        param2: Second parameter

    Returns:
        Formatted string
    """
    result = f"{param1}: {param2}"
    return result
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            reviewer = MultiModelCodeReviewer()
            report = reviewer.review_file(temp_path)

            # Report should be created
            assert isinstance(report, ReviewReport)

            # Clean code should have few or no issues
            assert report.metrics["total_issues"] <= 2  # Allow minor style suggestions

        finally:
            Path(temp_path).unlink()

    def test_review_nonexistent_file(self):
        """Test reviewing a file that doesn't exist."""
        reviewer = MultiModelCodeReviewer()

        with pytest.raises(FileNotFoundError):
            reviewer.review_file("/nonexistent/file.py")

    def test_review_directory(self):
        """Test reviewing all files in a directory."""
        # Create a temporary directory with multiple Python files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "file1.py").write_text("def test1(): pass")
            (Path(temp_dir) / "file2.py").write_text("def test2(): pass")
            (Path(temp_dir) / "subdir").mkdir()
            (Path(temp_dir) / "subdir" / "file3.py").write_text("def test3(): pass")

            reviewer = MultiModelCodeReviewer()
            reports = reviewer.review_directory(temp_dir)

            # Should find all 3 Python files
            assert len(reports) == 3

            # All should be ReviewReport instances
            assert all(isinstance(r, ReviewReport) for r in reports)

    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        test_code = """
try:
    x = 1
except:
    pass

f = open("test.txt")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            reviewer = MultiModelCodeReviewer()
            report = reviewer.review_file(temp_path)

            # Get issues by severity
            report.get_issues_by_severity("critical")
            high = report.get_issues_by_severity("high")
            report.get_issues_by_severity("medium")

            # Should have various severities
            assert len(report.issues) > 0

            # All returned issues should match the severity
            for issue in high:
                assert issue.severity == "high"

        finally:
            Path(temp_path).unlink()

    def test_get_issues_by_category(self):
        """Test filtering issues by category."""
        test_code = """
try:
    x = 1
except:
    pass
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            reviewer = MultiModelCodeReviewer()
            report = reviewer.review_file(temp_path)

            # Get issues by category
            bugs = report.get_issues_by_category("bug")

            # Should have bug-related issues
            assert len(bugs) > 0

            # All returned issues should be bug category
            for issue in bugs:
                assert issue.category == "bug"

        finally:
            Path(temp_path).unlink()

    def test_report_summary_generation(self):
        """Test that report summary is generated."""
        test_code = "def test(): pass"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = f.name

        try:
            reviewer = MultiModelCodeReviewer()
            report = reviewer.review_file(temp_path)

            # Summary should be generated
            assert report.summary is not None
            assert len(report.summary) > 0

        finally:
            Path(temp_path).unlink()
