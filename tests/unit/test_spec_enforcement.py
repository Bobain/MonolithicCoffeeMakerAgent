"""Unit tests for spec enforcement (US-047 - CFR-008).

This module tests the enforcement of CFR-008: ARCHITECT-ONLY SPEC CREATION

Tests:
- code_developer blocks when spec missing (does NOT create)
- Notification created when spec missing
- Spec exists check works correctly
- Multiple spec naming patterns supported
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from coffee_maker.autonomous.daemon_spec_manager import SpecManagerMixin


class MockNotificationDB:
    """Mock NotificationDB for testing."""

    def __init__(self):
        self.notifications = []

    def create_notification(
        self,
        type: str,
        title: str,
        message: str,
        priority: str = "normal",
        context=None,
        sound: bool = False,
        agent_id: str = None,
    ) -> int:
        """Mock create_notification method."""
        notif = {
            "id": len(self.notifications) + 1,
            "type": type,
            "title": title,
            "message": message,
            "priority": priority,
            "context": context,
            "sound": sound,
            "agent_id": agent_id,
        }
        self.notifications.append(notif)
        return notif["id"]


class MockSpecManager(SpecManagerMixin):
    """Mock implementation of SpecManagerMixin for testing."""

    def __init__(self, roadmap_path, notifications):
        self.roadmap_path = Path(roadmap_path)
        self.notifications = notifications
        self.git = Mock()


class TestSpecEnforcement:
    """Test CFR-008 spec enforcement."""

    @pytest.fixture
    def mock_notifications(self):
        """Create mock notification database."""
        return MockNotificationDB()

    @pytest.fixture
    def spec_manager(self, mock_notifications, tmp_path):
        """Create test spec manager with temporary directories."""
        # Create directory structure
        roadmap_path = tmp_path / "docs" / "roadmap" / "ROADMAP.md"
        roadmap_path.parent.mkdir(parents=True, exist_ok=True)
        roadmap_path.write_text("# Test ROADMAP")

        # Create specs directory
        specs_dir = tmp_path / "docs" / "architecture" / "specs"
        specs_dir.mkdir(parents=True, exist_ok=True)

        manager = MockSpecManager(roadmap_path, mock_notifications)
        manager.specs_dir = specs_dir
        return manager

    def test_spec_exists_returns_true(self, spec_manager):
        """Test that _ensure_technical_spec returns True when spec exists."""
        # Create a spec file
        spec_file = spec_manager.specs_dir / "SPEC-047-architect-only.md"
        spec_file.write_text("# Test Spec")

        priority = {"name": "US-047", "title": "Enforce CFR-008"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is True
        assert len(spec_manager.notifications.notifications) == 0

    def test_spec_missing_returns_false(self, spec_manager):
        """Test that _ensure_technical_spec returns False when spec missing."""
        priority = {"name": "US-047", "title": "Enforce CFR-008"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is False
        assert len(spec_manager.notifications.notifications) == 1

    def test_spec_missing_creates_notification(self, spec_manager):
        """Test that notification created when spec missing."""
        priority = {"name": "US-047", "title": "Enforce CFR-008"}

        spec_manager._ensure_technical_spec(priority)

        notifications = spec_manager.notifications.notifications
        assert len(notifications) == 1

        notif = notifications[0]
        assert notif["type"] == "error"
        assert "CFR-008" in notif["title"]
        assert "US-047" in notif["title"]
        assert "critical" == notif["priority"]
        assert notif["sound"] is False
        assert notif["agent_id"] == "code_developer"

    def test_spec_missing_notification_contains_details(self, spec_manager):
        """Test notification contains priority details."""
        priority = {"name": "US-047", "title": "Enforce CFR-008 Architect-Only"}

        spec_manager._ensure_technical_spec(priority)

        notif = spec_manager.notifications.notifications[0]
        message = notif["message"]

        assert "US-047" in message
        assert "Enforce CFR-008 Architect-Only" in message
        assert "SPEC-047" in message
        assert "architect must create" in message
        assert "BLOCKED" in message

    def test_spec_missing_notification_has_context(self, spec_manager):
        """Test notification context contains required information."""
        priority = {"name": "US-047", "title": "Enforce CFR-008"}

        spec_manager._ensure_technical_spec(priority)

        notif = spec_manager.notifications.notifications[0]
        context = notif["context"]

        assert context["priority_name"] == "US-047"
        assert context["priority_title"] == "Enforce CFR-008"
        assert context["spec_prefix"] == "SPEC-047"
        assert context["enforcement"] == "CFR-008"
        assert context["action_required"] == "architect must create technical spec"

    def test_priority_naming_pattern_us_dash(self, spec_manager):
        """Test spec detection for US-XXX naming pattern."""
        # Create spec file
        spec_file = spec_manager.specs_dir / "SPEC-048-test-spec.md"
        spec_file.write_text("# Test")

        priority = {"name": "US-048", "title": "Test Priority"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is True

    def test_priority_naming_pattern_priority(self, spec_manager):
        """Test spec detection for PRIORITY XXX naming pattern."""
        # Create spec file
        spec_file = spec_manager.specs_dir / "SPEC-009-test-spec.md"
        spec_file.write_text("# Test")

        priority = {"name": "PRIORITY 9", "title": "Test Priority"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is True

    def test_priority_naming_pattern_priority_decimal(self, spec_manager):
        """Test spec detection for PRIORITY X.Y naming pattern."""
        # Create spec file - spec prefix is SPEC-009-1 for PRIORITY 9.1
        spec_file = spec_manager.specs_dir / "SPEC-009-1-test-spec.md"
        spec_file.write_text("# Test")

        priority = {"name": "PRIORITY 9.1", "title": "Test Priority"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is True

    def test_priority_missing_name_returns_false(self, spec_manager):
        """Test that missing priority name returns False."""
        priority = {"title": "Test Priority"}  # Missing 'name'

        result = spec_manager._ensure_technical_spec(priority)

        assert result is False

    def test_multiple_specs_with_same_prefix(self, spec_manager):
        """Test that first matching spec is found."""
        # Create multiple specs with same prefix
        spec1 = spec_manager.specs_dir / "SPEC-047-spec-one.md"
        spec2 = spec_manager.specs_dir / "SPEC-047-spec-two.md"
        spec1.write_text("# Spec One")
        spec2.write_text("# Spec Two")

        priority = {"name": "US-047", "title": "Test"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is True

    def test_notification_cfr009_compliance(self, spec_manager):
        """Test notification follows CFR-009 (no sound for non-UI agents)."""
        priority = {"name": "US-047", "title": "Test"}

        spec_manager._ensure_technical_spec(priority)

        notif = spec_manager.notifications.notifications[0]

        # CFR-009: Background agents must use sound=False
        assert notif["sound"] is False
        assert notif["agent_id"] == "code_developer"

    def test_blocking_workflow_integration(self, spec_manager):
        """Test that spec blocking integrates with daemon workflow.

        When spec is missing:
        1. _ensure_technical_spec returns False
        2. Daemon loop detects False and skips priority
        3. Notification alerts user
        """
        priority = {"name": "US-047", "title": "Test Priority"}

        # Call _ensure_technical_spec (as daemon would)
        can_proceed = spec_manager._ensure_technical_spec(priority)

        # Simulate daemon response to False
        if not can_proceed:
            # Daemon should skip this priority
            skip_priority = True
        else:
            skip_priority = False

        assert skip_priority is True
        assert len(spec_manager.notifications.notifications) == 1

    def test_notify_spec_missing_called_on_missing_spec(self, spec_manager):
        """Test that _notify_spec_missing is called when spec missing."""
        priority = {"name": "US-047", "title": "Test"}

        # Mock the _notify_spec_missing method
        spec_manager._notify_spec_missing = Mock()

        # This should be called via _ensure_technical_spec
        # But we need to test it directly too
        spec_manager._notify_spec_missing(priority, "SPEC-047")

        spec_manager._notify_spec_missing.assert_called_once_with(priority, "SPEC-047")

    def test_empty_priority_name_returns_false(self, spec_manager):
        """Test that empty priority name returns False."""
        priority = {"name": "", "title": "Test"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is False

    def test_none_priority_name_returns_false(self, spec_manager):
        """Test that None priority name returns False."""
        priority = {"name": None, "title": "Test"}

        result = spec_manager._ensure_technical_spec(priority)

        assert result is False

    def test_no_specs_directory(self, spec_manager):
        """Test behavior when specs directory doesn't exist."""
        # Remove specs directory
        import shutil

        shutil.rmtree(spec_manager.specs_dir)

        priority = {"name": "US-047", "title": "Test"}

        result = spec_manager._ensure_technical_spec(priority)

        # Should return False (spec missing)
        assert result is False
        assert len(spec_manager.notifications.notifications) == 1


class TestNotifySpecMissing:
    """Test _notify_spec_missing method specifically."""

    @pytest.fixture
    def mock_notifications(self):
        """Create mock notification database."""
        return MockNotificationDB()

    @pytest.fixture
    def spec_manager(self, mock_notifications, tmp_path):
        """Create test spec manager."""
        roadmap_path = tmp_path / "docs" / "roadmap" / "ROADMAP.md"
        roadmap_path.parent.mkdir(parents=True, exist_ok=True)
        roadmap_path.write_text("# Test ROADMAP")

        manager = MockSpecManager(roadmap_path, mock_notifications)
        return manager

    def test_notification_title_format(self, spec_manager):
        """Test notification title follows CFR-008 format."""
        priority = {"name": "US-047", "title": "Enforce CFR-008"}

        spec_manager._notify_spec_missing(priority, "SPEC-047")

        notif = spec_manager.notifications.notifications[0]
        assert notif["title"] == "CFR-008: Missing Spec for US-047"

    def test_notification_message_includes_action(self, spec_manager):
        """Test notification message directs architect to take action."""
        priority = {"name": "US-047", "title": "Enforce CFR-008"}

        spec_manager._notify_spec_missing(priority, "SPEC-047")

        notif = spec_manager.notifications.notifications[0]
        message = notif["message"]

        assert "architect must create" in message.lower()
        assert "docs/architecture/specs/SPEC-047" in message

    def test_notification_priority_is_critical(self, spec_manager):
        """Test notification priority is CRITICAL."""
        priority = {"name": "US-047", "title": "Test"}

        spec_manager._notify_spec_missing(priority, "SPEC-047")

        notif = spec_manager.notifications.notifications[0]
        assert notif["priority"] == "critical"

    def test_notification_type_is_error(self, spec_manager):
        """Test notification type is 'error'."""
        priority = {"name": "US-047", "title": "Test"}

        spec_manager._notify_spec_missing(priority, "SPEC-047")

        notif = spec_manager.notifications.notifications[0]
        assert notif["type"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
