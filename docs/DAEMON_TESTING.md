# Daemon Testing Guide

Comprehensive guide for testing the `code_developer` autonomous daemon.

## 🎯 Overview

This guide covers:
- **CI Testing**: Automated tests via GitHub Actions
- **Manual Testing**: Local testing procedures
- **Integration Testing**: End-to-end workflows
- **Troubleshooting**: Common issues and solutions

## 🏃 Quick Start

### Run All Tests
```bash
# Fast tests only (smoke + unit)
pytest tests/ci_tests/ -v

# Include integration tests
pytest tests/ci_tests/ -v --run-e2e

# Run specific test file
pytest tests/ci_tests/test_daemon_smoke.py -v
```

### Run Health Checks
```bash
# Check daemon health from logs
python scripts/check_daemon_health.py

# Verify notification system
python scripts/verify_notifications.py
```

## 📋 Test Categories

### 1. Smoke Tests (Fast - <1 minute)
**Purpose**: Catch obvious breakage quickly

```bash
pytest tests/ci_tests/test_daemon_smoke.py -v -m smoke
```

**What they test**:
- ✅ All modules import successfully
- ✅ Daemon can be initialized
- ✅ ROADMAP parser works
- ✅ Git manager initializes
- ✅ Both CLI and API modes initialize

**When to run**: After every code change, before committing

### 2. Unit Tests (Medium - 2-5 minutes)
**Purpose**: Test individual components

```bash
pytest tests/ci_tests/ -v -m "not integration and not slow"
```

**What they test**:
- ✅ ROADMAP parsing with various formats
- ✅ Status detection (Complete, Planned, Blocked)
- ✅ Error handling (missing files, invalid input)
- ✅ Configuration options
- ✅ Git operations

**When to run**: Before opening PRs

### 3. Integration Tests (Slow - 10-30 minutes)
**Purpose**: Test complete workflows end-to-end

```bash
pytest tests/ci_tests/ -v -m integration --run-e2e
```

**Requirements**:
- Claude CLI installed OR ANTHROPIC_API_KEY set
- Git repository initialized
- Network access

**What they test**:
- ✅ Full daemon cycle: parse → execute → commit → PR
- ✅ Claude CLI execution
- ✅ Anthropic API calls
- ✅ Multi-priority workflows
- ✅ Notification system

**When to run**: Before releases, after major changes

### 4. Non-Regression Tests (Medium - 5 minutes)
**Purpose**: Ensure no regressions in critical functionality

```bash
pytest tests/autonomous/test_daemon_regression.py -v
```

**What they test**:
- ✅ Backward compatibility
- ✅ Critical user scenarios still work
- ✅ Default values unchanged
- ✅ Core APIs stable

**When to run**: Before every release

## 🤖 CI Testing (Automated)

### GitHub Actions Integration

Tests run automatically on:

#### 1. **Pull Requests to Main**
```yaml
# Triggers: When PR opened/updated
# Tests: Smoke + Unit tests
# Duration: ~5-10 minutes
```

**What runs**:
- Smoke tests (fast validation)
- Unit tests (core functionality)
- Health checks
- No integration tests (to stay fast)

**How to trigger**:
```bash
# Create PR
gh pr create --base main --head feature/my-feature

# Tests run automatically
# Check status in PR
```

#### 2. **Releases**
```yaml
# Triggers: When release published
# Tests: All tests including integration
# Duration: ~15-30 minutes
```

**What runs**:
- All smoke tests
- All unit tests
- Integration tests
- Non-regression tests
- Daemon health checks
- Test coverage report

**How to trigger**:
```bash
# Create and push tag
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Create release on GitHub
gh release create v1.2.0
```

#### 3. **Manual Dispatch**
```yaml
# Triggers: Manual workflow run
# Tests: Customizable test suite
# Duration: Varies
```

**How to trigger**:
```bash
# Via GitHub UI: Actions → Daemon CI Tests → Run workflow

# Or via gh CLI:
gh workflow run daemon-test.yml
```

### Viewing CI Results

```bash
# List recent workflow runs
gh run list --workflow=daemon-test.yml

# View specific run
gh run view <run-id>

# Download logs
gh run download <run-id>
```

## 🖥️ Local Testing

### Prerequisites

1. **Install dependencies**:
```bash
poetry install
```

2. **Optional: Install Claude CLI** (for CLI mode tests):
```bash
brew install anthropics/claude/claude
```

3. **Optional: Set API key** (for API mode tests):
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Test Execution

#### Run Specific Test Categories
```bash
# Smoke tests only
pytest tests/ci_tests/test_daemon_smoke.py -v

# ROADMAP parsing tests
pytest tests/ci_tests/test_roadmap_parsing.py -v

# Error handling tests
pytest tests/ci_tests/test_error_handling.py -v

# User scenario tests
pytest tests/ci_tests/test_daemon_user_scenarios.py -v

# CLI mode tests (requires Claude CLI)
pytest tests/ci_tests/test_daemon_cli_mode.py -v

# API mode tests (requires API key)
pytest tests/ci_tests/test_daemon_api_mode.py -v
```

#### Run with Options
```bash
# Verbose output
pytest tests/ci_tests/ -v -s

# Stop on first failure
pytest tests/ci_tests/ -x

# Run specific test
pytest tests/ci_tests/test_daemon_smoke.py::TestDaemonSmoke::test_daemon_imports_successfully

# Show slowest tests
pytest tests/ci_tests/ --durations=10

# Run with coverage
pytest tests/ci_tests/ --cov=coffee_maker.autonomous --cov-report=html
```

## 🔍 Integration Testing

Integration tests require actual Claude CLI or API access.

### CLI Mode Integration Test

```bash
# Ensure Claude CLI is installed
which claude

# Run CLI integration tests
pytest tests/ci_tests/test_daemon_cli_mode.py -v -m integration --run-e2e
```

**What it tests**:
1. Claude CLI execution
2. Prompt processing
3. Code generation
4. Timeout handling

### API Mode Integration Test

```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run API integration tests
pytest tests/ci_tests/test_daemon_api_mode.py -v -m integration --run-e2e
```

**What it tests**:
1. API client initialization
2. API calls
3. Response handling
4. Error handling

### Full E2E Test (Manual)

**Important**: Run in a **separate terminal** (not in Claude Code session).

```bash
# Terminal 1: Start daemon
cd /path/to/MonolithicCoffeeMakerAgent
poetry run code-developer --verbose --no-pr

# Expected behavior:
# 1. ✅ Initializes successfully
# 2. ✅ Finds next planned priority
# 3. ✅ Creates notification (if not auto-approve)
# 4. ✅ Waits or proceeds

# Terminal 2: Check notifications
poetry run project-manager notifications

# Terminal 2: Approve (if needed)
poetry run project-manager respond <ID> approve

# Terminal 1: Watch execution
# Should see:
# - Claude CLI execution
# - File changes
# - Git commit
# - Success message
```

## 🛠️ Health Checks

### Daemon Health Check

Analyzes logs for issues:

```bash
# Check default log location
python scripts/check_daemon_health.py

# Check custom log file
python scripts/check_daemon_health.py --log-file /path/to/daemon.log

# Read from stdin
tail -f daemon.log | python scripts/check_daemon_health.py --stdin
```

**Detects**:
- ❌ Infinite loops (priority attempted >3 times)
- ⚠️ Repeated errors
- ⚠️ No progress (daemon stuck)
- ⚠️ Performance issues (timeouts)

**Example output**:
```
====================================
DAEMON HEALTH CHECK RESULTS
====================================

✅ HEALTHY: No critical issues detected

✅ No infinite loops detected
   Attempts per priority:
   - PRIORITY 2.5: 1 attempt(s)
   - PRIORITY 2.6: 1 attempt(s)

✅ No repeated errors

✅ Daemon is making progress

✅ No performance issues
```

### Notification System Check

Verifies notification database:

```bash
# Check default database
python scripts/verify_notifications.py

# Check custom database
python scripts/verify_notifications.py --db-path /path/to/notifications.db
```

**Verifies**:
- ✅ Database exists
- ✅ Can connect to database
- ✅ Notifications table exists
- ✅ Can create notifications
- ✅ Can retrieve notifications

**Example output**:
```
====================================
NOTIFICATION SYSTEM VERIFICATION
====================================

Database: data/notifications.db
Exists: ✅

Verification Checks:
  ✅ Can Import
  ✅ Can Connect
  ✅ Has Notifications Table
  ✅ Can Create
  ✅ Can Retrieve

Pending Notifications: 2

====================================
✅ VERIFICATION PASSED
====================================
```

## 📊 Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest tests/ci_tests/ \
  --cov=coffee_maker.autonomous \
  --cov-report=html \
  --cov-report=term

# Open report
open htmlcov/index.html
```

### Coverage Goals

- **Smoke tests**: N/A (integration, not coverage)
- **Unit tests**: >70% line coverage
- **Critical paths**: >90% coverage
  - Daemon initialization
  - ROADMAP parsing
  - Error handling

## 🐛 Troubleshooting

### Tests Failing

#### "Claude CLI not found"
```bash
# Solution 1: Install Claude CLI
brew install anthropics/claude/claude

# Solution 2: Skip CLI tests
pytest tests/ci_tests/ -v -m "not integration"

# Solution 3: Set custom path
export CLAUDE_CLI_PATH=/path/to/claude
```

#### "API key not found"
```bash
# Solution: Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Or skip API tests
pytest tests/ci_tests/ -v -m "not integration"
```

#### "Tests hang or timeout"
```bash
# Solution 1: Increase timeout
pytest tests/ci_tests/ --timeout=300

# Solution 2: Skip slow tests
pytest tests/ci_tests/ -v -m "not slow"

# Solution 3: Run with -s to see output
pytest tests/ci_tests/ -v -s
```

#### "Import errors"
```bash
# Solution: Reinstall dependencies
poetry install --no-cache
```

### Tests Pass Locally, Fail in CI

**Common causes**:
1. **Environment differences**: CI uses Ubuntu, you use macOS
2. **Missing dependencies**: Check `pyproject.toml`
3. **Git state**: CI uses clean repo
4. **Timing issues**: CI might be slower

**Solutions**:
```bash
# Run tests in Docker (matches CI)
docker run -it python:3.11 bash
cd /app
poetry install
pytest tests/ci_tests/ -v

# Check CI logs for details
gh run view <run-id> --log
```

### Integration Tests Fail

**Common causes**:
1. **Running inside Claude Code session**: Resource conflict
2. **Network issues**: API unreachable
3. **Rate limiting**: Too many API calls

**Solutions**:
```bash
# Run in separate terminal (NOT in Claude Code)
# Open fresh terminal:
cd /path/to/project
poetry run pytest tests/ci_tests/ -v --run-e2e

# Check network
curl https://api.anthropic.com/v1/health

# Wait between test runs (rate limiting)
sleep 60 && pytest ...
```

## 📚 Testing Best Practices

### Before Committing
```bash
# 1. Run smoke tests
pytest tests/ci_tests/test_daemon_smoke.py -v

# 2. Run affected tests
pytest tests/ci_tests/test_<related>.py -v

# 3. Run health checks
python scripts/check_daemon_health.py
```

### Before Opening PR
```bash
# 1. Run all unit tests
pytest tests/ci_tests/ -v -m "not integration"

# 2. Run non-regression tests
pytest tests/autonomous/test_daemon_regression.py -v

# 3. Verify coverage
pytest tests/ci_tests/ --cov=coffee_maker.autonomous --cov-report=term

# 4. Check CI will pass
# All above must pass before PR
```

### Before Release
```bash
# 1. Run ALL tests
pytest tests/ -v --run-e2e

# 2. Manual E2E test
poetry run code-developer --verbose

# 3. Health checks
python scripts/check_daemon_health.py
python scripts/verify_notifications.py

# 4. Follow RELEASE_CHECKLIST.md
```

## 🔗 Related Documentation

- [Release Checklist](RELEASE_CHECKLIST.md) - Pre-release testing procedures
- [CI Tests README](../tests/ci_tests/README.md) - Detailed test documentation
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Contributing Guide](CONTRIBUTING.md) - How to contribute tests

## 🎓 Writing New Tests

When adding new daemon functionality:

### 1. Add Smoke Test
```python
# tests/ci_tests/test_daemon_smoke.py
def test_new_feature_initializes(self):
    """Verify new feature can be initialized."""
    assert NewFeature() is not None
```

### 2. Add Unit Tests
```python
# tests/ci_tests/test_new_feature.py
class TestNewFeature:
    def test_basic_functionality(self):
        """Test basic use case."""
        feature = NewFeature()
        result = feature.do_something()
        assert result == expected
```

### 3. Add Integration Test (if needed)
```python
# tests/ci_tests/test_daemon_integration.py
@pytest.mark.integration
def test_new_feature_e2e(self):
    """Test new feature end-to-end."""
    pytest.skip("Requires full setup")
```

### 4. Update CI Workflow (if needed)
```yaml
# .github/workflows/daemon-test.yml
- name: Test new feature
  run: pytest tests/ci_tests/test_new_feature.py -v
```

## 💡 Tips

- ✅ **Run tests frequently**: Catch issues early
- ✅ **Use markers**: Skip slow tests during development
- ✅ **Check coverage**: Ensure new code is tested
- ✅ **Test edge cases**: Empty inputs, errors, etc.
- ✅ **Use fixtures**: Share test setup via conftest.py
- ✅ **Mock external services**: Don't depend on API in unit tests
- ✅ **Keep tests fast**: Slow tests won't be run
- ✅ **Document test purpose**: Clear docstrings

---

**Questions or issues?** Open an issue on GitHub or check [Troubleshooting Guide](TROUBLESHOOTING.md).
