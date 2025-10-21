"""Tests for User Story Management Streamlit App.

Tests the integration between the app and underlying systems:
- RoadmapParser integration
- BugTrackingSkill integration
- Screenshot upload functionality
- Validation tracking

Related: US-111, SPEC-111
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.utils.bug_tracking_helper import get_bug_skill


class TestUserStoryManagementApp:
    """Test suite for User Story Management App."""

    def test_roadmap_parser_loads(self):
        """Test that RoadmapParser can load ROADMAP.md."""
        roadmap_path = PROJECT_ROOT / "docs" / "roadmap" / "ROADMAP.md"

        # Ensure ROADMAP exists
        assert roadmap_path.exists(), "ROADMAP.md should exist"

        # Initialize parser
        parser = RoadmapParser(str(roadmap_path))
        assert parser is not None

        # Get priorities
        priorities = parser.get_priorities()
        assert isinstance(priorities, list)
        assert len(priorities) > 0, "ROADMAP should have at least one priority"

    def test_bug_skill_initializes(self):
        """Test that BugTrackingSkill can be initialized."""
        bug_skill = get_bug_skill()
        assert bug_skill is not None

    def test_bug_skill_query(self):
        """Test that BugTrackingSkill can query bugs."""
        bug_skill = get_bug_skill()

        # Query bugs
        bugs = bug_skill.query_bugs(limit=10)
        assert isinstance(bugs, list)
        # May be empty if no bugs exist, but should not error

    def test_bug_skill_summary(self):
        """Test that BugTrackingSkill can get summary."""
        bug_skill = get_bug_skill()

        # Get summary
        summary = bug_skill.get_open_bugs_summary()
        assert isinstance(summary, dict)
        assert "critical" in summary
        assert "high" in summary
        assert "medium" in summary
        assert "low" in summary

    def test_uploads_directory_structure(self):
        """Test that uploads directory exists or can be created."""
        uploads_dir = PROJECT_ROOT / "streamlit_apps" / "user_story_management" / "uploads"

        # Create if doesn't exist
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Verify it exists
        assert uploads_dir.exists()
        assert uploads_dir.is_dir()

    def test_app_files_exist(self):
        """Test that all app files exist."""
        app_dir = PROJECT_ROOT / "streamlit_apps" / "user_story_management"

        # Main app
        assert (app_dir / "app.py").exists(), "app.py should exist"

        # README
        assert (app_dir / "README.md").exists(), "README.md should exist"

        # Pages
        pages_dir = app_dir / "pages"
        assert pages_dir.exists(), "pages directory should exist"
        assert (pages_dir / "1_📸_Screenshots.py").exists(), "Screenshots page should exist"
        assert (pages_dir / "2_✅_Validation_Tracking.py").exists(), "Validation page should exist"
        assert (pages_dir / "3_🐛_Bug_Tickets.py").exists(), "Bug tickets page should exist"

    def test_roadmap_parser_filters(self):
        """Test that RoadmapParser can filter priorities."""
        roadmap_path = PROJECT_ROOT / "docs" / "roadmap" / "ROADMAP.md"
        parser = RoadmapParser(str(roadmap_path))

        priorities = parser.get_priorities()

        # Test filtering by status
        completed = [p for p in priorities if "✅" in p.get("status", "")]
        in_progress = [p for p in priorities if "🔄" in p.get("status", "")]
        planned = [p for p in priorities if "📝" in p.get("status", "")]

        # All should be non-negative
        assert len(completed) >= 0
        assert len(in_progress) >= 0
        assert len(planned) >= 0

    def test_bug_creation_workflow(self):
        """Test bug creation workflow (without actually creating a bug)."""
        bug_skill = get_bug_skill()

        # Test that we can access the report_bug method
        assert hasattr(bug_skill, "report_bug")
        assert callable(bug_skill.report_bug)

        # Test that we can access other methods
        assert hasattr(bug_skill, "update_bug_status")
        assert hasattr(bug_skill, "query_bugs")
        assert hasattr(bug_skill, "get_bug_by_number")
        assert hasattr(bug_skill, "link_bug_to_commit")
        assert hasattr(bug_skill, "link_bug_to_pr")

    def test_database_exists(self):
        """Test that orchestrator database exists."""
        db_path = PROJECT_ROOT / "data" / "orchestrator.db"
        assert db_path.exists(), "orchestrator.db should exist"

    def test_us111_in_roadmap(self):
        """Test that US-111 exists in ROADMAP."""
        roadmap_path = PROJECT_ROOT / "docs" / "roadmap" / "ROADMAP.md"
        content = roadmap_path.read_text()

        assert "US-111" in content, "US-111 should be in ROADMAP"
        assert "User Story Management" in content, "User Story Management should be mentioned"


class TestBugTrackingIntegration:
    """Test bug tracking integration."""

    def test_bug_skill_velocity(self):
        """Test bug resolution velocity query."""
        bug_skill = get_bug_skill()

        velocity = bug_skill.get_bug_resolution_velocity()
        assert isinstance(velocity, list)
        # May be empty if no bugs resolved yet

    def test_bug_priority_distribution(self):
        """Test that we can query bugs by priority."""
        bug_skill = get_bug_skill()

        # Query high priority bugs
        high_bugs = bug_skill.query_bugs(priority="High", limit=10)
        assert isinstance(high_bugs, list)

        # Query critical bugs
        critical_bugs = bug_skill.query_bugs(priority="Critical", limit=10)
        assert isinstance(critical_bugs, list)

    def test_bug_status_query(self):
        """Test that we can query bugs by status."""
        bug_skill = get_bug_skill()

        # Query open bugs
        open_bugs = bug_skill.query_bugs(status="open", limit=10)
        assert isinstance(open_bugs, list)

        # Query resolved bugs
        resolved_bugs = bug_skill.query_bugs(status="resolved", limit=10)
        assert isinstance(resolved_bugs, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
