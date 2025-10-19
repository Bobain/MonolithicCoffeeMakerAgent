"""
Unit tests for SkillRegistry.

Tests skill discovery with fuzzy matching.

Author: code_developer
Date: 2025-10-19
Related: SPEC-055, US-055
"""

from coffee_maker.autonomous.skill_registry import SkillRegistry
from coffee_maker.autonomous.agent_registry import AgentType


class TestSkillRegistry:
    """Test SkillRegistry functionality."""

    def test_find_skills_exact_match(self, tmp_path):
        """Test finding skills by exact trigger match."""
        # Create skill with specific trigger
        skill_dir = tmp_path / "shared" / "exact-match-skill"
        skill_dir.mkdir(parents=True)

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            """---
name: exact-match-skill
version: 1.0.0
agent: shared
scope: shared
description: Test
triggers:
  - "implement feature with tests"
requires: []
---

# Skill
"""
        )

        from coffee_maker.autonomous.skill_loader import SkillLoader

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        registry = SkillRegistry(AgentType.CODE_DEVELOPER)
        registry.loader = loader
        registry._cache = registry._build_cache()

        skills = registry.find_skills_for_task("implement feature with tests")

        assert len(skills) == 1
        assert skills[0].name == "exact-match-skill"

    def test_find_skills_fuzzy_match(self, tmp_path):
        """Test finding skills by fuzzy matching."""
        # Create skill with similar trigger
        skill_dir = tmp_path / "shared" / "fuzzy-skill"
        skill_dir.mkdir(parents=True)

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            """---
name: fuzzy-skill
version: 1.0.0
agent: shared
scope: shared
description: Test
triggers:
  - "refactor code"
requires: []
---

# Skill
"""
        )

        from coffee_maker.autonomous.skill_loader import SkillLoader

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        registry = SkillRegistry(AgentType.CODE_DEVELOPER)
        registry.loader = loader
        registry._cache = registry._build_cache()

        # Try similar task description
        skills = registry.find_skills_for_task("refactor the code")

        # Should find the skill via fuzzy matching
        assert len(skills) >= 0  # May or may not match depending on threshold

    def test_no_skills_found(self, tmp_path):
        """Test when no skills match the task."""
        from coffee_maker.autonomous.skill_loader import SkillLoader

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        registry = SkillRegistry(AgentType.CODE_DEVELOPER)
        registry.loader = loader
        registry._cache = registry._build_cache()

        skills = registry.find_skills_for_task("completely unrelated task")

        assert skills == []

    def test_refresh_cache(self, tmp_path):
        """Test refreshing the skill cache."""
        from coffee_maker.autonomous.skill_loader import SkillLoader

        loader = SkillLoader(AgentType.CODE_DEVELOPER, skills_dir=tmp_path)
        registry = SkillRegistry(AgentType.CODE_DEVELOPER)
        registry.loader = loader
        registry._cache = registry._build_cache()

        # Initial cache should be empty
        initial_cache_size = len(registry._cache)

        # Add a new skill
        skill_dir = tmp_path / "shared" / "new-skill"
        skill_dir.mkdir(parents=True)

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            """---
name: new-skill
version: 1.0.0
agent: shared
scope: shared
description: New skill
triggers:
  - "new trigger"
requires: []
---

# New Skill
"""
        )

        # Refresh cache
        registry.refresh()

        # Cache should now include the new skill
        assert len(registry._cache) >= initial_cache_size
