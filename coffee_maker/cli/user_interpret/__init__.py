"""user_interpret proactive intelligence package.

This package provides context-aware, proactive features for user_interpret:
- Conversation logging
- Request tracking
- Proactive suggestions
"""

from coffee_maker.cli.user_interpret.conversation_logger import ConversationLogger
from coffee_maker.cli.user_interpret.request_tracker import RequestTracker
from coffee_maker.cli.user_interpret.proactive_suggestions import ProactiveSuggestions

__all__ = ["ConversationLogger", "RequestTracker", "ProactiveSuggestions"]
