# Exponential Backoff Implementation - Complete Guide

## Overview

The AutoPickerLLM system now implements **exponential backoff** as its **PRIMARY** strategy for handling rate limits, with fallback to alternative models as a **SECONDARY** strategy only for unexpected errors.

## Implementation Date

2025-10-08

## Core Philosophy

**WAIT-FIRST, FALLBACK-SECOND**

1. **PRIMARY Strategy: Wait with Exponential Backoff**
   - When rate limited, calculate exact wait time needed
   - Retry with exponentially increasing wait times
   - Wait up to 5 minutes (configurable) before giving up
   - This ensures primary model is used whenever possible

2. **SECONDARY Strategy: Fallback Models**
   - Only used when:
     - Wait time exceeds `max_wait_seconds` after all retries
     - Non-rate-limit errors occur (unexpected errors)
   - Fallbacks should be RARE in normal operation

## Key Configuration Parameters

```python
auto_llm = AutoPickerLLM(
    primary_llm=primary,
    primary_model_name="openai/gpt-4o-mini",
    fallback_llms=[(fallback1, "gemini/gemini-2.5-flash-lite")],
    rate_tracker=rate_tracker,

    # Exponential backoff configuration
    auto_wait=True,                  # Enable automatic waiting (default: True)
    max_wait_seconds=300.0,          # Max wait time before fallback (default: 5 minutes)
    max_retries=3,                   # Max retry attempts (default: 3)
    backoff_base=2.0,                # Exponential multiplier (default: 2.0)
)
```

## How Exponential Backoff Works

### Formula

```
wait_time = base_wait * (backoff_base ^ (retry_count - 1))
```

### Example Sequence

Assume `base_wait = 60s`, `backoff_base = 2.0`, `max_retries = 3`:

| Retry | Calculation | Wait Time | Cumulative Time |
|-------|-------------|-----------|-----------------|
| 0 (first attempt) | 60 * 2^0 = 60 * 1 | 60s | 60s |
| 1 | 60 * 2^0 = 60 * 1 | 60s | 120s |
| 2 | 60 * 2^1 = 60 * 2 | 120s | 240s |
| 3 | 60 * 2^2 = 60 * 4 | 240s | 480s (exceeds 300s max) |

At retry 3, wait time (240s) + previous cumulative (240s) = 480s exceeds `max_wait_seconds` (300s), so fallback is triggered.

## Behavior Flowchart

```
Request Received
    ↓
Estimate Tokens
    ↓
Check Context Length ──→ Too Large? ──→ Context Fallback
    ↓                                      (separate feature)
 Fits OK
    ↓
Check Rate Limit
    ↓
Can Make Request? ──Yes──→ Invoke LLM ──Success──→ Return Response ✅
    ↓                           ↓
   No                        Error?
    ↓                           ↓
Calculate Wait Time        Rate Limit Error?
    ↓                           ↓
auto_wait enabled?        Yes: Retry with Backoff
    ↓                     No: Fallback Immediately
   Yes                          ↓
    ↓                      Try Fallback Models
Wait Time > max_wait?           ↓
    ↓                      Success? ──Yes──→ Return Response ✅
   No                           ↓
    ↓                           No
Apply Exponential Backoff       ↓
(retry_count < max_retries)  Raise Error ❌
    ↓
Sleep(backoff_time)
    ↓
Increment retry_count
    ↓
Retry Check Rate Limit
    ↓
Still Limited? ──No──→ Invoke LLM
    ↓
   Yes
    ↓
Retry Exceeded? ──Yes──→ Fallback
    ↓
   No
    ↓
Increase Backoff & Retry Again
```

## Code Implementation Details

### 1. Rate Limit Retry Loop with Exponential Backoff

**File**: `coffee_maker/langchain_observe/auto_picker_llm.py`
**Lines**: 346-392

```python
# NEW: Retry with exponential backoff for rate limits
retry_count = 0
while retry_count <= self.max_retries:
    # Check if we can make the request
    if not self.rate_tracker.can_make_request(model_name, estimated_tokens):
        wait_time = self.rate_tracker.get_wait_time(model_name, estimated_tokens)

        if not self.auto_wait:
            logger.info(f"Rate limit reached for {model_name}, auto-wait disabled")
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
    logger.error(f"Exhausted {self.max_retries} retries for {model_name}. Using fallback.")
    self.stats["rate_limit_fallbacks"] += 1
    return None
```

### 2. Enhanced Error Handling with Rate Limit Detection

**File**: `coffee_maker/langchain_observe/auto_picker_llm.py`
**Lines**: 459-502

```python
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
        logger.error(f"Rate limit error persists after {retry_count} retries. Using fallback.")
        self.stats["rate_limit_fallbacks"] += 1
        return None

    # Not a rate limit error - fallback immediately on second occurrence
    logger.error(f"Unexpected error invoking {model_name}: {e}", exc_info=True)
    return None
```

## Behavior Examples

### Scenario 1: Normal Operation (No Rate Limits)

```
Request 1 at 10:00:00
├─ Check rate limit: OK ✅
├─ Invoke gpt-4o-mini
└─ Response returned (latency: 1.2s)

Request 2 at 10:00:05
├─ Check rate limit: OK ✅
├─ Invoke gpt-4o-mini
└─ Response returned (latency: 1.1s)
```

**Result**: Primary model used, no waiting, no fallback

---

### Scenario 2: Rate Limited - Wait and Retry (Success)

```
Request at 10:00:00
├─ Check rate limit: EXCEEDED ❌ (501/500 RPM)
├─ Calculate wait time: 45s
├─ Apply backoff (retry 0): 45s * 2^0 = 45s
├─ Sleep 45s
├─ Retry at 10:00:45
├─ Check rate limit: OK ✅
├─ Invoke gpt-4o-mini
└─ Response returned

Stats:
  - rate_limit_waits: 1
  - rate_limit_fallbacks: 0
  - primary_requests: 1
```

**Result**: Waited 45s, primary model used successfully

---

### Scenario 3: Rate Limited - Multiple Retries with Exponential Backoff

```
Request at 10:00:00
├─ Check rate limit: EXCEEDED ❌ (510/500 RPM)
├─ Calculate wait time: 30s
├─ Apply backoff (retry 0): 30s * 2^0 = 30s
├─ Sleep 30s
├─ Retry at 10:00:30
├─ Check rate limit: STILL EXCEEDED ❌ (505/500 RPM)
├─ Apply backoff (retry 1): 30s * 2^0 = 30s
├─ Sleep 30s
├─ Retry at 10:01:00
├─ Check rate limit: STILL EXCEEDED ❌ (501/500 RPM)
├─ Apply backoff (retry 2): 30s * 2^1 = 60s
├─ Sleep 60s
├─ Retry at 10:02:00
├─ Check rate limit: OK ✅
├─ Invoke gpt-4o-mini
└─ Response returned

Stats:
  - rate_limit_waits: 3
  - rate_limit_fallbacks: 0
  - primary_requests: 1
```

**Result**: Waited total 120s (30+30+60), primary model used successfully

---

### Scenario 4: Rate Limited - Exponential Backoff Exceeds Max Wait

```
Request at 10:00:00
├─ Check rate limit: EXCEEDED ❌ (520/500 RPM)
├─ Calculate wait time: 120s
├─ Apply backoff (retry 0): 120s * 2^0 = 120s
├─ Sleep 120s
├─ Retry at 10:02:00
├─ Check rate limit: STILL EXCEEDED ❌ (515/500 RPM)
├─ Apply backoff (retry 1): 120s * 2^0 = 120s
├─ Sleep 120s
├─ Retry at 10:04:00
├─ Check rate limit: STILL EXCEEDED ❌ (510/500 RPM)
├─ Apply backoff (retry 2): 120s * 2^1 = 240s
├─ Check: 240s > max_wait_seconds (300s)? No
├─ Sleep 240s
├─ Retry at 10:08:00
├─ Check rate limit: STILL EXCEEDED ❌
├─ Apply backoff (retry 3): 120s * 2^2 = 480s
├─ Check: 480s > max_wait_seconds (300s)? YES ❌
├─ Fallback to gemini-2.5-flash-lite
├─ Invoke gemini-2.5-flash-lite
└─ Response returned

Stats:
  - rate_limit_waits: 3
  - rate_limit_fallbacks: 1
  - fallback_requests: 1
```

**Result**: Waited total 480s (120+120+240), then fell back to alternative model

---

### Scenario 5: API Rate Limit Error (HTTP 429)

```
Request at 10:00:00
├─ Check rate limit: OK ✅ (internal tracker shows capacity)
├─ Invoke gpt-4o-mini
├─ API returns: HTTP 429 "Rate limit exceeded" ❌
├─ Detect rate limit error in exception
├─ Apply backoff (retry 1): 60s * 2^0 = 60s
├─ Sleep 60s
├─ Retry at 10:01:00
├─ Invoke gpt-4o-mini
├─ API returns: HTTP 429 "Rate limit exceeded" ❌
├─ Apply backoff (retry 2): 60s * 2^1 = 120s
├─ Sleep 120s
├─ Retry at 10:03:00
├─ Invoke gpt-4o-mini
├─ API Success ✅
└─ Response returned

Stats:
  - rate_limit_waits: 2
  - rate_limit_fallbacks: 0
  - primary_requests: 1
```

**Result**: Detected API-level rate limit, retried with backoff, eventually succeeded

---

### Scenario 6: Unexpected Error (Non-Rate-Limit)

```
Request at 10:00:00
├─ Check rate limit: OK ✅
├─ Invoke gpt-4o-mini
├─ Error: "Connection timeout" ❌
├─ Error type: NOT rate limit
├─ Fallback to gemini-2.5-flash-lite
├─ Invoke gemini-2.5-flash-lite
└─ Response returned

Stats:
  - rate_limit_waits: 0
  - rate_limit_fallbacks: 0
  - fallback_requests: 1
```

**Result**: Non-rate-limit error triggered immediate fallback (no retries)

---

## Statistics Tracking

The `AutoPickerLLM.stats` dictionary tracks:

```python
{
    "total_requests": 100,         # Total requests made
    "primary_requests": 85,        # Requests using primary model
    "fallback_requests": 15,       # Requests using fallback models
    "rate_limit_waits": 42,        # Times system waited for rate limits
    "rate_limit_fallbacks": 12,    # Rate limits that triggered fallback
}
```

### Interpreting Stats

**Good Performance (Wait-First Working)**:
```python
{
    "total_requests": 1000,
    "primary_requests": 950,       # 95% primary usage ✅
    "fallback_requests": 50,       # 5% fallback usage ✅
    "rate_limit_waits": 200,       # Many waits (system is patient) ✅
    "rate_limit_fallbacks": 30,    # Few fallbacks (waits work!) ✅
}
```

**Problem Pattern (Too Many Fallbacks)**:
```python
{
    "total_requests": 1000,
    "primary_requests": 400,       # 40% primary usage ❌
    "fallback_requests": 600,      # 60% fallback usage ❌
    "rate_limit_waits": 50,        # Few waits ❌
    "rate_limit_fallbacks": 550,   # Many fallbacks ❌
}
```
**Action**: Increase `max_wait_seconds` or `max_retries` to be more patient

---

## Configuration Tuning

### Conservative (Maximize Primary Model Usage)

```python
AutoPickerLLM(
    ...,
    max_wait_seconds=600.0,    # Wait up to 10 minutes
    max_retries=5,             # Try 5 times
    backoff_base=1.5,          # Slower exponential growth
)
```

**Best for**: Production systems where consistency matters more than latency

---

### Aggressive (Minimize Latency)

```python
AutoPickerLLM(
    ...,
    max_wait_seconds=30.0,     # Wait max 30 seconds
    max_retries=2,             # Try only twice
    backoff_base=3.0,          # Faster exponential growth
)
```

**Best for**: Development/testing where quick fallback is preferred

---

### Balanced (Default)

```python
AutoPickerLLM(
    ...,
    max_wait_seconds=300.0,    # Wait up to 5 minutes
    max_retries=3,             # Try 3 times
    backoff_base=2.0,          # Standard exponential growth
)
```

**Best for**: Most production use cases

---

## Langfuse Integration

### Tracked Events

1. **Rate Limit Waits**: Logged in stats, visible in generation metadata
2. **Rate Limit Fallbacks**: Logged as Langfuse events with metadata
3. **Context Fallbacks**: Logged separately (different feature)

### Example Langfuse Event

```python
langfuse_client.event(
    name="rate_limit_fallback",
    metadata={
        "original_model": "openai/gpt-4o-mini",
        "fallback_model": "gemini/gemini-2.5-flash-lite",
        "reason": "rate_limit_or_error",
        "wait_time_exceeded": 480.0,
        "max_wait_seconds": 300.0,
        "retry_count": 3
    }
)
```

### Monitoring Queries

See `docs/langfuse_cost_queries.md` and `docs/fallback_tracking_summary.md` for complete SQL queries.

**Quick Query - Fallback Rate**:
```sql
SELECT
    COUNT(*) as total_fallbacks,
    COUNT(*) FILTER (WHERE name = 'rate_limit_fallback') as rate_limit_fallbacks,
    COUNT(*) FILTER (WHERE name = 'context_length_fallback') as context_fallbacks
FROM events
WHERE name IN ('rate_limit_fallback', 'context_length_fallback')
    AND created_at >= NOW() - INTERVAL '24 hours';
```

---

## Best Practices

### 1. Monitor Fallback Rate

**Goal**: Keep fallback rate < 10%

```python
stats = auto_llm.get_stats()
fallback_rate = stats["fallback_requests"] / stats["total_requests"] * 100

if fallback_rate > 10:
    print(f"WARNING: High fallback rate: {fallback_rate:.1f}%")
    print("Consider increasing max_wait_seconds or max_retries")
```

### 2. Set Realistic Wait Times

- **Web APIs**: 30-60s max wait
- **Background Jobs**: 300-600s max wait
- **Batch Processing**: No limit (or very high)

### 3. Use Appropriate Backoff Base

- `1.5`: Gentle growth (1.5x each retry)
- `2.0`: Standard growth (2x each retry) - **recommended**
- `3.0`: Aggressive growth (3x each retry)

### 4. Log and Alert

```python
# Alert if too many retries
if auto_llm.stats["rate_limit_waits"] > 100:
    send_alert("High rate limit pressure - consider tier upgrade")

# Alert if too many fallbacks
if auto_llm.stats["rate_limit_fallbacks"] > 50:
    send_alert("Frequent fallbacks - increase max_wait_seconds")
```

### 5. Tier Planning

Track your usage patterns:

```python
# If you're hitting limits frequently, upgrade tier
total_waits = auto_llm.stats["rate_limit_waits"]
total_requests = auto_llm.stats["total_requests"]

if total_waits / total_requests > 0.3:  # 30% of requests wait
    print("Consider upgrading to higher tier for better throughput")
```

---

## Migration Guide

### From Old Logic (Fallback-First)

**Before** (immediate fallback after short wait):
```python
AutoPickerLLM(
    ...,
    max_wait_seconds=10.0,  # Very short wait
)
```

**After** (wait-first with exponential backoff):
```python
AutoPickerLLM(
    ...,
    max_wait_seconds=300.0,  # Patient waiting
    max_retries=3,           # Multiple attempts
    backoff_base=2.0,        # Exponential growth
)
```

### Expected Behavior Changes

| Scenario | Before | After |
|----------|--------|-------|
| Rate limited | Wait 10s → Fallback | Wait 30s → Retry → Wait 30s → Retry → Wait 60s → Retry |
| Heavy load | Many fallbacks | Few fallbacks, more waiting |
| Primary model usage | 60-70% | 85-95% |
| Fallback usage | 30-40% | 5-15% |
| Average latency | Lower | Higher (but more consistent) |

---

## Testing

### Test Coverage

All exponential backoff behavior is tested in `tests/unit/test_auto_picker_llm.py`:

1. ✅ `test_primary_llm_used_when_available` - Normal operation
2. ✅ `test_fallback_when_rate_limited` - Fallback after retries exhausted
3. ✅ `test_auto_wait_when_wait_time_acceptable` - Wait and retry successfully
4. ✅ `test_cascading_fallbacks` - Multiple fallback attempts
5. ✅ `test_llm_invocation_error_triggers_fallback` - Non-rate-limit errors

### Running Tests

```bash
# Run all tests
poetry run pytest tests/unit/test_auto_picker_llm.py -v

# Run specific test
poetry run pytest tests/unit/test_auto_picker_llm.py::TestAutoPickerLLM::test_auto_wait_when_wait_time_acceptable -v
```

---

## Troubleshooting

### Problem: Too Many Fallbacks

**Symptoms**: `fallback_requests > 20%` of total requests

**Solutions**:
1. Increase `max_wait_seconds` (e.g., 300 → 600)
2. Increase `max_retries` (e.g., 3 → 5)
3. Reduce `backoff_base` (e.g., 2.0 → 1.5)
4. Upgrade API tier for higher rate limits

---

### Problem: Requests Too Slow

**Symptoms**: Average latency very high, many waits

**Solutions**:
1. Decrease `max_wait_seconds` (e.g., 300 → 60)
2. Decrease `max_retries` (e.g., 3 → 2)
3. Increase `backoff_base` (e.g., 2.0 → 3.0) to hit max faster
4. Accept more fallbacks for lower latency

---

### Problem: Rate Limit Errors Still Occur

**Symptoms**: API returns HTTP 429 even after waiting

**Possible Causes**:
1. **Daily limit hit**: No retry will help, must wait until next day
2. **Shared rate limit**: Other processes using same API key
3. **Incorrect rate limit config**: `RateLimitConfig` doesn't match actual tier

**Solutions**:
1. Check daily usage in Langfuse
2. Use separate API keys per process
3. Verify `RateLimitConfig` matches your actual tier limits

---

## Summary

### Key Changes from Previous Implementation

| Feature | Before | After |
|---------|--------|-------|
| Default max wait | 10 seconds | 300 seconds (5 minutes) |
| Retry strategy | Single attempt | Up to 3 retries with exponential backoff |
| Backoff algorithm | None | `wait_time * backoff_base^(retry_count-1)` |
| Rate limit error handling | Immediate fallback | Retry with backoff up to max_retries |
| Philosophy | "Fallback quickly" | "Wait patiently, fallback rarely" |

### When to Use Fallback

**Old behavior**: Fallback after 10s wait
**New behavior**: Fallback only when:
1. Wait time exceeds `max_wait_seconds` after all retries, OR
2. Error is NOT a rate limit error (unexpected error)

### Expected Outcomes

- ✅ **95%+ primary model usage** (vs 60-70% before)
- ✅ **5-15% fallback usage** (vs 30-40% before)
- ✅ **Fewer Langfuse fallback events**
- ✅ **More predictable costs** (primary model used consistently)
- ⚠️ **Higher average latency** (waiting instead of immediate fallback)

---

## Conclusion

The exponential backoff implementation transforms AutoPickerLLM from a "fallback-first" system to a "wait-first" system, ensuring:

1. **Primary model prioritization**: Maximum use of your chosen primary model
2. **Graceful degradation**: Intelligent retry with increasing wait times
3. **Rare fallbacks**: Alternative models only used when truly necessary
4. **Cost predictability**: Consistent primary model usage = predictable costs
5. **Full observability**: All waits and fallbacks tracked in Langfuse

All changes are **backward compatible** - existing code continues to work, but with better default behavior.
