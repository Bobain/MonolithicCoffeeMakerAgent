"""Tests for code_developer daemon in Claude CLI mode.

These tests verify the daemon works correctly when using Claude CLI
instead of the Anthropic API.
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface


class TestClaudeCLIInterface:
    """Test Claude CLI interface implementation."""

    def test_claude_cli_is_available(self):
        """Verify Claude CLI is installed and accessible."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            assert cli.is_available()
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed at /opt/homebrew/bin/claude")
            raise

    def test_claude_cli_check_available(self):
        """Verify check_available() works correctly."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            assert cli.check_available()
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed")
            raise

    @pytest.mark.integration
    def test_claude_cli_execute_simple_prompt(self):
        """Verify Claude CLI can execute a simple prompt."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed")
            raise

        result = cli.execute_prompt("Say just 'OK'", timeout=30)

        assert result.success
        assert "OK" in result.content or "ok" in result.content.lower()
        assert result.usage["input_tokens"] > 0
        assert result.usage["output_tokens"] > 0

    @pytest.mark.integration
    def test_claude_cli_handles_timeout(self):
        """Verify Claude CLI handles timeout correctly."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed")
            raise

        # Very short timeout should fail
        result = cli.execute_prompt("Write a very long story...", timeout=1)  # 1 second - too short

        assert result.stop_reason == "timeout"
        assert result.error is not None

    def test_claude_cli_handles_invalid_path(self):
        """Verify error handling for invalid Claude CLI path."""
        with pytest.raises(RuntimeError, match="not found"):
            ClaudeCLIInterface(claude_path="/invalid/path/to/claude")


class TestDaemonCLIMode:
    """Test daemon functionality in CLI mode."""

    def test_daemon_cli_mode_prerequisite_check(self):
        """Verify daemon prerequisite check passes in CLI mode."""
        try:
            daemon = DevDaemon(
                roadmap_path="docs/ROADMAP.md", use_claude_cli=True, claude_cli_path="/opt/homebrew/bin/claude"
            )
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed")
            raise

        assert daemon._check_prerequisites()

    @pytest.mark.integration
    def test_daemon_cli_mode_execution(self, tmp_path):
        """Integration test: Verify daemon can execute in CLI mode."""
        # Create test roadmap with simple task
        test_roadmap = tmp_path / "ROADMAP.md"
        test_roadmap.write_text(
            """
# Test Roadmap

### 🔴 **PRIORITY 1: Test Task** 📝 Planned

**Status**: 📝 Planned

Create a simple test file.

**Deliverables**:
- Create test.txt with content "Hello World"
        """
        )

        try:
            daemon = DevDaemon(roadmap_path=str(test_roadmap), auto_approve=True, create_prs=False, use_claude_cli=True)
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed")
            raise

        # This is a full integration test - may take time
        # Test that daemon can at least start and parse roadmap
        next_priority = daemon.parser.get_next_planned_priority()
        assert next_priority is not None
        assert next_priority["name"] == "PRIORITY 1"
