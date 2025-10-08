"""Unit tests for FallbackStrategy implementations."""

import pytest

from coffee_maker.langchain_observe.strategies.fallback import (
    CostOptimizedFallback,
    SequentialFallback,
    SmartFallback,
    create_fallback_strategy,
)


class TestSequentialFallback:
    """Tests for SequentialFallback strategy."""

    @pytest.fixture
    def strategy(self):
        """Create strategy instance."""
        return SequentialFallback()

    def test_select_first_fallback(self, strategy):
        """Test that first fallback is always selected."""
        available = ["model1", "model2", "model3"]
        error = RuntimeError("Some error")

        result = strategy.select_next_fallback("failed_model", available, error)

        assert result == "model1"

    def test_select_empty_list(self, strategy):
        """Test with empty fallback list."""
        result = strategy.select_next_fallback("failed_model", [], RuntimeError())

        assert result is None

    def test_ignores_error_type(self, strategy):
        """Test that error type doesn't matter."""
        available = ["model1", "model2"]

        # Different error types should give same result
        result1 = strategy.select_next_fallback("failed", available, RuntimeError("rate limit"))
        result2 = strategy.select_next_fallback("failed", available, ValueError("context too large"))

        assert result1 == result2 == "model1"


class TestSmartFallback:
    """Tests for SmartFallback strategy."""

    @pytest.fixture
    def model_configs(self):
        """Create sample model configurations."""
        return {
            "openai/gpt-4o-mini": {
                "context_length": 128000,
                "provider": "openai",
            },
            "openai/gpt-4o": {
                "context_length": 128000,
                "provider": "openai",
            },
            "gemini/gemini-2.5-flash": {
                "context_length": 1000000,
                "provider": "gemini",
            },
            "anthropic/claude-3-5-sonnet-20241022": {
                "context_length": 200000,
                "provider": "anthropic",
            },
        }

    @pytest.fixture
    def strategy(self, model_configs):
        """Create strategy instance."""
        return SmartFallback(model_configs=model_configs)

    def test_context_error_selects_larger_context(self, strategy):
        """Test that context errors trigger larger context selection."""
        available = [
            "openai/gpt-4o-mini",  # 128k
            "anthropic/claude-3-5-sonnet-20241022",  # 200k
            "gemini/gemini-2.5-flash",  # 1M
        ]
        error = ValueError("Input exceeds context length")
        metadata = {"estimated_tokens": 150000}

        result = strategy.select_next_fallback("failed_model", available, error, metadata)

        # Should select claude (200k) as smallest sufficient
        assert result == "anthropic/claude-3-5-sonnet-20241022"

    def test_context_error_no_metadata(self, strategy):
        """Test context error without metadata."""
        available = ["model1", "model2"]
        error = ValueError("context too large")

        result = strategy.select_next_fallback("failed", available, error)

        # Without metadata, should still work (fallback to sequential)
        assert result in available

    def test_rate_limit_selects_different_provider(self, strategy):
        """Test that rate limit errors prefer different providers."""
        available = [
            "openai/gpt-4o",  # Same provider as failed
            "gemini/gemini-2.5-flash",  # Different provider
            "anthropic/claude-3-5-sonnet-20241022",  # Different provider
        ]
        error = RuntimeError("Rate limit exceeded - 429")

        result = strategy.select_next_fallback("openai/gpt-4o-mini", available, error)

        # Should select gemini (first different provider)
        assert result == "gemini/gemini-2.5-flash"

    def test_rate_limit_all_same_provider(self, strategy):
        """Test rate limit when all fallbacks are same provider."""
        available = ["openai/gpt-4o", "openai/gpt-3.5-turbo"]
        error = RuntimeError("429 too many requests")

        result = strategy.select_next_fallback("openai/gpt-4o-mini", available, error)

        # Should still return first (can't find different provider)
        assert result == "openai/gpt-4o"

    def test_unknown_error_uses_sequential(self, strategy):
        """Test that unknown errors fall back to sequential."""
        available = ["model1", "model2", "model3"]
        error = RuntimeError("Some unknown error")

        result = strategy.select_next_fallback("failed", available, error)

        # Should use sequential (first)
        assert result == "model1"

    def test_empty_fallback_list(self, strategy):
        """Test with empty fallback list."""
        result = strategy.select_next_fallback("failed", [], RuntimeError())

        assert result is None

    def test_context_keywords_detection(self, strategy):
        """Test various context error keywords."""
        available = ["anthropic/claude-3-5-sonnet-20241022", "gemini/gemini-2.5-flash"]
        metadata = {"estimated_tokens": 150000}

        context_errors = [
            "context length exceeded",
            "input too large",
            "maximum context reached",
            "token limit exceeded",
        ]

        for error_msg in context_errors:
            error = ValueError(error_msg)
            result = strategy.select_next_fallback("openai/gpt-4o-mini", available, error, metadata)
            # All should trigger context-aware selection
            assert result == "anthropic/claude-3-5-sonnet-20241022"

    def test_rate_limit_keywords_detection(self, strategy):
        """Test various rate limit error keywords."""
        available = ["gemini/gemini-2.5-flash", "openai/gpt-4o"]

        rate_limit_errors = [
            "rate limit exceeded",
            "429 too many requests",
            "quota exceeded",
            "resource_exhausted",
        ]

        for error_msg in rate_limit_errors:
            error = RuntimeError(error_msg)
            result = strategy.select_next_fallback("openai/gpt-4o-mini", available, error)
            # Should prefer gemini (different provider)
            assert result == "gemini/gemini-2.5-flash"


class TestCostOptimizedFallback:
    """Tests for CostOptimizedFallback strategy."""

    @pytest.fixture
    def model_costs(self):
        """Create sample model costs (per 1K tokens)."""
        return {
            "openai/gpt-4o": 5.0,
            "openai/gpt-4o-mini": 0.15,
            "gemini/gemini-2.5-flash": 0.075,
            "anthropic/claude-3-5-sonnet-20241022": 3.0,
        }

    @pytest.fixture
    def strategy(self, model_costs):
        """Create strategy instance."""
        return CostOptimizedFallback(model_costs=model_costs)

    def test_selects_cheapest_model(self, strategy):
        """Test that cheapest model is selected."""
        available = [
            "openai/gpt-4o",  # $5/1K
            "anthropic/claude-3-5-sonnet-20241022",  # $3/1K
            "openai/gpt-4o-mini",  # $0.15/1K
            "gemini/gemini-2.5-flash",  # $0.075/1K
        ]
        error = RuntimeError("Some error")

        result = strategy.select_next_fallback("failed_model", available, error)

        # Should select gemini (cheapest)
        assert result == "gemini/gemini-2.5-flash"

    def test_unknown_cost_treated_as_expensive(self, strategy):
        """Test that unknown costs are treated as expensive."""
        available = [
            "expensive/model",  # Unknown cost
            "openai/gpt-4o-mini",  # $0.15/1K
        ]

        result = strategy.select_next_fallback("failed", available, RuntimeError())

        # Should prefer known cost
        assert result == "openai/gpt-4o-mini"

    def test_all_unknown_costs(self, strategy):
        """Test with all unknown costs."""
        available = ["unknown1", "unknown2", "unknown3"]

        result = strategy.select_next_fallback("failed", available, RuntimeError())

        # Should return first (all have infinite cost)
        assert result == "unknown1"

    def test_empty_fallback_list(self, strategy):
        """Test with empty fallback list."""
        result = strategy.select_next_fallback("failed", [], RuntimeError())

        assert result is None

    def test_ignores_error_type(self, strategy):
        """Test that error type doesn't affect cost optimization."""
        available = ["openai/gpt-4o", "gemini/gemini-2.5-flash"]

        result1 = strategy.select_next_fallback("failed", available, RuntimeError("rate limit"))
        result2 = strategy.select_next_fallback("failed", available, ValueError("context error"))

        # Both should select cheapest
        assert result1 == result2 == "gemini/gemini-2.5-flash"


class TestCreateFallbackStrategy:
    """Tests for create_fallback_strategy factory function."""

    def test_create_sequential(self):
        """Test creating sequential strategy."""
        strategy = create_fallback_strategy("sequential")

        assert isinstance(strategy, SequentialFallback)

    def test_create_smart(self):
        """Test creating smart strategy."""
        configs = {"model1": {"context_length": 100000}}
        strategy = create_fallback_strategy("smart", model_configs=configs)

        assert isinstance(strategy, SmartFallback)
        assert strategy.model_configs == configs

    def test_create_cost(self):
        """Test creating cost-optimized strategy."""
        costs = {"model1": 1.0, "model2": 2.0}
        strategy = create_fallback_strategy("cost", model_costs=costs)

        assert isinstance(strategy, CostOptimizedFallback)
        assert strategy.model_costs == costs

    def test_unknown_strategy_type(self):
        """Test that unknown strategy type raises error."""
        with pytest.raises(ValueError, match="Unknown strategy type"):
            create_fallback_strategy("unknown_type")


class TestFallbackStrategyIntegration:
    """Integration tests for fallback strategies."""

    def test_realistic_smart_fallback_workflow(self):
        """Test realistic workflow with smart fallback."""
        # Setup
        model_configs = {
            "openai/gpt-4o-mini": {"context_length": 128000, "provider": "openai"},
            "gemini/gemini-2.5-flash": {"context_length": 1000000, "provider": "gemini"},
            "anthropic/claude-3-5-sonnet-20241022": {"context_length": 200000, "provider": "anthropic"},
        }
        strategy = SmartFallback(model_configs=model_configs)

        # Scenario 1: Context error
        available = list(model_configs.keys())
        error = ValueError("Input exceeds context length")
        metadata = {"estimated_tokens": 150000}

        result = strategy.select_next_fallback("openai/gpt-4o-mini", available, error, metadata)
        assert result == "anthropic/claude-3-5-sonnet-20241022"  # Smallest sufficient

        # Scenario 2: Rate limit error
        error = RuntimeError("429 rate limit exceeded")
        result = strategy.select_next_fallback("openai/gpt-4o-mini", available, error)
        assert result == "gemini/gemini-2.5-flash"  # Different provider

    def test_cost_optimization_workflow(self):
        """Test realistic cost optimization workflow."""
        model_costs = {
            "openai/gpt-4o": 5.0,
            "openai/gpt-4o-mini": 0.15,
            "gemini/gemini-2.5-flash": 0.075,
        }
        strategy = CostOptimizedFallback(model_costs=model_costs)

        available = list(model_costs.keys())

        # Always selects cheapest regardless of error
        result1 = strategy.select_next_fallback("failed", available, RuntimeError("rate limit"))
        result2 = strategy.select_next_fallback("failed", available, ValueError("context error"))

        assert result1 == result2 == "gemini/gemini-2.5-flash"
