"""Embedding utilities for ACE Curator semantic de-duplication.

This module provides OpenAI embedding generation and cosine similarity calculation
for semantic comparison of playbook bullets and delta items.

Cost Estimate: ~$0.18/year for typical usage with text-embedding-ada-002
"""

import os
from typing import Dict, List

import numpy as np


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""


class APIKeyMissingError(EmbeddingError):
    """Raised when OPENAI_API_KEY environment variable is not set."""


class OpenAIError(EmbeddingError):
    """Raised when OpenAI API call fails."""


# Global cache for embeddings (in-memory, cleared on restart)
_embedding_cache: Dict[str, List[float]] = {}


def get_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """Get embedding vector for text using OpenAI API.

    Args:
        text: Text to embed
        model: OpenAI embedding model (default: text-embedding-ada-002)

    Returns:
        Embedding vector as list of floats

    Raises:
        APIKeyMissingError: If OPENAI_API_KEY not set
        OpenAIError: If API call fails

    Example:
        >>> embedding = get_embedding("Always run tests before committing")
        >>> len(embedding)
        1536
    """
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise APIKeyMissingError(_get_setup_instructions())

    # Check cache first
    cache_key = f"{model}:{text}"
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]

    # Import OpenAI here to allow module to be imported without openai installed
    try:
        from openai import OpenAI
    except ImportError:
        raise OpenAIError(
            "OpenAI library not installed. Install with: pip install openai\n\n" "Or with poetry: poetry add openai"
        )

    # Call OpenAI API
    try:
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(input=text, model=model)
        embedding = response.data[0].embedding

        # Cache the result
        _embedding_cache[cache_key] = embedding

        return embedding
    except Exception as e:
        raise OpenAIError(f"OpenAI API call failed: {str(e)}")


def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Compute cosine similarity between two embeddings.

    Cosine similarity formula: dot(a, b) / (norm(a) * norm(b))
    Returns value in range [-1, 1], where:
    - 1.0 = identical
    - 0.0 = orthogonal
    - -1.0 = opposite

    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector

    Returns:
        Cosine similarity score (0.0 to 1.0)

    Example:
        >>> emb1 = get_embedding("Run tests before committing")
        >>> emb2 = get_embedding("Always run pytest before git commit")
        >>> similarity = compute_similarity(emb1, emb2)
        >>> similarity > 0.85  # High similarity
        True
    """
    # Convert to numpy arrays
    a = np.array(embedding1)
    b = np.array(embedding2)

    # Compute cosine similarity
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = dot_product / (norm_a * norm_b)

    # Clamp to [0, 1] range (cosine can be negative, but we only care about positive similarity)
    return max(0.0, float(similarity))


def clear_cache():
    """Clear the in-memory embedding cache.

    Useful for testing or when memory is constrained.
    """
    global _embedding_cache
    _embedding_cache.clear()


def get_cache_size() -> int:
    """Get number of cached embeddings.

    Returns:
        Number of entries in cache
    """
    return len(_embedding_cache)


def get_cache_info() -> Dict[str, int]:
    """Get cache statistics.

    Returns:
        Dictionary with cache size and estimated memory usage
    """
    num_entries = len(_embedding_cache)
    # Each embedding is ~1536 floats * 8 bytes = ~12KB
    estimated_memory_kb = num_entries * 12

    return {
        "num_entries": num_entries,
        "estimated_memory_kb": estimated_memory_kb,
    }


def _get_setup_instructions() -> str:
    """Get setup instructions for missing API key."""
    return """
ERROR: OPENAI_API_KEY not set

To use ACE Curator with OpenAI embeddings:

1. Get API key from: https://platform.openai.com/api-keys

2. Set environment variable:
   export OPENAI_API_KEY="sk-..."

3. Or add to .env file:
   OPENAI_API_KEY=sk-...

Cost: ~$0.18/year for embeddings (text-embedding-ada-002)
- $0.0001 per 1K tokens
- Typical playbook: 150 bullets * 20 words * 1.3 tokens/word = ~3.9K tokens
- Daily curation: $0.0005/day = $0.18/year

Alternative: Use local embeddings (sentence-transformers) - see docs
""".strip()
