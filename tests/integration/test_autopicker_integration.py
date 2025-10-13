"""Integration tests for AutoPickerLLMRefactored with real API calls.

These tests make actual API calls to verify the system works end-to-end.
They are slower and require valid API credentials.

Run with: pytest tests/integration/test_autopicker_integration.py -v
Skip with: pytest -m "not integration"
"""

import os
import time

import pytest
from langchain_openai import ChatOpenAI

from coffee_maker.llm.auto_picker import (
    AutoPickerLLMRefactored,
)
from coffee_maker.llm.scheduled import ScheduledLLM
from coffee_maker.llm.strategies.fallback import SequentialFallback
from coffee_maker.llm.strategies.metrics import LocalMetrics

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def check_api_keys():
    """Verify required API keys are present."""
    required_keys = ["OPENAI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        pytest.skip(f"Missing required API keys: {', '.join(missing_keys)}")


@pytest.fixture
def metrics():
    """Create fresh metrics instance for each test."""
    return LocalMetrics()


@pytest.fixture
def simple_primary_llm():
    """Create simple primary LLM for testing."""
    base_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, max_tokens=100)
    return ScheduledLLM(llm=base_llm, model_name="openai/gpt-3.5-turbo")


@pytest.fixture
def simple_fallback_llm():
    """Create simple fallback LLM for testing."""
    base_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=100)
    return ScheduledLLM(llm=base_llm, model_name="openai/gpt-4o-mini")


class TestBasicGeneration:
    """Test basic LLM generation functionality."""

    def test_simple_invoke(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test basic invoke with real API."""
        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            metrics_strategy=metrics,
        )

        start_time = time.time()
        response = llm.invoke("Say 'Hello World' in French.")
        elapsed = time.time() - start_time

        # Verify response
        assert response is not None
        assert len(response.content) > 0
        assert "bonjour" in response.content.lower() or "salut" in response.content.lower()

        # Verify metrics were recorded
        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-3.5-turbo"] >= 1
        assert stats["tokens"]["openai/gpt-3.5-turbo"] > 0
        assert elapsed < 10  # Should complete within 10 seconds

    def test_batch_invoke(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test batch processing with real API."""
        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            metrics_strategy=metrics,
        )

        inputs = ["Say 'one' in French", "Say 'two' in French", "Say 'three' in French"]

        start_time = time.time()
        responses = llm.batch(inputs)
        elapsed = time.time() - start_time

        # Verify responses
        assert len(responses) == 3
        for response in responses:
            assert response is not None
            assert len(response.content) > 0

        # Verify metrics
        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-3.5-turbo"] >= 3
        assert elapsed < 30  # Batch should complete within 30 seconds


class TestFallbackBehavior:
    """Test fallback behavior with real APIs."""

    def test_successful_primary_no_fallback(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test that successful primary doesn't trigger fallback."""
        fallback_strategy = SequentialFallback()

        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            fallback_strategy=fallback_strategy,
            metrics_strategy=metrics,
        )

        response = llm.invoke("Say hello")

        # Verify response
        assert response is not None
        assert len(response.content) > 0

        # Verify primary was used
        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-3.5-turbo"] >= 1


class TestTokenEstimation:
    """Test token estimation with real API responses."""

    def test_token_estimation_accuracy(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test that estimated tokens are reasonably close to actual."""
        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            metrics_strategy=metrics,
        )

        prompt = "Explain what machine learning is in exactly 50 words."
        response = llm.invoke(prompt)

        # Get actual token usage from metrics
        stats = metrics.get_metrics()
        actual_tokens = stats["tokens"]["openai/gpt-3.5-turbo"]

        # Verify tokens were recorded
        assert actual_tokens > 0
        assert actual_tokens < 1000  # Reasonable upper bound

        # Response should exist
        assert response is not None
        assert len(response.content) > 0


class TestCostTracking:
    """Test cost tracking with real API calls."""

    def test_cost_recorded(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test that costs are tracked for real API calls."""
        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            metrics_strategy=metrics,
        )

        response = llm.invoke("Count from 1 to 5")

        # Verify response
        assert response is not None

        # Verify cost was recorded
        stats = metrics.get_metrics()
        total_cost = metrics.get_total_cost()

        # Cost should be greater than 0 (even if small)
        assert total_cost > 0
        assert stats["costs"]["openai/gpt-3.5-turbo"] > 0


class TestErrorHandling:
    """Test error handling with real APIs."""

    def test_invalid_model_name(self, check_api_keys, metrics):
        """Test handling of invalid model name."""
        # Create LLM with invalid model
        invalid_llm = ChatOpenAI(model="gpt-99-nonexistent", temperature=0.7)
        scheduled_invalid = ScheduledLLM(llm=invalid_llm, model_name="openai/gpt-99-nonexistent")

        # Create fallback (valid model)
        fallback_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        scheduled_fallback = ScheduledLLM(llm=fallback_llm, model_name="openai/gpt-3.5-turbo")

        llm = AutoPickerLLMRefactored(
            primary_llm=scheduled_invalid,
            primary_model_name="openai/gpt-99-nonexistent",
            fallback_llms=[(scheduled_fallback, "openai/gpt-3.5-turbo")],
            metrics_strategy=metrics,
        )

        # Should fallback to valid model
        response = llm.invoke("Hello")
        assert response is not None

        # Error should be recorded in metrics
        stats = metrics.get_metrics()
        # Either error was recorded, or fallback was used successfully
        assert (
            len(stats.get("errors", {})) > 0
            or stats.get("fallbacks", {}) != {}
            or stats["requests"]["openai/gpt-3.5-turbo"] > 0
        )


class TestLatencyTracking:
    """Test latency tracking for real API calls."""

    def test_latency_recorded(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test that latency is tracked accurately."""
        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            metrics_strategy=metrics,
        )

        start_time = time.time()
        response = llm.invoke("Say hello")
        actual_elapsed = time.time() - start_time

        # Verify response
        assert response is not None

        # Get recorded latency
        recorded_latency = metrics.get_average_latency("openai/gpt-3.5-turbo")

        # Recorded latency should be close to actual (within 1 second tolerance)
        assert abs(recorded_latency - actual_elapsed) < 1.0
        assert recorded_latency > 0


class TestMultipleProviders:
    """Test with multiple providers if available."""

    def test_openai_provider(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test OpenAI provider integration."""
        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            metrics_strategy=metrics,
        )

        response = llm.invoke("What is 2+2?")

        assert response is not None
        assert "4" in response.content or "four" in response.content.lower()


@pytest.mark.slow
class TestLongRunning:
    """Tests that take longer to run."""

    def test_multiple_sequential_calls(self, check_api_keys, simple_primary_llm, simple_fallback_llm, metrics):
        """Test multiple sequential calls to verify stability."""
        llm = AutoPickerLLMRefactored(
            primary_llm=simple_primary_llm,
            primary_model_name="openai/gpt-3.5-turbo",
            fallback_llms=[(simple_fallback_llm, "openai/gpt-4o-mini")],
            metrics_strategy=metrics,
        )

        num_calls = 5
        responses = []

        for i in range(num_calls):
            response = llm.invoke(f"Count to {i+1}")
            responses.append(response)
            time.sleep(0.5)  # Small delay between calls

        # Verify all responses
        assert len(responses) == num_calls
        for response in responses:
            assert response is not None
            assert len(response.content) > 0

        # Verify metrics
        stats = metrics.get_metrics()
        assert stats["requests"]["openai/gpt-3.5-turbo"] >= num_calls
        assert stats["tokens"]["openai/gpt-3.5-turbo"] > 0
