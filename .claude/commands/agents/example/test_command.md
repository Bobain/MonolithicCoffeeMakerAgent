---
command: example.test_command
agent: example
action: test_command
description: Example command demonstrating the unified command architecture
tables:
  write: [notifications]
  read: [roadmap_priority]
required_skills: []
required_tools: []
---

# Example Test Command

This is an example command demonstrating the unified command architecture for SPEC-101.

## Purpose

This command shows how to:
1. Define command metadata in frontmatter
2. Specify table permissions (read/write)
3. Declare required skills and tools
4. Document command usage

## Architecture

Commands are defined as markdown files with YAML frontmatter metadata:

```
---
command: <agent>.<action_name>
agent: <agent_name>
action: <action_name>
tables:
  write: [table1, table2]
  read: [table3, table4]
required_skills: [skill1, skill2]
required_tools: [git, pytest]
---

# Command: <agent>.<action_name>

## Purpose
...
```

## Implementation

When loaded by `CommandLoader`, the command:

1. Parses frontmatter metadata
2. Validates permissions via `DomainWrapper`
3. Loads required skills
4. Executes with provided parameters
5. Returns results with audit trail

## Example Usage

```python
from coffee_maker.commands import CommandLoader
from coffee_maker.autonomous.agent_registry import AgentType

# Load commands for an agent
loader = CommandLoader(AgentType.EXAMPLE)

# List available commands
commands = loader.list_commands()

# Execute a command with parameters
result = loader.execute(
    "test_command",
    {"param1": "value1", "param2": "value2"}
)

# Check success
if result["success"]:
    print("Command executed successfully")
```

## Database Access

Commands can read from and write to authorized tables:

```python
# Read permission
items = db.read("roadmap_priority")

# Write permission (with audit logging)
db.write("notifications", {
    "target_agent": "developer",
    "message": "Task complete"
})

# Send notifications
db.send_notification(
    "other_agent",
    {"type": "event", "data": "..."}
)
```

## Skill Integration

Commands can declare required skills:

```yaml
required_skills:
  - technical_specification_handling
  - git_workflow_automation
```

Skills are loaded before execution and passed to the command's execute method.

## Error Handling

Permission errors are caught and raised:

```python
try:
    loader.execute("unauthorized_command", {})
except PermissionError as e:
    print(f"Access denied: {e}")
```

## Testing

See `tests/integration/test_command_system.py` for comprehensive integration tests.

## References

- SPEC-101: Foundation Infrastructure for Unified Agent Commands
- `.claude/commands/` - Centralized command definitions
- `coffee_maker/commands/` - Command system implementation
- `coffee_maker/database/domain_wrapper.py` - Permission enforcement
