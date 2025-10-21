# GUIDELINE-001: Error Handling with Custom Exception Hierarchy

**Category**: Best Practice

**Applies To**: All Python modules in coffee_maker/

**Author**: architect agent

**Date Created**: 2025-10-16

**Last Updated**: 2025-10-16

**Status**: Active

**Related ADRs**: None (derived from existing code patterns in exceptions.py)

**Related Specs**: N/A

---

## Overview

This guideline describes how to implement error handling in the Coffee Maker Agent codebase using our custom exception hierarchy. It ensures consistent error handling, rich error messages with context, and maintainable code.

---

## When to Use

Use this error handling pattern when:

- Implementing any module that could encounter errors
- Handling user input that could be invalid
- Performing operations that could fail (file I/O, network calls, database, AI providers)
- Any code where you need to provide meaningful error messages to users
- When you need to distinguish between different types of failures

**Example Scenarios**:
- Loading configuration files (use ConfigError)
- Calling AI providers (use ProviderError)
- Reading/writing files (use FileError)
- Managing daemon lifecycle (use DaemonError)
- Handling rate limits (use RateLimitError)

---

## When NOT to Use

Do NOT use this error handling pattern when:

- In simple data classes (they should be straightforward)
- For expected flow control (use if/else, not exceptions)
- In test fixtures (use pytest's built-in exception handling)
- When performance is absolutely critical and errors are extremely rare

**Anti-Example**: Don't use exceptions to control normal flow:
```python
# ❌ Bad: Using exceptions for flow control
try:
    result = get_cached_value(key)
except KeyError:
    result = compute_expensive_value(key)

# ✅ Good: Use if/else for expected cases
result = get_cached_value(key)
if result is None:
    result = compute_expensive_value(key)
```

---

## The Pattern

### Explanation

Our error handling pattern uses:

1. **Custom Exception Hierarchy**: All exceptions inherit from `CoffeeMakerError`
   ```
   CoffeeMakerError (base)
   ├── ConfigError
   ├── ProviderError
   ├── ResourceError
   ├── ModelError
   ├── FileError
   └── DaemonError
   ```

2. **Rich Error Messages**: Include context in exception messages
   - What went wrong
   - What was being attempted
   - Relevant data (file paths, provider names, etc.)

3. **Optional Details Dict**: Store additional context for logging/debugging
   ```python
   raise CoffeeMakerError("Failed to load config", details={
       "filepath": filepath,
       "error": str(e),
       "user": current_user
   })
   ```

4. **Defensive Programming**: Validate inputs early, fail fast
5. **Graceful Degradation**: Catch exceptions at service boundaries
6. **User-Friendly Messages**: Translate technical errors to readable messages
7. **Comprehensive Logging**: Log all exceptions with context

### Principles

1. **Fail Fast**: Validate inputs at function entry, don't wait for errors deep in code
2. **Be Specific**: Use specific exception types (ConfigError, not generic Exception)
3. **Add Context**: Include relevant data in error messages (file paths, IDs, etc.)
4. **Log Everything**: Log exceptions with full context for debugging
5. **User-Friendly**: Translate technical errors to readable messages for users
6. **Exception Chaining**: Use `from e` to preserve stack traces

---

## Implementation

### Step-by-Step Guide

1. **Import Custom Exceptions**: Import from centralized `exceptions.py`
   ```python
   from coffee_maker.exceptions import (
       CoffeeMakerError,
       ConfigError,
       ProviderError,
       FileError,
   )
   ```

2. **Validate Inputs Early**: Check inputs at function entry
   ```python
   def load_config(filepath: str) -> dict:
       """Load configuration from file."""
       # Validate input
       if not filepath:
           raise ConfigError("filepath cannot be empty")

       if not filepath.endswith((".json", ".yaml", ".yml")):
           raise ConfigError(
               f"Invalid config file extension: {filepath}. "
               "Expected .json, .yaml, or .yml"
           )

       # ... rest of implementation
   ```

3. **Provide Contextual Error Messages**: Include relevant data
   ```python
   def get_ai_response(provider: str, prompt: str) -> str:
       """Get AI response from provider."""
       if provider not in SUPPORTED_PROVIDERS:
           raise ProviderError(
               f"Unsupported provider '{provider}'. "
               f"Supported providers: {', '.join(SUPPORTED_PROVIDERS)}",
               details={"provider": provider, "supported": SUPPORTED_PROVIDERS}
           )

       # ... implementation
   ```

4. **Use Exception Chaining**: Preserve stack traces with `from e`
   ```python
   def load_json_file(filepath: str) -> dict:
       """Load JSON file."""
       try:
           with open(filepath, "r") as f:
               return json.load(f)
       except FileNotFoundError as e:
           raise FileError(
               f"Config file not found: {filepath}",
               details={"filepath": filepath}
           ) from e
       except json.JSONDecodeError as e:
           raise FileError(
               f"Invalid JSON in config file: {filepath}",
               details={"filepath": filepath, "error": str(e)}
           ) from e
       except Exception as e:
           # Catch unexpected errors and add context
           logger.exception("Unexpected error loading JSON", extra={"filepath": filepath})
           raise FileError(
               f"Failed to load config file: {filepath}",
               details={"filepath": filepath, "error": str(e)}
           ) from e
   ```

5. **Catch at Service Boundaries**: Handle exceptions at CLI/API layer
   ```python
   def cli_load_config(filepath: str) -> None:
       """CLI command to load config."""
       try:
           config = load_config(filepath)
           print(f"✅ Config loaded from {filepath}")
       except ConfigError as e:
           print(f"❌ Config error: {e}")
           if e.details:
               print(f"   Details: {e.details}")
           sys.exit(1)
       except FileError as e:
           print(f"❌ File error: {e}")
           logger.exception("Failed to load config file")
           sys.exit(1)
   ```

6. **Log Exceptions with Context**: Use structured logging
   ```python
   def dangerous_operation(param: str) -> None:
       """Perform operation that might fail."""
       try:
           # ... implementation
       except Exception as e:
           logger.exception(
               "Operation failed",
               extra={
                   "param": param,
                   "function": "dangerous_operation",
                   "traceback": traceback.format_exc()
               }
           )
           raise CoffeeMakerError(f"Operation failed for param: {param}") from e
   ```

### Code Examples

#### Good Example: Proper Error Handling in AI Provider

```python
from coffee_maker.exceptions import ProviderError, RateLimitError, ModelError
import logging

logger = logging.getLogger(__name__)


def call_ai_provider(
    provider_name: str,
    model: str,
    prompt: str,
    max_tokens: int = 1000
) -> str:
    """
    Call AI provider with prompt.

    Args:
        provider_name: Provider to use (claude, gemini, openai)
        model: Model identifier
        prompt: User prompt
        max_tokens: Maximum tokens in response

    Returns:
        AI response text

    Raises:
        ProviderError: If provider is invalid or unavailable
        RateLimitError: If rate limit exceeded
        ModelError: If model is unavailable or context too long
    """
    # 1. Validate inputs early
    if not provider_name:
        raise ProviderError("provider_name cannot be empty")

    if provider_name not in SUPPORTED_PROVIDERS:
        raise ProviderError(
            f"Unsupported provider: {provider_name}",
            details={"provider": provider_name, "supported": list(SUPPORTED_PROVIDERS.keys())}
        )

    if not prompt or not prompt.strip():
        raise ProviderError("prompt cannot be empty")

    if max_tokens <= 0:
        raise ProviderError(
            f"max_tokens must be positive: {max_tokens}",
            details={"max_tokens": max_tokens}
        )

    # 2. Get provider instance
    try:
        provider = get_provider(provider_name)
    except Exception as e:
        logger.error(f"Failed to get provider: {provider_name}", extra={"error": str(e)})
        raise ProviderError(
            f"Provider unavailable: {provider_name}",
            details={"provider": provider_name, "error": str(e)}
        ) from e

    # 3. Call provider with specific error handling
    try:
        response = provider.generate(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens
        )
        return response.text

    except RateLimitException as e:
        # Convert provider-specific exception to our exception
        logger.warning(
            f"Rate limit exceeded for {provider_name}",
            extra={"provider": provider_name, "model": model}
        )
        raise RateLimitError(
            provider=provider_name,
            limit_type="requests",
            retry_after=e.retry_after
        ) from e

    except ModelNotFoundException as e:
        logger.error(
            f"Model not found: {model}",
            extra={"provider": provider_name, "model": model}
        )
        raise ModelError(
            f"Model not available: {model} on {provider_name}",
            details={"provider": provider_name, "model": model}
        ) from e

    except ContextLengthException as e:
        logger.error(
            f"Context too long for {model}",
            extra={"provider": provider_name, "model": model, "prompt_length": len(prompt)}
        )
        raise ModelError(
            f"Prompt too long for {model}: {len(prompt)} chars",
            details={"provider": provider_name, "model": model, "prompt_length": len(prompt)}
        ) from e

    except Exception as e:
        # Catch unexpected errors
        logger.exception(
            "Unexpected error calling AI provider",
            extra={
                "provider": provider_name,
                "model": model,
                "prompt_length": len(prompt)
            }
        )
        raise ProviderError(
            f"Failed to call {provider_name}: {type(e).__name__}",
            details={"provider": provider_name, "model": model, "error": str(e)}
        ) from e
```

**Why This is Good**:
- ✅ Validates all inputs at function entry (fail fast)
- ✅ Uses specific exception types (ProviderError, RateLimitError, ModelError)
- ✅ Provides rich error messages with context
- ✅ Includes details dict for logging/debugging
- ✅ Logs exceptions with structured data
- ✅ Uses exception chaining (`from e`) to preserve stack traces
- ✅ Documents exceptions in docstring
- ✅ Converts provider-specific exceptions to our hierarchy
- ✅ Handles both expected and unexpected errors

#### Bad Example: Poor Error Handling

```python
# ❌ ANTI-PATTERN - DO NOT USE

def call_ai_provider(provider_name, model, prompt):
    # ❌ No type hints
    # ❌ No docstring
    # ❌ No input validation
    provider = get_provider(provider_name)  # ❌ No error handling
    response = provider.generate(model, prompt)  # ❌ No error handling
    return response.text
```

**Why This is Bad**:
- ❌ No type hints (unclear what types expected)
- ❌ No docstring (no documentation)
- ❌ No input validation (crashes with None or invalid input)
- ❌ No error handling (crashes with unclear errors)
- ❌ No logging (impossible to debug failures)
- ❌ No context in errors (user doesn't know what went wrong)

**How to Fix**:
- Add type hints and comprehensive docstring
- Validate all inputs at function entry
- Use try/except for operations that can fail
- Catch specific exceptions and provide context
- Log errors with relevant data
- Use exception chaining to preserve stack trace

#### Edge Cases

```python
# Edge Case 1: Empty provider name
try:
    response = call_ai_provider("", "model", "prompt")
except ProviderError as e:
    # Should raise: "provider_name cannot be empty"
    pass

# Edge Case 2: Unsupported provider
try:
    response = call_ai_provider("fake_provider", "model", "prompt")
except ProviderError as e:
    # Should raise: "Unsupported provider: fake_provider"
    # Details include supported providers
    pass

# Edge Case 3: Empty prompt
try:
    response = call_ai_provider("claude", "model", "")
except ProviderError as e:
    # Should raise: "prompt cannot be empty"
    pass

# Edge Case 4: Negative max_tokens
try:
    response = call_ai_provider("claude", "model", "prompt", max_tokens=-1)
except ProviderError as e:
    # Should raise: "max_tokens must be positive: -1"
    pass

# Edge Case 5: Rate limit exceeded
try:
    response = call_ai_provider("claude", "model", "prompt")
except RateLimitError as e:
    # Should include provider name and retry_after
    print(f"Rate limited! Retry after {e.retry_after} seconds")
    pass

# Edge Case 6: Model not found
try:
    response = call_ai_provider("claude", "nonexistent-model", "prompt")
except ModelError as e:
    # Should include provider and model name
    pass
```

---

## Testing

### Unit Testing

```python
# tests/unit/test_ai_provider.py
import pytest
from coffee_maker.exceptions import ProviderError, RateLimitError, ModelError
from coffee_maker.ai_provider import call_ai_provider


class TestAIProviderErrorHandling:
    """Test error handling in AI provider."""

    def test_empty_provider_name(self):
        """Should raise ProviderError for empty provider name."""
        with pytest.raises(ProviderError, match="cannot be empty"):
            call_ai_provider("", "model", "prompt")

    def test_unsupported_provider(self):
        """Should raise ProviderError for unsupported provider."""
        with pytest.raises(ProviderError, match="Unsupported provider"):
            call_ai_provider("fake_provider", "model", "prompt")

    def test_empty_prompt(self):
        """Should raise ProviderError for empty prompt."""
        with pytest.raises(ProviderError, match="prompt cannot be empty"):
            call_ai_provider("claude", "model", "")

    def test_negative_max_tokens(self):
        """Should raise ProviderError for negative max_tokens."""
        with pytest.raises(ProviderError, match="must be positive"):
            call_ai_provider("claude", "model", "prompt", max_tokens=-1)

    def test_rate_limit_error_with_retry_after(self, mock_provider_rate_limit):
        """Should raise RateLimitError with retry_after."""
        with pytest.raises(RateLimitError) as exc_info:
            call_ai_provider("claude", "model", "prompt")

        error = exc_info.value
        assert error.provider == "claude"
        assert error.retry_after == 60

    def test_model_not_found(self, mock_provider_model_not_found):
        """Should raise ModelError for nonexistent model."""
        with pytest.raises(ModelError, match="Model not available"):
            call_ai_provider("claude", "fake-model", "prompt")

    def test_exception_chaining_preserved(self, mock_provider_error):
        """Should preserve exception chain with 'from e'."""
        with pytest.raises(ProviderError) as exc_info:
            call_ai_provider("claude", "model", "prompt")

        # Verify exception chain
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, Exception)

    def test_details_dict_populated(self):
        """Should populate details dict with context."""
        with pytest.raises(ProviderError) as exc_info:
            call_ai_provider("fake_provider", "model", "prompt")

        error = exc_info.value
        assert "provider" in error.details
        assert "supported" in error.details
        assert error.details["provider"] == "fake_provider"

    def test_successful_call(self, mock_provider_success):
        """Should return response on success."""
        response = call_ai_provider("claude", "model", "test prompt")
        assert response == "mocked response"
```

### Integration Testing

```python
# tests/integration/test_ai_provider_integration.py
import pytest
from coffee_maker.ai_provider import call_ai_provider
from coffee_maker.exceptions import ProviderError, RateLimitError


@pytest.mark.integration
class TestAIProviderIntegration:
    """Integration tests with real AI providers (mocked)."""

    def test_full_workflow_with_error_recovery(self, mock_api):
        """Test full workflow with error and recovery."""
        # First call: rate limited
        with pytest.raises(RateLimitError) as exc_info:
            call_ai_provider("claude", "sonnet", "prompt")

        # Wait for retry_after
        time.sleep(exc_info.value.retry_after)

        # Second call: success
        response = call_ai_provider("claude", "sonnet", "prompt")
        assert response is not None

    def test_fallback_to_different_provider(self, mock_api):
        """Test fallback when one provider fails."""
        try:
            response = call_ai_provider("claude", "sonnet", "prompt")
        except ProviderError:
            # Fallback to Gemini
            response = call_ai_provider("gemini", "flash", "prompt")

        assert response is not None
```

---

## Common Pitfalls

### Pitfall 1: Catching Too Broad Exceptions

**Description**: Catching `Exception` or `BaseException` hides bugs and makes debugging impossible

**Example**:
```python
# ❌ Bad: Catches ALL exceptions including KeyboardInterrupt
try:
    result = dangerous_operation()
except Exception:
    return None  # Swallows real errors!
```

**Solution**:
```python
# ✅ Good: Catch specific exceptions
try:
    result = dangerous_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise ProviderError("Invalid input") from e
except IOError as e:
    logger.error(f"I/O error: {e}")
    raise FileError("File operation failed") from e
# Let other exceptions propagate (including KeyboardInterrupt)
```

### Pitfall 2: Silent Failures

**Description**: Catching exceptions and doing nothing hides bugs

**Example**:
```python
# ❌ Bad: Silent failure
try:
    save_to_database(data)
except Exception:
    pass  # User thinks save succeeded!
```

**Solution**:
```python
# ✅ Good: Log and re-raise or provide feedback
try:
    save_to_database(data)
except DatabaseError as e:
    logger.exception("Failed to save to database", extra={"data": data})
    raise CoffeeMakerError("Failed to save changes") from e
```

### Pitfall 3: Generic Error Messages

**Description**: Error messages without context are unhelpful

**Example**:
```python
# ❌ Bad: No context
if user is None:
    raise ValueError("Invalid user")
```

**Solution**:
```python
# ✅ Good: Include context
if user is None:
    raise ProviderError(
        f"User not found: {user_id}",
        details={"user_id": user_id, "attempted_at": datetime.now()}
    )
```

### Pitfall 4: Not Using Exception Chaining

**Description**: Losing original exception information

**Example**:
```python
# ❌ Bad: Loses original exception
try:
    result = external_api_call()
except Exception as e:
    raise ProviderError("API call failed")  # Lost original error!
```

**Solution**:
```python
# ✅ Good: Preserve exception chain
try:
    result = external_api_call()
except Exception as e:
    raise ProviderError(
        f"API call failed: {type(e).__name__}",
        details={"error": str(e)}
    ) from e  # Preserves stack trace
```

---

## Performance Considerations

**Performance Impact**: Low

**Description**:
Exception handling in Python has minimal performance impact when exceptions are rare. The cost of try/except blocks is negligible when no exception is raised (~3-5% overhead). Only when exceptions are actually thrown do you pay a significant performance cost (stack unwinding, traceback generation).

**Benchmarks**:
- try/except with no exception: ~1.03x slowdown (negligible)
- try/except with exception: ~100-1000x slowdown (expensive)

**Optimization Tips**:
1. **Don't use exceptions for normal flow control**
   ```python
   # ❌ Slow: Using exceptions for flow control
   try:
       result = cache[key]
   except KeyError:
       result = compute_value(key)

   # ✅ Fast: Use if/else for expected cases
   if key in cache:
       result = cache[key]
   else:
       result = compute_value(key)
   ```

2. **Validate inputs early to fail fast** (cheaper than catching exceptions deep in code)
3. **Cache validation results** if same inputs are used repeatedly
4. **Use pytest.raises()** in tests instead of try/except
5. **Profile code** to identify exception hotspots if performance is critical

---

## Related Patterns

### Related Guideline: GUIDELINE-002-logging-standards

[Link to GUIDELINE-002](./GUIDELINE-002-logging-standards.md)

**Relationship**: Error handling should use structured logging to capture context. See GUIDELINE-002 for how to log exceptions with relevant data for debugging.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Bare Except

**Description**: Using bare `except:` catches everything including SystemExit and KeyboardInterrupt

**Why It's Bad**:
- Catches SystemExit (prevents program termination)
- Catches KeyboardInterrupt (user can't Ctrl+C)
- Hides all bugs, making debugging impossible

**Example**:
```python
# ❌ Anti-pattern: Bare except
try:
    dangerous_operation()
except:  # Catches EVERYTHING!
    pass
```

**Instead Do**:
```python
# ✅ Good: Catch specific exceptions
try:
    dangerous_operation()
except (ValueError, IOError) as e:
    logger.exception("Operation failed")
    raise CoffeeMakerError("Operation failed") from e
```

### Anti-Pattern 2: Swallowing Exceptions

**Description**: Catching exceptions and doing nothing

**Why It's Bad**:
- Hides bugs
- Users don't know operations failed
- System state becomes inconsistent
- Debugging becomes impossible

**Example**:
```python
# ❌ Anti-pattern: Swallow exception
try:
    critical_operation()
except Exception:
    pass  # User thinks it worked!
```

**Instead Do**:
```python
# ✅ Good: Log and re-raise or handle appropriately
try:
    critical_operation()
except Exception as e:
    logger.exception("Critical operation failed")
    raise CoffeeMakerError("Operation failed") from e
```

### Anti-Pattern 3: Generic Exception Types

**Description**: Raising generic `Exception` instead of specific types

**Why It's Bad**:
- Callers can't distinguish between error types
- Makes error handling less precise
- Loses semantic meaning

**Example**:
```python
# ❌ Anti-pattern: Generic exception
def load_config(filepath):
    if not os.path.exists(filepath):
        raise Exception("File not found")  # Too generic!
```

**Instead Do**:
```python
# ✅ Good: Specific exception type
def load_config(filepath: str) -> dict:
    if not os.path.exists(filepath):
        raise FileError(
            f"Config file not found: {filepath}",
            details={"filepath": filepath}
        )
```

---

## Checklist

When implementing error handling, verify:

- [ ] All inputs are validated at function entry (fail fast)
- [ ] Custom exception types are used (not generic Exception)
- [ ] Error messages include relevant context (file paths, IDs, etc.)
- [ ] Details dict is populated for logging/debugging
- [ ] Exceptions are caught at service boundaries (CLI/API layer)
- [ ] All exceptions are logged with structured data
- [ ] User-facing errors are translated to friendly messages
- [ ] Exception chaining is used (`from e`) to preserve stack traces
- [ ] Docstrings document what exceptions are raised
- [ ] Unit tests cover all error cases (pytest.raises)
- [ ] Edge cases are handled gracefully
- [ ] No bare except clauses (always specify exception types)
- [ ] No silent failures (always log or re-raise)

---

## References

- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)
- [PEP 3134 - Exception Chaining](https://www.python.org/dev/peps/pep-3134/)
- [Defensive Programming](https://en.wikipedia.org/wiki/Defensive_programming)
- [coffee_maker/exceptions.py](../../coffee_maker/exceptions.py) - Our exception hierarchy
- [US-030: Code Quality & Architecture](../../ROADMAP.md#us-030) - Context for exception refactoring

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-16 | Created based on existing exception patterns | architect |
| 2025-10-16 | Added performance considerations | architect |
| 2025-10-16 | Added comprehensive testing examples | architect |

---

## Notes

**Migration Strategy**:
- This guideline is based on the existing exception hierarchy in `coffee_maker/exceptions.py`
- All new code should follow this pattern immediately
- Existing code will be refactored gradually (tracked in US-030)
- If you find code not following this pattern, create a tech debt ticket

**Questions?**
- Contact architect agent for architectural discussions
- Reference coffee_maker/exceptions.py for current exception hierarchy
- See US-030 in ROADMAP for migration status

---

**Remember**: Error handling is not just about catching exceptions - it's about providing meaningful feedback, maintaining system reliability, and making debugging easier. Always think about the developer who will debug your code at 3 AM!
