"""Centralized configuration for LLM models and their rate limits.

This module consolidates rate limit information from various provider files
and provides a single source of truth for model configurations.
"""

from coffee_maker.langchain_observe.rate_limiter import RateLimitConfig

# Model configurations with rate limits and capabilities
MODEL_CONFIGS = {
    "openai": {
        "gpt-4o": {
            "context_length": 128000,
            "max_output_tokens": 4096,
            "rate_limits": {
                "tier1": RateLimitConfig(requests_per_minute=500, tokens_per_minute=30000, requests_per_day=10000),
                "tier2": RateLimitConfig(requests_per_minute=5000, tokens_per_minute=450000, requests_per_day=10000),
            },
            "pricing": {"input_per_1m": 2.50, "output_per_1m": 10.00},
            "use_cases": ["complex_reasoning", "code_review", "primary"],
        },
        "gpt-4o-mini": {
            "context_length": 128000,
            "max_output_tokens": 16384,
            "rate_limits": {
                "tier1": RateLimitConfig(requests_per_minute=500, tokens_per_minute=200000, requests_per_day=10000),
                "tier2": RateLimitConfig(requests_per_minute=5000, tokens_per_minute=2000000, requests_per_day=10000),
            },
            "pricing": {"input_per_1m": 0.150, "output_per_1m": 0.600},
            "use_cases": ["general", "fallback", "budget"],
        },
        "gpt-3.5-turbo": {
            "context_length": 16385,
            "max_output_tokens": 4096,
            "rate_limits": {
                "tier1": RateLimitConfig(requests_per_minute=500, tokens_per_minute=60000, requests_per_day=10000),
            },
            "pricing": {"input_per_1m": 0.50, "output_per_1m": 1.50},
            "use_cases": ["budget", "simple"],
        },
        "gpt-4.1": {
            "context_length": 1000000,
            "max_output_tokens": 64000,
            "rate_limits": {
                "tier1": RateLimitConfig(requests_per_minute=100, tokens_per_minute=100000, requests_per_day=1000),
            },
            "pricing": {"input_per_1m": 10.00, "output_per_1m": 30.00},
            "use_cases": ["large_context", "complex_reasoning"],
        },
        "o1": {
            "context_length": 200000,
            "max_output_tokens": 100000,
            "rate_limits": {
                "tier1": RateLimitConfig(requests_per_minute=20, tokens_per_minute=100000, requests_per_day=500),
                "tier2": RateLimitConfig(requests_per_minute=40, tokens_per_minute=200000, requests_per_day=1000),
            },
            "pricing": {"input_per_1m": 15.00, "output_per_1m": 60.00},
            "use_cases": ["reasoning", "planning", "complex_problem_solving"],
        },
        "o1-mini": {
            "context_length": 128000,
            "max_output_tokens": 65536,
            "rate_limits": {
                "tier1": RateLimitConfig(requests_per_minute=30, tokens_per_minute=150000, requests_per_day=1000),
                "tier2": RateLimitConfig(requests_per_minute=60, tokens_per_minute=300000, requests_per_day=2000),
            },
            "pricing": {"input_per_1m": 3.00, "output_per_1m": 12.00},
            "use_cases": ["reasoning", "planning", "budget_reasoning"],
        },
    },
    "gemini": {
        "gemini-2.5-pro": {
            "context_length": 2097152,  # 2M tokens
            "max_output_tokens": 8192,
            "rate_limits": {
                "free": RateLimitConfig(requests_per_minute=5, tokens_per_minute=250000, requests_per_day=100),
                "paid": RateLimitConfig(
                    requests_per_minute=1000,
                    tokens_per_minute=-1,  # Unlimited
                    requests_per_day=-1,  # Unlimited
                ),
            },
            "pricing": {
                "free": True,
                "input_per_1m_low": 1.25,
                "output_per_1m_low": 10.00,
                "input_per_1m_high": 2.50,
                "output_per_1m_high": 15.00,
            },
            "use_cases": ["large_context", "primary"],
        },
        "gemini-2.5-flash-lite": {
            "context_length": 1048576,  # 1M tokens
            "max_output_tokens": 8192,
            "rate_limits": {
                "free": RateLimitConfig(requests_per_minute=15, tokens_per_minute=250000, requests_per_day=1000),
                "paid": RateLimitConfig(
                    requests_per_minute=2000,
                    tokens_per_minute=-1,  # Unlimited
                    requests_per_day=-1,  # Unlimited
                ),
            },
            "pricing": {"free": True, "input_per_1m": 0.10, "output_per_1m": 0.40},
            "use_cases": ["large_context", "budget", "fallback"],
        },
        "gemini-1.5-flash": {
            "context_length": 1048576,  # 1M tokens
            "max_output_tokens": 8192,
            "rate_limits": {
                "free": RateLimitConfig(requests_per_minute=15, tokens_per_minute=1000000, requests_per_day=1500),
                "paid": RateLimitConfig(requests_per_minute=2000, tokens_per_minute=8192000, requests_per_day=-1),
            },
            "pricing": {"free": True, "input_per_1m": 0.35, "output_per_1m": 1.05},
            "use_cases": ["large_context", "general"],
        },
        "gemini-2.0-flash-thinking-exp": {
            "context_length": 32768,
            "max_output_tokens": 8192,
            "rate_limits": {
                "free": RateLimitConfig(requests_per_minute=10, tokens_per_minute=32000, requests_per_day=500),
                "tier1": RateLimitConfig(requests_per_minute=50, tokens_per_minute=100000, requests_per_day=2000),
            },
            "pricing": {"free": True, "input_per_1m": 0.00, "output_per_1m": 0.00},
            "use_cases": ["reasoning", "planning", "problem_solving"],
        },
    },
}


def get_rate_limits_for_tier(tier: str = "tier1") -> dict:
    """Get rate limit configurations for all models at a specific tier.

    Args:
        tier: API tier (e.g., 'free', 'tier1', 'tier2', 'paid')

    Returns:
        Dictionary mapping model names to RateLimitConfig objects
    """
    rate_limits = {}

    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            if tier in config["rate_limits"]:
                full_model_name = f"{provider}/{model_name}"
                rate_limits[full_model_name] = config["rate_limits"][tier]

    return rate_limits


def get_model_context_length(provider: str, model: str) -> int:
    """Get the context length for a specific model.

    Args:
        provider: Provider name (e.g., 'openai', 'gemini')
        model: Model name

    Returns:
        Context length in tokens
    """
    if provider in MODEL_CONFIGS and model in MODEL_CONFIGS[provider]:
        return MODEL_CONFIGS[provider][model]["context_length"]
    return 4096  # Default fallback


def get_fallback_models(use_case: str = None) -> list:
    """Get a list of models suitable for fallback, ordered by preference.

    Args:
        use_case: Optional use case to filter by (e.g., 'large_context', 'budget')

    Returns:
        List of (provider, model_name) tuples ordered by preference
    """
    fallback_models = []

    # Priority order for fallbacks
    priority_order = [
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-2.5-flash-lite"),
        ("gemini", "gemini-1.5-flash"),
        ("openai", "gpt-3.5-turbo"),
    ]

    for provider, model_name in priority_order:
        if provider in MODEL_CONFIGS and model_name in MODEL_CONFIGS[provider]:
            config = MODEL_CONFIGS[provider][model_name]
            if use_case is None or use_case in config["use_cases"]:
                fallback_models.append((provider, model_name))

    return fallback_models


def get_large_context_model() -> tuple:
    """Get the model with the largest context window.

    Returns:
        (provider, model_name) tuple
    """
    max_context = 0
    best_model = None

    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            if config["context_length"] > max_context:
                max_context = config["context_length"]
                best_model = (provider, model_name)

    return best_model if best_model else ("openai", "gpt-4o-mini")


def get_large_context_models() -> list:
    """Get all models sorted by context length (largest first).

    Returns:
        List of (provider, model_name, context_length) tuples sorted by context descending
    """
    models_with_context = []

    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            context = config["context_length"]
            models_with_context.append((provider, model_name, context))

    # Sort by context length descending
    sorted_models = sorted(models_with_context, key=lambda x: x[2], reverse=True)

    return sorted_models


def get_model_context_length_from_name(full_model_name: str) -> int:
    """Get context length from full model name.

    Args:
        full_model_name: Format "provider/model" (e.g., "openai/gpt-4o")

    Returns:
        Context length in tokens

    Raises:
        ValueError: If model not found
    """
    if "/" not in full_model_name:
        raise ValueError(f"Invalid model name format: {full_model_name}. Expected 'provider/model'")

    provider, model = full_model_name.split("/", 1)

    if provider not in MODEL_CONFIGS:
        raise ValueError(f"Unknown provider: {provider}")

    if model not in MODEL_CONFIGS[provider]:
        raise ValueError(f"Unknown model: {model} for provider {provider}")

    return MODEL_CONFIGS[provider][model]["context_length"]
