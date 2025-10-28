"""Base class for all agent commands.

A Command represents a single action that an agent can perform.
Commands are typically loaded from markdown files and executed with parameters.

Architecture:
    - Command metadata (name, action, agent)
    - Permission requirements (tables, files, skills)
    - Skill dependencies
    - Execution logic

Example:
    >>> cmd = Command(
    ...     name="architect.create_spec",
    ...     agent="architect",
    ...     action="create_spec",
    ...     tables_write=["specs_specification"],
    ...     tables_read=["roadmap_priority"],
    ...     required_skills=["technical_specification_handling"]
    ... )
    >>> result = cmd.execute(db, {"priority_id": "PRIORITY-1"})
"""

from typing import Any, Dict, List, Optional

from coffee_maker.database.domain_wrapper import DomainWrapper
from coffee_maker.utils.logging import get_logger

logger = get_logger(__name__)


class Command:
    """Individual command implementation.

    Encapsulates:
    - Command metadata (name, agent, action)
    - Permission requirements (tables, files)
    - Skill dependencies
    - Execution logic

    Commands are typically loaded from markdown files by CommandLoader.
    """

    def __init__(
        self,
        name: str,
        agent: str,
        action: str,
        tables_write: Optional[List[str]] = None,
        tables_read: Optional[List[str]] = None,
        files_write: Optional[List[str]] = None,
        files_read: Optional[List[str]] = None,
        required_skills: Optional[List[str]] = None,
        required_tools: Optional[List[str]] = None,
        content: str = "",
        source_file: str = "",
    ):
        """Initialize command.

        Args:
            name: Full command name (e.g., "architect.create_spec")
            agent: Agent that owns this command
            action: Action name (e.g., "create_spec")
            tables_write: Tables this command writes to
            tables_read: Tables this command reads from
            files_write: Files this command writes
            files_read: Files this command reads
            required_skills: Skills required for execution
            required_tools: Tools required (git, gh, pytest, etc.)
            content: Markdown content from command file
            source_file: Path to source markdown file
        """
        self.name = name
        self.agent = agent
        self.action = action
        self.tables_write = tables_write or []
        self.tables_read = tables_read or []
        self.files_write = files_write or []
        self.files_read = files_read or []
        self.required_skills = required_skills or []
        self.required_tools = required_tools or []
        self.content = content
        self.source_file = source_file

    def execute(
        self,
        db: DomainWrapper,
        params: Dict[str, Any],
        skills: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the command.

        This is a base implementation. Specific commands can override
        this method or use declarative execution from markdown.

        Args:
            db: Domain wrapper for database access
            params: Command parameters
            skills: Loaded skills dictionary

        Returns:
            Result dictionary with 'success' key and command-specific data

        Example:
            >>> result = cmd.execute(db, {"priority_id": "PRIORITY-1"})
            >>> if result["success"]:
            ...     print(f"Created spec: {result['spec_id']}")
        """
        logger.info(f"Executing command: {self.name} with params: {params}")

        # Command-specific logic would go here
        # For now, this is a placeholder that will be enhanced
        # when individual commands are implemented

        return {
            "success": True,
            "command": self.name,
            "params": params,
        }

    def __repr__(self) -> str:
        """Return string representation of command."""
        return f"Command({self.name}, agent={self.agent}, action={self.action})"

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.name} ({self.agent})"
