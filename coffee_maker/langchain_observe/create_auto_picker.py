"""Helper functions to create AutoPickerLLM instances with sensible defaults.

DEPRECATED: This module uses the old AutoPickerLLM.
Use coffee_maker.langchain_observe.builder.SmartLLM for new code.
"""

import logging

import langfuse

from coffee_maker.langchain_observe.auto_picker_llm_refactored import (
    AutoPickerLLMRefactored,
    create_auto_picker_llm_refactored,
)
from coffee_maker.langchain_observe.cost_calculator import CostCalculator
from coffee_maker.langchain_observe.llm_config import MODEL_CONFIGS, get_fallback_models

logger = logging.getLogger(__name__)


def create_auto_picker_llm(
    tier: str = "tier1",
    primary_provider: str = "openai",
    primary_model: str = "gpt-4o-mini",
    auto_wait: bool = True,
    max_wait_seconds: float = 300.0,
    max_retries: int = 3,
    backoff_base: float = 2.0,
    min_wait_before_fallback: float = 90.0,
    streaming: bool = False,
) -> AutoPickerLLMRefactored:
    """Create an AutoPickerLLMRefactored instance with automatic fallback configuration.

    DEPRECATED: Use coffee_maker.langchain_observe.builder.SmartLLM instead.

    Args:
        tier: API tier for rate limiting ('free', 'tier1', 'tier2', 'paid')
        primary_provider: Primary LLM provider ('openai', 'gemini')
        primary_model: Primary model name
        auto_wait: Whether to automatically wait when rate limited (deprecated, always enabled)
        max_wait_seconds: Maximum seconds to wait before falling back (default: 300s = 5min)
        max_retries: Maximum retry attempts (deprecated, managed by ScheduledLLM)
        backoff_base: Exponential backoff multiplier (deprecated, managed by ScheduledLLM)
        min_wait_before_fallback: Minimum seconds before fallback (deprecated, managed by ScheduledLLM)
        streaming: Whether to enable streaming

    Returns:
        Configured AutoPickerLLMRefactored instance

    Example:
        >>> auto_llm = create_auto_picker_llm(tier="tier1", streaming=True)
        >>> response = auto_llm.invoke({"input": "Hello"})
    """
    from coffee_maker.langchain_observe.global_rate_tracker import get_global_rate_tracker

    # Use global rate tracker to ensure rate limits are shared across all LLM instances
    rate_tracker = get_global_rate_tracker(tier)

    # Get fallback models
    fallback_model_configs = get_fallback_models()
    fallback_configs = []

    for provider, model in fallback_model_configs:
        # Skip if it's the same as primary
        if provider == primary_provider and model == primary_model:
            continue

        # Check if this model is available in the current tier
        full_name = f"{provider}/{model}"
        if full_name not in rate_tracker.model_limits:
            logger.debug(f"Skipping {full_name} - not available in tier {tier}")
            continue

        logger.info(f"Adding fallback: {full_name}")
        fallback_configs.append((provider, model))

    if not fallback_configs:
        logger.warning("No fallback models available - will only use primary model")

    # Create cost calculator with pricing info
    pricing_info = {}
    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            full_name = f"{provider}/{model_name}"
            pricing_info[full_name] = config.get("pricing", {})

    cost_calculator = CostCalculator(pricing_info)
    logger.info("Initialized CostCalculator with pricing info for all models")

    # Get Langfuse client for cost tracking
    try:
        langfuse_client = langfuse.get_client()
        logger.info("Initialized Langfuse client for cost tracking")
    except Exception as e:
        logger.warning(f"Could not initialize Langfuse client: {e}")
        langfuse_client = None

    # Use the new refactored version
    auto_picker = create_auto_picker_llm_refactored(
        primary_provider=primary_provider,
        primary_model=primary_model,
        fallback_configs=fallback_configs,
        tier=tier,
        cost_calculator=cost_calculator,
        langfuse_client=langfuse_client,
        max_wait_seconds=max_wait_seconds,
        streaming=streaming,
    )

    logger.info(f"Created AutoPickerLLMRefactored with {len(fallback_configs)} fallback options")
    return auto_picker


def create_auto_picker_for_react_agent(
    tier: str = "tier1", streaming: bool = True, max_wait_seconds: float = 5.0
) -> AutoPickerLLMRefactored:
    """Create AutoPickerLLMRefactored optimized for ReAct agents.

    DEPRECATED: Use coffee_maker.langchain_observe.builder.SmartLLM.fast() instead.

    Args:
        tier: API tier
        streaming: Enable streaming for real-time output
        max_wait_seconds: Max wait before fallback (shorter for interactive agents)

    Returns:
        Configured AutoPickerLLMRefactored
    """
    return create_auto_picker_llm(
        tier=tier,
        primary_provider="openai",
        primary_model="gpt-4o-mini",
        auto_wait=True,
        max_wait_seconds=max_wait_seconds,
        streaming=streaming,
    )
