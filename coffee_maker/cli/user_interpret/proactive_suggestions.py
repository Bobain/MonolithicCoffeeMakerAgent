"""Generate proactive suggestions for user_listener."""

from typing import List, Dict, Any, Optional
import logging
from coffee_maker.cli.user_interpret.request_tracker import RequestTracker
from coffee_maker.cli.user_interpret.conversation_logger import ConversationLogger

logger = logging.getLogger(__name__)


class ProactiveSuggestions:
    """Generate proactive suggestions based on context.

    This class analyzes:
    - Recently completed requests (notify user proactively)
    - Pending request queue (provide status updates)
    - Conversation patterns (helpful tips)

    Example:
        suggester = ProactiveSuggestions()
        greeting = suggester.get_greeting_suggestions()
        for msg in greeting:
            print(msg)  # "Hey! The feature you requested is ready..."
    """

    def __init__(self):
        """Initialize proactive suggestions engine."""
        self.request_tracker = RequestTracker()
        self.conversation_logger = ConversationLogger()

    def get_greeting_suggestions(self) -> List[str]:
        """Get suggestions for user_listener greeting (when waking up).

        This is called when user_listener starts, providing proactive
        updates about completed work.

        Returns:
            List of short, proactive messages
        """
        suggestions = []

        # Check for recently completed requests
        completed = self.request_tracker.get_recently_completed(hours=24)

        for req in completed[:2]:  # Max 2 suggestions to avoid overwhelming
            if req["type"] == "feature":
                msg = f"✨ Hey! The feature you requested is ready: '{req['description']}'"
                if "result_location" in req:
                    msg += f" Check it out at: {req['result_location']}"
                suggestions.append(msg)

            elif req["type"] == "bug":
                msg = f"🔧 Good news! The bug you reported has been fixed: '{req['description']}'"
                if "result_location" in req:
                    msg += f" Details at: {req['result_location']}"
                suggestions.append(msg)

            elif req["type"] == "documentation":
                msg = f"📚 The documentation you asked for is ready: '{req['description']}'"
                if "result_location" in req:
                    msg += f" Available at: {req['result_location']}"
                suggestions.append(msg)

        # Check for pending requests (status update)
        pending = self.request_tracker.get_pending_requests()
        if len(pending) > 3:
            suggestions.append(
                f"📋 Just so you know, I'm tracking {len(pending)} pending requests for you. "
                "Let me know if you want a status update!"
            )

        # Check conversation patterns for helpful tips
        recent = self.conversation_logger.get_recent_conversations(limit=10)
        if recent:
            last_intent = recent[-1]["intent"]
            if last_intent == "add_feature":
                suggestions.append(
                    "💡 Tip: Once your feature is implemented, I can help you write tests for it!"
                )
            elif last_intent == "report_bug":
                suggestions.append(
                    "💡 Tip: I can create a GitHub issue for this bug if you'd like better tracking!"
                )

        return suggestions

    def get_contextual_suggestions(self, user_message: str) -> List[str]:
        """Get suggestions based on current message context.

        This is called during conversation to provide helpful tips
        based on what the user is asking about.

        Args:
            user_message: Current user message

        Returns:
            List of relevant suggestions
        """
        suggestions = []
        message_lower = user_message.lower()

        # If asking about status, suggest specific updates
        if "status" in message_lower or "progress" in message_lower:
            pending = self.request_tracker.get_pending_requests()
            if pending:
                suggestions.append(
                    f"I'm tracking {len(pending)} pending items. "
                    "Want details on any specific request?"
                )

        # If asking about roadmap, suggest relevant docs
        if "roadmap" in message_lower:
            suggestions.append(
                "📍 Pro tip: You can also check real-time status with "
                "`poetry run project-manager developer-status`"
            )

        # If asking about tests
        if "test" in message_lower or "testing" in message_lower:
            suggestions.append(
                "💡 Pro tip: Run `pytest -v` to see detailed test output, "
                "or `pytest --cov` for coverage reports"
            )

        # If asking about documentation
        if "docs" in message_lower or "documentation" in message_lower:
            suggestions.append(
                "📚 Pro tip: Check docs/ROADMAP.md for planned work, "
                "and docs/PRIORITY_*_TECHNICAL_SPEC.md for detailed specs"
            )

        # If expressing frustration
        recent = self.conversation_logger.get_recent_conversations(limit=5)
        if recent:
            last_signals = recent[-1].get("sentiment_signals", [])
            has_frustration = any(
                s.get("sentiment") == "frustration" for s in last_signals
            )
            if has_frustration:
                suggestions.append(
                    "I noticed you might be frustrated. I'm here to help! "
                    "Feel free to ask for clarification or a different approach."
                )

        return suggestions

    def get_completion_notification(self, request_id: str) -> Optional[str]:
        """Get notification message for completed request.

        This is called when a request is marked complete, generating
        a proactive notification for the user.

        Args:
            request_id: Request ID that was completed

        Returns:
            Notification message or None
        """
        request = self.request_tracker.get_request(request_id)
        if not request or request["status"] != "completed":
            return None

        req_type = request["type"]
        description = request["description"]
        result_location = request.get("result_location")

        if req_type == "feature":
            msg = f"✨ Great news! The feature you requested is ready: '{description}'"
            if result_location:
                msg += f"\n\n📖 Tutorial available at: {result_location}"
                msg += (
                    "\n\nThe feature has been tested and is ready for you to try out!"
                )
        elif req_type == "bug":
            msg = f"🔧 Bug fix complete! '{description}' has been resolved"
            if result_location:
                msg += f"\n\n📝 Fix details at: {result_location}"
        elif req_type == "documentation":
            msg = f"📚 Documentation ready! '{description}'"
            if result_location:
                msg += f"\n\n📖 Available at: {result_location}"
        else:
            msg = f"✅ Your request has been completed: '{description}'"

        return msg

    def get_pending_summary(self) -> Dict[str, Any]:
        """Get summary of all pending requests.

        Returns:
            Summary with counts by type and agent
        """
        pending = self.request_tracker.get_pending_requests()

        summary = {
            "total_pending": len(pending),
            "by_type": {},
            "by_agent": {},
            "oldest_request": None,
        }

        if not pending:
            return summary

        for req in pending:
            req_type = req["type"]
            summary["by_type"][req_type] = summary["by_type"].get(req_type, 0) + 1

            agent = req["delegated_to"]
            summary["by_agent"][agent] = summary["by_agent"].get(agent, 0) + 1

        # Find oldest request
        oldest = min(pending, key=lambda r: r["created_at"])
        summary["oldest_request"] = {
            "id": oldest["id"],
            "description": oldest["description"],
            "created_at": oldest["created_at"],
        }

        return summary
