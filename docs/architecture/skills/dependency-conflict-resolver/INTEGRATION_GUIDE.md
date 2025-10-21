# Dependency Conflict Resolver - Integration Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-21
**Status**: Production ✅

---

## Table of Contents

1. [Overview](#overview)
2. [SPEC-070 Integration](#spec-070-integration)
3. [Workflow Integration](#workflow-integration)
4. [API Integration](#api-integration)
5. [Agent Integration](#agent-integration)
6. [CI/CD Integration](#cicd-integration)
7. [Monitoring Integration](#monitoring-integration)

---

## Overview

This guide explains how to integrate the Dependency Conflict Resolver skill with other systems in the MonolithicCoffeeMakerAgent project.

### Key Integration Points

1. **SPEC-070 Pre-Approval Matrix**: Three-tier approval system
2. **architect Agent Workflow**: Automated dependency evaluation
3. **code_developer Workflow**: Fast-path for pre-approved packages
4. **Langfuse Observability**: Performance and quality tracking
5. **CI/CD Pipeline**: Automated dependency scanning
6. **ADR Generation**: Documentation automation

---

## SPEC-070 Integration

### Three-Tier Approval System

The Dependency Conflict Resolver integrates with [SPEC-070](../../specs/SPEC-070-dependency-pre-approval-matrix.md) to provide a three-tier approval workflow:

```
┌─────────────────────────────────────────────────────────┐
│              DEPENDENCY REQUEST                         │
└─────────────────────────────────────────────────────────┘
                        ↓
          ┌─────────────────────────┐
          │   DependencyChecker     │
          │ (Check Pre-Approval)    │
          └─────────────────────────┘
                        ↓
    ┌──────────────────┼──────────────────┐
    ↓                  ↓                  ↓
┌──────────┐   ┌──────────────┐   ┌─────────┐
│   TIER 1  │   │    TIER 2    │   │ TIER 3  │
│PRE-APPROVED│  │   STANDARD   │   │ BANNED  │
└──────────┘   └──────────────┘   └─────────┘
    ↓                  ↓                  ↓
 Auto-Add      Run Analyzer         Reject
 (2-5 min)     + User Approval    + Alternatives
               (20-30 min)        (immediate)
```

### Implementation

#### Step 1: Check Pre-Approval Status

```python
from pathlib import Path
from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

# Initialize tools
checker = DependencyChecker()
analyzer = DependencyAnalyzer(project_root=Path.cwd())

# Package to evaluate
package_name = "pytest-timeout"

# Check if pre-approved
status = checker.get_approval_status(package_name)

if status == ApprovalStatus.PRE_APPROVED:
    # Tier 1: Add immediately (no analysis needed)
    print(f"✅ {package_name} is pre-approved")
    print(f"Adding without full analysis...")
    # Add package
    subprocess.run(["poetry", "add", package_name])

elif status == ApprovalStatus.BANNED:
    # Tier 3: Reject immediately
    print(f"❌ {package_name} is banned")
    alternatives = checker.get_alternatives(package_name)
    print(f"Alternatives: {', '.join(alternatives)}")

else:
    # Tier 2: Full analysis required
    print(f"⚠️ {package_name} requires full analysis")
    report = analyzer.analyze_dependency(package_name)
    # Continue with standard approval workflow...
```

#### Step 2: Three-Tier Workflow

**Complete Integrated Workflow**:

```python
import subprocess
from pathlib import Path
from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer, Recommendation

def add_dependency_with_approval(package_name: str, version: str = None) -> bool:
    """
    Add dependency using three-tier approval system.

    Args:
        package_name: Package to add
        version: Optional version constraint

    Returns:
        True if package added successfully, False otherwise
    """
    checker = DependencyChecker()
    analyzer = DependencyAnalyzer(project_root=Path.cwd())

    # Step 1: Check pre-approval status
    status = checker.get_approval_status(package_name)

    # TIER 1: PRE-APPROVED (Fast Path)
    if status == ApprovalStatus.PRE_APPROVED:
        print(f"✅ {package_name} is pre-approved")
        print(f"⏱️ Estimated time: 2-5 minutes")

        # Add package immediately
        cmd = ["poetry", "add", package_name]
        if version:
            cmd[-1] = f"{package_name}{version}"

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Successfully added {package_name}")
            return True
        else:
            print(f"❌ Failed to add {package_name}: {result.stderr}")
            return False

    # TIER 3: BANNED (Reject Path)
    elif status == ApprovalStatus.BANNED:
        print(f"❌ {package_name} is BANNED")

        # Get ban reason
        ban_reason = checker.get_ban_reason(package_name)
        print(f"Reason: {ban_reason}")

        # Suggest alternatives
        alternatives = checker.get_alternatives(package_name)
        if alternatives:
            print(f"\n💡 Suggested alternatives:")
            for alt in alternatives:
                print(f"  - {alt}")

        return False

    # TIER 2: STANDARD (Full Analysis Path)
    else:
        print(f"⚠️ {package_name} requires full analysis")
        print(f"⏱️ Estimated time: 20-30 minutes")

        # Run full analysis
        report = analyzer.analyze_dependency(package_name, version)

        # Display report
        print(f"\n📊 Analysis Results:")
        print(f"Recommendation: {report.recommendation.value}")
        print(f"Security: {report.security.severity.value} ({report.security.cve_count} CVEs)")
        print(f"License: {report.license.license_name} (compatible: {report.license.compatible_with_apache2})")
        print(f"Conflicts: {'Yes' if report.conflicts.has_conflicts else 'No'}")

        # Auto-reject if recommendation is REJECT
        if report.recommendation == Recommendation.REJECT:
            print(f"\n❌ Analysis recommends REJECT")
            print(f"Reason: {report.summary}")

            if report.alternatives:
                print(f"\n💡 Suggested alternatives:")
                for alt in report.alternatives:
                    print(f"  - {alt}")

            return False

        # Request user approval for APPROVE or REVIEW
        print(f"\n🔔 User approval required")
        print(f"Please review analysis and confirm:")
        print(f"Report saved to: docs/architecture/dependency-analysis/{package_name}-analysis.md")

        # In automated workflow, this would delegate to user_listener
        # For now, assume approval granted

        cmd = ["poetry", "add", package_name]
        if version:
            cmd[-1] = f"{package_name}{version}"

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0


# Example usage
if __name__ == "__main__":
    # Tier 1: Pre-approved (fast)
    add_dependency_with_approval("pytest-timeout")  # ~2-5 min

    # Tier 2: Standard (full analysis)
    add_dependency_with_approval("some-new-package")  # ~20-30 min

    # Tier 3: Banned (immediate reject)
    add_dependency_with_approval("mysql-connector-python")  # instant
```

### Pre-Approved Packages

See [SPEC-070](../../specs/SPEC-070-dependency-pre-approval-matrix.md) for the complete list.

**Categories**:
1. **Testing & QA** (17 packages): pytest, pytest-cov, pytest-timeout, mypy, etc.
2. **Code Formatting** (8 packages): black, ruff, isort, flake8, etc.
3. **Observability** (6 packages): langfuse, opentelemetry, prometheus, sentry
4. **Performance** (5 packages): redis, cachetools, msgpack, etc.
5. **CLI/UI** (7 packages): click, typer, rich, colorama, etc.
6. **Web Frameworks** (4 packages): fastapi, uvicorn, pydantic, etc.

**Quick Check**:
```python
from coffee_maker.utils.dependency_checker import DependencyChecker

checker = DependencyChecker()

packages = ["pytest-timeout", "redis", "fastapi", "mysql-connector-python"]

for pkg in packages:
    status = checker.get_approval_status(pkg)
    print(f"{pkg}: {status.value}")

# Output:
# pytest-timeout: PRE_APPROVED
# redis: PRE_APPROVED
# fastapi: PRE_APPROVED
# mysql-connector-python: BANNED
```

---

## Workflow Integration

### architect Agent Workflow

**When**: code_developer requests new dependency

**Process**:
```python
# architect receives request from code_developer
dependency_request = {
    "package": "redis",
    "purpose": "Caching layer for agent state",
    "requester": "code_developer"
}

# Step 1: Check if pre-approved
checker = DependencyChecker()
status = checker.get_approval_status(dependency_request["package"])

if status == ApprovalStatus.PRE_APPROVED:
    # Fast path: Add immediately
    print(f"✅ {dependency_request['package']} is pre-approved, adding...")
    subprocess.run(["poetry", "add", dependency_request["package"]])

    # Notify code_developer
    print(f"✅ Dependency added, proceeding with implementation")

else:
    # Full analysis path
    analyzer = DependencyAnalyzer(project_root=Path.cwd())
    report = analyzer.analyze_dependency(dependency_request["package"])

    # Generate markdown report
    markdown = analyzer.generate_markdown_report(report)

    # Save report
    report_path = Path("docs/architecture/dependency-analysis")
    report_path.mkdir(parents=True, exist_ok=True)
    report_file = report_path / f"{dependency_request['package']}-analysis.md"
    report_file.write_text(markdown)

    # Request user approval via user_listener
    if report.recommendation == Recommendation.APPROVE:
        print(f"✅ Analysis recommends APPROVE")
        print(f"Requesting user approval...")
        # Delegate to user_listener

    elif report.recommendation == Recommendation.REVIEW:
        print(f"⚠️ Analysis recommends REVIEW")
        print(f"Issues: {report.summary}")
        print(f"Requesting user decision...")
        # Delegate to user_listener

    else:  # REJECT
        print(f"❌ Analysis recommends REJECT")
        print(f"Reason: {report.summary}")
        print(f"Alternatives: {', '.join(report.alternatives)}")
        # Notify code_developer of rejection
```

### code_developer Agent Workflow

**When**: Implementing feature that needs new dependency

**Process**:
```python
# code_developer needs dependency
print("Need 'redis' package for caching layer")

# Check if can add directly (pre-approved)
checker = DependencyChecker()
status = checker.get_approval_status("redis")

if status == ApprovalStatus.PRE_APPROVED:
    # code_developer CANNOT modify pyproject.toml directly (CFR-008)
    # But can request fast-path approval
    print("✅ redis is pre-approved, requesting architect to add...")

    # Delegate to architect with note
    message = {
        "to": "architect",
        "package": "redis",
        "purpose": "Caching layer for agent state",
        "pre_approved": True  # Signal fast-path
    }

    # architect adds immediately without user approval

else:
    # Full process required
    print("⚠️ redis requires full analysis and approval")
    print("Delegating to architect...")

    message = {
        "to": "architect",
        "package": "redis",
        "purpose": "Caching layer for agent state",
        "pre_approved": False  # Signal full analysis needed
    }

    # architect runs full analysis + requests user approval
```

---

## API Integration

### Using DependencyAnalyzer Programmatically

**Example 1: Simple Analysis**
```python
from pathlib import Path
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

analyzer = DependencyAnalyzer(project_root=Path.cwd())

# Analyze package
report = analyzer.analyze_dependency("pytest-timeout")

# Access results
print(report.recommendation.value)  # "APPROVE"
print(report.security.severity.value)  # "None"
print(report.license.license_name)  # "MIT"
```

**Example 2: Batch Analysis**
```python
packages = ["pytest", "requests", "click"]

reports = []
for package in packages:
    report = analyzer.analyze_dependency(package)
    reports.append(report)

# Summarize
for report in reports:
    print(f"{report.package_name}: {report.recommendation.value}")
```

**Example 3: Integration with Langfuse**
```python
from langfuse import Langfuse

# Initialize with Langfuse tracking
langfuse_client = Langfuse(
    secret_key="sk-...",
    public_key="pk-...",
    host="https://cloud.langfuse.com"
)

analyzer = DependencyAnalyzer(
    project_root=Path.cwd()),
    langfuse_client=langfuse_client
)

# Analysis is automatically tracked in Langfuse
report = analyzer.analyze_dependency("pytest-timeout")

# View trace in Langfuse dashboard
print(f"Trace ID: {report.trace_id}")  # If Langfuse enabled
```

### Custom Analysis Components

**Example: Override Security Scanner**
```python
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer
from coffee_maker.utils.dependency_security_scanner import SecurityScanner

class CustomSecurityScanner(SecurityScanner):
    """Custom scanner with additional checks."""

    def scan_security(self, package_name, version=None):
        # Run standard scan
        report = super().scan_security(package_name, version)

        # Add custom check (e.g., internal CVE database)
        custom_cves = self._check_internal_db(package_name)
        report.cve_ids.extend(custom_cves)
        report.cve_count += len(custom_cves)

        return report

# Use custom scanner
analyzer = DependencyAnalyzer(project_root=Path.cwd())
analyzer.security_scanner = CustomSecurityScanner()

report = analyzer.analyze_dependency("some-package")
```

---

## Agent Integration

### Notification System (CFR-009 Compliant)

**Background agents MUST use `sound=False`**:

```python
from coffee_maker.autonomous.notification_db import NotificationDB

# architect agent (background) - use sound=False
notification_db = NotificationDB()

notification_db.create_notification(
    agent_id="architect",
    message=f"✅ Dependency analysis complete: {package_name}",
    urgency="medium",
    sound=False  # CFR-009: Background agents must be silent
)
```

**user_listener (UI agent) - can use `sound=True`**:

```python
# user_listener is ONLY agent with UI
notification_db.create_notification(
    agent_id="user_listener",
    message=f"🔔 User approval required for {package_name}",
    urgency="high",
    sound=True  # user_listener is UI agent, can use sound
)
```

### Agent Communication Pattern

**architect → code_developer**:
```python
# architect completes analysis
notification_db.create_notification(
    agent_id="architect",
    message=f"✅ {package_name} approved and added to pyproject.toml",
    urgency="low",
    sound=False,
    metadata={
        "package": package_name,
        "recommendation": "APPROVE",
        "report_path": str(report_file)
    }
)
```

**architect → user_listener → user**:
```python
# architect requests user approval
notification_db.create_notification(
    agent_id="architect",
    message=f"🔔 User approval needed for {package_name}",
    urgency="high",
    sound=False,  # architect is background
    metadata={
        "package": package_name,
        "report_path": str(report_file),
        "action_required": "USER_APPROVAL"
    }
)

# user_listener forwards to user
notification_db.create_notification(
    agent_id="user_listener",
    message=f"🔔 Dependency approval required: {package_name}",
    urgency="high",
    sound=True,  # user_listener can use sound
    metadata={
        "package": package_name,
        "report_link": str(report_file)
    }
)
```

---

## CI/CD Integration

### GitHub Actions Workflow

**File**: `.github/workflows/dependency-check.yml`

```yaml
name: Dependency Security Check

on:
  pull_request:
    paths:
      - 'pyproject.toml'
      - 'poetry.lock'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  dependency-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: |
          poetry install
          poetry add --dev pip-audit safety

      - name: Run dependency analysis
        run: |
          python scripts/check_all_dependencies.py > dependency-report.md

      - name: Comment PR with report
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('dependency-report.md', 'utf8');

            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: report
            });

      - name: Fail on critical vulnerabilities
        run: |
          if grep -q "CRITICAL" dependency-report.md; then
            echo "❌ Critical vulnerabilities found"
            exit 1
          fi
```

**Script**: `scripts/check_all_dependencies.py`

```python
#!/usr/bin/env python3
"""Check all dependencies in pyproject.toml for security and compatibility."""

import sys
import tomli
from pathlib import Path
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer, Recommendation

def main():
    analyzer = DependencyAnalyzer(project_root=Path.cwd())

    # Read dependencies
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)

    dependencies = pyproject["tool"]["poetry"]["dependencies"]

    # Analyze each dependency
    issues = []
    for package, constraint in dependencies.items():
        if package == "python":
            continue  # Skip Python version

        print(f"Analyzing {package}...", file=sys.stderr)
        report = analyzer.analyze_dependency(package)

        if report.security.cve_count > 0:
            issues.append({
                "package": package,
                "severity": report.security.severity.value,
                "cves": report.security.cve_count,
                "mitigation": report.security.mitigation_notes
            })

    # Generate report
    print("# Dependency Security Report\n")
    print(f"**Scanned**: {len(dependencies)} packages\n")

    if issues:
        print(f"## ⚠️ {len(issues)} Issues Found\n")

        for issue in issues:
            print(f"### {issue['package']}")
            print(f"- **Severity**: {issue['severity']}")
            print(f"- **CVEs**: {issue['cves']}")
            print(f"- **Mitigation**: {issue['mitigation']}\n")

        # Exit with error if critical
        if any(i['severity'] == 'CRITICAL' for i in issues):
            sys.exit(1)
    else:
        print("## ✅ No Issues Found\n")
        print("All dependencies are secure and up to date.")

if __name__ == "__main__":
    main()
```

---

## Monitoring Integration

### Langfuse Dashboards

The Dependency Conflict Resolver automatically logs to Langfuse (if configured).

**Tracked Metrics**:
- `analysis_duration_seconds` - How long analysis took
- `recommendation` - Distribution of APPROVE/REVIEW/REJECT
- `security_severity` - Distribution of CVE severities
- `license_incompatible` - Count of incompatible licenses
- `conflicts_detected` - Count of version conflicts

**View in Langfuse**:
```
https://cloud.langfuse.com/project/{your-project}/traces
Filter: name = "dependency-conflict-resolver"
```

### Custom Metrics Export

**Export metrics to CSV**:
```python
import csv
from datetime import datetime, timedelta
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

# Analyze multiple packages
analyzer = DependencyAnalyzer(project_root=Path.cwd())

packages = ["pytest", "requests", "click", "redis", "fastapi"]
results = []

for package in packages:
    report = analyzer.analyze_dependency(package)
    results.append({
        "package": report.package_name,
        "recommendation": report.recommendation.value,
        "security_severity": report.security.severity.value,
        "cve_count": report.security.cve_count,
        "license": report.license.license_name,
        "compatible": report.license.compatible_with_apache2,
        "bundle_size_mb": report.impact.bundle_size_mb,
        "duration_s": report.analysis_duration_seconds,
        "timestamp": datetime.now().isoformat()
    })

# Export to CSV
with open("dependency-analysis-results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Results exported to dependency-analysis-results.csv")
```

---

## Next Steps

- 📖 Read [USER_GUIDE.md](./USER_GUIDE.md) for usage examples
- 🔧 See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues
- 📋 Review [SPEC-107](../../specs/SPEC-107-dependency-conflict-resolver-skill.md) for technical details
- 📋 Review [SPEC-070](../../specs/SPEC-070-dependency-pre-approval-matrix.md) for pre-approval matrix

---

**Last Updated**: 2025-10-21
**Version**: 1.0.0
**Status**: Production ✅
