"""Utility for reading/writing .env files."""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EnvManager:
    """Manage .env file for ACE configuration."""

    def __init__(self, env_path: Optional[Path] = None):
        """Initialize EnvManager.

        Args:
            env_path: Path to .env file (default: project root/.env)
        """
        if env_path is None:
            # Find project root
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / ".env").exists():
                    env_path = current / ".env"
                    break
                current = current.parent

        self.env_path = env_path
        logger.info(f"EnvManager using: {self.env_path}")

    def get_agent_ace_status(self, agent_name: str) -> bool:
        """Get ACE status for agent.

        Args:
            agent_name: Agent name (e.g., 'user_interpret')

        Returns:
            True if ACE enabled, False if disabled
        """
        env_var = f"ACE_ENABLED_{agent_name.upper()}"
        value = os.getenv(env_var, "true")  # Default: enabled
        return value.lower() != "false"

    def set_agent_ace_status(self, agent_name: str, enabled: bool) -> bool:
        """Set ACE status for agent.

        Args:
            agent_name: Agent name
            enabled: True to enable, False to disable

        Returns:
            True if successful
        """
        env_var = f"ACE_ENABLED_{agent_name.upper()}"
        new_value = "true" if enabled else "false"

        try:
            self._update_env_var(env_var, new_value)
            # Also update os.environ for immediate effect
            os.environ[env_var] = new_value
            logger.info(f"Set {env_var}={new_value}")
            return True
        except Exception as e:
            logger.error(f"Failed to update {env_var}: {e}")
            return False

    def _update_env_var(self, var_name: str, new_value: str):
        """Update or add environment variable in .env file."""
        if not self.env_path or not self.env_path.exists():
            raise FileNotFoundError(f".env file not found at {self.env_path}")

        # Read current content
        lines = self.env_path.read_text().split("\n")

        # Find and update variable
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"export {var_name}=") or line.strip().startswith(f"{var_name}="):
                lines[i] = f'export {var_name}="{new_value}"'
                updated = True
                break

        # Add if not found
        if not updated:
            lines.append(f'export {var_name}="{new_value}"')

        # Write back
        self.env_path.write_text("\n".join(lines))

    def get_all_agent_statuses(self) -> Dict[str, bool]:
        """Get ACE status for all known agents.

        Returns:
            Dict mapping agent name to ACE enabled status
        """
        agents = [
            "user_interpret",
            "user_listener",
            "assistant",
            "code_developer",
            "code_searcher",
            "project_manager",
        ]

        return {agent: self.get_agent_ace_status(agent) for agent in agents}
