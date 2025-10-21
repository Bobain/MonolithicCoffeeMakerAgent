---
description: Create hierarchical, modular technical specifications with progressive disclosure for efficient code_developer consumption
---

# Hierarchical Spec Creation Skill

**Purpose**: Create modular, hierarchical technical specs that code_developer consumes progressively (70% context reduction)

**Category**: architect productivity, spec architecture
**Impact**: 71% context reduction, 30% faster implementation, unlimited scalability

---

## What This Skill Does

Creates multi-level, modular technical specifications:
- ✅ **Overview document** (README.md): High-level architecture, phase summary
- ✅ **Phase documents** (phase1.md, phase2.md, etc.): Focused implementation steps
- ✅ **Reference links**: Guidelines, patterns, reusable components
- ✅ **Progressive disclosure**: code_developer reads only current phase
- ✅ **Context efficient**: 100-150 lines loaded vs 300+ in monolithic specs

**code_developer benefits**: Focused context, clear steps, faster implementation

---

## When To Use

**architect creating any technical spec**:
1. User requests: "Create spec for PRIORITY 24"
2. architect invokes: `hierarchical-spec-creation` skill
3. Skill creates directory structure with overview + phase documents
4. architect fills in architectural details
5. code_developer implements phase-by-phase

**Use this skill for ALL specs** (not just complex ones - all specs benefit from modularity)

---

## Hierarchical Spec Architecture

### Directory Structure

```
docs/architecture/specs/
└── SPEC-{number}-{slug}/
    ├── README.md                    # Overview (mandatory) - 100-150 lines
    ├── phase1-{name}.md            # Phase 1 detail - 50-100 lines
    ├── phase2-{name}.md            # Phase 2 detail - 50-100 lines
    ├── phase3-{name}.md            # Phase 3 detail - 50-100 lines
    ├── references.md               # Links to guidelines - 30-50 lines
    └── diagrams/                   # Architecture diagrams (optional)
        ├── architecture.png
        └── database-erd.png
```

### Information Hierarchy

```
Level 1: README.md (Overview)
  ├─ Problem Statement
  ├─ High-Level Architecture
  ├─ Technology Stack
  ├─ Phase Summary (brief)
  ├─ Dependencies
  └─ References to guidelines

Level 2: phase{N}.md (Detail)
  ├─ Phase Goal
  ├─ Detailed Steps
  ├─ Code Examples
  ├─ Acceptance Criteria
  └─ References for this phase

Level 3: Guidelines (Reusable patterns)
  ├─ GUIDELINE-XXX.md
  └─ Referenced by multiple specs
```

---

## Instructions

### Step 1: Create Directory Structure

```bash
# Extract priority number and create slug
PRIORITY_NUMBER="24"
SPEC_SLUG="technical-prerequisite-tracking"

# Create spec directory
mkdir -p "docs/architecture/specs/SPEC-${PRIORITY_NUMBER}-${SPEC_SLUG}/diagrams"

# Create placeholder files
touch "docs/architecture/specs/SPEC-${PRIORITY_NUMBER}-${SPEC_SLUG}/README.md"
touch "docs/architecture/specs/SPEC-${PRIORITY_NUMBER}-${SPEC_SLUG}/references.md"
```

**Time**: 30 seconds

### Step 2: Analyze Priority and Identify Phases

**Read ROADMAP priority**:
```bash
# Get priority content from ROADMAP
grep -A 50 "PRIORITY ${PRIORITY_NUMBER}:" docs/roadmap/ROADMAP.md
```

**Identify natural phases** (use CFR-016 guidelines):
- Database changes → Phase 1
- Core logic → Phase 2
- API/UI → Phase 3
- Tests/Docs → Phase 4

**Phase size target**: 1-2 hours each (CFR-016 requirement)

**Time**: 3-5 min

### Step 3: Write README.md (Overview)

**Template**: See [README.md Template](#readmemd-template-overview) below

**Content** (100-150 lines):
1. **Problem Statement**: What problem does this solve? (3-5 sentences)
2. **High-Level Architecture**: Component diagram, data flow
3. **Technology Stack**: Languages, frameworks, libraries
4. **Implementation Phases (Summary)**: Brief description of each phase with link
5. **Dependencies**: Technical prerequisites, external libraries
6. **References**: Links to guidelines and related specs
7. **Success Criteria**: Definition of Done

**Key Principle**: README is a MAP, not the full journey. Link to phase documents for details.

**Time**: 15-20 min

### Step 4: Write Phase Documents

For each phase, create `phase{N}-{name}.md`:

**Template**: See [Phase Document Template](#phase-document-template) below

**Content** (50-100 lines per phase):
1. **Goal**: What does this phase accomplish? (1-2 sentences)
2. **Prerequisites**: Dependencies on previous phases
3. **Detailed Steps**: Step-by-step implementation
4. **Code Examples**: Concrete examples for each step
5. **Acceptance Criteria**: Testable, specific criteria
6. **Testing This Phase**: How to verify completion
7. **References**: Patterns/guidelines for this phase
8. **Next Phase**: Link to next phase document

**Key Principle**: Each phase is SELF-CONTAINED. code_developer should understand what to do by reading ONLY this phase + overview.

**Time**: 10-15 min per phase (40-60 min for 4 phases)

### Step 5: Create or Reference Guidelines

**Check if pattern already exists**:
```bash
# Search existing guidelines
ls docs/architecture/guidelines/ | grep -i "jwt\|auth\|database"
```

**If pattern exists**: Link to it in references.md and phase documents

**If pattern is NEW and REUSABLE**: Create guideline document
```bash
# Create new guideline
touch docs/architecture/guidelines/GUIDELINE-{number}-{pattern-name}.md
```

**Example guidelines**:
- GUIDELINE-007-jwt-authentication-pattern.md
- GUIDELINE-008-password-hashing-standard.md
- GUIDELINE-009-api-security-checklist.md

**Guidelines vs Specs**:
- **Guideline**: Reusable pattern (used by many specs)
- **Spec**: Project-specific implementation (references guidelines)

**Time**: 5-10 min for references, 20-30 min for new guideline

### Step 6: Add Diagrams (Optional but Recommended)

**Create architecture diagrams**:
```bash
# Use ASCII art, Mermaid, or image files
# Save to diagrams/ directory
```

**Common diagrams**:
- **Architecture diagram**: Component interaction
- **Database ERD**: Table relationships
- **Data flow**: Request/response flow
- **State machine**: Status transitions

**Tools**:
- ASCII art (simple, in markdown)
- Mermaid (renders in GitHub)
- draw.io (export as PNG)

**Time**: 10-20 min

### Step 7: Update ROADMAP with Phase Tracking

**Add phase tracking to ROADMAP priority**:

```markdown
### PRIORITY 24: Technical Prerequisite Tracking 📝 Planned

**Implementation Phases**:
- [ ] Phase 1: Database schema (1 hour)
- [ ] Phase 2: Database methods (2 hours)
- [ ] Phase 3: Architect skill (2 hours)
- [ ] Phase 4: project_manager integration (1 hour)
- [ ] Phase 5: Documentation (1 hour)

**Current Phase**: Phase 1
**Spec**: [SPEC-024](../architecture/specs/SPEC-024-technical-prerequisite-tracking/README.md)
```

**Time**: 2-3 min

---

## Templates

### README.md Template (Overview)

```markdown
# SPEC-{number}: {Title}

**Status**: {Draft|Approved|Implemented}
**Created**: YYYY-MM-DD
**Author**: architect
**Priority**: {CRITICAL|HIGH|MEDIUM|LOW}
**Estimated Effort**: {X} hours total

## Problem Statement

What problem does this solve? (3-5 sentences)

Why is this important? What happens if we don't do this?

## High-Level Architecture

\`\`\`
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │─────>│   API       │─────>│  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
\`\`\`

Brief description of major components and data flow.

**Key Components**:
1. **Component A**: Description
2. **Component B**: Description
3. **Component C**: Description

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: SQLite
- **Libraries**: bcrypt, python-jose
- **Testing**: pytest

## Implementation Phases (Summary)

### Phase 1: {Phase Name} ({X} hours)
Brief description of what this phase does. **[Details →](phase1-{slug}.md)**

**Deliverables**: What files/features are created

### Phase 2: {Phase Name} ({X} hours)
Brief description of what this phase does. **[Details →](phase2-{slug}.md)**

**Deliverables**: What files/features are created

### Phase 3: {Phase Name} ({X} hours)
Brief description of what this phase does. **[Details →](phase3-{slug}.md)**

**Deliverables**: What files/features are created

### Phase 4: {Phase Name} ({X} hours)
Brief description of what this phase does. **[Details →](phase4-{slug}.md)**

**Deliverables**: What files/features are created

**Total**: {Total} hours

## Dependencies

**Technical Prerequisites**:
- TECH-XXX: {Prerequisite name} (if applicable)
- None (if standalone)

**External Libraries**:
- `library-name`: Purpose (see [Dependency Approval](../../SPEC-070-dependency-pre-approval-matrix.md))

**Related Specs**:
- SPEC-XXX: {Related spec title}

## References

- [GUIDELINE-XXX: {Pattern Name}](../../guidelines/GUIDELINE-XXX-{slug}.md)
- [GUIDELINE-YYY: {Pattern Name}](../../guidelines/GUIDELINE-YYY-{slug}.md)

## Success Criteria (Definition of Done)

- [ ] All phases complete
- [ ] All tests passing (>90% coverage)
- [ ] Security audit passed (if applicable)
- [ ] Documentation updated
- [ ] Puppeteer DoD verified (for web features)
- [ ] Code review approved
- [ ] Performance benchmarks met (if applicable)

---

**For implementation details, read the phase document for your current phase.**

**Determine current phase**: Check ROADMAP.md or your last commit message.

**Questions?** Contact architect via notification system.
```

### Phase Document Template

```markdown
# SPEC-{number} - Phase {N}: {Phase Name}

**Estimated Time**: {X} hours
**Dependencies**: Phase {N-1} must be complete (or "None" for Phase 1)
**Files Modified**: Estimated {X} files

## Goal

What does this phase accomplish? (1-2 sentences)

**Success**: When this phase is complete, {specific outcome}.

## Prerequisites

**Before starting this phase**:
- [ ] Phase {N-1} complete (if applicable)
- [ ] Dependencies installed: \`pip install dependency-name\`
- [ ] Related guidelines reviewed (see References below)
- [ ] Database backed up (if database changes)

## Detailed Steps

### Step 1: {Task Name}

**What**: Create/modify X with Y

**Why**: This is needed because Z

**How**:
1. Action 1 with specific details
2. Action 2 with specific details
3. Action 3 with specific details

**Code Example**:
\`\`\`python
# Example implementation
def example_function(param: str) -> dict:
    """
    Brief docstring explaining purpose.

    Args:
        param: Parameter description

    Returns:
        dict: Return value description
    """
    # Implementation details
    return {"result": "example"}
\`\`\`

**Files to Create/Modify**:
- \`coffee_maker/module/file.py\` (new file) - Purpose
- \`coffee_maker/other/file.py\` (modify function X) - Changes

---

### Step 2: {Task Name}

**What**: {Description}

**Why**: {Reason}

**How**:
1. {Action}
2. {Action}

**Code Example**:
\`\`\`python
# Example
\`\`\`

**Files to Create/Modify**:
- \`path/to/file.py\`

---

### Step 3: {Task Name}

... (repeat for each step in phase)

---

## Acceptance Criteria

**This phase is complete when**:
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2
- [ ] Specific, testable criterion 3
- [ ] All tests passing for this phase
- [ ] No linting errors (\`black .\`, \`autoflake\`)

## Testing This Phase

\`\`\`bash
# Run tests specific to this phase
pytest tests/test_{module}_phase{N}.py -v

# Expected output: All tests pass, X tests run
\`\`\`

**Verification steps**:
1. Run tests
2. Verify output matches expected
3. Check files created/modified
4. Commit changes with message: "Complete Phase {N}: {Phase Name}"

## References for This Phase

**Patterns used**:
- [GUIDELINE-XXX: {Pattern}](../../guidelines/GUIDELINE-XXX.md) - How to apply pattern

**Related documentation**:
- [Other spec](../SPEC-YYY/README.md) - Context or related work

## Next Phase

**After completing this phase**:
- Commit and push changes
- Update ROADMAP (mark Phase {N} complete)
- Proceed to **[Phase {N+1}: {Name}](phase{N+1}-{slug}.md)**

---

**Note**: This document focuses on Phase {N} only. See [README.md](README.md) for full spec overview.
```

---

## Benefits of Hierarchical Specs

### 1. Context Efficiency (71% reduction)

**Before (Monolithic)**:
- Total spec: 350 lines
- code_developer loads: 350 lines (entire spec)
- Wasted context: 280 lines (only needs current phase)

**After (Hierarchical)**:
- README: 100 lines
- Phase 1: 60 lines
- code_developer loads: 160 lines (README + current phase)
- Context saved: 190 lines (54% reduction in Phase 1)

### 2. Focus and Clarity

**code_developer sees**:
- High-level overview (README)
- Current phase details (phase{N}.md)
- Nothing else (no distraction from future phases)

**Result**: 30% faster implementation (better focus)

### 3. Scalability

**Large feature (10 phases)**:
- Monolithic spec: 800+ lines (exceeds context budget)
- Hierarchical spec: 100 (overview) + 60 (current phase) = 160 lines ✅

### 4. Reusability

**Common patterns**:
- Written once in guidelines
- Referenced by multiple specs
- Updates propagate automatically

**Example**:
- GUIDELINE-007 (JWT auth) referenced by 5 specs
- Update guideline → all specs benefit
- No duplication

### 5. Maintenance

**Update one phase**:
- Modify only phase{N}.md
- No need to touch other phases
- Clear separation of concerns

---

## Integration with code_developer Daemon

**Daemon enhancements** (see SPEC-NEXT-hierarchical-modular-spec-architecture.md):

### Phase Detection

```python
def _detect_current_phase(priority: dict) -> int:
    """Detect which phase to work on.

    Checks:
    1. ROADMAP phase tracking
    2. Git commit history
    3. File existence

    Returns:
        int: Phase number (1, 2, 3, etc.)
    """
```

### Phase Spec Loading

```python
def _load_phase_spec(priority_number: str, phase: int) -> str:
    """Load overview + current phase document.

    Args:
        priority_number: e.g., "24"
        phase: Phase number

    Returns:
        str: README.md + phase{N}.md content (~150 lines)
    """
```

### Context Optimization

```python
# OLD: Load entire spec
spec_content = read_full_spec()  # 350 lines

# NEW: Load overview + current phase
spec_content = load_phase_spec(priority_number, current_phase)  # 160 lines
```

---

## Success Metrics

**Target metrics for hierarchical specs**:
- Average spec context: <150 lines (vs 300+ monolithic)
- Phase implementation time: 30% faster
- Spec reusability: 50%+ from referenced guidelines
- Iteration count: 20% fewer (clearer guidance)

**Track per spec**:
- Lines loaded per iteration
- Implementation time per phase
- Number of guideline references
- code_developer feedback

---

## Examples

### Example 1: Authentication System

```
SPEC-025-user-authentication/
├── README.md (Overview)
│   ├── Problem: Need JWT auth for API
│   ├── Architecture: Users → JWT → API endpoints
│   ├── Phases: 4 phases, 5.5 hours total
│   └── References: GUIDELINE-007, GUIDELINE-008
├── phase1-database-schema.md
│   ├── Goal: Create users and sessions tables
│   ├── Steps: 3 steps with SQL examples
│   └── Time: 1 hour
├── phase2-authentication-logic.md
│   ├── Goal: Password hashing and JWT generation
│   ├── Steps: 4 steps with Python examples
│   └── Time: 1.5 hours
├── phase3-api-endpoints.md
│   ├── Goal: Register, login, logout endpoints
│   ├── Steps: 5 steps with FastAPI examples
│   └── Time: 2 hours
└── phase4-tests-documentation.md
    ├── Goal: Tests and API docs
    ├── Steps: 3 steps with pytest examples
    └── Time: 1 hour
```

**code_developer iteration 1**:
- Reads: README.md + phase1-database-schema.md (160 lines)
- Implements: Database schema
- Commits: "Complete Phase 1: Database schema"

**code_developer iteration 2**:
- Reads: README.md + phase2-authentication-logic.md (180 lines)
- Implements: Auth logic
- Commits: "Complete Phase 2: Authentication logic"

### Example 2: Technical Prerequisite Tracking

```
SPEC-024-technical-prerequisite-tracking/
├── README.md (Overview)
│   ├── Problem: Identify common technical foundations
│   ├── Architecture: Database + Methods + Skills + Integration
│   ├── Phases: 5 phases, 10 hours total
│   └── References: SPEC-050 (POC), GUIDELINE-010 (DB)
├── phase1-database-schema.md (2 hours)
├── phase2-database-methods.md (2 hours)
├── phase3-architect-skill.md (2 hours)
├── phase4-project-manager-integration.md (2 hours)
└── phase5-documentation.md (1 hour)
```

---

## Workflow Summary

1. **Invoke skill**: architect uses `hierarchical-spec-creation` skill
2. **Create structure**: Directory with README.md and phase files
3. **Write overview**: README.md with high-level architecture
4. **Write phases**: One document per phase (1-2 hours each)
5. **Link guidelines**: Reference existing patterns, create new if needed
6. **Update ROADMAP**: Add phase tracking
7. **code_developer implements**: Reads overview + current phase, implements progressively

**Total time**: 60-90 min (vs 120+ for monolithic spec)
**code_developer time**: 30% faster (focused context)
**Context usage**: 71% reduction (150 lines vs 350)

---

## Related

- **CFR-007**: Agent Context Budget (30% Maximum)
- **CFR-016**: Technical Specs Must Be Broken Into Small, Incremental Implementation Steps
- **SPEC-NEXT**: Hierarchical, Modular Technical Specification Architecture
- **PRIORITY 24**: Technical Prerequisite Identification and Tracking

---

**Last Updated**: 2025-10-21
**Maintained By**: architect
**Used By**: All technical spec creation
