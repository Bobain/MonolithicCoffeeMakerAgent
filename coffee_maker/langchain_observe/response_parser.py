"""Utilities for parsing LLM responses."""

from typing import Any, Tuple


def extract_token_usage(response: Any) -> Tuple[int, int]:
    """Extract token usage from LLM response.

    Args:
        response: LLM response object

    Returns:
        Tuple of (input_tokens, output_tokens)
    """
    input_tokens = 0
    output_tokens = 0

    # Try to extract actual usage from response metadata
    if hasattr(response, "response_metadata") and response.response_metadata:
        usage = response.response_metadata.get("usage", {})
        input_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
        output_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
    elif hasattr(response, "usage_metadata") and response.usage_metadata:
        # LangChain format
        input_tokens = getattr(response.usage_metadata, "input_tokens", 0)
        output_tokens = getattr(response.usage_metadata, "output_tokens", 0)

    return input_tokens, output_tokens


def is_rate_limit_error(error: Exception) -> bool:
    """Check if an error is a rate limit error.

    Args:
        error: Exception to check

    Returns:
        True if it's a rate limit error
    """
    error_msg = str(error).lower()
    rate_limit_keywords = [
        "rate limit",
        "ratelimit",
        "429",
        "quota",
        "too many requests",
        "resource_exhausted",
    ]
    return any(keyword in error_msg for keyword in rate_limit_keywords)
