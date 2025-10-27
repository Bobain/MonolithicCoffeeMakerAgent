---
command: create-component-spec
agent: ux_design_expert
action: create_component_specification
tables: [ui_component_library]
tools: [llm]
duration: 20m
---

## Purpose

Define reusable component structure with props schema and accessibility notes.

## Input Parameters

```yaml
COMPONENT_NAME:
  type: string
  description: Component name (PascalCase)
  example: "UserCard"

CATEGORY:
  type: string
  enum: [button, input, card, list, modal, form, layout, navigation]
  description: Component category

DESCRIPTION:
  type: string
  description: Component purpose and usage

PROPS_SCHEMA:
  type: object
  description: JSON schema defining component props

TAILWIND_CLASSES:
  type: string
  optional: true
  description: Default Tailwind CSS classes

ACCESSIBILITY_NOTES:
  type: string
  optional: true
  description: WCAG accessibility requirements
```

## Database Operations

### INSERT ui_component_library

```sql
INSERT INTO ui_component_library (
    component_id, component_name, category, description,
    props_schema, tailwind_classes, accessibility_notes,
    created_at, updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
```

## Success Criteria

- Component ID generated
- Props schema validated
- Tailwind classes specified
- Accessibility notes included
- Database record created

## Output Format

```json
{
  "success": true,
  "component_id": "COMP-USER-CARD",
  "component_name": "UserCard",
  "category": "card",
  "version": "1.0.0",
  "props_schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "avatar": {"type": "string"},
      "role": {"type": "string"}
    }
  },
  "tailwind_classes": "p-4 bg-white rounded-lg shadow-md",
  "accessibility_notes": "Implements ARIA labels and keyboard navigation",
  "message": "Component specification created"
}
```

## Props Schema Format

```json
{
  "type": "object",
  "properties": {
    "prop_name": {
      "type": "string|number|boolean|array|object",
      "required": true,
      "description": "Prop description",
      "default": "default_value"
    }
  }
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid category | CATEGORY not in enum | List valid categories |
| Invalid props | Schema format error | Show schema example |
| LLM error | API call failed | Retry up to 3 times |

## Examples

### Example 1: Card Component

```bash
/agents:ux_design_expert:create-component-spec \
  COMPONENT_NAME="UserCard" \
  CATEGORY="card" \
  DESCRIPTION="Displays user information with avatar and actions" \
  PROPS_SCHEMA='{
    "type": "object",
    "properties": {
      "name": {"type": "string", "required": true},
      "avatar": {"type": "string", "required": true},
      "role": {"type": "string"}
    }
  }' \
  TAILWIND_CLASSES="p-4 bg-white rounded-lg shadow-md hover:shadow-lg"
```

### Example 2: Button Component

```bash
/agents:ux_design_expert:create-component-spec \
  COMPONENT_NAME="Button" \
  CATEGORY="button" \
  DESCRIPTION="Reusable button component with variants" \
  PROPS_SCHEMA='{
    "type": "object",
    "properties": {
      "label": {"type": "string", "required": true},
      "variant": {"type": "string", "enum": ["primary", "secondary"]},
      "size": {"type": "string", "enum": ["sm", "md", "lg"]}
    }
  }'
```

## Implementation Notes

- Component IDs use format: `COMP-{CATEGORY}-{NAME}` (e.g., COMP-CARD-USERCARD)
- Props schema should follow JSON Schema standard
- Include Tailwind classes for styling consistency
- Document accessibility requirements (ARIA labels, keyboard support)
- Store usage examples for developers
- Support multiple variants per component
