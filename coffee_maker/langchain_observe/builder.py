"""Builder pattern for constructing LLM instances with fluent API.

This module provides a convenient builder interface for creating LLM instances
with all the bells and whistles (scheduling, fallbacks, cost tracking, etc.).
"""

import logging
from typing import List, Optional, Tuple

from coffee_maker.langchain_observe.auto_picker_llm_refactored import AutoPickerLLMRefactored
from coffee_maker.langchain_observe.strategies.context import ContextStrategy
from coffee_maker.langchain_observe.strategies.fallback import FallbackStrategy, create_fallback_strategy

logger = logging.getLogger(__name__)


class LLMBuilder:
    """Fluent builder for creating LLM instances.

    This builder makes it easy to construct complex LLM configurations with:
    - Primary model + fallbacks
    - Rate limiting (via tier)
    - Cost tracking
    - Context length management
    - Smart fallback strategies

    Example:
        >>> from coffee_maker.langchain_observe.builder import LLMBuilder
        >>> from coffee_maker.langchain_observe.cost_calculator import CostCalculator
        >>>
        >>> llm = (LLMBuilder()
        ...     .with_tier("tier1")
        ...     .with_primary("openai", "gpt-4o-mini")
        ...     .with_fallback("gemini", "gemini-2.5-flash")
        ...     .with_fallback("anthropic", "claude-3-5-haiku-20241022")
        ...     .with_cost_tracking(CostCalculator())
        ...     .with_smart_fallback()
        ...     .build())
    """

    def __init__(self):
        """Initialize builder with default values."""
        self._tier: str = "tier1"
        self._primary_provider: Optional[str] = None
        self._primary_model: Optional[str] = None
        self._fallbacks: List[Tuple[str, str]] = []
        self._cost_calculator = None
        self._langfuse_client = None
        self._max_wait_seconds: float = 300.0
        self._enable_context_fallback: bool = True
        self._fallback_strategy_type: str = "sequential"
        self._fallback_strategy: Optional[FallbackStrategy] = None
        self._context_strategy: Optional[ContextStrategy] = None

    def with_tier(self, tier: str) -> "LLMBuilder":
        """Set the API tier for rate limiting.

        Args:
            tier: Tier name (e.g., "tier1", "tier2")

        Returns:
            Self for chaining
        """
        self._tier = tier
        return self

    def with_primary(self, provider: str, model: str) -> "LLMBuilder":
        """Set the primary LLM.

        Args:
            provider: Provider name (e.g., "openai", "gemini", "anthropic")
            model: Model name (e.g., "gpt-4o-mini")

        Returns:
            Self for chaining
        """
        self._primary_provider = provider
        self._primary_model = model
        return self

    def with_fallback(self, provider: str, model: str) -> "LLMBuilder":
        """Add a fallback LLM.

        Args:
            provider: Provider name
            model: Model name

        Returns:
            Self for chaining
        """
        self._fallbacks.append((provider, model))
        return self

    def with_fallbacks(self, fallbacks: List[Tuple[str, str]]) -> "LLMBuilder":
        """Add multiple fallbacks at once.

        Args:
            fallbacks: List of (provider, model) tuples

        Returns:
            Self for chaining
        """
        self._fallbacks.extend(fallbacks)
        return self

    def with_cost_tracking(self, cost_calculator=None, langfuse_client=None) -> "LLMBuilder":
        """Enable cost tracking.

        Args:
            cost_calculator: CostCalculator instance (will create if None)
            langfuse_client: Langfuse client (will create if None)

        Returns:
            Self for chaining
        """
        if cost_calculator is None:
            try:
                from coffee_maker.langchain_observe.cost_calculator import CostCalculator
                from coffee_maker.langchain_observe.llm_config import MODEL_CONFIGS

                # Build pricing info from MODEL_CONFIGS
                pricing_info = {}
                for provider, models in MODEL_CONFIGS.items():
                    for model, config in models.items():
                        full_name = f"{provider}/{model}"
                        pricing_info[full_name] = config.get("pricing", {})

                cost_calculator = CostCalculator(pricing_info)
            except ImportError:
                logger.warning("Could not import CostCalculator or MODEL_CONFIGS")

        if langfuse_client is None:
            try:
                import langfuse

                langfuse_client = langfuse.get_client()
            except ImportError:
                logger.warning("Could not import langfuse")

        self._cost_calculator = cost_calculator
        self._langfuse_client = langfuse_client
        return self

    def with_max_wait(self, seconds: float) -> "LLMBuilder":
        """Set maximum wait time for rate limits.

        Args:
            seconds: Max wait in seconds

        Returns:
            Self for chaining
        """
        self._max_wait_seconds = seconds
        return self

    def with_context_fallback(self, enabled: bool = True) -> "LLMBuilder":
        """Enable or disable automatic context length fallback.

        Args:
            enabled: Whether to enable context fallback

        Returns:
            Self for chaining
        """
        self._enable_context_fallback = enabled
        return self

    def with_smart_fallback(self) -> "LLMBuilder":
        """Use smart fallback strategy (error-type aware).

        Returns:
            Self for chaining
        """
        self._fallback_strategy_type = "smart"
        return self

    def with_cost_optimized_fallback(self) -> "LLMBuilder":
        """Use cost-optimized fallback strategy (cheapest first).

        Returns:
            Self for chaining
        """
        self._fallback_strategy_type = "cost"
        return self

    def with_sequential_fallback(self) -> "LLMBuilder":
        """Use sequential fallback strategy (default).

        Returns:
            Self for chaining
        """
        self._fallback_strategy_type = "sequential"
        return self

    def with_custom_fallback_strategy(self, strategy: FallbackStrategy) -> "LLMBuilder":
        """Use a custom fallback strategy.

        Args:
            strategy: Custom FallbackStrategy instance

        Returns:
            Self for chaining
        """
        self._fallback_strategy = strategy
        return self

    def build(self) -> AutoPickerLLMRefactored:
        """Build the LLM instance.

        Returns:
            Configured AutoPickerLLMRefactored instance

        Raises:
            ValueError: If required configuration is missing
        """
        # Validate
        if self._primary_provider is None or self._primary_model is None:
            raise ValueError("Primary model not set. Call with_primary() first.")

        # Import here to avoid circular dependencies
        from coffee_maker.langchain_observe.auto_picker_llm_refactored import create_auto_picker_llm_refactored

        # Create fallback strategy if not custom
        if self._fallback_strategy is None:
            if self._fallback_strategy_type == "smart":
                # Get model configs for smart fallback
                model_configs = self._build_model_configs()
                self._fallback_strategy = create_fallback_strategy("smart", model_configs=model_configs)
            elif self._fallback_strategy_type == "cost":
                # Get model costs for cost-optimized fallback
                model_costs = self._build_model_costs()
                self._fallback_strategy = create_fallback_strategy("cost", model_costs=model_costs)
            else:
                # Sequential (default)
                self._fallback_strategy = create_fallback_strategy("sequential")

        # Build LLM using helper function
        llm = create_auto_picker_llm_refactored(
            primary_provider=self._primary_provider,
            primary_model=self._primary_model,
            fallback_configs=self._fallbacks,
            tier=self._tier,
            cost_calculator=self._cost_calculator,
            langfuse_client=self._langfuse_client,
            enable_context_fallback=self._enable_context_fallback,
            max_wait_seconds=self._max_wait_seconds,
            fallback_strategy=self._fallback_strategy,
        )

        return llm

    def _build_model_configs(self) -> dict:
        """Build model configurations for smart fallback.

        Returns:
            Dict mapping model names to configs
        """
        try:
            from coffee_maker.langchain_observe.llm_config import MODEL_CONFIGS

            configs = {}
            # Add primary
            full_name = f"{self._primary_provider}/{self._primary_model}"
            if self._primary_provider in MODEL_CONFIGS and self._primary_model in MODEL_CONFIGS[self._primary_provider]:
                configs[full_name] = MODEL_CONFIGS[self._primary_provider][self._primary_model]

            # Add fallbacks
            for provider, model in self._fallbacks:
                full_name = f"{provider}/{model}"
                if provider in MODEL_CONFIGS and model in MODEL_CONFIGS[provider]:
                    configs[full_name] = MODEL_CONFIGS[provider][model]

            return configs
        except ImportError:
            logger.warning("Could not import MODEL_CONFIGS")
            return {}

    def _build_model_costs(self) -> dict:
        """Build model costs for cost-optimized fallback.

        Returns:
            Dict mapping model names to costs per 1K tokens
        """
        try:
            from coffee_maker.langchain_observe.llm_config import MODEL_CONFIGS

            costs = {}
            # Calculate average cost per 1K tokens (input + output) / 2
            # Add primary
            full_name = f"{self._primary_provider}/{self._primary_model}"
            if self._primary_provider in MODEL_CONFIGS and self._primary_model in MODEL_CONFIGS[self._primary_provider]:
                config = MODEL_CONFIGS[self._primary_provider][self._primary_model]
                # Average of input and output cost
                avg_cost = (config.get("input_cost_per_1k", 0) + config.get("output_cost_per_1k", 0)) / 2
                costs[full_name] = avg_cost

            # Add fallbacks
            for provider, model in self._fallbacks:
                full_name = f"{provider}/{model}"
                if provider in MODEL_CONFIGS and model in MODEL_CONFIGS[provider]:
                    config = MODEL_CONFIGS[provider][model]
                    avg_cost = (config.get("input_cost_per_1k", 0) + config.get("output_cost_per_1k", 0)) / 2
                    costs[full_name] = avg_cost

            return costs
        except ImportError:
            logger.warning("Could not import MODEL_CONFIGS")
            return {}


class SmartLLM:
    """Ultra-simple facade for creating LLMs with smart defaults.

    This is the simplest way to get a production-ready LLM with all features:
    - Automatic scheduling and rate limiting
    - Smart fallbacks based on error type
    - Cost tracking
    - Context length management

    Example:
        >>> from coffee_maker.langchain_observe.builder import SmartLLM
        >>>
        >>> # Simplest: use tier defaults
        >>> llm = SmartLLM.for_tier("tier1")
        >>>
        >>> # With custom primary
        >>> llm = SmartLLM.for_tier("tier1", primary=("openai", "gpt-4o-mini"))
        >>>
        >>> # With custom fallbacks
        >>> llm = SmartLLM.for_tier(
        ...     "tier1",
        ...     primary=("openai", "gpt-4o-mini"),
        ...     fallbacks=[("gemini", "gemini-2.5-flash")]
        ... )
    """

    @staticmethod
    def for_tier(
        tier: str,
        primary: Optional[Tuple[str, str]] = None,
        fallbacks: Optional[List[Tuple[str, str]]] = None,
    ) -> AutoPickerLLMRefactored:
        """Create a smart LLM for a given tier.

        Args:
            tier: API tier (e.g., "tier1")
            primary: Optional (provider, model) tuple
            fallbacks: Optional list of (provider, model) tuples

        Returns:
            Configured LLM with smart defaults

        Example:
            >>> llm = SmartLLM.for_tier("tier1")
            >>> llm = SmartLLM.for_tier("tier1", primary=("openai", "gpt-4o"))
        """
        builder = LLMBuilder().with_tier(tier)

        # Set primary (or use smart default)
        if primary:
            builder.with_primary(primary[0], primary[1])
        else:
            # Smart default: gpt-4o-mini
            builder.with_primary("openai", "gpt-4o-mini")

        # Set fallbacks (or use smart defaults)
        if fallbacks:
            builder.with_fallbacks(fallbacks)
        else:
            # Smart defaults: gemini, then claude
            builder.with_fallback("gemini", "gemini-2.5-flash")
            builder.with_fallback("anthropic", "claude-3-5-haiku-20241022")

        # Enable all smart features
        return (
            builder.with_cost_tracking()
            .with_context_fallback(True)
            .with_smart_fallback()  # Smart fallback based on error type
            .build()
        )

    @staticmethod
    def fast(tier: str = "tier1") -> AutoPickerLLMRefactored:
        """Create a fast, cheap LLM optimized for speed and cost.

        Args:
            tier: API tier

        Returns:
            LLM optimized for speed/cost
        """
        return (
            LLMBuilder()
            .with_tier(tier)
            .with_primary("openai", "gpt-4o-mini")
            .with_fallback("gemini", "gemini-2.5-flash")
            .with_cost_tracking()
            .with_cost_optimized_fallback()  # Prefer cheaper models
            .build()
        )

    @staticmethod
    def powerful(tier: str = "tier1") -> AutoPickerLLMRefactored:
        """Create a powerful LLM optimized for quality.

        Args:
            tier: API tier

        Returns:
            LLM optimized for quality
        """
        return (
            LLMBuilder()
            .with_tier(tier)
            .with_primary("openai", "gpt-4o")
            .with_fallback("anthropic", "claude-3-5-sonnet-20241022")
            .with_fallback("gemini", "gemini-2.5-pro")
            .with_cost_tracking()
            .with_smart_fallback()
            .build()
        )
