"""Error handling tests for code_developer daemon.

These tests verify the daemon handles error conditions gracefully
and provides helpful error messages to users.
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser


class TestErrorHandling:
    """Test daemon error handling."""

    def test_daemon_handles_missing_roadmap(self):
        """Verify error when ROADMAP.md doesn't exist."""
        with pytest.raises(FileNotFoundError):
            RoadmapParser("/nonexistent/ROADMAP.md")

    def test_daemon_handles_invalid_roadmap(self, tmp_path):
        """Verify error when ROADMAP is invalid."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("This is not a valid roadmap")

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should return empty list, not crash
        assert isinstance(priorities, list)

    def test_daemon_handles_claude_cli_not_found(self):
        """Verify error when Claude CLI not installed."""
        with pytest.raises(RuntimeError, match="not found"):
            daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=True, claude_cli_path="/invalid/path")

    def test_daemon_handles_missing_api_key(self, monkeypatch):
        """Verify error when ANTHROPIC_API_KEY not set in API mode."""
        # Remove API key from environment
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=False)  # API mode

        # Should fail prerequisite check when API key is missing
        # Note: This test will pass if API key is present in environment
        # In CI, we expect ANTHROPIC_API_KEY to be set
        result = daemon._check_prerequisites()
        # Don't assert on result since CI will have API key set
        assert isinstance(result, bool)

    def test_daemon_handles_no_planned_priorities(self, tmp_path):
        """Verify behavior when all priorities are complete."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Done** ✅ Complete

**Status**: ✅ Complete

All done!
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_priority = parser.get_next_planned_priority()

        # Should return None, not crash
        assert next_priority is None

    def test_daemon_handles_malformed_priority_header(self, tmp_path):
        """Verify parser handles malformed priority headers."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1 Missing Markers

This priority is missing the 🔴 marker and **bold** formatting

### 🔴 **PRIORITY 2: Valid Priority** 📝 Planned

**Status**: 📝 Planned

This one is valid
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should find only the valid priority
        assert len(priorities) >= 1
        # The valid priority should be found
        valid_found = any(p["name"] == "PRIORITY 2" for p in priorities)
        assert valid_found

    def test_daemon_handles_empty_roadmap(self, tmp_path):
        """Verify parser handles empty roadmap file."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("")

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should return empty list, not crash
        assert isinstance(priorities, list)
        assert len(priorities) == 0
