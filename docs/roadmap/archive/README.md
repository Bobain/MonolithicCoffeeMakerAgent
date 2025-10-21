# ROADMAP Archive

**Purpose**: Store completed priorities to keep ROADMAP.md manageable (<10K lines)

**Structure**:
```
archive/
├── README.md                    # This file
├── 2025-Q3-COMPLETED.md        # Q3 2025 completed priorities
├── 2025-Q4-COMPLETED.md        # Q4 2025 completed priorities
└── ARCHIVE_INDEX.md             # Searchable index of all archived priorities
```

---

## Archiving Policy

**When to Archive**:
- At end of each quarter
- When ROADMAP.md exceeds 25K lines
- When a phase/epic is 100% complete

**What to Archive**:
- ✅ Complete priorities (status: Complete)
- 📋 All associated technical specs
- 📝 Implementation notes and lessons learned

**What Stays in ROADMAP.md**:
- 📝 Planned priorities
- 🔄 In Progress priorities
- ⏸️ Blocked priorities
- Recent completions (last 30 days)

---

## Archive Format

Each archive file follows this structure:

```markdown
# Completed Priorities - Q3 2025

**Period**: 2025-07-01 to 2025-09-30
**Total Priorities Completed**: X
**Total Effort**: Y hours
**Key Achievements**: [Summary]

---

## PRIORITY X: [Title]

**Status**: ✅ Complete
**Completed Date**: YYYY-MM-DD
**Effort**: X hours
**Technical Spec**: [Link to spec if exists]

### Description
[Original description]

### Acceptance Criteria
- [x] Criterion 1
- [x] Criterion 2

### Implementation Notes
[What was implemented, challenges, decisions]

### Related PRs
- #123 - [PR title]

### Lessons Learned
[Key takeaways for future work]

---

[Next priority...]
```

---

## How to Archive Priorities

**Automated (project_manager)**:

```python
# Use archive-roadmap skill (when implemented)
from coffee_maker.cli.roadmap_cli import RoadmapCLI

cli = RoadmapCLI()
cli.archive_completed_priorities(quarter="2025-Q3")
```

**Manual**:

1. Identify completed priorities from ROADMAP.md
2. Copy priority details to appropriate archive file (e.g., 2025-Q3-COMPLETED.md)
3. Add entry to ARCHIVE_INDEX.md
4. Remove from ROADMAP.md (keep only active work)
5. Commit with message: "docs(roadmap): Archive Q3 2025 completed priorities"

---

## Benefits of Archiving

**Performance**:
- Faster ROADMAP.md parsing (<2s vs 5-10s for 29K lines)
- Reduced context budget for agents (CFR-007 compliance)
- Faster git operations (smaller diffs)

**Maintainability**:
- ROADMAP.md stays focused on active work
- Easier to understand current state
- Historical record preserved

**Search**:
- ARCHIVE_INDEX.md provides searchable catalog
- Can grep across all archives for specific priorities
- Lessons learned captured for future reference

---

## Current Archives

### 2025-Q4 (Active)
- **File**: 2025-Q4-COMPLETED.md (in progress)
- **Priorities**: TBD
- **Status**: Current quarter

### 2025-Q3 (Placeholder)
- **File**: 2025-Q3-COMPLETED.md (not yet created)
- **Priorities**: TBD
- **Status**: Will be created when priorities are archived

---

## Archive Index

See `ARCHIVE_INDEX.md` for searchable index of all archived priorities.

---

**Maintained By**: project_manager agent
**Update Frequency**: End of each quarter, or when ROADMAP.md >25K lines
