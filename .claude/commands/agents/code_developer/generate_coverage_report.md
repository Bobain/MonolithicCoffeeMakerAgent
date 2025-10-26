---
command: code_developer.generate_coverage_report
agent: code_developer
action: generate_coverage_report
tables:
  write: [system_audit]
  read: []
required_skills: []
required_tools: [database, pytest, coverage]
---

# Command: code_developer.generate_coverage_report

## Purpose
Generate detailed test coverage report in multiple formats and identify coverage gaps.

## Input Parameters

```yaml
output_format: string    # "html", "json", "xml", "term", "term-missing" (default: "html")
output_path: string      # Output directory/file (default: "htmlcov/" or "coverage.json")
show_missing: boolean    # Show uncovered lines (default: true)
min_coverage: integer    # Fail if below this % (default: 0, no minimum)
include_modules: array   # Optional - specific modules to cover
```

## Database Operations

### 1. Build Coverage Command
```python
import subprocess
import json
import os
from datetime import datetime

def generate_coverage_report(db: DomainWrapper, params: dict):
    output_format = params.get("output_format", "html")
    output_path = params.get("output_path")

    # Determine output path based on format
    if not output_path:
        if output_format == "html":
            output_path = "htmlcov"
        elif output_format == "json":
            output_path = "coverage.json"
        elif output_format == "xml":
            output_path = "coverage.xml"
        else:
            output_path = None

    # Build pytest command with coverage
    cmd = ["pytest", "--cov=coffee_maker"]

    # Add coverage report format
    if output_format == "html":
        cmd.append("--cov-report=html")
    elif output_format == "json":
        cmd.append("--cov-report=json")
    elif output_format == "xml":
        cmd.append("--cov-report=xml")
    elif output_format == "term":
        cmd.append("--cov-report=term")
    elif output_format == "term-missing":
        cmd.append("--cov-report=term-missing")

    # Optional: Show term output alongside other formats
    if output_format != "term":
        cmd.append("--cov-report=term-missing")

    # Include specific modules if provided
    if params.get("include_modules"):
        for module in params["include_modules"]:
            cmd.append(f"--cov={module}")
```

### 2. Execute Coverage Report
```python
    # Run pytest with coverage
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr

    success = result.returncode == 0
```

### 3. Parse Coverage Data
```python
    # Parse coverage JSON for statistics
    coverage_data = {}
    overall_coverage = 0

    if output_format == "json" or os.path.exists("coverage.json"):
        try:
            with open("coverage.json") as f:
                coverage_json = json.load(f)
                overall_coverage = round(
                    coverage_json["totals"]["percent_covered"], 2
                )
                coverage_data = coverage_json
        except Exception as e:
            output += f"\nFailed to parse coverage.json: {e}"

    # Extract module coverage from output
    import re
    module_pattern = r"([\w/\.]+\.py)\s+(\d+)\s+(\d+)\s+(\d+%)"
    module_matches = re.findall(module_pattern, output)

    modules_analyzed = len(module_matches)
    modules_below_threshold = 0

    # Check threshold
    if params.get("min_coverage", 0) > 0:
        if overall_coverage < params.get("min_coverage"):
            modules_below_threshold = 1  # Mark as failing

    # Calculate uncovered lines
    uncovered_lines = 0
    if coverage_data and "totals" in coverage_data:
        covered = coverage_data["totals"].get("covered_lines", 0)
        num_statements = coverage_data["totals"].get("num_statements", 0)
        uncovered_lines = max(0, num_statements - covered)
```

### 4. Generate Report Files
```python
    # Report generation happens via pytest (above)
    # Just need to handle output path

    report_file = None
    if output_format == "html" and os.path.isdir(output_path or "htmlcov"):
        report_file = os.path.join(output_path or "htmlcov", "index.html")
    elif output_format == "json" and os.path.exists(output_path or "coverage.json"):
        report_file = output_path or "coverage.json"
    elif output_format == "xml" and os.path.exists(output_path or "coverage.xml"):
        report_file = output_path or "coverage.xml"
```

### 5. Audit Coverage Report
```python
    # Create audit record of coverage run
    db.write("system_audit", {
        "table_name": "coverage_reports",
        "item_id": f"coverage-{datetime.now().isoformat()}",
        "action": "generated",
        "field_changed": "coverage",
        "new_value": f"{overall_coverage}%",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat(),
        "metadata": json.dumps({
            "format": output_format,
            "overall_coverage": overall_coverage,
            "modules_analyzed": modules_analyzed,
            "uncovered_lines": uncovered_lines,
            "report_file": report_file
        })
    }, action="create")

    return {
        "success": success and (params.get("min_coverage", 0) <= overall_coverage),
        "coverage": overall_coverage,
        "output_format": output_format,
        "output_path": report_file or output_path,
        "uncovered_lines": uncovered_lines,
        "modules_analyzed": modules_analyzed,
        "modules_below_threshold": modules_below_threshold,
        "test_passed": success
    }
```

## Output

```json
{
  "success": true,
  "coverage": 92,
  "output_format": "html",
  "output_path": "htmlcov/index.html",
  "uncovered_lines": 145,
  "modules_analyzed": 42,
  "modules_below_threshold": 2
}
```

## Success Criteria

- ✅ Coverage report generated
- ✅ Missing lines identified
- ✅ Report accessible (files created)
- ✅ Threshold violations flagged (if min_coverage set)
- ✅ Multiple format support

## Report Formats

### HTML Report (Most Popular)
```python
generate_coverage_report(db, {
    "output_format": "html",
    "show_missing": True
})
# Creates htmlcov/index.html with interactive coverage view
```

### JSON Report (Programmatic)
```python
generate_coverage_report(db, {
    "output_format": "json"
})
# Creates coverage.json for parsing and analysis
```

### Terminal Report (Quick View)
```python
generate_coverage_report(db, {
    "output_format": "term-missing"
})
# Prints coverage to console with missing line numbers
```

### XML Report (CI Integration)
```python
generate_coverage_report(db, {
    "output_format": "xml"
})
# Creates coverage.xml for CI systems like Jenkins
```

## Viewing Coverage Reports

### HTML Report
Open in browser:
```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### JSON Report Analysis
```python
import json

with open("coverage.json") as f:
    data = json.load(f)

print(f"Overall coverage: {data['totals']['percent_covered']}%")
print(f"Covered lines: {data['totals']['covered_lines']}")
print(f"Missing lines: {data['totals']['num_statements'] - data['totals']['covered_lines']}")

# Analyze per-module coverage
for file, coverage in data.items():
    if file != "totals":
        percent = coverage["summary"]["percent_covered"]
        print(f"{file}: {percent}%")
```

## Coverage Thresholds

Set minimum required coverage:

```python
# Fail if coverage drops below 90%
generate_coverage_report(db, {
    "min_coverage": 90,
    "output_format": "html"
})
# Returns success=False if coverage < 90%
```

## Specific Modules

Generate coverage for specific modules:

```python
# Only check coffee_maker/models and coffee_maker/api
generate_coverage_report(db, {
    "include_modules": ["coffee_maker.models", "coffee_maker.api"],
    "output_format": "html"
})
```

## Bash Equivalents

```bash
# HTML report (interactive)
pytest --cov=coffee_maker --cov-report=html

# JSON report (programmatic)
pytest --cov=coffee_maker --cov-report=json

# Terminal with missing lines
pytest --cov=coffee_maker --cov-report=term-missing

# XML report
pytest --cov=coffee_maker --cov-report=xml

# All formats
pytest --cov=coffee_maker \
  --cov-report=html \
  --cov-report=json \
  --cov-report=term-missing
```

## Workflow

```
1. code_developer completes implementation
2. code_developer calls run_test_suite
3. code_developer calls generate_coverage_report
4. Report generated and saved
5. code_developer reviews coverage (target: 90%+)
6. If coverage < 90%: add more tests
7. If coverage >= 90%: ready to complete
```

## Coverage by Module

Typical coverage targets:

| Module | Target | Rationale |
|--------|--------|-----------|
| coffee_maker/models/ | 95% | Core business logic |
| coffee_maker/api/ | 90% | Endpoints |
| coffee_maker/utils/ | 85% | Utilities |
| coffee_maker/cli/ | 80% | CLI commands |
| tests/ | N/A | Test code (not counted) |

## Identifying Coverage Gaps

HTML report shows:
- Green lines: covered by tests
- Red lines: not covered by tests
- Yellow lines: partial coverage (branches)

## Integration with CI/CD

For GitHub Actions / other CI:

```yaml
# Generate coverage report
- run: pytest --cov=coffee_maker --cov-report=json

# Upload coverage
- uses: codecov/codecov-action@v3
  with:
    files: ./coverage.json
```

## Improving Coverage

Low coverage hints:

1. **Conditional branches** - Add tests for if/else paths
2. **Error cases** - Test exception handling
3. **Edge cases** - Test boundary conditions
4. **Integration** - Test component interactions
5. **Database** - Test data access patterns

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| ReportGenError | Coverage report failed | Check pytest-cov |
| ThresholdError | Coverage below minimum | Add more tests |
| FileNotFoundError | Output path invalid | Check path |
| ParseError | Failed to parse coverage | Check output format |

## Coverage Report Retention

Keep historical coverage reports:

```bash
mkdir -p coverage-reports
cp htmlcov coverage-reports/coverage-$(date +%Y%m%d-%H%M%S)
```

Then analyze trends over time to see if coverage is improving.

## Coverage Badge

Generate coverage badge for README:

```python
import json

with open("coverage.json") as f:
    coverage = json.load(f)["totals"]["percent_covered"]

badge_color = "green" if coverage >= 90 else "orange" if coverage >= 80 else "red"
print(f"[![Coverage](https://img.shields.io/badge/coverage-{coverage}%25-{badge_color})]")
```
