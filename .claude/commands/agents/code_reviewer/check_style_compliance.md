---
command: code_reviewer.check_style_compliance
agent: code_reviewer
action: check_style_compliance
tables:
  write: [review_issue]
  read: [review_code_review, review_commit]
required_tools: [black, flake8, pylint, git]
estimated_duration_seconds: 30
---

# Command: code_reviewer.check_style_compliance

## Purpose

Run black, flake8, and pylint to check code style compliance with project standards (PEP 8, Black formatting, code quality). This command identifies formatting issues, style violations, and code quality problems.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to check
review_id: string               # Required - link issues to review
check_black: boolean            # Check Black formatting (default: true)
check_flake8: boolean           # Check flake8 linting (default: true)
check_pylint: boolean           # Check pylint quality (default: true)
auto_fixable_only: boolean      # Report only auto-fixable issues (default: false)
show_details: boolean           # Include code context (default: true)
```

## Database Operations

**Query: Insert style issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, 'Style', ?, ?, ?, ?, datetime('now'));
```

## External Tools

### 1. Black Formatter Check

```bash
# Check Black compliance (no changes, just report)
black --check --diff coffee_maker/ tests/ 2>&1

# Parse output format:
# would reformat path/to/file.py
# All done! 45 files would be reformatted
```

**Severity Mapping**:
- Black reformatting needed → HIGH (auto-fixable in <1 min)

**Issue Template**:
- File: {file_path}
- Severity: HIGH
- Category: Style
- Description: "Black formatting would change code"
- Recommendation: "Run `black {file_path}` to auto-fix"
- Effort: "1 minute"

### 2. Flake8 Linting

```bash
# Run flake8 with JSON output
flake8 coffee_maker/ tests/ --max-line-length=120 --format=json 2>&1

# JSON Output Format:
# [
#   {
#     "filename": "path/to/file.py",
#     "line": 42,
#     "column": 5,
#     "code": "E501",
#     "text": "line too long"
#   }
# ]
```

**Severity Mapping**:
- `E*` (errors) → HIGH
- `W*` (warnings) → MEDIUM
- `F*` (flakes) → HIGH
- `C*` (complexity) → MEDIUM

**Error Codes**:
- E501: line too long
- E302: expected 2 blank lines
- W291: trailing whitespace
- F401: imported but unused
- C901: too complex

### 3. Pylint Code Quality

```bash
# Run pylint with JSON output
pylint coffee_maker/ --max-line-length=120 --exit-zero --output-format=json 2>&1

# JSON Output Format:
# [
#   {
#     "type": "convention",
#     "module": "module_name",
#     "obj": "function_name",
#     "line": 42,
#     "column": 0,
#     "message": "Missing docstring",
#     "message-id": "C0111"
#   }
# ]
```

**Severity Mapping**:
- `error` → HIGH (runtime issues)
- `fatal` → CRITICAL (syntax errors)
- `warning` → MEDIUM (potential issues)
- `convention` → LOW (style conventions)
- `refactor` → LOW (code improvement suggestions)

**Key Checks**:
- C0111: Missing docstring
- W0613: Unused argument
- R0913: Too many arguments
- R0914: Too many local variables

## Success Criteria

- ✅ Detects Black formatting issues (reformat needed)
- ✅ Parses flake8 violations with line numbers
- ✅ Extracts pylint issues with severity levels
- ✅ Maps all issues to appropriate severity
- ✅ Creates review_issue records for each finding
- ✅ Provides actionable recommendations
- ✅ Handles tool failures gracefully
- ✅ Completes in <30 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "analysis_duration_seconds": 18.3,
  "style_compliance": {
    "black_compliant": false,
    "flake8_status": "found_issues",
    "pylint_score": 8.2,
    "total_issues": 8
  },
  "black_findings": {
    "issues_found": 2,
    "auto_fixable": 2,
    "files_affected": ["coffee_maker/auth.py", "tests/test_auth.py"]
  },
  "flake8_findings": {
    "issues_found": 3,
    "by_severity": {
      "E": 1,
      "W": 2,
      "F": 0
    }
  },
  "pylint_findings": {
    "issues_found": 3,
    "by_type": {
      "error": 0,
      "warning": 1,
      "convention": 2
    }
  },
  "issues": [
    {
      "id": "ISS-1",
      "severity": "HIGH",
      "category": "Style",
      "file_path": "coffee_maker/auth.py",
      "line_number": 42,
      "code": "E501",
      "description": "Line too long (125 > 120 characters)",
      "recommendation": "Break line into multiple lines or reduce length",
      "auto_fixable": false
    },
    {
      "id": "ISS-2",
      "severity": "HIGH",
      "category": "Style",
      "file_path": "coffee_maker/auth.py",
      "line_number": null,
      "code": "black",
      "description": "Black formatting would change code",
      "recommendation": "Run `black coffee_maker/auth.py` to auto-fix",
      "auto_fixable": true
    }
  ],
  "summary": {
    "total_style_issues": 8,
    "auto_fixable_count": 2,
    "requires_manual_fix": 6,
    "estimated_fix_time": "2 hours"
  }
}
```

## Error Handling

**Tool Not Found**:
```json
{
  "status": "warning",
  "error": "Tool not found: flake8",
  "installed_tools": ["black", "pylint"],
  "missing_tools": ["flake8"],
  "note": "Install with: pip install flake8"
}
```

**Tool Execution Error**:
```json
{
  "status": "partial_success",
  "tool": "pylint",
  "error": "Syntax error in analyzed file",
  "completed_tools": ["black", "flake8"],
  "failed_tools": ["pylint"],
  "issues_found": 3
}
```

## Examples

### Example 1: Full style check

```bash
code_reviewer.check_style_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_black=true,
  check_flake8=true,
  check_pylint=true
)
```

### Example 2: Auto-fixable only

```bash
code_reviewer.check_style_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  auto_fixable_only=true
)
```

### Example 3: Black only

```bash
code_reviewer.check_style_compliance(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  check_black=true,
  check_flake8=false,
  check_pylint=false
)
```

## Implementation Notes

- Max line length: 120 characters (per project standards)
- Black must run with default Black settings
- Flake8 must use pylint-style output for consistency
- Pylint should exclude certain rules (W0613 for callbacks, C0114 for modules)
- Report issues per-file for easier navigation
- Auto-fixable issues can be marked for automatic correction
- Store issue code (E501, C0111, etc.) for tracking
- Consider severity when ranking issues

## Recommendations for Fixes

**Black Issues**: Run `black {file}` to auto-fix all formatting

**Line Too Long (E501)**:
```python
# Before
some_function(very_long_argument_1, very_long_argument_2, very_long_argument_3)

# After
some_function(
    very_long_argument_1,
    very_long_argument_2,
    very_long_argument_3
)
```

**Missing Docstring**:
```python
# Before
def my_function(x):
    return x * 2

# After
def my_function(x: int) -> int:
    """Multiply input by 2.

    Args:
        x: Integer to multiply

    Returns:
        int: Result of x * 2
    """
    return x * 2
```

## Related Commands

- `code_reviewer.generate_review_report` - Main review orchestrator
- `code_reviewer.validate_type_hints` - Check type hint compliance
- `code_reviewer.review_documentation` - Check docstring completeness

---

**Version**: 1.0
**Last Updated**: 2025-10-26
