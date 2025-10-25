---
name: code-forensics
version: 1.0.0
agent: assistant (with code analysis skills)
scope: agent-specific
description: >
  Code forensics analysis: trace file evolution, identify contributors,
  analyze commit patterns, detect code hotspots, generate insights.

triggers:
  - "code forensics"
  - "trace code evolution"
  - "who wrote this code"
  - "commit history analysis"

requires:
  - git

inputs:
  scope:
    type: string
    required: false
    description: Scope to analyze (file, directory, or entire repo)

  time_range:
    type: string
    required: false
    description: Time range (e.g., "last 6 months", default: all time)

outputs:
  contributors:
    type: list[dict]
    description: Top contributors (name, commits, lines changed)

  hotspots:
    type: list[string]
    description: Code hotspots (files changed most frequently)

  patterns:
    type: dict
    description: Commit patterns (time of day, day of week)

  report_path:
    type: string
    description: Path to forensics report

author: architect agent
created: 2025-10-19
---

# Code Forensics Skill

Code forensics analysis for assistant (with code analysis skills).

## Workflow

1. **Analyze Git History**: Parse git log for commits
2. **Identify Contributors**: Extract authors, commit counts, lines changed
3. **Detect Hotspots**: Find files changed most frequently
4. **Analyze Patterns**: Identify commit time patterns
5. **Generate Insights**: Extract meaningful insights
6. **Create Report**: Synthetic forensics report

## Expected Time Savings

- **Manual Forensics Analysis**: 1-2 hours
- **With Skill**: 10-15 minutes
- **Time Saved**: 85% reduction

## Use Cases

- **Onboarding**: "Who are the experts on this module?"
- **Code Review**: "What's the history of this file?"
- **Refactoring**: "Which files are changed most often?" (hotspots → refactor targets)
