# SPEC-108: Parallel Agent Execution with Git Worktree

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-19
**Related User Story**: PRIORITY 23 - US-108
**Dependencies**: SPEC-104 (Orchestrator Continuous Work Loop), ADR-013 (Git Workflow on roadmap branch)
**Strategic Value**: 75-150% velocity increase through parallel code_developer instances

---

## Executive Summary

This specification defines a **git worktree-based parallel execution system** that enables the orchestrator to spawn multiple code_developer instances working simultaneously on independent tasks. Using git's native worktree feature, each instance works in an isolated directory with its own feature branch, eliminating file conflicts while maintaining clean integration with the main roadmap branch.

**Key Innovation**: Unlike SPEC-043 (single workspace parallelism), this approach uses **separate physical directories** for each agent instance, achieving true isolation and enabling 2-3 concurrent developers.

**Key Capabilities**:
- **Multiple code_developer Instances**: 2-3 instances working simultaneously
- **Git Worktree Isolation**: Each instance in separate directory with feature branch
- **Automatic Task Separation**: architect identifies non-conflicting tasks
- **Clean Merge Strategy**: Automatic merge to roadmap branch or manual resolution
- **Resource Management**: CPU/memory limits prevent system exhaustion
- **Fault Tolerance**: Instance failures don't affect other instances

**Impact**:
- **+75% Velocity**: With 2 instances (1 main + 1 worktree)
- **+150% Velocity**: With 3 instances (1 main + 2 worktrees)
- **Zero File Conflicts**: Guaranteed by architect pre-validation
- **Predictable Progress**: Multiple priorities complete simultaneously

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Prerequisites & Dependencies](#prerequisites--dependencies)
3. [Architecture Overview](#architecture-overview)
4. [Component Specifications](#component-specifications)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Implementation Plan](#implementation-plan)
7. [Testing Strategy](#testing-strategy)
8. [Security Considerations](#security-considerations)
9. [Performance Requirements](#performance-requirements)
10. [Risk Analysis](#risk-analysis)
11. [Success Criteria](#success-criteria)

---

## Problem Statement

### Current Limitation

**Single Sequential Developer**:
```
Current: ONE code_developer on roadmap branch
├─► Works on PRIORITY 20 (3 hours)
├─► Waits for PRIORITY 20 completion
├─► Works on PRIORITY 21 (3 hours)
├─► Waits for PRIORITY 21 completion
├─► Works on PRIORITY 22 (3 hours)
└─► Total: 9 hours sequential

Acceleration Dashboard shows:
- 12+ parallelizable tasks available
- Only 1 developer working at a time
- Estimated +75% velocity with 2nd developer
```

**Why Current Approach Doesn't Scale**:
1. **Singleton Enforcement** (US-035): Only ONE instance of code_developer allowed
2. **Roadmap Branch** (CFR-013): All work must happen on roadmap branch
3. **File Conflicts**: Multiple instances editing same files → corruption
4. **No Isolation**: Single workspace → no way to separate work

### Desired State

**Multiple Parallel Developers with Isolation**:
```
Desired: THREE code_developers in parallel worktrees

Main Workspace: /path/to/MonolithicCoffeeMakerAgent (roadmap branch)
  └─► orchestrator coordinates work

Worktree 1: /path/to/MonolithicCoffeeMakerAgent-wt1 (feature/us-020)
  └─► code_developer instance 1 works on US-020 (3 hours)

Worktree 2: /path/to/MonolithicCoffeeMakerAgent-wt2 (feature/us-021)
  └─► code_developer instance 2 works on US-021 (3 hours)

All complete simultaneously → merge to roadmap
Total: 3 hours (vs 9 hours sequential)
Velocity: +200% (3x faster)
```

### User Requirement

From ROADMAP PRIORITY 23:
- **Goal**: Enable 2-3 parallel code_developer instances
- **Method**: Use git worktree for isolation
- **Target**: +75% velocity (2 instances), +150% velocity (3 instances)
- **Constraint**: architect must validate task separation (no file conflicts)
- **Safety**: Automatic merge or manual resolution, rollback on failures

---

## Prerequisites & Dependencies

### Required Completed Work

1. **SPEC-104: Orchestrator Continuous Work Loop** ✅
   - Orchestrator agent running 24/7
   - ROADMAP monitoring and task delegation
   - Message bus for agent coordination

2. **CFR-013: Git Workflow on roadmap Branch** ✅
   - All agents work on roadmap branch
   - No feature branches in normal workflow
   - Worktrees are exception (orchestrator-managed only)

3. **US-035: Singleton Agent Enforcement** ✅
   - One instance per agent type per workspace
   - Worktrees enable multiple instances (different workspaces)

4. **Acceleration Dashboard** (PRIORITY 21 - US-105) ✅
   - Identifies parallelizable tasks
   - Provides task separation analysis
   - Estimates velocity gains

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Git Version** | 2.5+ | 2.30+ |
| **Disk Space** | 5GB free | 10GB+ free |
| **Memory** | 8GB | 16GB+ |
| **CPU** | 4 cores | 8+ cores |
| **OS** | macOS, Linux | macOS Sonoma+, Ubuntu 22.04+ |

### New Skills Required

1. **architect: task-separator skill** (NEW)
   - Analyzes ROADMAP priorities
   - Identifies file dependencies
   - Validates task independence
   - Assigns tasks to worktrees

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Parallel Execution Coordinator                    │ │
│  │                                                              │ │
│  │  1. Get parallelizable tasks (Acceleration Dashboard)       │ │
│  │  2. Ask architect to validate task separation               │ │
│  │  3. Create git worktrees for independent tasks              │ │
│  │  4. Spawn code_developer instances in each worktree         │ │
│  │  5. Monitor progress (message bus)                          │ │
│  │  6. Merge completed work → roadmap branch                   │ │
│  │  7. Clean up worktrees                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GIT WORKTREE LAYER                           │
│                                                                  │
│  Main Repo: /path/to/MonolithicCoffeeMakerAgent                │
│  ├─► Branch: roadmap                                            │
│  ├─► Agent: orchestrator (coordinator only)                     │
│  └─► No code_developer (delegates to worktrees)                 │
│                                                                  │
│  Worktree 1: /path/to/MonolithicCoffeeMakerAgent-wt1           │
│  ├─► Branch: feature/us-020-skill-optimization                  │
│  ├─► Agent: code_developer instance 1                           │
│  ├─► Files: coffee_maker/skills/*, tests/skills/*              │
│  └─► Status: In Progress → Complete → Merge                     │
│                                                                  │
│  Worktree 2: /path/to/MonolithicCoffeeMakerAgent-wt2           │
│  ├─► Branch: feature/us-021-dashboard-ui                        │
│  ├─► Agent: code_developer instance 2                           │
│  ├─► Files: coffee_maker/cli/dashboard.py, tests/cli/*         │
│  └─► Status: In Progress → Complete → Merge                     │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT INSTANCES                             │
│                                                                  │
│  code_developer instance 1 (worktree 1)                         │
│  ├─► Workspace: /path/to/MonolithicCoffeeMakerAgent-wt1        │
│  ├─► Branch: feature/us-020-skill-optimization                  │
│  ├─► Task: Implement US-020                                     │
│  └─► Isolation: Separate process, workspace, branch             │
│                                                                  │
│  code_developer instance 2 (worktree 2)                         │
│  ├─► Workspace: /path/to/MonolithicCoffeeMakerAgent-wt2        │
│  ├─► Branch: feature/us-021-dashboard-ui                        │
│  ├─► Task: Implement US-021                                     │
│  └─► Isolation: Separate process, workspace, branch             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

Due to length constraints, I'll provide a summary of the key components. The full detailed specification includes:

### 1. ParallelExecutionCoordinator

**File**: `coffee_maker/orchestrator/parallel_execution_coordinator.py`

**Key Classes**:
- `ParallelExecutionCoordinator`: Main coordinator class
- `WorktreeConfig`: Configuration for each worktree
- `ResourceMonitor`: CPU/memory monitoring

**Key Methods**:
- `execute_parallel_batch()`: Execute tasks in parallel
- `_validate_task_separation()`: Use architect skill to check conflicts
- `_create_worktrees()`: Create git worktrees
- `_spawn_instances()`: Start code_developer in each worktree
- `_monitor_instances()`: Track progress
- `_merge_completed_work()`: Merge to roadmap branch
- `_cleanup_worktrees()`: Remove worktrees

### 2. architect: task-separator Skill

**File**: `.claude/skills/architect/task-separator/skill.py`

**Purpose**: Analyze priorities to identify independent tasks

**Key Methods**:
- `analyze_task_separation()`: Main analysis method
- `_build_file_map()`: Extract file lists from specs
- `_find_safe_pairs()`: Identify non-conflicting tasks
- `_find_conflicts()`: Detect file overlaps

---

## Implementation Plan

### Total Timeline: ~3 weeks (109 hours)

**Phase 1: architect task-separator Skill** (2 days - 16 hours)
- Create skill structure
- Implement file extraction
- Implement conflict detection
- Write unit tests

**Phase 2: ParallelExecutionCoordinator Core** (3.25 days - 26 hours)
- Create coordinator class
- Implement worktree management
- Implement instance spawning
- Write unit tests

**Phase 3: Monitoring & Merging** (3.1 days - 25 hours)
- Implement instance monitoring
- Implement merge strategy
- Implement resource monitoring
- Write unit tests

**Phase 4: Integration with Orchestrator** (3 days - 24 hours)
- Integrate with work loop
- Create CLI command
- Write integration tests
- End-to-end testing

**Phase 5: Documentation & Deployment** (2.25 days - 18 hours)
- Update documentation
- Create user guide
- Code review & approval
- Deploy to production

---

## Testing Strategy

### Unit Tests (50 tests, >85% coverage)
- Task separation logic
- Worktree management
- Instance spawning
- Monitoring & merging

### Integration Tests (10 tests)
- Full parallel execution (2-3 instances)
- Worktree isolation verification
- Merge integration
- Error recovery

### Manual Testing
- Basic parallel execution
- Conflict handling
- Resource limits

---

## Performance Requirements

| Metric | Target | Baseline |
|--------|--------|----------|
| **Velocity Gain** | +75% (2 inst), +150% (3 inst) | 100% (1 inst) |
| **Task Separation** | <15s | N/A |
| **Worktree Creation** | <10s | N/A |
| **Merge Operation** | <15s | N/A |
| **CPU Usage** | <80% | <30% |
| **Memory Usage** | <80% | <20% |

---

## Risk Analysis

### High Risks

1. **Merge Conflicts** (Medium probability)
   - Mitigation: architect pre-validation, user notification

2. **Resource Exhaustion** (Medium probability)
   - Mitigation: Resource monitoring, max 3 instances

3. **Git Corruption** (Low probability)
   - Mitigation: Atomic operations, rollback on failure

---

## Success Criteria

### Functional
- ✅ 2-3 parallel instances run successfully
- ✅ Task separation >95% accurate
- ✅ >90% automatic merges (no conflicts)
- ✅ Zero data loss

### Performance
- ✅ +75% velocity with 2 instances
- ✅ +150% velocity with 3 instances
- ✅ Operations complete in target times

### Quality
- ✅ >85% test coverage
- ✅ All pre-commit hooks pass
- ✅ Architect review approved
- ✅ Documentation complete

---

## Appendix A: CLI Usage

```bash
# Enable parallel execution
poetry run orchestrator start --enable-parallel --max-instances 3

# Monitor progress
poetry run orchestrator status --parallel

# Stop gracefully
poetry run orchestrator parallel --stop

# Cleanup worktrees
poetry run orchestrator parallel --cleanup
```

---

## Appendix B: Troubleshooting

### Merge Conflicts
```bash
git status
git mergetool
git commit -m "Manual conflict resolution"
```

### Cleanup Stuck Worktrees
```bash
git worktree remove --force ../MonolithicCoffeeMakerAgent-wt1
git branch -D feature/us-020-*
```

---

**End of Specification**

**Files to Create**:
- `coffee_maker/orchestrator/parallel_execution_coordinator.py`
- `.claude/skills/architect/task-separator/skill.py`
- `.claude/skills/architect/task-separator/SKILL.md`
- `.claude/skills/architect/task-separator/__init__.py`
- `tests/unit/test_parallel_execution_coordinator.py`
- `tests/integration/test_parallel_worktrees.py`

**Next Steps**:
1. Review and approve this specification
2. Create ADR-015: Parallel Execution with Git Worktree
3. Assign implementation to code_developer (PRIORITY 23)
4. Begin Phase 1 implementation (architect task-separator skill)
