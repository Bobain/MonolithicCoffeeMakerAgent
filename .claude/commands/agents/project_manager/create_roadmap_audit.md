---
command: project_manager.create_roadmap_audit
agent: project_manager
action: create_roadmap_audit
data_domain: roadmap
write_tables: [roadmap_audit]
read_tables: []
required_skills: []
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.create_roadmap_audit

## Purpose

Manually create an audit log entry for roadmap changes. Useful for documenting external modifications, manual interventions, or corrections that need to be tracked.

## Input Parameters

```yaml
priority_id: string      # Required - Priority affected
action: string           # Required - "create", "update", "delete", "status_change", "metadata_change", "manual_correction"
description: string      # Required - Human-readable description of the change
old_value: string        # Optional - Previous value
new_value: string        # Optional - New value
timestamp: string        # Optional - Override timestamp (ISO format, default: now)
```

## Database Operations

### WRITE Operations

```sql
-- Create audit entry
INSERT INTO roadmap_audit (
    priority_id, action, description, old_value, new_value,
    changed_by, changed_at
) VALUES (?, ?, ?, ?, ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify priority_id is provided
   - Verify action is valid type
   - Verify description is provided and non-empty

2. **Normalize Data**
   - Trim description to reasonable length
   - Truncate old_value and new_value to max 500 chars
   - Use provided timestamp or current time

3. **Create Audit Entry**
   - Generate unique audit entry ID
   - Write to roadmap_audit table
   - Set changed_by = "project_manager"
   - Set changed_at to timestamp (provided or now)

4. **Return Results**

## Output

```json
{
  "success": true,
  "audit_entry_id": "audit-12347",
  "priority_id": "PRIORITY-25",
  "action": "status_change",
  "created_at": "2025-10-26T10:35:00Z"
}
```

## Valid Actions

| Action | Use Case |
|--------|----------|
| `create` | Priority initially created |
| `update` | Priority fields updated (title, description, etc.) |
| `delete` | Priority removed from roadmap |
| `status_change` | Status updated (Planned → In Progress, etc.) |
| `metadata_change` | Associated metadata changed |
| `manual_correction` | Manual correction or adjustment |
| `external_change` | External tool modification |
| `dod_verification` | Definition of Done verification recorded |

## Implementation Pattern

```python
def create_roadmap_audit(db: DomainWrapper, params: dict):
    """Create a manual audit log entry for roadmap changes."""
    from datetime import datetime
    import uuid

    # 1. Validate input
    priority_id = params.get("priority_id")
    action = params.get("action")
    description = params.get("description")

    if not priority_id:
        raise ValueError("priority_id is required")

    if not action:
        raise ValueError("action is required")

    if not description:
        raise ValueError("description is required")

    # Validate action is in allowed list
    valid_actions = [
        "create", "update", "delete", "status_change",
        "metadata_change", "manual_correction", "external_change",
        "dod_verification"
    ]

    if action not in valid_actions:
        raise ValueError(
            f"Invalid action '{action}'. Valid actions: {', '.join(valid_actions)}"
        )

    # 2. Normalize data
    description = description.strip()
    if len(description) > 1000:
        description = description[:997] + "..."

    old_value = params.get("old_value", "")
    if old_value and len(old_value) > 500:
        old_value = old_value[:497] + "..."

    new_value = params.get("new_value", "")
    if new_value and len(new_value) > 500:
        new_value = new_value[:497] + "..."

    # Use provided timestamp or current time
    if params.get("timestamp"):
        timestamp = params["timestamp"]
    else:
        timestamp = datetime.now().isoformat()

    # Generate audit entry ID
    audit_id = f"audit-{uuid.uuid4().hex[:12]}"

    # 3. Create audit entry
    db.write("roadmap_audit", {
        "id": audit_id,
        "priority_id": priority_id,
        "action": action,
        "description": description,
        "old_value": old_value if old_value else None,
        "new_value": new_value if new_value else None,
        "changed_by": "project_manager",
        "changed_at": timestamp
    }, action="create")

    # 4. Return results
    return {
        "success": True,
        "audit_entry_id": audit_id,
        "priority_id": priority_id,
        "action": action,
        "created_at": timestamp
    }
```

## Success Criteria

- ✅ Audit entry created in database
- ✅ Timestamp recorded (provided or current)
- ✅ agent_name set to "project_manager"
- ✅ All fields populated correctly
- ✅ Unique audit entry ID generated

## Use Cases

### Use Case 1: Manual Correction
```json
{
  "priority_id": "PRIORITY-15",
  "action": "manual_correction",
  "description": "Corrected priority title from typo",
  "old_value": "Implemnet User Authentification",
  "new_value": "Implement User Authentication"
}
```

### Use Case 2: External Tool Change
```json
{
  "priority_id": "PRIORITY-20",
  "action": "external_change",
  "description": "Description updated via GitHub issue link",
  "old_value": "TBD",
  "new_value": "Build integration with GitHub API"
}
```

### Use Case 3: DoD Verification
```json
{
  "priority_id": "PRIORITY-25",
  "action": "dod_verification",
  "description": "Manual DoD verification recorded - all acceptance criteria met",
  "new_value": "Verified: UI responsive, tests passing, docs updated"
}
```

### Use Case 4: Manual Deletion
```json
{
  "priority_id": "PRIORITY-10",
  "action": "delete",
  "description": "Priority deleted - duplicate of PRIORITY-9",
  "old_value": "Complete API authentication module",
  "new_value": null
}
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| MissingFieldError | priority_id, action, or description missing | Provide all required fields |
| InvalidActionError | Invalid action type | Use valid action from allowed list |
| ValidationError | Data validation failed | Check field values and formats |
| PermissionError | Not project_manager | Only project_manager can create audit entries |

## CFR Compliance

- **CFR-009**: No sound notifications (sound=False)
- **CFR-015**: Database-first audit trail, no file modifications
- **CFR-007**: Minimal processing for audit creation

## Related Commands

- `project_manager.parse_roadmap` - Parse and sync ROADMAP.md
- `project_manager.update_priority_status` - Update priority status
- `project_manager.update_metadata` - Update ROADMAP metadata
- `project_manager.analyze_project_health` - Analyze health based on audit trails
