# Fallback Tracking in Langfuse - Complete Guide

## Overview

The AutoPickerLLM system tracks **all fallback events** in Langfuse, providing complete visibility into when and why alternative models are used.

## Types of Fallbacks Tracked

### 1. Rate Limit Fallbacks

**When it happens:** Primary model hits rate limits (RPM, TPM, or daily limits)

**Langfuse Event:**
```python
langfuse_client.event(
    name="rate_limit_fallback",
    metadata={
        "original_model": "openai/gpt-4o-mini",
        "fallback_model": "gemini/gemini-2.5-flash-lite",
        "reason": "rate_limit_or_error"
    }
)
```

**Example Scenario:**
```
Request #501 to gpt-4o-mini (limit: 500 RPM)
→ Rate limit exceeded
→ Automatically use gemini-2.5-flash-lite
→ Log rate_limit_fallback event ✅
```

### 2. Context Length Fallbacks

**When it happens:** Input exceeds model's context window

**Langfuse Event:**
```python
langfuse_client.event(
    name="context_length_fallback",
    metadata={
        "original_model": "openai/gpt-4o-mini",
        "fallback_model": "gemini/gemini-2.5-pro",
        "estimated_tokens": 150000,
        "original_max_context": 128000,
        "fallback_max_context": 2097152
    }
)
```

**Example Scenario:**
```
Input: 150,000 tokens
Primary: gpt-4o-mini (128K context limit)
→ Input too large
→ Automatically use gemini-2.5-pro (2M context)
→ Log context_length_fallback event ✅
```

## Langfuse Dashboard Queries

### Query 1: Rate Limit Fallback Tracking

**Purpose:** See when rate limits trigger fallbacks

```sql
SELECT
    metadata->>'original_model' as original_model,
    metadata->>'fallback_model' as fallback_model,
    COUNT(*) as fallback_count,
    DATE(created_at) as date
FROM events
WHERE name = 'rate_limit_fallback'
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY original_model, fallback_model, DATE(created_at)
ORDER BY date DESC, fallback_count DESC;
```

**What it shows:**
- Which models hit rate limits most often
- Which fallback models are used
- Daily patterns of rate limit issues

### Query 2: Context Length Fallback Tracking

**Purpose:** See when inputs exceed context limits

```sql
SELECT
    metadata->>'original_model' as original_model,
    metadata->>'fallback_model' as fallback_model,
    COUNT(*) as fallback_count,
    AVG(CAST(metadata->>'estimated_tokens' AS INTEGER)) as avg_input_tokens,
    AVG(CAST(metadata->>'original_max_context' AS INTEGER)) as original_context_limit,
    AVG(CAST(metadata->>'fallback_max_context' AS INTEGER)) as fallback_context_limit
FROM events
WHERE name = 'context_length_fallback'
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY original_model, fallback_model
ORDER BY fallback_count DESC;
```

**What it shows:**
- How often inputs are too large for primary model
- Average size of oversized inputs
- Which large-context models are used

### Query 3: All Fallbacks Combined

**Purpose:** Complete view of all fallback activity

```sql
SELECT
    name as fallback_type,
    metadata->>'original_model' as original_model,
    metadata->>'fallback_model' as fallback_model,
    COUNT(*) as total_fallbacks,
    DATE(created_at) as date
FROM events
WHERE name IN ('rate_limit_fallback', 'context_length_fallback')
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY name, metadata->>'original_model', metadata->>'fallback_model', DATE(created_at)
ORDER BY date DESC, total_fallbacks DESC;
```

**What it shows:**
- All fallback activity in one view
- Breakdown by fallback type
- Daily trends

### Query 4: Fallback Cost Impact

**Purpose:** Understand the cost of using fallback models

```sql
WITH fallback_traces AS (
    SELECT DISTINCT
        trace_id,
        name as fallback_type,
        metadata->>'original_model' as original_model,
        metadata->>'fallback_model' as fallback_model
    FROM events
    WHERE name IN ('rate_limit_fallback', 'context_length_fallback')
        AND created_at >= NOW() - INTERVAL '7 days'
)
SELECT
    ft.fallback_type,
    ft.original_model,
    ft.fallback_model,
    COUNT(DISTINCT ft.trace_id) as affected_traces,
    SUM(CAST(g.metadata->>'cost_usd' AS DECIMAL)) as total_cost,
    AVG(CAST(g.metadata->>'cost_usd' AS DECIMAL)) as avg_cost_per_request
FROM fallback_traces ft
JOIN generations g ON g.trace_id = ft.trace_id
WHERE g.metadata->>'cost_usd' IS NOT NULL
GROUP BY ft.fallback_type, ft.original_model, ft.fallback_model
ORDER BY total_cost DESC;
```

**What it shows:**
- Cost impact of each type of fallback
- Which fallbacks are most expensive
- Average cost increase per fallback

### Query 5: Fallback Success Rate

**Purpose:** See how often fallbacks succeed vs fail

```sql
WITH fallback_attempts AS (
    SELECT
        trace_id,
        name as fallback_type,
        metadata->>'original_model' as original_model,
        metadata->>'fallback_model' as fallback_model,
        created_at
    FROM events
    WHERE name IN ('rate_limit_fallback', 'context_length_fallback')
        AND created_at >= NOW() - INTERVAL '7 days'
),
generation_results AS (
    SELECT
        trace_id,
        COUNT(*) as generation_count,
        MAX(created_at) as last_generation
    FROM generations
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY trace_id
)
SELECT
    fa.fallback_type,
    fa.original_model,
    fa.fallback_model,
    COUNT(fa.trace_id) as total_fallbacks,
    COUNT(gr.trace_id) as successful_fallbacks,
    ROUND(100.0 * COUNT(gr.trace_id) / COUNT(fa.trace_id), 2) as success_rate_percent
FROM fallback_attempts fa
LEFT JOIN generation_results gr ON fa.trace_id = gr.trace_id
GROUP BY fa.fallback_type, fa.original_model, fa.fallback_model
ORDER BY total_fallbacks DESC;
```

**What it shows:**
- How often fallbacks lead to successful LLM calls
- Fallback reliability by model combination

## Python Code Examples

### Example 1: Query Fallback Events

```python
import langfuse
from datetime import datetime, timedelta

langfuse_client = langfuse.get_client()

# Get all fallback events from last 24 hours
end_time = datetime.now()
start_time = end_time - timedelta(days=1)

# Fetch events
events = langfuse_client.fetch_observations(
    type="event",
    name="rate_limit_fallback",  # or "context_length_fallback"
    start_time=start_time,
    end_time=end_time
)

# Analyze fallbacks
for event in events:
    print(f"Fallback: {event.metadata['original_model']} → {event.metadata['fallback_model']}")
```

### Example 2: Count Fallbacks by Type

```python
from collections import defaultdict

fallback_counts = defaultdict(lambda: defaultdict(int))

for event in events:
    original = event.metadata.get('original_model', 'unknown')
    fallback = event.metadata.get('fallback_model', 'unknown')
    fallback_counts[original][fallback] += 1

print("Fallback Summary:")
for original, fallbacks in fallback_counts.items():
    print(f"\n{original}:")
    for fallback, count in fallbacks.items():
        print(f"  → {fallback}: {count} times")
```

### Example 3: Calculate Fallback Rate

```python
# Get total requests
total_requests = auto_llm.stats["total_requests"]

# Get fallback requests
fallback_requests = auto_llm.stats["fallback_requests"]

# Calculate rate
fallback_rate = (fallback_requests / total_requests) * 100 if total_requests > 0 else 0

print(f"Fallback Rate: {fallback_rate:.2f}%")
print(f"Primary Model Usage: {100 - fallback_rate:.2f}%")
```

## Dashboard Recommendations

### Dashboard 1: Fallback Monitoring

**Purpose:** Real-time fallback tracking

**Widgets:**
1. **Fallbacks Over Time** (Line chart)
   - X-axis: Date/time
   - Y-axis: Number of fallbacks
   - Series: rate_limit_fallback, context_length_fallback

2. **Fallback Distribution** (Pie chart)
   - Slices: Each original_model → fallback_model combination
   - Values: Count of fallbacks

3. **Top Fallback Pairs** (Table)
   - Columns: Original Model, Fallback Model, Count, Avg Cost
   - Sorted by: Count descending

### Dashboard 2: Cost Impact

**Purpose:** Understand financial impact of fallbacks

**Widgets:**
1. **Cost by Fallback Type** (Bar chart)
   - X-axis: Fallback type
   - Y-axis: Total cost (USD)

2. **Cost Trend** (Line chart)
   - X-axis: Date
   - Y-axis: Cost (USD)
   - Series: Normal requests, Rate limit fallbacks, Context fallbacks

3. **Most Expensive Fallbacks** (Table)
   - Columns: Original → Fallback, Count, Total Cost, Avg Cost
   - Sorted by: Total Cost descending

### Dashboard 3: Performance Analysis

**Purpose:** Optimize fallback strategy

**Widgets:**
1. **Fallback Success Rate** (Gauge)
   - Value: % of fallbacks that succeeded
   - Threshold: Green >95%, Yellow 90-95%, Red <90%

2. **Latency Impact** (Box plot)
   - Compare latency: Normal requests vs Fallback requests

3. **Recommendations** (Text widget)
   - Auto-generated insights based on fallback patterns

## Alerts Configuration

### Alert 1: High Fallback Rate

```python
# Alert when fallback rate exceeds 20%
SELECT
    COUNT(*) as fallback_count,
    (SELECT COUNT(*) FROM generations WHERE created_at >= NOW() - INTERVAL '1 hour') as total_count
FROM events
WHERE name IN ('rate_limit_fallback', 'context_length_fallback')
    AND created_at >= NOW() - INTERVAL '1 hour'
HAVING (fallback_count::FLOAT / total_count) > 0.20;
```

### Alert 2: Expensive Fallback Pattern

```python
# Alert when fallbacks cost >$10 in last hour
SELECT
    SUM(CAST(g.metadata->>'cost_usd' AS DECIMAL)) as fallback_cost
FROM events e
JOIN generations g ON e.trace_id = g.trace_id
WHERE e.name IN ('rate_limit_fallback', 'context_length_fallback')
    AND e.created_at >= NOW() - INTERVAL '1 hour'
HAVING SUM(CAST(g.metadata->>'cost_usd' AS DECIMAL)) > 10.00;
```

### Alert 3: Context Limit Frequently Hit

```python
# Alert when >10 context fallbacks in 10 minutes
SELECT COUNT(*) as context_fallbacks
FROM events
WHERE name = 'context_length_fallback'
    AND created_at >= NOW() - INTERVAL '10 minutes'
HAVING COUNT(*) > 10;
```

## Best Practices

### 1. Regular Monitoring

- Check fallback dashboard daily
- Review weekly fallback patterns
- Investigate unexpected spikes

### 2. Cost Optimization

- If context fallbacks are frequent → consider using larger primary model
- If rate limit fallbacks are frequent → upgrade tier or add more fallbacks

### 3. Performance Tuning

- Monitor fallback latency impact
- Optimize fallback order (fastest/cheapest first)
- Consider pre-warming fallback models

### 4. Capacity Planning

- Use fallback trends to predict future needs
- Plan tier upgrades based on rate limit patterns
- Budget for fallback model costs

## Troubleshooting

### Issue: Too Many Rate Limit Fallbacks

**Symptoms:** High `rate_limit_fallback` event count

**Solutions:**
1. Upgrade API tier for higher limits
2. Add more fallback models
3. Implement request queuing/batching
4. Increase `max_wait_seconds` to wait instead of fallback

### Issue: Frequent Context Fallbacks

**Symptoms:** High `context_length_fallback` event count

**Solutions:**
1. Use larger primary model (e.g., gemini-2.5-pro)
2. Optimize input size (remove unnecessary context)
3. Implement input preprocessing/compression

### Issue: Fallbacks Failing

**Symptoms:** Low success rate from fallback query

**Solutions:**
1. Add more diverse fallback models
2. Check fallback model availability in tier
3. Verify fallback model configuration

## Summary

**Langfuse tracks TWO types of fallbacks:**

1. ✅ **Rate Limit Fallbacks** - When primary model hits API limits
2. ✅ **Context Length Fallbacks** - When input exceeds context window

**All fallback events include:**
- Original model name
- Fallback model name
- Reason for fallback
- Additional metadata (tokens, context limits, etc.)

**You can:**
- Query all fallback events via Langfuse API or SQL
- Create dashboards to visualize fallback patterns
- Set up alerts for fallback issues
- Analyze cost impact of fallbacks
- Optimize your fallback strategy based on data

Everything is automatically tracked with zero configuration needed!
