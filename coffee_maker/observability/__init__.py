"""
Observability and tracing for MonolithicCoffeeMakerAgent.

This package provides observability using Langfuse, including:
- Agent execution tracing
- Cost tracking
- Performance analytics
- Retry logic monitoring

All modules in this package use the @observe decorator from Langfuse.

Note: Core LLM abstractions have moved to coffee_maker.llm package.
This package is now focused purely on observability and tracing.

Public API:
    - TraceableAgent: Agent with built-in tracing
    - CostCalculator: Track LLM costs
    - retry_with_observability: Retry logic with tracing

Example:
    >>> from coffee_maker.observability import CostCalculator
    >>> calculator = CostCalculator()
    >>> cost = calculator.calculate_cost(model="gpt-4", tokens=1000)

Migration from langfuse_observe:
    For LLM functionality, use coffee_maker.llm instead:
    - get_llm() → coffee_maker.llm.get_llm()
    - SmartLLM → coffee_maker.llm.SmartLLM
    - RateLimiter → coffee_maker.llm.rate_limiting.RateLimiter
"""

from typing import TYPE_CHECKING, List

# Core observability components (use @observe)
from coffee_maker.observability.cost_calculator import CostCalculator

# Analytics
from coffee_maker.observability.analytics import (
    LangfuseExporter,
    PerformanceAnalyzer,
)

# Lazy import to avoid circular dependency with llm.factory
# (agents.py imports from llm.factory, which imports from observability.utils)
if TYPE_CHECKING:
    from coffee_maker.observability.agents import (
        agent_with_tracing,
        TraceableAgent,
    )


def __getattr__(name: str):
    """Lazy import to avoid circular dependencies."""
    if name == "agent_with_tracing":
        from coffee_maker.observability.agents import agent_with_tracing

        return agent_with_tracing
    elif name == "TraceableAgent":
        from coffee_maker.observability.agents import TraceableAgent

        return TraceableAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__: List[str] = [
    # Cost tracking
    "CostCalculator",
    # Agent tracing
    "agent_with_tracing",
    "TraceableAgent",
    # Analytics
    "LangfuseExporter",
    "PerformanceAnalyzer",
]
