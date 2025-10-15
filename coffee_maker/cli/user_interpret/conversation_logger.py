"""Conversation logging for user_interpret agent."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ConversationLogger:
    """Log and retrieve conversation history for user_interpret.

    This logger maintains:
    - Complete conversation history in JSONL format
    - Conversation summaries for quick analysis
    - Intent patterns for learning user behavior

    Example:
        logger = ConversationLogger()
        entry = logger.log_conversation(
            user_message="add a login feature",
            intent="add_feature",
            delegated_to="code_developer",
            sentiment_signals=[],
            confidence=0.9
        )
        recent = logger.get_recent_conversations(limit=10)
    """

    def __init__(self, docs_dir: str = "docs/user_interpret"):
        """Initialize conversation logger.

        Args:
            docs_dir: Directory for storing conversation data
        """
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.docs_dir / "conversation_history.jsonl"
        self.summaries_file = self.docs_dir / "conversation_summaries.json"

    def log_conversation(
        self,
        user_message: str,
        intent: str,
        delegated_to: str,
        sentiment_signals: List[Any],
        confidence: float,
    ) -> Dict[str, Any]:
        """Log conversation entry.

        Args:
            user_message: User's input message
            intent: Interpreted intent
            delegated_to: Agent to handle request
            sentiment_signals: List of SentimentSignal objects
            confidence: Confidence score for interpretation

        Returns:
            Conversation entry with timestamp and ID
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "intent": intent,
            "delegated_to": delegated_to,
            "sentiment_signals": [
                {
                    "sentiment": s.sentiment,
                    "confidence": s.confidence,
                    "severity": s.severity,
                }
                for s in sentiment_signals
            ],
            "confidence": confidence,
            "conversation_id": self._generate_id(),
        }

        # Append to JSONL file
        with open(self.history_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        logger.debug(f"Logged conversation: {entry['conversation_id']}")
        return entry

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations.

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversation entries, most recent last
        """
        if not self.history_file.exists():
            return []

        conversations = []
        with open(self.history_file, "r") as f:
            for line in f:
                if line.strip():
                    conversations.append(json.loads(line.strip()))

        return conversations[-limit:]

    def get_conversations_by_intent(
        self, intent: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get conversations matching specific intent.

        Args:
            intent: Intent to filter by
            limit: Maximum number to return

        Returns:
            List of matching conversations
        """
        recent = self.get_recent_conversations(limit=100)
        matching = [c for c in recent if c["intent"] == intent]
        return matching[-limit:]

    def summarize_recent_activity(self, days: int = 7) -> Dict[str, Any]:
        """Generate summary of recent activity.

        Args:
            days: Number of days to look back

        Returns:
            Summary statistics
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        recent = self.get_recent_conversations(limit=1000)

        # Filter by date
        relevant = [
            c for c in recent if datetime.fromisoformat(c["timestamp"]) > cutoff
        ]

        # Summarize
        summary = {
            "total_conversations": len(relevant),
            "intents": {},
            "agents_used": {},
            "avg_confidence": 0.0,
            "period_days": days,
        }

        if not relevant:
            return summary

        total_confidence = 0.0
        for conv in relevant:
            # Count intents
            intent = conv["intent"]
            summary["intents"][intent] = summary["intents"].get(intent, 0) + 1

            # Count agents
            agent = conv["delegated_to"]
            summary["agents_used"][agent] = summary["agents_used"].get(agent, 0) + 1

            # Sum confidence
            total_confidence += conv["confidence"]

        summary["avg_confidence"] = total_confidence / len(relevant)

        return summary

    def _generate_id(self) -> str:
        """Generate unique conversation ID.

        Returns:
            Unique ID based on timestamp
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
