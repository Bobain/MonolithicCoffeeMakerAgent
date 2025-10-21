"""
Unit tests for PR Monitoring skill.

Author: code_developer
Date: 2025-10-19
Related: US-071
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Import functions from pr_monitoring.py
# Note: The skill file uses dashes, which isn't valid Python import syntax
# We need to import it dynamically
import importlib.util

spec = importlib.util.spec_from_file_location(
    "pr_monitoring", Path(".claude/skills/project-manager/pr-monitoring/pr_monitoring.py")
)
pr_monitoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr_monitoring)


@pytest.fixture
def mock_prs():
    """Sample PR data for testing."""
    now = datetime.now(timezone.utc)

    return [
        # Ready to merge
        {
            "number": 1,
            "title": "Feature: Add user authentication",
            "author": "developer1",
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(hours=1),
            "is_draft": False,
            "labels": ["feature", "priority-high"],
            "reviews": [{"state": "APPROVED", "author": {"login": "reviewer1"}}],
            "status_checks": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
        # Failing checks
        {
            "number": 2,
            "title": "Fix: Database connection",
            "author": "developer2",
            "created_at": now - timedelta(days=3),
            "updated_at": now - timedelta(days=2),
            "is_draft": False,
            "labels": ["bug"],
            "reviews": [],
            "status_checks": [{"state": "FAILURE", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
        # Merge conflicts
        {
            "number": 3,
            "title": "Refactor: Code cleanup",
            "author": "developer3",
            "created_at": now - timedelta(days=5),
            "updated_at": now - timedelta(days=4),
            "is_draft": False,
            "labels": ["refactor"],
            "reviews": [],
            "status_checks": [],
            "mergeable": "CONFLICTING",
        },
        # Stale
        {
            "number": 4,
            "title": "Experimental: New feature",
            "author": "developer4",
            "created_at": now - timedelta(days=15),
            "updated_at": now - timedelta(days=10),
            "is_draft": False,
            "labels": ["experimental"],
            "reviews": [],
            "status_checks": [],
            "mergeable": "MERGEABLE",
        },
        # Draft
        {
            "number": 5,
            "title": "[WIP] Work in progress",
            "author": "developer5",
            "created_at": now - timedelta(days=1),
            "updated_at": now - timedelta(hours=6),
            "is_draft": True,
            "labels": ["wip"],
            "reviews": [],
            "status_checks": [],
            "mergeable": "MERGEABLE",
        },
        # Changes requested
        {
            "number": 6,
            "title": "Feature: Add analytics",
            "author": "developer6",
            "created_at": now - timedelta(days=6),
            "updated_at": now - timedelta(days=6),
            "is_draft": False,
            "labels": ["feature"],
            "reviews": [{"state": "CHANGES_REQUESTED", "author": {"login": "reviewer2"}}],
            "status_checks": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
        # Waiting for review
        {
            "number": 7,
            "title": "Feature: Add notifications",
            "author": "developer7",
            "created_at": now - timedelta(days=4),
            "updated_at": now - timedelta(days=4),
            "is_draft": False,
            "labels": ["feature"],
            "reviews": [],
            "status_checks": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
    ]


def test_categorize_pr_ready_to_merge(mock_prs):
    """Test PR categorization: ready to merge."""
    pr = mock_prs[0]  # Ready to merge PR
    now = datetime.now(timezone.utc)

    category = pr_monitoring.categorize_pr(pr, now)

    assert category == "ready_to_merge"


def test_categorize_pr_failing_checks(mock_prs):
    """Test PR categorization: failing checks."""
    pr = mock_prs[1]  # Failing checks PR
    now = datetime.now(timezone.utc)

    category = pr_monitoring.categorize_pr(pr, now)

    assert category == "failing_checks"


def test_categorize_pr_merge_conflicts(mock_prs):
    """Test PR categorization: merge conflicts."""
    pr = mock_prs[2]  # Merge conflicts PR
    now = datetime.now(timezone.utc)

    category = pr_monitoring.categorize_pr(pr, now)

    assert category == "merge_conflicts"


def test_categorize_pr_stale(mock_prs):
    """Test PR categorization: stale."""
    pr = mock_prs[3]  # Stale PR
    now = datetime.now(timezone.utc)

    category = pr_monitoring.categorize_pr(pr, now)

    assert category == "stale"


def test_categorize_pr_draft(mock_prs):
    """Test PR categorization: draft."""
    pr = mock_prs[4]  # Draft PR
    now = datetime.now(timezone.utc)

    category = pr_monitoring.categorize_pr(pr, now)

    assert category == "draft"


def test_categorize_pr_changes_requested(mock_prs):
    """Test PR categorization: changes requested."""
    pr = mock_prs[5]  # Changes requested PR
    now = datetime.now(timezone.utc)

    category = pr_monitoring.categorize_pr(pr, now)

    assert category == "changes_requested"


def test_categorize_pr_waiting_for_review(mock_prs):
    """Test PR categorization: waiting for review."""
    pr = mock_prs[6]  # Waiting for review PR
    now = datetime.now(timezone.utc)

    category = pr_monitoring.categorize_pr(pr, now)

    assert category == "waiting_for_review"


def test_categorize_prs(mock_prs):
    """Test categorizing all PRs."""
    now = datetime.now(timezone.utc)

    categorized = pr_monitoring.categorize_prs(mock_prs, now)

    assert len(categorized["ready_to_merge"]) == 1
    assert len(categorized["failing_checks"]) == 1
    assert len(categorized["merge_conflicts"]) == 1
    assert len(categorized["stale"]) == 1
    assert len(categorized["draft"]) == 1
    assert len(categorized["changes_requested"]) == 1
    assert len(categorized["waiting_for_review"]) == 1


def test_detect_issues_failing_checks_too_long(mock_prs):
    """Test issue detection: failing checks for >24 hours."""
    now = datetime.now(timezone.utc)
    categorized = pr_monitoring.categorize_prs(mock_prs, now)

    issues = pr_monitoring.detect_issues(categorized, now)

    # Should detect failing checks for >24 hours (PR #2)
    critical_issues = [i for i in issues if i["severity"] == "CRITICAL"]
    assert len(critical_issues) >= 1
    assert any(i["pr_number"] == 2 for i in critical_issues)


def test_detect_issues_changes_requested_no_response(mock_prs):
    """Test issue detection: changes requested for >5 days."""
    now = datetime.now(timezone.utc)
    categorized = pr_monitoring.categorize_prs(mock_prs, now)

    issues = pr_monitoring.detect_issues(categorized, now)

    # Should detect changes requested for >5 days (PR #6)
    high_issues = [i for i in issues if i["severity"] == "HIGH"]
    assert any(i["pr_number"] == 6 for i in high_issues)


def test_detect_issues_waiting_for_review_too_long(mock_prs):
    """Test issue detection: waiting for review for >3 days."""
    now = datetime.now(timezone.utc)
    categorized = pr_monitoring.categorize_prs(mock_prs, now)

    issues = pr_monitoring.detect_issues(categorized, now)

    # Should detect waiting for review for >3 days (PR #7)
    high_issues = [i for i in issues if i["severity"] == "HIGH"]
    assert any(i["pr_number"] == 7 for i in high_issues)


def test_detect_issues_stale(mock_prs):
    """Test issue detection: stale PRs."""
    now = datetime.now(timezone.utc)
    categorized = pr_monitoring.categorize_prs(mock_prs, now)

    issues = pr_monitoring.detect_issues(categorized, now)

    # Should detect stale PR (PR #4)
    medium_issues = [i for i in issues if i["severity"] == "MEDIUM"]
    assert any(i["pr_number"] == 4 for i in medium_issues)


def test_calculate_pr_health_score_perfect():
    """Test PR health score calculation: perfect score."""
    categorized_prs = {
        "ready_to_merge": [{"number": 1}, {"number": 2}],
        "waiting_for_review": [],
        "changes_requested": [],
        "failing_checks": [],
        "merge_conflicts": [],
        "stale": [],
        "draft": [],
    }
    issues = []

    score = pr_monitoring.calculate_pr_health_score(categorized_prs, issues)

    assert score == 100


def test_calculate_pr_health_score_failing_checks():
    """Test PR health score calculation: with failing checks."""
    categorized_prs = {
        "ready_to_merge": [],
        "waiting_for_review": [],
        "changes_requested": [],
        "failing_checks": [{"number": 1}],
        "merge_conflicts": [],
        "stale": [],
        "draft": [],
    }
    issues = [{"severity": "CRITICAL", "pr_number": 1}]

    score = pr_monitoring.calculate_pr_health_score(categorized_prs, issues)

    assert score < 100
    # Failing checks penalty (-30) + critical issue penalty (-15) = -45
    assert score <= 55


def test_calculate_pr_health_score_no_prs():
    """Test PR health score calculation: no PRs."""
    categorized_prs = {
        "ready_to_merge": [],
        "waiting_for_review": [],
        "changes_requested": [],
        "failing_checks": [],
        "merge_conflicts": [],
        "stale": [],
        "draft": [],
    }
    issues = []

    score = pr_monitoring.calculate_pr_health_score(categorized_prs, issues)

    assert score == 100


def test_generate_recommendations(mock_prs):
    """Test recommendation generation."""
    now = datetime.now(timezone.utc)
    categorized = pr_monitoring.categorize_prs(mock_prs, now)
    issues = pr_monitoring.detect_issues(categorized, now)

    recommendations = pr_monitoring.generate_recommendations(categorized, issues)

    # Should have recommendations for ready_to_merge, failing_checks, etc.
    assert len(recommendations) > 0

    # Check priorities are set correctly
    critical_recs = [r for r in recommendations if r["priority"] == "CRITICAL"]
    high_recs = [r for r in recommendations if r["priority"] == "HIGH"]

    assert len(critical_recs) > 0  # Failing checks
    assert len(high_recs) > 0  # Ready to merge


def test_generate_recommendations_sorted_by_priority(mock_prs):
    """Test recommendations are sorted by priority."""
    now = datetime.now(timezone.utc)
    categorized = pr_monitoring.categorize_prs(mock_prs, now)
    issues = pr_monitoring.detect_issues(categorized, now)

    recommendations = pr_monitoring.generate_recommendations(categorized, issues)

    # Verify sorted by priority (CRITICAL first, then HIGH, MEDIUM, LOW)
    priorities = [r["priority"] for r in recommendations]
    expected_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    for i in range(len(priorities) - 1):
        assert expected_order[priorities[i]] <= expected_order[priorities[i + 1]]


@patch("subprocess.run")
def test_fetch_open_prs_success(mock_run):
    """Test fetching open PRs successfully."""
    now = datetime.now(timezone.utc)

    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps(
            [
                {
                    "number": 1,
                    "title": "Test PR",
                    "author": {"login": "test_user"},
                    "createdAt": now.isoformat(),
                    "updatedAt": now.isoformat(),
                    "isDraft": False,
                    "labels": [],
                    "reviews": [],
                    "statusCheckRollup": [],
                    "mergeable": "MERGEABLE",
                }
            ]
        ),
    )

    prs = pr_monitoring.fetch_open_prs()

    assert len(prs) == 1
    assert prs[0]["number"] == 1
    assert prs[0]["title"] == "Test PR"
    assert prs[0]["author"] == "test_user"


@patch("subprocess.run")
def test_fetch_open_prs_failure(mock_run):
    """Test fetching open PRs failure handling."""
    mock_run.return_value = MagicMock(returncode=1, stderr="Error")

    prs = pr_monitoring.fetch_open_prs()

    assert prs == []


@patch("subprocess.run")
def test_get_repo_name_success(mock_run):
    """Test getting repository name successfully."""
    mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "owner/repo"}))

    repo_name = pr_monitoring.get_repo_name()

    assert repo_name == "owner/repo"


@patch("subprocess.run")
def test_get_repo_name_failure(mock_run):
    """Test getting repository name failure handling."""
    mock_run.return_value = MagicMock(returncode=1)

    repo_name = pr_monitoring.get_repo_name()

    assert repo_name == "unknown"


def test_send_notification(capsys):
    """Test sending notification for critical issues."""
    critical_issues = [
        {"pr_number": 1, "description": "Failing checks for 48 hours"},
        {"pr_number": 2, "description": "Merge conflicts for 5 days"},
    ]

    pr_monitoring.send_notification(critical_issues)

    captured = capsys.readouterr()
    assert "CRITICAL ALERT" in captured.out
    assert "2 critical PR issues" in captured.out
    assert "PR #1" in captured.out
    assert "PR #2" in captured.out


@patch("subprocess.run")
@patch("pathlib.Path.write_text")
def test_main_integration(mock_write_text, mock_run, mock_prs):
    """Test main function integration."""
    now = datetime.now(timezone.utc)

    # Mock gh CLI responses
    mock_run.side_effect = [
        # get_repo_name()
        MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "test/repo"})),
        # fetch_open_prs()
        MagicMock(
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "number": pr["number"],
                        "title": pr["title"],
                        "author": {"login": pr["author"]},
                        "createdAt": pr["created_at"].isoformat(),
                        "updatedAt": pr["updated_at"].isoformat(),
                        "isDraft": pr["is_draft"],
                        "labels": [{"name": label} for label in pr["labels"]],
                        "reviews": pr["reviews"],
                        "statusCheckRollup": pr["status_checks"],
                        "mergeable": pr["mergeable"],
                    }
                    for pr in mock_prs
                ]
            ),
        ),
    ]

    context = {"repo_name": "test/repo", "current_date": now.isoformat(), "generate_report": True}

    result = pr_monitoring.main(context)

    # Verify result structure
    assert "pr_health_score" in result
    assert "categorized_prs" in result
    assert "issues" in result
    assert "recommendations" in result
    assert "report_path" in result

    # Verify health score is calculated
    assert 0 <= result["pr_health_score"] <= 100

    # Verify categorized PRs counts
    assert result["categorized_prs"]["ready_to_merge"] == 1
    assert result["categorized_prs"]["failing_checks"] == 1

    # Verify issues detected
    assert len(result["issues"]) > 0

    # Verify recommendations generated
    assert len(result["recommendations"]) > 0

    # Verify report was written
    assert mock_write_text.called


def test_main_without_report():
    """Test main function without generating report."""
    context = {"generate_report": False}

    with patch("subprocess.run") as mock_run:
        # Mock empty PR list
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "test/repo"})),
            MagicMock(returncode=0, stdout=json.dumps([])),
        ]

        result = pr_monitoring.main(context)

        assert result["report_path"] is None
        assert result["pr_health_score"] == 100  # No PRs = perfect health
