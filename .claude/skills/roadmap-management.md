# Skill: ROADMAP Management

**Name**: `roadmap-management`
**Owner**: ALL agents (read access), ONLY project_manager/orchestrator (write access)
**Purpose**: Interact with database-backed ROADMAP using access control
**Priority**: CRITICAL - Single source of truth for project priorities

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ Reading current ROADMAP priorities and user stories
- ✅ Checking status of specific items
- ✅ Requesting status updates (via notifications)
- ✅ Approving/rejecting update requests (project_manager/orchestrator ONLY)
- ✅ Importing from or exporting to ROADMAP.md file

**Example Triggers**:
```python
# code_developer: Read next planned item
next_item = get_next_planned_item()

# code_developer: Request status update after completing work
request_roadmap_update(
    item_id="US-062",
    new_status="✅ Complete",
    message="Database migration complete, all tests passing"
)

# project_manager: Review and approve pending notifications
notifications = get_pending_roadmap_notifications()
approve_roadmap_notification(notification_id=5, notes="Verified")
```

---

## Architecture: Database-Backed ROADMAP with Access Control

**CRITICAL PRINCIPLE**: ROADMAP is stored in SQLite database, NOT directly edited in markdown files.

```
File System:                    Database:
docs/roadmap/ROADMAP.md ←→ roadmap_items table
                           roadmap_metadata table
                           roadmap_audit table
                           roadmap_update_notifications table
```

**Access Control**:
- 📖 **Read**: ALL agents can read items
- 🔒 **Write**: ONLY project_manager and orchestrator can modify items
- 📬 **Notifications**: Other agents create persistent update requests

**Benefits**:
- Concurrent access without file conflicts
- Complete audit trail of all changes
- Persistent notification workflow
- Bidirectional sync with markdown files

---

## Skill Execution Steps

### Step 1: Import RoadmapDatabase

**ALWAYS** import from the correct module:

```python
from pathlib import Path
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase
```

**Initialize**:
```python
db = RoadmapDatabase()  # Uses default path: data/roadmap.db
# OR with custom path:
db = RoadmapDatabase(db_path=Path("custom/roadmap.db"))
```

---

### Step 2: Reading ROADMAP Items (ALL agents)

**Use Case**: Check current priorities, find next work item

**Method**: `db.get_all_items(status_filter=None)`

**Example 1: Get all items**
```python
def check_current_priorities(self):
    """Get overview of all ROADMAP items."""
    db = RoadmapDatabase()
    items = db.get_all_items()

    for item in items:
        print(f"{item['id']}: {item['title']} - {item['status']}")

    return items
```

**Example 2: Filter by status**
```python
def get_in_progress_items(self):
    """Get all items currently in progress."""
    db = RoadmapDatabase()
    items = db.get_all_items(status_filter="🔄 In Progress")
    return items
```

**Example 3: Get next planned item**
```python
def get_next_work_item(self):
    """Get the first planned item from ROADMAP."""
    db = RoadmapDatabase()
    next_item = db.get_next_planned()

    if next_item:
        print(f"Next: {next_item['id']} - {next_item['title']}")
        return next_item
    else:
        print("No planned items remaining!")
        return None
```

---

### Step 3: Requesting Updates (ALL agents EXCEPT project_manager)

**CRITICAL**: Agents CANNOT directly modify ROADMAP. They must create notification requests.

**Use Case**: code_developer completes work and wants to update status

**Method**: `db.create_update_notification(item_id, requested_by, notification_type, requested_status, message)`

**Example 1: Request status update**
```python
def request_completion_update(self, item_id: str, completion_message: str):
    """Request ROADMAP status update to Complete."""
    db = RoadmapDatabase()

    notification_id = db.create_update_notification(
        item_id=item_id,
        requested_by="code_developer",  # Your agent type
        notification_type="status_update",
        requested_status="✅ Complete",
        message=completion_message
    )

    logger.info(f"📬 Created notification {notification_id} for {item_id}")
    return notification_id
```

**Example 2: Request status change to In Progress**
```python
def request_start_work(self, item_id: str):
    """Notify that work has started on item."""
    db = RoadmapDatabase()

    db.create_update_notification(
        item_id=item_id,
        requested_by="code_developer",
        notification_type="status_update",
        requested_status="🔄 In Progress",
        message=f"Started implementation of {item_id}"
    )
```

**Notification Types**:
- `"status_update"` - Request status change (most common)
- `"new_item"` - Request adding new priority (rare)
- `"modify_content"` - Request content changes (rare)

---

### Step 4: Reviewing Notifications (project_manager/orchestrator ONLY)

**Use Case**: project_manager checks pending update requests

**Method**: `db.get_pending_notifications(item_id=None)`

**Example: Review all pending notifications**
```python
def review_pending_updates(self):
    """Review all pending ROADMAP update requests."""
    db = RoadmapDatabase()
    notifications = db.get_pending_notifications()

    for notif in notifications:
        print(f"📬 Notification {notif['id']}:")
        print(f"   Requested by: {notif['requested_by']}")
        print(f"   Item: {notif['item_id']}")
        print(f"   Type: {notif['notification_type']}")
        print(f"   Requested status: {notif['requested_status']}")
        print(f"   Message: {notif['message']}")
        print(f"   Created: {notif['created_at']}")

    return notifications
```

---

### Step 5: Approving Notifications (project_manager/orchestrator ONLY)

**CRITICAL**: ONLY project_manager and orchestrator can approve notifications.

**Use Case**: Verify agent's work and apply the requested update

**Method**: `db.approve_notification(notification_id, processed_by, notes)`

**Example: Approve status update**
```python
def approve_completion(self, notification_id: int):
    """Approve code_developer's completion notification."""
    db = RoadmapDatabase()

    # Get notification details first
    notifications = db.get_pending_notifications()
    notif = next((n for n in notifications if n['id'] == notification_id), None)

    if not notif:
        logger.error(f"Notification {notification_id} not found")
        return False

    # Verify work is complete (check tests, review code, etc.)
    if self._verify_work_complete(notif['item_id']):
        # Approve and apply the update
        success = db.approve_notification(
            notification_id=notification_id,
            processed_by="project_manager",
            notes="Verified: all tests passing, code reviewed"
        )

        if success:
            # Export updated ROADMAP to markdown file
            db.export_to_file(Path("docs/roadmap/ROADMAP.md"))
            logger.info(f"✅ Approved and exported ROADMAP update")

        return success
    else:
        # Reject if work not complete
        return self.reject_completion(notification_id, "Tests still failing")
```

**Side Effects of Approval**:
1. Roadmap item is updated with requested changes
2. Notification is marked as 'approved'
3. Change is logged in audit trail
4. You must export to file to persist to ROADMAP.md

---

### Step 6: Rejecting Notifications (project_manager/orchestrator ONLY)

**Use Case**: Work is not complete, request needs more work

**Method**: `db.reject_notification(notification_id, processed_by, reason)`

**Example: Reject with feedback**
```python
def reject_completion(self, notification_id: int, reason: str):
    """Reject notification and provide feedback."""
    db = RoadmapDatabase()

    success = db.reject_notification(
        notification_id=notification_id,
        processed_by="project_manager",
        reason=reason
    )

    if success:
        # Optionally send message back to requesting agent
        logger.info(f"❌ Rejected notification {notification_id}: {reason}")

    return success
```

**Example Rejection Reasons**:
- "Tests still failing - 3 unit tests need fixes"
- "Implementation incomplete - missing error handling"
- "DoD not met - documentation pending"
- "CI checks failing - pre-commit hooks need fixes"

---

### Step 7: Import/Export (project_manager/orchestrator ONLY)

**Use Case**: Sync between database and markdown file

**Method**: `db.import_from_file(roadmap_path)` and `db.export_to_file(roadmap_path)`

**Example 1: Import from markdown**
```python
def import_roadmap_from_file(self):
    """Import ROADMAP.md into database."""
    db = RoadmapDatabase()
    roadmap_path = Path("docs/roadmap/ROADMAP.md")

    items_imported = db.import_from_file(roadmap_path)
    logger.info(f"✅ Imported {items_imported} items from ROADMAP.md")

    return items_imported
```

**Example 2: Export to markdown**
```python
def export_roadmap_to_file(self):
    """Export database to ROADMAP.md file."""
    db = RoadmapDatabase()
    roadmap_path = Path("docs/roadmap/ROADMAP.md")

    db.export_to_file(roadmap_path)
    logger.info(f"✅ Exported ROADMAP to {roadmap_path}")
```

**When to Export**:
- After approving notifications
- After manual database updates
- Before committing to git
- For human review

---

## Complete Workflow Examples

### Workflow 1: code_developer Completes Work

```python
# code_developer agent:
def complete_priority(self, priority_id: str):
    """Complete work on a priority and request status update."""
    # 1. Read current status
    db = RoadmapDatabase()
    items = db.get_all_items()
    item = next((i for i in items if i['id'] == priority_id), None)

    if not item:
        logger.error(f"Item {priority_id} not found")
        return

    # 2. Do the work
    self.implement_priority(item)

    # 3. Run tests
    if self.run_tests():
        # 4. Request status update
        db.create_update_notification(
            item_id=priority_id,
            requested_by="code_developer",
            notification_type="status_update",
            requested_status="✅ Complete",
            message=f"Implementation complete:\n"
                    f"- All features implemented\n"
                    f"- Tests passing: 100%\n"
                    f"- Documentation updated"
        )
        logger.info(f"📬 Requested completion approval for {priority_id}")
```

### Workflow 2: project_manager Reviews and Approves

```python
# project_manager agent:
def process_completion_requests(self):
    """Review and process all completion requests."""
    db = RoadmapDatabase()

    # 1. Get all pending notifications
    notifications = db.get_pending_notifications()

    for notif in notifications:
        if notif['notification_type'] != 'status_update':
            continue

        # 2. Verify work is complete
        item_id = notif['item_id']

        if self._verify_tests_passing(item_id):
            # 3. Approve
            db.approve_notification(
                notification_id=notif['id'],
                processed_by="project_manager",
                notes="Verified: tests passing, code reviewed"
            )
            logger.info(f"✅ Approved {item_id}")
        else:
            # 4. Reject with reason
            db.reject_notification(
                notification_id=notif['id'],
                processed_by="project_manager",
                reason="Tests failing - see CI output"
            )
            logger.info(f"❌ Rejected {item_id}")

    # 5. Export updated ROADMAP
    db.export_to_file(Path("docs/roadmap/ROADMAP.md"))
    logger.info("✅ Exported updated ROADMAP")
```

---

## Access Control Summary

| Operation | ALL Agents | project_manager | orchestrator |
|-----------|-----------|-----------------|--------------|
| `get_all_items()` | ✅ | ✅ | ✅ |
| `get_next_planned()` | ✅ | ✅ | ✅ |
| `create_update_notification()` | ✅ | ❌ (use direct update) | ❌ (use direct update) |
| `get_pending_notifications()` | ❌ | ✅ | ✅ |
| `approve_notification()` | ❌ | ✅ | ✅ |
| `reject_notification()` | ❌ | ✅ | ✅ |
| `update_status()` | ❌ | ✅ | ✅ |
| `import_from_file()` | ❌ | ✅ | ✅ |
| `export_to_file()` | ❌ | ✅ | ✅ |

---

## Error Handling

**Common Errors**:

1. **Item Not Found**
```python
items = db.get_all_items()
item = next((i for i in items if i['id'] == 'US-999'), None)
if not item:
    logger.error("Item US-999 not found in ROADMAP")
    return
```

2. **Notification Already Processed**
```python
success = db.approve_notification(notification_id, "project_manager")
if not success:
    logger.warning(f"Notification {notification_id} may be already processed")
```

3. **Access Denied** (skill doesn't enforce, but logs warning)
```python
# code_developer trying to directly update:
# db.update_status("US-062", "✅ Complete", "code_developer")  # DON'T DO THIS
# Instead, create notification:
db.create_update_notification("US-062", "code_developer", "status_update", "✅ Complete", "Work complete")
```

---

## Database Schema Reference

**roadmap_items table**:
- `id`: Item ID (US-062, PRIORITY-1)
- `item_type`: 'user_story' or 'priority'
- `number`: Numeric part (062, 1)
- `title`: Item title
- `status`: 📝 Planned, 🔄 In Progress, ✅ Complete
- `content`: Full markdown content
- `section_order`: Order in file (for export)
- `updated_by`: Last agent to update

**roadmap_update_notifications table**:
- `id`: Notification ID
- `item_id`: Which item to update
- `requested_by`: Agent requesting update
- `notification_type`: status_update, new_item, modify_content
- `requested_status`: Requested new status
- `message`: Agent's explanation
- `status`: pending, approved, rejected
- `processed_by`: Who approved/rejected
- `notes`: Approval/rejection notes

**roadmap_audit table**:
- Complete history of all changes
- Tracks who changed what and when

---

## Best Practices

1. **Always Read Before Write**: Check current state before requesting updates
2. **Provide Context**: Include detailed messages in notifications
3. **Export After Approval**: Always export to markdown after approving notifications
4. **Verify Before Approval**: project_manager should verify work before approving
5. **Clear Rejection Reasons**: Provide actionable feedback when rejecting
6. **Use Appropriate Agent**: Don't use code_developer context to approve its own requests

---

## Integration with Existing Systems

**RoadmapParser**: Will be updated to query database instead of parsing files

**BaseAgent**: Can include helper methods:
```python
class BaseAgent:
    def _get_current_roadmap_item(self) -> Optional[Dict]:
        """Get current work item from ROADMAP."""
        db = RoadmapDatabase()
        return db.get_next_planned()

    def _request_roadmap_completion(self, item_id: str, message: str):
        """Request completion of current work item."""
        db = RoadmapDatabase()
        return db.create_update_notification(
            item_id=item_id,
            requested_by=self.agent_type.value,
            notification_type="status_update",
            requested_status="✅ Complete",
            message=message
        )
```

---

**Last Updated**: 2025-10-21
**Status**: Production ✅
**Replaces**: Direct file editing of docs/roadmap/ROADMAP.md
