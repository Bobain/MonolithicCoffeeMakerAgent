# Daemon Testing Guide

Complete guide for testing the `code_developer` autonomous daemon.

## Overview

The daemon testing strategy has multiple layers:

1. **Smoke Tests**: Fast checks (<1 min) for obvious breakage
2. **Unit Tests**: Component-level testing
3. **Integration Tests**: End-to-end workflows
4. **Regression Tests**: Core functionality preservation
5. **CI Testing**: Automated testing on every PR/merge

## Quick Start

### Run All Tests

```bash
# All tests
pytest tests/

# CI tests only
pytest tests/ci_tests/

# Regression tests only
pytest tests/autonomous/
```

### Run Specific Test Suites

```bash
# Smoke tests (fastest)
pytest tests/ci_tests/test_daemon_smoke.py

# User scenario tests
pytest tests/ci_tests/test_daemon_user_scenarios.py

# Integration tests
pytest tests/ci_tests/ -m integration
```

## Production Monitoring

### Running the Daemon

```bash
# Auto-approve mode (fully autonomous)
poetry run code-developer --auto-approve

# Interactive mode (asks for approval)
poetry run code-developer

# CLI mode (uses Claude subscription)
poetry run code-developer --use-claude-cli --auto-approve

# API mode (uses Anthropic API credits)
poetry run code-developer --auto-approve
```

### Monitor Daemon Health

```bash
# Check for infinite loops
python scripts/check_daemon_health.py

# Check specific log file
python scripts/check_daemon_health.py --log-file daemon.log

# Custom max attempts threshold
python scripts/check_daemon_health.py --max-attempts 5
```

### Verify Notifications

```bash
# Verify notifications database
python scripts/verify_notifications.py

# Check specific database
python scripts/verify_notifications.py --db data/notifications.db

# View notifications via CLI
poetry run project-manager notifications
```

## CI Testing

### Automated Testing on GitHub

GitHub Actions runs daemon tests automatically on:

- **Pull requests to main** (before merging major changes)
- **Significant releases** (published releases, version tags)
- **Manual dispatch** (on-demand testing when needed)

### What CI Tests Verify

1. **No infinite loops**: Priority not retried >3 times
2. **Notifications created**: For blocked tasks and failures
3. **Daemon progresses**: Moves through roadmap correctly
4. **Core functionality intact**: Non-regression checks pass
5. **Both modes work**: CLI and API modes tested

### Triggering CI Tests

```bash
# Automatically triggered on:
git push origin feature-branch  # Creates PR
git tag -a v1.2.3 -m "Release"  # Version tag
git push origin v1.2.3

# Manual trigger via GitHub Actions UI
# Go to: Actions > Daemon Health Check > Run workflow
```

## Test Categories

### 1. Smoke Tests

**Purpose**: Fast sanity checks
**Run time**: <1 minute
**Location**: `tests/ci_tests/test_daemon_smoke.py`

```bash
pytest tests/ci_tests/test_daemon_smoke.py -v
```

**What's tested**:
- Module imports work
- Daemon initializes
- Components load correctly
- Both CLI and API modes initialize

### 2. CLI Mode Tests

**Purpose**: Verify Claude CLI integration
**Run time**: Fast (unit), Slow (integration)
**Location**: `tests/ci_tests/test_daemon_cli_mode.py`

**Requirements**:
- Claude CLI installed: `brew install claude-ai/claude/claude`
- Claude subscription active

```bash
# Skip if Claude CLI not installed
pytest tests/ci_tests/test_daemon_cli_mode.py -v

# Only unit tests (no actual CLI calls)
pytest tests/ci_tests/test_daemon_cli_mode.py -m "not integration"
```

### 3. API Mode Tests

**Purpose**: Verify Anthropic API integration
**Run time**: Fast (unit), Moderate (integration)
**Location**: `tests/ci_tests/test_daemon_api_mode.py`

**Requirements**:
- `ANTHROPIC_API_KEY` environment variable

```bash
# Export API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run tests
pytest tests/ci_tests/test_daemon_api_mode.py -v
```

### 4. User Scenario Tests

**Purpose**: Verify critical user workflows
**Run time**: Fast
**Location**: `tests/ci_tests/test_daemon_user_scenarios.py`

```bash
pytest tests/ci_tests/test_daemon_user_scenarios.py -v
```

**Scenarios tested**:
- First-time user setup
- Finding next planned task
- Max retries behavior
- No-changes detection
- Interactive mode

### 5. Error Handling Tests

**Purpose**: Verify graceful error handling
**Run time**: Fast
**Location**: `tests/ci_tests/test_error_handling.py`

```bash
pytest tests/ci_tests/test_error_handling.py -v
```

**Error scenarios**:
- Missing ROADMAP
- Invalid ROADMAP format
- Claude CLI not found
- Missing API key
- No planned priorities

### 6. Integration Tests

**Purpose**: End-to-end workflow testing
**Run time**: Moderate
**Location**: `tests/ci_tests/test_daemon_integration.py`

```bash
# Run all integration tests
pytest tests/ci_tests/ -m integration

# Skip integration tests (faster)
pytest tests/ci_tests/ -m "not integration"
```

### 7. Regression Tests

**Purpose**: Ensure core functionality unchanged
**Run time**: Fast
**Location**: `tests/autonomous/test_daemon_regression.py`

```bash
pytest tests/autonomous/test_daemon_regression.py -v
```

## Common Testing Scenarios

### Test New Priority Implementation

1. Add priority to ROADMAP.md
2. Run daemon in test mode:
   ```bash
   poetry run code-developer --auto-approve
   ```
3. Monitor logs for issues
4. Verify notification created if blocked
5. Check for infinite loops:
   ```bash
   python scripts/check_daemon_health.py
   ```

### Test Error Handling

1. Create invalid ROADMAP:
   ```bash
   cp docs/ROADMAP.md docs/ROADMAP.backup.md
   echo "Invalid content" > docs/ROADMAP.md
   ```
2. Run daemon:
   ```bash
   poetry run code-developer --auto-approve
   ```
3. Verify graceful error handling
4. Restore ROADMAP:
   ```bash
   mv docs/ROADMAP.backup.md docs/ROADMAP.md
   ```

### Test Notification System

1. Run daemon in interactive mode:
   ```bash
   poetry run code-developer  # No --auto-approve
   ```
2. Check notifications:
   ```bash
   poetry run project-manager notifications
   ```
3. Respond to notification:
   ```bash
   poetry run project-manager respond <id> approve
   ```

## Troubleshooting

### Tests Failing

#### Import Errors

```bash
# Ensure dependencies installed
poetry install

# Check Python version
python --version  # Should be 3.11+
```

#### Claude CLI Tests Failing

```bash
# Check if Claude CLI installed
which claude

# Install Claude CLI
brew install claude-ai/claude/claude

# Configure
claude configure
```

#### API Tests Failing

```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Or use .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

#### Database Lock Errors

```bash
# Stop all daemon instances
pkill -f code-developer

# Remove database
rm -f data/notifications.db*

# Restart daemon
poetry run code-developer --auto-approve
```

### Daemon Getting Stuck

#### Check for Infinite Loop

```bash
# Analyze daemon logs
python scripts/check_daemon_health.py

# Check notifications
python scripts/verify_notifications.py

# View daemon logs
tail -f daemon.log  # If logging to file
```

#### Manual Intervention

If daemon stuck on a priority:

1. **Stop daemon**: Ctrl+C or `pkill -f code-developer`
2. **Review priority**: Check ROADMAP.md for vague descriptions
3. **Options**:
   - **Clarify**: Make deliverables more concrete
   - **Manual**: Implement manually and mark complete
   - **Skip**: Mark as "Manual Only" in ROADMAP
4. **Restart daemon**: `poetry run code-developer --auto-approve`

### Notification Issues

#### Notifications Not Created

```bash
# Check database exists
ls -la data/notifications.db

# Check database permissions
chmod 644 data/notifications.db

# Verify schema
sqlite3 data/notifications.db ".schema"
```

#### Cannot Respond to Notifications

```bash
# List notifications
poetry run project-manager notifications

# Respond with correct ID
poetry run project-manager respond <id> approve

# Check response recorded
poetry run project-manager notifications --status responded
```

## Performance Testing

### Measure Test Speed

```bash
# Run with timing
pytest tests/ci_tests/ --durations=10

# Profile slow tests
pytest tests/ci_tests/ --durations=0
```

### Optimize Slow Tests

1. **Use mocks**: Avoid real API calls
2. **Use fixtures**: Reuse test data
3. **Mark slow tests**: `@pytest.mark.slow`
4. **Skip in development**:
   ```bash
   pytest tests/ci_tests/ -m "not slow"
   ```

## Coverage Reporting

### Generate Coverage Report

```bash
# Run with coverage
pytest tests/ --cov=coffee_maker.autonomous --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Goals

- **Overall**: 90%+ coverage
- **Critical paths**: 100% coverage
  - Daemon initialization
  - ROADMAP parsing
  - Retry logic
  - Error handling

## Best Practices

### Writing New Tests

1. **Use descriptive names**:
   ```python
   def test_daemon_creates_notification_on_max_retries(self):
       """Verify notification created when priority attempted too many times."""
   ```

2. **Use fixtures**:
   ```python
   def test_with_temp_roadmap(self, temp_roadmap):
       daemon = DevDaemon(roadmap_path=temp_roadmap)
   ```

3. **Mark appropriately**:
   ```python
   @pytest.mark.integration
   def test_full_workflow(self):
       ...
   ```

4. **Clear assertions**:
   ```python
   assert daemon.max_retries == 3, "Max retries should be 3"
   ```

### Running Tests Efficiently

```bash
# Fast development testing
pytest tests/ci_tests/ -m "not integration" -x  # Stop on first failure

# Full pre-commit testing
pytest tests/ci_tests/ -v

# Pre-release testing
pytest tests/ --cov=coffee_maker.autonomous
```

## Related Documentation

- **CI Test README**: `tests/ci_tests/README.md`
- **Release Checklist**: `docs/RELEASE_CHECKLIST.md`
- **GitHub Workflow**: `.github/workflows/daemon-test.yml`
- **Health Check Script**: `scripts/check_daemon_health.py`
- **Notification Verification**: `scripts/verify_notifications.py`

## Support

For issues with testing:

1. Check this guide first
2. Review test documentation in `tests/ci_tests/README.md`
3. Check GitHub Issues for known problems
4. Create new issue with:
   - Test command used
   - Full error output
   - Environment details (OS, Python version, etc.)
