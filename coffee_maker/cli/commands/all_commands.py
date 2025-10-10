"""Import all command handlers to trigger registration.

This module imports all command handler modules to ensure they are
registered via the @register_command decorator.

Simply import this module to load all commands:
    >>> from coffee_maker.cli.commands import all_commands
"""

# Import all command handlers to trigger @register_command decorator
from coffee_maker.cli.commands.add_priority import AddPriorityCommand
from coffee_maker.cli.commands.analyze_roadmap import AnalyzeRoadmapCommand
from coffee_maker.cli.commands.update_priority import UpdatePriorityCommand
from coffee_maker.cli.commands.user_story import UserStoryCommand
from coffee_maker.cli.commands.view_roadmap import ViewRoadmapCommand

# List of all command classes
ALL_COMMANDS = [
    AddPriorityCommand,
    UpdatePriorityCommand,
    ViewRoadmapCommand,
    AnalyzeRoadmapCommand,
    UserStoryCommand,
]

__all__ = ["ALL_COMMANDS"]
