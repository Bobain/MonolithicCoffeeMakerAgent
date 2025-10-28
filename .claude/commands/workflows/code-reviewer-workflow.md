---
command: code-reviewer-workflow
workflow: review
agent: code_reviewer
purpose: Complete code review workflow
tables: [code_review, quality_check, security_scan, test_coverage]
tools: [git, pytest, black, mypy, bandit]
duration: 10-45m
---

## Purpose

Execute complete code review workflow: analyze commit → run security scan → check style → validate tests → generate quality score → notify architect. This is the PRIMARY workflow command for the code_reviewer agent, replacing 4 individual commands with one intelligent workflow.

## Workflow Overview

```
review(target) → Analyze → Security → Style → Tests → Quality Score → ReviewResult
```

**Key Features**:
- **4 scope levels**: FULL (complete review), QUICK (fast check), SECURITY_ONLY, STYLE_ONLY
- **Quality scoring**: 0-100 score based on multiple metrics
- **Auto-fix support**: Can automatically fix style issues
- **Security scanning**: Bandit + custom security rules
- **Rich result tracking**: Comprehensive ReviewResult with issues found/fixed

## Input Parameters

```yaml
TARGET:
  type: string
  required: true
  description: Commit SHA, branch, or PR number to review
  example: "abc123def" or "main" or "PR-42"

SCOPE:
  type: string
  default: "full"
  enum: [full, quick, security-only, style-only]
  description: |
    - full: Complete review with all checks
    - quick: Fast review (style + basic tests)
    - security-only: Security scan only
    - style-only: Style check only

AUTO_FIX:
  type: boolean
  default: false
  description: Automatically fix style issues (Black, autoflake)

NOTIFY:
  type: boolean
  default: true
  description: Notify architect of review results

VERBOSE:
  type: boolean
  default: false
  description: Enable detailed logging
```

## Workflow Execution

### FULL Scope (Default)

Complete code review:

```python
1. Analyze target (commit, branch, or PR)
2. Run security scan (Bandit)
3. Check style compliance (Black, line length)
4. Validate test coverage (pytest-cov)
5. Check type hints (MyPy)
6. Analyze complexity (cyclomatic, cognitive)
7. Generate quality score (0-100)
8. Create review report
9. Notify architect if issues found
10. Return comprehensive ReviewResult
```

### QUICK Scope

Fast review for rapid iteration:

```python
1. Analyze target
2. Check style (Black only)
3. Run tests (no coverage)
4. Generate basic quality score
5. Return ReviewResult
```

### SECURITY_ONLY Scope

Security-focused review:

```python
1. Analyze target
2. Run Bandit security scanner
3. Check for hardcoded secrets
4. Validate input sanitization
5. Check SQL injection vulnerabilities
6. Return security-focused ReviewResult
```

### STYLE_ONLY Scope

Style-focused review:

```python
1. Analyze target
2. Run Black (with auto-fix if enabled)
3. Check line length
4. Validate docstrings
5. Return style-focused ReviewResult
```

## Result Object

```python
@dataclass
class ReviewResult:
    target: str  # Commit SHA or identifier
    status: str  # success | partial | failed
    quality_score: int  # 0-100
    issues_found: int
    issues_fixed: int
    checks_completed: List[str]
    checks_failed: List[str]
    duration_seconds: float
    error_message: Optional[str]
    metadata: Dict[str, Any]
```

## Success Criteria

### Full Success (status = "success")

- ✅ All checks completed
- ✅ Quality score >= 80
- ✅ No security issues
- ✅ Style compliant
- ✅ Test coverage >= 90%

### Partial Success (status = "partial")

- ✅ Most checks completed
- ⚠️ Quality score 60-79
- ⚠️ Minor issues found
- ⚠️ Some checks failed

### Failure (status = "failed")

- ❌ Critical error occurred
- ❌ Quality score < 60
- ❌ Security vulnerabilities found
- ❌ Major checks failed

## Quality Scoring Algorithm

```python
def calculate_quality_score(results):
    score = 100

    # Security (-30 points for vulnerabilities)
    if results["security"]["vulnerabilities"] > 0:
        score -= 30

    # Style (-10 points for violations)
    if results["style"]["violations"] > 0:
        score -= 10

    # Test coverage (-20 points if < 90%)
    coverage = results["tests"]["coverage"]
    if coverage < 90:
        score -= (90 - coverage) / 5  # 1 point per 5%

    # Type hints (-15 points if < 100%)
    type_coverage = results["type_hints"]["coverage"]
    if type_coverage < 100:
        score -= (100 - type_coverage) / 7  # ~1 point per 7%

    # Complexity (-10 points for high complexity)
    if results["complexity"]["high_complexity_functions"] > 0:
        score -= 10

    return max(score, 0)  # Floor at 0
```

## Database Operations

### Insert: Code Review

```sql
INSERT INTO code_review (
    review_id, target, scope, quality_score,
    issues_found, issues_fixed, status, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
```

### Insert: Security Scan

```sql
INSERT INTO security_scan (
    scan_id, review_id, tool, vulnerabilities_found,
    severity_high, severity_medium, severity_low,
    scan_output, created_at
) VALUES (?, ?, 'bandit', ?, ?, ?, ?, ?, datetime('now'))
```

### Insert: Quality Check

```sql
INSERT INTO quality_check (
    check_id, review_id, check_type, status,
    issues_found, output, created_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

### Update: Test Coverage

```sql
INSERT INTO test_coverage (
    coverage_id, review_id, total_coverage,
    statement_coverage, branch_coverage,
    uncovered_lines, created_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

## Error Handling

| Error | Cause | Recovery | Status |
|-------|-------|----------|--------|
| Target not found | Invalid commit SHA | Verify target exists | failed |
| Security scan failed | Bandit error | Review scan config | partial |
| Style check failed | Black error | Manual style fix | partial |
| Test execution failed | pytest error | Fix broken tests | partial |
| Coverage too low | < 90% coverage | Write more tests | partial |

## Examples

### Example 1: Full Review

```python
result = workflow.review(
    target="abc123def",
    scope="full",
    notify=True
)
```

**Result**:
```python
ReviewResult(
    target="abc123def",
    status="success",
    quality_score=92,
    issues_found=3,
    issues_fixed=0,
    checks_completed=["security", "style", "tests", "type_hints", "complexity"],
    checks_failed=[],
    duration_seconds=300.0,
    error_message=None,
    metadata={
        "security": {"vulnerabilities": 0},
        "style": {"violations": 0},
        "tests": {"coverage": 95.3, "passed": 150, "failed": 0},
        "type_hints": {"coverage": 98.5},
        "complexity": {"high_complexity_functions": 1}
    }
)
```

### Example 2: Quick Review

```python
result = workflow.review(
    target="def456ghi",
    scope="quick",
    notify=False
)
```

**Result**:
```python
ReviewResult(
    target="def456ghi",
    status="success",
    quality_score=85,
    issues_found=2,
    issues_fixed=0,
    checks_completed=["style", "tests"],
    checks_failed=[],
    duration_seconds=60.0,
    error_message=None,
    metadata={
        "style": {"violations": 0},
        "tests": {"passed": 50, "failed": 0}
    }
)
```

### Example 3: Security Only with Issues

```python
result = workflow.review(
    target="ghi789jkl",
    scope="security-only"
)
```

**Result**:
```python
ReviewResult(
    target="ghi789jkl",
    status="failed",
    quality_score=70,  # -30 for security issues
    issues_found=2,
    issues_fixed=0,
    checks_completed=["security"],
    checks_failed=["security"],
    duration_seconds=45.0,
    error_message="Security vulnerabilities found: 2 high, 0 medium",
    metadata={
        "security": {
            "vulnerabilities": 2,
            "high": 2,
            "medium": 0,
            "low": 0,
            "details": [
                "Hardcoded password in config.py:42",
                "SQL injection risk in query.py:108"
            ]
        }
    }
)
```

### Example 4: Style Only with Auto-Fix

```python
result = workflow.review(
    target="jkl012mno",
    scope="style-only",
    auto_fix=True
)
```

**Result**:
```python
ReviewResult(
    target="jkl012mno",
    status="success",
    quality_score=90,
    issues_found=15,
    issues_fixed=15,  # All fixed by Black
    checks_completed=["style"],
    checks_failed=[],
    duration_seconds=20.0,
    error_message=None,
    metadata={
        "style": {
            "violations": 15,
            "auto_fixed": 15,
            "files_formatted": ["app.py", "utils.py", "models.py"]
        }
    }
)
```

## Review Report Format

```markdown
# Code Review Report: abc123def

**Date**: 2025-10-28
**Scope**: FULL
**Quality Score**: 92/100
**Status**: SUCCESS

## Summary
✅ All checks passed
✅ High code quality
⚠️ 1 high-complexity function found

## Checks Completed
- ✅ Security Scan (Bandit)
- ✅ Style Check (Black)
- ✅ Test Coverage (95.3%)
- ✅ Type Hints (98.5%)
- ⚠️ Complexity Analysis

## Issues Found: 3

### High Complexity
- `calculate_route()` in `routing.py:156` - Cyclomatic complexity: 18
  **Recommendation**: Refactor into smaller functions

### Minor Issues
- Missing docstring in `helper.py:42`
- Line too long in `config.py:89` (125 chars)

## Test Coverage
- **Total**: 95.3%
- **Statements**: 96.1%
- **Branches**: 93.8%

**Uncovered**:
- `error_handler.py:45-52` (edge case handling)

## Security Scan
✅ No vulnerabilities found

## Recommendations
1. Refactor `calculate_route()` to reduce complexity
2. Add docstring to `helper()`
3. Increase test coverage to 100%
```

## Implementation Notes

### Security Scanning

```bash
# Run Bandit security scanner
bandit -r coffee_maker/ -f json -o scan_results.json

# Check for hardcoded secrets
grep -r "password\s*=\s*['\"]" coffee_maker/

# Validate SQL queries
grep -r "execute.*%" coffee_maker/
```

### Style Checking

```bash
# Run Black (with auto-fix)
black coffee_maker/ tests/

# Check line length
grep -r ".\{121,\}" coffee_maker/
```

### Test Coverage

```bash
# Run pytest with coverage
pytest --cov=coffee_maker --cov-report=term-missing --cov-report=json

# Parse coverage.json for metrics
```

### Type Hint Coverage

```bash
# Run MyPy
mypy coffee_maker/ --strict

# Calculate type hint coverage
# Count functions with type hints / total functions
```

## Integration with Other Workflows

### → Code Developer (post-commit)

```python
# Developer commits, reviewer checks
dev_result = developer.work(task_id="TASK-42")
if dev_result.commit_sha:
    review_result = reviewer.review(target=dev_result.commit_sha)
```

### → Architect (quality feedback)

```python
# Reviewer notifies architect of issues
review_result = reviewer.review(target="abc123def")
if review_result.quality_score < 80:
    # Auto-notify architect via agent_notification
```

### → Project Manager (quality tracking)

```python
# PM tracks code quality metrics
review_result = reviewer.review(target="abc123def")
pm.manage(
    action="track",
    updates={"quality_score": review_result.quality_score}
)
```

## Performance Expectations

| Scope | Duration | Checks Run | Issues Typical |
|-------|----------|------------|----------------|
| FULL | 10-30m | 5-7 checks | 0-10 issues |
| QUICK | 2-10m | 2-3 checks | 0-5 issues |
| SECURITY_ONLY | 3-15m | 1 check | 0-5 issues |
| STYLE_ONLY | 1-5m | 1 check | 0-20 issues |

## Best Practices

1. **Use FULL scope** for all commits to main branch
2. **Use QUICK scope** for rapid iteration on feature branches
3. **Use SECURITY_ONLY** before deployments
4. **Use STYLE_ONLY** with auto_fix during development
5. **Enable auto_fix** for style issues (saves time)
6. **Check quality_score** and aim for >= 85
7. **Review issues_found** even if status is success
8. **Set up pre-commit hooks** to run quick review

## Related Commands

- `developer.work()` - Implement code before review
- `architect.spec()` - Create specs that guide quality standards
- `project_manager.manage()` - Track quality metrics

---

**Workflow Reduction**: This single `review()` command replaces:
1. `run_security_scan()`
2. `check_style()`
3. `validate_tests()`
4. `generate_report()`

**Context Savings**: ~250 lines vs ~1,500 lines (4 commands)
