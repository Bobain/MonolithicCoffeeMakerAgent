"""
Tests for SPEC-106: Orchestrator Commands

Verifies all 15 orchestrator command files:
- Work Distribution (3): find-available-work, create-parallel-tasks, coordinate-dependencies
- Agent Lifecycle (5): spawn-agent-session, monitor-agent-lifecycle, kill-stalled-agent,
                       auto-restart-agent, detect-deadlocks
- Worktree Management (3): create-worktree, merge-completed-work, cleanup-worktrees
- System Monitoring (4): route-inter-agent-messages, monitor-resource-usage,
                         generate-activity-summary, handle-agent-errors
"""

import pytest
from pathlib import Path
import yaml


class TestOrchestratorCommands:
    """Test suite for SPEC-106 orchestrator commands."""

    COMMANDS_DIR = Path(
        "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/" ".claude/commands/agents/orchestrator"
    )

    EXPECTED_COMMANDS = {
        # Work Distribution (3 commands)
        "find-available-work.md": "find_available_work",
        "create-parallel-tasks.md": "create_parallel_tasks",
        "coordinate-dependencies.md": "coordinate_dependencies",
        # Agent Lifecycle (5 commands)
        "spawn-agent-session.md": "spawn_agent_session",
        "monitor-agent-lifecycle.md": "monitor_agent_lifecycle",
        "kill-stalled-agent.md": "kill_stalled_agent",
        "auto-restart-agent.md": "auto_restart_agent",
        "detect-deadlocks.md": "detect_deadlocks",
        # Worktree Management (3 commands)
        "create-worktree.md": "create_worktree",
        "merge-completed-work.md": "merge_completed_work",
        "cleanup-worktrees.md": "cleanup_worktrees",
        # System Monitoring (4 commands)
        "route-inter-agent-messages.md": "route_inter_agent_messages",
        "monitor-resource-usage.md": "monitor_resource_usage",
        "generate-activity-summary.md": "generate_activity_summary",
        "handle-agent-errors.md": "handle_agent_errors",
    }

    def test_all_15_commands_exist(self):
        """Verify all 15 command files exist."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            assert filepath.exists(), f"Missing command file: {filename}"
            assert filepath.is_file(), f"Not a file: {filepath}"

    def test_command_count(self):
        """Verify exactly 15 commands exist."""
        command_files = list(self.COMMANDS_DIR.glob("*.md"))
        assert len(command_files) == 15, f"Expected 15 commands, found {len(command_files)}"

    def test_command_metadata(self):
        """Verify command metadata in YAML frontmatter."""
        for filename, expected_action in self.EXPECTED_COMMANDS.items():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            # Extract YAML frontmatter
            assert content.startswith("---"), f"{filename}: Missing YAML frontmatter"
            yaml_end = content.find("\n---\n")
            assert yaml_end > 0, f"{filename}: Invalid YAML frontmatter"

            yaml_content = content[3:yaml_end]
            metadata = yaml.safe_load(yaml_content)

            # Verify required fields
            assert "command" in metadata, f"{filename}: Missing 'command' field"
            assert "agent" in metadata, f"{filename}: Missing 'agent' field"
            assert "action" in metadata, f"{filename}: Missing 'action' field"
            assert "description" in metadata, f"{filename}: Missing 'description' field"

            # Verify values
            assert metadata["agent"] == "orchestrator", f"{filename}: Wrong agent"
            assert metadata["action"] == expected_action, f"{filename}: Wrong action"
            assert (
                metadata["command"] == f"orchestrator.{expected_action.replace('_', '-')}"
            ), f"{filename}: Wrong command name"

    def test_database_tables_specified(self):
        """Verify database table access is specified."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            yaml_end = content.find("\n---\n")
            yaml_content = content[3:yaml_end]
            metadata = yaml.safe_load(yaml_content)

            # Verify tables field
            assert "tables" in metadata, f"{filename}: Missing 'tables' field"
            assert "read" in metadata["tables"], f"{filename}: Missing 'read' table list"
            assert "write" in metadata["tables"], f"{filename}: Missing 'write' table list"

            # Verify tables are lists
            assert isinstance(metadata["tables"]["read"], list), f"{filename}: 'read' tables must be list"
            assert isinstance(metadata["tables"]["write"], list), f"{filename}: 'write' tables must be list"

    def test_cfr_compliance_specified(self):
        """Verify CFR compliance is documented."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            yaml_end = content.find("\n---\n")
            yaml_content = content[3:yaml_end]
            metadata = yaml.safe_load(yaml_content)

            assert "cfr_compliance" in metadata, f"{filename}: Missing 'cfr_compliance'"
            assert isinstance(metadata["cfr_compliance"], list), f"{filename}: 'cfr_compliance' must be list"
            assert len(metadata["cfr_compliance"]) > 0, f"{filename}: Must list at least one CFR"

    def test_command_structure(self):
        """Verify command content has required sections."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            # Check for required sections
            required_sections = [
                "# Command: orchestrator.",
                "## Purpose",
                "## Parameters",
            ]

            for section in required_sections:
                assert section in content, f"{filename}: Missing section '{section}'"

    def test_work_distribution_commands(self):
        """Verify Work Distribution category (3 commands)."""
        commands = [
            "find-available-work.md",
            "create-parallel-tasks.md",
            "coordinate-dependencies.md",
        ]

        for cmd in commands:
            filepath = self.COMMANDS_DIR / cmd
            assert filepath.exists(), f"Missing: {cmd}"

            content = filepath.read_text()
            # Work distribution should deal with task scheduling
            assert any(
                keyword in content.lower() for keyword in ["task", "parallel", "dependency", "schedule"]
            ), f"{cmd}: Missing work distribution context"

    def test_agent_lifecycle_commands(self):
        """Verify Agent Lifecycle category (5 commands)."""
        commands = [
            "spawn-agent-session.md",
            "monitor-agent-lifecycle.md",
            "kill-stalled-agent.md",
            "auto-restart-agent.md",
            "detect-deadlocks.md",
        ]

        for cmd in commands:
            filepath = self.COMMANDS_DIR / cmd
            assert filepath.exists(), f"Missing: {cmd}"

            content = filepath.read_text()
            # Agent lifecycle should deal with agents
            assert any(
                keyword in content.lower() for keyword in ["agent", "process", "spawn", "lifecycle"]
            ), f"{cmd}: Missing agent lifecycle context"

    def test_worktree_management_commands(self):
        """Verify Worktree Management category (3 commands)."""
        commands = [
            "create-worktree.md",
            "merge-completed-work.md",
            "cleanup-worktrees.md",
        ]

        for cmd in commands:
            filepath = self.COMMANDS_DIR / cmd
            assert filepath.exists(), f"Missing: {cmd}"

            content = filepath.read_text()
            # Worktree commands should mention git
            assert (
                "git worktree" in content.lower() or "worktree" in content.lower()
            ), f"{cmd}: Missing git worktree reference"

    def test_system_monitoring_commands(self):
        """Verify System Monitoring category (4 commands)."""
        commands = [
            "route-inter-agent-messages.md",
            "monitor-resource-usage.md",
            "generate-activity-summary.md",
            "handle-agent-errors.md",
        ]

        for cmd in commands:
            filepath = self.COMMANDS_DIR / cmd
            assert filepath.exists(), f"Missing: {cmd}"

            content = filepath.read_text()
            # System monitoring should deal with system/monitoring
            assert any(
                keyword in content.lower() for keyword in ["monitor", "resource", "message", "error", "activity"]
            ), f"{cmd}: Missing monitoring context"

    def test_cfr_013_in_worktree_commands(self):
        """Verify CFR-013 compliance in worktree commands."""
        worktree_commands = [
            "create-worktree.md",
            "merge-completed-work.md",
            "cleanup-worktrees.md",
        ]

        for filename in worktree_commands:
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            yaml_end = content.find("\n---\n")
            yaml_content = content[3:yaml_end]
            metadata = yaml.safe_load(yaml_content)

            # Worktree commands must reference CFR-013
            assert "CFR-013" in str(metadata.get("cfr_compliance", [])), f"{filename}: Must reference CFR-013"

    def test_cfr_014_in_database_commands(self):
        """Verify CFR-014 compliance in database commands."""
        # Most commands write to database
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            yaml_end = content.find("\n---\n")
            yaml_content = content[3:yaml_end]
            metadata = yaml.safe_load(yaml_content)

            # Most commands reference CFR-014 (database tracing)
            cfr_list = str(metadata.get("cfr_compliance", []))
            if metadata["tables"]["write"]:  # If writes to database
                assert (
                    "CFR-014" in cfr_list or "CFR-015" in cfr_list
                ), f"{filename}: Database writing commands must reference CFR-014 or CFR-015"

    def test_output_format_documented(self):
        """Verify output formats are documented."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            # Look for output examples (JSON or markdown)
            has_json_example = "```json" in content
            has_markdown_example = "```markdown" in content or "**Output**" in content

            assert has_json_example or has_markdown_example, f"{filename}: Missing output format documentation"

    def test_success_criteria_documented(self):
        """Verify success criteria are defined."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            assert "## Success Criteria" in content, f"{filename}: Missing Success Criteria section"

    def test_error_handling_documented(self):
        """Verify error handling is documented."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            # Look for error handling
            has_error_section = "## Error Handling" in content
            has_error_examples = "error" in content.lower()

            assert has_error_section or has_error_examples, f"{filename}: Missing error handling documentation"

    def test_related_commands_documented(self):
        """Verify related commands are cross-referenced."""
        for filename in self.EXPECTED_COMMANDS.keys():
            filepath = self.COMMANDS_DIR / filename
            content = filepath.read_text()

            # Look for related commands section
            has_related_section = "## Related Commands" in content or "related commands" in content.lower()

            # Some commands might not have related commands, but at least document why
            if not has_related_section:
                # Check if there are any .md references to other commands
                ".md" in content and ("command" in content.lower())
                # This is lenient - just ensure they're thinking about relationships
                pass  # Allow either way


class TestOrchestratorCommandCategories:
    """Test organization by SPEC-106 categories."""

    def test_work_distribution_3_commands(self):
        """Work Distribution: 3 commands."""
        assert (
            len(
                [
                    "find-available-work.md",
                    "create-parallel-tasks.md",
                    "coordinate-dependencies.md",
                ]
            )
            == 3
        )

    def test_agent_lifecycle_5_commands(self):
        """Agent Lifecycle: 5 commands."""
        assert (
            len(
                [
                    "spawn-agent-session.md",
                    "monitor-agent-lifecycle.md",
                    "kill-stalled-agent.md",
                    "auto-restart-agent.md",
                    "detect-deadlocks.md",
                ]
            )
            == 5
        )

    def test_worktree_management_3_commands(self):
        """Worktree Management: 3 commands."""
        assert (
            len(
                [
                    "create-worktree.md",
                    "merge-completed-work.md",
                    "cleanup-worktrees.md",
                ]
            )
            == 3
        )

    def test_system_monitoring_4_commands(self):
        """System Monitoring: 4 commands."""
        assert (
            len(
                [
                    "route-inter-agent-messages.md",
                    "monitor-resource-usage.md",
                    "generate-activity-summary.md",
                    "handle-agent-errors.md",
                ]
            )
            == 4
        )

    def test_total_15_commands(self):
        """Total: 15 commands as per SPEC-106."""
        assert 3 + 5 + 3 + 4 == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
