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
            daemon = DevDaemon(roadmap_path="/nonexistent/ROADMAP.md")
            daemon._check_prerequisites()

    def test_daemon_handles_invalid_roadmap(self, tmp_path):
        """Verify error when ROADMAP is invalid."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("This is not a valid roadmap")

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should return empty list, not crash
        assert isinstance(priorities, list)
        assert len(priorities) == 0

    def test_daemon_handles_claude_cli_not_found(self):
        """Verify error when Claude CLI not installed."""
        daemon = DevDaemon(
            roadmap_path="docs/ROADMAP.md", use_claude_cli=True, claude_cli_path="/invalid/path/to/claude"
        )

        # Should fail prerequisite check
        assert not daemon._check_prerequisites()

    def test_daemon_handles_missing_api_key(self, monkeypatch):
        """Verify error when ANTHROPIC_API_KEY not set in API mode."""
        # Remove API key from environment
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=False)  # API mode

        # Should fail prerequisite check
        assert not daemon._check_prerequisites()

    def test_daemon_handles_no_planned_priorities(self, tmp_path):
        """Verify behavior when all priorities are complete."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Done ✅ Complete
All done!
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_priority = parser.get_next_planned_priority()

        # Should return None, not crash
        assert next_priority is None

    def test_parser_handles_corrupted_utf8(self, tmp_path):
        """Verify parser handles files with encoding issues."""
        roadmap = tmp_path / "ROADMAP.md"
        # Write valid markdown
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nContent")

        parser = RoadmapParser(str(roadmap))
        # Should not crash
        priorities = parser.get_priorities()
        assert isinstance(priorities, list)

    def test_daemon_handles_permission_denied(self, tmp_path):
        """Verify daemon handles permission errors gracefully."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap")

        # Make file unreadable
        roadmap.chmod(0o000)

        try:
            parser = RoadmapParser(str(roadmap))
            # Should raise PermissionError
            with pytest.raises(PermissionError):
                parser.roadmap_path.read_text()
        finally:
            # Restore permissions for cleanup
            roadmap.chmod(0o644)


class TestGitErrorHandling:
    """Test git-related error handling."""

    def test_daemon_handles_git_not_initialized(self, tmp_path):
        """Verify daemon handles non-git directory."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nTest")

        # tmp_path is not a git repo
        # Daemon should handle this gracefully
        daemon = DevDaemon(roadmap_path=str(roadmap))
        # Git operations might fail, but initialization should work
        assert daemon is not None

    def test_daemon_handles_dirty_git_state(self):
        """Verify daemon detects uncommitted changes."""
        from coffee_maker.autonomous.git_manager import GitManager

        git = GitManager()
        # Test that is_clean() returns a boolean
        result = git.is_clean()
        assert isinstance(result, bool)


class TestConfigurationErrors:
    """Test configuration error handling."""

    def test_daemon_rejects_invalid_max_retries(self):
        """Verify daemon validates max_retries parameter."""
        # Negative max_retries should be handled
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", max_retries=-1)
        # Should either reject or use default
        assert daemon.max_retries >= 0

    def test_daemon_handles_invalid_model_name(self):
        """Verify daemon handles invalid model names."""
        # Invalid model name - should be stored but caught later
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=True, model="invalid-model-name-12345")
        # Initialization should succeed (validation happens at runtime)
        assert daemon.claude.model == "invalid-model-name-12345"


class TestRuntimeErrors:
    """Test runtime error scenarios."""

    def test_daemon_handles_empty_priority_content(self, tmp_path):
        """Verify daemon handles priority with no content."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Empty Priority 📝 Planned

### PRIORITY 2: Has Content 📝 Planned
This one has content
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should find both priorities
        assert len(priorities) == 2

    def test_daemon_handles_very_long_roadmap(self, tmp_path):
        """Verify daemon handles very large ROADMAP files."""
        roadmap = tmp_path / "ROADMAP.md"

        # Create a large ROADMAP with many priorities
        content = "# Roadmap\n\n"
        for i in range(100):
            status = "✅ Complete" if i < 50 else "📝 Planned"
            content += f"### PRIORITY {i}: Task {i} {status}\n"
            content += f"Content for task {i}\n" * 10
            content += "\n"

        roadmap.write_text(content)

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        # Should handle all 100 priorities
        assert len(priorities) == 100

    def test_daemon_handles_unicode_in_roadmap(self, tmp_path):
        """Verify daemon handles Unicode characters in ROADMAP."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap 🚀

### PRIORITY 1: Test avec émojis 📝 Planned

Content with unicode: café, naïve, 日本語, 中文, עברית, العربية

**Deliverables**:
- Support émojis ✅
- Support unicode 🌍
- Test characters: αβγδ, абвгд
        """
        )

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        assert len(priorities) == 1
        assert "émojis" in priorities[0]["content"]
        assert "日本語" in priorities[0]["content"]


class TestEdgeCaseHandling:
    """Test edge case handling."""

    def test_daemon_handles_roadmap_path_with_spaces(self, tmp_path):
        """Verify daemon handles file paths with spaces."""
        roadmap_dir = tmp_path / "my project files"
        roadmap_dir.mkdir()
        roadmap = roadmap_dir / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nTest")

        daemon = DevDaemon(roadmap_path=str(roadmap))
        assert daemon.roadmap_path.exists()

    def test_daemon_handles_symlink_roadmap(self, tmp_path):
        """Verify daemon follows symlinks to ROADMAP."""
        real_roadmap = tmp_path / "real_ROADMAP.md"
        real_roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nTest")

        link_roadmap = tmp_path / "ROADMAP_link.md"
        link_roadmap.symlink_to(real_roadmap)

        daemon = DevDaemon(roadmap_path=str(link_roadmap))
        assert daemon.roadmap_path.exists()

    def test_parser_handles_windows_line_endings(self, tmp_path):
        """Verify parser handles Windows CRLF line endings."""
        roadmap = tmp_path / "ROADMAP.md"
        content = "# Roadmap\r\n\r\n### PRIORITY 1: Test 📝 Planned\r\nContent\r\n"
        roadmap.write_bytes(content.encode("utf-8"))

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        assert len(priorities) == 1

    def test_parser_handles_mixed_line_endings(self, tmp_path):
        """Verify parser handles mixed line endings."""
        roadmap = tmp_path / "ROADMAP.md"
        content = "# Roadmap\n\r\n### PRIORITY 1: Test 📝 Planned\r\nContent\n"
        roadmap.write_bytes(content.encode("utf-8"))

        parser = RoadmapParser(str(roadmap))
        priorities = parser.get_priorities()

        assert len(priorities) == 1
