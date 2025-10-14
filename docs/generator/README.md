# Generator Agent Directory

## Purpose
This directory contains execution reports, state logs, and comparative analyses from the Generator agent.

## Owned By
**generator** agent (ACE framework)

## Contents

### Execution Reports
- Dual execution traces for target agents
- Comparative analysis between executions
- Tool usage patterns
- Context bullet effectiveness tracking

### State Management
```json
{
  "agent_id": "{target_agent}",
  "total_executions": 0,
  "successful_executions": 0,
  "failed_executions": 0,
  "common_tools_used": [],
  "frequent_failures": [],
  "context_effectiveness_scores": {}
}
```

## File Naming Convention
- `execution_report_{agent_name}_{timestamp}.md` - Individual execution reports
- `state_log_{agent_name}.json` - Running state for each supervised agent
- `comparative_analysis_{date}.md` - Cross-agent pattern analysis

## Reference
Based on ACE (Agentic Context Engineering) framework: https://www.arxiv.org/abs/2510.04618

---
*Last Updated: 2025-10-14*
