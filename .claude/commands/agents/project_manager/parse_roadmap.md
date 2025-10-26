---
command: project_manager.parse_roadmap
agent: project_manager
action: parse_roadmap
data_domain: roadmap
write_tables: [roadmap_priority, roadmap_audit]
read_tables: [roadmap_priority]
required_skills: [roadmap_database_handling]
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.parse_roadmap

## Purpose

Parse ROADMAP.md file and sync all priorities to database. Performs diff detection to identify new, updated, and removed priorities.

## Input Parameters

```yaml
roadmap_file: string     # Path to ROADMAP.md (default: "docs/roadmap/ROADMAP.md")
force_sync: boolean      # Force full resync (default: false)
dry_run: boolean         # Preview changes without writing (default: false)
```

## Database Operations

### READ Operations

Query current roadmap state to detect changes:

```sql
SELECT id, title, status, description, estimated_hours,
       priority_number, created_at, updated_at
FROM roadmap_priority
ORDER BY priority_number;
```

### WRITE Operations

Insert, update, or remove priorities based on diff:

```sql
-- Insert new priority
INSERT INTO roadmap_priority (
    id, title, description, status, priority_number,
    estimated_hours, created_at, updated_at, updated_by
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'project_manager');

-- Update existing priority
UPDATE roadmap_priority
SET title = ?, description = ?, status = ?,
    estimated_hours = ?, updated_at = ?, updated_by = 'project_manager'
WHERE id = ?;

-- Create audit entry
INSERT INTO roadmap_audit (
    priority_id, action, description, old_value, new_value,
    changed_by, changed_at
) VALUES (?, ?, ?, ?, ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify roadmap_file path exists
   - Confirm file is readable
   - Check format is valid markdown

2. **Read ROADMAP.md**
   - Parse markdown content
   - Extract priority sections (lines matching pattern: `## PRIORITY-\d+:`)
   - Extract status indicators (📝, 🏗️, ✅, ❌, 🔴, 🔄)
   - Parse priority metadata (title, description, status)

3. **Load Current Database State**
   - Query all priorities from roadmap_priority
   - Build map of current_id → current_data
   - Create set of current_ids

4. **Perform Diff Analysis**
   - Extract new priority IDs from markdown
   - Identify added priorities: new_ids - current_ids
   - Identify removed priorities: current_ids - new_ids
   - Identify updated priorities: new_ids & current_ids
   - For updated: check if fields actually changed

5. **Apply Changes (if not dry_run)**
   - Insert new priorities (action="create")
   - Update existing priorities (action="update")
   - Create audit entries for each change
   - Track spec notification needs

6. **Send Notifications**
   - For new planned priorities: notify architect if spec_id missing
   - Pattern: `db.send_notification("architect", {...})`

7. **Return Results**

## Output

```json
{
  "success": true,
  "priorities_added": 3,
  "priorities_updated": 5,
  "priorities_removed": 1,
  "spec_notifications_sent": 2,
  "audit_entries_created": 9,
  "dry_run": false
}
```

## Implementation Pattern

```python
def parse_roadmap(db: DomainWrapper, params: dict):
    """Parse ROADMAP.md and sync to database."""
    import re
    from pathlib import Path

    # 1. Read file
    roadmap_file = Path(params.get("roadmap_file", "docs/roadmap/ROADMAP.md"))
    if not roadmap_file.exists():
        raise FileNotFoundError(f"ROADMAP.md not found at {roadmap_file}")

    content = roadmap_file.read_text()
    dry_run = params.get("dry_run", False)

    # 2. Parse priorities from markdown
    priority_pattern = r"^## (PRIORITY-\d+):\s+(.+)$"
    status_pattern = r"(📝|🏗️|✅|❌|🔴|🔄)\s+(.+)$"

    priorities = []
    current_priority = None

    for line in content.split('\n'):
        match = re.match(priority_pattern, line)
        if match:
            current_priority = {
                "id": match.group(1),
                "title": match.group(2).strip()
            }
            # Extract status from title if present
            status_match = re.search(status_pattern, current_priority["title"])
            if status_match:
                status_emoji = status_match.group(1)
                current_priority["title"] = current_priority["title"][:status_match.start()].strip()
                current_priority["status"] = map_emoji_to_status(status_emoji)
            priorities.append(current_priority)

    # 3. Get current database state
    current_items = db.read("roadmap_priority")
    current_ids = {item["id"] for item in current_items}

    # 4. Identify changes
    new_ids = {p["id"] for p in priorities}
    added = new_ids - current_ids
    removed = current_ids - new_ids
    updated = new_ids & current_ids

    added_count = 0
    updated_count = 0
    removed_count = 0
    audit_count = 0
    spec_notifs = 0

    if not dry_run:
        # 5. Apply changes
        for priority in priorities:
            if priority["id"] in added:
                db.write("roadmap_priority", priority, action="create")
                audit_count += 1
                added_count += 1

                # Check if needs spec
                if priority.get("status") == "📝 Planned" and not priority.get("spec_id"):
                    db.send_notification("architect", {
                        "type": "spec_needed",
                        "priority_id": priority["id"],
                        "title": priority["title"]
                    })
                    spec_notifs += 1

            elif priority["id"] in updated:
                current = next(i for i in current_items if i["id"] == priority["id"])
                if has_changes(current, priority):
                    db.write("roadmap_priority", priority, action="update")
                    audit_count += 1
                    updated_count += 1
    else:
        added_count = len(added)
        updated_count = len([p for p in priorities if p["id"] in updated and has_changes(
            next(i for i in current_items if i["id"] == p["id"]), p)])
        removed_count = len(removed)

    return {
        "success": True,
        "priorities_added": added_count,
        "priorities_updated": updated_count,
        "priorities_removed": len(removed) if not dry_run else len(removed),
        "spec_notifications_sent": spec_notifs,
        "audit_entries_created": audit_count,
        "dry_run": dry_run
    }

def map_emoji_to_status(emoji: str) -> str:
    """Map emoji to status string."""
    mapping = {
        "📝": "📝 Planned",
        "🏗️": "🏗️ In Progress",
        "✅": "✅ Complete",
        "❌": "❌ Rejected",
        "🔴": "🔴 Blocked",
        "🔄": "🔄 Reopened"
    }
    return mapping.get(emoji, "📝 Planned")

def has_changes(current: dict, priority: dict) -> bool:
    """Check if priority fields have changed."""
    for key in ["title", "description", "status"]:
        if current.get(key) != priority.get(key):
            return True
    return False
```

## Success Criteria

- ✅ All priorities from ROADMAP.md synced to database
- ✅ Diff detection identifies changes (added/updated/removed)
- ✅ Audit trail created for all changes
- ✅ Notifications sent for priorities needing specs
- ✅ Priority order preserved
- ✅ Dry-run mode works without persisting changes

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| FileNotFoundError | ROADMAP.md missing | Check file path, create template |
| ParseError | Malformed markdown | Fix markdown syntax, validate format |
| DuplicateIDError | Multiple priorities with same ID | Consolidate duplicates, update IDs |
| PermissionError | Cannot write to database | Verify agent is project_manager |

## CFR Compliance

- **CFR-009**: No sound notifications (sound=False)
- **CFR-015**: Database-first operations, no file writes
- **CFR-007**: Context-efficient parsing with early detection

## Related Commands

- `project_manager.update_priority_status` - Change priority status
- `project_manager.update_metadata` - Update ROADMAP header/footer
- `project_manager.create_roadmap_audit` - Manual audit log entry
