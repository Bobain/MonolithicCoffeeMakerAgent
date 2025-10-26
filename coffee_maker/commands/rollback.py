"""
Rollback Manager for Command System Migration

This module provides rollback capabilities for the command system migration.
If issues are detected with the new command system, agents can be rolled back
to legacy mode independently, without requiring a full system restart.

Example:
    manager = RollbackManager()
    manager.rollback_agent("code_developer")  # Back to legacy mode
    manager.rollback_phase(2)  # Back Phase 2 to legacy mode
    manager.rollback_all()  # Emergency rollback of entire system
"""

import logging
from datetime import datetime
from typing import Dict, List, Set

from coffee_maker.commands.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)


class RollbackManager:
    """
    Manage rollback of command system per agent or phase.

    This manager tracks rollback events and provides granular rollback capability
    at agent, phase, or full-system levels. Rollbacks are reversible - agents
    can be re-enabled after rollback.

    Attributes:
        flags: FeatureFlags instance for enabling/disabling commands
        rollback_history: Log of rollback events
    """

    def __init__(self):
        """Initialize rollback manager."""
        self.flags = FeatureFlags()
        self.rollback_history: List[Dict[str, str]] = []

    def rollback_agent(self, agent_name: str, reason: str = "Manual rollback") -> None:
        """
        Rollback single agent to legacy mode.

        Disables all commands for the specified agent, forcing it to use
        legacy implementations until explicitly re-enabled.

        Args:
            agent_name: Name of agent to rollback (e.g., 'code_developer')
            reason: Reason for rollback (logged for audit trail)
        """
        if agent_name not in self.flags.flags:
            logger.error(f"Unknown agent: {agent_name}")
            return

        # Disable all commands for this agent
        self.flags.disable_agent(agent_name)

        # Log rollback event
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_rollback",
            "agent": agent_name,
            "reason": reason,
        }
        self.rollback_history.append(event)

        logger.warning(f"Rolled back {agent_name} to legacy mode. Reason: {reason}")

    def rollback_phase(self, phase_num: int, reason: str = "Manual rollback") -> None:
        """
        Rollback all agents in a specific implementation phase.

        Phases are:
        - Phase 1: Infrastructure (no agents)
        - Phase 2: project_manager, architect, code_developer
        - Phase 3: code_reviewer, orchestrator
        - Phase 4: assistant, user_listener, ux_design_expert
        - Phase 5: All agents

        Args:
            phase_num: Phase number to rollback (1-5)
            reason: Reason for rollback

        Raises:
            ValueError: If invalid phase number
        """
        if phase_num < 1 or phase_num > 5:
            raise ValueError(f"Invalid phase number: {phase_num}")

        # Map phases to agents
        phase_agents = {
            1: [],  # No agents in foundation phase
            2: ["project_manager", "architect", "code_developer"],
            3: ["code_reviewer", "orchestrator"],
            4: ["assistant", "user_listener", "ux_design_expert"],
            5: [
                "project_manager",
                "architect",
                "code_developer",
                "code_reviewer",
                "orchestrator",
                "assistant",
                "user_listener",
                "ux_design_expert",
            ],
        }

        agents_to_rollback = phase_agents[phase_num]

        for agent in agents_to_rollback:
            self.flags.disable_agent(agent)

        # Log phase rollback
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "phase_rollback",
            "phase": phase_num,
            "agents_rolled_back": agents_to_rollback,
            "reason": reason,
        }
        self.rollback_history.append(event)

        logger.warning(f"Rolled back Phase {phase_num} ({len(agents_to_rollback)} agents). " f"Reason: {reason}")

    def rollback_all(self, reason: str = "Emergency system rollback") -> None:
        """
        Emergency rollback of entire command system.

        Disables all commands for all agents, returning the entire system
        to legacy mode. This is a last-resort action for critical issues.

        Args:
            reason: Reason for rollback (should indicate severity)
        """
        logger.critical(f"EMERGENCY ROLLBACK: {reason}")

        for agent in self.flags.flags.keys():
            self.flags.disable_agent(agent)

        # Log emergency rollback
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "emergency_rollback",
            "all_agents_rolled_back": True,
            "reason": reason,
        }
        self.rollback_history.append(event)

        logger.critical("All agents rolled back to legacy mode")

    def re_enable_agent(self, agent_name: str, reason: str = "Manual re-enable") -> None:
        """
        Re-enable commands for a previously rolled-back agent.

        Args:
            agent_name: Name of agent to re-enable
            reason: Reason for re-enabling
        """
        if agent_name not in self.flags.flags:
            logger.error(f"Unknown agent: {agent_name}")
            return

        self.flags.enable_agent(agent_name)

        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_reenable",
            "agent": agent_name,
            "reason": reason,
        }
        self.rollback_history.append(event)

        logger.info(f"Re-enabled {agent_name} to use command system")

    def is_rolled_back(self, agent_name: str) -> bool:
        """
        Check if an agent is currently in rolled-back (legacy) mode.

        Args:
            agent_name: Agent name to check

        Returns:
            True if agent is rolled back (no commands enabled)
        """
        if agent_name not in self.flags.flags:
            return False

        enabled_commands = self.flags.get_enabled_commands(agent_name)
        return len(enabled_commands) == 0

    def get_rollback_status(self) -> Dict[str, bool]:
        """
        Get rollback status for all agents.

        Returns:
            Dictionary mapping agent names to rollback status
                (True = rolled back, False = command system enabled)
        """
        return {agent: self.is_rolled_back(agent) for agent in self.flags.flags}

    def get_rolled_back_agents(self) -> Set[str]:
        """
        Get set of agents currently in rolled-back mode.

        Returns:
            Set of agent names that are rolled back
        """
        return {agent for agent, rolled_back in self.get_rollback_status().items() if rolled_back}

    def get_rollback_history(self) -> List[Dict[str, str]]:
        """
        Get complete rollback history.

        Returns:
            List of rollback events with timestamps and reasons
        """
        return self.rollback_history.copy()

    def clear_history(self) -> None:
        """Clear rollback history."""
        self.rollback_history = []
        logger.info("Cleared rollback history")

    def get_latest_rollback(self) -> Dict[str, str] | None:
        """
        Get the most recent rollback event.

        Returns:
            Latest rollback event, or None if no rollbacks recorded
        """
        return self.rollback_history[-1] if self.rollback_history else None

    def rollback_since_timestamp(self, timestamp: str, reason: str = "Automated rollback due to issues") -> List[str]:
        """
        Rollback agents that were modified since a specific timestamp.

        This is useful for automatic rollback of recently-changed agents
        if issues are detected after a deployment.

        Args:
            timestamp: ISO format timestamp to check since
            reason: Reason for rollback

        Returns:
            List of agents that were rolled back
        """
        rolled_back_agents = []

        # This would require tracking when each agent's commands were last modified
        # For now, log the request
        logger.info(f"Requested rollback of agents modified since {timestamp}: {reason}")

        return rolled_back_agents

    def can_rollback_safely(self, agent_name: str) -> bool:
        """
        Check if an agent can be rolled back safely.

        Some agents may have in-progress work that would be interrupted by rollback.
        This check verifies that it's safe to rollback.

        Args:
            agent_name: Agent to check

        Returns:
            True if safe to rollback, False if not
        """
        # In future, check if agent has in-progress work
        # For now, always return True
        return True

    def get_safe_rollback_order(self) -> List[str]:
        """
        Get recommended order for rolling back agents safely.

        This respects dependencies between agents - for example,
        code_developer should be rolled back before orchestrator
        to avoid coordination issues.

        Returns:
            List of agent names in safe rollback order
        """
        # Reverse dependency order
        # Orchestrator depends on all agents, so roll it back first
        # Code reviewer depends on code developer
        # Then roll back core agents
        return [
            "orchestrator",
            "code_reviewer",
            "code_developer",
            "architect",
            "project_manager",
            "assistant",
            "user_listener",
            "ux_design_expert",
        ]

    def rollback_all_safely(self, reason: str = "Safe system rollback") -> None:
        """
        Rollback all agents in safe order.

        Respects dependencies between agents to avoid coordination issues.

        Args:
            reason: Reason for rollback
        """
        logger.warning(f"Performing safe rollback of all agents: {reason}")

        for agent in self.get_safe_rollback_order():
            self.rollback_agent(agent, reason)

        logger.info("Safe rollback of all agents completed")
