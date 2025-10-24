# Critical Functional Requirements (CFRs) - System Invariants

**Version**: 3.0 (Hierarchical Summary)
**Date**: 2025-10-24
**Status**: Active
**Owner**: project_manager

---

## Purpose

These are CRITICAL system rules that MUST be enforced at ALL times. Violations MUST trigger:
1. Stop the violating action
2. Expose the problem to the user
3. Provide safe alternatives

**Full details**: See `data/cfr_extraction.json` for complete implementation details, code locations, and enforcement mechanisms.

---

## CFR Index - Quick Reference

| CFR | Title | Core Rule |
|-----|-------|-----------|
| **CFR-000** | **Master: Prevent File Conflicts** | EXACTLY ONE agent writes to any file at any moment |
| CFR-001 | Document Ownership | Each file has EXACTLY ONE owner |
| CFR-002 | Agent Role Boundaries | Each agent has EXACTLY ONE primary role |
| CFR-003 | No Overlap - Documents | No two agents can own same directory/file |
| CFR-004 | No Overlap - Responsibilities | No overlapping primary responsibilities |
| CFR-005 | Ownership Includes Maintenance | Owners must maintain their files |
| CFR-006 | Lessons Learned Capture | Document and apply all key lessons |
| CFR-007 | Agent Context Budget | Core materials ≤30% of context window |
| CFR-008 | Architect Creates Specs | ONLY architect creates specs, NEVER code_developer |
| CFR-009 | Sound Notifications | ONLY user_listener uses sound |
| CFR-010 | Architect Reviews Specs | Continuously review and improve specs |
| ~~CFR-011~~ | ~~Code Analysis Integration~~ | DEPRECATED - code-searcher agent deleted |
| CFR-012 | Agent Responsiveness | Prioritize immediate requests over background work |
| CFR-013 | Roadmap Branch Only | ALL agents work on `roadmap` branch ONLY |
| CFR-014 | Database Tracing | ALL orchestrator activities in SQLite database |
| CFR-015 | Continuous Planning Loop | System must always have work available |
| CFR-016 | Incremental Implementation | Break specs into small implementation steps |

---

## Core CFRs (Most Critical)

### CFR-000: PREVENT FILE CONFLICTS (Master Requirement) 🔴

**Rule**: EXACTLY ZERO or ONE agent writing to any file at any moment. NEVER two agents writing simultaneously.

**Why**: File conflicts cause data corruption, lost work, merge conflicts, system failure.

**Prevention**: All other CFRs exist to prevent this.

**Implementation**:
- `coffee_maker/autonomous/agent_registry.py` - Singleton enforcement
- `coffee_maker/autonomous/ace/file_ownership.py` - Ownership checks
- `docs/AGENT_SINGLETON_ARCHITECTURE.md` - Architecture

**Related**: CFR-001, CFR-002, CFR-003, CFR-004, CFR-013, CFR-014

---

### CFR-001: Document Ownership Boundaries

**Rule**: Each directory/file has EXACTLY ONE owner. Only owner can modify. Others are READ-ONLY.

**Why**: Implements CFR-000 by ensuring single writer per file.

**Ownership Matrix**:
| Owner | Files Owned |
|-------|-------------|
| code_developer | `.claude/**`, `coffee_maker/**`, `tests/**`, `scripts/**` |
| project_manager | `docs/roadmap/**`, `docs/templates/**`, `docs/tutorials/**`, `docs/*.md` |
| architect | `docs/architecture/**`, `pyproject.toml`, `poetry.lock` |
| generator | `docs/generator/**` |
| reflector | `docs/reflector/**` |
| curator | `docs/curator/**` |
| user_listener | `data/user_interpret/**` |

**Enforcement**: `FileOwnership.check_ownership()` in generator before writes. Auto-delegates to correct owner.

**Related**: CFR-000, CFR-003, CFR-005

---

### CFR-002: Agent Role Boundaries

**Rule**: Each agent has EXACTLY ONE primary role. NO overlaps.

**Why**: Role confusion leads to duplicate work and conflicts.

**Roles**:
- **user_listener**: User Interface (ONLY UI)
- **project_manager**: Strategic Planning (WHAT/WHY)
- **architect**: Technical Design (HOW)
- **code_developer**: Implementation (DOING)
- **assistant**: Demos + Documentation + Dispatch
- **code-reviewer**: QA and code reviews
- **ux-design-expert**: UI/UX design
- **generator**: Ownership Enforcement + Trace Capture
- **reflector**: Insight Extraction
- **curator**: Playbook Maintenance

**Enforcement**: Verify work matches agent's primary role before delegation.

**Related**: CFR-000, CFR-004

---

### CFR-008: Architect Creates ALL Specs

**Rule**: ONLY architect creates technical specifications. code_developer MUST NEVER create specs.

**Why**: Architect needs full ROADMAP context. Multiple spec creators cause inconsistent patterns.

**Flow**: architect reviews ROADMAP → creates ALL specs proactively → code_developer implements (no spec creation)

**Violation Prevention**: If code_developer needs spec: Block immediately, delegate to architect

**Implementation**: `coffee_maker/orchestrator/daemon.py` - `_ensure_technical_spec()` checks existence

**Related**: CFR-002, CFR-010, CFR-016

---

### CFR-013: Roadmap Branch Only

**Rule**: ALL agents MUST work on `roadmap` branch at ALL times. NO branch switching/creation.

**Why**: Single source of truth, prevents branch conflicts, simplifies workflow, prevents work loss.

**Allowed**:
- `git status`, `git add`, `git commit`, `git push/pull` on roadmap
- Temporary worktrees: `roadmap-implementation_task-*` (orchestrator only, must merge + delete after)

**Forbidden**:
- `git checkout <other-branch>`
- `git checkout -b <new-branch>`
- Working on main or feature/* branches

**Exception**: Orchestrator MAY create temporary worktree branches for parallel execution. MUST merge back and delete after each task.

**Enforcement**: Pre-commit hook validates current branch. `.pre-commit-config.yaml` + `coffee_maker/autonomous/git_operations.py`

**Related**: CFR-000, CFR-014

---

## Operational CFRs

### CFR-003: No Overlap - Documents

**Rule**: No two agents can own same directory/file. Ownership is EXCLUSIVE.

**Why**: Shared ownership creates ambiguity, leading to concurrent modifications.

**Enforcement**: CFR-001 ownership matrix is source of truth. Changes require user approval.

**Related**: CFR-000, CFR-001

---

### CFR-004: No Overlap - Responsibilities

**Rule**: No two agents can have overlapping primary responsibilities.

**Why**: Responsibility confusion leads to duplicate work and inefficiency.

**Enforcement**: Check responsibility matrix before work assignment. See `docs/AGENT_OWNERSHIP.md`

**Related**: CFR-000, CFR-002

---

### CFR-005: Ownership Includes Maintenance

**Rule**: File owners MUST maintain their files (clean, simplify, update, improve).

**Why**: Without maintenance, directories become cluttered and unmaintainable.

**Maintenance Duties** (Examples):
- **code_developer**: Refactor complex code, remove unused functions, clean temp files
- **project_manager**: Archive completed priorities, consolidate duplicates
- **architect**: Archive superseded ADRs, update specs with system changes

**Triggers**: Directory >50 files, file >2000 lines, architect identifies debt, >4h maintenance needed

**Related**: CFR-001, CFR-007

---

### CFR-006: Lessons Learned Must Be Captured and Applied

**Rule**: All key lessons (failures + successes) MUST be documented and actively used.

**Why**: Prevents repeating same mistakes endlessly.

**Lesson Types**:
- `WORKFLOW_FAILURE_*.md` - Process breakdowns
- `TECHNICAL_FAILURE_*.md` - Architecture/implementation errors
- `USER_FRUSTRATION_*.md` - UX gaps
- `SUCCESS_PATTERN_*.md` - Effective patterns
- `LESSONS_YYYY_MM.md` - Monthly summaries

**Location**: `docs/roadmap/learnings/` (owner: project_manager)

**Enforcement**: Capture within 24h of failure. Update docs within 1 week. Monthly summaries.

**Related**: CFR-001, CFR-005

---

### CFR-007: Agent Context Budget (30% Maximum)

**Rule**: Agent core materials MUST fit in ≤30% of context window.

**Why**: If core materials consume too much, agents have no room to work.

**Example**: 200K context → Max 60K core materials (30%), min 140K work space (70%)

**Remediation Strategies**:
1. Sharpen main knowledge document
2. Create detail documents (read on-demand)
3. Use line number references
4. Compress verbose examples

**Enforcement**: Measurement at agent startup. If >30%: VIOLATION, agent cannot start.

**Related**: CFR-001, CFR-005

---

### CFR-009: Sound Notifications

**Rule**: ONLY user_listener uses sound notifications (sound=True). Background agents MUST use sound=False.

**Why**: Prevents notification spam. Only user-facing interactions should produce audio.

**Allowed**: user_listener: `sound=True`

**Forbidden**: code_developer, architect, project_manager, assistant, all background agents: `sound=False` always

**Enforcement**: NotificationDB validates sound parameter based on requesting agent.

**Related**: CFR-002

---

### CFR-010: Architect Continuously Reviews Specs

**Rule**: Architect MUST regularly re-read ALL specs and FULL ROADMAP to proactively improve.

**Why**: Specs improve with fresh perspectives. Early complexity detection prevents wasted effort.

**Frequency**:
- Daily: Quick ROADMAP review
- Weekly: Deep review of all active specs
- Before each new spec: Review existing specs for patterns
- After implementation: Review spec vs what was built

**Deliverables**: Weekly improvement reports, updated specs, new ADRs

**Related**: CFR-001, CFR-008

---

### CFR-012: Agent Responsiveness Priority

**Rule**: ALL agents MUST prioritize immediate requests OVER continuous background work.

**Why**: Team collaboration takes precedence. Users/agents shouldn't wait for background loops.

**Priority Order**:
1. **HIGHEST**: User requests
2. **HIGH**: Inter-agent delegation requests
3. **NORMAL**: Continuous background work

**Implementation**: At loop start, check for new requests. If found, INTERRUPT background work immediately.

**Enforcement**: Every continuous loop MUST implement `check_for_immediate_requests()`

**Related**: CFR-000, CFR-008

---

### CFR-014: Database Tracing for Orchestrator

**Rule**: ALL orchestrator activities MUST be persisted in SQLite database. JSON files FORBIDDEN.

**Why**: Cannot measure velocity without historical data. JSON files cause data integrity bugs.

**Required Tables**:
- `agent_lifecycle` - PID, agent_type, task_id, spawned_at, completed_at, duration_ms
- `planning_loop_metrics` - Planned priorities, alerts, timing data

**Required Views**:
- `active_agents`, `agent_velocity`, `agent_bottlenecks`, `priority_timeline`

**Forbidden**: JSON files for `agent_state.json`, `work_loop_state.json`

**Database**: `data/orchestrator.db`

**Related**: CFR-000, CFR-013, CFR-015

---

### CFR-015: Continuous Planning Loop

**Rule**: System MUST continuously plan, create specs, implement code. ROADMAP must NEVER become empty.

**Why**: System designed for 24/7 operation. Empty ROADMAP with no planning is failure.

**Buffer Requirement**: project_manager MUST maintain 3-5 planned priorities ahead

**Architect SLA**: Create specs within 2 hours of new priorities (95% SLA target)

**Orchestrator Checks**:
1. Planned priorities exist? (count ≥ 1)
2. Specs ready? (has_spec=true)
3. Wait or stop decision

**Planning Triggers**: Priority completion, every 30min, ROADMAP low notification, user request

**Implementation**: `coffee_maker/orchestrator/continuous_work_loop.py`

**Related**: CFR-008, CFR-013, CFR-014

---

### CFR-016: Incremental Implementation Steps

**Rule**: Technical specs MUST be divided into small, incremental steps (single iteration each).

**Why**: Complex features naturally require multiple steps. Enables continuous progress.

**Key Principle**: Track CONSECUTIVE no-progress attempts, not total attempts. Progress resets counter.

**Iteration Logic**: Unlimited iterations while making file changes. Only give up after 3 CONSECUTIVE no-progress attempts.

**Architect Responsibilities**:
- Divide specs into phases (1-2 hours max each)
- Provide clear, actionable steps
- Estimate time per phase
- Document sequential dependencies

**Example**: Auth system: Phase 1 (DB schema) → Phase 2 (Auth logic) → Phase 3 (API endpoints) → Phase 4 (Tests)

**Related**: CFR-008, CFR-010

---

## Deprecated CFRs

### ~~CFR-011: Architect Must Integrate Code Analysis Findings Daily~~ ❌

**Status**: DEPRECATED (2025-10-24)

**Reason**: code-searcher agent was deleted. Code analysis now handled by:
- **code-reviewer**: Generates implementation-level code review summaries
- **architect**: Reads code_reviewer summaries and creates/improves specs
- **assistant**: Uses code-forensics and security-audit skills for deep analysis

**Replacement Workflow**:
1. code_reviewer generates summaries after implementations
2. architect reads summaries via `RoadmapDatabase.get_unreviewed_code_reviews()`
3. architect creates refactoring tasks or improves specs based on findings
4. architect marks reviews as read via `mark_review_as_read()`

**Original Intent**: Architect should continuously integrate code quality findings into specs to prevent technical debt.

**New Implementation**: See `.claude/agents/architect.md` - Workflow 6: Reading Code Review Summaries

---

## CFR Enforcement Layers

All CFRs are enforced through multiple layers:

**Layer 1: Tool-Level Enforcement**
- File ownership checks in generator
- Database permission checks
- Singleton agent registry

**Layer 2: Pre-Commit Hooks**
- CFR-013: Branch validation
- CFR-007: Context budget checks (future)

**Layer 3: Agent Self-Checks**
- Agents validate before actions
- Auto-delegation to correct owner
- Permission requests to user

**Layer 4: User Notification**
- Violations exposed to user
- Safe alternatives provided
- User approval required for exceptions

---

## Coverage Map

| Category | CFRs |
|----------|------|
| **File Conflicts** | CFR-000, CFR-001, CFR-003, CFR-014 |
| **Agent Coordination** | CFR-002, CFR-004, CFR-012 |
| **Maintenance** | CFR-005, CFR-006 |
| **Context Management** | CFR-007 |
| **Specification** | CFR-008, CFR-010, CFR-016 |
| **Notifications** | CFR-009 |
| **Source Control** | CFR-013 |
| **Observability** | CFR-014 |
| **Continuous Work** | CFR-015 |

---

## Related Documentation

- **Full Details**: `data/cfr_extraction.json` - Complete CFR implementation details
- **Agent Boundaries**: `docs/AGENT_OWNERSHIP.md` - Detailed responsibility matrix
- **Singleton Architecture**: `docs/AGENT_SINGLETON_ARCHITECTURE.md` - CFR-000 implementation
- **File Ownership Status**: `docs/FILE_OWNERSHIP_ENFORCEMENT_STATUS.md` - Enforcement implementation
- **Git Workflow**: `docs/architecture/guidelines/GUIDELINE-004-git-tagging-workflow.md` - CFR-013 details
- **Database Schema**: `data/orchestrator.db`, `data/roadmap.db` - CFR-014 implementation

---

**Last Updated**: 2025-10-24
**Status**: Active (15 CFRs enforced, 1 deprecated)
**Owner**: project_manager

**Remember**: CFRs are INVARIANTS. Violations MUST be blocked, not tolerated. These rules protect system integrity.
