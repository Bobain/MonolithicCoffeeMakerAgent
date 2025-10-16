"""Unit tests for SpecTemplateManager.

Tests the template-based spec generation functionality for US-045 Phase 1.

Test cases:
    - Template loading
    - Placeholder substitution
    - Spec file creation
    - Directory handling
    - Error cases
"""

import tempfile
from pathlib import Path

import pytest

from coffee_maker.autonomous.spec_template_manager import SpecTemplateManager


class TestSpecTemplateManager:
    """Test suite for SpecTemplateManager."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            specs_dir = tmpdir / "specs"
            specs_dir.mkdir()

            # Create a minimal template
            template_path = specs_dir / "SPEC-000-template.md"
            template_content = """# SPEC-XXX: [Feature Name]

**Status**: Draft | In Review | Approved | Implemented | Deprecated

**Author**: architect agent

**Date Created**: YYYY-MM-DD

---

## Executive Summary

Brief 2-3 sentence summary of what this spec describes.

---

## Problem Statement

### Current Situation

Describe the current state and what problems exist.

### Goal

What are we trying to achieve?

### Non-Goals

What are we explicitly NOT trying to achieve?

---

## Proposed Solution

### High-Level Approach

Describe the solution at a high level.
"""
            template_path.write_text(template_content)

            yield {
                "tmpdir": tmpdir,
                "specs_dir": specs_dir,
                "template_path": template_path,
            }

    def test_manager_initialization(self, temp_dirs):
        """Test SpecTemplateManager initialization."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        assert manager.template_path == temp_dirs["template_path"]
        assert manager.specs_dir == temp_dirs["specs_dir"]

    def test_create_spec_from_template_success(self, temp_dirs):
        """Test successful spec creation from template."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        priority = {
            "name": "PRIORITY 9",
            "title": "Enhanced Communication",
            "content": "Improve inter-agent communication with enhanced metrics.",
        }

        result = manager.create_spec_from_template(
            priority=priority,
            spec_filename="SPEC-009-enhanced-communication.md",
        )

        assert result is True

        # Verify file was created
        spec_file = temp_dirs["specs_dir"] / "SPEC-009-enhanced-communication.md"
        assert spec_file.exists()

        # Verify content includes priority details
        content = spec_file.read_text()
        assert "Enhanced Communication" in content
        assert "PRIORITY 9" in content
        assert "TODO" in content or "Review" in content

    def test_create_spec_missing_priority_name(self, temp_dirs):
        """Test spec creation fails when priority name missing."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        priority = {
            "title": "Missing Name",
            "content": "This priority has no name field.",
        }

        result = manager.create_spec_from_template(
            priority=priority,
            spec_filename="SPEC-000-missing-name.md",
        )

        assert result is False

    def test_create_spec_empty_filename(self, temp_dirs):
        """Test spec creation fails with empty filename."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        priority = {
            "name": "PRIORITY 9",
            "title": "Test Priority",
            "content": "Test content",
        }

        result = manager.create_spec_from_template(
            priority=priority,
            spec_filename="",
        )

        assert result is False

    def test_create_spec_missing_template(self, temp_dirs):
        """Test spec creation fails when template doesn't exist."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["tmpdir"] / "nonexistent.md"),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        priority = {
            "name": "PRIORITY 9",
            "title": "Test",
            "content": "Test",
        }

        result = manager.create_spec_from_template(
            priority=priority,
            spec_filename="SPEC-009-test.md",
        )

        assert result is False

    def test_spec_file_contains_review_marker(self, temp_dirs):
        """Test that generated spec includes architect review marker."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        priority = {
            "name": "US-045",
            "title": "Fix Daemon Loop",
            "content": "Fix infinite loop in daemon spec creation.",
        }

        manager.create_spec_from_template(
            priority=priority,
            spec_filename="SPEC-045-fix-daemon.md",
        )

        spec_file = temp_dirs["specs_dir"] / "SPEC-045-fix-daemon.md"
        content = spec_file.read_text()

        assert "TODO" in content or "auto-generated" in content.lower()

    def test_extract_problem_statement(self, temp_dirs):
        """Test problem statement extraction."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        stmt = manager._extract_problem_statement(
            "PRIORITY 9",
            "Enhanced Communication",
            "Add metrics to inter-agent communication.",
        )

        assert "PRIORITY 9" in stmt
        assert "Enhanced Communication" in stmt
        assert "Add metrics" in stmt

    def test_extract_problem_statement_empty_content(self, temp_dirs):
        """Test problem statement extraction with empty content."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        stmt = manager._extract_problem_statement(
            "PRIORITY 9",
            "Test Title",
            "",
        )

        assert "PRIORITY 9" in stmt
        assert "Test Title" in stmt

    def test_generate_basic_architecture(self, temp_dirs):
        """Test basic architecture generation."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        priority = {
            "name": "PRIORITY 9",
            "title": "Communication",
        }

        arch = manager._generate_basic_architecture(priority)

        assert "Component" in arch
        assert "Integration" in arch
        assert "Testing" in arch

    def test_creates_specs_directory_if_missing(self, temp_dirs):
        """Test that manager creates specs directory if it doesn't exist."""
        new_specs_dir = temp_dirs["tmpdir"] / "new_specs"
        assert not new_specs_dir.exists()

        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(new_specs_dir),
        )

        priority = {
            "name": "PRIORITY 9",
            "title": "Test",
            "content": "Test content",
        }

        result = manager.create_spec_from_template(
            priority=priority,
            spec_filename="SPEC-009-test.md",
        )

        assert result is True
        assert new_specs_dir.exists()

    def test_spec_contains_priority_content(self, temp_dirs):
        """Test that generated spec includes priority content."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        priority = {
            "name": "US-999",
            "title": "New Feature",
            "content": "This is a new feature that does something important.",
        }

        manager.create_spec_from_template(
            priority=priority,
            spec_filename="SPEC-999-new-feature.md",
        )

        spec_file = temp_dirs["specs_dir"] / "SPEC-999-new-feature.md"
        content = spec_file.read_text()

        assert "US-999" in content
        assert "New Feature" in content
        assert "important" in content

    def test_multiple_specs_can_be_created(self, temp_dirs):
        """Test that multiple specs can be created without conflicts."""
        manager = SpecTemplateManager(
            template_path=str(temp_dirs["template_path"]),
            specs_dir=str(temp_dirs["specs_dir"]),
        )

        # Create first spec
        priority1 = {
            "name": "PRIORITY 1",
            "title": "First Feature",
            "content": "First feature content",
        }
        result1 = manager.create_spec_from_template(
            priority=priority1,
            spec_filename="SPEC-001-first.md",
        )

        # Create second spec
        priority2 = {
            "name": "PRIORITY 2",
            "title": "Second Feature",
            "content": "Second feature content",
        }
        result2 = manager.create_spec_from_template(
            priority=priority2,
            spec_filename="SPEC-002-second.md",
        )

        assert result1 is True
        assert result2 is True

        spec1 = temp_dirs["specs_dir"] / "SPEC-001-first.md"
        spec2 = temp_dirs["specs_dir"] / "SPEC-002-second.md"

        assert spec1.exists()
        assert spec2.exists()
        assert spec1.read_text() != spec2.read_text()
