# ADR-010: Architect Commit Review and Skills Maintenance

**Status**: Accepted (Updated by ADR-011)

**Date**: 2025-10-18

**Author**: architect agent

**Updated**: 2025-10-18 (ADR-011: Orchestrator messaging replaces git hooks)

**Related Issues**: ADR-009 (Skills System), ADR-011 (Orchestrator Messaging), US-055/056/057 (Claude Skills Integration)

**Related Specs**: SPEC-001-advanced-code-search-skills.md

---

## Context

Following ADR-009's decision to retire the assistant agent (with code analysis skills) and replace it with a Skills system, we need to define **WHO maintains the skills** and **HOW the Code Index stays accurate**.

### Current State (Post ADR-009)

**Architecture Decided**:
```
user_listener (UI)
    ├── architect (design) ──────────┐
    ├── code_developer (implementation)  │
    ├── project_manager (planning)       │  All use skills
    ├── assistant (docs + dispatcher)    │
    └── ux-design-expert (UI/UX)     │
                                     │
                                     ↓
                           ┌─────────────────────┐
                           │   SKILLS SYSTEM     │
                           │                     │
                           │ - Code Index        │
                           │ - Functional Search │
                           │ - Code Explanation  │
                           │ - Security Audit    │
                           │ - Dependency Tracer │
                           └─────────────────────┘
                                     ↑
                           ┌─────────────────────┐
                           │  Auto-Update        │
                           │  (git hooks, cron)  │  ← Who maintains this?
                           └─────────────────────┘
```

**Open Questions from ADR-009**:
1. Who maintains the skills when code changes?
2. How do we ensure Code Index accuracy?
3. Who provides feedback on code quality?
4. How do skills improve over time?

**User's New Vision (2025-10-18)**:
> "L'architect doit relire tous les commits du code_developer, il en déduit des mises à jour des skills mais aussi un feedback à donner au code_developer : ceci peut aller à la fois au reflector du code_developer, au code_developer directement, ou encore au project_manager (si certaines parties du code doivent être ré-écrites). À chacune de ces opérations, l'architect peut donc procéder à la mise à jour des skills."

**Key Insight**: "La revue de code est importante et est la meilleure occasion de mettre à jour les index du code."

This vision adds a **new primary responsibility to architect**: systematic commit review as the **optimal trigger** for skills updates.

### The Problem

**Without systematic commit review**:
- Skills become stale as code evolves
- Code Index misses new patterns
- No quality feedback loop
- Technical debt accumulates unnoticed
- Architecture drift (code diverges from specs)

**Current architect limitations**:
- Only creates specs BEFORE implementation
- No visibility into WHAT was actually implemented
- Cannot verify specs were followed
- Cannot extract learnings from implementation

### Forces at Play

**Architectural Supervision**:
- code_developer implements autonomously (good)
- But implementations may deviate from specs (risk)
- Need feedback loop to align reality with design
- Skills should reflect ACTUAL codebase, not ideal design

**Skills Maintenance**:
- Skills are infrastructure (need ownership)
- Code Index must stay current (automatic + manual)
- New patterns emerge during implementation (need capture)
- Skills improve through usage feedback

**Feedback Routing**:
- Some feedback is **tactical** (code_developer: fix this function)
- Some feedback is **reflective** (reflector: pattern to remember)
- Some feedback is **strategic** (project_manager: rewrite needed)
- Need clear routing logic

**Agent Autonomy**:
- architect should not block code_developer
- Reviews happen POST-commit (non-blocking)
- Feedback is advisory, not mandatory (unless critical)
- Continuous improvement mindset

---

## Decision

We will **add a new primary responsibility to architect**: **systematic commit review and skills maintenance**.

**Agent Name**: Remains `architect` (no renaming)

**Rationale**: Code review is the **best opportunity** to update the Code Index because:
1. architect sees exactly what code changed (git diff)
2. architect understands architectural context (wrote the specs)
3. architect can validate spec compliance (design vs reality)
4. Skills updates are most accurate when based on actual commits

### 1. New Architect Responsibilities

**Core Responsibilities**:

| Responsibility | Before | After |
|----------------|-------------------|----------------------|
| **Architectural Design** | ✅ Create specs BEFORE implementation | ✅ Same (no change) |
| **Commit Review** | ❌ None | ✅ **NEW: Review ALL code_developer commits** |
| **Skills Maintenance** | ❌ None | ✅ **NEW: Update skills based on commits** |
| **Quality Feedback** | ❌ None | ✅ **NEW: Provide feedback to code_developer** |
| **Architecture Verification** | ❌ None | ✅ **NEW: Verify specs were followed** |
| **Pattern Extraction** | ❌ None | ✅ **NEW: Extract patterns for skills** |

**Why Keep "architect" Name**:
- Role remains fundamentally **architectural** (design + quality oversight)
- Commit review is natural extension of architectural responsibility
- No need for new agent name (adds complexity)
- Skills maintenance is infrastructure work (fits architect's domain)

### 2. Commit Review Workflow

**Trigger**: Every commit by code_developer to `roadmap` branch

⭐ **UPDATE (ADR-011)**: Uses **orchestrator messaging** instead of git hooks for better integration

**Process**:

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: code_developer commits code                         │
│  git commit -m "feat: Implement US-055 Phase 1"             │
│  git push origin roadmap                                     │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: code_developer sends message to architect           │
│  Via: Orchestrator file-based messaging (ADR-011)           │
│  File: data/agent_messages/architect_inbox/commit_<SHA>.json│
│  Priority: CRITICAL or NORMAL (auto-determined)             │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: architect analyzes commit                           │
│  - Read commit diff (git show <SHA>)                        │
│  - Identify changed files, functions, classes               │
│  - Compare against technical spec (if exists)               │
│  - Assess code quality, patterns, architecture              │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: architect updates skills                            │
│  - Update Code Index (new functions, classes)               │
│  - Add new patterns to pattern library                      │
│  - Update complexity metrics                                │
│  - Refresh dependency graph                                 │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: architect generates feedback                        │
│  Decision: Where to route feedback?                         │
│  ├─ Tactical feedback → code_developer directly             │
│  ├─ Learning feedback → reflector (code_developer)          │
│  └─ Strategic feedback → project_manager                    │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 6: Feedback delivery                                   │
│  - Write feedback file (data/architect_feedback/<SHA>.md)   │
│  - Notify recipient (Slack, email, or file flag)            │
│  - Track feedback status (acknowledged, addressed, ignored)  │
└──────────────────────────────────────────────────────────────┘
```

**Execution Mode**:
- **Asynchronous**: Does NOT block code_developer
- **Background task**: Runs in separate process
- **Low priority**: Does not consume critical resources
- **Gradual**: Can take hours to complete review (not urgent)

### 3. Skills Update Mechanism

**What Gets Updated**:

1. **Code Index** (primary)
   - Add new functions, classes, methods
   - Update line ranges for modified code
   - Refresh complexity metrics
   - Update "last_modified" timestamps

2. **Pattern Library** (secondary)
   - Extract new architectural patterns discovered
   - Document anti-patterns to avoid
   - Update best practices based on what works

3. **Dependency Graph** (tertiary)
   - Track new dependencies introduced
   - Identify circular dependencies
   - Flag breaking changes in APIs

**Update Granularity**:

| Change Type | Update Strategy | Example |
|-------------|----------------|---------|
| **Minor edit** (1-10 lines) | Incremental update | Fix typo in docstring → Update description only |
| **Function refactor** (10-50 lines) | Partial rebuild | Refactor login() → Re-analyze auth component |
| **New module** (50+ lines) | Full rebuild | New payment gateway → Rebuild payment category |
| **Architectural change** | Full rebuild + review | Switch to async → Rebuild entire index + spec review |

**Update Performance**:
- **Incremental**: 2-5 seconds (90% of commits)
- **Partial rebuild**: 10-20 seconds (9% of commits)
- **Full rebuild**: 30-60 seconds (1% of commits)

### 4. Feedback Routing Logic

**Three Feedback Channels**:

#### 4.1 → code_developer (Tactical Feedback)

**When**:
- Bug detected in implementation
- Code does not follow spec
- Performance issue identified
- Security vulnerability found

**Example**:
```markdown
## Tactical Feedback: US-055 Implementation

**Commit**: a1b2c3d - "feat: Implement Code Index builder"

**Issues Found**:
1. **Bug** (line 45): `index.get_category()` returns None when category missing
   - Expected: Raise KeyError
   - Impact: Silent failures in search queries
   - Fix: Add explicit None check or raise exception

2. **Performance** (line 120): Parsing all files sequentially
   - Current: 60 seconds for 450 files
   - Expected: <30 seconds (per spec)
   - Suggestion: Use ProcessPoolExecutor for parallel parsing

**Action Required**: Fix before next commit
**Priority**: HIGH
```

**Delivery**: Direct message to code_developer (file or Slack)

#### 4.2 → reflector (Learning Feedback)

**When**:
- New pattern discovered worth remembering
- Effective solution to complex problem
- Anti-pattern to avoid in future
- Best practice emerged

**Example**:
```markdown
## Learning Feedback: Effective Pattern for Async File I/O

**Commit**: a1b2c3d - "feat: Async index update"

**Pattern Discovered**:
- **What**: Atomic file writes with temp file + rename
- **Where**: coffee_maker/code_index/updater.py:150-180
- **Why Effective**:
  - Prevents partial writes during crash
  - No file corruption even if process killed
  - Fast (atomic rename is O(1) operation)
- **Reuse Opportunity**: Apply to all config file writes

**Recommendation**: Add to pattern library as "Atomic File Update Pattern"

**Reflector Action**: Store in code_developer's memory for future tasks
```

**Delivery**: Write to reflector's delta items storage

#### 4.3 → project_manager (Strategic Feedback)

**When**:
- Major architectural issue requiring rewrite
- Implementation diverges significantly from spec
- Technical debt reached critical level
- New priority needed to address systemic issue

**Example**:
```markdown
## Strategic Feedback: Payment Module Needs Refactoring

**Commit**: a1b2c3d - "feat: Add PayPal integration"

**Critical Issue**:
- Payment gateway code duplicated across 3 modules (Stripe, PayPal, Square)
- 80% code duplication detected (450 LOC duplicated)
- Each module has slightly different error handling (inconsistent)
- High risk: Bug fixes must be applied 3 times manually

**Recommendation**: Create PRIORITY X - Refactor Payment Gateways
- Extract common logic to AbstractPaymentGateway
- Implement gateway-specific code in subclasses
- Estimated effort: 8-12 hours
- Benefit: Reduce 450 LOC to ~150 LOC, consistent behavior

**Impact**: Current implementation works but creates technical debt
**Urgency**: MEDIUM (not blocking, but should address within 2 weeks)

**Action Required**: project_manager to add new priority to ROADMAP
```

**Delivery**: Notification to project_manager + create issue in ROADMAP

### 5. Feedback Routing Decision Tree

```python
def route_feedback(commit_analysis: CommitAnalysis) -> FeedbackRoute:
    """Decide where to send feedback based on analysis."""

    # Critical bugs/security → code_developer (URGENT)
    if commit_analysis.has_critical_issues():
        return FeedbackRoute.CODE_DEVELOPER

    # Spec deviation → code_developer (HIGH priority)
    if commit_analysis.deviates_from_spec():
        return FeedbackRoute.CODE_DEVELOPER

    # Major refactor needed → project_manager (strategic)
    if commit_analysis.requires_rewrite():
        return FeedbackRoute.PROJECT_MANAGER

    # High technical debt → project_manager (prioritization)
    if commit_analysis.technical_debt_score > 80:
        return FeedbackRoute.PROJECT_MANAGER

    # New pattern discovered → reflector (learning)
    if commit_analysis.has_new_patterns():
        return FeedbackRoute.REFLECTOR

    # Effective solution → reflector (best practice)
    if commit_analysis.quality_score > 90:
        return FeedbackRoute.REFLECTOR

    # Minor improvements → code_developer (low priority)
    if commit_analysis.has_minor_issues():
        return FeedbackRoute.CODE_DEVELOPER

    # No issues → just update skills (no feedback)
    return FeedbackRoute.SKILLS_ONLY
```

**Feedback Priority Levels**:

| Priority | Description | Response Time | Delivery |
|----------|-------------|---------------|----------|
| **CRITICAL** | Security, critical bugs | Immediate (blocks next commit) | Slack alert + file |
| **HIGH** | Spec deviation, performance | Within 1 day | File + notification |
| **MEDIUM** | Refactor needed, tech debt | Within 1 week | File only |
| **LOW** | Suggestions, best practices | Optional | Reflector delta items |

### 6. Code-Architect Workflow Integration

**Daily Workflow**:

```
Morning (9:00 AM):
1. Check pending commit reviews (overnight commits)
2. Prioritize reviews (critical first)
3. Review 5-10 commits (1-2 hours)
4. Update skills based on findings
5. Generate and route feedback

Afternoon (2:00 PM):
6. Create architectural specs for new priorities
7. Review project_manager's strategic priorities
8. Respond to code_developer questions
9. Refine skills based on usage feedback

Evening (5:00 PM):
10. Final commit review batch
11. Update skill metrics (accuracy, coverage)
12. Prepare reports for project_manager
```

**Weekly Activities**:
- **Monday**: Review last week's commits (summary)
- **Wednesday**: Skills health check (accuracy audit)
- **Friday**: Generate weekly report (patterns, issues, metrics)

**Monthly Activities**:
- **Full Code Index rebuild** (ensure accuracy)
- **Pattern library curation** (archive obsolete patterns)
- **Skills effectiveness review** (are they being used?)

---

## Consequences

### Positive Consequences

**1. Continuous Architecture Alignment**
- architect verifies implementations match specs
- Architecture drift detected early
- Specs stay relevant (updated based on reality)

**2. Skills Stay Current**
- Code Index reflects actual codebase (not outdated)
- New patterns captured automatically
- Skills improve with every commit

**3. Quality Feedback Loop**
- code_developer gets actionable feedback
- Learning is captured (reflector)
- Strategic issues escalated (project_manager)

**4. Reduced Technical Debt**
- Issues caught during review, not months later
- Refactoring opportunities identified proactively
- Code quality metrics tracked over time

**5. Better Collaboration**
- code_developer gets expert review (like pair programming)
- project_manager sees architectural health
- reflector learns from real implementations

**6. Knowledge Capture**
- Effective patterns documented
- Anti-patterns identified
- Best practices emerge organically

### Negative Consequences

**1. Additional Workload for architect**
- Must review every commit (time-consuming)
- Mitigated by: Asynchronous reviews, batch processing
- Mitigated by: Automated analysis tools (pre-filter commits)

**2. Potential Bottleneck**
- If reviews pile up, architect becomes overwhelmed
- Mitigated by: Priority-based review queue
- Mitigated by: Automated tools handle 80% of routine checks

**3. Feedback Overload for code_developer**
- Too much feedback can be demotivating
- Mitigated by: Clear priority levels (only CRITICAL is urgent)
- Mitigated by: Positive feedback mixed with critical feedback

**4. Skill Update Lag**
- Skills updated POST-commit (slight delay)
- Mitigated by: Incremental updates (2-5 seconds)
- Mitigated by: Git hooks trigger immediately

**5. Complexity in Feedback Routing**
- Decision tree may route incorrectly
- Mitigated by: Feedback tracking (measure routing accuracy)
- Mitigated by: Manual override (architect can re-route)

### Neutral Consequences

**1. Agent Count Unchanged**
- Still 5 agents (no renaming, architect keeps its name)
- Role expanded, but no new agents added

**2. File Structure Changes**
- New directory: `data/architect_feedback/`
- New files: `<commit_sha>.md` for each review

**3. Orchestrator Messaging Added** ⭐ UPDATE (ADR-011)
- code_developer sends messages to architect after commits
- architect polls inbox and processes review requests
- No git hooks needed (all communication via orchestrator)

---

## Implementation

### Phase 1: Infrastructure (Week 1)

**Deliverables**:
1. **Update architect agent documentation**:
   - Update `.claude/agents/architect.md` (add commit review responsibility)
   - Update CLAUDE.md (add new architect capabilities)
   - No renaming needed (keeps "architect" name)

2. **Commit Review Framework**:
   - `coffee_maker/code_architect/commit_reviewer.py`
   - Analyze commit diffs, identify changes
   - Compare against technical specs
   - Generate feedback reports

3. **Feedback Router**:
   - `coffee_maker/code_architect/feedback_router.py`
   - Implement decision tree logic
   - Support three routes (code_developer, reflector, project_manager)
   - Track feedback delivery and status

4. **Orchestrator Messaging Integration** ⭐ UPDATE (ADR-011):
   - code_developer sends commit_review_request messages
   - architect polls inbox for review requests
   - No git hooks needed (simpler implementation)

**Estimated Effort**: 12 hours (3 hours saved vs git hooks)

### Phase 2: Skills Maintenance (Week 2)

**Deliverables**:
1. **Skills Updater**:
   - `coffee_maker/code_architect/skills_updater.py`
   - Update Code Index based on commits
   - Extract new patterns to pattern library
   - Refresh dependency graph

2. **Automated Analysis Tools**:
   - Code complexity analyzer (cyclomatic complexity)
   - Pattern detector (identify common patterns)
   - Spec compliance checker (compare code vs spec)

3. **Feedback Templates**:
   - Tactical feedback template (for code_developer)
   - Learning feedback template (for reflector)
   - Strategic feedback template (for project_manager)

**Estimated Effort**: 12 hours

### Phase 3: Workflow Integration (Week 3)

**Deliverables**:
1. **architect Dashboard**:
   - Show pending commit reviews
   - Display feedback sent/received
   - Skills health metrics (accuracy, coverage)

2. **Notification System**:
   - Slack integration (optional)
   - File-based notifications (mandatory)
   - Email alerts for CRITICAL issues

3. **Feedback Tracking**:
   - Track feedback status (acknowledged, addressed, ignored)
   - Generate weekly reports
   - Measure routing accuracy

**Estimated Effort**: 8 hours

### Phase 4: Testing & Documentation (Week 4)

**Deliverables**:
1. **Integration Tests**:
   - Test commit review workflow end-to-end
   - Test feedback routing logic
   - Test skills update accuracy

2. **Documentation**:
   - architect agent guide
   - Commit review process documentation
   - Feedback routing decision tree diagram

3. **Metrics & Monitoring**:
   - Review queue length
   - Feedback delivery time
   - Skills update latency
   - Routing accuracy

**Estimated Effort**: 5 hours

**Total Implementation Effort**: 40 hours (5 full days or 2 weeks part-time)

---

## Migration Path

### Step 1: Gradual Rollout (Week 1-2)

**Actions**:
1. Update architect documentation (add commit review role)
2. Implement commit review infrastructure
3. Run reviews in "dry-run" mode (generate feedback, don't send)
4. Collect feedback quality metrics

**Validation**:
- Are reviews accurate?
- Is feedback actionable?
- Is routing correct?

### Step 2: Pilot with code_developer (Week 3)

**Actions**:
1. Enable feedback delivery to code_developer only
2. code_developer provides feedback on feedback quality
3. Refine routing logic based on feedback

**Validation**:
- Does code_developer find feedback useful?
- Is feedback timely?
- Are critical issues caught early?

### Step 3: Full Rollout (Week 4)

**Actions**:
1. Enable all three feedback routes
2. Integrate with reflector and project_manager
3. Monitor feedback flow and adjust

**Validation**:
- Is reflector capturing learnings?
- Is project_manager creating priorities from strategic feedback?
- Are skills staying current?

### Step 4: Optimization (Ongoing)

**Actions**:
1. Tune decision tree based on usage data
2. Improve automated analysis tools
3. Reduce false positives in feedback

**Metrics to Track**:
- Feedback acceptance rate (% of feedback acted upon)
- Routing accuracy (% correctly routed)
- Skills freshness (average lag time)

---

## Success Metrics

### Quantitative Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Skills Freshness** | N/A (no updates) | <5 minutes after commit | Time between commit and skills update |
| **Review Latency** | N/A (no reviews) | <2 hours for routine, <30 min for critical | Time from commit to feedback delivery |
| **Feedback Acceptance** | N/A | >70% (feedback acted upon) | % of feedback that results in code changes |
| **Routing Accuracy** | N/A | >90% (correctly routed) | % of feedback sent to correct recipient |
| **Critical Issues Caught** | 0 (no reviews) | >80% before production | % of critical issues found in review |
| **Pattern Library Growth** | 0 patterns | 50+ patterns in 6 months | Number of patterns documented |

### Qualitative Metrics

**code_developer Experience**:
- ✅ Feedback is timely and actionable
- ✅ Critical issues caught before merge to main
- ✅ Learning from effective patterns
- ✅ Not overwhelmed by feedback volume

**architect Effectiveness**:
- ✅ Reviews completed within SLA (2 hours routine, 30 min critical)
- ✅ Skills stay accurate and useful
- ✅ Architecture alignment maintained
- ✅ Technical debt trends downward

**project_manager Visibility**:
- ✅ Receives strategic feedback on refactoring needs
- ✅ Can prioritize technical debt reduction
- ✅ Understands architectural health trends

**reflector Learning**:
- ✅ Captures effective patterns from implementations
- ✅ Documents anti-patterns to avoid
- ✅ Builds institutional knowledge

---

## Alternatives Considered

### Alternative 1: Automated Tools Only (No Human Review)

**Description**: Use automated tools (linters, static analysis) to update skills, no architect involvement.

**Pros**:
- Fully automated (no manual effort)
- Instant feedback (no delay)
- No bottleneck risk

**Cons**:
- Misses architectural insights (tools can't assess design quality)
- No learning capture (patterns not documented)
- No strategic feedback (can't identify refactoring needs)
- Skills reflect syntax, not semantics

**Why Rejected**: Automated tools are necessary but insufficient. architect provides architectural judgment that tools cannot replicate.

### Alternative 2: Manual Review Only (No Automation)

**Description**: architect manually reviews all commits, no automated skills updates.

**Pros**:
- High-quality reviews (human judgment)
- Captures nuanced insights
- Flexible feedback

**Cons**:
- Does not scale (too slow for high commit volume)
- Skills update lag (manual updates take hours)
- Bottleneck risk (architect overwhelmed)

**Why Rejected**: Manual review is valuable but too slow. Hybrid approach (automation + human judgment) is optimal.

### Alternative 3: Periodic Batch Review (Weekly)

**Description**: architect reviews commits in weekly batches, not per-commit.

**Pros**:
- Less frequent interruptions
- Can review multiple commits in context
- Lower workload

**Cons**:
- Delayed feedback (1 week lag)
- Skills update lag (stale for 1 week)
- Critical issues not caught early

**Why Rejected**: Weekly batches are too slow. Per-commit review with priority-based scheduling is better.

### Alternative 4: code_developer Self-Review

**Description**: code_developer reviews own commits and updates skills.

**Pros**:
- No additional agent needed
- code_developer knows code best
- Immediate feedback

**Cons**:
- Conflicts of interest (reviewing own work)
- Misses architectural perspective
- No independent quality check
- code_developer already overloaded

**Why Rejected**: Independent review by architect provides valuable external perspective.

---

## Risks and Mitigations

### Risk 1: architect Becomes Bottleneck

**Risk**: Commit review queue grows faster than architect can process.

**Impact**: Feedback delayed, skills become stale, code_developer frustrated.

**Probability**: MEDIUM (if commit volume is high)

**Mitigation**:
1. **Priority Queue**: CRITICAL commits reviewed first (within 30 min)
2. **Automated Pre-Filtering**: Tools handle routine checks (80% of commits)
3. **Batch Processing**: Group similar commits for efficient review
4. **Time Limits**: Spend max 15 minutes per routine commit
5. **Escalation**: If queue >20 commits, notify project_manager

**Fallback**: Disable reviews temporarily, focus on skills updates only.

### Risk 2: Feedback Overload for code_developer

**Risk**: code_developer receives too much feedback, becomes demotivated.

**Impact**: Feedback ignored, quality issues persist.

**Probability**: LOW (with proper prioritization)

**Mitigation**:
1. **Clear Priorities**: Only CRITICAL feedback is urgent
2. **Actionable Feedback**: Focus on specific, fixable issues
3. **Positive Feedback**: Highlight good patterns (not just problems)
4. **Volume Limits**: Max 3 feedback items per commit
5. **Feedback Quality**: Measure acceptance rate, adjust accordingly

**Fallback**: Reduce feedback frequency, only send CRITICAL issues.

### Risk 3: Incorrect Feedback Routing

**Risk**: Feedback sent to wrong recipient (e.g., tactical to project_manager).

**Impact**: Confusion, delayed action, wasted effort.

**Probability**: LOW (with decision tree)

**Mitigation**:
1. **Decision Tree Testing**: Validate routing logic on historical commits
2. **Manual Override**: architect can manually re-route feedback
3. **Feedback Tracking**: Measure routing accuracy, refine decision tree
4. **Recipient Confirmation**: Recipients can re-route if incorrect

**Fallback**: All feedback goes to project_manager, who manually routes.

### Risk 4: Skills Update Accuracy

**Risk**: Skills updated incorrectly (wrong line numbers, missing code).

**Impact**: Searches return incorrect results, specs based on bad data.

**Probability**: LOW (with testing)

**Mitigation**:
1. **Automated Tests**: Validate skills update logic on sample commits
2. **Incremental Updates**: Only update changed code (reduce risk)
3. **Full Rebuild**: Weekly full rebuild to correct any drift
4. **Manual Spot Checks**: architect validates 10% of updates manually

**Fallback**: Manual skills update for critical priorities.

### Risk 5: Review Fatigue

**Risk**: architect gets tired of reviewing repetitive commits.

**Impact**: Review quality degrades, issues missed.

**Probability**: MEDIUM (over time)

**Mitigation**:
1. **Automated Tools**: Handle 80% of routine checks (reduce manual effort)
2. **Batching**: Review similar commits together (more efficient)
3. **Rotation**: Consider rotating review responsibility (future)
4. **Breaks**: architect can pause reviews when overloaded

**Fallback**: Reduce review frequency, focus on critical commits only.

---

## Validation

### Pre-Implementation Validation

**Questions to Answer**:
1. Can architect realistically review all commits within SLA?
   - Test: Review last 50 commits, measure time per commit
   - Expected: 5-15 minutes per commit (feasible)

2. Is feedback routing logic sound?
   - Test: Apply decision tree to historical commits
   - Expected: >80% routing accuracy

3. Will code_developer accept feedback?
   - Test: Pilot with 10 commits, gather feedback on feedback
   - Expected: >70% acceptance rate

### Post-Implementation Validation

**Success Criteria** (after 1 month):
- ✅ 100% of commits reviewed within SLA
- ✅ Skills freshness <5 minutes (95th percentile)
- ✅ Feedback acceptance >70%
- ✅ Routing accuracy >90%
- ✅ 0 critical issues reached production (caught in review)
- ✅ Pattern library has >20 patterns documented

**Failure Criteria** (triggers reassessment):
- ❌ Review queue >50 commits (bottleneck)
- ❌ Feedback acceptance <50% (not useful)
- ❌ Routing accuracy <70% (broken logic)
- ❌ Skills freshness >1 hour (too slow)

---

## References

- [ADR-009: Retire assistant (using code analysis skills), Replace with Skills](./ADR-009-retire-assistant (using code analysis skills)-replace-with-skills.md)
- [SPEC-001: Advanced Code Search Skills Architecture](../specs/SPEC-001-advanced-code-search-skills.md)
- [.claude/CLAUDE.md: Agent Tool Ownership Matrix](../../.claude/CLAUDE.md)
- [User Decision: 2025-10-18 Conversation](context)

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-18 | Created | architect (architect evolution) |
| 2025-10-18 | Status: Accepted | architect |

---

## Notes

**Decision Rationale**:

This decision is based on the user's explicit directive:
> "Le architect doit relire tous les commits du code_developer, il en déduit des mises à jour des skills mais aussi un feedback à donner au code_developer : ceci peut aller à la fois au reflector du code_developer, au code_developer directement, ou encore au project_manager (si certaines parties du code doivent être ré-écrites). À chacune de ces opérations, le architect peut donc procéder à la mise à jour des skills."

**Why This is the Right Decision**:

1. **Closes the Loop**
   - Before: architect creates specs → code_developer implements → (no verification)
   - After: architect creates specs → code_developer implements → architect reviews → feedback loop

2. **Skills Stay Current**
   - Code Index updated with every commit (not just nightly)
   - New patterns captured in real-time
   - Skills reflect actual codebase, not idealized design

3. **Quality Feedback**
   - Tactical: code_developer gets actionable fixes
   - Learning: reflector captures effective patterns
   - Strategic: project_manager prioritizes refactoring

4. **Architecture Alignment**
   - architect verifies specs were followed
   - Architecture drift detected early
   - Continuous improvement mindset

5. **Knowledge Capture**
   - Effective patterns documented (not lost)
   - Anti-patterns identified (not repeated)
   - Best practices emerge organically

**Trade-offs Accepted**:

1. **Additional Workload**
   - architect must review ALL commits
   - Accepted because: Automated tools handle 80% of routine checks

2. **Feedback Complexity**
   - Three routing destinations (code_developer, reflector, project_manager)
   - Accepted because: Decision tree provides clear logic

3. **Potential Bottleneck**
   - architect could become overwhelmed
   - Accepted because: Priority queue + batch processing + automated pre-filtering

**Open Questions**:

1. Should architect review commits from OTHER agents (assistant, project_manager)?
   - **Current Answer**: NO - Focus on code_developer commits only (most volume, highest impact)
   - **Future**: Expand to other agents if needed

2. What happens if code_developer disagrees with feedback?
   - **Current Answer**: Feedback is ADVISORY (not mandatory) unless CRITICAL
   - code_developer can challenge feedback, architect responds
   - project_manager arbitrates if dispute persists

3. Should feedback be public or private?
   - **Current Answer**: SEMI-PUBLIC
   - Tactical feedback: Private (code_developer only)
   - Learning feedback: Public (reflector, visible to all)
   - Strategic feedback: Public (project_manager, visible in ROADMAP)

**Future Work**:

- Automated commit categorization (ML-based)
- Sentiment analysis for feedback tone
- A/B testing for feedback effectiveness
- Integration with CI/CD (block merge on critical issues)

---

**Conclusion**: Adding systematic commit review and skills maintenance responsibilities to architect closes the architectural feedback loop, ensures skills stay current, and provides continuous quality improvement. This decision transforms architect from a "design-only" role to a "design + supervision + learning capture" role, making the autonomous development system more robust and self-improving.

**Key Insight**: Code review is the **perfect opportunity** to update skills because architect sees exactly what changed, understands the architectural context, and can validate implementation against specs - all in one workflow.

**Recommendation**: Accept this ADR and proceed with implementation according to the phased plan outlined above.

**Next Steps**:
1. Update SPEC-001 to reflect architect as skills maintainer (replaces assistant (using code analysis skills))
2. Update ADR-009 to document architect as skills owner
3. Begin Phase 1 implementation (commit review framework)
4. Pilot with code_developer to validate feedback quality
5. Measure skills freshness improvement (target: <5 minutes after commit)
