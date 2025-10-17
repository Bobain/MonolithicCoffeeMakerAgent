# ADR-006: Centralized Error Handling Strategy

**Status**: Proposed
**Date**: 2025-10-17
**Author**: architect agent

---

## Context

The MonolithicCoffeeMakerAgent codebase currently has **inconsistent error handling** across modules:

1. **Duplication**: Try/except blocks repeated across many files with similar logic
2. **Inconsistency**: Different error messages for similar failures
3. **Missing Context**: Errors don't always include sufficient debugging information
4. **Poor User Experience**: Technical errors exposed directly to users
5. **No Centralized Logging**: Error tracking scattered across the codebase

### Examples of Current Problems

**Problem 1: Duplicated Try/Except Blocks**
```python
# coffee_maker/cli/ai_service.py (Line 349)
try:
    # ... AI request ...
except Exception as e:
    logger.error(f"AI request failed: {e}")
    return AIResponse(
        message=f"Sorry, I encountered an error: {str(e)}",
        action=None,
        confidence=0.0,
        metadata=None,
    )

# coffee_maker/cli/roadmap_editor.py (Line 148)
try:
    # ... file operation ...
except Exception as e:
    logger.error(f"Failed to add priority: {e}")
    raise

# coffee_maker/autonomous/daemon.py (Line 234)
try:
    # ... daemon operation ...
except Exception as e:
    logger.error(f"Daemon error: {e}")
    # No re-raise, error swallowed
```

**Problem 2: Inconsistent Error Messages**
```python
# Different messages for similar failures:
"Failed to add priority: {e}"
"Priority addition failed: {e}"
"Error adding priority: {e}"
"Could not add priority: {e}"
```

**Problem 3: Missing Context in Errors**
```python
# This error doesn't tell us which priority or what the input was:
logger.error(f"Failed to add priority: {e}")

# Better would be:
logger.error(f"Failed to add priority {priority_number} ({title}): {e}", extra={
    "priority_number": priority_number,
    "title": title,
    "user_input": user_input,
    "stack_trace": traceback.format_exc()
})
```

---

## Decision

**We will adopt a centralized error handling strategy** with the following components:

### 1. Custom Exception Hierarchy

Define domain-specific exceptions that carry context:

```python
# coffee_maker/utils/exceptions.py

class CoffeeMakerError(Exception):
    """Base exception for all CoffeeMaker errors."""

    def __init__(self, message: str, context: Optional[Dict] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (context: {self.context})"


class ValidationError(CoffeeMakerError):
    """Raised when validation fails."""
    pass


class FileOperationError(CoffeeMakerError):
    """Raised when file operations fail."""
    pass


class AIServiceError(CoffeeMakerError):
    """Raised when AI service encounters an error."""
    pass


class DaemonError(CoffeeMakerError):
    """Raised when daemon encounters an error."""
    pass


class RoadmapError(CoffeeMakerError):
    """Raised when roadmap operations fail."""
    pass
```

### 2. Centralized Error Handler

Create a centralized error handler with consistent logging and user-friendly messages:

```python
# coffee_maker/utils/error_handler.py

from typing import Optional, Dict, Type
import logging
import traceback

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handler with context logging."""

    @staticmethod
    def handle_error(
        error: Exception,
        context: Optional[Dict] = None,
        user_message: Optional[str] = None,
        reraise: bool = True,
        log_level: str = "error"
    ) -> Optional[str]:
        """Handle error with centralized logging and optional re-raising.

        Args:
            error: Exception that occurred
            context: Additional context for debugging
            user_message: User-friendly message to return/log
            reraise: Whether to re-raise the exception after logging
            log_level: Logging level (debug, info, warning, error, critical)

        Returns:
            User-friendly error message if not re-raising

        Example:
            >>> try:
            ...     risky_operation()
            ... except Exception as e:
            ...     ErrorHandler.handle_error(
            ...         error=e,
            ...         context={"priority_number": "PRIORITY 10", "user": "admin"},
            ...         user_message="Failed to add priority. Please try again.",
            ...         reraise=False
            ...     )
        """
        # Build context dictionary
        error_context = context or {}
        error_context.update({
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
        })

        # Log with context
        log_func = getattr(logger, log_level, logger.error)
        log_func(
            f"Error occurred: {error}",
            extra={"error_context": error_context},
            exc_info=True
        )

        # Generate user message
        if user_message is None:
            user_message = ErrorHandler._generate_user_message(error)

        # Re-raise or return
        if reraise:
            raise error
        else:
            return user_message

    @staticmethod
    def _generate_user_message(error: Exception) -> str:
        """Generate user-friendly message from exception."""
        if isinstance(error, ValidationError):
            return f"Validation failed: {error.message}"
        elif isinstance(error, FileOperationError):
            return "File operation failed. Please check file permissions and try again."
        elif isinstance(error, AIServiceError):
            return "AI service is temporarily unavailable. Please try again later."
        elif isinstance(error, DaemonError):
            return "Daemon encountered an error. Check logs for details."
        elif isinstance(error, RoadmapError):
            return f"Roadmap operation failed: {error.message}"
        else:
            return f"An unexpected error occurred: {str(error)}"

    @staticmethod
    def wrap_operation(
        operation_name: str,
        context: Optional[Dict] = None,
        user_message: Optional[str] = None,
        reraise: bool = True
    ):
        """Decorator to wrap operations with error handling.

        Example:
            >>> @ErrorHandler.wrap_operation("add_priority", context={"priority": "10"})
            ... def add_priority(priority_number, title):
            ...     # ... operation ...
            ...     pass
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    return ErrorHandler.handle_error(
                        error=e,
                        context={
                            "operation": operation_name,
                            **(context or {}),
                            "args": args,
                            "kwargs": kwargs
                        },
                        user_message=user_message,
                        reraise=reraise
                    )
            return wrapper
        return decorator
```

### 3. Usage Patterns

**Pattern 1: Raise Custom Exceptions with Context**
```python
# BEFORE (current code):
if not self._validate_priority_number(priority_number, content):
    raise ValueError(f"Priority {priority_number} already exists or is invalid")

# AFTER (with centralized error handling):
if not self._validate_priority_number(priority_number, content):
    raise ValidationError(
        f"Priority {priority_number} already exists or is invalid",
        context={
            "priority_number": priority_number,
            "operation": "add_priority",
            "existing_priorities": existing_priorities
        }
    )
```

**Pattern 2: Handle Errors with Context Logging**
```python
# BEFORE (current code):
try:
    result = self.cli_interface.execute_prompt(full_prompt)
    if not result.success:
        raise Exception(result.error)
except Exception as e:
    logger.error(f"AI request failed: {e}")
    return AIResponse(message=f"Sorry, I encountered an error: {str(e)}", ...)

# AFTER (with centralized error handling):
try:
    result = self.cli_interface.execute_prompt(full_prompt)
    if not result.success:
        raise AIServiceError(result.error, context={"prompt": full_prompt[:100]})
except AIServiceError as e:
    user_message = ErrorHandler.handle_error(
        error=e,
        context={"model": self.model, "user_input": user_input[:100]},
        user_message="AI service is temporarily unavailable. Please try again.",
        reraise=False  # Return user-friendly message instead
    )
    return AIResponse(message=user_message, action=None, confidence=0.0)
```

**Pattern 3: Use Decorator for Repetitive Error Handling**
```python
# BEFORE (current code):
def add_priority(self, priority_number: str, ...):
    try:
        # Create backup
        self._create_backup()
        # ... rest of operation ...
        return True
    except Exception as e:
        logger.error(f"Failed to add priority: {e}")
        raise

# AFTER (with decorator):
@ErrorHandler.wrap_operation("add_priority", user_message="Failed to add priority")
def add_priority(self, priority_number: str, ...):
    # Create backup
    self._create_backup()
    # ... rest of operation ...
    return True
```

### 4. Integration with Observability

**Integrate with Langfuse for error tracking**:

```python
from coffee_maker.langfuse_observe import langfuse_context

class ErrorHandler:
    @staticmethod
    def handle_error(error: Exception, context: Optional[Dict] = None, ...):
        # ... existing logging ...

        # Report to Langfuse if available
        if langfuse_context.get_current_trace_id():
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(error),
                metadata=error_context
            )

        # ... rest of handling ...
```

---

## Consequences

### Positive

1. **Consistency**: All errors logged and handled uniformly
2. **Better Debugging**: Rich context in all error logs
3. **Improved UX**: User-friendly error messages instead of technical stack traces
4. **Easier Testing**: Mock error handling in tests
5. **Observability**: Integrated with Langfuse for error tracking
6. **Maintainability**: Centralized error handling reduces duplication

### Negative

1. **Migration Effort**: Need to update ~50+ error handling sites across codebase
2. **Learning Curve**: Team needs to learn new exception hierarchy
3. **Added Abstraction**: One more layer between error and handling
4. **Potential Over-Engineering**: Simple errors might not need full context

---

## Alternatives Considered

### Alternative 1: Keep Status Quo (Rejected)

**Pros**: No migration effort
**Cons**: Inconsistency continues, poor UX, hard to debug

**Why Rejected**: Technical debt accumulates, user experience suffers

### Alternative 2: Use Third-Party Error Tracking (e.g., Sentry)

**Pros**: Production-grade error tracking, rich dashboards
**Cons**: External dependency, cost, requires internet connection

**Why Rejected**: We already have Langfuse for observability. Adding Sentry would be redundant. We can integrate with Sentry later if needed.

### Alternative 3: Minimal Error Handler (Just Logging)

**Pros**: Simple, quick to implement
**Cons**: Doesn't solve UX problem, still inconsistent

**Why Rejected**: Doesn't provide enough value. Need custom exceptions and user-friendly messages.

---

## Migration Plan

### Phase 1: Create Error Handling Utilities (2 hours)
1. Create `coffee_maker/utils/exceptions.py`
2. Create `coffee_maker/utils/error_handler.py`
3. Add unit tests for error handling

### Phase 2: Migrate Critical Paths (4 hours)
4. Update `ai_service.py` error handling
5. Update `roadmap_editor.py` error handling
6. Update `daemon.py` error handling
7. Test critical paths

### Phase 3: Migrate Remaining Modules (4 hours)
8. Update `chat_interface.py`
9. Update `roadmap_cli.py`
10. Update autonomous modules
11. Full test suite

### Phase 4: Documentation (1 hour)
12. Update contributor documentation
13. Add error handling examples
14. Update CLAUDE.md with error handling guidelines

**Total Effort**: ~11 hours (~1.5 days)

---

## Implementation Guidelines

### For New Code

**ALWAYS use custom exceptions**:
```python
# ✅ GOOD
if not valid:
    raise ValidationError("Invalid input", context={"input": user_input})

# ❌ BAD
if not valid:
    raise ValueError("Invalid input")
```

**ALWAYS use ErrorHandler for logging**:
```python
# ✅ GOOD
try:
    risky_operation()
except SpecificError as e:
    ErrorHandler.handle_error(e, context={...}, user_message="User-friendly message")

# ❌ BAD
try:
    risky_operation()
except Exception as e:
    logger.error(f"Failed: {e}")
```

**Use decorator for repetitive patterns**:
```python
# ✅ GOOD
@ErrorHandler.wrap_operation("operation_name", context={...})
def operation():
    # ... code ...
    pass

# ❌ BAD
def operation():
    try:
        # ... code ...
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise
```

### For Existing Code

**Gradual migration**:
1. Start with critical paths (daemon, AI service, roadmap editor)
2. Add error handler to modified files during feature work
3. Deprecate old error handling patterns with warnings
4. Complete migration within 2 sprints

---

## Success Metrics

**Before**:
- ~50 inconsistent try/except blocks
- Technical errors shown to users
- Limited error context in logs
- No centralized error tracking

**After**:
- Consistent error handling across all modules
- User-friendly error messages
- Rich context in all error logs
- Integrated with Langfuse observability
- <100 LOC per error handling site (down from duplicated blocks)

---

## Open Questions

1. **Should we integrate with Sentry in the future?**
   - Decision: Defer to Phase 2. Monitor Langfuse integration first.

2. **Should errors be translated to multiple languages?**
   - Decision: Not now. English-only for initial release.

3. **Should we add retry logic to error handler?**
   - Decision: No. Retry logic is operation-specific, not error-handler concern.

---

## Related Work

- **ADR-004**: Code Quality Improvement Strategy (simplification first)
- **REFACTORING_BACKLOG**: P3 Item #9 (Extract shared error handling utilities)
- **SPEC-064, SPEC-065**: Refactoring specs that will benefit from centralized error handling

---

## Approval

**Pending approval from code_developer** for implementation.

Once approved, code_developer will:
1. Create feature branch: `feature/centralized-error-handling`
2. Implement error handling utilities
3. Migrate critical paths
4. Add comprehensive tests
5. Update documentation
6. Create PR for review

---

## Version History

- **v1.0** (2025-10-17): Initial proposal by architect agent
