"""Integration tests for /spec CLI command (US-016 Phase 5).

This module tests the end-to-end spec generation workflow via CLI.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from coffee_maker.cli.roadmap_cli import cmd_spec
from coffee_maker.cli.spec_workflow import SpecReviewResult
from coffee_maker.autonomous.spec_generator import TechnicalSpec, Phase, Task
from coffee_maker.utils.task_estimator import TimeEstimate


@pytest.fixture
def mock_spec_result():
    """Create mock SpecReviewResult for testing."""
    # Create minimal spec
    task = Task(
        title="Test task",
        description="Test",
        deliverable="Test output",
        dependencies=[],
        testing="Unit tests",
        time_estimate=TimeEstimate(
            total_hours=6.5,
            base_hours=5.0,
            breakdown={
                "implementation": 5.0,
                "testing": 1.0,
                "documentation": 0.5,
            },
            confidence=0.85,
            assumptions=["Base complexity: medium", "Testing required"],
            risks=[],
        ),
    )

    phase = Phase(
        name="Test Phase",
        goal="Complete testing",
        tasks=[task],
        risks=["Test risk"],
        success_criteria=["Tests pass"],
        total_hours=6.5,
    )

    spec = TechnicalSpec(
        feature_name="Test Feature",
        feature_type="general",
        complexity="medium",
        summary="Test summary",
        business_value="Test value",
        phases=[phase],
        total_hours=6.5,
        total_days=0.8,
        confidence=0.85,
        metadata={},
    )

    return SpecReviewResult(
        spec=spec,
        spec_path=Path("docs/TEST_SPEC.md"),
        markdown="# Test Spec",
        summary={"total_hours": 6.5, "total_days": 0.8, "phase_count": 1, "task_count": 1, "confidence": 0.85},
        delivery_estimate={
            "total_hours": 6.5,
            "total_days": 0.8,
            "buffer_percentage": 15,
            "buffered_hours": 7.5,
            "buffered_days": 1.2,
            "delivery_date": "2025-10-20",
            "confidence": 0.85,
        },
        approved=False,
    )


class TestSpecCLI:
    """Test /spec CLI command."""

    @patch("coffee_maker.cli.roadmap_cli.AIService")
    @patch("coffee_maker.cli.spec_workflow.SpecWorkflow")
    @patch("builtins.input")
    def test_spec_command_user_declines_review(
        self, mock_input, mock_workflow_class, mock_ai_service_class, mock_spec_result
    ):
        """Test spec command when user declines to review."""
        # Mock workflow
        mock_workflow = Mock()
        mock_workflow.generate_and_review_spec.return_value = mock_spec_result
        mock_workflow.format_spec_summary.return_value = "Spec summary"
        mock_workflow_class.return_value = mock_workflow

        # User declines review
        mock_input.return_value = "n"

        # Create args
        args = Mock()
        args.user_story = "Test user story"
        args.type = "general"
        args.complexity = "medium"
        args.id = "US-016"

        # Execute command
        result = cmd_spec(args)

        # Verify success
        assert result == 0

        # Verify workflow was called
        mock_workflow.generate_and_review_spec.assert_called_once_with(
            user_story="Test user story", feature_type="general", complexity="medium", user_story_id="US-016"
        )

    @patch("coffee_maker.cli.roadmap_cli.AIService")
    @patch("coffee_maker.cli.spec_workflow.SpecWorkflow")
    @patch("builtins.input")
    def test_spec_command_user_approves(self, mock_input, mock_workflow_class, mock_ai_service_class, mock_spec_result):
        """Test spec command when user reviews and approves."""
        # Mock workflow
        mock_workflow = Mock()
        mock_workflow.generate_and_review_spec.return_value = mock_spec_result
        mock_workflow.format_spec_summary.return_value = "Spec summary"
        mock_workflow.format_roadmap_update_example.return_value = "ROADMAP update example"
        mock_workflow.approve_spec.return_value = True
        mock_workflow_class.return_value = mock_workflow

        # User reviews and approves
        mock_input.side_effect = ["y", "y"]  # Review? Yes, Approve? Yes

        # Create args
        args = Mock()
        args.user_story = "Test user story"
        args.type = "general"
        args.complexity = "medium"
        args.id = "US-016"

        # Execute command
        result = cmd_spec(args)

        # Verify success
        assert result == 0

        # Verify approval was called
        mock_workflow.approve_spec.assert_called_once_with(mock_spec_result, "US-016")

    @patch("coffee_maker.cli.roadmap_cli.AIService")
    @patch("coffee_maker.cli.spec_workflow.SpecWorkflow")
    @patch("builtins.input")
    def test_spec_command_user_rejects(self, mock_input, mock_workflow_class, mock_ai_service_class, mock_spec_result):
        """Test spec command when user reviews and rejects."""
        # Mock workflow
        mock_workflow = Mock()
        mock_workflow.generate_and_review_spec.return_value = mock_spec_result
        mock_workflow.format_spec_summary.return_value = "Spec summary"
        mock_workflow.format_roadmap_update_example.return_value = "ROADMAP update example"
        mock_workflow.reject_spec.return_value = True
        mock_workflow_class.return_value = mock_workflow

        # User reviews and rejects
        mock_input.side_effect = ["y", "n", "Scope too large"]  # Review? Yes, Approve? No, Reason

        # Create args
        args = Mock()
        args.user_story = "Test user story"
        args.type = "general"
        args.complexity = "medium"
        args.id = "US-016"

        # Execute command
        result = cmd_spec(args)

        # Verify success
        assert result == 0

        # Verify rejection was called
        mock_workflow.reject_spec.assert_called_once_with(mock_spec_result, "Scope too large")

    @patch("coffee_maker.cli.roadmap_cli.AIService")
    @patch("coffee_maker.cli.spec_workflow.SpecWorkflow")
    @patch("builtins.input")
    def test_spec_command_without_user_story_id(
        self, mock_input, mock_workflow_class, mock_ai_service_class, mock_spec_result
    ):
        """Test spec command without user story ID (ROADMAP not updated)."""
        # Mock workflow
        mock_workflow = Mock()
        mock_workflow.generate_and_review_spec.return_value = mock_spec_result
        mock_workflow.format_spec_summary.return_value = "Spec summary"
        mock_workflow.approve_spec.return_value = True
        mock_workflow_class.return_value = mock_workflow

        # User reviews and approves but no ID
        mock_input.side_effect = ["y", "y"]  # Review? Yes, Approve? Yes

        # Create args WITHOUT id
        args = Mock()
        args.user_story = "Test user story"
        args.type = "general"
        args.complexity = "medium"
        args.id = None  # No ID provided

        # Execute command
        result = cmd_spec(args)

        # Verify success
        assert result == 0

        # Verify approve_spec was NOT called (no ID)
        mock_workflow.approve_spec.assert_not_called()

    @patch("coffee_maker.cli.roadmap_cli.AIService")
    @patch("coffee_maker.cli.spec_workflow.SpecWorkflow")
    def test_spec_command_error_handling(self, mock_workflow_class, mock_ai_service_class):
        """Test spec command error handling."""
        # Mock workflow to raise exception
        mock_workflow = Mock()
        mock_workflow.generate_and_review_spec.side_effect = Exception("Test error")
        mock_workflow_class.return_value = mock_workflow

        # Create args
        args = Mock()
        args.user_story = "Test user story"
        args.type = "general"
        args.complexity = "medium"
        args.id = "US-016"

        # Execute command
        result = cmd_spec(args)

        # Verify error return code
        assert result == 1
