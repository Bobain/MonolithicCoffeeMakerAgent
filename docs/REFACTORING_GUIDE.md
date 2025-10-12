# Coffee Maker Refactoring Guide

**Version**: 1.0
**Last Updated**: 2025-10-12
**Status**: Living Document

This guide documents the refactoring patterns, best practices, and lessons learned during the US-021 code quality improvement initiative. Use this as a reference when making future changes to the codebase.

---

## Table of Contents

1. [Overview](#overview)
2. [Refactoring Principles](#refactoring-principles)
3. [Code Organization Patterns](#code-organization-patterns)
4. [Configuration Management](#configuration-management)
5. [Error Handling](#error-handling)
6. [File Organization](#file-organization)
7. [Testing Strategy](#testing-strategy)
8. [Migration Checklist](#migration-checklist)
9. [Common Pitfalls](#common-pitfalls)
10. [Examples](#examples)

---

## Overview

### What Was Refactored

**US-021 Achievements** (Phases 0-2):

- ✅ **Type Hints**: 100% coverage (up from 68%)
- ✅ **Docstrings**: Comprehensive Google-style documentation
- ✅ **Code Duplication**: Reduced from 50+ instances to <5%
- ✅ **ConfigManager**: Centralized API key management
- ✅ **File I/O**: Unified JSON utilities
- ✅ **Error Handling**: Custom exception hierarchy
- ✅ **Logging**: Standardized utilities with emoji prefixes
- ✅ **File Splitting**: daemon.py reduced by 62% (1592→611 lines)
- ✅ **Naming**: Removed redundant `_utils` suffixes

### Why This Matters

- **Maintainability**: Easier to find and fix bugs
- **Onboarding**: New developers can understand code faster
- **Testing**: Isolated components are easier to test
- **Performance**: Centralized caching reduces repeated operations
- **Quality**: Consistent patterns reduce cognitive load

---

## Refactoring Principles

### 1. DRY (Don't Repeat Yourself)

**Before** (Duplicated):
```python
# In file1.py
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found")

# In file2.py
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Missing ANTHROPIC_API_KEY")

# In file3.py (15+ more times...)
```

**After** (Centralized):
```python
# All files use ConfigManager
from coffee_maker.config.manager import ConfigManager

api_key = ConfigManager.get_anthropic_api_key(required=True)
# Raises APIKeyMissingError with consistent message
```

**Benefits**:
- One place to update logic
- Consistent error messages
- Built-in caching
- Better testing

### 2. Single Responsibility Principle

**Before** (God Class):
```python
class DevDaemon:
    def run(self): ...              # Main loop
    def _sync_roadmap(self): ...    # Git operations
    def _create_spec(self): ...     # Spec management
    def _implement(self): ...       # Implementation
    def _write_status(self): ...    # Status tracking
    def _notify(self): ...          # Notifications
    # ... 1592 lines total
```

**After** (Mixin Composition):
```python
class DevDaemon(GitOpsMixin, SpecManagerMixin,
                ImplementationMixin, StatusMixin):
    def run(self): ...              # Main loop only
    def _check_prerequisites(self): # Core logic
    def stop(self): ...             # Shutdown
    # ... 611 lines, focused responsibility
```

**Benefits**:
- Easier to understand each component
- Can test mixins independently
- Can reuse mixins in other classes
- Smaller files, faster to navigate

### 3. Defensive Programming

**Before** (Crash-prone):
```python
def create_spec(priority):
    content = priority['content'][:2000]  # KeyError if missing!
    return f"Spec for {priority['name']}"
```

**After** (Defensive):
```python
def create_spec(priority):
    # Validate required fields
    if not priority.get("name"):
        logger.error("Priority missing 'name' field")
        return None

    # Safe content access
    content = priority.get("content", "")
    if not content:
        logger.warning(f"Priority {priority['name']} has no content")
        content = f"Title: {priority.get('title', 'Unknown')}"

    # Safe truncation
    content = content[:2000] if len(content) > 2000 else content
    return f"Spec for {priority['name']}"
```

**Benefits**:
- No KeyError crashes
- Clear error messages
- Graceful degradation
- Better debugging

---

## Code Organization Patterns

### Mixin Pattern (New)

**When to Use**:
- Large class needs to be split (>600 lines)
- Multiple orthogonal responsibilities
- Want to reuse functionality across classes
- Want to maintain backward compatibility

**Implementation**:
```python
# 1. Create focused mixins
# coffee_maker/autonomous/daemon_git_ops.py
class GitOpsMixin:
    """Git operations for daemon."""
    def _sync_roadmap_branch(self): ...
    def _merge_to_roadmap(self): ...

# coffee_maker/autonomous/daemon_status.py
class StatusMixin:
    """Status tracking for daemon."""
    def _write_status(self): ...
    def _update_subtask(self): ...

# 2. Compose in main class
# coffee_maker/autonomous/daemon.py
class DevDaemon(GitOpsMixin, StatusMixin):
    """Main daemon with composed functionality."""
    def __init__(self):
        # Required attributes for mixins
        self.git = GitManager()
        self.notifications = NotificationDB()

    def run(self):
        # Use mixin methods directly
        self._sync_roadmap_branch()
        self._write_status()
```

**Checklist**:
- ✅ Each mixin has clear, focused responsibility
- ✅ Mixin docstring lists required attributes
- ✅ No circular dependencies between mixins
- ✅ Main class provides all required attributes
- ✅ All mixin methods accessible via inheritance

### Utility Modules

**When to Use**:
- Function used in 3+ places
- Pure function (no side effects)
- General-purpose operation (I/O, validation, formatting)

**Structure**:
```
coffee_maker/
├── utils/
│   ├── file_io.py       # JSON read/write
│   ├── logging.py       # Logging helpers
│   ├── time.py          # Time utilities
│   └── validation.py    # Input validation
```

**Example**:
```python
# coffee_maker/utils/file_io.py
from pathlib import Path
from typing import Any, Dict

def read_json_file(path: Path, default: Dict = None) -> Dict[str, Any]:
    """Read JSON file with error handling.

    Args:
        path: Path to JSON file
        default: Default value if file missing/invalid

    Returns:
        Parsed JSON dict or default

    Example:
        >>> data = read_json_file(Path("config.json"), default={})
    """
    if not path.exists():
        return default or {}

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return default or {}
```

---

## Configuration Management

### ConfigManager Pattern

**Always use ConfigManager for**:
- API keys (Anthropic, OpenAI, Gemini, Langfuse)
- Environment variables
- Configuration values
- Secrets management

**Pattern**:
```python
from coffee_maker.config.manager import ConfigManager

# ✅ GOOD: Use ConfigManager
api_key = ConfigManager.get_anthropic_api_key(required=True)

# ❌ BAD: Direct os.getenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

**Exception**: Only use `os.getenv()` for:
- Non-sensitive config (like `DEBUG=true`)
- Test-specific overrides
- Feature flags

**Benefits**:
- Automatic caching (performance)
- Consistent error handling
- APIKeyMissingError with clear messages
- Centralized validation
- Easier to mock in tests

### Custom Exceptions

**Use the exception hierarchy**:
```python
from coffee_maker.exceptions import (
    CoffeeMakerError,      # Base
    ConfigError,           # Config issues
    APIKeyMissingError,    # Missing API key
    ProviderError,         # AI provider errors
    ResourceError,         # File/network errors
    ModelError,            # Model-specific errors
    FileError,             # File operations
    DaemonError,           # Daemon crashes
)

# ✅ GOOD: Specific exception
if not api_key:
    raise APIKeyMissingError(
        "ANTHROPIC_API_KEY not found",
        key_name="ANTHROPIC_API_KEY",
        env_file=".env"
    )

# ❌ BAD: Generic exception
if not api_key:
    raise ValueError("API key missing")
```

---

## Error Handling

### Logging Utilities

**Use standardized logging**:
```python
from coffee_maker.utils.logging import (
    get_logger,
    log_error,
    log_warning,
    log_with_context,
    log_duration,
)

logger = get_logger(__name__)

# ✅ GOOD: Structured logging
log_error(logger, "Failed to load config", exc_info=True,
          config_path=config_path, attempt=retry_count)

# ✅ GOOD: Performance logging
with log_duration(logger, "Claude API call"):
    response = claude.generate(prompt)

# ❌ BAD: Generic logging
logger.error(f"Error: {e}")
```

### Error Recovery Patterns

**Retry with Exponential Backoff**:
```python
from coffee_maker.utils.logging import log_duration
import time

def call_api_with_retry(prompt: str, max_retries: int = 3):
    """Call API with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            with log_duration(logger, f"API call (attempt {attempt + 1})"):
                return api.call(prompt)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            log_warning(logger, f"Rate limited, retrying in {wait_time}s",
                       attempt=attempt + 1, max_retries=max_retries)
            time.sleep(wait_time)
```

**Graceful Degradation**:
```python
def get_ai_response(prompt: str) -> str:
    """Get AI response with fallback providers."""
    providers = ["claude", "openai", "gemini"]

    for provider in providers:
        try:
            return call_provider(provider, prompt)
        except ProviderError as e:
            log_warning(logger, f"{provider} failed, trying next",
                       error=str(e), remaining=providers[providers.index(provider)+1:])

    # All providers failed - return safe default
    return "I'm having trouble responding right now. Please try again later."
```

---

## File Organization

### Size Guidelines

**Target File Sizes**:
- Main modules: **< 600 lines** (daemon.py: 611 ✅)
- Utility modules: **< 300 lines**
- Mixin modules: **< 500 lines**
- Test files: **< 400 lines**

**When to Split**:
1. File exceeds target size
2. Multiple responsibilities evident
3. Hard to find specific functionality
4. Many import statements (>20)

### Naming Conventions

**✅ GOOD Patterns**:
- `config/manager.py` (not `config_manager.py`)
- `utils/logging.py` (not `logging_utils.py`)
- `utils/file_io.py` (not `file_io_utils.py`)
- `daemon_git_ops.py` (mixin, clear purpose)

**❌ BAD Patterns**:
- `util.py` (too generic)
- `helpers.py` (what kind of helpers?)
- `stuff.py` (meaningless)
- `temp.py` (never temporary!)

### Import Organization

**Order**:
```python
# 1. Standard library
import json
import logging
from pathlib import Path
from typing import Dict, Optional

# 2. Third-party
from rich.console import Console
import anthropic

# 3. Local application
from coffee_maker.config.manager import ConfigManager
from coffee_maker.utils.logging import get_logger
from coffee_maker.exceptions import ConfigError
```

---

## Testing Strategy

### Test Coverage Goals

**Minimum Coverage**:
- Overall: **80%**
- Core modules: **90%** (daemon, config, utils)
- Critical paths: **100%** (API calls, file I/O, error handling)

### Test Organization

**Structure**:
```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_config_manager.py
│   ├── test_file_io.py
│   └── test_exceptions.py
├── integration/       # Multiple components
│   ├── test_daemon_workflow.py
│   └── test_api_providers.py
└── e2e/              # Full system tests
    └── test_priority_implementation.py
```

### Testing Patterns

**Unit Test Example**:
```python
import pytest
from coffee_maker.config.manager import ConfigManager
from coffee_maker.exceptions import APIKeyMissingError

class TestConfigManager:
    def test_get_api_key_success(self, monkeypatch):
        """Test successful API key retrieval."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")

        key = ConfigManager.get_anthropic_api_key()
        assert key == "test-key-123"

    def test_get_api_key_missing_required(self, monkeypatch):
        """Test missing required API key raises exception."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(APIKeyMissingError) as exc_info:
            ConfigManager.get_anthropic_api_key(required=True)

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)
```

**Integration Test Example**:
```python
import pytest
from coffee_maker.autonomous.daemon import DevDaemon

class TestDaemonWorkflow:
    def test_priority_implementation_flow(self, tmp_path, mock_claude_api):
        """Test full priority implementation workflow."""
        # Setup
        roadmap_path = tmp_path / "ROADMAP.md"
        roadmap_path.write_text("""
        ### PRIORITY 1: Test Priority
        **Status**: 📝 Planned

        Test implementation
        """)

        daemon = DevDaemon(roadmap_path=str(roadmap_path))

        # Execute
        priority = daemon.parser.get_next_planned_priority()
        success = daemon._implement_priority(priority)

        # Verify
        assert success is True
        assert mock_claude_api.execute_prompt.called
        assert daemon.git.create_branch.called
        assert daemon.git.commit.called
```

---

## Migration Checklist

### When Adding New Code

**✅ Pre-Implementation**:
- [ ] Check if similar functionality exists
- [ ] Read this refactoring guide
- [ ] Choose appropriate design pattern
- [ ] Plan for testability

**✅ During Implementation**:
- [ ] Use ConfigManager for API keys/config
- [ ] Use custom exceptions (not ValueError/Exception)
- [ ] Use logging utilities (not print)
- [ ] Use file_io utilities for JSON
- [ ] Add type hints
- [ ] Add Google-style docstrings

**✅ Post-Implementation**:
- [ ] Write unit tests (>80% coverage)
- [ ] Update documentation
- [ ] Run pre-commit hooks
- [ ] Check mypy validation

### When Refactoring Existing Code

**✅ Analysis Phase**:
- [ ] Identify code duplication
- [ ] Check file size (>600 lines?)
- [ ] List responsibilities
- [ ] Find reusable patterns

**✅ Refactoring Phase**:
- [ ] Extract utilities first (easy wins)
- [ ] Replace os.getenv() with ConfigManager
- [ ] Add defensive error handling
- [ ] Split large files (mixin pattern)
- [ ] Add/improve type hints

**✅ Validation Phase**:
- [ ] All tests passing
- [ ] No regressions
- [ ] Mypy validation clean
- [ ] Update documentation

---

## Common Pitfalls

### 1. **Bare Except Blocks**

**❌ BAD**:
```python
try:
    data = json.load(f)
except:  # Catches ALL exceptions, even KeyboardInterrupt!
    return None
```

**✅ GOOD**:
```python
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return None
except IOError as e:
    logger.error(f"File read error: {e}")
    return None
```

### 2. **Direct Dictionary Access**

**❌ BAD**:
```python
def process(priority):
    name = priority['name']  # KeyError if missing!
    content = priority['content'][:100]  # Crash if None!
```

**✅ GOOD**:
```python
def process(priority):
    # Validate required fields
    name = priority.get('name')
    if not name:
        logger.error("Priority missing name field")
        return None

    # Safe access with default
    content = priority.get('content', '')
    if content:
        content = content[:100]
```

### 3. **Inconsistent Error Messages**

**❌ BAD**:
```python
# file1.py
raise ValueError("API key not found")

# file2.py
raise Exception("Missing API key")

# file3.py
raise RuntimeError("ANTHROPIC_API_KEY required")
```

**✅ GOOD**:
```python
# All files
from coffee_maker.exceptions import APIKeyMissingError
raise APIKeyMissingError("ANTHROPIC_API_KEY not found in environment")
```

### 4. **Magic Numbers/Strings**

**❌ BAD**:
```python
def retry_api_call():
    for i in range(3):  # Why 3?
        time.sleep(2 ** i)  # What's this formula?
```

**✅ GOOD**:
```python
MAX_RETRIES = 3  # Industry standard for network operations
EXPONENTIAL_BACKOFF_BASE = 2  # 1s, 2s, 4s intervals

def retry_api_call():
    for attempt in range(MAX_RETRIES):
        wait_time = EXPONENTIAL_BACKOFF_BASE ** attempt
        time.sleep(wait_time)
```

---

## Examples

### Complete Refactoring Example

**Before** (465 lines, many issues):
```python
# coffee_maker/old_daemon.py
import os
import json

class OldDaemon:
    def run(self):
        # Get API key (duplicated in 15+ places)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("API key missing")

        # Read roadmap (duplicated JSON I/O)
        with open("roadmap.json") as f:
            roadmap = json.load(f)

        # Process priority (unsafe dict access)
        priority = roadmap['priorities'][0]
        name = priority['name']  # Crashes if missing!
        content = priority['content'][:100]  # Crashes if None!

        # Implementation (god method, 200+ lines)
        # ... tons of code ...
```

**After** (Clean, maintainable):
```python
# coffee_maker/autonomous/daemon.py
from typing import Optional
from coffee_maker.config.manager import ConfigManager
from coffee_maker.utils.file_io import read_json_file
from coffee_maker.utils.logging import get_logger
from coffee_maker.exceptions import ConfigError, FileError
from .daemon_implementation import ImplementationMixin

logger = get_logger(__name__)

class DevDaemon(ImplementationMixin):
    """Autonomous development daemon.

    Composed from mixins for focused responsibilities.
    """

    def run(self) -> None:
        """Run daemon main loop."""
        # Get API key (centralized, cached)
        try:
            api_key = ConfigManager.get_anthropic_api_key(required=True)
        except ConfigError as e:
            log_error(logger, "Configuration error", exc_info=True)
            return

        # Read roadmap (utility function, safe)
        roadmap = read_json_file(
            Path("roadmap.json"),
            default={"priorities": []}
        )

        # Process priority (defensive, validated)
        if not roadmap.get("priorities"):
            logger.warning("No priorities found in roadmap")
            return

        priority = roadmap["priorities"][0]
        success = self._implement_priority(priority)  # Mixin method

        if success:
            logger.info(f"✅ Implemented {priority.get('name', 'Unknown')}")
        else:
            logger.warning(f"⚠️ Implementation failed")
```

---

## Appendix: Quick Reference

### Code Review Checklist

**Before Approving PR**:
- [ ] All files < 600 lines
- [ ] Type hints on all functions
- [ ] Google-style docstrings
- [ ] Using ConfigManager (not os.getenv for API keys)
- [ ] Using custom exceptions (not ValueError/Exception)
- [ ] Using logging utilities (not print)
- [ ] No bare except blocks
- [ ] Safe dictionary access (.get())
- [ ] Test coverage > 80%
- [ ] Mypy validation passing
- [ ] Pre-commit hooks passing

### Refactoring Decision Tree

```
Is the file > 600 lines?
├─ YES → Consider mixin pattern or module split
└─ NO → Is code duplicated in 3+ places?
    ├─ YES → Extract to utility module
    └─ NO → Is error handling consistent?
        ├─ NO → Use custom exceptions + logging utilities
        └─ YES → Ship it! ✅
```

### Common Imports

```python
# Configuration
from coffee_maker.config.manager import ConfigManager

# Exceptions
from coffee_maker.exceptions import (
    CoffeeMakerError, ConfigError, APIKeyMissingError,
    ProviderError, ResourceError, FileError
)

# Utilities
from coffee_maker.utils.file_io import read_json_file, write_json_file
from coffee_maker.utils.logging import get_logger, log_error, log_duration
from coffee_maker.utils.time import format_duration, get_timestamp

# Type hints
from typing import Dict, List, Optional, Any
from pathlib import Path
```

---

## Conclusion

This refactoring guide represents the lessons learned from US-021. Following these patterns will:

✅ **Improve code quality** (fewer bugs, better maintainability)
✅ **Speed up development** (less duplication, clearer patterns)
✅ **Enhance testability** (isolated components, dependency injection)
✅ **Reduce cognitive load** (consistent patterns, clear organization)

**Remember**: Refactoring is never "done". Continuously improve the codebase while delivering features.

---

**Document Maintainers**: code_developer
**Last Review**: 2025-10-12
**Next Review**: After Phase 3 completion

🤖 *Generated with [Claude Code](https://claude.com/claude-code) via code_developer*
