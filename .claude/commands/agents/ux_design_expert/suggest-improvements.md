---
command: suggest-improvements
agent: ux_design_expert
action: identify_ux_enhancements
tables: [ui_design_specs, ui_component_library]
tools: [llm]
duration: 15m
---

## Purpose

Identify UX enhancement opportunities and improvements with prioritization by impact.

## Input Parameters

```yaml
SCOPE:
  type: string
  enum: [component, page, entire_app, specific]
  description: Scope of improvement suggestions

SPEC_ID:
  type: string
  optional: true
  description: Specific spec to analyze
  example: "UI-SPEC-042"

FOCUS_AREAS:
  type: array
  optional: true
  description: Specific areas to focus on
  items:
    type: string
    enum: [accessibility, performance, usability, consistency, aesthetics]
```

## Database Operations

### SELECT ui_design_specs, ui_component_library

Query design specs and components for analysis.

## Success Criteria

- Enhancement opportunities identified
- Prioritized by impact and effort
- Actionable recommendations provided
- Implementation notes included

## Output Format

```json
{
  "success": true,
  "scope": "page",
  "spec_id": "UI-SPEC-042",
  "total_suggestions": 8,
  "suggestions": [
    {
      "id": 1,
      "title": "Add loading skeleton for async data",
      "area": "usability",
      "impact": "high",
      "effort": "medium",
      "priority_score": 9.2,
      "description": "Show skeleton placeholders while loading data",
      "benefit": "Improves perceived performance and user experience",
      "implementation_notes": "Use react-loading-skeleton or custom CSS animations"
    },
    {
      "id": 2,
      "title": "Improve keyboard navigation",
      "area": "accessibility",
      "impact": "high",
      "effort": "medium",
      "priority_score": 8.8,
      "description": "Add focus visible indicators and keyboard shortcuts"
    }
  ],
  "message": "Improvement suggestions generated"
}
```

## Improvement Areas

| Area | Focus | Examples |
|------|-------|----------|
| accessibility | WCAG compliance | Keyboard nav, color contrast, labels |
| performance | Speed and efficiency | Lazy loading, image optimization, caching |
| usability | User experience | Feedback, error handling, navigation clarity |
| consistency | Design system | Component reuse, spacing, typography |
| aesthetics | Visual appeal | Colors, typography, imagery, animation |

## Priority Scoring

```
priority_score = (impact * 0.5) + (ease_of_implementation * 0.3) + (user_request * 0.2)
```

Where:
- impact: 1-10 (high impact = higher score)
- effort: 1-10 (low effort = higher score)
- user_request: 1-10 (frequently requested = higher score)

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Invalid scope | SCOPE not in enum | List valid scopes |
| Spec not found | Invalid SPEC_ID | List available specs |
| LLM error | API call failed | Retry up to 3 times |

## Examples

### Example 1: Page Improvements

```bash
/agents:ux_design_expert:suggest-improvements \
  SCOPE="page" \
  SPEC_ID="UI-SPEC-042" \
  FOCUS_AREAS='["usability", "accessibility"]'
```

### Example 2: Component Improvements

```bash
/agents:ux_design_expert:suggest-improvements \
  SCOPE="component" \
  SPEC_ID="UI-SPEC-043" \
  FOCUS_AREAS='["consistency", "performance"]'
```

### Example 3: Entire App Review

```bash
/agents:ux_design_expert:suggest-improvements \
  SCOPE="entire_app"
```

## Implementation Notes

- Use LLM to generate creative enhancement suggestions
- Analyze current specs and components
- Consider user experience best practices
- Evaluate accessibility opportunities
- Suggest specific implementation approaches
- Prioritize by impact and feasibility
- Include before/after examples
- Link to relevant design patterns
- Track suggested improvements for future roadmap
