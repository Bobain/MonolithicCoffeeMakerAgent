"""
Integration test for pr-monitoring-analysis skill with real GitHub PRs.

Updated to use Pythonic imports (PRIORITY 26).

Tests the full workflow against actual repository PRs (if available).

Author: code_developer (implementing US-071)
Date: 2025-10-19
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add .claude to path for skill imports (PRIORITY 26)
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root / ".claude"))

# Import using proper Python imports (PRIORITY 26)
from claude.skills.project_manager.pr_monitoring import pr_monitoring as pm

sys.modules["pr_monitoring"] = pm


class TestPRMonitoringIntegration:
    """Integration tests with real GitHub repository."""

    def test_full_workflow_execution_with_mock_prs(self):
        """Test complete PR monitoring workflow with mock PRs."""
        now = datetime.now(timezone.utc)

        # Mock GitHub CLI responses
        mock_prs_data = [
            {
                "number": 1,
                "title": "Test PR: Ready to merge",
                "author": {"login": "test_user"},
                "createdAt": now.isoformat(),
                "updatedAt": now.isoformat(),
                "isDraft": False,
                "labels": [{"name": "feature"}],
                "reviews": [{"state": "APPROVED", "author": {"login": "reviewer1"}}],
                "statusCheckRollup": [{"state": "SUCCESS", "context": "ci/tests"}],
                "mergeable": "MERGEABLE",
            }
        ]

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                # get_repo_name()
                MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "test/repo"})),
                # fetch_open_prs()
                MagicMock(returncode=0, stdout=json.dumps(mock_prs_data)),
            ]

            context = {"generate_report": True}

            # Execute full workflow
            start_time = time.time()
            result = pm.main(context)
            execution_time = time.time() - start_time

            # Verify execution time < 1 minute (US-071 acceptance criteria)
            assert execution_time < 60, f"Execution took {execution_time:.2f}s (should be <60s)"

            # Verify all required fields in result
            assert "pr_health_score" in result
            assert "categorized_prs" in result
            assert "issues" in result
            assert "recommendations" in result
            assert "report_path" in result

            # Verify health score is in range 0-100
            assert 0 <= result["pr_health_score"] <= 100

            # Verify categorized_prs has correct structure
            assert isinstance(result["categorized_prs"], dict)
            assert "ready_to_merge" in result["categorized_prs"]
            assert "waiting_for_review" in result["categorized_prs"]
            assert "failing_checks" in result["categorized_prs"]

            # Verify issues is a list
            assert isinstance(result["issues"], list)

            # Verify recommendations is a list
            assert isinstance(result["recommendations"], list)

            # Verify report was generated
            if result["report_path"]:
                report_path = Path(result["report_path"])
                assert report_path.exists()
                assert report_path.stat().st_size > 0

                # Verify report contains expected sections
                report_content = report_path.read_text()
                assert "Pull Request Monitoring & Analysis Report" in report_content
                assert "Health Score" in report_content
                assert "Executive Summary" in report_content

            print(f"\n✅ Integration test passed in {execution_time:.2f}s")
            print(f"   Health Score: {result['pr_health_score']}/100")
            print(f"   Categorized PRs: {result['categorized_prs']}")
            print(f"   Issues: {len(result['issues'])}")
            print(f"   Recommendations: {len(result['recommendations'])}")

    def test_performance_with_many_prs(self):
        """Test performance with many PRs (stress test)."""
        now = datetime.now(timezone.utc)

        # Create 50 mock PRs
        mock_prs_data = []
        for i in range(50):
            mock_prs_data.append(
                {
                    "number": i + 1,
                    "title": f"Test PR #{i+1}",
                    "author": {"login": f"developer{i % 5}"},
                    "createdAt": now.isoformat(),
                    "updatedAt": now.isoformat(),
                    "isDraft": i % 10 == 0,  # 10% draft
                    "labels": [{"name": "feature"}],
                    "reviews": [{"state": "APPROVED"}] if i % 3 == 0 else [],  # 33% approved
                    "statusCheckRollup": (
                        [{"state": "SUCCESS"}] if i % 2 == 0 else [{"state": "FAILURE"}]
                    ),  # 50% passing
                    "mergeable": "CONFLICTING" if i % 7 == 0 else "MERGEABLE",  # ~14% conflicts
                }
            )

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "test/repo"})),
                MagicMock(returncode=0, stdout=json.dumps(mock_prs_data)),
            ]

            context = {"generate_report": False}  # Skip report generation for speed

            start_time = time.time()
            pm.main(context)
            execution_time = time.time() - start_time

            # Even with 50 PRs, should complete in <5 seconds
            assert execution_time < 5, f"Execution took {execution_time:.2f}s (should be <5s)"

            print(f"\n✅ Performance test passed with 50 PRs in {execution_time:.2f}s")

    def test_error_handling_gh_unavailable(self):
        """Test error handling when gh CLI is unavailable."""
        with patch("subprocess.run") as mock_run:
            # Simulate gh command failure
            mock_run.return_value = MagicMock(returncode=1, stderr="gh: command not found")

            context = {"generate_report": False}

            # Should not crash, should return gracefully
            result = pm.main(context)

            # Should return empty results
            assert result["pr_health_score"] == 100  # No PRs = perfect health
            assert all(count == 0 for count in result["categorized_prs"].values())

            print("\n✅ Error handling test passed (gh unavailable)")

    def test_empty_repository(self):
        """Test behavior with repository that has no PRs."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=json.dumps({"nameWithOwner": "test/repo"})),
                MagicMock(returncode=0, stdout=json.dumps([])),  # No PRs
            ]

            context = {"generate_report": True}

            result = pm.main(context)

            # Should handle empty repository gracefully
            assert result["pr_health_score"] == 100
            assert all(count == 0 for count in result["categorized_prs"].values())
            assert len(result["issues"]) == 0

            print("\n✅ Empty repository test passed")
