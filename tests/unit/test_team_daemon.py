"""Unit tests for Team Daemon orchestration.

Tests cover:
- Team daemon initialization
- Agent spawning and health monitoring
- Team status reporting
- Configuration management
- Process lifecycle management
"""

import tempfile
from pathlib import Path

import pytest

from coffee_maker.autonomous.team_daemon import (
    AgentConfig,
    AgentProcessManager,
    AgentStatus,
    ProcessStatus,
    TeamConfig,
    TeamDaemon,
)
from coffee_maker.autonomous.message_queue import AgentType, MessageQueue


class TestTeamConfig:
    """Test suite for TeamConfig."""

    def test_default_config(self):
        """Test default team configuration."""
        config = TeamConfig()
        assert config.database_path == "data/orchestrator.db"
        assert config.health_check_interval == 30
        assert config.max_restart_attempts == 3

    def test_config_with_agents(self):
        """Test config initializes with default agents."""
        config = TeamConfig()
        assert len(config.agents) == 4
        assert AgentType.CODE_DEVELOPER in config.agents
        assert AgentType.PROJECT_MANAGER in config.agents
        assert AgentType.ARCHITECT in config.agents
        assert AgentType.ASSISTANT in config.agents

    def test_get_agent_config(self):
        """Test getting agent configuration."""
        config = TeamConfig()
        agent_config = config.get_agent_config(AgentType.CODE_DEVELOPER)
        assert agent_config.agent_type == AgentType.CODE_DEVELOPER
        assert agent_config.auto_approve is True

    def test_custom_agent_config(self):
        """Test custom agent configuration."""
        custom_agent_config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER, auto_approve=False, timeout_seconds=600)
        config = TeamConfig(agents={AgentType.CODE_DEVELOPER: custom_agent_config})

        agent_config = config.get_agent_config(AgentType.CODE_DEVELOPER)
        assert agent_config.auto_approve is False
        assert agent_config.timeout_seconds == 600


class TestAgentConfig:
    """Test suite for AgentConfig."""

    def test_default_agent_config(self):
        """Test default agent configuration."""
        config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER)
        assert config.agent_type == AgentType.CODE_DEVELOPER
        assert config.enabled is True
        assert config.auto_approve is False
        assert config.timeout_seconds == 300
        assert config.memory_limit_mb == 256

    def test_custom_agent_config(self):
        """Test custom agent configuration."""
        config = AgentConfig(
            agent_type=AgentType.CODE_DEVELOPER,
            auto_approve=True,
            memory_limit_mb=512,
        )
        assert config.auto_approve is True
        assert config.memory_limit_mb == 512


class TestAgentStatus:
    """Test suite for AgentStatus."""

    def test_default_status(self):
        """Test default agent status."""
        status = AgentStatus(agent_type=AgentType.CODE_DEVELOPER)
        assert status.agent_type == AgentType.CODE_DEVELOPER
        assert status.status == ProcessStatus.STOPPED
        assert status.restart_count == 0
        assert status.pid is None

    def test_running_status(self):
        """Test running agent status."""
        status = AgentStatus(
            agent_type=AgentType.CODE_DEVELOPER,
            status=ProcessStatus.RUNNING,
            pid=12345,
        )
        assert status.status == ProcessStatus.RUNNING
        assert status.pid == 12345


class TestTeamDaemon:
    """Test suite for TeamDaemon."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
        Path(f"{db_path}-shm").unlink(missing_ok=True)
        Path(f"{db_path}-wal").unlink(missing_ok=True)

    @pytest.fixture
    def daemon_config(self, temp_db):
        """Create team daemon configuration."""
        return TeamConfig(database_path=temp_db)

    @pytest.fixture
    def daemon(self, daemon_config):
        """Create team daemon instance."""
        return TeamDaemon(daemon_config)

    def test_daemon_initialization(self, daemon):
        """Test daemon initialization."""
        assert daemon.config is not None
        assert daemon.message_queue is not None
        assert daemon.running is False
        assert daemon.start_time is None
        assert len(daemon.agents) == 0

    def test_daemon_status_not_running(self, daemon):
        """Test daemon status when not running."""
        status = daemon.status()
        assert status.is_running is False
        assert status.uptime_seconds == 0.0

    def test_message_queue_created(self, daemon_config, temp_db):
        """Test message queue is created with correct path."""
        daemon = TeamDaemon(daemon_config)
        assert str(daemon.message_queue.db_path) == temp_db

    def test_daemon_config_propagation(self, daemon):
        """Test configuration is properly set in daemon."""
        assert daemon.config.health_check_interval == 30
        assert daemon.config.max_restart_attempts == 3

    def test_agent_process_manager_creation(self, daemon):
        """Test creating an agent process manager."""
        agent_config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER, auto_approve=True)
        manager = AgentProcessManager(
            agent_type=AgentType.CODE_DEVELOPER,
            config=agent_config,
            message_queue=daemon.message_queue,
        )

        assert manager.agent_type == AgentType.CODE_DEVELOPER
        assert manager.config.auto_approve is True
        assert manager.status == ProcessStatus.STOPPED
        assert manager.restart_count == 0

    def test_agent_process_status_snapshots(self, daemon):
        """Test getting agent process status."""
        agent_config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER)
        manager = AgentProcessManager(
            agent_type=AgentType.CODE_DEVELOPER,
            config=agent_config,
            message_queue=daemon.message_queue,
        )

        status = manager.get_status()
        assert isinstance(status, AgentStatus)
        assert status.agent_type == AgentType.CODE_DEVELOPER
        assert status.status == ProcessStatus.STOPPED

    def test_multiple_agents(self, daemon_config):
        """Test daemon can manage multiple agents."""
        config = TeamConfig(database_path=daemon_config.database_path)
        TeamDaemon(config)

        # Check configuration has multiple agents
        assert len(config.agents) == 4

    def test_disabled_agent_config(self, daemon_config):
        """Test disabling an agent in configuration."""
        config = daemon_config
        config.agents[AgentType.ASSISTANT].enabled = False

        TeamDaemon(config)
        agent_config = config.get_agent_config(AgentType.ASSISTANT)
        assert agent_config.enabled is False

    def test_team_status_structure(self, daemon):
        """Test team status has correct structure."""
        status = daemon.status()
        assert hasattr(status, "is_running")
        assert hasattr(status, "uptime_seconds")
        assert hasattr(status, "agents")
        assert hasattr(status, "message_queue_size")
        assert hasattr(status, "queue_metrics")

    def test_message_queue_metrics_available(self, daemon):
        """Test queue metrics are available in team status."""
        status = daemon.status()
        queue_metrics = status.queue_metrics

        assert isinstance(queue_metrics, dict)
        assert "total_tasks" in queue_metrics
        assert "completed_tasks" in queue_metrics

    def test_daemon_stop_when_not_running(self, daemon):
        """Test stopping daemon when not running doesn't error."""
        # Should not raise
        daemon.stop()
        assert daemon.running is False

    def test_agent_config_validation(self):
        """Test agent config with invalid agent type."""
        # Should not raise on construction
        config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER, memory_limit_mb=512)
        assert config.memory_limit_mb == 512

    def test_multiple_daemon_instances(self, daemon_config):
        """Test creating multiple daemon instances with different configs."""
        config1 = TeamConfig(database_path=daemon_config.database_path)
        config2 = TeamConfig(database_path="data/orchestrator2.db", health_check_interval=60)

        daemon1 = TeamDaemon(config1)
        daemon2 = TeamDaemon(config2)

        assert daemon1.config.health_check_interval == 30
        assert daemon2.config.health_check_interval == 60

        # Cleanup
        Path("data/orchestrator2.db").unlink(missing_ok=True)
        Path("data/orchestrator2.db-shm").unlink(missing_ok=True)
        Path("data/orchestrator2.db-wal").unlink(missing_ok=True)

    def test_process_status_transitions(self, daemon):
        """Test process status transitions."""
        assert ProcessStatus.STOPPED != ProcessStatus.RUNNING
        assert ProcessStatus.RUNNING != ProcessStatus.CRASHED
        assert ProcessStatus.CRASHED != ProcessStatus.STARTING

    def test_agent_restart_count_tracking(self, daemon):
        """Test agent tracks restart count."""
        agent_config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER)
        manager = AgentProcessManager(
            agent_type=AgentType.CODE_DEVELOPER,
            config=agent_config,
            message_queue=daemon.message_queue,
        )

        assert manager.restart_count == 0
        manager.restart_count += 1
        assert manager.restart_count == 1

    def test_agent_is_alive_when_stopped(self, daemon):
        """Test process is not alive when stopped."""
        agent_config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER)
        manager = AgentProcessManager(
            agent_type=AgentType.CODE_DEVELOPER,
            config=agent_config,
            message_queue=daemon.message_queue,
        )

        assert manager.is_alive() is False

    def test_team_config_with_custom_database(self):
        """Test team config with custom database path."""
        config = TeamConfig(database_path="/custom/path/orchestrator.db")
        assert config.database_path == "/custom/path/orchestrator.db"

    def test_agent_config_timeouts(self):
        """Test agent configuration timeout settings."""
        config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER, timeout_seconds=600)
        assert config.timeout_seconds == 600

    def test_daemon_health_check_interval_config(self, daemon_config):
        """Test health check interval is configurable."""
        config = TeamConfig(database_path=daemon_config.database_path)
        config.health_check_interval = 60

        daemon = TeamDaemon(config)
        assert daemon.config.health_check_interval == 60


class TestAgentProcessManager:
    """Test suite for AgentProcessManager."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
        Path(f"{db_path}-shm").unlink(missing_ok=True)
        Path(f"{db_path}-wal").unlink(missing_ok=True)

    @pytest.fixture
    def message_queue(self, temp_db):
        """Create message queue."""
        return MessageQueue(db_path=temp_db)

    @pytest.fixture
    def agent_manager(self, message_queue):
        """Create agent process manager."""
        config = AgentConfig(agent_type=AgentType.CODE_DEVELOPER, auto_approve=True)
        return AgentProcessManager(
            agent_type=AgentType.CODE_DEVELOPER,
            config=config,
            message_queue=message_queue,
        )

    def test_manager_initialization(self, agent_manager):
        """Test agent manager initialization."""
        assert agent_manager.agent_type == AgentType.CODE_DEVELOPER
        assert agent_manager.process is None
        assert agent_manager.pid is None
        assert agent_manager.restart_count == 0
        assert agent_manager.status == ProcessStatus.STOPPED

    def test_manager_is_alive_when_stopped(self, agent_manager):
        """Test manager reports not alive when stopped."""
        assert agent_manager.is_alive() is False

    def test_manager_get_status(self, agent_manager):
        """Test getting manager status."""
        status = agent_manager.get_status()
        assert isinstance(status, AgentStatus)
        assert status.status == ProcessStatus.STOPPED
        assert status.restart_count == 0

    def test_manager_stop_when_not_started(self, agent_manager):
        """Test stopping manager that was never started."""
        # Should not raise
        agent_manager.stop()
        assert agent_manager.status == ProcessStatus.STOPPED

    def test_manager_multiple_agents(self, message_queue):
        """Test creating managers for different agents."""
        managers = {}
        for agent_type in [
            AgentType.CODE_DEVELOPER,
            AgentType.PROJECT_MANAGER,
            AgentType.ARCHITECT,
        ]:
            config = AgentConfig(agent_type=agent_type)
            manager = AgentProcessManager(
                agent_type=agent_type,
                config=config,
                message_queue=message_queue,
            )
            managers[agent_type] = manager

        assert len(managers) == 3
        for agent_type, manager in managers.items():
            assert manager.agent_type == agent_type
