"""
Rate limiting subsystem for LLM calls.

This module provides rate limiting, budget tracking, and global rate management
to prevent exceeding API quotas and costs.

Public API:
    - RateLimiter: Rate limiting for LLM calls
    - GlobalRateTracker: Track rates across all LLM instances
    - CostBudget: Budget management for LLM costs

Example:
    >>> from coffee_maker.llm.rate_limiting import RateLimiter
    >>> limiter = RateLimiter(requests_per_minute=60)
    >>> with limiter:
    ...     llm.generate("Hello")
"""

# Note: Import directly from submodules to avoid circular dependencies
# Users should import from specific modules:
#   from coffee_maker.llm.rate_limiting.limiter import RateLimitTracker
#   from coffee_maker.llm.rate_limiting.tracker import get_global_rate_tracker

__all__ = [
    "RateLimitConfig",
    "RateLimitTracker",
    "get_global_rate_tracker",
    "CostBudgetTracker",
]


def __getattr__(name: str):
    """Lazy imports to avoid circular dependencies."""
    if name == "RateLimitConfig":
        from coffee_maker.llm.rate_limiting.limiter import RateLimitConfig

        return RateLimitConfig
    elif name == "RateLimitTracker":
        from coffee_maker.llm.rate_limiting.limiter import RateLimitTracker

        return RateLimitTracker
    elif name == "get_global_rate_tracker":
        from coffee_maker.llm.rate_limiting.tracker import get_global_rate_tracker

        return get_global_rate_tracker
    elif name == "CostBudgetTracker":
        from coffee_maker.llm.rate_limiting.budget import CostBudgetTracker

        return CostBudgetTracker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
