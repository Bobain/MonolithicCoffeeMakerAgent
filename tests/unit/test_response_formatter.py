"""Unit tests for ResponseFormatter (US-021 Phase 2)."""

from coffee_maker.cli.request_classifier import ClassificationResult, RequestType
from coffee_maker.cli.response_formatter import ResponseFormatter


class TestFormatClassificationHeader:
    """Test formatting classification headers."""

    def test_feature_request_header(self):
        """Test feature request header formatting."""
        result = ClassificationResult(
            request_type=RequestType.FEATURE_REQUEST,
            confidence=0.85,
            feature_indicators=["keyword: want"],
            methodology_indicators=[],
            suggested_questions=[],
            target_documents=["docs/roadmap/ROADMAP.md"],
        )

        header = ResponseFormatter.format_classification_header(result)

        assert "Feature Request Detected" in header
        assert "ROADMAP" in header
        assert "📝" in header

    def test_methodology_change_header(self):
        """Test methodology change header formatting."""
        result = ClassificationResult(
            request_type=RequestType.METHODOLOGY_CHANGE,
            confidence=0.75,
            feature_indicators=[],
            methodology_indicators=["keyword: always"],
            suggested_questions=[],
            target_documents=["docs/roadmap/TEAM_COLLABORATION.md"],
        )

        header = ResponseFormatter.format_classification_header(result)

        assert "Methodology Change Detected" in header
        assert "TEAM_COLLABORATION" in header
        assert "🔧" in header

    def test_hybrid_request_header(self):
        """Test hybrid request header formatting."""
        result = ClassificationResult(
            request_type=RequestType.HYBRID,
            confidence=0.80,
            feature_indicators=["keyword: want"],
            methodology_indicators=["keyword: always"],
            suggested_questions=[],
            target_documents=[
                "docs/roadmap/ROADMAP.md",
                "docs/roadmap/TEAM_COLLABORATION.md",
            ],
        )

        header = ResponseFormatter.format_classification_header(result)

        assert "Hybrid Request Detected" in header
        assert "ROADMAP" in header
        assert "TEAM_COLLABORATION" in header
        assert "🔀" in header

    def test_clarification_needed_header(self):
        """Test clarification needed header formatting."""
        result = ClassificationResult(
            request_type=RequestType.CLARIFICATION_NEEDED,
            confidence=0.20,
            feature_indicators=[],
            methodology_indicators=[],
            suggested_questions=["Could you clarify?"],
            target_documents=[],
        )

        header = ResponseFormatter.format_classification_header(result)

        assert "Clarification Needed" in header
        assert "❓" in header


class TestFormatConfirmationFooter:
    """Test formatting confirmation footers."""

    def test_single_document_footer(self):
        """Test footer with single document."""
        footer = ResponseFormatter.format_confirmation_footer(["docs/roadmap/ROADMAP.md"])

        assert "Confirmed" in footer
        assert "ROADMAP.md" in footer
        assert "✅" in footer

    def test_multiple_documents_footer(self):
        """Test footer with multiple documents."""
        footer = ResponseFormatter.format_confirmation_footer(
            ["docs/roadmap/ROADMAP.md", "docs/roadmap/TEAM_COLLABORATION.md"]
        )

        assert "Confirmed" in footer
        assert "ROADMAP.md" in footer
        assert "TEAM_COLLABORATION.md" in footer
        assert "✅" in footer
        # Should use list format
        assert "- `" in footer

    def test_empty_documents_footer(self):
        """Test footer with no documents."""
        footer = ResponseFormatter.format_confirmation_footer([])

        assert footer == ""


class TestFormatCompleteResponse:
    """Test formatting complete responses."""

    def test_complete_response_feature_request(self):
        """Test complete response for feature request."""
        result = ClassificationResult(
            request_type=RequestType.FEATURE_REQUEST,
            confidence=0.85,
            feature_indicators=["keyword: want"],
            methodology_indicators=[],
            suggested_questions=[],
            target_documents=["docs/roadmap/ROADMAP.md"],
        )

        ai_message = "I'll add email notifications to the roadmap."

        response = ResponseFormatter.format_complete_response(result, ai_message)

        # Should contain header, message, and footer
        assert "Feature Request Detected" in response
        assert ai_message in response
        assert "Confirmed" in response
        assert "ROADMAP.md" in response

    def test_complete_response_clarification(self):
        """Test complete response for clarification (no formatting)."""
        result = ClassificationResult(
            request_type=RequestType.CLARIFICATION_NEEDED,
            confidence=0.20,
            feature_indicators=[],
            methodology_indicators=[],
            suggested_questions=["Could you clarify?"],
            target_documents=[],
        )

        ai_message = "Could you please provide more details?"

        response = ResponseFormatter.format_complete_response(result, ai_message)

        # Should return message as-is (no formatting for clarification)
        assert response == ai_message

    def test_complete_response_hybrid(self):
        """Test complete response for hybrid request."""
        result = ClassificationResult(
            request_type=RequestType.HYBRID,
            confidence=0.80,
            feature_indicators=["keyword: want"],
            methodology_indicators=["keyword: always"],
            suggested_questions=[],
            target_documents=[
                "docs/roadmap/ROADMAP.md",
                "docs/roadmap/TEAM_COLLABORATION.md",
            ],
        )

        ai_message = "I'll implement the feature and update our process."

        response = ResponseFormatter.format_complete_response(result, ai_message)

        # Should contain hybrid header, message, and footer
        assert "Hybrid Request Detected" in response
        assert ai_message in response
        assert "Confirmed" in response
        assert "ROADMAP.md" in response
        assert "TEAM_COLLABORATION.md" in response
