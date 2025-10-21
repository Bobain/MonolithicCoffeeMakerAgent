"""Smoke tests for code_developer daemon in API mode.

These tests require ANTHROPIC_API_KEY and make real API calls.
They are excluded from CI/CD and must be run manually.

Usage:
    pytest tests/manual_tests/test_daemon_api_mode_smoke.py -v
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.claude_api_interface import ClaudeAPI


class TestDaemonAPIModeSmoke:
    """Smoke tests for daemon in API mode - requires ANTHROPIC_API_KEY."""

    def test_daemon_initializes_with_api_mode(self):
        """Verify daemon can be initialized in API mode.

        Requires: ANTHROPIC_API_KEY environment variable

        This test verifies that:
        - DevDaemon can be created with use_claude_cli=False
        - ClaudeAPI instance is created successfully
        - API key is loaded from environment
        """
        daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False)
        assert daemon.use_claude_cli is False
        assert isinstance(daemon.claude, ClaudeAPI)


@pytest.mark.parametrize("use_cli", [False])
class TestDaemonAPIModeInitialization:
    """Test daemon initialization in API mode.

    Requires: ANTHROPIC_API_KEY environment variable

    Note: CLI mode (use_cli=True) tests remain in CI tests.
    Only API mode tests are here because they require API key.
    """

    def test_daemon_mode_correct(self, use_cli):
        """Verify daemon correctly initializes in API mode.

        Requires: ANTHROPIC_API_KEY environment variable
        """
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md",
            use_claude_cli=use_cli,
            claude_cli_path=None,
        )
        assert daemon.use_claude_cli == use_cli
        assert isinstance(daemon.claude, ClaudeAPI)
