"""Agent color utilities for UI display.

This module provides utilities for displaying agent messages with their
designated colors from .claude/agents/*.md frontmatter.

Usage:
    from coffee_maker.cli.agent_colors import get_agent_colors, format_agent_message

    # Get all agent colors
    colors = get_agent_colors()

    # Format a message with agent color
    message = format_agent_message("code_developer", "Implementation complete!")
    console.print(message)
"""

from pathlib import Path
from typing import Dict, Optional
import yaml


def get_agent_colors() -> Dict[str, str]:
    """Load agent colors from .claude/agents/*.md frontmatter.

    Parses the YAML frontmatter in each agent definition file to extract
    the agent name and color configuration.

    Returns:
        Dictionary mapping agent_name -> color

    Example:
        >>> colors = get_agent_colors()
        >>> colors["code_developer"]
        'cyan'
        >>> colors["project_manager"]
        'green'
    """
    colors = {}

    # Find agents directory
    project_root = Path(__file__).parent.parent.parent
    agents_dir = project_root / ".claude" / "agents"

    if not agents_dir.exists():
        return {}

    for agent_file in agents_dir.glob("*.md"):
        if agent_file.name == "README.md":
            continue

        try:
            with open(agent_file) as f:
                content = f.read()

            # Parse frontmatter (between --- markers)
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1]
                    try:
                        data = yaml.safe_load(frontmatter_text)
                        if data:
                            name = data.get("name", agent_file.stem)
                            color = data.get("color", "white")
                            colors[name] = color
                    except yaml.YAMLError:
                        # Invalid YAML, skip
                        pass
        except Exception:
            # Skip files that can't be parsed
            pass

    return colors


def format_agent_message(agent_name: str, message: str, bold: bool = True) -> str:
    """Format message with agent color for Rich console.

    Args:
        agent_name: Name of agent (e.g., "code_developer", "project_manager")
        message: Message to display
        bold: Whether to make agent name bold (default: True)

    Returns:
        Rich-formatted string with color markup

    Example:
        >>> format_agent_message("code_developer", "Task complete!")
        '[cyan][bold]code_developer:[/bold][/cyan] Task complete!'

        >>> format_agent_message("project_manager", "Status updated", bold=False)
        '[green]project_manager:[/green] Status updated'
    """
    colors = get_agent_colors()
    color = colors.get(agent_name, "white")

    if bold:
        return f"[{color}][bold]{agent_name}:[/bold][/{color}] {message}"
    else:
        return f"[{color}]{agent_name}:[/{color}] {message}"


def get_agent_color(agent_name: str, default: str = "white") -> str:
    """Get the color for a specific agent.

    Args:
        agent_name: Name of agent
        default: Default color if agent not found (default: "white")

    Returns:
        Color string (e.g., "cyan", "green", "purple")

    Example:
        >>> get_agent_color("code_developer")
        'cyan'
        >>> get_agent_color("unknown_agent", default="gray")
        'gray'
    """
    colors = get_agent_colors()
    return colors.get(agent_name, default)


def list_all_agents() -> Dict[str, Dict[str, str]]:
    """List all available agents with their metadata.

    Returns:
        Dictionary mapping agent_name -> {color, description, model}

    Example:
        >>> agents = list_all_agents()
        >>> agents["code_developer"]
        {'color': 'cyan', 'description': 'Autonomous implementation...', 'model': 'sonnet'}
    """
    agents = {}

    # Find agents directory
    project_root = Path(__file__).parent.parent.parent
    agents_dir = project_root / ".claude" / "agents"

    if not agents_dir.exists():
        return {}

    for agent_file in agents_dir.glob("*.md"):
        if agent_file.name == "README.md":
            continue

        try:
            with open(agent_file) as f:
                content = f.read()

            # Parse frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1]
                    try:
                        data = yaml.safe_load(frontmatter_text)
                        if data:
                            name = data.get("name", agent_file.stem)
                            agents[name] = {
                                "color": data.get("color", "white"),
                                "description": data.get("description", ""),
                                "model": data.get("model", ""),
                            }
                    except yaml.YAMLError:
                        pass
        except Exception:
            pass

    return agents


# Cache agent colors (only load once per process)
_AGENT_COLORS_CACHE: Optional[Dict[str, str]] = None


def get_agent_colors_cached() -> Dict[str, str]:
    """Get agent colors with caching for performance.

    Returns:
        Dictionary mapping agent_name -> color (cached)
    """
    global _AGENT_COLORS_CACHE

    if _AGENT_COLORS_CACHE is None:
        _AGENT_COLORS_CACHE = get_agent_colors()

    return _AGENT_COLORS_CACHE


def clear_agent_colors_cache():
    """Clear the agent colors cache.

    Call this if agent definitions are updated at runtime.
    """
    global _AGENT_COLORS_CACHE
    _AGENT_COLORS_CACHE = None
