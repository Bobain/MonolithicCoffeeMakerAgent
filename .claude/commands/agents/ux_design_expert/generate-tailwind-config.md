---
command: generate-tailwind-config
agent: ux_design_expert
action: generate_tailwind_configuration
tables: [ui_design_tokens]
tools: [file_system]
duration: 15m
---

## Purpose

Generate Tailwind CSS configuration files from design tokens.

## Input Parameters

```yaml
PROJECT_NAME:
  type: string
  description: Project identifier for config
  example: "coffee_maker"

THEME_TYPE:
  type: string
  enum: [light, dark, custom]
  description: Theme variant to generate

OUTPUT_PATH:
  type: string
  optional: true
  description: Path to write config (default: tailwind.config.js)

INCLUDE_PLUGINS:
  type: boolean
  optional: true
  default: true
  description: Include custom Tailwind plugins
```

## Database Operations

### SELECT ui_design_tokens

```sql
SELECT token_name, value, category FROM ui_design_tokens
WHERE category IN ('color', 'spacing', 'typography', 'shadow')
ORDER BY category, token_name
```

## Success Criteria

- tailwind.config.js generated
- Design tokens integrated
- Custom utilities defined
- File written successfully
- Syntax validated

## Output Format

```json
{
  "success": true,
  "config_path": "tailwind.config.js",
  "theme_type": "light",
  "colors_defined": 24,
  "spacing_scales": 3,
  "custom_utilities": 8,
  "file_size_bytes": 2450,
  "message": "Tailwind configuration generated successfully"
}
```

## Generated Config Structure

```javascript
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './templates/**/*.html'
  ],
  theme: {
    extend: {
      colors: {...},
      spacing: {...},
      fontSize: {...},
      shadows: {...}
    }
  },
  plugins: [...]
}
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| No tokens found | Design tokens table empty | Create design tokens first |
| File write error | Permission denied | Check OUTPUT_PATH |
| Invalid syntax | Generated config has errors | Log details, validate manually |

## Examples

### Example 1: Generate Light Theme

```bash
/agents:ux_design_expert:generate-tailwind-config \
  PROJECT_NAME="coffee_maker" \
  THEME_TYPE="light" \
  OUTPUT_PATH="tailwind.config.js"
```

### Example 2: Generate Dark Theme

```bash
/agents:ux_design_expert:generate-tailwind-config \
  PROJECT_NAME="coffee_maker" \
  THEME_TYPE="dark"
```

## Implementation Notes

- Read design tokens from ui_design_tokens table
- Generate tailwind.config.js with theme colors, spacing, typography
- Create CSS variables for design tokens
- Include custom utilities for project-specific styles
- Support light/dark theme switching
- Validate generated JavaScript syntax
- Create backup before overwriting existing config
