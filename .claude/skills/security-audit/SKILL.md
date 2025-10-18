---
description: Vulnerability scanning, dependency analysis, and security pattern detection
---

# Security Audit Skill

## What This Skill Does

Comprehensive security analysis to identify vulnerabilities, analyze dependencies, and detect security-related code patterns.

**Capabilities**:
- **check_vulnerabilities**: Scan for common security vulnerabilities (SQL injection, hardcoded secrets, unsafe deserialization, weak crypto, missing validation, insecure random)
- **analyze_dependencies**: Analyze third-party dependencies for known vulnerabilities
- **find_security_patterns**: Identify security-related patterns and best practices
- **generate_report**: Create comprehensive security report

## When To Use

- Before deploying code to production
- After dependency updates
- During architecture reviews
- Compliance and security audits
- Identifying and fixing security vulnerabilities

## Instructions

### Check Vulnerabilities
```bash
python scripts/security_audit.py check_vulnerabilities
```

**Output**: Lists all detected vulnerabilities by severity

### Analyze Dependencies
```bash
python scripts/security_audit.py analyze_dependencies
```

**Output**: Third-party packages with known vulnerabilities

### Find Security Patterns
```bash
python scripts/security_audit.py find_security_patterns
```

**Output**: Security-related code patterns (custom crypto, exception suppression, debug mode, etc.)

### Generate Report
```bash
python scripts/security_audit.py generate_report
```

**Output**: Comprehensive security report with summary and recommendations

## Available Scripts

- `scripts/security_audit.py` - Main security scanning engine

## Used By

- **architect**: For security architecture reviews and best practices
- **code_developer**: For identifying and fixing security issues during implementation
- **project_manager**: For security compliance reporting

## Vulnerability Severity Levels

- **critical**: SQL injection, hardcoded secrets - must fix immediately
- **high**: Unsafe deserialization, weak crypto - fix before production
- **medium**: Missing validation, insecure random, debug mode - address soon
- **low**: Exception suppression, suspicious patterns - monitor and refactor

## Example Output

```json
{
  "vulnerabilities": {
    "sql_injection": {
      "severity": "critical",
      "count": 2,
      "locations": [
        {
          "file": "coffee_maker/db/queries.py",
          "line": 45,
          "issue": "f-string SQL query"
        }
      ]
    }
  },
  "summary": {
    "critical": 2,
    "high": 1,
    "medium": 3,
    "low": 0
  }
}
```
