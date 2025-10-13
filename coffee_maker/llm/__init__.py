"""
LLM abstraction layer for MonolithicCoffeeMakerAgent.

This package provides a unified interface for working with multiple LLM providers,
including rate limiting, scheduling, and fallback strategies.

Public API:
    - get_llm(): Create an LLM instance
    - SmartLLM: Intelligent LLM wrapper with auto-retry
    - LLMBuilder: Builder pattern for LLM configuration

Example:
    >>> from coffee_maker.llm import get_llm
    >>> llm = get_llm(provider="openai", model="gpt-4")
    >>> response = llm.generate("Hello, world!")
"""

# Note: Imports are done directly in modules to avoid circular dependencies
# Users should import from specific modules:
#   from coffee_maker.llm.factory import get_llm
#   from coffee_maker.llm.builder import SmartLLM
#   from coffee_maker.llm.config import LLMConfig

__all__ = [
    # Factory
    "get_llm",
    "get_scheduled_llm",
    # Builder
    "SmartLLM",
    "LLMBuilder",
]


def __getattr__(name: str):
    """Lazy imports to avoid circular dependencies."""
    if name == "get_llm":
        from coffee_maker.llm.factory import get_llm

        return get_llm
    elif name == "get_scheduled_llm":
        from coffee_maker.llm.factory import get_scheduled_llm

        return get_scheduled_llm
    elif name == "SmartLLM":
        from coffee_maker.llm.builder import SmartLLM

        return SmartLLM
    elif name == "LLMBuilder":
        from coffee_maker.llm.builder import LLMBuilder

        return LLMBuilder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
