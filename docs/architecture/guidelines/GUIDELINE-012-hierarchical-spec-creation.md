# GUIDELINE-012: Hierarchical Spec Creation Pattern

**Category**: Best Practice

**Applies To**: Technical Specifications

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: [SPEC-025: Hierarchical Modular Spec Architecture](../specs/SPEC-025-hierarchical-modular-spec-architecture/README.md)

---

## Overview

This guideline describes when to use hierarchical (phase-based) technical specifications versus monolithic (single-document) specifications. Hierarchical specs enable progressive implementation, reduce context waste, and scale to large features with 10+ phases.

---

## When to Use

Use hierarchical specs when:
- Feature requires >4 hours of implementation (typically 3+ phases)
- Feature has clearly distinct phases (database → API → UI → tests)
- Feature can be implemented progressively (Phase 1 complete before Phase 2 starts)
- CFR-016 compliance required (incremental steps of 1-2 hours each)
- Code_developer needs to implement phase-by-phase without full feature context

**Example**: "User Authentication System" (6 hours total)
- Phase 1: Database schema (1 hour)
- Phase 2: Authentication logic (1.5 hours)
- Phase 3: API endpoints (2 hours)
- Phase 4: Tests (1.5 hours)

---

## When NOT to Use

Do NOT use hierarchical specs when:
- Feature <4 hours total implementation time
- Feature is a single cohesive task (no clear phases)
- Quick bug fix or small enhancement
- Feature requires all components to exist simultaneously
- Too early to break down into phases (still in design phase)

**Example**: "Add new error message to CLI" - use monolithic spec

---

## The Pattern

### Explanation

Hierarchical specs organize large features into 1-2 hour implementation phases, stored in a directory structure:

```
docs/architecture/specs/SPEC-{number}-{slug}/
├── README.md                (Overview, architecture, prerequisites - 100-150 lines)
├── phase1-{name}.md         (Phase 1 details - 50-100 lines)
├── phase2-{name}.md         (Phase 2 details - 50-100 lines)
├── phase3-{name}.md         (Phase 3 details - 50-100 lines)
├── references.md            (Links to guidelines - 20-30 lines)
└── diagrams/                (Optional: architecture diagrams)
```

**Benefits**:
- **Progressive Disclosure**: code_developer reads ONLY the phase they're implementing
- **Context Efficiency**: ~150 lines per phase vs 350+ for monolithic spec
- **Scalability**: Handles 10+ phase features without context overflow
- **Independence**: Each phase is self-contained and testable
- **References**: Use guidelines to avoid repeating common patterns

### Principles

1. **Phase Independence**: Each phase is self-contained, builds on previous phases only
2. **Clear Deliverables**: Each phase has specific, testable outputs
3. **Size Consistency**: Phases are 1-2 hours (CFR-016 requirement)
4. **README is Essential**: Architect provides overview in README, phase files for implementation details
5. **Progressive Implementation**: Code_developer can implement Phase 1 independently

---

## How to Implement

### Step 1: Analyze Feature and Identify Phases

Break the feature into logical 1-2 hour phases:

1. Identify major components (database, API, UI, tests)
2. Order them sequentially (dependencies first)
3. Estimate time for each (1-2 hours each)
4. Ensure each phase is testable

**Example Breakdown**:
```
Feature: User Authentication (6 hours estimated)

Phase 1: Database Schema (1 hour)
- Create users table
- Create sessions table
- Write database migration

Phase 2: Auth Logic (1.5 hours)
- Hash password with bcrypt
- Generate JWT tokens
- Manage sessions

Phase 3: API Endpoints (2 hours)
- /register endpoint
- /login endpoint
- /logout endpoint

Phase 4: Tests (1.5 hours)
- Unit tests for auth functions
- Integration tests for endpoints
- Security tests
```

### Step 2: Create Directory Structure

```bash
mkdir -p docs/architecture/specs/SPEC-{number}-{slug}
cd docs/architecture/specs/SPEC-{number}-{slug}
touch README.md phase1-{name}.md phase2-{name}.md phase3-{name}.md references.md
```

### Step 3: Create README.md

README provides the big picture. Code_developer reads it first, then only the current phase.

**README.md Template**:
```markdown
# SPEC-{number}: {Full Title}

**Estimated Time**: {total hours}
**Dependencies**: [List prerequisites and dependencies]
**Status**: Planned | In Progress | Complete
**Phases**: 3-5 phases of 1-2 hours each

---

## Overview

{2-3 sentence summary of what this feature accomplishes}

## Architecture

{High-level architecture: diagram, major components, data flow}

## Prerequisites

- [List what must be done first]
- [List dependencies on other features]

## Phases

### Phase 1: {Name} (1 hour)
- {Deliverable 1}
- {Deliverable 2}

### Phase 2: {Name} (1.5 hours)
- {Deliverable 1}
- {Deliverable 2}

### Phase 3: {Name} (1 hour)
- {Deliverable 1}
- {Deliverable 2}

## Definition of Done

- [ ] All phases complete
- [ ] Tests passing (>80% coverage)
- [ ] Code reviewed
- [ ] Documentation updated

## References

See [references.md](./references.md) for links to guidelines and related specs.
```

### Step 4: Create Phase Files

Each phase file (~50-100 lines) contains implementation details for that phase only.

**Phase File Template**:
```markdown
# SPEC-{number} - Phase {N}: {Name}

**Estimated Time**: {1-2 hours}
**Dependencies**: [List prerequisites from earlier phases]
**Status**: Planned | In Progress | Complete

---

## Goal

{What this phase accomplishes}

## Prerequisites

- [ ] Phase X complete
- [ ] [Other prerequisites]

## Detailed Steps

### Step 1: {Task Description}

{Explanation and code examples}

```python
# Example implementation
def example():
    pass
```

### Step 2: {Task Description}

{Explanation and code examples}

## Acceptance Criteria

- [ ] {Testable criterion 1}
- [ ] {Testable criterion 2}
- [ ] {Testable criterion 3}

## Testing Approach

{How to test this phase independently}

```bash
pytest tests/test_phase_{N}.py -v
```

## Files Created/Modified

- `coffee_maker/module/file.py` (new/modified)
- `tests/test_module.py` (new/modified)
```

### Step 5: Create references.md

Link to guidelines and related specs to avoid duplication.

```markdown
# References

## Guidelines

- [GUIDELINE-013: Progressive Implementation Workflow](../../guidelines/GUIDELINE-013-progressive-implementation.md)
- [GUIDELINE-014: FastAPI Endpoints](../../guidelines/GUIDELINE-014-fastapi-endpoints.md)
- [GUIDELINE-016: Testing Strategy](../../guidelines/GUIDELINE-016-testing-strategy.md)

## Related Specs

- [SPEC-XXX: Related feature](../SPEC-XXX-related.md)

## External References

- [Documentation link](https://example.com)
```

---

## Anti-Patterns to Avoid

❌ **Don't create 10+ phases**
- Too granular, defeats purpose
- Combine related tasks into logical chunks
- **Better**: 3-5 larger phases than 10+ tiny phases

❌ **Don't make phases too large (>3 hours)**
- Risks timeout during implementation
- Can't fit in CFR-016 requirement (1-2 hours)
- **Better**: Split into sub-phases

❌ **Don't make later phases depend on future phases**
- Breaks progressive implementation
- Phase 2 can depend on Phase 1, NOT on Phase 3
- **Better**: Ensure sequential dependencies only

❌ **Don't duplicate guideline content in phase files**
- Defeats purpose of guidelines
- Makes specs too large
- **Better**: Reference guidelines, keep project-specific details in phase files

❌ **Don't write README that's too long (>200 lines)**
- Violates context efficiency goal
- **Better**: Put details in phase files, keep README as overview only

---

## Testing Approach

Validate hierarchical spec structure:

```bash
# Check directory created
ls -la docs/architecture/specs/SPEC-{number}-{slug}/

# Check all phase files exist
ls -la docs/architecture/specs/SPEC-{number}-{slug}/phase*.md

# Validate README has phase summary
grep -E "^### Phase [0-9]:" docs/architecture/specs/SPEC-{number}-{slug}/README.md

# Check file sizes (README <200 lines, phases <100 lines each)
wc -l docs/architecture/specs/SPEC-{number}-{slug}/*.md
```

---

## Related Guidelines

- [GUIDELINE-013: Progressive Implementation Workflow](./GUIDELINE-013-progressive-implementation.md)
- [GUIDELINE-014: FastAPI Endpoints](./GUIDELINE-014-fastapi-endpoints.md)
- [GUIDELINE-016: Testing Strategy](./GUIDELINE-016-testing-strategy.md)

---

## Examples in Codebase

- [SPEC-025: Hierarchical Modular Spec Architecture](../specs/SPEC-025-hierarchical-modular-spec-architecture/) (reference implementation with 5 phases)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial guideline for hierarchical spec creation |
