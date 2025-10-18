---
description: Automated dependency evaluation, conflict detection, security scanning, and license verification
---

# Dependency Conflict Resolver Skill

**Purpose**: Accelerate architect's dependency evaluation from 120 min to 20 min (83% reduction)

**Category**: architect productivity + security
**Impact**: 100 min saved per dependency, safer dependency decisions

**Owner**: architect agent (ONLY agent that can modify pyproject.toml)

---

## What This Skill Does

Automates the tedious and error-prone parts of dependency management:
- ✅ Checks version conflicts with existing dependencies
- ✅ Scans for CVEs (Common Vulnerabilities and Exposures)
- ✅ Verifies license compatibility with project license
- ✅ Evaluates package maintenance (last update, active contributors)
- ✅ Analyzes transitive dependencies (dep tree depth, size impact)
- ✅ Suggests 2-3 alternatives from PyPI
- ✅ Auto-generates dependency ADR draft

**architect adds 20%**: Final decision, user approval request, ADR review

---

## When To Use

**architect receives dependency request**:

1. code_developer needs package: "Need 'redis' for caching"
2. architect invokes: `dependency-conflict-resolver` skill
3. Skill generates evaluation report (80% automated)
4. architect reviews report and requests user approval (20% work)
5. Total time: 20 min (vs 120 min manual)

**Frequency**: Every time code_developer requests new Python package

---

## Instructions

### Step 1: Parse Dependency Request

**Input**: Dependency name + purpose from code_developer

**Example**:
```
code_developer: "Need 'redis' package for caching layer implementation"
```

**Extract**:
- Package name: `redis`
- Purpose: "caching layer implementation"
- Version constraint: (optional, e.g., `>=5.0`)

**Output**: Structured dependency request

---

### Step 2: Check Version Conflicts

**Script**: `scripts/version_checker.py`

```bash
python scripts/version_checker.py --package redis --constraint ">=5.0"
```

**Logic**:
1. Read `pyproject.toml` for existing dependencies
2. Fetch package metadata from PyPI JSON API
3. Check if requested version compatible with existing deps
4. Identify conflicts (e.g., `redis>=5.0` conflicts with `celery<5.3`)
5. Suggest resolution (upgrade conflicting package or adjust constraint)

**Output**:
```json
{
  "package": "redis",
  "requested_version": ">=5.0",
  "compatible": true,
  "conflicts": [],
  "latest_version": "5.0.8",
  "recommendation": "Use redis>=5.0,<6.0 for stability"
}
```

**Time**: 30-60s (vs 10-15 min manual)

---

### Step 3: Scan for CVEs

**Script**: `scripts/security_scanner.py`

```bash
python scripts/security_scanner.py --package redis --version 5.0.8
```

**Logic**:
1. Use `safety` package to scan for CVEs
2. Check OSV database (Open Source Vulnerabilities)
3. Fetch GitHub security advisories
4. Rate severity (CRITICAL / HIGH / MEDIUM / LOW)
5. Identify if CVE affects our use case

**Data Sources**:
- Safety DB: https://pyup.io/safety/
- OSV: https://osv.dev/
- GitHub Security Advisory: https://github.com/advisories

**Output**:
```json
{
  "package": "redis",
  "version": "5.0.8",
  "vulnerabilities": [],
  "severity": "NONE",
  "safe_to_use": true,
  "last_scanned": "2025-10-18T16:30:00Z"
}
```

**If CVEs found**:
```json
{
  "vulnerabilities": [
    {
      "id": "CVE-2024-1234",
      "severity": "HIGH",
      "description": "Remote code execution via ...",
      "affected_versions": "<5.0.5",
      "fixed_in": "5.0.5",
      "our_version_affected": false
    }
  ],
  "recommendation": "Use redis>=5.0.5 to avoid CVE-2024-1234"
}
```

**Time**: 1-2 min (vs 20-30 min manual CVE search)

---

### Step 4: Check License Compatibility

**Script**: `scripts/license_checker.py`

```bash
python scripts/license_checker.py --package redis
```

**Logic**:
1. Fetch package metadata from PyPI
2. Extract license (e.g., "BSD-3-Clause")
3. Check compatibility with project license (MIT)
4. Use license compatibility matrix

**License Compatibility Matrix** (MIT project):

| Dependency License | Compatible | Notes |
|-------------------|-----------|-------|
| MIT | ✅ YES | Perfect match |
| BSD-2-Clause, BSD-3-Clause | ✅ YES | Permissive |
| Apache-2.0 | ✅ YES | Permissive |
| ISC | ✅ YES | Permissive |
| MPL-2.0 | ⚠️ CONDITIONAL | File-level copyleft (OK for library) |
| GPL-2.0, GPL-3.0 | ❌ NO | Copyleft (infects project) |
| AGPL-3.0 | ❌ NO | Strong copyleft (avoid) |
| Proprietary | ❌ NO | Licensing restrictions |

**Output**:
```json
{
  "package": "redis",
  "license": "BSD-3-Clause",
  "project_license": "MIT",
  "compatible": true,
  "notes": "BSD-3-Clause is permissive and compatible with MIT"
}
```

**Time**: 30-60s (vs 5-10 min manual license research)

---

### Step 5: Evaluate Package Maintenance

**Script**: `scripts/maintenance_evaluator.py`

```bash
python scripts/maintenance_evaluator.py --package redis
```

**Logic**:
1. Fetch PyPI metadata (upload date, release history)
2. Fetch GitHub repo stats (stars, forks, open issues, last commit)
3. Calculate maintenance score (0-100)

**Maintenance Score Formula**:
```python
def calculate_maintenance_score(package_info):
    score = 0

    # Last release (<6 months: +30, 6-12 months: +20, >12 months: +10)
    days_since_release = (today - package_info["upload_date"]).days
    if days_since_release < 180:
        score += 30
    elif days_since_release < 365:
        score += 20
    else:
        score += 10

    # GitHub stars (>10k: +20, 1k-10k: +15, 100-1k: +10, <100: +5)
    stars = package_info["github_stars"]
    if stars > 10000:
        score += 20
    elif stars > 1000:
        score += 15
    elif stars > 100:
        score += 10
    else:
        score += 5

    # Open issues ratio (<10%: +20, 10-20%: +15, >20%: +10)
    issue_ratio = package_info["open_issues"] / package_info["total_issues"]
    if issue_ratio < 0.1:
        score += 20
    elif issue_ratio < 0.2:
        score += 15
    else:
        score += 10

    # Release frequency (>4/year: +20, 2-4/year: +15, <2/year: +10)
    releases_per_year = package_info["releases_last_year"]
    if releases_per_year > 4:
        score += 20
    elif releases_per_year >= 2:
        score += 15
    else:
        score += 10

    # Contributors (>50: +10, 10-50: +7, <10: +5)
    contributors = package_info["contributors"]
    if contributors > 50:
        score += 10
    elif contributors >= 10:
        score += 7
    else:
        score += 5

    return min(score, 100)
```

**Output**:
```json
{
  "package": "redis",
  "maintenance_score": 95,
  "last_release": "2025-09-15",
  "days_since_release": 33,
  "github_stars": 12500,
  "open_issues": 45,
  "total_issues": 1200,
  "issue_ratio": 0.04,
  "releases_last_year": 6,
  "contributors": 85,
  "verdict": "EXCELLENT (actively maintained)"
}
```

**Verdict Categories**:
- 90-100: **EXCELLENT** (actively maintained, use confidently)
- 70-89: **GOOD** (maintained, safe to use)
- 50-69: **ACCEPTABLE** (maintained but slow, proceed with caution)
- <50: **POOR** (abandoned or unmaintained, avoid)

**Time**: 1-2 min (vs 10-15 min manual research)

---

### Step 6: Analyze Dependency Tree

**Script**: `scripts/dependency_analyzer.py`

```bash
python scripts/dependency_analyzer.py --package redis --version 5.0.8
```

**Logic**:
1. Fetch package dependencies from PyPI metadata
2. Build dependency tree (recursive)
3. Calculate tree depth and breadth
4. Estimate total install size
5. Identify "heavy" dependencies (>10MB)

**Output**:
```json
{
  "package": "redis",
  "version": "5.0.8",
  "direct_dependencies": 2,
  "transitive_dependencies": 5,
  "total_dependencies": 7,
  "tree_depth": 3,
  "estimated_size_mb": 2.8,
  "heavy_dependencies": [],
  "dependency_tree": {
    "redis": {
      "async-timeout": {},
      "typing-extensions": {}
    }
  },
  "verdict": "LIGHTWEIGHT (minimal dependencies)"
}
```

**Verdict Categories**:
- <10 deps, <10MB: **LIGHTWEIGHT** (minimal impact)
- 10-30 deps, 10-50MB: **MODERATE** (acceptable impact)
- >30 deps, >50MB: **HEAVY** (significant impact, justify)

**Time**: 1-2 min (vs 15-20 min manual dependency tree exploration)

---

### Step 7: Find Alternatives

**Script**: `scripts/alternatives_finder.py`

```bash
python scripts/alternatives_finder.py --package redis --purpose "caching"
```

**Logic**:
1. Search PyPI for similar packages (keywords: "caching", "redis")
2. Rank by relevance, popularity, maintenance
3. Compare top 3 alternatives
4. Highlight trade-offs

**Output**:
```json
{
  "requested_package": "redis",
  "purpose": "caching",
  "alternatives": [
    {
      "name": "redis",
      "score": 95,
      "stars": 12500,
      "license": "BSD-3-Clause",
      "size_mb": 2.8,
      "last_release": "2025-09-15",
      "pros": ["Feature-rich", "Well-maintained", "Industry standard"],
      "cons": ["Requires Redis server"]
    },
    {
      "name": "pylibmc",
      "score": 75,
      "stars": 450,
      "license": "BSD-3-Clause",
      "size_mb": 1.2,
      "last_release": "2024-03-10",
      "pros": ["Lightweight", "Fast"],
      "cons": ["Requires memcached server", "Less maintained"]
    },
    {
      "name": "diskcache",
      "score": 70,
      "stars": 2100,
      "license": "Apache-2.0",
      "size_mb": 0.5,
      "last_release": "2025-07-20",
      "pros": ["No external server", "Simple"],
      "cons": ["Disk I/O slower than memory", "Single-machine only"]
    }
  ],
  "recommendation": "redis (best fit for distributed caching)"
}
```

**Time**: 2-3 min (vs 20-30 min manual alternative research)

---

### Step 8: Generate Evaluation Report

**Script**: `scripts/report_generator.py`

```bash
python scripts/report_generator.py \
  --package redis \
  --purpose "caching layer implementation" \
  --version-check results/version_check.json \
  --security-scan results/security_scan.json \
  --license-check results/license_check.json \
  --maintenance results/maintenance.json \
  --dependency-tree results/dependency_tree.json \
  --alternatives results/alternatives.json \
  --output docs/architecture/decisions/ADR-XXX-dependency-redis-draft.md
```

**Output**: ADR draft (80% complete)

```markdown
# ADR-XXX: Use Redis Package for Caching Layer

**Status**: Proposed
**Date**: 2025-10-18
**Author**: architect agent
**Requested By**: code_developer

## Context

code_developer needs a caching layer for [feature X]. Requested `redis` package.

## Decision

Add `redis>=5.0,<6.0` to project dependencies.

## Evaluation Summary

### ✅ Security
- **Vulnerabilities**: None found
- **Latest Version**: 5.0.8 (safe)
- **Severity**: NONE

### ✅ License Compatibility
- **Package License**: BSD-3-Clause
- **Project License**: MIT
- **Compatible**: YES (permissive license)

### ✅ Maintenance
- **Score**: 95/100 (EXCELLENT)
- **Last Release**: 2025-09-15 (33 days ago)
- **GitHub Stars**: 12,500
- **Contributors**: 85
- **Verdict**: Actively maintained

### ✅ Version Conflicts
- **Compatible**: YES
- **Conflicts**: None
- **Recommendation**: Use redis>=5.0,<6.0

### ✅ Dependency Impact
- **Direct Dependencies**: 2
- **Transitive Dependencies**: 5
- **Total Size**: 2.8 MB
- **Verdict**: LIGHTWEIGHT

### Alternatives Considered

1. **pylibmc** (score: 75)
   - Pros: Lightweight, fast
   - Cons: Requires memcached, less maintained
   - Rejected: Requires external server setup

2. **diskcache** (score: 70)
   - Pros: No external server, simple
   - Cons: Slower than memory cache, single-machine only
   - Rejected: Not suitable for distributed caching

## Consequences

### Positive
- ✅ Industry-standard caching solution
- ✅ Feature-rich (TTL, pub/sub, data structures)
- ✅ Well-maintained and secure
- ✅ Minimal dependency impact (2.8MB)
- ✅ License compatible with MIT

### Negative
- ⚠️ Requires Redis server setup (add to deployment)
- ⚠️ Adds 2.8MB to install size
- ⚠️ Introduces external dependency (Redis server)

## Recommendation

**✅ APPROVE** - `redis>=5.0,<6.0` is safe, well-maintained, and best fit for distributed caching.

**User Approval Required**: YES (architect policy)

---

**Next Steps** (if user approves):
1. architect runs: `poetry add "redis>=5.0,<6.0"`
2. architect updates this ADR status to "Accepted"
3. code_developer implements caching layer using redis
```

**Time**: 2-3 min (vs 30-40 min manual ADR writing)

---

### Step 9: architect Reviews and Requests User Approval

**architect adds** (20% of work):
- Review auto-generated evaluation
- Add any missing context (security concerns, alternatives)
- Request user approval via user_listener

**architect's approval request**:
```markdown
## Dependency Approval Request

**Package**: redis>=5.0,<6.0
**Purpose**: Caching layer implementation
**Evaluation**: PASSED (security ✅, license ✅, maintenance ✅)

**Summary**:
- Security: No CVEs, latest version safe
- License: BSD-3-Clause (compatible with MIT)
- Maintenance: 95/100 (excellent, actively maintained)
- Size: 2.8MB (lightweight)
- Alternatives: Evaluated pylibmc and diskcache (redis is best fit)

**Recommendation**: ✅ APPROVE

**Trade-offs**:
- ⚠️ Requires Redis server (add to deployment)
- ✅ But: Industry standard, feature-rich, well-supported

Approve? [y/n]
```

**Time**: 5-10 min (architect review + approval request)

---

## Total Time: 20 min (vs 120 min manual)

**Breakdown**:
- Step 1: Parse request (30s)
- Step 2: Version check (30-60s)
- Step 3: CVE scan (1-2 min)
- Step 4: License check (30-60s)
- Step 5: Maintenance eval (1-2 min)
- Step 6: Dependency tree (1-2 min)
- Step 7: Alternatives (2-3 min)
- Step 8: Generate report (2-3 min)
- Step 9: architect review + approval (5-10 min)

**Total**: ~20 min (83% reduction from 120 min)

---

## Scripts

### version_checker.py

**Purpose**: Check version conflicts with existing dependencies

**Usage**:
```bash
python scripts/version_checker.py --package redis --constraint ">=5.0"
```

**Implementation**:
```python
import requests
import toml
from packaging import version, specifiers

def check_version_conflicts(package_name, constraint=None):
    """Check if package version conflicts with existing deps."""

    # Read current dependencies
    pyproject = toml.load("pyproject.toml")
    current_deps = pyproject["tool"]["poetry"]["dependencies"]

    # Fetch package metadata from PyPI
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    metadata = response.json()

    latest_version = metadata["info"]["version"]

    # Check conflicts
    conflicts = []
    for dep_name, dep_constraint in current_deps.items():
        # Check if this dep conflicts with requested package
        # (requires dependency resolution logic)
        pass

    return {
        "package": package_name,
        "latest_version": latest_version,
        "compatible": len(conflicts) == 0,
        "conflicts": conflicts
    }
```

**Dependencies**: `requests`, `toml`, `packaging`

---

### security_scanner.py

**Purpose**: Scan for CVEs using safety database

**Usage**:
```bash
python scripts/security_scanner.py --package redis --version 5.0.8
```

**Implementation**:
```python
import subprocess
import json

def scan_for_cves(package_name, version):
    """Scan package for CVEs using safety."""

    # Use safety package to scan
    result = subprocess.run(
        ["safety", "check", "--json", f"{package_name}=={version}"],
        capture_output=True,
        text=True
    )

    vulnerabilities = json.loads(result.stdout)

    return {
        "package": package_name,
        "version": version,
        "vulnerabilities": vulnerabilities,
        "safe_to_use": len(vulnerabilities) == 0
    }
```

**Dependencies**: `safety`

---

### license_checker.py

**Purpose**: Check license compatibility

**Usage**:
```bash
python scripts/license_checker.py --package redis
```

**Implementation**:
```python
import requests

# License compatibility matrix
COMPATIBLE_LICENSES = {
    "MIT": ["MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC"],
    # Add more project licenses
}

def check_license_compatibility(package_name, project_license="MIT"):
    """Check if package license is compatible with project license."""

    # Fetch package metadata
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    metadata = response.json()

    package_license = metadata["info"]["license"]

    compatible = package_license in COMPATIBLE_LICENSES.get(project_license, [])

    return {
        "package": package_name,
        "license": package_license,
        "project_license": project_license,
        "compatible": compatible
    }
```

**Dependencies**: `requests`

---

### maintenance_evaluator.py

**Purpose**: Evaluate package maintenance score

**Usage**:
```bash
python scripts/maintenance_evaluator.py --package redis
```

**Implementation**:
```python
import requests
from datetime import datetime

def evaluate_maintenance(package_name):
    """Calculate maintenance score (0-100)."""

    # Fetch PyPI metadata
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    metadata = response.json()

    # Fetch GitHub stats (if repo available)
    github_url = metadata["info"]["project_urls"].get("Source")
    # ... fetch GitHub API data ...

    # Calculate score (formula from Step 5)
    score = calculate_maintenance_score(metadata)

    return {
        "package": package_name,
        "maintenance_score": score,
        "verdict": get_verdict(score)
    }
```

**Dependencies**: `requests`, `datetime`

---

### dependency_analyzer.py

**Purpose**: Analyze dependency tree

**Usage**:
```bash
python scripts/dependency_analyzer.py --package redis --version 5.0.8
```

**Implementation**:
```python
import requests

def analyze_dependency_tree(package_name, version):
    """Build dependency tree and calculate size."""

    # Fetch package metadata
    response = requests.get(f"https://pypi.org/pypi/{package_name}/{version}/json")
    metadata = response.json()

    # Get dependencies
    deps = metadata["info"]["requires_dist"] or []

    # Build tree (recursive)
    tree = build_tree(deps)

    # Calculate size
    size_mb = estimate_size(package_name, tree)

    return {
        "package": package_name,
        "total_dependencies": count_deps(tree),
        "estimated_size_mb": size_mb,
        "dependency_tree": tree
    }
```

**Dependencies**: `requests`

---

### alternatives_finder.py

**Purpose**: Find and rank alternative packages

**Usage**:
```bash
python scripts/alternatives_finder.py --package redis --purpose "caching"
```

**Implementation**:
```python
import requests

def find_alternatives(package_name, purpose):
    """Search PyPI for similar packages."""

    # Search PyPI
    response = requests.get(
        f"https://pypi.org/search/?q={purpose}",
        headers={"Accept": "application/json"}
    )

    # Rank results by stars, maintenance, license
    alternatives = rank_alternatives(response.json())

    return {
        "requested_package": package_name,
        "purpose": purpose,
        "alternatives": alternatives[:3]  # Top 3
    }
```

**Dependencies**: `requests`

---

### report_generator.py

**Purpose**: Generate ADR draft from evaluation results

**Usage**:
```bash
python scripts/report_generator.py \
  --package redis \
  --purpose "caching" \
  --output docs/architecture/decisions/ADR-XXX-dependency-redis-draft.md
```

**Implementation**:
```python
def generate_adr_draft(package_name, purpose, evaluation_results):
    """Generate ADR draft from evaluation results."""

    template = load_adr_template()

    # Populate template with evaluation data
    adr_content = template.format(
        package_name=package_name,
        purpose=purpose,
        security=evaluation_results["security"],
        license=evaluation_results["license"],
        maintenance=evaluation_results["maintenance"],
        alternatives=evaluation_results["alternatives"]
    )

    return adr_content
```

---

## Data Structures

### Dependency Request

```python
@dataclass
class DependencyRequest:
    package_name: str
    purpose: str  # Why we need this package
    constraint: str  # e.g., ">=5.0,<6.0"
    requested_by: str  # "code_developer"
```

### Evaluation Result

```python
@dataclass
class EvaluationResult:
    package_name: str
    version: str
    security_score: int  # 0-100
    license_compatible: bool
    maintenance_score: int  # 0-100
    dependency_count: int
    size_mb: float
    alternatives: List[Alternative]
    recommendation: str  # "APPROVE" / "REJECT" / "CONDITIONAL"
    justification: str
```

### Alternative Package

```python
@dataclass
class Alternative:
    name: str
    score: int  # 0-100
    pros: List[str]
    cons: List[str]
    reason_rejected: str
```

---

## Success Metrics

| Metric | Baseline (Manual) | Target (Automated) | Actual (Measured) |
|--------|-------------------|-------------------|-------------------|
| **Time per Dependency** | 120 min | 20 min | TBD |
| **CVE Detection** | 60% (manual search) | 100% (automated scan) | TBD |
| **License Check** | 80% (manual) | 100% (automated) | TBD |
| **Alternative Research** | 1-2 (manual) | 3 (automated) | TBD |
| **ADR Creation** | 30-40 min | 2-3 min | TBD |

---

## Integration with architect Workflow

**Before (Manual - 120 min)**:
1. code_developer requests: "Need redis package"
2. architect manually:
   - Reads pyproject.toml (5 min)
   - Searches PyPI for redis (5 min)
   - Checks for CVEs (20-30 min)
   - Verifies license (5-10 min)
   - Researches maintenance (10-15 min)
   - Analyzes dependencies (15-20 min)
   - Searches alternatives (20-30 min)
   - Writes ADR (30-40 min)
3. Requests user approval (5 min)
4. If approved: Adds dependency (1 min)

**After (Automated - 20 min)**:
1. code_developer requests: "Need redis package"
2. architect runs `dependency-conflict-resolver` skill (10 min):
   - Auto version check (30-60s)
   - Auto CVE scan (1-2 min)
   - Auto license check (30-60s)
   - Auto maintenance eval (1-2 min)
   - Auto dependency tree (1-2 min)
   - Auto alternatives (2-3 min)
   - Auto ADR draft (2-3 min)
3. architect reviews report (5 min)
4. Requests user approval (5 min)
5. If approved: Adds dependency (1 min)

---

## Maintenance

**architect owns**:
- Security scan cache (data/security_scans/)
- License compatibility matrix (scripts/license_matrix.json)
- Maintenance score history (data/maintenance_history.json)

**Update frequency**:
- Security scans: Daily (automated cron)
- License matrix: On policy change
- Maintenance history: After each dependency evaluation

---

## Limitations

**What This Skill CANNOT Do**:
- ❌ Make final approval decision (requires user consent)
- ❌ Assess use case fit (requires domain knowledge)
- ❌ Evaluate performance implications (requires benchmarking)
- ❌ Predict future maintenance (can only assess current state)

**What architect MUST Still Do** (20% of work):
- ✅ Review auto-generated evaluation
- ✅ Add context-specific concerns (e.g., "Redis server setup required")
- ✅ Request user approval
- ✅ Finalize ADR after approval
- ✅ Add dependency to pyproject.toml

---

## Dependencies

**Required**:
- ✅ `safety` package (CVE scanning)
- ✅ `requests` package (PyPI API)
- ✅ `toml` package (pyproject.toml parsing)
- ✅ `packaging` package (version comparison)

**Optional**:
- GitHub API token (for GitHub stats)
- OSV API access (for additional CVE data)

---

## Rollout Plan

### Week 1: Core Scripts (5-7 hrs)
- [ ] Implement version_checker.py
- [ ] Implement security_scanner.py
- [ ] Implement license_checker.py
- [ ] Test on 2-3 real packages

### Week 2: Advanced Scripts (3-5 hrs)
- [ ] Implement maintenance_evaluator.py
- [ ] Implement dependency_analyzer.py
- [ ] Implement alternatives_finder.py
- [ ] Test on 2-3 real packages

### Week 3: Integration (2-3 hrs)
- [ ] Implement report_generator.py
- [ ] Create this skill definition
- [ ] Test full workflow (end-to-end)
- [ ] Measure time savings

---

## Conclusion

**dependency-conflict-resolver skill** reduces dependency evaluation time by 83% (120 min → 20 min) by automating:
- Version conflict detection (5 min → 30-60s)
- CVE scanning (20-30 min → 1-2 min)
- License verification (5-10 min → 30-60s)
- Maintenance evaluation (10-15 min → 1-2 min)
- Dependency analysis (15-20 min → 1-2 min)
- Alternative research (20-30 min → 2-3 min)
- ADR drafting (30-40 min → 2-3 min)

**architect adds value** (5-10 min): Review, context, user approval request

**ROI**: 1-2 dependency evaluations pays back 8-10 hrs investment

**Recommendation**: Implement immediately to accelerate dependency management

---

**Created**: 2025-10-18
**Author**: architect agent
**Status**: Ready for implementation
