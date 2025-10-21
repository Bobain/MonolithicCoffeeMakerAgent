# SPEC-067: Architect Code Review Process

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: Code quality assurance and architectural governance

---

## Executive Summary

This specification defines the **Architect Code Review Process**, a mandatory quality gate where the architect agent reviews all implementations BEFORE they are deployed or merged to ensure architectural compliance, security, performance, and CFR adherence.

**Key Principles**:
- **architect is ONLY agent authorized to approve**:
  - New dependencies (poetry add)
  - Architectural changes
  - Security-sensitive code
  - Performance-critical implementations
- **Code review BEFORE PR creation**: architect reviews → approves → THEN code_developer creates PR
- **Part of Definition of Done (DoD)**: No feature is complete until architect approves
- **Documented Standards**: Clear review criteria, checklist, and approval process

**Impact**:
- **Higher Code Quality**: Architectural review catches issues before production
- **Security Assurance**: Security-sensitive code vetted by architect
- **Dependency Governance**: Only approved dependencies added (user consent required)
- **CFR Compliance**: Automatic verification of Critical Functional Requirements
- **Knowledge Transfer**: code_developer learns from architect feedback

---

## Problem Statement

### Current Pain Points

**1. No Architectural Oversight**
- code_developer implements features autonomously
- No verification that implementation follows architectural patterns
- Architecture drift over time (inconsistency creeps in)
- Security vulnerabilities introduced unknowingly

**2. Uncontrolled Dependency Addition**
- code_developer CANNOT modify pyproject.toml (architect-only)
- BUT: No clear process for requesting dependencies
- Result: code_developer blocked or adds dependencies incorrectly

**3. No CFR Validation**
- Critical Functional Requirements (CFRs) not verified during implementation
- CFR-007 (context budget <30%) violations discovered late
- CFR-008 (agent boundaries) violated unknowingly
- CFR-009 (error handling) inconsistent across codebase

**4. Inconsistent Code Quality**
- Patterns not consistently applied (mixins vs inheritance)
- Error handling varies (some defensive, some not)
- Performance implications not considered
- No review for security issues

### User Requirements

From architect role definition:
- **Code Review**: architect reviews ALL implementations for quality, security, architecture
- **Dependency Approval**: architect is ONLY agent that can add dependencies (requires user consent)
- **CFR Validation**: Verify compliance with Critical Functional Requirements
- **Approval Authority**: architect gives final approval before deployment
- **Feedback Loop**: code_developer addresses feedback and resubmits for review

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  IMPLEMENTATION PHASE                            │
│  code_developer implements feature based on architect's spec    │
│  - Writes code in coffee_maker/                                 │
│  - Writes tests in tests/                                       │
│  - Updates docs (if needed)                                     │
│  - Runs tests locally (all passing)                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              ARCHITECT CODE REVIEW ⭐ MANDATORY                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Step 1: Automated Pre-Review Checks                      │ │
│  │   - All tests passing (pytest)                             │ │
│  │   - Code formatted (black)                                 │ │
│  │   - Pre-commit hooks passed                                │ │
│  │   - No secrets detected (git-secrets)                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Step 2: Architectural Review                             │ │
│  │   - Follows architectural patterns (mixins, DI)            │ │
│  │   - Consistent with existing code                          │ │
│  │   - No architecture drift                                  │ │
│  │   - Spec compliance (matches SPEC-XXX)                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Step 3: Code Quality Review                              │ │
│  │   - Type hints present (where appropriate)                 │ │
│  │   - Error handling (defensive programming)                 │ │
│  │   - Logging/observability (Langfuse tracking)              │ │
│  │   - Test coverage (>80%)                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Step 4: Security Review                                  │ │
│  │   - No hardcoded secrets                                   │ │
│  │   - Input validation (no SQL injection, XSS)               │ │
│  │   - File access controls (read-only where needed)          │ │
│  │   - Agent isolation (no cross-agent data leakage)          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Step 5: Performance Review                               │ │
│  │   - Algorithms efficient (no O(n²) where O(n) possible)    │ │
│  │   - Caching where appropriate                              │ │
│  │   - Database queries optimized                             │ │
│  │   - Memory usage reasonable                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Step 6: CFR Compliance Review                            │ │
│  │   - CFR-007: Context budget <30% (agent prompts)           │ │
│  │   - CFR-008: Agent boundaries enforced                     │ │
│  │   - CFR-009: Proper error handling and recovery            │ │
│  │   - CFR-013: All work on roadmap branch ONLY               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Step 7: Dependency Review (if applicable)                │ │
│  │   - Security: No CVEs, actively maintained                 │ │
│  │   - Licensing: Compatible (MIT, Apache, BSD)               │ │
│  │   - Necessity: Truly needed or can we implement?           │ │
│  │   - User Approval: Request via user_listener               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Output: APPROVED or CHANGES_REQUESTED                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPROVAL DECISION                             │
│                                                                  │
│  ✅ APPROVED:                                                    │
│    → code_developer creates PR                                  │
│    → project_manager monitors CI/CD                             │
│    → Feature deployed                                           │
│                                                                  │
│  ❌ CHANGES_REQUESTED:                                           │
│    → architect provides detailed feedback                       │
│    → code_developer addresses issues                            │
│    → Re-submit for review (iterative)                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Example

**Scenario**: code_developer implements SPEC-063 (Agent Startup Skills)

```
1. code_developer completes implementation:
   - coffee_maker/skills/skill_loader.py (SkillLoader class)
   - .claude/skills/architect-startup.md (startup skill)
   - tests/unit/test_skill_loader.py (unit tests)
   - All tests passing locally ✅

2. code_developer requests architect review:
   "Implementation complete for SPEC-063. Ready for review.
    Files changed:
    - coffee_maker/skills/skill_loader.py (NEW)
    - tests/unit/test_skill_loader.py (NEW)
    - .claude/skills/architect-startup.md (NEW)
    All tests passing (127 passed, 0 failed).
    No new dependencies added."

3. architect performs automated pre-review:
   ✅ Tests passing
   ✅ Code formatted (black)
   ✅ Pre-commit hooks passed
   ✅ No secrets detected

4. architect performs architectural review:
   ✅ SkillLoader follows singleton pattern (correct)
   ✅ Error handling defensive (raises StartupError with clear messages)
   ✅ CFR-007 validation logic correct (context budget calculation accurate)
   ❓ QUESTION: Why use 4 chars/token estimate? More accurate to use tiktoken?

5. code_developer responds:
   "tiktoken adds dependency (tiktoken package). Simple 4 char/token estimate
    is conservative (slightly overestimates) which is safer for CFR-007.
    Alternative: Add tiktoken as optional dependency (only if available)."

6. architect makes decision:
   ✅ APPROVED (with suggestion)
   "Implementation approved. Suggestion: Add TODO comment to consider tiktoken
    in future if context budget becomes tight. No blocking issues."

7. code_developer creates PR:
   - PR title: "feat: Implement Agent Startup Skills (SPEC-063)"
   - PR description includes architect approval
   - CI/CD runs
   - project_manager monitors PR

8. architect documents approval:
   - Adds entry to docs/architecture/decisions/ADR-012-agent-startup-skills.md
   - Notes: "Reviewed and approved 2025-10-18. No security or performance concerns."
```

---

## Review Checklist

### 1. Automated Pre-Review Checks

**Run Before Human Review**:

```bash
# All tests must pass
pytest
# Exit code: 0 (success)

# Code formatting
black --check .
# Exit code: 0 (no changes needed)

# Pre-commit hooks
pre-commit run --all-files
# Exit code: 0 (all hooks passed)

# Secret detection (optional, if configured)
git secrets --scan
# Exit code: 0 (no secrets found)
```

**If ANY of these fail**: ❌ REJECT immediately, request code_developer fix

### 2. Architectural Review

**Questions to Answer**:

- [ ] Does implementation follow architectural patterns?
  - Mixins for composition (not god classes)
  - Dependency injection (not hardcoded dependencies)
  - Singleton enforcement (AgentRegistry)
- [ ] Consistent with existing code?
  - Naming conventions match
  - File structure logical
  - Import patterns consistent
- [ ] Matches technical specification (SPEC-XXX)?
  - All components implemented
  - APIs match spec
  - Data structures match spec
- [ ] No architecture drift?
  - New patterns justified (documented in ADR)
  - Doesn't introduce inconsistency

### 3. Code Quality Review

**Questions to Answer**:

- [ ] Type hints present?
  - Function signatures type-hinted
  - Complex data structures annotated (dataclasses preferred)
  - mypy would pass (if we ran it)
- [ ] Error handling robust?
  - Try/except blocks around risky operations
  - Custom exceptions for domain errors
  - Error messages helpful (suggest fixes)
  - No bare except clauses
- [ ] Logging/observability?
  - Langfuse @observe decorators on key functions
  - Print statements for user-facing messages
  - Errors logged with context
- [ ] Test coverage adequate?
  - Unit tests for all public functions
  - Integration tests for workflows
  - Edge cases covered (empty input, None values)
  - Target: >80% coverage

### 4. Security Review

**Questions to Answer**:

- [ ] No hardcoded secrets?
  - No API keys in code
  - No passwords in code
  - Config loaded from env vars or .env
  - git-secrets would pass
- [ ] Input validation?
  - User input sanitized
  - SQL injection prevented (use parameterized queries)
  - XSS prevented (escape HTML output)
  - File paths validated (no directory traversal)
- [ ] File access controls?
  - Read-only where appropriate
  - Write permissions checked
  - No arbitrary file access (user provides path → validate first)
- [ ] Agent isolation?
  - Agents don't share mutable state
  - No global variables (except singletons)
  - No cross-agent data leakage

### 5. Performance Review

**Questions to Answer**:

- [ ] Algorithms efficient?
  - No O(n²) where O(n) possible
  - No redundant loops
  - No unnecessary work (memoize expensive calls)
- [ ] Caching where appropriate?
  - Repeated lookups cached (e.g., file reads)
  - Cache invalidation strategy clear
  - LRU cache for bounded memory
- [ ] Database queries optimized?
  - Indexes used
  - No N+1 queries
  - Batch operations where possible
- [ ] Memory usage reasonable?
  - No memory leaks (objects released)
  - Large data structures streamed (not loaded entirely)
  - Generators used for large iterations

### 6. CFR Compliance Review

**Critical Functional Requirements Verification**:

- [ ] **CFR-007: Context Budget <30%**
  - Agent prompt size measured
  - Required docs measured
  - Total <30% of 200K tokens
  - Remediation if violated (split prompt, lazy load docs)
- [ ] **CFR-008: Agent Boundaries Enforced**
  - No direct agent-to-agent calls (must go through orchestrator or user_listener)
  - File ownership respected (architect doesn't modify coffee_maker/)
  - Clear separation of concerns
- [ ] **CFR-009: Proper Error Handling**
  - Errors caught and handled gracefully
  - User-friendly error messages
  - Suggested fixes provided
  - No silent failures
- [ ] **CFR-013: All Work on roadmap Branch**
  - Feature implemented on roadmap branch
  - No feature/* branches created
  - Git workflow followed

### 7. Dependency Review (If Applicable)

**If New Dependencies Added**:

- [ ] **Security Check**
  - No known CVEs (check GitHub security advisories)
  - Actively maintained (last commit <6 months)
  - Trusted maintainer (verified PyPI account)
  - Not deprecated or abandoned
- [ ] **Licensing Check**
  - License compatible with project (MIT, Apache, BSD preferred)
  - No GPL or AGPL (copyleft concerns)
  - License clearly stated in package metadata
- [ ] **Necessity Check**
  - Truly needed or can we implement ourselves?
  - Adds significant value (not reinventing wheel)
  - Minimal dependency footprint (not pulling 50 transitive deps)
  - Alternative libraries considered
- [ ] **User Approval Required**
  - architect creates proposal with justification
  - user_listener presents to user
  - User approves BEFORE poetry add
  - Documented in ADR after approval

---

## Approval Process

### When Architect Approves (✅ APPROVED)

**architect Actions**:
1. Provide approval message to code_developer
2. Document approval (optional: add note to ADR)
3. Unblock code_developer to create PR

**code_developer Actions**:
1. Create PR with implementation
2. Include "Reviewed by: architect" in PR description
3. Proceed with deployment process

**project_manager Actions**:
1. Monitor PR status
2. Track CI/CD results
3. Verify DoD after deployment

**Approval Message Template**:
```
✅ APPROVED: [Feature Name]

Architectural Review Complete:
- Architectural compliance: ✅ Follows patterns
- Code quality: ✅ Well-structured, type hints, tests
- Security: ✅ No issues detected
- Performance: ✅ Efficient algorithms, caching used
- CFR compliance: ✅ All CFRs verified
- Dependencies: [N/A or "Approved: package_name"]

Notes:
- [Any suggestions for future improvements]
- [Any observations worth noting]

You may proceed with PR creation.

Reviewed by: architect
Date: 2025-10-18
```

### When Architect Requests Changes (❌ CHANGES_REQUESTED)

**architect Actions**:
1. Provide detailed feedback with specific issues
2. Suggest fixes or alternatives
3. Block PR creation until addressed

**code_developer Actions**:
1. Read feedback carefully
2. Address each issue
3. Re-submit for review (may iterate multiple times)

**Feedback Message Template**:
```
❌ CHANGES_REQUESTED: [Feature Name]

Issues Found:

1. **Architectural Issue**: [Description]
   - Problem: [What's wrong]
   - Impact: [Why it matters]
   - Fix: [How to resolve]
   - Example: [Code example if helpful]

2. **Code Quality Issue**: [Description]
   - Problem: [What's wrong]
   - Impact: [Why it matters]
   - Fix: [How to resolve]

3. **Security Concern**: [Description]
   - Problem: [What's wrong]
   - Impact: [Risk level: LOW/MEDIUM/HIGH/CRITICAL]
   - Fix: [How to resolve]

4. **Performance Issue**: [Description]
   - Problem: [What's wrong]
   - Impact: [Performance penalty]
   - Fix: [How to optimize]

5. **CFR Violation**: [Which CFR]
   - Problem: [What's violated]
   - Impact: [Why it's critical]
   - Fix: [How to comply]

Please address these issues and re-submit for review.

Reviewed by: architect
Date: 2025-10-18
```

### When Dependencies Needed (🔒 REQUIRES_USER_APPROVAL)

**Special Process for Dependencies**:

```
1. code_developer realizes dependency needed:
   "Implementation blocked: Need 'networkx' package for dependency graph analysis"

2. code_developer delegates to architect:
   "Request dependency approval: networkx
    Purpose: Dependency graph analysis in WorkflowOptimizer
    Alternatives considered: Implement graph algorithms manually (3+ days work)"

3. architect evaluates dependency:
   - Security: ✅ No CVEs, last commit 2025-09, trusted maintainer
   - Licensing: ✅ BSD-3-Clause (compatible)
   - Necessity: ✅ Graph algorithms complex, not worth reimplementing
   - Size: ✅ 2.5MB, few transitive dependencies

4. architect creates proposal for user:
   "Dependency Approval Request: networkx

    Purpose: Dependency graph analysis for Orchestrator workflow optimization
    License: BSD-3-Clause (compatible)
    Security: No known vulnerabilities, actively maintained
    Size: 2.5MB
    Alternatives: Implement graph algorithms manually (~3 days work)

    Recommendation: APPROVE

    This package provides well-tested graph algorithms (topological sort,
    cycle detection) needed for workflow optimization. Reimplementing would
    be time-consuming and error-prone.

    Approve? [y/n]"

5. User responds via user_listener: "y"

6. architect adds dependency:
   poetry add networkx

7. architect documents decision:
   Create ADR-014-use-networkx-for-workflow-optimization.md

8. architect unblocks code_developer:
   "Dependency approved and added: networkx==3.2.1
    You may proceed with implementation."
```

---

## Integration with Git Workflow

### Code Review BEFORE PR Creation

**Standard Workflow**:

```
1. code_developer implements feature on roadmap branch
2. code_developer runs tests locally (all passing)
3. code_developer requests architect review ← BEFORE CREATING PR
4. architect reviews code
5. If approved:
   → code_developer creates PR
   → CI/CD runs automatically
   → project_manager monitors PR
6. If changes requested:
   → code_developer fixes issues
   → Re-submit to architect (goto step 4)
```

**Why Review BEFORE PR?**
- Avoid wasting CI/CD resources on code that needs rework
- Faster feedback loop (no waiting for CI to fail)
- architect can catch issues that CI can't (architectural problems)

### Commit Message Conventions

**After Architect Approval**:

```bash
git add .
git commit -m "feat: Implement agent startup skills (SPEC-063)

- Add SkillLoader class for loading Claude Code Skills
- Add CFR-007 validation in startup skills
- Add health checks for agent initialization
- Add unit tests (>80% coverage)

Architectural review: ✅ APPROVED by architect (2025-10-18)
All tests passing: 127 passed, 0 failed
No new dependencies added

Addresses: SPEC-063
Reviewed-by: architect

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Commit Message Must Include**:
- Feat type: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Description of what changed
- Architectural review status: `✅ APPROVED by architect`
- Test status: `All tests passing: X passed, 0 failed`
- Dependencies: `No new dependencies` or `Added: package_name`
- Related spec: `Addresses: SPEC-XXX`
- Reviewed-by: `Reviewed-by: architect`

---

## Review Metrics & SLAs

### Target Response Times

| Review Type | Target SLA | Priority |
|-------------|------------|----------|
| **Critical Bug Fix** | <2 hours | CRITICAL |
| **Security Issue** | <4 hours | HIGH |
| **New Feature** | <24 hours | MEDIUM |
| **Refactoring** | <48 hours | LOW |
| **Documentation** | <48 hours | LOW |

### Review Quality Metrics

**Track These Metrics**:
- **Time to First Review**: How long until architect provides initial feedback?
- **Iterations to Approval**: How many review cycles before approval?
- **Issues Found Per Review**: Number of issues architect catches
- **Issues Missed (Escaped to Production)**: Issues found in production that should've been caught in review

**Success Targets**:
- Time to First Review: <24 hours (MEDIUM priority features)
- Iterations to Approval: <2 iterations on average
- Issues Found Per Review: >3 (architect adding value)
- Issues Missed: <1 per month (high quality bar)

---

## Tools & Automation

### Automated Review Tools (Future Enhancement)

**Potential Automation**:

1. **Linter Integration**
   - mypy (type checking)
   - pylint (code quality)
   - bandit (security scanning)
   - Run automatically before architect review

2. **Test Coverage Reporting**
   - pytest-cov for coverage percentage
   - Auto-reject if <80% coverage

3. **Dependency Security Scanning**
   - Safety (checks for CVEs in dependencies)
   - Pip-audit (official Python tool)
   - Run before architect evaluates new dependencies

4. **CFR Validation Scripts**
   - CFR-007: Script to calculate context budget
   - CFR-008: Script to detect cross-agent calls
   - CFR-009: Script to verify error handling patterns

**Implementation**: Phase 2 (after manual process proven)

---

## Training & Documentation

### For code_developer

**What to Know**:
- architect reviews ALL implementations BEFORE PR
- Review checklist (know what architect looks for)
- How to request dependency approval
- How to respond to feedback
- Iterative process expected (don't take feedback personally)

**Best Practices**:
- Self-review before requesting architect review
- Run automated checks first (tests, formatting, pre-commit)
- Provide context in review request (what changed, why)
- Address feedback thoroughly (don't skip items)
- Ask questions if feedback unclear

### For architect

**What to Know**:
- Review checklist (systematic approach)
- How to provide constructive feedback
- When to approve vs request changes
- Dependency evaluation criteria
- CFR verification methods

**Best Practices**:
- Review promptly (respect SLAs)
- Be specific in feedback (not "this is wrong", but "this violates CFR-007 because...")
- Suggest fixes (not just identify problems)
- Acknowledge good work (positive feedback matters)
- Escalate blockers (if code_developer stuck, help debug)

---

## Examples

### Example 1: Approved Review (No Issues)

**Review Request from code_developer**:
```
Implementation complete: SPEC-062 (Orchestrator Agent Architecture)

Files changed:
- coffee_maker/orchestrator/message_bus.py (NEW)
- coffee_maker/orchestrator/performance_monitor.py (NEW)
- coffee_maker/orchestrator/workflow_optimizer.py (NEW)
- coffee_maker/orchestrator/orchestrator_agent.py (NEW)
- tests/unit/test_orchestrator_message_bus.py (NEW)
- tests/integration/test_orchestrator_workflow.py (NEW)

Tests: 45 new tests added, all passing (172 total, 0 failed)
Dependencies: networkx==3.2.1 (APPROVED by user via architect)
Coverage: 87% (above 80% target)
```

**architect Review Response**:
```
✅ APPROVED: Orchestrator Agent Architecture (SPEC-062)

Architectural Review Complete:

1. **Architectural Compliance**: ✅
   - Message bus follows pub/sub pattern correctly
   - Priority queue implementation solid (uses Python queue.PriorityQueue)
   - Agent integration pattern consistent (subscribe callbacks)
   - No architecture drift detected

2. **Code Quality**: ✅
   - Type hints comprehensive (all public APIs annotated)
   - Error handling defensive (try/except around queue operations)
   - Langfuse tracking present (@observe decorators)
   - Test coverage 87% (above 80% target) ✅

3. **Security**: ✅
   - No secrets detected
   - Agent isolation maintained (agents don't share mutable state)
   - Task routing safe (no data leakage between agents)
   - SQLite file permissions correct (writable only by orchestrator)

4. **Performance**: ✅
   - Queue operations O(log n) (priority queue is heap)
   - Bottleneck detection efficient (runs every 30s, not every task)
   - Memory usage bounded (completed tasks cleared periodically)
   - Workflow optimizer uses networkx efficiently (graph algorithms optimal)

5. **CFR Compliance**: ✅
   - CFR-007: Orchestrator context budget 22% (<30% ✅)
   - CFR-008: Agent boundaries enforced (all communication via message bus)
   - CFR-009: Error handling comprehensive (startup errors, task timeouts)
   - CFR-013: All work on roadmap branch ✅

6. **Dependency**: ✅
   - networkx==3.2.1 previously approved by user (ADR-013)

Notes:
- Excellent implementation, very clean code
- Workflow optimization logic particularly well-designed
- Consider adding circuit breaker pattern for task failures in future iteration (LOW priority)

You may proceed with PR creation.

Reviewed by: architect
Date: 2025-10-18
Time: 14:35 UTC
```

### Example 2: Changes Requested (Issues Found)

**Review Request from code_developer**:
```
Implementation complete: SPEC-063 (Agent Startup Skills)

Files changed:
- coffee_maker/skills/skill_loader.py (NEW)
- .claude/skills/architect-startup.md (NEW)
- tests/unit/test_skill_loader.py (NEW)

Tests: 23 new tests added, all passing
Dependencies: None
```

**architect Review Response**:
```
❌ CHANGES_REQUESTED: Agent Startup Skills (SPEC-063)

Issues Found:

1. **Code Quality Issue: Missing Type Hints**
   - Problem: `_validate_cfr007` method has no type hints
   - Impact: Reduces code readability and prevents mypy validation
   - Fix: Add type hints:
     ```python
     def _validate_cfr007(self, agent_name: str, step: SkillStep) -> None:
         """Validate CFR-007 context budget compliance."""
         ...
     ```

2. **Security Concern: Arbitrary File Read**
   - Problem: `load_skill(skill_name)` doesn't validate skill_name input
   - Impact: HIGH - Could allow directory traversal (e.g., skill_name = "../../../etc/passwd")
   - Fix: Validate skill_name is safe:
     ```python
     def load_skill(self, skill_name: str) -> List[SkillStep]:
         # Validate skill_name (no path separators)
         if "/" in skill_name or "\\" in skill_name or ".." in skill_name:
             raise ValueError(f"Invalid skill name: {skill_name}")

         skill_path = self.skills_dir / f"{skill_name}.md"
         ...
     ```

3. **CFR Violation: CFR-007 Not Enforced Correctly**
   - Problem: CFR-007 validation allows 30.0% exactly, but should be <30%
   - Impact: MEDIUM - Could allow context budget violations at boundary
   - Fix: Change condition:
     ```python
     # Before (WRONG):
     if budget_pct >= 30.0:  # Allows 30.0%

     # After (CORRECT):
     if budget_pct >= 30.0:  # Rejects >=30%
     ```
   Actually this is correct! But add comment to clarify:
   ```python
   # CFR-007: Context budget MUST be <30% (strictly less than, not <=)
   if budget_pct >= 30.0:
       raise CFR007ViolationError(...)
   ```

4. **Code Quality Issue: Missing Test for Edge Case**
   - Problem: No test for skill file not found scenario
   - Impact: LOW - Error handling not verified
   - Fix: Add test:
     ```python
     def test_load_skill_not_found():
         """Test skill loader handles missing skill file."""
         loader = SkillLoader()
         with pytest.raises(FileNotFoundError):
             loader.load_skill("nonexistent-skill")
     ```

Please address these 4 issues and re-submit for review.

Priority: Issue #2 (Security) is HIGH priority - must fix before approval.

Reviewed by: architect
Date: 2025-10-18
Time: 10:22 UTC
```

### Example 3: Dependency Approval Process

**code_developer Request**:
```
Implementation blocked: SPEC-062 (Orchestrator)

Need dependency: networkx
Purpose: Dependency graph analysis for workflow optimization
Required for: WorkflowOptimizer.analyze_dependencies()

Alternatives considered:
1. Implement graph algorithms manually:
   - Topological sort
   - Cycle detection
   - ~3 days work
   - Risk of bugs in complex algorithms

2. Use simpler approach (no graph):
   - Miss optimization opportunities
   - No cycle detection (risk of infinite loops)
   - Suboptimal scheduling

Recommendation: Use networkx (industry-standard, well-tested)
```

**architect Evaluation**:
```
Dependency Evaluation: networkx

1. **Security Check**: ✅
   - No known CVEs (checked GitHub security advisories)
   - Last commit: 2025-09-15 (active maintenance)
   - Trusted maintainer: NetworkX Developers
   - PyPI verified: ✅

2. **Licensing Check**: ✅
   - License: BSD-3-Clause
   - Compatible with our project: YES
   - No copyleft concerns: YES

3. **Necessity Check**: ✅
   - Truly needed: YES (graph algorithms complex)
   - Adds significant value: YES (saves 3 days work, reduces bug risk)
   - Dependency footprint: ACCEPTABLE (networkx + numpy + scipy)
   - Alternatives considered: Manual implementation (rejected: too complex)

4. **User Approval**: REQUIRED
   - Creating proposal for user...
```

**architect Proposal to User (via user_listener)**:
```
🔒 Dependency Approval Request: networkx

Purpose: Dependency graph analysis for Orchestrator workflow optimization
Version: networkx==3.2.1
License: BSD-3-Clause (compatible)
Security: No known vulnerabilities, actively maintained (last commit 2025-09-15)
Size: 2.5MB + dependencies (numpy, scipy)

Alternatives Considered:
1. Implement graph algorithms manually:
   - Pros: No dependency
   - Cons: ~3 days work, risk of bugs in complex algorithms
   - Verdict: Not recommended (reinventing wheel)

2. Use simpler approach without graph:
   - Pros: No dependency
   - Cons: Miss optimization opportunities, no cycle detection
   - Verdict: Defeats purpose of Orchestrator

Recommendation: APPROVE

This package provides well-tested, industry-standard graph algorithms
(topological sort, cycle detection, shortest path) needed for workflow
optimization. Reimplementing would be time-consuming, error-prone, and
not add value beyond what networkx provides.

Dependencies Added:
- networkx==3.2.1 (2.5MB)
- numpy==1.26.2 (already in project)
- scipy==1.11.4 (already in project)

Approve? [y/n]
```

**User Response (via user_listener)**:
```
y
```

**architect Actions After Approval**:
```bash
# 1. Add dependency
poetry add networkx==3.2.1

# 2. Verify installation
poetry show networkx
# networkx                     3.2.1    Python package for creating and manipulating graphs and networks

# 3. Create ADR
cat > docs/architecture/decisions/ADR-013-use-networkx-for-workflow-optimization.md << 'EOF'
# ADR-013: Use NetworkX for Workflow Optimization

**Status**: Accepted
**Date**: 2025-10-18
**Author**: architect agent

## Context

The Orchestrator agent (SPEC-062) requires dependency graph analysis
for workflow optimization. Specifically:
- Topological sort (find valid execution order)
- Cycle detection (detect circular dependencies)
- Graph traversal (find independent tasks)

## Decision

Use NetworkX library (v3.2.1) for graph algorithms.

## Consequences

### Positive
- Well-tested, industry-standard library
- Comprehensive graph algorithms (100+ algorithms)
- Saves ~3 days of development time
- Reduces risk of bugs in complex algorithms
- Active maintenance (last commit 2025-09-15)

### Negative
- Adds external dependency (2.5MB)
- Transitive dependencies (numpy, scipy - already in project)

## Alternatives Considered

1. **Implement manually**: Rejected (too complex, time-consuming)
2. **Use simpler approach**: Rejected (defeats purpose of Orchestrator)

## User Approval

- Requested: 2025-10-18 10:30 UTC
- Approved by: User (via user_listener)
- Added: 2025-10-18 10:35 UTC

## References

- SPEC-062: Orchestrator Agent Architecture
- NetworkX Documentation: https://networkx.org/
- License: BSD-3-Clause (compatible)
EOF

# 4. Notify code_developer
echo "✅ Dependency approved and added: networkx==3.2.1

You may proceed with implementation.

ADR created: docs/architecture/decisions/ADR-013-use-networkx-for-workflow-optimization.md

Reviewed by: architect
Date: 2025-10-18
Time: 10:35 UTC"
```

---

## Conclusion

The Architect Code Review Process ensures:

1. **Architectural Integrity**: All code follows established patterns
2. **Security Assurance**: Security-sensitive code vetted before deployment
3. **Dependency Governance**: Only approved dependencies added (user consent)
4. **CFR Compliance**: Critical Functional Requirements automatically verified
5. **Quality Standard**: Consistent code quality across entire codebase

**Key Principle**: architect is the final approval authority for ALL implementations.

**Part of DoD**: No feature is complete until architect approves.

---

**Related Documents**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/agents/architect.md` (architect role definition)
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md` (CFRs)
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/DOCUMENT_OWNERSHIP_MATRIX.md` (file ownership)

**Next Steps**:
1. Review and approve this spec
2. Update all technical specs (SPEC-062 through SPEC-066) to include code review phase ✅ DONE
3. Train code_developer on review process
4. Implement first review (SPEC-062 or SPEC-063)
5. Iterate based on learnings
