"""
Unit tests for SkillLoader.

Tests skill loading from .claude/skills/ directory.

Author: code_developer
Date: 2025-10-19
Related: SPEC-055, US-055
"""

import pytest
from coffee_maker.autonomous.skill_loader import SkillLoader
from coffee_maker.autonomous.agent_registry import AgentType


class TestSkillLoader:
    """Test SkillLoader functionality."""

    def test_list_available_skills_empty_directory(self, tmp_path):
        """Test listing skills when directory is empty."""
        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        skills = loader.list_available_skills()
        assert skills == []

    def test_list_available_skills_with_shared_skills(self, tmp_path):
        """Test listing shared skills."""
        # Create shared skill directory
        shared_dir = tmp_path / "shared" / "test-skill"
        shared_dir.mkdir(parents=True)

        # Create SKILL.md
        skill_md = shared_dir / "SKILL.md"
        skill_md.write_text(
            """---
name: test-skill
version: 1.0.0
agent: shared
scope: shared
description: Test skill
triggers:
  - test trigger
requires: []
---

# Test Skill
"""
        )

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        skills = loader.list_available_skills()

        assert len(skills) == 1
        assert skills[0].name == "test-skill"
        assert skills[0].scope == "shared"

    def test_load_skill_by_name(self, tmp_path):
        """Test loading a specific skill by name."""
        # Create skill directory
        skill_dir = tmp_path / "shared" / "my-skill"
        skill_dir.mkdir(parents=True)

        # Create SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            """---
name: my-skill
version: 1.0.0
agent: shared
scope: shared
description: My test skill
triggers:
  - my trigger
requires: []
---

# My Skill
"""
        )

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        skill = loader.load("my-skill")

        assert skill.name == "my-skill"
        assert skill.version == "1.0.0"

    def test_load_nonexistent_skill(self, tmp_path):
        """Test loading a skill that doesn't exist."""
        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent-skill")

    def test_skill_exists(self, tmp_path):
        """Test checking if skill exists."""
        # Create skill
        skill_dir = tmp_path / "shared" / "exists-skill"
        skill_dir.mkdir(parents=True)

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            """---
name: exists-skill
version: 1.0.0
agent: shared
scope: shared
description: Test
triggers: []
requires: []
---

# Skill
"""
        )

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)

        assert loader.skill_exists("exists-skill") is True
        assert loader.skill_exists("nonexistent") is False

    def test_agent_specific_skills_precedence(self, tmp_path):
        """Test that agent-specific skills take precedence over shared."""
        # Create shared skill
        shared_dir = tmp_path / "shared" / "override-skill"
        shared_dir.mkdir(parents=True)

        shared_md = shared_dir / "SKILL.md"
        shared_md.write_text(
            """---
name: override-skill
version: 1.0.0
agent: shared
scope: shared
description: Shared version
triggers: []
requires: []
---

# Shared
"""
        )

        # Create agent-specific skill (same name)
        agent_dir = tmp_path / "code-developer" / "override-skill"
        agent_dir.mkdir(parents=True)

        agent_md = agent_dir / "SKILL.md"
        agent_md.write_text(
            """---
name: override-skill
version: 2.0.0
agent: code-developer
scope: agent-specific
description: Agent-specific version
triggers: []
requires: []
---

# Agent Specific
"""
        )

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        skill = loader.load("override-skill")

        # Agent-specific should win
        assert skill.version == "2.0.0"
        assert skill.scope == "agent-specific"
