# LLM Rate Limiting, Cost Optimization & Intelligent Fallback Plan

## Executive Summary

This document outlines a comprehensive plan to build a robust ReAct agent system that:
1. **Prevents API limit failures** (requests/minute, tokens/minute, context length)
2. **Optimizes costs** by intelligently selecting appropriate models
3. **Tracks and reports spending** to Langfuse for visibility
4. **Provides automatic fallback** when limits are reached

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ReAct Agent                              │
│  ┌───────────────────────────────────────────────────┐      │
│  │         Smart LLM Router/Manager                  │      │
│  │  - Rate limit tracking                            │      │
│  │  - Cost calculation                               │      │
│  │  - Model selection                                │      │
│  │  - Automatic fallback                             │      │
│  └───────────────────────────────────────────────────┘      │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ Primary LLM  │ Fallback LLM │ Budget LLM   │            │
│  │ (gpt-4o)     │ (gpt-4o-mini)│ (gemini-flash)│           │
│  │ High quality │ Mid quality  │ Low cost     │            │
│  └──────────────┴──────────────┴──────────────┘            │
│           │                                                  │
│           ▼                                                  │
│  ┌───────────────────────────────────────────────────┐      │
│  │         Langfuse Cost Tracking                    │      │
│  │  - Token usage per model                          │      │
│  │  - Cost per request                               │      │
│  │  - Daily/hourly spend                             │      │
│  └───────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Rate Limit Tracker (`coffee_maker/langchain_observe/rate_limiter.py`)

**Purpose**: Track API usage in real-time to prevent hitting rate limits

**Key Features**:
- Track requests per minute per model
- Track tokens per minute per model
- Track daily request counts
- Sliding window algorithm for accurate rate limiting
- Thread-safe implementation

**Implementation**:
```python
class RateLimitTracker:
    """Track API rate limits for multiple models."""

    def __init__(self, model_limits: dict):
        """
        Args:
            model_limits: Dict of model -> limits
              Example: {
                "gpt-4o": {
                  "requests_per_minute": 5000,
                  "tokens_per_minute": 800000,
                  "requests_per_day": 10000
                }
              }
        """

    def can_make_request(self, model: str, estimated_tokens: int) -> bool:
        """Check if request can be made without hitting limits."""

    def record_request(self, model: str, tokens_used: int):
        """Record a completed request."""

    def get_wait_time(self, model: str, estimated_tokens: int) -> float:
        """Get seconds to wait before next request is allowed."""

    def get_usage_stats(self, model: str) -> dict:
        """Get current usage statistics."""
```

### 2. Cost Calculator (`coffee_maker/langchain_observe/cost_calculator.py`)

**Purpose**: Calculate costs for each request and track cumulative spending

**Implementation**:
```python
class CostCalculator:
    """Calculate and track LLM API costs."""

    def __init__(self, pricing_info: dict):
        """
        Args:
            pricing_info: Dict from llm_providers/*.py files
              Contains per-model pricing per 1M tokens
        """

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> dict:
        """
        Calculate cost for a request.

        Returns:
            {
              "input_cost": float,
              "output_cost": float,
              "total_cost": float,
              "currency": "USD"
            }
        """

    def get_cumulative_cost(
        self,
        model: str = None,
        timeframe: str = "day"
    ) -> float:
        """Get total spending (optionally filtered by model/timeframe)."""
```

### 3. Smart LLM Wrapper (`coffee_maker/langchain_observe/smart_llm.py`)

**Purpose**: Wrap LLM instances with intelligent rate limiting and fallback

**Key Features**:
- Automatic rate limit detection
- Intelligent model selection based on task
- Automatic fallback to cheaper/faster models
- Cost tracking and reporting
- Context length management

**Implementation**:
```python
class SmartLLM:
    """Intelligent LLM wrapper with rate limiting and fallback."""

    def __init__(
        self,
        primary_llm,
        fallback_llms: list,
        rate_tracker: RateLimitTracker,
        cost_calculator: CostCalculator,
        langfuse_client,
        context_strategy: str = "auto"
    ):
        """
        Args:
            primary_llm: Main LLM to use
            fallback_llms: List of fallback LLMs (in priority order)
            rate_tracker: Rate limit tracker instance
            cost_calculator: Cost calculator instance
            langfuse_client: Langfuse client for tracking
            context_strategy: How to handle context length
              - "auto": Automatically truncate/split
              - "error": Raise error if too long
              - "fallback": Use model with larger context
        """

    def invoke(self, input_data: dict, **kwargs):
        """
        Invoke LLM with intelligent fallback.

        Process:
        1. Estimate tokens in input
        2. Check rate limits for primary model
        3. If limit reached, wait or use fallback
        4. If context too large, truncate or use larger model
        5. Make request
        6. Calculate and log cost to Langfuse
        7. Return result
        """

    def estimate_tokens(self, text: str, model: str = None) -> int:
        """Estimate token count for text."""

    def _select_model_for_context(
        self,
        estimated_tokens: int
    ) -> tuple[Any, str]:
        """Select appropriate model based on context length."""

    def _handle_rate_limit(
        self,
        model_name: str,
        estimated_tokens: int
    ):
        """Handle rate limit by waiting or using fallback."""
```

### 4. Model Configuration (`coffee_maker/langchain_observe/llm_config.py`)

**Purpose**: Centralized configuration for all available models

**Implementation**:
```python
MODEL_CONFIGS = {
    "openai": {
        "gpt-4o": {
            "context_length": 128000,
            "max_output_tokens": 4096,
            "rate_limits": {
                "free": None,  # Not available on free tier
                "tier1": {
                    "requests_per_minute": 500,
                    "tokens_per_minute": 30000,
                    "requests_per_day": 10000
                },
                "tier2": {
                    "requests_per_minute": 5000,
                    "tokens_per_minute": 450000,
                    "requests_per_day": 10000
                }
            },
            "pricing": {
                "input_per_1m": 2.50,
                "output_per_1m": 10.00
            },
            "use_cases": ["complex_reasoning", "code_review", "primary"]
        },
        "gpt-4o-mini": {
            "context_length": 128000,
            "max_output_tokens": 16384,
            "rate_limits": {
                "free": None,
                "tier1": {
                    "requests_per_minute": 500,
                    "tokens_per_minute": 200000,
                    "requests_per_day": 10000
                }
            },
            "pricing": {
                "input_per_1m": 0.150,
                "output_per_1m": 0.600
            },
            "use_cases": ["general", "fallback", "budget"]
        }
    },
    "gemini": {
        "gemini-2.5-flash-lite": {
            "context_length": 1048576,  # 1M tokens!
            "max_output_tokens": 8192,
            "rate_limits": {
                "free": {
                    "requests_per_minute": 15,
                    "tokens_per_minute": 250000,
                    "requests_per_day": 1000
                },
                "paid": {
                    "requests_per_minute": -1,  # Unlimited
                    "tokens_per_minute": -1
                }
            },
            "pricing": {
                "free_tier": True,
                "input_per_1m": 0.10,
                "output_per_1m": 0.40
            },
            "use_cases": ["large_context", "budget", "fallback"]
        }
    }
}
```

### 5. Langfuse Integration (`coffee_maker/langchain_observe/langfuse_tracker.py`)

**Purpose**: Report costs and usage to Langfuse for visibility

**Implementation**:
```python
class LangfuseCostTracker:
    """Track and report costs to Langfuse."""

    def __init__(self, langfuse_client):
        self.client = langfuse_client

    def log_llm_usage(
        self,
        trace_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: dict,
        latency_ms: float,
        success: bool,
        error: str = None
    ):
        """
        Log LLM usage to Langfuse.

        Creates a generation event with:
        - Model name
        - Token counts
        - Cost breakdown
        - Latency
        - Success/failure status
        """
        self.client.generation(
            trace_id=trace_id,
            name=f"llm_call_{model}",
            model=model,
            usage={
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens,
                "unit": "TOKENS"
            },
            metadata={
                "cost_usd": cost["total_cost"],
                "cost_breakdown": cost,
                "latency_ms": latency_ms,
                "success": success,
                "error": error
            }
        )

    def create_cost_dashboard_query(self):
        """
        Return SQL/query for Langfuse dashboard showing:
        - Total cost by model
        - Cost over time
        - Cost per trace
        - Average cost per request
        """
```

## Integration with ReAct Agent

### Modified Agent Creation

```python
def create_smart_react_formatter_agent(
    langfuse_client: Langfuse,
    tier: str = "tier1",  # or "free", "tier2"
    budget_limit_usd: float = None
) -> tuple:
    """
    Create ReAct agent with intelligent LLM management.

    Args:
        langfuse_client: Langfuse client for tracking
        tier: API tier for rate limiting
        budget_limit_usd: Optional daily budget limit

    Returns:
        (agent, tools, llm_manager)
    """

    # 1. Load model configurations
    from coffee_maker.langchain_observe.llm_config import MODEL_CONFIGS

    # 2. Initialize rate tracker
    rate_tracker = RateLimitTracker(
        model_limits={
            model: config["rate_limits"][tier]
            for provider in MODEL_CONFIGS.values()
            for model, config in provider.items()
            if tier in config["rate_limits"]
        }
    )

    # 3. Initialize cost calculator
    cost_calculator = CostCalculator(
        pricing_info={
            model: config["pricing"]
            for provider in MODEL_CONFIGS.values()
            for model, config in provider.items()
        }
    )

    # 4. Create LLM instances
    primary_llm = get_llm(provider="openai", model="gpt-4o-mini", streaming=True)
    fallback_llms = [
        get_llm(provider="gemini", model="gemini-2.5-flash-lite", streaming=True),
        get_llm(provider="openai", model="gpt-3.5-turbo", streaming=True)
    ]

    # 5. Wrap in SmartLLM
    smart_llm = SmartLLM(
        primary_llm=primary_llm,
        fallback_llms=fallback_llms,
        rate_tracker=rate_tracker,
        cost_calculator=cost_calculator,
        langfuse_client=langfuse_client,
        context_strategy="auto"
    )

    # 6. Create agent with smart LLM
    agent, tools = create_react_formatter_agent(langfuse_client, smart_llm)

    return agent, tools, smart_llm
```

## Advanced Features

### 1. Context Length Management

**Strategy 1: Automatic Truncation**
- Truncate input to fit within context window
- Preserve most important parts (beginning + end)
- Log truncation to Langfuse

**Strategy 2: Model Fallback**
- If input too large for primary model
- Automatically use model with larger context (e.g., Gemini Flash with 1M tokens)
- Log model switch to Langfuse

**Strategy 3: Chunking**
- Split large inputs into chunks
- Process chunks sequentially
- Combine results

### 2. Budget Management

```python
class BudgetManager:
    """Manage daily/monthly spending limits."""

    def __init__(
        self,
        daily_limit_usd: float = None,
        monthly_limit_usd: float = None
    ):
        pass

    def check_budget(self, estimated_cost: float) -> bool:
        """Check if request would exceed budget."""

    def get_remaining_budget(self, timeframe: str = "day") -> float:
        """Get remaining budget."""

    def alert_budget_exceeded(self):
        """Send alert when budget limit reached."""
```

### 3. Intelligent Model Selection

```python
def select_model_for_task(
    task_type: str,
    input_length: int,
    budget_remaining: float,
    quality_preference: str = "balanced"
) -> str:
    """
    Select optimal model based on:
    - Task type (code_review, simple_query, complex_reasoning)
    - Input length (context requirements)
    - Budget constraints
    - Quality preferences (speed/cost/quality)

    Returns:
        model_name: str
    """

    # Example logic:
    if task_type == "code_review":
        if input_length > 50000:
            return "gemini-2.5-flash-lite"  # Large context
        elif quality_preference == "quality":
            return "gpt-4o"
        else:
            return "gpt-4o-mini"
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Create `RateLimitTracker` class
- [ ] Create `CostCalculator` class
- [ ] Create `MODEL_CONFIGS` centralized configuration
- [ ] Write unit tests for rate limiting logic

### Phase 2: Smart LLM Wrapper (Week 2)
- [ ] Implement `SmartLLM` wrapper class
- [ ] Add token estimation
- [ ] Add automatic fallback logic
- [ ] Add context length management
- [ ] Integration tests

### Phase 3: Langfuse Integration (Week 2)
- [ ] Create `LangfuseCostTracker` class
- [ ] Log costs to Langfuse
- [ ] Create Langfuse dashboard queries
- [ ] Add cost visualization

### Phase 4: ReAct Agent Integration (Week 3)
- [ ] Modify `create_react_formatter_agent`
- [ ] Update main.py to use smart agent
- [ ] End-to-end testing
- [ ] Documentation

### Phase 5: Advanced Features (Week 4)
- [ ] Implement `BudgetManager`
- [ ] Add intelligent model selection
- [ ] Add alerting for budget/limits
- [ ] Performance optimization

## Usage Examples

### Example 1: Basic Usage with Auto-Fallback

```python
# Create smart agent with automatic fallback
agent, tools, llm_manager = create_smart_react_formatter_agent(
    langfuse_client=langfuse_client,
    tier="free",  # Use free tier limits
    budget_limit_usd=5.00  # Daily budget limit
)

# Agent automatically:
# - Checks rate limits before each call
# - Falls back to cheaper models if limits reached
# - Tracks costs to Langfuse
# - Manages context length
response = agent_executor.invoke({"input": "Review PR #123"})
```

### Example 2: Get Cost Report

```python
# Get spending report
stats = llm_manager.get_usage_stats()
print(f"Total spent today: ${stats['total_cost_usd']:.2f}")
print(f"Requests made: {stats['total_requests']}")
print(f"By model:")
for model, cost in stats['cost_by_model'].items():
    print(f"  {model}: ${cost:.2f}")
```

### Example 3: Manual Model Selection

```python
# Force use of budget model for simple tasks
llm_manager.set_model_preference(
    task_type="simple_query",
    preferred_model="gpt-4o-mini"
)

# Use high-quality model for complex reasoning
llm_manager.set_model_preference(
    task_type="code_review",
    preferred_model="gpt-4o"
)
```

## Monitoring & Alerting

### Langfuse Dashboard Metrics

1. **Cost Metrics**:
   - Total cost (daily/weekly/monthly)
   - Cost per model
   - Cost per trace/session
   - Average cost per request

2. **Usage Metrics**:
   - Requests per minute/hour/day
   - Tokens per minute/hour/day
   - Context length distribution
   - Fallback frequency

3. **Performance Metrics**:
   - Average latency per model
   - Success rate
   - Error rate
   - Rate limit hit frequency

### Alerts

- Budget threshold reached (e.g., 80% of daily limit)
- Rate limit hit multiple times
- High error rate
- Unusual spending patterns

## Benefits

1. **Cost Optimization**:
   - Automatically use cheapest model that meets requirements
   - Track spending in real-time
   - Set budget limits

2. **Reliability**:
   - Never hit rate limits unexpectedly
   - Automatic fallback prevents failures
   - Graceful degradation

3. **Visibility**:
   - All costs tracked in Langfuse
   - Detailed metrics and dashboards
   - Easy to optimize spending

4. **Flexibility**:
   - Support for multiple providers (OpenAI, Gemini, etc.)
   - Easy to add new models
   - Configurable strategies

## Future Enhancements

1. **Smart Caching**: Cache repeated queries to save costs
2. **Prompt Optimization**: Automatically compress prompts to reduce tokens
3. **Batch Processing**: Group multiple requests when possible
4. **Predictive Rate Limiting**: Predict when limits will be hit
5. **Cost-Based Routing**: Route to cheapest available model in real-time
6. **A/B Testing**: Test different models for same task, track quality vs. cost

## References

- OpenAI Rate Limits: https://platform.openai.com/docs/guides/rate-limits
- Gemini Rate Limits: https://ai.google.dev/gemini-api/docs/rate-limits
- Langfuse Documentation: https://langfuse.com/docs
- Token Counting: https://github.com/openai/tiktoken
