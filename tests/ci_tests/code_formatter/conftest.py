"""Fixtures and configuration for code_formatter tests"""

import os
from unittest import mock

import pytest

# Set required environment variables before modules are imported
os.environ.setdefault("GOOGLE_API_KEY", "fake_test_key")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "fake_secret")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "fake_public")
os.environ.setdefault("LANGFUSE_HOST", "http://localhost")
os.environ.setdefault("GITHUB_TOKEN", "fake_github_token")
# Disable OpenTelemetry tracing during tests
os.environ.setdefault("OTEL_SDK_DISABLED", "true")


@pytest.fixture
def mock_langfuse_client() -> mock.MagicMock:
    """Provide a mock Langfuse client.

    Returns:
        mock.MagicMock: A mocked Langfuse client instance with pre-configured methods.
    """
    client = mock.MagicMock()
    mock_prompt = mock.MagicMock()
    mock_prompt.compile.return_value = "Mocked prompt text"
    mock_prompt.prompt = "Mocked prompt"
    client.get_prompt.return_value = mock_prompt
    client.flush.return_value = None
    client.update_current_trace.return_value = None
    return client
