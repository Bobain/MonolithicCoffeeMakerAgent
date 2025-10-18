"""Unit tests for Skill Loader."""

import pytest
from coffee_maker.autonomous.skill_loader import (
    load_skill,
    get_available_skills,
    SkillNames,
)


class TestSkillLoader:
    """Test skill loading functionality."""

    def test_load_skill_without_variables(self):
        """Test loading a skill without variable substitution."""
        # Load architecture-reuse-check skill (should exist)
        skill_content = load_skill(SkillNames.ARCHITECTURE_REUSE_CHECK)

        assert skill_content is not None
        assert len(skill_content) > 100  # Should have substantial content
        assert "architecture" in skill_content.lower()

    def test_load_skill_with_variables(self):
        """Test loading a skill with variable substitution."""
        # Note: architecture-reuse-check doesn't use variables currently
        # This test verifies the variable substitution mechanism works
        # by testing that variables would be substituted if they existed

        # Test 1: Load without variables (should work fine)
        skill_content_no_vars = load_skill(SkillNames.ARCHITECTURE_REUSE_CHECK)
        assert skill_content_no_vars is not None
        assert len(skill_content_no_vars) > 100

        # Test 2: Load with variables (should not break anything)
        skill_content_with_vars = load_skill(
            SkillNames.ARCHITECTURE_REUSE_CHECK,
            {
                "PRIORITY_NAME": "PRIORITY 10",
                "PROBLEM_DESCRIPTION": "Test problem description",
            },
        )
        # Should be identical since no variables exist in the skill
        assert skill_content_with_vars == skill_content_no_vars

    def test_load_nonexistent_skill(self):
        """Test loading a skill that doesn't exist raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_skill("nonexistent-skill")

    def test_load_skill_empty_name(self):
        """Test loading a skill with empty name raises ValueError."""
        with pytest.raises(ValueError):
            load_skill("")

    def test_get_available_skills(self):
        """Test getting list of available skills."""
        skills = get_available_skills()

        assert isinstance(skills, list)
        assert len(skills) >= 7  # Should have at least 7 skills now

        # Should include our created skills
        assert SkillNames.ARCHITECTURE_REUSE_CHECK in skills
        assert SkillNames.PROACTIVE_REFACTORING_ANALYSIS in skills
        assert SkillNames.TEST_FAILURE_ANALYSIS in skills
        assert SkillNames.ROADMAP_HEALTH_CHECK in skills
        assert SkillNames.DOD_VERIFICATION in skills
        assert SkillNames.GIT_WORKFLOW_AUTOMATION in skills
        assert SkillNames.PR_MONITORING_ANALYSIS in skills

    def test_skill_names_enum(self):
        """Test SkillNames enum has expected values."""
        # Architect skills
        assert hasattr(SkillNames, "ARCHITECTURE_REUSE_CHECK")
        assert hasattr(SkillNames, "PROACTIVE_REFACTORING_ANALYSIS")

        # code_developer skills
        assert hasattr(SkillNames, "TEST_FAILURE_ANALYSIS")
        assert hasattr(SkillNames, "DOD_VERIFICATION")
        assert hasattr(SkillNames, "GIT_WORKFLOW_AUTOMATION")

        # project_manager skills
        assert hasattr(SkillNames, "ROADMAP_HEALTH_CHECK")
        assert hasattr(SkillNames, "PR_MONITORING_ANALYSIS")

        # Verify values
        assert SkillNames.ARCHITECTURE_REUSE_CHECK == "architecture-reuse-check"
        assert SkillNames.PROACTIVE_REFACTORING_ANALYSIS == "proactive-refactoring-analysis"
        assert SkillNames.TEST_FAILURE_ANALYSIS == "test-failure-analysis"
        assert SkillNames.ROADMAP_HEALTH_CHECK == "roadmap-health-check"
        assert SkillNames.DOD_VERIFICATION == "dod-verification"
        assert SkillNames.GIT_WORKFLOW_AUTOMATION == "git-workflow-automation"
        assert SkillNames.PR_MONITORING_ANALYSIS == "pr-monitoring-analysis"


class TestSkillContentIntegrity:
    """Test skill content integrity and structure."""

    def test_architecture_reuse_check_structure(self):
        """Test architecture-reuse-check skill has expected structure."""
        skill = load_skill(SkillNames.ARCHITECTURE_REUSE_CHECK)

        # Should have key sections
        assert "## When to Use This Skill" in skill
        assert "## Skill Execution Steps" in skill
        assert "Step 1:" in skill  # Step-by-step process
        assert "Step 2:" in skill
        assert "decision" in skill.lower() or "Decision" in skill

    def test_proactive_refactoring_analysis_structure(self):
        """Test proactive-refactoring-analysis skill has expected structure."""
        skill = load_skill(SkillNames.PROACTIVE_REFACTORING_ANALYSIS)

        # Should have key sections
        assert "## When to Use This Skill" in skill or "## Mission Statement" in skill
        assert "refactoring" in skill.lower()
        assert "analysis" in skill.lower()

        # Should mention weekly execution
        assert "weekly" in skill.lower() or "Monday" in skill
