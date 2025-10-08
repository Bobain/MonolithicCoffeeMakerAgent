"""AutoPickerLLM Refactored: Simplified orchestrator with fallback logic only.

This is a SIMPLIFIED version of AutoPickerLLM that delegates:
- Rate limiting → ScheduledLLM
- Retry logic → ScheduledLLM's SchedulingStrategy
- Scheduling → ScheduledLLM
- Fallback selection → FallbackStrategy (NEW!)

AutoPickerLLM now ONLY handles:
- Fallback orchestration (primary → fallback1 → fallback2 → ...)
- Cost tracking
- Context length checking
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import tiktoken
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import Generation, LLMResult

from coffee_maker.langchain_observe.strategies.fallback import FallbackStrategy, SequentialFallback

logger = logging.getLogger(__name__)


class ContextLengthError(Exception):
    """Raised when input exceeds model's context length."""


class AutoPickerLLMRefactored(BaseLLM):
    """Simplified LLM orchestrator with fallback capabilities.

    This orchestrator:
    - Manages fallback logic (primary → fallback1 → fallback2 → ...)
    - Tracks costs via CostCalculator
    - Checks context lengths

    Scheduling, rate limiting, and retries are delegated to ScheduledLLM.

    Example:
        >>> from coffee_maker.langchain_observe.llm import get_scheduled_llm
        >>>
        >>> primary = get_scheduled_llm(provider="openai", model="gpt-4o-mini", tier="tier1")
        >>> fallback = get_scheduled_llm(provider="gemini", model="gemini-2.5-flash", tier="tier1")
        >>>
        >>> auto_picker = AutoPickerLLMRefactored(
        ...     primary_llm=primary,
        ...     primary_model_name="openai/gpt-4o-mini",
        ...     fallback_llms=[(fallback, "gemini/gemini-2.5-flash")],
        ... )
        >>> response = auto_picker.invoke({"input": "Review this code..."})
    """

    # Pydantic model fields
    primary_llm: Any  # Should be ScheduledLLM
    primary_model_name: str
    fallback_llms: List[Tuple[Any, str]]  # List of (ScheduledLLM, model_name)
    fallback_strategy: FallbackStrategy  # Strategy for selecting fallbacks
    cost_calculator: Optional[Any] = None  # CostCalculator instance
    langfuse_client: Optional[Any] = None  # Langfuse client for logging
    enable_context_fallback: bool = True  # Enable automatic context length fallback
    stats: Dict[str, int] = {}
    _tokenizer: Optional[Any] = None
    _large_context_models: Optional[List[Tuple[Any, str, int]]] = None  # Lazy-loaded

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    def __init__(
        self,
        primary_llm: Any,
        primary_model_name: str,
        fallback_llms: List[Tuple[Any, str]],
        fallback_strategy: Optional[FallbackStrategy] = None,
        cost_calculator: Optional[Any] = None,
        langfuse_client: Optional[Any] = None,
        enable_context_fallback: bool = True,
        **kwargs,
    ):
        """Initialize AutoPickerLLMRefactored.

        Args:
            primary_llm: Primary LLM (should be ScheduledLLM)
            primary_model_name: Full name of primary model (e.g., "openai/gpt-4o-mini")
            fallback_llms: List of (llm_instance, model_name) tuples for fallback
            fallback_strategy: Strategy for selecting fallbacks (default: SequentialFallback)
            cost_calculator: Optional CostCalculator for tracking costs
            langfuse_client: Optional Langfuse client for logging costs
            enable_context_fallback: If True, automatically fallback to larger-context models
        """
        # Initialize statistics
        stats = {
            "total_requests": 0,
            "primary_requests": 0,
            "fallback_requests": 0,
            "rate_limit_fallbacks": 0,
            "context_fallbacks": 0,
        }

        # Get tokenizer for the primary model
        tokenizer = self._get_tokenizer_static(primary_model_name)

        # Use default fallback strategy if none provided
        if fallback_strategy is None:
            fallback_strategy = SequentialFallback()

        # Call parent init
        super().__init__(
            primary_llm=primary_llm,
            primary_model_name=primary_model_name,
            fallback_llms=fallback_llms,
            fallback_strategy=fallback_strategy,
            cost_calculator=cost_calculator,
            langfuse_client=langfuse_client,
            enable_context_fallback=enable_context_fallback,
            stats=stats,
            _tokenizer=tokenizer,
            _large_context_models=None,
            **kwargs,
        )

    def invoke(self, input_data: dict, **kwargs) -> Any:
        """Invoke the LLM with fallback orchestration.

        Args:
            input_data: Input dictionary for the LLM
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            LLM response

        Raises:
            Exception: If all models fail
        """
        self.stats["total_requests"] += 1

        # Try primary model first
        primary_error = None
        result = self._try_invoke_model_with_error(
            self.primary_llm, self.primary_model_name, input_data, is_primary=True, **kwargs
        )

        if result["success"]:
            return result["response"]

        primary_error = result["error"]

        # Try fallback models using strategy
        logger.info(f"Primary model {self.primary_model_name} failed, trying fallbacks")

        # Build available fallbacks list
        available_fallback_names = [name for _, name in self.fallback_llms]
        fallback_dict = {name: llm for llm, name in self.fallback_llms}

        # Estimate tokens for smart fallback (if needed)
        estimated_tokens = self._estimate_tokens(input_data, self.primary_model_name)
        metadata = {"estimated_tokens": estimated_tokens}

        while available_fallback_names:
            # Use strategy to select next fallback
            next_fallback_name = self.fallback_strategy.select_next_fallback(
                failed_model_name=self.primary_model_name if primary_error else "previous_fallback",
                available_fallbacks=available_fallback_names,
                error=primary_error if primary_error else Exception("Unknown error"),
                metadata=metadata,
            )

            if next_fallback_name is None:
                break

            # Remove selected fallback from available list
            available_fallback_names.remove(next_fallback_name)
            fallback_llm = fallback_dict[next_fallback_name]

            logger.info(f"Attempting fallback to {next_fallback_name}")
            result = self._try_invoke_model_with_error(
                fallback_llm, next_fallback_name, input_data, is_primary=False, **kwargs
            )

            if result["success"]:
                # Log fallback to Langfuse
                if self.langfuse_client:
                    try:
                        self.langfuse_client.event(
                            name="fallback_success",
                            metadata={
                                "original_model": self.primary_model_name,
                                "fallback_model": next_fallback_name,
                                "reason": str(primary_error) if primary_error else "unknown",
                            },
                        )
                    except Exception as e:
                        logger.warning(f"Failed to log fallback to Langfuse: {e}")

                return result["response"]

        # All models failed
        raise RuntimeError(
            f"All LLM models failed. "
            f"Primary: {self.primary_model_name}, "
            f"Fallbacks: {[name for _, name in self.fallback_llms]}"
        )

    def _try_invoke_model_with_error(
        self, llm: Any, model_name: str, input_data: dict, is_primary: bool, **kwargs
    ) -> Dict[str, Any]:
        """Try to invoke a model and return success/error info.

        Args:
            llm: LLM instance
            model_name: Model name
            input_data: Input data
            is_primary: Whether this is primary model
            **kwargs: Additional args

        Returns:
            Dict with {"success": bool, "response": Any, "error": Optional[Exception]}
        """
        try:
            response = self._try_invoke_model(llm, model_name, input_data, is_primary, **kwargs)
            if response is None:
                return {"success": False, "response": None, "error": Exception("Model returned None")}
            return {"success": True, "response": response, "error": None}
        except Exception as e:
            return {"success": False, "response": None, "error": e}

    def _try_invoke_model(
        self, llm: Any, model_name: str, input_data: dict, is_primary: bool, **kwargs
    ) -> Optional[Any]:
        """Try to invoke a specific model, handling context length.

        Args:
            llm: LLM instance (should be ScheduledLLM)
            model_name: Full model name
            input_data: Input data
            is_primary: Whether this is the primary model
            **kwargs: Additional arguments

        Returns:
            LLM response if successful, None if failed

        Raises:
            ValueError: If input is too large for any available model
        """
        # Check context length FIRST (before invoking)
        if self.enable_context_fallback:
            fits, estimated_tokens, max_context = self._check_context_length(input_data, model_name)

            if not fits:
                logger.info(
                    f"Input too large for {model_name} "
                    f"({estimated_tokens:,} > {max_context:,} tokens), "
                    f"searching for larger-context model"
                )

                # Try to find suitable large-context model
                large_models = self._get_large_context_models(estimated_tokens)

                if large_models:
                    # Try each large-context model
                    for large_llm, large_model_name in large_models:
                        logger.info(f"Trying large-context fallback: {large_model_name}")

                        # Recursively try the large-context model
                        result = self._try_invoke_model(
                            large_llm, large_model_name, input_data, is_primary=False, **kwargs
                        )

                        if result is not None:
                            self.stats["context_fallbacks"] += 1

                            # Log context fallback to Langfuse
                            if self.langfuse_client:
                                try:
                                    from coffee_maker.langchain_observe.llm_config import (
                                        get_model_context_length_from_name,
                                    )

                                    self.langfuse_client.event(
                                        name="context_length_fallback",
                                        metadata={
                                            "original_model": model_name,
                                            "fallback_model": large_model_name,
                                            "estimated_tokens": estimated_tokens,
                                            "original_max_context": max_context,
                                            "fallback_max_context": get_model_context_length_from_name(
                                                large_model_name
                                            ),
                                        },
                                    )
                                except Exception as e:
                                    logger.warning(f"Failed to log context fallback to Langfuse: {e}")

                            return result

                # No suitable model found - raise error
                max_available = (
                    max((context for _, _, context in self._large_context_models), default=max_context)
                    if self._large_context_models
                    else max_context
                )

                raise ValueError(
                    f"Input is too large ({estimated_tokens:,} tokens) for any available model. "
                    f"Maximum supported context: {max_available:,} tokens. "
                    f"Original model: {model_name} (limit: {max_context:,} tokens). "
                    f"Please reduce input size."
                )

        # Invoke the LLM (scheduling/retry handled by ScheduledLLM)
        try:
            logger.debug(f"Invoking {model_name}")
            start_time = time.time()

            response = llm.invoke(input_data, **kwargs)
            latency = time.time() - start_time

            # Extract token counts from response
            input_tokens, output_tokens = self._extract_token_usage(response)

            # Calculate and log cost if cost_calculator is available
            if self.cost_calculator and input_tokens > 0:
                cost_info = self.cost_calculator.calculate_cost(model_name, input_tokens, output_tokens)
                logger.info(
                    f"{model_name} cost: ${cost_info['total_cost']:.4f} "
                    f"({input_tokens} in + {output_tokens} out tokens)"
                )

                # Log to Langfuse if client is available
                if self.langfuse_client:
                    try:
                        self.langfuse_client.generation(
                            name=f"llm_call_{model_name.replace('/', '_')}",
                            model=model_name,
                            usage={
                                "input": input_tokens,
                                "output": output_tokens,
                                "total": input_tokens + output_tokens,
                            },
                            metadata={
                                "cost_usd": cost_info["total_cost"],
                                "input_cost_usd": cost_info["input_cost"],
                                "output_cost_usd": cost_info["output_cost"],
                                "is_primary": is_primary,
                                "latency_seconds": latency,
                            },
                        )
                        logger.debug(f"Logged cost to Langfuse: ${cost_info['total_cost']:.4f}")
                    except Exception as e:
                        logger.warning(f"Failed to log cost to Langfuse: {e}")

            # Update stats
            if is_primary:
                self.stats["primary_requests"] += 1
            else:
                self.stats["fallback_requests"] += 1

            logger.info(f"Successfully invoked {model_name} in {latency:.2f}s")
            return response

        except Exception as e:
            # ScheduledLLM already handled retries, so any error means this model exhausted
            logger.error(f"Model {model_name} failed after all retries: {e}")

            # Check if this is a rate limit error for stats
            if self._is_rate_limit_error(e):
                self.stats["rate_limit_fallbacks"] += 1

            # Return None to try next fallback
            return None

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error.

        Args:
            error: The exception to check

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

    def _extract_token_usage(self, response: Any) -> Tuple[int, int]:
        """Extract token usage from response.

        Args:
            response: LLM response

        Returns:
            (input_tokens, output_tokens)
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

    def _check_context_length(self, input_data: dict, model_name: str) -> Tuple[bool, int, int]:
        """Check if input fits within model's context window.

        Args:
            input_data: Input dictionary
            model_name: Full model name (e.g., "openai/gpt-4o-mini")

        Returns:
            (fits, estimated_tokens, max_context_length)
        """
        from coffee_maker.langchain_observe.llm_config import get_model_context_length_from_name

        estimated_tokens = self._estimate_tokens(input_data, model_name)
        max_context = get_model_context_length_from_name(model_name)

        fits = estimated_tokens <= max_context

        if not fits:
            logger.warning(
                f"Input ({estimated_tokens:,} tokens) exceeds {model_name} " f"context limit ({max_context:,} tokens)"
            )

        return fits, estimated_tokens, max_context

    def _initialize_large_context_models(self):
        """Initialize list of large-context models sorted by preference."""
        from coffee_maker.langchain_observe.llm import get_scheduled_llm
        from coffee_maker.langchain_observe.llm_config import get_large_context_models

        # Get models sorted by context length (largest first)
        large_models = get_large_context_models()

        self._large_context_models = []

        # We need to know which tier we're using - extract from primary LLM
        # For now, we'll skip models not available (will be improved in context strategy)
        for provider, model, context_length in large_models:
            full_name = f"{provider}/{model}"

            try:
                # Create scheduled LLM instance
                llm_instance = get_scheduled_llm(provider=provider, model=model)
                self._large_context_models.append((llm_instance, full_name, context_length))
                logger.debug(f"Added large-context model: {full_name} ({context_length:,} tokens)")
            except Exception as e:
                logger.debug(f"Could not initialize {full_name}: {e}")

        logger.info(f"Initialized {len(self._large_context_models)} large-context models")

    def _get_large_context_models(self, required_tokens: int) -> List[Tuple[Any, str]]:
        """Get models with sufficient context length.

        Args:
            required_tokens: Minimum context length needed

        Returns:
            List of (llm_instance, model_name) tuples
        """
        # Lazy-load large context models
        if self._large_context_models is None:
            self._initialize_large_context_models()

        # Filter models that can handle the input
        suitable_models = [
            (llm, name) for llm, name, context_len in self._large_context_models if context_len >= required_tokens
        ]

        return suitable_models

    def _estimate_tokens(self, input_data: dict, model_name: str) -> int:
        """Estimate number of tokens in input.

        Args:
            input_data: Input dictionary
            model_name: Model name for token counting

        Returns:
            Estimated token count
        """
        # Convert input to string
        if isinstance(input_data, dict):
            # Common patterns for LangChain inputs
            text = input_data.get("input", "")
            if isinstance(text, str):
                input_text = text
            else:
                input_text = str(input_data)
        else:
            input_text = str(input_data)

        # Use tokenizer if available
        if self._tokenizer:
            try:
                tokens = len(self._tokenizer.encode(input_text))
                return tokens
            except Exception as e:
                logger.debug(f"Error using tokenizer: {e}")

        # Fallback: rough estimation (1 token ≈ 4 characters)
        estimated = len(input_text) // 4
        logger.debug(f"Using character-based token estimation: {estimated} tokens")
        return estimated

    @staticmethod
    def _get_tokenizer_static(model_name: str):
        """Get appropriate tokenizer for a model.

        Args:
            model_name: Full model name (e.g., "openai/gpt-4o-mini")

        Returns:
            Tokenizer instance or None
        """
        try:
            # Extract base model name
            if "/" in model_name:
                _, base_model = model_name.split("/", 1)
            else:
                base_model = model_name

            # Get tokenizer for OpenAI models
            if "gpt" in base_model.lower():
                encoding_name = "cl100k_base"  # Default for GPT-4/3.5
                return tiktoken.get_encoding(encoding_name)

            # For non-OpenAI models, return None
            return None

        except Exception as e:
            logger.debug(f"Could not load tokenizer for {model_name}: {e}")
            return None

    def get_stats(self) -> Dict:
        """Get usage statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            **self.stats,
            "primary_usage_percent": (
                (self.stats["primary_requests"] / self.stats["total_requests"] * 100)
                if self.stats["total_requests"] > 0
                else 0
            ),
            "fallback_usage_percent": (
                (self.stats["fallback_requests"] / self.stats["total_requests"] * 100)
                if self.stats["total_requests"] > 0
                else 0
            ),
        }

    def bind(self, **kwargs):
        """Bind arguments to the primary LLM.

        Args:
            **kwargs: Arguments to bind

        Returns:
            Self (for chaining)
        """
        # Bind to primary LLM
        if hasattr(self.primary_llm, "bind"):
            self.primary_llm = self.primary_llm.bind(**kwargs)

        # Also bind to fallback LLMs
        bound_fallbacks = []
        for fallback_llm, model_name in self.fallback_llms:
            if hasattr(fallback_llm, "bind"):
                bound_fallback = fallback_llm.bind(**kwargs)
                bound_fallbacks.append((bound_fallback, model_name))
            else:
                bound_fallbacks.append((fallback_llm, model_name))

        self.fallback_llms = bound_fallbacks
        return self

    @property
    def _llm_type(self) -> str:
        """Return type of language model."""
        return "auto_picker_llm_refactored"

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate responses for a list of prompts.

        Args:
            prompts: List of prompts to generate from
            stop: Stop sequences
            run_manager: Callback manager
            **kwargs: Additional arguments

        Returns:
            LLMResult with generations
        """
        generations = []
        for prompt in prompts:
            # Use invoke for each prompt
            response = self.invoke({"input": prompt}, **kwargs)

            # Convert response to Generation
            if hasattr(response, "content"):
                text = response.content
            else:
                text = str(response)

            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)


def create_auto_picker_llm_refactored(
    primary_provider: str,
    primary_model: str,
    fallback_configs: List[Tuple[str, str]],
    tier: str = "tier1",
    cost_calculator: Optional[Any] = None,
    langfuse_client: Optional[Any] = None,
    enable_context_fallback: bool = True,
    max_wait_seconds: float = 300.0,
) -> AutoPickerLLMRefactored:
    """Helper function to create AutoPickerLLMRefactored with scheduled LLMs.

    This is a convenience function that creates all the ScheduledLLM instances
    and wires them together with AutoPickerLLMRefactored.

    Args:
        primary_provider: Primary LLM provider (openai, gemini, anthropic)
        primary_model: Primary model name
        fallback_configs: List of (provider, model) tuples for fallbacks
        tier: API tier for rate limiting (default: tier1)
        cost_calculator: Optional CostCalculator for cost tracking
        langfuse_client: Optional Langfuse client for logging
        enable_context_fallback: Enable automatic context length fallback
        max_wait_seconds: Maximum wait time for rate limits

    Returns:
        Configured AutoPickerLLMRefactored instance

    Example:
        >>> from coffee_maker.langchain_observe.cost_calculator import CostCalculator
        >>> import langfuse
        >>>
        >>> cost_calc = CostCalculator()
        >>> langfuse_client = langfuse.get_client()
        >>>
        >>> auto_picker = create_auto_picker_llm_refactored(
        ...     primary_provider="openai",
        ...     primary_model="gpt-4o-mini",
        ...     fallback_configs=[
        ...         ("gemini", "gemini-2.5-flash"),
        ...         ("anthropic", "claude-3-5-haiku-20241022"),
        ...     ],
        ...     tier="tier1",
        ...     cost_calculator=cost_calc,
        ...     langfuse_client=langfuse_client,
        ... )
        >>> response = auto_picker.invoke({"input": "Hello"})
    """
    from coffee_maker.langchain_observe.llm import get_scheduled_llm

    # Create primary scheduled LLM
    primary_llm = get_scheduled_llm(
        langfuse_client=langfuse_client,
        provider=primary_provider,
        model=primary_model,
        tier=tier,
        max_wait_seconds=max_wait_seconds,
    )
    primary_model_name = f"{primary_provider}/{primary_model}"

    # Create fallback scheduled LLMs
    fallback_llms = []
    for fb_provider, fb_model in fallback_configs:
        fb_llm = get_scheduled_llm(
            langfuse_client=langfuse_client,
            provider=fb_provider,
            model=fb_model,
            tier=tier,
            max_wait_seconds=max_wait_seconds,
        )
        fb_model_name = f"{fb_provider}/{fb_model}"
        fallback_llms.append((fb_llm, fb_model_name))

    # Create AutoPickerLLMRefactored
    return AutoPickerLLMRefactored(
        primary_llm=primary_llm,
        primary_model_name=primary_model_name,
        fallback_llms=fallback_llms,
        cost_calculator=cost_calculator,
        langfuse_client=langfuse_client,
        enable_context_fallback=enable_context_fallback,
    )
