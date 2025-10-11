"""Tests for code_developer daemon in Anthropic API mode.

These tests verify the daemon works correctly when using the Anthropic API
directly instead of the Claude CLI.
"""

import pytest
import os
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.claude_api_interface import ClaudeAPI


class TestClaudeAPIInterface:
    """Test Claude API interface implementation."""

    def test_claude_api_initializes(self):
        """Verify Claude API can be initialized."""
        # May fail if ANTHROPIC_API_KEY not set, which is expected
        try:
            api = ClaudeAPI()
            assert api is not None
            assert api.model is not None
        except Exception as e:
            if "API key" in str(e) or "ANTHROPIC_API_KEY" in str(e):
                pytest.skip("ANTHROPIC_API_KEY not set in environment")
            raise

    def test_claude_api_has_check_available(self):
        """Verify API has check_available method."""
        try:
            api = ClaudeAPI()
            assert hasattr(api, "check_available")
            assert callable(api.check_available)
        except Exception as e:
            if "API key" in str(e):
                pytest.skip("ANTHROPIC_API_KEY not set")
            raise

    @pytest.mark.integration
    def test_claude_api_check_available(self):
        """Verify check_available() works correctly."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        api = ClaudeAPI()
        result = api.check_available()
        assert isinstance(result, bool)

    @pytest.mark.integration
    def test_claude_api_execute_simple_prompt(self):
        """Verify Claude API can execute a simple prompt."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        api = ClaudeAPI()
        result = api.execute_prompt("Say just 'OK'", timeout=30)

        assert result.success
        assert "OK" in result.content or "ok" in result.content.lower()
        assert result.usage["input_tokens"] > 0
        assert result.usage["output_tokens"] > 0

    @pytest.mark.integration
    def test_claude_api_handles_errors(self):
        """Verify Claude API handles errors gracefully."""
        # Create API with invalid key
        api = ClaudeAPI(api_key="invalid-key-for-testing")

        result = api.execute_prompt("Test prompt", timeout=5)

        # Should not crash, should return error result
        assert not result.success
        assert result.error is not None


class TestDaemonAPIMode:
    """Test daemon functionality in API mode."""

    def test_daemon_api_mode_initialization(self):
        """Verify daemon initializes correctly in API mode."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=False)  # API mode

        assert daemon.use_claude_cli is False
        assert isinstance(daemon.claude, ClaudeAPI)

    def test_daemon_api_mode_prerequisite_check(self):
        """Verify daemon prerequisite check in API mode."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=False)

        # This will actually call the API to verify availability
        result = daemon._check_prerequisites()
        assert isinstance(result, bool)

    @pytest.mark.integration
    def test_daemon_api_mode_execution(self, tmp_path):
        """Integration test: Verify daemon can execute in API mode."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

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

        daemon = DevDaemon(
            roadmap_path=str(test_roadmap), auto_approve=True, create_prs=False, use_claude_cli=False  # API mode
        )

        # Test that daemon can at least start and parse roadmap
        next_priority = daemon.parser.get_next_planned_priority()
        assert next_priority is not None
        assert next_priority["name"] == "PRIORITY 1"
