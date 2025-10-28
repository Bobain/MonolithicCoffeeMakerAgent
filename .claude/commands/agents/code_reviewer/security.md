# security

## Purpose
Run deep security scan with Bandit, detect secrets (API keys, passwords), check dependency vulnerabilities, generate security report.

## Parameters
```yaml
target: str  # Required, commit SHA, branch, or PR number
severity_threshold: str = "medium"  # "low" | "medium" | "high"
include_dependencies: bool = true  # Check for vulnerable packages
auto_report: bool = true  # Create security report
```

## Workflow
1. Identify target files (commit/branch/PR)
2. Run Bandit security scan
3. Detect hardcoded secrets (regex patterns)
4. Check dependency vulnerabilities (Safety)
5. Analyze SQL injection risks
6. Check for insecure deserialization
7. Generate security score (0-100)
8. Create report if auto_report=True
9. Return SecurityResult

## Database Operations
```sql
-- Log security scan
INSERT INTO security_scan (
    scan_id, target, timestamp, vulnerabilities_found,
    severity_breakdown, score, status
) VALUES (?, ?, datetime('now'), ?, ?, ?, 'completed')

-- Track vulnerability
INSERT INTO security_vulnerability (
    vulnerability_id, scan_id, severity, category,
    file_path, line_number, description, cwe_id
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
```

## Result Object
```python
@dataclass
class SecurityResult:
    target: str
    vulnerabilities_found: int
    severity_breakdown: dict  # {high: 0, medium: 2, low: 5}
    secrets_detected: int
    security_score: int  # 0-100
    report_path: str  # None if auto_report=False
    status: str  # "pass" | "warning" | "fail"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| BanditNotInstalled | Missing tool | Install: poetry add --dev bandit |
| TargetNotFound | Invalid commit/branch | Verify target exists |
| ScanTimeout | Analysis too long | Reduce scope or increase timeout |
| DependencyCheckFailed | Safety unavailable | Skip dependency check |

## Example
```python
result = security(target="abc123def", severity_threshold="medium")
# SecurityResult(
#   target="abc123def",
#   vulnerabilities_found=3,
#   severity_breakdown={"high": 0, "medium": 2, "low": 1},
#   secrets_detected=0,
#   security_score=92,
#   report_path="reports/security-abc123def.md",
#   status="warning"
# )
```

## Related Commands
- analyze() - Full review including security
- fix() - Auto-fix some security issues

---
Estimated: 55 lines | Context: ~3.5% | Examples: security_examples.md
