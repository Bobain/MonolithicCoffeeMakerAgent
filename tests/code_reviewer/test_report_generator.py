"""Tests for report generator."""

import tempfile
from datetime import datetime
from pathlib import Path

from coffee_maker.code_reviewer.models import ReviewIssue, ReviewReport
from coffee_maker.code_reviewer.report_generator import ReportGenerator


class TestReportGenerator:
    """Test suite for ReportGenerator."""

    def test_report_generator_initialization(self):
        """Test ReportGenerator can be initialized."""
        generator = ReportGenerator()
        assert generator is not None

    def test_generate_html_with_issues(self):
        """Test HTML generation with issues."""
        # Create a mock report
        report = ReviewReport(file_path="test.py", timestamp=datetime.now())

        report.add_issue(
            ReviewIssue(
                severity="critical",
                category="security",
                title="SQL Injection vulnerability",
                description="Direct string interpolation in SQL query",
                line_number=10,
                code_snippet='query = f"SELECT * FROM users WHERE id = {user_id}"',
                suggestion="Use parameterized queries",
                perspective="Security Auditor",
            )
        )

        report.add_issue(
            ReviewIssue(
                severity="high",
                category="bug",
                title="Resource leak detected",
                description="File opened without context manager",
                line_number=15,
                code_snippet='f = open("test.txt")',
                suggestion="Use: with open(...) as f:",
                perspective="Bug Hunter",
            )
        )

        report.calculate_metrics()
        report.summary = "Found 2 critical issues"

        generator = ReportGenerator()
        html = generator.generate_html(report)

        # Verify HTML contains key elements
        assert "<!DOCTYPE html>" in html
        assert "Code Review Report" in html
        assert "SQL Injection" in html
        assert "Resource leak" in html
        assert "critical" in html.lower()
        assert "high" in html.lower()

    def test_generate_html_no_issues(self):
        """Test HTML generation with no issues."""
        report = ReviewReport(file_path="test.py", timestamp=datetime.now())
        report.calculate_metrics()
        report.summary = "No issues found"

        generator = ReportGenerator()
        html = generator.generate_html(report)

        # Should indicate no issues
        assert "No issues found" in html or "Code looks great" in html or "looks good" in html

    def test_generate_markdown_with_issues(self):
        """Test Markdown generation with issues."""
        report = ReviewReport(file_path="test.py", timestamp=datetime.now())

        report.add_issue(
            ReviewIssue(
                severity="critical",
                category="security",
                title="Hardcoded secret",
                description="API key hardcoded in source",
                line_number=5,
                suggestion="Use environment variables",
                perspective="Security Auditor",
            )
        )

        report.calculate_metrics()
        report.summary = "Found 1 critical issue"

        generator = ReportGenerator()
        markdown = generator.generate_markdown(report)

        # Verify Markdown contains key elements
        assert "# Code Review Report" in markdown
        assert "Hardcoded secret" in markdown
        assert "Critical Issues" in markdown
        assert "**Severity:**" in markdown

    def test_save_html_report(self):
        """Test saving HTML report to file."""
        report = ReviewReport(file_path="test.py", timestamp=datetime.now())
        report.calculate_metrics()
        report.summary = "Test report"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_path = f.name

        try:
            generator = ReportGenerator()
            generator.save_html_report(report, temp_path)

            # Verify file was created
            assert Path(temp_path).exists()

            # Verify content
            content = Path(temp_path).read_text()
            assert "<!DOCTYPE html>" in content
            assert "Code Review Report" in content

        finally:
            Path(temp_path).unlink()

    def test_save_markdown_report(self):
        """Test saving Markdown report to file."""
        report = ReviewReport(file_path="test.py", timestamp=datetime.now())
        report.calculate_metrics()
        report.summary = "Test report"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            generator = ReportGenerator()
            generator.save_markdown_report(report, temp_path)

            # Verify file was created
            assert Path(temp_path).exists()

            # Verify content
            content = Path(temp_path).read_text()
            assert "# Code Review Report" in content

        finally:
            Path(temp_path).unlink()

    def test_html_severity_grouping(self):
        """Test that HTML groups issues by severity."""
        report = ReviewReport(file_path="test.py", timestamp=datetime.now())

        # Add issues of different severities
        for severity in ["critical", "high", "medium", "low"]:
            report.add_issue(
                ReviewIssue(
                    severity=severity,
                    category="bug",
                    title=f"{severity} issue",
                    description=f"This is a {severity} issue",
                    perspective="Bug Hunter",
                )
            )

        report.calculate_metrics()

        generator = ReportGenerator()
        html = generator.generate_html(report)

        # Should have sections for each severity
        assert "Critical Issues" in html
        assert "High Priority Issues" in html
        assert "Medium Priority Issues" in html
        assert "Low Priority Issues" in html
