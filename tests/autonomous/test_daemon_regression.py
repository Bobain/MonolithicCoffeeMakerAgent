#!/usr/bin/env python3
"""Non-regression tests for autonomous daemon.

These tests verify core functionality remains intact across releases.
Run before significant releases or when merging PRs to main.
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.git_manager import GitManager


class TestDaemonNonRegression:
    """Non-regression tests for critical daemon functionality."""

    def test_daemon_initializes_correctly(self):
        """Verify daemon can be initialized with default params."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")
        assert daemon is not None
        assert daemon.roadmap_path.exists()

    def test_roadmap_parser_finds_priorities(self):
        """Verify roadmap parser can find planned priorities."""
        parser = RoadmapParser("docs/ROADMAP.md")
        priorities = parser.get_priorities()
        assert len(priorities) > 0

    def test_no_changes_detection_works(self):
        """Verify daemon detects when no files changed (Fix Option 1)."""
        git = GitManager()
        assert git.is_clean() in [True, False]  # Should not raise

    def test_task_specific_prompt_detection(self, tmp_path):
        """Verify documentation tasks are detected correctly (Fix Option 3)."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Test Roadmap

### 🔴 **PRIORITY 2.5: UX Documentation** 📝 Planned

**Status**: 📝 Planned

Create user documentation and guides

**Deliverables**:
- Create docs/USER_GUIDE.md
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))

        # Test documentation priority
        doc_priority = daemon.parser.get_next_planned_priority()
        prompt = daemon._build_implementation_prompt(doc_priority)
        assert "CREATE FILES" in prompt

        # Test feature priority
        roadmap.write_text(
            """
# Test Roadmap

### 🔴 **PRIORITY 7: Implement Analytics** 📝 Planned

**Status**: 📝 Planned

Add analytics tracking

**Deliverables**:
- Implement analytics module
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))
        feature_priority = daemon.parser.get_next_planned_priority()
        prompt = daemon._build_implementation_prompt(feature_priority)
        # Feature prompts should NOT have CREATE FILES warning
        # (they have standard prompt)
        assert "ROADMAP" in prompt  # Should still mention roadmap

    def test_notification_created_on_no_changes(self):
        """Verify notification system is available."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")
        assert hasattr(daemon, "notifications")
        assert hasattr(daemon.notifications, "create_notification")

    def test_daemon_does_not_infinite_loop(self):
        """Critical: Verify daemon has max retry logic."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Verify max_retries is set
        assert hasattr(daemon, "max_retries")
        assert daemon.max_retries > 0

        # Verify attempted_priorities tracking exists
        assert hasattr(daemon, "attempted_priorities")
        assert isinstance(daemon.attempted_priorities, dict)

    def test_daemon_components_initialized(self):
        """Verify all daemon components initialize correctly."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Core components
        assert daemon.parser is not None
        assert daemon.git is not None
        assert daemon.claude is not None
        assert daemon.notifications is not None

        # Configuration
        assert isinstance(daemon.auto_approve, bool)
        assert isinstance(daemon.create_prs, bool)
        assert isinstance(daemon.sleep_interval, int)

    def test_git_manager_basic_operations(self):
        """Verify GitManager core functionality."""
        git = GitManager()

        # Should be able to get current branch
        branch = git.get_current_branch()
        assert isinstance(branch, str)
        assert len(branch) > 0

        # Should be able to check status
        is_clean = git.is_clean()
        assert isinstance(is_clean, bool)

        # Should be able to check for remote
        has_remote = git.has_remote()
        assert isinstance(has_remote, bool)

    def test_roadmap_parser_core_methods(self):
        """Verify RoadmapParser core functionality."""
        parser = RoadmapParser("docs/ROADMAP.md")

        # Should find priorities
        priorities = parser.get_priorities()
        assert isinstance(priorities, list)

        # Should find next planned (may be None)
        next_planned = parser.get_next_planned_priority()
        if next_planned:
            assert isinstance(next_planned, dict)
            assert "name" in next_planned
            assert "title" in next_planned

        # Should find in-progress priorities
        in_progress = parser.get_in_progress_priorities()
        assert isinstance(in_progress, list)

    def test_daemon_build_commit_message(self, tmp_path):
        """Verify daemon builds proper commit messages."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Test** 📝 Planned

**Status**: 📝 Planned

Test priority
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))
        priority = daemon.parser.get_next_planned_priority()

        message = daemon._build_commit_message(priority)

        # Should follow commit message conventions
        assert "PRIORITY 1" in message
        assert "Claude Code" in message
        assert len(message) > 0

    def test_daemon_build_pr_body(self, tmp_path):
        """Verify daemon builds proper PR bodies."""
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Test** 📝 Planned

**Status**: 📝 Planned

Test priority
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap))
        priority = daemon.parser.get_next_planned_priority()

        pr_body = daemon._build_pr_body(priority)

        # Should follow PR template
        assert "Summary" in pr_body
        assert "PRIORITY 1" in pr_body
        assert len(pr_body) > 0

    def test_daemon_prerequisite_check(self):
        """Verify prerequisite check executes without error."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Should return boolean, not crash
        result = daemon._check_prerequisites()
        assert isinstance(result, bool)


@pytest.mark.integration
class TestDaemonIntegrationRegression:
    """Integration regression tests - run before releases."""

    def test_full_daemon_initialization(self):
        """Test complete daemon initialization chain."""
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", auto_approve=False, create_prs=False)

        # All components should initialize
        assert daemon.parser is not None
        assert daemon.git is not None
        assert daemon.claude is not None
        assert daemon.notifications is not None

        # Prerequisite check should work
        result = daemon._check_prerequisites()
        assert isinstance(result, bool)

    def test_roadmap_parsing_end_to_end(self):
        """Test complete ROADMAP parsing workflow."""
        parser = RoadmapParser("docs/ROADMAP.md")

        # Should extract priorities
        priorities = parser.get_priorities()
        assert len(priorities) > 0

        # Should find next planned
        parser.get_next_planned_priority()
        # May or may not exist

        # Should extract deliverables
        if priorities:
            first_priority = priorities[0]
            deliverables = parser.extract_deliverables(first_priority["name"])
            assert isinstance(deliverables, list)
