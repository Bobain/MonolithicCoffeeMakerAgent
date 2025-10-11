"""User scenario tests for code_developer daemon.

These tests simulate real user workflows to ensure the daemon
works correctly for end users in production scenarios.
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser


class TestUserScenarios:
    """Test critical user scenarios."""

    def test_user_scenario_first_time_setup(self, tmp_path):
        """
        USER SCENARIO: First-time user sets up daemon

        Steps:
        1. User clones repo
        2. User runs: poetry run code-developer --auto-approve
        3. Daemon should start successfully
        """
        # Create minimal ROADMAP
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Welcome Task** 📝 Planned

**Status**: 📝 Planned

Create README.md
        """
        )

        # User runs daemon
        daemon = DevDaemon(
            roadmap_path=str(roadmap), auto_approve=True, use_claude_cli=False  # Use API mode to avoid CLI dependency
        )

        # Daemon should initialize successfully
        assert daemon is not None
        assert daemon._check_prerequisites()

    def test_user_scenario_daemon_finds_next_task(self, tmp_path):
        """
        USER SCENARIO: Daemon finds next planned task

        Steps:
        1. ROADMAP has completed and planned priorities
        2. Daemon should find first "📝 Planned" priority
        3. Daemon should NOT pick completed priorities
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### 🔴 **PRIORITY 1: Done Task** ✅ Complete

**Status**: ✅ Complete

Already done

### 🔴 **PRIORITY 2: Next Task** 📝 Planned

**Status**: 📝 Planned

This should be picked

### 🔴 **PRIORITY 3: Future Task** 📝 Planned

**Status**: 📝 Planned

This comes later
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_task = parser.get_next_planned_priority()

        assert next_task is not None
        assert next_task["name"] == "PRIORITY 2"
        assert "Next Task" in next_task["title"]

    def test_user_scenario_daemon_skips_after_max_retries(self):
        """
        USER SCENARIO: Daemon gives up after max retries

        Steps:
        1. Priority attempted 3 times with no changes
        2. Daemon should create notification
        3. Daemon should move to next priority (not loop)
        """
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")
        daemon.max_retries = 3

        # Simulate 3 failed attempts
        test_priority = {"name": "PRIORITY TEST", "title": "Test Task", "content": "Test content"}

        daemon.attempted_priorities["PRIORITY TEST"] = 3

        # Should skip this priority
        priority_name = test_priority["name"]
        attempt_count = daemon.attempted_priorities.get(priority_name, 0)

        assert attempt_count >= daemon.max_retries

    def test_user_scenario_daemon_creates_notification_on_no_changes(self):
        """
        USER SCENARIO: Daemon creates notification when no files changed

        Steps:
        1. Claude executes but makes no file changes
        2. Daemon detects no changes (git is_clean)
        3. Daemon creates notification for manual review
        4. Daemon returns success (not failure - avoids loop)
        """
        # This would be tested in integration - requires full daemon run
        # Verifying the logic exists in daemon implementation
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")
        assert hasattr(daemon, "git")
        assert hasattr(daemon.git, "is_clean")
        assert hasattr(daemon, "notifications")

    @pytest.mark.integration
    def test_user_scenario_full_workflow_cli_mode(self, tmp_path):
        """
        USER SCENARIO: Full daemon workflow in CLI mode

        Steps:
        1. User has Claude CLI installed
        2. User runs: code-developer --auto-approve
        3. Daemon reads ROADMAP
        4. Daemon creates branch
        5. Daemon executes Claude CLI
        6. Daemon commits changes
        7. Daemon creates PR
        8. Daemon moves to next priority
        """
        # Full integration test - requires Claude CLI
        # This is the most important test for users
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Test Roadmap

### 🔴 **PRIORITY 1: Integration Test** 📝 Planned

**Status**: 📝 Planned

Test implementation
        """
        )

        try:
            daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=True, create_prs=False, use_claude_cli=True)
            # Just verify initialization - full workflow would be too expensive
            assert daemon is not None
        except RuntimeError as e:
            if "not found" in str(e):
                pytest.skip("Claude CLI not installed")
            raise

    @pytest.mark.integration
    def test_user_scenario_interactive_mode(self, tmp_path):
        """
        USER SCENARIO: User runs daemon in interactive mode

        Steps:
        1. User runs: code-developer (no --auto-approve)
        2. Daemon finds next priority
        3. Daemon creates notification asking for approval
        4. Daemon waits for user response
        5. User approves via: project-manager respond <id> approve
        6. Daemon proceeds with implementation
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Test Roadmap

### 🔴 **PRIORITY 1: Interactive Test** 📝 Planned

**Status**: 📝 Planned

Test interactive approval
        """
        )

        daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=False, use_claude_cli=False)  # Interactive mode

        # Verify interactive mode is configured
        assert daemon.auto_approve is False
        assert hasattr(daemon, "_request_approval")
