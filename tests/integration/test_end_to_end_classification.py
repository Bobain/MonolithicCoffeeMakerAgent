"""End-to-end integration tests for US-021 Phase 3.

These tests verify the complete workflow:
1. User provides input
2. RequestClassifier classifies the request
3. AIService processes with classification context
4. DocumentUpdater updates appropriate documents
5. Documents contain expected content
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.document_updater import DocumentUpdater
from coffee_maker.cli.request_classifier import RequestClassifier, RequestType


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project structure."""
    # Create docs directory with realistic files
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create ROADMAP.md
    roadmap_path = docs_dir / "ROADMAP.md"
    roadmap_path.write_text(
        """# Coffee Maker Agent - Prioritized Roadmap

**Last Updated**: 2025-10-15
**Status**: Testing

---

## US-001: Initial Feature

**Status**: ✅ **COMPLETE**
**Created**: 2025-10-01

---
"""
    )

    # Create COLLABORATION_METHODOLOGY.md
    collab_path = docs_dir / "COLLABORATION_METHODOLOGY.md"
    collab_path.write_text(
        """# Team Collaboration Methodology

## General Guidelines

Follow these guidelines.

## Workflows

Standard workflows.

---
"""
    )

    # Create .claude/CLAUDE.md
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    claude_path = claude_dir / "CLAUDE.md"
    claude_path.write_text(
        """# Claude Instructions

## Special Instructions for Claude

Instructions here.

---
"""
    )

    return tmp_path


@pytest.fixture
def classifier():
    """Create RequestClassifier instance."""
    return RequestClassifier()


@pytest.fixture
def updater(temp_project_root, monkeypatch):
    """Create DocumentUpdater with temp paths."""
    updater = DocumentUpdater(project_root=temp_project_root)
    monkeypatch.setattr(updater, "ROADMAP_PATH", Path("docs/ROADMAP.md"))
    monkeypatch.setattr(updater, "COLLABORATION_PATH", Path("docs/COLLABORATION_METHODOLOGY.md"))
    monkeypatch.setattr(updater, "CLAUDE_PATH", Path(".claude/CLAUDE.md"))
    return updater


class TestFeatureRequestWorkflow:
    """Test complete workflow for feature requests."""

    def test_feature_request_classification_and_update(self, classifier, updater, temp_project_root):
        """Test feature request is classified and ROADMAP is updated."""
        # 1. User provides input
        user_input = "I want to add email notifications for completed tasks"

        # 2. Classify the request
        classification = classifier.classify(user_input)

        assert classification.request_type == RequestType.FEATURE_REQUEST
        assert classification.confidence > 0.5
        assert "docs/ROADMAP.md" in classification.target_documents

        # 3. Update documents
        metadata = {
            "title": "Email Notifications",
            "business_value": "Keep users informed",
            "estimated_effort": "2-3 days",
        }

        result = updater.update_documents(
            request_type=classification.request_type,
            content=user_input,
            target_documents=classification.target_documents,
            metadata=metadata,
        )

        # 4. Verify update
        assert result["docs/ROADMAP.md"] is True

        # 5. Check ROADMAP content
        roadmap_path = temp_project_root / "docs/ROADMAP.md"
        roadmap_content = roadmap_path.read_text()

        assert "US-002" in roadmap_content  # Next US after US-001
        assert "Email Notifications" in roadmap_content
        assert "Keep users informed" in roadmap_content
        assert "2-3 days" in roadmap_content

    def test_feature_request_with_ai_service_mock(self, temp_project_root, monkeypatch):
        """Test feature request through AIService (with mocked API)."""
        # Create AIService with document updater
        with patch("coffee_maker.cli.ai_service.Anthropic") as mock_anthropic:
            # Mock AI response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = [Mock(text="Great! I'll add that to the roadmap.")]
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            # Patch ConfigManager to return dummy API key
            with patch(
                "coffee_maker.cli.ai_service.ConfigManager.get_anthropic_api_key",
                return_value="test-key",
            ):
                # Create service
                service = AIService(use_claude_cli=False)

                # Patch document updater to use temp directory
                service.document_updater = DocumentUpdater(project_root=temp_project_root)
                monkeypatch.setattr(service.document_updater, "ROADMAP_PATH", Path("docs/ROADMAP.md"))
                monkeypatch.setattr(
                    service.document_updater,
                    "COLLABORATION_PATH",
                    Path("docs/COLLABORATION_METHODOLOGY.md"),
                )
                monkeypatch.setattr(
                    service.document_updater,
                    "CLAUDE_PATH",
                    Path(".claude/CLAUDE.md"),
                )

                # Process request
                response = service.process_request(
                    user_input="I want to add Slack notifications",
                    context={},
                    history=[],
                    stream=False,
                )

                # Verify classification happened
                assert response.metadata is not None
                assert "classification" in response.metadata
                assert response.metadata["classification"]["request_type"] == "feature_request"

                # Verify document was updated
                assert "document_updates" in response.metadata
                assert response.metadata["document_updates"]["docs/ROADMAP.md"] is True

                # Verify ROADMAP content
                roadmap_path = temp_project_root / "docs/ROADMAP.md"
                roadmap_content = roadmap_path.read_text()
                assert "Slack notifications" in roadmap_content


class TestMethodologyChangeWorkflow:
    """Test complete workflow for methodology changes."""

    def test_methodology_classification_and_update(self, classifier, updater, temp_project_root):
        """Test methodology change is classified and docs are updated."""
        # 1. User provides input
        # Use strong methodology indicators to ensure classification
        user_input = "From now on, our team policy is that every pull request requires 2 approvals from senior developers before merging"

        # 2. Classify the request
        classification = classifier.classify(user_input)

        # This should be METHODOLOGY (has "from now on", "policy", "requires", "every")
        assert classification.request_type == RequestType.METHODOLOGY_CHANGE
        assert classification.confidence > 0.3  # Lower threshold since we have at least 1 indicator
        assert "docs/COLLABORATION_METHODOLOGY.md" in classification.target_documents

        # 3. Update documents
        metadata = {
            "title": "Technical Spec Requirement",
            "section": "Workflows",
            "rationale": "Improves planning and reduces rework",
        }

        result = updater.update_documents(
            request_type=classification.request_type,
            content=user_input,
            target_documents=classification.target_documents,
            metadata=metadata,
        )

        # 4. Verify updates
        assert result["docs/COLLABORATION_METHODOLOGY.md"] is True

        # 5. Check content
        collab_path = temp_project_root / "docs/COLLABORATION_METHODOLOGY.md"
        collab_content = collab_path.read_text()

        assert "Technical Spec Requirement" in collab_content
        assert "2 approvals" in collab_content  # Check for our actual input content


class TestHybridRequestWorkflow:
    """Test complete workflow for hybrid requests."""

    def test_hybrid_request_updates_both_docs(self, classifier, updater, temp_project_root):
        """Test hybrid request updates both ROADMAP and COLLABORATION."""
        # 1. User provides input
        user_input = "I want a code review bot and we should require 2 approvals"

        # 2. Classify the request
        classification = classifier.classify(user_input)

        assert classification.request_type == RequestType.HYBRID
        assert classification.confidence > 0.5
        assert len(classification.target_documents) == 2
        assert "docs/ROADMAP.md" in classification.target_documents
        assert "docs/COLLABORATION_METHODOLOGY.md" in classification.target_documents

        # 3. Update documents
        metadata = {
            "title": "Code Review Process",
            "business_value": "Improve code quality",
            "rationale": "Automated reviews catch bugs early",
        }

        result = updater.update_documents(
            request_type=classification.request_type,
            content=user_input,
            target_documents=classification.target_documents,
            metadata=metadata,
        )

        # 4. Verify both updates
        assert result["docs/ROADMAP.md"] is True
        assert result["docs/COLLABORATION_METHODOLOGY.md"] is True

        # 5. Check both documents
        roadmap_path = temp_project_root / "docs/ROADMAP.md"
        roadmap_content = roadmap_path.read_text()
        assert "Code Review Process" in roadmap_content

        collab_path = temp_project_root / "docs/COLLABORATION_METHODOLOGY.md"
        collab_content = collab_path.read_text()
        assert "Code Review Process" in collab_content


class TestClarificationWorkflow:
    """Test workflow when clarification is needed."""

    def test_clarification_needed_no_update(self, classifier, updater):
        """Test that ambiguous input triggers clarification (no update)."""
        # 1. Ambiguous user input
        user_input = "Something about the system"

        # 2. Classify the request
        classification = classifier.classify(user_input)

        assert classification.request_type == RequestType.CLARIFICATION_NEEDED
        assert len(classification.suggested_questions) > 0
        assert len(classification.target_documents) == 0

        # 3. No documents should be updated
        # (In real workflow, AIService would return clarification prompt first)


class TestBackupAndRecovery:
    """Test backup and recovery in end-to-end workflow."""

    def test_backup_created_during_workflow(self, classifier, updater, temp_project_root):
        """Test that backups are created during updates."""
        user_input = "I want to add GraphQL API support"

        classification = classifier.classify(user_input)

        # Check initial backup count
        initial_backups = len(list(updater.backup_dir.glob("ROADMAP_*.md")))

        # Update documents
        updater.update_documents(
            request_type=classification.request_type,
            content=user_input,
            target_documents=classification.target_documents,
            metadata={"title": "GraphQL API"},
        )

        # Verify backup was created
        final_backups = len(list(updater.backup_dir.glob("ROADMAP_*.md")))
        assert final_backups == initial_backups + 1

    def test_recovery_from_partial_failure(self, classifier, updater, temp_project_root, monkeypatch):
        """Test recovery when update partially fails."""
        user_input = "Test feature"
        classification = classifier.classify(user_input)

        # Save original ROADMAP content
        roadmap_path = temp_project_root / "docs/ROADMAP.md"
        original_content = roadmap_path.read_text()

        # Simulate error in update
        def mock_update_roadmap(*args, **kwargs):
            raise Exception("Simulated failure")

        monkeypatch.setattr(updater, "_update_roadmap", mock_update_roadmap)

        # Try update (should fail)
        try:
            updater.update_documents(
                request_type=classification.request_type,
                content=user_input,
                target_documents=classification.target_documents,
                metadata={"title": "Test"},
            )
        except Exception:
            pass  # Expected

        # Verify ROADMAP was restored
        current_content = roadmap_path.read_text()
        assert current_content == original_content


class TestMultipleSequentialUpdates:
    """Test multiple updates in sequence."""

    def test_multiple_feature_requests_sequentially(self, classifier, updater, temp_project_root):
        """Test adding multiple features sequentially."""
        features = [
            "I want to add email notifications",
            "I need CSV export functionality",
            "Add a dashboard for analytics",
        ]

        for i, feature in enumerate(features, start=1):
            classification = classifier.classify(feature)

            assert classification.request_type == RequestType.FEATURE_REQUEST

            updater.update_documents(
                request_type=classification.request_type,
                content=feature,
                target_documents=classification.target_documents,
                metadata={"title": f"Feature {i}"},
            )

        # Verify all features were added
        roadmap_path = temp_project_root / "docs/ROADMAP.md"
        roadmap_content = roadmap_path.read_text()

        assert "US-002" in roadmap_content
        assert "US-003" in roadmap_content
        assert "US-004" in roadmap_content
        assert "Feature 1" in roadmap_content
        assert "Feature 2" in roadmap_content
        assert "Feature 3" in roadmap_content


class TestMetadataExtraction:
    """Test metadata extraction in AIService."""

    def test_extract_title_from_user_input(self):
        """Test _extract_title method."""
        with patch("coffee_maker.cli.ai_service.Anthropic"):
            with patch(
                "coffee_maker.cli.ai_service.ConfigManager.get_anthropic_api_key",
                return_value="test-key",
            ):
                service = AIService(use_claude_cli=False)

                # Test various inputs
                assert service._extract_title("I want to add email notifications") == "Add email notifications"
                assert service._extract_title("We should implement GraphQL API") == "Implement GraphQL API"
                assert service._extract_title("Can we add a dashboard?") == "Add a dashboard?"

                # Test long input
                long_input = "I want to " + "A" * 100
                title = service._extract_title(long_input)
                assert len(title) <= 80

    def test_extract_metadata_for_feature_request(self):
        """Test _extract_metadata_from_response for feature requests."""
        with patch("coffee_maker.cli.ai_service.Anthropic"):
            with patch(
                "coffee_maker.cli.ai_service.ConfigManager.get_anthropic_api_key",
                return_value="test-key",
            ):
                service = AIService(use_claude_cli=False)

                # Mock classification
                from coffee_maker.cli.request_classifier import ClassificationResult

                classification = ClassificationResult(
                    request_type=RequestType.FEATURE_REQUEST,
                    confidence=0.85,
                    feature_indicators=["keyword: add"],
                    methodology_indicators=[],
                    suggested_questions=[],
                    target_documents=["docs/ROADMAP.md"],
                )

                metadata = service._extract_metadata_from_response(
                    user_input="I want to add email notifications",
                    ai_response="Great idea!",
                    classification=classification,
                )

                # Verify metadata structure
                assert "title" in metadata
                assert "business_value" in metadata
                assert "estimated_effort" in metadata
                assert "acceptance_criteria" in metadata
                assert isinstance(metadata["acceptance_criteria"], list)


class TestVerification:
    """Test verification of updates."""

    def test_verify_feature_added_to_roadmap(self, classifier, updater, temp_project_root):
        """Test verifying that feature was added to ROADMAP."""
        user_input = "I want to add REST API endpoints"
        classification = classifier.classify(user_input)

        updater.update_documents(
            request_type=classification.request_type,
            content=user_input,
            target_documents=classification.target_documents,
            metadata={"title": "REST API Endpoints"},
        )

        # Verify using updater's verification method
        assert updater.verify_update("docs/ROADMAP.md", "REST API Endpoints")
        assert updater.verify_update("docs/ROADMAP.md", "US-002")

    def test_verify_methodology_added_to_collaboration(self, classifier, updater, temp_project_root):
        """Test verifying that methodology was added to COLLABORATION."""
        user_input = "Always run tests before committing"
        classification = classifier.classify(user_input)

        updater.update_documents(
            request_type=classification.request_type,
            content=user_input,
            target_documents=classification.target_documents,
            metadata={"title": "Pre-Commit Testing"},
        )

        # Verify
        assert updater.verify_update("docs/COLLABORATION_METHODOLOGY.md", "Pre-Commit Testing")
