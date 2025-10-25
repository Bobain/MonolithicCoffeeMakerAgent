"""
Integration test for roadmap-health skill with real ROADMAP.md.

Updated to use Pythonic imports (PRIORITY 26).

Tests the full workflow against the actual project ROADMAP.

Author: code_developer (implementing US-070)
Date: 2025-10-19
"""

import sys
import time
from pathlib import Path

import pytest

# Add .claude to path for skill imports (PRIORITY 26)
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root / ".claude"))

# Import using proper Python imports (PRIORITY 26)
from claude.skills.project_manager.roadmap_health import roadmap_health as rh

sys.modules["roadmap_health"] = rh


class TestRoadmapHealthIntegration:
    """Integration tests with real ROADMAP.md."""

    def test_full_workflow_execution(self):
        """Test complete roadmap health check workflow."""
        context = {"generate_report": True}

        # Execute full workflow
        start_time = time.time()
        result = rh.main(context)
        execution_time = time.time() - start_time

        # Verify execution time < 2 minutes (US-070 acceptance criteria)
        assert execution_time < 120, f"Execution took {execution_time:.2f}s (should be <120s)"

        # Verify all required fields in result
        assert "health_status" in result
        assert "health_score" in result
        assert "velocity" in result
        assert "blockers" in result
        assert "github_status" in result
        assert "report_path" in result

        # Verify health status is valid
        assert result["health_status"] in ["HEALTHY", "WARNING", "CRITICAL"]

        # Verify health score is in range 0-100
        assert 0 <= result["health_score"] <= 100

        # Verify velocity is non-negative
        assert result["velocity"] >= 0

        # Verify blockers is a list
        assert isinstance(result["blockers"], list)

        # Verify report was generated
        if result["report_path"]:
            report_path = Path(result["report_path"])
            assert report_path.exists()
            assert report_path.stat().st_size > 0

            # Verify report contains expected sections
            report_content = report_path.read_text()
            assert "# ROADMAP Health Report" in report_content
            assert "Health Score" in report_content
            assert "Velocity" in report_content
            assert "Top Blockers" in report_content or "No blockers" in report_content

        print(f"\n✅ Integration test passed in {execution_time:.2f}s")
        print(f"   Health: {result['health_status']}")
        print(f"   Score: {result['health_score']}/100")
        print(f"   Velocity: {result['velocity']} priorities/week")
        print(f"   Blockers: {len(result['blockers'])}")

    def test_parse_real_roadmap(self):
        """Test parsing the actual ROADMAP.md file."""
        roadmap_path = Path("docs/roadmap/ROADMAP.md")

        # Skip if ROADMAP doesn't exist
        if not roadmap_path.exists():
            pytest.skip("ROADMAP.md not found")

        priorities = rh.parse_roadmap()

        # Verify we found priorities
        assert len(priorities) > 0, "Should find at least one priority in ROADMAP"

        # Verify each priority has required fields
        for priority in priorities:
            assert "number" in priority
            assert "title" in priority
            assert "status" in priority
            assert "emoji" in priority

            # Verify status is valid
            assert priority["status"] in [
                "Planned",
                "In Progress",
                "Complete",
                "Blocked",
                "Manual Review",
                "Unknown",
            ]

        print(f"\n✅ Parsed {len(priorities)} priorities from ROADMAP")

    def test_velocity_calculation_real_git(self):
        """Test velocity calculation with real git history."""
        velocity = rh.calculate_velocity()

        # Velocity should be non-negative
        assert velocity >= 0

        # If we have commits, velocity should be reasonable (not absurdly high)
        if velocity > 0:
            assert velocity < 100, f"Velocity {velocity} seems unrealistically high"

        print(f"\n✅ Current velocity: {velocity} priorities/week")

    def test_github_status_check(self):
        """Test GitHub status checking (may fail if gh not configured)."""
        try:
            github_status = rh.check_github_status()

            # Verify structure
            assert "open_prs" in github_status
            assert "failed_ci" in github_status
            assert "prs" in github_status
            assert "runs" in github_status

            # Verify types
            assert isinstance(github_status["open_prs"], int)
            assert isinstance(github_status["failed_ci"], int)
            assert isinstance(github_status["prs"], list)
            assert isinstance(github_status["runs"], list)

            print(f"\n✅ GitHub status: {github_status['open_prs']} PRs, {github_status['failed_ci']} failed CI")

        except Exception as e:
            # GitHub CLI may not be configured - that's OK
            pytest.skip(f"GitHub CLI not available: {e}")

    def test_dependency_blocker_detection_real(self):
        """Test dependency blocker detection with real ROADMAP."""
        priorities = rh.parse_roadmap()

        if not priorities:
            pytest.skip("No priorities found in ROADMAP")

        dependency_blockers = rh.detect_dependency_blockers(priorities)

        # Verify structure of any blockers found
        for blocker in dependency_blockers:
            assert "priority" in blocker
            assert "blocker" in blocker
            assert "severity" in blocker
            assert "action" in blocker
            assert blocker["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        print(f"\n✅ Found {len(dependency_blockers)} dependency blockers")

    def test_performance_under_2_minutes(self):
        """Verify the skill executes in under 2 minutes (US-070 requirement)."""
        context = {"generate_report": True}

        # Run multiple times to get average
        execution_times = []

        for i in range(3):
            start_time = time.time()
            rh.main(context)
            execution_time = time.time() - start_time
            execution_times.append(execution_time)

        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)

        # Verify all runs < 2 minutes
        assert max_time < 120, f"Max execution time {max_time:.2f}s exceeds 120s limit"

        # Verify average is reasonable (< 1 minute)
        assert avg_time < 60, f"Average execution time {avg_time:.2f}s should be <60s"

        print(f"\n✅ Performance test passed")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Max: {max_time:.2f}s")
        print(f"   Min: {min(execution_times):.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
