"""Base class for consolidated commands with action-based routing pattern.

This module provides the foundation for the consolidated command architecture,
enabling consistent parameter validation, error handling, and action routing
across all agent commands.

The ConsolidatedCommand class enforces:
- Action parameter validation
- Consistent error handling
- Type checking for parameters
- Logging and observability
- Graceful fallback behavior
"""

import logging
from abc import ABC
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ConsolidatedCommand(ABC):
    """Base class for consolidated commands with action-based routing.

    Each consolidated command groups related operations under a single
    interface, using an action parameter to specify which operation to
    perform. This reduces cognitive load and improves maintainability.

    Example:
        class ProjectManagerCommands(ConsolidatedCommand):
            def roadmap(self, action="list", **params):
                actions = {
                    "list": self._list_all_priorities,
                    "details": self._get_priority_details,
                    "update": self._update_priority_metadata,
                    "status": self._check_priority_status
                }
                return self._route_action(action, actions, **params)
    """

    # Subclasses should set this to document their commands
    COMMANDS_INFO: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the consolidated command handler.

        Args:
            db_path: Optional path to the SQLite database. If None,
                    defaults to data/roadmap.db
        """
        if db_path is None:
            db_path = "data/roadmap.db"

        self.db_path = db_path
        self.logger = logger

    def _route_action(
        self,
        action: str,
        actions: Dict[str, Callable],
        **params: Any,
    ) -> Any:
        """Route action to the appropriate handler method.

        This method handles all the validation and error handling common
        to action-based command routing:
        1. Validates action is known
        2. Validates parameters are present
        3. Calls the appropriate handler
        4. Logs the operation
        5. Handles errors gracefully

        Args:
            action: The action name (e.g., "list", "details", "create")
            actions: Dictionary mapping action names to handler methods
            **params: Keyword arguments to pass to the handler

        Returns:
            The result from the action handler

        Raises:
            ValueError: If action is not recognized
            TypeError: If required parameters are missing
            Exception: Any exception from the action handler (re-raised)

        Example:
            actions = {
                "list": self._list_all,
                "details": self._get_details,
            }
            return self._route_action(action, actions, **params)
        """
        # Validate action
        if action not in actions:
            available_actions = ", ".join(sorted(actions.keys()))
            raise ValueError(f"Unknown action: '{action}'. " f"Available actions: {available_actions}")

        # Get the handler method
        handler = actions[action]

        # Log the operation
        self.logger.debug(f"Routing action: {action} with params: {list(params.keys())}")

        try:
            # Call the handler
            result = handler(**params)
            self.logger.debug(f"Action '{action}' completed successfully")
            return result
        except TypeError as e:
            # Parameter validation error
            self.logger.error(f"Invalid parameters for action '{action}': {e}")
            raise TypeError(f"Action '{action}' failed due to missing or invalid " f"parameters: {e}") from e
        except Exception as e:
            # Other errors
            self.logger.error(f"Action '{action}' failed with error: {e}", exc_info=True)
            raise

    def validate_required_params(self, params: Dict[str, Any], required: list[str]) -> None:
        """Validate that all required parameters are present.

        Args:
            params: Dictionary of parameters to check
            required: List of required parameter names

        Raises:
            TypeError: If any required parameter is missing

        Example:
            self.validate_required_params(
                {"priority_id": "PRIORITY-28"},
                ["priority_id"]
            )
        """
        missing = [p for p in required if p not in params or params[p] is None]
        if missing:
            raise TypeError(f"Missing required parameters: {', '.join(missing)}")

    def validate_param_type(self, param_name: str, param_value: Any, expected_type: type) -> None:
        """Validate that a parameter has the expected type.

        Args:
            param_name: Name of the parameter (for error messages)
            param_value: The actual parameter value
            expected_type: The expected type (e.g., str, int, dict)

        Raises:
            TypeError: If parameter is not the expected type

        Example:
            self.validate_param_type("priority_id", "PRIORITY-28", str)
            self.validate_param_type("metadata", {"key": "value"}, dict)
        """
        if not isinstance(param_value, expected_type):
            raise TypeError(
                f"Parameter '{param_name}' must be {expected_type.__name__}, " f"got {type(param_value).__name__}"
            )

    def validate_one_of(self, param_name: str, param_value: Any, allowed_values: list[str]) -> None:
        """Validate that a parameter is one of allowed values.

        Args:
            param_name: Name of the parameter (for error messages)
            param_value: The actual parameter value
            allowed_values: List of allowed values

        Raises:
            ValueError: If parameter is not one of the allowed values

        Example:
            self.validate_one_of("status", "blocked", ["blocked", "in-progress"])
        """
        if param_value not in allowed_values:
            raise ValueError(f"Parameter '{param_name}' must be one of " f"{allowed_values}, got '{param_value}'")

    def deprecated_command(self, old_name: str, new_command: str, new_action: str) -> Callable:
        """Create a deprecation wrapper for a legacy command.

        This creates a wrapper function that:
        1. Issues a DeprecationWarning
        2. Calls the new consolidated command
        3. Logs the deprecated usage

        Args:
            old_name: Name of the old command (for error message)
            new_command: Name of the new consolidated command
            new_action: Name of the action in the new command

        Returns:
            A wrapper function that redirects to the new command

        Example:
            check_priority_status = self.deprecated_command(
                "check_priority_status",
                "roadmap",
                "status"
            )
        """
        import warnings

        def wrapper(**params):
            warnings.warn(
                f"'{old_name}' is deprecated, use '{new_command}(action='{new_action}') " f"instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            self.logger.warning(f"Deprecated command called: {old_name} -> " f"{new_command}(action='{new_action}')")
            new_method = getattr(self, new_command)
            return new_method(action=new_action, **params)

        return wrapper

    def get_command_info(self, command_name: str) -> Dict[str, Any]:
        """Get information about a command.

        Args:
            command_name: Name of the command

        Returns:
            Dictionary with command metadata (actions, descriptions, etc.)

        Example:
            info = pm.get_command_info("roadmap")
            print(info["description"])
        """
        return self.COMMANDS_INFO.get(command_name, {})

    def list_commands(self) -> Dict[str, Dict[str, Any]]:
        """List all available commands and their actions.

        Returns:
            Dictionary of all commands with their metadata

        Example:
            commands = pm.list_commands()
            for cmd_name, cmd_info in commands.items():
                print(f"{cmd_name}: {cmd_info['actions']}")
        """
        return self.COMMANDS_INFO.copy()
