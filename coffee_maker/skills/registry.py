"""Skill Registry for Dynamic Skill Loading.

Provides Pythonic skill loading using proper imports instead of importlib.util.

This replaces the non-Pythonic approach of loading skills dynamically from file paths.

Usage:
    from coffee_maker.skills import get_skill

    # Load a skill
    task_separator = get_skill("architect.task_separator")
    result = task_separator.main({"priority_ids": [1, 2, 3]})

    # Or use the class directly
    skill_class = get_skill("architect.task_separator", as_class=True)
    instance = skill_class(repo_root=Path("/path/to/repo"))
    result = instance.execute(priority_ids=[1, 2, 3])

Author: code_developer (implementing PRIORITY 26)
Date: 2025-10-23
"""

import importlib
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Central registry for skill loading and management."""

    # Skill name to module path mapping
    SKILL_MAP: Dict[str, str] = {
        # Architect skills
        "architect.task_separator": "claude.skills.architect.task_separator.task_separator",
        "architect.architecture_analysis": "claude.skills.architect.architecture_analysis.architecture_analysis",
        "architect.architecture_reuse_check": "claude.skills.architect.architecture_reuse_check.architecture_reuse_check",
        "architect.code_review_history": "claude.skills.architect.code_review_history.code_review_history",
        "architect.dependency_conflict_resolver": "claude.skills.architect.dependency_conflict_resolver.dependency_conflict_resolver",
        "architect.dependency_impact": "claude.skills.architect.dependency_impact.dependency_impact",
        "architect.merge_worktree_branches": "claude.skills.architect.merge_worktree_branches.merge_worktree_branches",
        "architect.proactive_refactoring_analysis": "claude.skills.architect.proactive_refactoring_analysis.proactive_refactoring_analysis",
        # Shared skills
        "shared.bug_tracking": "claude.skills.shared.bug_tracking.bug_tracking",
        "shared.cfr_management": "claude.skills.shared.cfr_management.cfr_management",
        "shared.code_navigation": "claude.skills.shared.code_navigation.code_navigation",
        "shared.code_review_management": "claude.skills.shared.code_review_management.code_review_management",
        "shared.orchestrator_agent_management": "claude.skills.shared.orchestrator_agent_management.agent_management",
        "shared.orchestrator_health_monitor": "claude.skills.shared.orchestrator_health_monitor.orchestrator_health_monitor",
        "shared.roadmap_auto_management": "claude.skills.shared.roadmap_auto_management.roadmap_auto_management",
        "shared.roadmap_management": "claude.skills.shared.roadmap_management.roadmap_management",
        "shared.technical_specification_handling": "claude.skills.shared.technical_specification_handling.technical_specification_handling",
        # Project manager skills
        "project_manager.pr_monitoring": "claude.skills.project_manager.pr_monitoring.pr_monitoring",
        "project_manager.roadmap_health": "claude.skills.project_manager.roadmap_health.roadmap_health",
        # Assistant skills
        "assistant.bug_analyzer": "claude.skills.assistant.bug_analyzer.bug_analyzer",
        "assistant.demo_creator": "claude.skills.assistant.demo_creator.demo_creator",
    }

    @classmethod
    def _add_skills_to_path(cls, repo_root: Optional[Path] = None) -> None:
        """Add .claude/skills to Python path if not already present.

        This allows importing skills as: from claude.skills.architect.task_separator import ...

        Args:
            repo_root: Repository root path. If None, uses cwd.
        """
        if repo_root is None:
            repo_root = Path.cwd()

        skills_parent = repo_root / ".claude"
        skills_parent_str = str(skills_parent)

        if skills_parent_str not in sys.path:
            sys.path.insert(0, skills_parent_str)
            logger.debug(f"Added {skills_parent_str} to sys.path")

    @classmethod
    def get_skill(
        cls,
        skill_name: str,
        repo_root: Optional[Path] = None,
        as_class: bool = False,
    ) -> Any:
        """Load a skill by name.

        Args:
            skill_name: Skill name in format "category.skill_name" (e.g., "architect.task_separator")
            repo_root: Repository root path. If None, uses cwd.
            as_class: If True, return the skill class. If False, return the module.

        Returns:
            The skill module or class

        Raises:
            ValueError: If skill_name is not found in registry
            ImportError: If skill module cannot be imported

        Example:
            # Get module with main() function
            skill = get_skill("architect.task_separator")
            result = skill.main({"priority_ids": [1, 2, 3]})

            # Get class and instantiate
            SkillClass = get_skill("architect.task_separator", as_class=True)
            instance = SkillClass(repo_root=Path("/path"))
            result = instance.execute(priority_ids=[1, 2, 3])
        """
        if skill_name not in cls.SKILL_MAP:
            available = ", ".join(sorted(cls.SKILL_MAP.keys()))
            raise ValueError(f"Unknown skill: {skill_name}. Available skills: {available}")

        module_path = cls.SKILL_MAP[skill_name]

        # Ensure skills directory is in Python path
        cls._add_skills_to_path(repo_root)

        try:
            # Import the module using standard Python imports
            module = importlib.import_module(module_path)
            logger.debug(f"Successfully imported skill: {skill_name} from {module_path}")

            if as_class:
                # Return the skill class (assumes class name follows convention)
                # e.g., task_separator.TaskSeparatorSkill
                skill_class_name = _get_class_name_from_skill_name(skill_name)
                if hasattr(module, skill_class_name):
                    return getattr(module, skill_class_name)
                else:
                    # Fallback: find first class in module
                    for name in dir(module):
                        obj = getattr(module, name)
                        if isinstance(obj, type) and name.endswith("Skill"):
                            return obj
                    raise AttributeError(
                        f"No skill class found in {module_path}. " f"Expected class name: {skill_class_name}"
                    )

            return module

        except ImportError as e:
            logger.error(f"Failed to import skill {skill_name}: {e}", exc_info=True)
            raise ImportError(f"Failed to import skill {skill_name} from {module_path}: {e}") from e

    @classmethod
    def list_skills(cls) -> Dict[str, str]:
        """List all registered skills.

        Returns:
            Dictionary mapping skill names to module paths
        """
        return cls.SKILL_MAP.copy()


def _get_class_name_from_skill_name(skill_name: str) -> str:
    """Convert skill name to expected class name.

    Args:
        skill_name: e.g., "architect.task_separator"

    Returns:
        Expected class name, e.g., "TaskSeparatorSkill"
    """
    # Extract the skill part (after the dot)
    parts = skill_name.split(".")
    skill_part = parts[-1]

    # Convert snake_case to PascalCase
    words = skill_part.split("_")
    class_name = "".join(word.capitalize() for word in words) + "Skill"
    return class_name


# Convenience function
def get_skill(
    skill_name: str,
    repo_root: Optional[Path] = None,
    as_class: bool = False,
) -> Any:
    """Convenience function to load a skill.

    See SkillRegistry.get_skill() for details.
    """
    return SkillRegistry.get_skill(skill_name, repo_root, as_class)
