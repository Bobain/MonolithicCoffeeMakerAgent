# ADR-013: Dependency Pre-Approval Matrix

**Status**: Accepted

**Date**: 2025-10-18

**Author**: architect agent

**Related Issues**: Team Acceleration Opportunities (Opportunity 5.1)

**Related Specs**: [SPEC-070: Dependency Pre-Approval Matrix](../specs/SPEC-070-dependency-pre-approval-matrix.md)

---

## Context

### Problem

Every dependency addition requires user approval, creating friction and blocking development velocity:

**Current Workflow** (as of 2025-10-18):
```
code_developer needs dependency (e.g., pytest-timeout)
    ↓
Delegates to architect (cannot modify pyproject.toml)
    ↓
architect evaluates dependency (20 min with dependency-conflict-resolver skill)
    ↓
architect requests user approval via user_listener
    ↓
User manually approves (5-10 min wait time)
    ↓
architect runs `poetry add` + creates ADR
    ↓
Total time: 20-30 minutes per dependency
```

**Pain Points**:
1. **Repeated Evaluations**: Common dependencies (pytest, black, ruff) re-evaluated every time
2. **User Friction**: User must approve even "obviously safe" packages (e.g., pytest-mock)
3. **Blocking**: code_developer waits 20-30 min for simple additions
4. **Inconsistency**: Same package may be approved/rejected depending on context

**Quantified Impact**:
- **Frequency**: 5-8 dependency requests/month
- **Time per request**: 20-30 minutes (with skill)
- **Total time**: 100-240 minutes/month (1.7-4 hours/month)
- **Opportunity**: Pre-approval could save 54-86 min/month (0.9-1.4 hrs/month)

### Forces at Play

**Technical**:
- dependency-conflict-resolver skill already reduced time from 120 min → 20 min
- Pre-approval saves *remaining* 20 min for common packages
- Security is paramount - must maintain quality standards

**Business**:
- Development velocity important (Phase 0 acceleration)
- User time is valuable - reduce approval requests
- Trade-off: Speed vs. Control

**Social**:
- Developers want friction-free workflows
- User wants confidence in dependency choices
- architect wants to maintain architectural control

---

## Decision

**We will implement a three-tier dependency approval system with a pre-approved matrix of 63 commonly-used, vetted packages.**

### Three-Tier System

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPENDENCY REQUEST                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ┌─────────────────────────────────┐
              │   DependencyChecker Tool        │
              │  (Automated Classification)     │
              └─────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ PRE-APPROVED │   │   STANDARD   │   │    BANNED    │
│ (Auto-Add)   │   │ (Review+User)│   │   (Reject)   │
└──────────────┘   └──────────────┘   └──────────────┘
        ↓                   ↓                   ↓
  poetry add          Skill Review         Reject with
  (2-5 min)        + User Approval      alternatives
                     (20-30 min)          (immediate)
```

### Tier 1: Pre-Approved (63 packages)

**Criteria**:
- Well-known, widely-used packages (e.g., pytest, black, requests)
- MIT/Apache/BSD license (permissive, compatible with Apache 2.0)
- Active maintenance (commit within last 6 months)
- No known critical CVEs
- <10MB install size (lightweight)
- **NO user approval required** (auto-approve)

**Categories** (10 total):
1. Testing & QA (17 packages): pytest, pytest-cov, pytest-xdist, mypy, etc.
2. Code Formatting (8 packages): black, autoflake, isort, ruff, etc.
3. Observability (6 packages): langfuse, opentelemetry-*, prometheus-client, etc.
4. Performance (5 packages): cachetools, redis, hiredis, diskcache, msgpack
5. CLI & UI (7 packages): click, typer, rich, prompt-toolkit, etc.
6. Data Validation (5 packages): pydantic, marshmallow, jsonschema, etc.
7. HTTP & Networking (4 packages): requests, httpx, urllib3, aiohttp
8. Date & Time (2 packages): python-dateutil, pytz
9. Configuration (3 packages): python-dotenv, pyyaml, toml
10. AI & Language Models (6 packages): anthropic, openai, tiktoken, langchain, etc.

**Total**: 63 pre-approved packages

**Exemption**: pylint (GPL-2.0) exempted as development-only tool (doesn't ship with production code)

### Tier 2: Standard (Existing Workflow)

**Process**:
- architect uses dependency-conflict-resolver skill (15 min)
- architect requests user approval (5-10 min)
- User approves → poetry add + ADR creation
- **Total time**: 20-30 minutes (unchanged)

### Tier 3: Banned (Auto-Reject)

**Criteria**:
- GPL-licensed packages (license conflict with Apache 2.0)
- Unmaintained (last commit >2 years ago)
- High-CVE packages (>5 critical vulnerabilities)
- Heavyweight (>100MB install size)
- Known security issues

**Examples**:
- mysql-connector-python (GPL) → Use pymysql or aiomysql instead
- pyqt5 (GPL) → Use pyside6 or tkinter instead
- nose (unmaintained) → Use pytest instead

**Process**:
- Reject immediately with alternatives
- **Total time**: Immediate (seconds)

---

## Consequences

### Positive Consequences

✅ **Reduced Friction**:
- Pre-approved dependencies add in 2-5 min (vs. 20-30 min)
- No user approval required for common packages
- code_developer can work autonomously for 60-80% of dependencies

✅ **Time Savings**:
- **Per dependency**: 15-25 min saved for pre-approved packages
- **Per month**: 0.9-1.4 hours saved (3-5 pre-approved additions/month)
- **Per year**: 10.8-16.8 hours saved

✅ **Consistency**:
- Standardized dependency choices across team
- Clear rationale for approved vs. rejected packages
- Reduces "why was X approved but not Y?" confusion

✅ **Maintained Quality**:
- Only vetted, well-maintained packages pre-approved
- Security maintained (no GPL, no CVEs, active maintenance)
- architect retains control over architectural decisions

✅ **User Experience**:
- User only approves truly novel dependencies
- Fewer approval requests (5-8/month → 2-3/month)
- User time saved (1-3 hours/month)

### Negative Consequences

⚠️ **Maintenance Burden**:
- Pre-approved list requires quarterly review (2-4 hours/quarter)
- Security monitoring (automated with `safety`, `pip-audit`)
- Version constraint updates as packages evolve

⚠️ **False Sense of Security**:
- Risk: Pre-approved packages could develop vulnerabilities
- Mitigation: Quarterly security audits, automated CVE scanning

⚠️ **Potential for Bloat**:
- Risk: Pre-approved list grows too large (low-quality packages added)
- Mitigation: Strict criteria (well-known, <10MB, permissive license)

⚠️ **Circumvention Risk**:
- Risk: Developers bypass pre-commit hooks (--no-verify)
- Mitigation: CI enforcement (cannot bypass), PR reviews

### Neutral Consequences

🔵 **More Files**:
- New files: dependency_checker.py, check_dependencies.py, SPEC-070, ADR-013
- Slightly more complex codebase
- Trade-off: Complexity for velocity

🔵 **Learning Curve**:
- Developers must learn new workflow (check-dependency command)
- Documentation required (CLAUDE.md updates)
- One-time cost: ~30 min per developer

---

## Alternatives Considered

### Alternative 1: Full Automation (No User Approval Ever)

**Description**: Auto-approve ALL dependencies without user consent

**Pros**:
- Maximum velocity (no approval delays)
- Zero friction for developers

**Cons**:
- ❌ Loss of architectural control (anyone can add anything)
- ❌ Security risk (malicious packages could be added)
- ❌ Dependency bloat (no quality gates)
- ❌ Licensing risk (GPL packages could be added accidentally)

**Why Rejected**: Too risky - security and licensing compliance are non-negotiable. architect must retain veto power over dependencies.

### Alternative 2: No Automation (Full Manual Review)

**Description**: Keep current workflow (user approval for everything)

**Pros**:
- Maximum control (user approves every dependency)
- Highest security (every package manually evaluated)

**Cons**:
- ❌ Slow (20-30 min per dependency)
- ❌ Repeated work (pytest, black, etc. re-evaluated every time)
- ❌ User friction (user approves "obvious" packages)
- ❌ Blocks development velocity

**Why Rejected**: Too slow - dependency-conflict-resolver skill already automated evaluation (120 min → 20 min). Pre-approval is logical next step for common packages.

### Alternative 3: Smaller Pre-Approved List (20-30 packages)

**Description**: Only pre-approve most common packages (pytest, black, etc.)

**Pros**:
- Less maintenance (fewer packages to review quarterly)
- Lower risk (smaller attack surface)

**Cons**:
- ❌ Less impact (only saves time for 40-50% of dependencies)
- ❌ Still blocks development for common packages (requests, redis, etc.)
- ❌ Arbitrary cutoff (why 30 packages instead of 60?)

**Why Rejected**: Modest improvement over full 63-package list, but significantly less impact. 63 packages cover 60-80% of typical dependency needs (vs. 40-50% for 30 packages).

### Alternative 4: Dependency Budgets

**Description**: Give each agent a "dependency budget" (e.g., 5 auto-approvals/month)

**Pros**:
- Encourages thoughtful dependency choices
- Prevents dependency sprawl

**Cons**:
- ❌ Arbitrary limits (why 5 per month?)
- ❌ Complexity (tracking budgets, resetting monthly)
- ❌ Doesn't solve repeated evaluations (pytest still re-evaluated)

**Why Rejected**: Solves wrong problem - issue is *repeated evaluations*, not *total dependency count*. Pre-approval matrix directly addresses repeated evaluations.

---

## Implementation Notes

### Rollout Plan (Week 1)

**Phase 1: Core Implementation** (Days 1-2, 6-7 hours)
1. Create `coffee_maker/utils/dependency_checker.py` (DependencyChecker class)
2. Implement pre-approved packages dict (63 packages)
3. Implement banned packages dict (with alternatives)
4. Create unit tests (100% coverage target)

**Phase 2: Integration** (Days 3-4, 3-4 hours)
1. Create `scripts/check_dependencies.py` (pre-commit hook)
2. Add hook to `.pre-commit-config.yaml`
3. Add CLI command (`poetry run project-manager check-dependency <package>`)
4. Create integration tests

**Phase 3: Documentation** (Day 5, 2.5-3 hours)
1. Create ADR-013 (this document)
2. Update CLAUDE.md (new dependency workflow)
3. Create usage examples

**Total Implementation Time**: 11.5-14 hours

### Integration Points

1. **DependencyChecker Class** (`coffee_maker/utils/dependency_checker.py`):
   - `get_approval_status(package_name)` → ApprovalStatus (PRE_APPROVED, NEEDS_REVIEW, BANNED)
   - `is_pre_approved(package_name, version)` → bool
   - `get_ban_reason(package_name)` → str (why banned)
   - `get_alternatives(package_name)` → List[str] (pre-approved alternatives)
   - `check_pyproject_toml()` → List[str] (unapproved dependencies)

2. **Pre-Commit Hook** (`scripts/check_dependencies.py`):
   - Runs on every commit that modifies pyproject.toml
   - Blocks commit if unapproved dependencies found
   - Provides guidance on approval process

3. **CLI Command** (`poetry run project-manager check-dependency <package>`):
   - Quick way to check if package is pre-approved
   - Shows version constraints, ban reasons, alternatives

4. **CI Integration** (`.github/workflows/daemon-test.yml`):
   - Add dependency check to CI/CD pipeline
   - Prevents bypassing pre-commit hook

### Maintenance Schedule

**Quarterly Review** (architect responsibility, every 3 months):
1. Run security audit (`poetry run safety check`, `poetry run pip-audit`)
2. Check for unmaintained packages (last commit >6 months ago)
3. Review new popular packages (consider adding to pre-approved list)
4. Remove unused pre-approved packages (not in any project)
5. Update version constraints if needed
6. Document changes in ADR-013 history

**Automated Monitoring** (CI/CD):
- Monthly security scans (`safety`, `pip-audit`)
- Automatic alerts for new CVEs in pre-approved packages
- Move vulnerable packages to BANNED immediately

---

## Validation

### Success Metrics

**Quantitative**:
| Metric | Baseline | Target (Month 1) | Target (Month 3) |
|--------|----------|------------------|------------------|
| **Dependency Approval Time** | 20-30 min | 2-5 min (pre-approved) | 2 min (average) |
| **User Approvals Required** | 5-8/month | 2-3/month | 1-2/month |
| **Pre-Approved Usage Rate** | 0% | 60% | 80% |
| **Time Saved per Month** | 0 hrs | 0.9-1.4 hrs | 3-5 hrs |

**Qualitative**:
- ✅ Developer satisfaction (reduced friction)
- ✅ Architectural control maintained (security, quality standards)
- ✅ Consistency (standardized dependency choices)
- ✅ User experience improved (fewer approval requests)

### Reevaluation Triggers

**Re-evaluate if**:
1. **Security incident**: Pre-approved package has critical CVE
   → Move to BANNED immediately, suggest alternatives

2. **Low adoption**: <40% of dependencies are pre-approved after 3 months
   → Expand pre-approved list or investigate barriers

3. **High maintenance burden**: >8 hours/quarter spent on list maintenance
   → Consider reducing list or automating more

4. **User complaints**: User wants more control over pre-approved packages
   → Revert to manual approval for some categories

**Reevaluate in**: 6 months (2025-04-18)

---

## References

- [SPEC-070: Dependency Pre-Approval Matrix](../specs/SPEC-070-dependency-pre-approval-matrix.md) - Complete technical specification
- [Team Acceleration Opportunities](../../architecture/TEAM_ACCELERATION_OPPORTUNITIES.md) - Opportunity 5.1 (dependency pre-approval)
- [dependency-conflict-resolver skill](.claude/skills/dependency-conflict-resolver.md) - Existing dependency evaluation skill
- [Python Package Index (PyPI)](https://pypi.org/) - Source of dependency metadata
- [SPDX License List](https://spdx.org/licenses/) - License compatibility reference

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-18 | Created ADR-013 | architect |
| 2025-10-18 | Status changed to Accepted | architect |
| 2025-10-18 | Implemented DependencyChecker, pre-commit hook, CLI command | architect |

---

## Notes

### Risk 1: Outdated Pre-Approved List

**Risk**: Pre-approved packages become outdated (new CVEs, unmaintained)

**Mitigation**:
- Automated security scanning (monthly with `safety`, `pip-audit`)
- Quarterly manual review (architect responsibility)
- CI integration (alerts for new CVEs)
- Version constraints (pin to major versions, e.g., `>=2.0,<3.0`)

### Risk 2: Circumvention

**Risk**: Developers bypass pre-commit hooks (--no-verify)

**Mitigation**:
- CI enforcement (cannot bypass)
- PR reviews by code_developer
- Team education (explain importance of dependency review)
- Monitoring (track pyproject.toml changes in CI)

### Open Questions

1. **Should we add more categories?**
   - e.g., Database clients (psycopg2, pymongo), Machine Learning (scikit-learn, numpy)
   - Decision: Start with 10 categories (63 packages), expand based on usage patterns

2. **How to handle transitive dependencies?**
   - Pre-approved packages may depend on non-pre-approved packages
   - Decision: Allow transitive dependencies (trust pre-approved packages to vet their dependencies)

3. **What about version conflicts?**
   - Pre-approved package A requires dependency X>=2.0, package B requires X<2.0
   - Decision: dependency-conflict-resolver skill still handles conflicts (part of Tier 2 workflow)

### Future Work

**Phase 2: Automated Security Scanning** (Month 3)
- Integrate `safety` and `pip-audit` into CI/CD
- Automatically move vulnerable packages to BANNED
- Email notifications for new CVEs

**Phase 3: Usage Analytics** (Month 6)
- Track which pre-approved packages are actually used
- Remove unused packages from pre-approved list
- Suggest new packages based on usage patterns

**Phase 4: Langfuse Integration** (Month 12)
- Store pre-approved list in Langfuse (centralized, version-controlled)
- A/B testing of different approval criteria
- Track approval rates, time savings, security incidents

---

**Remember**: Pre-approval balances velocity with control. The goal is to reduce friction for common, safe packages while maintaining architectural oversight for novel dependencies.

**Status**: Accepted ✅
**Implementation**: Complete (Week 1, 11.5-14 hours)
**Rollout**: 2025-10-18

---

**Created**: 2025-10-18
**Author**: architect agent
**Version**: 1.0
