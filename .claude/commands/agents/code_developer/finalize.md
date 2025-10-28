<!-- DEPRECATED -->
<!-- This file is no longer used and will be removed in a future version. -->
<!-- Date deprecated: 2025-10-28 -->

<!-- Reason: Replaced by workflow.work() command in coffee_maker/commands/workflow/code_developer_workflow.py -->

# finalize

## Purpose
Run quality checks (Black, MyPy), generate conventional commit message, create git commit with 🤖 footer, verify all checks pass.

## Parameters
```yaml
task_id: str  # Required, format: TASK-N-M
run_checks: bool = true  # Run Black, MyPy validation
auto_commit: bool = true  # Create git commit
push: bool = false  # Push to remote (use with caution)
```

## Workflow
1. Load task and implementation metadata
2. Run Black formatter (if run_checks=true)
3. Run MyPy type checker (if run_checks=true)
4. Generate conventional commit message
5. Create git commit (if auto_commit=true)
6. Optionally push to remote
7. Record finalization in database
8. Return FinalizeResult

## Quality Checks (EMBEDDED - Essential Tools)

### Black Formatter
```bash
# Format all Python files
black . --line-length=120

# Check formatting without changes
black . --check --line-length=120

# Format specific files
black coffee_maker/auth.py tests/test_auth.py

# Show diffs
black . --diff --line-length=120
```

**Why Black?**
- Enforces consistent code style
- Eliminates style debates
- Required by pre-commit hooks

### MyPy Type Checker
```bash
# Check all files
mypy coffee_maker/

# Check specific file
mypy coffee_maker/auth.py

# Strict mode (recommended)
mypy coffee_maker/ --strict

# Show error codes
mypy coffee_maker/ --show-error-codes
```

**Why MyPy?**
- Catches type errors before runtime
- Improves code documentation
- Required for high-quality code

### Check Results Handling
```python
# Pseudo-code for quality checks
checks_passed = True

# Run Black
black_result = run_command("black . --check")
if black_result.returncode != 0:
    logger.error("Black formatting failed. Running auto-fix...")
    run_command("black .")  # Auto-fix
    checks_passed = False  # Need re-validation

# Run MyPy
mypy_result = run_command("mypy coffee_maker/")
if mypy_result.returncode != 0:
    logger.error("MyPy type checking failed. Manual fixes needed.")
    checks_passed = False

if not checks_passed:
    raise QualityCheckError("Quality checks failed. Review errors above.")
```

## Git Finalization (EMBEDDED)

### Conventional Commit Generation
```bash
# Generate commit message based on task
git commit -m "$(cat <<'EOF'
{type}({scope}): {description}

{Multi-line body with:
- List of changes
- Implementation notes
- Breaking changes if any}

Implements: {task_id}
Closes: {optional_issue_number}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Commit Type Selection Logic
```python
# Determine commit type from files changed
if "feat" in task_description.lower() or new_features:
    commit_type = "feat"
elif "fix" in task_description.lower() or bug_fixes:
    commit_type = "fix"
elif "refactor" in task_description.lower():
    commit_type = "refactor"
elif "test" in files_changed:
    commit_type = "test"
elif "docs" in files_changed:
    commit_type = "docs"
else:
    commit_type = "chore"
```

### Push to Remote (Use with Caution)
```bash
# Push current branch
git push origin HEAD

# Force push (DANGEROUS - avoid unless necessary)
git push origin HEAD --force-with-lease

# Push with tags
git push origin HEAD --tags
```

**Warning**: Only push when explicitly requested. Default: false.

## Database Operations
```sql
-- Record finalization
INSERT INTO finalization_log (
    finalization_id, task_id, black_passed, mypy_passed,
    commit_sha, pushed_to_remote, timestamp
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))

-- Update task status
UPDATE specs_task
SET status = 'finalized', finalized_at = datetime('now')
WHERE task_id = ?
```

## Result Object
```python
@dataclass
class FinalizeResult:
    task_id: str
    black_passed: bool
    mypy_passed: bool
    commit_created: bool
    commit_sha: str  # None if not committed
    pushed: bool
    status: str  # "success" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| BlackFailed | Formatting issues | Auto-fix with `black .` |
| MyPyFailed | Type errors | Manual fixes required |
| NothingToCommit | No staged changes | Check git status |
| CommitFailed | Git error | Resolve conflicts, check permissions |
| PushFailed | Remote rejected | Pull latest, resolve conflicts |

## Example
```python
result = finalize(
    task_id="TASK-8-1",
    run_checks=True,
    auto_commit=True,
    push=False
)
# FinalizeResult(
#   task_id="TASK-8-1",
#   black_passed=True,
#   mypy_passed=True,
#   commit_created=True,
#   commit_sha="abc123def456",
#   pushed=False,
#   status="success"
# )
```

## Common Issues and Fixes

### Black Formatting Failures
```bash
# Issue: Trailing whitespace
# Fix: black . (auto-fixes)

# Issue: Line too long
# Fix: Use black's default wrapping (120 chars)
```

### MyPy Type Errors
```python
# Issue: Missing return type
def process_data(data):  # ❌ Missing return type
    return data

# Fix: Add type hint
def process_data(data: dict) -> dict:  # ✅ Has return type
    return data
```

## Related Commands
- implement() - Create implementation first
- test() - Run tests before finalize

---
Estimated: 120 lines | Context: 7.5% | Self-contained: Yes ✅
