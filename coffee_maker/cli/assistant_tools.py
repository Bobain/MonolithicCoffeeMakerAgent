"""Tools for LangChain-powered assistant in project-manager.

This module provides tools that the assistant can use to help answer
complex questions and perform technical analysis.

PRIORITY 2.9.5: Transparent Assistant Integration
"""

import subprocess
from pathlib import Path
from typing import List, Optional

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class ReadFileInput(BaseModel):
    """Input for ReadFileTool."""

    file_path: str = Field(description="Path to the file to read")
    start_line: Optional[int] = Field(default=None, description="Start line number (optional)")
    end_line: Optional[int] = Field(default=None, description="End line number (optional)")


class ReadFileTool(BaseTool):
    """Tool to read file contents."""

    name = "read_file"
    description = "Read contents of a file. Use this to examine source code, documentation, or configuration files."
    args_schema = ReadFileInput

    def _run(self, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        """Read file contents."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File {file_path} does not exist"

            with open(path, "r") as f:
                lines = f.readlines()

            if start_line is not None and end_line is not None:
                lines = lines[start_line - 1 : end_line]
            elif start_line is not None:
                lines = lines[start_line - 1 :]

            return "".join(lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"


class SearchCodeInput(BaseModel):
    """Input for SearchCodeTool."""

    pattern: str = Field(description="Pattern to search for (regex supported)")
    file_pattern: Optional[str] = Field(default="*.py", description="File pattern to search in (e.g., *.py, *.md)")
    directory: Optional[str] = Field(default=".", description="Directory to search in")


class SearchCodeTool(BaseTool):
    """Tool to search code using grep."""

    name = "search_code"
    description = "Search for patterns in code files. Use this to find function definitions, class names, or specific code patterns."
    args_schema = SearchCodeInput

    def _run(self, pattern: str, file_pattern: str = "*.py", directory: str = ".") -> str:
        """Search code using grep."""
        try:
            cmd = ["grep", "-r", "-n", "--include", file_pattern, pattern, directory]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout if result.stdout else "No matches found"
            elif result.returncode == 1:
                return "No matches found"
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Search timed out"
        except Exception as e:
            return f"Error: {str(e)}"


class ListFilesInput(BaseModel):
    """Input for ListFilesTool."""

    pattern: str = Field(description="File pattern to match (e.g., **/*.py, *.md)")
    directory: Optional[str] = Field(default=".", description="Directory to search in")


class ListFilesTool(BaseTool):
    """Tool to list files matching a pattern."""

    name = "list_files"
    description = "List files matching a pattern. Use this to discover files in the codebase."
    args_schema = ListFilesInput

    def _run(self, pattern: str, directory: str = ".") -> str:
        """List files using glob."""
        try:
            path = Path(directory)
            files = list(path.glob(pattern))

            if not files:
                return "No files found matching pattern"

            return "\n".join(str(f) for f in sorted(files)[:100])  # Limit to 100 files
        except Exception as e:
            return f"Error: {str(e)}"


class GitLogInput(BaseModel):
    """Input for GitLogTool."""

    max_commits: Optional[int] = Field(default=10, description="Maximum number of commits to show")
    file_path: Optional[str] = Field(default=None, description="Show commits for specific file (optional)")


class GitLogTool(BaseTool):
    """Tool to view git commit history."""

    name = "git_log"
    description = (
        "View recent git commit history. Use this to understand recent changes or find when something was modified."
    )
    args_schema = GitLogInput

    def _run(self, max_commits: int = 10, file_path: Optional[str] = None) -> str:
        """Get git log."""
        try:
            cmd = ["git", "log", f"-{max_commits}", "--oneline"]
            if file_path:
                cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout if result.stdout else "No commits found"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


class GitDiffInput(BaseModel):
    """Input for GitDiffTool."""

    file_path: Optional[str] = Field(default=None, description="Show diff for specific file (optional)")
    commit: Optional[str] = Field(default=None, description="Compare with specific commit (optional)")


class GitDiffTool(BaseTool):
    """Tool to view git differences."""

    name = "git_diff"
    description = "View git differences. Use this to see what changed in files or between commits."
    args_schema = GitDiffInput

    def _run(self, file_path: Optional[str] = None, commit: Optional[str] = None) -> str:
        """Get git diff."""
        try:
            cmd = ["git", "diff"]
            if commit:
                cmd.append(commit)
            if file_path:
                cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout if result.stdout else "No differences found"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


class ExecuteBashInput(BaseModel):
    """Input for ExecuteBashTool."""

    command: str = Field(description="Bash command to execute")


class ExecuteBashTool(BaseTool):
    """Tool to execute bash commands (read-only operations)."""

    name = "execute_bash"
    description = (
        "Execute bash commands for read-only operations like ls, cat, ps, etc. "
        "DO NOT use for write operations. Use this to check system state or process info."
    )
    args_schema = ExecuteBashInput

    def _run(self, command: str) -> str:
        """Execute bash command."""
        # Safety check - only allow read-only commands
        dangerous_commands = ["rm", "mv", "cp", "dd", ">", ">>", "chmod", "chown"]
        if any(cmd in command.lower() for cmd in dangerous_commands):
            return "Error: Write operations not allowed"

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=Path.cwd())

            output = result.stdout if result.stdout else result.stderr
            return output if output else "Command executed successfully (no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"


def get_assistant_tools() -> List[BaseTool]:
    """Get all tools available to the assistant.

    Returns:
        List of LangChain tools
    """
    return [
        ReadFileTool(),
        SearchCodeTool(),
        ListFilesTool(),
        GitLogTool(),
        GitDiffTool(),
        ExecuteBashTool(),
    ]
