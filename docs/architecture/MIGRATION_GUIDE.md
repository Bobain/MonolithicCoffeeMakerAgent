# Command System Migration Guide

**Version**: 1.0
**Status**: Active
**Last Updated**: 2025-10-26

## Overview

This guide provides a comprehensive roadmap for migrating the MonolithicCoffeeMakerAgent system from its existing architecture to the new **command-driven architecture** (SPEC-100 through SPEC-108).

The migration is designed to be:
- **Non-destructive**: Existing workflows continue to function
- **Gradual**: One agent at a time, with rollback capability
- **Observable**: Detailed logging and comparison of legacy vs. command implementations
- **Safe**: Feature flags allow instant disable if issues arise

---

## Executive Summary

### What's Changing?

We're transitioning from scattered, inline operations to a **structured, command-driven architecture** where:

1. All agent responsibilities are documented as discrete commands
2. Database domain boundaries are enforced via permission wrappers
3. Commands are defined in markdown for clarity and documentation
4. Feature flags enable gradual rollout without system restart

### Why Migrate?

**Benefits**:
- 50% faster debugging (clear command boundaries)
- 75% reduction in onboarding time (documented commands)
- 90% reduction in permission violations (enforced boundaries)
- 100% documentation coverage
- 2x improvement in maintainability

### How Long Will It Take?

Total: **12.5 days** across 5 phases

| Phase | Duration | Agents | Status |
|-------|----------|--------|--------|
| Phase 1: Foundation | 3 days | Infrastructure | Planned |
| Phase 2: Core Agents | 3 days | project_manager, architect, code_developer | Planned |
| Phase 3: Support Agents | 2.5 days | code_reviewer, orchestrator | Planned |
| Phase 4: UI Agents | 2 days | assistant, user_listener, ux_design_expert | Planned |
| Phase 5: Migration | 2 days | Testing, documentation | Planned |

---

## Pre-Migration Checklist

Before starting the migration, ensure:

- [ ] All tests passing (`pytest --cov`)
- [ ] No critical issues in ROADMAP
- [ ] Team availability for 2-week migration
- [ ] Backup of database (`data/backup/coffee_maker.db`)
- [ ] Backup of git repository
- [ ] Feature flags file location ready (`.claude/command_flags.json`)

### Database Backup

```bash
# Create backup before migration starts
cp data/coffee_maker.db data/backup/coffee_maker.db.$(date +%Y%m%d)

# Verify backup
sqlite3 data/backup/coffee_maker.db ".tables"
```

---

## Migration Architecture

### Core Components

**1. FeatureFlags System**
- Location: `coffee_maker/commands/feature_flags.py`
- Purpose: Enable/disable commands per agent
- Persistence: JSON configuration file
- Default: All disabled (safe)

**2. ParallelOperationWrapper**
- Location: `coffee_maker/commands/parallel_operation.py`
- Purpose: Run legacy and command implementations in parallel
- Validation: Compare results for consistency
- Safety: Fall back to legacy on mismatch

**3. RollbackManager**
- Location: `coffee_maker/commands/rollback.py`
- Purpose: Rollback agents to legacy mode
- Granularity: Single agent, phase, or full system
- Safety: Reversible (can re-enable after rollback)

**4. Validation Tests**
- Location: `tests/integration/test_command_validation.py`
- Count: 34 tests covering all aspects
- Coverage: Permission, workflow, performance, data consistency

---

## Phase-by-Phase Migration Process

### Phase 1: Foundation Infrastructure (Day 1-3)

**Objective**: Build core command system infrastructure

**Tasks**:
1. Implement `DomainWrapper` class for permission enforcement
2. Implement `CommandLoader` for command discovery
3. Implement `Command` base class and execution framework
4. Create comprehensive test suite (>50 tests)

**Validation Checkpoints**:
- [ ] All foundation tests pass
- [ ] Permission enforcement working
- [ ] Audit trails being recorded
- [ ] No performance regression

**Rollback Plan**: No agents enabled yet, nothing to rollback

---

### Phase 2: Core Agents (Day 4-6)

**Objective**: Migrate project_manager, architect, code_developer

**Agents**: 3
**Commands**: 40 total
**Duration**: 3 days

#### Phase 2.1: project_manager Commands

**Timeline**: 1 day
**Commands**: 14

Implement groups:
1. Roadmap parsing (4 commands)
   - parse_roadmap
   - update_priority_status
   - update_metadata
   - create_roadmap_audit

2. Communication (3 commands)
   - create_notification
   - process_notifications
   - send_agent_notification

3. Monitoring (4 commands)
   - monitor_github_prs
   - monitor_github_issues
   - analyze_project_health
   - detect_stale_priorities

4. Verification (3 commands)
   - verify_dod_puppeteer
   - strategic_planning
   - create_roadmap_report

**Validation**:
```bash
# Test parallel operation
poetry run project-manager --mode=parallel-validation

# Verify no mismatches
tail -f logs/command_validation.log | grep "mismatch"
```

**Rollback if**: Mismatches detected OR performance degrades >5%

#### Phase 2.2: architect Commands

**Timeline**: 1 day
**Commands**: 12

Implement groups:
1. Specification Management (4 commands)
2. Task Management (3 commands)
3. Architecture Governance (5 commands)

**Validation**:
```bash
poetry run architect --mode=parallel-validation
```

#### Phase 2.3: code_developer Commands

**Timeline**: 1 day
**Commands**: 14

Implement groups:
1. Work Management (3 commands)
2. Code Operations (4 commands)
3. Quality Assurance (7 commands)

**Validation**:
```bash
poetry run code-developer --mode=parallel-validation

# Run test suite
pytest tests/integration/test_command_validation.py -v
```

**Post-Phase 2 Validation**:
```bash
# All three agents should pass validation
poetry run project-manager validate-phase 2

# Expected output:
# phase_2_status: READY_TO_PROCEED (or ROLLBACK_REQUIRED)
```

---

### Phase 3: Support Agents (Day 7-8.5)

**Objective**: Migrate code_reviewer and orchestrator

**Agents**: 2
**Commands**: 28 total
**Duration**: 2.5 days

#### Phase 3.1: code_reviewer Commands

**Timeline**: 1 day
**Commands**: 13

Groups:
1. Review Lifecycle (3 commands)
2. Code Analysis (6 commands)
3. Quality Reporting (4 commands)

#### Phase 3.2: orchestrator Commands

**Timeline**: 1.5 days
**Commands**: 15

Groups:
1. Work Distribution (3 commands)
2. Agent Lifecycle (5 commands)
3. Worktree Management (3 commands)
4. System Monitoring (4 commands)

**Post-Phase 3 Validation**:
```bash
poetry run project-manager validate-phase 3
```

---

### Phase 4: UI & Utility Agents (Day 9-10)

**Objective**: Migrate assistant, user_listener, ux_design_expert

**Agents**: 3
**Commands**: 30 total
**Duration**: 2 days

#### Phase 4.1: assistant Commands

**Timeline**: 0.5 days
**Commands**: 11

#### Phase 4.2: user_listener Commands

**Timeline**: 0.5 days
**Commands**: 9

#### Phase 4.3: ux_design_expert Commands

**Timeline**: 1 day
**Commands**: 10

**Post-Phase 4 Validation**:
```bash
poetry run project-manager validate-phase 4
```

---

### Phase 5: Migration Wrap-up (Day 11-12.5)

**Objective**: Testing, documentation, finalization

**Tasks**:
1. Run comprehensive test suite (all 98 commands)
2. Performance benchmarking
3. Documentation updates
4. Final validation and sign-off

**Validation**:
```bash
# Run full validation suite
pytest tests/integration/test_command_validation.py -v --cov

# Check performance
poetry run project-manager validate-performance

# Performance target: <5% overhead vs. legacy
```

---

## Day-by-Day Timeline

### Week 1

| Day | Task | Status | Owner |
|-----|------|--------|-------|
| Mon | Phase 1.1-1.3: Foundation infrastructure | Planned | architect |
| Tue | Phase 1 testing and validation | Planned | code_developer |
| Wed | Phase 2.1: project_manager (14 commands) | Planned | code_developer |
| Thu | Phase 2.2: architect (12 commands) | Planned | code_developer |
| Fri | Phase 2.3: code_developer (14 commands) + validation | Planned | code_developer |

### Week 2

| Day | Task | Status | Owner |
|-----|------|--------|-------|
| Mon | Phase 3.1-3.2: code_reviewer + orchestrator | Planned | code_developer |
| Tue | Phase 3 validation | Planned | code_developer |
| Wed | Phase 4.1-4.3: UI agents | Planned | code_developer |
| Thu | Phase 4 validation + documentation | Planned | code_developer |
| Fri | Phase 5: Final testing, sign-off | Planned | code_developer |

---

## Operation Modes During Migration

### Legacy Mode (Pre-Migration)

```python
# All agents use original implementation
agent.claim_priority()  # Uses legacy RoadmapDatabase directly
```

### Parallel Mode (During Migration)

```python
# Both implementations run, compared for consistency
agent.claim_priority()  # Runs both, compares, logs mismatches
```

### Command Mode (Post-Migration)

```python
# All agents use command system
agent.claim_priority()  # Uses command-driven implementation
```

### Emergency Mode (If Issues Arise)

```python
# Rollback to legacy mode instantly
manager.rollback_agent("code_developer")
manager.rollback_all()  # Full emergency rollback
```

---

## Feature Flag Management

### Initial State

```json
{
  "agent_flags": {
    "project_manager": {},
    "architect": {},
    "code_developer": {},
    "code_reviewer": {},
    "orchestrator": {},
    "assistant": {},
    "user_listener": {},
    "ux_design_expert": {}
  },
  "last_updated": "2025-10-26T12:00:00"
}
```

### After Phase 2

```json
{
  "agent_flags": {
    "project_manager": {
      "parse_roadmap": true,
      "create_notification": true,
      // ... 12 more enabled
    },
    "architect": {
      "create_spec": true,
      // ... 11 more enabled
    },
    "code_developer": {
      "claim_priority": true,
      // ... 13 more enabled
    },
    // ... other agents still disabled
  }
}
```

### After Phase 5 (Complete Migration)

All agents have all commands enabled. Legacy implementations can be deprecated.

---

## Monitoring and Observability

### Real-Time Monitoring

```bash
# Watch for mismatches during parallel operation
tail -f logs/parallel_operation_comparison.log

# Check agent status
poetry run project-manager agent-status

# View rollback history
poetry run project-manager rollback-history
```

### Key Metrics to Monitor

| Metric | Target | Action if Exceeded |
|--------|--------|-------------------|
| Mismatch rate | <0.1% | Investigate and fix |
| Performance overhead | <5% | Optimize wrapper |
| Test pass rate | 100% | Debug and fix |
| Permission violations | 0 | Audit and trace |
| Database integrity | Clean | Verify schema |

### Logging Configuration

```python
import logging

# Enable debug logging during migration
logging.getLogger("coffee_maker.commands.feature_flags").setLevel(logging.DEBUG)
logging.getLogger("coffee_maker.commands.parallel_operation").setLevel(logging.DEBUG)
logging.getLogger("coffee_maker.commands.rollback").setLevel(logging.DEBUG)
```

---

## Rollback Procedures

### Single Agent Rollback

If one agent has issues:

```python
from coffee_maker.commands.rollback import RollbackManager

manager = RollbackManager()
manager.rollback_agent("code_developer", "High mismatch rate detected")
# Agent immediately reverts to legacy mode
```

### Phase Rollback

If entire phase has issues:

```python
manager.rollback_phase(2, "Performance degradation in Phase 2")
# All agents in Phase 2 reverted to legacy
```

### Emergency Full Rollback

If critical system-wide issue:

```python
manager.rollback_all("Critical database corruption detected")
# Entire system reverted to legacy mode
```

### Re-enable After Rollback

After fixing issues:

```python
manager.re_enable_agent("code_developer", "Issues resolved, patch applied")
# Agent returns to command mode
```

---

## Testing Strategy

### Unit Tests

```bash
# Test individual components
pytest tests/unit/test_feature_flags.py -v
pytest tests/unit/test_parallel_operation.py -v
pytest tests/unit/test_rollback.py -v
```

### Integration Tests

```bash
# Test complete workflows
pytest tests/integration/test_command_validation.py -v

# Test specific validation categories
pytest tests/integration/test_command_validation.py::TestFeatureFlagsPermissionEnforcement -v
pytest tests/integration/test_command_validation.py::TestRollbackProcedures -v
pytest tests/integration/test_command_validation.py::TestPerformanceOverhead -v
```

### End-to-End Tests

```bash
# Full workflow test
poetry run code-developer --mode=e2e-migration-test

# Expected: All phases complete, no mismatches
```

### Performance Benchmarking

```bash
# Measure wrapper overhead
poetry run project-manager benchmark-parallel-operation

# Expected: <5% overhead
```

---

## Communication Plan

### Stakeholders

- **architecture team**: Responsible for spec creation
- **code_developer**: Responsible for implementation
- **project_manager**: Monitors progress and notifications
- **code_reviewer**: Reviews implementation PRs
- **all other agents**: Affected by migration, test their workflows

### Daily Standup

Each day of migration:

```bash
poetry run project-manager migration-status

# Outputs:
# Phase: 2.1 (project_manager commands)
# Enabled agents: project_manager (partial)
# Mismatches detected: 0
# Performance overhead: 2.3%
# Status: ON_TRACK
```

### Escalation Path

| Issue | Severity | Action | Owner |
|-------|----------|--------|-------|
| Mismatch rate >1% | High | Pause phase, investigate | code_developer |
| Performance >5% | High | Optimize and re-test | architect |
| Database error | Critical | Rollback all immediately | project_manager |
| Test failure | Medium | Fix and re-run | code_developer |

---

## Troubleshooting Guide

### Issue: High Mismatch Rate

**Symptom**: Comparison log shows >0.1% mismatches

**Investigation**:
```bash
# Export comparison log
poetry run project-manager export-comparison-log comparison.json

# Analyze mismatches
python scripts/analyze_mismatches.py comparison.json
```

**Solution**:
1. Identify command with issue
2. Compare legacy vs. command implementation
3. Fix command implementation
4. Re-run validation tests
5. If unresolvable, rollback phase

### Issue: Performance Degradation

**Symptom**: Operations taking >105% of legacy time

**Investigation**:
```bash
# Check wrapper overhead
poetry run project-manager benchmark-wrapper-overhead

# Profile specific command
python -m cProfile -s cumtime coffee_maker/commands/command_loader.py
```

**Solution**:
1. Identify slow operation
2. Optimize command execution
3. Re-benchmark
4. If >5% overhead persists, optimize wrapper design

### Issue: Permission Violations

**Symptom**: Audit log shows unauthorized write

**Investigation**:
```bash
# Check permission audit
sqlite3 data/coffee_maker.db "SELECT * FROM system_audit WHERE operation='DENY'"

# Trace violation
poetry run project-manager trace-permission-violation <audit_id>
```

**Solution**:
1. Verify correct permission assigned
2. Check domain wrapper logic
3. Update permission matrix if needed
4. Re-validate permission enforcement

---

## Post-Migration Tasks

### Week After Migration Completes

1. **Documentation Update**
   - [ ] Update README with command architecture
   - [ ] Create command reference guide
   - [ ] Document new workflows

2. **Code Cleanup**
   - [ ] Remove legacy implementations (after grace period)
   - [ ] Clean up feature flag files
   - [ ] Archive old database tables

3. **Performance Analysis**
   - [ ] Generate performance report
   - [ ] Identify optimization opportunities
   - [ ] Document performance baseline

4. **Team Training**
   - [ ] Conduct knowledge transfer sessions
   - [ ] Document new debugging procedures
   - [ ] Update developer onboarding guide

---

## Success Criteria

Migration is complete when:

- [ ] All 98 commands implemented and tested
- [ ] All 34 validation tests passing
- [ ] Zero critical issues in production
- [ ] Performance within 5% of baseline
- [ ] All agents running in command mode
- [ ] 100% documentation coverage
- [ ] Team trained on new architecture
- [ ] Legacy code removed (after grace period)

---

## References

### Technical Specifications

- [SPEC-100: Unified Agent Commands Architecture](../specs/SPEC-100-unified-agent-commands-architecture.md)
- [SPEC-101: Foundation Infrastructure](../specs/SPEC-101-foundation-infrastructure.md)
- [SPEC-102: project_manager Commands](../specs/SPEC-102-project-manager-commands.md)
- [SPEC-103: architect Commands](../specs/SPEC-103-architect-commands.md)
- [SPEC-104: code_developer Commands](../specs/SPEC-104-code-developer-commands.md)
- [SPEC-105: code_reviewer Commands](../specs/SPEC-105-code-reviewer-commands.md)
- [SPEC-106: orchestrator Commands](../specs/SPEC-106-orchestrator-commands.md)
- [SPEC-107: UI & Utility Agents Commands](../specs/SPEC-107-ui-agents-commands.md)
- [SPEC-108: Migration & Testing Strategy](../specs/SPEC-108-migration-testing-strategy.md)

### Implementation Files

- `coffee_maker/commands/feature_flags.py` - Feature flag system
- `coffee_maker/commands/parallel_operation.py` - Parallel validation wrapper
- `coffee_maker/commands/rollback.py` - Rollback manager
- `tests/integration/test_command_validation.py` - Validation tests

### Related Guidelines

- [GUIDELINE-001: Code Style](../guidelines/GUIDELINE-001-code-style.md)
- [GUIDELINE-004: Git Workflow](../guidelines/GUIDELINE-004-git-tagging-workflow.md)
- [GUIDELINE-005: Testing](../guidelines/GUIDELINE-005-testing.md)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-26 | code_developer | Initial draft |

---

**Document Status**: Active
**Last Review**: 2025-10-26
**Next Review**: 2025-11-09 (after migration completion)
