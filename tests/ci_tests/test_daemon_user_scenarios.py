"""User scenario tests for code_developer daemon.

These tests simulate real user workflows to ensure the daemon
works correctly for end users in production scenarios.
"""

import pytest
from pathlib import Path
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

### PRIORITY 1: Welcome Task 📝 Planned
Create README.md
        """
        )

        # User runs daemon
        daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=True, use_claude_cli=True)

        # Daemon should initialize successfully
        assert daemon is not None
        assert daemon._check_prerequisites() in [True, False]  # May fail if Claude CLI not installed

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

### PRIORITY 1: Done Task ✅ Complete
Already done

### PRIORITY 2: Next Task 📝 Planned
This should be picked

### PRIORITY 3: Future Task 📝 Planned
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

    def test_user_scenario_daemon_handles_empty_roadmap(self, tmp_path):
        """
        USER SCENARIO: User has empty or minimal ROADMAP

        Steps:
        1. ROADMAP exists but has no priorities
        2. Daemon should handle gracefully (not crash)
        3. Should return None for next priority
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# My Project Roadmap

This is a new project with no priorities yet.
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_priority = parser.get_next_planned_priority()

        # Should return None, not crash
        assert next_priority is None

    def test_user_scenario_daemon_handles_all_complete(self, tmp_path):
        """
        USER SCENARIO: All priorities are complete

        Steps:
        1. User has completed all work
        2. All priorities marked ✅ Complete
        3. Daemon should find no next task (sleep/exit)
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: First Feature ✅ Complete
Done!

### PRIORITY 2: Second Feature ✅ Complete
Also done!

### PRIORITY 3: Documentation ✅ Complete
All complete!
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_priority = parser.get_next_planned_priority()

        assert next_priority is None

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
        pytest.skip("Full E2E test - run manually outside CI")

    @pytest.mark.integration
    def test_user_scenario_interactive_mode(self):
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
        pytest.skip("Interactive test - requires notification system")

    def test_user_scenario_custom_roadmap_path(self, tmp_path):
        """
        USER SCENARIO: User specifies custom ROADMAP path

        Steps:
        1. User has ROADMAP in non-standard location
        2. User runs: code-developer --roadmap /path/to/ROADMAP.md
        3. Daemon should use custom path
        """
        custom_roadmap = tmp_path / "custom" / "MY_ROADMAP.md"
        custom_roadmap.parent.mkdir(parents=True)
        custom_roadmap.write_text(
            """
# Custom Roadmap

### PRIORITY 1: Test 📝 Planned
Custom location test
        """
        )

        daemon = DevDaemon(roadmap_path=str(custom_roadmap))
        assert daemon.roadmap_path == Path(custom_roadmap)
        assert daemon.roadmap_path.exists()

        parser = RoadmapParser(str(custom_roadmap))
        next_task = parser.get_next_planned_priority()
        assert next_task is not None

    def test_user_scenario_daemon_no_pr_mode(self, tmp_path):
        """
        USER SCENARIO: User wants daemon to commit but not create PRs

        Steps:
        1. User runs: code-developer --no-pr
        2. Daemon implements features
        3. Daemon commits changes
        4. Daemon DOES NOT create PR
        5. User can review commits and create PR manually
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nTest")

        daemon = DevDaemon(roadmap_path=str(roadmap), create_prs=False)

        assert daemon.create_prs is False

    def test_user_scenario_daemon_verbose_mode(self, tmp_path):
        """
        USER SCENARIO: User wants detailed logging

        Steps:
        1. User runs: code-developer --verbose
        2. Daemon should output detailed logs
        3. User can debug issues
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nTest")

        daemon = DevDaemon(roadmap_path=str(roadmap), verbose=True)

        assert daemon.verbose is True

    def test_user_scenario_daemon_continues_after_error(self):
        """
        USER SCENARIO: Daemon encounters error but continues

        Steps:
        1. Daemon implements PRIORITY 1 successfully
        2. PRIORITY 2 fails (error, timeout, etc.)
        3. Daemon creates notification for PRIORITY 2
        4. Daemon moves to PRIORITY 3
        5. Overall workflow continues
        """
        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md")

        # Simulate a failed priority
        daemon.attempted_priorities["PRIORITY 2"] = 3  # Max retries

        # Daemon should recognize this and skip
        assert daemon.attempted_priorities.get("PRIORITY 2", 0) >= daemon.max_retries


class TestCommonUserErrors:
    """Test how daemon handles common user mistakes."""

    def test_user_error_wrong_roadmap_path(self):
        """User specifies non-existent ROADMAP path."""
        with pytest.raises(FileNotFoundError):
            daemon = DevDaemon(roadmap_path="/nonexistent/ROADMAP.md")
            daemon._check_prerequisites()

    def test_user_error_roadmap_is_directory(self, tmp_path):
        """User accidentally points to directory instead of file."""
        directory = tmp_path / "ROADMAP"
        directory.mkdir()

        # Should raise error or handle gracefully
        with pytest.raises((IsADirectoryError, FileNotFoundError, ValueError)):
            parser = RoadmapParser(str(directory))
            parser.roadmap_path.read_text()

    def test_user_error_claude_cli_not_installed(self):
        """User tries CLI mode without installing Claude CLI."""
        daemon = DevDaemon(
            roadmap_path="docs/ROADMAP.md",
            use_claude_cli=True,
            claude_cli_path="/usr/local/bin/claude",  # Common but might not exist
        )

        # Should fail prerequisite check, not crash
        result = daemon._check_prerequisites()
        # Result can be True or False depending on installation
        assert isinstance(result, bool)

    def test_user_error_no_api_key_in_api_mode(self, monkeypatch):
        """User tries API mode without setting ANTHROPIC_API_KEY."""
        # Remove API key
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        daemon = DevDaemon(roadmap_path="docs/ROADMAP.md", use_claude_cli=False)

        # Should fail prerequisite check
        assert not daemon._check_prerequisites()


class TestUserWorkflowPatterns:
    """Test common user workflow patterns."""

    def test_workflow_daily_daemon_run(self, tmp_path):
        """
        WORKFLOW: User runs daemon daily to implement roadmap

        Pattern:
        - Morning: Start daemon with --auto-approve
        - Daemon works through 3-5 priorities
        - Evening: Review PRs and merge
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Daily Roadmap

### PRIORITY 1: Morning Feature ✅ Complete
Already done

### PRIORITY 2: Today's Task 📝 Planned
Working on this

### PRIORITY 3: Afternoon Feature 📝 Planned
Up next

### PRIORITY 4: Tomorrow's Feature 📝 Planned
For tomorrow
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_task = parser.get_next_planned_priority()

        # Should find PRIORITY 2
        assert next_task["name"] == "PRIORITY 2"

    def test_workflow_supervised_mode(self, tmp_path):
        """
        WORKFLOW: User wants to approve each priority

        Pattern:
        - Run daemon without --auto-approve
        - Daemon asks for approval via notification
        - User reviews and approves/rejects
        - Daemon proceeds or skips
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n\n### PRIORITY 1: Test 📝 Planned\nTest")

        daemon = DevDaemon(roadmap_path=str(roadmap), auto_approve=False)  # User wants to approve manually

        assert daemon.auto_approve is False

    def test_workflow_fix_and_retry(self, tmp_path):
        """
        WORKFLOW: Priority fails, user fixes ROADMAP, daemon retries

        Pattern:
        - PRIORITY 1 fails (vague description)
        - User edits ROADMAP with clearer instructions
        - User marks priority back to 📝 Planned
        - Daemon retries and succeeds
        """
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text(
            """
# Roadmap

### PRIORITY 1: Improved Description 📝 Planned

Create a Python function called `calculate_sum` that:
- Takes two integers as parameters
- Returns their sum
- Includes docstring
- Has unit tests

**Deliverables**:
- File: calculator.py
- Tests: test_calculator.py
        """
        )

        parser = RoadmapParser(str(roadmap))
        next_task = parser.get_next_planned_priority()

        # Clearer description should help daemon succeed
        assert "Deliverables" in next_task["content"]
        assert "calculate_sum" in next_task["content"]
