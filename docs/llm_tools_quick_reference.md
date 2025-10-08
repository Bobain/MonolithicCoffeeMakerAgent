# LLM Tools Quick Reference

## Available Tools

| Tool Name | Purpose | Primary Model | Best For |
|-----------|---------|---------------|----------|
| `invoke_llm_openai_long_context` | Long context | gpt-4o (128K) | Files > 10K lines |
| `invoke_llm_gemini_long_context` | Long context | gemini-2.0-pro (1M) | Very large files |
| `invoke_llm_openai_fast` | Fast | gpt-4o-mini | Quick checks |
| `invoke_llm_gemini_fast` | Fast | gemini-2.5-flash-lite | Speed priority |
| `invoke_llm_openai_accurate` | Accurate | gpt-4o | Complex analysis |
| `invoke_llm_gemini_accurate` | Accurate | gemini-2.0-pro | Critical review |
| `invoke_llm_openai_budget` | Budget | gpt-4o-mini | Cost sensitive |
| `invoke_llm_gemini_budget` | Budget | gemini-2.5-flash-lite | Batch processing |
| `invoke_llm_openai_second_best_model` | Balanced | gpt-4o | General purpose |
| `invoke_llm_gemini_second_best_model` | Balanced | gemini-2.5-flash | General purpose |

## When to Use

### By File Size
- **< 1K lines**: Use `fast` or `budget`
- **1K - 10K lines**: Use `second_best_model`
- **10K - 50K lines**: Use `long_context` (OpenAI)
- **> 50K lines**: Use `long_context` (Gemini)

### By Task Complexity
- **Simple syntax check**: `fast` or `budget`
- **Code review**: `second_best_model`
- **Complex algorithm**: `accurate`
- **Architecture analysis**: `accurate` with `long_context`

### By Priority
- **Speed**: `fast`
- **Cost**: `budget`
- **Quality**: `accurate`
- **Balance**: `second_best_model`

## Input Format

All tools use the same input format:

```json
{
    "task_description": "Your task description and code here"
}
```

## Example Usage in ReAct Agent

### Setup
```python
from coffee_maker.code_formatter.agents import create_react_formatter_agent

react_agent, tools, llm = create_react_formatter_agent(
    langfuse_client=langfuse_client,
    llm=auto_picker_llm,
    include_llm_tools=True,  # Enable LLM tools
    tier="tier1"
)
```

### Agent Thought Process
```
Question: Review PR #123

Thought: Need to get modified files first
Action: get_pr_modified_files
Observation: {"python_files": ["big_file.py", "utils.py"]}

Thought: big_file.py is 15K lines, need long context model
Action: invoke_llm_openai_long_context
Action Input: {"task_description": "Review this large file: <content>"}
Observation: Found 3 issues...

Thought: utils.py is small, use fast model
Action: invoke_llm_gemini_fast
Action Input: {"task_description": "Quick review: <content>"}
Observation: Looks good...

Thought: Post suggestions
Action: post_suggestion_in_pr_review
...
```

## Programmatic Access

### Get Tool List
```python
from coffee_maker.langchain_observe.llm_tools import get_llm_tool_names

tool_names = get_llm_tool_names()
# Returns: ['invoke_llm_openai_long_context', ...]
```

### Get Tool Summary
```python
from coffee_maker.langchain_observe.llm_tools import get_llm_tools_summary

summary = get_llm_tools_summary()
# Returns: {'long_context': {'openai': {...}, 'gemini': {...}}, ...}
```

### Create Specific Tool
```python
from coffee_maker.langchain_observe.llm_tools import create_llm_tool_wrapper
from coffee_maker.langchain_observe.llm_config import get_rate_limits_for_tier
from coffee_maker.langchain_observe.rate_limiter import RateLimitTracker

rate_limits = get_rate_limits_for_tier("tier1")
rate_tracker = RateLimitTracker(rate_limits)

llm = create_llm_tool_wrapper(
    purpose="long_context",
    provider="openai",
    rate_tracker=rate_tracker,
    tier="tier1"
)

response = llm.invoke({"input": "Analyze this code..."})
```

## Decision Matrix

| Scenario | Recommended Tool | Reason |
|----------|-----------------|---------|
| 20K line file | `invoke_llm_openai_long_context` | Needs 128K context |
| 100K line file | `invoke_llm_gemini_long_context` | Needs 1M context |
| Syntax validation | `invoke_llm_gemini_fast` | Simple task, speed matters |
| Critical algorithm | `invoke_llm_openai_accurate` | Accuracy critical |
| Batch of 100 files | `invoke_llm_gemini_budget` | Cost optimization |
| General review | `invoke_llm_openai_second_best_model` | Balanced approach |

## Provider Comparison

| Feature | OpenAI | Gemini |
|---------|--------|--------|
| Max context | 128K (gpt-4o) | 1M (gemini-2.0-pro) |
| Fastest model | gpt-4o-mini | gemini-2.5-flash-lite |
| Most accurate | gpt-4o | gemini-2.0-pro |
| Best for budget | gpt-4o-mini | gemini-2.5-flash-lite |
| Rate limits (tier1) | 500 RPM, 200K TPM | 1000 RPM, 4M TPM |

## Configuration

### Enable/Disable LLM Tools
```python
# Enable (default)
react_agent, tools, llm = create_react_formatter_agent(
    ...,
    include_llm_tools=True
)

# Disable
react_agent, tools, llm = create_react_formatter_agent(
    ...,
    include_llm_tools=False
)
```

### Change API Tier
```python
# Tier 1 (default)
llm_tools = create_llm_tools(tier="tier1")

# Tier 2 (higher limits)
llm_tools = create_llm_tools(tier="tier2")

# Free tier
llm_tools = create_llm_tools(tier="free")
```

## Error Handling

All tools include:
- ✓ Automatic fallback on rate limits
- ✓ Rate limit tracking and waiting
- ✓ Error logging and recovery
- ✓ Token estimation for requests

## Demo

Run the demo script to see all tools in action:
```bash
poetry run python examples/llm_tools_demo.py
```

## Documentation

- Full guide: `docs/llm_tools_usage.md`
- Implementation details: `docs/llm_tools_implementation_summary.md`
- This quick reference: `docs/llm_tools_quick_reference.md`
