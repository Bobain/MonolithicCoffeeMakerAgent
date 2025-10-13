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

from coffee_maker.llm.rate_limiting.limiter import RateLimiter
from coffee_maker.llm.rate_limiting.tracker import GlobalRateTracker
from coffee_maker.llm.rate_limiting.budget import CostBudget

__all__ = [
    "RateLimiter",
    "GlobalRateTracker",
    "CostBudget",
]
