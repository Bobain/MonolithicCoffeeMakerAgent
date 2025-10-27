# UX Design Expert Commands

10 commands for UI design specifications, component libraries, design tokens, and design debt tracking.

## Commands

### Interface Design (3 commands)

- **generate-ui-spec** - Create detailed UI specifications
  - Input: COMPONENT_NAME, REQUIREMENTS, COMPONENT_TYPE (optional), FIGMA_LINK (optional), ACCESSIBILITY_LEVEL (A|AA|AAA)
  - Output: spec_id (UI-SPEC-XXX), title, version=1.0.0, status=draft, sections
  - Use case: Create detailed design specifications with accessibility requirements

- **create-component-spec** - Define reusable component structure
  - Input: COMPONENT_NAME, CATEGORY (button|input|card|form|etc), DESCRIPTION, PROPS_SCHEMA, TAILWIND_CLASSES (optional), ACCESSIBILITY_NOTES (optional)
  - Output: component_id, component_name, props_schema, tailwind_classes
  - Use case: Document component structure for developers

- **validate-accessibility** - Ensure WCAG compliance
  - Input: SPEC_ID or COMPONENT_ID, WCAG_LEVEL (A|AA|AAA)
  - Output: compliance_score, issues_found, critical_issues, warnings, issues (array)
  - Use case: Verify WCAG compliance (contrast, labels, keyboard nav, etc.)

### Component Libraries (4 commands)

- **manage-component-library** - CRUD operations on component inventory
  - Input: ACTION (create|read|update|delete|list), COMPONENT_ID (for read/update/delete), DATA (for create/update), FILTERS (for list)
  - Output: component_id, component_name, count (for list), data
  - Use case: Maintain component library (add, view, update, remove, list)

- **generate-tailwind-config** - Create Tailwind CSS configurations
  - Input: PROJECT_NAME, THEME_TYPE (light|dark|custom), OUTPUT_PATH (optional), INCLUDE_PLUGINS (bool)
  - Output: config_path, theme_type, colors_defined, spacing_scales, custom_utilities, file_size
  - Use case: Generate tailwind.config.js from design tokens

- **create-design-tokens** - Define colors, spacing, typography tokens
  - Input: TOKEN_TYPE (color|spacing|typography|shadow|border_radius|chart_theme), VALUES (dict), CATEGORY (optional)
  - Output: token_type, tokens_created, token_list, css_variables
  - Use case: Define design system tokens (colors, sizes, fonts)

- **configure-chart-theme** - Set Highcharts theme and styling
  - Input: THEME_NAME, COLORS (array), FONT_FAMILY (optional), BACKGROUND_COLOR (optional), ACCENT_COLOR (optional)
  - Output: theme_name, config_path, colors, accessibility_check, contrast_score
  - Use case: Create consistent chart styling with design colors

### Design Review (3 commands)

- **review-ui-implementation** - Compare implementation to spec
  - Input: SPEC_ID, IMPLEMENTATION_URL (optional), COMPONENT_PATH (optional), SCREENSHOT_PATH (optional)
  - Output: conformance_score, deviations (array), approval_status, notes
  - Use case: QA check for UI implementation vs design spec

- **suggest-improvements** - Identify UX enhancement opportunities
  - Input: SCOPE (component|page|entire_app|specific), SPEC_ID (optional), FOCUS_AREAS (optional)
  - Output: total_suggestions, suggestions (array with title, impact, effort, priority_score)
  - Use case: Identify UX improvements ranked by impact

- **track-design-debt** - Monitor UI/UX technical debt
  - Input: ACTION (add|update|resolve|list), DESCRIPTION (for add), SEVERITY (critical|high|medium|low), COMPONENT_ID (optional), DEBT_ID (for update/resolve), REMEDIATION_PLAN (for resolve)
  - Output: debt_id (DEBT-DESIGN-XXX), status, created_at, resolved_at
  - Use case: Track design issues and remediation

## Implementation

Located in: `coffee_maker/commands/ux_design_expert_commands.py`

### Usage Example

```python
from coffee_maker.commands.ux_design_expert_commands import UXDesignExpertCommands

designer = UXDesignExpertCommands()

# 1. Generate UI spec
spec = designer.generate_ui_spec(
    component_name="Login Form",
    requirements="Email and password fields with validation",
    component_type="form",
    accessibility_level="AA"
)

# 2. Create component specification
component = designer.create_component_spec(
    component_name="LoginForm",
    category="form",
    description="Reusable login form component",
    props_schema={
        "type": "object",
        "properties": {
            "onSubmit": {"type": "function"},
            "isLoading": {"type": "boolean"}
        }
    },
    tailwind_classes="p-6 bg-white rounded-lg shadow"
)

# 3. Validate accessibility
validation = designer.validate_accessibility(
    spec_id=spec["spec_id"],
    wcag_level="AA"
)

# 4. Create design tokens
tokens = designer.create_design_tokens(
    token_type="color",
    values={
        "primary": "#0ea5e9",
        "secondary": "#f59e0b",
        "success": "#10b981"
    },
    category="brand-colors"
)

# 5. Generate Tailwind config
config = designer.generate_tailwind_config(
    project_name="coffee_maker",
    theme_type="light"
)

# 6. Configure chart theme
chart_theme = designer.configure_chart_theme(
    theme_name="light_theme",
    colors=["#0ea5e9", "#f59e0b", "#10b981"],
    font_family="Roboto"
)

# 7. Review implementation
review = designer.review_ui_implementation(
    spec_id=spec["spec_id"],
    implementation_url="http://localhost:8501/login"
)

# 8. Get improvement suggestions
improvements = designer.suggest_improvements(
    scope="page",
    spec_id=spec["spec_id"],
    focus_areas=["usability", "accessibility"]
)

# 9. Track design debt
debt = designer.track_design_debt(
    action="add",
    description="Form inputs missing focus styles",
    severity="medium",
    component_id=component["component_id"]
)

# Later: resolve the debt
designer.track_design_debt(
    action="resolve",
    debt_id=debt["debt_id"],
    remediation_plan="Added focus:ring focus states to all inputs"
)
```

## Database Tables

- `ui_design_specs` - Design specifications with versions
- `ui_component_library` - Component definitions and metadata
- `ui_design_tokens` - Design system tokens (colors, spacing, fonts)
- `ui_design_debt` - UI/UX technical debt tracking

## Design Token Types

| Type | Examples | Format |
|------|----------|--------|
| color | primary, secondary, success | #RRGGBB or rgb() |
| spacing | xs, sm, md, lg, xl | 0.25rem, 0.5rem, 1rem, etc. |
| typography | heading-1, body, caption | 32px Roboto Bold |
| shadow | sm, md, lg | 0 2px 8px rgba(0,0,0,0.1) |
| border_radius | sm, md, lg | 4px, 8px, 16px |
| chart_theme | light_theme, dark_theme | Highcharts config |

## Testing

Run tests with:
```bash
pytest tests/unit/test_spec114_commands.py::TestUXDesignExpertCommands -v
```

Test coverage includes:
- UI spec generation with WCAG levels
- Component spec creation with props schema
- Accessibility validation (contrast, labels, keyboard nav)
- Component library CRUD operations
- Tailwind config generation from tokens
- Design token creation (colors, spacing, typography)
- Highcharts theme configuration
- UI implementation review with conformance scoring
- Improvement suggestions with prioritization
- Design debt tracking and remediation

## Performance

- Spec generation: <1s (LLM enhanced)
- Component creation: <100ms
- Accessibility validation: <500ms
- Library CRUD: <100ms
- Tailwind config: <500ms
- Token creation: <100ms
- Chart theme config: <100ms
- Implementation review: <2s (visual inspection)
- Improvement suggestions: <2s (LLM)
- Design debt tracking: <100ms

## Accessibility Compliance

WCAG Guidelines checked:
- 1.4.3 Contrast (Minimum) - Color contrast ratios
- 1.4.11 Non-text Contrast - UI component contrast
- 2.1.1 Keyboard - Keyboard navigation support
- 2.4.7 Focus Visible - Focus indicator visibility
- 3.3.2 Labels or Instructions - Form labels present
- 3.3.4 Error Prevention - Error messages helpful
- 4.1.2 Name, Role, Value - ARIA labels correct

## Component Categories

- button - Button variants
- input - Form inputs
- card - Content cards
- list - List components
- modal - Modal dialogs
- form - Form groups
- layout - Layout components
- navigation - Navigation components

## Design Debt Severity Guide

| Severity | Criteria | Action |
|----------|----------|--------|
| critical | Blocks accessibility, major feature broken | Fix immediately |
| high | Significant UX degradation | Fix in next sprint |
| medium | Noticeable quality issue | Schedule for fix |
| low | Minor polish needed | Backlog for later |

## Error Handling

All commands return:
```json
{
  "success": true/false,
  "error": "error message if failed",
  "...": "command-specific results"
}
```

Common errors:
- Invalid enum values (component_type, token_type, severity, scope)
- Missing required parameters
- Spec/component/token not found
- Invalid JSON schema format
- Invalid hex color format
