---
command: project_manager.send_agent_notification
agent: project_manager
action: send_agent_notification
data_domain: notifications
write_tables: [notifications]
read_tables: []
required_skills: []
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.send_agent_notification

## Purpose

Convenience wrapper for sending common notification types to agents. Handles message formatting and default parameters based on message_type.

## Input Parameters

```yaml
target_agent: string     # Required - Agent to notify ("architect", "code_developer", etc.)
message_type: string     # Required - Type of message ("spec_needed", "review_complete", "work_available", etc.)
priority_id: string      # Required - Related priority ID
additional_data: object  # Optional - Additional context data
```

## Message Types and Auto-Configuration

### For Architect

#### spec_needed
- **Purpose**: Request specification for a priority
- **Auto-Priority**: high
- **Auto-Message**: "Specification needed for PRIORITY-{id}: {title}"

#### spec_review
- **Purpose**: Request review of specification
- **Auto-Priority**: high
- **Auto-Message**: "Specification ready for review: {spec_id}"

#### design_guidance
- **Purpose**: Request design guidance
- **Auto-Priority**: medium
- **Auto-Message**: "Design guidance needed for {priority_id}"

### For Code Developer

#### work_available
- **Purpose**: New priority ready for implementation
- **Auto-Priority**: high
- **Auto-Message**: "New work available: {priority_id} - {title}"

#### blocker_resolved
- **Purpose**: Blocking issue has been resolved
- **Auto-Priority**: high
- **Auto-Message**: "Blocking issue resolved for {priority_id}"

#### review_requested
- **Purpose**: Code review requested
- **Auto-Priority**: medium
- **Auto-Message**: "Code review requested for {priority_id}"

### For Orchestrator

#### priority_complete
- **Purpose**: Priority implementation complete
- **Auto-Priority**: high
- **Auto-Message**: "Priority complete: {priority_id} - {title}"

#### priority_blocked
- **Purpose**: Priority blocked, requires intervention
- **Auto-Priority**: urgent
- **Auto-Message**: "Priority blocked: {priority_id} - {reason}"

#### resource_needed
- **Purpose**: Additional resources needed
- **Auto-Priority**: high
- **Auto-Message**: "Resource needed for {priority_id}: {resource_type}"

### For Code Reviewer

#### review_available
- **Purpose**: New review item available
- **Auto-Priority**: medium
- **Auto-Message**: "Code review available: {priority_id}"

#### review_urgent
- **Purpose**: Urgent code review needed
- **Auto-Priority**: urgent
- **Auto-Message**: "Urgent code review needed: {priority_id}"

## Output

```json
{
  "success": true,
  "notification_id": "notif-12349",
  "target_agent": "architect",
  "message_type": "spec_needed",
  "priority_id": "PRIORITY-25"
}
```

## Implementation Pattern

```python
def send_agent_notification(db: DomainWrapper, params: dict):
    """Send agent-specific notification with auto-configured message."""
    from datetime import datetime
    import uuid

    # 1. Validate input
    target_agent = params.get("target_agent", "").strip()
    message_type = params.get("message_type", "").strip()
    priority_id = params.get("priority_id", "").strip()
    additional_data = params.get("additional_data", {})

    if not target_agent:
        raise ValueError("target_agent is required")

    if not message_type:
        raise ValueError("message_type is required")

    if not priority_id:
        raise ValueError("priority_id is required")

    # 2. Get priority data for message generation
    try:
        priorities = db.read("roadmap_priority", {"id": priority_id})
        priority_data = priorities[0] if priorities else {"id": priority_id}
    except:
        priority_data = {"id": priority_id}

    # 3. Determine notification configuration based on message_type
    notification_config = get_notification_config(
        target_agent, message_type, priority_data, additional_data
    )

    if not notification_config:
        raise ValueError(f"Unknown message_type: {message_type}")

    # 4. Create notification using create_notification logic
    notification_id = f"notif-{uuid.uuid4().hex[:12]}"

    notification_data = {
        "id": notification_id,
        "target_agent": target_agent,
        "source_agent": "project_manager",
        "notification_type": message_type,
        "item_id": priority_id,
        "message": notification_config["message"],
        "priority": notification_config["priority"],
        "status": "pending",
        "sound": False,  # CFR-009: Always false
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    db.write("notifications", notification_data, action="create")

    # 5. Return results
    return {
        "success": True,
        "notification_id": notification_id,
        "target_agent": target_agent,
        "message_type": message_type,
        "priority_id": priority_id
    }

def get_notification_config(target_agent: str, message_type: str,
                           priority_data: dict, additional_data: dict) -> dict:
    """Get auto-configuration for notification based on message_type."""

    configs = {
        # Architect messages
        "architect": {
            "spec_needed": {
                "priority": "high",
                "message": f"Specification needed for {priority_data.get('id')}: {priority_data.get('title', 'TBD')}"
            },
            "spec_review": {
                "priority": "high",
                "message": f"Specification ready for review: {additional_data.get('spec_id', 'SPEC-XXX')}"
            },
            "design_guidance": {
                "priority": "medium",
                "message": f"Design guidance needed for {priority_data.get('id')}"
            }
        },

        # Code Developer messages
        "code_developer": {
            "work_available": {
                "priority": "high",
                "message": f"New work available: {priority_data.get('id')} - {priority_data.get('title', 'TBD')}"
            },
            "blocker_resolved": {
                "priority": "high",
                "message": f"Blocking issue resolved for {priority_data.get('id')}"
            },
            "review_requested": {
                "priority": "medium",
                "message": f"Code review requested for {priority_data.get('id')}"
            }
        },

        # Orchestrator messages
        "orchestrator": {
            "priority_complete": {
                "priority": "high",
                "message": f"Priority complete: {priority_data.get('id')} - {priority_data.get('title', 'TBD')}"
            },
            "priority_blocked": {
                "priority": "urgent",
                "message": f"Priority blocked: {priority_data.get('id')} - {additional_data.get('reason', 'Unknown')}"
            },
            "resource_needed": {
                "priority": "high",
                "message": f"Resource needed for {priority_data.get('id')}: {additional_data.get('resource_type', 'Unknown')}"
            }
        },

        # Code Reviewer messages
        "code_reviewer": {
            "review_available": {
                "priority": "medium",
                "message": f"Code review available: {priority_data.get('id')}"
            },
            "review_urgent": {
                "priority": "urgent",
                "message": f"Urgent code review needed: {priority_data.get('id')}"
            }
        }
    }

    # Get target agent's configs
    agent_configs = configs.get(target_agent, {})

    # Return message_type config
    return agent_configs.get(message_type)
```

## Success Criteria

- ✅ Notification sent with correct format
- ✅ Message type mapped to agent expectations
- ✅ Priority auto-configured based on message type
- ✅ CFR-009 enforced (sound=false)
- ✅ Additional data included in message

## Common Use Cases

### Example 1: Request Spec for New Priority
```json
{
  "target_agent": "architect",
  "message_type": "spec_needed",
  "priority_id": "PRIORITY-25"
}
```

Response: Architect receives notification "Specification needed for PRIORITY-25: User Authentication System"

### Example 2: Notify Developer of Available Work
```json
{
  "target_agent": "code_developer",
  "message_type": "work_available",
  "priority_id": "PRIORITY-30"
}
```

Response: Developer receives notification "New work available: PRIORITY-30 - Database Schema"

### Example 3: Notify Orchestrator of Blocked Priority
```json
{
  "target_agent": "orchestrator",
  "message_type": "priority_blocked",
  "priority_id": "PRIORITY-20",
  "additional_data": {
    "reason": "Waiting for architect specification"
  }
}
```

Response: Orchestrator receives notification "Priority blocked: PRIORITY-20 - Waiting for architect specification"

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| InvalidAgentError | Unknown target agent | Use valid agent name |
| InvalidMessageTypeError | Unknown message_type | Use valid message type for agent |
| MissingPriorityError | priority_id not found | Verify priority ID |

## CFR Compliance

- **CFR-009**: ENFORCED - sound=False (no exceptions)
- **CFR-015**: Database-first notification system
- **CFR-007**: Efficient message generation with pre-configured patterns

## Related Commands

- `project_manager.create_notification` - Low-level notification creation
- `project_manager.process_notifications` - Process incoming notifications
