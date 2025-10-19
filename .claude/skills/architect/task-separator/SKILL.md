---
name: task-separator
version: 1.0.0
agent: architect
scope: agent-specific
description: >
  Analyze ROADMAP priorities to identify independent, non-conflicting tasks
  for parallel execution. Validates task separation by checking file dependencies
  and detecting potential conflicts.

triggers:
  - analyze task separation
  - identify parallel tasks
  - validate task independence

requires: []

inputs:
  priority_ids:
    type: list[int]
    required: true
    description: List of PRIORITY numbers to analyze (e.g., [20, 21, 22])

outputs:
  independent_pairs:
    type: list[tuple[int, int]]
    description: Pairs of priorities that can be executed in parallel

  conflicts:
    type: dict[tuple[int, int], list[str]]
    description: Map of priority pairs to conflicting files

  task_file_map:
    type: dict[int, list[str]]
    description: Map of priorities to files they will modify

author: architect agent
created: 2025-10-19
---

# Task Separator Skill

Automated task separation analysis for parallel execution.

## Workflow

1. **Extract File Lists**: Read technical specs for each priority
2. **Build File Map**: Map priorities to files they will modify
3. **Find Safe Pairs**: Identify priority pairs with zero file overlap
4. **Find Conflicts**: Detect priority pairs with file conflicts
5. **Generate Report**: Return independent pairs and conflicts

## Expected Time Savings

- **Manual Task Separation**: 30-45 minutes per batch
- **With Skill**: 10-15 seconds
- **Time Saved**: 98% reduction

## Example Usage

```python
from coffee_maker.skills.architect.task_separator import analyze_task_separation

result = analyze_task_separation([20, 21, 22, 23])

# Result:
# {
#   "independent_pairs": [(20, 21), (20, 23)],
#   "conflicts": {(21, 22): ["coffee_maker/cli/dashboard.py"]},
#   "task_file_map": {
#     20: ["coffee_maker/skills/*"],
#     21: ["coffee_maker/cli/dashboard.py"],
#     22: ["coffee_maker/cli/dashboard.py"],
#     23: ["coffee_maker/orchestrator/*"]
#   }
# }
```
