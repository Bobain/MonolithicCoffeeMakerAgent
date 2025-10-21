# SPEC-062: Logging Setup Consolidation

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: code-searcher refactoring_priorities_2025-10-17.md (Priority 4.1)
**Priority**: LOW
**Impact**: LOW (Maintenance)

---

## Problem Statement

### Current State
12 files have duplicate `logging.basicConfig()` calls with inconsistent configurations:
- Different log levels (INFO, DEBUG, WARNING)
- Different formats
- Different output destinations
- Scattered across codebase

### code-searcher Finding
> **Code Duplication: Logging Setup**
> - Pattern: `logging.basicConfig()` in 12 files
> - Issue: Inconsistent log configuration
> - Recommendation: Extract to single utility module
> - Effort: 3 hours
> - Impact: LOW (consistency improvement)

### Why This Matters
- Hard to change logging format globally
- Inconsistent log levels confuse users
- Duplicate code violates DRY principle
- Difficult to add new logging features

---

## Proposed Solution

Create centralized logging utility:

**`coffee_maker/utils/logging_setup.py`**:
```python
"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path


def setup_logging(
    name: str = None,
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_file: Path = None
) -> logging.Logger:
    """
    Configure logging with consistent format.

    Args:
        name: Logger name (defaults to calling module)
        level: Log level (INFO, DEBUG, etc.)
        log_to_file: Whether to log to file
        log_file: Custom log file path

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Consistent format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler (if requested)
    if log_to_file:
        log_file = log_file or Path("logs") / f"{name or 'app'}.log"
        log_file.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

---

## Migration

### Before (12 files with duplicate code)
```python
# daemon.py
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# roadmap_cli.py
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# chat_interface.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### After (consistent)
```python
# All files
from coffee_maker.utils.logging_setup import setup_logging

logger = setup_logging(__name__)
```

---

## Technical Details

### Files to Update
1. `daemon.py`
2. `roadmap_cli.py`
3. `chat_interface.py`
4. `daemon_git_ops.py`
5. `daemon_implementation.py`
6. `daemon_spec_manager.py`
7. `notifications.py`
8. `analyzer.py`
9. `status_report_generator.py`
10. `user_listener.py`
11. `code_reviewer/git_integration.py`
12. `langfuse_observe/analytics/analyzer.py`

### Migration Steps
1. Create `logging_setup.py` utility (30 min)
2. Update 12 files to use utility (1.5 hours)
3. Test logging still works (30 min)
4. Remove old basicConfig calls (30 min)

---

## Rollout Plan

### Week 1: Implementation (3 hours)
- **Day 1**: Create utility, update 6 files (1.5 hours)
- **Day 2**: Update remaining 6 files, test (1.5 hours)

---

## Success Criteria

### Quantitative
- ✅ 12 files updated to use utility
- ✅ Zero direct `basicConfig()` calls
- ✅ Consistent log format across all modules
- ✅ All tests pass

### Qualitative
- ✅ Easier to change logging format
- ✅ Consistent log levels
- ✅ Single place to configure logging

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 3 hours
**Actual Effort**: TBD
