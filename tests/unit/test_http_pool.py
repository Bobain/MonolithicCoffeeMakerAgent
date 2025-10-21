"""Unit tests for HTTP connection pool."""

import pytest
import httpx

from coffee_maker.langfuse_observe.http_pool import (
    HTTPConnectionPool,
    get_http_client,
    get_async_http_client,
)


class TestHTTPConnectionPool:
    """Tests for HTTPConnectionPool."""

    def setup_method(self):
        """Reset pool before each test."""
        HTTPConnectionPool.reset()

    def teardown_method(self):
        """Clean up pool after each test."""
        HTTPConnectionPool.reset()

    def test_singleton_pattern(self):
        """Test that HTTPConnectionPool is a singleton."""
        pool1 = HTTPConnectionPool()
        pool2 = HTTPConnectionPool()

        assert pool1 is pool2

    def test_get_client_returns_httpx_client(self):
        """Test that get_client returns httpx.Client."""
        client = HTTPConnectionPool.get_client()

        assert isinstance(client, httpx.Client)

    def test_get_async_client_returns_async_client(self):
        """Test that get_async_client returns httpx.AsyncClient."""
        client = HTTPConnectionPool.get_async_client()

        assert isinstance(client, httpx.AsyncClient)

    def test_same_client_returned_on_multiple_calls(self):
        """Test that same client instance is returned."""
        client1 = HTTPConnectionPool.get_client()
        client2 = HTTPConnectionPool.get_client()

        assert client1 is client2

    def test_custom_configuration(self):
        """Test pool with custom configuration."""
        pool = HTTPConnectionPool(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=60.0,
            timeout=120.0,
        )

        assert pool.max_connections == 50
        assert pool.max_keepalive_connections == 10
        assert pool.keepalive_expiry == 60.0
        assert pool.timeout == 120.0

    def test_close_cleans_up_resources(self):
        """Test that close properly cleans up."""
        client = HTTPConnectionPool.get_client()
        assert client is not None

        HTTPConnectionPool.close()

        # After close, _instance should be None
        assert HTTPConnectionPool._instance is None

    def test_reset_allows_new_instance(self):
        """Test that reset allows creating new instance with different config."""
        pool1 = HTTPConnectionPool(max_connections=100)
        assert pool1.max_connections == 100

        HTTPConnectionPool.reset()

        pool2 = HTTPConnectionPool(max_connections=50)
        assert pool2.max_connections == 50
        assert pool1 is not pool2  # Different instances after reset

    def test_async_client_works(self):
        """Test that async client can be created."""
        client = HTTPConnectionPool.get_async_client()

        assert isinstance(client, httpx.AsyncClient)
        assert client is not None


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def setup_method(self):
        """Reset pool before each test."""
        HTTPConnectionPool.reset()

    def teardown_method(self):
        """Clean up pool after each test."""
        HTTPConnectionPool.reset()

    def test_get_http_client_returns_client(self):
        """Test get_http_client convenience function."""
        client = get_http_client()

        assert isinstance(client, httpx.Client)

    def test_get_async_http_client_returns_client(self):
        """Test get_async_http_client convenience function."""
        client = get_async_http_client()

        assert isinstance(client, httpx.AsyncClient)

    def test_convenience_functions_use_same_pool(self):
        """Test that convenience functions use the same pool."""
        client1 = get_http_client()
        client2 = HTTPConnectionPool.get_client()

        assert client1 is client2

    def test_can_pass_config_to_convenience_functions(self):
        """Test passing configuration to convenience functions."""
        client = get_http_client(max_connections=75)
        pool = HTTPConnectionPool._instance

        assert pool.max_connections == 75


@pytest.mark.integration
class TestHTTPPoolIntegration:
    """Integration tests for HTTP pool with actual requests.

    These tests make real network requests and are marked as integration tests.
    Run with: pytest -m integration
    Skip with: pytest -m "not integration"
    """

    def setup_method(self):
        """Reset pool before each test."""
        HTTPConnectionPool.reset()

    def teardown_method(self):
        """Clean up pool after each test."""
        HTTPConnectionPool.reset()

    def test_can_make_request_with_pooled_client(self):
        """Test making HTTP request with pooled client."""
        client = get_http_client()

        # Make request to httpbin (public test API)
        try:
            response = client.get("https://httpbin.org/get", timeout=5.0)
            assert response.status_code == 200
        except Exception as e:
            pytest.skip(f"Network request failed: {e}")

    def test_multiple_requests_reuse_connection(self):
        """Test that multiple requests reuse the same client."""
        client = get_http_client()

        # Make multiple requests
        try:
            responses = []
            for _ in range(3):
                response = client.get("https://httpbin.org/get", timeout=5.0)
                responses.append(response)

            # All should succeed
            assert all(r.status_code == 200 for r in responses)
        except Exception as e:
            pytest.skip(f"Network requests failed: {e}")

    def test_async_client_created(self):
        """Test that async client can be created for async requests."""
        client = get_async_http_client()

        # Just verify it's created correctly, actual async requests
        # would require pytest-asyncio
        assert isinstance(client, httpx.AsyncClient)
        assert client is not None


class TestHTTPPoolThreadSafety:
    """Tests for thread safety of HTTP pool."""

    def setup_method(self):
        """Reset pool before each test."""
        HTTPConnectionPool.reset()

    def teardown_method(self):
        """Clean up pool after each test."""
        HTTPConnectionPool.reset()

    def test_concurrent_access_returns_same_instance(self):
        """Test that concurrent access returns same instance."""
        import threading

        instances = []

        def get_instance():
            pool = HTTPConnectionPool()
            instances.append(pool)

        # Create multiple threads trying to get the instance
        threads = [threading.Thread(target=get_instance) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All instances should be the same
        assert all(instance is instances[0] for instance in instances)
