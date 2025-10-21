# GUIDELINE-019: Configuration Management

**Category**: Best Practice

**Applies To**: Configuration, environment variables, secrets management

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: None

---

## Overview

This guideline describes how to manage application configuration using environment variables, configuration files, and secrets, supporting multiple environments (dev, staging, production).

---

## When to Use

Use this approach for:
- Database connection strings
- API keys and secrets
- Feature flags
- Environment-specific settings (dev vs production)
- Credentials and tokens
- Service URLs and endpoints

---

## When NOT to Use

Do NOT use configuration for:
- Application constants (use module-level constants)
- Business logic parameters (use database or API)
- Code-specific settings (hardcode in implementation)

---

## The Pattern

### Explanation

Configuration management uses:
1. **Environment Variables**: Secrets and environment-specific settings
2. **Configuration Files**: Default settings for each environment
3. **Pydantic Settings**: Type-safe configuration validation
4. **Priority Order**: CLI args > environment vars > config files > defaults
5. **Secrets Management**: Keep credentials separate and secure

### Principles

1. **Secrets in Environment**: Never commit credentials to git
2. **Type Safety**: Use Pydantic for validation
3. **Multi-Environment**: Support dev, staging, production
4. **Defaults**: Provide sensible defaults for development
5. **Documentation**: Document all configuration options
6. **Validation**: Validate configuration on startup

---

## How to Implement

### Step 1: Define Configuration Class

```python
# coffee_maker/config/settings.py

from typing import Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = "development"  # development, staging, production
    debug: bool = False

    # Database
    database_url: str = "sqlite:///coffee_maker.db"
    database_echo: bool = False  # Log SQL queries

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"

    # Security
    secret_key: str = "dev-secret-key"  # Override in .env
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # External Services
    email_service_url: Optional[str] = None
    email_api_key: Optional[str] = None
    storage_service_url: Optional[str] = None
    storage_api_key: Optional[str] = None

    # Feature Flags
    enable_email_verification: bool = True
    enable_two_factor_auth: bool = False
    max_concurrent_users: int = 1000

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or plain

    class Config:
        # Read from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Validate on assignment
        validate_assignment = True

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        if v not in ("development", "staging", "production"):
            raise ValueError(f"Invalid environment: {v}")
        return v

    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v

    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Validate secret key for production."""
        env = values.get("environment")
        if env == "production" and v == "dev-secret-key":
            raise ValueError(
                "SECRET_KEY must be set for production (not dev-secret-key)"
            )
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Load settings once
settings = Settings()
```

### Step 2: Create Environment Files

```bash
# .env (development - committed to git, no secrets)
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///coffee_maker_dev.db
DATABASE_ECHO=true
LOG_LEVEL=DEBUG
ENABLE_EMAIL_VERIFICATION=false
ENABLE_TWO_FACTOR_AUTH=false

# .env.example (template for new developers)
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///coffee_maker_dev.db
DATABASE_ECHO=false
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
EMAIL_SERVICE_URL=https://api.example.com
EMAIL_API_KEY=your-api-key-here

# .env.local (local overrides - NOT committed)
# Create this file with your local settings
SECRET_KEY=my-local-secret-key
EMAIL_API_KEY=my-local-api-key

# .env.staging (staging environment - NOT in repo, secrets in GitHub Secrets)
ENVIRONMENT=staging
DATABASE_URL=${DATABASE_URL}  # From GitHub Secrets
SECRET_KEY=${SECRET_KEY}      # From GitHub Secrets

# .env.production (production - NOT in repo, secrets in GitHub Secrets)
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=${DATABASE_URL}  # From GitHub Secrets
SECRET_KEY=${SECRET_KEY}      # From GitHub Secrets
```

### Step 3: Use Configuration in Application

```python
# coffee_maker/main.py

from fastapi import FastAPI
from coffee_maker.config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title="Coffee Maker",
    debug=settings.debug
)

# Log startup
logger.info(f"Starting in {settings.environment} environment")
logger.info(f"Database: {settings.database_url}")

# Configure database
from coffee_maker.db.database import get_engine

engine = get_engine(settings.database_url, echo=settings.database_echo)

# Configure JWT
from coffee_maker.auth.jwt_utils import JWTConfig

jwt_config = JWTConfig(
    secret_key=settings.secret_key,
    algorithm=settings.jwt_algorithm,
    expiration_hours=settings.jwt_expiration_hours
)
```

### Step 4: Access Configuration in Routes

```python
# coffee_maker/api/routes/example.py

from fastapi import APIRouter, HTTPException
from coffee_maker.config.settings import settings

router = APIRouter()


@router.get("/config/public")
async def get_public_config():
    """Return public configuration."""
    return {
        "environment": settings.environment,
        "api_version": "1.0.0",
        "features": {
            "email_verification": settings.enable_email_verification,
            "two_factor_auth": settings.enable_two_factor_auth
        }
    }


@router.post("/user")
async def create_user(request: dict):
    """Create user (with email verification based on config)."""
    if settings.enable_email_verification:
        # Send verification email
        send_verification_email(request["email"])

    # Create user
    return {"id": "123"}
```

### Step 5: Environment-Specific Behavior

```python
# coffee_maker/services/email_service.py

import logging
from coffee_maker.config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Send emails."""

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email."""
        if settings.is_development:
            # Log instead of sending in development
            logger.info(f"[DEV] Would send email to {to}: {subject}")
            return True

        if settings.is_production:
            # Use production email service
            return self._send_via_production_service(to, subject, body)

        # Staging: actually send but log
        logger.info(f"[STAGING] Sending email to {to}: {subject}")
        return self._send_via_production_service(to, subject, body)

    def _send_via_production_service(self, to: str, subject: str, body: str):
        """Send via external service."""
        # Use settings.email_service_url and settings.email_api_key
        pass
```

### Step 6: Validate Configuration on Startup

```python
# coffee_maker/config/validation.py

import logging
from coffee_maker.config.settings import settings

logger = logging.getLogger(__name__)


def validate_configuration():
    """Validate configuration on startup."""
    errors = []

    # Check production settings
    if settings.is_production:
        if settings.secret_key == "dev-secret-key":
            errors.append("SECRET_KEY not set for production")

        if not settings.email_service_url:
            errors.append("EMAIL_SERVICE_URL required for production")

        if not settings.storage_service_url:
            errors.append("STORAGE_SERVICE_URL required for production")

    # Check database connectivity
    try:
        from coffee_maker.db.database import test_connection
        test_connection(settings.database_url)
    except Exception as e:
        errors.append(f"Cannot connect to database: {e}")

    if errors:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        raise ValueError("Invalid configuration")

    logger.info("Configuration validated successfully")


# Call on startup
if __name__ == "__main__":
    validate_configuration()
```

---

## Anti-Patterns to Avoid

❌ **Don't hardcode secrets**
```python
# BAD: Secret in code
SECRET_KEY = "my-secret-key"  # ❌ Will be in git history!
DATABASE_PASSWORD = "admin123"  # ❌ Exposed!
```
**Better**: Use environment variables
```python
import os
SECRET_KEY = os.getenv("SECRET_KEY", "dev-default")  # ✅ From .env
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")  # ✅ From environment
```

❌ **Don't commit .env files**
```bash
# BAD: Committed to git
git add .env.production  # ❌ Exposes production secrets!
```
**Better**: Add to .gitignore
```bash
# .gitignore
.env
.env.local
.env.*.local
```

❌ **Don't skip validation**
```python
# BAD: No validation
settings.database_url  # ❌ Could be None or invalid format
```
**Better**: Validate with Pydantic
```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    database_url: str  # ✅ Required, will error if not set

    @validator("database_url")
    def validate_url(cls, v):
        if not v.startswith("postgresql://"):
            raise ValueError("Invalid database URL")
        return v
```

❌ **Don't mix environments**
```python
# BAD: Same credentials for dev and production
DATABASE_URL=postgresql://admin:password@localhost/coffee_maker

# Used for both:
# - Development (local machine)
# - Staging (shared server)
# - Production (critical data!)
```
**Better**: Separate credentials per environment
```bash
# .env (development)
DATABASE_URL=sqlite:///coffee_maker_dev.db

# .env.staging (GitHub Secret)
DATABASE_URL=${STAGING_DATABASE_URL}  # Unique staging database

# .env.production (GitHub Secret)
DATABASE_URL=${PRODUCTION_DATABASE_URL}  # Unique production database
```

---

## Testing Approach

```python
# tests/unit/test_settings.py

import pytest
from coffee_maker.config.settings import Settings


def test_settings_defaults():
    """Test default values."""
    settings = Settings()
    assert settings.environment == "development"
    assert settings.api_port == 8000


def test_settings_from_env(monkeypatch):
    """Test loading from environment."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("DEBUG", "false")

    settings = Settings()
    assert settings.environment == "staging"
    assert settings.debug is False


def test_settings_validation():
    """Test validation."""
    with pytest.raises(ValueError, match="Invalid environment"):
        Settings(environment="invalid")


def test_production_validation():
    """Test production-specific validation."""
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(
            environment="production",
            secret_key="dev-secret-key"
        )
```

---

## Related Guidelines

- [GUIDELINE-017: Custom Exceptions](./GUIDELINE-017-custom-exceptions.md)

---

## Examples in Codebase

- `coffee_maker/config/settings.py` (settings class)
- `.env` (development defaults)
- `.env.example` (template)

---

## References

- [Pydantic Settings](https://docs.pydantic.dev/usage/settings/)
- [Python-dotenv](https://github.com/theskumar/python-dotenv)
- [12-Factor App Configuration](https://12factor.net/config)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial configuration management guideline |
