"""Skill Loader - Load and execute Claude Code Skills.

Skills are reusable prompt templates stored in .claude/skills/ directory.
They help agents perform specialized tasks consistently and effectively.

Architecture:
    - Skills stored as markdown files in .claude/skills/
    - Variable substitution using $VARIABLE_NAME format
    - Loaded on-demand by agents (architect, code_developer, etc.)

Related:
    - .claude/skills/architecture-reuse-check.md
    - .claude/skills/proactive-refactoring-analysis.md
"""

import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SkillNames:
    """Enum-like class for skill names (prevents typos)."""

    # Universal skills (ALL agents)
    TRACE_EXECUTION = "trace-execution"  # ACE generator skill - used by ALL agents
    CONTEXT_BUDGET_OPTIMIZER = "context-budget-optimizer"  # Phase 0 skill - used by ALL agents

    # Architect skills
    ARCHITECTURE_REUSE_CHECK = "architecture-reuse-check"
    PROACTIVE_REFACTORING_ANALYSIS = "proactive-refactoring-analysis"
    ARCHITECT_STARTUP = "architect-startup"  # CFR-007 solution

    # code_developer skills
    TEST_FAILURE_ANALYSIS = "test-failure-analysis"
    DOD_VERIFICATION = "dod-verification"
    GIT_WORKFLOW_AUTOMATION = "git-workflow-automation"
    CODE_DEVELOPER_STARTUP = "code-developer-startup"  # CFR-007 solution

    # project_manager skills
    ROADMAP_HEALTH_CHECK = "roadmap-health-check"
    PR_MONITORING_ANALYSIS = "pr-monitoring-analysis"
    PROJECT_MANAGER_STARTUP = "project-manager-startup"  # CFR-007 solution


def load_skill(skill_name: str, variables: Optional[Dict[str, str]] = None) -> str:
    """Load a skill template and substitute variables.

    Args:
        skill_name: Name of skill file (without .md extension)
        variables: Dictionary of variable substitutions {VAR_NAME: value}

    Returns:
        Skill content with variables substituted

    Raises:
        FileNotFoundError: If skill file doesn't exist
        ValueError: If skill_name is empty

    Example:
        >>> skill = load_skill(SkillNames.ARCHITECTURE_REUSE_CHECK, {
        ...     "PRIORITY_NAME": "PRIORITY 10",
        ...     "PROBLEM_DESCRIPTION": "Commit review system"
        ... })
        >>> # skill now contains the template with variables replaced
    """
    if not skill_name:
        raise ValueError("skill_name cannot be empty")

    # Skill file location
    skill_file = Path(f".claude/skills/{skill_name}.md")

    if not skill_file.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_file}")

    # Read skill content
    logger.info(f"📚 Loading skill: {skill_name}")
    skill_content = skill_file.read_text(encoding="utf-8")

    # Substitute variables
    if variables:
        for var_name, var_value in variables.items():
            placeholder = f"${var_name}"
            skill_content = skill_content.replace(placeholder, str(var_value))

        logger.info(f"✅ Skill loaded with {len(variables)} variable(s) substituted")
    else:
        logger.info(f"✅ Skill loaded (no variables)")

    return skill_content


def get_available_skills() -> list[str]:
    """Get list of available skill names.

    Returns:
        List of skill names (without .md extension)

    Example:
        >>> skills = get_available_skills()
        >>> print(skills)
        ['architecture-reuse-check', 'proactive-refactoring-analysis']
    """
    skills_dir = Path(".claude/skills")

    if not skills_dir.exists():
        logger.warning(f"Skills directory not found: {skills_dir}")
        return []

    skill_files = list(skills_dir.glob("*.md"))
    skill_names = [f.stem for f in skill_files]

    logger.info(f"Found {len(skill_names)} available skills")
    return sorted(skill_names)
