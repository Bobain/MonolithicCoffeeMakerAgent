---
name: visual-regression
version: 1.0.0
agent: ux-design-expert
scope: agent-specific
description: >
  Visual regression testing: capture screenshots before/after changes,
  compare pixel-by-pixel, highlight differences, generate report.

triggers:
  - "visual regression test"
  - "detect UI changes"
  - "screenshot comparison"

requires:
  - puppeteer (MCP)
  - pixelmatch>=5.0  # Pixel-level image comparison

inputs:
  baseline_url:
    type: string
    required: true
    description: Baseline URL (before changes)

  current_url:
    type: string
    required: true
    description: Current URL (after changes)

  pages:
    type: list[string]
    required: true
    description: Pages to test (e.g., ["/", "/dashboard", "/settings"])

outputs:
  differences_found:
    type: bool
    description: Visual differences detected?

  diff_screenshots:
    type: list[string]
    description: Diff screenshots showing differences

  report_path:
    type: string
    description: Path to regression report

author: architect agent
created: 2025-10-19
---

# Visual Regression Skill

Visual regression testing for ux-design-expert.

## Workflow

1. **Capture Baseline**: Screenshot baseline pages
2. **Capture Current**: Screenshot current pages
3. **Compare Pixel-by-Pixel**: Use pixelmatch to detect differences
4. **Highlight Differences**: Generate diff images
5. **Generate Report**: Visual regression report with screenshots

## Expected Time Savings

- **Manual Visual Testing**: 1 hour
- **With Skill**: 10 minutes
- **Time Saved**: 83% reduction
