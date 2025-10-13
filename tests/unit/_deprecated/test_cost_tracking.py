"""Unit tests for cost tracking integration."""

import unittest
from unittest.mock import MagicMock, Mock

# DEPRECATED: from coffee_maker.langfuse_observe.auto_picker_llm import AutoPickerLLM
from coffee_maker.observability.cost_calculator import CostCalculator
from coffee_maker.llm.rate_limiting.limiter import RateLimitConfig, RateLimitTracker


class TestCostTracking(unittest.TestCase):
    """Test cost tracking functionality in AutoPickerLLM."""

    def setUp(self):
        """Set up test fixtures."""
        # Create rate tracker
        self.rate_tracker = RateLimitTracker(
            {
                "openai/gpt-4o-mini": RateLimitConfig(requests_per_minute=100, tokens_per_minute=10000),
                "gemini/gemini-2.5-flash-lite": RateLimitConfig(requests_per_minute=100, tokens_per_minute=10000),
            }
        )

        # Create cost calculator with pricing
        self.pricing_info = {
            "openai/gpt-4o-mini": {"input_per_1m": 0.150, "output_per_1m": 0.600},
            "gemini/gemini-2.5-flash-lite": {"free": True},
        }
        self.cost_calculator = CostCalculator(self.pricing_info)

        # Mock Langfuse client
        self.langfuse_client = MagicMock()

        # Mock primary LLM
        self.primary_llm = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.content = "Test response"

    def test_cost_calculated_for_paid_model(self):
        """Test that cost is calculated correctly for paid models."""
        # Set up response with usage metadata
        self.mock_response.response_metadata = {"usage": {"prompt_tokens": 1000, "completion_tokens": 500}}
        self.primary_llm.invoke.return_value = self.mock_response

        # Create AutoPickerLLM with cost tracking
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            cost_calculator=self.cost_calculator,
            langfuse_client=self.langfuse_client,
        )

        # Invoke
        result = auto_llm.invoke({"input": "test"})

        # Verify cost was calculated
        self.assertIsNotNone(result)

        # Check cost was logged to Langfuse
        self.langfuse_client.generation.assert_called_once()
        call_args = self.langfuse_client.generation.call_args

        # Verify usage data
        self.assertEqual(call_args[1]["usage"]["input"], 1000)
        self.assertEqual(call_args[1]["usage"]["output"], 500)
        self.assertEqual(call_args[1]["usage"]["total"], 1500)

        # Verify cost metadata
        self.assertIn("cost_usd", call_args[1]["metadata"])
        self.assertIn("input_cost_usd", call_args[1]["metadata"])
        self.assertIn("output_cost_usd", call_args[1]["metadata"])

        # Verify cost calculation
        expected_input_cost = (1000 / 1_000_000) * 0.150
        expected_output_cost = (500 / 1_000_000) * 0.600
        expected_total = expected_input_cost + expected_output_cost

        self.assertAlmostEqual(call_args[1]["metadata"]["cost_usd"], expected_total, places=6)

    def test_cost_zero_for_free_model(self):
        """Test that free models report $0 cost."""
        # Mock fallback LLM
        fallback_llm = MagicMock()
        fallback_response = MagicMock()
        fallback_response.content = "Fallback response"
        fallback_response.response_metadata = {"usage": {"prompt_tokens": 1000, "completion_tokens": 500}}
        fallback_llm.invoke.return_value = fallback_response

        # Make primary fail
        self.primary_llm.invoke.side_effect = Exception("Primary failed")

        # Create AutoPickerLLM with cost tracking
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[(fallback_llm, "gemini/gemini-2.5-flash-lite")],
            rate_tracker=self.rate_tracker,
            cost_calculator=self.cost_calculator,
            langfuse_client=self.langfuse_client,
        )

        # Invoke (should use fallback)
        result = auto_llm.invoke({"input": "test"})

        # Verify fallback was used
        self.assertIsNotNone(result)

        # Check cost was logged to Langfuse
        self.langfuse_client.generation.assert_called_once()
        call_args = self.langfuse_client.generation.call_args

        # Verify free model has $0 cost
        self.assertEqual(call_args[1]["metadata"]["cost_usd"], 0.0)

    def test_cost_tracking_without_langfuse(self):
        """Test that cost tracking works even without Langfuse client."""
        # Set up response with usage metadata
        self.mock_response.response_metadata = {"usage": {"prompt_tokens": 1000, "completion_tokens": 500}}
        self.primary_llm.invoke.return_value = self.mock_response

        # Create AutoPickerLLM WITHOUT langfuse_client
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            cost_calculator=self.cost_calculator,
            langfuse_client=None,  # No Langfuse
        )

        # Invoke - should not raise error
        result = auto_llm.invoke({"input": "test"})
        self.assertIsNotNone(result)

        # Verify cost was still calculated (check cost calculator history)
        stats = self.cost_calculator.get_cost_stats(timeframe="all")
        self.assertEqual(stats["total_requests"], 1)
        self.assertGreater(stats["total_cost_usd"], 0)

    def test_token_extraction_from_usage_metadata(self):
        """Test token extraction from LangChain's usage_metadata format."""
        # Set up response with usage_metadata (LangChain format)
        # Create a proper mock object with integer attributes
        usage_metadata = Mock()
        usage_metadata.input_tokens = 800
        usage_metadata.output_tokens = 400

        mock_response = Mock()
        mock_response.content = "Test response"
        mock_response.usage_metadata = usage_metadata
        # Don't set response_metadata so it uses usage_metadata path
        mock_response.response_metadata = None

        self.primary_llm.invoke.return_value = mock_response

        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            cost_calculator=self.cost_calculator,
            langfuse_client=self.langfuse_client,
        )

        # Invoke
        auto_llm.invoke({"input": "test"})

        # Check correct tokens were logged
        call_args = self.langfuse_client.generation.call_args
        self.assertEqual(call_args[1]["usage"]["input"], 800)
        self.assertEqual(call_args[1]["usage"]["output"], 400)

    def test_fallback_cost_tracking(self):
        """Test that fallback model usage is tracked correctly."""
        # Make primary rate-limited
        self.rate_tracker.record_request("openai/gpt-4o-mini", 9999)  # Almost at limit

        # Mock fallback LLM
        fallback_llm = MagicMock()
        fallback_response = MagicMock()
        fallback_response.content = "Fallback response"
        fallback_response.response_metadata = {"usage": {"prompt_tokens": 500, "completion_tokens": 250}}
        fallback_llm.invoke.return_value = fallback_response

        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[(fallback_llm, "gemini/gemini-2.5-flash-lite")],
            rate_tracker=self.rate_tracker,
            cost_calculator=self.cost_calculator,
            langfuse_client=self.langfuse_client,
            auto_wait=False,  # Don't wait, use fallback immediately
        )

        # Invoke with large input to trigger rate limit
        auto_llm.invoke({"input": "x" * 10000})

        # Check that fallback model was logged
        call_args = self.langfuse_client.generation.call_args
        self.assertEqual(call_args[1]["model"], "gemini/gemini-2.5-flash-lite")
        self.assertEqual(call_args[1]["metadata"]["is_primary"], False)

    def test_cost_calculator_cumulative_tracking(self):
        """Test that CostCalculator tracks cumulative costs."""
        # Set up response
        self.mock_response.response_metadata = {"usage": {"prompt_tokens": 1000, "completion_tokens": 500}}
        self.primary_llm.invoke.return_value = self.mock_response

        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            cost_calculator=self.cost_calculator,
            langfuse_client=self.langfuse_client,
        )

        # Make multiple requests
        auto_llm.invoke({"input": "test1"})
        auto_llm.invoke({"input": "test2"})
        auto_llm.invoke({"input": "test3"})

        # Check cumulative cost
        stats = self.cost_calculator.get_cost_stats(timeframe="all")
        self.assertEqual(stats["total_requests"], 3)

        # Each request: (1000 * 0.150 + 500 * 0.600) / 1M = 0.00045
        expected_total = 3 * 0.00045
        self.assertAlmostEqual(stats["total_cost_usd"], expected_total, places=6)

    def test_langfuse_error_doesnt_break_flow(self):
        """Test that Langfuse errors don't break LLM invocation."""
        # Set up response
        self.mock_response.response_metadata = {"usage": {"prompt_tokens": 1000, "completion_tokens": 500}}
        self.primary_llm.invoke.return_value = self.mock_response

        # Make Langfuse client raise error
        self.langfuse_client.generation.side_effect = Exception("Langfuse error")

        # Create AutoPickerLLM
        auto_llm = AutoPickerLLM(
            primary_llm=self.primary_llm,
            primary_model_name="openai/gpt-4o-mini",
            fallback_llms=[],
            rate_tracker=self.rate_tracker,
            cost_calculator=self.cost_calculator,
            langfuse_client=self.langfuse_client,
        )

        # Invoke - should not raise error
        result = auto_llm.invoke({"input": "test"})
        self.assertIsNotNone(result)

        # Cost should still be calculated
        stats = self.cost_calculator.get_cost_stats(timeframe="all")
        self.assertEqual(stats["total_requests"], 1)


if __name__ == "__main__":
    unittest.main()
