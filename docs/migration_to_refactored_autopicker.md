# Migration to AutoPickerLLMRefactored

**Date**: 2025-10-08

**Status**: ✅ Complete

---

## Overview

This document describes the complete migration from the old `AutoPickerLLM` to the new `AutoPickerLLMRefactored` architecture.

---

## Why Migrate?

### Problems with Old AutoPickerLLM

1. **Too many responsibilities** (~780 lines)
   - Rate limiting logic
   - Retry logic with exponential backoff
   - Fallback orchestration
   - Cost tracking
   - Context management
   - Token estimation

2. **Hard to test**
   - Tightly coupled components
   - Complex initialization
   - Difficult to mock

3. **Inflexible**
   - No pluggable strategies
   - Fixed fallback order
   - Cannot optimize for cost or error type

### Benefits of New Architecture

1. **Clean separation of concerns**
   - Rate limiting → `ScheduledLLM`
   - Retry logic → `SchedulingStrategy`
   - Fallback selection → `FallbackStrategy`
   - Context checking → `ContextStrategy`
   - Orchestration → `AutoPickerLLMRefactored` (~350 lines)

2. **Pluggable strategies**
   - `SequentialFallback` (default, backward compatible)
   - `SmartFallback` (error-aware)
   - `CostOptimizedFallback` (cheapest first)
   - Custom strategies easily added

3. **Simple API**
   - `SmartLLM.for_tier("tier1")` - One line, production-ready
   - `LLMBuilder()` - Fluent API for advanced configuration
   - Sensible defaults for common use cases

---

## Migration Status

### Files Migrated

| File | Status | Changes |
|------|--------|---------|
| `llm_tools.py` | ✅ Complete | Uses `create_auto_picker_llm_refactored()` |
| `create_auto_picker.py` | ✅ Complete | Delegates to refactored version, marked DEPRECATED |
| `code_formatter/agents.py` | ✅ Complete | Updated isinstance() checks and imports |
| `code_formatter/main.py` | ✅ Complete | Updated statistics printing |
| `auto_picker_llm.py` | ✅ Deprecated | Marked DEPRECATED with migration guide |

### Test Status

| Test Suite | Tests | Status |
|-------------|-------|--------|
| `test_auto_picker_llm_refactored.py` | 14 | ✅ All passing |
| `test_context_strategy.py` | 17 | ✅ All passing |
| `test_fallback_strategy.py` | 22 | ✅ All passing |
| `test_builder.py` | 19 | ✅ All passing |
| **Total** | **72** | ✅ **100% passing** |

---

## Migration Guide

### Quick Migration (Most Users)

**Before** (old):
```python
from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_llm

llm = create_auto_picker_llm(
    tier="tier1",
    primary_provider="openai",
    primary_model="gpt-4o-mini",
    auto_wait=True,
    max_wait_seconds=300.0,
)
```

**After** (new - simple):
```python
from coffee_maker.langchain_observe.builder import SmartLLM

llm = SmartLLM.for_tier("tier1")
```

That's it! You get:
- Automatic rate limiting
- Smart fallback (error-aware)
- Cost tracking
- Context management
- Production-ready configuration

### Advanced Migration

**Before** (old):
```python
from coffee_maker.langchain_observe.auto_picker_llm import AutoPickerLLM
from coffee_maker.langchain_observe.llm import get_scheduled_llm
from coffee_maker.langchain_observe.global_rate_tracker import get_global_rate_tracker

rate_tracker = get_global_rate_tracker("tier1")
primary = get_scheduled_llm(provider="openai", model="gpt-4o-mini", tier="tier1")
fallback = get_scheduled_llm(provider="gemini", model="gemini-2.5-flash", tier="tier1")

auto_picker = AutoPickerLLM(
    primary_llm=primary,
    primary_model_name="openai/gpt-4o-mini",
    fallback_llms=[(fallback, "gemini/gemini-2.5-flash")],
    rate_tracker=rate_tracker,
    auto_wait=True,
    max_wait_seconds=300.0,
    max_retries=3,
    backoff_base=2.0,
)
```

**After** (new - advanced):
```python
from coffee_maker.langchain_observe.builder import LLMBuilder

llm = (LLMBuilder()
    .with_tier("tier1")
    .with_primary("openai", "gpt-4o-mini")
    .with_fallback("gemini", "gemini-2.5-flash")
    .with_cost_tracking()
    .with_smart_fallback()  # NEW: Error-aware fallback selection
    .with_max_wait(300.0)
    .build()
)
```

Much cleaner! And you get:
- Error-aware fallback selection
- Easier to read and maintain
- All parameters have sensible defaults
- Easy to add more configuration

### Custom Fallback Strategy

**New capability** (not possible with old version):
```python
from coffee_maker.langchain_observe.builder import LLMBuilder

# Cost-optimized: always use cheapest fallback
llm = (LLMBuilder()
    .with_tier("tier1")
    .with_primary("openai", "gpt-4o-mini")
    .with_fallbacks([
        ("gemini", "gemini-2.5-flash"),
        ("anthropic", "claude-3-5-haiku-20241022"),
    ])
    .with_cost_optimized_fallback()  # NEW: Prefer cheaper models
    .build()
)
```

---

## API Comparison

### Initialization

| Feature | Old API | New API |
|---------|---------|---------|
| Basic setup | 15 lines of code | 1 line |
| Primary model | Manual LLM creation | Provider + model string |
| Fallbacks | List of LLM tuples | List of (provider, model) tuples |
| Rate tracking | Manual rate tracker | Automatic (tier-based) |
| Cost tracking | Manual CostCalculator | Automatic with `.with_cost_tracking()` |
| Fallback strategy | Fixed sequential | Pluggable (sequential, smart, cost, custom) |

### Usage

Both versions have the same invocation API:
```python
# Works with both old and new
response = llm.invoke({"input": "Hello"})

# Stats also work the same
stats = llm.get_stats()
```

---

## Breaking Changes

**None!** The migration is 100% backward compatible.

- Old `AutoPickerLLM` still works
- Old `create_auto_picker_llm()` still works
- All existing code continues to function
- Tests pass without modification

However, old code is **marked as DEPRECATED** and should be migrated when convenient.

---

## Benefits Achieved

### 1. Cleaner Architecture

**Before**:
```
AutoPickerLLM (780 lines)
  ├─ Rate limiting logic
  ├─ Retry logic
  ├─ Backoff calculations
  ├─ Fallback orchestration
  ├─ Cost tracking
  └─ Context management
```

**After**:
```
AutoPickerLLMRefactored (350 lines)
  ├─ Fallback orchestration only
  └─ Delegates to specialized components:
      ├─ ScheduledLLM → Rate limiting & retries
      ├─ FallbackStrategy → Fallback selection
      ├─ ContextStrategy → Context checking
      ├─ CostCalculator → Cost tracking
      └─ Langfuse → Observability
```

### 2. Pluggable Strategies

**Sequential** (default, backward compatible):
```python
.with_sequential_fallback()  # Try fallbacks in order
```

**Smart** (error-aware):
```python
.with_smart_fallback()  # Choose fallback based on error type
# - Context error → Larger context model
# - Rate limit error → Different provider
```

**Cost-optimized**:
```python
.with_cost_optimized_fallback()  # Always use cheapest fallback
```

**Custom**:
```python
class MyStrategy(FallbackStrategy):
    def select_next_fallback(self, failed_model, available, error, metadata):
        # Your custom logic here
        pass

.with_custom_fallback_strategy(MyStrategy())
```

### 3. Simpler API

**One-liner for common cases**:
```python
llm = SmartLLM.for_tier("tier1")
llm = SmartLLM.fast("tier1")       # Fast & cheap
llm = SmartLLM.powerful("tier1")   # Quality-focused
```

**Fluent API for advanced cases**:
```python
llm = (LLMBuilder()
    .with_tier("tier1")
    .with_primary("openai", "gpt-4o-mini")
    .with_fallback("gemini", "gemini-2.5-flash")
    .with_smart_fallback()
    .build()
)
```

### 4. Better Testing

**Before**:
- Hard to test in isolation
- Need to mock many dependencies
- Complex setup

**After**:
- Each component testable independently
- Strategy Pattern makes mocking easy
- 72 comprehensive tests (vs 0 before)

---

## Commits

| Commit | Description | Files |
|--------|-------------|-------|
| `0d33395` | Migrate llm_tools.py | 1 file |
| `a836202` | Migrate create_auto_picker.py | 1 file |
| `bf4ac25` | Migrate code_formatter | 2 files |
| `e1e86d5` | Deprecate old AutoPickerLLM | 1 file |

Total: **4 commits**, **5 files** migrated

---

## Recommendations

### For New Code

✅ **Use SmartLLM** for simple cases:
```python
from coffee_maker.langchain_observe.builder import SmartLLM
llm = SmartLLM.for_tier("tier1")
```

✅ **Use LLMBuilder** for custom configuration:
```python
from coffee_maker.langchain_observe.builder import LLMBuilder
llm = (LLMBuilder()
    .with_tier("tier1")
    .with_primary("openai", "gpt-4o-mini")
    .with_smart_fallback()
    .build()
)
```

### For Existing Code

⚠️ **No rush to migrate** - old code still works

But when you touch old code:
1. Replace `create_auto_picker_llm()` with `SmartLLM.for_tier()`
2. Replace manual `AutoPickerLLM` initialization with `LLMBuilder()`
3. Consider using smart or cost-optimized fallback strategies

### For Custom Strategies

💡 **Implement FallbackStrategy** for custom fallback logic:
```python
from coffee_maker.langchain_observe.strategies.fallback import FallbackStrategy

class MyStrategy(FallbackStrategy):
    def select_next_fallback(self, failed_model, available, error, metadata):
        # Your logic here
        pass
```

---

## Next Steps

Future enhancements (not required, but possible):

1. **Metrics Strategy** - Pluggable metrics collection
2. **Cost Budget Enforcement** - Automatic budget limits
3. **Token Estimation Strategy** - Pluggable token estimators
4. **Remove old AutoPickerLLM** - After 100% migration

---

## Summary

✅ Migration complete
✅ All files using new architecture
✅ Old code marked as deprecated
✅ 100% backward compatible
✅ 72 tests passing
✅ Cleaner, simpler, more flexible

The migration successfully improves code quality while maintaining full backward compatibility. Users can migrate at their convenience, with clear upgrade paths provided.
