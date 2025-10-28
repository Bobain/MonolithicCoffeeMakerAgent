# Phase 0 Dependencies Map

**Last Updated**: 2025-10-18
**Purpose**: Track dependencies between Phase 0 user stories to coordinate parallel work
**Owner**: project_manager agent

---

## Critical Path

The CRITICAL PATH determines the minimum time to complete Phase 0.

```
US-091 (Code Index) → US-092 & US-093 (Migrations) → US-094 (Validation) → US-095 & US-096 (Retirement)
   |
   ├→ US-097 (Spec Creation Automation)
   └→ US-102 (Refactoring Coordinator)
```

**Critical Path Duration**: 13-21 hours (estimated)
- US-091: 5-7 hours (BLOCKING)
- US-092: 3-5 hours (parallel with US-093)
- US-093: 3-5 hours (parallel with US-092)
- US-094: 2-3 hours (monitoring setup)
- US-095 & US-096: 2-3 hours (retirement)

**Actual Timeline**: 3-4 weeks (due to validation period US-094)

---

## Dependency Graph

### Group 1: Code Analysis Skills (FOUNDATION)

```
US-090 (5 Code Analysis Skills)  ← COMPLETE ✅
  │
  ├─ BLOCKS → US-091 (Code Index Infrastructure)  ← IN PROGRESS 🔄
  │               │
  │               ├─ BLOCKS → US-092 (Migrate to architect)
  │               ├─ BLOCKS → US-093 (Migrate to code_developer)
  │               ├─ BLOCKS → US-097 (Spec Creation Automation)
  │               └─ BLOCKS → US-102 (Refactoring Coordinator)
  │
  └─ ENABLES → US-092 (architect uses code analysis skills)
  └─ ENABLES → US-093 (code_developer uses code analysis skills)

US-092 + US-093 (Both complete)
  │
  └─ BLOCKS → US-094 (Transition Validation - 3 weeks)
                 │
                 └─ BLOCKS → US-095 (Retire assistant (using code analysis skills))
                                │
                                └─ BLOCKS → US-096 (Archive assistant (using code analysis skills).md)
```

**Status**:
- US-090: COMPLETE ✅ (2025-10-18)
- US-091: IN PROGRESS 🔄 (code_developer assigned, 60% complete)
- US-092-096: PLANNED (awaiting US-091 completion)

**Blockers**:
- US-091 blocks ALL migration work (US-092, US-093, US-097, US-102)
- Must complete US-091 by 2025-10-20 to stay on track

---

### Group 2: Startup Skills (INDEPENDENT - CFR-007 FIX)

```
US-062 (code_developer-startup)  ← PLANNED
  │
  ├─ NO DEPENDENCIES (can start immediately)
  └─ PROVIDES PATTERN → US-063, US-064 (implementation reference)

US-063 (architect-startup)  ← PLANNED
  │
  ├─ DEPENDS ON → US-062 (code pattern reference)
  └─ BLOCKS → US-068, US-069, US-097, US-103 (architect acceleration skills)

US-064 (project_manager-startup)  ← PLANNED
  │
  ├─ DEPENDS ON → US-062 (code pattern reference)
  └─ NO DOWNSTREAM DEPENDENCIES
```

**Parallel Execution**: US-062, US-063, US-064 can be implemented simultaneously after US-062 establishes pattern.

**Status**:
- US-062: PLANNED (highest priority, CFR-007 critical)
- US-063: PLANNED (depends on US-062 pattern)
- US-064: PLANNED (depends on US-062 pattern)

**Timeline**:
- US-062: 10-15 hours (target: 2025-10-25)
- US-063: 10-15 hours (target: 2025-10-27)
- US-064: 10-15 hours (target: 2025-10-29)

**Blockers**: None (independent of Group 1)

---

### Group 3: code_developer Acceleration (DEPENDS ON US-062)

```
US-062 (code_developer-startup)  ← HIGHEST PRIORITY
  │
  ├─ BLOCKS → US-065 (test-failure-analysis)
  ├─ BLOCKS → US-066 (dod-verification)
  ├─ BLOCKS → US-067 (git-workflow-automation)
  └─ BLOCKS → US-102 (refactoring-coordinator)
           │
           └─ ALSO DEPENDS ON → US-091 (code index)
           └─ ALSO DEPENDS ON → US-069 (refactoring analysis)

US-065, US-066, US-067  ← INDEPENDENT (can run in parallel after US-062)

US-102 (refactoring-coordinator)
  │
  ├─ DEPENDS ON → US-062 (startup skill infrastructure)
  ├─ DEPENDS ON → US-091 (code index for impact analysis)
  └─ DEPENDS ON → US-069 (refactoring analysis skill)
```

**Parallel Execution**: US-065, US-066, US-067 can be implemented simultaneously after US-062.

**Status**:
- US-065: PLANNED (skill file exists, needs integration)
- US-066: PLANNED (skill file exists, needs integration)
- US-067: PLANNED (skill file exists, needs integration)
- US-102: PLANNED (depends on US-091 completion)

**Timeline**:
- US-065: 5-7 hours (target: 2025-11-01)
- US-066: 5-7 hours (target: 2025-11-03)
- US-067: 5-7 hours (target: 2025-11-05)
- US-102: 8-10 hours (target: 2025-11-07)

**Blockers**: US-062 (startup skills) must complete first

---

### Group 4: architect Acceleration (DEPENDS ON US-063 & US-091)

```
US-063 (architect-startup)  ← MUST COMPLETE FIRST
  │
  ├─ BLOCKS → US-068 (architecture-reuse-check)
  ├─ BLOCKS → US-069 (proactive-refactoring-analysis)
  ├─ BLOCKS → US-097 (spec-creation-automation)
  └─ BLOCKS → US-103 (commit-review-automation)

US-091 (Code Index)  ← MUST COMPLETE FIRST
  │
  ├─ BLOCKS → US-068 (needs indexed components for reuse check)
  ├─ BLOCKS → US-069 (needs indexed code for refactoring analysis)
  ├─ BLOCKS → US-097 (needs indexed code for spec automation)
  └─ BLOCKS → US-103 (needs indexed patterns for commit review)

US-068, US-069  ← INDEPENDENT (can run in parallel after US-063 + US-091)

US-097 (spec-creation-automation)
  │
  ├─ DEPENDS ON → US-063 (architect-startup)
  ├─ DEPENDS ON → US-091 (code index)
  └─ MOVED FROM Phase 8 (higher priority due to immediate value)

US-103 (commit-review-automation)
  │
  ├─ DEPENDS ON → US-063 (architect-startup)
  ├─ DEPENDS ON → US-091 (code index)
  └─ NEW (from ADR-010)
```

**Parallel Execution**: US-068, US-069, US-097, US-103 can be implemented simultaneously after US-063 + US-091.

**Status**:
- US-068: PLANNED (skill file exists, needs integration)
- US-069: PLANNED (skill file exists, needs integration)
- US-097: PLANNED (NEW - moved from Phase 8)
- US-103: PLANNED (NEW - from ADR-010)

**Timeline**:
- US-068: 6-8 hours (target: 2025-11-08)
- US-069: 6-8 hours (target: 2025-11-10)
- US-097: 10-12 hours (target: 2025-11-12)
- US-103: 8-10 hours (target: 2025-11-14)

**Blockers**: US-063 (architect-startup) AND US-091 (code index) must both complete first

---

## Coordination Points

### Coordination Point 1: Week 1 (US-091 Complete)
**Date**: 2025-10-20 (target)
**Milestone**: Code Index infrastructure complete
**Unblocks**:
- US-092, US-093 (migrations can begin)
- US-097 (spec creation automation)
- US-102 (refactoring coordinator)
- US-068, US-069 (architect acceleration, when combined with US-063)

**Actions**:
- code_developer: Complete US-091 implementation
- code_developer: Begin US-092, US-093 immediately (parallel work)
- architect: Review US-091 implementation (quality gate)
- project_manager: Update progress tracker

---

### Coordination Point 2: Week 2 (Migrations Complete)
**Date**: 2025-10-21 (target)
**Milestone**: assistant (using code analysis skills) responsibilities migrated to architect + code_developer
**Unblocks**:
- US-094 (3-week transition validation period begins)
- US-062 (startup skills can begin in parallel)

**Actions**:
- code_developer: Mark US-092, US-093 complete
- project_manager: Begin US-094 monitoring (3-week period)
- code_developer: Begin US-062 implementation (highest priority)
- architect: Review migration quality

---

### Coordination Point 3: Week 3 (Startup Skills Complete)
**Date**: 2025-10-29 (target)
**Milestone**: All agent startup skills implemented (US-062, US-063, US-064)
**Unblocks**:
- US-065, US-066, US-067 (code_developer acceleration)
- US-068, US-069, US-097, US-103 (architect acceleration)

**Actions**:
- code_developer: Complete US-062, US-063, US-064
- code_developer: Begin US-065, US-066, US-067 in parallel
- architect: Begin spec for US-097, US-103
- project_manager: CFR-007 validation (expect 0 violations)

---

### Coordination Point 4: Week 4 (Acceleration Skills Complete)
**Date**: 2025-11-15 (target)
**Milestone**: All Phase 0 user stories complete
**Unblocks**:
- ACE Phases 1-7 (begin with 2.5-4x velocity)

**Actions**:
- code_developer: Complete all acceleration skills (US-065-067, US-102, US-068-069, US-097, US-103)
- project_manager: Final Phase 0 retrospective
- project_manager: Velocity measurements (baseline for Phase 1+)
- architect: Review all implementations (quality gate)

---

## Parallel Work Tracks

### Track 1: code_developer Primary Work
**Week 1**: US-091 (Code Index) - 100% focus
**Week 2**: US-092, US-093 (Migrations) - parallel work
**Week 3**: US-062 (code_developer-startup) - 100% focus, then US-065-067 parallel
**Week 4**: US-102, remaining work

**Total Time**: ~75-95 hours

---

### Track 2: architect Primary Work
**Week 1**: Review US-091 implementation
**Week 2**: Review US-092, US-093 migrations
**Week 3**: US-063 (architect-startup) - 100% focus
**Week 4**: US-068-069, US-097, US-103 - parallel with code_developer

**Total Time**: ~50-70 hours

---

### Track 3: project_manager Monitoring
**All Weeks**: Monitor progress, detect blockers, update docs
**Week 2+**: US-094 transition validation (ongoing, 3 weeks)
**Week 4**: Final retrospective, velocity analysis

**Total Time**: ~15-20 hours

---

## Risk Matrix: Dependency Failures

### Risk 1: US-091 Delayed
**Impact**: CRITICAL - Blocks 6 user stories (US-092, US-093, US-097, US-102, US-068, US-069)
**Mitigation**:
- Daily check-ins on US-091 progress
- If >2 days late, escalate to architect for help
- Consider scope reduction (3-level index → 2-level)

### Risk 2: US-062 Delayed
**Impact**: HIGH - Blocks 7 user stories (US-063, US-064, US-065-067, US-102)
**Mitigation**:
- Prioritize US-062 above all other work
- Time-box to 15 hours max (deliver MVP if needed)
- architect provides design review early (Day 1-2)

### Risk 3: US-063 Delayed
**Impact**: MEDIUM - Blocks 4 user stories (US-068, US-069, US-097, US-103)
**Mitigation**:
- Use US-062 implementation as reference (pattern already established)
- Parallel work: code_developer continues US-065-067 while architect works on US-063

### Risk 4: US-094 Validation Finds Issues
**Impact**: LOW-MEDIUM - May require rework of US-092, US-093
**Mitigation**:
- Continuous monitoring during 3-week period
- Early detection → early fix (don't wait 3 weeks)
- Rollback plan: Keep assistant (using code analysis skills) available during validation

---

## Coordination Rules

### Rule 1: No Work Starts Until Dependencies Complete
**Enforcement**: project_manager checks dependencies before approving new work

Example:
```
code_developer: "Starting US-097 (spec-creation-automation)"
project_manager: "BLOCKED - US-097 depends on US-063 (not started) and US-091 (in progress)"
```

### Rule 2: Parallel Work Must Be Independent
**Enforcement**: project_manager validates no file conflicts

Example:
```
US-065, US-066, US-067 can run in parallel because:
- Different files (test_analyzer.py, dod_checker.py, git_automator.py)
- No shared dependencies (beyond US-062)
- Independent test suites
```

### Rule 3: Weekly Dependency Reviews
**Enforcement**: project_manager reviews dependency graph every Monday

**Questions**:
- Any dependencies blocking critical path?
- Any parallel work creating conflicts?
- Any risks of cascading delays?

---

## Dependency Tracking Commands

### Check Dependencies for a User Story

```bash
# Show what blocks US-XXX
poetry run project-manager dependencies --blocked-by US-XXX

# Show what US-XXX blocks
poetry run project-manager dependencies --blocks US-XXX

# Show entire dependency graph
poetry run project-manager dependencies --graph
```

### Validate Ready to Start

```bash
# Check if US-XXX can start (all dependencies complete)
poetry run project-manager dependencies --ready-check US-XXX

# Output: READY or BLOCKED (with list of incomplete dependencies)
```

---

## Notes

- Dependencies tracked in this file MUST match ACE_USER_STORIES.md
- Update this file whenever user story status changes
- Use dependency graph to optimize parallel work
- Critical path determines minimum completion time (cannot be accelerated beyond 3-4 weeks due to US-094 validation period)

---

**Maintained By**: project_manager agent
**Update Frequency**: Daily during Phase 0, after each user story status change
**Source**: docs/roadmap/ACE_USER_STORIES.md, docs/roadmap/PHASE_0_ACCELERATION_PLAN.md
