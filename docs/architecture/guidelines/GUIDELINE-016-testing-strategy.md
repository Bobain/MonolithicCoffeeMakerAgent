# GUIDELINE-016: Testing Strategy

**Category**: Best Practice

**Applies To**: All tests in coffee_maker codebase

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: None

---

## Overview

This guideline describes the three-tier testing strategy: unit tests (fast, isolated), integration tests (components together), and end-to-end tests (full workflows). It covers test structure, coverage requirements, and best practices.

---

## When to Use

Follow this testing strategy for:
- All feature implementations
- Bug fixes (add regression tests)
- API endpoints
- Service classes
- Database operations
- CLI commands

---

## When NOT to Use

Do NOT write tests for:
- Third-party library code
- Configuration files
- Generated code (migrations, etc.)
- Temporary test scripts

---

## The Pattern

### Explanation

We use three tiers of testing:

1. **Unit Tests** (~70% of tests)
   - Test individual functions/methods in isolation
   - Fast (milliseconds)
   - Use mocks for dependencies
   - Test both happy path and error cases

2. **Integration Tests** (~20% of tests)
   - Test components working together
   - Slower (seconds)
   - Use real database for most, mocks for external services
   - Test realistic workflows

3. **End-to-End Tests** (~10% of tests)
   - Test complete user workflows
   - Slowest (minutes)
   - Full stack (database, API, client)
   - Real external services when possible

### Principles

1. **Test Pyramid**: More unit tests than integration, more integration than E2E
2. **Isolation**: Unit tests should not depend on other tests
3. **Clarity**: Test names describe what is tested
4. **Coverage**: Target >80% code coverage
5. **Speed**: Fast tests run on every commit
6. **Maintainability**: Avoid test duplication, use fixtures

---

## How to Implement

### Step 1: Project Test Structure

```
coffee_maker/
├── module/
│   ├── __init__.py
│   ├── service.py        # Implementation
│   └── models.py         # Data models
└── tests/
    ├── unit/
    │   ├── test_service.py        # Unit tests
    │   └── test_models.py
    ├── integration/
    │   ├── test_service_with_db.py  # Integration tests
    │   └── test_api_workflows.py
    └── e2e/
        └── test_user_workflows.py   # E2E tests
```

### Step 2: Unit Test Structure

```python
# tests/unit/test_service.py

import pytest
from unittest.mock import Mock, patch
from coffee_maker.module.service import UserService
from coffee_maker.module.models import User

class TestUserService:
    """Unit tests for UserService."""

    @pytest.fixture
    def service(self):
        """Create service with mocked dependencies."""
        return UserService(
            db=Mock(),
            email_client=Mock(),
            password_hasher=Mock()
        )

    def test_create_user_success(self, service):
        """Test successful user creation."""
        # Arrange
        service.email_client.send.return_value = True
        request = {"email": "user@example.com", "password": "secure123"}

        # Act
        user = service.create_user(**request)

        # Assert
        assert user.email == "user@example.com"
        assert user.id is not None
        service.email_client.send.assert_called_once()

    def test_create_user_invalid_email(self, service):
        """Test creation with invalid email."""
        # Arrange
        request = {"email": "invalid", "password": "secure123"}

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email"):
            service.create_user(**request)

    def test_create_user_duplicate_email(self, service):
        """Test creation with duplicate email."""
        # Arrange
        service.db.get.return_value = Mock()  # User exists
        request = {"email": "user@example.com", "password": "secure123"}

        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            service.create_user(**request)

    def test_create_user_email_failure(self, service):
        """Test creation when email sending fails."""
        # Arrange
        service.email_client.send.side_effect = Exception("SMTP error")
        request = {"email": "user@example.com", "password": "secure123"}

        # Act & Assert
        with pytest.raises(Exception, match="SMTP error"):
            service.create_user(**request)

    @patch('coffee_maker.module.service.logger')
    def test_create_user_logs_creation(self, mock_logger, service):
        """Test that user creation is logged."""
        # Arrange
        service.email_client.send.return_value = True
        request = {"email": "user@example.com", "password": "secure123"}

        # Act
        user = service.create_user(**request)

        # Assert
        mock_logger.info.assert_called()
```

### Step 3: Integration Test Structure

```python
# tests/integration/test_service_with_db.py

import pytest
from sqlalchemy import create_engine
from coffee_maker.module.service import UserService
from coffee_maker.db.models import Base, User

@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def service_with_db(db_session):
    """Create service with real database."""
    return UserService(db=db_session)


class TestUserServiceIntegration:
    """Integration tests with real database."""

    def test_create_and_retrieve_user(self, service_with_db, db_session):
        """Test creating and retrieving user."""
        # Create
        user = service_with_db.create_user(
            email="user@example.com",
            password="secure123"
        )

        # Retrieve from database
        retrieved = db_session.query(User).filter_by(id=user.id).first()

        # Verify
        assert retrieved is not None
        assert retrieved.email == "user@example.com"
        assert retrieved.password_hash is not None  # Hashed

    def test_list_users(self, service_with_db):
        """Test listing users."""
        # Create multiple users
        service_with_db.create_user(email="user1@example.com", password="pass1")
        service_with_db.create_user(email="user2@example.com", password="pass2")
        service_with_db.create_user(email="user3@example.com", password="pass3")

        # List users
        users = service_with_db.list_users()

        # Verify
        assert len(users) == 3
```

### Step 4: End-to-End Test Structure

```python
# tests/e2e/test_user_workflows.py

import pytest
from fastapi.testclient import TestClient
from coffee_maker.api.main import app
from coffee_maker.db.models import User

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestUserWorkflows:
    """End-to-end tests for user workflows."""

    def test_user_registration_workflow(self, client):
        """Test complete user registration workflow."""
        # Register user
        register_response = client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "secure123"
        })
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # Login
        login_response = client.post("/api/auth/login", json={
            "email": "newuser@example.com",
            "password": "secure123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["token"]

        # Access protected endpoint
        protected_response = client.get(
            "/api/users/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 200
        assert protected_response.json()["id"] == user_id

        # Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_response.status_code == 204
```

### Step 5: Shared Test Fixtures

```python
# tests/conftest.py

import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_email_client():
    """Mock email client for all tests."""
    return Mock(send=Mock(return_value=True))

@pytest.fixture
def mock_db():
    """Mock database for all tests."""
    return Mock()

@pytest.fixture
def mock_logger():
    """Mock logger for all tests."""
    return Mock()
```

### Step 6: Run Tests with Coverage

```bash
# Run all tests with coverage report
pytest --cov=coffee_maker --cov-report=html --cov-report=term

# Output:
# Name                          Stmts   Miss  Cover   Missing
# -----------------------------------------------------------
# coffee_maker/module/service.py   45     3    93%    45-47
# coffee_maker/module/models.py    32     2    94%    18,42
# TOTAL                           450    15    97%

# Run only unit tests (fast)
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run specific test
pytest tests/unit/test_service.py::TestUserService::test_create_user_success -v
```

---

## Anti-Patterns to Avoid

❌ **Don't write tests that depend on each other**
```python
# BAD: Test order dependent
def test_1_create_user(self):
    global user_id
    user_id = service.create_user(...)

def test_2_get_user(self):
    user = service.get_user(user_id)  # ❌ Depends on test_1_create_user
```
**Better**: Each test is independent
```python
@pytest.fixture
def user(service):
    return service.create_user(...)

def test_get_user(self, user):
    retrieved = service.get_user(user.id)
    assert retrieved.id == user.id
```

❌ **Don't test implementation details**
```python
# BAD: Testing internal implementation
def test_password_hash_format(self):
    hash = hasher.hash("password")
    assert hash.startswith("$2b$")  # ❌ Testing bcrypt format, not function
```
**Better**: Test behavior
```python
def test_password_verification(self):
    hash = hasher.hash("password")
    assert hasher.verify("password", hash)  # ✅ Tests behavior
    assert not hasher.verify("wrong", hash)  # ✅ Tests behavior
```

❌ **Don't use sleep() in tests**
```python
# BAD: Flaky test with sleep
def test_async_operation(self):
    start_operation()
    time.sleep(2)  # ❌ Flaky, slow
    verify_complete()
```
**Better**: Use mocking or async test utilities
```python
@pytest.mark.asyncio
async def test_async_operation(self):
    result = await operation()  # ✅ Proper async testing
    assert result.is_complete
```

❌ **Don't mix unit and integration tests**
```python
# BAD: Unit test that touches database
@pytest.fixture
def service(self):
    return UserService(db=real_db_connection)  # ❌ Not isolated

def test_create_user(self, service):
    user = service.create_user(...)
```
**Better**: Unit tests use mocks
```python
@pytest.fixture
def service(self):
    return UserService(db=Mock())  # ✅ Isolated

def test_create_user(self, service):
    user = service.create_user(...)
```

❌ **Don't write large test methods**
```python
# BAD: Test does too much
def test_user_workflow(self):
    # 50 lines of test code
    # Tests create, read, update, delete
```
**Better**: One assertion per test
```python
def test_create_user(self):
    user = service.create_user(...)
    assert user.id is not None

def test_retrieve_user(self):
    user = service.get_user(user_id)
    assert user.email == "user@example.com"
```

---

## Testing Approach

### Test Pyramid

```
        E2E Tests (10%)
         /          \
        /            \
   Integration Tests (20%)
       /                \
      /                  \
  Unit Tests (70%)
```

### Coverage Requirements

- **Target**: >80% code coverage
- **Minimum**: >75% for any module
- **Critical paths**: 100% coverage (auth, payments, etc.)

```bash
# Check coverage
pytest --cov=coffee_maker --cov-report=term-missing

# Generate HTML report
pytest --cov=coffee_maker --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Related Guidelines

- [GUIDELINE-014: FastAPI Endpoints](./GUIDELINE-014-fastapi-endpoints.md)
- [GUIDELINE-001: Error Handling](./GUIDELINE-001-error-handling.md)

---

## Examples in Codebase

- `tests/unit/` (unit test examples)
- `tests/integration/` (integration test examples)
- `tests/conftest.py` (shared fixtures)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial testing strategy guideline |
