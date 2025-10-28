"""User Listener Workflow Command - Ultra-Consolidated."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from coffee_maker.commands.consolidated.user_listener_commands import UserListenerCommands
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class InteractResult:
    user_input: str
    response: str = ""
    intent: str = ""
    target_agent: str = ""
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UserListenerWorkflow:
    def __init__(self, db_path: Optional[str] = None):
        self.commands = UserListenerCommands(db_path)
        self.logger = logger

    def interact(self, input: str, context: Optional[dict] = None, suggested_agent: Optional[str] = None) -> str:
        datetime.now()
        try:
            intent = self.commands.understand(action="classify_intent", user_input=input)
            agent = self.commands.understand(action="determine_agent", user_input=input)
            result = self.commands.route(action="route_request", request_text=input, target_agent=agent)
            return f"Routed to {agent}: {result}"
        except Exception as e:
            return f"Error: {e}"
