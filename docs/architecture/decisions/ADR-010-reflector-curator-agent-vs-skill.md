# ADR-010: Should Reflector and Curator Remain Agents or Become Skills?

**Status**: APPROVED ✅
**Date**: 2025-10-18
**Approved**: 2025-10-18 (User approval obtained)
**Author**: architect agent
**Related**: ADR-009 (code-searcher retirement), trace-execution skill

---

## Context

### Background

The MonolithicCoffeeMakerAgent system uses the **ACE (Agent Context Evolving) Framework** for continuous improvement through observation, reflection, and curation:

1. **trace-execution** (SKILL) - Captures execution traces → `docs/generator/`
2. **Reflector** (AGENT) - Analyzes traces → creates delta items → `docs/reflector/`
3. **Curator** (AGENT) - Synthesizes delta items → creates playbooks → `docs/curator/`

### Recent Change: generator → trace-execution Skill

**Previously**: generator was a separate agent that observed other agents' executions
**Now**: trace-execution is a skill embedded in ALL agents' startup workflows (ADR-009)

**Benefits achieved**:
- ✅ More accurate (execution context already available)
- ✅ Simpler architecture (no IPC, no separate process)
- ✅ Better performance (direct writes, minimal overhead)
- ✅ Easier integration (embedded in startup skills)
- ✅ Mandatory compliance (automatic execution)

### The Question

**Should Reflector and Curator also become skills?**

This decision is **CRITICAL** because:
- It affects the ACE framework's architecture fundamentally
- Reflector and Curator have different invocation patterns than generator
- The agent → skill conversion must be justified by clear benefits
- Wrong choice could complicate the system unnecessarily

### Current Agent Count

**With code-searcher retirement (ADR-009)**:
- 6 agents → 5 agents after code-searcher removed

**If Reflector and Curator remain agents**:
- Total: 5 agents (user_listener, architect, code_developer, project_manager, assistant) + Reflector + Curator = **7 agents**

**If Reflector and Curator become skills**:
- Total: **5 agents** only

### Forces at Play

1. **Simplicity**: Fewer agents → simpler system, lower coordination overhead
2. **Invocation Pattern**: Reflector/Curator analyze MULTIPLE agents' work (not 1:1 like generator)
3. **Scheduling**: When to run reflection/curation? On-demand? Daily? After N traces?
4. **Context Budget**: CFR-007 requires agents fit in ≤30% of context window
5. **Autonomy**: Should reflection/curation be explicit user requests or automatic background work?
6. **Ownership**: Who owns `docs/reflector/` and `docs/curator/` if they're skills?

---

## Decision

**RECOMMENDATION**: **Reflector and Curator should REMAIN AS AGENTS**, not become skills.

**Reasoning**:

### 1. Fundamental Difference from generator

| Aspect | trace-execution (skill) | Reflector (agent) | Curator (agent) |
|--------|------------------------|-------------------|-----------------|
| **Invocation** | EVERY agent execution (1:1) | Analyzes MANY traces (N:1) | Analyzes MANY delta items (N:1) |
| **Context** | Execution context already available | Must read/parse multiple trace files | Must synthesize across delta items |
| **Timing** | Real-time (during execution) | Periodic (daily/weekly) | Strategic (weekly/monthly) |
| **Ownership** | No ownership (embedded in agents) | Owns docs/reflector/ | Owns docs/curator/ |
| **Output** | Trace files (docs/generator/) | Delta items (insights) | Playbooks (strategic recommendations) |
| **Complexity** | Simple (log events) | Medium (pattern detection, analysis) | High (synthesis, ROI calculation) |

**Key Insight**: trace-execution is **EMBEDDED INSTRUMENTATION** (like logging), while Reflector and Curator are **ANALYTICAL AGENTS** that work across multiple executions.

### 2. Cross-Agent Analysis Requires Agent Status

**Reflector's Job**:
- Read ALL traces from `docs/generator/` (from architect, code_developer, project_manager, etc.)
- Analyze patterns ACROSS agents (not just one agent's work)
- Identify system-wide bottlenecks (e.g., "code discovery slow for ALL agents")
- Create delta items documenting insights

**Example**:
```
Reflector reads:
- 10 architect traces (spec creation)
- 15 code_developer traces (implementation)
- 8 project_manager traces (health checks)

Reflector finds:
- "All agents waste 20-30% time on code discovery"
- "architect specs take 90-150 min, code search is 20% of time"
- "code_developer repetitively greps same files"

Reflector creates delta item:
- BOTTLENECK: Code discovery (15-30 min per spec)
- PATTERN: Manual grepping (across ALL agents)
- OPPORTUNITY: Create code index skill (saves 23-30.7 hrs/month)
```

**Why this needs an agent**:
- **Cross-agent perspective**: No single agent has visibility into ALL traces
- **Strategic analysis**: Requires synthesizing patterns across multiple executions
- **Independent scheduling**: Should run periodically (daily/weekly), not tied to any single agent's execution
- **Dedicated focus**: Reflection is its own task, not a side effect of another agent's work

### 3. Curator Performs Strategic Synthesis

**Curator's Job**:
- Read ALL delta items from `docs/reflector/`
- Synthesize patterns across time (not just one reflection cycle)
- Calculate ROI for skill recommendations (time saved / effort invested)
- Prioritize opportunities (high ROI first)
- Maintain evolving playbooks (update as system changes)
- Track skill effectiveness post-deployment

**Example**:
```
Curator reads delta items:
- Week 1: "Code discovery bottleneck (15-30 min)"
- Week 2: "Code discovery still slow (20-35 min)"
- Week 3: "New bottleneck: Spec template population (15 min)"

Curator calculates:
- Code discovery appears 3 times → High-priority issue
- Time wasted: 30 min/spec × 4 specs/week × 4 weeks = 8 hours/month
- Implementation effort: 15-20 hours (from ADR-009, SPEC-001)
- ROI: 8 hrs/month × 12 months = 96 hrs saved / 20 hrs effort = 4.8x return

Curator recommends:
- PRIORITY 1: Create code-index skill (4.8x ROI)
- PRIORITY 2: Automate spec templates (3.2x ROI)
- PRIORITY 3: Optimize ROADMAP parsing (2.1x ROI)
```

**Why this needs an agent**:
- **Long-term perspective**: Tracks patterns over weeks/months
- **ROI calculation**: Requires business logic (time saved × frequency / effort)
- **Playbook maintenance**: Living documents that evolve with system
- **Strategic priority**: Decides WHAT to build next (strategic function)
- **Independent invocation**: User or project_manager invokes when planning priorities

### 4. Invocation Pattern Mismatch

**trace-execution (skill) invocation**:
```
EVERY agent execution (automatic, 1:1 relationship)
  ↓
architect startup → trace-execution
code_developer startup → trace-execution
project_manager startup → trace-execution
```

**Reflector (agent) invocation**:
```
PERIODIC (scheduled or on-demand, N:1 relationship)
  ↓
Daily cron job → Reflector analyzes last 24 hours of traces
OR
User request → user_listener → Reflector "analyze recent traces"
```

**Curator (agent) invocation**:
```
STRATEGIC (user-triggered or weekly, N:1 relationship)
  ↓
Weekly planning → project_manager → Curator "recommend skill priorities"
OR
User request → user_listener → Curator "what should we build next?"
```

**Why this matters**:
- Skills are designed for **embedded execution** (run as part of another agent's work)
- Reflector/Curator need **independent execution** (run separately from any single agent)
- If they were skills, WHO would invoke them? When? How often?

**Problem with skill approach**:
```
# If Reflector were a skill, where would it run?

architect-startup: invoke reflector skill?
→ NO! architect shouldn't analyze ALL traces just because it started up

code_developer-startup: invoke reflector skill?
→ NO! code_developer shouldn't do reflection analysis during implementation

project_manager-startup: invoke reflector skill?
→ MAYBE? But why should reflection happen every time PM starts?

# Result: Awkward invocation pattern, no clear owner
```

**Solution with agent approach**:
```
# Reflector as agent (clear invocation)

Cron job (daily 2am):
→ Invoke Reflector agent
→ Reflector analyzes last 24 hours of traces
→ Reflector creates delta items
→ Done

OR

User via user_listener: "Analyze recent performance"
→ user_listener delegates to Reflector agent
→ Reflector analyzes traces from last week
→ Reflector presents findings
→ Done
```

### 5. Ownership and Responsibility

**Current Ownership** (from .claude/CLAUDE.md):
```
| File/Directory | Owner | Can Modify? | Others |
|----------------|-------|-------------|--------|
| docs/generator/ | generator | YES - Execution traces | All others: READ-ONLY |
| docs/reflector/ | reflector | YES - Delta items | All others: READ-ONLY |
| docs/curator/ | curator | YES - Playbooks | All others: READ-ONLY |
```

**If Reflector/Curator become skills**:
```
| File/Directory | Owner | Can Modify? | Others |
|----------------|-------|-------------|--------|
| docs/generator/ | Infrastructure (trace-execution skill) | Auto-generated | All others: READ-ONLY |
| docs/reflector/ | ??? | ??? | ??? |
| docs/curator/ | ??? | ??? | ??? |
```

**Problem**: Skills don't have ownership (they're tools used by agents)

**Attempted solutions**:
1. **Option A**: project_manager owns docs/reflector/ and docs/curator/
   - Problem: project_manager would need to invoke skills periodically
   - Problem: Mixing strategic planning (roadmap) with reflection/curation
   - Problem: project_manager doesn't naturally "own" continuous improvement

2. **Option B**: architect owns docs/reflector/ and docs/curator/
   - Problem: architect designs features, not analyzes execution patterns
   - Problem: Would require architect to run reflection as background task
   - Problem: Confusion of responsibilities (design vs. analysis)

3. **Option C**: No ownership (infrastructure-generated)
   - Problem: Who decides when to run reflection/curation?
   - Problem: Who ensures delta items are acted upon?
   - Problem: Who maintains playbooks?

**Solution**: Keep Reflector and Curator as agents with clear ownership

---

## Options Considered

### Option 1: Keep Reflector and Curator as Agents (RECOMMENDED)

**What**:
- Reflector remains an agent (owns docs/reflector/)
- Curator remains an agent (owns docs/curator/)
- Total agent count: 5 core + Reflector + Curator = **7 agents**

**Architecture**:
```
Core Agents (5):
- user_listener (UI)
- architect (design)
- code_developer (implementation)
- project_manager (planning)
- assistant (docs + dispatcher + demos)

ACE Agents (2):
- Reflector (analyze traces → delta items)
- Curator (synthesize delta items → playbooks)

Skills (universal):
- trace-execution (embedded in all agents)
```

**Invocation**:
```
Reflector:
- Scheduled (daily cron: analyze last 24 hours)
- On-demand (user request via user_listener)

Curator:
- Scheduled (weekly cron: synthesize week's delta items)
- On-demand (user request: "what should we prioritize?")
- Planning-triggered (project_manager: "recommend next skills")
```

**Pros**:
- ✅ Clear ownership (Reflector owns docs/reflector/, Curator owns docs/curator/)
- ✅ Independent scheduling (daily/weekly, not tied to other agents)
- ✅ Cross-agent analysis (Reflector sees ALL traces, Curator sees ALL delta items)
- ✅ Strategic function (Curator makes priority recommendations)
- ✅ Consistent with ACE framework design (Observe → Reflect → Curate → Improve)
- ✅ User can invoke explicitly ("show me reflection analysis")
- ✅ Playbooks evolve independently of any single agent's work

**Cons**:
- ❌ More agents (7 instead of 5)
- ❌ Coordination overhead (scheduling, invocation)
- ❌ Context budget pressure (CFR-007)
- ❌ Singleton enforcement needed (only one Reflector/Curator at a time)

**Mitigations**:
- Reflector/Curator run infrequently (daily/weekly), low overhead
- Lightweight agents (mostly read/write files, minimal LLM usage)
- Can be disabled if not needed (optional optimization layer)

### Option 2: Convert Reflector and Curator to Skills

**What**:
- Reflector becomes a skill (invoked by... someone?)
- Curator becomes a skill (invoked by... someone?)
- Total agent count: **5 agents**

**Architecture**:
```
Core Agents (5):
- user_listener (UI)
- architect (design)
- code_developer (implementation)
- project_manager (planning)
- assistant (docs + dispatcher + demos)

Skills (universal):
- trace-execution (embedded in all agents)
- reflector-analysis (invoked by ???)
- curator-synthesis (invoked by ???)
```

**Invocation** (PROBLEM):
```
# Who invokes reflector-analysis skill?

Option A: project_manager-startup skill
→ Problem: PM doesn't need reflection every startup
→ Problem: Mixing planning with analysis

Option B: Scheduled cron job
→ Problem: Cron job isn't an agent, can't invoke skills
→ Problem: Would need wrapper script (awkward)

Option C: User request via user_listener
→ Problem: Requires user to remember to ask
→ Problem: Not autonomous (defeats purpose)
```

**Pros**:
- ✅ Fewer agents (5 instead of 7)
- ✅ Simpler architecture (no separate Reflector/Curator processes)
- ✅ Lower context budget (fewer agent prompts)

**Cons**:
- ❌ No clear owner for docs/reflector/ and docs/curator/
- ❌ Awkward invocation pattern (who runs the skills? when?)
- ❌ Not autonomous (skills need to be triggered by something)
- ❌ Cross-agent analysis doesn't fit skill model (skills are agent-scoped)
- ❌ Strategic synthesis requires agent-level reasoning (skills are tactical)
- ❌ Playbook maintenance requires continuity (skills are stateless)

**Why Rejected**:
- Invocation pattern mismatch (skills designed for embedded execution, not cross-agent analysis)
- Ownership confusion (skills don't own directories)
- Loss of autonomy (skills must be triggered, agents can run independently)

### Option 3: Hybrid (Reflector Skill, Curator Agent)

**What**:
- Reflector becomes a skill (invoked by project_manager periodically)
- Curator remains an agent (strategic synthesis, playbook maintenance)
- Total agent count: 5 core + Curator = **6 agents**

**Rationale**:
- Reflector does tactical analysis (pattern detection, bottleneck identification)
- Curator does strategic synthesis (ROI calculation, priority recommendations)
- Tactical work fits skill model, strategic work fits agent model

**Pros**:
- ✅ Fewer agents than Option 1 (6 instead of 7)
- ✅ Clear ownership for curator (Curator agent owns docs/curator/)
- ✅ Strategic synthesis preserved (Curator agent makes recommendations)

**Cons**:
- ❌ Reflector invocation still awkward (when does PM invoke it?)
- ❌ Reflector output ownership unclear (who owns docs/reflector/?)
- ❌ Inconsistent design (one ACE layer is skill, other is agent)
- ❌ Cross-agent analysis doesn't fit skill model (Reflector analyzes ALL agents)

**Why Rejected**:
- Inconsistent architecture (mixing skill and agent for similar functions)
- Reflector invocation pattern still problematic
- Ownership confusion for docs/reflector/
- Not significantly simpler than Option 1

### Option 4: Merge Reflector and Curator into One Agent

**What**:
- Create single "ACE Agent" combining Reflector + Curator responsibilities
- ACE Agent analyzes traces AND synthesizes playbooks
- Total agent count: 5 core + ACE = **6 agents**

**Architecture**:
```
ACE Agent:
- Reads traces from docs/generator/
- Analyzes patterns (reflection)
- Writes delta items to docs/ace/delta_items/
- Synthesizes playbooks (curation)
- Writes playbooks to docs/ace/playbooks/
```

**Pros**:
- ✅ Fewer agents (6 instead of 7)
- ✅ Clear ownership (ACE agent owns docs/ace/)
- ✅ Cohesive workflow (reflection → curation in one process)

**Cons**:
- ❌ Violates single responsibility principle (one agent does two distinct jobs)
- ❌ Harder to understand (mixed concerns in one agent)
- ❌ Less flexible (can't run reflection without curation)
- ❌ Loses granularity (delta items are intermediate artifacts, useful independently)

**Why Rejected**:
- Mixing concerns (reflection and curation are distinct analytical processes)
- Loss of modularity (can't evolve reflection/curation independently)
- Delta items valuable as standalone artifacts (project_manager can read them without playbooks)

---

## Consequences

### Positive Consequences (Keeping Agents)

1. **Clear Ownership and Responsibility**
   - Reflector owns docs/reflector/ (delta items)
   - Curator owns docs/curator/ (playbooks)
   - No confusion about who creates/maintains these artifacts

2. **Independent Scheduling**
   - Reflector runs daily (analyzes last 24 hours)
   - Curator runs weekly (synthesizes week's insights)
   - Scheduling decoupled from other agents' work

3. **Cross-Agent Analysis**
   - Reflector sees ALL agents' traces (architect, code_developer, project_manager)
   - Identifies system-wide patterns (not just one agent's behavior)
   - Enables global optimization (benefits entire system)

4. **Strategic Function Preserved**
   - Curator makes priority recommendations (what to build next)
   - ROI calculations guide investment decisions
   - Playbooks evolve with system maturity

5. **Autonomous Operation**
   - Reflector runs automatically (daily cron)
   - Curator runs automatically (weekly cron)
   - No user intervention required (but user can invoke on-demand)

6. **Consistent ACE Framework**
   - Observe (trace-execution skill)
   - Reflect (Reflector agent)
   - Curate (Curator agent)
   - Improve (agents consume playbooks)
   - Clean architectural separation of concerns

### Negative Consequences (Keeping Agents)

1. **More Agents to Manage**
   - 7 agents instead of 5 (if skills)
   - More coordination overhead
   - More singleton enforcement
   - More documentation to maintain

2. **Context Budget Pressure**
   - CFR-007: Agents must fit in ≤30% of context window
   - More agents = more prompts to load
   - Mitigated by: Reflector/Curator run infrequently, can be lightweight

3. **Scheduling Complexity**
   - Need cron jobs or scheduling infrastructure
   - Reflector/Curator must be invoked periodically
   - Mitigated by: Simple cron setup, project_manager can trigger

4. **Potential Overhead**
   - If Reflector/Curator run too frequently, could slow system
   - If they analyze too many traces at once, could be expensive
   - Mitigated by: Tunable frequency, incremental analysis

### Neutral Consequences

1. **Agent Count Change**
   - code-searcher retired (ADR-009) → -1 agent
   - Reflector + Curator remain → +2 agents (but they always existed)
   - Net: Still fewer agents than before if code-searcher removed

2. **Invocation Pattern**
   - trace-execution: Embedded (every agent execution)
   - Reflector: Scheduled or on-demand (daily/weekly)
   - Curator: Scheduled or on-demand (weekly/monthly)
   - Different patterns for different purposes (by design)

---

## Implementation Plan

### Phase 1: Clarify Current State (1 hour)

**Goal**: Document existing Reflector and Curator implementations (if any)

**Tasks**:
1. Search codebase for Reflector/Curator references
2. Check if Reflector/Curator agents exist yet
3. Document current state in this ADR

**Expected Finding**: Reflector and Curator likely NOT implemented yet (placeholders only)

### Phase 2: Design Reflector Agent (2 hours)

**Goal**: Create Reflector agent specification

**Tasks**:
1. Define Reflector agent prompt (.claude/agents/reflector.md)
2. Specify trace analysis algorithm (pattern detection, bottleneck identification)
3. Define delta item format (docs/reflector/delta_YYYYMMDD.md)
4. Create invocation mechanism (cron job, user_listener delegation)

**Deliverable**: `.claude/agents/reflector.md` (agent definition)

### Phase 3: Implement Reflector Agent (8 hours)

**Goal**: Working Reflector agent that analyzes traces

**Tasks**:
1. Create Reflector agent class (coffee_maker/autonomous/reflector.py)
2. Implement trace reading (from docs/generator/)
3. Implement pattern detection (bottlenecks, repetitive work)
4. Implement delta item creation (docs/reflector/)
5. Add Langfuse observability (@observe decorator)
6. Add to AgentRegistry (singleton enforcement)
7. Create cron job or scheduled task
8. Unit tests (>80% coverage)

**Deliverable**: Working Reflector agent

### Phase 4: Design Curator Agent (2 hours)

**Goal**: Create Curator agent specification

**Tasks**:
1. Define Curator agent prompt (.claude/agents/curator.md)
2. Specify synthesis algorithm (ROI calculation, prioritization)
3. Define playbook format (docs/curator/playbook_YYYYMMDD.md)
4. Create invocation mechanism (weekly cron, user_listener delegation)

**Deliverable**: `.claude/agents/curator.md` (agent definition)

### Phase 5: Implement Curator Agent (10 hours)

**Goal**: Working Curator agent that creates playbooks

**Tasks**:
1. Create Curator agent class (coffee_maker/autonomous/curator.py)
2. Implement delta item reading (from docs/reflector/)
3. Implement synthesis logic (pattern aggregation across time)
4. Implement ROI calculation (time saved / effort invested)
5. Implement playbook creation (docs/curator/)
6. Add Langfuse observability (@observe decorator)
7. Add to AgentRegistry (singleton enforcement)
8. Create weekly cron job
9. Unit tests (>80% coverage)

**Deliverable**: Working Curator agent

### Phase 6: Integration & Testing (4 hours)

**Goal**: End-to-end ACE workflow working

**Tasks**:
1. Test trace-execution skill (verify traces created)
2. Test Reflector agent (verify delta items created from traces)
3. Test Curator agent (verify playbooks created from delta items)
4. Test full cycle: trace → reflect → curate → improve
5. Integration tests (>80% coverage)
6. Update documentation (.claude/CLAUDE.md, ROADMAP.md)

**Deliverable**: Complete ACE framework operational

### Timeline

**Total Effort**: 27 hours

**Breakdown**:
- Phase 1 (Clarify): 1 hour
- Phase 2 (Reflector Design): 2 hours
- Phase 3 (Reflector Implementation): 8 hours
- Phase 4 (Curator Design): 2 hours
- Phase 5 (Curator Implementation): 10 hours
- Phase 6 (Integration): 4 hours

**Assigned To**: code_developer (after ADR approval)

---

## Risks and Mitigations

### Risk 1: Reflector/Curator Run Too Frequently

**Risk**: Daily/weekly execution creates too much overhead

**Impact**: System slowdown, high LLM costs

**Probability**: LOW (analysis is lightweight)

**Mitigation**:
1. Tunable frequency (can reduce to weekly/monthly if needed)
2. Incremental analysis (only new traces since last run)
3. Cost monitoring (Langfuse tracks LLM usage)
4. Opt-out option (can disable if not valuable)

**Fallback**: Reduce frequency or disable entirely

### Risk 2: Delta Items and Playbooks Ignored

**Risk**: Reflector creates insights, but no one acts on them

**Impact**: Wasted effort, no continuous improvement

**Probability**: MEDIUM (depends on team discipline)

**Mitigation**:
1. project_manager integrates playbook recommendations into ROADMAP
2. Weekly review of delta items (scheduled in planning meetings)
3. ROI calculations make value clear (justifies investment)
4. user_listener can surface insights ("Curator recommends X, approve?")

**Fallback**: If insights unused, reduce Reflector/Curator frequency

### Risk 3: Scheduling Complexity

**Risk**: Cron jobs fail, Reflector/Curator don't run

**Impact**: Stale insights, missed optimization opportunities

**Probability**: LOW (cron is reliable)

**Mitigation**:
1. Monitoring (track last run timestamp)
2. Fallback to manual invocation (user can trigger via user_listener)
3. project_manager can invoke as part of planning workflow
4. Alerts if Reflector/Curator haven't run in >7 days

**Fallback**: Manual invocation via user_listener

### Risk 4: Context Budget Exceeded

**Risk**: Adding Reflector/Curator exceeds CFR-007 (≤30% context for agents)

**Impact**: Agents can't load full context, functionality degraded

**Probability**: LOW (Reflector/Curator are lightweight)

**Mitigation**:
1. Reflector/Curator prompts are concise (focus on analysis, not features)
2. Lazy loading (only load when invoked)
3. Context optimization (trim unnecessary details)
4. Monitor context usage (Langfuse tracks token consumption)

**Fallback**: Simplify Reflector/Curator prompts, remove non-essential context

---

## Validation

### Success Metrics

**Phase 3 Success (Reflector Working)**:
- ✅ Reflector analyzes traces from docs/generator/
- ✅ Delta items created in docs/reflector/
- ✅ Bottlenecks identified (e.g., "code discovery takes 20-30 min")
- ✅ Patterns detected (e.g., "architect always spends 20% time searching")
- ✅ Opportunities documented (e.g., "create code index skill")

**Phase 5 Success (Curator Working)**:
- ✅ Curator reads delta items from docs/reflector/
- ✅ Playbooks created in docs/curator/
- ✅ ROI calculations accurate (matches manual estimation)
- ✅ Priority recommendations actionable (project_manager can add to ROADMAP)
- ✅ Skill effectiveness tracked post-deployment

**Overall Success**:
- ✅ ACE framework operational (Observe → Reflect → Curate → Improve)
- ✅ Reflector runs daily (analyzes last 24 hours automatically)
- ✅ Curator runs weekly (synthesizes week's insights)
- ✅ project_manager integrates playbook recommendations into ROADMAP
- ✅ Continuous improvement visible (new skills deployed based on curator recommendations)

### Reevaluation Triggers

Reassess this decision if:

1. **Scheduling becomes problematic**
   - Cron jobs fail repeatedly
   - Manual invocation too burdensome
   - → Consider: Embedded skills with simpler invocation

2. **Insights unused**
   - Delta items and playbooks ignored for >1 month
   - No ROADMAP priorities added from curator recommendations
   - → Consider: Reduce frequency or disable

3. **Context budget exceeded**
   - CFR-007 violated (agents >30% context)
   - Reflector/Curator prompts too large
   - → Consider: Simplify agents or convert to skills

4. **Cross-agent analysis not valuable**
   - System-wide patterns not found
   - Agent-specific insights more useful
   - → Consider: Embedded reflection skills per-agent

---

## References

- [ADR-009: Retire code-searcher, Replace with Skills](./ADR-009-retire-code-searcher-replace-with-skills.md)
- [trace-execution Skill](./../../../.claude/skills/trace-execution.md)
- [SPEC-001: Advanced Code Search Skills Architecture](../specs/SPEC-001-advanced-code-search-skills.md)
- [.claude/CLAUDE.md: Agent Tool Ownership Matrix](../../.claude/CLAUDE.md)
- [CFR-007: Context Budget Management](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-18 | Created | architect |
| 2025-10-18 | Status: Proposed | architect |
| 2025-10-18 | Status: APPROVED by user | project_manager |
| 2025-10-18 | ROADMAP updated (US-059, US-060, US-061 ready) | project_manager |

---

## Notes

### Key Takeaways

1. **trace-execution skill was correct**: Embedded instrumentation fits skill model perfectly
2. **Reflector/Curator as agents is correct**: Cross-agent analysis requires agent status
3. **Different patterns for different purposes**: Not everything should be a skill
4. **Invocation pattern is decisive**: Skills = embedded, Agents = independent

### Architectural Principle

**When to use Skills vs. Agents**:

| Use SKILL when... | Use AGENT when... |
|-------------------|-------------------|
| Execution context already available | Must gather context from multiple sources |
| 1:1 relationship (agent → skill) | N:1 relationship (many inputs → one analysis) |
| Embedded in another agent's workflow | Independent execution required |
| Tactical operation (logging, validation) | Strategic operation (analysis, planning) |
| Real-time (during execution) | Periodic (scheduled or on-demand) |
| No ownership needed | Clear ownership required (documents, artifacts) |

**Examples**:
- **SKILL**: trace-execution (embedded in all agents, logs during execution)
- **AGENT**: Reflector (analyzes ALL traces, runs periodically)
- **AGENT**: Curator (strategic synthesis, owns playbooks)

### Why This Decision Matters

The ACE framework is foundational for continuous improvement. Getting the architecture right ensures:
- ✅ Insights are captured accurately (trace-execution skill)
- ✅ Patterns are detected system-wide (Reflector agent)
- ✅ Opportunities are prioritized strategically (Curator agent)
- ✅ System evolves autonomously (observe → reflect → curate → improve)

**Wrong decision = broken ACE loop = no continuous improvement**

---

## Conclusion

**DECISION**: **Reflector and Curator REMAIN AS AGENTS**

**Justification**:
1. Cross-agent analysis requires independent agent status
2. Invocation pattern mismatch (skills are embedded, Reflector/Curator are periodic)
3. Clear ownership needed for docs/reflector/ and docs/curator/
4. Strategic function requires agent-level reasoning
5. Consistent with ACE framework design

**Next Steps**:
1. User approves this ADR via user_listener
2. code_developer implements Reflector agent (Phase 2-3)
3. code_developer implements Curator agent (Phase 4-5)
4. code_developer integrates and tests (Phase 6)
5. ACE framework becomes operational

**Expected Outcome**: Autonomous continuous improvement through systematic observation, reflection, and curation.

---

**Remember**: Skills are tools embedded in agents. Agents are autonomous entities that own responsibilities. Reflector and Curator are agents, not tools! 🔍🤖
