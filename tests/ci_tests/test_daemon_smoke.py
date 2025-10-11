"""Smoke tests for code_developer daemon.

These tests run quickly (<1 minute) and catch obvious breakage.
Run on every commit to ensure basic functionality works.
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.git_manager import GitManager
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
from coffee_maker.autonomous.claude_api_interface import ClaudeAPI


class TestDaemonSmoke:
    """Smoke tests - fast checks for obvious breakage."""

    def test_daemon_imports_successfully(self):
        """Verify all modules can be imported."""
        assert DevDaemon is not None
        assert RoadmapParser is not None
        assert GitManager is not None

    def test_daemon_initializes_with_defaults(self):
        """Verify daemon can be created with default parameters."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", auto_approve=False)
        assert daemon is not None
        assert daemon.roadmap_path.exists()
        assert daemon.auto_approve is False

    def test_daemon_initializes_with_cli_mode(self):
        """Verify daemon can be initialized in CLI mode."""
        # Skip if Claude CLI not installed
        try:
            daemon = DevDaemon(
                roadmap_path="docs/ROADMAP.md", use_claude_cli=True, claude_cli_path="/opt/homebrew/bin/claude"
            )
            assert daemon.use_claude_cli is True
            assert isinstance(daemon.claude, ClaudeCLIInterface)
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed")
            raise

    def test_daemon_initializes_with_api_mode(self):
        """Verify daemon can be initialized in API mode."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=False)
        assert daemon.use_claude_cli is False
        assert isinstance(daemon.claude, ClaudeAPI)

    def test_roadmap_parser_loads_roadmap(self):
        """Verify roadmap parser can load ROADMAP.md."""
        parser = RoadmapParser("docs/ROADMAP.md")
        assert parser is not None

    def test_roadmap_parser_finds_priorities(self):
        """Verify parser can extract priorities from ROADMAP."""
        parser = RoadmapParser("docs/ROADMAP.md")
        priorities = parser.get_priorities()
        assert len(priorities) > 0
        assert all("name" in p for p in priorities)

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


@pytest.mark.parametrize("use_cli", [True, False])
class TestDaemonModeInitialization:
    """Test daemon initialization in both CLI and API modes."""

    def test_daemon_mode_correct(self, use_cli):
        """Verify daemon correctly initializes in specified mode."""
        # Skip CLI mode test if Claude CLI not installed
        if use_cli:
            try:
                daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=use_cli)
            except RuntimeError as e:
                if "not found" in str(e):
                    pytest.skip("Claude CLI not installed")
                raise
        else:
            daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=use_cli)

        assert daemon.use_claude_cli == use_cli

        if use_cli:
            assert isinstance(daemon.claude, ClaudeCLIInterface)
        else:
            assert isinstance(daemon.claude, ClaudeAPI)
