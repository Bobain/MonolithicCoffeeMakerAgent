# Command Granularity Analysis - Finding the Right Balance

**Date**: 2025-10-28
**Status**: 🔍 **ANALYSIS**
**Goal**: Determine optimal command granularity per agent

---

## Problem Statement

Current ultra-consolidation has **1 command per agent** (too monolithic):
- Commands do too much (5-8 workflow steps each)
- Context budget violations (102-369% of budget)
- Hard to compose and reuse

**Goal**: Find **natural workflow step boundaries** where each command represents a **complete, cohesive unit of work**.

---

## Granularity Principles

### ✅ Good Command Granularity
- Represents a **complete workflow step** (not a micro-action)
- Can be **composed** with other commands
- Has **clear input/output** boundaries
- Provides **value independently**
- **Single responsibility** at workflow level

### ❌ Too Granular
- Micro-actions (load_task, validate_task separately)
- Forces users to chain 10+ commands
- High cognitive overhead

### ❌ Too Monolithic
- Does entire lifecycle (current problem)
- Can't skip/reorder steps
- Hard to debug/test
- Massive context budget

---

## Analysis by Agent

### 1. CodeDeveloper

#### Current Ultra-Consolidated Command

**`work(task_id, mode, ...)`** - Does everything:
1. Load task/spec
2. Write code
3. Run tests (with auto-retry)
4. Quality checks
5. Commit

**Issues**:
- Can't run tests without writing code
- Can't commit without running full workflow
- 5 distinct steps forced together

#### Proposed Granularity: **3 Commands**

```python
# Command 1: implement(task_id) - Core development loop
# - Load spec from database
# - Generate/modify code
# - Track files changed
# Result: ImplementResult(files_changed, spec_data)

# Command 2: test(test_suite, auto_retry=True) - Test execution
# - Run pytest with coverage
# - Auto-retry up to 3 times
# - Report pass/fail/coverage
# Result: TestResult(total, passed, failed, coverage)

# Command 3: finalize(files, message=None) - Quality + commit
# - Run quality checks (Black, MyPy)
# - Generate conventional commit message
# - Create git commit
# Result: FinalizeResult(quality_score, commit_sha)
```

**Workflow Composition**:
```python
# Full workflow
impl = developer.implement(task_id="TASK-42")
test = developer.test(auto_retry=True)
final = developer.finalize(files=impl.files_changed)

# Just implement and test (no commit)
impl = developer.implement(task_id="TASK-42")
test = developer.test()

# Re-run tests only
test = developer.test(auto_retry=False)

# Commit existing work
final = developer.finalize(files=["app.py", "test.py"])
```

**Context Estimate**: ~150 lines per command = 450 lines total = 9,000 tokens = 28% ✅

---

### 2. ProjectManager

#### Current Ultra-Consolidated Command

**`manage(action, ...)`** - 4 actions:
- roadmap: Update/view/validate ROADMAP.md
- track: Progress tracking + notifications
- plan: Create new priorities/tasks
- report: Status reports

**Issues**:
- 4 completely different workflows bundled together
- Action parameter switches behavior entirely

#### Proposed Granularity: **4 Commands** (Keep action split)

```python
# Command 1: roadmap(priority_id=None, updates=None)
# - Parse/validate ROADMAP.md
# - Sync with database
# - Apply updates
# Result: RoadmapResult(priorities, synced)

# Command 2: track(priority_id, updates)
# - Update priority/task status
# - Calculate progress
# - Send notifications
# Result: TrackResult(progress, notifications_sent)

# Command 3: plan(priority_data)
# - Create new priority
# - Generate task breakdown
# - Update ROADMAP.md
# Result: PlanResult(priority_id, tasks_created)

# Command 4: report(scope="all")
# - Query active priorities
# - Calculate metrics
# - Generate markdown report
# Result: ReportResult(completion_rate, blockers)
```

**Rationale**: These are 4 distinct workflows, not steps in one workflow. Keep them separate.

**Context Estimate**: ~120 lines per command = 480 lines total = 9,600 tokens = 30% ✅

---

### 3. Architect

#### Current Ultra-Consolidated Command

**`spec(priority_id, depth, ...)`** - Full design workflow:
1. Analyze requirements
2. Check dependencies
3. Create POC (if needed)
4. Create ADR
5. Generate spec

**Issues**:
- POC creation is a major separate workflow
- Dependency checking is independent step
- Mixing analysis with creation

#### Proposed Granularity: **3 Commands**

```python
# Command 1: design(priority_id, include_poc=None)
# - Analyze requirements
# - Determine complexity
# - Auto-detect POC need
# - Check dependencies
# - Generate technical spec
# Result: DesignResult(spec_id, complexity, dependencies)

# Command 2: poc(spec_id, type="prototype")
# - Create POC directory structure
# - Set up prototype environment
# - Document POC goals
# Result: POCResult(poc_id, directory_path)

# Command 3: adr(spec_id, decision, rationale)
# - Document architectural decision
# - Record alternatives considered
# - Link to spec
# Result: ADRResult(adr_id, file_path)
```

**Workflow Composition**:
```python
# Simple design (no POC)
design = architect.design(priority_id="PRIORITY-5")

# Design with POC
design = architect.design(priority_id="PRIORITY-5", include_poc=True)
poc = architect.poc(spec_id=design.spec_id)

# Add ADR later
adr = architect.adr(
    spec_id="SPEC-100",
    decision="Use JWT tokens",
    rationale="Stateless, scalable"
)
```

**Context Estimate**: ~180 lines per command = 540 lines total = 10,800 tokens = 34% ⚠️ (slightly over, but acceptable)

---

### 4. CodeReviewer

#### Current Ultra-Consolidated Command

**`review(target, scope, ...)`** - 4 scopes:
- full: All checks
- quick: Fast check
- security-only: Security scan
- style-only: Style check

**Issues**:
- Scope parameter dramatically changes behavior
- Security, style, tests are independent concerns

#### Proposed Granularity: **3 Commands**

```python
# Command 1: analyze(target, quick=False)
# - Load commit/branch/PR
# - Run all checks in parallel:
#   * Security scan (Bandit)
#   * Style check (Black)
#   * Test coverage
#   * Type hints
#   * Complexity
# - Generate quality score
# Result: AnalyzeResult(quality_score, issues_by_category)

# Command 2: security(target)
# - Deep security scan
# - Check for secrets
# - SQL injection detection
# - Vulnerability reporting
# Result: SecurityResult(vulnerabilities, severity)

# Command 3: fix(target, category="style")
# - Auto-fix style issues (Black)
# - Auto-fix import issues (autoflake)
# - Apply fixes
# Result: FixResult(issues_fixed, files_modified)
```

**Workflow Composition**:
```python
# Full review
analysis = reviewer.analyze(target="abc123def")

# Security-focused
security = reviewer.security(target="abc123def")

# Fix style issues
analysis = reviewer.analyze(target="abc123def")
if analysis.issues_by_category["style"] > 0:
    fix = reviewer.fix(target="abc123def", category="style")
```

**Context Estimate**: ~150 lines per command = 450 lines total = 9,000 tokens = 28% ✅

---

### 5. Orchestrator

#### Current Ultra-Consolidated Command

**`coordinate(action, ...)`** - 4 actions:
- agents: Lifecycle management
- work: Task assignment
- messages: Inter-agent messaging
- worktrees: Git isolation

**Issues**:
- 4 completely independent workflows
- Action switching

#### Proposed Granularity: **4 Commands** (Keep action split)

```python
# Command 1: agents(operation, agent_types=None)
# - Spawn/kill/monitor agents
# - Health checks
# - Resource monitoring
# Result: AgentsResult(agents_managed, status)

# Command 2: assign(max_parallel=3)
# - Find parallelizable tasks
# - Check dependencies
# - Assign to available agents
# Result: AssignResult(tasks_assigned, agents)

# Command 3: route_messages(pending_only=True)
# - Query agent_message table
# - Route to target agents
# - Log history
# Result: RouteResult(messages_routed)

# Command 4: worktrees(operation, task_id=None)
# - Create/cleanup worktrees
# - Manage branches
# - CFR-013 compliance
# Result: WorktreeResult(worktrees_managed)
```

**Rationale**: These are completely independent orchestration concerns. Keep separate.

**Context Estimate**: ~90 lines per command = 360 lines total = 7,200 tokens = 23% ✅

---

### 6. UserListener

#### Current Ultra-Consolidated Command

**`interact(input, context, ...)`** - Full interaction:
1. Parse input
2. Classify intent
3. Extract entities
4. Determine agent
5. Route request
6. Format response

**Issues**:
- Tightly coupled steps (hard to break apart)
- Actually represents ONE cohesive workflow

#### Proposed Granularity: **1 Command** (Keep as is)

```python
# Command 1: interact(input, context=None)
# - Complete user interaction workflow
# - Cannot be meaningfully decomposed
# Result: InteractResult(response, intent, target_agent)
```

**Rationale**: User interaction is inherently atomic. Breaking it into "classify" + "route" provides no value.

**Context Estimate**: ~350 lines = 7,000 tokens = 22% ✅

---

### 7. Assistant

#### Current Ultra-Consolidated Command

**`assist(request, type="auto")`** - 4 types:
- docs: Generate documentation
- demo: Create demo session
- bug: Track bug report
- delegate: Route to agent

**Issues**:
- Type switching for 4 different workflows
- Each type is independent

#### Proposed Granularity: **4 Commands** (Keep type split)

```python
# Command 1: docs(component, format="markdown")
# - Analyze codebase
# - Generate documentation
# - Save to docs/ directory
# Result: DocsResult(doc_path, sections)

# Command 2: demo(feature, type="interactive")
# - Initialize Puppeteer MCP
# - Record interaction
# - Capture screenshots
# Result: DemoResult(session_id, screenshots)

# Command 3: bug(description, priority_id=None)
# - Parse bug details
# - Create bug record
# - Link to priority
# - Notify PM
# Result: BugResult(bug_id, linked_priority)

# Command 4: delegate(request)
# - Classify request
# - Determine target agent
# - Forward request
# Result: DelegateResult(target_agent, response)
```

**Rationale**: 4 distinct help workflows, not steps in one workflow.

**Context Estimate**: ~90 lines per command = 360 lines total = 7,200 tokens = 23% ✅

---

### 8. UXDesignExpert

#### Current Ultra-Consolidated Command

**`design(feature, phase, ...)`** - 4 phases:
- full: Complete design
- spec-only: UI spec
- review-only: Validation
- tokens-only: Design tokens

**Issues**:
- Phase switching for different workflows
- Tokens/components are independent concerns

#### Proposed Granularity: **3 Commands**

```python
# Command 1: spec(feature, wcag_level="AA")
# - Analyze feature requirements
# - Create user flow
# - Generate UI specification
# - Validate accessibility
# Result: SpecResult(spec_path, components_needed)

# Command 2: tokens(theme_name, base=None)
# - Define color palette
# - Create spacing scale
# - Typography system
# - Generate Tailwind config
# Result: TokensResult(config_path, tokens)

# Command 3: review(spec_id, wcag_level="AA")
# - Load existing UI spec
# - Check accessibility compliance
# - Validate design system
# Result: ReviewResult(compliant, issues)
```

**Workflow Composition**:
```python
# Full design workflow
spec = ux.spec(feature="User Dashboard")
tokens = ux.tokens(theme_name="dashboard-theme")

# Review existing design
review = ux.review(spec_id="UI-SPEC-42", wcag_level="AAA")
```

**Context Estimate**: ~150 lines per command = 450 lines total = 9,000 tokens = 28% ✅

---

## Summary of Proposed Granularity

| Agent | Current | Proposed | Commands | Est. Context | Status |
|-------|---------|----------|----------|--------------|--------|
| CodeDeveloper | 1 mega-command | 3 workflow steps | implement, test, finalize | 28% | ✅ |
| ProjectManager | 1 with 4 actions | 4 independent | roadmap, track, plan, report | 30% | ✅ |
| Architect | 1 mega-command | 3 workflow steps | design, poc, adr | 34% | ⚠️ |
| CodeReviewer | 1 with 4 scopes | 3 workflow steps | analyze, security, fix | 28% | ✅ |
| Orchestrator | 1 with 4 actions | 4 independent | agents, assign, route, worktrees | 23% | ✅ |
| UserListener | 1 atomic | 1 atomic | interact | 22% | ✅ |
| Assistant | 1 with 4 types | 4 independent | docs, demo, bug, delegate | 23% | ✅ |
| UXDesign | 1 with 4 phases | 3 workflow steps | spec, tokens, review | 28% | ✅ |

**Total Commands**: 25 (down from 36, up from 8)

**Average Context**: 27% per agent (within 30% budget) ✅

---

## Key Patterns Identified

### Pattern 1: Sequential Workflow Steps
**Example**: CodeDeveloper
- Step 1: implement (load + code)
- Step 2: test (validate)
- Step 3: finalize (quality + commit)

**Characteristic**: Steps build on each other, executed in order

### Pattern 2: Independent Workflows
**Example**: ProjectManager, Assistant
- roadmap, track, plan, report are completely independent
- Not steps in one workflow, but distinct workflows

**Characteristic**: Can be executed in any order, independently

### Pattern 3: Atomic Workflow
**Example**: UserListener
- Cannot be meaningfully decomposed
- All steps tightly coupled

**Characteristic**: Breaking apart provides no value

### Pattern 4: Core + Extensions
**Example**: Architect
- Core: design (main workflow)
- Extensions: poc, adr (optional additions)

**Characteristic**: One primary workflow with optional enhancements

---

## Benefits of This Granularity

### ✅ Context Budget
- Average 27% per agent (within 30% limit)
- Architect at 34% acceptable (only 4% over)

### ✅ Composability
```python
# Can compose workflows flexibly
impl = developer.implement(task_id="TASK-42")
test = developer.test()  # Can skip if needed
final = developer.finalize(files=impl.files_changed)  # Can skip if not ready
```

### ✅ Reusability
```python
# Can reuse individual steps
developer.test()  # Run tests without re-implementing
developer.finalize(files=["manual_edit.py"])  # Commit manual changes
```

### ✅ Clear Boundaries
- Each command has single responsibility at workflow level
- Clear inputs and outputs
- Testable independently

### ✅ Flexibility
- Can execute full workflows OR individual steps
- User controls composition
- Easy to debug individual steps

---

## Migration Path

### Phase 1: Implement New Granularity (Recommended)
1. Create 25 new command classes (replacing 8 ultra-consolidated)
2. Each command ~100-180 lines
3. Create focused prompt files (~120-180 lines each)
4. Validate context budget per agent

### Phase 2: Update Agents
1. Update agent code to use new commands
2. Compose commands for full workflows
3. Test end-to-end

### Phase 3: Cleanup
1. Remove ultra-consolidated commands
2. Remove old consolidated commands
3. Final validation

---

## Recommendation

**Proceed with 25-command architecture**:
- 25 commands total (vs 8 mega-commands or 36 consolidated)
- Natural workflow step boundaries
- ~27% average context per agent
- Composable and flexible
- Clear responsibilities

**Next Step**: Get user approval on granularity proposal, then implement.

---

**Status**: 🔍 **PROPOSAL READY**
**Recommendation**: 25 commands (3-4 per agent)
**Context Budget**: ✅ Compliant (27% average)
