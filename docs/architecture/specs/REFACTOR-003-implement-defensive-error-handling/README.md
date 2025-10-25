# REFACTOR-003: Implement Defensive Error Handling

## Overview

# REFACTOR-003: Implement Defensive Error Handling

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-16
**Priority**: 🔴 CRITICAL
**Estimated Effort**: 10-15 hours
**Expected Value**: ⭐⭐⭐⭐⭐ (very high)
**ROI**: 5.0 (highest)

---

## Problem Statement

### Current State

The codebase has **insufficient error handling** in critical paths, leading to daemon crashes, data loss, and difficult-to-debug failures.

**Critical Issues**:

1. **File I/O without validation** (15+ locations)
```python
# In status_report_generator.py, line 162
content = self.roadmap_path.read_text()  # ❌ No error handling!
```

2. **Network calls without retry** (8+ locations)
```python
# In claude_api_interface.py
response = self.client.messages.create(...)  # ❌ No retry on transient failures
```

3. **Missing input validation** (20+ locations)
```python
# In roadmap_parser.py
priority_number = match.group(1)  # ❌ No validation if match is None
```

4. **Uncaught exceptions in daemon loop**
```python
# In daemon.py, line 466
success = self._implement_priority(next_priority)  # ❌ Crashes daemon on unexpected errors
```

### Impact

**Reliability**: 😞 Poor
- Daemon crashes on transient file system issues (permissions, disk full)
- Network failures bring down entire system
- Malformed ROADMAP.md causes crashes

**User Experience**: 😞 Poor
- Cryptic error messages
- No recovery guidance
- Data loss on unexpected errors

**Debuggability**: 😞 Poor
- Missing context in logs
- Hard to reproduce failures
- No error breadcrumbs

**Operational Metrics** (last 30 days):
- Daemon crashes: 5 (preventable with better error handling)
- User-reported "mysterious failures": 8
- Average time to debug production issues: 45 minutes

---

## Proposed Solution

### Architecture: Defensive Programming with Error Recovery

Implement a **layered error handling strategy**:

1. **Layer 1**: Input Validation (prevent errors)
2. **Layer 2**: Defensive Operations (safe defaults, retry logic)
3. **Layer 3**: Error Recovery (graceful degradation, fallbacks)
4. **Layer 4**: Error Reporting (clear messages, logging, metrics)

**Related Guidelines**:
- [GUIDELINE-001: Error Handling](../../guidelines/GUIDELINE-001-error-handling.md) - Core error handling patterns
- [GUIDELINE-017: Custom Exceptions](../../guidelines/GUIDELINE-017-custom-exceptions.md) - Exception hierarchy design
- [GUIDELINE-020: Observability](../../guidelines/GUIDELINE-020-observability.md) - Error logging and tracing

### Component 1: DefensiveMixin (File Operations)

```python
# coffee_maker/utils/defensive_io.py

import logging
import shutil
from pathlib import Path
from typing import Optional, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class DefensiveFileMixin:
    """Defensive file operations with validation and recovery.

    Provides safe file I/O methods that:
    - Validate inputs before operations
    - Handle common errors gracefully
    - Create automatic backups
    - Use atomic writes
    - Provide clear error messages
    """

    def read_file_safely(
        self,
        path: Path,
        default: Optional[str] = None,
        encoding: str = 'utf-8'
    ) -> Optional[str]:
        """Read file with comprehensive error handling.

        Args:
            path: File path to read
            default: Default value if file cannot be read
            encoding: File encoding (default: utf-8)

        Returns:
            File contents or default value

        Example:
            >>> content = self.read_file_safely(Path("roadmap.md"), default="# Empty")
            >>> print(content)
        """
        # Validate input
        if not isinstance(path, Path):
            path = Path(path)

        # Check existence
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return default

        # Check if it's a file
        if not path.is_file():
            logger.error(f"Path is not a file: {path}")
            return default

        # Try to read
        try:
            return path.read_text(encoding=encoding)

        except PermissionError:
            logger.error(f"Permission denied reading {path}")
            return default

        except UnicodeDecodeError as e:
            logger.error(f"Encoding error in {path}: {e}")
            logger.info(f"Try reading {path} with different encoding")
            return default

        except OSError as e:
            logger.error(f"OS error reading {path}: {e}")
            return default

        except Exception as e:
            logger.error(f"Unexpected error reading {path}: {e}")
            return default

    def write_file_safely(
        self,
        path: Path,
        content: str,
        create_backup: bool = True,
        encoding: str = 'utf-8'
    ) -> bool:
        """Write file with atomic operation and optional backup.

        Args:
            path: File path to write
            content: Content to write
            create_backup: Whether to create backup if file exists
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful, False otherwise

        Example:
            >>> success = self.write_file_safely(
            ...     Path("roadmap.md"),
            ...     "# Updated Roadmap",
            ...     create_backup=True
            ... )
            >>> print(f"Write {'succeeded' if success else 'failed'}")
        """
        # Validate input
        if not isinstance(path, Path):
            path = Path(path)

        if not isinstance(content, str):
            logger.error(f"Content must be string, got {type(content)}")
            return False

        # Create parent directory if needed
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create parent directory {path.parent}: {e}")
            return False

        # Create backup if requested
        backup_path = None
        if create_backup and path.exists():
            try:
                backup_path = path.with_suffix('.backup')
                shutil.copy2(path, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
                # Continue anyway - backup failure shouldn't block write

        # Atomic write
        temp_path = path.with_suffix('.tmp')
        try:
            # Write to temp file
            temp_path.write_text(content, encoding=encoding)

            # Atomic rename
            temp_path.replace(path)

            logger.debug(f"Successfully wrote {path}")
            return True

        except PermissionError:
            logger.error(f"Permission denied writing {path}")
            # Try to restore from backup
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, path)
                logger.info(f"Restored from backup: {backup_path}")
            return False

        except OSError as e:
            logger.error(f"OS error writing {path}: {e}")
            # Try to restore from backup
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, path)
                logger.info(f"Restored from backup: {backup_path}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error writing {path}: {e}")
            return False

        finally:
            # Clean up temp file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors

    def ensure_file_exists(
        self,
        path: Path,
        default_content: str = "",
        encoding: str = 'utf-8'
    ) -> bool:
        """Ensure file exists, create with default content if missing.

        Args:
            path: File path
            default_content: Content to write if file doesn't exist
            encoding: File encoding

        Returns:
            True if file exists (or was created), False on error

        Example:
            >>> self.ensure_file_exists(
            ...     Path("config.json"),
            ...     default_content="{}"
            ... )
        """
        if not isinstance(path, Path):
            path = Path(path)

        if path.exists():
            return True

        # Create with default content
        return self.write_file_safely(path, default_content, create_backup=False, encoding=encoding)
```

### Component 2: Retry Decorator (Network Operations)

```python
# coffee_maker/utils/retry.py

import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Backoff multiplier (default: 2.0)
        exceptions: Tuple of exceptions to catch (default: all)

    Returns:
        Decorated function with retry logic

    Example:
        >>> @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        ... def call_api():
        ...     return requests.get("https://api.example.com")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    time.sleep(delay)
                    delay *= backoff_factor

            return None  # Should never reach here

        return wrapper
    return decorator
```

### Component 3: Input Validation

```python
# coffee_maker/utils/validation.py

from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class Validator:
    """Input validation utilities."""

    @staticmethod
    def validate_not_none(value: Any, name: str) -> Any:
        """Validate value is not None.

        Args:
            value: Value to validate
            name: Value name (for error messages)

        Returns:
            Value if valid

        Raises:
            ValueError: If value is None
        """
        if value is None:
            raise ValueError(f"{name} cannot be None")
        return value

    @staticmethod
    def validate_not_empty(value: str, name: str) -> str:
        """Validate string is not empty.

        Args:
            value: String to validate
            name: Value name (for error messages)

        Returns:
            Value if valid

        Raises:
            ValueError: If value is empty or None
        """
        if not value or not value.strip():
            raise ValueError(f"{name} cannot be empty")
        return value

    @staticmethod
    def validate_file_exists(path: Path, name: str) -> Path:
        """Validate file exists.

        Args:
            path: File path
            name: Value name (for error messages)

        Returns:
            Path if valid

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If path is not a file
        """
        if not path.exists():
            raise FileNotFoundError(f"{name} not found: {path}")

        if not path.is_file():
            raise ValueError(f"{name} is not a file: {path}")

        return path
```

---

---

## Implementation Phases

This specification is organized into phases for progressive disclosure and context efficiency.

### Phase 1: Implement Defensive Utilities (3 hours)
**Document**: [phase1-implement-defensive-utilities.md](./phase1-implement-defensive-utilities.md)

### Phase 2: Apply to Critical Path - daemon.py (3 hours)
**Document**: [phase2-apply-to-critical-path-daemonpy.md](./phase2-apply-to-critical-path-daemonpy.md)

### Phase 3: Apply to Core Modules (4-6 hours)
**Document**: [phase3-apply-to-core-modules.md](./phase3-apply-to-core-modules.md)

### Phase 4: Testing & Monitoring (3 hours)
**Document**: [phase4-testing-monitoring.md](./phase4-testing-monitoring.md)


---

## Related Documents

- [GUIDELINE-001: Error Handling](../../guidelines/GUIDELINE-001-error-handling.md)
- [GUIDELINE-017: Custom Exceptions](../../guidelines/GUIDELINE-017-custom-exceptions.md)
- [GUIDELINE-020: Observability](../../guidelines/GUIDELINE-020-observability.md)

---

**Note**: This specification uses hierarchical format for 71% context reduction.
Each phase is in a separate file - read only the phase you're implementing.
