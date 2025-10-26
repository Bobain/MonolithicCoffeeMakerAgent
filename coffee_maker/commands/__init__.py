"""Commands module for unified agent command execution.

This module provides:
- Command: Base class for all agent commands
- CommandLoader: Loads and executes commands from markdown files
- FeatureFlags: Manage per-agent command feature flags for gradual rollout
- ParallelOperationWrapper: Run legacy and command implementations in parallel
- RollbackManager: Rollback agents to legacy mode if issues detected

Example:
    >>> from coffee_maker.commands import CommandLoader, FeatureFlags
    >>> from coffee_maker.autonomous.agent_registry import AgentType
    >>>
    >>> # Load commands
    >>> loader = CommandLoader(AgentType.ARCHITECT)
    >>> result = loader.execute("create_spec", {"priority_id": "PRIORITY-1"})
    >>>
    >>> # Manage migration with feature flags
    >>> flags = FeatureFlags()
    >>> flags.enable_phase(2)  # Enable Phase 2 agents
    >>>
    >>> # If issues arise, rollback
    >>> from coffee_maker.commands import RollbackManager
    >>> manager = RollbackManager()
    >>> manager.rollback_phase(2, "Issues detected")
"""

from coffee_maker.commands.command import Command
from coffee_maker.commands.command_loader import CommandLoader
from coffee_maker.commands.feature_flags import FeatureFlags
from coffee_maker.commands.parallel_operation import ParallelOperationWrapper
from coffee_maker.commands.rollback import RollbackManager

__all__ = [
    "Command",
    "CommandLoader",
    "FeatureFlags",
    "ParallelOperationWrapper",
    "RollbackManager",
]
