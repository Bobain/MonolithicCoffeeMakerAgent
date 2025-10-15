"""Global registry for singleton agents.

This module provides a registry to ensure only one instance of each agent exists
and remains running throughout the application lifecycle. This improves trace
correlation and maintains consistent state across all agent operations.

Philosophy:
- Each agent should be a singleton (only one instance exists)
- Agents should be initialized once and remain running
- All calls to an agent should use the same instance
- This ensures consistent state and better trace correlation

CRITICAL: Thread-safe implementation prevents race conditions.
For code_developer, this ensures ONLY ONE instance can exist at a time.

Usage:
    from coffee_maker.autonomous.ace.agent_registry import AgentRegistry
    from coffee_maker.cli.user_interpret import UserInterpret

    # Get singleton instance (creates if doesn't exist)
    agent = AgentRegistry.get_agent(UserInterpret)

    # Subsequent calls return the same instance
    same_agent = AgentRegistry.get_agent(UserInterpret)
    assert agent is same_agent  # True
"""

import logging
import threading
from typing import Any, Dict, Type

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for singleton agents with thread-safe locking.

    This class maintains a global registry of agent instances, ensuring
    only one instance of each agent class exists at any time.

    The registry is thread-safe using a two-level locking strategy:
    1. Global lock for managing per-agent locks
    2. Agent-specific locks for creating instances

    CRITICAL: For code_developer, this prevents multiple instances from
    being created simultaneously (race condition protection).
    """

    _instances: Dict[str, Any] = {}
    _locks: Dict[str, threading.Lock] = {}
    _global_lock = threading.Lock()

    @classmethod
    def get_agent(cls, agent_class: Type, *args, **kwargs) -> Any:
        """Get or create singleton agent instance (thread-safe).

        This method returns the existing singleton instance if one exists,
        or creates a new instance if this is the first request for this agent class.

        CRITICAL: Uses two-level locking to prevent race conditions.
        For code_developer, this ensures ONLY ONE instance can be created.

        Args:
            agent_class: The agent class to instantiate
            *args: Positional arguments to pass to agent constructor (only used on first creation)
            **kwargs: Keyword arguments to pass to agent constructor (only used on first creation)

        Returns:
            Singleton instance of the agent class

        Example:
            >>> agent1 = AgentRegistry.get_agent(UserInterpret)
            >>> agent2 = AgentRegistry.get_agent(UserInterpret)
            >>> assert agent1 is agent2  # Same instance
        """
        agent_name = agent_class.__name__

        # Get or create lock for this agent class
        with cls._global_lock:
            if agent_name not in cls._locks:
                cls._locks[agent_name] = threading.Lock()

        # Acquire agent-specific lock
        with cls._locks[agent_name]:
            if agent_name not in cls._instances:
                logger.info(f"🔐 Creating singleton instance of {agent_name} (thread-safe)")
                cls._instances[agent_name] = agent_class(*args, **kwargs)
            else:
                logger.debug(f"🔐 Returning existing instance of {agent_name} (thread-safe)")

        return cls._instances[agent_name]

    @classmethod
    def has_agent(cls, agent_class: Type) -> bool:
        """Check if agent instance already exists.

        Args:
            agent_class: The agent class to check

        Returns:
            True if singleton instance exists, False otherwise

        Example:
            >>> AgentRegistry.has_agent(UserInterpret)
            False
            >>> agent = AgentRegistry.get_agent(UserInterpret)
            >>> AgentRegistry.has_agent(UserInterpret)
            True
        """
        agent_name = agent_class.__name__
        return agent_name in cls._instances

    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered agents (primarily for testing).

        This removes all singleton instances from the registry. Use with caution
        in production code as it will force re-initialization of all agents.

        This also clears the ACEAgent._instance singleton to ensure a fresh start.

        CRITICAL: Thread-safe clearing to prevent race conditions.

        Example:
            >>> agent = AgentRegistry.get_agent(UserInterpret)
            >>> AgentRegistry.clear_registry()
            >>> AgentRegistry.has_agent(UserInterpret)
            False
        """
        with cls._global_lock:
            logger.info(f"Clearing agent registry ({len(cls._instances)} agents)")

            # Also clear ACEAgent singletons (for agents using ACEAgent base class)
            for agent_class_name, agent_instance in cls._instances.items():
                # Clear the _instance class variable if it exists
                agent_class = type(agent_instance)
                if hasattr(agent_class, "_instance"):
                    delattr(agent_class, "_instance")
                    logger.debug(f"Cleared singleton instance for {agent_class_name}")

            cls._instances.clear()
            cls._locks.clear()

    @classmethod
    def get_all_agents(cls) -> Dict[str, Any]:
        """Get all registered agent instances.

        Returns:
            Dictionary mapping agent class names to instances

        Example:
            >>> agent1 = AgentRegistry.get_agent(UserInterpret)
            >>> agent2 = AgentRegistry.get_agent(CodeDeveloper)
            >>> all_agents = AgentRegistry.get_all_agents()
            >>> assert len(all_agents) == 2
        """
        return cls._instances.copy()
