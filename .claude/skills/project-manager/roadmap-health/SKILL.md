---
name: roadmap-health
version: 1.0.0
agent: project-manager
scope: agent-specific
description: >
  Automated ROADMAP health monitoring: analyze priorities, check GitHub
  status, identify blockers, generate synthetic health report.

triggers:
  - check roadmap health
  - analyze roadmap status
  - identify blockers
  - roadmap health report

requires:
  - gh>=2.0  # GitHub CLI

inputs:
  generate_report:
    type: bool
    required: false
    description: Generate health report file? (default: true)

outputs:
  health_status:
    type: string
    description: Overall health (HEALTHY, WARNING, CRITICAL)

  blockers:
    type: list[dict]
    description: List of blockers (priority, blocker, severity)

  github_status:
    type: dict
    description: GitHub status (open PRs, CI failures, etc.)

  report_path:
    type: string
    description: Path to generated health report

author: architect agent
created: 2025-10-19
---

# ROADMAP Health Skill

Automated ROADMAP health monitoring for project_manager.

## Workflow

1. **Parse ROADMAP**: Extract all priorities, statuses
2. **Check GitHub**: Query PRs, issues, CI/CD status
3. **Identify Blockers**: Detect stuck priorities, failed CI
4. **Analyze Trends**: Compare vs last week
5. **Generate Report**: Synthetic 1-2 page report
6. **Send Notification**: Alert user if critical blockers

## Expected Time Savings

- **Manual Health Check**: 30-45 minutes
- **With Skill**: 5 minutes
- **Time Saved**: 85% reduction
