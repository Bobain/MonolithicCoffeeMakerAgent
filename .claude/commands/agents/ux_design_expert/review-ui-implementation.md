---
command: review-ui-implementation
agent: ux_design_expert
action: review_implementation_against_spec
tables: [ui_design_specs]
tools: [file_system, puppeteer_mcp]
duration: 20m
---

## Purpose

Compare UI implementation against design specification with visual inspection.

## Input Parameters

```yaml
SPEC_ID:
  type: string
  description: Design spec ID to review against
  example: "UI-SPEC-042"

IMPLEMENTATION_URL:
  type: string
  optional: true
  description: URL to implemented component
  example: "http://localhost:8501/dashboard"

COMPONENT_PATH:
  type: string
  optional: true
  description: Path to component file for code review

SCREENSHOT_PATH:
  type: string
  optional: true
  description: Screenshot of implementation for visual comparison
```

## Database Operations

### SELECT ui_design_specs

```sql
SELECT content FROM ui_design_specs WHERE spec_id = ?
```

## External Tools

### Puppeteer MCP (if URL provided)

Navigate to component URL and capture visual evidence.

## Success Criteria

- Implementation compared to spec
- Deviations identified with severity
- Visual inspection completed
- Approval status set
- Review report generated

## Output Format

```json
{
  "success": true,
  "spec_id": "UI-SPEC-042",
  "review_date": "2025-10-27T10:30:00Z",
  "conformance_score": 87,
  "deviations": [
    {
      "area": "Color Scheme",
      "severity": "low",
      "expected": "Primary blue #0ea5e9",
      "actual": "Darker blue #0284c7",
      "suggestion": "Adjust color to match spec"
    }
  ],
  "approval_status": "approved_with_notes",
  "notes": "Implementation is 87% conformant. Minor color variations noted.",
  "message": "Review completed successfully"
}
```

## Conformance Levels

| Score | Status | Meaning |
|-------|--------|---------|
| 95-100 | approved | Full conformance |
| 80-94 | approved_with_notes | Minor deviations acceptable |
| 60-79 | changes_requested | Notable deviations need fixing |
| <60 | rejected | Significant deviations from spec |

## Deviation Severity

| Severity | Impact | Examples |
|----------|--------|----------|
| critical | Breaks spec requirements | Wrong layout, missing components |
| high | Significant visual difference | Colors off, spacing incorrect |
| medium | Noticeable but acceptable | Font size slightly different |
| low | Minor details | Icon size, shadow intensity |

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Spec not found | Invalid SPEC_ID | List available specs |
| URL unreachable | Component not running | Check implementation_url |
| Screenshot failed | Puppeteer error | Use component_path instead |

## Examples

### Example 1: Review with URL

```bash
/agents:ux_design_expert:review-ui-implementation \
  SPEC_ID="UI-SPEC-042" \
  IMPLEMENTATION_URL="http://localhost:8501/dashboard"
```

### Example 2: Review Code Implementation

```bash
/agents:ux_design_expert:review-ui-implementation \
  SPEC_ID="UI-SPEC-042" \
  COMPONENT_PATH="src/components/Dashboard.tsx"
```

### Example 3: Review with Screenshot

```bash
/agents:ux_design_expert:review-ui-implementation \
  SPEC_ID="UI-SPEC-042" \
  SCREENSHOT_PATH="evidence/dashboard-implementation.png"
```

## Implementation Notes

- Load spec content from database
- Compare implementation against spec requirements
- Use Puppeteer to inspect live components
- Check colors, typography, spacing, layout
- Validate responsive design
- Generate conformance score (0-100)
- Identify deviations by severity
- Provide actionable improvement suggestions
- Create visual before/after comparison
