"""Unit tests for UserStoryCommandHandler."""

import pytest
from unittest.mock import Mock

from coffee_maker.cli.commands.user_story_command import (
    UserStoryCommandHandler,
    UserStoryDraft,
    ValidationState,
)


class TestUserStoryCommandHandler:
    """Test suite for UserStoryCommandHandler."""

    @pytest.fixture
    def mock_ai_service(self):
        """Mock AIService."""
        mock = Mock()
        # Default AI response for extraction
        mock_response = Mock()
        mock_response.message = (
            "Title: Test Feature\n"
            "Description: As a user I want to test features so that I can verify functionality\n"
            "Acceptance Criteria:\n"
            "- Feature works correctly\n"
            "- Tests pass\n"
            "Estimated Effort: 2 days"
        )
        mock.process_request.return_value = mock_response
        return mock

    @pytest.fixture
    def mock_roadmap_editor(self):
        """Mock RoadmapEditor."""
        editor = Mock()
        editor.get_user_story_summary.return_value = {
            "total": 1,
            "stories": [
                {
                    "id": "US-042",
                    "title": "PDF Export",
                    "description": "As a user I want to export reports to PDF",
                    "status": "📝 Backlog",
                }
            ],
            "backlog": 1,
            "in_discussion": 0,
            "ready": 0,
            "assigned": 0,
            "complete": 0,
        }
        editor.add_user_story.return_value = True
        return editor

    @pytest.fixture
    def handler(self, mock_ai_service, mock_roadmap_editor):
        """Create handler with mocks."""
        return UserStoryCommandHandler(ai_service=mock_ai_service, roadmap_editor=mock_roadmap_editor)

    def test_parse_command_valid(self, handler):
        """Test parsing valid /US command."""
        description = handler._parse_command("/US I want to export reports")
        assert description == "I want to export reports"

    def test_parse_command_case_insensitive(self, handler):
        """Test /US is case-insensitive."""
        description = handler._parse_command("/us I want to export reports")
        assert description == "I want to export reports"

    def test_parse_command_empty(self, handler):
        """Test parsing /US with no description."""
        description = handler._parse_command("/US")
        assert description == ""

    def test_handle_command_no_description(self, handler):
        """Test /US with no description returns error."""
        result = handler.handle_command("/US")
        assert "❌" in result["message"]
        assert result["requires_input"] is False

    def test_handle_command_creates_draft(self, handler, mock_ai_service):
        """Test /US creates draft and checks similarity."""
        result = handler.handle_command("/US I want to export reports")

        # Should create draft
        assert handler.current_draft is not None
        assert handler.current_draft.title == "Test Feature"
        assert result["requires_input"] is True
        assert "📝 User Story Draft" in result["message"]

    def test_similarity_detection_high(self, handler):
        """Test similarity detection flags duplicates."""
        # Create draft similar to existing US-042
        draft = UserStoryDraft(
            title="PDF Export Feature",
            description="As a user I want to export to PDF so that I can save reports",
            acceptance_criteria=["Export works"],
        )

        handler._check_similarity(draft)

        # Should find US-042 as similar
        assert len(draft.similar_stories) > 0
        assert draft.similar_stories[0][0] == "US-042"
        assert draft.similar_stories[0][1] > 0.5  # Similarity score

    def test_similarity_detection_low(self, handler):
        """Test similarity detection with unrelated story."""
        # Create draft completely different from existing stories
        draft = UserStoryDraft(
            title="Email Notifications",
            description="As a user I want to receive email alerts so that I stay informed",
            acceptance_criteria=["Emails sent"],
        )

        handler._check_similarity(draft)

        # Should not find similar stories
        assert len(draft.similar_stories) == 0

    def test_classify_response_approve(self, handler):
        """Test classifying approval responses."""
        assert handler._classify_response("yes") == "approve"
        assert handler._classify_response("looks good") == "approve"
        assert handler._classify_response("approve") == "approve"
        assert handler._classify_response("ok") == "approve"

    def test_classify_response_refine(self, handler):
        """Test classifying refinement responses."""
        assert handler._classify_response("change the title") == "refine"
        assert handler._classify_response("should be different") == "refine"
        assert handler._classify_response("update the description") == "refine"

    def test_classify_response_reject(self, handler):
        """Test classifying rejection responses."""
        assert handler._classify_response("no") == "reject"
        assert handler._classify_response("cancel") == "reject"
        assert handler._classify_response("abort") == "reject"

    def test_handle_approval_moves_to_prioritization(self, handler):
        """Test approval transitions to prioritization state."""
        # Setup draft
        handler.current_draft = UserStoryDraft(
            title="Test",
            description="As a user I want test so that it works",
            acceptance_criteria=["Test"],
            state=ValidationState.AWAITING_VALIDATION,
        )

        result = handler._handle_approval()

        assert handler.current_draft.state == ValidationState.PRIORITIZING
        assert "Suggested Placement" in result["message"]
        assert result["requires_input"] is True

    def test_handle_rejection_clears_draft(self, handler):
        """Test rejection clears draft."""
        # Setup draft
        handler.current_draft = UserStoryDraft(title="Test", description="Test", acceptance_criteria=["Test"])

        result = handler._handle_rejection()

        assert handler.current_draft is None
        assert "❌" in result["message"]
        assert result["requires_input"] is False

    def test_finalize_adds_to_roadmap(self, handler, mock_roadmap_editor):
        """Test finalization adds user story to roadmap."""
        # Setup draft
        handler.current_draft = UserStoryDraft(
            title="Test Feature",
            description="As a user I want to test so that I can verify",
            acceptance_criteria=["Criterion 1"],
            state=ValidationState.PRIORITIZING,
        )

        result = handler.finalize_user_story("BACKLOG")

        # Should call add_user_story
        mock_roadmap_editor.add_user_story.assert_called_once()

        # Should clear draft
        assert handler.current_draft is None

        # Should confirm success
        assert "✅" in result["message"]
        assert result["requires_input"] is False

    def test_parse_user_story_description(self, handler):
        """Test parsing user story description."""
        description = "As a developer I want to write tests so that code quality improves"
        role, want, so_that = handler._parse_user_story_description(description)

        assert role == "developer"
        assert want == "write tests"
        assert so_that == "code quality improves"

    def test_parse_user_story_description_fallback(self, handler):
        """Test parsing falls back for malformed description."""
        description = "I just want something to work"
        role, want, so_that = handler._parse_user_story_description(description)

        assert role == "user"
        assert want == description
        assert so_that == "it provides value"

    def test_parse_ai_extraction(self, handler):
        """Test parsing AI extraction response."""
        ai_response = """Title: Email Notifications

Description: As a user I want to receive email alerts so that I stay informed

Acceptance Criteria:
- Emails are sent on important events
- User can configure preferences
- Unsubscribe option available

Estimated Effort: 3-5 days"""

        parsed = handler._parse_ai_extraction(ai_response)

        assert parsed["title"] == "Email Notifications"
        assert "As a user I want to receive email alerts" in parsed["description"]
        assert len(parsed["criteria"]) == 3
        assert "Emails are sent on important events" in parsed["criteria"]
        assert parsed["effort"] == "3-5 days"

    def test_handle_validation_response_no_draft(self, handler):
        """Test validation response when no draft exists."""
        result = handler.handle_validation_response("yes")

        assert "⚠️" in result["message"]
        assert "no user story draft" in result["message"].lower()

    def test_handle_refinement(self, handler, mock_ai_service):
        """Test handling refinement request."""
        # Setup draft
        handler.current_draft = UserStoryDraft(
            title="Original Title",
            description="As a user I want original feature",
            acceptance_criteria=["Original criterion"],
            state=ValidationState.AWAITING_VALIDATION,
        )

        # Mock refined response
        mock_response = Mock()
        mock_response.message = (
            "Title: Refined Title\n"
            "Description: As a user I want refined feature so that it's better\n"
            "Acceptance Criteria:\n"
            "- Refined criterion 1\n"
            "- Refined criterion 2\n"
            "Estimated Effort: 3 days"
        )
        mock_ai_service.process_request.return_value = mock_response

        result = handler._handle_refinement("change the title to something better")

        # Should update draft
        assert handler.current_draft.title == "Refined Title"
        assert "refined feature" in handler.current_draft.description
        assert len(handler.current_draft.acceptance_criteria) == 2

        # Should re-present draft
        assert "📝 User Story Draft" in result["message"]
        assert result["requires_input"] is True
