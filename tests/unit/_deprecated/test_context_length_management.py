"""Unit tests for context length management in AutoPickerLLM."""

import unittest
from unittest.mock import MagicMock

from coffee_maker.langfuse_observe.auto_picker_llm import AutoPickerLLM
from coffee_maker.langfuse_observe.llm_config import (
    get_large_context_models,
    get_model_context_length_from_name,
)
from coffee_maker.langfuse_observe.rate_limiter import RateLimitConfig, RateLimitTracker


class TestContextLengthHelpers(unittest.TestCase):
    """Test helper functions for context length management."""

    def test_get_large_context_models(self):
        """Test that large context models are returned sorted by context length."""
        models = get_large_context_models()

        # Should return list of tuples
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

        # Each item should be (provider, model_name, context_length)
        for item in models:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 3)
            provider, model_name, context_length = item
            self.assertIsInstance(provider, str)
            self.assertIsInstance(model_name, str)
            self.assertIsInstance(context_length, int)
            self.assertGreater(context_length, 0)

        # Should be sorted by context length descending
        context_lengths = [item[2] for item in models]
        self.assertEqual(context_lengths, sorted(context_lengths, reverse=True))

    def test_get_model_context_length_from_name(self):
        """Test getting context length from model name."""
        # Test valid models
        gpt4o_context = get_model_context_length_from_name("openai/gpt-4o")
        self.assertEqual(gpt4o_context, 128000)

        gpt4o_mini_context = get_model_context_length_from_name("openai/gpt-4o-mini")
        self.assertEqual(gpt4o_mini_context, 128000)

        # Test invalid format
        with self.assertRaises(ValueError) as ctx:
            get_model_context_length_from_name("invalid-format")
        self.assertIn("Invalid model name format", str(ctx.exception))

        # Test unknown provider
        with self.assertRaises(ValueError) as ctx:
            get_model_context_length_from_name("unknown/model")
        self.assertIn("Unknown provider", str(ctx.exception))

        # Test unknown model
        with self.assertRaises(ValueError) as ctx:
            get_model_context_length_from_name("openai/unknown-model")
        self.assertIn("Unknown model", str(ctx.exception))


class TestContextLengthManagement(unittest.TestCase):
    """Test context length management in AutoPickerLLM."""

    def setUp(self):
        """Set up test fixtures."""
        # Create rate tracker with models of different context lengths
        self.rate_tracker = RateLimitTracker(
            {
                "openai/gpt-4o-mini": RateLimitConfig(requests_per_minute=100, tokens_per_minute=1000000),
                "openai/gpt-4o": RateLimitConfig(requests_per_minute=100, tokens_per_minute=1000000),
                "gemini/gemini-2.5-pro": RateLimitConfig(requests_per_minute=100, tokens_per_minute=5000000),
            }
        )

        # Mock primary LLM (gpt-4o-mini with 128K context)
        self.primary_llm = MagicMock()
        self.primary_response = MagicMock()
        self.primary_response.content = "Primary response"
        self.primary_response.response_metadata = {"usage": {"prompt_tokens": 100, "completion_tokens": 50}}

    def test_normal_input_uses_primary_model(self):
        """Test that normal-sized input uses the primary model."""
        self.primary_llm.invoke.return_value = self.primary_response

        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            enable_context_fallback=True,
        )

        # Normal input (small)
        result = auto_llm.invoke({"input": "x" * 100})  # ~25 tokens

        # Should use primary model
        self.assertIsNotNone(result)
        self.primary_llm.invoke.assert_called_once()

    def test_large_input_triggers_context_fallback(self):
        """Test that large input triggers fallback to larger-context model."""
        # Mock large-context model (gemini-2.5-pro with 2M context)
        large_llm = MagicMock()
        large_response = MagicMock()
        large_response.content = "Large context response"
        large_response.response_metadata = {"usage": {"prompt_tokens": 200000, "completion_tokens": 100}}
        large_llm.invoke.return_value = large_response

        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            enable_context_fallback=True,
        )

        # Mock large context models initialization
        auto_llm._large_context_models = [
            (large_llm, "gemini/gemini-2.5-pro", 2097152),
            (MagicMock(), "openai/gpt-4o", 128000),
        ]

        # Large input that exceeds gpt-4o-mini's 128K limit
        # ~150K tokens (600K chars / 4)
        large_input = "x" * 600000

        result = auto_llm.invoke({"input": large_input})

        # Should use large-context model
        self.assertIsNotNone(result)
        large_llm.invoke.assert_called_once()
        # Primary should not be called (context too large)
        self.primary_llm.invoke.assert_not_called()

    def test_context_fallback_logs_to_langfuse(self):
        """Test that context fallback is logged to Langfuse."""
        # Mock Langfuse client
        langfuse_client = MagicMock()

        # Mock large-context model
        large_llm = MagicMock()
        large_response = MagicMock()
        large_response.content = "Large context response"
        large_response.response_metadata = {"usage": {"prompt_tokens": 200000, "completion_tokens": 100}}
        large_llm.invoke.return_value = large_response

        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            enable_context_fallback=True,
            langfuse_client=langfuse_client,
        )

        # Mock large context models
        auto_llm._large_context_models = [
            (large_llm, "gemini/gemini-2.5-pro", 2097152),
        ]

        # Large input
        large_input = "x" * 600000
        auto_llm.invoke({"input": large_input})

        # Verify Langfuse event was logged
        langfuse_client.event.assert_called_once()
        call_args = langfuse_client.event.call_args

        # Check event name
        self.assertEqual(call_args[1]["name"], "context_length_fallback")

        # Check metadata
        metadata = call_args[1]["metadata"]
        self.assertEqual(metadata["original_model"], "openai/gpt-4o-mini")
        self.assertEqual(metadata["fallback_model"], "gemini/gemini-2.5-pro")
        self.assertIn("estimated_tokens", metadata)
        self.assertIn("original_max_context", metadata)
        self.assertIn("fallback_max_context", metadata)

    def test_impossibly_large_input_raises_error(self):
        """Test that input larger than any model raises clear error."""
        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            enable_context_fallback=True,
        )

        # Mock large context models (even the largest can't handle this)
        auto_llm._large_context_models = [
            (MagicMock(), "gemini/gemini-2.5-pro", 2097152),
        ]

        # Impossibly large input (>2M tokens, ~8M chars)
        huge_input = "x" * 10000000

        # Should raise ValueError with clear message
        with self.assertRaises(ValueError) as ctx:
            auto_llm.invoke({"input": huge_input})

        error_msg = str(ctx.exception)
        self.assertIn("Input is too large", error_msg)
        self.assertIn("for any available model", error_msg)
        self.assertIn("Maximum supported context", error_msg)
        self.assertIn("Please reduce input size", error_msg)

    def test_context_fallback_disabled(self):
        """Test that context fallback can be disabled."""
        # Create AutoPickerLLM with context fallback disabled
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            enable_context_fallback=False,  # Disabled
        )

        # Large input
        large_input = "x" * 600000

        # Mock primary to succeed (even though input is too large)
        self.primary_llm.invoke.return_value = self.primary_response

        # Should attempt to use primary model (no context check)
        result = auto_llm.invoke({"input": large_input})

        # Should try primary (context checking is disabled)
        self.primary_llm.invoke.assert_called_once()

    def test_check_context_length_method(self):
        """Test the _check_context_length method directly."""
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
        )

        # Small input should fit
        fits, tokens, max_context = auto_llm._check_context_length({"input": "x" * 100}, "openai/gpt-4o-mini")
        self.assertTrue(fits)
        self.assertLess(tokens, max_context)
        self.assertEqual(max_context, 128000)

        # Large input should not fit
        fits, tokens, max_context = auto_llm._check_context_length({"input": "x" * 600000}, "openai/gpt-4o-mini")
        self.assertFalse(fits)
        self.assertGreater(tokens, max_context)
        self.assertEqual(max_context, 128000)

    def test_get_large_context_models_filtered_by_tier(self):
        """Test that large context models are filtered by current tier."""
        # Rate tracker with only small models
        limited_tracker = RateLimitTracker(
            {
                "openai/gpt-4o-mini": RateLimitConfig(requests_per_minute=100, tokens_per_minute=1000000),
            }
        )

        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=limited_tracker,
        )

        # Initialize large context models
        auto_llm._initialize_large_context_models()

        # Should only include models available in the tier
        available_models = [name for _, name, _ in auto_llm._large_context_models]

        # gemini-2.5-pro should not be available (not in tracker)
        self.assertNotIn("gemini/gemini-2.5-pro", available_models)

        # gpt-4o-mini should be available
        self.assertIn("openai/gpt-4o-mini", available_models)

    def test_multiple_fallback_attempts(self):
        """Test that multiple fallback models are tried if first fails."""
        # Mock large-context models
        large_llm1 = MagicMock()
        large_llm1.invoke.side_effect = Exception("Model 1 failed")

        large_llm2 = MagicMock()
        large_response2 = MagicMock()
        large_response2.content = "Model 2 success"
        large_response2.response_metadata = {"usage": {"prompt_tokens": 200000, "completion_tokens": 100}}
        large_llm2.invoke.return_value = large_response2

        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            enable_context_fallback=True,
        )

        # Mock large context models (ordered by preference)
        # Both have sufficient context for the input
        auto_llm._large_context_models = [
            (large_llm1, "gemini/gemini-2.5-pro", 2097152),  # Will fail
            (
                large_llm2,
                "openai/gpt-4.1",
                1000000,
            ),  # Will succeed (has enough context)
        ]

        # Large input (150K tokens)
        large_input = "x" * 600000
        result = auto_llm.invoke({"input": large_input})

        # Should succeed with second model
        self.assertIsNotNone(result)
        large_llm1.invoke.assert_called_once()  # First attempt
        large_llm2.invoke.assert_called_once()  # Second attempt (success)


if __name__ == "__main__":
    unittest.main()
