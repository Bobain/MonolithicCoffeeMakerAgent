# finalize

## Purpose
Run quality checks (Black, MyPy, type hints), generate conventional commit message, create git commit.

## Parameters
```yaml
files: List[str]  # Files to finalize (required)
commit_message: str = None  # Custom message, auto-generated if None
skip_quality: bool = false  # Skip Black/MyPy checks
auto_push: bool = false  # Push to remote after commit
```

## Workflow
1. Run Black formatter on files
2. Run MyPy type checker
3. Validate 100% type hint coverage
4. Generate conventional commit message if not provided
5. Create git commit with files
6. Optionally push to remote
7. Return FinalizeResult

## Quality Checks
```bash
# Black formatting
black {files} --check --line-length 120

# MyPy type checking
mypy {files} --strict

# Type hint coverage validation
python -m mypy --html-report htmlcov {files}
```

## Result Object
```python
@dataclass
class FinalizeResult:
    quality_score: int  # 0-100 based on checks
    commit_sha: str  # Git commit hash
    files_committed: List[str]
    status: str  # "success" | "partial" | "failed"
    checks_passed: List[str]  # ["black", "mypy", "type_hints"]
    checks_failed: List[str]
```

## Commit Message Generation
```python
# Analyze changes to determine type
commit_type = "feat"  # feat | fix | refactor | test | docs
scope = extract_scope_from_files(files)  # e.g., "auth"
description = generate_description(files, changes)

# Format: {type}({scope}): {description}
# Example: feat(auth): Implement JWT token validation
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| BlackFailed | Style violations | Review Black output, fix manually |
| MyPyFailed | Type errors | Add/fix type hints |
| TypeHintMissing | Functions without hints | Add type hints to all functions |
| GitCommitFailed | Nothing to commit / git error | Check git status, stage files |

## Example
```python
result = finalize(files=["auth.py", "test_auth.py"])
# FinalizeResult(
#   quality_score=95,
#   commit_sha="abc123def456",
#   files_committed=["auth.py", "test_auth.py"],
#   status="success",
#   checks_passed=["black", "mypy", "type_hints"],
#   checks_failed=[]
# )
```

## Related Commands
- implement() - Generate code first
- test() - Validate before finalizing

---
Estimated: 50 lines | Context: ~3% | Examples: finalize_examples.md
