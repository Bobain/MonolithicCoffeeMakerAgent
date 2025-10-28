# test

## Purpose
Run pytest with coverage, auto-retry failed tests up to 3 times, record test metrics in database, ensure ≥90% coverage.

## Parameters
```yaml
target: str = "."  # Test path (file, directory, or "." for all)
coverage: bool = true  # Generate coverage report
retry_count: int = 3  # Auto-retry failed tests
fail_under: int = 90  # Minimum coverage percentage
verbose: bool = false  # Detailed test output
```

## Workflow
1. Identify tests to run (path resolution)
2. Execute pytest with coverage
3. If tests fail and retry_count > 0, retry
4. Calculate coverage percentage
5. Validate coverage ≥ fail_under threshold
6. Record test metrics in database
7. Return TestResult with pass/fail status

## Pytest Integration (EMBEDDED - Essential Commands)

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific directory
pytest tests/unit/

# Run specific file
pytest tests/unit/test_auth.py

# Run specific test
pytest tests/unit/test_auth.py::test_oauth2_flow
```

### Coverage Collection
```bash
# Run with coverage
pytest --cov=coffee_maker --cov-report=term-missing

# Save coverage report
pytest --cov=coffee_maker --cov-report=html --cov-report=term

# Fail if coverage below threshold
pytest --cov=coffee_maker --cov-fail-under=90
```

### Test Output Control
```bash
# Verbose output (show all test names)
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Quiet mode (minimal output)
pytest -q
```

### Retry Logic (EMBEDDED)
```python
# Pseudo-code for retry mechanism
for attempt in range(1, retry_count + 1):
    result = run_pytest(target, coverage=coverage)

    if result.passed:
        return result  # Success

    if attempt < retry_count:
        logger.warning(f"Tests failed, retrying ({attempt}/{retry_count})...")
        time.sleep(2)  # Brief delay before retry

# All retries exhausted
return result  # Final failure
```

### Coverage Threshold Validation
```python
# Check coverage meets threshold
if coverage_pct < fail_under:
    raise CoverageError(
        f"Coverage {coverage_pct}% is below threshold {fail_under}%. "
        f"Add tests for uncovered code."
    )
```

## Database Operations
```sql
-- Record test execution
INSERT INTO test_execution_log (
    execution_id, target, tests_run, tests_passed,
    tests_failed, coverage_pct, duration_seconds,
    retry_count, timestamp
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))

-- Track coverage trends
INSERT INTO coverage_history (
    coverage_id, timestamp, coverage_pct, lines_covered,
    lines_total, execution_id
) VALUES (?, datetime('now'), ?, ?, ?, ?)
```

## Result Object
```python
@dataclass
class TestResult:
    tests_run: int
    tests_passed: int
    tests_failed: int
    coverage_pct: float  # 0.0-100.0
    duration_seconds: float
    retry_attempts: int  # How many retries were needed
    status: str  # "pass" | "fail" | "coverage_fail"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| TestsNotFound | No tests match target | Check path exists, verify test file naming |
| CoverageToolMissing | pytest-cov not installed | Install: poetry add --dev pytest-cov |
| TestExecutionTimeout | Tests hung/timeout | Reduce scope or increase timeout limit |
| CoverageFailure | Coverage below threshold | Add tests for uncovered code paths |
| PytestError | Syntax/import errors | Fix test code errors before retry |

## Example
```python
result = test(
    target="tests/unit/",
    coverage=True,
    retry_count=3,
    fail_under=90
)
# TestResult(
#   tests_run=45,
#   tests_passed=45,
#   tests_failed=0,
#   coverage_pct=94.2,
#   duration_seconds=12.5,
#   retry_attempts=0,
#   status="pass"
# )
```

## Common Test Patterns

### Unit Test Structure
```python
def test_feature_name():
    # Arrange: Set up test data
    user = create_test_user()

    # Act: Execute code under test
    result = authenticate_user(user)

    # Assert: Verify expected outcome
    assert result.is_authenticated
    assert result.user_id == user.id
```

### Fixture Usage
```python
@pytest.fixture
def db_session():
    """Provide test database session."""
    session = create_test_session()
    yield session
    session.close()
```

## Related Commands
- implement() - Create implementation before testing
- finalize() - Run final quality checks

---
Estimated: 120 lines | Context: 7.5% | Self-contained: Yes ✅
