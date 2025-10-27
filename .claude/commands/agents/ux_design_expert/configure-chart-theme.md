---
command: configure-chart-theme
agent: ux_design_expert
action: configure_highcharts_theme
tables: [ui_design_tokens]
tools: [file_system]
duration: 15m
---

## Purpose

Configure Highcharts theme and styling with design system colors.

## Input Parameters

```yaml
THEME_NAME:
  type: string
  description: Theme identifier
  example: "coffee_maker_light"

COLORS:
  type: array
  description: Array of hex colors for chart palette
  items: string (hex color)

FONT_FAMILY:
  type: string
  optional: true
  description: Primary font family
  default: "Roboto, sans-serif"

BACKGROUND_COLOR:
  type: string
  optional: true
  description: Chart background color (hex)

ACCENT_COLOR:
  type: string
  optional: true
  description: Accent color for highlights
```

## Database Operations

### INSERT ui_design_tokens

```sql
INSERT INTO ui_design_tokens (
    token_id, token_name, token_type, value, category,
    created_by, created_at, updated_at
) VALUES (?, ?, 'chart_theme', ?, 'chart_theme', 'ux_design_expert', datetime('now'), datetime('now'))
```

## Success Criteria

- Highcharts config JSON generated
- Colors match design tokens
- Accessibility contrast validated
- Theme file created
- Syntax validated

## Output Format

```json
{
  "success": true,
  "theme_name": "coffee_maker_light",
  "config_path": "src/styles/highcharts-theme.js",
  "colors": ["#0ea5e9", "#f59e0b", "#10b981", "#ef4444"],
  "font_family": "Roboto, sans-serif",
  "accessibility_check": true,
  "contrast_score": 4.8,
  "message": "Highcharts theme configured successfully"
}
```

## Generated Config

```javascript
Highcharts.theme = {
  colors: ['#0ea5e9', '#f59e0b', '#10b981', '#ef4444'],
  chart: {
    backgroundColor: '#ffffff',
    borderColor: '#e5e7eb',
    style: { fontFamily: 'Roboto, sans-serif' }
  },
  title: { style: { fontSize: '24px', fontWeight: 'bold' } },
  legend: { itemStyle: { color: '#374151', fontSize: '14px' } }
};
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid color | Hex format incorrect | Show valid hex format |
| Low contrast | Colors fail accessibility check | Suggest darker/lighter variants |
| File write error | Permission denied | Check OUTPUT_PATH |

## Examples

### Example 1: Light Theme

```bash
/agents:ux_design_expert:configure-chart-theme \
  THEME_NAME="coffee_maker_light" \
  COLORS='["#0ea5e9", "#f59e0b", "#10b981", "#ef4444"]' \
  FONT_FAMILY="Roboto, sans-serif" \
  BACKGROUND_COLOR="#ffffff" \
  ACCENT_COLOR="#0ea5e9"
```

### Example 2: Dark Theme

```bash
/agents:ux_design_expert:configure-chart-theme \
  THEME_NAME="coffee_maker_dark" \
  COLORS='["#06b6d4", "#fbbf24", "#34d399", "#f87171"]' \
  BACKGROUND_COLOR="#1f2937" \
  ACCENT_COLOR="#06b6d4"
```

## Implementation Notes

- Generate Highcharts theme object configuration
- Validate color hex format (#RRGGBB)
- Check accessibility contrast (WCAG AA: 4.5:1 minimum)
- Store theme configuration in database
- Create theme file (JavaScript module)
- Support light and dark variants
- Include typography and spacing adjustments
- Export as Highcharts-compatible module
