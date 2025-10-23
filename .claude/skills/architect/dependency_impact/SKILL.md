---
name: dependency-impact
version: 1.0.0
agent: architect
scope: agent-specific
description: >
  Automated dependency impact analysis: analyze dependency changes,
  identify breaking changes, assess migration risk, suggest rollout plan.

triggers:
  - "analyze dependency impact"
  - "assess dependency change"
  - "dependency migration risk"

requires:
  - safety>=2.0  # Dependency vulnerability scanner

inputs:
  package_name:
    type: string
    required: true
    description: Package to analyze

  current_version:
    type: string
    required: true
    description: Current version

  target_version:
    type: string
    required: true
    description: Target version to upgrade to

outputs:
  breaking_changes:
    type: list[string]
    description: List of breaking changes

  migration_risk:
    type: string
    description: Risk level (LOW, MEDIUM, HIGH, CRITICAL)

  rollout_plan:
    type: list[string]
    description: Suggested rollout steps

  report_path:
    type: string
    description: Path to impact analysis report

author: architect agent
created: 2025-10-19
---

# Dependency Impact Skill

Automated dependency impact analysis for architect.

## Workflow

1. **Fetch Changelog**: Get changelog between versions
2. **Identify Breaking Changes**: Parse for breaking changes
3. **Scan Codebase**: Find usages of changed APIs
4. **Assess Risk**: Determine migration risk level
5. **Generate Rollout Plan**: Suggest migration steps
6. **Create Report**: Synthetic 1-2 page report

## Expected Time Savings

- **Manual Impact Analysis**: 45 minutes
- **With Skill**: 5-10 minutes
- **Time Saved**: 80% reduction
