# Ultra-Consolidation Analysis - Workflow-Based Commands

**Date**: 2025-10-27
**Status**: PROPOSAL
**Goal**: Reduce 36 commands to ~10 workflow-based commands while staying under CFR-007 (30% context budget)

---

## 🚨 Problem Statement

### Current State
- **36 consolidated commands** across 8 agents
- **108 command prompt files**
- **26,517 lines** of prompts
- **Context Budget**: CFR-007 requires ≤30% of 200k context = 60k tokens ≈ 240k chars

### Issues
1. **Too Many Commands**: 36 is still too granular
2. **Context Overload**: 26k lines violates CFR-007
3. **Not Workflow-Based**: Commands are steps, not workflows
4. **Cognitive Load**: Agents need to remember too many command names

---

## 💡 Core Insight: Workflow-Based Design

**Current Approach**: Many small commands for individual steps
```python
# Example: code_developer has 6 commands
developer.implement(action="load", task_id="TASK-1")
developer.implement(action="write_code")
developer.test(action="run")
developer.git(action="commit")
developer.quality(action="pre_commit")
```

**Proposed Approach**: One command per workflow
```python
# One command handles entire workflow
developer.work(task_id="TASK-1")  # Does: load → implement → test → commit
```

---

## 🎯 Proposed Ultra-Consolidated Structure

### Target: ~10 Total Commands (70% Reduction)

#### Tier 1: Core Workflow Commands (5 commands)

| Agent | Command | What It Does | Replaces |
|-------|---------|--------------|----------|
| **code_developer** | `work(task_id)` | Full implementation workflow: spec→code→test→commit | 6 commands |
| **architect** | `spec(priority_id)` | Full design workflow: analyze→design→spec→adr | 5 commands |
| **project_manager** | `manage(action)` | Project operations: roadmap, tasks, tracking | 5 commands |
| **code_reviewer** | `review(target)` | Full review workflow: analyze→review→report→notify | 4 commands |
| **orchestrator** | `coordinate(action)` | Team coordination: agents, tasks, messages | 5 commands |

**Total: 5 commands** (replaces 25 commands)

#### Tier 2: Support Commands (3 commands)

| Agent | Command | What It Does | Replaces |
|-------|---------|--------------|----------|
| **user_listener** | `interact(input)` | Full UI workflow: understand→route→respond | 3 commands |
| **assistant** | `assist(request)` | Help workflow: classify→delegate→respond | 4 commands |
| **ux_design_expert** | `design(feature)` | Full design workflow: spec→components→review | 4 commands |

**Total: 3 commands** (replaces 11 commands)

### Grand Total: **8 Commands** (from 36)

---

## 📋 Detailed Command Specifications

### 1. code_developer.work(task_id, mode="auto")

**Purpose**: Complete implementation workflow from task to commit

**Workflow**:
```python
1. Load task/spec from database
2. Analyze requirements
3. Generate/modify code
4. Run tests automatically
5. Fix any test failures
6. Run quality checks (black, mypy, pre-commit)
7. Commit with conventional message
8. Update task status
```

**Parameters**:
- `task_id`: Task to implement (required)
- `mode`: "auto" (full workflow) | "step" (interactive) | "test-only" | "commit-only"
- `skip_tests`: Skip test execution (default: False)
- `auto_commit`: Auto-commit on success (default: True)

**Returns**: Implementation result with stats

**Replaces**: implement, test, refactor, docs, git, quality (6 → 1)

---

### 2. architect.spec(priority_id, depth="full")

**Purpose**: Complete architectural design workflow

**Workflow**:
```python
1. Load priority from roadmap
2. Analyze requirements and dependencies
3. Design solution architecture
4. Create technical specification
5. Document architectural decisions (ADR)
6. Review and validate POC if needed
7. Update dependency matrix
8. Notify relevant agents
```

**Parameters**:
- `priority_id`: Priority to design (required)
- `depth`: "full" | "quick" | "update" | "review"
- `poc_required`: Create POC first (default: auto-detect)
- `dependencies`: List of dependencies to check

**Returns**: Spec ID and status

**Replaces**: design, specs, dependency, adr, poc (5 → 1)

---

### 3. project_manager.manage(action, **params)

**Purpose**: Project management operations

**Actions**:
- `roadmap`: Update/view/validate roadmap
- `track`: Track progress and send notifications
- `plan`: Create new priorities and tasks
- `report`: Generate status reports

**Workflow** (depends on action):
```python
# roadmap: Update entire roadmap workflow
1. Load current roadmap
2. Apply updates
3. Validate consistency
4. Notify affected agents
5. Update git

# track: Progress tracking workflow
1. Query task statuses
2. Identify blockers
3. Send notifications
4. Update roadmap status
```

**Parameters**: Action-specific

**Returns**: Action result

**Replaces**: roadmap, tasks, specs, notifications, git (5 → 1)

---

### 4. code_reviewer.review(target, scope="full")

**Purpose**: Complete code review workflow

**Workflow**:
```python
1. Detect what to review (commit/PR/file)
2. Run all analysis:
   - Style compliance (black, pylint)
   - Security scan (bandit)
   - Complexity analysis
   - Test coverage check
   - Type hint validation
   - Architecture compliance
3. Generate comprehensive report
4. Calculate quality score
5. Notify architect if issues found
6. Track issues for resolution
```

**Parameters**:
- `target`: What to review (commit SHA, PR number, file path)
- `scope`: "full" | "quick" | "security-only" | "style-only"
- `auto_fix`: Attempt auto-fixes (default: False)

**Returns**: Review report with quality score

**Replaces**: review, analyze, monitor, notify (4 → 1)

---

### 5. orchestrator.coordinate(action, **params)

**Purpose**: Multi-agent coordination

**Actions**:
- `agents`: Manage agent lifecycle (spawn, kill, monitor)
- `work`: Find and assign work to agents
- `messages`: Route inter-agent messages
- `worktrees`: Manage git worktrees for parallel work

**Workflow** (example: `coordinate("work")`):
```python
1. Query available work from specs
2. Check agent availability
3. Detect parallelizable tasks
4. Create worktrees if needed
5. Spawn agents with assignments
6. Monitor progress
7. Merge completed work
```

**Parameters**: Action-specific

**Returns**: Coordination result

**Replaces**: agents, orchestrate, worktree, messages, monitor (5 → 1)

---

### 6. user_listener.interact(input, context=None)

**Purpose**: Full user interaction workflow

**Workflow**:
```python
1. Understand user input (classify intent, extract entities)
2. Determine target agent
3. Route request through orchestrator
4. Wait for response
5. Present result to user
6. Update conversation context
```

**Parameters**:
- `input`: User's input text (required)
- `context`: Conversation context (optional)
- `suggested_agent`: Hint for routing (optional)

**Returns**: Response to display to user

**Replaces**: understand, route, conversation (3 → 1)

---

### 7. assistant.assist(request, type="auto")

**Purpose**: Assistance and delegation workflow

**Workflow**:
```python
1. Classify request type (docs, demo, bug, delegation)
2. Route to appropriate handler:
   - Docs: Generate documentation
   - Demo: Create/record demo
   - Bug: Track and report bug
   - Delegation: Route to specialist agent
3. Execute requested action
4. Return formatted result
```

**Parameters**:
- `request`: Assistance request (required)
- `type`: "auto" | "docs" | "demo" | "bug" | "delegate"

**Returns**: Assistance result

**Replaces**: delegate, docs, demo, bug (4 → 1)

---

### 8. ux_design_expert.design(feature, phase="full")

**Purpose**: Complete UX design workflow

**Workflow**:
```python
1. Generate UI specification
2. Create component specifications
3. Design/configure design system:
   - Tailwind config
   - Design tokens
   - Component library
4. Review implementation if exists
5. Validate accessibility (WCAG)
6. Track design debt
7. Create remediation plans
```

**Parameters**:
- `feature`: Feature to design (required)
- `phase`: "full" | "spec-only" | "review-only" | "tokens-only"
- `wcag_level`: "A" | "AA" | "AAA" (default: "AA")

**Returns**: Design artifacts and status

**Replaces**: design, components, review, debt (4 → 1)

---

## 📊 Comparison: Before vs After

### Command Count
```
Before: 36 commands
After:  8 commands
Reduction: 78%
```

### Complexity Per Agent
| Agent | Before | After | Reduction |
|-------|--------|-------|-----------|
| code_developer | 6 | 1 | 83% |
| architect | 5 | 1 | 80% |
| project_manager | 5 | 1 | 80% |
| code_reviewer | 4 | 1 | 75% |
| orchestrator | 5 | 1 | 80% |
| user_listener | 3 | 1 | 67% |
| assistant | 4 | 1 | 75% |
| ux_design_expert | 4 | 1 | 75% |

### Prompt Files (Estimated)
```
Before: 108 files, 26,517 lines
After:  8-16 files, ~3,000-5,000 lines
Reduction: ~85%
```

### Context Budget Impact
```
Before: 26,517 lines ≈ 53k tokens (26% of 200k)
After:  ~4,000 lines ≈ 8k tokens (4% of 200k)
Improvement: 5x reduction, well under CFR-007 limit
```

---

## 💪 Benefits of Ultra-Consolidation

### 1. Cognitive Simplicity
- **1 command per agent** (primary workflow)
- Easy to remember
- Clear mental model
- Less context switching

### 2. Workflow Alignment
- Commands match actual work patterns
- End-to-end workflows, not steps
- Atomic operations
- Better error recovery

### 3. CFR-007 Compliance
- 4% of context vs 26%
- Plenty of room for task-specific context
- Fast to load and parse
- Scalable for future growth

### 4. Maintainability
- Fewer files to update
- Less duplication
- Clearer ownership
- Easier testing

### 5. Developer Experience
- Simpler API
- One command to rule them all
- Progressive disclosure (mode/action params)
- Consistent patterns

---

## 🎨 Design Principles

### 1. Workflow-First
Each command represents a complete workflow, not a step

### 2. Smart Defaults
Commands work with minimal parameters, but allow fine control

### 3. Progressive Disclosure
- Simple case: `work(task_id)` - just works
- Advanced: `work(task_id, mode="step", skip_tests=True)`

### 4. Single Responsibility
Each command owns ONE workflow, does it completely

### 5. Composable
Commands can call each other for complex scenarios

---

## 🔄 Migration Strategy

### Phase 1: Add Ultra-Consolidated Commands (Parallel)
- Keep existing 36 commands
- Add 8 new workflow commands
- Both work simultaneously
- No breaking changes

### Phase 2: Update Agent Implementations
- code_developer uses `work()` instead of 6 commands
- architect uses `spec()` instead of 5 commands
- Validate autonomous operation

### Phase 3: Deprecate Granular Commands
- Mark old commands as deprecated
- Update documentation
- Provide migration guide

### Phase 4: Remove Legacy (Optional)
- After validation period
- Clean removal
- Celebrate simplicity! 🎉

---

## 📝 Implementation Checklist

### High Priority
- [ ] Create `work()` command for code_developer
- [ ] Create `spec()` command for architect
- [ ] Create `manage()` command for project_manager
- [ ] Create `review()` command for code_reviewer

### Medium Priority
- [ ] Create `coordinate()` command for orchestrator
- [ ] Create `interact()` command for user_listener

### Low Priority
- [ ] Create `assist()` command for assistant
- [ ] Create `design()` command for ux_design_expert

### Documentation
- [ ] Update CFR-007 compliance docs
- [ ] Create workflow command guide
- [ ] Update API reference
- [ ] Create migration examples

---

## 🤔 Open Questions

1. **Granular Control**: Do we need escape hatches for sub-steps?
   - **Answer**: Yes, use `mode` parameter (e.g., `mode="test-only"`)

2. **Error Handling**: What happens if mid-workflow step fails?
   - **Answer**: Return partial results + error info, allow retry from that step

3. **Observability**: How to see what's happening inside workflow?
   - **Answer**: Detailed logging + progress callbacks + `--verbose` mode

4. **Testing**: How to test complex workflows?
   - **Answer**: Mock intermediate steps, test full flow + unit test helpers

5. **Backward Compatibility**: Keep old commands forever?
   - **Answer**: Deprecation path, eventually remove after validation

---

## 🎯 Success Criteria

### Quantitative
- ✅ Reduce to ≤10 commands (target: 8)
- ✅ Context budget <10% (target: 4%)
- ✅ <5k lines of prompts (target: 4k)
- ✅ 100% test coverage maintained

### Qualitative
- ✅ Agent workflows feel natural
- ✅ Less cognitive load on users
- ✅ Easier to document and teach
- ✅ Better error recovery
- ✅ Faster agent execution

---

## 🚀 Recommendation

**Proceed with ultra-consolidation**:
1. Implement 8 workflow-based commands
2. Maintain backward compatibility
3. Migrate agents progressively
4. Validate with autonomous operation
5. Remove legacy commands after validation

**Result**: Simpler, more powerful, CFR-007 compliant command architecture.

---

**Status**: PROPOSAL - Awaiting approval to implement
**Impact**: 78% reduction in commands, 85% reduction in prompts, 5x better CFR-007 compliance
**Risk**: Low (backward compatible migration)
**Effort**: ~2-3 days implementation

---

**Next Step**: Get approval, then start with code_developer.work() as proof of concept
