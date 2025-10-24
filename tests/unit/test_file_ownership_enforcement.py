"""Unit tests for File Ownership Enforcement (US-038).

This test suite validates the FileOwnership registry and ownership enforcement
mechanisms that implement CFR-001 (Document Ownership Boundaries).

Test Coverage:
    - Ownership lookup for all file patterns
    - Ownership checking with violation detection
    - Edge cases and error handling
    - Cache behavior and performance
    - Rule validation and conflict detection

Related:
    - US-038: File Ownership Enforcement
    - CFR-001: Document Ownership Boundaries
    - docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md
"""

import pytest

from coffee_maker.autonomous.ace.file_ownership import (
    FileOwnership,
    OwnershipUnclearError,
    OwnershipViolationError,
)
from coffee_maker.autonomous.agent_registry import AgentType


class TestFileOwnershipLookup:
    """Test ownership lookup for different file patterns."""

    def test_code_developer_owns_claude_config(self):
        """Test code_developer owns .claude/ directory."""
        assert FileOwnership.get_owner(".claude/CLAUDE.md") == AgentType.CODE_DEVELOPER
        assert FileOwnership.get_owner(".claude/agents/generator.md") == AgentType.CODE_DEVELOPER
        assert FileOwnership.get_owner(".claude/commands/implement-feature.md") == AgentType.CODE_DEVELOPER
        assert FileOwnership.get_owner(".claude/mcp/puppeteer.json") == AgentType.CODE_DEVELOPER

    def test_code_developer_owns_coffee_maker_code(self):
        """Test code_developer owns coffee_maker/ implementation."""
        assert FileOwnership.get_owner("coffee_maker/cli/roadmap_cli.py") == AgentType.CODE_DEVELOPER
        assert FileOwnership.get_owner("coffee_maker/autonomous/daemon.py") == AgentType.CODE_DEVELOPER
        assert FileOwnership.get_owner("coffee_maker/autonomous/ace/generator.py") == AgentType.CODE_DEVELOPER

    def test_code_developer_owns_tests(self):
        """Test code_developer owns tests/ directory."""
        assert FileOwnership.get_owner("tests/unit/test_daemon.py") == AgentType.CODE_DEVELOPER
        assert FileOwnership.get_owner("tests/ci_tests/test_integration.py") == AgentType.CODE_DEVELOPER

    def test_code_developer_owns_scripts(self):
        """Test code_developer owns scripts/ directory."""
        assert FileOwnership.get_owner("scripts/deploy.sh") == AgentType.CODE_DEVELOPER

    def test_code_developer_owns_precommit(self):
        """Test code_developer owns .pre-commit-config.yaml."""
        assert FileOwnership.get_owner(".pre-commit-config.yaml") == AgentType.CODE_DEVELOPER

    def test_project_manager_owns_roadmap(self):
        """Test project_manager owns docs/roadmap/ directory."""
        assert FileOwnership.get_owner("docs/roadmap/ROADMAP.md") == AgentType.PROJECT_MANAGER
        assert FileOwnership.get_owner("docs/roadmap/TEAM_COLLABORATION.md") == AgentType.PROJECT_MANAGER
        assert FileOwnership.get_owner("docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md") == AgentType.PROJECT_MANAGER

    def test_project_manager_owns_templates(self):
        """Test project_manager owns docs/templates/ directory."""
        assert FileOwnership.get_owner("docs/templates/SYNERGY_ANALYSIS_TEMPLATE.md") == AgentType.PROJECT_MANAGER

    def test_project_manager_owns_tutorials(self):
        """Test project_manager owns docs/tutorials/ directory."""
        assert FileOwnership.get_owner("docs/tutorials/QUICKSTART.md") == AgentType.PROJECT_MANAGER

    def test_project_manager_owns_top_level_docs(self):
        """Test project_manager owns top-level docs/*.md files."""
        assert FileOwnership.get_owner("docs/README.md") == AgentType.PROJECT_MANAGER
        assert FileOwnership.get_owner("docs/CONTRIBUTING.md") == AgentType.PROJECT_MANAGER

    def test_project_manager_owns_code_searcher_docs(self):
        """Test project_manager owns docs/assistant (with code analysis skills)/ directory."""
        assert (
            FileOwnership.get_owner("docs/assistant (with code analysis skills)/security_audit_2025-10-13.md")
            == AgentType.PROJECT_MANAGER
        )

    def test_architect_owns_architecture_docs(self):
        """Test architect owns docs/architecture/ directory."""
        assert FileOwnership.get_owner("docs/architecture/specs/US_038_TECHNICAL_SPEC.md") == AgentType.ARCHITECT
        assert FileOwnership.get_owner("docs/architecture/decisions/ADR_001.md") == AgentType.ARCHITECT
        assert FileOwnership.get_owner("docs/architecture/guidelines/ERROR_HANDLING.md") == AgentType.ARCHITECT

    def test_architect_owns_dependencies(self):
        """Test architect owns pyproject.toml and poetry.lock."""
        assert FileOwnership.get_owner("pyproject.toml") == AgentType.ARCHITECT
        assert FileOwnership.get_owner("poetry.lock") == AgentType.ARCHITECT

    def test_generator_owns_traces(self):
        """Test generator owns docs/generator/ directory."""
        assert FileOwnership.get_owner("docs/generator/traces/trace_001.json") == AgentType.GENERATOR

    def test_reflector_owns_deltas(self):
        """Test reflector owns docs/reflector/ directory."""
        assert FileOwnership.get_owner("docs/reflector/deltas/delta_001.md") == AgentType.REFLECTOR

    def test_curator_owns_playbooks(self):
        """Test curator owns docs/curator/ directory."""
        assert FileOwnership.get_owner("docs/curator/playbook.json") == AgentType.CURATOR

    def test_user_listener_owns_data(self):
        """Test user_listener owns data/user_interpret/ directory."""
        assert FileOwnership.get_owner("data/user_interpret/conversation_logs.db") == AgentType.USER_LISTENER


class TestOwnershipChecking:
    """Test ownership checking and violation detection."""

    def test_check_ownership_success(self):
        """Test ownership check succeeds for correct owner."""
        assert FileOwnership.check_ownership(AgentType.CODE_DEVELOPER, ".claude/CLAUDE.md") is True

    def test_check_ownership_failure(self):
        """Test ownership check fails for incorrect owner."""
        assert FileOwnership.check_ownership(AgentType.PROJECT_MANAGER, ".claude/CLAUDE.md") is False

    def test_check_ownership_raises_on_violation(self):
        """Test ownership check raises exception when requested."""
        with pytest.raises(OwnershipViolationError) as exc_info:
            FileOwnership.check_ownership(
                AgentType.PROJECT_MANAGER,
                ".claude/CLAUDE.md",
                raise_on_violation=True,
            )

        error = exc_info.value
        assert error.agent == AgentType.PROJECT_MANAGER
        assert error.file_path == ".claude/CLAUDE.md"
        assert error.owner == AgentType.CODE_DEVELOPER
        assert "Ownership Violation" in str(error)

    def test_ownership_violation_error_message(self):
        """Test OwnershipViolationError has clear message."""
        error = OwnershipViolationError(
            agent=AgentType.PROJECT_MANAGER,
            file_path=".claude/CLAUDE.md",
            owner=AgentType.CODE_DEVELOPER,
        )

        message = str(error)
        assert "project_manager" in message
        assert ".claude/CLAUDE.md" in message
        assert "code_developer" in message
        assert "CFR-001" in message


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_ownership_unclear_for_unknown_file(self):
        """Test ownership unclear for files not in registry."""
        with pytest.raises(OwnershipUnclearError) as exc_info:
            FileOwnership.get_owner("unknown/random/file.txt")

        error = exc_info.value
        assert error.file_path == "unknown/random/file.txt"
        assert "Ownership Unclear" in str(error)

    def test_check_ownership_allows_unclear_files(self):
        """Test ownership check allows unclear files (fail open)."""
        # Should not raise, just log warning and return True
        result = FileOwnership.check_ownership(AgentType.CODE_DEVELOPER, "unknown/file.txt")
        assert result is True

    def test_path_normalization(self):
        """Test paths are normalized (leading ./ removed)."""
        owner1 = FileOwnership.get_owner("coffee_maker/test.py")
        owner2 = FileOwnership.get_owner("./coffee_maker/test.py")
        assert owner1 == owner2

    def test_glob_pattern_matching_with_subdirectories(self):
        """Test glob patterns match deep subdirectories."""
        assert FileOwnership.get_owner("coffee_maker/deep/nested/path/file.py") == AgentType.CODE_DEVELOPER


class TestAllowedPaths:
    """Test getting allowed paths for agents."""

    def test_code_developer_allowed_paths(self):
        """Test code_developer allowed paths."""
        paths = FileOwnership.get_allowed_paths(AgentType.CODE_DEVELOPER)
        assert ".claude/**" in paths
        assert "coffee_maker/**" in paths
        assert "tests/**" in paths

    def test_project_manager_allowed_paths(self):
        """Test project_manager allowed paths."""
        paths = FileOwnership.get_allowed_paths(AgentType.PROJECT_MANAGER)
        assert "docs/roadmap/**" in paths
        assert "docs/templates/**" in paths
        assert "docs/tutorials/**" in paths

    def test_architect_allowed_paths(self):
        """Test architect allowed paths."""
        paths = FileOwnership.get_allowed_paths(AgentType.ARCHITECT)
        assert "docs/architecture/**" in paths
        assert "pyproject.toml" in paths
        assert "poetry.lock" in paths


class TestCacheBehavior:
    """Test ownership cache for performance."""

    def setup_method(self):
        """Clear cache before each test."""
        FileOwnership.clear_cache()

    def test_cache_is_used(self):
        """Test ownership lookups are cached."""
        # First lookup
        owner1 = FileOwnership.get_owner(".claude/CLAUDE.md")

        # Second lookup should use cache
        owner2 = FileOwnership.get_owner(".claude/CLAUDE.md")

        assert owner1 == owner2
        assert ".claude/CLAUDE.md" in FileOwnership._ownership_cache

    def test_cache_clear(self):
        """Test cache can be cleared."""
        FileOwnership.get_owner(".claude/CLAUDE.md")
        assert len(FileOwnership._ownership_cache) > 0

        FileOwnership.clear_cache()
        assert len(FileOwnership._ownership_cache) == 0


class TestRuleValidation:
    """Test ownership rule validation."""

    def test_validate_rules_succeeds(self):
        """Test ownership rules are valid (no conflicts)."""
        assert FileOwnership.validate_rules() is True

    def test_pattern_overlap_detection(self):
        """Test overlapping patterns are detected."""
        # These patterns overlap
        assert FileOwnership._patterns_could_overlap("docs/**", "docs/roadmap/**") is True

        # These don't overlap
        assert FileOwnership._patterns_could_overlap("coffee_maker/**", "docs/**") is False


class TestPatternMatching:
    """Test glob pattern matching logic."""

    def test_matches_exact_file(self):
        """Test exact file path matches."""
        assert FileOwnership._matches_pattern("pyproject.toml", "pyproject.toml") is True

    def test_matches_directory_with_glob(self):
        """Test directory matching with **."""
        assert FileOwnership._matches_pattern("coffee_maker/cli/test.py", "coffee_maker/**") is True

    def test_matches_deep_nesting(self):
        """Test deep nested paths match **."""
        assert FileOwnership._matches_pattern("coffee_maker/a/b/c/d/e/file.py", "coffee_maker/**") is True

    def test_does_not_match_different_directory(self):
        """Test paths don't match wrong patterns."""
        assert FileOwnership._matches_pattern("docs/test.md", "coffee_maker/**") is False


class TestOwnershipScenarios:
    """Test realistic ownership scenarios."""

    def test_scenario_project_manager_tries_to_modify_claude_md(self):
        """Scenario: project_manager attempts to modify .claude/CLAUDE.md.

        Expected: Ownership violation detected, should delegate to code_developer.
        """
        with pytest.raises(OwnershipViolationError) as exc_info:
            FileOwnership.check_ownership(
                AgentType.PROJECT_MANAGER,
                ".claude/CLAUDE.md",
                raise_on_violation=True,
            )

        error = exc_info.value
        assert error.owner == AgentType.CODE_DEVELOPER
        assert "auto-delegate" in str(error).lower()

    def test_scenario_code_developer_tries_to_modify_roadmap(self):
        """Scenario: code_developer attempts to modify ROADMAP.md status.

        Expected: For strategic changes, ownership violation detected.
        Note: code_developer CAN update status, but this is a simplification.
        """
        with pytest.raises(OwnershipViolationError) as exc_info:
            FileOwnership.check_ownership(
                AgentType.CODE_DEVELOPER,
                "docs/roadmap/ROADMAP.md",
                raise_on_violation=True,
            )

        error = exc_info.value
        assert error.owner == AgentType.PROJECT_MANAGER

    def test_scenario_assistant_tries_to_modify_code(self):
        """Scenario: assistant attempts to modify code (READ-ONLY agent).

        Expected: Ownership violation, assistant owns NO files.
        """
        with pytest.raises(OwnershipViolationError) as exc_info:
            FileOwnership.check_ownership(
                AgentType.ASSISTANT,
                "coffee_maker/cli/test.py",
                raise_on_violation=True,
            )

        error = exc_info.value
        assert error.owner == AgentType.CODE_DEVELOPER

    def test_scenario_architect_modifies_pyproject(self):
        """Scenario: architect modifies pyproject.toml (dependency management).

        Expected: Success, architect owns pyproject.toml.
        """
        assert FileOwnership.check_ownership(AgentType.ARCHITECT, "pyproject.toml") is True

    def test_scenario_code_developer_implements_feature(self):
        """Scenario: code_developer implements feature in coffee_maker/.

        Expected: Success, code_developer owns all implementation.
        """
        files = [
            "coffee_maker/cli/new_feature.py",
            "tests/unit/test_new_feature.py",
            ".claude/commands/new-prompt.md",
        ]

        for file in files:
            assert FileOwnership.check_ownership(AgentType.CODE_DEVELOPER, file) is True


class TestCFRCompliance:
    """Test compliance with Critical Functional Requirements."""

    def test_cfr_001_document_ownership_boundaries(self):
        """Test CFR-001: Each file has exactly ONE owner."""
        test_files = [
            (".claude/CLAUDE.md", AgentType.CODE_DEVELOPER),
            ("docs/roadmap/ROADMAP.md", AgentType.PROJECT_MANAGER),
            ("docs/architecture/specs/test.md", AgentType.ARCHITECT),
            ("pyproject.toml", AgentType.ARCHITECT),
        ]

        for file, expected_owner in test_files:
            owner = FileOwnership.get_owner(file)
            assert owner == expected_owner, f"{file} should have exactly ONE owner"

    def test_cfr_003_no_overlap_documents(self):
        """Test CFR-003: No two agents can own the same directory."""
        # Validate that ownership rules have no conflicts
        assert FileOwnership.validate_rules() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
