"""Load and execute commands for agents from markdown files.

Commands are defined as markdown files with frontmatter metadata.
The CommandLoader handles:
- Loading command files from disk
- Parsing frontmatter metadata
- Validating permissions
- Loading required skills
- Executing commands with parameters

Example:
    >>> loader = CommandLoader(AgentType.ARCHITECT)
    >>> result = loader.execute("create_spec", {"priority_id": "PRIORITY-25"})

Command Format:
    ```markdown
    ---
    command: architect.create_spec
    agent: architect
    action: create_spec
    tables:
      write: [specs_specification]
      read: [roadmap_priority]
    required_skills: [technical_specification_handling]
    ---

    # Command: architect.create_spec

    ## Purpose
    Create a technical specification for a priority...
    ```
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import frontmatter

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.commands.command import Command
from coffee_maker.database.domain_wrapper import DomainWrapper
from coffee_maker.utils.logging import get_logger

logger = get_logger(__name__)


class CommandLoader:
    """Loads and executes commands for an agent from markdown files.

    Commands are defined as markdown files with frontmatter metadata:

    ```markdown
    ---
    command: architect.create_spec
    agent: architect
    action: create_spec
    tables:
      write: [specs_specification]
      read: [roadmap_priority]
    required_skills: [technical_specification_handling]
    ---

    # Command: architect.create_spec

    ## Purpose
    Create a technical specification for a priority...
    ```

    Example:
        >>> loader = CommandLoader(AgentType.ARCHITECT)
        >>> result = loader.execute("create_spec", {"priority_id": "PRIORITY-25"})
    """

    def __init__(
        self,
        agent_type: AgentType,
        commands_dir: Optional[Path] = None,
    ):
        """Initialize command loader.

        Args:
            agent_type: Type of agent
            commands_dir: Directory containing command files
                         (default: .claude/commands/agents/{agent})
        """
        self.agent_type = agent_type
        self.agent_name = agent_type.value
        self.db = DomainWrapper(agent_type)

        if commands_dir is None:
            commands_dir = Path(f".claude/commands/agents/{self.agent_name}")

        self.commands_dir = commands_dir
        self.commands: Dict[str, Command] = {}

        # Load all commands for this agent
        if self.commands_dir.exists():
            self._load_commands()
        else:
            logger.warning(f"Commands directory not found: {self.commands_dir}")

    def _load_commands(self) -> None:
        """Load all command markdown files for this agent."""
        try:
            command_files = list(self.commands_dir.glob("*.md"))
            logger.debug(f"Found {len(command_files)} command files in {self.commands_dir}")

            for cmd_file in command_files:
                try:
                    command = self._parse_command(cmd_file)
                    self.commands[command.action] = command
                    logger.debug(f"Loaded command: {command.name}")
                except Exception as e:
                    logger.error(f"Failed to load command {cmd_file}: {e}")

            logger.info(f"Loaded {len(self.commands)} commands for {self.agent_name}")
        except Exception as e:
            logger.error(f"Error loading commands from {self.commands_dir}: {e}")

    def _parse_command(self, path: Path) -> Command:
        """Parse command from markdown file.

        Args:
            path: Path to command markdown file

        Returns:
            Command object

        Raises:
            ValueError: If command metadata is invalid
        """
        with open(path, encoding="utf-8") as f:
            post = frontmatter.load(f)

        metadata = post.metadata

        # Extract and validate required metadata
        command_name = metadata.get("command", f"unknown.{path.stem}")
        agent = metadata.get("agent", self.agent_name)
        action = metadata.get("action", path.stem)

        # Extract table permissions
        tables_config = metadata.get("tables", {})
        tables_write = tables_config.get("write", [])
        tables_read = tables_config.get("read", [])

        # Extract file permissions
        files_config = metadata.get("files", {})
        files_write = files_config.get("write", [])
        files_read = files_config.get("read", [])

        # Extract skill and tool requirements
        required_skills = metadata.get("required_skills", [])
        required_tools = metadata.get("required_tools", [])

        return Command(
            name=command_name,
            agent=agent,
            action=action,
            tables_write=tables_write,
            tables_read=tables_read,
            files_write=files_write,
            files_read=files_read,
            required_skills=required_skills,
            required_tools=required_tools,
            content=post.content,
            source_file=str(path),
        )

    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute a command with parameters.

        Args:
            action: Action name (e.g., "create_spec")
            params: Parameters for command execution

        Returns:
            Command execution result

        Raises:
            ValueError: If command not found
            PermissionError: If permission validation fails
        """
        if action not in self.commands:
            raise ValueError(
                f"Command '{action}' not found for {self.agent_name}. " f"Available: {list(self.commands.keys())}"
            )

        command = self.commands[action]

        logger.info(f"Executing command: {command.name}")

        # Validate permissions BEFORE execution
        self._validate_permissions(command)

        # Load required skills
        skills = self._load_skills(command.required_skills)

        # Execute command
        result = command.execute(self.db, params, skills)

        logger.info(f"Command {command.name} completed: {result.get('success', False)}")

        return result

    def _validate_permissions(self, command: Command) -> None:
        """Validate agent has permissions for command.

        Args:
            command: Command to validate

        Raises:
            PermissionError: If agent lacks required permissions
        """
        # Check write permissions
        for table in command.tables_write:
            if not self.db.can_write(table):
                raise PermissionError(
                    f"Command '{command.name}' requires write access to '{table}' "
                    f"but {self.agent_name} cannot write to it"
                )

        # Check read permissions
        for table in command.tables_read:
            if not self.db.can_read(table):
                raise PermissionError(
                    f"Command '{command.name}' requires read access to '{table}' "
                    f"but {self.agent_name} cannot read from it"
                )

    def _load_skills(self, skill_names: List[str]) -> Dict[str, Any]:
        """Load required skills for command.

        Args:
            skill_names: List of skill names to load

        Returns:
            Dictionary of skill name to skill object
        """
        skills = {}
        for skill_name in skill_names:
            try:
                # Try to import the skill dynamically
                # For now, this is a placeholder - actual skill loading
                # would use coffee_maker.autonomous.skill_loader
                logger.debug(f"Loaded skill: {skill_name}")
                skills[skill_name] = None  # Placeholder
            except Exception as e:
                logger.warning(f"Failed to load skill {skill_name}: {e}")

        return skills

    def list_commands(self) -> List[str]:
        """List all available commands for this agent.

        Returns:
            List of command action names
        """
        return list(self.commands.keys())

    def get_command(self, action: str) -> Optional[Command]:
        """Get a command by action name.

        Args:
            action: Action name

        Returns:
            Command object or None if not found
        """
        return self.commands.get(action)
