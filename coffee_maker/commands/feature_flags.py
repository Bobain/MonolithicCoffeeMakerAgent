"""
Feature Flag System for Gradual Command Rollout

This module provides a feature flag system for managing gradual rollout of the
command system across agents. Each agent can have commands enabled/disabled
independently, allowing for safe, incremental migration from legacy to command-based
architecture.

Example:
    flags = FeatureFlags()
    if flags.is_enabled("code_developer", "claim_priority"):
        # Use new command-based implementation
    else:
        # Fall back to legacy implementation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class FeatureFlags:
    """
    Per-agent feature flags for gradual command system rollout.

    This system allows independent enabling/disabling of commands for each agent,
    supporting phased migration from legacy to command-based architecture without
    risk of breaking existing workflows.

    Attributes:
        config_path: Path to the feature flags configuration file
        flags: In-memory cache of feature flag state
    """

    def __init__(self, config_path: str = ".claude/command_flags.json"):
        """
        Initialize feature flags system.

        Args:
            config_path: Path to feature flags JSON configuration file.
                If file doesn't exist, creates with all flags disabled (safe default).
        """
        self.config_path = Path(config_path)
        self.flags: Dict[str, Dict[str, bool]] = {}
        self._load_flags()

    def _load_flags(self) -> None:
        """Load feature flags from configuration file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                    self.flags = config.get("agent_flags", {})
                logger.info(f"Loaded feature flags from {self.config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse feature flags JSON: {e}")
                self.flags = self._get_default_flags()
        else:
            # Create default (all disabled) configuration
            self.flags = self._get_default_flags()
            self._save_flags()
            logger.info(f"Created default feature flags at {self.config_path}")

    @staticmethod
    def _get_default_flags() -> Dict[str, Dict[str, bool]]:
        """
        Get default feature flag configuration (all disabled - safe default).

        Returns:
            Dictionary with all agents and their command flags set to False.
        """
        return {
            "project_manager": {},
            "architect": {},
            "code_developer": {},
            "code_reviewer": {},
            "orchestrator": {},
            "assistant": {},
            "user_listener": {},
            "ux_design_expert": {},
        }

    def _save_flags(self) -> None:
        """Save current feature flags to configuration file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(
                {
                    "agent_flags": self.flags,
                    "last_updated": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )
        logger.info(f"Saved feature flags to {self.config_path}")

    def is_enabled(self, agent: str, command: str) -> bool:
        """
        Check if a command is enabled for an agent.

        Args:
            agent: Agent name (e.g., 'code_developer', 'architect')
            command: Command name (e.g., 'claim_priority', 'create_spec')

        Returns:
            True if command is enabled for agent, False otherwise
        """
        if agent not in self.flags:
            logger.warning(f"Unknown agent: {agent}")
            return False
        return self.flags.get(agent, {}).get(command, False)

    def enable_command(self, agent: str, command: str) -> None:
        """
        Enable a command for an agent.

        Args:
            agent: Agent name
            command: Command name
        """
        if agent not in self.flags:
            self.flags[agent] = {}
        self.flags[agent][command] = True
        self._save_flags()
        logger.info(f"Enabled {command} for {agent}")

    def disable_command(self, agent: str, command: str) -> None:
        """
        Disable a command for an agent.

        Args:
            agent: Agent name
            command: Command name
        """
        if agent not in self.flags:
            self.flags[agent] = {}
        self.flags[agent][command] = False
        self._save_flags()
        logger.info(f"Disabled {command} for {agent}")

    def enable_agent(self, agent: str) -> None:
        """
        Enable all commands for an agent.

        Args:
            agent: Agent name
        """
        if agent not in self.flags:
            self.flags[agent] = {}
        # Find all commands for this agent and enable them
        for command in self.flags[agent]:
            self.flags[agent][command] = True
        self._save_flags()
        logger.info(f"Enabled all commands for {agent}")

    def disable_agent(self, agent: str) -> None:
        """
        Disable all commands for an agent (rollback to legacy mode).

        Args:
            agent: Agent name
        """
        if agent not in self.flags:
            self.flags[agent] = {}
        # Disable all commands for this agent
        for command in self.flags[agent]:
            self.flags[agent][command] = False
        self._save_flags()
        logger.warning(f"Disabled all commands for {agent} (rolled back to legacy)")

    def get_agent_status(self, agent: str) -> Dict[str, bool]:
        """
        Get all command flags for an agent.

        Args:
            agent: Agent name

        Returns:
            Dictionary mapping command names to enabled/disabled status
        """
        return self.flags.get(agent, {})

    def get_all_flags(self) -> Dict[str, Dict[str, bool]]:
        """
        Get all feature flags.

        Returns:
            Complete feature flag dictionary
        """
        return self.flags.copy()

    def register_command(self, agent: str, command: str, enabled: bool = False) -> None:
        """
        Register a new command in feature flags.

        Args:
            agent: Agent name
            command: Command name
            enabled: Whether command should be initially enabled
        """
        if agent not in self.flags:
            self.flags[agent] = {}
        self.flags[agent][command] = enabled
        self._save_flags()
        logger.info(f"Registered {command} for {agent} (enabled={enabled})")

    def enable_phase(self, phase_num: int) -> None:
        """
        Enable all commands for a specific implementation phase.

        This is a convenience method for enabling multiple agents at once
        during phased rollout (e.g., Phase 2 includes project_manager, architect, code_developer).

        Args:
            phase_num: Phase number (1-5)

        Raises:
            ValueError: If invalid phase number
        """
        if phase_num == 1:
            # Foundation - no agents, just infrastructure
            pass
        elif phase_num == 2:
            # Core agents: project_manager, architect, code_developer
            for agent in ["project_manager", "architect", "code_developer"]:
                self.enable_agent(agent)
        elif phase_num == 3:
            # Support agents: code_reviewer, orchestrator
            for agent in ["code_reviewer", "orchestrator"]:
                self.enable_agent(agent)
        elif phase_num == 4:
            # UI agents: assistant, user_listener, ux_design_expert
            for agent in ["assistant", "user_listener", "ux_design_expert"]:
                self.enable_agent(agent)
        elif phase_num == 5:
            # All agents enabled
            for agent in self.flags:
                self.enable_agent(agent)
        else:
            raise ValueError(f"Invalid phase number: {phase_num} (must be 1-5)")

        logger.info(f"Enabled Phase {phase_num}")

    def get_enabled_agents(self) -> Set[str]:
        """
        Get set of agents that have at least one command enabled.

        Returns:
            Set of agent names with enabled commands
        """
        return {agent for agent, commands in self.flags.items() if any(commands.values())}

    def get_enabled_commands(self, agent: str) -> Set[str]:
        """
        Get set of enabled commands for an agent.

        Args:
            agent: Agent name

        Returns:
            Set of enabled command names
        """
        return {command for command, enabled in self.flags.get(agent, {}).items() if enabled}
