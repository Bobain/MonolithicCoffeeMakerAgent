"""user_interpret agent with AUTOMATIC ACE integration.

This agent uses the ACEAgent base class for automatic ACE supervision.
NO manual wrapper needed - ACE integration is automatic!

IMPORTANT: This is the v2 implementation showing the new pattern.
Once validated, this will replace user_interpret.py and user_interpret_ace.py.
"""

import logging
from typing import Dict, Any, Optional, List
from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent
from coffee_maker.cli.sentiment_analyzer import SentimentAnalyzer, SentimentSignal

logger = logging.getLogger(__name__)


class UserInterpret(ACEAgent):
    """user_interpret with automatic ACE integration.

    Inheriting from ACEAgent provides automatic:
    - ACE_ENABLED_USER_INTERPRET environment variable checking
    - ACEGenerator initialization if enabled
    - Trace generation for all executions
    - Consistent send_message() interface

    Usage:
        agent = UserInterpret()
        result = agent.execute_task("add a login feature")

        # That's it! ACE is automatic if ACE_ENABLED_USER_INTERPRET=true
    """

    @property
    def agent_name(self) -> str:
        """Agent name for ACE."""
        return "user_interpret"

    @property
    def agent_objective(self) -> str:
        """Agent objective for ACE context."""
        return "Interpret user intent, analyze sentiment, and delegate to appropriate agents"

    @property
    def success_criteria(self) -> str:
        """Success criteria for ACE evaluation."""
        return "Correct intent interpretation, accurate sentiment detection, appropriate agent delegation"

    def __init__(self):
        """Initialize user_interpret agent."""
        # Initialize ACE (automatic via base class)
        super().__init__()

        # Skip agent-specific initialization if already initialized (singleton)
        if hasattr(self, "_agent_initialized") and self._agent_initialized:
            logger.debug(
                "UserInterpret agent-specific components already initialized (singleton)"
            )
            return

        # Initialize agent-specific components
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversation_history: List[str] = []

        # NEW: Proactive intelligence components
        from coffee_maker.cli.user_interpret import (
            ConversationLogger,
            RequestTracker,
            ProactiveSuggestions,
        )

        self.conversation_logger = ConversationLogger()
        self.request_tracker = RequestTracker()
        self.proactive_suggestions = ProactiveSuggestions()

        # Mark agent-specific init as complete
        self._agent_initialized = True

        logger.info(
            "UserInterpret initialized (with automatic ACE + proactive intelligence)"
        )

    def _execute_implementation(
        self, user_message: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Core interpretation logic.

        This is called by:
        - execute_task() when ACE disabled (direct)
        - send_message() when ACE enabled (via generator)

        Args:
            user_message: Raw user input
            context: Optional context (recent messages, user history, etc.)

        Returns:
            Interpretation result with delegation decision
        """
        # Set plan (generator will capture this) - NEW
        self._set_plan(
            [
                "Analyze user sentiment",
                "Interpret user intent",
                "Choose appropriate agent",
                "Generate response",
            ]
        )

        # Track conversation
        self.conversation_history.append(user_message)
        self.conversation_history = self.conversation_history[-10:]

        # Step 1: Analyze sentiment - NEW TRACKING
        self._update_plan_progress("Analyze user sentiment", "in_progress")
        try:
            sentiment_signals = self.sentiment_analyzer.analyze(
                user_message, self.conversation_history[:-1]
            )
            self._update_plan_progress("Analyze user sentiment", "completed")
        except Exception as e:
            self._report_difficulty(
                f"Sentiment analysis failed: {e}", severity="medium"
            )
            self._update_plan_progress("Analyze user sentiment", "failed")
            sentiment_signals = []  # Fallback

        # Step 2: Interpret intent - NEW TRACKING
        self._update_plan_progress("Interpret user intent", "in_progress")
        intent = self._interpret_intent(user_message)

        # Report concern if intent is unclear - NEW
        if intent == "general_question":
            self._report_concern("Intent unclear, defaulting to general_question")

        self._update_plan_progress("Interpret user intent", "completed")

        # Step 3: Choose agent - NEW TRACKING
        self._update_plan_progress("Choose appropriate agent", "in_progress")
        agent = self._choose_agent(intent, sentiment_signals)
        self._update_plan_progress("Choose appropriate agent", "completed")

        # Step 4: Generate response - NEW TRACKING
        self._update_plan_progress("Generate response", "in_progress")
        response = self._generate_response(
            user_message, intent, agent, sentiment_signals
        )
        self._update_plan_progress("Generate response", "completed")

        # Calculate confidence
        confidence = self._calculate_confidence(intent, sentiment_signals)

        result = {
            "intent": intent,
            "sentiment_signals": sentiment_signals,
            "delegated_to": agent,
            "message_to_user": response,
            "confidence": confidence,
        }

        # NEW: Log conversation for proactive intelligence
        self.conversation_logger.log_conversation(
            user_message=user_message,
            intent=intent,
            delegated_to=agent,
            sentiment_signals=sentiment_signals,
            confidence=confidence,
        )

        # NEW: Track requests for proactive updates
        if intent in ["add_feature", "report_bug", "update_documentation"]:
            request_type = {
                "add_feature": "feature",
                "report_bug": "bug",
                "update_documentation": "documentation",
            }[intent]

            request_id = self.request_tracker.add_request(
                request_type=request_type,
                description=user_message[:100],  # Short summary
                user_message=user_message,
                delegated_to=agent,
            )
            result["request_id"] = request_id
            logger.info(f"Created request tracking: {request_id}")

        return result

    def _interpret_intent(self, message: str) -> str:
        """Interpret user intent from message."""
        message_lower = message.lower()

        # Roadmap view
        if "roadmap" in message_lower or "what's planned" in message_lower:
            return "view_roadmap"

        # Status check
        if any(kw in message_lower for kw in ["status", "progress", "how's it going"]):
            return "check_status"

        # Documentation request
        if any(
            kw in message_lower for kw in ["update docs", "update the docs", "document"]
        ):
            return "update_documentation"

        # Feature request
        if any(
            kw in message_lower
            for kw in ["implement", "add feature", "i need", "can you build"]
        ):
            return "add_feature"

        # Bug report
        if any(
            kw in message_lower for kw in ["broken", "failing", "error", "bug", "crash"]
        ):
            return "report_bug"

        # Demo request
        if any(kw in message_lower for kw in ["show me", "demo", "can i see"]):
            return "request_demo"

        # Tutorial request
        if any(
            kw in message_lower for kw in ["how do i", "tutorial", "teach me", "guide"]
        ):
            return "request_tutorial"

        # How-to question
        if any(
            kw in message_lower for kw in ["how does", "what is", "explain", "how to"]
        ):
            return "ask_how_to"

        # Feedback
        if any(
            kw in message_lower
            for kw in [
                "thank",
                "good job",
                "great work",
                "well done",
                "perfect",
                "works great",
            ]
        ):
            return "provide_feedback"

        # Default: general question
        return "general_question"

    def _choose_agent(
        self, intent: str, sentiment_signals: List[SentimentSignal]
    ) -> str:
        """Choose appropriate agent based on intent and sentiment."""
        agent_map = {
            "add_feature": "code_developer",
            "report_bug": "code_developer",
            "update_documentation": "project_manager",
            "request_demo": "assistant",
            "request_tutorial": "assistant",
            "ask_how_to": "assistant",
            "check_status": "project_manager",
            "view_roadmap": "project_manager",
            "provide_feedback": "curator",
            "general_question": "assistant",
        }

        return agent_map.get(intent, "assistant")

    def _generate_response(
        self,
        user_message: str,
        intent: str,
        agent: str,
        sentiment_signals: List[SentimentSignal],
    ) -> str:
        """Generate message for user_listener to display."""
        # Acknowledge sentiment if present
        sentiment_ack = ""
        if sentiment_signals:
            for sig in sentiment_signals:
                if sig.sentiment == "frustration":
                    sentiment_ack = "I understand you're frustrated. "
                elif sig.sentiment == "confusion":
                    sentiment_ack = "Let me help clarify that. "
                elif sig.sentiment == "satisfaction":
                    sentiment_ack = "I'm glad that worked! "

        # Generate delegation message
        action_map = {
            "add_feature": "implement this feature",
            "report_bug": "fix this issue",
            "update_documentation": "update the documentation",
            "request_demo": "show you how this works",
            "request_tutorial": "create a tutorial",
            "ask_how_to": "explain this",
            "check_status": "check the project status",
            "view_roadmap": "show you the roadmap",
            "provide_feedback": "record your feedback",
            "general_question": "answer your question",
        }

        action = action_map.get(intent, "help with this")

        return f"{sentiment_ack}I'll ask {agent} to {action}. I'll come back as soon as I can to summarize what's been done."

    def _calculate_confidence(
        self, intent: str, sentiment_signals: List[SentimentSignal]
    ) -> float:
        """Calculate confidence in interpretation."""
        # Base confidence
        confidence = 0.7

        # Higher confidence for clear intents
        if intent in ["add_feature", "report_bug", "check_status"]:
            confidence += 0.2

        # Sentiment signals increase confidence
        if sentiment_signals:
            avg_sentiment_conf = sum(s.confidence for s in sentiment_signals) / len(
                sentiment_signals
            )
            confidence = (confidence + avg_sentiment_conf) / 2

        return min(1.0, confidence)

    def interpret(
        self, user_message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Public interpret method (for backward compatibility).

        This delegates to execute_task() which handles ACE automatically.
        """
        return self.execute_task(user_message, context=context)

    # NEW: Proactive intelligence methods
    def get_greeting_suggestions(self) -> List[str]:
        """Get proactive suggestions for greeting.

        Returns:
            List of proactive messages to show user
        """
        return self.proactive_suggestions.get_greeting_suggestions()

    def get_contextual_suggestions(self, user_message: str) -> List[str]:
        """Get contextual suggestions for current message.

        Args:
            user_message: User's current message

        Returns:
            List of relevant suggestions
        """
        return self.proactive_suggestions.get_contextual_suggestions(user_message)

    def mark_request_completed(
        self, request_id: str, result_location: Optional[str] = None
    ):
        """Mark a tracked request as completed.

        Args:
            request_id: Request ID to mark complete
            result_location: Optional path to result
        """
        self.request_tracker.mark_completed(request_id, result_location)

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending requests.

        Returns:
            List of pending request dicts
        """
        return self.request_tracker.get_pending_requests()

    def get_conversation_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get conversation summary for recent period.

        Args:
            days: Number of days to summarize

        Returns:
            Summary statistics
        """
        return self.conversation_logger.summarize_recent_activity(days=days)
