"""Comprehensive tests for architect agent registration and operations.

This test suite verifies that the architect agent is properly registered
and operational in the autonomous agent system.

Tests:
    - AgentType enum includes ARCHITECT
    - File ownership rules correctly map to architect
    - AgentRegistry can register/unregister architect
    - Context manager works with architect
    - Singleton enforcement prevents duplicate architects
"""

import pytest
from coffee_maker.autonomous.agent_registry import (
    AgentRegistry,
    AgentType,
    AgentAlreadyRunningError,
)
from coffee_maker.autonomous.ace.file_ownership import (
    FileOwnership,
    OwnershipViolationError,
)


class TestArchitectAgentType:
    """Test that architect is properly defined in AgentType enum."""

    def test_architect_exists_in_agent_type(self):
        """Verify ARCHITECT exists in AgentType enum."""
        assert hasattr(AgentType, "ARCHITECT")
        assert AgentType.ARCHITECT.value == "architect"

    def test_all_agent_types_include_architect(self):
        """Verify architect is in the complete list of agent types."""
        all_types = [agent.value for agent in AgentType]
        assert "architect" in all_types

    def test_architect_agent_type_is_unique(self):
        """Verify architect value is unique (no duplicates)."""
        values = [agent.value for agent in AgentType]
        assert values.count("architect") == 1


class TestArchitectFileOwnership:
    """Test that architect has correct file ownership rules."""

    def test_architect_owns_architecture_directory(self):
        """Verify architect owns docs/architecture/ directory."""
        test_files = [
            "docs/architecture/specs/SPEC-001-test.md",
            "docs/architecture/decisions/ADR-001-test.md",
            "docs/architecture/guidelines/GUIDELINE-001-test.md",
            "docs/architecture/README.md",
        ]

        for test_file in test_files:
            owner = FileOwnership.get_owner(test_file)
            assert owner == AgentType.ARCHITECT, f"{test_file} should be owned by architect"

    def test_architect_owns_pyproject_toml(self):
        """Verify architect owns pyproject.toml (dependency management)."""
        owner = FileOwnership.get_owner("pyproject.toml")
        assert owner == AgentType.ARCHITECT

    def test_architect_owns_poetry_lock(self):
        """Verify architect owns poetry.lock."""
        owner = FileOwnership.get_owner("poetry.lock")
        assert owner == AgentType.ARCHITECT

    def test_architect_allowed_paths(self):
        """Verify architect's allowed path patterns."""
        allowed_paths = FileOwnership.get_allowed_paths(AgentType.ARCHITECT)

        expected_patterns = [
            "docs/architecture/**",
            "pyproject.toml",
            "poetry.lock",
        ]

        for pattern in expected_patterns:
            assert pattern in allowed_paths, f"Architect should own {pattern}"

    def test_architect_does_not_own_code_files(self):
        """Verify architect does NOT own implementation code (code_developer's domain)."""
        code_files = [
            "coffee_maker/cli/roadmap_cli.py",
            "tests/unit/test_something.py",
            "scripts/deploy.sh",
        ]

        for code_file in code_files:
            owner = FileOwnership.get_owner(code_file)
            assert owner != AgentType.ARCHITECT, f"{code_file} should NOT be owned by architect"
            assert owner == AgentType.CODE_DEVELOPER, f"{code_file} should be owned by code_developer"

    def test_architect_does_not_own_roadmap(self):
        """Verify architect does NOT own docs/roadmap/ (project_manager's domain)."""
        roadmap_files = [
            "docs/roadmap/ROADMAP.md",
            "docs/roadmap/PRIORITY_1_STRATEGIC_SPEC.md",
        ]

        for roadmap_file in roadmap_files:
            owner = FileOwnership.get_owner(roadmap_file)
            assert owner != AgentType.ARCHITECT, f"{roadmap_file} should NOT be owned by architect"
            assert owner == AgentType.PROJECT_MANAGER, f"{roadmap_file} should be owned by project_manager"


class TestArchitectRegistration:
    """Test that architect can be registered/unregistered in AgentRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        registry = AgentRegistry()
        registry.reset()

    def teardown_method(self):
        """Clean up registry after each test."""
        registry = AgentRegistry()
        registry.reset()

    def test_register_architect_agent(self):
        """Verify architect can be registered."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.ARCHITECT)

        assert registry.is_registered(AgentType.ARCHITECT)

        # Clean up
        registry.unregister_agent(AgentType.ARCHITECT)

    def test_unregister_architect_agent(self):
        """Verify architect can be unregistered."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.ARCHITECT)
        assert registry.is_registered(AgentType.ARCHITECT)

        registry.unregister_agent(AgentType.ARCHITECT)
        assert not registry.is_registered(AgentType.ARCHITECT)

    def test_get_architect_info(self):
        """Verify we can get architect agent info."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.ARCHITECT)

        info = registry.get_agent_info(AgentType.ARCHITECT)
        assert info is not None
        assert "pid" in info
        assert "started_at" in info

        # Clean up
        registry.unregister_agent(AgentType.ARCHITECT)

    def test_duplicate_architect_raises_error(self):
        """Verify that attempting to register architect twice raises error."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.ARCHITECT)

        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.ARCHITECT)

        assert "architect" in str(exc_info.value).lower()
        assert "already running" in str(exc_info.value).lower()

        # Clean up
        registry.unregister_agent(AgentType.ARCHITECT)


class TestArchitectContextManager:
    """Test architect agent with context manager pattern (RECOMMENDED usage)."""

    def setup_method(self):
        """Reset registry before each test."""
        registry = AgentRegistry()
        registry.reset()

    def teardown_method(self):
        """Clean up registry after each test."""
        registry = AgentRegistry()
        registry.reset()

    def test_context_manager_registers_and_unregisters(self):
        """Verify context manager properly registers/unregisters architect."""
        registry = AgentRegistry()

        assert not registry.is_registered(AgentType.ARCHITECT), "Should start unregistered"

        with AgentRegistry.register(AgentType.ARCHITECT):
            assert registry.is_registered(AgentType.ARCHITECT), "Should be registered inside context"

        assert not registry.is_registered(AgentType.ARCHITECT), "Should be unregistered after context"

    def test_context_manager_unregisters_on_exception(self):
        """Verify context manager unregisters even if exception occurs."""
        registry = AgentRegistry()

        with pytest.raises(ValueError):
            with AgentRegistry.register(AgentType.ARCHITECT):
                assert registry.is_registered(AgentType.ARCHITECT), "Should be registered"
                raise ValueError("Test exception")

        assert not registry.is_registered(AgentType.ARCHITECT), "Should be unregistered despite exception"

    def test_context_manager_prevents_duplicate_registration(self):
        """Verify context manager prevents duplicate architect registration."""
        with AgentRegistry.register(AgentType.ARCHITECT):
            # Attempt to register architect again should fail
            with pytest.raises(AgentAlreadyRunningError):
                with AgentRegistry.register(AgentType.ARCHITECT):
                    pass


class TestArchitectOwnershipEnforcement:
    """Test that ownership violations are properly detected for architect."""

    def test_check_ownership_returns_true_for_architect_files(self):
        """Verify architect ownership check returns True for architect-owned files."""
        architect_files = [
            "docs/architecture/specs/SPEC-001-test.md",
            "pyproject.toml",
            "poetry.lock",
        ]

        for file_path in architect_files:
            is_owner = FileOwnership.check_ownership(AgentType.ARCHITECT, file_path)
            assert is_owner, f"Architect should own {file_path}"

    def test_check_ownership_returns_false_for_non_architect_files(self):
        """Verify architect ownership check returns False for other agents' files."""
        other_agent_files = [
            ("coffee_maker/cli/roadmap_cli.py", AgentType.CODE_DEVELOPER),
            ("docs/roadmap/ROADMAP.md", AgentType.PROJECT_MANAGER),
        ]

        for file_path, expected_owner in other_agent_files:
            is_owner = FileOwnership.check_ownership(AgentType.ARCHITECT, file_path)
            assert not is_owner, f"Architect should NOT own {file_path}"

            # Verify correct owner
            actual_owner = FileOwnership.get_owner(file_path)
            assert actual_owner == expected_owner, f"{file_path} should be owned by {expected_owner.value}"

    def test_ownership_violation_raises_error(self):
        """Verify that ownership violation raises OwnershipViolationError."""
        # Try to claim code_developer's file as architect
        with pytest.raises(OwnershipViolationError) as exc_info:
            FileOwnership.check_ownership(
                AgentType.ARCHITECT, "coffee_maker/cli/roadmap_cli.py", raise_on_violation=True
            )

        assert "architect" in str(exc_info.value).lower()
        assert "code_developer" in str(exc_info.value).lower()


class TestArchitectIntegration:
    """Integration tests for architect agent in the full system."""

    def setup_method(self):
        """Reset registry before each test."""
        registry = AgentRegistry()
        registry.reset()

    def teardown_method(self):
        """Clean up registry after each test."""
        registry = AgentRegistry()
        registry.reset()

    def test_architect_can_coexist_with_other_agents(self):
        """Verify architect can be registered alongside other agents."""
        registry = AgentRegistry()

        # Register multiple agents including architect
        registry.register_agent(AgentType.ARCHITECT)
        registry.register_agent(AgentType.CODE_DEVELOPER)
        registry.register_agent(AgentType.PROJECT_MANAGER)

        # All should be registered
        assert registry.is_registered(AgentType.ARCHITECT)
        assert registry.is_registered(AgentType.CODE_DEVELOPER)
        assert registry.is_registered(AgentType.PROJECT_MANAGER)

        # Get all registered agents
        all_agents = registry.get_all_registered_agents()
        assert len(all_agents) == 3
        assert AgentType.ARCHITECT in all_agents
        assert AgentType.CODE_DEVELOPER in all_agents
        assert AgentType.PROJECT_MANAGER in all_agents

        # Clean up
        registry.reset()

    def test_architect_singleton_enforcement_across_attempts(self):
        """Verify singleton enforcement prevents multiple architect instances."""
        registry = AgentRegistry()
        registry.register_agent(AgentType.ARCHITECT)

        # Multiple registration attempts should all fail
        for _ in range(3):
            with pytest.raises(AgentAlreadyRunningError):
                registry.register_agent(AgentType.ARCHITECT)

        # Should still be registered
        assert registry.is_registered(AgentType.ARCHITECT)

        # Clean up
        registry.unregister_agent(AgentType.ARCHITECT)


class TestArchitectDocumentation:
    """Test that architect agent documentation exists and is accessible."""

    def test_architect_agent_file_exists(self):
        """Verify .claude/agents/architect.md exists."""
        import os

        agent_file = ".claude/agents/architect.md"
        assert os.path.exists(agent_file), f"Agent definition file should exist: {agent_file}"

    def test_architect_agent_file_has_content(self):
        """Verify architect.md has meaningful content."""
        with open(".claude/agents/architect.md", "r") as f:
            content = f.read()

        # Check for key sections
        assert "architect" in content.lower()
        assert "technical" in content.lower() or "architecture" in content.lower()
        assert len(content) > 100, "Agent file should have substantial content"


# Summary test to run all checks at once
def test_architect_agent_fully_operational():
    """
    Meta-test that verifies architect agent is fully operational.

    This test serves as a high-level verification that all components
    of the architect agent are working correctly.
    """
    # 1. AgentType includes architect
    assert AgentType.ARCHITECT.value == "architect"

    # 2. File ownership rules exist
    allowed_paths = FileOwnership.get_allowed_paths(AgentType.ARCHITECT)
    assert len(allowed_paths) >= 3  # Should own at least docs/architecture/**, pyproject.toml, poetry.lock

    # 3. Can register architect
    registry = AgentRegistry()
    registry.reset()

    try:
        with AgentRegistry.register(AgentType.ARCHITECT):
            assert registry.is_registered(AgentType.ARCHITECT)
    finally:
        registry.reset()

    # 4. Agent file exists
    import os

    assert os.path.exists(".claude/agents/architect.md")

    # If all checks pass, architect is fully operational!


class TestArchitectPOCCreation:
    """Test POC creation functionality (US-050)."""

    @pytest.fixture
    def agent(self, tmp_path):
        """Create ArchitectAgent with tmp directories."""
        from coffee_maker.autonomous.agents.architect_agent import ArchitectAgent

        status_dir = tmp_path / "status"
        message_dir = tmp_path / "messages"
        status_dir.mkdir()
        message_dir.mkdir()

        return ArchitectAgent(status_dir=status_dir, message_dir=message_dir)

    def test_should_create_poc_decision_matrix_high_complexity_high_effort(self, agent):
        """Test that POC is required for high effort + high complexity."""
        # High effort (>16 hours) + High complexity → POC REQUIRED
        assert agent._should_create_poc(20, "high") is True
        assert agent._should_create_poc(84, "high") is True
        assert agent._should_create_poc(16.1, "high") is True

    def test_should_create_poc_decision_matrix_medium_complexity_high_effort(self, agent):
        """Test that POC defaults to NO for medium complexity even with high effort."""
        # High effort (>16 hours) + Medium complexity → MAYBE (default: NO)
        assert agent._should_create_poc(20, "medium") is False
        assert agent._should_create_poc(84, "medium") is False

    def test_should_create_poc_decision_matrix_low_complexity(self, agent):
        """Test that POC is not needed for low complexity regardless of effort."""
        # Low complexity → NO POC
        assert agent._should_create_poc(8, "low") is False
        assert agent._should_create_poc(20, "low") is False
        assert agent._should_create_poc(84, "low") is False

    def test_should_create_poc_decision_matrix_low_effort(self, agent):
        """Test that POC is not needed for low effort even with high complexity."""
        # Low effort (<= 16 hours) → NO POC
        assert agent._should_create_poc(8, "high") is False
        assert agent._should_create_poc(16, "high") is False
        assert agent._should_create_poc(10, "medium") is False

    def test_should_create_poc_case_insensitive(self, agent):
        """Test that complexity parameter is case-insensitive."""
        # Case variations should work
        assert agent._should_create_poc(20, "HIGH") is True
        assert agent._should_create_poc(20, "High") is True
        assert agent._should_create_poc(20, "HiGh") is True

    def test_extract_requirements_from_priority_basic(self, agent):
        """Test basic requirements extraction from priority."""
        priority = {
            "number": "050",
            "name": "US-050",
            "title": "POC Creation Framework",
            "content": "Estimated Effort: 8-16 hours\nTechnical Complexity: High",
        }

        requirements = agent._extract_requirements_from_priority(priority)

        assert "title" in requirements
        assert "estimated_effort_hours" in requirements
        assert "technical_complexity" in requirements
        assert requirements["title"] == "POC Creation Framework"

    def test_generate_poc_readme_replaces_placeholders(self, tmp_path):
        """Test that POC README generation replaces template placeholders."""
        import os
        from pathlib import Path
        from coffee_maker.autonomous.agents.architect_agent import ArchitectAgent

        # Change to tmp directory for test
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create template for test
            template_dir = Path("docs/architecture/pocs/POC-000-template")
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "README.md").write_text("# POC-{number}: {Feature Name}\n{Date}\n{X-Y}")

            # Create agent
            status_dir = tmp_path / "status"
            message_dir = tmp_path / "messages"
            status_dir.mkdir()
            message_dir.mkdir()
            agent = ArchitectAgent(status_dir=status_dir, message_dir=message_dir)

            priority = {"number": "050", "name": "US-050", "title": "Test Feature"}
            requirements = {"title": "Test Feature", "estimated_effort_hours": 20, "technical_complexity": "high"}

            readme = agent._generate_poc_readme(priority, requirements)

            # Verify placeholders replaced
            assert "{number}" not in readme  # Should be replaced with "050"
            assert "{Feature Name}" not in readme  # Should be replaced with "Test Feature"
            assert "{Date}" not in readme  # Should be replaced with actual date
            assert "POC-050" in readme  # Should have actual number

        finally:
            os.chdir(original_cwd)

    def test_create_poc_creates_directory(self, tmp_path):
        """Test that _create_poc creates POC directory structure."""
        import os
        from pathlib import Path
        from coffee_maker.autonomous.agents.architect_agent import ArchitectAgent

        # Change to tmp directory for test
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create template directory for test
            template_dir = Path("docs/architecture/pocs/POC-000-template")
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "README.md").write_text("# POC-{number}: {Feature Name}\n{Date}\n{X-Y}")
            (template_dir / "example_component.py").write_text("# Example")
            (template_dir / "test_poc.py").write_text("# Test")

            # Create agent
            status_dir = tmp_path / "status"
            message_dir = tmp_path / "messages"
            status_dir.mkdir()
            message_dir.mkdir()
            agent = ArchitectAgent(status_dir=status_dir, message_dir=message_dir)

            priority = {"number": "999", "name": "US-999", "title": "Test Feature"}
            requirements = {"title": "Test Feature", "estimated_effort_hours": 20, "technical_complexity": "high"}

            poc_dir = agent._create_poc(priority, requirements)

            # Verify directory created
            assert poc_dir is not None
            assert poc_dir.exists()
            assert (poc_dir / "README.md").exists()

            # Verify README content
            readme_content = (poc_dir / "README.md").read_text()
            assert "POC-999" in readme_content
            assert "Test Feature" in readme_content

        finally:
            os.chdir(original_cwd)
