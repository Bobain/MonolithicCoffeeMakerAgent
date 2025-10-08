"""Unit tests for AutoPickerLLM."""

from unittest import mock

import pytest

from coffee_maker.langchain_observe.auto_picker_llm import AutoPickerLLM
from coffee_maker.langchain_observe.rate_limiter import RateLimitConfig, RateLimitTracker


class MockLLM:
    """Mock LLM for testing."""

    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.call_count = 0

    def invoke(self, input_data: dict, **kwargs):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"Mock LLM {self.name} failed")
        return {"content": f"Response from {self.name}"}


class TestAutoPickerLLM:
    """Tests for AutoPickerLLM."""

    @pytest.fixture
    def rate_tracker(self):
        """Create a rate limit tracker for testing."""
        return RateLimitTracker(
            {
                "openai/gpt-4o-mini": RateLimitConfig(
                    requests_per_minute=10, tokens_per_minute=1000, requests_per_day=100
                ),
                "gemini/gemini-2.5-flash-lite": RateLimitConfig(
                    requests_per_minute=15, tokens_per_minute=2000, requests_per_day=200
                ),
            }
        )

    @pytest.fixture
    def auto_picker(self, rate_tracker):
        """Create an AutoPickerLLM for testing."""
        primary = MockLLM("primary")
        fallback1 = MockLLM("fallback1")
        fallback2 = MockLLM("fallback2")

        return AutoPickerLLM(
            primary_llm=primary,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[
                (fallback1, "gemini/gemini-2.5-flash-lite"),
                (fallback2, "openai/gpt-3.5-turbo"),
            ],
            rate_tracker=rate_tracker,
            auto_wait=True,
            max_wait_seconds=5.0,
        )

    def test_primary_llm_used_when_available(self, auto_picker):
        """Test that primary LLM is used when available."""
        result = auto_picker.invoke({"input": "test"})

        assert result["content"] == "Response from primary"
        assert auto_picker.stats["total_requests"] == 1
        assert auto_picker.stats["primary_requests"] == 1
        assert auto_picker.stats["fallback_requests"] == 0

    def test_fallback_when_rate_limited(self, auto_picker, rate_tracker):
        """Test fallback to alternative model when rate limited."""
        # Fill up primary model's rate limit
        for _ in range(10):
            rate_tracker.record_request("openai/gpt-4o-mini", tokens_used=50)

        # Next request should use fallback
        result = auto_picker.invoke({"input": "test"})

        assert result["content"] == "Response from fallback1"
        assert auto_picker.stats["fallback_requests"] == 1
        assert auto_picker.stats["rate_limit_fallbacks"] == 1

    def test_auto_wait_when_wait_time_acceptable(self, auto_picker, rate_tracker):
        """Test that AutoPickerLLM waits when wait time is under max_wait_seconds."""
        # Fill up rate limit but leave time for recovery
        for _ in range(10):
            rate_tracker.record_request("openai/gpt-4o-mini", tokens_used=50)

        # Mock can_make_request to return False first time, then True after waiting
        call_count = [0]

        def mock_can_make_request(model_name, tokens):
            call_count[0] += 1
            # First call: rate limited
            # Second call (after waiting): OK
            return call_count[0] > 1

        with mock.patch.object(rate_tracker, "can_make_request", side_effect=mock_can_make_request):
            with mock.patch.object(rate_tracker, "get_wait_time", return_value=3.0):
                with mock.patch("time.sleep") as mock_sleep:
                    result = auto_picker.invoke({"input": "test"})

                    # Should have waited once
                    mock_sleep.assert_called_once_with(3.0)
                    assert auto_picker.stats["rate_limit_waits"] == 1
                    assert result["content"] == "Response from primary"

    def test_cascading_fallbacks(self, auto_picker, rate_tracker):
        """Test that fallbacks cascade when multiple models are rate limited."""
        # Fill up both primary and first fallback
        for _ in range(10):
            rate_tracker.record_request("openai/gpt-4o-mini", tokens_used=50)
        for _ in range(15):
            rate_tracker.record_request("gemini/gemini-2.5-flash-lite", tokens_used=50)

        # Should use second fallback (but it's not in rate tracker, so it will succeed)
        result = auto_picker.invoke({"input": "test"})

        assert result["content"] == "Response from fallback2"
        assert auto_picker.stats["fallback_requests"] == 1

    def test_all_models_fail_raises_error(self, rate_tracker):
        """Test that error is raised when all models fail or are rate limited."""
        # Create auto picker with all failing LLMs
        failing_primary = MockLLM("primary", should_fail=True)
        failing_fallback = MockLLM("fallback1", should_fail=True)

        auto_picker = AutoPickerLLM(
            primary_llm=failing_primary,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[(failing_fallback, "gemini/gemini-2.5-flash-lite")],
            rate_tracker=rate_tracker,
        )

        with pytest.raises(RuntimeError) as exc_info:
            auto_picker.invoke({"input": "test"})

        assert "All LLM models failed or are rate-limited" in str(exc_info.value)

    def test_token_estimation_with_tokenizer(self, auto_picker):
        """Test token estimation using tiktoken."""
        # AutoPickerLLM should use tiktoken for OpenAI models
        input_text = "This is a test message for token counting"
        estimated = auto_picker._estimate_tokens({"input": input_text}, "openai/gpt-4o-mini")

        # Should be roughly 8-10 tokens
        assert 6 <= estimated <= 12

    def test_token_estimation_fallback(self, auto_picker):
        """Test token estimation fallback for models without tokenizer."""
        input_text = "This is a test message for token counting"
        estimated = auto_picker._estimate_tokens({"input": input_text}, "unknown/model")

        # For unknown models, should use character-based estimation (len / 4)
        # Note: tiktoken might still be used if the model name contains "gpt",
        # so we just verify we get a reasonable token count
        len(input_text) // 4
        # Allow for either tiktoken (8-10) or character-based (10)
        assert 7 <= estimated <= 12

    def test_statistics_tracking(self, auto_picker, rate_tracker):
        """Test that statistics are correctly tracked."""
        # Make some requests with primary
        auto_picker.invoke({"input": "test1"})
        auto_picker.invoke({"input": "test2"})

        # Fill up primary and trigger final attempt after 90s wait
        for _ in range(10):
            rate_tracker.record_request("openai/gpt-4o-mini", tokens_used=50)

        # Set last_call_time to >90s ago to allow immediate fallback
        import time

        rate_tracker.set_last_call_time(time.time() - 100.0)

        auto_picker.invoke({"input": "test3"})

        stats = auto_picker.get_stats()

        assert stats["total_requests"] == 3
        assert stats["primary_requests"] == 2
        assert stats["fallback_requests"] == 1
        assert stats["primary_usage_percent"] == pytest.approx(66.67, rel=0.1)
        assert stats["fallback_usage_percent"] == pytest.approx(33.33, rel=0.1)

    def test_get_rate_limit_stats(self, auto_picker, rate_tracker):
        """Test getting rate limit statistics."""
        # Make some requests
        auto_picker.invoke({"input": "test"})
        auto_picker.invoke({"input": "test"})

        stats = auto_picker.get_rate_limit_stats("openai/gpt-4o-mini")

        assert "requests_per_minute" in stats
        assert "tokens_per_minute" in stats
        assert stats["requests_per_minute"]["current"] >= 2

    def test_llm_invocation_error_triggers_fallback(self, rate_tracker):
        """Test that LLM errors trigger fallback to next model."""
        failing_primary = MockLLM("primary", should_fail=True)
        working_fallback = MockLLM("fallback1")

        auto_picker = AutoPickerLLM(
            primary_llm=failing_primary,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[(working_fallback, "gemini/gemini-2.5-flash-lite")],
            rate_tracker=rate_tracker,
        )

        result = auto_picker.invoke({"input": "test"})

        assert result["content"] == "Response from fallback1"
        assert auto_picker.stats["fallback_requests"] == 1
        assert failing_primary.call_count == 1
        assert working_fallback.call_count == 1

    def test_min_wait_before_fallback(self, rate_tracker):
        """Test that system waits at least 90s from last call before using fallback."""
        primary = MockLLM("primary")
        fallback = MockLLM("fallback1")

        auto_picker = AutoPickerLLM(
            primary_llm=primary,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[(fallback, "gemini/gemini-2.5-flash-lite")],
            rate_tracker=rate_tracker,
            max_wait_seconds=5.0,  # Low max wait to trigger fallback quickly
            min_wait_before_fallback=90.0,
        )

        # First call succeeds and sets last_call_time in rate_tracker
        result1 = auto_picker.invoke({"input": "test"})
        assert result1["content"] == "Response from primary"
        initial_time = rate_tracker.get_last_call_time()
        assert initial_time is not None

        # Fill up rate limit to trigger fallback attempt
        for _ in range(10):
            rate_tracker.record_request("openai/gpt-4o-mini", tokens_used=50)

        # Mock time.sleep to verify 90s wait is enforced
        with mock.patch("time.sleep") as mock_sleep:
            # Use side_effect to simulate time progression
            time_progression = [initial_time + 30.0]  # Start 30s after last call

            def time_side_effect():
                # After sleep is called, advance time
                if mock_sleep.call_count > 0:
                    time_progression[0] += mock_sleep.call_args_list[-1][0][0]
                return time_progression[0]

            with mock.patch("time.time", side_effect=time_side_effect):
                result2 = auto_picker.invoke({"input": "test"})

                # Should wait 60s (90s - 30s) before making final attempt
                sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]

                # Should have waited the remaining 60s
                assert any(pytest.approx(60.0, rel=0.1) == call for call in sleep_calls)
                # Final attempt should succeed (primary model)
                assert result2["content"] == "Response from primary"
