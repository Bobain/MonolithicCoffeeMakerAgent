---
command: manage-component-library
agent: ux_design_expert
action: crud_component_library
tables: [ui_component_library]
tools: []
duration: 10m
---

## Purpose

CRUD operations on component inventory with versioning and audit trails.

## Input Parameters

```yaml
ACTION:
  type: string
  enum: [create, read, update, delete, list]
  description: CRUD action

COMPONENT_ID:
  type: string
  optional: true
  description: Component identifier (for read/update/delete)

DATA:
  type: object
  optional: true
  description: Component data (for create/update)
  properties:
    component_name: string
    category: string
    description: string
    props_schema: object
    tailwind_classes: string

FILTERS:
  type: object
  optional: true
  description: Filters for list action
  properties:
    category: string
```

## Database Operations

### CREATE, READ, UPDATE, DELETE

```sql
-- CREATE
INSERT INTO ui_component_library (...)

-- READ
SELECT * FROM ui_component_library WHERE component_id = ?

-- UPDATE
UPDATE ui_component_library SET ... WHERE component_id = ?

-- DELETE
DELETE FROM ui_component_library WHERE component_id = ?

-- LIST
SELECT * FROM ui_component_library WHERE category = ? ORDER BY component_name
```

## Success Criteria

- Operation completed successfully
- Audit trail created
- Related specs updated (if applicable)
- Database consistent

## Output Format

```json
{
  "success": true,
  "action": "create",
  "component_id": "COMP-CARD-USERCARD",
  "component_name": "UserCard",
  "category": "card",
  "message": "Component created successfully"
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Component not found | Invalid COMPONENT_ID | List available components |
| Duplicate component | Component already exists | Suggest update instead |
| Delete failed | Component in use | Show dependent specs |

## Examples

### Example 1: Create Component

```bash
/agents:ux_design_expert:manage-component-library \
  ACTION="create" \
  DATA='{
    "component_name": "UserCard",
    "category": "card",
    "description": "User information card"
  }'
```

### Example 2: List Components

```bash
/agents:ux_design_expert:manage-component-library \
  ACTION="list" \
  FILTERS={"category": "button"}
```

### Example 3: Update Component

```bash
/agents:ux_design_expert:manage-component-library \
  ACTION="update" \
  COMPONENT_ID="COMP-CARD-USERCARD" \
  DATA={"tailwind_classes": "p-6 bg-white rounded-lg shadow-lg"}
```

## Implementation Notes

- Component IDs auto-generated: `COMP-{CATEGORY}-{NAME}`
- Maintain creation and update timestamps
- Audit trail for all operations
- Check for component dependencies before delete
- Version component updates
