# analyze

## Purpose
Run comprehensive code review: security scan, style check, test coverage, type hints, complexity analysis, generate quality score.

## Parameters
```yaml
target: str  # Required, commit SHA, branch, or PR number
quick: bool = false  # Fast analysis (skip deep checks)
auto_fix: bool = false  # Auto-fix style issues
notify_architect: bool = true  # Notify on quality < 80
```

## Workflow
1. Identify target (commit/branch/PR)
2. Run security scan (Bandit)
3. Check style compliance (Black)
4. Validate test coverage (pytest-cov)
5. Check type hint coverage (MyPy)
6. Analyze complexity (cyclomatic, cognitive)
7. Calculate quality score (0-100)
8. Generate review report
9. Notify architect if score < 80
10. Return AnalyzeResult

## Quality Score Calculation
```python
score = 100
if security_vulnerabilities > 0: score -= 30
if style_violations > 0: score -= 10
if test_coverage < 90%: score -= (90 - coverage) / 5
if type_coverage < 100%: score -= (100 - coverage) / 7
if high_complexity_functions > 0: score -= 10
return max(score, 0)
```

## Result Object
```python
@dataclass
class AnalyzeResult:
    target: str
    quality_score: int  # 0-100
    issues_found: int
    issues_by_category: dict  # {security: 0, style: 2, ...}
    checks_completed: List[str]
    checks_failed: List[str]
    duration_seconds: float
    status: str  # "success" | "partial" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| TargetNotFound | Invalid commit/branch | Verify target exists |
| ScanToolMissing | Bandit not installed | Install: poetry add --dev bandit |
| TestExecutionFailed | Tests broken | Fix tests before review |
| TimeoutError | Analysis too long | Reduce scope or increase timeout |

## Example
```python
result = analyze(target="abc123def", quick=False)
# AnalyzeResult(
#   target="abc123def",
#   quality_score=92,
#   issues_found=3,
#   issues_by_category={"security": 0, "style": 2, "coverage": 1},
#   checks_completed=["security", "style", "tests", "types", "complexity"],
#   checks_failed=[],
#   duration_seconds=45.2,
#   status="success"
# )
```

## Related Commands
- security() - Deep security analysis
- fix() - Auto-fix identified issues

---
Estimated: 65 lines | Context: ~4% | Examples: analyze_examples.md
