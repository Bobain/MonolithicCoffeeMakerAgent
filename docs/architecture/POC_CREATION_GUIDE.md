# POC Creation Guide

**Purpose**: Guide for architect to create Proof of Concept (POC) implementations for complex features
**Last Updated**: 2025-10-19
**Related**: SPEC-050, US-050

---

## Table of Contents

1. [Overview](#overview)
2. [When to Create a POC](#when-to-create-a-poc)
3. [POC Decision Matrix](#poc-decision-matrix)
4. [POC Structure](#poc-structure)
5. [Step-by-Step Process](#step-by-step-process)
6. [Best Practices](#best-practices)
7. [Examples](#examples)
8. [Common Pitfalls](#common-pitfalls)

---

## Overview

### What is a POC?

A **Proof of Concept (POC)** is a minimal working implementation that validates technical feasibility BEFORE full implementation. POCs:

- **Prove technical concepts work** (20-30% of full feature scope)
- **Reduce implementation risk** by discovering issues early
- **Guide code_developer** with concrete working examples
- **Save time** by validating approaches before costly implementation

### Key Principles

1. **Minimal Scope**: 20-30% of full implementation
2. **Working Code**: Must actually run and prove concepts
3. **Basic Testing**: Just enough to validate it works
4. **Not Production**: Explicitly NOT production-ready code
5. **Time-Boxed**: Should take 20-30% of full implementation time

---

## When to Create a POC

### Decision Matrix

Use this matrix to decide if a POC is needed:

| Estimated Effort | Technical Complexity | Create POC? | Rationale |
|------------------|----------------------|-------------|-----------|
| **<1 day** (<8 hours) | Low | ❌ NO | Straightforward, spec sufficient |
| **<1 day** (<8 hours) | Medium | ❌ NO | Spec with code examples sufficient |
| **<1 day** (<8 hours) | High | ⚠️ MAYBE | If novel pattern, consider POC |
| **1-2 days** (8-16 hours) | Low | ❌ NO | Spec sufficient |
| **1-2 days** (8-16 hours) | Medium | ⚠️ MAYBE | If integration risks, consider POC |
| **1-2 days** (8-16 hours) | High | ✅ YES | **POC recommended** |
| **>2 days** (>16 hours) | Low | ❌ NO | Spec sufficient |
| **>2 days** (>16 hours) | Medium | ⚠️ MAYBE | If integration risks, consider POC |
| **>2 days** (>16 hours) | High | ✅ YES | **POC REQUIRED** |

### Complexity Assessment

**Technical Complexity = HIGH** if **ANY** of these apply:

- ✅ Novel architectural pattern (not used in project before)
- ✅ External system integration (GitHub API, Puppeteer, databases)
- ✅ Multi-process or async complexity
- ✅ Performance-critical (caching, rate limiting, optimization)
- ✅ Security-sensitive (authentication, authorization, data protection)
- ✅ Cross-cutting concerns (affects multiple agents)

**Technical Complexity = MEDIUM** if **SOME** of these apply:

- ⚠️ Uses existing patterns but combines them in new ways
- ⚠️ Moderate integration (file I/O, CLI commands)
- ⚠️ Some testing complexity
- ⚠️ Multiple components but straightforward

**Technical Complexity = LOW** if **NONE** of these apply:

- ℹ️ Simple refactor or code cleanup
- ℹ️ Uses well-established patterns
- ℹ️ Single component, no integration
- ℹ️ Easy to test

---

## POC Structure

### Standard Directory Layout

```
docs/architecture/pocs/POC-{number}-{feature-slug}/
├── README.md              # POC overview (REQUIRED)
├── {component1}.py        # Minimal implementation (REQUIRED)
├── {component2}.py        # Additional components (if needed)
├── test_poc.py            # Basic tests proving it works (REQUIRED)
├── requirements.txt       # POC-specific dependencies (OPTIONAL)
└── data/                  # Sample data files (OPTIONAL)
```

### Required Files

1. **README.md**: Complete documentation (use template)
2. **{component}.py**: Minimal working implementation
3. **test_poc.py**: Tests that prove POC works

### Optional Files

1. **requirements.txt**: If POC needs dependencies not in main project
2. **data/**: Sample data for testing
3. **Additional .py files**: If POC has multiple components

---

## Step-by-Step Process

### Phase 1: Planning (10-15% of time)

1. **Review the User Story**:
   - Read the full user story / priority
   - Understand business requirements
   - Identify core technical challenges

2. **Apply Decision Matrix**:
   - Estimate effort (hours)
   - Assess technical complexity (Low/Medium/High)
   - Determine if POC needed

3. **Define POC Scope** (if creating POC):
   - List 3-5 technical concepts to prove
   - Define what's OUT of scope
   - Target 20-30% of full implementation
   - Time-box to 20-30% of full implementation time

4. **Create POC Directory**:
   ```bash
   cd docs/architecture/pocs/
   cp -r POC-000-template/ POC-{number}-{feature-slug}/
   cd POC-{number}-{feature-slug}/
   ```

### Phase 2: Implementation (60-70% of time)

1. **Fill in README Template**:
   - Update header (number, name, date, time budget)
   - List concepts to prove
   - Define what's NOT in scope
   - Document expected outcomes

2. **Implement Minimal Code**:
   - Focus ONLY on proving core concepts
   - Skip error handling edge cases
   - Use print statements for logging (OK for POC)
   - Add comments explaining key decisions
   - Keep it simple and readable

3. **Write Basic Tests**:
   - One test per concept to prove
   - Just prove it works (not comprehensive)
   - Use unittest or pytest
   - Tests should pass!

### Phase 3: Validation (15-20% of time)

1. **Run the POC**:
   ```bash
   python {main_file}.py
   ```
   - Verify output matches expectations
   - Confirm all concepts work

2. **Run the Tests**:
   ```bash
   python test_poc.py
   # OR
   pytest test_poc.py
   ```
   - All tests should pass
   - If tests fail, fix POC or adjust approach

3. **Document Learnings**:
   - Update README with findings
   - Note what worked well
   - Note what needs adjustment
   - Add recommendations for code_developer

### Phase 4: Handoff (5-10% of time)

1. **Finalize README**:
   - Complete all sections
   - Add time tracking
   - Document limitations
   - Write conclusion and recommendation

2. **Link to Technical Spec**:
   - Update SPEC-{number} to reference POC
   - Add link: "See POC-{number} for proof-of-concept"

3. **Commit to Git**:
   ```bash
   git add docs/architecture/pocs/POC-{number}-*/
   git commit -m "feat: Add POC-{number} - {Feature Name}

   Proves {concept 1}, {concept 2}, {concept 3} work correctly.

   Time: {X} hours
   Scope: {Y}% of SPEC-{number}

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

4. **Notify code_developer**:
   - Create notification (if using notification system)
   - Include POC location and key findings

---

## Best Practices

### DO ✅

1. **Keep POCs Minimal**:
   - 20-30% of full feature scope
   - Prove concepts, not build production code
   - Time-box to avoid scope creep

2. **Make POCs Runnable**:
   - Must actually execute and work
   - Include clear "How to Run" instructions
   - Tests must pass

3. **Document Learnings**:
   - What worked well
   - What needs adjustment
   - Recommendations for full implementation

4. **Use POC-000-template**:
   - Start from template for consistency
   - Fill in all sections of README
   - Follow standard structure

5. **Reference POC in Spec**:
   - Link spec to POC directory
   - Explain what POC proves
   - Guide code_developer to use it

### DON'T ❌

1. **Don't Make POCs Production-Ready**:
   - No comprehensive error handling needed
   - No full test coverage needed
   - No optimization needed
   - Basic logging (print) is fine

2. **Don't Spend Too Much Time**:
   - POC should be 20-30% of full time
   - If taking longer, reduce scope
   - Time-box ruthlessly

3. **Don't Skip Testing**:
   - POC must have basic tests
   - Tests must prove concepts work
   - If tests fail, POC is incomplete

4. **Don't Expect code_developer to Copy-Paste**:
   - POC is reference, not template
   - code_developer builds production version
   - POC guides architecture, not implementation

5. **Don't Create POC for Everything**:
   - Use decision matrix
   - Only for complex/risky features
   - Specs sufficient for most work

---

## Examples

### Example 1: US-072 (Multi-Agent Orchestration) ✅ POC Created

**Decision**:
- **Effort**: 15-20 hours (>2 days)
- **Complexity**: **HIGH** (multi-process, IPC, fault tolerance)
- **Result**: ✅ **POC REQUIRED**

**POC**: `docs/architecture/pocs/POC-072-team-daemon/`

**What It Proved**:
- ✅ Subprocess spawning works
- ✅ Message passing works
- ✅ Health monitoring works
- ✅ Graceful shutdown works

**Outcome**: Successfully validated approach, code_developer implemented full version in 24 hours (vs. estimated 32)

**Time Saved**: ~3-4 hours (POC caught design issues early)

---

### Example 2: US-055 (Claude Skills Integration) ✅ POC Required

**Decision**:
- **Effort**: 84-104 hours (>2 days)
- **Complexity**: **VERY HIGH** (new infrastructure, Code Execution Tool, 5+ components)
- **Result**: ✅ **POC REQUIRED**

**POC Should Create**: `docs/architecture/pocs/POC-055-claude-skills/`

**What It Should Prove**:
- ✅ Code Execution Tool integration works
- ✅ SkillLoader can discover and load skills
- ✅ ExecutionController API design sound
- ✅ Security sandboxing effective

**Estimated POC Time**: 4-6 hours (20-30% of minimal infrastructure)

**Expected Time Savings**: 8-12 hours (avoid costly mistakes in 84-104 hour implementation)

---

### Example 3: US-047 (Architect-Only Spec Creation) ❌ No POC

**Decision**:
- **Effort**: 16-24 hours (1-2 days)
- **Complexity**: **MEDIUM** (workflow changes, validation logic)
- **Result**: ❌ **NO POC** (spec sufficient)

**Rationale**:
- Uses existing patterns (agent validation)
- No novel architecture
- No external integrations
- Straightforward workflow changes

**Approach**: Detailed technical spec with code examples was sufficient

---

### Example 4: US-048 (Silent Background Agents) ❌ No POC

**Decision**:
- **Effort**: 4-6 hours (<1 day)
- **Complexity**: **LOW** (parameter validation)
- **Result**: ❌ **NO POC** (spec overkill)

**Rationale**:
- Simple parameter change
- Single file modification
- Well-understood pattern
- No risk

**Approach**: Lightweight spec with examples was sufficient

---

## Common Pitfalls

### Pitfall 1: POC Too Large

**Problem**: POC becomes 50-80% of full implementation, takes too long

**Solution**:
- Ruthlessly scope POC to 20-30%
- Time-box to prevent scope creep
- Focus ONLY on proving core concepts
- Skip edge cases, optimization, polish

### Pitfall 2: POC Code Copied to Production

**Problem**: code_developer copies POC code directly, inherits minimal error handling

**Solution**:
- Add clear warnings in POC README
- Comment POC code: "NOT production ready"
- Explain in README: "Use as reference, not template"
- List limitations prominently

### Pitfall 3: No Tests in POC

**Problem**: POC claims to work but has no proof

**Solution**:
- REQUIRE test_poc.py in every POC
- Tests must prove each concept works
- Run tests before committing POC
- Include test output in README

### Pitfall 4: POC for Simple Features

**Problem**: Creating POCs for straightforward work wastes time

**Solution**:
- Use decision matrix rigorously
- Only create POC for HIGH complexity + >2 day effort
- For simple work, detailed spec is sufficient
- Don't over-engineer

### Pitfall 5: POC Never Validated

**Problem**: POC created but never tested, may not actually work

**Solution**:
- Run POC before finalizing
- Execute all tests
- Document actual output in README
- Fix issues before handoff

---

## Appendix: POC Creation Checklist

### Before Creating POC

- [ ] Reviewed user story / priority fully
- [ ] Estimated effort >2 days (16+ hours)?
- [ ] Technical complexity = High?
- [ ] Decision matrix says POC required or recommended?
- [ ] Defined 3-5 technical concepts to prove
- [ ] Time-boxed to 20-30% of full implementation

### During POC Creation

- [ ] Created POC directory from template
- [ ] Filled in README template completely
- [ ] Implemented minimal working code (20-30% scope)
- [ ] Added basic tests (one per concept)
- [ ] Ran POC and verified it works
- [ ] Ran tests and all pass
- [ ] Documented learnings and recommendations
- [ ] Listed clear limitations

### After POC Creation

- [ ] README complete and accurate
- [ ] All tests passing
- [ ] POC actually runs successfully
- [ ] Referenced POC in technical spec
- [ ] Committed POC to git
- [ ] Linked POC in SPEC: "See POC-{number}"
- [ ] Informed code_developer POC available

---

## Quick Reference

**POC Required When**:
- Effort >2 days (16+ hours) **AND**
- Complexity = High (novel patterns, integrations, multi-process, security)

**POC Scope**:
- 20-30% of full feature
- Prove 3-5 core concepts
- Time-box to 20-30% of full time

**POC Files** (Required):
- `README.md` (complete template)
- `{component}.py` (minimal working code)
- `test_poc.py` (basic tests, all passing)

**POC Success Criteria**:
- Actually runs
- All tests pass
- Proves stated concepts
- Documents learnings
- Guides code_developer

---

**Last Updated**: 2025-10-19
**Maintained By**: architect agent
**Version**: 1.0
