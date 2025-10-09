"""End-to-end tests for the Coffee Maker Agent.

This package contains E2E tests that validate the full autonomous development workflow.

⚠️ WARNING: E2E tests perform REAL operations:
- Create real Git branches
- Execute real Claude CLI commands
- Make real commits
- Push to real remote repository
- Create real pull requests

Only run E2E tests when you want to validate the full system end-to-end.

Usage:
    # Run E2E tests with explicit flag
    pytest tests/e2e/ -v -s --run-e2e

    # Or enable via environment variable
    export DAEMON_E2E_TEST=1
    pytest tests/e2e/ -v -s

    # Run full implementation test (creates real PRs!)
    export DAEMON_E2E_FULL=1
    pytest tests/e2e/test_daemon_e2e.py::TestDaemonE2EFull::test_daemon_full_implementation -v -s
"""
