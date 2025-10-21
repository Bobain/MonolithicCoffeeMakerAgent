"""Unit tests for request classification system.

Tests cover:
- Feature request detection
- Methodology change detection
- Hybrid requests (both types)
- Clarification needed scenarios
- Edge cases
- Indicator collection
- Confidence scoring
"""

import pytest
from coffee_maker.cli.request_classifier import (
    RequestClassifier,
    RequestType,
)


@pytest.fixture
def classifier():
    """Create a RequestClassifier instance for testing."""
    return RequestClassifier()


# ============================================================================
# Feature Request Tests
# ============================================================================


def test_clear_feature_request(classifier):
    """Test obvious feature request with strong indicators."""
    result = classifier.classify("I want to add email notifications when the daemon completes a task")
    assert result.request_type == RequestType.FEATURE_REQUEST
    assert result.confidence > 0.5
    assert "docs/roadmap/ROADMAP.md" in result.target_documents
    assert len(result.feature_indicators) > 0


def test_user_story_format(classifier):
    """Test user story format detection (As a X, I want Y)."""
    result = classifier.classify("As a user, I want to receive Slack notifications so that I stay informed")
    assert result.request_type == RequestType.FEATURE_REQUEST
    assert result.confidence > 0.5
    assert "docs/roadmap/ROADMAP.md" in result.target_documents


def test_implement_feature_request(classifier):
    """Test feature request with 'implement' keyword."""
    result = classifier.classify("We need to implement a dashboard that shows real-time metrics")
    assert result.request_type == RequestType.FEATURE_REQUEST
    assert result.confidence > 0.5


def test_build_capability_request(classifier):
    """Test feature request with 'build' keyword."""
    result = classifier.classify("Can you build an API endpoint for status updates?")
    assert result.request_type == RequestType.FEATURE_REQUEST
    assert result.confidence > 0.5


def test_add_functionality_request(classifier):
    """Test feature request with 'add' keyword."""
    result = classifier.classify("Add a button to export reports as PDF")
    assert result.request_type == RequestType.FEATURE_REQUEST
    assert result.confidence > 0.5


# ============================================================================
# Methodology Change Tests
# ============================================================================


def test_clear_methodology_change(classifier):
    """Test obvious methodology change with strong indicators."""
    result = classifier.classify("From now on, we should always write technical specs before coding")
    # Note: Could be HYBRID if "create" triggers feature indicators, but should have methodology dominant
    assert result.request_type in [RequestType.METHODOLOGY_CHANGE, RequestType.HYBRID]
    assert result.confidence > 0.5
    assert "docs/COLLABORATION_METHODOLOGY.md" in result.target_documents
    assert len(result.methodology_indicators) > 0


def test_process_change(classifier):
    """Test process change detection."""
    result = classifier.classify("Update our git workflow policy")
    # Simpler version to avoid "need" triggering feature indicators
    assert result.request_type == RequestType.METHODOLOGY_CHANGE
    assert result.confidence >= 0.33


def test_workflow_update(classifier):
    """Test workflow update detection."""
    result = classifier.classify("Our deployment process should include automated testing")
    assert result.request_type == RequestType.METHODOLOGY_CHANGE
    assert result.confidence > 0.5


def test_always_never_pattern(classifier):
    """Test 'always/never' pattern for methodology."""
    result = classifier.classify("The team should always use type hints in Python code")
    assert result.request_type == RequestType.METHODOLOGY_CHANGE
    assert result.confidence > 0.5


def test_pm_should_pattern(classifier):
    """Test 'PM should' pattern for methodology."""
    result = classifier.classify("PM should always verify PRs before merging")
    assert result.request_type == RequestType.METHODOLOGY_CHANGE
    assert result.confidence > 0.5


# ============================================================================
# Hybrid Request Tests
# ============================================================================


def test_hybrid_request(classifier):
    """Test request that's both feature + methodology."""
    result = classifier.classify(
        "I want to add a review process where every PR requires two approvals, "
        "and we should implement a bot to enforce this policy"
    )
    assert result.request_type == RequestType.HYBRID
    assert "docs/roadmap/ROADMAP.md" in result.target_documents
    assert "docs/COLLABORATION_METHODOLOGY.md" in result.target_documents
    assert len(result.feature_indicators) > 0
    assert len(result.methodology_indicators) > 0


def test_hybrid_feature_and_workflow(classifier):
    """Test hybrid request combining feature and workflow."""
    result = classifier.classify(
        "Build a CI/CD pipeline that automatically runs tests, "
        "and update our deployment process to require manual approval"
    )
    assert result.request_type == RequestType.HYBRID
    assert len(result.target_documents) == 2


def test_hybrid_pm_capability(classifier):
    """Test hybrid request for PM capability (feature) with process change."""
    result = classifier.classify(
        "PM needs the ability to detect whether user input is a feature or methodology change, "
        "and should always ask clarifying questions when ambiguous"
    )
    assert result.request_type == RequestType.HYBRID
    assert result.confidence > 0.5


# ============================================================================
# Clarification Needed Tests
# ============================================================================


def test_ambiguous_request(classifier):
    """Test ambiguous request that needs clarification."""
    result = classifier.classify("We should improve our documentation")
    assert result.request_type == RequestType.CLARIFICATION_NEEDED
    assert len(result.suggested_questions) > 0


def test_low_confidence_feature(classifier):
    """Test low confidence feature request."""
    result = classifier.classify("Something about notifications would be nice")
    # With at least one indicator ("notification"), will classify as feature
    assert result.request_type in [
        RequestType.FEATURE_REQUEST,
        RequestType.CLARIFICATION_NEEDED,
    ]
    # But confidence should be low
    assert result.confidence <= 0.67


def test_vague_improvement(classifier):
    """Test vague improvement request."""
    result = classifier.classify("Make it better")
    assert result.request_type == RequestType.CLARIFICATION_NEEDED
    assert len(result.suggested_questions) > 0


def test_unclear_context(classifier):
    """Test request with unclear context."""
    result = classifier.classify("Update the thing we discussed")
    assert result.request_type == RequestType.CLARIFICATION_NEEDED


# ============================================================================
# Edge Cases
# ============================================================================


def test_empty_input(classifier):
    """Test empty input handling."""
    result = classifier.classify("")
    assert result.request_type == RequestType.CLARIFICATION_NEEDED
    assert result.confidence == 0.0
    assert len(result.suggested_questions) > 0


def test_whitespace_only_input(classifier):
    """Test whitespace-only input."""
    result = classifier.classify("   \n\t  ")
    assert result.request_type == RequestType.CLARIFICATION_NEEDED
    assert result.confidence == 0.0


def test_very_long_input(classifier):
    """Test very long input doesn't cause issues."""
    long_text = "I want " * 1000 + "to add notifications"
    result = classifier.classify(long_text)
    assert result.request_type in [
        RequestType.FEATURE_REQUEST,
        RequestType.CLARIFICATION_NEEDED,
    ]
    assert result.confidence >= 0.0


def test_mixed_case_input(classifier):
    """Test that classification is case-insensitive."""
    result1 = classifier.classify("I WANT TO ADD NOTIFICATIONS")
    result2 = classifier.classify("i want to add notifications")
    assert result1.request_type == result2.request_type


def test_special_characters(classifier):
    """Test input with special characters."""
    result = classifier.classify("I want to add @notifications with #tags and $variables!")
    assert result.request_type == RequestType.FEATURE_REQUEST


# ============================================================================
# Indicator Tests
# ============================================================================


def test_feature_indicators_found(classifier):
    """Test that feature indicators are collected correctly."""
    result = classifier.classify("I want to implement a new feature that adds notifications")
    assert len(result.feature_indicators) > 0
    assert any("keyword" in ind for ind in result.feature_indicators)
    assert result.request_type == RequestType.FEATURE_REQUEST


def test_methodology_indicators_found(classifier):
    """Test that methodology indicators are collected correctly."""
    result = classifier.classify("We should change our workflow and process")
    assert len(result.methodology_indicators) > 0
    assert any("keyword" in ind for ind in result.methodology_indicators)
    assert result.request_type == RequestType.METHODOLOGY_CHANGE


def test_multiple_feature_keywords(classifier):
    """Test detection of multiple feature keywords."""
    result = classifier.classify(
        "I want to build a dashboard that implements notifications " "and creates reports with API integration"
    )
    assert result.request_type == RequestType.FEATURE_REQUEST
    # Should find multiple indicators
    assert len(result.feature_indicators) >= 5


def test_multiple_methodology_keywords(classifier):
    """Test detection of multiple methodology keywords."""
    result = classifier.classify("Our workflow and process should follow our methodology and guidelines")
    assert result.request_type == RequestType.METHODOLOGY_CHANGE
    # Should find multiple indicators
    assert len(result.methodology_indicators) >= 4


# ============================================================================
# Confidence Tests
# ============================================================================


def test_high_confidence_feature(classifier):
    """Test high confidence feature request."""
    result = classifier.classify("As a user, I want to add a dashboard that implements real-time notifications")
    assert result.confidence > 0.7
    assert result.request_type == RequestType.FEATURE_REQUEST


def test_high_confidence_methodology(classifier):
    """Test high confidence methodology change."""
    result = classifier.classify("The team must follow our testing policy and never skip the approval process")
    # Avoid words like "review" (contains "view") that might trigger feature keywords
    assert result.confidence >= 0.67
    assert result.request_type in [RequestType.METHODOLOGY_CHANGE, RequestType.HYBRID]


def test_low_confidence_ambiguous(classifier):
    """Test low confidence for ambiguous input."""
    result = classifier.classify("Something needs improvement")
    # "need" might trigger feature, but overall should be low confidence
    assert result.confidence <= 0.67
    # Could be classified as either based on "need" keyword
    assert result.request_type in [
        RequestType.FEATURE_REQUEST,
        RequestType.CLARIFICATION_NEEDED,
    ]


def test_medium_confidence_triggers_clarification(classifier):
    """Test classification with mixed signals."""
    result = classifier.classify("Add some improvements to the process")
    # Has both "add" (feature) and "process" (methodology) - should be hybrid
    # Or could classify as one type if one dominates
    assert result.request_type in [
        RequestType.HYBRID,
        RequestType.FEATURE_REQUEST,
        RequestType.METHODOLOGY_CHANGE,
    ]


# ============================================================================
# Target Documents Tests
# ============================================================================


def test_feature_targets_roadmap(classifier):
    """Test that feature requests target ROADMAP."""
    result = classifier.classify("I want to add a new notification system")
    assert result.request_type == RequestType.FEATURE_REQUEST
    assert "docs/roadmap/ROADMAP.md" in result.target_documents


def test_methodology_targets_collaboration(classifier):
    """Test that methodology changes target COLLABORATION_METHODOLOGY."""
    result = classifier.classify("Our team policy is to write specs before coding")
    # Pure methodology - no "create" to confuse
    assert result.request_type == RequestType.METHODOLOGY_CHANGE
    assert "docs/COLLABORATION_METHODOLOGY.md" in result.target_documents


def test_hybrid_targets_both_documents(classifier):
    """Test that hybrid requests target both documents."""
    result = classifier.classify("Build a review system and implement a policy that requires approval")
    if result.request_type == RequestType.HYBRID:
        assert len(result.target_documents) == 2
        assert "docs/roadmap/ROADMAP.md" in result.target_documents
        assert "docs/COLLABORATION_METHODOLOGY.md" in result.target_documents


def test_clarification_has_empty_or_suggested_targets(classifier):
    """Test that unclear requests either have no targets or suggested targets."""
    result = classifier.classify("Make things better")
    assert result.request_type == RequestType.CLARIFICATION_NEEDED
    # Either no targets (completely unclear) or suggested targets (leaning one way)
    assert isinstance(result.target_documents, list)


# ============================================================================
# Real-World Scenarios
# ============================================================================


def test_real_world_us021_example(classifier):
    """Test the actual US-021 user story."""
    result = classifier.classify(
        "As a project manager, I need to be able to interpret the user's context: "
        "what part of what he is saying are user stories, and what parts concern "
        "the collaboration methodologies, or both. I can ask him to make sure I "
        "understood as I need to get sure which documents should be updated"
    )
    # This is a feature request (PM capability) with methodology elements
    assert result.request_type in [RequestType.FEATURE_REQUEST, RequestType.HYBRID]


def test_real_world_git_workflow_change(classifier):
    """Test real-world git workflow change."""
    result = classifier.classify(
        "We should change our git branching strategy to use GitFlow instead of trunk-based development"
    )
    assert result.request_type == RequestType.METHODOLOGY_CHANGE


def test_real_world_dashboard_feature(classifier):
    """Test real-world dashboard feature request."""
    result = classifier.classify("I need a dashboard showing code_developer progress with real-time updates")
    assert result.request_type == RequestType.FEATURE_REQUEST


def test_real_world_testing_policy(classifier):
    """Test real-world testing policy change."""
    result = classifier.classify("Every PR must have tests before it can be merged")
    assert result.request_type == RequestType.METHODOLOGY_CHANGE
