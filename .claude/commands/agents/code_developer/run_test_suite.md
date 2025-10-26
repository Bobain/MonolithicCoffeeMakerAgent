---
command: code_developer.run_test_suite
agent: code_developer
action: run_test_suite
tables:
  write: [metrics_subtask, system_audit]
  read: []
required_skills: []
required_tools: [database, pytest]
---

# Command: code_developer.run_test_suite

## Purpose
Execute pytest with coverage reporting and record metrics to database.

## Input Parameters

```yaml
test_path: string        # Optional - Specific test file/directory (default: "tests/")
coverage_threshold: integer # Minimum coverage required (default: 90)
markers: array           # Optional - pytest markers to run
fail_fast: boolean       # Stop on first failure (default: false)
verbose: boolean         # Verbose output (default: false)
```

## Database Operations

### 1. Build Pytest Command
```python
import subprocess
import time
import json
import os
from datetime import datetime

def run_test_suite(db: DomainWrapper, params: dict):
    test_path = params.get("test_path", "tests/")
    coverage_threshold = params.get("coverage_threshold", 90)

    # Build pytest command
    cmd = [
        "pytest",
        test_path,
        "--cov=coffee_maker",
        "--cov-report=json",
        "--cov-report=term",
        "-q"  # Quiet by default
    ]

    if params.get("verbose", False):
        cmd.extend(["-vv"])
    else:
        cmd.append("-q")

    if params.get("markers"):
        marker_expr = " and ".join(params["markers"])
        cmd.extend(["-m", marker_expr])

    if params.get("fail_fast", False):
        cmd.append("-x")
```

### 2. Execute Tests
```python
    # Run tests and measure time
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time

    tests_passed = result.returncode == 0
```

### 3. Parse Coverage
```python
    # Read coverage.json for detailed stats
    coverage = 0
    coverage_data = None

    try:
        if os.path.exists("coverage.json"):
            with open("coverage.json") as f:
                coverage_data = json.load(f)
                coverage = round(coverage_data["totals"]["percent_covered"], 2)
    except Exception as e:
        coverage = 0
        result.stderr += f"\nFailed to parse coverage: {e}"
```

### 4. Parse Test Counts
```python
    # Parse test results from output
    output = result.stdout + result.stderr

    # Extract counts using regex or pytest json report
    tests_run = 0
    tests_passed_count = 0
    tests_failed = 0
    tests_skipped = 0
    failed_tests = []

    # Simple parsing (would be enhanced with pytest plugin)
    if " passed" in output:
        try:
            # Extract from "123 passed in 1.23s"
            import re
            match = re.search(r"(\d+) passed", output)
            if match:
                tests_passed_count = int(match.group(1))
                tests_run += tests_passed_count
        except:
            pass

    if " failed" in output:
        try:
            match = re.search(r"(\d+) failed", output)
            if match:
                tests_failed = int(match.group(1))
                tests_run += tests_failed
                failed_tests.append({"test_name": "See output", "error": output[:500]})
        except:
            pass

    if " skipped" in output:
        try:
            match = re.search(r"(\d+) skipped", output)
            if match:
                tests_skipped = int(match.group(1))
                tests_run += tests_skipped
        except:
            pass
```

### 5. Record Metrics
```python
    # Store test results in metrics table
    metrics_data = {
        "metric_type": "test_run",
        "test_path": test_path,
        "tests_run": tests_run,
        "tests_passed": tests_passed_count,
        "tests_failed": tests_failed,
        "tests_skipped": tests_skipped,
        "coverage": coverage,
        "coverage_threshold": coverage_threshold,
        "duration_seconds": round(duration, 2),
        "recorded_by": "code_developer",
        "recorded_at": datetime.now().isoformat(),
        "test_output": output[:500] if not tests_passed else ""
    }

    metric_id = db.write("metrics_subtask", metrics_data, action="create")
```

### 6. Create Audit Trail
```python
    db.write("system_audit", {
        "table_name": "metrics_subtask",
        "item_id": metric_id,
        "action": "create",
        "field_changed": "metric_type",
        "new_value": "test_run",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": tests_passed and coverage >= coverage_threshold,
        "tests_run": tests_run,
        "tests_passed": tests_passed_count,
        "tests_failed": tests_failed,
        "tests_skipped": tests_skipped,
        "coverage": coverage,
        "coverage_threshold": coverage_threshold,
        "duration_seconds": round(duration, 2),
        "failed_tests": failed_tests,
        "metric_id": metric_id
    }
```

## Output

```json
{
  "success": true,
  "tests_run": 156,
  "tests_passed": 155,
  "tests_failed": 1,
  "tests_skipped": 0,
  "coverage": 92,
  "coverage_threshold": 90,
  "duration_seconds": 12.5,
  "failed_tests": [
    {
      "test_name": "test_authentication",
      "error": "AssertionError: Expected 200, got 401"
    }
  ]
}
```

## Success Criteria

- ✅ Tests executed
- ✅ Coverage calculated and stored
- ✅ Results recorded in database
- ✅ Failed tests identified
- ✅ Metrics tracked for trend analysis

## Test Markers

Run specific test categories:

```python
# Run only integration tests
run_test_suite(db, {
    "markers": ["integration"]
})

# Skip slow tests
run_test_suite(db, {
    "markers": ["not slow"]
})

# Run security tests only
run_test_suite(db, {
    "markers": ["security"]
})
```

## Coverage Thresholds

```python
# Require 95% coverage
run_test_suite(db, {
    "coverage_threshold": 95
})

# Minimum 85% coverage
run_test_suite(db, {
    "coverage_threshold": 85
})
```

## Fail Fast Mode

```python
# Stop on first failure
run_test_suite(db, {
    "fail_fast": True
})
```

## Bash Equivalent

```bash
# Run all tests with coverage
pytest --cov=coffee_maker --cov-report=json --cov-report=term

# Run specific test file
pytest tests/test_auth.py --cov=coffee_maker

# Run with markers
pytest -m "not slow" --cov=coffee_maker

# Stop on first failure
pytest -x --cov=coffee_maker

# Verbose output
pytest -vv --cov=coffee_maker
```

## Integration with Code Developer Workflow

After running tests:
1. Check `success` flag
2. If false: Call `fix_failing_tests` to debug
3. If true and coverage >= threshold: Mark task complete
4. If true but coverage low: Add more tests

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| TestExecutionError | Pytest failed to run | Check pytest installation |
| CoverageParseFailed | Coverage report invalid | Check pytest-cov |
| InvalidMarkerError | Unknown pytest marker | Check marker names |
| PathNotFoundError | Test path invalid | Verify test directory |

## Coverage Targets by Module

Different modules may have different coverage targets:

```
coffee_maker/models/     → 95% (business logic)
coffee_maker/api/        → 90% (endpoints)
coffee_maker/utils/      → 85% (utilities)
coffee_maker/cli/        → 80% (CLI commands)
```

Default: 90% for all modules (can be overridden per task)
