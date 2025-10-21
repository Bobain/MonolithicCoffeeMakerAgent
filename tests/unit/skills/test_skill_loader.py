"""
Unit tests for StartupSkillLoader.

Tests the skill loading and execution functionality for agent startup skills.
"""

import os
from unittest.mock import patch

import pytest

from coffee_maker.skills.skill_loader import (
    CFR007ViolationError,
    ContextLoadError,
    HealthCheckError,
    ResourceInitializationError,
    SkillStep,
    StartupSkillLoader,
)


@pytest.fixture
def skill_loader():
    """Create a StartupSkillLoader instance."""
    return StartupSkillLoader()


def test_load_skill_orchestrator(skill_loader):
    """Test loading orchestrator-startup skill file."""
    steps = skill_loader.load_skill("orchestrator-startup")

    assert len(steps) == 4  # 4 steps in orchestrator-startup.md
    assert "Load Required Context" in steps[0].description
    assert "CFR-007" in steps[1].description
    assert "Health Checks" in steps[2].description
    assert "Initialize" in steps[3].description
    assert len(steps[0].checklist) > 0


def test_load_skill_file_not_found(skill_loader):
    """Test loading non-existent skill file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        skill_loader.load_skill("non-existent-skill")

    assert "Skill not found" in str(exc_info.value)


def test_calculate_context_budget_under_limit(skill_loader):
    """Test context budget calculation under 30% limit."""
    # Mock agent file to be small
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value="x" * 1000):  # 250 tokens
            budget_pct = skill_loader._calculate_context_budget("test_agent")

            # Should be well under 30%
            assert budget_pct < 30.0


def test_validate_cfr007_under_limit(skill_loader):
    """Test CFR-007 validation passes when under budget."""
    # Mock small context
    with patch.object(skill_loader, "_calculate_context_budget", return_value=25.0):
        step = SkillStep(description="CFR-007 Validation", checklist=[])

        # Should not raise
        skill_loader._validate_cfr007("test_agent", step)


def test_validate_cfr007_over_limit(skill_loader):
    """Test CFR-007 validation fails when over budget."""
    # Mock large context
    with patch.object(skill_loader, "_calculate_context_budget", return_value=35.0):
        step = SkillStep(description="CFR-007 Validation", checklist=[])

        with pytest.raises(CFR007ViolationError) as exc_info:
            skill_loader._validate_cfr007("test_agent", step)

        assert "Context budget exceeded" in str(exc_info.value)
        assert "35.0%" in str(exc_info.value)


def test_estimate_tokens(skill_loader):
    """Test token estimation."""
    text = "x" * 400  # 400 characters
    tokens = skill_loader._estimate_tokens(text)

    assert tokens == 100  # 400 / 4 = 100 tokens


def test_execute_health_checks_architect_success(skill_loader):
    """Test health checks for architect agent."""
    step = SkillStep(description="Health Checks", checklist=[])

    # Mock all required directories exist
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_dir", return_value=True):
            # Should not raise
            skill_loader._execute_health_checks("architect", step)


def test_execute_health_checks_architect_missing_directory(skill_loader):
    """Test health checks fail when directory missing."""
    step = SkillStep(description="Health Checks", checklist=[])

    # Mock directory doesn't exist
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(HealthCheckError) as exc_info:
            skill_loader._execute_health_checks("architect", step)

        assert "Required directory not found" in str(exc_info.value)


def test_execute_health_checks_code_developer_no_api_key(skill_loader):
    """Test health checks fail when API key missing for code_developer."""
    step = SkillStep(description="Health Checks", checklist=[])

    # Mock no API key
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(HealthCheckError) as exc_info:
            skill_loader._execute_health_checks("code_developer", step)

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)


def test_load_required_context_success(skill_loader):
    """Test loading required context files."""
    step = SkillStep(description="Load Required Context", checklist=[])

    # Mock all required files exist
    with patch("pathlib.Path.exists", return_value=True):
        # Should not raise
        skill_loader._load_required_context("test_agent", step)


def test_load_required_context_missing_file(skill_loader):
    """Test context loading fails when file missing."""
    step = SkillStep(description="Load Required Context", checklist=[])

    # Mock file doesn't exist
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(ContextLoadError) as exc_info:
            skill_loader._load_required_context("test_agent", step)

        assert "Required file not found" in str(exc_info.value)


def test_initialize_agent_resources_architect(skill_loader):
    """Test initializing architect agent resources."""
    step = SkillStep(description="Initialize Agent Resources", checklist=[])

    # Mock ADR directory exists
    with patch("pathlib.Path.exists", return_value=True):
        with patch("coffee_maker.autonomous.agent_registry.AgentRegistry.register"):
            # Should not raise
            skill_loader._initialize_agent_resources("architect", step)


def test_initialize_agent_resources_code_developer(skill_loader):
    """Test initializing code_developer agent resources."""
    step = SkillStep(description="Initialize Agent Resources", checklist=[])

    # Mock all mixin files exist
    with patch("pathlib.Path.exists", return_value=True):
        with patch("coffee_maker.autonomous.agent_registry.AgentRegistry.register"):
            # Should not raise
            skill_loader._initialize_agent_resources("code_developer", step)


def test_initialize_agent_resources_missing_mixin(skill_loader):
    """Test resource initialization fails when mixin missing."""
    step = SkillStep(description="Initialize Agent Resources", checklist=[])

    # Mock mixin file doesn't exist
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(ResourceInitializationError) as exc_info:
            skill_loader._initialize_agent_resources("code_developer", step)

        assert "Daemon mixin not found" in str(exc_info.value)


def test_suggest_fixes_cfr007_violation(skill_loader):
    """Test suggesting fixes for CFR-007 violation."""
    error = CFR007ViolationError("Context budget exceeded")
    fixes = skill_loader._suggest_fixes(error)

    assert len(fixes) > 0
    assert any("Reduce agent prompt size" in fix for fix in fixes)


def test_suggest_fixes_health_check_api_key(skill_loader):
    """Test suggesting fixes for missing API key."""
    error = HealthCheckError("ANTHROPIC_API_KEY not set")
    fixes = skill_loader._suggest_fixes(error)

    assert len(fixes) > 0
    assert any("Set ANTHROPIC_API_KEY" in fix for fix in fixes)


def test_suggest_fixes_context_load_error(skill_loader):
    """Test suggesting fixes for context load error."""
    error = ContextLoadError("Required file not found: .claude/CLAUDE.md")
    fixes = skill_loader._suggest_fixes(error)

    assert len(fixes) > 0
    assert any("Verify file exists" in fix for fix in fixes)


def test_execute_startup_skill_success(skill_loader):
    """Test successful startup skill execution."""
    # Mock all checks pass
    with patch.object(skill_loader, "load_skill") as mock_load:
        with patch.object(skill_loader, "_calculate_context_budget", return_value=25.0):
            with patch.object(skill_loader, "_validate_cfr007"):
                with patch.object(skill_loader, "_execute_health_checks"):
                    with patch.object(skill_loader, "_load_required_context"):
                        with patch.object(skill_loader, "_initialize_agent_resources"):
                            # Mock steps
                            mock_load.return_value = [
                                SkillStep("Load Required Context", []),
                                SkillStep("Validate CFR-007", []),
                                SkillStep("Health Checks", []),
                                SkillStep("Initialize", []),
                            ]

                            result = skill_loader.execute_startup_skill("test_agent")

                            assert result.success is True
                            assert result.steps_completed == 4
                            assert result.total_steps == 4
                            assert result.context_budget_pct == 25.0
                            assert result.execution_time_seconds >= 0


def test_execute_startup_skill_failure(skill_loader):
    """Test startup skill execution failure."""
    # Mock CFR-007 violation
    with patch.object(skill_loader, "load_skill") as mock_load:
        with patch.object(skill_loader, "_load_required_context"):
            with patch.object(skill_loader, "_validate_cfr007") as mock_validate:
                # Mock steps
                mock_load.return_value = [
                    SkillStep("Load Required Context", []),
                    SkillStep("Validate CFR-007", []),
                ]

                # Raise error on CFR-007 validation
                mock_validate.side_effect = CFR007ViolationError("Budget exceeded")

                result = skill_loader.execute_startup_skill("test_agent")

                assert result.success is False
                assert "Budget exceeded" in result.error_message
                assert len(result.suggested_fixes) > 0


def test_get_health_check_results(skill_loader):
    """Test getting health check results."""
    results = skill_loader._get_health_check_results("test_agent")

    assert isinstance(results, dict)
    assert "files_readable" in results
    assert "directories_writable" in results
    assert "api_keys_present" in results
    assert "dependencies_installed" in results
    assert "agent_registered" in results
