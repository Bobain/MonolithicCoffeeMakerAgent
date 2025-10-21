# GUIDELINE-017: Custom Exception Hierarchy

**Category**: Design Pattern

**Applies To**: Exception handling throughout coffee_maker codebase

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: None

---

## Overview

This guideline describes how to define and use custom exceptions in the coffee_maker codebase. It covers exception hierarchy, when to raise exceptions, and how to handle them appropriately.

---

## When to Use

Define and use custom exceptions when:
- Creating new service or module
- Need to distinguish between error types (validation vs not found vs permission)
- Want to provide meaningful error context to callers
- Building APIs or CLI tools that need specific error codes
- Implementing retry logic or error recovery

---

## When NOT to Use

Do NOT use custom exceptions for:
- Expected application flow (use if/else instead)
- All errors the same (let built-in exceptions propagate)
- Catching exceptions you don't handle
- Testing expected failures (use pytest.raises)

---

## The Pattern

### Explanation

Custom exception hierarchy provides:
1. **Base Exception**: All custom exceptions inherit from this
2. **Category Exceptions**: General categories (NotFoundError, ValidationError, etc.)
3. **Specific Exceptions**: Detailed exceptions for specific scenarios
4. **Context Information**: Include relevant data in exception messages
5. **Proper Propagation**: Let exceptions bubble up appropriately

### Principles

1. **Hierarchy**: Exceptions organized in logical hierarchy
2. **Inheritance**: All custom exceptions inherit from base
3. **Specificity**: More specific exceptions before general ones
4. **Context**: Include data relevant to debugging
5. **Documentation**: Clear docstrings explain when to use

---

## How to Implement

### Step 1: Define Exception Base Class

```python
# coffee_maker/exceptions.py

class CoffeeMakerException(Exception):
    """Base exception for all coffee_maker errors."""

    def __init__(self, message: str, code: str = None, context: dict = None):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (e.g., "INVALID_INPUT")
            context: Additional context information (e.g., {"field": "email"})
        """
        self.message = message
        self.code = code or self.__class__.__name__
        self.context = context or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/API response."""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context
        }

    def __str__(self):
        return self.message
```

### Step 2: Define Category Exceptions

```python
# coffee_maker/exceptions.py

class ValidationError(CoffeeMakerException):
    """Raised when input validation fails."""
    pass


class NotFoundError(CoffeeMakerException):
    """Raised when requested resource not found."""
    pass


class PermissionError(CoffeeMakerException):
    """Raised when user lacks required permissions."""
    pass


class ConflictError(CoffeeMakerException):
    """Raised when resource already exists or state conflict."""
    pass


class ExternalServiceError(CoffeeMakerException):
    """Raised when external service fails."""
    pass


class DatabaseError(CoffeeMakerException):
    """Raised when database operation fails."""
    pass


class ConfigurationError(CoffeeMakerException):
    """Raised when configuration is invalid."""
    pass
```

### Step 3: Define Specific Exceptions

```python
# coffee_maker/modules/auth/exceptions.py

from coffee_maker.exceptions import ValidationError, NotFoundError, ConflictError

class InvalidEmailError(ValidationError):
    """Raised when email format is invalid."""

    def __init__(self, email: str):
        super().__init__(
            message=f"Invalid email format: {email}",
            code="INVALID_EMAIL",
            context={"email": email}
        )


class UserNotFoundError(NotFoundError):
    """Raised when user not found."""

    def __init__(self, user_id: str):
        super().__init__(
            message=f"User not found: {user_id}",
            code="USER_NOT_FOUND",
            context={"user_id": user_id}
        )


class UserAlreadyExistsError(ConflictError):
    """Raised when user already exists."""

    def __init__(self, email: str):
        super().__init__(
            message=f"User already exists: {email}",
            code="USER_ALREADY_EXISTS",
            context={"email": email}
        )


class InvalidPasswordError(ValidationError):
    """Raised when password is invalid."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid password: {reason}",
            code="INVALID_PASSWORD",
            context={"reason": reason}
        )
```

### Step 4: Raise Exceptions with Context

```python
# coffee_maker/modules/auth/service.py

import re
import logging
from coffee_maker.modules.auth.exceptions import (
    InvalidEmailError,
    UserAlreadyExistsError,
    InvalidPasswordError,
    UserNotFoundError
)

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service."""

    def register_user(self, email: str, password: str) -> dict:
        """
        Register new user.

        Args:
            email: User email
            password: User password

        Returns:
            User data

        Raises:
            InvalidEmailError: If email format invalid
            InvalidPasswordError: If password invalid
            UserAlreadyExistsError: If user already exists
        """
        # Validate email format
        if not self._is_valid_email(email):
            raise InvalidEmailError(email)

        # Validate password strength
        if not self._is_valid_password(password):
            reason = "Password must be at least 8 characters"
            raise InvalidPasswordError(reason)

        # Check if user exists
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(email)

        # Create user
        logger.info(f"Creating new user: {email}")
        user = self.db.create_user(
            email=email,
            password_hash=self._hash_password(password)
        )

        logger.info(f"User created: {user.id}")
        return user.to_dict()

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """Validate password strength."""
        return len(password) >= 8
```

### Step 5: Handle Exceptions Appropriately

```python
# coffee_maker/api/routes/auth.py

from fastapi import APIRouter, HTTPException
from coffee_maker.modules.auth.service import AuthService
from coffee_maker.modules.auth.exceptions import (
    CoffeeMakerException,
    ValidationError,
    ConflictError,
    NotFoundError
)

router = APIRouter()
auth_service = AuthService()

@router.post("/register")
async def register(request: dict) -> dict:
    """
    Register new user.

    Raises:
        HTTPException: 400 for validation errors, 409 for conflicts
    """
    try:
        user = auth_service.register_user(
            email=request["email"],
            password=request["password"]
        )
        return user

    except ValidationError as e:
        # Client error: bad input
        raise HTTPException(
            status_code=422,
            detail={
                "code": e.code,
                "message": e.message,
                "context": e.context
            }
        )

    except ConflictError as e:
        # Client error: resource conflict
        raise HTTPException(
            status_code=409,
            detail={
                "code": e.code,
                "message": e.message
            }
        )

    except CoffeeMakerException as e:
        # Unexpected application error
        logger.exception(f"Application error: {e.to_dict()}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

### Step 6: Log Exception Context

```python
# coffee_maker/modules/user/service.py

import logging
from coffee_maker.exceptions import DatabaseError

logger = logging.getLogger(__name__)

def update_user(user_id: str, **updates) -> dict:
    """Update user."""
    try:
        logger.info(f"Updating user: {user_id}", extra={"user_id": user_id})

        user = db.get_user(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        updated_user = db.update_user(user_id, **updates)
        logger.info(f"User updated: {user_id}", extra={"user_id": user_id})

        return updated_user.to_dict()

    except UserNotFoundError as e:
        # Expected error, log at info level
        logger.info(f"User not found: {e.to_dict()}")
        raise

    except DatabaseError as e:
        # Unexpected database error, log at error level
        logger.error(
            f"Database error updating user",
            exc_info=True,
            extra={
                "user_id": user_id,
                "error": e.to_dict()
            }
        )
        raise
```

---

## Anti-Patterns to Avoid

❌ **Don't raise generic Exception**
```python
# BAD: Generic exception hides problem
def create_user(email: str):
    if not email:
        raise Exception("Invalid email")  # ❌ What error?
```
**Better**: Specific exception
```python
def create_user(email: str):
    if not email:
        raise InvalidEmailError(email)  # ✅ Clear error type
```

❌ **Don't catch and ignore exceptions**
```python
# BAD: Silent failure
try:
    user = db.get_user(user_id)
except:
    pass  # ❌ Problem hidden!
```
**Better**: Handle or re-raise
```python
try:
    user = db.get_user(user_id)
except UserNotFoundError as e:
    logger.warning(f"User not found: {e}")
    raise  # ✅ Or handle appropriately
```

❌ **Don't use exceptions for flow control**
```python
# BAD: Exception for expected flow
try:
    items = get_items()
except IndexError:
    items = []  # ❌ Using exception for control flow
```
**Better**: Normal control flow
```python
items = get_items() or []  # ✅ Or
items = get_items() if items else []  # ✅ Or
if not items:
    items = []
```

❌ **Don't lose exception context**
```python
# BAD: Re-raising loses original exception
try:
    user = db.get_user(user_id)
except DatabaseError:
    raise  # ✅ Good
except Exception as e:
    raise ValueError("Failed to get user")  # ❌ Loses original context
```
**Better**: Preserve exception chain
```python
try:
    user = db.get_user(user_id)
except DatabaseError as e:
    logger.exception(f"Database error: {e}")
    raise DatabaseError(f"Failed to get user: {e}") from e  # ✅ Preserves chain
```

---

## Testing Approach

```python
# tests/unit/test_exceptions.py

import pytest
from coffee_maker.exceptions import CoffeeMakerException, ValidationError
from coffee_maker.modules.auth.exceptions import InvalidEmailError

def test_exception_context():
    """Test exception carries context."""
    exc = InvalidEmailError("bad@")
    assert exc.code == "INVALID_EMAIL"
    assert exc.context["email"] == "bad@"

def test_exception_to_dict():
    """Test exception serialization."""
    exc = InvalidEmailError("bad@")
    exc_dict = exc.to_dict()
    assert exc_dict["code"] == "INVALID_EMAIL"
    assert "message" in exc_dict

def test_register_invalid_email():
    """Test registration with invalid email."""
    service = AuthService()
    with pytest.raises(InvalidEmailError) as exc_info:
        service.register_user("bad@", "password123")

    assert exc_info.value.context["email"] == "bad@"
```

---

## Related Guidelines

- [GUIDELINE-001: Error Handling](./GUIDELINE-001-error-handling.md)
- [GUIDELINE-014: FastAPI Endpoints](./GUIDELINE-014-fastapi-endpoints.md)

---

## Examples in Codebase

- `coffee_maker/exceptions.py` (base exceptions)
- `coffee_maker/modules/auth/exceptions.py` (specific exceptions)
- `coffee_maker/api/routes/auth.py` (exception handling in API)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial custom exception hierarchy guideline |
