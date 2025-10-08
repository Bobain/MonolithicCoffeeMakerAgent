"""Unit tests for ContextStrategy implementations."""

import pytest

from coffee_maker.langchain_observe.strategies.context import (
    LargeContextFallbackStrategy,
    NoContextCheckStrategy,
    create_context_strategy,
)


class TestLargeContextFallbackStrategy:
    """Tests for LargeContextFallbackStrategy."""

    @pytest.fixture
    def model_limits(self):
        """Create sample model context limits."""
        return {
            "openai/gpt-4o-mini": 128000,
            "openai/gpt-4o": 128000,
            "gemini/gemini-2.5-flash": 1000000,
            "anthropic/claude-3-5-sonnet-20241022": 200000,
            "anthropic/claude-3-5-haiku-20241022": 200000,
        }

    @pytest.fixture
    def strategy(self, model_limits):
        """Create strategy instance."""
        return LargeContextFallbackStrategy(model_context_limits=model_limits)

    def test_check_fits_small_input(self, strategy):
        """Test that small input fits within limits."""
        input_data = {"input": "Hello world" * 10}  # ~20-30 tokens
        model_name = "openai/gpt-4o-mini"

        fits, estimated_tokens, max_context = strategy.check_fits(input_data, model_name)

        assert fits is True
        assert estimated_tokens < 100  # Should be small
        assert max_context == 128000

    def test_check_fits_large_input(self, strategy):
        """Test that very large input exceeds limits."""
        # Create input that's definitely > 128k tokens
        large_text = "word " * 200000  # ~200k tokens
        input_data = {"input": large_text}
        model_name = "openai/gpt-4o-mini"

        fits, estimated_tokens, max_context = strategy.check_fits(input_data, model_name)

        assert fits is False
        assert estimated_tokens > 128000
        assert max_context == 128000

    def test_check_fits_unknown_model(self, strategy):
        """Test that unknown models have very large context (no limit)."""
        input_data = {"input": "test"}
        model_name = "unknown/model"

        fits, estimated_tokens, max_context = strategy.check_fits(input_data, model_name)

        assert fits is True  # Unknown model = no limit
        assert max_context == 10_000_000  # Very large default

    def test_get_larger_context_models(self, strategy):
        """Test finding models with larger context."""
        # Need 150k tokens
        required_tokens = 150000

        models = strategy.get_larger_context_models(required_tokens)

        # Should return models with >= 150k tokens
        assert "openai/gpt-4o-mini" not in models  # Only 128k
        assert "openai/gpt-4o" not in models  # Only 128k
        assert "anthropic/claude-3-5-sonnet-20241022" in models  # 200k
        assert "gemini/gemini-2.5-flash" in models  # 1M

        # Should be sorted by size (smallest first)
        assert models[0] == "anthropic/claude-3-5-sonnet-20241022"  # 200k first
        assert "gemini/gemini-2.5-flash" in models[-2:]  # 1M later

    def test_get_larger_context_models_no_suitable(self, strategy):
        """Test when no model has sufficient context."""
        # Need 2M tokens (more than any model)
        required_tokens = 2000000

        models = strategy.get_larger_context_models(required_tokens)

        assert models == []

    def test_estimate_tokens_dict_input(self, strategy):
        """Test token estimation with dict input."""
        input_data = {"input": "Hello world"}
        model_name = "openai/gpt-4o-mini"

        tokens = strategy.estimate_tokens(input_data, model_name)

        # Should be ~2-3 tokens for "Hello world"
        assert 1 <= tokens <= 10

    def test_estimate_tokens_string_input(self, strategy):
        """Test token estimation with string input."""
        input_data = "Hello world"
        model_name = "openai/gpt-4o-mini"

        tokens = strategy.estimate_tokens(input_data, model_name)

        assert 1 <= tokens <= 10

    def test_estimate_tokens_list_input(self, strategy):
        """Test token estimation with list input."""
        input_data = ["Hello", "world"]
        model_name = "openai/gpt-4o-mini"

        tokens = strategy.estimate_tokens(input_data, model_name)

        assert tokens > 0

    def test_tokenizer_caching(self, strategy):
        """Test that tokenizers are cached per model."""
        model_name = "openai/gpt-4o-mini"

        # First call
        tokens1 = strategy.estimate_tokens("Hello", model_name)

        # Tokenizer should be cached
        assert model_name in strategy._tokenizers

        # Second call should use cached tokenizer
        tokens2 = strategy.estimate_tokens("Hello", model_name)

        assert tokens1 == tokens2

    def test_non_openai_model_fallback(self, strategy):
        """Test that non-OpenAI models use character-based estimation."""
        input_data = {"input": "Hello world"}  # 11 characters
        model_name = "gemini/gemini-2.5-flash"

        tokens = strategy.estimate_tokens(input_data, model_name)

        # Should use character-based: 11 // 4 = 2
        assert tokens == 2  # "Hello world" = 11 chars / 4 = 2 tokens


class TestNoContextCheckStrategy:
    """Tests for NoContextCheckStrategy."""

    @pytest.fixture
    def strategy(self):
        """Create strategy instance."""
        return NoContextCheckStrategy()

    def test_check_fits_always_true(self, strategy):
        """Test that check_fits always returns True."""
        # Very large input
        large_input = {"input": "word " * 1000000}
        model_name = "openai/gpt-4o-mini"

        fits, estimated_tokens, max_context = strategy.check_fits(large_input, model_name)

        assert fits is True
        assert estimated_tokens == 0
        assert max_context == 10_000_000  # Very large default

    def test_get_larger_context_models_empty(self, strategy):
        """Test that get_larger_context_models returns empty list."""
        models = strategy.get_larger_context_models(1000000)

        assert models == []

    def test_estimate_tokens_zero(self, strategy):
        """Test that estimate_tokens returns 0."""
        tokens = strategy.estimate_tokens("any input", "any/model")

        assert tokens == 0


class TestCreateContextStrategy:
    """Tests for create_context_strategy factory function."""

    def test_create_with_check_disabled(self):
        """Test creating strategy with checks disabled."""
        strategy = create_context_strategy(enable_context_check=False)

        assert isinstance(strategy, NoContextCheckStrategy)

    def test_create_with_check_enabled(self):
        """Test creating strategy with checks enabled."""
        model_limits = {
            "openai/gpt-4o-mini": 128000,
            "gemini/gemini-2.5-flash": 1000000,
        }

        strategy = create_context_strategy(enable_context_check=True, model_limits=model_limits)

        assert isinstance(strategy, LargeContextFallbackStrategy)
        assert strategy.model_limits == model_limits

    def test_create_with_auto_load_limits(self):
        """Test that it can auto-load limits from llm_config."""
        # This should work because llm_config exists in the project
        strategy = create_context_strategy(enable_context_check=True)

        assert isinstance(strategy, LargeContextFallbackStrategy)
        # Should have loaded some models
        assert len(strategy.model_limits) > 0
        # Should include common models
        assert any("gpt" in model for model in strategy.model_limits.keys())


class TestContextStrategyIntegration:
    """Integration tests for context strategies."""

    def test_realistic_workflow(self):
        """Test a realistic workflow with context checking and fallback."""
        # Setup
        model_limits = {
            "openai/gpt-4o-mini": 128000,
            "anthropic/claude-3-5-sonnet-20241022": 200000,
        }
        strategy = LargeContextFallbackStrategy(model_context_limits=model_limits)

        # Scenario: Input too large for gpt-4o-mini
        large_input = {"input": "word " * 150000}  # ~150k tokens
        primary_model = "openai/gpt-4o-mini"

        # 1. Check if fits in primary
        fits, estimated_tokens, max_context = strategy.check_fits(large_input, primary_model)

        assert fits is False
        assert estimated_tokens > 128000

        # 2. Get alternative models
        alternatives = strategy.get_larger_context_models(estimated_tokens)

        assert len(alternatives) > 0
        assert "anthropic/claude-3-5-sonnet-20241022" in alternatives

        # 3. Verify fallback fits
        fallback_model = alternatives[0]
        fits_fallback, _, max_fallback = strategy.check_fits(large_input, fallback_model)

        assert fits_fallback is True
        assert max_fallback >= estimated_tokens
