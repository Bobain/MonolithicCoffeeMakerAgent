# ACE Delegation Chain Tracking - Usage Guide

## Overview

The ACE framework now supports **delegation chain tracking** to propagate user satisfaction signals from delegating agents (like `user_listener`) to delegated agents (like `code_developer`).

This ensures that satisfaction feedback reaches the agents that performed the actual work, enabling proper learning from user feedback.

## Problem Solved

**Before**: User provides satisfaction to `user_listener` → satisfaction stays with `user_listener` → `code_developer` (who did the actual work) has NO satisfaction signal → Reflector can't learn what worked.

**After**: User provides satisfaction to `user_listener` → satisfaction propagates through delegation chain → `code_developer` receives propagated satisfaction → Reflector can learn from real work satisfaction.

## Architecture

### Delegation Chain Format

Each trace now includes:
- `parent_trace_id`: The trace ID of the delegating agent
- `delegation_chain`: List of all agents in the chain with their trace IDs

```json
{
  "trace_id": "1760506616322509",
  "parent_trace_id": "1760506616321612",
  "delegation_chain": [
    {
      "agent": "user_listener",
      "trace_id": "1760506616321612",
      "timestamp": "2025-10-15T10:00:00"
    },
    {
      "agent": "code_developer",
      "trace_id": "1760506616322509",
      "timestamp": "2025-10-15T10:00:01"
    }
  ]
}
```

### Satisfaction Propagation

When satisfaction is attached to a parent trace, it can be propagated to all child traces using the `ACEReflector.propagate_satisfaction()` method.

Propagated satisfaction includes metadata:
```json
{
  "score": 5,
  "positive_feedback": "Perfect implementation!",
  "timestamp": "2025-10-15T10:00:00",
  "propagated_from": "1760506616321612",
  "propagated_from_agent": "user_listener",
  "note": "Satisfaction propagated from parent agent (user_listener)"
}
```

## Usage Example

### Step 1: User Listener Observes Delegation

```python
from coffee_maker.cli.user_listener_ace import UserListenerACE

# Initialize ACE
ace = UserListenerACE(enabled=True)

# Observe delegation
parent_trace_id = ace.observe_delegation(
    user_query="Implement authentication feature",
    intent="code_implementation",
    delegated_to="code_developer",
    success=True,
    duration_seconds=2.0
)

# Returns: "1760506616321612" (trace ID for user_listener)
```

### Step 2: Code Developer Executes (Receives Delegation Chain)

```python
from coffee_maker.autonomous.ace.generator import ACEGenerator
from coffee_maker.autonomous.ace.trace_manager import TraceManager
from coffee_maker.autonomous.ace.config import get_default_config

# Initialize generator
config = get_default_config()
trace_manager = TraceManager(config.trace_dir)
generator = ACEGenerator(
    agent_interface=claude_cli,
    config=config,
    agent_name="code_developer"
)

# Load parent trace to get delegation chain
parent_trace = trace_manager.read_trace(parent_trace_id)

# Execute with delegation chain
result = generator.execute_with_trace(
    prompt="Implement authentication feature",
    parent_trace_id=parent_trace_id,
    delegation_chain=parent_trace.delegation_chain
)

child_trace_id = result["trace_id"]
# Returns: "1760506616322509" (trace ID for code_developer)
```

### Step 3: User Provides Satisfaction

```python
from coffee_maker.autonomous.ace.generator import ACEGenerator

# Attach satisfaction to user_listener trace
satisfaction = {
    "score": 5,
    "positive_feedback": "Perfect implementation! Tests passed, code is clean.",
    "improvement_areas": "",
    "timestamp": "2025-10-15T10:05:00"
}

generator.attach_satisfaction(parent_trace_id, satisfaction)
```

### Step 4: Propagate Satisfaction Through Chain

```python
from coffee_maker.autonomous.ace.reflector import ACEReflector

# Initialize reflector
reflector = ACEReflector(
    agent_name="user_listener",
    traces_base_dir=config.trace_dir,
    deltas_base_dir=config.delta_dir
)

# Propagate satisfaction
num_propagated = reflector.propagate_satisfaction(parent_trace_id)
# Returns: 1 (satisfaction propagated to code_developer trace)
```

### Step 5: Verify Propagation

```python
# Load child trace
child_trace = trace_manager.read_trace(child_trace_id)

# Check satisfaction
print(child_trace.user_satisfaction)
# {
#   "score": 5,
#   "positive_feedback": "Perfect implementation! Tests passed, code is clean.",
#   "propagated_from": "1760506616321612",
#   "propagated_from_agent": "user_listener",
#   "note": "Satisfaction propagated from parent agent (user_listener)"
# }
```

## CLI Integration Example

Here's how the user_listener CLI could be updated to automatically propagate satisfaction:

```python
# In coffee_maker/cli/user_listener.py

@user_listener.command()
@click.argument("trace_id")
@click.option("--session-summary", required=True, help="Brief summary of work done")
def feedback(trace_id, session_summary):
    """Provide satisfaction feedback for completed session.

    Usage:
        coffee-maker user-listener feedback trace_123 --session-summary "Implemented auth feature"
    """
    console = Console()

    # 1. Collect satisfaction
    ace = UserListenerACE(enabled=True)
    satisfaction = ace.collect_satisfaction(trace_id, session_summary)

    if not satisfaction:
        console.print("[red]Failed to collect satisfaction[/red]")
        return

    # 2. Attach satisfaction to trace
    config = get_default_config()
    generator = ACEGenerator(
        agent_interface=None,  # Not needed for attach_satisfaction
        config=config,
        agent_name="user_listener"
    )

    try:
        generator.attach_satisfaction(trace_id, satisfaction)
        console.print(
            f"[green]✓[/green] Satisfaction (score={satisfaction['score']}) attached to trace: {trace_id}"
        )
    except Exception as e:
        console.print(f"[red]Failed to attach satisfaction: {e}[/red]")
        return

    # 3. Propagate satisfaction through delegation chain
    reflector = ACEReflector(
        agent_name="user_listener",
        traces_base_dir=config.trace_dir,
        deltas_base_dir=config.delta_dir
    )

    console.print()
    console.print("[cyan]Propagating feedback through delegation chain...[/cyan]")

    num_propagated = reflector.propagate_satisfaction(trace_id)

    if num_propagated > 0:
        console.print(
            f"[green]✓[/green] Feedback propagated to {num_propagated} delegated agent(s)",
            style="bold green"
        )
    else:
        console.print(
            "[yellow]No delegated agents found (no propagation needed)[/yellow]"
        )

    console.print()
    console.print("[bold green]Feedback collection complete![/bold green]")
```

## Multi-Level Delegation

The system supports multi-level delegation chains:

```
user_listener → assistant → code_developer
     (trace_1)   (trace_2)     (trace_3)
```

When satisfaction is attached to `trace_1`, propagation works recursively:
1. `reflector.propagate_satisfaction(trace_1)` finds `trace_2` (parent_trace_id == trace_1)
2. Propagates satisfaction to `trace_2`
3. Recursively calls `propagate_satisfaction(trace_2)`
4. Finds `trace_3` (parent_trace_id == trace_2)
5. Propagates satisfaction to `trace_3`

Total propagations: 2 (assistant and code_developer both receive satisfaction)

## Trace Visualization

The markdown export now shows delegation chain:

```markdown
# Execution Trace: 1760506616322509

**Timestamp**: 2025-10-15T10:00:01
**Agent**: code_developer
**Query**: Implement authentication feature

## Delegation Chain

1. **user_listener** (trace: `1760506616321612`, time: 2025-10-15T10:00:00)
2. **code_developer** (trace: `1760506616322509`, time: 2025-10-15T10:00:01)

**Parent Trace**: 1760506616321612

## Agent Identity

- **Objective**: Implement features from ROADMAP autonomously
- **Success Criteria**: Code runs, tests pass, DoD verified, PR created

## User Satisfaction

**Score**: 5/5
**Timestamp**: 2025-10-15T10:05:00
**Feedback**: Perfect implementation! Tests passed, code is clean.
**Note**: Satisfaction propagated from parent agent (user_listener)
```

## Testing

Comprehensive test suite available at `tests/unit/test_ace_delegation_chain.py`:

- ✅ Trace model with delegation chain fields
- ✅ Serialization/deserialization preserves chain
- ✅ Markdown visualization shows chain
- ✅ Generator accepts and tracks delegation chain
- ✅ UserListenerACE creates and returns trace_id
- ✅ Satisfaction propagates from parent to child
- ✅ Multi-level delegation (3-level chain)
- ✅ No propagation when no children
- ✅ No propagation when no satisfaction data
- ✅ End-to-end workflow test

Run tests:
```bash
pytest tests/unit/test_ace_delegation_chain.py -v
```

## Benefits

1. **Accurate Learning**: Reflector can now learn from satisfaction signals attached to the agents that did the actual work
2. **Better Insights**: Success patterns and failure modes are correctly attributed to the executing agents
3. **Delegation Transparency**: Full visibility into delegation chains in trace visualizations
4. **Recursive Propagation**: Supports arbitrarily deep delegation chains
5. **Metadata Tracking**: Propagated satisfaction includes source information for audit trails

## Future Enhancements

Potential future improvements:
- **Automatic Propagation**: Propagate satisfaction automatically when attached (no manual call needed)
- **Weighted Propagation**: Reduce satisfaction score slightly when propagating (to distinguish direct vs. indirect)
- **Selective Propagation**: Only propagate to specific agent types
- **Bidirectional Signals**: Propagate errors/failures upward to delegating agents

---

**Implementation Date**: 2025-10-15
**Version**: 1.0
**Status**: ✅ Complete and Tested
