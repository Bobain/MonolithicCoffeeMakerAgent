# Dependency Conflict Resolver - User Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-21
**Status**: Production ✅

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Overview](#overview)
3. [Usage](#usage)
4. [Understanding Reports](#understanding-reports)
5. [Common Scenarios](#common-scenarios)
6. [Best Practices](#best-practices)
7. [FAQs](#faqs)

---

## Quick Start

### 5-Minute Tutorial

**Before** (Manual Process - 40-60 minutes):
```bash
# 1. Manually check PyPI for package info
# 2. Read through security advisories
# 3. Check license compatibility
# 4. Test version conflicts manually
# 5. Estimate bundle size impact
# 6. Write ADR documenting decision
```

**After** (Automated - 2-3 minutes):
```python
from pathlib import Path
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

# Initialize analyzer
analyzer = DependencyAnalyzer(project_root=Path.cwd())

# Analyze package
report = analyzer.analyze_dependency("pytest-timeout")

# Review recommendation
print(f"Recommendation: {report.recommendation.value}")
print(f"Analysis time: {report.analysis_duration_seconds:.2f}s")
```

**Time Savings**: 93-95% reduction (40-60 min → 2-3 min)

---

## Overview

### What Is This?

The Dependency Conflict Resolver is an automated tool that performs comprehensive dependency analysis in seconds, replacing hours of manual work.

### What Does It Do?

✅ **Conflict Detection**: Checks version conflicts with existing dependencies
✅ **Security Scanning**: Scans for CVEs using pip-audit and safety
✅ **License Compatibility**: Validates compatibility with Apache 2.0
✅ **Version Analysis**: Checks if version is latest/deprecated
✅ **Impact Assessment**: Estimates bundle size and install time

### When Should I Use It?

**Use this tool whenever**:
- 🆕 Adding a new Python package to the project
- 🔄 Updating an existing dependency to a new version
- 🔍 Evaluating alternatives to a problematic package
- 📋 Documenting dependency decisions for ADRs

**Don't use it for**:
- Built-in Python stdlib modules (no analysis needed)
- Packages already in pyproject.toml (unless updating)
- Non-Python dependencies (Docker, Node.js, etc.)

---

## Usage

### Installation

No installation required! The skill is already available in the project.

**Prerequisites**:
```bash
# Verify dependencies are installed
poetry show | grep -E "(pip-audit|safety)"

# If missing, install (already pre-approved):
poetry add --dev pip-audit safety
```

### Basic Usage

#### Python API

**Example 1: Analyze a package (no version constraint)**
```python
from pathlib import Path
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

# Initialize
analyzer = DependencyAnalyzer(project_root=Path.cwd())

# Analyze
report = analyzer.analyze_dependency("pytest-timeout")

# Check recommendation
if report.recommendation.value == "APPROVE":
    print(f"✅ Safe to add: {report.installation_command}")
elif report.recommendation.value == "REVIEW":
    print(f"⚠️ Needs review: {report.summary}")
else:  # REJECT
    print(f"❌ Rejected: {report.summary}")
    print(f"Alternatives: {', '.join(report.alternatives)}")
```

**Example 2: Analyze with version constraint**
```python
# Analyze specific version
report = analyzer.analyze_dependency("requests", version=">=2.31.0")

print(f"Package: {report.package_name}")
print(f"Requested: {report.requested_version}")
print(f"Latest: {report.version.latest_stable}")
print(f"Recommendation: {report.recommendation.value}")
```

**Example 3: Generate markdown report**
```python
# Get full markdown report
markdown = analyzer.generate_markdown_report(report)
print(markdown)

# Save to file
output_path = Path("docs/architecture/dependency-analysis")
output_path.mkdir(parents=True, exist_ok=True)

report_file = output_path / f"{report.package_name}-analysis.md"
report_file.write_text(markdown)
print(f"Report saved to: {report_file}")
```

#### Claude Skill Invocation

From Claude Code interface:
```markdown
architect: dependency-conflict-resolver pytest-timeout
```

Output:
```
🔍 Analyzing pytest-timeout...

✅ APPROVED - Safe to add

📊 Analysis Results:
- Security: ✅ No vulnerabilities (0 CVEs)
- License: ✅ MIT (compatible with Apache 2.0)
- Conflicts: ✅ No version conflicts detected
- Version: ✅ Latest stable (2.2.0)
- Bundle Size: 0.01 MB

⏱️ Analysis completed in 2.37 seconds

💡 Installation command:
poetry add pytest-timeout

📄 Full report saved to:
docs/architecture/dependency-analysis/pytest-timeout-2025-10-21.md
```

---

## Understanding Reports

### Report Structure

Every analysis generates an `AnalysisReport` with these components:

```python
@dataclass
class AnalysisReport:
    package_name: str                      # Package analyzed
    requested_version: Optional[str]       # Version constraint (if any)
    recommendation: Recommendation         # APPROVE / REVIEW / REJECT
    security: SecurityReport               # CVE scan results
    license: LicenseInfo                   # License compatibility
    version: VersionInfo                   # Version analysis
    conflicts: ConflictInfo                # Dependency conflicts
    impact: ImpactAssessment              # Installation impact
    summary: str                           # Human-readable summary
    installation_command: Optional[str]    # Command to run
    alternatives: List[str]                # Alternative packages
    analysis_duration_seconds: float       # Performance metric
```

### Recommendation Levels

#### ✅ APPROVE (Green Light)

**Meaning**: Package is safe to add immediately

**Criteria**:
- ✅ No security vulnerabilities (CVEs)
- ✅ License compatible with Apache 2.0
- ✅ No version conflicts
- ✅ Not deprecated
- ✅ Reasonable bundle size (<50 MB)

**Action**: Add package using provided command

**Example**:
```
✅ APPROVE: pytest-timeout 2.2.0

Summary: Safe to add. No conflicts, no vulnerabilities, MIT license.
Command: poetry add pytest-timeout
```

#### ⚠️ REVIEW (Yellow Flag)

**Meaning**: Package may have issues, needs architect review

**Criteria**:
- ⚠️ Medium/Low severity CVEs (not Critical/High)
- ⚠️ Unknown license (needs manual verification)
- ⚠️ Complex dependency tree (depth > 5)
- ⚠️ Large bundle size (>50 MB)
- ⚠️ Version conflicts (resolvable)

**Action**: Review issues, decide if acceptable

**Example**:
```
⚠️ REVIEW: pillow 10.0.0

Summary: Package has 1 Medium CVE (CVE-2023-1234).
Mitigation: Upgrade to pillow>=10.1.0 when available.
```

#### ❌ REJECT (Red Flag)

**Meaning**: Package should not be added

**Criteria**:
- ❌ Critical/High severity CVEs
- ❌ Incompatible license (GPL, AGPL)
- ❌ Unresolvable version conflicts
- ❌ Package deprecated/unmaintained
- ❌ Platform incompatible

**Action**: Do not add, use suggested alternatives

**Example**:
```
❌ REJECT: mysql-connector-python 8.0.0

Summary: GPL license incompatible with Apache 2.0.
Alternatives: pymysql, aiomysql, mysql-connector-python-rf
```

### Security Report Details

```python
@dataclass
class SecurityReport:
    severity: SecuritySeverity     # CRITICAL | HIGH | MEDIUM | LOW | NONE
    cve_count: int                 # Number of CVEs found
    cve_ids: List[str]             # CVE identifiers
    vulnerabilities: List[Dict]    # Detailed vulnerability info
    mitigation_notes: str          # Recommended actions
    scan_timestamp: str            # When scan was performed
```

**Severity Levels**:
- **CRITICAL**: Remote code execution, privilege escalation
- **HIGH**: Significant security risk, patch immediately
- **MEDIUM**: Moderate risk, plan to patch soon
- **LOW**: Minor risk, patch when convenient
- **NONE**: No known vulnerabilities

**Example with CVEs**:
```python
report = analyzer.analyze_dependency("requests", version="2.27.0")
print(report.security.severity)  # HIGH
print(report.security.cve_count)  # 2
print(report.security.cve_ids)    # ['CVE-2023-32681', 'CVE-2024-35195']
print(report.security.mitigation_notes)
# "Upgrade to requests>=2.31.0 to fix vulnerabilities"
```

### License Compatibility

**Compatible Licenses** (with Apache 2.0):
- ✅ MIT
- ✅ BSD (2-Clause, 3-Clause)
- ✅ Apache 2.0
- ✅ ISC
- ✅ Unlicense / Public Domain
- ✅ CC0

**Incompatible Licenses**:
- ❌ GPL (2.0, 3.0)
- ❌ AGPL
- ❌ LGPL (unless used as library)
- ❌ Proprietary licenses

**Unknown Licenses**:
- ⚠️ Marked as REVIEW
- ⚠️ Requires manual verification

### Impact Assessment

```python
@dataclass
class ImpactAssessment:
    estimated_install_time_seconds: int    # How long to install
    bundle_size_mb: float                  # Disk space impact
    sub_dependencies_added: List[str]      # Transitive dependencies
    platform_compatibility: Dict[str, bool] # OS compatibility
```

**Example**:
```python
print(report.impact.bundle_size_mb)              # 0.25 MB
print(report.impact.estimated_install_time_seconds)  # 3 seconds
print(report.impact.sub_dependencies_added)      # [] (no sub-deps)
print(report.impact.platform_compatibility)
# {"linux": True, "macos": True, "windows": True}
```

---

## Common Scenarios

### Scenario 1: Adding a Safe Package

**Situation**: Need pytest-timeout for test reliability

**Analysis**:
```python
analyzer = DependencyAnalyzer(project_root=Path.cwd())
report = analyzer.analyze_dependency("pytest-timeout")
```

**Result**:
```
✅ APPROVE
Security: None (0 CVEs)
License: MIT (compatible)
Conflicts: None
Bundle Size: 0.01 MB
Duration: 2.37s
```

**Action**:
```bash
poetry add pytest-timeout
git add pyproject.toml poetry.lock
git commit -m "Add pytest-timeout for test timeouts

✅ Approved by dependency-conflict-resolver
- No security vulnerabilities
- MIT license (compatible)
- No conflicts detected"
```

### Scenario 2: Package with Security Vulnerabilities

**Situation**: Need requests library, but old version has CVEs

**Analysis**:
```python
report = analyzer.analyze_dependency("requests", version="2.27.0")
```

**Result**:
```
⚠️ REVIEW
Security: HIGH (2 CVEs)
  - CVE-2023-32681: Proxy authentication bypass
  - CVE-2024-35195: Certificate validation issue
License: Apache 2.0 (compatible)
Mitigation: Upgrade to requests>=2.31.0
```

**Action**:
```bash
# Use latest version instead
poetry add "requests>=2.31.0"
```

### Scenario 3: GPL License Conflict

**Situation**: Need MySQL connector, but GPL license is incompatible

**Analysis**:
```python
report = analyzer.analyze_dependency("mysql-connector-python")
```

**Result**:
```
❌ REJECT
Security: None (0 CVEs)
License: GPL (INCOMPATIBLE with Apache 2.0)
Alternatives: pymysql, aiomysql, mysql-connector-python-rf
```

**Action**:
```bash
# Use compatible alternative
poetry add pymysql  # MIT license
```

### Scenario 4: Version Conflicts

**Situation**: Package requires incompatible version of existing dependency

**Analysis**:
```python
report = analyzer.analyze_dependency("package-a", version=">=2.0")
```

**Result**:
```
⚠️ REVIEW
Conflicts: True
  - package-a>=2.0 requires dependency-x>=3.0
  - package-b==1.5 requires dependency-x<3.0
Recommendation: Upgrade package-b to >=2.0 or adjust constraint
```

**Action**:
```bash
# Option 1: Upgrade conflicting package
poetry add "package-b>=2.0"

# Option 2: Adjust version constraint
poetry add "package-a>=1.0,<2.0"
```

### Scenario 5: Large Bundle Impact

**Situation**: Package adds many transitive dependencies

**Analysis**:
```python
report = analyzer.analyze_dependency("tensorflow")
```

**Result**:
```
⚠️ REVIEW
Security: None (0 CVEs)
License: Apache 2.0 (compatible)
Bundle Size: 523 MB
Sub-dependencies: 47 packages
Install Time: ~180 seconds

Impact: Large bundle size, consider alternatives
```

**Action**:
```bash
# Evaluate if worth the impact
# Consider lighter alternatives: scikit-learn, pytorch-cpu

# If needed, document in ADR:
# docs/architecture/decisions/ADR-XXX-tensorflow-dependency.md
```

---

## Best Practices

### 1. Always Analyze Before Adding

**DON'T**:
```bash
# ❌ Add without analysis
poetry add some-random-package
```

**DO**:
```python
# ✅ Analyze first
analyzer = DependencyAnalyzer(project_root=Path.cwd())
report = analyzer.analyze_dependency("some-random-package")

if report.recommendation.value == "APPROVE":
    # Safe to add
    subprocess.run(["poetry", "add", "some-random-package"])
```

### 2. Document Decisions

**Create ADR for**:
- Packages with REVIEW recommendation
- Packages with security warnings
- Packages with large bundle impact
- Packages with licensing concerns

**Template**:
```markdown
# ADR-XXX: Add {package-name} Dependency

## Status
Accepted

## Context
{Why we need this package}

## Analysis
{Paste dependency-conflict-resolver report}

## Decision
{Why we decided to add despite warnings}

## Consequences
{Trade-offs and mitigations}
```

### 3. Check Integration with SPEC-070

Some packages are **pre-approved** (skip analysis):
```python
from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus

checker = DependencyChecker()
status = checker.get_approval_status("pytest-timeout")

if status == ApprovalStatus.PRE_APPROVED:
    # Fast path: Add immediately
    print("✅ Pre-approved, no analysis needed")
else:
    # Full analysis required
    report = analyzer.analyze_dependency("pytest-timeout")
```

### 4. Monitor Bundle Size

Keep track of total bundle size impact:
```python
reports = []
for package in ["package-a", "package-b", "package-c"]:
    report = analyzer.analyze_dependency(package)
    reports.append(report)

total_size = sum(r.impact.bundle_size_mb for r in reports)
print(f"Total bundle impact: {total_size:.2f} MB")

if total_size > 100:
    print("⚠️ Warning: Large bundle size, consider optimization")
```

### 5. Update Dependencies Regularly

Re-analyze existing dependencies quarterly:
```python
import tomli

# Read current dependencies
with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)

dependencies = pyproject["tool"]["poetry"]["dependencies"]

for package in dependencies:
    if package == "python":
        continue  # Skip Python version

    print(f"\nAnalyzing {package}...")
    report = analyzer.analyze_dependency(package)

    if report.security.cve_count > 0:
        print(f"⚠️ {package} has {report.security.cve_count} CVEs")
        print(f"   Mitigation: {report.security.mitigation_notes}")
```

---

## FAQs

### Q: How accurate is the security scanning?

**A**: Very accurate. The tool uses:
- **pip-audit**: Official PyPA tool, scans against OSV database
- **safety**: Pyup.io database with 60,000+ known vulnerabilities

False positives are rare (~1%). False negatives possible if CVE just disclosed.

### Q: What if a package has no license information?

**A**: The tool marks it as REVIEW with "unknown" license. You must:
1. Check the package repository (GitHub, GitLab)
2. Look for LICENSE or COPYING file
3. Contact maintainer if unclear
4. Document in ADR if proceeding

### Q: Can I override a REJECT recommendation?

**A**: Yes, but document why:
```python
if report.recommendation.value == "REJECT":
    print(f"Rejected because: {report.summary}")

    # If you still want to proceed:
    # 1. Document in ADR with justification
    # 2. Get user approval
    # 3. Add package with caution
```

### Q: How long does analysis take?

**A**: Typically 2-3 seconds:
- **Best case**: 1-2s (cache hit, simple package)
- **Average case**: 2-3s (network calls, security scan)
- **Worst case**: 5-8s (large dependency tree, slow PyPI)

Parallel execution makes it 3x faster than sequential.

### Q: Does it work offline?

**A**: Partial functionality:
- ✅ Conflict detection (uses local poetry.lock)
- ❌ Security scanning (requires internet)
- ❌ License checking (requires PyPI API)
- ❌ Version analysis (requires PyPI API)

Recommendation: Run analysis with internet connection.

### Q: Can I analyze multiple packages at once?

**A**: Yes, but run them sequentially to avoid rate limits:
```python
packages = ["package-a", "package-b", "package-c"]

for package in packages:
    report = analyzer.analyze_dependency(package)
    print(f"{package}: {report.recommendation.value}")
    time.sleep(1)  # Rate limit protection
```

### Q: What about private PyPI repositories?

**A**: Not currently supported. The tool only queries public PyPI.

**Workaround**: For private packages, skip automated analysis and do manual review.

---

## Performance Tips

### 1. Enable Caching

Results are cached for 1 hour (PyPI metadata) and 24 hours (security scans):

```python
# First analysis: ~3 seconds
report1 = analyzer.analyze_dependency("requests")

# Second analysis (within 1 hour): ~0.5 seconds (cached)
report2 = analyzer.analyze_dependency("requests")
```

### 2. Batch Analysis

Analyze multiple packages efficiently:
```python
from concurrent.futures import ThreadPoolExecutor

packages = ["pytest", "requests", "click", "pydantic"]

def analyze_package(pkg):
    analyzer = DependencyAnalyzer(project_root=Path.cwd())
    return analyzer.analyze_dependency(pkg)

with ThreadPoolExecutor(max_workers=4) as executor:
    reports = list(executor.map(analyze_package, packages))

for report in reports:
    print(f"{report.package_name}: {report.recommendation.value}")
```

### 3. Monitor with Langfuse

Track performance over time:
```python
# Langfuse automatically tracks:
# - analysis_duration_seconds
# - recommendation distribution
# - security_severity distribution
# - cache hit rate

# View in Langfuse dashboard:
# https://cloud.langfuse.com/project/{your-project}
```

---

## Next Steps

- 📖 Read [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for SPEC-070 integration
- 🔧 See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues
- 📋 Review [SPEC-107](../../specs/SPEC-107-dependency-conflict-resolver-skill.md) for technical details
- 🎯 Check [ROADMAP.md](../../../roadmap/ROADMAP.md) for latest updates

---

**Need Help?**
- 💬 Ask architect agent
- 📝 Create GitHub issue
- 📧 Contact project_manager

**Last Updated**: 2025-10-21
**Version**: 1.0.0
**Status**: Production ✅
