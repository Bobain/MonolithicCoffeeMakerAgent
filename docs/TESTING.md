# Testing Guide - MonolithicCoffeeMakerAgent

**Version**: 1.0
**Last Updated**: 2025-10-16 (US-021 Phase 4)
**Status**: Living Document

This guide covers testing strategies, tools, and best practices for the MonolithicCoffeeMakerAgent project.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Organization](#test-organization)
3. [Running Tests](#running-tests)
4. [Test Markers](#test-markers)
5. [Coverage Reporting](#coverage-reporting)
6. [Parallel Execution](#parallel-execution)
7. [Writing Tests](#writing-tests)
8. [Best Practices](#best-practices)

---

## Quick Start

```bash
# Install dependencies
poetry install

# Run all unit tests (fast, <30s)
pytest -m "not slow"

# Run all tests including slow ones
pytest

# Run with coverage
pytest --cov=coffee_maker --cov-report=term

# Run in parallel (for large test suites)
pytest -n auto
```

---

## Test Organization

### Directory Structure

```
tests/
├── unit/                  # Unit tests (fast, isolated)
│   ├── test_*.py         # Test modules
│   └── _deprecated/      # Old tests (excluded)
├── integration/          # Integration tests (marked slow)
├── e2e/                  # End-to-end tests (marked e2e)
└── fixtures/             # Shared fixtures
```

### Test Categories

**Unit Tests** (`tests/unit/`):
- Fast execution (< 1 second per test)
- Isolated components
- No external dependencies
- Mock external services

**Integration Tests** (marked `@pytest.mark.integration`):
- Test multiple components together
- May use real file I/O
- Can take 1-5 seconds per test

**End-to-End Tests** (marked `@pytest.mark.e2e`):
- Test complete workflows
- Use real services (if available)
- Can take 5+ seconds per test

**Slow Tests** (marked `@pytest.mark.slow`):
- Tests using `time.sleep()`
- Heavy computation
- Large data processing
- Excluded from fast test suite

---

## Running Tests

### Basic Commands

```bash
# All unit tests (fast)
pytest tests/unit/

# Specific test file
pytest tests/unit/test_notifications.py

# Specific test class
pytest tests/unit/test_notifications.py::TestNotificationDB

# Specific test method
pytest tests/unit/test_notifications.py::TestNotificationDB::test_add_notification

# Run with verbose output
pytest -v

# Stop at first failure
pytest -x

# Show local variables on failure
pytest -l

# Quiet mode (less output)
pytest -q
```

### Test Selection

```bash
# Fast tests only (exclude slow tests)
pytest -m "not slow"

# Only integration tests
pytest -m integration

# Only slow tests
pytest -m slow

# Combine markers (OR)
pytest -m "slow or integration"

# Combine markers (AND)
pytest -m "integration and not slow"
```

---

## Test Markers

### Available Markers

Defined in `pytest.ini`:

```ini
markers =
    slow: Tests that take >1 second (use time.sleep or heavy operations)
    integration: Integration tests that test multiple components together
    e2e: End-to-end tests that test complete workflows
    streamlit: Streamlit app tests (require streamlit server)
    unit: Fast unit tests (default)
```

### Using Markers

```python
import pytest
import time

@pytest.mark.slow
def test_with_sleep():
    """Test that uses time.sleep()."""
    time.sleep(3.0)
    assert True

@pytest.mark.integration
def test_full_workflow():
    """Test multiple components together."""
    # Test code
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_system():
    """End-to-end test of full system."""
    # Test code
    pass
```

### Marker Strategy

**When to mark as `@pytest.mark.slow`**:
- Uses `time.sleep()` for actual timing
- Takes > 1 second to execute
- Heavy computation or large data processing
- Network calls to real services (not mocked)

**CI/CD Strategy**:
- **PR checks**: Run fast tests only (`pytest -m "not slow"`)
- **Nightly builds**: Run all tests including slow ones (`pytest`)
- **Target**: Fast test suite < 30 seconds ✅ ACHIEVED (21.53s)

---

## Coverage Reporting

### Configuration

Coverage is configured in `pytest.ini`:

```ini
[coverage:run]
source = coffee_maker
omit =
    */tests/*
    */__pycache__/*
    */site-packages/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
fail_under = 80
```

### Running Coverage

```bash
# Terminal report
pytest --cov=coffee_maker --cov-report=term

# HTML report (detailed, opens in browser)
pytest --cov=coffee_maker --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=coffee_maker --cov-report=xml

# Multiple report formats
pytest --cov=coffee_maker --cov-report=term --cov-report=html
```

### Coverage Targets

**Project Goals**:
- Overall: **80%** (enforced)
- Core modules: **90%** (daemon, config, utils)
- Critical paths: **100%** (API calls, file I/O, error handling)

**Example Output**:
```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
coffee_maker/cli/notifications.py     150     30    80%
coffee_maker/config/manager.py          45      2    96%
coffee_maker/utils/file_io.py           30      0   100%
-------------------------------------------------------
TOTAL                                  225     32    86%
```

---

## Parallel Execution

### Overview

Parallel test execution uses `pytest-xdist` to run tests across multiple CPU cores.

**When to Use**:
- Large test suites (>100 tests)
- Long-running integration tests
- CI/CD with multiple workers

**When NOT to Use**:
- Small test sets (<50 tests) - overhead exceeds benefit
- Tests with shared state
- Tests that modify global configuration

### Commands

```bash
# Automatic worker count (uses all CPUs)
pytest -n auto

# Specific number of workers
pytest -n 4

# With coverage (requires pytest-cov)
pytest -n auto --cov=coffee_maker

# Load balancing strategy
pytest -n auto --dist loadscope  # Group by test scope
pytest -n auto --dist loadfile   # Group by file
pytest -n auto --dist loadgroup  # Group by xdist_group marker
```

### Performance Comparison

**Small Test Set** (43 tests):
- Sequential: 2.08s
- Parallel (8 workers): 7.73s
- **Verdict**: Sequential is faster (less overhead)

**Large Test Set** (expected >200 tests):
- Sequential: ~60s estimated
- Parallel (8 workers): ~15-20s estimated
- **Verdict**: Parallel is faster (4x speedup)

### Best Practices

1. **Use for CI/CD**: Parallel execution shines in CI/CD pipelines
2. **Avoid for development**: Overhead not worth it for quick test runs
3. **Isolate tests**: Ensure tests don't depend on execution order
4. **Resource limits**: Don't exceed available CPU cores

---

## Writing Tests

### Test Structure

**Standard Pattern**:
```python
import pytest
from coffee_maker.cli.notifications import NotificationDB

class TestNotificationDB:
    """Test notification database functionality."""

    def test_add_notification(self, tmp_path):
        """Test adding a notification."""
        # Arrange
        db = NotificationDB(db_path=tmp_path / "test.db")
        message = "Test notification"

        # Act
        db.add_notification("info", message)

        # Assert
        notifications = db.get_all_notifications()
        assert len(notifications) == 1
        assert notifications[0]["message"] == message
```

### Using Fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_db(tmp_path):
    """Create temporary notification database."""
    db_path = tmp_path / "notifications.db"
    db = NotificationDB(db_path=db_path)
    yield db
    # Cleanup happens automatically (tmp_path is removed)

def test_with_fixture(temp_db):
    """Test using fixture."""
    temp_db.add_notification("info", "Test")
    assert len(temp_db.get_all_notifications()) == 1
```

### Mocking

```python
import pytest
from unittest.mock import Mock, patch

def test_with_mock(monkeypatch):
    """Test with mocked API call."""
    # Mock environment variable
    monkeypatch.setenv("API_KEY", "test-key")

    # Mock external API
    mock_api = Mock()
    mock_api.call.return_value = "Success"

    with patch("coffee_maker.api.ClaudeAPI", return_value=mock_api):
        result = call_api("test prompt")
        assert result == "Success"
        mock_api.call.assert_called_once()
```

---

## Best Practices

### 1. Test Isolation

**✅ GOOD**: Independent tests
```python
def test_add_user(temp_db):
    """Each test uses fresh database."""
    temp_db.add_user("Alice")
    assert temp_db.count() == 1
```

**❌ BAD**: Tests depend on order
```python
def test_add_user():
    db.add_user("Alice")  # Shared state!

def test_user_count():
    assert db.count() == 1  # Breaks if order changes!
```

### 2. Fast by Default

**✅ GOOD**: Mock slow operations
```python
def test_api_call(monkeypatch):
    """Mock API call."""
    mock_api = Mock(return_value="result")
    monkeypatch.setattr("module.api.call", mock_api)
    assert call_api() == "result"
```

**❌ BAD**: Real API calls in unit tests
```python
def test_api_call():
    """Slow! Network I/O!"""
    result = real_api.call()  # Takes 2+ seconds
    assert result
```

### 3. Clear Test Names

**✅ GOOD**: Descriptive names
```python
def test_add_notification_with_valid_message():
    """Test adding notification with valid message."""

def test_add_notification_raises_error_on_empty_message():
    """Test that empty message raises ValueError."""
```

**❌ BAD**: Vague names
```python
def test_1():
    """What does this test?"""

def test_notification():
    """Too generic."""
```

### 4. Arrange-Act-Assert Pattern

```python
def test_user_creation():
    """Test user creation workflow."""
    # Arrange - Set up test data
    name = "Alice"
    email = "alice@example.com"

    # Act - Perform the action
    user = create_user(name, email)

    # Assert - Verify the outcome
    assert user.name == name
    assert user.email == email
    assert user.id is not None
```

### 5. Use Markers Appropriately

```python
# Fast unit test - no marker needed
def test_validation():
    assert validate_email("test@example.com") == True

# Slow test - mark it!
@pytest.mark.slow
def test_with_delay():
    time.sleep(2.0)
    assert True

# Integration test - mark it!
@pytest.mark.integration
def test_full_workflow():
    # Multiple components
    pass
```

---

## Performance Optimization

### Current Stats (US-021 Phase 3 + 4)

**Test Suite Performance**:
- **Before optimization**: 169.26s (2m 49s) - Too slow
- **After optimization**: 21.53s - Fast enough for CI/CD
- **Improvement**: 87% faster (7.9x speed improvement!)

**Optimization Strategies**:
1. Mark slow tests with `@pytest.mark.slow`
2. Run fast tests in CI/CD: `pytest -m "not slow"`
3. Run all tests nightly: `pytest`
4. Use parallel execution for large suites: `pytest -n auto`

**ROADMAP Parsing** (US-021 Phase 4):
- **Before**: 16.31ms per parse
- **After**: 0.06ms per parse (cached)
- **Improvement**: 274x faster (99.6% reduction!)

---

## Troubleshooting

### Common Issues

**Tests fail with "ModuleNotFoundError"**:
```bash
# Solution: Install dependencies
poetry install
```

**Tests hang or timeout**:
```bash
# Solution: Identify and mark slow tests
pytest --durations=10  # Show 10 slowest tests
```

**Coverage not collected**:
```bash
# Solution: Ensure source is specified
pytest --cov=coffee_maker --cov-report=term
```

**Parallel execution fails**:
```bash
# Solution: Tests may have shared state
# Run sequentially or fix test isolation
pytest tests/unit/ --verbose
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run fast tests
        run: poetry run pytest -m "not slow" --cov=coffee_maker --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Additional Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **pytest-xdist**: https://pytest-xdist.readthedocs.io/
- **REFACTORING_GUIDE.md**: Testing best practices
- **PERFORMANCE_ANALYSIS.md**: Performance optimization details

---

**Document Owner**: code_developer
**Last Updated**: 2025-10-16 (US-021 Phase 4 Complete)

---

🤖 *Generated with [Claude Code](https://claude.com/claude-code) via code_developer*
