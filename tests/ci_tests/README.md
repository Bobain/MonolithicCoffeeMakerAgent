# CI Tests for code_developer Daemon

This directory contains comprehensive CI tests for the `code_developer` autonomous development daemon.

## Overview

The CI test suite ensures the daemon works correctly for end users before code reaches production. Tests cover:

- **Smoke tests**: Fast checks for obvious breakage (<1 minute)
- **CLI mode tests**: Claude CLI integration
- **API mode tests**: Anthropic API integration
- **User scenarios**: Critical user workflows
- **Error handling**: Graceful error handling
- **Integration tests**: End-to-end workflows
- **Regression tests**: Core functionality preservation

## Test Structure

```
tests/ci_tests/
├── README.md                           # This file
├── conftest.py                         # Pytest fixtures
├── test_daemon_smoke.py                # Quick smoke tests (<1min)
├── test_daemon_cli_mode.py             # Claude CLI mode tests
├── test_daemon_api_mode.py             # Anthropic API mode tests
├── test_daemon_integration.py          # End-to-end workflows
├── test_daemon_user_scenarios.py       # Critical user scenarios
├── test_roadmap_parsing.py             # ROADMAP parsing tests
├── test_git_operations.py              # Git workflow tests
├── test_notification_system.py         # Notification tests
├── test_error_handling.py              # Error scenarios
└── fixtures/
    ├── sample_roadmap.md               # Test ROADMAP
    ├── sample_roadmap_empty.md         # Empty ROADMAP test
    └── sample_roadmap_invalid.md       # Invalid ROADMAP test
```

## Running Tests

### Run all tests

```bash
pytest tests/ci_tests/
```

### Run smoke tests only (fast)

```bash
pytest tests/ci_tests/test_daemon_smoke.py
```

### Run specific test file

```bash
pytest tests/ci_tests/test_daemon_cli_mode.py
```

### Run specific test

```bash
pytest tests/ci_tests/test_daemon_smoke.py::TestDaemonSmoke::test_daemon_imports_successfully
```

### Run with verbose output

```bash
pytest tests/ci_tests/ -v
```

### Run integration tests

```bash
pytest tests/ci_tests/ -m integration
```

### Skip integration tests (faster)

```bash
pytest tests/ci_tests/ -m "not integration"
```

### Run with coverage

```bash
pytest tests/ci_tests/ --cov=coffee_maker.autonomous --cov-report=html
```

## Test Categories

### Smoke Tests (`test_daemon_smoke.py`)

Fast tests that verify basic functionality:
- Module imports work
- Daemon initializes with defaults
- Components initialize correctly
- Both CLI and API modes work

**Run time**: <1 minute

### CLI Mode Tests (`test_daemon_cli_mode.py`)

Tests for Claude CLI integration:
- CLI availability check
- Simple prompt execution
- Timeout handling
- Error handling

**Requires**: Claude CLI installed at `/opt/homebrew/bin/claude`

### API Mode Tests (`test_daemon_api_mode.py`)

Tests for Anthropic API integration:
- API initialization
- API availability check
- Simple prompt execution
- Error handling

**Requires**: `ANTHROPIC_API_KEY` environment variable

### User Scenario Tests (`test_daemon_user_scenarios.py`)

Real user workflow tests:
- First-time setup
- Finding next planned task
- Max retries behavior
- No-changes detection
- Interactive mode

**Run time**: Fast (uses mocks/test roadmaps)

### Error Handling Tests (`test_error_handling.py`)

Error scenario tests:
- Missing ROADMAP
- Invalid ROADMAP format
- Claude CLI not found
- Missing API key
- No planned priorities
- Malformed priorities

**Run time**: Fast

### Integration Tests (`test_daemon_integration.py`)

End-to-end workflow tests:
- Full daemon initialization
- Prerequisite checking
- ROADMAP parsing
- Prompt building
- Commit message generation
- PR body generation

**Run time**: Moderate (marked with `@pytest.mark.integration`)

### ROADMAP Parsing Tests (`test_roadmap_parsing.py`)

ROADMAP.md parsing tests:
- Priority extraction
- Status extraction
- Deliverables extraction
- Priority filtering
- Malformed ROADMAP handling

**Run time**: Fast

### Git Operations Tests (`test_git_operations.py`)

Git workflow tests:
- Branch operations
- Status checking
- Remote detection
- Commit operations (integration)

**Run time**: Fast (basic), moderate (integration)

### Notification Tests (`test_notification_system.py`)

Notification system tests:
- Notification creation
- Pending notifications
- Priority filtering
- Responding to notifications
- Mark as read/dismissed

**Run time**: Fast

## Test Fixtures

### Sample ROADMAPs

The `fixtures/` directory contains sample ROADMAP files for testing:

- **`sample_roadmap.md`**: Valid ROADMAP with multiple priorities at different stages
- **`sample_roadmap_empty.md`**: Empty ROADMAP with no priorities
- **`sample_roadmap_invalid.md`**: ROADMAP with malformed priorities

### Pytest Fixtures (conftest.py)

Shared fixtures available in all tests:

- `sample_roadmap`: Sample ROADMAP content
- `empty_roadmap`: Empty ROADMAP content
- `invalid_roadmap`: Invalid ROADMAP content
- `temp_roadmap`: Temporary ROADMAP file
- `temp_roadmap_empty`: Temporary empty ROADMAP file
- `temp_roadmap_invalid`: Temporary invalid ROADMAP file
- `mock_priority`: Mock priority dictionary
- `mock_documentation_priority`: Mock documentation priority

## CI Integration

These tests run automatically on:

- **Pull requests to main** (before merge)
- **Significant releases** (published, created)
- **Version tags** (v*.*.*)
- **Manual dispatch** (on-demand)

See `.github/workflows/daemon-test.yml` for CI configuration.

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.integration`: Full integration tests (may be slow)
- `@pytest.mark.slow`: Slow-running tests

Skip integration tests for faster development:

```bash
pytest tests/ci_tests/ -m "not integration"
```

## Requirements

### All Tests

- Python 3.11+
- pytest
- Project dependencies (`poetry install`)

### CLI Mode Tests

- Claude CLI installed: `brew install claude-ai/claude/claude`
- Claude subscription active

### API Mode Tests

- `ANTHROPIC_API_KEY` environment variable set
- Anthropic API credits available

## Coverage Goals

- **Target**: 90%+ code coverage
- **Critical paths**: 100% coverage
  - Daemon initialization
  - ROADMAP parsing
  - Retry logic
  - Error handling

## Continuous Improvement

### Adding New Tests

1. Create test file in `tests/ci_tests/`
2. Follow naming convention: `test_*.py`
3. Use descriptive test names: `test_feature_behavior()`
4. Add docstrings explaining what is tested
5. Use appropriate fixtures from `conftest.py`
6. Mark integration tests with `@pytest.mark.integration`

### Test Guidelines

- **Fast by default**: Most tests should run in <1 second
- **Use mocks**: Avoid external API calls in unit tests
- **Use fixtures**: Reuse test data via fixtures
- **Clear assertions**: Use descriptive assertion messages
- **Cleanup**: Use fixtures with cleanup (tmp_path, etc.)

## Troubleshooting

### Claude CLI Tests Failing

```bash
# Check if Claude CLI is installed
which claude

# Install Claude CLI
brew install claude-ai/claude/claude

# Configure Claude CLI
claude configure
```

### API Tests Failing

```bash
# Check if API key is set
echo $ANTHROPIC_API_KEY

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...
```

### Database Lock Errors

```bash
# Remove test database
rm -f data/notifications.db*
```

### Permission Errors

```bash
# Ensure test directories are writable
chmod -R u+w tests/
```

## Related Documentation

- **Daemon Testing Guide**: `docs/DAEMON_TESTING.md`
- **Release Checklist**: `docs/RELEASE_CHECKLIST.md`
- **GitHub Workflow**: `.github/workflows/daemon-test.yml`
- **Non-Regression Tests**: `tests/autonomous/test_daemon_regression.py`
