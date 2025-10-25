# SPEC-025: Hierarchical, Modular Technical Specification Architecture

**Status**: Approved
**Created**: 2025-10-21
**Priority**: PRIORITY 25 (HIGH - Context Efficiency + Progressive Implementation)
**Estimated Effort**: 10 hours total
**Related CFRs**: CFR-007 (Context Budget), CFR-016 (Incremental Implementation)

---

## Problem Statement

Currently, technical specifications are monolithic documents that code_developer reads in their entirety, even when only implementing a specific phase or subtask.

**Problems**:
- **Context Waste**: code_developer loads 350-line spec when only needs 50 lines for current phase (80% wasted)
- **Cognitive Overload**: Too much information reduces focus on current subtask
- **Inefficient Updates**: Changing one phase requires re-reading entire spec
- **Duplication**: Common patterns repeated across specs instead of referenced
- **Scalability**: Large features create massive specs that exceed context budgets

**Example Scenario**:
```
code_developer implementing Phase 1 (database schema):
Loads: SPEC-025-user-authentication.md (350 lines)
  - Overview (50 lines)
  - Phase 1: Database (60 lines) ← ONLY NEEDS THIS
  - Phase 2: Auth Logic (80 lines) ← NOT NEEDED YET
  - Phase 3: API (90 lines) ← NOT NEEDED YET
  - Phase 4: Tests (70 lines) ← NOT NEEDED YET

Context waste: 280 lines (80%)
```

---

## High-Level Architecture

This feature introduces a **three-level hierarchical structure** for technical specifications:

```
┌─────────────────────────────────────────────────────────┐
│         HIERARCHICAL SPEC ARCHITECTURE                   │
└─────────────────────────────────────────────────────────┘

Level 1: Overview (README.md)
  ├── Problem statement
  ├── High-level architecture
  ├── Technology stack
  └── Phase summary (brief)

Level 2: Phase Documents (phaseN-*.md)
  ├── phase1-foundation.md (60 lines)
  ├── phase2-core-features.md (80 lines)
  ├── phase3-polish.md (70 lines)
  └── ... (scalable to 10+ phases)

Level 3: Reference Documents (guidelines)
  ├── GUIDELINE-007-jwt-auth.md
  ├── GUIDELINE-008-password-hashing.md
  └── ... (reusable patterns)
```

**Directory Structure**:
```
docs/architecture/specs/
└── SPEC-025-hierarchical-spec-architecture/
    ├── README.md                     ← This file (overview)
    ├── phase1-shared-skill.md       ← Phase 1 details
    ├── phase2-daemon-enhancement.md  ← Phase 2 details
    ├── phase3-guidelines-library.md  ← Phase 3 details
    ├── phase4-spec-migration.md      ← Phase 4 details
    └── phase5-testing-docs.md        ← Phase 5 details
```

---

## Technology Stack

**Implementation**:
- **Skill**: `.claude/skills/shared/technical-specification-handling/SKILL.md` (v2.0.0)
  - Already implements hierarchical spec support
  - Backward compatible with monolithic specs
- **Language**: Python 3.11+
- **Storage**: File system (markdown files in directory structure)
- **Detection**: Automatic phase detection (ROADMAP, git history, file existence)

**Integration Points**:
- **architect**: Uses `create_hierarchical` action to create directory-based specs
- **code_developer**: Uses `read_hierarchical` action to load only relevant phase

---

## Implementation Phases (Summary)

### Phase 1: Shared Skill Enhancement (COMPLETED ✅)
**Effort**: 2 hours | **Status**: Complete (v2.0.0 released)

Extended technical-specification-handling skill with hierarchical spec support. **[Details →](phase1-shared-skill.md)**

**Deliverables**:
- ✅ Hierarchical spec creation logic
- ✅ Progressive disclosure reading
- ✅ Phase detection algorithms
- ✅ Backward compatibility with monolithic specs

---

### Phase 2: Daemon Enhancement
**Effort**: 3 hours | **Status**: Planned

Update daemon_implementation.py to support progressive implementation with phase detection. **[Details →](phase2-daemon-enhancement.md)**

**Deliverables**:
- `_detect_current_phase()` method
- `_load_phase_spec()` method
- Updated `_build_feature_prompt()` for hierarchical loading
- Progress tracking (reset no_progress_count when files change)

---

### Phase 3: Guidelines Library
**Effort**: 2 hours | **Status**: Planned

Create reusable pattern library to reduce spec duplication. **[Details →](phase3-guidelines-library.md)**

**Deliverables**:
- Guidelines directory structure
- 5-10 initial guidelines (JWT auth, password hashing, API patterns, etc.)
- Updated specs to reference guidelines instead of duplicating

---

### Phase 4: Spec Migration
**Effort**: 3 hours | **Status**: Planned

Migrate existing monolithic specs to hierarchical structure. **[Details →](phase4-spec-migration.md)**

**Deliverables**:
- Migration strategy and tooling
- Migrate 3+ recent specs (SPEC-020, SPEC-021, SPEC-022)
- Migration guide documentation

---

### Phase 5: Testing and Documentation
**Effort**: 2 hours | **Status**: Planned

Comprehensive testing and documentation updates. **[Details →](phase5-testing-docs.md)**

**Deliverables**:
- Unit tests for hierarchical spec handling
- Integration tests with code_developer
- Updated architect workflow documentation
- Examples and tutorials

---

**Total Estimated Effort**: 10 hours (2 + 3 + 2 + 3 + 2)

---

## Dependencies

**Technical Prerequisites**:
- ✅ COMPLETED: `.claude/skills/shared/technical-specification-handling/SKILL.md` (v2.0.0)
- ✅ COMPLETED: CFR-016 added to CRITICAL_FUNCTIONAL_REQUIREMENTS.md
- ✅ COMPLETED: daemon_implementation.py fixes (no_progress_count tracking)

**External Dependencies**: None (all built with existing tech stack)

**Related Specs**:
- [SPEC-NEXT-hierarchical-modular-spec-architecture.md](../SPEC-NEXT-hierarchical-modular-spec-architecture.md) (design rationale)
- [CFR-016: Incremental Implementation Steps](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-016)
- [CFR-007: Context Budget](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-007)

---

## References

**Guidelines** (to be created in Phase 3):
- GUIDELINE-012: Hierarchical Spec Creation Pattern
- GUIDELINE-013: Progressive Implementation Workflow

**Skills**:
- [technical-specification-handling v2.0.0](/.claude/skills/shared/technical-specification-handling/SKILL.md)

**Related Documents**:
- [SPEC-NEXT-hierarchical-modular-spec-architecture.md](../SPEC-NEXT-hierarchical-modular-spec-architecture.md) - Original design document (comprehensive rationale)
- [ROADMAP.md PRIORITY 25](../../roadmap/ROADMAP.md) - Strategic spec

---

## Success Criteria (Definition of Done)

**Overall DoD**:
- [ ] All 5 phases complete
- [ ] Technical specification handling skill v2.0.0 integrated
- [ ] daemon_implementation.py supports progressive implementation
- [ ] At least 3 specs migrated to hierarchical format
- [ ] Guidelines library created with 5+ patterns
- [ ] All tests passing (unit + integration)
- [ ] Documentation updated (architect workflow, examples)
- [ ] CFR-016 compliance verified

**Metrics**:
- Average spec context usage: **<150 lines** (vs 300+ currently) ✅ Target: 71% reduction
- Phase implementation time: **30% faster** (better focus)
- Spec reusability: **50%+ content** from referenced guidelines
- code_developer iterations: **20% fewer** (clearer guidance)

---

## Benefits Summary

**Context Efficiency**:
- ✅ **71% context reduction**: Load only overview + current phase (150 lines vs 350)
- ✅ **CFR-007 compliant**: Specs stay within context budget limits

**Progressive Implementation**:
- ✅ **CFR-016 compliant**: Each phase is 1-2 hours (achievable in one iteration)
- ✅ **Unlimited iterations**: code_developer can iterate while making progress
- ✅ **Clear progress tracking**: Phases checked off in ROADMAP

**Scalability**:
- ✅ **Large features manageable**: 10+ phases stay organized
- ✅ **Modular updates**: Change one phase without touching others

**Reusability**:
- ✅ **Pattern library**: Common patterns extracted to guidelines
- ✅ **Reduced duplication**: Reference guidelines instead of repeating

---

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL SPEC WORKFLOW                  │
└───────────────────────────────────────────────────────────────┘

architect creates spec:
    ↓
  Uses technical-specification-handling skill
    ↓
  Creates SPEC-025/ directory with README + phase files
    ↓
  Each phase: 1-2 hours, clear steps, acceptance criteria
    ↓
code_developer starts implementation:
    ↓
  Reads README.md (overview, 100-150 lines)
    ↓
  Detects current phase (ROADMAP, git, file existence)
    ↓
  Loads ONLY current phase document (50-100 lines)
    ↓
  Total context: ~150 lines (vs 350 monolithic) ✅
    ↓
  Implements phase, commits, marks phase complete
    ↓
  Moves to next phase (reads next phase file)
    ↓
  Repeats until all phases complete
```

---

## Progressive Disclosure Pattern

**Key Innovation**: code_developer only loads what's needed NOW

```
Monolithic Spec (OLD):
┌─────────────────────────────┐
│  SPEC-025.md (350 lines)   │
│  ├── Overview              │
│  ├── Phase 1 (needed)      │
│  ├── Phase 2 (not needed)  │
│  ├── Phase 3 (not needed)  │
│  └── Phase 4 (not needed)  │
└─────────────────────────────┘
Context: 350 lines (80% waste)

Hierarchical Spec (NEW):
┌─────────────────────────────┐
│  README.md (100 lines)     │ ← Always loaded
│  + phase1.md (50 lines)    │ ← Current phase only
└─────────────────────────────┘
Context: 150 lines (71% reduction ✅)

Unused phase files NOT loaded:
  - phase2.md (loaded later)
  - phase3.md (loaded later)
  - phase4.md (loaded later)
```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backward compatibility issues | Low | Medium | Skill supports both hierarchical and monolithic specs |
| Phase detection failures | Low | High | Multiple detection strategies (ROADMAP, git, files) with fallback to Phase 1 |
| architect resistance to new format | Medium | Low | Provide templates, automation, and clear examples |
| Migration effort underestimated | Medium | Medium | Start with recent specs, migrate older ones on-demand |
| Guidelines duplication | Low | Low | Review guidelines during creation, consolidate duplicates |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-21 | architect | Initial hierarchical specification created for PRIORITY 25 |

---

## For Implementation

**Current Phase?** Check ROADMAP.md or see phase completion below:

**Phase Status**:
- [x] Phase 1: Shared Skill Enhancement (COMPLETED)
- [ ] Phase 2: Daemon Enhancement (NEXT)
- [ ] Phase 3: Guidelines Library
- [ ] Phase 4: Spec Migration
- [ ] Phase 5: Testing and Documentation

**Next Steps**:
1. code_developer: Read [phase2-daemon-enhancement.md](phase2-daemon-enhancement.md)
2. Implement daemon enhancement
3. Mark Phase 2 complete in ROADMAP
4. Proceed to Phase 3

---

**Note**: This specification itself demonstrates the hierarchical format. Each phase document contains focused, actionable steps for 1-2 hours of work.
