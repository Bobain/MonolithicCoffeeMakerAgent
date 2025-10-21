# Manual Tests - On-Demand Testing Only

**⚠️ These tests are NOT run automatically in CI/CD pipelines.**

This directory contains tests that require manual execution because they:
- Make real API calls to Claude CLI
- Create real Git branches and commits
- Push to remote repositories
- Create pull requests
- Modify system state
- Take significant time to run
- May incur costs (API usage)

## Tests in This Directory

### `test_daemon_api_mode_smoke.py`
Smoke tests for daemon in API mode (requires ANTHROPIC_API_KEY):
- DevDaemon initialization with API mode
- ClaudeAPI instance creation
- API key validation

**Run with:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
pytest manual_tests/test_daemon_api_mode_smoke.py -v
```

### `test_daemon_cli_mode.py`
Tests for daemon in Claude CLI mode (requires Claude CLI installed):
- ClaudeCLIInterface initialization and configuration
- Claude CLI availability checks
- Command execution and timeout handling
- Integration tests with real Claude CLI calls

**Run with:**
```bash
# Requires: brew install claude (or equivalent)
pytest manual_tests/test_daemon_cli_mode.py -v
```

### `test_daemon_integration.py`
Integration tests for the autonomous daemon components:
- RoadmapParser with real ROADMAP.md
- ClaudeCLIInterface availability checks
- GitManager operations
- Component integration

**Run with:**
```bash
pytest manual_tests/test_daemon_integration.py -v
```

### `test_daemon_e2e.py`
Full end-to-end tests for the daemon workflow:
- Complete implementation cycle
- Real branch creation
- Real Claude CLI execution
- Real commits and pushes
- Real PR creation

**Run with:**
```bash
# Basic E2E tests (safe)
pytest manual_tests/test_daemon_e2e.py -v -s --run-e2e

# Full E2E tests (creates real branches/commits)
export DAEMON_E2E_FULL=1
pytest manual_tests/test_daemon_e2e.py::TestDaemonE2EFull::test_daemon_full_implementation -v -s
```

## When to Run These Tests

### Before Deployment
Run these tests before deploying daemon changes to production:
```bash
# Run all manual tests
pytest manual_tests/ -v -s --run-e2e
```

### After Major Changes
Run after significant changes to:
- Daemon implementation
- Claude CLI integration
- Git operations
- Roadmap parsing

### User Acceptance Testing
Run when validating the full autonomous workflow with real data.

## Prerequisites

Before running these tests, ensure:

1. ✅ **ANTHROPIC_API_KEY** set in environment (for API mode tests)
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   # Or add to .env file
   ```

2. ✅ **Claude CLI** installed and authenticated (for CLI mode tests)
   ```bash
   claude --version
   ```

3. ✅ **gh CLI** installed and authenticated (for E2E tests)
   ```bash
   gh auth status
   ```

4. ✅ **Git remote** configured
   ```bash
   git remote -v
   ```

4. ✅ **Not on main/master** branch (for safety)
   ```bash
   git checkout -b test/manual-testing
   ```

## CI/CD Exclusion

These tests are excluded from CI/CD because:

1. **Cost**: Claude CLI usage consumes subscription/API credits
2. **Time**: E2E tests can take 5-30 minutes
3. **Side Effects**: Create real Git branches, commits, PRs
4. **External Dependencies**: Require Claude CLI, gh CLI authentication
5. **Triggered by Daemon**: These tests run every time code_developer ships code

The CI pipeline only runs:
- `tests/unit/` - Fast, isolated unit tests
- `tests/ci_tests/` - Safe integration tests with mocks

## Running Individual Tests

```bash
# Test daemon initialization only
pytest manual_tests/test_daemon_e2e.py::TestDaemonE2EFull::test_daemon_initialization -v

# Test roadmap parsing only
pytest manual_tests/test_daemon_integration.py::TestRoadmapParserIntegration::test_parse_real_roadmap -v

# Test Claude CLI availability
pytest manual_tests/test_daemon_integration.py::TestClaudeCLIIntegration::test_check_availability_real -v
```

## Safety Notes

⚠️ **Always run on a feature branch, never on main/master**

⚠️ **E2E tests create real commits - review before merging**

⚠️ **Full E2E tests can create PRs - monitor GitHub**

⚠️ **Tests may consume Claude API credits**

## Troubleshooting

### Tests Fail: "Claude CLI not available"
```bash
# Install Claude CLI
brew install claude

# Verify
claude --version
```

### Tests Fail: "gh CLI not authenticated"
```bash
# Login to GitHub
gh auth login

# Verify
gh auth status
```

### Tests Fail: "Cannot run on main branch"
```bash
# Switch to feature branch
git checkout -b test/manual-testing
```

---

**Last Updated**: October 21, 2025
**Location**: `/manual_tests/` (outside `tests/` directory)
**Previous Location**: `tests/manual_tests/` → Moved to root level to prevent accidental CI execution
**Reason**: Exclude from CI - run only on user demand
