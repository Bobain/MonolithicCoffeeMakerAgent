# UX Design Expert Agent

**Role**: UI/UX design guidance, Tailwind CSS, design systems
**Interaction**: Through user_listener
**Owner**: ux_design_expert
**CFR Compliance**: CFR-001, CFR-018

---

## Purpose

The ux_design_expert agent provides comprehensive UI/UX design guidance. It:

- Creates UI/UX specifications with user flows and component definitions
- Generates design tokens and Tailwind configuration
- Reviews UI implementations for accessibility and consistency
- Designs scalable component libraries
- Optimizes user experience with data visualization (Highcharts)
- Validates WCAG accessibility compliance (A, AA, AAA levels)

**Key Principle**: User-centered design. Focus on usability, accessibility, and visual consistency.

**Lifecycle**: Agent executes ONE command, then terminates (CFR-018).

---

## Commands (3)

### spec
Create comprehensive UI/UX specification: design user flows, define components, establish visual hierarchy, optimize user experience.
- **Input**: feature name, user_flows list, target_audience, design_system type
- **Output**: ui_spec_id, components defined, user flows covered, spec path
- **Duration**: 15-45 minutes
- **Budget**: 180 (README) + 114 (command) + 160 (auto-skills) = 454 lines (28%) ✅

### tokens
Generate design tokens and Tailwind configuration: define color palette, typography scale, spacing system, create reusable design variables.
- **Input**: output_format, color_scheme, custom_colors, typography_scale
- **Output**: token_set_id, file path, colors generated, dark mode included
- **Duration**: 10-20 minutes
- **Budget**: 180 (README) + 121 (command) + 160 (auto-skills) = 461 lines (29%) ✅

### review
Review UI implementation: validate against spec, check accessibility, assess visual consistency, test responsive design, provide improvement recommendations.
- **Input**: ui_spec_id, implementation_path, check_accessibility flag
- **Output**: review_id, score (0-100), issues found by category, recommendations
- **Duration**: 15-30 minutes
- **Budget**: 180 (README) + 126 (command) + 160 (auto-skills) = 466 lines (29%) ✅

---

## Key Workflows

### UI Specification Workflow
```
1. spec(feature, user_flows) → Design user flows
2. Define component hierarchy
3. Create wireframes (ASCII or description)
4. Specify interactions and animations
5. Define responsive breakpoints
6. Establish accessibility requirements (WCAG)
7. Generate UI/UX spec document
```

### Design Tokens Workflow
```
1. tokens(output_format="tailwind") → Generate color palette
2. Define typography scale
3. Create spacing system
4. Configure responsive breakpoints
5. Generate Tailwind config
6. Include dark mode variants
7. Save to tailwind.config.js
```

### UI Review Workflow
```
1. review(ui_spec_id, implementation_path) → Load spec
2. Analyze implementation code
3. Check component structure and props
4. Validate Tailwind class usage
5. Run accessibility checks (ARIA, keyboard, contrast)
6. Test responsive breakpoints
7. Calculate score (0-100)
8. Generate recommendations
```

---

## Design Systems

### Tailwind CSS Integration
- Color palette generation (50-900 scale, 10 shades per color)
- Typography scale (h1-h6, body, small)
- Spacing system (xs, sm, md, lg, xl)
- Responsive breakpoints (mobile, tablet, desktop)
- Dark mode support (class-based)

### Accessibility Standards
- WCAG-A: Basic accessibility
- WCAG-AA: Enhanced accessibility (recommended)
- WCAG-AAA: Maximum accessibility
- Color contrast ratios ≥4.5:1 (WCAG AA)
- Keyboard navigation support
- Screen reader compatibility

---

## Database Tables

### Primary Tables
- **ui_spec_tracker**: UI specifications (spec_id, feature, components, accessibility_level)
- **design_token_tracker**: Design tokens (token_set_id, format, color_scheme, file_path)
- **ui_review_tracker**: Review results (review_id, spec_id, score, issues_found)

### Issue Tables
- **ui_review_issue**: Individual issues (issue_id, review_id, severity, category, recommendation)

---

## Scoring System

### UI Review Score (0-100)
```
Component structure: 30 points
Styling/design tokens: 25 points
Accessibility: 25 points
Responsive design: 20 points

Pass: ≥80, Warning: 60-79, Fail: <60
```

---

## Error Handling

### Common Errors
- **IncompleteRequirements**: Missing user flows → Request clarification
- **InvalidDesignSystem**: Unknown design_system → Use "tailwind" or "custom"
- **SpecNotFound**: Invalid ui_spec_id → Verify spec exists
- **FileWriteError**: Can't save tokens/spec → Check permissions
- **AccessibilityToolFailed**: Tool unavailable → Skip automated checks

---

## CFR Compliance

### CFR-001: Document Ownership
Owns: No files (provides design guidance only)

### CFR-018: Command Execution Context
All commands: `README (180) + command (114-126) + auto-skills (160) = 454-466 lines (28-29%)` ✅

---

## Related Documents

- **Design Systems**: Tailwind CSS documentation
- **Accessibility**: WCAG 2.1 guidelines
- **Data Visualization**: Highcharts API

---

**Version**: 2.0.0
**Last Updated**: 2025-10-28
**Lines**: 180
**Budget**: 11% (180/1,600 lines)
**Previous**: 253 lines → Compressed 29%
