---
command: code_developer.fix_failing_tests
agent: code_developer
action: fix_failing_tests
tables:
  write: [system_audit]
  read: [metrics_subtask]
required_skills: [code_forensics]
required_tools: [database, pytest]
---

# Command: code_developer.fix_failing_tests

## Purpose
Analyze and fix failing tests identified by test suite, with optional automatic fixes.

## Input Parameters

```yaml
test_name: string        # Optional - Specific test to fix (or analyze all failures)
auto_fix: boolean        # Attempt automatic fix (default: false)
analyze_only: boolean    # Only analyze, don't fix (default: false)
max_attempts: integer    # Max fix attempts (default: 3)
```

## Database Operations

### 1. Get Latest Test Failures
```python
from datetime import datetime
import subprocess
import json

def fix_failing_tests(db: DomainWrapper, params: dict):
    # Get latest test metrics from database
    metrics = db.read("metrics_subtask", {
        "metric_type": "test_run"
    }, sort_by="recorded_at", limit=1)

    if not metrics or metrics[0]["tests_failed"] == 0:
        return {
            "success": True,
            "message": "No failing tests",
            "tests_analyzed": 0
        }

    latest_test_run = metrics[0]
```

### 2. Run Tests to Get Failures
```python
    # Run tests again to capture failure details
    result = subprocess.run(
        ["pytest", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )

    test_output = result.stdout + result.stderr

    # Parse failures from output
    import re
    failure_pattern = r"(test_\w+.*?) (FAILED|ERROR)(.*?)(?=test_|$)"
    failures = re.findall(failure_pattern, test_output, re.DOTALL)

    issues_found = []
    for test_name, status, error_msg in failures:
        issue = {
            "test_name": test_name.strip(),
            "error_type": status,
            "error_message": error_msg.strip()[:200],
            "root_cause": "Analyzing...",
            "suggested_fix": "",
            "auto_fixed": False
        }
        issues_found.append(issue)
```

### 3. Analyze Root Causes
```python
    # Analyze each failure
    for issue in issues_found:
        error_msg = issue["error_message"]

        # Common error patterns and fixes
        if "AssertionError" in error_msg:
            issue["root_cause"] = "Assertion failed - logic error or wrong expected value"
            issue["suggested_fix"] = "Review assertion logic"

        elif "AttributeError" in error_msg:
            issue["root_cause"] = "Missing or renamed attribute"
            issue["suggested_fix"] = "Check attribute names match actual implementation"

        elif "ImportError" in error_msg:
            issue["root_cause"] = "Missing import or module not found"
            issue["suggested_fix"] = "Add missing import statement"

        elif "TypeError" in error_msg:
            issue["root_cause"] = "Wrong argument type or missing required argument"
            issue["suggested_fix"] = "Check function signature and call arguments"

        elif "KeyError" in error_msg:
            issue["root_cause"] = "Dictionary key not found"
            issue["suggested_fix"] = "Verify dictionary keys match data structure"

        elif "IndexError" in error_msg:
            issue["root_cause"] = "List index out of range"
            issue["suggested_fix"] = "Check list bounds before accessing"

        elif "database" in error_msg.lower():
            issue["root_cause"] = "Database connection or query error"
            issue["suggested_fix"] = "Check database setup in test fixtures"

        elif "mock" in error_msg.lower():
            issue["root_cause"] = "Mock setup or patch issue"
            issue["suggested_fix"] = "Verify mock.patch targets are correct"

        else:
            issue["root_cause"] = "Unknown error type - manual analysis needed"
            issue["suggested_fix"] = "Review error message and test code"
```

### 4. Attempt Auto-Fix (Optional)
```python
    fixes_applied = 0

    if params.get("auto_fix", False) and not params.get("analyze_only", False):
        for issue in issues_found:
            if issue["error_type"] == "FAILED":
                # Attempt automatic fixes based on pattern
                success = False

                if "ImportError" in issue["error_message"]:
                    # Try to fix import errors automatically
                    success = attempt_fix_import(issue["test_name"])

                elif "AttributeError" in issue["error_message"]:
                    # Try to fix attribute errors
                    success = attempt_fix_attribute(issue["test_name"])

                if success:
                    issue["auto_fixed"] = True
                    fixes_applied += 1

        # Re-run tests after fixes
        result = subprocess.run(
            ["pytest", "--tb=short"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return {
                "success": True,
                "tests_analyzed": len(issues_found),
                "issues_found": issues_found,
                "fixes_applied": fixes_applied,
                "tests_now_passing": True
            }
```

### 5. Record Analysis
```python
    # Store analysis in audit trail
    db.write("system_audit", {
        "table_name": "test_failures",
        "item_id": f"analysis-{datetime.now().isoformat()}",
        "action": "analyzed",
        "field_changed": "failures",
        "new_value": json.dumps(issues_found),
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat()
    }, action="create")

    return {
        "success": True,
        "tests_analyzed": len(issues_found),
        "issues_found": issues_found,
        "fixes_applied": fixes_applied,
        "analyze_only": params.get("analyze_only", False)
    }
```

## Output

```json
{
  "success": true,
  "tests_analyzed": 3,
  "issues_found": [
    {
      "test_name": "test_authentication",
      "error_type": "FAILED",
      "root_cause": "Missing token validation",
      "suggested_fix": "Add token validation in auth middleware",
      "auto_fixed": false
    },
    {
      "test_name": "test_database_connection",
      "error_type": "FAILED",
      "root_cause": "Database connection error",
      "suggested_fix": "Check database setup in test fixtures",
      "auto_fixed": true
    }
  ],
  "fixes_applied": 1
}
```

## Success Criteria

- ✅ Failing tests identified
- ✅ Root causes analyzed
- ✅ Fixes suggested
- ✅ Auto-fix applied (if enabled)
- ✅ Analysis recorded in audit trail

## Analyze-Only Mode

Just get analysis without fixing:

```python
fix_failing_tests(db, {
    "analyze_only": True
})
# Returns issues_found with suggested_fixes
```

## Auto-Fix Mode

Let code_developer attempt automatic fixes:

```python
fix_failing_tests(db, {
    "auto_fix": True
})
# Attempts fixes and reruns tests
```

## Specific Test Analysis

Analyze just one failing test:

```python
fix_failing_tests(db, {
    "test_name": "test_authentication",
    "analyze_only": True
})
```

## Common Error Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| AssertionError | Wrong expected value | Update assertion |
| ImportError | Missing module | Add import statement |
| AttributeError | Renamed attribute | Update attribute name |
| TypeError | Wrong argument type | Fix function call |
| KeyError | Missing dict key | Check data structure |
| IndexError | Array out of bounds | Add bounds check |

## Workflow

```
1. run_test_suite reports failures
2. code_developer calls fix_failing_tests
3. Failures analyzed and categorized
4. Suggested fixes provided to developer
5. code_developer reviews and applies fixes
6. run_test_suite called again
7. If all pass: complete implementation
8. If still failing: manual intervention needed
```

## Integration with Run Test Suite

After `run_test_suite` returns failures:

```python
# Get test results
test_results = run_test_suite(db, {"test_path": "tests/"})

if not test_results["success"]:
    # Analyze failures
    analysis = fix_failing_tests(db, {
        "analyze_only": True
    })

    # Review issues_found and apply fixes
    for issue in analysis["issues_found"]:
        print(f"Test: {issue['test_name']}")
        print(f"Root Cause: {issue['root_cause']}")
        print(f"Suggested Fix: {issue['suggested_fix']}")

    # Retry tests
    test_results = run_test_suite(db, {"test_path": "tests/"})
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| NoFailuresError | No test failures found | Skip command |
| AnalysisFailedError | Failed to parse test output | Manual review needed |
| AutoFixFailedError | Automatic fix didn't work | Manual fix required |
