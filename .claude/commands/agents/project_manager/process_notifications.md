---
command: project_manager.process_notifications
agent: project_manager
action: process_notifications
data_domain: notifications
write_tables: [notifications, roadmap_priority, roadmap_audit]
read_tables: [notifications, roadmap_priority]
required_skills: [roadmap_database_handling]
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.process_notifications

## Purpose

Process incoming notifications from other agents (status change requests, completion confirmations, etc.). Reviews pending notifications and applies approved changes to the roadmap.

## Input Parameters

```yaml
batch_size: integer      # Optional - Number of notifications to process (default: 10)
auto_approve: boolean    # Optional - Auto-approve safe changes (default: false)
filter_type: string      # Optional - Filter by notification_type
filter_source: string    # Optional - Filter by source_agent
```

## Database Operations

### READ Operations

```sql
-- Get pending notifications for project_manager
SELECT id, source_agent, notification_type, item_id, message,
       priority, created_at, payload
FROM notifications
WHERE target_agent = 'project_manager'
  AND status = 'pending'
  AND (? IS NULL OR notification_type = ?)
  AND (? IS NULL OR source_agent = ?)
ORDER BY priority DESC, created_at ASC
LIMIT ?;

-- Get related priority for status changes
SELECT id, status, spec_id, title
FROM roadmap_priority
WHERE id = ?;
```

### WRITE Operations

```sql
-- Update notification status
UPDATE notifications
SET status = ?, updated_at = ?, reviewed_at = ?
WHERE id = ?;

-- Apply priority status change
UPDATE roadmap_priority
SET status = ?, updated_at = ?, updated_by = 'project_manager'
WHERE id = ?;

-- Create audit entry
INSERT INTO roadmap_audit (
    priority_id, action, description, old_value, new_value,
    changed_by, changed_at
) VALUES (?, 'notification_processed', ?, ?, ?, 'project_manager', ?);
```

## Execution Steps

1. **Query Pending Notifications**
   - Fetch notifications with status='pending' and target_agent='project_manager'
   - Order by priority (high→low), then created_at (old→new)
   - Apply filters if provided
   - Limit to batch_size

2. **Iterate Each Notification**
   - For each pending notification:
     - Identify notification type
     - Extract item_id and requested changes
     - Determine approval criteria

3. **Review Notification**
   - Check notification type:
     - `status_change_request`: Verify DoD or auto_approve
     - `priority_update_request`: Validate changes
     - `spec_completion`: Check spec exists
     - `other_types`: Handle appropriately

4. **Make Approval Decision**
   - If auto_approve=true: approve safe changes
   - If DoD verified: approve status changes
   - Otherwise: reject with reason
   - Log decision in audit trail

5. **Apply Changes**
   - If approved: apply changes to roadmap
   - Update notification status ("approved", "rejected", "deferred")
   - Create audit entry for applied changes

6. **Update Notification Status**
   - Mark as "approved", "rejected", or "deferred"
   - Set reviewed_at timestamp
   - Include result summary

7. **Return Results**

## Output

```json
{
  "success": true,
  "processed": 3,
  "approved": 2,
  "rejected": 1,
  "deferred": 0,
  "notifications": [
    {
      "notification_id": "notif-123",
      "source_agent": "code_developer",
      "notification_type": "status_change_request",
      "item_id": "PRIORITY-25",
      "action": "approved",
      "reason": "DoD verified"
    },
    {
      "notification_id": "notif-124",
      "source_agent": "architect",
      "notification_type": "spec_completion",
      "item_id": "PRIORITY-30",
      "action": "approved",
      "reason": "Spec created and validated"
    },
    {
      "notification_id": "notif-125",
      "source_agent": "code_developer",
      "notification_type": "status_change_request",
      "item_id": "PRIORITY-20",
      "action": "rejected",
      "reason": "DoD verification required"
    }
  ]
}
```

## Implementation Pattern

```python
def process_notifications(db: DomainWrapper, params: dict):
    """Process incoming notifications from other agents."""
    from datetime import datetime

    batch_size = params.get("batch_size", 10)
    auto_approve = params.get("auto_approve", False)
    filter_type = params.get("filter_type")
    filter_source = params.get("filter_source")

    # 1. Query pending notifications
    query_params = {
        "target_agent": "project_manager",
        "status": "pending"
    }

    notifications = db.read("notifications", query_params)

    # Apply filters if provided
    if filter_type:
        notifications = [n for n in notifications if n.get("notification_type") == filter_type]

    if filter_source:
        notifications = [n for n in notifications if n.get("source_agent") == filter_source]

    # Sort by priority (high→low), then created_at (old→new)
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    notifications.sort(
        key=lambda n: (priority_order.get(n.get("priority", "medium"), 3),
                       n.get("created_at", ""))
    )

    # Limit to batch_size
    notifications = notifications[:batch_size]

    # 2. Process each notification
    results = []

    for notif in notifications:
        notification_id = notif["id"]
        notif_type = notif.get("notification_type")
        source_agent = notif.get("source_agent")
        item_id = notif.get("item_id")
        message = notif.get("message", "")

        approval_result = {
            "notification_id": notification_id,
            "source_agent": source_agent,
            "notification_type": notif_type,
            "item_id": item_id
        }

        # 3. Review and decide on approval
        if notif_type == "status_change_request":
            # Extract requested status from message
            requested_status = extract_status_from_message(message)

            # Check DoD verification
            dod_verified = check_dod_status(db, item_id) if not auto_approve else True

            if dod_verified or auto_approve:
                # Approve and apply change
                try:
                    current = db.read("roadmap_priority", {"id": item_id})
                    if current:
                        old_status = current[0].get("status")

                        db.write("roadmap_priority", {
                            "id": item_id,
                            "status": requested_status,
                            "updated_at": datetime.now().isoformat()
                        }, action="update")

                        db.write("roadmap_audit", {
                            "priority_id": item_id,
                            "action": "notification_processed",
                            "description": f"Status change approved via notification from {source_agent}",
                            "old_value": old_status,
                            "new_value": requested_status,
                            "changed_by": "project_manager",
                            "changed_at": datetime.now().isoformat()
                        }, action="create")

                        approval_result["action"] = "approved"
                        approval_result["reason"] = "DoD verified" if not auto_approve else "Auto-approved"
                except Exception as e:
                    approval_result["action"] = "rejected"
                    approval_result["reason"] = f"Error applying change: {str(e)}"
            else:
                approval_result["action"] = "rejected"
                approval_result["reason"] = "DoD verification required"

        elif notif_type == "spec_completion":
            # Check spec exists and is complete
            try:
                specs = db.read("specs_specification", {"id": item_id})
                if specs and specs[0].get("status") == "complete":
                    approval_result["action"] = "approved"
                    approval_result["reason"] = "Spec created and validated"
                else:
                    approval_result["action"] = "rejected"
                    approval_result["reason"] = "Spec incomplete or not found"
            except Exception as e:
                approval_result["action"] = "rejected"
                approval_result["reason"] = f"Error validating spec: {str(e)}"

        elif notif_type == "priority_update_request":
            # Auto-approve priority metadata updates
            try:
                # Extract update data from message
                update_data = extract_update_data(message)
                db.write("roadmap_priority", {
                    "id": item_id,
                    **update_data,
                    "updated_at": datetime.now().isoformat()
                }, action="update")

                approval_result["action"] = "approved"
                approval_result["reason"] = "Update applied"
            except Exception as e:
                approval_result["action"] = "rejected"
                approval_result["reason"] = f"Error applying update: {str(e)}"

        else:
            # Unknown notification type - defer
            approval_result["action"] = "deferred"
            approval_result["reason"] = f"Unknown notification type: {notif_type}"

        # 4. Update notification status
        status_map = {
            "approved": "approved",
            "rejected": "rejected",
            "deferred": "pending"
        }

        db.write("notifications", {
            "id": notification_id,
            "status": status_map.get(approval_result["action"], "pending"),
            "updated_at": datetime.now().isoformat()
        }, action="update")

        results.append(approval_result)

    # 5. Return summary
    approved = len([r for r in results if r["action"] == "approved"])
    rejected = len([r for r in results if r["action"] == "rejected"])
    deferred = len([r for r in results if r["action"] == "deferred"])

    return {
        "success": True,
        "processed": len(results),
        "approved": approved,
        "rejected": rejected,
        "deferred": deferred,
        "notifications": results
    }

def check_dod_status(db: DomainWrapper, priority_id: str) -> bool:
    """Check if priority's Definition of Done is verified."""
    try:
        items = db.read("roadmap_priority", {"id": priority_id})
        if items:
            return items[0].get("dod_verified", False)
    except:
        pass
    return False

def extract_status_from_message(message: str) -> str:
    """Extract status from notification message."""
    # Simple pattern: look for status emoji in message
    status_map = {
        "✅": "✅ Complete",
        "🏗️": "🏗️ In Progress",
        "📝": "📝 Planned"
    }
    for emoji, status in status_map.items():
        if emoji in message:
            return status
    return None

def extract_update_data(message: str) -> dict:
    """Extract update data from message."""
    # This would parse structured data from message
    # For now, return empty dict
    return {}
```

## Success Criteria

- ✅ Pending notifications retrieved correctly
- ✅ Each notification reviewed
- ✅ Status change applied if approved
- ✅ Rejection reason recorded if rejected
- ✅ Audit trail updated for all changes
- ✅ Notification status updated

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| NoNotificationsError | No pending notifications | Return empty results |
| ValidationError | Invalid notification format | Log error, defer notification |
| DoDVerificationError | Cannot verify DoD | Reject and ask for manual verification |
| PermissionError | Not project_manager | Only project_manager can process |

## CFR Compliance

- **CFR-009**: No sound notifications (sound=False)
- **CFR-015**: Database-first notification processing
- **CFR-007**: Efficient batch processing of notifications

## Related Commands

- `project_manager.create_notification` - Send notification
- `project_manager.send_agent_notification` - Wrapper for common patterns
- `project_manager.update_priority_status` - Update priority status
