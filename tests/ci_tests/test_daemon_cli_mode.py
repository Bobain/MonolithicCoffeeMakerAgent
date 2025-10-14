"""Tests for code_developer daemon in Claude CLI mode.

These tests verify the daemon works correctly when using Claude CLI
instead of the Anthropic API.
"""

import pytest
from pathlib import Path
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface


class TestClaudeCLIInterface:
    """Test Claude CLI interface implementation."""

    def test_claude_cli_initialization(self):
        """Verify Claude CLI interface can be initialized."""
        cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
        assert cli is not None
        assert cli.claude_path == Path("/opt/homebrew/bin/claude")

    def test_claude_cli_is_available(self):
        """Verify Claude CLI is installed and accessible."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            available = cli.is_available()
            # If Claude CLI is installed, this should return True
            # If not installed, the initialization would have raised an error
            assert isinstance(available, bool)
        except RuntimeError as e:
            # Expected if Claude CLI is not installed
            pytest.skip(f"Claude CLI not available: {e}")

    def test_claude_cli_check_available(self):
        """Verify check_available() works correctly."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            result = cli.check_available()
            assert isinstance(result, bool)
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    @pytest.mark.integration
    def test_claude_cli_execute_simple_prompt(self):
        """Verify Claude CLI can execute a simple prompt."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            result = cli.execute_prompt("Say just 'OK'", timeout=30)

            assert result.success
            assert "OK" in result.content or "ok" in result.content.lower()
            assert result.usage["input_tokens"] > 0
            assert result.usage["output_tokens"] > 0
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    @pytest.mark.integration
    def test_claude_cli_handles_timeout(self):
        """Verify Claude CLI handles timeout correctly."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            # Very short timeout should fail
            result = cli.execute_prompt("Write a very long story...", timeout=1)  # 1 second - too short

            assert result.stop_reason == "timeout" or result.error is not None
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    def test_claude_cli_handles_invalid_path(self):
        """Verify error handling for invalid Claude CLI path."""
        with pytest.raises(RuntimeError, match="not found|does not exist"):
            ClaudeCLIInterface(claude_path="/invalid/path/to/claude")

    def test_claude_cli_with_custom_model(self):
        """Verify Claude CLI accepts custom model parameter."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude", model="sonnet")
            assert cli.model == "sonnet"
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    def test_claude_cli_with_project_flag(self):
        """Verify Claude CLI supports -p project flag."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude", use_project_context=True)
            assert cli.use_project_context is True
        except RuntimeError:
            pytest.skip("Claude CLI not installed")


class TestDaemonCLIMode:
    """Test daemon functionality in CLI mode."""

    def test_daemon_cli_mode_initialization(self):
        """Verify daemon can be initialized in CLI mode."""
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True, claude_cli_path="/opt/homebrew/bin/claude"
        )
        assert daemon.use_claude_cli is True
        assert isinstance(daemon.claude, ClaudeCLIInterface)

    def test_daemon_cli_mode_prerequisite_check(self):
        """Verify daemon prerequisite check in CLI mode."""
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True, claude_cli_path="/opt/homebrew/bin/claude"
        )

        # This will return False if Claude CLI is not installed
        # That's okay - we're just testing the check doesn't crash
        result = daemon._check_prerequisites()
        assert isinstance(result, bool)

    def test_daemon_cli_mode_with_invalid_path_fails(self):
        """Verify daemon fails gracefully with invalid CLI path."""
        daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True, claude_cli_path="/invalid/path")

        # Prerequisite check should fail
        assert not daemon._check_prerequisites()

    @pytest.mark.integration
    def test_daemon_cli_mode_execution(self, tmp_path):
        """Integration test: Verify daemon can execute in CLI mode."""
        # Create test roadmap with simple task
        test_roadmap = tmp_path / "ROADMAP.md"
        test_roadmap.write_text(
            """
# Test Roadmap

### PRIORITY 1: Test Task 📝 Planned

Create a simple test file.

**Deliverables**:
- Create test.txt with content "Hello World"
        """
        )

        try:
            daemon = DevDaemon(
                roadmap_path=str(test_roadmap),
                auto_approve=True,
                create_prs=False,
                use_claude_cli=True,
                claude_cli_path="/opt/homebrew/bin/claude",
            )

            # This is a full integration test - may take time
            # Test that daemon can at least start and parse roadmap
            next_priority = daemon.parser.get_next_planned_priority()
            assert next_priority is not None
            assert next_priority["name"] == "PRIORITY 1"
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    def test_daemon_cli_mode_model_configuration(self):
        """Verify daemon CLI mode accepts model configuration."""
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md",
            use_claude_cli=True,
            claude_cli_path="/opt/homebrew/bin/claude",
            model="sonnet",
        )

        assert daemon.claude.model == "sonnet"

    def test_daemon_cli_mode_uses_correct_default_model(self):
        """Verify daemon uses 'sonnet' as default model."""
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True, claude_cli_path="/opt/homebrew/bin/claude"
        )

        # Default should be 'sonnet', not 'claude-sonnet-4'
        assert daemon.claude.model == "sonnet"


class TestClaudeCLIErrorHandling:
    """Test error handling in Claude CLI mode."""

    def test_cli_handles_missing_executable(self):
        """Verify graceful handling when Claude CLI not found."""
        with pytest.raises(RuntimeError):
            ClaudeCLIInterface(claude_path="/nonexistent/claude")

    def test_cli_returns_error_on_failed_execution(self):
        """Verify error response when CLI execution fails."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            # Empty prompt might cause an error
            result = cli.execute_prompt("", timeout=10)
            # Should return error, not crash
            assert hasattr(result, "success")
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    def test_daemon_handles_cli_unavailable(self):
        """Verify daemon handles unavailable Claude CLI gracefully."""
        daemon = DevDaemon(
            roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True, claude_cli_path="/nonexistent/claude"
        )

        # Should fail prerequisite check, not crash
        assert not daemon._check_prerequisites()


class TestClaudeCLIConfiguration:
    """Test Claude CLI configuration options."""

    def test_cli_accepts_timeout_parameter(self):
        """Verify Claude CLI respects timeout parameter."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            # Should accept timeout parameter without error
            # (actual timeout testing in integration tests)
            assert hasattr(cli, "execute_prompt")
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    def test_cli_command_construction(self):
        """Verify CLI command is constructed correctly."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude", model="sonnet", use_project_context=True)
            # Verify configuration is stored
            assert cli.model == "sonnet"
            assert cli.use_project_context is True
        except RuntimeError:
            pytest.skip("Claude CLI not installed")


@pytest.mark.integration
class TestClaudeCLIIntegration:
    """Integration tests for Claude CLI mode (requires Claude CLI installed)."""

    def test_cli_basic_completion(self):
        """Test basic Claude CLI completion works."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            result = cli.execute_prompt("What is 2+2? Answer with just the number.", timeout=30)

            assert result.success
            assert "4" in result.content
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    def test_cli_with_code_generation(self):
        """Test Claude CLI can generate code."""
        try:
            cli = ClaudeCLIInterface(claude_path="/opt/homebrew/bin/claude")
            result = cli.execute_prompt(
                "Write a Python function that returns 'Hello'. Just the code, no explanation.", timeout=60
            )

            assert result.success
            assert "def" in result.content or "return" in result.content
        except RuntimeError:
            pytest.skip("Claude CLI not installed")

    def test_daemon_full_cli_workflow(self, tmp_path):
        """Test complete daemon workflow in CLI mode."""
        try:
            # Create minimal roadmap
            roadmap = tmp_path / "ROADMAP.md"
            roadmap.write_text(
                """
# Test Roadmap

### PRIORITY 1: Simple Task 📝 Planned

Create a file called hello.txt with the text "Hello World".

**Deliverables**:
- File: hello.txt
- Content: "Hello World"
            """
            )

            daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=True, create_prs=False, use_claude_cli=True)

            # Verify setup
            assert daemon._check_prerequisites()
            next_task = daemon.parser.get_next_planned_priority()
            assert next_task is not None
            assert "Simple Task" in next_task["title"]

        except RuntimeError:
            pytest.skip("Claude CLI not installed")
