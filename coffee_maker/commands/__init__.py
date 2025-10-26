"""Commands module for unified agent command execution.

This module provides:
- Command: Base class for all agent commands
- CommandLoader: Loads and executes commands from markdown files

Example:
    >>> from coffee_maker.commands import CommandLoader
    >>> from coffee_maker.autonomous.agent_registry import AgentType
    >>> loader = CommandLoader(AgentType.ARCHITECT)
    >>> result = loader.execute("create_spec", {"priority_id": "PRIORITY-1"})
"""

from coffee_maker.commands.command import Command
from coffee_maker.commands.command_loader import CommandLoader

__all__ = ["Command", "CommandLoader"]
