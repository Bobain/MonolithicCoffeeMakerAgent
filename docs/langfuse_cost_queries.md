# Langfuse Cost Tracking Queries

This document provides SQL queries and instructions for creating dashboards in Langfuse to visualize LLM costs.

## Overview

The AutoPickerLLM system automatically logs cost information to Langfuse with the following metadata:

- `cost_usd`: Total cost in USD
- `input_cost_usd`: Input token cost
- `output_cost_usd`: Output token cost
- `is_primary`: Whether primary or fallback model was used
- `latency_seconds`: Request latency

Additionally, usage information is logged:
- `input`: Input token count
- `output`: Output token count
- `total`: Total token count

## Dashboard Queries

### 1. Total Cost by Model

**Description**: Shows cumulative cost for each model over a time period.

**SQL Query**:
```sql
SELECT
    model,
    COUNT(*) as request_count,
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) as total_cost_usd,
    SUM(usage->>'input') as total_input_tokens,
    SUM(usage->>'output') as total_output_tokens,
    AVG(CAST(metadata->>'cost_usd' AS DECIMAL)) as avg_cost_per_request
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY model
ORDER BY total_cost_usd DESC;
```

**Usage**: Add this as a chart in Langfuse dashboard, visualize as bar chart.

---

### 2. Cost Over Time (Daily)

**Description**: Shows daily spending trends.

**SQL Query**:
```sql
SELECT
    DATE(created_at) as date,
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) as daily_cost_usd,
    COUNT(*) as request_count,
    SUM(usage->>'total') as total_tokens
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

**Usage**: Add as time series chart to track spending over time.

---

### 3. Primary vs Fallback Model Usage and Cost

**Description**: Compare primary model usage vs fallback usage.

**SQL Query**:
```sql
SELECT
    CASE
        WHEN metadata->>'is_primary' = 'true' THEN 'Primary'
        ELSE 'Fallback'
    END as model_type,
    COUNT(*) as request_count,
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) as total_cost_usd,
    AVG(CAST(metadata->>'latency_seconds' AS DECIMAL)) as avg_latency_sec,
    AVG(CAST(metadata->>'cost_usd' AS DECIMAL)) as avg_cost_per_request
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY model_type;
```

**Usage**: Visualize as pie chart or bar chart to understand fallback impact.

---

### 4. Most Expensive Requests

**Description**: Identify the most costly individual requests.

**SQL Query**:
```sql
SELECT
    id,
    model,
    CAST(metadata->>'cost_usd' AS DECIMAL) as cost_usd,
    usage->>'input' as input_tokens,
    usage->>'output' as output_tokens,
    metadata->>'is_primary' as is_primary,
    created_at
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '7 days'
ORDER BY cost_usd DESC
LIMIT 20;
```

**Usage**: Use as table view to investigate expensive requests.

---

### 5. Cost by Hour (for rate limiting analysis)

**Description**: Shows hourly cost patterns to understand peak usage.

**SQL Query**:
```sql
SELECT
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as request_count,
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) as hourly_cost_usd,
    SUM(usage->>'total') as total_tokens
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;
```

**Usage**: Line chart to identify usage patterns and rate limit triggers.

---

### 6. Token Efficiency Analysis

**Description**: Calculate cost per token for each model.

**SQL Query**:
```sql
SELECT
    model,
    COUNT(*) as request_count,
    SUM(usage->>'total') as total_tokens,
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) as total_cost_usd,
    (SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) / NULLIF(SUM(usage->>'total'), 0)) * 1000000 as cost_per_1m_tokens
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND usage->>'total' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY model
ORDER BY cost_per_1m_tokens DESC;
```

**Usage**: Table view to compare model efficiency.

---

### 7. Cumulative Cost (Running Total)

**Description**: Running total of costs over time.

**SQL Query**:
```sql
SELECT
    created_at,
    model,
    CAST(metadata->>'cost_usd' AS DECIMAL) as cost_usd,
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) OVER (ORDER BY created_at) as cumulative_cost_usd
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at;
```

**Usage**: Line chart showing cumulative spending.

---

### 8. Cost Distribution by Request Type

**Description**: Shows cost distribution across different percentiles.

**SQL Query**:
```sql
SELECT
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY CAST(metadata->>'cost_usd' AS DECIMAL)) as p50_cost,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY CAST(metadata->>'cost_usd' AS DECIMAL)) as p90_cost,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY CAST(metadata->>'cost_usd' AS DECIMAL)) as p95_cost,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY CAST(metadata->>'cost_usd' AS DECIMAL)) as p99_cost,
    MIN(CAST(metadata->>'cost_usd' AS DECIMAL)) as min_cost,
    MAX(CAST(metadata->>'cost_usd' AS DECIMAL)) as max_cost,
    AVG(CAST(metadata->>'cost_usd' AS DECIMAL)) as avg_cost
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '7 days';
```

**Usage**: Summary statistics for cost distribution.

---

## Recommended Dashboards

### Cost Monitoring Dashboard
Create a dashboard with:
1. **Total Cost by Model** (Bar chart)
2. **Cost Over Time** (Line chart)
3. **Primary vs Fallback** (Pie chart)
4. **Cumulative Cost** (Line chart)

### Performance Dashboard
Create a dashboard with:
1. **Token Efficiency Analysis** (Table)
2. **Cost by Hour** (Line chart)
3. **Most Expensive Requests** (Table)
4. **Cost Distribution** (Summary stats)

## Setting Budget Alerts

You can create alerts in Langfuse based on these queries:

### Daily Budget Alert
```sql
SELECT
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) as daily_cost
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= CURRENT_DATE
HAVING SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) > 10.00;  -- Alert if > $10/day
```

### Hourly Spike Alert
```sql
SELECT
    DATE_TRUNC('hour', created_at) as hour,
    SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) as hourly_cost
FROM generations
WHERE metadata->>'cost_usd' IS NOT NULL
    AND created_at >= NOW() - INTERVAL '1 hour'
GROUP BY DATE_TRUNC('hour', created_at)
HAVING SUM(CAST(metadata->>'cost_usd' AS DECIMAL)) > 2.00;  -- Alert if > $2/hour
```

## Python Code to Fetch Cost Data

You can also fetch cost data programmatically:

```python
import langfuse
from datetime import datetime, timedelta

langfuse_client = langfuse.get_client()

# Get cost stats for last 24 hours
end_time = datetime.now()
start_time = end_time - timedelta(days=1)

generations = langfuse_client.get_generations(
    start_time=start_time,
    end_time=end_time,
    limit=1000
)

total_cost = 0
model_costs = {}

for gen in generations:
    if gen.metadata and 'cost_usd' in gen.metadata:
        cost = float(gen.metadata['cost_usd'])
        total_cost += cost

        model = gen.model
        if model not in model_costs:
            model_costs[model] = 0
        model_costs[model] += cost

print(f"Total cost (24h): ${total_cost:.4f}")
print("\nCost by model:")
for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True):
    print(f"  {model}: ${cost:.4f}")
```

## Integration with CostCalculator

The `CostCalculator` class provides its own analytics:

```python
from coffee_maker.langchain_observe.cost_calculator import CostCalculator

# Get comprehensive stats
stats = cost_calculator.get_cost_stats(timeframe="day")
print(f"Total cost (24h): ${stats['total_cost_usd']:.4f}")
print(f"Total requests: {stats['total_requests']}")
print(f"Average cost/request: ${stats['average_cost_per_request']:.4f}")

# Get cost by model
cost_by_model = cost_calculator.get_cost_by_model(timeframe="day")
for model, cost in cost_by_model.items():
    print(f"{model}: ${cost:.4f}")

# Get recent cost records
recent_costs = cost_calculator.get_recent_costs(limit=10)
for record in recent_costs:
    print(f"{record.model}: ${record.total_cost:.4f} at {record.timestamp}")
```

---

### 9. Rate Limit Fallback Tracking

**Description**: Track when rate limits cause fallback to alternative models.

**SQL Query**:
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

**Usage**: Identify rate limit bottlenecks and when fallback models are being used.

---

### 10. Context Length Fallback Tracking

**Description**: Track when inputs exceed context limits and require fallback to larger models.

**SQL Query**:
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

**Usage**: Identify which models frequently hit context limits and require larger-context fallbacks.

---

### 11. All Fallbacks Summary

**Description**: Combined view of all types of fallbacks (rate limit + context length).

**SQL Query**:
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

**Usage**: Get a complete picture of all fallback activity across your system.

---

### 12. Context Fallback Impact on Costs

**Description**: Analyze cost impact of context fallback (larger models are usually more expensive).

**SQL Query**:
```sql
WITH fallback_traces AS (
    SELECT DISTINCT
        trace_id,
        metadata->>'original_model' as original_model,
        metadata->>'fallback_model' as fallback_model
    FROM events
    WHERE name = 'context_length_fallback'
        AND created_at >= NOW() - INTERVAL '7 days'
)
SELECT
    ft.original_model,
    ft.fallback_model,
    COUNT(DISTINCT ft.trace_id) as affected_traces,
    SUM(CAST(g.metadata->>'cost_usd' AS DECIMAL)) as total_cost,
    AVG(CAST(g.metadata->>'cost_usd' AS DECIMAL)) as avg_cost_per_request
FROM fallback_traces ft
JOIN generations g ON g.trace_id = ft.trace_id
WHERE g.metadata->>'cost_usd' IS NOT NULL
GROUP BY ft.original_model, ft.fallback_model
ORDER BY total_cost DESC;
```

**Usage**: Understand the cost implications of context fallback decisions.

---

## Notes

- All cost calculations are based on per-1M-token pricing from `MODEL_CONFIGS`
- Free-tier models (e.g., `gemini-2.5-flash-lite`) report $0.00 cost
- Costs are logged in real-time as LLM requests are made
- The AutoPickerLLM automatically logs to Langfuse when `langfuse_client` is provided
- Cost data is stored in Langfuse generation metadata for historical analysis
- Context fallback events are logged as separate events with full metadata
