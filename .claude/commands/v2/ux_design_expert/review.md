# review

## Purpose
Review UI implementation: validate against spec, check accessibility, assess visual consistency, test responsive design, provide improvement recommendations.

## Parameters
```yaml
ui_spec_id: str  # Required, UI spec to validate against
implementation_path: str  # Required, path to UI code
check_accessibility: bool = true  # Run accessibility checks
check_responsive: bool = true  # Validate responsive design
generate_report: bool = true  # Create review report
```

## Workflow
1. Load UI specification
2. Analyze implementation code
3. Check component structure and props
4. Validate Tailwind class usage
5. Run accessibility checks (ARIA, keyboard, contrast)
6. Test responsive breakpoints
7. Assess visual consistency
8. Generate improvement recommendations
9. Create review report
10. Return ReviewResult

## Review Checklist
```yaml
Component Structure:
  - [ ] Props match spec
  - [ ] States implemented (default, hover, active, disabled)
  - [ ] Composition follows hierarchy

Styling:
  - [ ] Tailwind classes match design tokens
  - [ ] Responsive breakpoints correct
  - [ ] Dark mode support (if required)

Accessibility:
  - [ ] ARIA labels present
  - [ ] Keyboard navigation works
  - [ ] Color contrast ratio ≥ 4.5:1 (WCAG AA)
  - [ ] Screen reader compatible

User Experience:
  - [ ] Loading states defined
  - [ ] Error states handled
  - [ ] Success feedback provided
```

## Database Operations
```sql
-- Create review record
INSERT INTO ui_review_tracker (
    review_id, ui_spec_id, implementation_path,
    score, issues_found, created_at
) VALUES (?, ?, ?, ?, ?, datetime('now'))

-- Track issues
INSERT INTO ui_review_issue (
    issue_id, review_id, severity, category,
    description, line_number, recommendation
) VALUES (?, ?, ?, ?, ?, ?, ?)
```

## Result Object
```python
@dataclass
class ReviewResult:
    review_id: str
    ui_spec_id: str
    score: int  # 0-100
    issues_found: int
    issues_by_category: dict  # {accessibility: 2, styling: 1}
    recommendations: List[str]
    report_path: str
    status: str  # "pass" | "warning" | "fail"
```

## Scoring System
```
100 points total:
- Component structure: 30 points
- Styling/design tokens: 25 points
- Accessibility: 25 points
- Responsive design: 20 points

Pass: ≥80, Warning: 60-79, Fail: <60
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| SpecNotFound | Invalid ui_spec_id | Verify spec exists |
| ImplementationNotFound | Invalid path | Check path exists |
| ParseError | Can't analyze code | Review code syntax |
| AccessibilityToolFailed | Tool unavailable | Skip automated checks |

## Example
```python
result = review(
    ui_spec_id="UI-SPEC-005",
    implementation_path="src/components/Dashboard.tsx",
    check_accessibility=True
)
# ReviewResult(
#   review_id="review-001",
#   ui_spec_id="UI-SPEC-005",
#   score=92,
#   issues_found=3,
#   issues_by_category={"accessibility": 2, "styling": 1},
#   recommendations=[
#     "Add ARIA label to chart component",
#     "Increase color contrast on secondary buttons"
#   ],
#   report_path="reports/ui-review-001.md",
#   status="pass"
# )
```

## Related Commands
- spec() - Creates UI specs to review against
- tokens() - Defines design tokens to validate

---
Estimated: 65 lines | Context: ~4% | Examples: review_examples.md
