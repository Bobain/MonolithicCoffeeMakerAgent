# Dependency Conflict Resolver - Troubleshooting Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-21
**Status**: Production ✅

---

## Table of Contents

1. [Common Errors](#common-errors)
2. [Performance Issues](#performance-issues)
3. [Network Problems](#network-problems)
4. [Security Scanner Issues](#security-scanner-issues)
5. [License Detection Problems](#license-detection-problems)
6. [Conflict Resolution](#conflict-resolution)
7. [Integration Issues](#integration-issues)
8. [Debugging Tips](#debugging-tips)

---

## Common Errors

### Error: Package Not Found

**Symptom**:
```
PackageNotFoundError: Package 'non-existent-package' not found on PyPI
```

**Cause**: Package doesn't exist on PyPI or name is misspelled

**Solution**:
```python
# 1. Verify package name on PyPI
# Visit: https://pypi.org/project/{package-name}/

# 2. Check for common typos
analyzer.analyze_dependency("pytest-timeout")  # ✅ Correct
analyzer.analyze_dependency("pytest_timeout")  # ❌ Wrong separator

# 3. Search PyPI for similar packages
import requests
response = requests.get(f"https://pypi.org/search/?q={package_name}")
# Review search results for correct name
```

### Error: Analysis Timeout

**Symptom**:
```
TimeoutError: Analysis exceeded 180 seconds for package 'large-package'
```

**Cause**: Package has extremely large dependency tree or slow network

**Solution**:
```python
# Option 1: Increase timeout (in analyzer source)
# Edit: coffee_maker/utils/dependency_analyzer.py
# Change: timeout=180 → timeout=300

# Option 2: Skip security scan (faster)
analyzer = DependencyAnalyzer(project_root=Path.cwd())
analyzer.security_scanner = None  # Skip slow security scan

report = analyzer.analyze_dependency("large-package")

# Option 3: Analyze in background
import threading

def analyze_async(package):
    analyzer = DependencyAnalyzer(project_root=Path.cwd())
    report = analyzer.analyze_dependency(package)
    print(f"Analysis complete: {report.recommendation.value}")

thread = threading.Thread(target=analyze_async, args=("large-package",))
thread.start()
print("Analysis running in background...")
```

### Error: Version Parsing Failed

**Symptom**:
```
ValueError: Invalid version constraint: '>=2.0.0.1'
```

**Cause**: Invalid version format

**Solution**:
```python
# ❌ Invalid version formats
analyzer.analyze_dependency("package", version=">=2.0.0.1")  # Too many dots
analyzer.analyze_dependency("package", version="~=latest")   # Invalid operator

# ✅ Valid version formats
analyzer.analyze_dependency("package", version=">=2.0.0")
analyzer.analyze_dependency("package", version="^2.0")
analyzer.analyze_dependency("package", version="~=2.0")
analyzer.analyze_dependency("package", version="==2.0.1")

# Use packaging library to validate
from packaging.specifiers import SpecifierSet

try:
    SpecifierSet(">=2.0.0")  # Valid
    SpecifierSet(">=2.0.0.1")  # Raises InvalidSpecifier
except Exception as e:
    print(f"Invalid version: {e}")
```

### Error: Import Error (Langfuse)

**Symptom**:
```
ImportError: No module named 'langfuse'
```

**Cause**: Langfuse not installed (but it's optional)

**Solution**:
```bash
# Langfuse is optional - analyzer works without it
# No action needed if you don't want Langfuse tracking

# To enable Langfuse tracking:
poetry add langfuse

# Verify installation
python -c "import langfuse; print('Langfuse installed')"
```

**Code handles missing Langfuse automatically**:
```python
# No changes needed - analyzer auto-detects Langfuse
analyzer = DependencyAnalyzer(project_root=Path.cwd())

# Works with or without Langfuse
report = analyzer.analyze_dependency("pytest-timeout")
```

---

## Performance Issues

### Analysis Taking Too Long (>30 seconds)

**Expected**: 2-3 seconds
**Actual**: 30+ seconds

**Diagnosis**:
```python
import time
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

analyzer = DependencyAnalyzer(project_root=Path.cwd())

# Time each component
start = time.time()
report = analyzer.analyze_dependency("pytest-timeout")
duration = time.time() - start

print(f"Total duration: {duration:.2f}s")

# Check component times (if logged)
# Look for slow components in Langfuse dashboard
```

**Common Causes & Fixes**:

#### 1. Slow PyPI API

**Symptom**: License/version analysis slow
**Fix**: Use caching or mirror
```python
# Results are cached for 1 hour automatically
# Re-running same analysis should be instant

# Force cache refresh if needed
import requests_cache
requests_cache.clear()
```

#### 2. Slow Security Scan

**Symptom**: Security component takes >10 seconds
**Fix**: Check pip-audit/safety installation
```bash
# Verify tools are installed
pip-audit --version
safety --version

# Update to latest versions
poetry add --dev pip-audit safety --latest

# Or skip security scan temporarily
# (Set analyzer.security_scanner = None)
```

#### 3. Large Dependency Tree

**Symptom**: Conflict analysis slow
**Fix**: Use dry-run optimization
```bash
# Poetry dry-run can be slow for complex trees
# Solution: Cache poetry.lock analysis

# Or analyze incrementally
poetry show --tree > dependency_tree.txt
# Parse dependency_tree.txt instead of running poetry repeatedly
```

---

## Network Problems

### PyPI API Not Responding

**Symptom**:
```
requests.exceptions.ConnectionError: Failed to connect to pypi.org
```

**Diagnosis**:
```bash
# Test PyPI connectivity
curl https://pypi.org/pypi/pytest/json

# Check network proxy settings
env | grep -i proxy

# Test DNS resolution
nslookup pypi.org
```

**Solutions**:

#### 1. Temporary PyPI Outage
```python
# Implement retry with backoff
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        report = analyzer.analyze_dependency("pytest-timeout")
        break
    except requests.exceptions.ConnectionError:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Retry {attempt + 1} in {wait_time}s...")
            time.sleep(wait_time)
        else:
            print("❌ PyPI unreachable after retries")
            raise
```

#### 2. Corporate Proxy
```bash
# Configure proxy for requests
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080

# Or in Python
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'https://proxy.company.com:8080'
```

#### 3. Offline Mode
```python
# Use cached data only
# Analyzer falls back to cached results if network unavailable

# Check cache directory
import requests_cache
cache_dir = requests_cache.get_cache()
print(f"Cache location: {cache_dir}")

# Pre-populate cache for offline use
packages = ["pytest", "requests", "click"]
for package in packages:
    # Analyze with network to populate cache
    analyzer.analyze_dependency(package)

# Now works offline (for 1 hour)
```

---

## Security Scanner Issues

### pip-audit Not Installed

**Symptom**:
```
WARNING: pip-audit not found, skipping CVE scan
```

**Fix**:
```bash
# Install pip-audit
poetry add --dev pip-audit

# Verify installation
pip-audit --version

# Test on a package
pip-audit --requirement <(echo "requests==2.27.0")
```

### safety Not Installed

**Symptom**:
```
WARNING: safety not found, skipping vulnerability scan
```

**Fix**:
```bash
# Install safety
poetry add --dev safety

# Verify installation
safety --version

# Test on a package
safety check --json
```

### False Positive CVEs

**Symptom**:
```
Security: HIGH (1 CVE)
CVE-2023-XXXXX: Fixed in newer version
```

**Diagnosis**:
```bash
# Check if CVE is actually fixed
pip-audit --requirement <(echo "requests==2.31.0")

# Manually verify on PyPI security tab
# Visit: https://pypi.org/project/requests/2.31.0/#security
```

**Workaround**:
```python
# If false positive confirmed, suppress in report
report = analyzer.analyze_dependency("requests", version="2.31.0")

if report.security.cve_count > 0:
    # Manually verify each CVE
    for vuln in report.security.vulnerabilities:
        print(f"CVE: {vuln['cve_id']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Fixed in: {vuln['fixed_version']}")

    # Document false positive in ADR if confirmed
```

### Security Scan Too Slow

**Symptom**: Security scan takes >20 seconds

**Fix**:
```python
# Option 1: Skip security scan temporarily
analyzer.security_scanner = None
report = analyzer.analyze_dependency("package")
print("⚠️ Security scan skipped (manual review required)")

# Option 2: Use faster scanner (pip-audit only)
from coffee_maker.utils.dependency_security_scanner import SecurityScanner

class FastSecurityScanner(SecurityScanner):
    def scan_security(self, package_name, version=None):
        # Only run pip-audit, skip safety
        result = self._run_pip_audit(package_name, version)
        return self._parse_pip_audit_output(result)

analyzer.security_scanner = FastSecurityScanner()
```

---

## License Detection Problems

### License Shows as "Unknown"

**Symptom**:
```
License: Unknown
Type: unknown
Compatible: False (requires manual review)
```

**Cause**: Package doesn't declare license in PyPI metadata

**Solution**:
```python
# Step 1: Check PyPI page manually
# Visit: https://pypi.org/project/{package-name}/

# Step 2: Check package repository (GitHub, GitLab)
import requests

response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
data = response.json()

# Check metadata
print(f"License: {data['info'].get('license', 'Not specified')}")
print(f"Project URL: {data['info'].get('project_url', 'N/A')}")
print(f"Home Page: {data['info'].get('home_page', 'N/A')}")

# Visit repository and look for LICENSE file

# Step 3: Document findings
# If MIT/Apache/BSD → Manually approve
# If GPL/AGPL → Reject
# If unclear → Contact maintainer
```

### License Incorrectly Detected

**Symptom**:
```
License: BSD
Type: permissive
Compatible: True

# But actual license is BSD-4-Clause (incompatible)
```

**Solution**:
```python
# Always verify license manually for critical packages
# Check exact license text, not just name

# Download package and inspect LICENSE file
import subprocess

subprocess.run(["pip", "download", "--no-deps", package_name])
# Extract .whl/.tar.gz and read LICENSE file

# Report incorrect detection as issue if needed
```

### GPL License Not Detected

**Symptom**: GPL package shows as compatible

**Solution**:
```python
# Verify license detection
from coffee_maker.utils.dependency_license_checker import LicenseChecker

checker = LicenseChecker()
license_info = checker.check_license("mysql-connector-python")

print(f"License: {license_info.license_name}")
print(f"Type: {license_info.license_type}")
print(f"Compatible: {license_info.compatible_with_apache2}")

# Expected:
# License: GPL
# Type: copyleft
# Compatible: False

# If showing as compatible, report bug
```

---

## Conflict Resolution

### False Positive Conflicts

**Symptom**:
```
Conflicts: True
package-a>=2.0 conflicts with package-b<2.0
```

**But**: Actually compatible when installed

**Diagnosis**:
```bash
# Test installation manually
poetry add package-a package-b --dry-run

# If succeeds, it's false positive
# If fails, it's real conflict
```

**Solution**:
```python
# Override conflict detection if needed
report = analyzer.analyze_dependency("package-a")

if report.conflicts.has_conflicts:
    # Manually verify
    print(f"Conflicts: {report.conflicts.conflicts}")

    # Test actual installation
    result = subprocess.run(
        ["poetry", "add", "package-a", "--dry-run"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ False positive - no real conflict")
        # Proceed with installation
```

### Circular Dependencies Not Detected

**Symptom**: Analyzer reports no circular dependencies, but they exist

**Diagnosis**:
```bash
# Manually check dependency tree
poetry show --tree | grep -A 10 package-name

# Look for cycles:
# package-a → package-b → package-c → package-a
```

**Solution**:
```python
# Report as issue if circular dependency missed
# Include poetry.lock and dependency tree in bug report
```

### Version Conflict Resolution Fails

**Symptom**:
```
Recommendation: REVIEW
Conflicts: package-a>=2.0 requires dependency-x>=3.0
          package-b==1.5 requires dependency-x<3.0
Resolution: Unable to resolve automatically
```

**Solutions**:

#### Option 1: Upgrade Conflicting Package
```bash
# Check if package-b has newer version
poetry show package-b

# If newer version available
poetry add "package-b>=2.0"  # May resolve conflict
```

#### Option 2: Adjust Version Constraints
```bash
# Use compatible version of package-a
poetry add "package-a>=1.0,<2.0"  # Avoid conflict
```

#### Option 3: Fork and Patch
```bash
# If no resolution possible, fork package-b
git clone https://github.com/author/package-b
cd package-b

# Update dependency in pyproject.toml
# dependency-x = ">=2.0,<4.0"  # Widen constraint

# Install from local fork
poetry add ../package-b
```

---

## Integration Issues

### SPEC-070 Pre-Approval Not Working

**Symptom**: Pre-approved packages still require full analysis

**Diagnosis**:
```python
from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus

checker = DependencyChecker()
status = checker.get_approval_status("pytest-timeout")

print(f"Status: {status}")  # Should be PRE_APPROVED

if status != ApprovalStatus.PRE_APPROVED:
    print("❌ Pre-approval not recognized")
```

**Fix**:
```python
# Check SPEC-070 matrix is loaded
import sys
sys.path.append("coffee_maker/utils")

from dependency_checker import PREAPPROVED_PACKAGES
print(f"Pre-approved packages: {len(PREAPPROVED_PACKAGES)}")

# If empty, check file location
# Expected: coffee_maker/utils/dependency_checker.py

# Verify package is in list
if "pytest-timeout" in PREAPPROVED_PACKAGES:
    print("✅ Package is in pre-approved list")
else:
    print("❌ Package NOT in pre-approved list")
    print("Add to SPEC-070 if appropriate")
```

### Langfuse Not Logging

**Symptom**: Analysis runs but no traces in Langfuse dashboard

**Diagnosis**:
```python
# Check if Langfuse is configured
import os
print(f"LANGFUSE_PUBLIC_KEY: {os.getenv('LANGFUSE_PUBLIC_KEY', 'NOT SET')}")
print(f"LANGFUSE_SECRET_KEY: {os.getenv('LANGFUSE_SECRET_KEY', 'NOT SET')}")
print(f"LANGFUSE_HOST: {os.getenv('LANGFUSE_HOST', 'NOT SET')}")
```

**Fix**:
```bash
# Set environment variables
export LANGFUSE_PUBLIC_KEY="pk-..."
export LANGFUSE_SECRET_KEY="sk-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"

# Or create .env file
echo "LANGFUSE_PUBLIC_KEY=pk-..." >> .env
echo "LANGFUSE_SECRET_KEY=sk-..." >> .env
echo "LANGFUSE_HOST=https://cloud.langfuse.com" >> .env

# Load with python-dotenv
poetry add python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv()"
```

### Notification Not Appearing

**Symptom**: Analysis completes but no notification to user

**Diagnosis**:
```python
from coffee_maker.autonomous.notification_db import NotificationDB

db = NotificationDB()

# Check recent notifications
notifications = db.get_all_notifications(limit=10)
for notif in notifications:
    print(f"{notif['timestamp']}: {notif['message']}")
```

**Fix**:
```python
# Verify notification is created (CFR-009 compliant)
from coffee_maker.autonomous.notification_db import NotificationDB

notification_db = NotificationDB()

# architect (background agent) - MUST use sound=False
notification_db.create_notification(
    agent_id="architect",
    message="Dependency analysis complete",
    urgency="medium",
    sound=False  # CFR-009: Background agents silent
)

# user_listener (UI agent) - can use sound=True
notification_db.create_notification(
    agent_id="user_listener",
    message="Approval required for dependency",
    urgency="high",
    sound=True  # user_listener is UI agent
)
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging

# Set debug level for analyzer
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("coffee_maker.utils.dependency_analyzer")
logger.setLevel(logging.DEBUG)

# Now run analysis with verbose output
analyzer = DependencyAnalyzer(project_root=Path.cwd())
report = analyzer.analyze_dependency("pytest-timeout")

# Output shows detailed component execution:
# DEBUG: Starting dependency analysis for pytest-timeout
# DEBUG: ConflictAnalyzer: No conflicts detected (0.5s)
# DEBUG: SecurityScanner: Scanning with pip-audit (1.2s)
# DEBUG: LicenseChecker: Fetching PyPI metadata (0.3s)
# ...
```

### Inspect Raw Report Data

```python
from dataclasses import asdict

analyzer = DependencyAnalyzer(project_root=Path.cwd())
report = analyzer.analyze_dependency("pytest-timeout")

# Convert to dict for inspection
report_dict = asdict(report)

# Pretty print
import json
print(json.dumps(report_dict, indent=2, default=str))

# Inspect specific components
print(f"Security CVEs: {report.security.cve_ids}")
print(f"License issues: {report.license.issues}")
print(f"Conflicts: {report.conflicts.conflicts}")
```

### Test Individual Components

```python
# Test ConflictAnalyzer separately
from coffee_maker.utils.dependency_conflict_analyzer import ConflictAnalyzer

conflict_analyzer = ConflictAnalyzer(project_root=Path.cwd())
conflicts = conflict_analyzer.check_conflicts("pytest-timeout")
print(f"Conflicts: {conflicts.has_conflicts}")

# Test SecurityScanner separately
from coffee_maker.utils.dependency_security_scanner import SecurityScanner

security_scanner = SecurityScanner()
security_report = security_scanner.scan_security("pytest-timeout")
print(f"CVEs: {security_report.cve_count}")

# Test LicenseChecker separately
from coffee_maker.utils.dependency_license_checker import LicenseChecker

license_checker = LicenseChecker()
license_info = license_checker.check_license("pytest-timeout")
print(f"License: {license_info.license_name}")
```

### Profile Performance

```python
import cProfile
import pstats

# Profile analysis
profiler = cProfile.Profile()
profiler.enable()

analyzer = DependencyAnalyzer(project_root=Path.cwd())
report = analyzer.analyze_dependency("pytest-timeout")

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)  # Top 20 slowest functions
```

### Compare with Manual Check

```bash
# Manual security check
pip-audit --requirement <(echo "pytest-timeout")

# Manual license check
curl https://pypi.org/pypi/pytest-timeout/json | jq '.info.license'

# Manual conflict check
poetry add pytest-timeout --dry-run

# Compare with analyzer results
```

---

## Getting Help

### Check Logs
```bash
# View analyzer logs
tail -f logs/dependency-analyzer.log

# View Langfuse traces
# https://cloud.langfuse.com/project/{your-project}/traces
# Filter: name = "dependency-conflict-resolver"
```

### Run Tests
```bash
# Run analyzer tests
pytest tests/unit/test_dependency_analyzer.py -v

# Run integration tests
pytest tests/integration/test_dependency_analyzer_integration.py -v

# Check test coverage
pytest --cov=coffee_maker.utils.dependency_analyzer --cov-report=html
```

### Report Issues

If problem persists:
1. 📝 Check [GitHub Issues](https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues)
2. 💬 Ask architect agent
3. 📧 Contact project_manager

**Include in bug report**:
- Package name and version
- Full error message
- Python version (`python --version`)
- Poetry version (`poetry --version`)
- OS and platform
- Minimal reproduction example

---

## Common Scenarios

### Scenario 1: Want to Skip Security Scan

```python
# Temporarily disable security scanning
analyzer = DependencyAnalyzer(project_root=Path.cwd())
analyzer.security_scanner = None

report = analyzer.analyze_dependency("package-name")
# Security section will show: "Not scanned"
```

### Scenario 2: Need Faster Analysis

```python
# Use cached results only (no network calls)
# Re-run same analysis within 1 hour

# First run: 2-3 seconds
report1 = analyzer.analyze_dependency("pytest")

# Second run: 0.5 seconds (cached)
report2 = analyzer.analyze_dependency("pytest")
```

### Scenario 3: Offline Analysis

```python
# Pre-populate cache while online
packages = ["pytest", "requests", "click", "redis"]
for pkg in packages:
    analyzer.analyze_dependency(pkg)

# Now works offline (for 1 hour cache TTL)
# Disconnect network and try
report = analyzer.analyze_dependency("pytest")  # Uses cache
```

---

**Last Updated**: 2025-10-21
**Version**: 1.0.0
**Status**: Production ✅
