# CI Tests for code_developer Daemon

This directory contains comprehensive CI tests for the `code_developer` autonomous daemon. These tests ensure the daemon remains functional for end users and prevent regressions.

## Test Structure

```
tests/ci_tests/
├── README.md                           # This file
├── test_daemon_smoke.py                # Quick smoke tests (<1min)
├── test_daemon_cli_mode.py             # Claude CLI mode tests
├── test_daemon_api_mode.py             # Anthropic API mode tests
├── test_daemon_integration.py          # End-to-end workflows
├── test_daemon_user_scenarios.py       # Critical user scenarios
├── test_roadmap_parsing.py             # ROADMAP parsing tests
├── test_git_operations.py              # Git workflow tests
├── test_notification_system.py         # Notification tests
├── test_error_handling.py              # Error scenarios
├── conftest.py                         # Pytest fixtures
└── fixtures/
    ├── sample_roadmap.md               # Test ROADMAP
    ├── sample_roadmap_empty.md         # Empty ROADMAP test
    └── sample_roadmap_invalid.md       # Invalid ROADMAP test
```

## Test Categories

### 1. Smoke Tests (`test_daemon_smoke.py`)
**Purpose**: Fast tests that verify basic functionality (run on every commit)
**Runtime**: <1 minute
**Coverage**:
- Module imports
- Daemon initialization (CLI and API modes)
- ROADMAP parser functionality
- Git manager basic operations

**Run**:
```bash
pytest tests/ci_tests/test_daemon_smoke.py -v
```

### 2. Claude CLI Mode Tests (`test_daemon_cli_mode.py`)
**Purpose**: Verify Claude CLI integration works correctly
**Runtime**: 2-3 minutes
**Coverage**:
- Claude CLI availability check
- Simple prompt execution
- Timeout handling
- Invalid path error handling
- Daemon CLI mode initialization

**Run**:
```bash
pytest tests/ci_tests/test_daemon_cli_mode.py -v
```

### 3. Anthropic API Mode Tests (`test_daemon_api_mode.py`)
**Purpose**: Verify Anthropic API integration works correctly
**Runtime**: 2-3 minutes
**Coverage**:
- API client initialization
- API key validation
- Simple API calls
- Error handling
- Rate limiting

**Run**:
```bash
pytest tests/ci_tests/test_daemon_api_mode.py -v
```

### 4. Integration Tests (`test_daemon_integration.py`)
**Purpose**: Test complete workflows end-to-end
**Runtime**: 5-10 minutes
**Coverage**:
- Full daemon cycle: parse → execute → commit → PR
- Branch creation and switching
- Multi-priority workflows
- Notification creation and handling

**Run**:
```bash
pytest tests/ci_tests/test_daemon_integration.py -v -m integration
```

### 5. User Scenario Tests (`test_daemon_user_scenarios.py`)
**Purpose**: Test critical user workflows
**Runtime**: 3-5 minutes
**Coverage**:
- First-time user setup
- Interactive mode (approval workflow)
- Auto-approve mode
- Error recovery scenarios
- Max retry behavior

**Run**:
```bash
pytest tests/ci_tests/test_daemon_user_scenarios.py -v
```

### 6. ROADMAP Parsing Tests (`test_roadmap_parsing.py`)
**Purpose**: Verify ROADMAP.md parsing is robust
**Runtime**: <1 minute
**Coverage**:
- Priority extraction
- Status detection (Planned, Complete, In Progress)
- Malformed ROADMAP handling
- Edge cases (empty, invalid, missing sections)

**Run**:
```bash
pytest tests/ci_tests/test_roadmap_parsing.py -v
```

### 7. Git Operations Tests (`test_git_operations.py`)
**Purpose**: Verify git workflow operations
**Runtime**: 1-2 minutes
**Coverage**:
- Branch creation
- Commit creation
- Change detection
- Clean state detection
- PR creation (mocked)

**Run**:
```bash
pytest tests/ci_tests/test_git_operations.py -v
```

### 8. Notification System Tests (`test_notification_system.py`)
**Purpose**: Verify notification system works correctly
**Runtime**: 1-2 minutes
**Coverage**:
- Notification creation
- Notification retrieval
- Approval workflow
- Timeout handling

**Run**:
```bash
pytest tests/ci_tests/test_notification_system.py -v
```

### 9. Error Handling Tests (`test_error_handling.py`)
**Purpose**: Verify daemon handles errors gracefully
**Runtime**: 1-2 minutes
**Coverage**:
- Missing ROADMAP
- Invalid ROADMAP
- Missing Claude CLI
- Missing API key
- No planned priorities

**Run**:
```bash
pytest tests/ci_tests/test_error_handling.py -v
```

## Running Tests

### Run All CI Tests
```bash
# All tests (fast only)
pytest tests/ci_tests/ -v

# Include integration tests (slower)
pytest tests/ci_tests/ -v -m "not slow"

# All tests including slow ones
pytest tests/ci_tests/ -v --run-slow
```

### Run Specific Test Categories
```bash
# Smoke tests only (fastest)
pytest tests/ci_tests/test_daemon_smoke.py -v

# User scenarios
pytest tests/ci_tests/test_daemon_user_scenarios.py -v

# Integration tests (requires Claude CLI)
pytest tests/ci_tests/test_daemon_integration.py -v -m integration
```

### Run Tests with Coverage
```bash
pytest tests/ci_tests/ --cov=coffee_maker.autonomous --cov-report=html
```

## Test Markers

Tests use pytest markers to categorize execution:

- `@pytest.mark.integration` - Full integration tests (requires Claude CLI/API)
- `@pytest.mark.slow` - Tests that take >30 seconds
- `@pytest.mark.smoke` - Fast smoke tests (<1 minute total)

## CI Integration

These tests run automatically via GitHub Actions:

### On Every PR to Main
```yaml
- Smoke tests (fast validation)
- Unit tests
- Error handling tests
```

### On Significant Releases
```yaml
- All tests including integration
- Daemon health checks
- Non-regression suite
```

### On Manual Dispatch
```yaml
- Custom test selection
- Specific priority testing
- Full E2E validation
```

## Test Fixtures

Shared fixtures are defined in `conftest.py`:

- `tmp_roadmap` - Temporary ROADMAP.md for testing
- `test_daemon` - Pre-configured DevDaemon instance
- `mock_git` - Mocked GitManager for tests
- `test_db` - Temporary notifications database

## Success Criteria

Tests must meet these criteria:

- ✅ All tests pass on CI before merge
- ✅ Tests cover 90%+ of user scenarios
- ✅ Tests run in <10 minutes total
- ✅ Clear test failure messages guide debugging
- ✅ Both CLI and API modes tested
- ✅ No false positives (flaky tests)

## Troubleshooting

### Tests Fail with "Claude CLI not found"
```bash
# Install Claude CLI
brew install anthropics/claude/claude

# Or specify custom path
export CLAUDE_CLI_PATH=/path/to/claude
```

### Tests Fail with "API key not found"
```bash
# Set API key for API mode tests
export ANTHROPIC_API_KEY=sk-ant-...
```

### Integration Tests Timeout
```bash
# Increase timeout for slow connections
pytest tests/ci_tests/ --timeout=300
```

### Tests Fail Inside Claude Code Session
These tests should be run in a **separate terminal**, not inside an active Claude Code session, to avoid resource conflicts.

## Contributing

When adding new daemon functionality:

1. **Add tests first** (TDD approach)
2. **Update this README** with new test categories
3. **Ensure tests are fast** (<10 min total)
4. **Use appropriate markers** (`@pytest.mark.integration`, etc.)
5. **Update fixtures** in `conftest.py` if needed
6. **Document failure modes** and troubleshooting

## Related Documentation

- [Daemon Testing Guide](../../docs/DAEMON_TESTING.md)
- [Release Checklist](../../docs/RELEASE_CHECKLIST.md)
- [Non-Regression Tests](../autonomous/test_daemon_regression.py)
- [GitHub Actions Workflow](../../.github/workflows/daemon-test.yml)
