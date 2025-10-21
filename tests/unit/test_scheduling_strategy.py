"""Unit tests for scheduling strategies."""

import time
from unittest import mock

import pytest

from coffee_maker.langfuse_observe.global_rate_tracker import get_global_rate_tracker
from coffee_maker.langfuse_observe.strategies.scheduling import (
    ProactiveRateLimitScheduler,
)


class TestProactiveRateLimitScheduler:
    """Tests for ProactiveRateLimitScheduler strategy."""

    @pytest.fixture
    def rate_tracker(self):
        """Create a fresh rate tracker for testing."""
        from collections import deque

        # Use tier1 with known limits
        tracker = get_global_rate_tracker("tier1")
        # Clear any existing history
        tracker._request_history.clear()
        tracker._last_call_time = None

        # Ensure request history is initialized for test models
        for model in tracker.model_limits:
            if model not in tracker._request_history:
                tracker._request_history[model] = deque()

        return tracker

    @pytest.fixture
    def scheduler(self, rate_tracker):
        """Create a scheduler with default settings."""
        return ProactiveRateLimitScheduler(rate_tracker=rate_tracker, safety_margin=2)

    def test_initialization(self, scheduler, rate_tracker):
        """Test scheduler initializes correctly."""
        assert scheduler.rate_tracker is rate_tracker
        assert scheduler.safety_margin == 2

    def test_initialization_invalid_tracker(self):
        """Test that initialization fails with invalid tracker."""
        with pytest.raises(TypeError, match="must be RateLimitTracker"):
            ProactiveRateLimitScheduler(rate_tracker="not_a_tracker")

    def test_can_proceed_when_empty(self, scheduler):
        """Test that we can proceed when no requests have been made."""
        can_proceed, wait_time = scheduler.can_proceed("openai/gpt-4o-mini", 1000)
        assert can_proceed is True
        assert wait_time == 0.0

    def test_enforces_rpm_spacing(self, scheduler, rate_tracker):
        """Test that scheduler enforces 60/RPM spacing between requests."""
        model_name = "openai/gpt-4o-mini"

        # Make first request
        scheduler.record_request(model_name, 1000)

        # Immediately check if we can make another
        can_proceed, wait_time = scheduler.can_proceed(model_name, 1000)

        # Should not be able to proceed immediately
        # For tier1 gpt-4o-mini: RPM=500, so min spacing = 60/500 = 0.12s
        assert can_proceed is False
        assert wait_time > 0
        assert wait_time <= 0.12  # Should be at most 60/RPM seconds

    @pytest.mark.slow
    def test_allows_proceed_after_spacing(self, scheduler, rate_tracker):
        """Test that we can proceed after minimum spacing has elapsed."""
        model_name = "openai/gpt-4o-mini"

        # Make first request
        scheduler.record_request(model_name, 1000)

        # Wait for minimum spacing (60/RPM)
        limits = rate_tracker.model_limits[model_name]
        rpm = limits.requests_per_minute
        min_spacing = 60.0 / rpm

        time.sleep(min_spacing + 0.01)  # Add small buffer

        # Now should be able to proceed
        can_proceed, wait_time = scheduler.can_proceed(model_name, 1000)
        assert can_proceed is True
        assert wait_time == 0.0

    @pytest.mark.slow
    def test_safety_margin_requests(self, scheduler, rate_tracker):
        """Test that scheduler stops at N-2 of request limit."""
        model_name = "openai/gpt-4o-mini"
        limits = rate_tracker.model_limits[model_name]
        rpm = limits.requests_per_minute

        # Calculate safe limit (RPM - safety_margin)
        safe_limit = rpm - scheduler.safety_margin  # 500 - 2 = 498

        # Make requests up to safe limit with proper spacing
        min_spacing = 60.0 / rpm
        for i in range(int(safe_limit)):
            scheduler.record_request(model_name, 100)
            if i < safe_limit - 1:  # Don't sleep after last request
                time.sleep(min_spacing)

        # Now we should be at the safety margin
        can_proceed, wait_time = scheduler.can_proceed(model_name, 100)

        # Should not be able to proceed (at safety margin)
        assert can_proceed is False
        assert wait_time > 0

    @pytest.mark.slow
    def test_safety_margin_tokens(self, scheduler, rate_tracker):
        """Test that scheduler stops at N-2 of token limit."""
        model_name = "openai/gpt-4o-mini"
        limits = rate_tracker.model_limits[model_name]
        tpm = limits.tokens_per_minute

        # Calculate safe token limit
        safe_token_limit = tpm - scheduler.safety_margin  # 200000 - 2 = 199998

        # Use large token count to approach limit quickly
        tokens_per_request = safe_token_limit // 2  # Half the safe limit

        # Make first request
        scheduler.record_request(model_name, tokens_per_request)

        # Wait for spacing
        rpm = limits.requests_per_minute
        min_spacing = 60.0 / rpm
        time.sleep(min_spacing)

        # Try to make another request with remaining tokens
        remaining_tokens = safe_token_limit - tokens_per_request

        # This should succeed (just under limit)
        can_proceed, _ = scheduler.can_proceed(model_name, remaining_tokens - 10)
        assert can_proceed is True

        # But this should fail (would exceed safe limit)
        can_proceed, wait_time = scheduler.can_proceed(model_name, remaining_tokens + 10)
        assert can_proceed is False
        assert wait_time > 0

    def test_record_request_updates_tracker(self, scheduler, rate_tracker):
        """Test that recording a request updates the rate tracker."""
        model_name = "openai/gpt-4o-mini"

        # Check initial state
        usage_before = rate_tracker.get_usage_stats(model_name)
        assert usage_before["requests_per_minute"]["current"] == 0
        assert usage_before["tokens_per_minute"]["current"] == 0

        # Record request
        scheduler.record_request(model_name, 1000)

        # Check updated state
        usage_after = rate_tracker.get_usage_stats(model_name)
        assert usage_after["requests_per_minute"]["current"] == 1
        assert usage_after["tokens_per_minute"]["current"] == 1000

    def test_get_status(self, scheduler, rate_tracker):
        """Test getting status for a model."""
        model_name = "openai/gpt-4o-mini"

        # Get status before any requests
        status = scheduler.get_status(model_name)

        assert status["model"] == model_name
        assert status["current_requests"] == 0
        assert status["current_tokens"] == 0
        assert status["safe_request_limit"] == 498  # 500 - 2
        assert status["total_request_limit"] == 500
        assert status["at_capacity"] is False

        # Make some requests
        scheduler.record_request(model_name, 5000)

        # Get status after request
        status = scheduler.get_status(model_name)
        assert status["current_requests"] == 1
        assert status["current_tokens"] == 5000

    def test_wait_until_ready_immediate(self, scheduler):
        """Test wait_until_ready when immediately ready."""
        model_name = "openai/gpt-4o-mini"

        # Should be ready immediately
        ready = scheduler.wait_until_ready(model_name, 1000, max_wait=1.0)
        assert ready is True

    @pytest.mark.slow
    def test_wait_until_ready_with_wait(self, scheduler, rate_tracker):
        """Test wait_until_ready when need to wait."""
        model_name = "openai/gpt-4o-mini"

        # Make a request to trigger spacing requirement
        scheduler.record_request(model_name, 1000)

        # This should wait for spacing and then succeed
        start_time = time.time()
        ready = scheduler.wait_until_ready(model_name, 1000, max_wait=1.0)
        elapsed = time.time() - start_time

        assert ready is True
        # Should have waited for at least the minimum spacing
        limits = rate_tracker.model_limits[model_name]
        min_spacing = 60.0 / limits["requests_per_minute"]
        assert elapsed >= min_spacing * 0.9  # Allow 10% tolerance

    @pytest.mark.slow
    def test_wait_until_ready_exceeds_max_wait(self, scheduler, rate_tracker):
        """Test wait_until_ready when wait would exceed max_wait."""
        model_name = "openai/gpt-4o-mini"
        limits = rate_tracker.model_limits[model_name]
        rpm = limits.requests_per_minute
        safe_limit = rpm - scheduler.safety_margin

        # Fill up to safety margin
        min_spacing = 60.0 / rpm
        for i in range(int(safe_limit)):
            scheduler.record_request(model_name, 100)
            if i < safe_limit - 1:
                time.sleep(min_spacing)

        # Now at capacity, would need to wait for window to slide (~60s)
        # But we set max_wait to 0.1s
        ready = scheduler.wait_until_ready(model_name, 100, max_wait=0.1)
        assert ready is False  # Should fail because wait too long

    def test_multiple_models_independent(self, scheduler):
        """Test that different models are tracked independently."""
        model1 = "openai/gpt-4o-mini"
        model2 = "openai/gpt-4o"

        # Make requests to model1
        scheduler.record_request(model1, 1000)

        # Should not affect model2
        can_proceed, wait_time = scheduler.can_proceed(model2, 1000)
        assert can_proceed is True
        assert wait_time == 0.0

    def test_sliding_window_expiry(self, scheduler, rate_tracker):
        """Test that old requests expire from sliding window."""
        model_name = "openai/gpt-4o-mini"

        # Record a request
        scheduler.record_request(model_name, 1000)

        # Check usage
        usage = rate_tracker.get_usage_stats(model_name)
        assert usage["requests_per_minute"]["current"] == 1

        # Mock time to be 61 seconds in the future (outside 60s window)
        with mock.patch("time.time", return_value=time.time() + 61):
            usage = rate_tracker.get_usage_stats(model_name)
            assert usage["requests_per_minute"]["current"] == 0  # Should have expired
            assert usage["tokens_per_minute"]["current"] == 0

    def test_repr(self, scheduler):
        """Test string representation."""
        repr_str = repr(scheduler)
        assert "ProactiveRateLimitScheduler" in repr_str
        assert "safety_margin=2" in repr_str

    def test_different_safety_margins(self, rate_tracker):
        """Test schedulers with different safety margins."""
        model_name = "openai/gpt-4o-mini"
        limits = rate_tracker.model_limits[model_name]
        rpm = limits.requests_per_minute

        # Scheduler with safety_margin=1 (N-1)
        scheduler1 = ProactiveRateLimitScheduler(rate_tracker, safety_margin=1)
        status1 = scheduler1.get_status(model_name)
        assert status1["safe_request_limit"] == rpm - 1

        # Scheduler with safety_margin=5 (N-5)
        scheduler5 = ProactiveRateLimitScheduler(rate_tracker, safety_margin=5)
        status5 = scheduler5.get_status(model_name)
        assert status5["safe_request_limit"] == rpm - 5

    def test_unknown_model(self, scheduler):
        """Test behavior with unknown model."""
        unknown_model = "unknown/model-xxx"

        # Should allow request (fail-open)
        can_proceed, wait_time = scheduler.can_proceed(unknown_model, 1000)
        assert can_proceed is True
        assert wait_time == 0.0

        # Status should return error
        status = scheduler.get_status(unknown_model)
        assert "error" in status

    @pytest.mark.slow
    @pytest.mark.integration
    def test_integration_realistic_usage(self, scheduler):
        """Test realistic usage pattern with multiple requests."""
        model_name = "openai/gpt-4o-mini"

        # Simulate making several requests with proper scheduling
        for i in range(10):
            # Check if we can proceed
            can_proceed, wait_time = scheduler.can_proceed(model_name, 1000)

            if not can_proceed:
                # Wait as instructed
                time.sleep(wait_time)
                can_proceed, wait_time = scheduler.can_proceed(model_name, 1000)

            # Should now be able to proceed
            assert can_proceed is True

            # Make the request
            scheduler.record_request(model_name, 1000)

        # All requests should have succeeded
        status = scheduler.get_status(model_name)
        assert status["current_requests"] == 10
