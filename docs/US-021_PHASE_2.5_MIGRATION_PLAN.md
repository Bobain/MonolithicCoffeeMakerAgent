# US-021 Phase 2.5: Utility Adoption & Systematic Refactoring

**Status**: 📝 Planned
**Created**: 2025-10-12
**Estimated Effort**: 7-10 days
**Priority**: High - Foundation for code quality

## Overview

This phase focuses on systematically adopting the utilities and patterns created in Phase 2, ensuring the entire codebase benefits from:
- Unified exception hierarchy
- Standardized logging with context
- ConfigManager for all configuration
- Error recovery strategies implementation
- Fixing dangerous error handling patterns

## Goals

1. **100% adoption** of `coffee_maker/utils/logging_utils.py` (71 files)
2. **100% adoption** of `coffee_maker/exceptions.py` hierarchy (70+ files)
3. **Complete ConfigManager migration** (10 remaining files)
4. **Zero dangerous error patterns** (fix 12+ files with bare except:)
5. **Error recovery implementation** in critical paths (20+ files)

## Current State

### Phase 2 Completions (2025-10-12)
- ✅ Exception hierarchy created (`coffee_maker/exceptions.py`, 365 lines)
- ✅ Logging utilities created (`coffee_maker/utils/logging_utils.py`, 469 lines)
- ✅ Error recovery documentation (`docs/ERROR_RECOVERY_STRATEGIES.md`, 800+ lines)
- ✅ ConfigManager created and partially adopted (Phase 1)

### Adoption Status
- ❌ **71 files** still using `logging.getLogger()` directly
- ❌ **70+ files** not using exception hierarchy
- ❌ **10 files** still using `os.getenv()` directly
- ❌ **12+ files** with dangerous error patterns (`except:`, generic `except Exception:`)
- ❌ **0 files** implementing documented error recovery strategies

## Execution Plan

---

## **STAGE 1: High-Impact, Low-Effort Fixes** (1.5 days)

**Goal**: Fix critical safety issues and complete ConfigManager migration

### Task 1.1: Fix Dangerous Error Handling (1 day)

**Files with bare `except:` (CRITICAL):**
1. `coffee_maker/autonomous/daemon.py:779`
   - Context: Git checkout recovery
   - Fix: Catch `subprocess.CalledProcessError`, log with context

2. `coffee_maker/cli/chat_interface.py`
   - Search pattern: `except:`
   - Count occurrences
   - Fix each with specific exception types

3. `coffee_maker/langchain_observe/llm.py`
   - Similar pattern
   - Add structured error logging

**Implementation Pattern:**
```python
# BEFORE (DANGEROUS):
try:
    risky_operation()
except:
    pass  # Silently swallows KeyboardInterrupt, SystemExit!

# AFTER (SAFE):
from coffee_maker.exceptions import SpecificError
from coffee_maker.utils.logging_utils import log_error

try:
    risky_operation()
except SpecificError as e:
    log_error(logger, "Operation failed", e, context={"operation": "risky"})
    # Decide: raise, return default, or continue
except Exception as e:
    log_error(logger, "Unexpected error", e)
    raise  # Don't swallow unexpected errors
```

**Acceptance Criteria:**
- [ ] Zero files with bare `except:`
- [ ] All `except Exception:` have structured logging
- [ ] All error handlers specify recovery action
- [ ] Test each fixed error path

**Estimated Time**: 6-8 hours

---

### Task 1.2: Complete ConfigManager Migration (0.5 days)

**Remaining files using `os.getenv()`:**

1. `coffee_maker/monitoring/metrics.py`
2. `coffee_maker/monitoring/alerts.py`
3. `coffee_maker/api/routes/status.py`
4. `coffee_maker/api/main.py`
5. `coffee_maker/langchain_observe/analytics/config.py`
6. `coffee_maker/code_formatter/main.py`
7. `coffee_maker/langchain_observe/llm.py`
8. `coffee_maker/cli/gcp_client.py` (custom config - may skip)
9. `coffee_maker/ai_providers/provider_config.py`
10. `coffee_maker/config/manager.py` (implementation file - skip)

**Migration Pattern:**
```python
# BEFORE:
import os
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Missing ANTHROPIC_API_KEY")

# AFTER:
from coffee_maker.config.manager import ConfigManager
api_key = ConfigManager.get_anthropic_api_key(required=True)
# Raises APIKeyMissingError with helpful message automatically
```

**Acceptance Criteria:**
- [ ] All files use ConfigManager for API keys
- [ ] Zero `os.getenv()` for API keys (except custom configs)
- [ ] All imports tested and working
- [ ] Update imports in affected files

**Estimated Time**: 3-4 hours

---

## **STAGE 2: Logging Utilities Adoption** (2-3 days)

**Goal**: Migrate 71 files to use standardized logging utilities

### Task 2.1: Identify Migration Priorities (0.5 days)

Create prioritized file list:
- **Tier 1 (Critical)**: daemon.py, chat_interface.py, ai_service.py (most used)
- **Tier 2 (High)**: AI providers, git_manager, roadmap_parser
- **Tier 3 (Medium)**: CLI commands, utilities
- **Tier 4 (Low)**: Analytics, examples, tests

**Deliverable**: `docs/LOGGING_MIGRATION_CHECKLIST.md` with all 71 files categorized

**Estimated Time**: 4 hours

---

### Task 2.2: Tier 1 - Critical Files (1 day)

**Files:**
1. `coffee_maker/autonomous/daemon.py` (1579 lines, 50+ logging calls)
2. `coffee_maker/cli/chat_interface.py` (1436 lines, 40+ logging calls)
3. `coffee_maker/cli/ai_service.py` (747 lines, 30+ logging calls)

**Migration Steps per File:**
1. Add import: `from coffee_maker.utils.logging_utils import get_logger, log_error, log_warning, log_duration, LogFormatter`
2. Replace `logging.getLogger(__name__)` with `get_logger(__name__)`
3. Replace error logging:
   - `logger.error(f"msg {e}")` → `log_error(logger, "msg", e, context={...})`
4. Add context to critical logs:
   - Include operation name, attempt count, relevant IDs
5. Wrap slow operations with `log_duration`:
   - Claude API calls
   - Database operations
   - Git operations
6. Use `LogFormatter` for user-visible messages:
   - `LogFormatter.success("Task complete")`
   - `LogFormatter.error("Operation failed")`

**Example Migration:**
```python
# BEFORE:
logger = logging.getLogger(__name__)

try:
    result = claude.execute_prompt(prompt)
    logger.info("Claude API succeeded")
except Exception as e:
    logger.error(f"Claude API failed: {e}")
    raise

# AFTER:
from coffee_maker.utils.logging_utils import get_logger, log_error, log_duration

logger = get_logger(__name__)

try:
    with log_duration(logger, "Claude API execution") as ctx:
        result = claude.execute_prompt(prompt)
        ctx["tokens"] = result.usage["input_tokens"]
        # Automatically logs: "Claude API execution completed in 45.32s (tokens=1500)"
except Exception as e:
    log_error(
        logger,
        "Claude API execution failed",
        e,
        context={
            "model": "claude-sonnet-4",
            "prompt_length": len(prompt),
            "attempt": attempt_count
        }
    )
    raise
```

**Acceptance Criteria:**
- [ ] All 3 files use `get_logger(__name__)`
- [ ] All error logs use `log_error()` with context
- [ ] Slow operations wrapped in `log_duration()`
- [ ] User-facing messages use `LogFormatter`
- [ ] Test each file's functionality after migration
- [ ] Commit per file: "refactor: Adopt logging utilities in {filename}"

**Estimated Time**: 8 hours

---

### Task 2.3: Tier 2 - High Priority Files (0.5 days)

**Files:**
1. `coffee_maker/ai_providers/providers/claude_provider.py`
2. `coffee_maker/ai_providers/providers/openai_provider.py`
3. `coffee_maker/ai_providers/providers/gemini_provider.py`
4. `coffee_maker/autonomous/git_manager.py`
5. `coffee_maker/autonomous/roadmap_parser.py`
6. `coffee_maker/utils/github.py`

**Same migration pattern as Tier 1, fewer logging calls per file**

**Estimated Time**: 4 hours

---

### Task 2.4: Tier 3 & 4 - Remaining Files (1 day)

**Batch processing:**
- CLI commands (15 files)
- Utilities (10 files)
- LangChain observe (20 files)
- Analytics (10 files)
- Code formatter (5 files)
- Monitoring (5 files)

**Strategy**: Similar patterns, focus on error logging with context

**Estimated Time**: 8 hours

---

## **STAGE 3: Exception Hierarchy Adoption** (2-3 days)

**Goal**: Replace scattered exceptions with unified hierarchy

### Task 3.1: Audit Current Exception Usage (0.5 days)

**Search patterns:**
```bash
grep -r "raise ValueError" coffee_maker/
grep -r "raise RuntimeError" coffee_maker/
grep -r "raise Exception" coffee_maker/
grep -r "class.*Error.*Exception" coffee_maker/
```

**Deliverable**:
- List of all custom exceptions currently defined
- List of all generic exception raises
- Mapping: generic exception → appropriate hierarchy exception

**Estimated Time**: 4 hours

---

### Task 3.2: Replace Generic Exceptions (1 day)

**Common patterns:**

```python
# Pattern 1: Configuration errors
# BEFORE:
raise ValueError("Missing API key")
# AFTER:
from coffee_maker.exceptions import APIKeyMissingError
raise APIKeyMissingError("ANTHROPIC_API_KEY")

# Pattern 2: Provider errors
# BEFORE:
raise RuntimeError(f"Provider {name} failed")
# AFTER:
from coffee_maker.exceptions import ProviderError
raise ProviderError(f"Provider {name} failed", details={"provider": name})

# Pattern 3: File errors
# BEFORE:
raise OSError(f"Cannot read {path}")
# AFTER:
from coffee_maker.exceptions import FileOperationError
raise FileOperationError(f"Cannot read {path}", details={"path": path})

# Pattern 4: Resource limits
# BEFORE:
raise Exception("Rate limit exceeded")
# AFTER:
from coffee_maker.exceptions import RateLimitError
raise RateLimitError(provider="openai", limit_type="requests", retry_after=60)
```

**Priority files:**
1. AI providers (already use some exceptions)
2. Config manager (already uses exceptions)
3. Daemon (many error cases)
4. Git manager
5. File I/O utilities

**Acceptance Criteria:**
- [ ] Zero generic `raise ValueError` for domain errors
- [ ] Zero generic `raise RuntimeError` for domain errors
- [ ] All domain errors use appropriate exception type
- [ ] All custom exceptions include `details` dict
- [ ] Exception messages are user-friendly

**Estimated Time**: 8 hours

---

### Task 3.3: Update Exception Handlers (1 day)

**Pattern:**
```python
# BEFORE:
try:
    provider.execute()
except Exception as e:
    logger.error(f"Failed: {e}")
    return None

# AFTER:
from coffee_maker.exceptions import ProviderError, RateLimitError, AllProvidersFailedError
from coffee_maker.utils.logging_utils import log_error

try:
    provider.execute()
except RateLimitError as e:
    # Specific handling for rate limits
    log_error(logger, "Rate limited, will retry", e)
    time.sleep(e.retry_after or 60)
    return retry_with_backoff(provider.execute)
except ProviderError as e:
    # Fallback to next provider
    log_error(logger, "Provider failed, trying fallback", e)
    return fallback_provider.execute()
except CoffeeMakerError as e:
    # All application errors
    log_error(logger, "Application error", e)
    return None
```

**Estimated Time**: 8 hours

---

## **STAGE 4: Error Recovery Implementation** (2-3 days)

**Goal**: Implement documented error recovery strategies in critical paths

### Task 4.1: Create Error Recovery Module (0.5 days)

**File**: `coffee_maker/utils/error_recovery.py`

**Contents:**
1. `retry_with_backoff()` decorator
2. `exponential_backoff_with_jitter()` function
3. `CircuitBreaker` class (from documentation)
4. `fallback()` decorator

**Example implementation:**
```python
"""Error recovery utilities implementing strategies from ERROR_RECOVERY_STRATEGIES.md"""

import functools
import random
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional, Tuple, Type

from coffee_maker.utils.logging_utils import get_logger, log_error

logger = get_logger(__name__)


def exponential_backoff_with_jitter(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> float:
    """Calculate backoff delay with jitter.

    Args:
        attempt: Attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds with jitter added
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = delay * 0.25 * (2 * random.random() - 1)
    return delay + jitter


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay between retries
        retriable_exceptions: Tuple of exceptions to retry on

    Returns:
        Decorated function

    Example:
        >>> @retry_with_backoff(max_retries=3, retriable_exceptions=(RateLimitError,))
        >>> def call_api():
        >>>     return client.execute()
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retriable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        logger.error(f"All {max_retries} retries exhausted for {func.__name__}")
                        raise

                    delay = exponential_backoff_with_jitter(attempt, base_delay, max_delay)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}, "
                        f"retrying in {delay:.2f}s",
                        extra={"exception": str(e), "delay": delay}
                    )
                    time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Failing, reject requests
    HALF_OPEN = "half_open"    # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker for failing operations.

    Prevents cascading failures by temporarily disabling failing operations.

    States:
        CLOSED: Normal operation
        OPEN: Too many failures, reject all requests
        HALF_OPEN: Testing if service recovered

    Example:
        >>> breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        >>> result = breaker.call(risky_function, arg1, arg2)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            timeout: Seconds before attempting recovery
            success_threshold: Successes needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at: Optional[datetime] = None

    def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if datetime.now() - self.opened_at > timedelta(seconds=self.timeout):
                logger.info("Circuit breaker: transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN (opened at {self.opened_at})"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                logger.info("Circuit breaker: transitioning to CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            logger.warning(
                f"Circuit breaker: transitioning to OPEN "
                f"({self.failure_count} failures)"
            )
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now()


def fallback(fallback_func: Callable):
    """Decorator to provide fallback function on failure.

    Args:
        fallback_func: Function to call if primary fails

    Returns:
        Decorated function

    Example:
        >>> def use_cache():
        >>>     return cached_data
        >>>
        >>> @fallback(use_cache)
        >>> def fetch_from_api():
        >>>     return api.get_data()
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(
                    logger,
                    f"{func.__name__} failed, using fallback",
                    e
                )
                return fallback_func(*args, **kwargs)

        return wrapper
    return decorator


__all__ = [
    "exponential_backoff_with_jitter",
    "retry_with_backoff",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
    "fallback",
]
```

**Acceptance Criteria:**
- [ ] All recovery utilities implemented and tested
- [ ] Unit tests for each utility (>90% coverage)
- [ ] Documentation strings complete
- [ ] Examples in docstrings work

**Estimated Time**: 4 hours

---

### Task 4.2: Apply to Critical Paths (1 day)

**Priority locations:**

1. **daemon.py**: Claude API calls
   ```python
   from coffee_maker.utils.error_recovery import CircuitBreaker, retry_with_backoff
   from coffee_maker.exceptions import RateLimitError

   class DevDaemon:
       def __init__(self):
           self.claude_breaker = CircuitBreaker(
               failure_threshold=5,
               timeout=300,
               success_threshold=2
           )

       @retry_with_backoff(
           max_retries=3,
           retriable_exceptions=(RateLimitError,)
       )
       def _call_claude_with_retry(self, prompt):
           return self.claude_breaker.call(
               self.claude.execute_prompt,
               prompt
           )
   ```

2. **AI providers**: Rate limit handling
   ```python
   @retry_with_backoff(
       max_retries=3,
       base_delay=2.0,
       retriable_exceptions=(RateLimitError, QuotaExceededError)
   )
   def execute_prompt(self, prompt):
       # Implementation
   ```

3. **git_manager.py**: Network operations
   ```python
   @retry_with_backoff(
       max_retries=3,
       retriable_exceptions=(subprocess.CalledProcessError,)
   )
   def push(self):
       # Implementation
   ```

4. **file_io.py**: Transient filesystem errors
   ```python
   @retry_with_backoff(
       max_retries=3,
       base_delay=0.5,
       retriable_exceptions=(OSError,)
   )
   def write_json_file(path, data):
       # Implementation with atomic write
   ```

**Acceptance Criteria:**
- [ ] All Claude API calls use circuit breaker
- [ ] All rate limit errors use retry with backoff
- [ ] All network operations use retry
- [ ] All file operations handle transient errors
- [ ] Test recovery behavior for each

**Estimated Time**: 8 hours

---

### Task 4.3: Add Fallback Chains (1 day)

**Provider fallback:**
```python
from coffee_maker.utils.error_recovery import fallback
from coffee_maker.exceptions import ProviderUnavailableError

class AIService:
    def __init__(self):
        self.primary = openai_provider
        self.secondary = gemini_provider
        self.tertiary = claude_provider

    def execute_with_fallback(self, prompt):
        """Execute with automatic provider fallback."""
        providers = [self.primary, self.secondary, self.tertiary]

        for provider in providers:
            try:
                return provider.execute_prompt(prompt)
            except ProviderUnavailableError as e:
                logger.warning(f"{provider.name} unavailable, trying next")
                continue

        raise AllProvidersFailedError("All providers exhausted")
```

**Acceptance Criteria:**
- [ ] All provider calls use fallback chain
- [ ] Fallback order based on cost/availability
- [ ] Log each fallback transition
- [ ] Test complete fallback chain

**Estimated Time**: 8 hours

---

## **STAGE 5: File Splitting** (2-3 days)

**Goal**: Break down files >600 lines into focused modules

### Task 5.1: Split daemon.py (1 day)

**Current**: 1579 lines
**Target**: 4-5 files, each <400 lines

**Proposed structure:**
```
coffee_maker/autonomous/
├── daemon.py (400 lines)          # Main loop, coordination
├── daemon_prompts.py (300 lines)  # Prompt building
├── daemon_status.py (250 lines)   # Status tracking, subtasks
├── daemon_recovery.py (200 lines) # Crash recovery, context reset
└── daemon_specs.py (200 lines)    # Tech spec creation
```

**Migration approach:**
1. Create new modules with extracted functions
2. Update imports in daemon.py
3. Test each extraction incrementally
4. Commit per extraction

**Estimated Time**: 8 hours

---

### Task 5.2: Split chat_interface.py (0.5 days)

**Current**: 1436 lines
**Target**: 3-4 files, each <500 lines

**Proposed structure:**
```
coffee_maker/cli/
├── chat_interface.py (400 lines)    # Main interface loop
├── chat_commands.py (300 lines)     # Command handlers
├── chat_display.py (300 lines)      # UI rendering
└── chat_history.py (200 lines)      # Conversation history
```

**Estimated Time**: 4 hours

---

### Task 5.3: Split Remaining Large Files (1 day)

**Files:**
- `roadmap_cli.py` (967 lines) → 2 files
- `roadmap_editor.py` (945 lines) → 2-3 files
- `ai_service.py` (747 lines) → 2 files

**Estimated Time**: 8 hours

---

## Success Metrics

### Code Quality Metrics
- [ ] **Type hint coverage**: Maintain 100%
- [ ] **Docstring coverage**: Maintain 100% for public APIs
- [ ] **Average file size**: < 500 lines (currently 330)
- [ ] **Max file size**: < 800 lines (currently 1579)
- [ ] **Code duplication**: < 3% (use pylint)

### Migration Metrics
- [ ] **Logging adoption**: 100% (71/71 files)
- [ ] **Exception adoption**: 100% (70+/70+ files)
- [ ] **ConfigManager adoption**: 100% (10/10 remaining files)
- [ ] **Dangerous patterns**: 0 (currently 12+)
- [ ] **Error recovery**: 20+ critical paths

### Testing Metrics
- [ ] **Unit test coverage**: > 80%
- [ ] **Integration tests**: All critical workflows
- [ ] **Regression tests**: No functionality broken
- [ ] **Performance**: No degradation from refactoring

## Testing Strategy

### Per-Stage Testing

**Stage 1 (Fixes):**
- Run full test suite after each file
- Manual smoke test for daemon, chat_interface
- Test error paths explicitly

**Stage 2 (Logging):**
- Check log output format
- Verify structured context in logs
- Test log_duration accuracy

**Stage 3 (Exceptions):**
- Test each exception type raised/caught
- Verify exception messages are user-friendly
- Check exception context/details

**Stage 4 (Recovery):**
- Test retry logic with mock failures
- Test circuit breaker state transitions
- Test fallback chains
- Simulate rate limits, network errors

**Stage 5 (Splitting):**
- Run full test suite after each split
- Check imports work correctly
- Verify no functionality lost

### Regression Testing

After each commit:
```bash
# Unit tests
pytest tests/ -v

# Type checking
mypy coffee_maker/

# Linting
black coffee_maker/
autoflake coffee_maker/

# Integration tests
./scripts/integration_test.sh
```

## Rollback Plan

If migration causes issues:

1. **Per-commit rollback**: Each stage committed separately
   ```bash
   git revert <commit-hash>
   ```

2. **Per-stage rollback**: Create branch per stage
   ```bash
   git checkout main
   git branch -D stage-2-logging-migration
   ```

3. **Feature flags**: Add flags to toggle new behavior
   ```python
   USE_NEW_LOGGING = os.getenv("USE_NEW_LOGGING", "true").lower() == "true"
   ```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking changes | Medium | High | Incremental commits, full test suite |
| Performance degradation | Low | Medium | Benchmark before/after, profiling |
| Import cycles | Medium | Medium | Careful module design, dependency graph |
| Test failures | High | Low | Fix tests as discovered |
| Merge conflicts | High | Low | Frequent merges to roadmap |

## Communication Plan

**User notifications:**
- Create ticket: US-021.5 - Utility Adoption & Systematic Refactoring
- Update ROADMAP.md daily with progress
- Merge to roadmap branch after each stage
- Create notification on completion

**Progress tracking:**
- Daily status updates in ROADMAP.md
- Commit messages follow convention: `refactor(phase-2.5): {description}`
- Use todo list for task tracking
- Record time spent per stage

## Timeline

| Stage | Tasks | Estimated | Start | End |
|-------|-------|-----------|-------|-----|
| 1 | High-impact fixes | 1.5 days | Day 1 | Day 2 |
| 2 | Logging adoption | 2-3 days | Day 2 | Day 5 |
| 3 | Exception adoption | 2-3 days | Day 5 | Day 8 |
| 4 | Error recovery | 2-3 days | Day 8 | Day 11 |
| 5 | File splitting | 2-3 days | Day 11 | Day 14 |
| **Total** | | **10-14 days** | | |

## Deliverables

1. **Code artifacts:**
   - [ ] `coffee_maker/utils/error_recovery.py` (new)
   - [ ] 71 files migrated to logging utilities
   - [ ] 70+ files using exception hierarchy
   - [ ] 10 files migrated to ConfigManager
   - [ ] 5 large files split into 15+ focused modules

2. **Documentation:**
   - [ ] `docs/LOGGING_MIGRATION_CHECKLIST.md`
   - [ ] Updated `docs/REFACTORING_GUIDE.md`
   - [ ] Migration notes in each refactored file

3. **Testing:**
   - [ ] Unit tests for error_recovery.py
   - [ ] Integration tests for recovery patterns
   - [ ] Regression test suite passing

4. **Metrics:**
   - [ ] Code quality report (before/after)
   - [ ] Test coverage report
   - [ ] Performance benchmark results

## Next Steps After Phase 2.5

1. **Phase 3**: Testing & Documentation
   - Achieve >80% unit test coverage
   - Create integration tests
   - Update architecture diagrams

2. **Phase 4**: Performance & Optimization
   - Profile slow operations
   - Add caching where appropriate
   - Optimize imports

## References

- US-021: Code Refactoring & Technical Debt Reduction
- `docs/ERROR_RECOVERY_STRATEGIES.md`
- `coffee_maker/exceptions.py`
- `coffee_maker/utils/logging_utils.py`
- `coffee_maker/config/manager.py`

## Approval

**Created by**: code_developer (autonomous daemon)
**Date**: 2025-10-12
**Status**: Awaiting user approval

**Questions for user:**
1. Approve timeline (10-14 days)?
2. Any files to exclude from migration?
3. Any additional patterns to address?
4. Preferred order of stages?

---

**End of Migration Plan**
