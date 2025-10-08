# LLM Tools for ReAct Agent

## Overview

The LLM tools system provides the ReAct agent with the ability to delegate tasks to specialized LLM models based on specific requirements (purpose) and provider preferences. This allows the agent to intelligently select the right model for each subtask.

## Available Purposes

### 1. **long_context**
Use when dealing with very large files or contexts.

- **OpenAI**: gpt-4o (128K context) → fallback: gpt-4o-mini
- **Gemini**: gemini-2.0-pro (1M context) → fallback: gemini-2.5-flash

### 2. **second_best_model**
Balanced performance and cost for general tasks.

- **OpenAI**: gpt-4o → fallback: gpt-4o-mini
- **Gemini**: gemini-2.5-flash → fallback: gemini-2.5-flash-lite

### 3. **fast**
Optimized for speed and quick analysis.

- **OpenAI**: gpt-4o-mini → fallback: gpt-3.5-turbo
- **Gemini**: gemini-2.5-flash-lite → fallback: gemini-2.5-flash

### 4. **accurate**
Maximum accuracy for complex analysis.

- **OpenAI**: gpt-4o → fallback: gpt-4o-mini
- **Gemini**: gemini-2.0-pro → fallback: gemini-2.5-flash

### 5. **budget**
Cost-optimized for simple tasks.

- **OpenAI**: gpt-4o-mini → fallback: gpt-3.5-turbo
- **Gemini**: gemini-2.5-flash-lite → fallback: gemini-2.5-flash

## Tool Names

The tools follow the naming pattern: `invoke_llm_{provider}_{purpose}`

Examples:
- `invoke_llm_openai_long_context`
- `invoke_llm_gemini_fast`
- `invoke_llm_openai_accurate`
- `invoke_llm_gemini_budget`
- `invoke_llm_openai_second_best_model`

## How the ReAct Agent Uses LLM Tools

The ReAct agent can use these tools to delegate specific analysis tasks:

### Example 1: Analyzing a Large File

```
Thought: This file is 15,000 lines long, I need a model with large context window
Action: invoke_llm_openai_long_context
Action Input: {"task_description": "Analyze this large Python file and identify all code quality issues: <file content>"}
Observation: <LLM response with analysis>
```

### Example 2: Quick Syntax Check

```
Thought: I just need to check if this code has syntax errors, use fast model
Action: invoke_llm_gemini_fast
Action Input: {"task_description": "Check this Python code for syntax errors: <code>"}
Observation: <LLM response>
```

### Example 3: Complex Code Review

```
Thought: This is complex business logic, need accurate analysis
Action: invoke_llm_openai_accurate
Action Input: {"task_description": "Review this complex algorithm for correctness and edge cases: <code>"}
Observation: <LLM response>
```

## Integration in Code

### Creating LLM Tools

```python
from coffee_maker.langchain_observe.llm_tools import create_llm_tools

# Create all LLM tools for tier1 API limits
llm_tools = create_llm_tools(tier="tier1")

# Add to your ReAct agent tools
all_tools = github_tools + llm_tools
```

### Using in ReAct Agent Creation

```python
from coffee_maker.code_formatter.agents import create_react_formatter_agent

# Create agent with LLM tools enabled
react_agent, tools, llm = create_react_formatter_agent(
    langfuse_client=langfuse_client,
    llm=base_llm,
    use_auto_picker=False,
    tier="tier1",
    include_llm_tools=True  # Enable LLM tools
)
```

### Disabling LLM Tools

```python
# Create agent without LLM tools
react_agent, tools, llm = create_react_formatter_agent(
    langfuse_client=langfuse_client,
    llm=base_llm,
    include_llm_tools=False  # Disable LLM tools
)
```

## Tool Input Format

All LLM tools expect a JSON input with a `task_description` field:

```json
{
    "task_description": "The task or prompt to send to the LLM"
}
```

The task_description should contain:
1. Clear instructions for the LLM
2. The code or content to analyze
3. Specific questions or requirements

## Rate Limiting

Each LLM tool uses the AutoPickerLLM wrapper, which means:
- Rate limits are tracked per model
- Automatic fallback when primary model is rate-limited
- Can auto-wait if wait time is acceptable
- Shared rate tracker across all tools prevents exceeding API limits

## Programmatic Usage

### Get Tool Summary

```python
from coffee_maker.langchain_observe.llm_tools import get_llm_tools_summary

summary = get_llm_tools_summary()
# Returns dict with all purposes, providers, and model configurations
```

### Get Tool Names

```python
from coffee_maker.langchain_observe.llm_tools import get_llm_tool_names

names = get_llm_tool_names()
# Returns list of all tool names
```

### Create Specific Tool Wrapper

```python
from coffee_maker.langchain_observe.llm_tools import create_llm_tool_wrapper
from coffee_maker.langchain_observe.rate_limiter import RateLimitTracker
from coffee_maker.langchain_observe.llm_config import get_rate_limits_for_tier

# Create rate tracker
rate_limits = get_rate_limits_for_tier("tier1")
rate_tracker = RateLimitTracker(rate_limits)

# Create specific tool wrapper
llm = create_llm_tool_wrapper(
    purpose="long_context",
    provider="openai",
    rate_tracker=rate_tracker,
    tier="tier1"
)

# Use directly
response = llm.invoke({"input": "Analyze this code..."})
```

## Decision Guide for Agent

When the agent needs to choose which LLM tool to use:

| Task Characteristics | Recommended Purpose | Why |
|---------------------|---------------------|-----|
| File > 10K lines | `long_context` | Need large context window |
| Complex algorithm | `accurate` | Need highest quality analysis |
| Simple syntax check | `fast` | Speed is priority |
| Batch processing | `budget` | Cost optimization |
| General review | `second_best_model` | Balanced performance |

| Provider Preference | When to Use |
|--------------------|-------------|
| OpenAI | - Need deterministic output<br>- JSON mode required<br>- Proven reliability |
| Gemini | - Very large context (1M tokens)<br>- Cost sensitive<br>- High throughput |

## Example: ReAct Agent Decision Process

```
Question: Review PR #123 in repository owner/repo

Thought: First, I need to get the list of modified files
Action: get_pr_modified_files
Action Input: {"repo_full_name": "owner/repo", "pr_number": 123}
Observation: {"python_files": ["app.py", "utils.py", "big_file.py"], "total_files": 3}

Thought: big_file.py might be large, let me check its content
Action: get_pr_file_content
Action Input: {"repo_full_name": "owner/repo", "pr_number": 123, "file_path": "big_file.py"}
Observation: <15,000 lines of code>

Thought: This file is very large, I should use a long context model for analysis
Action: invoke_llm_openai_long_context
Action Input: {"task_description": "Review this large Python file for code quality issues according to the style guide: <content>"}
Observation: Found 5 issues: ...

Thought: Now I'll post the suggestions
Action: post_suggestion_in_pr_review
...
```

## Benefits

1. **Optimized Cost**: Use budget models for simple tasks, expensive models only when needed
2. **Better Performance**: Fast models for quick checks, accurate models for complex analysis
3. **Scalability**: Handle large files with long-context models
4. **Reliability**: Automatic fallback prevents failures
5. **Flexibility**: Agent can choose the right tool for each specific task
