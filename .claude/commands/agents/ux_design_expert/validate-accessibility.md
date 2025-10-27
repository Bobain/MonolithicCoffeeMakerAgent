---
command: validate-accessibility
agent: ux_design_expert
action: check_wcag_compliance
tables: [ui_design_specs, ui_component_library]
tools: [accessibility_checker]
duration: 15m
---

## Purpose

Ensure design specifications meet WCAG accessibility compliance requirements.

## Input Parameters

```yaml
SPEC_ID:
  type: string
  description: Design spec ID or component ID
  example: "UI-SPEC-042"

WCAG_LEVEL:
  type: string
  enum: [A, AA, AAA]
  description: WCAG compliance level to check

COMPONENT_ID:
  type: string
  optional: true
  description: Component ID (alternative to SPEC_ID)
```

## Database Operations

### SELECT ui_design_specs or ui_component_library

Query the specification/component details for validation.

## Success Criteria

- WCAG guidelines checked against spec
- Issues identified and logged
- Recommendations provided
- Compliance score calculated

## Output Format

```json
{
  "success": true,
  "spec_id": "UI-SPEC-042",
  "wcag_level": "AA",
  "compliance_score": 92,
  "issues_found": 3,
  "critical_issues": 0,
  "warnings": 3,
  "issues": [
    {
      "level": "warning",
      "guideline": "1.4.3 Contrast",
      "description": "Color contrast ratio 4.5:1, should be 7:1 for AAA",
      "suggestion": "Use darker shade for text color"
    }
  ],
  "message": "Accessibility validation completed"
}
```

## WCAG Guidelines Checked

| Category | Guideline | Check |
|----------|-----------|-------|
| Perceivable | 1.4.3 Contrast (Minimum) | Color contrast ratios |
| Perceivable | 1.4.11 Non-text Contrast | UI component contrast |
| Operable | 2.1.1 Keyboard | Keyboard navigation support |
| Operable | 2.4.7 Focus Visible | Focus indicator visibility |
| Understandable | 3.3.2 Labels or Instructions | Form labels present |
| Understandable | 3.3.4 Error Prevention | Error messages helpful |
| Robust | 4.1.2 Name, Role, Value | ARIA labels correct |

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Spec not found | Invalid SPEC_ID | List available specs |
| Invalid WCAG level | Level not in enum | Use default 'AA' |
| Validation failed | Checker error | Return partial results |

## Examples

### Example 1: Validate Spec for AA

```bash
/agents:ux_design_expert:validate-accessibility \
  SPEC_ID="UI-SPEC-042" \
  WCAG_LEVEL="AA"
```

### Example 2: Validate Component

```bash
/agents:ux_design_expert:validate-accessibility \
  COMPONENT_ID="COMP-BUTTON-PRIMARY" \
  WCAG_LEVEL="AAA"
```

## Implementation Notes

- Check color contrast ratios (4.5:1 for AA, 7:1 for AAA)
- Verify ARIA labels and roles
- Validate keyboard navigation support
- Check focus indicator visibility
- Verify form labels and error messages
- Generate compliance report with recommendations
- Suggest fixes for each issue
