# Dependency Approval: pyyaml

**Date**: 2025-10-17
**Approver**: User
**Decision**: ✅ **APPROVED**

---

## Dependency Details

**Package**: `pyyaml`
**Version**: Latest stable (to be determined during implementation)
**Purpose**: Parse YAML metadata for Claude Skills
**License**: MIT License (permissive, commercial-friendly)
**Maturity**: Stable, widely used (10M+ downloads/month on PyPI)

---

## Why This Dependency is Needed

Claude Skills use YAML metadata files (`SKILL.md`) to define:
- Skill name and description
- Trigger phrases for automatic invocation
- Parameters and return types
- Dependencies on other skills
- Version information
- Author and maintenance info

**Example SKILL.md**:
```yaml
---
name: test-driven-implementation
description: Implement features using test-driven development
version: 1.0.0
trigger_phrases:
  - "implement with TDD"
  - "test-driven implementation"
  - "write tests first"
parameters:
  - name: spec_file
    type: string
    required: true
  - name: coverage_threshold
    type: float
    default: 0.8
returns:
  type: object
  properties:
    tests_written: integer
    implementation_complete: boolean
    coverage: float
---
```

**Without pyyaml**: Cannot parse skill metadata, skills cannot be discovered or invoked properly

---

## Security Considerations

**PyYAML Security**:
- ✅ Well-maintained project (active development since 2006)
- ✅ MIT License (no legal risks)
- ✅ Wide adoption (used by major projects: Ansible, Docker Compose, Kubernetes configs)
- ✅ Security updates actively maintained
- ⚠️ Past vulnerabilities (CVE-2020-1747) have been patched
- ✅ Using `safe_load()` prevents arbitrary code execution

**Our Usage**:
```python
import yaml

# ✅ SAFE: Only use yaml.safe_load()
with open(skill_metadata_file) as f:
    metadata = yaml.safe_load(f)  # Secure parsing

# ❌ NEVER use yaml.load() - allows arbitrary code execution
```

**Mitigation Strategy**:
- Always use `yaml.safe_load()` (prevents code injection)
- Never parse untrusted YAML files
- Skills only loaded from `.claude/skills/` (controlled directory)
- Validate metadata schema after parsing
- Keep pyyaml updated (dependency monitoring via Dependabot)

---

## Alternatives Considered

### 1. **JSON metadata** (instead of YAML)
**Pros**:
- No external dependency (Python stdlib `json` module)
- Simpler parsing
- More restrictive syntax (less attack surface)

**Cons**:
- Less human-readable (no comments, strict syntax)
- Anthropic Skills standard uses YAML (not JSON)
- Would deviate from Claude Skills conventions

**Decision**: Rejected - YAML is the standard for Skills

### 2. **TOML metadata**
**Pros**:
- Simpler than YAML
- More secure parsing (no code execution risks)
- Good readability

**Cons**:
- Requires additional dependency (`toml` or `tomli`)
- Not the Skills standard
- Less familiar to users

**Decision**: Rejected - Not the standard format

### 3. **Python dict literals**
**Pros**:
- No parsing needed (native Python)
- Extremely fast

**Cons**:
- Security risk (arbitrary code execution via `eval()`)
- Not human-editable (requires Python knowledge)
- Not the Skills standard

**Decision**: Rejected - Security risk and non-standard

---

## Impact Assessment

**Positive Impacts**:
- ✅ Enables Claude Skills integration (750% ROI over 5 years)
- ✅ Follows industry standard (YAML for config files)
- ✅ Human-readable metadata (easy to write and maintain)
- ✅ Minimal overhead (lightweight library, ~100KB)

**Negative Impacts**:
- ⚠️ Adds one external dependency (manageable)
- ⚠️ Requires security vigilance (use `safe_load()` only)
- ⚠️ Maintenance burden (keep updated for security patches)

**Net Impact**: **Strongly Positive** - Essential for Skills, minimal cost

---

## Installation

**Add to pyproject.toml**:
```toml
[tool.poetry.dependencies]
python = "^3.9"
pyyaml = "^6.0"  # Skills metadata parsing
```

**Install**:
```bash
poetry add pyyaml
```

**Verify**:
```python
import yaml
print(yaml.__version__)  # Should show 6.0+
```

---

## Usage Guidelines

**✅ SAFE Usage**:
```python
import yaml

# Load skill metadata
with open('.claude/skills/my-skill/SKILL.md') as f:
    metadata = yaml.safe_load(f)  # SAFE - prevents code execution

# Validate schema
if not isinstance(metadata, dict):
    raise ValueError("Invalid metadata format")
if 'name' not in metadata or 'description' not in metadata:
    raise ValueError("Missing required fields")

# Use metadata
skill_name = metadata['name']
trigger_phrases = metadata.get('trigger_phrases', [])
```

**❌ UNSAFE Usage (NEVER DO THIS)**:
```python
import yaml

# DANGEROUS - allows arbitrary code execution
with open(untrusted_file) as f:
    metadata = yaml.load(f, Loader=yaml.Loader)  # ❌ UNSAFE!
```

**Enforcement**:
- Code review: Verify only `safe_load()` is used
- Static analysis: Add rule to detect unsafe `yaml.load()` calls
- Documentation: GUIDELINE-005 mandates `safe_load()` usage

---

## Monitoring and Maintenance

**Dependency Monitoring**:
- ✅ Dependabot enabled (automatic security alerts)
- ✅ `poetry update pyyaml` monthly
- ✅ Review changelogs for breaking changes
- ✅ Test skill loading after updates

**Security Monitoring**:
- Subscribe to PyYAML security advisories
- Check CVE database monthly
- Update immediately if vulnerabilities discovered

**Version Pinning**:
- Use `^6.0` (allows minor updates, blocks breaking changes)
- Test thoroughly before major version upgrades
- Document any version-specific behavior

---

## Approval Summary

**Decision**: ✅ **APPROVED**

**Justification**:
1. **Essential**: Cannot implement Claude Skills without YAML parsing
2. **Standard**: Industry-standard library (10M+ downloads/month)
3. **Secure**: Using `safe_load()` prevents code execution
4. **Low Risk**: Well-maintained, active security updates
5. **High Value**: Enables 750% ROI Skills integration

**Conditions**:
- ✅ Always use `yaml.safe_load()` (never `yaml.load()`)
- ✅ Only parse files from `.claude/skills/` directory
- ✅ Validate metadata schema after parsing
- ✅ Keep pyyaml updated (Dependabot monitoring)
- ✅ Code review enforcement of safe usage patterns

**Approved By**: User
**Date**: 2025-10-17
**For Priority**: US-055 (Claude Skills Integration - Phase 1)

---

## Next Steps

1. ✅ Add `pyyaml` to `pyproject.toml`
2. ✅ Run `poetry add pyyaml`
3. ✅ Update poetry.lock
4. ✅ Implement SkillLoader with `safe_load()` usage
5. ✅ Add code review checklist item (verify safe_load usage)
6. ✅ Document in GUIDELINE-005 (mandatory safe_load)

---

**Conclusion**: pyyaml dependency approved for Claude Skills Integration. Proceed with implementation following security guidelines.
