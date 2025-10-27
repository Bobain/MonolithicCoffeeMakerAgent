---
command: generate-ui-spec
agent: ux_design_expert
action: create_ui_specification
tables: [ui_design_specs]
tools: [llm]
duration: 30m
---

## Purpose

Create detailed UI specifications for components or pages with design guidelines and requirements.

## Input Parameters

```yaml
COMPONENT_NAME:
  type: string
  description: Name of UI component or page
  example: "Dashboard Layout"

REQUIREMENTS:
  type: string
  description: Design requirements and constraints

COMPONENT_TYPE:
  type: string
  enum: [page, component, layout, modal, form]
  optional: true
  description: Type of component

FIGMA_LINK:
  type: string
  optional: true
  description: Figma reference link

ACCESSIBILITY_LEVEL:
  type: string
  optional: true
  enum: [A, AA, AAA]
  default: AA
  description: WCAG compliance level
```

## Database Operations

### INSERT ui_design_specs

```sql
INSERT INTO ui_design_specs (
    spec_id, title, component_type, version, content, figma_link,
    created_by, created_at, updated_at, status
) VALUES (?, ?, ?, '1.0.0', ?, ?, 'ux_design_expert', datetime('now'), datetime('now'), 'draft')
```

## Success Criteria

- Spec ID generated (UI-SPEC-XXX)
- Full design spec created in markdown
- Accessibility requirements included
- WCAG level specified
- Database record created

## Output Format

```json
{
  "success": true,
  "spec_id": "UI-SPEC-042",
  "title": "Dashboard Layout",
  "version": "1.0.0",
  "component_type": "page",
  "accessibility_level": "AA",
  "status": "draft",
  "created_at": "2025-10-27T10:30:00Z",
  "figma_link": "https://figma.com/...",
  "sections": ["Overview", "Requirements", "Layout", "Components", "Accessibility", "Examples"],
  "message": "UI specification created successfully"
}
```

## Specification Sections

1. **Overview** - Component purpose and use cases
2. **Requirements** - Design requirements and constraints
3. **Layout** - Grid, spacing, responsive design
4. **Components** - Sub-components and composition
5. **Styling** - Colors, typography, spacing
6. **Accessibility** - WCAG compliance notes
7. **Examples** - Usage examples and variations
8. **Implementation Notes** - Developer guidance

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid type | COMPONENT_TYPE not in enum | Use default 'component' |
| LLM error | API call failed | Retry up to 3 times |
| Figma link invalid | Link doesn't work | Warn but continue |

## Examples

### Example 1: Page Specification

```bash
/agents:ux_design_expert:generate-ui-spec \
  COMPONENT_NAME="Dashboard Layout" \
  REQUIREMENTS="3-column responsive layout with sidebar navigation" \
  COMPONENT_TYPE="page" \
  ACCESSIBILITY_LEVEL="AA"
```

### Example 2: Component with Figma

```bash
/agents:ux_design_expert:generate-ui-spec \
  COMPONENT_NAME="User Card" \
  REQUIREMENTS="Reusable component showing user info with avatar and actions" \
  COMPONENT_TYPE="component" \
  FIGMA_LINK="https://figma.com/file/.../User-Card"
```

## Implementation Notes

- Spec IDs use format: `UI-SPEC-{sequential-number}`
- Generate comprehensive markdown specification
- Include WCAG accessibility requirements
- Provide Figma design reference
- Create component variations documentation
- Version specs semantically (1.0.0, 1.1.0, etc.)
- Store full spec content in database
