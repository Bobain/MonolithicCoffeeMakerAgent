#!/usr/bin/env python3
"""Fallback strategy examples for Multi-AI Provider Support.

This script demonstrates automatic fallback, retry logic, and resilience features.

Requirements:
    - Multiple providers configured (at least 2)
    - API keys set in environment variables
    - coffee-maker installed with ai_providers package

Usage:
    python3 examples/priority_8/fallback_strategy.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.ai_providers import (
    FallbackStrategy,
    AllProvidersFailedError,
)


def example_1_basic_fallback():
    """Example 1: Basic fallback usage."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Fallback")
    print("=" * 60)

    strategy = FallbackStrategy()

    result = strategy.execute_with_fallback(
        prompt="Write a function to check if a string is a palindrome",
        system_prompt="You are an expert Python developer.",
    )

    print(f"✓ Success with provider: {result.model}")
    print(f"  Response: {result.content[:100]}...")
    print(f"  Tokens: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")


def example_2_custom_fallback_order():
    """Example 2: Custom fallback provider order."""
    print("\n" + "=" * 60)
    print("Example 2: Custom Fallback Order")
    print("=" * 60)

    strategy = FallbackStrategy()

    # Try OpenAI first, then Claude, then Gemini
    result = strategy.execute_with_fallback(
        prompt="Explain what a microservice is",
        providers=["openai", "claude", "gemini"],  # Custom order
    )

    print(f"✓ Success with: {result.model}")
    print(f"  Provider: {result.metadata.get('provider', 'unknown')}")


def example_3_cost_aware_fallback():
    """Example 3: Cost-aware execution with fallback."""
    print("\n" + "=" * 60)
    print("Example 3: Cost-Aware Fallback")
    print("=" * 60)

    strategy = FallbackStrategy()

    # Enable cost checking (will skip providers that exceed limits)
    result = strategy.execute_with_fallback(
        prompt="Generate API documentation for a REST endpoint",
        check_cost=True,  # Check cost limits before execution
    )

    print(f"✓ Success with: {result.model}")
    print(f"  Response: {result.content[:80]}...")


def example_4_fallback_with_context():
    """Example 4: Fallback with working directory context."""
    print("\n" + "=" * 60)
    print("Example 4: Fallback with Context")
    print("=" * 60)

    strategy = FallbackStrategy()

    # Provide working directory context (useful for file operations)
    result = strategy.execute_with_fallback(
        prompt="List best practices for Python project structure",
        working_dir=str(project_root),
    )

    print(f"✓ Success with: {result.model}")
    print(f"  Response: {result.content[:100]}...")


def example_5_error_handling():
    """Example 5: Handle all providers failing."""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)

    strategy = FallbackStrategy()

    try:
        # This will try all providers in fallback order
        result = strategy.execute_with_fallback(
            prompt="Test fallback error handling",
            providers=["claude", "openai", "gemini"],
        )

        print(f"✓ Success with: {result.model}")

    except AllProvidersFailedError as e:
        print(f"✗ All providers failed: {e}")
        print("  This is expected if no API keys are configured")

    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_6_retry_behavior():
    """Example 6: Demonstrate retry behavior."""
    print("\n" + "=" * 60)
    print("Example 6: Retry Behavior")
    print("=" * 60)

    strategy = FallbackStrategy()

    print("Fallback strategy will:")
    print("  1. Try primary provider (3 retries with exponential backoff)")
    print("  2. On rate limit: Skip to next provider immediately")
    print("  3. On unavailable: Retry 3x, then try next provider")
    print("  4. On cost limit: Skip provider, try next")
    print("  5. All failed: Raise AllProvidersFailedError")

    result = strategy.execute_with_fallback(prompt="Echo: Testing retry behavior")

    print(f"\n✓ Completed with: {result.model}")


def example_7_smart_routing():
    """Example 7: Smart routing based on task complexity."""
    print("\n" + "=" * 60)
    print("Example 7: Smart Routing")
    print("=" * 60)

    def execute_with_smart_routing(prompt, complexity="medium"):
        """Route to optimal provider based on complexity."""
        strategy = FallbackStrategy()

        if complexity == "high":
            # Complex tasks: Try Claude first (best quality)
            providers = ["claude", "openai", "gemini"]
        elif complexity == "low":
            # Simple tasks: Try Gemini first (cheapest)
            providers = ["gemini", "openai", "claude"]
        else:
            # Medium: Try OpenAI first (balanced)
            providers = ["openai", "claude", "gemini"]

        print(f"Complexity: {complexity}")
        print(f"Provider order: {' → '.join(providers)}")

        return strategy.execute_with_fallback(prompt=prompt, providers=providers)

    # High complexity task
    result1 = execute_with_smart_routing(
        prompt="Design a distributed caching system with Redis and Memcached",
        complexity="high",
    )
    print(f"✓ High complexity → {result1.model}\n")

    # Low complexity task
    result2 = execute_with_smart_routing(prompt="Add a docstring to a function", complexity="low")
    print(f"✓ Low complexity → {result2.model}\n")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Multi-AI Provider Support - Fallback Strategy Examples")
    print("=" * 60)

    try:
        example_1_basic_fallback()
        example_2_custom_fallback_order()
        example_3_cost_aware_fallback()
        example_4_fallback_with_context()
        example_5_error_handling()
        example_6_retry_behavior()
        example_7_smart_routing()

        print("\n" + "=" * 60)
        print("✓ All examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
