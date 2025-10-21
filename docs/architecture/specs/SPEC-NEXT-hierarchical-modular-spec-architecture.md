# SPEC-NEXT: Hierarchical, Modular Technical Specification Architecture

**Status**: Draft
**Created**: 2025-10-21
**Author**: user_listener (from user requirement)
**Priority**: HIGH
**Related CFRs**: CFR-007 (Context Budget), CFR-016 (Incremental Implementation)

## Problem Statement

Currently, technical specifications are monolithic documents that code_developer reads in their entirety, even when only implementing a specific phase or subtask.

**Problems**:
1. **Context Waste**: code_developer loads 300+ line spec when only needs 50 lines for current phase
2. **Cognitive Overload**: Too much information reduces focus on current subtask
3. **Inefficient Updates**: Changing one phase requires re-reading entire spec
4. **Duplication**: Common patterns repeated across multiple specs instead of referenced
5. **Scalability**: Large features create massive specs that exceed context budgets

**Example**:
```
Current: code_developer implementing Phase 1 (database schema)
Loads: SPEC-025-user-authentication.md (350 lines)
  - Overview (50 lines)
  - Phase 1: Database (60 lines) ← ONLY NEEDS THIS
  - Phase 2: Auth Logic (80 lines) ← NOT NEEDED YET
  - Phase 3: API Endpoints (90 lines) ← NOT NEEDED YET
  - Phase 4: Tests (70 lines) ← NOT NEEDED YET

Context waste: 280 lines (80% wasted!)
```

## Proposed Solution: Hierarchical Spec Architecture

**Implementation**: This is implemented as a Claude skill for architect

**Skill Location**: `.claude/skills/architect/hierarchical-spec-creation/SKILL.md`

**Usage**: architect invokes the `hierarchical-spec-creation` skill when creating ANY technical specification

---

### 1. Multi-Level Spec Structure

**Level 1: Overview Document** (Always read)
```
docs/architecture/specs/SPEC-025-user-authentication/
└── README.md (100-150 lines)
    ├── Problem Statement
    ├── High-level Architecture
    ├── Technology Stack
    ├── Phase Overview (summary only)
    ├── Dependencies
    └── References to detail docs
```

**Level 2: Phase Documents** (Read on-demand)
```
docs/architecture/specs/SPEC-025-user-authentication/
├── README.md (overview)
├── phase1-database-schema.md (60 lines)
├── phase2-authentication-logic.md (80 lines)
├── phase3-api-endpoints.md (90 lines)
└── phase4-tests-documentation.md (70 lines)
```

**Level 3: Reference Documents** (Read on-demand)
```
docs/architecture/guidelines/
├── GUIDELINE-007-jwt-authentication-pattern.md
├── GUIDELINE-008-password-hashing-standard.md
└── GUIDELINE-009-api-security-checklist.md
```

### 2. Progressive Disclosure Pattern

```
┌─────────────────────────────────────────────────────────┐
│         HIERARCHICAL SPEC CONSUMPTION                    │
└─────────────────────────────────────────────────────────┘

code_developer starts implementation:
    ↓
Read SPEC-025/README.md (overview) ← Always read
    ↓
Identify current phase: Phase 1
    ↓
Read SPEC-025/phase1-database-schema.md ← Only current phase
    ↓
References GUIDELINE-008? → Read it on-demand
    ↓
Implement Phase 1 with focused context (110 lines vs 350)
    ↓
Commit, push, continue
    ↓
Next iteration: Read SPEC-025/phase2-authentication-logic.md
    ↓
...progressive implementation continues
```

### 3. File Structure Standards

#### Option A: Directory-Based (RECOMMENDED)

```
docs/architecture/specs/
└── SPEC-{number}-{slug}/
    ├── README.md                    # Overview (mandatory)
    ├── phase1-{name}.md            # Phase 1 detail
    ├── phase2-{name}.md            # Phase 2 detail
    ├── phase3-{name}.md            # Phase 3 detail
    ├── references.md               # Links to guidelines/patterns
    └── diagrams/                   # Architecture diagrams
        ├── architecture.png
        └── database-erd.png
```

**Benefits**:
- Clear organization
- Easy to navigate
- Scalable (add phases as needed)
- Supports diagrams and assets

**Example**:
```
docs/architecture/specs/SPEC-025-user-authentication/
├── README.md
├── phase1-database-schema.md
├── phase2-authentication-logic.md
├── phase3-api-endpoints.md
├── phase4-tests-documentation.md
├── references.md
└── diagrams/
    ├── auth-flow.png
    └── database-erd.png
```

#### Option B: Skill-Based (ADVANCED)

```
.claude/skills/spec-{number}-{slug}/
├── skill.md                        # Skill definition
├── overview.md                     # High-level summary
├── phases/
│   ├── phase1.md
│   ├── phase2.md
│   └── phase3.md
└── references/
    ├── patterns.md
    └── guidelines.md
```

**Benefits**:
- Integrates with Claude Skills
- Automatic invocation support
- More advanced composition

### 4. README.md Template (Overview Document)

```markdown
# SPEC-{number}: {Title}

**Status**: {Draft|Approved|Implemented}
**Created**: YYYY-MM-DD
**Priority**: {CRITICAL|HIGH|MEDIUM|LOW}
**Estimated Effort**: {X} hours total

## Problem Statement

What problem does this solve? (3-5 sentences)

## High-Level Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │─────>│   API       │─────>│  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
```

Brief description of major components and data flow.

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: SQLite
- **Auth**: JWT (python-jose), bcrypt (passlib)
- **Testing**: pytest

## Implementation Phases (Summary)

### Phase 1: Database Schema (1 hour)
Create users and sessions tables. **[Details →](phase1-database-schema.md)**

### Phase 2: Authentication Logic (1.5 hours)
Password hashing, JWT generation/validation. **[Details →](phase2-authentication-logic.md)**

### Phase 3: API Endpoints (2 hours)
Register, login, logout endpoints. **[Details →](phase3-api-endpoints.md)**

### Phase 4: Tests & Documentation (1 hour)
Unit tests, integration tests, API docs. **[Details →](phase4-tests-documentation.md)**

**Total**: 5.5 hours

## Dependencies

- **Technical Prerequisites**: None (or reference TECH-XXX)
- **External Libraries**: bcrypt, python-jose (see Dependency Approval)
- **Related Specs**: SPEC-020 (Database Migration Framework)

## References

- [GUIDELINE-007: JWT Authentication Pattern](../../guidelines/GUIDELINE-007-jwt-authentication-pattern.md)
- [GUIDELINE-008: Password Hashing Standard](../../guidelines/GUIDELINE-008-password-hashing-standard.md)
- [GUIDELINE-009: API Security Checklist](../../guidelines/GUIDELINE-009-api-security-checklist.md)

## Success Criteria (Definition of Done)

- [ ] All phases complete
- [ ] All tests passing
- [ ] Security audit passed (GUIDELINE-009)
- [ ] Documentation updated
- [ ] Puppeteer DoD verified (if applicable)

---

**For implementation details, read the phase document for your current phase.**

**Current Phase?** Check ROADMAP.md or your last commit message.
```

### 5. Phase Document Template

```markdown
# SPEC-{number} - Phase {N}: {Phase Name}

**Estimated Time**: {X} hours
**Dependencies**: Phase {N-1} must be complete
**Files Modified**: List of files

## Goal

What does this phase accomplish? (1-2 sentences)

## Prerequisites

- Phase {N-1} complete
- Dependencies installed (if any)
- Related guidelines reviewed

## Detailed Steps

### Step 1: {Task Name}

**What**: Create X with Y

**Why**: This enables Z

**How**:
1. Action 1
2. Action 2
3. Action 3

**Code Example**:
```python
# Example implementation
def example():
    pass
```

**Files to Create/Modify**:
- `path/to/file.py` (new file)
- `path/to/other.py` (modify function X)

### Step 2: {Task Name}

... (repeat for each step in phase)

## Acceptance Criteria

- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2
- [ ] Specific, testable criterion 3

## Testing This Phase

```bash
# Run tests specific to this phase
pytest tests/test_phase_{n}.py -v
```

Expected output: All tests pass

## References for This Phase

- [Pattern used](../../guidelines/GUIDELINE-XXX.md)
- [Related documentation](../other-spec.md)

## Next Phase

After completing this phase, proceed to:
- **[Phase {N+1}: {Name}](phase{N+1}-{slug}.md)**

---

**Note**: This is a focused document for Phase {N} only. See [README.md](README.md) for full spec overview.
```

### 6. Daemon Enhancement for Phase Detection

**NOTE**: This section describes future enhancements to `daemon_implementation.py` that need to be implemented.

**Update `daemon_implementation.py`**:

```python
def _detect_current_phase(self, priority: dict) -> int:
    """Detect which phase code_developer should work on next.

    Strategy:
    1. Check ROADMAP.md for phase progress tracking
    2. Check git commit history for completed phases
    3. Check file existence (if Phase 2 files exist, Phase 2 done)
    4. Default to Phase 1

    Returns:
        int: Phase number (1, 2, 3, etc.)
    """
    priority_number = priority.get("number")
    if not priority_number:
        return 1

    # Strategy 1: Check ROADMAP for phase tracking
    # Example: "Phase 2/4 complete" in priority content
    content = priority.get("content", "")
    phase_match = re.search(r"Phase (\d+)/\d+ complete", content)
    if phase_match:
        completed_phase = int(phase_match.group(1))
        return completed_phase + 1  # Next phase

    # Strategy 2: Check commit messages
    # Look for "Complete Phase X" in recent commits
    commits = self.git.get_recent_commits(limit=10)
    for commit in commits:
        if f"PRIORITY {priority_number}" in commit["message"]:
            phase_match = re.search(r"Complete Phase (\d+)", commit["message"])
            if phase_match:
                completed_phase = int(phase_match.group(1))
                return completed_phase + 1

    # Strategy 3: Check file existence
    # If phase files mentioned in spec exist, phase is done
    # (This requires parsing phase spec to find expected files)

    # Default: Start with Phase 1
    return 1


def _load_phase_spec(self, priority_number: str, phase: int) -> str:
    """Load specific phase document for current implementation.

    Args:
        priority_number: e.g., "25"
        phase: Phase number (1, 2, 3, etc.)

    Returns:
        str: Phase spec content (focused, ~50-100 lines)
    """
    spec_dir = Path(f"docs/architecture/specs/SPEC-{priority_number}-*/")
    matching_dirs = list(Path("docs/architecture/specs").glob(f"SPEC-{priority_number}-*"))

    if not matching_dirs:
        logger.warning(f"No spec directory found for PRIORITY {priority_number}")
        return "[NO SPEC FOUND]"

    spec_dir = matching_dirs[0]

    # Always read overview (README.md)
    overview_file = spec_dir / "README.md"
    phase_file = spec_dir / f"phase{phase}-*.md"

    content = []

    # Read overview
    if overview_file.exists():
        content.append("# OVERVIEW\n")
        content.append(overview_file.read_text())
        content.append("\n---\n\n")

    # Read current phase detail
    phase_files = list(spec_dir.glob(f"phase{phase}-*.md"))
    if phase_files:
        content.append(f"# CURRENT PHASE: Phase {phase}\n")
        content.append(phase_files[0].read_text())
    else:
        logger.warning(f"No phase {phase} document found in {spec_dir}")
        content.append(f"[NO PHASE {phase} DOCUMENT FOUND]")

    return "\n".join(content)


def _build_feature_prompt(self, priority: dict) -> str:
    """Build implementation prompt with hierarchical spec loading."""
    priority_number = priority.get("number")

    # Detect current phase
    current_phase = self._detect_current_phase(priority)
    logger.info(f"📍 Detected current phase: {current_phase}")

    # Load only relevant spec content (overview + current phase)
    spec_content = self._load_phase_spec(priority_number, current_phase)
    logger.info(f"✅ Loaded spec content: {len(spec_content)} chars (phase {current_phase})")

    # Build prompt with focused spec
    return load_prompt(
        PromptNames.IMPLEMENT_FEATURE,
        {
            "PRIORITY_NAME": priority["name"],
            "PRIORITY_TITLE": priority["title"],
            "PRIORITY_CONTENT": priority.get("content", "")[:500],  # Brief summary
            "SPEC_CONTENT": spec_content,  # Overview + current phase only
        },
    )
```

### 7. architect Responsibilities

**Update architect workflow** (CFR-016 compliance):

**Use the `hierarchical-spec-creation` skill** for ALL technical specifications:
- Invoke skill: `/hierarchical-spec-creation` or use Task tool with skill
- Skill creates directory structure and templates
- architect fills in architectural details and design decisions

1. **Create Spec Directory**:
   ```bash
   mkdir -p docs/architecture/specs/SPEC-{number}-{slug}/diagrams
   ```

2. **Write README.md** (overview):
   - Problem statement
   - High-level architecture
   - Phase summary (brief)
   - References to guidelines
   - Total time estimate

3. **Write Phase Documents**:
   - One document per phase
   - 50-100 lines each
   - Focused, actionable steps
   - Clear acceptance criteria

4. **Link to References**:
   - Don't duplicate patterns
   - Reference existing guidelines
   - Create new guidelines if pattern is reusable

5. **Update ROADMAP**:
   - Mark which phase is next
   - Track phase completion

### 8. Benefits of Hierarchical Specs

**Context Efficiency**:
- Before: 350 lines loaded (entire spec)
- After: 100 lines loaded (overview + current phase)
- Savings: 71% context reduction

**Focus**:
- code_developer sees only what's needed NOW
- Less cognitive overload
- Clearer implementation path

**Scalability**:
- Large features (10+ phases) still manageable
- Each phase document stays small (<100 lines)
- No single file exceeds context budget

**Reusability**:
- Common patterns in guidelines (referenced, not duplicated)
- architect builds library of reusable patterns
- Specs become composition of patterns

**Maintenance**:
- Update one phase without touching others
- Easy to add/remove phases
- Clear separation of concerns

### 9. Reference System

**Create Reusable Guidelines**:

```
docs/architecture/guidelines/
├── GUIDELINE-007-jwt-authentication-pattern.md
├── GUIDELINE-008-password-hashing-standard.md
├── GUIDELINE-009-api-security-checklist.md
├── GUIDELINE-010-database-migration-pattern.md
└── GUIDELINE-011-fastapi-endpoint-pattern.md
```

**Specs Reference Guidelines**:

Instead of:
```markdown
## JWT Implementation (50 lines of JWT details)
```

Use:
```markdown
## JWT Implementation

Follow [GUIDELINE-007: JWT Authentication Pattern](../../guidelines/GUIDELINE-007-jwt-authentication-pattern.md).

Project-specific configuration:
- Secret key: Load from environment variable `JWT_SECRET`
- Token expiry: 24 hours
- Algorithm: HS256
```

**Benefits**:
- Guidelines written once, referenced many times
- Updates to guidelines propagate to all specs
- Specs stay focused on project-specific details
- New team members learn patterns from guidelines

### 10. Migration Strategy

**Phase 1: Create Structure** (1 hour)
- Create directory-based spec structure
- Update architect workflow
- Create templates

**Phase 2: Enhance Daemon** (2 hours)
- Add `_detect_current_phase()`
- Add `_load_phase_spec()`
- Update `_build_feature_prompt()`
- Test with existing specs

**Phase 3: Migrate Existing Specs** (3-4 hours)
- Convert existing monolithic specs to hierarchical
- Start with most recent specs (SPEC-020+)
- Backfill older specs as needed

**Phase 4: Create Guidelines Library** (2-3 hours)
- Extract common patterns from existing specs
- Create guideline documents
- Update specs to reference guidelines

**Total**: 8-10 hours

## Implementation Plan

### Phase 1: Foundation (2 hours)

**Goal**: Create directory structure and templates

**Steps**:
1. Create spec template directory with README.md and phase templates
2. Update architect documentation with new workflow
3. Create example hierarchical spec (SPEC-025 as proof of concept)

**Acceptance Criteria**:
- [ ] Template directory exists with all templates
- [ ] Example spec created with 4 phases
- [ ] architect documentation updated

### Phase 2: Daemon Enhancement (3 hours)

**Goal**: Update code_developer to read hierarchical specs

**Steps**:
1. Add `_detect_current_phase()` method
2. Add `_load_phase_spec()` method
3. Update `_build_feature_prompt()` to use hierarchical loading
4. Add phase tracking to ROADMAP updates

**Acceptance Criteria**:
- [ ] daemon detects current phase correctly
- [ ] daemon loads only relevant spec content
- [ ] Context usage reduced by 50%+
- [ ] All tests passing

### Phase 3: Guidelines Library (2 hours)

**Goal**: Create reusable pattern library

**Steps**:
1. Create guidelines directory structure
2. Extract common patterns from existing specs
3. Create 5-10 initial guidelines
4. Update specs to reference guidelines

**Acceptance Criteria**:
- [ ] Guidelines directory created
- [ ] 5+ guidelines documented
- [ ] At least 2 specs updated to reference guidelines

### Phase 4: Migration (3 hours)

**Goal**: Migrate existing specs to hierarchical structure

**Steps**:
1. Migrate SPEC-020, SPEC-021, SPEC-022 (most recent)
2. Update older specs as they're accessed
3. Document migration process

**Acceptance Criteria**:
- [ ] 3+ specs migrated to hierarchical structure
- [ ] Migration guide documented
- [ ] No breaking changes to existing workflow

## Benefits Summary

1. **71% Context Reduction**: Load only what's needed for current phase
2. **Scalable**: Large features (10+ phases) remain manageable
3. **Focused**: code_developer sees only relevant information
4. **Reusable**: Common patterns extracted to guidelines
5. **Maintainable**: Update one phase without touching others
6. **CFR Compliant**: Aligns with CFR-007 (context budget) and CFR-016 (incremental steps)

## Success Metrics

- Average spec context usage: <150 lines (vs 300+ currently)
- Phase implementation time: 30% faster (better focus)
- Spec reusability: 50%+ of content from referenced guidelines
- code_developer iterations: 20% fewer (clearer guidance)

## Related

- **CFR-007**: Agent Context Budget (30% Maximum)
- **CFR-016**: Technical Specs Must Be Broken Into Small, Incremental Implementation Steps
- **PRIORITY 24**: Technical Prerequisite Identification and Tracking
- **SPEC-050**: POC Management and Workflow

---

**Total Estimated Effort**: 10 hours
**Expected ROI**: 30-40% faster implementations, 70% context reduction
**Priority**: HIGH (enables efficient progressive implementation)
