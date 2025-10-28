# fix

## Purpose
Auto-fix code issues: run Black formatting, autoflake unused imports, isort import ordering, optionally commit changes.

## Parameters
```yaml
target: str = "."  # Path to fix (file, directory, or ".")
fix_type: str = "all"  # "all" | "format" | "imports" | "style"
auto_commit: bool = false  # Create commit after fixes
verify_tests: bool = true  # Run tests after fixes
```

## Workflow
1. Identify files to fix
2. Run Black formatter (fix_type: format or all)
3. Run autoflake for unused imports (fix_type: imports or all)
4. Run isort for import ordering (fix_type: imports or all)
5. Run tests if verify_tests=True
6. Create commit if auto_commit=True and tests pass
7. Return FixResult with file counts

## Bash Commands
```bash
# Format with Black
black {target} --line-length=120

# Remove unused imports with autoflake
autoflake --remove-all-unused-imports --in-place {target}

# Sort imports with isort
isort {target} --profile black

# Verify with tests
pytest --tb=short
```

## Result Object
```python
@dataclass
class FixResult:
    files_modified: int
    fixes_applied: dict  # {format: 5, imports: 3, style: 2}
    tests_passed: bool
    commit_created: bool
    status: str  # "success" | "partial" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| ToolNotInstalled | Black/autoflake missing | Install: poetry add --dev black autoflake isort |
| TestsFailed | Fixes broke tests | Revert changes |
| NoFilesFound | Target path invalid | Check target path exists |
| CommitFailed | Git error | Check git status |

## Example
```python
result = fix(target="coffee_maker/", fix_type="all", verify_tests=True)
# FixResult(
#   files_modified=12,
#   fixes_applied={"format": 8, "imports": 3, "style": 1},
#   tests_passed=True,
#   commit_created=False,
#   status="success"
# )
```

## Related Commands
- analyze() - Identify issues before fixing
- test() (code_developer) - Run tests

---
Estimated: 50 lines | Context: ~3% | Examples: fix_examples.md
