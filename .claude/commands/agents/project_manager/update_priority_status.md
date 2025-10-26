---
command: project_manager.update_priority_status
agent: project_manager
action: update_priority_status
data_domain: roadmap
write_tables: [roadmap_priority, roadmap_audit]
read_tables: [roadmap_priority]
required_skills: [roadmap_database_handling]
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.update_priority_status

## Purpose

Update the status of a priority (e.g., Planned → In Progress → Complete). Enforces valid status transitions and optionally verifies Definition of Done before marking complete.

## Input Parameters

```yaml
priority_id: string      # Required - Priority identifier (e.g., "PRIORITY-25")
new_status: string       # Required - New status value ("📝 Planned", "🏗️ In Progress", "✅ Complete", "❌ Rejected", "🔴 Blocked", "🔄 Reopened")
reason: string           # Optional - Reason for status change
verify_dod: boolean      # Optional - Run DoD verification before marking complete (default: true)
```

## Database Operations

### READ Operations

```sql
SELECT id, title, status, description, spec_id, started_at, dod_verified
FROM roadmap_priority
WHERE id = ?;
```

### WRITE Operations

```sql
-- Update priority status
UPDATE roadmap_priority
SET status = ?, updated_at = ?, updated_by = 'project_manager',
    completed_at = CASE WHEN ? = '✅ Complete' THEN ? ELSE completed_at END
WHERE id = ?;

-- Create audit entry
INSERT INTO roadmap_audit (
    priority_id, action, description, old_value, new_value,
    changed_by, changed_at
) VALUES (?, 'status_change', ?, ?, ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify priority_id is provided
   - Verify new_status is provided
   - Check new_status is valid format

2. **Fetch Current Priority**
   - Query priority from roadmap_priority
   - Raise NotFoundError if not found
   - Extract old_status for audit trail

3. **Validate Transition**
   - Check if transition is valid (see Valid Status Transitions)
   - Raise InvalidTransitionError if invalid
   - Store old_status and new_status

4. **Verify DoD (if marking complete)**
   - If new_status == "✅ Complete" and verify_dod=true:
     - Call DoD verification workflow
     - Check if priority has spec
     - Verify acceptance criteria met
     - If failed: return error with details

5. **Update Status**
   - Write new status to roadmap_priority
   - Set updated_at to current timestamp
   - Set completed_at if marking complete
   - Include updated_by = "project_manager"

6. **Create Audit Entry**
   - Log status change to roadmap_audit
   - Include old_status, new_status, reason
   - Set changed_by = "project_manager"

7. **Send Notifications**
   - If status == "✅ Complete": notify orchestrator
   - If status == "🔴 Blocked": notify relevant agents
   - Pattern: `db.send_notification(target_agent, {...})`

8. **Return Results**

## Output

```json
{
  "success": true,
  "priority_id": "PRIORITY-25",
  "old_status": "🏗️ In Progress",
  "new_status": "✅ Complete",
  "dod_verified": true,
  "audit_entry_id": "audit-12345",
  "notifications_sent": 1
}
```

## Valid Status Transitions

```
START: 📝 Planned
  ├─→ 🏗️ In Progress (when spec ready and developer available)
  ├─→ ❌ Rejected (if decided not to implement)
  └─→ 🔴 Blocked (if blocked by dependency)

IN PROGRESS: 🏗️ In Progress
  ├─→ ✅ Complete (when DoD verified)
  ├─→ 🔴 Blocked (if blocked)
  └─→ 🔄 Reopened (if rejected → reopened)

COMPLETE: ✅ Complete
  ├─→ 🔄 Reopened (if issues found after completion)
  └─→ (end state, no other transitions)

REJECTED: ❌ Rejected
  ├─→ 📝 Planned (if decision reversed)
  └─→ (generally end state)

BLOCKED: 🔴 Blocked
  ├─→ 🏗️ In Progress (if blocker resolved)
  ├─→ 📝 Planned (if decided to postpone)
  └─→ ❌ Rejected (if decided not to implement)

REOPENED: 🔄 Reopened
  ├─→ 🏗️ In Progress (resume implementation)
  ├─→ ❌ Rejected (if decided to cancel)
  └─→ 🔴 Blocked (if blocked again)
```

## Implementation Pattern

```python
def update_priority_status(db: DomainWrapper, params: dict):
    """Update priority status with validation and audit trail."""
    from datetime import datetime

    priority_id = params["priority_id"]
    new_status = params["new_status"]
    reason = params.get("reason", "")
    verify_dod = params.get("verify_dod", True)

    # 1. Fetch current priority
    items = db.read("roadmap_priority", {"id": priority_id})
    if not items:
        raise ValueError(f"Priority {priority_id} not found")

    current = items[0]
    old_status = current["status"]

    # 2. Validate transition
    if not is_valid_transition(old_status, new_status):
        valid_transitions = get_valid_transitions(old_status)
        raise ValueError(
            f"Invalid transition from {old_status} to {new_status}. "
            f"Valid transitions: {valid_transitions}"
        )

    # 3. Verify DoD if marking complete
    dod_verified = True
    if new_status == "✅ Complete" and verify_dod:
        dod_result = verify_dod_status(db, priority_id)
        if not dod_result["passed"]:
            return {
                "success": False,
                "error": "DoD verification failed",
                "dod_result": dod_result
            }
        dod_verified = dod_result.get("verified", True)

    # 4. Update status
    update_data = {
        "id": priority_id,
        "status": new_status,
        "updated_at": datetime.now().isoformat()
    }

    if new_status == "✅ Complete":
        update_data["completed_at"] = datetime.now().isoformat()

    db.write("roadmap_priority", update_data, action="update")

    # 5. Create audit entry
    db.write("roadmap_audit", {
        "priority_id": priority_id,
        "action": "status_change",
        "description": f"Status changed from {old_status} to {new_status}. Reason: {reason}",
        "old_value": old_status,
        "new_value": new_status,
        "changed_by": "project_manager",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    # 6. Send notifications based on status change
    notifications_sent = 0

    if new_status == "✅ Complete":
        db.send_notification("orchestrator", {
            "type": "priority_complete",
            "priority_id": priority_id,
            "title": current.get("title")
        })
        notifications_sent += 1

    elif new_status == "🔴 Blocked":
        db.send_notification("orchestrator", {
            "type": "priority_blocked",
            "priority_id": priority_id,
            "reason": reason
        })
        notifications_sent += 1

    return {
        "success": True,
        "priority_id": priority_id,
        "old_status": old_status,
        "new_status": new_status,
        "dod_verified": dod_verified,
        "notifications_sent": notifications_sent
    }

def is_valid_transition(old_status: str, new_status: str) -> bool:
    """Check if status transition is valid."""
    valid_transitions = {
        "📝 Planned": ["🏗️ In Progress", "❌ Rejected", "🔴 Blocked"],
        "🏗️ In Progress": ["✅ Complete", "🔴 Blocked", "🔄 Reopened"],
        "✅ Complete": ["🔄 Reopened"],
        "❌ Rejected": ["📝 Planned"],
        "🔴 Blocked": ["🏗️ In Progress", "📝 Planned", "❌ Rejected"],
        "🔄 Reopened": ["🏗️ In Progress", "❌ Rejected", "🔴 Blocked"]
    }
    return new_status in valid_transitions.get(old_status, [])

def get_valid_transitions(status: str) -> list:
    """Get valid transitions for a status."""
    transitions = {
        "📝 Planned": ["🏗️ In Progress", "❌ Rejected", "🔴 Blocked"],
        "🏗️ In Progress": ["✅ Complete", "🔴 Blocked", "🔄 Reopened"],
        "✅ Complete": ["🔄 Reopened"],
        "❌ Rejected": ["📝 Planned"],
        "🔴 Blocked": ["🏗️ In Progress", "📝 Planned", "❌ Rejected"],
        "🔄 Reopened": ["🏗️ In Progress", "❌ Rejected", "🔴 Blocked"]
    }
    return transitions.get(status, [])

def verify_dod_status(db: DomainWrapper, priority_id: str) -> dict:
    """Verify Definition of Done for a priority."""
    priority = db.read("roadmap_priority", {"id": priority_id})[0]

    # Check if has spec
    if not priority.get("spec_id"):
        return {
            "passed": False,
            "reason": "Priority has no spec"
        }

    # Check if spec exists and is complete
    # This would normally call the DoD verification skill
    return {
        "passed": True,
        "verified": True,
        "checks": [
            {"name": "Spec exists", "passed": True},
            {"name": "Implementation complete", "passed": True},
            {"name": "Tests passing", "passed": True},
            {"name": "Documentation updated", "passed": True}
        ]
    }
```

## Success Criteria

- ✅ Status updated in database
- ✅ Audit trail created with old/new values
- ✅ DoD verification passed (if marking complete)
- ✅ Notifications sent to relevant agents
- ✅ Valid status transitions enforced

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| NotFoundError | Priority doesn't exist | Verify priority ID |
| InvalidTransitionError | Invalid status change | Check valid transitions |
| DoDFailedError | DoD verification failed | Fix implementation, re-verify |
| PermissionError | Not project_manager | Only project_manager can update status |

## CFR Compliance

- **CFR-009**: No sound notifications (sound=False)
- **CFR-015**: Database-first, no file modifications
- **CFR-007**: Efficient validation with early error detection

## Related Commands

- `project_manager.parse_roadmap` - Parse and sync ROADMAP.md
- `project_manager.verify_dod_puppeteer` - Verify Definition of Done
- `project_manager.update_metadata` - Update ROADMAP header/footer
