# tokens

## Purpose
Generate design tokens and Tailwind configuration: define color palette, typography scale, spacing system, create reusable design variables.

## Parameters
```yaml
output_format: str = "tailwind"  # "tailwind" | "css-vars" | "scss"
color_scheme: str = "modern"  # "modern" | "minimal" | "vibrant" | "custom"
custom_colors: dict = None  # {primary: "#...", secondary: "#..."}
typography_scale: str = "default"  # "default" | "compact" | "relaxed"
generate_dark_mode: bool = true  # Include dark mode tokens
```

## Workflow
1. Analyze design requirements
2. Generate color palette (light + dark if enabled)
3. Define typography scale
4. Create spacing system
5. Configure responsive breakpoints
6. Generate Tailwind config or CSS variables
7. Save to appropriate file
8. Return TokensResult

## Token Structure
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    colors: {
      primary: { 50: '#...', ..., 900: '#...' },
      secondary: { ... },
      neutral: { ... }
    },
    spacing: {
      xs: '0.5rem',
      sm: '0.75rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem'
    },
    typography: {
      h1: '2.5rem',
      h2: '2rem',
      body: '1rem',
      small: '0.875rem'
    },
    extend: {
      animation: { ... },
      boxShadow: { ... }
    }
  },
  darkMode: 'class'
}
```

## Database Operations
```sql
-- Track design tokens
INSERT INTO design_token_tracker (
    token_set_id, output_format, color_scheme,
    file_path, created_at, version
) VALUES (?, ?, ?, ?, datetime('now'), '1.0.0')

-- Link to UI spec
UPDATE design_token_tracker
SET related_ui_spec_id = ?
WHERE token_set_id = ?
```

## Color Palette Generation
- **Primary**: Brand identity, CTA buttons
- **Secondary**: Supporting actions
- **Neutral**: Backgrounds, borders, text
- **Semantic**: Success, warning, error, info
- **Each color**: 50-900 scale (10 shades)

## Result Object
```python
@dataclass
class TokensResult:
    token_set_id: str
    output_format: str
    file_path: str
    colors_generated: int
    dark_mode_included: bool
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| InvalidColorFormat | Malformed hex code | Validate color inputs |
| FileWriteError | Can't save config | Check permissions |
| ConflictingTokens | Duplicate token names | Review token naming |
| InvalidScale | Unknown scale value | Use predefined scales |

## Example
```python
result = tokens(
    output_format="tailwind",
    color_scheme="modern",
    custom_colors={"primary": "#3B82F6", "secondary": "#8B5CF6"},
    generate_dark_mode=True
)
# TokensResult(
#   token_set_id="tokens-001",
#   output_format="tailwind",
#   file_path="tailwind.config.js",
#   colors_generated=50,
#   dark_mode_included=True,
#   status="success"
# )
```

## Related Commands
- spec() - Creates UI specs requiring tokens
- review() - Validates token usage

---
Estimated: 60 lines | Context: ~4% | Examples: tokens_examples.md
