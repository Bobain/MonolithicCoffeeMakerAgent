"""ACE integration for assistant agent.

This module provides ACE (Agentic Context Engineering) integration for the
assistant agent. assistant is a good candidate for ACE because:

1. Fast operations (10-30s) - dual execution feasible
2. Good volume (20-50/day) - sufficient data
3. Quick feedback - response quality measurable
4. Clear metrics - answer completeness, delegation accuracy

The assistant ACE observes:
- Documentation search strategies
- When to delegate vs answer directly
- Example provision quality
- Answer completeness and accuracy

Example:
    >>> ace = AssistantACE()
    >>> playbook_context = ace.get_playbook_context()
    >>> # Use playbook_context to inform response strategy
"""

import logging
import os

from coffee_maker.autonomous.ace.config import get_default_config
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader

logger = logging.getLogger(__name__)


class AssistantACE:
    """ACE wrapper for assistant agent.

    Learns patterns:
    - Documentation search strategies
    - When to delegate vs answer directly
    - Example provision quality
    - Answer completeness

    Attributes:
        enabled: Whether ACE is enabled for assistant
        config: ACE configuration
        playbook_loader: Loader for assistant playbook

    Example:
        >>> ace = AssistantACE(enabled=True)
        >>> if ace.enabled:
        ...     playbook = ace.get_playbook_context()
        ...     # Use playbook to inform response
    """

    def __init__(self, enabled: bool = None):
        """Initialize ACE for assistant.

        Args:
            enabled: Enable ACE (defaults to ACE_ENABLED_ASSISTANT env var)
                    If not specified, reads from environment variable.
        """
        if enabled is None:
            enabled = os.getenv("ACE_ENABLED_ASSISTANT", "false").lower() == "true"

        self.enabled = enabled

        if not self.enabled:
            logger.info("ACE disabled for assistant")
            return

        config = get_default_config()
        config.ensure_directories()

        self.config = config
        self.playbook_loader = PlaybookLoader(agent_name="assistant", config=config)

        logger.info("✅ ACE enabled for assistant")
        logger.info(f"   Playbook: {self.playbook_loader.playbook_path}")

    def get_playbook_context(self) -> str:
        """Get current playbook as context for responses.

        Returns:
            Playbook markdown or empty string if no playbook available

        Example:
            >>> ace = AssistantACE()
            >>> context = ace.get_playbook_context()
            >>> if context:
            ...     print("Using playbook to inform response")
        """
        if not self.enabled:
            return ""

        try:
            playbook = self.playbook_loader.load()
            return self.playbook_loader.to_markdown(playbook)
        except FileNotFoundError:
            logger.debug("No playbook found yet")
            return ""
        except Exception as e:
            logger.warning(f"Failed to load playbook: {e}")
            return ""
