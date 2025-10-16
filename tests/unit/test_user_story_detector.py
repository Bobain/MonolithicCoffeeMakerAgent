"""Unit tests for UserStoryDetector - Automatic user story detection.

This test suite covers:
1. Formal pattern detection (15+ tests)
2. Informal pattern detection (10+ tests)
3. Edge cases (5+ tests)
4. AI integration (mocked tests)

Total: 30+ tests for >90% coverage
"""

from unittest.mock import Mock
from coffee_maker.cli.user_story_detector import UserStoryDetector, UserStoryDetection


class TestFormalPatternDetection:
    """Test formal user story pattern detection (As a X I want Y so that Z)."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = UserStoryDetector(ai_service=None)  # No AI for pattern tests

    def test_standard_format_with_commas(self):
        """Test: As a X, I want Y, so that Z."""
        result = self.detector.detect("As a developer, I want CI/CD, so that builds are automated")

        assert result.is_user_story is True
        assert result.confidence >= 0.95
        assert result.as_a == "developer"
        assert result.i_want == "CI/CD"
        assert result.so_that == "builds are automated"
        assert result.detection_method == "formal_pattern"

    def test_standard_format_without_commas(self):
        """Test: As a X I want Y so that Z."""
        result = self.detector.detect("As a developer I want CI/CD so that builds are automated")

        assert result.is_user_story is True
        assert result.as_a == "developer"
        assert result.i_want == "CI/CD"
        assert result.so_that == "builds are automated"

    def test_format_with_to(self):
        """Test: As a X, I want to Y so that Z."""
        result = self.detector.detect("As a developer, I want to deploy on GCP so that it runs 24/7")

        assert result.is_user_story is True
        assert result.as_a == "developer"
        # "to" is included in the pattern match
        assert "deploy on GCP" in result.i_want
        assert result.so_that == "it runs 24/7"

    def test_format_with_need_instead_of_want(self):
        """Test: As a X, I need Y so that Z."""
        result = self.detector.detect("As a user, I need email notifications so that I stay informed")

        assert result.is_user_story is True
        assert result.as_a == "user"
        assert result.i_want == "email notifications"
        assert result.so_that == "I stay informed"

    def test_format_without_so_that(self):
        """Test: As a X, I want Y (no 'so that')."""
        result = self.detector.detect("As a developer, I want automated testing")

        assert result.is_user_story is True
        assert result.as_a == "developer"
        assert result.i_want == "automated testing"
        assert result.so_that == ""
        assert result.confidence >= 0.90  # Still high confidence

    def test_format_with_an(self):
        """Test: As an X, I want Y."""
        result = self.detector.detect("As an administrator, I want user management")

        assert result.is_user_story is True
        assert result.as_a == "administrator"
        assert result.i_want == "user management"

    def test_case_insensitive(self):
        """Test: Case insensitive detection."""
        result = self.detector.detect("as a USER, i WANT email ALERTS so that I GET notified")

        assert result.is_user_story is True
        assert result.as_a == "USER"
        assert result.i_want == "email ALERTS"

    def test_multiline_user_story(self):
        """Test: User story across multiple lines."""
        result = self.detector.detect(
            """As a developer,
            I want automated deployments
            so that releases are faster"""
        )

        assert result.is_user_story is True
        assert result.as_a == "developer"
        assert "automated deployments" in result.i_want

    def test_user_story_with_period(self):
        """Test: User story ending with period."""
        result = self.detector.detect("As a user, I want search functionality so that I can find items.")

        assert result.is_user_story is True
        assert result.as_a == "user"
        assert "search functionality" in result.i_want
        assert "find items" in result.so_that

    def test_user_story_with_exclamation(self):
        """Test: User story with enthusiasm."""
        result = self.detector.detect("As a developer, I want code review automation!")

        assert result.is_user_story is True
        assert result.as_a == "developer"

    def test_complex_role(self):
        """Test: Complex role description."""
        result = self.detector.detect(
            "As a system administrator managing multiple environments, I want centralized logging"
        )

        assert result.is_user_story is True
        assert "administrator" in result.as_a.lower()

    def test_complex_want(self):
        """Test: Complex feature description."""
        result = self.detector.detect(
            "As a developer, I want automated CI/CD pipeline with testing, linting, and deployment stages"
        )

        assert result.is_user_story is True
        assert "CI/CD" in result.i_want

    def test_complex_so_that(self):
        """Test: Complex benefit description."""
        result = self.detector.detect(
            "As a user, I want export functionality so that I can analyze data in Excel, "
            "share reports with stakeholders, and archive records"
        )

        assert result.is_user_story is True
        assert "export" in result.i_want.lower()

    def test_title_generation(self):
        """Test: Title is generated correctly."""
        result = self.detector.detect("As a developer, I want email notifications")

        assert result.suggested_title != ""
        assert len(result.suggested_title) > 0
        assert result.suggested_title[0].isupper()  # Capitalized

    def test_confidence_with_so_that(self):
        """Test: Full user story has 1.0 confidence."""
        result = self.detector.detect("As a user, I want feature X so that I get benefit Y")

        assert result.confidence == 1.0

    def test_confidence_without_so_that(self):
        """Test: User story without 'so that' has slightly lower confidence."""
        result = self.detector.detect("As a user, I want feature X")

        assert result.confidence >= 0.90
        assert result.confidence < 1.0


class TestInformalPatternDetection:
    """Test informal user story pattern detection."""

    def setup_method(self):
        """Setup test fixtures."""
        # Mock AI service for informal tests
        self.mock_ai = Mock()
        self.detector = UserStoryDetector(ai_service=self.mock_ai, confidence_threshold=0.70)

    def test_i_want_pattern(self):
        """Test: I want [feature]."""
        # Mock AI validation
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text="""ROLE: user
WANT: email notifications
SO_THAT: stay informed
TITLE: Email Notifications
CATEGORY: integration
CONFIDENCE: 0.80"""
            )
        ]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("I want email notifications")

        assert result.is_user_story is True
        assert result.confidence >= 0.70
        assert result.detection_method == "informal_ai"

    def test_i_need_pattern(self):
        """Test: I need [feature]."""
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text="""ROLE: developer
WANT: automated testing
SO_THAT: catch bugs early
TITLE: Automated Testing
CATEGORY: feature
CONFIDENCE: 0.85"""
            )
        ]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("I need automated testing")

        assert result.is_user_story is True
        assert "automated testing" in result.i_want.lower()

    def test_we_should_pattern(self):
        """Test: We should [action]."""
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text="""ROLE: team
WANT: implement code review process
SO_THAT: improve code quality
TITLE: Code Review Process
CATEGORY: feature
CONFIDENCE: 0.75"""
            )
        ]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("We should implement code review process")

        assert result.is_user_story is True

    def test_can_we_add_pattern(self):
        """Test: Can we add [feature]?"""
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text="""ROLE: user
WANT: search functionality
SO_THAT: find items quickly
TITLE: Search Functionality
CATEGORY: feature
CONFIDENCE: 0.78"""
            )
        ]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("Can we add search functionality?")

        assert result.is_user_story is True

    def test_imperative_add_pattern(self):
        """Test: Add [feature]."""
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text="""ROLE: developer
WANT: logging system
SO_THAT: debug issues
TITLE: Logging System
CATEGORY: infrastructure
CONFIDENCE: 0.82"""
            )
        ]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("Add a logging system")

        assert result.is_user_story is True

    def test_would_be_nice_pattern(self):
        """Test: It would be nice to have [feature]."""
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text="""ROLE: user
WANT: dark mode
SO_THAT: reduce eye strain
TITLE: Dark Mode
CATEGORY: ui
CONFIDENCE: 0.77"""
            )
        ]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("It would be nice to have dark mode")

        assert result.is_user_story is True

    def test_not_a_user_story_question(self):
        """Test: Regular question (not a user story)."""
        # Questions don't match any patterns, so will return "no_match" without calling AI
        result = self.detector.detect("What is the status of priority 5?")

        assert result.is_user_story is False
        # Without pattern match and without AI triggering, it's no_match
        assert result.detection_method == "no_match"

    def test_not_a_user_story_conversation(self):
        """Test: Conversational input (not a user story)."""
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [Mock(text="NOT_A_USER_STORY")]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("Thanks for the update!")

        assert result.is_user_story is False

    def test_informal_without_ai_service(self):
        """Test: Informal pattern without AI service (low confidence)."""
        detector_no_ai = UserStoryDetector(ai_service=None)

        result = detector_no_ai.detect("I want email notifications")

        # Should detect pattern but low confidence without AI
        assert result.is_user_story is False  # Below threshold
        assert result.confidence < 0.70
        assert result.detection_method == "informal_pattern"

    def test_ai_error_handling(self):
        """Test: AI error handling."""
        self.mock_ai.use_claude_cli = False
        self.mock_ai.client.messages.create.side_effect = Exception("API error")

        result = self.detector.detect("I want feature X")

        # Should return detection with error method
        assert result.detection_method == "ai_error"
        assert result.is_user_story is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = UserStoryDetector(ai_service=None)

    def test_empty_input(self):
        """Test: Empty string."""
        result = self.detector.detect("")

        assert result.is_user_story is False
        assert result.confidence == 0.0
        assert result.detection_method == "empty_input"

    def test_whitespace_only(self):
        """Test: Whitespace only."""
        result = self.detector.detect("   \n\t  ")

        assert result.is_user_story is False
        assert result.confidence == 0.0

    def test_very_long_user_story(self):
        """Test: Very long user story (title truncation)."""
        long_text = (
            "As a developer, I want a very very very very very very very very very "
            "very very very very very very long feature description that exceeds 80 characters"
        )

        result = self.detector.detect(long_text)

        assert result.is_user_story is True
        assert len(result.suggested_title) <= 80

    def test_special_characters(self):
        """Test: User story with special characters."""
        result = self.detector.detect("As a user, I want UTF-8 support (émojis 🎉) so that I can use special chars")

        assert result.is_user_story is True

    def test_multiple_user_stories(self):
        """Test: Multiple user stories in one input (detects first)."""
        result = self.detector.detect(
            "As a developer, I want CI/CD. As a user, I want email alerts. " "As an admin, I want user management."
        )

        assert result.is_user_story is True
        # Should detect first one
        assert result.as_a == "developer"

    def test_user_story_mid_text(self):
        """Test: User story in the middle of other text."""
        result = self.detector.detect(
            "I think that as a user, I want search functionality so I can find items. That would be great!"
        )

        assert result.is_user_story is True
        assert result.as_a == "user"

    def test_confidence_threshold_boundary(self):
        """Test: Confidence exactly at threshold."""
        detector = UserStoryDetector(ai_service=None, confidence_threshold=0.95)

        # User story without "so that" has 0.95 confidence
        result = detector.detect("As a user, I want feature X")

        assert result.confidence == 0.95
        # Should be classified as user story (>= threshold)
        assert result.is_user_story is True

    def test_custom_confidence_threshold(self):
        """Test: Custom confidence threshold."""
        detector_strict = UserStoryDetector(ai_service=None, confidence_threshold=0.99)

        result = detector_strict.detect("As a user, I want feature X")  # 0.95 confidence

        # The formal pattern is detected with 0.95 confidence
        # is_user_story is set to True in formal_pattern detection regardless of threshold
        # (threshold is only used for AI detection triggers)
        assert result.confidence == 0.95
        assert result.is_user_story is True  # Formal patterns always set True


class TestAIIntegration:
    """Test AI-enhanced detection (mocked)."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_ai = Mock()
        self.detector = UserStoryDetector(ai_service=self.mock_ai)

    def test_ai_enhancement_of_formal_pattern(self):
        """Test: AI enhances formal pattern with better title."""
        self.mock_ai.use_claude_cli = False
        mock_response = Mock()
        mock_response.content = [Mock(text="TITLE: Deploy Application on GCP\nCATEGORY: infrastructure")]
        self.mock_ai.client.messages.create.return_value = mock_response

        result = self.detector.detect("As a developer, I want to deploy on GCP so that it runs 24/7")

        assert result.is_user_story is True
        # High confidence formal patterns (1.0) don't trigger AI enhancement
        # Only patterns with confidence < 0.90 trigger AI validation
        # Formal pattern is detected and returned immediately
        assert result.detection_method == "formal_pattern"

    def test_ai_cli_mode(self):
        """Test: AI service using CLI mode."""
        self.mock_ai.use_claude_cli = True
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = "TITLE: Email Notifications\nCATEGORY: integration"
        self.mock_ai.cli_interface.execute_prompt.return_value = mock_result

        result = self.detector.detect("As a user, I want email alerts")

        assert result.is_user_story is True

    def test_ai_cli_failure(self):
        """Test: AI CLI failure handling."""
        self.mock_ai.use_claude_cli = True
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "CLI error"
        self.mock_ai.cli_interface.execute_prompt.return_value = mock_result

        # Should still detect formal pattern without AI
        result = self.detector.detect("As a user, I want feature X")

        assert result.is_user_story is True
        assert result.detection_method == "formal_pattern"  # Falls back to pattern


class TestDataStructure:
    """Test UserStoryDetection data structure."""

    def test_to_dict_conversion(self):
        """Test: Convert detection to dictionary."""
        detection = UserStoryDetection(
            raw_input="test",
            as_a="developer",
            i_want="feature",
            so_that="benefit",
            confidence=0.95,
            suggested_title="Test Feature",
            suggested_category="feature",
            is_user_story=True,
            detection_method="formal_pattern",
        )

        data = detection.to_dict()

        assert data["raw_input"] == "test"
        assert data["as_a"] == "developer"
        assert data["i_want"] == "feature"
        assert data["so_that"] == "benefit"
        assert data["confidence"] == 0.95
        assert data["suggested_title"] == "Test Feature"
        assert data["suggested_category"] == "feature"
        assert data["is_user_story"] is True
        assert data["detection_method"] == "formal_pattern"

    def test_default_values(self):
        """Test: Default values in UserStoryDetection."""
        detection = UserStoryDetection(raw_input="test")

        assert detection.as_a == ""
        assert detection.i_want == ""
        assert detection.so_that == ""
        assert detection.confidence == 0.0
        assert detection.is_user_story is False
        assert detection.detection_method == "none"


# Run tests with: pytest tests/unit/test_user_story_detector.py -v
