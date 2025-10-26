---
command: project_manager.update_metadata
agent: project_manager
action: update_metadata
data_domain: roadmap
write_tables: [roadmap_metadata, roadmap_audit]
read_tables: [roadmap_metadata]
required_skills: []
required_tools: []
cfr_compliance: [CFR-007, CFR-009, CFR-015]
---

# Command: project_manager.update_metadata

## Purpose

Update ROADMAP.md header/footer metadata (project description, goals, metrics, header information). Changes are persisted to database and can be exported to markdown.

## Input Parameters

```yaml
metadata_type: string    # Required - "header" or "footer"
content: string          # Required - New content for section
section: string          # Optional - Specific section to update (e.g., "project_goals", "team_info")
key: string              # Optional - Specific key to update (for structured metadata)
value: string            # Optional - Value for key (for key-value updates)
```

## Database Operations

### READ Operations

```sql
SELECT id, type, content, section, updated_at
FROM roadmap_metadata
WHERE type = ? AND (section = ? OR section IS NULL);
```

### WRITE Operations

```sql
-- Update or insert metadata
INSERT INTO roadmap_metadata (
    id, type, content, section, updated_at, updated_by
) VALUES (?, ?, ?, ?, ?, 'project_manager')
ON CONFLICT(id) DO UPDATE SET
    content = excluded.content,
    section = excluded.section,
    updated_at = excluded.updated_at,
    updated_by = excluded.updated_by;

-- Create audit entry
INSERT INTO roadmap_audit (
    priority_id, action, description, old_value, new_value,
    changed_by, changed_at
) VALUES (?, 'metadata_update', ?, ?, ?, 'project_manager', ?);
```

## Execution Steps

1. **Validate Input**
   - Verify metadata_type is "header" or "footer"
   - Verify content is provided (not empty)
   - Validate section if provided

2. **Load Current Metadata**
   - Query roadmap_metadata for current state
   - Store old_content for audit trail
   - Build metadata_id: `{type}_{section or default}`

3. **Prepare New Metadata**
   - If key/value provided: update structured metadata
   - If content provided: replace entire section content
   - Add timestamps and updated_by metadata

4. **Write to Database**
   - Use UPSERT pattern (INSERT OR UPDATE)
   - Write to roadmap_metadata table
   - Set updated_at and updated_by

5. **Create Audit Entry**
   - Log metadata change to roadmap_audit
   - Include old_content and new_content
   - Set action = "metadata_update"

6. **Return Results**

## Output

```json
{
  "success": true,
  "metadata_type": "header",
  "section": "project_goals",
  "updated_at": "2025-10-26T10:30:00Z",
  "audit_entry_id": "audit-12346",
  "content_preview": "## Project Goals\n\n- Goal 1\n- Goal 2"
}
```

## Implementation Pattern

```python
def update_metadata(db: DomainWrapper, params: dict):
    """Update ROADMAP metadata (header/footer)."""
    from datetime import datetime

    metadata_type = params.get("metadata_type", "").lower()
    content = params.get("content")
    section = params.get("section")
    key = params.get("key")
    value = params.get("value")

    # 1. Validate input
    if metadata_type not in ["header", "footer"]:
        raise ValueError(f"Invalid metadata_type: {metadata_type}. Must be 'header' or 'footer'")

    if not content and not (key and value):
        raise ValueError("Must provide either 'content' or both 'key' and 'value'")

    # 2. Load current metadata
    query_section = section or f"{metadata_type}_default"
    current_items = db.read("roadmap_metadata", {
        "type": metadata_type,
        "section": query_section
    })

    old_content = ""
    if current_items:
        old_content = current_items[0].get("content", "")

    # 3. Prepare new metadata
    metadata_id = f"{metadata_type}_{section or 'default'}"

    if key and value:
        # Update structured metadata (key-value)
        current_dict = {}
        if old_content:
            try:
                import json
                current_dict = json.loads(old_content)
            except (json.JSONDecodeError, ValueError):
                current_dict = {}

        current_dict[key] = value
        import json
        new_content = json.dumps(current_dict, indent=2)
    else:
        # Replace entire section content
        new_content = content

    # 4. Write to database
    db.write("roadmap_metadata", {
        "id": metadata_id,
        "type": metadata_type,
        "content": new_content,
        "section": query_section,
        "updated_at": datetime.now().isoformat(),
        "updated_by": "project_manager"
    }, action="update")

    # 5. Create audit entry
    db.write("roadmap_audit", {
        "priority_id": metadata_id,
        "action": "metadata_update",
        "description": f"Updated {metadata_type} metadata - {section or 'default'}",
        "old_value": old_content[:200] if old_content else None,
        "new_value": new_content[:200] if new_content else None,
        "changed_by": "project_manager",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    # 6. Return results
    return {
        "success": True,
        "metadata_type": metadata_type,
        "section": section or "default",
        "updated_at": datetime.now().isoformat(),
        "content_preview": new_content[:100] + "..." if len(new_content) > 100 else new_content
    }
```

## Metadata Sections

### Header Metadata

Common sections:
- `project_description` - High-level project overview
- `project_goals` - Strategic goals for the project
- `team_info` - Team members and roles
- `quick_links` - Quick reference links
- `status_summary` - Current project status

### Footer Metadata

Common sections:
- `last_updated` - Last update timestamp
- `metrics_summary` - Key metrics
- `next_milestones` - Upcoming milestones
- `contact_info` - Contact information
- `related_docs` - Related documentation links

## Success Criteria

- ✅ Metadata updated in database
- ✅ Audit trail created
- ✅ Old value captured for rollback capability
- ✅ Updated_at and updated_by set correctly
- ✅ Content preview returned

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| InvalidTypeError | metadata_type not "header" or "footer" | Use valid type |
| MissingContentError | Neither content nor key/value provided | Provide content or key/value pair |
| ValidationError | Invalid section name | Check section parameter |
| PermissionError | Not project_manager | Only project_manager can update metadata |

## CFR Compliance

- **CFR-009**: No sound notifications (sound=False)
- **CFR-015**: Database-first storage, no direct file modifications
- **CFR-007**: Efficient metadata updates with minimal overhead

## Related Commands

- `project_manager.parse_roadmap` - Parse and sync ROADMAP.md
- `project_manager.create_roadmap_audit` - Manual audit log entry
- `project_manager.create_roadmap_report` - Generate status report
