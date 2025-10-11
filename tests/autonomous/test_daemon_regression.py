#!/usr/bin/env python3
"""Non-regression tests for autonomous daemon.

These tests verify core functionality remains intact across releases.
Run before significant releases or when merging PRs to main.

Usage:
    pytest tests/autonomous/test_daemon_regression.py -v
    pytest tests/autonomous/test_daemon_regression.py -v -m integration
"""

import pytest
from pathlib import Path
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.git_manager import GitManager


class TestDaemonNonRegression:
    """Non-regression tests for critical daemon functionality."""

    def test_daemon_initializes_correctly(self):
        """Verify daemon can be initialized with default params."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")
        assert daemon is not None
        assert daemon.roadmap_path.exists()
        assert daemon.roadmap_path.name == "ROADMAP.md"

    def test_daemon_accepts_all_parameters(self):
        """Verify daemon accepts all configuration parameters."""
        daemon = DevDaemon(
            roadmap_path="docs/ROADMAP.md",
            auto_approve=True,
            create_prs=False,
            use_claude_cli=True,
            max_retries=5,
            verbose=True,
        )

        assert daemon.auto_approve is True
        assert daemon.create_prs is False
        assert daemon.use_claude_cli is True
        assert daemon.max_retries == 5
        assert daemon.verbose is True

    def test_roadmap_parser_finds_priorities(self):
        """Verify roadmap parser can find planned priorities."""
        parser = RoadmapParser("docs/ROADMAP.md")
        priorities = parser.get_all_priorities()
        assert len(priorities) > 0
        # Each priority should have required fields
        for p in priorities:
            assert "name" in p
            assert "title" in p
            assert "status" in p
            assert "content" in p

    def test_roadmap_parser_detects_statuses(self, tmp_path):
        """Verify parser correctly detects priority statuses."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Done ✅ Complete
Complete

### PRIORITY 2: Working 🔄 In Progress
In progress

### PRIORITY 3: Todo 📝 Planned
Planned

### PRIORITY 4: Blocked ⏸️ Blocked
Blocked
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_all_priorities()

        assert len(priorities) == 4
        assert priorities[0]["status"] == "complete"
        assert priorities[1]["status"] == "in_progress"
        assert priorities[2]["status"] == "planned"
        assert priorities[3]["status"] == "blocked"

    def test_no_changes_detection_works(self):
        """Verify daemon detects when no files changed."""
        git = GitManager()
        # Should not raise exception
        result = git.is_clean()
        assert isinstance(result, bool)

    def test_get_next_planned_priority_logic(self, tmp_path):
        """Verify get_next_planned_priority returns correct priority."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Done ✅ Complete
Done

### PRIORITY 2: Current 📝 Planned
Should be returned

### PRIORITY 3: Future 📝 Planned
Later
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_priority = parser.get_next_planned_priority()

        assert next_priority is not None
        assert next_priority["name"] == "PRIORITY 2"
        assert next_priority["status"] == "planned"

    def test_daemon_skips_after_max_retries(self):
        """Verify daemon tracks and respects max retries."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", max_retries=3)

        # Simulate failed attempts
        daemon.attempted_priorities["PRIORITY_TEST"] = 3

        # Should recognize max retries reached
        assert daemon.attempted_priorities["PRIORITY_TEST"] >= daemon.max_retries

    def test_daemon_has_required_methods(self):
        """Verify daemon has all required methods."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Check critical methods exist
        assert hasattr(daemon, "run")
        assert hasattr(daemon, "_check_prerequisites")
        assert hasattr(daemon, "_build_implementation_prompt")
        assert callable(daemon.run)
        assert callable(daemon._check_prerequisites)

    def test_git_manager_has_required_methods(self):
        """Verify GitManager has all required methods."""
        git = GitManager()

        # Check critical methods exist
        assert hasattr(git, "is_clean")
        assert hasattr(git, "get_current_branch")
        assert hasattr(git, "branch_exists")
        assert callable(git.is_clean)
        assert callable(git.get_current_branch)

    def test_parser_handles_empty_roadmap_gracefully(self, tmp_path):
        """Verify parser doesn't crash on empty ROADMAP."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Empty Roadmap\n")

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_all_priorities()

        assert priorities == []
        assert parser.get_next_planned_priority() is None

    def test_parser_handles_malformed_priorities(self, tmp_path):
        """Verify parser handles malformed priorities without crashing."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY ABC: Invalid Number
Invalid

### PRIORITY 1: Valid 📝 Planned
Valid priority

### Not a priority header
Just text
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_all_priorities()

        # Should find at least the valid one
        assert any(p["name"] == "PRIORITY 1" for p in priorities)


@pytest.mark.integration
class TestDaemonIntegrationNonRegression:
    """Integration tests - run before releases."""

    def test_daemon_prerequisite_check_comprehensive(self):
        """Test prerequisite check covers all requirements."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Should check and return boolean
        result = daemon._check_prerequisites()
        assert isinstance(result, bool)

    def test_full_daemon_initialization_sequence(self, tmp_path):
        """Test complete initialization sequence works."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Test Roadmap

### PRIORITY 1: Test Task 📝 Planned

Create a test file.

**Deliverables**:
- File: test.txt
        """
        )

        # Complete initialization
        daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=True, create_prs=False)

        # Verify all components initialized
        assert daemon.parser is not None
        assert daemon.roadmap_path.exists()
        assert daemon.claude is not None

        # Can find next task
        next_task = daemon.parser.get_next_planned_priority()
        assert next_task is not None

    def test_daemon_mode_switching_works(self, tmp_path):
        """Test daemon can be created in both CLI and API modes."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nTest")

        # CLI mode
        daemon_cli = DevDaemon(roadmap_path=str(roadmap), use_claude_cli=True)
        assert daemon_cli.use_claude_cli is True

        # API mode
        daemon_api = DevDaemon(roadmap_path=str(roadmap), use_claude_cli=False)
        assert daemon_api.use_claude_cli is False

    @pytest.mark.slow
    def test_daemon_handles_large_roadmap(self, tmp_path):
        """Test daemon handles large ROADMAP files efficiently."""
        roadmap = tmp_path / "ROADMAP.md"

        # Create large ROADMAP
        content = "# Large Roadmap\n\n"
        for i in range(50):
            content += f"### PRIORITY {i}: Task {i} 📝 Planned\n"
            content += f"Content for task {i}\n\n"

        roadmap.write_text(content)

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_all_priorities()

        assert len(priorities) == 50

        # Should still find next planned efficiently
        next_task = parser.get_next_planned_priority()
        assert next_task is not None


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility."""

    def test_daemon_accepts_old_initialization(self):
        """Verify daemon works with minimal initialization."""
        # Old-style initialization with just roadmap path
        daemon = DevDaemon("docs/ROADMAP.md")
        assert daemon is not None

    def test_parser_accepts_string_path(self):
        """Verify parser accepts string paths (not just Path objects)."""
        # String path
        parser1 = RoadmapParser("docs/ROADMAP.md")
        assert parser1.roadmap_path.exists()

        # Path object
        parser2 = RoadmapParser(Path("docs/ROADMAP.md"))
        assert parser2.roadmap_path.exists()

    def test_daemon_defaults_are_sensible(self):
        """Verify default values are sensible and unchanged."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Check defaults haven't changed
        assert daemon.auto_approve is False  # Safe default
        assert daemon.create_prs is True  # Default behavior
        assert daemon.max_retries == 3  # Standard retry count
        assert daemon.verbose is False  # Quiet by default


class TestCriticalUserScenarios:
    """Test scenarios critical to users."""

    def test_user_can_start_daemon_with_auto_approve(self, tmp_path):
        """Test user can start daemon with --auto-approve flag."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Task 📝 Planned\nTask")

        daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=True)
        assert daemon.auto_approve is True

    def test_user_can_disable_pr_creation(self, tmp_path):
        """Test user can disable PR creation with --no-pr flag."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Task 📝 Planned\nTask")

        daemon = DevDaemon(roadmap_path=str(roadmap), create_prs=False)
        assert daemon.create_prs is False

    def test_user_can_use_custom_roadmap_path(self, tmp_path):
        """Test user can specify custom ROADMAP path."""
        custom_path = tmp_path / "MY_ROADMAP.md"
        custom_path.write_text("# Custom\n\n### PRIORITY 1: Task 📝 Planned\nTask")

        daemon = DevDaemon(roadmap_path=str(custom_path))
        assert daemon.roadmap_path == custom_path

    def test_daemon_fails_gracefully_on_missing_roadmap(self):
        """Test daemon fails gracefully when ROADMAP missing."""
        with pytest.raises(FileNotFoundError):
            daemon = DevDaemon(roadmap_path="/nonexistent/ROADMAP.md")
            daemon._check_prerequisites()
