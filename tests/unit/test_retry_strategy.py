"""Unit tests for retry strategies."""

import time
from unittest import mock

import pytest

from coffee_maker.langchain_observe.strategies.retry import ExponentialBackoffRetry


class TestExponentialBackoffRetry:
    """Tests for ExponentialBackoffRetry strategy."""

    @pytest.fixture
    def retry_strategy(self):
        """Create a retry strategy with default settings."""
        return ExponentialBackoffRetry(
            max_retries=3,
            backoff_base=2.0,
            max_wait_seconds=300.0,
            min_wait_before_fallback=90.0,
        )

    def test_initialization(self, retry_strategy):
        """Test retry strategy initializes with correct parameters."""
        assert retry_strategy.max_retries == 3
        assert retry_strategy.backoff_base == 2.0
        assert retry_strategy.max_wait_seconds == 300.0
        assert retry_strategy.min_wait_before_fallback == 90.0

    def test_should_retry_within_limits(self, retry_strategy):
        """Test that retry is allowed within max_retries and max_wait."""
        # Attempt 0, 1, 2 should all retry
        assert retry_strategy.should_retry(attempt=0, elapsed_time=0)
        assert retry_strategy.should_retry(attempt=1, elapsed_time=10)
        assert retry_strategy.should_retry(attempt=2, elapsed_time=20)

    def test_should_not_retry_after_max_retries(self, retry_strategy):
        """Test that retry is not allowed after max_retries."""
        # Attempt 3 exceeds max_retries=3
        assert not retry_strategy.should_retry(attempt=3, elapsed_time=0)
        assert not retry_strategy.should_retry(attempt=4, elapsed_time=0)

    def test_should_not_retry_after_max_wait(self, retry_strategy):
        """Test that retry is not allowed after max_wait_seconds."""
        # Even on attempt 0, if we've waited too long, don't retry
        assert not retry_strategy.should_retry(attempt=0, elapsed_time=301)
        assert not retry_strategy.should_retry(attempt=1, elapsed_time=400)

    def test_exponential_backoff_calculation(self, retry_strategy):
        """Test exponential backoff time calculation."""
        # base=2.0, so: 2^0=1, 2^1=2, 2^2=4, 2^3=8
        assert retry_strategy.get_backoff_time(0) == 1.0
        assert retry_strategy.get_backoff_time(1) == 2.0
        assert retry_strategy.get_backoff_time(2) == 4.0
        assert retry_strategy.get_backoff_time(3) == 8.0

    def test_custom_backoff_base(self):
        """Test exponential backoff with custom base."""
        retry = ExponentialBackoffRetry(backoff_base=3.0)
        # base=3.0, so: 3^0=1, 3^1=3, 3^2=9, 3^3=27
        assert retry.get_backoff_time(0) == 1.0
        assert retry.get_backoff_time(1) == 3.0
        assert retry.get_backoff_time(2) == 9.0
        assert retry.get_backoff_time(3) == 27.0

    def test_should_not_fallback_before_min_wait(self, retry_strategy):
        """Test that fallback is blocked if min_wait_before_fallback not reached."""
        # Retries exhausted, but only 30s since last call (< 90s min)
        assert not retry_strategy.should_fallback(attempt=3, elapsed_time=100, time_since_last_call=30.0)

    def test_should_fallback_after_min_wait(self, retry_strategy):
        """Test that fallback is allowed after min_wait_before_fallback."""
        # Retries exhausted AND 100s since last call (> 90s min)
        assert retry_strategy.should_fallback(attempt=3, elapsed_time=100, time_since_last_call=100.0)

    def test_should_fallback_when_wait_exceeded(self, retry_strategy):
        """Test fallback when max_wait_seconds exceeded."""
        # Wait exceeded (350s > 300s max) AND enough time since last call
        assert retry_strategy.should_fallback(attempt=2, elapsed_time=350, time_since_last_call=100.0)

    def test_should_not_fallback_within_limits(self, retry_strategy):
        """Test that fallback is not triggered when within limits."""
        # Still have retries left, haven't exceeded wait time
        assert not retry_strategy.should_fallback(attempt=1, elapsed_time=50, time_since_last_call=100.0)

    def test_wait_remaining_time(self, retry_strategy):
        """Test calculation of remaining wait time before fallback."""
        # Need to wait 90s, already waited 30s -> 60s remaining
        assert retry_strategy.wait_remaining_time(time_since_last_call=30.0) == 60.0

        # Need to wait 90s, already waited 100s -> 0s remaining (can fallback)
        assert retry_strategy.wait_remaining_time(time_since_last_call=100.0) == 0.0

        # Exactly at threshold
        assert retry_strategy.wait_remaining_time(time_since_last_call=90.0) == 0.0

    def test_enforce_min_wait_already_satisfied(self, retry_strategy):
        """Test enforce_min_wait when already waited long enough."""
        with mock.patch("time.sleep") as mock_sleep:
            # Already waited 100s (> 90s min), should not sleep
            retry_strategy.enforce_min_wait(time_since_last_call=100.0)
            mock_sleep.assert_not_called()

    def test_enforce_min_wait_needs_waiting(self, retry_strategy):
        """Test enforce_min_wait when need to wait more."""
        with mock.patch("time.sleep") as mock_sleep:
            # Waited 30s, need 90s -> should sleep 60s
            retry_strategy.enforce_min_wait(time_since_last_call=30.0)
            mock_sleep.assert_called_once_with(60.0)

    def test_repr(self, retry_strategy):
        """Test string representation."""
        repr_str = repr(retry_strategy)
        assert "ExponentialBackoffRetry" in repr_str
        assert "max_retries=3" in repr_str
        assert "backoff_base=2.0" in repr_str
        assert "max_wait_seconds=300.0" in repr_str
        assert "min_wait_before_fallback=90.0" in repr_str

    def test_integration_retry_then_fallback(self):
        """Test complete retry sequence followed by fallback."""
        retry = ExponentialBackoffRetry(
            max_retries=2, backoff_base=2.0, max_wait_seconds=100.0, min_wait_before_fallback=10.0
        )

        time.time()

        # Attempt 0: should retry
        assert retry.should_retry(0, elapsed_time=0)
        backoff = retry.get_backoff_time(0)
        assert backoff == 1.0

        # Attempt 1: should retry
        assert retry.should_retry(1, elapsed_time=1)
        backoff = retry.get_backoff_time(1)
        assert backoff == 2.0

        # Attempt 2: at max_retries, no more retries
        assert not retry.should_retry(2, elapsed_time=3)

        # Should fallback if enough time passed since last call
        # Simulate 15s since last call (> 10s min)
        assert retry.should_fallback(attempt=2, elapsed_time=3, time_since_last_call=15.0)

    def test_edge_case_zero_retries(self):
        """Test strategy with zero retries (immediate fallback)."""
        retry = ExponentialBackoffRetry(max_retries=0)

        # Even attempt 0 should not retry
        assert not retry.should_retry(0, elapsed_time=0)

        # Should fallback immediately (if min_wait satisfied)
        assert retry.should_fallback(attempt=0, elapsed_time=0, time_since_last_call=100.0)

    def test_edge_case_very_high_retries(self):
        """Test strategy with very high retry count."""
        retry = ExponentialBackoffRetry(max_retries=100)

        # Should allow many retries as long as within max_wait
        assert retry.should_retry(50, elapsed_time=0)
        assert retry.should_retry(99, elapsed_time=0)

        # But not if we've exceeded max_wait
        assert not retry.should_retry(50, elapsed_time=301)

    def test_different_backoff_bases(self):
        """Test that different backoff bases produce expected wait times."""
        # Linear (base=1.0) - always 1 second
        linear = ExponentialBackoffRetry(backoff_base=1.0)
        assert linear.get_backoff_time(0) == 1.0
        assert linear.get_backoff_time(5) == 1.0

        # Square (base=2.0)
        square = ExponentialBackoffRetry(backoff_base=2.0)
        assert square.get_backoff_time(0) == 1.0
        assert square.get_backoff_time(4) == 16.0

        # Aggressive (base=5.0)
        aggressive = ExponentialBackoffRetry(backoff_base=5.0)
        assert aggressive.get_backoff_time(0) == 1.0
        assert aggressive.get_backoff_time(3) == 125.0
