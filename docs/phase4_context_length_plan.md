# Phase 4: Context Length Management - Implementation Plan

## Overview

Implement automatic detection and handling of inputs that exceed model context windows, with intelligent fallback to larger-context models.

## Principles

1. **NEVER truncate user input** - Preserve all information
2. **Automatic fallback** - Try models with larger context windows
3. **Clear errors** - If no model can handle the input, throw descriptive error
4. **Transparent logging** - Log all context-related decisions to Langfuse

## Implementation Strategy

### 1. Context Length Detection

Before invoking any model, check if estimated input tokens exceed the model's context window:

```python
estimated_tokens = self._estimate_tokens(input_data, model_name)
max_context = get_model_context_length(model_name)

if estimated_tokens > max_context:
    # Input too large for this model
    # Try fallback to larger-context model
```

### 2. Large-Context Model Fallback

Automatically try models with progressively larger context windows:

**Priority Order (by context length):**
1. `gemini/gemini-2.5-pro` - 2,097,152 tokens (2M)
2. `openai/gpt-4.1` - 1,000,000 tokens (1M)
3. `gemini/gemini-2.5-flash-lite` - 1,048,576 tokens (1M)
4. `gemini/gemini-1.5-flash` - 1,048,576 tokens (1M)
5. `openai/gpt-4o` - 128,000 tokens (128K)
6. `openai/gpt-4o-mini` - 128,000 tokens (128K)

### 3. Error Handling

If no available model can handle the input size:
```python
raise ValueError(
    f"Input is too large ({estimated_tokens:,} tokens). "
    f"Maximum supported context is {max_available:,} tokens. "
    f"Please reduce input size."
)
```

## Implementation Details

### Changes to AutoPickerLLM

#### 1. Add Configuration

```python
class AutoPickerLLM(BaseLLM):
    # Existing fields...
    enable_context_fallback: bool = True  # Enable automatic fallback
    large_context_models: Optional[List[Tuple[Any, str]]] = None  # Lazy-loaded
```

#### 2. Add Context Check Method

```python
def _check_context_length(
    self, input_data: dict, model_name: str
) -> Tuple[bool, int, int]:
    """Check if input fits within model's context window.

    Args:
        input_data: Input dictionary
        model_name: Full model name (e.g., "openai/gpt-4o-mini")

    Returns:
        (fits, estimated_tokens, max_context_length)
    """
    estimated_tokens = self._estimate_tokens(input_data, model_name)
    max_context = get_model_context_length_from_name(model_name)

    fits = estimated_tokens <= max_context

    if not fits:
        logger.warning(
            f"Input ({estimated_tokens:,} tokens) exceeds {model_name} "
            f"context limit ({max_context:,} tokens)"
        )

    return fits, estimated_tokens, max_context
```

#### 3. Add Large-Context Model Finder

```python
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
    if self.large_context_models is None:
        self._initialize_large_context_models()

    # Filter models that can handle the input
    suitable_models = [
        (llm, name) for llm, name, context_len in self.large_context_models
        if context_len >= required_tokens
    ]

    return suitable_models


def _initialize_large_context_models(self):
    """Initialize list of large-context models sorted by preference."""
    from coffee_maker.langchain_observe.agents import get_llm
    from coffee_maker.langchain_observe.llm_config import get_large_context_models

    # Get models sorted by context length (largest first)
    large_models = get_large_context_models()

    self.large_context_models = []

    for provider, model, context_length in large_models:
        full_name = f"{provider}/{model}"

        # Skip if not in current rate tracker (not available in tier)
        if full_name not in self.rate_tracker.model_limits:
            logger.debug(f"Skipping {full_name} - not in current tier")
            continue

        try:
            # Create LLM instance
            llm_instance = get_llm(provider=provider, model=model)
            self.large_context_models.append((llm_instance, full_name, context_length))
            logger.debug(f"Added large-context model: {full_name} ({context_length:,} tokens)")
        except Exception as e:
            logger.warning(f"Could not initialize {full_name}: {e}")
```

#### 4. Modify _try_invoke_model

Add context check before rate limit check:

```python
def _try_invoke_model(
    self, llm: Any, model_name: str, input_data: dict, is_primary: bool, **kwargs
) -> Optional[Any]:
    """Try to invoke a specific model, handling context length and rate limits."""

    # NEW: Check context length FIRST
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
                        large_llm,
                        large_model_name,
                        input_data,
                        is_primary=False,
                        **kwargs
                    )

                    if result is not None:
                        # Log context fallback to Langfuse
                        if self.langfuse_client:
                            try:
                                self.langfuse_client.event(
                                    name="context_length_fallback",
                                    metadata={
                                        "original_model": model_name,
                                        "fallback_model": large_model_name,
                                        "estimated_tokens": estimated_tokens,
                                        "original_max_context": max_context,
                                        "fallback_max_context": get_model_context_length_from_name(large_model_name),
                                    }
                                )
                            except Exception as e:
                                logger.warning(f"Failed to log context fallback to Langfuse: {e}")

                        return result

            # No suitable model found
            max_available = max(
                (context for _, _, context in self.large_context_models),
                default=max_context
            )

            raise ValueError(
                f"Input is too large ({estimated_tokens:,} tokens) for any available model. "
                f"Maximum supported context: {max_available:,} tokens. "
                f"Original model: {model_name} (limit: {max_context:,} tokens). "
                f"Please reduce input size."
            )

    # Continue with existing rate limit check and invoke logic...
    # ... (rest of existing code)
```

### Changes to llm_config.py

Add helper functions:

```python
def get_large_context_models() -> List[Tuple[str, str, int]]:
    """Get all models sorted by context length (largest first).

    Returns:
        List of (provider, model_name, context_length) tuples
    """
    models_with_context = []

    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            context = config["context_length"]
            models_with_context.append((provider, model_name, context))

    # Sort by context length descending
    sorted_models = sorted(models_with_context, key=lambda x: x[2], reverse=True)

    return sorted_models


def get_model_context_length_from_name(full_model_name: str) -> int:
    """Get context length from full model name.

    Args:
        full_model_name: Format "provider/model" (e.g., "openai/gpt-4o")

    Returns:
        Context length in tokens

    Raises:
        ValueError: If model not found
    """
    if "/" not in full_model_name:
        raise ValueError(f"Invalid model name format: {full_model_name}. Expected 'provider/model'")

    provider, model = full_model_name.split("/", 1)

    if provider not in MODEL_CONFIGS:
        raise ValueError(f"Unknown provider: {provider}")

    if model not in MODEL_CONFIGS[provider]:
        raise ValueError(f"Unknown model: {model} for provider {provider}")

    return MODEL_CONFIGS[provider][model]["context_length"]
```

### Changes to create_auto_picker.py

Enable context fallback by default:

```python
def create_auto_picker_llm(...) -> AutoPickerLLM:
    # ... existing code ...

    # Create AutoPickerLLM
    auto_picker = AutoPickerLLM(
        primary_llm=primary_llm,
        primary_model_name=primary_model_name,
        fallback_llms=fallback_llms,
        rate_tracker=rate_tracker,
        auto_wait=auto_wait,
        max_wait_seconds=max_wait_seconds,
        cost_calculator=cost_calculator,
        langfuse_client=langfuse_client,
        enable_context_fallback=True,  # NEW: Enable by default
    )

    return auto_picker
```

## Testing Strategy

### Unit Tests

1. **Test context detection**
   - Input within limits → proceed normally
   - Input exceeds limits → trigger fallback

2. **Test large-context fallback**
   - Small input → use primary model
   - Large input → use gemini-2.5-pro or gpt-4.1
   - Very large input → use gemini-2.5-pro (2M tokens)

3. **Test error handling**
   - Input larger than any model → clear error message
   - No large-context models available → clear error

4. **Test Langfuse logging**
   - Context fallback event logged
   - Metadata includes original/fallback models and token counts

### Integration Tests

1. Test with actual large inputs (simulated)
2. Verify costs are tracked correctly for fallback models
3. Verify rate limits work with fallback models

## Langfuse Logging

### Event Structure

```python
langfuse_client.event(
    name="context_length_fallback",
    metadata={
        "original_model": "openai/gpt-4o-mini",
        "fallback_model": "gemini/gemini-2.5-pro",
        "estimated_tokens": 150000,
        "original_max_context": 128000,
        "fallback_max_context": 2097152,
        "reason": "input_exceeds_context"
    }
)
```

### Dashboard Query

```sql
-- Count context fallbacks by model
SELECT
    metadata->>'original_model' as original_model,
    metadata->>'fallback_model' as fallback_model,
    COUNT(*) as fallback_count,
    AVG(CAST(metadata->>'estimated_tokens' AS INTEGER)) as avg_input_tokens
FROM events
WHERE name = 'context_length_fallback'
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY original_model, fallback_model
ORDER BY fallback_count DESC;
```

## Benefits

1. **Never lose information** - No truncation means full context preserved
2. **Automatic optimization** - Use smallest model that can handle input
3. **Cost awareness** - Only use expensive large-context models when needed
4. **Clear errors** - Users know immediately if input is too large
5. **Full transparency** - All fallback decisions logged to Langfuse

## Example Behavior

### Scenario 1: Normal Input (1,000 tokens)
```
Primary model: openai/gpt-4o-mini (128K context)
Input: 1,000 tokens
Action: Use gpt-4o-mini ✅
```

### Scenario 2: Large Input (150,000 tokens)
```
Primary model: openai/gpt-4o-mini (128K context)
Input: 150,000 tokens
Action: Automatically fallback to gemini/gemini-2.5-pro (2M context) ✅
Logged: Context fallback event to Langfuse
```

### Scenario 3: Very Large Input (500,000 tokens)
```
Primary model: openai/gpt-4o-mini (128K context)
Input: 500,000 tokens
Action: Automatically fallback to gemini/gemini-2.5-pro (2M context) ✅
```

### Scenario 4: Impossibly Large Input (3,000,000 tokens)
```
Primary model: openai/gpt-4o-mini (128K context)
Input: 3,000,000 tokens
Action: Error ❌
Message: "Input is too large (3,000,000 tokens) for any available model. Maximum supported context: 2,097,152 tokens. Please reduce input size."
```

## Files to Create/Modify

### New Files
- `tests/unit/test_context_length_management.py` - Unit tests

### Modified Files
- `coffee_maker/langchain_observe/auto_picker_llm.py` - Add context checking
- `coffee_maker/langchain_observe/llm_config.py` - Add helper functions
- `coffee_maker/langchain_observe/create_auto_picker.py` - Enable by default
- `docs/langfuse_cost_queries.md` - Add context fallback queries

## Implementation Checklist

- [ ] Add helper functions to llm_config.py
- [ ] Add context checking to AutoPickerLLM
- [ ] Add large-context model initialization
- [ ] Modify _try_invoke_model for context fallback
- [ ] Add Langfuse event logging
- [ ] Update create_auto_picker.py
- [ ] Write unit tests
- [ ] Update documentation
- [ ] Run all tests
