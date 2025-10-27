"""User Listener Commands - Consolidated Architecture.

Consolidates legacy commands into 3 unified commands:
1. understand - NLU for user requests
2. route - Route requests to appropriate agents
3. conversation - Conversation state management

This module provides user interface capabilities through
consolidated command interfaces.
"""

from typing import Any, Dict, List, Optional

from .base_command import ConsolidatedCommand


class UserListenerCommands(ConsolidatedCommand):
    """User Listener commands for user interface operations.

    Commands:
        understand(action, **params) - NLU for user requests
        route(action, **params) - Request routing
        conversation(action, **params) - Conversation management
    """

    COMMANDS_INFO = {
        "understand": {
            "description": "NLU for user requests",
            "actions": ["classify_intent", "extract_entities", "determine_agent"],
        },
        "route": {
            "description": "Route requests to appropriate agents",
            "actions": ["route_request", "queue", "handle_fallback"],
        },
        "conversation": {
            "description": "Conversation state management",
            "actions": ["track", "update_context", "manage_session"],
        },
    }

    def understand(
        self,
        action: str = "classify_intent",
        user_input: Optional[str] = None,
    ) -> Any:
        """NLU for user requests.

        Actions:
            classify_intent - Classify user intent from input
            extract_entities - Extract entities from user input
            determine_agent - Determine appropriate target agent

        Args:
            action: Operation to perform
            user_input: User's input text

        Returns:
            dict: Classification, entities, or agent determination result

        Raises:
            ValueError: If action is unknown
        """
        actions = {
            "classify_intent": self._classify_intent,
            "extract_entities": self._extract_entities,
            "determine_agent": self._determine_agent,
        }

        return self._route_action(
            action,
            actions,
            user_input=user_input,
        )

    def route(
        self,
        action: str = "route_request",
        request_text: Optional[str] = None,
        target_agent: Optional[str] = None,
    ) -> Any:
        """Route requests to appropriate agents.

        Actions:
            route_request - Route user request to target agent
            queue - Queue request for processing
            handle_fallback - Handle fallback when routing fails

        Args:
            action: Operation to perform
            request_text: User request text
            target_agent: Target agent name

        Returns:
            dict: Routing result or status
            bool: Success indicator

        Raises:
            ValueError: If action is unknown
        """
        actions = {
            "route_request": self._route_request,
            "queue": self._queue_request,
            "handle_fallback": self._handle_fallback,
        }

        return self._route_action(
            action,
            actions,
            request_text=request_text,
            target_agent=target_agent,
        )

    def conversation(
        self,
        action: str = "track",
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Conversation state management.

        Actions:
            track - Track conversation history
            update_context - Update conversation context
            manage_session - Manage conversation session

        Args:
            action: Operation to perform
            session_id: Session ID (for track/manage_session)
            context: Context to update (for update_context)

        Returns:
            dict: Conversation data or status
            bool: Success indicator

        Raises:
            ValueError: If action is unknown
        """
        actions = {
            "track": self._track_conversation,
            "update_context": self._update_context,
            "manage_session": self._manage_session,
        }

        return self._route_action(
            action,
            actions,
            session_id=session_id,
            context=context,
        )

    # Private methods for understand actions

    def _classify_intent(self, user_input: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Classify user intent from input."""
        self.validate_required_params({"user_input": user_input}, ["user_input"])
        return {
            "intent": "unknown",
            "confidence": 0.5,
        }

    def _extract_entities(self, user_input: Optional[str] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """Extract entities from user input."""
        self.validate_required_params({"user_input": user_input}, ["user_input"])
        return []

    def _determine_agent(self, user_input: Optional[str] = None, **kwargs: Any) -> str:
        """Determine appropriate target agent."""
        self.validate_required_params({"user_input": user_input}, ["user_input"])
        return "assistant"

    # Private methods for route actions

    def _route_request(
        self,
        request_text: Optional[str] = None,
        target_agent: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Route user request to target agent."""
        self.validate_required_params(
            {"request_text": request_text, "target_agent": target_agent},
            ["request_text", "target_agent"],
        )
        return {
            "routed_to": target_agent,
            "status": "pending",
        }

    def _queue_request(self, request_text: Optional[str] = None, **kwargs: Any) -> int:
        """Queue request for processing."""
        self.validate_required_params({"request_text": request_text}, ["request_text"])
        return 1

    def _handle_fallback(self, request_text: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Handle fallback when routing fails."""
        self.validate_required_params({"request_text": request_text}, ["request_text"])
        return {"handled": True, "suggestion": "Try asking more specifically"}

    # Private methods for conversation actions

    def _track_conversation(self, session_id: Optional[str] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """Track conversation history."""
        self.validate_required_params({"session_id": session_id}, ["session_id"])
        return []

    def _update_context(
        self,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> bool:
        """Update conversation context."""
        self.validate_required_params(
            {"session_id": session_id, "context": context},
            ["session_id", "context"],
        )
        return True

    def _manage_session(self, session_id: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Manage conversation session."""
        self.validate_required_params({"session_id": session_id}, ["session_id"])
        return {
            "session_id": session_id,
            "status": "active",
        }
