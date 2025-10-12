# Error Recovery Strategies

**Version**: 1.0
**Last Updated**: 2025-10-12
**Related**: US-021 Phase 2 - Architecture Improvements

## Overview

This document describes error handling and recovery strategies for the Coffee Maker Agent. It provides guidelines for handling different exception types, implementing retry logic, and ensuring graceful degradation of service.

## Table of Contents

1. [Exception Hierarchy](#exception-hierarchy)
2. [General Principles](#general-principles)
3. [Recovery Strategies by Error Type](#recovery-strategies-by-error-type)
4. [Retry Patterns](#retry-patterns)
5. [Circuit Breaker Pattern](#circuit-breaker-pattern)
6. [Fallback Mechanisms](#fallback-mechanisms)
7. [Logging and Monitoring](#logging-and-monitoring)
8. [Examples](#examples)

---

## Exception Hierarchy

The Coffee Maker Agent uses a unified exception hierarchy defined in `coffee_maker/exceptions.py`:

```
CoffeeMakerError (base)
├── ConfigError
│   ├── ConfigurationError
│   └── APIKeyMissingError
├── ProviderError
│   ├── ProviderNotFoundError
│   ├── ProviderNotEnabledError
│   ├── ProviderConfigError
│   ├── ProviderUnavailableError
│   └── AllProvidersFailedError
├── ResourceError
│   ├── RateLimitError
│   ├── QuotaExceededError
│   ├── CostLimitExceededError
│   └── BudgetExceededError
├── ModelError
│   ├── ModelNotAvailableError
│   └── ContextLengthError
├── FileError
│   └── FileOperationError
└── DaemonError
    ├── DaemonCrashError
    └── DaemonStateError
```

**Usage**:
```python
from coffee_maker.exceptions import (
    CoffeeMakerError,
    ProviderError,
    ResourceError,
    RateLimitError,
)

try:
    # Operation that may fail
    result = provider.execute_prompt(prompt)
except RateLimitError as e:
    # Handle rate limiting
    logger.warning(f"Rate limited: {e}")
except ProviderError as e:
    # Handle provider failures
    logger.error(f"Provider failed: {e}")
except CoffeeMakerError as e:
    # Catch-all for application errors
    logger.error(f"Application error: {e}")
```

---

## General Principles

### 1. Fail Fast, Recover Gracefully

- **Detect errors early**: Validate inputs and check preconditions
- **Report errors clearly**: Use structured logging with context
- **Recover when possible**: Implement retry logic and fallbacks
- **Fail gracefully**: Provide useful error messages to users

### 2. Error Context is Critical

Always include relevant context when raising or logging errors:
```python
from coffee_maker.utils.logging_utils import log_error

try:
    result = api_call()
except Exception as e:
    log_error(
        logger,
        "API call failed",
        e,
        context={
            "provider": "openai",
            "model": "gpt-4-turbo",
            "retry_count": retry_count,
        }
    )
```

### 3. Don't Swallow Exceptions

Avoid bare `except:` clauses that hide errors:
```python
# Bad: Swallows all errors
try:
    operation()
except:
    pass

# Good: Specific exception handling
try:
    operation()
except RateLimitError as e:
    handle_rate_limit(e)
except ProviderError as e:
    log_error(logger, "Provider failed", e)
    raise  # Re-raise if we can't handle it
```

### 4. Use Exception Chaining

When catching and re-raising exceptions, preserve the original exception:
```python
try:
    parse_config(data)
except ValueError as e:
    raise ConfigurationError(
        f"Invalid configuration format: {e}",
        details={"data": data}
    ) from e
```

---

## Recovery Strategies by Error Type

### ConfigError

**Characteristics**: Configuration issues, missing API keys, invalid settings

**Recovery Strategy**: FAIL FAST
- These errors typically occur at startup
- Cannot be recovered at runtime
- Should halt initialization and report clearly

**Example**:
```python
from coffee_maker.exceptions import ConfigError, APIKeyMissingError
from coffee_maker.config.manager import ConfigManager

try:
    api_key = ConfigManager.get_openai_api_key(required=True)
except APIKeyMissingError as e:
    logger.error(
        "Cannot start: OpenAI API key missing. "
        "Set OPENAI_API_KEY environment variable."
    )
    raise  # Halt startup
```

**Best Practices**:
- Validate all configuration at startup
- Provide clear instructions for fixing configuration issues
- Don't attempt runtime recovery for config errors

---

### ProviderError

**Characteristics**: AI provider failures, unavailable models, provider configuration issues

**Recovery Strategy**: FALLBACK TO ALTERNATE PROVIDER
- Use fallback provider chain (e.g., OpenAI → Gemini → Anthropic)
- Log provider failures with context
- Track provider health metrics

**Example**:
```python
from coffee_maker.exceptions import (
    ProviderError,
    ProviderUnavailableError,
    AllProvidersFailedError,
)

def execute_with_fallback(prompt: str, providers: list):
    """Execute prompt with provider fallback chain."""
    last_error = None

    for provider in providers:
        try:
            logger.info(f"Attempting provider: {provider.name}")
            result = provider.execute_prompt(prompt)
            logger.info(f"Success with provider: {provider.name}")
            return result

        except ProviderUnavailableError as e:
            last_error = e
            log_error(
                logger,
                f"Provider {provider.name} unavailable, trying next",
                e,
                context={"provider": provider.name}
            )
            continue

    # All providers failed
    raise AllProvidersFailedError(
        f"All {len(providers)} providers failed",
        details={"last_error": str(last_error)}
    )
```

**Best Practices**:
- Implement provider health checks
- Use fallback chains defined in configuration
- Track provider availability metrics
- Consider provider cost when ordering fallback chain

---

### ResourceError

**Characteristics**: Rate limits, quota exceeded, budget limits, cost overruns

**Recovery Strategy**: RETRY WITH BACKOFF + FALLBACK
- Implement exponential backoff for rate limits
- Switch to alternate provider if quota exceeded
- Respect `retry_after` headers
- Circuit breaker for repeated failures

**Example**:
```python
import time
from coffee_maker.exceptions import RateLimitError, QuotaExceededError

def execute_with_retry(provider, prompt, max_retries=3):
    """Execute with exponential backoff on rate limits."""
    for attempt in range(max_retries):
        try:
            return provider.execute_prompt(prompt)

        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed

            # Exponential backoff
            wait_time = e.retry_after or (2 ** attempt)
            logger.warning(
                f"Rate limited, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})",
                extra={"provider": e.provider, "wait_time": wait_time}
            )
            time.sleep(wait_time)

        except QuotaExceededError as e:
            # Cannot retry, need different provider
            log_error(logger, "Quota exceeded, switching provider", e)
            raise
```

**Best Practices**:
- Respect `retry_after` when provided
- Use exponential backoff: 1s, 2s, 4s, 8s, 16s
- Add jitter to avoid thundering herd
- Track rate limit events for capacity planning
- Consider budget limits before retrying expensive operations

---

### ModelError

**Characteristics**: Model unavailable, context length exceeded

**Recovery Strategy**: FALLBACK TO ALTERNATE MODEL
- For context length errors, try model with larger context window
- For unavailable models, fallback to similar model
- Consider truncating input if context length exceeded

**Example**:
```python
from coffee_maker.exceptions import ContextLengthError, ModelNotAvailableError

def execute_with_model_fallback(prompt: str, provider):
    """Handle model-specific errors with fallback."""
    try:
        return provider.execute_prompt(prompt)

    except ContextLengthError as e:
        logger.warning(
            f"Context length exceeded ({e.details.get('tokens')} tokens), "
            f"trying larger model"
        )
        # Try larger context model
        provider.model = "gpt-4-turbo-preview"  # 128k context
        return provider.execute_prompt(prompt)

    except ModelNotAvailableError as e:
        logger.warning(f"Model {e.details.get('model')} unavailable, using fallback")
        # Fallback to similar model
        provider.model = "gpt-4"
        return provider.execute_prompt(prompt)
```

**Best Practices**:
- Validate context length before making API calls
- Define fallback models in configuration
- Consider truncating input (with user consent) rather than failing
- Log token usage to prevent repeated context length errors

---

### FileError

**Characteristics**: File not found, permission denied, disk full

**Recovery Strategy**: RETRY + USER NOTIFICATION
- Retry transient filesystem errors (disk busy, lock contention)
- Report permanent errors clearly to user
- Ensure cleanup on partial writes

**Example**:
```python
from coffee_maker.exceptions import FileError, FileOperationError
from coffee_maker.utils.logging_utils import log_error

def safe_write_file(path: str, content: str, max_retries=3):
    """Write file with retry on transient errors."""
    for attempt in range(max_retries):
        try:
            # Atomic write: write to temp file, then move
            temp_path = f"{path}.tmp"
            with open(temp_path, 'w') as f:
                f.write(content)
            os.rename(temp_path, path)
            logger.info(f"File written: {path}")
            return

        except PermissionError as e:
            # Permanent error, don't retry
            log_error(logger, f"Permission denied: {path}", e)
            raise FileOperationError(
                f"Cannot write to {path}: permission denied",
                details={"path": path}
            ) from e

        except OSError as e:
            if attempt == max_retries - 1:
                log_error(logger, f"Failed to write {path} after {max_retries} attempts", e)
                raise FileOperationError(
                    f"Failed to write {path}: {e}",
                    details={"path": path, "attempts": max_retries}
                ) from e

            logger.warning(f"Transient error writing {path}, retrying...")
            time.sleep(0.5 * (attempt + 1))
```

**Best Practices**:
- Use atomic writes (temp file + rename)
- Clean up temp files on failure
- Check disk space before large writes
- Validate file permissions early
- Use file locking for concurrent access

---

### DaemonError

**Characteristics**: Daemon crashes, invalid state transitions

**Recovery Strategy**: RESTART + STATE RECOVERY
- Automatically restart daemon on crash (with crash limit)
- Persist daemon state for recovery
- Validate state transitions
- Alert on repeated crashes

**Example**:
```python
from coffee_maker.exceptions import DaemonCrashError, DaemonStateError

class DaemonManager:
    MAX_CRASHES = 5

    def run_with_recovery(self):
        """Run daemon with automatic crash recovery."""
        crash_count = 0

        while crash_count < self.MAX_CRASHES:
            try:
                logger.info(f"Starting daemon (crash count: {crash_count})")
                self.daemon.run()
                break  # Normal exit

            except DaemonCrashError as e:
                crash_count += 1
                log_error(
                    logger,
                    f"Daemon crashed ({crash_count}/{self.MAX_CRASHES})",
                    e,
                    context={
                        "crash_count": crash_count,
                        "max_crashes": self.MAX_CRASHES,
                    }
                )

                if crash_count >= self.MAX_CRASHES:
                    logger.critical(
                        f"Daemon crashed {self.MAX_CRASHES} times, stopping"
                    )
                    raise

                # Wait before restart (exponential backoff)
                wait_time = min(2 ** crash_count, 60)
                logger.info(f"Restarting daemon in {wait_time}s...")
                time.sleep(wait_time)

                # Recover state
                self._recover_state()

    def _recover_state(self):
        """Recover daemon state from persistence."""
        try:
            state = self.load_state()
            self.daemon.restore_state(state)
            logger.info("Daemon state recovered")
        except Exception as e:
            log_error(logger, "Failed to recover state, starting fresh", e)
```

**Best Practices**:
- Implement crash limits to prevent infinite restart loops
- Persist daemon state regularly
- Use exponential backoff for restart delays
- Alert operations team on repeated crashes
- Validate state before restoration
- Log all state transitions for debugging

---

## Retry Patterns

### Exponential Backoff with Jitter

Recommended for rate limits and transient failures:

```python
import random
import time

def exponential_backoff_with_jitter(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate backoff delay with jitter.

    Args:
        attempt: Attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds with jitter added
    """
    # Exponential backoff: base_delay * 2^attempt
    delay = min(base_delay * (2 ** attempt), max_delay)

    # Add jitter: ±25% of delay
    jitter = delay * 0.25 * (2 * random.random() - 1)

    return delay + jitter


def retry_with_backoff(func, max_retries=5, retriable_exceptions=(Exception,)):
    """Retry function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum retry attempts
        retriable_exceptions: Tuple of exceptions to retry on

    Returns:
        Function result

    Raises:
        Last exception if all retries exhausted
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return func()
        except retriable_exceptions as e:
            last_exception = e

            if attempt == max_retries - 1:
                logger.error(f"All {max_retries} retries exhausted")
                raise

            delay = exponential_backoff_with_jitter(attempt)
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed, retrying in {delay:.2f}s",
                extra={"exception": str(e), "delay": delay}
            )
            time.sleep(delay)
```

### Linear Backoff

For predictable retry intervals:

```python
def linear_backoff(attempt: int, delay: float = 1.0) -> float:
    """Linear backoff: delay * attempt."""
    return delay * (attempt + 1)
```

### Fixed Delay

For simple retry scenarios:

```python
def fixed_delay(delay: float = 1.0) -> float:
    """Fixed delay between retries."""
    return delay
```

---

## Circuit Breaker Pattern

Prevent cascading failures by temporarily disabling failing operations:

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for failing operations."""

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
        self.opened_at = None

    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker."""
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if datetime.now() - self.opened_at > timedelta(seconds=self.timeout):
                logger.info("Circuit breaker: transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

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


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
```

**Usage**:
```python
# Create circuit breaker for OpenAI provider
openai_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    success_threshold=2,
)

def call_openai_with_breaker(prompt: str):
    """Call OpenAI through circuit breaker."""
    try:
        return openai_breaker.call(
            openai_provider.execute_prompt,
            prompt
        )
    except CircuitBreakerOpenError:
        logger.warning("OpenAI circuit breaker open, using fallback")
        return gemini_provider.execute_prompt(prompt)
```

---

## Fallback Mechanisms

### Provider Fallback Chain

Defined in `config/ai_providers_config.yaml`:

```yaml
fallback_chain:
  - provider: openai
    model: gpt-4-turbo
  - provider: gemini
    model: gemini-1.5-pro
  - provider: anthropic
    model: claude-3-opus
```

**Implementation**:
```python
from coffee_maker.ai_providers.fallback_strategy import FallbackStrategy

fallback = FallbackStrategy(config)
result = fallback.execute_with_fallback(prompt)
```

### Degraded Mode Operation

For non-critical features, allow degraded operation:

```python
def get_feature_status(feature: str) -> dict:
    """Get feature status with fallback."""
    try:
        # Try primary data source (API)
        return api_client.get_status(feature)
    except ProviderError as e:
        logger.warning(f"API unavailable, using cached data: {e}")
        # Fallback to cached data
        return cache.get_status(feature)
```

### Default Values

Provide sensible defaults when optional features fail:

```python
def get_completion_with_defaults(prompt: str) -> str:
    """Get AI completion with sensible defaults."""
    try:
        result = provider.execute_prompt(prompt)
        return result.content
    except AllProvidersFailedError as e:
        log_error(logger, "All providers failed, using default response", e)
        return "I'm currently unable to process your request. Please try again later."
```

---

## Logging and Monitoring

### Structured Error Logging

Always use structured logging for errors:

```python
from coffee_maker.utils.logging_utils import log_error, LogFormatter

try:
    result = operation()
except ProviderError as e:
    log_error(
        logger,
        LogFormatter.error("Provider operation failed"),
        e,
        context={
            "provider": provider.name,
            "model": provider.model,
            "retry_count": retry_count,
            "cost_so_far": total_cost,
        }
    )
```

### Metrics to Track

**Error Rates**:
- Errors by type (ConfigError, ProviderError, etc.)
- Errors by component (daemon, AI provider, file operations)
- Error rate per minute/hour

**Recovery Success**:
- Retry success rate
- Fallback usage frequency
- Circuit breaker state transitions

**Performance Impact**:
- Retry delay total
- Fallback latency
- Cost of retries

### Alerting Thresholds

**Critical Alerts**:
- Daemon crash count > 3 in 1 hour
- All providers failing
- Circuit breaker open for > 5 minutes
- Budget exceeded

**Warning Alerts**:
- Error rate > 10% for 5 minutes
- Retry rate > 20%
- Single provider failing
- Budget at 80%

---

## Examples

### Example 1: AI Provider Call with Full Error Handling

```python
from coffee_maker.exceptions import (
    ProviderError,
    RateLimitError,
    QuotaExceededError,
    AllProvidersFailedError,
)
from coffee_maker.utils.logging_utils import log_error, log_duration

def execute_task_with_error_handling(task: str) -> str:
    """Execute AI task with comprehensive error handling."""
    providers = [openai_provider, gemini_provider, anthropic_provider]
    max_retries = 3

    for provider in providers:
        for attempt in range(max_retries):
            try:
                with log_duration(logger, f"{provider.name} execution"):
                    result = provider.execute_prompt(task)
                    logger.info(
                        f"Task completed successfully with {provider.name}",
                        extra={
                            "provider": provider.name,
                            "tokens": result.usage["input_tokens"] + result.usage["output_tokens"],
                        }
                    )
                    return result.content

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = e.retry_after or (2 ** attempt)
                    logger.warning(
                        f"Rate limited, retrying in {wait_time}s",
                        extra={"provider": provider.name, "attempt": attempt + 1}
                    )
                    time.sleep(wait_time)
                else:
                    log_error(
                        logger,
                        f"Rate limit exhausted for {provider.name}, trying next provider",
                        e
                    )
                    break

            except QuotaExceededError as e:
                log_error(logger, f"Quota exceeded for {provider.name}, trying next provider", e)
                break

            except ProviderError as e:
                log_error(logger, f"Provider {provider.name} failed", e)
                break

    # All providers failed
    raise AllProvidersFailedError("All providers exhausted")
```

### Example 2: File Operation with Retry

```python
from coffee_maker.exceptions import FileOperationError
from coffee_maker.utils.logging_utils import log_error

def write_checkpoint_with_retry(path: str, data: dict, max_retries: int = 3) -> None:
    """Write checkpoint file with retry logic."""
    import json

    for attempt in range(max_retries):
        temp_path = f"{path}.tmp"

        try:
            # Atomic write
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, path)

            logger.info(f"Checkpoint written: {path}")
            return

        except OSError as e:
            if attempt == max_retries - 1:
                log_error(
                    logger,
                    f"Failed to write checkpoint after {max_retries} attempts",
                    e,
                    context={"path": path}
                )
                raise FileOperationError(f"Cannot write checkpoint: {e}") from e

            logger.warning(f"Write failed (attempt {attempt + 1}), retrying...")
            time.sleep(0.5 * (attempt + 1))

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
```

### Example 3: Daemon with Crash Recovery

```python
from coffee_maker.exceptions import DaemonCrashError
from coffee_maker.utils.logging_utils import log_error, LogFormatter

class ResilientDaemon:
    """Daemon with automatic crash recovery."""

    MAX_CRASHES = 5

    def run_with_recovery(self):
        """Run daemon with crash recovery."""
        crash_count = 0

        while crash_count < self.MAX_CRASHES:
            try:
                logger.info(LogFormatter.in_progress("Starting daemon"))
                self._run_daemon()
                logger.info(LogFormatter.success("Daemon exited normally"))
                break

            except KeyboardInterrupt:
                logger.info("Daemon interrupted by user")
                break

            except Exception as e:
                crash_count += 1
                log_error(
                    logger,
                    LogFormatter.error(f"Daemon crashed ({crash_count}/{self.MAX_CRASHES})"),
                    e,
                    context={"crash_count": crash_count}
                )

                if crash_count >= self.MAX_CRASHES:
                    raise DaemonCrashError(crash_count, self.MAX_CRASHES, e)

                # Exponential backoff
                wait_time = min(2 ** crash_count, 60)
                logger.info(f"Restarting in {wait_time}s...")
                time.sleep(wait_time)

    def _run_daemon(self):
        """Main daemon loop."""
        # Implementation...
        pass
```

---

## Summary

**Key Takeaways**:

1. **Use the exception hierarchy**: Catch specific exceptions for targeted recovery
2. **Implement retry logic**: Exponential backoff for transient failures
3. **Use fallback chains**: Multiple providers/models for resilience
4. **Log with context**: Structured logging enables debugging and monitoring
5. **Fail gracefully**: Provide useful error messages and degraded operation
6. **Monitor and alert**: Track error rates and recovery success

**Quick Reference**:

| Error Type | Recovery Strategy | Retry? | Fallback? |
|------------|------------------|--------|-----------|
| ConfigError | Fail fast | No | No |
| ProviderError | Fallback chain | Yes | Yes |
| ResourceError | Exponential backoff | Yes | Yes |
| ModelError | Model fallback | Maybe | Yes |
| FileError | Retry transient | Yes | No |
| DaemonError | Restart daemon | N/A | N/A |

**Related Documentation**:
- `coffee_maker/exceptions.py` - Exception hierarchy
- `coffee_maker/utils/logging_utils.py` - Logging utilities
- `config/ai_providers_config.yaml` - Provider configuration
- `docs/ROADMAP.md` - US-021 Architecture Improvements
