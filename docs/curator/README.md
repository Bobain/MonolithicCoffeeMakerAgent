# Curator Agent Directory

## Purpose
This directory contains evolving agent playbooks, curation reports, and context health metrics.

## Owned By
**curator** agent (ACE framework)

## Contents

### Agent Playbooks
Structured, evolving contexts for each supervised agent:
- Core strategies (high priority, high confidence)
- Tool usage patterns
- Domain concepts
- Known failure modes
- Conditional strategies

### Curation Reports
- Delta integration decisions
- Semantic de-duplication results
- Pruning actions
- Playbook health metrics

### Health Metrics
- Total active bullets
- Average helpful count
- Effectiveness ratio: helpful/(helpful+harmful)
- Coverage score

## File Naming Convention
- `playbook_{agent_name}.md` - Current playbook for each agent
- `playbook_{agent_name}_v{version}.json` - Version-controlled playbook state
- `curation_report_{date}.md` - Integration and maintenance reports
- `health_metrics_{agent_name}.json` - Ongoing effectiveness tracking

## Playbook Structure
```markdown
# Agent Playbook: {agent_name}

## 🎯 Core Strategies (High Priority, High Confidence)
### {category_1}
- [bullet_001] {content} [helpful: 10, harmful: 0]

## 🔧 Tool Usage Patterns
- [bullet_012] {content} [helpful: 5, harmful: 0]

## 📚 Domain Concepts
- [bullet_020] {content} [helpful: 3, harmful: 0]

## ⚠️ Known Failure Modes
- [bullet_025] {content} [harmful: 5, helpful: 0]

## 🔄 Conditional Strategies
- [bullet_030] {content} [helpful: 6, harmful: 1]
```

## Deterministic Merge Logic
- Similarity > 0.90: MERGE_IDENTICAL
- Similarity > 0.85 + same category: MERGE_SIMILAR
- Similarity > 0.75 + same type: UPDATE_EXISTING or INCREMENT_COUNTER

## Context Collapse Prevention
Monitor warning signs:
- Total bullets decreasing rapidly (>20% in single session)
- Average content length decreasing
- Loss of domain-specific terminology
- Effectiveness ratio declining

## Target Metrics
- Healthy size: 50-150 bullets
- Effectiveness ratio: > 0.85
- Update frequency: 20-30% bullets/week
- Pruning rate: 5-10% bullets/month

## Reference
Based on ACE (Agentic Context Engineering) framework: https://www.arxiv.org/abs/2510.04618

---
*Last Updated: 2025-10-14*
