"""Strategy pattern implementations for LLM management.

This package contains pluggable strategies for handling various aspects
of LLM invocation:
- Retry logic with exponential backoff
- Proactive scheduling to prevent rate limits
- Rate limiting
- Context length management
- Cost tracking

Each strategy is focused on a single responsibility and can be tested
and extended independently.
"""

from coffee_maker.langchain_observe.strategies.retry import (
    RetryStrategy,
    ExponentialBackoffRetry,
)
from coffee_maker.langchain_observe.strategies.scheduling import (
    SchedulingStrategy,
    ProactiveRateLimitScheduler,
)

__all__ = [
    "RetryStrategy",
    "ExponentialBackoffRetry",
    "SchedulingStrategy",
    "ProactiveRateLimitScheduler",
]
