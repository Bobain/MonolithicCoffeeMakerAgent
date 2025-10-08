"""Context management strategies for LLM input length handling.

This module provides strategies for checking if input fits within model context limits
and finding alternative models with larger context windows when needed.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, List, Tuple

logger = logging.getLogger(__name__)


class ContextStrategy(ABC):
    """Abstract base class for context length management strategies.

    A context strategy determines:
    - Whether input fits within a model's context window
    - How many tokens the input requires
    - Which alternative models can handle larger inputs
    """

    @abstractmethod
    def check_fits(self, input_data: Any, model_name: str) -> Tuple[bool, int, int]:
        """Check if input fits within model's context limit.

        Args:
            input_data: Input to check (text, dict, list of messages, etc.)
            model_name: Full model name (e.g., "openai/gpt-4o-mini")

        Returns:
            Tuple of (fits, estimated_tokens, max_context):
            - fits: True if input fits within context limit
            - estimated_tokens: Estimated number of tokens in input
            - max_context: Maximum context tokens for this model
        """

    @abstractmethod
    def get_larger_context_models(self, required_tokens: int) -> List[str]:
        """Get models that can handle the required token count.

        Args:
            required_tokens: Number of tokens needed

        Returns:
            List of model names sorted by context size (smallest suitable first)
        """

    @abstractmethod
    def estimate_tokens(self, input_data: Any, model_name: str) -> int:
        """Estimate number of tokens for input.

        Args:
            input_data: Input to estimate
            model_name: Model name (for model-specific tokenizers)

        Returns:
            Estimated token count
        """
