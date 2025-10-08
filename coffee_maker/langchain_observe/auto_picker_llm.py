"""AutoPickerLLM: Intelligent LLM wrapper with rate limiting and automatic fallback.

This module provides an intelligent wrapper around LLM instances that:
- Tracks rate limits and prevents API limit errors
- Automatically falls back to alternative models when limits are reached
- Estimates token usage to make informed decisions
- Provides detailed logging and monitoring
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import tiktoken
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import Generation, LLMResult

from coffee_maker.langchain_observe.rate_limiter import RateLimitTracker

logger = logging.getLogger(__name__)


class AutoPickerLLM(BaseLLM):
    """Intelligent LLM wrapper with rate limiting and fallback capabilities.

    This class wraps one or more LLM instances and provides:
    - Automatic rate limit checking before requests
    - Fallback to alternative models when primary is rate-limited
    - Token estimation for better rate limit predictions
    - Wait time calculation and optional automatic waiting

    Example:
        >>> primary = get_llm(provider="openai", model="gpt-4o-mini")
        >>> fallback = get_llm(provider="gemini", model="gemini-2.5-flash-lite")
        >>> auto_llm = AutoPickerLLM(
        ...     primary_llm=primary,
        ...     primary_model_name="openai/gpt-4o-mini",
        ...     fallback_llms=[(fallback, "gemini/gemini-2.5-flash-lite")],
        ...     rate_tracker=rate_tracker
        ... )
        >>> response = auto_llm.invoke({"input": "Review this code..."})
    """

    # Pydantic model fields
    primary_llm: Any
    primary_model_name: str
    fallback_llms: List[Tuple[Any, str]]
    rate_tracker: RateLimitTracker
    auto_wait: bool = True
    max_wait_seconds: float = 300.0  # Max wait for rate limits (5 minutes default)
    max_retries: int = 3  # Max retry attempts with exponential backoff
    backoff_base: float = 2.0  # Exponential backoff multiplier
    min_wait_before_fallback: float = 90.0  # Min seconds to wait before allowing fallback
    stats: Dict[str, int] = {}
    _tokenizer: Optional[Any] = None
    cost_calculator: Optional[Any] = None  # CostCalculator instance
    langfuse_client: Optional[Any] = None  # Langfuse client for cost tracking
    enable_context_fallback: bool = True  # Enable automatic context length fallback
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
        rate_tracker: RateLimitTracker,
        auto_wait: bool = True,
        max_wait_seconds: float = 300.0,
        max_retries: int = 3,
        backoff_base: float = 2.0,
        min_wait_before_fallback: float = 90.0,
        cost_calculator: Optional[Any] = None,
        langfuse_client: Optional[Any] = None,
        enable_context_fallback: bool = True,
        **kwargs,
    ):
        """Initialize AutoPickerLLM wrapper.

        Args:
            primary_llm: Primary LLM instance to use
            primary_model_name: Full name of primary model (e.g., "openai/gpt-4o-mini")
            fallback_llms: List of (llm_instance, model_name) tuples for fallback
            rate_tracker: RateLimitTracker instance for tracking usage
            auto_wait: If True, automatically wait when rate limited
            max_wait_seconds: Maximum seconds to wait for rate limits (default 300s = 5min)
            max_retries: Maximum retry attempts with exponential backoff (default 3)
            backoff_base: Exponential backoff multiplier (default 2.0)
            min_wait_before_fallback: Minimum seconds to wait from last call before fallback (default 90s)
            cost_calculator: Optional CostCalculator for tracking costs
            langfuse_client: Optional Langfuse client for logging costs
            enable_context_fallback: If True, automatically fallback to larger-context models
        """
        # Initialize statistics
        stats = {
            "total_requests": 0,
            "primary_requests": 0,
            "fallback_requests": 0,
            "rate_limit_waits": 0,
            "rate_limit_fallbacks": 0,
        }

        # Get tokenizer for the primary model
        tokenizer = self._get_tokenizer_static(primary_model_name)

        # Call parent init with all fields
        super().__init__(
            primary_llm=primary_llm,
            primary_model_name=primary_model_name,
            fallback_llms=fallback_llms,
            rate_tracker=rate_tracker,
            auto_wait=auto_wait,
            max_wait_seconds=max_wait_seconds,
            max_retries=max_retries,
            backoff_base=backoff_base,
            min_wait_before_fallback=min_wait_before_fallback,
            stats=stats,
            _tokenizer=tokenizer,
            cost_calculator=cost_calculator,
            langfuse_client=langfuse_client,
            enable_context_fallback=enable_context_fallback,
            _large_context_models=None,  # Lazy-loaded
            **kwargs,
        )

    def invoke(self, input_data: dict, **kwargs) -> Any:
        """Invoke the LLM with rate limiting and fallback.

        Args:
            input_data: Input dictionary for the LLM
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            LLM response

        Raises:
            Exception: If all models fail or are rate-limited
        """
        self.stats["total_requests"] += 1

        # Try primary model first
        result = self._try_invoke_model(
            self.primary_llm, self.primary_model_name, input_data, is_primary=True, **kwargs
        )

        if result is not None:
            return result

        # Try fallback models
        logger.info(f"Primary model {self.primary_model_name} unavailable, trying fallbacks")
        for fallback_llm, fallback_model_name in self.fallback_llms:
            logger.info(f"Attempting fallback to {fallback_model_name}")
            result = self._try_invoke_model(fallback_llm, fallback_model_name, input_data, is_primary=False, **kwargs)

            if result is not None:
                # Log rate limit fallback to Langfuse
                if self.langfuse_client:
                    try:
                        self.langfuse_client.event(
                            name="rate_limit_fallback",
                            metadata={
                                "original_model": self.primary_model_name,
                                "fallback_model": fallback_model_name,
                                "reason": "rate_limit_or_error",
                            },
                        )
                    except Exception as e:
                        logger.warning(f"Failed to log rate limit fallback to Langfuse: {e}")

                return result

        # All models failed
        raise RuntimeError(
            f"All LLM models failed or are rate-limited. "
            f"Primary: {self.primary_model_name}, "
            f"Fallbacks: {[name for _, name in self.fallback_llms]}"
        )

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
        from coffee_maker.langchain_observe.agents import get_llm
        from coffee_maker.langchain_observe.llm_config import get_large_context_models

        # Get models sorted by context length (largest first)
        large_models = get_large_context_models()

        self._large_context_models = []

        for provider, model, context_length in large_models:
            full_name = f"{provider}/{model}"

            # Skip if not in current rate tracker (not available in tier)
            if full_name not in self.rate_tracker.model_limits:
                logger.debug(f"Skipping {full_name} - not in current tier")
                continue

            try:
                # Create LLM instance
                llm_instance = get_llm(provider=provider, model=model)
                self._large_context_models.append((llm_instance, full_name, context_length))
                logger.debug(f"Added large-context model: {full_name} ({context_length:,} tokens)")
            except Exception as e:
                logger.warning(f"Could not initialize {full_name}: {e}")

        logger.info(f"Initialized {len(self._large_context_models)} large-context models")

    def _get_large_context_models(self, required_tokens: int) -> List[Tuple[Any, str]]:
        """Get models with sufficient context length, sorted by preference.

        Returns models that:
        1. Can handle required_tokens
        2. Are available in current tier
        3. Sorted by: context length, then cost

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

    def _try_invoke_model(
        self, llm: Any, model_name: str, input_data: dict, is_primary: bool, **kwargs
    ) -> Optional[Any]:
        """Try to invoke a specific model, handling context length and rate limits.

        Args:
            llm: LLM instance
            model_name: Full model name
            input_data: Input data
            is_primary: Whether this is the primary model
            **kwargs: Additional arguments

        Returns:
            LLM response if successful, None if rate-limited or context exceeded

        Raises:
            ValueError: If input is too large for any available model
        """
        # NEW: Check context length FIRST (before rate limiting)
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

        # Estimate tokens in input (if not already done by context check)
        if self.enable_context_fallback:
            # Already estimated in context check
            pass
        else:
            estimated_tokens = self._estimate_tokens(input_data, model_name)

        # NEW: Retry with exponential backoff for rate limits
        retry_count = 0
        while retry_count <= self.max_retries:
            # Check if we can make the request
            if not self.rate_tracker.can_make_request(model_name, estimated_tokens):
                wait_time = self.rate_tracker.get_wait_time(model_name, estimated_tokens)

                if not self.auto_wait:
                    # Auto-wait disabled, but still check minimum wait before fallback
                    last_call_time = self.rate_tracker.get_last_call_time()
                    if last_call_time is not None:
                        time_since_last_call = time.time() - last_call_time
                        if time_since_last_call < self.min_wait_before_fallback:
                            remaining_wait = self.min_wait_before_fallback - time_since_last_call
                            logger.info(
                                f"Rate limit reached for {model_name}, auto-wait disabled, "
                                f"but only {time_since_last_call:.1f}s since last call. "
                                f"Waiting additional {remaining_wait:.1f}s before fallback (min: {self.min_wait_before_fallback}s)."
                            )
                            time.sleep(remaining_wait)
                            self.stats["rate_limit_waits"] += 1

                    logger.info(f"Rate limit reached for {model_name}, using fallback")
                    self.stats["rate_limit_fallbacks"] += 1
                    return None

                # Calculate backoff time (exponential for retries after first attempt)
                if retry_count > 0:
                    # Exponential backoff: wait_time * backoff_base^(retry_count-1)
                    # First retry: base * 2^0 = base
                    # Second retry: base * 2^1 = base * 2
                    # Third retry: base * 2^2 = base * 4
                    backoff_time = wait_time * (self.backoff_base ** (retry_count - 1))
                    logger.info(
                        f"Rate limit retry {retry_count}/{self.max_retries} for {model_name}. "
                        f"Waiting {backoff_time:.1f}s (base: {wait_time:.1f}s, multiplier: {self.backoff_base}^{retry_count-1})"
                    )
                else:
                    # First attempt: just wait the calculated time
                    backoff_time = wait_time
                    logger.info(f"Rate limit reached for {model_name}. Waiting {backoff_time:.1f}s")

                # Check if wait time is acceptable
                if backoff_time > self.max_wait_seconds:
                    # Check if minimum time since last call has passed (and not already done final attempt)
                    last_call_time = self.rate_tracker.get_last_call_time()
                    if last_call_time is not None and retry_count <= self.max_retries:
                        time_since_last_call = time.time() - last_call_time
                        if time_since_last_call < self.min_wait_before_fallback:
                            remaining_wait = self.min_wait_before_fallback - time_since_last_call
                            logger.info(
                                f"Wait time {backoff_time:.1f}s exceeds max {self.max_wait_seconds}s, "
                                f"but only {time_since_last_call:.1f}s since last call. "
                                f"Waiting additional {remaining_wait:.1f}s, then making ONE FINAL ATTEMPT."
                            )
                            time.sleep(remaining_wait)
                            self.stats["rate_limit_waits"] += 1

                            # Make ONE FINAL ATTEMPT after ensuring 90s wait
                            logger.info(
                                f"Making final attempt for {model_name} after {self.min_wait_before_fallback}s wait"
                            )
                            # Recursively call this method ONE MORE TIME (will fallback if fails)
                            # Remove retry_count from kwargs if present to avoid conflict
                            kwargs_copy = {k: v for k, v in kwargs.items() if k != "retry_count"}
                            return self._try_invoke_model(
                                llm, model_name, input_data, is_primary, retry_count=self.max_retries + 1, **kwargs_copy
                            )

                    logger.warning(
                        f"Wait time {backoff_time:.1f}s exceeds max {self.max_wait_seconds}s. "
                        f"Tried {retry_count} retries. Using fallback."
                    )
                    self.stats["rate_limit_fallbacks"] += 1
                    return None

                # Wait and retry
                time.sleep(backoff_time)
                self.stats["rate_limit_waits"] += 1
                retry_count += 1
                continue  # Retry the rate limit check

            # Rate limit OK, break out of retry loop
            break

        # If we exhausted all retries
        if retry_count > self.max_retries:
            # Check if minimum time since last call has passed
            last_call_time = self.rate_tracker.get_last_call_time()
            if last_call_time is not None:
                time_since_last_call = time.time() - last_call_time
                if time_since_last_call < self.min_wait_before_fallback:
                    remaining_wait = self.min_wait_before_fallback - time_since_last_call
                    logger.info(
                        f"Exhausted {self.max_retries} retries, but only {time_since_last_call:.1f}s since last call. "
                        f"Waiting additional {remaining_wait:.1f}s, then making ONE FINAL ATTEMPT."
                    )
                    time.sleep(remaining_wait)
                    self.stats["rate_limit_waits"] += 1

                    # Make ONE FINAL ATTEMPT after ensuring 90s wait
                    logger.info(f"Making final attempt for {model_name} after {self.min_wait_before_fallback}s wait")
                    # Recursively call this method ONE MORE TIME (will fallback if fails)
                    kwargs_copy = {k: v for k, v in kwargs.items() if k != "retry_count"}
                    return self._try_invoke_model(
                        llm, model_name, input_data, is_primary, retry_count=self.max_retries + 2, **kwargs_copy
                    )

            logger.error(f"Exhausted {self.max_retries} retries for {model_name}. Using fallback.")
            self.stats["rate_limit_fallbacks"] += 1
            return None

        # Make the request
        try:
            logger.debug(f"Invoking {model_name} with ~{estimated_tokens} tokens")
            start_time = time.time()

            # Update last call timestamp BEFORE making the call
            # (ensures 90s wait applies to any attempt, successful or not)
            # This is global across all LLM instances via the shared rate_tracker
            self.rate_tracker.set_last_call_time(time.time())

            response = llm.invoke(input_data, **kwargs)
            latency = time.time() - start_time

            # Extract actual token counts from response if available
            input_tokens = estimated_tokens
            output_tokens = 0

            # Try to extract actual usage from response metadata
            if hasattr(response, "response_metadata") and response.response_metadata:
                usage = response.response_metadata.get("usage", {})
                input_tokens = usage.get("prompt_tokens", usage.get("input_tokens", estimated_tokens))
                output_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
            elif hasattr(response, "usage_metadata") and response.usage_metadata:
                # LangChain format
                input_tokens = getattr(response.usage_metadata, "input_tokens", estimated_tokens)
                output_tokens = getattr(response.usage_metadata, "output_tokens", 0)

            # If we got actual token counts, use them for rate limiting
            total_tokens = input_tokens + output_tokens if output_tokens > 0 else estimated_tokens
            self.rate_tracker.record_request(model_name, total_tokens)

            # Calculate and log cost if cost_calculator is available
            if self.cost_calculator:
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
            error_msg = str(e).lower()

            # Check if this is a rate limit error
            is_rate_limit_error = any(
                keyword in error_msg
                for keyword in [
                    "rate limit",
                    "ratelimit",
                    "429",
                    "quota",
                    "too many requests",
                    "resource_exhausted",
                ]
            )

            if is_rate_limit_error:
                logger.warning(f"Rate limit error from {model_name}: {e}")

                # Retry with exponential backoff (if not already at max retries)
                if retry_count < self.max_retries and self.auto_wait:
                    retry_count += 1
                    # Force wait time of 60s for rate limit errors
                    backoff_time = 60 * (self.backoff_base ** (retry_count - 1))

                    if backoff_time <= self.max_wait_seconds:
                        logger.info(
                            f"Retrying {model_name} after rate limit error "
                            f"(attempt {retry_count}/{self.max_retries}, waiting {backoff_time:.1f}s)"
                        )
                        time.sleep(backoff_time)
                        self.stats["rate_limit_waits"] += 1
                        # Recursive retry
                        return self._try_invoke_model(llm, model_name, input_data, is_primary, **kwargs)

                # Max retries exhausted or wait too long
                # Check if minimum time since last call has passed
                last_call_time = self.rate_tracker.get_last_call_time()
                if last_call_time is not None:
                    time_since_last_call = time.time() - last_call_time
                    if time_since_last_call < self.min_wait_before_fallback:
                        remaining_wait = self.min_wait_before_fallback - time_since_last_call
                        logger.info(
                            f"Rate limit error persists, but only {time_since_last_call:.1f}s since last call. "
                            f"Waiting additional {remaining_wait:.1f}s, then making ONE FINAL ATTEMPT."
                        )
                        time.sleep(remaining_wait)
                        self.stats["rate_limit_waits"] += 1

                        # Make ONE FINAL ATTEMPT after ensuring 90s wait
                        logger.info(
                            f"Making final attempt for {model_name} after {self.min_wait_before_fallback}s wait"
                        )
                        # Recursively call this method ONE MORE TIME (will fallback if fails)
                        kwargs_copy = {k: v for k, v in kwargs.items() if k != "retry_count"}
                        return self._try_invoke_model(
                            llm, model_name, input_data, is_primary, retry_count=self.max_retries + 2, **kwargs_copy
                        )

                logger.error(f"Rate limit error persists after {retry_count} retries. Using fallback.")
                self.stats["rate_limit_fallbacks"] += 1
                return None

            # Not a rate limit error - fallback immediately on second occurrence
            # (Could be authentication, invalid request, etc.)
            logger.error(f"Unexpected error invoking {model_name}: {e}", exc_info=True)
            return None

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

        # Fallback: rough estimation (1 token ≈ 4 characters for English text)
        estimated = len(input_text) // 4
        logger.debug(f"Using character-based token estimation: {estimated} tokens")
        return estimated

    @staticmethod
    def _get_tokenizer_static(model_name: str):
        """Get appropriate tokenizer for a model (static method).

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
                # Map to appropriate encoding
                encoding_map = {
                    "gpt-4": "cl100k_base",
                    "gpt-3.5": "cl100k_base",
                }

                encoding_name = "cl100k_base"  # Default for GPT-4/3.5
                for key, value in encoding_map.items():
                    if key in base_model:
                        encoding_name = value
                        break

                return tiktoken.get_encoding(encoding_name)

            # For non-OpenAI models, return None (will use character estimation)
            return None

        except Exception as e:
            logger.debug(f"Could not load tokenizer for {model_name}: {e}")
            return None

    def _get_tokenizer(self, model_name: str):
        """Get appropriate tokenizer for a model.

        Args:
            model_name: Full model name (e.g., "openai/gpt-4o-mini")

        Returns:
            Tokenizer instance or None
        """
        return self._get_tokenizer_static(model_name)

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

    def get_rate_limit_stats(self, model_name: str = None) -> Dict:
        """Get rate limit statistics for a model.

        Args:
            model_name: Model to get stats for (defaults to primary)

        Returns:
            Rate limit usage statistics
        """
        model = model_name or self.primary_model_name
        return self.rate_tracker.get_usage_stats(model)

    def bind(self, **kwargs):
        """Bind arguments to the primary LLM (for LangChain compatibility).

        This delegates to the primary LLM's bind method.

        Args:
            **kwargs: Arguments to bind

        Returns:
            Self (for chaining)
        """
        # Bind to primary LLM if it has the method
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
        return "auto_picker_llm"

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
