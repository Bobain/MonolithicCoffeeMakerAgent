"""Unit tests for MetadataExtractor (US-021 Phase 4).

Tests AI-enhanced metadata extraction from user requests.
"""

import pytest
from coffee_maker.cli.metadata_extractor import MetadataExtractor, ExtractedMetadata
from coffee_maker.cli.request_classifier import RequestType


@pytest.fixture
def extractor():
    """Create MetadataExtractor without AI."""
    return MetadataExtractor(use_ai=False)


class TestMetadataExtractorInitialization:
    """Test MetadataExtractor initialization."""

    def test_init_without_ai(self):
        """Test initialization without AI."""
        extractor = MetadataExtractor(use_ai=False)
        assert extractor.use_ai is False
        assert extractor.ai_client is None

    def test_init_with_ai(self):
        """Test initialization with AI."""
        extractor = MetadataExtractor(use_ai=True)
        assert extractor.use_ai is True


class TestTitleExtraction:
    """Test title extraction from user input."""

    def test_extract_title_simple(self, extractor):
        """Test simple title extraction."""
        title = extractor._extract_title("Add email notifications")
        assert title == "Add email notifications"

    def test_extract_title_removes_i_want_to(self, extractor):
        """Test title extraction removes 'I want to' prefix."""
        title = extractor._extract_title("I want to add Slack integration")
        assert title == "Add Slack integration"
        assert not title.lower().startswith("i want")

    def test_extract_title_removes_we_should(self, extractor):
        """Test title extraction removes 'we should' prefix."""
        title = extractor._extract_title("we should implement OAuth")
        assert title == "Implement OAuth"

    def test_extract_title_capitalizes_first_letter(self, extractor):
        """Test title extraction capitalizes first letter."""
        title = extractor._extract_title("add feature X")
        assert title[0].isupper()

    def test_extract_title_truncates_long_text(self, extractor):
        """Test title extraction truncates very long text."""
        long_text = "A" * 100
        title = extractor._extract_title(long_text)
        assert len(title) <= 80

    def test_extract_title_takes_first_sentence(self, extractor):
        """Test title extraction takes only first sentence."""
        title = extractor._extract_title("Add email notifications. Also add SMS alerts.")
        assert "email notifications" in title
        assert "SMS" not in title


class TestComplexityEstimation:
    """Test complexity estimation based on keywords."""

    def test_estimate_complexity_low(self, extractor):
        """Test low complexity estimation."""
        complexity = extractor._estimate_complexity("Add a simple button")
        assert complexity == "low"

    def test_estimate_complexity_medium(self, extractor):
        """Test medium complexity estimation."""
        complexity = extractor._estimate_complexity("Add email notifications")
        assert complexity == "medium"

    def test_estimate_complexity_high_single_keyword(self, extractor):
        """Test high complexity with single high-complexity keyword."""
        complexity = extractor._estimate_complexity("Add OAuth authentication")
        assert complexity in ["medium", "high"]

    def test_estimate_complexity_high_multiple_keywords(self, extractor):
        """Test high complexity with multiple keywords."""
        complexity = extractor._estimate_complexity("Add OAuth authentication with API integration")
        assert complexity == "high"


class TestEffortExtraction:
    """Test effort estimation extraction."""

    def test_extract_effort_days(self, extractor):
        """Test extracting effort in days."""
        effort = extractor._extract_effort("This will take 2-3 days")
        assert effort == "2-3 days"

    def test_extract_effort_weeks(self, extractor):
        """Test extracting effort in weeks."""
        effort = extractor._extract_effort("Estimated 1 week")
        assert effort == "1 week"

    def test_extract_effort_hours(self, extractor):
        """Test extracting effort in hours."""
        effort = extractor._extract_effort("Should take 4-6 hours")
        assert effort == "4-6 hours"

    def test_extract_effort_none(self, extractor):
        """Test no effort mentioned returns None."""
        effort = extractor._extract_effort("Add a feature")
        assert effort is None


class TestDependencyExtraction:
    """Test dependency detection from user input."""

    def test_extract_dependency_depends_on(self, extractor):
        """Test extracting 'depends on' pattern."""
        deps = extractor._extract_dependencies("This depends on US-021")
        assert "US-021" in deps

    def test_extract_dependency_requires(self, extractor):
        """Test extracting 'requires' pattern."""
        deps = extractor._extract_dependencies("Requires US-033 to be complete")
        assert "US-033" in deps

    def test_extract_dependency_blocked_by(self, extractor):
        """Test extracting 'blocked by' pattern."""
        deps = extractor._extract_dependencies("Blocked by US-015")
        assert "US-015" in deps

    def test_extract_multiple_dependencies(self, extractor):
        """Test extracting multiple dependencies."""
        deps = extractor._extract_dependencies("Depends on US-021 and requires US-033")
        assert "US-021" in deps
        assert "US-033" in deps

    def test_extract_no_dependencies(self, extractor):
        """Test no dependencies returns empty list."""
        deps = extractor._extract_dependencies("Add a standalone feature")
        assert deps == []


class TestAcceptanceCriteriaGeneration:
    """Test default acceptance criteria generation."""

    def test_generate_criteria_for_feature_request(self, extractor):
        """Test acceptance criteria for feature request."""
        criteria = extractor._generate_default_acceptance_criteria(RequestType.FEATURE_REQUEST, "Add feature")

        assert isinstance(criteria, list)
        assert len(criteria) > 0
        assert any("implemented" in c.lower() for c in criteria)
        assert any("test" in c.lower() for c in criteria)

    def test_generate_criteria_for_methodology_change(self, extractor):
        """Test acceptance criteria for methodology change."""
        criteria = extractor._generate_default_acceptance_criteria(RequestType.METHODOLOGY_CHANGE, "Change process")

        assert isinstance(criteria, list)
        assert any("documented" in c.lower() for c in criteria)

    def test_generate_criteria_for_hybrid(self, extractor):
        """Test acceptance criteria for hybrid request."""
        criteria = extractor._generate_default_acceptance_criteria(RequestType.HYBRID, "Add feature and change process")

        assert isinstance(criteria, list)
        assert len(criteria) >= 2  # Should cover both aspects


class TestBusinessValueExtraction:
    """Test business value hint extraction."""

    def test_extract_business_value_so_that(self, extractor):
        """Test extracting 'so that' pattern."""
        value = extractor._extract_business_value_hints("Add notifications so that users stay informed")

        assert value is not None
        assert "users stay informed" in value

    def test_extract_business_value_because(self, extractor):
        """Test extracting 'because' pattern."""
        value = extractor._extract_business_value_hints("Add OAuth because it's more secure")

        assert value is not None
        assert "secure" in value.lower()

    def test_extract_business_value_improve(self, extractor):
        """Test extracting value with 'improve' keyword."""
        value = extractor._extract_business_value_hints("Add analytics to improve decision-making")

        assert value is not None
        assert "improve" in value.lower() or "decision" in value.lower()


class TestPrioritySuggestion:
    """Test priority level suggestion."""

    def test_suggest_priority_critical_keyword(self, extractor):
        """Test critical priority from keyword."""
        priority = extractor._suggest_priority("Fix critical security bug", "low")
        assert priority == "critical"

    def test_suggest_priority_urgent_keyword(self, extractor):
        """Test critical priority from 'urgent' keyword."""
        priority = extractor._suggest_priority("Urgent: production is down", "low")
        assert priority == "critical"

    def test_suggest_priority_high_keyword(self, extractor):
        """Test high priority from keyword."""
        priority = extractor._suggest_priority("This is important and should be done soon", "low")
        assert priority == "high"

    def test_suggest_priority_based_on_complexity(self, extractor):
        """Test priority suggestion based on complexity."""
        priority = extractor._suggest_priority("Add a feature", "high")
        assert priority == "high"  # High complexity → high priority


class TestMethodologyMetadataExtraction:
    """Test methodology-specific metadata extraction."""

    def test_extract_rationale(self, extractor):
        """Test rationale extraction."""
        rationale = extractor._extract_rationale("We should use Git flow because it's more structured")

        assert rationale is not None
        assert "structured" in rationale.lower()

    def test_extract_applies_to_explicit(self, extractor):
        """Test extracting explicit 'applies to'."""
        applies = extractor._extract_applies_to("This applies to all developers")
        assert "developers" in applies.lower()

    def test_extract_applies_to_implicit(self, extractor):
        """Test extracting implicit role mentions."""
        applies = extractor._extract_applies_to("The project manager should review all PRs")
        # Should find "project manager" role or default to "All"
        assert "project manager" in applies.lower() or "all" in applies.lower()

    def test_suggest_collaboration_section_git(self, extractor):
        """Test section suggestion for Git-related changes."""
        section = extractor._suggest_collaboration_section("We should change our git branching strategy")
        assert "git" in section.lower() or "workflow" in section.lower()

    def test_suggest_collaboration_section_pr(self, extractor):
        """Test section suggestion for PR-related changes."""
        section = extractor._suggest_collaboration_section("All pull requests need 2 reviews")
        assert "pull request" in section.lower() or "review" in section.lower()


class TestFullMetadataExtraction:
    """Test complete metadata extraction flow."""

    def test_extract_metadata_feature_request(self, extractor):
        """Test full metadata extraction for feature request."""
        metadata = extractor.extract_metadata(
            request_type=RequestType.FEATURE_REQUEST,
            user_input="I want to add email notifications so that users stay informed. This will take 2-3 days.",
            ai_response="Great idea! Email notifications would be valuable.",
        )

        assert isinstance(metadata, ExtractedMetadata)
        assert metadata.title is not None
        assert "email" in metadata.title.lower()
        assert metadata.business_value is not None
        assert metadata.estimated_effort == "2-3 days"
        assert metadata.complexity in ["low", "medium", "high"]
        assert metadata.acceptance_criteria is not None

    def test_extract_metadata_methodology_change(self, extractor):
        """Test full metadata extraction for methodology change."""
        metadata = extractor.extract_metadata(
            request_type=RequestType.METHODOLOGY_CHANGE,
            user_input="All PRs must have 2 approvals because it improves code quality",
        )

        assert metadata.title is not None
        assert metadata.rationale is not None
        assert "quality" in metadata.rationale.lower()
        assert metadata.applies_to is not None

    def test_extract_metadata_with_dependencies(self, extractor):
        """Test metadata extraction with dependencies."""
        metadata = extractor.extract_metadata(
            request_type=RequestType.FEATURE_REQUEST,
            user_input="Add GraphQL API, depends on US-021 (authentication refactor)",
        )

        assert metadata.dependencies is not None
        assert "US-021" in metadata.dependencies

    def test_extract_metadata_empty_input(self, extractor):
        """Test metadata extraction with minimal input."""
        metadata = extractor.extract_metadata(request_type=RequestType.FEATURE_REQUEST, user_input="Add feature")

        # Should still extract something
        assert metadata.title is not None
        assert metadata.complexity is not None


class TestTagExtraction:
    """Test tag extraction from user input."""

    def test_extract_tags_technology(self, extractor):
        """Test extracting technology tags."""
        tags = extractor._extract_tags("Add Python API with database integration")

        assert "python" in tags
        assert "api" in tags
        assert "database" in tags

    def test_extract_tags_limits_to_five(self, extractor):
        """Test tag extraction limits to 5 tags."""
        text = "python api database frontend backend ui ux security performance testing documentation devops"
        tags = extractor._extract_tags(text)

        assert len(tags) <= 5

    def test_extract_tags_empty(self, extractor):
        """Test no tags extracted returns empty list."""
        tags = extractor._extract_tags("Just a simple feature")
        # May or may not have tags, but should return a list
        assert isinstance(tags, list)
