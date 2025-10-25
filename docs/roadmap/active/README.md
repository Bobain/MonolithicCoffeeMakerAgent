# Active ROADMAP Details

**Purpose**: Detailed breakdowns of active phases/epics referenced from main ROADMAP.md

**Structure**:
```
active/
├── README.md                    # This file
├── PHASE_0_ACTIVE.md           # Phase 0 details (assistant (with code analysis skills) migration + skills)
├── PHASE_1_ACTIVE.md           # Phase 1 details (agent startup skills)
├── PHASE_2_ACTIVE.md           # Phase 2 details (code_developer skills)
└── ...
```

---

## Why Separate Active Details?

**Problem**: ROADMAP.md is 29K+ lines, mostly from detailed phase descriptions

**Solution**: Move phase details to separate files, keep ROADMAP.md as high-level overview

**Benefits**:
- ROADMAP.md stays <10K lines (faster parsing, better CFR-007 compliance)
- Phase details remain accessible via links
- Agents load only relevant phase details (not entire ROADMAP)
- Easier navigation and maintenance

---

## File Format

Each active file follows this structure:

```markdown
# PHASE X: [Phase Name]

**Status**: 🔄 In Progress / 📝 Planned
**Priority**: HIGH / MEDIUM / LOW
**Total Stories**: X
**Completed**: Y / X (Z%)
**Target Completion**: YYYY-MM-DD

---

## Overview

[Phase description and goals]

---

## User Stories

### US-XXX: [Story Title]

**Status**: 🔄 In Progress / 📝 Planned / ✅ Complete
**Priority**: HIGH / MEDIUM / LOW
**Effort**: X-Y hours
**Assigned**: [Agent name]

**User Story**:
As a [role], I need [feature], so that [benefit].

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Dependencies**: [List of blocking stories]

**Technical Spec**: [Link if exists]

---

[Next story...]

---

## Phase Progress

### Completed Stories
- ✅ US-XXX: [Title] (Completed: YYYY-MM-DD)

### In Progress Stories
- 🔄 US-XXX: [Title] (Assigned: [agent])

### Planned Stories
- 📝 US-XXX: [Title]

---

## Blockers

[List any blockers affecting this phase]

---

## Notes

[Any additional context, decisions, or lessons learned]
```

---

## How to Use

**In ROADMAP.md** (high-level reference):

```markdown
## PRIORITY X: Phase 0 - Skills Infrastructure

**Status**: 🔄 In Progress
**Details**: See [PHASE_0_ACTIVE.md](active/PHASE_0_ACTIVE.md)
**Progress**: 7 / 16 stories complete (43.75%)
**Target**: 2025-11-15

**Summary**: Implement skills to accelerate code_developer and architect by 3-5x

[Brief 2-3 sentence description]
```

**In PHASE_X_ACTIVE.md** (full details):
- Complete user story breakdowns
- Acceptance criteria
- Dependencies
- Progress tracking
- Blockers

---

## Active Phases

### PHASE_0_ACTIVE.md
- **Phase**: Phase 0 - Skills Infrastructure
- **Status**: 🔄 In Progress
- **Stories**: 16 (7 complete)
- **Target**: 2025-11-15

---

**Note**: Files will be created as phases become active. Completed phases move to archive/.

---

**Maintained By**: project_manager agent
**Update Frequency**: After each story completion or phase status change
