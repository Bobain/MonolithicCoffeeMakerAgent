# Automatic ACE Integration for All Agents

**Status**: ✅ Implemented and Tested
**Date**: 2025-10-15
**Version**: 1.0

---

## Overview

ACE (Agentic Context Engineering) integration is now **fully automatic** for all agents in the Coffee Maker Agent system. When you create a new agent, ACE supervision is automatic—no manual wrapper files needed!

### Key Benefits

1. **Zero Boilerplate**: No `*_ace.py` wrapper files needed
2. **Consistent Pattern**: All agents follow the same integration pattern
3. **Environment Controlled**: Enable/disable ACE per agent via env vars
4. **Single Execution**: Prevents the double-execution bug by design
5. **Backward Compatible**: Existing agents can be migrated gradually

---

## Quick Start: Creating a New Agent

```python
# 1. Import ACEAgent base class
from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

# 2. Inherit from ACEAgent
class MyNewAgent(ACEAgent):

    # 3. Define agent metadata (required)
    @property
    def agent_name(self) -> str:
        return "my_new_agent"  # Used for env var: ACE_ENABLED_MY_NEW_AGENT

    @property
    def agent_objective(self) -> str:
        return "Process data and generate insights"

    @property
    def success_criteria(self) -> str:
        return "Data processed accurately with actionable insights"

    # 4. Implement your agent logic
    def _execute_implementation(self, task: str, **kwargs) -> Dict[str, Any]:
        """Your agent logic goes here."""
        # Do your work
        result = self.process_data(task)
        return {"result": result}
```

That's it! ACE integration is **automatic**.

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│ User calls: agent.execute_task(...)    │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────────┐
│ ACEAgent.execute_task()                        │
│ ┌────────────────────────────────────────────┐ │
│ │ if ACE_ENABLED_{AGENT_NAME} == "true":     │ │
│ │   → generator.execute_with_trace()         │ │
│ │      ↓                                      │ │
│ │      generator calls send_message()        │ │
│ │      ↓                                      │ │
│ │      send_message() calls                  │ │
│ │      _execute_implementation()             │ │
│ │      ↓                                      │ │
│ │      generator captures trace              │ │
│ │      ↓                                      │ │
│ │      returns agent_result                  │ │
│ │                                             │ │
│ │ else:                                       │ │
│ │   → _execute_implementation() (direct)     │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
                 │
                 ↓
        ┌───────────────┐
        │ Agent Result  │
        └───────────────┘
```

### Key Components

1. **ACEAgent Base Class** (`coffee_maker/autonomous/ace/agent_wrapper.py`)
   - Checks `ACE_ENABLED_{AGENT_NAME}` environment variable
   - Initializes ACEGenerator if enabled
   - Routes executions through generator or directly
   - Provides consistent `send_message()` interface

2. **ACEGenerator** (existing, unchanged)
   - Wraps agent execution
   - Creates traces
   - Handles dual execution (conditional)
   - Returns agent_result

3. **Agent Implementation** (your code)
   - Implements `_execute_implementation()`
   - Defines agent metadata (name, objective, criteria)
   - Business logic only—no ACE code!

---

## Environment Variables

Enable/disable ACE per agent:

```bash
# .env.example
export ACE_ENABLED_USER_INTERPRET="true"   # ✅ ACE active
export ACE_ENABLED_USER_LISTENER="false"   # ❌ ACE disabled
export ACE_ENABLED_ASSISTANT="true"        # ✅ ACE active
export ACE_ENABLED_CODE_DEVELOPER="false"  # ❌ ACE disabled
export ACE_ENABLED_MY_NEW_AGENT="true"     # ✅ ACE active for new agent
```

**Pattern**: `ACE_ENABLED_{AGENT_NAME_UPPERCASE}="true|false"`

---

## Migration Guide: Existing Agents

### Before (Manual Wrapper Pattern)

```
coffee_maker/cli/
├── user_interpret.py        # Agent logic
└── user_interpret_ace.py    # Manual ACE wrapper (redundant!)
```

**Old Code** (`user_interpret_ace.py`):
```python
class UserInterpretWithACE:
    def __init__(self):
        self.user_interpret = UserInterpret()

        if os.getenv("ACE_ENABLED_USER_INTERPRET") == "true":
            self.generator = ACEGenerator(...)
            self.ace_enabled = True

    def interpret(self, message, context):
        if self.ace_enabled:
            result = self.generator.execute_with_trace(...)
            return result["agent_result"]
        else:
            return self.user_interpret.interpret(message, context)

    def send_message(self, message, **kwargs):
        return self.user_interpret.interpret(message, kwargs.get("context"))
```

### After (Automatic Integration)

```
coffee_maker/cli/
└── user_interpret.py        # Agent with automatic ACE (no wrapper!)
```

**New Code** (`user_interpret.py`):
```python
from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

class UserInterpret(ACEAgent):
    @property
    def agent_name(self) -> str:
        return "user_interpret"

    @property
    def agent_objective(self) -> str:
        return "Interpret user intent and delegate"

    @property
    def success_criteria(self) -> str:
        return "Correct interpretation and delegation"

    def _execute_implementation(self, message: str, context=None, **kwargs):
        # Your logic here (same as before)
        return {"intent": intent, "delegated_to": agent}
```

**Benefits**:
- ✅ 50% less code (no wrapper file!)
- ✅ Automatic ACE integration
- ✅ No manual trace handling
- ✅ Consistent with all other agents

---

## API Reference

### ACEAgent Base Class

```python
class ACEAgent(ABC):
    """Base class for all agents with automatic ACE integration."""

    # ===== REQUIRED: Implement these =====

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Agent name (used for env var and traces)."""
        pass

    @property
    @abstractmethod
    def agent_objective(self) -> str:
        """Agent's primary objective."""
        pass

    @property
    @abstractmethod
    def success_criteria(self) -> str:
        """Success criteria for evaluation."""
        pass

    @abstractmethod
    def _execute_implementation(self, *args, **kwargs) -> Any:
        """Your agent logic here."""
        pass

    # ===== PROVIDED: Use these =====

    def execute_task(self, *args, **kwargs) -> Any:
        """Public interface. Routes through ACE if enabled."""
        pass

    def send_message(self, message: str, **kwargs) -> Any:
        """Generator interface. Routes to _execute_implementation()."""
        pass

    def _format_prompt(self, *args, **kwargs) -> str:
        """Override to customize prompt formatting."""
        pass
```

### ACEAgentWrapper Class

For wrapping existing agents without refactoring:

```python
from coffee_maker.autonomous.ace.agent_wrapper import wrap_agent_with_ace

# Wrap existing agent
my_agent = MyExistingAgent()
wrapped = wrap_agent_with_ace(
    agent=my_agent,
    agent_name="my_agent",
    agent_objective="Process data",
    success_criteria="Data processed",
    execute_method="process"  # Which method to wrap
)

# Use wrapped version
result = wrapped.execute_task(data)
```

### Decorator Pattern

For class-level wrapping:

```python
from coffee_maker.autonomous.ace.agent_wrapper import ace_integrated

@ace_integrated(
    agent_name="my_agent",
    agent_objective="Process data",
    success_criteria="Data processed"
)
class MyAgent:
    def execute(self, data):
        return {"result": data}

# ACE is automatic!
agent = MyAgent()
result = agent.execute("test")  # Traced if ACE_ENABLED_MY_AGENT=true
```

---

## Testing

All automatic integration patterns have comprehensive tests:

```bash
# Test automatic ACE integration
poetry run pytest tests/unit/test_automatic_ace_integration.py -v

# Test specific agent (user_interpret v2)
poetry run pytest tests/unit/test_automatic_ace_integration.py::TestAutomaticACEIntegration -v
```

**Test Coverage**:
- ✅ Automatic environment variable checking
- ✅ Generator initialization when enabled
- ✅ Direct execution when disabled
- ✅ Single execution (no double-execution bug)
- ✅ Trace creation with correct data
- ✅ Backward compatibility
- ✅ New agent pattern validation

---

## Best Practices

### DO ✅

1. **Inherit from ACEAgent for new agents**
   ```python
   class MyAgent(ACEAgent):
       # Implement required properties and _execute_implementation
   ```

2. **Use descriptive agent metadata**
   ```python
   @property
   def agent_objective(self) -> str:
       return "Analyze code for security vulnerabilities and suggest fixes"
   ```

3. **Keep business logic in _execute_implementation()**
   ```python
   def _execute_implementation(self, code: str, **kwargs):
       # Your logic here, no ACE code!
       return {"vulnerabilities": results}
   ```

4. **Test both ACE enabled and disabled**
   ```python
   @patch.dict(os.environ, {"ACE_ENABLED_MY_AGENT": "true"})
   def test_with_ace():
       agent = MyAgent()
       assert agent.ace_enabled is True

   @patch.dict(os.environ, {"ACE_ENABLED_MY_AGENT": "false"})
   def test_without_ace():
       agent = MyAgent()
       assert agent.ace_enabled is False
   ```

### DON'T ❌

1. **Don't create manual *_ace.py wrapper files**
   ```python
   # ❌ NO! This is the old pattern
   class MyAgentWithACE:
       def __init__(self):
           self.agent = MyAgent()
           if ace_enabled:
               self.generator = ACEGenerator(...)
   ```

2. **Don't call _execute_implementation() directly from public methods**
   ```python
   # ❌ NO! This bypasses ACE
   def my_public_method(self, data):
       return self._execute_implementation(data)

   # ✅ YES! Route through execute_task()
   def my_public_method(self, data):
       return self.execute_task(data)
   ```

3. **Don't hardcode ACE logic in your agent**
   ```python
   # ❌ NO! ACE is automatic
   def execute(self, task):
       if self.ace_enabled:
           result = self.generator.execute_with_trace(...)
       # ... (this is what ACEAgent does for you!)
   ```

---

## Troubleshooting

### Issue: Agent not traced even though ACE enabled

**Check**:
1. Environment variable set correctly?
   ```bash
   echo $ACE_ENABLED_MY_AGENT  # Should be "true"
   ```

2. Agent name matches env var?
   ```python
   @property
   def agent_name(self) -> str:
       return "my_agent"  # Must match ACE_ENABLED_MY_AGENT
   ```

3. Calling execute_task(), not _execute_implementation()?
   ```python
   agent.execute_task(data)  # ✅ Correct
   agent._execute_implementation(data)  # ❌ Bypasses ACE
   ```

### Issue: Double execution (agent runs twice)

**This should be IMPOSSIBLE with ACEAgent**. If you see double execution:

1. Are you calling both execute_task() AND _execute_implementation()?
2. Are you using the old manual wrapper pattern?
3. Did you override execute_task() without calling super()?

**Solution**: Use ACEAgent base class—it prevents this by design.

### Issue: Tests failing with ACEAgent

**Check**:
1. Mock os.getenv for ACE_ENABLED_{AGENT_NAME}
2. Mock ACEGenerator if testing ACE-enabled path
3. Mock get_default_config

```python
@patch("coffee_maker.autonomous.ace.agent_wrapper.os.getenv")
@patch("coffee_maker.autonomous.ace.agent_wrapper.ACEGenerator")
@patch("coffee_maker.autonomous.ace.agent_wrapper.get_default_config")
def test_my_agent(mock_config, mock_gen, mock_env):
    mock_env.return_value = "true"  # ACE enabled
    mock_config.return_value = {}
    mock_gen.return_value = Mock()

    agent = MyAgent()
    # ... test ...
```

---

## Examples

### Example 1: Simple Agent

```python
from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

class WeatherAgent(ACEAgent):
    @property
    def agent_name(self) -> str:
        return "weather"

    @property
    def agent_objective(self) -> str:
        return "Fetch weather data for requested locations"

    @property
    def success_criteria(self) -> str:
        return "Weather data retrieved and formatted correctly"

    def _execute_implementation(self, location: str, **kwargs) -> Dict[str, Any]:
        # Fetch weather data
        data = self.fetch_weather(location)
        return {"location": location, "temperature": data.temp, "condition": data.condition}
```

Usage:
```python
# Set environment variable
export ACE_ENABLED_WEATHER="true"

# Use agent
agent = WeatherAgent()
result = agent.execute_task("San Francisco")
# Automatically traced if ACE enabled!
```

### Example 2: Agent with Context

```python
class CodeReviewAgent(ACEAgent):
    @property
    def agent_name(self) -> str:
        return "code_review"

    @property
    def agent_objective(self) -> str:
        return "Review code for quality, security, and best practices"

    @property
    def success_criteria(self) -> str:
        return "Comprehensive review with actionable feedback"

    def _execute_implementation(self, code: str, context: Dict = None, **kwargs) -> Dict[str, Any]:
        # Access context
        language = context.get("language", "python") if context else "python"

        # Review code
        issues = self.analyze_code(code, language)
        suggestions = self.generate_suggestions(issues)

        return {
            "issues_found": len(issues),
            "issues": issues,
            "suggestions": suggestions,
            "language": language
        }
```

Usage:
```python
agent = CodeReviewAgent()
result = agent.execute_task(
    code="def foo(): pass",
    context={"language": "python", "file": "main.py"}
)
```

### Example 3: Migrating Existing Agent

**Before** (user_interpret.py + user_interpret_ace.py):
```python
# user_interpret.py
class UserInterpret:
    def interpret(self, message: str, context=None):
        # ... logic ...
        return {"intent": intent}

# user_interpret_ace.py (50 lines of boilerplate!)
class UserInterpretWithACE:
    # ... manual wrapper code ...
```

**After** (just user_interpret.py):
```python
from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

class UserInterpret(ACEAgent):
    @property
    def agent_name(self) -> str:
        return "user_interpret"

    @property
    def agent_objective(self) -> str:
        return "Interpret user intent and delegate to appropriate agents"

    @property
    def success_criteria(self) -> str:
        return "Correct intent interpretation, accurate sentiment, appropriate delegation"

    def _execute_implementation(self, message: str, context=None, **kwargs):
        # Same logic as before
        return {"intent": intent}

    # Backward compatibility
    def interpret(self, message: str, context=None):
        return self.execute_task(message, context=context)
```

**Result**:
- ❌ Delete `user_interpret_ace.py` (no longer needed!)
- ✅ 50% less code
- ✅ Automatic ACE integration
- ✅ Backward compatible

---

## Rollout Plan

### Phase 1: Validation (COMPLETED ✅)
- ✅ Implement ACEAgent base class
- ✅ Create user_interpret_v2 as proof of concept
- ✅ Write comprehensive tests
- ✅ Validate automatic integration works

### Phase 2: Migration (NEXT)
1. Migrate user_interpret to use ACEAgent
   - Replace user_interpret.py with v2 implementation
   - Delete user_interpret_ace.py
   - Update imports in user_listener.py

2. Migrate other agents:
   - assistant → AssistantAgent(ACEAgent)
   - code_developer → CodeDeveloperAgent(ACEAgent)
   - project_manager → ProjectManagerAgent(ACEAgent)
   - code-searcher → CodeSearcherAgent(ACEAgent)

3. Update documentation:
   - Update CLAUDE.md
   - Update agent definitions in .claude/agents/
   - Update ROADMAP.md

### Phase 3: Enforcement (FUTURE)
- Add linter rule: "No *_ace.py files allowed"
- Pre-commit hook: Verify all agents inherit from ACEAgent
- Documentation: "How to add a new agent" guide

---

## Related Documentation

- [ACE Framework Guide](ACE_FRAMEWORK_GUIDE.md) - Overview of ACE system
- [Agent ACE Integration Pattern](AGENT_ACE_INTEGRATION_PATTERN.md) - Old manual pattern (deprecated)
- [Testing Guide](../tests/README.md) - How to test agents

---

## Summary

**Automatic ACE integration** means:

1. ✅ **New agents**: Just inherit from ACEAgent—ACE is automatic
2. ✅ **Existing agents**: Migrate to ACEAgent pattern—delete manual wrappers
3. ✅ **No boilerplate**: No `*_ace.py` wrapper files needed
4. ✅ **Consistent**: All agents follow same pattern
5. ✅ **Safe**: Prevents double-execution bug by design
6. ✅ **Testable**: Comprehensive test coverage included

**The future is automatic! 🚀**
