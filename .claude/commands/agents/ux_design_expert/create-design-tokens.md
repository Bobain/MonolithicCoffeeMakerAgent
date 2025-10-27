---
command: create-design-tokens
agent: ux_design_expert
action: define_design_system_tokens
tables: [ui_design_tokens]
tools: []
duration: 10m
---

## Purpose

Define colors, spacing, typography design tokens for consistent design system.

## Input Parameters

```yaml
TOKEN_TYPE:
  type: string
  enum: [color, spacing, typography, shadow, border_radius]
  description: Type of design token

VALUES:
  type: object
  description: Token definitions
  properties:
    token_name:
      type: string
      description: Design token name (kebab-case)
    value:
      type: string
      description: Token value (hex, size, etc.)

CATEGORY:
  type: string
  optional: true
  description: Token category for organization
  example: "primary-colors"
```

## Database Operations

### INSERT ui_design_tokens

```sql
INSERT INTO ui_design_tokens (
    token_id, token_name, token_type, value, category,
    created_by, created_at, updated_at
) VALUES (?, ?, ?, ?, ?, 'ux_design_expert', datetime('now'), datetime('now'))
```

## Success Criteria

- Tokens stored in database
- Naming conventions validated
- CSS variables generated
- Values formatted correctly

## Output Format

```json
{
  "success": true,
  "token_type": "color",
  "tokens_created": 12,
  "category": "primary-colors",
  "token_list": [
    {"token_name": "primary-50", "value": "#f0f9ff", "token_id": "TOK-PRIMARY-50"},
    {"token_name": "primary-100", "value": "#e0f2fe", "token_id": "TOK-PRIMARY-100"}
  ],
  "css_variables": "--primary-50: #f0f9ff; --primary-100: #e0f2fe;",
  "message": "Design tokens created successfully"
}
```

## Token Types

| Type | Example Value | Format |
|------|---------------|--------|
| color | #FF6B6B | Hex color |
| spacing | 1rem | CSS size |
| typography | 16px Roboto | Font spec |
| shadow | 0 2px 8px rgba(0,0,0,0.1) | Box shadow |
| border_radius | 8px | Pixel value |

## Naming Convention

- All lowercase with hyphens: `primary-color`, `spacing-md`
- Pattern: `{category}-{property}-{variant}`
- Example: `color-primary-50`, `spacing-padding-xl`

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid type | TOKEN_TYPE not in enum | List valid types |
| Duplicate token | Token already exists | Suggest update instead |
| Invalid format | Value format incorrect | Show valid format examples |

## Examples

### Example 1: Create Color Tokens

```bash
/agents:ux_design_expert:create-design-tokens \
  TOKEN_TYPE="color" \
  CATEGORY="primary-colors" \
  VALUES='{
    "primary-50": "#f0f9ff",
    "primary-100": "#e0f2fe",
    "primary-500": "#0ea5e9",
    "primary-900": "#0c2d57"
  }'
```

### Example 2: Create Spacing Tokens

```bash
/agents:ux_design_expert:create-design-tokens \
  TOKEN_TYPE="spacing" \
  CATEGORY="spacing" \
  VALUES='{
    "spacing-xs": "0.25rem",
    "spacing-sm": "0.5rem",
    "spacing-md": "1rem",
    "spacing-lg": "2rem",
    "spacing-xl": "3rem"
  }'
```

### Example 3: Create Typography Tokens

```bash
/agents:ux_design_expert:create-design-tokens \
  TOKEN_TYPE="typography" \
  CATEGORY="fonts" \
  VALUES='{
    "heading-1": "32px Roboto Bold",
    "heading-2": "24px Roboto Bold",
    "body": "16px Roboto Regular"
  }'
```

## Implementation Notes

- Token IDs use format: `TOK-{TYPE}-{UPPERCASE-NAME}` (e.g., `TOK-COLOR-PRIMARY-50`)
- Naming must be kebab-case (lowercase with hyphens)
- Values formatted by token type:
  - color: Hex (#RRGGBB) or RGB
  - spacing: CSS units (rem, px, em)
  - typography: Font size and family
  - shadow: CSS box-shadow value
  - border_radius: Pixel values
- Generate CSS variables for Tailwind integration
- Support token versioning for future updates
