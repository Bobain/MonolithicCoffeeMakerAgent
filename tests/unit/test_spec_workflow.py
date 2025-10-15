"""Unit tests for SpecWorkflow (US-016 Phase 5).

This module tests the interactive spec generation workflow including:
- Spec generation from user stories
- Delivery estimate calculation with buffer
- ROADMAP updates with spec references
- Approve/reject workflow
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from coffee_maker.cli.spec_workflow import (
    SpecWorkflow,
    SpecReviewResult,
    DeliveryEstimate,
)
from coffee_maker.autonomous.spec_generator import TechnicalSpec, Phase, Task
from coffee_maker.utils.task_estimator import TimeEstimate


@pytest.fixture
def mock_ai_service():
    """Create mock AI service."""
    mock = Mock()
    mock.use_claude_cli = False
    mock.client = Mock()
    return mock


@pytest.fixture
def mock_spec():
    """Create mock TechnicalSpec for testing."""
    # Create mock tasks
    task1 = Task(
        title="Create database model",
        description="Implement User model",
        deliverable="User model in models.py",
        dependencies=[],
        testing="Unit tests for model",
        time_estimate=TimeEstimate(
            total_hours=3.0,
            base_hours=2.0,
            breakdown={
                "implementation": 2.0,
                "testing": 0.5,
                "documentation": 0.5,
            },
            confidence=0.9,
            assumptions=["Base complexity: medium", "Testing required"],
            risks=[],
        ),
    )

    task2 = Task(
        title="Create API endpoint",
        description="Implement GET /users endpoint",
        deliverable="API endpoint in routes.py",
        dependencies=["Create database model"],
        testing="Integration tests",
        time_estimate=TimeEstimate(
            total_hours=4.5,
            base_hours=3.0,
            breakdown={
                "implementation": 3.0,
                "testing": 1.0,
                "documentation": 0.5,
            },
            confidence=0.85,
            assumptions=["Base complexity: medium", "Testing required", "Documentation required"],
            risks=["Integration complexity may increase estimate"],
        ),
    )

    # Create mock phase
    phase = Phase(
        name="Database Layer",
        goal="Implement database models and migrations",
        tasks=[task1, task2],
        risks=["Schema changes may require migration"],
        success_criteria=["All models created", "Tests passing"],
        total_hours=7.5,
    )

    # Create mock spec
    spec = TechnicalSpec(
        feature_name="User Management System",
        feature_type="crud",
        complexity="medium",
        summary="Implement user management with CRUD operations",
        business_value="Enable user administration",
        phases=[phase],
        total_hours=7.5,
        total_days=0.9,
        confidence=0.88,
        metadata={"created_at": datetime.now().isoformat()},
    )

    return spec


@pytest.fixture
def workflow(mock_ai_service):
    """Create SpecWorkflow instance for testing."""
    return SpecWorkflow(mock_ai_service, velocity_hours_per_day=6.0)


class TestSpecWorkflow:
    """Test SpecWorkflow class."""

    def test_initialization(self, workflow):
        """Test workflow initialization."""
        assert workflow.ai_service is not None
        assert workflow.spec_generator is not None
        assert workflow.roadmap_editor is not None
        assert workflow.velocity_hours_per_day == 6.0

    def test_calculate_delivery_estimate_high_confidence(self, workflow):
        """Test delivery estimate calculation with high confidence (90%+)."""
        # High confidence should get 10% buffer
        estimate = workflow._calculate_delivery_estimate(24.0, 0.95)

        assert estimate.total_hours == 24.0
        assert estimate.total_days == 3.0  # 24 / 8
        assert estimate.buffer_percentage == 10
        assert estimate.buffered_hours == 26.4  # 24 * 1.1
        assert estimate.buffered_days == 4.4  # 26.4 / 6.0 velocity
        assert estimate.confidence == 0.95

        # Check delivery date is in future
        delivery_date = datetime.strptime(estimate.delivery_date, "%Y-%m-%d")
        assert delivery_date > datetime.now()

    def test_calculate_delivery_estimate_medium_confidence(self, workflow):
        """Test delivery estimate calculation with medium confidence (70-90%)."""
        # Medium confidence should get 15% buffer
        estimate = workflow._calculate_delivery_estimate(20.0, 0.80)

        assert estimate.total_hours == 20.0
        assert estimate.buffer_percentage == 15
        assert estimate.buffered_hours == 23.0  # 20 * 1.15
        assert estimate.buffered_days == 3.8  # 23.0 / 6.0 velocity (rounded)

    def test_calculate_delivery_estimate_low_confidence(self, workflow):
        """Test delivery estimate calculation with low confidence (<70%)."""
        # Low confidence should get 20% buffer
        estimate = workflow._calculate_delivery_estimate(15.0, 0.60)

        assert estimate.total_hours == 15.0
        assert estimate.buffer_percentage == 20
        assert estimate.buffered_hours == 18.0  # 15 * 1.2
        assert estimate.buffered_days == 3.0  # 18.0 / 6.0 velocity

    def test_slugify(self, workflow):
        """Test slugify method."""
        assert workflow._slugify("Email Notifications System") == "email-notifications-system"
        assert workflow._slugify("User Authentication") == "user-authentication"
        assert workflow._slugify("API v2.0 - New Features") == "api-v20-new-features"
        assert workflow._slugify("  Spaces   Around  ") == "spaces-around"
        assert workflow._slugify("Special!@#$%Characters") == "specialcharacters"

    def test_generate_and_review_spec(self, workflow, mock_spec, tmp_path):
        """Test spec generation and review workflow."""
        # Mock spec generator
        workflow.spec_generator.generate_spec_from_user_story = Mock(return_value=mock_spec)
        workflow.spec_generator.render_spec_to_markdown = Mock(return_value="# Test Spec")

        # Use tmp_path for file operations
        with patch("coffee_maker.cli.spec_workflow.Path") as mock_path_class:
            # Make Path("docs") return tmp_path
            mock_path_class.return_value = tmp_path

            # Generate spec
            result = workflow.generate_and_review_spec(
                user_story="As a user, I want to manage users",
                feature_type="crud",
                complexity="medium",
                user_story_id="US-016",
            )

            # Verify result
            assert isinstance(result, SpecReviewResult)
            assert result.spec == mock_spec
            assert result.markdown == "# Test Spec"
            assert result.summary["total_hours"] == 7.5
            assert result.summary["phase_count"] == 1
            assert result.summary["task_count"] == 2
            assert result.approved is False  # Not approved yet

            # Verify delivery estimate
            assert "delivery_date" in result.delivery_estimate
            assert "buffered_hours" in result.delivery_estimate
            assert "confidence" in result.delivery_estimate

            # Verify spec was saved
            assert result.spec_path.name == "US-016_TECHNICAL_SPEC.md"

    def test_format_spec_summary(self, workflow, mock_spec):
        """Test spec summary formatting."""
        result = SpecReviewResult(
            spec=mock_spec,
            spec_path=Path("docs/TEST_SPEC.md"),
            markdown="# Test",
            summary={
                "total_hours": 7.5,
                "total_days": 0.9,
                "phase_count": 1,
                "task_count": 2,
                "confidence": 0.88,
            },
            delivery_estimate={
                "total_hours": 7.5,
                "total_days": 0.9,
                "buffer_percentage": 15,
                "buffered_hours": 8.6,
                "buffered_days": 1.4,
                "delivery_date": "2025-10-20",
                "confidence": 0.88,
            },
            approved=False,
        )

        summary = workflow.format_spec_summary(result)

        assert "Specification complete!" in summary
        assert "7.5 hours" in summary
        assert "0.9 days" in summary
        assert "Phases: 1" in summary
        assert "Tasks: 2" in summary
        assert "88%" in summary
        assert "2025-10-20" in summary

    def test_format_roadmap_update_example(self, workflow, mock_spec):
        """Test ROADMAP update example formatting."""
        result = SpecReviewResult(
            spec=mock_spec,
            spec_path=Path("docs/US-016_TECHNICAL_SPEC.md"),
            markdown="# Test",
            summary={"total_hours": 7.5, "total_days": 0.9, "phase_count": 1, "task_count": 2, "confidence": 0.88},
            delivery_estimate={
                "total_hours": 7.5,
                "total_days": 0.9,
                "buffer_percentage": 15,
                "buffered_hours": 8.6,
                "buffered_days": 1.4,
                "delivery_date": "2025-10-20",
                "confidence": 0.88,
            },
            approved=False,
        )

        example = workflow.format_roadmap_update_example(result, "US-016")

        assert "US-016" in example
        assert "READY TO IMPLEMENT" in example
        assert "8.6 hours" in example
        assert "1.4 days" in example
        assert "docs/US-016_TECHNICAL_SPEC.md" in example
        assert "88%" in example
        assert "2025-10-20" in example

    @patch("coffee_maker.cli.spec_workflow.ROADMAP_PATH")
    def test_update_roadmap_with_spec(self, mock_roadmap_path, workflow, mock_spec):
        """Test ROADMAP update with spec reference."""
        # Mock ROADMAP content
        roadmap_content = """
# ROADMAP

## US-016 - User Management System

**As a**: Admin
**I want**: User management

---
"""

        mock_roadmap_path.read_text.return_value = roadmap_content
        mock_roadmap_path.write_text = Mock()

        # Create result
        result = SpecReviewResult(
            spec=mock_spec,
            spec_path=Path("docs/US-016_TECHNICAL_SPEC.md"),
            markdown="# Test",
            summary={"total_hours": 7.5, "total_days": 0.9, "phase_count": 1, "task_count": 2, "confidence": 0.88},
            delivery_estimate={
                "total_hours": 7.5,
                "total_days": 0.9,
                "buffer_percentage": 15,
                "buffered_hours": 8.6,
                "buffered_days": 1.4,
                "delivery_date": "2025-10-20",
                "confidence": 0.88,
            },
            approved=False,
        )

        # Update ROADMAP
        workflow._update_roadmap_with_spec("US-016", result)

        # Verify write was called
        mock_roadmap_path.write_text.assert_called_once()

        # Get written content
        written_content = mock_roadmap_path.write_text.call_args[0][0]

        # Verify spec reference was added
        assert "READY TO IMPLEMENT" in written_content
        assert "8.6 hours" in written_content
        assert "docs/US-016_TECHNICAL_SPEC.md" in written_content
        assert "88%" in written_content

    def test_approve_spec(self, workflow, mock_spec):
        """Test spec approval."""
        result = SpecReviewResult(
            spec=mock_spec,
            spec_path=Path("docs/US-016_TECHNICAL_SPEC.md"),
            markdown="# Test",
            summary={"total_hours": 7.5, "total_days": 0.9, "phase_count": 1, "task_count": 2, "confidence": 0.88},
            delivery_estimate={
                "total_hours": 7.5,
                "total_days": 0.9,
                "buffer_percentage": 15,
                "buffered_hours": 8.6,
                "buffered_days": 1.4,
                "delivery_date": "2025-10-20",
                "confidence": 0.88,
            },
            approved=False,
        )

        # Mock ROADMAP update
        workflow._update_roadmap_with_spec = Mock()

        # Approve spec
        success = workflow.approve_spec(result, "US-016")

        assert success is True
        assert result.approved is True
        workflow._update_roadmap_with_spec.assert_called_once_with("US-016", result)

    def test_reject_spec(self, workflow, mock_spec):
        """Test spec rejection."""
        result = SpecReviewResult(
            spec=mock_spec,
            spec_path=Path("docs/US-016_TECHNICAL_SPEC.md"),
            markdown="# Test",
            summary={"total_hours": 7.5, "total_days": 0.9, "phase_count": 1, "task_count": 2, "confidence": 0.88},
            delivery_estimate={
                "total_hours": 7.5,
                "total_days": 0.9,
                "buffer_percentage": 15,
                "buffered_hours": 8.6,
                "buffered_days": 1.4,
                "delivery_date": "2025-10-20",
                "confidence": 0.88,
            },
            approved=False,
        )

        # Reject spec
        success = workflow.reject_spec(result, "Scope too large")

        assert success is True
        assert result.approved is False
        assert result.rejection_reason == "Scope too large"


class TestDeliveryEstimate:
    """Test DeliveryEstimate dataclass."""

    def test_delivery_estimate_creation(self):
        """Test DeliveryEstimate creation."""
        estimate = DeliveryEstimate(
            total_hours=24.0,
            total_days=3.0,
            buffer_percentage=15,
            buffered_hours=27.6,
            buffered_days=3.5,
            delivery_date="2025-10-20",
            confidence=0.85,
        )

        assert estimate.total_hours == 24.0
        assert estimate.total_days == 3.0
        assert estimate.buffer_percentage == 15
        assert estimate.buffered_hours == 27.6
        assert estimate.buffered_days == 3.5
        assert estimate.delivery_date == "2025-10-20"
        assert estimate.confidence == 0.85


class TestSpecReviewResult:
    """Test SpecReviewResult dataclass."""

    def test_spec_review_result_creation(self, mock_spec):
        """Test SpecReviewResult creation."""
        result = SpecReviewResult(
            spec=mock_spec,
            spec_path=Path("docs/TEST_SPEC.md"),
            markdown="# Test Spec",
            summary={"total_hours": 10.0},
            delivery_estimate={"delivery_date": "2025-10-20"},
            approved=True,
            rejection_reason=None,
        )

        assert result.spec == mock_spec
        assert result.spec_path == Path("docs/TEST_SPEC.md")
        assert result.markdown == "# Test Spec"
        assert result.summary["total_hours"] == 10.0
        assert result.approved is True
        assert result.rejection_reason is None

    def test_spec_review_result_rejection(self, mock_spec):
        """Test SpecReviewResult with rejection."""
        result = SpecReviewResult(
            spec=mock_spec,
            spec_path=Path("docs/TEST_SPEC.md"),
            markdown="# Test Spec",
            summary={"total_hours": 10.0},
            delivery_estimate={"delivery_date": "2025-10-20"},
            approved=False,
            rejection_reason="Needs more detail",
        )

        assert result.approved is False
        assert result.rejection_reason == "Needs more detail"
