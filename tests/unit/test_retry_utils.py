"""Unit tests for coffee_maker.langfuse_observe.retry_utils module."""

import time
from unittest.mock import Mock

import pytest

from coffee_maker.langfuse_observe.retry import (
    RetryConfig,
    RetryExhausted,
    with_conditional_retry,
    with_retry,
)


class TestRetryConfig:
    """Tests for RetryConfig class."""

    def test_default_initialization(self):
        """Should initialize with default values."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.backoff_base == 2.0
        assert config.max_backoff == 60.0
        assert config.retriable_exceptions == (Exception,)
        assert config.should_retry_predicate is None

    def test_custom_initialization(self):
        """Should initialize with custom values."""
        config = RetryConfig(
            max_attempts=5,
            backoff_base=3.0,
            max_backoff=120.0,
            retriable_exceptions=(ValueError, TypeError),
        )
        assert config.max_attempts == 5
        assert config.backoff_base == 3.0
        assert config.max_backoff == 120.0
        assert config.retriable_exceptions == (ValueError, TypeError)

    def test_calculate_backoff_exponential(self):
        """Should calculate exponential backoff."""
        config = RetryConfig(backoff_base=2.0, max_backoff=60.0)

        assert config.calculate_backoff(0) == 1.0  # 2^0
        assert config.calculate_backoff(1) == 2.0  # 2^1
        assert config.calculate_backoff(2) == 4.0  # 2^2
        assert config.calculate_backoff(3) == 8.0  # 2^3
        assert config.calculate_backoff(4) == 16.0  # 2^4

    def test_calculate_backoff_respects_max(self):
        """Should cap backoff at max_backoff."""
        config = RetryConfig(backoff_base=2.0, max_backoff=10.0)

        assert config.calculate_backoff(0) == 1.0
        assert config.calculate_backoff(3) == 8.0
        assert config.calculate_backoff(4) == 10.0  # capped at max_backoff
        assert config.calculate_backoff(10) == 10.0  # still capped

    def test_is_retriable_default(self):
        """Should consider all exceptions retriable by default."""
        config = RetryConfig()

        assert config.is_retriable(ValueError("test"))
        assert config.is_retriable(TypeError("test"))
        assert config.is_retriable(Exception("test"))

    def test_is_retriable_specific_exceptions(self):
        """Should only retry specific exception types."""
        config = RetryConfig(retriable_exceptions=(ValueError, TypeError))

        assert config.is_retriable(ValueError("test"))
        assert config.is_retriable(TypeError("test"))
        assert not config.is_retriable(KeyError("test"))
        assert not config.is_retriable(Exception("test"))

    def test_is_retriable_with_predicate(self):
        """Should use custom predicate when provided."""

        def is_rate_limit(error):
            return "rate limit" in str(error).lower()

        config = RetryConfig(should_retry_predicate=is_rate_limit)

        assert config.is_retriable(ValueError("Rate limit exceeded"))
        assert config.is_retriable(Exception("API rate limit"))
        assert not config.is_retriable(ValueError("Other error"))

    def test_is_retriable_predicate_and_type(self):
        """Should check both exception type and predicate."""

        def is_rate_limit(error):
            return "rate limit" in str(error).lower()

        config = RetryConfig(retriable_exceptions=(ValueError,), should_retry_predicate=is_rate_limit)

        assert config.is_retriable(ValueError("Rate limit exceeded"))
        assert not config.is_retriable(ValueError("Other error"))
        assert not config.is_retriable(TypeError("Rate limit exceeded"))


class TestWithRetry:
    """Tests for with_retry decorator."""

    def test_success_on_first_attempt(self):
        """Should return immediately if function succeeds."""
        mock_func = Mock(return_value="success")

        @with_retry(max_attempts=3)
        def test_func():
            return mock_func()

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_success_after_retries(self):
        """Should retry and eventually succeed."""
        mock_func = Mock(side_effect=[ValueError("fail 1"), ValueError("fail 2"), "success"])

        @with_retry(max_attempts=3, backoff_base=0.01)  # Fast backoff for testing
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_exhausted(self):
        """Should raise RetryExhausted after max attempts."""
        mock_func = Mock(side_effect=ValueError("always fails"))

        @with_retry(max_attempts=3, backoff_base=0.01)
        def test_func():
            mock_func()

        with pytest.raises(RetryExhausted) as exc_info:
            test_func()

        assert mock_func.call_count == 3
        assert isinstance(exc_info.value.original_error, ValueError)
        assert exc_info.value.attempts == 3
        assert "always fails" in str(exc_info.value.original_error)

    def test_non_retriable_exception(self):
        """Should not retry non-retriable exceptions."""
        mock_func = Mock(side_effect=KeyError("not retriable"))

        @with_retry(max_attempts=3, retriable_exceptions=(ValueError,))
        def test_func():
            mock_func()

        with pytest.raises(KeyError):
            test_func()

        assert mock_func.call_count == 1  # No retries

    def test_custom_retry_predicate(self):
        """Should use custom predicate to determine retry."""

        def is_transient(error):
            return "transient" in str(error).lower()

        mock_func = Mock(
            side_effect=[
                ValueError("transient error"),  # Will retry
                ValueError("permanent error"),  # Will not retry
            ]
        )

        @with_retry(max_attempts=3, should_retry_predicate=is_transient, backoff_base=0.01)
        def test_func():
            mock_func()

        with pytest.raises(ValueError) as exc_info:
            test_func()

        assert "permanent error" in str(exc_info.value)
        assert mock_func.call_count == 2

    def test_backoff_timing(self):
        """Should wait with exponential backoff between retries."""
        mock_func = Mock(side_effect=[ValueError("1"), ValueError("2"), "success"])

        @with_retry(max_attempts=3, backoff_base=2.0)
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        start = time.time()
        result = test_func()
        elapsed = time.time() - start

        assert result == "success"
        # Should wait: 1s (2^0) + 2s (2^1) = 3s minimum
        assert elapsed >= 3.0
        assert elapsed < 4.0  # Allow some overhead

    def test_on_retry_callback(self):
        """Should call on_retry callback before each retry."""
        callback_mock = Mock()
        mock_func = Mock(side_effect=[ValueError("1"), ValueError("2"), "success"])

        @with_retry(max_attempts=3, backoff_base=0.01, on_retry=callback_mock)
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        result = test_func()

        assert result == "success"
        assert callback_mock.call_count == 2  # Called before retry 1 and 2

        # Check callback arguments
        first_call = callback_mock.call_args_list[0]
        assert isinstance(first_call[0][0], ValueError)  # error
        assert first_call[0][1] == 1  # attempt number

    def test_on_retry_callback_exception(self):
        """Should continue retry even if callback fails."""

        def failing_callback(error, attempt):
            raise RuntimeError("Callback failed")

        mock_func = Mock(side_effect=[ValueError("1"), "success"])

        @with_retry(max_attempts=3, backoff_base=0.01, on_retry=failing_callback)
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        # Should succeed despite callback failure
        result = test_func()
        assert result == "success"

    def test_preserves_function_metadata(self):
        """Should preserve original function name and docstring."""

        @with_retry(max_attempts=3)
        def my_function():
            """My function docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring."

    def test_max_backoff_limit(self):
        """Should respect max_backoff limit."""
        mock_func = Mock(side_effect=[ValueError("1"), ValueError("2"), ValueError("3"), "success"])

        @with_retry(
            max_attempts=4,
            backoff_base=10.0,
            max_backoff=5.0,  # Would be 10, 100, 1000 without max  # Cap at 5 seconds
        )
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        start = time.time()
        result = test_func()
        elapsed = time.time() - start

        assert result == "success"
        # Should wait: 1s (10^0) + 5s (capped) + 5s (capped) = 11s minimum
        # But we use base=10, so 10^0=1, 10^1=10 (capped to 5), 10^2=100 (capped to 5)
        # Total: 1 + 5 + 5 = 11s
        assert elapsed >= 11.0
        assert elapsed < 13.0


class TestWithConditionalRetry:
    """Tests for with_conditional_retry decorator."""

    def test_success_on_first_attempt(self):
        """Should return immediately if function succeeds."""
        condition_mock = Mock()
        mock_func = Mock(return_value="success")

        @with_conditional_retry(condition_check=condition_mock, max_attempts=3)
        def test_func():
            return mock_func()

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 1
        assert condition_mock.call_count == 0  # Not called on success

    def test_retry_with_cleanup(self):
        """Should retry with cleanup function."""
        cleanup_mock = Mock()

        def condition_check(error):
            if "retriable" in str(error):
                return True, cleanup_mock
            return False, None

        mock_func = Mock(side_effect=[ValueError("retriable error"), "success"])

        @with_conditional_retry(condition_check=condition_check, max_attempts=3, backoff_base=0.01)
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 2
        assert cleanup_mock.call_count == 1  # Cleanup called before retry

    def test_no_retry_when_condition_false(self):
        """Should not retry when condition returns False."""
        cleanup_mock = Mock()

        def condition_check(error):
            return False, None

        mock_func = Mock(side_effect=ValueError("non-retriable"))

        @with_conditional_retry(condition_check=condition_check, max_attempts=3)
        def test_func():
            mock_func()

        with pytest.raises(ValueError) as exc_info:
            test_func()

        assert mock_func.call_count == 1
        assert cleanup_mock.call_count == 0

    def test_cleanup_failure_does_not_block_retry(self):
        """Should continue retry even if cleanup fails."""

        def failing_cleanup():
            raise RuntimeError("Cleanup failed")

        def condition_check(error):
            return True, failing_cleanup

        mock_func = Mock(side_effect=[ValueError("1"), "success"])

        @with_conditional_retry(condition_check=condition_check, max_attempts=3, backoff_base=0.01)
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        # Should succeed despite cleanup failure
        result = test_func()
        assert result == "success"

    def test_max_attempts_exhausted(self):
        """Should raise error after max attempts."""
        cleanup_mock = Mock()

        def condition_check(error):
            return True, cleanup_mock

        mock_func = Mock(side_effect=ValueError("always fails"))

        @with_conditional_retry(condition_check=condition_check, max_attempts=2, backoff_base=0.01)
        def test_func():
            mock_func()

        with pytest.raises(ValueError):
            test_func()

        assert mock_func.call_count == 2
        assert cleanup_mock.call_count == 1  # Only called once (not on last attempt)

    def test_backoff_timing(self):
        """Should wait with backoff between retries."""
        cleanup_mock = Mock()

        def condition_check(error):
            return True, cleanup_mock

        mock_func = Mock(side_effect=[ValueError("1"), ValueError("2"), "success"])

        @with_conditional_retry(condition_check=condition_check, max_attempts=3, backoff_base=2.0)
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        start = time.time()
        result = test_func()
        elapsed = time.time() - start

        assert result == "success"
        # Should wait: 1s (2^0) + 2s (2^1) = 3s minimum
        assert elapsed >= 3.0
        assert elapsed < 4.0

    def test_no_cleanup_function(self):
        """Should handle case where cleanup function is None."""

        def condition_check(error):
            return True, None  # Retry but no cleanup

        mock_func = Mock(side_effect=[ValueError("1"), "success"])

        @with_conditional_retry(condition_check=condition_check, max_attempts=3, backoff_base=0.01)
        def test_func():
            result = mock_func()
            if isinstance(result, Exception):
                raise result
            return result

        result = test_func()
        assert result == "success"


class TestRetryExhausted:
    """Tests for RetryExhausted exception."""

    def test_exception_attributes(self):
        """Should store original error and attempt count."""
        original = ValueError("original error")
        exc = RetryExhausted(original, 5)

        assert exc.original_error is original
        assert exc.attempts == 5

    def test_exception_message(self):
        """Should include error details in message."""
        original = ValueError("rate limit exceeded")
        exc = RetryExhausted(original, 3)

        message = str(exc)
        assert "3 attempts" in message
        assert "ValueError" in message
        assert "rate limit exceeded" in message

    def test_exception_chaining(self):
        """Should support exception chaining."""
        original = ValueError("original")
        exc = RetryExhausted(original, 2)

        assert exc.__cause__ is None  # Not automatically chained

        # But can be chained manually
        try:
            raise exc from original
        except RetryExhausted as e:
            assert e.__cause__ is original


class TestIntegration:
    """Integration tests for retry utilities."""

    def test_github_pending_review_scenario(self):
        """Simulate GitHub pending review conflict scenario."""
        cleanup_called = []

        def condition_check(error):
            if "pending review" in str(error).lower():

                def cleanup():
                    cleanup_called.append(True)

                return True, cleanup
            return False, None

        # Simulate API calls
        call_count = []

        @with_conditional_retry(condition_check=condition_check, max_attempts=2, backoff_base=0.01)
        def post_comment():
            call_count.append(1)
            if len(call_count) == 1:
                raise ValueError("Pending review conflict")
            return "Success"

        result = post_comment()

        assert result == "Success"
        assert len(call_count) == 2  # Initial + 1 retry
        assert len(cleanup_called) == 1  # Cleanup called once

    def test_mixed_retry_strategies(self):
        """Test combining multiple retry decorators."""
        # This tests that decorators can be stacked

        @with_retry(max_attempts=2, retriable_exceptions=(ValueError,), backoff_base=0.01)
        @with_retry(max_attempts=2, retriable_exceptions=(TypeError,), backoff_base=0.01)
        def multi_retry_func(counter):
            counter["calls"] += 1
            if counter["calls"] == 1:
                raise ValueError("First error")
            elif counter["calls"] == 2:
                raise TypeError("Second error")
            return "Success"

        counter = {"calls": 0}
        result = multi_retry_func(counter)

        assert result == "Success"
        assert counter["calls"] == 3
