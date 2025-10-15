# Standard Pattern for ACE Integration

**Version**: 1.0
**Last Updated**: 2025-10-15

## Overview

This document defines the **mandatory standard pattern** for integrating any new agent with the ACE (Agentic Context Engineering) framework. Every agent that should be observed by ACE MUST follow this exact pattern to ensure correct trace generation and result handling.

## Critical Bug Fixed

The original implementation had a logic error where `execute_with_trace()` created a trace but then called the agent directly, bypassing the generator's observation and causing double execution. This pattern fixes that by:

1. Generator stores agent's actual result in `Execution.agent_response`
2. Generator returns `agent_result` in the response dictionary
3. Wrapper uses the returned `agent_result` directly (single execution)

## The Standard Pattern

### 1. Core Agent Implementation (NO ACE Code)

Every agent should have a core implementation file with NO ACE code:

**File**: `coffee_maker/cli/my_agent.py`

```python
"""Core agent implementation - NO ACE code here."""

from typing import Dict, Any


class MyAgent:
    """Core agent logic without ACE observation."""

    def __init__(self):
        """Initialize agent."""
        pass

    def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary task.

        Args:
            task: Task description or user message
            context: Additional context for execution

        Returns:
            Result dictionary (format depends on agent)
        """
        # Agent logic here
        result = {
            "status": "success",
            "data": "...",
            # Agent-specific fields
        }
        return result
```

**Key Points**:
- NO ACE imports
- NO ACE logic
- Pure agent functionality
- Testable in isolation

### 2. ACE Wrapper Implementation

Create a separate wrapper file that adds ACE observation:

**File**: `coffee_maker/cli/my_agent_ace.py`

```python
"""ACE wrapper for my_agent agent.

my_agent is under ACE supervision to learn:
- [What the agent should learn]
- [Patterns to identify]
- [Improvements to discover]
"""

import os
import logging
from typing import Dict, Any, Optional

from coffee_maker.cli.my_agent import MyAgent
from coffee_maker.autonomous.ace.generator import ACEGenerator
from coffee_maker.autonomous.ace.config import get_default_config

logger = logging.getLogger(__name__)


class MyAgentWithACE:
    """my_agent wrapped with ACE observation.

    All executions of my_agent are observed by generator,
    creating traces for reflector to analyze.
    """

    def __init__(self):
        """Initialize agent with optional ACE observation."""
        self.agent = MyAgent()

        # Check if ACE enabled via environment variable
        ace_enabled = os.getenv("ACE_ENABLED_MY_AGENT", "false").lower() == "true"

        if ace_enabled:
            config = get_default_config()
            self.generator = ACEGenerator(
                agent_interface=self,  # self is the interface
                config=config,
                agent_name="my_agent",
                agent_objective="[What this agent accomplishes]",
                success_criteria="[How success is measured]"
            )
            self.ace_enabled = True
            logger.info("ACE enabled for my_agent")
        else:
            self.generator = None
            self.ace_enabled = False
            logger.info("ACE disabled for my_agent")

    def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute with ACE observation (if enabled).

        Args:
            task: Task description or user message
            context: Additional context for execution

        Returns:
            Result dictionary from agent
        """
        if self.ace_enabled:
            # Execute through generator (creates trace and returns actual result)
            result = self.generator.execute_with_trace(
                prompt=task,
                priority_context=context or {},
                context=context,  # Pass context as kwarg for send_message
            )
            # Generator returns {agent_result, result, trace_id, duration, errors}
            # Return the agent's actual result (NO double execution)
            return result["agent_result"]
        else:
            # Direct execution (no trace)
            return self.agent.execute_task(task, context)

    def send_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Interface method for ACEGenerator - REQUIRED.

        This is called by generator.execute_with_trace().
        The generator observes this execution and returns the result.

        Args:
            message: The prompt/task (passed by generator)
            **kwargs: Additional parameters passed to execute_with_trace

        Returns:
            Agent's result (will be stored as agent_result)
        """
        context = kwargs.get("context")
        return self.agent.execute_task(message, context)
```

**Key Points**:
- Imports ACE components
- Checks `ACE_ENABLED_MY_AGENT` environment variable
- Wraps agent execution with generator
- Returns `result["agent_result"]` (NOT `result["result"]`)
- `send_message()` is REQUIRED for ACEGenerator interface
- NO double execution

### 3. Environment Variable

Add to `.env.example` and user's `.env`:

```bash
# Enable ACE observation for my_agent
export ACE_ENABLED_MY_AGENT="false"
```

**Naming Convention**:
- Format: `ACE_ENABLED_{AGENT_NAME}`
- Agent name in UPPERCASE
- Default: `"false"`

### 4. Agent Definition File

Create agent definition for documentation:

**File**: `.claude/agents/my_agent.md`

```markdown
---
name: my_agent
description: [Brief description of what this agent does]
model: sonnet
color: [blue|green|purple|etc]
---

# my_agent

## Primary Responsibility

[What this agent is responsible for]

## Key Capabilities

- [Capability 1]
- [Capability 2]
- [Capability 3]

## ACE Integration

This agent is under ACE supervision to learn:
- [Learning goal 1]
- [Learning goal 2]
- [Learning goal 3]

Enable ACE observation:
```bash
export ACE_ENABLED_MY_AGENT="true"
```

## Usage

```python
from coffee_maker.cli.my_agent_ace import MyAgentWithACE

agent = MyAgentWithACE()
result = agent.execute_task("Do something", {"context": "value"})
```
```

### 5. Always Use Wrapped Version

In all code that uses the agent, import the ACE wrapper:

```python
# ❌ WRONG - bypasses ACE
from coffee_maker.cli.my_agent import MyAgent
agent = MyAgent()

# ✅ CORRECT - goes through ACE (when enabled)
from coffee_maker.cli.my_agent_ace import MyAgentWithACE
agent = MyAgentWithACE()
```

**Note**: When ACE is disabled (default), the wrapper just calls the core agent directly, so there's no performance penalty.

## How It Works

### Execution Flow (ACE Enabled)

```
User calls: agent.execute_task(task, context)
    ↓
Wrapper checks: if self.ace_enabled
    ↓
Generator: execute_with_trace(prompt=task, ...)
    ↓
Generator calls: self.agent_interface.send_message(task, context=context)
    ↓
Wrapper.send_message(): self.agent.execute_task(task, context)
    ↓
Core agent executes and returns result
    ↓
Generator stores result in: execution1.agent_response
    ↓
Generator returns: {"agent_result": execution1.agent_response, ...}
    ↓
Wrapper returns: result["agent_result"]
    ↓
User gets: Original agent result (observed by ACE)
```

### Execution Flow (ACE Disabled)

```
User calls: agent.execute_task(task, context)
    ↓
Wrapper checks: if self.ace_enabled → False
    ↓
Wrapper calls directly: self.agent.execute_task(task, context)
    ↓
User gets: Agent result (no ACE overhead)
```

## Testing

### Test with ACE Disabled (Default)

```bash
# Should work normally (no traces)
poetry run python -c "
from coffee_maker.cli.my_agent_ace import MyAgentWithACE
agent = MyAgentWithACE()
result = agent.execute_task('test', {})
print(result)
"
```

### Test with ACE Enabled

```bash
# Should create traces in data/ace/traces/
export ACE_ENABLED_MY_AGENT="true"

poetry run python -c "
from coffee_maker.cli.my_agent_ace import MyAgentWithACE
agent = MyAgentWithACE()
result = agent.execute_task('test', {})
print(result)
"

# Check trace was created
ls -la data/ace/traces/
```

### Verify Trace Content

```bash
# View trace as JSON
cat data/ace/traces/trace_*.json | jq .

# View trace as markdown
poetry run python -c "
from coffee_maker.autonomous.ace.trace_manager import TraceManager
tm = TraceManager('data/ace/traces')
traces = tm.list_traces()
if traces:
    trace = tm.read_trace(traces[0])
    print(trace.to_markdown())
"
```

## Common Mistakes

### ❌ Mistake 1: Calling Agent Twice

```python
def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if self.ace_enabled:
        result = self.generator.execute_with_trace(...)  # Calls agent once
        return self.agent.execute_task(task, context)  # WRONG: Second call!
```

**Fix**: Return `result["agent_result"]` directly.

### ❌ Mistake 2: Using Wrong Result Field

```python
def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if self.ace_enabled:
        result = self.generator.execute_with_trace(...)
        return result["result"]  # WRONG: This is just "success"/"failure"
```

**Fix**: Use `result["agent_result"]` which contains the actual agent response.

### ❌ Mistake 3: Missing send_message()

```python
class MyAgentWithACE:
    # Missing send_message() method
    pass
```

**Fix**: Always implement `send_message()` as the ACEGenerator interface.

### ❌ Mistake 4: Adding Prefixes to Prompt

```python
def interpret(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if self.ace_enabled:
        result = self.generator.execute_with_trace(
            prompt=f"Interpret user message: {user_message}",  # WRONG: Prefix added
            ...
        )
```

**Fix**: Pass raw message, extract in `send_message()` if needed (but usually not needed).

## Checklist for New Agent Integration

- [ ] Core agent implementation in `coffee_maker/cli/{agent_name}.py` (NO ACE code)
- [ ] ACE wrapper in `coffee_maker/cli/{agent_name}_ace.py`
- [ ] Environment variable `ACE_ENABLED_{AGENT_NAME}` added to `.env.example`
- [ ] Agent definition in `.claude/agents/{agent_name}.md`
- [ ] All imports use `{agent_name}_ace` (wrapped version)
- [ ] `send_message()` method implemented in wrapper
- [ ] Returns `result["agent_result"]` (NOT `result["result"]`)
- [ ] No double execution (verified by testing)
- [ ] Tested with ACE disabled (default behavior)
- [ ] Tested with ACE enabled (traces created)
- [ ] Trace content verified (contains agent result)

## Benefits

1. **Consistent**: All agents follow same pattern
2. **Testable**: Core agent can be tested in isolation
3. **Observable**: ACE framework can observe all agents
4. **Optional**: ACE disabled by default (no overhead)
5. **Correct**: No double execution, proper result handling
6. **Maintainable**: Clear separation of concerns

## Future Agents

Every new agent MUST follow this pattern:

1. Create core implementation (no ACE)
2. Create ACE wrapper following template above
3. Add environment variable
4. Create agent definition
5. Always use wrapped version in code
6. Test with ACE enabled/disabled

## Questions?

See:
- `coffee_maker/cli/user_interpret_ace.py` - Reference implementation
- `coffee_maker/autonomous/ace/generator.py` - Generator that wraps agents
- `coffee_maker/autonomous/ace/models.py` - Data models (Execution, ExecutionTrace)
- `docs/ACE_FRAMEWORK.md` - Full ACE framework documentation

---

**Remember**: Follow this pattern exactly for all new agents. Deviations will cause bugs!
