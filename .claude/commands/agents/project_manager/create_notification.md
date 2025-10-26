---
command: project_manager.create_notification
agent: project_manager
action: create_notification
data_domain: notifications
write_tables: [notifications]
read_tables: []
required_skills: []
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.create_notification

## Purpose

Send a notification to another agent via the shared notifications system. Enforces CFR-009 (no sound for background agents) and includes metadata for message routing and tracking.

## Input Parameters

```yaml
target_agent: string     # Required - Agent to notify ("architect", "code_developer", "orchestrator", etc.)
notification_type: string # Required - Type of notification ("spec_needed", "priority_complete", "work_available", etc.)
item_id: string          # Optional - Related item ID (priority_id, spec_id, etc.)
message: string          # Required - Notification message
priority: string         # Optional - Priority level ("low", "medium", "high", "urgent", default: "medium")
sound: boolean           # Optional - Play sound (MUST be false per CFR-009, enforced)
```

## Database Operations

### WRITE Operations

```sql
-- Create notification
INSERT INTO notifications (
    id, target_agent, source_agent, notification_type, item_id, message,
    priority, status, sound, created_at, updated_at
) VALUES (?, ?, 'project_manager', ?, ?, ?, ?, 'pending', 0, ?, ?);
```

## Execution Steps

1. **Validate Input**
   - Verify target_agent is provided
   - Verify notification_type is provided
   - Verify message is provided and non-empty
   - Verify priority is in valid list (low, medium, high, urgent)

2. **CFR-009 Enforcement**
   - Check if sound parameter is True
   - If sound=True: raise CFR009ViolationError
   - Force sound=False for all project_manager notifications

3. **Validate Target Agent**
   - Verify target_agent is a known agent type
   - Valid agents: architect, code_developer, orchestrator, code_reviewer, assistant, user_listener, ux_design_expert

4. **Generate Notification ID**
   - Create unique ID: `notif-{uuid}`

5. **Create Notification Record**
   - Write to notifications table
   - Set source_agent = "project_manager"
   - Set status = "pending"
   - Set sound = False (CFR-009)
   - Set created_at and updated_at to current timestamp

6. **Return Results**

## Output

```json
{
  "success": true,
  "notification_id": "notif-12348",
  "target_agent": "architect",
  "notification_type": "spec_needed",
  "message": "Specification needed for PRIORITY-25",
  "priority": "medium",
  "created_at": "2025-10-26T10:40:00Z"
}
```

## Implementation Pattern

```python
def create_notification(db: DomainWrapper, params: dict):
    """Send notification to another agent with CFR-009 enforcement."""
    from datetime import datetime
    import uuid

    # 1. Validate input
    target_agent = params.get("target_agent", "").strip()
    notification_type = params.get("notification_type", "").strip()
    message = params.get("message", "").strip()
    priority = params.get("priority", "medium").lower()
    item_id = params.get("item_id")

    if not target_agent:
        raise ValueError("target_agent is required")

    if not notification_type:
        raise ValueError("notification_type is required")

    if not message:
        raise ValueError("message is required")

    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        raise ValueError(
            f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
        )

    # 2. CFR-009 Enforcement - No sound for background agents
    if params.get("sound", False):
        raise ValueError(
            "CFR-009 violation: project_manager cannot use sound=True. "
            "Only user_listener can use sound=True. "
            "All background agents must use sound=False."
        )

    # 3. Validate target agent
    valid_agents = [
        "architect", "code_developer", "orchestrator", "code_reviewer",
        "assistant", "user_listener", "ux_design_expert"
    ]

    if target_agent not in valid_agents:
        raise ValueError(
            f"Invalid target_agent '{target_agent}'. "
            f"Valid agents: {', '.join(valid_agents)}"
        )

    # 4. Generate notification ID
    notification_id = f"notif-{uuid.uuid4().hex[:12]}"

    # 5. Create notification record
    notification_data = {
        "id": notification_id,
        "target_agent": target_agent,
        "source_agent": "project_manager",
        "notification_type": notification_type,
        "item_id": item_id,
        "message": message,
        "priority": priority,
        "status": "pending",
        "sound": False,  # CFR-009: Always false for background agents
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    result_id = db.write("notifications", notification_data, action="create")

    # 6. Return results
    return {
        "success": True,
        "notification_id": notification_id,
        "target_agent": target_agent,
        "notification_type": notification_type,
        "message": message,
        "priority": priority,
        "created_at": notification_data["created_at"]
    }
```

## Common Notification Types

### For Architect
- `spec_needed` - Specification needed for priority
- `spec_approved` - Specification approved and ready
- `design_review` - Architecture design review requested

### For Code Developer
- `work_available` - New priority ready for implementation
- `code_review_ready` - Code ready for review
- `blocker_resolved` - Blocking issue resolved

### For Orchestrator
- `priority_complete` - Priority implementation complete
- `priority_blocked` - Priority blocked, needs attention
- `resource_needed` - Additional resources needed

### For Code Reviewer
- `review_requested` - Code review requested
- `review_complete` - Review complete

### For User Listener
- `status_update` - Status update for user
- `alert` - Important alert

## Success Criteria

- ✅ Notification created in database
- ✅ CFR-009 enforced (sound=false for background agents)
- ✅ Target agent specified and validated
- ✅ Priority level set correctly
- ✅ Unique notification ID generated
- ✅ Timestamp recorded

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| CFR009ViolationError | sound=True | Use sound=False (CFR-009 requirement) |
| InvalidAgentError | Unknown target agent | Use valid agent name from list |
| ValidationError | Missing required fields | Provide target_agent, notification_type, message |
| PriorityError | Invalid priority level | Use "low", "medium", "high", or "urgent" |

## CFR Compliance

- **CFR-009**: MANDATORY - sound=False enforced for all project_manager notifications
  - Raises error if sound=True
  - Always sets sound=False in database
  - Rationale: Only user_listener can produce audio (CFR-009)

- **CFR-015**: Database-first notification storage
  - All notifications stored in notifications table
  - No file-based queue systems

- **CFR-007**: Efficient notification creation with minimal overhead

## Related Commands

- `project_manager.process_notifications` - Process incoming notifications
- `project_manager.send_agent_notification` - Wrapper for common notification patterns
