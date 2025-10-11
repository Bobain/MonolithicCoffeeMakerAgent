"""Pytest configuration and fixtures for CI tests.

This file provides shared fixtures and configuration for all CI tests.
"""

import pytest
from pathlib import Path
from typing import Generator


@pytest.fixture
def tmp_roadmap(tmp_path) -> Path:
    """Create a temporary ROADMAP.md for testing.

    Returns:
        Path to temporary ROADMAP.md file
    """
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text(
        """
# Test Roadmap

### PRIORITY 1: First Task ✅ Complete
This task is already complete.

### PRIORITY 2: Current Task 📝 Planned
This is the current task to work on.

**Deliverables**:
- Create a test file
- Add some content

### PRIORITY 3: Future Task 📝 Planned
This task comes next.
    """
    )
    return roadmap


@pytest.fixture
def empty_roadmap(tmp_path) -> Path:
    """Create an empty ROADMAP.md for testing edge cases.

    Returns:
        Path to empty ROADMAP.md file
    """
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text("# Empty Roadmap\n\nNo priorities yet.\n")
    return roadmap


@pytest.fixture
def complete_roadmap(tmp_path) -> Path:
    """Create a ROADMAP.md with all tasks complete.

    Returns:
        Path to ROADMAP.md with all complete tasks
    """
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text(
        """
# Completed Roadmap

### PRIORITY 1: First Task ✅ Complete
Done!

### PRIORITY 2: Second Task ✅ Complete
Also done!

### PRIORITY 3: Third Task ✅ Complete
All complete!
    """
    )
    return roadmap


@pytest.fixture
def test_daemon(tmp_roadmap):
    """Create a DevDaemon instance for testing.

    Args:
        tmp_roadmap: Fixture providing temporary ROADMAP

    Returns:
        Configured DevDaemon instance
    """
    from coffee_maker.autonomous.daemon import DevDaemon

    daemon = DevDaemon(
        roadmap_path=str(tmp_roadmap), auto_approve=True, create_prs=False, use_claude_cli=True, max_retries=3
    )
    return daemon


@pytest.fixture
def mock_git_clean(monkeypatch):
    """Mock GitManager to always return clean status.

    This prevents tests from being affected by actual git state.
    """
    from coffee_maker.autonomous.git_manager import GitManager

    def mock_is_clean(self):
        return True

    monkeypatch.setattr(GitManager, "is_clean", mock_is_clean)


@pytest.fixture
def mock_git_dirty(monkeypatch):
    """Mock GitManager to always return dirty status.

    This simulates uncommitted changes for testing.
    """
    from coffee_maker.autonomous.git_manager import GitManager

    def mock_is_clean(self):
        return False

    monkeypatch.setattr(GitManager, "is_clean", mock_is_clean)


@pytest.fixture
def test_db(tmp_path) -> Generator[Path, None, None]:
    """Create a temporary notifications database for testing.

    Yields:
        Path to temporary database file

    Cleanup:
        Removes database after test
    """
    db_path = tmp_path / "test_notifications.db"
    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def mock_claude_cli_available(monkeypatch):
    """Mock Claude CLI to always be available.

    This allows tests to run without Claude CLI installed.
    """
    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

    def mock_is_available(self):
        return True

    def mock_check_available(self):
        return True

    monkeypatch.setattr(ClaudeCLIInterface, "is_available", mock_is_available)
    monkeypatch.setattr(ClaudeCLIInterface, "check_available", mock_check_available)


@pytest.fixture
def mock_claude_cli_unavailable(monkeypatch):
    """Mock Claude CLI to be unavailable.

    This simulates Claude CLI not being installed.
    """
    from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

    def mock_is_available(self):
        return False

    def mock_check_available(self):
        return False

    monkeypatch.setattr(ClaudeCLIInterface, "is_available", mock_is_available)
    monkeypatch.setattr(ClaudeCLIInterface, "check_available", mock_check_available)


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock ANTHROPIC_API_KEY environment variable.

    This allows API mode tests to run without real API key.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-12345")


@pytest.fixture
def sample_priority():
    """Provide a sample priority dictionary for testing.

    Returns:
        Dict with priority information
    """
    return {
        "name": "PRIORITY 1",
        "title": "Sample Task",
        "status": "planned",
        "content": """
This is a sample priority for testing.

**Deliverables**:
- Create sample.py
- Add tests
- Update documentation
        """,
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test (may be slow)")
    config.addinivalue_line("markers", "slow: mark test as slow (>30 seconds)")
    config.addinivalue_line("markers", "smoke: mark test as smoke test (fast, basic checks)")


def pytest_addoption(parser):
    """Add custom pytest command-line options."""
    parser.addoption("--run-slow", action="store_true", default=False, help="run slow tests")
    parser.addoption(
        "--run-e2e", action="store_true", default=False, help="run end-to-end tests (requires Claude CLI/API)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command-line options."""
    # Skip slow tests unless --run-slow is specified
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

    # Skip E2E tests unless --run-e2e is specified
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_e2e)
