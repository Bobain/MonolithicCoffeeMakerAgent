"""Unit tests for AutoPickerLLMRefactored.

These tests verify that the refactored AutoPickerLLM correctly:
1. Delegates scheduling/retry to ScheduledLLM
2. Handles fallback orchestration
3. Tracks costs
4. Manages context length checking
"""

from unittest import mock

import pytest

from coffee_maker.llm.auto_picker import (
    AutoPickerLLMRefactored,
    create_auto_picker_llm_refactored,
)


class MockScheduledLLM:
    """Mock ScheduledLLM for testing (simulates ScheduledLLM behavior)."""

    def __init__(self, name: str, should_fail: bool = False, fail_count: int = 0):
        self.name = name
        self.should_fail = should_fail
        self.fail_count = fail_count  # Number of times to fail before succeeding
        self.call_count = 0
        self.model_name = name

    def invoke(self, input_data: dict, **kwargs):
        """Invoke the mock LLM.

        This simulates ScheduledLLM which already handles:
        - Rate limiting
        - Retries with backoff
        - Scheduling
        """
        self.call_count += 1

        # Simulate temporary failures (ScheduledLLM would handle retries)
        if self.call_count <= self.fail_count:
            raise RuntimeError(f"Rate limit error from {self.name}")

        if self.should_fail:
            # Permanent failure (ScheduledLLM exhausted all retries)
            raise RuntimeError(f"Mock LLM {self.name} permanently failed")

        # Success!
        return MockResponse(content=f"Response from {self.name}")


class MockResponse:
    """Mock LLM response."""

    def __init__(self, content: str, input_tokens: int = 100, output_tokens: int = 50):
        self.content = content
        self.response_metadata = {
            "usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }
        }


class MockCostCalculator:
    """Mock cost calculator for testing."""

    def __init__(self):
        self.calculations = []

    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int):
        """Calculate cost (mock)."""
        cost_info = {
            "input_cost": input_tokens * 0.0001,
            "output_cost": output_tokens * 0.0002,
            "total_cost": (input_tokens * 0.0001) + (output_tokens * 0.0002),
        }
        self.calculations.append((model_name, input_tokens, output_tokens, cost_info))
        return cost_info


class TestAutoPickerLLMRefactored:
    """Tests for refactored AutoPickerLLM."""

    @pytest.fixture
    def mock_cost_calculator(self):
        """Create mock cost calculator."""
        return MockCostCalculator()

    @pytest.fixture
    def auto_picker(self, mock_cost_calculator):
        """Create an AutoPickerLLMRefactored for testing."""
        primary = MockScheduledLLM("primary")
        fallback1 = MockScheduledLLM("fallback1")
        fallback2 = MockScheduledLLM("fallback2")

        return AutoPickerLLMRefactored(
            primary_llm=primary,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[
                (fallback1, "gemini/gemini-2.5-flash"),
                (fallback2, "anthropic/claude-3-5-haiku-20241022"),
            ],
            cost_calculator=mock_cost_calculator,
            enable_context_fallback=False,  # Disable for basic tests
        )

    def test_primary_llm_used_when_available(self, auto_picker):
        """Test that primary LLM is used when available."""
        result = auto_picker.invoke({"input": "test"})

        assert result.content == "Response from primary"
        assert auto_picker.stats["total_requests"] == 1
        assert auto_picker.stats["primary_requests"] == 1
        assert auto_picker.stats["fallback_requests"] == 0

    def test_fallback_when_primary_fails(self, auto_picker):
        """Test fallback to alternative model when primary fails.

        In the refactored version, ScheduledLLM handles retries internally.
        If primary raises an error, it means ScheduledLLM exhausted all retries.
        """
        # Make primary fail permanently (after ScheduledLLM retries)
        auto_picker.primary_llm.should_fail = True

        result = auto_picker.invoke({"input": "test"})

        # Should use first fallback
        assert result.content == "Response from fallback1"
        assert auto_picker.stats["total_requests"] == 1
        assert auto_picker.stats["primary_requests"] == 0
        assert auto_picker.stats["fallback_requests"] == 1

    def test_multiple_fallbacks(self, auto_picker):
        """Test cascading through multiple fallbacks."""
        # Make primary and first fallback fail
        auto_picker.primary_llm.should_fail = True
        auto_picker.fallback_llms[0][0].should_fail = True

        result = auto_picker.invoke({"input": "test"})

        # Should use second fallback
        assert result.content == "Response from fallback2"
        assert auto_picker.stats["fallback_requests"] == 1

    def test_all_models_fail_raises_error(self, auto_picker):
        """Test that RuntimeError is raised when all models fail."""
        # Make all models fail
        auto_picker.primary_llm.should_fail = True
        auto_picker.fallback_llms[0][0].should_fail = True
        auto_picker.fallback_llms[1][0].should_fail = True

        with pytest.raises(RuntimeError, match="All LLM models failed"):
            auto_picker.invoke({"input": "test"})

    def test_cost_tracking(self, auto_picker, mock_cost_calculator):
        """Test that costs are correctly tracked."""
        result = auto_picker.invoke({"input": "test"})

        # Verify cost was calculated
        assert len(mock_cost_calculator.calculations) == 1
        model_name, input_tokens, output_tokens, cost_info = mock_cost_calculator.calculations[0]

        assert model_name == "openai/gpt-4o-mini"
        assert input_tokens == 100
        assert output_tokens == 50
        assert cost_info["total_cost"] > 0

    def test_cost_tracking_with_fallback(self, auto_picker, mock_cost_calculator):
        """Test that costs are tracked correctly when using fallback."""
        auto_picker.primary_llm.should_fail = True

        result = auto_picker.invoke({"input": "test"})

        # Should track cost for fallback model
        assert len(mock_cost_calculator.calculations) == 1
        model_name, _, _, _ = mock_cost_calculator.calculations[0]
        assert model_name == "gemini/gemini-2.5-flash"

    def test_stats_tracking(self, auto_picker):
        """Test that statistics are correctly tracked."""
        # Make 3 successful requests to primary
        for _ in range(3):
            auto_picker.invoke({"input": "test"})

        # Make 2 requests that fall back
        auto_picker.primary_llm.should_fail = True
        for _ in range(2):
            auto_picker.invoke({"input": "test"})

        stats = auto_picker.get_stats()

        assert stats["total_requests"] == 5
        assert stats["primary_requests"] == 3
        assert stats["fallback_requests"] == 2
        assert stats["primary_usage_percent"] == 60.0
        assert stats["fallback_usage_percent"] == 40.0

    def test_context_length_checking_disabled(self, auto_picker):
        """Test that context checking can be disabled."""
        # Context checking is disabled in fixture
        assert auto_picker.enable_context_fallback is False

        # Should invoke without context checking
        result = auto_picker.invoke({"input": "test" * 10000})
        assert result.content == "Response from primary"

    def test_context_length_fallback(self, mock_cost_calculator):
        """Test context length fallback behavior."""
        # Create auto_picker with context checking enabled
        primary = MockScheduledLLM("primary")
        fallback = MockScheduledLLM("large-context-fallback")

        auto_picker = AutoPickerLLMRefactored(
            primary_llm=primary,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[(fallback, "anthropic/claude-3-5-sonnet-20241022")],
            cost_calculator=mock_cost_calculator,
            enable_context_fallback=True,
        )

        # Mock context length checking to trigger fallback
        with mock.patch.object(
            auto_picker,
            "_check_context_length",
            side_effect=[
                (False, 200000, 128000),  # Primary: too large
                (True, 200000, 200000),  # Fallback: fits
            ],
        ):
            with mock.patch.object(
                auto_picker,
                "_get_large_context_models",
                return_value=[(fallback, "anthropic/claude-3-5-sonnet-20241022")],
            ):
                result = auto_picker.invoke({"input": "test" * 50000})

                # Should use large-context fallback
                assert result.content == "Response from large-context-fallback"
                assert auto_picker.stats["context_fallbacks"] == 1

    def test_rate_limit_error_detection(self, auto_picker):
        """Test that rate limit errors are correctly detected for stats."""

        class RateLimitError(Exception):
            pass

        # Make primary raise rate limit error
        auto_picker.primary_llm.invoke = mock.Mock(side_effect=RuntimeError("Rate limit exceeded - 429"))

        # Should fall back to next model
        result = auto_picker.invoke({"input": "test"})

        assert result.content == "Response from fallback1"
        assert auto_picker.stats["rate_limit_fallbacks"] == 1

    def test_bind_method(self, auto_picker):
        """Test that bind method works correctly."""
        # Add bind method to mock LLMs
        auto_picker.primary_llm.bind = mock.Mock(return_value=auto_picker.primary_llm)
        auto_picker.fallback_llms[0][0].bind = mock.Mock(return_value=auto_picker.fallback_llms[0][0])

        # Call bind
        result = auto_picker.bind(temperature=0.5)

        # Should bind to primary and fallbacks
        auto_picker.primary_llm.bind.assert_called_once_with(temperature=0.5)
        auto_picker.fallback_llms[0][0].bind.assert_called_once_with(temperature=0.5)

        # Should return self for chaining
        assert result is auto_picker


class TestCreateAutoPickerLLMRefactored:
    """Tests for create_auto_picker_llm_refactored helper function."""

    def test_create_with_defaults(self):
        """Test creating AutoPickerLLMRefactored with default parameters."""
        with mock.patch("coffee_maker.langfuse_observe.llm.get_scheduled_llm") as mock_get_scheduled:
            # Mock get_scheduled_llm to return mock instances
            mock_get_scheduled.side_effect = lambda **kwargs: MockScheduledLLM(
                f"{kwargs['provider']}/{kwargs['model']}"
            )

            auto_picker = create_auto_picker_llm_refactored(
                primary_provider="openai",
                primary_model="gpt-4o-mini",
                fallback_configs=[
                    ("gemini", "gemini-2.5-flash"),
                ],
            )

            # Verify correct calls
            assert mock_get_scheduled.call_count == 2  # primary + 1 fallback

            # Verify AutoPickerLLMRefactored created correctly
            assert auto_picker.primary_model_name == "openai/gpt-4o-mini"
            assert len(auto_picker.fallback_llms) == 1
            assert auto_picker.fallback_llms[0][1] == "gemini/gemini-2.5-flash"

    def test_create_with_multiple_fallbacks(self):
        """Test creating with multiple fallbacks."""
        with mock.patch("coffee_maker.langfuse_observe.llm.get_scheduled_llm") as mock_get_scheduled:
            mock_get_scheduled.side_effect = lambda **kwargs: MockScheduledLLM(
                f"{kwargs['provider']}/{kwargs['model']}"
            )

            auto_picker = create_auto_picker_llm_refactored(
                primary_provider="openai",
                primary_model="gpt-4o-mini",
                fallback_configs=[
                    ("gemini", "gemini-2.5-flash"),
                    ("anthropic", "claude-3-5-haiku-20241022"),
                ],
                tier="tier2",
            )

            # Verify 3 LLMs created (primary + 2 fallbacks)
            assert mock_get_scheduled.call_count == 3
            assert len(auto_picker.fallback_llms) == 2

    def test_create_with_cost_calculator(self):
        """Test creating with cost calculator."""
        mock_cost_calc = MockCostCalculator()

        with mock.patch("coffee_maker.langfuse_observe.llm.get_scheduled_llm") as mock_get_scheduled:
            mock_get_scheduled.side_effect = lambda **kwargs: MockScheduledLLM(
                f"{kwargs['provider']}/{kwargs['model']}"
            )

            auto_picker = create_auto_picker_llm_refactored(
                primary_provider="openai",
                primary_model="gpt-4o-mini",
                fallback_configs=[],
                cost_calculator=mock_cost_calc,
            )

            # Verify cost calculator attached
            assert auto_picker.cost_calculator is mock_cost_calc
