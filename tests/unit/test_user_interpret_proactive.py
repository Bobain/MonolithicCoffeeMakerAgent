"""Tests for user_interpret proactive intelligence.

Tests cover:
- ConversationLogger
- RequestTracker
- ProactiveSuggestions
- Integration with UserInterpret
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from coffee_maker.cli.user_interpret.conversation_logger import ConversationLogger
from coffee_maker.cli.user_interpret.request_tracker import RequestTracker
from coffee_maker.cli.user_interpret.proactive_suggestions import ProactiveSuggestions


@pytest.fixture
def temp_docs_dir():
    """Create temporary docs directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestConversationLogger:
    """Tests for ConversationLogger."""

    def test_log_conversation_creates_entry(self, temp_docs_dir):
        """Test logging creates proper entry."""
        logger = ConversationLogger(docs_dir=temp_docs_dir)

        entry = logger.log_conversation(
            user_message="add a login feature",
            intent="add_feature",
            delegated_to="code_developer",
            sentiment_signals=[],
            confidence=0.9,
        )

        assert "timestamp" in entry
        assert entry["intent"] == "add_feature"
        assert entry["delegated_to"] == "code_developer"
        assert entry["confidence"] == 0.9
        assert "conversation_id" in entry

    def test_log_conversation_appends_to_file(self, temp_docs_dir):
        """Test multiple logs append to same file."""
        logger = ConversationLogger(docs_dir=temp_docs_dir)

        logger.log_conversation("msg 1", "intent1", "agent1", [], 0.8)
        logger.log_conversation("msg 2", "intent2", "agent2", [], 0.9)

        recent = logger.get_recent_conversations(limit=10)
        assert len(recent) == 2
        assert recent[0]["user_message"] == "msg 1"
        assert recent[1]["user_message"] == "msg 2"

    def test_get_recent_conversations_limits(self, temp_docs_dir):
        """Test limit parameter works."""
        logger = ConversationLogger(docs_dir=temp_docs_dir)

        # Log 5 conversations
        for i in range(5):
            logger.log_conversation(f"msg {i}", "intent", "agent", [], 0.8)

        recent = logger.get_recent_conversations(limit=3)
        assert len(recent) == 3
        assert recent[-1]["user_message"] == "msg 4"

    def test_get_conversations_by_intent(self, temp_docs_dir):
        """Test filtering by intent."""
        logger = ConversationLogger(docs_dir=temp_docs_dir)

        logger.log_conversation("feature req", "add_feature", "agent", [], 0.9)
        logger.log_conversation("bug report", "report_bug", "agent", [], 0.8)
        logger.log_conversation("another feature", "add_feature", "agent", [], 0.9)

        features = logger.get_conversations_by_intent("add_feature")
        assert len(features) == 2
        assert all(c["intent"] == "add_feature" for c in features)

    def test_summarize_recent_activity(self, temp_docs_dir):
        """Test activity summary generation."""
        logger = ConversationLogger(docs_dir=temp_docs_dir)

        logger.log_conversation("msg1", "add_feature", "code_developer", [], 0.9)
        logger.log_conversation("msg2", "add_feature", "code_developer", [], 0.8)
        logger.log_conversation("msg3", "report_bug", "code_developer", [], 0.7)

        summary = logger.summarize_recent_activity(days=7)

        assert summary["total_conversations"] == 3
        assert summary["intents"]["add_feature"] == 2
        assert summary["intents"]["report_bug"] == 1
        assert summary["agents_used"]["code_developer"] == 3
        assert 0.7 <= summary["avg_confidence"] <= 0.9


class TestRequestTracker:
    """Tests for RequestTracker."""

    def test_add_request_creates_entry(self, temp_docs_dir):
        """Test adding request."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)

        request_id = tracker.add_request(
            request_type="feature",
            description="Login feature",
            user_message="add a login feature",
            delegated_to="code_developer",
        )

        assert request_id.startswith("feature_")

        # Verify it's in pending
        pending = tracker.get_pending_requests()
        assert len(pending) == 1
        assert pending[0]["id"] == request_id
        assert pending[0]["status"] == "pending"

    def test_mark_completed(self, temp_docs_dir):
        """Test marking request complete."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)

        request_id = tracker.add_request("feature", "Test", "test msg", "agent")
        tracker.mark_completed(request_id, result_location="/docs/tutorial.md")

        # Should not be in pending
        pending = tracker.get_pending_requests()
        assert len(pending) == 0

        # Should be in recently completed
        completed = tracker.get_recently_completed(hours=1)
        assert len(completed) == 1
        assert completed[0]["id"] == request_id
        assert completed[0]["status"] == "completed"
        assert completed[0]["result_location"] == "/docs/tutorial.md"

    def test_get_recently_completed_filters_by_time(self, temp_docs_dir):
        """Test time filtering for completed requests."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)

        req_id = tracker.add_request("feature", "Test", "test", "agent")
        tracker.mark_completed(req_id)

        # Should find it within 24 hours
        recent = tracker.get_recently_completed(hours=24)
        assert len(recent) == 1

        # Manually modify timestamp to be old (hack for testing)
        for category in tracker.requests.values():
            if isinstance(category, list):
                for req in category:
                    if req["id"] == req_id:
                        old_time = datetime.now() - timedelta(hours=48)
                        req["completed_at"] = old_time.isoformat()
        tracker._save_requests()

        # Should not find it within 24 hours
        recent = tracker.get_recently_completed(hours=24)
        assert len(recent) == 0

    def test_get_request(self, temp_docs_dir):
        """Test retrieving specific request."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)

        req_id = tracker.add_request("bug", "Test bug", "test", "agent")

        request = tracker.get_request(req_id)
        assert request is not None
        assert request["id"] == req_id
        assert request["type"] == "bug"

    def test_update_status(self, temp_docs_dir):
        """Test updating request status."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)

        req_id = tracker.add_request("feature", "Test", "test", "agent")
        tracker.update_status(req_id, "in_progress", notes="Started work")

        request = tracker.get_request(req_id)
        assert request["status"] == "in_progress"
        assert len(request["notes"]) == 1
        assert request["notes"][0]["text"] == "Started work"


class TestProactiveSuggestions:
    """Tests for ProactiveSuggestions."""

    def test_greeting_suggestions_for_completed_requests(self, temp_docs_dir):
        """Test greeting suggestions show completed work."""
        # Setup: Create completed request
        tracker = RequestTracker(docs_dir=temp_docs_dir)
        req_id = tracker.add_request("feature", "Login system", "add login", "agent")
        tracker.mark_completed(req_id, result_location="/docs/login_tutorial.md")

        # Create suggester
        suggester = ProactiveSuggestions()
        suggester.request_tracker = tracker  # Use our test tracker

        greeting = suggester.get_greeting_suggestions()

        assert len(greeting) > 0
        assert any(
            "ready" in s.lower() or "login system" in s.lower() for s in greeting
        )

    def test_greeting_suggestions_for_pending_queue(self, temp_docs_dir):
        """Test greeting mentions pending queue."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)

        # Add many pending requests
        for i in range(5):
            tracker.add_request("feature", f"Feature {i}", f"msg {i}", "agent")

        suggester = ProactiveSuggestions()
        suggester.request_tracker = tracker

        greeting = suggester.get_greeting_suggestions()

        # Should mention pending requests
        assert any("pending" in s.lower() for s in greeting)

    def test_contextual_suggestions_for_status_query(self, temp_docs_dir):
        """Test contextual suggestions for status questions."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)
        tracker.add_request("feature", "Test", "test", "agent")

        suggester = ProactiveSuggestions()
        suggester.request_tracker = tracker

        contextual = suggester.get_contextual_suggestions("what's the status?")

        assert len(contextual) > 0
        assert any("pending" in s.lower() for s in contextual)

    def test_contextual_suggestions_for_roadmap_query(self, temp_docs_dir):
        """Test contextual suggestions for roadmap."""
        suggester = ProactiveSuggestions()
        suggester.request_tracker = RequestTracker(docs_dir=temp_docs_dir)

        contextual = suggester.get_contextual_suggestions("show me the roadmap")

        assert len(contextual) > 0
        assert any("roadmap" in s.lower() or "status" in s.lower() for s in contextual)

    def test_get_completion_notification(self, temp_docs_dir):
        """Test completion notification messages."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)
        req_id = tracker.add_request("feature", "Auth system", "add auth", "agent")
        tracker.mark_completed(req_id, result_location="/docs/auth_tutorial.md")

        suggester = ProactiveSuggestions()
        suggester.request_tracker = tracker

        notification = suggester.get_completion_notification(req_id)

        assert notification is not None
        assert "Auth system" in notification
        assert "/docs/auth_tutorial.md" in notification

    def test_get_pending_summary(self, temp_docs_dir):
        """Test pending summary statistics."""
        tracker = RequestTracker(docs_dir=temp_docs_dir)
        tracker.add_request("feature", "F1", "f1", "code_developer")
        tracker.add_request("feature", "F2", "f2", "code_developer")
        tracker.add_request("bug", "B1", "b1", "code_developer")
        tracker.add_request("documentation", "D1", "d1", "project_manager")

        suggester = ProactiveSuggestions()
        suggester.request_tracker = tracker

        summary = suggester.get_pending_summary()

        assert summary["total_pending"] == 4
        assert summary["by_type"]["feature"] == 2
        assert summary["by_type"]["bug"] == 1
        assert summary["by_type"]["documentation"] == 1
        assert summary["by_agent"]["code_developer"] == 3
        assert summary["by_agent"]["project_manager"] == 1
        assert summary["oldest_request"] is not None


class TestUserInterpretIntegration:
    """Integration tests for UserInterpret with proactive intelligence.

    NOTE: Due to namespace collision between user_interpret.py file and
    user_interpret/ package, these tests verify component integration
    without importing UserInterpret directly.
    """

    def test_components_integrate_correctly(self, temp_docs_dir):
        """Test that components work together."""
        # Create components
        logger = ConversationLogger(docs_dir=temp_docs_dir)
        tracker = RequestTracker(docs_dir=temp_docs_dir)
        suggester = ProactiveSuggestions()
        suggester.conversation_logger = logger
        suggester.request_tracker = tracker

        # Simulate conversation logging
        logger.log_conversation(
            user_message="add a login feature",
            intent="add_feature",
            delegated_to="code_developer",
            sentiment_signals=[],
            confidence=0.9,
        )

        # Track request
        req_id = tracker.add_request(
            request_type="feature",
            description="Login feature",
            user_message="add a login feature",
            delegated_to="code_developer",
        )

        # Verify integration
        recent = logger.get_recent_conversations()
        assert len(recent) > 0
        assert recent[-1]["intent"] == "add_feature"

        pending = tracker.get_pending_requests()
        assert len(pending) > 0

    def test_proactive_flow_end_to_end(self, temp_docs_dir):
        """Test complete proactive flow."""
        # Create components
        tracker = RequestTracker(docs_dir=temp_docs_dir)
        suggester = ProactiveSuggestions()
        suggester.request_tracker = tracker
        suggester.conversation_logger = ConversationLogger(docs_dir=temp_docs_dir)

        # Create and complete request
        req_id = tracker.add_request(
            "feature", "Dashboard UI", "add dashboard", "ux_design_expert"
        )
        tracker.mark_completed(req_id, "/docs/dashboard_tutorial.md")

        # Get greeting suggestions
        greeting = suggester.get_greeting_suggestions()

        assert len(greeting) > 0
        assert any("Dashboard UI" in s or "ready" in s for s in greeting)

        # Get completion notification
        notification = suggester.get_completion_notification(req_id)
        assert notification is not None
        assert "Dashboard UI" in notification

    def test_conversation_and_request_tracking_together(self, temp_docs_dir):
        """Test conversation logging with request tracking."""
        logger = ConversationLogger(docs_dir=temp_docs_dir)
        tracker = RequestTracker(docs_dir=temp_docs_dir)

        # Log multiple conversations
        logger.log_conversation("feature 1", "add_feature", "code_developer", [], 0.9)
        logger.log_conversation("feature 2", "add_feature", "code_developer", [], 0.8)
        logger.log_conversation("bug fix", "report_bug", "code_developer", [], 0.7)

        # Track corresponding requests
        tracker.add_request("feature", "Feature 1", "feature 1", "code_developer")
        tracker.add_request("feature", "Feature 2", "feature 2", "code_developer")
        tracker.add_request("bug", "Bug fix", "bug fix", "code_developer")

        # Verify
        summary = logger.summarize_recent_activity(days=1)
        assert summary["total_conversations"] == 3
        assert summary["intents"]["add_feature"] == 2

        pending = tracker.get_pending_requests()
        assert len(pending) == 3
