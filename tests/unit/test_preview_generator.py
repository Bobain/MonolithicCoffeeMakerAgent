"""Unit tests for PreviewGenerator (US-021 Phase 4).

Tests preview generation for document updates before they are applied.
"""

import pytest
from pathlib import Path
from coffee_maker.cli.preview_generator import (
    PreviewGenerator,
)
from coffee_maker.cli.request_classifier import RequestType


@pytest.fixture
def preview_generator(tmp_path):
    """Create PreviewGenerator with temp project root."""
    return PreviewGenerator(project_root=tmp_path)


@pytest.fixture
def sample_roadmap(tmp_path):
    """Create sample ROADMAP.md file."""
    roadmap_path = tmp_path / "docs" / "ROADMAP.md"
    roadmap_path.parent.mkdir(parents=True)
    roadmap_path.write_text(
        """# Coffee Maker Agent - Roadmap

## US-001: First Feature

**Status**: ✅ COMPLETE

---

## US-002: Second Feature

**Status**: 📝 PLANNED

---
"""
    )
    return roadmap_path


class TestPreviewGeneratorInitialization:
    """Test PreviewGenerator initialization."""

    def test_init_with_default_root(self):
        """Test initialization with default project root."""
        generator = PreviewGenerator()
        assert generator.project_root == Path.cwd()

    def test_init_with_custom_root(self, tmp_path):
        """Test initialization with custom project root."""
        generator = PreviewGenerator(project_root=tmp_path)
        assert generator.project_root == tmp_path


class TestFeatureRequestPreviews:
    """Test preview generation for feature requests."""

    def test_preview_feature_request_roadmap(self, preview_generator, sample_roadmap):
        """Test preview for feature request targeting ROADMAP."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="I want to add email notifications for completed tasks",
            target_documents=["docs/ROADMAP.md"],
            metadata={
                "title": "Email Notifications",
                "business_value": "Keep users informed",
                "estimated_effort": "2-3 days",
                "us_number": 3,
            },
        )

        assert result is not None
        assert len(result.previews) == 1
        assert result.total_additions > 0
        assert result.requires_confirmation is True

        preview = result.previews[0]
        assert preview.document_path == "docs/ROADMAP.md"
        assert "US-3" in preview.preview_text or "US-003" in preview.preview_text  # Either format
        assert "Email Notifications" in preview.preview_text
        assert "Keep users informed" in preview.preview_text

    def test_preview_shows_additions_with_plus_prefix(self, preview_generator, sample_roadmap):
        """Test that preview shows additions with + prefix (diff style)."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add Slack integration",
            target_documents=["docs/ROADMAP.md"],
            metadata={"title": "Slack Integration", "us_number": 3},
        )

        preview = result.previews[0]
        # Check for diff-style formatting with + prefix (US-3 or US-003)
        assert (
            "+ ## US-3: Slack Integration" in preview.preview_text
            or "+ ## US-003: Slack Integration" in preview.preview_text
        )

    def test_preview_includes_location_info(self, preview_generator, sample_roadmap):
        """Test that preview includes estimated location information."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add analytics",
            target_documents=["docs/ROADMAP.md"],
            metadata={"title": "Analytics", "us_number": 3},
        )

        preview = result.previews[0]
        assert "Location:" in preview.preview_text
        # Should indicate where it will be inserted
        assert "line" in preview.preview_text.lower() or "section" in preview.preview_text.lower()

    def test_preview_multiple_documents(self, preview_generator, tmp_path):
        """Test preview generation for multiple documents."""
        # Create documents
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "ROADMAP.md").write_text("# Roadmap")
        (tmp_path / "docs" / "COLLABORATION_METHODOLOGY.md").write_text("# Collab")

        result = preview_generator.generate_preview(
            request_type=RequestType.HYBRID,
            content="Add code review bot and 2 PR approvals required",
            target_documents=["docs/ROADMAP.md", "docs/COLLABORATION_METHODOLOGY.md"],
            metadata={"title": "Code Review Bot", "rationale": "Improve quality"},
        )

        assert len(result.previews) == 2
        assert result.previews[0].document_path == "docs/ROADMAP.md"
        assert result.previews[1].document_path == "docs/COLLABORATION_METHODOLOGY.md"


class TestMethodologyChangePreviews:
    """Test preview generation for methodology changes."""

    def test_preview_methodology_change(self, preview_generator, tmp_path):
        """Test preview for methodology change."""
        collab_path = tmp_path / "docs" / "COLLABORATION_METHODOLOGY.md"
        collab_path.parent.mkdir(parents=True)
        collab_path.write_text("# Collaboration\n\n## General Guidelines\n")

        result = preview_generator.generate_preview(
            request_type=RequestType.METHODOLOGY_CHANGE,
            content="All PRs must have 2 approvals before merging",
            target_documents=["docs/COLLABORATION_METHODOLOGY.md"],
            metadata={
                "title": "PR Approval Policy",
                "rationale": "Improve code quality",
            },
        )

        assert len(result.previews) == 1
        preview = result.previews[0]
        assert "PR Approval Policy" in preview.preview_text
        assert "Improve code quality" in preview.preview_text


class TestPreviewValidation:
    """Test validation and warnings in previews."""

    def test_preview_warns_about_missing_document(self, preview_generator):
        """Test preview warns if document doesn't exist."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add feature",
            target_documents=["docs/NONEXISTENT.md"],
            metadata={"title": "Feature"},
        )

        preview = result.previews[0]
        assert len(preview.warnings) > 0
        assert any("does not exist" in w.lower() for w in preview.warnings)

    def test_preview_checks_duplicate_us_numbers(self, preview_generator, sample_roadmap):
        """Test preview warns about duplicate US numbers."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Duplicate feature",
            target_documents=["docs/ROADMAP.md"],
            metadata={"title": "Duplicate", "us_number": 1},  # US-001 already exists
        )

        preview = result.previews[0]
        # Should warn about duplicate
        assert any("US-001" in w and ("already exists" in w or "duplicate" in w.lower()) for w in preview.warnings)

    def test_preview_warns_about_similar_titles(self, preview_generator, sample_roadmap):
        """Test preview warns about similar titles."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add feature",
            target_documents=["docs/ROADMAP.md"],
            metadata={
                "title": "First Feature",
                "us_number": 3,
            },  # Title similar to US-001
        )

        preview = result.previews[0]
        assert any("similar" in w.lower() or "already exist" in w.lower() for w in preview.warnings)


class TestPreviewSummary:
    """Test preview summary generation."""

    def test_summary_includes_request_type(self, preview_generator, sample_roadmap):
        """Test summary includes request type."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add feature",
            target_documents=["docs/ROADMAP.md"],
            metadata={"title": "Feature", "us_number": 3},
        )

        assert "feature_request" in result.summary.lower()

    def test_summary_includes_document_count(self, preview_generator, tmp_path):
        """Test summary includes document count."""
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "ROADMAP.md").write_text("# Roadmap")
        (tmp_path / "docs" / "COLLABORATION_METHODOLOGY.md").write_text("# Collab")

        result = preview_generator.generate_preview(
            request_type=RequestType.HYBRID,
            content="Hybrid request",
            target_documents=["docs/ROADMAP.md", "docs/COLLABORATION_METHODOLOGY.md"],
            metadata={"title": "Hybrid"},
        )

        assert "2" in result.summary  # 2 documents

    def test_summary_includes_total_additions(self, preview_generator, sample_roadmap):
        """Test summary includes total line additions."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add feature",
            target_documents=["docs/ROADMAP.md"],
            metadata={"title": "Feature", "us_number": 3},
        )

        assert result.total_additions > 0
        assert str(result.total_additions) in result.summary


class TestConfirmationPrompt:
    """Test confirmation prompt formatting."""

    def test_format_confirmation_prompt(self, preview_generator, sample_roadmap):
        """Test confirmation prompt formatting."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add feature",
            target_documents=["docs/ROADMAP.md"],
            metadata={"title": "Feature", "us_number": 3},
        )

        prompt = preview_generator.format_confirmation_prompt(result)

        assert "CONFIRMATION REQUIRED" in prompt or "confirm" in prompt.lower()
        assert "y" in prompt.lower() or "yes" in prompt.lower()
        assert "n" in prompt.lower() or "no" in prompt.lower()
        assert "Feature" in prompt  # Should include preview content


class TestEstimatedLocation:
    """Test location estimation in documents."""

    def test_estimate_location_before_first_us(self, preview_generator, sample_roadmap):
        """Test location estimated before first US entry."""
        # Should insert before US-001
        location = preview_generator._estimate_location(sample_roadmap, RequestType.FEATURE_REQUEST)

        assert "before" in location.lower() or "line" in location.lower()

    def test_estimate_location_for_collaboration(self, preview_generator, tmp_path):
        """Test location estimation for collaboration document."""
        collab_path = tmp_path / "docs" / "COLLABORATION_METHODOLOGY.md"
        collab_path.parent.mkdir(parents=True)
        collab_path.write_text("# Collab\n\n## General Guidelines\n\nContent here\n")

        location = preview_generator._estimate_location(collab_path, RequestType.METHODOLOGY_CHANGE)

        assert "section" in location.lower() or "line" in location.lower()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_content(self, preview_generator, sample_roadmap):
        """Test preview with empty content."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="",
            target_documents=["docs/ROADMAP.md"],
            metadata={"title": "Empty", "us_number": 3},
        )

        # Should still generate preview (validation happens elsewhere)
        assert len(result.previews) == 1

    def test_missing_metadata(self, preview_generator, sample_roadmap):
        """Test preview with missing metadata."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add feature",
            target_documents=["docs/ROADMAP.md"],
            metadata={},  # No metadata
        )

        assert len(result.previews) == 1
        # Should use defaults
        preview = result.previews[0]
        assert "New Feature" in preview.preview_text or "TBD" in preview.preview_text

    def test_invalid_document_path(self, preview_generator):
        """Test preview with invalid document path."""
        result = preview_generator.generate_preview(
            request_type=RequestType.FEATURE_REQUEST,
            content="Add feature",
            target_documents=["invalid/path/to/nowhere.md"],
            metadata={"title": "Feature"},
        )

        # Should handle gracefully
        assert len(result.previews) == 1
        preview = result.previews[0]
        assert len(preview.warnings) > 0
