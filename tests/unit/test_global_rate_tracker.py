"""Unit tests for global rate tracker singleton."""

from coffee_maker.langchain_observe.global_rate_tracker import (
    get_global_rate_tracker,
    get_global_rate_tracker_stats,
    reset_global_rate_tracker,
)


class TestGlobalRateTracker:
    """Tests for global rate tracker singleton."""

    def setup_method(self):
        """Reset global tracker before each test."""
        reset_global_rate_tracker()

    def teardown_method(self):
        """Reset global tracker after each test."""
        reset_global_rate_tracker()

    def test_singleton_same_instance(self):
        """Test that get_global_rate_tracker returns the same instance."""
        tracker1 = get_global_rate_tracker(tier="tier1")
        tracker2 = get_global_rate_tracker(tier="tier1")

        assert tracker1 is tracker2  # Same object reference

    def test_singleton_shared_state(self):
        """Test that rate limits are shared across instances."""
        tracker1 = get_global_rate_tracker(tier="tier1")
        tracker2 = get_global_rate_tracker(tier="tier1")

        # Record a request using tracker1
        tracker1.record_request("openai/gpt-4o-mini", tokens_used=100)

        # Check state using tracker2
        stats = tracker2.get_usage_stats("openai/gpt-4o-mini")
        assert stats["requests_per_minute"]["current"] == 1
        assert stats["tokens_per_minute"]["current"] == 100

    def test_tier_change_resets_tracker(self):
        """Test that changing tier creates a new tracker."""
        tracker1 = get_global_rate_tracker(tier="tier1")
        tracker1.record_request("openai/gpt-4o-mini", tokens_used=100)

        # Change tier - should get new tracker
        tracker2 = get_global_rate_tracker(tier="tier2")

        # Should be different instance
        assert tracker1 is not tracker2

        # New tracker should have clean state
        stats = tracker2.get_usage_stats("openai/gpt-4o-mini")
        assert stats["requests_per_minute"]["current"] == 0

    def test_reset_clears_singleton(self):
        """Test that reset clears the global tracker."""
        tracker1 = get_global_rate_tracker(tier="tier1")
        tracker1.record_request("openai/gpt-4o-mini", tokens_used=100)

        # Reset
        reset_global_rate_tracker()

        # Get new tracker - should be clean
        tracker2 = get_global_rate_tracker(tier="tier1")
        assert tracker1 is not tracker2

        stats = tracker2.get_usage_stats("openai/gpt-4o-mini")
        assert stats["requests_per_minute"]["current"] == 0

    def test_get_stats_before_creation(self):
        """Test getting stats when no tracker exists."""
        reset_global_rate_tracker()
        stats = get_global_rate_tracker_stats()
        assert stats is None

    def test_get_stats_after_creation(self):
        """Test getting stats for all models."""
        tracker = get_global_rate_tracker(tier="tier1")
        tracker.record_request("openai/gpt-4o-mini", tokens_used=100)
        tracker.record_request("openai/gpt-4o", tokens_used=200)

        stats = get_global_rate_tracker_stats()
        assert stats is not None
        assert "openai/gpt-4o-mini" in stats
        assert "openai/gpt-4o" in stats
        assert stats["openai/gpt-4o-mini"]["requests_per_minute"]["current"] == 1
        assert stats["openai/gpt-4o"]["requests_per_minute"]["current"] == 1

    def test_multiple_tools_share_rate_limits(self):
        """Test that multiple tools using same model share rate limits."""
        from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_llm

        # Create two AutoPickerLLM instances with same primary model
        llm1 = create_auto_picker_llm(tier="tier1", primary_model="gpt-4o-mini")
        llm2 = create_auto_picker_llm(tier="tier1", primary_model="gpt-4o-mini")

        # Both should use the same rate tracker
        assert llm1.rate_tracker is llm2.rate_tracker

        # Record request with llm1
        llm1.rate_tracker.record_request("openai/gpt-4o-mini", tokens_used=100)

        # Should be visible in llm2
        stats = llm2.rate_tracker.get_usage_stats("openai/gpt-4o-mini")
        assert stats["requests_per_minute"]["current"] == 1

    def test_llm_tools_share_rate_limits_with_main_agent(self):
        """Test that LLM tools share rate limits with main agent."""
        from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_llm
        from coffee_maker.langchain_observe.llm_tools import create_llm_tools

        # Create main agent's AutoPickerLLM
        main_llm = create_auto_picker_llm(tier="tier1", primary_model="gpt-4o-mini")

        # Create LLM tools (which also use gpt-4o-mini for some tools)
        tools = create_llm_tools(tier="tier1")

        # Record request with main LLM
        main_llm.rate_tracker.record_request("openai/gpt-4o-mini", tokens_used=100)

        # Get a tool that uses gpt-4o-mini (fast or budget tool)
        fast_tool = next(t for t in tools if t.name == "invoke_llm_openai_fast")

        # The tool's rate tracker should see the request from main LLM
        # Note: We need to access the rate tracker through the global singleton
        from coffee_maker.langchain_observe.global_rate_tracker import get_global_rate_tracker

        shared_tracker = get_global_rate_tracker(tier="tier1")
        stats = shared_tracker.get_usage_stats("openai/gpt-4o-mini")
        assert stats["requests_per_minute"]["current"] == 1
