# test

## Purpose
Run pytest test suite with coverage tracking, auto-retry on failures up to 3 times, record execution metrics.

## Parameters
```yaml
test_suite: str = None  # Specific test path, None = all tests
auto_retry: bool = true  # Retry failures up to 3 times
coverage_required: float = 0.90  # Minimum coverage (0.0-1.0)
verbose: bool = false  # Detailed test output
```

## Workflow
1. Run pytest with coverage plugin
2. Parse test results (passed/failed/skipped)
3. If failures and auto_retry: retry up to 3 times
4. Calculate coverage percentage
5. Record execution in database
6. Return TestResult with metrics

## Database Insert
```sql
-- Record test execution
INSERT INTO test_execution (
    execution_id, task_id, test_command, total_tests,
    passed, failed, skipped, duration_seconds,
    coverage_percentage, output, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
```

## Result Object
```python
@dataclass
class TestResult:
    total: int  # Total tests run
    passed: int  # Tests passed
    failed: int  # Tests failed
    skipped: int  # Tests skipped
    coverage: float  # Coverage 0.0-1.0
    duration_seconds: float
    status: str  # "success" | "partial" | "failed"
    failed_tests: List[str]  # Names of failed tests
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| PytestNotFound | pytest not installed | Install: poetry add --dev pytest |
| TestsFailed | Code errors | Review failed test output |
| CoverageLow | < coverage_required | Add more tests or review threshold |
| TimeoutError | Tests hung | Check for infinite loops, add timeout |

## Example
```python
result = test(auto_retry=True)
# TestResult(
#   total=150, passed=150, failed=0, skipped=0,
#   coverage=0.953, duration_seconds=12.3,
#   status="success", failed_tests=[]
# )
```

## Retry Logic
Attempt 1 → Fail → Wait 2s → Attempt 2 → Fail → Wait 4s → Attempt 3

## Related Commands
- implement() - Generate code before testing
- finalize() - Quality checks after tests pass

---
Estimated: 55 lines | Context: ~3.5% | Examples: test_examples.md
