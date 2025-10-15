"""Tests for document ownership enforcement.

CRITICAL: These tests verify the ownership system has no overlaps and
correctly enforces permissions to prevent multi-agent conflicts.
"""

import pytest
from coffee_maker.autonomous.document_ownership import (
    DocumentOwnershipGuard,
    requires_ownership,
)


class TestDocumentOwnershipGuard:
    """Test ownership enforcement core functionality."""

    def test_no_overlapping_ownership_critical(self):
        """CRITICAL: Verify NO overlaps in ownership rules.

        This is the MOST IMPORTANT test - overlaps break parallel operations.
        """
        guard = DocumentOwnershipGuard()
        violations = guard.validate_no_overlaps()

        assert len(violations) == 0, (
            f"CRITICAL: Ownership overlaps detected:\n" +
            "\n".join(violations)
        )

    def test_project_manager_owns_only_roadmap_subdir(self):
        """Verify project_manager owns docs/roadmap/ NOT all of docs/."""
        guard = DocumentOwnershipGuard()

        # Can write to roadmap
        assert guard.can_write("project_manager", "docs/roadmap/ROADMAP.md")
        assert guard.can_write("project_manager", "docs/roadmap/TEAM_COLLABORATION.md")

        # CANNOT write to other docs subdirectories
        assert not guard.can_write("project_manager", "docs/architecture/specs/test.md")
        assert not guard.can_write("project_manager", "docs/generator/traces/test.json")

    def test_project_manager_cannot_write_code(self):
        """project_manager CANNOT write to code files or .claude/ directory."""
        assert not DocumentOwnershipGuard.can_write("project_manager", "coffee_maker/cli/test.py")
        assert not DocumentOwnershipGuard.can_write("project_manager", "tests/unit/test_example.py")
        assert not DocumentOwnershipGuard.can_write("project_manager", "scripts/deploy.sh")
        assert not DocumentOwnershipGuard.can_write("project_manager", ".claude/CLAUDE.md")
        assert not DocumentOwnershipGuard.can_write("project_manager", ".claude/agents/project_manager.md")
        assert not DocumentOwnershipGuard.can_write("project_manager", ".claude/commands/implement-feature.md")

    def test_code_developer_can_write_code(self):
        """code_developer can write to coffee_maker/, tests/, scripts/, .claude/."""
        assert DocumentOwnershipGuard.can_write("code_developer", "coffee_maker/cli/new_feature.py")
        assert DocumentOwnershipGuard.can_write("code_developer", "coffee_maker/autonomous/daemon.py")
        assert DocumentOwnershipGuard.can_write("code_developer", "tests/unit/test_new_feature.py")
        assert DocumentOwnershipGuard.can_write("code_developer", "tests/ci_tests/test_integration.py")
        assert DocumentOwnershipGuard.can_write("code_developer", "scripts/my_script.py")
        assert DocumentOwnershipGuard.can_write("code_developer", ".claude/CLAUDE.md")
        assert DocumentOwnershipGuard.can_write("code_developer", ".claude/agents/code_developer.md")
        assert DocumentOwnershipGuard.can_write("code_developer", ".claude/commands/implement-feature.md")

    def test_code_developer_cannot_write_docs(self):
        """code_developer CANNOT write to any docs/ subdirectories."""
        assert not DocumentOwnershipGuard.can_write("code_developer", "docs/roadmap/ROADMAP.md")
        assert not DocumentOwnershipGuard.can_write("code_developer", "docs/architecture/specs/test.md")
        assert not DocumentOwnershipGuard.can_write("code_developer", "docs/templates/template.md")

    def test_architect_owns_pyproject_toml(self):
        """Verify architect owns pyproject.toml (dependency management)."""
        guard = DocumentOwnershipGuard()

        assert guard.can_write("architect", "pyproject.toml")
        assert not guard.can_write("code_developer", "pyproject.toml")

    def test_architect_owns_poetry_lock(self):
        """Verify architect owns poetry.lock."""
        guard = DocumentOwnershipGuard()

        assert guard.can_write("architect", "poetry.lock")
        assert not guard.can_write("code_developer", "poetry.lock")

    def test_user_interpret_can_write_own_data(self):
        """user_interpret can write to data/user_interpret/ directory."""
        assert DocumentOwnershipGuard.can_write("user_interpret", "data/user_interpret/conversation_history.jsonl")
        assert DocumentOwnershipGuard.can_write("user_interpret", "data/user_interpret/conversation_summaries.json")

    def test_user_interpret_cannot_write_docs(self):
        """user_interpret CANNOT write to docs/ subdirectories."""
        assert not DocumentOwnershipGuard.can_write("user_interpret", "docs/roadmap/ROADMAP.md")
        assert not DocumentOwnershipGuard.can_write("user_interpret", "docs/user_interpret/README.md")

    def test_no_parent_directory_ownership(self):
        """Verify no agent owns parent directory when subdirectories have different owners."""
        guard = DocumentOwnershipGuard()

        # docs/ should NOT appear in ownership rules
        assert "docs/" not in guard.OWNERSHIP_RULES

        # Each subdirectory must be explicitly owned
        assert "docs/roadmap/" in guard.OWNERSHIP_RULES
        assert "docs/architecture/" in guard.OWNERSHIP_RULES
        assert "docs/generator/" in guard.OWNERSHIP_RULES

    def test_architect_owns_dependencies(self):
        """Verify architect owns dependency management files."""
        guard = DocumentOwnershipGuard()

        owners_pyproject = guard.get_owners("pyproject.toml")
        assert owners_pyproject == {"architect"}

        owners_lock = guard.get_owners("poetry.lock")
        assert owners_lock == {"architect"}

    def test_code_developer_cannot_modify_dependencies(self):
        """Verify code_developer CANNOT modify dependency files."""
        guard = DocumentOwnershipGuard()

        with pytest.raises(PermissionError):
            guard.assert_can_write("code_developer", "pyproject.toml")

        with pytest.raises(PermissionError):
            guard.assert_can_write("code_developer", "poetry.lock")

    def test_user_interpret_cannot_write_code(self):
        """user_interpret CANNOT write to code directories."""
        assert not DocumentOwnershipGuard.can_write("user_interpret", "coffee_maker/cli/test.py")
        assert not DocumentOwnershipGuard.can_write("user_interpret", "tests/unit/test_example.py")

    def test_generator_can_write_traces(self):
        """Generator (ACE component) can write to docs/generator/."""
        assert DocumentOwnershipGuard.can_write("generator", "docs/generator/traces/2025-10-15/trace.json")
        assert DocumentOwnershipGuard.can_write("generator", "docs/generator/metadata.json")

    def test_generator_cannot_write_other_ace_dirs(self):
        """Generator CANNOT write to other ACE component directories."""
        assert not DocumentOwnershipGuard.can_write("generator", "docs/reflector/deltas/delta.json")
        assert not DocumentOwnershipGuard.can_write("generator", "docs/curator/playbooks/playbook.json")

    def test_reflector_can_write_deltas(self):
        """Reflector (ACE component) can write to docs/reflector/."""
        assert DocumentOwnershipGuard.can_write("reflector", "docs/reflector/deltas/delta_001.json")
        assert DocumentOwnershipGuard.can_write("reflector", "docs/reflector/insights.json")

    def test_curator_can_write_playbooks(self):
        """Curator (ACE component) can write to docs/curator/."""
        assert DocumentOwnershipGuard.can_write("curator", "docs/curator/playbooks/agent_playbook.json")
        assert DocumentOwnershipGuard.can_write("curator", "docs/curator/effectiveness_report.json")

    def test_architect_can_write_architecture_docs(self):
        """Architect can write to docs/architecture/ directory."""
        assert DocumentOwnershipGuard.can_write("architect", "docs/architecture/specs/feature_spec.md")
        assert DocumentOwnershipGuard.can_write("architect", "docs/architecture/decisions/ADR-001-test.md")
        assert DocumentOwnershipGuard.can_write("architect", "docs/architecture/guidelines/guidelines.md")

    def test_architect_cannot_write_other_dirs(self):
        """Architect CANNOT write to other directories."""
        assert not DocumentOwnershipGuard.can_write("architect", "coffee_maker/cli/test.py")
        assert not DocumentOwnershipGuard.can_write("architect", "docs/ROADMAP.md")
        assert not DocumentOwnershipGuard.can_write("architect", "docs/generator/trace.json")

    def test_ownership_violation_raises_error(self):
        """Attempting to write without ownership raises PermissionError."""
        with pytest.raises(PermissionError, match="OWNERSHIP VIOLATION"):
            DocumentOwnershipGuard.assert_can_write("user_interpret", "docs/ROADMAP.md")

    def test_get_owners_returns_correct_agents(self):
        """get_owners returns the correct set of owners for each path."""
        # Test various paths
        assert DocumentOwnershipGuard.get_owners("docs/roadmap/ROADMAP.md") == {"project_manager"}
        assert DocumentOwnershipGuard.get_owners("coffee_maker/cli/test.py") == {"code_developer"}
        assert DocumentOwnershipGuard.get_owners(".claude/CLAUDE.md") == {"code_developer"}
        assert DocumentOwnershipGuard.get_owners(".claude/agents/code_developer.md") == {"code_developer"}
        assert DocumentOwnershipGuard.get_owners("data/user_interpret/history.jsonl") == {"user_interpret"}
        assert DocumentOwnershipGuard.get_owners("docs/generator/trace.json") == {"generator"}
        assert DocumentOwnershipGuard.get_owners("pyproject.toml") == {"architect"}
        assert DocumentOwnershipGuard.get_owners("poetry.lock") == {"architect"}

    def test_ownership_error_message_is_helpful(self):
        """PermissionError message includes helpful context."""
        try:
            DocumentOwnershipGuard.assert_can_write("assistant", "docs/roadmap/ROADMAP.md")
            pytest.fail("Expected PermissionError")
        except PermissionError as e:
            error_msg = str(e)
            assert "OWNERSHIP VIOLATION" in error_msg
            assert "assistant" in error_msg
            assert "project_manager" in error_msg
            assert ".claude/CLAUDE.md" in error_msg  # Reference to docs


class TestOwnershipScenarios:
    """Test real-world ownership scenarios."""

    def test_user_interpret_owns_conversation_logs_exclusively(self):
        """user_interpret exclusively owns conversation logs.

        No other agent should be able to write to user_interpret's data directory.
        """
        path = "data/user_interpret/conversation_history.jsonl"

        # user_interpret can write
        assert DocumentOwnershipGuard.can_write("user_interpret", path)

        # No one else can
        assert not DocumentOwnershipGuard.can_write("project_manager", path)
        assert not DocumentOwnershipGuard.can_write("code_developer", path)
        assert not DocumentOwnershipGuard.can_write("assistant", path)
        assert not DocumentOwnershipGuard.can_write("generator", path)

    def test_project_manager_exclusively_owns_roadmap(self):
        """project_manager and code_developer can write to ROADMAP with field restrictions.

        Special case: ROADMAP.md has shared write with clear boundaries:
        - project_manager: strategic updates (add/remove priorities, descriptions)
        - code_developer: status updates only (Planned → In Progress → Complete)
        """
        path = "docs/roadmap/ROADMAP.md"

        # Both can write (with field restrictions enforced separately)
        assert DocumentOwnershipGuard.can_write("project_manager", path)
        # Note: code_developer can write but only to status fields (enforced at application layer)

        # Others cannot write
        assert not DocumentOwnershipGuard.can_write("user_interpret", path)
        assert not DocumentOwnershipGuard.can_write("assistant", path)

    def test_ace_components_have_separate_directories(self):
        """ACE components have separate, non-overlapping directories.

        This ensures Generator, Reflector, and Curator don't conflict.
        """
        # Generator owns traces
        assert DocumentOwnershipGuard.can_write("generator", "docs/generator/traces/trace.json")
        assert not DocumentOwnershipGuard.can_write("reflector", "docs/generator/traces/trace.json")
        assert not DocumentOwnershipGuard.can_write("curator", "docs/generator/traces/trace.json")

        # Reflector owns deltas
        assert DocumentOwnershipGuard.can_write("reflector", "docs/reflector/deltas/delta.json")
        assert not DocumentOwnershipGuard.can_write("generator", "docs/reflector/deltas/delta.json")
        assert not DocumentOwnershipGuard.can_write("curator", "docs/reflector/deltas/delta.json")

        # Curator owns playbooks
        assert DocumentOwnershipGuard.can_write("curator", "docs/curator/playbooks/playbook.json")
        assert not DocumentOwnershipGuard.can_write("generator", "docs/curator/playbooks/playbook.json")
        assert not DocumentOwnershipGuard.can_write("reflector", "docs/curator/playbooks/playbook.json")

    def test_code_developer_owns_all_implementation_files(self):
        """code_developer has exclusive ownership of implementation and technical configs.

        This prevents other agents from modifying code or technical configurations directly.
        NOTE: architect owns pyproject.toml and poetry.lock (dependency management).
        """
        paths = [
            "coffee_maker/cli/roadmap_cli.py",
            "coffee_maker/autonomous/daemon.py",
            "tests/unit/test_daemon.py",
            "tests/ci_tests/test_integration.py",
            "scripts/deploy.sh",
            ".claude/CLAUDE.md",
            ".claude/agents/code_developer.md",
            ".claude/commands/implement-feature.md",
        ]

        for path in paths:
            # code_developer can write
            assert DocumentOwnershipGuard.can_write("code_developer", path), f"code_developer should own {path}"

            # Others cannot
            assert not DocumentOwnershipGuard.can_write(
                "project_manager", path
            ), f"project_manager should NOT own {path}"
            assert not DocumentOwnershipGuard.can_write("assistant", path), f"assistant should NOT own {path}"

    def test_project_manager_owns_strategic_docs_subdirs(self):
        """project_manager owns specific docs subdirectories (not all of docs/).

        project_manager owns:
        - docs/roadmap/
        - docs/templates/
        - docs/tutorials/
        - docs/code-searcher/ (writes code-searcher reports)
        - docs/user_interpret/ (meta-docs about user_interpret)
        """
        paths = [
            "docs/roadmap/ROADMAP.md",
            "docs/templates/TEMPLATE.md",
            "docs/code-searcher/analysis_2025-10-15.md",
        ]

        for path in paths:
            # project_manager can write
            assert DocumentOwnershipGuard.can_write("project_manager", path), f"project_manager should own {path}"

            # Others cannot
            assert not DocumentOwnershipGuard.can_write("code_developer", path), f"code_developer should NOT own {path}"


class TestOwnershipDecorator:
    """Test @requires_ownership decorator."""

    def test_decorator_allows_owned_files(self):
        """@requires_ownership decorator allows writes to owned files."""

        @requires_ownership("code_developer")
        def write_file(file_path):
            return f"written to {file_path}"

        # Should work for owned file
        result = write_file("coffee_maker/test.py")
        assert result == "written to coffee_maker/test.py"

    def test_decorator_blocks_non_owned_files(self):
        """@requires_ownership decorator blocks writes to non-owned files."""

        @requires_ownership("code_developer")
        def write_file(file_path):
            return f"written to {file_path}"

        # Should fail for non-owned file
        with pytest.raises(PermissionError, match="OWNERSHIP VIOLATION"):
            write_file("docs/ROADMAP.md")

    def test_decorator_with_kwarg(self):
        """@requires_ownership works with file_path as kwarg."""

        @requires_ownership("user_interpret")
        def write_data(file_path, content):
            return f"wrote {content} to {file_path}"

        # Should work
        result = write_data(file_path="data/user_interpret/test.json", content="data")
        assert "data" in result

        # Should fail
        with pytest.raises(PermissionError):
            write_data(file_path="docs/ROADMAP.md", content="data")


class TestOwnershipEdgeCases:
    """Test edge cases and error handling."""

    def test_unknown_agent_cannot_write_anywhere(self):
        """Unknown agents cannot write to any location."""
        assert not DocumentOwnershipGuard.can_write("unknown_agent", "docs/ROADMAP.md")
        assert not DocumentOwnershipGuard.can_write("unknown_agent", "coffee_maker/test.py")
        assert not DocumentOwnershipGuard.can_write("unknown_agent", "data/user_interpret/test.json")

    def test_assistant_cannot_write_anywhere(self):
        """assistant is READ-ONLY and cannot write to any location.

        assistant is a dispatcher/librarian, not a writer.
        """
        paths = [
            "docs/ROADMAP.md",
            "coffee_maker/cli/test.py",
            "data/user_interpret/test.json",
            ".claude/CLAUDE.md",
            ".claude/agents/assistant.md",
            ".claude/commands/implement-feature.md",
        ]

        for path in paths:
            assert not DocumentOwnershipGuard.can_write(
                "assistant", path
            ), f"assistant should be READ-ONLY, cannot write to {path}"

    def test_get_owners_returns_empty_for_unmatched_path(self):
        """get_owners returns empty set for paths with no ownership rule."""
        owners = DocumentOwnershipGuard.get_owners("some/random/path.txt")
        assert owners == set()

    def test_ownership_validation_runs_successfully(self):
        """Ownership validation completes without errors."""
        # This should not raise any exceptions
        result = DocumentOwnershipGuard.validate_no_overlaps()
        # Result is list of violations (empty list = success)
        assert len(result) == 0
