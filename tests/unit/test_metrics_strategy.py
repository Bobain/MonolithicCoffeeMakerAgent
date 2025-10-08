"""Unit tests for MetricsStrategy implementations."""

import pytest

from coffee_maker.langchain_observe.strategies.metrics import (
    LocalMetrics,
    NoOpMetrics,
    PrometheusMetrics,
    create_metrics_strategy,
)


class TestLocalMetrics:
    """Tests for LocalMetrics."""

    @pytest.fixture
    def metrics(self):
        """Create LocalMetrics instance."""
        return LocalMetrics()

    def test_record_request(self, metrics):
        """Test recording a request."""
        metrics.record_request("openai/gpt-4o", latency=1.5, tokens=100, is_primary=True, success=True)

        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-4o"] == 1
        assert stats["latencies"]["openai/gpt-4o"] == 1.5
        assert stats["tokens"]["openai/gpt-4o"] == 100

    def test_record_multiple_requests(self, metrics):
        """Test recording multiple requests."""
        metrics.record_request("openai/gpt-4o", latency=1.0, tokens=100)
        metrics.record_request("openai/gpt-4o", latency=2.0, tokens=200)
        metrics.record_request("gemini/flash", latency=0.5, tokens=50)

        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-4o"] == 2
        assert stats["requests"]["gemini/flash"] == 1
        assert stats["latencies"]["openai/gpt-4o"] == 3.0
        assert stats["tokens"]["openai/gpt-4o"] == 300

    def test_record_error(self, metrics):
        """Test recording an error."""
        metrics.record_error("openai/gpt-4o", "rate_limit", "Too many requests")

        stats = metrics.get_metrics()
        assert stats["errors"]["openai/gpt-4o:rate_limit"] == 1

    def test_record_cost(self, metrics):
        """Test recording cost."""
        metrics.record_cost("openai/gpt-4o", cost=0.05, tokens=1000)

        stats = metrics.get_metrics()
        assert stats["costs"]["openai/gpt-4o"] == 0.05

    def test_record_fallback(self, metrics):
        """Test recording a fallback."""
        metrics.record_fallback("openai/gpt-4o", "gemini/flash", "rate_limit")

        stats = metrics.get_metrics()
        assert stats["fallbacks"]["openai/gpt-4o->gemini/flash"] == 1

    def test_get_average_latency(self, metrics):
        """Test calculating average latency."""
        metrics.record_request("openai/gpt-4o", latency=1.0, tokens=100)
        metrics.record_request("openai/gpt-4o", latency=3.0, tokens=100)

        avg_latency = metrics.get_average_latency("openai/gpt-4o")
        assert avg_latency == 2.0

    def test_get_average_latency_no_requests(self, metrics):
        """Test average latency with no requests."""
        avg_latency = metrics.get_average_latency("openai/gpt-4o")
        assert avg_latency == 0.0

    def test_get_total_cost(self, metrics):
        """Test calculating total cost."""
        metrics.record_cost("openai/gpt-4o", cost=0.05, tokens=1000)
        metrics.record_cost("gemini/flash", cost=0.01, tokens=500)

        total_cost = metrics.get_total_cost()
        assert abs(total_cost - 0.06) < 0.0001  # Float precision tolerance

    def test_reset(self, metrics):
        """Test resetting metrics."""
        metrics.record_request("openai/gpt-4o", latency=1.0, tokens=100)
        metrics.record_error("openai/gpt-4o", "rate_limit", "Error")
        metrics.record_cost("openai/gpt-4o", cost=0.05, tokens=1000)

        metrics.reset()

        stats = metrics.get_metrics()
        assert stats["requests"] == {}
        assert stats["errors"] == {}
        assert stats["costs"] == {}
        assert stats["total_records"] == 0


class TestNoOpMetrics:
    """Tests for NoOpMetrics."""

    @pytest.fixture
    def metrics(self):
        """Create NoOpMetrics instance."""
        return NoOpMetrics()

    def test_record_request_does_nothing(self, metrics):
        """Test that recording a request does nothing."""
        metrics.record_request("openai/gpt-4o", latency=1.0, tokens=100)
        stats = metrics.get_metrics()
        assert stats == {"type": "noop"}

    def test_record_error_does_nothing(self, metrics):
        """Test that recording an error does nothing."""
        metrics.record_error("openai/gpt-4o", "rate_limit", "Error")
        stats = metrics.get_metrics()
        assert stats == {"type": "noop"}

    def test_record_cost_does_nothing(self, metrics):
        """Test that recording cost does nothing."""
        metrics.record_cost("openai/gpt-4o", cost=0.05, tokens=1000)
        stats = metrics.get_metrics()
        assert stats == {"type": "noop"}

    def test_record_fallback_does_nothing(self, metrics):
        """Test that recording a fallback does nothing."""
        metrics.record_fallback("openai/gpt-4o", "gemini/flash", "rate_limit")
        stats = metrics.get_metrics()
        assert stats == {"type": "noop"}


class TestPrometheusMetrics:
    """Tests for PrometheusMetrics."""

    def test_initialization_without_library(self):
        """Test initialization when prometheus_client is not available."""
        # PrometheusMetrics should handle missing library gracefully
        metrics = PrometheusMetrics()
        # Should not raise error
        metrics.record_request("openai/gpt-4o", latency=1.0, tokens=100)


class TestCreateMetricsStrategy:
    """Tests for create_metrics_strategy factory function."""

    def test_create_local_metrics(self):
        """Test creating local metrics strategy."""
        metrics = create_metrics_strategy("local")
        assert isinstance(metrics, LocalMetrics)

    def test_create_noop_metrics(self):
        """Test creating noop metrics strategy."""
        metrics = create_metrics_strategy("noop")
        assert isinstance(metrics, NoOpMetrics)

    def test_create_prometheus_metrics(self):
        """Test creating prometheus metrics strategy."""
        metrics = create_metrics_strategy("prometheus")
        assert isinstance(metrics, PrometheusMetrics)

    def test_create_unknown_defaults_to_local(self):
        """Test that unknown strategy type defaults to local."""
        metrics = create_metrics_strategy("unknown")
        assert isinstance(metrics, LocalMetrics)


class TestMetricsIntegration:
    """Integration tests for metrics strategies."""

    def test_complete_request_lifecycle(self):
        """Test complete lifecycle of a request with metrics."""
        metrics = LocalMetrics()

        # Simulate successful request
        metrics.record_request("openai/gpt-4o", latency=1.5, tokens=1000, is_primary=True, success=True)
        metrics.record_cost("openai/gpt-4o", cost=0.05, tokens=1000)

        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-4o"] == 1
        assert stats["costs"]["openai/gpt-4o"] == 0.05
        assert metrics.get_average_latency("openai/gpt-4o") == 1.5

    def test_request_with_fallback(self):
        """Test request lifecycle with fallback."""
        metrics = LocalMetrics()

        # Primary fails
        metrics.record_request("openai/gpt-4o", latency=0.5, tokens=100, is_primary=True, success=False)
        metrics.record_error("openai/gpt-4o", "rate_limit", "Too many requests")

        # Fallback to gemini
        metrics.record_fallback("openai/gpt-4o", "gemini/flash", "rate_limit")
        metrics.record_request("gemini/flash", latency=1.0, tokens=100, is_primary=False, success=True)
        metrics.record_cost("gemini/flash", cost=0.01, tokens=100)

        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-4o"] == 1
        assert stats["requests"]["gemini/flash"] == 1
        assert stats["errors"]["openai/gpt-4o:rate_limit"] == 1
        assert stats["fallbacks"]["openai/gpt-4o->gemini/flash"] == 1
        assert stats["costs"]["gemini/flash"] == 0.01

    def test_multiple_models_tracking(self):
        """Test tracking metrics across multiple models."""
        metrics = LocalMetrics()

        # Track different models
        models = [
            ("openai/gpt-4o", 1.5, 1000, 0.05),
            ("gemini/flash", 0.8, 500, 0.01),
            ("anthropic/claude", 2.0, 1500, 0.08),
        ]

        for model, latency, tokens, cost in models:
            metrics.record_request(model, latency=latency, tokens=tokens)
            metrics.record_cost(model, cost=cost, tokens=tokens)

        stats = metrics.get_metrics()
        assert len(stats["requests"]) == 3
        assert stats["requests"]["openai/gpt-4o"] == 1
        assert stats["requests"]["gemini/flash"] == 1
        assert stats["requests"]["anthropic/claude"] == 1
        assert metrics.get_total_cost() == 0.14
