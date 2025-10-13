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

# Core factory and builder
from coffee_maker.llm.factory import get_llm, LLM
from coffee_maker.llm.builder import SmartLLM, LLMBuilder

# Configuration
from coffee_maker.llm.config import LLMConfig

__all__ = [
    # Factory
    "get_llm",
    "LLM",
    # Builder
    "SmartLLM",
    "LLMBuilder",
    # Configuration
    "LLMConfig",
]
