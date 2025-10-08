# AutoPickerLLM Implementation Summary

## Overview

The AutoPickerLLM system provides intelligent rate limiting and automatic fallback for LLM API calls. It prevents API limit failures and optimizes cost by automatically selecting the best available model based on current rate limits.

## Key Components

### 1. Rate Limiting (`rate_limiter.py`)

**RateLimitConfig**
- Dataclass defining rate limits for a model
- Fields: `requests_per_minute`, `tokens_per_minute`, `requests_per_day`

**RateLimitTracker**
- Sliding window algorithm for tracking usage
- Tracks requests and tokens per model
- Methods:
  - `can_make_request(model, estimated_tokens)` - Check if request is allowed
  - `record_request(model, tokens_used)` - Record completed request
  - `get_wait_time(model, estimated_tokens)` - Calculate wait time until next allowed request
  - `get_usage_stats(model)` - Get current usage statistics

### 2. Model Configuration (`llm_config.py`)

**MODEL_CONFIGS**
- Centralized configuration for all LLM models
- Organized by provider (openai, gemini)
- Contains:
  - Context length limits
  - Max output tokens
  - Rate limits per tier (free, tier1, tier2, paid)
  - Use cases and capabilities

**Helper Functions**
- `get_rate_limits_for_tier(tier)` - Get rate limits for API tier
- `get_fallback_models()` - Get ordered list of fallback models
- `get_model_config(provider, model)` - Get specific model configuration

### 3. AutoPickerLLM (`auto_picker_llm.py`)

**AutoPickerLLM Class**
- Intelligent wrapper around LLM instances
- Automatically selects best available model based on rate limits
- Features:
  - Token estimation using tiktoken for OpenAI models
  - Automatic waiting when rate limited (configurable)
  - Cascading fallback to alternative models
  - Detailed statistics tracking

**Key Methods**
- `invoke(input_data, **kwargs)` - Main entry point, handles rate limiting and fallback
- `_try_invoke_model(llm, model_name, input_data, is_primary, **kwargs)` - Try specific model
- `_estimate_tokens(input_data, model_name)` - Estimate token usage
- `get_stats()` - Get usage statistics
- `get_rate_limit_stats(model_name)` - Get rate limit statistics

**Statistics Tracked**
- Total requests
- Primary model requests
- Fallback requests
- Rate limit waits
- Rate limit fallbacks

### 4. Helper Functions (`create_auto_picker.py`)

**create_auto_picker_llm()**
- Create AutoPickerLLM with automatic configuration
- Parameters:
  - `tier` - API tier for rate limiting
  - `primary_provider` - Primary LLM provider
  - `primary_model` - Primary model name
  - `auto_wait` - Whether to auto-wait when rate limited
  - `max_wait_seconds` - Max wait before fallback
  - `streaming` - Enable streaming

**create_auto_picker_for_react_agent()**
- Optimized preset for ReAct agents
- Uses gpt-4o-mini as primary with streaming enabled
- Shorter max_wait_seconds (5s) for interactive use

## Integration

### ReAct Agent Integration

The AutoPickerLLM is integrated into the ReAct agent creation:

```python
# In coffee_maker/code_formatter/agents.py
def create_react_formatter_agent(langfuse_client, llm, use_auto_picker=False, tier="tier1"):
    if use_auto_picker and not isinstance(llm, AutoPickerLLM):
        from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_for_react_agent
        llm = create_auto_picker_for_react_agent(tier=tier, streaming=True)

    # ... rest of agent creation
    return agent, tools, llm
```

### Main Entry Point

```python
# In coffee_maker/code_formatter/main.py
auto_picker_llm = create_auto_picker_for_react_agent(tier="tier1", streaming=True)
react_agent, tools, llm_instance = create_react_formatter_agent(
    langfuse_client, auto_picker_llm, use_auto_picker=False
)

# After execution, print statistics
if isinstance(llm_instance, AutoPickerLLM):
    stats = llm_instance.get_stats()
    logger.info(f"Total requests: {stats['total_requests']}")
    logger.info(f"Primary model: {stats['primary_requests']} ({stats['primary_usage_percent']:.1f}%)")
    logger.info(f"Fallback: {stats['fallback_requests']} ({stats['fallback_usage_percent']:.1f}%)")
```

## Example Usage

```python
from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_llm

# Create AutoPickerLLM
auto_llm = create_auto_picker_llm(
    tier="tier1",
    primary_provider="openai",
    primary_model="gpt-4o-mini",
    auto_wait=True,
    max_wait_seconds=10.0,
    streaming=True
)

# Use like any LLM
response = auto_llm.invoke({"input": "Review this code..."})

# Get statistics
stats = auto_llm.get_stats()
print(f"Primary usage: {stats['primary_usage_percent']:.1f}%")
print(f"Fallbacks: {stats['fallback_requests']}")
```

## Testing

### Unit Tests

**test_rate_limiter.py** (13 tests)
- Rate limit configuration
- RPM (requests per minute) limits
- TPM (tokens per minute) limits
- Daily request limits
- Wait time calculation
- Old request cleanup
- Usage statistics

**test_auto_picker_llm.py** (10 tests)
- Primary LLM usage
- Fallback on rate limit
- Auto-wait behavior
- Cascading fallbacks
- Error handling
- Token estimation
- Statistics tracking
- Rate limit stats

All 23 tests pass ✓

## Configuration by Tier

### Free Tier
- OpenAI: 200 RPM, 40K TPM, 500 requests/day
- Gemini: 15 RPM, 250K TPM, 1000 requests/day

### Tier 1
- OpenAI gpt-4o-mini: 500 RPM, 200K TPM, 10K requests/day
- Gemini flash-lite: 1000 RPM, 4M TPM, no daily limit

### Tier 2
- OpenAI gpt-4o-mini: 5000 RPM, 2M TPM, 100K requests/day
- Gemini flash: 2000 RPM, 4M TPM, no daily limit

### Paid Tier
- OpenAI gpt-4o: 10K RPM, 30M TPM, no daily limit
- Gemini flash: 4000 RPM, 4M TPM, no daily limit

## Future Enhancements

See `docs/llm_rate_limiting_and_cost_optimization_plan.md` for planned features:
- Cost tracking and calculation
- Budget management
- Langfuse cost integration
- Context length management
- Enhanced model selection strategies
