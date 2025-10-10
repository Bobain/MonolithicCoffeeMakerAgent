"""Command handlers for project manager CLI.

This package provides command handlers for slash commands and natural
language processing in the interactive chat interface.

Available commands:
- /add - Add new priority
- /update - Update existing priority
- /view - View roadmap
- /analyze - Analyze roadmap health
- /suggest - Get AI recommendations
- /implement - Start daemon implementation
- /status - Check daemon status
- /help - Show help

Example:
    >>> from coffee_maker.cli.commands import get_command_handler
    >>>
    >>> handler = get_command_handler("add")
    >>> response = handler.execute(["User Authentication"], editor)
"""

from coffee_maker.cli.commands.base import BaseCommand

# Command registry will be populated as commands are implemented
COMMAND_REGISTRY = {}


def register_command(command_class):
    """Register a command handler.

    Decorator to register command handlers in the global registry.

    Args:
        command_class: Command class to register

    Returns:
        The command class (unchanged)

    Example:
        >>> @register_command
        ... class MyCommand(BaseCommand):
        ...     ...
    """
    instance = command_class()
    COMMAND_REGISTRY[instance.name] = instance
    return command_class


def get_command_handler(command_name: str) -> BaseCommand:
    """Get command handler by name.

    Args:
        command_name: Command name (without /)

    Returns:
        Command handler instance or None

    Example:
        >>> handler = get_command_handler("add")
        >>> if handler:
        ...     response = handler.execute(args, editor)
    """
    return COMMAND_REGISTRY.get(command_name)


def list_commands():
    """List all registered commands.

    Returns:
        Dictionary of command names to handlers

    Example:
        >>> commands = list_commands()
        >>> for name, handler in commands.items():
        ...     print(f"{name}: {handler.description}")
    """
    return COMMAND_REGISTRY.copy()


__all__ = [
    "BaseCommand",
    "register_command",
    "get_command_handler",
    "list_commands",
    "COMMAND_REGISTRY",
]
