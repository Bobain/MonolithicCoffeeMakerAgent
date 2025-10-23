# Dependency Conflict Resolver Skill

**Agent**: architect
**Category**: Dependency Management
**Time Savings**: 40-60 min → 2-3 min (93-95% reduction)

## Purpose

Automate dependency evaluation with comprehensive analysis:
- Conflict detection (version conflicts, circular dependencies)
- Security scanning (CVE databases via pip-audit and safety)
- License compatibility (Apache 2.0)
- Version analysis (recency, breaking changes, deprecation)
- Impact assessment (bundle size, install time, sub-dependencies)

## Usage

```bash
# Analyze dependency (no version constraint)
poetry run python -c "
from pathlib import Path
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

analyzer = DependencyAnalyzer(Path.cwd())
report = analyzer.analyze_dependency('pytest-timeout')
print(analyzer.generate_markdown_report(report))
"

# Analyze with version constraint
poetry run python -c "
from pathlib import Path
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer

analyzer = DependencyAnalyzer(Path.cwd())
report = analyzer.analyze_dependency('pytest-timeout', '>=2.0.0')
print(analyzer.generate_markdown_report(report))
"
```

## Output

Markdown report with:
- **Recommendation**: APPROVE / REVIEW / REJECT
- **Security**: CVE scan results with severity classification
- **License**: Compatibility with Apache 2.0
- **Conflicts**: Version conflicts, circular dependencies
- **Version**: Latest stable, deprecation status, breaking changes
- **Impact**: Bundle size, install time, sub-dependencies, platform compatibility

## Integration

- Works with SPEC-070 pre-approval matrix
- Logs to Langfuse for observability
- Generates comprehensive markdown reports

## Examples

### Example 1: Safe Package (APPROVE)

```python
from pathlib import Path
from coffee_maker.utils.dependency_analyzer import DependencyAnalyzer, Recommendation

analyzer = DependencyAnalyzer(Path.cwd())
report = analyzer.analyze_dependency("pytest-timeout")

# Expected output:
# - recommendation: APPROVE
# - security: No vulnerabilities
# - license: MIT (compatible)
# - conflicts: None
# - version: Latest stable
# - impact: Minimal (< 1MB, no sub-deps)

if report.recommendation == Recommendation.APPROVE:
    print(f"✅ Safe to add: {report.installation_command}")
    # Output: ✅ Safe to add: poetry add pytest-timeout
```

### Example 2: GPL Package (REJECT)

```python
analyzer = DependencyAnalyzer(Path.cwd())
report = analyzer.analyze_dependency("mysql-connector-python")

# Expected output:
# - recommendation: REJECT
# - license: GPL (incompatible with Apache 2.0)
# - alternatives: ["pymysql", "aiomysql", "mysqlclient"]

if report.recommendation == Recommendation.REJECT:
    print(f"❌ Rejected: {report.summary}")
    print(f"Alternatives: {', '.join(report.alternatives)}")
    # Output:
    # ❌ Rejected: Not recommended: incompatible GPL license. Consider alternatives.
    # Alternatives: pymysql, aiomysql, mysqlclient
```

### Example 3: Package with CVEs (REVIEW)

```python
analyzer = DependencyAnalyzer(Path.cwd())
report = analyzer.analyze_dependency("requests", "==2.27.0")

# Expected output:
# - recommendation: REVIEW
# - security: High severity vulnerabilities found
# - cve_count: 2
# - mitigation: Use with caution, review CVE details

if report.recommendation == Recommendation.REVIEW:
    print(f"⚠️ Needs review: {report.summary}")
    print(f"Security: {report.security.severity.value} ({report.security.cve_count} CVEs)")
    print(f"Mitigation: {report.security.mitigation_notes}")
```

## Technical Details

### Components

1. **ConflictAnalyzer**: Detects version conflicts using Poetry's resolver
2. **SecurityScanner**: Scans for CVEs using pip-audit and safety
3. **LicenseChecker**: Validates license compatibility via PyPI API
4. **VersionAnalyzer**: Analyzes version recency via PyPI API
5. **ImpactAssessor**: Estimates installation impact

### Performance

- **Parallel execution**: All 5 components run concurrently (ThreadPoolExecutor)
- **Target time**: < 3 minutes for typical package
- **Actual time**: 2-10 seconds for most packages (cached PyPI data)
- **Time savings**: 40-60 min manual → 2-3 min automated (93-95% reduction)

### Error Handling

- Graceful degradation if tools unavailable (pip-audit, safety)
- Network error handling with retries
- Timeout protection (3 minutes max)
- Clear error messages for troubleshooting

## Prerequisites

- Python 3.11+
- Poetry 1.8+
- pip-audit (dev dependency)
- safety (dev dependency)

Install with:
```bash
poetry add --group dev pip-audit safety
```

## Observability

- Langfuse tracking with `@observe()` decorator
- Metrics logged:
  - Analysis duration
  - Recommendation type (APPROVE/REVIEW/REJECT)
  - Security severity
  - Conflicts detected
  - License compatibility

## References

- [SPEC-107: Dependency Conflict Resolver Skill](../../../docs/architecture/specs/SPEC-107-dependency-conflict-resolver-skill.md)
- [SPEC-070: Dependency Pre-Approval Matrix](../../../docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md)
- [ADR-013: Dependency Pre-Approval Matrix](../../../docs/architecture/decisions/ADR-013-dependency-pre-approval-matrix.md)
