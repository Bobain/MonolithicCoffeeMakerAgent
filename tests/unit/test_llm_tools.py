"""Unit tests for LLM tools."""

import pytest

from coffee_maker.langchain_observe.llm_config import get_rate_limits_for_tier
from coffee_maker.langchain_observe.llm_tools import (
    MODEL_PURPOSES,
    create_llm_tool_wrapper,
    create_llm_tools,
    get_llm_tool_names,
    get_llm_tools_summary,
)
from coffee_maker.langchain_observe.rate_limiter import RateLimitTracker


class TestLLMTools:
    """Tests for LLM tools functionality."""

    @pytest.fixture
    def rate_tracker(self):
        """Create a rate tracker for testing."""
        rate_limits = get_rate_limits_for_tier("tier1")
        return RateLimitTracker(rate_limits)

    def test_model_purposes_structure(self):
        """Test that MODEL_PURPOSES has expected structure."""
        assert "long_context" in MODEL_PURPOSES
        assert "fast" in MODEL_PURPOSES
        assert "accurate" in MODEL_PURPOSES
        assert "budget" in MODEL_PURPOSES
        assert "second_best_model" in MODEL_PURPOSES

        # Each purpose should have openai and gemini
        for purpose in MODEL_PURPOSES.values():
            assert "openai" in purpose
            assert "gemini" in purpose

            # Each provider config should have 4 elements: (provider, primary, fallback, description)
            for provider_config in purpose.values():
                assert len(provider_config) == 4
                provider, primary, fallback, desc = provider_config
                assert isinstance(provider, str)
                assert isinstance(primary, str)
                assert isinstance(fallback, str)
                assert isinstance(desc, str)

    def test_create_llm_tool_wrapper_valid(self, rate_tracker):
        """Test creating LLM tool wrapper with valid inputs."""
        llm = create_llm_tool_wrapper(
            purpose="fast",
            provider="openai",
            rate_tracker=rate_tracker,
            tier="tier1",
        )

        assert llm is not None
        assert hasattr(llm, "invoke")
        assert llm.primary_model_name == "openai/gpt-4o-mini"

    def test_create_llm_tool_wrapper_invalid_purpose(self, rate_tracker):
        """Test creating LLM tool wrapper with invalid purpose."""
        with pytest.raises(ValueError) as exc_info:
            create_llm_tool_wrapper(
                purpose="invalid_purpose",
                provider="openai",
                rate_tracker=rate_tracker,
            )

        assert "Invalid purpose" in str(exc_info.value)

    def test_create_llm_tool_wrapper_invalid_provider(self, rate_tracker):
        """Test creating LLM tool wrapper with invalid provider."""
        with pytest.raises(ValueError) as exc_info:
            create_llm_tool_wrapper(
                purpose="fast",
                provider="invalid_provider",
                rate_tracker=rate_tracker,
            )

        assert "Invalid provider" in str(exc_info.value)

    def test_create_llm_tool_wrapper_long_context(self, rate_tracker):
        """Test creating long context LLM tool."""
        llm = create_llm_tool_wrapper(
            purpose="long_context",
            provider="openai",
            rate_tracker=rate_tracker,
        )

        assert llm.primary_model_name == "openai/gpt-4o"
        assert len(llm.fallback_llms) == 1
        assert llm.fallback_llms[0][1] == "openai/gpt-4o-mini"

    def test_create_llm_tool_wrapper_accurate(self, rate_tracker):
        """Test creating accurate LLM tool."""
        llm = create_llm_tool_wrapper(
            purpose="accurate",
            provider="gemini",
            rate_tracker=rate_tracker,
        )

        assert llm.primary_model_name == "gemini/gemini-2.0-pro"
        assert llm.fallback_llms[0][1] == "gemini/gemini-2.5-flash"

    def test_create_llm_tools(self):
        """Test creating all LLM tools."""
        tools = create_llm_tools(tier="tier1")

        # Should create tools for all purposes and providers
        expected_count = len(MODEL_PURPOSES) * 2  # 2 providers per purpose
        assert len(tools) == expected_count

        # Check that all tools have required attributes
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "func")
            assert hasattr(tool, "description")
            assert tool.name.startswith("invoke_llm_")

    def test_get_llm_tool_names(self):
        """Test getting LLM tool names."""
        names = get_llm_tool_names()

        assert len(names) > 0
        assert "invoke_llm_openai_fast" in names
        assert "invoke_llm_gemini_long_context" in names
        assert "invoke_llm_openai_accurate" in names

        # All names should follow the pattern
        for name in names:
            assert name.startswith("invoke_llm_")
            parts = name.split("_")
            assert len(parts) >= 4  # invoke, llm, provider, purpose...

    def test_get_llm_tools_summary(self):
        """Test getting LLM tools summary."""
        summary = get_llm_tools_summary()

        # Should have all purposes
        assert "long_context" in summary
        assert "fast" in summary
        assert "accurate" in summary

        # Each purpose should have providers
        for purpose_config in summary.values():
            assert "openai" in purpose_config
            assert "gemini" in purpose_config

            # Each provider should have required fields
            for provider_config in purpose_config.values():
                assert "primary_model" in provider_config
                assert "fallback_model" in provider_config
                assert "description" in provider_config
                assert "tool_name" in provider_config

    def test_tool_names_consistency(self):
        """Test that tool names are consistent between functions."""
        tools = create_llm_tools()
        tool_names_from_tools = [t.name for t in tools]
        tool_names_from_func = get_llm_tool_names()

        assert set(tool_names_from_tools) == set(tool_names_from_func)

    def test_llm_tool_purposes_coverage(self):
        """Test that we have tools for common use cases."""
        summary = get_llm_tools_summary()

        # Verify we have tools for different needs
        purposes = list(summary.keys())
        assert "long_context" in purposes  # For large files
        assert "fast" in purposes  # For quick tasks
        assert "accurate" in purposes  # For complex analysis
        assert "budget" in purposes  # For cost optimization
        assert "second_best_model" in purposes  # For balanced use

    def test_tool_description_format(self):
        """Test that tool descriptions are properly formatted."""
        tools = create_llm_tools()

        for tool in tools:
            # Description should mention the purpose
            assert "Invoke" in tool.description
            assert "LLM" in tool.description

            # Should include input format information
            assert "Input format" in tool.description or "task_description" in tool.description

            # Should include use case guidance
            assert "Use this tool when" in tool.description or "For tasks" in tool.description
