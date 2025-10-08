"""LLM Tools for ReAct Agent.

This module provides LLM instances wrapped as tools that can be used by ReAct agents
to invoke specific models based on purpose (e.g., long-context, fast, accurate).
"""

import logging
from typing import Any, Dict, List

from langchain_core.tools import Tool

from coffee_maker.langchain_observe.agents import get_llm
from coffee_maker.langchain_observe.auto_picker_llm import AutoPickerLLM
from coffee_maker.langchain_observe.rate_limiter import RateLimitTracker

logger = logging.getLogger(__name__)

# Define model purposes and their configurations
# Format: purpose -> (provider, primary_model, fallback_model, description)
MODEL_PURPOSES = {
    "long_context": {
        "openai": ("openai", "gpt-4o", "gpt-4o-mini", "For tasks requiring very long context (128K tokens)"),
        "gemini": ("gemini", "gemini-2.0-pro", "gemini-2.5-flash", "For tasks requiring very long context (1M tokens)"),
    },
    "reasoning": {
        "openai": ("openai", "o1", "o1-mini", "Advanced reasoning and planning with chain-of-thought"),
        "gemini": (
            "gemini",
            "gemini-2.0-flash-thinking-exp",
            "gemini-2.5-flash",
            "Extended thinking and problem-solving",
        ),
    },
    "best_model": {
        "openai": ("openai", "gpt-4o", "gpt-4o-mini", "Best overall OpenAI model for quality and performance"),
        "gemini": (
            "gemini",
            "gemini-2.0-pro",
            "gemini-2.5-flash",
            "Best overall Gemini model for quality and performance",
        ),
    },
    "second_best_model": {
        "openai": ("openai", "gpt-4o-mini", "gpt-3.5-turbo", "Good quality with better cost efficiency"),
        "gemini": ("gemini", "gemini-2.5-flash", "gemini-2.5-flash-lite", "Good quality with better cost efficiency"),
    },
    "fast": {
        "openai": ("openai", "gpt-4o-mini", "gpt-3.5-turbo", "Fastest OpenAI model for quick tasks"),
        "gemini": ("gemini", "gemini-2.5-flash-lite", "gemini-2.5-flash", "Fastest Gemini model"),
    },
    "accurate": {
        "openai": ("openai", "gpt-4o", "gpt-4o-mini", "Most accurate OpenAI model"),
        "gemini": ("gemini", "gemini-2.0-pro", "gemini-2.5-flash", "Most accurate Gemini model"),
    },
    "budget": {
        "openai": ("openai", "gpt-4o-mini", "gpt-3.5-turbo", "Most cost-effective OpenAI model"),
        "gemini": ("gemini", "gemini-2.5-flash-lite", "gemini-2.5-flash", "Most cost-effective Gemini model"),
    },
}


def create_llm_tool_wrapper(
    purpose: str,
    provider: str,
    rate_tracker: RateLimitTracker,
    tier: str = "tier1",
    auto_wait: bool = True,
    max_wait_seconds: float = 10.0,
) -> AutoPickerLLM:
    """Create an AutoPickerLLM configured for a specific purpose and provider.

    Args:
        purpose: Purpose of the LLM (e.g., 'long_context', 'fast', 'accurate')
        provider: Provider to use ('openai' or 'gemini')
        rate_tracker: Shared rate limit tracker instance
        tier: API tier for rate limiting
        auto_wait: Whether to auto-wait when rate limited
        max_wait_seconds: Max seconds to wait before fallback

    Returns:
        Configured AutoPickerLLM instance

    Raises:
        ValueError: If purpose or provider is invalid
    """
    if purpose not in MODEL_PURPOSES:
        raise ValueError(f"Invalid purpose '{purpose}'. Valid purposes: {list(MODEL_PURPOSES.keys())}")

    if provider not in MODEL_PURPOSES[purpose]:
        available = list(MODEL_PURPOSES[purpose].keys())
        raise ValueError(f"Invalid provider '{provider}' for purpose '{purpose}'. Available: {available}")

    provider_name, primary_model, fallback_model, description = MODEL_PURPOSES[purpose][provider]

    logger.info(f"Creating LLM tool: {purpose} ({provider}) - {description}")
    logger.info(f"  Primary: {primary_model}, Fallback: {fallback_model}")

    # Create primary LLM
    primary_llm = get_llm(provider=provider_name, model=primary_model)
    primary_model_name = f"{provider_name}/{primary_model}"

    # Create fallback LLM
    fallback_llm = get_llm(provider=provider_name, model=fallback_model)
    fallback_model_name = f"{provider_name}/{fallback_model}"

    # Create AutoPickerLLM
    auto_picker = AutoPickerLLM(
        primary_llm=primary_llm,
        primary_model_name=primary_model_name,
        fallback_llms=[(fallback_llm, fallback_model_name)],
        rate_tracker=rate_tracker,
        auto_wait=auto_wait,
        max_wait_seconds=max_wait_seconds,
    )

    return auto_picker


def invoke_llm_tool(
    provider: str,
    purpose: str,
    task_description: str,
    rate_tracker: RateLimitTracker,
    tier: str = "tier1",
) -> str:
    """Invoke an LLM tool with specific provider and purpose.

    This is the function that gets wrapped as a LangChain tool.

    Args:
        provider: Provider to use ('openai' or 'gemini')
        purpose: Purpose/use case ('long_context', 'fast', 'accurate', 'budget', 'second_best_model')
        task_description: The task/prompt to send to the LLM
        rate_tracker: Rate limit tracker instance
        tier: API tier

    Returns:
        LLM response as string
    """
    logger.info(f"Invoking LLM tool: provider={provider}, purpose={purpose}")

    try:
        llm = create_llm_tool_wrapper(
            purpose=purpose,
            provider=provider,
            rate_tracker=rate_tracker,
            tier=tier,
        )

        response = llm.invoke({"input": task_description})

        # Extract content from response
        if hasattr(response, "content"):
            return response.content
        return str(response)

    except Exception as e:
        logger.error(f"LLM tool invocation failed: {e}", exc_info=True)
        return f"Error invoking LLM: {str(e)}"


def create_llm_tools(tier: str = "tier1") -> List[Tool]:
    """Create all LLM tools for the ReAct agent.

    Args:
        tier: API tier for rate limiting

    Returns:
        List of LangChain Tool instances
    """
    # Use global rate tracker to ensure rate limits are shared across all LLM instances
    from coffee_maker.langchain_observe.global_rate_tracker import get_global_rate_tracker

    rate_tracker = get_global_rate_tracker(tier)

    tools = []

    # Create a tool for each purpose
    for purpose, providers_config in MODEL_PURPOSES.items():
        for provider in providers_config.keys():
            _, _, _, description = providers_config[provider]

            tool_name = f"invoke_llm_{provider}_{purpose}"
            tool_description = f"""Invoke {provider} LLM for {purpose} tasks. {description}

Input format (JSON):
{{
    "task_description": "The task or prompt to send to the LLM"
}}

Use this tool when you need to:
- {purpose.replace('_', ' ').title()}: {description}
- Provider preference: {provider}

Example:
{{"task_description": "Analyze this code and suggest improvements: <code here>"}}
"""

            def make_tool_func(p=provider, pur=purpose):
                def tool_func(task_description: str) -> str:
                    """Invoke LLM with specific provider and purpose."""
                    return invoke_llm_tool(
                        provider=p,
                        purpose=pur,
                        task_description=task_description,
                        rate_tracker=rate_tracker,
                        tier=tier,
                    )

                return tool_func

            tool = Tool(
                name=tool_name,
                func=make_tool_func(),
                description=tool_description,
            )

            tools.append(tool)
            logger.info(f"Created LLM tool: {tool_name}")

    logger.info(f"Created {len(tools)} LLM tools total")
    return tools


def get_llm_tool_names() -> List[str]:
    """Get list of all LLM tool names.

    Returns:
        List of tool names
    """
    names = []
    for purpose in MODEL_PURPOSES.keys():
        for provider in MODEL_PURPOSES[purpose].keys():
            names.append(f"invoke_llm_{provider}_{purpose}")
    return names


def get_llm_tools_summary() -> Dict[str, Any]:
    """Get summary of available LLM tools.

    Returns:
        Dictionary with tools organized by purpose and provider
    """
    summary = {}
    for purpose, providers_config in MODEL_PURPOSES.items():
        summary[purpose] = {}
        for provider, (prov_name, primary, fallback, desc) in providers_config.items():
            summary[purpose][provider] = {
                "primary_model": f"{prov_name}/{primary}",
                "fallback_model": f"{prov_name}/{fallback}",
                "description": desc,
                "tool_name": f"invoke_llm_{provider}_{purpose}",
            }
    return summary
