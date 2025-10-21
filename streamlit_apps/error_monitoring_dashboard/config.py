"""Configuration for Streamlit Error Monitoring Dashboard.

This module provides configuration management for the error monitoring dashboard,
connecting to the Langfuse export database (SQLite or PostgreSQL).

Example:
    >>> config = DashboardConfig.from_env()
    >>> print(config.db_path)
    'llm_metrics.db'
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DashboardConfig:
    """Configuration for Error Monitoring Dashboard.

    Attributes:
        db_type: Database type ("sqlite" or "postgresql")
        sqlite_path: Path to SQLite database file (default: llm_metrics.db)
        postgres_host: PostgreSQL host (required if db_type="postgresql")
        postgres_port: PostgreSQL port (default: 5432)
        postgres_database: PostgreSQL database name
        postgres_user: PostgreSQL username
        postgres_password: PostgreSQL password
        page_title: Dashboard page title
        layout: Page layout ("wide" or "centered")
        initial_sidebar_state: Initial sidebar state ("expanded" or "collapsed")
        theme: Dashboard theme ("light" or "dark")
        cache_ttl: Cache time-to-live in seconds (default: 300)
        max_rows_export: Maximum rows for data export (default: 100000)
        alert_check_interval: Interval to check for new alerts in seconds (default: 60)
        error_rate_threshold: Error rate threshold for alerts (default: 0.10 = 10%)
        critical_error_threshold: Critical error count threshold (default: 5)

    Example:
        >>> config = DashboardConfig.from_env()
        >>> print(config.db_path)
        'llm_metrics.db'
    """

    # Database configuration
    db_type: str = "sqlite"
    sqlite_path: str = "llm_metrics.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "llm_metrics"
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None

    # Dashboard configuration
    page_title: str = "Error Monitoring Dashboard"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    theme: str = "light"

    # Performance configuration
    cache_ttl: int = 300  # 5 minutes
    max_rows_export: int = 100_000

    # Alert configuration
    alert_check_interval: int = 60  # 1 minute
    error_rate_threshold: float = 0.10  # 10%
    critical_error_threshold: int = 5

    @classmethod
    def from_env(cls) -> "DashboardConfig":
        """Load configuration from environment variables.

        Environment variables:
            DB_TYPE: Database type - "sqlite" or "postgresql" (default: sqlite)
            SQLITE_PATH: SQLite database path (default: llm_metrics.db)
            POSTGRES_HOST: PostgreSQL host
            POSTGRES_PORT: PostgreSQL port (default: 5432)
            POSTGRES_DATABASE: PostgreSQL database name
            POSTGRES_USER: PostgreSQL username
            POSTGRES_PASSWORD: PostgreSQL password
            ERROR_DASHBOARD_TITLE: Dashboard page title
            DASHBOARD_LAYOUT: Page layout ("wide" or "centered")
            DASHBOARD_SIDEBAR: Initial sidebar state
            DASHBOARD_THEME: Dashboard theme
            CACHE_TTL: Cache TTL in seconds (default: 300)
            MAX_ROWS_EXPORT: Max rows for export (default: 100000)
            ALERT_CHECK_INTERVAL: Alert check interval in seconds (default: 60)
            ERROR_RATE_THRESHOLD: Error rate threshold for alerts (default: 0.10)
            CRITICAL_ERROR_THRESHOLD: Critical error count threshold (default: 5)

        Returns:
            DashboardConfig instance with values from environment

        Example:
            >>> config = DashboardConfig.from_env()
            >>> config.db_path
            'llm_metrics.db'
        """
        return cls(
            db_type=os.getenv("DB_TYPE", "sqlite"),
            sqlite_path=os.getenv("SQLITE_PATH", "llm_metrics.db"),
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_database=os.getenv("POSTGRES_DATABASE", "llm_metrics"),
            postgres_user=os.getenv("POSTGRES_USER"),
            postgres_password=os.getenv("POSTGRES_PASSWORD"),
            page_title=os.getenv("ERROR_DASHBOARD_TITLE", "Error Monitoring Dashboard"),
            layout=os.getenv("DASHBOARD_LAYOUT", "wide"),
            initial_sidebar_state=os.getenv("DASHBOARD_SIDEBAR", "expanded"),
            theme=os.getenv("DASHBOARD_THEME", "light"),
            cache_ttl=int(os.getenv("CACHE_TTL", "300")),
            max_rows_export=int(os.getenv("MAX_ROWS_EXPORT", "100000")),
            alert_check_interval=int(os.getenv("ALERT_CHECK_INTERVAL", "60")),
            error_rate_threshold=float(os.getenv("ERROR_RATE_THRESHOLD", "0.10")),
            critical_error_threshold=int(os.getenv("CRITICAL_ERROR_THRESHOLD", "5")),
        )

    @property
    def db_path(self) -> str:
        """Get database path for SQLite or connection string for PostgreSQL.

        Returns:
            Database path/connection string

        Example:
            >>> config = DashboardConfig(db_type="sqlite", sqlite_path="test.db")
            >>> config.db_path
            'test.db'
        """
        if self.db_type == "sqlite":
            return self.sqlite_path
        elif self.db_type == "postgresql":
            if not self.postgres_user or not self.postgres_password:
                raise ValueError("postgres_user and postgres_password required for PostgreSQL")
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
            )
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

    @property
    def absolute_db_path(self) -> str:
        """Get absolute path to SQLite database.

        Returns:
            Absolute path to database file

        Example:
            >>> config = DashboardConfig()
            >>> config.absolute_db_path
            '/full/path/to/llm_metrics.db'
        """
        if self.db_type == "sqlite":
            return str(Path(self.sqlite_path).resolve())
        return self.db_path

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If SQLite database doesn't exist

        Example:
            >>> config = DashboardConfig()
            >>> config.validate()
        """
        if self.db_type == "sqlite":
            db_file = Path(self.sqlite_path)
            if not db_file.exists():
                raise FileNotFoundError(
                    f"SQLite database not found: {self.sqlite_path}\n"
                    f"Please ensure the analytics database has been created.\n"
                    f"Expected path: {db_file.resolve()}"
                )
        elif self.db_type == "postgresql":
            if not self.postgres_user or not self.postgres_password:
                raise ValueError("postgres_user and postgres_password are required for PostgreSQL")
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}. Must be 'sqlite' or 'postgresql'.")

        # Validate cache TTL
        if self.cache_ttl < 0:
            raise ValueError("cache_ttl must be non-negative")

        # Validate max rows export
        if self.max_rows_export <= 0:
            raise ValueError("max_rows_export must be positive")

        # Validate alert thresholds
        if self.error_rate_threshold < 0 or self.error_rate_threshold > 1:
            raise ValueError("error_rate_threshold must be between 0 and 1")

        if self.critical_error_threshold < 0:
            raise ValueError("critical_error_threshold must be non-negative")


# Global configuration instance
_config: Optional[DashboardConfig] = None


def get_config() -> DashboardConfig:
    """Get global dashboard configuration.

    Returns:
        DashboardConfig instance

    Example:
        >>> config = get_config()
        >>> print(config.page_title)
        'Error Monitoring Dashboard'
    """
    global _config
    if _config is None:
        _config = DashboardConfig.from_env()
    return _config


def set_config(config: DashboardConfig) -> None:
    """Set global dashboard configuration.

    Args:
        config: DashboardConfig instance

    Example:
        >>> config = DashboardConfig(page_title="My Dashboard")
        >>> set_config(config)
    """
    global _config
    _config = config
