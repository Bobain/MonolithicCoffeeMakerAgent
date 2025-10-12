#!/usr/bin/env python3
"""Basic usage examples for Multi-AI Provider Support.

This script demonstrates the fundamental ways to use the multi-provider system.

Requirements:
    - At least one provider configured (Claude, OpenAI, or Gemini)
    - API keys set in environment variables
    - coffee-maker installed with ai_providers package

Usage:
    python3 examples/priority_8/basic_usage.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.ai_providers import get_provider, list_enabled_providers, list_available_providers


def example_1_default_provider():
    """Example 1: Use the default provider from config."""
    print("\n" + "=" * 60)
    print("Example 1: Default Provider")
    print("=" * 60)

    provider = get_provider()
    print(f"✓ Using provider: {provider.name}")
    print(f"  Model: {provider.model}")

    # Execute a simple prompt
    result = provider.execute_prompt("Say 'Hello from the multi-provider system!'")

    if result.success:
        print(f"✓ Response: {result.content[:100]}...")
        print(f"  Tokens: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")
        print(f"  Model: {result.model}")
    else:
        print(f"✗ Error: {result.error}")


def example_2_specific_provider():
    """Example 2: Use a specific provider."""
    print("\n" + "=" * 60)
    print("Example 2: Specific Provider (OpenAI)")
    print("=" * 60)

    try:
        # Use OpenAI specifically
        provider = get_provider("openai")
        print(f"✓ Using provider: {provider.name}")

        result = provider.execute_prompt("Write a Python function to reverse a string")

        if result.success:
            print(f"✓ Response:\n{result.content}")
            print(f"  Cost estimate: ${provider.estimate_cost(result.content):.4f}")
        else:
            print(f"✗ Error: {result.error}")

    except Exception as e:
        print(f"✗ Failed to use OpenAI: {e}")
        print("  Make sure OPENAI_API_KEY is set and openai provider is enabled")


def example_3_list_providers():
    """Example 3: List available providers."""
    print("\n" + "=" * 60)
    print("Example 3: List Providers")
    print("=" * 60)

    # List enabled providers from config
    enabled = list_enabled_providers()
    print(f"Enabled providers: {', '.join(enabled)}")

    # List actually available providers (API keys set + reachable)
    print("\nChecking availability...")
    available = list_available_providers(check_connectivity=False)
    print(f"Available providers: {', '.join(available)}")

    if not available:
        print("⚠️  No providers available. Check API keys and config.")


def example_4_compare_providers():
    """Example 4: Compare responses from different providers."""
    print("\n" + "=" * 60)
    print("Example 4: Compare Providers")
    print("=" * 60)

    prompt = "Explain what a binary search tree is in one sentence."

    available = list_available_providers()

    for provider_name in available:
        print(f"\n--- {provider_name.upper()} ---")

        provider = get_provider(provider_name)
        result = provider.execute_prompt(prompt)

        if result.success:
            print(f"Response: {result.content}")
            print(f"Tokens: {result.usage['input_tokens']} in, {result.usage['output_tokens']} out")
        else:
            print(f"Error: {result.error}")


def example_5_cost_estimation():
    """Example 5: Estimate costs before execution."""
    print("\n" + "=" * 60)
    print("Example 5: Cost Estimation")
    print("=" * 60)

    prompt = "Implement a REST API with authentication, CRUD operations, and database integration."

    available = list_available_providers()

    print(f"Task: {prompt[:60]}...")
    print("\nCost estimates:")

    for provider_name in available:
        provider = get_provider(provider_name)
        estimated_cost = provider.estimate_cost(
            prompt=prompt,
            system_prompt="You are an expert software developer.",
            max_output_tokens=2000,
        )

        print(f"  {provider_name:10s}: ${estimated_cost:.4f}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Multi-AI Provider Support - Basic Usage Examples")
    print("=" * 60)

    try:
        example_1_default_provider()
        example_2_specific_provider()
        example_3_list_providers()
        example_4_compare_providers()
        example_5_cost_estimation()

        print("\n" + "=" * 60)
        print("✓ All examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
