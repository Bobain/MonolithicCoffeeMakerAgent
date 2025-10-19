---
name: architecture-analysis
version: 1.0.0
agent: architect
scope: agent-specific
description: >
  Automated architecture analysis: scan codebase, build dependency graph,
  identify patterns, suggest improvements, generate synthetic report.

triggers:
  - analyze architecture
  - review codebase structure
  - architecture health check

requires:
  - radon>=6.0  # Code complexity metrics

inputs:
  scope:
    type: string
    required: false
    description: Scope to analyze (default: entire codebase)

outputs:
  complexity_score:
    type: float
    description: Average cyclomatic complexity

  recommendations:
    type: list[string]
    description: List of improvement recommendations

  report_path:
    type: string
    description: Path to analysis report

author: architect agent
created: 2025-10-19
---

# Architecture Analysis Skill

Automated architecture analysis for architect.

## Workflow

1. **Scan Codebase**: Analyze all Python files
2. **Measure Complexity**: Calculate cyclomatic complexity
3. **Identify Patterns**: Detect anti-patterns, code smells
4. **Generate Recommendations**: Suggest refactorings, improvements
5. **Create Report**: Synthetic 1-2 page report

## Expected Time Savings

- **Manual Architecture Review**: 2-3 hours
- **With Skill**: 15-20 minutes
- **Time Saved**: 85% reduction
