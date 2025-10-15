"""ACE wrapper for user_interpret agent.

user_interpret is under ACE supervision to learn:
- Better intent interpretation
- More accurate sentiment detection
- Improved agent selection
"""

import os
import logging
from typing import Dict, Any, Optional

from coffee_maker.cli.user_interpret import UserInterpret
from coffee_maker.autonomous.ace.generator import ACEGenerator
from coffee_maker.autonomous.ace.config import get_default_config

logger = logging.getLogger(__name__)


class UserInterpretWithACE:
    """user_interpret wrapped with ACE observation.

    All executions of user_interpret are observed by generator,
    creating traces for reflector to analyze.
    """

    def __init__(self):
        self.user_interpret = UserInterpret()

        # Check if ACE enabled
        ace_enabled = os.getenv("ACE_ENABLED_USER_INTERPRET", "false").lower() == "true"

        if ace_enabled:
            config = get_default_config()
            self.generator = ACEGenerator(
                agent_interface=self,  # user_interpret is the "agent"
                config=config,
                agent_name="user_interpret",
                agent_objective="Interpret user intent and delegate appropriately",
                success_criteria="Correct intent interpretation, accurate sentiment, appropriate delegation",
            )
            self.ace_enabled = True
            logger.info("ACE enabled for user_interpret")
        else:
            self.generator = None
            self.ace_enabled = False
            logger.info("ACE disabled for user_interpret")

    def interpret(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Interpret with ACE observation (if enabled)."""
        if self.ace_enabled:
            # Execute through generator (creates trace and returns actual result)
            result = self.generator.execute_with_trace(
                prompt=user_message,  # Pass raw message (no prefix)
                priority_context=context or {},
                context=context,  # Pass as kwarg for send_message
            )
            # Generator returns {agent_result, result, trace_id, duration, errors}
            # Return the agent's actual interpretation result
            return result["agent_result"]
        else:
            # Direct execution (no trace)
            return self.user_interpret.interpret(user_message, context)

    def send_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Interface method for ACEGenerator.

        This is called by generator.execute_with_trace().
        The generator observes this execution and returns the result.
        """
        context = kwargs.get("context")
        return self.user_interpret.interpret(message, context)
