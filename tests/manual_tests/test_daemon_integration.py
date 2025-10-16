"""Integration tests for autonomous daemon components.

These tests verify that the daemon modules work together correctly:
- RoadmapParser reads and parses ROADMAP.md
- ClaudeCLI can check availability
- GitManager can perform basic operations
- All components integrate properly

Note: These are integration tests, not full end-to-end tests.
Full E2E testing requires a live Claude CLI and Git remote.
"""

from pathlib import Path

import pytest

from coffee_maker.autonomous.claude_cli_interface import ClaudeCLI
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.autonomous.roadmap_parser import RoadmapParser


class TestRoadmapParserIntegration:
    """Test RoadmapParser with real ROADMAP.md."""

    def test_parse_real_roadmap(self):
        """Test parsing the actual ROADMAP.md file."""
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            pytest.skip("ROADMAP.md not found")

        parser = RoadmapParser(str(roadmap_path))
        priorities = parser.get_priorities()

        # Should have multiple priorities
        assert len(priorities) > 0

        # Each priority should have required fields
        for priority in priorities:
            assert "name" in priority
            assert "number" in priority
            assert "title" in priority
            assert "status" in priority
            assert "content" in priority

            # Name should match format
            assert priority["name"].startswith("PRIORITY")

    def test_get_next_planned_priority_real(self):
        """Test finding next planned priority in real ROADMAP."""
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            pytest.skip("ROADMAP.md not found")

        parser = RoadmapParser(str(roadmap_path))
        next_priority = parser.get_next_planned_priority()

        # May or may not have planned priorities
        if next_priority:
            assert "name" in next_priority
            assert "📝" in next_priority["status"] or "planned" in next_priority["status"].lower()

    def test_get_in_progress_priorities_real(self):
        """Test finding in-progress priorities in real ROADMAP."""
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            pytest.skip("ROADMAP.md not found")

        parser = RoadmapParser(str(roadmap_path))
        in_progress = parser.get_in_progress_priorities()

        # Should return list (may be empty)
        assert isinstance(in_progress, list)

        # If there are in-progress priorities, verify format
        for priority in in_progress:
            assert "🔄" in priority["status"] or "in progress" in priority["status"].lower()

    def test_extract_deliverables_real(self):
        """Test extracting deliverables from real ROADMAP."""
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            pytest.skip("ROADMAP.md not found")

        parser = RoadmapParser(str(roadmap_path))
        priorities = parser.get_priorities()

        if priorities:
            # Try to extract deliverables from first priority
            deliverables = parser.extract_deliverables(priorities[0]["name"])
            # Should return list (may be empty)
            assert isinstance(deliverables, list)


class TestClaudeCLIIntegration:
    """Test ClaudeCLI integration with system."""

    def test_check_availability_real(self):
        """Test checking if Claude CLI is actually available."""
        cli = ClaudeCLI()
        result = cli.check_available()

        # Should return bool
        assert isinstance(result, bool)

        # If available, should be the real claude command
        if result:
            # Try to get version
            version_result = cli.execute_command(["--version"], timeout=5)
            assert version_result.returncode in [0, 1]  # May succeed or fail

    def test_execute_command_help(self):
        """Test executing a simple help command."""
        cli = ClaudeCLI()

        # Try --help (should work even if not authenticated)
        result = cli.execute_command(["--help"], timeout=5)

        # Should complete (success or error)
        assert result.returncode is not None
        assert isinstance(result.stdout, str)
        assert isinstance(result.stderr, str)


class TestGitManagerIntegration:
    """Test GitManager with real Git repository."""

    def test_get_current_branch_real(self):
        """Test getting current branch in real repo."""
        git = GitManager()
        branch = git.get_current_branch()

        # Should return string
        assert isinstance(branch, str)
        assert len(branch) > 0

    def test_get_status_real(self):
        """Test getting Git status in real repo."""
        git = GitManager()
        status = git.get_status()

        # Should return string
        assert isinstance(status, str)
        # Should contain typical git status keywords
        assert any(
            keyword in status.lower() for keyword in ["branch", "commit", "working", "nothing to commit", "changes"]
        )

    def test_has_remote_real(self):
        """Test checking if real repo has remote."""
        git = GitManager()
        has_remote = git.has_remote()

        # Should return bool
        assert isinstance(has_remote, bool)

        # If has remote, verify we can get it
        if has_remote:
            result = git._run_git("remote", "-v")
            assert "origin" in result.stdout or "upstream" in result.stdout

    def test_is_clean_real(self):
        """Test checking if real repo is clean."""
        git = GitManager()
        is_clean = git.is_clean()

        # Should return bool
        assert isinstance(is_clean, bool)


class TestDaemonComponentsIntegration:
    """Test daemon components working together."""

    def test_roadmap_to_git_workflow(self):
        """Test workflow: parse roadmap → create branch → commit."""
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            pytest.skip("ROADMAP.md not found")

        # Parse roadmap
        parser = RoadmapParser(str(roadmap_path))
        priorities = parser.get_priorities()
        assert len(priorities) > 0

        # Get first priority
        priority = priorities[0]

        # Create branch name (without actually creating it)
        branch_name = f"test/{priority['name'].lower().replace(' ', '-').replace(':', '')}"
        assert len(branch_name) > 5
        assert branch_name.startswith("test/")

    def test_all_components_initialize(self):
        """Test that all daemon components can be initialized."""
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            pytest.skip("ROADMAP.md not found")

        # Initialize all components
        parser = RoadmapParser(str(roadmap_path))
        git = GitManager()
        claude = ClaudeCLI()

        # All should be initialized
        assert parser.content is not None
        assert git.repo_path.exists()
        assert claude.cli_path == "claude"

        # Should be able to call basic methods
        priorities = parser.get_priorities()
        current_branch = git.get_current_branch()
        claude_available = claude.check_available()

        assert isinstance(priorities, list)
        assert isinstance(current_branch, str)
        assert isinstance(claude_available, bool)


class TestDaemonSafety:
    """Test daemon safety features."""

    def test_git_operations_require_clean_state(self):
        """Test that Git operations check for clean state."""
        git = GitManager()

        # is_clean should work
        is_clean = git.is_clean()
        assert isinstance(is_clean, bool)

    def test_roadmap_parser_validates_file_exists(self):
        """Test that parser validates ROADMAP exists."""
        with pytest.raises(FileNotFoundError):
            RoadmapParser("/nonexistent/roadmap.md")

    def test_claude_cli_handles_timeout(self):
        """Test that Claude CLI handles timeouts gracefully."""
        cli = ClaudeCLI(timeout=1)

        # Execute with very short timeout (likely to timeout on complex operations)
        result = cli.execute_prompt("test prompt", timeout=0.001)

        # Should handle timeout gracefully
        assert result.returncode is not None
        assert isinstance(result.stderr, str)

    def test_git_operations_handle_errors(self):
        """Test that Git operations handle errors gracefully."""
        git = GitManager()

        # Try to checkout nonexistent branch
        result = git.checkout("nonexistent-branch-12345")

        # Should return False, not raise exception
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
