# SPEC-100: Unified Agent Commands Architecture - Master Specification

**Status**: Draft
**Created**: 2025-10-26
**Author**: architect
**Priority**: PRIORITY-TBD
**Related ADRs**: ADR-TBD
**Related CFRs**: CFR-007, CFR-013, CFR-014, CFR-015

## Executive Summary

Transform the MonolithicCoffeeMaker agent system from scattered, inline operations to a structured, command-driven architecture with enforced database domain boundaries. This is achieved through **evolutionary enhancement** - wrapping existing infrastructure rather than replacing it.

### Key Objectives

1. **Extract all agent responsibilities** into discrete, documented commands (98 total)
2. **Enforce database domain boundaries** using permission wrappers
3. **Reuse existing infrastructure** - no schema changes, wrap existing classes
4. **Document both implemented and planned features** from introspection and prompts
5. **Create clear audit trails** for all operations

### Approach

- **Evolutionary, not revolutionary** - Enhance existing system rather than replace
- **Use existing tables** - 30+ tables already well-structured
- **Wrap existing classes** - RoadmapDatabase and others remain intact
- **Progressive rollout** - One agent at a time, validated at each step

---

## Architecture Overview

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│              Agent Layer (Existing)                     │
│  ArchitectAgent, CodeDeveloperAgent, etc.               │
└─────────────────────┬───────────────────────────────────┘
                      │ uses
┌─────────────────────▼───────────────────────────────────┐
│           CommandLoader (NEW - SPEC-101)                │
│  - Loads agent-specific commands from .md files         │
│  - Validates permissions before execution               │
│  - Manages skill dependencies                           │
└─────────────────────┬───────────────────────────────────┘
                      │ executes
┌─────────────────────▼───────────────────────────────────┐
│             Command Classes (NEW - SPEC-101)            │
│  - Encapsulates single responsibility                   │
│  - Self-documenting via markdown metadata               │
│  - Enforces success criteria                            │
└─────────────────────┬───────────────────────────────────┘
                      │ uses
┌─────────────────────▼───────────────────────────────────┐
│          DomainWrapper (NEW - SPEC-101)                 │
│  - Enforces table ownership permissions                 │
│  - Adds audit trails to all operations                  │
│  - Wraps existing database classes                      │
└─────────────────────┬───────────────────────────────────┘
                      │ wraps
┌─────────────────────▼───────────────────────────────────┐
│    Existing Database Infrastructure (Unchanged)         │
│  RoadmapDatabase, NotificationDatabase, etc.            │
└─────────────────────────────────────────────────────────┘
```

---

## Database Domain Model

### Table Ownership Matrix

| Domain | Agent Owner | Tables | Write Permission |
|--------|-------------|--------|------------------|
| **Roadmap Management** | project_manager | roadmap_priority, roadmap_metadata, roadmap_audit | PROJECT_MANAGER only |
| **Specifications** | architect | specs_specification, specs_task, specs_task_dependency | ARCHITECT only |
| **Code Reviews** | code_reviewer | review_code_review | CODE_REVIEWER only |
| **Implementation** | code_developer | review_commit, metrics_subtask | CODE_DEVELOPER only |
| **Orchestration** | orchestrator | agent_lifecycle, orchestrator_task, orchestrator_bug, agent_message | ORCHESTRATOR only |
| **Shared Communication** | ALL | notifications, system_audit | ALL agents |

### Read Permission Model

| Agent | Read Access |
|-------|-------------|
| **project_manager** | ALL tables (monitoring role) |
| **orchestrator** | ALL tables (coordination role) |
| **assistant** | ALL tables (demo/help role) |
| **architect** | roadmap_priority, specs_*, review_code_review |
| **code_developer** | roadmap_priority, specs_*, review_commit |
| **code_reviewer** | specs_*, review_*, roadmap_priority |
| **user_listener** | roadmap_priority, notifications |
| **ux_design_expert** | roadmap_priority, specs_specification |

---

## Command Organization

### Directory Structure

```
.claude/commands/agents/
├── architect/           # 12 commands (SPEC-103)
├── code_developer/      # 14 commands (SPEC-104)
├── project_manager/     # 14 commands (SPEC-102)
├── code_reviewer/       # 13 commands (SPEC-105)
├── orchestrator/        # 15 commands (SPEC-106)
├── assistant/           # 11 commands (SPEC-107)
├── user_listener/       # 9 commands (SPEC-108)
└── ux_design_expert/    # 10 commands (SPEC-109)

Total: 98 commands across 8 agents
```

### Command Categories

| Category | Count | Examples |
|----------|-------|----------|
| Database Operations | 24 | create_spec, update_priority, record_commit |
| Workflow Orchestration | 15 | spawn_agent, detect_deadlocks, merge_worktrees |
| Code Quality | 18 | run_tests, check_style, security_scan |
| Project Management | 14 | verify_dod, monitor_prs, analyze_health |
| Communication | 12 | send_notification, route_message, delegate |
| UI/UX Design | 10 | design_interface, create_components |
| Documentation | 5 | generate_adr, update_guidelines |

---

## Child Specifications

### Phase 1: Foundation (SPEC-101)

**Purpose**: Core infrastructure for command system
**Complexity**: High
**Dependencies**: None
**Estimated Effort**: 3 days

**Components**:
- `DomainWrapper` class - Database access control
- `CommandLoader` class - Command discovery and loading
- `Command` base class - Command execution framework
- Permission system - Table ownership enforcement
- Audit trail system - Operation tracking

**Implementation Tasks**:
1. TASK-101-1: Implement DomainWrapper with permission enforcement
2. TASK-101-2: Implement CommandLoader with markdown parsing
3. TASK-101-3: Implement Command base class with execution framework
4. TASK-101-4: Create comprehensive test suite for foundation

**Context Size**: ~15% (foundation code + tests)

---

### Phase 2: Core Agents - Project Manager (SPEC-102)

**Purpose**: Implement 14 project_manager commands
**Complexity**: Medium
**Dependencies**: SPEC-101
**Estimated Effort**: 1 day

**Command Groups**:
1. **Roadmap Parsing** (4 commands)
   - parse_roadmap, update_priority_status, update_metadata, create_roadmap_audit
2. **Communication** (3 commands)
   - create_notification, process_notifications, send_agent_notification
3. **Monitoring** (4 commands)
   - monitor_github_prs, monitor_github_issues, analyze_project_health, detect_stale_priorities
4. **Verification** (3 commands)
   - verify_dod_puppeteer, strategic_planning, create_roadmap_report

**Implementation Tasks**:
1. TASK-102-1: Implement roadmap parsing commands (4 commands)
2. TASK-102-2: Implement communication commands (3 commands)
3. TASK-102-3: Implement monitoring commands (4 commands)
4. TASK-102-4: Implement verification commands (3 commands)

**Context Size**: ~20% per task (commands + related database code)

---

### Phase 2: Core Agents - Architect (SPEC-103)

**Purpose**: Implement 12 architect commands
**Complexity**: Medium
**Dependencies**: SPEC-101, SPEC-102
**Estimated Effort**: 1 day

**Command Groups**:
1. **Specification Management** (4 commands)
   - create_spec, link_spec_to_priority, validate_spec_completeness, update_spec
2. **Task Management** (3 commands)
   - create_implementation_tasks, define_task_dependencies, update_task_status
3. **Architecture Governance** (5 commands)
   - generate_adr, update_guidelines, update_cfrs, approve_dependency, merge_worktree_branches

**Implementation Tasks**:
1. TASK-103-1: Implement specification management commands (4 commands)
2. TASK-103-2: Implement task management commands (3 commands)
3. TASK-103-3: Implement architecture governance commands (5 commands)

**Context Size**: ~22% per task

---

### Phase 2: Core Agents - Code Developer (SPEC-104)

**Purpose**: Implement 14 code_developer commands
**Complexity**: Medium
**Dependencies**: SPEC-101, SPEC-102, SPEC-103
**Estimated Effort**: 1 day

**Command Groups**:
1. **Work Management** (3 commands)
   - claim_priority, load_spec, update_implementation_status
2. **Code Operations** (4 commands)
   - record_commit, complete_implementation, request_code_review, create_pull_request
3. **Quality Assurance** (7 commands)
   - run_test_suite, fix_failing_tests, run_pre_commit_hooks, implement_bug_fix, track_metrics, generate_coverage_report, update_claude_config

**Implementation Tasks**:
1. TASK-104-1: Implement work management commands (3 commands)
2. TASK-104-2: Implement code operations commands (4 commands)
3. TASK-104-3: Implement quality assurance commands (7 commands)

**Context Size**: ~23% per task

---

### Phase 3: Support Agents - Code Reviewer (SPEC-105)

**Purpose**: Implement 13 code_reviewer commands
**Complexity**: Medium
**Dependencies**: SPEC-101, SPEC-104
**Estimated Effort**: 1 day

**Command Groups**:
1. **Review Lifecycle** (3 commands)
   - detect_new_commits, generate_review_report, notify_architect
2. **Code Analysis** (6 commands)
   - check_style_compliance, run_security_scan, analyze_complexity, check_test_coverage, validate_type_hints, check_architecture_compliance
3. **Quality Reporting** (4 commands)
   - track_issue_resolution, generate_quality_score, review_documentation, validate_dod_compliance

**Implementation Tasks**:
1. TASK-105-1: Implement review lifecycle commands (3 commands)
2. TASK-105-2: Implement code analysis commands (6 commands)
3. TASK-105-3: Implement quality reporting commands (4 commands)

**Context Size**: ~22% per task

---

### Phase 3: Support Agents - Orchestrator (SPEC-106)

**Purpose**: Implement 15 orchestrator commands
**Complexity**: High (complex coordination logic)
**Dependencies**: SPEC-101, all agent specs
**Estimated Effort**: 1.5 days

**Command Groups**:
1. **Work Distribution** (3 commands)
   - find_available_work, create_parallel_tasks, coordinate_dependencies
2. **Agent Lifecycle** (5 commands)
   - spawn_agent_session, monitor_agent_lifecycle, kill_stalled_agent, auto_restart_agent, detect_deadlocks
3. **Worktree Management** (3 commands)
   - create_worktree, merge_completed_work, cleanup_worktrees
4. **System Monitoring** (4 commands)
   - route_inter_agent_messages, monitor_resource_usage, generate_activity_summary, handle_agent_errors

**Implementation Tasks**:
1. TASK-106-1: Implement work distribution commands (3 commands)
2. TASK-106-2: Implement agent lifecycle commands (5 commands)
3. TASK-106-3: Implement worktree management commands (3 commands)
4. TASK-106-4: Implement system monitoring commands (4 commands)

**Context Size**: ~20% per task

---

### Phase 4: UI & Utility Agents (SPEC-107)

**Purpose**: Implement assistant (11), user_listener (9), ux_design_expert (10) commands
**Complexity**: Low-Medium
**Dependencies**: SPEC-101
**Estimated Effort**: 2 days

**Grouped by Agent**:
- **assistant**: Demo creation, bug reporting, delegation
- **user_listener**: Intent classification, routing, conversation management
- **ux_design_expert**: Interface design, component libraries, Tailwind configs

**Implementation Tasks**:
1. TASK-107-1: Implement assistant commands (11 commands)
2. TASK-107-2: Implement user_listener commands (9 commands)
3. TASK-107-3: Implement ux_design_expert commands (10 commands)

**Context Size**: ~18% per task

---

### Phase 5: Migration & Testing (SPEC-108)

**Purpose**: Migration strategy, validation, rollback procedures
**Complexity**: Medium
**Dependencies**: All previous specs
**Estimated Effort**: 2 days

**Components**:
1. **Feature Flag System** - Gradual rollout per agent
2. **Parallel Operation** - Legacy and command modes
3. **Validation Framework** - Permission tests, workflow tests, performance tests
4. **Rollback Procedures** - Agent-by-agent rollback capability
5. **Documentation** - Migration guide, training materials

**Implementation Tasks**:
1. TASK-108-1: Implement feature flag system
2. TASK-108-2: Create validation test suite
3. TASK-108-3: Implement rollback procedures
4. TASK-108-4: Create migration documentation

**Context Size**: ~15% per task

---

## Implementation Timeline

| Phase | Days | Specs | Tasks | Commands |
|-------|------|-------|-------|----------|
| **Phase 1: Foundation** | 3 | SPEC-101 | 4 tasks | Infrastructure |
| **Phase 2: Core Agents** | 3 | SPEC-102, 103, 104 | 10 tasks | 40 commands |
| **Phase 3: Support Agents** | 2.5 | SPEC-105, 106 | 7 tasks | 28 commands |
| **Phase 4: UI Agents** | 2 | SPEC-107 | 3 tasks | 30 commands |
| **Phase 5: Migration** | 2 | SPEC-108 | 4 tasks | Testing/Docs |
| **TOTAL** | **12.5 days** | **7 specs** | **28 tasks** | **98 commands** |

---

## Success Criteria

### Technical Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Backward Compatibility** | 100% | Existing workflows pass |
| **Command Coverage** | 98/98 | All responsibilities mapped |
| **Permission Enforcement** | 100% | No unauthorized writes |
| **Audit Coverage** | 100% | All operations logged |
| **Performance Impact** | <5% | Wrapper overhead benchmark |
| **Test Coverage** | >90% | Unit + integration tests |
| **Context Budget** | <30% | Per-task prompt size |

### Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Debugging Speed** | 50% faster | Time to trace issues |
| **Onboarding Time** | 75% reduction | New developer ramp-up |
| **Permission Errors** | 90% reduction | Domain violations |
| **Documentation** | 100% | All commands documented |
| **Maintainability** | 2x improvement | Change complexity score |

---

## Risk Management

### High-Priority Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Breaking existing workflows** | Low | High | Parallel operation, feature flags, comprehensive testing |
| **Performance degradation** | Low | Medium | Benchmarking each phase, optimization budget |
| **Skill integration complexity** | Medium | Medium | Progressive testing, skill isolation |
| **Context budget violations** | Medium | High | Careful task sizing, validation before implementation |

### Rollback Strategy

Each phase can be rolled back independently via feature flags:

```python
AGENT_COMMAND_FLAGS = {
    "project_manager": True,   # Commands enabled
    "architect": False,        # Still using legacy
    "code_developer": False,   # Still using legacy
    # ... etc
}
```

---

## Validation Checkpoints

After each phase:
1. ✅ All permission tests pass
2. ✅ Existing workflows function correctly
3. ✅ Audit trail complete and accurate
4. ✅ Performance within acceptable range (<5% overhead)
5. ✅ No data corruption or integrity issues
6. ✅ Context budget compliance (<30% per task)

---

## Dependencies

### Python Packages

| Package | Purpose | Approval Status |
|---------|---------|-----------------|
| `frontmatter` | Parse markdown command definitions | ✅ Approved (Tier 1) |
| `pyyaml` | YAML parsing for command metadata | ✅ Approved (Tier 1) |

### Existing Infrastructure (No Changes Required)

- `RoadmapDatabase` - Database access layer
- `NotificationDatabase` - Inter-agent communication
- `AgentRegistry` - Singleton enforcement (CFR-000)
- `SkillLoader` - Skill system integration
- Git worktree system - Parallel execution

---

## Related Documents

### Strategic Documents
- [docs/UNIFIED_AGENT_COMMANDS_COMPLETE_PLAN.md](../../UNIFIED_AGENT_COMMANDS_COMPLETE_PLAN.md) - Source plan
- [docs/roadmap/ROADMAP.md](../../roadmap/ROADMAP.md) - Priority tracking
- [docs/AGENT_OWNERSHIP.md](../../AGENT_OWNERSHIP.md) - Agent boundaries

### Technical References
- [docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md](SPEC-070-dependency-pre-approval-matrix.md) - Dependency approval
- [docs/architecture/guidelines/GUIDELINE-004-git-tagging-workflow.md](../guidelines/GUIDELINE-004-git-tagging-workflow.md) - Git workflow
- [docs/CFR-015-CENTRALIZED-DATABASE-STORAGE.md](../../CFR-015-CENTRALIZED-DATABASE-STORAGE.md) - Database organization

### CFRs Referenced
- **CFR-000**: Singleton Agent Enforcement
- **CFR-007**: Context Budget (<30% per task)
- **CFR-009**: Sound Notifications (user_listener only)
- **CFR-013**: Git Workflow (roadmap branch, worktrees)
- **CFR-014**: Database Tracing (SQLite required)
- **CFR-015**: Centralized Database Storage (data/ directory)

---

## Next Steps

1. **Review and approve** this master specification
2. **Create detailed child specs** (SPEC-101 through SPEC-108)
3. **Implement Phase 1** (Foundation infrastructure)
4. **Validate** foundation with comprehensive tests
5. **Proceed sequentially** through phases 2-5

---

**Specification Status**: Draft - Awaiting Review
**Estimated Total Effort**: 12.5 days
**Total Commands**: 98
**Total Implementation Tasks**: 28
**Context Budget Compliance**: All tasks <30%
