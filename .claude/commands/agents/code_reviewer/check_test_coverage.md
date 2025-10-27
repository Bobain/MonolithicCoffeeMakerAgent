---
command: code_reviewer.check_test_coverage
agent: code_reviewer
action: check_test_coverage
tables:
  write: [review_issue]
  read: [review_code_review, review_commit]
required_tools: [pytest, coverage]
estimated_duration_seconds: 60
---

# Command: code_reviewer.check_test_coverage

## Purpose

Run pytest with coverage to verify test coverage meets project standards (>90%). This command ensures adequate testing of all code changes and identifies untested code paths.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to check
review_id: string               # Required - link issues to review
minimum_coverage: number        # Minimum required (default: 90)
critical_minimum: number        # Critical threshold (default: 80)
run_tests: boolean              # Run tests (default: true)
report_html: boolean            # Generate HTML report (default: true)
check_branch_coverage: boolean  # Check branch coverage (default: true)
new_code_only: boolean          # Check only new code (default: false)
include_slow_tests: boolean     # Include slow tests (default: false)
```

## Database Operations

**Query: Insert coverage issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, 'Testing', ?, ?, ?, ?, datetime('now'));
```

## External Tools

### Run Tests with Coverage

```bash
# Run pytest with coverage tracking
pytest tests/ --cov=coffee_maker --cov-report=json --cov-report=html --cov-report=term 2>&1

# Output includes:
# tests/unit/test_auth.py::test_login PASSED
# tests/integration/test_workflow.py::test_full_workflow PASSED
# ...
# ============ 145 passed, 0 failed in 42.3s ============
# TOTAL: 92.3%
```

### Parse Coverage JSON

```bash
# Coverage JSON location: coverage.json
# Contains per-file and per-line coverage data

python3 << 'EOF'
import json
with open("coverage.json") as f:
    cov = json.load(f)
    total = cov["totals"]["percent_covered"]
    branch = cov["totals"]["percent_covered_lines"]
    print(f"Total: {total:.1f}%")
    print(f"Branch: {branch:.1f}%")
EOF
```

### Coverage Report Analysis

```bash
# Generate coverage report
coverage report --skip-covered

# Output format:
# Name                           Stmts   Miss  Cover   Missing
# ─────────────────────────────────────────────────────────────
# coffee_maker/__init__.py           2      0   100%
# coffee_maker/auth.py              45      3    93%   42, 48, 52
# coffee_maker/db.py                78      5    94%   102, 110, 115-120
# ─────────────────────────────────────────────────────────────
# TOTAL                            567     11    98%
```

## Success Criteria

- ✅ Runs entire test suite without errors
- ✅ Parses coverage JSON output correctly
- ✅ Calculates line and branch coverage percentages
- ✅ Identifies uncovered lines per file
- ✅ Creates review_issue for coverage below threshold
- ✅ Tracks coverage trends (increasing/decreasing)
- ✅ Generates HTML report for review
- ✅ Completes in <60 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "test_duration_seconds": 42.3,
  "coverage_summary": {
    "total_coverage": 92.3,
    "line_coverage": 91.5,
    "branch_coverage": 88.2,
    "coverage_status": "GOOD"
  },
  "test_results": {
    "passed": 145,
    "failed": 0,
    "skipped": 2,
    "errors": 0,
    "total_tests": 147,
    "success_rate": 98.6
  },
  "coverage_by_component": {
    "coffee_maker": 92.3,
    "coffee_maker/autonomous": 88.5,
    "coffee_maker/cli": 95.2,
    "tests": 100.0
  },
  "uncovered_files": [
    {
      "file_path": "coffee_maker/db.py",
      "coverage": 89.5,
      "uncovered_lines": 5,
      "lines": [102, 110, 115, 120, 125],
      "issue_severity": "MEDIUM"
    },
    {
      "file_path": "coffee_maker/api.py",
      "coverage": 85.2,
      "uncovered_lines": 12,
      "lines": [42, 48, 52, 60, 68, 75, 82, 89, 96, 103, 110, 117],
      "issue_severity": "HIGH"
    }
  ],
  "issues": [
    {
      "id": "ISS-1",
      "severity": "HIGH",
      "category": "Testing",
      "file_path": "coffee_maker/api.py",
      "line_number": null,
      "description": "Test coverage for coffee_maker/api.py is 85.2% (below 90% threshold)",
      "recommendation": "Add tests for error handling and edge cases",
      "uncovered_count": 12
    }
  ],
  "coverage_trend": {
    "previous_coverage": 91.5,
    "current_coverage": 92.3,
    "change": "+0.8%",
    "trend": "improving"
  },
  "report_files": {
    "html_report": "htmlcov/index.html",
    "json_report": "coverage.json"
  }
}
```

## Coverage Rating System

| Coverage % | Rating | Status |
|-----------|--------|--------|
| 95-100 | A | Excellent - highly tested |
| 90-94 | B | Good - acceptable |
| 85-89 | C | Fair - needs improvement |
| 80-84 | D | Poor - significant gaps |
| <80 | F | Critical - needs major work |

## Error Handling

**All Tests Pass with Good Coverage**:
```json
{
  "status": "success",
  "coverage_summary": {
    "total_coverage": 95.2,
    "coverage_status": "EXCELLENT"
  },
  "test_results": {
    "passed": 150,
    "failed": 0
  },
  "message": "All tests passing - excellent coverage"
}
```

**Test Failures**:
```json
{
  "status": "failure",
  "error_type": "TEST_FAILURE",
  "test_results": {
    "passed": 140,
    "failed": 3,
    "failed_tests": [
      "tests/test_auth.py::test_login_invalid",
      "tests/test_db.py::test_connection_timeout",
      "tests/test_api.py::test_error_handling"
    ]
  },
  "note": "Fix failing tests before merging"
}
```

**Coverage Below Critical**:
```json
{
  "status": "success",
  "coverage_summary": {
    "total_coverage": 78.5,
    "coverage_status": "CRITICAL"
  },
  "issues": [
    {
      "severity": "CRITICAL",
      "description": "Coverage of 78.5% is below critical minimum of 80%"
    }
  ]
}
```

## Examples

### Example 1: Full coverage check

```bash
code_reviewer.check_test_coverage(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  minimum_coverage=90,
  run_tests=true,
  report_html=true
)
```

### Example 2: Quick coverage check (no HTML)

```bash
code_reviewer.check_test_coverage(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  minimum_coverage=85,
  report_html=false
)
```

### Example 3: New code only

```bash
code_reviewer.check_test_coverage(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  new_code_only=true,
  minimum_coverage=95  # Higher threshold for new code
)
```

## Implementation Notes

- Project standard is 90% minimum coverage
- Critical threshold is 80% (blocks merge if below)
- Always run full test suite (not just unit tests)
- Include integration tests in coverage
- Track coverage trends across commits
- Identify specific uncovered lines for targeted testing
- Generate HTML reports for detailed review
- Consider code complexity when setting thresholds

## Coverage Improvement Strategies

### Strategy 1: Test Missing Branches

**Uncovered Code**:
```python
def authenticate(username, password):
    if not username:
        raise ValueError("Username required")  # Branch never tested

    if not password:
        raise ValueError("Password required")  # Branch never tested

    return validate_credentials(username, password)
```

**Tests Needed**:
```python
def test_authenticate_missing_username():
    with pytest.raises(ValueError, match="Username required"):
        authenticate("", "password")

def test_authenticate_missing_password():
    with pytest.raises(ValueError, match="Password required"):
        authenticate("user", "")

def test_authenticate_valid():
    result = authenticate("user", "password")
    assert result is True
```

### Strategy 2: Error Handling Tests

**Pattern**:
```python
def test_function_error_handling():
    with pytest.raises(SpecificException):
        function_that_errors()

    # Verify error message
    with pytest.raises(SpecificException, match="error pattern"):
        function_that_errors()
```

### Strategy 3: Edge Cases

**Pattern**:
```python
@pytest.mark.parametrize("input,expected", [
    (None, None),
    ("", ""),
    (0, 0),
    (-1, "error"),
    (999999, "success"),
])
def test_edge_cases(input, expected):
    assert process(input) == expected
```

## Related Commands

- `code_reviewer.generate_review_report` - Main review orchestrator
- `code_reviewer.check_style_compliance` - Code quality checks
- `code_reviewer.validate_dod_compliance` - Verify acceptance criteria

---

**Version**: 1.0
**Last Updated**: 2025-10-26
