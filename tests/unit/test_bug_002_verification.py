"""Unit tests for BUG-002 verification.

BUG-002: Daemon crashes when priority has no technical spec or missing content
Fix: Safe dictionary access with .get() and validation

These tests verify that:
1. _ensure_technical_spec handles missing priority fields gracefully
2. No KeyError when priority dict is missing 'name' or 'content'
3. Appropriate warnings/errors are logged
4. Daemon continues operation without crashing
"""

import pytest
import logging
from unittest.mock import patch
from pathlib import Path

from coffee_maker.autonomous.daemon_spec_manager import SpecManagerMixin
from coffee_maker.cli.notifications import NotificationDB


class MockDaemon(SpecManagerMixin):
    """Mock daemon class for testing SpecManagerMixin."""

    def __init__(self, roadmap_path: Path):
        """Initialize mock daemon with required attributes."""
        self.roadmap_path = roadmap_path
        self.notifications = NotificationDB()


class TestBug002Verification:
    """Verify BUG-002 fix: graceful handling of missing priority content."""

    @pytest.fixture
    def mock_daemon(self, tmp_path):
        """Create mock daemon instance for testing with proper directory structure."""
        # Create directory structure: tmp/docs/roadmap/ROADMAP.md
        roadmap_dir = tmp_path / "docs" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        roadmap_path = roadmap_dir / "ROADMAP.md"
        roadmap_path.touch()

        # Create specs directory: tmp/docs/architecture/specs/
        spec_dir = tmp_path / "docs" / "architecture" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        return MockDaemon(roadmap_path)

    @pytest.fixture
    def mock_spec_dir(self, tmp_path):
        """Get spec directory path (created by mock_daemon fixture)."""
        spec_dir = tmp_path / "docs" / "architecture" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        return spec_dir

    def test_ensure_technical_spec_missing_name(self, mock_daemon, caplog):
        """Test _ensure_technical_spec rejects priority without name field.

        BUG-002: Code used to crash with KeyError when priority['name'] missing.
        Fix: Use priority.get("name") and validate before accessing.
        """
        # Given: Priority without name field (malformed)
        priority = {"content": "Some content", "title": "Test Priority"}

        # When: Ensuring technical spec with missing name
        with caplog.at_level(logging.ERROR):
            result = mock_daemon._ensure_technical_spec(priority)

        # Then: Returns False and logs error (no crash!)
        assert result is False, "Should return False for priority without name"
        assert "missing 'name' field" in caplog.text, "Should log error about missing name field"

    def test_ensure_technical_spec_handles_missing_content(self, mock_daemon, caplog, mock_spec_dir):
        """Test _ensure_technical_spec logs warning for missing content.

        BUG-002: Code used to crash when accessing priority['content'][:2000]
        if content was None or missing.
        Fix: Use priority.get("content", "") with safe access.
        """
        # Given: Priority with name but no content (valid but minimal)
        priority = {
            "name": "PRIORITY 99",
            "title": "Test Priority",
            # No 'content' field
        }

        # Mock notification creation
        with patch.object(mock_daemon.notifications, "create_notification"):
            # When: Ensuring technical spec with missing content
            result = mock_daemon._ensure_technical_spec(priority)

        # Then: Should handle gracefully (no crash, just returns False since spec doesn't exist)
        # The important part is NO KeyError or TypeError
        assert result is False, "Should return False when spec doesn't exist (not crash!)"

    def test_ensure_technical_spec_none_content(self, mock_daemon, mock_spec_dir):
        """Test _ensure_technical_spec handles None content.

        BUG-002 edge case: content field exists but is None.
        """
        # Given: Priority with None content
        priority = {"name": "PRIORITY 99", "title": "Test Priority", "content": None}

        # Mock notification creation
        with patch.object(mock_daemon.notifications, "create_notification"):
            # When: Ensuring technical spec
            result = mock_daemon._ensure_technical_spec(priority)

        # Then: No crash (the critical test!)
        assert isinstance(result, bool), "Should return boolean without crashing on None content"

    def test_ensure_technical_spec_empty_content(self, mock_daemon, mock_spec_dir):
        """Test _ensure_technical_spec handles empty string content.

        BUG-002 edge case: content field is empty string.
        """
        # Given: Priority with empty string content
        priority = {"name": "PRIORITY 99", "title": "Test Priority", "content": ""}

        # Mock notification creation
        with patch.object(mock_daemon.notifications, "create_notification"):
            # When: Ensuring technical spec
            result = mock_daemon._ensure_technical_spec(priority)

        # Then: No crash (handles empty content gracefully)
        assert isinstance(result, bool), "Should return boolean without crashing on empty content"

    def test_ensure_technical_spec_with_valid_priority(self, mock_daemon, mock_spec_dir):
        """Test _ensure_technical_spec works with well-formed priority.

        Regression test: ensure fix doesn't break normal operation.
        """
        # Given: Well-formed priority
        priority = {
            "name": "PRIORITY 99",
            "title": "Test Priority",
            "content": "This is a detailed description of the priority.",
        }

        # Create a spec file that should be found
        spec_file = mock_spec_dir / "SPEC-099-test.md"
        spec_file.write_text("# SPEC-099: Test\n\nTest spec content")

        # When: Ensuring technical spec
        result = mock_daemon._ensure_technical_spec(priority)

        # Then: Should find spec and return True
        assert result is True, "Should return True when spec exists for well-formed priority"

    def test_ensure_technical_spec_spec_not_found(self, mock_daemon, mock_spec_dir, caplog):
        """Test _ensure_technical_spec blocks when spec missing.

        BUG-002: Should handle missing spec gracefully, not crash.
        """
        # Given: Valid priority but spec doesn't exist
        priority = {"name": "PRIORITY 88", "title": "Priority Without Spec", "content": "Some content"}

        # Mock notification creation
        with patch.object(mock_daemon.notifications, "create_notification"):
            # When: Ensuring technical spec
            with caplog.at_level(logging.ERROR):
                result = mock_daemon._ensure_technical_spec(priority)

        # Then: Should block (return False) and log error
        assert result is False, "Should return False when spec doesn't exist"
        assert "CFR-008" in caplog.text, "Should log CFR-008 enforcement message"
        assert "BLOCKING" in caplog.text, "Should indicate implementation is blocked"

    def test_notify_spec_missing_handles_missing_fields(self, mock_daemon):
        """Test _notify_spec_missing handles priority with missing fields.

        BUG-002: Should use .get() for all priority field access.
        """
        # Given: Priority with missing title
        priority = {
            "name": "PRIORITY 77"
            # Missing 'title' field
        }

        # Mock notification manager
        with patch.object(mock_daemon.notifications, "create_notification") as mock_create:
            # When: Notifying about missing spec
            mock_daemon._notify_spec_missing(priority, "SPEC-077")

            # Then: Should not crash and should have called create_notification
            mock_create.assert_called_once()

            # Verify it used safe defaults for missing fields
            call_args = mock_create.call_args
            message = call_args[1]["message"]
            assert "Unknown Title" in message, "Should use 'Unknown Title' default for missing title"

    def test_notify_spec_missing_handles_completely_empty_priority(self, mock_daemon):
        """Test _notify_spec_missing handles priority with no fields.

        BUG-002 extreme case: priority dict is nearly empty.
        """
        # Given: Minimal priority (worst case)
        priority = {}

        # Mock notification manager
        with patch.object(mock_daemon.notifications, "create_notification") as mock_create:
            # When: Notifying about missing spec
            try:
                mock_daemon._notify_spec_missing(priority, "SPEC-000")
                no_crash = True
            except (KeyError, TypeError, AttributeError):
                no_crash = False

            # Then: Should not crash (the critical assertion)
            assert no_crash, "Should handle empty priority dict without crashing"

    def test_ensure_technical_spec_with_us_prefix(self, mock_daemon, mock_spec_dir):
        """Test spec prefix extraction for US-* priorities.

        Verifies BUG-002 fix works with different priority name formats.
        """
        # Given: Priority with US- prefix
        priority = {"name": "US-045", "title": "Some User Story", "content": "Description"}

        # Create matching spec
        spec_file = mock_spec_dir / "SPEC-045-test.md"
        spec_file.write_text("# SPEC-045\n\nContent")

        # When: Ensuring technical spec
        result = mock_daemon._ensure_technical_spec(priority)

        # Then: Should extract correct spec number and find spec
        assert result is True, "Should find spec for US-045 priority"

    def test_ensure_technical_spec_with_decimal_priority(self, mock_daemon, mock_spec_dir):
        """Test spec prefix extraction for PRIORITY X.Y format.

        Verifies BUG-002 fix works with sub-priority numbering.
        """
        # Given: Priority with decimal format
        priority = {"name": "PRIORITY 2.6", "title": "Daemon Fix Verification", "content": "Verify fixes work"}

        # Create matching spec
        spec_file = mock_spec_dir / "SPEC-002-6-daemon-fix.md"
        spec_file.write_text("# SPEC-002-6\n\nContent")

        # When: Ensuring technical spec
        result = mock_daemon._ensure_technical_spec(priority)

        # Then: Should extract correct spec prefix (002-6) and find spec
        assert result is True, "Should find spec for PRIORITY 2.6"


# Run with: pytest tests/unit/test_bug_002_verification.py -v
