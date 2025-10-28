# Runtime Context Validation

**Status**: Proposed
**Created**: 2025-10-28
**Priority**: High

---

## Problem Statement

Current CFR-018 budget enforcement uses **line counting**, which is highly inaccurate:
- Lines vary from 10-200 characters
- No correlation to actual LLM token usage
- Over-conservative estimates (480 lines ≈ 9,600 tokens vs 60K budget)

**User feedback**:
> "Shouldn't the context size be estimated with number of words rather than number of lines?"
> "Is it possible to measure at runtime the number of tokens we sent to an agent?"

**Answer**: YES! We should measure actual token usage at runtime.

---

## Proposed Solution

### 1. Token Counting (Pre-Execution)

Use Anthropic's tokenizer to count tokens BEFORE sending to API:

```python
from anthropic import Anthropic

def count_tokens(text: str, model: str = "claude-sonnet-4.0") -> int:
    """Count tokens in text using Anthropic's tokenizer.

    Args:
        text: The text to tokenize
        model: The model to use for tokenization

    Returns:
        Number of tokens
    """
    client = Anthropic()
    # Anthropic provides token counting via their API
    # Or use tiktoken for OpenAI-compatible counting
    return client.count_tokens(text)


def validate_context_budget(
    command_text: str,
    agent_readme: str,
    auto_skills: str = "",
    max_tokens: int = 60_000  # 30% of 200K
) -> dict:
    """Validate that context fits within budget.

    Returns:
        {
            "command_tokens": int,
            "readme_tokens": int,
            "skills_tokens": int,
            "total_tokens": int,
            "budget_tokens": int,
            "usage_percent": float,
            "within_budget": bool
        }
    """
    command_tokens = count_tokens(command_text)
    readme_tokens = count_tokens(agent_readme)
    skills_tokens = count_tokens(auto_skills)

    total = command_tokens + readme_tokens + skills_tokens
    usage_percent = (total / max_tokens) * 100

    return {
        "command_tokens": command_tokens,
        "readme_tokens": readme_tokens,
        "skills_tokens": skills_tokens,
        "total_tokens": total,
        "budget_tokens": max_tokens,
        "usage_percent": usage_percent,
        "within_budget": total <= max_tokens
    }
```

### 2. Runtime Tracking (Post-Execution)

Capture actual token usage from API response:

```python
from anthropic import Anthropic
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def execute_command_with_tracking(
    agent_type: str,
    command_name: str,
    prompt: str,
    **kwargs
) -> Dict[str, Any]:
    """Execute command and track actual token usage.

    Returns:
        {
            "result": command result,
            "tokens": {
                "input": actual input tokens,
                "output": actual output tokens,
                "total": total tokens used,
                "estimated_input": pre-execution estimate,
                "accuracy": estimate vs actual %
            }
        }
    """
    # 1. Pre-execution: Estimate input tokens
    estimated_input = count_tokens(prompt)

    # 2. Validate budget
    validation = validate_context_budget(
        command_text=extract_command_from_prompt(prompt),
        agent_readme=extract_readme_from_prompt(prompt),
        auto_skills=extract_skills_from_prompt(prompt)
    )

    if not validation["within_budget"]:
        logger.warning(
            f"CFR-018 WARNING: {agent_type}.{command_name} "
            f"using {validation['total_tokens']} tokens "
            f"({validation['usage_percent']:.1f}% of budget)"
        )

    # 3. Execute
    client = Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4.0",
        messages=[{"role": "user", "content": prompt}],
        **kwargs
    )

    # 4. Extract actual usage from response
    actual_input = response.usage.input_tokens
    actual_output = response.usage.output_tokens
    total_tokens = actual_input + actual_output

    # 5. Log accuracy
    accuracy = (estimated_input / actual_input * 100) if actual_input > 0 else 0
    logger.info(
        f"{agent_type}.{command_name}: "
        f"Estimated {estimated_input} tokens, "
        f"actual {actual_input} input + {actual_output} output = {total_tokens} total "
        f"(estimate accuracy: {accuracy:.1f}%)"
    )

    # 6. Record to database for analysis
    record_token_usage(
        agent_type=agent_type,
        command_name=command_name,
        estimated_input=estimated_input,
        actual_input=actual_input,
        actual_output=actual_output,
        validation=validation
    )

    return {
        "result": response.content,
        "tokens": {
            "input": actual_input,
            "output": actual_output,
            "total": total_tokens,
            "estimated_input": estimated_input,
            "accuracy": accuracy
        }
    }
```

### 3. Database Tracking

Create table to track token usage over time:

```sql
CREATE TABLE IF NOT EXISTS command_token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type TEXT NOT NULL,
    command_name TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Pre-execution estimates
    estimated_input_tokens INTEGER,

    -- Actual usage from API
    actual_input_tokens INTEGER,
    actual_output_tokens INTEGER,
    total_tokens INTEGER,

    -- Budget validation
    command_tokens INTEGER,
    readme_tokens INTEGER,
    skills_tokens INTEGER,
    infrastructure_tokens INTEGER,  -- command + readme + skills
    budget_tokens INTEGER,  -- max allowed (60K)
    usage_percent REAL,
    within_budget BOOLEAN,

    -- Accuracy tracking
    estimate_accuracy_percent REAL,

    -- Context
    task_id TEXT,
    session_id TEXT
);

CREATE INDEX idx_token_usage_agent_command
ON command_token_usage(agent_type, command_name);

CREATE INDEX idx_token_usage_timestamp
ON command_token_usage(executed_at);
```

### 4. Analysis Queries

```sql
-- Average token usage per agent/command
SELECT
    agent_type,
    command_name,
    AVG(actual_input_tokens) as avg_input,
    AVG(actual_output_tokens) as avg_output,
    AVG(total_tokens) as avg_total,
    AVG(usage_percent) as avg_budget_usage,
    COUNT(*) as executions,
    SUM(CASE WHEN within_budget = 0 THEN 1 ELSE 0 END) as over_budget_count
FROM command_token_usage
GROUP BY agent_type, command_name
ORDER BY avg_budget_usage DESC;

-- Estimate accuracy over time
SELECT
    DATE(executed_at) as date,
    agent_type,
    AVG(estimate_accuracy_percent) as avg_accuracy,
    COUNT(*) as executions
FROM command_token_usage
GROUP BY date, agent_type
ORDER BY date DESC, agent_type;

-- Find commands exceeding budget
SELECT
    agent_type,
    command_name,
    actual_input_tokens,
    infrastructure_tokens,
    usage_percent,
    executed_at
FROM command_token_usage
WHERE within_budget = 0
ORDER BY usage_percent DESC
LIMIT 20;
```

---

## Implementation Plan

### Phase 1: Token Counting Infrastructure
1. Add Anthropic tokenizer dependency
2. Create `token_counter.py` utility module
3. Create `command_token_usage` database table
4. Write unit tests for token counting

### Phase 2: Pre-Execution Validation
1. Create `@validate_context_budget` decorator
2. Apply to all command execution functions
3. Log warnings for over-budget commands
4. Update CFR-018 with token-based limits

### Phase 3: Runtime Tracking
1. Wrap API calls to capture usage data
2. Store actual vs estimated tokens in database
3. Create dashboard/report for token analysis
4. Identify and fix over-budget commands

### Phase 4: Continuous Monitoring
1. Set up alerts for budget violations
2. Track estimate accuracy over time
3. Adjust budgets based on real data
4. Generate weekly usage reports

---

## Updated Budget (Token-Based)

### Current (Line-Based) - INCORRECT
```
30% of 1,600 lines = 480 lines
480 lines × 80 chars/line = 38,400 chars
38,400 chars ÷ 4 chars/token = 9,600 tokens
```

### Correct (Token-Based)
```
Claude context: 200,000 tokens
30% budget: 60,000 tokens (infrastructure)
70% budget: 140,000 tokens (work content)

Infrastructure (30% = 60K tokens):
  - Command: ~3-5K tokens (varies by command)
  - Agent README: ~3-4K tokens (180 lines × ~20 tokens/line)
  - Auto-skills: ~2-3K tokens (assumed)
  - Total: ~10K tokens (5% actual vs 30% budgeted)

Work Content (70% = 140K tokens):
  - Spec: ~6-8K tokens (320 lines)
  - Code context: ~4-6K tokens
  - System prompts: ~5-8K tokens
  - Remaining: ~115K tokens available
```

**Finding**: We have MUCH more room than we thought!

---

## Benefits

### 1. Accuracy
- Measures actual LLM token usage
- No guessing with line/word counts
- Real data from API responses

### 2. Validation
- Pre-execution budget checks
- Runtime warnings for overages
- Historical tracking for trends

### 3. Optimization
- Identify truly over-budget commands
- Right-size agent READMEs based on real data
- Optimize prompts for token efficiency

### 4. Observability
- Dashboard showing token usage per agent/command
- Alerts for budget violations
- Trend analysis over time

---

## Example: Decorator Pattern

```python
from functools import wraps
from typing import Callable, Any

def with_context_tracking(max_budget_tokens: int = 60_000):
    """Decorator to track token usage for command execution.

    Usage:
        @with_context_tracking(max_budget_tokens=60_000)
        def implement_task(task_id: str) -> dict:
            # Command implementation
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract agent/command info
            agent_type = func.__module__.split('.')[-2]  # e.g., "code_developer"
            command_name = func.__name__  # e.g., "implement_task"

            # Build prompt (this is simplified)
            prompt = build_command_prompt(
                agent_type=agent_type,
                command_name=command_name,
                args=args,
                kwargs=kwargs
            )

            # Validate budget
            validation = validate_context_budget(
                command_text=prompt["command"],
                agent_readme=prompt["readme"],
                auto_skills=prompt["skills"],
                max_tokens=max_budget_tokens
            )

            if not validation["within_budget"]:
                logger.error(
                    f"CFR-018 VIOLATION: {agent_type}.{command_name} "
                    f"exceeds budget: {validation['usage_percent']:.1f}%"
                )
                raise ContextBudgetViolationError(
                    f"Command context {validation['total_tokens']} tokens "
                    f"exceeds budget of {max_budget_tokens}"
                )

            # Execute with tracking
            result = execute_command_with_tracking(
                agent_type=agent_type,
                command_name=command_name,
                prompt=prompt["full_prompt"],
                func=func,
                args=args,
                kwargs=kwargs
            )

            return result

        return wrapper
    return decorator


# Usage example:
@with_context_tracking(max_budget_tokens=60_000)
def implement_task(task_id: str) -> ImplementResult:
    """Implement task from specification."""
    # Token counting happens automatically via decorator
    # Budget validation happens automatically
    # Usage tracking happens automatically

    # Just write the implementation logic:
    spec = load_spec(task_id)
    files = generate_code(spec)
    commit_sha = create_commit(files)

    return ImplementResult(
        task_id=task_id,
        files_changed=files,
        commit_sha=commit_sha
    )
```

---

## Next Steps

1. **Immediate**: Create token counting utility module
2. **Short-term**: Add database table and tracking decorator
3. **Medium-term**: Collect real usage data for 1-2 weeks
4. **Long-term**: Update CFR-018 with token-based budgets

---

## Related

- **CFR-018**: Command Execution Context Budget (needs token-based update)
- **CFR-007**: Agent Context Budget (parent requirement)
- **Anthropic Docs**: [Token Counting](https://docs.anthropic.com/claude/docs/models-overview#token-counting)

---

**Status**: Ready for implementation
**Estimated Effort**: 2-3 days for Phase 1-2, 1 week for Phase 3-4
**Priority**: High (improves accuracy and observability)
