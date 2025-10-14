# Reflector Agent Directory

## Purpose
This directory contains reflection analyses, extracted insights, and proposed delta items for context improvement.

## Owned By
**reflector** agent (ACE framework)

## Contents

### Reflection Reports
- Execution trace analysis
- Success/failure pattern identification
- Concrete, actionable insights
- Structured delta proposals

### Delta Items
Each delta includes:
- **Type**: helpful_strategy | harmful_pattern | domain_concept | tool_usage | failure_mode
- **Content**: Specific, actionable insight (1-3 sentences)
- **Evidence**: Examples from execution traces
- **Applicability**: When/where to apply
- **Priority**: high | medium | low
- **Confidence**: high | medium | low
- **Action**: add_new | update_existing | mark_harmful

## File Naming Convention
- `reflection_report_{agent_name}_{timestamp}.md` - Analysis reports
- `delta_proposals_{agent_name}_{date}.json` - Structured delta items
- `refinement_rounds_{session_id}.md` - Multi-round refinement tracking

## Quality Guidelines

### DO ✓
- Be specific and concrete
- Provide clear evidence
- Focus on actionable insights
- Maintain appropriate scope

### DON'T ✗
- Be vague
- Make unsupported claims
- Generate redundant insights
- Over-generalize

## Reference
Based on ACE (Agentic Context Engineering) framework: https://www.arxiv.org/abs/2510.04618

---
*Last Updated: 2025-10-14*
