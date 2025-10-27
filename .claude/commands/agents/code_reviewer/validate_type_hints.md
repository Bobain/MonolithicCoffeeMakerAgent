---
command: code_reviewer.validate_type_hints
agent: code_reviewer
action: validate_type_hints
tables:
  write: [review_issue]
  read: [review_code_review, review_commit]
required_tools: [mypy, git]
estimated_duration_seconds: 20
---

# Command: code_reviewer.validate_type_hints

## Purpose

Run mypy in strict mode to validate type hint compliance and catch type-related bugs. This command ensures code uses proper type annotations for better maintainability and IDE support.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to check
review_id: string               # Required - link issues to review
strict_mode: boolean            # Use mypy strict (default: true)
check_untyped: boolean          # Flag untyped definitions (default: true)
check_unused_ignores: boolean   # Find unnecessary type ignores (default: true)
severity_threshold: string      # Report: "all", "error", "warning" (default: "error")
show_error_codes: boolean       # Show error codes (default: true)
per_module_strict: array        # Modules to check strict (default: coffee_maker/*)
```

## Database Operations

**Query: Insert type issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, 'Type Safety', ?, ?, ?, ?, datetime('now'));
```

## External Tools

### Mypy Type Checker

```bash
# Run mypy in strict mode
mypy coffee_maker/ --strict --show-error-codes --output-format=json 2>&1

# JSON Output Format:
# [
#   {
#     "file": "coffee_maker/auth.py",
#     "line": 42,
#     "column": 10,
#     "severity": "error",
#     "message": "Unsupported operand types for + (\"int\" and \"str\")",
#     "message_id": "operator"
#   }
# ]
```

### Mypy Error Codes

| Code | Issue | Severity |
|------|-------|----------|
| arg-type | Argument type mismatch | ERROR |
| assignment | Assignment type mismatch | ERROR |
| operator | Unsupported operand types | ERROR |
| return-value | Return value mismatch | ERROR |
| no-redef | Function redefined | ERROR |
| no-untyped-def | Missing function type hint | WARNING |
| no-untyped-call | Calling untyped function | WARNING |
| unused-ignore | Unnecessary type: ignore | WARNING |
| missing-return | Missing return statement | ERROR |
| name-defined | Undefined name | ERROR |
| redundant-expr | Redundant expression | WARNING |
| union-attr | Accessing attribute on union type | ERROR |
| attr-defined | Undefined attribute | ERROR |
| misc | Miscellaneous error | WARNING |
| valid-type | Invalid type annotation | ERROR |
| import | Import error | ERROR |
| unused-type-ignore | Unused # type: ignore | WARNING |

## Success Criteria

- ✅ Runs mypy in strict mode without crashing
- ✅ Parses JSON output correctly
- ✅ Maps mypy severities to issue severities
- ✅ Identifies type errors and warnings
- ✅ Creates review_issue records for each finding
- ✅ Suggests type hint improvements
- ✅ Reports untyped function definitions
- ✅ Completes in <20 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "type_check_duration_seconds": 16.2,
  "type_compliance": {
    "total_errors": 2,
    "total_warnings": 5,
    "total_issues": 7,
    "compliance_score": 95.2
  },
  "error_breakdown": {
    "arg_type": 1,
    "assignment": 1,
    "no_untyped_def": 3,
    "unused_ignore": 2
  },
  "issues": [
    {
      "id": "ISS-1",
      "severity": "HIGH",
      "category": "Type Safety",
      "file_path": "coffee_maker/auth.py",
      "line_number": 42,
      "column": 10,
      "error_code": "operator",
      "message": "Unsupported operand types for + (\"int\" and \"str\")",
      "description": "Type mismatch: cannot add int and str together",
      "recommendation": "Ensure both operands are the same type",
      "code_snippet": "result = count + password  # Wrong: count is int, password is str"
    },
    {
      "id": "ISS-2",
      "severity": "MEDIUM",
      "category": "Type Safety",
      "file_path": "coffee_maker/db.py",
      "line_number": 15,
      "column": 0,
      "error_code": "no-untyped-def",
      "message": "Function is missing a return type annotation",
      "description": "Function 'connect' has no return type hint",
      "recommendation": "Add return type: def connect() -> Connection:",
      "code_snippet": "def connect(host, port):"
    }
  ],
  "untyped_functions": [
    {
      "file": "coffee_maker/utils.py",
      "function": "format_output",
      "line": 25,
      "suggestion": "def format_output(data: dict) -> str:"
    }
  ],
  "unused_ignores": [
    {
      "file": "coffee_maker/legacy.py",
      "line": 42,
      "message": "Unnecessary # type: ignore comment"
    }
  ],
  "type_score": 95,
  "summary": {
    "perfect_score": false,
    "needs_fixes": 7,
    "estimated_fix_time": "1-2 hours"
  }
}
```

## Mypy Configuration

**mypy.ini / setup.cfg**:
```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict = True
```

## Error Handling

**No Type Issues Found**:
```json
{
  "status": "success",
  "type_compliance": {
    "total_errors": 0,
    "total_warnings": 0,
    "compliance_score": 100
  },
  "message": "Perfect type safety - all code properly typed"
}
```

**Mypy Not Installed**:
```json
{
  "status": "error",
  "error_type": "TOOL_NOT_FOUND",
  "message": "mypy not installed",
  "installation": "pip install mypy",
  "exit_code": 1
}
```

**Syntax Error**:
```json
{
  "status": "error",
  "error_type": "PARSE_ERROR",
  "message": "Syntax error in analyzed file",
  "file": "coffee_maker/broken.py",
  "recovery": "Fix syntax errors and retry"
}
```

## Examples

### Example 1: Full type checking

```bash
code_reviewer.validate_type_hints(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  strict_mode=true,
  check_untyped=true
)
```

### Example 2: Errors only

```bash
code_reviewer.validate_type_hints(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  severity_threshold="error"
)
```

### Example 3: With unused ignore check

```bash
code_reviewer.validate_type_hints(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_unused_ignores=true
)
```

## Implementation Notes

- Project standard is 100% type hint coverage
- Mypy strict mode enforces complete typing
- Type ignores should be justified with comments
- Consider mypy plugins for special cases (pytest, sqlalchemy, etc.)
- Review type error messages carefully - they often point to logic bugs
- Gradual typing acceptable for legacy code
- Store mypy versions for reproducibility

## Type Hint Patterns

### Pattern 1: Function Signatures

**Before** (no types):
```python
def authenticate(username, password):
    return validate_credentials(username, password)
```

**After** (complete types):
```python
def authenticate(username: str, password: str) -> bool:
    """Authenticate user with credentials."""
    return validate_credentials(username, password)
```

### Pattern 2: Optional Types

**Before** (implicit None):
```python
def get_user(user_id):
    if user_id in users:
        return users[user_id]
    return None
```

**After** (explicit Optional):
```python
from typing import Optional

def get_user(user_id: int) -> Optional[User]:
    """Get user by ID, returning None if not found."""
    if user_id in users:
        return users[user_id]
    return None
```

### Pattern 3: Union Types

**Before** (unclear):
```python
def process(data):
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, int):
        return data * 2
```

**After** (clear types):
```python
from typing import Union

def process(data: Union[str, int]) -> Union[str, int]:
    """Process string or integer."""
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, int):
        return data * 2
    raise TypeError(f"Unsupported type: {type(data)}")
```

### Pattern 4: Collections

**Before** (implicit Any):
```python
def process_list(items):
    return [item.upper() for item in items]
```

**After** (explicit types):
```python
from typing import List

def process_list(items: List[str]) -> List[str]:
    """Convert all strings to uppercase."""
    return [item.upper() for item in items]
```

### Pattern 5: Generics

**Before** (no constraints):
```python
class Container:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value
```

**After** (generic type):
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Container(Generic[T]):
    """Generic container for any type."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        """Get stored value."""
        return self.value
```

## Related Commands

- `code_reviewer.generate_review_report` - Main review orchestrator
- `code_reviewer.check_style_compliance` - Code quality checks
- `code_reviewer.review_documentation` - Documentation quality

---

**Version**: 1.0
**Last Updated**: 2025-10-26
