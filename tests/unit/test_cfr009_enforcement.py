"""Unit tests for CFR-009 Silent Background Agents enforcement.

CFR-009: ONLY user_listener can use sound notifications.
All other agents (code_developer, architect, project_manager, etc.)
must work silently in the background.

Tests verify:
1. user_listener CAN use sound=True
2. Background agents CANNOT use sound=True
3. Background agents CAN use sound=False
4. Proper exception raised on violation
5. Backward compatibility (agent_id=None)
"""

import pytest
from coffee_maker.cli.notifications import CFR009ViolationError, NotificationDB


@pytest.fixture
def notification_db():
    """Create a test notification database."""
    return NotificationDB()


class TestCFR009UserListener:
    """Tests for user_listener agent (UI-facing, can use sound)."""

    def test_user_listener_can_use_sound(self, notification_db):
        """user_listener CAN play sounds (CFR-009 compliant)."""
        # Should NOT raise
        notif_id = notification_db.create_notification(
            type="info",
            title="Test Notification",
            message="This is a test",
            sound=True,
            agent_id="user_listener",
        )
        assert notif_id > 0

        # Verify notification was created
        notif = notification_db.get_notification(notif_id)
        assert notif is not None
        assert notif["title"] == "Test Notification"

    def test_user_listener_silent_notification(self, notification_db):
        """user_listener can also create silent notifications."""
        notif_id = notification_db.create_notification(
            type="info",
            title="Silent Test",
            message="Silent notification",
            sound=False,
            agent_id="user_listener",
        )
        assert notif_id > 0


class TestCFR009BackgroundAgents:
    """Tests for background agents (code_developer, architect, etc.)."""

    def test_code_developer_cannot_use_sound(self, notification_db):
        """code_developer CANNOT play sounds (CFR-009 enforcement)."""
        with pytest.raises(CFR009ViolationError) as exc_info:
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="code_developer",
            )

        # Verify error message
        assert "CFR-009 VIOLATION" in str(exc_info.value)
        assert "code_developer" in str(exc_info.value)
        assert "sound=True" in str(exc_info.value)

    def test_architect_cannot_use_sound(self, notification_db):
        """architect CANNOT play sounds (CFR-009 enforcement)."""
        with pytest.raises(CFR009ViolationError) as exc_info:
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="architect",
            )
        assert "architect" in str(exc_info.value)

    def test_project_manager_cannot_use_sound(self, notification_db):
        """project_manager CANNOT play sounds (CFR-009 enforcement)."""
        with pytest.raises(CFR009ViolationError) as exc_info:
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="project_manager",
            )
        assert "project_manager" in str(exc_info.value)

    def test_assistant_cannot_use_sound(self, notification_db):
        """assistant CANNOT play sounds (CFR-009 enforcement)."""
        with pytest.raises(CFR009ViolationError) as exc_info:
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="assistant",
            )
        assert "assistant" in str(exc_info.value)

    def test_code_searcher_cannot_use_sound(self, notification_db):
        """code_searcher CANNOT play sounds (CFR-009 enforcement)."""
        with pytest.raises(CFR009ViolationError) as exc_info:
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="code_searcher",
            )
        assert "code_searcher" in str(exc_info.value)

    def test_ux_design_expert_cannot_use_sound(self, notification_db):
        """ux_design_expert CANNOT play sounds (CFR-009 enforcement)."""
        with pytest.raises(CFR009ViolationError) as exc_info:
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="ux_design_expert",
            )
        assert "ux_design_expert" in str(exc_info.value)


class TestCFR009BackgroundAgentsSilent:
    """Tests for background agents using silent notifications (compliant)."""

    def test_background_agents_silent(self, notification_db):
        """All background agents CAN use sound=False (CFR-009 compliant)."""
        agents = [
            "code_developer",
            "architect",
            "project_manager",
            "assistant",
            "code_searcher",
            "ux_design_expert",
        ]

        for agent in agents:
            # Should NOT raise
            notif_id = notification_db.create_notification(
                type="info",
                title=f"Test from {agent}",
                message="Testing silent notification",
                sound=False,
                agent_id=agent,
            )
            assert notif_id > 0

            # Verify notification was created
            notif = notification_db.get_notification(notif_id)
            assert notif is not None
            assert f"Test from {agent}" in notif["title"]


class TestCFR009BackwardCompatibility:
    """Tests for backward compatibility (agent_id=None)."""

    def test_no_agent_id_with_sound_true(self, notification_db):
        """Notification with sound=True and no agent_id should work (no validation)."""
        # agent_id=None → validation skipped (backward compatibility)
        notif_id = notification_db.create_notification(
            type="info",
            title="No agent_id test",
            message="Should work",
            sound=True,
            agent_id=None,
        )
        assert notif_id > 0

    def test_no_agent_id_with_sound_false(self, notification_db):
        """Notification with sound=False and no agent_id should work."""
        notif_id = notification_db.create_notification(
            type="info",
            title="Silent, no agent_id",
            message="Should work",
            sound=False,
            agent_id=None,
        )
        assert notif_id > 0

    def test_no_agent_id_no_sound_param(self, notification_db):
        """Notification with defaults (no agent_id, sound defaults to False)."""
        notif_id = notification_db.create_notification(
            type="info",
            title="Default test",
            message="Using all defaults",
        )
        assert notif_id > 0


class TestCFR009ErrorMessages:
    """Tests for CFR-009 violation error messages."""

    def test_error_message_clarity(self, notification_db):
        """Error message should be clear about CFR-009 violation."""
        with pytest.raises(CFR009ViolationError) as exc_info:
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="code_developer",
            )

        error_msg = str(exc_info.value)
        assert "CFR-009 VIOLATION" in error_msg
        assert "code_developer" in error_msg
        assert "cannot use sound=True" in error_msg
        assert "user_listener" in error_msg
        assert "Background agents must use sound=False" in error_msg

    def test_error_exception_type(self, notification_db):
        """Exception should be CFR009ViolationError type."""
        with pytest.raises(CFR009ViolationError):
            notification_db.create_notification(
                type="info",
                title="Test",
                message="Test",
                sound=True,
                agent_id="code_developer",
            )


class TestCFR009IntegrationWithNotifications:
    """Integration tests for CFR-009 with notification system."""

    def test_sound_false_default(self, notification_db):
        """Default sound should be False (silent by default)."""
        # Create without specifying sound parameter
        notif_id = notification_db.create_notification(
            type="info",
            title="Default sound test",
            message="Should be silent by default",
            agent_id="code_developer",
        )
        assert notif_id > 0

    def test_multiple_agents_mixed_sound_settings(self, notification_db):
        """Multiple agents with different sound settings."""
        # user_listener with sound
        user_notif = notification_db.create_notification(
            type="info",
            title="User notification",
            message="User listening",
            sound=True,
            agent_id="user_listener",
        )
        assert user_notif > 0

        # code_developer silent
        dev_notif = notification_db.create_notification(
            type="info",
            title="Developer notification",
            message="Developer working silently",
            sound=False,
            agent_id="code_developer",
        )
        assert dev_notif > 0

        # Verify both exist
        assert notification_db.get_notification(user_notif) is not None
        assert notification_db.get_notification(dev_notif) is not None

    def test_notification_priority_with_sound_enforcement(self, notification_db):
        """CFR-009 enforcement works with all priority levels."""
        priorities = ["critical", "high", "normal", "low"]

        for priority in priorities:
            # code_developer cannot use sound with any priority
            with pytest.raises(CFR009ViolationError):
                notification_db.create_notification(
                    type="info",
                    title=f"Test {priority}",
                    message="Test",
                    priority=priority,
                    sound=True,
                    agent_id="code_developer",
                )

            # But can use sound=False with any priority
            notif_id = notification_db.create_notification(
                type="info",
                title=f"Test {priority} silent",
                message="Test",
                priority=priority,
                sound=False,
                agent_id="code_developer",
            )
            assert notif_id > 0
