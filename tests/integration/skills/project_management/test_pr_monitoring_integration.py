"""
Integration tests for pr-monitoring-analysis skill.

Tests real GitHub API integration (requires gh CLI and GitHub access).

Author: code_developer (implementing US-071)
Date: 2025-10-19
"""

import subprocess
from pathlib import Path

import pytest

from coffee_maker.skills.project_management.pr_monitoring import (
    PRAnalysisReport,
    PRMonitoring,
)


@pytest.fixture
def pr_monitor():
    """Create PR monitoring instance for testing."""
    return PRMonitoring()


def check_gh_cli_available() -> bool:
    """Check if gh CLI is available."""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_gh_auth() -> bool:
    """Check if gh CLI is authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.skipif(not check_gh_cli_available(), reason="gh CLI not available")
@pytest.mark.skipif(not check_gh_auth(), reason="gh CLI not authenticated")
class TestPRMonitoringIntegration:
    """Integration tests with real GitHub API."""

    def test_fetch_prs_from_github(self, pr_monitor: PRMonitoring):
        """Test fetching PRs from GitHub."""
        prs = pr_monitor._fetch_prs()

        # Should return list (may be empty if no PRs)
        assert isinstance(prs, list)

        # If PRs exist, verify structure
        if prs:
            pr = prs[0]
            assert pr.number > 0
            assert pr.title
            assert pr.author
            assert pr.created_at
            assert pr.updated_at

    def test_analyze_prs_end_to_end(self, pr_monitor: PRMonitoring):
        """Test complete PR analysis end-to-end."""
        report = pr_monitor.analyze_prs()

        # Verify report structure
        assert isinstance(report, PRAnalysisReport)
        assert report.repository
        assert report.health_status in ["EXCELLENT", "GOOD", "FAIR", "POOR"]
        assert 0 <= report.metrics.health_score <= 100
        assert report.execution_time_seconds > 0

        # Verify categorization
        assert isinstance(report.categorized_prs, dict)
        assert pr_monitor.CATEGORY_READY_TO_MERGE in report.categorized_prs
        assert pr_monitor.CATEGORY_FAILING_CHECKS in report.categorized_prs

        # Verify report markdown
        assert "Pull Request Monitoring & Analysis Report" in report.report_markdown
        assert report.repository in report.report_markdown

    def test_save_report(self, pr_monitor: PRMonitoring, tmp_path: Path):
        """Test saving PR analysis report."""
        report = pr_monitor.analyze_prs()

        # Save to temporary path
        output_path = tmp_path / "pr-analysis.md"
        saved_path = pr_monitor.save_report(report, output_path)

        # Verify file exists
        assert saved_path.exists()
        assert saved_path == output_path

        # Verify content
        content = saved_path.read_text()
        assert "Pull Request Monitoring & Analysis Report" in content

    def test_categorize_real_prs(self, pr_monitor: PRMonitoring):
        """Test categorizing real PRs from GitHub."""
        prs = pr_monitor._fetch_prs()

        if not prs:
            pytest.skip("No PRs found in repository")

        categorized_prs = pr_monitor._categorize_prs(prs)

        # Verify all categories exist
        assert pr_monitor.CATEGORY_READY_TO_MERGE in categorized_prs
        assert pr_monitor.CATEGORY_WAITING_FOR_REVIEW in categorized_prs
        assert pr_monitor.CATEGORY_FAILING_CHECKS in categorized_prs

        # Verify total count matches
        total_categorized = sum(len(prs) for prs in categorized_prs.values())
        assert total_categorized == len(prs)

    def test_detect_issues_real_prs(self, pr_monitor: PRMonitoring):
        """Test detecting issues in real PRs."""
        prs = pr_monitor._fetch_prs()

        if not prs:
            pytest.skip("No PRs found in repository")

        categorized_prs = pr_monitor._categorize_prs(prs)
        issues = pr_monitor._detect_issues(categorized_prs)

        # Verify issues structure
        assert isinstance(issues, list)

        if issues:
            issue = issues[0]
            assert issue.pr_number > 0
            assert issue.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            assert issue.issue_type
            assert issue.description
            assert issue.recommendation

    def test_generate_recommendations_real_prs(self, pr_monitor: PRMonitoring):
        """Test generating recommendations for real PRs."""
        prs = pr_monitor._fetch_prs()

        if not prs:
            pytest.skip("No PRs found in repository")

        categorized_prs = pr_monitor._categorize_prs(prs)
        issues = pr_monitor._detect_issues(categorized_prs)
        recommendations = pr_monitor._generate_recommendations(categorized_prs, issues)

        # Verify recommendations structure
        assert isinstance(recommendations, list)

        if recommendations:
            rec = recommendations[0]
            assert rec.priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            assert rec.action
            assert rec.details
            assert rec.timeline


@pytest.mark.integration
class TestPRMonitoringWithoutGitHub:
    """Integration tests without requiring GitHub API access."""

    def test_analyze_prs_with_no_github_access(self, tmp_path: Path):
        """Test PR analysis gracefully handles no GitHub access."""
        # Create monitor with temporary path (no git repo)
        monitor = PRMonitoring(repository="test/repo", project_root=tmp_path)

        # Should not raise exception, just return empty report
        report = monitor.analyze_prs()

        assert report.metrics.total_prs == 0
        assert report.metrics.health_score == 100  # No PRs = perfect health
        assert "No issues identified" in report.report_markdown or report.metrics.total_prs == 0

    def test_get_repo_name_without_git(self, tmp_path: Path):
        """Test repository name detection without git."""
        monitor = PRMonitoring(project_root=tmp_path)

        repo_name = monitor._get_repo_name()

        # Should return default
        assert repo_name == "unknown/repo"
