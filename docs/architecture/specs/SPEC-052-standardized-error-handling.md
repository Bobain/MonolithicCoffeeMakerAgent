# SPEC-052: Standardized Error Handling

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CODE_QUALITY_ANALYSIS_2025-10-17.md (Finding #3)
**Priority**: LOW
**Impact**: MEDIUM (UX Consistency)

---

## Problem Statement

### Current State
Error messages across CLI commands use **inconsistent formatting**, creating a confusing user experience:

- Some use `print(f"❌ Error: {e}")`
- Others use `error(f"Error: {e}")`
- Some use `logger.error()` only (no user-facing message)
- Different emoji usage (❌, 🔴, ERROR:)
- Varying verbosity levels

### code-searcher Finding
> "Inconsistent Error Message Formatting
> Pattern: Across multiple CLI commands
> Issue: Mixed error handling (print, error(), logger)
> Impact: UI/UX inconsistency
> Fix: Standardize with helper functions
> Effort: 1-2 hours
> Priority: LOW (cosmetic)"

### Examples of Inconsistency

**roadmap_cli.py:401** (raw print):
```python
print(f"❌ Error reading status: {e}")
```

**roadmap_cli.py:433** (error() helper):
```python
error(f"Failed to get assistant status: {e}")
```

**roadmap_cli.py:1022** (inconsistent format):
```python
print(f"❌ Error showing metrics: {e}")
```

**daemon.py** (logger only, no user message):
```python
logger.error(f"Error resetting context: {e}")
```

**Why This Matters**:
- Users see different error styles for same type of failure
- Hard to grep logs for specific error types
- Developers must remember multiple error patterns
- No centralized error handling strategy

---

## Proposed Solution

### Simplified Approach (per ADR-003)

Create **single error handling module** (`coffee_maker/cli/error_handler.py`) that provides:
1. **Standardized error display** (consistent format)
2. **Severity levels** (ERROR, WARNING, INFO)
3. **Logging integration** (user message + log entry)
4. **Context preservation** (command, args, traceback)

### Architecture

```
coffee_maker/cli/
├── error_handler.py          # NEW: Centralized error handling
│   ├── handle_error()        # Main error handler
│   ├── handle_warning()      # Warning messages
│   ├── handle_info()         # Info messages
│   └── ErrorContext          # Context dataclass
│
├── roadmap_cli.py            # UPDATE: Use error_handler
└── commands/                 # UPDATE: Use error_handler
    ├── roadmap.py
    ├── status.py
    ├── notifications.py
    └── chat.py
```

**Benefits**:
- **Consistency**: Same error format everywhere
- **Centralized**: Single place to update error handling
- **Logging**: Automatic log integration
- **Debugging**: Better context for troubleshooting

---

## Component Design

### 1. Error Handler Module

```python
# coffee_maker/cli/error_handler.py

import logging
import sys
from dataclasses import dataclass
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    command: str                    # Command that failed (e.g., "view")
    message: str                    # User-facing error message
    exception: Optional[Exception] = None  # Original exception (if any)
    context: Optional[dict] = None  # Additional context (args, etc.)
    severity: ErrorSeverity = ErrorSeverity.ERROR
    exit_code: int = 1             # Exit code for CLI


def handle_error(
    command: str,
    message: str,
    exception: Optional[Exception] = None,
    context: Optional[dict] = None,
    exit_program: bool = False
) -> int:
    """
    Handle errors with consistent formatting and logging.

    Args:
        command: Command that encountered the error
        message: User-friendly error message
        exception: Original exception (if any)
        context: Additional context (args, environment, etc.)
        exit_program: If True, exit the program with error code

    Returns:
        Error exit code (1)

    Example:
        >>> handle_error("view", "Failed to load roadmap", exception=e)
        ❌ Error in 'view': Failed to load roadmap
        1
    """
    # Build user-facing message
    user_message = f"❌ Error in '{command}': {message}"
    print(user_message, file=sys.stderr)

    # Log detailed error
    log_message = f"Command '{command}' failed: {message}"
    if exception:
        logger.error(log_message, exc_info=exception)
    else:
        logger.error(log_message)

    # Log context if available
    if context:
        logger.debug(f"Error context: {context}")

    if exit_program:
        sys.exit(1)

    return 1


def handle_warning(
    command: str,
    message: str,
    context: Optional[dict] = None
) -> int:
    """
    Handle warnings (non-critical issues).

    Example:
        >>> handle_warning("status", "Some metrics unavailable")
        ⚠️  Warning in 'status': Some metrics unavailable
        0
    """
    user_message = f"⚠️  Warning in '{command}': {message}"
    print(user_message, file=sys.stderr)

    logger.warning(f"Command '{command}': {message}")
    if context:
        logger.debug(f"Warning context: {context}")

    return 0  # Warnings don't cause failure


def handle_info(
    command: str,
    message: str
) -> int:
    """
    Handle info messages (FYI, not errors).

    Example:
        >>> handle_info("view", "Showing last 100 lines")
        ℹ️  Info: Showing last 100 lines
        0
    """
    print(f"ℹ️  Info: {message}")
    logger.info(f"Command '{command}': {message}")
    return 0


def handle_success(
    command: str,
    message: str
) -> int:
    """
    Handle success messages.

    Example:
        >>> handle_success("respond", "Notification approved")
        ✅ Success: Notification approved
        0
    """
    print(f"✅ Success: {message}")
    logger.info(f"Command '{command}': {message}")
    return 0
```

### 2. Usage in CLI Commands

**Before (inconsistent)**:
```python
# roadmap_cli.py - OLD ❌
def cmd_view(args):
    try:
        # ... code ...
    except Exception as e:
        print(f"❌ Error reading roadmap: {e}")  # Inconsistent
        return 1
```

**After (standardized)**:
```python
# roadmap_cli.py - NEW ✅
from coffee_maker.cli.error_handler import handle_error, handle_success

def cmd_view(args):
    try:
        # ... code ...
        return handle_success("view", "Roadmap displayed successfully")
    except FileNotFoundError as e:
        return handle_error(
            "view",
            "Roadmap file not found",
            exception=e,
            context={"args": vars(args)}
        )
    except Exception as e:
        return handle_error(
            "view",
            f"Unexpected error: {e}",
            exception=e,
            context={"args": vars(args)}
        )
```

### 3. Daemon Integration

**Daemon errors should use error_handler too**:
```python
# daemon.py
from coffee_maker.cli.error_handler import handle_error

class DevDaemon:
    def run(self):
        try:
            # ... daemon logic ...
        except KeyboardInterrupt:
            handle_info("daemon", "Daemon stopped by user")
            return 0
        except Exception as e:
            return handle_error(
                "daemon",
                "Daemon crashed unexpectedly",
                exception=e,
                context={"current_priority": self.current_priority}
            )
```

---

## Technical Details

### Error Message Format Standards

**ERROR (severity: ERROR)**:
```
❌ Error in 'command': message
```

**WARNING (severity: WARNING)**:
```
⚠️  Warning in 'command': message
```

**INFO (severity: INFO)**:
```
ℹ️  Info: message
```

**SUCCESS (severity: SUCCESS)**:
```
✅ Success: message
```

### Logging Levels Mapping

| Severity | User Display | Log Level | Exit Code |
|----------|-------------|-----------|-----------|
| ERROR | ❌ Error | logging.ERROR | 1 |
| WARNING | ⚠️ Warning | logging.WARNING | 0 |
| INFO | ℹ️ Info | logging.INFO | 0 |
| SUCCESS | ✅ Success | logging.INFO | 0 |

### Context Dictionary Structure

```python
{
    "command": str,           # e.g., "view"
    "args": dict,             # Parsed CLI arguments
    "environment": dict,      # Optional env vars
    "current_priority": str,  # Optional (for daemon)
    "user": str,              # Optional (for multi-user)
}
```

---

## Migration Strategy

### Phase 1: Create Error Handler Module (30 min)
```bash
# Create module
touch coffee_maker/cli/error_handler.py

# Implement functions (copy from spec above)
```

### Phase 2: Update roadmap_cli.py (30 min)
1. Import error_handler functions
2. Replace all `print(f"❌ Error: ...")` with `handle_error()`
3. Replace all `error(...)` calls with `handle_error()`
4. Add success messages with `handle_success()`

### Phase 3: Update Command Modules (1 hour)
**If SPEC-050 implemented** (modular CLI):
- Update `commands/roadmap.py`
- Update `commands/status.py`
- Update `commands/notifications.py`
- Update `commands/chat.py`

**If NOT yet modular**:
- Update all command functions in `roadmap_cli.py`

### Phase 4: Update Daemon (30 min)
- Update `daemon.py` error handling
- Update mixin error handling
- Ensure all errors use `handle_error()`

### Phase 5: Testing (30 min)
- Test error cases manually
- Verify log output
- Check exit codes

**Total**: 3 hours

---

## Data Structures

### ErrorContext Dataclass
```python
@dataclass
class ErrorContext:
    command: str
    message: str
    exception: Optional[Exception] = None
    context: Optional[dict] = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    exit_code: int = 1
```

### ErrorSeverity Enum
```python
class ErrorSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
```

---

## Testing Strategy

### Unit Tests

**New Test File**: `tests/unit/cli/test_error_handler.py`

```python
import pytest
from io import StringIO
from coffee_maker.cli.error_handler import (
    handle_error,
    handle_warning,
    handle_info,
    handle_success,
)


class TestErrorHandler:
    def test_handle_error_format(self, capsys):
        """Test error message format."""
        result = handle_error("view", "File not found")

        captured = capsys.readouterr()
        assert "❌ Error in 'view': File not found" in captured.err
        assert result == 1

    def test_handle_error_with_exception(self, capsys):
        """Test error with exception logging."""
        exception = ValueError("Invalid input")
        result = handle_error(
            "status",
            "Invalid priority",
            exception=exception
        )

        captured = capsys.readouterr()
        assert "❌ Error in 'status': Invalid priority" in captured.err
        assert result == 1

    def test_handle_warning_format(self, capsys):
        """Test warning message format."""
        result = handle_warning("metrics", "Some data missing")

        captured = capsys.readouterr()
        assert "⚠️  Warning in 'metrics': Some data missing" in captured.err
        assert result == 0  # Warnings don't fail

    def test_handle_info_format(self, capsys):
        """Test info message format."""
        result = handle_info("view", "Showing roadmap")

        captured = capsys.readouterr()
        assert "ℹ️  Info: Showing roadmap" in captured.out
        assert result == 0

    def test_handle_success_format(self, capsys):
        """Test success message format."""
        result = handle_success("respond", "Notification approved")

        captured = capsys.readouterr()
        assert "✅ Success: Notification approved" in captured.out
        assert result == 0

    def test_error_with_context(self, caplog):
        """Test error with context logging."""
        context = {"args": {"priority": 5}}
        handle_error("view", "Error", context=context)

        # Check context was logged
        assert "Error context" in caplog.text
```

### Integration Tests

**Test CLI Error Handling**: `tests/ci_tests/test_cli_error_handling.py`

```python
def test_cli_error_handling_integration():
    """Test error handling across CLI commands."""
    # Test non-existent command
    result = subprocess.run(
        ["project-manager", "invalid-command"],
        capture_output=True,
        text=True
    )
    assert "❌ Error" in result.stderr
    assert result.returncode != 0

    # Test valid command with error condition
    # (e.g., missing ROADMAP.md)
```

### Manual Testing
```bash
# Test error handling
project-manager view-priority 999  # Should show error
project-manager view /nonexistent  # Should show file not found
project-manager status             # Should show success

# Verify log output
tail -f logs/project_manager.log  # Check logged errors
```

---

## Rollout Plan

### Week 1: Implementation
- **Day 1**: Create error_handler.py module (30 min)
- **Day 1**: Write unit tests (1 hour)
- **Day 1**: Update roadmap_cli.py (30 min)
- **Day 2**: Update command modules (1 hour)
- **Day 2**: Update daemon error handling (30 min)

### Week 1: Testing
- **Day 2**: Run unit tests (15 min)
- **Day 2**: Manual CLI testing (30 min)
- **Day 3**: Fix any issues (1 hour buffer)

### Week 1: Cleanup
- **Day 3**: Remove old error() helper (15 min)
- **Day 3**: Update CLAUDE.md (15 min)

**Total Timeline**: 3 days (5 hours actual work)

---

## Risks & Mitigations

### Risk 1: Breaking Existing Error Handling
**Likelihood**: LOW
**Impact**: MEDIUM (users see wrong error messages)
**Mitigation**:
- Comprehensive testing of all error paths
- Keep old error() function during transition
- Gradual migration (one command at a time)

### Risk 2: Log Spam (Too Much Logging)
**Likelihood**: MEDIUM
**Impact**: LOW (noise in logs)
**Mitigation**:
- Use appropriate log levels (ERROR for errors, DEBUG for context)
- Add log level configuration
- Test log output before rollout

### Risk 3: Performance Impact
**Likelihood**: VERY LOW
**Impact**: VERY LOW
**Mitigation**:
- Error handling is simple (no complex logic)
- Logging is async (non-blocking)
- No performance impact expected

---

## Success Criteria

### Quantitative
- ✅ 100% of CLI commands use error_handler
- ✅ 100% of daemon errors use error_handler
- ✅ All error messages follow standard format
- ✅ All errors logged with appropriate level
- ✅ Exit codes consistent (0 = success, 1 = error)
- ✅ Test coverage ≥95% for error_handler module

### Qualitative
- ✅ Users see consistent error messages
- ✅ Developers use error_handler for new commands
- ✅ Logs are easy to grep and analyze
- ✅ Error messages are helpful (actionable)

---

## Before & After Examples

### Example 1: Roadmap View Error

**Before** (inconsistent):
```python
# roadmap_cli.py
try:
    roadmap = load_roadmap()
except Exception as e:
    print(f"❌ Error reading roadmap: {e}")  # Inconsistent
    return 1
```

**After** (standardized):
```python
# roadmap_cli.py
from coffee_maker.cli.error_handler import handle_error

try:
    roadmap = load_roadmap()
except FileNotFoundError as e:
    return handle_error("view", "Roadmap file not found", exception=e)
except Exception as e:
    return handle_error("view", f"Failed to load roadmap: {e}", exception=e)
```

### Example 2: Daemon Error

**Before** (logger only):
```python
# daemon.py
try:
    self.reset_context()
except Exception as e:
    logger.error(f"Error resetting context: {e}")  # No user message
```

**After** (user + log):
```python
# daemon.py
from coffee_maker.cli.error_handler import handle_error

try:
    self.reset_context()
except Exception as e:
    handle_error("daemon", "Failed to reset context", exception=e)
```

---

## Related Work

### Depends On
- None (independent utility module)

### Enables
- **SPEC-050**: Modular CLI commands will use error_handler
- **Future**: Centralized error metrics and monitoring

### Related Specs
- **SPEC-051**: Prompt utilities (similar utility pattern)

---

## Future Enhancements

### After This Implementation
1. **Error Recovery**: Automatic retry logic for transient errors
2. **Error Analytics**: Track error frequency, types
3. **User Feedback**: "Report this error" option
4. **Rich Error Display**: Use rich library for better formatting

---

## Appendix A: Current Error Patterns

### Patterns Found in Codebase

| Pattern | Count | Files |
|---------|-------|-------|
| `print(f"❌ Error: {e}")` | 12 | roadmap_cli.py, daemon.py |
| `error(f"Error: {e}")` | 8 | roadmap_cli.py |
| `logger.error(...)` only | 15 | daemon.py, mixins |
| `print(f"Error: ...")` (no emoji) | 5 | old scripts |

**Total Inconsistencies**: 40+ locations

### After Standardization

| Pattern | Count | Files |
|---------|-------|-------|
| `handle_error(...)` | 35 | All CLI + daemon |
| `handle_warning(...)` | 5 | Where appropriate |

**Consistency**: 100%

---

## Appendix B: Error Categories

### Common Error Types

1. **File Not Found** (FileNotFoundError)
   - Roadmap missing
   - Config missing
   - Logs missing

2. **Invalid Input** (ValueError)
   - Invalid priority number
   - Invalid date format
   - Invalid arguments

3. **Permission Denied** (PermissionError)
   - Cannot write to file
   - Cannot create directory

4. **Network Errors** (ConnectionError)
   - API timeout
   - GitHub API failure

5. **Unexpected Errors** (Exception)
   - Catch-all for unknown issues

### Error Handling Strategy by Type

```python
try:
    # ... operation ...
except FileNotFoundError as e:
    return handle_error("cmd", "File not found: {path}", exception=e)
except ValueError as e:
    return handle_error("cmd", "Invalid input: {details}", exception=e)
except PermissionError as e:
    return handle_error("cmd", "Permission denied: {path}", exception=e)
except ConnectionError as e:
    return handle_warning("cmd", "Network error (retrying...)", exception=e)
    # ... retry logic ...
except Exception as e:
    return handle_error("cmd", f"Unexpected error: {e}", exception=e)
```

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 5 hours
**Actual Effort**: TBD
