"""ACE integration for user_listener agent.

This module provides ACE (Agentic Context Engineering) integration for the
user_listener agent. user_listener is an ideal candidate for ACE because:

1. Fast operations (< 10s) - enables dual execution
2. High volume (50-100/day) - sufficient data for learning
3. Immediate feedback - can measure success quickly
4. Clear success metrics - delegation accuracy, response quality

The user_listener ACE observes:
- Delegation decisions (which agent to delegate to)
- Intent recognition patterns
- Response synthesis strategies
- Failure recovery approaches

Example:
    >>> ace = UserListenerACE()
    >>> playbook_context = ace.get_playbook_context()
    >>> # Use playbook_context to inform delegation decisions
    >>> ace.observe_delegation(
    ...     user_query="Fix the bug in roadmap_cli.py",
    ...     intent="code_fix",
    ...     delegated_to="code_developer",
    ...     success=True,
    ...     duration_seconds=8.5
    ... )
"""

import logging
import os
from typing import Optional

from coffee_maker.autonomous.ace.config import get_default_config
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader

logger = logging.getLogger(__name__)


class UserListenerACE:
    """ACE wrapper for user_listener agent.

    Observes delegation decisions and learns patterns:
    - Which agent to delegate to for which requests
    - Intent recognition patterns
    - Response synthesis strategies
    - Failure recovery approaches

    Attributes:
        enabled: Whether ACE is enabled for user_listener
        config: ACE configuration
        playbook_loader: Loader for user_listener playbook

    Example:
        >>> ace = UserListenerACE(enabled=True)
        >>> if ace.enabled:
        ...     playbook = ace.get_playbook_context()
        ...     # Use playbook to inform delegation
    """

    def __init__(self, enabled: bool = None):
        """Initialize ACE for user_listener.

        Args:
            enabled: Enable ACE (defaults to ACE_ENABLED_USER_LISTENER env var)
                    If not specified, reads from environment variable.
        """
        if enabled is None:
            enabled = os.getenv("ACE_ENABLED_USER_LISTENER", "false").lower() == "true"

        self.enabled = enabled

        if not self.enabled:
            logger.info("ACE disabled for user_listener")
            return

        # Initialize ACE components
        config = get_default_config()
        config.ensure_directories()

        # Note: user_listener doesn't have a traditional agent_interface
        # We'll track delegations manually instead
        self.config = config
        self.playbook_loader = PlaybookLoader(agent_name="user_listener", config=config)

        logger.info("✅ ACE enabled for user_listener")
        logger.info(f"   Playbook: {self.playbook_loader.playbook_path}")

    def get_playbook_context(self) -> str:
        """Get current playbook as context for delegation decisions.

        Returns:
            Playbook markdown or empty string if no playbook available

        Example:
            >>> ace = UserListenerACE()
            >>> context = ace.get_playbook_context()
            >>> if context:
            ...     print("Using playbook to inform delegation")
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

    def observe_delegation(
        self,
        user_query: str,
        intent: str,
        delegated_to: str,
        success: bool,
        duration_seconds: float,
        user_feedback: Optional[str] = None,
    ):
        """Observe a delegation decision for later reflection.

        This method records delegation decisions so the reflector can later
        analyze patterns and extract insights to improve future delegations.

        Args:
            user_query: User's original query
            intent: Interpreted intent (e.g., "code_fix", "documentation", "status_query")
            delegated_to: Agent delegated to (e.g., "code_developer", "project_manager")
            success: Whether delegation solved the problem (True/False)
            duration_seconds: Time taken to complete delegation
            user_feedback: Optional user feedback on quality of response

        Example:
            >>> ace.observe_delegation(
            ...     user_query="What's the status of PRIORITY-5?",
            ...     intent="status_query",
            ...     delegated_to="project_manager",
            ...     success=True,
            ...     duration_seconds=2.3,
            ...     user_feedback="Good"
            ... )
        """
        if not self.enabled:
            return

        # TODO: Store observation for later reflection
        # For now, just log it
        logger.info(
            f"ACE Observation: '{user_query[:50]}...' "
            f"→ {delegated_to} "
            f"(intent={intent}, success={success}, duration={duration_seconds:.1f}s)"
        )

        if user_feedback:
            logger.info(f"  User feedback: {user_feedback}")

        # Future: Write observation to trace file for reflector to analyze
        # This would follow the same pattern as code_developer's ACEGenerator
        # but adapted for delegation observations rather than code changes
