# Retry Patterns Documentation

## Overview

This project implements centralized retry logic with full Langfuse observability for handling transient failures in network operations, API calls, and database operations.

**Module**: `coffee_maker.langchain_observe.retry_utils`

## Core Components

### 1. `@with_retry` Decorator

General-purpose retry decorator with exponential backoff and Langfuse integration.

**Features**:
- Configurable retry attempts (default: 3)
- Exponential backoff with configurable base (default: 2.0s)
- Maximum backoff limit (default: 60s)
- Selective exception retry with type filtering
- Custom retry predicates for advanced logic
- Callback support for custom actions on retry
- Full Langfuse observability (each retry logged as span)
- Dual logging to Python logger and Langfuse

**Basic Usage**:
```python
from coffee_maker.langchain_observe.retry_utils import with_retry

@with_retry(max_attempts=3, backoff_base=2.0)
def fetch_data_from_api():
    """Flaky API call with automatic retry."""
    response = requests.get("https://api.example.com/data")
    return response.json()
```

**Advanced Usage with Custom Predicate**:
```python
def is_rate_limit_error(error):
    """Check if error is a rate limit error."""
    return "rate limit" in str(error).lower()

@with_retry(
    max_attempts=10,
    backoff_base=2.0,
    max_backoff=60.0,
    retriable_exceptions=(ConnectionError, TimeoutError),
    should_retry_predicate=is_rate_limit_error,
)
def rate_limited_api_call():
    """API call with intelligent rate limit retry."""
    return api_client.fetch()
```

**With Callback**:
```python
def on_retry_callback(error, attempt):
    """Called before each retry attempt."""
    logger.info(f"Retry {attempt} due to {error}")
    # Custom logic here

@with_retry(
    max_attempts=5,
    backoff_base=2.0,
    on_retry=on_retry_callback,
)
def operation_with_notifications():
    """Operation that notifies on retry."""
    return perform_operation()
```

### 2. `@with_conditional_retry` Decorator

Specialized retry decorator for scenarios requiring cleanup before retry.

**Features**:
- Conditional retry based on error inspection
- Optional cleanup function execution before retry
- Useful for resolving conflicts (e.g., GitHub pending reviews)
- Exponential backoff support

**Usage Pattern**:
```python
from coffee_maker.langchain_observe.retry_utils import with_conditional_retry

def create_retry_condition(resource):
    """Create a condition checker with access to resource context."""

    def check_condition(error):
        """Check if error requires retry and return cleanup function.

        Returns:
            Tuple[bool, Optional[Callable]]: (should_retry, cleanup_func)
        """
        if not should_retry_this_error(error):
            return False, None

        # Define cleanup function with access to resource
        def cleanup():
            clear_resource_state(resource)

        return True, cleanup

    return check_condition

@with_conditional_retry(
    condition_check=create_retry_condition(my_resource),
    max_attempts=2,
    backoff_base=1.0,
)
def operation():
    """Operation with conditional cleanup on retry."""
    return perform_operation()
```

### 3. `RetryExhausted` Exception

Raised when all retry attempts have been exhausted.

**Attributes**:
- `original_error`: The final exception that caused failure
- `attempts`: Number of attempts made

**Usage**:
```python
from coffee_maker.langchain_observe.retry_utils import RetryExhausted, with_retry

try:
    result = flaky_operation()
except RetryExhausted as e:
    logger.error(f"Operation failed after {e.attempts} attempts")
    logger.error(f"Final error: {e.original_error}")
    # Handle permanent failure
```

### 4. `RetryConfig` Class

Configuration object for retry behavior (used internally by decorators).

**Attributes**:
- `max_attempts`: Maximum attempts (including initial call)
- `backoff_base`: Base for exponential backoff (seconds)
- `max_backoff`: Maximum backoff time (seconds)
- `retriable_exceptions`: Tuple of exception types to retry
- `should_retry_predicate`: Optional function to determine if error is retriable

**Methods**:
- `calculate_backoff(attempt: int) -> float`: Calculate backoff for given attempt
- `is_retriable(error: Exception) -> bool`: Determine if error should trigger retry

## Implementation Examples

### Example 1: Langfuse API Calls

**File**: `coffee_maker/langchain_observe/analytics/exporter.py`

```python
from coffee_maker.langchain_observe.retry_utils import RetryExhausted, with_retry

@with_retry(
    max_attempts=3,
    backoff_base=2.0,
    retriable_exceptions=(ConnectionError, TimeoutError, Exception),
)
def _fetch_traces_from_langfuse(self, from_timestamp, to_timestamp):
    """Fetch traces from Langfuse API with automatic retry.

    Will retry up to 3 times with exponential backoff (1s, 2s, 4s).
    """
    trace_list = self.langfuse.get_traces(
        from_timestamp=from_timestamp.isoformat(),
        to_timestamp=to_timestamp.isoformat(),
        limit=self.config.export_batch_size,
    )
    return [trace.dict() for trace in trace_list.data]

# Usage with error handling
try:
    traces = self._fetch_traces_from_langfuse(from_ts, to_ts)
except RetryExhausted as e:
    logger.error(f"Failed to fetch traces after all retries: {e.original_error}")
    stats["errors"] += 1
```

### Example 2: GitHub PR Review Comments

**File**: `coffee_maker/utils/github.py`

```python
from coffee_maker.langchain_observe.retry_utils import with_conditional_retry

def _create_pending_review_retry_condition(pr, current_user_login):
    """Create retry condition for pending review conflicts."""

    def check_pending_review_conflict(error):
        """Check if error is pending review conflict and return cleanup."""
        if not isinstance(error, GithubException):
            return False, None

        if error.status != 422 or not _is_pending_review_conflict(error):
            return False, None

        logger.info("Detected pending review conflict. Will cleanup and retry.")

        def cleanup():
            """Clear pending review before retry."""
            cleared = _clear_pending_review(pr, current_user_login)
            if not cleared:
                logger.warning("Failed to clear pending review")

        return True, cleanup

    return check_pending_review_conflict

@observe
def post_suggestion_in_pr_review(repo_full_name, pr_number, file_path, ...):
    """Post code suggestion with automatic pending review resolution."""
    pr = repo.get_pull(pr_number)
    current_user_login = g.get_user().login

    # Create retry condition
    retry_condition = _create_pending_review_retry_condition(pr, current_user_login)

    # Post comment with retry
    @with_conditional_retry(
        condition_check=retry_condition,
        max_attempts=2,
        backoff_base=1.0,
    )
    def _post_review_comment():
        pr.create_review_comment(**comment_kwargs)

    _post_review_comment()
```

## Retry Timing

### Exponential Backoff Calculation

For `backoff_base = 2.0`:

| Attempt | Backoff Time | Formula |
|---------|--------------|---------|
| 1 (initial) | 0s | - |
| 2 (1st retry) | 1s | 2^0 = 1 |
| 3 (2nd retry) | 2s | 2^1 = 2 |
| 4 (3rd retry) | 4s | 2^2 = 4 |
| 5 (4th retry) | 8s | 2^3 = 8 |

**Max Backoff Limit**: If calculated backoff exceeds `max_backoff`, it's capped at that value.

Example with `max_backoff = 10.0` and `backoff_base = 10.0`:
- Attempt 2: 1s (10^0)
- Attempt 3: 10s (10^1, capped at 10)
- Attempt 4: 10s (10^2 = 100, capped at 10)

## Langfuse Observability

### Automatic Span Creation

Each retry operation creates Langfuse spans for observability:

1. **`_log_retry_attempt`**: Span created for each retry attempt with metadata:
   - Function name
   - Attempt number
   - Max attempts
   - Error type and message
   - Backoff duration

2. **`_log_retry_success`**: Span created when retry eventually succeeds:
   - Function name
   - Successful attempt number
   - Total time spent

3. **`_log_retry_exhausted`**: Span created when all retries fail:
   - Function name
   - Total attempts
   - Total time spent
   - Final error

### Viewing in Langfuse

Navigate to your Langfuse dashboard to see:
- Retry attempts as nested spans
- Retry timing and backoff patterns
- Success/failure rates
- Error patterns over time

## Best Practices

### 1. Choose Appropriate Max Attempts

```python
# Quick operations: 2-3 attempts
@with_retry(max_attempts=2)
def quick_api_call():
    pass

# Critical operations with transient failures: 5-10 attempts
@with_retry(max_attempts=10)
def critical_with_rate_limits():
    pass
```

### 2. Set Realistic Backoff

```python
# Fast recovery for temporary network blips
@with_retry(max_attempts=3, backoff_base=1.0)
def network_operation():
    pass

# Longer backoff for rate-limited APIs
@with_retry(max_attempts=10, backoff_base=5.0, max_backoff=300.0)
def rate_limited_api():
    pass
```

### 3. Use Specific Exception Types

```python
# Too broad - will retry non-transient errors
@with_retry(retriable_exceptions=(Exception,))
def operation():
    pass

# Better - only retry transient failures
@with_retry(retriable_exceptions=(ConnectionError, TimeoutError, RequestException))
def operation():
    pass
```

### 4. Implement Smart Retry Predicates

```python
def is_transient_database_error(error):
    """Only retry deadlocks and connection losses."""
    if isinstance(error, OperationalError):
        msg = str(error).lower()
        return "deadlock" in msg or "connection" in msg
    return False

@with_retry(
    retriable_exceptions=(OperationalError,),
    should_retry_predicate=is_transient_database_error,
)
def database_operation():
    pass
```

### 5. Handle RetryExhausted Appropriately

```python
from coffee_maker.langchain_observe.retry_utils import RetryExhausted

try:
    result = critical_operation()
except RetryExhausted as e:
    # Log the failure
    logger.error(f"Critical operation failed after {e.attempts} attempts")
    logger.error(f"Final error: {e.original_error}")

    # Take appropriate action
    # - Alert monitoring system
    # - Fallback to alternative approach
    # - Store for manual review
    # - Return degraded response

    raise  # Re-raise if caller needs to know
```

### 6. Use Conditional Retry for Stateful Operations

```python
# Good: Clear state before retry
def create_cleanup(resource):
    def check_conflict(error):
        if is_conflict(error):
            return True, lambda: clear_state(resource)
        return False, None
    return check_conflict

@with_conditional_retry(condition_check=create_cleanup(resource))
def stateful_operation():
    pass

# Bad: Retry without cleanup, leading to repeated conflicts
@with_retry()
def stateful_operation():
    pass  # Will keep hitting same conflict
```

## Testing

Comprehensive test suite in `tests/unit/test_retry_utils.py`:

- RetryConfig: 10 tests
- with_retry: 11 tests
- with_conditional_retry: 7 tests
- RetryExhausted: 3 tests
- Integration scenarios: 2 tests

**Run tests**:
```bash
pytest tests/unit/test_retry_utils.py -v
```

## Migration Guide

### From Manual Retry to `@with_retry`

**Before**:
```python
def fetch_data():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            return api.get_data()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)
```

**After**:
```python
@with_retry(max_attempts=3, backoff_base=2.0)
def fetch_data():
    return api.get_data()
```

### From Custom Retry Logic to `@with_conditional_retry`

**Before**:
```python
def post_comment():
    for attempt in range(2):
        try:
            return pr.create_comment(text)
        except GithubException as e:
            if "pending review" in str(e) and attempt == 0:
                clear_pending_reviews()
                time.sleep(1)
            else:
                raise
```

**After**:
```python
def check_pending(error):
    if isinstance(error, GithubException) and "pending review" in str(error):
        return True, clear_pending_reviews
    return False, None

@with_conditional_retry(condition_check=check_pending, max_attempts=2)
def post_comment():
    return pr.create_comment(text)
```

## Performance Considerations

### Total Retry Time

Calculate maximum time for operation:

```
total_time = operation_time * attempts + sum(backoff_times)
```

Example with `max_attempts=4`, `backoff_base=2.0`, `operation_time=1s`:
```
total_time = (1s * 4) + (1s + 2s + 4s) = 4s + 7s = 11s
```

### Memory Usage

Each retry decorator adds minimal memory overhead:
- Closure for configuration (~100 bytes)
- Langfuse span metadata (~1KB per retry)

### Langfuse Impact

Each retry creates 1-3 Langfuse spans:
- Minimal performance impact (~5-10ms per span)
- Spans are created asynchronously
- No blocking on Langfuse availability

## Future Enhancements

Potential improvements to consider:

1. **Jitter**: Add randomization to backoff to prevent thundering herd
2. **Circuit Breaker**: Fail fast after repeated failures
3. **Retry Budget**: Limit total retry time across all operations
4. **Adaptive Backoff**: Adjust backoff based on error patterns
5. **Metrics**: Track retry success/failure rates

## Related Documentation

- [Exponential Backoff Implementation](exponential_backoff_implementation.md) - Original LLM-specific retry
- [Error Handling Strategy](error_handling_and_fallback_strategy.md) - General error handling
- [Refactoring Analysis](refactoring_analysis.md) - Refactoring rationale

## Change History

- **2025-01-09**: Initial implementation of centralized retry utilities
  - Created `coffee_maker/langchain_observe/retry_utils.py`
  - Applied to GitHub PR operations and Langfuse API calls
  - Full test coverage with 30+ tests
