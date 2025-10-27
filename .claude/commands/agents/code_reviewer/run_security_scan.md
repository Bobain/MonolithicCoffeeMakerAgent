---
command: code_reviewer.run_security_scan
agent: code_reviewer
action: run_security_scan
tables:
  write: [review_issue]
  read: [review_code_review, review_commit]
required_tools: [bandit, git]
estimated_duration_seconds: 20
---

# Command: code_reviewer.run_security_scan

## Purpose

Run bandit security vulnerability scanner to detect potential security issues in Python code. This command identifies security vulnerabilities, hardcoded passwords, dangerous function calls, and other security anti-patterns.

## Input Parameters

```yaml
commit_sha: string              # Required - commit to scan
review_id: string               # Required - link issues to review
severity_threshold: string      # Report: "all", "HIGH", "MEDIUM" (default: "HIGH")
exclude_tests: boolean          # Skip test files (default: false)
include_severity: array         # Include severities: ["HIGH", "MEDIUM", "LOW"]
show_evidence: boolean          # Include code snippets (default: true)
```

## Database Operations

**Query: Insert security issues**
```sql
INSERT INTO review_issue (
    id, review_id, severity, category, file_path, line_number,
    description, recommendation, created_at
) VALUES (?, ?, ?, 'Security', ?, ?, ?, ?, datetime('now'));
```

## External Tools

### Bandit Security Scanner

```bash
# Run bandit on entire project
bandit -r coffee_maker/ -f json 2>&1

# JSON Output Format:
# {
#   "results": [
#     {
#       "test_id": "B102",
#       "test_name": "exec_used",
#       "issue_severity": "HIGH",
#       "issue_cwe": {"id": 95},
#       "issue_text": "Use of exec detected",
#       "line_number": 42,
#       "line_range": [42, 43],
#       "filename": "path/to/file.py",
#       "node": "exec"
#     }
#   ],
#   "metrics": {
#     "path/to/file.py": {
#       "TOTAL": 1,
#       "HIGH": 1,
#       "MEDIUM": 0,
#       "LOW": 0
#     }
#   }
# }
```

### Severity Mapping

**Bandit HIGH → CRITICAL** (immediate action required):
- SQL injection vulnerabilities (B602, B608)
- Code injection (B102, B303, B307)
- Pickle deserialization (B301)
- Hardcoded secrets (B105, B106, B107)
- Insecure temporary files (B108)
- Use of input() in Python 2 (B322)

**Bandit MEDIUM → HIGH** (address before merge):
- Assert usage in production (B101)
- Try/except pass (B110)
- Mutable default arguments (B006)
- Weak cryptography (B303, B304, B305)
- Shell=True in subprocess (B602)

**Bandit LOW → MEDIUM** (informational):
- Exception handling warnings (B110, B112)
- Import warnings (B611)
- Type confusion (B303)

### Key Bandit Tests

| Test ID | Issue | Severity |
|---------|-------|----------|
| B101 | assert_used | LOW |
| B102 | exec_used | HIGH |
| B105 | hardcoded_password_string | MEDIUM |
| B106 | hardcoded_password_funcarg | MEDIUM |
| B107 | hardcoded_password_default | MEDIUM |
| B108 | hardcoded_temp_file | MEDIUM |
| B110 | try_except_pass | LOW |
| B201 | flask_debug_true | HIGH |
| B301 | pickle | HIGH |
| B302 | marshal | HIGH |
| B303 | md5 | MEDIUM |
| B304 | des | HIGH |
| B305 | cipher | MEDIUM |
| B306 | mktemp_q | MEDIUM |
| B307 | eval | HIGH |
| B308 | mark_safe | MEDIUM |
| B309 | httpsconnection | MEDIUM |
| B310 | url_open | MEDIUM |
| B311 | random | LOW |
| B312 | telnetlib | HIGH |
| B313 | xml | MEDIUM |
| B314 | xml_bad_etree | MEDIUM |
| B315 | xml_expat | MEDIUM |
| B316 | xml_sax | MEDIUM |
| B317 | xml_pulldom | MEDIUM |
| B318 | xml_minidom | MEDIUM |
| B319 | xml_etree_iterparse | MEDIUM |
| B320 | xml_etree | MEDIUM |
| B321 | ftplib | MEDIUM |
| B322 | input | MEDIUM |
| B323 | unverified_context | MEDIUM |
| B324 | hashlib | MEDIUM |
| B325 | tempnam | MEDIUM |
| B601 | paramiko_calls | MEDIUM |
| B602 | subprocess_popen_with_shell_equals_true | HIGH |
| B603 | subprocess_without_shell_equals_true | LOW |
| B604 | any_other_function_with_shell_equals_true | MEDIUM |
| B605 | start_process_with_a_shell | MEDIUM |
| B606 | start_process_with_no_shell | LOW |
| B607 | partial_paramiko_calls | MEDIUM |
| B608 | hardcoded_sql_string | HIGH |
| B609 | wildcard_injection | MEDIUM |
| B610 | django_sql_injection | HIGH |
| B611 | django_security_middleware | MEDIUM |
| B612 | logging_config_var | MEDIUM |
| B701 | jinja2_autoescape_false | HIGH |
| B702 | mako_templates | HIGH |
| B703 | django_mark_safe | MEDIUM |

## Success Criteria

- ✅ Runs bandit scanner without crashing
- ✅ Parses JSON output correctly
- ✅ Maps Bandit severities to issue severities
- ✅ Identifies all vulnerability types
- ✅ Creates review_issue records with proper fields
- ✅ Includes file paths and line numbers
- ✅ Provides security recommendations
- ✅ Handles no vulnerabilities gracefully
- ✅ Completes in <20 seconds

## Output Format

```json
{
  "status": "success",
  "review_id": "REV-2025-10-26T10-35-abc1",
  "commit_sha": "abc123def456",
  "scan_duration_seconds": 12.5,
  "vulnerabilities_found": 2,
  "severity_breakdown": {
    "critical": 1,
    "high": 1,
    "medium": 0,
    "low": 0
  },
  "files_affected": ["coffee_maker/auth.py"],
  "metrics": {
    "total_files_scanned": 45,
    "files_with_issues": 1
  },
  "issues": [
    {
      "id": "ISS-1",
      "severity": "CRITICAL",
      "category": "Security",
      "file_path": "coffee_maker/auth.py",
      "line_number": 42,
      "test_id": "B608",
      "test_name": "hardcoded_sql_string",
      "description": "Possible SQL injection vector through string-based query",
      "code_snippet": "query = \"SELECT * FROM users WHERE id = \" + user_id",
      "recommendation": "Use parameterized queries with placeholders (?)",
      "cwe_id": 89
    },
    {
      "id": "ISS-2",
      "severity": "HIGH",
      "category": "Security",
      "file_path": "coffee_maker/auth.py",
      "line_number": 85,
      "test_id": "B102",
      "test_name": "exec_used",
      "description": "Use of exec detected - code execution vulnerability",
      "code_snippet": "exec(user_input)",
      "recommendation": "Avoid exec() or use restricted evaluation",
      "cwe_id": 95
    }
  ],
  "summary": {
    "critical_vulnerabilities": 1,
    "requires_immediate_fix": true,
    "estimated_fix_time": "2-4 hours"
  }
}
```

## Error Handling

**No Vulnerabilities Found**:
```json
{
  "status": "success",
  "vulnerabilities_found": 0,
  "message": "No security vulnerabilities detected",
  "scan_duration_seconds": 9.2
}
```

**Bandit Not Installed**:
```json
{
  "status": "error",
  "error_type": "TOOL_NOT_FOUND",
  "message": "bandit scanner not installed",
  "installation": "pip install bandit",
  "exit_code": 1
}
```

**Scan Error**:
```json
{
  "status": "error",
  "error_type": "SCAN_FAILED",
  "message": "Bandit scan failed",
  "error_detail": "SyntaxError in file.py",
  "recovery": "Fix syntax errors and retry"
}
```

## Examples

### Example 1: Full security scan

```bash
code_reviewer.run_security_scan(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  severity_threshold="ALL",
  show_evidence=true
)
```

### Example 2: Critical only

```bash
code_reviewer.run_security_scan(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  include_severity=["CRITICAL"]
)
```

### Example 3: Exclude tests

```bash
code_reviewer.run_security_scan(
  commit_sha="abc123def456",
  review_id="REV-2025-10-26T10-35-abc1",
  exclude_tests=true,
  severity_threshold="HIGH"
)
```

## Implementation Notes

- Critical security issues should trigger architect notification immediately
- Store Bandit test_id and test_name for issue tracking
- Include CWE (Common Weakness Enumeration) IDs for reference
- Generate recommendations specific to the vulnerability type
- Consider false positives in high-security environments
- Re-scan when security configuration changes
- Track vulnerability history for trend analysis

## Security Fix Recommendations

### SQL Injection (B608)

**Before**:
```python
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
```

**After**:
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### Code Execution (B102)

**Before**:
```python
exec(user_input)
```

**After**:
```python
# Use ast.literal_eval for safe data parsing
import ast
try:
    data = ast.literal_eval(user_input)
except (ValueError, SyntaxError):
    data = None
```

### Hardcoded Passwords (B105)

**Before**:
```python
password = "admin123"
db.connect(password=password)
```

**After**:
```python
import os
password = os.environ.get("DB_PASSWORD")
db.connect(password=password)
```

### Shell Injection (B602)

**Before**:
```python
subprocess.Popen("ls -la " + user_dir, shell=True)
```

**After**:
```python
subprocess.Popen(["ls", "-la", user_dir], shell=False)
```

## Related Commands

- `code_reviewer.generate_review_report` - Main review orchestrator
- `code_reviewer.check_architecture_compliance` - Check CFRs
- `code_reviewer.notify_architect` - Escalate critical findings

---

**Version**: 1.0
**Last Updated**: 2025-10-26
