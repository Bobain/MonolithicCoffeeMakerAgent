---
command: ux-design-workflow
workflow: design
agent: ux_design_expert
purpose: Complete UX/UI design workflow
tables: [ui_spec, component_library, design_tokens, accessibility_check]
tools: [file_system, tailwind_config]
duration: 10-45m
---

## Purpose

Execute complete UX/UI design workflow: analyze feature → generate UI spec → create design tokens → manage component library → validate accessibility. This is the PRIMARY workflow command for the ux_design_expert agent.

## Workflow Overview

```
design(feature) → Analyze → UI Spec → Tokens → Components → Accessibility → DesignResult
```

**Key Features**:
- **4 design phases**: FULL (complete), SPEC_ONLY (fast spec), REVIEW_ONLY (validate), TOKENS_ONLY (theme)
- **Tailwind CSS integration**: Generates Tailwind config
- **Highcharts support**: Data visualization design
- **Accessibility validation**: WCAG 2.1 compliance (AA/AAA)
- **Component library management**: Reusable component specs

## Input Parameters

```yaml
FEATURE:
  type: string
  required: true
  description: Feature name to design UI for
  example: "User Dashboard"

PHASE:
  type: string
  default: "full"
  enum: [full, spec-only, review-only, tokens-only]
  description: |
    - full: Complete design workflow
    - spec-only: UI spec generation only
    - review-only: Validate existing design
    - tokens-only: Design tokens/theme only

WCAG_LEVEL:
  type: string
  default: "AA"
  enum: [A, AA, AAA]
  description: WCAG accessibility level target
```

## Workflow Execution

### FULL Phase (Default)

Complete UX design workflow:

```python
1. Analyze feature requirements
2. Create user flow diagram
3. Generate UI specification
4. Define design tokens (colors, spacing, typography)
5. Create component specifications
6. Generate Tailwind config
7. Validate accessibility (WCAG)
8. Add to component library
9. Return DesignResult
```

### SPEC_ONLY Phase

Fast UI spec generation:

```python
1. Analyze feature
2. Generate UI specification
3. Return basic DesignResult
```

### REVIEW_ONLY Phase

Validate existing design:

```python
1. Load existing UI spec
2. Check accessibility compliance
3. Validate design system adherence
4. Generate review report
5. Return validation DesignResult
```

### TOKENS_ONLY Phase

Design tokens and theme:

```python
1. Define color palette
2. Create spacing scale
3. Define typography
4. Generate Tailwind config
5. Return tokens DesignResult
```

## Result Object

```python
@dataclass
class DesignResult:
    feature: str
    status: str  # success | partial | failed
    spec_created: bool
    components_created: bool
    duration_seconds: float
    metadata: Dict[str, Any]
```

## Database Operations

### Insert: UI Spec

```sql
INSERT INTO ui_spec (
    spec_id, feature_name, components, layout,
    design_tokens, accessibility_level, created_at, status
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 'active')
```

### Insert: Component Library

```sql
INSERT INTO component_library (
    component_id, name, category, props,
    tailwind_classes, example, created_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

### Insert: Design Tokens

```sql
INSERT INTO design_tokens (
    token_id, category, name, value,
    tailwind_class, created_at
) VALUES (?, ?, ?, ?, ?, datetime('now'))
```

### Insert: Accessibility Check

```sql
INSERT INTO accessibility_check (
    check_id, spec_id, wcag_level, status,
    issues_found, recommendations, created_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

## Examples

### Example 1: Full Design Workflow

```python
result = workflow.design(
    feature="User Dashboard",
    phase="full",
    wcag_level="AA"
)
```

**Result**:
```python
DesignResult(
    feature="User Dashboard",
    status="success",
    spec_created=True,
    components_created=True,
    duration_seconds=1200.0,  # 20 minutes
    metadata={
        "spec_path": "docs/design/user-dashboard.md",
        "components": ["DashboardCard", "StatsWidget", "ChartContainer"],
        "tokens": {
            "colors": 12,
            "spacing": 8,
            "typography": 6
        },
        "accessibility": {
            "level": "AA",
            "compliant": True,
            "issues": 0
        },
        "tailwind_config": "tailwind.config.dashboard.js"
    }
)
```

### Example 2: Spec Only

```python
result = workflow.design(
    feature="Login Form",
    phase="spec-only"
)
```

**Result**:
```python
DesignResult(
    feature="Login Form",
    status="success",
    spec_created=True,
    components_created=False,
    duration_seconds=300.0,  # 5 minutes
    metadata={
        "spec_path": "docs/design/login-form.md",
        "layout": "centered",
        "components_needed": ["FormInput", "Button", "ErrorMessage"]
    }
)
```

### Example 3: Review Existing Design

```python
result = workflow.design(
    feature="User Profile",
    phase="review-only",
    wcag_level="AAA"
)
```

**Result**:
```python
DesignResult(
    feature="User Profile",
    status="partial",
    spec_created=False,
    components_created=False,
    duration_seconds=180.0,  # 3 minutes
    metadata={
        "accessibility": {
            "level": "AAA",
            "compliant": False,
            "issues": 3,
            "details": [
                "Contrast ratio 3.8:1 (needs 7:1 for AAA)",
                "Missing alt text on avatar image",
                "Focus indicators insufficient"
            ]
        },
        "recommendations": [
            "Increase text color contrast",
            "Add descriptive alt text",
            "Enhance focus indicators (outline: 3px)"
        ]
    }
)
```

### Example 4: Tokens Only

```python
result = workflow.design(
    feature="Dark Mode Theme",
    phase="tokens-only"
)
```

**Result**:
```python
DesignResult(
    feature="Dark Mode Theme",
    status="success",
    spec_created=False,
    components_created=False,
    duration_seconds=240.0,  # 4 minutes
    metadata={
        "tokens": {
            "colors": {
                "background": "#1a1a1a",
                "surface": "#2d2d2d",
                "primary": "#3b82f6",
                "text": "#f5f5f5"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem"
            },
            "typography": {
                "base": "16px",
                "scale": 1.25,
                "fonts": {
                    "sans": "Inter, system-ui",
                    "mono": "JetBrains Mono, monospace"
                }
            }
        },
        "tailwind_config": "tailwind.config.dark.js"
    }
)
```

## UI Specification Format

### Complete UI Spec

```markdown
# UI Spec: User Dashboard

**Feature**: User Dashboard
**Phase**: Full Design
**WCAG Level**: AA
**Status**: Active

## User Flow
1. User lands on dashboard
2. Sees overview statistics
3. Can navigate to detailed views
4. Interacts with charts and widgets

## Layout

### Desktop (≥1024px)
- 3-column grid
- Sidebar (280px)
- Main content (flex-1)
- Right panel (320px)

### Tablet (768px-1023px)
- 2-column grid
- Collapsible sidebar
- Main content

### Mobile (<768px)
- Single column
- Bottom navigation
- Stacked widgets

## Components

### DashboardCard
**Purpose**: Container for dashboard widgets
**Props**:
- title: string
- icon?: IconComponent
- footer?: ReactNode

**Tailwind Classes**:
```
bg-white dark:bg-gray-800
rounded-lg shadow-md
p-6 space-y-4
```

### StatsWidget
**Purpose**: Display key metrics
**Props**:
- value: number
- label: string
- change?: number (percentage)
- trend?: 'up' | 'down'

### ChartContainer
**Purpose**: Wrapper for Highcharts visualizations
**Props**:
- type: 'line' | 'bar' | 'pie'
- data: ChartData
- options?: HighchartsOptions

## Design Tokens

### Colors
```javascript
colors: {
  primary: {
    50: '#eff6ff',
    500: '#3b82f6',
    900: '#1e3a8a'
  },
  surface: {
    light: '#ffffff',
    dark: '#1f2937'
  }
}
```

### Spacing
```javascript
spacing: {
  'card-padding': '1.5rem',
  'widget-gap': '1rem',
  'section-margin': '2rem'
}
```

### Typography
```javascript
fontSize: {
  'stat-value': ['2.5rem', { lineHeight: '1.2' }],
  'stat-label': ['0.875rem', { lineHeight: '1.4' }]
}
```

## Accessibility

### WCAG AA Compliance
- ✅ Contrast ratio ≥ 4.5:1 for text
- ✅ Focus indicators visible
- ✅ Keyboard navigation supported
- ✅ ARIA labels on interactive elements
- ✅ Alt text for images

### Screen Reader Support
- Semantic HTML structure
- Descriptive button labels
- Live regions for dynamic updates

## Highcharts Configuration

```javascript
{
  chart: {
    type: 'line',
    backgroundColor: 'transparent'
  },
  title: {
    text: 'Usage Over Time',
    style: { color: 'var(--text-primary)' }
  },
  accessibility: {
    description: 'Line chart showing user activity trends'
  }
}
```
```

## Tailwind Config Generation

```javascript
// tailwind.config.dashboard.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          // ... full scale
        }
      },
      spacing: {
        'card': '1.5rem',
        'widget': '1rem'
      },
      borderRadius: {
        'card': '0.5rem'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
}
```

## Accessibility Validation

### WCAG Checks

```python
def validate_wcag(spec, level="AA"):
    checks = []

    # Contrast ratio
    for color_pair in spec.color_combinations:
        ratio = calculate_contrast(color_pair)
        required = 4.5 if level == "AA" else 7.0
        if ratio < required:
            checks.append(f"Contrast too low: {ratio:.2f}:1")

    # Alt text
    if not all(img.has_alt for img in spec.images):
        checks.append("Missing alt text on images")

    # Focus indicators
    if not spec.focus_indicators.visible:
        checks.append("Focus indicators not visible")

    return checks
```

## Performance Expectations

| Phase | Duration | Spec Created | Components | Tokens |
|-------|----------|--------------|------------|--------|
| FULL | 15-45m | Yes | Yes | Yes |
| SPEC_ONLY | 5-15m | Yes | No | No |
| REVIEW_ONLY | 3-10m | No | No | No |
| TOKENS_ONLY | 3-8m | No | No | Yes |

## Best Practices

1. **Use FULL phase** for new features
2. **Use SPEC_ONLY** for rapid prototyping
3. **Use REVIEW_ONLY** before launch
4. **Use TOKENS_ONLY** for theming
5. **Target WCAG AA** as minimum (AAA for critical features)
6. **Mobile-first design** - start with mobile layout
7. **Component reuse** - check library before creating new
8. **Dark mode support** - include dark mode tokens

## Related Commands

- `architect.spec()` - Technical specs reference UI specs
- `developer.work()` - Implements UI specs
- `assistant.assist()` - Creates demos of designed UIs

---

**Workflow Reduction**: This single `design()` command replaces:
1. `generate_ui_spec()`
2. `create_design_tokens()`
3. `manage_component_library()`
4. `validate_accessibility()`
5. `generate_tailwind_config()`

**Context Savings**: ~150 lines vs ~1,000 lines (5 commands)
