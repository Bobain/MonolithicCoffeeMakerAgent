"""Unit tests for RateLimitTracker."""

import time
from unittest import mock

import pytest

from coffee_maker.llm.rate_limiting.limiter import RateLimitConfig, RateLimitTracker


class TestRateLimitConfig:
    """Tests for RateLimitConfig dataclass."""

    def test_create_config(self):
        """Test creating a rate limit configuration."""
        config = RateLimitConfig(requests_per_minute=100, tokens_per_minute=50000, requests_per_day=1000)

        assert config.requests_per_minute == 100
        assert config.tokens_per_minute == 50000
        assert config.requests_per_day == 1000

    def test_config_without_daily_limit(self):
        """Test configuration without daily limit."""
        config = RateLimitConfig(requests_per_minute=100, tokens_per_minute=50000)

        assert config.requests_per_day is None


class TestRateLimitTracker:
    """Tests for RateLimitTracker."""

    @pytest.fixture
    def tracker(self):
        """Create a rate limit tracker for testing."""
        return RateLimitTracker(
            {
                "test-model": RateLimitConfig(requests_per_minute=10, tokens_per_minute=1000, requests_per_day=100),
                "slow-model": RateLimitConfig(requests_per_minute=2, tokens_per_minute=500, requests_per_day=10),
            }
        )

    def test_can_make_request_initially(self, tracker):
        """Test that requests can be made initially."""
        assert tracker.can_make_request("test-model", estimated_tokens=100)

    def test_can_make_request_unknown_model(self, tracker):
        """Test that unknown models are allowed (with warning)."""
        assert tracker.can_make_request("unknown-model", estimated_tokens=100)

    def test_rpm_limit(self, tracker):
        """Test that requests per minute limit is enforced."""
        # Make 10 requests (the limit)
        for i in range(10):
            assert tracker.can_make_request("test-model", estimated_tokens=10)
            tracker.record_request("test-model", tokens_used=10)

        # 11th request should be blocked
        assert not tracker.can_make_request("test-model", estimated_tokens=10)

    def test_tpm_limit(self, tracker):
        """Test that tokens per minute limit is enforced."""
        # Use up most of the token budget
        assert tracker.can_make_request("test-model", estimated_tokens=900)
        tracker.record_request("test-model", tokens_used=900)

        # Request that would exceed limit should be blocked
        assert not tracker.can_make_request("test-model", estimated_tokens=200)

        # Request within limit should be allowed
        assert tracker.can_make_request("test-model", estimated_tokens=50)

    def test_daily_limit(self, tracker):
        """Test that daily request limit is enforced."""
        # Make requests up to daily limit
        for i in range(100):
            tracker.record_request("test-model", tokens_used=1)

        # Next request should be blocked
        assert not tracker.can_make_request("test-model", estimated_tokens=1)

    def test_cleanup_old_requests(self, tracker):
        """Test that old requests are cleaned up after 60 seconds."""
        # Record a request
        tracker.record_request("test-model", tokens_used=100)

        # Mock time to be 61 seconds later
        with mock.patch("time.time", return_value=time.time() + 61):
            tracker._cleanup_old_requests("test-model")

        # Request history should be empty
        assert len(tracker._request_history["test-model"]) == 0

    def test_get_wait_time_rpm(self, tracker):
        """Test wait time calculation for RPM limit."""
        # Fill up RPM limit
        for i in range(10):
            tracker.record_request("test-model", tokens_used=10)

        wait_time = tracker.get_wait_time("test-model", estimated_tokens=10)

        # Should need to wait close to 60 seconds
        assert 55 < wait_time <= 60

    def test_get_wait_time_tpm(self, tracker):
        """Test wait time calculation for TPM limit."""
        # Use most of token budget
        tracker.record_request("test-model", tokens_used=950)

        wait_time = tracker.get_wait_time("test-model", estimated_tokens=100)

        # Should need to wait
        assert wait_time > 0

    def test_get_wait_time_no_wait_needed(self, tracker):
        """Test wait time when no waiting is needed."""
        wait_time = tracker.get_wait_time("test-model", estimated_tokens=10)
        assert wait_time == 0.0

    def test_get_usage_stats(self, tracker):
        """Test getting usage statistics."""
        # Make some requests
        tracker.record_request("test-model", tokens_used=100)
        tracker.record_request("test-model", tokens_used=200)

        stats = tracker.get_usage_stats("test-model")

        assert stats["requests_per_minute"]["current"] == 2
        assert stats["requests_per_minute"]["limit"] == 10
        assert stats["tokens_per_minute"]["current"] == 300
        assert stats["tokens_per_minute"]["limit"] == 1000
        assert stats["requests_today"] == 2

    def test_daily_reset(self, tracker):
        """Test that daily count resets after 24 hours."""
        # Make some requests
        tracker.record_request("test-model", tokens_used=10)
        assert tracker._daily_requests["test-model"] == 1

        # Mock time to be 24+ hours later
        with mock.patch("time.time", return_value=time.time() + 86401):
            tracker._reset_daily_count_if_needed("test-model")

        assert tracker._daily_requests["test-model"] == 0
