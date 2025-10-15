"""Unit tests for Streamlit EnvManager."""

import os
import tempfile
from pathlib import Path
import pytest
from coffee_maker.streamlit_app.utils.env_manager import EnvManager


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write('export COFFEE_MAKER_RUN_CI_TESTS="True"\n')
        f.write('export LANGFUSE_SECRET_KEY="test-key"\n')
        f.write('export ACE_ENABLED_USER_INTERPRET="true"\n')
        f.write('export ACE_ENABLED_CODE_DEVELOPER="false"\n')
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


def test_env_manager_reads_status(temp_env_file):
    """Test EnvManager reads ACE status correctly."""
    manager = EnvManager(env_path=temp_env_file)

    # Set environment variables to match file
    os.environ["ACE_ENABLED_USER_INTERPRET"] = "true"
    os.environ["ACE_ENABLED_CODE_DEVELOPER"] = "false"

    status_enabled = manager.get_agent_ace_status("user_interpret")
    status_disabled = manager.get_agent_ace_status("code_developer")

    assert status_enabled is True
    assert status_disabled is False


def test_env_manager_reads_default_status(temp_env_file):
    """Test EnvManager returns default (enabled) for unknown agents."""
    manager = EnvManager(env_path=temp_env_file)

    # Agent not in .env should default to enabled
    status = manager.get_agent_ace_status("unknown_agent")
    assert status is True


def test_env_manager_updates_status(temp_env_file):
    """Test EnvManager can update ACE status."""
    manager = EnvManager(env_path=temp_env_file)

    # Set initial state
    os.environ["ACE_ENABLED_TEST_AGENT"] = "true"

    # Test toggle to disabled
    success = manager.set_agent_ace_status("test_agent", False)
    assert success is True

    # Verify environment was updated
    assert os.environ.get("ACE_ENABLED_TEST_AGENT") == "false"

    # Verify file was updated
    content = temp_env_file.read_text()
    assert 'export ACE_ENABLED_TEST_AGENT="false"' in content


def test_env_manager_adds_new_variable(temp_env_file):
    """Test EnvManager can add new ACE variable to .env file."""
    manager = EnvManager(env_path=temp_env_file)

    # Add new agent
    success = manager.set_agent_ace_status("new_agent", True)
    assert success is True

    # Verify file was updated
    content = temp_env_file.read_text()
    assert 'export ACE_ENABLED_NEW_AGENT="true"' in content


def test_env_manager_get_all_agent_statuses(temp_env_file):
    """Test EnvManager can get all agent statuses."""
    manager = EnvManager(env_path=temp_env_file)

    # Set some environment variables
    os.environ["ACE_ENABLED_USER_INTERPRET"] = "true"
    os.environ["ACE_ENABLED_CODE_DEVELOPER"] = "false"

    statuses = manager.get_all_agent_statuses()

    assert isinstance(statuses, dict)
    assert "user_interpret" in statuses
    assert "code_developer" in statuses
    assert "assistant" in statuses
    assert len(statuses) == 6  # Should have 6 known agents


def test_env_manager_handles_missing_file():
    """Test EnvManager handles missing .env file gracefully."""
    non_existent_path = Path("/tmp/non_existent_env_file_12345.env")
    manager = EnvManager(env_path=non_existent_path)

    # Should not raise error when reading (uses os.getenv)
    status = manager.get_agent_ace_status("user_interpret")
    assert isinstance(status, bool)

    # Should return False when trying to write to missing file
    success = manager.set_agent_ace_status("test_agent", False)
    assert success is False


def test_env_manager_updates_existing_variable(temp_env_file):
    """Test EnvManager updates existing variable instead of duplicating."""
    manager = EnvManager(env_path=temp_env_file)

    # Update existing variable twice
    manager.set_agent_ace_status("user_interpret", False)
    manager.set_agent_ace_status("user_interpret", True)

    # Verify file has only one occurrence
    content = temp_env_file.read_text()
    count = content.count("ACE_ENABLED_USER_INTERPRET")
    assert count == 1
