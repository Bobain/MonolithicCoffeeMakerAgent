"""Subprocess wrapper for Claude CLI.

This module provides a simple interface to execute Claude CLI commands
as subprocesses, enabling the daemon to invoke Claude Code programmatically.

Example:
    >>> from coffee_maker.autonomous.claude_cli_interface import ClaudeCLI
    >>>
    >>> cli = ClaudeCLI()
    >>> result = cli.execute_prompt(
    ...     "Read docs/ROADMAP.md and implement PRIORITY 2"
    ... )
    >>> print(result.stdout)
"""

import logging
import subprocess
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CLIResult:
    """Result from Claude CLI execution.

    Attributes:
        returncode: Process exit code (0 = success)
        stdout: Standard output
        stderr: Standard error
        success: Whether execution succeeded
    """

    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.returncode == 0


class ClaudeCLI:
    """Wrapper for Claude CLI subprocess execution.

    This class provides methods to execute Claude CLI commands programmatically,
    enabling the daemon to invoke Claude Code for autonomous development.

    Attributes:
        cli_path: Path to claude command (defaults to 'claude')
        timeout: Default timeout in seconds

    Example:
        >>> cli = ClaudeCLI()
        >>> result = cli.execute_prompt("Implement feature X")
        >>> if result.success:
        ...     print("Feature implemented!")
    """

    def __init__(self, cli_path: str = "claude", timeout: int = 3600):
        """Initialize Claude CLI interface.

        Args:
            cli_path: Path to claude command (default: 'claude')
            timeout: Default timeout in seconds (default: 3600 = 1 hour)
        """
        self.cli_path = cli_path
        self.timeout = timeout
        logger.info(f"ClaudeCLI initialized with path: {cli_path}")

    def execute_prompt(
        self,
        prompt: str,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> CLIResult:
        """Execute a prompt using Claude CLI.

        Args:
            prompt: The prompt to send to Claude
            working_dir: Working directory for execution
            timeout: Timeout in seconds (None = use default)

        Returns:
            CLIResult with stdout, stderr, and return code

        Example:
            >>> cli = ClaudeCLI()
            >>> result = cli.execute_prompt(
            ...     "Read docs/ROADMAP.md and implement PRIORITY 2"
            ... )
            >>> if result.success:
            ...     print("Implementation complete")
        """
        timeout = timeout or self.timeout

        # Build command: echo "prompt" | claude
        # Claude CLI reads from stdin when not in interactive mode
        cmd = [self.cli_path]

        logger.info(f"Executing Claude CLI: {prompt[:100]}...")

        try:
            result = subprocess.run(
                cmd,
                input=prompt,  # Pass prompt via stdin
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            logger.info(f"Claude CLI completed with code {result.returncode}")

            return CLIResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Claude CLI timed out after {timeout}s")
            return CLIResult(
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
            )

        except Exception as e:
            logger.error(f"Claude CLI execution failed: {e}")
            return CLIResult(
                returncode=-1,
                stdout="",
                stderr=str(e),
            )

    def execute_command(
        self,
        args: List[str],
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> CLIResult:
        """Execute arbitrary Claude CLI command.

        Args:
            args: Command arguments (e.g., ['code', '--help'])
            working_dir: Working directory
            timeout: Timeout in seconds

        Returns:
            CLIResult with stdout, stderr, and return code

        Example:
            >>> cli = ClaudeCLI()
            >>> result = cli.execute_command(['--version'])
            >>> print(result.stdout)
        """
        timeout = timeout or self.timeout

        cmd = [self.cli_path] + args

        logger.info(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return CLIResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s")
            return CLIResult(
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
            )

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return CLIResult(
                returncode=-1,
                stdout="",
                stderr=str(e),
            )

    def check_available(self) -> bool:
        """Check if Claude CLI is available.

        Returns:
            True if Claude CLI is installed and accessible

        Example:
            >>> cli = ClaudeCLI()
            >>> if cli.check_available():
            ...     print("Claude CLI is ready!")
        """
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            available = result.returncode == 0
            if available:
                logger.info(f"Claude CLI available: {result.stdout.strip()}")
            else:
                logger.warning("Claude CLI not available")
            return available

        except Exception as e:
            logger.error(f"Failed to check Claude CLI: {e}")
            return False
