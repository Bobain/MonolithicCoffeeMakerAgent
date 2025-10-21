"""Smoke tests for code_developer daemon.

These tests run quickly (<1 minute) and catch obvious breakage.
Run on every commit to ensure basic functionality works.
"""

import pytest
from pathlib import Path
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface


class TestDaemonSmoke:
    """Smoke tests - fast checks for obvious breakage."""

    def test_daemon_imports_successfully(self):
        """Verify all modules can be imported."""
        assert DevDaemon is not None
        assert RoadmapParser is not None
        assert GitManager is not None

    def test_daemon_initializes_with_defaults(self, mock_api_key):
        """Verify daemon can be created with default parameters."""
        daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", auto_approve=False, use_claude_cli=True)
        assert daemon is not None
        assert daemon.roadmap_path.exists()
        assert daemon.auto_approve is False

    def test_daemon_initializes_with_cli_mode(self, mock_api_key):
        """Verify daemon can be initialized in CLI mode."""
        # Use a path that might not exist - test just initialization
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True, claude_cli_path="/opt/homebrew/bin/claude"
        )
        assert daemon.use_claude_cli is True
        assert isinstance(daemon.claude, ClaudeCLIInterface)

    # test_daemon_initializes_with_api_mode moved to tests/manual_tests/test_daemon_api_mode_smoke.py
    # because it requires ANTHROPIC_API_KEY

    def test_roadmap_parser_loads_roadmap(self):
        """Verify roadmap parser can load ROADMAP.md."""
        parser = RoadmapParser("docs/roadmap/ROADMAP.md")
        assert parser is not None
        assert parser.roadmap_path.exists()

    def test_roadmap_parser_finds_priorities(self):
        """Verify parser can extract priorities from ROADMAP."""
        parser = RoadmapParser("docs/roadmap/ROADMAP.md")
        priorities = parser.get_priorities()
        assert len(priorities) > 0
        assert all("name" in p for p in priorities)
        assert all("title" in p for p in priorities)
        assert all("status" in p for p in priorities)

    def test_git_manager_initializes(self):
        """Verify GitManager can be created."""
        git = GitManager()
        assert git is not None

    def test_git_manager_detects_repo(self):
        """Verify GitManager detects we're in a Git repo."""
        git = GitManager()
        # This should not raise an exception
        status = git.is_clean()
        assert isinstance(status, bool)

    def test_roadmap_parser_reads_file_content(self):
        """Verify parser can read ROADMAP content."""
        parser = RoadmapParser("docs/roadmap/ROADMAP.md")
        content = parser.roadmap_path.read_text()
        assert len(content) > 0
        assert "PRIORITY" in content or "Priority" in content.lower()


@pytest.mark.parametrize("use_cli", [True])  # False moved to manual tests
class TestDaemonModeInitialization:
    """Test daemon initialization in CLI mode.

    Note: API mode (use_cli=False) tests moved to tests/manual_tests/test_daemon_api_mode_smoke.py
    because they require ANTHROPIC_API_KEY.
    """

    def test_daemon_mode_correct(self, mock_api_key, use_cli):
        """Verify daemon correctly initializes in CLI mode."""
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md",
            use_claude_cli=use_cli,
            claude_cli_path="/opt/homebrew/bin/claude",
        )
        assert daemon.use_claude_cli == use_cli
        assert isinstance(daemon.claude, ClaudeCLIInterface)


class TestRoadmapParserSmoke:
    """Smoke tests for RoadmapParser."""

    def test_parser_get_next_planned_priority(self):
        """Verify parser can find next planned priority."""
        parser = RoadmapParser("docs/roadmap/ROADMAP.md")
        # This might return None if all priorities are complete
        next_priority = parser.get_next_planned_priority()
        # Should not raise exception
        assert next_priority is None or isinstance(next_priority, dict)

    def test_parser_handles_malformed_status(self, tmp_path):
        """Verify parser handles priorities with unexpected status formats."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Test Task WEIRD STATUS
Some content
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()
        # Should not crash, might parse status as unknown
        assert isinstance(priorities, list)


class TestGitManagerSmoke:
    """Smoke tests for GitManager."""

    def test_git_manager_get_current_branch(self):
        """Verify can get current branch name."""
        git = GitManager()
        branch = git.get_current_branch()
        assert isinstance(branch, str)
        assert len(branch) > 0

    def test_git_manager_is_clean_returns_bool(self):
        """Verify is_clean returns boolean."""
        git = GitManager()
        result = git.is_clean()
        assert isinstance(result, bool)


class TestDaemonConfiguration:
    """Test daemon configuration options."""

    def test_daemon_accepts_custom_roadmap_path(self, mock_api_key, tmp_path):
        """Verify daemon accepts custom ROADMAP path."""
        roadmap = tmp_path / "CUSTOM_ROADMAP.md"
        roadmap.write_text("# Custom Roadmap\n\n### PRIORITY 1: Test ✅ Complete\nDone")

        daemon = DevDaemon(roadmap_path=str(roadmap), use_claude_cli=True)
        assert daemon.roadmap_path == Path(roadmap)
        assert daemon.roadmap_path.exists()

    def test_daemon_accepts_auto_approve_flag(self, mock_api_key):
        """Verify daemon accepts auto_approve configuration."""
        daemon_auto = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", auto_approve=True, use_claude_cli=True)
        daemon_manual = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", auto_approve=False, use_claude_cli=True)

        assert daemon_auto.auto_approve is True
        assert daemon_manual.auto_approve is False

    def test_daemon_accepts_create_prs_flag(self, mock_api_key):
        """Verify daemon accepts create_prs configuration."""
        daemon_with_pr = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", create_prs=True, use_claude_cli=True)
        daemon_no_pr = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", create_prs=False, use_claude_cli=True)

        assert daemon_with_pr.create_prs is True
        assert daemon_no_pr.create_prs is False

    def test_daemon_has_max_retries(self, mock_api_key):
        """Verify daemon has max_retries field."""
        daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True)
        assert hasattr(daemon, "max_retries")
        assert daemon.max_retries == 3  # Default value


@pytest.mark.smoke
class TestQuickSmokeTest:
    """Ultra-fast smoke tests that can run on every file save."""

    def test_all_modules_import(self):
        """Verify all daemon modules can be imported without errors."""
        from coffee_maker.autonomous import daemon
        from coffee_maker.autonomous import roadmap_parser
        from coffee_maker.autonomous import git_manager
        from coffee_maker.autonomous import claude_cli_interface
        from coffee_maker.autonomous import claude_api_interface

        assert all([daemon, roadmap_parser, git_manager, claude_cli_interface, claude_api_interface])

    def test_daemon_class_exists(self):
        """Verify DevDaemon class is properly defined."""
        assert hasattr(DevDaemon, "__init__")
        assert hasattr(DevDaemon, "run")
        assert hasattr(DevDaemon, "_check_prerequisites")

    def test_roadmap_parser_class_exists(self):
        """Verify RoadmapParser class is properly defined."""
        assert hasattr(RoadmapParser, "__init__")
        assert hasattr(RoadmapParser, "get_priorities")
        assert hasattr(RoadmapParser, "get_next_planned_priority")

    def test_git_manager_class_exists(self):
        """Verify GitManager class is properly defined."""
        assert hasattr(GitManager, "__init__")
        assert hasattr(GitManager, "is_clean")
        assert hasattr(GitManager, "get_current_branch")
