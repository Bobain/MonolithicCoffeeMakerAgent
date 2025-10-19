"""
Skill Loader for Claude Skills Integration.

Loads skills from .claude/skills/ directory with YAML frontmatter parsing.
Supports both shared skills (all agents) and agent-specific skills.

Author: architect agent
Date: 2025-10-19
Related: SPEC-055, US-055
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

from coffee_maker.autonomous.agent_registry import AgentType

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """Metadata for a Claude Skill."""

    name: str
    version: str
    agent: str
    scope: str  # "shared" or "agent-specific"
    description: str
    triggers: List[str]  # Task descriptions that trigger this skill
    requires: List[str]  # Dependencies (Python packages)
    skill_path: Path

    @classmethod
    def from_skill_md(cls, skill_path: Path) -> "SkillMetadata":
        """Parse SKILL.md file for metadata.

        Args:
            skill_path: Path to skill directory

        Returns:
            SkillMetadata instance

        Raises:
            FileNotFoundError: If SKILL.md not found
            ValueError: If SKILL.md has invalid format
        """
        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found: {skill_md}")

        content = skill_md.read_text()

        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])

                    return cls(
                        name=metadata.get("name", skill_path.name),
                        version=metadata.get("version", "1.0.0"),
                        agent=metadata.get("agent", "shared"),
                        scope=metadata.get("scope", "shared"),
                        description=metadata.get("description", ""),
                        triggers=metadata.get("triggers", []),
                        requires=metadata.get("requires", []),
                        skill_path=skill_path,
                    )
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid YAML in SKILL.md: {skill_md}\nError: {e}")

        raise ValueError(f"Invalid SKILL.md format (missing YAML frontmatter): {skill_md}")


class SkillLoader:
    """Load Claude Skills from .claude/skills/ directory.

    Example:
        >>> loader = SkillLoader(agent_type=AgentType.CODE_DEVELOPER)
        >>> skills = loader.list_available_skills()
        >>> skill = loader.load("test-driven-implementation")
    """

    def __init__(self, agent_type: AgentType, skills_dir: Optional[Path] = None):
        """Initialize SkillLoader.

        Args:
            agent_type: Type of agent loading skills
            skills_dir: Custom skills directory (default: .claude/skills)
        """
        self.agent_type = agent_type
        self.skills_dir = skills_dir or Path(".claude/skills")
        self.shared_skills_dir = self.skills_dir / "shared"

        # Convert agent type to directory name (e.g., CODE_DEVELOPER → code-developer)
        agent_dir_name = agent_type.value.replace("_", "-")
        self.agent_skills_dir = self.skills_dir / agent_dir_name

    def list_available_skills(self) -> List[SkillMetadata]:
        """List all skills available to this agent (shared + agent-specific).

        Returns:
            List of SkillMetadata for available skills
        """
        skills = []

        # 1. Load shared skills
        if self.shared_skills_dir.exists():
            for skill_path in self.shared_skills_dir.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    try:
                        skills.append(SkillMetadata.from_skill_md(skill_path))
                    except (FileNotFoundError, ValueError) as e:
                        logger.warning(f"Failed to load shared skill {skill_path.name}: {e}")

        # 2. Load agent-specific skills
        if self.agent_skills_dir.exists():
            for skill_path in self.agent_skills_dir.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    try:
                        skills.append(SkillMetadata.from_skill_md(skill_path))
                    except (FileNotFoundError, ValueError) as e:
                        logger.warning(f"Failed to load agent skill {skill_path.name}: {e}")

        return skills

    def load(self, skill_name: str) -> SkillMetadata:
        """Load a specific skill by name.

        Agent-specific skills take precedence over shared skills.

        Args:
            skill_name: Name of skill to load

        Returns:
            SkillMetadata for the skill

        Raises:
            FileNotFoundError: If skill not found
        """
        # Try agent-specific first
        agent_skill_path = self.agent_skills_dir / skill_name
        if agent_skill_path.exists():
            return SkillMetadata.from_skill_md(agent_skill_path)

        # Fall back to shared
        shared_skill_path = self.shared_skills_dir / skill_name
        if shared_skill_path.exists():
            return SkillMetadata.from_skill_md(shared_skill_path)

        raise FileNotFoundError(
            f"Skill '{skill_name}' not found for agent {self.agent_type.value}\n"
            f"Searched:\n"
            f"  - {agent_skill_path}\n"
            f"  - {shared_skill_path}"
        )

    def skill_exists(self, skill_name: str) -> bool:
        """Check if skill exists for this agent.

        Args:
            skill_name: Name of skill to check

        Returns:
            True if skill exists, False otherwise
        """
        try:
            self.load(skill_name)
            return True
        except FileNotFoundError:
            return False
