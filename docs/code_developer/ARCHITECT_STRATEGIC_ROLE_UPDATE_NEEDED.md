# Action Needed: Update .claude/CLAUDE.md with Architect's Strategic Role

**Date**: 2025-10-15
**Created By**: project_manager
**For**: code_developer
**Priority**: Medium
**Status**: Pending

---

## Summary

The `.claude/CLAUDE.md` file needs to be updated to reflect the architect agent's strategic role in roadmap optimization. This is technical documentation owned by code_developer.

---

## Context

User provided critical clarification about architect's role:

> "the code-architect takes a step-back contrary to code_developer who implements the next priority: the code-architect should be aware of all the roadmap, as well as all the codebase, and find the simplest, more robust and efficient way to integrate a feature. It should also have an impact on the roadmap prioritization, as it could be able to say that once a feature is implemented, another one will be quick to implement: such info can help project_manager change priorities to ship as much value as possible in a given timeframe"

---

## What Was Updated

project_manager has already updated the following strategic documentation:

1. **docs/roadmap/TEAM_COLLABORATION.md** ✅
   - Added comprehensive architect strategic workflow
   - Emphasized STRATEGIC vs TACTICAL distinction
   - Added synergy analysis workflow example

2. **docs/DOCUMENT_OWNERSHIP_MATRIX.md** ✅
   - Added `docs/architecture/synergies/` directory ownership
   - Documented roadmap synergy analysis workflow
   - Updated architect responsibilities with roadmap optimization

3. **docs/SYSTEM_REQUIREMENTS.md** ✅
   - Updated architect agent boundaries
   - Emphasized strategic analysis and roadmap optimization
   - Clarified architect vs code_developer distinction

4. **docs/templates/SYNERGY_ANALYSIS_TEMPLATE.md** ✅ (NEW)
   - Created template for architect's synergy reports
   - Complete workflow for identifying implementation synergies
   - Time savings analysis framework

---

## What Needs to be Updated

**File**: `.claude/CLAUDE.md`

**Ownership**: code_developer (technical configurations)

**Section to Update**: "Agent Tool Ownership & Boundaries" section

### Specific Changes Needed

#### 1. Update architect Description

**Current** (approximate):
```markdown
**architect** - Architectural Design & Dependencies
- Role: System architecture, technical specifications, dependency management
- Scope: docs/architecture/, pyproject.toml, poetry.lock
- Authority: Creates ADRs, manages dependencies (requires user approval)
- Workflow: Works BEFORE code_developer (pre-implementation design)
```

**Should Be**:
```markdown
**architect** - Strategic Architecture & Roadmap Optimization
- Role: Strategic architectural oversight, roadmap optimization, dependency management
- Philosophy: Takes a step back - analyzes ENTIRE roadmap and ENTIRE codebase (big picture)
- Scope: docs/architecture/ (specs, ADRs, guidelines, synergies), pyproject.toml, poetry.lock
- Authority: Creates ADRs, manages dependencies (requires user approval), influences ROADMAP prioritization
- Key Responsibilities:
  - STRATEGIC ANALYSIS: Analyzes entire roadmap and entire codebase
  - ROADMAP OPTIMIZATION: Identifies implementation synergies, recommends priority reordering
  - VALUE MAXIMIZATION: Helps ship maximum value in given timeframe
  - TECHNICAL SPECS: Creates architectural designs before implementation
  - DEPENDENCY MANAGEMENT: Only agent that runs `poetry add` (user approval required)
- Workflow: Works BEFORE code_developer (strategic design + priority optimization)
- Impact: Can recommend moving priorities up/down based on synergy analysis
- Motto: "Design first, optimize priorities, implement efficiently"
```

#### 2. Emphasize code_developer as TACTICAL

**Add Clarification**:
```markdown
**code_developer** - Autonomous Implementation (TACTICAL)
- Role: Executes all code changes (TACTICAL execution, not strategic planning)
- Philosophy: Focus on next priority - implement what architect designed
- Scope: coffee_maker/, tests/, scripts/, .claude/
- Authority: Creates PRs autonomously, updates ROADMAP status
- Workflow: Implements AFTER architect designs
- Key Distinction:
  - architect = STRATEGIC (entire roadmap, entire codebase, synergies)
  - code_developer = TACTICAL (next priority, focused execution)
- Does NOT: Analyze entire roadmap for synergies, optimize priorities
- Motto: "I execute the design, not the strategy"
```

#### 3. Add Synergy Analysis Workflow

**New Section** (in architecture patterns or workflows):
```markdown
### Synergy Analysis Workflow (architect)

**When**: Periodically or when new related priorities added to ROADMAP

**Flow**:
1. architect analyzes ENTIRE ROADMAP for related priorities
2. architect analyzes ENTIRE CODEBASE for reusable infrastructure
3. architect identifies implementation synergies
4. architect creates synergy report: docs/architecture/synergies/SYNERGY_[date]_[area].md
   - Uses template: docs/templates/SYNERGY_ANALYSIS_TEMPLATE.md
   - Contains: Time savings analysis, priority reordering recommendations
5. architect advises project_manager on priority optimization
6. project_manager updates ROADMAP based on architect's recommendations
7. architect creates technical specs with extensibility in mind
8. code_developer implements following architect's strategic design

**Example**:
If architect identifies that US-034 (Slack) and US-042 (Email) share 80% infrastructure:
- Recommends: Move US-042 immediately after US-034
- Reduces: US-042 estimate from 8h to 2h (reuse base)
- Saves: 6 hours total (37.5% time reduction)
- Result: Ships both features faster, maximizes value/time
```

#### 4. Update Tool Ownership Matrix

**Add to table**:
```markdown
| **docs/architecture/synergies/** | architect | Roadmap synergy analysis | READ-ONLY |
```

---

## Example: Strategic vs Tactical

**architect (STRATEGIC)**:
- "I see US-034 (Slack) and US-042 (Email) both need notifications"
- "Let's analyze the codebase for reusable patterns"
- "Identified synergy: 80% code reuse if implemented consecutively"
- "Recommendation: Move US-042 immediately after US-034"
- "This saves 6 hours and ships both features faster"

**code_developer (TACTICAL)**:
- "Next priority: US-034 (Slack Integration)"
- "Read architect's technical spec"
- "Implement extensible notification framework per spec"
- "Write tests, commit, create PR"
- "Update ROADMAP status: Planned → Complete"

---

## Why This Matters

1. **Clear Role Separation**: architect = strategic, code_developer = tactical
2. **Roadmap Optimization**: architect helps maximize value delivery
3. **Time Savings**: Identifying synergies reduces implementation time
4. **Better Architecture**: Strategic view leads to more extensible designs

---

## References

**Updated Strategic Documentation**:
- docs/roadmap/TEAM_COLLABORATION.md (comprehensive architect workflow)
- docs/DOCUMENT_OWNERSHIP_MATRIX.md (synergy analysis ownership)
- docs/SYSTEM_REQUIREMENTS.md (strategic vs tactical distinction)
- docs/templates/SYNERGY_ANALYSIS_TEMPLATE.md (NEW - synergy report template)

**Technical Documentation to Update**:
- .claude/CLAUDE.md (code_developer owns this file)

---

## Action Items

For **code_developer**:
- [ ] Read this document to understand architect's strategic role
- [ ] Review updated strategic documentation (TEAM_COLLABORATION.md, etc.)
- [ ] Update .claude/CLAUDE.md with architect's strategic responsibilities
- [ ] Emphasize STRATEGIC (architect) vs TACTICAL (code_developer) distinction
- [ ] Add synergy analysis workflow section
- [ ] Update tool ownership matrix with docs/architecture/synergies/
- [ ] Commit changes with descriptive message
- [ ] Mark this document as complete

---

**Created**: 2025-10-15
**Status**: Pending code_developer action
**Priority**: Medium (not blocking, but important for clarity)
