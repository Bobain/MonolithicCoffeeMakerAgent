# SPEC-025 - Phase 3: Guidelines Library

**Estimated Time**: 2 hours
**Dependencies**: Phase 1 complete, Phase 2 in progress
**Status**: Planned
**Files Created**: `docs/architecture/guidelines/GUIDELINE-012-*.md` (and others)

---

## Goal

Create a library of reusable implementation patterns and best practices that technical specs can reference instead of duplicating. This reduces spec size by 50%+ and establishes single-source-of-truth documentation for common patterns.

**What This Phase Accomplishes**:
- Extract common patterns from existing specs into guidelines
- Create 5-10 initial guidelines (JWT auth, API patterns, testing strategies, etc.)
- Update existing specs to reference guidelines instead of repeating content
- Establish guideline creation workflow for architect

---

## Prerequisites

- [ ] Phase 1 complete (hierarchical spec infrastructure)
- [ ] Understanding of common patterns in existing specs
- [ ] Review of existing specs to identify duplication

---

## Detailed Steps

### Step 1: Identify Common Patterns

**What**: Analyze existing specs to find repeated patterns

**Why**: Avoid creating guidelines for one-off implementations

**How**:
1. Review recent specs (SPEC-020, SPEC-021, SPEC-022, etc.)
2. Look for patterns that appear 3+ times across different specs
3. Document pattern occurrences and variations
4. Prioritize patterns by frequency and importance

**Common Patterns to Extract**:
- JWT authentication implementation
- Password hashing with bcrypt
- API endpoint structure (FastAPI)
- Database migration workflow
- Testing strategy (unit, integration, e2e)
- Error handling patterns
- Async/await patterns
- Configuration management
- Observability (Langfuse tracking)
- Git workflow (commit, tag, branch)

**Implementation**:
```bash
# Search for JWT mentions across specs
grep -r "JWT" docs/architecture/specs/*.md | wc -l
# If >3 occurrences, create GUIDELINE-007-jwt-authentication.md

# Search for password hashing
grep -r "bcrypt\|password hash" docs/architecture/specs/*.md | wc -l
# If >3 occurrences, create GUIDELINE-008-password-hashing.md

# Search for API patterns
grep -r "FastAPI\|@router" docs/architecture/specs/*.md | wc -l
# If >3 occurrences, create GUIDELINE-009-fastapi-endpoints.md
```

**Output**: List of 10-15 candidate patterns

**Files to Create/Modify**:
- None yet (analysis phase)

---

### Step 2: Create Guideline Template

**What**: Define standard structure for all guidelines

**Why**: Consistency makes guidelines easier to use and maintain

**How**:
1. Create GUIDELINE-000-template.md as reference
2. Define sections: When to Use, How to Implement, Anti-Patterns, Testing
3. Include code examples and references

**Template Structure**:
```markdown
# GUIDELINE-{number}: {Title}

**Category**: {Design Pattern | Best Practice | Anti-Pattern | Testing Strategy}
**Applies To**: {What part of codebase}
**Author**: architect
**Date**: {YYYY-MM-DD}
**Version**: 1.0.0

---

## When to Use

When should developers use this pattern? What problems does it solve?

**Use Cases**:
- Use case 1
- Use case 2

**Don't Use When**:
- Situation where pattern not appropriate

---

## How to Implement

Step-by-step with code examples.

### Step 1: {Task}

```python
# Good example
class GoodExample:
    pass
```

### Step 2: {Task}

...

---

## Anti-Patterns to Avoid

What NOT to do.

```python
# Bad example
class BadExample:
    pass  # ❌ Don't do this because...
```

**Why This is Bad**: Explanation

---

## Testing Approach

How to test code using this pattern.

```python
def test_pattern():
    # Test implementation
    assert result == expected
```

**Test Coverage**:
- Test case 1
- Test case 2

---

## Related Guidelines

- [GUIDELINE-XXX](./GUIDELINE-XXX-title.md)

---

## Examples in Codebase

- `coffee_maker/path/to/example.py` (lines 10-50)
- `coffee_maker/path/to/example2.py` (lines 30-80)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | {DATE} | Initial guideline |
```

**Files to Create/Modify**:
- `docs/architecture/guidelines/GUIDELINE-000-template.md` (new file)

---

### Step 3: Create Initial Guidelines (5-10)

**What**: Create first set of guidelines for most common patterns

**Why**: Provide immediate value, demonstrate approach

**How**:
1. Use template to create each guideline
2. Include real code examples from codebase
3. Document current best practices
4. Keep guidelines focused (1-2 pages max)

**Priority Guidelines to Create**:

1. **GUIDELINE-012: Hierarchical Spec Creation Pattern**
   - When to use hierarchical vs monolithic specs
   - How to break features into phases
   - Phase size guidelines (1-2 hours)
   - Template usage

2. **GUIDELINE-013: Progressive Implementation Workflow**
   - Phase-by-phase implementation process
   - How code_developer uses hierarchical specs
   - ROADMAP phase tracking
   - Git commit messages for phases

3. **GUIDELINE-014: FastAPI Endpoint Pattern**
   - Standard endpoint structure
   - Error handling
   - Request/response models
   - Authentication integration

4. **GUIDELINE-015: Database Migration Pattern**
   - When to create migrations
   - Migration file structure
   - Testing migrations
   - Rollback strategy

5. **GUIDELINE-016: Testing Strategy**
   - Unit test structure
   - Integration test approach
   - Mocking patterns
   - Coverage requirements (>80%)

6. **GUIDELINE-017: Error Handling Pattern**
   - Custom exception hierarchy
   - Error logging
   - User-facing error messages
   - Retry logic

7. **GUIDELINE-018: Async/Await Pattern**
   - When to use async
   - Common async patterns
   - Error handling in async
   - Testing async code

8. **GUIDELINE-019: Configuration Management**
   - Environment variables
   - Config file structure
   - Secrets management
   - Multi-environment support

9. **GUIDELINE-020: Observability Pattern**
   - Langfuse integration
   - Trace decorators
   - Metrics to track
   - Log formatting

10. **GUIDELINE-021: Git Workflow**
    - Commit message format
    - Tagging strategy
    - Branch naming (roadmap only, per CFR-013)
    - PR creation

**Implementation Example** (GUIDELINE-012):
```markdown
# GUIDELINE-012: Hierarchical Spec Creation Pattern

**Category**: Best Practice
**Applies To**: Technical Specifications
**Author**: architect
**Date**: 2025-10-21
**Version**: 1.0.0

## When to Use

Use hierarchical specs when:
- Feature requires >4 hours of implementation
- Feature has clearly distinct phases (database → API → UI → tests)
- Feature needs progressive implementation (can't do all at once)
- CFR-016 compliance required (incremental steps)

Use monolithic specs when:
- Feature <4 hours total
- Single cohesive implementation (no clear phases)
- Small bug fix or enhancement

## How to Implement

### Step 1: Break Feature Into Phases

Each phase should be:
- **1-2 hours** of work (CFR-016 requirement)
- **Independently testable**
- **Clear deliverables**
- **Sequential** (Phase 2 depends on Phase 1)

Example breakdown:
```
Feature: User Authentication (6 hours total)
  Phase 1: Database Schema (1 hour)
    - Create users table
    - Create sessions table
    - Write migration
  Phase 2: Auth Logic (1.5 hours)
    - Password hashing
    - JWT generation
    - Session management
  Phase 3: API Endpoints (2 hours)
    - Register endpoint
    - Login endpoint
    - Logout endpoint
  Phase 4: Tests (1.5 hours)
    - Unit tests
    - Integration tests
    - Security tests
```

### Step 2: Use technical-specification-handling Skill

```python
from coffee_maker.utils.spec_handler import SpecHandler

spec_handler = SpecHandler()

result = spec_handler.create_hierarchical(
    us_number="104",
    title="User Authentication System",
    phases=[
        {"name": "database-schema", "hours": 1},
        {"name": "auth-logic", "hours": 1.5},
        {"name": "api-endpoints", "hours": 2},
        {"name": "tests", "hours": 1.5}
    ]
)

# Creates directory: SPEC-104-user-authentication-system/
# With files: README.md, phase1-database-schema.md, etc.
```

### Step 3: Fill In Phase Details

For each phase file:
1. Goal (what this phase accomplishes)
2. Prerequisites (previous phase complete, dependencies)
3. Detailed steps (numbered, actionable)
4. Code examples
5. Acceptance criteria (testable)
6. Testing approach

## Anti-Patterns to Avoid

❌ **Don't create 10+ phases**: Too granular, defeats purpose
  - Combine related tasks into logical 1-2 hour chunks

❌ **Don't make phases too large**: >3 hours risks timeout
  - Split large phases into sub-phases

❌ **Don't make phases dependent on future phases**: Sequential only
  - Phase 2 can depend on Phase 1, but NOT on Phase 3

## Testing Approach

Validate spec structure:
```bash
# Check directory created
ls -la docs/architecture/specs/SPEC-104-user-authentication-system/

# Check phase files exist
ls -la docs/architecture/specs/SPEC-104-*/phase*.md

# Validate README has phase summary
grep "Phase 1:" docs/architecture/specs/SPEC-104-*/README.md
```

## Related Guidelines

- [GUIDELINE-013: Progressive Implementation Workflow](./GUIDELINE-013-progressive-implementation-workflow.md)
- [CFR-016: Incremental Implementation](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-016)

## Examples in Codebase

- [SPEC-025-hierarchical-modular-spec-architecture/](../specs/SPEC-025-hierarchical-modular-spec-architecture/) (reference implementation)
```

**Files to Create/Modify**:
- `docs/architecture/guidelines/GUIDELINE-012-hierarchical-spec-creation.md` (new)
- `docs/architecture/guidelines/GUIDELINE-013-progressive-implementation.md` (new)
- `docs/architecture/guidelines/GUIDELINE-014-fastapi-endpoints.md` (new)
- ... (7 more guidelines)

---

### Step 4: Update Existing Specs to Reference Guidelines

**What**: Replace duplicated content in specs with guideline references

**Why**: Reduce spec size, maintain single source of truth

**How**:
1. Identify specs with duplicated patterns
2. Replace detailed implementation with reference to guideline
3. Keep project-specific details in spec
4. Test that code_developer can still implement from updated spec

**Before** (duplicated content):
```markdown
## JWT Implementation

JWT tokens are JSON Web Tokens used for stateless authentication.

### Setup

1. Install python-jose:
   ```bash
   poetry add python-jose[cryptography]
   ```

2. Create secret key:
   ```python
   import secrets
   SECRET_KEY = secrets.token_hex(32)
   ```

3. Generate token:
   ```python
   from jose import jwt
   from datetime import datetime, timedelta

   def create_token(user_id: str) -> str:
       payload = {
           "user_id": user_id,
           "exp": datetime.utcnow() + timedelta(hours=24)
       }
       return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
   ```

... (30 more lines)
```

**After** (referenced guideline):
```markdown
## JWT Implementation

Follow [GUIDELINE-007: JWT Authentication Pattern](../../guidelines/GUIDELINE-007-jwt-authentication.md).

**Project-Specific Configuration**:
- Token expiry: 24 hours (requirement from security team)
- Secret key location: `JWT_SECRET` environment variable
- Algorithm: HS256 (per guideline default)
- Additional claims: Include `role` and `permissions` fields
```

**Benefit**: 30 lines → 8 lines (73% reduction) ✅

**Files to Create/Modify**:
- Update 2-3 existing specs to use guideline references

---

### Step 5: Document Guideline Creation Workflow

**What**: Update architect documentation with guideline creation process

**Why**: architect needs to know when and how to create new guidelines

**How**:
1. Add section to `.claude/agents/architect.md`
2. Document decision criteria (when to create guideline)
3. Document creation process (use template, fill sections)
4. Document maintenance (versioning, updates)

**Add to architect.md**:
```markdown
## Creating Implementation Guidelines

### When to Create a Guideline

Create a new guideline when:
- Pattern appears 3+ times across different specs
- Pattern is reusable across features
- Pattern represents best practice worth documenting
- Team asked "how do we do X?" multiple times

### Guideline Creation Process

1. Use GUIDELINE-000-template.md as starting point
2. Number sequentially (next available GUIDELINE-XXX)
3. Write clear "When to Use" section
4. Include real code examples from codebase
5. Document anti-patterns (what NOT to do)
6. Add testing approach
7. Link to related guidelines
8. Commit with message: "docs: Add GUIDELINE-XXX - {title}"

### Guideline Maintenance

- **Update** when best practices change
- **Version** using semantic versioning
- **Archive** when superseded by better approach
- **Reference** from multiple specs to ensure value
```

**Files to Create/Modify**:
- `.claude/agents/architect.md` (add guideline creation section)

---

## Acceptance Criteria

**This phase is complete when**:

- [ ] GUIDELINE-000-template.md created
- [ ] 5-10 initial guidelines created (GUIDELINE-012 through GUIDELINE-021)
- [ ] Guidelines cover most common patterns (JWT, API, testing, etc.)
- [ ] At least 2 existing specs updated to reference guidelines
- [ ] architect.md updated with guideline creation workflow
- [ ] All guidelines have code examples and anti-patterns
- [ ] Guidelines reviewed for accuracy and completeness

**Validation**:
```bash
# Check guidelines exist
ls -la docs/architecture/guidelines/GUIDELINE-*.md | wc -l
# Expected: 11 (template + 10 guidelines)

# Check specs reference guidelines
grep -r "GUIDELINE-" docs/architecture/specs/*.md | wc -l
# Expected: >10 references
```

---

## Testing This Phase

### Manual Testing

1. **Create new spec using guidelines**:
   - architect creates SPEC-999-test-feature/
   - References GUIDELINE-012 (hierarchical spec creation)
   - References GUIDELINE-014 (FastAPI endpoints)
   - Verify spec is concise (guideline references instead of duplication)

2. **code_developer uses spec with guidelines**:
   - code_developer reads SPEC-999
   - Follows guideline links to get implementation details
   - Implements feature successfully
   - Verify guidelines provide sufficient detail

3. **Measure spec size reduction**:
   - Before: Spec with duplicated content (300 lines)
   - After: Spec with guideline references (150 lines)
   - Target: 50% reduction ✅

---

## References for This Phase

**Related Documents**:
- [GUIDELINE-000-template.md](../../guidelines/GUIDELINE-000-template.md) (to be created)
- Existing specs for pattern extraction

---

## Next Phase

**After completing this phase, proceed to**:
- **[Phase 4: Spec Migration](phase4-spec-migration.md)**

**Deliverable Handoff**:
- Guidelines library established (5-10 initial guidelines)
- architect workflow documented
- Specs reference guidelines (50% size reduction demonstrated)
- Pattern library ready for growth

---

**Note**: Guidelines are living documents. They will grow organically as new patterns emerge. This phase establishes the foundation.
