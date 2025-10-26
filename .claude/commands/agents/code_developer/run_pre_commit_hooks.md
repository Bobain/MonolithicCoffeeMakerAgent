---
command: code_developer.run_pre_commit_hooks
agent: code_developer
action: run_pre_commit_hooks
tables:
  write: [system_audit]
  read: []
required_skills: []
required_tools: [database, pre-commit]
---

# Command: code_developer.run_pre_commit_hooks

## Purpose
Execute pre-commit hooks (black, flake8, mypy, isort, etc.) and track code quality metrics.

## Input Parameters

```yaml
hooks: array             # Optional - Specific hooks to run (default: all)
all_files: boolean       # Run on all files (default: false, only staged)
show_diff: boolean       # Show diff of changes (default: true)
fail_on_changes: boolean # Fail if hooks modify files (default: false)
```

## Database Operations

### 1. Build Pre-Commit Command
```python
import subprocess
import json
from datetime import datetime

def run_pre_commit_hooks(db: DomainWrapper, params: dict):
    cmd = ["pre-commit", "run"]

    # Add specific hooks if provided
    if params.get("hooks"):
        for hook in params["hooks"]:
            cmd.extend(["--hook-stage", "commit", hook])

    # Run on all files or staged only
    if params.get("all_files", False):
        cmd.append("--all-files")

    if not params.get("show_diff", True):
        cmd.append("--no-show-diff")
```

### 2. Execute Hooks
```python
    # Run pre-commit
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr

    hooks_passed = result.returncode == 0
```

### 3. Parse Hook Results
```python
    # Parse output to identify which hooks ran and results
    import re

    hooks_run = []
    hooks_failed = []
    files_modified = []

    # Parse hook results from output
    hook_pattern = r"(\w+)\.\.\.\.(passed|failed|skipped)"
    hook_matches = re.findall(hook_pattern, output)

    for hook_name, status in hook_matches:
        if status == "passed":
            hooks_run.append({"hook": hook_name, "status": "passed"})
        elif status == "failed":
            hooks_run.append({"hook": hook_name, "status": "failed"})
            hooks_failed.append(hook_name)

    # Detect files modified by hooks
    file_pattern = r"(?:modified|added|changed):\s+(.*)"
    file_matches = re.findall(file_pattern, output)
    files_modified = [f.strip() for f in file_matches]
```

### 4. Validate Code Quality
```python
    # Check if hooks made changes (which might indicate issues)
    if files_modified and params.get("fail_on_changes", False):
        return {
            "success": False,
            "error": "Hooks modified files",
            "hooks_run": len(hooks_run),
            "hooks_passed": len([h for h in hooks_run if h["status"] == "passed"]),
            "hooks_failed": len(hooks_failed),
            "files_modified": files_modified,
            "details": hooks_run
        }
```

### 5. Record Metrics
```python
    # Record hook execution in audit trail
    db.write("system_audit", {
        "table_name": "pre_commit_runs",
        "item_id": f"hooks-{datetime.now().isoformat()}",
        "action": "executed",
        "field_changed": "hooks",
        "new_value": json.dumps(hooks_run),
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat(),
        "metadata": json.dumps({
            "total_hooks": len(hooks_run),
            "failed": hooks_failed,
            "files_modified": files_modified
        })
    }, action="create")

    return {
        "success": hooks_passed,
        "hooks_run": len(hooks_run),
        "hooks_passed": len([h for h in hooks_run if h["status"] == "passed"]),
        "hooks_failed": len(hooks_failed),
        "files_modified": files_modified,
        "details": hooks_run
    }
```

## Output

```json
{
  "success": true,
  "hooks_run": 5,
  "hooks_passed": 5,
  "hooks_failed": 0,
  "files_modified": ["coffee_maker/models/user.py"],
  "details": [
    {
      "hook": "black",
      "status": "passed",
      "files_changed": 1
    },
    {
      "hook": "flake8",
      "status": "passed"
    },
    {
      "hook": "mypy",
      "status": "passed"
    },
    {
      "hook": "isort",
      "status": "passed"
    },
    {
      "hook": "trailing-whitespace",
      "status": "passed"
    }
  ]
}
```

## Success Criteria

- ✅ All hooks executed
- ✅ Code formatted (black)
- ✅ Linting passed (flake8)
- ✅ Type checking passed (mypy)
- ✅ Import sorting passed (isort)
- ✅ Files modified tracked
- ✅ Metrics recorded

## Configured Hooks

The project has pre-commit configured with:

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| black | Code formatting | Yes (modifies files) |
| flake8 | Linting | No (reports issues) |
| mypy | Type checking | No (reports issues) |
| isort | Import sorting | Yes (modifies files) |
| trailing-whitespace | Whitespace cleanup | Yes |
| end-of-file-fixer | EOF newlines | Yes |
| check-yaml | YAML validation | No |

## Run All Hooks

Default mode - runs only on staged files:

```python
run_pre_commit_hooks(db, {})
```

## Run on All Files

Useful after major changes:

```python
run_pre_commit_hooks(db, {
    "all_files": True
})
```

## Run Specific Hooks

Run only formatting and type checking:

```python
run_pre_commit_hooks(db, {
    "hooks": ["black", "mypy"]
})
```

## Fail if Hooks Modify Files

Strict mode - fail if any hook needs to modify code:

```python
run_pre_commit_hooks(db, {
    "fail_on_changes": True
})
# Returns error if black or isort modified files
```

## Bash Equivalent

```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run with diffs
pre-commit run --show-diff-on-failure

# Run at commit stage
pre-commit run --hook-stage commit
```

## Workflow

```
1. code_developer completes implementation
2. code_developer calls run_pre_commit_hooks
3. Hooks format, lint, and type-check code
4. If failures: code_developer reviews output
5. If passes: hooks may modify files (black, isort)
6. code_developer reviews modifications
7. code_developer commits changes
```

## Integration with Implementation

Before committing code:

```python
# 1. Run tests
test_results = run_test_suite(db, {})
if not test_results["success"]:
    fix_failing_tests(db, {"auto_fix": True})

# 2. Run pre-commit hooks
hook_results = run_pre_commit_hooks(db, {
    "all_files": False,  # Only staged files
    "show_diff": True
})

if not hook_results["success"]:
    # Review and fix issues
    print(f"Hook failures: {hook_results['details']}")

# 3. Stage modified files
# git add -A

# 4. Commit
# git commit -m "feat: Implementation message"
```

## Code Quality Standards

| Standard | Tool | Config |
|----------|------|--------|
| Format | black | 120 char line length |
| Lint | flake8 | Max 120 chars, ignore E501 |
| Types | mypy | Strict mode, inline types |
| Imports | isort | Python 3.7+, profile=black |

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| HookFailedError | Code quality issue | Fix reported issues |
| ToolNotFoundError | Tool not installed | poetry install pre-commit |
| ConfigError | Invalid pre-commit config | Check .pre-commit-config.yaml |

## Performance Tips

1. Use `all_files: False` (default) for development
2. Use `all_files: True` before PR creation
3. Run `black` and `isort` first (fastest)
4. Run `mypy` last (slowest, most thorough)
5. Skip slow hooks with `--skip` if needed

## Pre-Commit Config

Configuration in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
```
