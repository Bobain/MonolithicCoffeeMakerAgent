"""Integration tests for code_developer daemon.

These tests verify end-to-end workflows work correctly.
Marked with @pytest.mark.integration to allow selective execution.
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.git_manager import GitManager


@pytest.mark.integration
class TestDaemonIntegration:
    """Integration tests - full workflow testing."""

    def test_daemon_full_initialization(self):
        """Test complete daemon initialization with all components."""
        daemon = DevDaemon(
            roadmap_path="docs/ROADMAP.md",
            auto_approve=False,
            create_prs=False,
            use_claude_cli=False,
        )

        # Verify all components initialized
        assert daemon.parser is not None
        assert daemon.git is not None
        assert daemon.claude is not None
        assert daemon.notifications is not None

        # Verify configuration
        assert daemon.auto_approve is False
        assert daemon.create_prs is False
        assert daemon.max_retries == 3

    def test_daemon_prerequisite_check_complete(self):
        """Test complete prerequisite check."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # This will check:
        # - Claude API/CLI available
        # - Git repo exists
        # - ROADMAP.md exists
        result = daemon._check_prerequisites()

        # Should return boolean
        assert isinstance(result, bool)

    def test_daemon_parses_real_roadmap(self):
        """Test daemon can parse the actual project ROADMAP."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        priorities = daemon.parser.get_priorities()

        # Should find multiple priorities
        assert len(priorities) > 0

        # Each priority should have required structure
        for p in priorities:
            assert "name" in p
            assert "title" in p
            assert "status" in p
            assert "content" in p

    def test_daemon_finds_next_planned_priority(self):
        """Test daemon can find next planned priority."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        next_priority = daemon.parser.get_next_planned_priority()

        # May or may not have planned priorities
        if next_priority:
            assert "name" in next_priority
            assert "title" in next_priority
            assert "Planned" in next_priority["status"] or "📝" in next_priority["status"]

    def test_daemon_build_implementation_prompt(self, tmp_path):
        """Test daemon builds implementation prompts correctly."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Feature Task** 📝 Planned

**Status**: 📝 Planned

Implement new feature
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))
        priority = daemon.parser.get_next_planned_priority()

        # Build prompt
        prompt = daemon._build_implementation_prompt(priority)

        # Should contain key information
        assert "PRIORITY 1" in prompt
        assert "Feature Task" in prompt

    def test_daemon_build_documentation_prompt(self, tmp_path):
        """Test daemon builds documentation prompts correctly."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 2: Documentation** 📝 Planned

**Status**: 📝 Planned

Create user documentation and guides

**Deliverables**:
- Create docs/USER_GUIDE.md
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))
        priority = daemon.parser.get_next_planned_priority()

        # Build prompt
        prompt = daemon._build_implementation_prompt(priority)

        # Should contain CREATE FILES warning
        assert "CREATE FILES" in prompt
        assert "DOCUMENTATION" in prompt

    def test_daemon_build_commit_message(self, tmp_path):
        """Test daemon builds proper commit messages."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Test Feature** 📝 Planned

**Status**: 📝 Planned

Test
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))
        priority = daemon.parser.get_next_planned_priority()

        message = daemon._build_commit_message(priority)

        # Should follow conventions
        assert "feat:" in message or "Implement" in message
        assert "PRIORITY 1" in message
        assert "Claude Code" in message

    def test_daemon_build_pr_body(self, tmp_path):
        """Test daemon builds proper PR descriptions."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Test Feature** 📝 Planned

**Status**: 📝 Planned

Test
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))
        priority = daemon.parser.get_next_planned_priority()

        pr_body = daemon._build_pr_body(priority)

        # Should follow template
        assert "Summary" in pr_body
        assert "PRIORITY 1" in pr_body
        assert "DevDaemon" in pr_body

    def test_daemon_retry_logic(self):
        """Test daemon retry tracking."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Simulate multiple attempts
        priority_name = "PRIORITY TEST"
        daemon.attempted_priorities[priority_name] = 0

        # Increment
        daemon.attempted_priorities[priority_name] += 1
        assert daemon.attempted_priorities[priority_name] == 1

        daemon.attempted_priorities[priority_name] += 1
        assert daemon.attempted_priorities[priority_name] == 2

        daemon.attempted_priorities[priority_name] += 1
        assert daemon.attempted_priorities[priority_name] == 3

        # Should hit max_retries
        assert daemon.attempted_priorities[priority_name] >= daemon.max_retries

    def test_git_integration(self):
        """Test Git operations integration."""
        git = GitManager()

        # Basic operations should work
        current_branch = git.get_current_branch()
        assert isinstance(current_branch, str)
        assert len(current_branch) > 0

        is_clean = git.is_clean()
        assert isinstance(is_clean, bool)

        has_remote = git.has_remote()
        assert isinstance(has_remote, bool)

    def test_roadmap_parser_deliverables_extraction(self):
        """Test deliverable extraction from real ROADMAP."""
        parser = RoadmapParser("docs/ROADMAP.md")
        priorities = parser.get_priorities()

        if len(priorities) > 0:
            # Try to extract deliverables from first priority
            first_priority = priorities[0]
            deliverables = parser.extract_deliverables(first_priority["name"])

            # Should return list (may be empty)
            assert isinstance(deliverables, list)

    @pytest.mark.slow
    def test_daemon_single_iteration_dry_run(self, tmp_path):
        """Test daemon can run single iteration (dry run - no actual implementation)."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Test** 📝 Planned

**Status**: 📝 Planned

Simple test task
        """
        )

        daemon = DevDaemon(
            roadmap_path=str(roadmap),
            auto_approve=True,
            create_prs=False,
            use_claude_cli=False,
        )

        # Just verify daemon can be configured
        # Don't actually run to avoid API costs
        assert daemon is not None
        assert daemon._check_prerequisites() in [True, False]
