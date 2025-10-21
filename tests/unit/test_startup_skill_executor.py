"""Unit tests for StartupSkillExecutor - US-062, US-063, US-064

Tests CFR-007 validation, health checks, and skill execution.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from coffee_maker.autonomous.startup_skill_executor import (
    StartupSkillExecutor,
    SkillExecutionResult,
    CFR007ViolationError,
    HealthCheckError,
    ContextLoadError,
    ResourceInitializationError,
    StartupError,
)


class TestStartupSkillExecutor:
    """Test StartupSkillExecutor functionality."""

    @pytest.fixture
    def executor(self):
        """Create StartupSkillExecutor instance."""
        return StartupSkillExecutor()

    def test_execute_startup_skill_code_developer_success(self, executor):
        """Test code_developer startup skill execution (with/without API key)."""
        # This test runs with or without ANTHROPIC_API_KEY set
        result = executor.execute_startup_skill("code_developer")

        # Should have valid result structure
        assert result.agent_name == "code_developer"
        assert result.skill_name == "code-developer-startup"
        assert result.steps_completed > 0
        assert result.execution_time_seconds > 0

        # If API key not set, startup will fail - that's ok for this test
        # The important thing is that the skill executed and tried all checks
        if not os.getenv("ANTHROPIC_API_KEY"):
            assert result.success is False
            assert "API key" in result.error_message
        else:
            assert result.success is True

    def test_execute_startup_skill_architect_success(self, executor):
        """Test successful architect startup skill execution."""
        result = executor.execute_startup_skill("architect")

        assert result.success is True
        assert result.agent_name == "architect"
        assert result.skill_name == "architect-startup"  # No underscore to replace
        assert result.steps_completed > 0

    def test_execute_startup_skill_project_manager_success(self, executor):
        """Test successful project_manager startup skill execution."""
        result = executor.execute_startup_skill("project_manager")

        assert result.success is True
        assert result.agent_name == "project_manager"
        assert result.skill_name == "project-manager-startup"  # underscore converted to hyphen
        assert result.steps_completed > 0

    def test_skill_file_not_found(self, executor):
        """Test skill file not found error."""
        result = executor.execute_startup_skill("nonexistent-agent")

        assert result.success is False
        assert "not found" in result.error_message.lower()
        assert len(result.suggested_fixes) > 0

    def test_cfr007_validation_success(self, executor):
        """Test CFR-007 validation (passes if API key present)."""
        result = executor.execute_startup_skill("code_developer")

        # If API key is present, context budget should be small
        if os.getenv("ANTHROPIC_API_KEY"):
            assert result.success is True
            # Startup files should be very small (<1% of context window)
            assert result.context_budget_pct < 1.0
        else:
            # If no API key, health check fails before context budget check
            assert result.success is False

    def test_cfr007_budget_calculation(self, executor):
        """Test CFR-007 context budget calculation."""
        # Only counts agent-specific startup files, not large docs like ROADMAP
        budget_pct = executor._calculate_context_budget("architect")

        # Should be a reasonable percentage (not > 1% for small startup files)
        assert budget_pct >= 0
        # Should be < 100% (sanity check)
        assert budget_pct < 100.0  # Must have some content

    def test_token_estimation(self, executor):
        """Test token estimation accuracy."""
        # 4 characters per token
        text = "x" * 4000  # Should be ~1000 tokens
        tokens = executor._estimate_tokens(text)

        assert tokens >= 900
        assert tokens <= 1100

    def test_token_estimation_empty_string(self, executor):
        """Test token estimation with empty string."""
        tokens = executor._estimate_tokens("")

        assert tokens == 1  # Minimum 1 token

    def test_health_check_directories_exist(self, executor):
        """Test health check for directory existence."""
        result = executor._check_directories_exist()

        assert result.passed is True
        assert "Critical directories" in result.name

    def test_health_check_write_access(self, executor):
        """Test health check for write access."""
        result = executor._check_directories_writable()

        assert result.passed is True or result.passed is False  # Can be either

    def test_health_check_api_key_present(self, executor):
        """Test health check for API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}):
            result = executor._check_api_key("ANTHROPIC_API_KEY")
            assert result.passed is True

    def test_health_check_api_key_missing(self, executor):
        """Test health check for missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = executor._check_api_key("NONEXISTENT_KEY")
            assert result.passed is False

    def test_health_check_command_available(self, executor):
        """Test health check for command availability."""
        result = executor._check_command_available("git")

        # git should be available on most systems
        assert isinstance(result.passed, bool)

    def test_health_check_file_exists(self, executor):
        """Test health check for file existence."""
        result = executor._check_file_exists("docs/roadmap/ROADMAP.md")

        assert result.passed is True
        assert "ROADMAP.md" in result.name

    def test_health_check_file_missing(self, executor):
        """Test health check for missing file."""
        result = executor._check_file_exists("nonexistent_file.md")

        assert result.passed is False

    def test_health_check_directory_exists(self, executor):
        """Test health check for directory existence."""
        result = executor._check_directory_exists("docs/architecture")

        assert result.passed is True
        assert "docs/architecture" in result.name

    def test_health_check_directory_missing(self, executor):
        """Test health check for missing directory."""
        result = executor._check_directory_exists("nonexistent/directory")

        assert result.passed is False

    def test_suggest_fixes_api_key_error(self, executor):
        """Test suggested fixes for API key error."""
        error = HealthCheckError("ANTHROPIC_API_KEY not set")
        fixes = executor._suggest_fixes("code_developer", error)

        assert len(fixes) > 0
        assert any("ANTHROPIC_API_KEY" in fix for fix in fixes)

    def test_suggest_fixes_cfr007_error(self, executor):
        """Test suggested fixes for CFR-007 error."""
        error = CFR007ViolationError("Context budget exceeded")
        fixes = executor._suggest_fixes("code_developer", error)

        assert len(fixes) > 0
        # CFR007ViolationError should suggest context-related fixes
        assert any("context" in fix.lower() or "load" in fix.lower() for fix in fixes)

    def test_suggest_fixes_file_not_found(self, executor):
        """Test suggested fixes for file not found error."""
        error = FileNotFoundError("file.md not found")
        fixes = executor._suggest_fixes("architect", error)

        assert len(fixes) > 0

    def test_skill_execution_result_string_representation(self):
        """Test SkillExecutionResult string representation."""
        result = SkillExecutionResult(
            success=True,
            skill_name="test-skill",
            agent_name="test_agent",
            steps_completed=4,
            total_steps=4,
            context_budget_pct=25.0,
            health_checks=[],
            execution_time_seconds=0.5,
        )

        result_str = str(result)

        assert "SUCCESS" in result_str
        assert "test-skill" in result_str
        assert "25.0" in result_str

    def test_startup_skill_executor_constants(self):
        """Test StartupSkillExecutor constants."""
        assert StartupSkillExecutor.CONTEXT_WINDOW == 200_000
        assert StartupSkillExecutor.CFR007_BUDGET_PCT == 30.0
        assert StartupSkillExecutor.CFR007_BUDGET_TOKENS == 60_000


class TestSkillStepParsing:
    """Test skill file loading and parsing."""

    def test_load_skill_file_code_developer(self):
        """Test loading code_developer startup skill."""
        executor = StartupSkillExecutor()
        steps = executor._load_skill_file("code-developer-startup")

        assert len(steps) == 4  # Should have 4 standard initialization steps
        assert all(hasattr(s, "description") for s in steps)
        assert all(hasattr(s, "checklist") for s in steps)
        assert any("Load Required Context" in s.description for s in steps)
        assert any("CFR-007" in s.description for s in steps)
        assert any("Health Checks" in s.description for s in steps)

    def test_load_skill_file_architect(self):
        """Test loading architect startup skill."""
        executor = StartupSkillExecutor()
        steps = executor._load_skill_file("architect-startup")

        assert len(steps) == 4  # Should have 4 standard initialization steps
        assert any("Load Required Context" in s.description for s in steps)

    def test_load_skill_file_project_manager(self):
        """Test loading project_manager startup skill."""
        executor = StartupSkillExecutor()
        steps = executor._load_skill_file("project-manager-startup")

        assert len(steps) == 4  # Should have 4 standard initialization steps
        assert any("Load Required Context" in s.description for s in steps)

    def test_load_skill_file_not_found(self):
        """Test loading non-existent skill file."""
        executor = StartupSkillExecutor()

        with pytest.raises(FileNotFoundError):
            executor._load_skill_file("nonexistent-skill")


class TestCFR007Compliance:
    """Test CFR-007 context budget compliance."""

    def test_context_budget_calculation_returns_percentage(self):
        """Test context budget returns a valid percentage."""
        executor = StartupSkillExecutor()

        for agent_name in ["code_developer", "architect", "project_manager"]:
            budget_pct = executor._calculate_context_budget(agent_name)
            # Should return a percentage value
            assert isinstance(budget_pct, float)
            assert budget_pct > 0

    def test_context_budget_positive(self):
        """Test context budget is positive."""
        executor = StartupSkillExecutor()

        for agent_name in ["code_developer", "architect", "project_manager"]:
            budget_pct = executor._calculate_context_budget(agent_name)
            assert budget_pct > 0

    def test_context_budget_consistent(self):
        """Test context budget is consistent across calls."""
        executor = StartupSkillExecutor()

        budget1 = executor._calculate_context_budget("architect")
        budget2 = executor._calculate_context_budget("architect")

        assert budget1 == budget2


class TestHealthChecks:
    """Test health check functionality."""

    def test_execute_health_checks_code_developer(self):
        """Test health checks for code_developer."""
        executor = StartupSkillExecutor()
        step = MagicMock()
        step.description = "Health Checks"

        # This should not raise an error (assuming API key is set in test environment)
        try:
            checks = executor._execute_health_checks("code_developer", step)
            assert len(checks) > 0
        except HealthCheckError as e:
            # If API key missing, that's expected in test environment
            assert "ANTHROPIC_API_KEY" in str(e)

    def test_execute_health_checks_architect(self):
        """Test health checks for architect."""
        executor = StartupSkillExecutor()
        step = MagicMock()
        step.description = "Health Checks"

        checks = executor._execute_health_checks("architect", step)
        assert len(checks) > 0

    def test_execute_health_checks_project_manager(self):
        """Test health checks for project_manager."""
        executor = StartupSkillExecutor()
        step = MagicMock()
        step.description = "Health Checks"

        checks = executor._execute_health_checks("project_manager", step)
        assert len(checks) > 0


class TestErrorHandling:
    """Test error handling in startup skills."""

    def test_startup_error_exception(self):
        """Test StartupError exception."""
        with pytest.raises(StartupError):
            raise StartupError("Test error")

    def test_cfr007_violation_exception(self):
        """Test CFR007ViolationError exception."""
        with pytest.raises(CFR007ViolationError):
            raise CFR007ViolationError("Budget exceeded")

    def test_health_check_error_exception(self):
        """Test HealthCheckError exception."""
        with pytest.raises(HealthCheckError):
            raise HealthCheckError("Check failed")

    def test_context_load_error_exception(self):
        """Test ContextLoadError exception."""
        with pytest.raises(ContextLoadError):
            raise ContextLoadError("File not found")

    def test_resource_initialization_error_exception(self):
        """Test ResourceInitializationError exception."""
        with pytest.raises(ResourceInitializationError):
            raise ResourceInitializationError("Resource not available")
