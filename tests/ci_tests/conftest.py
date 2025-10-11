"""Pytest configuration and fixtures for CI tests.

This module provides shared fixtures and configuration for all
CI tests of the code_developer daemon.
"""

import pytest


@pytest.fixture
def sample_roadmap():
    """Sample ROADMAP content for testing."""
    return """
# Project Roadmap

### 🔴 **PRIORITY 1: First Feature** ✅ Complete

**Status**: ✅ Complete

This priority is already complete.

**Deliverables**:
- Create initial setup
- Configure project

### 🔴 **PRIORITY 2: Active Feature** 📝 Planned

**Status**: 📝 Planned

This priority should be picked up by the daemon.

**Deliverables**:
- Implement feature A
- Add tests for feature A
- Update documentation

### 🔴 **PRIORITY 3: Future Feature** 📝 Planned

**Status**: 📝 Planned

This priority comes later.

**Deliverables**:
- Implement feature B
"""


@pytest.fixture
def empty_roadmap():
    """Empty ROADMAP content for testing."""
    return """
# Project Roadmap

No priorities defined yet.
"""


@pytest.fixture
def invalid_roadmap():
    """Invalid/malformed ROADMAP content for testing."""
    return """
# Project Roadmap

### PRIORITY 1 Missing Format

This priority is missing the required format markers.

Content without proper structure.
"""


@pytest.fixture
def temp_roadmap(sample_roadmap, tmp_path):
    """Create temporary ROADMAP file for testing.

    Args:
        sample_roadmap: Sample roadmap content fixture
        tmp_path: pytest tmp_path fixture

    Returns:
        Path to temporary ROADMAP.md file
    """
    roadmap_path = tmp_path / "ROADMAP.md"
    roadmap_path.write_text(sample_roadmap)
    return str(roadmap_path)


@pytest.fixture
def temp_roadmap_empty(empty_roadmap, tmp_path):
    """Create temporary empty ROADMAP file for testing."""
    roadmap_path = tmp_path / "ROADMAP_empty.md"
    roadmap_path.write_text(empty_roadmap)
    return str(roadmap_path)


@pytest.fixture
def temp_roadmap_invalid(invalid_roadmap, tmp_path):
    """Create temporary invalid ROADMAP file for testing."""
    roadmap_path = tmp_path / "ROADMAP_invalid.md"
    roadmap_path.write_text(invalid_roadmap)
    return str(roadmap_path)


@pytest.fixture
def mock_priority():
    """Mock priority dictionary for testing."""
    return {
        "name": "PRIORITY 2",
        "number": "2",
        "title": "Test Feature",
        "status": "📝 Planned",
        "content": """
### 🔴 **PRIORITY 2: Test Feature** 📝 Planned

**Status**: 📝 Planned

Implement test feature with comprehensive testing.

**Deliverables**:
- Create test_feature.py
- Add unit tests
- Update README.md
""",
    }


@pytest.fixture
def mock_documentation_priority():
    """Mock documentation priority for testing."""
    return {
        "name": "PRIORITY 3",
        "number": "3",
        "title": "User Documentation",
        "status": "📝 Planned",
        "content": """
### 🔴 **PRIORITY 3: User Documentation** 📝 Planned

**Status**: 📝 Planned

Create comprehensive user documentation.

**Deliverables**:
- Create docs/USER_GUIDE.md
- Create docs/QUICKSTART.md
- Update README.md with examples
""",
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may be slow or require external services)"
    )
    config.addinivalue_line("markers", "slow: mark test as slow-running")
