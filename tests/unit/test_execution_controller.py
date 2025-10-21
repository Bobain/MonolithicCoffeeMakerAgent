"""
Unit tests for ExecutionController.

Tests unified execution of skills and prompts.

Author: code_developer
Date: 2025-10-19
Related: SPEC-055, US-055
"""

import pytest
from coffee_maker.autonomous.execution_controller import (
    ExecutionController,
    ExecutionMode,
    ExecutionResult,
    NoSkillFoundError,
)
from coffee_maker.autonomous.agent_registry import AgentType


class TestExecutionController:
    """Test ExecutionController functionality."""

    def test_init_controller(self):
        """Test creating an ExecutionController."""
        controller = ExecutionController(AgentType.CODE_DEVELOPER)

        assert controller.agent_type == AgentType.CODE_DEVELOPER

    def test_execute_prompt_only_mode(self):
        """Test executing in PROMPT_ONLY mode."""
        controller = ExecutionController(AgentType.CODE_DEVELOPER)

        result = controller.execute(task="test task", mode=ExecutionMode.PROMPT_ONLY)

        assert isinstance(result, ExecutionResult)
        assert result.mode == ExecutionMode.PROMPT_ONLY
        assert result.skills_used == []
        assert len(result.prompts_used) > 0
        assert result.success is True

    def test_execute_skill_only_mode_no_skill(self):
        """Test executing in SKILL_ONLY mode when no skill exists."""
        controller = ExecutionController(AgentType.CODE_DEVELOPER)

        with pytest.raises(NoSkillFoundError):
            controller.execute(task="nonexistent task", mode=ExecutionMode.SKILL_ONLY)

    def test_execute_hybrid_mode_fallback(self):
        """Test HYBRID mode falls back to prompt when no skill found."""
        controller = ExecutionController(AgentType.CODE_DEVELOPER)

        result = controller.execute(task="nonexistent task", mode=ExecutionMode.HYBRID)

        # Should fall back to PROMPT_ONLY
        assert isinstance(result, ExecutionResult)
        assert result.mode == ExecutionMode.PROMPT_ONLY
        assert result.success is True


class TestExecutionResult:
    """Test ExecutionResult dataclass."""

    def test_execution_result_creation(self):
        """Test creating an ExecutionResult."""
        result = ExecutionResult(
            output="test output",
            mode=ExecutionMode.SKILL_ONLY,
            skills_used=["skill1"],
            prompts_used=[],
            execution_time=1.5,
            success=True,
            errors=[],
        )

        assert result.output == "test output"
        assert result.mode == ExecutionMode.SKILL_ONLY
        assert result.skills_used == ["skill1"]
        assert result.execution_time == 1.5
        assert result.success is True
