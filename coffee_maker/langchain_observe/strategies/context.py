"""Context management strategies for LLM input length handling.

This module provides strategies for checking if input fits within model context limits
and finding alternative models with larger context windows when needed.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import tiktoken

logger = logging.getLogger(__name__)


class ContextLengthError(Exception):
    """Raised when input exceeds all available models' context length."""


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


class LargeContextFallbackStrategy(ContextStrategy):
    """Strategy that finds models with larger context windows when needed.

    This is the default strategy that:
    1. Estimates token count for input
    2. Checks if it fits in current model
    3. If not, finds models with larger context windows
    4. Returns them sorted by size (smallest sufficient first)
    """

    def __init__(
        self,
        model_context_limits: Dict[str, int],
    ):
        """Initialize strategy.

        Args:
            model_context_limits: Dict mapping model names to context limits
        """
        self.model_limits = model_context_limits
        self._tokenizers: Dict[str, Any] = {}

    def check_fits(self, input_data: Any, model_name: str) -> Tuple[bool, int, int]:
        """Check if input fits in model's context window.

        Args:
            input_data: Input data
            model_name: Full model name

        Returns:
            (fits, estimated_tokens, max_context_length)
        """
        # Estimate tokens
        estimated_tokens = self.estimate_tokens(input_data, model_name)

        # Get context limit (use very large number for unknown models)
        max_context = self.model_limits.get(model_name, 10_000_000)

        # Check if fits
        fits = estimated_tokens <= max_context

        if not fits:
            logger.warning(
                f"Input ({estimated_tokens:,} tokens) exceeds {model_name} " f"context limit ({max_context:,} tokens)"
            )

        return fits, estimated_tokens, max_context

    def get_larger_context_models(self, required_tokens: int) -> List[str]:
        """Get models with sufficient context length.

        Args:
            required_tokens: Minimum tokens needed

        Returns:
            List of model names sorted by context size
        """
        # Find all models that can handle required tokens
        suitable_models = [(model, limit) for model, limit in self.model_limits.items() if limit >= required_tokens]

        # Sort by context length (smallest sufficient first)
        suitable_models.sort(key=lambda x: x[1])

        model_names = [model for model, _ in suitable_models]

        logger.info(f"Found {len(model_names)} models for {required_tokens:,} tokens: {model_names}")

        return model_names

    def estimate_tokens(self, input_data: Any, model_name: str) -> int:
        """Estimate token count for input.

        Args:
            input_data: Input to estimate
            model_name: Model name

        Returns:
            Estimated token count
        """
        # Extract text from input
        text = self._extract_text(input_data)

        # Get or create tokenizer
        if model_name not in self._tokenizers:
            self._tokenizers[model_name] = self._get_tokenizer(model_name)

        tokenizer = self._tokenizers[model_name]

        # Use tokenizer if available
        if tokenizer:
            try:
                return len(tokenizer.encode(text))
            except Exception as e:
                logger.debug(f"Error using tokenizer for {model_name}: {e}")

        # Fallback: 1 token ≈ 4 characters
        return len(text) // 4

    def _extract_text(self, input_data: Any) -> str:
        """Extract text from input data.

        Args:
            input_data: Input (dict, str, or other)

        Returns:
            Extracted text
        """
        if isinstance(input_data, dict):
            # LangChain format
            text = input_data.get("input", "")
            if isinstance(text, str):
                return text
            else:
                return str(input_data)
        elif isinstance(input_data, str):
            return input_data
        elif isinstance(input_data, list):
            # List of messages
            return str(input_data)
        else:
            return str(input_data)

    def _get_tokenizer(self, model_name: str) -> Optional[Any]:
        """Get tokenizer for model.

        Args:
            model_name: Full model name

        Returns:
            Tokenizer or None
        """
        try:
            # Extract base model name
            if "/" in model_name:
                _, base_model = model_name.split("/", 1)
            else:
                base_model = model_name

            # Only works for OpenAI models
            if "gpt" in base_model.lower():
                encoding_name = "cl100k_base"  # GPT-4/3.5 encoding
                return tiktoken.get_encoding(encoding_name)

            return None

        except Exception as e:
            logger.debug(f"Could not load tokenizer for {model_name}: {e}")
            return None


class NoContextCheckStrategy(ContextStrategy):
    """Strategy that disables context checking (always returns fits=True)."""

    def check_fits(self, input_data: Any, model_name: str) -> Tuple[bool, int, int]:
        """Always return that input fits.

        Args:
            input_data: Input data (ignored)
            model_name: Model name (ignored)

        Returns:
            (True, 0, 10_000_000) - always fits
        """
        return True, 0, 10_000_000

    def get_larger_context_models(self, required_tokens: int) -> List[str]:
        """Return empty list (no alternatives needed).

        Args:
            required_tokens: Required tokens (ignored)

        Returns:
            Empty list
        """
        return []

    def estimate_tokens(self, input_data: Any, model_name: str) -> int:
        """Return 0 (not checking).

        Args:
            input_data: Input (ignored)
            model_name: Model name (ignored)

        Returns:
            0
        """
        return 0


def create_context_strategy(
    enable_context_check: bool = True,
    model_limits: Optional[Dict[str, int]] = None,
) -> ContextStrategy:
    """Factory function to create context strategy.

    Args:
        enable_context_check: If False, use NoContextCheckStrategy
        model_limits: Dict of model context limits (required if check enabled)

    Returns:
        ContextStrategy instance

    Example:
        >>> from coffee_maker.langchain_observe.llm_config import get_all_model_context_limits
        >>> limits = get_all_model_context_limits()
        >>> strategy = create_context_strategy(
        ...     enable_context_check=True,
        ...     model_limits=limits
        ... )
    """
    if not enable_context_check:
        return NoContextCheckStrategy()

    if model_limits is None:
        # Try to load from llm_config
        try:
            from coffee_maker.langchain_observe.llm_config import get_all_model_context_limits

            model_limits = get_all_model_context_limits()
        except ImportError:
            logger.warning("Could not import get_all_model_context_limits, using empty limits")
            model_limits = {}

    return LargeContextFallbackStrategy(model_context_limits=model_limits)
