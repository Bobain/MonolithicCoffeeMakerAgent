# task-separator Skill

**Agent**: architect
**Purpose**: Analyze task independence for parallel execution safety
**Location**: `.claude/skills/architect/task-separator/`

## Overview

Analyzes multiple ROADMAP priorities to determine if they can be executed in parallel without file conflicts. This enables the orchestrator to safely spawn multiple code_developer instances in git worktrees.

## Capabilities

1. **Spec File Parsing**: Extract file impacts from technical specifications
2. **Conflict Detection**: Identify shared files between priorities
3. **Independence Analysis**: Determine which priority pairs are safe to parallelize
4. **Confidence Scoring**: Rate analysis confidence (0-100)

## Input

```python
{
    "priority_ids": [23, 24, 25]  # List of PRIORITY numbers to analyze
}
```

## Output

```python
{
    "valid": true,
    "independent_pairs": [
        (23, 24),  # These priorities don't share files
        (23, 25),
        (24, 25)
    ],
    "conflicts": {},
    "task_file_map": {
        23: ["coffee_maker/cli/foo.py", "tests/test_foo.py"],
        24: ["coffee_maker/utils/bar.py", "tests/test_bar.py"],
        25: ["coffee_maker/skills/baz.py"]
    }
}
```

## Performance

- **Target**: <10s for 3 priorities
- **Acceptable**: <30s
- **Unacceptable**: >60s

## Related

- **SPEC-108**: Parallel Agent Execution with Git Worktrees
- **ParallelExecutionCoordinator**: Uses this skill for validation
- **ContinuousWorkLoop**: Calls this skill to detect parallelizable work
