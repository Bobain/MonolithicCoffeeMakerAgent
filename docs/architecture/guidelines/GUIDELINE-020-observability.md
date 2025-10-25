# GUIDELINE-020: Observability Pattern

**Category**: Best Practice

**Applies To**: Logging, tracing, metrics tracking

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: None

---

## Overview

This guideline describes how to implement observability in the codebase using logging, Langfuse tracing, and metrics. Observability enables debugging production issues, understanding performance, and tracking user behavior.

---

## When to Use

Implement observability for:
- Application startup and shutdown
- User actions (login, create, delete)
- External service calls (API, database)
- Error conditions and exceptions
- Performance-critical sections
- Feature usage tracking

---

## When NOT to Use

Do NOT log:
- Sensitive data (passwords, tokens, PII)
- Every line of code execution (too verbose)
- Third-party library internals
- Test execution details
- Debug information in production

---

## The Pattern

### Explanation

Observability uses three pillars:

1. **Logging**: Text records of events
   - Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Includes timestamp, logger name, message, context

2. **Tracing**: Track request flow through system
   - Langfuse integration for distributed tracing
   - Shows how requests flow through services
   - Identifies bottlenecks and errors

3. **Metrics**: Quantitative measurements
   - Response times, error counts, user counts
   - Alerts on thresholds

### Principles

1. **Structured Logging**: Use JSON format for log parsing
2. **Context Information**: Include request ID, user ID, etc.
3. **Appropriate Levels**: Use correct log level for each message
4. **No Secrets**: Never log passwords, tokens, PII
5. **Performance**: Logging should not significantly impact performance
6. **Traces**: Trace all requests through system

---

## How to Implement

### Step 1: Configure Logging

```python
# coffee_maker/config/logging.py

import logging
import json
from pythonjsonlogger import jsonlogger
from coffee_maker.config.settings import settings


def setup_logging():
    """Configure JSON logging."""
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.log_level)

    # Create JSON formatter
    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s %(context)s"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Call on startup
setup_logging()
```

### Step 2: Log Application Events

```python
# coffee_maker/main.py

import logging
from coffee_maker.config.logging import setup_logging
from coffee_maker.config.settings import settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def startup():
    """Application startup."""
    logger.info("Starting application", extra={
        "environment": settings.environment,
        "debug": settings.debug,
        "version": "1.0.0"
    })

    # Setup database
    logger.info("Initializing database", extra={
        "database": "postgresql",
        "url": settings.database_url
    })

    # Setup external services
    logger.info("Connecting to external services", extra={
        "email_service": settings.email_service_url,
        "storage_service": settings.storage_service_url
    })

    logger.info("Startup complete")


def shutdown():
    """Application shutdown."""
    logger.info("Shutting down application")
    # Cleanup
    logger.info("Shutdown complete")
```

### Step 3: Log User Actions

```python
# coffee_maker/api/routes/auth.py

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register")
async def register(request: dict):
    """Register new user."""
    email = request["email"]

    logger.info("User registration attempt", extra={
        "email": email,
        "action": "register_start"
    })

    try:
        # Validate email
        if not validate_email(email):
            logger.warning("Invalid email format", extra={
                "email": email,
                "reason": "format_invalid"
            })
            raise ValueError("Invalid email")

        # Check if user exists
        if user_exists(email):
            logger.warning("Registration failed - user exists", extra={
                "email": email,
                "reason": "duplicate_email"
            })
            raise ValueError("User already exists")

        # Create user
        user = create_user(email, request["password"])

        logger.info("User registered successfully", extra={
            "user_id": user.id,
            "email": email,
            "action": "register_complete"
        })

        return {"id": user.id}

    except Exception as e:
        logger.error("Registration failed", extra={
            "email": email,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise


@router.post("/login")
async def login(request: dict):
    """Login user."""
    email = request["email"]

    logger.info("Login attempt", extra={
        "email": email,
        "action": "login_start"
    })

    try:
        user = authenticate_user(email, request["password"])

        logger.info("Login successful", extra={
            "user_id": user.id,
            "email": email,
            "action": "login_complete"
        })

        return {"token": generate_token(user.id)}

    except Exception as e:
        logger.warning("Login failed", extra={
            "email": email,
            "reason": str(e)
        })
        raise
```

### Step 4: Log External Service Calls

```python
# coffee_maker/services/email_service.py

import logging
import time

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send email with logging."""
    start_time = time.time()

    logger.info("Sending email", extra={
        "to": to,
        "subject": subject[:50],  # Truncate for readability
        "service": "email"
    })

    try:
        # Call external service
        response = external_email_service.send(
            to=to,
            subject=subject,
            body=body
        )

        duration = time.time() - start_time

        logger.info("Email sent successfully", extra={
            "to": to,
            "subject": subject[:50],
            "duration_ms": int(duration * 1000),
            "service": "email",
            "status": "success"
        })

        return True

    except Exception as e:
        duration = time.time() - start_time

        logger.error("Failed to send email", extra={
            "to": to,
            "subject": subject[:50],
            "duration_ms": int(duration * 1000),
            "error": str(e),
            "service": "email",
            "status": "failed"
        }, exc_info=True)

        raise
```

### Step 5: Integrate Langfuse for Tracing

```python
# coffee_maker/config/langfuse.py

from langfuse import Langfuse
from coffee_maker.config.settings import settings

# Initialize Langfuse
langfuse = Langfuse(
    public_key=settings.langfuse_public_key,
    secret_key=settings.langfuse_secret_key,
    host=settings.langfuse_host
) if settings.langfuse_enabled else None


def trace_request(request_id: str, user_id: str = None):
    """Create trace for request."""
    if not langfuse:
        return None

    trace = langfuse.trace(
        name="request",
        input={"request_id": request_id},
        user_id=user_id
    )

    return trace


def trace_span(trace, name: str, input_data: dict = None):
    """Create span within trace."""
    if not trace:
        return None

    span = trace.span(
        name=name,
        input=input_data or {}
    )

    return span
```

### Step 6: Use Decorators for Automatic Tracing

```python
# coffee_maker/decorators/observability.py

import functools
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)


def log_execution(func: Callable) -> Callable:
    """Decorator to log function execution."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        func_name = func.__name__

        logger.debug(f"Executing {func_name}", extra={
            "function": func_name,
            "action": "start"
        })

        try:
            result = func(*args, **kwargs)

            duration = time.time() - start_time
            logger.debug(f"Completed {func_name}", extra={
                "function": func_name,
                "duration_ms": int(duration * 1000),
                "action": "complete"
            })

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed {func_name}", extra={
                "function": func_name,
                "duration_ms": int(duration * 1000),
                "error": str(e),
                "action": "failed"
            }, exc_info=True)
            raise

    return wrapper


def track_metrics(metric_name: str):
    """Decorator to track metrics."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Track success metric
                duration = time.time() - start_time
                record_metric(
                    metric_name,
                    duration,
                    status="success"
                )

                return result

            except Exception as e:
                duration = time.time() - start_time
                record_metric(
                    metric_name,
                    duration,
                    status="error"
                )
                raise

        return wrapper

    return decorator


# Usage
@log_execution
@track_metrics("user_registration")
def register_user(email: str, password: str):
    """Register user with automatic logging and metrics."""
    # Implementation
    pass
```

### Step 7: Structured Logging Context

```python
# coffee_maker/context/logging_context.py

import contextvars
from typing import Optional, Dict

# Context variables for request tracking
request_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
user_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)
session_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "session_id", default=None
)


class LogContext:
    """Context manager for logging."""

    def __init__(self, request_id: str, user_id: str = None):
        self.request_id = request_id
        self.user_id = user_id
        self.tokens = []

    def __enter__(self):
        self.tokens.append(request_id.set(self.request_id))
        if self.user_id:
            self.tokens.append(user_id.set(self.user_id))
        return self

    def __exit__(self, *args):
        for token in self.tokens:
            token.var.reset(token)

    @staticmethod
    def get_context() -> Dict[str, str]:
        """Get current context for logging."""
        ctx = {}
        if req_id := request_id.get():
            ctx["request_id"] = req_id
        if u_id := user_id.get():
            ctx["user_id"] = u_id
        if sess_id := session_id.get():
            ctx["session_id"] = sess_id
        return ctx


# Usage
import uuid
import logging

logger = logging.getLogger(__name__)

@app.post("/register")
async def register(request: dict):
    req_id = str(uuid.uuid4())
    with LogContext(request_id=req_id):
        logger.info("Registering user", extra=LogContext.get_context())
        # All logs in this block will include request_id
```

---

## Anti-Patterns to Avoid

❌ **Don't log sensitive data**
```python
# BAD: Logging passwords and tokens
logger.info(f"User login", extra={
    "email": email,
    "password": password,  # ❌ Never log passwords!
    "token": token  # ❌ Never log tokens!
})
```
**Better**: Log only non-sensitive data
```python
logger.info(f"User login", extra={
    "email": email,
    "user_id": user_id  # ✅ Safe to log
})
```

❌ **Don't log at wrong level**
```python
# BAD: Wrong log levels
logger.error("User logged in")  # ❌ Should be INFO
logger.info("Retry attempt 3")  # ❌ Should be DEBUG
logger.warning("Configuration loaded")  # ❌ Should be INFO
```
**Better**: Use appropriate levels
```python
logger.info("User logged in")      # ✅ Normal operation
logger.debug("Retry attempt 3")    # ✅ Debug info
logger.info("Configuration loaded") # ✅ Startup info
logger.warning("Slow query")       # ✅ Performance issue
logger.error("Database error")     # ✅ Error condition
```

❌ **Don't log without context**
```python
# BAD: Logging without context
logger.info("User created")  # ❌ Which user? When? Why?
logger.error("Failed")  # ❌ What failed? Why?
```
**Better**: Include context
```python
logger.info("User created", extra={
    "user_id": user.id,
    "email": user.email,
    "source": "api"
})

logger.error("Database connection failed", extra={
    "database": "postgresql",
    "host": "db.example.com",
    "error": str(e)
})
```

❌ **Don't use print statements**
```python
# BAD: Using print instead of logging
print(f"Processing user {user_id}")  # ❌ Not logged, not structured
```
**Better**: Use logging
```python
logger.info(f"Processing user", extra={"user_id": user_id})  # ✅ Logged and structured
```

---

## Testing Approach

```python
# tests/unit/test_logging.py

import logging
import pytest


def test_logging_structure(caplog):
    """Test log structure."""
    logger = logging.getLogger("test")

    logger.info("Test message", extra={
        "user_id": "123",
        "action": "test"
    })

    assert "Test message" in caplog.text
    assert "user_id" in caplog.text


def test_no_sensitive_data(caplog):
    """Test that sensitive data is not logged."""
    logger = logging.getLogger("test")

    # This should fail if password is logged
    logger.info("User action", extra={
        "email": "user@example.com"
        # No password field
    })

    assert "password" not in caplog.text.lower()
```

---

## Related Guidelines

- [GUIDELINE-001: Error Handling](./GUIDELINE-001-error-handling.md)

---

## Examples in Codebase

- `coffee_maker/config/logging.py` (logging setup)
- `coffee_maker/api/routes/` (logging in endpoints)
- `coffee_maker/services/` (logging in services)

---

## References

- [Python Logging](https://docs.python.org/3/library/logging.html)
- [JSON Logging with python-json-logger](https://github.com/madzak/python-json-logger)
- [Langfuse Documentation](https://docs.langfuse.com/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial observability pattern guideline |
