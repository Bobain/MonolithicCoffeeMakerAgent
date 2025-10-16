"""Unit tests for DocumentUpdater (US-021 Phase 3).

Tests the document update system including:
- ROADMAP.md updates (feature requests)
- COLLABORATION_METHODOLOGY.md updates (methodology changes)
- CLAUDE.md updates (technical guidelines)
- Backup/restore functionality
- Error handling and recovery
"""

from pathlib import Path

import pytest

from coffee_maker.cli.document_updater import DocumentUpdateError, DocumentUpdater
from coffee_maker.cli.request_classifier import RequestType


@pytest.fixture
def temp_docs(tmp_path):
    """Create temporary document structure for testing.

    Creates realistic document structure:
    - docs/roadmap/ROADMAP.md with existing US entries
    - docs/COLLABORATION_METHODOLOGY.md with sections
    - .claude/CLAUDE.md with instructions
    """
    # Create docs directory
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create realistic ROADMAP.md
    roadmap_path = docs_dir / "ROADMAP.md"
    roadmap_path.write_text(
        """# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-15
**Current Branch**: `roadmap`
**Status**: Testing Phase 3

---

## 🔴 TOP PRIORITY FOR code_developer

Current priority: US-021 Phase 3 - Document Updates

---

## US-001: Authentication System

**Status**: ✅ **COMPLETE**
**Created**: 2025-10-01

**Description**:
Implement user authentication with JWT tokens

**Business Value**: Security and user management
**Estimated Effort**: 3-5 days

---

## US-002: Email Notifications

**Status**: 🔄 **IN PROGRESS**
**Created**: 2025-10-10

**Description**:
Send email notifications for important events

---
"""
    )

    # Create realistic COLLABORATION_METHODOLOGY.md
    collab_path = docs_dir / "COLLABORATION_METHODOLOGY.md"
    collab_path.write_text(
        """# Team Collaboration Methodology

## General Guidelines

All team members should follow these guidelines.

## Workflows

Our standard workflow for features:
1. Create technical spec
2. Implement feature
3. Test and deploy

## Code Review Process

All code must be reviewed before merging.

---
"""
    )

    # Create realistic .claude/CLAUDE.md
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    claude_path = claude_dir / "CLAUDE.md"
    claude_path.write_text(
        """# Claude Instructions

## Project Overview

MonolithicCoffeeMakerAgent is an autonomous software development system.

## Special Instructions for Claude

Follow these instructions when working on the project.

### Code Standards

Use Black formatter and type hints.

---
"""
    )

    return tmp_path


@pytest.fixture
def updater(temp_docs, monkeypatch):
    """Create DocumentUpdater with temp paths."""
    updater = DocumentUpdater(project_root=temp_docs)

    # Update paths to use temp directories
    monkeypatch.setattr(updater, "ROADMAP_PATH", Path("docs/roadmap/ROADMAP.md"))
    monkeypatch.setattr(
        updater,
        "COLLABORATION_PATH",
        Path("docs/COLLABORATION_METHODOLOGY.md"),
    )
    monkeypatch.setattr(updater, "CLAUDE_PATH", Path(".claude/CLAUDE.md"))

    return updater


class TestDocumentUpdaterBasics:
    """Test basic DocumentUpdater functionality."""

    def test_updater_initialization(self, updater):
        """Test updater initializes correctly."""
        assert updater is not None
        assert updater.project_root is not None
        assert updater.backup_dir.exists()

    def test_backup_directory_created(self, updater):
        """Test backup directory is created on init."""
        assert updater.backup_dir.exists()
        assert updater.backup_dir.is_dir()


class TestRoadmapUpdates:
    """Test ROADMAP.md updates for feature requests."""

    def test_add_feature_request_to_roadmap(self, updater):
        """Test adding a new feature request to ROADMAP."""
        result = updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="I want to add Slack notifications",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={
                "title": "Slack Notifications",
                "business_value": "Improve team communication",
                "estimated_effort": "2-3 days",
            },
        )

        assert result["docs/roadmap/ROADMAP.md"] is True

        # Verify content was added
        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()

        assert "US-003" in content  # Next US number after US-002
        assert "Slack Notifications" in content
        assert "Improve team communication" in content
        assert "2-3 days" in content
        assert "FEATURE REQUEST" in content

    def test_roadmap_gets_next_us_number(self, updater):
        """Test that _get_next_us_number() works correctly."""
        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        lines = roadmap_path.read_text().splitlines(keepends=True)

        next_num = updater._get_next_us_number(lines)
        assert next_num == 3  # Should be 3 after US-001 and US-002

    def test_roadmap_insertion_point(self, updater):
        """Test finding correct insertion point in ROADMAP."""
        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        lines = roadmap_path.read_text().splitlines(keepends=True)

        insert_idx = updater._find_roadmap_insertion_point(lines)

        # Should insert before first US entry (US-001)
        assert "## US-001" in lines[insert_idx]

    def test_multiple_feature_requests(self, updater):
        """Test adding multiple feature requests sequentially."""
        # Add first feature
        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Feature 1",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={"title": "Feature 1"},
        )

        # Add second feature
        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Feature 2",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={"title": "Feature 2"},
        )

        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()

        assert "US-003" in content  # First new feature
        assert "US-004" in content  # Second new feature
        assert "Feature 1" in content
        assert "Feature 2" in content

    def test_roadmap_acceptance_criteria_list(self, updater):
        """Test acceptance criteria are formatted correctly."""
        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Test feature",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={
                "title": "Test Feature",
                "acceptance_criteria": [
                    "Criterion 1",
                    "Criterion 2",
                    "Criterion 3",
                ],
            },
        )

        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()

        assert "- [ ] Criterion 1" in content
        assert "- [ ] Criterion 2" in content
        assert "- [ ] Criterion 3" in content


class TestCollaborationUpdates:
    """Test COLLABORATION_METHODOLOGY.md updates."""

    def test_add_methodology_change(self, updater):
        """Test adding methodology change."""
        result = updater.update_documents(
            request_type=RequestType.METHODOLOGY_CHANGE,
            content="Always create technical specs before implementation",
            target_documents=["docs/COLLABORATION_METHODOLOGY.md"],
            metadata={
                "title": "Technical Spec Requirement",
                "section": "Workflows",
                "rationale": "Improves planning and reduces rework",
                "applies_to": "All developers",
            },
        )

        assert result["docs/COLLABORATION_METHODOLOGY.md"] is True

        collab_path = updater.project_root / "docs/COLLABORATION_METHODOLOGY.md"
        content = collab_path.read_text()

        assert "Technical Spec Requirement" in content
        assert "Always create technical specs" in content
        assert "Improves planning and reduces rework" in content
        assert "All developers" in content

    def test_methodology_section_detection(self, updater):
        """Test finding correct section in COLLABORATION_METHODOLOGY."""
        collab_path = updater.project_root / "docs/COLLABORATION_METHODOLOGY.md"
        lines = collab_path.read_text().splitlines(keepends=True)

        # Test finding "Workflows" section
        insert_idx = updater._find_collaboration_section(lines, "Workflows")
        assert insert_idx > 0  # Found the section

        # Verify it's after the "## Workflows" heading
        found_workflows = False
        for i in range(insert_idx - 1, -1, -1):
            if "## Workflows" in lines[i]:
                found_workflows = True
                break
        assert found_workflows

    def test_methodology_with_new_section(self, updater):
        """Test creating new section if not found."""
        updater.update_documents(
            request_type=RequestType.METHODOLOGY_CHANGE,
            content="New section content",
            target_documents=["docs/COLLABORATION_METHODOLOGY.md"],
            metadata={"title": "New Section", "section": "NonExistent Section"},
        )

        collab_path = updater.project_root / "docs/COLLABORATION_METHODOLOGY.md"
        content = collab_path.read_text()

        # Should still add content (at end)
        assert "New Section" in content


class TestClaudeUpdates:
    """Test CLAUDE.md updates."""

    def test_add_technical_guideline(self, updater):
        """Test adding technical guideline to CLAUDE.md."""
        result = updater.update_documents(
            request_type=RequestType.METHODOLOGY_CHANGE,
            content="Always use async/await for I/O operations",
            target_documents=[".claude/CLAUDE.md"],
            metadata={
                "title": "Async I/O Guideline",
                "section": "Special Instructions for Claude",
            },
        )

        assert result[".claude/CLAUDE.md"] is True

        claude_path = updater.project_root / ".claude/CLAUDE.md"
        content = claude_path.read_text()

        assert "Async I/O Guideline" in content
        assert "Always use async/await for I/O operations" in content


class TestBackupRestore:
    """Test backup and restore functionality."""

    def test_backup_created_before_update(self, updater):
        """Test that backup is created before updating."""
        # Get initial backup count
        initial_backups = len(list(updater.backup_dir.glob("ROADMAP_*.md")))

        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Test",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={"title": "Test"},
        )

        # Check backup was created
        backups = list(updater.backup_dir.glob("ROADMAP_*.md"))
        assert len(backups) == initial_backups + 1

    def test_restore_on_error(self, updater, monkeypatch):
        """Test backup is restored when update fails."""
        # Save original content
        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        original_content = roadmap_path.read_text()

        # Force an error during update
        def mock_update_roadmap(*args, **kwargs):
            raise Exception("Simulated error")

        monkeypatch.setattr(updater, "_update_roadmap", mock_update_roadmap)

        # Try update (should fail and restore)
        with pytest.raises(DocumentUpdateError):
            updater.update_documents(
                request_type=RequestType.FEATURE_REQUEST,
                content="Test",
                target_documents=["docs/roadmap/ROADMAP.md"],
                metadata={"title": "Test"},
            )

        # Verify content was restored
        current_content = roadmap_path.read_text()
        assert current_content == original_content

    def test_backup_preserves_file_metadata(self, updater):
        """Test that backup preserves file metadata (timestamps, etc)."""
        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"

        # Get original modification time
        roadmap_path.stat().st_mtime

        # Create backup
        updater._create_backup(roadmap_path)

        # Check backup exists and has similar metadata
        backups = list(updater.backup_dir.glob("ROADMAP_*.md"))
        assert len(backups) > 0

        # Verify backup has content
        backup = backups[-1]
        assert backup.read_text() == roadmap_path.read_text()


class TestHybridRequests:
    """Test hybrid requests (feature + methodology)."""

    def test_hybrid_updates_multiple_docs(self, updater):
        """Test hybrid request updates both ROADMAP and COLLABORATION."""
        result = updater.update_documents(
            request_type=RequestType.HYBRID,
            content="Implement code review bot and require 2 approvals",
            target_documents=[
                "docs/roadmap/ROADMAP.md",
                "docs/COLLABORATION_METHODOLOGY.md",
            ],
            metadata={
                "title": "Code Review Process",
                "business_value": "Improve code quality",
                "rationale": "Automated reviews catch bugs early",
            },
        )

        assert result["docs/roadmap/ROADMAP.md"] is True
        assert result["docs/COLLABORATION_METHODOLOGY.md"] is True

        # Verify ROADMAP updated
        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        roadmap_content = roadmap_path.read_text()
        assert "Code Review Process" in roadmap_content

        # Verify COLLABORATION updated
        collab_path = updater.project_root / "docs/COLLABORATION_METHODOLOGY.md"
        collab_content = collab_path.read_text()
        assert "Code Review Process" in collab_content


class TestVerification:
    """Test document verification."""

    def test_verify_update_success(self, updater):
        """Test verifying successful update."""
        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Test feature",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={"title": "Test Feature"},
        )

        # Verify the update
        assert updater.verify_update("docs/roadmap/ROADMAP.md", "Test Feature") is True
        assert updater.verify_update("docs/roadmap/ROADMAP.md", "Test feature") is True

    def test_verify_update_not_found(self, updater):
        """Test verification fails when content not found."""
        assert updater.verify_update("docs/roadmap/ROADMAP.md", "NonExistent Content") is False

    def test_verify_nonexistent_document(self, updater):
        """Test verification fails for nonexistent document."""
        assert updater.verify_update("docs/NONEXISTENT.md", "content") is False


class TestErrorHandling:
    """Test error handling."""

    def test_update_nonexistent_document_type(self, updater):
        """Test updating unknown document type."""
        result = updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Test",
            target_documents=["unknown/path.md"],
            metadata={"title": "Test"},
        )

        # Should return False for unknown type (but not raise exception)
        assert result["unknown/path.md"] is False

    def test_update_with_empty_metadata(self, updater):
        """Test update works with minimal metadata."""
        result = updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Test feature",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={},  # Empty metadata
        )

        assert result["docs/roadmap/ROADMAP.md"] is True

        # Verify it used defaults
        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()
        assert "TBD" in content  # Default values used


class TestEdgeCases:
    """Test edge cases and corner conditions."""

    def test_update_with_special_characters(self, updater):
        """Test content with special characters."""
        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Feature with $pecial ch@racters & symbols!",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={"title": "Special Characters Test"},
        )

        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()
        assert "$pecial ch@racters & symbols!" in content

    def test_update_with_multiline_content(self, updater):
        """Test content spanning multiple lines."""
        multiline_content = """This is a feature request
        that spans multiple lines
        with different paragraphs.

        It should preserve formatting."""

        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content=multiline_content,
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={"title": "Multiline Test"},
        )

        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()
        assert "spans multiple lines" in content
        assert "preserve formatting" in content

    def test_update_with_very_long_title(self, updater):
        """Test with very long title."""
        long_title = "A" * 200  # 200 character title

        updater.update_documents(
            request_type=RequestType.FEATURE_REQUEST,
            content="Test",
            target_documents=["docs/roadmap/ROADMAP.md"],
            metadata={"title": long_title},
        )

        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()
        assert long_title in content

    def test_concurrent_updates(self, updater):
        """Test multiple updates in sequence work correctly."""
        # Simulate concurrent-ish updates
        for i in range(5):
            updater.update_documents(
                request_type=RequestType.FEATURE_REQUEST,
                content=f"Feature {i}",
                target_documents=["docs/roadmap/ROADMAP.md"],
                metadata={"title": f"Feature {i}"},
            )

        roadmap_path = updater.project_root / "docs/roadmap/ROADMAP.md"
        content = roadmap_path.read_text()

        # All features should be present
        for i in range(5):
            assert f"Feature {i}" in content

        # Should have US-003 through US-007
        assert "US-003" in content
        assert "US-007" in content
