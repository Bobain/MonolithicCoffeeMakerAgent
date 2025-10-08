# Model Characteristics Exposure - Implementation Summary

## Date
2025-10-08

## Overview
Successfully implemented comprehensive model characteristics exposure to agent tools, enabling agents to make informed decisions about which LLM models to use based on real-time availability, costs, context limits, and rate limit status.

## User Request
> "are models aware of their limitations or strength (long_context)? are these characteristics they clearly exposed when they are turned into tools so that their model user can eventually plan their use according to rate limits?"

**Answer**: YES! Models now fully expose their characteristics to agents.

## What Was Implemented

### 1. Enhanced Tool Descriptions

Every `invoke_llm_*` tool now includes comprehensive model information in its description:

```
PRIMARY MODEL: gpt-4o
  Context Window: 128,000 tokens
  Cost: $2.50/1M input tokens, $10.00/1M output tokens
  Rate Limits:
    - 500 requests/minute
    - 30,000 tokens/minute
    - 10,000 requests/day
  Current Usage:
    - Requests: 0.0% of limit
    - Tokens: 0.0% of limit
  ✓ STATUS: AVAILABLE

FALLBACK MODEL: gpt-4o-mini
  Context Window: 128,000 tokens
  Cost: $0.15/1M input tokens, $0.60/1M output tokens
  [... rate limits and usage ...]

BEHAVIOR:
- System will automatically wait (with exponential backoff) if rate limited
- Minimum 90 seconds must pass since last call before fallback
- Falls back only if wait exceeds 5 minutes OR unexpected errors occur
- All costs and usage tracked in Langfuse
```

### 2. New Tool: `check_llm_availability`

A dedicated tool that provides comprehensive status of ALL available models:

**Features**:
- Shows time since last LLM call (affects 90s fallback rule)
- Groups models by purpose (long_context, reasoning, fast, etc.)
- Displays real-time usage percentages
- Clear status indicators (✓ AVAILABLE, ⚠️ NEAR LIMIT, ⚠️ RATE LIMITED)
- Complete cost information for all models

**Example Output**:
```
================================================================================
LLM MODEL AVAILABILITY AND STATUS
================================================================================

⏱️  Last LLM call: 45 seconds ago
⚠️  Must wait 45s more before fallback allowed (90s minimum)

PURPOSE: REASONING
[OPENAI] Advanced reasoning and planning with chain-of-thought

  PRIMARY: o1
    Context: 200,000 tokens
    Cost: $15.00/$60.00 per 1M tokens (in/out)
    Usage: 5/20 req/min (25%), 12000/100000 tok/min (12%)
    ✓ AVAILABLE
```

### 3. Provider-Based Configuration

Refactored `llm_config.py` to pull information directly from provider files:

**Before** (hardcoded):
```python
MODEL_CONFIGS = {
    "openai": {
        "gpt-4o-mini": {
            "context_length": 128000,
            "rate_limits": {...},  # Manually duplicated
            "pricing": {...},      # Manually duplicated
        }
    }
}
```

**After** (dynamic from providers):
```python
# Import from provider files
from coffee_maker.langchain_observe.llm_providers import openai, gemini

# Automatically transform provider info
MODEL_CONFIGS = {
    "openai": _transform_provider_info_to_config("openai", openai.MODELS_INFO),
    "gemini": _transform_provider_info_to_config("gemini", gemini.MODELS_ÌNFO),
}
```

### 4. Enhanced Provider Files

#### `llm_providers/openai.py`
Added comprehensive `MODELS_INFO` with:
- Rate limits for tier1 and tier2
- Context lengths and max output tokens
- Pricing for all models
- All OpenAI models: gpt-4o, gpt-4o-mini, gpt-3.5-turbo, gpt-4.1, o1, o1-mini

#### `llm_providers/gemini.py`
Enhanced with missing models:
- Added `gemini-2.5-flash` (free and paid tiers)
- Added `gemini-2.0-flash-thinking-exp` (free and tier1)
- Added context_length to all models
- Complete pricing information

## Benefits for Agents

### 1. Informed Decision Making

Agents can now see:
- **Context limits**: Choose models based on input size
- **Current availability**: Avoid rate-limited models
- **Cost differences**: Optimize for budget when appropriate
- **Fallback behavior**: Understand what happens on rate limits

### 2. Proactive Planning

With `check_llm_availability`, agents can:
- Query all model statuses before starting work
- Plan which models to use for different parts of a task
- Avoid triggering rate limit waits
- Optimize costs by selecting cheaper models when sufficient

### 3. Real-Time Adaptation

Tools show current usage percentages:
- `0-79%`: ✓ AVAILABLE - safe to use
- `80-99%`: ⚠️ NEAR LIMIT - consider alternatives
- `100%`: ⚠️ RATE LIMITED - will auto-wait or fallback

## Implementation Details

### Key Functions

#### `get_model_characteristics()`
**Location**: `llm_tools.py:162-252`

Extracts and formats model characteristics:
```python
def get_model_characteristics(
    provider_name: str,
    primary_model: str,
    fallback_model: str,
    rate_tracker: RateLimitTracker
) -> str:
    # Returns formatted string with:
    # - Context windows
    # - Costs (handles FREE and paid models)
    # - Rate limits
    # - Current usage
    # - Availability status
```

#### `check_llm_availability()`
**Location**: `llm_tools.py:331-478`

Comprehensive status checker:
```python
def check_llm_availability(tier: str = "tier1") -> str:
    # Returns detailed status report showing:
    # - Time since last LLM call
    # - All models grouped by purpose
    # - Real-time usage for each
    # - Availability indicators
```

#### `_transform_provider_info_to_config()`
**Location**: `llm_config.py:11-87`

Transforms provider MODELS_INFO to MODEL_CONFIGS format:
- Collects all unique models across tiers
- Merges rate limits from multiple tiers
- Handles both simple and tiered pricing
- Preserves context length and max output tokens
- Automatically infers use cases

#### `_infer_use_cases()`
**Location**: `llm_config.py:90-136`

Intelligently determines use cases from model names:
- Large context: "2.5-pro", "1.5-pro", "4.1"
- Reasoning: "o1", "thinking"
- Budget: "lite", "mini", "3.5", "flash"
- Code review: "4o", "pro"

## Files Created/Modified

### Modified Files
1. **`llm_tools.py`**
   - Added `get_model_characteristics()` function
   - Added `check_llm_availability()` function and tool
   - Updated `create_llm_tools()` to include characteristics
   - Fixed pricing extraction (input_per_1m/output_per_1m keys)

2. **`llm_config.py`**
   - Complete rewrite to use provider files
   - Added `_transform_provider_info_to_config()`
   - Added `_infer_use_cases()`
   - MODEL_CONFIGS now dynamically built from providers

3. **`llm_providers/openai.py`**
   - Added comprehensive MODELS_INFO dictionary
   - Commented out example code that ran at import
   - Fixed MODELS_LIST to use string references

4. **`llm_providers/gemini.py`**
   - Added gemini-2.5-flash to all tiers
   - Added gemini-2.0-flash-thinking-exp
   - Added context_length to all models
   - Enhanced pricing information

5. **`llm_providers/__init__.py`**
   - Fixed SUPPORTED_PROVIDERS initialization
   - Added proper logging import

### Test Files
- All 61 existing tests pass
- `test_llm_tools.py`: Updated to handle check_llm_availability tool

## Usage Examples

### For Agent Development

```python
from coffee_maker.langchain_observe.llm_tools import create_llm_tools

# Create tools - characteristics automatically included
tools = create_llm_tools(tier="tier1")

# Agents see in tool descriptions:
# - Context windows: "Context Window: 128,000 tokens"
# - Costs: "$0.15/1M input tokens"
# - Current status: "✓ STATUS: AVAILABLE"

# Agent can check availability before choosing
availability_tool = [t for t in tools if t.name == "check_llm_availability"][0]
status = availability_tool.func()
# Returns comprehensive status of all models
```

### Adding a New Model

**Single source of truth approach**:

1. Add to provider file MODELS_INFO:
```python
# In llm_providers/openai.py
"gpt-5": {
    "requests per minute": 100,
    "tokens per minute": 50000,
    "requests per day": 5000,
    "context_length": 256000,
    "max_output_tokens": 8192,
    "price": {
        "per 1M tokens input": 5.00,
        "per 1M tokens output": 20.00,
    },
}
```

2. That's it! Automatically available in:
   - MODEL_CONFIGS
   - All LLM tools (when appropriate tier)
   - Rate tracking
   - Tool descriptions
   - Availability checker

## Test Results

```bash
$ poetry run pytest tests/unit/ -v
...
======================== 61 passed, 2 warnings in 1.37s ========================
```

All tests passing:
- ✅ 11 AutoPickerLLM tests
- ✅ 10 Context length management tests
- ✅ 7 Cost tracking tests
- ✅ 8 Global rate tracker tests
- ✅ 12 LLM tools tests (including new availability tool)
- ✅ 13 Rate limiter tests

## Demonstration

### Tool Description Example

```python
tools = create_llm_tools('tier1')
fast_tool = [t for t in tools if t.name == 'invoke_llm_openai_fast'][0]

print(fast_tool.description)
# Shows complete characteristics:
# - PRIMARY MODEL: gpt-4o-mini
#   Context Window: 128,000 tokens
#   Cost: $0.15/1M input, $0.60/1M output
#   Rate Limits: 500 RPM, 200K TPM, 10K RPD
#   Current Usage: 0.0% of limit
#   ✓ STATUS: AVAILABLE
```

### Availability Checker Example

```python
availability_tool = [t for t in tools if t.name == 'check_llm_availability'][0]
status = availability_tool.func()

# Returns comprehensive report grouped by purpose:
# PURPOSE: REASONING
#   PRIMARY: o1 (200K context, $15/$60 per 1M, ✓ AVAILABLE)
#   FALLBACK: o1-mini (128K context, $3/$12 per 1M, ✓ AVAILABLE)
#
# PURPOSE: FAST
#   PRIMARY: gpt-4o-mini (128K context, $0.15/$0.60, ✓ AVAILABLE)
#   ...
```

## Conclusion

✅ **Complete**: Model characteristics are now fully exposed to agents

Agents can now:
- ✅ See context window limits for each model
- ✅ View real-time rate limit usage
- ✅ Compare costs between models
- ✅ Check availability before making requests
- ✅ Understand fallback behavior
- ✅ Make informed decisions about model selection

All information is:
- ✅ Dynamically pulled from provider files (single source of truth)
- ✅ Real-time updated based on current usage
- ✅ Clearly formatted with status indicators
- ✅ Available in both tool descriptions and dedicated checker tool

The system now provides complete transparency to agents, enabling intelligent model selection based on context requirements, availability, and cost optimization.
