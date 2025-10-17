# SPEC-061: Daemon CLI Mode Detection Testing

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: code-searcher refactoring_priorities_2025-10-17.md (Priority 3.3)
**Priority**: LOW
**Impact**: MEDIUM (Daemon Reliability)

---

## Problem Statement

### Current State
Daemon CLI mode detection (`daemon_cli.py`) has basic tests but misses:
- CLI detection when installed/not installed
- API key validation scenarios
- Auto-approval flag handling edge cases
- Startup error conditions

### code-searcher Finding
> **Test Coverage Gaps: Daemon CLI**
> - Location: `coffee_maker/autonomous/daemon_cli.py`
> - Missing Coverage: Mode detection, validation, error conditions
> - Effort: 5 hours
> - Impact: MEDIUM (more robust daemon startup)

### Why This Matters
- Wrong mode selection crashes daemon
- Missing API keys cause cryptic errors
- Auto-approval failures are hard to debug
- Startup errors confuse users

---

## Proposed Solution

Add targeted tests for daemon CLI:

1. **Mode Detection** (3 tests)
   - Detect Claude CLI when installed
   - Detect API mode when CLI not installed
   - Handle ambiguous situations

2. **Validation** (3 tests)
   - API key presence validation
   - Claude CLI path validation
   - Configuration file validation

3. **Auto-Approval** (2 tests)
   - Auto-approval flag handling
   - Interactive mode validation

4. **Error Conditions** (3 tests)
   - Missing API key error
   - CLI not found error
   - Invalid configuration error

---

## Component Design

### New Test File

**`tests/unit/autonomous/test_daemon_cli.py`**:

```python
class TestDaemonModeDetection:
    """Test daemon mode detection logic."""

    @patch('shutil.which')
    def test_detect_cli_when_installed(self, mock_which):
        """Test detects Claude CLI when installed."""
        mock_which.return_value = "/usr/local/bin/claude"

        mode = detect_claude_mode()

        assert mode == "cli"
        assert get_claude_path() == "/usr/local/bin/claude"

    @patch('shutil.which')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_detect_api_when_cli_not_installed(self, mock_which):
        """Test falls back to API mode when CLI not installed."""
        mock_which.return_value = None

        mode = detect_claude_mode()

        assert mode == "api"

    @patch('shutil.which')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''})
    def test_error_when_no_cli_and_no_api_key(self, mock_which):
        """Test error when neither CLI nor API key available."""
        mock_which.return_value = None

        with pytest.raises(ValueError) as exc_info:
            detect_claude_mode()

        assert "No Claude CLI found" in str(exc_info.value)
        assert "ANTHROPIC_API_KEY" in str(exc_info.value)


class TestDaemonValidation:
    """Test daemon configuration validation."""

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_validate_api_key_present(self):
        """Test validation passes when API key present."""
        result = validate_api_key()

        assert result is True

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''})
    def test_validate_api_key_missing(self):
        """Test validation fails when API key missing."""
        with pytest.raises(ValueError):
            validate_api_key()

    @patch('pathlib.Path.exists')
    def test_validate_claude_cli_path(self, mock_exists):
        """Test Claude CLI path validation."""
        mock_exists.return_value = True

        result = validate_claude_cli_path("/usr/local/bin/claude")

        assert result is True

    @patch('pathlib.Path.exists')
    def test_validate_invalid_cli_path(self, mock_exists):
        """Test error for invalid Claude CLI path."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            validate_claude_cli_path("/nonexistent/claude")

    def test_validate_config_file(self, tmp_path):
        """Test configuration file validation."""
        config_file = tmp_path / ".env"
        config_file.write_text("ANTHROPIC_API_KEY=test")

        result = validate_config_file(config_file)

        assert result is True


class TestAutoApprovalHandling:
    """Test auto-approval flag handling."""

    def test_auto_approve_flag_enabled(self):
        """Test daemon runs with auto-approve enabled."""
        daemon = DevDaemon(auto_approve=True)

        assert daemon.auto_approve is True
        assert daemon.requires_user_input() is False

    def test_auto_approve_flag_disabled(self):
        """Test daemon requires input with auto-approve disabled."""
        daemon = DevDaemon(auto_approve=False)

        assert daemon.auto_approve is False
        assert daemon.requires_user_input() is True

    def test_interactive_mode_validation(self):
        """Test interactive mode requires terminal."""
        daemon = DevDaemon(auto_approve=False)

        if not sys.stdin.isatty():
            with pytest.raises(RuntimeError):
                daemon.start()


class TestDaemonErrorConditions:
    """Test daemon startup error conditions."""

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''})
    def test_missing_api_key_error(self):
        """Test error message for missing API key."""
        with pytest.raises(ValueError) as exc_info:
            DevDaemon(mode="api")

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)
        assert "environment variable" in str(exc_info.value)

    @patch('shutil.which', return_value=None)
    def test_cli_not_found_error(self, mock_which):
        """Test error message when CLI not found."""
        with pytest.raises(FileNotFoundError) as exc_info:
            DevDaemon(mode="cli")

        assert "Claude CLI" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_invalid_configuration_error(self, tmp_path):
        """Test error for invalid configuration file."""
        config_file = tmp_path / ".env"
        config_file.write_text("INVALID SYNTAX")

        with pytest.raises(ValueError):
            DevDaemon(config_file=config_file)
```

---

## Technical Details

### Test Coverage Goals
- Mode detection: 100%
- Validation: 100%
- Auto-approval: 95%
- Error handling: 90%

### Mock Infrastructure
```python
@pytest.fixture
def mock_daemon_env(monkeypatch):
    """Mock daemon environment for testing."""
    monkeypatch.setenv('ANTHROPIC_API_KEY', 'test-key')
    monkeypatch.setattr('shutil.which', lambda x: '/usr/local/bin/claude')
```

---

## Rollout Plan

### Week 1: Implementation (5 hours)
- **Day 1**: Mode detection tests (2 hours)
- **Day 2**: Validation tests (1.5 hours)
- **Day 3**: Auto-approval + error tests (1.5 hours)

---

## Success Criteria

### Quantitative
- ✅ 11 new tests added
- ✅ Daemon CLI coverage ≥90%
- ✅ All error scenarios tested
- ✅ Mode detection verified

### Qualitative
- ✅ More robust daemon startup
- ✅ Clear error messages
- ✅ Easier to debug mode issues

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 5 hours
**Actual Effort**: TBD
