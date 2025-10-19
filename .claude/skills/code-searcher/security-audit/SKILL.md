---
name: security-audit
version: 1.0.0
agent: code-searcher
scope: agent-specific
description: >
  Comprehensive security audit: scan for OWASP Top 10 vulnerabilities,
  check dependencies, analyze authentication flows, generate report.

triggers:
  - "security audit"
  - "scan for vulnerabilities"
  - "check security"
  - "OWASP audit"

requires:
  - bandit>=1.7  # Python security scanner
  - safety>=2.0  # Dependency vulnerability scanner

inputs:
  scope:
    type: string
    required: false
    description: Scope to audit (default: entire codebase)

outputs:
  vulnerabilities:
    type: list[dict]
    description: List of vulnerabilities found

  security_score:
    type: float
    description: Security score (0-100)

  report_path:
    type: string
    description: Path to security audit report

author: architect agent
created: 2025-10-19
---

# Security Audit Skill

Comprehensive security audit for code-searcher.

## Workflow

1. **Scan Code**: Use bandit to scan for vulnerabilities
2. **Check Dependencies**: Use safety to scan dependencies
3. **Analyze Auth Flows**: Review authentication/authorization
4. **Classify Vulnerabilities**: Map to OWASP Top 10
5. **Generate Score**: Calculate security score
6. **Create Report**: Synthetic security audit report

## Expected Time Savings

- **Manual Security Audit**: 3 hours
- **With Skill**: 30 minutes
- **Time Saved**: 83% reduction
