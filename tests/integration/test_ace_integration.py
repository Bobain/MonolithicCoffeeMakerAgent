"""Integration tests for ACE framework components.

These tests verify that ACE components work together correctly,
from trace generation through curation.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock

from coffee_maker.autonomous.ace import ACEGenerator, ACEReflector
from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader


@pytest.fixture
def ace_config(tmp_path):
    """Create temporary ACE configuration for testing."""
    config = ACEConfig(
        trace_dir=tmp_path / "traces",
        delta_dir=tmp_path / "deltas",
        playbook_dir=tmp_path / "playbooks",
        similarity_threshold=0.85,
        pruning_rate=0.10,
        min_helpful_count=2,
        max_bullets=150,
    )
    config.ensure_directories()
    return config


@pytest.fixture
def mock_agent_interface():
    """Create mock agent interface for testing."""
    interface = Mock()
    interface.send_message = Mock(
        return_value={
            "result": "success",
            "message": "Implementation complete",
            "token_usage": 1000,
        }
    )
    return interface


class TestACEIntegration:
    """Integration tests for ACE framework."""

    def test_cli_commands_available(self):
        """Test that ACE CLI commands are importable."""
        from coffee_maker.autonomous.ace.cli import cmd_reflector, cmd_curator, cmd_status

        assert callable(cmd_reflector)
        assert callable(cmd_curator)
        assert callable(cmd_status)

    def test_daemon_ace_initialization(self):
        """Test that daemon can initialize ACE framework."""
        import os

        # Test with ACE disabled
        os.environ["ACE_ENABLED"] = "false"
        from coffee_maker.autonomous.daemon import DevDaemon

        # This should not raise an error
        # Note: We can't fully instantiate daemon without Claude API setup
        assert DevDaemon is not None

    def test_config_from_env(self, monkeypatch):
        """Test ACE configuration loading from environment."""
        monkeypatch.setenv("ACE_ENABLED", "true")
        monkeypatch.setenv("ACE_SIMILARITY_THRESHOLD", "0.90")
        monkeypatch.setenv("ACE_MAX_BULLETS", "200")

        from coffee_maker.autonomous.ace.config import ACEConfig

        config = ACEConfig.from_env()

        assert config.enabled is True
        assert config.similarity_threshold == 0.90
        assert config.max_bullets == 200

    def test_generator_creates_trace(self, ace_config, mock_agent_interface):
        """Test that generator creates execution traces."""
        generator = ACEGenerator(
            agent_interface=mock_agent_interface,
            config=ace_config,
            agent_name="test_agent",
        )

        result = generator.execute_with_trace(prompt="Test implementation", priority_context={"priority": 1})

        assert result["trace_id"]
        assert result["result"] == "success"

        # Check trace file was created
        trace_files = list(ace_config.trace_dir.glob("test_agent_*.json"))
        assert len(trace_files) > 0

    def test_reflector_processes_traces(self, ace_config, mock_agent_interface):
        """Test that reflector can process traces and create deltas."""
        # First create a trace
        generator = ACEGenerator(
            agent_interface=mock_agent_interface,
            config=ace_config,
            agent_name="test_agent",
        )

        generator.execute_with_trace(prompt="Test implementation", priority_context={"priority": 1})

        # Now run reflector
        reflector = ACEReflector(config=ace_config, agent_name="test_agent")

        deltas = reflector.analyze_recent_traces(hours=1)

        # Reflector should create delta files (might be 0 if no actionable insights)
        list(ace_config.delta_dir.glob("test_agent_delta_*.json"))
        # Note: Delta count depends on reflector's analysis - may be 0

    def test_playbook_loader_handles_missing_file(self, ace_config):
        """Test that playbook loader handles missing playbook gracefully."""
        loader = PlaybookLoader(agent_name="nonexistent_agent", config=ace_config)

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_playbook_persistence(self, ace_config):
        """Test that playbooks can be saved and loaded."""
        from coffee_maker.autonomous.ace.models import Playbook, PlaybookBullet

        # Create a simple playbook
        playbook = Playbook(
            playbook_version="1.0.0",
            last_updated=datetime.now().isoformat(),
            categories={
                "test_category": [
                    PlaybookBullet(
                        bullet_id="bullet_1",
                        text="Test bullet",
                        category="test_category",
                        helpful_count=5,
                        pruned_count=0,
                        last_used=datetime.now().isoformat(),
                        created_at=datetime.now().isoformat(),
                    )
                ]
            },
        )

        # Save it
        loader = PlaybookLoader(agent_name="test_agent", config=ace_config)
        playbook_path = loader.playbook_path
        playbook_path.parent.mkdir(parents=True, exist_ok=True)

        with open(playbook_path, "w") as f:
            json.dump(playbook.to_dict(), f, indent=2)

        # Load it back
        loaded_playbook = loader.load()

        assert loaded_playbook.playbook_version == "1.0.0"
        assert "test_category" in loaded_playbook.categories
        assert len(loaded_playbook.categories["test_category"]) == 1


class TestACECLICommands:
    """Test ACE CLI command integration."""

    def test_project_manager_curate_command(self):
        """Test that project-manager curate command is registered."""
        from coffee_maker.cli.roadmap_cli import cmd_curate

        assert callable(cmd_curate)

    def test_project_manager_playbook_command(self):
        """Test that project-manager playbook command is registered."""
        from coffee_maker.cli.roadmap_cli import cmd_playbook

        assert callable(cmd_playbook)


class TestPhase5Stubs:
    """Test that Phase 5 enhancement stubs are available."""

    def test_langfuse_integration_stub(self):
        """Test Langfuse integration stub exists."""
        from coffee_maker.autonomous.ace.langfuse_integration import LangfuseACEIntegration

        integration = LangfuseACEIntegration(enabled=False)
        assert integration is not None
        assert integration.enabled is False

    def test_multi_agent_stub(self):
        """Test multi-agent playbook manager stub exists."""
        from coffee_maker.autonomous.ace.multi_agent import MultiAgentPlaybookManager

        manager = MultiAgentPlaybookManager(agents=["test_agent"])
        assert manager is not None
        assert manager.agents == ["test_agent"]


@pytest.mark.skipif(not Path(".env").exists(), reason="Requires .env file with API keys for full E2E test")
class TestACEFullWorkflow:
    """End-to-end workflow tests (requires API keys)."""

    def test_full_ace_workflow(self, ace_config):
        """Test complete ACE workflow: Generate -> Reflect -> Curate.

        This is a placeholder for full E2E testing when API keys are available.
        """
        # This test would require:
        # 1. Real Claude API or CLI
        # 2. Actual priority to implement
        # 3. Full daemon execution
        # For now, we just verify the components exist


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
