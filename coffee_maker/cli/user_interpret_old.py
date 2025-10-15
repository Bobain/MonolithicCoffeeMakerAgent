"""user_interpret agent - Intent interpretation and delegation routing.

This agent is the "brain" between user_listener and the team.
It analyzes sentiment, interprets intent, and chooses the right agent.

IMPORTANT: This agent is under ACE supervision!
"""

import logging
from typing import Dict, Any, Optional, List
from coffee_maker.cli.sentiment_analyzer import SentimentAnalyzer, SentimentSignal

logger = logging.getLogger(__name__)


class UserInterpret:
    """Interpret user intent and delegate to appropriate agents.

    This agent handles:
    1. Sentiment analysis
    2. Intent interpretation
    3. Agent selection
    4. Response synthesis

    This agent is wrapped by ACEGenerator for observation and learning.
    """

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversation_history: List[str] = []

        logger.info("UserInterpret initialized")

    def interpret(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Interpret user message and decide delegation.

        Args:
            user_message: Raw user input
            context: Optional context (recent messages, user history, etc.)

        Returns:
            Interpretation result with delegation decision
        """
        # Track conversation
        self.conversation_history.append(user_message)
        self.conversation_history = self.conversation_history[-10:]

        # Analyze sentiment
        sentiment_signals = self.sentiment_analyzer.analyze(user_message, self.conversation_history[:-1])

        # Interpret intent
        intent = self._interpret_intent(user_message)

        # Choose agent
        agent = self._choose_agent(intent, sentiment_signals)

        # Generate response
        response = self._generate_response(user_message, intent, agent, sentiment_signals)

        return {
            "intent": intent,
            "sentiment_signals": sentiment_signals,
            "delegated_to": agent,
            "message_to_user": response,
            "confidence": self._calculate_confidence(intent, sentiment_signals),
        }

    def _interpret_intent(self, message: str) -> str:
        """Interpret user intent from message.

        Returns intent type (add_feature, report_bug, ask_how_to, etc.)
        """
        message_lower = message.lower()

        # Roadmap view (check before demo to avoid "show me" collision)
        if "roadmap" in message_lower or "what's planned" in message_lower:
            return "view_roadmap"

        # Status check
        if any(kw in message_lower for kw in ["status", "progress", "how's it going"]):
            return "check_status"

        # Documentation request (check before general patterns)
        if any(kw in message_lower for kw in ["update docs", "update the docs", "document"]):
            return "update_documentation"

        # Feature request
        if any(kw in message_lower for kw in ["implement", "add feature", "i need", "can you build"]):
            return "add_feature"

        # Bug report
        if any(kw in message_lower for kw in ["broken", "failing", "error", "bug", "crash"]):
            return "report_bug"

        # Demo request
        if any(kw in message_lower for kw in ["show me", "demo", "can i see"]):
            return "request_demo"

        # Tutorial request
        if any(kw in message_lower for kw in ["how do i", "tutorial", "teach me", "guide"]):
            return "request_tutorial"

        # How-to question
        if any(kw in message_lower for kw in ["how does", "what is", "explain", "how to"]):
            return "ask_how_to"

        # Feedback (check satisfaction signals)
        if any(
            kw in message_lower for kw in ["thank", "good job", "great work", "well done", "perfect", "works great"]
        ):
            return "provide_feedback"

        # Default: general question
        return "general_question"

    def _choose_agent(self, intent: str, sentiment_signals: List[SentimentSignal]) -> str:
        """Choose appropriate agent based on intent and sentiment."""
        # Intent-based routing
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

    def _calculate_confidence(self, intent: str, sentiment_signals: List[SentimentSignal]) -> float:
        """Calculate confidence in interpretation."""
        # Base confidence
        confidence = 0.7

        # Higher confidence for clear intents
        if intent in ["add_feature", "report_bug", "check_status"]:
            confidence += 0.2

        # Sentiment signals increase confidence
        if sentiment_signals:
            avg_sentiment_conf = sum(s.confidence for s in sentiment_signals) / len(sentiment_signals)
            confidence = (confidence + avg_sentiment_conf) / 2

        return min(1.0, confidence)
