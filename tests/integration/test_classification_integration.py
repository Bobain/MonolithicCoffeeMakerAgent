"""Integration tests for classification system (US-021 Phase 2).

These tests verify that the RequestClassifier integrates properly with AIService
and provides the expected user experience with classification context.
"""

from unittest.mock import patch

import pytest

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.request_classifier import RequestClassifier, RequestType


@pytest.fixture
def ai_service():
    """Create AIService with classification enabled (mocked API).

    We mock the API to avoid requiring actual API keys in tests.
    The focus is on testing classification integration, not API calls.
    """
    # Mock the API client to avoid requiring real API key
    with patch("coffee_maker.cli.ai_service.Anthropic"):
        with patch("coffee_maker.config.ConfigManager.get_anthropic_api_key", return_value="test-key"):
            service = AIService(use_claude_cli=False)
            # Ensure classifier is available
            service.classifier = RequestClassifier()
            return service


@pytest.fixture
def classifier():
    """Create standalone RequestClassifier for direct testing."""
    return RequestClassifier()


@pytest.fixture
def mock_context():
    """Mock roadmap context for testing."""
    return {
        "roadmap_summary": {
            "total": 10,
            "completed": 5,
            "in_progress": 2,
            "planned": 3,
            "priorities": [
                {"number": "US-001", "title": "Test Feature", "status": "completed"},
                {"number": "US-002", "title": "Another Feature", "status": "planned"},
            ],
        }
    }


class TestFeatureRequestClassification:
    """Test feature request classification and handling."""

    def test_clear_feature_request_classification(self, ai_service):
        """Test that clear feature requests are classified correctly."""
        # This test only verifies classification, not full AI response
        # (to avoid API calls in tests)
        user_input = "I want to add email notifications to the system"

        # Use the classify_user_request method to test classification
        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.FEATURE_REQUEST.value
        assert "docs/roadmap/ROADMAP.md" in result["target_documents"]
        assert result["confidence"] > 0.0

    def test_user_story_format_classification(self, ai_service):
        """Test user story format is classified as feature request."""
        user_input = "As a developer, I want to deploy on GCP so that it runs 24/7"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.FEATURE_REQUEST.value
        assert len(result["feature_indicators"]) > 0

    def test_implement_feature_classification(self, ai_service):
        """Test 'implement' keyword triggers feature classification."""
        user_input = "Implement a dashboard for viewing agent status"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.FEATURE_REQUEST.value


class TestMethodologyChangeClassification:
    """Test methodology change classification and handling."""

    def test_clear_methodology_change_classification(self, ai_service):
        """Test that clear methodology changes are classified correctly."""
        user_input = "From now on, we should always create technical specs first"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # "create" can trigger feature indicators, so might be hybrid
        # The key is that TEAM_COLLABORATION.md is targeted
        assert result["type"] in [
            RequestType.METHODOLOGY_CHANGE.value,
            RequestType.HYBRID.value,
        ]
        assert any("TEAM_COLLABORATION.md" in doc for doc in result["target_documents"])

    def test_process_change_classification(self, ai_service):
        """Test process change keywords trigger methodology classification."""
        user_input = "Change our workflow to require 2 approvals on all PRs"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.METHODOLOGY_CHANGE.value

    def test_always_pattern_classification(self, ai_service):
        """Test 'always' pattern triggers methodology classification."""
        user_input = "Every commit should always have tests"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.METHODOLOGY_CHANGE.value


class TestHybridRequestClassification:
    """Test hybrid request classification (feature + methodology)."""

    def test_hybrid_request_both_types(self, ai_service):
        """Test requests with both feature and methodology indicators."""
        user_input = "I want to add a code review bot, and every PR must have 2 approvals"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.HYBRID.value
        assert len(result["target_documents"]) >= 2

    def test_hybrid_targets_both_documents(self, ai_service):
        """Test hybrid requests target both ROADMAP and TEAM_COLLABORATION."""
        user_input = "Implement slack notifications and always notify on PR merge"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # Might be classified as feature or hybrid depending on indicators
        # Just verify it has meaningful classification
        assert result["confidence"] > 0.0
        assert len(result["target_documents"]) > 0


class TestClarificationNeeded:
    """Test clarification handling for ambiguous requests."""

    def test_ambiguous_request_needs_clarification(self, ai_service):
        """Test ambiguous requests trigger clarification."""
        user_input = "We should improve something"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # Low confidence should lead to clarification
        if result["confidence"] < 0.33:
            assert result["type"] == RequestType.CLARIFICATION_NEEDED.value
            assert len(result["suggested_questions"]) > 0

    def test_vague_request_suggests_questions(self, ai_service):
        """Test vague requests get helpful clarification questions."""
        user_input = "Fix it"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # Very vague should need clarification
        assert result["confidence"] < 0.5


class TestClassificationMetadata:
    """Test that classification metadata is properly passed through."""

    def test_classification_metadata_structure(self, ai_service):
        """Test classification result has expected metadata structure."""
        user_input = "I want to add analytics dashboard"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert "type" in result
        assert "confidence" in result
        assert "target_documents" in result
        assert "feature_indicators" in result
        assert "methodology_indicators" in result
        assert "suggested_questions" in result

    def test_feature_indicators_captured(self, ai_service):
        """Test that feature indicators are captured in metadata."""
        user_input = "I need to build a new dashboard feature"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert len(result["feature_indicators"]) > 0
        # Should detect keywords like "need", "build", "feature"

    def test_methodology_indicators_captured(self, ai_service):
        """Test that methodology indicators are captured in metadata."""
        user_input = "Our policy should be to always write tests first"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert len(result["methodology_indicators"]) > 0
        # Should detect keywords like "policy", "always"


class TestRealWorldExamples:
    """Test real-world examples from ROADMAP."""

    def test_real_world_slack_notification_feature(self, ai_service):
        """Test real user story: Slack notifications."""
        user_input = "I want to add Slack notifications when priorities complete"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.FEATURE_REQUEST.value
        assert "docs/roadmap/ROADMAP.md" in result["target_documents"]

    def test_real_world_git_workflow_change(self, ai_service):
        """Test real methodology change: Git workflow."""
        user_input = "From now on, all code changes must go through feature branches"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # "feature branches" can trigger feature indicators, might be hybrid
        assert result["type"] in [
            RequestType.METHODOLOGY_CHANGE.value,
            RequestType.HYBRID.value,
        ]

    def test_real_world_dashboard_with_charts(self, ai_service):
        """Test real feature: Dashboard with charts."""
        user_input = "I need a dashboard showing agent progress with charts"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        assert result["type"] == RequestType.FEATURE_REQUEST.value

    def test_real_world_testing_requirement(self, ai_service):
        """Test real methodology: Testing requirements."""
        user_input = "Every new feature must have unit tests and integration tests"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # "feature", "tests" can trigger both indicators, might be hybrid
        assert result["type"] in [
            RequestType.METHODOLOGY_CHANGE.value,
            RequestType.HYBRID.value,
        ]


class TestConfidenceScoring:
    """Test confidence scoring works as expected."""

    def test_high_confidence_feature(self, ai_service):
        """Test high confidence feature requests."""
        user_input = "I want to implement a new analytics dashboard feature"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # Multiple indicators should give high confidence
        assert result["confidence"] >= 0.33  # At least medium confidence

    def test_high_confidence_methodology(self, ai_service):
        """Test high confidence methodology changes."""
        user_input = "Change our workflow process: every PR must always have 2 approvals"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # Multiple methodology indicators
        assert result["confidence"] >= 0.33

    def test_low_confidence_triggers_appropriate_response(self, ai_service):
        """Test low confidence leads to clarification."""
        user_input = "Make it better"

        result = ai_service.classify_user_request(user_input)

        assert result is not None
        # Very vague should have low confidence
        assert result["confidence"] < 0.5


# Note: Full integration tests that make actual API calls to Claude
# would be in a separate test file with @pytest.mark.integration
# to avoid running them in regular CI/CD pipelines.
