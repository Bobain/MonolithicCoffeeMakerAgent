---
name: bug-analyzer
version: 1.0.0
agent: assistant
scope: agent-specific
description: >
  Automated bug analysis: reproduce bug, capture logs/screenshots,
  analyze root cause, generate comprehensive bug report.

triggers:
  - "analyze bug"
  - "reproduce bug"
  - "bug root cause analysis"
  - "comprehensive bug report"

requires:
  - puppeteer (MCP)

inputs:
  bug_description:
    type: string
    required: true
    description: Bug description

  reproduction_steps:
    type: list[string]
    required: false
    description: Steps to reproduce (auto-generated if not provided)

outputs:
  reproduced:
    type: bool
    description: Bug successfully reproduced?

  root_cause:
    type: string
    description: Root cause analysis

  logs:
    type: list[string]
    description: Captured log files

  screenshots:
    type: list[string]
    description: Bug screenshots

  report_path:
    type: string
    description: Path to bug report

author: architect agent
created: 2025-10-19
---

# Bug Analyzer Skill

Automated bug analysis for assistant.

## Workflow

1. **Reproduce Bug**: Execute reproduction steps
2. **Capture Evidence**: Logs, screenshots, stack traces
3. **Analyze Root Cause**: Identify failing code path
4. **Generate Report**: Comprehensive bug report with:
   - Root cause analysis
   - Requirements for fix
   - Expected behavior once corrected
   - Complete reproduction steps
   - Environment details
   - Impact assessment

## Expected Time Savings

- **Manual Bug Analysis**: 1-2 hours
- **With Skill**: 15-20 minutes
- **Time Saved**: 75-85% reduction
