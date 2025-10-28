# spec

## Purpose
Create comprehensive UI/UX specification: design user flows, define components, establish visual hierarchy, optimize user experience.

## Parameters
```yaml
feature: str  # Required, feature name
user_flows: List[str]  # Required, key user flows to design
target_audience: str = "general"  # User persona
design_system: str = "tailwind"  # "tailwind" | "custom"
accessibility_level: str = "WCAG-AA"  # "WCAG-A" | "WCAG-AA" | "WCAG-AAA"
```

## Workflow
1. Analyze feature requirements
2. Design user flows and journey maps
3. Define component hierarchy
4. Create wireframes (ASCII or description)
5. Specify interactions and animations
6. Define responsive breakpoints
7. Establish accessibility requirements
8. Generate UI/UX specification document
9. Return SpecResult

## UI Specification Structure
```markdown
# UI/UX Spec: {feature}

## User Flows
1. Flow 1: [Steps...]
2. Flow 2: [Steps...]

## Components
### Component 1
- **Purpose**: ...
- **Props**: {prop: type}
- **States**: [default, hover, active, disabled]
- **Tailwind Classes**: ...

## Visual Hierarchy
- Primary: CTA buttons, main content
- Secondary: Supporting actions
- Tertiary: Metadata, timestamps

## Responsive Design
- Mobile (<640px): ...
- Tablet (640-1024px): ...
- Desktop (>1024px): ...

## Accessibility
- ARIA labels: ...
- Keyboard navigation: ...
- Screen reader support: ...
```

## Database Operations
```sql
-- Create UI spec record
INSERT INTO ui_spec_tracker (
    ui_spec_id, feature_name, design_system,
    accessibility_level, created_at, status
) VALUES (?, ?, ?, ?, datetime('now'), 'draft')

-- Link to technical spec
UPDATE ui_spec_tracker
SET related_spec_id = ?, related_priority_id = ?
WHERE ui_spec_id = ?
```

## Result Object
```python
@dataclass
class SpecResult:
    ui_spec_id: str
    feature: str
    components_defined: int
    user_flows_covered: int
    spec_path: str
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| IncompleteRequirements | Missing user flows | Request clarification |
| InvalidDesignSystem | Unknown design_system | Use "tailwind" or "custom" |
| AccessibilityConflict | Requirements incompatible | Review WCAG guidelines |
| FileWriteError | Can't save spec | Check permissions |

## Example
```python
result = spec(
    feature="User Dashboard",
    user_flows=["View metrics", "Filter data", "Export reports"],
    design_system="tailwind",
    accessibility_level="WCAG-AA"
)
# SpecResult(
#   ui_spec_id="UI-SPEC-005",
#   feature="User Dashboard",
#   components_defined=8,
#   user_flows_covered=3,
#   spec_path="docs/ui/UI-SPEC-005-user-dashboard.md",
#   status="success"
# )
```

## Related Commands
- tokens() - Generate design tokens for components
- review() - Validate implementation against spec

---
Estimated: 60 lines | Context: ~4% | Examples: spec_examples.md
