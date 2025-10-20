"""
Unit tests for roadmap-health skill.

Tests all core functionality: parsing, health scoring, velocity calculation,
blocker detection, and dependency analysis.

Author: code_developer (implementing US-070)
Date: 2025-10-19
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import functions directly by loading the module
import importlib.util
import sys

# Load roadmap_health module from .claude/skills
skill_path = (
    Path(__file__).parent.parent.parent.parent / ".claude/skills/project-manager/roadmap-health/roadmap_health.py"
)
spec = importlib.util.spec_from_file_location("roadmap_health", skill_path)
rh = importlib.util.module_from_spec(spec)
sys.modules["roadmap_health"] = rh
spec.loader.exec_module(rh)


class TestParseRoadmap:
    """Test ROADMAP parsing functionality."""

    def test_parse_roadmap_empty_file(self, tmp_path: Path):
        """Test parsing empty ROADMAP file."""
        roadmap_file = tmp_path / "ROADMAP.md"
        roadmap_file.write_text("")

        with patch("roadmap_health.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_text.return_value = ""

            priorities = rh.parse_roadmap()
            assert priorities == []

    def test_parse_roadmap_with_priorities(self):
        """Test parsing ROADMAP with various priority formats."""
        content = """
### PRIORITY 1: First Task 📝
Some content

### PRIORITY 2: Second Task 🔄
More content

### PRIORITY 3: Third Task ✅
Done
"""
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = content

        with patch("roadmap_health.Path", return_value=mock_path_instance):
            priorities = rh.parse_roadmap()

            # Parser only matches "PRIORITY X:" format with number, not "US-XXX"
            assert len(priorities) == 3
            assert priorities[0]["number"] == "1"
            assert priorities[0]["title"] == "First Task"
            assert priorities[0]["status"] == "Planned"
            assert priorities[1]["status"] == "In Progress"
            assert priorities[2]["status"] == "Complete"


class TestCalculateVelocity:
    """Test velocity calculation from git history."""

    def test_calculate_velocity_success(self):
        """Test velocity calculation with successful git log."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """abc123 feat: Implement US-001
def456 feat: Implement US-002
ghi789 fix: Update PRIORITY 3
jkl012 feat: Complete US-004
mno345 docs: Update README
pqr678 feat: Implement US-005
"""

        with patch("roadmap_health.subprocess.run", return_value=mock_result):
            velocity = rh.calculate_velocity()

            # Should find 4 unique priorities (US-001, US-002, US-004, US-005)
            # Note: "fix: Update PRIORITY 3" doesn't match because "fix:" is not in the trigger words
            # Over 4 weeks = 4/4 = 1.0
            assert velocity == 1.0

    def test_calculate_velocity_git_failure(self):
        """Test velocity calculation when git command fails."""
        mock_result = Mock()
        mock_result.returncode = 1

        with patch("roadmap_health.subprocess.run", return_value=mock_result):
            velocity = rh.calculate_velocity()
            assert velocity == 0.0

    def test_calculate_velocity_no_priorities(self):
        """Test velocity calculation with commits but no priority completions."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """abc123 fix: Random bug fix
def456 docs: Update documentation
ghi789 refactor: Clean up code
"""

        with patch("roadmap_health.subprocess.run", return_value=mock_result):
            velocity = rh.calculate_velocity()
            assert velocity == 0.0


class TestCalculateHealthScore:
    """Test health score calculation (0-100)."""

    def test_perfect_health_score(self):
        """Test calculation with perfect health."""
        priorities = [{"status": "Complete"} for _ in range(10)]
        blockers = []
        github_status = {"failed_ci": 0, "open_prs": 3}
        trends = {"completion_rate": 100.0, "velocity": 1.0}

        score = rh.calculate_health_score(priorities, blockers, github_status, trends)

        # Perfect score components:
        # Completion: 30 (100% * 0.3)
        # Velocity: 20 (1.0 * 20)
        # Blockers: 25 (no blockers)
        # CI: 15 (no failures)
        # PR: 10 (<5 PRs)
        # Total: 100
        assert score == 100

    def test_poor_health_score(self):
        """Test calculation with poor health."""
        priorities = [{"status": "Planned"} for _ in range(10)]
        blockers = [
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
        ]
        github_status = {"failed_ci": 10, "open_prs": 20}
        trends = {"completion_rate": 0.0, "velocity": 0.1}

        score = rh.calculate_health_score(priorities, blockers, github_status, trends)

        # Poor score components:
        # Completion: 0 (0% complete)
        # Velocity: 2 (0.1 * 20)
        # Blockers: 12 (25 - 2*5 - 1*3)
        # CI: 5 (max(0, 15 - 10))
        # PR: 0 (>10 PRs)
        # Total: 19
        assert score == 19

    def test_health_score_boundaries(self):
        """Test health score stays within 0-100 bounds."""
        # Test minimum bound
        priorities = []
        blockers = [{"severity": "CRITICAL"} for _ in range(10)]  # Many blockers
        github_status = {"failed_ci": 20, "open_prs": 50}
        trends = {"completion_rate": 0.0, "velocity": 0.0}

        score = rh.calculate_health_score(priorities, blockers, github_status, trends)
        assert 0 <= score <= 100

        # Test maximum bound (can't exceed 100)
        priorities = [{"status": "Complete"} for _ in range(100)]
        blockers = []
        github_status = {"failed_ci": 0, "open_prs": 0}
        trends = {"completion_rate": 100.0, "velocity": 5.0}  # Very high velocity

        score = rh.calculate_health_score(priorities, blockers, github_status, trends)
        assert score == 100


class TestDetectDependencyBlockers:
    """Test dependency blocker detection."""

    def test_detect_dependency_blockers_simple(self):
        """Test detecting simple dependency blocker."""
        priorities = [
            {"number": "1", "title": "Task 1", "status": "In Progress"},
            {"number": "2", "title": "Task 2", "status": "Planned"},
        ]

        roadmap_content = """
### PRIORITY 1: Task 1 🔄
**Blocked By**: US-2

### PRIORITY 2: Task 2 📝
"""

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = roadmap_content

        with patch("roadmap_health.Path", return_value=mock_path_instance):
            blockers = rh.detect_dependency_blockers(priorities)

            assert len(blockers) == 1
            assert "PRIORITY 1" in blockers[0]["priority"]
            assert "Blocked by PRIORITY 2" in blockers[0]["blocker"]
            assert blockers[0]["severity"] == "HIGH"

    def test_detect_dependency_blockers_complete_dependency(self):
        """Test no blocker when dependency is complete."""
        priorities = [
            {"number": "1", "title": "Task 1", "status": "In Progress"},
            {"number": "2", "title": "Task 2", "status": "Complete"},
        ]

        roadmap_content = """
### PRIORITY 1: Task 1 🔄
**Blocked By**: US-2

### PRIORITY 2: Task 2 ✅
"""

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = roadmap_content

        with patch("roadmap_health.Path", return_value=mock_path_instance):
            blockers = rh.detect_dependency_blockers(priorities)

            # No blocker because dependency is complete
            assert len(blockers) == 0

    def test_detect_dependency_blockers_multiple_dependencies(self):
        """Test detecting multiple dependency blockers."""
        priorities = [
            {"number": "1", "title": "Task 1", "status": "Planned"},
            {"number": "2", "title": "Task 2", "status": "Planned"},
            {"number": "3", "title": "Task 3", "status": "Planned"},
        ]

        roadmap_content = """
### PRIORITY 1: Task 1 📝
**Dependencies**: US-2, PRIORITY 3

### PRIORITY 2: Task 2 📝

### PRIORITY 3: Task 3 📝
"""

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = roadmap_content

        with patch("roadmap_health.Path", return_value=mock_path_instance):
            blockers = rh.detect_dependency_blockers(priorities)

            # Should detect 2 blockers (both US-2 and PRIORITY 3 incomplete)
            assert len(blockers) == 2


class TestIdentifyBlockers:
    """Test overall blocker identification."""

    def test_identify_blockers_all_types(self):
        """Test identifying all types of blockers."""
        priorities = [
            {"number": "1", "status": "Blocked", "title": "Task 1"},
            {"number": "2", "status": "In Progress", "title": "Task 2"},
            {"number": "3", "status": "In Progress", "title": "Task 3"},
            {"number": "4", "status": "In Progress", "title": "Task 4"},
            {"number": "5", "status": "In Progress", "title": "Task 5"},
        ]

        github_status = {"failed_ci": 5, "open_prs": 10}

        with patch("roadmap_health.detect_dependency_blockers", return_value=[]):
            blockers = rh.identify_blockers(priorities, github_status)

            # Should have:
            # 1. Explicitly blocked priority
            # 2. Multiple in-progress (4 > 3)
            # 3. Failed CI
            # 4. Stale PRs (10 > 5)
            assert len(blockers) >= 4


class TestDetermineHealth:
    """Test health status determination."""

    def test_determine_health_critical(self):
        """Test CRITICAL health status."""
        blockers = [{"severity": "CRITICAL"}]
        github_status = {"failed_ci": 0}

        health = rh.determine_health(blockers, github_status)
        assert health == "CRITICAL"

    def test_determine_health_critical_ci_failures(self):
        """Test CRITICAL from too many CI failures."""
        blockers = []
        github_status = {"failed_ci": 5}

        health = rh.determine_health(blockers, github_status)
        assert health == "CRITICAL"

    def test_determine_health_warning(self):
        """Test WARNING health status."""
        blockers = [{"severity": "HIGH"}]
        github_status = {"failed_ci": 1}

        health = rh.determine_health(blockers, github_status)
        assert health == "WARNING"

    def test_determine_health_healthy(self):
        """Test HEALTHY status."""
        blockers = []
        github_status = {"failed_ci": 0}

        health = rh.determine_health(blockers, github_status)
        assert health == "HEALTHY"


class TestMainFunction:
    """Test main execution function."""

    def test_main_integration(self):
        """Test main function integration."""
        context = {"generate_report": False}  # Don't generate report for speed

        # Mock all external dependencies
        with (
            patch("roadmap_health.parse_roadmap") as mock_parse,
            patch("roadmap_health.check_github_status") as mock_github,
            patch("roadmap_health.identify_blockers") as mock_blockers,
            patch("roadmap_health.analyze_trends") as mock_trends,
            patch("roadmap_health.calculate_health_score") as mock_score,
            patch("roadmap_health.determine_health") as mock_health,
        ):
            # Setup mocks
            mock_parse.return_value = [{"number": "1", "status": "Complete"}]
            mock_github.return_value = {"open_prs": 2, "failed_ci": 0}
            mock_blockers.return_value = []
            mock_trends.return_value = {"completion_rate": 100.0, "velocity": 1.0}
            mock_score.return_value = 95
            mock_health.return_value = "HEALTHY"

            # Execute
            result = rh.main(context)

            # Verify
            assert result["health_status"] == "HEALTHY"
            assert result["health_score"] == 95
            assert result["velocity"] == 1.0
            assert result["blockers"] == []
            assert result["report_path"] is None  # Because generate_report=False


class TestAnalyzeTrends:
    """Test trend analysis."""

    def test_analyze_trends_with_velocity(self):
        """Test trends include velocity calculation."""
        priorities = [
            {"status": "Complete"},
            {"status": "Complete"},
            {"status": "Planned"},
        ]

        with patch("roadmap_health.calculate_velocity", return_value=1.5):
            trends = rh.analyze_trends(priorities)

            assert trends["completion_rate"] == pytest.approx(66.67, rel=0.01)
            assert trends["velocity"] == 1.5  # Should use mocked value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
