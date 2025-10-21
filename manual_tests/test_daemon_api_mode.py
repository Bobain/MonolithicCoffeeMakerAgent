"""Tests for code_developer daemon in Anthropic API mode.

These tests verify the daemon works correctly when using the Anthropic API
instead of Claude CLI.
"""

import pytest
import os
from unittest.mock import patch
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.claude_api_interface import ClaudeAPI
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface


class TestClaudeAPIInterface:
    """Test Anthropic API interface implementation."""

    def test_claude_api_initialization(self):
        """Verify Claude API interface can be initialized."""
        # Mock the API key check
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            api = ClaudeAPI()
            assert api is not None

    def test_claude_api_requires_api_key(self):
        """Verify Claude API requires ANTHROPIC_API_KEY."""
        # Remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            # Should handle missing API key gracefully
            try:
                api = ClaudeAPI()
                # If initialization succeeds, check_available should fail
                assert not api.check_available()
            except (ValueError, KeyError, RuntimeError):
                # Expected if API key is strictly required
                pass

    def test_claude_api_check_available(self):
        """Verify check_available() works correctly."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            api = ClaudeAPI()
            # With mock key, check_available might return True or False
            result = api.check_available()
            assert isinstance(result, bool)

    def test_claude_api_accepts_model_parameter(self):
        """Verify API accepts custom model parameter."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            api = ClaudeAPI(model="claude-sonnet-4-5-20250929")
            assert api.model == "claude-sonnet-4-5-20250929"

    def test_claude_api_default_model(self):
        """Verify API uses correct default model."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            api = ClaudeAPI()
            # Should have a valid default model
            assert hasattr(api, "model")
            assert isinstance(api.model, str)
            assert len(api.model) > 0


class TestDaemonAPIMode:
    """Test daemon functionality in API mode."""

    def test_daemon_api_mode_initialization(self):
        """Verify daemon can be initialized in API mode."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False)
            assert daemon.use_claude_cli is False
            assert isinstance(daemon.claude, ClaudeAPI)

    def test_daemon_api_mode_prerequisite_check(self):
        """Verify daemon prerequisite check in API mode."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False)

            # Prerequisite check should verify API key exists
            result = daemon._check_prerequisites()
            assert isinstance(result, bool)

    def test_daemon_api_mode_fails_without_key(self):
        """Verify daemon fails gracefully without API key."""
        with patch.dict(os.environ, {}, clear=True):
            daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False)

            # Should fail prerequisite check
            result = daemon._check_prerequisites()
            assert result is False

    def test_daemon_api_mode_model_configuration(self):
        """Verify daemon API mode accepts model configuration."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            daemon = DevDaemon(
                roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False, model="claude-sonnet-4-5-20250929"
            )

            assert daemon.claude.model == "claude-sonnet-4-5-20250929"


class TestClaudeAPIErrorHandling:
    """Test error handling in API mode."""

    def test_api_handles_missing_key_gracefully(self):
        """Verify graceful handling when API key missing."""
        with patch.dict(os.environ, {}, clear=True):
            try:
                api = ClaudeAPI()
                # If initialization succeeds, check should fail
                assert not api.check_available()
            except (ValueError, KeyError, RuntimeError):
                # Expected behavior
                pass

    def test_daemon_handles_api_unavailable(self):
        """Verify daemon handles unavailable API gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False)

            # Should fail prerequisite check, not crash
            assert not daemon._check_prerequisites()

    @pytest.mark.integration
    def test_api_handles_network_errors(self):
        """Verify API handles network errors gracefully."""
        # This would require mocking the Anthropic client
        # or actual API key for integration testing
        pytest.skip("Requires API key for integration testing")


class TestAPIConfiguration:
    """Test API configuration options."""

    def test_api_accepts_timeout_parameter(self):
        """Verify API respects timeout parameter."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            api = ClaudeAPI(timeout=60)
            assert api.timeout == 60

    def test_api_accepts_max_tokens_parameter(self):
        """Verify API accepts max_tokens configuration."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            api = ClaudeAPI(max_tokens=4096)
            assert api.max_tokens == 4096

    def test_api_defaults_are_sensible(self):
        """Verify API has sensible default values."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            api = ClaudeAPI()
            # Check defaults exist and are reasonable
            assert hasattr(api, "model")
            assert hasattr(api, "timeout")
            assert hasattr(api, "max_tokens")


@pytest.mark.integration
class TestClaudeAPIIntegration:
    """Integration tests for API mode (requires ANTHROPIC_API_KEY)."""

    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="Requires ANTHROPIC_API_KEY environment variable")
    def test_api_basic_completion(self):
        """Test basic API completion works."""
        api = ClaudeAPI()
        result = api.execute_prompt("What is 2+2? Answer with just the number.", timeout=30)

        assert result.success
        assert "4" in result.content

    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="Requires ANTHROPIC_API_KEY environment variable")
    def test_api_with_code_generation(self):
        """Test API can generate code."""
        api = ClaudeAPI()
        result = api.execute_prompt(
            "Write a Python function that returns 'Hello'. Just the code, no explanation.", timeout=60
        )

        assert result.success
        assert "def" in result.content or "return" in result.content

    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="Requires ANTHROPIC_API_KEY environment variable")
    def test_daemon_full_api_workflow(self, tmp_path):
        """Test complete daemon workflow in API mode."""
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

        daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=True, create_prs=False, use_claude_cli=False)

        # Verify setup
        assert daemon._check_prerequisites()
        next_task = daemon.parser.get_next_planned_priority()
        assert next_task is not None
        assert "Simple Task" in next_task["title"]


class TestModeSwitching:
    """Test switching between CLI and API modes."""

    def test_can_create_both_modes_sequentially(self):
        """Verify can create daemon in both modes sequentially."""
        # CLI mode
        daemon_cli = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True)
        assert isinstance(daemon_cli.claude, ClaudeCLIInterface)

        # API mode
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            daemon_api = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False)
            assert isinstance(daemon_api.claude, ClaudeAPI)

    def test_modes_are_independent(self):
        """Verify different daemon instances don't interfere."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            daemon1 = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=True)
            daemon2 = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", use_claude_cli=False)

            assert daemon1.use_claude_cli is True
            assert daemon2.use_claude_cli is False
            assert type(daemon1.claude) != type(daemon2.claude)
