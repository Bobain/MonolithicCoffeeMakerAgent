---
command: code_reviewer.generate_review_report
agent: code_reviewer
action: generate_review_report
tables:
  write: [review_code_review, review_issue]
  read: [review_commit, specs_specification, roadmap_priority]
required_tools: [black, flake8, pylint, bandit, radon, mypy, pytest]
estimated_duration_seconds: 60
---

# Command: code_reviewer.generate_review_report

## Purpose

Analyze a commit's code changes and generate a comprehensive review report including all code quality findings. This is the main command that orchestrates all other code analysis commands and produces the final review record.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to review
run_all_checks: boolean         # Run full analysis suite (default: true)
focus_areas: array              # Optional - ["security", "style", "complexity", "coverage", "types", "architecture"]
quality_threshold: number       # Minimum acceptable score (default: 7.0)
include_recommendations: boolean # Include fix recommendations (default: true)
generate_html_report: boolean   # Export HTML version (default: false)
```

## Database Operations

**Query 1: Get review entry**
```sql
SELECT id, commit_sha, status, started_at
FROM review_code_review
WHERE commit_sha = ? AND status = 'pending'
LIMIT 1;
```

**Query 2: Get commit details**
```sql
SELECT commit_sha, created_at, author, message, files_changed
FROM review_commit
WHERE sha = ?;
```

**Query 3: Insert issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));
```

**Query 4: Update review completion**
```sql
UPDATE review_code_review
SET quality_score = ?,
    total_issues = ?,
    critical_issues = ?,
    style_issues = ?,
    security_issues = ?,
    coverage_issues = ?,
    approved = ?,
    status = 'completed',
    completed_at = datetime('now'),
    analysis_time_seconds = ?
WHERE commit_sha = ?;
```

## External Tools

### 1. Style Compliance Checks

```bash
# Check with black (PEP 8 formatter)
black --check --diff coffee_maker/ tests/ 2>/dev/null

# Check with flake8 (style and logic errors)
flake8 coffee_maker/ tests/ --max-line-length=120 --format=json

# Check with pylint (comprehensive code quality)
pylint coffee_maker/ --max-line-length=120 --exit-zero --output-format=json
```

### 2. Security Scan

```bash
# Run bandit security scanner
bandit -r coffee_maker/ -f json -o /tmp/bandit-report.json 2>/dev/null
cat /tmp/bandit-report.json
```

### 3. Complexity Analysis

```bash
# Check cyclomatic complexity
radon cc coffee_maker/ -a -j

# Check maintainability index
radon mi coffee_maker/ -j

# Check cognitive complexity
radon cc coffee_maker/ --show-complexity --average
```

### 4. Test Coverage

```bash
# Run pytest with coverage
pytest tests/ --cov=coffee_maker --cov-report=json --cov-report=term-summary 2>/dev/null

# Parse coverage JSON
python3 -c "import json; cov=json.load(open('.coverage')); print(cov['totals']['percent_covered'])"
```

### 5. Type Checking

```bash
# Run mypy strict type checking
mypy coffee_maker/ --strict --show-error-codes --output-format=json 2>/dev/null
```

### 6. Architecture Compliance

```bash
# Check CFR compliance (manual inspection of code patterns)
grep -r "AgentRegistry" coffee_maker/ --include="*.py" | wc -l
grep -r "sound=False" coffee_maker/ --include="*.py" | wc -l
grep -r "CFR" docs/architecture/guidelines --include="*.md"
```

## Success Criteria

- ✅ Executes all selected analysis tools without crashing
- ✅ Parses tool output into structured issues
- ✅ Calculates quality_score (1-10) based on formula
- ✅ Identifies severity for each issue (CRITICAL, HIGH, MEDIUM, LOW)
- ✅ Stores all issues in review_issue table
- ✅ Updates review_code_review with findings
- ✅ Completes analysis in <60 seconds
- ✅ Provides actionable recommendations for each issue
- ✅ Handles tool failures gracefully (continue with other tools)

## Quality Score Calculation

```
base_score = 10.0

# Style violations (max -3.0)
black_issues × -0.5 (capped at -1.0)
flake8_issues × -0.3 (capped at -1.0)
pylint_score: max(0, (7.5 - score) × -0.2)

# Security (max -3.0)
bandit_critical × -2.0
bandit_high × -1.0
bandit_medium × -0.5

# Testing (max -2.0)
(coverage < 90%) × -1.0 per 5% below
test_count_decrease × -0.5

# Complexity (max -2.0)
high_complexity_functions × -0.5

# Type Safety (max -2.0)
mypy_errors × -1.0
missing_type_hints × -0.1 per function

# Architecture (max -2.0)
cfr_violations × -2.0
pattern_violations × -1.0

final_score = max(1, min(10, base_score))
approved = final_score >= quality_threshold
```

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "quality_score": 7,
  "approved": true,
  "analysis_duration_seconds": 47.3,
  "issues_summary": {
    "total_issues": 8,
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 2
  },
  "analysis_results": {
    "style": {
      "black_compliant": false,
      "flake8_issues": 3,
      "pylint_score": 8.2,
      "auto_fixable": 2
    },
    "security": {
      "vulnerabilities": 1,
      "critical_count": 1,
      "high_count": 0,
      "scan_time_seconds": 8.2
    },
    "complexity": {
      "average_complexity": 3.5,
      "high_complexity_functions": 1,
      "maintainability_index": 81.2
    },
    "testing": {
      "coverage": 89.5,
      "passing_tests": 145,
      "failing_tests": 0
    },
    "types": {
      "mypy_errors": 1,
      "type_compliance": 98.5
    },
    "architecture": {
      "cfr_violations": 0,
      "pattern_issues": 0,
      "compliance_score": 100
    }
  },
  "issues": [
    {
      "id": "ISS-1",
      "severity": "CRITICAL",
      "category": "Security",
      "file_path": "coffee_maker/auth.py",
      "line_number": 42,
      "description": "SQL injection vulnerability detected",
      "recommendation": "Use parameterized queries instead of string concatenation",
      "effort_estimate": "30 minutes"
    }
  ],
  "report_url": "docs/code-reviews/REV-2025-10-26T10-35-abc1.html"
}
```

## Error Handling

**Tool Execution Error**:
```json
{
  "status": "partial_success",
  "warning": "Some analysis tools failed",
  "failed_tools": ["bandit"],
  "completed_tools": ["black", "flake8", "pylint", "mypy"],
  "quality_score": 6,
  "approved": false,
  "note": "Analysis incomplete - security check failed"
}
```

**No Issues Found**:
```json
{
  "status": "success",
  "quality_score": 10,
  "approved": true,
  "issues": [],
  "message": "Perfect code quality - no issues detected"
}
```

## Examples

### Example 1: Full analysis

```bash
code_reviewer.generate_review_report(
  commit_sha="abc123def456",
  run_all_checks=true,
  quality_threshold=7.0
)
```

### Example 2: Security-focused review

```bash
code_reviewer.generate_review_report(
  commit_sha="abc123def456",
  focus_areas=["security", "types"],
  include_recommendations=true
)
```

### Example 3: Quick assessment

```bash
code_reviewer.generate_review_report(
  commit_sha="abc123def456",
  run_all_checks=false,
  focus_areas=["style", "coverage"]
)
```

## Implementation Notes

- Generate unique review IDs as: `REV-{timestamp}-{commit_sha[:8]}`
- Store issues with generated IDs as: `ISS-{sequential}`
- Handle tool failures gracefully - continue analysis with other tools
- Cache tool outputs to avoid re-running for same commit
- Use git diff to analyze only changed files (optimization)
- Mark critical security issues for immediate architect notification

## Related Commands

- `code_reviewer.detect_new_commits` - Find commits to review
- `code_reviewer.notify_architect` - Escalate critical findings
- `code_reviewer.check_style_compliance` - Detailed style analysis
- `code_reviewer.run_security_scan` - Detailed security analysis

---

**Version**: 1.0
**Last Updated**: 2025-10-26
