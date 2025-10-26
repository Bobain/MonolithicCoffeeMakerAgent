---
command: code_developer.update_claude_config
agent: code_developer
action: update_claude_config
tables:
  write: [system_audit]
  read: []
required_skills: []
required_tools: [database, file_system]
---

# Command: code_developer.update_claude_config

## Purpose
Update .claude/ configuration files (agent definitions, commands, skills) with version control and backups.

## Input Parameters

```yaml
config_type: string      # Required - "agent", "command", "skill"
config_name: string      # Required - Name of config to update (e.g., "code_developer")
updates: object          # Required - Fields to update
backup: boolean          # Create backup before update (default: true)
validate: boolean        # Validate syntax (default: true)
```

## Database Operations

### 1. Determine Config File Path
```python
from pathlib import Path
import json
from datetime import datetime
import shutil

def update_claude_config(db: DomainWrapper, params: dict):
    config_type = params["config_type"]
    config_name = params["config_name"]
    updates = params["updates"]

    # Determine file path based on config type
    if config_type == "agent":
        config_file = Path(f".claude/agents/{config_name}.md")
    elif config_type == "command":
        config_file = Path(f".claude/commands/agents/code_developer/{config_name}.md")
    elif config_type == "skill":
        config_file = Path(f".claude/skills/code-developer/{config_name}/SKILL.md")
    else:
        return {
            "success": False,
            "error": f"Unknown config type: {config_type}",
            "valid_types": ["agent", "command", "skill"]
        }

    # Verify file exists
    if not config_file.exists():
        return {
            "success": False,
            "error": f"Config file not found: {config_file}"
        }
```

### 2. Create Backup
```python
    backup_file = None

    if params.get("backup", True):
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = Path(f"{config_file}.backup-{timestamp}")

        try:
            shutil.copy2(config_file, backup_file)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create backup: {e}"
            }
```

### 3. Read Current Config
```python
    # Read current configuration
    try:
        current_content = config_file.read_text()
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read config: {e}"
        }

    # Parse based on type
    if config_type == "agent":
        updated_content = update_agent_config(current_content, updates)
    elif config_type == "command":
        updated_content = update_command_config(current_content, updates)
    elif config_type == "skill":
        updated_content = update_skill_config(current_content, updates)
```

### 4. Update Configuration
```python
def update_agent_config(content: str, updates: dict) -> str:
    """Update agent configuration file."""
    import re

    # Update YAML frontmatter if present
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                metadata = yaml.safe_load(parts[1])
            except:
                metadata = {}

            # Apply updates
            metadata.update(updates)

            # Reconstruct YAML
            import yaml
            updated_yaml = yaml.dump(metadata, default_flow_style=False)
            return f"---\n{updated_yaml}---\n{parts[2]}"

    # If no YAML, just append updates as comments
    return content + f"\n\n<!-- Updated: {updates} -->"

def update_command_config(content: str, updates: dict) -> str:
    """Update command configuration file."""
    # Similar to agent_config
    return update_agent_config(content, updates)

def update_skill_config(content: str, updates: dict) -> str:
    """Update skill configuration file."""
    # Similar to agent_config
    return update_agent_config(content, updates)
```

### 5. Validate Configuration
```python
    if params.get("validate", True):
        # Validate syntax based on type
        if config_type in ["agent", "command", "skill"]:
            # Check YAML frontmatter syntax
            try:
                if updated_content.startswith("---"):
                    parts = updated_content.split("---", 2)
                    if len(parts) >= 2:
                        import yaml
                        yaml.safe_load(parts[1])
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Invalid YAML syntax: {e}",
                    "backup_file": str(backup_file) if backup_file else None
                }

        # Validate required fields based on type
        if config_type == "command":
            if "command:" not in updated_content or "agent:" not in updated_content:
                return {
                    "success": False,
                    "error": "Command missing required YAML fields (command, agent)",
                    "backup_file": str(backup_file) if backup_file else None
                }
```

### 6. Write Updated Config
```python
    # Write updated configuration
    try:
        config_file.write_text(updated_content)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write config: {e}",
            "backup_file": str(backup_file) if backup_file else None
        }
```

### 7. Audit Update
```python
    # Create audit record
    db.write("system_audit", {
        "table_name": "config_updates",
        "item_id": str(config_file),
        "action": "updated",
        "field_changed": json.dumps(updates),
        "new_value": updated_content[:200],  # Preview
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat(),
        "metadata": json.dumps({
            "config_type": config_type,
            "backup_file": str(backup_file) if backup_file else None,
            "validated": params.get("validate", True)
        })
    }, action="create")

    return {
        "success": True,
        "config_type": config_type,
        "config_name": config_name,
        "file_updated": str(config_file),
        "backup_created": str(backup_file) if backup_file else None,
        "changes_applied": len(updates)
    }
```

## Output

```json
{
  "success": true,
  "config_type": "agent",
  "config_name": "code_developer",
  "file_updated": ".claude/agents/code_developer.md",
  "backup_created": ".claude/agents/code_developer.md.backup-20251026-120000",
  "changes_applied": 3
}
```

## Success Criteria

- ✅ Config file updated
- ✅ Backup created (if enabled)
- ✅ Syntax valid (if validation enabled)
- ✅ Audit trail created
- ✅ Changes persisted to filesystem

## Update Agent Configuration

Update agent definition:

```python
update_claude_config(db, {
    "config_type": "agent",
    "config_name": "code_developer",
    "updates": {
        "version": "2.1",
        "status": "production",
        "capabilities": ["implementation", "testing", "review"]
    },
    "backup": True,
    "validate": True
})
```

## Update Command Configuration

Add new parameter to command:

```python
update_claude_config(db, {
    "config_type": "command",
    "config_name": "run_test_suite",
    "updates": {
        "required_tools": ["database", "pytest", "coverage"],
        "version": "1.1"
    }
})
```

## Update Skill Configuration

Update skill metadata:

```python
update_claude_config(db, {
    "config_type": "skill",
    "config_name": "code_forensics",
    "updates": {
        "version": "2.0",
        "triggers": ["fix_failing_tests", "debug_errors"]
    }
})
```

## Configuration File Locations

```
.claude/
├── agents/
│   ├── code_developer.md
│   ├── architect.md
│   ├── project_manager.md
│   └── ...
├── commands/
│   ├── agents/
│   │   └── code_developer/
│   │       ├── claim_priority.md
│   │       ├── load_spec.md
│   │       └── ...
│   └── ...
└── skills/
    └── code-developer/
        ├── code_forensics/
        │   └── SKILL.md
        └── ...
```

## Backup Management

### List Backups
```bash
ls -la .claude/agents/code_developer.md.backup-*
```

### Restore from Backup
```bash
cp .claude/agents/code_developer.md.backup-20251026-120000 \
   .claude/agents/code_developer.md
```

### Cleanup Old Backups
```bash
# Keep last 5 backups
ls -t .claude/agents/code_developer.md.backup-* | tail -n +6 | xargs rm
```

## YAML Frontmatter Format

All configuration files use YAML frontmatter:

```yaml
---
command: code_developer.run_test_suite
agent: code_developer
tables:
  write: [metrics_subtask, system_audit]
  read: []
required_skills: []
required_tools: [database, pytest]
---

# Markdown content below
```

## Common Updates

### Add New Required Tool
```python
update_claude_config(db, {
    "config_type": "command",
    "config_name": "run_test_suite",
    "updates": {
        "required_tools": ["database", "pytest", "coverage"]
    }
})
```

### Update Command Version
```python
update_claude_config(db, {
    "config_type": "command",
    "config_name": "create_pull_request",
    "updates": {
        "version": "1.1"
    }
})
```

### Update Skill Triggers
```python
update_claude_config(db, {
    "config_type": "skill",
    "config_name": "test_failure_analysis",
    "updates": {
        "triggers": ["fix_failing_tests", "debug_test_errors"]
    }
})
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| ConfigNotFoundError | File doesn't exist | Verify config name |
| InvalidTypeError | Unknown config type | Use valid type |
| YAMLSyntaxError | Invalid YAML | Fix syntax |
| BackupFailedError | Can't create backup | Check permissions |
| ValidationError | Config invalid | Review updates |

## Validation Strictness

### Strict Mode (Default)
```python
update_claude_config(db, {
    "config_type": "command",
    "config_name": "run_test_suite",
    "updates": {"version": "1.1"},
    "validate": True  # Validates YAML, required fields
})
# Fails if YAML syntax invalid
```

### Lenient Mode
```python
update_claude_config(db, {
    "config_type": "command",
    "config_name": "run_test_suite",
    "updates": {"version": "1.1"},
    "validate": False  # Skip validation
})
# Allows any content
```

## Rollback Procedure

If update causes issues:

1. List backups:
   ```bash
   ls -t .claude/agents/code_developer.md.backup-*
   ```

2. Restore from backup:
   ```python
   # Manual restore
   cp .claude/agents/code_developer.md.backup-20251026-120000 \
      .claude/agents/code_developer.md
   ```

3. Verify restoration:
   ```bash
   cat .claude/agents/code_developer.md
   ```

## Integration with Other Commands

Update config when:
- Adding new parameters to command
- Updating skill capabilities
- Changing agent responsibilities
- Fixing configuration bugs

Example workflow:
```python
# 1. Test new feature
# 2. Update command definition
update_claude_config(db, {...})
# 3. Commit changes
# 4. PR for review
```

## Audit Trail

All updates tracked in `system_audit` table:

```sql
SELECT * FROM system_audit
WHERE table_name = 'config_updates'
ORDER BY changed_at DESC;
```

View what changed and when for complete history.
