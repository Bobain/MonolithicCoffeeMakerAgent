---
name: design-system
version: 1.0.0
agent: ux-design-expert
scope: agent-specific
description: >
  Design system generation: analyze Tailwind CSS usage, extract patterns,
  generate design tokens, create component library documentation.

triggers:
  - "generate design system"
  - "extract design tokens"
  - "analyze design patterns"

requires:
  - graphviz>=0.20  # Component relationship graphs

inputs:
  scope:
    type: string
    required: false
    description: Scope to analyze (default: templates/)

outputs:
  design_tokens:
    type: dict
    description: Design tokens (colors, spacing, typography)

  components:
    type: list[string]
    description: UI components identified

  report_path:
    type: string
    description: Path to design system documentation

author: architect agent
created: 2025-10-19
---

# Design System Skill

Design system generation for ux-design-expert.

## Workflow

1. **Scan Templates**: Analyze HTML/templates for Tailwind usage
2. **Extract Tokens**: Identify color palette, spacing, typography
3. **Identify Components**: Detect reusable UI patterns
4. **Generate Documentation**: Create design system docs
5. **Visualize Relationships**: Component dependency graph

## Expected Time Savings

- **Manual Design System Creation**: 4-6 hours
- **With Skill**: 30 minutes
- **Time Saved**: 90% reduction
