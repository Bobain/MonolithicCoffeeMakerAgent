"""
Integration tests for PR Monitoring skill.

Tests the skill with realistic GitHub data scenarios.

Author: code_developer
Date: 2025-10-19
Related: US-071
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Import pr-monitoring module
import importlib.util

spec = importlib.util.spec_from_file_location(
    "pr_monitoring", Path(".claude/skills/project-manager/pr-monitoring/pr_monitoring.py")
)
pr_monitoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr_monitoring)


@pytest.fixture
def realistic_prs():
    """Realistic PR data mimicking actual GitHub repository."""
    now = datetime.now(timezone.utc)

    return [
        # Scenario 1: Multiple PRs ready to merge (good health)
        {
            "number": 101,
            "title": "feat: Implement US-070 - roadmap-health-check Skill",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(days=1)).isoformat(),
            "updatedAt": (now - timedelta(hours=2)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "feature"}, {"name": "priority-high"}],
            "reviews": [{"state": "APPROVED", "author": {"login": "architect"}}],
            "statusCheckRollup": [
                {"state": "SUCCESS", "context": "ci/tests"},
                {"state": "SUCCESS", "context": "ci/lint"},
            ],
            "mergeable": "MERGEABLE",
        },
        {
            "number": 102,
            "title": "feat: Implement git-workflow-automation skill",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(hours=18)).isoformat(),
            "updatedAt": (now - timedelta(hours=1)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "feature"}],
            "reviews": [{"state": "APPROVED", "author": {"login": "architect"}}],
            "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
        # Scenario 2: PR with failing tests (critical)
        {
            "number": 103,
            "title": "fix: Database connection pool leak",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(days=2)).isoformat(),
            "updatedAt": (now - timedelta(days=1, hours=12)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "bug"}, {"name": "critical"}],
            "reviews": [],
            "statusCheckRollup": [
                {"state": "FAILURE", "context": "ci/tests", "conclusion": "FAILURE"},
                {"state": "SUCCESS", "context": "ci/lint"},
            ],
            "mergeable": "MERGEABLE",
        },
        # Scenario 3: PR waiting for review (4 days old)
        {
            "number": 104,
            "title": "feat: Add user notifications system",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(days=4)).isoformat(),
            "updatedAt": (now - timedelta(days=4)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "feature"}],
            "reviews": [],
            "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
        # Scenario 4: PR with merge conflicts (5 days old)
        {
            "number": 105,
            "title": "refactor: Reorganize project structure",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(days=5)).isoformat(),
            "updatedAt": (now - timedelta(days=4)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "refactor"}],
            "reviews": [],
            "statusCheckRollup": [],
            "mergeable": "CONFLICTING",
        },
        # Scenario 5: Stale PR (12 days old, no activity)
        {
            "number": 106,
            "title": "experimental: New caching mechanism",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(days=12)).isoformat(),
            "updatedAt": (now - timedelta(days=10)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "experimental"}],
            "reviews": [{"state": "COMMENT", "author": {"login": "reviewer1"}}],
            "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
        # Scenario 6: Draft PR (work in progress)
        {
            "number": 107,
            "title": "[WIP] Recipe sharing feature",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(hours=8)).isoformat(),
            "updatedAt": (now - timedelta(hours=2)).isoformat(),
            "isDraft": True,
            "labels": [{"name": "wip"}],
            "reviews": [],
            "statusCheckRollup": [],
            "mergeable": "MERGEABLE",
        },
        # Scenario 7: PR with changes requested (6 days ago)
        {
            "number": 108,
            "title": "feat: Analytics dashboard",
            "author": {"login": "code_developer"},
            "createdAt": (now - timedelta(days=7)).isoformat(),
            "updatedAt": (now - timedelta(days=6)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "feature"}],
            "reviews": [{"state": "CHANGES_REQUESTED", "author": {"login": "architect"}}],
            "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
    ]


@patch("subprocess.run")
@patch("pathlib.Path.write_text")
def test_full_pr_analysis_workflow(mock_write_text, mock_run, realistic_prs):
    """Test complete PR analysis workflow with realistic data."""
    now = datetime.now(timezone.utc)

    # Mock gh CLI responses
    mock_run.side_effect = [
        # get_repo_name()
        MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "user/MonolithicCoffeeMakerAgent"})),
        # fetch_open_prs()
        MagicMock(returncode=0, stdout=json.dumps(realistic_prs)),
    ]

    context = {"repo_name": "user/MonolithicCoffeeMakerAgent", "current_date": now.isoformat(), "generate_report": True}

    result = pr_monitoring.main(context)

    # Verify categorization
    assert result["categorized_prs"]["ready_to_merge"] == 2  # PRs 101, 102
    assert result["categorized_prs"]["failing_checks"] == 1  # PR 103
    assert result["categorized_prs"]["waiting_for_review"] == 1  # PR 104
    assert result["categorized_prs"]["merge_conflicts"] == 1  # PR 105
    assert result["categorized_prs"]["stale"] == 1  # PR 106
    assert result["categorized_prs"]["draft"] == 1  # PR 107
    assert result["categorized_prs"]["changes_requested"] == 1  # PR 108

    # Verify issues detected
    assert len(result["issues"]) >= 5  # Critical, high, medium issues

    # Verify critical issue for failing checks
    critical_issues = [i for i in result["issues"] if i["severity"] == "CRITICAL"]
    assert len(critical_issues) >= 1
    assert any(i["pr_number"] == 103 for i in critical_issues)

    # Verify high issues (waiting for review, changes requested, merge conflicts)
    high_issues = [i for i in result["issues"] if i["severity"] == "HIGH"]
    assert len(high_issues) >= 3

    # Verify medium issues (stale PR)
    medium_issues = [i for i in result["issues"] if i["severity"] == "MEDIUM"]
    assert len(medium_issues) >= 1

    # Verify health score reflects issues
    # With 2 ready, 1 failing, 1 conflict, 1 stale, and multiple issues:
    # Should be in "POOR" to "FAIR" range (score can be low with many issues)
    assert 0 <= result["pr_health_score"] <= 85

    # Verify recommendations
    assert len(result["recommendations"]) >= 4

    # Should recommend merging ready PRs
    merge_rec = next((r for r in result["recommendations"] if "Merge ready PRs" in r["action"]), None)
    assert merge_rec is not None
    assert merge_rec["priority"] == "HIGH"

    # Should recommend fixing failing checks
    failing_rec = next((r for r in result["recommendations"] if "failing CI checks" in r["action"]), None)
    assert failing_rec is not None
    assert failing_rec["priority"] == "CRITICAL"

    # Verify report was generated
    assert result["report_path"] is not None
    assert mock_write_text.called


@patch("subprocess.run")
@patch("pathlib.Path.write_text")
def test_healthy_repository_scenario(mock_write_text, mock_run):
    """Test scenario with healthy repository (all PRs ready or in review)."""
    now = datetime.now(timezone.utc)

    healthy_prs = [
        # All PRs ready to merge or in review (recent)
        {
            "number": 201,
            "title": "feat: Feature A",
            "author": {"login": "dev1"},
            "createdAt": (now - timedelta(hours=12)).isoformat(),
            "updatedAt": (now - timedelta(hours=1)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "feature"}],
            "reviews": [{"state": "APPROVED", "author": {"login": "reviewer"}}],
            "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
        {
            "number": 202,
            "title": "feat: Feature B",
            "author": {"login": "dev2"},
            "createdAt": (now - timedelta(hours=6)).isoformat(),
            "updatedAt": (now - timedelta(hours=2)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "feature"}],
            "reviews": [],
            "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}],
            "mergeable": "MERGEABLE",
        },
    ]

    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "user/healthy-repo"})),
        MagicMock(returncode=0, stdout=json.dumps(healthy_prs)),
    ]

    context = {"generate_report": True}

    result = pr_monitoring.main(context)

    # Verify high health score
    assert result["pr_health_score"] >= 90  # Should be "EXCELLENT"

    # Verify minimal issues
    assert len(result["issues"]) == 0  # No issues in healthy repo

    # Verify primary recommendation is to merge ready PRs
    assert len(result["recommendations"]) >= 1
    assert result["recommendations"][0]["priority"] in ["HIGH", "MEDIUM"]


@patch("subprocess.run")
@patch("pathlib.Path.write_text")
def test_critical_repository_scenario(mock_write_text, mock_run):
    """Test scenario with critical repository health (many failing PRs)."""
    now = datetime.now(timezone.utc)

    critical_prs = [
        # Multiple PRs with critical issues
        {
            "number": 301,
            "title": "fix: Critical bug",
            "author": {"login": "dev1"},
            "createdAt": (now - timedelta(days=3)).isoformat(),
            "updatedAt": (now - timedelta(days=2)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "bug"}],
            "reviews": [],
            "statusCheckRollup": [{"state": "FAILURE", "context": "ci/tests", "conclusion": "FAILURE"}],
            "mergeable": "MERGEABLE",
        },
        {
            "number": 302,
            "title": "fix: Another critical bug",
            "author": {"login": "dev2"},
            "createdAt": (now - timedelta(days=2)).isoformat(),
            "updatedAt": (now - timedelta(days=1, hours=12)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "bug"}],
            "reviews": [],
            "statusCheckRollup": [{"state": "FAILURE", "context": "ci/tests", "conclusion": "FAILURE"}],
            "mergeable": "CONFLICTING",
        },
        {
            "number": 303,
            "title": "refactor: Major refactor",
            "author": {"login": "dev3"},
            "createdAt": (now - timedelta(days=8)).isoformat(),
            "updatedAt": (now - timedelta(days=7)).isoformat(),
            "isDraft": False,
            "labels": [{"name": "refactor"}],
            "reviews": [{"state": "CHANGES_REQUESTED", "author": {"login": "reviewer"}}],
            "statusCheckRollup": [],
            "mergeable": "CONFLICTING",
        },
    ]

    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "user/critical-repo"})),
        MagicMock(returncode=0, stdout=json.dumps(critical_prs)),
    ]

    context = {"generate_report": True}

    result = pr_monitoring.main(context)

    # Verify low health score
    assert result["pr_health_score"] <= 50  # Should be "POOR" or "FAIR"

    # Verify multiple critical/high issues
    critical_issues = [i for i in result["issues"] if i["severity"] == "CRITICAL"]
    high_issues = [i for i in result["issues"] if i["severity"] == "HIGH"]
    # Should have at least 2 critical/high issues (failing checks, merge conflicts)
    assert len(critical_issues) + len(high_issues) >= 2

    # Verify critical recommendations
    assert any(r["priority"] == "CRITICAL" for r in result["recommendations"])


@patch("subprocess.run")
def test_github_cli_unavailable(mock_run):
    """Test graceful handling when GitHub CLI is unavailable."""
    # Simulate gh command failure
    mock_run.return_value = MagicMock(returncode=127, stderr="gh: command not found")

    prs = pr_monitoring.fetch_open_prs()

    # Should return empty list, not crash
    assert prs == []


@patch("subprocess.run")
@patch("pathlib.Path.write_text")
def test_empty_repository(mock_write_text, mock_run):
    """Test scenario with no open PRs."""
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "user/empty-repo"})),
        MagicMock(returncode=0, stdout=json.dumps([])),  # No PRs
    ]

    context = {"generate_report": True}

    result = pr_monitoring.main(context)

    # Verify perfect health score (no PRs = healthy)
    assert result["pr_health_score"] == 100

    # Verify no issues
    assert len(result["issues"]) == 0

    # Verify no recommendations (or minimal)
    assert len(result["recommendations"]) <= 1


@patch("subprocess.run")
@patch("pathlib.Path.write_text")
def test_report_generation(mock_write_text, mock_run, realistic_prs):
    """Test report generation contains all expected sections."""
    datetime.now(timezone.utc)

    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "user/test-repo"})),
        MagicMock(returncode=0, stdout=json.dumps(realistic_prs)),
    ]

    context = {"generate_report": True}

    result = pr_monitoring.main(context)

    # Verify write_text was called
    assert mock_write_text.called

    # Get the report content
    report_content = mock_write_text.call_args[0][0]

    # Verify report contains key sections
    assert "# Pull Request Monitoring & Analysis Report" in report_content
    assert "## Executive Summary" in report_content
    assert "## PRs by Category" in report_content
    assert "## Issues Found" in report_content
    assert "## Recommendations" in report_content

    # Verify report contains health score
    assert f"{result['pr_health_score']}/100" in report_content

    # Verify report contains PR counts
    assert "Ready to Merge" in report_content
    assert "Waiting for Review" in report_content

    # Verify report contains specific PRs
    assert "PR #101" in report_content or "PR #102" in report_content


@patch("subprocess.run")
def test_performance_large_pr_set(mock_run):
    """Test performance with large number of PRs."""
    import time

    now = datetime.now(timezone.utc)

    # Generate 50 PRs
    large_pr_set = []
    for i in range(1, 51):
        large_pr_set.append(
            {
                "number": i,
                "title": f"PR {i}",
                "author": {"login": f"dev{i % 5}"},
                "createdAt": (now - timedelta(days=i % 10)).isoformat(),
                "updatedAt": (now - timedelta(days=i % 5)).isoformat(),
                "isDraft": i % 10 == 0,  # 10% draft
                "labels": [{"name": "feature"}],
                "reviews": [{"state": "APPROVED", "author": {"login": "reviewer"}}] if i % 3 == 0 else [],
                "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}] if i % 4 != 0 else [],
                "mergeable": "CONFLICTING" if i % 7 == 0 else "MERGEABLE",
            }
        )

    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "user/large-repo"})),
        MagicMock(returncode=0, stdout=json.dumps(large_pr_set)),
    ]

    context = {"generate_report": False}  # Skip report generation for speed

    start = time.time()
    result = pr_monitoring.main(context)
    elapsed = time.time() - start

    # Should complete in <1 second (requirement from US-071)
    assert elapsed < 1.0

    # Verify all PRs were processed
    total_categorized = sum(result["categorized_prs"].values())
    assert total_categorized == 50


def test_prioritization_logic():
    """Test that critical issues are prioritized correctly."""
    now = datetime.now(timezone.utc)

    categorized_prs = {
        "ready_to_merge": [],
        "waiting_for_review": [
            {"number": 1, "created_at": now - timedelta(days=5), "updated_at": now - timedelta(days=5)}
        ],
        "changes_requested": [],
        "failing_checks": [{"number": 2, "updated_at": now - timedelta(days=2)}],
        "merge_conflicts": [],
        "stale": [],
        "draft": [],
    }

    issues = pr_monitoring.detect_issues(categorized_prs, now)

    # Critical issues should come first in sorting
    critical_issues = [i for i in issues if i["severity"] == "CRITICAL"]
    high_issues = [i for i in issues if i["severity"] == "HIGH"]

    # Should have at least one critical (failing checks >24h)
    assert len(critical_issues) >= 1

    # Should have at least one high (waiting for review >3 days)
    assert len(high_issues) >= 1
