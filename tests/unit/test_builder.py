"""Unit tests for LLMBuilder and SmartLLM."""

from unittest import mock

import pytest

from coffee_maker.langfuse_observe.builder import LLMBuilder, SmartLLM


class MockScheduledLLM:
    """Mock ScheduledLLM for testing."""

    def __init__(self, model_name: str):
        self.model_name = model_name


class TestLLMBuilder:
    """Tests for LLMBuilder."""

    def test_builder_basic_configuration(self):
        """Test basic builder configuration."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            mock_create.return_value = "mocked_llm"

            llm = (
                LLMBuilder()
                .with_tier("tier1")
                .with_primary("openai", "gpt-4o-mini")
                .with_fallback("gemini", "gemini-2.5-flash")
                .build()
            )

            # Verify create was called with correct args
            mock_create.assert_called_once()
            args = mock_create.call_args
            assert args.kwargs["primary_provider"] == "openai"
            assert args.kwargs["primary_model"] == "gpt-4o-mini"
            assert args.kwargs["fallback_configs"] == [("gemini", "gemini-2.5-flash")]
            assert args.kwargs["tier"] == "tier1"

    def test_builder_missing_primary_raises_error(self):
        """Test that building without primary raises error."""
        with pytest.raises(ValueError, match="Primary model not set"):
            LLMBuilder().build()

    def test_builder_with_multiple_fallbacks(self):
        """Test builder with multiple fallbacks."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            mock_create.return_value = "mocked_llm"

            llm = (
                LLMBuilder()
                .with_primary("openai", "gpt-4o-mini")
                .with_fallback("gemini", "gemini-2.5-flash")
                .with_fallback("anthropic", "claude-3-5-haiku-20241022")
                .build()
            )

            args = mock_create.call_args
            assert len(args.kwargs["fallback_configs"]) == 2

    def test_builder_with_fallbacks_method(self):
        """Test builder with_fallbacks method (multiple at once)."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            mock_create.return_value = "mocked_llm"

            fallbacks = [
                ("gemini", "gemini-2.5-flash"),
                ("anthropic", "claude-3-5-haiku-20241022"),
            ]

            LLMBuilder().with_primary("openai", "gpt-4o-mini").with_fallbacks(fallbacks).build()

            args = mock_create.call_args
            assert args.kwargs["fallback_configs"] == fallbacks

    def test_builder_with_cost_tracking(self):
        """Test builder with cost tracking enabled."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            mock_create.return_value = "mocked_llm"

            mock_cost_calc = mock.Mock()
            mock_langfuse = mock.Mock()

            llm = (
                LLMBuilder()
                .with_primary("openai", "gpt-4o-mini")
                .with_cost_tracking(cost_calculator=mock_cost_calc, langfuse_client=mock_langfuse)
                .build()
            )

            args = mock_create.call_args
            assert args.kwargs["cost_calculator"] is mock_cost_calc
            assert args.kwargs["langfuse_client"] is mock_langfuse

    def test_builder_with_max_wait(self):
        """Test builder with custom max wait time."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            mock_create.return_value = "mocked_llm"

            LLMBuilder().with_primary("openai", "gpt-4o-mini").with_max_wait(600.0).build()

            args = mock_create.call_args
            assert args.kwargs["max_wait_seconds"] == 600.0

    def test_builder_with_context_fallback_disabled(self):
        """Test builder with context fallback disabled."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            mock_create.return_value = "mocked_llm"

            LLMBuilder().with_primary("openai", "gpt-4o-mini").with_context_fallback(False).build()

            args = mock_create.call_args
            assert args.kwargs["enable_context_fallback"] is False

    def test_builder_with_smart_fallback(self):
        """Test builder with smart fallback strategy."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.builder.create_fallback_strategy") as mock_strategy:
                mock_create.return_value = "mocked_llm"
                mock_strategy.return_value = "smart_strategy"

                LLMBuilder().with_primary("openai", "gpt-4o-mini").with_smart_fallback().build()

                # Should create smart strategy
                mock_strategy.assert_called_once()
                assert mock_strategy.call_args.args[0] == "smart"

    def test_builder_with_cost_optimized_fallback(self):
        """Test builder with cost-optimized fallback strategy."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.builder.create_fallback_strategy") as mock_strategy:
                mock_create.return_value = "mocked_llm"
                mock_strategy.return_value = "cost_strategy"

                LLMBuilder().with_primary("openai", "gpt-4o-mini").with_cost_optimized_fallback().build()

                # Should create cost strategy
                mock_strategy.assert_called_once()
                assert mock_strategy.call_args.args[0] == "cost"

    def test_builder_with_sequential_fallback(self):
        """Test builder with sequential fallback strategy (default)."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.builder.create_fallback_strategy") as mock_strategy:
                mock_create.return_value = "mocked_llm"
                mock_strategy.return_value = "sequential_strategy"

                LLMBuilder().with_primary("openai", "gpt-4o-mini").with_sequential_fallback().build()

                # Should create sequential strategy
                mock_strategy.assert_called_once()
                assert mock_strategy.call_args.args[0] == "sequential"

    def test_builder_with_custom_fallback_strategy(self):
        """Test builder with custom fallback strategy."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            mock_create.return_value = "mocked_llm"

            custom_strategy = mock.Mock()

            llm = (
                LLMBuilder()
                .with_primary("openai", "gpt-4o-mini")
                .with_custom_fallback_strategy(custom_strategy)
                .build()
            )

            args = mock_create.call_args
            assert args.kwargs["fallback_strategy"] is custom_strategy

    def test_builder_fluent_api(self):
        """Test that builder methods return self for chaining."""
        builder = LLMBuilder()

        # All methods should return self
        assert builder.with_tier("tier1") is builder
        assert builder.with_primary("openai", "gpt-4o-mini") is builder
        assert builder.with_fallback("gemini", "gemini-2.5-flash") is builder
        assert builder.with_max_wait(600.0) is builder
        assert builder.with_context_fallback(True) is builder
        assert builder.with_smart_fallback() is builder


class TestSmartLLM:
    """Tests for SmartLLM facade."""

    def test_for_tier_with_defaults(self):
        """Test SmartLLM.for_tier with defaults."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.cost_calculator.CostCalculator"):
                mock_create.return_value = "mocked_llm"

                SmartLLM.for_tier("tier1")

                # Should have called create
                mock_create.assert_called_once()

    def test_for_tier_with_custom_primary(self):
        """Test SmartLLM.for_tier with custom primary."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.cost_calculator.CostCalculator"):
                mock_create.return_value = "mocked_llm"

                llm = SmartLLM.for_tier("tier1", primary=("openai", "gpt-4o"))

                # Should use custom primary
                args = mock_create.call_args
                assert args.kwargs["primary_provider"] == "openai"
                assert args.kwargs["primary_model"] == "gpt-4o"

    def test_for_tier_with_custom_fallbacks(self):
        """Test SmartLLM.for_tier with custom fallbacks."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.cost_calculator.CostCalculator"):
                mock_create.return_value = "mocked_llm"

                custom_fallbacks = [("gemini", "gemini-2.5-pro")]
                llm = SmartLLM.for_tier("tier1", fallbacks=custom_fallbacks)

                # Should use custom fallbacks
                args = mock_create.call_args
                assert args.kwargs["fallback_configs"] == custom_fallbacks

    def test_for_tier_smart_defaults(self):
        """Test that SmartLLM.for_tier uses smart defaults."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.cost_calculator.CostCalculator"):
                mock_create.return_value = "mocked_llm"

                SmartLLM.for_tier("tier1")

                args = mock_create.call_args
                # Default primary
                assert args.kwargs["primary_provider"] == "openai"
                assert args.kwargs["primary_model"] == "gpt-4o-mini"

                # Default fallbacks
                assert ("gemini", "gemini-2.5-flash") in args.kwargs["fallback_configs"]
                assert ("anthropic", "claude-3-5-haiku-20241022") in args.kwargs["fallback_configs"]

    def test_fast_preset(self):
        """Test SmartLLM.fast() preset."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.cost_calculator.CostCalculator"):
                mock_create.return_value = "mocked_llm"

                SmartLLM.fast("tier1")

                args = mock_create.call_args
                # Should use fast/cheap models
                assert args.kwargs["primary_model"] == "gpt-4o-mini"
                assert ("gemini", "gemini-2.5-flash") in args.kwargs["fallback_configs"]

    def test_powerful_preset(self):
        """Test SmartLLM.powerful() preset."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.cost_calculator.CostCalculator"):
                mock_create.return_value = "mocked_llm"

                SmartLLM.powerful("tier1")

                args = mock_create.call_args
                # Should use powerful models
                assert args.kwargs["primary_model"] == "gpt-4o"
                # Should have quality fallbacks
                assert any(
                    "claude" in str(config) or "sonnet" in str(config) for config in args.kwargs["fallback_configs"]
                )


class TestBuilderIntegration:
    """Integration tests for builder."""

    def test_complete_workflow(self):
        """Test complete builder workflow."""
        with mock.patch(
            "coffee_maker.langfuse_observe.auto_picker_llm_refactored.create_auto_picker_llm_refactored"
        ) as mock_create:
            with mock.patch("coffee_maker.langfuse_observe.cost_calculator.CostCalculator"):
                mock_create.return_value = "mocked_llm"

                # Build complex LLM config
                llm = (
                    LLMBuilder()
                    .with_tier("tier2")
                    .with_primary("openai", "gpt-4o")
                    .with_fallback("anthropic", "claude-3-5-sonnet-20241022")
                    .with_fallback("gemini", "gemini-2.5-pro")
                    .with_cost_tracking()
                    .with_smart_fallback()
                    .with_context_fallback(True)
                    .with_max_wait(600.0)
                    .build()
                )

                # Verify all configuration
                args = mock_create.call_args
                assert args.kwargs["tier"] == "tier2"
                assert args.kwargs["primary_provider"] == "openai"
                assert args.kwargs["primary_model"] == "gpt-4o"
                assert len(args.kwargs["fallback_configs"]) == 2
                assert args.kwargs["max_wait_seconds"] == 600.0
                assert args.kwargs["enable_context_fallback"] is True
                assert args.kwargs["fallback_strategy"] is not None
