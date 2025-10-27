"""User Listener Workflow Command - Ultra-Consolidated."""

from typing import Optional
from coffee_maker.commands.consolidated.user_listener_commands import UserListenerCommands
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class UserListenerWorkflow:
    """Ultra-consolidated workflow command for user interaction."""

    def __init__(self, db_path: Optional[str] = None):
        self.commands = UserListenerCommands(db_path)
        self.logger = logger

    def interact(self, input: str, context: Optional[dict] = None, suggested_agent: Optional[str] = None) -> str:
        """Execute full user interaction workflow.

        Args:
            input: User's input text (required)
            context: Conversation context (optional)
            suggested_agent: Hint for routing (optional)

        Returns:
            Response to display to user
        """
        # TODO: Implement full workflow logic
        # 1. Understand input
        intent = self.commands.understand(action="classify_intent", user_input=input)
        # 2. Determine agent
        agent = self.commands.understand(action="determine_agent", user_input=input)
        # 3. Route request
        result = self.commands.route(action="route_request", request_text=input, target_agent=agent)
        return f"Routed to {agent}: {result}"
