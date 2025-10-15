"""Tests for architect agent with ACE integration."""

from unittest.mock import Mock, patch
from pathlib import Path

from coffee_maker.autonomous.agents.architect import Architect


class TestArchitectAgent:
    """Test architect agent functionality."""

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator")
    @patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config")
    def test_architect_automatically_enables_ace(self, mock_config, mock_generator_class, mock_getenv):
        """Verify architect automatically enables ACE."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_ARCHITECT":
                return "true"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_config.return_value = {}
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Clear singleton
        if hasattr(Architect, "_instance"):
            delattr(Architect, "_instance")

        # Create agent
        agent = Architect()

        # Verify ACE enabled
        assert agent.ace_enabled is True
        assert agent.generator is not None

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_architect_can_disable_ace(self, mock_getenv):
        """Verify architect can disable ACE via env var."""

        def getenv_side_effect(key, default=""):
            if key == "ACE_ENABLED_ARCHITECT":
                return "false"
            return default

        mock_getenv.side_effect = getenv_side_effect

        # Clear singleton
        if hasattr(Architect, "_instance"):
            delattr(Architect, "_instance")

        # Create agent
        agent = Architect()

        # Verify ACE disabled
        assert agent.ace_enabled is False
        assert agent.generator is None

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_architect_creates_directories(self, mock_getenv):
        """Verify architect creates required directories."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(Architect, "_instance"):
            delattr(Architect, "_instance")

        agent = Architect()

        # Verify directories exist
        assert agent.architecture_dir.exists()
        assert agent.specs_dir.exists()
        assert agent.decisions_dir.exists()
        assert agent.guidelines_dir.exists()

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_architect_properties(self, mock_getenv):
        """Verify architect agent properties."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(Architect, "_instance"):
            delattr(Architect, "_instance")

        agent = Architect()

        assert agent.agent_name == "architect"
        assert "architecture" in agent.agent_objective.lower()
        assert "specs" in agent.success_criteria.lower()  # "technical specs"

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_architect_creates_adr(self, mock_getenv):
        """Verify architect can create ADRs."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(Architect, "_instance"):
            delattr(Architect, "_instance")

        agent = Architect()

        # Create ADR
        adr_path = agent.create_adr(
            title="Test Decision",
            context="Testing ADR creation",
            decision="Use test framework",
            consequences="Better test coverage",
        )

        # Verify ADR created
        assert adr_path.exists()
        assert adr_path.name.startswith("ADR-")
        assert "test-decision" in adr_path.name.lower()

        # Verify content
        content = adr_path.read_text()
        assert "Test Decision" in content
        assert "Testing ADR creation" in content
        assert "Use test framework" in content
        assert "Better test coverage" in content

        # Cleanup
        adr_path.unlink()

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_architect_singleton_pattern(self, mock_getenv):
        """Verify architect uses singleton pattern."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(Architect, "_instance"):
            delattr(Architect, "_instance")

        # Create two instances
        agent1 = Architect()
        agent2 = Architect()

        # Verify they're the same instance
        assert agent1 is agent2

    @patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
    def test_architect_execute_implementation(self, mock_getenv):
        """Verify architect can execute implementation tasks."""
        mock_getenv.return_value = "false"

        # Clear singleton
        if hasattr(Architect, "_instance"):
            delattr(Architect, "_instance")

        agent = Architect()

        # Execute task
        result = agent._execute_implementation(
            task="Test Architecture",
            context={"requirements": ["req1", "req2"]},
        )

        # Verify result
        assert result["status"] == "success"
        assert "specification" in result
        assert "guidelines" in result
        assert result["ready_for_implementation"] is True

        # Cleanup created files
        spec_path = Path(result["specification"])
        if spec_path.exists():
            spec_path.unlink()
